from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
from PIL import Image
from peft import LoraConfig, get_peft_model
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _common import processed_dir
from services.config import get_settings


def build_prompt(row: dict) -> str:
    disease_ko = row["metadata"].get("source_label", "??")
    return (
        "? ?? ???? ?? ??? ???? JSON??? ????. "
        "?? ??? ??, ??? ???, ???, ??, ??, ??? ??????. "
        f"?? ??: {disease_ko}"
    )


def main() -> None:
    settings = get_settings()
    dataset_path = processed_dir() / "vlm_train_dataset.jsonl"
    rows = [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines()[: settings.vlm.train_max_samples]]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if settings.vlm.torch_dtype == "float16" and device.type == "cuda" else torch.float32

    processor = AutoProcessor.from_pretrained(settings.vlm.model_id, trust_remote_code=True)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        settings.vlm.model_id,
        trust_remote_code=True,
        torch_dtype=dtype,
    )
    model.to(device)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.train()

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    last_loss = None
    for row in rows[: settings.vlm.train_max_steps]:
        image = Image.open(row["image"]).convert("RGB")
        prompt = build_prompt(row)
        target = row["messages"][-1]["content"]

        prompt_messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ],
        }]
        full_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": target}],
            },
        ]

        prompt_text = processor.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
        full_text = processor.apply_chat_template(full_messages, tokenize=False, add_generation_prompt=False)

        full_inputs = processor(text=[full_text], images=[image], return_tensors="pt", padding=True)
        prompt_inputs = processor(text=[prompt_text], images=[image], return_tensors="pt", padding=True)
        full_inputs = {k: v.to(device) if hasattr(v, 'to') else v for k, v in full_inputs.items()}
        prompt_len = prompt_inputs["input_ids"].shape[1]
        labels = full_inputs["input_ids"].clone()
        labels[:, :prompt_len] = -100

        outputs = model(**full_inputs, labels=labels)
        loss = outputs.loss
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        last_loss = float(loss.item())

    artifact = {
        "model_id": settings.vlm.model_id,
        "device": str(device),
        "dtype": str(dtype),
        "train_rows_used": len(rows),
        "train_steps": settings.vlm.train_max_steps,
        "last_train_loss": last_loss,
        "adapter_trainable_params": sum(p.numel() for p in model.parameters() if p.requires_grad),
    }
    out = processed_dir() / "qwen_lora_train_metrics.json"
    out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    adapter_dir = processed_dir() / "qwen_lora_adapter_preview"
    model.save_pretrained(adapter_dir)
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
    print(f"saved {out}")


if __name__ == "__main__":
    main()


