# Milestones

## v11.0 fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs (Shipped: 2026-09-05)

**Phases completed:** 8 phases, 29 plans, 65 tasks

**Key accomplishments:**

- fdars-core bumped 0.23.0→0.33.0 (parallel only) with zero numeric drift confirmed by 5339-test green gate; 6 deprecated call sites suppressed via CONTINGENCY #[allow(deprecated)]; full API audit recorded in 66-AUDIT.md
- fdars.fts PyO3 submodule registered end-to-end with ftsm binding proven transposition-correct on a non-square (40x25) AR(1) fixture — 4 tests pass, build green, no warnings
- Four fts forecasting bindings via combined-function pattern: ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr — all transposition-correct on the non-square (40x25) fixture with 9/9 tests passing.
- Five FTS diagnostics functions bound: functional_acf/pacf (seed=42, int64 lags), functional_difference (naked array), stationarity_test (permutation p-value, deterministic), long_run_covariance (col-major reshape, symmetric 1e-10); FTS-02 complete with 21 passing tests
- `spectral_density` (per-frequency col-major reshape), `dpca`, and `dpca_reconstruct` (combined-function pattern) complete the 13-function `fdars.fts` submodule; all 27 fts tests pass on the non-square (N=40, M=25) fixture
- FND-02 rewritten to assert Phase-55 baseline _submodule_names ⊆ current set plus per-name import/attribute registration, eliminating the git-diff byte-freeze that broke on every new submodule addition
- fof_regression bound into fdars.regression via dual numpy2d_to_fdmatrix path, returning a 9-key PyDict with beta_surface shape (m_y, m_x) = (18, 25) proven on a 3-distinct-dim non-square fixture
- Four FOF functions bound to fdars.regression — combined-refit predict pattern, REG-02 subject-id validation, and 10 passing tests on a 3-distinct-dim (N=30, MX=25, MY=18) non-square fixture
- New `fdars.scalar_on_function` submodule binding five additive/selection functions (fam, fregre_gkam, fregre_gsam, variable_selection, model_selection_ncomp) via Default::default()+mutation for #[non_exhaustive] config structs and an Err-returning VarSelectPenalty wildcard arm
- Relocated `extract_list_of_vecs` from `pace_fpca_mod.rs` into `convert.rs` as public `extract_ragged_vecs(list, caller_name)`, rewired both pace_fpca call sites, and proved behavior unchanged via 20 passing tests.
- New `fdars.frechet` submodule with three density-default Fréchet functions (`frechet_anova` 9-key, `frechet_global_reg` / `frechet_local_reg` 3-key) using `numpy2d_to_fdmatrix` I/O; 21 tests pass on non-square (N=40, M=50, N_OUT=10) fixtures
- `frechet_mean` bound with monomorphized SPD/spherical/correlation string dispatch, per-space column-major marshalling, structural validation, and a ValueError wildcard arm — 35 tests green
- `fdars.density_fda` submodule registered with 5 functions: `normalize_density` (naked 1D), `lqd_transform` / `inverse_lqd` (naked 1D, LQD round-trip tested), `wasserstein_barycenter` (naked 1D), and `lqd_fpca` (6-key PyDict with `loadings` key for the rotation matrix).
- Route frechet_mean's spherical sample through convert::extract_ragged_vecs, closing FRE-03's "used by the Fréchet inputs" gap with zero behavior change
- PyMultiFunData opaque #[pyclass] handle — pyfda's second opaque Rust type — with a list-of-components builder, n_obs/n_components accessors, and three pre-constructor validation guards, registered as fdars.multi_fdata
- `fdars.famm` submodule binding `dense_flmm` (14-key REML-EM result), `fast_fmm` (6-key Wald result), and `multi_famm` (4-key multi-variable result with D per-dimension component dicts) from fdars-core 0.33's plain-FdMatrix FAMM API.
- mfpca (6-key PyDict: scores/eigenfunctions/eigenvalues/means/scales/grid_sizes) and spe_multivariate (naked (n,) array) added to fdars.spm via Vec<FdMatrix>/Vec<&FdMatrix> slice pattern; pub(super) fields excluded; 11 tests on non-square multi-variable fixture all pass
- Four advanced functional clustering algorithms (DBSCAN, KCFC, FunFEM, elastic-alignment) bound into `fdars.clustering` with documented labels/result PyDicts; all transposition-guarded on non-square fixtures; 4 tests passing.
- New `fdars.shapelet` submodule binding five shapelet functions + two opaque handles (`PyShapeletFit` wrapping `ShapeletTransformFit`, `PyShapeletClassifierFit` with `predict()`) + two string-dispatched `#[non_exhaustive]` enums with mandatory Err arms; all 24 shapelet+FND-02 tests green.
- PyGakGramTrain opaque handle + 5 GAK functions (gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict) added to fdars.metric with (n,n) and (n_test,n_train) sklearn precomputed-kernel shape contracts verified
- fts aspect builder created and registered end-to-end; frechet stub registered; both method strings added atomically across advisor _supported, server _DIAGNOSTICS_METHODS, and guard-sync test literal in ONE commit; 37 offline serialization tests pass
- Real frechet diagnostics builder with anova/global_reg/local_reg/frechet_mean branches using CONFIRMED PyDict keys from frechet_mod.rs; grounded native-Python scalars; JSON-serialisable; deterministic.
- Extends three existing advisor aspect builders for the v11.0 new methods (fof/fof_re/fam/gkam/shapelet/mfpca/spe_multivariate) with grounded, JSON-serialisable, numpy-scalar-free diagnostics; shapelet opaque-handle TypeError prevented by coercion guard in __init__.py.
- Extended test_advisor_grounding.py with fts/frechet native-scalar grounding cases and dual-mode LLM-free subprocess+in-process assertion; combined 273-test advisor/guard-sync gate green
- FTS page + FDARS_FENCE_OK fence + STYLE_SPEC-conformant 720x480 SVG diagram + Analyze nav wiring, proving the end-to-end docs authoring loop for the remaining 6 families
- Three Regression-section doc pages (FoF, Additive SoF, Frechet) with offline FDARS_FENCE_OK fences, three STYLE_SPEC 720x480 SVGO-idempotent SVG diagrams, and Regression nav entries — DOCS_FAST build green, check_docs_figures exit 0
- Four Analyze-section pages with offline FDARS_FENCE_OK fences, four STYLE_SPEC SVGO-idempotent SVGs, and nav entries — completing DOCS-01/DOCS-02 coverage for all Analyze families; API discrepancies from RESEARCH templates corrected via per-fence Python sanity checks.
- Advisor `aspects.md` updated for the v11.0 methods, whole-site `mkdocs build --strict` gate green, and all 8 new hand-authored SVG diagrams human-approved in the blocking diagram review
- Version bumped 0.9.0 → 0.10.0 in Cargo.toml + pyproject.toml and committed; PyPI release tag checkpoint handed to user

