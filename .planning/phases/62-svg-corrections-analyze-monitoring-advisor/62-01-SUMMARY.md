---
phase: 62-svg-corrections-analyze-monitoring-advisor
plan: "01"
subsystem: docs/assets/diagrams
tags: [svg, a11y, accessibility, diagram-quality, elastic-clustering, defect-fix]
status: complete

dependency_graph:
  requires: []
  provides:
    - 26 concept SVGs with A11Y title/desc/aria-labelledby (A11Y-01, A11Y-02)
    - elastic-clustering.svg full redraw (DEFECT-01, DEFECT-03)
    - outlier-detection.svg Amplitude taxonomy confirmed (DEFECT-03)
    - covariance-functions.svg arrow-entity consistency fix (A11Y-01)
    - advisor-mcp.svg boundary label geometry fix (DEFECT-02)
    - sklearn-pipeline-dataflow.svg predictor label overflow fix (DEFECT-01)
  affects:
    - Phase 64 (SYNC-01): elastic-clustering thumb must be re-synced to match new concept
    - Phase 65: whole-site SVGO gate and build will exercise all 26 corrected SVGs

tech_stack:
  added: []
  patterns:
    - SVG <title>+<desc> wired via aria-labelledby (long-form accessibility pattern)
    - SVGO idempotence gate: svgo(svgo(x)) == svgo(x) under svgo.config.mjs

key_files:
  created: []
  modified:
    - docs/assets/diagrams/spm.svg
    - docs/assets/diagrams/tolerance-bands.svg
    - docs/assets/diagrams/clustering.svg
    - docs/assets/diagrams/gmm-clustering.svg
    - docs/assets/diagrams/outlier-detection.svg
    - docs/assets/diagrams/functional-outliers.svg
    - docs/assets/diagrams/functional-boxplot.svg
    - docs/assets/diagrams/seasonal-analysis.svg
    - docs/assets/diagrams/equivalence-testing.svg
    - docs/assets/diagrams/covariance-functions.svg
    - docs/assets/diagrams/scoring-metrics.svg
    - docs/assets/diagrams/functional-statistics.svg
    - docs/assets/diagrams/advanced-spm.svg
    - docs/assets/diagrams/profile-partial-monitoring.svg
    - docs/assets/diagrams/advisor-loop.svg
    - docs/assets/diagrams/advisor-grounding-invariant.svg
    - docs/assets/diagrams/advisor-aspects.svg
    - docs/assets/diagrams/advisor-agent-skill.svg
    - docs/assets/diagrams/advisor-auto-tuning.svg
    - docs/assets/diagrams/advisor-comparative-selection.svg
    - docs/assets/diagrams/advisor-mcp.svg
    - docs/assets/diagrams/advisor-pipeline-report.svg
    - docs/assets/diagrams/advisor-providers.svg
    - docs/assets/diagrams/advisor-python-api.svg
    - docs/assets/diagrams/sklearn-pipeline-dataflow.svg
    - docs/assets/diagrams/elastic-clustering.svg

decisions:
  - "outlier-detection.svg: kept Magnitude/Shape/Amplitude taxonomy — confirmed correct by docs/analyze/outlier-detection.md (Amplitude = exaggerated peaks/troughs; X[2] *= 2.5 code example)"
  - "elastic-clustering.svg: full redraw (3-panel: mixed-phase input curves + elastic distance heatmap + cluster output families) to method-accurately depict SRVF/Fisher-Rao clustering"
  - "advisor-comparative-selection.svg: winner-box 'fdars-authoritative' label has 25px clearance to right edge in coordinate space — no geometry fix required (audit may have observed font-rendering artifact)"
  - "advisor-mcp.svg: 'stdio' label moved from y=54 (top edge overlap) to y=76 inside diagram; 'handle+/scalars' label moved from x=178 (straddling boundary) to x=152 text-anchor=end on agent side"
  - "sklearn-pipeline-dataflow.svg: Predictor box widened from w=110 to w=128, FPCLDAClassifier label shrunk to font-size=11 to eliminate right-edge overflow"
  - "covariance-functions.svg: both aria-label and <title> now consistently use the HTML entity &#8594; (arrow) to match the visible title"

metrics:
  duration: "~45 minutes"
  completed: "2026-09-02"
  tasks_completed: 5
  tasks_total: 5
  commits: 4

actuals:
  tokens: 78000
  tasks: 5
  commits: 4
---

# Phase 62 Plan 01: SVG Corrections — Analyze / Monitoring / Advisor Summary

Applied accessibility (A11Y-01/02), defect (DEFECT-01/02/03), and STYLE_SPEC conformance (SPEC-01) corrections to all 26 concept diagrams in the analyze / monitoring / advisor / sklearn buckets: universal long-form `<title>+<desc>+aria-labelledby`, one method-accurate full redraw (elastic-clustering), outlier taxonomy confirmed, three minor geometry flags fixed.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 — Tracer | A11Y pattern end-to-end on spm.svg; verified rsvg-convert + SVGO idempotence | c1b0a0e |
| 2 — Analyze A11Y | title+desc+aria-labelledby on 11 analyze diagrams; covariance arrow-entity fix | 023e093 |
| 3 — Monitoring/Advisor/sklearn A11Y + geometry | 13 diagrams: A11Y + advisor-mcp boundary fix, sklearn predictor overflow fix | 70e195c |
| 4 — elastic-clustering redraw | Full method-accurate redraw with 13 curve path elements | d005cbf |
| 5 — Batch gate | All 26 pass A11Y/render/SVGO/scope checks; BATCH_GATE_OK | (verification) |

## Accessibility Work (A11Y-01, A11Y-02)

