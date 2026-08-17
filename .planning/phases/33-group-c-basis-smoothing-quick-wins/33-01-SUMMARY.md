---
phase: 33-group-c-basis-smoothing-quick-wins
plan: "01"
subsystem: basis-smoothing
tags: [basis, smoothing, aic, pyo3, bindings]
status: complete

dependency_graph:
  requires:
    - Phase 30 (0.20 baseline; CvCriterion non_exhaustive wildcard arm already present)
  provides:
    - fdars.basis.constant_basis (BASIS-01)
    - fdars.basis.smooth_basis_aic (BASIS-02)
    - fdars.smoothing.optim_bandwidth(criterion="aic") (BASIS-03)
  affects:
    - Phase 35 (docs page for the new bindings — DOCS-06)

tech_stack:
  added:
    - constant_basis PyO3 binding (infallible Vec<f64> → 1-D ndarray via vec_to_numpy1d)
    - smooth_basis_aic PyO3 binding (copy of smooth_basis_gcv, AIC-optimal lambda)
    - CvCriterion::Aic input dispatch arm in optim_bandwidth
    - CvCriterion::Aic => "aic" output arm in optim_bandwidth (replaces Phase-30 stopgap)
  patterns:
    - String criterion dispatch → enum arm (CvCriterion / BasisCriterion)
    - Option<SmoothBasisResult>::None → PyValueError for degenerate input
    - Infallible core fn → Ok(vec_to_numpy1d(...)) with PyResult return type

key_files:
  created:
    - tests/test_basis_smoothing.py (11 tests covering all 3 tasks)
  modified:
    - src/basis_mod.rs (constant_basis + smooth_basis_aic + PyArray1 import)
    - src/smoothing_mod.rs (optim_bandwidth AIC input arm + explicit AIC output arm)

decisions:
  - "smooth_basis_aic placed in basis_mod.rs (beside GCV twin) not smoothing_mod.rs — follows closest existing analog placement delegated to execute time in 33-CONTEXT.md"
  - "CvCriterion::Aic output arm added explicitly; _ => 'unknown' wildcard retained for #[non_exhaustive] forward-compat — enum is non_exhaustive so wildcard cannot be removed"
  - "constant_basis returns 1-D ndarray (not 2-D matrix) — core returns plain Vec<f64>, plan specifies 1-D via vec_to_numpy1d"
  - "basis_nbasis_cv aic support was already shipped in a prior phase; this plan adds test coverage only (no Rust edit)"

metrics:
  duration: "~5 minutes"
  completed: "2026-08-17"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
  files_changed: 3

actuals:
  tokens: 15000
  tasks: 3
  commits: 3
---

# Phase 33 Plan 01: Basis/Smoothing Quick Wins Summary

**One-liner:** AIC model selection added for kernel bandwidth (optim_bandwidth), basis smoothing (smooth_basis_aic), and intercept column (constant_basis) via three additive PyO3 bindings against fdars-core 0.20.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (tracer) | optim_bandwidth AIC kernel-bandwidth path | 791b4ea | src/smoothing_mod.rs, tests/test_basis_smoothing.py |
| 2 | constant_basis all-ones intercept column | d1ebc83 | src/basis_mod.rs, tests/test_basis_smoothing.py |
| 3 | smooth_basis_aic + basis_nbasis_cv aic test | 5e747c7 | src/basis_mod.rs, tests/test_basis_smoothing.py |

## What Was Built

### BASIS-03: optim_bandwidth(criterion="aic") (Task 1 — tracer)
Added `"aic" => CvCriterion::Aic` input arm in `src/smoothing_mod.rs` alongside the existing "cv"/"gcv" arms. Added explicit `CvCriterion::Aic => "aic"` output arm, replacing the Phase-30 stopgap where AIC results fell through to `_ => "unknown"`. The `_` wildcard arm is retained for `#[non_exhaustive]` forward-compatibility. Updated the error message to list all three accepted criterion strings.

### BASIS-01: constant_basis (Task 2)
Added `constant_basis` `#[pyfunction]` in `src/basis_mod.rs`. Takes `argvals: PyReadonlyArray1<f64>`, converts to Vec, calls the infallible `fdars_core::basis::constant_basis`, and returns via `vec_to_numpy1d`. Returns a 1-D float64 ndarray of shape (m,) with all entries equal to 1.0. Empty input returns a length-0 array without panicking.

### BASIS-02: smooth_basis_aic + basis_nbasis_cv aic (Task 3)
Added `smooth_basis_aic` `#[pyfunction]` in `src/basis_mod.rs` as a verbatim copy of `smooth_basis_gcv` with only the fdars-core call changed to `smooth_basis_aic`. Identical parameter set, identical PyDict field map (fitted, coefficients, edf, gcv, aic, bic, nbasis), identical `Option::None → PyValueError` handling. Added test coverage for `basis_nbasis_cv(criterion="aic")` — the Rust implementation was already shipping from a prior phase; no Rust edit required.

## Verification

- `maturin develop`: green (all 3 commits)
- `cargo clippy -- -D warnings`: green
- `cargo fmt --check`: green
- `python -m pytest tests/test_basis_smoothing.py -q`: 11/11 passed
- Full suite (480 tests + 1 skipped): green, no regressions
- Import check: `fdars.basis.constant_basis`, `fdars.basis.smooth_basis_aic`, `fdars.smoothing.optim_bandwidth` all importable

## Deviations from Plan

None — plan executed exactly as written. `basis_nbasis_cv` "aic" support was already implemented per the Prior-work note; only test coverage was added (no Rust edit), consistent with the plan's instructions.

## Known Stubs

None. All three artifacts are fully wired to fdars-core 0.20 functions and return real computed results.

## Self-Check: PASSED

- `src/basis_mod.rs` — modified (constant_basis + smooth_basis_aic)
- `src/smoothing_mod.rs` — modified (optim_bandwidth AIC arms)
- `tests/test_basis_smoothing.py` — created (11 tests)
- Commits 791b4ea, d1ebc83, 5e747c7 — all present in git log
