from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from _common import PROCESSED_DIR, write_csv


def main() -> None:
    rows = [
        {"source_label": "건선", "canonical_label": "psoriasis", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "아토피", "canonical_label": "atopic_dermatitis", "mapping_type": "normalized", "notes": "short label"},
        {"source_label": "아토피 피부염", "canonical_label": "atopic_dermatitis", "mapping_type": "exact", "notes": "normalized disease name"},
        {"source_label": "여드름", "canonical_label": "acne", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "정상", "canonical_label": "normal", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "주사", "canonical_label": "rosacea", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "지루", "canonical_label": "seborrheic_dermatitis", "mapping_type": "normalized", "notes": "short label"},
        {"source_label": "지루성 피부염", "canonical_label": "seborrheic_dermatitis", "mapping_type": "exact", "notes": "normalized disease name"},
        {"source_label": "안면홍조", "canonical_label": "facial_flushing", "mapping_type": "related_concept", "notes": "do not merge into rosacea"},
        {"source_label": "안면 홍조증", "canonical_label": "facial_flushing", "mapping_type": "related_concept", "notes": "spacing variant"},
    ]
    write_csv(PROCESSED_DIR / "label_mapping.csv", ["source_label", "canonical_label", "mapping_type", "notes"], rows)
    print(f"wrote {PROCESSED_DIR / 'label_mapping.csv'}")


if __name__ == "__main__":
    main()
