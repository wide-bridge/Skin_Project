from __future__ import annotations

import json
import math
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

from common import (
    active_config_path,
    experiment_name,
    filter_rows_by_labels,
    label_list,
    load_config,
    manifest_path,
    processed_dir,
    read_csv_rows,
    write_json,
)


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class FrontalManifestDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], image_size: int, train: bool) -> None:
        self.rows = rows
        aug = []
        if train:
            aug = [
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomApply(
                    [
                        transforms.RandomAffine(
                            degrees=6,
                            translate=(0.03, 0.03),
                            scale=(0.96, 1.04),
                        )
                    ],
                    p=0.7,
                ),
                transforms.RandomResizedCrop(
                    size=(image_size, image_size),
                    scale=(0.92, 1.0),
                    ratio=(0.97, 1.03),
                ),
                transforms.RandomApply(
                    [
                        transforms.ColorJitter(
                            brightness=0.08,
                            contrast=0.08,
                            saturation=0.05,
                            hue=0.01,
                        )
                    ],
                    p=0.6,
                ),
                transforms.RandomApply(
                    [
                        transforms.GaussianBlur(
                            kernel_size=3,
                            sigma=(0.1, 0.6),
                        )
                    ],
                    p=0.15,
                ),
            ]
        if train:
            self.transform = transforms.Compose(
                aug
                + [
                    transforms.ToTensor(),
                    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
                    transforms.RandomErasing(
                        p=0.10,
                        scale=(0.01, 0.04),
                        ratio=(0.8, 1.25),
                        value="random",
                    ),
                ]
            )
        else:
            self.transform = transforms.Compose(
                [
                    transforms.Resize((image_size, image_size)),
                    transforms.ToTensor(),
                    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
                ]
            )
        labels = label_list()
        self.label_to_id = {label: idx for idx, label in enumerate(labels)}

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int):
        row = self.rows[index]
        image = Image.open(row["image_path"]).convert("RGB")
        x = self.transform(image)
        y = self.label_to_id[row["canonical_label"]]
        return x, y, row["image_id"]


def build_model(backbone: str, num_classes: int) -> nn.Module:
    name = backbone.lower()
    if name == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if name == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        return model
    if name == "efficientnet_v2_s":
        model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported backbone: {backbone}")


def set_trainable_layers(model: nn.Module, backbone: str, stage: str, ratio: float) -> None:
    for param in model.parameters():
        param.requires_grad = False

    if backbone == "resnet18":
        for param in model.fc.parameters():
            param.requires_grad = True
        if stage in {"partial", "full"}:
            for param in model.layer4.parameters():
                param.requires_grad = True
        if stage == "full":
            for param in model.parameters():
                param.requires_grad = True
        return

    if backbone == "efficientnet_b0":
        for param in model.classifier.parameters():
            param.requires_grad = True
        if stage in {"partial", "full"}:
            features = list(model.features.children())
            num_blocks = len(features)
            start_idx = max(0, num_blocks - max(1, int(math.ceil(num_blocks * ratio))))
            for block in features[start_idx:]:
                for param in block.parameters():
                    param.requires_grad = True
        if stage == "full":
            for param in model.parameters():
                param.requires_grad = True
        return

    if backbone == "efficientnet_v2_s":
        for param in model.classifier.parameters():
            param.requires_grad = True
        if stage in {"partial", "full"}:
            features = list(model.features.children())
            num_blocks = len(features)
            start_idx = max(0, num_blocks - max(1, int(math.ceil(num_blocks * ratio))))
            for block in features[start_idx:]:
                for param in block.parameters():
                    param.requires_grad = True
        if stage == "full":
            for param in model.parameters():
                param.requires_grad = True
        return

    raise ValueError(f"Unsupported backbone: {backbone}")


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> dict[str, float]:
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total = 0
    total_loss = 0.0
    correct = 0
    with torch.no_grad():
        for x, y, _ in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            pred = logits.argmax(dim=1)
            total += y.numel()
            total_loss += float(loss.item()) * y.size(0)
            correct += (pred == y).sum().item()
    return {
        "loss": total_loss / total if total else math.inf,
        "accuracy": correct / total if total else 0.0,
        "samples": total,
    }


