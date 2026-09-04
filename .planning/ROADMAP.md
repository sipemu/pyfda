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
- 🚧 **v11.0 — fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs** — Phases 66–73 (in progress)

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

### 🚧 v11.0 fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs (In Progress)

**Milestone Goal:** Bump `fdars-core` 0.23.0 → 0.33.0 (parallel-only, no linalg), expose the new upstream surface as PyO3 bindings + Python API, extend the AI advisor where relevant (grounding invariant preserved), and document it to the method-accurate standard. Isolated-bump → parallel-binding-groups → advisor → docs shape, same as v4.0/v5.0/v6.0. Phase numbering continues from v10.0's Phase 65 — this milestone starts at Phase 66.

- [x] **Phase 66: Isolated Crate Bump + Regression Gate** — Bump 0.23.0 → 0.33.0, gate on the full ~772-test suite, record the 0.24–0.33 changelog/match-arm audit (completed 2026-09-02)
- [x] **Phase 67: Functional Time Series (`fdars.fts`)** — New `fdars.fts` submodule: FTSM fit/forecast, ACF/PACF/stationarity/long-run-covariance, fPLSR/DPCA (completed 2026-09-02)
- [x] **Phase 68: Function-on-Function & Scalar-on-Function Regression** — `fof_regression` + random effects extending `fdars.regression`; additive/generalized SoF models + variable/model selection extending `fdars.scalar_on_function` (completed 2026-09-02)
- [x] **Phase 69: Fréchet Regression & Density FDA** — `convert.rs` ragged-list refactor, then new `fdars.frechet` and `fdars.density_fda` submodules (completed 2026-09-03)
- [x] **Phase 70: Multi-Domain Data, FAMM & Advanced Clustering** — `PyMultiFunData` handle → mixed-model FAMM → multivariate SPM (sequential) + advanced clustering (completed 2026-09-04)
- [x] **Phase 71: Shapelets & GAK Metric** — New `fdars.shapelet` submodule (`PyShapeletFit` + 2 enums) + Global-Alignment-Kernel metric extending `fdars.metric` (completed 2026-09-04)
- [ ] **Phase 72: Advisor Extension** — New `fts`/`frechet` aspects + extended `regression`/`classification`/`spm` aspects; grounding invariant + atomic MCP guard-sync
- [ ] **Phase 73: Documentation & Release** — One method-accurate page + hand-authored SVG + offline fence per new family; whole-site `--strict` green; human diagram review; package 0.9.0 → 0.10.0 + tag `v0.10.0`

#### Phase 66: Isolated Crate Bump + Regression Gate

