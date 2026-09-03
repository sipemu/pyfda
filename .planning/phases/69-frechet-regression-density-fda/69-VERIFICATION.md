---
phase: 69-frechet-regression-density-fda
verified: 2026-09-03T20:11:59Z
status: passed
resolved: 2026-09-03T20:45:00Z
score: 3/3 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps_closed:
  - truth: "extract_ragged_vecs is factored into src/convert.rs, validated on non-uniform per-observation lengths, and used by the density/Fréchet inputs"
    status: resolved
    resolution: "Gap closed by plan 69-05 (commit 9167e0b): frechet_mean's spherical arm — a list of (d,) 1-D unit vectors, exactly the Vec<Vec<f64>> shape the helper produces — now calls crate::convert::extract_ragged_vecs(objects, \"frechet_mean\") instead of per-item PyReadonlyArray1 extraction (frechet_mod.rs:402), with unit-norm + dimension-consistency validation preserved. This literally satisfies SC1's 'used by the Fréchet inputs' clause and consolidates the list-of-1D-arrays extraction through the shared utility. User-chosen approach (gap closure: wire into spherical). Full suite re-run: 5443 passed, 10 skipped, 0 failed. SPD/correlation arms and density_fda (rectangular 0.33 API shapes) correctly keep numpy2d/1d converters."
---

# Phase 69: Fréchet Regression & Density FDA — Verification Report

**Phase Goal:** Users can run Fréchet (metric-space) regression/ANOVA and density-valued FDA transforms through two new submodules, backed by a shared ragged-list input helper factored into the conversion layer.
**Verified:** 2026-09-03T20:11:59Z
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `extract_ragged_vecs` factored into `src/convert.rs`, validated on non-uniform lengths, and used by density/Fréchet inputs | PARTIAL — FAILED | Helper is in convert.rs (`pub fn extract_ragged_vecs` at line 108) and tested on ragged lengths (4 tests pass). But NOT called from frechet_mod.rs or density_fda_mod.rs; only pace_fpca_mod.rs (lines 89-90) uses it. ROADMAP SC1 says "used by the density/Fréchet inputs" — unmet. |
| 2 | `import fdars.frechet` works; `frechet_mean`, `frechet_global_reg`, `frechet_local_reg`, `frechet_anova` callable; string dispatch with `Err` arm; each returns documented PyDict | VERIFIED | Live import succeeds. All 4 functions present. `frechet_mean(space='spd')` returns (3,3) array. `space='bogus'` raises ValueError listing valid spaces. Non-symmetric SPD raises ValueError. CR-01 fix confirmed: `flat_col_major_to_numpy2d` returns `PyResult` with length guard at line 308. 35 tests (pre-review) + 53 tests (post-review) pass. |
| 3 | `import fdars.density_fda` works; `normalize_density`, `lqd_transform`, `inverse_lqd`, `wasserstein_barycenter`, `lqd_fpca` callable; first four return naked 1D arrays; `lqd_fpca` returns 6-key dict | VERIFIED | Live import succeeds. All 5 functions present. `normalize_density` returns ndarray ndim=1. `lqd_transform` returns ndarray ndim=1. `inverse_lqd` returns ndarray ndim=1. `wasserstein_barycenter` returns ndarray ndim=1, shape (100,). `lqd_fpca` returns dict with keys `['fve', 'loadings', 'mean', 'ncomp', 'scores', 'singular_values']` — all 6 correct. WR-01 fix confirmed: all 5 functions declared `pub fn`. 17 tests pass. |

**Score:** 2/3 truths verified (0 present, behavior-unverified)

---

### Gaps Summary

**One gap blocks SC1:** The ROADMAP success criterion states `extract_ragged_vecs` must be "used by the density/Fréchet inputs." The implementation chose 2D matrix inputs for both new submodules — a sound design decision for the actual fdars-core API shapes involved (density functions take FdMatrix, frechet_mean objects are 2D matrices or 1D vectors) — but this deviates from the stated contract.

The helper is correctly relocated into `convert.rs` as a public function, it is tested on non-uniform ragged lengths, and it preserves existing `pace_fpca` behavior. The relocation goal of FRE-03 is otherwise achieved. The specific "used by" clause is the unmet part.

**Two paths to close the gap:**

1. **Wire the helper:** At least one frechet or density_fda function should accept a ragged list input and route through `extract_ragged_vecs`. The most natural candidate is `frechet_mean` when `space='density'` (if ever implemented), or a wrapper accepting list-of-array inputs for any function.

