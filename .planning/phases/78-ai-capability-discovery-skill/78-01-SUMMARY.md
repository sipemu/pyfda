---
phase: 78-ai-capability-discovery-skill
plan: "01"
subsystem: capability-dataset
tags: [capability-map, introspection, skill-02, tracer, json-artifact]
status: complete

dependency_graph:
  requires: []
  provides:
    - scripts/generate_capability_dataset.py
    - python/fdars/_capability_map.json
    - python/fdars/_capability_curation.json
    - tests/test_capability_accuracy.py
  affects:
    - .claude/skills/fdars-capabilities/ (78-02 consumes the map)
    - docs/llms.txt (78-03 consumes the map)
    - python/fdars/mcp/server.py (78-04 consumes the map)

tech_stack:
  added: []
  patterns:
    - importlib.resources.files() for Py 3.9+ wheel-safe package data loading
    - inspect.signature() on PyO3 0.28 native callables (all pass — no __text_signature__ fallback needed)
    - sort_keys=True + static ordered _SUBMODULE_NAMES for byte-stable JSON
    - Curation data file merged at generate time (hand-authored 'when' guidance preserved across regenerations)

key_files:
  created:
    - scripts/generate_capability_dataset.py
    - python/fdars/_capability_map.json
    - python/fdars/_capability_curation.json
    - tests/test_capability_accuracy.py
  modified: []

decisions:
  - "_Fdata entry uses special __init__ key + sorted public methods resolved on fdars.Fdata class"
  - "no-drift test strips 'when' curation fields before byte-comparison so adding curation entries doesn't trigger spurious drift failures"
  - "curation merge skips keys that don't match live callables (silent ignore — no build break on stale curation keys)"

metrics:
  duration: 265
  completed: "2026-09-06"
  tasks: 3
  commits: 3

estimate:
  tokens: 55000
  raw_tokens: 30000

actuals:
  tokens: 8000
  tasks: 3
  commits: 3
---

# Phase 78 Plan 01: Capability Dataset Generator and SKILL-02 Harness Summary

Single-sentence summary: Introspection generator producing a byte-stable 31-entry capability map (30 modules + `_Fdata`, 437 callables) from live `fdars` via `__all__` + `inspect.signature`, with 28 curated when-to-use one-liners merged in and a SKILL-02 accuracy test proving no-drift and full importability.

## What Was Built

Three artifacts that form the single source of truth for the capability-discovery skill:

1. **`scripts/generate_capability_dataset.py`** — The introspection generator. Reads each module's `__all__` (authoritative public-API filter), extracts `inspect.signature` + first-docstring-line purpose for every callable, adds a special `_Fdata` entry for the top-level OOP class, and merges curated `when`-to-use guidance from `_capability_curation.json`. Emits `python/fdars/_capability_map.json` with `json.dump(..., sort_keys=True, ensure_ascii=False)`.

2. **`python/fdars/_capability_map.json`** — The committed, byte-stable capability dataset. 31 top-level entries: 27 native submodules + `datasets` + `metrics` + `covariance` + `_Fdata`. 437 total callables. Excludes `advisor`, `plot`, and `results` (non-duplication boundary). 20 entries carry curated `when` guidance.

3. **`python/fdars/_capability_curation.json`** — 28 hand-authored when-to-use one-liners (all ≤120 chars) covering every module family. Keys use `"module.callable"` format; stale keys are silently ignored at merge time.

4. **`tests/test_capability_accuracy.py`** — SKILL-02 accuracy harness:
   - `test_capability_map_no_drift`: Regenerates from live fdars, strips `when` fields from both sides, byte-compares JSON — any signature or docstring change fails.
   - `test_capability_map_all_importable`: Resolves every `fdars.<module>.<fn>` via `getattr`; `_Fdata` methods resolved on `fdars.Fdata`.
   - No `mcp` import (Python 3.9 safe, COMPAT-03).

## Verification Results

All verification gates passed:

| Verification | Command | Result |
|---|---|---|
| MAP STABLE | `python scripts/generate_capability_dataset.py && git diff --quiet _capability_map.json` | PASS |
| KEY CONSTRAINTS | `_Fdata in keys AND advisor/plot/results not in keys` | PASS (31 keys) |
| SKILL-02 tests | `pytest tests/test_capability_accuracy.py -q` | 2 passed |
| No mcp import | grep check | PASS (Py3.9 safe) |
| CURATION OK | `>=6 entries, all <=120 chars` | PASS (28 entries) |
| MERGE OK | `when fields merged into map` | PASS (20 entries) |

## Commits

| Hash | Message |
|------|---------|
| c2c6d18 | feat(78-01): add capability dataset generator and initial committed map |
| 94d44b0 | feat(78-01): add curated when-to-use guidance and regenerate map with merged entries |
| fdc5c0b | test(78-01): add SKILL-02 accuracy harness (no-drift + all-importable) |

## Deviations from Plan

None — plan executed exactly as written.

The Task 2 commit updated `_capability_map.json` a second time (after the Task 1 commit) because the initial commit was made before the curation file existed, so the second run added the `when` fields. This is the expected sequence: author curation file (Task 2), regenerate map with merged guidance, commit both together. The final committed map is the output of a generator run with the curation file present, per the plan's action spec.

## Tracer Feedback Gate

Tracer end-to-end verified before Task 2 expansion:
- Generator ran clean, no stderr warnings
- `git diff --quiet -- python/fdars/_capability_map.json` returned 0 (byte-identical on re-run)
- Map structure validated: `_Fdata` present, `advisor`/`plot`/`results` absent

## Security Review (threat model coverage)

| Threat ID | Mitigated? | Evidence |
|-----------|-----------|---------|
| T-78-01 Tampering via introspection | Yes | Generator reads `__doc__`/`inspect.signature` only — no eval/exec/network |
| T-78-02 Info disclosure via map | Accepted | Map contains only public API signatures already documented on the site |
| T-78-03 Non-deterministic JSON | Yes | `sort_keys=True` + static `_SUBMODULE_NAMES`; SKILL-02 no-drift test asserts byte-stability |

## Known Stubs

None — all entries are fully introspected from live code. No placeholder data.

## Self-Check: PASSED

- [x] `scripts/generate_capability_dataset.py` exists: FOUND
- [x] `python/fdars/_capability_map.json` exists: FOUND (31 modules, 437 callables)
- [x] `python/fdars/_capability_curation.json` exists: FOUND (28 entries)
- [x] `tests/test_capability_accuracy.py` exists: FOUND
- [x] Commit c2c6d18 exists: FOUND
- [x] Commit 94d44b0 exists: FOUND
- [x] Commit fdc5c0b exists: FOUND
- [x] All SKILL-02 tests green: 2 passed
- [x] No mcp import in test: confirmed
