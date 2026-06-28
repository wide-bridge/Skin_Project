# 05_작업지시서_(RAG_데이터정제_및_검색기반구축)

## 1. 목적

2차 구현으로 진단 결과 설명과 일반 상담에 활용할 RAG 기반을 구축한다.

이번 05 단계의 목표는 아래와 같다.

- 피부질환/성형 Q&A corpus 정제
- `label_data` 우선 RAG corpus 구축 원칙 반영
- 질환 설명용, 일반 피부상담용, 성형상담용 corpus 분리
- 후속 챗봇 응답에 연결 가능한 검색 기반 확보

## 2. 선행 조건

- 03 단계의 데이터 계층 원칙 확정 완료
- RAG는 `label_data` 우선 사용 원칙 확정 완료

## 3. 범위

### In Scope

- dermatology RAG corpus
- plastic/cosmetic RAG corpus
- 질환 설명용 retrieval 구조
- 질환명 mapping 반영

### Out of Scope for Now

- UI 검색 경험 고도화
- HITL 리뷰 화면 연결
- 고급 reranker 실험

## 4. 핵심 산출물

- `rag_corpus_derma.jsonl`
- `rag_corpus_plastic.jsonl`
- `rag_label_source_diff_report.md`
- 최소 retrieval test 결과

## 5. 완료 기준

- `label_data` 기준 corpus 생성 정책 문서화 완료
- dermatology / plastic corpus 분리 완료
- 검색 가능한 최소 RAG 기반 확보
- 챗봇이 조회 가능한 형태의 문서 구조 확보
