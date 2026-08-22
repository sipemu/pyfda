---
phase: 37-group-a-regression-bindings
verified: 2026-08-20T21:47:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 37: Group A — Regression Bindings Verification Report

**Phase Goal:** Users can fit a concurrent (varying-coefficient) functional regression and an exponential-family functional GLM from the extended `fdars.regression` submodule, layout-correct across the numpy↔FdMatrix boundary.
**Verified:** 2026-08-20T21:47:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `from fdars.regression import concurrent_regression, functional_glm` both succeed (REGR-03) | VERIFIED | Import test confirms both symbols resolve. `TestRegressionImportPaths` (4 tests) passes. Both `m.add_function(wrap_pyfunction!(...))` calls present at `regression_mod.rs:1217-1218`. `register_submodule!(regression, ...)` in `lib.rs:48`. |
| 2 | `concurrent_regression(predictors, response, argvals=None, bandwidth=..., kernel=...)` returns dict with keys {beta_curve, intercept, fitted, residuals, argvals} (REGR-01) | VERIFIED | Live smoke: `sorted(result.keys()) == ['argvals', 'beta_curve', 'fitted', 'intercept', 'residuals']`. Test `test_smoke` asserts exact key set and all shapes. |
| 3 | `beta_curve` shaped `(p, m)` (predictor curves × grid, NOT observations × grid); p=3 transposition guard test exists and passes (REGR-01) | VERIFIED | Live call with p=3, n=10, m=12: `beta_curve.shape == (3, 12)`. `test_beta_curve_shape_p3` asserts `result["beta_curve"].shape == (3, 12)` with explicit `assert n != p`. `test_beta_curve_rows_are_curves` asserts each row has length m. All 3 shape-related tests pass. |
| 4 | `concurrent_regression` is deterministic and `residuals == response - fitted` element-wise (REGR-01) | VERIFIED | `test_determinism` asserts `np.array_equal` on beta_curve/fitted/residuals across two identical calls. `test_residuals_consistency` asserts `np.allclose(residuals, response - fitted, atol=1e-10, rtol=1e-10)`. Both pass. |
| 5 | `functional_glm(data, response, family='gaussian', n_comp=3, ...)` returns dict with 15 exposed fields (14 non-fpca struct fields + derived "family" string); embedded `fpca` field NOT present (REGR-02) | VERIFIED | Live call: 15 keys in dict, `"fpca" not in result`. `test_gaussian_smoke` asserts exact 15-key expected set and `"fpca" not in result`. Code at `regression_mod.rs:1095-1126` inserts 15 keys explicitly and comments "r.fpca is intentionally NOT inserted". |
| 6 | `family` dispatches GlmFamily (Binomial/Poisson/Gamma/Gaussian) by string; all 4 families return link-appropriate finite fitted_values; unknown family raises ValueError (REGR-02) | VERIFIED | `test_binomial_family`: fv in (0,1), `iterations <= 50`. `test_poisson_family`: fv > 0. `test_gamma_family`: fv > 0. `test_invalid_family`: `ValueError` with message "family must be 'binomial', 'poisson', 'gamma', or 'gaussian', got 'tweedie'". All pass. `family_from_str` at `regression_mod.rs:1069-1080` with mandatory `#[non_exhaustive]` wildcard. |
| 7 | All fallible paths via `to_pyresult()` (no `.unwrap()` in new functions); degenerate inputs raise ValueError (REGR-03) | VERIFIED | `grep -c '\.unwrap()\|\.expect(' regression_mod.rs` returns 0. `to_pyresult()` wraps both core calls at lines 1051-1057 and 1182-1190. `test_empty_predictors_raises`, `test_bad_bandwidth_raises`, `test_mismatched_predictor_raises`, `test_binomial_domain_guard`, `test_poisson_domain_guard`, `test_gamma_domain_guard` all assert `ValueError`. All pass. |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

---

### ROADMAP Success Criteria Mapping

