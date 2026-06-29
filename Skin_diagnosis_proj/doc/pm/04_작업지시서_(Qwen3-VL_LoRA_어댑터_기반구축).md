# 04_작업지시서_(Qwen3-VL_LoRA_어댑터_기반구축)

## 1. 목적

1차 구현 착수 단계에서 `Qwen 계열 VLM + LoRA adapter`를 바로 연결할 수 있도록,
먼저 피부질환 진단용 데이터 산출물과 진단 API 계약을 고정한다.

이번 04 단계의 목표는 아래와 같다.

- VLM 학습용 데이터 산출물 구조 확정
- 피부질환 ontology / label mapping 구조 확정
- 이미지 1장 입력 -> 구조화 JSON 출력 경로 확보
- 실제 모델 없이도 placeholder 진단 API가 동작하도록 구현
- 후속 Qwen 계열 VLM / LoRA adapter, RAG, 챗봇이 붙을 수 있는 계약 고정

## 2. 선행 조건

- 03 단계의 데이터 정의 및 ontology 원칙 정리 완료
- canonical label 방향 확정 완료
- RAG 본문은 `label_data` 우선 사용 정책 확정 완료

## 3. 범위

### In Scope

- `image_manifest.csv` 생성 구조
- `disease_ontology.csv` 생성 구조
- `label_mapping.csv` 생성 구조
- `vlm_train_dataset.jsonl` 생성 구조
- `rag_corpus_derma.jsonl` placeholder 생성 구조
- FastAPI 최소 앱
- `/health`
- `/diagnosis/infer`
- strict JSON response schema
- placeholder VLM service 구조

### Out of Scope for Now

- 실제 Qwen 계열 모델 로딩
- 실제 LoRA adapter 결합
- RAG 결합
- 일반 상담 챗봇 고도화
- Vision fallback 비교 실험
- HITL 운영 화면
- React UI 구현

## 4. 핵심 산출물

- `scripts/build_image_manifest.py`
- `scripts/build_disease_ontology.py`
- `scripts/build_label_mapping.py`
- `scripts/build_vlm_train_dataset.py`
- `scripts/build_rag_corpus_derma.py`
- `data/processed/*` 산출물
- FastAPI inference entrypoint
- diagnosis JSON schema
- 최소 smoke test 결과

## 5. 권장 출력 형식

```json
{
  "predicted_disease": "acne",
  "confidence": 0.81,
  "differentials": ["comedonal_acne", "inflammatory_papule"],
  "needs_human_review": true,
  "summary": "Placeholder response generated without loading an actual VLM model."
}
```

## 6. 완료 기준

- `python scripts/build_image_manifest.py` 실행 가능
- `python scripts/build_disease_ontology.py` 실행 가능
- `python scripts/build_label_mapping.py` 실행 가능
- `python scripts/build_vlm_train_dataset.py` 실행 가능
- `python scripts/build_rag_corpus_derma.py` 실행 가능
- 각 스크립트는 `data/processed/` 아래 정해진 포맷 파일 생성
- `uvicorn apps.api.main:app --reload` 실행 가능
- `GET /health` 정상 응답
- `POST /diagnosis/infer` 정상 응답
- 실제 모델 없이도 placeholder JSON 반환
- 원본 이미지, 원본 라벨, 체크포인트, `.env`, `config.local.yaml` Git 제외 확인

## 7. 진행 중 수정사항 기록

- 기존 04 문서는 `Qwen3-VL + LoRA 최소 추론` 중심으로 작성되어 있었음
- 현재 실제 1차 구현 범위는 `데이터 산출물 + placeholder 진단 API` 중심으로 재정렬되었음
- 따라서 이번 04 문서는 현행 완료 기준에 맞게 갱신함
