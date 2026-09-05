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
- ✅ **v10.0 — Diagram Quality & Accessibility Pass** — Phases 60–65 (shipped 2026-09-02)
- ✅ **v11.0 — fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs** — Phases 66–73 (shipped 2026-09-05)
- 🚧 **v12.0 — Docs Depth, Card Coverage & AI Capability Skill** — Phases 74–79 (in progress)

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

<details>
<summary>✅ v10.0 Diagram Quality & Accessibility Pass (Phases 60–65) — SHIPPED 2026-09-02</summary>

- [x] Phase 60: Diagram Quality Audit (2/2 plans) — completed 2026-09-02
- [x] Phase 61: SVG Corrections — learn / represent / align (1/1) — completed 2026-09-02
- [x] Phase 62: SVG Corrections — analyze / monitoring / advisor (1/1) — completed 2026-09-02
- [x] Phase 63: SVG Corrections — regression / inference / examples (1/1) — completed 2026-09-02
- [x] Phase 64: Cards & Thumbnails Sync + New Coverage (1/1) — completed 2026-09-02
- [x] Phase 65: STYLE_SPEC Refresh, Whole-Site Gate & Human Review (1/1) — completed 2026-09-02

Full detail: `.planning/milestones/v10.0-ROADMAP.md`
</details>

<details>
<summary>✅ v11.0 fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs (Phases 66–73) — SHIPPED 2026-09-05</summary>

Bumped `fdars-core` 0.23.0 → 0.33.0 (parallel-only, no linalg; zero drift, 5650-test gate) and exposed the new upstream surface across six capability families through PyO3 bindings + Python API, extended the advisor with new `fts`/`frechet` aspects (grounding invariant + MCP guard-sync held), and documented everything with 8 method-accurate hand-authored SVGs + offline worked examples (whole-site `--strict` green; blocking human diagram review approved). 24/24 requirements validated; package 0.9.0 → 0.10.0 (PyPI tag `v0.10.0` handed to user). Full detail: `.planning/milestones/v11.0-ROADMAP.md`.

- [x] Phase 66: Isolated Crate Bump + Regression Gate — 0.23.0 → 0.33.0 on the ~772-test baseline; 0.24–0.33 changelog/match-arm audit (`66-AUDIT.md`) (completed 2026-09-02)
- [x] Phase 67: Functional Time Series (`fdars.fts`) — 13-function submodule: FTSM fit/forecast/update, ACF/PACF/stationarity/long-run-covariance, fPLSR, spectral density, DPCA (completed 2026-09-02)
- [x] Phase 68: Function-on-Function & Scalar-on-Function Regression — `fof_regression` + FOF family in `fdars.regression`; new `fdars.scalar_on_function` (additive/generalized SoF + variable/model selection) (completed 2026-09-02)
- [x] Phase 69: Fréchet Regression & Density FDA — `convert.rs` ragged-list refactor; new `fdars.frechet` (`frechet_mean` SPD/spherical/correlation) and `fdars.density_fda` (LQD/Wasserstein) (completed 2026-09-03)
- [x] Phase 70: Multi-Domain Data, FAMM & Advanced Clustering — `PyMultiFunData`/`fdars.multi_fdata`; `fdars.famm`; `mfpca`/`spe_multivariate` in `fdars.spm`; DBSCAN/KCFC/FunFEM/elastic clustering (completed 2026-09-04)
- [x] Phase 71: Shapelets & GAK Metric — new `fdars.shapelet` (2 opaque fit handles + 2 enums) + 5 GAK functions in `fdars.metric` (sklearn precomputed-kernel shapes) (completed 2026-09-04)
- [x] Phase 72: Advisor Extension — new `fts`/`frechet` aspects + grounded fof/fam/gkam/shapelet/mfpca/spe_multivariate diagnostics; atomic MCP guard-sync (completed 2026-09-04)
- [x] Phase 73: Documentation & Release — per-family method-accurate pages + 8 SVGs + offline fences; whole-site `--strict` green; human diagram review; pkg 0.9.0 → 0.10.0 + tag `v0.10.0` (completed 2026-09-05)

