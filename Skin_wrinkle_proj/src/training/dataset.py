from __future__ import annotations

from collections import Counter

import torch
from PIL import Image, ImageFilter
from torch.utils.data import Dataset, WeightedRandomSampler
from torchvision import transforms

from src.data.roi import crop_roi


class MaybeSharpness:
    def __init__(self, prob: float = 0.0):
        self.prob = prob

    def __call__(self, image: Image.Image) -> Image.Image:
        import random
        if random.random() < self.prob:
            return image.filter(ImageFilter.SHARPEN)
        return image


class SkinConditionDataset(Dataset):
    def __init__(self, rows: list[dict], image_size: int, use_roi_crop: bool, roi_padding_ratio: float, augment: bool, augmentation_config: dict | None = None, use_precrop: bool = False):
        self.rows = rows
        self.use_roi_crop = use_roi_crop
        self.use_precrop = use_precrop
        self.roi_padding_ratio = roi_padding_ratio
        self.augmentation_config = augmentation_config or {}
        self.transform = self._build_transform(image_size, augment)

    def _build_transform(self, image_size: int, augment: bool):
        ops = []
        if augment:
            cfg = self.augmentation_config
            ops.extend([
                transforms.RandomResizedCrop(
                    image_size,
                    scale=(float(cfg.get('resized_crop_scale_min', 0.92)), float(cfg.get('resized_crop_scale_max', 1.0))),
                    ratio=(float(cfg.get('resized_crop_ratio_min', 0.95)), float(cfg.get('resized_crop_ratio_max', 1.05))),
                ),
                transforms.RandomHorizontalFlip(p=float(cfg.get('horizontal_flip_prob', 0.0))),
                transforms.ColorJitter(
                    brightness=float(cfg.get('brightness', 0.08)),
                    contrast=float(cfg.get('contrast', 0.08)),
                    saturation=float(cfg.get('saturation', 0.05)),
                    hue=float(cfg.get('hue', 0.02)),
                ),
                transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=float(cfg.get('blur_prob', 0.10))),
                transforms.RandomApply([MaybeSharpness(1.0)], p=float(cfg.get('sharpness_prob', 0.10))),
            ])
        else:
            ops.append(transforms.Resize((image_size, image_size)))
        ops.extend([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        return transforms.Compose(ops)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index: int):
        row = self.rows[index]
        if self.use_precrop and row.get('precrop_available') and row.get('precrop_path'):
            image = Image.open(row['precrop_path']).convert('RGB')
        elif self.use_roi_crop and row['roi_available']:
            image = crop_roi(row['image_path'], row['bbox'], self.roi_padding_ratio)
        else:
            image = Image.open(row['image_path']).convert('RGB')
        return {
            'image': self.transform(image),
            'target': int(row['target_value']),
            'person_key': row['person_key'],
            'image_path': row['image_path'],
        }


def build_weighted_sampler(rows: list[dict]) -> WeightedRandomSampler:
    counts = Counter(int(row['target_value']) for row in rows)
    weights = [1.0 / counts[int(row['target_value'])] for row in rows]
    return WeightedRandomSampler(weights=torch.DoubleTensor(weights), num_samples=len(rows), replacement=True)


ForeheadWrinkleDataset = SkinConditionDataset
