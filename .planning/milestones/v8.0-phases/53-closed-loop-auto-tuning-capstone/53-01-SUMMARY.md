---
phase: 53-closed-loop-auto-tuning-capstone
plan: "01"
subsystem: advisor
tags: [tuning, bounded-loop, state-machine, pydantic, offline-testing, termination-safety]

requires:
  - phase: 51-comparative-method-selection
    provides: _METRIC_REGISTRY + _extract_metric_value (direction + list-scalar extraction reused by tuning loop)
  - phase: 52-pipeline-diagnostic-report
    provides: schema fallback pattern (TuneProposal/TuningTrace follow same try/except ImportError twin-definition)

provides:
  - run_tuning_loop() bounded state machine with injectable propose_fn
  - _PARAM_REGISTRY (smoothing/basis/fpca/clustering tuneable=True; alignment/depth tuneable=False)
  - TuneProposal/TuningStep/TuningTrace/TuneResult schemas (pydantic + ImportError-fallback)
  - Optional Recommendation.parameter_delta (backward-compatible)
  - Offline test suite proving all 5 termination modes + determinism + guard

affects:
  - 53-02 (MCP heuristic tuning tool reuses run_tuning_loop)
  - 53-03 (Python API auto_tune uses LLM propose_fn + TuneResult)

actuals:
  tokens: 14200
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Injectable propose_fn seam: propose_fn(current_params, history) -> dict replaces all LLM/heuristic/mock variation"
    - "Budget-first termination precedence: step>=max_steps checked BEFORE propose_fn to prevent LLM cost waste"
    - "Goodhart guard: _check_guards runs AFTER fdars re-run; guard violation stops even when target improving"
    - "visited_params set with 4-sig-fig rounding catches float near-revisits"
    - "Twin-definition schema pattern: pydantic branch + except ImportError fallback stand-ins (mirrors Advice/Recommendation)"

key-files:
  created:
    - python/fdars/advisor/_tuning.py
    - tests/test_advisor_tuning.py
    - tests/test_advisor_schema.py
  modified:
    - python/fdars/advisor/_schema.py

key-decisions:
  - "Budget check is FIRST each iteration (before propose_fn) — prevents one wasted LLM call on the step that hits the cap (Pitfall 3)"
  - "Guard check is AFTER fdars re-run — diagnostics required to evaluate guard rules; oscillation-revisit is BEFORE re-run to avoid wasted fdars call"
  - "_METRIC_REGISTRY direction reused from _compare_methods; no local direction dict (no drift risk)"
  - "_extract_metric_value reused for cumulative_variance_explained last-element extraction"
  - "cluster_sizes guard uses isinstance-list check + min() to prevent silent TypeError (Pitfall 4 / T-53A-03)"
  - "_UnparseableProposalError exits loop immediately with n_steps=0, no retry (TUNE-01)"
  - "Recommendation.parameter_delta added as last optional field (backward-compatible; existing five-field construction unaffected)"
  - "run_tuning_loop accepts _run_method + _build_diagnostics test seam kwargs to avoid real fdars calls in unit tests"

patterns-established:
  - "Termination precedence: budget > parse_failure > oscillation-revisit > guard_stop > convergence > ping-pong"
  - "TDD RED commit (test(53-01):) + GREEN commit (feat(53-01):) per tracer task"

requirements-completed: [TUNE-01, TUNE-02, TUNE-05, TUNE-06]

