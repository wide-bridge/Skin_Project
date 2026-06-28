# 00_작업지시서_(GitHub_연결_및_형상관리_기반구축)

## 1. 목적

GitHub를 일반 자료 보관소가 아니라 아래 목적의 운영 공간으로 사용한다.

- 두 대의 PC에서 작업 연속성 유지
- GPT의 PM 문서 검토 및 의사결정 추적
- Codex의 코드 검토 및 변경 이력 관리
- 원본 데이터, 대용량 산출물, 민감정보를 코드 저장소와 분리

프로젝트 루트:

```text
D:\vibe_coding\codex\Skin_Proj
```

## 2. 운영 원칙

### 2.1 GitHub에 올리는 것

- 소스코드
- 공용 설정 파일
- `config.template.yaml`
- `README.md`
- `.gitignore`
- PM 작업지시서
- 개발 규칙 문서
- Prompt 템플릿
- 상태 공유 문서
- 의사결정 로그
- 구조 유지용 `.gitkeep`, `README.md`

### 2.2 GitHub에 올리지 않는 것

- 원본 데이터
- 생성된 `jsonl`, `manifest`, `split`, `validation log`
- 모델 weight, checkpoint, adapter weight
- 대용량 출력물
- 참고자료 성격의 문서
- `.env`, `.env.local`, `config.local.yaml`
- API Key 포함 가능 파일

### 2.3 경량 상태 파일 허용

두 PC 작업 연속성을 위해 아래 파일은 GitHub 추적 허용 대상이다.

- `docs/dev/current_status.md`
- `docs/dev/next_actions.md`
- `docs/dev/known_issues.md`
- `docs/dev/smoke_test_summary.md`
- `docs/pm/decision_log.md`
- `outputs/.gitkeep`
- `outputs/validation/.gitkeep`
- `outputs/smoke_tests/.gitkeep`
- `lora/README.md`

## 3. 디렉터리 구조

```text
doc/
  pm/
  spec/
  local_only/

docs/
  pm/
  dev/
```

역할:

- `doc/pm`: 공식 작업지시서
- `doc/spec`: 기술 규격 문서
- `doc/local_only`: GitHub 비추적 참고자료
- `docs/pm`: 의사결정 로그
- `docs/dev`: 현재 상태, 다음 작업, 이슈, smoke test 요약

## 4. 브랜치 전략

기본 브랜치:

```text
main
dev
```

원칙:

- `main`은 안정 버전만 유지
- 일상 작업은 `dev` 또는 feature 브랜치에서 수행
- `main` 직접 개발 금지

## 5. .gitignore 기준

핵심 원칙:

- 민감정보 제외
- 생성 데이터 제외
- 모델/체크포인트 제외
- local-only 문서 제외
- 구조 유지용 placeholder만 예외 허용

## 6. Push 전 확인

필수 확인 항목:

1. `git status`
2. `git ls-files`
3. 커밋 포함 파일 목록
4. 제외한 파일 목록
5. 일반 참고 문서 포함 여부
6. 생성 데이터 포함 여부
7. `.env` / `config.local.yaml` 포함 여부
8. `docs/dev/current_status.md`, `docs/dev/next_actions.md` 갱신 여부

## 7. 현재 결과 기준

00 단계 완료 상태:

- 로컬 Git 저장소 초기화 완료
- `main`, `dev` 브랜치 정리 완료
- `origin` 연결 완료
- GitHub 원격 저장소 연결 완료
- local-only 문서와 생성 산출물 추적 해제 완료
- `dev` 브랜치 push 완료

원격 저장소:

```text
https://github.com/wide-bridge/skin-vlm-agent
```

## 8. 완료 기준

- GitHub 운영 목적이 문서화됨
- 커밋 허용/금지 기준 정리됨
- 상태 공유 문서 위치와 역할 정리됨
- `.gitignore` 기준 정리됨
- 로컬 전용 문서와 생성 산출물 분리됨
- `dev` 브랜치 기준 원격 검토 가능 상태 확보
