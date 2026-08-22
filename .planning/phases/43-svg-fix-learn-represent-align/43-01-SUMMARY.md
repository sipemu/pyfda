---
phase: 43-svg-fix-learn-represent-align
plan: 01
subsystem: docs/assets/diagrams
tags: [svg, diagrams, style-spec, learn, represent, align]
status: complete

dependency_graph:
  requires: [42-01-SUMMARY.md]
  provides: [corrected learn/represent/align SVG batch]
  affects: [docs/assets/diagrams, Phase 49 site build]

tech_stack:
  added: []
  patterns:
    - SVGO idempotence gate (svgo@3.3.4 --config svgo.config.mjs, check-only)
    - rsvg-convert per-section PNG review
    - STYLE_SPEC canonical <style> block verbatim migration

key_files:
  modified:
    - docs/assets/diagrams/smoothing.svg
    - docs/assets/diagrams/pace-fpca.svg
    - docs/assets/diagrams/banded-alignment.svg
    - docs/assets/diagrams/ex-sonar-tsrvf.svg
  created: []

decisions:
  - "depth-functions.svg left byte-unchanged: functional_boxplot confirmed registered at src/depth_mod.rs:625"
  - "fpca/elastic-fpca/basis-representation/andrews-transformation/distance-metrics left byte-unchanged: all inline font-size= values are intentional size reductions (not CSS-class-size duplicates), removing would change render"
  - "elastic-alignment.svg left byte-unchanged: phase γ(t) label already present at line 61"
  - "shift-registration.svg left byte-unchanged: rigid-vs-elastic contrast key confirmed unambiguous in PNG"
  - "ex-sonar-tsrvf.svg height set to 480 (STYLE_SPEC multi-row allowed value): content fits within 404px, 76px bottom padding"

metrics:
  duration: "4 minutes (15:27–15:32 UTC)"
  completed: "2026-08-22"
  tasks: 3
  commits: 3
  files_changed: 4

actuals:
  tokens: 22000
  tasks: 3
  commits: 3
---

# Phase 43 Plan 01: SVG Fix — learn / represent / align — Summary

**One-liner:** Hand-authored SVG corrections across learn/represent/align batch — Panel-3 ghost removal, PACE subtitle overflow fix, banded-alignment label re-anchor, and full STYLE_SPEC migration of ex-sonar-tsrvf.svg (700→720 viewBox, canonical five CSS classes, role/aria).

---

## Per-Diagram Outcomes

### learn/ Section (Task 1 — tracer)

| Diagram | Outcome | What changed |
|---------|---------|-------------|
| smoothing.svg | **CHANGED** | Removed ghost jagged polyline (stroke-opacity=.2) in Panel 3 that near-duplicated Panel 1 noisy path at y-offset ~5px; Panel 3 now shows only the bold smooth cubic-bezier curve |
| introduction.svg | confirmed OK (16 OK set) | unchanged |
| custom-plotting.svg | confirmed OK (16 OK set) | unchanged |
| simulation.svg | confirmed OK (16 OK set) | unchanged |
| derivatives.svg | confirmed OK (16 OK set) | unchanged |
| irregular-sampling.svg | confirmed OK (16 OK set) | unchanged |

### represent/ Section (Task 2)

| Diagram | Outcome | What changed |
|---------|---------|-------------|
| fpca.svg | **NO EDIT** | All inline font-size= (9px) on .sm elements are intentional reductions from 11px class size; removing would change render geometry |
| elastic-fpca.svg | **NO EDIT** | All inline font-size= (11px on .mono, 9px on .sm) are intentional reductions; not duplicates |
| basis-representation.svg | **NO EDIT** | All inline font-size= (9px on .sm) are intentional reductions; not duplicates |
| andrews-transformation.svg | **NO EDIT** | All inline font-size= (11px on .mono, 10px and 9px on .sm) are intentional; not duplicates |
| distance-metrics.svg | **NO EDIT** | All inline font-size= (11px, 10.5px on .mono) are intentional reductions from 12px class size |
| pace-fpca.svg | **CHANGED** | Shortened subtitle from ~130 chars ("Left: ragged per-curve observation grids (different t-positions per curve) — Right: smooth eigenfunctions recovered on a common work grid") to ~95 chars ("Ragged per-curve grids (sparse, irregular) — PACE recovers smooth eigenfunctions on a common grid"); fits within 720px viewBox |
| depth-functions.svg | **CONFIRMED NO CHANGE** | `functional_boxplot` IS exported: `src/depth_mod.rs:625` `m.add_function(wrap_pyfunction!(functional_boxplot, m)?)`. Reference in diagram is method-accurate. File left byte-unchanged. |
| streaming-depth.svg | confirmed OK (16 OK set) | unchanged |
| imputation.svg | confirmed OK (16 OK set) | unchanged |
| interpolation-policy.svg | confirmed OK (16 OK set) | unchanged |

