---
phase: 32-group-b-depth-boxplot-bindings
plan: "01"
subsystem: depth-bindings
tags: [rust, pyo3, depth, boxplot, functional-data-analysis]
status: complete

dependency_graph:
  requires:
    - 30-01 (fdars-core 0.20 baseline green)
    - 31-01 (Phase 31 inference bindings — patterns mirrored)
  provides:
    - fdars.depth.functional_depth (DEPTH-01)
    - fdars.depth.functional_boxplot (DEPTH-02)
  affects:
    - src/depth_mod.rs
    - tests/test_depth.py

tech_stack:
  added:
    - fdars_core::depth::dispatch::{DepthMethod, FunctionalBoxplotResult} (via re-export at fdars_core::depth)
    - fdars_core::depth::{functional_depth, functional_boxplot} (0.20 dispatch functions)
  patterns:
    - depth_method_from_str: string -> DepthMethod with non_exhaustive wildcard ValueError arm
    - boxplot_result_to_pydict: non_exhaustive field access (no struct literal); outliers Vec<usize> -> Python list of i64
    - seed=None -> 0 (mirrors Phase 31 seed contract; byte-identical reproducibility by default)

key_files:
  created:
    - tests/test_depth.py (27 tests — TDD RED + GREEN)
  modified:
    - src/depth_mod.rs (extended with depth_method_from_str, boxplot_result_to_pydict, functional_depth, functional_boxplot)

decisions:
  - "Used re-exported paths fdars_core::depth::{DepthMethod, FunctionalBoxplotResult, functional_depth, functional_boxplot} rather than the dispatch submodule paths — cleaner and matches the public API surface."
  - "outliers: Vec<usize> -> Vec<i64> -> Python list via PyO3 auto-conversion; not an ndarray — matches the locked 32-CONTEXT.md decision."
  - "seed=None resolves to u64 default 0 inside depth_method_from_str — same contract as Phase 31 inference multiplier; two calls with seed=None produce byte-identical results."
  - "All 27 test assertions written in a single tests/test_depth.py (not split into separate files) following existing test_inference.py conventions."

metrics:
  duration_minutes: 4
  completed_date: "2026-08-17"
  tasks_completed: 2
  commits: 2

actuals:
  tokens: 7669
  tasks: 2
  commits: 2
---

# Phase 32 Plan 01: Depth/Boxplot Bindings Summary

**One-liner:** Unified string-dispatched `functional_depth` + `functional_boxplot` with 7-key dict contract and layout-guard tests, extending `fdars.depth` via fdars-core 0.20 dispatch functions.

## What Was Built

### Task 1 — functional_depth (DEPTH-01)

**`depth_method_from_str(method, scale, nproj, seed)`** — private Rust helper that maps a Python string to `fdars_core::depth::DepthMethod`, with `#[non_exhaustive]` wildcard `_ => PyValueError` fallback. seed=None resolves to 0 (mirror of Phase 31 contract).

**`fdars.depth.functional_depth(data, method="fraiman_muniz", scale=True, nproj=50, seed=None)`** — returns `ndarray (n,)` of self-depth values, dispatching to all four DepthMethod variants: FraimanMuniz, Band, ModifiedBand, RandomProjection.

### Task 2 — functional_boxplot (DEPTH-02)

**`boxplot_result_to_pydict`** — private helper that accesses each `FunctionalBoxplotResult` field individually (never struct-literal the `#[non_exhaustive]` type). Band fields converted via `vec_to_numpy1d`; outliers via `Vec<i64>` → Python list.

**`fdars.depth.functional_boxplot(data, method="modified_band", factor=1.5, ...)`** — returns a 7-key dict: `{median, central_lower, central_upper, whisker_lower, whisker_upper, outliers, depths}`. Band fields are 1-D ndarrays of length m; depths is length n; outliers is a Python list of ints.

### Test Coverage (27 tests)

- TDD RED commit (076e3e5): full test file before any Rust code
- TDD GREEN commit (75d45a7): implementation passes all 27 tests
- Import path tests (both `import fdars.depth` and `from fdars.depth import functional_depth`)
- Shape tests for all 4 methods
- `fraiman_muniz_1d` self-depth cross-check (within `np.allclose`)
- Seed determinism for random_projection (explicit seed + seed=None)
- 7-key dict contract assertion
- Layout guard: band fields shape (m,), depths shape (n,), outliers list of ints in [0,n)
- Transposition guard: asserts band field lengths equal m, not n (when n != m)
- Degenerate ValueError coverage: empty data, <2 curves for band/boxplot, nproj=0, negative factor, unknown method

## Commits

| Hash | Message |
|------|---------|
| 076e3e5 | test(32-01): add failing tests for functional_depth and functional_boxplot (RED) |
| 75d45a7 | feat(32-01): implement functional_depth + functional_boxplot in fdars.depth (GREEN) |

## Verification Results

- `cargo fmt --check`: 0 (clean)
- `cargo clippy -- -D warnings`: 0 (clean; wildcard arm present; no unwrap)
- `maturin develop`: 0 (build green)
- `python -m pytest tests/test_depth.py -q`: 27 passed
- Full suite (excluding live integration): 465 passed, 1 skipped (no regressions)

## Deviations from Plan

None — plan executed exactly as written. Both TDD gates (RED then GREEN) followed. No `.unwrap()` in new bindings. No `Cargo.lock` committed.

## Known Stubs

None — all seven boxplot dict fields are fully wired from fdars-core output.

## Self-Check: PASSED

- `src/depth_mod.rs`: FOUND
- `tests/test_depth.py`: FOUND
- commit 076e3e5: FOUND (RED)
- commit 75d45a7: FOUND (GREEN)
- All 27 tests pass; full suite green
