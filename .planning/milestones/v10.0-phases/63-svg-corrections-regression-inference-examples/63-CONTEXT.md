# Phase 63: SVG Corrections — regression / inference / examples - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Audit-driven (the 60-AUDIT.md worklist is the spec)

<domain>
## Phase Boundary

Correct the 40 concept diagrams in the regression/ + inference/ + examples/ buckets on the defect, accessibility, and STYLE_SPEC axes, per `.planning/phases/60-diagram-quality-audit/60-AUDIT.md` (§1 concept table + §5 Phase-63 worklist). Completes the concept-diagram correction sweep (all 90 across phases 61+62+63). Delivers DEFECT-01/02/03, A11Y-01, A11Y-02, SPEC-01 for THIS bucket. SYNC/COVER = Phase 64; STYLE_SPEC.md refresh + whole-site gate + human review = Phase 65.

**The 40 diagrams (all in `docs/assets/diagrams/`):**
- regression (15): scalar-on-function, function-on-scalar, classification, elastic-regression, elastic-multinomial, scalar-on-shape, concurrent-regression, functional-glm, cross-validation, regression-diagnostics, uncertainty-quantification, explainability, conformal-prediction, conformal-classification, robust-regression
- inference (4): inference-anova, inference-permutation-test, inference-scb, itp-interval-inference
- examples (21): ex-sonar-tsrvf, ex-canadian-weather, ex-canadian-precipitation, ex-canadian-depth-centrality, ex-canadian-function-on-scalar, ex-canadian-seasonal, ex-andrews-wine, ex-andrews-wine-intro, ex-andrews-wine-clustering, ex-andrews-wine-qc, ex-biopharma-monitoring, ex-cross-validation, ex-explainability-regions, ex-functional-outlier-workflow, ex-growth-alignment, ex-inline-monitoring, ex-phoneme-shape, ex-tecator-conformal-coverage, ex-tecator-monitoring, ex-tecator-regression, ex-tolerance-vs-conformal

</domain>

<decisions>
## Implementation Decisions

### Design/geometry + layout (DEFECT-01, DEFECT-02) — the 4 Major fixes are the priority
- **concurrent-regression.svg** (Major): the inter-panel transition label ("concurrent"/"regression" + arrow) overflows both panel borders (text ~±60px in a 44px gap). FIX: widen the gap, reduce font, or reposition the label outside the overlap zone so it is legible and does not overlap panels.
- **ex-canadian-precipitation.svg** (Major): rightmost "Geographic drivers" panel text is clipped at the right viewBox edge (x=720). FIX: widen the panel / reduce font / reduce text density so no text is clipped.
- **ex-canadian-depth-centrality.svg** (Major): rightmost "Ranked centrality" panel text clipped at the right edge. FIX: shrink font / narrow text / add line breaks so labels are fully visible.
- **ex-canadian-seasonal.svg** (Major): bottom-right result badge ("summer peak day constant; level rise") truncated at the right edge. FIX: shorten the label or reduce font so the full conclusion is visible.
- Any other Minor design/geometry flags in §1 for these 40 diagrams: fix if clearly improving (clipping, overflow, overlap, misaligned/mismatched lines); else leave.

### Accessibility (A11Y-01, A11Y-02) — every diagram in the bucket
- **A11Y-02:** add long-form `<title>` + `<desc>` wired via `aria-labelledby` on the root `<svg>` (universal gap). `<desc>` = 1–2 sentences on what the diagram depicts + the method/workflow it illustrates.
- **A11Y-01:** fix flagged `aria-label` paraphrase mismatches so the root `aria-label` matches the visible `.ttl` title text.

### Method-accuracy (DEFECT-03) — hard gate
- Every correction preserves/improves method-accuracy; a fix must never misdepict the method or the worked example it summarizes. The text-clipping fixes are layout-only (do not change meaning) — but re-wording a truncated label must keep the same method-accurate conclusion. When unsure, stay conservative and note for Phase 65 human review.

### STYLE_SPEC conformance (SPEC-01)
- Keep conformant to the CURRENT `docs/assets/diagrams/STYLE_SPEC.md`; audit found 0 STYLE_SPEC defects here, so mostly "do not regress." NO palette/typography change. Do NOT edit STYLE_SPEC.md.

### Constraints
- Hand-authored inline SVG (locked); edit source by hand. Docs-only; no whole-site build here (Phase 65) — render changed SVGs to PNG (`rsvg-convert`) and visually confirm each Major fix actually resolves the clipping/overflow. Keep SVGO-idempotent.

### Claude's Discretion
- `<desc>` wording, id naming, and the exact layout technique for each Major fix (widen vs shrink vs reflow) are at the executor's discretion, provided the render shows no clipping/overflow and method-accuracy holds.

</decisions>

<code_context>
## Existing Code Insights
- 60-AUDIT.md §1 (regression/inference/examples rows) + §5 Phase-63 worklist — READ FIRST. The 4 Major rows carry exact coordinates/line refs.
- `docs/assets/diagrams/STYLE_SPEC.md` — conformance + accessibility pattern.
- The examples diagrams summarize worked-example pages under `docs/examples/*.md` — check those for the correct conclusions when re-wording truncated labels.
- `rsvg-convert` for render-verify (critical here — the 4 Major defects are only visible in the render).
</code_context>

<specifics>
## Specific Ideas
- Edits ONLY the 40 listed SVGs under `docs/assets/diagrams/`. Does NOT touch thumbs/cards (Phase 64), STYLE_SPEC.md (Phase 65), or docs prose.
- This is the largest bucket (40) and carries 4 of the milestone's 5 Major defects — prioritize the Major fixes and render-verify them explicitly.
</specifics>

<deferred>
## Deferred Ideas
- Thumb re-sync for any redrawn diagram → Phase 64 (SYNC-01).
- STYLE_SPEC.md refresh → Phase 65 (SPEC-02).
</deferred>
