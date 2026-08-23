---
phase: 50-deferred-advisor-aspects-compat-pre-flight
plan: "01"
subsystem: testing
tags: [mcp, advisor, anthropic, guard-sync, compat, python-3.9]

# Dependency graph
requires: []
provides:
  - "anthropic<1.0 upper bound in [advisor] extra (COMPAT-01)"
  - "MCP v2 MCPServer + 3-tool import smoke test (COMPAT-02)"
  - "Version-independent guard-sync test running on Python 3.9 (COMPAT-03)"
affects:
  - "50-02 (deferred aspects — advisor/MCP surface these tests protect)"
  - "50-03 (grounding matrix — runs on Python 3.9 baseline)"
  - "Phase 54 (docs gate — MCP server surface)"

actuals:
  tokens: 2374
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Version-gated test pattern: module-level pytestmark skip mirrors test_mcp_server.py for mcp-dependent tests"
    - "Version-independent guard-sync: recover advisor._supported by parsing ValueError message (no mcp import); ast.literal_eval on bracketed sorted list"
    - "Hard-coded expected frozenset pattern: _EXPECTED_DIAGNOSTICS_METHODS as test-local mirror of _DIAGNOSTICS_METHODS with maintenance comment"

key-files:
  created:
    - "tests/test_mcp_import_smoke.py"
    - "tests/test_guard_sync_version_independent.py"
  modified:
    - "pyproject.toml (anthropic extra: >=0.72.0 -> >=0.72.0,<1.0)"

key-decisions:
  - "COMPAT-01: Pin anthropic<1.0 in [advisor] extra; full 1.x migration (which drops Python 3.9) deferred to its own milestone"
  - "COMPAT-02: MCP server.py import is verify-only — already uses MCPServer (mcp v2); regression test added, no production change"
  - "COMPAT-03: Guard-sync split: primary test uses ValueError parse (no mcp import, runs 3.9+); companion test internally guarded to 3.10+ via importorskip keeps hard-coded literal honest"

requirements-completed: [COMPAT-01, COMPAT-02, COMPAT-03]

coverage:
  - id: D1
    description: "anthropic>=0.72.0,<1.0 upper bound in [advisor] extra of pyproject.toml"
    requirement: COMPAT-01
    verification:
      - kind: other
        ref: "grep 'anthropic>=0.72.0,<1.0' pyproject.toml (returns 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "MCP v2 MCPServer + fdars_build_diagnostics, fdars_run_method, fdars_compare_run import and load"
    requirement: COMPAT-02
    verification:
      - kind: unit
        ref: "tests/test_mcp_import_smoke.py::test_mcp_v2_server_import_and_tools_load"
        status: pass
    human_judgment: false
  - id: D3
    description: "Guard-sync assertion (advisor._supported == _EXPECTED_DIAGNOSTICS_METHODS) runs on Python 3.9 without importing mcp"
    requirement: COMPAT-03
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_guard_sync_version_independent"
        status: pass
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_guard_sync_mcp_server_matches_expected"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-08-23
status: complete
---

# Phase 50 Plan 01: Compat Pre-flight Summary

**Three blocking compatibility fixes: anthropic pinned below 1.0, MCP v2 server + 3 tools regression-tested, and guard-sync assertion split into a version-independent test that runs on Python 3.9 without importing mcp.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-08-23T21:05:41Z
- **Completed:** 2026-08-23T21:08:14Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `pyproject.toml` [advisor] extra now caps `anthropic<1.0`, deferring the 1.x migration (which drops Python 3.9) to its own milestone
- New `tests/test_mcp_import_smoke.py` proves `MCPServer` (mcp v2 path), `fdars.mcp.server.mcp`, and all 3 tool handlers (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`) load without error; module-level skip on Python <3.10 mirrors `test_mcp_server.py`
- New `tests/test_guard_sync_version_independent.py` provides a primary guard-sync test (Python 3.9-safe: recovers `advisor._supported` by parsing the `ValueError` message via `ast.literal_eval`, no mcp import) plus a 3.10-guarded companion that imports `_DIAGNOSTICS_METHODS` to keep the hard-coded 14-aspect `_EXPECTED_DIAGNOSTICS_METHODS` literal honest

## Task Commits

1. **Task 1: COMPAT-02 tracer** - `913007f` (test)
2. **Task 2: COMPAT-01 pyproject.toml pin** - `c31c0b6` (chore)
3. **Task 3: COMPAT-03 version-independent guard-sync** - `2ca96cf` (test)

## Files Created/Modified

- `tests/test_mcp_import_smoke.py` - MCP v2 server + 3-tool import smoke test (version-gated to 3.10+)
- `tests/test_guard_sync_version_independent.py` - Guard-sync test (primary runs 3.9+; companion 3.10+)
- `pyproject.toml` - [advisor] extra: anthropic>=0.72.0 → anthropic>=0.72.0,<1.0

## Decisions Made

- COMPAT-01: Pin `anthropic<1.0`; full 1.x migration deferred (1.0 drops Python 3.9)
- COMPAT-02: server.py import already correct (`MCPServer` from `mcp.server`); test-only, no production change
- COMPAT-03: Primary guard-sync test uses ValueError parse so it works on Python 3.9 where mcp is absent; a companion test (3.10-guarded) cross-checks the hard-coded literal against `_DIAGNOSTICS_METHODS`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Compat pre-flight complete; advisor and MCP surface are tested against the pinned dependency set
- Plan 50-02 (deferred aspects: PACE-FPCA, elastic-multinomial, ITP) can proceed on this stable base
- The guard-sync test in `test_guard_sync_version_independent.py` will catch any drift when Plan 50-02 extends the advisor (it is a no-op for this plan: `_DIAGNOSTICS_METHODS` and `_supported` are unchanged)

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Self-Check: PASSED

- `tests/test_mcp_import_smoke.py` exists on disk: FOUND
- `tests/test_guard_sync_version_independent.py` exists on disk: FOUND
- `pyproject.toml` contains `anthropic>=0.72.0,<1.0`: FOUND
- git log confirms commits 913007f, c31c0b6, 2ca96cf: FOUND
- `pytest tests/test_mcp_import_smoke.py tests/test_guard_sync_version_independent.py -q`: 3 passed

---
*Phase: 50-deferred-advisor-aspects-compat-pre-flight*
*Completed: 2026-08-23*