| SC | Criterion | Status | Notes |
|----|-----------|--------|-------|
| SC1 | `concurrent_regression` with `list[np.ndarray]` predictors → dict; `beta_curve` shaped `(p, m)`, p≥2 transposition guard test | PASS | Truths 2, 3, 4 above. Live-confirmed `(3, 12)` at p=3, n=10. |
| SC2 | `functional_glm(data, response, argvals, family=..., n_comp=..., ...)` → dict (all fields); family dispatches GlmFamily by string; FPCA re-fit internally | PASS (with documented deviation) | All assertions hold. The `argvals` parameter in SC2/REGR-02 text is NOT present in `functional_glm` — this is a deliberate, research-backed deviation: `fdars-core 0.23.0` does not accept `argvals` in `functional_glm` (builds uniform grid internally at glm.rs:557). The PLAN explicitly states "Signature (per RESEARCH — NO argvals)" and RESEARCH.md verified this at the core source. The goal outcome (user can call functional_glm and get valid results) is fully achieved. |
| SC3 | Both registered with converters; `to_pyresult()` guards; degenerate inputs raise `ValueError` | PASS | Truth 7. Both functions in `register()`, 0 `.unwrap()` in new code. |
| SC4 | Docs caveats for Phase 41: Gamma inverse link (1/μ) and non-R-comparable AIC | PASS | `regression_mod.rs:1090-1092` contains the DOCS caveat comment block for Phase 41/DOCS-08. Also repeated in the `functional_glm` docstring at line 1143. |

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/regression_mod.rs` | Modified with new functions and converters | VERIFIED | Contains `concurrent_regression` (#[pyfunction], line 1037), `functional_glm` (#[pyfunction], line 1168), `concurrent_regr_result_to_pydict` (line 988), `functional_glm_result_to_pydict` (line 1095), `family_from_str` (line 1069), and register() additions at lines 1217-1218. |
| `tests/test_regression.py` | New pytest file with 3 test classes | VERIFIED | Present. 20 tests across `TestConcurrentRegression` (8), `TestFunctionalGlm` (8), `TestRegressionImportPaths` (4). All 20 pass. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `regression_mod.rs:1217` | `concurrent_regression #[pyfunction]` | `m.add_function(wrap_pyfunction!(concurrent_regression, m)?)` | WIRED | Confirmed in `register()` |
| `regression_mod.rs:1218` | `functional_glm #[pyfunction]` | `m.add_function(wrap_pyfunction!(functional_glm, m)?)` | WIRED | Confirmed in `register()` |
| `lib.rs:48` | `regression_mod::register` | `register_submodule!(m, "regression", regression_mod::register)` | WIRED | Pre-existing; unchanged |
| `predictors: Vec<PyReadonlyArray2>` | `Vec<FdMatrix>` | per-element `numpy2d_to_fdmatrix` collect `PyResult<Vec<_>>` at line 1045-1048 | WIRED | `PyO3 0.28 FromPyObject` for `Vec<T>` confirmed working by test suite |
| `fdars_core::concurrent_regression::concurrent_regression` | core call | `to_pyresult(...)` at line 1051-1057 | WIRED | No `.unwrap()`, errors surface as `ValueError` |
| `fdars_core::scalar_on_function::functional_glm` | core call | `to_pyresult(...)` at line 1182-1190 | WIRED | No `.unwrap()`, `family_from_str` gates on unknown tokens |
| `r.fpca` | NOT inserted in dict | `functional_glm_result_to_pydict` comment + absence | WIRED | "r.fpca is intentionally NOT inserted" comment at line 1124; `"fpca" not in result` confirmed live |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `concurrent_regression` / `beta_curve` | `r.beta_curve: FdMatrix` | `fdars_core::concurrent_regression::concurrent_regression` real kernel-smoothing computation | Yes — live-confirmed `(3,12)` with distinct values per row | FLOWING |
| `functional_glm` / `fitted_values` | `r.fitted_values: Vec<f64>` | `fdars_core::scalar_on_function::functional_glm` IRLS computation | Yes — live gaussian/binomial/poisson/gamma all return finite, link-appropriate values | FLOWING |
| `functional_glm` / `family` (derived) | `match r.family { ... }` | `r.family: GlmFamily` from core result struct | Yes — round-trips correctly for all 4 families | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `concurrent_regression` dict keys and shapes | `python -c "... result = regression.concurrent_regression(...); assert set(result.keys()) == {...}; assert result['beta_curve'].shape == (3, 12)"` | Keys correct, `beta_curve` = (3, 12), `fitted` = (10, 12), `intercept` = (12,), `argvals` = (12,), `residuals` = (10, 12) | PASS |
| `functional_glm` 15-key dict, no fpca, gaussian | `python -c "... result = regression.functional_glm(...); assert len(result) == 15; assert 'fpca' not in result"` | 15 keys, `fpca` absent, `family == 'gaussian'`, `fitted_values` len == 20 | PASS |
| Invalid family raises ValueError | `python -c "regression.functional_glm(..., family='tweedie')"` | `ValueError: family must be 'binomial', 'poisson', 'gamma', or 'gaussian', got 'tweedie'` | PASS |
| Empty predictors raises ValueError | `python -c "regression.concurrent_regression([], response)"` | `ValueError: invalid dimension for 'predictors': expected at least 1, got ...` | PASS |
| `functional_glm` has no `argvals` param | `inspect.signature(regression.functional_glm)` | params: `['data', 'response', 'family', 'n_comp', 'scalar_covariates', 'max_iter', 'tol']` — no `argvals` | PASS |
| Full test suite — no regression | `.venv/bin/python -m pytest tests/ -q` | **620 passed, 4 skipped, 0 failed** in 106.79s | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| REGR-01 | 37-01-PLAN.md | `concurrent_regression` with `list[np.ndarray]` predictors; `beta_curve (p,m)`; transposition guard at p≥2 | SATISFIED | Truths 2, 3, 4. Live and test-confirmed. |
| REGR-02 | 37-01-PLAN.md | `functional_glm`; all fields exposed (minus fpca); 4-family dispatch; ValueError on unknown | SATISFIED (with documented deviation) | Truth 5, 6. `argvals` omitted per research: core API does not support it. Goal outcome achieved. |
| REGR-03 | 37-01-PLAN.md | Both registered; `to_pyresult()` guards; degenerate inputs raise ValueError | SATISFIED | Truth 7. 0 `.unwrap()` in new code. All guard tests pass. |

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `src/convert.rs:57` (pre-existing) | `.unwrap()` in `fdmatrix_to_numpy2d` called by new converters | Info (pre-existing) | IN-02 from REVIEW — pre-existing tech debt, not introduced in Phase 37; unwrap cannot panic in practice (from_vec2 only fails on ragged inner vecs). Tracked for follow-up. |

