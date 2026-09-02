# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (shipped 2026-08-17)
- ✅ **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** — Phases 30–35 (shipped 2026-08-18)
- ✅ **v6.0 — fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference** — Phases 36–41 (shipped 2026-08-22)
- ✅ **v7.0 — Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth** — Phases 42–49 (shipped 2026-08-23)
- ✅ **v8.0 — Advisor: New Capabilities** — Phases 50–54 (shipped 2026-08-31)
- ✅ **v9.0 — scikit-learn API Compatibility** — Phases 55–59 (shipped 2026-09-02)
- 🚧 **v10.0 — Diagram Quality & Accessibility Pass** — Phases 60–65 (in progress)

## Phases

<details>
<summary>✅ v1.0 Documentation Overhaul (Phases 1–9) — SHIPPED 2026-08-08</summary>

Reworked the MkDocs site's hand-authored SVG diagrams and worked example pages to a consistently high, method-accurate standard, on top of new style/determinism/doc-test guardrails. Full detail: `.planning/milestones/v1.0-ROADMAP.md`.

- [x] Phase 1: Foundation — SVG style spec, SVGO lint gate, deterministic builds, snippets, pytest-markdown-docs, DOCS_FAST (completed 2026-08-07)
- [x] Phase 2: Audit — nav + reference-API audit → diagram coverage map + ranked gap list (completed 2026-08-07)
- [x] Phase 3: learn/ Diagrams — conform, fix coordinate-reuse bug, close gaps (completed 2026-08-08)
- [x] Phase 4: represent/ Diagrams — remove R-era content, conform, close gaps (completed 2026-08-08)
- [x] Phase 5: align/ Diagrams — conform, fix phase-vs-amplitude split, close gaps (completed 2026-08-08)
- [x] Phase 6: analyze/ Diagrams — migrate legacy outliers, conform, close gaps (completed 2026-08-08)
- [x] Phase 7: regression/ Diagrams — redraw conformal band, conform, close gaps (completed 2026-08-08)
- [x] Phase 8: monitoring/ Diagrams — remove R-era content, redraw control limits, close gaps (completed 2026-08-08)
- [x] Phase 9: Examples Sweep — all pages correct against current API, enriched narrative, improved figures, five new examples (completed 2026-08-08)

</details>

<details>
<summary>✅ v2.0 Grounded AI analysis advisor (Phases 10–13) — SHIPPED 2026-08-10</summary>

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout. Full detail: `.planning/milestones/v2.0-ROADMAP.md`.

- [x] Phase 10: Advisor Core Primitive (completed 2026-08-09)
- [x] Phase 11: Python API Surface (completed 2026-08-09)
- [x] Phase 12: Tool / MCP Surface (completed 2026-08-09)
- [x] Phase 13: Agent Skill Surface (completed 2026-08-10)

</details>

<details>
<summary>✅ v2.1 Document the AI Advisor (Phases 14–18) — SHIPPED 2026-08-11</summary>

Gave the published MkDocs site a first-class, method-accurate "AI Advisor" section documenting the shipped v2.0 grounded advisor. Full detail: `.planning/milestones/v2.1-ROADMAP.md`.

- [x] Phase 14: Advisor Concept & Diagrams (completed 2026-08-11)
- [x] Phase 15: Python API Page (completed 2026-08-11)
- [x] Phase 16: Tool / MCP Server Page (completed 2026-08-11)
- [x] Phase 17: Agent Skill Page (completed 2026-08-11)
- [x] Phase 18: Nav & Build Integration (completed 2026-08-11)

</details>

<details>
<summary>✅ v3.0 Provider-Agnostic Advisor, Full-Library Coverage (Phases 19–24) — SHIPPED 2026-08-12</summary>

Made the fdars AI advisor work with any LLM backend through a custom `Provider` protocol, and gave every fdars analysis aspect its own advisor — grounding invariant preserved on every backend. Full detail: `.planning/milestones/v3.0-ROADMAP.md`.

