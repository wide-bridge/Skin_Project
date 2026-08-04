import os
import json
import re
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import numpy as np
from openai import OpenAI

from app import config

_openai_client = None


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(http_client=httpx.Client(trust_env=False, timeout=60.0))
    return _openai_client


DIAGNOSIS_TO_MAKEUP_SKIN_PROBLEM = {
    "아토피": ["아토피 피부"],
    "여드름": ["면포성 여드름 피부", "화농성 여드름 피부"],
    "주사": ["주사 피부", "홍조 피부"],
    "지루": ["지루성 피부염"],
    "건선": ["민감성 피부", "홍조 피부"],
    "정상": [],
}

DIAGNOSIS_DIRECT_MAKEUP_LABEL = {
    "아토피": True,
    "여드름": True,
    "주사": True,
    "지루": True,
    "건선": False,
    "정상": False,
}

DIAGNOSIS_TO_MEDICAL_TERMS = {
    "아토피": ["아토피", "아토피 피부염"],
    "여드름": ["여드름", "면포", "화농성"],
    "주사": ["주사", "홍반", "Rosacea"],
    "지루": ["지루", "지루성 피부염"],
    "건선": ["건선"],
    "정상": ["피부 관리", "자외선 차단"],
}

MEDICAL_FORBIDDEN_TERMS = [
    "메이크업", "화장", "커버", "쿠션", "파운데이션", "컨실러", "베이스",
    "색조", "프라이머", "세팅 스프레이", "스펀지", "브러시",
]

DIAGNOSIS_MEDICAL_GUIDANCE = {
    "주사": (
        "주사는 얼굴 홍조, 따가움, 열감, 혈관 확장, 염증성 병변이 반복될 수 있는 피부 상태입니다. "
        "자외선, 온도 변화, 음주, 매운 음식, 사우나, 강한 자극을 줄이고 피부를 문지르지 않는 것이 중요합니다."
    ),
    "건선": (
        "건선은 붉은 반점과 각질이 반복될 수 있는 만성 염증성 피부질환입니다. "
        "피부 건조와 마찰을 줄이고 병변을 긁거나 억지로 각질을 떼어내지 않는 것이 중요합니다."
    ),
    "아토피": (
        "아토피 피부염은 가려움, 건조, 염증이 반복될 수 있는 피부질환입니다. "
        "피부 장벽이 약해질 수 있어 보습, 자극 회피, 가려움 악화 요인 관리가 중요합니다."
    ),
    "여드름": (
        "여드름은 면포, 염증성 구진, 농포 등이 생길 수 있는 피부질환입니다. "
        "병변을 짜거나 만지는 행동을 줄이고 염증이 심하거나 반복되면 피부과 상담이 필요합니다."
    ),
    "지루": (
        "지루성 피부염은 피지 분비가 많은 부위에 붉어짐, 각질, 가려움이 반복될 수 있는 피부질환입니다. "
        "과도한 세정과 자극을 피하고 증상 악화 시 피부과 상담이 필요합니다."
    ),
    "정상": (
        "이미지상 뚜렷한 병변 가능성이 낮더라도 피부 변화가 반복되거나 불편감이 있으면 경과 관찰이 필요합니다."
    ),
}


def make_query_text(diagnosis: Optional[str], question: str) -> str:
    diagnosis = diagnosis or ""
    mapped_makeup = ", ".join(DIAGNOSIS_TO_MAKEUP_SKIN_PROBLEM.get(diagnosis, []))
    medical_terms = ", ".join(DIAGNOSIS_TO_MEDICAL_TERMS.get(diagnosis, []))
    return f"진단결과: {diagnosis}\n관련 피부문제: {mapped_makeup}\n관련 의학용어: {medical_terms}\n사용자 질문: {question}"


def make_medical_query_text(diagnosis: Optional[str], question: str) -> str:
    diagnosis = diagnosis or ""
    medical_terms = ", ".join(DIAGNOSIS_TO_MEDICAL_TERMS.get(diagnosis, []))
    return f"진단결과: {diagnosis}\n관련 의학용어: {medical_terms}\n사용자 질문: {question}"


def _read_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _infer_makeup_category(folder_name: str):
    parts = folder_name.split("_")
    if len(parts) >= 3:
        return parts[1], parts[2]
    return "", folder_name


