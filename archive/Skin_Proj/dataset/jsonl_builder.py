import argparse
import json
from pathlib import Path

from utils.config import CONFIG
from utils.io import write_jsonl
from utils.labels import remap_label_value
from utils.paths import JSONL_DIR, MANIFEST_DIR, PROMPTS_DIR, SPLIT_DIR


def load_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8").strip()


def build_rows(manifest_path: Path, split_path: Path, prompt_path: Path) -> dict[str, list[dict]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    split = json.loads(split_path.read_text(encoding="utf-8"))
    prompt = load_prompt(prompt_path)
    owner = {}
    for split_name, person_ids in split.items():
        for person_id in person_ids:
            owner[person_id] = split_name

    result = {"train": [], "val": [], "test": []}
    for row in manifest:
        split_name = owner.get(row["person_id"])
        if not split_name:
            continue

        result[split_name].append(
            {
                "id": row["id"],
                "person_id": row["person_id"],
                "scenario": row["scenario"],
                "view": row["view"],
                "image": row["image_path"],
                "label": row["label_path"],
                "instruction": prompt,
                "output": {
                    "forehead_wrinkle": remap_label_value("forehead_wrinkle", int(row["forehead_wrinkle"])),
                    "forehead_pigmentation": remap_label_value("forehead_pigmentation", int(row["forehead_pigmentation"])),
                },
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DIR / CONFIG["project"]["manifest_name"])
    parser.add_argument("--split", type=Path, default=SPLIT_DIR / CONFIG["project"]["split_name"])
    parser.add_argument("--prompt", type=Path, default=PROMPTS_DIR / "train.txt")
    parser.add_argument("--output-dir", type=Path, default=JSONL_DIR)
    args = parser.parse_args()

    result = build_rows(args.manifest, args.split, args.prompt)
    output_names = {
        "train": CONFIG["project"]["train_jsonl_name"],
        "val": CONFIG["project"]["val_jsonl_name"],
        "test": CONFIG["project"]["test_jsonl_name"],
    }
    for split_name, rows in result.items():
        out_path = args.output_dir / output_names[split_name]
        write_jsonl(out_path, rows)
        print(f"{split_name} rows={len(rows)} -> {out_path}")


if __name__ == "__main__":
    main()