- [x] Phase 19: Provider Foundation & Grounding Contract (completed 2026-08-12)
- [x] Phase 20: Additional Provider Adapters (completed 2026-08-12)
- [x] Phase 21: Per-Aspect Advisor Coverage (completed 2026-08-12)
- [x] Phase 22: Surface Integration (completed 2026-08-12)
- [x] Phase 23: Packaging & CI (completed 2026-08-12)
- [x] Phase 24: Documentation (completed 2026-08-12)

</details>

<details>
<summary>✅ v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Phases 25–29) — SHIPPED 2026-08-17</summary>

Upgraded `fdars-core` 0.14.0 → 0.17.0 and exposed the new upstream functional-data capabilities through PyO3 bindings + the Python API, extended the advisor, and documented everything to the method-accurate standard. Full detail: `.planning/milestones/v4.0-ROADMAP.md`.

- [x] Phase 25: Crate Bump + Regression Gate (completed 2026-08-14)
- [x] Phase 26: Interpolation, Imputation & Functional Statistics Bindings (completed 2026-08-15)
- [x] Phase 27: Scoring Metrics & Alignment/Registration Bindings (completed 2026-08-15)
- [x] Phase 28: Advisor Extension (completed 2026-08-16)
- [x] Phase 29: Docs — Diagrams & Worked Examples (completed 2026-08-17)

</details>

<details>
<summary>✅ v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Phases 30–35) — SHIPPED 2026-08-18</summary>

Upgraded `fdars-core` 0.17.0 → 0.20.0 and exposed the new functional-inference + depth/boxplot + basis/smoothing surface, extended the advisor with an `inference` aspect, and documented it all. Full detail: `.planning/milestones/v5.0-ROADMAP.md`.

- [x] Phase 30: Crate Bump + Regression Gate (completed 2026-08-17)
- [x] Phase 31: Group A — `fdars.inference` Bindings (completed 2026-08-17)
- [x] Phase 32: Group B — Depth/Boxplot Bindings (completed 2026-08-17)
- [x] Phase 33: Group C — Basis/Smoothing Quick Wins (completed 2026-08-17)
- [x] Phase 34: Advisor Extension (completed 2026-08-17)
- [x] Phase 35: Docs — Diagrams & Worked Examples (completed 2026-08-18)

</details>

<details>
<summary>✅ v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (Phases 36–41) — SHIPPED 2026-08-22</summary>

Upgraded `fdars-core` 0.20.0 → 0.23.0 and exposed the new upstream surface across three capability groups, extended the advisor, and documented everything (blocking human diagram review caught + fixed an inverted hypograph/epigraph asymmetry). Full detail: `.planning/milestones/v6.0-ROADMAP.md`.

- [x] Phase 36: Crate Bump + Regression Gate (completed 2026-08-20)
- [x] Phase 37: Group A — Regression Bindings (completed 2026-08-20)
- [x] Phase 38: Group B — FPCA & Classification Bindings (completed 2026-08-21)
- [x] Phase 39: Group C — Depth/Outliers/Interval-Inference Bindings (completed 2026-08-21)
- [x] Phase 40: Advisor Extension (completed 2026-08-21)
- [x] Phase 41: Docs — Diagrams & Worked Examples (completed 2026-08-22)

</details>

<details>
<summary>✅ v7.0 Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth (Phases 42–49) — SHIPPED 2026-08-23</summary>

Docs-only quality pass (no crate bump, no new bindings). A full 61-diagram 4-axis scored inventory gated the milestone; SVG corrections batched by section; 20 new example-page workflow SVGs + 5 new advisor-surface SVGs; thin v4–v6 method pages extended. Whole-site `mkdocs build --strict` green offline; blocking human diagram review approved. Full detail: `.planning/milestones/v7.0-ROADMAP.md`.

