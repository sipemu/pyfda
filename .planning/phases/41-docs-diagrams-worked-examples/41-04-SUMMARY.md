---
phase: 41-docs-diagrams-worked-examples
plan: "04"
subsystem: docs/advisor,docs (whole-site),docs/assets/diagrams
tags: [docs, advisor, svg, svgo, mkdocs, human-review, method-accuracy]
depends_on:
  requires: [41-01, 41-02, 41-03]
  provides:
    - docs/advisor/aspects.md (Phase-40 extended diagnostics)
    - whole-site strict build source-of-truth gate (green)
    - whole-corpus SVGO-idempotence + determinism gate (green)
    - human diagram method-accuracy sign-off (all 6 new SVGs)
  affects: [mkdocs.yml, docs/assets/diagrams/functional-outliers.svg, docs/represent/depth-functions.md]
tech_stack:
  added: []
  patterns:
    - whole-site MkDocs strict build as source-of-truth gate (non-DOCS_FAST, all fences full-size)
    - svgo@3.3.4 --config svgo.config.mjs idempotence + determinism (no date/timestamp metadata)
    - blocking-human diagram method-accuracy review (not auto-approvable)
key_files:
  created:
    - .planning/phases/41-docs-diagrams-worked-examples/41-04-SUMMARY.md
  modified:
    - docs/advisor/aspects.md
    - docs/assets/diagrams/functional-outliers.svg
    - docs/represent/depth-functions.md
    - mkdocs.yml
decisions:
  - "Human diagram review caught a real method-accuracy defect: functional-outliers.svg and depth-functions.md asymmetry prose had the hypograph/epigraph direction INVERTED. Verified empirically against shipped fdars: a top-of-bundle curve has HIGH hypograph_index (1.0, many curves below) and LOW epigraph_index (0.125); a bottom curve is the reverse. Corrected the SVG panel geometry, arrow/reference labels, caption, and depth-functions.md lines 526-529."
  - "Correct convention matches the depth-functions.md API table (hypograph_index = proportion of curves BELOW the reference) and summary line 554 (epigraph_index assigns low depth to a curve above the bulk); only the 41-03 asymmetry subsection + diagram were inverted."
  - "Whole-site gate uses the FULL strict build (no DOCS_FAST) so every fence executes at full data size — the milestone's source-of-truth build. Green at 1351s."
  - "Worktree isolation disabled for the phase: doc-build fences hardcode the main-tree .venv/bin/mkdocs path, so executors ran sequentially on main (see chore commit adbecf1)."
metrics:
  duration: "~1h advisor authoring + gates; 1x whole-site strict build (~22.5 min) + 1x re-verify build (~22.5 min) after the human-review fix"
  completed: "2026-08-22"
  tasks_completed: 4
  commits: 3
status: complete
requirements: [DOCS-11]
actuals:
  tasks: 4
  commits: 3
---

# Phase 41 Plan 04: Advisor Aspects + Whole-Site Gate + Human Diagram Review (DOCS-11) Summary

Closed DOCS-11: updated the advisor `aspects.md` for the Phase-40 extended diagnostics, confirmed every new v6.0 page is nav-wired, ran the whole-site strict build as the source-of-truth gate, verified whole-corpus SVGO-idempotence + determinism on all six new SVGs, and completed the blocking human diagram method-accuracy review — which caught and corrected an inverted hypograph/epigraph asymmetry in the functional-outliers diagram and depth-functions prose.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update advisor/aspects.md for Phase-40 extended diagnostics | 01183ee | `docs/advisor/aspects.md` |
| 2 | Confirm nav completeness + whole-site strict build gate | 23fe222 | build-gate record |
| 3 | Whole-corpus SVGO idempotence + determinism gate | (verification only) | all 6 new SVGs |
| 4 | BLOCKING human diagram method-accuracy review + fix | bbe2579 | `functional-outliers.svg`, `depth-functions.md` |

