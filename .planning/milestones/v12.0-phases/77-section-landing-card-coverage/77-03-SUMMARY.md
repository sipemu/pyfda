---
phase: 77-section-landing-card-coverage
plan: "03"
subsystem: docs/regression
status: complete
tags: [thumbnails, gallery-cards, svg, regression, card-coverage]
requires: [77-01]
provides: [CARD-03, CARD-06-regression]
affects: [docs/regression/index.md]
tech_stack:
  added: []
  patterns: [hand-authored-svg, svgo-idempotence, fdars-gallery-card]
key_files:
  created:
    - docs/assets/thumb/concurrent-regression.svg
    - docs/assets/thumb/functional-glm.svg
    - docs/assets/thumb/function-on-function.svg
    - docs/assets/thumb/additive-sof.svg
    - docs/assets/thumb/frechet-regression.svg
  modified:
    - docs/regression/index.md
decisions:
  - "Concurrent-regression: wavy β(t) coefficient function with zero-reference line — plainest possible expression of the varying-coefficient concept"
  - "Functional-GLM: two-panel sketch (functional predictor → arrow → binary scatter + logistic S-curve) at 115/168 x-split to fit both panels under 1200 bytes"
  - "Function-on-function: contour-line representation of the bivariate coefficient surface β(s,t) inside a bounding rectangle with s- and t-axes"
  - "Additive-SOF: arch + trough component curves sharing a mid-baseline, scalar-response circle at right edge"
  - "Fréchet regression: geodesic arc with two filled observation circles and one open conditional-mean circle on a faint reference horizon"
metrics:
  duration_minutes: 2
  completed: "2026-09-06"
  tasks_completed: 1
  commits: 1
  files_changed: 6
estimate:
  tokens: 54000
actuals:
  tokens: 1901
  tasks: 1
  commits: 1
---

# Phase 77 Plan 03: Regression Section Card Coverage Summary

**One-liner:** Five hand-authored #dc3545 SVG thumbnails (concurrent-regression, functional-glm, function-on-function, additive-sof, frechet-regression) — all SVGO-idempotent, rsvg-render-clean — inserted as fdars-gallery cards into docs/regression/index.md, completing CARD-03.

## What Was Built

Five new minimal 320×180 inline-SVG thumbnails for the regression section, each using hue `#dc3545`, and five matching `fdars-gallery` card entries inserted into `docs/regression/index.md` immediately after the `function-on-scalar` card (before `classification`).

### Thumbnails authored

| Slug | Concept | Bytes | SVGO | Render |
|------|---------|-------|------|--------|
| `concurrent-regression` | Wavy β(t) coefficient curve + zero-reference dashed line | 610 | idempotent | OK |
| `functional-glm` | Two-panel: functional curve → arrow → binary scatter + logistic S | 1156 | idempotent | OK |
| `function-on-function` | Bivariate β(s,t) surface as nested contour arcs in bounding rectangle | 857 | idempotent | OK |
| `additive-sof` | Arch + trough component curves + scalar-response circle | 854 | idempotent | OK |
| `frechet-regression` | Geodesic arc, 2 filled observation circles, 1 open conditional-mean circle | 672 | idempotent | OK |

### Cards inserted into docs/regression/index.md

| Card | href | src |
|------|------|-----|
| Concurrent Regression | `concurrent-regression/` | `../assets/thumb/concurrent-regression.svg` |
| Functional GLM | `functional-glm/` | `../assets/thumb/functional-glm.svg` |
| Function-on-Function | `function-on-function/` | `../assets/thumb/function-on-function.svg` |
| Additive Scalar-on-Function | `additive-sof/` | `../assets/thumb/additive-sof.svg` |
| Fréchet Regression | `frechet-regression/` | `../assets/thumb/frechet-regression.svg` |

## Verification Gates

Both gates passed:

**Structural gate (node one-liner):**
- All 5 thumbnail files exist
- Each has `viewBox="0 0 320 180"`, `#dc3545` hue, no other section hex
- Each has `role="img"` + `aria-label`, no `<title>/<desc>/aria-labelledby/<style>`
- All under 1200 bytes
- `docs/regression/index.md` carries all 5 cards' `href` + `src`
- Result: `STRUCT OK regression 5 thumbnails + 5 cards`

**Determinism gate (SVGO two-pass + rsvg render):**
- All 5 thumbnails: SVGO pass1 == pass2 (idempotent)
- All 5 thumbnails: `rsvg-convert` exits 0
- Result: `SVGO idempotent + render OK`

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all cards link to existing regression method pages; no placeholder content.

## Threat Flags

None — docs-only static SVG assets and one index.md edit, no new network or code surface.

## Self-Check: PASSED

- [x] docs/assets/thumb/concurrent-regression.svg exists (610 bytes)
- [x] docs/assets/thumb/functional-glm.svg exists (1156 bytes)
- [x] docs/assets/thumb/function-on-function.svg exists (857 bytes)
- [x] docs/assets/thumb/additive-sof.svg exists (854 bytes)
- [x] docs/assets/thumb/frechet-regression.svg exists (672 bytes)
- [x] docs/regression/index.md contains all 5 cards' href and src
- [x] Commit cd61d50 exists: feat(77-03): add 5 regression thumbnails and gallery cards (CARD-03)
