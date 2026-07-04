from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.manifest import build_target_manifest
from src.data.splits import make_loose_split, make_strict_split
from src.training.train import append_metrics_csv, train_experiment
from src.utils.config import ensure_dir, load_config
from src.utils.io import write_text


def load_completed_runs(metrics_path: Path) -> set[tuple[str, str]]:
    completed = set()
    if not metrics_path.exists():
        return completed
    with metrics_path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_id = row.get('run_id')
            split_name = row.get('split_name')
            if run_id and split_name:
                completed.add((run_id, split_name))
    return completed


def write_baseline_summary(path: Path, rows: list[dict]) -> None:
    lines = ['# Forehead Wrinkle Baseline Results', '']
    for row in rows:
        lines.extend([
            f"## {row['run_id']} / {row['split_name']}",
            f"- backbone: {row['backbone']}",
            f"- task_type: {row['task_type']}",
            f"- num_classes: {row['num_classes']}",
            f"- accuracy: {row['accuracy']}",
            f"- tolerance1_accuracy: {row['tolerance1_accuracy']}",
            f"- mae: {row['mae']}",
            f"- confusion_csv: {row['confusion_csv']}",
            '',
        ])
    write_text(path, '\n'.join(lines))


def main(config_path: str):
    config = load_config(config_path)
    outputs_root = Path(config['paths']['outputs_root'])
    reports_dir = ensure_dir(outputs_root / 'reports')
    target_key = config['settings']['target_key']
    metrics_path = outputs_root / 'metrics' / f'metrics_{target_key}.csv'

    manifest_rows = build_target_manifest(config['paths']['image_root'], config['paths']['label_root'], config['settings']['scenarios'], target_key, config['settings'].get('label_remap'))
    split_builders = {
        'loose': make_loose_split(manifest_rows, config['settings']['seed'], config['settings']['split_ratio']),
        'strict': make_strict_split(manifest_rows, config['settings']['seed'], config['settings']['split_ratio']),
    }

    completed_runs = load_completed_runs(metrics_path)
    new_rows = []
    for experiment in config['experiments']:
        for split_name, split_rows in split_builders.items():
            run_key = (experiment['run_id'], split_name)
            if run_key in completed_runs:
                continue
            row = train_experiment(config, experiment, split_name, split_rows)
            append_metrics_csv(metrics_path, row)
            new_rows.append(row)

    if new_rows:
        write_baseline_summary(reports_dir / f'baseline_result_{target_key}.md', new_rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    main(args.config)
