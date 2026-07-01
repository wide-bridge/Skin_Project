from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _common import BASELINE_LABELS, processed_dir
from _utf8 import read_csv_dicts_utf8_sig, write_json_utf8, write_jsonl_utf8
from services.config import get_settings

LABEL_TO_ID = {label: idx for idx, label in enumerate(BASELINE_LABELS)}
ID_TO_LABEL = {value: key for key, value in LABEL_TO_ID.items()}
LABEL_ORDER = list(BASELINE_LABELS)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class SkinManifestEvalDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], image_size: int) -> None:
        self.rows = rows
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int):
        row = self.rows[idx]
        image = Image.open(row["image_path"]).convert("RGB")
        x = self.transform(image)
        y = LABEL_TO_ID[row["canonical_label"]]
        return x, y, row["image_id"], row["canonical_label"]


def load_manifest(path: Path) -> list[dict[str, str]]:
    return read_csv_dicts_utf8_sig(path)


def build_model(backbone: str, num_classes: int) -> nn.Module:
    name = backbone.lower()
    if name == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if name == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported baseline backbone: {backbone}")


def compute_classification_metrics(labels: list[str], golds: list[str], preds: list[str]) -> dict:
    confusion = {gold: {pred: 0 for pred in labels} for gold in labels}
    for gold, pred in zip(golds, preds):
        confusion[gold][pred] += 1

    per_class = {}
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        support = sum(confusion[label].values())
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }

    macro_precision = sum(per_class[label]["precision"] for label in labels) / len(labels)
    macro_recall = sum(per_class[label]["recall"] for label in labels) / len(labels)
    macro_f1 = sum(per_class[label]["f1"] for label in labels) / len(labels)
    total_support = sum(per_class[label]["support"] for label in labels)
    weighted_f1 = (
        sum(per_class[label]["f1"] * per_class[label]["support"] for label in labels) / total_support
        if total_support
        else 0.0
    )

    return {
        "labels": labels,
        "confusion_matrix": confusion,
        "per_class": per_class,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="test", help="dataset split to evaluate")
    parser.add_argument("--max-samples", type=int, default=0, help="optional cap for faster eval")
    args = parser.parse_args()

    settings = get_settings()
    manifest = load_manifest(processed_dir() / "image_manifest.csv")
    rows = [row for row in manifest if row["model_split"] == args.split]
    if args.max_samples and args.max_samples > 0:
        rows = rows[: args.max_samples]
    if not rows:
        raise RuntimeError(f"no rows found for split={args.split}")

    backbone_name = settings.baseline.backbone.lower()
    checkpoint_path = processed_dir() / f"baseline_{backbone_name}_state.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"baseline checkpoint not found: {checkpoint_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = SkinManifestEvalDataset(rows, settings.baseline.image_size)
    loader = DataLoader(dataset, batch_size=settings.baseline.batch_size, shuffle=False, num_workers=settings.baseline.num_workers)
    model = build_model(settings.baseline.backbone, len(LABEL_TO_ID)).to(device)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()

    criterion = nn.CrossEntropyLoss()
    total = 0
    correct = 0
    total_loss = 0.0
    golds: list[str] = []
    preds: list[str] = []
    predictions: list[dict] = []

    with torch.no_grad():
        for x, y, image_ids, label_names in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            pred_ids = logits.argmax(dim=1)

            total += y.numel()
            correct += (pred_ids == y).sum().item()
            total_loss += float(loss.item()) * y.size(0)

            for image_id, gold_label, pred_id in zip(image_ids, label_names, pred_ids.cpu().tolist()):
                pred_label = ID_TO_LABEL[pred_id]
                golds.append(gold_label)
                preds.append(pred_label)
                predictions.append(
                    {
                        "image_id": image_id,
                        "ground_truth": gold_label,
                        "predicted_disease": pred_label,
                        "correct": pred_label == gold_label,
                    }
                )

    cls_metrics = compute_classification_metrics(LABEL_ORDER, golds, preds)
    metrics = {
        "backbone": backbone_name,
        "checkpoint_path": str(checkpoint_path),
        "split": args.split,
        "samples": total,
        "accuracy": correct / total if total else math.nan,
        "loss": total_loss / total if total else math.inf,
        "labels": cls_metrics["labels"],
        "confusion_matrix": cls_metrics["confusion_matrix"],
        "per_class": cls_metrics["per_class"],
        "macro_precision": cls_metrics["macro_precision"],
        "macro_recall": cls_metrics["macro_recall"],
        "macro_f1": cls_metrics["macro_f1"],
        "weighted_f1": cls_metrics["weighted_f1"],
    }

    split_suffix = args.split.strip().lower()
    metrics_path = processed_dir() / f"baseline_eval_metrics_{split_suffix}.json"
    predictions_path = processed_dir() / f"baseline_eval_predictions_{split_suffix}.jsonl"
    write_json_utf8(metrics_path, metrics, indent=2)
    write_jsonl_utf8(predictions_path, predictions)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"saved {metrics_path}")
    print(f"saved {predictions_path}")


if __name__ == "__main__":
    main()
