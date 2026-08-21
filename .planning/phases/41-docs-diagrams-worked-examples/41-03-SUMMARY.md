---
phase: 41-docs-diagrams-worked-examples
plan: "03"
subsystem: docs/inference,docs/represent,docs/analyze
tags: [docs, svg, markdown-exec, depth, outliers, inference, itp]
depends_on:
  requires: [41-02]
  provides:
    - docs/inference/interval-inference.md
    - docs/assets/diagrams/itp-interval-inference.svg
    - docs/represent/depth-functions.md (Group C extension)
    - docs/analyze/outlier-detection.md (Group C extension)
    - docs/assets/diagrams/functional-outliers.svg
  affects: [mkdocs.yml]
tech_stack:
  added: []
  patterns:
    - hand-authored inline SVG (STYLE_SPEC-conformant, viewBox 720x300)
    - markdown-exec exec fence with FDARS_FENCE_OK sentinel
    - MkDocs Material nav wiring (Inference section expanded to 2 items)
key_files:
  created:
    - docs/inference/interval-inference.md
    - docs/assets/diagrams/itp-interval-inference.svg
    - docs/assets/diagrams/functional-outliers.svg
  modified:
    - docs/represent/depth-functions.md
    - docs/analyze/outlier-detection.md
    - mkdocs.yml
decisions:
  - "ITP closure direction corrected: adjusted p-values are >= raw p-values (FWER control increases conservativeness). RESEARCH.md stated adjusted <= raw which contradicts actual API output; empirical test confirmed adj >= raw is the correct direction. SVG and page text reflect verified behavior."
  - "Task 1 build ran before Tasks 2/3 were written (correct tracer-first pattern). Second build verified Tasks 2/3."
  - "Task 4 (SVGO gate) had no commit since both SVGs were already committed; gate passed as verification-only."
  - "functional_depth fence uses output that confirms all 9 methods work, even though not all flag the same outlier — the fence correctly demonstrates the API, not a specific detection result."
metrics:
  duration: "~55 minutes active authoring + 2 sequential DOCS_FAST builds (~26 min each)"
  completed: "2026-08-21"
  tasks_completed: 4
  commits: 2
status: complete
requirements: [DOCS-10]
actuals:
  tokens: 74000
  tasks: 4
  commits: 2
---

# Phase 41 Plan 03: Depth / Outliers / Interval Inference (DOCS-10) Summary

One new page (interval-inference.md with ITP SVG and fence), two page extensions (depth-functions.md with 9 new depth methods, outlier-detection.md with 4 new detectors and asymmetry SVG), and two new STYLE_SPEC-conformant SVGs — all building offline under DOCS_FAST=1 strict mode with executed fences emitting FDARS_FENCE_OK.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (tracer) | Interval-wise Inference page + SVG + nav + build | 4b2ac8f | `interval-inference.md`, `itp-interval-inference.svg`, `mkdocs.yml` |
| 2 | Depth-functions.md Group C extension | a704c4f | `depth-functions.md` |
| 3 | Outlier-detection.md Group C extension + SVG | a704c4f | `outlier-detection.md`, `functional-outliers.svg` |
| 4 | SVGO idempotence gate | (verification only) | Both new SVGs pass IDEMPOTENT check |

## Verification Results

All plan automated checks pass on the second DOCS_FAST strict build (exit 0):

