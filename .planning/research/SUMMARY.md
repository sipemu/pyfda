# Project Research Summary

**Project:** pyfda — Documentation Overhaul (SVG diagrams + example pages)
**Domain:** Technical/scientific library documentation — hand-authored SVG concept diagrams + reproducible code-driven worked examples (MkDocs Material)
**Researched:** 2026-08-07
**Confidence:** MEDIUM (stack/features MEDIUM from web + inspection; architecture/pitfalls HIGH from direct source analysis of all 43 SVGs, scripts, Makefile, mkdocs.yml)

## Executive Summary

pyfda's `fdars` documentation is already a mature MkDocs Material site with a working figure pipeline (`markdown-exec` + `scripts/docs_fig.py`), ~43 hand-authored inline SVG diagrams, and 17 worked-example pages. The overhaul is therefore **not** a rebuild — it is a consistency-and-accuracy pass over an existing, largely sound foundation. Research strongly converges on a single conclusion: **35 of 43 diagrams already share a de-facto baseline** (`viewBox="0 0 720 300"`, an inline `<style>` block with five CSS classes (`.ttl`, `.sub`, `.lab`, `.sm`, `.mono`), `role="img"` + `aria-label`), so the highest-leverage first move is to *formalize that baseline into a written style spec plus a machine linter* before touching any diagram.

The recommended approach is additive tooling on top of the current stack: SVGO 3.3.4 (configured to preserve the `<style>` block and accessibility attributes) as a consistency linter; a one-line `svg.hashsalt` fix in `docs_fig.py` for deterministic figure output; `pymdownx.snippets` to de-duplicate dataset-loading preambles; and `pytest-markdown-docs` to test example code fences. Diagrams stay hand-authored inline SVG per project decision — Mermaid/D2/Inkscape are explicitly rejected.

