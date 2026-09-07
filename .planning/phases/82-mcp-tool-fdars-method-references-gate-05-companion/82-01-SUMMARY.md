---
phase: 82-mcp-tool-fdars-method-references-gate-05-companion
plan: 01
subsystem: mcp
tags: [mcp, fdars_method_references, llm-free, guard-sync, importlib, references-map, GATE-05]

requires:
  - phase: 81-scientific-provenance-data
    provides: _references_map.json with 57 papers/243 callable_index entries; _capability_map.json with 437 callables; GATE-05 A/B primary guard tests
  - phase: 78-fdars-list-capabilities
    provides: fdars_list_capabilities pattern; _CAPABILITY_MODULES frozenset; lazy-import discipline; guard-sync test structure

provides:
  - fdars_method_references() @mcp.tool() in python/fdars/mcp/server.py — LLM-free static reference lookup by callable
  - _REFERENCES_MODULES frozenset alias (derived from _CAPABILITY_MODULES, single source of truth)
  - GATE-05 C: test_references_tool_llm_free_boundary (AST no-import + result-key boundary)
  - GATE-05 D: test_references_mcp_server_frozenset_matches (three-way frozenset mirror)
  - _EXPECTED_REFERENCES_MODULES literal in test file (30 members, byte-identical to _CAPABILITY_MODULES)
  - All 6 return-contract branches verified: curated hit, all-curated:false hit, sentinel miss, bare-callable resolution, ambiguous, _Fdata special-case, ValueError on unknown module

affects: [83-fdars-advisor-skill, 84-phase-gate-citation-review, docs-llms-txt]

actuals:
  tokens: 4785
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - fdars_method_references handler mirrors fdars_list_capabilities — lazy importlib.resources JSON load, frozenset gate BEFORE any I/O, noqa:PLC0415 on all in-body imports
    - _REFERENCES_MODULES is an alias (not a copy) of _CAPABILITY_MODULES — the DERIVED relationship is asserted by the (D) guard three-way equality check
    - Guard Group 3 companion tests (C/D) follow Py3.10+ skip + pytest.importorskip pattern established in Guard Group 2; (C) uses AST-walk on inspect.getsource for structural no-import assertion

key-files:
  created: []
  modified:
    - python/fdars/mcp/server.py
    - tests/test_guard_sync_version_independent.py

key-decisions:
  - "_REFERENCES_MODULES is an alias (= _CAPABILITY_MODULES), not an independent frozenset, so that a single line of code establishes the DERIVED relationship and the (D) guard's three-way equality assertion is structurally guaranteed"
  - "Coverage denominator derived live from _capability_map.json via sum(len(v) for v in cap_data.values()) — never hardcoded. Authoring-time value is 437, not 409 (see 409-to-437 correction note below)"
  - "Return contract for callable_index hit with all-curated:false papers is curated:False + papers:[] (no sentinel), distinguishing it from the callable_index miss (sentinel:NO_CURATED_ENTRY) per the honesty rule: present but unverified is different from absent"
  - "_Fdata special-cased with module != '_Fdata' guard before frozenset check — consistent with fdars_list_capabilities precedent (server.py:796-798)"
  - "Tool + guard tests committed in ONE atomic commit (GATE-04 lesson: the guard is meaningless without the tool, and the tool is unguarded without the guard)"

patterns-established:
  - "GATE-05 companion pattern: (C) AST-walk asserts LLM-free boundary structurally; (D) three-way frozenset mirror asserts _REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES == _CAPABILITY_MODULES — run on Py3.10+ with mcp importorskip"
  - "Sentinel contract: NO_CURATED_ENTRY for callable_index miss; AMBIGUOUS_CALLABLE for bare callable with >1 prefix matches; neither sentinel appears on a hit (even an all-curated:false hit)"

requirements-completed: [MCP-01, MCP-02, MCP-03, MCP-04]

coverage:
  - id: D1
    description: "fdars_method_references returns curated:true hit with papers/coverage/version and no provider/model keys for depth.fraiman_muniz_1d"
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_tool_llm_free_boundary"
        status: pass
    human_judgment: false
  - id: D2
    description: "fdars_method_references returns sentinel NO_CURATED_ENTRY for explain.shap_values (absent from callable_index) with no doi key"
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_tool_llm_free_boundary"
        status: pass
    human_judgment: false
  - id: D3
    description: "fdars_method_references handler body imports no advisor/provider module (AST-level assertion)"
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_tool_llm_free_boundary"
        status: pass
    human_judgment: false
  - id: D4
    description: "_REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES == _CAPABILITY_MODULES three-way frozenset mirror"
    requirement: MCP-04
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_mcp_server_frozenset_matches"
        status: pass
    human_judgment: false
  - id: D5
    description: "All 6 return-contract branches verified: curated hit, all-curated:false hit, sentinel miss, bare-callable resolution, _Fdata special-case, unknown-module ValueError"
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "inline sweep via PYTHONPATH=python .venv/bin/python -c ... prints POSITIVE BRANCHES OK + VALUEERROR BRANCH OK"
        status: pass
    human_judgment: false

duration: 23min
completed: 2026-09-07
status: complete
---

# Phase 82 Plan 01: fdars_method_references MCP Tool + GATE-05 Companion Summary

