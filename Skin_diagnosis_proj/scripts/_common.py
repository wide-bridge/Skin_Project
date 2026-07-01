from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

try:
    from scripts._utf8 import read_yaml_utf8, write_csv_dicts_utf8_sig, write_jsonl_utf8
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from _utf8 import read_yaml_utf8, write_csv_dicts_utf8_sig, write_jsonl_utf8

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.template.yaml"

CLASS_MAP = {
    "건선": "psoriasis",
    "아토피": "atopic_dermatitis",
    "여드름": "acne",
    "정상": "normal",
    "주사": "rosacea",
    "지루": "seborrheic_dermatitis",
}

BASELINE_LABELS = [
    "acne",
    "atopic_dermatitis",
    "normal",
    "psoriasis",
    "rosacea",
    "seborrheic_dermatitis",
]

VIEW_MAP = {
    "정면": "frontal",
    "측면": "side",
}

DISPLAY_EN_MAP = {
    "psoriasis": "Psoriasis",
    "atopic_dermatitis": "Atopic Dermatitis",
    "acne": "Acne",
    "normal": "Normal",
    "rosacea": "Rosacea",
    "seborrheic_dermatitis": "Seborrheic Dermatitis",
    "facial_flushing": "Facial Flushing",
}

DISPLAY_KO_MAP = {
    "psoriasis": "건선",
    "atopic_dermatitis": "아토피 피부염",
    "acne": "여드름",
    "normal": "정상",
    "rosacea": "주사",
    "seborrheic_dermatitis": "지루성 피부염",
    "facial_flushing": "안면홍조",
}


def load_config() -> dict:
    return read_yaml_utf8(CONFIG_PATH)


def dataset_root() -> Path:
    return Path(load_config()["datasets"]["derma_ai_root"])


def qna_training_root() -> Path:
    return Path(load_config()["datasets"]["qna_training_root"])


def processed_dir() -> Path:
    rel = load_config()["datasets"].get("processed_dir", "data/processed")
    return PROJECT_ROOT / rel


def test_per_class_view() -> int:
    return int(load_config()["datasets"].get("test_per_class_view", 20))


def ensure_processed_dir() -> None:
    processed_dir().mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> None:
    ensure_processed_dir()
    write_csv_dicts_utf8_sig(path, fieldnames, rows)


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    ensure_processed_dir()
    write_jsonl_utf8(path, rows)


def parse_folder_name(name: str) -> tuple[str, str, str]:
    parts = name.split("_")
    prefix = parts[0]
    label_ko = parts[1]
    view_ko = parts[2]
    return prefix, label_ko, view_ko


def deterministic_bucket(key: str) -> int:
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def image_png_path(split_dir: str, label_folder: str, stem: str) -> Path:
    prefix = "Training" if split_dir == "train" else "Validation"
    source_prefix = "TS" if split_dir == "train" else "VS"
    return dataset_root() / prefix / "source_data" / f"{source_prefix}_{label_folder}" / f"{stem}.png"


def slugify_text(text: str) -> str:
    cleaned = []
    for char in text.lower().strip():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "-", "_", "/"}:
            cleaned.append("_")
    slug = "".join(cleaned).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or "unknown"
