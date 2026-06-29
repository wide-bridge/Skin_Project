# Smoke Test Summary

기준일: 2026-06-29

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
- `python scripts/train_baseline_classifier.py` 실행 성공
- 요약 결과:
  - device: `cuda`
  - train_samples: `96`
  - val_samples: `24`
  - test_samples: `240`
  - last_train_loss: `1.764684796333313`
  - val_accuracy: `0.16666666666666666`

## 04-C Qwen3-VL + LoRA
- `python scripts/train_qwen_vlm_lora.py` 실행 성공
- 요약 결과:
  - model_id: `Qwen/Qwen3-VL-4B-Instruct`
  - train_rows_used: `2`
  - train_steps: `1`
  - last_train_loss: `2.9925694465637207`
  - adapter_trainable_params: `2949120`

## 04-D 샘플 추론
- `python scripts/run_sample_inference_baseline.py` 실행 성공
- 결과:
  - ground_truth: `psoriasis`
  - predicted_disease: `psoriasis`
  - confidence: `0.8898764252662659`
  - needs_human_review: `false`

## FastAPI placeholder
- 기존 `/health`, `/diagnosis/infer` placeholder 구조는 유지 중
- 현재 04의 핵심 검증은 모델/학습/추론 경로이며, API는 후속 연결 대상으로 본다.
