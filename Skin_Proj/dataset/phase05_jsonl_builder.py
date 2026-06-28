import argparse
import json
from pathlib import Path

from utils.io import write_jsonl
from utils.paths import OUTPUTS_DIR, PROMPTS_DIR


TARGETS = [
    "forehead_wrinkle",
    "forehead_pigmentation",
    "glabellus_wrinkle",
    "l_cheek_pigmentation",
    "r_cheek_pigmentation",
]


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_candidate_pool(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_unique_rows(candidate_payload: dict, prompt: str) -> list[dict]:
    by_id: dict[str, dict] = {}
    for target in TARGETS:
        for classes in candidate_payload["pool"][target].values():
            for items in classes.values():
                for item in items:
                    row = by_id.setdefault(
                        item["id"],
                        {
                            "id": item["id"],
                            "person_id": item["person_id"],
                            "scenario": item["scenario"],
                            "view": item["view"],
                            "image": item["image_path"],
                            "instruction": prompt,
                            "output": {key: int(item["labels"][key]) for key in TARGETS},
                            "phase05_targets": list(TARGETS),
                            "phase05_source": "class_balanced_reliable_data_candidate",
                        },
                    )
                    row.setdefault("phase05_slots", []).append(
                        {
                            "target": item["target"],
                            "class": int(item["class"]),
                            "scenario": item["scenario"],
                        }
                    )
    return sorted(by_id.values(), key=lambda row: (row["person_id"], row["scenario"], row["id"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build phase 05 local JSONL from class-balanced candidates.")
    parser.add_argument(
        "--candidates",
        type=Path,
        default=OUTPUTS_DIR / "eval" / "phase05_5target_class_balanced_candidates_min3.json",
    )
    parser.add_argument("--prompt", type=Path, default=PROMPTS_DIR / "phase05_train.txt")
    parser.add_argument("--output", type=Path, default=OUTPUTS_DIR / "eval" / "phase05_5target_train_candidates.jsonl")
    args = parser.parse_args()

    payload = load_candidate_pool(args.candidates)
    rows = build_unique_rows(payload, load_prompt(args.prompt))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output, rows)
    print(f"rows={len(rows)} -> {args.output}")


if __name__ == "__main__":
    main()
