---
phase: 27-scoring-metrics-alignment-registration-bindings
verified: 2026-08-15T21:41:29Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 27: Scoring Metrics & Alignment/Registration Bindings — Verification Report

**Phase Goal:** Users can score functional predictions with five error metrics and run least-squares shift registration, registration-quality scoring, and banded elastic alignment — with every fallible input surfacing as a clean ValueError rather than a Rust panic.
**Verified:** 2026-08-15T21:41:29Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 5 metrics (functional_mae/mse/mape/msle/explained_variance) reachable via both import paths (STAT-03) | VERIFIED | Live import: `import fdars.scoring; [getattr(fdars.scoring, f) for f in [...]]` prints ok; `from fdars.scoring import functional_mse` works. Both import paths exercised in `tests/test_scoring.py::TestNamespace`. |
| 2 | functional_mse(X, X, argvals) == 0.0 for identical curves (STAT-03) | VERIFIED | Live: `fdars.scoring.functional_mse(y, y, av)` returned exactly `0.0`. 351 test_scoring.py tests include `test_identical_curves_zero` with `pytest.approx(0.0, abs=1e-12)`. |
| 3 | MAPE on near-zero true values raises ValueError; MSLE on values <= -1 raises ValueError (STAT-03) | VERIFIED | Live: MAPE raised `ValueError: ...MAPE is undefined when y_true contains values near zero`; MSLE raised `ValueError: ...MSLE requires y_true > -1; found y_true[0,0] = -1.5`. Test guards `test_raises_for_zero_y_true`, `test_raises_for_y_true_le_minus_one`, `test_raises_for_y_pred_le_minus_one` all green. |
| 4 | No .unwrap() in src/scoring_mod.rs (STAT-03 / T-27-01-01) | VERIFIED | `grep -n 'unwrap()' src/scoring_mod.rs` returns zero live code matches. Line 8 occurrence is inside a `//!` doc comment, not live code. |
| 5 | least_squares_shift_registration returns dict {registered_data (n,m), shifts (n,)} (ALGN-01) | VERIFIED | Live: `sorted(r.keys()) == ['registered_data', 'shifts']`; shape `(3,20)` and `(3,)` confirmed; dtype float64 confirmed. Test class `TestLeastSquaresShiftRegistration` (8 tests) green. |
| 6 | fd.shift_register() returns (registered Fdata, shifts ndarray) with same argvals (ALGN-01) | VERIFIED | Live: `type(registered).__name__ == 'Fdata'`; `shifts.shape == (5,)`; `np.allclose(registered.argvals, fd.argvals)` True; `registered.n_obs == fd.n_obs` True. `fdata_class.py` line 728 confirmed. |
| 7 | 3 quality scores (least_squares_score/pairwise_correlation_score/sobolev_least_squares_score) return finite floats; sobolev on non-uniform grid with lambda>0 raises ValueError (ALGN-02) | VERIFIED | Live: ls_score=0.000086 (finite, >=0); pc_score=0.998945 (finite, in [-1,1]); sobolev(lambda=0) equals least_squares_score exactly; non-uniform grid raised `ValueError: ...sobolev_least_squares_score with lambda>0 requires a uniform grid`. Test `test_sobolev_nonuniform_grid_raises_value_error` uses `pytest.raises(ValueError, match="(?i)uniform")`. |
| 8 | 3 *_with_band functions present (band_frac=None default); NO *_banded variants bound (ALGN-03) | VERIFIED | Live: all 3 reachable via attribute; `hasattr(almod, 'karcher_mean_banded')` etc. all False. Test `test_no_banded_variants_in_module` green. `grep -c 'karcher_mean_banded|elastic_self_distance_matrix_banded|elastic_cross_distance_matrix_banded' src/alignment_mod.rs` returns 0. |
| 9 | Banded distance matrices route through fdmatrix_to_numpy2d; multi-curve DISTINCT-per-curve transposition round-trip passes (ALGN-03 / #33 guard) | VERIFIED | Live: D[0,2]=1.920802 matches independent pairwise d(curve0,curve2)=1.920802; symmetric (D==D.T); zero diagonal. `test_multicurve_transposition_round_trip` green (distinct sin(k*pi*t) curves). |
| 10 | No .unwrap() on any fallible fdars-core Result in the new alignment wrappers (T-27-02-02) | VERIFIED | `awk 'NR>=2095' src/alignment_mod.rs | grep 'unwrap()'` returned zero matches. All fallible calls (`to_pyresult(...)`) chain the `?` operator; karcher_mean_with_band and the banded distance matrix fns are INFALLIBLE per fdars-core and are called without to_pyresult (correct). |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/scoring_mod.rs` | NEW module with 5 pyfunctions + register() | VERIFIED | 205 lines; all 5 pyfunctions + `pub fn register()` registered in all 5. No stubs, no unwrap(). |
| `tests/test_scoring.py` | NEW: namespace, hand-checked MSE, ValueError guards | VERIFIED | 288 lines; 23 test functions in 5 classes covering all acceptance criteria. |
| `src/lib.rs` | `mod scoring_mod;` + `register_submodule!(m, "scoring", ...)` | VERIFIED | `mod scoring_mod;` at line 26; `register_submodule!(m, "scoring", scoring_mod::register)` at line 58. |
| `python/fdars/__init__.py` | `"scoring"` in `_submodule_names` | VERIFIED | `"scoring"` at line 52 of the `_submodule_names` tuple. |
| `src/alignment_mod.rs` | +7 pyfunctions (all listed in plan) | VERIFIED | 2432 lines; 7 new functions at lines 2103-2358; registered at lines 2424-2430 with `// Phase 27-02:` comment. |
| `python/fdars/fdata_class.py` | `def shift_register(self, max_shift)` method | VERIFIED | Line 728; delegates to `_native.alignment.least_squares_shift_registration`; wraps result in Fdata; returns `(registered_fdata, result["shifts"])`. |
| `tests/test_alignment_registration.py` | NEW: 37 tests per SUMMARY | VERIFIED | 405 lines; 37 test functions across 6 test classes + 1 module-level grep-gate function. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/scoring_mod.rs` | `fdars.scoring` namespace | `register_submodule!(m, "scoring", scoring_mod::register)` in `src/lib.rs` | WIRED | Confirmed at lib.rs:58; live import succeeds. |
| `python/fdars/__init__.py` | `fdars.scoring` | `"scoring"` in `_submodule_names` | WIRED | Line 52; auto-registered in the loop at line 55. |
| `fd.shift_register()` | `fdars.alignment.least_squares_shift_registration` | `_native.alignment.least_squares_shift_registration(self.data, self.argvals, max_shift)` | WIRED | fdata_class.py lines 760-771; result dict unwrapped into Fdata + shifts ndarray. |
| `karcher_mean_with_band` | `fdmatrix_to_numpy2d` (transposition guard) | `aligned_data` and `gammas` set via `fdmatrix_to_numpy2d(py, &result.*)` | WIRED | alignment_mod.rs lines 2272-2276; confirmed in code. |
| `elastic_self_distance_matrix_with_band` | `fdmatrix_to_numpy2d` | `Ok(fdmatrix_to_numpy2d(py, &result))` | WIRED | alignment_mod.rs line 2316. |
| `elastic_cross_distance_matrix_with_band` | `fdmatrix_to_numpy2d` | `Ok(fdmatrix_to_numpy2d(py, &result))` | WIRED | alignment_mod.rs line 2357. |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `functional_mse` | result f64 | `fdars_core::functional_mse(&yt, &yp, &av)` | Yes — Simpson-integrated from actual matrices | FLOWING |
| `least_squares_shift_registration` | `registered_data` | `fdars_core::alignment::least_squares_shift_registration(&mat, &av, max_shift)?.registered_data` | Yes — real ShiftRegistrationResult | FLOWING |
| `least_squares_shift_registration` | `shifts` | `result.shifts` (Vec<f64> from fdars-core) | Yes | FLOWING |
| `karcher_mean_with_band` | `aligned_data` | `fdars_core::alignment::karcher_mean_with_band(...)`.aligned_data | Yes — real KarcherMeanResult | FLOWING |
| `elastic_self_distance_matrix_with_band` | return matrix | `fdars_core::alignment::elastic_self_distance_matrix_with_band(...)` | Yes — pairwise distances | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 5 scoring metrics importable | `python -c "import fdars.scoring; [getattr(fdars.scoring,f) for ...]"` | ok | PASS |
| functional_mse(X,X) == 0.0 | live Python call | 0.0 exactly | PASS |
| MAPE near-zero raises ValueError | live Python call | ValueError with NUMERICAL_EPS message | PASS |
| MSLE <= -1 raises ValueError | live Python call | ValueError with boundary message | PASS |
| least_squares_shift_registration dict shape | live Python call | keys=['registered_data','shifts'], shapes (3,20)/(3,) | PASS |
| fd.shift_register() returns (Fdata, ndarray) | live Python call | type=Fdata, shifts=(5,), argvals preserved | PASS |
| sobolev(lambda=0) == least_squares_score | live Python call | np.isclose=True (0.000086 vs 0.000086) | PASS |
| sobolev non-uniform grid raises ValueError | live Python call | ValueError with "uniform" message | PASS |
| All 3 _with_band functions present; no _banded bound | live Python call | All 3 present, 0 _banded names | PASS |
| Transposition round-trip D[0,2] | live Python call | 1.920802 == 1.920802 (rtol=1e-6) | PASS |
| Full test suite | `.venv/bin/pytest tests/ -q --tb=no` | **388 passed, 4 skipped** in 105s | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| STAT-03 | 27-01-PLAN.md | 5 functional scoring metrics with ValueError guards | SATISFIED | All 5 live-importable; MSE(X,X)=0 confirmed; MAPE/MSLE ValueError confirmed; no unwrap(). |
| ALGN-01 | 27-02-PLAN.md | least_squares_shift_registration + fd.shift_register() | SATISFIED | Dict keys/shapes confirmed live; fd.shift_register() returns (Fdata, ndarray) with preserved argvals. |
| ALGN-02 | 27-02-PLAN.md | 3 quality scores; Sobolev uniform-grid requirement surfaced | SATISFIED | All 3 scores finite/in-range; sobolev(lambda=0)==ls_score; non-uniform raises clear ValueError. |
| ALGN-03 | 27-02-PLAN.md | 3 banded *_with_band fns; band_frac=None unbanded; transposition guard | SATISFIED | All 3 present; no _banded bound; transposition round-trip D[0,2] matches independent pairwise. |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/scoring_mod.rs` | 8 | `unwrap()` in `//!` doc comment | Info | Not live code — module-level doc string describing the absence of panics. No impact. |

No TODO/FIXME/TBD/XXX/PLACEHOLDER markers found in any phase-27 modified files. No empty implementations. No hardcoded static returns.

---

### Human Verification Required

None. All truths are mechanically verified at all four levels (exists, substantive, wired, data-flowing). No visual/UI behavior, external service, or state-transition invariants that cannot be confirmed via code inspection and live execution.

---

### Gaps Summary

No gaps. All 10 must-haves verified. All 4 requirements (STAT-03, ALGN-01, ALGN-02, ALGN-03) satisfied. Full test suite green at 388 passed / 4 skipped — matching the SUMMARY claim exactly, confirmed by running `.venv/bin/pytest tests/ -q --tb=no`.

**Verdict:** Phase 27 goal is achieved. Users can score functional predictions with all five error metrics (functional_mae/mse/mape/msle/explained_variance) and run least-squares shift registration (`least_squares_shift_registration` + `fd.shift_register()`), registration-quality scoring (three scores, with Sobolev non-uniform-grid ValueError confirmed live), and banded elastic alignment (three `*_with_band` functions with `band_frac=None` unbanded default). Every fallible input surfaces as a clean `ValueError` via `to_pyresult()` — zero `.unwrap()` calls in any new code path. The banded distance matrices route through `fdmatrix_to_numpy2d` and pass the multi-curve DISTINCT-per-curve transposition round-trip test. No regressions.

---

_Verified: 2026-08-15T21:41:29Z_
_Verifier: Claude (gsd-verifier)_