**Verification:** verified_closeout — all 8 phases (66–73) `phase_complete` + `verification_status: passed`; milestone audit PASSED (5650 tests, 24/24 requirements). Known verification overrides: 0 newly acknowledged, 2 carried forward from a prior close (see STATE.md Deferred Items).

---

## v10.0 Diagram Quality & Accessibility Pass (Shipped: 2026-09-02)

**Phases completed:** 6 phases, 7 plans, 9 tasks

**Key accomplishments:**

- 90 concept SVGs scored on 4 axes (design/geometry rsvg-render-backed, STYLE_SPEC grep-verified, accessibility text-matched, sync deferred) — 5 Major geometry defects found, STYLE_SPEC universally clean, A11Y gap universal Minor.
- 60-AUDIT.md completed: all 156 SVGs scored (90 concept + 8 cards + 58 thumbs); 1 Major thumb drift (elastic-clustering), 3 sklearn COVER-01 gaps, ranked 61/62/63 worklists + Phase-64 SYNC/COVER/A11Y-03 lists ready.
- Fixed 4 Major layout defects + 4 Minor geometry issues + applied A11Y-02 accessibility pattern to all 40 concept diagrams in regression/, inference/, and examples/ documentation buckets

---

## v9.0 scikit-learn API Compatibility (Shipped: 2026-09-02)

**Phases completed:** 5 phases, 17 plans, 24 tasks
**Git range:** `06d8919` → `98da2d0` (~107 commits, 117 files, +18,453 / −135) · 2026-08-31 → 2026-09-02
**Delivered:** `fdars.sklearn` — a pure-Python scikit-learn-compatible estimator layer over the current bindings. **28 estimators** across five families pass the full `check_estimator` battery with zero exemptions; native `Pipeline` / `GridSearchCV` / `cross_val_score` integration + proven interop with native sklearn estimators. Package 0.8.0 → 0.9.0, released to PyPI (tag `v0.9.0`).