- [x] Phase 42: Diagram Audit (completed 2026-08-22)
- [x] Phase 43: SVG Fix — learn / represent / align (completed 2026-08-22)
- [x] Phase 44: SVG Fix — analyze / monitoring / advisor (completed 2026-08-22)
- [x] Phase 45: SVG Fix — regression / inference (completed 2026-08-22)
- [x] Phase 46: Diagram Coverage — examples pages (completed 2026-08-22)
- [x] Phase 47: Diagram Coverage — advisor surface pages (completed 2026-08-22)
- [x] Phase 48: Page Depth (completed 2026-08-22)
- [x] Phase 49: Whole-Site Gate & Human Review (completed 2026-08-23)

</details>

<details>
<summary>✅ v8.0 Advisor: New Capabilities (Phases 50–54) — SHIPPED 2026-08-31</summary>

Extended the fdars AI advisor with four new capabilities (deferred aspects, comparative method-selection, pipeline diagnostic report, closed-loop auto-tuning) — grounding invariant + MCP-LLM-free boundary held throughout. Package 0.7.0 → 0.8.0. Full detail: `.planning/milestones/v8.0-ROADMAP.md`.

- [x] Phase 50: Deferred advisor aspects (completed 2026-08-31)
- [x] Phase 51: Comparative method-selection (completed 2026-08-31)
- [x] Phase 52: Pipeline diagnostic report (completed 2026-08-31)
- [x] Phase 53: Closed-loop auto-tuning (capstone) (completed 2026-08-31)
- [x] Phase 54: Eval strategy + docs (completed 2026-08-31)

</details>

<details>
<summary>✅ v9.0 scikit-learn API Compatibility (Phases 55–59) — SHIPPED 2026-09-02</summary>

Added `fdars.sklearn` — a pure-Python scikit-learn-compatible estimator layer over the current bindings so functional-data methods plug natively into `Pipeline`/`GridSearchCV`/`cross_val_score`, interoperate with native sklearn estimators, and offer `fit`/`transform`/`predict` ergonomics. **28 estimators** across five families pass the full `check_estimator` battery with zero exemptions; non-compliant methods EXCLUDED (reason-coded in `_coverage.py`), not exempted. 5 phases, 17 plans; `tests/sklearn/` 4294 passed / 0 failed; whole-site `mkdocs build --strict` green offline. Package 0.8.0 → 0.9.0, released to PyPI (tag `v0.9.0`). Closed via a documented Phase-59 verification override. Full detail: `.planning/milestones/v9.0-ROADMAP.md`.

- [x] Phase 55: Compliance-Triage & Foundation — `[sklearn]` extra + gated subpackage + `_BaseFdarsEstimator` + ~30-candidate triage → `EXCLUDED_METHODS` registry + go/no-go gate (completed 2026-08-31)
- [x] Phase 56: Transformers — FPCA + smoothers + imputer/interpolator + basis + depth as `TransformerMixin`; `Pipeline([smoother, fpca])` (completed 2026-08-31)
- [x] Phase 57: Regressors & Classifiers — FPC/PLS/GLM/nonparametric regressors + logistic/LDA/QDA/KNN/DD/elastic classifiers; `Pipeline` + `GridSearchCV` (completed 2026-08-31)
- [x] Phase 58: Clusterers & Outlier Detectors + Compliance Gate — KMeans/fuzzy/GMM + 6 detectors (stored-reference depth); full-matrix gate (28 estimators, 0 exemptions) + interop + CI 3.9–3.14 (completed 2026-09-01)
- [x] Phase 59: Documentation & Docs Gate — "scikit-learn API" docs section + coverage/EXCLUDE list + Pipeline & GridSearchCV worked examples + data-flow SVG; `--strict` green; pkg bump + PyPI release (shipped 2026-09-02; closed via verification override)

</details>

### 🚧 v10.0 Diagram Quality & Accessibility Pass (In Progress)

