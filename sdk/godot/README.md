# sdk/godot — Godot 4 SDK

Godot 4.7+ 애드온. `.vcpack` / `.vcbundle` 을 읽어 캐릭터를 런타임에 조립한다 (스펙 12절).

## 구조 (계획)

```
project.godot            # SDK 개발·테스트용 프로젝트 (이 폴더 자체)
addons/vcf/              # 배포 대상 애드온 (GDScript)
tests/run_tests.gd       # headless 테스트 진입점 (SceneTree 스크립트, 실패 시 exit 1)
tests/fixtures/          # 테스트용 팩·번들
```

## 검증

`scripts/verify.sh` 가 `project.godot` 이 있으면 다음을 실행한다.

```
"$GODOT_BIN" --headless --path sdk/godot --script res://tests/run_tests.gd
```

`GODOT_BIN` 기본값: `D:/Godot/Godot_v4.7.2-stable_win64/Godot_v4.7.2-stable_win64_console.exe`.

참고: glTF 런타임 로드는 `GLTFDocument` / `GLTFState` 로 검증됨 (`documents/spikes/gltf-roundtrip.md`).
