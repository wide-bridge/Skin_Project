from __future__ import annotations

from _common import DISPLAY_EN_MAP, processed_dir, write_csv


def main() -> None:
    rows = [
        {"canonical_label": "psoriasis", "display_name_ko": "??", "display_name_en": DISPLAY_EN_MAP["psoriasis"], "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "atopic_dermatitis", "display_name_ko": "??? ???", "display_name_en": DISPLAY_EN_MAP["atopic_dermatitis"], "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "acne", "display_name_ko": "???", "display_name_en": DISPLAY_EN_MAP["acne"], "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "normal", "display_name_ko": "??", "display_name_en": DISPLAY_EN_MAP["normal"], "category": "normal", "is_active": True, "notes": "image_class"},
        {"canonical_label": "rosacea", "display_name_ko": "??", "display_name_en": DISPLAY_EN_MAP["rosacea"], "category": "skin_disease", "is_active": True, "notes": "image_class; keep independent from facial_flushing"},
        {"canonical_label": "seborrheic_dermatitis", "display_name_ko": "??? ???", "display_name_en": DISPLAY_EN_MAP["seborrheic_dermatitis"], "category": "skin_disease", "is_active": True, "notes": "image_class"},
        {"canonical_label": "facial_flushing", "display_name_ko": "????", "display_name_en": DISPLAY_EN_MAP["facial_flushing"], "category": "related_concept", "is_active": True, "notes": "do not merge into rosacea"},
    ]
    out = processed_dir() / "disease_ontology.csv"
    write_csv(out, ["canonical_label", "display_name_ko", "display_name_en", "category", "is_active", "notes"], rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
