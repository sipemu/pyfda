---
phase: 12-tool-mcp-surface
plan: 02
subsystem: api
tags: [mcp, model-context-protocol, fdars-run-method, runner, stdio, pytest-asyncio]

# Dependency graph
requires:
  - phase: 12-01
    provides: "MCPServer('fdars-advisor'), HandleRegistry, fdars_build_diagnostics, in-process Client(mcp) test pattern"
  - phase: 11-python-api-surface
    provides: "advisor.build_diagnostics (offline, deterministic, JSON-serialisable diagnostics for 5 methods)"
provides:
  - "python/fdars/mcp/_runner.py — run_method dispatch over five fdars methods by reference"
  - "fdars_run_method @mcp.tool() — strict-schema tool returning {result_id, method}; arrays stay in registry"
  - "run_stdio() entry point — mcp.run(transport='stdio'); transport-agnostic handler layer"
  - "tests/test_mcp_server.py extended — test_list_and_call_tools, test_run_method_all_methods, test_build_diagnostics_all_methods"
affects: [12-03-compare-loop, phase-13-agent-skill]

# Actuals
actuals:
  tokens: 9800
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_runner.run_method: closed-set method validation before any fdars call (T-12-02); scalar-only params (T-12-03)"
    - "fdars_run_method returns only {result_id, method} — arrays stay in registry (Pitfall 4, by-reference invariant)"
    - "Synchronous def tool handlers throughout; no async def for fdars sync compute (Pitfall 2)"
    - "run_stdio() is the sole transport wiring; tool handlers are transport-agnostic (CONTEXT locked decision)"
    - "_unwrap_tool_result helper: structured_content first, content[0].text JSON fallback (Open Question 2 resolution)"
    - "pspline_fit_gcv is the smoothing runner; build_diagnostics smoothing Branch B re-runs it with data+argvals internally"

key-files:
  created:
    - python/fdars/mcp/_runner.py
  modified:
    - python/fdars/mcp/server.py
    - tests/test_mcp_server.py

key-decisions:
  - "smoothing runner = pspline_fit_gcv: stored result lacks lambda_values; build_diagnostics smoothing Branch B (re-run with data+argvals) handles diagnostics correctly when with_argvals=True"
  - "basis runner = basis_nbasis_cv (not pspline_fit_gcv): basis_nbasis_cv returns optimal_nbasis/scores/criterion keys; build_diagnostics basis Branch B falls back to raw data call which matches"
  - "run_stdio() is a standalone function NOT embedded in any tool handler; if __name__=='__main__' guard in server.py"
  - "All five methods produce diagnostics with correct 'method' key from fdars_build_diagnostics — verified end-to-end in test_build_diagnostics_all_methods"

requirements-completed: [TOOL-01, TOOL-02]

coverage:
  - id: D5
    description: "run_method dispatches all five real fdars methods; unknown method raises ValueError (T-12-02)"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "python/fdars/mcp/_runner.py + tests/test_mcp_server.py::test_run_method_all_methods"
        status: pass
    human_judgment: false
  - id: D6
    description: "fdars_run_method returns only {result_id, method}; result_id resolves in registry (by-reference invariant)"
    requirement: TOOL-01
    verification:
      - kind: integration
        ref: "tests/test_mcp_server.py::test_run_method_all_methods"
        status: pass
    human_judgment: false
  - id: D7
    description: "run->build chain works for all five methods; diagnostics['method'] matches requested method"
    requirement: TOOL-01
    verification:
      - kind: integration
        ref: "tests/test_mcp_server.py::test_build_diagnostics_all_methods"
        status: pass
    human_judgment: false
  - id: D8
    description: "list_tools() returns both tools; call_tool() succeeds for fdars_run_method and fdars_build_diagnostics"
    requirement: TOOL-02
    verification:
      - kind: integration
        ref: "tests/test_mcp_server.py::test_list_and_call_tools"
        status: pass
    human_judgment: false
  - id: D9
    description: "run_stdio() exists in server.py and calls mcp.run(transport='stdio'); transport-agnostic handlers"
    requirement: TOOL-02
    verification:
      - kind: unit
        ref: "grep -q 'def run_stdio' python/fdars/mcp/server.py && grep -q 'transport=\"stdio\"' python/fdars/mcp/server.py"
        status: pass
    human_judgment: false

# Metrics
duration: 4min
completed: 2026-08-09
status: complete
---

# Phase 12 Plan 02: fdars_run_method + run_stdio + Full Test Coverage Summary

