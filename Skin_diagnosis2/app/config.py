import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = Path(r"D:/PyProject/env_keys/.env")

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def first_existing_path(*paths: Path) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path
    return None


PROJECT_DIR = BASE_DIR
MODEL_PATH = first_existing_path(
    PROJECT_DIR / "models" / "best_efficientnet_b3_skin_diagnosis.pt",
    PROJECT_DIR / "best_efficientnet_b3_skin_diagnosis.pt",
)

OPENAI_MODEL = "gpt-4o-mini"

MAKEUP_TRAIN_DIR = Path(r"D:/ai_hub_data/02.문제성 피부 메이크업 추천 데이터/3.개방데이터/1.데이터/Training/2.라벨링데이터")
MAKEUP_VALID_DIR = Path(r"D:/ai_hub_data/02.문제성 피부 메이크업 추천 데이터/3.개방데이터/1.데이터/Validation/2.라벨링데이터")
DERM_TRAIN_DIR = Path(r"D:/ai_hub_data/08.전문 의학지식 데이터/3.개방데이터/1.데이터/Training/02.라벨링데이터/TL_피부과")

IMAGE_SIZE = 300
UNCERTAIN_CONFIDENCE_THRESHOLD = 0.65
UNCERTAIN_MARGIN_THRESHOLD = 0.15

DEFAULT_CLASSES = ["건선", "아토피", "여드름", "정상", "주사", "지루"]
