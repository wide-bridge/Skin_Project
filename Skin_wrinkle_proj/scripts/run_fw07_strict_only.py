from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.manifest import build_target_manifest
from src.data.splits import make_strict_split
from src.training.train import append_metrics_csv, train_experiment
from src.utils.config import load_config


def main(config_path: str):
    config = load_config(config_path)
    outputs_root = Path(config['paths']['outputs_root'])
    target_key = config['settings']['target_key']
    metrics_path = outputs_root / 'metrics' / f'metrics_{target_key}.csv'
    manifest_rows = build_target_manifest(
        config['paths']['image_root'],
        config['paths']['label_root'],
        config['settings']['scenarios'],
        target_key,
        config['settings'].get('label_remap'),
        config['paths'].get('precrop_root'),
        config['settings'].get('precrop_part'),
    )
    strict_split = make_strict_split(manifest_rows, config['settings']['seed'], config['settings']['split_ratio'])
    experiment = next(exp for exp in config['experiments'] if exp['run_id'] == 'FW-07')
    row = train_experiment(config, experiment, 'strict', strict_split)
    append_metrics_csv(metrics_path, row)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    main(args.config)
