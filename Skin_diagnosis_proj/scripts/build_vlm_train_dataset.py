from __future__ import annotations

import csv
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _common import processed_dir, write_jsonl


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def build_messages(row: dict[str, str]) -> list[dict[str, str]]:
    disease_ko = row.get("source_label") or "미상"
    canonical = row.get("canonical_label") or "unknown"
    return [
        {"role": "system", "content": "피부질환 진단 보조 모델입니다. 지정된 JSON 스키마로만 응답하세요."},
        {"role": "user", "content": f"이 얼굴 이미지의 피부 상태를 분석하고 JSON으로 답하세요. 후보 질환은 건선, 아토피 피부염, 여드름, 정상, 주사, 지루성 피부염입니다. 정답 라벨: {disease_ko}"},
        {"role": "assistant", "content": f'{{"predicted_disease":"{canonical}","confidence":0.95,"differentials":[],"needs_human_review":false}}'},
    ]


def main() -> None:
    manifest_path = processed_dir() / "image_manifest.csv"
    rows = []
    for row in load_manifest(manifest_path):
        rows.append({
            "id": row["image_id"],
            "image": row["image_path"],
            "messages": build_messages(row),
            "metadata": {
                "model_split": row["model_split"],
                "original_split": row["original_split"],
                "canonical_label": row["canonical_label"],
                "source_label": row["source_label"],
                "view": row["view"],
            },
        })
    out = processed_dir() / "vlm_train_dataset.jsonl"
    write_jsonl(out, rows)
    print(f"wrote {out} with {len(rows)} rows")


if __name__ == "__main__":
    main()