def main() -> None:
    cfg = load_config()
    labels = label_list()
    rows = read_csv_rows(manifest_path())
    selected_rows = filter_rows_by_labels(rows, labels)
    excluded_samples = len(rows) - len(selected_rows)
    if excluded_samples:
        print(f"Excluded {excluded_samples} samples outside configured labels: {labels}")
    train_rows = [row for row in selected_rows if row["split"] == "train"]
    val_rows = [row for row in selected_rows if row["split"] == "val"]

    backbone = cfg["model"]["backbone"]
    image_size = int(cfg["model"]["image_size"])
    batch_size = int(cfg["training"]["batch_size"])
    epochs = int(cfg["training"]["epochs"])
    lr = float(cfg["training"]["learning_rate"])
    weight_decay = float(cfg["training"]["weight_decay"])
    patience = int(cfg["training"]["patience"])
    stage_epochs = [int(v) for v in cfg["training"]["stage_epochs"]]
    stage_unfreeze_ratios = [float(v) for v in cfg["training"]["stage_unfreeze_ratios"]]
    stage_learning_rates = [float(v) for v in cfg["training"]["stage_learning_rates"]]
    num_workers = int(cfg["training"]["num_workers"])

    if not (len(stage_epochs) == len(stage_unfreeze_ratios) == len(stage_learning_rates)):
        raise ValueError("stage_epochs, stage_unfreeze_ratios, and stage_learning_rates must have the same length")

    stage_bounds: list[tuple[int, int, float, float]] = []
    start_epoch = 1
    for epoch_count, ratio, stage_lr in zip(stage_epochs, stage_unfreeze_ratios, stage_learning_rates):
        end_epoch = start_epoch + epoch_count - 1
        stage_bounds.append((start_epoch, end_epoch, ratio, stage_lr))
        start_epoch = end_epoch + 1

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = FrontalManifestDataset(train_rows, image_size=image_size, train=True)
    val_ds = FrontalManifestDataset(val_rows, image_size=image_size, train=False)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    model = build_model(backbone, len(labels)).to(device)
    criterion = nn.CrossEntropyLoss()
    history: list[dict[str, float | int | str]] = []
    best_val_acc = -1.0
    best_val_loss = math.inf
    best_epoch = 0
    patience_count = 0

    out_dir = processed_dir()
    run_name = experiment_name()
    checkpoint_path = out_dir / f"{run_name}_{backbone}_best.pt"
    history_path = out_dir / f"{run_name}_train_history.json"
    metrics_path = out_dir / f"{run_name}_train_metrics.json"

    for epoch in range(1, epochs + 1):
        active_stage_name = "full"
        active_ratio = 1.0
        active_lr = lr
        for idx, (start_e, end_e, ratio, stage_lr) in enumerate(stage_bounds, start=1):
            if start_e <= epoch <= end_e:
                active_ratio = ratio
                active_lr = stage_lr
                active_stage_name = f"stage_{idx}"
                break

        if active_ratio <= 0.0:
            stage = "head"
        elif active_ratio >= 1.0:
            stage = "full"
        else:
            stage = "partial"

        set_trainable_layers(model, backbone, stage, active_ratio)
        optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=active_lr, weight_decay=weight_decay)

        model.train()
        running_loss = 0.0
        running_samples = 0
        for x, y, _ in train_loader:
            x = x.to(device)
            y = y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            running_loss += float(loss.item()) * y.size(0)
            running_samples += y.size(0)

        train_loss = running_loss / running_samples if running_samples else math.inf
        val_metrics = evaluate(model, val_loader, device)
        artifact = {
            "epoch": epoch,
            "stage": active_stage_name,
            "stage_mode": stage,
            "unfreeze_ratio": active_ratio,
            "learning_rate": active_lr,
            "train_loss": train_loss,
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
        }
        history.append(artifact)
        write_json(history_path, history, indent=2)
        print(json.dumps(artifact, ensure_ascii=False))

        improved = (
            val_metrics["accuracy"] > best_val_acc
            or (math.isclose(val_metrics["accuracy"], best_val_acc) and val_metrics["loss"] < best_val_loss)
        )
        if improved:
            best_val_acc = val_metrics["accuracy"]
            best_val_loss = val_metrics["loss"]
            best_epoch = epoch
            patience_count = 0
            torch.save(model.state_dict(), checkpoint_path)
        else:
            patience_count += 1
            if patience_count >= patience:
                break

    summary = {
        "device": str(device),
        "config_path": str(active_config_path()),
        "backbone": backbone,
        "labels": labels,
        "num_classes": len(labels),
        "excluded_samples": excluded_samples,
        "train_samples": len(train_rows),
        "val_samples": len(val_rows),
        "best_epoch": best_epoch,
        "best_val_accuracy": best_val_acc,
        "best_val_loss": best_val_loss,
        "checkpoint_path": str(checkpoint_path),
        "patience": patience,
        "stage_epochs": stage_epochs,
        "stage_unfreeze_ratios": stage_unfreeze_ratios,
        "stage_learning_rates": stage_learning_rates,
    }
    write_json(metrics_path, summary, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
