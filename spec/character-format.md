# Voxel Character Format (VCF) v0.1

웹 툴, 생성 도구, 엔진 SDK(Godot, Unity) 사이의 계약. 이 문서와 같은 폴더의 데이터 파일·JSON Schema가 기준이며, 코드가 이 문서와 다르면 코드가 틀린 것이다.

- 상태: 초안 (v0.1.0). v1.0 전까지 하위 호환을 보장하지 않는다.
- 키워드 MUST / SHOULD / MAY 는 RFC 2119 의미로 쓴다.

## 1. 구성 요소 한눈에 보기

| 이름 | 파일 | 누가 만드나 | 누가 읽나 |
| --- | --- | --- | --- |
| 스켈레톤 | `spec/sd_v1.skeleton.json` | 스펙 (고정) | 모두 |
| 슬롯 정의 | `spec/slots.json` | 스펙 (고정) | 웹 툴, 생성 도구, SDK |
| 색 역할 | `spec/palette-roles.json` | 스펙 (고정) | 모두 |
| 캐릭터 정의 | `*.vchar.json` | 웹 툴, 게임 | 웹 툴, SDK |
| 파츠 팩 | `*.vcpack` (zip) | 웹 툴, 생성 도구 | 웹 툴, SDK |
| 내보내기 번들 | `*.vcbundle` (zip) | 웹 툴 | 웹 툴(import), SDK |
| 베이크 GLB | `character.glb` | 웹 툴 | 아무 엔진 (SDK 불필요) |

두 가지 사용 방식을 지원한다.

1. **런타임 조립 (SDK 사용):** 캐릭터 정의 + 파츠 팩 + 애니메이션을 SDK가 읽어 게임 안에서 조립한다. 게임 내 커스터마이즈가 가능하다.
2. **정적 사용 (SDK 없음):** 웹 툴이 캐릭터 하나를 스킨드 메시 + 애니메이션이 든 GLB로 굽는다. glTF 2.0을 읽는 모든 엔진에서 바로 쓴다.

## 2. 좌표계와 단위

- glTF 2.0 규약을 따른다: 오른손 좌표계, **+Y 위**, 단위 미터.
- 캐릭터는 **+Z를 바라본다**. 캐릭터의 왼쪽은 **+X**다.
- **복셀 1개 = 1/64 m (0.015625 m).** 기준 체형의 키(발바닥~정수리, 귀·머리장식 제외)는 64복셀 = 1.0 m.
- 원점은 두 발 사이 바닥(발바닥 높이)이다.
- 스펙 데이터 파일의 위치 값은 모두 **모델 공간 복셀 단위**다. 미터 변환은 `× 0.015625`.
- 레스트 포즈는 **T 포즈**이며, 모든 뼈의 레스트 회전은 항등(identity)이다. 따라서 뼈의 레스트 월드 변환은 위치만으로 정해진다.

### 2.1 MagicaVoxel(.vox) 축 변환

`.vox` 는 Z-up 오른손 좌표계다. 피스의 복셀 좌표 `(vx, vy, vz)` 는 다음과 같이 모델 공간으로 옮긴다.

```
model = origin + (vx, vz, -vy)        // origin: 피스의 `origin` 값 (복셀 단위)
```

즉 MagicaVoxel에서 캐릭터 정면은 -Y 방향(기본 정면 뷰에서 카메라를 향함)이다. 복셀 `(vx, vy, vz)` 는 모델 공간에서 `[x, x+1] × [y, y+1] × [z-1, z]` 정육면체를 차지한다.

## 3. 스켈레톤 `sd_v1`

정의: `spec/sd_v1.skeleton.json`.

