# 016 작업지시서: 피부분석 5-class no-rosacea 및 여드름 검출 재점검 v1

## 문서번호
- `SD-PM-016`

## 1. 작성 목적
본 문서는 기존 피부질환 분류 실험과 여드름 병변 검출 실험을 재점검하고, 제품 방향에 맞춰 `rosacea`를 제외한 피부분석 모델 실험을 다시 정의하기 위한 작업지시서이다.

이번 재정의의 핵심 판단은 다음과 같다.

- 주 고객이 여성이고, 현재 제품 방향은 질환 진단 전체보다 피부 분석, 트러블 관리, 상담 필요성 판단에 가깝다.
- `rosacea`는 현재 피부분석 지표와 연결성이 낮고, `seborrheic_dermatitis`와 혼동을 만든다.
- 따라서 분류 모델은 `4질환 + 정상` 구조로 재정의한다.
- 여드름 병변 검출 모델은 진단 모델이 아니라 여드름 위치와 염증성 병변 근거를 제공하는 보조 모듈로 둔다.

## 2. 최종 대상 클래스
### 2.1 포함 클래스
- `acne`
- `atopic_dermatitis`
- `normal`
- `psoriasis`
- `seborrheic_dermatitis`

### 2.2 제외 클래스
- `rosacea`

제외 사유:

- 주 고객 및 서비스 메시지와 직접 연결성이 낮다.
- 홍조/혈관성 피부 분석 모듈이 별도로 없는 상태에서는 사용자에게 설명 가능한 관리 지표로 연결하기 어렵다.
- 기존 6-class confusion matrix에서 `rosacea`와 `seborrheic_dermatitis` 혼동이 존재한다.
- 현재 단계에서는 범위를 좁혀 스크리닝 신뢰도를 올리는 것이 더 적절하다.

## 3. 기존 분류 모델 점검
### 3.1 6-class frontal-only 기준
근거 파일:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed\frontal_eval_metrics_val.json`

주요 결과:

| 항목 | 값 |
|---|---:|
| samples | 600 |
| accuracy | 0.8283 |
| macro F1 | 0.8210 |
| normal vs lesion binary accuracy | 0.9967 |
| false normal count | 2 |

판단:

- frontal-only 기준 80% 초반-중반 성능은 확보했다.
- 정상 탐지는 매우 안정적이다.
- 약한 클래스는 `seborrheic_dermatitis`, `rosacea` 축이다.

### 3.2 6-class front+side 기준
근거 파일:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed\frontal_plus_side_v2s_eval_metrics_val.json`

주요 결과:

| 항목 | 값 |
|---|---:|
| samples | 1200 |
| accuracy | 0.8942 |
| macro F1 | 0.8958 |
| normal vs lesion binary accuracy | 0.9950 |
| false normal count | 6 |

판단:

- front+side 입력은 이미 90%에 근접한다.
- `rosacea` 제외 후에는 목표인 90% 이상을 현실적으로 노릴 수 있다.
- 단, front+side는 같은 환자/이미지 계열의 정면과 측면이 섞이는지 확인해야 하므로 split 누수 여부를 점검해야 한다.

## 4. 여드름 병변 검출 모델 재점검
### 4.1 U-Net + EfficientNet acne track
근거 파일:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed\acne_track_v1\acne_track_v1_metrics.json`

주요 결과:

| 항목 | 값 |
|---|---:|
| samples | 200 |
| binary acne detection accuracy | 0.9600 |
| precision | 0.9423 |
| recall | 0.9800 |
| specificity | 0.9400 |
| F1 | 0.9608 |
| severity proxy MAE | 1.82 |
| severity exact accuracy | 0.15 |
| severity within-one accuracy | 0.43 |

판단:

- 여드름 있음/없음 스크리닝은 사용 가능성이 높다.
- 중증도 0-4 등급은 아직 사용자에게 직접 노출하면 안 된다.
- 현재 중증도는 임상 정답이 아니라 bbox 기반 proxy이므로, 내부 참고값으로만 둔다.

### 4.2 YOLO26s inflammatory acne detector
근거 데이터셋:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed\acne_yolo26\inflammatory_only_side_tile512_min24\acne_yolo26_summary.json`

데이터 구성:

| 항목 | 값 |
|---|---:|
| view mode | side |
| class mode | inflammatory_only |
| tile size | 512 |
| selected images | 1800 |
| train acne/normal | 640 / 640 |
| val acne/normal | 160 / 160 |
| test acne/normal | 100 / 100 |
| train boxes | 974 |
| val boxes | 464 |
| test boxes | 249 |

최근 노트북 실행 로그 기준 YOLO26s 검증 결과:

| 항목 | 값 |
|---|---:|
| precision | 0.586 |
| recall | 0.552 |
| mAP50 | 0.560 |
| mAP50-95 | 0.197 |

