# Left Periocular Wrinkle Severity Access Index

## 역할
- 이 문서는 `l_perocular` 주름 중증도 실험축으로 다시 진입할 때 보는 상위 접근 인덱스입니다.
- 실제 실행 구조를 옮기지 않고, 기준 문서와 대표 실험 자산으로 빠르게 연결하는 역할만 합니다.

## 기준 문서
- [003_작업지시서_(눈가_중증도_실험과정_및_최종정리).md](../../../../../Skin_wrinkle_proj/doc/pm/current/003_작업지시서_(눈가_중증도_실험과정_및_최종정리).md)
- 보조 기반 문서: [000_작업지시서_(GitHub_연결_프로젝트_기반_설정).md](../../../../../Skin_wrinkle_proj/doc/pm/current/000_작업지시서_(GitHub_연결_프로젝트_기반_설정).md)

## 대표 yaml
- [l_perocular_wrinkle_lpe02_v2s_clean_aug.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_wrinkle_lpe02_v2s_clean_aug.yaml)
- 보조 참고:
  - [l_perocular_wrinkle_lpe01_precrop.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_wrinkle_lpe01_precrop.yaml)

## 대표 script
- [run_lpe02_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_lpe02_strict_only.py)
- 보조 참고:
  - [run_lpe01_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_lpe01_strict_only.py)
  - [run_perocular_v2s_clean_sequence.ps1](../../../../../Skin_wrinkle_proj/scripts/run_perocular_v2s_clean_sequence.ps1)

## 대표 outputs
- [metrics_l_perocular_wrinkle.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_l_perocular_wrinkle.csv)

## 대표 checkpoints
- [LPE-02_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/LPE-02_strict.pt)
- 보조 참고:
  - [LPE-01_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/LPE-01_strict.pt)

## 현재 판단 기준
- 현재 왼쪽 눈가 주름 중증도 축의 대표 기준은 `LPE-02`입니다.
- 판단 근거:
  - `EfficientNetV2-S`
  - `regression`
  - `l_perocular pre-crop`
  - `strict split`
  - `clean augmentation`
- 현재 기준 문서상 `LPE-02 / strict`가 왼쪽 눈가 축의 최종 대표 기준으로 정리되어 있습니다.

## 다음에 이어서 볼 포인트
- 왼쪽 눈가 축 다음은 `r_perocular state`입니다.
- 주름 실험 전체 기준이 어떻게 이어지는지는 [docs/current/wrinkle/README.md](../../README.md)에서 다시 확인합니다.
- 왼쪽 눈가 축 후속 고도화 시 확인할 것:
  - 오른쪽 대비 개선 폭 차이의 원인
  - 상태 실험(`l_perocular state`)과 웹에서 어떻게 결합할지

## 주의사항
- 이 문서는 접근 인덱스일 뿐이며, 실행 경로를 대체하지 않습니다.
- `Skin_wrinkle_proj` 본체, `doc/pm/current`, `configs`, `scripts`, `outputs`, `checkpoints`는 현재 위치를 유지합니다.
- 재실행 시 발생 가능한 문제:
  - `run_lpe02_strict_only.py`는 내부에서 `LPE-02` run_id를 직접 선택하므로, yaml 구조가 바뀌면 실패할 수 있습니다.
  - yaml 안의 `paths.outputs_root`, `image_root`, `label_root`, `precrop_root`가 현재 환경과 맞지 않으면 재실행이 깨질 수 있습니다.
  - metrics csv는 append 방식일 수 있어 중복 실행 시 결과 누적이 생길 수 있습니다.
  - `pre-crop` 전제를 갖는 실험이므로 crop 자산 상태가 다르면 재현성이 흔들릴 수 있습니다.
  - 오른쪽/왼쪽 눈가를 너무 빨리 통합해서 해석하면 현재 기준 문서의 분리 판단을 흐릴 수 있습니다.