- 휴머노이드 뼈 이름은 Unity `HumanBodyBones` 및 Godot `SkeletonProfileHumanoid` 의 이름과 **같다**. 따라서 두 엔진의 휴머노이드 리타깃 매핑은 이름 그대로 1:1이다.
- 손가락 뼈는 없다(벙어리장갑 손). Unity Humanoid 아바타는 손가락 없이 유효하다.
- 보조 뼈(`Ear_L`, `Tail_01` 등)는 휴머노이드 매핑에 들어가지 않으며, 스프링 물리나 전용 애니메이션으로 움직인다.
- 소켓(`Socket_*`)은 무기·장비를 붙이는 뼈다. 애니메이션은 소켓을 키로 잡지 않는다(SHOULD NOT).
- 각 뼈의 `head` 는 레스트 포즈에서 뼈 원점의 모델 공간 복셀 좌표다.

### 3.1 체형 파라미터

캐릭터 정의의 `body` 로 몇 가지만 바꾼다. 범위를 벗어난 값은 범위로 잘라낸다(clamp).

| 키 | 범위 | 기본 | 적용 |
| --- | --- | --- | --- |
| `height` | 0.85 ~ 1.15 | 1.0 | `Root` 균일 스케일 |
| `headScale` | 0.85 ~ 1.20 | 1.0 | `Head` 균일 스케일 (자식 포함) |

## 4. 슬롯

정의: `spec/slots.json`. 슬롯은 "어느 뼈에, 어느 범위 안에" 붙는 파츠 자리다.

- 슬롯마다 `bounds`(모델 공간 복셀 AABB, `[min, max)`)가 있다. 파츠의 모든 복셀은 이 안에 있어야 한다(MUST). `weapon_*` 슬롯은 소켓 기준 상대 범위다.
- `required: true` 슬롯(`body`, `head`)은 캐릭터 정의에서 비울 수 없다.
- `mirror: true` 슬롯(예: `sleeve`, `ears`)의 파츠는 왼쪽 피스만 저장해도 되며, 툴이 X를 뒤집어 오른쪽 피스를 만든다. 뒤집은 피스는 `_L` → `_R` 뼈에 붙는다.
- `layer` 는 그리기·겹침 우선순위다. 숫자가 클수록 바깥쪽이다.

### 4.1 기본 몸(`body`)과 가림 규칙

기본 몸은 부위별 피스로 나뉜다(`torso`, `upperarm_l`, `lowerarm_l`, `hand_l`, `upperleg_l`, …; 목록은 `slots.json` 의 `body.pieces`).

- 파츠는 `hidesBodyPieces` 로 덮어 가리는 몸 피스를 숨긴다. 예: 긴 바지는 `upperleg_*`, `lowerleg_*` 를 숨긴다. 가려진 피스가 원래 보여야 할 피부는 파츠가 직접 포함한다.
- 파츠는 `hidesSlots` 로 다른 슬롯 전체를 숨길 수 있다. 예: 풀페이스 투구는 `hair_front`, `ears` 를 숨긴다.
- 파츠는 `occupies` 로 자기 슬롯 외에 다른 슬롯을 차지할 수 있다. 예: 원피스는 `top` 에 들어가며 `bottom` 을 차지한다. 차지된 슬롯에는 다른 파츠를 넣을 수 없다.
- 숨겨지지 않은 서로 다른 피스의 복셀이 같은 칸을 차지하거나 면이 같은 평면에서 겹치면 안 된다(MUST NOT, z-fighting 방지). 바깥 레이어 파츠는 안쪽 피스보다 최소 1복셀 바깥에 있어야 한다. 툴의 검증기가 이를 검사한다.

## 5. 색: 팔레트 인덱스와 역할

정의: `spec/palette-roles.json`.

복셀과 얼굴 텍스처는 RGB가 아니라 **팔레트 인덱스(1~255, 0 = 빈칸)** 를 저장한다.

```
index = 1 + role * 4 + shade        // role 0..62, shade 0..3  → index 1..252
```

역할 63은 쓰지 않는다(인덱스가 255를 넘는다). 인덱스 253~255는 예약이다.

| shade | 의미 | 기본 색 대비 OKLCH 명도(L) |
| --- | --- | --- |
| 0 | 기본 | ±0 |
| 1 | 그늘 | −0.10 |
| 2 | 깊은 그늘 | −0.20 |
| 3 | 하이라이트 | +0.08 |

