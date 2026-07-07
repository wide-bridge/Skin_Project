from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from PIL import Image
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForMultimodalLM, AutoProcessor, BitsAndBytesConfig

from utils.config import CONFIG
from utils.env import load_env_file
from utils.paths import EXTERNAL_ENV_PATH


def resolve_torch_dtype(name: str) -> torch.dtype:
    lowered = name.lower()
    if lowered in {"float16", "fp16"}:
        return torch.float16
    if lowered in {"bfloat16", "bf16"}:
        return torch.bfloat16
    return torch.float32


def get_runtime_model_config(profile: str | None = None) -> dict[str, Any]:
    profile_name = profile or CONFIG["runtime"]["default_profile"]
    profiles = CONFIG["model_profiles"]
    if profile_name not in profiles:
        raise KeyError(f"Unknown model profile: {profile_name}")
    return dict(profiles[profile_name])


def resolve_device_map(value: Any, device: str | None = None) -> Any:
    if value == "single_gpu":
        return {"": device or "cuda"}
    if value in {"none", None, ""}:
        return None
    return value


def load_processor(profile: str | None = None) -> Any:
    model_cfg = get_runtime_model_config(profile)
    env_values = load_env_file(EXTERNAL_ENV_PATH)
    token = env_values.get("HF_TOKEN")
    return AutoProcessor.from_pretrained(
        model_cfg["processor_name"],
        token=token,
        trust_remote_code=bool(model_cfg.get("trust_remote_code", False)),
        local_files_only=bool(model_cfg.get("local_files_only", False)),
    )


def load_base_model(profile: str | None = None) -> Any:
    model_cfg = get_runtime_model_config(profile)
    env_values = load_env_file(EXTERNAL_ENV_PATH)
    token = env_values.get("HF_TOKEN")
    dtype = resolve_torch_dtype(model_cfg["precision"])
    quantization = model_cfg.get("quantization")
    quantization_config = None
    if quantization == "4bit":
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    elif quantization == "8bit":
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    return AutoModelForMultimodalLM.from_pretrained(
        model_cfg["model_name"],
        token=token,
        dtype=dtype,
        device_map=resolve_device_map(model_cfg.get("device_map"), model_cfg.get("device")),
        trust_remote_code=bool(model_cfg.get("trust_remote_code", False)),
        local_files_only=bool(model_cfg.get("local_files_only", False)),
        low_cpu_mem_usage=bool(model_cfg.get("low_cpu_mem_usage", True)),
        quantization_config=quantization_config,
    )


def attach_lora(model: Any, profile: str | None = None) -> Any:
    model_cfg = get_runtime_model_config(profile)
    lora_cfg = LoraConfig(
        r=int(model_cfg["lora_r"]),
        lora_alpha=int(model_cfg["lora_alpha"]),
        lora_dropout=float(model_cfg["lora_dropout"]),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=model_cfg["target_modules"],
    )
    return get_peft_model(model, lora_cfg)


def load_lora_model(adapter_path: Path, profile: str | None = None) -> tuple[Any, Any]:
    processor = load_processor(profile)
    model = load_base_model(profile)
    model = PeftModel.from_pretrained(model, adapter_path)
    return processor, model


def build_generation_inputs(processor: Any, image_path: Path, prompt_text: str, profile: str | None = None) -> dict[str, Any]:
    image = Image.open(image_path).convert("RGB")
    image = resize_image(image, profile)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(
        text=[text],
        images=[image],
        return_tensors="pt",
        padding=True,
    )
    return inputs


def resize_image(image: Image.Image, profile: str | None = None) -> Image.Image:
    model_cfg = get_runtime_model_config(profile)
    max_size = int(model_cfg["max_image_size"])
    width, height = image.size
    longest = max(width, height)
    if longest <= max_size:
        return image
    scale = max_size / float(longest)
    new_size = (int(width * scale), int(height * scale))
    return image.resize(new_size)


def get_generation_max_new_tokens(profile: str | None = None) -> int:
    model_cfg = get_runtime_model_config(profile)
    return int(model_cfg.get("generation_max_new_tokens", 64))
