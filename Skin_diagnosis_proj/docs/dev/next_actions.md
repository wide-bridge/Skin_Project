# Next Actions

1. baseline 학습 샘플 수와 epoch를 늘려 1차 성능 추세를 다시 확인한다.
2. `Qwen3-VL-4B-Instruct` LoRA 학습 step과 sample 수를 단계적으로 늘린다.
3. `주사`, `지루`, `여드름`, `아토피` 중심으로 샘플 추론을 여러 장 돌려 혼동 패턴을 확인한다.
4. baseline과 Qwen3-VL 결과를 같은 validation 기준으로 비교한다.
5. 그 다음 단계에서만 FastAPI 연결과 05 RAG를 본격 진행한다.