### align/ Section (Task 3)

| Diagram | Outcome | What changed |
|---------|---------|-------------|
| elastic-alignment.svg | **CONFIRMED NO CHANGE** | `phase γ(t)` label already present at line 61 (`<text class="sm" x="652" y="192" text-anchor="middle" fill="#6c757d">phase &#947;(t)</text>`); warp inset is labeled. Diagram surfaced for Phase 49 human review (see section below). |
| banded-alignment.svg | **CHANGED** | Relocated "upper band edge" annotation: moved from x=180 text-anchor="end" (clipped by legend box ending at x=166) to x=230 y=94 centered above the band start; adjusted leader line. Label no longer overlaps matrix grid. |
| shift-registration.svg | **CONFIRMED NO CHANGE** | Rigid-vs-elastic contrast key (solid blue "shift (rigid)" vs dashed grey "elastic warp" at bottom of method panel) reads unambiguously as a side-by-side contrast in the PNG render; not sequential steps. File left byte-unchanged. |
| ex-sonar-tsrvf.svg | **CHANGED — full STYLE_SPEC migration** | See detail below. |
| advanced-alignment.svg | confirmed OK (16 OK set) | unchanged |
| landmark-registration.svg | confirmed OK (16 OK set) | unchanged |
| tsrvf.svg | confirmed OK (16 OK set) | unchanged |
| alignment-comparison.svg | confirmed OK (16 OK set) | unchanged |
| shape-analysis.svg | confirmed OK (16 OK set) | unchanged |

### ex-sonar-tsrvf.svg — Full STYLE_SPEC Migration Detail

Complete migration from non-conforming to fully conforming:

| Attribute | Before | After |
|-----------|--------|-------|
| viewBox | `0 0 700 400` | `0 0 720 480` |
| fill="none" | missing | added to root svg |
| role="img" | missing | added |
| aria-label | missing | "Validation-First Framework: Three Analysis Paths" |
| style block | `text{font-family:sans-serif}` + `.title/.label/.small/.acc/.box` | Canonical five-class block verbatim from STYLE_SPEC: `.ttl/.sub/.lab/.sm/.mono` |
| title text | `.title` class | `.ttl` class |
| subtitle | none | `.sub` class: "Test elasticity first — let the data choose the right analysis path" |
| section labels | `.label` class | `.lab` class |
| body text | `.small` class | `.sm` class |
| accuracy figures | `.acc` class | `.mono` class |
| method content | preserved intact | preserved intact (three paths, Phase/Total=0.31, 87.0%/77.7%/66.2% accuracy, bottom annotation) |

---

## Method-Accuracy FLAG Resolutions

| FLAG | Resolution |
|------|-----------|
| `depth-functions.svg` — does `functional_boxplot()` exist? | **CONFIRMED EXPORTED**: `src/depth_mod.rs:625` registers `functional_boxplot`. Diagram reference is correct. |
| `shift-registration.svg` — "elastic warp" label contradicts rigid API? | **CONFIRMED ACCURATE**: Legend is a contrast key (rigid vs elastic), confirmed against `docs/align/shift-registration.md:9` prose and PNG visual; shift_register API is rigid (scalar δ argmin); diagram teaches the CONTRAST, not a post-hoc elastic step. |
| `elastic-alignment.svg` — γ(t) inset unlabeled? | **CONFIRMED ALREADY LABELED**: `phase γ(t)` text element present at line 61. See Phase 49 callout below. |

---

## Phase 49 Human Diagram Review — Callouts

The following diagram is flagged for the **Phase 49 blocking human diagram accuracy review**:

### elastic-alignment.svg — Pedagogical Judgment (γ(t) inset)

