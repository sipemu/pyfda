---
phase: 27-scoring-metrics-alignment-registration-bindings
plan: "02"
subsystem: alignment
status: complete
tags: [rust, pyo3, fdars-core, alignment, registration, banded, shift-registration]

dependency_graph:
  requires:
    - 27-01-SUMMARY.md  # fdars.scoring baseline; 351 tests green
  provides:
    - fdars.alignment.least_squares_shift_registration (dict result)
    - fdars.alignment.least_squares_score
    - fdars.alignment.pairwise_correlation_score
    - fdars.alignment.sobolev_least_squares_score
    - fdars.alignment.karcher_mean_with_band
    - fdars.alignment.elastic_self_distance_matrix_with_band
    - fdars.alignment.elastic_cross_distance_matrix_with_band
    - Fdata.shift_register() method
  affects:
    - src/alignment_mod.rs  # +7 pyfunctions
    - python/fdars/fdata_class.py  # +shift_register() method
    - tests/test_alignment_registration.py  # 37 tests (NEW)

tech_stack:
  added: []
  patterns:
    - "#[pyfunction] thin wrappers calling fdars_core::alignment::* via to_pyresult()"
    - "PyDict result marshalling for ShiftRegistrationResult (mirrors karcher_mean)"
    - "fdmatrix_to_numpy2d for all matrix returns (transposition guard #33)"
    - "Option<f64> band_frac with None=unbanded default"

key_files:
  created:
    - tests/test_alignment_registration.py
  modified:
    - src/alignment_mod.rs
    - python/fdars/fdata_class.py

decisions:
  - "Bind *_with_band variants (band_frac: Option<f64>=None) NOT *_banded (band_frac: f64 where 0.0 does NOT disable) — per CONTEXT.md locked decision"
  - "ShiftRegistrationResult marshalled as PyDict {registered_data, shifts} — consistent with karcher_mean dict convention"
  - "fd.shift_register() returns (Fdata, ndarray) 2-tuple — registered Fdata preserves argvals/rangeval/names/id/metadata"
  - "sobolev_least_squares_score: lambda_ parameter renamed from 'lambda' to avoid Rust keyword collision; non-uniform grid + lambda>0 raises ValueError via to_pyresult"
  - "All 7 new pyfunctions compiled in a single maturin build after tracer commit to avoid extra compile cycles"

metrics:
  duration_seconds: 364
  completed_date: "2026-08-15"
  tasks_completed: 3
  commits: 2
  files_modified: 3
  tests_added: 37

actuals:
  tokens: 17000
  tasks: 3
  commits: 2
---

# Phase 27 Plan 02: Alignment Registration Additions Summary

Shift registration, registration-quality scores, and banded elastic alignment added to `fdars.alignment`. +7 pyfunctions in `src/alignment_mod.rs`, `fd.shift_register()` in `fdata_class.py`, 37 new tests. Full suite 388 passed / 4 skipped (was 351/4 baseline — no regressions).

## What Was Built

### Task 1 (Tracer): `least_squares_shift_registration`
`fdars.alignment.least_squares_shift_registration(data, argvals, max_shift)` returns a `PyDict` with two keys:
- `registered_data` — shape `(n, m)` ndarray of shifted curves on the original grid
- `shifts` — shape `(n,)` float64 ndarray of per-curve horizontal shifts

Fallible via `to_pyresult()` — no `.unwrap()`. Verified end-to-end with dict-shape + identity-shift tests before any expansion task.

### Task 2: Quality Scores + `fd.shift_register()`
Three registration-quality scoring functions:
- `least_squares_score(registered, argvals)` → `f64` (mean L2 spread; lower is better)
- `pairwise_correlation_score(registered, argvals)` → `f64` (range approximately `[-1, 1]`; higher is better)
- `sobolev_least_squares_score(registered, argvals, lambda_=0.0)` → `f64` (LS + derivative penalty; requires uniform grid when `lambda_ > 0` — raises `ValueError` otherwise)

`Fdata.shift_register(max_shift)` method returns `(registered_fdata, shifts)` — registered `Fdata` preserves `argvals`, `rangeval`, `names`, `id`, `metadata`.

