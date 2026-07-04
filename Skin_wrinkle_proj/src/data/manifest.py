from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.data.roi import validate_bbox


TARGET_JSON_SUFFIX = {
    'forehead_wrinkle': '01',
    'forehead_pigmentation': '01',
    'glabellus_wrinkle': '02',
    'l_perocular_wrinkle': '03',
    'r_perocular_wrinkle': '04',
    'l_cheek_pore': '05',
    'l_cheek_pigmentation': '05',
    'r_cheek_pore': '06',
    'r_cheek_pigmentation': '06',
    'lip_dryness': '07',
    'chin_sagging': '08',
}


def parse_angle_token(filename: str) -> str:
    parts = filename.replace('.jpg', '').split('_')
    return parts[2] if len(parts) >= 3 else 'UNK'


def infer_target_json_suffix(target_key: str) -> str:
    suffix = TARGET_JSON_SUFFIX.get(target_key)
    if suffix is None:
        raise ValueError(f'Unsupported target_key for manifest build: {target_key}')
    return suffix


def build_target_manifest(
    image_root: str | Path,
    label_root: str | Path,
    scenarios: list[str],
    target_key: str,
    label_remap: dict[int, int] | dict[str, int] | None = None,
    precrop_root: str | Path | None = None,
    precrop_part: str | None = None,
) -> list[dict[str, Any]]:
    image_root = Path(image_root)
    label_root = Path(label_root)
    precrop_root = Path(precrop_root) if precrop_root and precrop_part else None
    normalized_remap = None
    if label_remap is not None:
        normalized_remap = {int(k): int(v) for k, v in label_remap.items()}
    target_suffix = infer_target_json_suffix(target_key)
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_label_dir = label_root / scenario
        if not scenario_label_dir.exists():
            continue
        for subject_dir in sorted(p for p in scenario_label_dir.iterdir() if p.is_dir()):
            for json_path in sorted(subject_dir.glob(f'*_{target_suffix}.json')):
                with json_path.open('r', encoding='utf-8') as f:
                    payload = json.load(f)
                info = payload.get('info', {})
                images = payload.get('images', {})
                annotations = payload.get('annotations', {})
                filename = info.get('filename')
                bbox = images.get('bbox')
                width = int(images.get('width', 0) or 0)
                height = int(images.get('height', 0) or 0)
                raw_label_value = annotations.get(target_key)
                if filename is None or raw_label_value is None:
                    continue
                raw_label_value = int(raw_label_value)
                mapped_label = normalized_remap.get(raw_label_value, raw_label_value) if normalized_remap else raw_label_value
                image_path = image_root / scenario / subject_dir.name / filename
                subject_id = str(info.get('id', subject_dir.name))
                roi_available = image_path.exists() and validate_bbox(bbox, width, height)
                precrop_path = None
                precrop_available = False
                if precrop_root is not None and precrop_part:
                    candidate_dir = precrop_root / precrop_part / scenario / subject_dir.name
                    preferred = candidate_dir / filename
                    fallback = candidate_dir / f'{json_path.stem}.jpg'
                    candidate = preferred if preferred.exists() else fallback
                    precrop_path = str(candidate)
                    precrop_available = candidate.exists()
                rows.append({
                    'scenario': scenario,
                    'subject_id': subject_id,
                    'person_key': f'{scenario}:{subject_id}',
                    'image_filename': filename,
                    'image_path': str(image_path),
                    'label_path': str(json_path),
                    'raw_target_value': raw_label_value,
                    'target_value': int(mapped_label),
                    'bbox': bbox,
                    'roi_available': bool(roi_available),
                    'precrop_path': precrop_path,
                    'precrop_available': bool(precrop_available),
                    'angle_token': parse_angle_token(filename),
                    'width': width,
                    'height': height,
                })
    return rows


def build_forehead_manifest(
    image_root: str | Path,
    label_root: str | Path,
    scenarios: list[str],
    target_key: str,
    label_remap: dict[int, int] | dict[str, int] | None = None,
    precrop_root: str | Path | None = None,
    precrop_part: str | None = None,
) -> list[dict[str, Any]]:
    return build_target_manifest(
        image_root=image_root,
        label_root=label_root,
        scenarios=scenarios,
        target_key=target_key,
        label_remap=label_remap,
        precrop_root=precrop_root,
        precrop_part=precrop_part,
    )
