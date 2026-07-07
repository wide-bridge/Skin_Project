# 073 Wrinkle 접근 하이어라키 검증 및 아카이브 판정

## 1. 목적
- `docs/current/wrinkle` 아래에 만든 접근 하이어라키가 몇 개월 뒤 재진입용 구조로 충분한지 검증한다.
- `Skin_wrinkle_proj`는 기준 프로젝트로 유지하고, 이름 변경이나 본체 이동은 후속 단계로 남긴다.
- `Skin_Proj`, `Skin_diagnosis_proj` 중 어떤 자산부터 archive 성격으로 정리할 수 있는지 위험도를 구분한다.

## 2. 이번 단계에서 검증한 범위
- 상위 인덱스:
  - [docs/current/wrinkle/README.md](../current/wrinkle/README.md)
- 중증도 접근 인덱스:
  - [forehead](../current/wrinkle/severity/forehead/README.md)
  - [glabellus](../current/wrinkle/severity/glabellus/README.md)
  - [r_perocular severity](../current/wrinkle/severity/r_perocular/README.md)
  - [l_perocular severity](../current/wrinkle/severity/l_perocular/README.md)
- 상태 접근 인덱스:
  - [r_perocular state](../current/wrinkle/state/r_perocular/README.md)
  - [l_perocular state](../current/wrinkle/state/l_perocular/README.md)

## 3. 검증 결과
### 3-1. wrinkle 접근 구조
- `wrinkle` 접근 하이어라키는 `중증도 / 상태`와 `부위 축` 기준으로 재진입 경로를 분리하는 데 성공했다.
- 각 README는 `기준 문서`, `대표 yaml`, `대표 script`, `대표 outputs`, `대표 checkpoints`, `현재 판단 기준`, `다음 포인트`, `주의사항`을 담고 있다.
- 따라서 몇 개월 뒤 다시 접근할 때도 "어디서부터 읽어야 하는가"를 먼저 해결할 수 있다.

### 3-2. 실행 안정성
- `Skin_wrinkle_proj` 본체는 이동하지 않았다.
- `doc/pm/current`, `configs`, `scripts`, `outputs`, `checkpoints`, `logs`, `skin_crop_data`도 이동하지 않았다.
- `src`와 import 구조도 건드리지 않았다.
- 따라서 현재 단계의 변경은 실행 경로를 대체하지 않는 문서 인덱스 추가로 한정된다.

### 3-3. 링크 검증
- 폴더명 변경을 나중으로 미룬 상태이므로, 접근 인덱스 안의 링크는 다시 `Skin_wrinkle_proj` 기준으로 맞췄다.
- 이 조치를 통해 "현재 실제 경로"와 "상위 접근 문서" 사이의 불일치를 제거했다.

## 4. 이번 단계에서 확인된 위험
### 4-1. wrinkle 이름 변경
- `Skin_wrinkle_proj -> Skin_wrinkle` 변경은 아직 진행하지 않는다.
- 이유:
  - 스크립트의 `Set-Location`
  - 문서 상대경로
  - 일부 절대경로 설명
  - 재실행 시 checkpoint / outputs 참조
  가 함께 흔들릴 수 있기 때문이다.

### 4-2. Skin_diagnosis_proj archive 이동
- `Skin_diagnosis_proj`는 지금 단계에서 archive로 옮기지 않는다.
- 이유:
  - `run_api.ps1`
  - `run_phase04_long_training.ps1`
  - `run_qwen_phase04_train.ps1`
  - 일부 평가 결과 json 안의 절대경로
  가 남아 있어 이동 시 실행/참조 경로가 깨질 수 있다.

### 4-3. Skin_Proj archive 이동
- `Skin_Proj`는 `Skin_diagnosis_proj`보다 archive 후보로 더 적합하다.
- 다만 현재 워킹트리에 삭제/신규 파일이 섞여 있으므로, 실제 이동 전에 상태 정리가 필요하다.

## 5. archive 판정
- `Skin_wrinkle_proj`
  - 현재 유지
  - 기준 프로젝트
- `Skin_diagnosis_proj`
  - 현재 유지
  - reference / legacy-project 성격
  - archive 이동은 보류
- `Skin_Proj`
  - archive 우선 후보
  - 실제 이동은 후속 단계에서 단독으로 검토

## 6. 몇 개월 뒤 다시 시작할 때의 권장 접근 순서
1. [docs/current/wrinkle/README.md](../current/wrinkle/README.md)부터 읽는다.
2. 필요한 실험축 README를 선택한다.
3. 해당 README에서 `기준 문서 -> 대표 yaml -> 대표 script -> 대표 outputs/checkpoints` 순서로 내려간다.
4. 이름 변경이나 archive 재배치는 그 다음 별도 단계로 검토한다.

## 7. 최종 판정
- 프로세스 6 기준으로 `wrinkle-first 접근 하이어라키`는 유효하다.
- 현재 시점에서는 "실행 구조 이동"보다 "접근 구조와 역할 정의"가 더 중요하며, 그 목적은 달성되었다.
- 다음 우선순위는 `Skin_Proj`의 archive 정리이고, `Skin_diagnosis_proj`와 `Skin_wrinkle_proj`의 폴더명/위치 변경은 아직 보류하는 것이 안전하다.