- **역할 0~31: 재색칠 가능.** 캐릭터 정의의 `palette` 가 역할별 기본 색을 준다. 없는 역할은 `palette-roles.json` 의 `default` 색을 쓴다.
- **역할 32~62: 고정 색.** 파츠마다 `fixedColors` 에 역할별 기본 색을 정한다. 캐릭터가 바꿀 수 없다.
- shade 색은 기본 색에서 위 표대로 OKLCH 명도만 바꿔 계산한다(채도·색상 유지, L은 [0,1]로 clamp). 결과는 sRGB로 변환한다.
- 파츠는 shade 색을 직접 지정할 수 있다: `shadeOverrides`.

### 5.1 팔레트 텍스처

런타임 셰이더는 256×1 sRGB 텍스처 하나로 색을 칠한다. 텍스처의 x = 팔레트 인덱스, 텍스처 필터는 point(nearest)다.

- 캐릭터마다 팔레트 텍스처가 하나다. 이 텍스처는 재색칠 역할을 담고, 고정 색 역할은 파츠별 색을 담는다. 같은 고정 역할을 두 파츠가 다른 색으로 쓰면 SDK는 파츠별 텍스처를 쓸 수 있다(MAY).
- 메시의 `TEXCOORD_0` 는 `((index + 0.5) / 256, 0.5)` 이다.

## 6. 파츠

파츠 = 메타(`part.json`) + 피스 1개 이상. 피스 하나는 정확히 뼈 하나에 강체로 붙는다(스킨 웨이트 1.0).

### 6.1 파츠 ID

- 형식: `<pack>:<name>`. 예: `core:hair_bob_01`.
- `pack`, `name` 은 `^[a-z0-9][a-z0-9_]*$`, 64자 이하.
- 같은 팩 안에서 `name` 은 유일하다.

### 6.2 피스 종류

| `kind` | 원본 | 베이크 결과 | 용도 |
| --- | --- | --- | --- |
| `voxel` | `.vox` (모델 1개) | 메시 (GLB 노드) | 대부분의 파츠 |
| `decal` | 인덱스 PNG (8비트, 0 = 투명) | 쿼드 메시 + 텍스처 | 얼굴 |

`voxel` 피스의 `origin` 은 `.vox` 격자 원점의 모델 공간 복셀 좌표다(2.1절).

### 6.3 얼굴 (`face` 슬롯)

- 얼굴은 `decal` 피스 하나와 표정 프레임 여러 개다. 쿼드 위치는 머리 파츠가 정한 `faceRect` 를 따른다.
- 원본은 8비트 인덱스 PNG 아틀라스이며, 같은 팔레트 규칙(5절)으로 칠한다. 그래서 눈동자 색(`eye` 역할)을 바꿀 수 있다.
- 해상도: 얼굴 1복셀당 4픽셀. 기본 `faceRect` 20×12복셀 → 프레임 80×48 픽셀.
- 쿼드는 `faceRect.z` 평면에서 +Z로 **0.05복셀** 떨어뜨려 놓는다(z-fighting 방지, Godot·Unity에서 검증).
- 베이크 GLB에서 얼굴 재질은 `alphaMode: MASK`, `alphaCutoff: 0.5` 다.
- 필수 표정: `neutral`, `blink`. 권장: `smile`, `angry`, `sad`, `surprised`, `hurt`.

### 6.4 메시 베이크 규칙

웹 툴(`packages/core`)만 `.vox` → 메시 변환을 한다. SDK는 베이크된 메시만 읽는다.

- 같은 팔레트 인덱스를 가진 인접 면은 그리디 메싱으로 합친다(MUST 아님, SHOULD).
- 면 노멀은 평면(flat)이다. 정점은 면끼리 공유하지 않는다.
- 숨겨진 면(같은 피스 안에서 맞닿은 면)은 만들지 않는다.
- 정점 위치는 모델 공간 미터다(레스트 포즈). SDK가 피스를 뼈에 붙일 때 로컬 오프셋은 `−bone.head × 0.015625` 다(레스트 회전이 항등이므로).

## 7. 캐릭터 정의 (`*.vchar.json`)

