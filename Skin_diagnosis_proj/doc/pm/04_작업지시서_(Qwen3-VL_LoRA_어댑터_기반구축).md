# 04 작업지시서 (Qwen3-VL LoRA 어댑터 구현)

## 목적
피부질환 진단 프로젝트의 1차 핵심 구현으로서, 웹보다 먼저 모델 학습/추론 경로를 실제로 검증한다. 본 단계에서는 baseline 비전 모델과 Qwen3-VL 계열 어댑터 학습 경로를 모두 준비하고, 샘플 추론과 중간 성능 확인까지 수행한다.

## 진행 순서
1. 04-A 데이터/학습셋 준비
2. 04-B 베이스라인 모델
3. 04-C Qwen3-VL + LoRA/QLoRA
4. 04-D 로컬 추론 검증
5. 이후 FastAPI 연결 및 05 RAG 진행

## 04-A 데이터/학습셋 준비
- 실제 Derma_AI 이미지 구조 기준으로 클래스/뷰를 확정한다.
- `주사`는 이미지 분류 클래스에 포함한다.
- `image_manifest.csv`, `disease_ontology.csv`, `label_mapping.csv`, `vlm_train_dataset.jsonl`, `rag_corpus_derma.jsonl`를 생성한다.
- 학습 포맷은 baseline 분류기용과 Qwen3-VL instruction tuning용을 모두 준비한다.

## 04-B 베이스라인 모델
- baseline backbone은 현재 `EfficientNet-B0`를 기준으로 사용한다.
- ImageNet pretrained 가중치를 사용하고, 피부질환 6클래스 분류기로 fine-tuning 한다.
- 검증 목표는 아래와 같다.
  - train/val split에서 실제 성능 기준선 확보
  - best checkpoint 저장
  - 추후 Qwen3-VL 계열 결과와 비교 가능한 기준선 확보
- 현재 확인된 최고 baseline 결과는 `epoch 7 / val_accuracy 0.9125`이다.

## 04-C Qwen3-VL + LoRA/QLoRA
- 기준 모델은 `Qwen/Qwen3-VL-4B-Instruct`이다.
- 초기에는 LoRA 경로를 검증했고, 현재는 `QLoRA` 경로를 우선 실험한다.
- QLoRA 기준 설정은 아래를 따른다.
  - 4-bit load
  - `nf4`
  - double quantization
  - adapter만 학습
- 목적은 아래와 같다.
  - 3090 24GB 환경에서 더 안정적인 메모리 사용
  - adapter 학습 경로의 장시간 실행 가능성 확보
  - 상태 파일, best adapter, latest adapter, resume 구조 보강

## 04-D 로컬 추론 검증
- baseline 샘플 추론을 수행한다.
- 이후 `주사`, `지루`, `여드름`, `아토피` 중심으로 다건 추론을 확대해 혼동 패턴을 확인한다.
- Qwen 계열은 우선 학습 안정화와 checkpoint 생성이 선행되어야 하며, 그 후 생성 결과의 질환명 정확도/JSON 파싱률을 본다.

## 현재까지 수행 결과
- 04-A: 완료 수준
- 04-B: `EfficientNet-B0` 기준 실제 학습 및 최고 `val_accuracy 0.9125` 확인
- 04-C:
  - LoRA tiny-step 학습 경로 확인 완료
  - 현재는 QLoRA 단독 재실행 구조로 전환 완료
- 04-D: baseline 샘플 추론 1회 이상 확인

## 현재 산출물
- `data/processed/image_manifest.csv` (10800 rows)
- `data/processed/disease_ontology.csv`
- `data/processed/label_mapping.csv`
- `data/processed/vlm_train_dataset.jsonl` (10800 rows)
- `data/processed/rag_corpus_derma.jsonl`
- `data/processed/baseline_train_metrics.json`
- `data/processed/baseline_train_history.json`
- `data/processed/baseline_sample_inference.json`
- `data/processed/qwen_lora_train_metrics.json`
- `outputs/qwen_qlora_phase04/` (status/checkpoints/adapters)

## 완료 기준
- baseline 실제 학습 실행 및 기준선 확보
- Qwen3-VL 어댑터 학습 경로 실행 확인
- QLoRA 기반 장시간 학습 구조 확보
- 샘플 추론 실행
- 결과를 docs/dev 상태 문서에 반영
- 로컬 산출물은 보존하되, 체크포인트와 대용량 산출물은 Git에 포함하지 않는다.