No TBD/FIXME/XXX markers in either modified file. No return-null or placeholder stubs. No hardcoded empty data in non-test code.

---

### Review Warnings (WR-01/02/03) — Addressed Confirmation

| Warning | Issue | Resolution | Evidence |
|---------|-------|------------|---------|
| WR-01 | Code comment and test docstring both said "14 keys" but 15 keys are inserted | Fixed in commit `75e5345` | `regression_mod.rs:1086` now reads "15 keys are exposed"; `test_regression.py:152` docstring reads "15 keys, no fpca" |
| WR-02 | `test_smoke` did not assert shapes beyond `fitted` | Fixed in commit `75e5345` | `test_smoke` now asserts `beta_curve.shape == (1, m)`, `intercept.shape == (m,)`, `argvals.shape == (m,)`, `residuals.shape == (n, m)` (lines 48-59) |
| WR-03 | `test_binomial_family` used same seed for data and response RNG; no convergence assertion | Fixed in commit `75e5345` | Binomial test uses `rng = np.random.default_rng(202)` (different from data seed=1); asserts `result["iterations"] <= 50` (line 193-194) |

---

### Human Verification Required

None. All phase behaviors have automated verification. Full test suite passes (620/620).

---

### Gaps Summary

No gaps. All must-have truths are verified.

**Documented deviation (not a gap):** The `functional_glm` Python signature does NOT include the `argvals` parameter shown in ROADMAP SC2 and REGR-02 text. This was discovered during research (RESEARCH.md Pitfall 3) and explicitly decided in the PLAN ("NO argvals" per RESEARCH). The `fdars-core 0.23.0` core function `functional_glm` builds its own uniform grid internally; adding an `argvals` parameter would either be ignored or require core API changes outside this phase's scope. The goal outcome is fully achieved.

**Advisory (IN-02, pre-existing):** `fdmatrix_to_numpy2d` in `src/convert.rs:57` contains a pre-existing `.unwrap()` that the new converters call. This is a pre-existing pattern not introduced by Phase 37. It cannot panic in practice (from_vec2 only fails on ragged inner vecs, which core never produces). Tracked for follow-up cleanup.

---

_Verified: 2026-08-20T21:47:00Z_
_Verifier: Claude (gsd-verifier)_
