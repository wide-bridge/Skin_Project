# 04_작업지시서_(Qwen3-VL_LoRA_어댑터_기반구축)

## 1. 목적

1차 구현의 핵심 본체로 `Qwen3-VL + LoRA adapter` 기반 피부질환 진단 경로를 구축한다.

이번 04 단계의 목표는 아래와 같다.

- Qwen3-VL 기반 최소 추론 경로 준비
- LoRA adapter 적용 구조 정의
- 이미지 1장 입력 -> 구조화 JSON 출력 경로 확보
- 후속 챗봇과 RAG가 붙을 수 있는 진단 결과 포맷 확정

## 2. 선행 조건

- 03 단계의 데이터 정의 및 ontology 원칙 정리 완료
- canonical label과 VLM 출력 JSON 방향 확정 완료

## 3. 범위

### In Scope

- Qwen3-VL 모델 선택
- LoRA adapter 적용 구조
- 이미지 추론 파이프라인
- strict JSON 출력 형식
- 최소 테스트 입력/출력 경로

### Out of Scope for Now

- RAG 결합
- 일반 상담 챗봇 고도화
- Vision fallback 비교 실험
- HITL 운영 화면

## 4. 핵심 산출물

- VLM inference entrypoint
- LoRA adapter 로딩 구조
- diagnosis JSON schema
- 최소 smoke test 결과

## 5. 권장 출력 형식

```json
{
  "predicted_disease": "여드름",
  "confidence": 0.82,
  "differentials": ["지루성 피부염"],
  "needs_human_review": false
}
```

## 6. 완료 기준

- 이미지 1장 기준 최소 추론 가능
- JSON strict parsing 가능
- LoRA adapter 결합 구조 확인 완료
- 챗봇이 호출 가능한 진단 결과 포맷 확보
