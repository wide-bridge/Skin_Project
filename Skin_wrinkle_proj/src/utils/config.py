import copy
import os
from pathlib import Path

import yaml


def _expand_env_values(value):
    if isinstance(value, dict):
        return {k: _expand_env_values(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env_values(v) for v in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def load_config(path: str | Path) -> dict:
    config_path = Path(path)
    with config_path.open('r', encoding='utf-8') as f:
        return _expand_env_values(yaml.safe_load(f))


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def deep_copy_config(config: dict) -> dict:
    return copy.deepcopy(config)
