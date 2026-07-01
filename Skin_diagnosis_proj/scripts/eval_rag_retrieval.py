from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _common import processed_dir
from _utf8 import read_csv_dicts_utf8_sig, read_jsonl_utf8, write_json_utf8, write_jsonl_utf8
from services.rag.retriever import retrieve_dermatology_contexts


def load_manifest() -> list[dict[str, str]]:
    return read_csv_dicts_utf8_sig(processed_dir() / "image_manifest.csv")


def load_predictions(split: str) -> list[dict]:
    path = processed_dir() / f"baseline_eval_predictions_{split}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"baseline predictions not found: {path}")
    return read_jsonl_utf8(path)


def build_manifest_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["image_id"]: row for row in rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="test")
    parser.add_argument("--per-class", type=int, default=5, help="number of samples to review for each ground-truth class")
    args = parser.parse_args()

    manifest = load_manifest()
    manifest_lookup = build_manifest_lookup(manifest)
    predictions = load_predictions(args.split)

    by_label: dict[str, list[dict]] = defaultdict(list)
    for row in predictions:
        by_label[str(row["ground_truth"])].append(row)

    selected: list[dict] = []
    for label, rows in sorted(by_label.items()):
        selected.extend(rows[: args.per_class])

    reviews: list[dict] = []
    retrieved_label_counter: Counter[str] = Counter()
    per_class_match_counter: dict[str, Counter[str]] = defaultdict(Counter)

    for row in selected:
        image_id = str(row["image_id"])
        predicted = str(row["predicted_disease"])
        ground_truth = str(row["ground_truth"])
        manifest_row = manifest_lookup.get(image_id, {})
        contexts = retrieve_dermatology_contexts(predicted, [], top_k=3)
        retrieved_labels = [str(ctx.get("canonical_label", "")) for ctx in contexts]
        for retrieved_label in retrieved_labels:
            retrieved_label_counter[retrieved_label] += 1
            per_class_match_counter[ground_truth][retrieved_label] += 1

        reviews.append(
            {
                "image_id": image_id,
                "ground_truth": ground_truth,
                "predicted_disease": predicted,
                "correct_prediction": bool(row.get("correct", False)),
                "view": manifest_row.get("view"),
                "retrieved_context_count": len(contexts),
                "retrieved_labels": retrieved_labels,
                "retrieved_doc_ids": [ctx.get("doc_id") for ctx in contexts],
                "retrieved_titles": [ctx.get("disease_name_ko") for ctx in contexts],
            }
        )

    summary = {
        "split": args.split,
        "per_class": args.per_class,
        "review_samples": len(reviews),
        "retrieved_label_counts": dict(retrieved_label_counter),
        "per_ground_truth_retrieved_labels": {
            label: dict(counter) for label, counter in sorted(per_class_match_counter.items())
        },
    }

    review_path = processed_dir() / f"rag_retrieval_review_{args.split}.jsonl"
    summary_path = processed_dir() / f"rag_retrieval_review_summary_{args.split}.json"
    write_jsonl_utf8(review_path, reviews)
    write_json_utf8(summary_path, summary, indent=2)

    print(f"saved {review_path}")
    print(f"saved {summary_path}")


if __name__ == "__main__":
    main()
