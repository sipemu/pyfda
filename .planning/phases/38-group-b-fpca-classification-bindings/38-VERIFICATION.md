---
phase: 38-group-b-fpca-classification-bindings
verified: 2026-08-20T22:34:18Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 38: Group B FPCA & Classification Bindings Verification Report

**Phase Goal:** Users can run sparse/irregular PACE functional PCA over a new ragged-grid IrregFdata input, and fit a K-class one-vs-rest elastic multinomial classifier, from a new `src/pace_fpca_mod.rs` and the extended `fdars.classification` submodule.
**Verified:** 2026-08-20T22:34:18Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | `fdars.pace_fpca.irreg_fdata_from_lists` accepts two Python lists of ragged 1-D arrays and returns a `PyIrregFdata` opaque handle; `pace_fpca(handle, ...)` round-trips end-to-end | ✓ VERIFIED | `src/pace_fpca_mod.rs:92-153`, `src/pace_fpca_mod.rs:219-239`; smoke: `handle type: <class 'builtins.PyIrregFdata'>`; `TestIrregFdataRoundTrip::test_irreg_round_trip` passes |
| 2  | `irreg_fdata_from_lists` rejects a plain dense 2-D numpy array of ANY dtype (`float64`, `float32`, `int32`, `int64`) with a `ValueError` (CR-01 dtype-agnostic guard) | ✓ VERIFIED | `src/pace_fpca_mod.rs:97-116`: dtype-agnostic via `cast::<numpy::PyUntypedArray>().map(|a| a.ndim() == 2)`, NOT `is_instance_of::<PyArray2<f64>>()`; confirmed post-review commit `a34f4c6`; parametrized `test_dense_array_rejection` over 4 dtypes passes; smoke confirms all 4 dtypes rejected |
| 3  | `irreg_fdata_from_lists` rejects ragged per-curve mismatch AND outer-length mismatch with `ValueError` BEFORE `IrregFdata::from_lists` (no PanicException) | ✓ VERIFIED | `src/pace_fpca_mod.rs:130-148`: outer-length guard at line 131-136, per-curve guard at 140-148, both precede `from_lists` call at line 151; `TestIrregFdataValidation` class (3 tests) passes |
| 4  | `fdars.pace_fpca` returns a dict with exactly 10 keys: `mean`, `eigenvalues`, `eigenfunctions`, `scores`, `fitted`, `fitted_lower`, `fitted_upper`, `argvals`, `sigma2`, `ncomp` | ✓ VERIFIED | `src/pace_fpca_mod.rs:164-188`: `pace_fpca_result_to_pydict` sets all 10 keys; smoke shows `sorted(keys) == ['argvals', 'eigenfunctions', 'eigenvalues', 'fitted', 'fitted_lower', 'fitted_upper', 'mean', 'ncomp', 'scores', 'sigma2']`; `test_pace_result_keys` passes |
| 5  | `eigenfunctions` is shaped `(m, ncomp)` and `scores` is shaped `(n, ncomp)`, transposition-guarded with `n != m != ncomp`; includes discrete L2 orthonormality check | ✓ VERIFIED | `src/pace_fpca_mod.rs:172-176`: `fdmatrix_to_numpy2d` maps FdMatrix (nrows=m, ncols=ncomp) → numpy `(m,ncomp)`; smoke: `eigenfunctions (51,2)`, `scores (6,2)` with n=6, m=51, ncomp=2; `test_eigenfunctions_transposition_guard` now asserts `dt*(ef.T@ef) ≈ I` (atol=0.30) after WR-01 fix in commit `a34f4c6`; `test_scores_transposition_guard` asserts `n != m != ncomp` |
| 6  | `result["ncomp"]` echoes actual extracted count (may be < requested); all shapes use `result.ncomp`; two identical calls return byte-identical arrays | ✓ VERIFIED | `src/pace_fpca_mod.rs:186`: `dict.set_item("ncomp", r.ncomp)` — actual, not requested; `test_ncomp_truncation` requests 10, asserts `actual <= 10` and shape consistency; `test_pace_determinism` checks `np.array_equal` on eigenfunctions/scores/fitted |
| 7  | `fdars.classification.elastic_multinomial` returns a 5-key dict omitting `class_models`; keys are `n_classes`, `classes`, `train_probabilities`, `predicted_classes`, `train_accuracy` | ✓ VERIFIED | `src/classification_mod.rs:278-295`: 5 keys set, `class_models` explicitly omitted with Rust comment; smoke: `class_models absent: True`; `test_multinomial_smoke` passes with exact key-set assertion |
| 8  | `train_probabilities` is shaped `(n, K)`, transposition-guarded at K=3 (K != n=30), with each row summing to 1.0 | ✓ VERIFIED | `src/classification_mod.rs:285-289`: `fdmatrix_to_numpy2d(py, &r.train_probabilities)` (FdMatrix nrows=n, ncols=K → numpy (n,K)); smoke: `shape (30,3)`, `np.allclose(row_sums, 1.0, atol=1e-6): True`; `test_multinomial_proba_shape` passes |
| 9  | Negative labels (e.g. `[-1,0,1]`) and non-contiguous labels (e.g. `[0,2]`) raise `ValueError`; CR-01 guard fires BEFORE `i64→usize` cast; `match="non-negative"` and `match="contiguous"` both verified | ✓ VERIFIED | `src/classification_mod.rs:346-353`: `raw.iter().any(|&x| x < 0)` guard before `map(|&x| x as usize)` cast; non-contiguous surfaced from core via `to_pyresult()`; smoke: both guards fire correctly; `test_negative_label_guard` (`match="non-negative"`) and `test_noncontiguous_label_guard` (`match="contiguous"`, pinned in WR-02 fix `a34f4c6`) pass |
| 10 | All fallible core calls route through `to_pyresult()` (no `.unwrap()`/`.expect()` in new functions); full pytest suite green + fmt + clippy clean | ✓ VERIFIED | grep: zero `.unwrap()` or `.expect(` in `pace_fpca_mod.rs` or `classification_mod.rs`; `to_pyresult()` used at lines 238 and 355; full suite: **643 passed, 4 skipped, 0 failed** (observed live); SUMMARY confirms `cargo fmt --check` + `cargo clippy -- -D warnings` clean (commit `a34f4c6` message confirms) |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/pace_fpca_mod.rs` | New: `PyIrregFdata` `#[pyclass]`, `irreg_fdata_from_lists`, `run_pace_fpca` (exposed as `pace_fpca`), `extract_list_of_vecs`, `pace_fpca_result_to_pydict`, `register()` | ✓ VERIFIED | 252-line file; all symbols present and substantive; wired via `lib.rs` |
| `src/classification_mod.rs` | Extended: `elastic_multinomial` + `elastic_multinomial_result_to_pydict` added to `register()` | ✓ VERIFIED | `elastic_multinomial` at line 331, converter at 278, registered at line 370 |
| `src/lib.rs` | `mod pace_fpca_mod;` + `register_submodule!(m, "pace_fpca", pace_fpca_mod::register)` | ✓ VERIFIED | `mod pace_fpca_mod;` at line 21 (alphabetical, between `outliers_mod` and `regression_mod` per rustfmt); `register_submodule!` at line 62 |
| `python/fdars/__init__.py` | `"pace_fpca"` added to `_submodule_names` tuple | ✓ VERIFIED | Line 54: `"pace_fpca",  # Phase 38 — PACE FPCA + IrregFdata opaque handle` |
| `tests/test_pace_fpca.py` | New: `TestIrregFdataRoundTrip` (1), `TestIrregFdataValidation` (3+param=4), `TestPaceFpcaResult` (7), `TestPaceImportPaths` (2) | ✓ VERIFIED | 13 test methods collected; 10 passing (parametrized test counts 3 extra) = 23 total with classification |
| `tests/test_classification.py` | New: `TestElasticMultinomial` (5), `TestClassificationImportPaths` (2) | ✓ VERIFIED | 7 test methods collected; all pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `python/fdars/__init__.py` | `fdars.pace_fpca.*` | `_submodule_names` loop → `sys.modules["fdars.pace_fpca"]` | ✓ WIRED | Line 54 in tuple; smoke confirms `callable(fdars.pace_fpca.irreg_fdata_from_lists)` |
| `src/lib.rs` | `pace_fpca_mod::register` | `register_submodule!(m, "pace_fpca", ...)` | ✓ WIRED | Line 62; `mod pace_fpca_mod;` declared at line 21 |
| `pace_fpca_mod::register()` | `PyIrregFdata` class | `m.add_class::<PyIrregFdata>()?` | ✓ WIRED | `src/pace_fpca_mod.rs:247` |
| `run_pace_fpca` | `fdars_core::pace_fpca::pace_fpca` | `to_pyresult(fdars_core::pace_fpca::pace_fpca(&data.inner, &config))?` | ✓ WIRED | `src/pace_fpca_mod.rs:238` |
| `elastic_multinomial` | `fdars_core::elastic_regression::elastic_multinomial` | `to_pyresult(...)` after CR-01 guard | ✓ WIRED | `src/classification_mod.rs:355`; registered at line 370 |
| `classification_mod::register()` | `elastic_multinomial` | `m.add_function(wrap_pyfunction!(elastic_multinomial, m)?)` | ✓ WIRED | `src/classification_mod.rs:370` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `eigenfunctions` | `r.eigenfunctions` | `fdars_core::pace_fpca::pace_fpca` result field | Yes — FdMatrix from core PACE decomposition | ✓ FLOWING |
| `scores` | `r.scores` | `fdars_core::pace_fpca::pace_fpca` result field | Yes — projection scores from core | ✓ FLOWING |
| `train_probabilities` | `r.train_probabilities` | `fdars_core::elastic_regression::elastic_multinomial` result field | Yes — softmax probabilities from OvR fit | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `irreg_fdata_from_lists` builds handle, `pace_fpca` returns 10-key dict | Python smoke (inline) | `eigenfunctions (51,2)`, `scores (6,2)`, all 10 keys present | ✓ PASS |
| 2-D arrays of all dtypes (float64, float32, int32, int64) rejected with ValueError | Python smoke (inline) | All 4 dtypes → `"received a 2-D numpy array"` | ✓ PASS |
| `elastic_multinomial` returns 5 keys, `class_models` absent, rows sum to 1 | Python smoke (inline) | `class_models absent: True`, `np.allclose(row_sums, 1.0): True` | ✓ PASS |
| Negative label guard fires before usize cast | Python smoke (inline) | `"labels must be non-negative"` | ✓ PASS |
| Non-contiguous label guard (via core → to_pyresult) | Python smoke (inline) | `"labels must form the contiguous range 0..2"` | ✓ PASS |
| Full pytest suite | `.venv/bin/python -m pytest tests/ -q` | **643 passed, 4 skipped, 0 failed** | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PACE-01 | 38-01-PLAN.md | Sparse/irregular `IrregFdata` builder with dense-array + mismatch `ValueError` guards | ✓ SATISFIED | `irreg_fdata_from_lists` with dtype-agnostic CR-01 guard + outer/per-curve guards; all guard tests pass |
| PACE-02 | 38-01-PLAN.md | `pace_fpca` 10-key dict, transposition-guarded eigenfunctions/scores, `actual_ncomp` truncation, determinism | ✓ SATISFIED | Full converter in `pace_fpca_result_to_pydict`; all `TestPaceFpcaResult` tests pass |
| CLASS-01 | 38-01-PLAN.md | `elastic_multinomial` 5-key dict, `(n,K)` proba guard, CR-01 negative/non-contiguous label guard, `class_models` omitted | ✓ SATISFIED | Implementation in `classification_mod.rs`; all `TestElasticMultinomial` tests pass |

