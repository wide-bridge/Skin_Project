# Skin_Proj

Qwen3-VL + LoRA 기반 피부분석 PoC를 위한 프로젝트 베이스입니다.

## 범위

- 원본 데이터는 외부 경로를 직접 참조합니다.
- 프로젝트 폴더에는 manifest, split, jsonl, validation log, checkpoint, inference output 같은 가공 산출물만 생성합니다.
- 1차 타깃은 `forehead_wrinkle`, `forehead_pigmentation` 입니다.

## 원본 데이터 및 환경 설정

- 원본 데이터 경로와 환경변수 경로는 `config.local.yaml` 또는 `.env.local`에서 관리합니다.
- `config.template.yaml`을 복사해 각 PC별 로컬 경로를 설정합니다.

## 디렉터리

- [dataset](dataset): manifest, split, jsonl, 검증 코드
- [prompts](prompts): 학습/추론 프롬프트
- [train](train): LoRA 학습 스크립트
- [inference](inference): CLI 추론 스크립트
- [utils](utils): 공용 설정, 경로, 로딩 유틸

## 권장 순서

1. `dataset/manifest_builder.py`로 manifest 생성
2. `dataset/splitter.py`로 person 단위 split 생성
3. `dataset/jsonl_builder.py`로 학습용 JSONL 생성
4. `dataset/validator.py`로 검증 로그 생성
5. `train/train_lora.py`로 LoRA 학습 연결
6. `inference/cli_infer.py`로 샘플 추론 확인

## 주의

- 원본 데이터는 복사하지 않습니다.
- `.env`는 프로젝트 폴더로 복사하지 않습니다.
- API 키는 로그와 산출물에 남기지 않습니다.
