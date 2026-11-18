# spec — Voxel Character Format (VCF) v0.1

웹 툴, 생성 도구, 엔진 SDK가 공유하는 계약. 모든 구현은 이 폴더를 기준으로 한다.

| 파일 | 내용 |
| --- | --- |
| [character-format.md](character-format.md) | 포맷 명세 본문 (좌표계, 스켈레톤, 슬롯, 색, 파츠, 팩, 번들, 버전, SDK 요구사항) |
| [sd_v1.skeleton.json](sd_v1.skeleton.json) | 스켈레톤 `sd_v1`: 뼈 계층, 레스트 위치(복셀), 휴머노이드 매핑, 좌우 대칭 쌍 |
| [slots.json](slots.json) | 파츠 슬롯: 허용 뼈, 범위, 레이어, 대칭, 기본 몸 피스 |
| [palette-roles.json](palette-roles.json) | 색 역할과 shade 규칙 |
| [schemas/](schemas/) | JSON Schema (draft 2020-12): 캐릭터, 파츠, 팩 매니페스트, 번들 매니페스트 |
| [examples/](examples/) | 스키마별 예시 |

검사: `python -I scripts/check_spec.py` (`scripts/verify.sh` 에 포함). 스키마 유효성, 예시·샘플 검증, 스켈레톤·슬롯·색 역할 사이의 일관성을 확인한다.

스펙을 바꿀 때는 `schemaVersion` 을 올리고, 이전 버전 파일을 위한 마이그레이션을 `packages/core` 에 추가한다(명세 11절).
