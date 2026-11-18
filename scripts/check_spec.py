"""Static checks for the VCF spec (spec/) and sample data.

Run from the repo root: python -I scripts/check_spec.py
- every schema in spec/schemas is a valid JSON Schema (draft 2020-12)
- spec examples and samples validate against their schemas
- skeleton, slots and palette roles are consistent with each other
- character samples only use known slots, recolorable role names and existing bones
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:  # pragma: no cover
    sys.exit("check_spec: requires `pip install jsonschema` (>= 4.18)")

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec"
errors: list[str] = []


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def err(msg: str) -> None:
    errors.append(msg)


# ---- schemas ---------------------------------------------------------------
schemas = {p.name: load(p) for p in sorted((SPEC / "schemas").glob("*.schema.json"))}
registry = Registry()
for name, s in schemas.items():
    Draft202012Validator.check_schema(s)
    res = Resource.from_contents(s)
    registry = registry.with_resource(s["$id"], res).with_resource(name, res)


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(schemas[name], registry=registry)


def validate(name: str, path: Path) -> dict:
    data = load(path)
    for e in validator(name).iter_errors(data):
        loc = "/".join(str(x) for x in e.absolute_path) or "(root)"
        err(f"{path.relative_to(ROOT)}: {loc}: {e.message}")
    return data


# ---- spec data -------------------------------------------------------------
skel = load(SPEC / "sd_v1.skeleton.json")
slots = load(SPEC / "slots.json")
roles = load(SPEC / "palette-roles.json")

bones = {b["name"]: b for b in skel["bones"]}
if len(bones) != len(skel["bones"]):
    err("skeleton: duplicate bone names")
roots = [b for b in skel["bones"] if b["parent"] is None]
if [b["name"] for b in roots] != ["Root"]:
    err("skeleton: exactly one root bone named Root expected")
for b in skel["bones"]:
    if b["parent"] is not None and b["parent"] not in bones:
        err(f"skeleton: {b['name']} has unknown parent {b['parent']}")
    if b["kind"] == "humanoid" and b["humanoid"] != b["name"]:
        err(f"skeleton: humanoid bone {b['name']} must map to its own name")
    if b["kind"] != "humanoid" and b["humanoid"] is not None:
        err(f"skeleton: non-humanoid bone {b['name']} must have humanoid null")
for left, right in skel["mirror"]:
    if left not in bones or right not in bones:
        err(f"skeleton: mirror pair {left}/{right} references unknown bone")
        continue
    lx, ly, lz = bones[left]["head"]
    rx, ry, rz = bones[right]["head"]
    if (rx, ry, rz) != (-lx, ly, lz):
        err(f"skeleton: {right} head must mirror {left} across x")
    lp, rp = bones[left]["parent"], bones[right]["parent"]
    pairs = {a: b for a, b in skel["mirror"]}
    if lp != rp and pairs.get(lp) != rp:
        err(f"skeleton: parents of {left}/{right} are not mirrored")
# parent must be declared before child (simple load order for SDKs)
seen: set[str] = set()
for b in skel["bones"]:
    if b["parent"] is not None and b["parent"] not in seen:
        err(f"skeleton: {b['name']} listed before its parent {b['parent']}")
    seen.add(b["name"])

slot_names = [s["name"] for s in slots["slots"]]
schema_slots = schemas["character.schema.json"]["$defs"]["slotName"]["enum"]
if sorted(slot_names) != sorted(schema_slots):
    err("slots.json and character.schema.json slotName enum differ")
slot_by_name = {s["name"]: s for s in slots["slots"]}
for s in slots["slots"]:
    for bn in s["bones"]:
        if bn not in bones:
            err(f"slots: {s['name']} references unknown bone {bn}")
    if "bounds" in s:
        lo, hi = s["bounds"]
        if any(a >= b for a, b in zip(lo, hi)):
            err(f"slots: {s['name']} bounds min must be < max")
    rel = s.get("boundsRelativeTo")
    if rel is not None and rel not in bones:
        err(f"slots: {s['name']} boundsRelativeTo unknown bone {rel}")
    for p in s.get("pieces", []):
        if p["bone"] not in s["bones"]:
            err(f"slots: {s['name']} piece {p['name']} bone {p['bone']} not in slot bones")
    if s["mirror"] and not any(b.endswith(("_L", "_R")) or b.startswith(("Left", "Right")) for b in s["bones"]):
        err(f"slots: mirrored slot {s['name']} has no sided bones")
for name in ("body", "head"):
    if not slot_by_name.get(name, {}).get("required"):
        err(f"slots: {name} must be required")
body_pieces = {p["name"] for p in slot_by_name["body"]["pieces"]}

role_names: dict[str, int] = {}
for r in roles["roles"]:
    if not 0 <= r["role"] <= 31:
        err(f"palette-roles: recolorable role {r['name']} out of 0-31")
    if r["name"] in role_names:
        err(f"palette-roles: duplicate role name {r['name']}")
    role_names[r["name"]] = r["role"]
if len({r["role"] for r in roles["roles"]}) != len(roles["roles"]):
    err("palette-roles: duplicate role numbers")
fixed_lo, fixed_hi = roles["fixedRoles"]
if fixed_lo != 32 or 1 + fixed_hi * 4 + 3 > 255:
    err("palette-roles: fixedRoles must start at 32 and keep index = 1 + role*4 + shade <= 255")

# ---- examples and samples --------------------------------------------------
EX = SPEC / "examples"
for p in sorted(EX.glob("part.*.json")):
    part = validate("part.schema.json", p)
    slot = slot_by_name.get(part.get("slot"))
    if slot is None:
        continue
    names = {pc["name"] for pc in part["pieces"]}
    for pc in part["pieces"]:
        if pc["bone"] not in slot["bones"]:
            err(f"{p.name}: piece {pc['name']} bone {pc['bone']} not allowed in slot {slot['name']}")
        if "mirrorOf" in pc and pc["mirrorOf"] not in names:
            err(f"{p.name}: piece {pc['name']} mirrors unknown piece {pc['mirrorOf']}")
        if "origin" in pc and "bounds" in slot and "boundsRelativeTo" not in slot:
            lo, hi = slot["bounds"]
            if not all(lo[i] <= pc["origin"][i] <= hi[i] for i in range(3)):
                err(f"{p.name}: piece {pc['name']} origin outside slot bounds")
    for bp in part.get("hidesBodyPieces", []):
        if bp not in body_pieces:
            err(f"{p.name}: hidesBodyPieces references unknown body piece {bp}")
if (EX / "pack-manifest.json").exists():
    validate("pack-manifest.schema.json", EX / "pack-manifest.json")
if (EX / "bundle-manifest.json").exists():
    validate("bundle-manifest.schema.json", EX / "bundle-manifest.json")

for p in sorted((ROOT / "samples").rglob("*.vchar.json")):
    ch = validate("character.schema.json", p)
    for key in ch.get("palette", {}):
        if key not in role_names:
            err(f"{p.relative_to(ROOT)}: palette key {key} is not a recolorable role")

# negative check: the character schema must reject an obviously bad file
bad = {"format": "vcf.character", "schemaVersion": "0.1.0", "skeleton": "sd_v1",
       "parts": {"body": "core:b", "wings": "core:x"}}
if validator("character.schema.json").is_valid(bad):
    err("character.schema.json accepts a file without head and with an unknown slot")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"spec: ok ({len(bones)} bones, {len(slot_names)} slots, {len(role_names)} roles)")
