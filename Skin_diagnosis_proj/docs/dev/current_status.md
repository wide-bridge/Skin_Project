# Current Status

- 기준일: 2026-06-29
- 현재 단계: 04 모델 학습/추론 우선 진행 중
- 현재 판단: 04-A는 완료 수준, 04-B/04-C는 실제 실행 검증까지 진행, 04-D는 샘플 추론 검증 1차 완료

## 04-A 데이터/학습셋 준비
- Derma_AI 실제 이미지 구조를 기준으로 질환 6종(`건선`, `아토피`, `여드름`, `정상`, `주사`, `지루`)과 뷰 2종(`정면`, `측면`)을 확인했다.
- `주사`는 이미지 분류 클래스에 포함한 상태로 유지한다.
- `data/processed/image_manifest.csv` 생성 완료: 총 10,800 rows
- `data/processed/vlm_train_dataset.jsonl` 생성 완료: 총 10,800 rows
- `data/processed/disease_ontology.csv`, `label_mapping.csv`, `rag_corpus_derma.jsonl` 재생성 완료

## 04-B 베이스라인 모델
- `torchvision resnet18` 기준 baseline 학습 루프를 실제로 연결했다.
- 학습 실행 결과:
  - device: `cuda`
  - train_samples: `96`
  - val_samples: `24`
  - test_samples: `240`
  - last_train_loss: `1.764684796333313`
  - val_accuracy: `0.16666666666666666`
- 산출물:
  - `data/processed/baseline_train_metrics.json`
  - `data/processed/baseline_resnet18_state.pt` (Git 제외 대상)

## 04-C Qwen3-VL + LoRA
- `Qwen/Qwen3-VL-4B-Instruct` 기준 tiny-step LoRA 학습 루프를 실제로 연결했다.
- 의존성 보강:
  - `transformers` 업그레이드
  - `peft`, `accelerate` 설치
- tiny-step 실행 결과:
  - model_id: `Qwen/Qwen3-VL-4B-Instruct`
  - device: `cuda`
  - dtype: `torch.float16`
  - train_rows_used: `2`
  - train_steps: `1`
  - last_train_loss: `2.9925694465637207`
  - adapter_trainable_params: `2949120`
- 산출물:
  - `data/processed/qwen_lora_train_metrics.json`
  - `data/processed/qwen_lora_adapter_preview/` (Git 제외 대상)

## 04-D 샘플 추론 검증
- baseline 샘플 추론 1건 실행 완료
- 결과 요약:
  - image_id: `H1_501413_P1_L0`
  - ground_truth: `psoriasis`
  - predicted_disease: `psoriasis`
  - confidence: `0.8898764252662659`
  - needs_human_review: `false`
- 산출물:
  - `data/processed/baseline_sample_inference.json`

## 비고
- 현재 단계의 중심은 웹이 아니라 모델 검증이다.
- FastAPI placeholder 구조는 유지하되, 04의 본체는 데이터/모델/추론 검증이다.
