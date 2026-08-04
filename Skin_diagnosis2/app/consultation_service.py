from typing import Optional

from app.diagnosis import predict_image
from app.rag_service import compose_answer
from app.safety import route_question
from app.schemas import ChatResponse


MAKEUP_INTENT_WORDS = [
    "메이크업", "화장", "커버", "쿠션", "파운데이션", "컨실러", "베이스", "색조",
]


def suggestions_for(route: str, has_diagnosis: bool):
    if route == "medical":
        return ["추가 증상 상담", "피부과 상담 기준", "생활 관리 방법"]
    if route == "hybrid":
        return ["커버 메이크업", "피해야 할 성분", "병원 방문 필요성"]
    if has_diagnosis:
        return ["증상 악화 신호", "피부과 상담 기준", "생활 관리 방법"]
    return ["피부 사진 분석", "증상 상담", "생활 관리 방법"]


def handle_consultation(message: str = "", image_bytes: Optional[bytes] = None, mode: str = "unified") -> ChatResponse:
    diagnosis = predict_image(image_bytes) if image_bytes else None
    diagnosis_label = diagnosis.label if diagnosis else None

    question = (message or "").strip()
    if not question and diagnosis:
        question = "이미지 분석 결과를 바탕으로 피부 병변 관리 방법과 피부과 상담이 필요한 기준을 알려주세요."
    elif not question:
        question = "피부 증상과 병변 관리 방법을 상담하고 싶습니다."

    route = route_question(question)

    answer = compose_answer(
        diagnosis=diagnosis_label,
        question=question,
        route=route,
        diagnosis_notice=diagnosis.notice if diagnosis else "",
    )

    return ChatResponse(
        mode=mode,
        route=route,
        answer=answer,
        diagnosis=diagnosis,
        suggestions=suggestions_for(route, diagnosis is not None),
    )
