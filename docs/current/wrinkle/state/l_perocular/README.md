# Left Periocular Wrinkle State Access Index

## 역할
- 이 문서는 `l_perocular` 주름 상태 실험축으로 다시 진입할 때 보는 상위 접근 인덱스입니다.
- 실제 실행 구조를 옮기지 않고, 기준 문서와 대표 상태 실험 자산으로 빠르게 연결하는 역할만 합니다.

## 기준 문서
- [004_작업지시서_(눈가_주름_상태_실험과정_및_최종정리).md](../../../../../Skin_wrinkle_proj/doc/pm/current/004_작업지시서_(눈가_주름_상태_실험과정_및_최종정리).md)
- 보조 연결 문서:
  - [003_작업지시서_(눈가_중증도_실험과정_및_최종정리).md](../../../../../Skin_wrinkle_proj/doc/pm/current/003_작업지시서_(눈가_중증도_실험과정_및_최종정리).md)

## 대표 yaml
- 깊이 상태:
  - [l_perocular_depth_lpd03_v2s_extreme_middle_aug.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_depth_lpd03_v2s_extreme_middle_aug.yaml)
- 요철 상태:
  - [l_perocular_relief_lpr03_v2s_extreme_middle_aug.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_relief_lpr03_v2s_extreme_middle_aug.yaml)
- 보조 참고:
  - [l_perocular_shape_lps01_v2s_multi4_aug.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_shape_lps01_v2s_multi4_aug.yaml)
  - [l_perocular_shape_lps02_v2s_multi4_bins_aug.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_shape_lps02_v2s_multi4_bins_aug.yaml)
  - [l_perocular_depth_lpd02_v2s_pctordinal_aug.yaml](../../../../../Skin_wrinkle_proj/configs/l_perocular_depth_lpd02_v2s_pctordinal_aug.yaml)

## 대표 script
- 깊이/요철 3그룹 상태 공통 실행:
  - [run_shape_extreme_middle_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_shape_extreme_middle_strict_only.py)
- 보조 참고:
  - [run_lps01_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_lps01_strict_only.py)
  - [run_lps02_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_lps02_strict_only.py)
  - [run_shape_percentile_ordinal_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_shape_percentile_ordinal_strict_only.py)
  - [run_perocular_shape_extreme_middle_sequence.ps1](../../../../../Skin_wrinkle_proj/scripts/run_perocular_shape_extreme_middle_sequence.ps1)

## 대표 outputs
- 깊이 상태:
  - [metrics_l_perocular_depth_extreme_middle.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_l_perocular_depth_extreme_middle.csv)
- 요철 상태:
  - [metrics_l_perocular_relief_extreme_middle.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_l_perocular_relief_extreme_middle.csv)
- 보조 참고:
  - [metrics_l_perocular_shape.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_l_perocular_shape.csv)
  - [metrics_l_perocular_shape_5bin.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_l_perocular_shape_5bin.csv)
  - [metrics_l_perocular_shape_multitask.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_l_perocular_shape_multitask.csv)

## 대표 checkpoints
- 깊이 상태:
  - [LPD-03_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/LPD-03_strict.pt)
- 요철 상태:
  - [LPR-03_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/LPR-03_strict.pt)
- 보조 참고:
  - `LPD-02`: 추후 확인
  - `LPR-02`: 추후 확인
  - `LPD-01`, `LPR-01`: 추후 확인

## 현재 판단 기준
- 현재 왼쪽 눈가 상태 축의 대표 기준은 `3그룹 상태 표현`입니다.
- 대표 채택:
  - 깊이 상태: `LPD-03`
  - 요철 상태: `LPR-03`
- 현재 기준 문서상 왼쪽 눈가 상태는 5등급 exact보다 `낮음/중간/높음`에 가까운 3그룹 표현이 웹/서비스 관점에서 더 적절한 것으로 정리되어 있습니다.

## 다음에 이어서 볼 포인트
- 주름 실험 상태 축 정리 이후에는 `Skin_wrinkle_proj -> Skin_wrinkle` 이름 변경 영향 점검으로 넘어갑니다.
- 주름 실험 전체 기준이 어떻게 이어지는지는 [docs/current/wrinkle/README.md](../../README.md)에서 다시 확인합니다.
- 왼쪽 눈가 상태 후속 고도화 시 확인할 것:
  - 상태 카드를 웹에서 severity와 어떻게 분리 표현할지
  - 깊이와 요철을 각각 보여줄지, 통합 상태 요약으로 보여줄지
  - `LPS-01/LPS-02` 연속값/5-bin 분석을 어느 수준까지 유지할지

## 주의사항
- 이 문서는 접근 인덱스일 뿐이며, 실행 경로를 대체하지 않습니다.
- `Skin_wrinkle_proj` 본체, `doc/pm/current`, `configs`, `scripts`, `outputs`, `checkpoints`는 현재 위치를 유지합니다.
- 재실행 시 발생 가능한 문제:
  - 상태 실험은 `shape -> 5bin -> percentile ordinal -> extreme-middle 3그룹`으로 단계가 여러 개라, 대표 기준을 착각하면 잘못된 실험을 다시 돌릴 수 있습니다.
  - yaml 안의 `paths.outputs_root`, `image_root`, `label_root`, `precrop_root`가 현재 환경과 맞지 않으면 재실행이 깨질 수 있습니다.
  - metrics csv는 append 방식일 수 있어 중복 실행 시 결과 누적이 생길 수 있습니다.
  - `pre-crop` 및 기기지표 전제를 갖는 실험이므로 자산 상태가 다르면 재현성이 흔들릴 수 있습니다.
  - `LPD-02`, `LPR-02`, `LPD-01`, `LPR-01` 계열은 현재 최종 산출물 확인이 불충분하므로 대표 기준으로 쓰지 않아야 합니다.
