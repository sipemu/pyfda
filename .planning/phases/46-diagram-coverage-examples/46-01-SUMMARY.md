---
phase: 46-diagram-coverage-examples
plan: "01"
subsystem: docs/examples
tags: [diagrams, svg, examples, diacov-01, canadian-weather, andrews-wine]
status: complete

requires: []
provides:
  - ex-canadian-weather.svg
  - ex-canadian-depth-centrality.svg
  - ex-canadian-function-on-scalar.svg
  - ex-canadian-precipitation.svg
  - ex-canadian-seasonal.svg
  - ex-andrews-wine.svg
  - ex-andrews-wine-intro.svg
  - ex-andrews-wine-clustering.svg
  - ex-andrews-wine-qc.svg
affects:
  - docs/examples/canadian-weather.md
  - docs/examples/canadian-depth-centrality.md
  - docs/examples/canadian-function-on-scalar.md
  - docs/examples/canadian-precipitation.md
  - docs/examples/canadian-seasonal.md
  - docs/examples/andrews-wine.md
  - docs/examples/andrews-wine-intro.md
  - docs/examples/andrews-wine-clustering.md
  - docs/examples/andrews-wine-qc.md

tech-stack:
  added: []
  patterns:
    - hand-authored inline SVG (720-wide viewBox, STYLE_SPEC canonical style block)
    - workflow/pipeline genre per ex-sonar-tsrvf.svg precedent
    - .fdars-diagram embed near page top before first ## heading
    - svgo@3.3.4 idempotence gate + rsvg-convert PNG render check

key-files:
  created:
    - docs/assets/diagrams/ex-canadian-weather.svg
    - docs/assets/diagrams/ex-canadian-depth-centrality.svg
    - docs/assets/diagrams/ex-canadian-function-on-scalar.svg
    - docs/assets/diagrams/ex-canadian-precipitation.svg
    - docs/assets/diagrams/ex-canadian-seasonal.svg
    - docs/assets/diagrams/ex-andrews-wine.svg
    - docs/assets/diagrams/ex-andrews-wine-intro.svg
    - docs/assets/diagrams/ex-andrews-wine-clustering.svg
    - docs/assets/diagrams/ex-andrews-wine-qc.svg
  modified:
    - docs/examples/canadian-weather.md (+2 lines: embed)
    - docs/examples/canadian-depth-centrality.md (+2 lines: embed)
    - docs/examples/canadian-function-on-scalar.md (+2 lines: embed)
    - docs/examples/canadian-precipitation.md (+2 lines: embed)
    - docs/examples/canadian-seasonal.md (+2 lines: embed)
    - docs/examples/andrews-wine.md (+2 lines: embed)
    - docs/examples/andrews-wine-intro.md (+2 lines: embed)
    - docs/examples/andrews-wine-clustering.md (+2 lines: embed)
    - docs/examples/andrews-wine-qc.md (+2 lines: embed)

decisions:
  - "Tracer-first: authored ex-canadian-weather.svg end-to-end first to prove the create→embed→svgo→PNG pipeline before scaling"
  - "Height 480 for multi-row workflows (canadian-weather, canadian-seasonal, andrews-wine, andrews-wine-clustering, andrews-wine-qc); 300 for single-row (depth-centrality, function-on-scalar, precipitation, andrews-wine-intro)"
  - "Embed position: after the intro paragraph, before the first !! warning or ## heading — consistent with sonar-tsrvf.md line ~22 pattern"
  - "andrews-wine pages: embed before !!! warning admonition (which is itself before the first ## heading)"

metrics:
  duration: "~9 minutes"
  completed: "2026-08-22"
  tasks: 3
  commits: 3
  files: 18

estimate:
  tokens: 95000

actuals:
  tokens: 87000
  tasks: 3
  commits: 3
---

# Phase 46 Plan 01: Diagram Coverage — Examples (Canadian + Andrews) Summary

**One-liner:** 9 method-accurate workflow SVGs authored for the canadian-weather tracer + 4 canadian + 4 andrews-wine example pages, all STYLE_SPEC-conformant, svgo-idempotent, and embedded via `.fdars-diagram`.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (tracer) | author + embed ex-canadian-weather.svg | 3d29e2d | ex-canadian-weather.svg, canadian-weather.md |
| 2 | 4 canadian-family workflow SVGs | 181d9db | 4 SVGs + 4 .md pages |
| 3 | 4 andrews-wine-family workflow SVGs | 27647c3 | 4 SVGs + 4 .md pages |

## New SVG Files and Their Depicted Method Arcs

