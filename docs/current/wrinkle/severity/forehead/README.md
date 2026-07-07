# Forehead Wrinkle Severity Access Index

## 역할
- 이 문서는 `forehead` 주름 중증도 실험축으로 다시 진입할 때 보는 상위 접근 인덱스입니다.
- 실제 실행 구조를 옮기지 않고, 기준 문서와 대표 실험 자산으로 빠르게 연결하는 역할만 합니다.

## 기준 문서
- [001_작업지시서_(이마_주름_중증도_실험과정_및_최종정리).md](../../../../../Skin_wrinkle_proj/doc/pm/current/001_작업지시서_(이마_주름_중증도_실험과정_및_최종정리).md)
- 보조 기반 문서: [000_작업지시서_(GitHub_연결_프로젝트_기반_설정).md](../../../../../Skin_wrinkle_proj/doc/pm/current/000_작업지시서_(GitHub_연결_프로젝트_기반_설정).md)

## 대표 yaml
- [forehead_wrinkle_fw07_v2s_tuned.yaml](../../../../../Skin_wrinkle_proj/configs/forehead_wrinkle_fw07_v2s_tuned.yaml)
- 보조 참고:
  - [forehead_wrinkle_fw05_precrop.yaml](../../../../../Skin_wrinkle_proj/configs/forehead_wrinkle_fw05_precrop.yaml)
  - [forehead_wrinkle_fw06_v2s_precrop.yaml](../../../../../Skin_wrinkle_proj/configs/forehead_wrinkle_fw06_v2s_precrop.yaml)

## 대표 script
- [run_fw07_strict_only.py](../../../../../Skin_wrinkle_proj/scripts/run_fw07_strict_only.py)
- 보조 참고:
  - [run_baseline_forehead.py](../../../../../Skin_wrinkle_proj/scripts/run_baseline_forehead.py)

## 대표 outputs
- [metrics_forehead_wrinkle.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/metrics_forehead_wrinkle.csv)
- 보조 참고:
  - [label_distribution_forehead_wrinkle.csv](../../../../../Skin_wrinkle_proj/outputs/metrics/label_distribution_forehead_wrinkle.csv)
  - [forehead_wrinkle_phase1_experiment_table.md](../../../../../Skin_wrinkle_proj/docs/dev/forehead_wrinkle_phase1_experiment_table.md)

## 대표 checkpoints
- [FW-07_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/FW-07_strict.pt)
- 보조 참고:
  - [FW-05_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/FW-05_strict.pt)
  - [FW-02_strict.pt](../../../../../Skin_wrinkle_proj/checkpoints/FW-02_strict.pt)

## 현재 판단 기준
- 현재 이마 주름 중증도 축의 대표 기준은 `FW-07`입니다.
- 판단 근거:
  - `EfficientNetV2-S`
  - `regression`
  - `forehead pre-crop`
  - `strict split`
  - `weak augmentation`
  - `staged unfreeze`
- 현재 기준 문서상 `FW-07 / strict`는 이마 축에서 가장 높은 대표 성능으로 정리되어 있습니다.

## 다음에 이어서 볼 포인트
- 이마 축 다음 확장 순서는 `glabellus` 중증도입니다.
- 주름 실험 전체 기준이 어떻게 이어지는지는 [docs/current/wrinkle/README.md](../../README.md)에서 다시 확인합니다.
- 이마 축의 후속 고도화 시 확인할 것:
  - `FW-07` 이후 추가 개선 실험 존재 여부
  - representative checkpoint와 metrics의 최신성
  - 웹 PoC 연결 시 결과 설명 문구 정리 여부

## 주의사항
- 이 문서는 접근 인덱스일 뿐이며, 실행 경로를 대체하지 않습니다.
- `Skin_wrinkle_proj` 본체, `doc/pm/current`, `configs`, `scripts`, `outputs`, `checkpoints`는 현재 위치를 유지합니다.
- 재실행 시 발생 가능한 문제:
  - `run_fw07_strict_only.py`는 내부에서 `FW-07` run_id를 직접 선택하므로, yaml 구조가 바뀌면 실패할 수 있습니다.
  - yaml 안의 `paths.outputs_root`, `image_root`, `label_root`, `precrop_root`가 현재 환경과 맞지 않으면 재실행이 깨질 수 있습니다.
  - metrics csv는 append 방식일 수 있어 중복 실행 시 결과 누적이 생길 수 있습니다.
  - `pre-crop` 전제를 갖는 실험이므로 crop 자산 상태가 다르면 재현성이 흔들릴 수 있습니다.
  - 현재 링크된 대표 자산은 지금 기준으로 타당하지만, 이후 추가 실험이 생기면 대표 자산을 다시 검토해야 합니다.
