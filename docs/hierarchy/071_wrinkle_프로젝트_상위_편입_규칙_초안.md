# 071 상위 하이어라키 기준 wrinkle 프로젝트 편입 규칙

## 1. 목적
- `Skin_wrinkle_proj`를 상위 하이어라키 `projects/wrinkle`에 어떻게 편입할지 논리 규칙을 먼저 확정한다.
- 이번 문서는 물리 이동 문서가 아니라, 현재 활성 프로젝트를 깨지 않으면서 상위 구조와 연결하기 위한 기준 문서다.
- 내일 진행할 주름 + 피부진단 웹 PoC에서 `wrinkle` 결과를 바로 참조할 수 있도록 문서, 코드, 산출물의 역할을 분리한다.

## 2. 프로세스 1, 2와의 정합성 검토
### 2-1. 프로세스 1과의 일치점
- `Skin_wrinkle_proj`는 현재 활성 프로젝트이며 즉시 폐기하거나 archive로 보낼 대상이 아니다.
- `Skin_wrinkle_proj`는 절대경로와 현재 위치 의존이 남아 있으므로 지금 당장 `projects/wrinkle`로 물리 이동하면 실행이 깨질 수 있다.
- 따라서 이번 프로세스는 물리 이동이 아니라 편입 규칙 정의에 집중해야 한다.

### 2-2. 프로세스 2와의 일치점
- 상위 문서 [070_상위_하이어라키_설계_초안.md](./070_상위_하이어라키_설계_초안.md)에서 정의한 `projects/wrinkle`은 주름 분석 전용 하위 프로젝트다.
- 이번 문서는 그 상위 정의를 `Skin_wrinkle_proj`에 구체적으로 대응시키는 세부 편입 규칙 문서다.
- 즉 `070`이 상위 구조 문서라면, 본 문서는 `wrinkle` 도메인의 하위 연결 규칙 문서다.

### 2-3. 이번에 새로 확인된 주의점
- 문서 체계는 `doc/pm/current`, `doc/pm/legacy`로 이미 잘 정리되어 있다.
- 반면 실행 체계는 `configs`, `scripts`, `src`, `outputs`, `checkpoints`, `logs` 중심으로 누적되어 있다.
- 또한 최상위에 `config` 폴더가 별도로 존재하지만 현재 비어 있어 보이며, 실제 설정은 `configs`가 사용되고 있다.
- 따라서 상위 편입 규칙에는 `config`와 `configs`의 역할 정리가 포함되어야 한다.

## 3. wrinkle 프로젝트의 현재 역할
- 현재 실제 프로젝트 위치: `D:\vibe_coding\codex\Skin_Project\Skin_wrinkle_proj`
- 상위 하이어라키상의 목표 위치: `projects/wrinkle`
- 현재 역할:
  - 주름 중증도 분석
  - 주름 상태 분석
  - ROI 기반 crop 입력 실험
  - 모델 학습, 평가, 결과 저장
  - 웹 PoC에 연결될 주름 결과 기준 제공

한 문장 정의:
- `Skin_wrinkle_proj`는 현재 주름 분석의 실행 주체이며, 상위 하이어라키에서는 장차 `projects/wrinkle`로 편입될 활성 하위 프로젝트다.

## 4. current / legacy 문서 체계의 상위 연결 규칙
### 4-1. 기본 원칙
- `Skin_wrinkle_proj/doc/pm/current`는 주름 분석의 현재 기준 문서 묶음이다.
- `Skin_wrinkle_proj/doc/pm/legacy`는 과거 실험 흔적과 주석성 참고 자료 묶음이다.
- 상위 `docs`는 이 둘을 대체하지 않고, 프로젝트 간 공통 기준과 연결 구조를 설명한다.

### 4-2. 상위 docs와의 역할 분담
- 상위 `docs/hierarchy`
  - 전체 프로젝트 구조, 책임 범위, 편입 규칙을 정의한다.
- 상위 `docs/current`
  - 장차 주름과 진단을 가로지르는 상위 운영 기준이 필요할 때 사용한다.
- `Skin_wrinkle_proj/doc/pm/current`
  - 주름 도메인 내부의 실제 기준 문서를 유지한다.
- `Skin_wrinkle_proj/doc/pm/legacy`
  - 현재 문서의 근거, 보조 설명, 과거 판단 추적 자료를 유지한다.

### 4-3. 현재 기준 문서의 역할
- `current/000`
  - 주름 프로젝트의 기반 설정, 데이터 루트, split/crop 규칙, 공통 운영 기준
- `current/001`
  - 이마 주름 중증도 최종 기준
