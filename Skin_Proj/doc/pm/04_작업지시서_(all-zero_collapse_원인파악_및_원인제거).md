# 04_작업지시서_(all-zero_collapse_원인파악_및_원인제거)

## 1. 목적

04 단계의 목적은 아래 두 가지를 한 문서 안에서 순차적으로 처리하는 것이다.

- `all-zero collapse`의 실제 원인을 근거와 함께 확정한다.
- 확정된 원인을 최소 수정으로 제거하고, collapse 해소 여부를 검증한다.

이 단계는 본학습 성능 최적화 단계가 아니다.  
먼저 원인을 구조적으로 파악하고, collapse를 깨는 데 필요한 최소 수정만 적용하는 것이 목적이다.

또한 이 문서는 04 진행 중 계속 수정·보완되는 기준 문서로 운영한다.

## 2. 현재 전제

- `00` GitHub 및 형상관리 기반: 완료
- `01` Vision Agent 기반 구축: 완료
- `02` Qwen3-VL LoRA smoke path: 완료
- `03` 소규모 정량평가 및 프로파일 비교: 완료

03 단계 결론:

- JSON parsing: 통과
- 필수 key exact match: 통과
- label range validation: 통과
- exact match: 낮음
- 당시 문제는 `all-zero collapse`

04 단계 시작 시점의 핵심 질문:

- 모델이 왜 `0`만 출력하는가
- 그 원인이 prompt bias인지, loss mask 구조인지, training label 연결인지, 데이터 연결 문제인지 구분할 수 있는가

## 3. 현재 04 결론 요약

현재까지의 04 진행 결과는 아래와 같다.

- `all-zero collapse`는 해소되었다.
- `single-value collapse`도 현재 30샘플 기준으로는 보이지 않는다.
- `lora_checkpoint_4b exact_match_rate`는 `0.10`이다.
- 즉 문제의 성격은 `collapse`에서 `낮은 정확도`로 전환되었다.

따라서 04의 종료 판단은 다음과 같다.

- collapse 원인 파악: 완료
- 1차 원인 제거: 완료
- 남은 과제: 정확도 개선 및 본학습 품질 향상

## 4. 기본 원칙

- `primary_4b`를 기준 프로필로 사용한다.
- `quantized_4b`는 비교 후보로만 사용한다.
- `5단계 리매핑`은 유지한다.
- `outputs/eval/*`, `outputs/debug/*` 원본 로그는 로컬 전용이다.
- GitHub에는 `docs/dev/current_status.md`, `docs/dev/next_actions.md` 요약만 반영한다.
- `dataset/jsonl/train_forehead.jsonl`은 GitHub 커밋 대상이 아닌 로컬 생성 산출물 참조 대상이다.
- 04에서는 능동학습을 적용하지 않는다.
- balanced subset 검증은 필수 완료 조건이 아니라 필요 시 수행하는 보조 검증이다.

## 5. 원인 파악

### 5.1 loss mask 구조 확인

확인 대상:

- assistant JSON token에만 loss가 걸리는가
- prompt / user token은 `labels=-100` 처리되는가
- 전체 `input_ids`가 그대로 labels로 복사되고 있지는 않은가

확인 결과:

- 초기 상태에서는 `labels = input_ids.clone()` 구조였다.
- 즉 prompt / user / assistant 전체에 loss가 걸리고 있었다.
- 이는 collapse의 가장 강한 원인 후보 중 하나였다.

관련 파일:

- `D:\vibe_coding\codex\Skin_Proj\train\train_lora.py`

### 5.2 training label 주입 확인

확인 대상:

- JSONL `output` 값이 실제 training labels에 반영되는가
- chat template 적용 후 assistant JSON 구간이 유지되는가
- labels tensor가 assistant JSON 구간과 대응되는가

확인 결과:

- assistant JSON 자체는 입력에 들어가고 있었다.
- 문제는 JSON이 빠진 것이 아니라, assistant-only supervision이 없었다는 점이다.

관련 파일:

- `D:\vibe_coding\codex\Skin_Proj\train\train_lora.py`
- `D:\vibe_coding\codex\Skin_Proj\dataset\jsonl_builder.py`
- `D:\vibe_coding\codex\Skin_Proj\dataset\jsonl\train_forehead.jsonl`

주의:

- `train_forehead.jsonl`은 로컬 생성 산출물이며 GitHub 커밋 대상이 아니다.

### 5.3 prompt bias 확인

확인 대상:

- inference prompt가 기본값 `0`을 유도하는가
- zero-filled JSON 예시가 base model bias를 만드는가

확인 결과:

- 초기 inference prompt에는 `{"forehead_wrinkle": 0, "forehead_pigmentation": 0}` 예시가 포함돼 있었다.
- base model도 이 구조를 따라 `0` 출력 쪽으로 편향되었다.
- 이는 collapse의 또 다른 강한 원인이었다.

관련 파일:

