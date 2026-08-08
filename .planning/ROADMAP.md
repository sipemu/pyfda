# Roadmap: pyfda — Documentation Overhaul

## Overview

This milestone brings the `fdars` MkDocs site's ~43 hand-authored SVG diagrams and 17 example pages to a consistently high, method-accurate standard. Work proceeds in three stages: first, establish the tooling and guardrails (style spec, linter, determinism, test harness) that everything else depends on; second, audit the full nav to derive an evidence-based list of diagram gaps and new-example candidates; third, sweep each documentation section's diagrams in priority order (learn → represent → align → analyze → regression → monitoring), with a user review gate per section before the next begins; and finally, sweep the examples section last so that API issues surfaced by running example code can be caught and corrected after diagrams are settled.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - Establish SVG style spec, SVGO linter, deterministic builds, snippets, pytest-markdown-docs, and DOCS_FAST gate (completed 2026-08-07)
- [x] **Phase 2: Audit** - Nav + reference-API audit that produces the diagram coverage map and ranked gap list (completed 2026-08-07)
- [x] **Phase 3: learn/ Diagrams** - Sweep learn/ section: conform, fix coordinate bug, and close coverage gaps (completed 2026-08-08)
- [x] **Phase 4: represent/ Diagrams** - Sweep represent/ section: remove R-era content, conform, close gaps (completed 2026-08-08)
- [x] **Phase 5: align/ Diagrams** - Sweep align/ section: conform, fix phase-vs-amplitude split, close gaps (completed 2026-08-08)
- [x] **Phase 6: analyze/ Diagrams** - Sweep analyze/ section: migrate legacy outliers, conform, close gaps (completed 2026-08-08)
- [x] **Phase 7: regression/ Diagrams** - Sweep regression/ section: redraw conformal band, conform, close gaps (completed 2026-08-08)
- [x] **Phase 8: monitoring/ Diagrams** - Sweep monitoring/ section: remove R-era content, redraw control limits, close gaps (completed 2026-08-08)
- [ ] **Phase 9: Examples Sweep** - All example pages correct against current API, enriched narrative, improved figures, five new examples

## Phase Details

### Phase 1: Foundation

**Goal**: The tooling and guardrails that every subsequent diagram sweep depends on are in place and verified working
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: FND-01, FND-02, FND-03, FND-04, FND-05, FND-06
**Success Criteria** (what must be TRUE):

  1. `docs/assets/diagrams/STYLE_SPEC.md` exists and documents the palette, the five CSS classes (`.ttl` `.sub` `.lab` `.sm` `.mono`), stroke weights, viewBox width 720, allowed heights, and contains a copy-paste `<style>` block
  2. Running `svgo --config svgo.config.mjs` against any existing conforming diagram produces no errors and leaves the `<style>` block, IDs, `<desc>`, `viewBox`, and `role`/`aria-label` intact
  3. Two consecutive `mkdocs build` runs produce byte-identical SVG output from `docs_fig.py` exec blocks
  4. Dataset-loading preambles are factored into `docs/includes/` snippets and `pymdownx.snippets` is enabled in `mkdocs.yml`, so example pages no longer repeat the CSV-loading block inline
  5. `pytest --co -q` discovers example code fences via `pytest-markdown-docs`, and a `conftest.py` globals hook exposes `np`, `plt`, and `fdars` to fence execution
  6. Setting `DOCS_FAST=1` causes the docs build to reduce expensive iteration counts (e.g. `max_iter`, `nb`) so a local verification completes materially faster than the full build

**Plans**: 4/4 plans executed
**Wave 1**

- [x] 01-01-PLAN.md — TRACER: STYLE_SPEC.md + svgo.config.mjs + SVGO lint gate proven end-to-end through CI (FND-01, FND-02)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — svg.hashsalt determinism + DOCS_FAST fast() helper in docs_fig.py (FND-03, FND-06)
- [x] 01-03-PLAN.md — pymdownx.snippets + docs/includes/ dataset preambles (FND-04)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-04-PLAN.md — pytest-markdown-docs conftest harness + one-page CI doc-test gate (FND-05)

### Phase 2: Audit

