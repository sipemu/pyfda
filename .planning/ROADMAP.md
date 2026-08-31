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
- 🚧 **v9.0 — scikit-learn API Compatibility** — Phases 55–59 (in progress)

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

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout (fdars computes the numbers; the LLM only interprets and cites them). Full detail: `.planning/milestones/v2.0-ROADMAP.md`.

- [x] Phase 10: Advisor Core Primitive — offline `build_diagnostics` + grounded `advise` (Claude structured outputs) + cluster-difference specialization + `[advisor]` extra (completed 2026-08-09)
- [x] Phase 11: Python API Surface — recommend-only advisor on the public `fdars` API, offline + env-gated tests, `examples/advisor_recipe.py` (completed 2026-08-09)
- [x] Phase 12: Tool / MCP Surface — coarse-grained tools + stdio MCP server + agentic re-run/compare loop (completed 2026-08-09)
- [x] Phase 13: Agent Skill Surface — `SKILL.md` + walkthrough packaging the interpret→recommend→re-run→compare workflow, documented execution environment (completed 2026-08-10)

</details>

<details>
<summary>✅ v2.1 Document the AI Advisor (Phases 14–18) — SHIPPED 2026-08-11</summary>

Gave the published MkDocs site a first-class, method-accurate "AI Advisor" section documenting the shipped v2.0 grounded advisor. Documentation-only; every page method-accurate against `python/fdars/advisor.py`, `python/fdars/mcp/`, and `.claude/skills/fdars-advisor/`; full `mkdocs build --strict` green. Full detail: `.planning/milestones/v2.1-ROADMAP.md`.

- [x] Phase 14: Advisor Concept & Diagrams — overview page + grounding-invariant & advisor-loop inline SVGs (completed 2026-08-11)
- [x] Phase 15: Python API Page — `build_diagnostics`/`advise`/`describe_cluster_differences` + offline worked example that runs in the build (completed 2026-08-11)
- [x] Phase 16: Tool / MCP Server Page — three tools, by-reference handle model, stdio, re-run/compare loop (completed 2026-08-11)
- [x] Phase 17: Agent Skill Page — git-URL install + interpret→recommend→re-run→compare walkthrough (completed 2026-08-11)
- [x] Phase 18: Nav & Build Integration — "AI Advisor" nav section wired; full `--strict` build clean (completed 2026-08-11)

</details>

<details>
<summary>✅ v3.0 Provider-Agnostic Advisor, Full-Library Coverage (Phases 19–24) — SHIPPED 2026-08-12</summary>

A custom `Provider` protocol with Anthropic/OpenAI(-compatible)/Gemini/Ollama adapters, a centralized validate-and-retry + `_check_grounding` guard, deterministic offline `build_diagnostics` for all 12 fdars aspects through one shared schema/prompt, MCP + Agent Skill surface updates (MCP stays LLM-free), a Python 3.9–3.14 CI matrix, and a provider-setup + per-aspect docs section. Full detail: `.planning/milestones/v3.0-ROADMAP.md`.

- [x] Phase 19: Provider Foundation & Grounding Contract — `Provider` protocol + `AnthropicProvider` + centralized validate-and-retry + `_check_grounding` (completed 2026-08-12)
- [x] Phase 20: Additional Provider Adapters — OpenAI(-compatible)/Ollama/Gemini adapters as optional extras with deferred imports (completed 2026-08-12)
- [x] Phase 21: Per-Aspect Advisor Coverage — deterministic offline `build_diagnostics` across all 12 fdars aspects via `_ASPECT_PRIMERS` (completed 2026-08-12)
- [x] Phase 22: Surface Integration — MCP tools + Agent Skill provider-selection docs; MCP boundary stays LLM-free (completed 2026-08-12)
- [x] Phase 23: Packaging & CI — Python 3.9–3.14 matrix, version-gated extras, bare-venv smoke, aspect×provider grounding matrix (completed 2026-08-12)
- [x] Phase 24: Documentation — provider setup + per-aspect coverage page, executed offline fences, `--strict` build green (completed 2026-08-12)

</details>

