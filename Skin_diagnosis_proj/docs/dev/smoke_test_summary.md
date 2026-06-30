# Smoke Test Summary

기준일: 2026-06-30

## 04-A 데이터 산출물
- `python scripts/build_image_manifest.py` 실행 성공
  - 출력: `data/processed/image_manifest.csv`
  - rows: `10800`
- `python scripts/build_disease_ontology.py` 실행 성공
  - 출력: `data/processed/disease_ontology.csv`
- `python scripts/build_label_mapping.py` 실행 성공
  - 출력: `data/processed/label_mapping.csv`
- `python scripts/build_vlm_train_dataset.py` 실행 성공
  - 출력: `data/processed/vlm_train_dataset.jsonl`
  - rows: `10800`
- `python scripts/build_rag_corpus_derma.py` 실행 성공
  - 출력: `data/processed/rag_corpus_derma.jsonl`

## 04-B baseline 학습
- backbone: `EfficientNet-B0`
- 최고 검증 정확도 확인:
  - `epoch 7 / val_accuracy 0.9125`
- 샘플 추론 결과 예시:
  - `ground_truth: psoriasis`
  - `predicted_disease: psoriasis`
  - `confidence: 0.9730455279350281`

## 04-C Qwen3-VL LoRA / QLoRA
- LoRA tiny-step 학습 경로 확인 완료
- QLoRA 기준 단독 실행 구조 전환 완료
- 현재 QLoRA status 예시:
  - `phase: running`
  - `epoch: 1`
  - `global_step: 150`
  - `last_train_loss: 0.05207056179642677`

## 04-D 추론 검증
- baseline 샘플 추론 실행 성공
- Qwen 계열은 학습 안정화 후 생성 결과 검증 예정

## FastAPI placeholder
- 기존 `/health`, `/diagnosis/infer` placeholder 구조는 유지 중
- 현재 04의 핵심 검증은 모델/학습/추론 경로이며, API는 후속 연결 대상으로 본다.
