import argparse
import json
import random
from pathlib import Path

from utils.config import CONFIG
from utils.io import write_json
from utils.paths import MANIFEST_DIR, SPLIT_DIR


def build_split(
    manifest_path: Path,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> dict:
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    person_ids = sorted({row["person_id"] for row in rows})
    rng = random.Random(seed)
    rng.shuffle(person_ids)

    total = len(person_ids)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    split = {
        "train": person_ids[:train_end],
        "val": person_ids[train_end:val_end],
        "test": person_ids[val_end:],
    }
    return split


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_DIR / CONFIG["project"]["manifest_name"],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SPLIT_DIR / CONFIG["project"]["split_name"],
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    split = build_split(args.manifest, seed=args.seed)
    write_json(args.output, split)
    print(
        "split counts -> "
        f"train={len(split['train'])}, val={len(split['val'])}, test={len(split['test'])}"
    )


if __name__ == "__main__":
    main()
