# 00_작업지시서_(GitHub_연결_및_형상관리_기반구축)

## 1. 목적

`Skin_diagnosis_proj`는 피부질환 진단 VLM 프로젝트를 중심으로 시작하되, 이후 RAG, 비전 분기, HITL, React/FastAPI 서비스까지 확장할 수 있는 장기 작업 저장소로 운영한다.

이번 00 단계의 목적은 아래와 같다.

- GitHub 기반 공동 작업 구조 확립
- 프로젝트 산출물과 민감 데이터의 분리
- PM 문서, 개발 상태 문서, 작업 로그의 추적 가능 상태 확보
- 이후 `01~` 단계 작업지시서를 안정적으로 누적 수정할 수 있는 기반 마련

프로젝트 루트:

```text
D:\vibe_coding\codex\Skin_Project\Skin_diagnosis_proj
```

## 2. 운영 원칙

### 2.1 GitHub에 포함하는 것

- 소스코드
- 공용 설정 템플릿
- 작업지시서
- 기술 설계 문서
- 개발 상태 문서
- README
- `.gitignore`
- API 스펙 문서
- 프롬프트 템플릿
- 예시용 소규모 샘플 설정

### 2.2 GitHub에 포함하지 않는 것

- 원본 이미지 데이터
- 원본 라벨 데이터
- 외부 참고 데이터셋 복사본
- 생성된 manifest, split, jsonl 대용량 결과물
- 벡터 인덱스 실데이터
- 체크포인트, adapter weight, cache
- `.env`, `.env.local`, `config.local.yaml`
- 개인 검토용 문서, 비공개 회의자료, 민감 의료 문서

### 2.3 문서 구분

- `doc/pm`: 공식 작업지시서와 범위 정의
- `doc/spec`: 모델, 데이터, API, 오케스트레이션 상세 스펙
- `doc/local_only`: 외부 반출 금지 참고 문서
- `docs/dev`: 현재 상태, 다음 작업, 이슈, 스모크 테스트 요약

## 3. 권장 디렉터리 구조

```text
doc/
  pm/
  spec/
  local_only/

docs/
  dev/

apps/
  api/
  web/

services/
  router/
  vlm/
  vision/
  rag/
  hitl/

data/
  manifests/
  splits/
  processed/
  eval/

prompts/

scripts/

outputs/
```

## 4. 브랜치 정책

기본 브랜치:

```text
main
dev
```

운영 원칙:

- `main`은 안정 상태만 반영
- 기본 작업은 `dev` 또는 feature branch에서 수행
- 대규모 문서 개편도 `dev` 기준으로 진행
- 작업지시서 수정 이력은 커밋 메시지로 남김

## 5. .gitignore 기준

반드시 제외할 항목:

- 데이터 원본 경로 연결 산출물
- 대용량 학습 결과물
- 로컬 캐시
- 비밀키 및 로컬 설정
- 벡터 DB 실파일
- 업로드 이미지 및 사용자 로그 원본

## 6. 상태 문서

초기부터 아래 문서를 유지한다.

- `docs/dev/current_status.md`
- `docs/dev/next_actions.md`
- `docs/dev/known_issues.md`
- `docs/dev/smoke_test_summary.md`

## 7. 완료 기준

아래를 만족하면 00 단계 완료로 본다.

- 저장소 내 문서 구조 생성 완료
- `doc/pm` 작업지시서 시작점 생성 완료
- `docs/dev` 상태 문서 생성 완료
- Git 추적 제외 범위 합의 완료
- 이후 01 단계부터 작업을 누적할 수 있는 구조 확인 완료
