# Smoke Test Summary

## Completed Smoke Tests

### 2B smoke-safe one-batch training

- Environment: `skin_vlm`
- Command path:
  - `D:\anaconda3\envs\skin_vlm\python.exe -m train.train_lora --smoke-safe --run-one-batch`
- Result: success
- Confirmed:
  - processor load
  - base model load
  - LoRA attach
  - JSONL sample load
  - input build
  - forward
  - loss
  - backward
  - optimizer step
  - checkpoint save

### 2B smoke-safe reload inference

- Command path:
  - `D:\anaconda3\envs\skin_vlm\python.exe -m inference.cli_infer --smoke-safe --use-lora --image D:\PyProject\datasets\skinAI\korea_skin_data\model_and_data\docker_image\skin_dataset\data_and_model\dataset\img\01\0001\0001_01_F.jpg`
- Result: success
- Confirmed:
  - saved adapter reload
  - sample image inference
  - JSON-style output

### 4B one-batch training smoke test

- Command path:
  - `D:\anaconda3\envs\skin_vlm\python.exe -m train.train_lora --profile primary_4b --run-one-batch`
- Timeout observations:
  - `600000 ms` (`10분`): loss 출력 후 timeout으로 종료
  - `1800000 ms` (`30분`): forward / loss / backward / optimizer_step / checkpoint_saved 성공
- Interpretation:
  - `10분` timeout 실패는 모델 실패가 아니라 실행 시간 부족으로 판단
  - 향후 4B smoke test 기본 timeout 권장값은 `30분 이상`

## Blocked / Deferred

### 8B local LoRA training

- Result: blocked / deferred
- Reason:
  - previous 8B one-batch path caused OS-level crash on Windows
  - local full/fp16 LoRA training is unsafe at current stage

### 8B quantized path

- Result: allowed for feasibility check only
- Scope:
  - quantized load test
  - inference-only smoke test
- Excluded:
  - 8B local LoRA training
