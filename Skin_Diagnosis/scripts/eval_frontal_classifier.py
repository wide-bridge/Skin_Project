from __future__ import annotations

import argparse
import math

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
    write_jsonl,
)


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class EvalDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], image_size: int) -> None:
        self.rows = rows
        self.transform = transforms.Compose(
            [transforms.Resize((image_size, image_size)), transforms.ToTensor(), transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
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
        return x, y, row


def build_model(backbone: str, num_classes: int) -> nn.Module:
    if backbone == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if backbone == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        return model
    if backbone == "efficientnet_v2_s":
        model = models.efficientnet_v2_s(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported backbone: {backbone}")


def classification_metrics(labels: list[str], golds: list[str], preds: list[str]) -> dict:
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
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": sum(confusion[label].values()),
        }

    macro_f1 = sum(per_class[label]["f1"] for label in labels) / len(labels)
    return {"confusion_matrix": confusion, "per_class": per_class, "macro_f1": macro_f1}


def age_bucket_metrics(rows: list[dict], normal_label: str = "normal") -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["age_range"], []).append(row)

    results = []
    for age_range, bucket_rows in sorted(grouped.items()):
        total = len(bucket_rows)
        correct = sum(1 for row in bucket_rows if row["correct"])
        false_normal = sum(1 for row in bucket_rows if row["ground_truth"] != normal_label and row["predicted_label"] == normal_label)
        results.append(
            {
                "age_range": age_range,
                "samples": total,
                "accuracy": correct / total if total else 0.0,
                "false_normal_count": false_normal,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="val")
    args = parser.parse_args()

    cfg = load_config()
    backbone = cfg["model"]["backbone"]
    image_size = int(cfg["model"]["image_size"])
    batch_size = int(cfg["training"]["batch_size"])
    num_workers = int(cfg["training"]["num_workers"])
    review_threshold = float(cfg["model"]["human_review_confidence_threshold"])
    labels = label_list()
    id_to_label = {idx: label for idx, label in enumerate(labels)}

    split_rows = [row for row in read_csv_rows(manifest_path()) if row["split"] == args.split]
    rows = filter_rows_by_labels(split_rows, labels)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = EvalDataset(rows, image_size=image_size)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    model = build_model(backbone, len(labels)).to(device)
    run_name = experiment_name()
    checkpoint_path = processed_dir() / f"{run_name}_{backbone}_best.pt"
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()

    criterion = nn.CrossEntropyLoss()
    total = 0
    total_loss = 0.0
    correct = 0
    golds: list[str] = []
    preds: list[str] = []
    prediction_rows: list[dict] = []

    with torch.no_grad():
        for x, y, batch_rows in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            probs = torch.softmax(logits, dim=1)
            confs, pred_ids = probs.max(dim=1)
            loss = criterion(logits, y)

            total += y.numel()
            total_loss += float(loss.item()) * y.size(0)
            correct += (pred_ids == y).sum().item()

            for i, row in enumerate(batch_rows["image_id"]):
                gold_label = batch_rows["canonical_label"][i]
                pred_label = id_to_label[int(pred_ids[i].cpu().item())]
                confidence = float(confs[i].cpu().item())
                golds.append(gold_label)
                preds.append(pred_label)
                prediction_rows.append(
                    {
                        "image_id": row,
                        "ground_truth": gold_label,
                        "predicted_label": pred_label,
                        "confidence": confidence,
                        "needs_human_review": confidence < review_threshold,
                        "correct": gold_label == pred_label,
                        "age_range": batch_rows["age_range"][i],
                    }
                )

    cls = classification_metrics(labels, golds, preds)
    false_normal = sum(1 for row in prediction_rows if row["ground_truth"] != "normal" and row["predicted_label"] == "normal")
    lesion_binary_correct = sum(
        1
        for row in prediction_rows
        if ((row["ground_truth"] == "normal") == (row["predicted_label"] == "normal"))
    )

    metrics = {
        "backbone": backbone,
        "config_path": str(active_config_path()),
        "checkpoint_path": str(checkpoint_path),
        "split": args.split,
        "labels": labels,
        "num_classes": len(labels),
        "excluded_samples": len(split_rows) - len(rows),
        "samples": total,
        "accuracy": correct / total if total else math.nan,
        "loss": total_loss / total if total else math.inf,
        "macro_f1": cls["macro_f1"],
        "confusion_matrix": cls["confusion_matrix"],
        "per_class": cls["per_class"],
        "false_normal_count": false_normal,
        "normal_vs_lesion_binary_accuracy": lesion_binary_correct / total if total else 0.0,
        "human_review_threshold": review_threshold,
        "human_review_count": sum(1 for row in prediction_rows if row["needs_human_review"]),
        "age_range_breakdown": age_bucket_metrics(prediction_rows),
    }

    metrics_path = processed_dir() / f"{run_name}_eval_metrics_{args.split}.json"
    preds_path = processed_dir() / f"{run_name}_eval_predictions_{args.split}.jsonl"
    write_json(metrics_path, metrics, indent=2)
    write_jsonl(preds_path, prediction_rows)
    print(metrics)


if __name__ == "__main__":
    main()
