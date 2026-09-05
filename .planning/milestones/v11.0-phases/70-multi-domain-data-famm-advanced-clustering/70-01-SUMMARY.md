---
phase: 70-multi-domain-data-famm-advanced-clustering
plan: 01
subsystem: api
tags: [pyo3, rust, multi_fdata, opaque-handle, pyclass, fdars-core-0.33]

requires:
  - phase: 38-pace-fpca
    provides: PyIrregFdata opaque-handle template (pace_fpca_mod.rs pattern mirrored exactly)

provides:
  - PyMultiFunData opaque #[pyclass] wrapping fdars_core::multi_fdata::MultiFunData
  - multi_fdata_from_components builder (Python list of 2D arrays + 1D argvals → PyMultiFunData)
  - fdars.multi_fdata submodule registered in lib.rs and __init__.py
  - n_obs and n_components #[getter] accessors
  - Construction-time validation (outer-list mismatch, 1D data rejection, nrows mismatch via core)
  - tests/test_multi_fdata.py with 4 passing tests (happy-path + 3 guard failures)

affects:
  - 70-02 (famm_mod.rs — next plan; no dependency on PyMultiFunData, but shares lib.rs + __init__.py)
  - 70-03 (spm extension — no dependency on PyMultiFunData)
  - 70-04 (clustering extension — no dependency on PyMultiFunData)

actuals:
  tokens: 2264      # 9056 chars / 4 over the 4 modified/created files
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Opaque #[pyclass] handle: second instance of PyIrregFdata mirror pattern (pace_fpca_mod.rs)"
    - "Pre-constructor guards: outer-list length + 1D-data rejection before MultiFunData::new; nrows/argvals-len delegated to core"
    - "numpy::PyUntypedArray ndim() check (dtype-agnostic) for 1D rejection guard"

key-files:
  created:
    - src/multi_fdata_mod.rs
    - tests/test_multi_fdata.py
  modified:
    - src/lib.rs
    - python/fdars/__init__.py

key-decisions:
  - "PyMultiFunData documented as standalone container — module-level //! comment records that no 0.33 FAMM/MFPCA/clustering function accepts it; MULTI-02 'where required' phrase is vacuously satisfied (0 consumers in 0.33)"
  - "Guard order: outer-list length check first, then 1D rejection per element, then core constructor validates nrows uniformity and argvals.len()==ncols — mirrors pace_fpca_mod.rs guard layering"
  - "numpy1d_to_vec used for argvals (not extract_ragged_vecs) — components supply uniform 1D arrays, not ragged lists"

patterns-established:
  - "Pattern: opaque handle #[pyclass] for multi-component fdars-core types (second instance)"
  - "Pattern: pre-constructor guard chain (length → ndim → core) prevents panics on bad Python input"

requirements-completed: [MULTI-01]

coverage:
  - id: D1
    description: "fdars.multi_fdata submodule registered and importable; PyMultiFunData and multi_fdata_from_components present"
    requirement: MULTI-01
    verification:
      - kind: integration
        ref: "python -c \"import fdars.multi_fdata as mf; assert callable(mf.multi_fdata_from_components); assert hasattr(mf, 'PyMultiFunData')\""
        status: pass
    human_judgment: false
  - id: D2
    description: "multi_fdata_from_components builds PyMultiFunData from non-square components; n_obs and n_components return correct values"
    requirement: MULTI-01
    verification:
      - kind: unit
        ref: "tests/test_multi_fdata.py#test_build_and_accessors"
        status: pass
    human_judgment: false
  - id: D3
    description: "Outer list-length mismatch raises ValueError before MultiFunData::new"
    requirement: MULTI-01
    verification:
      - kind: unit
        ref: "tests/test_multi_fdata.py#test_reject_length_mismatch"
        status: pass
    human_judgment: false
  - id: D4
    description: "1-D data array passed as component raises ValueError (2-D required)"
    requirement: MULTI-01
    verification:
      - kind: unit
        ref: "tests/test_multi_fdata.py#test_reject_1d_data"
        status: pass
    human_judgment: false
  - id: D5
    description: "Components with different nrows raises ValueError (surfaced from MultiFunData::new)"
    requirement: MULTI-01
    verification:
      - kind: unit
        ref: "tests/test_multi_fdata.py#test_reject_nrows_mismatch"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-09-03
