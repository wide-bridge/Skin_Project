# 00_작업지시서_(GitHub_연결_및_형상관리_기반구축)

## 1. 목적

`Skin_diagnosis_proj`를 피부질환 진단 VLM 프로젝트의 독립 작업 공간으로 시작하고, 이후 문서, 코드, 데이터 산출물, 설정 파일을 GitHub 기준으로 안정적으로 관리할 수 있는 최소 기반을 마련한다.

이번 00 단계의 목적은 아래와 같다.

- 프로젝트 문서 시작점 생성
- 개발 상태 문서 생성
- GitHub 반영 가능한 초기 구조 확보
- 비밀키, 원본 데이터, 대용량 산출물의 분리 원칙 명시
- 이후 `01~` 단계 작업지시서를 누적 수정할 수 있는 기준점 확보

프로젝트 루트:

```text
D:\vibe_coding\codex\Skin_Project\Skin_diagnosis_proj
```

## 2. 현재 저장소 기준 운영 원칙

### 2.1 GitHub에 포함하는 것

- `Skin_diagnosis_proj/doc/pm` 작업지시서
- `Skin_diagnosis_proj/docs/dev` 상태 문서
- 이후 추가될 소스코드와 공용 설정 템플릿
- 기술 스펙 문서와 API 문서

### 2.2 GitHub에 포함하지 않는 것

- 원본 이미지 데이터
- 원본 라벨 데이터
- 외부 참고 데이터셋 복사본
- 생성된 manifest, split, jsonl 대용량 결과물
- 체크포인트, adapter weight, cache
- `.env`, `.env.local`, `config.local.yaml`
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
  doc/
    pm/
      00_작업지시서_(GitHub_연결_및_형상관리_기반구축).md
      01_작업지시서_(프로젝트정의_및_범위확정).md
      02_작업지시서_(시스템아키텍처_및_서비스기반구축).md
      03_작업지시서_(데이터정의_및_VLM학습기반정리).md
      04_작업지시서_(RAG_비전_HITL_확장구조정의).md
      05_작업지시서_(React_FastAPI_UI_API_구현범위정의).md
  docs/
    dev/
      current_status.md
      known_issues.md
      next_actions.md
      smoke_test_summary.md
```

아래 구조는 향후 단계에서 확장한다.

- `doc/spec`
- `doc/local_only`
- `apps/`
- `services/`
- `data/`
- `outputs/`

## 4. 브랜치 및 원격 상태

현재 확인된 상태:

- 현재 브랜치: `main`
- 원격 저장소: `origin -> https://github.com/wide-bridge/Skin_Project.git`
- 최신 반영 커밋: `91a3bfb Add initial Skin_diagnosis_proj planning docs`

운영 원칙:

- 현재는 `main`에 초기 문서 반영 완료
- 이후 실제 구현 단계부터는 `dev` 또는 feature branch 운영을 권장

## 5. .gitignore 기준

루트 저장소의 `.gitignore`에서 현재 아래 범주가 이미 제외되고 있다.

- `.env`, `.env.*`
- `config.local.yaml`, `*.local.yaml`
- `outputs`, `checkpoints`, `runs`
- 모델 weight 계열 파일
- dataset 산출물 폴더
- `logs`, `.cache`, `cache`

현재 확인 사항:

- `Skin_diagnosis_proj` 자체에서 별도 산출물은 아직 생성되지 않음
- 루트 `.gitignore` 수정 사항이 다른 작업과 함께 존재하므로 이번 00 단계 완료 처리에는 포함하지 않음

## 6. 상태 문서

현재 생성 완료된 상태 문서:

- `docs/dev/current_status.md`
- `docs/dev/next_actions.md`
- `docs/dev/known_issues.md`
- `docs/dev/smoke_test_summary.md`

역할:

- `current_status.md`: 현재 진행 상태
- `next_actions.md`: 바로 이어질 작업
- `known_issues.md`: 현재 확인된 리스크
- `smoke_test_summary.md`: 코드 스모크 테스트가 시작되면 누적 기록

## 7. 00 단계 수행 결과

이번 00 단계에서 실제로 완료된 작업:

- `Skin_diagnosis_proj` 문서 루트 생성
- `00~05` 작업지시서 초안 생성
- `docs/dev` 상태 문서 생성
- Git 커밋 생성
- GitHub `main` 브랜치 push 완료
- 외부 환경키 위치 확인

이번 단계에서 의도적으로 아직 하지 않은 작업:

- `apps`, `services`, `data`, `outputs` 실제 폴더 생성
- 세부 `.gitignore` 프로젝트별 보강
- 코드 스모크 테스트
- 구현용 설정 템플릿 생성

위 항목은 01 이후 단계 범위로 넘긴다.

## 8. 완료 기준

아래를 만족하므로 00 단계는 완료로 처리한다.

- 저장소 내 문서 구조 생성 완료
- `doc/pm` 작업지시서 시작점 생성 완료
- `docs/dev` 상태 문서 생성 완료
- GitHub 커밋 및 push 완료
- 외부 환경키 위치 및 비밀값 분리 원칙 확인 완료
- 이후 01 단계부터 작업을 누적할 수 있는 기준점 확보 완료
