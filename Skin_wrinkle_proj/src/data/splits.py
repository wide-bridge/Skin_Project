from __future__ import annotations

import random
from collections import Counter, defaultdict


def _slice_counts(total: int, train_ratio: float, val_ratio: float) -> tuple[int, int, int]:
    train_n = int(total * train_ratio)
    val_n = int(total * val_ratio)
    test_n = total - train_n - val_n
    return train_n, val_n, test_n


def make_loose_split(rows: list[dict], seed: int, split_ratio: dict[str, float]) -> dict[str, list[dict]]:
    rng = random.Random(seed)
    items = list(rows)
    rng.shuffle(items)
    train_n, val_n, test_n = _slice_counts(len(items), split_ratio['train'], split_ratio['val'])
    return {'train': items[:train_n], 'val': items[train_n: train_n + val_n], 'test': items[train_n + val_n:]}


def make_strict_split(rows: list[dict], seed: int, split_ratio: dict[str, float]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['person_key']].append(row)
    keys = list(grouped.keys())
    rng = random.Random(seed)
    rng.shuffle(keys)
    train_n, val_n, test_n = _slice_counts(len(keys), split_ratio['train'], split_ratio['val'])
    train_keys = set(keys[:train_n])
    val_keys = set(keys[train_n: train_n + val_n])
    test_keys = set(keys[train_n + val_n:])
    splits = {'train': [], 'val': [], 'test': []}
    for key, items in grouped.items():
        if key in train_keys:
            splits['train'].extend(items)
        elif key in val_keys:
            splits['val'].extend(items)
        elif key in test_keys:
            splits['test'].extend(items)
    return splits


def split_label_distribution(split_rows: dict[str, list[dict]]) -> list[dict]:
    summary = []
    for split_name, rows in split_rows.items():
        counter = Counter(row['target_value'] for row in rows)
        total = len(rows)
        for label in sorted(counter):
            summary.append({'split': split_name, 'label': label, 'count': counter[label], 'ratio': round(counter[label] / total, 6) if total else 0.0})
    return summary


def leakage_report(split_rows: dict[str, list[dict]]) -> dict:
    person_sets = {name: {row['person_key'] for row in rows} for name, rows in split_rows.items()}
    image_sets = {name: {row['image_path'] for row in rows} for name, rows in split_rows.items()}
    return {
        'person_overlap_train_val': sorted(person_sets['train'] & person_sets['val']),
        'person_overlap_train_test': sorted(person_sets['train'] & person_sets['test']),
        'person_overlap_val_test': sorted(person_sets['val'] & person_sets['test']),
        'image_overlap_train_val': sorted(image_sets['train'] & image_sets['val']),
        'image_overlap_train_test': sorted(image_sets['train'] & image_sets['test']),
        'image_overlap_val_test': sorted(image_sets['val'] & image_sets['test']),
    }
