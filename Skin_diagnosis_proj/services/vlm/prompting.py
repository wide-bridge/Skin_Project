from pathlib import Path

from services.config import ROOT_DIR, get_settings


def load_diagnosis_prompt() -> str:
    settings = get_settings()
    prompt_path = ROOT_DIR / settings.prompts.diagnosis_system
    return Path(prompt_path).read_text(encoding="utf-8")

