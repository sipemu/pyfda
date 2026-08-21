---
phase: 39-group-c-depth-outliers-interval-inference-bindings
plan: "01"
subsystem: depth
tags: [rust, pyo3, depth, bindings, dispatcher]
status: complete

dependency_graph:
  requires: []
  provides: [DEPTH-03]
  affects: [src/depth_mod.rs, tests/test_depth.py]

tech_stack:
  added: []
  patterns:
    - "parameter-free DepthMethod enum arms added to existing string dispatcher"
    - "wildcard error message rewritten to list all 13 supported tokens"

key_files:
  created: []
  modified:
    - src/depth_mod.rs
    - tests/test_depth.py

decisions:
  - "Added 9 new arms immediately after random_projection in depth_method_from_str, keeping the existing order (original 4 + total_variation from tracer + 8 remaining)"
  - "Wildcard error message uses a single multi-line format! string listing all 13 tokens verbatim; rustfmt wraps cleanly with no line-length violations"
  - "Test fixture uses np.random.default_rng(0).standard_normal((10, 20)) — n=10 satisfies every min-n guard (max is 3 for extremal/total_variation); avoids loading the Canadian Weather dataset for speed"
  - "Boxplot coverage uses a representative 3-token subset (total_variation, hypograph_index, extremal) rather than all 9 to keep test time low while proving the shared dispatcher path"

metrics:
  duration_minutes: 5
  completed: "2026-08-21"
  tasks_completed: 2
  tasks_total: 2
  commits: 2

actuals:
  tokens: 8500
  tasks: 2
  commits: 2
---

# Phase 39 Plan 01: Group C DEPTH Bindings — 13-Variant Dispatcher Summary

Extended `depth_method_from_str` in `src/depth_mod.rs` with 9 new parameter-free `DepthMethod` variants from fdars-core 0.23.0, bringing the total to 13 supported depth methods accessible via `fdars.depth.functional_depth(method=...)` and `fdars.depth.functional_boxplot(method=...)` — DEPTH-03 complete.

## What Was Built

### src/depth_mod.rs — depth_method_from_str extended

Added 9 new parameter-free match arms after the `"random_projection"` arm:

| Python token | Rust variant | min-n |
|---|---|---|
| `"total_variation"` | `DepthMethod::TotalVariation` | 3 |
| `"hypograph_index"` | `DepthMethod::HypographIndex` | 2 |
| `"modified_hypograph_index"` | `DepthMethod::ModifiedHypographIndex` | 1 |
| `"epigraph_index"` | `DepthMethod::EpigraphIndex` | 2 |
| `"half_region"` | `DepthMethod::HalfRegion` | 2 |
| `"modified_half_region"` | `DepthMethod::ModifiedHalfRegion` | 2 |
| `"extremal"` | `DepthMethod::Extremal` | 3 |
| `"extreme_rank_length"` | `DepthMethod::ExtremeRankLength` | 2 |
| `"l_infinity"` | `DepthMethod::LInfinity` | 1 |

Wildcard error message rewritten to list all 13 supported tokens. Docstrings for `functional_depth` and `functional_boxplot` updated to enumerate all 13 method strings. No signature change. No `.unwrap()` or `.expect()` added. All fallible paths route through existing `to_pyresult()`.

### tests/test_depth.py — new test classes

- `TestFunctionalDepthNewVariants`: tracer test `test_total_variation_dispatch` (Task 1) + parametrized `test_new_variant_finite` covering all 9 new tokens (Task 2)
- `TestFunctionalBoxplotNewMethods`: `test_boxplot_accepts_new_methods` parametrized over `total_variation`, `hypograph_index`, `extremal` — proves shared dispatcher path
- Extended `TestFunctionalDepthValueErrors.test_unknown_method_lists_new_tokens`: asserts error message matches `"total_variation"` proving wildcard was rewritten
- Extended `TestFunctionalBoxplotValueErrors.test_unknown_method_boxplot_lists_new_tokens`: same for boxplot path

## Verification Results

- `maturin develop` — green (both tasks)
- `pytest tests/test_depth.py -q` — 44 passed, 0 failed
- `pytest tests/ -q` (full suite) — 658 passed, 4 skipped, 0 failed
- `cargo fmt --check` — clean
- `cargo clippy -- -D warnings` — clean
- No `.unwrap()` or `.expect()` introduced (confirmed via diff)

## Deviations from Plan

None — plan executed exactly as written. The 9 variant tokens and Rust enum variant names matched the HIGH-confidence research verbatim. The tracer (Task 1 — `total_variation`) compiled and dispatched on the first build attempt.

## Self-Check

- [x] `src/depth_mod.rs` modified with 9 new arms + rewritten wildcard + updated docstrings
- [x] `tests/test_depth.py` updated with `TestFunctionalDepthNewVariants`, `TestFunctionalBoxplotNewMethods`, and extended invalid-method tests
- [x] Task 1 commit: f4586ec
- [x] Task 2 commit: ce295db
- [x] Full pytest suite 658 passed, 0 failed
- [x] cargo fmt/clippy clean

## Self-Check: PASSED