2. **Override:** If the design decision to use 2D matrix inputs is the intended final form, add an override in VERIFICATION.md frontmatter accepting that SC1's "used by density/Fréchet inputs" was aspirational and the correct design supersedes it.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/convert.rs` | `pub fn extract_ragged_vecs` | VERIFIED | Line 108: `pub fn extract_ragged_vecs(list: &Bound<'_, PyList>, caller_name: &str) -> PyResult<Vec<Vec<f64>>>` |
| `src/pace_fpca_mod.rs` | No `extract_list_of_vecs`; uses `crate::convert::extract_ragged_vecs` | VERIFIED | Old helper absent (grep returns 0); lines 89-90 call `crate::convert::extract_ragged_vecs` |
| `src/frechet_mod.rs` | 4 public `#[pyfunction]` frechet functions | VERIFIED | 503 lines; all 4 functions present as `pub fn` |
| `src/density_fda_mod.rs` | 5 public `#[pyfunction]` density_fda functions | VERIFIED | 280 lines; all 5 functions `pub fn` (WR-01 fix applied at review) |
| `src/lib.rs` | Both modules registered | VERIFIED | Lines 32-33: `mod frechet_mod; mod density_fda_mod;`; lines 69-70: `register_submodule!` for both |
| `python/fdars/__init__.py` | Both names in `_submodule_names` | VERIFIED | Lines 61-62: `"frechet"` and `"density_fda"` with Phase 69 comments |
| `tests/test_frechet.py` | Frechet tests | VERIFIED | 53 tests (including WR-02 `test_non_symmetric_raises` for correlation) |
| `tests/test_density_fda.py` | Density FDA tests | VERIFIED | 17 tests |
| `tests/test_convert_ragged.py` | Ragged helper behavior tests | VERIFIED | 4 tests: non-uniform lengths accepted, mixed types accepted, unsupported type raises ValueError |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `pace_fpca_mod.rs:89-90` | `convert::extract_ragged_vecs` | `crate::convert::extract_ragged_vecs(list, "irreg_fdata_from_lists")` | WIRED | Both call sites confirmed |
| `frechet_mod.rs` | `convert.rs` helpers | `crate::convert::{fdmatrix_to_numpy2d, numpy1d_to_vec, numpy2d_to_fdmatrix, to_pyresult, usize_vec_to_numpy1d, vec_to_numpy1d}` | WIRED | Import line 10-13 confirmed |
| `density_fda_mod.rs` | `convert.rs` helpers | `crate::convert::{fdmatrix_to_numpy2d, numpy1d_to_vec, numpy2d_to_fdmatrix, to_pyresult, vec_to_numpy1d}` | WIRED | Import lines 9-11 confirmed |
| `lib.rs` | `frechet_mod::register` | `register_submodule!(m, "frechet", frechet_mod::register)` | WIRED | Line 69 |
| `lib.rs` | `density_fda_mod::register` | `register_submodule!(m, "density_fda", density_fda_mod::register)` | WIRED | Line 70 |
| `__init__.py` | both submodule names | `_submodule_names` tuple, lines 61-62 | WIRED | Both names registered |
| `frechet_mod.rs` → `extract_ragged_vecs` | NOT WIRED | Should be used by Fréchet inputs per SC1 | NOT_WIRED | Frechet uses per-object `item.extract::<PyReadonlyArray2<f64>>()` instead |
| `density_fda_mod.rs` → `extract_ragged_vecs` | NOT WIRED | Should be used by density inputs per SC1 | NOT_WIRED | Density uses `numpy1d_to_vec` / `numpy2d_to_fdmatrix` instead |

### Code Review Fixes Verification

All four findings from 69-REVIEW.md verified as fixed:

