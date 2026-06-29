from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from _common import PROCESSED_DIR, write_csv


def main() -> None:
    rows = [
        {"canonical_label": "psoriasis", "display_name_ko": "건선", "display_name_en": "Psoriasis", "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "atopic_dermatitis", "display_name_ko": "아토피 피부염", "display_name_en": "Atopic Dermatitis", "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "acne", "display_name_ko": "여드름", "display_name_en": "Acne", "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "normal", "display_name_ko": "정상", "display_name_en": "Normal", "category": "normal", "is_active": True, "notes": "image_class"},
        {"canonical_label": "rosacea", "display_name_ko": "주사", "display_name_en": "Rosacea", "category": "skin_disease", "is_active": True, "notes": "image_class, text knowledge gap"},
        {"canonical_label": "seborrheic_dermatitis", "display_name_ko": "지루성 피부염", "display_name_en": "Seborrheic Dermatitis", "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "facial_flushing", "display_name_ko": "안면홍조", "display_name_en": "Facial Flushing", "category": "related_concept", "is_active": True, "notes": "related concept only; do not merge with rosacea"},
    ]
    write_csv(PROCESSED_DIR / "disease_ontology.csv", ["canonical_label", "display_name_ko", "display_name_en", "category", "is_active", "notes"], rows)
    print(f"wrote {PROCESSED_DIR / 'disease_ontology.csv'}")


if __name__ == "__main__":
    main()
