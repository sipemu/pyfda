---
phase: 51-comparative-method-selection
plan: "03"
subsystem: mcp
tags: [mcp, advisor, compare-methods, llm-free, by-reference, deterministic]

requires:
  - phase: 51-01
    provides: deterministic compare_methods(run_llm=False) ranking core
  - phase: 51-02
    provides: LLM-narrated comparison + MCP server pattern (fdars_compare_run analog)

provides:
  - fdars_compare_methods @mcp.tool in python/fdars/mcp/server.py
  - compare_methods_mcp helper in python/fdars/mcp/_compare_methods.py
  - tests/test_mcp_compare_methods.py covering ranking, by-reference, LLM-free, guard-sync

affects:
  - mcp-surface (new tool in the server)
  - advisor (consumed via run_llm=False path only)

actuals:
  tokens: 6153
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "fdars_compare_methods: flat scalar schema, method validated at tool boundary against _RUNNABLE_METHODS, delegation to helper (Single Responsibility)"
    - "LLM-free invariant: tool imports only _compare_methods helper; no advise() in the MCP layer"
    - "by-reference return: only opaque handles + scalar metric values cross the MCP boundary (Anti-Pattern 4)"
    - "guard-sync no-op: new tool adds zero entries to _RUNNABLE_METHODS or _DIAGNOSTICS_METHODS"

key-files:
  created:
    - python/fdars/mcp/_compare_methods.py
    - tests/test_mcp_compare_methods.py
  modified:
    - python/fdars/mcp/server.py

key-decisions:
  - "Validate method at the tool boundary (server.py) before delegating to the helper — fail fast, clear error naming the supported set"
  - "Helper (_compare_methods.py) validates candidate param allowlist before any run — all T-51-10 validation upfront"
  - "Tool delegates entirely to compare_methods_mcp; no ranking logic inlined in server.py (Single Responsibility / Anti-Pattern 5)"
  - "Task 3 proof tests already committed with the helper in the prior agent session — no separate Task 3 commit needed"

patterns-established:
  - "MCP compare tool: thin @mcp.tool wrapper validates input, delegates to a standalone helper, never touches advise()"
  - "LLM-free file-scan test: construct token at runtime to avoid test file self-flagging"
  - "guard-sync test: assert exact set sizes in a dedicated test that would fail on any accidental expansion"

requirements-completed: [COMPARE-04]

coverage:
  - id: D1
    description: "fdars_compare_methods @mcp.tool registered in server.py, validates method against _RUNNABLE_METHODS, delegates to compare_methods_mcp"
    requirement: COMPARE-04
    verification:
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_tool_handler_returns_ranking"
        status: pass
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_rejects_method_not_in_runnable"
        status: pass
    human_judgment: false

  - id: D2
    description: "compare_methods_mcp helper re-runs candidates, builds diagnostics, delegates ranking to compare_methods(run_llm=False), returns by-reference"
    requirement: COMPARE-04
    verification:
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_ranking_matches_offline_core"
        status: pass
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_returns_by_reference_no_arrays"
        status: pass
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_rejects_candidate_method_outside_runnable"
        status: pass
    human_judgment: false

  - id: D3
    description: "LLM-free invariant: _compare_methods.py and server.py contain no advise() reference; guard-sync no-op (14 diagnostics, 6 runnable)"
    requirement: COMPARE-04
    verification:
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_tool_never_imports_advise"
        status: pass
      - kind: unit
        ref: "tests/test_mcp_compare_methods.py::test_guard_sync_still_no_op"
        status: pass
      - kind: unit
        ref: "tests/test_mcp_server.py::test_mcp_does_not_import_advise"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-24
status: complete
---

# Phase 51 Plan 03: fdars_compare_methods MCP Tool Summary

**fdars_compare_methods MCP tool — LLM-free multi-candidate deterministic ranking via re-run + compare_methods(run_llm=False), returning opaque handles only**

## Performance

- **Duration:** 12 min (resuming from prior session; Task 1 already committed)
- **Started:** 2026-08-24T (continuation from 691a482)
- **Completed:** 2026-08-24
- **Tasks:** 3 (Task 1 pre-committed; Tasks 2 + 3 completed in this session)
- **Files modified:** 3

## Accomplishments