**Goal**: An evidence-based, user-selectable list of diagram coverage gaps and new-example candidates is produced from a systematic nav + API sweep
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: AUD-01, AUD-02, AUD-03
**Success Criteria** (what must be TRUE):

  1. A written audit document maps every page in the nav to its diagram(s) and classifies each as accurate, inconsistent, or missing — no page is omitted
  2. The audit document contains a grep report that flags all R-era content (`extendr`, `autoplot`, R-specific identifiers) found in diagrams and prose, with file locations
  3. The audit produces a ranked list of diagram coverage gaps and new-example candidates that the user can select from before Phase 3 begins

**Plans**: 3/3 plans executed

**Wave 1**

- [x] 02-01-PLAN.md — TRACER: scaffold 02-AUDIT.md (3 sections, taxonomy, ID schemes) + audit learn/ end-to-end (AUD-01/02/03)

**Wave 2** *(blocked on Wave 1)*

- [x] 02-02-PLAN.md — coverage rows for the remaining 5 method sections (represent/align/analyze/regression/monitoring); AUD-01 completeness (AUD-01)

**Wave 3** *(blocked on Wave 2)*

- [x] 02-03-PLAN.md — full-scope R-era grep report + reference-API sweep + ranked user-selectable GAP/EX list (AUD-02, AUD-03)

### Phase 3: learn/ Diagrams

**Goal**: Every diagram in the learn/ section conforms to STYLE_SPEC.md and faithfully depicts what the method actually does
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: DIA-01
**Success Criteria** (what must be TRUE):

  1. All learn/ SVG diagrams pass SVGO lint against `svgo.config.mjs` with zero errors
  2. The smoothing diagram's "smoothed" panel uses the corrected smoothed path, not the reused noisy coordinates — verified on the built site
  3. Every learn/ page that warrants a diagram (introduction, smoothing, derivatives, irregular-sampling, simulation, custom-plotting) has an accurate, non-generic diagram visible on the built site
  4. All legacy-outlier learn/ diagrams (off-spec fonts, viewBox, or palette) have been migrated to the STYLE_SPEC.md standard

**Plans**: 2/2 plans executed

**Wave 1**

- [x] 03-01-PLAN.md — TRACER: fix smoothing.svg GAP-0001 ghost bug, prove SVGO gate + built-site render (DIA-01)

**Wave 2** *(blocked on Wave 1)*

- [x] 03-02-PLAN.md — verify remaining 5 learn/ diagrams (SVGO gate, STYLE_SPEC markers, build) + COVERAGE.md (DIA-01)

### Phase 4: represent/ Diagrams

**Goal**: Every diagram in the represent/ section conforms to STYLE_SPEC.md, is free of R-era content, and faithfully depicts what the method actually does
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: DIA-02
**Success Criteria** (what must be TRUE):

  1. All represent/ SVG diagrams pass SVGO lint with zero errors
  2. `basis-representation.svg` contains no `extendr`, `autoplot`, or R-specific identifiers — verified by grep and on the built site
  3. Every represent/ page that warrants a diagram (basis-representation, FPCA, andrews-transformation, distance-metrics, elastic-fpca) has an accurate diagram visible on the built site
  4. All legacy-outlier represent/ diagrams have been migrated to the STYLE_SPEC.md standard

**Plans**: 2 plans

- [x] 04-01-PLAN.md — Migrate depth-functions.svg (GAP-0002) to STYLE_SPEC (tracer: restyle → SVGO gate → build → review)
- [x] 04-02-PLAN.md — Section-wide verification of all 7 represent/ diagrams (SVGO, STYLE_SPEC markers, R-era grep, build) + COVERAGE.md

### Phase 5: align/ Diagrams

**Goal**: Every diagram in the align/ section conforms to STYLE_SPEC.md and correctly depicts elastic alignment concepts including the phase-vs-amplitude split
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: DIA-03
**Success Criteria** (what must be TRUE):

  1. All align/ SVG diagrams pass SVGO lint with zero errors
  2. The elastic-alignment diagram visually distinguishes phase variation from amplitude variation — both concepts are legibly labeled and correctly depicted on the built site
  3. Every align/ page that warrants a diagram (elastic-alignment, landmark-registration, tsrvf, shape-analysis, alignment-comparison, advanced-alignment) has an accurate diagram visible on the built site
  4. All legacy-outlier align/ diagrams have been migrated to the STYLE_SPEC.md standard

**Plans**: TBD

### Phase 6: analyze/ Diagrams

