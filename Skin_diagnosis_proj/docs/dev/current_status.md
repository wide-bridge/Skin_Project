# Current Status

- 기준일: 2026-06-30
- 현재 단계: 04 모델 학습/추론 우선 진행 중
- 현재 판단:
  - 04-A는 완료 수준
  - 04-B는 EfficientNet-B0 기준 baseline 확보 완료
  - 04-C는 LoRA 검증을 지나 QLoRA 단독 본학습 구조로 전환 완료
  - 04-D는 baseline 샘플 추론 검증 완료, Qwen 계열은 학습 안정화 진행 중

## 04-A 데이터/학습셋 준비
- Derma_AI 실제 이미지 구조를 기준으로 질환 6종(`건선`, `아토피`, `여드름`, `정상`, `주사`, `지루`)과 뷰 2종(`정면`, `측면`)을 확인했다.
- `주사`는 이미지 분류 클래스에 포함한 상태로 유지한다.
- `data/processed/image_manifest.csv` 생성 완료: 총 10,800 rows
- `data/processed/vlm_train_dataset.jsonl` 생성 완료: 총 10,800 rows
- `data/processed/disease_ontology.csv`, `label_mapping.csv`, `rag_corpus_derma.jsonl` 재생성 완료

## 04-B 베이스라인 모델
- baseline backbone은 현재 `EfficientNet-B0`다.
- 실제 학습 기록상 최고 검증 정확도는 `epoch 7 / val_accuracy 0.9125`다.
- 최근 장시간 학습 기록은 `epoch 15`까지 확인되었다.
- 산출물:
  - `data/processed/baseline_train_metrics.json`
  - `data/processed/baseline_train_history.json`
  - `data/processed/baseline_sample_inference.json`

## 04-C Qwen3-VL + LoRA / QLoRA
- `Qwen/Qwen3-VL-4B-Instruct` 기준 LoRA tiny-step 학습 경로는 확인 완료.
- 현재는 `QLoRA` 기준으로 단독 실행 구조를 재구성했다.
- 상태/체크포인트/재시작 경로:
  - `outputs/qwen_qlora_phase04/status.json`
  - `outputs/qwen_qlora_phase04/checkpoints/`
  - `outputs/qwen_qlora_phase04/best_adapter/`
  - `outputs/qwen_qlora_phase04/latest_adapter/`
- 현재 status 기준 확인값 예시:
  - `phase: running`
  - `epoch: 1`
  - `global_step: 150`
  - `last_train_loss: 0.05207056179642677`

## 04-D 샘플 추론 검증
- baseline 샘플 추론 결과 확인 완료
- 예시:
  - image_id: `H1_501413_P1_L0`
  - ground_truth: `psoriasis`
  - predicted_disease: `psoriasis`
  - confidence: `0.9730455279350281`
  - needs_human_review: `false`

## 비고
- 현재 단계의 중심은 웹이 아니라 모델 검증이다.
- FastAPI placeholder 구조는 유지하되, 04의 본체는 데이터/모델/추론 검증이다.
- docs/dev는 실제 최신 결과 기준으로 계속 갱신한다.