**Milestone Goal:** Bring all 156 hand-authored inline SVGs to one consistently high, defect-free, accessible bar — every diagram well-made (no mismatched lines / misaligned geometry / layout defects), STYLE_SPEC-conformant, accessible (`role`/`aria-label` + long-form `<title>`/`<desc>`/`aria-labelledby` on complex diagrams), and with cards/thumbs synced to their concept diagrams, plus method-accurate diagrams added to the audit-identified pages that still lack one. Docs-only, diagram-focused successor to v7.0's Documentation Quality Pass. Same shape: scored-inventory audit → section-batched corrections (defect + accessibility + STYLE_SPEC) → cards/thumbs sync + new coverage → whole-site build/review gate.

**Scope decisions (locked):** consistency + defect-fix depth ONLY — NO palette/typography change (deferred DIAG-FUT-03); dark-mode OUT of scope (deferred DIAG-FUT-01b); audit covers all 156 SVGs (90 concept in `docs/assets/diagrams/`, 8 cards in `docs/assets/cards/`, 58 thumbs in `docs/assets/thumb/`).

**Standing constraints every phase inherits:** docs-only — NO `fdars-core` bump, NO bindings, NO advisor/MCP changes, NO package version bump (v7.0 precedent); diagrams stay hand-authored inline SVG (locked constraint — no programmatic generation); the SVGO idempotence + build-determinism CI gate must stay green; the whole-site `mkdocs build --strict` must be green offline (run at close — this milestone changes static SVGs, not fences, so most work needs no full rebuild); docs phases run SEQUENTIALLY on `main` (NOT in worktrees — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path; `use_worktrees: false`); per-section review on the built site; a BLOCKING human diagram method-accuracy review before milestone close (the v6.0 hypograph/epigraph lesson).

- [ ] **Phase 60: Diagram Quality Audit** - Scored inventory of all 156 SVGs (design/geometry, STYLE_SPEC, accessibility, thumb/card sync) → milestone-gating fix list + coverage-gap list
- [ ] **Phase 61: SVG Corrections — learn / represent / align** - Correct that batch on defect + accessibility + STYLE_SPEC axes; per-section built-site review
- [ ] **Phase 62: SVG Corrections — analyze / monitoring / advisor** - Correct that batch on defect + accessibility + STYLE_SPEC axes; per-section built-site review
- [ ] **Phase 63: SVG Corrections — regression / inference / examples** - Correct that batch on defect + accessibility + STYLE_SPEC axes; per-section built-site review
- [ ] **Phase 64: Cards & Thumbnails Sync + New Coverage** - Sync 8 cards + 58 thumbs to their corrected concept diagrams; add method-accurate diagrams to audit-identified gap pages
- [ ] **Phase 65: STYLE_SPEC Refresh, Whole-Site Gate & Human Review** - Refresh STYLE_SPEC status/counts + accessibility pattern; `--strict` green offline; SVGO/determinism gate; blocking human diagram review

## Phase Details

### Phase 60: Diagram Quality Audit
**Goal**: A scored inventory of all 156 hand-authored SVGs — 90 concept (`docs/assets/diagrams/`), 8 cards (`docs/assets/cards/`), 58 thumbs (`docs/assets/thumb/`) — is produced as the milestone-gating artifact, each scored on design/geometry quality, STYLE_SPEC conformance, accessibility, and thumb/card sync, so every downstream correction, sync, and coverage phase executes against evidence rather than guesswork.
**Depends on**: Nothing (first phase of milestone; gates all downstream v10.0 work)
**Requirements**: AUDIT-01, AUDIT-02
**Success Criteria** (what must be TRUE):
  1. The audit report inventories all 156 SVGs (90 concept + 8 cards + 58 thumbs), each scored on four axes — design/geometry quality (mismatched lines, misaligned endpoints, overlapping/misplaced elements, layout), STYLE_SPEC conformance, accessibility (`role`/`aria-label`/`<title>`/`<desc>`), and thumb-to-concept / card-to-concept sync.
  2. The report flags each diagram with a defect severity and groups the concept-diagram findings into a ranked, per-section fix list aligned to the docs sections (learn, represent, align, analyze, monitoring, advisor, regression, inference, examples) so each downstream correction phase (61/62/63) has an explicit, evidence-backed worklist.
  3. The report identifies the coverage gap — the pages/methods that still lack a concept diagram — driving the COVER-01 scope for Phase 64.
  4. The report identifies which of the 58 thumbnails and 8 cards have drifted from their current concept diagrams, driving the SYNC-01/SYNC-02 scope for Phase 64.
