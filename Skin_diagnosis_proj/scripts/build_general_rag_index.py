from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scripts._utf8 import read_jsonl_utf8, write_json_utf8
from services.config import ROOT_DIR, get_settings

TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z0-9_]+")
MAX_QUESTION_COUNT = 6
MAX_CONTENT_COUNT = 3
MAX_CONTENT_CHARS = 800


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else ROOT_DIR / path


def _tokenize(text: str) -> list[str]:
    text = text.lower().strip()
    return [token for token in TOKEN_PATTERN.findall(text) if len(token) > 1]


def _group_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        domain = str(row.get("domain", "") or "")
        label = str(row.get("canonical_label", "") or "")
        disease_name_ko = str(row.get("disease_name_ko", "") or "")
        intention = str(row.get("intention", "") or "일반")
        key = (domain, label, disease_name_ko, intention)
        entry = grouped.setdefault(
            key,
            {
                "doc_id": f"{domain}-{label or disease_name_ko}-{intention}",
                "domain": domain,
                "canonical_label": label,
                "disease_name_ko": disease_name_ko,
                "intention": intention,
                "content_parts": [],
                "questions": [],
                "source_paths": [],
            },
        )
        content = str(row.get("content", "") or "").strip()
        if content and len(entry["content_parts"]) < MAX_CONTENT_COUNT and content not in entry["content_parts"]:
            entry["content_parts"].append(content[:MAX_CONTENT_CHARS])
        for question in row.get("representative_questions", []) or []:
            question = str(question).strip()
            if question and question not in entry["questions"] and len(entry["questions"]) < MAX_QUESTION_COUNT:
                entry["questions"].append(question)
        source_path = str(row.get("source_path", "") or "")
        if source_path and source_path not in entry["source_paths"]:
            entry["source_paths"].append(source_path)
    documents: list[dict[str, Any]] = []
    for entry in grouped.values():
        text_parts = [
            entry["disease_name_ko"],
            entry["canonical_label"],
            entry["intention"],
            *entry["questions"],
            *entry["content_parts"],
        ]
        combined = "\n\n".join(part for part in text_parts if part)
        documents.append(
            {
                "doc_id": entry["doc_id"],
                "domain": entry["domain"],
                "canonical_label": entry["canonical_label"],
                "disease_name_ko": entry["disease_name_ko"],
                "intention": entry["intention"],
                "content": combined,
                "source_paths": entry["source_paths"][:5],
            }
        )
    return documents


def build_index() -> dict[str, Any]:
    settings = get_settings()
    derma_rows = read_jsonl_utf8(_resolve(settings.rag.derma_corpus_path))
    plastic_rows = read_jsonl_utf8(_resolve(settings.rag.plastic_corpus_path))
    documents = _group_rows(derma_rows + plastic_rows)

    doc_tokens: list[list[str]] = []
    document_frequency: defaultdict[str, int] = defaultdict(int)
    for document in documents:
        tokens = _tokenize(document["content"])
        doc_tokens.append(tokens)
        for token in set(tokens):
            document_frequency[token] += 1

    doc_count = max(len(documents), 1)
    idf = {
        token: math.log((doc_count + 1) / (freq + 1)) + 1.0
        for token, freq in document_frequency.items()
    }

    indexed_documents: list[dict[str, Any]] = []
    for document, tokens in zip(documents, doc_tokens, strict=True):
        counts = Counter(tokens)
        raw_weights = {token: count * idf[token] for token, count in counts.items()}
        norm = math.sqrt(sum(weight * weight for weight in raw_weights.values())) or 1.0
        vector = {token: weight / norm for token, weight in raw_weights.items()}
        indexed_documents.append(
            {
                **document,
                "vector": vector,
            }
        )

    return {
        "version": 1,
        "doc_count": len(indexed_documents),
        "vocabulary_size": len(idf),
        "idf": idf,
        "documents": indexed_documents,
    }


def main() -> None:
    settings = get_settings()
    output_path = _resolve(settings.rag.general_vector_index_path)
    index = build_index()
    write_json_utf8(output_path, index)
    print(
        {
            "general_vector_index_path": str(output_path),
            "doc_count": index["doc_count"],
            "vocabulary_size": index["vocabulary_size"],
        }
    )


if __name__ == "__main__":
    main()
