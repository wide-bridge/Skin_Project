from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from _common import CLASS_MAP, qna_training_root, slugify_text, write_jsonl
from _utf8 import read_json_utf8_sig


QUESTION_DIR_NAME = "1.질문"
ANSWER_DIR_NAME = "2.답변"
SKIN_DOMAIN_NAME = "피부질환"
PLASTIC_DOMAIN_NAME = "성형미용 및 재건"

CANONICAL_OVERRIDES = {
    "안면홍조": "facial_flushing",
    "hot_flush": "facial_flushing",
    "seborrheric_dermatitis": "seborrheic_dermatitis",
}


def question_root(base_root: Path, domain_name: str) -> Path:
    return base_root / QUESTION_DIR_NAME / domain_name


def answer_root(base_root: Path, domain_name: str) -> Path:
    return base_root / ANSWER_DIR_NAME / domain_name


def load_json(path: Path) -> dict:
    return read_json_utf8_sig(path)


def build_question_index(base_root: Path, domain_name: str) -> dict[tuple[str, str], list[dict]]:
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for path in sorted(question_root(base_root, domain_name).rglob("*.json")):
        data = load_json(path)
        disease_ko = data["disease_name"]["kor"].strip()
        intention = data.get("intention", "").strip()
        entry = {
            "question_id": data.get("fileName", path.stem),
            "question": data.get("question", "").strip(),
            "path": str(path),
            "entities": data.get("entities", []),
            "num_of_words": data.get("num_of_words"),
        }
        index[(disease_ko, intention)].append(entry)
    return index


def canonical_label_from_disease(disease_ko: str, disease_en: str) -> str:
    if disease_ko in CLASS_MAP:
        return CLASS_MAP[disease_ko]
    if disease_ko in CANONICAL_OVERRIDES:
        return CANONICAL_OVERRIDES[disease_ko]
    if disease_en:
        slug = slugify_text(disease_en)
        return CANONICAL_OVERRIDES.get(slug, slug)
    slug = slugify_text(disease_ko)
    return CANONICAL_OVERRIDES.get(slug, slug)


def answer_sections(answer: dict) -> dict[str, str]:
    return {
        "intro": answer.get("intro", "").strip(),
        "body": answer.get("body", "").strip(),
        "conclusion": answer.get("conclusion", "").strip(),
    }


def compose_content(representative_questions: list[str], sections: dict[str, str]) -> str:
    blocks: list[str] = []
    if representative_questions:
        blocks.append("대표 질문:\n" + "\n".join(f"- {question}" for question in representative_questions))
    answer_text = "\n\n".join(part for part in (sections["intro"], sections["body"], sections["conclusion"]) if part)
    if answer_text:
        blocks.append("답변:\n" + answer_text)
    return "\n\n".join(blocks).strip()


def build_corpus_rows(base_root: Path, domain_name: str, domain_slug: str) -> list[dict]:
    questions_by_key = build_question_index(base_root, domain_name)
    rows: list[dict] = []
    for path in sorted(answer_root(base_root, domain_name).rglob("*.json")):
        data = load_json(path)
        disease_ko = data["disease_name"]["kor"].strip()
        disease_en = data["disease_name"].get("eng", "").strip()
        intention = data.get("intention", "").strip()
        key = (disease_ko, intention)
        question_entries = questions_by_key.get(key, [])
        representative_questions: list[str] = []
        seen = set()
        for entry in question_entries:
            question = entry["question"]
            if question and question not in seen:
                representative_questions.append(question)
                seen.add(question)
            if len(representative_questions) >= 3:
                break
        sections = answer_sections(data["answer"])
        rows.append(
            {
                "doc_id": f"{domain_slug}-{data.get('fileName', path.stem)}",
                "domain": domain_slug,
                "category": data.get("disease_category", domain_name).strip(),
                "canonical_label": canonical_label_from_disease(disease_ko, disease_en),
                "disease_name_ko": disease_ko,
                "disease_name_en": disease_en,
                "intention": intention,
                "department": data.get("department", []),
                "question_count": len(question_entries),
                "representative_questions": representative_questions,
                "question_ids": [entry["question_id"] for entry in question_entries[:10]],
                "answer_intro": sections["intro"],
                "answer_body": sections["body"],
                "answer_conclusion": sections["conclusion"],
                "content": compose_content(representative_questions, sections),
                "source_type": "label_data",
                "source_path": str(path),
                "metadata": {
                    "answer_id": data.get("fileName", path.stem),
                    "question_example_paths": [entry["path"] for entry in question_entries[:3]],
                    "answer_num_of_words": data.get("num_of_words"),
                },
            }
        )
    return rows


def build_group_counter(base_root: Path, domain_name: str) -> dict[str, Counter]:
    q_counter: Counter = Counter()
    a_counter: Counter = Counter()
    for path in sorted(question_root(base_root, domain_name).rglob("*.json")):
        data = load_json(path)
        key = f"{data['disease_name']['kor'].strip()}||{data.get('intention', '').strip()}"
        q_counter[key] += 1
    for path in sorted(answer_root(base_root, domain_name).rglob("*.json")):
        data = load_json(path)
        key = f"{data['disease_name']['kor'].strip()}||{data.get('intention', '').strip()}"
        a_counter[key] += 1
    return {"questions": q_counter, "answers": a_counter}


def build_diff_rows(label_root: Path, source_root: Path, domain_name: str, domain_slug: str) -> list[dict]:
    label_counts = build_group_counter(label_root, domain_name)
    source_counts = build_group_counter(source_root, domain_name)
    keys = set(label_counts["questions"]) | set(label_counts["answers"]) | set(source_counts["questions"]) | set(source_counts["answers"])
    rows: list[dict] = []
    for key in sorted(keys):
        disease_ko, intention = key.split("||", 1)
        rows.append(
            {
                "domain": domain_slug,
                "disease_name_ko": disease_ko,
                "intention": intention,
                "label_question_count": label_counts["questions"][key],
                "label_answer_count": label_counts["answers"][key],
                "source_question_count": source_counts["questions"][key],
                "source_answer_count": source_counts["answers"][key],
                "question_count_diff": label_counts["questions"][key] - source_counts["questions"][key],
                "answer_count_diff": label_counts["answers"][key] - source_counts["answers"][key],
                "counts_match": (
                    label_counts["questions"][key] == source_counts["questions"][key]
                    and label_counts["answers"][key] == source_counts["answers"][key]
                ),
            }
        )
    return rows


def write_corpus(out_path: Path, rows: list[dict]) -> None:
    write_jsonl(out_path, rows)


def default_label_root() -> Path:
    return qna_training_root() / "label_data"


def default_source_root() -> Path:
    return qna_training_root() / "source_data"
