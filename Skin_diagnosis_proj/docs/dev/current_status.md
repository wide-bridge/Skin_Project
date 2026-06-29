# Current Status

- `00` GitHub 연결 및 형상관리 기반구축 단계 완료
- `01` 프로젝트정의 및 범위확정 단계 완료
- `02` 시스템아키텍처 및 서비스기반구축 단계 완료
- `03` 데이터정의 및 VLM학습기반정리 단계 완료
- `04` 1차 구현 착수 완료
- 실행 가능한 데이터 생성 스크립트 추가 완료:
  - `python scripts/build_image_manifest.py`
  - `python scripts/build_disease_ontology.py`
  - `python scripts/build_label_mapping.py`
  - `python scripts/build_vlm_train_dataset.py`
  - `python scripts/build_rag_corpus_derma.py`
- 생성 산출물 위치 고정 완료: `data/processed/`
- FastAPI 최소 진단 API 실행 확인 완료:
  - `uvicorn apps.api.main:app --reload --port 8000`
  - `GET /health`
  - `POST /diagnosis/infer`
- 실제 Qwen 계열 VLM 및 LoRA adapter 로딩은 placeholder 상태 유지
