# Spike: glTF 왕복 검증 (2026-11-18)

**결론: VCF v0.1의 glTF 설계는 Godot 4.7.2와 Unity 6000.6.8f1(glTFast 6.21.0) 양쪽에서 그대로 동작한다.** 스켈레톤·스킨·클립·팔레트 텍스처·얼굴 데칼 모두 에디터 import와 런타임 로드에서 통과했다. 스펙 수정은 세 가지(extras 의존 제거, 데칼 오프셋, 엔진별 주의사항)뿐이다.

## 무엇을 만들었나

스펙 데이터(`sd_v1.skeleton.json`, `palette-roles.json`)만으로 외부 라이브러리 없이 GLB 두 개를 생성했다.

| 파일 | 내용 |
| --- | --- |
| `spike_baked.glb` | 단일 스킨드 메시, 조인트 36개(웨이트 1.0), 피스 23개 / 276 삼각형, 256×1 팔레트 텍스처(nearest), 얼굴 데칼 쿼드(RGBA, alpha MASK), 클립 `walk`·`idle`(30 fps, 1초) — 50 KB |
| `spike_part.glb` | 스킨 없는 피스 노드 2개(모델 공간 정점), 노드 `extras` = `{bone, piece, slot}` |

팔레트 shade 색은 스펙 5절 공식(OKLab에서 L만 이동)으로 계산했다.

## 결과

| 검사 | Godot 4.7.2 | Unity 6.6 + glTFast 6.21 |
| --- | --- | --- |
| 에디터 import | 통과 (PackedScene) | 통과 (GltfImporter) |
| 런타임 로드 | 통과 (`GLTFDocument`) | 통과 (`GltfImport`) |
| 뼈 36개, 레스트 위치 | 통과 (Head = 0.5625 m) | 통과 |
| 좌우 방향 | 왼손 +X (glTF 그대로) | 왼손 −X (glTFast가 X 반전, 캐릭터 기준 왼쪽 유지) |
| 휴머노이드 매핑 | `SkeletonProfileHumanoid` 필수 뼈 전부 존재 | `AvatarBuilder` 로 Humanoid Avatar 생성: valid, isHuman (21개 매핑) |
| 클립 | `walk`, `idle`, 길이 1.0 s | `walk`, `idle` (기본 Legacy) |
| 포즈 샘플 (walk 0.25 s) | LeftUpperLeg 29.8° | LeftUpperLeg 29.8° |
| 팔레트 텍스처 필터 | Nearest | Point |
| 얼굴 데칼 | alpha scissor, z-fighting 없음 | alpha cutoff 0.5, z-fighting 없음 |
| 노드 `extras` | 메타 `extras` 로 보존 | **버려짐** (노드 이름만 남음) |

![Godot 렌더: 레스트, walk 정면, walk 측면](gltf-roundtrip-godot.png)

![Unity 렌더: walk 측면, walk 정면, 레스트](gltf-roundtrip-unity.png)

## 발견 사항과 조치

1. **glTFast는 노드 `extras` 를 읽지 않는다.** SDK는 피스→뼈 매핑을 `extras` 에서 얻으면 안 된다. → 스펙 8절: 매핑은 `part.json` 의 `pieces[].bone` 이 기준이고, GLB 노드 이름 = 피스 이름. `extras` 는 참고용으로 격하.
2. **얼굴 데칼은 머리 앞면에서 0.05복셀 띄우면** 두 엔진 모두 z-fighting이 없었다. → 스펙 6.3절에 오프셋 명시.
3. **glTFast는 클립을 기본 Legacy로 가져온다.** Humanoid 리타깃을 쓰려면 importer의 Animation Method를 Mecanim으로 바꾸거나 런타임 `ImportSettings.AnimationMethod` 를 지정해야 한다. → 스펙 13절(엔진별 참고).
4. **Unity 에디터에서 런타임 API(`GltfImport`)를 쓸 때** 기본 defer agent가 `DontDestroyOnLoad` 를 호출해 예외가 난다. `UninterruptedDeferAgent` 를 넘기면 해결. → 스펙 13절.
5. **Unity 렌더 색이 Godot보다 옅다.** 새 프로젝트 기본 색 공간(Gamma) 때문으로 추정한다. Unity SDK는 Linear 색 공간과 sRGB 팔레트 텍스처를 전제로 하고, 팔레트 전용 셰이더로 확인해야 한다. → 스펙 13절, Unity SDK 계획의 검증 항목.

## 아직 검증하지 않은 것

- 외부 Humanoid 클립(Mixamo 등)을 `sd_v1` 에 리타깃했을 때의 품질 (특히 짧은 팔이 머리를 뚫는지).
- URP/Godot용 팔레트 전용 셰이더와 런타임 재색칠(팔레트 텍스처 교체).
- 스프링 물리(꼬리·귀·치마 보조 뼈).
- 실제 그리디 메싱 결과의 정점 수 (스파이크는 박스만 사용).

## 재현

스파이크 스크립트는 로컬 `.artifact/spikes/` 에 있다(커밋 안 됨): `gltf-roundtrip/make_glb.py`, `godot-check/check.gd`·`render.gd`, `unity-check/staging/Check.cs`. 이 로직은 `packages/core` 의 glTF writer와 SDK 테스트로 옮겨 정식화한다.
