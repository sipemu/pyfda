---
phase: 77-section-landing-card-coverage
plan: "02"
subsystem: docs/represent
tags: [docs, thumbnails, gallery, svg, card-coverage, represent]
status: complete

dependency_graph:
  requires: [77-01]
  provides: [CARD-02, CARD-06-represent]
  affects: [docs/represent/index.md, docs/assets/thumb/]

tech_stack:
  added: []
  patterns:
    - "Hand-authored inline-SVG thumbnails (320x180, #198754 represent hue)"
    - "SVGO@3.3.4 two-pass idempotence verification"
    - "fdars-gallery card insertion pattern"

key_files:
  created:
    - docs/assets/thumb/pace-fpca.svg
    - docs/assets/thumb/interpolation.svg
    - docs/assets/thumb/imputation.svg
  modified:
    - docs/represent/index.md

decisions:
  - "interpolation.svg simplified to ~1150 bytes by using filled circles + vertical tick lines instead of separate tick marks + open circles, keeping design clear and under 1200 byte limit"
  - "imputation.svg authored minimal (656 bytes): solid-dashed-solid three-segment pattern cleanly depicts the imputed gap concept"
  - "pace-fpca.svg uses both a dashed faint background curve (the latent trajectory) and solid filled dots (sparse observations) plus a bold overlaid smooth curve — readable at thumbnail scale"

metrics:
  duration_seconds: 155
  completed: "2026-09-06"
  tasks_completed: 1
  tasks_total: 1
  commits: 1

estimate:
  tokens: 46000
actuals:
  tokens: 6000
  tasks: 1
  commits: 1
---

# Phase 77 Plan 02: Represent Section Gallery Card Coverage Summary

**One-liner:** Three hand-authored green (#198754) 320×180 SVG thumbnails and fdars-gallery cards for pace-fpca, interpolation, and imputation, bringing the represent landing gallery to 100% card coverage.

## What Was Built

### Task 1: Author represent thumbnails + insert 3 gallery cards (CARD-02, CARD-06)

**Commit:** 4b08823

Authored three new minimal hand-authored inline-SVG thumbnails and inserted their gallery cards into `docs/represent/index.md`:

**docs/assets/thumb/pace-fpca.svg** (~1070 bytes):
- L-shaped axis, 7 filled circles at irregular (x, y) positions depicting sparse observations
- Dashed faint background curve (the latent trajectory underlying the sparse data)
- Bold smooth cubic Bézier overlaid (the PACE-recovered smooth), all in #198754 green
- aria-label="PACE sparse FPCA"

**docs/assets/thumb/interpolation.svg** (~1150 bytes):
- L-shaped axis, 4 filled circle dots at coarse-grid x positions with vertical tick lines to the x-axis
- Bold smooth cubic Bézier curve through those points (the interpolated result)
- Concept: coarse-grid source points → smooth resampled curve; all in #198754 green
- aria-label="Spline interpolation"

**docs/assets/thumb/imputation.svg** (~656 bytes):
- L-shaped axis, solid-dashed-solid three-segment curve pattern
- Left solid segment → dashed middle segment (the missing/imputed region) → right solid segment
- Concept: a curve with a gap filled by imputation; all in #198754 green
- aria-label="Missing value imputation"

**docs/represent/index.md** — 3 fdars-gallery cards inserted after `basis-representation` (before `andrews-transformation`), in order: pace-fpca → interpolation → imputation. Gallery reaches 100% coverage (10 cards: fpca, elastic-fpca, basis-representation, pace-fpca, interpolation, imputation, andrews-transformation, depth-functions, streaming-depth, distance-metrics).

## Verification Results

### Gate 1: Structural Check
- All 3 thumbnail files exist
- Each has `viewBox="0 0 320 180"`
- Each carries `#198754` hue; no other section hex present
- Each has `role="img"` + `aria-label="..."`
- No `<title>`, `<desc>`, `aria-labelledby>`, or `<style>` in any thumbnail
- All under 1200 bytes (pace-fpca: 1070, interpolation: 1150, imputation: 656)
- All 3 cards present in `docs/represent/index.md` (href + src)
- **Result: STRUCT OK represent 3 thumbnails + 3 cards**

### Gate 2: SVGO Idempotence + Smoke Render
- SVGO two-pass diff empty for all 3: pace-fpca, interpolation, imputation
- `rsvg-convert -w 320 -h 180` exits 0 for all 3
- **Result: ALL GATES PASSED**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] interpolation.svg initial size exceeded 1200 bytes**
- **Found during:** Task 1 verification gate (structural check)
- **Issue:** First iteration of interpolation.svg was 1667 bytes (separate tick marks + open stroke circles + dense-grid intermediate ticks)
- **Fix:** Redesigned to use solid filled circles + vertical tick lines to the axis (removes the separate short tick-mark-only lines). Kept the conceptual clarity (coarse-grid input points → smooth curve) while bringing size to 1150 bytes
- **Files modified:** docs/assets/thumb/interpolation.svg
- **Commit:** 4b08823 (fixed before commit, single atomic commit)

## Known Stubs

None. All 3 thumbnails are fully authored line-art with no placeholder content.

## Threat Flags

None. Docs-only plan — static decorative SVG files and HTML card entries in a section index. No scripts, no external references, no network surface.

## Self-Check: PASSED

- docs/assets/thumb/pace-fpca.svg: FOUND
- docs/assets/thumb/interpolation.svg: FOUND
- docs/assets/thumb/imputation.svg: FOUND
- docs/represent/index.md: pace-fpca/interpolation/imputation cards: FOUND
- Commit 4b08823: FOUND