@lru_cache(maxsize=1)
def fallback_makeup_docs() -> List[Dict]:
    docs = []
    roots = [config.MAKEUP_TRAIN_DIR, config.MAKEUP_VALID_DIR]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            try:
                data = _read_json(path)
            except Exception:
                continue
            major_category, folder_skin_problem = _infer_makeup_category(path.parent.name)
            human = data.get("Human_info", {})
            skin = data.get("Skin_info", {})
            ann = data.get("Annotation_info", {})
            skin_problem = human.get("Skin Problem Type") or folder_skin_problem
            document = "\n".join([
                f"피부문제: {skin_problem}",
                f"대분류: {major_category}",
                f"피부상태: {skin.get('Skin condition category', '')}",
                f"피부밝기: {skin.get('Skin Brightness', '')}",
                f"고민상황: {skin.get('worry level/situation', '')}",
                f"메이크업목적: {human.get('makeup purpose', '')}",
                f"중요속성: {human.get('important attributes', '')}",
                f"질문: {ann.get('User Question', '')}",
                f"답변: {ann.get('Makeup Response', '')}",
                f"추천성분: {ann.get('Recommended Ingredients', '')}",
                f"회피성분: {ann.get('Ingredients to Avoid', '')}",
            ])
            docs.append({
                "document": document,
                "metadata": {
                    "source": "makeup_json_fallback",
                    "path": str(path),
                    "skin_problem": skin_problem,
                    "major_category": major_category,
                },
                "distance": 0.0,
            })
    return docs


@lru_cache(maxsize=1)
def fallback_derm_docs() -> List[Dict]:
    docs = []
    root = config.DERM_TRAIN_DIR
    if not root.exists():
        return docs
    for path in root.glob("*.json"):
        try:
            data = _read_json(path)
        except Exception:
            continue
        question = data.get("question", "")
        answer = data.get("answer", "")
        docs.append({
            "document": f"질문: {question}\n답변: {answer}",
            "metadata": {
                "source": "dermatology_json_fallback",
                "path": str(path),
                "qa_id": str(data.get("qa_id", "")),
                "q_type": str(data.get("q_type", "")),
            },
            "distance": 0.0,
        })
    return docs


def _faiss_text(doc: Dict) -> str:
    metadata = doc.get("metadata", {})
    metadata_text = " ".join(str(value) for value in metadata.values())
    return f"{doc.get('document', '')}\n{metadata_text}"


def _add_hash_feature(vector: np.ndarray, feature: str, weight: float):
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(digest, "little", signed=False)
    idx = value % vector.shape[0]
    sign = 1.0 if ((value >> 8) % 2 == 0) else -1.0
    vector[idx] += sign * weight


def _hash_embedding(text: str, dim: int = 768) -> np.ndarray:
    text = re.sub(r"\s+", " ", str(text).lower()).strip()
    vector = np.zeros(dim, dtype="float32")
    for token in text.split():
        _add_hash_feature(vector, f"tok:{token}", 1.5)
    compact = text.replace(" ", "")
    for n in range(2, 5):
        for i in range(max(0, len(compact) - n + 1)):
            _add_hash_feature(vector, compact[i:i + n], 1.0)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


def _hash_embeddings(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, 768), dtype="float32")
    return np.vstack([_hash_embedding(text) for text in texts]).astype("float32")


def _build_faiss_index(docs: List[Dict]):
    import faiss

    if not docs:
        return None, []
    texts = [_faiss_text(doc) for doc in docs]
    embeddings = _hash_embeddings(texts)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index, docs


@lru_cache(maxsize=1)
def makeup_faiss_index():
    return _build_faiss_index(fallback_makeup_docs())


@lru_cache(maxsize=1)
def derm_faiss_index():
    return _build_faiss_index(fallback_derm_docs())


def _faiss_search(index_docs, diagnosis: Optional[str], question: str, n_results: int, required_skin_problems=None) -> List[Dict]:
    return _faiss_search_with_query(index_docs, make_query_text(diagnosis, question), n_results, required_skin_problems)


