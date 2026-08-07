---
phase: 01-foundation
plan: "02"
subsystem: docs-tooling
status: complete
completed: "2026-08-07"
duration: "2 minutes"

tags:
  - docs
  - determinism
  - matplotlib
  - FND-03
  - FND-06

dependency_graph:
  requires:
    - 01-01  # STYLE_SPEC.md and foundation context
  provides:
    - svg.hashsalt set in docs_fig.py (FND-03 mechanism)
    - fast() helper in docs_fig.py (FND-06, D-08)
  affects:
    - All later-phase exec blocks that render figures (hashsalt applies automatically)
    - All later-phase exec blocks with expensive params (call fast() for speed)

tech_stack:
  added:
    - "matplotlib svg.hashsalt rcParam (FND-03 determinism mechanism)"
  patterns:
    - "Central DOCS_FAST helper (D-08): single fast() call per expensive param; no per-block os.environ checks"
    - "RNG seeding convention: stochastic blocks must add rng = np.random.default_rng(42); audited per-section in phases 3-8"

key_files:
  modified:
    - path: scripts/docs_fig.py
      description: "Added svg.hashsalt to rcParams dict; added import os as _os; added fast(full, fast_value) helper after render(); updated module docstring Usage block"

decisions:
  - "svg.hashsalt placed inside existing rcParams.update() dict (module-import-time, before any figure renders) — ensures all docs_fig-rendered SVGs get deterministic IDs without changing call sites"
  - "import os as _os with leading-underscore alias keeps the stdlib import out of help(docs_fig) output per project module-design conventions"
  - "fast() reads os.environ.get('DOCS_FAST') at call time (not at module-import time) — env var can be set after import and still takes effect; matches D-08 intent"
  - "Module docstring Usage block explicitly states fast mode is speed-only and NOT the determinism source of truth (D-07 documentation requirement)"

metrics:
  duration: "2 minutes"
  completed: "2026-08-07"
  tasks_completed: 2
  tasks_total: 2
  commits: 2
  files_modified: 1

actuals:
  tokens: 682    # 2728 chars / 4 over realized diff
  tasks: 2
  commits: 2
---

# Phase 01 Plan 02: Determinism and Speed Guardrails for docs_fig.py Summary

svg.hashsalt set to "fdars-docs" for byte-identical SVG IDs across full builds; fast(full, fast_value) helper added as the single DOCS_FAST switch for later-phase authors.

## What Was Built

Two targeted additions to `scripts/docs_fig.py`, the central figure render entrypoint:

1. **svg.hashsalt (FND-03):** The key `"svg.hashsalt": "fdars-docs"` was added to the existing `plt.rcParams.update({...})` dict. Without this, matplotlib uses `uuid4()` for SVG element IDs — so every build produces different IDs and byte-for-byte comparison of two builds always fails. With a fixed salt, IDs are deterministic. A comment documents that hashsalt covers IDs only; stochastic exec blocks must also seed their own RNG (`rng = np.random.default_rng(42)`), with per-block auditing deferred to phases 3–8.

2. **fast() helper (FND-06, D-08):** `import os as _os` was added to the stdlib imports block (leading-underscore alias per project convention). `fast(full, fast_value)` was added after `render()` — it returns `fast_value` when `DOCS_FAST` is set, else `full`. The module docstring Usage block was extended to show `fast()` call-site examples and explicitly state that fast mode is speed-only and MUST NOT be used as the publish/determinism source of truth (D-07).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Set svg.hashsalt for deterministic SVG IDs (FND-03) | 166d623 | scripts/docs_fig.py |
| 2 | Add the fast(full, fast_value) DOCS_FAST helper (FND-06, D-08) | 27be8a9 | scripts/docs_fig.py |

## Verification

- `PYTHONPATH=scripts python -c "import docs_fig, matplotlib.pyplot as plt; assert plt.rcParams['svg.hashsalt']=='fdars-docs'"` → `HASHSALT_OK`
- `fast(500, 50)` returns `500` when `DOCS_FAST` unset; returns `50` when `DOCS_FAST=1` → `FAST_OK`
- Single `os.environ.get('DOCS_FAST')` occurrence in `docs_fig.py` (DRY, D-08) → confirmed

## Deviations from Plan

None — plan executed exactly as written. Both additions are additive-only to `scripts/docs_fig.py`. No other rcParams keys changed. No other files touched.

## Known Stubs

None.

## Threat Flags

None. This plan adds no network surface, auth paths, file access patterns, or schema changes. The two mitigations in the plan threat register (T-01-02a: fast-mode docstring/D-07; T-01-02b: hashsalt is intentional fixed value) are both implemented as documented.

## Self-Check: PASSED

- `scripts/docs_fig.py` exists and was modified: FOUND
- Commit `166d623` exists: FOUND
- Commit `27be8a9` exists: FOUND
- `plt.rcParams['svg.hashsalt'] == 'fdars-docs'` at import time: VERIFIED
- `fast(500, 50)` returns correct values for both env states: VERIFIED
