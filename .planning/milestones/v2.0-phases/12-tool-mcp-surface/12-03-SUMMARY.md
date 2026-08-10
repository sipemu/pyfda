---
phase: 12-tool-mcp-surface
plan: 03
subsystem: api
tags: [mcp, model-context-protocol, compare-loop, tool-03, fdars-compare-run, tdd]

# Dependency graph
requires:
  - phase: 12-02
    provides: "fdars_run_method, _runner.run_method, fdars_build_diagnostics, HandleRegistry, 4-test suite"
  - phase: 11-python-api-surface
    provides: "advisor.build_diagnostics (offline, deterministic, JSON-serialisable diagnostics for 5 methods)"
provides:
  - "python/fdars/mcp/_compare.py — compare_run(dataset_id, method, before_result_id, params_after) -> dict"
  - "fdars_compare_run @mcp.tool() — flat-param, strict-schema tool returning before/after/delta (TOOL-03)"
  - "tests/test_mcp_server.py extended — test_compare_run_unit_allowlist, test_compare_run_smoothing, test_compare_run_delta_sign"
  - "examples/mcp_recipe.py — offline end-to-end compare recipe (Python 3.10+)"
  - "advisor.py Branch A-prime fix — pspline_fit_gcv single-fit scalars produce non-empty smoothing diagnostics"
affects: [phase-13-agent-skill]

# Actuals
actuals:
  tokens: 18000
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_compare.compare_run: allowlist-validates params_after keys before any computation (T-12-03)"
    - "delta[key] = after[key] - before[key] for finite scalar float/int keys only; bool/list/None/non-finite excluded"
    - "fdars_compare_run flattens after-params as top-level typed args (Pitfall 6: no nested params_after: dict in MCP schema)"
    - "Branch A-prime in _build_smoothing_diagnostics: pspline_fit_gcv single-fit result → optimal_gcv/optimal_edf scalars"
    - "mcp_recipe.py: sys.version_info < (3, 10) guard exits 0 on Python 3.9 (import-safe everywhere)"

key-files:
  created:
    - python/fdars/mcp/_compare.py
    - examples/mcp_recipe.py
  modified:
    - python/fdars/mcp/server.py
    - tests/test_mcp_server.py
    - python/fdars/advisor.py

key-decisions:
  - "fdars_compare_run flattens after-params as top-level optional typed args (NOT params_after: dict) — MCP schema is fully specified from type hints (Pitfall 6)"
  - "Branch A-prime added to _build_smoothing_diagnostics: pspline_fit_gcv returns scalar gcv/edf/aic/bic (no lambda_values sweep); mapping to optimal_gcv/optimal_edf enables non-empty delta for the compare loop"
  - "compare_run passes data=data kwarg to build_diagnostics for Branch B compatibility; Branch A-prime fires before it reaches Branch B for pspline results"
  - "mcp_recipe.py drives fdars.mcp helpers directly (no live Client transport) — mirrors advisor_recipe.py structure"

requirements-completed: [TOOL-03]

coverage:
  - id: D10
    description: "compare_run rejects unknown params_after keys with ValueError (T-12-03 allowlist)"
    requirement: TOOL-03
    verification:
      - kind: unit
        ref: "tests/test_mcp_server.py::test_compare_run_unit_allowlist"
        status: pass
    human_judgment: false
  - id: D11
    description: "fdars_compare_run returns before/after/delta with non-empty delta dict via in-process Client"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "tests/test_mcp_server.py::test_compare_run_smoothing"
        status: pass
    human_judgment: false
  - id: D12
    description: "Delta has at least one numeric key — deterministic, fdars-computed, no LLM"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "tests/test_mcp_server.py::test_compare_run_delta_sign"
        status: pass
    human_judgment: false
  - id: D13
    description: "examples/mcp_recipe.py exits 0 offline, prints observable delta block"
    requirement: TOOL-03
    verification:
      - kind: manual
        ref: ".venv/bin/python examples/mcp_recipe.py"
        status: pass
    human_judgment: false

# Metrics
duration: 7min
completed: 2026-08-09
status: complete
---

# Phase 12 Plan 03: fdars_compare_run + Compare Loop + mcp_recipe.py Summary

**Closed the TOOL-03 agentic re-run/compare loop: `_compare.py` delta builder, `fdars_compare_run` tool with flat-param MCP schema, three deterministic tests, and `examples/mcp_recipe.py` running the full register → run → compare loop offline.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-08-09T21:17:48Z
- **Completed:** 2026-08-09T21:24:48Z
- **Tasks:** 3 (TDD _compare.py + server extension + tests/recipe)
- **Files modified:** 5 (2 created, 3 modified)

## Accomplishments

