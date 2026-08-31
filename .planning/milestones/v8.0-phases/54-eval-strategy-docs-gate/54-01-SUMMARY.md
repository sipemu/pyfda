---
phase: 54-eval-strategy-docs-gate
plan: "01"
subsystem: advisor
tags: [eval, deterministic-fixtures, compare-methods, auto-tune, grounding, FakeProvider, offline-testing, EVAL-01, EVAL-02]

dependency_graph:
  requires:
    - phase: 51-comparative-method-selection
      provides: "compare_methods() offline core; fdars-sort winner authority (COMPARE-01); incommensurability guard (COMPARE-03)"
    - phase: 53-closed-loop-auto-tuning-capstone
      provides: "auto_tune() API; run_tuning_loop with injectable seams; TuneResult/TuningTrace schema; FakeProvider pattern"
  provides:
    - "tests/test_advisor_eval.py — 14 offline deterministic eval tests + 1 env-gated live smoke test"
    - "TestComparativeEval: known-best winner assertion (fdars-sort, run_llm=False), determinism, grounding-pass offline (EVAL-01)"
    - "TestAutoTuneEval: improving-direction, bounded-termination, offline-seams, grounding-pass assertions (EVAL-02)"
    - "test_eval_live_comparison_smoke: env-gated winner-preservation smoke (skips without key; no LLM-as-judge)"
  affects:
    - "54-02..54-04 (docs plans): EVAL-01/EVAL-02 requirements satisfied; milestone close can proceed"

actuals:
  tokens: 7284
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Known-from-data fixture pattern: construct candidate set with unambiguous winner by metric value engineering; assert fdars-sort selects it"
    - "Monotonically-improving seam: _make_fake_build_diagnostics with strictly improving target_values list for direction-assertion tests"
    - "FakeProvider with qualitative-only evidence: no numeric tokens in evidence strings so _check_grounding passes without any match required"
    - "Alternating-proposal FakeProvider: propose PROPOSED_VALUE + (call_count % 2) to avoid oscillation-revisit while exercising multiple accepted steps"
    - "env-gated live test named test_eval_live_* (not test_live_*) to preserve QUAL-02 exact-3 contract"

key-files:
  created:
    - tests/test_advisor_eval.py
  modified: []

key-decisions:
  - "All three task classes placed in a single file (test_advisor_eval.py) per plan design — no separate file per task class"
  - "Grounding-pass test for compare_methods uses kind='method' (valid Recommendation kind enum value) — 'selection' is not a valid kind; caught during TDD GREEN run"
  - "Alternating proposed param values (PROPOSED_VALUE + call_count % 2) prevents early oscillation-revisit termination while still testing the improving-direction property"
  - "Live smoke test named test_eval_live_comparison_smoke (not test_live_*) per QUAL-02 contract; env-gated via @pytest.mark.skipif; asserts winner-preservation only (no LLM-as-judge quality score)"
  - "Tasks 1, 2, and 3 committed atomically as one commit since all tests were authored in a single file pass with no intermediate broken state"

requirements-completed: [EVAL-01, EVAL-02]

coverage:
  - id: D1
    description: "Deterministic comparative eval: compare_methods(run_llm=False)[winner] == known-best on constructed dataset (EVAL-01)"
    requirement: EVAL-01
    verification:
      - kind: unit
        ref: tests/test_advisor_eval.py::TestComparativeEval::test_known_best_winner_equals_fdars_sort
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestComparativeEval::test_determinism_same_winner_on_repeated_calls
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestComparativeEval::test_grounding_pass_offline_fake_provider
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestComparativeEval::test_incommensurable_mixed_families_raises_value_error
        status: pass
    human_judgment: false
  - id: D2
    description: "Deterministic auto-tune eval: target metric moves in improving direction, bounded termination, fully offline (EVAL-02)"
    requirement: EVAL-02
    verification:
      - kind: unit
        ref: tests/test_advisor_eval.py::TestAutoTuneEval::test_target_metric_improves_in_known_direction
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestAutoTuneEval::test_improved_is_true_after_accepted_steps
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestAutoTuneEval::test_bounded_termination_stop_reason_in_known_set
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestAutoTuneEval::test_offline_no_api_key
        status: pass
      - kind: unit
        ref: tests/test_advisor_eval.py::TestAutoTuneEval::test_grounding_pass_qualitative_evidence_does_not_fire
        status: pass
    human_judgment: false
  - id: D3
    description: "Env-gated live smoke test skips cleanly without ANTHROPIC_API_KEY; no LLM-as-judge anywhere in file"
    verification:
      - kind: unit
        ref: "env -u ANTHROPIC_API_KEY .venv/bin/python -m pytest tests/test_advisor_eval.py -q → 14 passed, 1 skipped"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-08-30
