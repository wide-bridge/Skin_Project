# Skin_wrinkle_proj Development Outline

## Project Scope
- Project theme: facial wrinkle analysis
- Current phase: `forehead_wrinkle` single-target baseline validation only
- Explicitly out of scope for this phase:
  - `glabellus_wrinkle`
  - `l_perocular_wrinkle`, `r_perocular_wrinkle`
  - all-target expansion
  - UI or service work
  - broad hyperparameter search

## Implementation Principle
- Keep `Skin_Project` as the mono-repo root.
- Keep original dataset outside the repo.
- Build executable validation and baseline training code only for the approved 01 scope.
- Compare `loose split` and `strict split` first.
- Use the smallest model set that can answer the phase-1 questions.

## Source Layout
- `src/data`: manifest building, ROI handling, split generation
- `src/training`: datasets, models, losses, training loop
- `src/evaluation`: metrics and confusion matrix export
- `src/utils`: config and path helpers
- `configs`: reproducible config templates
- `scripts`: runnable entrypoints

## Phase-1 Decision Questions
1. Is `forehead_wrinkle` learnable with the current dataset structure?
2. Does `strict split` materially underperform `loose split`?
3. Is `classification`, `regression`, or `ordinal` the more stable formulation?
4. Is `EfficientNet` or `Swin-T` the better baseline axis for the next review?