**Goal**: Every diagram in the analyze/ section conforms to STYLE_SPEC.md, and all previously identified legacy outliers are migrated to the standard
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: DIA-04
**Success Criteria** (what must be TRUE):

  1. All analyze/ SVG diagrams pass SVGO lint with zero errors
  2. Previously flagged legacy-outlier diagrams (clustering, depth-functions, gmm-clustering, outlier-detection, seasonal-analysis, covariance-functions, elastic-clustering) use the STYLE_SPEC.md viewBox, palette, and CSS classes — verified on the built site
  3. Every analyze/ page that warrants a diagram (clustering, depth-functions, outlier-detection, tolerance-bands, covariance-functions, seasonal-analysis, equivalence-testing, gmm-clustering, elastic-clustering) has an accurate diagram visible on the built site

**Plans**: TBD

### Phase 7: regression/ Diagrams

**Goal**: Every diagram in the regression/ section conforms to STYLE_SPEC.md and correctly depicts method semantics, including the functional conformal prediction band
**Mode:** mvp
**Depends on**: Phase 6
**Requirements**: DIA-05
**Success Criteria** (what must be TRUE):

  1. All regression/ SVG diagrams pass SVGO lint with zero errors
  2. `conformal-prediction.svg` accurately depicts the conformal prediction interval for `fdars.conformal` regression — **CORRECTED (Phase 7):** live verification shows `conformal_fregre_lm`/`_np` are scalar-on-function (scalar response, per-observation interval `[ŷ − q, ŷ + q]`), NOT functional. The scalar-interval depiction is method-accurate; the original "time-varying band ŷ(t)±q(t)" premise (audit GAP-0004) was a false positive — no redraw. See 07-VERIFICATION.md.
  3. The scalar-on-function regression diagram shows the β(t) coefficient curve as the key visual element — verified on the built site
  4. Every regression/ page that warrants a diagram (scalar-on-function, function-on-scalar, robust-regression, conformal-prediction, conformal-classification, classification, regression-diagnostics, cross-validation) has an accurate diagram visible on the built site

**Plans**: TBD
**UI hint**: yes

### Phase 8: monitoring/ Diagrams

**Goal**: Every diagram in the monitoring/ section conforms to STYLE_SPEC.md, is free of R-era content, and correctly depicts SPM Phase I/II control limits
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: DIA-06
**Success Criteria** (what must be TRUE):

  1. All monitoring/ SVG diagrams pass SVGO lint with zero errors
  2. `spm.svg` contains no `extendr`, `autoplot`, or R-specific identifiers — verified by grep and on the built site
  3. The SPM diagram(s) correctly depict Phase I (in-control estimation) and Phase II (online monitoring) control limits as distinct visual elements on the built site
  4. Every monitoring/ page that warrants a diagram (spm, advanced-spm, profile-partial-monitoring) has an accurate diagram visible on the built site

**Plans**: TBD

### Phase 9: Examples Sweep

**Goal**: Every `docs/examples/*.md` runs correctly against the current `fdars` API, carries enriched narrative, has improved output figures, and five new worked examples cover under-documented capabilities
**Mode:** mvp
**Depends on**: Phase 8
**Requirements**: EX-01, EX-02, EX-03, EX-04
**Success Criteria** (what must be TRUE):

  1. `pytest --md` (pytest-markdown-docs) passes on every `docs/examples/*.md` page without errors or silent wrong-output — value assertions and dict-key checks guard against API drift
  2. Every example page follows the Problem → Data → Method → Interpretation structure with genuine interpretation text, not just code
  3. Example output figures use consistent styling and captions; Code/Output tabs are applied where appropriate; each example cross-links to the relevant API reference page
  4. Five new worked examples are present and passing: conformal coverage guarantee, function-on-scalar regression, outlier-detection workflow, tolerance-bands vs conformal comparison, and functional depth centrality ordering

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete    | 2026-08-07 |
| 2. Audit | 3/3 | Complete    | 2026-08-07 |
| 3. learn/ Diagrams | 2/2 | Complete    | 2026-08-08 |
| 4. represent/ Diagrams | 2/2 | Complete    | 2026-08-08 |
| 5. align/ Diagrams | 1/0 | Complete    | 2026-08-08 |
| 6. analyze/ Diagrams | 1/0 | Complete    | 2026-08-08 |
| 7. regression/ Diagrams | 1/0 | Complete    | 2026-08-08 |
| 8. monitoring/ Diagrams | 1/0 | Complete    | 2026-08-08 |
| 9. Examples Sweep | 0/TBD | Not started | - |
