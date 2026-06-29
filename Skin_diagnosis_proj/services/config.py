from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "config.template.yaml"


class VLMConfig(BaseModel):
    model_id: str
    adapter_path: str | None = None
    device: str = "cuda"
    torch_dtype: str = "float16"
    max_new_tokens: int = 256
    do_sample: bool = False


class PromptConfig(BaseModel):
    diagnosis_system: str


class AppConfig(BaseModel):
    name: str
    env: str = "local"


class Settings(BaseModel):
    app: AppConfig
    vlm: VLMConfig
    prompts: PromptConfig


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)
    return Settings.model_validate(raw)

