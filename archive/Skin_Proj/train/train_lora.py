import argparse
import json
import time
from statistics import mean
from pathlib import Path

import torch

from utils.config import CONFIG
from utils.io import merge_json
from utils.modeling import (
    attach_lora,
    get_runtime_model_config,
    load_base_model,
    load_processor,
    resize_image,
)
from utils.paths import JSONL_DIR, LORA_DIR, PROMPTS_DIR


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Qwen3-VL LoRA training skeleton")
    parser.add_argument("--profile")
    parser.add_argument("--model-name")
    parser.add_argument("--train-file", type=Path, default=JSONL_DIR / CONFIG["project"]["train_jsonl_name"])
    parser.add_argument("--val-file", type=Path, default=JSONL_DIR / CONFIG["project"]["val_jsonl_name"])
    parser.add_argument("--train-prompt", type=Path, default=PROMPTS_DIR / "train.txt")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--batch-size", type=int, default=CONFIG["training"]["batch_size"])
    parser.add_argument("--epochs", type=int, default=CONFIG["training"]["epochs"])
    parser.add_argument("--max-steps", type=int, default=CONFIG["training"]["max_steps"])
    parser.add_argument("--learning-rate", type=float, default=CONFIG["training"]["learning_rate"])
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=CONFIG["training"]["gradient_accumulation_steps"],
    )
    parser.add_argument("--num-workers", type=int, default=CONFIG["training"]["num_workers"])
    parser.add_argument("--timeout-seconds", type=int, default=CONFIG["training"]["timeout_seconds"])
    parser.add_argument("--measure-steps", type=int, default=0)
    parser.add_argument("--estimate-eval-samples", type=int, default=0)
    parser.add_argument("--run-one-batch", action="store_true")
    parser.add_argument("--run-small-train", action="store_true")
    parser.add_argument("--smoke-safe", action="store_true")
    return parser


def load_first_sample(jsonl_path: Path) -> dict:
    with jsonl_path.open("r", encoding="utf-8") as fp:
        first_line = fp.readline()
    return json.loads(first_line)


def iterate_jsonl(jsonl_path: Path):
    with jsonl_path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def estimate_eval_seconds(profile: str | None, explicit_samples: int) -> float:
    if explicit_samples > 0:
        sample_count = explicit_samples
    else:
        sample_count = int(CONFIG["evaluation"]["phase05_samples_per_scenario"]) * len(CONFIG["data"]["scenarios"])
    profile_name = profile or CONFIG["runtime"]["default_profile"]
    key = f"estimated_avg_inference_sec_{profile_name}"
    fallback = float(CONFIG["evaluation"].get(key, CONFIG["evaluation"].get("estimated_avg_inference_sec_primary_4b", 3.0)))
    return fallback * sample_count


def build_timeout_recommendation(expected_total_seconds: float, profile: str | None) -> int:
    multiplier = float(CONFIG["execution_policy"]["timeout_multiplier"])
    minimum = int(CONFIG["execution_policy"]["min_timeout_seconds"])
    default_primary = int(CONFIG["execution_policy"]["primary_4b_default_timeout_seconds"])
    recommended = int(expected_total_seconds * multiplier)
    recommended = max(recommended, minimum)
    if (profile or CONFIG["runtime"]["default_profile"]) == "primary_4b":
        recommended = max(recommended, default_primary)
    return recommended