**Goal**: The pinned crate moves 0.23.0 → 0.33.0 on a proven-green baseline, isolating the sole numeric change (10-minor drift risk) from all binding work so binding-correctness issues can't hide behind an upgrade regression.
**Depends on**: Nothing (first phase of this milestone; continues from v10.0's Phase 65)
**Requirements**: DEP-01, DEP-02, DEP-03
**Success Criteria** (what must be TRUE):

  1. `fdars-core` is pinned at `0.33.0` (parallel feature only, no linalg) in `Cargo.toml` + `Cargo.lock`, and `maturin develop` builds green (MSRV 1.83 unchanged)
  2. The full existing Python suite (~772 tests) passes with zero new failures against the bumped crate; any numeric-tolerance change is documented (expected: none)
  3. A recorded 0.24→0.33 changelog + API audit confirms every existing `match`-arm/enum-variant string in `src/*_mod.rs` still exists at 0.33, and flags the four 0.30-deprecated 2D depth functions for later migration
  4. Only `Cargo.toml` and `Cargo.lock` change in this phase — no new bindings, no test edits

**Plans**: 1/1 plans executed

- [x] 66-01-PLAN.md — bump fdars-core 0.23→0.33 (Cargo.toml/lock), maturin build gate, full pytest regression gate, and 0.24→0.33 changelog + enum/match-arm API audit (flag 4 deprecated 2D depth fns)

**Parallelizable**: No — sequential regression gate; must land before any binding phase.

#### Phase 67: Functional Time Series (`fdars.fts`)

**Goal**: Users can fit and forecast functional time series and compute time-series diagnostics through a new importable `fdars.fts` submodule.
**Depends on**: Phase 66
**Requirements**: FTS-01, FTS-02, FTS-03
**Success Criteria** (what must be TRUE):

  1. `import fdars.fts` works; users can fit an FTSM model and produce single- and multi-step forecasts, receiving a documented PyDict result that is transposition-correct on non-square (`n_obs ≠ n_points`) input
  2. Users can compute `functional_acf` / `functional_pacf`, run a stationarity test, and compute a long-run covariance, with deterministic results where the upstream function accepts a seed
  3. Users can call the dimension-reduction/forecasting extras available at 0.33 (`fplsr` and/or `dpca`), each returning a documented PyDict

**Plans**: 5/5 plans executed (tracer-first; 4 sequential waves — all touch `src/fts_mod.rs` + `tests/test_fts.py`)

- [x] 67-05-PLAN.md

- [x] 67-01-PLAN.md — TRACER: register `fdars.fts` submodule + bind `ftsm` end-to-end (lib.rs + __init__.py + fts_mod.rs), non-square (40×25) ftsm test green
- [x] 67-02-PLAN.md — Forecasting family: `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update` (combined-function pattern) + `fplsr`
- [x] 67-03-PLAN.md — Diagnostics family: `functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance` (seed-deterministic)
- [x] 67-04-PLAN.md — Spectral/DR family: `spectral_density`, `dpca`, `dpca_reconstruct` (combined-function pattern) — completes all 13 functions

**Parallelizable**: Yes at the phase level — new `src/fts_mod.rs`, disjoint from other binding groups; can run in a worktree in parallel with Phases 68, 69, 71. Internally sequential: all four plans append to the same `src/fts_mod.rs` + `tests/test_fts.py`, so they run in wave order 1→2→3→4.

#### Phase 68: Function-on-Function & Scalar-on-Function Regression

**Goal**: Users can run function-on-function regression (including random effects) and the new additive/generalized scalar-on-function models with variable/model selection, closing a visible gap in the existing regression surface.
**Depends on**: Phase 66
**Requirements**: REG-01, REG-02, REG-03
**Success Criteria** (what must be TRUE):

  1. `fof_regression` (+ `predict`) is callable via `fdars.regression`, returning a `beta`-surface/result PyDict, transposition- and `argvals`-guarded
  2. `fof_re_regression` (+ `predict_fof_re`) is callable with subject-id validation for the random-effects structure
  3. Additive/generalized SoF models (`fam`, `fregre_gkam`, `fregre_gsam`) and selection routines (`variable_selection`, `model_selection_ncomp`) are callable via `fdars.scalar_on_function`

**Plans**: 3/3 plans executed

- [x] 68-01-PLAN.md — Tracer: `fof_regression` bound end-to-end into `fdars.regression` (dual-2D, `beta_surface (m_y,m_x)` shape) [REG-01]
- [x] 68-02-PLAN.md — FOF family: `predict_fof`, `fof_cv`, `fof_re_regression` (subject-id validation), `predict_fof_re` [REG-01, REG-02]
- [x] 68-03-PLAN.md — New `fdars.scalar_on_function` submodule: `fam`, `fregre_gsam`, `fregre_gkam`, `variable_selection`, `model_selection_ncomp` [REG-03]

**Parallelizable**: Yes — extends `src/regression_mod.rs` / `scalar_on_function`; disjoint from other groups' module files; can run in a worktree in parallel with Phases 67, 69, 71.

#### Phase 69: Fréchet Regression & Density FDA

**Goal**: Users can run Fréchet (metric-space) regression/ANOVA and density-valued FDA transforms through two new submodules, backed by a shared ragged-list input helper factored into the conversion layer.
**Depends on**: Phase 66
**Requirements**: FRE-01, FRE-02, FRE-03
**Success Criteria** (what must be TRUE):

  1. The shared `extract_ragged_vecs` helper is factored into `src/convert.rs` (out of `pace_fpca_mod.rs`), validated on non-uniform per-observation lengths, and used by the density/Fréchet inputs
  2. `import fdars.frechet` works; users can compute `frechet_mean`, `frechet_global_reg`, `frechet_local_reg`, and `frechet_anova` (metric-space backend chosen by string dispatch with an `Err` fallback arm), each returning a documented PyDict
  3. `import fdars.density_fda` works; users can run `lqd_transform` / `inverse_lqd`, `lqd_fpca`, `wasserstein_barycenter`, and `normalize_density`

**Plans**: 5/5 plans executed

Plans:

- [x] 69-05-PLAN.md

- [x] 69-01-PLAN.md — FRE-03: relocate `extract_list_of_vecs` → `convert::extract_ragged_vecs` (caller_name param), rewire pace_fpca (behavior-preserving), ragged-input test [wave 1]
- [x] 69-02-PLAN.md — FRE-01 (tracer): register `fdars.frechet` + density-default `frechet_anova` (tracer) → `frechet_global_reg` → `frechet_local_reg` [wave 2]
- [x] 69-03-PLAN.md — FRE-01: `frechet_mean` monomorphized 3-space dispatch (spd/spherical/correlation) + per-space marshalling/validation + Err wildcard arm [wave 3]
- [x] 69-04-PLAN.md — FRE-02: register `fdars.density_fda` + `normalize_density` (tracer) → `lqd_transform`/`inverse_lqd`/`wasserstein_barycenter` (naked arrays) → `lqd_fpca` (6-key dict) [wave 4]

**Parallelizable**: Yes at phase level — new `src/frechet_mod.rs` + `src/density_fda_mod.rs`; the `convert.rs` refactor is an internal prerequisite sequenced first WITHIN this phase. Can run in a worktree in parallel with Phases 67, 68, 71. Internally SEQUENTIAL (waves 1→2→3→4): 69-02/03 both write `src/frechet_mod.rs` and all four touch `src/lib.rs`/`__init__.py` + rebuild.

#### Phase 70: Multi-Domain Data, FAMM & Advanced Clustering

**Goal**: Users can construct multi-domain functional data and pass it to mixed-model (FAMM) and multivariate SPM bindings, and run the advanced clustering methods added at 0.33.
**Depends on**: Phase 66
**Requirements**: MULTI-01, MULTI-02, MULTI-03, MULTI-04
**Success Criteria** (what must be TRUE):

  1. A new `PyMultiFunData` opaque `#[pyclass]` handle (mirroring `PyIrregFdata`) plus a builder from component curves is registered and constructible from Python
  2. Mixed-model bindings (`dense_flmm`, `fast_fmm`, `multi_famm`) are callable, consuming `PyMultiFunData` where required, returning documented PyDicts
  3. Multivariate/multi-domain SPM bindings (e.g. MFPCA / multi-domain monitoring) extend `fdars.spm`, built AFTER `PyMultiFunData` within this phase (internal sequential dependency)
  4. Advanced clustering (`dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd`) is callable, each returning a labels/result PyDict, transposition-guarded

**Plans**: 4/4 plans executed (tracer-first; 4 sequential waves — worktrees disabled; shared `src/lib.rs`/`__init__.py` + rebuild)

- [x] 70-01-PLAN.md — TRACER: `PyMultiFunData` opaque handle + `multi_fdata_from_components` builder → new `fdars.multi_fdata` submodule (standalone container; not consumed downstream in 0.33) [MULTI-01, wave 1]
- [x] 70-02-PLAN.md — new `fdars.famm` submodule: `dense_flmm` (tracer, 14-key) → `fast_fmm` (6-key) → `multi_famm` (4-key) — plain 2D inputs, none consume the handle [MULTI-02, wave 2]
- [x] 70-03-PLAN.md — extend `fdars.spm`: `mfpca` (6 public-field dict) + `spe_multivariate` ((n,) array) — built after PyMultiFunData; only phase touching `spm_mod.rs` [MULTI-03, wave 3]
- [x] 70-04-PLAN.md — extend `fdars.clustering`: `dbscan_fd` (int64 -1-noise) → `kcfc_cluster`/`funfem_cluster` → `align_cluster_fd` — transposition-guarded [MULTI-04, wave 4]

**Parallelizable**: No (worktree-sharing) — this is the ONLY group touching `src/spm_mod.rs`, and it carries an internal sequential dependency (`PyMultiFunData` builder MUST precede the SPM multivariate extensions). Run sequentially within itself; never share a worktree with another binding phase. Depends only on Phase 66, so it may still overlap the other binding phases as long as it uses its own isolated worktree.

#### Phase 71: Shapelets & GAK Metric

**Goal**: Users can discover and apply shapelets (with a fitted-state handle and classifier) and use the Global-Alignment-Kernel metric — including its Gram matrix as a precomputed sklearn kernel.
**Depends on**: Phase 66
**Requirements**: SHAPE-01, SHAPE-02
**Success Criteria** (what must be TRUE):

  1. `import fdars.shapelet` works; users can `discover_shapelets`, `shapelet_transform_fit` / `shapelet_transform`, `shapelet_classifier_fit`, and `shapelet_distance`, with a `PyShapeletFit` opaque handle
  2. The two new enums (`QualityMeasure`, `ShapeletClassifier`) are dispatched by string, each with an `Err` fallback arm that raises `ValueError` listing valid variants on invalid input
  3. GAK metric functions (`gak`, `gak_gram_matrix`, `gak_gram_train` / `gak_gram_predict`, `sigma_gak`) extend `fdars.metric`, with the Gram output usable as a precomputed kernel

**Plans**: 2/2 plans executed

- [x] 71-01-PLAN.md — SHAPE-01: new `fdars.shapelet` submodule (discover/transform_fit→PyShapeletFit/transform/classifier→PyShapeletClassifierFit/distance) + QualityMeasure/ShapeletClassifier string dispatch
- [x] 71-02-PLAN.md — SHAPE-02: GAK metric extending `fdars.metric` (gak/sigma_gak/gak_gram_matrix/gak_gram_train→PyGakGramTrain/gak_gram_predict) with precomputed-kernel Gram contract

**Parallelizable**: Yes — new `src/shapelet_mod.rs` + `metric` extension; disjoint from other groups' module files; can run in a worktree in parallel with Phases 67, 68, 69.

#### Phase 72: Advisor Extension

**Goal**: The AI advisor produces grounded diagnostics for the new capability families, with the grounding invariant and MCP guard-sync held as hard constraints.
**Depends on**: Phases 67, 68, 69, 70, 71 (needs the new functions live and callable)
**Requirements**: ADV-01, ADV-02
**Success Criteria** (what must be TRUE):

  1. New `fts` and `frechet` advisor aspects (diagnostics-only) exist, plus extensions of the existing `regression`/`classification`/`spm` aspects for the new methods, with every diagnostic a real fdars-computed native `float`/`int` scalar (no Python-derived or numpy scalars)
  2. MCP `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` guard-sync stays consistent — updated atomically with each aspect in a single commit; `test_guard_sync_version_independent.py` and a per-aspect `json.dumps(build_diagnostics(...))` serialization test pass
  3. The MCP compute path stays provably LLM-free (no LLM in the number path); `frechet` stays diagnostics-only (not added to `_RUNNABLE_METHODS`)

**Plans**: 4 plans
- [ ] 72-01-PLAN.md — fts aspect (tracer) + atomic guard-sync registration of fts+frechet across all 3 locations
- [ ] 72-02-PLAN.md — frechet aspect (anova/global_reg/local_reg/mean grounded branches)
- [ ] 72-03-PLAN.md — extend regression/classification/spm (fof/fam/gkam, shapelet handle, mfpca/spe_multivariate)
- [ ] 72-04-PLAN.md — grounding + LLM-free assertion + full advisor/guard-sync gate
**Parallelizable**: No — sequential; depends on all binding phases landing.

#### Phase 73: Documentation & Release

**Goal**: Every new capability family is documented to the project's method-accurate standard and the package is released, closing the milestone.
**Depends on**: Phase 72
**Requirements**: DOCS-01, DOCS-02, DOCS-03, REL-01
**Success Criteria** (what must be TRUE):

  1. One dedicated method-accurate page per new capability family (fts, fof/sof-regression, frechet, density-fda, multi-domain/FAMM, clustering, shapelet) is wired into `mkdocs.yml` nav, each with a runnable offline worked example emitting `FDARS_FENCE_OK`
  2. One hand-authored, STYLE_SPEC-conformant, SVGO-idempotent inline SVG concept diagram per new family exists, method-accurate against the shipped binding; advisor `aspects.md` is updated for the new/extended aspects
  3. Whole-site `mkdocs build --strict` passes green offline, and the blocking human diagram method-accuracy review is approved before close
  4. Package version is bumped `0.9.0 → 0.10.0` in `Cargo.toml` + `pyproject.toml` and tag `v0.10.0` is applied (triggers PyPI publish)

**Plans**: TBD
**UI hint**: no
**Parallelizable**: No — runs SEQUENTIALLY on `main` (`use_worktrees: false`); doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path, so a worktree executor would build the wrong tree and fail verification.

## Progress

**Execution Order:**
Phases execute in numeric order: 66 → 67 → 68 → 69 → 70 → 71 → 72 → 73. Phases 67–71 are additive binding groups that MAY run concurrently in isolated worktrees after 66 lands, with one exception: Phase 70 is the only `spm_mod.rs` writer and must not share a worktree with another binding phase. Phases 72 (advisor) and 73 (docs/release) are strictly sequential and last; 73 runs on `main`.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 66. Isolated Crate Bump + Regression Gate | v11.0 | 1/1 | Complete    | 2026-09-02 |
| 67. Functional Time Series (`fdars.fts`) | v11.0 | 5/5 | Complete    | 2026-09-02 |
| 68. Function-on-Function & Scalar-on-Function Regression | v11.0 | 3/3 | Complete    | 2026-09-02 |
| 69. Fréchet Regression & Density FDA | v11.0 | 5/5 | Complete    | 2026-09-03 |
| 70. Multi-Domain Data, FAMM & Advanced Clustering | v11.0 | 4/4 | Complete    | 2026-09-04 |
| 71. Shapelets & GAK Metric | v11.0 | 2/2 | Complete    | 2026-09-04 |
| 72. Advisor Extension | v11.0 | 0/TBD | Not started | - |
| 73. Documentation & Release | v11.0 | 0/TBD | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v10.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{...}-phases/`._
