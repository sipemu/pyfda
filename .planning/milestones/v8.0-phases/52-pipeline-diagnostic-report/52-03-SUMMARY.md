---
phase: 52-pipeline-diagnostic-report
plan: "03"
subsystem: mcp
tags: [mcp, pipeline, diagnostics, grounding, offline, tdd, llm-free, by-reference]

requires:
  - phase: 52-pipeline-diagnostic-report
    plan: "01"
    provides: "build_pipeline_report(run_llm=False) offline aggregation core"

provides:
  - "fdars_build_pipeline_report MCP tool in python/fdars/mcp/server.py"
  - "build_pipeline_report_mcp helper in python/fdars/mcp/_pipeline.py"
  - "19-test offline suite tests/test_mcp_pipeline_report.py"
  - "test_tool_never_imports_advise LLM-free guard for mcp/_pipeline.py"
  - "guard-sync no-op assertion: _RUNNABLE_METHODS (6) + _DIAGNOSTICS_METHODS (14) unchanged"

affects:
  - "fdars MCP tool surface (server.py now exposes 5 tools)"
  - "53-auto-tuning (per-stage pipeline report available via MCP boundary)"

actuals:
  tokens: 6024
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Subprocess-based LLM-free module-load check (test_importing_pipeline_module_does_not_import_advise): isolates from prior test imports that load providers"
    - "Pre-run allowlist validation for both params AND aspect before any fdars call (T-52-09 fail-closed, mirrors _compare_methods.py)"
    - "Deferred local imports in build_pipeline_report_mcp keep _pipeline.py LLM-free at load time"
    - "Stage entries passed to offline core with precomputed diagnostics (has 'method' key) — avoids double-running _normalize_stages"
    - "By-reference return: {report_id, stages:[{stage, aspect, result_id}]} — arrays stay in registry (Anti-Pattern 4)"

key-files:
  created:
    - python/fdars/mcp/_pipeline.py
    - tests/test_mcp_pipeline_report.py
  modified:
    - python/fdars/mcp/server.py

key-decisions:
  - "Validate ALL stages (params + aspects) before running ANY stage — fail-closed allowlist (T-52-09): any validation error aborts the entire pipeline request"
  - "Pass precomputed diagnostics dicts (carrying 'method' key) to offline core — avoids double-running build_diagnostics in _normalize_stages (mirrors _compare_methods.py Step 2 pattern)"
  - "Subprocess-based module-load test instead of sys.modules inspection — the shared test suite loads fdars.advisor.providers in prior tests, making sys.modules inspection a false positive; subprocess gives a truly fresh interpreter"
  - "Internal _tool_manager._tools dict for synchronous tool registration check — mcp.list_tools() is async/coroutine, not iterable synchronously"
  - "Guard-sync no-op: _RUNNABLE_METHODS (6) and _DIAGNOSTICS_METHODS (14) untouched (T-52-11)"

requirements-completed: [PIPE-04]

duration: 11min
completed: 2026-08-30
status: complete
---

# Phase 52 Plan 03: Pipeline Diagnostic Report — MCP Tool Summary

**`fdars_build_pipeline_report` LLM-free MCP tool: re-runs each pipeline stage, aggregates by-reference via the offline core, stays provably LLM-free, guard-sync no-op**

## Performance

- **Duration:** 11 min
- **Started:** 2026-08-30T19:02:18Z
- **Completed:** 2026-08-30T19:13:00Z
- **Tasks:** 3 (Task 1 TDD RED/GREEN + Task 2 thin handler + Task 3 test suite)
- **Files modified:** 3

## Accomplishments

- `build_pipeline_report_mcp` in `python/fdars/mcp/_pipeline.py` mirrors `compare_methods_mcp` exactly: Python-3.10 guard, `_ALLOWED_PARAMS` allowlist, pre-run validation of all stage params + aspects, per-stage `run_method` → `registry.store_result` → `build_diagnostics`, delegation to `build_pipeline_report(run_llm=False)`, by-reference return (handles + scalars only)
- `fdars_build_pipeline_report` thin handler added to `server.py`: delegates entirely to `build_pipeline_report_mcp` with no inlined logic, no provider/model argument, no change to `_RUNNABLE_METHODS` or `_DIAGNOSTICS_METHODS` (guard-sync no-op confirmed)
- 19-test offline suite in `tests/test_mcp_pipeline_report.py`: by-reference shape, allowlist validation, aspect rejection, stage-order preservation, offline-core delegation, LLM-free file-scan guard, subprocess module-load guard, guard-sync no-op assertion, recursive no-array check
- Full suite: 953 passed, 9 skipped, 0 failed — no regressions

