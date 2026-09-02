# Phase 62: SVG Corrections — analyze / monitoring / advisor - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Audit-driven (the 60-AUDIT.md worklist is the spec)

<domain>
## Phase Boundary

Correct the 26 concept diagrams in the analyze/ + monitoring/ + advisor/ buckets (plus the sklearn edge-case diagram) on the defect, accessibility, and STYLE_SPEC axes, per `.planning/phases/60-diagram-quality-audit/60-AUDIT.md` (§1 concept table + §5 Phase-62 worklist). Delivers DEFECT-01/02/03, A11Y-01, A11Y-02, SPEC-01 for THIS bucket only. SYNC/COVER = Phase 64; STYLE_SPEC.md refresh + whole-site gate + human review = Phase 65.

**The 26 diagrams (all in `docs/assets/diagrams/`):**
- analyze (12): tolerance-bands, clustering, gmm-clustering, elastic-clustering, outlier-detection, functional-outliers, functional-boxplot, seasonal-analysis, equivalence-testing, covariance-functions, scoring-metrics, functional-statistics
- monitoring (3): spm, advanced-spm, profile-partial-monitoring
- advisor (10): advisor-loop, advisor-grounding-invariant, advisor-aspects, advisor-agent-skill, advisor-auto-tuning, advisor-comparative-selection, advisor-mcp, advisor-pipeline-report, advisor-providers, advisor-python-api
- sklearn edge case (1): sklearn-pipeline-dataflow

</domain>

<decisions>
## Implementation Decisions

### Accessibility (A11Y-01, A11Y-02) — every diagram in the bucket
- **A11Y-02:** add long-form `<title>` + `<desc>` wired via `aria-labelledby` on the root `<svg>` (universal gap). `<desc>` = 1–2 sentences on what the diagram depicts + the method it illustrates.
- **A11Y-01:** fix flagged `aria-label` paraphrase mismatches so the root `aria-label` matches the visible `.ttl` title text.

### Design/geometry + layout (DEFECT-01, DEFECT-02) — where flagged
- **elastic-clustering.svg** (Major): the concept diagram is a bare text-flow box chart (Raw Curves → Elastic Distance Matrix → Distance-Based Clustering → Results) with NO curve imagery, while its thumbnail depicts elastic-alignment wave curves — a content mismatch (the most significant drift in the set). FIX: bring the concept diagram to the bar — make it clearly depict the elastic-clustering METHOD (elastic pairwise distances → distance-based clustering of curves). A redraw that shows curve families being grouped is appropriate; keep it method-accurate to how fdars elastic clustering works (elastic/Fisher-Rao distance matrix → clustering). NOTE: the corresponding THUMB re-sync is Phase 64 (SYNC-01) — this phase fixes the CONCEPT diagram; record the redraw so Phase 64 can mirror it.
- **outlier-detection.svg** (method-accuracy FLAG): the diagram labels an "Amplitude Outlier" type; the canonical fdars taxonomy is Magnitude / Shape / Phase. Verify the correct term against the fdars outlier taxonomy and relabel to the method-accurate term (likely "Phase" rather than "Amplitude") if confirmed. If ambiguous, keep conservative and flag for Phase 65 human review.
- Any other Minor design/geometry flags in §1 for these 26 diagrams: fix if clearly improving; else leave.

### Method-accuracy (DEFECT-03) — hard gate
- Every correction preserves/improves method-accuracy; a fix must never misdepict the method. The elastic-clustering redraw and the outlier-detection taxonomy relabel are method-accuracy-sensitive — verify against fdars behavior / the corresponding docs page prose. When unsure, stay conservative and note for Phase 65 human review.

### STYLE_SPEC conformance (SPEC-01)
- Keep conformant to the CURRENT `docs/assets/diagrams/STYLE_SPEC.md`; audit found 0 STYLE_SPEC defects here, so mostly "do not regress." NO palette/typography change. Do NOT edit STYLE_SPEC.md.

### Constraints
- Hand-authored inline SVG (locked); edit source by hand. Docs-only; no whole-site build here (Phase 65) — render changed SVGs to PNG (`rsvg-convert`) and visually confirm. Keep SVGO-idempotent.

### Claude's Discretion
- `<desc>` wording, id naming, and how elastic-clustering is redrawn (as long as it method-accurately depicts elastic-distance-based clustering and reaches the quality bar) are at the executor's discretion.

</decisions>

<code_context>
## Existing Code Insights
- 60-AUDIT.md §1 (analyze/monitoring/advisor/sklearn rows) + §5 Phase-62 worklist — READ FIRST.
- `docs/assets/diagrams/STYLE_SPEC.md` — conformance + accessibility pattern.
- The docs pages for these methods (e.g. `docs/analyze/*.md`, `docs/monitoring/*.md`, advisor pages) carry the method prose to check taxonomy/labels against.
- `rsvg-convert` for render-verify.
</code_context>

<specifics>
## Specific Ideas
- Edits ONLY the 26 listed SVGs under `docs/assets/diagrams/`. Does NOT touch thumbs/cards (Phase 64), STYLE_SPEC.md (Phase 65), or docs prose.
</specifics>

<deferred>
## Deferred Ideas
- elastic-clustering THUMB re-sync after the concept redraw → Phase 64 (SYNC-01, flagged Major drift).
- STYLE_SPEC.md refresh → Phase 65 (SPEC-02).
</deferred>