**Key accomplishments:**

- Foundation & packaging (Phase 55) — `[sklearn]` optional extra + gated `fdars.sklearn` subpackage + shared `_BaseFdarsEstimator` (BaseEstimator contract, `argvals` constructor param, float32→64 cast, tags-API 1.3–1.8 feature-detect shim).
- Compliance triage (Phase 55) — ~30 candidates run through `check_estimator` → PASS/EXCLUDE verdicts + reason-coded `EXCLUDED_METHODS` registry; go/no-go GO on all six families.
- Transformers (Phase 56) — FPCA, B-spline/local-poly smoothers, imputer/interpolator, basis, depth as `TransformerMixin`; `Pipeline([smoother, fpca])` grid-changing chain.
- Regressors & classifiers (Phase 57) — FPC/PLS/GLM/nonparametric `RegressorMixin`; logistic/LDA/QDA/KNN/DD/elastic-multinomial `ClassifierMixin`; `Pipeline` + `GridSearchCV`.
- MagnitudeShapeDetector promoted to `check_estimator`-green `OutlierMixin` via stored-reference `modified_band_1d(X, X_fit_)` depth scoring (47/47 checks, zero exemptions), resolving Phase-57 CR-03 subset-invariance violation.
- LRTOutlierDetector, OutliergramDetector, TVDMSSDetector, MUODDetector, and DepthgramDetector promoted to `check_estimator`-green OutlierMixin via stored-reference `modified_band_1d(X, X_fit_)` depth scoring (282/282 checks, zero exemptions), completing OUT-01 and OUT-02.
- Full-matrix parametrize_with_checks gate over all 28 wrapped estimators locked with zero exemptions (COMPLY-01, 1387 checks); FPCATransformer → RandomForestClassifier Pipeline interop proven (COMPLY-02); sklearn-compliance CI job wired across Python 3.9–3.14.
- Documentation & release (Phase 59) — new "scikit-learn API" docs section (concept + per-family reference + coverage/EXCLUDE list + Pipeline & GridSearchCV worked examples + hand-authored data-flow SVG); whole-site `mkdocs build --strict` green offline; pkg bump + PyPI release.

**Verification:** Phases 55–58 VERIFICATION.md all `passed` (7/7, 10/10, 9/9, 14/14); whole `tests/sklearn/` suite 4294 passed / 0 failed. Milestone audit PASSED 28/28 (`.planning/milestones/v9.0-MILESTONE-AUDIT.md`).

**Closeout:** `override_closeout`. Phase 59 (Documentation & Docs Gate) shipped its deliverables (docs live, `--strict` green, tag `v0.9.0` on PyPI) but never received a formal `59-VERIFICATION.md` — closed via a user-approved verification override (verification-doc gap, not a deliverable gap). DOCS-03's blocking human diagram review was pre-verified method-accurate but never explicitly approved; now moot since the SVG is live. The 9 Phase-56 triage deferrals were resolved in-file (superseded by Phases 57–58, not exempted). Known verification overrides: 0 newly acknowledged, 2 carried forward from a prior close (see STATE.md Deferred Items).

---

## v8.0 Advisor: New Capabilities (Shipped: 2026-08-31)

**Phases completed:** 5 phases, 16 plans, 41 tasks

**Key accomplishments:**

