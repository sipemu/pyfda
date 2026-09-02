---
phase: 68-function-on-function-scalar-on-function-regression
plan: "02"
subsystem: regression
tags: [fof-regression, random-effects, pyo3, fdars-core, functional-data]

requires:
  - phase: 68-function-on-function-scalar-on-function-regression
    plan: "01"
    provides: fof_regression bound in src/regression_mod.rs; non-square fixture in tests/test_fof_regression.py

provides:
  - predict_fof (combined-refit stateless predict, numpy (n_new, m_y) output) bound in fdars.regression
  - fof_cv (K-fold CV over ncomp pairs, PyDict with candidates/cv_errors/optimal/min_cv_mse) bound in fdars.regression
  - fof_re_regression (mixed-effects FOF with REG-02 subject-id validation, 13-key PyDict) bound in fdars.regression
  - predict_fof_re (combined-refit stateless predict for RE model, numpy (n_new, m_y)) bound in fdars.regression
  - validate_subject_ids helper (shared by fof_re_regression and predict_fof_re)
  - 6 new pytest tests covering all four functions plus validation and error guards

affects:
  - 68-03 (scalar_on_function submodule — independent, different file)
  - Any downstream documentation phase referencing fdars.regression FOF surface

actuals:
  tokens: 17819
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Combined-refit stateless predict: refit from raw training data + new_x inside the binding, return numpy 2D — no opaque pyclass handle (mirrors Phase 67 ftsm_forecast)"
    - "validate_subject_ids helper: factor repeated REG-02 validation into a private Rust fn shared by fof_re_regression and predict_fof_re"
    - "FofReConfig struct literal (NOT #[non_exhaustive]): field-by-field assignment used for safety, direct literal confirmed legal"
    - "usize tuple conversion: Vec<(usize,usize)> → Vec<(i64,i64)> for Python-compatible candidate list"

key-files:
  created: []
  modified:
    - src/regression_mod.rs
    - tests/test_fof_regression.py

key-decisions:
  - "Combined-refit predict (no pyclass): predict_fof and predict_fof_re accept raw training data, refit internally, return numpy — consistent with Phase 67 precedent and locked CONTEXT.md decision"
  - "validate_subject_ids as shared helper fn: both fof_re_regression and predict_fof_re call it, keeping REG-02 validation DRY and the dedup logic in one place"
  - "Task 1 and Task 2 implemented in same atomic edit: all four functions (predict_fof, fof_cv, fof_re_regression, predict_fof_re) added in one src/regression_mod.rs modification; Task 2 verified independently before Task 3 tests"

requirements-completed: [REG-01, REG-02]

coverage:
  - id: D1
    description: "predict_fof bound and callable; returns numpy (n_new, m_y) on (10,18) fixture"
    requirement: REG-01
    verification:
      - kind: unit
        ref: tests/test_fof_regression.py#test_predict_fof_shape
        status: pass
    human_judgment: false
  - id: D2
    description: "fof_cv bound and callable; returns dict with candidates (list of 2-tuples), optimal (2-tuple), min_cv_mse > 0"
    verification:
      - kind: unit
        ref: tests/test_fof_regression.py#test_fof_cv
        status: pass
    human_judgment: false
  - id: D3
    description: "fof_re_regression bound with REG-02 validation; random_effects (5,18), sigma2_u (3,), n_subjects=5; fpca internals excluded"
    requirement: REG-02
    verification:
      - kind: unit
        ref: tests/test_fof_regression.py#test_fof_re_regression_shapes
        status: pass
    human_judgment: false
  - id: D4
    description: "predict_fof_re bound and callable; returns numpy (10,18)"
    requirement: REG-02
    verification:
      - kind: unit
        ref: tests/test_fof_regression.py#test_predict_fof_re_shape
        status: pass
    human_judgment: false
  - id: D5
    description: "Subject-id validation raises ValueError on wrong length and single group (REG-02 guard)"
    requirement: REG-02
    verification:
      - kind: unit
        ref: tests/test_fof_regression.py#test_subject_id_validation
        status: pass
    human_judgment: false
  - id: D6
    description: "Error guards: ncomp_x=0 and n_folds>n raise ValueError"
    verification:
      - kind: unit
        ref: tests/test_fof_regression.py#test_fof_error_guards
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-02
status: complete
---

# Phase 68 Plan 02: FOF Family Completion Summary