스키마: `spec/schemas/character.schema.json`. 예시: `samples/characters/fox_miko.vchar.json`.

```json
{
  "format": "vcf.character",
  "schemaVersion": "0.1.0",
  "skeleton": "sd_v1",
  "name": "Fox Miko",
  "body": { "height": 1.0, "headScale": 1.05 },
  "parts": { "body": "core:body_base_01", "head": "core:head_round_01", "hair_front": "core:hair_bob_bangs_01" },
  "palette": { "skin": "#F6D7C3", "hair1": "#F2C27A" },
  "face": { "default": "neutral" },
  "requires": [ { "pack": "core", "version": "^0.1.0" } ]
}
```

- `parts` 의 키는 슬롯 이름, 값은 파츠 ID 또는 `null`(빈 슬롯).
- `palette` 의 키는 재색칠 역할 이름(0~31), 값은 `#RRGGBB` sRGB.
- `requires` 는 이 캐릭터가 쓰는 팩과 버전 범위(semver)다. 툴은 내보낼 때 자동으로 채운다.
- `extensions` 객체에는 게임별 데이터를 넣는다. 리더는 모르는 키를 보존해야 한다(MUST).

## 8. 파츠 팩 (`*.vcpack`)

zip 파일. 스키마: `spec/schemas/pack-manifest.schema.json`, `spec/schemas/part.schema.json`.

```
manifest.json
parts/<slot>/<name>/part.json
parts/<slot>/<name>/<piece>.vox          # voxel 원본 (선택: 런타임 팩에서는 생략 가능)
parts/<slot>/<name>/<piece>.png          # decal 원본
parts/<slot>/<name>/part.glb             # 베이크 메시 (필수)
previews/<name>.png                      # 썸네일 128×128 (선택)
```

- `part.glb` 에는 피스마다 노드 하나가 있다. **노드 이름 = 피스 이름**(`part.json` 의 `pieces[].name`).
- 피스 → 뼈 매핑의 기준은 `part.json` 의 `pieces[].bone` 이다. SDK는 이것을 써야 한다(MUST).
- 노드 `extras` = `{ "bone": "...", "piece": "...", "slot": "..." }` 는 참고용으로 쓴다(SHOULD). Unity glTFast는 `extras` 를 버리므로, SDK가 `extras` 에 의존하면 안 된다(MUST NOT).
- decal 피스의 텍스처는 인덱스 값을 R 채널에 담은 PNG(`R = index`, `A = 0` 이면 투명)로 GLB에 넣는다.
- 원본(`.vox`)이 있는 팩만 웹 툴에서 편집할 수 있다. 런타임 배포용 팩은 원본을 빼도 된다(`manifest.editable: false`).

## 9. 애니메이션

- 애니메이션 팩은 `sd_v1` 스켈레톤 노드를 가진 GLB이며, 클립 = glTF animation.
- 클립은 제자리(in-place)다. 루트 모션은 v0 범위 밖이다.
- 샘플링 30 fps, 보간은 LINEAR(회전은 쿼터니언 선형 → 엔진이 slerp).
- 표준 클립 이름: `idle`, `walk`, `run`, `jump_start`, `jump_loop`, `land`, `hit`, `die`, `attack_1h`, `attack_2h`, `cast`, `emote_wave`. 게임은 이 밖의 이름을 자유롭게 추가한다.
- 보조 뼈(꼬리·귀·치마)는 클립에 넣지 않는 것을 권장한다(SHOULD NOT). SDK의 스프링 물리가 움직인다.

## 10. 내보내기 번들 (`*.vcbundle`)

웹 툴의 export 결과. zip 파일. 스키마: `spec/schemas/bundle-manifest.schema.json`.

```
bundle.json                 # 번들 매니페스트
characters/<id>.vchar.json  # 캐릭터 1개 이상
packs/<pack>.vcpack         # 쓰인 파츠만 담은 팩 (또는 전체 팩)
animations/<name>.glb       # 애니메이션 팩
baked/<id>.glb              # 선택: 캐릭터별 정적 GLB (6.4 + 5.1 텍스처 내장)
previews/<id>.png           # 선택: 캐릭터 썸네일
```

