---
phase: 70-multi-domain-data-famm-advanced-clustering
verified: 2026-09-04T08:30:00Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 70: Multi-domain Data, FAMM, Advanced Clustering — Verification Report

**Phase Goal:** Users can construct multi-domain functional data and pass it to mixed-model (FAMM) and multivariate SPM bindings, and run the advanced clustering methods added at 0.33.
**Verified:** 2026-09-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `import fdars.multi_fdata` works and exposes `multi_fdata_from_components` + `PyMultiFunData` (SC1) | VERIFIED | Live: `python -c "import fdars.multi_fdata as mf; assert callable(mf.multi_fdata_from_components); assert hasattr(mf, 'PyMultiFunData')"` passes |
| 2 | `multi_fdata_from_components` builds a `PyMultiFunData` handle from a list of 2D arrays + 1D argvals; `n_obs` and `n_components` getters return correct values (SC1) | VERIFIED | Live: n_obs=20, n_components=2 on non-square fixture (20×30, 20×25); `tests/test_multi_fdata.py::test_build_and_accessors` passes |
| 3 | Mismatched outer list lengths, 1D data array, or mismatched nrows each raise `ValueError` before core constructor panics (SC1) | VERIFIED | `tests/test_multi_fdata.py` — 5 guard tests pass (length mismatch, 1D data, nrows mismatch, argvals-length mismatch, empty list) |
| 4 | `import fdars.famm` works; `dense_flmm`, `fast_fmm`, `multi_famm` are callable and return documented PyDicts (SC2) | VERIFIED | Live: all three callable; `tests/test_famm.py` — 8 tests pass; 14/6/4-key dicts confirmed |
| 5 | `dense_flmm` returns a 14-key dict; `fast_fmm` returns a 6-key dict (p=0 gives (0,0)-shaped arrays); `multi_famm` returns a 4-key dict with a components list of D per-dimension dicts (SC2) | VERIFIED | `tests/test_famm.py` passes; deviation from plan noted: fdars-core 0.33 returns (0,0) FdMatrix (not (0,m)) for p=0 — test corrected to match actual upstream behaviour |
| 6 | None of the three FAMM bindings accept `PyMultiFunData` — all take plain 2D numpy arrays (SC2, vacuously satisfied) | VERIFIED | Code inspection: `famm_mod.rs` contains no `PyRef<PyMultiFunData>` parameter; module-level `//!` comment documents this explicitly |
| 7 | `mfpca` is callable via `fdars.spm` and returns a 6-key PyDict; eigenfunctions and means are lists of P entries (SC3) | VERIFIED | Live: keys `{scores, eigenfunctions, eigenvalues, means, scales, grid_sizes}` confirmed; `scores.shape==(20,4)`, `len(eigenfunctions)==2`, `len(means)==2`; `tests/test_spm_mfpca.py` 11 tests pass |
| 8 | `spe_multivariate` is callable via `fdars.spm` and returns a naked `(n,)` 1D numpy array (SC3) | VERIFIED | Live: `spe.ndim==1`, `spe.shape==(20,)`; `tests/test_spm_mfpca.py::test_spe_multivariate_shape` passes |
| 9 | Both SPM functions built after `PyMultiFunData` within this phase (SC3 ordering); neither consumes it; `pub(super)` fields not read (SC3) | VERIFIED | Wave ordering: 70-01 (multi_fdata) precedes 70-03 (spm); `spm_mod.rs` contains no `PyMultiFunData` reference; `combined_rotation`/`scale_threshold` absent from dict and from source |
| 10 | `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd` callable via `fdars.clustering`, each returning a labels/result PyDict; `dbscan_fd` cluster is `int64` with -1 for noise; `kcfc_cluster` omits `fpca_models`; `funfem_cluster` membership is `(n,k)`; `align_cluster_fd` templates is a length-k list; all transposition-guarded (SC4) | VERIFIED | Live: dtype `int64` confirmed for all four; `n_noise=20` (all-noise, eps=0.5 on 30-dim data); `fpca_models` absent; `membership.shape==(20,2)`; 3 templates each `(30,)`; `tests/test_clustering_advanced.py` 4 tests pass |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/multi_fdata_mod.rs` | `PyMultiFunData` opaque handle + builder (MULTI-01) | VERIFIED | 164 lines; substantive; wired via `lib.rs` `mod multi_fdata_mod` + `register_submodule!` |
| `src/famm_mod.rs` | Three FAMM bindings + `dense_flmm_result_to_pydict` helper (MULTI-02) | VERIFIED | 312 lines; substantive; wired via `lib.rs` `mod famm_mod` + `register_submodule!` |
| `src/spm_mod.rs` (extended) | `mfpca` + `spe_multivariate` appended (MULTI-03) | VERIFIED | Lines 882-1071; both registered in `spm_mod::register`; no new `register_submodule!` needed |
| `src/clustering_mod.rs` (extended) | Four advanced clustering functions appended (MULTI-04) | VERIFIED | Lines 313-565; all four registered in `clustering_mod::register` |
| `tests/test_multi_fdata.py` | 5 tests: happy-path + 5 guard failures | VERIFIED | 79 lines; non-square fixture (20×30, 20×25); 5 passed (includes IN-04/IN-05 additions) |
| `tests/test_famm.py` | 8 tests on non-square (20×30) FAMM fixtures | VERIFIED | 191 lines; dense_flmm/fast_fmm/multi_famm covered |
| `tests/test_spm_mfpca.py` | 11 tests: mfpca 6-key dict + spe_multivariate (n,) array | VERIFIED | 127 lines; non-square fixture (20×30, 20×25) |
| `tests/test_clustering_advanced.py` | 4 tests covering all four advanced algorithms | VERIFIED | 129 lines; non-square fixture (20×30); WR-01 fix included |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/lib.rs` | `multi_fdata_mod::register` | `register_submodule!(m, "multi_fdata", multi_fdata_mod::register)` | WIRED | Line 73; `mod multi_fdata_mod;` at line 34 |
| `src/lib.rs` | `famm_mod::register` | `register_submodule!(m, "famm", famm_mod::register)` | WIRED | Line 74; `mod famm_mod;` at line 35 |
| `python/fdars/__init__.py` | `multi_fdata` submodule | `_submodule_names` tuple includes `"multi_fdata"` | WIRED | Line 65 with Phase 70 comment |
| `python/fdars/__init__.py` | `famm` submodule | `_submodule_names` tuple includes `"famm"` | WIRED | Line 66 with Phase 70 comment |
| `spm_mod::register` | `mfpca` + `spe_multivariate` | `m.add_function(wrap_pyfunction!(...))` | WIRED | Lines 1069-1070 of `spm_mod.rs` |
| `clustering_mod::register` | 4 advanced functions | `m.add_function(wrap_pyfunction!(...))` ×4 | WIRED | Lines 562-565 of `clustering_mod.rs` |
| `multi_fdata_from_components` | `fdars_core::multi_fdata::MultiFunData::new` | `to_pyresult(fdars_core::multi_fdata::MultiFunData::new(components))?` | WIRED | Line 151 of `multi_fdata_mod.rs` |
| `mfpca` | `fdars_core::spm::mfpca::mfpca` | `to_pyresult(fdars_core::spm::mfpca::mfpca(&refs, &config))?` | WIRED | Line 913 of `spm_mod.rs` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `multi_fdata_from_components` | `inner: MultiFunData` | `fdars_core::multi_fdata::MultiFunData::new(components)` | Yes — real component matrices | FLOWING |
| `dense_flmm` | 14-key dict | `fdars_core::famm::dense_flmm(...)` via `dense_flmm_result_to_pydict` | Yes — REML-EM fitted result | FLOWING |
| `fast_fmm` | 6-key dict | `fdars_core::famm::fast_fmm(...)` | Yes — fast FMM Wald result | FLOWING |
| `multi_famm` | 4-key dict + components | `fdars_core::famm::multi_famm(...)` | Yes — multi-variable FAMM result | FLOWING |
| `mfpca` | 6-key dict | `fdars_core::spm::mfpca::mfpca(&refs, &config)` | Yes — multivariate FPCA result | FLOWING |
| `spe_multivariate` | `(n,)` array | `fdars_core::spm::stats::spe_multivariate(...)` | Yes — SPE statistic per observation | FLOWING |
| `dbscan_fd` | 4-key dict | `fdars_core::clustering_advanced::dbscan_fd(...)` | Yes — density clustering result | FLOWING |
| `kcfc_cluster` | 4-key dict | `fdars_core::clustering_advanced::kcfc_cluster(...)` | Yes — per-cluster FPCA result | FLOWING |
| `funfem_cluster` | 6-key dict | `fdars_core::clustering_advanced::funfem_cluster(...)` | Yes — Fisher-EM discriminative result | FLOWING |
| `align_cluster_fd` | 5-key dict | `fdars_core::clustering_advanced::align_cluster_fd(...)` | Yes — elastic-alignment clustering | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `multi_fdata_from_components` builds handle with correct accessors | Live Python: `n_obs=20, n_components=2` on (20×30, 20×25) fixture | PASS | PASS |
| `mfpca` returns 6-key dict with correct shapes; no pub(super) keys | Live Python: keys confirmed; `scores.shape==(20,4)`; `combined_rotation` absent | PASS | PASS |
| `spe_multivariate` returns naked (20,) 1D array | Live Python: `spe.ndim==1`, `spe.shape==(20,)` | PASS | PASS |
| `dbscan_fd` returns int64 cluster with -1 noise; n_noise > 0 | Live Python: `dtype=int64`, `n_noise=20` (all-noise, eps=0.5 / 30-dim) | PASS | PASS |
| `kcfc_cluster` omits `fpca_models`; `reconstruction_errors.shape==(20,3)` | Live Python: `fpca_models` absent; shape confirmed | PASS | PASS |
| `funfem_cluster` `membership.shape==(20,2)` | Live Python: confirmed | PASS | PASS |
| `align_cluster_fd` templates: 3 entries each `(30,)`, `distances.shape==(20,3)` | Live Python: confirmed | PASS | PASS |
| Phase test suite (29 tests) | `.venv/bin/pytest tests/test_multi_fdata.py tests/test_famm.py tests/test_spm_mfpca.py tests/test_clustering_advanced.py -q` | 29 passed | PASS |
| Full regression (critical gate) | `.venv/bin/pytest tests/ -q` | **5472 passed, 10 skipped, 120 warnings, 0 failures** | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| MULTI-01 | 70-01 | New `PyMultiFunData` opaque `#[pyclass]` handle + builder from component curves; registered and constructible from Python | SATISFIED | `src/multi_fdata_mod.rs`; 5 tests pass; live construction verified |
| MULTI-02 | 70-02 | Mixed-model bindings exposed — `dense_flmm`, `fast_fmm`, `multi_famm` — consuming `PyMultiFunData` where required, returning documented PyDicts | SATISFIED | `src/famm_mod.rs`; 8 tests pass; "where required" vacuously satisfied (0 FAMM functions consume `MultiFunData` in 0.33) |
| MULTI-03 | 70-03 | Multivariate/multi-domain SPM bindings exposed extending `fdars.spm`, sequenced after `PyMultiFunData` within the phase | SATISFIED | `mfpca` + `spe_multivariate` in `spm_mod.rs`; 11 tests pass; wave 3 ordering satisfied |
| MULTI-04 | 70-04 | Advanced clustering bound — `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd` — each returning a labels/result PyDict, transposition-guarded | SATISFIED | `clustering_mod.rs`; 4 tests pass; int64 noise, fpca_models-omission, membership shape, templates list all verified |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/famm_mod.rs` | 93 | `"not yet implemented in fdars-core 0.33"` in docstring | Info | Accurately describes upstream limitation in a `Raises` docstring section — this is documentation, not a code placeholder. Not a debt marker. |

No `TBD`, `FIXME`, or `XXX` debt markers found in any phase-modified file.

The `"not yet implemented"` phrase in `famm_mod.rs:93` appears in a `/// Raises` docstring describing a known upstream fdars-core 0.33 limitation (`random_slopes=True` not yet supported). It is a documentation accuracy statement, not a code stub or unresolved debt. No blocker.