### Task 3: Banded `*_with_band` Functions
Three banded elastic alignment functions with `band_frac: Option<f64>=None` (unbanded when `None`):
- `karcher_mean_with_band` — same dict keys as `karcher_mean`; `band_frac=None` matches unbanded result
- `elastic_self_distance_matrix_with_band` — `(n, n)` symmetric matrix; zero diagonal
- `elastic_cross_distance_matrix_with_band` — `(n1, n2)` matrix

All matrix returns route through `fdmatrix_to_numpy2d` (transposition guard #33).

## Test Results

| Category | Tests |
|----------|-------|
| least_squares_shift_registration (Task 1) | 8 |
| Quality scores (Task 2) | 8 |
| fd.shift_register() (Task 2) | 6 |
| karcher_mean_with_band (Task 3) | 4 |
| elastic_self_distance_matrix_with_band (Task 3) | 6 |
| elastic_cross_distance_matrix_with_band (Task 3) | 4 |
| no-_banded-variants grep gate (Task 3) | 1 |
| **Total new** | **37** |
| **Full suite** | **388 passed / 4 skipped** |

## Success Criteria Verification

- [x] `least_squares_shift_registration` returns `{registered_data (n,m), shifts (n,)}` — confirmed by `sorted(result.keys()) == ['registered_data', 'shifts']`
- [x] `fd.shift_register()` returns `(Fdata, shifts)` with same argvals, n_obs, shifts shape `(n_obs,)`
- [x] Three quality scores return finite in-range floats; `sobolev(lambda=0) ≈ least_squares_score`; sobolev non-uniform + lambda>0 raises `ValueError`
- [x] `karcher_mean_with_band(band_frac=None)` ≈ unbanded `karcher_mean` to tolerance
- [x] Banded distance matrices route through `fdmatrix_to_numpy2d`; multi-curve DISTINCT-per-curve transposition round-trip passes (d[0,2] matches independently computed pairwise distance)
- [x] No `_banded` variant bound (grep gate == 0); no `.unwrap()` on fallible results
- [x] Full suite 388 passed / 4 skipped — no regressions vs 351 baseline

## Threat Mitigations Applied (T-27-02)

| Threat | Mitigation |
|--------|-----------|
| T-27-02-01: Transposition on banded matrices | All 3 banded matrix returns route through `fdmatrix_to_numpy2d`; DISTINCT-per-curve round-trip test asserts `D[0,2]` matches independent pairwise |
| T-27-02-02: `.unwrap()` panic on fallible Results | `to_pyresult()` on all fallible calls; `pytest.raises(ValueError)` for sobolev non-uniform grid |
| T-27-02-03: Binding wrong banded API (`_banded` vs `_with_band`) | Bound `_with_band` (Option<f64>=None); grep gate asserts no `_banded` variant; `band_frac=None` equals unbanded test |
| T-27-02-04: ShiftRegistrationResult dropping shifts | Dict-shape test asserts both `registered_data` and `shifts` keys with correct shapes and dtype |

## Deviations from Plan

### Auto-confirmed: Commit structure
The plan specified 3 separate per-task commits, but Tasks 2 and 3 were staged together in the Task 2 commit because all 7 pyfunctions were added to `alignment_mod.rs` in a single Edit operation during the tracer expansion. The test file already included all Task 3 tests when written. No functionality was affected; all acceptance criteria are met.

Rule: None — the plan's commit structure is advisory; functional delivery is complete.

## Known Stubs

None — all bound functions wire to real fdars-core 0.17.0 implementations.

## Self-Check: PASSED

- `src/alignment_mod.rs` exists and contains 7 new pyfunctions: FOUND
- `python/fdars/fdata_class.py` contains `def shift_register`: FOUND (line 728)
- `tests/test_alignment_registration.py` exists with 37 tests: FOUND
- Commit `345272f` (Task 1 tracer): FOUND
- Commit `c0fb834` (Tasks 2+3 expansion): FOUND
- Full suite: 388 passed / 4 skipped — no regressions: VERIFIED
