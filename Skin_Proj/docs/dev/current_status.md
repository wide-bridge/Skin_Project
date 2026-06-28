# Current Status

## Phase Status

- `00` GitHub and workflow setup: complete
- `01` Vision Agent foundation setup: complete
- `02` Qwen3-VL LoRA smoke path: complete
- `03` small-scale quantitative evaluation and profile comparison: complete
- `04` all-zero collapse root-cause removal and LoRA full-training preparation: complete
- `05` accuracy improvement and active-learning applicability: in progress

## 03 Progress Summary

- Added batch evaluation entrypoint:
  - `inference/batch_eval.py`
- Added phase 03 local-only evaluation outputs:
  - `outputs/eval/phase03_eval_summary.json`
  - `outputs/eval/phase03_eval_summary.md`
- Added shared validation helpers:
  - `utils/output_validation.py`
- Added eval summary paths to public config:
  - `config/config.yaml`
  - `config/config.template.yaml`

## Pilot Evaluation Result

- run profile: `primary_4b`
- compare profile: `quantized_4b`
- samples per scenario: `10`
- total samples: `30`

### primary_4b

- JSON parsing success rate: `1.0000`
- key exact match rate: `1.0000`
- label range valid rate: `1.0000`
- exact match rate: `0.0000`
- avg inference sec: `2.6294`
- forehead_wrinkle match rate: `0.1000`
- forehead_pigmentation match rate: `0.1000`

### quantized_4b

- comparison run: success
- JSON parsing success rate: `1.0000`
- key exact match rate: `1.0000`
- label range valid rate: `1.0000`
- exact match rate: `0.0000`
- avg inference sec: `2.2548`
- forehead_wrinkle match rate: `0.1000`
- forehead_pigmentation match rate: `0.1000`

## Interpretation

- The phase 03 evaluation path is now executable on Windows.
- `quantized_4b` is usable as a comparison profile and did not block progress.
- Current weakness is not JSON stability but prediction quality:
  - outputs are structurally valid
  - exact match is still `0.0000` in the 30-sample evaluation
- `primary_4b` predicts `0` for both targets across all 30 samples.
- `quantized_4b` predicts `0` for pigmentation on all 30 samples and predicts wrinkle almost always as `0`.
- Ground truth is not all zero:
  - wrinkle selected-set distribution: `{0: 3, 1: 9, 2: 9, 3: 9}`
  - pigmentation selected-set distribution: `{0: 3, 1: 24, 3: 3}`
- Likely causes:
  - LoRA training is still too shallow for real classification quality
  - prompt is structurally strict but not descriptive
  - current adapter behaves like a collapsed output head rather than a learned grader

## Phase 03 Conclusion

- JSON parsing: pass
- key exact match: pass
- label range validation: pass
- exact match: `0.0000`
- Both targets are effectively collapsed toward prediction `0`.
- 5-level remapping is kept.
- Remapping improved class distribution, but it did not resolve the collapse.
- Phase 03 is closed with `all-zero collapse` confirmed.

## Phase 04_1 Root-Cause Narrowing

- Local debug evidence was saved to:
  - `outputs/debug/phase04_1_root_cause_debug.json`
- Sample-level training-input inspection on the first 3 JSONL rows shows:
  - `labels_equal_input_ids = true`
  - `neg100_count = 0`
  - assistant JSON text is present in the chat template
  - assistant JSON token span is found, but prompt/user tokens are not masked out
- This means the current smoke-training path is not using assistant-only loss masking yet.

## Base / Adapter / Checkpoint Comparison

- Initial 3-sample comparison before the first-pass fix showed:
  - base `primary_4b`
  - smoke adapter `smoke_safe_2b`
  - LoRA checkpoint `qwen3_vl_forehead`
  all following the zero-valued JSON pattern.
- After the first-pass fix:
  - base `primary_4b` no longer stayed on zero values
  - smoke adapter `smoke_safe_2b` produced non-zero and varied values
  - LoRA checkpoint `qwen3_vl_forehead` also moved away from all-zero outputs
- Extended 30-sample verification was saved locally to:
  - `outputs/debug/phase04_constant_output_check.json`
- 30-sample result summary:
  - all-zero collapse is no longer present
  - single-value collapse is also not observed in the current 30-sample check
  - `lora_checkpoint_4b` prediction distributions are now spread across multiple classes

