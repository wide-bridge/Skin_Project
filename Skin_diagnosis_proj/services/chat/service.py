from __future__ import annotations

import base64
import hashlib
from functools import lru_cache
from pathlib import Path

from scripts._common import DISPLAY_KO_MAP
from services.config import ROOT_DIR
from services.rag.general_retriever import build_general_answer, retrieve_general_contexts
from services.schemas import ChatRequest, ChatResponse, DiagnosisRequest
from services.vlm.service import get_vlm_service


class ChatService:
    def __init__(self) -> None:
        self._uploads_dir = ROOT_DIR / "data" / "uploads" / "chat"
        self._uploads_dir.mkdir(parents=True, exist_ok=True)

    def _persist_uploaded_image(self, image_name: str | None, image_bytes_base64: str) -> Path:
        suffix = ".png"
        if image_name and "." in image_name:
            suffix = Path(image_name).suffix or ".png"
        payload = image_bytes_base64.split(",", 1)[-1]
        image_bytes = base64.b64decode(payload)
        digest = hashlib.md5(image_bytes).hexdigest()
        path = self._uploads_dir / f"chat_{digest}{suffix}"
        if not path.exists():
            path.write_bytes(image_bytes)
        return path

    def ask(self, request: ChatRequest) -> ChatResponse:
        image_path: str | None = request.image_path
        if request.image_bytes_base64:
            saved = self._persist_uploaded_image(request.image_name, request.image_bytes_base64)
            image_path = str(saved)

        if image_path:
            diagnosis_result = get_vlm_service().infer(DiagnosisRequest(image_path=image_path))
            disease_ko = DISPLAY_KO_MAP.get(diagnosis_result.predicted_disease, diagnosis_result.predicted_disease)
            guidance = diagnosis_result.care_guidance[:2]
            answer = f"{disease_ko} 관리와 치료 방향을 중심으로 간단히 안내합니다. {' · '.join(guidance)}"
            return ChatResponse(
                mode="image_analysis",
                user_message=request.message,
                answer=answer,
                related_domain="dermatology",
                image_path=image_path,
                diagnosis_result=diagnosis_result,
                retrieved_contexts=diagnosis_result.retrieved_contexts,
            )

        domain, contexts = retrieve_general_contexts(request.message)
        answer = build_general_answer(request.message, domain, contexts)
        return ChatResponse(
            mode="general_rag",
            user_message=request.message,
            answer=answer,
            related_domain=domain,
            retrieved_contexts=contexts,
        )


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService()
