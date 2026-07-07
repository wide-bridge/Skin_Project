import argparse
import json
import time
from collections import Counter
from pathlib import Path

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
from utils.paths import LORA_DIR, MANIFEST_DIR, PROMPTS_DIR


def load_manifest(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_rows(manifest: list[dict], scenarios: list[str], samples_per_scenario: int) -> list[dict]:
    selected: list[dict] = []
    for scenario in scenarios:
        rows = [row for row in manifest if row["scenario"] == scenario]
        seen: set[str] = set()
        count = 0
        for row in rows:
            person_id = row["person_id"]
            if person_id in seen:
                continue
            selected.append(row)
            seen.add(person_id)
            count += 1
            if count >= samples_per_scenario:
                break
    return selected


def build_ground_truth(row: dict) -> dict:
    return {
        "forehead_wrinkle": int(row["forehead_wrinkle"]),
        "forehead_pigmentation": int(row["forehead_pigmentation"]),
    }


def exact_match(prediction: dict, truth: dict) -> bool:
    return all(prediction.get(key) == truth.get(key) for key in truth)


def classify_active_learning_sample(result: dict) -> dict:
    if not result["json_parsed"] or not result["key_match"] or not result["valid"]:
        return {
            "bucket": "invalid",
            "reason": "invalid_output_format",
            "target_errors": {},
            "wrong_targets": [],
            "total_abs_error": None,
            "confidence_proxy": 0.0,
            "priority": 4,
        }

    target_errors = {
        key: abs(int(result["prediction"].get(key)) - int(result["ground_truth"][key]))
        for key in DEFAULT_OUTPUT.keys()
    }
    wrong_targets = [key for key, error in target_errors.items() if error != 0]
    total_abs_error = sum(target_errors.values())

    if not wrong_targets:
        bucket = "trusted"
        reason = "all_targets_match"
        priority = 0
    elif len(wrong_targets) == 1 and total_abs_error <= 1:
        bucket = "uncertain"
        reason = "single_target_near_miss"
        priority = 2
    else:
        bucket = "hard"
        reason = "multi_target_or_large_error"
        priority = 3

    return {
        "bucket": bucket,
        "reason": reason,
        "target_errors": target_errors,
        "wrong_targets": wrong_targets,
        "total_abs_error": total_abs_error,
        "confidence_proxy": round(1.0 / (1.0 + total_abs_error), 4),
        "priority": priority,
    }


def target_summary(results: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for key in DEFAULT_OUTPUT.keys():
        truth_counter = Counter(item["ground_truth"][key] for item in results)
        pred_counter = Counter(item["prediction"].get(key) for item in results)
        matches = sum(1 for item in results if item["prediction"].get(key) == item["ground_truth"][key])
        summary[key] = {
            "match_rate": matches / len(results) if results else 0.0,
            "ground_truth_distribution": dict(sorted(truth_counter.items())),
            "prediction_distribution": dict(sorted(pred_counter.items(), key=lambda kv: str(kv[0]))),
            "always_zero_prediction": sum(pred_counter.values()) == pred_counter.get(0, 0),
        }
    return summary


def recommend_active_learning_action(bucket_counter: Counter, total: int) -> str:
    if total == 0:
        return "no_samples_evaluated"
    invalid_rate = bucket_counter.get("invalid", 0) / total
    trusted_rate = bucket_counter.get("trusted", 0) / total
    uncertain_rate = bucket_counter.get("uncertain", 0) / total
    hard_rate = bucket_counter.get("hard", 0) / total
    if invalid_rate > 0:
        return "fix_output_format_before_active_learning"
    if trusted_rate >= 0.3 and uncertain_rate >= 0.3 and hard_rate <= 0.3:
        return "lazy_gate_passed_expand_to_3_steps"
    if uncertain_rate >= 0.5 and trusted_rate > 0:
        return "lazy_collect_more_candidates_before_training_expansion"
    if hard_rate >= 0.5:
        return "inspect_hard_samples_before_more_training"
    return "lazy_hold_training_and_continue_candidate_tracking"


def active_learning_summary(results: list[dict]) -> dict:
    bucket_counter = Counter(item["active_learning"]["bucket"] for item in results)
    scenario_buckets: dict[str, dict] = {}
    for scenario in sorted({item["scenario"] for item in results}):
        scenario_rows = [item for item in results if item["scenario"] == scenario]
        scenario_buckets[scenario] = dict(
            sorted(Counter(item["active_learning"]["bucket"] for item in scenario_rows).items())
        )

    valid_rows = [item for item in results if item["active_learning"]["total_abs_error"] is not None]
    target_errors = {}
    for key in DEFAULT_OUTPUT.keys():
        errors = [item["active_learning"]["target_errors"][key] for item in valid_rows]
        target_errors[key] = {
            "avg_abs_error": sum(errors) / len(errors) if errors else 0.0,
            "max_abs_error": max(errors) if errors else 0,
            "error_distribution": dict(sorted(Counter(errors).items())),
        }

    def candidate_payload(item: dict) -> dict:
        return {
            "id": item["id"],
            "scenario": item["scenario"],
            "view": item["view"],
            "ground_truth": item["ground_truth"],
            "prediction": item["prediction"],
            "target_errors": item["active_learning"]["target_errors"],
            "reason": item["active_learning"]["reason"],
            "confidence_proxy": item["active_learning"]["confidence_proxy"],
        }

    uncertain = [
        candidate_payload(item)
        for item in results
        if item["active_learning"]["bucket"] == "uncertain"
    ][:10]
    hard = sorted(
        [item for item in results if item["active_learning"]["bucket"] == "hard"],
        key=lambda item: item["active_learning"]["total_abs_error"] or 0,
        reverse=True,
    )

    return {
        "bucket_counts": dict(sorted(bucket_counter.items())),
        "scenario_bucket_counts": scenario_buckets,
        "target_error_summary": target_errors,
        "trusted_count": bucket_counter.get("trusted", 0),
        "uncertain_candidates": uncertain,
        "hard_candidates": [candidate_payload(item) for item in hard[:10]],
        "recommended_next_action": recommend_active_learning_action(bucket_counter, len(results)),
    }


def summarize_metrics(results: list[dict]) -> dict:
    total = len(results)
    parsed = sum(1 for item in results if item["json_parsed"])
    valid = sum(1 for item in results if item["valid"])
    exact = sum(1 for item in results if item["exact_match"])
    key_match = sum(1 for item in results if item["key_match"])
    avg_time = sum(item["elapsed_sec"] for item in results) / total if total else 0.0
    return {
        "count": total,
        "json_parsing_success_rate": parsed / total if total else 0.0,
        "key_exact_match_rate": key_match / total if total else 0.0,
        "label_range_valid_rate": valid / total if total else 0.0,
        "exact_match_rate": exact / total if total else 0.0,
        "avg_inference_sec": avg_time,
    }


def scenario_summary(results: list[dict]) -> dict:
    scenarios = sorted({item["scenario"] for item in results})
    return {
        scenario: {
            "metrics": summarize_metrics([item for item in results if item["scenario"] == scenario]),
            "targets": target_summary([item for item in results if item["scenario"] == scenario]),
        }
        for scenario in scenarios
    }


def manifest_target_distribution(rows: list[dict]) -> dict:
    return {
        key: dict(sorted(Counter(int(row[key]) for row in rows).items()))
        for key in DEFAULT_OUTPUT.keys()
    }


def infer_analysis(results: list[dict], all_rows: list[dict], prompt_text: str) -> dict:
    target_stats = target_summary(results)
    full_distribution = manifest_target_distribution(all_rows)
    prompt_minimal_json = "json" in prompt_text.lower() and "{" in prompt_text and "}" in prompt_text
    analysis = {
        "always_zero_prediction_targets": [key for key, stat in target_stats.items() if stat["always_zero_prediction"]],
        "selected_target_summary": target_stats,
        "full_manifest_target_distribution": full_distribution,
        "prompt_is_json_only_style": prompt_minimal_json,
        "likely_causes": [],
    }
    if analysis["always_zero_prediction_targets"]:
        analysis["likely_causes"].append("model_outputs_collapsed_to_zero")
    if any(any(int(label) != 0 for label in dist.keys()) for dist in full_distribution.values()):
        analysis["likely_causes"].append("ground_truth_distribution_is_not_all_zero")
    if prompt_minimal_json:
        analysis["likely_causes"].append("prompt_is_structural_not_descriptive")
    analysis["likely_causes"].append("lora_training_is_likely_insufficient_for_accuracy")
    return analysis


def evaluate_profile(profile: str, rows: list[dict], all_rows: list[dict], prompt_text: str, use_lora: bool) -> dict:
    adapter_path = LORA_DIR / CONFIG["model_profiles"][profile]["lora_output_dir"]
    if use_lora and adapter_path.exists():
        processor, model = load_lora_model(adapter_path, profile)
    else:
        processor = load_processor(profile)
        model = load_base_model(profile)

    results: list[dict] = []
    for row in rows:
        truth = build_ground_truth(row)
        started = time.perf_counter()
        inputs = build_generation_inputs(processor, Path(row["image_path"]), prompt_text, profile)
        device = model.device
        inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}
        generated = model.generate(**inputs, max_new_tokens=get_generation_max_new_tokens(profile))
        elapsed = time.perf_counter() - started
        text = processor.batch_decode(generated, skip_special_tokens=True)[0]

        payload = DEFAULT_OUTPUT
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
            "exact_match": exact_match(payload, truth) if parsed and valid else False,
            "elapsed_sec": round(elapsed, 4),
        }
        result["active_learning"] = classify_active_learning_sample(result)
        results.append(result)
    return {
        "profile": profile,
        "metrics": summarize_metrics(results),
        "scenario_metrics": scenario_summary(results),
        "target_metrics": target_summary(results),
        "active_learning": active_learning_summary(results),
        "analysis": infer_analysis(results, all_rows, prompt_text),
        "results": results,
    }


