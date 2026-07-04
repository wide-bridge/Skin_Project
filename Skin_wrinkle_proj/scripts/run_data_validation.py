from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.manifest import build_target_manifest
from src.data.splits import leakage_report, make_loose_split, make_strict_split, split_label_distribution
from src.utils.config import ensure_dir, load_config
from src.utils.io import write_csv, write_json, write_text


def format_report(target_key: str, manifest_rows: list[dict], loose_split: dict, strict_split: dict, loose_leakage: dict, strict_leakage: dict) -> str:
    total = len(manifest_rows)
    roi_ok = sum(1 for row in manifest_rows if row['roi_available'])
    raw_label_counts = {}
    mapped_label_counts = {}
    for row in manifest_rows:
        raw_label_counts[row['raw_target_value']] = raw_label_counts.get(row['raw_target_value'], 0) + 1
        mapped_label_counts[row['target_value']] = mapped_label_counts.get(row['target_value'], 0) + 1
    lines = [
        f'# {target_key} Data Validation Report',
        '',
        f'- total_samples: {total}',
        f'- roi_available_samples: {roi_ok}',
        f'- roi_availability_ratio: {roi_ok / total:.4f}' if total else '- roi_availability_ratio: 0.0000',
        f'- unique_person_keys: {len({row["person_key"] for row in manifest_rows})}',
        '',
        '## Raw Label Distribution',
    ]
    for label, count in sorted(raw_label_counts.items()):
        lines.append(f'- raw_label_{label}: {count}')
    lines.extend(['', '## Remapped Label Distribution'])
    for label, count in sorted(mapped_label_counts.items()):
        lines.append(f'- mapped_label_{label}: {count}')
    lines.extend(['', '## Loose Split Counts'])
    for split_name, rows in loose_split.items():
        lines.append(f'- {split_name}: {len(rows)}')
    lines.extend(['', '## Strict Split Counts'])
    for split_name, rows in strict_split.items():
        lines.append(f'- {split_name}: {len(rows)}')
    lines.extend(['', '## Loose Leakage Check'])
    for key, values in loose_leakage.items():
        lines.append(f'- {key}: {len(values)} overlaps')
    lines.extend(['', '## Strict Leakage Check'])
    for key, values in strict_leakage.items():
        lines.append(f'- {key}: {len(values)} overlaps')
    return '\n'.join(lines) + '\n'


def main(config_path: str):
    config = load_config(config_path)
    outputs_root = Path(config['paths']['outputs_root'])
    reports_dir = ensure_dir(outputs_root / 'reports')
    metrics_dir = ensure_dir(outputs_root / 'metrics')

    target_key = config['settings']['target_key']
    manifest_rows = build_target_manifest(config['paths']['image_root'], config['paths']['label_root'], config['settings']['scenarios'], target_key, config['settings'].get('label_remap'))
    loose_split = make_loose_split(manifest_rows, config['settings']['seed'], config['settings']['split_ratio'])
    strict_split = make_strict_split(manifest_rows, config['settings']['seed'], config['settings']['split_ratio'])
    loose_leakage = leakage_report(loose_split)
    strict_leakage = leakage_report(strict_split)
    label_distribution = split_label_distribution(strict_split)

    write_json(reports_dir / 'loose_split.json', loose_split)
    write_json(reports_dir / 'strict_split.json', strict_split)
    write_csv(metrics_dir / f'label_distribution_{target_key}.csv', label_distribution, ['split', 'label', 'count', 'ratio'])
    write_text(reports_dir / f'data_validation_report_{target_key}.md', format_report(target_key, manifest_rows, loose_split, strict_split, loose_leakage, strict_leakage))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    main(args.config)
