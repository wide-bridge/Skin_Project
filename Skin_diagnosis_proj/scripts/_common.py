from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable

import yaml

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
    with CONFIG_PATH.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def dataset_root() -> Path:
    return Path(load_config()["datasets"]["derma_ai_root"])


def processed_dir() -> Path:
    rel = load_config()["datasets"].get("processed_dir", "data/processed")
    return PROJECT_ROOT / rel


def test_per_class_view() -> int:
    return int(load_config()["datasets"].get("test_per_class_view", 20))


def ensure_processed_dir() -> None:
    processed_dir().mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> None:
    ensure_processed_dir()
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    ensure_processed_dir()
    with path.open("w", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")


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