### Code Review Findings — Addressed Status

The REVIEW.md (status `issues_found`) flagged 1 critical + 2 warnings + 2 info items. All were addressed in commit `a34f4c6 fix(38-01): address code-review findings (dtype guard + test hardening)`:

| Finding | Severity | Addressed | How |
|---------|----------|-----------|-----|
| CR-01: Dense-array guard missed non-float64 dtypes (`is_instance_of::<PyArray2<f64>>`) | Critical | Yes | Replaced with dtype-agnostic `cast::<numpy::PyUntypedArray>().map(|a| a.ndim() == 2)` |
| WR-01: Missing orthonormality assertion in eigenfunctions test | Warning | Yes | Added `dt * (ef.T @ ef) ≈ np.eye(k)` assertion (atol=0.30, correct L2 inner product) |
| WR-02: `test_noncontiguous_label_guard` missing `match=` pattern | Warning | Yes | Added `match="contiguous"` to the `pytest.raises` call |
| IN-01: Dense-array test only covered `float64` dtype | Info | Yes | Parametrized across `[float64, float32, int32, int64]` |
| IN-02: `extract_list_of_vecs` accepted only `PyList`, not `PyTuple` | Info | Yes | Added `PyTuple` branch in `extract_list_of_vecs` |

### Anti-Patterns Found

