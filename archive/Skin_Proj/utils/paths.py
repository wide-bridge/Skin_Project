from pathlib import Path
from utils.config import CONFIG

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_IMG_ROOT = Path(CONFIG["data"]["source_img_root"])
SOURCE_LABEL_ROOT = Path(CONFIG["data"]["source_label_root"])
EXTERNAL_ENV_PATH = Path(CONFIG["data"]["external_env_path"])

DATASET_DIR = PROJECT_ROOT / "dataset"
MANIFEST_DIR = DATASET_DIR / "manifests"
SPLIT_DIR = DATASET_DIR / "splits"
JSONL_DIR = DATASET_DIR / "jsonl"
LOG_DIR = DATASET_DIR / "logs"

PROMPTS_DIR = PROJECT_ROOT / "prompts"
TRAIN_DIR = PROJECT_ROOT / "train"
INFERENCE_DIR = PROJECT_ROOT / "inference"
MODELS_DIR = PROJECT_ROOT / "models"
LORA_DIR = PROJECT_ROOT / "lora"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CONFIG_DIR = PROJECT_ROOT / "config"