</details>

### 🚧 v12.0 Docs Depth, Card Coverage & AI Capability Skill (Phases 74–79) — IN PROGRESS

**Milestone Goal:** Bring the recently-added (v11.0-era) functionality up to the documentation bar of the mature pages, complete section-landing card coverage across the focus sections, and give AI agents a way to discover the full fdars capability surface — a docs + skill milestone, no `fdars-core` bump and no new bindings (v7.0/v10.0 precedent).

**Standing execution constraints (all content/doc phases):** run SEQUENTIALLY on `main` with `use_worktrees: false` — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path (v6.0/v11.0 standing decision). Keep fence datasets small (~25-min whole-site executed `--strict` build). The whole-site `mkdocs build --strict` gate, the SVGO/determinism gate, and the blocking human diagram review run ONCE, in the final gate phase (Phase 79) — not per content phase.

- [x] **Phase 74: Deepen Regression-Family Thin Pages** - Bring `frechet-regression`, `function-on-function`, `additive-sof`, `concurrent-regression`, `functional-glm` to mature-page parity (completed 2026-09-05)
- [x] **Phase 75: Deepen Analyze-Family Thin Pages** - Bring `functional-time-series`, `density-fda`, `multi-domain`, `shapelets`, `advanced-clustering` to mature-page parity (completed 2026-09-05)
- [x] **Phase 76: Flagship End-to-End Example Pages** - 2–3 marquee worked-example pages (FTS forecast, Fréchet regression, +1 if a strong dataset fit exists) (completed 2026-09-06)
- [ ] **Phase 77: Section-Landing Card Coverage** - 18 focus-section thumbnails + gallery cards (align/represent/regression/analyze) + 3 examples cards
- [ ] **Phase 78: AI Capability-Discovery Skill** - Agent Skill `SKILL.md` + verified capability map + LLM-oriented docs page + LLM-free MCP capability tool
- [ ] **Phase 79: Close Gate — Strict Build, SVGO/Determinism, Human Review & Release** - Whole-site `--strict` + SVGO/determinism gates, blocking human diagram review, grounding/MCP verification, offline-fence sweep, version tick + release handoff

## Phase Details

### Phase 74: Deepen Regression-Family Thin Pages

**Goal**: The five thin regression-family method pages read like the mature pages — a reader can decide when to use each method, cross-navigate to related methods, choose parameters, interpret results, and copy runnable examples.
**Depends on**: Nothing (first phase of v12.0; picks up from Phase 73)
**Requirements**: DEPTH-01
**Success Criteria** (what must be TRUE):

  1. Each of `frechet-regression`, `function-on-function`, `additive-sof`, `concurrent-regression`, `functional-glm` has a "When to use" decision section and a "See also" cross-reference block.
  2. Each page adds parameter-selection + result-interpretation guidance and ≥3 caution/tip/note admonition boxes.
  3. Each page carries ≥3 runnable inline `FDARS_FENCE_OK` worked examples that emit the sentinel when run offline under `.venv`.
  4. Every method claim on these pages is accurate against the shipped v11.0 bindings (no stale/renamed API, no R-era prose).

**Plans**: 5/5 plans executed

- [x] 74-01-PLAN.md — TRACER: frechet-regression.md to full parity (fix frechet_anova/local_reg/xout API) + offline fence verify
- [x] 74-02-PLAN.md — function-on-function.md to parity (fix predict_fof arg order + fof_cv params)
- [x] 74-03-PLAN.md — additive-sof.md to parity (fix fam/gsam auto-defaults + variable_selection/model_selection keys)
- [x] 74-04-PLAN.md — concurrent-regression.md to full parity (manual predict + manual bandwidth-CV + decision/see-also)
- [x] 74-05-PLAN.md — functional-glm.md to full parity (gaussian-reduces-to-linear + param selection + decision/see-also)

