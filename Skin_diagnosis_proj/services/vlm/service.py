from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torchvision import models, transforms

from scripts._common import BASELINE_LABELS, DISPLAY_KO_MAP, processed_dir
from services.config import get_settings
from services.rag.retriever import retrieve_dermatology_contexts
from services.schemas import DiagnosisRequest, DiagnosisResponse
from services.vlm.prompting import load_diagnosis_prompt

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class VLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.prompt = load_diagnosis_prompt()
        self._runtime_loaded = False
        self._device = torch.device("cuda" if torch.cuda.is_available() and self.settings.vlm.device == "cuda" else "cpu")
        self._model: torch.nn.Module | None = None
        self._transform = transforms.Compose([
            transforms.Resize((self.settings.baseline.image_size, self.settings.baseline.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def _build_model(self) -> torch.nn.Module:
        backbone = self.settings.baseline.backbone.lower()
        if backbone == "resnet18":
            model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            model.fc = torch.nn.Linear(model.fc.in_features, len(BASELINE_LABELS))
            return model
        if backbone == "efficientnet_b0":
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            in_features = model.classifier[1].in_features
            model.classifier[1] = torch.nn.Linear(in_features, len(BASELINE_LABELS))
            return model
        raise ValueError(f"Unsupported baseline backbone: {self.settings.baseline.backbone}")

    def _checkpoint_path(self) -> Path:
        backbone_name = self.settings.baseline.backbone.lower()
        return processed_dir() / f"baseline_{backbone_name}_state.pt"

    def load_runtime(self) -> None:
        checkpoint_path = self._checkpoint_path()
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Baseline checkpoint not found: {checkpoint_path}")
        model = self._build_model().to(self._device)
        model.load_state_dict(torch.load(checkpoint_path, map_location=self._device))
        model.eval()
        self._model = model
        self._runtime_loaded = True

    def _build_explanation(self, predicted_label: str, confidence: float, contexts: list[dict[str, Any]]) -> str:
        disease_ko = DISPLAY_KO_MAP.get(predicted_label, predicted_label)
        if contexts:
            summary = str(contexts[0].get("content", "")).strip().replace("\n", " ")
            summary = summary[:280].strip()
            return f"Baseline 진단 결과는 {disease_ko} 가능성이 높습니다. 참고 문서 요약: {summary}"
        return (
            f"Baseline 진단 결과는 {disease_ko} 가능성이 높습니다. "
            f"현재 신뢰도는 {confidence:.3f}이며, 직접 연결된 설명 문서를 찾지 못해 일반 안내 수준으로 제공합니다."
        )

    def _build_care_guidance(self, predicted_label: str, needs_human_review: bool) -> list[str]:
        disease_ko = DISPLAY_KO_MAP.get(predicted_label, predicted_label)
        guidance = [
            f"현재 예측 질환 후보는 {disease_ko}입니다.",
            "증상이 지속되거나 악화되면 피부과 진료를 권장합니다.",
        ]
        if needs_human_review:
            guidance.append("신뢰도가 충분히 높지 않아 의료진 확인이 필요할 수 있습니다.")
        if predicted_label == "normal":
            guidance.append("특이 병변이 뚜렷하지 않아도 자극성 화장품과 과도한 마찰은 피하는 것이 좋습니다.")
        return guidance

    def infer(self, request: DiagnosisRequest) -> DiagnosisResponse:
        image_path = Path(request.image_path) if request.image_path else None
        if image_path is None or not image_path.exists():
            return DiagnosisResponse(
                predicted_disease="unknown",
                confidence=0.0,
                differentials=[],
                needs_human_review=True,
                summary="입력 이미지 경로를 찾을 수 없어 baseline 진단을 수행하지 못했습니다.",
                retrieved_contexts=[],
                explanation="입력 이미지가 확인되지 않아 질환 설명을 생성하지 못했습니다.",
                care_guidance=["올바른 이미지 경로를 다시 확인해 주세요."],
            )

        if not self._runtime_loaded:
            self.load_runtime()

        assert self._model is not None
        image = Image.open(image_path).convert("RGB")
        x = self._transform(image).unsqueeze(0).to(self._device)
        with torch.no_grad():
            logits = self._model(x)
            probs = torch.softmax(logits, dim=1)[0]
            topk = torch.topk(probs, k=min(self.settings.rag.retrieval_top_k, len(BASELINE_LABELS)))

        predicted_idx = topk.indices[0].item()
        predicted_label = BASELINE_LABELS[predicted_idx]
        confidence = float(topk.values[0].item())
        differentials = [BASELINE_LABELS[idx.item()] for idx in topk.indices[1:]]
        needs_human_review = confidence < self.settings.baseline.human_review_confidence_threshold
        retrieved_contexts = retrieve_dermatology_contexts(predicted_label, differentials, top_k=self.settings.rag.retrieval_top_k)

        disease_ko = DISPLAY_KO_MAP.get(predicted_label, predicted_label)
        differential_ko = [DISPLAY_KO_MAP.get(label, label) for label in differentials]
        summary = (
            f"Baseline({self.settings.baseline.backbone}) 기준 {disease_ko} 가능성이 가장 높습니다. "
            f"신뢰도는 {confidence:.3f}이며, 감별 후보는 {', '.join(differential_ko) if differential_ko else '없음'}입니다."
        )
        if needs_human_review:
            summary += " 신뢰도가 충분히 높지 않아 전문의 확인이 필요할 수 있습니다."

        payload: dict[str, Any] = {
            "predicted_disease": predicted_label,
            "confidence": confidence,
            "differentials": differentials,
            "needs_human_review": needs_human_review,
            "summary": summary,
            "retrieved_contexts": retrieved_contexts,
            "explanation": self._build_explanation(predicted_label, confidence, retrieved_contexts),
            "care_guidance": self._build_care_guidance(predicted_label, needs_human_review),
        }
        return DiagnosisResponse.model_validate(payload)


@lru_cache(maxsize=1)
def get_vlm_service() -> VLMService:
    return VLMService()