<details>
<summary>✅ v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Phases 25–29) — SHIPPED 2026-08-17</summary>

Upgraded `fdars-core` 0.14.0 → 0.17.0 (parallel-only, no linalg; zero FPCA drift) and exposed the new upstream surface — `fdars.represent`, functional statistics + `depth_based_median`/`trim_mean`, a new `fdars.scoring` submodule, and `fdars.alignment` shift registration / quality scores / banded elastic alignment — extended the advisor with a `scoring` aspect + imputation/registration diagnostics (grounding invariant + MCP guard-sync preserved), and documented it all. Full detail: `.planning/milestones/v4.0-ROADMAP.md`.

- [x] Phase 25: Crate Bump + Regression Gate — 0.17.0 pinned (parallel-only, no linalg); full suite green as the sole gate (completed 2026-08-17)
- [x] Phase 26: represent + Functional Statistics Bindings — `fdars.represent` + variance/std/covariance + depth-based median/trim mean + 6 `Fdata` methods (completed 2026-08-17)
- [x] Phase 27: scoring + Alignment Bindings — `fdars.scoring` (5 metrics) + shift registration + 3 quality scores + banded elastic alignment (completed 2026-08-17)
- [x] Phase 28: Advisor Extension — `scoring` aspect #13 + imputation/registration diagnostics; grounding invariant + guard-sync atomic (completed 2026-08-17)
- [x] Phase 29: Docs — 6 new pages + 6 method-accurate SVGs + offline `FDARS_FENCE_OK` worked examples; `--strict` green (completed 2026-08-17)

</details>

<details>
<summary>✅ v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Phases 30–35) — SHIPPED 2026-08-18</summary>

