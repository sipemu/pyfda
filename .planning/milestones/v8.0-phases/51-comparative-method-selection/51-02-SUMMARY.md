---
phase: 51-comparative-method-selection
plan: "02"
subsystem: advisor
tags: [compare-methods, comparison-task-family, per-candidate-provenance, winner-authority, grounding, COMPARE-01, COMPARE-02]
dependency_graph:
  requires:
    - phase: 51-01
      provides: "compare_methods() offline core, _METRIC_REGISTRY, _normalize_candidates, _rank, deterministic winner"
  provides:
    - "'comparison' task family in _system_prompt() (COMPARE-02)"
    - "compare_methods(run_llm=True) path returning winner (fdars-authoritative) + Advice narration"
    - "Per-candidate labeled provenance payload — list of {label, diagnostics} blocks"
    - "Per-candidate grounding check (_check_grounding run per block, not against merged dict)"
    - "Offline + env-gated live tests (tests/test_compare_methods_advise.py)"
  affects: [Plan 03 (MCP tool fdars_compare_methods — must stay LLM-free)]

actuals:
  tokens: 6800
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Per-candidate labeled provenance blocks: [{label, diagnostics}] passed to LLM — never flat-merged"
    - "Winner authority: fdars sort winner captured before LLM call, re-asserted in result after"
    - "Per-candidate grounding: _check_grounding(advice, block.diagnostics) per block — cross-candidate citation fails"
    - "Deferred LLM imports inside run_llm=True branch — module load stays side-effect-free"

key-files:
  created:
    - tests/test_compare_methods_advise.py
  modified:
    - python/fdars/advisor/_compare_methods.py
    - python/fdars/advisor/_prompts.py
    - tests/test_compare_methods.py

key-decisions:
  - "Per-candidate grounding via calling _check_grounding(advice, block_diagnostics) once per labeled block — a value in candidate A's block is NOT accepted as grounding for a claim about candidate B"
  - "compare_methods import path: from fdars.advisor import compare_methods (public API via __init__.py); test imports corrected to match"
  - "test_core_is_llm_free updated to check column-0 (module-level) imports only — deferred local imports in run_llm=True branch are intentional, not violations"
  - "result['advice'] carries the Advice object; result['winner'] is always the fdars-sort winner regardless of LLM narration content (T-51-05)"

requirements-completed: [COMPARE-01, COMPARE-02]

coverage:
  - id: D1
    description: "'comparison' task clause in _system_prompt() with grounding invariant and narration-only instruction"
    requirement: COMPARE-02
    verification:
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_comparison_task_prompt_added
        status: pass
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_existing_tasks_unchanged
        status: pass
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_comparison_rejects_bogus_task
        status: pass
    human_judgment: false
  - id: D2
    description: "compare_methods(run_llm=True) preserves fdars-sort winner regardless of LLM narration"
    requirement: COMPARE-01
    verification:
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_winner_set_before_llm_and_preserved
        status: pass
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_llm_cannot_override_winner
        status: pass
    human_judgment: false
  - id: D3
    description: "Per-candidate labeled provenance blocks passed to LLM — never flat-merged dict"
    requirement: COMPARE-02
    verification:
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_provenance_is_per_candidate_not_flat_merged
        status: pass
    human_judgment: false
  - id: D4
    description: "Per-candidate grounding check — cross-candidate citation raises GroundingViolationError"
    requirement: COMPARE-02
    verification:
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_grounding_runs_per_candidate
        status: pass
    human_judgment: false
  - id: D5
    description: "Env-gated live comparison narration smoke test skips cleanly without ANTHROPIC_API_KEY"
    verification:
      - kind: unit
        ref: tests/test_compare_methods_advise.py::test_live_comparison_narration
        status: pass
    human_judgment: false

duration: ~10min
completed: "2026-08-24"
status: complete
---

# Phase 51 Plan 02: Comparison Task Family + LLM Narration Path Summary

**compare_methods(run_llm=True) path with fdars-authoritative winner and per-candidate labeled provenance blocks passed to the LLM; grounding checked per candidate (not against merged dict) so cross-candidate citation raises GroundingViolationError.**

## Performance

- **Duration:** ~10 min (resume from Task 1 crash; Tasks 2+3 only)
- **Started:** 2026-08-24 (resumed)
- **Completed:** 2026-08-24
- **Tasks:** 3 (Task 1 committed 784f571 prior run; Tasks 2+3 committed 8147d41 this run)
- **Files modified:** 3

## Accomplishments

- `_system_prompt("comparison", ...)` returns a prompt with the grounding invariant and a narration-only comparison task clause; the three pre-existing task prompts are unchanged (equality-asserted).
- `compare_methods(run_llm=True)` computes the deterministic ranking + winner from the fdars sort BEFORE calling the LLM, passes each candidate as a labeled `{label, diagnostics}` block (never merged), runs `_check_grounding` once per block, and returns `result["winner"]` from the fdars sort regardless of LLM narration content (T-51-05).
- Per-candidate grounding: `_check_grounding(advice, block_diagnostics)` per candidate block — a value only in candidate A's diagnostics raises `GroundingViolationError` when cited in evidence about candidate B.
- 8 offline tests pass; `test_live_comparison_narration` collected and skipped without `ANTHROPIC_API_KEY`; full suite 859 passed, 8 skipped — no regressions.

