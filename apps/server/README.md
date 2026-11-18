# apps/server — 로컬 백엔드

웹 에디터용 로컬 서버 (Node + TypeScript). 로컬 전용이며 외부 공개를 전제로 하지 않는다.

## 책임 (계획)

- 파츠 라이브러리 저장소: `parts/` 의 팩 읽기/쓰기, 목록·검색 API
- LLM 프록시: API 키는 서버 환경 변수(`.env`)에만 두고 브라우저로 보내지 않는다
- 파츠 생성 루프: 복셀 DSL 생성 → `@vcf/core` 로 복셀화·검증 → 렌더 → 비평 반복
- 이미지 → 3D → 복셀화 경로의 외부 API 호출

## 검증

`npm run build -w @vcf/server`, `npm run test -w @vcf/server` (vitest). 외부 API는 테스트에서 목(mock)으로 대체한다.