```
ITP_FENCE_OK        — FDARS_FENCE_OK in site/inference/interval-inference/index.html
ITP_SVG_OK          — itp-interval-inference.svg referenced in page HTML
DEPTH_HYPOGRAPH_OK  — hypograph_index in site/represent/depth-functions/index.html
DEPTH_FENCE_OK      — FDARS_FENCE_OK in site/represent/depth-functions/index.html
OUTLIERS_SVG_OK     — functional-outliers.svg in site/analyze/outlier-detection/index.html
OUTLIERS_FENCE_OK   — FDARS_FENCE_OK in site/analyze/outlier-detection/index.html
TRACER_OK           — Tracer build (Task 1 first build) exited 0 with FDARS_FENCE_OK
IDEMPOTENT: docs/assets/diagrams/itp-interval-inference.svg
IDEMPOTENT: docs/assets/diagrams/functional-outliers.svg
NO_SRC_CHANGES      — git diff src/*.rs empty
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ITP closure direction corrected in SVG and documentation**
- **Found during:** Task 1 fence testing
- **Issue:** RESEARCH.md and PLAN.md stated "closure REDUCES p-values: adjusted at or BELOW raw" — but the actual API returns adjusted_pvalues >= raw_pvalues consistently. This was verified empirically: with nbasis=5 giving n_basis=6 actual functions, raw values near 0.005 adjusted to ~0.035–0.136.
- **Fix:** SVG legend says "closure-adjusted (≥ raw)" and shows adjusted bars above raw; page text contains `!!! note "Closure increases individual p-values"` correcting the plan's mistaken statement. This is the standard behavior of FWER multiple-testing corrections (Holm, Romano-Wolf) — adjusting conservatively to control family-wise error rate.
- **Files modified:** `itp-interval-inference.svg`, `interval-inference.md`
- **No additional commit required** — the corrected content is in the Task 1 commit.

### No Other Deviations

Fences executed as specified in RESEARCH.md blueprints. All three API surfaces (itp_one_pop, functional_depth with 9 methods, tvdmss/muod/sequential_transform_outliers/depthgram) confirmed offline-executable against shipped bindings.

## Pages Produced

### docs/inference/interval-inference.md (new)
- H1 "Interval-wise Testing Procedure (ITP)"
- Summary table: itp_one_pop / itp_two_pop / itp_flm
- SVG include: itp-interval-inference.svg
- Theory section: basis expansion, permutation p-values, closure adjustment with KaTeX
- Parameter tables for all three functions
- Returns table with all 5 keys
- n_basis clamping admonition (Pitfall 5)
- Closure-direction correction note (adjusted >= raw)
- Executed fence: n=20, m=40, seed=0, DOCS_FAST fast() for n_perm

### docs/represent/depth-functions.md (extended)
- New "## New depth measures (v6.0)" section before ## References
- Method table: 9 new functional_depth method strings with one-line descriptions
- Note on hypograph/epigraph asymmetry with pointer to outlier-detection.md diagram
- Executed fence looping over all 9 methods

### docs/analyze/outlier-detection.md (extended)
- New "## Functional-outlier detectors (v6.0)" section before ## See also
- functional-outliers.svg include
- Subsections for tvdmss, muod, sequential_transform_outliers, depthgram
- Parameter + returned-keys tables per detector
- depth_method (not method) Pitfall 4 warning
- n >= 3 (muod) and n >= 2 (depthgram) minimum-sample notes
- no-argvals/no-seed note for tvdmss and muod
- Executed fence exercising all 4 detectors

## SVG Diagrams

### itp-interval-inference.svg
- viewBox "0 0 720 300", fill="none", role="img", aria-label, verbatim style block
- Left panel: bar chart of test statistics per basis function (large in middle where shift is)
- Right panel: side-by-side raw (light) and closure-adjusted (dark) p-values with 0.05 threshold
- Closure direction CORRECT: adjusted bars above raw, labelled "adj >= raw (FWER control)"
- SVGO idempotent under svgo@3.3.4

### functional-outliers.svg
- viewBox "0 0 720 300", fill="none", role="img", aria-label, verbatim style block
- Left panel: hypograph index — curve at BOTTOM of bundle (many curves above → high hypograph)
- Right panel: epigraph index — curve at TOP of bundle (many curves below → high epigraph)
- >= 2 reference curves with asymmetric counting correctly labelled
- Asymmetry summary in bottom text strip
- SVGO idempotent under svgo@3.3.4

## Self-Check: PASSED

- FOUND: docs/inference/interval-inference.md
- FOUND: docs/assets/diagrams/itp-interval-inference.svg
- FOUND: docs/assets/diagrams/functional-outliers.svg
- FOUND: commit 4b2ac8f (Task 1 — ITP page + SVG + nav)
- FOUND: commit a704c4f (Tasks 2+3 — depth extension + outlier extension + SVG)
- FOUND: ITP FDARS_FENCE_OK in site/inference/interval-inference/index.html
- FOUND: depth FDARS_FENCE_OK in site/represent/depth-functions/index.html
- FOUND: outliers FDARS_FENCE_OK in site/analyze/outlier-detection/index.html