- Created `python/fdars/mcp/_compare.py` exposing `compare_run(dataset_id, method, before_result_id, params_after)`. Allowlist-validates `params_after` keys against `{lambda_, n_basis, n_comp, k, seed}` (T-12-03); fetches before result from registry (T-12-01 fail closed); re-runs via `run_method`; stores after result; builds diagnostics for both; computes delta dict (scalar finite float/int diffs only, booleans excluded). `__all__ = ["compare_run"]`; NumPy/Sphinx docstrings; deterministic, no LLM, no network.
- Extended `python/fdars/mcp/server.py` with synchronous `@mcp.tool() fdars_compare_run` using flat typed after-params (`lambda_: float | None = None`, etc.) — MCP schema fully specified from type hints, no nested `params_after: dict` (Pitfall 6). Validates method at tool boundary (T-12-02), delegates entirely to `_compare.compare_run`.
- Fixed pre-existing bug in `python/fdars/advisor.py` `_build_smoothing_diagnostics` (Rule 1): added Branch A-prime to handle `pspline_fit_gcv` single-fit results (has `gcv`/`edf` scalars but no `lambda_values` sweep). Maps to `optimal_gcv`/`optimal_edf`/`gcv_aic_approx`/`gcv_bic_approx` directly. Without this fix the compare loop produced an empty delta for the smoothing method.
- Extended `tests/test_mcp_server.py` with three Plan 12-03 tests: `test_compare_run_unit_allowlist` (direct unit test, no Client), `test_compare_run_smoothing` (before/after/delta non-empty via Client), `test_compare_run_delta_sign` (at least one numeric delta key exists, deterministic assertion).
- Created `examples/mcp_recipe.py` mirroring `advisor_recipe.py`: 4-step offline workflow (register → run → compare → print delta); Python 3.9 guard exits 0 cleanly; prints 4 scalar delta keys (gcv_aic_approx, gcv_bic_approx, optimal_gcv, optimal_edf). No ANTHROPIC_API_KEY, no network.
- Full suite: **111 passed, 1 skipped** (Python 3.9 skip intact). All tests offline, no ANTHROPIC_API_KEY, no network.

## Task Commits

1. **Task 1 RED: failing tests** - `e64ca20` (test)
2. **Task 1 GREEN: _compare.py** - `599a9cf` (feat)
3. **Task 2: server.py + advisor.py fix** - `a3b6fe7` (feat)
4. **Task 3: tests + mcp_recipe.py** - `e6786be` (feat)

## Files Created/Modified

- `python/fdars/mcp/_compare.py` — Created. `compare_run` delta builder; allowlist validation; scalar-finite delta filter; `__all__`; NumPy/Sphinx docstrings.
- `python/fdars/mcp/server.py` — Extended with `fdars_compare_run @mcp.tool()` (flat typed args, synchronous, delegates to `_compare`). Updated module docstring to list all three tools.
- `python/fdars/advisor.py` — Branch A-prime added to `_build_smoothing_diagnostics`; handles `pspline_fit_gcv` single-fit scalar results (bug fix).
- `tests/test_mcp_server.py` — Extended with three Plan 12-03 tests; module docstring updated to list all three plans.
- `examples/mcp_recipe.py` — Created. Offline end-to-end recipe; Python 3.9 guard; deterministic delta output.

## Decisions Made

- **`fdars_compare_run` flattens after-params as top-level optional typed args** — No `params_after: dict` in the MCP tool signature so the schema is fully specified. The handler assembles `params_after` locally from non-None args before passing to `compare_run` (Pitfall 6).
- **Branch A-prime in `_build_smoothing_diagnostics`** — `pspline_fit_gcv` returns scalar `gcv`/`edf` (not a lambda sweep), so Branch A (needs `lambda_values`) never fired. Branch A-prime detects the `"gcv" in raw and "edf" in raw and "lambda_values" not in raw` pattern and maps directly to `optimal_gcv`/`optimal_edf`.
- **Recipe drives helpers directly** — `mcp_recipe.py` imports `registry`, `run_method`, `compare_run` directly rather than via an async Client. This mirrors `advisor_recipe.py` (direct API, not via protocol layer) and avoids asyncio boilerplate in a script context.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed `_build_smoothing_diagnostics` Branch A-prime for pspline_fit_gcv single-fit results**
- **Found during:** Task 2 verification (test_compare_run_smoothing delta was empty)
- **Issue:** `pspline_fit_gcv` returns `{'fitted', 'coefficients', 'edf', 'rss', 'gcv', 'aic', 'bic'}` — Branch A requires `lambda_values` (GCV sweep, not present); Branch B requires `data`/`argvals` in kwargs and also had a bug (`pspline_fit_gcv(data, argvals)` called without required `n_basis`). Result: all-None diagnostics → empty delta.
- **Fix:** Added Branch A-prime in `_build_smoothing_diagnostics` that detects the single-fit pattern and maps scalars to `optimal_gcv`, `optimal_edf`, `gcv_aic_approx`, `gcv_bic_approx`.
- **Files modified:** `python/fdars/advisor.py`
- **Commit:** `a3b6fe7`

## Known Stubs

None — compare loop runs real fdars computation; delta is fully populated from non-None scalar diagnostics keys.

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns introduced. All additions are in-process (handle registry, fdars native calls, MCP tool handler). T-12-02 (method allowlist at tool boundary), T-12-03 (params_after allowlist in compare_run), T-12-01 (KeyError on unknown IDs) mitigations applied and tested.

## Self-Check: PASSED

- `python/fdars/mcp/_compare.py` exists on disk.
- `python/fdars/mcp/server.py` extended with `fdars_compare_run`.
- `python/fdars/advisor.py` extended with Branch A-prime.
- `tests/test_mcp_server.py` extended with three Plan 12-03 tests.
- `examples/mcp_recipe.py` exists on disk.
- Commits `e64ca20`, `599a9cf`, `a3b6fe7`, `e6786be` present in git history.
- `pytest tests/test_mcp_server.py -q` → 7 passed.
- `pytest tests/ -q` → 111 passed, 1 skipped.
- `python examples/mcp_recipe.py` → exits 0, prints delta block with 4 keys.

---
*Phase: 12-tool-mcp-surface*
*Completed: 2026-08-09*