def run_preflight_measurement(
    processor,
    model,
    train_file: Path,
    profile: str | None,
    learning_rate: float,
    gradient_accumulation_steps: int,
    measure_steps: int,
    max_steps: int,
    estimate_eval_samples: int,
    output_dir: Path,
) -> dict:
    device = model.device if hasattr(model, "device") else torch.device("cuda" if torch.cuda.is_available() else "cpu")
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    samples = []
    step_seconds = []
    image_seconds = []
    forward_seconds = []
    backward_seconds = []
    optimizer_seconds = []
    max_memory_mb = 0.0
    measured = 0

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    for sample in iterate_jsonl(train_file):
        if measured >= measure_steps:
            break
        image_started = time.perf_counter()
        batch = build_train_inputs(processor, sample, profile)
        image_seconds.append(time.perf_counter() - image_started)
        batch = {k: v.to(device) if hasattr(v, "to") else v for k, v in batch.items()}
        step_started = time.perf_counter()
        forward_started = time.perf_counter()
        outputs = model(**batch)
        loss = outputs.loss / max(gradient_accumulation_steps, 1)
        forward_seconds.append(time.perf_counter() - forward_started)
        backward_started = time.perf_counter()
        loss.backward()
        backward_seconds.append(time.perf_counter() - backward_started)
        optimizer_started = time.perf_counter()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        optimizer_seconds.append(time.perf_counter() - optimizer_started)
        step_seconds.append(time.perf_counter() - step_started)
        samples.append({"id": sample["id"], "loss": float(loss.item() * max(gradient_accumulation_steps, 1))})
        measured += 1
        if torch.cuda.is_available():
            max_memory_mb = max(max_memory_mb, torch.cuda.max_memory_allocated() / (1024 * 1024))

    checkpoint_started = time.perf_counter()
    temp_dir = output_dir.parent / f"{output_dir.name}_estimate_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(temp_dir)
    processor.save_pretrained(temp_dir)
    checkpoint_seconds = time.perf_counter() - checkpoint_started

    estimated_training_seconds = mean(step_seconds) * float(max_steps) if step_seconds else 0.0
    estimated_eval_seconds = estimate_eval_seconds(profile, estimate_eval_samples)
    safety_buffer_seconds = checkpoint_seconds + 300.0
    total_estimated_seconds = estimated_training_seconds + checkpoint_seconds + estimated_eval_seconds + safety_buffer_seconds
    recommended_timeout_seconds = build_timeout_recommendation(total_estimated_seconds, profile)

    return {
        "profile": profile or CONFIG["runtime"]["default_profile"],
        "batch_size": CONFIG["training"]["batch_size"],
        "max_steps": max_steps,
        "measure_steps": measured,
        "sample_losses": samples,
        "avg_step_seconds": mean(step_seconds) if step_seconds else 0.0,
        "avg_image_load_seconds": mean(image_seconds) if image_seconds else 0.0,
        "avg_forward_seconds": mean(forward_seconds) if forward_seconds else 0.0,
        "avg_backward_seconds": mean(backward_seconds) if backward_seconds else 0.0,
        "avg_optimizer_seconds": mean(optimizer_seconds) if optimizer_seconds else 0.0,
        "checkpoint_save_seconds": checkpoint_seconds,
        "estimated_eval_seconds": estimated_eval_seconds,
        "safety_buffer_seconds": safety_buffer_seconds,
        "total_estimated_seconds": total_estimated_seconds,
        "recommended_timeout_seconds": recommended_timeout_seconds,
        "gpu_peak_memory_mb": max_memory_mb,
        "checkpoint_probe_dir": str(temp_dir),
    }


def find_subsequence(sequence: list[int], target: list[int]) -> int:
    if not target or len(target) > len(sequence):
        return -1
    for idx in range(len(sequence) - len(target) + 1):
        if sequence[idx : idx + len(target)] == target:
            return idx
    return -1


def build_assistant_only_labels(processor, input_ids: torch.Tensor, assistant_text: str) -> torch.Tensor:
    labels = torch.full_like(input_ids, -100)
    assistant_ids = processor.tokenizer.encode(assistant_text, add_special_tokens=False)
    token_list = input_ids[0].tolist()
    assistant_start = find_subsequence(token_list, assistant_ids)
    if assistant_start < 0:
        raise RuntimeError("Assistant JSON token span not found in input_ids")
    assistant_end = assistant_start + len(assistant_ids)
    labels[0, assistant_start:assistant_end] = input_ids[0, assistant_start:assistant_end]
    return labels