**Four FOF functions bound to fdars.regression — combined-refit predict pattern, REG-02 subject-id validation, and 10 passing tests on a 3-distinct-dim (N=30, MX=25, MY=18) non-square fixture**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-02T21:07:52Z
- **Completed:** 2026-09-02T21:11:07Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- `predict_fof` bound in `fdars.regression`: combined-refit (refit fof_regression internally from raw training data, predict on new_x), returns numpy 2D of shape (n_new, m_y). No opaque pyclass handle required.
- `fof_cv` bound: K-fold cross-validation over (ncomp_x, ncomp_y) grid; seed typed `u64` per Pitfall 7; PyDict with `candidates` (list of `(int,int)` tuples), `cv_errors` (numpy 1D), `optimal` (tuple), `min_cv_mse` (float > 0).
- `fof_re_regression` bound with REG-02 validation: length check + ≥2 distinct groups check applied BEFORE the core call via a shared `validate_subject_ids` helper. Returns 13-key PyDict; `fpca_x`/`fpca_y` intentionally excluded. `FofReConfig` struct literal used (confirmed NOT `#[non_exhaustive]`).
- `predict_fof_re` bound: same combined-refit pattern, same subject-id validation, returns numpy (n_new, m_y).
- All four functions registered in `regression_mod.rs::register()`.
- 6 new pytest tests appended to `tests/test_fof_regression.py` (10 total, all green): shape assertions, dict key/type checks, REG-02 error cases (both validation paths), and error guards.

## Task Commits

1. **Task 1+2: predict_fof, fof_cv, fof_re_regression, predict_fof_re** - `b8f3df9` (feat)
2. **Task 3: Tests** - `35f11d4` (test)

**Plan metadata:** committed with docs commit (see below)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/src/regression_mod.rs` — added `predict_fof`, `fof_cv`, `validate_subject_ids` (private helper), `fof_re_regression`, `predict_fof_re`; updated `register()` with all four new functions; updated section comment to "Plans 01-02"
- `/home/simonm/projects/rust/pyfda/tests/test_fof_regression.py` — appended 6 tests: `test_predict_fof_shape`, `test_fof_cv`, `test_fof_re_regression_shapes`, `test_predict_fof_re_shape`, `test_subject_id_validation`, `test_fof_error_guards`

## Decisions Made

- Combined-refit pattern (no pyclass): `predict_fof` / `predict_fof_re` take raw training data + new_x, refit internally, return numpy. Consistent with Phase 67 precedent and locked CONTEXT.md decision.
- `validate_subject_ids` as private helper: DRY between `fof_re_regression` and `predict_fof_re`; uses `sort_unstable` + `dedup` on a clone for allocation-minimal distinct count.
- Tasks 1 and 2 implemented in same atomic `src/regression_mod.rs` edit: practical implementation naturally grouped all four functions together. Task 2 acceptance criteria verified independently before moving to Task 3.

## Deviations from Plan

### Auto-fixed Issues

None — all four functions written together in a single Rust file edit as the natural implementation unit. This is a minor process deviation (Tasks 1 and 2 share one code commit) but has no impact on correctness, test coverage, or the acceptance criteria — both tasks were fully verified before Task 3.

---

**Total deviations:** 0 bugs auto-fixed. 1 minor process note (Tasks 1+2 combined commit).
**Impact on plan:** No scope creep. All acceptance criteria for Tasks 1-3 met independently.

## Issues Encountered

None.

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Subject-id validation (T-68-03 mitigation) implemented as specified. fpca_x/fpca_y excluded (T-68-04 mitigation verified by test assertion).

## Known Stubs

None.

## Self-Check: PASSED

- `src/regression_mod.rs` exists and contains predict_fof, fof_cv, fof_re_regression, predict_fof_re
- `tests/test_fof_regression.py` exists with 6 new tests (168 lines added)
- Commit `b8f3df9` exists: feat(68-02): bind predict_fof and fof_cv to fdars.regression
- Commit `35f11d4` exists: test(68-02): append predict_fof/cv/re tests to test_fof_regression.py
- `.venv/bin/pytest tests/test_fof_regression.py -x -q`: 10 passed in 0.81s

## Next Phase Readiness

- REG-01 complete: `fof_regression` + `predict_fof` callable, transposition-guarded
- REG-02 complete: `fof_re_regression` + `predict_fof_re` callable with subject-id validation; `random_effects` (5, 18) proven
- `fof_cv` bound and tested
- Ready for Phase 68 Plan 03: scalar_on_function submodule (independent file — `src/scalar_on_function_mod.rs`)

---
*Phase: 68-function-on-function-scalar-on-function-regression*
*Completed: 2026-09-02*
