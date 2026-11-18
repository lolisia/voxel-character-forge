# apps/web — 캐릭터 에디터

브라우저 기반 캐릭터 생성 툴 (TypeScript + Vite + three.js). 포맷 처리는 모두 `@vcf/core` 를 쓴다.

## 기능 (계획)

- 슬롯별 파츠 선택, 역할별 색 선택, 체형 파라미터
- 3D 미리보기: 회전, 표정 전환, 애니메이션 재생
- Import: `.vchar.json`, `.vcbundle` (팩은 라이브러리에 추가)
- Export: `.vchar.json`, `.vcbundle` (파츠 서브셋 팩 + 애니메이션 + 선택적 베이크 GLB)
- 파츠 생성 UI: 프롬프트 → 서버의 생성 루프 → 미리보기 → 승인 (`apps/server` 연동)

## 검증

`npm run build -w @vcf/web`, `npm run test -w @vcf/web` (vitest, 로직 위주). 브라우저 확인은 수동.