| Finding | Fix | Status |
|---------|-----|--------|
| CR-01: `flat_col_major_to_numpy2d` panics on length mismatch | `result.len() != d * d` guard at frechet_mod.rs:308 returning `PyValueError` | VERIFIED — guard present; function returns `PyResult` |
| WR-01: density_fda functions declared `fn` not `pub fn` | `pub` added to all 5 functions | VERIFIED — all 5 at lines 42, 92, 134, 180, 237 are `pub fn` |
| WR-02: no test for correlation symmetry validation | `test_non_symmetric_raises` added to `TestFrechetMeanCorrelation` | VERIFIED — at test_frechet.py:337 |
| WR-03: k=0 produces nonsensical error message | Explicit `if k == 0` branch at frechet_mod.rs:76-79 | VERIFIED — `"group_labels is empty — at least 2 groups required"` |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `import fdars.frechet, fdars.density_fda` succeeds | `python -c "import fdars.frechet, fdars.density_fda"` | Exit 0 | PASS |
| `frechet_mean(space='spd')` returns (d,d) array | `frechet.frechet_mean(objects, space='spd', d=3).shape` | `(3, 3)` | PASS |
| `frechet_mean(space='bogus')` raises ValueError | Spot-check | ValueError: "space must be 'spd', 'spherical', or 'correlation', got 'bogus'" | PASS |
| Non-symmetric SPD raises ValueError | Spot-check | ValueError mentioning non-symmetric | PASS |
| `normalize_density` returns naked 1D array | `type(result).__name__, ndim` | `ndarray`, 1 | PASS |
| `lqd_transform` returns naked 1D array | `type(result).__name__, ndim` | `ndarray`, 1 | PASS |
| `inverse_lqd` returns naked 1D array | `type(result).__name__, ndim` | `ndarray`, 1 | PASS |
| `wasserstein_barycenter` returns naked 1D array (shape M,) | `ndim, shape` | 1, `(100,)` | PASS |
| `lqd_fpca` returns 6-key dict | `sorted(fpca_result.keys())` | `['fve', 'loadings', 'mean', 'ncomp', 'scores', 'singular_values']` | PASS |

### Phase Test Results

| Test File | Count | Result |
|-----------|-------|--------|
| `tests/test_frechet.py` | 53 | All PASS |
| `tests/test_density_fda.py` | 17 | All PASS |
| `tests/test_convert_ragged.py` | 4 | All PASS |
| **Phase total** | **57** | **All PASS** |

### Full Regression Suite

```
5443 passed, 10 skipped, 120 warnings in 140.65s
```

- pace_fpca tests: PASS (FRE-03 refactor is behavior-preserving)
- FND-02 guard: PASS (subset invariant not violated; new submodule names are additive)
- Pre-existing test count unchanged at 5443 passed
- Zero new failures introduced by Phase 69

### Requirements Coverage

| Requirement | Phase | Description | Status | Evidence |
|-------------|-------|-------------|--------|----------|
| FRE-01 | 69 | `fdars.frechet` submodule with 4 functions, string dispatch, Err arm, PyDict results | SATISFIED | Live import + 53 tests pass + spot-checks |
| FRE-02 | 69 | `fdars.density_fda` submodule with 5 functions, correct return types | SATISFIED | Live import + 17 tests pass + spot-checks |
| FRE-03 | 69 | `extract_ragged_vecs` in convert.rs, validated on ragged lengths, used by density/Fréchet inputs | PARTIALLY SATISFIED | Helper exists and is tested; but "used by" clause unmet (see gap) |

### Anti-Patterns Found

No blocking anti-patterns in phase files. No TBD/FIXME/XXX/TODO/HACK markers in any of the 6 phase-modified files. No stub implementations. No placeholder return values.

| File | Pattern | Severity | Notes |
|------|---------|----------|-------|
| None detected | — | — | Phase files are clean |

---

## Summary of Gaps

**1 BLOCKER gap:**

**Truth 1 (SC1 / FRE-03):** ROADMAP requires `extract_ragged_vecs` to be "used by the density/Fréchet inputs." The implementation correctly places the helper in `convert.rs` and uses it in `pace_fpca_mod.rs`, but neither `frechet_mod.rs` nor `density_fda_mod.rs` imports or calls it. Both new modules use 2D-matrix (`numpy2d_to_fdmatrix`) or 1D-vector (`numpy1d_to_vec`) inputs instead of ragged Python lists.

This is a design mismatch: the frechet API accepts a list of 2D numpy arrays (one per metric-space object, not ragged 1D curves), and the density_fda API accepts a 2D density matrix. The ragged helper is appropriate for irregular functional data curves, not for these structured inputs. The implementation's choice of 2D matrix inputs is technically sound — but the ROADMAP said otherwise, making this a contract violation.

**Resolution options:**

Option A (code change): Add a ragged-input pathway to at least one frechet or density_fda function that calls `extract_ragged_vecs`. For example, `frechet_global_reg` and `frechet_local_reg` currently require 2D density matrices; an overload accepting a `PyList` of 1D density arrays and converting via `extract_ragged_vecs` would satisfy SC1.

Option B (override): Accept that SC1's "used by density/Fréchet inputs" was written based on aspirational research notes but the concrete fdars-core 0.33 API shapes (FdMatrix, not ragged lists) made 2D matrix inputs the correct and superior design. Add an override entry to close the gap.

---

_Verified: 2026-09-03T20:11:59Z_
_Verifier: Claude (gsd-verifier)_
