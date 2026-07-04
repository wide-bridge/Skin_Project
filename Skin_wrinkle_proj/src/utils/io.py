from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def write_json(path: str | Path, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')


def write_csv(path: str | Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    import csv

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
