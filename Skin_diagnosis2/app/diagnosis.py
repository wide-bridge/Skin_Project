from functools import lru_cache
from io import BytesIO
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import EfficientNet_B3_Weights, efficientnet_b3

from app import config
from app.safety import diagnosis_notice, uncertainty_label
from app.schemas import DiagnosisResult, PredictionItem


def _build_model(num_classes: int):
    weights = EfficientNet_B3_Weights.IMAGENET1K_V1
    model = efficientnet_b3(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


@lru_cache(maxsize=1)
def load_model():
    if config.MODEL_PATH is None:
        raise FileNotFoundError("EfficientNet-B3 checkpoint was not found.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(config.MODEL_PATH, map_location=device)
    class_to_idx = checkpoint.get("class_to_idx", {name: idx for idx, name in enumerate(config.DEFAULT_CLASSES)})
    idx_to_class = {int(idx): name for name, idx in class_to_idx.items()}

    model = _build_model(len(class_to_idx))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, device, idx_to_class


@lru_cache(maxsize=1)
def image_transform():
    weights = EfficientNet_B3_Weights.IMAGENET1K_V1
    return transforms.Compose([
        transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=weights.transforms().mean, std=weights.transforms().std),
    ])


def predict_image(image_bytes: bytes) -> Optional[DiagnosisResult]:
    if not image_bytes:
        return None

    model, device, idx_to_class = load_model()
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    tensor = image_transform()(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    order = np.argsort(probs)[::-1]
    top_predictions = [
        PredictionItem(label=idx_to_class[int(idx)], confidence=float(probs[idx]))
        for idx in order[:3]
    ]
    top1 = top_predictions[0]
    top2_conf = top_predictions[1].confidence if len(top_predictions) > 1 else 0.0
    margin = float(top1.confidence - top2_conf)
    uncertainty = uncertainty_label(top1.confidence, margin)

    return DiagnosisResult(
        label=top1.label,
        confidence=top1.confidence,
        top_predictions=top_predictions,
        margin=margin,
        uncertainty=uncertainty,
        notice=diagnosis_notice(top1.label, top1.confidence, margin),
    )