**Plans**: 2 plans
- [ ] 60-01-PLAN.md — Skeleton + score all 90 concept diagrams (4 axes, render-backed) + section/61-62-63 bucket map
- [ ] 60-02-PLAN.md — Score 8 cards + 58 thumbs with drift detection; COVER-01 gap list, SYNC-01/02 drift list, ranked 61/62/63 fix worklists, self-check
**UI hint**: yes

### Phase 61: SVG Corrections — learn / represent / align
**Goal**: Every concept diagram in the learn, represent, and align sections is corrected on the defect, accessibility, and STYLE_SPEC axes and verified on the built site, so this batch meets the consistently-high, defect-free, accessible bar without ever misdepicting the method.
**Depends on**: Phase 60
**Requirements**: DEFECT-01, DEFECT-02, DEFECT-03, A11Y-01, A11Y-02, SPEC-01 (learn/represent/align batch)
**Success Criteria** (what must be TRUE):
  1. Every diagram flagged with geometry/line defects (mismatched lines, misaligned endpoints, overlapping/misplaced elements) or layout defects (spacing, alignment, label overlap, panel sizing) in learn/represent/align renders correctly on the built site with those defects gone (rendered PNG check).
  2. Every concept diagram in this batch carries `role="img"` + an `aria-label` matching its title text, and every complex/multi-panel diagram in this batch carries a long-form `<title>` + `<desc>` wired via `aria-labelledby`.
  3. Every diagram in this batch conforms to `STYLE_SPEC.md` (viewBox conventions, canonical `<style>` block, palette, stroke weights, panel patterns) and passes the SVGO idempotence + build-determinism CI gate (byte-identical rebuilds).
  4. Every correction in this batch preserves method-accuracy — no diagram misdepicts what its method does after the fix — and each section passes a built-site review before the batch is done.
**Plans**: TBD
**UI hint**: yes

### Phase 62: SVG Corrections — analyze / monitoring / advisor
**Goal**: Every concept diagram in the analyze, monitoring, and advisor sections is corrected on the defect, accessibility, and STYLE_SPEC axes and verified on the built site.
**Depends on**: Phase 61
**Requirements**: DEFECT-01, DEFECT-02, DEFECT-03, A11Y-01, A11Y-02, SPEC-01 (analyze/monitoring/advisor batch)
**Success Criteria** (what must be TRUE):
  1. Every diagram flagged with geometry/line or layout defects in analyze/monitoring/advisor renders correctly on the built site with those defects gone (rendered PNG check).
  2. Every concept diagram in this batch carries `role="img"` + an `aria-label` matching its title text, and every complex/multi-panel diagram carries a long-form `<title>` + `<desc>` wired via `aria-labelledby`.
  3. Every diagram in this batch conforms to `STYLE_SPEC.md` and passes the SVGO idempotence + build-determinism CI gate (byte-identical rebuilds).
  4. Every correction in this batch preserves method-accuracy, and each section passes a built-site review before the batch is done.
**Plans**: TBD
**UI hint**: yes

