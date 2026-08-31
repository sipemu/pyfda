---
phase: 52-pipeline-diagnostic-report
plan: "01"
subsystem: advisor
tags: [pipeline, diagnostics, grounding, aggregation, offline, tdd, pyo3, fdars]

requires:
  - phase: 51-comparative-method-selection
    provides: "_compare_methods.py per-candidate provenance + {'_candidates':[...]} union-grounding pattern — mirrored here as {'_stages':[...]}"

provides:
  - "build_pipeline_report() offline aggregation core in python/fdars/advisor/_pipeline.py"
  - "Per-stage list-of-blocks structure [{stage, aspect, diagnostics}] — NEVER flat-merged"
  - "{'_stages':[...]} union-grounding payload wrapper (mirrors Phase-51 {'_candidates':[...]})"
  - "build_pipeline_report exported from fdars.advisor.__all__"
  - "Offline test suite tests/test_pipeline_report.py (19 tests, 891 total green)"

affects:
  - 52-pipeline-diagnostic-report/52-02 (narrative path + PipelineReport schema builds on this aggregation)
  - 52-pipeline-diagnostic-report/52-03 (MCP tool fdars_build_pipeline_report delegates here)
  - 53-auto-tuning (per-stage isolation is the load-bearing property the capstone reuses)

actuals:
  tokens: 7016
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "_normalize_stages(): precomputed diagnostics passthrough (has 'method' key) vs raw result dispatch — mirrors Phase-51 _normalize_candidates()"
    - "Deferred 'from fdars.advisor import build_diagnostics' local import in _pipeline.py keeps module LLM-free at load time (T-52-03)"
    - "_build_stages_union(blocks) returns {'_stages':[diag,...]} so _flatten_diagnostics_numbers recurses list without key-collision (T-52-02, mirrors Phase-51 {'_candidates':[...]})"
    - "LIST-of-blocks aggregation: each stage block is {'stage':str, 'aspect':str, 'diagnostics':dict} — NEVER {**a,**b} (T-52-01)"
    - "NotImplementedError for run_llm=True as explicit Plan 02 hook (same pattern as Phase-51 Plan 01)"
    - "TDD RED/GREEN: test file committed first (failing), then implementation committed to pass"

key-files:
  created:
    - python/fdars/advisor/_pipeline.py
    - tests/test_pipeline_report.py
  modified:
    - python/fdars/advisor/__init__.py

key-decisions:
  - "Aggregate as LIST of per-stage blocks (not dict) — preserves caller-declared order and prevents same-keyed key collision (T-52-01)"
  - "Deferred local import of build_diagnostics inside _normalize_stages() — module stays LLM-free at load without a separate guard function (T-52-03)"
  - "Stage entry resolves result value via 'diagnostics', 'result', or 'value' keys (preference order) — mirrors _normalize_candidates convenience for callers"
  - "NotImplementedError for run_llm=True — explicit Plan 02 hook so the deferred narrative path is obvious and testable"
  - "__init__.py export added during Task 1 GREEN phase to allow tests to import via fdars.advisor — Task 2 is a confirmed no-op diff"

requirements-completed: [PIPE-01]

coverage:
  - id: D1
    description: "build_pipeline_report() aggregates >=2 stages into an ordered LIST of {stage, aspect, diagnostics} blocks with no flat-merge"
    requirement: PIPE-01
    verification:
      - kind: unit
        ref: tests/test_pipeline_report.py#TestStagesIsListOfBlocks
        status: pass
      - kind: unit
        ref: tests/test_pipeline_report.py#TestNoFlatMergeSameKeySurvives
        status: pass
      - kind: unit
        ref: tests/test_pipeline_report.py#TestStageOrderPreserved
        status: pass
    human_judgment: false
  - id: D2
    description: "Precomputed diagnostics dict (has 'method' key) is passed through unchanged without re-running build_diagnostics"
    requirement: PIPE-01
    verification:
      - kind: unit
        ref: tests/test_pipeline_report.py#TestPrecomputedDiagnosticsPassthrough
        status: pass
    human_judgment: false
  - id: D3
    description: "Raw result dict runs build_diagnostics(result, aspect, argvals=...) and produces diagnostics with 'method' key"
    requirement: PIPE-01
    verification:
      - kind: unit
        ref: tests/test_pipeline_report.py#TestRawResultRunsBuildDiagnostics
        status: pass
    human_judgment: false
  - id: D4
    description: "{'_stages':[...]} union payload feeds _flatten_diagnostics_numbers with numbers from every stage (T-52-02)"
    requirement: PIPE-01
    verification:
      - kind: unit
        ref: tests/test_pipeline_report.py#TestUnionPayloadCollectsAllStageNumbers
        status: pass
    human_judgment: false
  - id: D5
    description: "_pipeline.py has no module-level anthropic/providers import — LLM-free at load (T-52-03)"
    requirement: PIPE-01
    verification:
      - kind: unit
        ref: tests/test_pipeline_report.py#TestCoreLLMFree::test_core_is_llm_free
        status: pass
    human_judgment: false
  - id: D6
    description: "build_pipeline_report is exported from fdars.advisor and in __all__"
    requirement: PIPE-01
    verification:
      - kind: unit
        ref: tests/test_pipeline_report.py#TestStagesIsListOfBlocks::test_stages_is_list
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-08-30
status: complete
---