### Task 1 (Tracer)

**`ex-canadian-weather.svg`** (720×480)
Method arc: `load_canadian_weather` → `fanova` (permutation F-test, F≈22.5, p=0.002, 4 regions) + pairwise `fanova` → `fosr`/`fosr_fpc` (β_lat(t), β_lon(t), R²=0.47→0.81) → `predict_fosr` (3 hypothetical stations) → `fclassif_cv`/`fclassif_lda` (86% CV accuracy on temperature curves).
Two main analytical branches: fanova (does regional structure exist?) and fosr (which geography drives it?), converging on a classification close.

### Task 2 (Canadian Family)

**`ex-canadian-depth-centrality.svg`** (720×300)
Method arc: `Fdata(temp, argvals=t)` → `.depth(method="fraiman_muniz")` → depth-shaded curve plot (pale = peripheral, dark = central) → deepest = functional median (mid-continental station) → `.depth(method="modified_band")` comparison (correlation FM vs MBD ≈ 0.99, confirming ordering is a data property).

**`ex-canadian-function-on-scalar.svg`** (720×300)
Method arc: scalar predictors [lat z-scored] → design matrix [1, latz] → `fosr(temp, design, λ_=0.01)` → β_lat(t) coefficient curve (negative all year, deepest in January at −7°C/SD, flattens in summer) → `predict_fosr(new_locs)` → two predicted annual temperature curves (southern warm / northern cold; diverge in winter, converge in summer).

**`ex-canadian-precipitation.svg`** (720×300)
Method arc: `load_canadian_weather("precipitation")` → `log1p` transform → `pspline_fit_1d(X, day, n_basis=40, λ_=10.0)` (P-spline smoothing, removes daily noise) → smoothed Xs → two parallel branches: `fosr(Xs, [lat,lon])` (β_lat seasonal sign flip, β_lon west-east gradient) + `fanova(Xs, region_codes)` (significant regional differences p≈0.001, Pacific wet-winter most distinctive) → `predict_fosr` hypothetical station.

**`ex-canadian-seasonal.svg`** (720×480)
Method arc: 8-year Edmonton series (base annual cycle × 8 years with +0.3°C/yr trend + 3%/yr amplitude + noise) → four period detectors [`estimate_period_fft`, `autoperiod`, `cfd_autoperiod`, `sazed`] all returning 365 days + `lomb_scargle_fdata` periodogram (dominant 365-day spike) → `stl_decompose(fd, 365)` (trend/seasonal/remainder; trend recovers +0.3°C/yr) + `ssa_fdata(fd, window=730)` (components 1–2 near-tied pair = periodic fingerprint, ~89% variance) → `seasonal_strength` + `classify_seasonality` (strength≈0.97, classified StableSeasonal, stable timing) → `detect_peaks` + `analyze_peak_timing` (peak day stable ~214 across all stations/years).

### Task 3 (Andrews-Wine Family)

**`ex-andrews-wine.svg`** (720×480)
Method arc: 178 wine rows → z-score 13 columns → Andrews curves (178×160) → four parallel detectors: [1] `depth.modified_band_1d` (centrality ranking, shallow tail = candidates, no yes/no), [2] `outliers.magnitude_shape` (magnitude vs shape axes, top 6 flagged, mostly magnitude), [3] `outliers.outliergram` (MBD vs MEI parabolic band, **flags wines 69 + 95 Grignolino**), [4] `outliers.detect_outliers_lrt` (bootstrap threshold, **0 flagged** at α=0.05) → cross-check vs Mahalanobis distance (agrees on magnitude outliers, misses shape axis).
Three detectors (depth + MS + outliergram) agree on same handful: wines 69 + 95 (extreme magnesium, shape anomaly); LRT strictest, declines to flag.

**`ex-andrews-wine-intro.svg`** (720×300)
Method arc: 13-D wine row → per-column z-score → Andrews formula f_x(t) = x₁/√2 + x₂sin(t) + x₃cos(t) + … (numpy, no fdars binding) → fdars tools on curves: `metric.lp_self_1d` (Parseval: ||f_x − f_y||_L2 = √π·||x−y||_2, verified on 15,753 pairs) + `fdata.mean_1d` (cultivar mean curve) + `depth.modified_band_1d` (functional boxplot per cultivar: Barolo tight, Grignolino widest) → full fdars toolbox enabled.

