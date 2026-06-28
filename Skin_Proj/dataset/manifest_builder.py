import argparse
import json
from pathlib import Path

from utils.config import CONFIG
from utils.io import write_json
from utils.labels import remap_label_value
from utils.paths import MANIFEST_DIR, SOURCE_IMG_ROOT, SOURCE_LABEL_ROOT

TARGET_LABEL_FILE_SUFFIX = "_01.json"
TARGET_KEYS = tuple(CONFIG["task"]["target_keys"])
SCENARIOS = tuple(CONFIG["data"]["scenarios"])


def build_manifest() -> list[dict]:
    rows: list[dict] = []
    for scenario in SCENARIOS:
        label_root = SOURCE_LABEL_ROOT / scenario
        img_root = SOURCE_IMG_ROOT / scenario
        if not label_root.exists() or not img_root.exists():
            continue

        for person_dir in sorted(p for p in label_root.iterdir() if p.is_dir() and p.name != ".ipynb_checkpoints"):
            for label_path in sorted(person_dir.glob(f"*{TARGET_LABEL_FILE_SUFFIX}")):
                if label_path.name.endswith("-checkpoint.json"):
                    continue

                payload = json.loads(label_path.read_text(encoding="utf-8"))
                info = payload.get("info", {})
                image_name = info.get("filename")
                image_path = img_root / person_dir.name / image_name
                ann = payload.get("annotations", {})

                if not all(key in ann for key in TARGET_KEYS):
                    continue

                view = _extract_view(label_path.stem, scenario)
                rows.append(
                    {
                        "id": f"{person_dir.name}_{scenario}_{view}",
                        "person_id": str(info.get("id", person_dir.name)),
                        "scenario": scenario,
                        "view": view,
                        "image_path": str(image_path),
                        "label_path": str(label_path),
                        "source_image_name": image_name,
                        "forehead_wrinkle": remap_label_value("forehead_wrinkle", int(ann["forehead_wrinkle"])),
                        "forehead_pigmentation": remap_label_value("forehead_pigmentation", int(ann["forehead_pigmentation"])),
                    }
                )
    return rows


def _extract_view(stem: str, scenario: str) -> str:
    token = f"_{scenario}_"
    if token not in stem:
        return "UNKNOWN"
    tail = stem.split(token, 1)[1]
    return tail.rsplit("_", 1)[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=MANIFEST_DIR / CONFIG["project"]["manifest_name"],
    )
    args = parser.parse_args()

    manifest = build_manifest()
    write_json(args.output, manifest)
    print(f"manifest rows={len(manifest)} -> {args.output}")


if __name__ == "__main__":
    main()
