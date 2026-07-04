from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader

from src.evaluation.metrics import classification_accuracy, confusion_matrix, mean_absolute_error, save_confusion_csv, tolerance_accuracy
from src.training.dataset import SkinConditionDataset, build_weighted_sampler
from src.training.losses import build_loss, make_ordinal_targets
from src.training.models import WrappedModel, apply_lazy_freeze


def _predict_classes(task_type: str, outputs: torch.Tensor, num_classes: int) -> torch.Tensor:
    if task_type == 'classification':
        return outputs.argmax(dim=1)
    if task_type == 'regression':
        return torch.clamp(outputs.round(), 0, num_classes - 1).long()
    if task_type == 'ordinal':
        return torch.clamp((torch.sigmoid(outputs) > 0.5).sum(dim=1).long(), 0, num_classes - 1)
    raise ValueError(task_type)


def _compute_loss(task_type: str, criterion, outputs: torch.Tensor, targets: torch.Tensor, num_classes: int) -> torch.Tensor:
    if task_type == 'classification':
        return criterion(outputs, targets)
    if task_type == 'regression':
        return criterion(outputs.float(), targets.float())
    if task_type == 'ordinal':
        return criterion(outputs, make_ordinal_targets(targets, num_classes))
    raise ValueError(task_type)


def _make_loader(rows: list[dict], config: dict, augment: bool, shuffle: bool = False) -> DataLoader:
    dataset = SkinConditionDataset(
        rows=rows,
        image_size=int(config['settings']['image_size']),
        use_roi_crop=bool(config['settings']['use_roi_crop']),
        use_precrop=bool(config['settings'].get('use_precrop', False)),
        roi_padding_ratio=float(config['settings']['roi_padding_ratio']),
        augment=augment,
        augmentation_config=config['training'].get('augmentation', {}),
    )
    sampler = build_weighted_sampler(rows) if augment and config['training'].get('weighted_sampler', False) else None
    return DataLoader(dataset, batch_size=int(config['training']['batch_size']), shuffle=(shuffle and sampler is None), sampler=sampler, num_workers=int(config['training']['num_workers']), pin_memory=True)


def evaluate_model(model, loader, task_type: str, device: torch.device, num_classes: int):
    model.eval()
    criterion = build_loss(task_type)
    all_true, all_pred = [], []
    running_loss = 0.0
    with torch.no_grad():
        for batch in loader:
            images = batch['image'].to(device)
            targets = batch['target'].to(device)
            outputs = model(images)
            loss = _compute_loss(task_type, criterion, outputs, targets, num_classes)
            preds = _predict_classes(task_type, outputs, num_classes)
            running_loss += loss.item() * images.size(0)
            all_true.extend(targets.cpu().tolist())
            all_pred.extend(preds.cpu().tolist())
    total = max(1, len(all_true))
    return {'loss': running_loss / total, 'accuracy': classification_accuracy(all_true, all_pred), 'tolerance1_accuracy': tolerance_accuracy(all_true, all_pred, 1), 'mae': mean_absolute_error(all_true, all_pred), 'confusion_matrix': confusion_matrix(all_true, all_pred, num_classes=num_classes)}


def train_experiment(config: dict, experiment: dict, split_name: str, split_rows: dict[str, list[dict]]):
    run_id = experiment['run_id']
    task_type = experiment['task_type']
    device_name = config['training']['device']
    device = torch.device(device_name if device_name == 'cuda' and torch.cuda.is_available() else 'cpu')
    num_classes = len({row['target_value'] for rows in split_rows.values() for row in rows})

    outputs_root = Path(config['paths']['outputs_root'])
    checkpoints_root = Path(config['paths']['checkpoints_root'])
    logs_root = Path(config['paths']['logs_root'])
    (outputs_root / 'confusion_matrix').mkdir(parents=True, exist_ok=True)
    checkpoints_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)

    log_path = logs_root / f'train_{run_id}_{split_name}.log'
    logger = logging.getLogger(f'{run_id}_{split_name}')
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)

    model = WrappedModel(experiment['backbone'], task_type, num_classes=num_classes, pretrained=bool(experiment.get('pretrained', True))).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(config['training']['learning_rate']), weight_decay=float(config['training']['weight_decay']))
    criterion = build_loss(task_type)

    train_loader = _make_loader(split_rows['train'], config, augment=True, shuffle=True)
    val_loader = _make_loader(split_rows['val'], config, augment=False)
    test_loader = _make_loader(split_rows['test'], config, augment=False)

    best_val_mae = float('inf')
    best_state = None
    stale_epochs = 0
    patience = int(config['training']['patience'])
    early_stop_start_epoch = int(config['training']['freeze'].get('early_stop_start_epoch', int(config['training']['freeze'].get('unfreeze_full_epoch', 20)) + 1))

    for epoch in range(int(config['training']['max_epochs'])):
        apply_lazy_freeze(model, epoch, config['training']['freeze'])
        model.train()
        running_loss, sample_count = 0.0, 0
        for batch in train_loader:
            images = batch['image'].to(device)
            targets = batch['target'].to(device)
            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            loss = _compute_loss(task_type, criterion, outputs, targets, num_classes)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)
            sample_count += images.size(0)
        train_loss = running_loss / max(1, sample_count)
        val_metrics = evaluate_model(model, val_loader, task_type, device, num_classes)
        logger.info('epoch=%s train_loss=%.6f val_loss=%.6f val_acc=%.4f val_tol1=%.4f val_mae=%.4f', epoch + 1, train_loss, val_metrics['loss'], val_metrics['accuracy'], val_metrics['tolerance1_accuracy'], val_metrics['mae'])

        if val_metrics['mae'] < best_val_mae:
            best_val_mae = val_metrics['mae']
            stale_epochs = 0
            best_state = {k: v.cpu() for k, v in model.state_dict().items()}
        elif (epoch + 1) >= early_stop_start_epoch:
            stale_epochs += 1

        if (epoch + 1) >= early_stop_start_epoch and stale_epochs >= patience:
            logger.info('early_stop epoch=%s', epoch + 1)
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    test_metrics = evaluate_model(model, test_loader, task_type, device, num_classes)
    confusion_path = outputs_root / 'confusion_matrix' / f'{run_id}_{split_name}.csv'
    save_confusion_csv(confusion_path, test_metrics['confusion_matrix'])
    checkpoint_path = checkpoints_root / f'{run_id}_{split_name}.pt'
    torch.save(model.state_dict(), checkpoint_path)

    return {'run_id': run_id, 'split_name': split_name, 'backbone': experiment['backbone'], 'task_type': task_type, 'num_classes': num_classes, 'pretrained': bool(experiment.get('pretrained', True)), 'accuracy': round(test_metrics['accuracy'], 6), 'tolerance1_accuracy': round(test_metrics['tolerance1_accuracy'], 6), 'mae': round(test_metrics['mae'], 6), 'log_path': str(log_path), 'checkpoint_path': str(checkpoint_path), 'confusion_csv': str(confusion_path)}


def append_metrics_csv(path: str | Path, row: dict[str, Any]):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open('a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)
