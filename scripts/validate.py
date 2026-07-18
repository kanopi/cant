#!/usr/bin/env python3
"""Validate cant.yaml against the entry schema and the catalog's structural rules.

Rules beyond the per-entry schema:
  - IDs are unique and strictly sequential from CANT-1 (append-only implies no gaps).
  - `related` references must resolve to existing IDs (no self-references).
  - Genus ranges are not enforced (entries append by genus, not by block).

Usage: python3 scripts/validate.py
Exit non-zero on any failure.

Requires: pyyaml. jsonschema is used when available; otherwise a built-in
field check covers the required/enum/pattern rules.
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "cant.yaml"
SCHEMA = ROOT / "schema" / "cant-entry.schema.json"

errors = []

data = yaml.safe_load(CATALOG.read_text())
schema = json.loads(SCHEMA.read_text())

entries = data.get("entries", [])
if not entries:
    errors.append("catalog has no entries")

if not isinstance(data.get("version"), int):
    errors.append("catalog `version` must be an integer")
if not isinstance(data.get("edition"), str) or not data.get("edition"):
    errors.append("catalog `edition` must be a non-empty string")

# --- per-entry validation ---------------------------------------------------
try:
    import jsonschema  # type: ignore

    validator = jsonschema.Draft202012Validator(schema)
    for entry in entries:
        for err in validator.iter_errors(entry):
            errors.append(f"{entry.get('id', '?')}: {err.message}")
except ImportError:
    props = schema["properties"]
    for entry in entries:
        eid = entry.get("id", "?")
        for field in schema["required"]:
            if field not in entry:
                errors.append(f"{eid}: missing required field {field!r}")
        for field in entry:
            if field not in props:
                errors.append(f"{eid}: unknown field {field!r}")
        genus = entry.get("genus")
        if genus not in props["genus"]["enum"]:
            errors.append(f"{eid}: genus {genus!r} not in {props['genus']['enum']}")
        if not re.match(props["id"]["pattern"], str(entry.get("id", ""))):
            errors.append(f"{eid}: id does not match CANT-N pattern")
        for ev in entry.get("evidence", []) or [{}]:
            if ev.get("type") not in ("captured", "documented"):
                errors.append(f"{eid}: evidence type must be captured|documented")
            if not ev.get("source"):
                errors.append(f"{eid}: evidence entry missing source")
        if not entry.get("evidence"):
            errors.append(f"{eid}: evidence is required — no hypothetical entries")

# --- catalog-level rules ----------------------------------------------------
ids = [e.get("id") for e in entries]
if len(ids) != len(set(ids)):
    errors.append("duplicate IDs found")

nums = []
for i in ids:
    m = re.match(r"^CANT-(\d+)$", str(i))
    if m:
        nums.append(int(m.group(1)))
if sorted(nums) != list(range(1, len(nums) + 1)):
    errors.append(
        "IDs must be strictly sequential from CANT-1 with no gaps "
        "(append-only: deprecate entries, never remove them)"
    )

id_set = set(ids)
for entry in entries:
    for rel in entry.get("related", []) or []:
        if rel not in id_set:
            errors.append(f"{entry.get('id')}: related id {rel} does not exist")
        if rel == entry.get("id"):
            errors.append(f"{entry.get('id')}: entry relates to itself")

# --- report -------------------------------------------------------------------
if errors:
    for e in errors:
        print(f"FAIL {e}", file=sys.stderr)
    sys.exit(1)

by_genus = {}
for e in entries:
    by_genus.setdefault(e["genus"], 0)
    by_genus[e["genus"]] += 1
captured = sum(1 for e in entries if any(ev["type"] == "captured" for ev in e["evidence"]))
print(
    f"OK {len(entries)} entries ({', '.join(f'{v} {k}' for k, v in by_genus.items())}); "
    f"{captured} with captured specimens; edition {data['edition']}"
)
