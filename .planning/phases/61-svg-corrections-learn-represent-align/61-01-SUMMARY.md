---
phase: 61-svg-corrections-learn-represent-align
plan: "01"
subsystem: docs/assets/diagrams
tags: [svg, accessibility, a11y, diagram-corrections, method-accuracy]
status: complete

dependency_graph:
  requires: []
  provides:
    - A11Y-01: all 24 learn/represent/align concept diagrams have aria-label matching .ttl title verbatim
    - A11Y-02: all 24 diagrams carry <title>/<desc>/aria-labelledby
    - DEFECT-02: shift-registration inter-panel crowding resolved; banded-alignment edge labels repositioned; pace-fpca subtitle shortened
    - DEFECT-03: shift-registration "elastic warp" method-accuracy defect removed
  affects:
    - docs/assets/diagrams/ (24 SVG files)

tech_stack:
  added: []
  patterns:
    - inline SVG aria-labelledby + <title> + <desc> accessibility contract (per STYLE_SPEC)

key_files:
  created: []
  modified:
    - docs/assets/diagrams/shift-registration.svg
    - docs/assets/diagrams/introduction.svg
    - docs/assets/diagrams/custom-plotting.svg
    - docs/assets/diagrams/simulation.svg
    - docs/assets/diagrams/smoothing.svg
    - docs/assets/diagrams/derivatives.svg
    - docs/assets/diagrams/irregular-sampling.svg
    - docs/assets/diagrams/fpca.svg
    - docs/assets/diagrams/elastic-fpca.svg
    - docs/assets/diagrams/basis-representation.svg
    - docs/assets/diagrams/andrews-transformation.svg
    - docs/assets/diagrams/depth-functions.svg
    - docs/assets/diagrams/streaming-depth.svg
    - docs/assets/diagrams/distance-metrics.svg
    - docs/assets/diagrams/pace-fpca.svg
    - docs/assets/diagrams/imputation.svg
    - docs/assets/diagrams/interpolation-policy.svg
    - docs/assets/diagrams/elastic-alignment.svg
    - docs/assets/diagrams/advanced-alignment.svg
    - docs/assets/diagrams/landmark-registration.svg
    - docs/assets/diagrams/tsrvf.svg
    - docs/assets/diagrams/alignment-comparison.svg
    - docs/assets/diagrams/shape-analysis.svg
    - docs/assets/diagrams/banded-alignment.svg

decisions:
  - "Removed shift-registration elastic-warp label and dashed arrow path entirely (no replacement annotation); conservative removal per DEFECT-03 hard gate"
  - "pace-fpca subtitle shortened from ~80 chars to 72 chars by removing the em-dash clause and restating concisely"
  - "banded-alignment: upper-band-edge label repositioned from (x=490,y=100) to (x=466,y=116); band_frac label moved from y=92 to y=88 to create vertical separation"
  - "depth-functions pre-existing inline .ttl font-size/style deviation left untouched per SPEC-01 do-not-regress"
  - "<desc> text in advanced-alignment.svg uses HTML entity &amp; in the aria-label for the & in Penalized & Constrained"

metrics:
  duration: "~9 minutes"
  completed: "2026-09-02"
  tasks_completed: 5
  tasks_total: 5
  commits: 4
  files_modified: 24

actuals:
  tokens: 38000
  tasks: 5
  commits: 4
---

# Phase 61 Plan 01: SVG Corrections — learn/represent/align Summary

All 24 learn/ + represent/ + align/ concept diagrams corrected for accessibility (A11Y-01 + A11Y-02), three design/geometry defects fixed (DEFECT-01/02/03), and STYLE_SPEC conformance preserved (SPEC-01). Every diagram renders cleanly to PNG via rsvg-convert.

## One-Liner

Accessibility markup (title/desc/aria-labelledby) added to all 24 learn/represent/align SVG concept diagrams, with shift-registration method-accuracy defect removed, banded-alignment labels repositioned, and pace-fpca subtitle shortened.

## What Was Done

### Per-Diagram Categorisation

| Category | Files | Changes |
|----------|-------|---------|
| A11Y-only (21 files) | introduction, custom-plotting, simulation, smoothing, derivatives, irregular-sampling, fpca, elastic-fpca, basis-representation, andrews-transformation, streaming-depth, distance-metrics, imputation, interpolation-policy, elastic-alignment, advanced-alignment, landmark-registration, tsrvf, alignment-comparison, shape-analysis | A11Y-01 aria-label + A11Y-02 title/desc/aria-labelledby only |
| A11Y + design fix (3 files) | shift-registration, banded-alignment, pace-fpca | A11Y + geometry/method correction |
| Complex diagram desc (2 files) | depth-functions (720×520), banded-alignment (720×480) | A11Y + long-form 2-sentence desc |

### Accessibility Contract Applied (all 24)

Every diagram now carries:
- `<title id="<slug>-title">` — the verbatim `.ttl` title text
- `<desc id="<slug>-desc">` — 1–2 method-accurate sentences grounded in audit §1 Notes
- `aria-labelledby="<slug>-title <slug>-desc"` on the root `<svg>`
- `aria-label` corrected to match the visible `.ttl` title text character-for-character