## Verification Results

Whole-site strict build (source-of-truth gate, full data, non-DOCS_FAST) after the human-review fix:

```
FULL_GATE_OK  /  GATE_EXIT:0
Documentation built in 1351.12 seconds
- nav: concurrent-regression.md, functional-glm.md, pace-fpca.md, interval-inference.md all present in mkdocs.yml
- FDARS_FENCE_OK present in all 7 built pages:
    regression/concurrent-regression, regression/functional-glm, represent/pace-fpca,
    regression/classification, represent/depth-functions, analyze/outlier-detection,
    inference/interval-inference
- svgo@3.3.4 idempotence (byte-identical 2nd pass) + no date/timestamp metadata on all 6 SVGs:
    concurrent-regression, functional-glm, pace-fpca, elastic-multinomial,
    itp-interval-inference, functional-outliers
- No src/*.rs changes
```

## Human Diagram Method-Accuracy Review (Task 4)

Six diagrams rendered to PNG at 1440px and reviewed against the shipped `fdars` bindings.
Five passed unchanged; one required a correction:

| Diagram | Verdict |
|---|---|
| concurrent-regression | PASS — time-varying β(t) curves, `(p, m)`, not scalar |
| functional-glm | PASS — Gamma `inverse g(μ)=1/μ`, `≠ log-link (R default)` |
| pace-fpca | PASS — sparse ragged observations → smooth eigenfunctions on work grid |
| elastic-multinomial | PASS — K one-vs-rest binary elastic classifiers → softmax (not LDA) |
| itp-interval-inference | PASS — closure-adjusted p-values ≥ raw (FWER control) |
| functional-outliers | FIXED — hypograph/epigraph asymmetry was inverted |

### Deviation (Rule 1 — Bug): inverted hypograph/epigraph asymmetry

- **Found during:** Task 4 human diagram review.
- **Issue:** `functional-outliers.svg` and the `depth-functions.md` "Hypograph vs epigraph asymmetry" prose (lines 526–529) stated a bottom-of-bundle curve has HIGH hypograph + LOW epigraph. This is inverted, and contradicted the same page's own API table (line 512: `hypograph_index` = proportion of curves BELOW the reference) and summary line 554.
- **Ground truth (empirical, shipped bindings):** for a top-of-bundle curve `functional_depth(..., method="hypograph_index")` → 1.0 and `epigraph_index` → 0.125; a bottom-of-bundle curve is the reverse. So: top curve → HIGH hypograph + LOW epigraph; bottom curve → LOW hypograph + HIGH epigraph.
- **Fix (commit bbe2579):** swapped the two panels' drawn geometry, arrow directions, reference/arrow labels, and the caption in the SVG; corrected `depth-functions.md` lines 526–529. Re-ran SVGO idempotence (pass, no date metadata), re-rendered the PNG, and re-ran the whole-site strict gate (FULL_GATE_OK, exit 0).
- **Human sign-off:** approved after re-presentation.

## Pages / Artifacts Produced

### docs/advisor/aspects.md (extended)
- Documents the Phase-40 extended grounded diagnostics for the `outliers` and `regression` advisor aspects (new detector + regression result scalars), grounding invariant preserved.

### docs/assets/diagrams/functional-outliers.svg (corrected)
- Left "Hypograph Index" panel: reference near the TOP, 7 bundle curves below, `hypograph_index ≈ 0.88`.
- Right "Epigraph Index" panel: reference near the BOTTOM, 7 curves above, `epigraph_index ≈ 0.88`.
- Caption: top curve → HIGH hypograph + LOW epigraph; bottom → the reverse.
- SVGO idempotent under svgo@3.3.4, no date metadata.

### docs/represent/depth-functions.md (corrected)
- "Hypograph vs epigraph asymmetry" subsection direction fixed to match the API table and shipped behavior.

## Self-Check: PASSED
