import json
from pathlib import Path
from typing import Iterable, Any


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def merge_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(current, dict):
            current.update(payload)
            payload = current
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
