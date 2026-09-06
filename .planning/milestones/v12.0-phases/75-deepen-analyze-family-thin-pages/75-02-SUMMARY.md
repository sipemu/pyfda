---
phase: 75-deepen-analyze-family-thin-pages
plan: "02"
subsystem: docs
tags: [density-fda, lqd-transform, analyze-family, parity, DEPTH-02]
status: complete
requirements: [DEPTH-02]

dependency_graph:
  requires: ["75-01"]
  provides: ["density-fda.md parity (DEPTH-02)"]
  affects: ["docs/analyze/density-fda.md"]

tech_stack:
  added: []
  patterns:
    - UNNUMBERED mature analyze page template
    - inverse_lqd 3-argument correction
    - quantile-grid output clarification
    - LQD round-trip proof fence
    - Wasserstein barycenter + LQD-FPCA barycenter/score combined fence
    - html figure fence (density overlay + score scatter, side-by-side)

key_files:
  modified:
    - docs/analyze/density-fda.md

decisions:
  - "inverse_lqd documented with 3-argument signature (psi, t_grid, target_argvals) — no 2-argument form"
  - "quantile-grid mismatch is the primary correctness hazard; addressed in warning admonition AND prose AND round-trip fence shape print"
  - "n_quantile_pts optional param added to both lqd_transform and lqd_fpca tables"
  - "html figure: side-by-side (density overlay + LQD-FPCA score scatter) shows both barycenter and decomposition in one panel"
  - "fve row reports cumulative variance — prose explains to argmax for ncomp selection"
  - "See also targets: frechet-regression.md, functional-statistics.md, outlier-detection.md, index.md"

metrics:
  duration_minutes: 2
  completed: "2026-09-05"
  tasks_completed: 1
  commits: 1

actuals:
  tokens: 11000
  tasks: 1
  commits: 1
---

# Phase 75 Plan 02: Density FDA — Summary

**One-liner:** density-fda.md restructured to UNNUMBERED analyze parity with 3-arg `inverse_lqd` corrected, quantile-grid output shape clarified in prose and admonition, `n_quantile_pts` documented, and 3 offline-verified FDARS_FENCE_OK fences including an html figure.

## What Was Built

`docs/analyze/density-fda.md` was expanded from a thin ~150-line API-only page (missing When-to-use, See-also, and a round-trip inverse_lqd example) to a full mature-page parity document:

- **Method-selector table** at the top: normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter, lqd_fpca with key output descriptions.
- **## When to use** decision section: when densities appear as data objects; contrast LQD-space analysis with naive L2-FPCA; explicit Fréchet-regression cross-reference for density responses.
- **Corrected API documentation** for all three priority discrepancies:
  1. `inverse_lqd(psi, t_grid, target_argvals)` — 3-argument form; the old 2-argument `inverse_lqd(lqd, argvals)` form has been removed.
  2. `lqd_transform` full signature with `n_quantile_pts=None` optional parameter.
  3. `lqd_fpca` full signature with `n_quantile_pts=None` optional parameter.
- **Quantile-grid clarification:** prose in the warning admonition, prose in the intro section, and the round-trip fence `psi.shape` print all confirm that LQD output is `(n_q,)` not `(m,)`.
- **5 admonitions** (exceeds the ≥3 requirement):
  - `!!! tip "Start with normalize_density"` (intro)
  - `!!! warning "LQD output lives on the quantile grid"` (after Core Concept)
  - `!!! note "inverse_lqd requires the explicit quantile grid"` (inverse_lqd section)
  - `!!! tip "Input rows must be valid unit densities"` (wasserstein_barycenter section)
  - `!!! warning "mean and loadings are on the quantile grid (n_q,), not (m,)"` (lqd_fpca section)
- **3 runnable FDARS_FENCE_OK fences:**
  1. Round-trip proof fence: normalize → lqd_transform → inverse_lqd, prints psi.shape proving n_q ≠ m.
  2. Barycenter + LQD-FPCA combined fence: full 12-density example, prints scores shape and fve.
  3. `html="1"` figure fence: side-by-side panel (density overlay + barycenter, LQD-FPCA score scatter).
- **Parameter selection and result interpretation** subsections: ncomp via fve argmax, reading LQD loadings as modes of density-shape variation, using scores downstream.
- **## See also** cross-references: frechet-regression.md, functional-statistics.md, outlier-detection.md, index.md.
- **References** preserved verbatim (Petersen & Müller 2016, van den Boogaart et al. 2014).

## Verification

Both gates passed:

1. **Structural gate (node one-liner):** `STRUCT OK fences=3 adm=5 html=1`
   - `## When to use` present ✓
   - `## See also` present ✓
   - ≥3 FDARS_FENCE_OK sentinels (3) ✓
   - ≥3 admonitions (5) ✓
   - ≥1 html figure fence (1) ✓
   - `inverse_lqd(psi, t_grid, target_argvals` pattern present ✓
   - No 2-argument `inverse_lqd(...)` calls survive ✓
   - `n_quantile_pts` present ✓
   - "quantile grid" phrase present ✓

2. **Fence gate:** `ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK in docs/analyze/density-fda.md`

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All three fences use self-contained synthetic data; no real dataset references or placeholder values.

## Threat Flags

None. Docs-only edit; no new network surface, authentication paths, or schema changes.

## Self-Check

- [x] `docs/analyze/density-fda.md` exists on disk (302 insertions committed)
- [x] Commit `42a233a` exists in git log
- [x] Both verify gates passed before commit

## Self-Check: PASSED
