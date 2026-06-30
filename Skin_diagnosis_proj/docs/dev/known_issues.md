# Known Issues

- `Validation` 데이터를 다시 `val/test`로 나누는 임시 split 정책을 사용 중이다. 별도 독립 test set이 없으므로 향후 분리 전략을 재검토해야 한다.
- `transformers` 업그레이드 과정에서 `streamlit` 관련 dependency warning(`packaging`, `rich`, `tenacity`)이 발생했다. 현재 04 실행에는 직접 영향이 없지만 환경 정리는 필요하다.
- Windows 환경에서 Hugging Face cache symlink warning이 발생할 수 있다. 현재는 치명적 이슈는 아니며 성능/용량 측면 참고 사항이다.
- 한글 경로/라벨을 터미널에서 출력할 때 인코딩이 깨져 보일 수 있다. 파일 내용 자체는 UTF-8로 저장하고 있다.
- baseline은 `ResNet18`이 아니라 현재 `EfficientNet-B0`를 사용한다. 예전 smoke test 기록과 혼동하지 않도록 주의한다.
- Qwen 계열은 LoRA tiny-step 기록과 QLoRA 본학습 기록이 서로 다른 단계의 산출물일 수 있으므로 metrics 파일 해석 시 실행 시점을 구분해야 한다.
- `outputs/qwen_qlora_phase04/`와 adapter/checkpoint 계열은 로컬 산출물이며 Git에 포함하지 않는다.