- Three blocking compatibility fixes: anthropic pinned below 1.0, MCP v2 server + 3 tools regression-tested, and guard-sync assertion split into a version-independent test that runs on Python 3.9 without importing mcp.
- ITP vector-to-scalar reduction (detection+localisation), PACE-FPCA noise/signal and band-width scalars, elastic-multinomial overfitting gap, and extended primers for all three — all grounded native float/int, json.dumps clean, guard-sync unchanged.
- Offline aspect×provider matrix extended with PACE-FPCA/elastic-multinomial/ITP fixtures (6 new cases all passing _check_grounding); env-gated live coverage added for all three, CI stays network-free
- compare_methods(run_llm=True) path with fdars-authoritative winner and per-candidate labeled provenance blocks passed to the LLM; grounding checked per candidate (not against merged dict) so cross-candidate citation raises GroundingViolationError.
- fdars_compare_methods MCP tool — LLM-free multi-candidate deterministic ranking via re-run + compare_methods(run_llm=False), returning opaque handles only
- Per-stage list-of-blocks offline aggregation core for `build_pipeline_report()` with `{"_stages":[...]}` union-grounding payload, mirroring Phase-51's `{"_candidates":[...]}` provenance pattern
- Deterministic Python cross-stage caveat rule table (PIPE-03) + PipelineReport schema (PIPE-02) + pipeline_report() LLM narrative path under union grounding — caveats are Python-authoritative, LLM narrates, never invents
- `fdars_build_pipeline_report` LLM-free MCP tool: re-runs each pipeline stage, aggregates by-reference via the offline core, stays provably LLM-free, guard-sync no-op
- Bounded tuning loop state machine with injectable propose_fn, 5-mode termination (budget/converged/oscillation/guard_stop/parse_failure), TuneProposal/TuningTrace schemas, and an offline test suite proving all safety guarantees without API key or network.
- LLM-backed closed-loop tuning: auto_tune() drives the wave-1 loop core via a schema-validated, clamped propose_fn; the 'parameter_proposal' prompt clause forbids numeric predictions; all behavior proven offline with an injected FakeProvider.
- LLM-free `fdars_auto_tune` MCP tool driving the wave-1 loop core with a deterministic gradient-sign heuristic (bisection step decay; log-scale lambda_; int rounding); file-scan + determinism + by-reference + guard-sync confirmed offline.
- Deterministic eval fixtures for 'good advice' — known-from-data comparative winner and auto-tune improving-direction assertions, fully offline via FakeProvider and injectable seams (EVAL-01, EVAL-02)
- Three method-accurate, STYLE_SPEC-conformant, SVGO-idempotent inline SVGs for comparative selection (fdars-authoritative winner), pipeline report (per-stage provenance + Python caveats), and auto-tuning (bounded propose→clamp→re-run→compare loop) — all three grounded in shipped 50–53 code semantics.
- Three mature-structure pages (comparative-selection, pipeline-report, auto-tuning) with embedded Plan-02 SVGs and offline FDARS_FENCE_OK worked examples; aspects.md updated with PACE-FPCA noise/signal, ITP detection+localisation, and elastic-multinomial overfitting scalars; AI Advisor nav wired in mkdocs.yml.
- 2026-08-31 (orchestrator-driven gate; the human-review task is `autonomous: false`)

---

## v7.0 v7.0 (Shipped: 2026-08-23)

**Phases completed:** 8 phases, 9 plans, 9 tasks

**Key accomplishments:**

- Full 61-diagram 4-axis scored inventory — visual/STYLE_SPEC/XML/method-accuracy — with ranked fix list (43=25, 44=17, 45=19), coverage-gap list (20 examples + 5 advisor pages), and thin-page list (8 confirmed + 2 borderline) gate the entire v7.0 milestone.
- Hand-authored SVG corrections across learn/represent/align batch — Panel-3 ghost removal, PACE subtitle overflow fix, banded-alignment label re-anchor, and full STYLE_SPEC migration of ex-sonar-tsrvf.svg (700→720 viewBox, canonical five CSS classes, role/aria).
- De-cramped elastic-multinomial.svg to 720×480, improved scalar-on-function β̂(t) inset prominence, and confirmed functional-glm Gamma inverse-link annotation correct; zero redundant overrides across all four diagrams.
- 9 method-accurate workflow SVGs authored for the canadian-weather tracer + 4 canadian + 4 andrews-wine example pages, all STYLE_SPEC-conformant, svgo-idempotent, and embedded via `.fdars-diagram`.
- 11 method-accurate workflow SVGs authored across tecator (regression/conformal/monitoring), monitoring (penicillin/inline), and misc (cross-validation/explainability/outliers/growth/phoneme/tolerance) example pages — completing 20/20 DIACOV-01 gap coverage.
- Extended three method pages with new executable worked examples (binomial+poisson GLM, PACE-vs-standard-FPCA, ITP-vs-t_perm_test) — all fences verified offline under `.venv`.

---

## v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (Shipped: 2026-08-22)

**Phases completed:** 6 phases, 11 plans, 16 tasks

**Key accomplishments:**

- (none recorded)

---

## v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Shipped: 2026-08-18)

**Phases completed:** 6 phases, 11 plans, 17 tasks

**Key accomplishments:**

