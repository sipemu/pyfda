---
phase: 39-group-c-depth-outliers-interval-inference-bindings
plan: "03"
subsystem: inference bindings (ITP)
tags: [rust, pyo3, inference, interval-testing, itp, numpy]
status: complete

dependency_graph:
  requires: []
  provides:
    - fdars.inference.itp_one_pop
    - fdars.inference.itp_two_pop
    - fdars.inference.itp_flm
  affects:
    - src/inference_mod.rs
    - tests/test_inference.py

tech_stack:
  added: []
  patterns:
    - itp_result_to_pydict: Vec<f64> p-values → 1-D numpy via vec_to_numpy1d (distinct from test_result_to_pydict)
    - basis_type_from_str: string dispatch for #[non_exhaustive] ProjectionBasisType (bspline/fourier)
    - basis_type_variant_str: ProjectionBasisType → &'static str for dict serialisation
    - mu0_optional: Option<PyReadonlyArray1> → mu0.map(numpy1d_to_vec).as_deref() for Option<&[f64]>

key_files:
  modified:
    - src/inference_mod.rs
    - tests/test_inference.py

decisions:
  - Use fdars_core::inference::{itp_one_pop,itp_two_pop,itp_flm,ItpResult} re-export path (confirmed at v0.23.0 inference/mod.rs:40)
  - Use fdars_core::ProjectionBasisType crate-root re-export (confirmed at v0.23.0 lib.rs:462)
  - mu0 converted via mu0.map(numpy1d_to_vec).as_deref() — avoids lifetime issues vs as_ref().map(...).transpose()? pattern
  - itp_result_to_pydict is a new private function, not an overload of test_result_to_pydict (different key set)
  - seed=None → 0 matches t_perm_test convention for byte-identical permutation reproducibility

metrics:
  duration: "443s (~7 min)"
  completed: "2026-08-21T05:58:40Z"
  tasks_completed: 3
  commits: 3
  files_modified: 2

actuals:
  tokens: 4638    # 18553 chars / 4 over the diff
  tasks: 3
  commits: 3
---

# Phase 39 Plan 03: Group C INTERVAL-INFERENCE (ITP) Bindings Summary

Three interval-wise testing procedures from fdars-core 0.23.0 — `itp_one_pop`, `itp_two_pop`, `itp_flm` — are now callable from Python under `fdars.inference`. Each returns an `ItpResult`-derived dict with vector p-values as 1-D numpy arrays, a string basis_type, and integer n_basis/n_perm.

## What Was Built

### New Symbols in `src/inference_mod.rs`

| Symbol | Kind | Purpose |
|--------|------|---------|
| `basis_type_from_str` | private fn | String → ProjectionBasisType dispatch; unknown token → ValueError |
| `basis_type_variant_str` | private fn | ProjectionBasisType → &'static str ("bspline"/"fourier"/"unknown") |
| `itp_result_to_pydict` | private fn | #[non_exhaustive] ItpResult → 5-key PyDict with 1-D p-value arrays |
| `itp_one_pop` | #[pyfunction] | One-population ITP; optional null mean mu0; bspline/fourier dispatch |
| `itp_two_pop` | #[pyfunction] | Two-population ITP; seeded permutation; deterministic under seed=None |
| `itp_flm` | #[pyfunction] | FLM ITP; raw data+response re-fits internally; no persistent handle |

All three functions appended to `inference_mod::register()`.

### New Tests in `tests/test_inference.py`

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestItpOnePop` | 3 | smoke (5-key dict, shape n_basis, [0,1]), fourier dispatch, invalid-basis ValueError |
| `TestItpTwoPop` | 3 | smoke, seed=None determinism (np.array_equal), nbasis=1 ValueError |
| `TestItpFlm` | 3 | smoke, bad-basis ValueError matching token, fourier round-trip |

## Key Technical Decisions

- **itp_result_to_pydict is DISTINCT from test_result_to_pydict**: The existing helper returns `{statistic:f64, p_value:f64, n_perm:usize}`; the new one returns `{adjusted_pvalues:ndarray, raw_pvalues:ndarray, basis_type:str, n_basis:int, n_perm:int}`. Vector p-values require `vec_to_numpy1d`; scalar p-value would silently drop data if the wrong converter were used.
- **n_basis vs nbasis**: B-spline clamping may reduce the actual basis count below the requested `nbasis`. Tests assert `shape == (result["n_basis"],)`, not `== nbasis`.
- **mu0 conversion**: `mu0.map(numpy1d_to_vec).as_deref()` converts `Option<PyReadonlyArray1>` to `Option<&[f64]>` cleanly without transpose lifetime complexity.
- **Fully-qualified import path confirmed**: `fdars_core::inference::{itp_one_pop, itp_two_pop, itp_flm, ItpResult}` are re-exported at the inference module level (not the itp submodule). `fdars_core::ProjectionBasisType` is at crate root. Both verified against v0.23.0 source.

## Verification Results

- `maturin develop`: builds green after each task (3 incremental builds).
- `pytest tests/test_inference.py::TestItpOnePop -x -q`: 3 passed (tracer gate).
- `pytest tests/test_inference.py::TestItpTwoPop -q`: 3 passed.
- `pytest tests/test_inference.py::TestItpFlm -q`: 3 passed.
- `pytest tests/ -q`: **675 passed, 4 skipped — zero regression**.
- `cargo fmt --check`: clean (one fmt fix applied to itp_flm call site line break).
- `cargo clippy -- -D warnings`: clean.

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 09244bd | feat(39-03) | itp_one_pop tracer + itp_result_to_pydict + basis_type dispatch |
| 981612e | feat(39-03) | itp_two_pop binding — two-sample ITP + seeded determinism |
| 960a084 | feat(39-03) | itp_flm binding + register all 3 ITP fns; fmt/clippy clean |

## Deviations from Plan

**1. [Rule 1 - Bug] rustfmt line-length fix on itp_flm call site**
- **Found during:** Task 3 `cargo fmt --check`
- **Issue:** `fdars_core::inference::itp_flm(&mat, &y, &av, bt, nbasis, n_perm, s)` exceeded rustfmt line width when wrapped in `to_pyresult(...))?;`
- **Fix:** Broke the call across 3 lines per rustfmt's style (matching the itp_one_pop call above it)
- **Files modified:** `src/inference_mod.rs`
- **Commit:** 960a084 (included in Task 3 commit)

No architectural deviations. The plan was executed exactly as written.

## Known Stubs

None. All three ITP functions are fully wired end-to-end: Python kwargs → FdMatrix/slice conversion → fdars-core call → ItpResult field-by-field → PyDict with 1-D numpy p-value arrays.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. The three ITP functions follow the same trust model as all other fdars.inference functions: untrusted Python inputs (data matrices, argvals, basis_type strings, usize parameters) validated by `basis_type_from_str` (wildcard ValueError) and fdars-core's own guards (nbasis<2, n_perm==0, n<2, length mismatches — all surfaced as ValueError via `to_pyresult()`). No new STRIDE threats beyond those documented in the plan's threat register (T-39c-01..03, all mitigated).

## Self-Check: PASSED

- `src/inference_mod.rs` — FOUND
- `tests/test_inference.py` — FOUND
- Task 1 commit 09244bd — FOUND
- Task 2 commit 981612e — FOUND
- Task 3 commit 960a084 — FOUND
- All 3 ITP functions importable under `fdars.inference` — VERIFIED
- Full suite 675 passed, 4 skipped — VERIFIED
- cargo fmt --check — CLEAN
- cargo clippy -- -D warnings — CLEAN
