from utils.config import CONFIG


LABEL_REMAP = CONFIG["task"].get("label_remap", {})


def remap_label_value(key: str, value: int) -> int:
    remap = LABEL_REMAP.get(key)
    if not remap:
        return int(value)
    return int(remap.get(int(value), value))
