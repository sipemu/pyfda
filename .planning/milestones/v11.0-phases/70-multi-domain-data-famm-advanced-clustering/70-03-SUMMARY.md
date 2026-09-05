---
phase: 70-multi-domain-data-famm-advanced-clustering
plan: 03
subsystem: spm
tags: [rust, pyo3, numpy, mfpca, spe_multivariate, spm, fdars-core-0.33]

requires:
  - phase: 70-01
    provides: PyMultiFunData handle (ordering constraint satisfied — spm bindings built after MULTI-01)

provides:
  - mfpca #[pyfunction] in fdars.spm returning a 6-key PyDict (scores, eigenfunctions, eigenvalues, means, scales, grid_sizes)
  - spe_multivariate #[pyfunction] in fdars.spm returning a naked (n,) 1-D numpy array
  - tests/test_spm_mfpca.py with 11 tests on NON-SQUARE multi-variable fixture

affects:
  - 70-04 (clustering bindings — same spm_mod.rs pattern usable)
  - Phase 72 (advisor spm/clustering aspect extensions — MULTI-03 provides new methods to advise)
  - Phase 73 (docs pages for mfpca + spe_multivariate)

actuals:
  tokens: 3315
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Vec<FdMatrix>/Vec<&FdMatrix> collect pattern for Python list-of-2D-arrays → &[&FdMatrix] slice (established in concurrent_regression phase 68; applied here for mfpca + spe_multivariate)"
    - "Lifetime-ordered argvals conversion: Vec<Vec<f64>> declared before Vec<&[f64]> refs (Pitfall 4 — av_vecs outlives av_refs)"
    - "PyList::empty(py) + append() for building Python lists of numpy arrays inside a PyDict (eigenfunctions, means, grid_sizes)"

key-files:
  created:
    - tests/test_spm_mfpca.py
  modified:
    - src/spm_mod.rs

key-decisions:
  - "Used extract::<PyReadonlyArray2<f64>>() (matching multi_fdata_mod.rs pattern) rather than downcast for cleaner error messages — consistent with 70-01 style"
  - "MfpcaConfig built via Default::default() + field mutation per research section 7 — consistent with project pattern even though MfpcaConfig is NOT #[non_exhaustive]"
  - "spe_multivariate returns vec_to_numpy1d (naked PyArray1) — NOT a PyDict; matches research spec and enables direct array operations in Python"

requirements-completed: [MULTI-03]

coverage:
  - id: D1
    description: "mfpca #[pyfunction] in fdars.spm returns 6-key PyDict (scores, eigenfunctions, eigenvalues, means, scales, grid_sizes) with no pub(super) fields"
    requirement: MULTI-03
    verification:
      - kind: unit
        ref: tests/test_spm_mfpca.py#test_mfpca_returns_six_key_dict
        status: pass
      - kind: unit
        ref: tests/test_spm_mfpca.py#test_mfpca_scores_shape
        status: pass
      - kind: unit
        ref: tests/test_spm_mfpca.py#test_mfpca_eigenfunctions_list_length
        status: pass
      - kind: unit
        ref: tests/test_spm_mfpca.py#test_mfpca_no_pub_super_keys
        status: pass
    human_judgment: false
  - id: D2
    description: "spe_multivariate #[pyfunction] in fdars.spm returns naked (n_obs,) 1-D numpy array"
    requirement: MULTI-03
    verification:
      - kind: unit
        ref: tests/test_spm_mfpca.py#test_spe_multivariate_shape
        status: pass
      - kind: unit
        ref: tests/test_spm_mfpca.py#test_spe_multivariate_is_not_dict
        status: pass
    human_judgment: false
  - id: D3
    description: "Full test suite (5466 tests) remains green after extending spm_mod.rs"
    requirement: MULTI-03
    verification:
      - kind: unit
        ref: "pytest tests/ -q → 5466 passed, 10 skipped"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-09-03
status: complete
---

