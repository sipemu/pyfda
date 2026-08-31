---
phase: 53-closed-loop-auto-tuning-capstone
plan: "02"
subsystem: advisor
tags: [tuning, llm-proposal, grounding-invariant, parameter-proposal, offline-testing, parse-failure-no-retry, clamping]

requires:
  - phase: 53-01
    provides: run_tuning_loop, _PARAM_REGISTRY, _UnparseableProposalError, TuneResult, Recommendation.parameter_delta

provides:
  - auto_tune() Python API in advisor/__init__.py (added to __all__)
  - 'parameter_proposal' task clause in advisor/_prompts.py (no-numeric-prediction prohibition)
  - tests/test_advisor_tuning_llm.py (14 offline tests with FakeProvider — no API key, no network)

affects:
  - 53-03 (eval harness: auto_tune returns Phase-54-ready TuneResult with rich trace)
  - 54 (eval): auto_tune().trace is the input to the evaluation harness

actuals:
  tokens: 14800
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "_intercepting_build wrapper: wraps _build_diagnostics to share current_diag with propose_fn closure without double fdars re-run"
    - "FakeProvider satisfies Provider protocol (runtime_checkable) for fully offline testing"
    - "History passed in domain_context OUTSIDE the Diagnostics block (Pitfall 1: _check_grounding only sees current-step diagnostics)"
    - "Out-of-range clamp: max(lo, min(hi, raw_val)) + int-cast for int params — never rejects, always records clamped param_after"
    - "Parse-failure-no-retry: wrong param name OR missing parameter_delta raises _UnparseableProposalError immediately, loop exits parse_failure without a second advise() call"

key-files:
  created:
    - tests/test_advisor_prompts_parameter_proposal.py
    - tests/test_advisor_tuning_llm.py
  modified:
    - python/fdars/advisor/_prompts.py
    - python/fdars/advisor/__init__.py

key-decisions:
  - "auto_tune passes history in domain_context BEFORE the Diagnostics block so _check_grounding only sees current-step numbers (Pitfall 1, T-53B-04)"
  - "_intercepting_build wraps _build_diagnostics to share current_diag with LLM closure — avoids double fdars call per step"
  - "Wrong param name in parameter_delta exits parse_failure immediately (no retry); same as absent parameter_delta"
  - "Out-of-range new_value is CLAMPED (not rejected); clamped value is recorded in TuningStep.param_after (T-53B-02)"
  - "FakeProvider implements Provider protocol structurally (runtime_checkable): name, model, supports_native_structured_output attributes required for resolve_provider isinstance check"
  - "parameter_proposal clause uses STRICT PROHIBITION with explicit list of qualitative direction examples (should decrease, should increase, likely to improve)"
  - "TuneResult.improved uses _is_improvement from _tuning (reuses direction from _METRIC_REGISTRY — no drift risk)"

requirements-completed: [TUNE-03]

coverage:
  - id: E1
    description: "auto_tune(method='alignment') raises ValueError naming the reason"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneRejectsNonTuneable.test_alignment_raises_value_error
        status: pass
    human_judgment: false
  - id: E2
    description: "auto_tune(method='depth') raises ValueError naming the reason"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneRejectsNonTuneable.test_depth_raises_value_error
        status: pass
    human_judgment: false
  - id: E3
    description: "auto_tune completes offline with FakeProvider and no ANTHROPIC_API_KEY"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneOfflineNoApiKey.test_offline_no_api_key
        status: pass
    human_judgment: false
  - id: E4
    description: "Result is a TuneResult with populated trace and stop_reason"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneReturnsTuneResult
        status: pass
    human_judgment: false
  - id: E5
    description: "Out-of-range new_value above hi is clamped to hi; recorded in TuningStep.param_after"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneClampOutOfRange.test_clamps_above_range
        status: pass
    human_judgment: false
  - id: E6
    description: "Out-of-range new_value below lo is clamped to lo; recorded in TuningStep.param_after"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneClampOutOfRange.test_clamps_below_range
        status: pass
    human_judgment: false
  - id: E7
    description: "Missing parameter_delta exits parse_failure immediately; advise called exactly once"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneParseFailureNoRetry.test_advise_called_exactly_once_on_parse_failure
        status: pass
    human_judgment: false
  - id: E8
    description: "Wrong param name in parameter_delta exits parse_failure"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneParseFailureNoRetry.test_wrong_param_name_exits_parse_failure
        status: pass
    human_judgment: false
  - id: E9
    description: "auto_tune in fdars.advisor.__all__; importable directly"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_tuning_llm.py#TestAutoTuneInAllExports
        status: pass
    human_judgment: false
  - id: E10
    description: "_system_prompt('parameter_proposal') returns prompt with parameter_delta and no-numeric-prediction prohibition; 5 prior families unchanged"
    requirement: TUNE-03
    verification:
      - kind: unit
        ref: tests/test_advisor_prompts_parameter_proposal.py
        status: pass
    human_judgment: false

