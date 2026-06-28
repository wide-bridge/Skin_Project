from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
LOCAL_CONFIG_PATH = PROJECT_ROOT / "config" / "config.local.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    target = config_path or CONFIG_PATH
    raw = target.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        config = yaml.safe_load(raw)
        return _merge_local_config(config, yaml)
    except Exception:
        config = _simple_yaml_load(raw)
        return _merge_local_config(config, None)


def _merge_local_config(base: dict[str, Any], yaml_module: Any | None) -> dict[str, Any]:
    if not LOCAL_CONFIG_PATH.exists():
        return base

    local_raw = LOCAL_CONFIG_PATH.read_text(encoding="utf-8")
    if yaml_module is not None:
        local_cfg = yaml_module.safe_load(local_raw)
    else:
        local_cfg = _simple_yaml_load(local_raw)
    return _deep_merge(base, local_cfg)


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    return override


def _simple_yaml_load(raw: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    lines = raw.splitlines()

    for idx, raw_line in enumerate(lines):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]

        if line.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("Invalid YAML structure")
            parent.append(_parse_scalar(line[2:].strip()))
            continue

        if ":" not in line:
            raise ValueError(f"Invalid YAML line: {line}")

        key, remainder = line.split(":", 1)
        key = key.strip()
        remainder = remainder.strip()

        if remainder:
            if not isinstance(parent, dict):
                raise ValueError("Invalid YAML structure")
            parent[key] = _parse_scalar(remainder)
            continue

        next_container: Any = [] if _next_nonempty_is_list(lines, idx) else {}
        if not isinstance(parent, dict):
            raise ValueError("Invalid YAML structure")
        parent[key] = next_container
        stack.append((indent, next_container))

    return root


def _next_nonempty_is_list(lines: list[str], start_idx: int) -> bool:
    for next_idx in range(start_idx + 1, len(lines)):
        stripped = lines[next_idx].strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped.startswith("- ")
    return False


def _parse_scalar(text: str) -> Any:
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


CONFIG = load_config()