**Expanded the proven MCP tracer into the full coarse-grained tool set: `_runner.py` with five-method fdars dispatch by reference, `fdars_run_method` returning only `{result_id, method}` (arrays in registry), `run_stdio()` stdio entry point, and three offline tests covering both tools across all five methods.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-08-09T21:10:58Z
- **Completed:** 2026-08-09T21:15:25Z
- **Tasks:** 3 (1 runner module + 1 server extension + 1 TDD test extension)
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- Created `python/fdars/mcp/_runner.py` exposing `run_method(dataset_id, method, *, lambda_=None, n_basis=None, n_comp=None, k=None, seed=None)` dispatching to all five real fdars functions (karcher_mean, basis_nbasis_cv, pspline_fit_gcv, regression.fpca, kmeans_fd). Method validated against closed set before any fdars call (T-12-02); only scalar params accepted (T-12-03).
- Extended `python/fdars/mcp/server.py` with synchronous `@mcp.tool() fdars_run_method` returning only `{"result_id", "method"}` (Pitfall 4: arrays stay in registry). Added `run_stdio()` calling `mcp.run(transport="stdio")` with `if __name__ == "__main__"` guard. Tool handlers remain transport-agnostic (CONTEXT locked decision).
- Extended `tests/test_mcp_server.py` with three async tests using `async with Client(mcp)`: `test_list_and_call_tools` (both tools listed and callable, TOOL-02), `test_run_method_all_methods` (all five methods return resolvable result_id, TOOL-01), `test_build_diagnostics_all_methods` (run→build chain across all five methods, TOOL-01).
- Full suite: **108 passed, 1 skipped** (Python 3.9 module skip intact). All tests offline, no ANTHROPIC_API_KEY, no network.

## Task Commits

1. **Task 1: _runner.py** - `190fa9e` (feat)
2. **Task 2: server.py extensions** - `161854e` (feat)
3. **Task 3: extended tests** - `55b38b3` (test)

## Files Created/Modified

- `python/fdars/mcp/_runner.py` — Created. `run_method` dispatch over five fdars methods; closed-set validation; scalar-only params; `__all__ = ["run_method"]`; NumPy/Sphinx docstrings.
- `python/fdars/mcp/server.py` — Extended with `fdars_run_method` `@mcp.tool()` (returns only handle+method; synchronous) and `run_stdio()` + `__main__` guard.
- `tests/test_mcp_server.py` — Extended with three Plan 12-02 tests, `_unwrap_tool_result` helper, `_method_params` helper, and `dataset_id` fixture.

## Decisions Made

- **`smoothing` runner = `pspline_fit_gcv`** — the stored result (`fitted`, `coefficients`, `edf`, `rss`, `gcv`, `aic`, `bic`) lacks `lambda_values`; `build_diagnostics` smoothing Branch B handles this by re-running with `data+argvals` when `with_argvals=True`. The tool boundary carries only handles and scalar params; multi-lambda sweep arrays never cross it.
- **`basis` runner = `basis_nbasis_cv`** — returns `optimal_nbasis`/`scores`/`criterion` keys; the smoothing/basis distinction maps correctly to the advisor's two separate diagnostics branches.
- **`run_stdio()` standalone function** — not embedded in any tool handler; transport-agnostic handler layer preserved for future HTTP transport (CONTEXT locked decision confirmed in implementation).

## Deviations from Plan

None — plan executed exactly as written.

All five methods dispatch to the correct real fdars function with documented defaults; all five run→build diagnostic chains produce `method`-keyed diagnostics; both tools are listed and invocable in-process; `run_stdio()` wires stdio without touching tool logic.

## Known Stubs

None — all five method paths run real fdars computation; diagnostics are non-stub (method key always populated; other keys may be None for smoothing/basis fallback path but that is expected behavior documented in the runner and the build_diagnostics branch logic).

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns introduced. All additions are in-process (handle registry, fdars native calls, MCP stdio handler). T-12-02 (method allowlist) and T-12-03 (scalar-only params) mitigations applied in `_runner.py` and confirmed by the type-hint-derived MCP schema on `fdars_run_method`.

## Self-Check: PASSED

- `python/fdars/mcp/_runner.py` exists on disk.
- `python/fdars/mcp/server.py` extended with `fdars_run_method` and `run_stdio`.
- `tests/test_mcp_server.py` extended with three Plan 12-02 tests.
- Commits `190fa9e`, `161854e`, `55b38b3` all present in git history.
- `pytest tests/test_mcp_server.py -q` → 4 passed.
- `pytest tests/ -q` → 108 passed, 1 skipped.

---
*Phase: 12-tool-mcp-surface*
*Completed: 2026-08-09*
