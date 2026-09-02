# Phase 64: Cards & Thumbnails Sync + New Coverage - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Audit-driven (60-AUDIT.md §3 cards, §4 thumbs, COVER/SYNC sections are the spec)

<domain>
## Phase Boundary

Bring the derivative assets (8 section cards, 58 gallery thumbnails) in line with the now-corrected concept diagrams, fix decorative-thumb accessibility semantics, and add the audit-identified missing concept diagrams. Delivers SYNC-01, SYNC-02, A11Y-03, COVER-01. STYLE_SPEC.md refresh + whole-site --strict gate + blocking human review are Phase 65.

Runs AFTER phases 61/62/63 (concept diagrams already corrected on main). This phase is executed sequentially on main (not parallel).

</domain>

<decisions>
## Implementation Decisions

### SYNC-01 — thumbnail sync (58 thumbs)
- The audit found only ONE Major thumb drift: **elastic-clustering.svg thumb** (`docs/assets/thumb/elastic-clustering.svg`) depicts the old before/after wave-alignment motif, but the concept was REDRAWN in Phase 62 to show elastic-distance-based clustering of curve families. REDRAW the thumb to a simplified abstraction of the NEW concept (curve families grouped into clusters), consistent with thumb style.
- The other 57 thumbs were scored faithful. The 61/62/63 corrections were mostly A11Y markup additions (no visual content change) plus geometry fixes that preserve each diagram's motif — so the remaining thumbs stay faithful. Re-check is fine, but do NOT regenerate thumbs whose concept motif is unchanged.

### SYNC-02 — section cards (8 cards)
- Only **examples.svg** card scored Minor, and the audit judged it "cosmetic-only — the deliberate abstract gallery motif, not a content mismatch." REVIEW all 8 cards; improve examples.svg only if it clearly increases representativeness WITHOUT losing the deliberate gallery motif. It is acceptable to leave the cards as-is if review confirms they meet the bar — record the decision.

### A11Y-03 — decorative thumbnail semantics
- Gallery thumbnails duplicate the linked title text, so they are decorative. In each section gallery page (`docs/*/index.md`), the gallery `<img class="fdars-gallery-thumb">` uses `alt=""` (correct) — add `aria-hidden="true"` on those gallery `<img>` elements so screen readers do not double-announce the thumbnail alongside its link text. Apply consistently across all section gallery pages that carry `fdars-gallery-thumb`.

### COVER-01 — new coverage (3 new concept diagrams)
- Create 3 NEW hand-authored inline SVG concept diagrams for the sklearn method-family pages that currently lack one:
  - `docs/assets/diagrams/sklearn-transformers.svg` → wire into `docs/sklearn/transformers.md`
  - `docs/assets/diagrams/sklearn-regressors-classifiers.svg` → wire into `docs/sklearn/regressors-classifiers.md`
  - `docs/assets/diagrams/sklearn-clusterers-outliers.svg` → wire into `docs/sklearn/clusterers-outliers.md`
- Each new diagram MUST be method-accurate (depict what that estimator family actually does in `fdars.sklearn` — check the page prose), STYLE_SPEC-conformant (viewBox 0 0 720 300, canonical `<style>` block, palette, stroke weights, panel patterns), and accessible from creation (role="img" + aria-label + long-form `<title>`/`<desc>`/`aria-labelledby`).
- `docs/sklearn/index.md` already has `sklearn-pipeline-dataflow.svg` — do NOT duplicate. `coverage.md` and `gridsearch-example.md` are list/example pages — no concept diagram needed (COVER-01 scoped to the 3 method-family pages only).
- Wire each diagram into its page as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }` following the existing reference convention.

### Method-accuracy (hard gate)
- The 3 new sklearn diagrams and the elastic-clustering thumb redraw must be method-accurate; carry them into the Phase-65 blocking human review checklist.

### Constraints
- Hand-authored inline SVG (locked). Docs-only: no fdars-core/binding/advisor/package changes. Do NOT run the whole-site build (Phase 65) — render changed/new SVGs to PNG (`rsvg-convert`) to verify. Do NOT edit STYLE_SPEC.md (Phase 65). Do NOT re-edit the 90 concept diagrams corrected in 61/62/63.

### Claude's Discretion
- Exact composition of the 3 new sklearn diagrams (panels, labels) and the elastic-clustering thumb redraw, provided method-accuracy + STYLE_SPEC conformance hold.

</decisions>

<code_context>
## Existing Code Insights
- 60-AUDIT.md §3 (cards table), §4 (thumbnail table), and the COVER/SYNC sections — the per-asset findings. READ FIRST.
- Thumbs: `docs/assets/thumb/*.svg` (58). Cards: `docs/assets/cards/*.svg` (8). New concept diagrams go in `docs/assets/diagrams/`.
- Section gallery pages: `docs/*/index.md` reference `../assets/cards/<section>.svg` and `../assets/thumb/<name>.svg` (the A11Y-03 edit target).
- sklearn pages exist: `docs/sklearn/{index,transformers,regressors-classifiers,clusterers-outliers,coverage,gridsearch-example}.md`. transformers/regressors-classifiers/clusterers-outliers currently have 0 diagram refs (COVER-01 targets).
- `docs/assets/diagrams/sklearn-pipeline-dataflow.svg` — the existing sklearn diagram (already in index.md); use as the style/method reference for the 3 new ones.
- `docs/assets/diagrams/STYLE_SPEC.md` — conformance rubric.
- `rsvg-convert` for render-verify.
</code_context>

<specifics>
## Specific Ideas
- The elastic-clustering concept redraw (Phase 62) is the reason its thumb needs re-sync — mirror the new concept's clusters-of-curves motif.
</specifics>

<deferred>
## Deferred Ideas
- STYLE_SPEC.md status/count refresh + whole-site --strict + SVGO/determinism gate + blocking human diagram review → Phase 65.
</deferred>