def build_markdown(summary: dict) -> str:
    lines = [
        "# Phase 03 Eval Summary",
        "",
        f"- run_profile: {summary['primary_profile']}",
        f"- compare_profile: {summary.get('compare_profile') or 'none'}",
        f"- samples_per_scenario: {summary['samples_per_scenario']}",
        f"- total_samples: {summary['total_samples']}",
        "",
        "## Primary Metrics",
    ]
    metrics = summary["primary"]["metrics"]
    target_metrics = summary["primary"]["target_metrics"]
    lines.extend(
        [
            f"- count: {metrics['count']}",
            f"- json_parsing_success_rate: {metrics['json_parsing_success_rate']:.4f}",
            f"- key_exact_match_rate: {metrics['key_exact_match_rate']:.4f}",
            f"- label_range_valid_rate: {metrics['label_range_valid_rate']:.4f}",
            f"- exact_match_rate: {metrics['exact_match_rate']:.4f}",
            f"- avg_inference_sec: {metrics['avg_inference_sec']:.4f}",
            "",
            "## Scenario Metrics",
        ]
    )
    for scenario, scenario_metrics in summary["primary"]["scenario_metrics"].items():
        scenario_targets = scenario_metrics["targets"]
        scenario_metric_values = scenario_metrics["metrics"]
        lines.extend(
            [
                f"### {scenario}",
                f"- count: {scenario_metric_values['count']}",
                f"- json_parsing_success_rate: {scenario_metric_values['json_parsing_success_rate']:.4f}",
                f"- key_exact_match_rate: {scenario_metric_values['key_exact_match_rate']:.4f}",
                f"- label_range_valid_rate: {scenario_metric_values['label_range_valid_rate']:.4f}",
                f"- exact_match_rate: {scenario_metric_values['exact_match_rate']:.4f}",
                f"- avg_inference_sec: {scenario_metric_values['avg_inference_sec']:.4f}",
                f"- forehead_wrinkle_match_rate: {scenario_targets['forehead_wrinkle']['match_rate']:.4f}",
                f"- forehead_pigmentation_match_rate: {scenario_targets['forehead_pigmentation']['match_rate']:.4f}",
                "",
            ]
        )
    lines.extend(
        [
            "## Primary Target Metrics",
            f"- forehead_wrinkle_match_rate: {target_metrics['forehead_wrinkle']['match_rate']:.4f}",
            f"- forehead_wrinkle_truth_distribution: {target_metrics['forehead_wrinkle']['ground_truth_distribution']}",
            f"- forehead_wrinkle_prediction_distribution: {target_metrics['forehead_wrinkle']['prediction_distribution']}",
            f"- forehead_pigmentation_match_rate: {target_metrics['forehead_pigmentation']['match_rate']:.4f}",
            f"- forehead_pigmentation_truth_distribution: {target_metrics['forehead_pigmentation']['ground_truth_distribution']}",
            f"- forehead_pigmentation_prediction_distribution: {target_metrics['forehead_pigmentation']['prediction_distribution']}",
            "",
            "## Primary Analysis",
            f"- always_zero_prediction_targets: {summary['primary']['analysis']['always_zero_prediction_targets']}",
            f"- likely_causes: {summary['primary']['analysis']['likely_causes']}",
            "",
            "## Active Learning Summary",
            f"- bucket_counts: {summary['primary']['active_learning']['bucket_counts']}",
            f"- scenario_bucket_counts: {summary['primary']['active_learning']['scenario_bucket_counts']}",
            f"- recommended_next_action: {summary['primary']['active_learning']['recommended_next_action']}",
            f"- uncertain_candidate_count: {len(summary['primary']['active_learning']['uncertain_candidates'])}",
            f"- hard_candidate_count: {len(summary['primary']['active_learning']['hard_candidates'])}",
            "",
        ]
    )
    compare = summary.get("compare")
    if compare is not None:
        if "error" in compare:
            lines.extend(
                [
                    "## Compare Profile Result",
                    f"- profile: {compare['profile']}",
                    f"- status: failed",
                    f"- error: {compare['error']}",
                    "",
                ]
            )
        else:
            compare_metrics = compare["metrics"]
            compare_targets = compare["target_metrics"]
            lines.extend(
                [
                    "## Compare Profile Result",
                    f"- profile: {compare['profile']}",
                    f"- status: success",
                    f"- count: {compare_metrics['count']}",
                    f"- json_parsing_success_rate: {compare_metrics['json_parsing_success_rate']:.4f}",
                    f"- key_exact_match_rate: {compare_metrics['key_exact_match_rate']:.4f}",
                    f"- label_range_valid_rate: {compare_metrics['label_range_valid_rate']:.4f}",
                    f"- exact_match_rate: {compare_metrics['exact_match_rate']:.4f}",
                    f"- avg_inference_sec: {compare_metrics['avg_inference_sec']:.4f}",
                    f"- forehead_wrinkle_match_rate: {compare_targets['forehead_wrinkle']['match_rate']:.4f}",
                    f"- forehead_pigmentation_match_rate: {compare_targets['forehead_pigmentation']['match_rate']:.4f}",
                    f"- always_zero_prediction_targets: {compare['analysis']['always_zero_prediction_targets']}",
                    "",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch evaluation for phase 03")
    parser.add_argument("--profile", default="primary_4b")
    parser.add_argument("--compare-profile", default="quantized_4b")
    parser.add_argument("--samples-per-scenario", type=int, default=10)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DIR / CONFIG["project"]["manifest_name"])
    parser.add_argument("--prompt", type=Path, default=PROMPTS_DIR / "inference.txt")
    parser.add_argument("--no-lora", action="store_true")
    parser.add_argument("--skip-compare", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    rows = select_rows(manifest, list(CONFIG["data"]["scenarios"]), args.samples_per_scenario)
    prompt_text = args.prompt.read_text(encoding="utf-8").strip()
    use_lora = not args.no_lora

    primary = evaluate_profile(args.profile, rows, manifest, prompt_text, use_lora)
    compare = None
    if not args.skip_compare:
        try:
            compare = evaluate_profile(args.compare_profile, rows, manifest, prompt_text, use_lora)
        except Exception as exc:
            compare = {"profile": args.compare_profile, "error": str(exc)}

    summary = {
        "primary_profile": args.profile,
        "compare_profile": None if args.skip_compare else args.compare_profile,
        "samples_per_scenario": args.samples_per_scenario,
        "total_samples": len(rows),
        "primary": primary,
        "compare": compare,
    }

    json_path = Path(CONFIG["logging"]["eval_summary_json"])
    md_path = Path(CONFIG["logging"]["eval_summary_md"])
    write_json(json_path, summary)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(build_markdown(summary), encoding="utf-8")

    print(f"primary_profile={args.profile}")
    print(f"compare_profile={args.compare_profile if not args.skip_compare else 'skipped'}")
    print(f"total_samples={len(rows)}")
    print(f"summary_json={json_path}")
    print(f"summary_md={md_path}")


if __name__ == "__main__":
    main()
