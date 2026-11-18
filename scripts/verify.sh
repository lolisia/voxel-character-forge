#!/usr/bin/env bash
# Repository verification entry point: build + test every component.
# The pipeline runs this as `global_verify` after each task and after integration.
# Each component block runs as soon as the component exists; a missing toolchain for an
# existing component is a failure, not a skip. Deterministic, non-interactive (Windows Git Bash too).
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n== %s\n' "$*"; }
die() { printf 'verify: %s\n' "$*" >&2; exit 1; }

PY=python
command -v "$PY" >/dev/null 2>&1 || PY=python3

# ---------------------------------------------------------------- data + spec
step "data: JSON files parse"
"$PY" -I - <<'PYEOF'
import json, os, sys
SKIP = {"node_modules", "dist", "coverage", "bin", "obj", "Library", "Temp"}
bad = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP]
    for f in files:
        if f.endswith(".json"):
            p = os.path.join(root, f)
            try:
                with open(p, encoding="utf-8") as fh:
                    json.load(fh)
            except Exception as e:
                bad.append(f"{p}: {e}")
if bad:
    print("\n".join(bad)); sys.exit(1)
print("json: ok")
PYEOF

step "spec: schemas, data consistency, samples"
"$PY" -I scripts/check_spec.py

# ---------------------------------------------------------------- node workspaces (packages/*, apps/*)
has_files() { compgen -G "$1" >/dev/null; }

if has_files 'packages/*/package.json' || has_files 'apps/*/package.json'; then
  step "node: install, build, test (workspaces)"
  [ -f package-lock.json ] || die "workspace packages exist but package-lock.json is missing (run npm install and commit the lockfile)"
  if [ ! -d node_modules ]; then
    npm ci --no-audit --no-fund
  fi
  npm run build --workspaces --if-present
  npm run test --workspaces --if-present
fi

# ---------------------------------------------------------------- Godot SDK
if [ -f sdk/godot/project.godot ]; then
  step "sdk/godot: headless tests"
  GODOT_BIN="${GODOT_BIN:-D:/Godot/Godot_v4.7.2-stable_win64/Godot_v4.7.2-stable_win64_console.exe}"
  [ -x "$GODOT_BIN" ] || die "Godot not found at $GODOT_BIN (set GODOT_BIN)"
  [ -f sdk/godot/tests/run_tests.gd ] || die "sdk/godot/tests/run_tests.gd is missing"
  "$GODOT_BIN" --headless --path sdk/godot --import >/dev/null 2>&1 || true
  "$GODOT_BIN" --headless --path sdk/godot --script res://tests/run_tests.gd
fi

# ---------------------------------------------------------------- Unity SDK (pure logic, no editor)
if has_files 'sdk/unity/Tests~/Logic/*.csproj'; then
  step "sdk/unity: logic tests (dotnet)"
  command -v dotnet >/dev/null 2>&1 || die "dotnet SDK not found"
  dotnet test sdk/unity/Tests~/Logic --nologo
fi
# Unity editor tests (batchmode) are opt-in and added by the Unity SDK plan (VERIFY_UNITY=1).

echo
echo "verify: ok"