- **File:** `docs/assets/diagrams/elastic-alignment.svg`
- **Issue:** The Plan 43-01 pre-flight note identified the small warp γ(t) inset (Panel 3, ~line 55) as a pedagogical-judgment call, not a factual error. The `phase γ(t)` label IS already present. However, the warp inset (`<rect x="0" y="0" width="56" height="56">` inside `<g transform="translate(624,120)">`) is visually small relative to the main aligned-curves panel.
- **Conservative fix applied:** None needed — label already present. File left byte-unchanged.
- **For Phase 49 reviewer:** Confirm whether the current size/prominence of the γ(t) warp inset adequately communicates amplitude/phase decomposition to new users, per `docs/align/elastic-alignment.md:6-13`. If the inset is considered too small, a redesign of Panel 3 to give the γ(t) warp more visual weight may be warranted.
- **Risk level:** Low — the label is present and the page prose is clear; this is a question of pedagogical emphasis only.

---

## Deviations from Plan

### Auto-confirmed: XML Cleanup — No Edits for 5 Represent/ Files

**Found during:** Task 2

**Issue:** The plan called for removing inline `font-size=` attributes "that duplicate the size already carried by the element's CSS class." Upon inspection, all inline font-size= values in the five XML-cleanup targets are intentional size reductions (9–11px) from their CSS class sizes (11px for .sm, 12px for .mono), NOT duplicates. Removing them would visibly change the rendered diagram geometry.

**Action:** Per plan rule ("Where an inline size intentionally differs from the class and removing it would visibly change the render, keep the override"), all five files left byte-unchanged (fpca, elastic-fpca, basis-representation, andrews-transformation, distance-metrics).

**Files:** fpca.svg, elastic-fpca.svg, basis-representation.svg, andrews-transformation.svg, distance-metrics.svg

This is a scope narrowing, not a missed fix — the plan correctly anticipated this outcome in "favour deletion only when it does not change rendered geometry."

### Auto-confirmed: elastic-alignment.svg Already Has Phase Label

**Found during:** Task 3 pre-flight

**Issue:** Plan called for adding `phase γ(t)` label to the warp inset. Label was already present at line 61 of the file.

**Action:** File left byte-unchanged. Surfaced in Phase 49 callout section for human adequacy review.

---

## Verification Summary

### SVGO Idempotence Gates (per changed diagram)

| File | SVGO pass 1→2 idempotent | rsvg-convert PNG non-empty |
|------|--------------------------|--------------------------|
| smoothing.svg | PASS (cmp exit 0) | PASS |
| pace-fpca.svg | PASS (cmp exit 0) | PASS |
| banded-alignment.svg | PASS (cmp exit 0) | PASS |
| ex-sonar-tsrvf.svg | PASS (cmp exit 0) | PASS |

### No-Churn Guard

`git diff --stat HEAD~3..HEAD -- docs/assets/diagrams/` lists only:
- docs/assets/diagrams/banded-alignment.svg
- docs/assets/diagrams/ex-sonar-tsrvf.svg
- docs/assets/diagrams/pace-fpca.svg
- docs/assets/diagrams/smoothing.svg

No OK diagrams were modified.

### STYLE_SPEC Conformance

ex-sonar-tsrvf.svg grep assertions passed: viewBox 720, role="img", aria-label, .ttl{, .sub{, .lab{, .sm{, .mono{.

---

## Known Stubs

None — all changes are complete migrations/fixes with no placeholder content.

---

## Threat Flags

None — no new network endpoints, auth paths, or trust boundaries introduced. All changes are hand-authored SVG in the static docs asset directory.

---

## Self-Check: PASSED

- smoothing.svg exists and modified: CONFIRMED
- pace-fpca.svg exists and modified: CONFIRMED
- banded-alignment.svg exists and modified: CONFIRMED
- ex-sonar-tsrvf.svg exists and modified: CONFIRMED (full migration)
- depth-functions.svg byte-unchanged: CONFIRMED
- Commits:
  - ddca5cc: fix(diagrams): learn/ — redraw smoothing.svg Panel-3 reference
  - 60d17ad: fix(diagrams): represent/ — pace-fpca subtitle overflow
  - 6aa9772: fix(diagrams): align/ — ex-sonar STYLE_SPEC migration + banded label re-anchor