## Task Commits

1. **Task 1: 'comparison' task clause in _system_prompt** - `784f571` (feat) — committed prior run
2. **Task 2+3: run_llm=True path + env-gated live test** - `8147d41` (feat) — committed this run

**Plan metadata:** (see below — docs commit)

## Files Created/Modified

- `python/fdars/advisor/_compare_methods.py` — `run_llm=True` branch: normalize+guard+sort (reused from offline path), per-candidate provenance payload, LLM call via `resolve_provider`, per-candidate `_check_grounding`, winner re-assertion
- `python/fdars/advisor/_prompts.py` — `"comparison"` added to `_supported_tasks`, comparison task clause (already committed in `784f571`)
- `tests/test_compare_methods_advise.py` — 8 offline tests + 1 env-gated live test; test imports corrected to `from fdars.advisor import compare_methods`
- `tests/test_compare_methods.py` — `test_core_is_llm_free` fixed to check column-0 imports only

## Decisions Made

- Per-candidate grounding implemented by calling `_check_grounding(advice, block["diagnostics"])` once per labeled block. The `_check_grounding` function flat-scans ALL numeric tokens in evidence against the provided diagnostics dict; running it once per block means a value only in candidate A will be accepted when checking A's block but will raise when checking B's block if the evidence mentions it for B.
- Winner authority: `result["winner"]` is always from the pre-LLM fdars sort (captured before the provider call). The `result["advice"]` field carries the LLM `Advice` object as-is. No post-narration winner extraction is attempted.
- Import path fix: tests originally used `from fdars.advisor.compare_methods import compare_methods` (wrong — no `compare_methods.py` submodule exists). Fixed to `from fdars.advisor import compare_methods` (the public path via `__init__.py`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_core_is_llm_free checks all indentation levels, not module-level only**

- **Found during:** Task 2 verification (post-commit full suite run)
- **Issue:** `test_core_is_llm_free` uses `line.strip().startswith(...)` which picks up all imports regardless of indentation. When the `run_llm=True` branch adds deferred local imports inside the function body, the test fails claiming module-level violation even though the imports are inside a function.
- **Fix:** Changed to `line.startswith(...)` (without `strip()`) so only column-0 (module-level) imports are checked. Updated the test comment to make the intent explicit.
- **Files modified:** `tests/test_compare_methods.py`
- **Verification:** `test_core_is_llm_free` passes; 21/21 Plan 01 tests still pass.
- **Committed in:** `8147d41`

**2. [Rule 1 - Bug] Test imports used non-existent fdars.advisor.compare_methods submodule path**

- **Found during:** Task 2 — first run of the test suite after writing Task 2 tests
- **Issue:** Test bodies imported `from fdars.advisor.compare_methods import compare_methods` (no underscore). No such public submodule exists; the implementation lives in `_compare_methods.py` and is exported via `fdars.advisor.__init__.py`.
- **Fix:** Changed all 6 import occurrences to `from fdars.advisor import compare_methods`.
- **Files modified:** `tests/test_compare_methods_advise.py`
- **Verification:** All 8 offline tests pass; import succeeds without error.
- **Committed in:** `8147d41`

---

**Total deviations:** 2 auto-fixed (both Rule 1 bugs)
**Impact on plan:** Both fixes necessary for correctness. No scope creep; all plan goals achieved.

## Issues Encountered

- Prior executor crashed on a transient 529 Overloaded after committing Task 1. This run resumed from Task 2 with a clean working tree.

## Known Stubs

None — all plan goals achieved. `compare_methods(run_llm=True)` is fully implemented. The Plan 03 MCP tool remains unimplemented (out of scope for Plan 02).

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The LLM call path was already anticipated by the advisor architecture.

## Self-Check

| Artifact | Status |
|----------|--------|
| `python/fdars/advisor/_compare_methods.py` run_llm=True | FOUND — implemented |
| `python/fdars/advisor/_prompts.py` comparison clause | FOUND — committed 784f571 |
| `tests/test_compare_methods_advise.py` | FOUND — 8 tests + 1 skipped |
| Commit `784f571` (Task 1) | FOUND |
| Commit `8147d41` (Task 2+3) | FOUND |
| Task 1 AC: `pytest -k "prompt or unchanged or bogus"` | 3 passed |
| Task 2 AC: `pytest -k "winner or provenance or per_candidate"` | 4 passed |
| Task 3 AC: `test_live_comparison_narration` skipped offline | VERIFIED |
| Full suite (859 tests) | 859 passed, 8 skipped |
| LLM cannot override winner | VERIFIED (mock narration test) |
| Per-candidate provenance (not flat-merged) | VERIFIED |
| GroundingViolationError on cross-candidate citation | VERIFIED |
| COMPARE-01 winner authority | VERIFIED |
| COMPARE-02 comparison task family | VERIFIED |

## Self-Check: PASSED

---
*Phase: 51-comparative-method-selection*
*Completed: 2026-08-24*
