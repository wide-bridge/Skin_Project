from __future__ import annotations

import torch
import torch.nn as nn


def build_loss(task_type: str):
    if task_type == 'classification':
        return nn.CrossEntropyLoss()
    if task_type == 'regression':
        return nn.MSELoss()
    if task_type == 'ordinal':
        return nn.BCEWithLogitsLoss()
    raise ValueError(f'Unsupported task type: {task_type}')


def make_ordinal_targets(targets: torch.Tensor, num_classes: int) -> torch.Tensor:
    thresholds = torch.arange(num_classes - 1, device=targets.device).unsqueeze(0)
    return (targets.unsqueeze(1) > thresholds).float()
