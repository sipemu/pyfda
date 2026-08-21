# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (shipped 2026-08-17)
- ✅ **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** — Phases 30–35 (shipped 2026-08-18)
- 🚧 **v6.0 — fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference** — Phases 36–41 (in progress)

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

Made the fdars AI advisor work with any LLM backend (Anthropic, OpenAI/OpenAI-compatible, Google Gemini, local Ollama) through a custom `Provider` protocol, and gave every fdars analysis aspect its own advisor (diagnostics + grounded task families) — with the grounding invariant preserved on every backend. 28/28 requirements complete; suite 259 passed / 4 skipped. Full detail: `.planning/milestones/v3.0-ROADMAP.md`.

- [x] Phase 19: Provider Foundation & Grounding Contract — `Provider` protocol + Anthropic refactor + validate-and-retry + centralized `_check_grounding` (completed 2026-08-12)
- [x] Phase 20: Additional Provider Adapters — OpenAI (+ `base_url`), Ollama (local, no key), Gemini adapters as optional extras (completed 2026-08-12)
- [x] Phase 21: Per-Aspect Advisor Coverage — `build_diagnostics` + three grounded task families for all 12 fdars aspects via one shared schema/prompt (completed 2026-08-12)
- [x] Phase 22: Surface Integration — MCP exposes new aspect diagnostics (LLM-free); provider selection via Python `advise()`; Agent Skill documents coverage (completed 2026-08-12)
- [x] Phase 23: Packaging & CI — Python 3.9–3.14 matrix with version-gated extras + bare-venv smoke + aspect × provider offline grounding matrix (completed 2026-08-12)
- [x] Phase 24: Documentation — provider setup guide + per-aspect coverage page + updated overview/API pages; `mkdocs build --strict` offline (completed 2026-08-12)

</details>

<details>
<summary>✅ v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Phases 25–29) — SHIPPED 2026-08-17</summary>

Upgraded `fdars-core` 0.14.0 → 0.17.0 and exposed the new upstream functional-data capabilities (interpolation/imputation, functional statistics/scoring, shift registration/registration-quality/banded elastic alignment) through PyO3 bindings + the Python API, extended the v3.0 AI advisor to cover the relevant new capabilities (grounding invariant preserved), and documented everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Dependency-ordered: crate bump + regression gate first; two independent binding groups (parallel-eligible); advisor on top; docs last. 16/16 requirements complete; suite 426 passed / 4 skipped; whole-site `mkdocs build --strict` green offline. Full detail: `.planning/milestones/v4.0-ROADMAP.md`.

- [x] Phase 25: Crate Bump + Regression Gate — 0.17.0 pinned (parallel-only, no linalg), suite green, zero FPCA tolerance changes (completed 2026-08-14)
- [x] Phase 26: Interpolation, Imputation & Functional Statistics Bindings — `fdars.represent` + `fdars.fdata` stats + 6 Fdata methods; multi-curve transposition-tested (completed 2026-08-15)
- [x] Phase 27: Scoring Metrics & Alignment/Registration Bindings — `fdars.scoring` + shift registration (+ `fd.shift_register()`) + 3 quality scores + banded elastic alignment (completed 2026-08-15)
- [x] Phase 28: Advisor Extension — `scoring` aspect #13 + imputation-quality (represent) + registration-quality (alignment); grounding invariant + MCP guard-sync preserved (completed 2026-08-16)
- [x] Phase 29: Docs — Diagrams & Worked Examples — 6 new pages + 6 method-accurate hand-authored SVGs + offline FDARS_FENCE_OK worked examples; whole-site strict build green (completed 2026-08-17)

</details>

<details>
<summary>✅ v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Phases 30–35) — SHIPPED 2026-08-18</summary>