### Code Review Items (WR-01, IN-01, IN-04, IN-05 — all resolved)

| Finding | Status | Commit | Evidence |
|---------|--------|--------|---------|
| WR-01: `test_dbscan_fd` did not assert -1 noise encoding fires | FIXED | `b2bc409` | `assert result["n_noise"] > 0` present at line 51 of `test_clustering_advanced.py` |
| IN-01: Package docstring missing `multi_fdata` and `famm` entries | FIXED | `3ed8472` | Lines 24-25 of `python/fdars/__init__.py` now include both bullets |
| IN-04: Missing `argvals_length_mismatch` guard test | FIXED | `8e581e4` | `test_reject_argvals_length_mismatch` at line 64 of `test_multi_fdata.py` |
| IN-05: Missing empty-components guard test | FIXED | `8e581e4` | `test_reject_empty_components` at line 71 of `test_multi_fdata.py` |
| IN-02: Loop variable `m` in `mfpca` (cosmetic) | OUT OF SCOPE | — | Excluded per REVIEW-FIX objective; no runtime impact |
| IN-03: Missing `Raises` sections in 4 clustering bindings | OUT OF SCOPE | — | Excluded per REVIEW-FIX objective; code correct |

### Human Verification Required

None. All success criteria are objectively verifiable from the codebase and live checks.

### Gaps Summary

No gaps. All four ROADMAP success criteria (SC1–SC4) are verified against the actual codebase:

- SC1: `PyMultiFunData` opaque handle is registered, constructible, and tested with non-square fixtures and five guard cases.
- SC2: `dense_flmm`, `fast_fmm`, `multi_famm` are callable from `fdars.famm` returning 14/6/4-key dicts; "consuming PyMultiFunData where required" is vacuously satisfied (no 0.33 FAMM function accepts `MultiFunData`).
- SC3: `mfpca` (6-key PyDict; P-length eigenfunctions/means; no pub(super) keys) and `spe_multivariate` (naked (n,) array) extend `fdars.spm`; built after `PyMultiFunData` in wave ordering.
- SC4: `dbscan_fd` (int64 -1-noise, n_noise=20), `kcfc_cluster` (fpca_models-omitted), `funfem_cluster` ((n,k) membership), `align_cluster_fd` (length-k templates) extend `fdars.clustering`; all transposition-guarded on 20×30 non-square fixture.

Full regression: **5472 passed, 10 skipped, 0 failures** — no pre-existing test regressions; FND-02 guard tolerates the two new submodules.

---

_Verified: 2026-09-04_
_Verifier: Claude (gsd-verifier)_
