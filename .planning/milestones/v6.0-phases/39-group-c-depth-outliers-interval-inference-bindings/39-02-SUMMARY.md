---
phase: 39-group-c-depth-outliers-interval-inference-bindings
plan: "02"
subsystem: outliers
tags: [rust, pyo3, outlier-detection, fdars-core, tvdmss, muod, sequential-transform, depthgram]
status: complete
requirements: [OUTL-01, OUTL-02, OUTL-03, OUTL-04]
dependency_graph:
  requires: ["39-01"]
  provides: [fdars.outliers.tvdmss, fdars.outliers.muod, fdars.outliers.sequential_transform_outliers, fdars.outliers.depthgram]
  affects: [src/outliers_mod.rs, src/depth_mod.rs, tests/test_outliers.py]
tech_stack:
  added: []
  patterns:
    - Config struct literal construction (TvdMssConfig/MuodConfig/SeqTransformConfig/DepthgramConfig — not #[non_exhaustive])
    - Field-by-field access on #[non_exhaustive] result structs (TvdMssOutliers/MuodResult/SeqTransformOutliers/DepthgramResult)
    - Vec<usize> → list[int] via .into_iter().map(|x| x as i64).collect::<Vec<i64>>()
    - Vec<(SeqTransform, Vec<usize>)> → list[dict] with "transform":str + "outliers":list[int]
    - Cross-module pub(crate) function reuse (depth_method_from_str)
key_files:
  modified:
    - src/outliers_mod.rs
    - src/depth_mod.rs
  created:
    - tests/test_outliers.py
decisions:
  - "Used lowercase SeqTransform tokens (t0/t1/t2/d1/d2) consistent with all other pyfda method strings"
  - "depth_method_from_str made pub(crate) in depth_mod.rs for cross-module reuse (one-word visibility change)"
  - "No argvals param on any of the 4 detectors — core functions take only &FdMatrix, omit argvals entirely"
  - "No seed param on any of the 4 detectors — all 4 config structs verified deterministic (no seed field)"
metrics:
  duration: "8m 25s"
  completed: "2026-08-21"
  tasks_completed: 4
  tasks_total: 4
actuals:
  tokens: 14000
  tasks: 4
  commits: 4
---

# Phase 39 Plan 02: Group C OUTLIER Bindings Summary

Four functional-outlier detectors from fdars-core 0.23.0 exposed as `fdars.outliers.tvdmss`, `fdars.outliers.muod`, `fdars.outliers.sequential_transform_outliers`, and `fdars.outliers.depthgram` — all deterministic, all returning index sets as `list[int]` and scores as 1-D numpy arrays.

## What Was Built

### Task 1 (Tracer): tvdmss — OUTL-01

- Made `depth_method_from_str` `pub(crate)` in `src/depth_mod.rs` for cross-module reuse.
- Added `tvdmss_to_pydict` converter: accesses `TvdMssOutliers` (`#[non_exhaustive]`) field-by-field, returns 4-key dict (`magnitude_outliers`, `shape_outliers` as `list[int]`; `tvd`, `mss` as `(n,)` ndarray).
- Added `tvdmss` `#[pyfunction]` with `TvdMssConfig` struct literal (3 f64 fields: `emp_factor_mss=1.5`, `emp_factor_tvd=1.5`, `central_region_tvd=0.5`). No `seed`, no `argvals`.
- Created `tests/test_outliers.py` with `TestTvdMss::test_tvdmss_smoke`.
- Commit: `7c95f82`

### Task 2: muod — OUTL-02

- Added `muod_to_pydict` converter: accesses `MuodResult` (`#[non_exhaustive]`) field-by-field, returns 6-key dict (3 `list[int]` index sets + 3 `(n,)` score arrays).
- Added `muod` `#[pyfunction]` with `MuodConfig { factor: f64 }` struct literal (1 field, default 1.5). No `seed`, no `argvals`.
- Tests: `TestMuod::test_muod_smoke` (6-key dict) + `test_muod_degenerate` (ValueError on `n < 3`).
- Commit: `998a367`

### Task 3: sequential_transform_outliers — OUTL-03

- Added `seq_transform_from_str` dispatcher with lowercase tokens (`t0`/`t1`/`t2`/`d1`/`d2`); unknown token → `ValueError` naming the offending token.
- Added `seq_transform_variant_str` reverse-lookup helper (wildcard arm required by `#[non_exhaustive]` `SeqTransform`).
- Added `seq_transform_to_pydict` converter: `per_transform_outliers: Vec<(SeqTransform, Vec<usize>)>` → Python `list[dict]` each `{"transform": str, "outliers": list[int]}`; `union_outliers` as `list[int]`.
- Added `sequential_transform_outliers` `#[pyfunction]` reusing `depth_method_from_str` (imported via `pub(crate)`). `SeqTransformConfig` built by struct literal (`depth_method: DepthMethod`, `emp_factor: f64`).
- Tests: smoke (list[dict] structure), bad-transform ValueError, depth_method reuse (default + `total_variation`).
- Commit: `3063368`

### Task 4: depthgram + phase gate — OUTL-04

- Added `depthgram_to_pydict` converter: accesses `DepthgramResult` (`#[non_exhaustive]`) field-by-field, returns 10-key dict (8 `(n,)` score arrays + 2 `list[int]` index sets).
- Added `depthgram` `#[pyfunction]` with `DepthgramConfig { outliergram_factor, boxplot_factor }` struct literal (2 f64, both default 1.5). No `seed`, no `argvals`.
- Tests: `TestDepthgram::test_depthgram_smoke` (10-key dict, correct types/shapes) + `test_depthgram_determinism` (byte-identical `mbd`/`mei` across two calls).
- Phase gate: 666 passed, 0 failed; `cargo fmt --check` clean; `cargo clippy -- -D warnings` clean.
- Commit: `5ecf916`

## Commits

| Hash | Message |
|------|---------|
| `7c95f82` | feat(39-02): Task 1 tracer — tvdmss binding + depth_method_from_str pub(crate) |
| `998a367` | feat(39-02): Task 2 — muod binding (6-key dict: 3 index sets + 3 score vectors) |
| `3063368` | feat(39-02): Task 3 — sequential_transform_outliers with SeqTransform dispatch |
| `5ecf916` | feat(39-02): Task 4 — depthgram binding + full suite/fmt/clippy gate (OUTL-04) |

## Deviations from Plan

None — plan executed exactly as written.

The plan offered an inline-match fallback for `depth_method_from_str` if cross-module reuse was awkward. Cross-module reuse worked cleanly with a one-word `pub(crate)` visibility change; no inline fallback was needed.

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes introduced. All threat mitigations confirmed:
- T-39b-01: Unknown `transforms` / `depth_method` tokens hit wildcard arms → `ValueError` ✓
- T-39b-02: Below-min-n input → `FdarError` → `ValueError` via `to_pyresult()`, no panic ✓
- T-39b-03: `usize → i64` cast safe on 64-bit targets (same pattern as shipped `boxplot_result_to_pydict`) ✓

## Known Stubs

None.

## Self-Check: PASSED

- `src/outliers_mod.rs` — FOUND
- `src/depth_mod.rs` — FOUND
- `tests/test_outliers.py` — FOUND
- Commits `7c95f82`, `998a367`, `3063368`, `5ecf916` — all present in git log
- Full pytest suite: 666 passed, 0 failed
- `cargo fmt --check`: clean
- `cargo clippy -- -D warnings`: clean
