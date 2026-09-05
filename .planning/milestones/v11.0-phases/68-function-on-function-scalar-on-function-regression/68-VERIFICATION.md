---
phase: 68-function-on-function-scalar-on-function-regression
verified: 2026-09-02T21:34:19Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 68: Function-on-Function / Scalar-on-Function Regression — Verification Report

**Phase Goal:** Users can run function-on-function regression (incl. random effects) and the new additive/generalized scalar-on-function models with variable/model selection, via `fdars.regression` (extended) and a new `fdars.scalar_on_function` submodule.
**Verified:** 2026-09-02T21:34:19Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `fof_regression` (+ `predict_fof`) callable via `fdars.regression`, returns beta-surface/result PyDict, transposition- and argvals-guarded (REG-01) | VERIFIED | Live: `beta_surface.shape == (18, 25)` on N=30/MX=25/MY=18 fixture; 9-key dict confirmed; fpca_x/fpca_y absent; `pytest tests/test_fof_regression.py` 10 passed (incl. plan-01 tracer + predict tests) |
| 2 | `fof_re_regression` (+ `predict_fof_re`) callable with subject-id validation for random-effects structure (REG-02) | VERIFIED | Live: negative IDs raise `ValueError("non-negative integers...wrapped to 18446744073709551615")`; single-group raises `ValueError("at least 2 distinct subjects")`; 13-key dict exhaustively asserted (`set(result) == expected_re_keys`); `predict_fof_re` single-group test present (WR-03 fix) |
| 3 | `fof_cv` callable via `fdars.regression`, returns candidates/optimal/cv_errors/min_cv_mse | VERIFIED | Function bound and registered at `regression_mod.rs:1222`; test `test_fof_cv` checks 4-key dict, candidates as list of 2-tuples, min_cv_mse > 0 |
| 4 | `fdars.scalar_on_function` import succeeds — submodule registered in `lib.rs` + `__init__.py` (REG-03) | VERIFIED | `lib.rs:30` declares `mod scalar_on_function_mod`; `lib.rs:66` registers via `register_submodule!`; `__init__.py:58` adds `"scalar_on_function"` to `_submodule_names`; live import succeeds |
| 5 | `fam`, `fregre_gkam`, `fregre_gsam` callable via `fdars.scalar_on_function`, returning correct shapes/keys | VERIFIED | All three bound at `scalar_on_function_mod.rs:455-457`; `test_fam_returns_correct_keys_and_shapes` confirms `fitted_values.shape == (30,)` and 7-key dict; `test_fregre_gkam_two_predictors` confirms `converged` is bool and `bandwidths.shape == (2,)` on 2-predictor fixture |
| 6 | `variable_selection` callable, rejects invalid penalty with ValueError; `active_predictors.shape == (2,)` on 2-predictor fixture | VERIFIED | `penalty_from_str` rejects unsupported penalties via `Err`-arm; `test_variable_selection_invalid_penalty_raises` uses `pytest.raises(ValueError, match="unsupported")`; `test_variable_selection_group_lasso` confirms `active_predictors.shape == (2,)` |
| 7 | `model_selection_ncomp` callable via `fdars.scalar_on_function`, returns `best_ncomp >= 1` for aic/bic/gcv | VERIFIED | Copied verbatim from `regression_mod.rs`; three tests (`test_model_selection_ncomp_gcv/aic/bic`) all assert `best_ncomp >= 1` |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/regression_mod.rs` | FOF functions + validation helper | VERIFIED | 59 719 bytes; `fof_regression`, `predict_fof`, `fof_cv`, `fof_re_regression`, `predict_fof_re` all defined and registered at lines 1220-1224; `validate_subject_ids` helper at line 1442 with WR-01 `I64_MAX_AS_USIZE` guard |
| `src/scalar_on_function_mod.rs` | New submodule with 5 SoF functions | VERIFIED | 17 590 bytes; all five functions defined; `register` fn at lines 454-460; `penalty_from_str` helper with `Err`-arm for unsupported penalties |
| `src/lib.rs` | `mod scalar_on_function_mod` + `register_submodule!` | VERIFIED | Line 30: `mod scalar_on_function_mod;`; line 66: `register_submodule!(m, "scalar_on_function", scalar_on_function_mod::register)` |
| `python/fdars/__init__.py` | `"scalar_on_function"` in `_submodule_names` | VERIFIED | Line 58 adds the entry with a Phase 68 comment |
| `tests/test_fof_regression.py` | Non-square FOF tests + validation + error guards | VERIFIED | 13 262 bytes; 10 test functions covering fit/predict/cv/re-fit/re-predict/validation/error-guards; WR-02 exhaustive key-set assertion at line 234; WR-03 `predict_fof_re` single-group test at line 331 |
| `tests/test_scalar_on_function.py` | SoF tests for all five functions | VERIFIED | 8 166 bytes; 10 test functions; invalid-penalty `pytest.raises(ValueError)` present |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `fdars.regression.fof_regression` | `fdars_core::fof_regression::fof_regression` | `regression_mod.rs:1289` | WIRED | Direct `fdars_core::fof_regression::fof_regression(...)` call |
| `fdars.regression.fof_re_regression` | `validate_subject_ids` + `fdars_core::fof_regression::fof_re_regression` | `regression_mod.rs:1539,1547` | WIRED | Validation called before core; `FofReConfig` struct literal |
| `fdars.regression.predict_fof_re` | `validate_subject_ids` + `fdars_core::fof_regression::predict_fof_re` | `regression_mod.rs:1632,1640,1643` | WIRED | Both callers share `validate_subject_ids` (WR-01 fix applies to both) |
| `fdars.scalar_on_function` | `scalar_on_function_mod::register` | `lib.rs:66` + `__init__.py:58` | WIRED | `register_submodule!` macro wires the native side; `_submodule_names` wires the Python side |
| `variable_selection` | `penalty_from_str` | `scalar_on_function_mod.rs:27-37` | WIRED | `Err`-arm mandatory because `VarSelectPenalty` is `#[non_exhaustive]`; rejects "group_mcp"/"group_scad" |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `beta_surface` shape (18, 25) on N=30/MX=25/MY=18 fixture | Python: `result['beta_surface'].shape == (MY, MX)` | `(18, 25)` | PASS |
| Negative `subject_ids` raises `ValueError` (WR-01 fix) | Python: `r.fof_re_regression(..., [-1,...], ...)` | `ValueError: ...non-negative integers...wrapped to 18446744073709551615` | PASS |
| Single-group `subject_ids` raises `ValueError` | Python: `r.fof_re_regression(..., zeros(N), ...)` | `ValueError: at least 2 distinct subjects` | PASS |
| Phase tests | `.venv/bin/pytest tests/test_fof_regression.py tests/test_scalar_on_function.py -q` | 20 passed in 0.82s | PASS |
| Full suite regression check | `.venv/bin/pytest tests/ -q` | 5386 passed, 10 skipped, 120 warnings | PASS — no regressions |