### Phase 63: SVG Corrections — regression / inference / examples
**Goal**: Every concept diagram in the regression, inference, and examples sections is corrected on the defect, accessibility, and STYLE_SPEC axes and verified on the built site, completing the full-set concept-diagram correction sweep across all sections.
**Depends on**: Phase 62
**Requirements**: DEFECT-01, DEFECT-02, DEFECT-03, A11Y-01, A11Y-02, SPEC-01 (regression/inference/examples batch)
**Success Criteria** (what must be TRUE):
  1. Every diagram flagged with geometry/line or layout defects in regression/inference/examples renders correctly on the built site with those defects gone (rendered PNG check), with special care on the depth/interval-inference diagrams per the v6.0 hypograph/epigraph lesson.
  2. Every concept diagram in this batch carries `role="img"` + an `aria-label` matching its title text, and every complex/multi-panel diagram carries a long-form `<title>` + `<desc>` wired via `aria-labelledby`.
  3. Every diagram in this batch conforms to `STYLE_SPEC.md` and passes the SVGO idempotence + build-determinism CI gate (byte-identical rebuilds).
  4. Across Phases 61–63, every flagged concept diagram on the Phase-60 fix list has been corrected and no diagram misdepicts its method — the full concept-diagram set (all 90) now meets the DEFECT-01/02/03, A11Y-01/02, and SPEC-01 bar.
**Plans**: TBD
**UI hint**: yes

### Phase 64: Cards & Thumbnails Sync + New Coverage
**Goal**: The 8 section cards and 58 gallery thumbnails are brought in line with their now-corrected concept diagrams (using correct decorative semantics for the thumbs), and method-accurate concept diagrams are added to the audit-identified pages/methods that still lack one — closing the sync and coverage gaps against the corrected concept-diagram set.
**Depends on**: Phase 63
**Requirements**: SYNC-01, SYNC-02, A11Y-03, COVER-01
**Success Criteria** (what must be TRUE):
  1. All 58 gallery thumbnails reflect their current (corrected) concept diagrams — redrawn/regenerated where the Phase-60 audit flagged drift — and render correctly on the built site.
  2. All 8 section cards are reviewed and brought to the same quality and consistency bar as the concept diagrams (STYLE_SPEC-conformant, defect-free).
  3. Decorative gallery thumbnails use correct non-announcing semantics (empty `alt` / `aria-hidden`) consistently, so screen readers do not announce redundant decorative images.
  4. Every audit-identified page/method that lacked a concept diagram now references a hand-authored inline concept SVG that renders on the built site, is method-accurate, STYLE_SPEC-conformant, accessible, and passes the SVGO idempotence + build-determinism gate.
**Plans**: TBD
**UI hint**: yes

### Phase 65: STYLE_SPEC Refresh, Whole-Site Gate & Human Review
**Goal**: `STYLE_SPEC.md` is refreshed to match the shipped diagram set (stale status/counts corrected, accessibility pattern finalized), and the whole documentation site passes its final quality gate — a green offline `mkdocs build --strict`, a green SVGO/determinism gate across all diagrams, and a blocking human diagram method-accuracy review before milestone close.
**Depends on**: Phase 61, Phase 62, Phase 63, Phase 64
**Requirements**: SPEC-02, GATE-01, GATE-02, GATE-03
**Success Criteria** (what must be TRUE):
  1. `STYLE_SPEC.md` is updated so its status/counts match the shipped diagram set (the stale "34 of 43" accessibility note is corrected against the 90 concept diagrams that exist today) and the accessibility pattern (`role`/`aria-label` + `<title>`/`<desc>`/`aria-labelledby`) is finalized to match the corrected set.
  2. The SVGO idempotence + build-determinism gate is green across all 156 SVGs — no drift on re-run.
  3. Whole-site `mkdocs build --strict` exits 0 offline after all changes.
  4. A blocking human diagram method-accuracy review passes — no diagram misdepicts its method — before the milestone is closed.
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 60 → 61 → 62 → 63 → 64 → 65

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 60. Diagram Quality Audit | v10.0 | 0/0 | Not started | - |
| 61. SVG Corrections — learn / represent / align | v10.0 | 0/0 | Not started | - |
| 62. SVG Corrections — analyze / monitoring / advisor | v10.0 | 0/0 | Not started | - |
| 63. SVG Corrections — regression / inference / examples | v10.0 | 0/0 | Not started | - |
| 64. Cards & Thumbnails Sync + New Coverage | v10.0 | 0/0 | Not started | - |
| 65. STYLE_SPEC Refresh, Whole-Site Gate & Human Review | v10.0 | 0/0 | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v9.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{...}-phases/`._