status: complete
---

# Phase 54 Plan 01: Eval Strategy (Deterministic Offline Fixtures) Summary

**Deterministic eval fixtures for 'good advice' — known-from-data comparative winner and auto-tune improving-direction assertions, fully offline via FakeProvider and injectable seams (EVAL-01, EVAL-02)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-08-30T21:26:07Z
- **Completed:** 2026-08-30T21:29:24Z
- **Tasks:** 3 (all in one file, committed atomically)
- **Files modified:** 1

## Accomplishments

- `tests/test_advisor_eval.py` created with 668 lines and 15 tests (14 offline + 1 env-gated)
- `TestComparativeEval` (8 tests): constructed candidate set with unambiguous winner (`mean_amplitude_separation=0.91` vs 0.55 and 0.30); asserts `compare_methods(run_llm=False)["winner"]` equals the known-best label; tests determinism on repeated calls; grounding-pass with offline FakeProvider (qualitative-only evidence); incommensurable-input ValueError guards
- `TestAutoTuneEval` (6 tests): monotonically-improving fake diagnostics (GCV 0.50→0.45→...) with alternating FakeProvider proposals; asserts target moves in lower-is-better direction per accepted step; `improved=True`; bounded `stop_reason`; tests both lower-is-better (smoothing GCV) and higher-is-better (clustering separation)
- `test_eval_live_comparison_smoke` (1 test, skipped without key): env-gated winner-preservation smoke, no LLM-as-judge quality scoring, named `test_eval_live_*` to preserve QUAL-02 exact-3 `test_live_*` contract
- All 14 offline tests pass; 1 live test skips cleanly without API key; no network, no LLM-as-judge in CI

## Task Commits

All three tasks completed atomically:

1. **Task 1: Comparative eval + Task 2: Auto-tune eval + Task 3: Env-gated live + CI policy** - `4e4213c` (test)

## Files Created/Modified

- `tests/test_advisor_eval.py` — 668 lines; `TestComparativeEval` (EVAL-01), `TestAutoTuneEval` (EVAL-02), `test_eval_live_comparison_smoke` (env-gated smoke)

## Decisions Made

- Grounding-pass test uses `kind="method"` for the Recommendation — `"selection"` is not a valid enum value; caught as Rule 1 auto-fix during TDD GREEN run
- Alternating param proposals (`PROPOSED_VALUE + call_count % 2`) prevent early oscillation-revisit termination while testing multi-step improving direction
- Single atomic commit for all three tasks since the file was authored cleanly in one pass with no intermediate broken state

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Invalid Recommendation kind value in grounding-pass test**
- **Found during:** Task 1 (comparative eval, TDD GREEN run)
- **Issue:** Used `kind="selection"` in the FakeProvider's fake Advice, but Recommendation.kind is a Literal enum accepting only `"parameter"`, `"method"`, or `"none"`
- **Fix:** Changed `kind="selection"` to `kind="method"` in `test_grounding_pass_offline_fake_provider`
- **Files modified:** tests/test_advisor_eval.py
- **Verification:** `pytest tests/test_advisor_eval.py -k "Comparative" -x -q` exits 0
- **Committed in:** 4e4213c (task commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug in test fixture)
**Impact on plan:** Minor — single-line fix; did not affect scope or test coverage design.

## Issues Encountered

None — all acceptance criteria passed after the single auto-fix above.

## Self-Check

Verified files exist on disk:
- `tests/test_advisor_eval.py`: exists
- `.planning/phases/54-eval-strategy-docs-gate/54-01-SUMMARY.md`: exists

Verified commits:
- 4e4213c: `test(54-01): deterministic offline eval fixtures for comparative + auto-tune` — exists

Acceptance criteria verified:
- `.venv/bin/python -m pytest tests/test_advisor_eval.py -k "Comparative" -x -q` → 8 passed (exit 0)
- `.venv/bin/python -m pytest tests/test_advisor_eval.py -k "AutoTune" -x -q` → 6 passed (exit 0)
- `env -u ANTHROPIC_API_KEY .venv/bin/python -m pytest tests/test_advisor_eval.py -q` → 14 passed, 1 skipped (exit 0)
- Live test name: `test_eval_live_comparison_smoke` (does not start with `test_live_`, QUAL-02 preserved)
- No LLM-as-judge anywhere in file

## Self-Check: PASSED

## Next Phase Readiness

EVAL-01 and EVAL-02 satisfied. Ready for 54-02 (comparative method-selection docs page + SVG), 54-03 (pipeline diagnostic report docs), and 54-04 (auto-tune docs + blocking human diagram review gate).

---
*Phase: 54-eval-strategy-docs-gate*
*Completed: 2026-08-30*
