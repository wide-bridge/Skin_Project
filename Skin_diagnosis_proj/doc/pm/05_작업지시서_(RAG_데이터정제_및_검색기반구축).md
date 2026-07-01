# 05 작업지시서 (RAG 데이터정제 및 검색기반구축)

## 1. 목적

baseline 진단 결과를 설명과 상담으로 확장하기 위한 RAG 기반을 구축한다.

이번 05 단계의 목표는 아래와 같다.

- baseline이 예측한 질환 후보를 기준으로 관련 문서를 검색할 수 있는 retrieval 구조 확립
- `label_data` 우선 원칙으로 dermatology / plastic corpus를 실제 데이터로 정제
- 피부질환 설명용과 성형/미용 상담용 corpus를 분리 유지
- 06 단계 서비스 응답에 바로 연결할 수 있는 검색 결과 구조 확보

## 2. 선행 조건

- 04 단계에서 1차 진단 엔진을 baseline(`EfficientNet-B0`)으로 결정 완료
- 03 단계의 데이터 계층 원칙 확정 완료
- RAG는 `label_data` 우선 사용 원칙 확정 완료

## 3. 범위

### In Scope

- dermatology RAG corpus
- plastic/cosmetic RAG corpus
- baseline 예측 질환 기준 retrieval 구조
- 질환명 mapping 및 canonical label 반영
- 단순 필터 + 점수화 기반 초기 retriever

### Out of Scope for Now

- 고급 reranker 실험
- 벡터 DB 운영 고도화
- HITL 리뷰 화면 연결
- 챗봇 대화 메모리 고도화

## 4. 핵심 구현 방향

- 입력 이미지 자체를 RAG에 넣지 않고, baseline 추론 결과를 retrieval query로 사용한다.
- `predicted_disease`, `differentials`, `confidence`를 바탕으로 관련 dermatology 문서를 우선 검색한다.
- 피부질환 corpus와 plastic corpus는 분리 유지하며, 혼합 검색은 하지 않는다.
- 첫 단계는 단순 규칙 기반 retrieval로 시작하고, 이후 필요 시 embedding 검색으로 확장한다.

## 5. 핵심 산출물

- `rag_corpus_derma.jsonl`
- `rag_corpus_plastic.jsonl`
- `rag_label_source_diff_report.jsonl`
- baseline 예측 결과를 입력으로 받는 최소 retriever 코드
- retrieval 샘플 검토 결과

## 6. 완료 기준

- `label_data` 기준 corpus 생성 정책 문서화 완료
- dermatology / plastic corpus 분리 완료
- baseline 예측 질환 후보 기준 최소 retrieval 동작 확인
- 검색 결과를 06 서비스 응답에 전달할 수 있는 구조 확보
- 질환별 설명 샘플 검토 가능