def build_train_inputs(processor, sample: dict, profile: str | None = None) -> dict:
    from PIL import Image

    image = Image.open(sample["image"]).convert("RGB")
    image = resize_image(image, profile)
    assistant_text = json.dumps(sample["output"], ensure_ascii=False)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": sample["instruction"]},
            ],
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": assistant_text}],
        },
    ]
    chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    batch = processor(
        text=[chat_text],
        images=[image],
        return_tensors="pt",
        padding=True,
    )
    batch["labels"] = build_assistant_only_labels(processor, batch["input_ids"], assistant_text)
    return batch


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    profile = args.profile or ("smoke_safe_2b" if args.smoke_safe else None)
    model_cfg = get_runtime_model_config(profile)
    if not bool(model_cfg.get("allow_lora_training", True)):
        raise RuntimeError(f"LoRA training disabled for profile: {profile or CONFIG['runtime']['default_profile']}")
    model_name = args.model_name or model_cfg["model_name"]
    output_dir = args.output_dir or (LORA_DIR / model_cfg["lora_output_dir"])
    smoke_log_path = Path(CONFIG["logging"]["smoke_test_json"])

    processor = load_processor(profile)
    print("processor_loaded", flush=True)
    model = load_base_model(profile)
    print("base_model_loaded", flush=True)
    model = attach_lora(model, profile)
    print("lora_attached", flush=True)
    model.train()

    print("Qwen3-VL LoRA training", flush=True)
    print(f"model={model_name}", flush=True)
    print(f"profile={profile or 'default'}", flush=True)
    print(f"train_file={args.train_file}", flush=True)
    print(f"val_file={args.val_file}", flush=True)
    print(f"output_dir={output_dir}", flush=True)
    print(
        (
            f"batch_size={args.batch_size}, epochs={args.epochs}, max_steps={args.max_steps}, "
            f"lr={args.learning_rate}, grad_accum={args.gradient_accumulation_steps}, "
            f"num_workers={args.num_workers}, timeout_seconds={args.timeout_seconds}"
        ),
        flush=True,
    )

    if not args.run_one_batch and not args.run_small_train and args.measure_steps <= 0:
        print("Model and LoRA adapter loaded successfully.", flush=True)
        print(
            "Use --run-one-batch to run forward/loss/backward/optimizer/checkpoint smoke test.",
            flush=True,
        )
        print(
            "Use --run-small-train to run a bounded small-run LoRA training loop.",
            flush=True,
        )
        return

    log_payload = {
        "train_profile": profile or CONFIG["runtime"]["default_profile"],
        "train_model_name": model_name,
        "train_precision": model_cfg["precision"],
        "train_device_map": model_cfg["device_map"],
        "train_max_image_size": model_cfg["max_image_size"],
        "train_generation_max_new_tokens": model_cfg["generation_max_new_tokens"],
        "train_local_files_only": model_cfg["local_files_only"],
    }
    device = model.device if hasattr(model, "device") else torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log_payload["train_device"] = str(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    print("optimizer_ready", flush=True)

    if args.measure_steps > 0:
        measurement = run_preflight_measurement(
            processor=processor,
            model=model,
            train_file=args.train_file,
            profile=profile,
            learning_rate=args.learning_rate,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            measure_steps=args.measure_steps,
            max_steps=args.max_steps,
            estimate_eval_samples=args.estimate_eval_samples,
            output_dir=output_dir,
        )
        print("preflight_estimate_ready", flush=True)
        print(f"profile={measurement['profile']}", flush=True)
        print(f"batch_size={measurement['batch_size']}", flush=True)
        print(f"max_steps={measurement['max_steps']}", flush=True)
        print(f"avg_step_seconds={measurement['avg_step_seconds']:.4f}", flush=True)
        print(f"avg_image_load_seconds={measurement['avg_image_load_seconds']:.4f}", flush=True)
        print(f"avg_forward_seconds={measurement['avg_forward_seconds']:.4f}", flush=True)
        print(f"avg_backward_seconds={measurement['avg_backward_seconds']:.4f}", flush=True)
        print(f"avg_optimizer_seconds={measurement['avg_optimizer_seconds']:.4f}", flush=True)
        print(f"checkpoint_save_seconds={measurement['checkpoint_save_seconds']:.4f}", flush=True)
        print(f"estimated_eval_seconds={measurement['estimated_eval_seconds']:.4f}", flush=True)
        print(f"total_estimated_seconds={measurement['total_estimated_seconds']:.4f}", flush=True)
        print(f"recommended_timeout_seconds={measurement['recommended_timeout_seconds']}", flush=True)
        print(f"gpu_peak_memory_mb={measurement['gpu_peak_memory_mb']:.2f}", flush=True)
        log_payload["preflight_estimate"] = measurement
        merge_json(smoke_log_path, log_payload)
        if not args.run_one_batch and not args.run_small_train:
            return

    if args.run_one_batch:
        sample = load_first_sample(args.train_file)
        print(f"sample_loaded={sample['id']}", flush=True)
        log_payload["train_sample_id"] = sample["id"]
        batch = build_train_inputs(processor, sample, profile)
        print("train_inputs_built", flush=True)
        batch = {k: v.to(device) if hasattr(v, "to") else v for k, v in batch.items()}
        print(f"batch_moved_to_device={device}", flush=True)

        outputs = model(**batch)
        loss = outputs.loss
        print(f"loss={loss.item():.6f}", flush=True)
        log_payload["train_loss"] = float(loss.item())
        loss.backward()
        print("backward_done", flush=True)
        optimizer.step()
        print("optimizer_step_done", flush=True)
        optimizer.zero_grad(set_to_none=True)

    if args.run_small_train:
        started = time.perf_counter()
        step = 0
        running_losses: list[float] = []
        timed_out = False
        for epoch_idx in range(args.epochs):
            for sample in iterate_jsonl(args.train_file):
                if args.timeout_seconds and (time.perf_counter() - started) >= args.timeout_seconds:
                    timed_out = True
                    print("small_train_timeout_reached", flush=True)
                    break
                if step >= args.max_steps:
                    break
                batch = build_train_inputs(processor, sample, profile)
                batch = {k: v.to(device) if hasattr(v, "to") else v for k, v in batch.items()}
                outputs = model(**batch)
                loss = outputs.loss / max(args.gradient_accumulation_steps, 1)
                running_losses.append(float(loss.item() * max(args.gradient_accumulation_steps, 1)))
                loss.backward()
                step += 1
                if step % max(args.gradient_accumulation_steps, 1) == 0:
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                print(
                    f"small_train_step={step} sample_id={sample['id']} loss={running_losses[-1]:.6f}",
                    flush=True,
                )
            if timed_out or step >= args.max_steps:
                break
        if step % max(args.gradient_accumulation_steps, 1) != 0:
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
        log_payload["small_train_completed_steps"] = step
        log_payload["small_train_timeout_reached"] = timed_out
        if running_losses:
            log_payload["small_train_last_loss"] = running_losses[-1]
            log_payload["small_train_avg_loss"] = sum(running_losses) / len(running_losses)
        print(f"small_train_completed_steps={step}", flush=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)
    print(f"checkpoint_saved={output_dir}", flush=True)
    log_payload["train_checkpoint_saved"] = True
    log_payload["train_checkpoint_dir"] = str(output_dir)
    merge_json(smoke_log_path, log_payload)


if __name__ == "__main__":
    main()