- `current/002`
  - 미간 주름 중증도 최종 기준
- `current/003`
  - 눈가 주름 중증도 최종 기준
- `current/004`
  - 눈가 주름 상태 최종 기준

### 4-4. 편입 규칙
- 상위 구조 관점에서는 `Skin_wrinkle_proj/doc/pm/current/000~004`를 `projects/wrinkle`의 공식 기준 문서로 간주한다.
- 상위 `docs`는 주름 문서 본문을 다시 복제하지 않고, 주름 프로젝트를 어디에 어떻게 연결하는지와 타 도메인과의 관계만 정리한다.
- 즉 주름 도메인의 실험 판단은 계속 `Skin_wrinkle_proj/doc/pm/current`에 남기고, 상위 문서는 메타 구조만 관리한다.

## 5. legacy 문서의 위치와 작동 원칙
### 5-1. 역할 정의
- `legacy`는 더 이상 현재 기준 문서가 아니다.
- `legacy`는 아래 목적에만 사용한다.
  - 초기 가설 확인
  - 중간 설계 흔적 추적
  - 폐기된 방향의 근거 확인
  - current 문서의 세부 배경 확인

### 5-2. current 대비 관계
- 새로운 의사결정, 웹 구현, 후속 실험 기준은 반드시 `current/000~004`를 우선 참조한다.
- `legacy`는 current 문서를 보조하는 주석/참고자료여야 하며, 본문을 대체해서는 안 된다.
- `LEGACY_INDEX.md`는 이 원칙을 위한 연결 인덱스로 유지한다.

### 5-3. 재검토 판단
- 현재 `README_작업지시서_배치안내.md`와 `legacy/LEGACY_INDEX.md` 구조상 `legacy`는 본문 대체가 아니라 참고자료로 작동하도록 설계되어 있다.
- 따라서 프로세스 1, 2의 방향과 충돌하지 않는다.

## 6. 코드/설정/산출물의 상위 편입 규칙
### 6-1. 현재 실행 체계
현재 `Skin_wrinkle_proj`의 실행 중심 폴더는 아래와 같다.
- `configs`
- `scripts`
- `src`
- `outputs`
- `checkpoints`
- `logs`

보조 또는 과거 성격 폴더:
- `config`
- `dataset`
- `eval`
- `train`
- `docs`
- `doc`

### 6-2. 목표 대응 구조
장기적으로 `projects/wrinkle` 아래에서는 아래 대응을 목표로 한다.
- `configs` -> `projects/wrinkle/configs`
- `scripts` -> `projects/wrinkle/scripts`
- `src` -> `projects/wrinkle/src`
- `outputs` -> `projects/wrinkle/outputs`
- `checkpoints` -> `projects/wrinkle/checkpoints`
- `logs` -> `projects/wrinkle/logs`
- `doc/pm/current`, `doc/pm/legacy` -> 주름 프로젝트 문서 영역으로 유지

### 6-3. 지금 당장 유지할 것
- 현재 경로 의존 때문에 위 폴더들은 `Skin_wrinkle_proj` 안에 그대로 유지한다.
- 상위 하이어라키는 이를 `projects/wrinkle`에 대응되는 현재 실제 프로젝트로 해석한다.
- 즉 지금은 이름만 목표 구조에 맞춰 해석하고, 물리 이동은 보류한다.

### 6-4. config / configs 정리 원칙
- 실제 실험 설정 파일은 `configs`에 존재한다.
- 최상위 `config` 폴더는 현재 비어 있어 역할이 불명확하다.
- 따라서 현재 기준에서는:
  - `configs`를 공식 설정 루트로 간주한다.
  - `config`는 향후 정리 대상 또는 제거 후보로 표시한다.
- 단, 즉시 삭제는 하지 않는다.

## 7. wrinkle 내부 분석축 분리 규칙
### 7-1. 상위 기준 분석축
`wrinkle` 내부 분석축은 아래 두 가지로 고정한다.
- `severity`
- `state`

### 7-2. severity 범위
`severity`에는 아래 문서와 실험군이 포함된다.
- `current/001` 이마 주름 중증도
- `current/002` 미간 주름 중증도
- `current/003` 눈가 주름 중증도

대표 설정/실행 단위 예시:
- `configs/forehead_wrinkle_fw07_v2s_tuned.yaml`
- `configs/glabellus_wrinkle_gw03_v2s_clean_aug.yaml`
- `configs/l_perocular_wrinkle_lpe02_v2s_clean_aug.yaml`
- `configs/r_perocular_wrinkle_rpe02_v2s_clean_aug.yaml`

