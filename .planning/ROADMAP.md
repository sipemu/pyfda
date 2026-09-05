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

## Progress

All milestones through v11.0 are shipped. No active milestone — start the next one with `/gsd-new-milestone` (phase numbering continues from Phase 74).

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v11.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{...}-phases/`._
