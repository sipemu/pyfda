---
phase: 52-pipeline-diagnostic-report
plan: "02"
subsystem: advisor
tags: [pipeline, caveats, grounding, PipelineReport, tdd, union-grounding, pydantic, offline]

requires:
  - phase: 52-pipeline-diagnostic-report
    plan: "01"
    provides: "build_pipeline_report() offline aggregation core + {'_stages':[...]} union payload"

provides:
  - "_compute_cross_stage_caveats() deterministic Python rule table in _pipeline.py"
  - "Three documented threshold constants: _IMPUTED_FRACTION_CAVEAT_THRESHOLD, _OUTLIER_FRACTION_CAVEAT_THRESHOLD, _LOW_CUMULATIVE_VARIANCE_THRESHOLD"
  - "PipelineReport schema in _schema.py (pydantic + fallback stand-in)"
  - "'pipeline' task family clause in _prompts.py"
  - "pipeline_report() LLM narrative path with union grounding in _pipeline.py"
  - "fdars.advisor.__all__ exports: pipeline_report, PipelineReport"
  - "Offline + env-gated test suite tests/test_pipeline_report_advise.py (43 tests, 934 total green)"

affects:
  - 52-pipeline-diagnostic-report/52-03 (MCP tool fdars_build_pipeline_report wraps pipeline_report)
  - 53-auto-tuning (pipeline_report caveats are the cross-stage signals auto-tuning consumes)

actuals:
  tokens: 52000
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "_compute_cross_stage_caveats(blocks, thresholds=None): iterates per-stage blocks (NEVER flat-merged), applies deterministic rule table, emits structured caveat dicts with native float/int values"
    - "Rule table: R1 (represent high imputed_fraction), R2 (outliers high fraction/count fallback), R3 (fpca low last cumulative_variance_explained)"
    - "pipeline_report() LLM path: compute caveats BEFORE LLM call -> per-stage labeled blocks (NEVER flat-merged) -> complete_structured(PipelineReport) -> _check_grounding_pipeline ONCE against {'_stages':[...]} union -> attach Python caveats authoritatively"
    - "_check_grounding_pipeline(): adapter that applies _extract_numbers + _is_grounded_number to narrative + stages text (PipelineReport has no .recommendations list)"
    - "PipelineReport in both pydantic try branch (BaseModel) and except ImportError fallback branch (plain stand-in with __init__/__repr__/__eq__)"
    - "build_pipeline_report(run_llm=True) now delegates to pipeline_report() (Plan 01 NotImplementedError hook replaced)"

key-files:
  created:
    - tests/test_pipeline_report_advise.py
  modified:
    - python/fdars/advisor/_pipeline.py
    - python/fdars/advisor/_schema.py
    - python/fdars/advisor/_prompts.py
    - python/fdars/advisor/__init__.py
    - tests/test_pipeline_report.py

key-decisions:
  - "Caveats computed BEFORE LLM call and attached authoritatively after — LLM narrates but cannot alter Python-computed caveats (T-52-04)"
  - "_check_grounding_pipeline() adapter applies grounding to narrative + stages text without a Recommendation list — keeps _check_grounding's token-matching logic unchanged and reusable"
  - "Union grounding ONCE against {'_stages':[...]} — no per-stage-strict checks (Phase-51 WR-03 lesson: per-stage-strict over-rejects legitimate cross-stage narration)"
  - "Rule 2 fallback chain: outlier_fraction -> n_outliers/n_obs -> n_union_outliers as count-based indicator — handles all seven outlier result shapes"
  - "build_pipeline_report(run_llm=True) delegates to pipeline_report() rather than keeping NotImplementedError — both entry points now functional"
  - "test_pipeline_report.py updated: Plan-01 'NotImplementedError' hook test replaced with 'not-NotImplementedError' assertion"

requirements-completed: [PIPE-02, PIPE-03]