- fdars-core pinned at 0.20.0 (parallel-only) with CvCriterion #[non_exhaustive] wildcard arm; 426-test regression baseline confirmed green with zero numeric drift
- New `fdars.inference` submodule (8 functions: two-sample permutation tests, Degras SCB bands, FLM post-hoc inference re-fitting `fregre_lm` internally, and one-way ANOVA V-statistic), registered and importable; `TestResult`/`ToleranceBand` → PyDict, deterministic `seed=None`→0; degenerate inputs raise `ValueError` (incl. a negative-group-label guard from code review)
- Unified string-dispatched `functional_depth` + `functional_boxplot` with 7-key dict contract and layout-guard tests, extending `fdars.depth` via fdars-core 0.20 dispatch functions.
- AIC model selection added for kernel bandwidth (optim_bandwidth), basis smoothing (smooth_basis_aic), and intercept column (constant_basis) via three additive PyO3 bindings against fdars-core 0.20.
- Created the Functional Inference page with three method-accurate hand-authored SVGs and four offline executed fences covering two-sample tests, SCB bands, one-way functional ANOVA, and FLM inference.
- Functional Boxplot page with López-Pintado–Romo depth-fence theory, STYLE_SPEC-conformant SVG (median/50% central region/whiskers/outliers), executed Canadian Weather fence emitting FDARS_FENCE_OK, and Analyze nav wiring.
- docs/represent/basis-representation.md
- Whole-site `mkdocs build --strict` (19 min, exit 0) + SVGO idempotence (all 4 new SVGs PASS) + pytest green (560 passed / 4 skipped) — halted at blocking human diagram method-accuracy review.

---

## v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Shipped: 2026-08-17)

**Phases completed:** 5 phases, 11 plans, 16 tasks

**Key accomplishments:**

- fdars-core pinned to 0.17.0 (parallel only, no linalg); maturin build green; 259-test Python suite passes with zero failures and zero FPCA tolerance relaxations needed.
- New module `src/represent_mod.rs`
- Five new `#[pyfunction]`s in `src/fdata_mod.rs`
- Five Simpson-integrated prediction-scoring metrics (`functional_mae/mse/mape/msle/explained_variance`) bound in a new `fdars.scoring` PyO3 submodule with MAPE/MSLE `ValueError` guards and zero `.unwrap()` calls.
- 1. [Rule 1 - Bug] NaN propagation in represent.py data_range statistics
- Two new represent section pages (spline interpolation + ExtrapolationPolicy, missing-value imputation) each with a hand-authored STYLE_SPEC-conforming SVG concept diagram and an executed offline FDARS_FENCE_OK worked example, wired into the MkDocs Represent nav, with the full docs toolchain proven end-to-end.
- Two new analyze section pages (functional summary statistics and scoring metrics) each with a STYLE_SPEC-conforming hand-authored SVG and an executed offline FDARS_FENCE_OK worked example against the real shipped fdars.fdata and fdars.scoring bindings.
- All six new Phase 29 capability pages wired into mkdocs.yml nav, whole-site strict build green (1088s, offline, exit 0), all six new SVGs SVGO-idempotent, all six executed fences emit FDARS_FENCE_OK — halted at the blocking human diagram-review checkpoint.

---

## v3.0 Provider-Agnostic Advisor, Full-Library Coverage (Shipped: 2026-08-12)

**Phases completed:** 6 phases, 19 plans, 33 tasks

**Key accomplishments:**

- **Phase 19 — Provider foundation & grounding contract:** converted `advisor.py` into an `advisor/` package and refactored `advise()` behind a uniform `Provider` protocol + `AnthropicProvider` + a centralized `ValidateAndRetry` (native / validate-and-retry-to-cap) and `_check_grounding` guard — a pure refactor with the existing advisor suite green throughout.
- **Phase 20 — Additional provider adapters:** added `OpenAIProvider` (+ `base_url` for OpenAI-compatible/local endpoints), `OllamaProvider` (fully local, no key), and `GeminiProvider` (with `_gemini_schema` Pydantic→Gemini translation), each an optional extra (`[openai]`/`[gemini]`/`[ollama]`/`[all-providers]`) with deferred imports and actionable ImportErrors; base package still imports with no provider installed.
- **Phase 21 — Per-aspect advisor coverage:** added deterministic offline `build_diagnostics` for depth, outliers, classification, represent, regression, regression-CV, and SPM so all 12 fdars aspects now carry the three grounded task families through one shared schema/prompt (`_ASPECT_PRIMERS`) — no per-aspect duplication.
- **Phase 22 — Surface integration:** exposed the new coverage through the MCP tools (depth runnable; 6 aspects diagnostics-only via `fdars_build_diagnostics`) while keeping the MCP boundary provably LLM-free, and documented provider selection in the Agent Skill; provider selection stays Python-API-only.
- **Phase 23 — Packaging & CI:** Python 3.9–3.14 CI matrix with version-gated extras (`openai<2.0` on 3.9; `[gemini]`/`[mcp]` 3.10+), a bare-venv smoke proof (core imports with zero provider SDKs), and a 24-cell aspect × provider offline grounding matrix + live-contract confirmation.
- **Phase 24 — Documentation:** new provider setup guide + per-aspect coverage page (builder-derived key tables, executed offline `build_diagnostics` fences emitting `FDARS_FENCE_OK`), updated overview/Python-API docs for provider-agnostic operation, all passing `mkdocs build --strict` offline.

