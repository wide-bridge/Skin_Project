from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from _common import PROCESSED_DIR, SAMPLES_DIR, write_csv, write_minimal_png


def main() -> None:
    sample_image = SAMPLES_DIR / "sample_face_placeholder.png"
    if not sample_image.exists():
        write_minimal_png(sample_image)

    rows = [
        {
            "image_id": "sample-acne-001",
            "image_path": str(sample_image),
            "split": "train",
            "canonical_label": "acne",
            "source_label": "여드름",
            "view": "frontal",
            "source": "placeholder",
            "exists": True,
        }
    ]
    write_csv(
        PROCESSED_DIR / "image_manifest.csv",
        ["image_id", "image_path", "split", "canonical_label", "source_label", "view", "source", "exists"],
        rows,
    )
    print(f"wrote {PROCESSED_DIR / 'image_manifest.csv'}")


if __name__ == "__main__":
    main()
