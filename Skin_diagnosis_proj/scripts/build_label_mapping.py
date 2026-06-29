from __future__ import annotations

from _common import processed_dir, write_csv


def main() -> None:
    rows = [
        {"source_label": "??", "canonical_label": "psoriasis", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "???", "canonical_label": "atopic_dermatitis", "mapping_type": "normalized", "notes": "short label"},
        {"source_label": "??? ???", "canonical_label": "atopic_dermatitis", "mapping_type": "exact", "notes": "normalized disease name"},
        {"source_label": "???", "canonical_label": "acne", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "??", "canonical_label": "normal", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "??", "canonical_label": "rosacea", "mapping_type": "exact", "notes": "image label"},
        {"source_label": "??", "canonical_label": "seborrheic_dermatitis", "mapping_type": "normalized", "notes": "short label"},
        {"source_label": "??? ???", "canonical_label": "seborrheic_dermatitis", "mapping_type": "exact", "notes": "normalized disease name"},
        {"source_label": "????", "canonical_label": "facial_flushing", "mapping_type": "related_concept", "notes": "do not merge into rosacea"},
        {"source_label": "?? ???", "canonical_label": "facial_flushing", "mapping_type": "related_concept", "notes": "spacing variant"},
    ]
    out = processed_dir() / "label_mapping.csv"
    write_csv(out, ["source_label", "canonical_label", "mapping_type", "notes"], rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