### Design/Geometry Fixes

#### shift-registration.svg (DEFECT-02 + DEFECT-03)

**Decision:** Removed the "elastic warp" label text (line ~53 in original) and its dashed curved arrow path (line ~51) and arrowhead (line ~52) entirely. No replacement annotation was added — conservative removal per the plan's guidance.

**Result:** The Contrast key now shows only "shift (rigid)" with a straight blue arrow. The inter-panel gap between Panel 2 and Panel 3 is no longer crowded (was two arrows/labels in 44px gap; now one). The diagram correctly depicts rigid scalar shift only with no implication of elastic warping.

**Visually confirmed** in rendered PNG: no elastic-warp entry visible; "shift (rigid)" key remains clear; L2 objective shading and δ(rigid) arrow intact.

#### pace-fpca.svg (DEFECT-02 subtitle overflow)

**Original subtitle:** "Ragged per-curve grids (sparse, irregular) — PACE recovers smooth eigenfunctions on a common grid" (82 characters)

**Shortened to:** "PACE recovers smooth eigenfunctions from sparse, irregular per-curve grids" (72 characters)

**Visually confirmed** in rendered PNG: subtitle sits well within the 720px viewBox width with no clipping. Method-accuracy preserved — PACE still correctly described as recovering smooth eigenfunctions from sparse/irregular per-curve observations.

#### banded-alignment.svg (DEFECT-01/02 edge crowding)

The two crowded labels at the top-right of the DP cost-matrix panel were repositioned:

- "upper band edge" label: moved from (x=490, y=100, start anchor) to (x=466, y=116, start anchor); pointer arrow adjusted accordingly from (490,98)→(445,112) to (466,114)→(432,116)
- "band_frac × m = B" monospace label: moved from y=92 to y=88 (nudged up to create vertical gap from "upper band edge")

**Visually confirmed** in rendered PNG: both labels are readable and separated; "band_frac × m = B" in blue in the upper-right area; "upper band edge" in orange with arrow pointing to the dashed orange line. No panel/font/palette changes.

#### depth-functions.svg (A11Y-02 special case)

The most complex diagram in the represent/ bucket (720×520, multi-panel: curve sample + depth() interface + depth values bar chart + Depth-Based Tools application grid + bottom summary row). A genuinely informative 2-sentence `<desc>` was written covering both the depth-ranking operation and the downstream tools grid. The pre-existing inline `.ttl` `font-size="20" style="fill:#333"` deviation was left untouched per SPEC-01 do-not-regress.

## Deviations from Plan

None — plan executed exactly as written. All 5 tasks completed in order; each committed atomically. The conservative removal of the elastic-warp label (no replacement annotation) was explicitly recommended by the plan.

## Phase 65 Human Review Notes

The following items should be confirmed in the Phase 65 blocking human review:

1. **shift-registration.svg**: The "Contrast key" region now shows only "shift (rigid)". No annotation clarifying that shift_register is NOT an elastic method was added (conservative removal). If the diagram reviewer feels a clarifying note is needed (e.g., "rigid only — no warping"), this should be added during Phase 65.

2. **banded-alignment.svg label repositions**: The "upper band edge" label was moved. A human should confirm the arrow still clearly associates the label with the correct dashed orange line in the rendered diagram.

3. **All 24 `<desc>` texts**: The method-accurate descriptions were written from audit §1 Notes. A human should spot-check 3–4 of the most complex diagrams (depth-functions, banded-alignment, elastic-alignment, pace-fpca) to confirm the desc text correctly characterises the method.

## Known Stubs

None. All `<desc>` elements contain real method-accurate prose — no placeholder text was used.

## Threat Flags

None. All changes are confined to SVG accessibility attributes and element-text content within the 24 diagram files. No new network endpoints, auth paths, file access patterns, or schema changes were introduced.

## Verification Results

### Self-Check

All 24 SVGs:
- Render to non-empty PNGs via rsvg-convert (exit 0) — confirmed
- Carry `<title id="<slug>-title">`, `<desc id="<slug>-desc">`, and `aria-labelledby="<slug>-title <slug>-desc"` — confirmed by grep
- shift-registration.svg contains no "elastic warp" string — confirmed
- `git diff db68201..HEAD --name-only` shows exactly 24 `docs/assets/diagrams/*.svg` files — confirmed, no scope violations
- No viewBox/style/palette changes — confirmed by not modifying `<style>` blocks
- Three design-defect diagrams visually inspected in rendered PNGs — confirmed clean

### Task 5 Automated Gate (exact verify command output)

All 24 diagrams: ALL CHECKS PASSED

## Self-Check: PASSED

All 24 SVG files exist on disk, all 4 commits exist in git history (1f309d5, f0883ec, 65f7420, 9c32604), and the scope guard confirms no files outside `docs/assets/diagrams/*.svg` were modified.