**LLM-free `fdars_method_references()` @mcp.tool() shipped in server.py with `importlib.resources` JSON lookup, six-branch return contract, and GATE-05 (C)/(D) guard tests — all in one atomic commit; coverage emits derived 28/437**

## Performance

- **Duration:** 23 min
- **Started:** 2026-09-07T18:21:23Z
- **Completed:** 2026-09-07T18:44:33Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Shipped `fdars_method_references(method: str) -> dict` — a synchronous `@mcp.tool()` immediately after `fdars_list_capabilities` in `python/fdars/mcp/server.py`. Accepts `"module.callable"` (frozenset-gated before any JSON I/O) or bare `"callable"` (suffix-resolved). Returns curated paper entries with cross-language pointers, or an explicit sentinel — never `{}`, never raises except on an unknown module prefix.
- Added `_REFERENCES_MODULES: frozenset[str] = _CAPABILITY_MODULES` alias in server.py — the DERIVED single-source-of-truth relationship; the (D) guard asserts the three-way equality.
- Added `_EXPECTED_REFERENCES_MODULES` (30 members, byte-identical to `_CAPABILITY_MODULES`) in the test file, plus GATE-05 companion tests (C) `test_references_tool_llm_free_boundary` and (D) `test_references_mcp_server_frozenset_matches` — committed atomically with the tool (GATE-04 lesson).
- All 12 guard tests green including the two new Py3.10+ companion tests; all 6 return-contract branches verified against the live committed JSON.

## Coverage Denominator Correction: 409 → 437

**For Phase 84 to reconcile:** The MCP-02 requirement text says "N/409" but the derived honest denominator from the live `_capability_map.json` is **437** (verified: `sum(len(v) for v in cap_data.values()) == 437`). The tool derives the denominator at call time — never hardcoded — so it reports `28/437`, not `28/409`. Phase 81 already established 437 as the true callable count (the CURATE-05 coverage test emits `COVERAGE: N/437`). Phase 84 should update the MCP-02 requirement text from 409 to 437.

## Task Commits

1. **Task 1 + Task 2 (atomic):** `3610b45` — feat(82-01): add fdars_method_references MCP tool + GATE-05 Guard Group 3 (C/D)
   - Task 1 (tracer): implemented the tool, alias, docstring update, `_EXPECTED_REFERENCES_MODULES`, and both companion tests in one commit (GATE-04 requirement)
   - Task 2 (behavioral sweep): no production edits needed; all 6 branches verified against the committed tool; no handler fixes required

## Files Created/Modified

- `python/fdars/mcp/server.py` — Added `_REFERENCES_MODULES` alias, updated `_CAPABILITY_MODULES` maintenance comment, updated module docstring (Tools exposed), added `fdars_method_references` handler (~160 lines)
- `tests/test_guard_sync_version_independent.py` — Added `_EXPECTED_REFERENCES_MODULES` frozenset literal, Guard Group 3 companion section header, `test_references_tool_llm_free_boundary` (C), `test_references_mcp_server_frozenset_matches` (D)

## Decisions Made

- `_REFERENCES_MODULES` is an alias (`= _CAPABILITY_MODULES`), not a copy, so the DERIVED relationship is structural — the (D) guard's three-way equality holds by construction and is enforced at every module load.
- Coverage denominator derived live at call time (`sum(len(v) for v in cap_data.values())`) — keeps the coverage string honest as the capability map grows without requiring a code update.
- Return contract distinguishes "callable_index miss" (sentinel) from "callable_index hit, all papers curated:false" (no sentinel, papers list present) — consistent with the honesty principle: present-but-unverified is a different state from absent.

## Deviations from Plan

None — plan executed exactly as written. The handler sketch in 82-RESEARCH was followed verbatim. No bugs found, no fixes needed.

## Issues Encountered

None — the RESEARCH.md sketches were high-confidence and implementation-ready. The only non-obvious moment was confirming that `clustering.align_cluster_fd` IS in `callable_index` (it is, with a curated:false placeholder paper), which is the correct all-curated:false hit branch test case.

## User Setup Required

None — no external service configuration required. The tool runs LLM-free via static JSON file reads.

## Next Phase Readiness

- **Phase 83 (fdars-advisor skill):** Can now import `fdars_method_references` as the LLM-free provenance layer on top of which the hybrid curated/ungrounded fallback skill is built. The GATE-05 LLM-free boundary is closed and provable.
- **Phase 84 (strict gate + human citation review):** Should reconcile the MCP-02 requirement text to replace "N/409" with "N/437" (derived denominator). The (D) guard and `_EXPECTED_REFERENCES_MODULES` literal are ready for any future callable-count expansion.

## Self-Check

- [x] `python/fdars/mcp/server.py` exists with `fdars_method_references` and `_REFERENCES_MODULES`
- [x] `tests/test_guard_sync_version_independent.py` exists with `test_references_tool_llm_free_boundary` and `test_references_mcp_server_frozenset_matches`
- [x] Commit `3610b45` exists (`git log --oneline | grep 3610b45`)
- [x] All 12 guard tests pass
- [x] HIT OK and MISS OK verified inline

## Self-Check: PASSED

All committed files present, commit hash verified, all tests green, all inline acceptance checks pass.

---
*Phase: 82-mcp-tool-fdars-method-references-gate-05-companion*
*Completed: 2026-09-07*