Upgraded `fdars-core` 0.17.0 → 0.20.0 (parallel-only, no `linalg`) and exposed the new upstream functional-inference + depth/boxplot + basis/smoothing surface through PyO3 bindings + the Python API — a new `fdars.inference` submodule (two-sample tests, Degras SCB bands, FLM post-hoc inference, one-way ANOVA V-statistic), `fdars.depth.functional_depth`/`functional_boxplot`, and `fdars.basis.constant_basis`/`smooth_basis_aic` + `optim_bandwidth(criterion="aic")` — extended the grounded advisor with an `inference` diagnostics aspect (#14; grounding invariant + guard-sync preserved), and documented it all to the method-accurate standard (new Inference nav section + functional-boxplot page + basis/smoothing fold-ins + advisor aspects.md; 4 hand-authored SVGs; human diagram review approved). Dependency-ordered: crate bump + regression gate first; three independent binding groups; advisor on top; docs last. 21/21 requirements complete; suite 560 passed / 4 skipped; whole-site `mkdocs build --strict` green offline. Full detail: `.planning/milestones/v5.0-ROADMAP.md`.

- [x] Phase 30: Crate Bump + Regression Gate — 0.20.0 pinned (parallel-only, no linalg) + `CvCriterion` wildcard arm; 426-test baseline green, zero drift (completed 2026-08-17)
- [x] Phase 31: Group A — `fdars.inference` Bindings — new submodule: two-sample permutation tests + SCB bands + FLM inference + ANOVA V-stat (`TestResult`/`ToleranceBand` → PyDict, deterministic seed) (completed 2026-08-17)
- [x] Phase 32: Group B — Depth/Boxplot Bindings — `functional_depth` dispatcher + `functional_boxplot` (7-key dict, transposition-guarded) extending `fdars.depth` (completed 2026-08-17)
- [x] Phase 33: Group C — Basis/Smoothing Quick Wins — `constant_basis` + `smooth_basis_aic` + `optim_bandwidth(criterion="aic")` (Phase-30 stopgap fixed) (completed 2026-08-17)
- [x] Phase 34: Advisor Extension — `inference` diagnostics aspect (#14); grounding invariant + MCP guard-sync (single atomic commit) preserved (completed 2026-08-17)
- [x] Phase 35: Docs — Diagrams & Worked Examples — new Inference section + boxplot page + basis/smoothing fold-ins + aspects.md; 4 method-accurate hand-authored SVGs; whole-site strict build green; human review approved (completed 2026-08-18)

</details>

### 🚧 v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (Phases 36–41)

Bump the pinned `fdars-core` 0.20.0 → 0.23.0 (parallel-only, no `linalg`; MSRV verified 1.81 ≤ 1.83) and expose the new upstream surface through PyO3 bindings + the Python API across three independent capability groups — Group A Regression (`concurrent_regression` + `functional_glm` extending `fdars.regression`), Group B FPCA & Classification (`pace_fpca` on a new sparse/irregular `IrregFdata` input + `elastic_multinomial` extending `fdars.classification`), Group C Depth/Outliers/Interval-Inference (9 new depth methods + 4 outlier detectors extending `fdars.outliers` + 3 interval-wise tests extending `fdars.inference`) — extend the grounded advisor where a real grounded scalar exists (extend the `outliers` aspect, closing the v5.0 Phase-34 boxplot-outlier deferral; extend the `regression` aspect; Group B advisor treatment decided at plan time), and document everything to the method-accurate standard (new pages + hand-authored inline SVGs + offline `FDARS_FENCE_OK` worked examples). Same shape as v4.0/v5.0: crate bump + regression gate first (BLOCKS everything), three independent binding groups (parallel-eligible after the bump — distinct `src/*_mod.rs` files), advisor on top (needs the shipped result dicts), docs last (run against the real shipped bindings).

- [x] **Phase 36: Crate Bump + Regression Gate** — Bump 0.20.0 → 0.23.0 (parallel-only, no linalg), wildcard fallback arms for any newly-`#[non_exhaustive]` upstream enums reached by existing code, full ~560-test suite green as the sole gate; isolated commit before any new binding work (completed 2026-08-20)
- [x] **Phase 37: Group A — Regression Bindings** — `concurrent_regression` (`beta_curve` `(p,m)` transposition-guarded) + `functional_glm` (`GlmFamily` string dispatch, re-fits FPCA internally; Gamma inverse-link + AIC caveat) extending `fdars.regression` (completed 2026-08-20)
- [x] **Phase 38: Group B — FPCA & Classification Bindings** — new `src/pace_fpca_mod.rs`: `IrregFdata` lists-of-arrays builder + `pace_fpca`; `elastic_multinomial` (CR-01 label guard) extending `fdars.classification` [IrregFdata interface spike at plan time] (completed 2026-08-21)
- [x] **Phase 39: Group C — Depth/Outliers/Interval-Inference Bindings** — 9 new `DepthMethod` variants + 4 outlier detectors (`tvdmss`/`muod`/`sequential_transform_outliers`/`depthgram`) + 3 ITP tests (`itp_one_pop`/`itp_two_pop`/`itp_flm`) with a new `itp_result_to_pydict` [outliers seed audit spike at plan time] (completed 2026-08-21)
- [ ] **Phase 40: Advisor Extension** — extend the `outliers` aspect (new detector scalar diagnostics; closes the Phase-34 deferral) + the `regression` aspect (GLM deviance/AIC, concurrent fit summary); Group B advisor coverage decided at plan time; grounding invariant + MCP guard-sync (single atomic commit) preserved [ADV-05 feasibility spike at plan time]
- [ ] **Phase 41: Docs — Diagrams & Worked Examples** — new Regression / PACE-FPCA + elastic-multinomial / depth-outliers-inference pages + method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples; advisor aspects.md update; whole-site `mkdocs build --strict` green; blocking human diagram review

## Phase Details (v6.0)

### Phase 36: Crate Bump + Regression Gate

**Goal**: `fdars-core` is pinned at 0.23.0 and the entire existing binding + advisor suite still passes, on a green baseline, before any new binding work begins.
**Depends on**: Nothing (first phase of v6.0; continues from v5.0 Phase 35)
**Requirements**: DEP-05, DEP-06
**Success Criteria** (what must be TRUE):

  1. `Cargo.toml` pins `fdars-core = { version = "0.23.0", features = ["parallel"] }` (no `linalg`) and `maturin develop` builds green — the bump is a single-field dependency diff (0.21/0.22/0.23 all additive/non-breaking).
  2. Any upstream enum that became `#[non_exhaustive]` at 0.23 and is reached by existing pyfda code carries a wildcard `_ => PyValueError` fallback arm — the crate does NOT compile without it.
  3. The full existing binding + advisor suite (~560 tests) passes unchanged — no new tests, no tolerance relaxations — as the sole success criterion.
  4. The bump lands as an isolated commit before any new-binding work, so any downstream binding issue cannot hide behind an upgrade regression.

**Plans**: 1 plan

- [x] 36-01-PLAN.md — Bump fdars-core 0.20.0→0.23.0 (parallel-only, no linalg), rebuild via maturin develop, and run the full existing suite as the regression gate (zero failures)

**UI hint**: no

### Phase 37: Group A — Regression Bindings

**Goal**: Users can fit a concurrent (varying-coefficient) functional regression and an exponential-family functional GLM from the extended `fdars.regression` submodule, layout-correct across the numpy↔FdMatrix boundary.
**Depends on**: Phase 36
**Requirements**: REGR-01, REGR-02, REGR-03
**Success Criteria** (what must be TRUE):

  1. User can call `fdars.regression.concurrent_regression(predictors, response, argvals, ...)` with `predictors` a `list[np.ndarray]` → a dict from `ConcurrentRegrResult`; the `beta_curve` field is shaped `(p, m)` (predictors × grid, NOT `(n_obs, m)`) and round-trips correctly, proven by a multi-predictor (`p ≥ 2`) transposition guard test.
  2. User can call `fdars.regression.functional_glm(data, response, argvals, family=..., n_comp=..., ...)` → a dict from `FunctionalGlmResult` (all fields exposed); `family` dispatches a `#[non_exhaustive]` `GlmFamily` (Binomial/Poisson/Gamma/Gaussian) by string with a `ValueError` wildcard fallback, and the wrapper re-fits FPCA internally (raw data in, no persistent handle).
  3. Both functions are registered in `src/regression_mod.rs` + `register_submodule!` with a `ConcurrentRegrResult`/`FunctionalGlmResult` → PyDict converter each; all fallible paths route through `to_pyresult()` (no `.unwrap()`); degenerate inputs (mismatched grids, too few curves, invalid family/ncomp) raise `ValueError`.
  4. The docs-facing caveats are captured for Phase 41: Gamma's inverse canonical link (1/μ) and the non-R-comparable `functional_glm` AIC magnitude.

**Plan-time spike**: confirm `ConcurrentRegrResult.beta_curve` orientation `(p, m)` against the multi-predictor transposition test (REGR-01).

**Plans**: 1 plan

- [x] 37-01-PLAN.md — `concurrent_regression` (tracer proves `list[np.ndarray]`→`Vec<FdMatrix>` binding + `beta_curve` `(p,m)` transposition guard) + `functional_glm` (all-14-field converter, `GlmFamily` string dispatch, embedded fpca kept internal, 4-family + domain guards) in `src/regression_mod.rs`

**UI hint**: no

### Phase 38: Group B — FPCA & Classification Bindings

**Goal**: Users can run sparse/irregular PACE functional PCA over a new ragged-grid `IrregFdata` input, and fit a K-class one-vs-rest elastic multinomial classifier, from a new `src/pace_fpca_mod.rs` and the extended `fdars.classification` submodule.
**Depends on**: Phase 36
**Requirements**: PACE-01, PACE-02, CLASS-01
**Success Criteria** (what must be TRUE):

  1. A sparse/irregular input path is exposed — `fdars.irreg_fdata_from_lists(argvals_list, values_list)` accepts two Python lists of 1-D arrays (ragged per-curve grids) and constructs the fdars-core CSR-layout `IrregFdata`; passing a plain dense 2-D array is rejected with a `ValueError` (never silently misinterpreted).
  2. User can call `fdars.pace_fpca(irreg_fdata, config...)` → a dict from `PaceFpcaResult` (all 10 fields incl. eigenfunctions `(m, ncomp)`, scores `(n, ncomp)`, per-curve confidence bands) with a struct-literal-safe `PaceFpcaConfig`; `eigenfunctions`/`scores` layout is transposition-guarded and `actual_ncomp` truncation is handled. Lives in the new `src/pace_fpca_mod.rs`.
  3. User can call `fdars.classification.elastic_multinomial(data, labels, argvals, ...)` → a dict from `ElasticMultinomialResult` (`train_probabilities` `(n, K)` transposition-guarded at `K ≥ 3`); labels must be 0-indexed contiguous (`0..K`) — a negative/non-contiguous-label guard (v5.0 CR-01 pattern) raises a helpful `ValueError` rather than wrapping `i64→usize`.
  4. All new functions are registered with `to_pyresult()` guards (no `.unwrap()`); degenerate inputs (mismatched list lengths, dense-array-to-IrregFdata, invalid ncomp/labels) raise `ValueError`.

**Plan-time spike**: `IrregFdata` list-of-arrays PyO3 constructor interface — no existing pyfda precedent; resolve before writing `pace_fpca` (PACE-01/PACE-02).

**Plans**: 1 plan

- [x] 38-01-PLAN.md — Tracer-first: pyfda's first `#[pyclass] PyIrregFdata` + `irreg_fdata_from_lists` + `pace_fpca` round-trip (novel-risk-first), then IrregFdata dense/ragged/outer-length `ValueError` guards, the full 10-key `pace_fpca` dict with eigenfunctions/scores `(m,ncomp)`/`(n,ncomp)` transposition guards + `actual_ncomp` truncation + determinism, and `elastic_multinomial` (CR-01 label guard, `(n,K)` proba guard, `class_models` omitted) extending `fdars.classification`; new `src/pace_fpca_mod.rs` + `lib.rs`/`__init__.py` registration

**UI hint**: no

### Phase 39: Group C — Depth/Outliers/Interval-Inference Bindings

**Goal**: Users gain 9 new functional-depth methods, 4 functional-outlier detectors, and 3 interval-wise tests — extending `fdars.depth`, `fdars.outliers`, and `fdars.inference` respectively — all deterministic offline and layout-correct across the numpy↔FdMatrix boundary.
**Depends on**: Phase 36
**Requirements**: DEPTH-03, OUTL-01, OUTL-02, OUTL-03, OUTL-04, ITP-01, ITP-02, ITP-03, ITP-04
**Success Criteria** (what must be TRUE):

  1. `fdars.depth.functional_depth(..., method=...)` (and `functional_boxplot`'s `method`) accepts the 9 new fdars-core 0.23 `DepthMethod` variants (`hypograph_index`, `modified_hypograph_index`, `epigraph_index`, `half_region`, `modified_half_region`, `extremal`, `extreme_rank_length`, `l_infinity`, `total_variation` — 13 total); the Python string map covers every new variant and the `#[non_exhaustive]` wildcard error message lists all supported methods.
  2. User can run all four outlier detectors — `fdars.outliers.tvdmss`, `.muod`, `.sequential_transform_outliers(transforms=[...])`, `.depthgram` — each returning a dict with outlier indices as a Python `list[int]` plus fdars-computed scores/threshold; `transforms` maps a `#[non_exhaustive]` `SeqTransform` by string with a `ValueError` wildcard fallback; any random component takes `seed=None` → fixed default for byte-identical offline reproducibility.
  3. User can run all three interval-wise tests — `fdars.inference.itp_one_pop(mu0=...)`, `.itp_two_pop(seed=None)`, `.itp_flm(basis_type=...)` — each returning an `ItpResult` dict with **vector** closure-adjusted p-values + unadjusted p-values + the test-statistic curve; `basis_type` maps a `#[non_exhaustive]` `ProjectionBasisType` by string with a `ValueError` fallback, and `itp_flm` re-fits internally (no persistent handle).
  4. The three ITP functions are registered in `src/inference_mod.rs` + `register_submodule!` via a **new** `itp_result_to_pydict` helper (distinct from `test_result_to_pydict`, since results are p-value vectors not scalars) exposing vectors as 1-D arrays; all fallible paths route through `to_pyresult()`; degenerate inputs raise `ValueError`.

**Plan-time spike**: audit `outliers_mod.rs` / fdars-core 0.23 outlier signatures for existing `seed` parameters; add seed exposure where random components exist (OUTL-01..04).

**Plans**: TBD
**UI hint**: no

### Phase 40: Advisor Extension

**Goal**: The grounded advisor's existing `outliers` and `regression` aspects surface grounded scalar diagnostics for the new detector and regression results, with the grounding invariant and the advisor/MCP guard-sync preserved.
**Depends on**: Phase 37 (regression bindings), Phase 39 (outlier-detector bindings)
**Requirements**: ADV-04, ADV-05
**Success Criteria** (what must be TRUE):

  1. The existing `outliers` aspect summarizes the new fdars-computed outlier-detector results as grounded scalar diagnostics (e.g. `n_outliers`, outlier fraction, score/threshold ranges — never raw index lists or numpy aggregates), closing the v5.0 Phase-34 functional-boxplot-outlier deferral; no new aspect key is added — `build_diagnostics` dispatch detects the new result-dict keys.
  2. The existing `regression` aspect surfaces grounded diagnostics for the new regression results (`functional_glm` deviance/AIC, `concurrent_regression` fit summary) wherever a real fdars-computed scalar is available; grounding invariant preserved.
  3. Any change to `_DIAGNOSTICS_METHODS`/`_RUNNABLE_METHODS`/`_supported` lands in a SINGLE atomic commit keeping `test_diagnostics_methods_match_advisor_supported` green; offline determinism is preserved (no numpy scalars, byte-identical `json.dumps`) and the LLM only interprets and cites diagnostic values.
  4. Group B advisor coverage (`pace_fpca` via the `fpca` aspect, `elastic_multinomial` via the `classification` aspect) is decided at plan time on feasibility — included only if a genuinely grounded scalar diagnostic exists, otherwise left as bindings + docs only.

**Plan-time spike**: confirm whether `pace_fpca` / `elastic_multinomial` expose a genuinely grounded scalar diagnostic before committing advisor coverage; finalize the exact outlier scalar spec (ADV-05).

**Plans**: TBD
**UI hint**: no

### Phase 41: Docs — Diagrams & Worked Examples

**Goal**: The published MkDocs site documents the new regression, PACE-FPCA/classification, and depth/outliers/interval-inference capabilities to the project's method-accurate standard, with the whole site building strict-green offline against the real shipped bindings.
**Depends on**: Phase 37, Phase 38, Phase 39, Phase 40
**Requirements**: DOCS-08, DOCS-09, DOCS-10, DOCS-11
**Success Criteria** (what must be TRUE):

  1. New/updated Regression docs cover `concurrent_regression` + `functional_glm` with method-accurate hand-authored inline SVG(s) + a runnable offline worked example emitting `FDARS_FENCE_OK` (small/synthetic or subsampled data), documenting the Gamma inverse link + AIC caveat.
  2. New FPCA/Classification docs carry a PACE-FPCA page (SVG showing irregular/sparse observations + recovered eigenfunctions; executed fence using small inline synthetic sparse data, `n ≤ 20`) and elastic-multinomial coverage (phoneme.csv subsampled to 3 classes, `m ≤ 64` for fence speed).
  3. New/updated Depth-Outliers-Inference docs fold the 9 new depth methods into the depth page, add a functional-outliers page for the 4 detectors (method-accurate SVG), and add an interval-wise-inference page for `itp_*` (SVG showing closure-adjusted p-value intervals, correct closure direction); each new page carries a runnable offline `FDARS_FENCE_OK` worked example.
  4. Advisor `aspects.md` is updated for the extended `outliers`/`regression` diagnostics; all new pages are wired into `mkdocs.yml` nav; whole-site `mkdocs build --strict` passes offline (exit 0); every new SVG is SVGO-idempotent and determinism-clean; a blocking human diagram method-accuracy review (rsvg-convert PNG check: depth asymmetry, PACE irregular observations, ITP closure direction) is satisfied before the milestone closes.

**Plans**: TBD
**UI hint**: yes

## Progress (v6.0)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 36. Crate Bump + Regression Gate | 0/? | Not started | - |
| 37. Group A — Regression Bindings | 0/1 | Planned | - |
| 38. Group B — FPCA & Classification Bindings | 0/1 | Planned | - |
| 39. Group C — Depth/Outliers/Interval-Inference Bindings | 0/? | Not started | - |
| 40. Advisor Extension | 0/? | Not started | - |
| 41. Docs — Diagrams & Worked Examples | 0/? | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v5.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1,3.0,4.0,5.0}-phases/`._