판단:

- 염증성 여드름 위치 후보를 보여주는 보조 모델로는 의미가 있다.
- 단독 진단 모델이나 병변 개수 확정 모델로 쓰기에는 아직 부족하다.
- 현재는 `피부 트러블 근거 시각화`, `상담 권장 보조`, `LLM 설명 근거` 용도로 제한한다.
- 다음 실험에서는 confidence threshold, tile 정책, 작은 bbox 필터 기준, 정상 tile false positive를 함께 점검한다.

## 5. 새 실험 정의
### 5.1 실험 A: frontal-only 5-class no-rosacea
설정 파일:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\config\frontal_only_v2s_5class_no_rosacea.yaml`

데이터:

| 항목 | 값 |
|---|---:|
| 전체 원본 | 5400 |
| 제외 rosacea | 900 |
| 사용 샘플 | 4500 |
| train | 3200 |
| val | 800 |
| test | 500 |
| 클래스별 샘플 | 900 |

목표:

- validation accuracy >= 0.85
- macro F1 >= 0.85
- normal recall >= 0.98
- false normal count 최소화

### 5.2 실험 B: front+side 5-class no-rosacea
설정 파일:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\config\front_plus_side_v2s_5class_no_rosacea.yaml`

manifest:

- `D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed\front_plus_side_manifest\lesion_manifest.csv`

데이터:

| 항목 | 값 |
|---|---:|
| 전체 원본 | 10800 |
| 제외 rosacea | 1800 |
| 사용 샘플 | 9000 |
| train | 6400 |
| val | 1600 |
| test | 1000 |
| frontal | 4500 |
| side | 4500 |
| 클래스별 샘플 | 1800 |

목표:

- validation accuracy >= 0.90
- macro F1 >= 0.90
- normal recall >= 0.98
- disease macro recall >= 0.88

## 6. 구현 변경 사항
### 6.1 Config 선택
`SKIN_DIAGNOSIS_CONFIG` 환경변수로 실험 설정을 바꿔 실행한다.

예시:

```powershell
$env:SKIN_DIAGNOSIS_CONFIG="D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/config/frontal_only_v2s_5class_no_rosacea.yaml"
python D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/scripts/train_frontal_classifier.py
```

### 6.2 라벨 필터링
config의 `labels`에 없는 라벨은 학습/평가에서 자동 제외한다.

따라서 기존 `lesion_manifest.csv`에 `rosacea`가 남아 있어도 5-class 실험에는 섞이지 않는다.

## 7. 백그라운드 실행 계획
검수 후 실행할 명령:

### 7.1 frontal-only
```powershell
& D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/scripts/run_train_frontal_background.ps1 `
  -ConfigPath "D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/config/frontal_only_v2s_5class_no_rosacea.yaml" `
  -TaskName "SkinDiagnosisTrainFrontal5Class"
```

### 7.2 front+side
```powershell
& D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/scripts/run_train_frontal_background.ps1 `
  -ConfigPath "D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/config/front_plus_side_v2s_5class_no_rosacea.yaml" `
  -TaskName "SkinDiagnosisTrainFrontSide5Class"
```

상태 확인:

```powershell
& D:/vibe_coding/codex/Skin_Project/Skin_Diagnosis/scripts/check_train_frontal_background.ps1
```

## 8. 검수 요청 항목
학습 시작 전 검수받을 사항:

- `rosacea` 제외 확정 여부
- 최종 클래스가 `acne`, `atopic_dermatitis`, `normal`, `psoriasis`, `seborrheic_dermatitis` 5개인지
- frontal-only 목표를 85% 이상으로 둘지
- front+side 목표를 90% 이상으로 둘지
- front+side를 단일 모델로 먼저 돌릴지, frontal/side 개별 모델 + late fusion으로 갈지
- 여드름 YOLO detector는 병변 위치 보조로만 둘지
- 사용자 화면에는 질환 확정 진단이 아니라 의심/상담 권장 표현만 사용할지

## 9. 최종 판단
현재 단계의 제품 구조는 다음처럼 정리한다.

```text
입력 이미지
 -> 5-class no-rosacea 피부 상태 스크리닝
    -> acne / atopic_dermatitis / normal / psoriasis / seborrheic_dermatitis

 -> acne lesion detector
    -> 염증성 여드름 위치 후보
    -> 트러블 근거 시각화

 -> rule/LLM explanation layer
    -> 확정 진단 금지
    -> 의심 질환, 피부 관리 방향, 상담 권장 여부 설명
```

실험은 검수 후 `frontal-only`를 먼저 실행하고, 결과가 85% 이상이면 `front+side`를 실행한다. `front+side`가 90% 미만이면 late fusion 또는 seed ensemble을 추가 실험한다.
