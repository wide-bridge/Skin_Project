from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


def classification_accuracy(y_true, y_pred) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float((y_true == y_pred).mean()) if len(y_true) else 0.0


def tolerance_accuracy(y_true, y_pred, tolerance: int = 1) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float((np.abs(y_true - y_pred) <= tolerance).mean()) if len(y_true) else 0.0


def mean_absolute_error(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.abs(y_true - y_pred).mean()) if len(y_true) else 0.0


def confusion_matrix(y_true, y_pred, num_classes: int = 5):
    matrix = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        matrix[int(t), int(p)] += 1
    return matrix


def save_confusion_csv(path: str | Path, matrix) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['true\\pred'] + [str(i) for i in range(matrix.shape[1])])
        for idx, row in enumerate(matrix):
            writer.writerow([idx] + row.tolist())
