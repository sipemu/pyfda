# Requirements: pyfda — Documentation Overhaul

**Defined:** 2026-08-07
**Core Value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### Foundation (tooling & guardrails)

- [x] **FND-01**: A written SVG style spec at `docs/assets/diagrams/STYLE_SPEC.md` codifies the palette, typography classes (`.ttl` `.sub` `.lab` `.sm` `.mono`), stroke weights, the fixed viewBox width (720) and the allowed heights, and a canonical copy-paste `<style>` block
- [x] **FND-02**: An SVGO config (`svgo.config.mjs`) losslessly lints/optimizes diagrams while preserving the `<style>` block, IDs, `<desc>`, `viewBox`, and `role`/`aria-label` accessibility attributes
- [x] **FND-03**: Built figures are deterministic — `docs_fig.py` sets `svg.hashsalt` and stochastic example blocks seed their RNG — so two consecutive builds produce byte-identical SVG output
- [x] **FND-04**: `pymdownx.snippets` is enabled and shared dataset-loading preambles are factored into `docs/includes/`, removing duplicated CSV-loading blocks across example pages
- [x] **FND-05**: Example code fences are runnable as tests via `pytest-markdown-docs` with a `conftest.py` globals hook exposing `np`, `plt`, and `fdars`
- [x] **FND-06**: A fast docs-build path (`DOCS_FAST`) lowers expensive iteration counts so authors can verify pages locally without slow full rebuilds

### Audit (scope derivation)

- [x] **AUD-01**: A nav + reference-API audit produces a page→diagram map that classifies every diagram as accurate, inconsistent, or missing
- [x] **AUD-02**: The audit greps for and flags all R-era content (`extendr`, `autoplot`, R-specific identifiers) across diagrams and prose
- [x] **AUD-03**: The audit produces a ranked, user-selectable list of diagram coverage gaps and candidate new worked examples

### Diagram sweeps (per section — priority)

Each section requirement means: every diagram in that section conforms to `STYLE_SPEC.md`, is method-accurate on the rendered page, has any legacy-outlier SVG migrated to the standard viewBox/style/palette, and closes that section's approved coverage gaps. Reviewed on the built site before the next section starts.

- [x] **DIA-01**: `learn/` diagrams conform and are accurate (introduction, smoothing — fix the noisy/smoothed coordinate reuse bug, derivatives, irregular-sampling, simulation, custom-plotting)
- [x] **DIA-02**: `represent/` diagrams conform and are accurate (basis-representation — remove R-era `extendr`/`autoplot` content, FPCA, andrews-transformation, distance-metrics, elastic-fpca)
- [ ] **DIA-03**: `align/` diagrams conform and are accurate (elastic-alignment phase-vs-amplitude split, landmark-registration, tsrvf, shape-analysis, alignment-comparison, advanced-alignment)
- [ ] **DIA-04**: `analyze/` diagrams conform and are accurate (clustering, depth-functions, outlier-detection, tolerance-bands, covariance-functions, seasonal-analysis, equivalence-testing, gmm-clustering, elastic-clustering — migrate legacy outliers)
- [ ] **DIA-05**: `regression/` diagrams conform and are accurate (scalar-on-function β(t) coefficient curve, function-on-scalar, robust-regression, conformal-prediction — redraw as a functional band ŷ(t) ± q(t), conformal-classification, classification, regression-diagnostics, cross-validation)
- [ ] **DIA-06**: `monitoring/` diagrams conform and are accurate (spm — remove R-era content, redraw Phase I/II control limits; advanced-spm; profile-partial-monitoring)

### Example sweeps (secondary)

- [ ] **EX-01**: Every `docs/examples/*.md` runs correctly against the current `fdars` API — `pytest-markdown-docs` passes, `check_docs_figures.py` is clean, and value/dict-key assertions guard against silent output drift
- [ ] **EX-02**: Example narratives follow Problem → Data → Method → Interpretation with genuine interpretation, not just code
- [ ] **EX-03**: Example output figures are improved for clarity (styling, captions, Code/Output tabs) and cross-linked to the API reference
- [ ] **EX-04**: Five new worked examples cover under-documented capabilities: conformal coverage guarantee, function-on-scalar regression, outlier-detection workflow, tolerance-bands vs conformal comparison, and functional depth centrality ordering

## v2 Requirements

Acknowledged but deferred; not in this milestone's roadmap.

### Accessibility

- **A11Y-01**: Long-form `<title>`/`<desc>` + `aria-labelledby` descriptions for the most complex diagrams, validated with a screen reader

### Examples

- **EX2-01**: Editorial consolidation decisions (e.g. `sonar-tsrvf` vs `phoneme-shape` overlap; whether the 4-page Andrews-wine series stays split or merges)

## Out of Scope

Explicitly excluded to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Programmatic/tool-generated diagrams (Mermaid, D2, Inkscape, matplotlib-drawn concept SVGs) | Project decision: diagrams stay hand-authored inline SVG for conceptual control |
| Dark-mode SVG variants | Out of scope for this milestone; light-mode renders acceptably |
| Library/runtime changes to `fdars`/`fdars-core` | This is a documentation milestone; code changes only if an example exposes a genuine binding bug |
| R-parity feature work | Tracked separately in `PARITY_PLAN.md` |
| Interactive widgets (plotly/bokeh) in docs | Maintenance debt; static figures suffice and stay reproducible |
| Decorative-only "logo" diagrams | Anti-feature: diagrams must teach (show a transformation/before-after/spatial relationship), not decorate |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 1 | Complete |
| FND-02 | Phase 1 | Complete |
| FND-03 | Phase 1 | Complete |
| FND-04 | Phase 1 | Complete |
| FND-05 | Phase 1 | Complete |
| FND-06 | Phase 1 | Complete |
| AUD-01 | Phase 2 | Complete |
| AUD-02 | Phase 2 | Complete |
| AUD-03 | Phase 2 | Complete |
| DIA-01 | Phase 3 | Complete |
| DIA-02 | Phase 4 | Complete |
| DIA-03 | Phase 5 | Pending |
| DIA-04 | Phase 6 | Pending |
| DIA-05 | Phase 7 | Pending |
| DIA-06 | Phase 8 | Pending |
| EX-01 | Phase 9 | Pending |
| EX-02 | Phase 9 | Pending |
| EX-03 | Phase 9 | Pending |
| EX-04 | Phase 9 | Pending |

**Coverage:**

- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-07*
*Last updated: 2026-08-07 after roadmap creation (all 19 requirements mapped)*
