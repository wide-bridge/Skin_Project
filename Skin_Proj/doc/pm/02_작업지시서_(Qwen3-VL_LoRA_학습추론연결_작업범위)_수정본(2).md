# 02_작업지시서_(Qwen3-VL_LoRA_학습추론연결_작업범위)_수정본(2)

## 1. 목적

Qwen3-VL + LoRA 기반의 실제 학습/추론 파이프라인을 연결하고, 로컬 Windows 환경에서 재현 가능한 smoke path를 확보한다.

검증 대상:

- Processor load
- Model load
- LoRA attach
- Forward
- Loss
- Backward
- Optimizer step
- Checkpoint save/load
- Reloaded checkpoint inference
- JSON strict parsing

## 2. 모델 운영 원칙

현재 단계 모델 정책:

- `primary_4b`: 기본 학습/추론 연결 모델
- `quantized_4b`: 4B 경량화 fallback
- `smoke_safe_2b`: 안전 fallback
- `deferred_8b`: 로컬 LoRA 학습 금지, inference-only 후보

이유:

- 8B full/fp16 local LoRA 학습은 Windows + RTX 3090 환경에서 OS 레벨 크래시 이력이 있음
- 현재 목표는 최고 성능이 아니라 연결 검증과 안정성 확보

## 3. 작업 범위

### 3.1 config 기준 관리

`config/config.yaml`과 `config/config.template.yaml`에서 아래를 관리한다.

- profile 구조
- model / processor 이름
- precision
- device_map
- device
- max_image_size
- generation_max_new_tokens
- local_files_only
- allow_lora_training
- target_modules
- num_workers

CLI override는 허용하되, 기본값은 config 기준으로 유지한다.

### 3.2 현재 구현 기준 profile

실제 구현 기준:

- `primary_4b`
  - model: `Qwen/Qwen3-VL-4B-Instruct`
  - precision: `float16`
  - device_map: `single_gpu`
  - device: `cuda`
  - max_image_size: `1024`
  - local_files_only: `true`
- `quantized_4b`
  - model: `Qwen/Qwen3-VL-4B-Instruct`
  - quantization: `4bit`
  - max_image_size: `768`
- `smoke_safe_2b`
  - model: `Qwen/Qwen3-VL-2B-Instruct`
  - max_image_size: `768`
- `deferred_8b`
  - model: `Qwen/Qwen3-VL-8B-Instruct`
  - `allow_lora_training: false`

### 3.3 학습 연결

구현 대상:

- Processor load
- Base model load
- LoRA attach
- JSONL sample load
- Prompt load
- Resize 적용
- Forward / Loss / Backward / Optimizer
- Checkpoint save
- Reloaded checkpoint inference

### 3.4 학습 검증 순서

1. `primary_4b` one-batch smoke test

```bash
python -m train.train_lora --profile primary_4b --run-one-batch
```

2. 4B가 실패하면 `quantized_4b` 또는 `smoke_safe_2b`로 fallback

3. `deferred_8b`로 `train_lora` 실행은 차단

### 3.5 추론 검증

`01/02/03` 시나리오에서 각각 최소 1장 추론한다.

검증 항목:

- JSON strict parsing
- 필수 key exact match
- label range validation

필수 key:

- `forehead_wrinkle`
- `forehead_pigmentation`

### 3.6 입력 정책

- ROI crop은 이번 단계에 포함하지 않음
- resize policy와 aspect ratio 유지 적용
- Windows 실행 기준 `num_workers=0`

### 3.7 로그 분리

`validation_report`와 `smoke_test_log`는 분리한다.

- validation:
  - 데이터 검증 전용
- smoke:
  - 모델 load / 학습 / 추론 연결 검증 전용

## 4. 현재 결과 기준

02 단계 실제 완료 상태:

- `primary_4b` one-batch smoke test 성공
- 10분 timeout은 실행 시간 부족으로 실패
- 30분 timeout에서 forward/loss/backward/optimizer/checkpoint save 성공
- `deferred_8b` 학습 차단 성공
- `01/02/03` 각 1장 추론 성공
- strict JSON parsing 성공
- key / label range 검증 성공
- `cuda:0` 코드 하드코딩 제거
- `target_modules` config 이동
- `num_workers=0` 반영

관련 로그:

- `outputs/smoke_tests/smoke_test_log.json`
- `docs/dev/smoke_test_summary.md`

## 5. 개발 규칙

- config 밖의 민감 경로 하드코딩 금지
- Model ID 하드코딩 금지
- Prompt 본문 하드코딩 금지
- Resize policy 하드코딩 금지
- API Key 하드코딩 금지
- 8B local LoRA 학습 금지
- `deferred_8b` 학습 실행 차단 유지

## 6. 작업 제외 범위

- ROI Crop
- Prompt tuning
- Macro F1 최종 평가
- View 조합 실험
- 데이터 증강
- Backbone 변경
- 8B 로컬 LoRA 학습
- RAG
- Vector DB
- UI
- 챗봇 제품화

## 7. 완료 기준

- profile 구조 구현 완료
- `primary_4b` smoke test 성공
- `deferred_8b` 학습 차단 성공
- `01/02/03` 시나리오 추론 성공
- JSON strict parsing 성공
- key / range validation 성공
- validation / smoke log 분리 완료
- 하드코딩 점검 완료

02는 현재 완료 상태로 본다.