# Phase 70 Plan 03: MFPCA + SPE Multivariate Bindings Summary

**mfpca (6-key PyDict: scores/eigenfunctions/eigenvalues/means/scales/grid_sizes) and spe_multivariate (naked (n,) array) added to fdars.spm via Vec<FdMatrix>/Vec<&FdMatrix> slice pattern; pub(super) fields excluded; 11 tests on non-square multi-variable fixture all pass**

## Performance

- **Duration:** 7 min
- **Started:** 2026-09-03T21:24:02Z
- **Completed:** 2026-09-03T21:31:37Z
- **Tasks:** 2
- **Files modified:** 2 (src/spm_mod.rs + tests/test_spm_mfpca.py created)

## Accomplishments

- `mfpca` #[pyfunction] appended to `src/spm_mod.rs`: takes a Python list of 2-D numpy arrays, builds `Vec<FdMatrix>` + `Vec<&FdMatrix>`, calls `fdars_core::spm::mfpca::mfpca`, returns a 6-key PyDict with `scores`, `eigenfunctions` (PyList of P arrays), `eigenvalues`, `means` (PyList of P arrays), `scales`, `grid_sizes`; `combined_rotation` and `scale_threshold` (pub(super)) NOT referenced
- `spe_multivariate` #[pyfunction] appended to `src/spm_mod.rs`: 3 PyList params (standardized_vars, reconstructed_vars, argvals_list); both 2-D lists via Vec<FdMatrix>/Vec<&FdMatrix>; argvals via Vec<Vec<f64>> declared before Vec<&[f64]> refs (Pitfall 4 — lifetime-correct); returns naked `vec_to_numpy1d` array (not a dict)
- `tests/test_spm_mfpca.py` created with 11 tests on NON-SQUARE fixture (n=20, var1 20×30, var2 20×25): mfpca 6-key dict correctness + shape checks + no pub(super) keys; spe_multivariate (20,) shape + not-a-dict + non-negative residuals
- Both functions registered in `spm_mod::register`; full 5466-test suite remains green

## Task Commits

1. **Task 1: Bind mfpca into fdars.spm** - `dff4e28` (feat)
2. **Task 2: Bind spe_multivariate + tests/test_spm_mfpca.py** - `b9387ad` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `src/spm_mod.rs` — Two new #[pyfunction]s (mfpca, spe_multivariate) + PyList import + both registered in register()
- `tests/test_spm_mfpca.py` — 11 pytest tests for MULTI-03 acceptance criteria

## Decisions Made

- Used `extract::<PyReadonlyArray2<f64>>()` (matching multi_fdata_mod.rs pattern) rather than downcast — consistent with 70-01 style and gives cleaner error messages
- `MfpcaConfig` built via `Default::default()` + field mutation (consistent project pattern even though MfpcaConfig is NOT #[non_exhaustive])
- `spe_multivariate` returns a naked `PyArray1<f64>` (not a PyDict) — matches research spec; enables direct numpy operations in Python

## Deviations from Plan

None — plan executed exactly as written. Both functions match the signatures and output contracts specified in the research (section 4.1, 4.2, Pitfall 4).

## Issues Encountered

None.

## Self-Check

- [x] `tests/test_spm_mfpca.py` exists on disk
- [x] `git log --oneline` shows `dff4e28` (mfpca) and `b9387ad` (spe_multivariate) commits
- [x] `fdars.spm.mfpca` callable — verified
- [x] `pytest tests/test_spm_mfpca.py -x -q` — 11 passed
- [x] `pytest tests/ -q` — 5466 passed, 10 skipped

## Self-Check: PASSED

## Next Phase Readiness

- MULTI-03 complete; MULTI-04 (advanced clustering — dbscan_fd, kcfc_cluster, funfem_cluster, align_cluster_fd) is next in wave 3
- No blockers; spm_mod.rs pattern now well-established for this phase

---
*Phase: 70-multi-domain-data-famm-advanced-clustering*
*Completed: 2026-09-03*