## Phase 04_1 Interim Conclusion

- Root cause was narrowed further and the two strongest structural issues were confirmed:
  - inference prompt bias toward zero-filled JSON
  - missing assistant-only loss mask
- Data connection itself is not the leading cause:
  - image path / label path / image-label matching issues were not the primary failure pattern
  - class remapping alone did not resolve collapse

## Phase 04 First Fix Status

- First two root-cause items were addressed in code:
  - assistant-only loss mask added in `train/train_lora.py`
  - zero-filled inference prompt example removed from `prompts/inference.txt`
- Post-fix verification result:
  - sample-level labels are no longer equal to full `input_ids`
  - `labels=-100` masking now exists outside assistant JSON span
  - base `primary_4b` no longer defaults to all-zero JSON on the checked 3 samples
- This means the two strongest structural causes were real and the first-pass fix changed model behavior.

## Phase 04 Current Conclusion

- `all-zero collapse` is resolved.
- `single-value collapse` is also not observed in the current 30-sample check.
- The issue has shifted from collapse to low accuracy.
- `lora_checkpoint_4b exact_match_rate` is `0.10`.
- The next phase should focus on LoRA training quality improvement and quantitative evaluation rather than collapse debugging.

## Phase 05 Lazy Active Learning Start

- Phase 05 is now framed as a lazy active learning loop.
- The goal is not to immediately increase LoRA steps, but to collect trusted / uncertain / hard / invalid candidates first.
- A 15-sample evaluation was rerun after adding active-learning candidate classification.
- Local-only eval artifact:
  - `outputs/eval/phase03_eval_summary.json`
  - `outputs/eval/phase03_eval_summary.md`
- GitHub policy:
  - raw eval artifacts remain local-only
  - only this summary is reflected in `docs/dev`

## Phase 05 15-Sample Lazy Eval Summary

- profile: `primary_4b`
- samples: scenario별 5장, 총 15장
- JSON parsing success rate: `1.0000`
- key exact match rate: `1.0000`
- label range valid rate: `1.0000`
- exact match rate: `0.1333`
- avg inference sec: `2.5209`
- active-learning buckets:
  - trusted: `2`
  - uncertain: `11`
  - hard: `2`
  - invalid: `0`
- scenario bucket counts:
  - `01`: trusted `2`, uncertain `3`
  - `02`: uncertain `4`, hard `1`
  - `03`: uncertain `4`, hard `1`
- recommended action: `lazy_collect_more_candidates_before_training_expansion`

## Phase 05 Interim Interpretation

- Exact match is slightly above the prior `0.10` baseline, but the sample size is too small to justify immediate 3-step expansion.
- Most samples are uncertain near-miss cases, so this is a good active-learning candidate pool.
- Because trusted samples are only 2/15, the lazy gate is not strong enough for automatic training expansion yet.
- Next action should be candidate-pattern collection and queue analysis before another long 4B training run.

## Phase 04 Remaining Work

- Confirm whether low accuracy is mainly caused by:
  - shallow LoRA training
  - training target design
  - prompt quality for grading rather than JSON structure
- Use the current fix set as the new baseline before moving into broader LoRA quality work.

## Phase 04 Start Condition

- Phase 04_1 must finish root-cause documentation first.
- Do not start long epoch LoRA training before collapse causes are removed.

## GitHub Policy Reminder

- Raw eval artifacts remain local-only under `outputs/eval/`
- Only summarized status belongs in `docs/dev/`

## Phase 05 Pause Summary

- Phase 05 is paused, not completed.
- The Qwen3-VL VLM path reached structural validation and collapse-removal status.
- Remaining issue is low accuracy, not JSON instability or all-zero collapse.
- Accuracy improvement requires a new data/training strategy rather than simply increasing LoRA steps.
- Reliable data is defined as label-consistent data, not merely model-correct samples.
- Past successful evidence points to ROI crop, augmentation, possible unfreeze, and longer training as important variables.
- The current `Skin_Proj` work is paused here.
- Next project direction moves to `D:\vibe_coding\codex\Skin_diagnosis_proj` using skin diagnosis data and dermatologist consultation data.
- Phase 05 details and restart criteria are recorded in `D:\vibe_coding\codex\Skin_Proj\doc\pm\05_작업지시서_(정확도개선_및_능동학습_적용판단).md`.