Upgraded `fdars-core` 0.17.0 → 0.20.0 (parallel-only, zero drift) and exposed a new `fdars.inference` submodule (two-sample permutation tests, Degras SCB bands, FLM post-hoc inference, one-way ANOVA), `functional_depth`/`functional_boxplot` in `fdars.depth`, and AIC model selection + `constant_basis` in `fdars.basis`/`fdars.smoothing`. Added an `inference` advisor aspect (#14) and documented it all. Full detail: `.planning/milestones/v5.0-ROADMAP.md`.

- [x] Phase 30: Crate Bump + Regression Gate — 0.20.0 pinned; 426-test gate green; `CvCriterion` wildcard arm (completed 2026-08-18)
- [x] Phase 31: Group A — Inference Bindings — `fdars.inference` submodule (two-sample tests, SCB, FLM inference, ANOVA) (completed 2026-08-18)
- [x] Phase 32: Group B — Depth & Functional Boxplot — `functional_depth` dispatcher + `functional_boxplot` (completed 2026-08-18)
- [x] Phase 33: Group C — Basis & Smoothing Quick Wins — `constant_basis` + AIC smoothing selection (completed 2026-08-18)
- [x] Phase 34: Advisor Extension — `inference` aspect (#14); grounding invariant + guard-sync preserved (completed 2026-08-18)
- [x] Phase 35: Docs — new Inference section + functional-boxplot + basis/smoothing fold-ins + 4 SVGs; `--strict` green (completed 2026-08-18)

</details>

<details>
<summary>✅ v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (Phases 36–41) — SHIPPED 2026-08-22</summary>

Upgraded `fdars-core` 0.20.0 → 0.23.0 (parallel-only, no `linalg`; MSRV verified 1.81 ≤ 1.83) and exposed the new upstream surface across three independent capability groups — Group A Regression (`concurrent_regression` + `functional_glm`), Group B FPCA & Classification (`pace_fpca` over a new sparse/irregular `IrregFdata` input + `elastic_multinomial`), Group C Depth/Outliers/Interval-Inference (9 new depth methods + 4 outlier detectors + 3 interval-wise ITP tests) — extended the grounded advisor's `outliers`/`regression`/`classification`/`fpca` aspects (closing the v5.0 Phase-34 boxplot-outlier deferral; ITP deferred as vector-valued; grounding invariant + MCP guard-sync preserved), and documented everything. Full detail: `.planning/milestones/v6.0-ROADMAP.md`.

- [x] Phase 36: Crate Bump + Regression Gate — 0.23.0 pinned; ~560-test suite green as the sole gate; wildcard fallback arms (completed 2026-08-20)
- [x] Phase 37: Group A — Regression Bindings — `concurrent_regression` + `functional_glm` extending `fdars.regression` (completed 2026-08-20)
- [x] Phase 38: Group B — FPCA & Classification Bindings — `PyIrregFdata` + `pace_fpca` submodule + `elastic_multinomial` (completed 2026-08-21)
- [x] Phase 39: Group C — Depth/Outliers/Interval-Inference Bindings — 9 depth variants + 4 outlier detectors + 3 ITP tests (completed 2026-08-21)
- [x] Phase 40: Advisor Extension — extended `outliers`/`regression`/`classification`/`fpca` aspects; ITP deferred; guard-sync no-op (completed 2026-08-21)
- [x] Phase 41: Docs — new pages + 6 SVGs + offline `FDARS_FENCE_OK` worked examples; blocking human diagram review (caught hypograph/epigraph asymmetry) (completed 2026-08-22)

</details>

<details>
<summary>✅ v7.0 Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth (Phases 42–49) — SHIPPED 2026-08-23</summary>

A docs-only quality pass (no crate bump, no new bindings, no advisor logic change). A full 61-diagram 4-axis scored inventory gated the milestone; hand-authored SVG corrections were batched by section; 20 new example-page workflow SVGs + 5 new advisor-surface SVGs closed the coverage gap; thin v4–v6 method pages were extended to full parity with new executable worked examples. Whole-site `mkdocs build --strict` green offline; blocking human diagram review approved. 12/12 requirements validated; 8 phases, 9 plans. Full detail: `.planning/milestones/v7.0-ROADMAP.md`.

- [x] Phase 42: Diagram Audit — 4-axis scored inventory → ranked per-section fix list + coverage-gap + thin-page lists (completed 2026-08-22)
- [x] Phase 43: SVG Fix — learn / represent / align — corrected that batch on all four axes; per-section built-site review (completed 2026-08-22)
- [x] Phase 44: SVG Fix — analyze / monitoring / advisor — corrected that batch on all four axes; per-section built-site review (completed 2026-08-22)
- [x] Phase 45: SVG Fix — regression / inference — corrected that batch on all four axes; per-section built-site review (completed 2026-08-22)
- [x] Phase 46: Diagram Coverage — examples pages — 20 new method-accurate example-page workflow SVGs (completed 2026-08-22)
- [x] Phase 47: Diagram Coverage — advisor surface pages — 5 new method-accurate advisor concept SVGs (completed 2026-08-22)
- [x] Phase 48: Page Depth — thin v4–v6 method pages extended to mature structure + new offline worked examples (completed 2026-08-22)
- [x] Phase 49: Whole-Site Gate & Human Review — `mkdocs build --strict` green offline; blocking human diagram review approved (completed 2026-08-23)

</details>

<details>
<summary>✅ v8.0 Advisor: New Capabilities (Phases 50–54) — SHIPPED 2026-08-31</summary>

Extended the fdars AI advisor with four new capabilities — deferred-aspect coverage (PACE-FPCA / elastic-multinomial / ITP), comparative method-selection, pipeline diagnostic reports, and a closed-loop auto-tuning capstone — plus a deterministic eval strategy and docs, holding the grounding invariant + MCP-LLM-free boundary throughout. 27/27 requirements; 5 phases, 16 plans, 41 tasks; suite 1045 passed / 10 skipped; whole-site `mkdocs build --strict` green; blocking human diagram review approved. Full detail: `.planning/milestones/v8.0-ROADMAP.md`.

- [x] Phase 50: Deferred Advisor Aspects (+ compat pre-flight) — grounded PACE-FPCA/elastic-multinomial/ITP scalars + primers; `anthropic<1.0` pin; version-independent guard-sync test (completed 2026-08-23)
- [x] Phase 51: Comparative Method-Selection — deterministic fdars winner + "comparison" task family + LLM-free MCP tool (completed 2026-08-24)
- [x] Phase 52: Pipeline Diagnostic Report — per-stage provenance + Python cross-stage caveats + LLM-free MCP tool (completed 2026-08-30)
- [x] Phase 53: Closed-Loop Auto-Tuning (capstone) — bounded propose→apply→re-run→compare loop; Python-API (LLM delta) + LLM-free heuristic MCP tool (completed 2026-08-30)
- [x] Phase 54: Eval Strategy + Docs Gate — deterministic eval + 3 pages/SVGs + offline fences + `--strict` green + blocking human diagram review (completed 2026-08-31)

</details>

### 🚧 v9.0 scikit-learn API Compatibility (In Progress)

**Milestone Goal:** Add a scikit-learn-compatible estimator layer over `fdars` so functional-data methods plug natively into `Pipeline`, `GridSearchCV`, and `cross_val_score`, interoperate with native sklearn estimators, and offer the familiar `fit`/`transform`/`predict` ergonomics — with every wrapped estimator passing the full `check_estimator` battery, no exemptions.

**Hard constraints (apply to every phase):**

- **Full `check_estimator` compliance, NO exemptions** — no `expected_failed_checks` / `_xfail_checks`. Any fdars method that cannot pass the full battery is **EXCLUDED** from the sklearn layer (it remains available through the existing functional API) and recorded reason-coded in `sklearn/_coverage.py` — never exempted.
- **`[sklearn]` optional extra** (pinned `scikit-learn>=1.3,<1.7`) — the base package stays sklearn-free and imports with zero sklearn installed; `python/fdars/__init__.py` is NOT modified; `fdars.sklearn` gates in its own `__init__.py` exactly like `advisor`/`mcp`.
- **Plain-ndarray boundary** — estimators take `(n_obs, n_points)` ndarrays with `argvals` as a constructor param (default `np.arange(n_features)`); they call `fdars._native.*` directly and NEVER construct an `Fdata` internally (dtype side-effects break `check_estimator`).
- **NO `fdars-core` bump; NO advisor/MCP changes** — pure-Python layer over the current 0.23.0 bindings.

#### Phase 55: Compliance-Triage & Foundation

**Goal**: Establish the shared sklearn-contract base class + `[sklearn]` extra, then discover the definitive scope by skeletoning every candidate estimator and running the check battery — producing a per-estimator PASS / PASS-WITH-FIXES / EXCLUDE verdict before any real implementation.
**Depends on**: Nothing (first phase of v9.0)
**Requirements**: FND-01, FND-02, FND-03, FND-04, TRIAGE-01, TRIAGE-02, TRIAGE-03
**Success Criteria** (what must be TRUE):

  1. `import fdars` succeeds with zero sklearn installed; `import fdars.sklearn` without the extra raises an actionable `ImportError`; `python/fdars/__init__.py` is unchanged (`git diff` empty for that file).
  2. `_BaseFdarsEstimator(BaseEstimator)` stores `argvals` (and all constructor args) verbatim in `__init__`, resolves `self.argvals_` (default `np.arange(n_features)`) in `fit`, sets `n_features_in_` via `validate_data`, casts float32→float64 before native calls, and passes `clone`/`get_params`/`set_params` round-trips — verified by the tags-API compat shim exercising sklearn 1.3 and 1.6 paths.
  3. Every one of the ~30 candidate estimators has a skeleton run through `parametrize_with_checks` yielding a recorded PASS / PASS-WITH-FIXES / EXCLUDE verdict.
  4. `sklearn/_coverage.py` `EXCLUDED_METHODS` lists every excluded fdars method with its failing-check / structural reason; each excluded method is confirmed still callable through the existing functional API.
  5. The go/no-go gate confirms a viable core PASSes (≈1 FPCA, 2 smoothers, 2 regressors, 2 classifiers, 1 clusterer, 2 outlier detectors) before any family implementation begins.

**Plans**: 3/3 plans executed
**Notes**: Mandatory-first — under the no-exemptions rule, scope is DISCOVERED by triage, not assumed. Flag for a research-phase during `/gsd-plan-phase` if the tags-API compat shim (`sklearn-compat` vs hand-rolled try/import guard) or the triage harness needs it. Guards for the 1-sample / 1-feature error-substring contracts (`"1 sample"`, `"1 feature(s)"`, etc.) and FPCA SVD sign canonicalization live in the base class / per-estimator wrappers.

Plans:

- [x] 55-01-PLAN.md — Tracer: [sklearn] extra + gated subpackage + _BaseFdarsEstimator (compat shim) + FPCATransformer passing parametrize_with_checks end-to-end
- [x] 55-02-PLAN.md — Skeleton the remaining ~30 candidates across all five families + run the full parametrize_with_checks battery (triage_results.txt)
- [x] 55-03-PLAN.md — Populate _coverage.py verdicts + EXCLUDED_METHODS, verify excluded-still-callable, assert the go/no-go viable-core gate

#### Phase 56: Transformers

**Goal**: Ship the transformer family — with `FPCATransformer` (the central grid-changing hub the predictors consume) built and validated first — as fully `check_estimator`-compliant `TransformerMixin` estimators.
**Depends on**: Phase 55
**Requirements**: XFORM-01, XFORM-02, XFORM-03, XFORM-04, XFORM-05, XFORM-06
**Success Criteria** (what must be TRUE):

  1. `parametrize_with_checks` is green for `FPCATransformer`, which maps `(n_obs, n_points)` → `(n_obs, n_components)` scores with SVD sign canonicalization (fit is idempotent under `check_fit_idempotent`).
  2. B-spline and local-polynomial smoothing transformers, imputation + spline-interpolation transformers, a basis-representation transformer, and a depth transformer are each `check_estimator`-green `TransformerMixin` estimators.
  3. A `Pipeline([smoother, fpca])` round-trips fit → transform end-to-end (the grid-changing chain works).
  4. Every transformer calls `fdars._native.*` directly with validated ndarrays and never constructs an `Fdata`.

**Plans**: 1/3 plans executed
**Notes**: FPCATransformer first (unlocks the whole Pipeline story). Only estimators the Phase-55 triage marked PASS / PASS-WITH-FIXES are wrapped; anything EXCLUDE stays in `_coverage.py`. Research flag: if the PASS-WITH-FIXES list is large, a short targeted check for exact per-sklearn-version error-message substrings may be warranted.
**UI hint**: no

Plans:

- [x] 56-01-PLAN.md — Promote Imputer to full green (tracer) + regression-guard the 5 already-PASS transformers + fast per-transformer compliance harness
- [ ] 56-02-PLAN.md — Promote BasisRepresentation (1-feature guard) + SplineInterpolator (idempotent grid, y=None, order guard) to full green; flip verdicts to PASS
- [ ] 56-03-PLAN.md — Pipeline([smoother, fpca]) round-trip (XFORM-06) + FPCA idempotence guard (XFORM-01) + Fdata-free contract test

#### Phase 57: Regressors & Classifiers

**Goal**: Ship the regressor and classifier families as fully `check_estimator`-compliant `RegressorMixin` / `ClassifierMixin` estimators, reusing the base-class + FPCATransformer patterns, and prove a full predictive pipeline under hyperparameter search.
**Depends on**: Phase 56
**Requirements**: REG-01, REG-02, CLF-01, CLF-02, PRED-01
**Success Criteria** (what must be TRUE):

  1. FPC-based functional regression and PLS regression are `check_estimator`-green `RegressorMixin` estimators exposing a working `score()`.
  2. Differentiator regressors that passed triage (robust FPC regression, Gaussian-only GLM, nonparametric regression) are `check_estimator`-green `RegressorMixin` estimators.
  3. FPC-based classifiers (logistic, LDA, QDA, KNN) are `check_estimator`-green `ClassifierMixin` estimators, each using `LabelEncoder` in `fit` and storing `X_fit_`/`y_fit_` where the underlying method re-fits at predict time; DD-classifier and elastic-multinomial are wrapped where triage passed.
  4. A `Pipeline([imputer, smoother, fpca, classifier])` wrapped in `GridSearchCV` fits and predicts end-to-end.

**Plans**: TBD
**Notes**: Standard patterns established in Phases 55–56 — skip research-phase. Non-Gaussian GLM / list-of-matrices / IrregFdata-input methods that triage marked EXCLUDE stay in `_coverage.py`.

Plans:

- [ ] 57-01: TBD

#### Phase 58: Clusterers & Outlier Detectors + Compliance Gate

**Goal**: Ship the clusterer and outlier-detector families as fully compliant `ClusterMixin` / `OutlierMixin` estimators, then — with all five families now present — lock the full-matrix compliance gate and prove native-sklearn interop.
**Depends on**: Phase 57
**Requirements**: CLUS-01, CLUS-02, OUT-01, OUT-02, COMPLY-01, COMPLY-02
**Success Criteria** (what must be TRUE):

  1. `FunctionalKMeans` is a `check_estimator`-green `ClusterMixin` estimator, deterministic under a fixed `random_state`; fuzzy c-means / functional GMM are wrapped where triage passed.
  2. The classic outlier trio (LRT, outliergram, magnitude-shape) — plus newer detectors (tvdmss, muod, depthgram) where triage passed — are `check_estimator`-green `OutlierMixin` estimators with a continuous `decision_function` and `predict` (a continuous score synthesized for index-list-returning methods).
  3. `parametrize_with_checks` is green for every wrapped estimator across all five families with zero exemptions, run as a CI job across the Python 3.9–3.14 matrix exercising both the sklearn 1.3–1.5 and 1.6 API paths.
  4. Interop is proven: an fdars transformer feeds a native sklearn estimator (e.g. `FPCATransformer` scores → `RandomForestClassifier`) inside one `Pipeline`.

**Plans**: TBD
**Notes**: Clusterers/outliers separated for their determinism (fixed-`random_state` reproducibility of rayon-parallel paths — confirm in planning) and synthesized-`decision_function` specifics. The full-matrix `parametrize_with_checks` gate naturally lands here once every family exists; `_coverage.py` is finalized.

Plans:

- [ ] 58-01: TBD

#### Phase 59: Documentation & Docs Gate

**Goal**: Publish a method-accurate "scikit-learn API" docs section — concept page + per-family reference pages + the coverage/EXCLUDE list + offline Pipeline & GridSearchCV worked examples + hand-authored SVG(s) — gated by a green whole-site `--strict` build and blocking human diagram review, then bump the package version at close.
**Depends on**: Phase 58
**Requirements**: DOCS-01, DOCS-02, DOCS-03, REL-01
**Success Criteria** (what must be TRUE):

  1. A "scikit-learn API" section is wired into MkDocs nav: a concept/overview page + per-family reference pages + the published coverage/EXCLUDE list.
  2. Offline `FDARS_FENCE_OK` worked examples exist (including a `Pipeline` example and a `GridSearchCV` example) and the whole-site `mkdocs build --strict` runs green offline.
  3. Method-accurate hand-authored inline SVG diagram(s) (layer architecture / data flow) meet the v7.0 STYLE_SPEC + SVGO-idempotence bar and pass a blocking human diagram review before close.
  4. Package version is bumped 0.8.0 → 0.9.0 and the `[sklearn]` extra is documented in packaging.

**Plans**: TBD
**Notes**: Docs last — offline fences require working estimators. MUST run sequentially on `main`, NOT in worktrees (standing v6.0 rule: doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path; `use_worktrees: false`). Docs build is ~19–25 min with executed fences — keep new fence data small and use the offline path (no network in the docs build). Package bump at close; a semver `vX.Y.Z` tag triggers PyPI publish.
**UI hint**: no

Plans:

- [ ] 59-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 55 → 56 → 57 → 58 → 59

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 55. Compliance-Triage & Foundation | v9.0 | 3/3 | Complete    | 2026-08-31 |
| 56. Transformers | v9.0 | 1/3 | In Progress|  |
| 57. Regressors & Classifiers | v9.0 | 0/TBD | Not started | - |
| 58. Clusterers & Outlier Detectors + Compliance Gate | v9.0 | 0/TBD | Not started | - |
| 59. Documentation & Docs Gate | v9.0 | 0/TBD | Not started | - |