**UI hint**: no

### Phase 75: Deepen Analyze-Family Thin Pages

**Goal**: The five thin analyze-family method pages reach the same mature-page parity, so a reader can choose, parameterize, interpret, and run each analyze method with confidence.
**Depends on**: Phase 74 (sequential on `main`; disjoint page set)
**Requirements**: DEPTH-02
**Success Criteria** (what must be TRUE):

  1. Each of `functional-time-series`, `density-fda`, `multi-domain`, `shapelets`, `advanced-clustering` has a "When to use" decision section and a "See also" cross-reference block.
  2. Each page adds parameter-selection + result-interpretation guidance and ≥3 caution/tip/note admonition boxes.
  3. Each page carries ≥3 runnable inline `FDARS_FENCE_OK` worked examples that emit the sentinel when run offline under `.venv`.
  4. Every method claim on these pages is accurate against the shipped v11.0 bindings and existing `docs/data/` datasets.

**Plans**: 5/5 plans executed

- [x] 75-01-PLAN.md — TRACER: functional-time-series.md to full parity (8 API corrections)
- [x] 75-02-PLAN.md — density-fda.md to parity (3-arg inverse_lqd, quantile-grid clarification)
- [x] 75-03-PLAN.md — multi-domain.md to parity (dense_flmm/multi_famm take plain arrays, not PyMultiFunData)
- [x] 75-04-PLAN.md — shapelets.md to parity (discover_shapelets dict, shapelet_distance tuple)
- [x] 75-05-PLAN.md — advanced-clustering.md to parity (funfem_cluster/align_cluster_fd full signatures)

**UI hint**: no

### Phase 76: Flagship End-to-End Example Pages

**Goal**: The examples section gains 2–3 marquee end-to-end walkthroughs for the new methods, matching the mature `examples/` standard (narrative + real dataset + runnable offline fences), wired into nav.
**Depends on**: Phase 75 (methods documented; sequential on `main`)
**Requirements**: EXMP-01, EXMP-02, EXMP-03
**Success Criteria** (what must be TRUE):

  1. A flagship Functional Time Series example page (forecast + evaluation) runs end-to-end offline against a `docs/data/` dataset, emitting `FDARS_FENCE_OK`.
  2. A flagship Fréchet-regression example page (metric-space response walkthrough) runs end-to-end offline, emitting `FDARS_FENCE_OK`.
  3. A third flagship example (e.g. shapelet classification or density FDA) is added if a strong `docs/data/` fit exists; otherwise the "2–3" range is satisfied by the first two, with the decision recorded.
  4. Each new example page is wired into the examples nav so a reader reaches it from the site navigation.

**Plans**: 3/3 plans executed

- [x] 76-01-PLAN.md — EXMP-02 Fréchet-regression flagship example (tracer; KDE density response on latitude) + nav
- [x] 76-02-PLAN.md — EXMP-01 Functional Time Series flagship example (forecast + RMSE eval) + nav
- [x] 76-03-PLAN.md — EXMP-03 shapelet-classification flagship example (phoneme 3-class) + nav

**UI hint**: no

### Phase 77: Section-Landing Card Coverage

**Goal**: The align, represent, regression, and analyze landing galleries reach 100% card coverage and the examples gallery gains its three missing cards — every focus-section page is reachable from a section-landing card with a hand-authored thumbnail.
**Depends on**: Phase 76 (example pages exist before their examples cards; sequential on `main`)
**Requirements**: CARD-01, CARD-02, CARD-03, CARD-04, CARD-05, CARD-06
**Success Criteria** (what must be TRUE):

  1. Align (`shift-registration`, `banded-alignment`) and represent (`pace-fpca`, `interpolation`, `imputation`) landing galleries show a card for every page.
  2. Regression (5 pages) and analyze (8 pages) landing galleries show a card for every focus-section page.
  3. The examples landing page shows cards for `functional-outlier-workflow`, `canadian-depth-centrality`, and `tolerance-vs-conformal`.
  4. Each new card has a hand-authored inline SVG thumbnail at `docs/assets/thumb/<page-slug>.svg` that is STYLE_SPEC-conformant and decorative-accessible (matching the existing `aria-hidden` card pattern).

