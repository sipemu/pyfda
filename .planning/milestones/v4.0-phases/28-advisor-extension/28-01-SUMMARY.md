---
phase: 28-advisor-extension
plan: "01"
subsystem: advisor
tags: [advisor, scoring, diagnostics, grounding, mcp, guard-sync]
status: complete

dependency_graph:
  requires:
    - "27-xx: v4.0 bindings shipped; fdars.scoring metrics available"
  provides:
    - "scoring diagnostics aspect (13th); _ASPECT_PRIMERS['scoring'] for advise()"
  affects:
    - "28-02: ADV-02 builds on same wiring pattern for represent/alignment extensions"

tech_stack:
  added: []
  patterns:
    - "attribute-first / dict-fallback metric resolution (from represent.py)"
    - "native float() cast on every builder value (no numpy scalar leakage)"
    - "atomic three-file guard-sync commit: aspect builder + advisor __init__ + MCP server"

key_files:
  created:
    - python/fdars/advisor/aspects/scoring.py
    - tests/test_advisor_scoring.py
  modified:
    - python/fdars/advisor/__init__.py
    - python/fdars/mcp/server.py
    - python/fdars/advisor/_prompts.py

decisions:
  - "Caller passes 5 fdars-computed metrics; builder only summarises — no recompute, no y_true/y_pred params (grounding invariant)"
  - "Three guarded edits (scoring.py + dispatch, _supported, _DIAGNOSTICS_METHODS) land in ONE commit — guard-sync test stays green at every commit boundary"
  - "_RUNNABLE_METHODS stays 6 — scoring is diagnostics-only in MCP (needs caller-supplied metrics)"
  - "scoring gets full grounded treatment: builder + _ASPECT_PRIMERS['scoring'] for interpretation/parameter/method task families"

metrics:
  duration: "5m (2026-08-16T19:02:44Z to 2026-08-16T19:07:46Z)"
  completed: "2026-08-16"
  tasks_completed: 3
  commits: 3

actuals:
  tokens: 8000
  tasks: 3
  commits: 3
---

# Phase 28 Plan 01: Scoring Advisor Aspect Summary

ADV-01 tracer: `scoring` wired end-to-end as the 13th advisor diagnostics aspect with grounding invariant, guard-sync atomicity, and offline determinism proof.

## What Was Built

- **`python/fdars/advisor/aspects/scoring.py`** — `_build_scoring_diagnostics(raw, **kwargs)` builder that summarises caller-supplied fdars metrics. Accepts long-form keys (`functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, `functional_explained_variance`) and short aliases (`mae`, `mse`, `mape`, `msle`, `explained_variance`). Computes two summary fields: `largest_error_metric` (name of the error metric with the highest value among present error metrics) and `explained_variance_band` (`"high"` / `"moderate"` / `"low"` threshold at 0.9 / 0.5). All values are native Python `float/str/bool/None` — no numpy scalars.
- **`python/fdars/advisor/__init__.py`** — `"scoring"` added to `_supported` set (now 13) and a `method_lc == "scoring"` lazy-import dispatch branch added to the chain.
- **`python/fdars/mcp/server.py`** — `"scoring"` added to `_DIAGNOSTICS_METHODS` (now 13). `_RUNNABLE_METHODS` unchanged at 6.
- **`python/fdars/advisor/_prompts.py`** — `_ASPECT_PRIMERS["scoring"]` clause explaining the 5 fdars prediction-scoring metrics and the summary fields, enabling `advise()` for interpretation/parameter/method task families.
- **`tests/test_advisor_scoring.py`** — 12 offline tests: basic correctness, absent-key → None, short-alias resolution, ev_band thresholds, largest_error_metric, byte-identical determinism + no-numpy-scalar recursive walker, grounding via `_extract_numbers`, and offline/no-network assertion.

## Task Outcomes

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (tracer) | scoring aspect wired end-to-end — guard-sync green | da505c2 | scoring.py, advisor/__init__.py, mcp/server.py |
| 2 | scoring primer for advise() | 398ca10 | advisor/_prompts.py |
| 3 | offline-determinism + grounding + no-numpy-scalar tests | c181a9a | tests/test_advisor_scoring.py |

## Verification

- Guard-sync: `test_diagnostics_methods_match_advisor_supported` — GREEN
- Scoring suite: `tests/test_advisor_scoring.py` — 12 passed, 0 failed (offline, no key)
- Full suite: `tests/` — 400 passed, 4 skipped, 0 failures (baseline 392 + 8 new)
- Atomicity: commit da505c2 contains all three guarded files together (verified via `git log --stat`)
- `_DIAGNOSTICS_METHODS == 13`, `_RUNNABLE_METHODS == 6` — confirmed

## Deviations from Plan

None — plan executed exactly as written.

The test file contains 12 tests rather than the plan's minimum of 4; the additional 8 tests cover short-alias resolution, absent-key handling, ev_band thresholds, and largest_error_metric edge cases.  All are offline and add no regressions.

## Known Stubs

None.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. The builder is a pure offline Python function. No threat flags.

## Self-Check: PASSED

- `python/fdars/advisor/aspects/scoring.py` — FOUND
- `tests/test_advisor_scoring.py` — FOUND
- Commit da505c2 — FOUND (guard-sync atomic commit)
- Commit 398ca10 — FOUND (primer commit)
- Commit c181a9a — FOUND (tests commit)
- Full suite: 400 passed, 4 skipped, 0 failures — PASSED
