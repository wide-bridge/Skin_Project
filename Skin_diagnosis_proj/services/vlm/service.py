from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from services.config import get_settings
from services.schemas import DiagnosisRequest, DiagnosisResponse
from services.vlm.prompting import load_diagnosis_prompt


class VLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.prompt = load_diagnosis_prompt()
        self._runtime_loaded = False

    def load_runtime(self) -> None:
        # Phase 04 placeholder:
        # Qwen-family VLM loading and LoRA adapter attachment will be added later.
        self._runtime_loaded = True

    def infer(self, request: DiagnosisRequest) -> DiagnosisResponse:
        image_exists = False
        if request.image_path:
            image_exists = Path(request.image_path).exists()

        if not self._runtime_loaded:
            self.load_runtime()

        payload: dict[str, Any] = {
            "predicted_disease": "acne" if image_exists else "unknown",
            "confidence": 0.81 if image_exists else 0.0,
            "differentials": ["comedonal_acne", "inflammatory_papule"] if image_exists else [],
            "needs_human_review": True,
            "summary": "Placeholder response generated without loading an actual VLM model.",
        }
        return self._parse_response(payload)

    def _parse_response(self, payload: dict[str, Any] | str) -> DiagnosisResponse:
        if isinstance(payload, str):
            payload = json.loads(payload)
        return DiagnosisResponse.model_validate(payload)


@lru_cache(maxsize=1)
def get_vlm_service() -> VLMService:
    return VLMService()
