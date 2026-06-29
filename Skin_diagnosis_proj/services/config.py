from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "config.template.yaml"


class DatasetConfig(BaseModel):
    derma_ai_root: str
    processed_dir: str = "data/processed"
    test_per_class_view: int = 20


class VLMConfig(BaseModel):
    model_id: str
    adapter_path: str | None = None
    device: str = "cuda"
    torch_dtype: str = "float16"
    max_new_tokens: int = 256
    do_sample: bool = False
    train_max_samples: int = 2
    train_max_steps: int = 1


class BaselineConfig(BaseModel):
    backbone: str = "resnet18"
    image_size: int = 384
    batch_size: int = 8
    epochs: int = 1
    learning_rate: float = 3e-4
    num_workers: int = 0
    train_max_samples: int = 96
    val_max_samples: int = 24


class PromptConfig(BaseModel):
    diagnosis_system: str


class AppConfig(BaseModel):
    name: str
    env: str = "local"


class Settings(BaseModel):
    app: AppConfig
    datasets: DatasetConfig
    vlm: VLMConfig
    baseline: BaselineConfig
    prompts: PromptConfig


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)
    return Settings.model_validate(raw)
