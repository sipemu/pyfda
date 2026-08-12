---
phase: 22-surface-integration
plan: "02"
subsystem: mcp
tags: [mcp, diagnostics, aspects, guard, testing]
status: complete

dependency_graph:
  requires: ["22-01"]
  provides: ["_DIAGNOSTICS_METHODS (12)", "n_classes param", "represent argvals injection", "guard-sync test", "diagnostics-only rejection test"]
  affects: ["python/fdars/mcp/server.py", "tests/test_mcp_server.py"]

tech_stack:
  added: []
  patterns:
    - "_DIAGNOSTICS_METHODS frozenset (12) as superset guard for fdars_build_diagnostics"
    - "argvals-injection into fallback result dict for represent aspect"
    - "scalar n_classes param forwarded to build_diagnostics for classification"
    - "sync-check test via advisor error message parsing (T-22-07 drift lock)"

key_files:
  created: []
  modified:
    - python/fdars/mcp/server.py
    - tests/test_mcp_server.py

decisions:
  - "_DIAGNOSTICS_METHODS (12) guards fdars_build_diagnostics; _RUNNABLE_METHODS (6) guards run_method/compare_run — clear split prevents diagnostics-only aspects from being dispatched via run_method"
  - "represent argvals injection: when result_id is None and method=='represent', build fallback result as {data, argvals} not {data} so _build_represent_diagnostics can compute grid statistics"
  - "n_classes forwarded only when not None — avoids passing None through to build_diagnostics where it is an explicit param"
  - "sync-check test parses the advisor ValueError message to reconstruct advisor._supported; asserts set equality with _DIAGNOSTICS_METHODS — catches both drift scenarios (phantom entry and stale guard)"

metrics:
  duration_seconds: 243
  completed: "2026-08-12T13:11:26Z"
  tasks_completed: 3
  tasks_total: 3
  commits: 3

actuals:
  tokens: 14000
  tasks: 3
  commits: 3
---

# Phase 22 Plan 02: Diagnostics-Only Aspect Expansion Summary

Expanded the proven Wave-1 MCP slice to the full 12-aspect diagnostics surface
(`_DIAGNOSTICS_METHODS`) — including the six diagnostics-only aspects (outliers,
classification, represent, regression, regression_cv, spm) reachable via
`fdars_build_diagnostics` over a caller-supplied result — and locked the
runnable-vs-diagnostics split plus the guard/advisor sync with tests.

## What Was Built

### Task 1 — `_DIAGNOSTICS_METHODS` (12) + n_classes + represent argvals injection (`server.py`)

Three surgical changes to `python/fdars/mcp/server.py`:

1. **`_DIAGNOSTICS_METHODS` frozenset (12 members)** added at module level after
   `_RUNNABLE_METHODS`. Contains all six runnable methods plus outliers, classification,
   represent, regression, regression_cv, spm. The guard at the top of
   `fdars_build_diagnostics` now checks `_DIAGNOSTICS_METHODS` (not `_RUNNABLE_METHODS`).

2. **`n_classes: int | None = None` param** added to `fdars_build_diagnostics` signature.
   Forwarded to `build_diagnostics` only when not None (avoids passing None through as an
   explicit arg). Documented in docstring as required for `method="classification"`.

3. **Represent argvals injection fix**: when `result_id is None` and `method_lc == "represent"`,
   the fallback result dict is `{"data": data, "argvals": argvals}` instead of `{"data": data}`.
   This lets `_build_represent_diagnostics` find the evaluation grid via `raw.get("argvals")`.

Verification: `len(_DIAGNOSTICS_METHODS)==12 and len(_RUNNABLE_METHODS)==6 and _RUNNABLE_METHODS <= _DIAGNOSTICS_METHODS` — passes.

### Task 2 — Guard-sync test (`tests/test_mcp_server.py`)

`test_diagnostics_methods_match_advisor_supported` (synchronous, no asyncio):

- Provokes `advisor.build_diagnostics` ValueError with a sentinel method name
- Parses the `Supported: [...]` list from the error message via `ast.literal_eval`
- Asserts `_DIAGNOSTICS_METHODS == advisor_supported` (exact set equality)
- Catches both T-22-07 drift scenarios: phantom entries in `_DIAGNOSTICS_METHODS`
  and new advisor aspects not yet mirrored into the guard

### Task 3 — Diagnostics-only aspect tests (`tests/test_mcp_server.py`)

Three tests following the in-process `Client(mcp)` + `_unwrap_tool_result` + `dataset_id`
fixture patterns:

- **`test_build_diagnostics_represent`**: calls `fdars_build_diagnostics` with
  `method="represent"` and no `result_id`; asserts `method=="represent"`, `n_obs` int,
  `n_points` int. Exercises the argvals-injection fix.

- **`test_build_diagnostics_classification_with_n_classes`**: stores a synthetic
  point-estimate classification result `{"predicted": [...], "accuracy": 0.80}` in the
  registry; calls with `method="classification"` and `n_classes=2`; asserts
  `n_classes==2` in returned diagnostics.

- **`test_run_method_rejects_diagnostics_only`**: calls `fdars_run_method` with
  `method="regression"`; asserts the tool raises or signals an error (confirms the
  runnable-vs-diagnostics split holds at the run_method boundary).

## Verification Results

```
tests/test_mcp_server.py — 13 passed (was 9; +4 from plan 22-02)
tests/test_skill.py + tests/test_advisor*.py — 81 passed, 1 skipped
Total: 94 passed, 1 skipped
```

Final method sets:
- `_RUNNABLE_METHODS` (6): alignment, basis, clustering, depth, fpca, smoothing
- `_DIAGNOSTICS_METHODS` (12): all 6 runnable + classification, outliers, regression, regression_cv, represent, spm
- Diagnostics-only aspects (6 = `_DIAGNOSTICS_METHODS - _RUNNABLE_METHODS`): classification, outliers, regression, regression_cv, represent, spm

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Task | Commit | Message |
|------|--------|---------|
| T1 | 2770ea3 | feat(22-02): add _DIAGNOSTICS_METHODS (12), n_classes param, represent argvals injection |
| T2 | 4db0a51 | test(22-02): add sync-check test locking _DIAGNOSTICS_METHODS to advisor._supported |
| T3 | 7d64c40 | test(22-02): add represent, classification(n_classes), run_method rejection tests |

## Self-Check

All files exist and all commit hashes are present in git log.

## Self-Check: PASSED
