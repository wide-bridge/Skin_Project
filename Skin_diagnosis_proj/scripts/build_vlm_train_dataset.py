from __future__ import annotations

import csv
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from _common import PROCESSED_DIR, write_jsonl


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def build_messages(row: dict[str, str]) -> list[dict[str, str]]:
    disease = row.get("source_label") or row.get("canonical_label") or "미상"
    return [
        {"role": "system", "content": "피부질환 진단 보조 모델입니다. 지정된 JSON 스키마로만 응답하세요."},
        {"role": "user", "content": f"이 얼굴 이미지의 피부 상태를 분석하고 JSON으로 답하세요. 정답 라벨: {disease}"},
        {"role": "assistant", "content": f'{{"predicted_disease":"{row.get("canonical_label", "unknown")}","confidence":0.95,"differentials":[],"needs_human_review":false}}'},
    ]


def main() -> None:
    manifest_rows = load_manifest(PROCESSED_DIR / "image_manifest.csv")
    rows = []
    for row in manifest_rows:
        rows.append({
            "id": row["image_id"],
            "image": row["image_path"],
            "messages": build_messages(row),
            "metadata": {
                "split": row.get("split", "train"),
                "canonical_label": row.get("canonical_label", "unknown"),
                "source_label": row.get("source_label", ""),
                "view": row.get("view", "unknown"),
            },
        })
    write_jsonl(PROCESSED_DIR / "vlm_train_dataset.jsonl", rows)
    print(f"wrote {PROCESSED_DIR / 'vlm_train_dataset.jsonl'}")


if __name__ == "__main__":
    main()