coverage:
  - id: D1
    description: "run_tuning_loop terminates with stop_reason='budget' when max_steps reached (always-improve mock)"
    requirement: TUNE-01
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning.py#test_budget_exhaustion
        status: pass
    human_judgment: false
  - id: D2
    description: "run_tuning_loop terminates with stop_reason='converged' after K=3 consecutive non-improvements"
    requirement: TUNE-02
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning.py#test_convergence
        status: pass
    human_judgment: false
  - id: D3
    description: "run_tuning_loop terminates with stop_reason='oscillation' when param revisited"
    requirement: TUNE-02
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning.py#test_oscillation_param_revisit
        status: pass
    human_judgment: false
  - id: D4
    description: "run_tuning_loop terminates with stop_reason='parse_failure' on _UnparseableProposalError; proposer called exactly once, n_steps=0"
    requirement: TUNE-01
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning.py#test_parse_failure
        status: pass
    human_judgment: false
  - id: D5
    description: "Guard stop: clustering degenerate cluster (min cluster_size < 2) stops loop with guard_stop and non-empty guard_violations even while target is improving (Goodhart)"
    requirement: TUNE-05
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning.py#test_guard_stop_clustering
        status: pass
    human_judgment: false
  - id: D6
    description: "Determinism: identical inputs produce byte-identical TuningTrace field dicts"
    requirement: TUNE-01
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning.py#test_determinism
        status: pass
    human_judgment: false
  - id: D7
    description: "TuneProposal/TuningStep/TuningTrace/TuneResult importable and JSON-serialisable under both pydantic and ImportError-fallback"
    requirement: TUNE-06
    verification:
      - kind: unit
        ref: tests/test_advisor_schema.py#test_tune_schema_json_serialisable
        status: pass
    human_judgment: false
  - id: D8
    description: "Recommendation.parameter_delta defaults to None; existing five-field Recommendation construction unchanged"
    requirement: TUNE-06
    verification:
      - kind: unit
        ref: tests/test_advisor_schema.py#test_recommendation_parameter_delta_optional
        status: pass
    human_judgment: false
  - id: D9
    description: "_PARAM_REGISTRY contains 6 methods (smoothing/basis/fpca/clustering tuneable=True; alignment/depth tuneable=False) with correct target metrics and guard rules"
    requirement: TUNE-01
    verification:
      - kind: unit
        ref: "python -c \"from fdars.advisor._tuning import _PARAM_REGISTRY; assert set(_PARAM_REGISTRY)=={'smoothing','basis','fpca','clustering','alignment','depth'}\""
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-08-30
status: complete
---

# Phase 53 Plan 01: Closed-Loop Auto-Tuning TRACER Summary

**Bounded tuning loop state machine with injectable propose_fn, 5-mode termination (budget/converged/oscillation/guard_stop/parse_failure), TuneProposal/TuningTrace schemas, and an offline test suite proving all safety guarantees without API key or network.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-08-30T20:11:56Z
- **Completed:** 2026-08-30T20:19:13Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- `run_tuning_loop()` bounded state machine: injectable `propose_fn`, 5 termination conditions in strict precedence, guard diagnostics, oscillation detection (revisit + ping-pong), convergence window K=3
- `_PARAM_REGISTRY`: smoothing (n_basis/optimal_gcv/edf guard), basis (lambda_/optimal_edf/gcv guard), fpca (n_comp/cumulative_variance_explained/phase_leakage guard), clustering (k/mean_amplitude_separation/cluster_sizes guard), alignment+depth (tuneable=False)
- Schema types (pydantic + ImportError-fallback): TuneProposal, TuningStep, TuningTrace, TuneResult; Recommendation.parameter_delta (Optional, backward-compatible)
- Offline test suite: 18 tests covering all 5 stop reasons + determinism + fpca list-extraction + JSON-serialisability + guard helpers (no API key, no network)
- LLM-free at module load: grep confirms 0 anthropic imports; direction reused from `_METRIC_REGISTRY`, never a local dict

## Task Commits

Each task was committed atomically with TDD RED/GREEN:

1. **Task 1 (RED): Schema tests** — `3d3dcfc` (test: failing schema import tests)
2. **Task 1 (GREEN): Schema types** — `09b7ac7` (feat: TuneProposal/TuningStep/TuningTrace/TuneResult + parameter_delta)
3. **Task 2 (GREEN): Loop core + registry** — `c75c0a2` (feat: bounded loop core + _PARAM_REGISTRY + termination state machine)
4. **Task 3 (GREEN): Offline test suite** — `a7a2887` (test: all 5 stop reasons + determinism + guard + fpca extraction)

