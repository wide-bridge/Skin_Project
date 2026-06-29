from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _common import processed_dir
from services.config import get_settings

LABELS = ["acne", "atopic_dermatitis", "normal", "psoriasis", "rosacea", "seborrheic_dermatitis"]


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def build_model() -> torch.nn.Module:
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(LABELS))
    return model


def main() -> None:
    settings = get_settings()
    state_path = processed_dir() / "baseline_resnet18_state.pt"
    manifest = load_manifest(processed_dir() / "image_manifest.csv")
    sample = next(row for row in manifest if row["model_split"] == "test")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model().to(device)
    model.load_state_dict(torch.load(state_path, map_location=device))
    model.eval()
    image = Image.open(sample["image_path"]).convert("RGB")
    x = transforms.Compose([transforms.Resize((settings.baseline.image_size, settings.baseline.image_size)), transforms.ToTensor()])(image).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        top2 = torch.topk(probs, k=2)
    result = {
        "image_id": sample["image_id"],
        "ground_truth": sample["canonical_label"],
        "predicted_disease": LABELS[top2.indices[0].item()],
        "confidence": float(top2.values[0].item()),
        "differentials": [LABELS[i.item()] for i in top2.indices[1:]],
        "needs_human_review": float(top2.values[0].item()) < 0.8,
    }
    out = processed_dir() / "baseline_sample_inference.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
