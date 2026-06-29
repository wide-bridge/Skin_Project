from __future__ import annotations

from fastapi import APIRouter

from services.schemas import DiagnosisRequest, DiagnosisResponse
from services.vlm.service import get_vlm_service

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/diagnosis/infer", response_model=DiagnosisResponse)
def infer_diagnosis(request: DiagnosisRequest) -> DiagnosisResponse:
    service = get_vlm_service()
    return service.infer(request)
