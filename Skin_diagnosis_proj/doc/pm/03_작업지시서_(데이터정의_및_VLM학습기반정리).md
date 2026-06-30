# 03_작업지시서_(데이터정의_및_VLM학습기반정리)

## 1. 목적

피부질환 진단 VLM을 학습하고 추론하기 위한 데이터 계층을 정의한다. 이번 단계는 모델 성능 개선보다 `정합성 있는 데이터 구조화`를 우선한다.

이번 03 단계의 목표는 아래와 같다.

- 이미지 데이터 구조와 라벨 구조를 프로젝트 기준으로 고정
- 질환 ontology를 canonical label 기준으로 정의
- 이미지 질환명과 Q&A 질환명을 연결하는 매핑 정책 확정
- baseline vision과 VLM 학습/추론에 공통으로 사용할 산출물 형식 확정
- RAG corpus 생성 기준 확정
- 텍스트 지식 공백과 클래스 불균형 리스크를 별도 관리 대상으로 명시

## 2. 선행 조건

02 단계는 완료 상태를 전제로 한다.

- React + FastAPI 기반 서비스 구조 확정 완료
- VLM / Vision / RAG / HITL 모듈 경계 확정 완료
- 라우팅 규칙 확정 완료
- 04~06 1차 구현 라인 확정 완료

## 3. 현재 확인된 데이터 기준

### 3.1 피부질환 이미지 데이터

현재 이미지 질환 축:

- 건선
- 아토피
- 여드름
- 정상
- 주사
- 지루

현재 실제 산출물 기준:

- `image_manifest.csv` 생성 완료
- 총 행 수: `10800`
- split 컬럼: `original_split`, `model_split`
- 표준 라벨 컬럼: `canonical_label`
- view 컬럼: `frontal`, `side`

### 3.2 피부질환 Q&A 데이터

- 피부질환 Q&A는 이미지 데이터보다 넓은 질환군 포함
- 성형미용 및 재건 Q&A는 별도 축으로 존재
- 이미지 데이터 클래스와 Q&A 질환명이 완전히 일치하지 않음
- RAG 본문 corpus는 `label_data` 우선 사용
- `source_data`는 검증/감사/보완용으로 사용

### 3.3 주요 ontology 이슈

- 이미지 클래스에는 `주사`가 존재
- Q&A에는 `안면홍조`, `안면 홍조증`이 존재
- `주사`와 `안면홍조`는 동일시하지 않음
- `주사`는 canonical label로 유지
- `안면홍조`는 related concept로 유지

## 4. 이번 단계에서 확정한 데이터 원칙

- 이미지 데이터 기준 canonical label 우선
- Q&A는 alias 또는 related concept로 연결
- `label_data`를 RAG 본문 기준으로 사용
- `source_data`는 차이 비교와 누락 보완 검토용
- 질환명 매핑은 코드가 아니라 데이터 파일로 관리
- baseline vision과 VLM은 같은 manifest와 같은 canonical label 체계를 공유한다.

## 5. 산출물 기준

- `image_manifest.csv`
- `disease_ontology.csv`
- `label_mapping.csv`
- `vlm_train_dataset.jsonl`
- `rag_corpus_derma.jsonl`
- `rag_corpus_plastic.jsonl`
- `missing_knowledge_report.md`
- `rag_label_source_diff_report.md`

## 6. 1차 구현과의 연결

이번 단계의 데이터 정의는 아래 1차 구현 라인과 직접 연결된다.

- `04`: baseline/VLM 입력 데이터와 출력 평가의 기준 데이터
- `05`: RAG corpus 생성 기준 데이터
- `06`: API/챗봇 응답에 연결되는 diagnosis/context payload의 기준 데이터

## 7. 완료 기준

아래를 만족하므로 03 단계는 완료 처리 가능 상태다.

- 데이터 구조 문서화 완료
- canonical 질환 ontology 초안 완료
- 이미지/Q&A 매핑 정책 정의 완료
- baseline/VLM 공통 학습 포맷 초안 완료
- RAG용 `label_data` 우선 사용 원칙 기록 완료
- 04~06 구현에 필요한 데이터 기준 정의 완료
