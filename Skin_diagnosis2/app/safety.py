from app.config import UNCERTAIN_CONFIDENCE_THRESHOLD, UNCERTAIN_MARGIN_THRESHOLD


MEDICAL_KEYWORDS = [
    "병원", "치료", "약", "연고", "스테로이드", "원인", "심각", "진단",
    "증상", "가려움", "통증", "염증", "전염", "악화", "진물", "출혈",
]

MAKEUP_KEYWORDS = [
    "화장", "메이크업", "커버", "쿠션", "파운데이션", "컨실러", "베이스",
    "색조", "성분", "제품", "지속력", "피해야", "추천 성분", "립", "선크림",
]

WARNING_SIGNS = ["통증", "급격한 악화", "진물", "출혈", "광범위한 염증", "반복 악화"]


def route_question(question: str) -> str:
    text = (question or "").lower()
    makeup_score = sum(keyword in text for keyword in MAKEUP_KEYWORDS)
    medical_score = sum(keyword in text for keyword in MEDICAL_KEYWORDS)
    if makeup_score and medical_score:
        return "hybrid"
    if makeup_score > medical_score:
        return "makeup"
    return "medical"


def uncertainty_label(confidence: float, margin: float) -> str:
    if confidence < UNCERTAIN_CONFIDENCE_THRESHOLD or margin < UNCERTAIN_MARGIN_THRESHOLD:
        return "불확실"
    if confidence < 0.85 or margin < 0.30:
        return "중간"
    return "높음"


def diagnosis_notice(label: str, confidence: float, margin: float) -> str:
    level = uncertainty_label(confidence, margin)
    if level == "불확실":
        return (
            "이미지 기반 피부진단보조 결과가 불확실합니다. 확정 진단이 아니며, "
            "정면/조명/화질에 따라 주사·지루·여드름 등이 혼동될 수 있습니다."
        )
    return (
        f"이미지 기반 피부진단보조 결과 '{label}' 가능성이 {level} 수준입니다. "
        "확정 진단은 아니며 증상이 심하면 피부과 상담을 권장합니다."
    )


def warning_text() -> str:
    return "통증, 급격한 악화, 진물, 출혈, 광범위한 염증, 반복 악화가 있으면 피부과 상담을 권장합니다."