---

## Code Review Warnings — Fix Confirmation

All three warnings from `68-REVIEW.md` were fixed per `68-REVIEW-FIX.md` (commit `86cface`, `5ea7023`, `84ba2e8`; all_fixed status):

| Warning | Fix | Confirmed |
|---------|-----|-----------|
| WR-01: Negative `subject_ids` wraps silently to `usize::MAX` | `I64_MAX_AS_USIZE` sentinel in `validate_subject_ids`; both callers (`fof_re_regression`, `predict_fof_re`) share the helper | Yes — live test passes |
| WR-02: `fof_re_regression` key-set not exhaustively tested | `assert set(result) == expected_re_keys` added at `test_fof_regression.py:239` | Yes — 13-key exact-match assertion present |
| WR-03: `predict_fof_re` single-group case not tested | `pytest.raises(ValueError, match="at least 2 distinct subjects")` for `predict_fof_re` at line 331 | Yes — test present and passing |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REG-01 | 68-01, 68-02 | `fof_regression` + `predict_fof` extending `fdars.regression`, transposition- and argvals-guarded | SATISFIED | `beta_surface (18,25)` verified live; 9-key dict; `fof_cv` also bound |
| REG-02 | 68-02 | `fof_re_regression` + `predict_fof_re` with subject-id validation | SATISFIED | Validation guards confirmed for negative IDs, single-group, wrong-length; `random_effects.shape == (5,18)` in test |
| REG-03 | 68-03 | `fam`, `fregre_gkam`, `fregre_gsam`, `variable_selection`, `model_selection_ncomp` via `fdars.scalar_on_function` | SATISFIED | All five callable; submodule registered in `lib.rs` + `__init__.py`; `penalty_from_str` rejects invalid penalties |

---

## Anti-Pattern Scan

Files modified in phase: `src/regression_mod.rs`, `src/scalar_on_function_mod.rs`, `src/lib.rs`, `python/fdars/__init__.py`, `tests/test_fof_regression.py`, `tests/test_scalar_on_function.py`.

No `TBD`, `FIXME`, or `XXX` markers found in any of the above files. No stub return patterns (`return null`, empty dict with no real data, placeholder arrays). All implementations call into `fdars_core` and convert real return values.

---

## Human Verification Required

None. All truths are verified by code inspection and live behavioral checks (imports, shape assertions, validation, full test suite).

---

_Verified: 2026-09-02T21:34:19Z_
_Verifier: Claude (gsd-verifier)_
