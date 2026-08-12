---
phase: 22-surface-integration
plan: "01"
subsystem: mcp
tags: [mcp, depth, surf-01, surf-02, tracer, llm-free]
status: complete

dependency_graph:
  requires: []
  provides:
    - "_RUNNABLE_METHODS frozenset (6 methods incl. depth) in _runner.py + server.py"
    - "depth end-to-end runnable via fdars_run_method + fdars_build_diagnostics"
    - "test_run_method_depth (SURF-01 acceptance)"
    - "test_mcp_does_not_import_advise (SURF-02 invariant lock)"
  affects:
    - python/fdars/mcp/_runner.py
    - python/fdars/mcp/server.py
    - tests/test_mcp_server.py

tech_stack:
  added: []
  patterns:
    - "Depth runner returns {scores: ndarray, method_name: str}; server unwraps scores before delegating to advisor"
    - "_RUNNABLE_METHODS frozenset as canonical single source of truth (runner + server keep in sync)"
    - "Runtime token construction in test to avoid self-flagging file scan"

key_files:
  modified:
    - python/fdars/mcp/_runner.py
    - python/fdars/mcp/server.py
    - tests/test_mcp_server.py

decisions:
  - "fraiman_muniz_1d(data, data) self-depth: second arg is ref_data (not argvals) — hard-coded for MCP to avoid string injection (T-12-03)"
  - "Server-side dict unwrap (result['scores']) rather than modifying Phase-21 depth.py builder"
  - "_SUPPORTED_METHODS kept as alias for _RUNNABLE_METHODS for backward compat"

metrics:
  duration_minutes: 15
  completed: "2026-08-12"
  tasks_completed: 3
  commits: 3
  files_modified: 3

actuals:
  tokens: 12000
  tasks: 3
  commits: 3
---

# Phase 22 Plan 01: Depth Runnable + LLM-Free Invariant Lock Summary

Tracer plan for Phase 22 Surface Integration. Proved the new MCP surface end-to-end
on depth — wired through every layer (`_runner.py` dispatch → `server.py` unwrap →
in-process MCP Client) — and permanently locked the LLM-free invariant with a file scan.

## What Was Built

**Task 1 — `_runner.py`: `_RUNNABLE_METHODS` + depth dispatch**

Renamed `_SUPPORTED_METHODS` to `_RUNNABLE_METHODS` and added `"depth"`, making
the runnable set exactly `{alignment, fpca, basis, smoothing, clustering, depth}`.
Kept `_SUPPORTED_METHODS = _RUNNABLE_METHODS` alias for external callers. Added a
depth dispatch branch that calls `fdars.depth.fraiman_muniz_1d(data, data)` (self-depth)
and returns `{"scores": ndarray(n,), "method_name": "fraiman_muniz"}`.

**Task 2 — `server.py`: `_RUNNABLE_METHODS` + depth unwrap**

Renamed the server-local `_SUPPORTED_METHODS` to `_RUNNABLE_METHODS` (mirroring
the runner), added `"depth"`. Added depth-dict unwrap in `fdars_build_diagnostics`:
when `method=="depth"` and the stored result is a dict with a `"scores"` key, the
server unwraps `result["scores"]` and forwards `method_name` to the depth builder
before calling `advisor.build_diagnostics`. Updated `fdars_compare_run` guard to
`_RUNNABLE_METHODS` with a Pitfall-3 comment (compare is restricted to re-runnable
methods only). Updated all docstrings.

**Task 3 — `test_mcp_server.py`: two tracer tests**

- `test_mcp_does_not_import_advise` (SURF-02, sync, no fixture): scans all
  `python/fdars/mcp/*.py` for any reference to the advisor entrypoint; search
  token built at runtime (`"adv" + "ise"`) to avoid self-flagging; asserts zero
  violations.
- `test_run_method_depth` (SURF-01, async, `dataset_id` fixture): calls
  `fdars_run_method("depth")`, asserts `result_id` returned; verifies
  `registry.get_result(result_id)` is a dict with `"scores"` key; calls
  `fdars_build_diagnostics(result_id=..., method="depth")`; asserts
  `method=="depth"`, `n_obs` is int, `depth_mean` is float.

## Deviation from Plan

### Auto-fix [Rule 1 — Bug] fraiman_muniz_1d signature

**Found during:** Task 1 implementation verification

**Issue:** The plan and research both described the depth call as
`fraiman_muniz_1d(data, argvals)`, treating `argvals` as the second positional
argument. The actual Rust signature is `fraiman_muniz_1d(data, ref_data, scale=True)`
where `ref_data` is the **reference sample** (another data matrix), not the
evaluation grid. Passing `argvals` (shape `(m,)`) where `ref_data` (shape
`(n_ref, m)`) is expected would produce a shape mismatch or wrong result.

**Fix:** Implemented as `fraiman_muniz_1d(data, data)` — self-depth using the
dataset as its own reference sample. This is the canonical general-purpose depth
computation: every curve is ranked against the full empirical distribution.

**Files modified:** `python/fdars/mcp/_runner.py` (depth branch)

**Impact:** Correct depth scores are computed; no test regressions.

## Verification Results

```
$ .venv/bin/python -m pytest tests/test_mcp_server.py -x -q
9 passed in 19.61s   (7 pre-existing + 2 new)

$ .venv/bin/python -m pytest tests/test_skill.py tests/test_advisor.py tests/test_advisor_providers.py -x -q
68 passed, 1 skipped in 4.63s

$ grep -rl "advise" python/fdars/mcp/  → (no output: zero violations)

$ python -c "from fdars.mcp._runner import _RUNNABLE_METHODS as R; from fdars.mcp.server import _RUNNABLE_METHODS as S; assert R == S and len(R) == 6"
# → OK
```

All three success criteria met:
- depth is runnable via `fdars_run_method` and its result flows through `fdars_build_diagnostics` compute-only.
- The MCP LLM-free invariant is locked by `test_mcp_does_not_import_advise`.
- No pre-existing MCP test regresses (9/9 pass).

## Commits

| Task | Commit | Message |
|------|--------|---------|
| Task 1 | `c527875` | feat(22-01): add depth to _RUNNABLE_METHODS + dispatch branch in _runner.py |
| Task 2 | `2fa2743` | feat(22-01): rename server guard to _RUNNABLE_METHODS + depth unwrap in build_diagnostics |
| Task 3 | `66f3102` | test(22-01): add test_run_method_depth and test_mcp_does_not_import_advise |

## Self-Check: PASSED

- `/home/simonm/projects/rust/pyfda/python/fdars/mcp/_runner.py` — exists, `_RUNNABLE_METHODS` has 6 methods
- `/home/simonm/projects/rust/pyfda/python/fdars/mcp/server.py` — exists, unwrap added, guard updated
- `/home/simonm/projects/rust/pyfda/tests/test_mcp_server.py` — exists, 2 new tests
- All 3 commits verified in `git log --oneline -3`