The two dominant risks are **diagram inaccuracy** and **example rot**, and research found concrete, already-present instances of both. Two SVGs (`spm.svg`, `basis-representation.svg`) still contain R-era content (`extendr` branding, `autoplot()`, R function names); `smoothing.svg` has a coordinate bug where the "smoothed" panel reuses the noisy path; and `conformal-prediction.svg` depicts a scalar `ŷ ± const` interval when `fdars` conformal functional regression produces a time-varying band `ŷ(t) ± q(t)`. On the examples side, the existing `check_docs_figures.py` catches hard exceptions but misses silent wrong-output from changed API defaults (exactly the `lambda_=1.0→0.0` class of bug from issue #37). These findings directly shape phase ordering: audit + guardrails first, then accuracy sweeps, then examples.

## Key Findings

### Recommended Stack

All additive to the existing MkDocs Material 9.7.7 / markdown-exec 1.12.3 / KaTeX foundation (no framework changes). See `research/STACK.md`.

**Core technologies:**
- **SVGO 3.3.4** (not 4.x): lossless SVG lint/optimize — configured with `inlineStyles/mergeStyles/minifyStyles/cleanupIds/removeDesc/removeViewBox: false` to preserve the hand-authored `<style>` block, IDs, and accessibility. v4 changed the plugin API (June 2026) and is avoided.
- **`svg.hashsalt` rcParam** in `docs_fig.py` (`mpl.rcParams["svg.hashsalt"]="fdars-docs"`): makes matplotlib SVG clip-path IDs deterministic so built output diffs are meaningful and CI is stable — a one-line, high-value fix.
- **pytest-markdown-docs 0.9.2**: runs `.md` python fences as tests with `continuation` (shared-state multi-block examples) + globals injection via `conftest.py`. Complements (does not replace) `check_docs_figures.py`, which still covers `exec="1"` blocks.
- **pymdownx.snippets** (add to `mkdocs.yml`): factor the repeated 8–10 line dataset-loading preamble into `docs/includes/` to cut duplication across the Canadian-weather / Tecator / Andrews example families.
- **STYLE_SPEC.md** (`docs/assets/diagrams/`): the shared token layer as a written doc with a copy-paste `<style>` block — because external CSS cannot pierce the SVG boundary when diagrams are referenced as `<img src>`.

### Expected Features

From `research/FEATURES.md`. A diagram *teaches* (not decorates) when it shows a transformation, a concrete before/after, or spatial relationships prose can't encode.

**Must have (table stakes):**
- Problem → Data → Method → Interpretation structure on every worked example (best pages already follow it; risk is inconsistency across the other 15)
- Accurate concept diagrams for the FDA methods that genuinely need them
- Every example reproducible and runnable against the current API, cross-linked to the API reference

**Should have (differentiators):**
- Clear visual explanations for the seven methods that most need them: **elastic alignment (phase vs amplitude split), FPCA (eigenfunction effect), basis representation (weighted sum of bases), scalar-on-function regression (coefficient curve β(t)), depth/outlier detection (centrality ordering), SPM monitoring (Phase I/II), conformal prediction (functional band vs scalar CI)**
- Five new worked examples for under-documented capabilities: conformal coverage guarantee, function-on-scalar regression, outlier-detection workflow, tolerance-bands vs conformal comparison, functional depth centrality

**Defer / anti-features:**
- Logo-style abstract SVGs (shapes, no data), over-long "reference-dump" examples, interactive widgets (plotly/bokeh), dark-mode SVG variants — all out of scope or maintenance debt

### Architecture Approach

From `research/ARCHITECTURE.md`. The design system already exists implicitly; the work is to make it explicit and enforce it. The figure pipeline (`docs_fig.py` rcParams, `docs_data.py` 7 loaders with a `(argvals, X, meta)` contract, post-build `check_docs_figures.py`) is production-quality as-is.

**Major components:**
1. **Style spec (tokens)** — `STYLE_SPEC.md` + canonical `<style>` block; the shared ruler every diagram is measured against
2. **Individual diagrams** — 43 hand-authored SVGs; 35 conform, 8–9 legacy outliers (`clustering`, `depth-functions`, `spm`, `gmm-clustering`, `outlier-detection`, `seasonal-analysis`, `covariance-functions`, `elastic-clustering`, `ex-sonar-tsrvf`) use off-spec fonts/viewBox/palette
3. **Figure/example pipeline** — datasets → `docs_fig`/`docs_data` → build-time SVG figures → pages; gated by `mkdocs build --strict` + `check_docs_figures.py` (post-build, not pre-build — exec blocks fail silently otherwise)

### Critical Pitfalls

Top items from `research/PITFALLS.md` (all HIGH confidence — observed directly in source):

1. **R-era content in diagrams** (`spm.svg`, `basis-representation.svg`) — grep for `extendr`/`autoplot`/R identifiers in the audit; highest-priority accuracy fixes.
2. **Method-inaccurate diagrams** — `smoothing.svg` (smoothed panel reuses noisy coordinates); `conformal-prediction.svg` (scalar interval instead of functional band `ŷ(t) ± q(t)`). Validate each diagram against the actual method semantics on the rendered page.
3. **Consistency drift with no enforcement** — the two-convention split (modern `<style>` vs legacy inline `font-family`) will spread without a machine linter; land SVGO + STYLE_SPEC.md *before* revising any diagram.
4. **Silent example rot** — `check_docs_figures.py` misses wrong-output from changed API defaults (the issue-#37 `lambda_` pattern), empty figures, and dict-key drift in result wrappers; add value assertions + dict-key checks to example UAT.
5. **Slow builds discourage local verification** — repeated expensive calls (`karcher_mean(max_iter=25)` ×4 in `growth-alignment.md`, `equivalence_test(nb=500)`); add a `DOCS_FAST` gate and reduce iteration counts in exec blocks.

## Implications for Roadmap

Research forces a dependency-ordered structure. Granularity is **Fine**, so section sweeps split into their own phases.

### Phase 1: Foundation — Style Spec + Guardrails
**Rationale:** Nothing else can be measured or kept consistent without a written spec and a linter; determinism + test tooling must exist before sweeps.
**Delivers:** `docs/assets/diagrams/STYLE_SPEC.md`; `svgo.config.mjs`; `svg.hashsalt` in `docs_fig.py`; `pymdownx.snippets` in `mkdocs.yml`; `pytest-markdown-docs` + `conftest.py` globals; `DOCS_FAST` build gate; frozen docs deps (NumPy pin).
**Avoids:** consistency drift, non-deterministic figures, slow builds.

### Phase 2: Nav + Reference-API Audit
**Rationale:** User chose to derive the coverage/new-example list from a nav + API audit; gap detection must precede sweeps.
**Delivers:** cross-section diagram map (page → diagram, accurate/inconsistent/missing), grep report for R-era identifiers, ranked coverage-gap + new-example list for user selection.
**Addresses:** coverage gaps; **Avoids:** guessing scope.

### Phases 3–8: Section-by-Section Diagram Sweeps (with per-section review gate)
**Rationale:** Diagrams are the priority; sweep highest-risk methods first; SVGO green before each section starts. Order: **learn → represent → align → analyze → regression → monitoring** (regression is largest ~12 pages and most likely to surface accuracy issues).
**Delivers:** each section's diagrams brought to STYLE_SPEC.md and made method-accurate; legacy outliers migrated; user reviews the built site per section before the next begins.
**Uses:** SVGO lint, STYLE_SPEC.md. **Implements:** the diagram design-system component.

### Phase 9 (last): Examples Sweep
**Rationale:** Deliberately last — running example code may reveal API issues that must be fixed before figures finalize.
**Delivers:** every `docs/examples/*.md` correct against current API (pytest-markdown-docs), enriched narrative, improved figures/captions, and the 5 new worked examples.
**Avoids:** example rot (value + dict-key assertions, two-consecutive-build determinism as UAT).

### Phase Ordering Rationale
- Style spec + linter are a hard prerequisite for every diagram sweep (consistency ruler must exist first).
- Audit precedes sweeps so scope is evidence-based, not guessed.
- Diagrams before examples (user priority) and because example fixes may depend on nothing, but example execution may surface API bugs best handled after diagrams are settled.
- Section sweeps run serially with review gates matching the user's per-section approval preference.

### Research Flags
Phases likely needing deeper research during planning:
- **Regression + Monitoring diagram sweeps:** method semantics (scalar-on-function β(t), conformal functional bands, SPM Phase I/II control limits) must be verified against `fdars-core` behavior to draw them correctly.
- **Examples sweep:** confirm `pytest-markdown-docs` handles multi-block narrative state on a real page before adopting it as the CI pattern.

Phases with standard patterns (can skip research-phase):
- **Foundation + Audit:** mechanical/tooling; no external research needed.
- **learn/represent/align/analyze diagram sweeps:** established concepts, baseline already defined.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core tool versions verified vs live PyPI/npm; SVGO/pytest config details LOW (not yet run against the actual files) |
| Features | MEDIUM | Cross-checked vs scikit-fda/scikit-learn/statsmodels; per-method priority needs audit to confirm |
| Architecture | HIGH | All 43 SVGs + scripts + Makefile + mkdocs.yml inspected directly |
| Pitfalls | HIGH | Specific accuracy bugs observable in SVG source; example-rot patterns confirmed in CI scripts + issue #37 history |

**Overall confidence:** MEDIUM–HIGH (implementation ground truth is strong; some tool-config specifics need a smoke test in Phase 1).

### Gaps to Address
- **SVGO config vs real files:** validate `cleanupIds:false` / `convertTransform:false` against the actual SVGs in Phase 1 (may be relaxable for extra savings).
- **pytest-markdown-docs multi-block state:** smoke-test on one narrative example page before committing to it as the CI pattern.
- **Which of the 50 SVGs are inaccurate vs merely inconsistent:** resolved by the Phase 2 audit (requires rendering each page).
- **Editorial scope questions:** `sonar-tsrvf` vs `phoneme-shape` overlap; whether the 4-page Andrews-wine series stays or consolidates — decide during the examples phase.

## Sources

### Primary (HIGH confidence)
- Project codebase — all 43 `docs/assets/diagrams/*.svg`, `scripts/docs_fig.py`, `scripts/docs_data.py`, `scripts/check_docs_figures.py`, `Makefile`, `mkdocs.yml`, `docs/hooks.py` (direct inspection; ground truth for baseline, outliers, and accuracy bugs)
- `.planning/codebase/` map (ARCHITECTURE, STRUCTURE, CONCERNS) and issue #37 / MEMORY history for the `lambda_` example-rot pattern

### Secondary (MEDIUM confidence)
- Comparative docs of scikit-fda, scikit-learn, statsmodels, GPyTorch — example structure and diagram conventions
- Data/ink-ratio principle — teaching-vs-decorative diagram distinction

### Tertiary (LOW confidence, validate in Phase 1)
- PyPI/npm/GitHub version checks: markdown-exec 1.12.3, mkdocs-material 9.7.7, SVGO 3.3.4/4.0.2, pytest-markdown-docs 0.9.2, matplotlib 3.11.1
- SVGO preset-default plugin docs; matplotlib `svg.hashsalt` changelog; Deque/WCAG 1.1.1 SVG accessibility guidance

---
*Research completed: 2026-08-07*
*Ready for roadmap: yes*
