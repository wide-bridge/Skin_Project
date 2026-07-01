from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from scripts._utf8 import read_json_utf8, write_json_utf8
from scripts.build_general_rag_index import build_index
from services.config import ROOT_DIR, get_settings

TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z0-9_]+")
PLASTIC_KEYWORDS = {
    "성형",
    "재건",
    "코성형",
    "쌍꺼풀",
    "눈성형",
    "윤곽",
    "보형물",
    "가슴성형",
    "구개열",
    "구순열",
    "흉터성형",
}
DERMA_KEYWORDS = {
    "피부",
    "피부질환",
    "건선",
    "여드름",
    "주사",
    "아토피",
    "지루성",
    "붉음",
    "가려움",
    "트러블",
}
SYMPTOM_HINTS = {
    "acne": {"여드름", "트러블", "뾰루지", "농포", "면포", "턱", "피지", "염증"},
    "atopic_dermatitis": {"가려움", "건조", "보습", "아토피", "태열", "습진"},
    "rosacea": {"홍조", "붉음", "붉은", "주사", "열감", "얼굴 붉음"},
    "seborrheic_dermatitis": {"지루", "각질", "비듬", "두피", "코옆", "붉은 각질"},
    "psoriasis": {"건선", "은백색", "비늘", "판", "두꺼운 각질"},
}
INTENTION_HINTS = {
    "치료": {"치료", "연고", "약", "병원", "개선"},
    "예방": {"예방", "조심", "피하다", "생활", "관리", "루틴"},
    "정의": {"무엇", "뭐", "의미", "정의", "설명"},
    "진단": {"진단", "검사", "확인", "사진", "판별"},
}


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else ROOT_DIR / path


def _tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if len(token) > 1]


def _infer_domain(message: str) -> str:
    if any(keyword in message for keyword in PLASTIC_KEYWORDS):
        return "plastic_reconstruction"
    if any(keyword in message for keyword in DERMA_KEYWORDS):
        return "dermatology"
    return "dermatology"


@lru_cache(maxsize=1)
def load_general_vector_index() -> dict[str, Any]:
    settings = get_settings()
    path = _resolve(settings.rag.general_vector_index_path)
    if not path.exists():
        index = build_index()
        write_json_utf8(path, index)
        return index
    return read_json_utf8(path)


def retrieve_general_contexts(message: str, top_k: int | None = None) -> tuple[str, list[dict[str, Any]]]:
    settings = get_settings()
    if top_k is None:
        top_k = settings.rag.general_chat_top_k
    index = load_general_vector_index()
    domain = _infer_domain(message)
    tokens = _tokenize(message)
    if not tokens:
        return domain, []

    idf: dict[str, float] = index["idf"]
    counts = Counter(tokens)
    raw_weights = {token: count * idf[token] for token, count in counts.items() if token in idf}
    norm = math.sqrt(sum(weight * weight for weight in raw_weights.values())) or 1.0
    query_vector = {token: weight / norm for token, weight in raw_weights.items()}

    scored: list[tuple[float, dict[str, Any]]] = []
    for document in index["documents"]:
        if document.get("domain") != domain:
            continue
        vector = document.get("vector", {})
        score = sum(query_vector.get(token, 0.0) * float(weight) for token, weight in vector.items() if token in query_vector)
        if score > 0:
            scored.append((_score_document_for_message(document, message, score), document))

    scored.sort(key=lambda item: (-item[0], item[1].get("doc_id", "")))
    contexts: list[dict[str, Any]] = []
    for score, document in scored[:top_k]:
        contexts.append(
            {
                "doc_id": document.get("doc_id"),
                "domain": document.get("domain"),
                "disease_name_ko": document.get("disease_name_ko"),
                "canonical_label": document.get("canonical_label"),
                "intention": document.get("intention"),
                "content": document.get("content"),
                "source_path": ", ".join(document.get("source_paths", [])[:3]),
                "score": round(float(score), 4),
            }
        )
    return domain, contexts


def build_general_answer(message: str, domain: str, contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        if domain == "plastic_reconstruction":
            return "성형·재건 관련 질문으로 이해했지만, 바로 연결할 문서를 찾지 못했습니다. 수술 종류, 부위, 시기 같은 조건을 조금 더 구체적으로 알려주시면 다시 찾아드릴 수 있습니다."
        return "피부 관련 질문으로 이해했지만, 바로 연결할 문서를 찾지 못했습니다. 증상 부위, 색 변화, 가려움 여부처럼 증상을 조금 더 구체적으로 적어주시면 더 정확히 찾아드릴 수 있습니다."

    limit = get_settings().rag.general_chat_context_char_limit
    top = contexts[0]
    summary = str(top.get("content", "") or "").replace("\n", " ").strip()[:limit]
    disease_name = str(top.get("disease_name_ko", "") or "관련 질환")
    intention = str(top.get("intention", "") or "일반")
    if domain == "plastic_reconstruction":
        return f"질문하신 내용은 성형·재건 영역의 `{disease_name}` / `{intention}` 문서와 가장 가깝습니다. 참고 문서 기준으로 보면 {summary}"
    return f"질문하신 내용은 피부질환 영역의 `{disease_name}` / `{intention}` 문서와 가장 가깝습니다. 참고 문서 기준으로 보면 {summary}"


def _score_document_for_message(document: dict[str, Any], message: str, base_score: float) -> float:
    score = base_score
    canonical_label = str(document.get("canonical_label", "") or "")
    intention = str(document.get("intention", "") or "")
    for label, keywords in SYMPTOM_HINTS.items():
        if canonical_label == label and any(keyword in message for keyword in keywords):
            score += 0.9
    for hint_intention, keywords in INTENTION_HINTS.items():
        if intention == hint_intention and any(keyword in message for keyword in keywords):
            score += 0.45
    if document.get("domain") == "dermatology" and intention == "재활":
        score -= 0.35
    return score
