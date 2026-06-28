# 03_작업지시서_(데이터정의_및_VLM학습기반정리)

## 1. 목적

피부질환 진단 VLM을 학습하고 추론하기 위한 데이터 계층을 정의한다. 이 단계는 모델 성능 개선보다 `정합성 있는 데이터 구조화`를 우선한다.

## 2. 주요 작업

- 이미지 데이터 구조 파악
- 라벨 JSON 구조 파악
- 질환 ontology 정의
- 이미지 질환명과 Q&A 질환명 매핑
- manifest / split / processed metadata 설계
- VLM 학습용 포맷 정의

## 3. 질환 ontology 원칙

- 이미지 데이터 기준 canonical label을 우선 정의
- Q&A 데이터는 alias 또는 related concept로 연결
- 질환명 불일치는 별도 리포트로 관리
- 텍스트 자산이 부족한 클래스는 `missing_knowledge`로 표시

예시:

- `지루` -> canonical `지루성 피부염`
- `주사` -> canonical `주사`
- `안면홍조` -> `주사`와 동일시하지 않고 related concept로 유지

## 4. 데이터 산출물

- `image_manifest.csv` 또는 `jsonl`
- `train/val/test split`
- `disease_ontology.csv`
- `label_mapping.csv`
- `missing_knowledge_report.md`
- `vlm_train_dataset.jsonl`

## 5. VLM 출력 방향

1차 출력은 자유서술보다 구조화된 JSON을 기본으로 한다.

예시 필드:

```json
{
  "predicted_disease": "주사",
  "confidence": 0.78,
  "differentials": ["안면홍조", "지루성 피부염"],
  "needs_human_review": true
}
```

## 6. 구현 원칙

- 원본 데이터는 복사하지 않고 참조 기반 처리 우선
- split은 leakage 방지 기준 우선
- 질환 ontology는 코드보다 데이터 파일로 관리
- VLM 포맷은 향후 다른 모델에도 재사용 가능해야 함

## 7. 완료 기준

- 데이터 구조 문서화 완료
- 질환 ontology 초안 완료
- VLM 학습용 포맷 초안 완료
- 결손 질환/지식 불균형 리포트 초안 완료