**Plans**: TBD
**UI hint**: yes

### Phase 78: AI Capability-Discovery Skill

**Goal**: AI agents can discover the whole fdars capability surface across the three selected surfaces — a standalone Agent Skill, an LLM-oriented docs page, and an LLM-free MCP capability tool — distinct from and non-duplicating the existing narrow `fdars-advisor` skill/MCP.
**Depends on**: Nothing new in v12.0 (independent of the DEPTH/CARD content work; scheduled here to keep the final gate phase clean). Runs on `main`, `use_worktrees: false`.
**Requirements**: SKILL-01, SKILL-02, SKILL-03, SKILL-04
**Success Criteria** (what must be TRUE):

  1. A standalone capability-discovery Agent Skill ships a spec-valid `SKILL.md` mapping every public fdars submodule — what each method does, when to reach for it, and how to call it (signature + minimal usage).
  2. An automated test/harness verifies the skill's capability map against the live package (every documented method exists and is importable; no stale/renamed entries).
  3. An LLM-oriented docs page (llms.txt-style API digest of the whole library) is authored/generated and wired into the site.
  4. An MCP capability tool (e.g. `fdars_list_capabilities` / describe) is added to the existing server, returns the capability surface, stays provably LLM-free, and its guard/tests are updated to cover it.

**Plans**: TBD
**UI hint**: no

### Phase 79: Close Gate — Strict Build, SVGO/Determinism, Human Review & Release

**Goal**: The whole milestone is proven correct and shippable in one pass — the site builds strict and offline with every fence green, all new SVGs pass the determinism gates, a human approves the new diagrams for method-accuracy, the advisor/MCP boundaries still hold, and the release handoff is prepared.
**Depends on**: Phases 74, 75, 76, 77, 78 (all content, cards, and the skill must land before the single whole-site gate). Runs on `main`, `use_worktrees: false`.
**Requirements**: GATE-01, GATE-02, GATE-03, GATE-04, DEPTH-03
**Success Criteria** (what must be TRUE):

  1. Whole-site `mkdocs build --strict` is green offline and every worked example across the milestone emits `FDARS_FENCE_OK` (satisfying DEPTH-03's offline/method-accuracy sweep for the DEPTH pages).
  2. The SVGO idempotence + build-determinism gate is green across all new/changed SVGs (new thumbnails and any new concept diagrams).
  3. A blocking human diagram/method-accuracy review of the new thumbnails (and any new concept diagrams) is approved before close.
  4. Advisor/MCP tests (including guard-sync) are green after the SKILL-04 tool lands — grounding invariant + MCP LLM-free boundary preserved.
  5. Any package-version tick is committed; any irreversible publish (tag/PyPI) stays human-gated and is handed off, not executed autonomously.

**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:** Phases execute in numeric order: 74 → 75 → 76 → 77 → 78 → 79 (all sequential on `main`, `use_worktrees: false`).

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 74. Deepen Regression-Family Thin Pages | v12.0 | 5/5 | Complete    | 2026-09-05 |
| 75. Deepen Analyze-Family Thin Pages | v12.0 | 5/5 | Complete    | 2026-09-05 |
| 76. Flagship End-to-End Example Pages | v12.0 | 3/3 | Complete    | 2026-09-06 |
| 77. Section-Landing Card Coverage | v12.0 | 0/TBD | Not started | - |
| 78. AI Capability-Discovery Skill | v12.0 | 0/TBD | Not started | - |
| 79. Close Gate — Strict Build, SVGO/Determinism, Human Review & Release | v12.0 | 0/TBD | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v11.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{...}-phases/`._