coverage:
  - id: D1
    description: "_compute_cross_stage_caveats() R1: represent high imputed_fraction -> FPCA/clustering caveat with real value"
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestCaveatRule1HighImputation
        status: pass
    human_judgment: false
  - id: D2
    description: "_compute_cross_stage_caveats() R2: outliers high fraction -> downstream caveat"
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestCaveatRule2HighOutliers
        status: pass
    human_judgment: false
  - id: D3
    description: "_compute_cross_stage_caveats() R3: fpca low last cumulative_variance_explained -> clustering caveat"
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestCaveatRule3LowCumulativeVariance
        status: pass
    human_judgment: false
  - id: D4
    description: "All values below thresholds -> zero caveats"
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestCaveatNoneFiresBelowThreshold
        status: pass
    human_judgment: false
  - id: D5
    description: "Threshold override via param changes which caveats fire"
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestCaveatThresholdOverride
        status: pass
    human_judgment: false
  - id: D6
    description: "Caveat numeric values are native float/int equal to real per-stage diagnostics (grounded)"
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestCaveatValueIsNativeType
        status: pass
    human_judgment: false
  - id: D7
    description: "PipelineReport schema: stages, narrative, caveats fields; pydantic + fallback; Advice unchanged"
    requirement: PIPE-02
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestPipelineReportSchemaImport
        status: pass
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestAdviceAndRecommendationUnchanged
        status: pass
    human_judgment: false
  - id: D8
    description: "'pipeline' task family in _system_prompt with grounding invariant and narration-only clause"
    requirement: PIPE-02
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestPipelineTaskPrompt
        status: pass
    human_judgment: false
  - id: D9
    description: "pipeline_report() fabrication caught (GroundingViolationError); real cross-stage numbers pass"
    requirement: PIPE-02
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestPipelineReportUnionGrounding::test_fabricated_number_raises_grounding_error
        status: pass
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestPipelineReportUnionGrounding::test_real_cross_stage_number_passes_grounding
        status: pass
    human_judgment: false
  - id: D10
    description: "Python-computed caveats attached to result regardless of LLM narration"
    requirement: PIPE-02
    verification:
      - kind: unit
        ref: tests/test_pipeline_report_advise.py#TestPipelineReportCaveatAttachment
        status: pass
    human_judgment: false

duration: 13 min
completed: 2026-08-30
status: complete
---

# Phase 52 Plan 02: Pipeline Diagnostic Report Narrative Layer Summary

**Deterministic Python cross-stage caveat rule table (PIPE-03) + PipelineReport schema (PIPE-02) + pipeline_report() LLM narrative path under union grounding — caveats are Python-authoritative, LLM narrates, never invents**

## Performance

- **Duration:** 13 min
- **Started:** 2026-08-30T18:45:31Z
- **Completed:** 2026-08-30T18:59:05Z
- **Tasks:** 3 (all TDD: RED commit then GREEN commit)
- **Files modified:** 5

## Accomplishments

