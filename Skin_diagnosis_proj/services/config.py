from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from scripts._utf8 import read_yaml_utf8


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "config.template.yaml"


class DatasetConfig(BaseModel):
    derma_ai_root: str
    qna_training_root: str | None = None
    processed_dir: str = "data/processed"
    test_per_class_view: int = 20


class VLMConfig(BaseModel):
    model_id: str
    adapter_path: str | None = None
    resume_adapter_strategy: str = "latest"
    resume_optimizer_state: bool = True
    reset_patience_on_resume: bool = True
    device: str = "cuda"
    torch_dtype: str = "float16"
    use_qlora: bool = False
    load_in_4bit: bool = False
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    max_new_tokens: int = 256
    do_sample: bool = False
    train_max_samples: int = 0
    val_max_samples: int = 0
    train_max_steps: int = 0
    epochs: int = 1
    batch_size: int = 1
    gradient_accumulation_steps: int = 4
    learning_rate: float = 1e-4
    log_every_steps: int = 10
    early_stopping_patience: int = 2


class BaselineConfig(BaseModel):
    backbone: str = "resnet18"
    image_size: int = 384
    batch_size: int = 8
    epochs: int = 1
    learning_rate: float = 3e-4
    num_workers: int = 0
    train_max_samples: int = 0
    val_max_samples: int = 0
    early_stopping_patience: int = 8
    human_review_confidence_threshold: float = 0.8


class RAGConfig(BaseModel):
    retrieval_top_k: int = 3
    derma_corpus_path: str = "data/processed/rag_corpus_derma.jsonl"
    plastic_corpus_path: str = "data/processed/rag_corpus_plastic.jsonl"
    alias_mapping_path: str = "config/rag_aliases.json"
    default_guidance_terms: list[str] = [
        "피부건조증",
        "피부염",
        "여드름",
        "아토피성 피부염",
        "건선",
    ]


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
    rag: RAGConfig
    prompts: PromptConfig


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    raw: dict[str, Any] = read_yaml_utf8(CONFIG_PATH)
    return Settings.model_validate(raw)
