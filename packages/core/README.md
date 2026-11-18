# packages/core — `@vcf/core`

VCF 포맷의 기준 구현 (TypeScript, 브라우저·Node 공용). 웹 툴과 로컬 서버가 이 패키지만 통해 포맷을 다룬다.

## 책임

- `spec/` 데이터(스켈레톤, 슬롯, 색 역할)와 JSON Schema를 읽어 타입·검증기 제공
- 캐릭터 정의 검증·정규화, 버전 마이그레이션 (`spec/character-format.md` 11절)
- `.vox` 읽기/쓰기, 축 변환 (2.1절)
- 복셀 → 메시 베이크: 그리디 메싱, 평면 노멀, 팔레트 UV (6.4절)
- 팔레트 계산: OKLab shade, 256×1 팔레트 텍스처 (5절)
- glTF 2.0 writer: 파츠 GLB, 베이크 캐릭터 GLB (8·10절)
- `.vcpack` / `.vcbundle` zip 읽기/쓰기, 매니페스트 검증
- 파츠 검증기: 슬롯 범위, 허용 뼈, 겹침·z-fighting, 가림 규칙 (4절)

## 하지 않는 것

- DOM, three.js, 네트워크 접근 (순수 로직만)
- LLM 호출 (`apps/server` 담당)

## 규칙

- `spec/` 은 읽기 전용이다. 스펙과 다르게 구현해야 하면 작업을 멈추고 보고한다.
- 공개 API가 바뀌면 `apps/web`, `apps/server` 도 함께 고친다 (파이프라인 `contract_paths`).

## 검증

`npm run build -w @vcf/core`, `npm run test -w @vcf/core` (vitest). `scripts/verify.sh` 가 workspace 전체를 실행한다.
