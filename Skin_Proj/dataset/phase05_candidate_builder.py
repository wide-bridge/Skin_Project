import argparse
import json
from collections import defaultdict
from pathlib import Path

from utils.config import CONFIG
from utils.io import write_json
from utils.paths import OUTPUTS_DIR, SOURCE_IMG_ROOT, SOURCE_LABEL_ROOT


WRINKLE_TARGET_SUFFIXES = {
    "forehead_wrinkle": "01",
    "glabellus_wrinkle": "02",
    "l_perocular_wrinkle": "03",
    "r_perocular_wrinkle": "04",
}

SKIN_DIAGNOSIS_TARGET_SUFFIXES = {
    "forehead_wrinkle": "01",
    "forehead_pigmentation": "01",
    "glabellus_wrinkle": "02",
    "l_perocular_wrinkle": "03",
    "r_perocular_wrinkle": "04",
    "l_cheek_pore": "05",
    "l_cheek_pigmentation": "05",
    "r_cheek_pore": "06",
    "r_cheek_pigmentation": "06",
    "lip_dryness": "07",
    "chin_sagging": "08",
}

TARGET_SETS = {
    "wrinkle": WRINKLE_TARGET_SUFFIXES,
    "skin_diagnosis": SKIN_DIAGNOSIS_TARGET_SUFFIXES,
}
SCENARIOS = tuple(CONFIG["data"]["scenarios"])
CLASSES = tuple(range(5))


def remap_to_five_levels(value: int) -> int:
    return min(int(value), 4)


def read_annotation(label_path: Path) -> dict:
    payload = json.loads(label_path.read_text(encoding="utf-8"))
    return {
        "info": payload.get("info", {}),
        "annotations": payload.get("annotations", {}),
    }


def build_front_rows(target_suffixes: dict[str, str]) -> list[dict]:
    targets = tuple(target_suffixes.keys())
    rows: list[dict] = []
    for scenario in SCENARIOS:
        label_root = SOURCE_LABEL_ROOT / scenario
        img_root = SOURCE_IMG_ROOT / scenario
        if not label_root.exists() or not img_root.exists():
            continue

        for person_dir in sorted(path for path in label_root.iterdir() if path.is_dir()):
            base = f"{person_dir.name}_{scenario}_F"
            label_paths = {
                suffix: person_dir / f"{base}_{suffix}.json"
                for suffix in set(target_suffixes.values())
            }
            if not all(path.exists() for path in label_paths.values()):
                continue

            merged: dict = {}
            source_image_name = None
            for suffix, label_path in label_paths.items():
                payload = read_annotation(label_path)
                info = payload["info"]
                source_image_name = source_image_name or info.get("filename")
                merged.update(payload["annotations"])

            if not source_image_name:
                continue
            image_path = img_root / person_dir.name / source_image_name
            if not image_path.exists():
                continue
            if not all(target in merged and merged[target] is not None for target in targets):
                continue

            row = {
                "id": base,
                "person_id": person_dir.name,
                "scenario": scenario,
                "view": "F",
                "image_path": str(image_path),
                "source_image_name": source_image_name,
            }
            for target in targets:
                row[target] = remap_to_five_levels(int(merged[target]))
                row[f"{target}_label_path"] = str(label_paths[target_suffixes[target]])
            rows.append(row)
    return rows


def select_candidates(rows: list[dict], targets: tuple[str, ...], per_cell_goal: int) -> dict:
    pool = {
        target: {
            str(cls): {scenario: [] for scenario in SCENARIOS}
            for cls in CLASSES
        }
        for target in targets
    }

    for target in TARGETS:
        for cls in CLASSES:
            for scenario in SCENARIOS:
                seen_person: set[str] = set()
                candidates = [
                    row for row in rows
                    if row["scenario"] == scenario and int(row[target]) == cls
                ]
                for row in candidates:
                    if row["person_id"] in seen_person:
                        continue
                    pool[target][str(cls)][scenario].append(
                        {
                            "id": row["id"],
                            "person_id": row["person_id"],
                            "scenario": row["scenario"],
                            "view": row["view"],
                            "image_path": row["image_path"],
                            "target": target,
                            "class": cls,
                            "target_label_path": row[f"{target}_label_path"],
                            "labels": {key: row[key] for key in targets},
                        }
                    )
                    seen_person.add(row["person_id"])
                    if len(pool[target][str(cls)][scenario]) >= per_cell_goal:
                        break
    return pool


