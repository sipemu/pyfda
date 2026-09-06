---
phase: 78-ai-capability-discovery-skill
plan: "04"
subsystem: mcp, testing
tags: [mcp, capability-discovery, llm-free, guard-sync, importlib-resources, frozenset, py39-safe]

# Dependency graph
requires:
  - phase: 78-01
    provides: python/fdars/_capability_map.json (committed capability dataset — loaded at call time by the new tool)

provides:
  - fdars_list_capabilities @mcp.tool() registered in python/fdars/mcp/server.py (LLM-free, SKILL-04)
  - _CAPABILITY_MODULES frozenset (30 submodule names) in server.py
  - Guard-sync extensions in tests/test_guard_sync_version_independent.py (GATE-04):
      _EXPECTED_CAPABILITY_MODULES + PRIMARY (Py3.9) JSON-keys test + Py3.10+ LLM-free companion + Py3.10+ server-frozenset test
  - fdars_list_capabilities added to tests/test_mcp_import_smoke.py smoke coverage

affects: [78-05, phase-79-gate, gsd-verify-work]

actuals:
  tokens: 4286
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "importlib.resources JSON load pattern: resources.files('fdars') / '_capability_map.json' for package-data access surviving wheel install"
    - "Three-way literal mirror: server._CAPABILITY_MODULES == JSON submodule keys == test _EXPECTED_CAPABILITY_MODULES (T-78-10 guard discipline)"
    - "Py3.9-safe guard-sync extension: primary loads JSON only; Py3.10+ companions guard themselves internally with pytest.skip + pytest.importorskip"

key-files:
  modified:
    - python/fdars/mcp/server.py
    - tests/test_guard_sync_version_independent.py
    - tests/test_mcp_import_smoke.py

key-decisions:
  - "frozenset _CAPABILITY_MODULES mirrors the 30 submodule keys of _capability_map.json (excluding _Fdata class entry) — the tool can filter to any submodule but the special _Fdata key remains in the full return"
  - "Allowlist-first input validation: module arg checked against _CAPABILITY_MODULES frozenset BEFORE importlib.resources load (T-78-08 path-traversal mitigation)"
  - "Return dict carries no provider/model keys and makes no model call — LLM-free boundary is structurally enforced, not just documented"
  - "Guard-sync PRIMARY test imports only stdlib (json, importlib.resources, pytest) — no mcp import — so it runs on Python 3.9+ without skipping"

patterns-established:
  - "LLM-free MCP tool: @mcp.tool() that reads committed static JSON via importlib.resources; no advise(); no provider arg; return dict provably model-key-free"
  - "GATE-04 three-test guard pattern: (a) Py3.9 JSON keys == expected frozenset; (b) Py3.10+ tool return has no provider/model keys; (c) Py3.10+ server frozenset == expected frozenset"

requirements-completed: [SKILL-04]

coverage:
  - id: D1
    description: "fdars_list_capabilities @mcp.tool() registered in server.py — returns static capability surface, no model call, no provider/model keys"
    requirement: SKILL-04
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py#test_capability_tool_llm_free_boundary"
        status: pass
      - kind: unit
        ref: "tests/test_mcp_import_smoke.py#test_mcp_v2_server_import_and_tools_load"
        status: pass
    human_judgment: false
  - id: D2
    description: "_CAPABILITY_MODULES frozenset in server.py equals committed JSON submodule keys (minus _Fdata) — three-way literal mirror enforced"
    requirement: SKILL-04
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py#test_capability_map_modules_match_expected"
        status: pass
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py#test_capability_mcp_server_frozenset_matches"
        status: pass
    human_judgment: false
  - id: D3
    description: "Guard-sync Py3.9-safe PRIMARY test (no mcp import) catches JSON key drift from expected frozenset"
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py#test_capability_map_modules_match_expected"
        status: pass
    human_judgment: false
  - id: D4
    description: "Existing advisor loop and _RUNNABLE_METHODS/_DIAGNOSTICS_METHODS unchanged — additive only"
    verification:
      - kind: unit
        ref: "tests/test_mcp_server.py + tests/test_advisor_grounding.py (67 tests)"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-09-06
status: complete
---

# Phase 78 Plan 04: AI Capability-Discovery Skill (SKILL-04 / GATE-04) Summary

