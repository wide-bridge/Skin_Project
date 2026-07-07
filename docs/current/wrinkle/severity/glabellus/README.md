# Glabellus Wrinkle Severity Access Index

## 역할
- 이 문서는 `glabellus` 주름 중증도 실험축으로 다시 진입할 때 보는 상위 접근 인덱스입니다.
- 실제 실행 구조를 옮기지 않고, 기준 문서와 대표 실험 자산으로 빠르게 연결하는 역할만 합니다.

## 기준 문서
- [002_작업지시서_(미간_주름_중증도_실험과정_및_최종정리).md](../../../../../Skin_wrinkle_proj/doc/pm/current/002_작업지시서_(미간_주름_중증도_실험과정_및_최종정리).md)
- 보조 기반 문서: [000_작업지시서_(GitHub_연결_프로젝트_기반_설정).md](../../../../../Skin_wrinkle_proj/doc/pm/current/000_작업지시서_(GitHub_연결_프로젝트_기반_설정).md)

## 대표 yaml
- [glabellus_wrinkle_gw03_v2s_clean_aug.yaml](../../../../../Skin_wrinkle_proj/configs/glabellus_wrinkle_gw03_v2s_clean_aug.yaml)
- 보조 참고:
  - [glabellus_wrinkle_gw01_precrop.yaml](../../../../../Skin_wrinkle_proj/configs/glabellus_wrinkle_gw01_precrop.yaml)
  - [glabellus_wrinkle_gw02_v2s_tuned.yaml](../../../../../Skin_wrinkle_proj/configs/glabellus_wrinkle_gw02_v2s_tuned.yaml)
  - [glabellus_wrinkle_gw05_v2s_clean_aug_fine_unfreeze_hard.yaml](../../../../../Skin_wrinkle_proj/configs/glabellus_wrinkle_gw05_v2s_clean_aug_fine_unfreeze_hard.yaml)
  - [glabellus_wrinkle_gw06_v2s_clean_aug_fine_unfreeze_soft_label.yaml](../../../../../Skin_wrinkle_proj/configs/glabellus_wrinkle_gw06_v2s_clean_aug_fine_unfreeze_soft_label.yaml)

## 대표 script
- [run_gw03_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_gw03_strict_only.py)
- 보조 참고:
  - [run_gw05_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_gw05_strict_only.py)
  - [run_gw06_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_gw06_strict_only.py)

## 대표 outputs
- [metrics_glabellus_wrinkle.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_glabellus_wrinkle.csv)

## 대표 checkpoints
- [GW-03_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/GW-03_strict.pt)
- 보조 참고:
  - [GW-05_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/GW-05_strict.pt)
  - [GW-06_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/GW-06_strict.pt)

## 현재 판단 기준
- 현재 미간 주름 중증도 축의 대표 기준은 `GW-03`입니다.
- 판단 근거:
  - `EfficientNetV2-S`
  - `regression`
  - `glabellus pre-crop`
  - `strict split`
  - `cleaned weak augmentation`
  - `staged unfreeze`
- 현재 기준 문서상 `GW-03 / strict`가 미간 축의 최종 대표 기준으로 정리되어 있습니다.

## 다음에 이어서 볼 포인트
- 미간 축 다음 확장 순서는 `r_perocular` 주름 중증도입니다.
- 주름 실험 전체 기준이 어떻게 이어지는지는 [docs/current/wrinkle/README.md](../../README.md)에서 다시 확인합니다.
- 미간 축 후속 고도화 시 확인할 것:
  - `GW-03` 이후 추가 개선 실험 존재 여부
  - `GW-05`, `GW-06`의 재평가 필요성
  - `GW-04`의 실제 완료 여부 및 산출물 존재 여부

## 주의사항
- 이 문서는 접근 인덱스일 뿐이며, 실행 경로를 대체하지 않습니다.
- `Skin_wrinkle_proj` 본체, `doc/pm/current`, `configs`, `scripts`, `outputs`, `checkpoints`는 현재 위치를 유지합니다.
- 재실행 시 발생 가능한 문제:
  - `run_gw03_strict_only.py`는 내부에서 `GW-03` run_id를 직접 선택하므로, yaml 구조가 바뀌면 실패할 수 있습니다.
  - yaml 안의 `paths.outputs_root`, `image_root`, `label_root`, `precrop_root`가 현재 환경과 맞지 않으면 재실행이 깨질 수 있습니다.
  - metrics csv는 append 방식일 수 있어 중복 실행 시 결과 누적이 생길 수 있습니다.
  - `pre-crop` 전제를 갖는 실험이므로 crop 자산 상태가 다르면 재현성이 흔들릴 수 있습니다.
  - `GW-04`는 config는 존재하지만 현재 기준 문서상 최종 metrics/checkpoint/confusion 산출물이 확인되지 않으므로, 대표 기준으로 사용하면 안 됩니다.
