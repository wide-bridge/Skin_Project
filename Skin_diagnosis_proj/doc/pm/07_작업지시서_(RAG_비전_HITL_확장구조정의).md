# 04_작업지시서_(RAG_비전_HITL_확장구조정의)

## 1. 목적

VLM 본체 외에 RAG, Vision, HITL이 어떤 역할로 붙는지 정의하고, 후속 구현 순서를 정리한다.

## 2. 확장 모듈 정의

### 2.1 Diagnosis RAG

- VLM 또는 Vision 결과를 설명하는 용도
- 질환 설명, 감별 포인트, 주의사항, 생활관리 중심
- 진단 모델의 출력 결과를 근거로 호출

### 2.2 General Derma RAG

- 사용자의 일반 피부질환 상담 질문 대응
- 이미지 입력 없이도 작동 가능
- 피부질환 Q&A 코퍼스 기반

### 2.3 Plastic / Cosmetic RAG

- 성형미용 및 재건 질문 대응
- 진단 파이프라인과 분리 운영
- 일반 상담형 경로로 라우팅

### 2.4 Vision Branch

- VLM 외 별도 분류기 또는 비전 인코더 기반 경로
- baseline, fallback, 재검증 목적

### 2.5 HITL

- 불확실한 케이스 검토
- 운영자 피드백 기록
- 고위험 응답 제한
- 후속 데이터 보정 연결

## 3. 라우팅 원칙

- `이미지 전용 요청` -> VLM 우선
- `이미지 + 설명 요청` -> VLM -> Diagnosis RAG
- `텍스트 피부질환 질문` -> General Derma RAG
- `텍스트 성형 질문` -> Plastic RAG
- `불확실한 진단` -> HITL flag
- `필요 시` -> Vision Branch 재확인

## 4. 구현 우선순위

1. VLM
2. Diagnosis RAG
3. General Derma RAG
4. Plastic RAG
5. Vision Branch
6. HITL 세부 운영정책 고도화

## 5. 완료 기준

- 확장 모듈 역할 분리 완료
- 라우팅 규칙 문서화 완료
- 후속 구현 순서 정의 완료
- HITL이 구현 범위임을 명시 완료
