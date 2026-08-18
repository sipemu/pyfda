---
phase: 31-group-a-fdars-inference-bindings
plan: "03"
subsystem: inference
tags: [rust, pyo3, fdars-core, inference, flm, anova, tdd]
status: complete

dependency_graph:
  requires: [31-01, 31-02]
  provides: [INFER-06, INFER-07, INFER-08]
  affects: [fdars.inference, tests/test_inference.py]

tech_stack:
  added: []
  patterns:
    - "FLM re-fit pattern: fregre_lm internally, FregreLmResult stays in Rust, same as predict_fregre_lm"
    - "oneway_anova_vstat: PyReadonlyArray1<i64> → numpy1d_to_usize_vec → Vec<usize>"

key_files:
  created: []
  modified:
    - src/inference_mod.rs
    - tests/test_inference.py

decisions:
  - "flm_f_test/flm_gof_test default n_comp=5 (plan spec); consistent with SIGNATURES.md summary"
  - "Degenerate-input tests use n<3 rows (fregre_lm InvalidDimension) for flm_f_test and n=4 rows (GoF degenerate df) for flm_gof_test — core clamps n_comp rather than erroring on oversized ncomp"

metrics:
  duration_minutes: 35
  completed_date: "2026-08-17"
  tasks_completed: 3
  commits: 2

estimate:
  tokens: 55000

actuals:
  tokens: 14000
  tasks: 3
  commits: 2
---

# Phase 31 Plan 03: FLM Inference + One-Way ANOVA V-Statistic Summary

One-liner: Three FLM/ANOVA inference bindings completing the `fdars.inference` surface — `flm_f_test` and `flm_gof_test` re-fit `fregre_lm` internally (FregreLmResult never crosses the boundary), `oneway_anova_vstat` accepts a 0-indexed i64 group array (asymptotic V-statistic, n_perm==0).

## What Was Built

Three new `#[pyfunction]` bindings added to `src/inference_mod.rs` and registered, completing the 8-function `fdars.inference` Group A surface:

**`flm_f_test(data, response, n_comp=5)`** — Overall-significance F-test for a scalar-on-function linear regression. Re-fits `fregre_lm` internally via `fdars_core::scalar_on_function::fregre_lm(&mat, &resp, None, n_comp)`, passes `&FregreLmResult` to `fdars_core::inference::flm_f_test`, returns `{statistic, p_value, n_perm}` with `n_perm==0`. `FregreLmResult` never crosses the Python boundary.

**`flm_gof_test(data, response, n_comp=5)`** — Ramsey-RESET goodness-of-fit test; bound symmetrically with `flm_f_test` (same signature, same re-fit path). A small p-value indicates the linear model misses a nonlinear effect.

**`oneway_anova_vstat(data, groups, argvals)`** — Asymptotic one-way functional ANOVA V-statistic (Satterthwaite scaled-χ²). Accepts `groups` as `PyReadonlyArray1<i64>` converted via `numpy1d_to_usize_vec`; 0-indexed labels documented. Returns `{statistic, p_value, n_perm}` with `n_perm==0`. Validation (len mismatch, < 2 distinct groups, n < 3) forwarded from fdars-core via `to_pyresult`.

## TDD Gate Compliance

| Gate | Commit |
|------|--------|
| RED (test) | `35c4e2d` — failing tests for all 3 functions |
| GREEN (feat) | `98300a1` — implementation + test fixes |

## Test Results

- Full suite: 491 passed, 4 skipped (same 4 skipped as baseline — no regressions)
- `tests/test_inference.py` — 65 tests pass (was 46; 19 new tests added)
- `cargo clippy --all-targets -- -D warnings` — clean
- `cargo fmt --check` — clean

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Degenerate-fit test strategy corrected**

- **Found during:** GREEN phase (Task 1 implementation)
- **Issue:** Plan specified "n_comp >= n raises ValueError" but `fdars_core::scalar_on_function::fregre_lm` clamps `n_comp` to available data rather than erroring. The degenerate-fit error is actually triggered by insufficient rows (n < 3 for fregre_lm, n <= 4 for flm_gof_test's auxiliary df check).
- **Fix:** Changed `test_degenerate_n_comp_raises_value_error` to `test_degenerate_input_raises_value_error` using `n < 3` rows (n=2) for `flm_f_test` and `n = 4` rows for `flm_gof_test`. Core behavior is authoritative; tests corrected to match.
- **Files modified:** `tests/test_inference.py`
- **Commit:** `98300a1`

## Known Stubs

None — all three functions are fully wired to fdars-core 0.20.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. The STRIDE mitigations from the threat model are implemented:

- **T-31-07** (degenerate FLM/ANOVA inputs): routed through `to_pyresult()` — no `.unwrap()`; ValueError tests pass
- **T-31-08** (float group labels silently truncated): `PyReadonlyArray1<i64>` binding rejects float arrays; `numpy1d_to_usize_vec` preserves semantics
- **T-31-09** (FregreLmResult as Python handle): re-fit internally per locked decision; `FregreLmResult` never crosses the boundary

## Self-Check: PASSED

- `src/inference_mod.rs` contains `flm_f_test`, `flm_gof_test`, `oneway_anova_vstat` and registers all three
- `tests/test_inference.py` has `TestFlmFTest`, `TestFlmGofTest`, `TestOnewayAnovaVstat` classes
- Commits 35c4e2d (RED) and 98300a1 (GREEN) exist in git log
- 491 passed / 4 skipped — full suite green
