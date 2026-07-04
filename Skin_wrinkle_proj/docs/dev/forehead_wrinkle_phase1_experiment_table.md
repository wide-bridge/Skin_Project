# Forehead Wrinkle Phase-1 Experiment Table

## Objective
Answer the minimum approved questions without expanding target scope.

## Core Metrics
- accuracy
- tolerance-1 accuracy
- MAE
- confusion matrix
- loose vs strict delta

## Approved Baseline Runs
| Run ID | Backbone | Head Type | Split Modes | Freeze Strategy | Augmentation | Purpose |
|---|---|---|---|---|---|---|
| FW-01 | EfficientNet-B0 | classification | loose + strict | lazy unfreeze | weak-plus | CNN classification baseline |
| FW-02 | EfficientNet-B0 | regression | loose + strict | lazy unfreeze | weak-plus | Ordered severity as continuous score |
| FW-03 | Swin-T | ordinal | loose + strict | lazy unfreeze | weak-plus | Transformer ordinal baseline |

## Lazy Fine-Tuning Principle
- Keep the backbone mostly frozen through the warmup window
- Unfreeze the last stage only after the head has stabilized
- Delay full-backbone unfreeze so early stopping does not kill the run before transfer can happen
- Use a longer patience window because the schedule is intentionally slow
- Keep the epoch cap at 50

## Augmentation Principle
- weak resized crop jitter
- weak horizontal flip
- weak brightness/contrast jitter
- weak color jitter
- slight blur/sharpness variation
- no heavy geometry distortion

## Review Gate
Move beyond `forehead_wrinkle` only after PM review of:
- data validation report
- baseline metric table
- loose vs strict gap
- confusion trends