- `_compute_cross_stage_caveats(blocks, *, thresholds=None)` in `_pipeline.py` — a deterministic Python rule table over the real per-stage diagnostic blocks (NEVER flat-merged); emits structured caveat dicts with native `float`/`int` values; no LLM involved (PIPE-03 mitigated)
- Three documented module-level threshold constants with conservative defaults: `_IMPUTED_FRACTION_CAVEAT_THRESHOLD = 0.20`, `_OUTLIER_FRACTION_CAVEAT_THRESHOLD = 0.15`, `_LOW_CUMULATIVE_VARIANCE_THRESHOLD = 0.80`; all overridable via `thresholds=` param
- Rule table: Rule-1 (represent `imputed_fraction` above threshold -> FPCA/clustering reliability caveat), Rule-2 (outliers aspect outlier fraction above threshold -> downstream caveat; fallback chain: `outlier_fraction` -> `n_outliers/n_obs` -> `n_union_outliers` count), Rule-3 (fpca last `cumulative_variance_explained` below threshold -> clustering caveat)
- `PipelineReport` schema in `_schema.py`: Pydantic `BaseModel` branch (fields: `stages: List[str]`, `narrative: str`, `caveats: List[Any]`) + `except ImportError` fallback stand-in class with `__init__`/`__repr__`/`__eq__`; `Advice` and `Recommendation` unchanged (PIPE-02)
- `"pipeline"` added to `_supported_tasks` in `_system_prompt` with a narration-only, no-invent-caveats clause; grounding invariant embedded; four pre-existing task clauses byte-identical (PIPE-02)
- `pipeline_report()` LLM narrative entry point in `_pipeline.py`: (1) normalize stages to blocks, (2) compute caveats BEFORE LLM call, (3) deferred provider/schema imports, (4) per-stage labeled blocks sent to LLM (NEVER flat-merged), (5) `complete_structured(PipelineReport, ...)`, (6) `_check_grounding_pipeline()` ONCE against `{"_stages":[...]}` union (T-52-05 mitigated; WR-03 over-rejection avoided), (7) Python caveats attached authoritatively (T-52-04 mitigated)
- `_check_grounding_pipeline()` adapter applies `_extract_numbers` + `_is_grounded_number` to `.narrative` + `.stages` text (PipelineReport has no `.recommendations` list)
- `build_pipeline_report(run_llm=True)` now delegates to `pipeline_report()` (Plan 01 `NotImplementedError` hook resolved)
- `pipeline_report` and `PipelineReport` exported from `fdars.advisor.__all__`
- 43-test offline + env-gated test suite in `tests/test_pipeline_report_advise.py`; full suite 934 passed, 9 skipped, 0 failed

## Task Commits

1. **Task 1+2+3 RED: Failing tests** - `a717e44` (test)
2. **Task 1+2+3 GREEN: Implementation** - `e407592` (feat)

_Note: All three TDD RED tests were written together upfront (as a single test file covering all three tasks), then all three GREEN implementations were written together. Both are committed with the correct RED/GREEN TDD commit convention._

## Files Created/Modified

- `python/fdars/advisor/_pipeline.py` — Added: `_IMPUTED_FRACTION_CAVEAT_THRESHOLD`, `_OUTLIER_FRACTION_CAVEAT_THRESHOLD`, `_LOW_CUMULATIVE_VARIANCE_THRESHOLD` constants; `_compute_cross_stage_caveats()`; `_check_grounding_pipeline()`; `pipeline_report()`; updated `build_pipeline_report()` to delegate to `pipeline_report()` when `run_llm=True`
- `python/fdars/advisor/_schema.py` — Added `PipelineReport` in both pydantic branch and except ImportError fallback branch
- `python/fdars/advisor/_prompts.py` — Added `"pipeline"` to `_supported_tasks`; added pipeline task clause
- `python/fdars/advisor/__init__.py` — Added `pipeline_report` and `PipelineReport` to `__all__` and re-export lines
- `tests/test_pipeline_report_advise.py` — New: 43-test offline + env-gated suite
- `tests/test_pipeline_report.py` — Updated: Plan-01 `NotImplementedError` hook test replaced with `not-NotImplementedError` assertion

## Decisions Made