## Task Commits

1. **Task 1 RED: Failing tests for MCP pipeline tool** - `2085842` (test)
2. **Task 1 GREEN + Tasks 2/3: Implementation + handler + test fixes** - `b4a656e` (feat)

## Files Created/Modified

- `python/fdars/mcp/_pipeline.py` — New MCP helper: `build_pipeline_report_mcp` (validate-all-before-run, per-stage run+store+diag, offline-core delegation, by-reference return)
- `python/fdars/mcp/server.py` — Added `fdars_build_pipeline_report` @mcp.tool handler; updated docstring tool list
- `tests/test_mcp_pipeline_report.py` — 19-test offline suite (by-reference, LLM-free guards, guard-sync, recursive array check)

## Decisions Made

- **Validate ALL before running ANY:** Both param allowlist and aspect membership are checked across all stages before the first `run_method` call. Any validation error aborts the pipeline request entirely (T-52-09 fail-closed). This prevents partial state from accumulating (e.g., stage 0 ran, then stage 1 validation fails — no orphaned result in registry).
- **Precomputed diagnostics passthrough:** Stage entries passed to `build_pipeline_report` carry the pre-built diagnostics dict (with `"method"` key). `_normalize_stages` detects this and skips `build_diagnostics` re-run — avoids double computation and matches `_compare_methods.py` Step 2 pattern.
- **Subprocess for module-load isolation test:** Changed from `sys.modules` inspection to a subprocess check. The shared pytest run loads `fdars.advisor.providers` in prior tests (e.g., `test_advisor.py`), so `sys.modules` inspection gave a false positive — providers appeared loaded even though `_pipeline.py` never caused the import. A fresh subprocess provides true isolation.
- **Internal `_tool_manager._tools` dict for registration check:** `mcp.list_tools()` is a coroutine (requires `await`); for the synchronous unit test, `mcp._tool_manager._tools.keys()` provides the same information without needing asyncio infrastructure.
- **No new `_RUNNABLE_METHODS` / `_DIAGNOSTICS_METHODS` entries:** Adding the pipeline tool is a guard-sync no-op. The pipeline stages use existing runnable aspects — no new aspect key or method slot needed (T-52-11, PIPE-04).

## Deviations from Plan

**1. [Rule 1 - Bug] Subprocess-based module-load test (not sys.modules inspection)**
- **Found during:** Task 3 verification in full suite
- **Issue:** `test_importing_pipeline_module_does_not_import_advise` failed when run as part of the full suite because `fdars.advisor.providers` was already loaded by prior tests (test_advisor.py etc.) — making the `sys.modules` check a false positive
- **Fix:** Replaced `sys.modules` pop/restore pattern with a subprocess check using `sys.executable`. The subprocess gets a clean interpreter with no prior imports, so the check is truly isolated
- **Files modified:** `tests/test_mcp_pipeline_report.py`
- **Commit:** `b4a656e`

**2. [Rule 1 - Bug] Synchronous MCP tool registration check**
- **Found during:** Task 3 test run
- **Issue:** `test_tool_is_registered_as_mcp_tool` used `mcp.list_tools()` as if iterable, but it returns a coroutine — `TypeError: 'coroutine' object is not iterable`
- **Fix:** Changed to `mcp._tool_manager._tools.keys()` for synchronous inspection. Added docstring noting that async client path is tested in `test_mcp_server.py`
- **Files modified:** `tests/test_mcp_pipeline_report.py`
- **Commit:** `b4a656e`

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| `python/fdars/mcp/_pipeline.py` exists | FOUND |
| `tests/test_mcp_pipeline_report.py` exists | FOUND |
| `mcp/_pipeline.py` has no `advise` import | PASS (grep: 0 matches) |
| `fdars_build_pipeline_report` registered in MCP tool set | PASS |
| Non-runnable aspect raises ValueError | PASS |
| Unknown param key raises ValueError before any run | PASS |
| Return is JSON-serialisable (no arrays) | PASS |
| `report_id` is a string handle | PASS |
| `_RUNNABLE_METHODS` count == 6 (guard-sync no-op) | PASS |
| `_DIAGNOSTICS_METHODS` count == 14 (guard-sync no-op) | PASS |
| `tests/test_mcp_pipeline_report.py` 19/19 pass | PASS |
| `test_diagnostics_methods_match_advisor_supported` passes | PASS |
| Full suite 953 passed, 9 skipped, 0 failed | PASS |
| Commits 2085842 and b4a656e exist | VERIFIED |

---
*Phase: 52-pipeline-diagnostic-report*
*Completed: 2026-08-30*
