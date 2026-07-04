from __future__ import annotations

import warnings
from pathlib import Path

import torch.nn as nn
from torchvision.models import (
    EfficientNet_B0_Weights,
    EfficientNet_V2_S_Weights,
    Swin_T_Weights,
    efficientnet_b0,
    efficientnet_v2_s,
    swin_t,
)


def _torch_cache_dir() -> Path:
    return Path.home() / '.cache' / 'torch' / 'hub' / 'checkpoints'


def _cached_weight_or_none(weight_enum):
    cache_dir = _torch_cache_dir()
    filename = weight_enum.url.rsplit('/', 1)[-1]
    return weight_enum if (cache_dir / filename).exists() else None


class RegressionHead(nn.Module):
    def __init__(self, in_features: int):
        super().__init__()
        self.head = nn.Linear(in_features, 1)

    def forward(self, x):
        return self.head(x).squeeze(1)


class OrdinalHead(nn.Module):
    def __init__(self, in_features: int, num_classes: int):
        super().__init__()
        self.head = nn.Linear(in_features, num_classes - 1)

    def forward(self, x):
        return self.head(x)


class WrappedModel(nn.Module):
    def __init__(self, backbone_name: str, task_type: str, num_classes: int, pretrained: bool = True):
        super().__init__()
        self.backbone_name = backbone_name
        self.task_type = task_type
        self.num_classes = num_classes
        if backbone_name == 'efficientnet_b0':
            weights = _cached_weight_or_none(EfficientNet_B0_Weights.DEFAULT) if pretrained else None
            self.backbone = efficientnet_b0(weights=weights)
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        elif backbone_name == 'efficientnet_v2_s':
            weights = _cached_weight_or_none(EfficientNet_V2_S_Weights.DEFAULT) if pretrained else None
            self.backbone = efficientnet_v2_s(weights=weights)
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        elif backbone_name == 'swin_t':
            weights = _cached_weight_or_none(Swin_T_Weights.DEFAULT) if pretrained else None
            try:
                self.backbone = swin_t(weights=weights)
            except Exception as exc:
                warnings.warn(f'Falling back to random init for swin_t: {exc}')
                self.backbone = swin_t(weights=None)
            in_features = self.backbone.head.in_features
            self.backbone.head = nn.Identity()
        else:
            raise ValueError(f'Unsupported backbone: {backbone_name}')

        if task_type == 'classification':
            self.head = nn.Linear(in_features, num_classes)
        elif task_type == 'regression':
            self.head = RegressionHead(in_features)
        elif task_type == 'ordinal':
            self.head = OrdinalHead(in_features, num_classes)
        else:
            raise ValueError(f'Unsupported task type: {task_type}')

    def forward(self, x):
        return self.head(self.backbone(x))


def _freeze_all(model: WrappedModel):
    for param in model.backbone.parameters():
        param.requires_grad = False


def _unfreeze_all(model: WrappedModel):
    for param in model.backbone.parameters():
        param.requires_grad = True


def _unfreeze_modules(modules):
    for module in modules:
        for param in module.parameters():
            param.requires_grad = True


def _efficientnet_feature_slices(model: WrappedModel, count: int):
    feature_modules = list(model.backbone.features)
    count = max(1, min(count, len(feature_modules)))
    return feature_modules[-count:]


def _unfreeze_last_stage_partial(model: WrappedModel):
    if model.backbone_name in {'efficientnet_b0', 'efficientnet_v2_s'}:
        _unfreeze_modules(_efficientnet_feature_slices(model, 1))
    elif model.backbone_name == 'swin_t' and hasattr(model.backbone, 'features'):
        _unfreeze_modules(list(model.backbone.features)[-1:])
    if hasattr(model.backbone, 'norm'):
        _unfreeze_modules([model.backbone.norm])


def _unfreeze_last_stage(model: WrappedModel):
    if model.backbone_name in {'efficientnet_b0', 'efficientnet_v2_s'}:
        _unfreeze_modules(_efficientnet_feature_slices(model, 2))
    elif model.backbone_name == 'swin_t' and hasattr(model.backbone, 'features'):
        _unfreeze_modules(list(model.backbone.features)[-2:])
    if hasattr(model.backbone, 'norm'):
        _unfreeze_modules([model.backbone.norm])


def _unfreeze_middle_stage(model: WrappedModel):
    if model.backbone_name in {'efficientnet_b0', 'efficientnet_v2_s'}:
        _unfreeze_modules(_efficientnet_feature_slices(model, 4))
    elif model.backbone_name == 'swin_t' and hasattr(model.backbone, 'features'):
        _unfreeze_modules(list(model.backbone.features)[-3:])
    if hasattr(model.backbone, 'norm'):
        _unfreeze_modules([model.backbone.norm])


def apply_lazy_freeze(model: WrappedModel, epoch: int, freeze_config: dict):
    current_epoch = epoch + 1
    _freeze_all(model)
    for param in model.head.parameters():
        param.requires_grad = True

    partial_epoch = int(freeze_config.get('unfreeze_last_stage_partial_epoch', 0) or 0)
    last_stage_epoch = int(freeze_config.get('unfreeze_last_stage_epoch', 10))
    middle_epoch = int(freeze_config.get('unfreeze_middle_stage_epoch', 0) or 0)
    full_epoch = int(freeze_config.get('unfreeze_full_epoch', 20))

    if partial_epoch and current_epoch >= partial_epoch:
        _unfreeze_last_stage_partial(model)
    if current_epoch >= last_stage_epoch:
        _unfreeze_last_stage(model)
    if middle_epoch and current_epoch >= middle_epoch:
        _unfreeze_middle_stage(model)
    if current_epoch >= full_epoch:
        _unfreeze_all(model)
