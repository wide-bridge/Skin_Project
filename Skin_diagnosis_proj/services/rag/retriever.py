from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from scripts._common import DISPLAY_KO_MAP
from scripts._utf8 import read_json_utf8, read_jsonl_utf8
from services.config import ROOT_DIR, get_settings


def _derma_corpus_path() -> Path:
    settings = get_settings()
    path = Path(settings.rag.derma_corpus_path)
    return path if path.is_absolute() else ROOT_DIR / path


def _plastic_corpus_path() -> Path:
    settings = get_settings()
    path = Path(settings.rag.plastic_corpus_path)
    return path if path.is_absolute() else ROOT_DIR / path


def _alias_mapping_path() -> Path:
    settings = get_settings()
    path = Path(settings.rag.alias_mapping_path)
    return path if path.is_absolute() else ROOT_DIR / path


def _default_guidance_terms() -> list[str]:
    return list(get_settings().rag.default_guidance_terms)


@lru_cache(maxsize=1)
def load_disease_aliases() -> dict[str, list[str]]:
    raw = read_json_utf8(_alias_mapping_path())
    return {str(key): [str(item) for item in value] for key, value in dict(raw).items()}


@lru_cache(maxsize=1)
def load_derma_corpus() -> list[dict[str, Any]]:
    return read_jsonl_utf8(_derma_corpus_path())


@lru_cache(maxsize=1)
def load_plastic_corpus() -> list[dict[str, Any]]:
    return read_jsonl_utf8(_plastic_corpus_path())


def _score_row(row: dict[str, Any], terms: list[str], preferred_intentions: list[str] | None = None) -> int:
    disease_name = str(row.get("disease_name_ko", ""))
    intention = str(row.get("intention", "") or "")
    haystacks = [
        disease_name,
        str(row.get("category", "")),
        str(row.get("content", "")),
        str(row.get("answer_intro", "")),
        str(row.get("answer_body", "")),
        str(row.get("answer_conclusion", "")),
    ]
    score = 0
    for term in terms:
        if not term:
            continue
        if disease_name == term:
            score += 100
            continue
        for value in haystacks[1:]:
            if term in value:
                score += 1
    score += min(int(row.get("question_count", 0)), 3)
    if preferred_intentions and intention in preferred_intentions:
        score += 20
    return score


def _select_rows(
    rows: list[dict[str, Any]],
    terms: list[str],
    top_k: int,
    preferred_intentions: list[str] | None = None,
) -> list[dict[str, Any]]:
    exact_rows = [row for row in rows if str(row.get("disease_name_ko", "")) in terms]
    search_rows = exact_rows if exact_rows else rows
    scored: list[tuple[int, dict[str, Any]]] = []
    for row in search_rows:
        score = _score_row(row, terms, preferred_intentions)
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1].get("doc_id", "")))
    return [row for _, row in scored[:top_k]]


def _fallback_rows(rows: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    scored: list[tuple[int, dict[str, Any]]] = []
    for row in rows:
        score = _score_row(row, _default_guidance_terms())
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1].get("doc_id", "")))
    return [row for _, row in scored[:top_k]]


def retrieve_dermatology_contexts(
    predicted_disease: str,
    differentials: list[str] | None = None,
    top_k: int | None = None,
    preferred_intentions: list[str] | None = None,
) -> list[dict[str, Any]]:
    if top_k is None:
        top_k = int(get_settings().rag.retrieval_top_k)
    if predicted_disease == "normal":
        return []
    corpus = load_derma_corpus()
    disease_aliases = load_disease_aliases()
    primary_terms: list[str] = []
    primary_ko = DISPLAY_KO_MAP.get(predicted_disease)
    if primary_ko:
        primary_terms.append(primary_ko)
    primary_terms.extend(disease_aliases.get(predicted_disease, []))

    selected = _select_rows(corpus, primary_terms, top_k, preferred_intentions)
    if not selected and differentials:
        differential_terms: list[str] = []
        for label in differentials:
            diff_ko = DISPLAY_KO_MAP.get(label)
            if diff_ko:
                differential_terms.append(diff_ko)
            differential_terms.extend(disease_aliases.get(label, []))
        selected = _select_rows(corpus, differential_terms, top_k, preferred_intentions)
    if not selected:
        selected = _fallback_rows(corpus, top_k)

    contexts: list[dict[str, Any]] = []
    for row in selected:
        contexts.append(
            {
                "doc_id": row.get("doc_id"),
                "domain": row.get("domain"),
                "disease_name_ko": row.get("disease_name_ko"),
                "canonical_label": row.get("canonical_label"),
                "intention": row.get("intention"),
                "content": row.get("content"),
                "source_path": row.get("source_path"),
            }
        )
    return contexts