Applied universal pattern to all 26 diagrams:
- `<title id="t-{id}">` with verbatim `.ttl` title text — resolves A11Y-01 paraphrase mismatches
- `<desc id="d-{id}">` with 1–2 method-accurate sentences — resolves A11Y-02 gap
- `aria-labelledby="t-{id} d-{id}"` on root `<svg>` — full long-form accessible name
- Root `aria-label` updated to match title verbatim (A11Y-01)

All 26 diagrams render clean via `rsvg-convert` and are SVGO-idempotent under `svgo.config.mjs`.

## elastic-clustering.svg Full Redraw (DEFECT-01, DEFECT-03) — SYNC-01 Flag

**Previous state:** 4 bare white rounded-rectangle text boxes (Raw Curves → Elastic Distance Matrix → Distance-Based Clustering → Results) with all-caps inline-styled labels, ~40% canvas fill, zero curve `<path>` elements.

**New design (3-panel, viewBox 0 0 720 300):**
1. **Input panel** (blue): 6 real curve `<path>` elements showing a mixed-phase family — 3 low-amplitude curves (indigo) and 3 high-amplitude curves (orange), all with the same bump shape but varying peak locations (phase variation).
2. **Distance panel** (orange): 6×6 `<rect>` heatmap depicting the elastic amplitude distance matrix from `elastic_self_distance_matrix()` — low distances (blue cells) within each amplitude group, high distances (orange/warm cells) across groups; `hierarchical_cut(D, k=2)` label.
3. **Cluster panel** (green): Two recovered clusters shown as curve families — Cluster 1 (low amplitude, indigo) and Cluster 2 (high amplitude, orange) — demonstrating that phase variation is ignored; only amplitude shape distinguishes the groups.

**Method accuracy:** Correctly depicts the SRVF/Fisher-Rao amplitude distance pipeline (`elastic_self_distance_matrix` → `hierarchical_cut`). Does NOT depict the align "before/after warped waves" motif (that is the align method, not clustering).

**SYNC-01 dependency (Phase 64):** The current thumbnail at `docs/assets/thumb/elastic-clustering.svg` shows aligned before/after wave curves — a content mismatch with the new concept diagram. Phase 64 must regenerate the thumbnail to match the new 3-panel cluster-families concept.

All canonical `<style>` classes used for text (`.ttl`, `.sub`, `.lab`, `.sm`, `.mono`); no inline `style="fill:..."` text overrides.

## outlier-detection.svg — Amplitude Taxonomy Confirmed (DEFECT-03)

The audit flagged "Amplitude Outlier" as potentially incorrect (suggesting "Phase" might be the canonical term). Pre-planning verification against `docs/analyze/outlier-detection.md` confirmed:

- Lines 7–9 of the docs page define: "Amplitude — The curve has exaggerated peaks and troughs"
- The code example uses `X[2] *= 2.5  # amplitude outlier` (scale multiplication)
- The fdars taxonomy is **Magnitude / Shape / Amplitude** (not Phase)

**Decision:** KEEP the three panel labels `Magnitude Outlier / Shape Outlier / Amplitude Outlier` exactly. Only A11Y work was applied. No taxonomy relabel.

## covariance-functions.svg — Arrow-Entity Consistency Fix (A11Y-01)

The audit noted the title uses `&#8594;` (→ HTML entity) while `aria-label` spelled it out as "to". Both now consistently use `&#8594;` in both `aria-label` and `<title>`, eliminating the A11Y-01 mismatch.

## Minor Geometry Fixes (DEFECT-01, DEFECT-02)

| Diagram | Issue | Fix Applied |
|---------|-------|-------------|
| advisor-mcp.svg | "stdio" label at y=54 crowding top edge; "handle+/scalars" label centered at x=178 straddling dashed boundary at x=175 | "stdio" moved to y=76 text-anchor=end at x=163 (inside diagram, left of line); "handle+/scalars" moved to x=152 text-anchor=end (agent side, clear of boundary) |
| sklearn-pipeline-dataflow.svg | "FPCLDAClassifier" mono label overflowing Predictor box right edge (box w=110, right edge at x=698) | Box widened to w=128 (right edge at x=708), label font-size reduced to 11px within .mono sizing; arrow 4→5 endpoint adjusted |
| advisor-comparative-selection.svg | "fdars-authoritative" label reported as slightly clipped at right edge | No change required: coordinate analysis shows text center=542, estimated width ~99px, extending to ~591 vs box right edge at 616 — 25px clearance. Audit note may have been a display-rendering artifact. |

## Scope Compliance

- `git status` shows 0 files changed outside `docs/assets/diagrams/` and `.planning/` — no thumbs, cards, STYLE_SPEC.md, docs prose, or code touched.
- `docs/assets/diagrams/STYLE_SPEC.md` unchanged.
- All changes confined to the 26 files listed in `files_modified`.

## Verification Results

```
TRACER_OK           (Task 1: spm.svg end-to-end)
ANALYZE_A11Y_OK     (Task 2: 11 analyze diagrams)
BATCH3_A11Y_OK      (Task 3: 13 monitoring/advisor/sklearn diagrams)
ELASTIC_OK          (Task 4: elastic-clustering.svg — 13 paths, SVGO-idempotent)
BATCH_GATE_OK       (Task 5: all 26 checked — A11Y, render, SVGO, scope)
```

## Known Stubs

None. All 26 diagrams are complete and method-accurate. No placeholder text or wired-but-empty content.

## Self-Check: PASSED

- All 26 modified SVGs confirmed present on disk
- All 4 task commits confirmed in git log: c1b0a0e, 023e093, 70e195c, d005cbf
- BATCH_GATE_OK verified
- SUMMARY.md written