**LLM-free `fdars_list_capabilities` @mcp.tool() registered in MCP server — loads committed `_capability_map.json` via importlib.resources, no model call, frozenset-gated allowlist, and GATE-04 three-test guard-sync added to prove LLM-free boundary on Py3.9+**

## Performance

- **Duration:** 5 min
- **Started:** 2026-09-06T19:25:07Z
- **Completed:** 2026-09-06T19:30:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Added `_CAPABILITY_MODULES` frozenset (30 submodule names) and `fdars_list_capabilities` `@mcp.tool()` to `python/fdars/mcp/server.py` — the tool loads the pre-committed `_capability_map.json` via `importlib.resources` at call time, making NO model call (provably LLM-free: no provider/model keys in return, no ANTHROPIC_API_KEY required)
- Extended `tests/test_guard_sync_version_independent.py` with `_EXPECTED_CAPABILITY_MODULES` frozenset + PRIMARY (Py3.9-safe, no mcp import) JSON-keys test + two Py3.10+ companions: LLM-free boundary assertion + server-frozenset match (GATE-04); all 6 guard-sync tests green
- Extended `tests/test_mcp_import_smoke.py` to import and assert `fdars_list_capabilities` is callable alongside the existing three tool handlers; module-level Py3.10+ skipif guard unchanged
- All 67 existing MCP/advisor tests still green; existing tools, `_RUNNABLE_METHODS`, `_DIAGNOSTICS_METHODS`, and the advisor loop are untouched (additive-only change)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add LLM-free fdars_list_capabilities MCP tool + _CAPABILITY_MODULES frozenset** - `031c58b` (feat)
2. **Task 2: Extend guard-sync — Py3.9 JSON-keys primary + Py3.10+ LLM-free companion (GATE-04)** - `c5c2bb8` (feat)
3. **Task 3: Add fdars_list_capabilities to the MCP import smoke test** - `b55464d` (feat)

## Files Created/Modified

- `python/fdars/mcp/server.py` — added `_CAPABILITY_MODULES` frozenset + `fdars_list_capabilities` @mcp.tool() after `fdars_auto_tune`; updated module docstring to list all 7 tools
- `tests/test_guard_sync_version_independent.py` — added Guard Group 2 (GATE-04): `_EXPECTED_CAPABILITY_MODULES` frozenset + 3 new tests; added `json` and `importlib.resources` imports; updated module docstring
- `tests/test_mcp_import_smoke.py` — extended tool-handlers set to include `fdars_list_capabilities`; updated module docstring

## Decisions Made

- `_CAPABILITY_MODULES` frozenset contains the 30 submodule keys of `_capability_map.json` (excluding `_Fdata` class entry) — the frozenset mirrors the submodule surface; the full tool return when `module=None` includes `_Fdata` from the JSON, and guard companions exclude it when comparing returned module sets
- Allowlist-first design: `module` arg is validated against `_CAPABILITY_MODULES` frozenset BEFORE `importlib.resources` load (T-78-08 path-traversal mitigation; the JSON path is hardcoded, the arg only filters returned keys)
- Guard PRIMARY test uses stdlib only (`json`, `importlib.resources`) — no mcp import — so it runs on Python 3.9 without skipping; existing Py3.9 guard discipline (COMPAT-03) preserved

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes beyond what the plan's threat model covers. T-78-08 (path traversal via module arg) mitigated by frozenset allowlist. T-78-09 (LLM-free boundary) mitigated structurally and by guard test. T-78-10 (frozenset/JSON drift) mitigated by three-way literal mirror.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All SKILL-04 / GATE-04 deliverables green; ready for Phase 79 consolidated close gate
- Phase 79 will run GATE-04 final confirmation + whole-site `mkdocs --strict` build
- Three-way literal mirror (server `_CAPABILITY_MODULES` == JSON keys == test `_EXPECTED_CAPABILITY_MODULES`) is drift-locked for every future PR

## Self-Check: PASSED

- SUMMARY.md: FOUND at `.planning/phases/78-ai-capability-discovery-skill/78-04-SUMMARY.md`
- Task 1 commit: FOUND `031c58b`
- Task 2 commit: FOUND `c5c2bb8`
- Task 3 commit: FOUND `b55464d`
- All 6 guard-sync tests: PASSED
- Smoke test: PASSED (1 test)
- 67 existing MCP/advisor tests: PASSED
- Import smoke: PASSED (no ImportError)

---
*Phase: 78-ai-capability-discovery-skill*
*Completed: 2026-09-06*