- `D:\vibe_coding\codex\Skin_Proj\prompts\inference.txt`
- `D:\vibe_coding\codex\Skin_Proj\inference\cli_infer.py`

### 5.4 데이터 연결 문제 배제

확인 대상:

- 이미지 경로 정상
- 라벨 경로 정상
- image-label 매칭 정상
- scenario / view 혼합 문제 없음
- split leakage 없음

확인 결과:

- 데이터 연결 문제는 주원인이 아니었다.
- collapse는 데이터 누락이나 경로 깨짐보다 학습 입력 구조와 prompt bias에 더 강하게 연결되어 있었다.

### 5.5 분포 문제 확인

확인 대상:

- 5단계 리매핑 후 분포
- 필요 시 balanced subset에서도 collapse가 반복되는가

확인 결과:

- 5단계 리매핑은 분포 완화에는 도움이 되었지만 collapse 자체를 해결하지는 못했다.
- 따라서 class remapping만으로는 원인이 설명되지 않았다.

## 6. 원인 제거

### 6.1 loss mask 수정

적용 기준:

- prompt / user token: `labels=-100`
- assistant JSON token: 실제 정답 labels

적용 결과:

- assistant-only loss mask가 추가되었다.
- sample-level 확인에서 `labels_equal_input_ids = false`가 확인되었다.
- `labels=-100` masking이 assistant JSON 바깥 구간에 적용됨이 확인되었다.

관련 파일:

- `D:\vibe_coding\codex\Skin_Proj\train\train_lora.py`

### 6.2 prompt 수정

적용 기준:

- 기본값 `0` 유도 문구 제거
- zero-filled JSON 예시 제거
- JSON 키 구조는 유지하되 값 bias는 제거

적용 결과:

- base model 출력이 더 이상 all-zero 패턴에 고정되지 않았다.

관련 파일:

- `D:\vibe_coding\codex\Skin_Proj\prompts\inference.txt`

### 6.3 수정 후 검증

검증 순서:

1. prompt 수정 후 base inference 확인
2. loss mask 수정 후 one-batch 입력 검증
3. base `primary_4b`, `smoke_safe_2b`, `qwen3_vl_forehead` 비교
4. 30샘플 기준 상수 출력 여부 확인

검증 결과:

- `all-zero collapse` 해소
- `single-value collapse`도 현재 30샘플 기준 미관측
- `lora_checkpoint_4b`는 여러 클래스 값을 출력
- 다만 정확도는 여전히 낮음

## 7. 현재 최종 판단

04의 핵심 결론은 아래와 같다.

1. 가장 강한 원인은 다음 두 가지였다.
   - zero-filled inference prompt bias
   - assistant-only loss mask 부재
2. 위 두 원인은 실제 수정 후 모델 행동 변화를 통해 확인되었다.
3. collapse는 해소되었다.
4. 현재 남은 문제는 collapse가 아니라 낮은 정확도다.

즉 04는 “왜 `0`만 출력하는가”라는 문제에는 답을 냈고,  
이제 남은 문제는 “왜 정답을 잘 못 맞히는가”로 바뀌었다.

## 8. 작업 범위

04 범위 안에서 허용되는 것:

- loss mask 구조 검증
- JSONL target 주입 검증
- prompt bias 제거
- collapse 해소 여부 검증
- 필요 시 balanced subset 보조 검증
- 결과를 `docs/dev`에 요약 반영

04 범위 밖:

- 대규모 epoch 본학습 최적화
- ROI crop
- 대규모 prompt tuning 반복
- data augmentation
- 8B local LoRA training
- 능동학습 적용

## 9. 산출물 정책

로컬 전용 산출물:

- `outputs/debug/*`
- `outputs/eval/*`
- `dataset/jsonl/train_forehead.jsonl`

GitHub 반영 대상:

- `D:\vibe_coding\codex\Skin_Proj\docs\dev\current_status.md`
- `D:\vibe_coding\codex\Skin_Proj\docs\dev\next_actions.md`

커밋 금지:

- `outputs/debug/*`
- `outputs/eval/*`
- `config.local.yaml`
- `.env`
- 원본 이미지 경로 하드코딩
- prompt 본문 하드코딩

## 10. 완료 기준

아래를 만족하면 04는 완료로 본다.

- collapse 원인 파악 완료
- 1순위 원인 수정 완료
- `all-zero collapse` 해소 확인 완료
- `single-value collapse` 미관측 확인 완료
- 결과를 `docs/dev`에 요약 반영 완료

정확도 향상은 04의 완료 기준이 아니다.  
정확도 개선은 다음 단계의 핵심 과제로 넘긴다.

## 11. 다음 단계 연결

04 이후 다음 단계는 아래처럼 이어진다.

1. LoRA 본학습 품질 개선
2. 정량 평가 재실행
3. 필요 시 능동학습 적용 필요성 판단

즉 04는 collapse를 끊는 단계이고,  
그 다음부터가 실제 품질 개선 단계다.