status: complete
---

# Phase 70 Plan 01: PyMultiFunData Opaque Handle + `fdars.multi_fdata` Submodule Summary

**PyMultiFunData opaque #[pyclass] handle — pyfda's second opaque Rust type — with a list-of-components builder, n_obs/n_components accessors, and three pre-constructor validation guards, registered as fdars.multi_fdata**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-03T21:07:18Z
- **Completed:** 2026-09-03T21:12:14Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- New `src/multi_fdata_mod.rs`: `PyMultiFunData` opaque `#[pyclass]` wrapping `fdars_core::multi_fdata::MultiFunData`, mirroring the `PyIrregFdata` pattern from `pace_fpca_mod.rs`
- `multi_fdata_from_components(data_list, argvals_list)` builder with three-layer guard chain (outer-length, 1D-rejection, core constructor) before `MultiFunData::new`
- `n_obs` and `n_components` `#[getter]` accessors delegating to the inner Rust type
- Module-level `//!` comment explicitly documents that no fdars-core 0.33 FAMM/MFPCA/clustering function consumes this handle — standalone container only
- `lib.rs` and `__init__.py` registrations wired; `import fdars.multi_fdata` works end-to-end
- `tests/test_multi_fdata.py`: 4 tests (happy-path non-square build + 3 guard failures), all passing

## Task Commits

1. **Task 1: Create src/multi_fdata_mod.rs + lib.rs + __init__.py (tracer)** - `27c093a` (feat)
2. **Task 2: Create tests/test_multi_fdata.py (TDD)** - `806dce8` (test)

## Files Created/Modified

- `src/multi_fdata_mod.rs` — PyMultiFunData handle, multi_fdata_from_components builder, register fn
- `tests/test_multi_fdata.py` — 4 pytest tests covering MULTI-01 happy-path and all three guard cases
- `src/lib.rs` — added `mod multi_fdata_mod;` + `register_submodule!(m, "multi_fdata", ...)`
- `python/fdars/__init__.py` — appended `"multi_fdata"` to `_submodule_names` (Phase 70 comment)

## Decisions Made

- `PyMultiFunData` documented as a standalone container: the module-level `//!` comment in `multi_fdata_mod.rs` explicitly states no 0.33 FAMM/MFPCA/clustering function accepts it. This preempts any future misreading of MULTI-02's "where required" phrase (vacuously satisfied: 0 consumers).
- Guard order mirrors `pace_fpca_mod.rs`: outer-length check first → per-element 1D rejection → delegate nrows/argvals consistency to `MultiFunData::new` via `to_pyresult`. Avoids panic before the core can validate.
- `numpy1d_to_vec` used for argvals (not `extract_ragged_vecs`) — components supply uniform 1D arrays, not ragged lists; the simpler helper is appropriate.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- MULTI-01 complete: `PyMultiFunData` handle registered, constructible, tested
- Plan 70-02 (`famm_mod.rs`) is independent of this handle — FAMM functions take plain `FdMatrix` inputs; no ordering constraint blocks it
- Plan 70-03 (spm extension) and Plan 70-04 (clustering extension) likewise independent
- Full test suite: 5447 passed, 10 skipped, 0 failures — no regressions introduced

## Self-Check: PASSED

- `src/multi_fdata_mod.rs` exists: FOUND
- `tests/test_multi_fdata.py` exists: FOUND
- Commit `27c093a` exists: FOUND
- Commit `806dce8` exists: FOUND
- `pytest tests/test_multi_fdata.py`: 4 passed
- `pytest tests/ -q`: 5447 passed, 10 skipped, 0 failures

---
*Phase: 70-multi-domain-data-famm-advanced-clustering*
*Completed: 2026-09-03*
