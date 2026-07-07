import argparse
import json
from pathlib import Path

from utils.config import CONFIG
from utils.io import write_json
from utils.paths import JSONL_DIR, LOG_DIR, MANIFEST_DIR, SPLIT_DIR

REQUIRED_MANIFEST_KEYS = {
    "id",
    "person_id",
    "scenario",
    "view",
    "image_path",
    "label_path",
    "forehead_wrinkle",
    "forehead_pigmentation",
}
REQUIRED_OUTPUT_KEYS = set(CONFIG["task"]["target_keys"])


def validate(manifest_path: Path, split_path: Path, jsonl_dir: Path) -> dict:
    issues: dict[str, list] = {
        "missing_image": [],
        "missing_label": [],
        "missing_manifest_keys": [],
        "invalid_label_type": [],
        "split_leakage": [],
        "jsonl_errors": [],
    }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    split = json.loads(split_path.read_text(encoding="utf-8"))
    owner = {}
    for split_name, person_ids in split.items():
        for person_id in person_ids:
            if person_id in owner and owner[person_id] != split_name:
                issues["split_leakage"].append(
                    {"person_id": person_id, "splits": [owner[person_id], split_name]}
                )
            owner[person_id] = split_name

    for row in manifest:
        missing = sorted(REQUIRED_MANIFEST_KEYS - row.keys())
        if missing:
            issues["missing_manifest_keys"].append({"id": row.get("id"), "missing": missing})

        if not Path(row["image_path"]).exists():
            issues["missing_image"].append(row["image_path"])
        if not Path(row["label_path"]).exists():
            issues["missing_label"].append(row["label_path"])

        for key in REQUIRED_OUTPUT_KEYS:
            if not isinstance(row.get(key), int):
                issues["invalid_label_type"].append(
                    {"id": row.get("id"), "key": key, "value": row.get(key)}
                )

    for jsonl_path in sorted(jsonl_dir.glob("*.jsonl")):
        with jsonl_path.open("r", encoding="utf-8") as fp:
            for line_no, line in enumerate(fp, start=1):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    issues["jsonl_errors"].append(
                        {"file": str(jsonl_path), "line": line_no, "error": str(exc)}
                    )
                    continue
                output = row.get("output", {})
                missing_output = sorted(REQUIRED_OUTPUT_KEYS - output.keys())
                if missing_output:
                    issues["jsonl_errors"].append(
                        {
                            "file": str(jsonl_path),
                            "line": line_no,
                            "error": f"missing output keys: {missing_output}",
                        }
                    )
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DIR / CONFIG["project"]["manifest_name"])
    parser.add_argument("--split", type=Path, default=SPLIT_DIR / CONFIG["project"]["split_name"])
    parser.add_argument("--jsonl-dir", type=Path, default=JSONL_DIR)
    parser.add_argument("--output", type=Path, default=LOG_DIR / CONFIG["project"]["validation_log_name"])
    args = parser.parse_args()

    issues = validate(args.manifest, args.split, args.jsonl_dir)
    write_json(args.output, issues)
    summary = {key: len(value) for key, value in issues.items()}
    print(f"validation summary -> {summary}")


if __name__ == "__main__":
    from utils.io import write_json

    main()
