# 피부병변진단보조 및 상담 챗봇 PoC

EfficientNet-B3 기반 피부병변 이미지 분류 모델과 FAISS 기반 RAG 상담 시스템을 결합한 피부진단보조 및 메이크업 상담 챗봇입니다.

본 프로젝트는 사용자가 피부 이미지를 업로드하거나 피부 상태를 질문하면, 이미지 기반 추정 결과와 상담용 지식 데이터를 함께 활용해 피부관리, 메이크업 방법, 병원 상담 필요성을 안내하는 PoC입니다.

## 주요 기능

- 피부 이미지 업로드 기반 피부진단보조
- 정상/건선/아토피/여드름/주사/지루 6개 클래스 분류
- 피부질환 및 병변 관리 상담
- 문제성 피부 메이크업 방법 및 성분 상담
- 병원 방문 권고가 필요한 위험 신호 안내
- FAISS 기반 RAG 검색과 OpenAI LLM 답변 생성
- LLM-as-a-Judge 및 RAGAS 평가 노트북 제공

## RAG 구성

상담 데이터는 두 갈래로 분리해 사용합니다.

- 메이크업 RAG: 문제성 피부 메이크업 추천 데이터
- 피부과 상담 RAG: 전문 의학지식 데이터 중 피부과 QA

앱 실행 시 원본 JSON 데이터를 로드하고, 한국어 문자 n-gram hash embedding을 이용해 FAISS 인메모리 인덱스를 구성합니다. 이 방식은 별도 벡터DB 서버나 SQLite 기반 저장소 없이 실행되므로 PoC 데모 환경에서 안정적으로 동작합니다.

질문 유형에 따라 `makeup`, `medical`, `hybrid`로 라우팅한 뒤 관련 문서를 검색하고, 검색 문맥과 사용자 질문을 OpenAI LLM에 전달해 답변을 생성합니다.

## 실행 방법

API 키는 프로젝트 폴더에 저장하지 않고 아래 경로에서 로드합니다.

`D:/PyProject/env_keys/.env`

필요한 환경변수:

- `OPENAI_API_KEY`
- `HF_TOKEN` 또는 Hugging Face 관련 토큰

```powershell
conda activate skin_vlm
cd D:\vibe_coding\codex\Skin_Project\Skin_diagnosis2
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## 프로젝트 구조

```text
app/          FastAPI 서버, CNN 추론, FAISS RAG, 상담 로직
templates/    HTML UI
static/       CSS/JS 정적 파일
notebooks/    학습 및 상담 RAG 실험 노트북
models/       EfficientNet-B3 체크포인트
reports/      평가 이미지 및 발표용 결과
```

## 평가 요약

- EfficientNet-B3 테스트 정확도: 88.83%
- 측면 이미지 정확도: 99.50%
- 정면 이미지 정확도: 78.17%
- 정면에서 여드름, 주사, 지루 클래스 혼동이 상대적으로 큼
- 일부 오답에서 softmax confidence가 높게 나타나므로 confidence calibration이 필요함

상세 실험 과정과 결과는 `notebooks/`의 ipynb 파일을 참고합니다.

## 주의

본 프로젝트는 의료 확정 진단 서비스가 아니라 피부진단보조 및 상담 PoC입니다. 통증, 급격한 악화, 진물, 출혈, 광범위한 염증, 반복 악화가 있으면 피부과 상담을 권장합니다.
