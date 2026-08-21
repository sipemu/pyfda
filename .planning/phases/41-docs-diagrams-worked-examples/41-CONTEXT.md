# Phase 41: Docs — Diagrams & Worked Examples - Context

**Gathered:** 2026-08-21
**Status:** Ready for planning
**Mode:** Smart-discuss (autonomous) — grounded in the project's locked docs constraints (hand-authored inline SVG, method-accurate, offline `FDARS_FENCE_OK` fences) + the established v4.0/v5.0 docs-phase pattern; full-autonomy run. NOTE: this phase ends at a BLOCKING human diagram method-accuracy review (DOCS-11) — the orchestrator will pause for the user there.

<domain>
## Phase Boundary

Document the v6.0 bindings (Phases 37–40) to the project's method-accurate standard: new/updated MkDocs pages + hand-authored inline SVG diagrams + runnable OFFLINE worked examples emitting `FDARS_FENCE_OK`, all wired into `mkdocs.yml` nav, with the whole site building `mkdocs build --strict` green (~19 min, real compute) and a blocking human diagram review before the milestone closes.

Requirements: DOCS-08 (Regression), DOCS-09 (FPCA/Classification), DOCS-10 (Depth/Outliers/Interval-Inference), DOCS-11 (advisor aspects.md + nav + strict build + SVGO + human review).

</domain>

<decisions>
## Implementation Decisions

### DOCS-08 — Regression
- New/updated Regression page(s) covering `fdars.regression.concurrent_regression` + `functional_glm` — method-accurate hand-authored inline SVG(s) + a runnable offline `FDARS_FENCE_OK` worked example (small/synthetic or subsampled data). Document the Gamma inverse-link (1/μ) + non-R-comparable AIC caveats surfaced in Phase 37. Wire into the Regression nav section. (Exact page split — new `concurrent-regression.md`/`functional-glm.md` vs folding into existing regression pages — decided at plan time by the established nav pattern.)

### DOCS-09 — FPCA & Classification
- PACE-FPCA page (likely `docs/represent/pace-fpca.md`) — method-accurate SVG showing irregular/sparse observations + recovered eigenfunctions; executed fence using SMALL inline synthetic sparse data (n ≤ 20) built via `fdars.irreg_fdata_from_lists` → `fdars.pace_fpca`.
- elastic-multinomial coverage (fold into `docs/regression/classification.md` or a page) — worked example on phoneme.csv subsampled to 3 classes, m ≤ 64 for fence speed.

### DOCS-10 — Depth / Outliers / Interval Inference
- Fold the 9 new `functional_depth` methods into the existing depth page (`docs/represent/depth-functions.md`) with a short method table + a representative fence.
- Functional-outliers coverage (extend `docs/analyze/outlier-detection.md` or a new page) for the 4 detectors — method-accurate SVG + fence.
- Interval-wise-inference page (likely `docs/inference/interval-inference.md`) for `itp_one_pop`/`itp_two_pop`/`itp_flm` — SVG showing closure-adjusted p-value intervals (CORRECT closure direction) + fence.

### DOCS-11 — Advisor + nav + build + review
- Update the advisor `aspects.md` for the extended `outliers`/`regression`/`classification`/`fpca` diagnostics (Phase 40).
- All new pages wired into `mkdocs.yml` nav; whole-site `mkdocs build --strict` passes offline (exit 0); every new SVG is SVGO-idempotent and determinism-clean.
- BLOCKING human diagram method-accuracy review (rsvg-convert PNG check: depth asymmetry, PACE irregular observations, ITP closure direction) before the milestone closes — the orchestrator PAUSES here for the user.

### Method-accuracy + build constraints (locked)
- Diagrams stay HAND-AUTHORED inline SVG conforming to `STYLE_SPEC.md` (viewBox, inline `<style>` classes, system-ui, role="img"+aria-label); no programmatic generation.
- Fences execute REAL fdars compute offline and MUST emit `FDARS_FENCE_OK`; keep fence data tiny (PACE/ITP synthetic n ≤ 20) so the ~19-min build doesn't blow out (target < ~25 min).
- Build recipe: venv + `PYTHONPATH=scripts` + `DOCS_FAST` for iteration; the full `mkdocs build --strict` (DOCS_FAST unset) is the source-of-truth gate. Use `rsvg-convert` to render new SVGs to PNG for the human review.

### Claude's Discretion
Exact page split / filenames, diagram compositions (within STYLE_SPEC), and fence datasets are at Claude's discretion, grounded in the existing docs pages and the shipped v6.0 API. The human diagram review is NOT at Claude's discretion — it is a blocking user gate.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/inference/functional-inference.md`, `docs/analyze/functional-boxplot.md` — v5.0 precedents for a new capability page (SVG + executed fence + nav).
- `docs/represent/depth-functions.md`, `docs/analyze/outlier-detection.md`, `docs/regression/classification.md` — existing pages to EXTEND.
- `docs/assets/diagrams/*.svg` + `STYLE_SPEC.md` — the hand-authored SVG baseline + style contract; `inference-*.svg`/`functional-boxplot.svg` are recent method-accurate exemplars.
- `scripts/docs_fig.py` (`DOCS_FAST`), `mkdocs.yml` nav, the `markdown-exec` fenced-execution mechanism (`PYTHONPATH=scripts`).
- v4.0 Phase 29 / v5.0 Phase 35 — the direct docs-phase precedents (new pages + SVGs + FDARS_FENCE_OK fences + strict build + human review).

### Established Patterns
- Each new capability: a page with a concept SVG (`![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`) + a runnable offline fence that ends by printing `FDARS_FENCE_OK`; page wired into `mkdocs.yml` nav; SVG passes the SVGO idempotence + determinism CI gate.

### Integration Points
- New/updated `docs/**/*.md`, new `docs/assets/diagrams/*.svg`, `mkdocs.yml` nav, advisor `aspects.md`. No source code changes (docs-only phase).

</code_context>

<specifics>
## Specific Ideas

Mirror v5.0 Phase 35 exactly. Keep executed fences tiny (synthetic sparse for PACE, subsampled phoneme for multinomial, small n for ITP). Render every new SVG to PNG with `rsvg-convert` for the self-review pass before surfacing the blocking human review.

</specifics>

<deferred>
## Deferred Ideas

- `fdars.plot.plot_functional_boxplot()` helper (PLOT-01) — future milestone, not docs.
- Dedicated PACE/multinomial advisor aspects (PACE-ADV/MULTINOM-ADV) — deferred at Phase 40.

</deferred>