_Note: Task 2 had no separate RED commit — the acceptance criterion was the import-and-assert one-liner, which was confirmed failing before implementation._

## Files Created/Modified

- `python/fdars/advisor/_tuning.py` — NEW: loop core, _PARAM_REGISTRY, _UnparseableProposalError, helpers (_round_param, _extract_target, _is_improvement, _check_guards, _is_ping_pong), _make_mock_propose_fn test seam
- `python/fdars/advisor/_schema.py` — MODIFIED: added TuneProposal/TuningStep/TuningTrace/TuneResult + Recommendation.parameter_delta under both pydantic and ImportError-fallback branches
- `tests/test_advisor_tuning.py` — NEW: 18 offline tests, all 5 stop reasons, determinism, guard, fpca list extraction
- `tests/test_advisor_schema.py` — NEW: 7 schema tests, backward-compat verification

## Decisions Made

- Budget check is FIRST each iteration (before propose_fn) — prevents one wasted LLM/fdars call on the step that hits the cap (Pitfall 3)
- Guard check is AFTER fdars re-run (diagnostics required); oscillation-revisit is BEFORE re-run (avoids wasted fdars call on known repeat)
- Direction imported from `_METRIC_REGISTRY` in `_compare_methods`; never a local direction dict (no drift risk, RESEARCH "Don't Hand-Roll")
- `_extract_metric_value` reused from `_compare_methods` for cumulative_variance_explained last-element extraction (RESEARCH Open Question 3)
- cluster_sizes guard uses `isinstance(sizes, list) and len(sizes) > 0` before `min()` to prevent silent TypeError (Pitfall 4 / T-53A-03)
- `run_tuning_loop` accepts `_run_method` + `_build_diagnostics` kwargs as test seams; real imports are deferred inside the loop body (T-53A-04)
- `Recommendation.parameter_delta` added as the LAST field (keyword-only default None) so all existing five-field constructions remain valid

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria verified as specified. No architectural changes were required.

## Known Stubs

None — the tracer is production-quality. All 5 termination paths are fully implemented and exercised offline.

## Self-Check: PASSED

Files exist:
- `[ -f python/fdars/advisor/_tuning.py ]` → FOUND
- `[ -f python/fdars/advisor/_schema.py ]` → FOUND (modified)
- `[ -f tests/test_advisor_tuning.py ]` → FOUND
- `[ -f tests/test_advisor_schema.py ]` → FOUND

Commits exist (git log verified):
- `3d3dcfc` test(53-01): schema RED — FOUND
- `09b7ac7` feat(53-01): schema GREEN — FOUND
- `c75c0a2` feat(53-01): loop core — FOUND
- `a7a2887` test(53-01): test suite — FOUND

Test results:
- `tests/test_advisor_tuning.py` — 18 passed
- `tests/test_advisor_schema.py` — 7 passed
- `tests/test_advisor_gemini_schema.py` — 6 passed (no regression)
- LLM-free check: `grep -v '^#' python/fdars/advisor/_tuning.py | grep -c anthropic` → 0

## Issues Encountered

None.

## Next Phase Readiness

- Wave 1 tracer is committed and green; all safety guarantees proven offline
- Plan 53-02 (MCP `fdars_auto_tune` + heuristic propose_fn) can use `run_tuning_loop` with `_run_method`/`_build_diagnostics` from the real MCP runner
- Plan 53-03 (Python API `auto_tune()` + LLM propose_fn) can build the LLM closure over `advise()` and populate `Recommendation.parameter_delta`
- No blockers

---
*Phase: 53-closed-loop-auto-tuning-capstone*
*Completed: 2026-08-30*