**Verification:** all 28 requirements (PROV/GROUND/ASPECT/SURF/QUAL/DOCS) Complete; milestone audit PASSED (28/28 wired, both core intents met); full suite 259 passed / 4 skipped.

---

## v2.1 Document the AI Advisor (Shipped: 2026-08-11)

**Phases completed:** 5 phases, 5 plans, 7 tasks

**Key accomplishments:**

- Two STYLE_SPEC-conformant inline SVGs (grounding invariant two-lane + advisor loop with Python API exit branch) and a complete AI Advisor overview page method-accurate against `advisor.py`, `mcp/server.py`, and `SKILL.md`.
- AI Advisor nav section wired into mkdocs.yml and proven build-clean: strict build exits 0, all four advisor pages render, FDARS_FENCE_OK confirmed, both SVGs pass SVGO idempotence

---

## v2.0 Grounded AI analysis advisor (Shipped: 2026-08-10)

**Phases completed:** 4 phases, 11 plans, 14 tasks

**Key accomplishments:**

- JWT-style submodule injection + sys.modules registration makes `fdars.advisor` a first-class public API, with `[advisor]` optional extra pinning `anthropic>=0.72.0` + `pydantic>=2.0`.
- Full `TestBuildDiagnosticsOffline` suite (real dataset, determinism, ImportError guard) plus env-gated `TestAdvisorIntegration` class; all offline tests pass network-free, integration test skips cleanly without `ANTHROPIC_API_KEY`.
- Standalone `examples/advisor_recipe.py` script: load Canadian Weather → cluster via kmeans_fd → offline build_diagnostics → optional LLM interpretation guarded by ANTHROPIC_API_KEY; exits 0 without a key (PYAPI-03).
- End-to-end MCP tracer: `[mcp]` extra + `HandleRegistry` (by-reference handles) + `MCPServer("fdars-advisor")` exposing `fdars_build_diagnostics`, proven via an in-process `Client(mcp)` that lists and invokes the tool offline against real Canadian Weather clustering diagnostics.
- Expanded the proven MCP tracer into the full coarse-grained tool set: `_runner.py` with five-method fdars dispatch by reference, `fdars_run_method` returning only `{result_id, method}` (arrays in registry), `run_stdio()` stdio entry point, and three offline tests covering both tools across all five methods.
- Closed the TOOL-03 agentic re-run/compare loop: `_compare.py` delta builder, `fdars_compare_run` tool with flat-param MCP schema, three deterministic tests, and `examples/mcp_recipe.py` running the full register → run → compare loop offline.
- TDD tracer proves the fdars-advisor skill end-to-end — SKILL.md manifest (agentskills.io-compliant frontmatter), offline walkthrough script (Canadian Weather -> smoothing -> 4-key delta), and 6-function pytest module driving both artifacts.
- All three Plan 02 expansion deliverables (env-gated advise() walkthrough step, complete SKILL.md body with Grounded Advice + Grounding Invariant, and three edge tests) were pre-built in Plan 01 and verified green in 6/6 tests at wave-2 start.

**Requirements:** 16/16 v2.0 requirements complete (CORE, ADVISE, PYAPI, TOOL, SKILL — all mapped to Phases 10–13). All four v2.0 phases `phase_complete` + `verification_status: passed`.

**Closeout:** override_closeout — 1 acknowledged deferred item at close: Phase 12 `12-CONTEXT.md` listed 3 "Open questions for research" (MCP SDK/version, tool JSON-schema design, by-reference data passing) that were in fact resolved during Phase 12 execution (mcp 2.0.0 stdio, `HandleRegistry`, network-free tests). Recorded in STATE.md → Deferred Items. Human UAT (2026-08-10) confirmed the real-key LLM advisor path produces grounded advice citing fdars-computed diagnostics.

---