def _faiss_search_with_query(index_docs, query_text: str, n_results: int, required_skin_problems=None) -> List[Dict]:
    index, docs = index_docs
    if index is None or not docs:
        return []
    query_embedding = _hash_embeddings([query_text])
    fetch_k = min(len(docs), max(n_results * 20, 50))
    scores, indices = index.search(query_embedding, fetch_k)

    rows = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        doc = dict(docs[int(idx)])
        metadata = dict(doc.get("metadata", {}))
        if required_skin_problems and metadata.get("skin_problem", "") not in required_skin_problems:
            continue
        metadata["retrieval_engine"] = "faiss"
        doc["metadata"] = metadata
        doc["distance"] = float(1.0 - score)
        rows.append(doc)
        if len(rows) >= n_results:
            break
    return rows


def _score_doc(doc: Dict, query_terms: List[str], required_skin_problems: Optional[List[str]] = None) -> int:
    text = (doc.get("document", "") + " " + " ".join(str(v) for v in doc.get("metadata", {}).values())).lower()
    score = sum(3 for term in query_terms if term and term.lower() in text)
    if required_skin_problems:
        skin_problem = doc.get("metadata", {}).get("skin_problem", "")
        if skin_problem in required_skin_problems:
            score += 20
    return score


def _fallback_search(docs: List[Dict], diagnosis: Optional[str], question: str, n_results: int, required_skin_problems=None) -> List[Dict]:
    question_terms = [term for term in re.split(r"[\s,./!?·]+", question or "") if len(term) >= 2]
    terms = [diagnosis or "", question] + question_terms + (DIAGNOSIS_TO_MEDICAL_TERMS.get(diagnosis or "", []))
    terms += DIAGNOSIS_TO_MAKEUP_SKIN_PROBLEM.get(diagnosis or "", [])
    scored = [(doc, _score_doc(doc, terms, required_skin_problems)) for doc in docs]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [doc for doc, _ in scored[:n_results]]


def retrieve_makeup(diagnosis: Optional[str], question: str, n_results: int = 4) -> List[Dict]:
    mapped = DIAGNOSIS_TO_MAKEUP_SKIN_PROBLEM.get(diagnosis or "", [])
    if diagnosis == "정상":
        return []

    try:
        rows = _faiss_search(makeup_faiss_index(), diagnosis, question, n_results, mapped or None)
        if rows:
            return rows
    except Exception as exc:
        print(f"FAISS makeup retrieval failed, using JSON keyword fallback: {exc}")
    return _fallback_search(fallback_makeup_docs(), diagnosis, question, n_results, mapped or None)


def retrieve_medical(diagnosis: Optional[str], question: str, n_results: int = 4) -> List[Dict]:
    try:
        rows = _faiss_search_with_query(derm_faiss_index(), make_medical_query_text(diagnosis, question), n_results)
        if rows:
            return rows
    except Exception as exc:
        print(f"FAISS medical retrieval failed, using JSON keyword fallback: {exc}")
    return _fallback_search(fallback_derm_docs(), diagnosis, question, n_results)


def build_context_block(rows: List[Dict], title: str, max_chars_per_doc: int = 900) -> str:
    if not rows:
        return f"[{title}]\n검색 결과 없음"
    parts = [f"[{title}]"]
    for idx, row in enumerate(rows, start=1):
        parts.append(f"문서 {idx}\nmetadata: {row.get('metadata', {})}\ncontent:\n{row.get('document', '')[:max_chars_per_doc]}")
    return "\n\n".join(parts)


