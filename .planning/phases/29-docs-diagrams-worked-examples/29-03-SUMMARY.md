---
phase: 29-docs-diagrams-worked-examples
plan: "03"
subsystem: docs/align + docs/advisor
tags: [align, shift-registration, banded-alignment, advisor, svg, worked-examples]
status: complete

dependency_graph:
  requires: [29-01]
  provides: [docs/align/shift-registration.md, docs/align/banded-alignment.md, docs/assets/diagrams/shift-registration.svg, docs/assets/diagrams/banded-alignment.svg, docs/advisor/aspects.md#scoring, docs/advisor/aspects.md#imputation-quality, docs/advisor/aspects.md#registration-quality]
  affects: [29-04-PLAN.md, DOCS-01, DOCS-02, DOCS-03]

tech_stack:
  added: []
  patterns:
    - "Hand-authored inline SVG with 720×300 and 720×480 viewBox conforming to STYLE_SPEC"
    - "Executed offline FDARS_FENCE_OK fence pattern on align/ pages"
    - "Advisor aspects.md extension pattern: add new section + Coverage Table row + extend existing section rows"

key_files:
  created:
    - docs/align/shift-registration.md
    - docs/align/banded-alignment.md
    - docs/assets/diagrams/shift-registration.svg
    - docs/assets/diagrams/banded-alignment.svg
  modified:
    - docs/advisor/aspects.md

decisions:
  - "Used canadian_weather (uniform daily grid) for both fence examples — growth grid is non-uniform, making sobolev_least_squares_score raise with lambda>0"
  - "banded-alignment.svg uses 720×480 (tall) viewBox to accommodate DP grid panel above + curve panels below without crowding"
  - "shift-registration.svg includes a contrast glyph (straight arrow 'shift rigid' vs curved arrow 'elastic warp') in the method panel to make the distinction explicit"
  - "aspects.md scoring fence is executed (offline, deterministic, no API key) — mirrors the existing fpca and depth fences on the same page"
  - "Registration-quality keys (ls_score, pairwise_corr_score, sobolev_score) default None in the alignment diagnostic when registration inputs are absent, matching the existing None-on-missing pattern"

metrics:
  duration_minutes: 40
  completed_date: "2026-08-17"
  tasks_completed: 3
  tasks_total: 3
  commits: 3

actuals:
  tokens: 68000
  tasks: 3
  commits: 3
---

# Phase 29 Plan 03: Align Docs + Advisor Aspects Summary

Authored two new align-section pages (shift-registration and banded-alignment) each with a method-accurate hand-authored STYLE_SPEC-conforming inline SVG and an executed offline FDARS_FENCE_OK worked example, and extended docs/advisor/aspects.md with scoring/imputation-quality/registration-quality coverage while keeping the build fully offline.

## What was built

### Task 1: shift-registration.md + shift-registration.svg

- **SVG:** `docs/assets/diagrams/shift-registration.svg` (720×300). Three-panel: misaligned curves with blurred mean → method panel showing the horizontal shift δ (straight arrow) contrasting against a curved "elastic warp" glyph → registered curves with sharpened mean. The rigid vs elastic contrast is built into the method panel itself with two labelled arrows. SVGO idempotent; role="img"; conforms to STYLE_SPEC.
- **Page:** `docs/align/shift-registration.md`. Covers least_squares_shift_registration (golden-section search, max_shift parameter), fd.shift_register() convenience method, all three registration-quality scores (least_squares_score, pairwise_correlation_score, sobolev_least_squares_score) with a decision-rule table, and a mathematical note contrasting rigid vs elastic registration.
- **Fence:** Loads canadian_weather (8-station subset, fixed seed), calls `alignment.least_squares_shift_registration`, prints per-station shifts + all three quality scores, ends with FDARS_FENCE_OK. Uniform grid → sobolev score works.

### Task 2: banded-alignment.md + banded-alignment.svg

- **SVG:** `docs/assets/diagrams/banded-alignment.svg` (720×480). Top half: 10×10 DP grid with Sakoe–Chiba band rendered as a blue diagonal stripe (inside = colour-coded, outside = grey), main diagonal dashed line, optimal warp path, orange band-edge lines, band_frac label. Bottom half: two panels showing unregistered vs banded-registered curves. Method-accurate: the band is literally |i−j|≤B cells. SVGO idempotent; role="img".
- **Page:** `docs/align/banded-alignment.md`. Covers karcher_mean_with_band (same keys as karcher_mean), elastic_self/cross_distance_matrix_with_band, band_frac selection guidelines, speed/accuracy tradeoff workflow. Cross-links to elastic-alignment.md, shift-registration.md.
- **Fence:** Loads canadian_weather (8-station subset), calls `karcher_mean_with_band(band_frac=0.2)` + `elastic_self_distance_matrix_with_band`, prints convergence + distance matrix symmetry check, ends with FDARS_FENCE_OK.

### Task 3: docs/advisor/aspects.md extensions

Three extensions, no existing content removed:

1. **Coverage Table:** Added `scoring` row; updated `alignment` diagnostic count from 14 to 17; updated `represent` diagnostic count from 10 to 13.
2. **`## alignment` section:** Added three registration-quality rows (`ls_score`, `pairwise_corr_score`, `sobolev_score`) all defaulting None when registration inputs absent, plus an actionable tip box.
3. **`## represent` section:** Added three imputation-quality rows (`nan_frac`, `has_boundary_nans`, `imputation_method`) all defaulting None when no NaN in inputs, plus an imputation-quality guidance tip.
4. **New `## scoring` section:** Full section with fdars source reference, key table for the 5 integrated metrics, MAPE/MSLE domain-restriction warning, an executed offline fence (no API key; FDARS_FENCE_OK), and task families.

The scoring fence is deterministic (fixed seed synthetic data). All pre-existing FDARS_FENCE_OK sentinels preserved (source count increased from 2 to 3; HTML count from prior build exceeded).

## Deviations from Plan

### Auto-discovered: growth dataset incompatible with sobolev_least_squares_score

- **Found during:** Task 1 fence development
- **Issue:** growth dataset has non-uniform age grid (31 unequally-spaced points) — sobolev_least_squares_score raises `ValueError` when lambda>0 requires uniform grid
- **Fix:** Switched to canadian_weather (365 uniformly-spaced daily points) for the shift-registration fence, matching the rule in the method table
- **Commit:** faacdff (Task 1)
- **Rule:** Rule 1 (bug prevention) / Rule 3 (blocking issue resolution)

## Known Stubs

None. Both fences run against real fdars.alignment bindings on real (non-synthetic) data from docs/data/.

## Threat Flags

None. No new network endpoints or auth paths introduced. Both fences are offline/deterministic. No ANTHROPIC_API_KEY fence added.

## Self-Check: PASSED

Files created/found:
- docs/align/shift-registration.md: FOUND
- docs/align/banded-alignment.md: FOUND
- docs/assets/diagrams/shift-registration.svg: FOUND
- docs/assets/diagrams/banded-alignment.svg: FOUND
- docs/advisor/aspects.md: FOUND (modified)

Commits:
- faacdff: Task 1 (shift-registration page + SVG)
- 6cbd773: Task 2 (banded-alignment page + SVG)
- 3e814a9: Task 3 (aspects.md extensions)