duration: 18min
completed: 2026-08-30
status: complete
---

# Phase 53 Plan 02: LLM Proposal Path — auto_tune() + parameter_proposal Clause Summary

**LLM-backed closed-loop tuning: auto_tune() drives the wave-1 loop core via a schema-validated, clamped propose_fn; the 'parameter_proposal' prompt clause forbids numeric predictions; all behavior proven offline with an injected FakeProvider.**

## Performance

- **Duration:** 18 min
- **Completed:** 2026-08-30
- **Tasks:** 2
- **Commits:** 4 (2 RED + 2 GREEN, per TDD discipline)
- **Files modified:** 4

## Accomplishments

- `auto_tune(dataset_id, method, *, target_metric, max_steps, domain_context, model, provider, guard, _run_method, _build_diagnostics, **initial_params) -> TuneResult` added to `advisor/__init__.py` and `__all__`
- `_make_llm_propose_fn` closure (inline in `auto_tune`): calls `advise(task='parameter_proposal')`, reads `Recommendation.parameter_delta`, clamps `new_value` to spec range, raises `_UnparseableProposalError` on absent/wrong-param/non-numeric — loop exits parse_failure, no retry
- `_intercepting_build` wrapper: shares `current_diag` with the propose_fn closure without a double fdars call per step
- History passed in `domain_context` BEFORE the `Diagnostics` block — `_check_grounding` only sees current-step numbers (Pitfall 1, T-53B-04)
- `parameter_proposal` task clause in `_prompts.py`: explicit STRICT PROHIBITION forbidding numeric predictions in `expected_effect` and `rationale`; instructs qualitative direction only
- `FakeProvider` satisfying the `Provider` protocol (runtime_checkable) for fully offline testing
- 14 offline tests in `tests/test_advisor_tuning_llm.py`: non-tuneable ValueError, clamp above/below range, parse_failure with exactly-one-advise-call, wrong-param-name parse_failure, offline with no API key, TuneResult type/trace, improved flag
- 10 offline tests in `tests/test_advisor_prompts_parameter_proposal.py`: prompt content, prohibition presence, grounding invariant, case-insensitivity, regression for 5 prior families

## Task Commits

Each task committed atomically with TDD RED/GREEN:

1. **Task 1 (RED): Failing prompt tests** — `658015d` (test: RED for parameter_proposal clause)
2. **Task 1 (GREEN): parameter_proposal clause** — `69b941e` (feat: add clause with no-numeric-prediction prohibition)
3. **Task 2 (RED): Failing auto_tune tests** — `4f2c561` (test: RED for auto_tune LLM proposal path)
4. **Task 2 (GREEN): auto_tune implementation** — `f56c9e7` (feat: auto_tune + _make_llm_propose_fn closure)

## Files Created/Modified

- `python/fdars/advisor/_prompts.py` — MODIFIED: added 'parameter_proposal' to `_supported_tasks`; added elif branch with STRICT PROHIBITION clause; updated docstring
- `python/fdars/advisor/__init__.py` — MODIFIED: added `auto_tune()` + `_make_llm_propose_fn` closure; added to `__all__`
- `tests/test_advisor_prompts_parameter_proposal.py` — NEW: 10 offline tests for parameter_proposal clause
- `tests/test_advisor_tuning_llm.py` — NEW: 14 offline tests for auto_tune() LLM path

