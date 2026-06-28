# 00 작업지시서: GitHub 연결 및 프로젝트 기반 설정

## 목표
- `Skin_Project`를 상위 mono-repo로 관리한다.
- `Skin_wrinkle_proj`를 새 주름 분석 프로젝트의 작업 루트로 사용한다.
- 로컬/원격 구조, 기본 폴더, Git 추적 정책을 고정한다.

## 현재 결정
- 상위 repo: `D:\vibe_coding\codex\Skin_Project`
- 원격 repo: `https://github.com/wide-bridge/Skin_Project`
- 하위 프로젝트:
  - `Skin_Proj`
  - `Skin_wrinkle_proj`
  - `Skin_diagnosis_proj`

## 이번 단계 작업
1. `Skin_Project` 루트 Git 초기화 및 origin 연결
2. 기존 하위 독립 repo 흔적 제거 (`Skin_Proj/.git`)
3. `Skin_wrinkle_proj` 기본 폴더 구조 생성
4. 루트 `.gitignore` 초안 적용

## Git 원칙
- 상위 `Skin_Project`만 Git repo로 관리한다.
- 하위 프로젝트는 개별 repo로 두지 않는다.
- 출력물, 체크포인트, 로컬 설정, 대용량 중간 산출물은 커밋하지 않는다.

## 완료 기준
- `Skin_Project` 루트에서 `git status`가 정상 동작한다.
- `origin`이 `wide-bridge/Skin_Project`로 연결된다.
- `Skin_wrinkle_proj`에 기본 작업 폴더가 준비된다.
