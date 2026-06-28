import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path

from inference.batch_eval import build_ground_truth, classify_active_learning_sample
from utils.config import CONFIG
from utils.io import write_json
from utils.modeling import (
    build_generation_inputs,
    get_generation_max_new_tokens,
    load_base_model,
    load_lora_model,
    load_processor,
)
from utils.output_validation import DEFAULT_OUTPUT, parse_json_payload, validate_output
from utils.paths import LORA_DIR, MANIFEST_DIR, OUTPUTS_DIR, PROMPTS_DIR


TARGETS = ["forehead_wrinkle", "forehead_pigmentation"]


def load_manifest(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def target_key(target: str, cls: int) -> str:
    return f"{target}:{cls}"


def build_balanced_scan_order(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for row in rows:
        for target in TARGETS:
            grouped[(target, row["scenario"], int(row[target]))].append(row)

    ordered: list[dict] = []
    seen_ids: set[str] = set()
    scenarios = list(CONFIG["data"]["scenarios"])
    max_len = max((len(items) for items in grouped.values()), default=0)
    for idx in range(max_len):
        for target in TARGETS:
            for cls in range(5):
                for scenario in scenarios:
                    items = grouped.get((target, scenario, cls), [])
                    if idx >= len(items):
                        continue
                    row = items[idx]
                    row_id = row["id"]
                    if row_id in seen_ids:
                        continue
                    ordered.append(row)
                    seen_ids.add(row_id)
    return ordered


def pool_counts(pool: dict[str, list[dict]]) -> dict[str, dict]:
    counts = {}
    for target in TARGETS:
        counts[target] = {}
        for cls in range(5):
            key = target_key(target, cls)
            scenario_counts = defaultdict(int)
            for item in pool[key]:
                scenario_counts[item["scenario"]] += 1
            counts[target][str(cls)] = {
                "count": len(pool[key]),
                "scenario_counts": dict(sorted(scenario_counts.items())),
            }
    return counts


def is_goal_met(pool: dict[str, list[dict]], per_class_goal: int) -> bool:
    return all(len(pool[target_key(target, cls)]) >= per_class_goal for target in TARGETS for cls in range(5))


def can_add_for_scenario(pool: dict[str, list[dict]], target: str, cls: int, scenario: str, per_class_goal: int) -> bool:
    key = target_key(target, cls)
    if len(pool[key]) >= per_class_goal:
        return False
    soft_cap = math.ceil(per_class_goal / len(CONFIG["data"]["scenarios"]))
    scenario_count = sum(1 for item in pool[key] if item["scenario"] == scenario)
    if scenario_count < soft_cap:
        return True
    # Allow over-cap only when the other scenarios are not producing enough reliable samples.
    return len(pool[key]) >= per_class_goal - 1


def evaluate_row(processor, model, row: dict, prompt_text: str, profile: str) -> dict:
    truth = build_ground_truth(row)
    started = time.perf_counter()
    inputs = build_generation_inputs(processor, Path(row["image_path"]), prompt_text, profile)
    device = model.device
    inputs = {key: value.to(device) if hasattr(value, "to") else value for key, value in inputs.items()}
    generated = model.generate(**inputs, max_new_tokens=get_generation_max_new_tokens(profile))
    elapsed = time.perf_counter() - started
    text = processor.batch_decode(generated, skip_special_tokens=True)[0]

    payload = dict(DEFAULT_OUTPUT)
    parsed = False
    try:
        payload = parse_json_payload(text)
        parsed = True
    except Exception:
        payload = dict(DEFAULT_OUTPUT)

    valid, issues = validate_output(payload)
    key_match = sorted(payload.keys()) == sorted(DEFAULT_OUTPUT.keys())
    result = {
        "id": row["id"],
        "person_id": row["person_id"],
        "scenario": row["scenario"],
        "view": row["view"],
        "image_path": row["image_path"],
        "ground_truth": truth,
        "prediction": payload,
        "json_parsed": parsed,
        "valid": valid,
        "issues": issues,
        "key_match": key_match,
        "elapsed_sec": round(elapsed, 4),
    }
    result["active_learning"] = classify_active_learning_sample(
        {
            **result,
            "exact_match": all(payload.get(key) == truth.get(key) for key in truth) if parsed and valid else False,
        }
    )
    return result


def build_summary(profile: str, evaluated: list[dict], pool: dict[str, list[dict]], per_class_goal: int) -> dict:
    return {
        "profile": profile,
        "per_class_goal": per_class_goal,
        "evaluated_count": len(evaluated),
        "reliable_rule": "valid_json_and_prediction_equals_ground_truth_for_target_class",
        "goal_met": is_goal_met(pool, per_class_goal),
        "pool_counts": pool_counts(pool),
        "pool": pool,
    }


def build_markdown(summary: dict) -> str:
    lines = [
        "# Phase 05 Reliable Pool Summary",
        "",
        f"- profile: {summary['profile']}",
        f"- per_class_goal: {summary['per_class_goal']}",
        f"- evaluated_count: {summary['evaluated_count']}",
        f"- reliable_rule: {summary['reliable_rule']}",
        f"- goal_met: {summary['goal_met']}",
        "",
    ]
    for target, classes in summary["pool_counts"].items():
        lines.append(f"## {target}")
        for cls, item in classes.items():
            lines.append(
                f"- class {cls}: count={item['count']}, scenario_counts={item['scenario_counts']}"
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect class-balanced reliable samples for phase 05.")
    parser.add_argument("--profile", default="primary_4b")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DIR / CONFIG["project"]["manifest_name"])
    parser.add_argument("--prompt", type=Path, default=PROMPTS_DIR / "inference.txt")
    parser.add_argument("--per-class-goal", type=int, default=10)
    parser.add_argument("--max-eval", type=int, default=0, help="0 means scan all candidates.")
    parser.add_argument("--no-lora", action="store_true")
    args = parser.parse_args()

    rows = build_balanced_scan_order(load_manifest(args.manifest))
    if args.max_eval > 0:
        rows = rows[: args.max_eval]

    adapter_path = LORA_DIR / CONFIG["model_profiles"][args.profile]["lora_output_dir"]
    if not args.no_lora and adapter_path.exists():
        processor, model = load_lora_model(adapter_path, args.profile)
    else:
        processor = load_processor(args.profile)
        model = load_base_model(args.profile)

    prompt_text = args.prompt.read_text(encoding="utf-8").strip()
    pool: dict[str, list[dict]] = defaultdict(list)
    evaluated: list[dict] = []
    started = time.perf_counter()

    for index, row in enumerate(rows, start=1):
        result = evaluate_row(processor, model, row, prompt_text, args.profile)
        evaluated.append(result)
        if result["json_parsed"] and result["valid"] and result["key_match"]:
            for target in TARGETS:
                cls = int(result["ground_truth"][target])
                if result["prediction"].get(target) == cls and can_add_for_scenario(
                    pool, target, cls, result["scenario"], args.per_class_goal
                ):
                    pool[target_key(target, cls)].append(
                        {
                            "id": result["id"],
                            "person_id": result["person_id"],
                            "scenario": result["scenario"],
                            "view": result["view"],
                            "image_path": result["image_path"],
                            "target": target,
                            "class": cls,
                            "ground_truth": result["ground_truth"],
                            "prediction": result["prediction"],
                            "active_learning": result["active_learning"],
                        }
                    )
        if index % 25 == 0 or is_goal_met(pool, args.per_class_goal):
            elapsed = time.perf_counter() - started
            print(f"evaluated={index} elapsed_sec={elapsed:.1f} goal_met={is_goal_met(pool, args.per_class_goal)}")
            print(json.dumps(pool_counts(pool), ensure_ascii=False))
        if is_goal_met(pool, args.per_class_goal):
            break

    summary = build_summary(args.profile, evaluated, pool, args.per_class_goal)
    out_dir = OUTPUTS_DIR / "eval"
    json_path = out_dir / "phase05_reliable_pool.json"
    md_path = out_dir / "phase05_reliable_pool.md"
    write_json(json_path, summary)
    md_path.write_text(build_markdown(summary), encoding="utf-8")
    print(f"summary_json={json_path}")
    print(f"summary_md={md_path}")
    print(f"goal_met={summary['goal_met']}")


if __name__ == "__main__":
    main()