### 7-3. state 범위
`state`에는 아래 문서와 실험군이 포함된다.
- `current/004` 눈가 주름 상태

대표 설정/실행 단위 예시:
- `configs/r_perocular_shape_rps01_v2s_multi4_aug.yaml`
- `configs/r_perocular_shape_rps02_v2s_multi4_bins_aug.yaml`
- `configs/r_perocular_depth_rpd03_v2s_extreme_middle_aug.yaml`
- `configs/l_perocular_depth_lpd03_v2s_extreme_middle_aug.yaml`
- `configs/r_perocular_relief_rpr03_v2s_extreme_middle_aug.yaml`
- `configs/l_perocular_relief_lpr03_v2s_extreme_middle_aug.yaml`

### 7-4. 웹 PoC 기준 해석
- 내일 웹 PoC에서 우선 직접 연결하기 쉬운 축은 `severity`다.
- `state`는 이미 current/004에서 서비스 해석 규칙까지 일부 정리되어 있으므로, 눈가 부위에 한해 보조 카드 또는 상세 상태 카드로 확장 가능하다.
- 따라서 웹 PoC 기준 우선순위는:
  1. `severity`
  2. `state`
  순으로 본다.

## 8. 상위 문서와 하위 프로젝트 문서의 역할 분담
### 8-1. 상위 문서가 담당할 것
- 프로젝트 전체 구조
- 프로젝트 간 책임 분리
- 하이어라키와 번호 체계
- 이동 순서와 영향 범위
- integration/web과의 연결 원칙

### 8-2. wrinkle 하위 문서가 담당할 것
- 실험 목적과 맥락
- 모델별 비교 결과
- 최종 채택 기준
- 관련 `.py`, `.yaml`, `.md` 산출물 목록
- 상태/중증도 해석 규칙

### 8-3. 핵심 원칙
- 상위 문서는 `무엇을 어디에 둬야 하는가`를 설명한다.
- 하위 프로젝트 문서는 `왜 그렇게 판단했고 무엇이 기준인가`를 설명한다.
- 이 역할이 섞이면 상위 문서가 비대해지고 하위 문서가 약해지므로 분리 유지가 필요하다.

## 9. 내일 웹 PoC 관점의 바로 참조 규칙
### 9-1. 바로 참조할 기준 문서
- `current/001`: forehead severity
- `current/002`: glabellus severity
- `current/003`: perocular severity
- `current/004`: perocular state

### 9-2. 바로 참조할 산출물 종류
- `outputs/metrics/*.csv`
- `configs/*.yaml`
- `scripts/run_*`
- `checkpoints/*.pt`

### 9-3. 웹 PoC를 위한 최소 연결 규칙
- PoC는 우선 `current` 문서 기준으로 어떤 모델/설정이 대표 기준인지 판단한다.
- 실제 추론 연결 시에는 current 문서에 적힌 대표 run과 대응 yaml/checkpoint를 우선 사용한다.
- `legacy` 문서는 PoC 기준선 선택에 직접 개입하지 않는다.

## 10. 최종 편입 판단
### 10-1. 지금 유지
- `Skin_wrinkle_proj`의 현재 물리 위치
- 현재 `doc/pm/current`, `doc/pm/legacy` 체계
- `configs`, `scripts`, `src`, `outputs`, `checkpoints`, `logs`의 현 구조

### 10-2. 나중 이동
- `Skin_wrinkle_proj` 전체를 `projects/wrinkle` 물리 구조로 옮기는 작업
- `skin_crop_data`를 `shared/crop_data`로 물리 이동하는 작업
- 경로 하드코딩 제거 후의 폴더 정규화

### 10-3. 상위에서 참조
- `docs/hierarchy/070`과 본 문서 `071`
- 향후 생성될 상위 구조 문서
- 내일 생성할 `integration/web` 설계 문서

## 11. 프로세스 3 결론
- `Skin_wrinkle_proj`는 현재 활성 프로젝트로 그대로 유지한다.
- 상위 하이어라키에서는 이를 `projects/wrinkle`에 대응되는 실행 프로젝트로 해석한다.
- 주름 도메인의 기준 판단은 계속 `doc/pm/current/000~004`가 담당한다.
- `legacy`는 참고자료로만 유지한다.
- 물리 이동은 경로 의존성 정리 이후 별도 프로세스로 수행한다.

## 12. 한 문장 요약
- `Skin_wrinkle_proj`는 지금은 현재 위치를 유지하되, 상위 구조에서는 `projects/wrinkle`의 실제 실행 원본으로 해석하고, 기준 판단은 current 문서에서, 메타 구조는 상위 hierarchy 문서에서 관리한다.
