import json
import re

from utils.config import CONFIG

DEFAULT_OUTPUT = CONFIG["task"]["output_schema"]
LABEL_RANGES = CONFIG["task"]["label_ranges"]


def parse_json_payload(text: str) -> dict:
    candidate = text.strip()
    if "```json" in candidate:
        candidate = candidate.split("```json", 1)[1]
        candidate = candidate.split("```", 1)[0]
    elif "```" in candidate:
        candidate = candidate.split("```", 1)[1]
        candidate = candidate.split("```", 1)[0]
    candidate = candidate.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        matches = re.findall(r"\{[^{}]*\}", candidate)
        if not matches:
            raise
        return json.loads(matches[-1])


def validate_output(payload: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if sorted(payload.keys()) != sorted(DEFAULT_OUTPUT.keys()):
        issues.append("key_mismatch")
    for key, schema in LABEL_RANGES.items():
        value = payload.get(key)
        if not isinstance(value, int):
            issues.append(f"{key}_not_int")
            continue
        if value < int(schema["min"]) or value > int(schema["max"]):
            issues.append(f"{key}_out_of_range")
    return len(issues) == 0, issues
