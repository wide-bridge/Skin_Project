from __future__ import annotations

import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _utf8 import read_csv_dicts_utf8_sig
from services.schemas import DiagnosisRequest
from services.vlm.service import get_vlm_service


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="psoriasis", help="target canonical label to sample from test split")
    args = parser.parse_args()

    manifest = read_csv_dicts_utf8_sig(PROJECT_ROOT / "data" / "processed" / "image_manifest.csv")
    sample = next(
        row
        for row in manifest
        if row["model_split"] == "test" and row["canonical_label"] == args.label
    )

    service = get_vlm_service()
    result = service.infer(DiagnosisRequest(image_path=sample["image_path"]))
    print(
        {
            "image_id": sample["image_id"],
            "ground_truth": sample["canonical_label"],
            "predicted_disease": result.predicted_disease,
            "confidence": result.confidence,
            "differentials": result.differentials,
            "retrieved_context_count": len(result.retrieved_contexts),
            "first_context": result.retrieved_contexts[0].model_dump() if result.retrieved_contexts else None,
            "explanation": result.explanation,
            "care_guidance": result.care_guidance,
        }
    )


if __name__ == "__main__":
    main()
