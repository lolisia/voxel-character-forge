#!/usr/bin/env bash
# Repository verification entry point: build + test every component.
# The pipeline runs this as `global_verify` after each task and after integration.
# Add one block per component; keep it deterministic and non-interactive (Windows Git Bash too).
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n== %s\n' "$*"; }

PY=python
command -v "$PY" >/dev/null 2>&1 || PY=python3

step "data: JSON files parse"
"$PY" -I - <<'PYEOF'
import json, pathlib, sys
bad = []
for p in pathlib.Path(".").rglob("*.json"):
    if any(part.startswith(".") for part in p.parts) or "Library" in p.parts:
        continue
    try:
        json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        bad.append(f"{p}: {e}")
if bad:
    print("\n".join(bad)); sys.exit(1)
print("json: ok")
PYEOF

step "spec: schemas, data consistency, samples"
"$PY" -I scripts/check_spec.py

# step "tools: test"
# (cd tools && "$PY" -m pytest -q)

echo "verify: ok"