def compose_answer(diagnosis: Optional[str], question: str, route: str, diagnosis_notice: str = "") -> str:
    makeup_rows = retrieve_makeup(diagnosis, question) if route in ("makeup", "hybrid") else []
    medical_rows = retrieve_medical(diagnosis, question) if route in ("medical", "hybrid") else []

    if not os.getenv("OPENAI_API_KEY"):
        return fallback_answer(diagnosis, question, route, makeup_rows, medical_rows, diagnosis_notice)

    if route == "medical":
        system_prompt = (
            "너는 피부질환·병변 진단보조 상담 챗봇이다. "
            "확정 진단, 처방, 약물 지시, 제품 추천은 하지 않는다. "
            "반드시 피부과 의학지식 RAG 검색 결과에 근거해 답한다. "
            "답변 범위는 피부질환/병변의 일반적 설명, 생활 관리, 악화 관찰 포인트, 피부과 상담 기준으로 제한한다. "
            "메이크업, 화장, 커버, 쿠션, 파운데이션, 컨실러, 베이스, 색조, 세팅 스프레이 관련 조언은 절대 포함하지 않는다."
        )
    else:
        system_prompt = (
            "너는 피부진단보조 및 메이크업 상담 PoC 챗봇이다. "
            "확정 진단, 처방, 약물 지시는 하지 않는다. "
            "반드시 RAG 검색 결과에 근거해 답하고, 검색 결과에 없는 성분명은 새로 만들지 않는다. "
            "통증, 급격한 악화, 진물, 출혈, 광범위한 염증, 반복 악화가 있으면 피부과 상담을 권장한다."
        )
    user_prompt = f"""
피부진단보조 결과: {diagnosis or '없음'}
진단 안내: {diagnosis_notice or '없음'}
질문 의도 route: {route}
사용자 질문: {question}

{build_context_block(makeup_rows, '메이크업 추천 RAG') if route in ('makeup', 'hybrid') else ''}

{build_context_block(medical_rows, '피부과 의학지식 RAG') if route in ('medical', 'hybrid') else ''}

답변 형식:
1. 이미지 기반 결과가 있으면 확정 진단이 아닌 보조 추정임을 짧게 안내
2. 사용자 질문에 직접 답변
3. route가 medical이면 피부질환·병변의 일반 관리, 악화 관찰 포인트, 피부과 상담 기준만 안내
4. route가 makeup 또는 hybrid일 때만 RAG 근거 기반 메이크업 방법/성분을 안내
5. 마지막에 짧은 주의 문구
""".strip()

    try:
        response = get_openai_client().chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        answer = response.choices[0].message.content.strip()
        if route == "medical" and contains_makeup_terms(answer):
            return medical_safe_answer(diagnosis, diagnosis_notice)
        return answer
    except Exception as exc:
        print(f"OpenAI answer generation failed, using rule-based fallback: {exc}")
        return fallback_answer(diagnosis, question, route, makeup_rows, medical_rows, diagnosis_notice)


def contains_makeup_terms(text: str) -> bool:
    return any(term in (text or "") for term in MEDICAL_FORBIDDEN_TERMS)


def medical_safe_answer(diagnosis, diagnosis_notice):
    lines = []
    if diagnosis_notice:
        lines.append(diagnosis_notice)
    if diagnosis:
        lines.append(DIAGNOSIS_MEDICAL_GUIDANCE.get(diagnosis, "피부 병변은 증상 변화와 악화 여부를 관찰하는 것이 중요합니다."))
    else:
        lines.append("피부 병변은 위치, 크기, 색 변화, 통증, 가려움, 진물 여부를 관찰하는 것이 중요합니다.")
    lines.extend([
        "일반 관리는 병변을 문지르거나 긁지 않고, 자극이 강한 세정과 과도한 마찰을 피하며, 피부가 건조하지 않도록 기본 보습을 유지하는 방향으로 진행합니다.",
        "악화 관찰 포인트는 붉은기 확대, 통증 증가, 진물, 출혈, 열감, 병변 범위 증가, 반복 악화입니다.",
        "증상이 빠르게 악화되거나 불편감이 지속되면 확정 진단과 치료 방향 확인을 위해 피부과 상담을 권장합니다.",
    ])
    return "\n\n".join(lines)


def fallback_answer(diagnosis, question, route, makeup_rows, medical_rows, diagnosis_notice):
    lines = []
    if diagnosis:
        lines.append(diagnosis_notice)
    if route == "medical":
        return medical_safe_answer(diagnosis, diagnosis_notice)
    lines.append("현재 질문에 대해 검색된 상담 근거를 기준으로 안내드립니다.")
    if route in ("makeup", "hybrid") and makeup_rows:
        lines.append(makeup_rows[0]["document"][:700])
    if route in ("medical", "hybrid") and medical_rows:
        lines.append(medical_rows[0]["document"][:700])
    lines.append("통증, 급격한 악화, 진물, 출혈, 광범위한 염증이 있으면 피부과 상담을 권장합니다.")
    return "\n\n".join(lines)
