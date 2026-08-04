from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "baseline_config.yaml"
CONFIG_ENV_VAR = "SKIN_DIAGNOSIS_CONFIG"


def load_config() -> dict[str, Any]:
    config_path = Path(os.environ.get(CONFIG_ENV_VAR, CONFIG_PATH))
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def active_config_path() -> Path:
    return Path(os.environ.get(CONFIG_ENV_VAR, CONFIG_PATH))


def processed_dir() -> Path:
    cfg = load_config()
    return Path(cfg["dataset"]["output_dir"])


def experiment_name() -> str:
    cfg = load_config()
    return str(cfg["dataset"].get("experiment_name", "default"))


def manifest_path() -> Path:
    cfg = load_config()
    return Path(cfg["dataset"]["manifest_path"])


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def write_json(path: Path, data: Any, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=indent)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def label_list() -> list[str]:
    cfg = load_config()
    return list(cfg["labels"])


def filter_rows_by_labels(rows: list[dict[str, str]], labels: list[str] | None = None) -> list[dict[str, str]]:
    allowed = set(labels or label_list())
    return [row for row in rows if row.get("canonical_label") in allowed]
