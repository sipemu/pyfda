---
phase: 35-docs-diagrams-worked-examples
plan: "03"
subsystem: documentation
tags: [docs, basis, smoothing, advisor, aic, constant_basis, inference]
status: complete
completed: "2026-08-18"

dependency_graph:
  requires: [35-01, 35-02]
  provides: [DOCS-06]
  affects: [docs/represent/basis-representation.md, docs/learn/smoothing.md, docs/advisor/aspects.md]

tech_stack:
  added: []
  patterns:
    - executed offline fence with FDARS_FENCE_OK sentinel (established pattern, applied consistently)
    - diagnostics-only advisor aspect (build_diagnostics with method="inference", no API key)

key_files:
  modified:
    - docs/represent/basis-representation.md
    - docs/learn/smoothing.md
    - docs/advisor/aspects.md

decisions:
  - constant_basis subsection placed between "When to use basis representations" lead-in and "Evaluating basis matrices directly" section (natural neighbour for raw basis-matrix content)
  - AIC selection subsection placed inside the existing "Basis Expansion" section just before "Penalized Basis", where basis_nbasis_cv with criterion="gcv" is already documented
  - All three AIC entry points documented together in a single subsection (smooth_basis_aic, optim_bandwidth(criterion="aic"), basis_nbasis_cv(criterion="aic")) with one fence covering all three
  - inference aspect fence uses a synthetic TestResult dict (no real fdars.inference call) — preserves grounding invariant, matching fpca/depth/scoring offline precedent
  - n_perm==0 asymptotic-path note included in the inference section per STATE.md accumulated context

metrics:
  duration: 39m
  completed: "2026-08-18"
  tasks_completed: 2
  tasks_total: 2

actuals:
  tokens: 9500
  tasks: 2
  commits: 2
---

# Phase 35 Plan 03: Basis/Smoothing Quick Wins + Advisor Inference Aspect Summary

Folded the v5.0 basis/smoothing bindings (constant_basis, smooth_basis_aic, AIC variants of optim_bandwidth and basis_nbasis_cv) into the existing docs pages, and extended the advisor coverage page with the new 14th inference aspect — all with executed offline fences emitting FDARS_FENCE_OK, strict build green.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Document constant_basis (represent) + AIC selection (smoothing) | c2350f0 | docs/represent/basis-representation.md, docs/learn/smoothing.md |
| 2 | Update advisor aspects.md for the new inference aspect (14 aspects) | d545e45 | docs/advisor/aspects.md |

## What Was Built

### Task 1: constant_basis + AIC selection documentation

**docs/represent/basis-representation.md** — new "## Constant basis" subsection added before "Evaluating basis matrices directly". Documents:
- What the constant basis is ($\phi_1(t) = 1$, intercept column of a regression design matrix)
- Signature: `constant_basis(argvals)` returning a 1-D all-ones float64 array
- Typical use cases (intercept term, mean-correction reference, sanity check)
- Executed offline fence: `constant_basis` on a 50-point grid, prints shape and `np.all(phi == 1.0) FDARS_FENCE_OK`
- Note explaining why `fdata_to_basis_1d(n_basis=1)` does NOT give the constant basis
- Added `constant_basis(argvals)` row to the API summary table

**docs/learn/smoothing.md** — new "### AIC-based selection" subsection added inside the "Basis Expansion" section. Documents:
- AIC formula and how it differs from GCV (explicit EDF penalisation)
- All three AIC entry points with code snippets:
  - `smooth_basis_aic(data, argvals, n_basis, ...)` — AIC-optimal P-spline penalty
  - `optim_bandwidth(criterion="aic", ...)` — AIC-optimal kernel bandwidth
  - `basis_nbasis_cv(criterion="aic", ...)` — AIC-optimal basis count
- Executed offline fence: synthetic 30-point, 12-curve dataset; runs all three AIC paths; prints results; appends `FDARS_FENCE_OK`
- GCV vs AIC tip box explaining when each is preferable
- Added "AIC-optimal smoothing" row to the method summary table

### Task 2: advisor aspects.md inference aspect

**docs/advisor/aspects.md** — two additions:
- **Coverage Table row**: `inference` row added (14th aspect); fdars source column notes diagnostics-only over caller-supplied TestResult / ToleranceBand dict; offline fence column links to [this page](#inference)
- **"## inference" section**: full per-aspect documentation following the fpca/depth/scoring pattern:
  - Description: diagnostics-only, caller supplies dict from fdars.inference functions, grounding invariant preserved
  - Input shapes: TestResult (statistic, p_value, n_perm) and ToleranceBand (lower, upper, center, half_width)
  - Key detail: `n_perm == 0` is legitimate (asymptotic path, e.g. Hotelling T²), not a missing value
  - Full diagnostics key table: 9 keys (method, statistic, p_value, n_perm, significant_at_0.01/0.05/0.10, strongest_significance_level, is_permutation_test, band_present, half_width)
  - Task families: interpretation / parameter / method
  - Executed offline fence: synthetic TestResult dict, `build_diagnostics(method="inference")`, prints 5 diagnostics + `FDARS_FENCE_OK`

## Verification Results

- `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build --strict` exited 0 (1215 s build time)
- `BASIS_FENCE_OK` — FDARS_FENCE_OK present in site/represent/basis-representation/index.html
- `CONSTANT_OK` — constant_basis referenced in site/represent/basis-representation/index.html
- `SMOOTH_FENCE_OK` — FDARS_FENCE_OK present in site/learn/smoothing/index.html
- `AIC_OK` — smooth_basis_aic referenced in site/learn/smoothing/index.html
- `INFERENCE_ASPECT_OK` — inference referenced in site/advisor/aspects/index.html
- `COVERAGE_14_OK` — aspects.md has ≥14 coverage-table pipe rows

## Deviations from Plan

None — plan executed exactly as written. All three AIC entry points documented together in one subsection (clean cohesive section), matching the plan's intent of covering all three in one fence. Constant basis note about `fdata_to_basis_1d(n_basis=1)` distinction added (Rule 2 — auto-add missing critical clarity; not an API change).

## Known Stubs

None. All executed fences run real fdars compute and emit FDARS_FENCE_OK. The inference fence uses a synthetic dict (not a real inference call) which is by design (grounding invariant, offline build) and documented as such.

## Threat Surface Scan

No new threat surface introduced. The three new executed fences use:
- Tiny synthetic data (30 grid points, 12 observations max) — DoS risk negligible (T-35-06 mitigated)
- Synthetic TestResult dict for the inference fence — no API key, no live inference compute (T-35-07 accepted)

## Self-Check: PASSED

- [x] docs/represent/basis-representation.md modified — confirmed via git log
- [x] docs/learn/smoothing.md modified — confirmed via git log
- [x] docs/advisor/aspects.md modified — confirmed via git log
- [x] Task 1 commit c2350f0 exists: `git log --oneline | grep c2350f0` ✓
- [x] Task 2 commit d545e45 exists: `git log --oneline | grep d545e45` ✓
- [x] All 6 verification tokens printed (BASIS_FENCE_OK, CONSTANT_OK, SMOOTH_FENCE_OK, AIC_OK, INFERENCE_ASPECT_OK, COVERAGE_14_OK)
- [x] Strict build exit=0
