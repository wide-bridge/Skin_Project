# Lazy Training Strategy

## Intent
This phase uses a lazy unfreeze schedule.
The point is not to rush full-backbone fine-tuning, but to let the head stabilize first and only then expand trainable capacity.

## Schedule
- Epoch 0 to 9: head-only or near head-only training
- Epoch 10 to 19: unfreeze the last backbone stage
- Epoch 20 onward: unfreeze the full backbone only if validation still benefits

## Early Stopping Policy
- epoch cap: 50
- patience: 15
- rationale: allow the model to survive the delayed unfreeze schedule instead of stopping before the backbone has meaningfully adapted

## Windows Runtime Policy
- environment: `skin_vlm`
- device: `cuda`
- `num_workers: 0`
- keep the run stable rather than aggressively parallel

## Transfer-Learning Policy
- EfficientNet-B0 uses local pretrained weights when they are already cached
- Swin-T uses pretrained weights only if a local cache exists; otherwise it falls back to random init without blocking on download
