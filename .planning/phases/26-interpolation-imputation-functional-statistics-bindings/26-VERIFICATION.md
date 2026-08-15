---
phase: 26-interpolation-imputation-functional-statistics-bindings
verified: 2026-08-15T18:21:52Z
status: passed
score: 8/8
behavior_unverified: 0
overrides_applied: 0
---

# Phase 26: Interpolation, Imputation & Functional Statistics Bindings — Verification Report

**Phase Goal:** Users can spline-interpolate onto off-grid points with a chosen extrapolation policy, impute missing values on a regular grid, and compute functional variance/std/covariance plus depth-based median and trimmed mean — all layout-correct across the numpy↔FdMatrix boundary.

**Verified:** 2026-08-15T18:21:52Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | REPR-01: `from fdars.represent import spline_interpolate` works; interpolates n curves onto off-grid query points returning an n×q array, layout-correct per-curve | VERIFIED | Import confirmed live; `spline_interpolate` present in `src/represent_mod.rs` routing through `fdmatrix_to_numpy2d`; per-curve `sin((i+1)·π·t)` round-trip test with `assert_allclose` per curve passes (36 tests, 0 failed) |
| 2 | REPR-02: ExtrapolationPolicy string param ('boundary'/'exception'/'fill'/'periodic') + `_ => PyValueError` fallback arm; 'fill' takes fill_value; out-of-domain behavior per policy | VERIFIED | `parse_extrapolation_policy()` in `represent_mod.rs` lines 200–213 has all four arms plus `_ =>` fallback; live check: unknown policy raises `ValueError: policy must be 'boundary', 'exception', 'fill', or 'periodic'`; OOD + exception raises `ValueError`; all four policy arms tested in `test_represent.py` |
| 3 | REPR-03: `impute_missing_values` fills NaN via 'linear'/'mean'/'constant'; `fd.interpolate()` and `fd.impute()` reachable as Fdata methods | VERIFIED | `impute_missing_values` in `represent_mod.rs` with `ImputationMethod` dispatch; `Fdata.interpolate()` at `fdata_class.py:630–682`, `Fdata.impute()` at `fdata_class.py:684+`; live check: `hasattr(fd, 'interpolate')` and `hasattr(fd, 'impute')` both `True`; all-NaN row raises `ValueError`; imputation tests pass |
| 4 | Degenerate inputs raise Python ValueError via `to_pyresult()`, not a Rust panic | VERIFIED | `grep -c '.unwrap()'` on `represent_mod.rs` → 0; every `Result` path uses `to_pyresult(...)?`; OOD+exception, all-NaN, unknown policy/method all raise `ValueError` live |
| 5 | STAT-01: `functional_variance`, `functional_std`, `functional_covariance` present in `fdars.fdata`; covariance layout-correct — diagonal equals `functional_variance` AND known off-diagonal cov[0,1]=7/3 for hand-chosen dataset | VERIFIED | All three symbols present; live check: `diag(cov)==var` passes `assert_allclose(rtol=1e-12)`; `cov[0,1]=7/3` passes `assert_allclose(rtol=1e-12)`; multi-curve transposition round-trip test in `test_fdata_stats.py::TestFunctionalCovariance::test_multi_curve_transposition_round_trip` (diag==var + cov[0,1] matches numpy Bessel cross-covariance) — 33 tests pass |
| 6 | STAT-02: `depth_based_median` returns actual median curve (length-m 1-D float array equal to an observed row), never a bare int; `trim_mean(α=0)` equals `mean_1d` exactly | VERIFIED | Live check: `depth_based_median(X).shape == (3,)`, `ndim==1`, `dtype=float64`, `any(array_equal(result, X[i]))` True; `assert_allclose(trim_mean(X,0.0), mean_1d(X), atol=1e-15)` passes; binding in `fdata_mod.rs:432–442` resolves via `mat.row(idx)` — index never crosses to Python |
| 7 | Fdata convenience methods `fd.var()`, `fd.std()`, `fd.cov()`, `fd.median()` delegate correctly; `fd.median()` returns an Fdata row (n_obs=1) | VERIFIED | Methods at `fdata_class.py:433–626`; `fd.var()` → `_native.fdata.functional_variance(self.data)`; `fd.median()` → `_native.fdata.depth_based_median(self.data)` wrapped in `Fdata(curve[np.newaxis,:], ...)` with `id=["median"]`; tests assert `med.n_obs==1`, `med.n_points==fd.n_points`, data equals observed row |
| 8 | Layout: multi-curve transposition round-trip tests exist and guard the #33 bug class for both `spline_interpolate` (REPR) and `functional_covariance` (STAT) | VERIFIED | `test_represent.py::TestSplineInterpolateTracer::test_transposition_guard` (per-curve allclose + `not allclose(result[0], result[1], atol=0.05)`); `test_fdata_stats.py::TestFunctionalCovariance::test_multi_curve_transposition_round_trip` (5 curves × 4 grid points, diag==var + cov[0,1] vs numpy); both pass |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/represent_mod.rs` | New PyO3 module with 4 pyfunctions + register fn | VERIFIED | 243 lines; exports `spline_interpolate`, `spline_interpolate_with_policy`, `fdata_interpolate_with_policy`, `impute_missing_values`; all matrix returns via `fdmatrix_to_numpy2d` |
| `fdars.represent` native submodule | Registered in `src/lib.rs` and `python/fdars/__init__.py` | VERIFIED | `register_submodule!(m, "represent", represent_mod::register)` at `lib.rs:56`; `"represent"` in `_submodule_names` tuple at `__init__.py:51`; both `import fdars.represent` and `from fdars.represent import spline_interpolate` work live |
| `Fdata.interpolate()` and `Fdata.impute()` | Methods in `python/fdars/fdata_class.py` | VERIFIED | `interpolate()` at line 630, `impute()` at line 684; both substantive (delegate to `_native.represent`, return new `Fdata`) |
| `tests/test_represent.py` | 36 tests: tracer round-trip, policy dispatch, imputation, Fdata methods | VERIFIED | 36 tests exist; all pass (confirmed 69/69 for both test files) |
| `src/fdata_mod.rs` extended | 5 new pyfunctions + register lines | VERIFIED | `functional_variance`, `functional_std`, `functional_covariance`, `depth_based_median`, `trim_mean` at lines 330–496; all 5 in `register()` fn at lines 490–494 |
| `Fdata.var()`, `.std()`, `.cov()`, `.median()` | Methods in `python/fdars/fdata_class.py` | VERIFIED | All four methods present at lines 433–626; substantive delegators |
| `tests/test_fdata_stats.py` | 33 tests: var/std identity, cov transposition guard, depth median resolves, trim_mean identity, degenerate-input ValueError | VERIFIED | 33 tests exist; all pass |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/lib.rs` | `represent_mod::register` | `register_submodule!(m, "represent", represent_mod::register)` at line 56 | WIRED | Confirmed in file; `import fdars.represent` succeeds live |
| `python/fdars/__init__.py` | `fdars.represent` namespace | `"represent"` in `_submodule_names` at line 51; sys.modules loop | WIRED | Confirmed; `from fdars.represent import spline_interpolate` succeeds live |
| `Fdata.interpolate()` | `_native.represent.spline_interpolate_with_policy` | Direct call in `fdata_class.py:671` | WIRED | Substantive delegation; per-curve value test passes |
| `Fdata.impute()` | `_native.represent.impute_missing_values` | Direct call in `fdata_class.py` | WIRED | Substantive delegation; NaN-removal test passes |
| `functional_covariance` | `convert::fdmatrix_to_numpy2d` | `Ok(fdmatrix_to_numpy2d(py, &result))` at `fdata_mod.rs:408` | WIRED | Column-major transposition guard active; layout-correctness confirmed via diag==var AND known off-diagonal live |
| `depth_based_median` | `mat.row(idx)` → `vec_to_numpy1d` | `fdata_mod.rs:440–441` — index resolved before return | WIRED | Index never crosses to Python; returns length-m float64 array equal to an observed row — confirmed live |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `spline_interpolate` | `result` matrix | `fdars_core::spline_interpolate(&mat, &av, &qp, order)` | Yes — live core computation | FLOWING |
| `impute_missing_values` | `result` matrix | `fdars_core::impute_missing_values(&mat, &av, im)` | Yes — live core computation | FLOWING |
| `functional_covariance` | `result` FdMatrix | `fdars_core::fdata::functional_covariance(&mat)` | Yes — Bessel-corrected covariance | FLOWING |
| `depth_based_median` | `row_vec` | `mat.row(idx)` from resolved `fdars_core::fdata::depth_based_median(&mat)` | Yes — actual observed curve row | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| REPR-01/02/03 imports resolve | `python -c "from fdars.represent import spline_interpolate, spline_interpolate_with_policy, fdata_interpolate_with_policy, impute_missing_values"` | OK | PASS |
| `fd.interpolate` and `fd.impute` exist on Fdata | `hasattr(fd, 'interpolate')`, `hasattr(fd, 'impute')` | Both True | PASS |
| Unknown ExtrapolationPolicy → ValueError | `spline_interpolate_with_policy(..., policy='bogus')` | `ValueError: policy must be 'boundary', 'exception', 'fill', or 'periodic'` | PASS |
| OOD + 'exception' → ValueError | `spline_interpolate_with_policy(..., policy='exception', q=[1.5])` | `ValueError` raised | PASS |
| All-NaN row impute → ValueError | `impute_missing_values([[nan,nan,nan]], ...)` | `ValueError` raised | PASS |
| STAT-01: `functional_variance/std/covariance` exist | `hasattr(fdars.fdata, 'functional_variance')` etc. | All True | PASS |
| STAT-01: covariance layout — diag(cov)==var AND cov[0,1]==7/3 | `assert_allclose(np.diag(cov), var, rtol=1e-12)` + `assert_allclose(cov[0,1], 7/3, rtol=1e-12)` | Both pass | PASS |
| STAT-02: `depth_based_median` returns curve not int | `m.shape==(3,)`, `m.ndim==1`, `m.dtype==float64`, `any(array_equal(m, X[i]))` | All True | PASS |
| STAT-02: `trim_mean(α=0)==mean_1d` exactly | `assert_allclose(trim_mean(X,0.0), mean_1d(X), atol=1e-15)` | Pass | PASS |
| Full test suite (69 Phase 26 tests) | `.venv/bin/pytest tests/test_represent.py tests/test_fdata_stats.py -q` | 69 passed | PASS |
| No regressions (full suite) | `.venv/bin/pytest tests/ -q` | 328 passed, 4 skipped | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| REPR-01 | 26-01-PLAN.md | Spline-interpolate onto off-grid query points | SATISFIED | `spline_interpolate` + `spline_interpolate_with_policy` present, wired, tested with per-curve round-trip |
| REPR-02 | 26-01-PLAN.md | ExtrapolationPolicy string enum with forward-compatible fallback | SATISFIED | Four-arm + `_ => PyValueError` in `represent_mod.rs:204–212`; all arms tested live |
| REPR-03 | 26-01-PLAN.md | `impute_missing_values` + `fd.interpolate()`/`fd.impute()` Fdata methods | SATISFIED | All three artifacts present, wired, and passing tests |
| STAT-01 | 26-02-PLAN.md | `functional_variance/std/covariance`; covariance layout-correct by multi-curve round-trip | SATISFIED | All three present; `test_multi_curve_transposition_round_trip` asserts diag==var AND known off-diagonal |
| STAT-02 | 26-02-PLAN.md | `depth_based_median` resolves index→curve; `trim_mean(α=0)==mean` | SATISFIED | `mat.row(idx)` path in binding; live and test-confirmed |

---

### Anti-Patterns Found

None. No `TBD`, `FIXME`, or `XXX` markers in any of the five files modified or created by this phase. No `.unwrap()` calls on `Result<_, FdarError>` in `represent_mod.rs` (count: 0) or the new additions to `fdata_mod.rs` (count: 0).

---

### Human Verification Required

None. All must-haves are fully verified programmatically: imports resolve, behavioral spot-checks pass live, and 328 tests pass with no regressions.

---

## Verdict

Phase 26 achieves its goal completely. All five required bindings (`spline_interpolate*`, `fdata_interpolate_with_policy`, `impute_missing_values`, `functional_variance/std/covariance`, `depth_based_median`, `trim_mean`) are present, registered in the correct submodule namespaces (`fdars.represent` and `fdars.fdata`), wired through the column-major-safe `fdmatrix_to_numpy2d` / `vec_to_numpy1d` conversion helpers, and covered by behavioral tests. The mandated anti-regression guards for the #33 transposition bug class are confirmed real: the covariance test asserts both `diag(cov)==functional_variance` and a hand-computed off-diagonal value `cov[0,1]=7/3`, and the interpolation tracer asserts per-curve `allclose` on distinct `sin(k·π·t)` shapes — neither check can pass on a transposed matrix. The `depth_based_median` index-to-curve resolution is confirmed live (returns a `(3,) float64` array equal to an observed row, never an integer). The `ExtrapolationPolicy` fallback arm fires correctly on unrecognized strings. The full suite of 328 tests passes with 4 pre-existing skips and zero new failures.

---

_Verified: 2026-08-15T18:21:52Z_
_Verifier: Claude (gsd-verifier)_
