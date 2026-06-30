# 00_작업지시서_(GitHub_연결_및_형상관리_기반구축)

## 1. 목적

`Skin_diagnosis_proj`를 피부질환 진단 프로젝트의 독립 작업 공간으로 운영하고, 이후 문서, 코드, 설정, 실험 산출물을 GitHub와 로컬 전용 영역으로 분리해 안정적으로 관리할 수 있는 최소 기반을 마련한다.

이번 00 단계의 목적은 아래와 같다.

- 프로젝트 문서 시작점 생성
- 개발 상태 문서 생성
- GitHub 반영 가능한 초기 구조 확보
- 비밀키, 원본 데이터, 대용량 산출물의 분리 원칙 명시
- 이후 `01~08` 단계 작업지시서를 누적 수정할 수 있는 기준점 확보
- `doc/not_push` 로컬 전용 문서/노트북 운영 기준 확정

프로젝트 루트:

```text
D:\vibe_coding\codex\Skin_Project\Skin_diagnosis_proj
```

## 2. 현재 저장소 기준 운영 원칙

### 2.1 GitHub에 포함하는 것

- `Skin_diagnosis_proj/doc/pm` 작업지시서
- `Skin_diagnosis_proj/docs/dev` 상태 문서
- 소스코드와 공용 설정 템플릿
- 기술 스펙 문서와 API 문서
- 재현 가능한 소규모 산출물 예시

### 2.2 GitHub에 포함하지 않는 것

- 원본 이미지 데이터
- 원본 라벨 데이터
- 외부 참고 데이터셋 복사본
- 대용량 manifest/jsonl 중 로컬 실험용 파생 산출물
- 체크포인트, adapter weight, quantized cache
- `.env`, `.env.local`, `config.local.yaml`
- `doc/not_push` 아래 로컬 전용 문서와 노트북
- 외부 비공개 참고 문서 원문

### 2.3 외부 환경키 위치

로컬 비밀값은 저장소 밖에서 관리한다.

- 환경키 위치: `D:\PyProject\env_keys\.env`
- 확인된 주요 변수명:
  - `HF_TOKEN`
  - `OPENROUTER_API_KEY`
  - `OPENAI_API_KEY`

주의:

- 위 파일은 Git 추적 대상이 아니다.
- 문서와 코드에는 비밀값을 직접 기록하지 않는다.

## 3. 현재 실제 구조

현재 `Skin_diagnosis_proj` 기준 실제 생성된 구조는 아래와 같다.

```text
Skin_diagnosis_proj/
  apps/
    api/
    web/
  config/
  data/
    processed/
  doc/
    pm/
    not_push/
  docs/
    dev/
  outputs/
    logs/
    qwen_qlora_phase04/
  prompts/
  scripts/
  services/
```

## 4. 브랜치 및 원격 상태

현재 확인된 상태:

- 현재 브랜치: `main`
- 원격 저장소: `origin -> https://github.com/wide-bridge/Skin_Project.git`
- 최신 반영 커밋은 Git 기록 기준으로 갱신 관리

운영 원칙:

- 현재는 `main`에 문서와 일부 구현 반영 중
- 이후 장시간 학습/대규모 리팩터링은 `feature branch` 운영을 권장

## 5. .gitignore 기준

현재 프로젝트에서 분리 관리되는 주요 항목은 아래와 같다.

- `.env`, `.env.*`
- `config.local.yaml`, `*.local.yaml`
- `doc/not_push/`
- `outputs/` 하위 장시간 학습 산출물
- `checkpoints`, `runs`, adapter preview
- 모델 weight 계열 파일
- 대용량 데이터/캐시 폴더

현재 확인 사항:

- `data/processed` 안에는 Git에 포함할 소규모 기준 산출물과, 로컬 전용 학습 로그/metrics가 혼재할 수 있다.
- ignore 정책은 학습 구조 변화에 따라 계속 보강한다.

## 6. 상태 문서

현재 운영 중인 상태 문서:

- `docs/dev/current_status.md`
- `docs/dev/next_actions.md`
- `docs/dev/known_issues.md`
- `docs/dev/smoke_test_summary.md`

## 7. 00 단계 수행 결과

이번 00 단계에서 실제로 완료된 작업:

- `Skin_diagnosis_proj` 문서 루트 생성
- `00~08` 작업지시서 운영이 가능한 기반 생성
- `docs/dev` 상태 문서 생성
- Git 커밋 및 GitHub push 기반 확보
- 외부 환경키 위치 확인
- 로컬 전용 `doc/not_push` 운영 기준 확보

## 8. 완료 기준

아래를 만족하므로 00 단계는 완료로 처리한다.

- 저장소 내 문서 구조 생성 완료
- `doc/pm` 작업지시서 시작점 생성 완료
- `docs/dev` 상태 문서 생성 완료
- GitHub 커밋 및 push 가능 상태 확인 완료
- 외부 환경키 위치 및 비밀값 분리 원칙 확인 완료
- 로컬 전용 문서/노트북 분리 원칙 확인 완료
- 이후 01 단계부터 작업을 누적할 수 있는 기준점 확보 완료
