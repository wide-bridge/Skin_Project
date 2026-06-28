# 01 작업지시서: forehead_wrinkle 단일타깃 기준선 검증 및 학습전략 비교

## 목표
- `forehead_wrinkle` 단일 타깃에서 학습 가능성과 병목 원인을 먼저 확인한다.
- 최고 성능 탐색보다 문제 구조를 분해하는 기준선 실험을 우선한다.

## 핵심 질문
1. `EfficientNet`과 `Swin-T` 중 어떤 축이 더 안정적인가?
2. `classification` 대비 `regression/ordinal`이 실제로 더 낫나?
3. `loose split`과 `strict split` 차이가 얼마나 큰가?
4. 약한 증강과 샘플링 보정이 성능 안정화에 도움이 되나?

## 1차 실험 범위
- 타깃: `forehead_wrinkle`
- 입력: 가능하면 이마 ROI crop 기준
- split:
  - 탐색용 `loose split`
  - 판단용 `strict split`
- 모델:
  - `EfficientNet + classification`
  - `EfficientNet + regression/ordinal`
  - `Swin-T + regression/ordinal`
- 학습:
  - 조기종료 유지
  - epoch 상한 50
  - 동일 학습 budget으로 비교
- 증강:
  - 약한 crop/brightness/contrast/color jitter만 우선
  - weighted sampler 또는 class-balanced loss 병행
  - 과한 blur/warping/random erase는 제외

## 평가 지표
- accuracy
- +-1 허용 accuracy
- MAE
- confusion matrix
- `loose` vs `strict` 성능 차이

## 의사결정 기준
- `forehead_wrinkle` 단일 타깃에서 의미 있는 기준선이 서면 02 단계로 확장한다.
- `loose`만 높고 `strict`가 낮으면 누수/개인차 의존을 먼저 점검한다.
- 둘 다 낮으면 라벨 경계 또는 타깃 정의를 먼저 재검토한다.

## 다음 단계 연결
- 02: `forehead_wrinkle + glabellus_wrinkle`
- 03: `perocular` 추가 검토
