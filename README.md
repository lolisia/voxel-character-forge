# Voxel Character Forge

SD 체형 복셀 캐릭터를 **웹 툴에서 파츠 단위로 생성(LLM/AI)** 하고, **엔진 중립 포맷으로 내보내** 게임에서 **커스터마이즈 가능한 캐릭터로 조립**하는 파이프라인.

- 모든 캐릭터는 하나의 SD 스켈레톤(`sd_v1`)을 공유한다. 애니메이션은 모든 캐릭터가 재사용한다.
- 파츠는 뼈 하나에 강체로 붙는 복셀 덩어리다. 웹 툴이 메시(GLB)로 구워 배포한다.
- 색은 역할 인덱스로 저장하고, 런타임 팔레트로 칠한다.
- 캐릭터 하나 = 파츠 ID + 팔레트를 담은 작은 JSON (`*.vchar.json`).
- 내보내기: `.vcbundle` (SDK로 런타임 조립) 또는 베이크 GLB (SDK 없이 아무 엔진).

포맷 명세: [spec/](spec/) · 설계 배경: [제안서](https://claude.ai/artifact/KNELnxunnKr91FpEQBSvaE) · 검증 기록: [documents/spikes/](documents/spikes/)

## 구조

```
spec/            포맷 명세(VCF), 스켈레톤·슬롯·색 역할 데이터, JSON Schema — 모든 구현의 계약
packages/core/   @vcf/core (TS): 스키마 검증, 마이그레이션, .vox, 메시 베이크, 팔레트, glTF writer, 팩·번들 I/O
apps/web/        캐릭터 에디터 (Vite + three.js): 편집, 미리보기, import/export
apps/server/     로컬 백엔드 (Node): 파츠 라이브러리, LLM 프록시, 생성 루프
sdk/godot/       Godot 4 애드온: 팩·번들 로드, 런타임 조립
sdk/unity/       Unity 6 UPM 패키지 (glTFast): 팩·번들 로드, 런타임 조립
parts/           파츠 라이브러리 (팩 원본)
animations/      sd_v1 애니메이션 팩
samples/         예시 캐릭터 정의
reference/       체형·스타일 레퍼런스 이미지
documents/       설계 문서, spike 기록
scripts/         verify.sh (전체 검증), check_spec.py (스펙 검사)
```

## 생성 경로

| 경로 | 흐름 | 용도 |
| --- | --- | --- |
| A | 텍스트 → LLM 복셀 DSL → 복셀화 → 4방향 렌더 → LLM 비평 루프 | 대부분의 파츠 |
| B | 컨셉 삼면도 → 이미지→3D → 슬롯별 복셀화 → 팔레트 양자화 | 머리카락 등 유기적 형태, 코스튬 세트 |

두 경로 모두 검증기(규격·간섭 검사)와 개발자 승인을 거쳐 `parts/`에 들어간다.

## 로드맵

- [x] 포맷 스펙 v0.1 + JSON Schema
- [x] glTF 왕복 검증 (Godot 4.7, Unity 6.6 + glTFast)
- [ ] 계획 1: `packages/core` — 스키마·메시 베이크·glTF·팩/번들
- [ ] 계획 2: `apps/web` (+ `apps/server`) — 에디터, import/export
- [ ] 계획 3: `sdk/godot`
- [ ] 계획 4: `sdk/unity`
- [ ] 계획 5: 생성 기능 — LLM 복셀 DSL, 이미지→복셀

## 개발

- Node 22 (`.nvmrc`), npm workspaces (`packages/*`, `apps/*`)
- 전체 검증: `bash scripts/verify.sh` — 컴포넌트가 생기면 해당 빌드·테스트가 자동으로 포함된다
- Godot 테스트는 `GODOT_BIN`, Unity 로직 테스트는 .NET SDK가 필요하다

## 저장소 메모

- 이미지·FBX 등 대용량 바이너리는 Git LFS로 관리한다 (`.gitattributes`).
- 클론 후 `git lfs install`을 한 번 실행한다.