- Registered `fdars_compare_methods` as a `@mcp.tool()` synchronous handler in `server.py`, mirroring the `fdars_compare_run` pattern: flat scalar schema, method validated against `_RUNNABLE_METHODS` at the boundary, delegation to the helper
- `compare_methods_mcp` helper (pre-committed as `ab495a6`) re-runs each candidate via `run_method`, stores results in the registry, builds diagnostics, and delegates ranking to `compare_methods(run_llm=False)` — ranking logic lives exactly once (Anti-Pattern 5)
- All 7 tests in `test_mcp_compare_methods.py` pass; pre-existing `test_mcp_server.py` suite (13 tests) stays green; total 20 tests pass

## Task Commits

Each task committed atomically:

1. **Task 1: compare_methods_mcp helper** — `ab495a6` / `ebe2c35` (feat + doc-comment fix, pre-committed)
2. **Task 1 RED gate** — `691a482` (test: failing tests for compare_methods_mcp)
3. **Task 2: fdars_compare_methods tool** — `adaab72` (feat: register tool in server.py)
4. Task 3 proof tests were already committed as part of `691a482` (the test file contained all 7 tests including the LLM-free and guard-sync assertions — they passed once the tool was wired)

**Plan metadata commit:** (docs commit — see final step)

## Files Created/Modified

- `python/fdars/mcp/_compare_methods.py` — compare_methods_mcp helper (pre-committed); allowlist validation, per-candidate re-run + diagnostics, delegation to ranking core, by-reference return
- `python/fdars/mcp/server.py` — added fdars_compare_methods @mcp.tool, updated docstring tool list
- `tests/test_mcp_compare_methods.py` — 7 tests: ranking_matches_offline_core, returns_by_reference_no_arrays, rejects_candidate_method_outside_runnable, rejects_method_not_in_runnable, tool_handler_returns_ranking, tool_never_imports_advise, guard_sync_still_no_op

## Decisions Made

- **Validate at tool boundary, not only in the helper:** `server.py` checks `method_lc not in _RUNNABLE_METHODS` before delegating, giving a clear `ValueError` naming the supported set at the MCP surface (fail fast, T-51-10)
- **No ranking logic in server.py:** the handler is 3 lines after validation — import helper, call helper, return. No re-run or sort logic duplicated (Anti-Pattern 5 / Single Responsibility)
- **Task 3 tests committed with helper in prior session:** the test file included all 7 tests from the start; they were not re-committed separately

## Deviations from Plan

None — plan executed exactly as written. The resumption pattern (pre-committed Tasks 1 + 3 tests, Task 2 server.py wiring remaining) matched the resume_context specification.

## Issues Encountered

None — the two failing tests (`test_tool_handler_returns_ranking`, `test_rejects_method_not_in_runnable`) failed with `ImportError: cannot import name 'fdars_compare_methods'`, confirming precisely the missing wiring. Adding the tool resolved both immediately.

## Threat Mitigations Verified

| Threat | Mitigation | Status |
|--------|-----------|--------|
| T-51-09 Elevation (LLM in compute path) | No advise import; file-scan test passes | Verified |
| T-51-10 Tampering (unsupported method) | method validated at tool boundary; allowlist in helper | Verified |
| T-51-11 Info disclosure (arrays crossing MCP boundary) | by-reference return; test_returns_by_reference_no_arrays passes | Verified |
| T-51-12 Tampering (guard-sync drift) | _RUNNABLE_METHODS=6, _DIAGNOSTICS_METHODS=14 unchanged | Verified |

## Next Phase Readiness

- COMPARE-04 fully implemented and tested; MCP tool is ready for agentic use
- Phase 51 (Comparative Method Selection) complete — all three plans done

---

## Self-Check: PASSED

**Files exist:**
- FOUND: python/fdars/mcp/_compare_methods.py
- FOUND: python/fdars/mcp/server.py (fdars_compare_methods registered)
- FOUND: tests/test_mcp_compare_methods.py

**Commits exist:**
- 691a482: test(51-03): add failing tests
- ab495a6: feat(51-03): compare_methods_mcp helper
- ebe2c35: doc-comment reword
- adaab72: feat(51-03): register fdars_compare_methods MCP tool in server.py

**Tests:** 20 passed (7 in test_mcp_compare_methods.py + 13 in test_mcp_server.py)

---
*Phase: 51-comparative-method-selection*
*Completed: 2026-08-24*
