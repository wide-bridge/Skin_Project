# 06 작업지시서 (최소챗봇 구현 및 VLM RAG 연결준비)

## 1. 목적

1차 서비스 마무리 단계로 baseline 진단 결과와 RAG 검색 결과를 API 응답에 결합하여, 설명 가능한 최소 상담 루프를 만든다.

이번 06 단계의 목표는 아래와 같다.

- `/diagnosis/infer`에 baseline 추론 결과를 실서비스 응답으로 연결
- retrieval 결과를 함께 반환하는 최소 RAG 연결 구조 구현
- 템플릿 기반 설명과 주의 문구를 먼저 구성하고, 이후 필요 시 LLM 자연어 생성으로 확장할 수 있게 설계
- 향후 챗봇/상담 루프로 확장 가능한 응답 payload 확정

## 2. 선행 조건

- 04에서 baseline 진단 엔진 확정 완료
- 05의 dermatology / plastic corpus 및 retrieval 구조 정의 완료

## 3. 구현 원칙

- 진단 엔진은 baseline(`EfficientNet-B0`)을 사용한다.
- `/diagnosis/infer`는 최소한 아래 세 레이어를 포함한다.
  - baseline 분류 결과
  - RAG 검색 결과
  - 설명/주의 문구 생성 결과
- 처음에는 템플릿 기반 설명으로 시작하고, 이후 LLM은 선택적으로 연결한다.
- 피부질환 설명과 성형/미용 상담은 분리된 corpus를 사용한다.

## 4. 최소 기능

- 사용자 이미지 입력
- baseline 질환 예측 결과 반환
- `retrieved_contexts` 반환
- `explanation` 반환
- `care_guidance` 반환
- 후속 일반 상담 모드 확장을 위한 응답 구조 확보

## 5. 응답 구조 방향

- `predicted_disease`
- `confidence`
- `differentials`
- `needs_human_review`
- `retrieved_contexts`
- `explanation`
- `care_guidance`

## 6. 완료 기준

- `/diagnosis/infer`가 baseline 추론 결과를 실제로 반환
- RAG retrieval 결과가 응답에 포함
- 최소 설명 문구와 주의 문구가 응답에 포함
- 질환별 샘플 응답 검토 가능
- 이후 LLM/챗봇 확장 포인트 확보
