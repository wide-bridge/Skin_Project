# 01_작업지시서_(Vision_Agent_기반구축_작업범위)_수정본

## 1. 목적

Qwen3-VL 기반 피부분석 PoC를 위한 데이터 준비, 입력 구조, 검증 기반, 최소 추론 경로를 구축한다.

이번 단계의 목적은 최고 성능이 아니라 아래가 가능한 상태를 만드는 것이다.

- 원본 데이터를 복사하지 않고 외부 경로 참조
- `01/02/03` 시나리오 구조 정리
- `person_id` 기준 split 생성
- JSONL 학습 입력 생성
- 데이터 검증 로그 생성
- 최소 학습/추론 연결 기반 확보

## 2. 작업 범위

### 2.1 프로젝트 구조

```text
config/
dataset/
prompts/
train/
inference/
models/
lora/
outputs/
utils/
doc/
docs/
```

### 2.2 원본 데이터 사용 원칙

- 원본 데이터는 프로젝트 폴더로 복사하지 않는다.
- 원본 이미지/라벨 경로는 `config.local.yaml` 또는 동등한 로컬 설정에서 관리한다.
- 공용 저장소에는 절대경로를 커밋하지 않는다.

프로젝트 내부에는 아래 로컬 산출물만 생성할 수 있다.

- manifest
- split
- jsonl
- validation report
- smoke test log
- checkpoint
- inference output

위 산출물은 로컬 생성 허용 대상이며 Git 추적 대상에서는 제외한다.

### 2.3 데이터 범위

- `01`: 7 view
- `02`: 3 view
- `03`: 3 view

### 2.4 Manifest

Manifest 필수 항목:

- `id`
- `person_id`
- `scenario`
- `view`
- `image_path`
- `label_path`

### 2.5 Split

Train / Validation / Test split은 `person_id` 기준으로 수행한다.

금지:

- 동일 `person_id`가 여러 split에 중복 포함
- `scenario`만 기준으로 split
- `view`만 기준으로 split

### 2.6 JSONL 생성

1차 타깃은 아래 두 개로 제한한다.

- `forehead_wrinkle`
- `forehead_pigmentation`

학습 단계 출력 기준은 `JSON only`이다.

### 2.7 Dataset Validator

검증 항목:

- 이미지 존재 여부
- 라벨 존재 여부
- 원본 경로 유효 여부
- JSON 형식
- metadata 누락 여부
- person_id split 위반 여부
- scenario / view 누락 여부
- target key 누락 여부
- label 타입 및 범위 이상 여부

검증 결과는 `validation_report`로 관리한다.

### 2.8 Prompt

프롬프트 본문은 코드에 하드코딩하지 않는다.

사용 파일:

- `prompts/train.txt`
- `prompts/inference.txt`

### 2.9 LoRA 학습 기반

01 단계의 모델 운영 원칙:

- `4B`: 기본 학습/추론 연결 모델
- `2B`: smoke-safe fallback
- `8B`: 로컬 LoRA 학습 기본 경로에서 제외
- `8B`: quantized inference feasibility check만 허용

01 단계에서 필요한 것은 아래 수준이다.

- 최소 1 batch 입력 경로 확인
- smoke-safe 입력 경로 확인
- 학습/추론 연결을 위한 실행 기반 확보

### 2.10 최소 추론 경로

CLI 기반 최소 추론 경로를 준비한다.

01 단계 최소 추론 기준:

- JSON parsing 가능
- 필수 key 존재
- label 범위 검증 가능

`01/02/03` 전체 scenario 추론과 strict exact match 평가는 02 단계 검증 범위로 둔다.

## 3. 설정 및 경로 관리 규칙

- `.env`는 프로젝트에 복사하지 않는다.
- 로컬 경로는 `config.local.yaml` 또는 `.env.local`로 분리한다.
- 공용 config는 `config/config.yaml`
- 템플릿 config는 `config/config.template.yaml`
- 코드 내부 절대경로 하드코딩 금지

## 4. GitHub 운영 기준 연동

GitHub에는 아래만 남긴다.

- 생성 코드
- 검증 코드
- 학습/추론 코드
- prompt 템플릿
- 공용 config
- 작업지시서
- 상태 공유 문서

GitHub에서 제외:

- `dataset/jsonl/`
- `dataset/manifests/`
- `dataset/splits/`
- `dataset/logs/`
- `outputs/validation/` 실제 결과물
- `outputs/smoke_tests/` 실제 결과물

## 5. 상태 문서 갱신

01 단계 종료 시 아래 문서를 실제 내용으로 갱신한다.

- `docs/dev/current_status.md`
- `docs/dev/next_actions.md`
- `docs/dev/smoke_test_summary.md`

## 6. 개발 규칙

- 원본 데이터 수정 금지
- 원본 데이터 복사 금지
- prompt 본문 하드코딩 금지
- model id 직접 하드코딩 최소화, config/profile 기준 관리
- validation log와 smoke log 분리
- 8B 로컬 LoRA 학습 금지

## 7. 작업 제외 범위

- 챗봇 UI
- Streamlit
- Gradio
- RAG
- Vector DB
- 보고서 자동화
- 최종 정량 평가
- 8B 로컬 LoRA 학습

허용 예외:

- 8B quantized load feasibility check
- 8B quantized inference-only smoke test

## 8. 현재 결과 기준

01 단계 완료 상태:

- 프로젝트 구조 생성 완료
- manifest / split / JSONL / validator 코드 구현 완료
- 생성 산출물 Git 추적 제외 완료
- prompt 분리 완료
- 공용 config + template + local override 구조 반영 완료
- 상태 문서 갱신 완료

## 9. 완료 기준

- 프로젝트 구조 생성 완료
- `01/02/03` 반영 manifest/split/jsonl 생성 코드 완료
- validator 구현 완료
- validation report와 smoke log 분리 완료
- prompt 분리 완료
- 원본 데이터 비복사 원칙 유지 확인
- 생성 산출물 Git 추적 제외 확인
- `docs/dev/current_status.md` 갱신
- `docs/dev/next_actions.md` 갱신
- `docs/dev/smoke_test_summary.md` 갱신

01은 현재 완료 상태로 본다.