def summarize_pool(rows: list[dict], targets: tuple[str, ...], pool: dict, per_cell_goal: int) -> dict:
    targets = {}
    for target in targets:
        targets[target] = {}
        for cls in CLASSES:
            targets[target][str(cls)] = {}
            for scenario in SCENARIOS:
                count = len(pool[target][str(cls)][scenario])
                available = sum(
                    1 for row in rows
                    if row["scenario"] == scenario and int(row[target]) == cls
                )
                targets[target][str(cls)][scenario] = {
                    "selected": count,
                    "available": available,
                    "goal": per_cell_goal,
                    "goal_met": count >= per_cell_goal,
                }
    return targets


def build_markdown(summary: dict) -> str:
    lines = [
        "# Phase 05 Five-Target Class-Balanced Data Candidates",
        "",
        f"- per_cell_goal: {summary['per_cell_goal']}",
        f"- target_count: {len(summary['target_list'])}",
        f"- front_rows: {summary['front_rows']}",
        f"- slot_goal: {summary['slot_goal']}",
        f"- selected_slots: {summary['selected_slots']}",
        f"- unique_image_ids: {summary['unique_image_ids']}",
        "",
    ]
    for target, classes in summary["targets"].items():
        lines.append(f"## {target}")
        for cls, scenarios in classes.items():
            parts = [
                f"{scenario}={item['selected']}/{item['goal']}"
                for scenario, item in scenarios.items()
            ]
            lines.append(f"- class {cls}: " + ", ".join(parts))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build phase 05 class-balanced data candidates.")
    parser.add_argument("--target-set", choices=sorted(TARGET_SETS), default="skin_diagnosis")
    parser.add_argument("--per-cell-goal", type=int, default=3)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    target_suffixes = TARGET_SETS[args.target_set]
    targets = tuple(target_suffixes.keys())
    rows = build_front_rows(target_suffixes)
    pool = select_candidates(rows, targets, args.per_cell_goal)
    selected_items = [
        item
        for target in targets
        for cls in CLASSES
        for scenario in SCENARIOS
        for item in pool[target][str(cls)][scenario]
    ]
    output_json = args.output_json or OUTPUTS_DIR / "eval" / f"phase05_{args.target_set}_class_balanced_candidates.json"
    output_md = args.output_md or OUTPUTS_DIR / "eval" / f"phase05_{args.target_set}_class_balanced_candidates.md"
    summary = {
        "selection_rule": "front_view_valid_paths_merge_target_suffixes_class_scenario_person_unique",
        "target_set": args.target_set,
        "target_list": list(targets),
        "per_cell_goal": args.per_cell_goal,
        "front_rows": len(rows),
        "slot_goal": len(targets) * len(CLASSES) * len(SCENARIOS) * args.per_cell_goal,
        "selected_slots": len(selected_items),
        "unique_image_ids": len({item["id"] for item in selected_items}),
        "targets": summarize_pool(rows, targets, pool, args.per_cell_goal),
        "pool": pool,
    }
    write_json(output_json, summary)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(build_markdown(summary), encoding="utf-8")
    print(f"summary_json={output_json}")
    print(f"summary_md={output_md}")
    print(f"selected_slots={summary['selected_slots']}/{summary['slot_goal']}")
    print(f"unique_image_ids={summary['unique_image_ids']}")


if __name__ == "__main__":
    main()
