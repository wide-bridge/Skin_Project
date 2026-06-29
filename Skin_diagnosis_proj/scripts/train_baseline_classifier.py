from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
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

from _common import processed_dir
from services.config import get_settings

LABEL_TO_ID = {
    "acne": 0,
    "atopic_dermatitis": 1,
    "normal": 2,
    "psoriasis": 3,
    "rosacea": 4,
    "seborrheic_dermatitis": 5,
}


class SkinManifestDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], image_size: int) -> None:
        self.rows = rows
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
        ])

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int):
        row = self.rows[idx]
        image = Image.open(row["image_path"]).convert("RGB")
        x = self.transform(image)
        y = LABEL_TO_ID[row["canonical_label"]]
        return x, y, row["image_id"]


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def stratified_take(rows: list[dict[str, str]], total_limit: int) -> list[dict[str, str]]:
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_label[row["canonical_label"]].append(row)
    labels = sorted(by_label)
    per_label = max(1, total_limit // max(1, len(labels)))
    selected: list[dict[str, str]] = []
    for label in labels:
        selected.extend(by_label[label][:per_label])
    return selected[:total_limit]


def build_model(num_classes: int) -> nn.Module:
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> dict:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y, _ in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            preds = logits.argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.numel()
    return {"accuracy": correct / total if total else 0.0, "samples": total}


def main() -> None:
    settings = get_settings()
    manifest = load_manifest(processed_dir() / "image_manifest.csv")
    train_all = [row for row in manifest if row["model_split"] == "train"]
    val_all = [row for row in manifest if row["model_split"] == "val"]
    test_rows = [row for row in manifest if row["model_split"] == "test"]
    train_rows = stratified_take(train_all, settings.baseline.train_max_samples)
    val_rows = stratified_take(val_all, settings.baseline.val_max_samples)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = SkinManifestDataset(train_rows, settings.baseline.image_size)
    val_ds = SkinManifestDataset(val_rows, settings.baseline.image_size)
    train_loader = DataLoader(train_ds, batch_size=settings.baseline.batch_size, shuffle=True, num_workers=settings.baseline.num_workers)
    val_loader = DataLoader(val_ds, batch_size=settings.baseline.batch_size, shuffle=False, num_workers=settings.baseline.num_workers)

    model = build_model(num_classes=len(LABEL_TO_ID)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=settings.baseline.learning_rate)
    criterion = nn.CrossEntropyLoss()

    model.train()
    last_loss = None
    for _ in range(settings.baseline.epochs):
        for x, y, _ in train_loader:
            x = x.to(device)
            y = y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            last_loss = float(loss.item())

    val_metrics = evaluate(model, val_loader, device)
    artifact = {
        "device": str(device),
        "backbone": settings.baseline.backbone,
        "train_samples": len(train_rows),
        "val_samples": len(val_rows),
        "test_samples": len(test_rows),
        "train_label_counts": dict(sorted(Counter(row['canonical_label'] for row in train_rows).items())),
        "last_train_loss": last_loss,
        "val_accuracy": val_metrics["accuracy"],
    }
    out = processed_dir() / "baseline_train_metrics.json"
    out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    torch.save(model.state_dict(), processed_dir() / "baseline_resnet18_state.pt")
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
