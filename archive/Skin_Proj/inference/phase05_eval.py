import argparse
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from utils.modeling import (
    build_generation_inputs,
    get_generation_max_new_tokens,
    load_base_model,
    load_lora_model,
    load_processor,
)
from utils.paths import OUTPUTS_DIR, PROMPTS_DIR


TARGETS = [
    "forehead_wrinkle",
    "forehead_pigmentation",
    "glabellus_wrinkle",
    "l_cheek_pigmentation",
    "r_cheek_pigmentation",
]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_json_payload(text: str) -> dict:
    candidate = text.strip()
    if "```json" in candidate:
        candidate = candidate.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in candidate:
        candidate = candidate.split("```", 1)[1].split("```", 1)[0]
    candidate = candidate.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.rfind("{")
        end = candidate.rfind("}")
        if start < 0 or end < start:
            raise
        return json.loads(candidate[start : end + 1])


def validate_payload(payload: dict) -> tuple[bool, list[str]]:
    issues = []
    if sorted(payload.keys()) != sorted(TARGETS):
        issues.append("key_mismatch")
    for target in TARGETS:
        value = payload.get(target)
        if not isinstance(value, int):
            issues.append(f"{target}_not_int")
            continue
        if value < 0 or value > 4:
            issues.append(f"{target}_out_of_range")
    return not issues, issues


def classify_result(result: dict) -> dict:
    if not result["json_parsed"] or not result["valid"]:
        return {"bucket": "invalid", "total_abs_error": None, "wrong_targets": TARGETS}
    target_errors = {
        target: abs(int(result["prediction"].get(target)) - int(result["ground_truth"][target]))
        for target in TARGETS
    }
    wrong_targets = [target for target, error in target_errors.items() if error != 0]
    total_abs_error = sum(target_errors.values())
    if not wrong_targets:
        bucket = "trusted"
    elif len(wrong_targets) <= 2 and all(target_errors[target] <= 1 for target in wrong_targets):
        bucket = "uncertain"
    else:
        bucket = "hard"
    return {
        "bucket": bucket,
        "target_errors": target_errors,
        "wrong_targets": wrong_targets,
        "total_abs_error": total_abs_error,
        "confidence_proxy": round(1.0 / (1.0 + total_abs_error), 4),
    }


def evaluate_rows(profile: str, rows: list[dict], prompt_text: str, adapter_dir: Path | None) -> dict:
    if adapter_dir is not None:
        processor, model = load_lora_model(adapter_dir, profile)
    else:
        processor = load_processor(profile)
        model = load_base_model(profile)

    results = []
    for row in rows:
        started = time.perf_counter()
        inputs = build_generation_inputs(processor, Path(row["image"]), prompt_text, profile)
        device = model.device
        inputs = {key: value.to(device) if hasattr(value, "to") else value for key, value in inputs.items()}
        generated = model.generate(**inputs, max_new_tokens=get_generation_max_new_tokens(profile))
        elapsed = time.perf_counter() - started
        text = processor.batch_decode(generated, skip_special_tokens=True)[0]

        payload = {}
        parsed = False
        try:
            payload = parse_json_payload(text)
            parsed = True
        except Exception:
            payload = {}
        valid, issues = validate_payload(payload)
        result = {
            "id": row["id"],
            "person_id": row["person_id"],
            "scenario": row["scenario"],
            "view": row["view"],
            "ground_truth": row["output"],
            "prediction": payload,
            "json_parsed": parsed,
            "valid": valid,
            "issues": issues,
            "elapsed_sec": round(elapsed, 4),
        }
        result["active_learning"] = classify_result(result)
        results.append(result)
    return summarize(results)


def summarize(results: list[dict]) -> dict:
    total = len(results)
    bucket_counts = Counter(item["active_learning"]["bucket"] for item in results)
    target_summary = {}
    for target in TARGETS:
        matches = [
            item for item in results
            if item["valid"] and item["prediction"].get(target) == item["ground_truth"][target]
        ]
        class_counts = defaultdict(lambda: defaultdict(int))
        reliable_counts = defaultdict(lambda: defaultdict(int))
        for item in results:
            cls = int(item["ground_truth"][target])
            scenario = item["scenario"]
            class_counts[str(cls)][scenario] += 1
            if item["valid"] and item["prediction"].get(target) == cls:
                reliable_counts[str(cls)][scenario] += 1
        target_summary[target] = {
            "match_rate": len(matches) / total if total else 0.0,
            "class_scenario_counts": {cls: dict(sorted(values.items())) for cls, values in class_counts.items()},
            "reliable_class_scenario_counts": {
                cls: dict(sorted(values.items())) for cls, values in reliable_counts.items()
            },
        }
    exact = sum(
        1 for item in results
        if item["valid"] and all(item["prediction"].get(target) == item["ground_truth"][target] for target in TARGETS)
    )
    return {
        "count": total,
        "json_parsing_success_rate": sum(1 for item in results if item["json_parsed"]) / total if total else 0.0,
        "valid_rate": sum(1 for item in results if item["valid"]) / total if total else 0.0,
        "exact_match_rate": exact / total if total else 0.0,
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "target_summary": target_summary,
        "avg_inference_sec": sum(item["elapsed_sec"] for item in results) / total if total else 0.0,
        "results": results,
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# Phase 05 Five-Target Eval Summary",
        "",
        f"- profile: {payload['profile']}",
        f"- adapter_dir: {payload.get('adapter_dir') or 'none'}",
        f"- count: {payload['summary']['count']}",
        f"- json_parsing_success_rate: {payload['summary']['json_parsing_success_rate']:.4f}",
        f"- valid_rate: {payload['summary']['valid_rate']:.4f}",
        f"- exact_match_rate: {payload['summary']['exact_match_rate']:.4f}",
        f"- avg_inference_sec: {payload['summary']['avg_inference_sec']:.4f}",
        f"- bucket_counts: {payload['summary']['bucket_counts']}",
        "",
    ]
    for target, summary in payload["summary"]["target_summary"].items():
        lines.append(f"## {target}")
        lines.append(f"- match_rate: {summary['match_rate']:.4f}")
        lines.append(f"- reliable_class_scenario_counts: {summary['reliable_class_scenario_counts']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate phase 05 five-target candidate JSONL.")
    parser.add_argument("--profile", default="primary_4b")
    parser.add_argument("--jsonl", type=Path, default=OUTPUTS_DIR / "eval" / "phase05_5target_train_candidates.jsonl")
    parser.add_argument("--prompt", type=Path, default=PROMPTS_DIR / "phase05_train.txt")
    parser.add_argument("--adapter-dir", type=Path)
    parser.add_argument("--output-json", type=Path, default=OUTPUTS_DIR / "eval" / "phase05_5target_eval_summary.json")
    parser.add_argument("--output-md", type=Path, default=OUTPUTS_DIR / "eval" / "phase05_5target_eval_summary.md")
    args = parser.parse_args()

    payload = {
        "profile": args.profile,
        "adapter_dir": str(args.adapter_dir) if args.adapter_dir else None,
        "jsonl": str(args.jsonl),
        "summary": evaluate_rows(args.profile, load_jsonl(args.jsonl), args.prompt.read_text(encoding="utf-8"), args.adapter_dir),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.output_md.write_text(build_markdown(payload), encoding="utf-8")
    print(f"summary_json={args.output_json}")
    print(f"summary_md={args.output_md}")
    print(f"bucket_counts={payload['summary']['bucket_counts']}")


if __name__ == "__main__":
    main()
