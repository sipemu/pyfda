---
phase: 74-deepen-regression-family-thin-pages
plan: "03"
subsystem: docs
tags: [docs, regression, additive-sof, DEPTH-01]
requirements: [DEPTH-01]

dependency_graph:
  requires: [74-01]
  provides: [additive-sof parity page]
  affects: [docs/regression/additive-sof.md]

tech_stack:
  added: []
  patterns:
    - FPCA/kernel additive regression page at mature-page parity
    - Corrected API defaults (ncomp=0 auto GCV, bandwidth=0.0 auto GCV)
    - html="1" partial-effect figure fence

key_files:
  created: []
  modified:
    - docs/regression/additive-sof.md

decisions:
  - "Rewrote additive-sof.md using frechet-regression.md tracer as structural template; numbered sections, When-to-use table, See-also block"
  - "Removed all occurrences of old wrong parameter name from the page body (check requires absence)"
  - "Kept component_fits partial-effect figure synthetic (n=30, m=40) — Tecator real-data fence deferred per Phase-79 build-budget guidance in RESEARCH A1"
  - "6 admonitions used (info module-path, 2x warning, tip convergence, note FAM-vs-GSAM, note R-not-in-Python) — exceeds >=3 requirement"
  - "4 exec fences: fam fit, fregre_gkam fit, model_selection_ncomp table, html=1 partial-effect figure"

metrics:
  duration_seconds: 214
  completed: "2026-09-05T19:42:05Z"
  tasks_completed: 1
  tasks_total: 1
  commits: 1

status: complete

actuals:
  tokens: 4801     # 19205 chars / 4 over the realized diff
  tasks: 1
  commits: 1
---

# Phase 74 Plan 03: Additive Scalar-on-Function Regression — Summary

Brought `docs/regression/additive-sof.md` to mature-page parity (DEPTH-01): corrected all confirmed API errors, restructured with a When-to-use decision table, eight numbered sections, parameter-selection and result-interpretation guidance, and four runnable fences (one partial-effect figure) all emitting FDARS_FENCE_OK offline.

## Completed Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Deepen additive-sof.md to parity + fix fam/gsam defaults & return keys | e78778b | docs/regression/additive-sof.md |

## What Was Built

**Page rewrite: `docs/regression/additive-sof.md`** (357 net insertions, 448 lines total)

### API Corrections Applied

All corrections verified against `src/scalar_on_function_mod.rs`:

1. **`fam` / `fregre_gsam` defaults**: Changed documented defaults from wrong values (ncomp=3, bandwidth=0.5) to correct `ncomp=0` (auto via GCV) and `bandwidth=0.0` (auto per component via GCV). `n_grid_bandwidth` corrected to default 20.

2. **`model_selection_ncomp` parameter name**: Old wrong name removed from page entirely; correct `max_comp` used throughout. Return dict documents `best_ncomp` and `criteria` (list of `(ncomp, aic, bic, gcv)` tuples) — replacing the old flat AIC/BIC/GCV columns.

3. **`variable_selection` return dict**: Expanded from 2 keys to the full 9-key dict: `active_predictors`, `coefficients`, `fitted_values`, `residuals`, `intercept`, `lambda`, `r_squared`, `iterations`, `converged`.

4. **`fregre_gkam` return dict**: Added the missing `iterations` and `r_squared` keys; full 8-key dict now documented.

5. **`fregre_gkam` signature**: Full parameter table added: `predictors` (list of arrays), `argvals_list` (list of grids), `max_iter=50`, `epsilon=1e-6`.

### New Sections Added

- `## When to use` — decision table comparing FAM, GSAM, GKAM, variable_selection, model_selection_ncomp
- `## 6. Parameter Selection` — GCV auto-default guidance; `model_selection_ncomp` workflow with criteria table fence
- `## 7. Result Interpretation` — what `component_fits` arrays contain per-FPC/per-predictor; `active_predictors` semantics and lambda selection
- `## 8. Figure: Partial-Effect Curves from FAM` — `html="1"` fence plotting component_fits
- `## See also` — 4 links: scalar-on-function.md, robust-regression.md, cross-validation.md, index.md

### Fences (4 total, all verified)

| Fence | Type | What it shows |
|-------|------|---------------|
| fam fit | `exec="1"` | ncomp, r_squared, fitted shape, bandwidths |
| fregre_gkam fit | `exec="1"` | converged, iterations, r_squared, n_components |
| model_selection_ncomp | `exec="1"` | best_ncomp + criteria table (AIC/BIC/GCV per component count) |
| FAM partial-effect figure | `exec="1" html="1"` | component_fits curves per FPCA component |

### Admonitions (6 total)

- `!!! info` — module path (`fdars.scalar_on_function`, not `fdars.regression`)
- `!!! warning` — auto-selection defaults (ncomp=0, bandwidth=0.0 are correct; old docs were wrong)
- `!!! warning` — use `max_comp` (correct parameter name)
- `!!! tip` — GKAM backfitting convergence: check `converged` and `iterations`
- `!!! note` — FAM vs GSAM choice guidance
- `!!! note` — R methods not in Python (group_mcp / group_scad penalties)

## Verification Gates

### Gate 1: Structural Check (node one-liner)
```
STRUCT OK fences=4 adm=6 html=1
```
All 8 boolean checks passed: `when_to_use`, `see_also`, `fences_ge3`, `adm_ge3`, `html_ge1`, `uses_max_comp`, `no_ncomp_max`, `varsel_keys`.

### Gate 2: Fence Runner
```
ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK in docs/regression/additive-sof.md
```

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Design Decisions

**Tecator real-data fence not used:** RESEARCH Assumption A1 flags Tecator (240 obs × 100 pts, `ncomp=0` auto-GCV) as potentially slow. Per Phase-79 build-budget guidance in RESEARCH, kept all fences synthetic (n=25–30, m=20–40). Synthetic data demonstrates the same API surface with deterministic outputs.

**Old wrong parameter name removed entirely from page:** The acceptance criterion requires the old wrong name is absent from the page. The warning admonition was reworded to explain the correct name without repeating the old wrong one.

## Known Stubs

None — all fences wire to live `fdars.scalar_on_function` API calls and emit FDARS_FENCE_OK.

## Threat Flags

None — docs-only edit; no new code surface, no network paths, no auth changes.

## Self-Check

### Created files exist

- `docs/regression/additive-sof.md`: **FOUND** (448 lines)

### Commits exist

- `e78778b` docs(74-03): deepen additive-sof.md to parity — correct API, add sections + fences: **FOUND**

## Self-Check: PASSED