- **Caveats computed BEFORE LLM call:** Python-authoritative by construction — the LLM cannot alter the caveats because they are computed before the LLM is invoked and re-attached to the result after narration (T-52-04).
- **Union grounding ONCE:** `_check_grounding_pipeline()` checks the `{"_stages":[...]}` union, not per-stage-strict. A cited value is grounded when present in ANY stage. This avoids the Phase-51 WR-03 over-rejection failure where legitimate cross-stage narration was rejected.
- **_check_grounding_pipeline() adapter:** Rather than modifying `_check_grounding` to handle both `Advice` and `PipelineReport`, a lightweight adapter applies the same token-matching primitives to the narrative/stages text. Keeps the existing grounding machinery unchanged.
- **Rule 2 fallback chain:** `outlier_fraction` -> `n_outliers/n_obs` -> `n_union_outliers` as count-based proxy (count/100) — handles all seven outlier result shapes from `aspects/outliers.py` including sequential_transform_outliers where `n_obs` is not available.
- **build_pipeline_report delegation:** Plan 01's `NotImplementedError` hook replaced by a delegation to `pipeline_report()`. Both entry points work; `build_pipeline_report(run_llm=False)` still returns the offline dict.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated Plan-01 test expecting NotImplementedError**
- **Found during:** Task 3 GREEN (full suite run)
- **Issue:** `test_pipeline_report.py::TestCoreLLMFree::test_run_llm_true_raises_not_implemented` expected `NotImplementedError` from `build_pipeline_report(run_llm=True)` — the Plan 01 hook. Now that Plan 02 is implemented, this raises a provider/import error instead.
- **Fix:** Updated the test to assert `NotImplementedError` is NOT raised (Plan 02 is implemented), while allowing any other exception (provider not configured in offline CI).
- **Files modified:** `tests/test_pipeline_report.py`
- **Commit:** e407592

**Total deviations:** 1 auto-fixed (Rule 1 — test updated to reflect implemented behavior). **Impact:** negligible — the test was a Plan 01 implementation guard, now correctly updated for Plan 02.

## Threat Mitigations Verified

| Threat | Status |
|--------|--------|
| T-52-04: LLM inventing caveats | Mitigated — caveats computed by `_compute_cross_stage_caveats` BEFORE LLM call; re-attached authoritatively after narration |
| T-52-05: Fabricated numeric citation | Mitigated — `_check_grounding_pipeline` against `{"_stages":[...]}` union; test asserts fabricated value raises GroundingViolationError |
| T-52-06: Per-stage-strict over-rejection | Mitigated — ONE union check, not per-stage-strict; test asserts real cross-stage value passes |
| T-52-07: LLM SDK imported at module load | Mitigated — all provider/schema/_check_grounding imports are inside `pipeline_report()` body; module load stays LLM-free |

## Issues Encountered

None beyond the deviation documented above.

## Next Phase Readiness

- Plan 03 (MCP tool `fdars_build_pipeline_report`) can now wrap both `build_pipeline_report(run_llm=False)` and `pipeline_report()` directly.
- Auto-tuning (Phase 53) can consume `pipeline_report()` caveats as cross-stage signals — the per-stage isolation and Python-authoritative caveat properties are the load-bearing abstractions it needs.
- Guard-sync confirmed no-op: no new `_DIAGNOSTICS_METHODS` / `build_diagnostics._supported` key.

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| `python/fdars/advisor/_pipeline.py` exists | FOUND |
| `python/fdars/advisor/_schema.py` has PipelineReport | FOUND |
| `python/fdars/advisor/_prompts.py` has 'pipeline' clause | FOUND |
| `tests/test_pipeline_report_advise.py` exists | FOUND |
| Caveat tests pass: `pytest -k caveat` | 27 passed |
| Full pipeline test suite: `pytest tests/test_pipeline_report_advise.py` | 43 passed, 1 skipped |
| `from fdars.advisor._schema import PipelineReport` succeeds | PASS |
| Four pre-existing task prompts byte-identical | PASS |
| Fabricated value raises GroundingViolationError (offline mock) | PASS |
| Real cross-stage value passes grounding (offline mock) | PASS |
| Python-computed caveats attached to result | PASS |
| `test_live_pipeline_narration` skipped without ANTHROPIC_API_KEY | 1 skipped |
| Full suite: 934 passed, 9 skipped, 0 failed | PASS |
| No new `_DIAGNOSTICS_METHODS` key | PASS |
| Commits a717e44 and e407592 exist | VERIFIED |

---
*Phase: 52-pipeline-diagnostic-report*
*Completed: 2026-08-30*
