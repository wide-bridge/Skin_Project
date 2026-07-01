from __future__ import annotations

from fastapi import APIRouter

from services.chat.service import get_chat_service
from services.schemas import ChatRequest, ChatResponse, DiagnosisRequest, DiagnosisResponse
from services.vlm.service import get_vlm_service

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/diagnosis/infer", response_model=DiagnosisResponse)
def infer_diagnosis(request: DiagnosisRequest) -> DiagnosisResponse:
    service = get_vlm_service()
    return service.infer(request)


@router.post("/chat/ask", response_model=ChatResponse)
def ask_chat(request: ChatRequest) -> ChatResponse:
    service = get_chat_service()
    return service.ask(request)