# Phase 52 Plan 01: Pipeline Diagnostic Report — Tracer Summary

**Per-stage list-of-blocks offline aggregation core for `build_pipeline_report()` with `{"_stages":[...]}` union-grounding payload, mirroring Phase-51's `{"_candidates":[...]}` provenance pattern**

## Performance

- **Duration:** 6 min
- **Started:** 2026-08-30T18:36:00Z
- **Completed:** 2026-08-30T18:42:32Z
- **Tasks:** 3 (Task 1 tracer TDD + Task 2 export + Task 3 comprehensive tests)
- **Files modified:** 3

## Accomplishments

- `build_pipeline_report()` in `python/fdars/advisor/_pipeline.py` aggregates an ordered list of stage entries into a LIST of `{stage, aspect, diagnostics}` blocks — NEVER a flat `{**a, **b}` merge (T-52-01 mitigated)
- `_build_stages_union(blocks)` returns `{"_stages": [<diag>, ...]}` so `_flatten_diagnostics_numbers` recurses the list and collects every stage's numbers without key-collision loss (T-52-02 mitigated)
- Deferred `from fdars.advisor import build_diagnostics` local import keeps `_pipeline.py` LLM-free at module load (T-52-03 mitigated); `run_llm=True` raises `NotImplementedError` as an explicit Plan 02 hook
- `build_pipeline_report` exported from `fdars.advisor.__all__` via `__init__.py` re-export line (mirrors `compare_methods` re-export pattern)
- 19-test offline suite in `tests/test_pipeline_report.py`; full suite 891 passed, 8 skipped — no regressions

## Task Commits

1. **Task 1 RED: Failing tests for aggregation core** - `b9f7d5d` (test)
2. **Task 1 GREEN + Task 2: Implementation + export** - `a43f188` (feat)

_Note: Task 3 (comprehensive test file) was written upfront in Task 1 RED to enable complete TDD. Task 2 export was added in Task 1 GREEN so the tests could import via `fdars.advisor`. Both are committed with the correct task commits above._

## Files Created/Modified

- `python/fdars/advisor/_pipeline.py` — New offline aggregation core: `_normalize_stages()`, `_build_stages_union()`, `build_pipeline_report()`
- `python/fdars/advisor/__init__.py` — Added `"build_pipeline_report"` to `__all__` and re-export line
- `tests/test_pipeline_report.py` — 19-test offline suite (list-of-blocks, no-flat-merge, union payload, LLM-free invariant)

## Decisions Made

- **LIST aggregation, not dict:** Per-stage blocks are a Python list so caller-declared order is guaranteed and same-keyed diagnostic values across stages can never collide. A dict key would silently overwrite earlier stage values (T-52-01).
- **Phase-51 union-grounding pattern:** `{"_stages": [...]}` wrapper mirrors `{"_candidates": [...]}` from `_compare_methods.py` exactly — `_flatten_diagnostics_numbers` recurses lists already, so no code change needed in the validate module (T-52-02).
- **Deferred local import in _normalize_stages:** `from fdars.advisor import build_diagnostics` is inside the function body, not at module level, keeping `_pipeline.py` side-effect-free at load — same pattern as `_compare_methods.py` (T-52-03).
- **Three accepted result keys (`"diagnostics"`, `"result"`, `"value"`):** mirrors `_normalize_candidates` convenience so callers can use whichever key name matches their data structure.
- **`NotImplementedError` for `run_llm=True`:** explicit hook so Plan 02 cannot be accidentally omitted; same pattern as Phase-51 Plan 01 deferring its LLM path.

## Deviations from Plan

None — plan executed exactly as written. The export (`__init__.py`) was added during Task 1 GREEN phase (rather than as a standalone Task 2 commit) because the tests import via `fdars.advisor` and needed the export to pass; this is a sequencing convenience within TDD, not a scope deviation.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 02 can build directly on `build_pipeline_report(run_llm=False)` — it will add the `pipeline_report()` narrative function, the `"pipeline"` task family system prompt, and the `PipelineReport` schema; the `NotImplementedError` hook in `run_llm=True` is the explicit entry point.
- Per-stage list-of-blocks + union-grounding payload proven end-to-end — the load-bearing isolation property Phase 53 auto-tuning capstone depends on is established.
- Guard-sync no-op confirmed: `_DIAGNOSTICS_METHODS` and `build_diagnostics._supported` are unchanged (no new aspect key).

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| `python/fdars/advisor/_pipeline.py` exists | FOUND |
| `tests/test_pipeline_report.py` exists | FOUND |
| `build_pipeline_report` in `fdars.advisor.__all__` | PASS |
| `tests/test_pipeline_report.py` 19/19 pass | PASS |
| Full suite 891 passed, 8 skipped, 0 failed | PASS |
| No regressions | PASS |
| Commits b9f7d5d and a43f188 exist | VERIFIED |

---
*Phase: 52-pipeline-diagnostic-report*
*Completed: 2026-08-30*