- **Import:** 웹 툴은 `.vchar.json` 단독(필요한 팩이 라이브러리에 있어야 함)과 `.vcbundle` 둘 다 읽는다. 번들 안의 팩은 라이브러리에 추가하며, 같은 팩·같은 버전이 이미 있으면 건너뛴다.
- **베이크 GLB:** 단일 스킨드 메시, 조인트 = 스켈레톤 전체, 웨이트 1.0, 팔레트를 구운 텍스처 하나, 재질은 glTF 기본 PBR(metallic 0, roughness 1)과 `KHR_materials_unlit`(선택). 애니메이션 클립을 함께 넣을 수 있다.

## 11. 버전과 마이그레이션

- `schemaVersion` 은 semver다. 리더는 **같은 major**만 읽는다. 0.x 동안은 minor가 major처럼 취급된다.
- 웹 툴은 이전 버전 파일을 import할 때 마이그레이션 함수를 순서대로 적용한다(`0.1 → 0.2 → …`). 마이그레이션 함수는 `packages/core` 에 둔다.
- 팩은 자체 `version`(semver)을 가진다. 파츠를 지우거나 슬롯을 바꾸면 major를 올린다.

## 12. SDK 최소 요구 기능

각 엔진 SDK는 다음을 제공해야 한다(MUST).

1. `.vcpack` 과 `.vcbundle` 로드 (엔진 에디터 import + 런타임 로드).
2. `sd_v1` 스켈레톤 생성 및 엔진 휴머노이드 매핑(Unity Avatar, Godot SkeletonProfileHumanoid).
3. 캐릭터 정의 → 조립: 피스 부착, 가림 규칙(4.1) 적용, 체형 파라미터 적용.
4. 팔레트 텍스처 생성(5절)과 팔레트 셰이더/재질.
5. 슬롯 단위 교체 API와 팔레트 변경 API (전체 재조립 없이).
6. 얼굴 표정 전환 API.
7. 캐릭터 정의 직렬화(게임 세이브용) — 7절 형식 그대로.

SHOULD: 피스 병합(드로우콜 축소), 보조 뼈 스프링 물리.

## 13. 엔진별 참고 (glTF 왕복 검증 결과)

근거: `documents/spikes/gltf-roundtrip.md` (Godot 4.7.2, Unity 6000.6.8f1 + glTFast 6.21.0).

- **좌표:** Godot은 glTF 축을 그대로 쓴다. glTFast는 X를 반전해 Unity 왼손 좌표계로 바꾸며, 캐릭터는 +Z를 보고 왼쪽 손은 −X에 온다(캐릭터 기준 좌우는 유지). SDK는 축을 직접 바꾸지 않는다.
- **휴머노이드:** Godot `SkeletonProfileHumanoid` 필수 뼈가 전부 같은 이름으로 존재한다. Unity는 `HumanBodyBones` 이름 그대로 `AvatarBuilder.BuildHumanAvatar` 로 유효한 Humanoid Avatar가 만들어진다.
- **Unity 클립:** glTFast는 기본으로 Legacy 클립을 만든다. Humanoid 리타깃이 필요하면 importer의 Animation Method를 Mecanim으로, 런타임에서는 `ImportSettings.AnimationMethod` 를 지정한다.
- **Unity 에디터 도구:** 에디터에서 런타임 API(`GltfImport`)를 쓸 때는 `UninterruptedDeferAgent` 를 넘긴다(기본 agent는 플레이 모드 전용).
- **Unity 색 공간:** SDK는 Linear 색 공간과 sRGB 팔레트 텍스처를 전제로 한다.

## 14. 열린 질문 (v0.2 이전에 결정)

- 파츠 메시 LOD를 둘지 (복셀 해상도 절반 베이크).
- 아웃라인을 메시(뒤집힌 셸)로 구울지, 셰이더로 할지.
- 무기 슬롯 파츠의 크기 상한과 그립 위치 규약.
- 루트 모션 지원 여부.