No debt markers (`TBD`, `FIXME`, `XXX`) found in `src/pace_fpca_mod.rs` or `src/classification_mod.rs`. The single `unwrap_or` and `unwrap_or_else` occurrences are safe fallbacks (not panicking calls): `unwrap_or(false)` for ndim checks, `unwrap_or_else(|_| "?".to_string())` for type-name display, and `unwrap_or_else(||...)` for the default work grid. No empty stubs or placeholder returns.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | — |

### Human Verification Required

None. All behavioral invariants are exercised by the test suite and confirmed via behavioral spot-checks above.

---

## Gaps Summary

No gaps. All 10 must-have truths are VERIFIED by direct code inspection + behavioral spot-checks + 643-test suite (zero failures). The sole code-review critical finding (CR-01 dtype-agnostic guard) and all warnings/info items were addressed in commit `a34f4c6` prior to this verification.

---

## ROADMAP Success Criteria

| SC# | Success Criterion | Status | Evidence |
|-----|-------------------|--------|----------|
| 1 | `fdars.irreg_fdata_from_lists` accepts two Python lists of 1-D arrays; dense 2-D array rejected with `ValueError` | ✓ PASS | Dtype-agnostic guard via `PyUntypedArray.ndim()==2`; all 4 dtype variants rejected; smoke + tests |
| 2 | `fdars.pace_fpca(irreg_fdata, ...)` → 10-key dict; `eigenfunctions (m,ncomp)` / `scores (n,ncomp)` transposition-guarded; `actual_ncomp` truncation; lives in new `src/pace_fpca_mod.rs` | ✓ PASS | All converters correct; eigenfunctions (51,2) and scores (6,2) verified with n=6,m=51,ncomp=2; `TestPaceFpcaResult` 7 tests green |
| 3 | `fdars.classification.elastic_multinomial` → 5-key dict; `train_probabilities (n,K)` at K=3 guarded; negative/non-contiguous label → `ValueError` | ✓ PASS | CR-01 guard before cast; non-contiguous via core; all `TestElasticMultinomial` tests green; rows sum to 1.0 |
| 4 | All new functions registered with `to_pyresult()` guards (no `.unwrap()`); degenerate inputs raise `ValueError` | ✓ PASS | Zero `.unwrap()` / `.expect()` in new code; `to_pyresult()` at `pace_fpca_mod.rs:238` and `classification_mod.rs:355`; all guards raise `ValueError` |

---

_Verified: 2026-08-20T22:34:18Z_
_Verifier: Claude (gsd-verifier)_
