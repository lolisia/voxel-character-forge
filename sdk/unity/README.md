# sdk/unity — Unity SDK

Unity 6 UPM 패키지 (`com.lolisia.vcf`). glTFast로 GLB를 읽고 캐릭터를 런타임에 조립한다 (스펙 12절, 13절).

## 구조 (계획)

```
package.json             # UPM 매니페스트 (의존: com.unity.cloud.gltfast)
Runtime/                 # 런타임 어셈블리
Runtime/Core/            # UnityEngine 비의존 순수 로직 (정의 파싱, 가림 규칙, 팔레트 계산)
Editor/                  # 에디터 import (ScriptedImporter 등)
Tests/                   # Unity Test Framework 테스트 (에디터에서 실행)
Tests~/Logic/            # dotnet test 프로젝트: Runtime/Core 소스를 직접 컴파일해 테스트 (Unity가 무시하는 ~ 폴더)
```

## 검증

- 기본 (`scripts/verify.sh`): `Tests~/Logic/*.csproj` 가 있으면 `dotnet test` 를 실행한다. Unity 에디터가 필요 없다.
- Unity 테스트 (선택, Unity SDK 계획에서 추가): `VERIFY_UNITY=1 bash scripts/verify.sh` 일 때만 Unity batchmode로 `Tests/` 를 실행한다. 느리고 라이선스가 필요하므로 기본 게이트에서 제외한다.

## 주의

- `Runtime/Core/` 는 `UnityEngine` 을 참조하지 않는다. 엔진 의존 코드는 `Runtime/` 의 다른 폴더에 둔다.
- 런타임 로드는 `GltfImport` + `ImportSettings.AnimationMethod`, 에디터에서는 `UninterruptedDeferAgent` (스펙 13절).