**`ex-andrews-wine-clustering.svg`** (720×480)
Method arc: 178 Andrews curves → `kmeans_fd(curves, t, k=3)` (centroid curves, accuracy≈0.95 vs true cultivars) → cluster validity: `silhouette_score_data` + `calinski_harabasz_data` (k=2,3,4,5; both peak near k=3) → `fuzzy_cmeans_fd` (soft membership, flags boundary wines with max_membership < 0.6) → `fanova(curves, cultivar)` (permutation p≈0, F(t) curve shows where separation is largest) → `fpca(curves, t, n_comp=5)` (PC1≈45%/PC2≈24%; ANOVA F per feature: flavanoids, proline, od280 dominate; FPCA score plot: 3 tight clouds).

**`ex-andrews-wine-qc.svg`** (720×480)
Method arc: Barolo reference (59 in-control wines, cultivar 1) → `modified_band_1d` → functional boxplot (median, central 50% band, 1.5× fences) → per-cultivar boxplot specs → `fpca_tolerance_band(ref, ncomp=3, nb=800, coverage=0.95)` (Barbera wines: nearly all breach Barolo band) → Phase I: `spm_phase1(ref, t, ncomp=3, α=0.05)` (calibrate model + T² and SPE control limits) → Phase II: `spm_monitor` (Grignolino + Barbera: ~100% alarmed; SPE most decisive — wrong grape varies in new directions) → diagnostics: `spm.t2_pc_contributions` + within-cultivar z-scores → named culprit chemicals (e.g., flavanoids + colour intensity for Barbera).

## Judgment Calls for Phase 49 Human Diagram Review

The following diagrams involved interpretation choices that the Phase 49 blocking human diagram review should verify:

1. **`ex-canadian-weather.svg`** — The page runs both temperature AND precipitation through fanova/fosr in separate sections. The diagram shows temperature as the primary arc and mentions precipitation in the bottom note as a repeat. This is correct but the planner should confirm the diagram does not need a side-by-side two-variable structure (the page is about temperature primarily).

2. **`ex-canadian-seasonal.svg`** — The page is very rich (8 different seasonal functions). The diagram shows the arc as: period detectors → Lomb-Scargle → STL/SSA → seasonal strength. It does NOT depict `detect_peaks` (35-station geographic peak timing) and `analyze_peak_timing` (multi-year peak trend), which are secondary analyses. These are mentioned only in the bottom note. Reviewer should confirm whether these sections are prominent enough to warrant inclusion in the main diagram panels.

3. **`ex-andrews-wine-clustering.svg`** — The page also includes bootstrap confidence bands on cultivar means (pure numpy, no fdars) and an FPCA score plot. The diagram includes fpca but not the bootstrap section (which is a pure-numpy analysis). This omission is consistent with the "actual fdars methods" constraint — the bootstrap is numpy, not fdars — but the reviewer should confirm.

4. **`ex-andrews-wine-qc.svg`** — The QC page includes a "robust trimmed mean" section (depth-based trimmed mean vs ordinary mean). This is computed via `modified_band_1d` (an fdars method). The diagram omits this step to keep the main flow to 4 clear panels (boxplot → tolerance band → SPM Phase I → SPM Phase II + diagnostics). The trimmed-mean robustness demonstration is a separate proof-of-concept section, not part of the monitoring workflow. Reviewer should confirm the omission is appropriate.

## Deviations from Plan

None — plan executed exactly as written. All 3 tasks (tracer + 2 batches) completed, all 9 diagrams pass the check-ex.sh gate, all 9 pages embed correctly.

## Self-Check

### Created files exist:
- [x] docs/assets/diagrams/ex-canadian-weather.svg
- [x] docs/assets/diagrams/ex-canadian-depth-centrality.svg
- [x] docs/assets/diagrams/ex-canadian-function-on-scalar.svg
- [x] docs/assets/diagrams/ex-canadian-precipitation.svg
- [x] docs/assets/diagrams/ex-canadian-seasonal.svg
- [x] docs/assets/diagrams/ex-andrews-wine.svg
- [x] docs/assets/diagrams/ex-andrews-wine-intro.svg
- [x] docs/assets/diagrams/ex-andrews-wine-clustering.svg
- [x] docs/assets/diagrams/ex-andrews-wine-qc.svg

### Commits exist:
- [x] 3d29e2d (Task 1 tracer)
- [x] 181d9db (Task 2 canadian family)
- [x] 27647c3 (Task 3 andrews-wine family)

### No-regression guard: PASSED (all 3 batches)

### svgo@3.3.4 idempotence gate: PASSED (all 9 diagrams)

### rsvg-convert PNG non-empty: PASSED (all 9 diagrams)

## Self-Check: PASSED
