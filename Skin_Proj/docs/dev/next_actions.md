# Next Actions

## Immediate

1. Treat phase 04 collapse debugging as complete.
2. Keep 5-level remapping for the current two targets.
3. Run phase 05 as a lazy active learning loop, not as immediate long training.
4. Use `lora_checkpoint_4b` as the main quality-improvement target.
5. Keep `primary_4b` as a base-model baseline and `quantized_4b` as comparison only.

## Phase 04 Results Locked In

1. `all-zero collapse` is no longer present.
2. `single-value collapse` is not observed in the current 30-sample check.
3. `lora_checkpoint_4b exact_match_rate` is `0.10`.
4. The failure mode has changed from collapse to low accuracy.

## Phase 04 Root-Cause Interpretation

1. Prompt bias and missing assistant-only loss mask were real root causes.
2. Those two fixes changed model behavior and removed the original collapse pattern.
3. JSONL output injection and raw data linkage are no longer the first explanation for the current failure mode.

## Next Technical Goal

1. Improve LoRA training quality through lazy active-learning evidence.
2. Keep candidate queues before expanding LoRA steps.
3. Recheck train-time supervision quality on more than smoke-level steps only after lazy gate approval.
4. Prepare the next quantitative evaluation around accuracy improvement and candidate-pattern stability.

## Immediate Next Check

1. Review the 15-sample lazy eval queue:
   - trusted `2`
   - uncertain `11`
   - hard `2`
   - invalid `0`
2. Check whether uncertain / hard samples concentrate by scenario, view, target, or label boundary.
3. Do not move directly to 3-step training unless the lazy gate is satisfied.
4. If more evidence is needed, expand candidate collection first before expanding training.
5. Use quantitative evaluation and candidate-pattern stability, not collapse symptoms, as the next gating signal.

## Phase 05 Lazy Gate

Proceed to 3-step training only if:

1. JSON parsing / key / label range remain stable.
2. Exact match or target-level match improves beyond the baseline.
3. Prediction distribution does not collapse.
4. Candidate buckets are interpretable.
5. Trusted samples are sufficient to confirm at least some reliable behavior.

Hold training expansion if:

1. Improvement is too small for the sample size.
2. Most samples are uncertain without a clear pattern.
3. Hard samples need data, label, or prompt inspection first.
4. The GPU-time cost is not justified by the evidence.

## If quantized_4b Fails

1. Save failure cause in local eval summary.
2. Continue phase 03 with `primary_4b`.
3. Do not mark phase 03 failed only because `quantized_4b` failed.

## Phase 04 Guardrail

- Do not revert to collapse debugging unless a new constant-output symptom reappears.
- Do not treat class remapping alone as a solution to low accuracy.
- Do not overinterpret valid JSON output as quality improvement.
- Use local raw debug/eval logs only as reference; keep GitHub updates summary-only.

## Phase 05 Guardrail

- Do not run long 4B training only because exact match moved from `0.10` to `0.1333`.
- Do not commit `outputs/eval/*` or `outputs/debug/*`.
- Do not put uncertain / hard raw sample lists into GitHub if they expose local paths or raw data.
- Summarize candidate counts and patterns only in `docs/dev`.

## Not in Scope Yet

- ROI crop
- prompt tuning
- data augmentation
- long epoch training
- 8B local LoRA training

## Phase 05 Pause Decision

1. Pause `Skin_Proj` phase 05 here.
2. Do not start additional Qwen3-VL LoRA training in this project until the data/training strategy is reapproved.
3. Treat the current remaining issue as low accuracy, not collapse.
4. If this project is resumed, start from `D:\vibe_coding\codex\Skin_Proj\doc\pm\05_작업지시서_(정확도개선_및_능동학습_적용판단).md`.
5. Recheck reliable-data criteria, ROI strategy, augmentation, freeze/unfreeze, and long-training plan before running new experiments.
6. Move new work to `D:\vibe_coding\codex\Skin_diagnosis_proj` in a new chat.
7. Use `D:\PyProject\skin_talk\skintalk_min` as a reference source only; do not directly commit `.env`, upload images, SQLite DB, or model weights.
