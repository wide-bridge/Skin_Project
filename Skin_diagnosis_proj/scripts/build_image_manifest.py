from __future__ import annotations

import json
from pathlib import Path

from _common import CLASS_MAP, VIEW_MAP, dataset_root, deterministic_bucket, image_png_path, parse_folder_name, processed_dir, test_per_class_view, write_csv


FIELDNAMES = [
    "image_id",
    "image_path",
    "label_path",
    "original_split",
    "model_split",
    "canonical_label",
    "source_label",
    "view",
    "source",
    "exists",
]


def build_rows() -> list[dict]:
    rows: list[dict] = []
    root = dataset_root()
    for split_name, split_dir, folder_prefix in [("train", root / "Training" / "label_data", "TL"), ("val", root / "Validation" / "label_data", "VL")]:
        for label_folder_dir in sorted(split_dir.iterdir()):
            if not label_folder_dir.is_dir():
                continue
            _, label_ko, view_ko = parse_folder_name(label_folder_dir.name)
            canonical_label = CLASS_MAP[label_ko]
            view = VIEW_MAP[view_ko]
            items = sorted(label_folder_dir.glob("*.json"))
            if split_name == "val":
                ordered = sorted(items, key=lambda p: deterministic_bucket(p.stem))
                test_names = {p.stem for p in ordered[:test_per_class_view()]}
            else:
                test_names = set()
            for label_path in items:
                stem = label_path.stem
                image_path = image_png_path(split_name, f"{label_ko}_{view_ko}", stem)
                model_split = "test" if stem in test_names else split_name
                rows.append({
                    "image_id": stem,
                    "image_path": str(image_path),
                    "label_path": str(label_path),
                    "original_split": split_name,
                    "model_split": model_split,
                    "canonical_label": canonical_label,
                    "source_label": label_ko,
                    "view": view,
                    "source": "derma_ai",
                    "exists": image_path.exists() and label_path.exists(),
                })
    return rows


def main() -> None:
    out = processed_dir() / "image_manifest.csv"
    rows = build_rows()
    write_csv(out, FIELDNAMES, rows)
    print(f"wrote {out} with {len(rows)} rows")


if __name__ == "__main__":
    main()

