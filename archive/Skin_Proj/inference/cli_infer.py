import argparse
import json
from pathlib import Path

from utils.config import CONFIG
from utils.io import merge_json
from utils.modeling import (
    build_generation_inputs,
    get_generation_max_new_tokens,
    get_runtime_model_config,
    load_base_model,
    load_lora_model,
    load_processor,
)
from utils.output_validation import DEFAULT_OUTPUT, parse_json_payload, validate_output
from utils.paths import LORA_DIR, PROMPTS_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI inference skeleton for Qwen3-VL")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, default=PROMPTS_DIR / "inference.txt")
    parser.add_argument("--profile")
    parser.add_argument("--model-name")
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--use-lora", action="store_true")
    parser.add_argument("--smoke-safe", action="store_true")
    args = parser.parse_args()
    profile = args.profile or ("smoke_safe_2b" if args.smoke_safe else None)
    model_cfg = get_runtime_model_config(profile)
    if args.use_lora and not bool(model_cfg.get("allow_lora_training", True)) and "deferred" in (profile or ""):
        raise RuntimeError(f"LoRA adapter inference not expected for deferred profile: {profile}")
    model_name = args.model_name or model_cfg["model_name"]
    adapter_path = args.adapter_path or (LORA_DIR / model_cfg["lora_output_dir"])
    smoke_log_path = Path(CONFIG["logging"]["smoke_test_json"])

    prompt_text = args.prompt.read_text(encoding="utf-8").strip()
    if args.use_lora and adapter_path.exists():
        processor, model = load_lora_model(adapter_path, profile)
    else:
        processor = load_processor(profile)
        model = load_base_model(profile)

    inputs = build_generation_inputs(processor, args.image, prompt_text, profile)
    device = model.device
    inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}
    generated = model.generate(**inputs, max_new_tokens=get_generation_max_new_tokens(profile))
    text = processor.batch_decode(generated, skip_special_tokens=True)[0]

    print(f"model={model_name}")
    print(f"profile={profile or 'default'}")
    print(f"image={args.image}")
    print(f"prompt={prompt_text}")
    print(text)
    log_payload = {
        "inference_profile": profile or CONFIG["runtime"]["default_profile"],
        "inference_model_name": model_name,
        "inference_image": str(args.image),
    }
    try:
        parsed = parse_json_payload(text)
        is_valid, issues = validate_output(parsed)
        print(json.dumps(parsed, ensure_ascii=False))
        log_payload["inference_output"] = parsed
        log_payload["inference_json_parsed"] = True
        log_payload["inference_valid"] = is_valid
        log_payload["inference_issues"] = issues
    except Exception:
        print(json.dumps(DEFAULT_OUTPUT, ensure_ascii=False))
        log_payload["inference_output"] = DEFAULT_OUTPUT
        log_payload["inference_json_parsed"] = False
        log_payload["inference_valid"] = False
        log_payload["inference_issues"] = ["json_parse_failed"]
    merge_json(smoke_log_path, {f"inference_{args.image.stem}": log_payload})


if __name__ == "__main__":
    main()
