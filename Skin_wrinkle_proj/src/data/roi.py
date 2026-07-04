from __future__ import annotations

from pathlib import Path

from PIL import Image


def validate_bbox(bbox: list[int] | tuple[int, int, int, int] | None, width: int, height: int) -> bool:
    if not bbox or len(bbox) != 4:
        return False
    x1, y1, x2, y2 = [int(v) for v in bbox]
    if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
        return False
    if x2 > width or y2 > height:
        return False
    return True


def expand_bbox(bbox: list[int], width: int, height: int, padding_ratio: float) -> list[int]:
    x1, y1, x2, y2 = bbox
    bw = x2 - x1
    bh = y2 - y1
    pad_x = int(bw * padding_ratio)
    pad_y = int(bh * padding_ratio)
    return [
        max(0, x1 - pad_x),
        max(0, y1 - pad_y),
        min(width, x2 + pad_x),
        min(height, y2 + pad_y),
    ]


def crop_roi(image_path: str | Path, bbox: list[int], padding_ratio: float = 0.0) -> Image.Image:
    image = Image.open(Path(image_path)).convert('RGB')
    width, height = image.size
    crop_box = expand_bbox(bbox, width, height, padding_ratio)
    return image.crop(tuple(crop_box))
