# 04 작업지시서 (Qwen3-VL LoRA 어댑터 구현)

## 목적
피부질환 진단 프로젝트의 1차 핵심 구현으로서, 웹보다 먼저 모델 학습/추론 경로를 실제로 검증한다. 본 단계에서는 baseline 비전 모델과 Qwen3-VL + LoRA 경로를 모두 준비하고, 샘플 추론까지 확인한다.

## 진행 순서
1. 04-A 데이터/학습셋 준비
2. 04-B 베이스라인 모델
3. 04-C Qwen3-VL + LoRA
4. 04-D 로컬 추론 검증
5. 이후 FastAPI 연결 및 05 RAG 진행

## 04-A 데이터/학습셋 준비
- 실제 Derma_AI 이미지 구조 기준으로 클래스/뷰를 확정한다.
- `주사`는 이미지 분류 클래스에 포함한다.
- `image_manifest.csv`, `disease_ontology.csv`, `label_mapping.csv`, `vlm_train_dataset.jsonl`, `rag_corpus_derma.jsonl`를 생성한다.
- 학습 포맷은 baseline 분류기용과 Qwen3-VL instruction tuning용을 모두 준비한다.

## 04-B 베이스라인 모델
- `torchvision resnet18` 기준 baseline classifier를 실제로 학습한다.
- train/val/test split 기준으로 최소 1회 학습을 수행한다.
- 샘플 수를 제한한 경량 실행부터 시작해, 이후 점진적으로 확대한다.

## 04-C Qwen3-VL + LoRA
- `Qwen/Qwen3-VL-4B-Instruct`를 기준 모델로 사용한다.
- `peft` 기반 LoRA adapter를 연결한다.
- tiny-step이라도 실제 train step을 실행해 로딩/학습 경로를 검증한다.
- structured JSON 출력용 instruction 포맷을 유지한다.

## 04-D 로컬 추론 검증
- baseline 샘플 추론을 수행한다.
- 이후 `주사`, `지루`, `여드름`, `아토피` 중심으로 다건 추론을 확대해 혼동 패턴을 확인한다.

## 현재까지 수행 결과
- 04-A: 완료 수준
- 04-B: 실제 학습 1회 실행 확인
- 04-C: Qwen3-VL-4B tiny-step LoRA 학습 실행 확인
- 04-D: baseline 샘플 추론 1회 확인

## 현재 산출물
- `data/processed/image_manifest.csv` (10800 rows)
- `data/processed/vlm_train_dataset.jsonl` (10800 rows)
- `data/processed/baseline_train_metrics.json`
- `data/processed/baseline_sample_inference.json`
- `data/processed/qwen_lora_train_metrics.json`

## 완료 기준
- baseline 실제 학습 실행
- Qwen3-VL + LoRA tiny-step 학습 실행
- 샘플 추론 실행
- 결과를 docs/dev 상태 문서에 반영
- 로컬 산출물은 보존하되, 체크포인트와 대용량 산출물은 Git에 포함하지 않는다.
