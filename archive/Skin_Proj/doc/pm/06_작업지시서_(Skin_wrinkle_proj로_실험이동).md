# 06 작업지시서: Skin_wrinkle_proj로 실험 이동

## 1. 문서 목적
본 문서는 `Skin_Proj` 안의 05 흐름 이후, wrinkle 계열 정확도 검증 실험이 별도 프로젝트 `Skin_wrinkle_proj`로 이동했음을 기록하는 전환 문서이다.

즉 `Skin_Proj`에서는 더 이상 직접 wrinkle 기준선 실험을 이어서 수행하지 않고, 해당 작업은 `Skin_wrinkle_proj`에서 독립적으로 관리한다.

## 2. 이동 배경
`Skin_Proj`의 Qwen3-VL + LoRA 경로는 구조 검증과 collapse 제거까지는 의미가 있었으나, 그 이후 병목은 단순 step 증가보다 데이터 정의와 학습 전략 문제에 가까웠다.

특히 wrinkle 계열은 아래 특성이 강했다.
- 순서형 라벨 구조
- 인접 클래스 경계의 불안정성
- 동일인 누수 여부에 따른 해석 차이
- ROI 기반 고전 비전모델 기준선 검증 필요성

따라서 정확도개선과 능동학습 적용판단을 바로 이어가기보다, 별도 프로젝트에서 단일 타깃 기준선 검증을 먼저 수행하는 것이 더 타당하다고 판단하였다.

## 3. 이동 대상
실험 이동 대상 프로젝트:
- [Skin_wrinkle_proj](D:/vibe_coding/codex/Skin_Project/Skin_wrinkle_proj)

해당 프로젝트에서는 다음을 별도로 관리한다.
- `forehead_wrinkle` 단일 타깃 기준선 검증
- `strict split` 중심 일반화 판단
- `classification / regression / ordinal` 비교
- 이후 wrinkle 계열 확장 여부 판단

## 4. Skin_Proj에서의 의미
이후 `Skin_Proj`에서 wrinkle 관련 작업을 다시 볼 때는, 이 프로젝트 안에서 직접 이어서 구현하지 않고 `Skin_wrinkle_proj`의 작업지시서와 결과를 먼저 참조한다.

즉:
- `Skin_Proj`의 05는 중단
- `Skin_Proj`의 06은 이동 안내
- 실제 실험 관리와 후속 판단은 `Skin_wrinkle_proj/doc/pm`에서 진행

## 5. 참조 위치
실제 실험 내용과 앞으로의 진행 계획은 아래 위치에서 관리한다.
- [Skin_wrinkle_proj/doc/pm](D:/vibe_coding/codex/Skin_Project/Skin_wrinkle_proj/doc/pm)

## 6. 결론
`Skin_Proj`에서 wrinkle 기준선 실험은 여기서 종료하고, 후속 실험은 `Skin_wrinkle_proj`로 이동한다.
본 문서는 그 전환 사실을 기록하는 문서이다.