## Decisions Made

- History passed in domain_context BEFORE the Diagnostics block (Pitfall 1): `_check_grounding` reads `diagnostics` (current-step dict), not a merged dict with history. History values in domain_context are outside the grounding check's scope.
- `_intercepting_build` wrapper updates `_current_diag_holder[0]` on every `build_diagnostics` call — propose_fn closure reads the latest diag without a double fdars re-run.
- Wrong param name in `parameter_delta` exits parse_failure immediately (same path as absent parameter_delta) — prevents the LLM from redirecting the loop to a different param.
- `FakeProvider` must have `name`, `model`, `supports_native_structured_output` attributes for `isinstance(provider, _ProviderProtocol)` (runtime_checkable) in `resolve_provider` to recognize it.
- Evidence strings in `FakeProvider` responses use qualitative-only text (no numeric tokens) so `_check_grounding` never fires on synthetic diagnostics — offline tests remain green regardless of the fake diagnostics values.
- `TuneResult.improved` uses `_is_improvement` from `_tuning` (reuses `_METRIC_REGISTRY` direction — no drift risk).

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria verified as specified. No architectural changes were required.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

The existing `_check_grounding` guard continues to run on every `advise()` call in the `parameter_proposal` path — the grounding invariant is preserved by the existing mechanism.

## Known Stubs

None — all behavior implemented and exercised offline.

## Self-Check: PASSED

Files exist:
- `python/fdars/advisor/_prompts.py` → FOUND (modified)
- `python/fdars/advisor/__init__.py` → FOUND (modified)
- `tests/test_advisor_tuning_llm.py` → FOUND (created)
- `tests/test_advisor_prompts_parameter_proposal.py` → FOUND (created)

Commits exist (git log verified):
- `658015d` test(53-02): RED — failing tests for parameter_proposal prompt clause — FOUND
- `69b941e` feat(53-02): add parameter_proposal system-prompt clause — FOUND
- `4f2c561` test(53-02): RED — failing tests for auto_tune() — FOUND
- `f56c9e7` feat(53-02): auto_tune() LLM-backed API — FOUND

Test results:
- `tests/test_advisor_tuning_llm.py` — 14 passed
- `tests/test_advisor_prompts_parameter_proposal.py` — 10 passed
- `tests/test_advisor_tuning.py` — 18 passed (no regression)
- `tests/test_advisor_schema.py` — 7 passed (no regression)
- Total: 49 passed, 0 failed

Key guarantees verified:
- `auto_tune` in `fdars.advisor.__all__` — PASS
- `alignment` and `depth` raise `ValueError` — PASS
- `parameter_proposal` clause has no-numeric-prediction prohibition — PASS
- LLM-free at module load (no anthropic import at top level) — PASS

## Issues Encountered

1. `FakeProvider` initially lacked `name`, `model`, `supports_native_structured_output` attributes required by the `runtime_checkable` `Provider` protocol. `resolve_provider` uses `isinstance(provider, _ProviderProtocol)` — without these attributes, the fake was not recognized as a Provider instance and fell through to the `provider_name == "anthropic"` path, which tried to instantiate an AnthropicProvider (requiring an API key). Fix: added the three required class attributes to `FakeProvider`.

2. Evidence strings in initial `FakeProvider` responses contained `"test_value=1.0"` which has a numeric token `1.0`. `_check_grounding` checks evidence against the fake diagnostics dict (e.g. `{"optimal_gcv": 0.1}`) — `1.0` does not match `0.1`, causing `GroundingViolationError`. Fix: changed evidence strings to qualitative-only text with no numeric tokens.

Both issues were resolved inline (deviation Rule 3: blocking issues auto-fixed).

## Next Phase Readiness

- `auto_tune()` is Phase-54-ready: `TuneResult.trace` contains all steps with `param_before`, `param_after`, `target_before`, `target_after`, `accepted`, `stop_reason`, `guard_violations`
- `TuningTrace.stop_reason` covers all 5 termination modes for eval harness classification
- No blockers

---
*Phase: 53-closed-loop-auto-tuning-capstone*
*Completed: 2026-08-30*
