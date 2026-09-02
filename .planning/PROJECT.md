# pyfda — Documentation Overhaul

## What This Is

pyfda is the PyO3 binding layer that exposes the Rust `fdars-core` functional-data-analysis library to Python as the `fdars` package (represent, smooth, align, analyze, regress, monitor). It also ships a **scikit-learn-compatible estimator layer** (`fdars.sklearn`, optional `[sklearn]` extra) so functional-data methods plug natively into sklearn's `Pipeline`, `GridSearchCV`, and `cross_val_score`, interoperate with native sklearn estimators, and offer the familiar `fit`/`transform`/`predict` ergonomics — with all 28 wrapped estimators passing the full `check_estimator` battery, no exemptions.

## Core Value

The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

## Current State

**Shipped milestones:**
- ✅ **v1.0 — Documentation Overhaul** (Phases 1–9): shared SVG `STYLE_SPEC.md` + SVGO/determinism CI guardrails, a nav+reference-API audit that derived the gap/example scope, six section diagram sweeps (learn/represent/align/analyze/regression/monitoring — all method-accurate and R-era-free), and an examples sweep (all pages run against the current API, plus five new worked examples).
- ✅ **v2.0 — Grounded AI analysis advisor** (Phases 10–13): a deterministic, offline `build_diagnostics` core + grounded `advise()` (Claude structured outputs, `claude-opus-4-8`) exposed across four surfaces — Python API (recommend-only), Tool/MCP (agentic re-run/compare over stdio), and an Anthropic Agent Skill. The grounding invariant holds throughout: fdars computes every number, the LLM only interprets and cites diagnostic values. Human UAT (2026-08-10) confirmed the real-key path produces grounded advice.
- ✅ **v2.1 — Document the AI Advisor** (Phases 14–18): a new top-level "AI Advisor" docs-site section — a concept/grounding-invariant overview with two hand-authored inline SVG diagrams (grounding invariant, advisor loop), plus per-surface pages for the Python API (recommend-only, with an offline worked example that executes in the docs build), the Tool/MCP server (3 tools, by-reference handle model, stdio, re-run/compare loop), and the Agent Skill (git-URL install + interpret→recommend→re-run→compare walkthrough) — all wired into nav and passing a `mkdocs build --strict` gate. Method-accurate against the shipped v2.0 code; diagrams pass the SVGO/determinism gate.
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** (Phases 19–24): a custom `Provider` protocol with Anthropic/OpenAI(-compatible)/Gemini/Ollama adapters (per-provider optional extras) and a centralized validate-and-retry + `_check_grounding` guard, deterministic offline `build_diagnostics` for all 12 fdars aspects through one shared schema/prompt, MCP + Agent Skill surface updates (MCP stays LLM-free), a Python 3.9–3.14 CI matrix with version-gated extras + bare-venv smoke proof, and a provider-setup + per-aspect docs section. 28/28 requirements complete; suite 259 passed / 4 skipped.
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** (Phases 25–29): upgraded `fdars-core` 0.14.0 → 0.17.0 (parallel-only, no linalg; zero FPCA drift) and exposed the new upstream surface — `fdars.represent` (interpolation/extrapolation-policy/imputation), functional statistics + `depth_based_median`/`trim_mean` in `fdars.fdata` with six new `Fdata` methods, a new `fdars.scoring` submodule (5 metrics), and `fdars.alignment` shift registration (+ `fd.shift_register()`) / registration-quality scores / banded elastic alignment. Extended the advisor with a `scoring` aspect (#13) + imputation/registration diagnostics (grounding invariant + MCP guard-sync preserved), and documented it all with 6 new dedicated pages + 6 method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples (whole-site `mkdocs build --strict` green). 16/16 requirements complete; suite 426 passed / 4 skipped.
- ✅ **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** (Phases 30–35): upgraded `fdars-core` 0.17.0 → 0.20.0 (parallel-only, zero drift; `CvCriterion` wildcard arm) and exposed a new `fdars.inference` submodule (two-sample permutation tests, Degras SCB bands, FLM post-hoc inference, one-way ANOVA — `TestResult`→PyDict, deterministic seed), `functional_depth`/`functional_boxplot` in `fdars.depth`, and AIC model selection + `constant_basis` in `fdars.basis`/`fdars.smoothing`. Added an `inference` advisor aspect (#14) and documented it all with new pages + 4 method-accurate SVGs + offline `FDARS_FENCE_OK` worked examples (whole-site `mkdocs build --strict` green). 21/21 requirements validated; suite 560 passed / 4 skipped.
- ✅ **v6.0 — fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference** (Phases 36–41): upgraded `fdars-core` 0.20.0 → 0.23.0 (parallel-only, no linalg; MSRV verified 1.81 ≤ 1.83) and exposed the new upstream surface across three groups — Group A `concurrent_regression`/`functional_glm` (`fdars.regression`), Group B `pace_fpca` over a new sparse/irregular `IrregFdata` input + `elastic_multinomial` (`fdars.classification`), Group C 9 new depth methods + 4 outlier detectors (`fdars.outliers`) + 3 interval-wise ITP tests (`fdars.inference`). Extended the advisor's `outliers`/`regression`/`classification`/`fpca` aspects with grounded scalars (closing the v5.0 Phase-34 boxplot-outlier deferral; ITP deferred as vector-valued), and documented everything with new pages + 6 method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples. Blocking human diagram review caught and corrected an inverted hypograph/epigraph asymmetry (verified against shipped bindings). 23/23 requirements validated; suite 772 passed / 4 skipped; whole-site `mkdocs build --strict` green offline.
- ✅ **v7.0 — Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth** (Phases 42–49): a docs-only quality pass (no crate bump, no new bindings). A full 61-diagram 4-axis scored inventory (visual/STYLE_SPEC/XML/method-accuracy) gated the milestone; hand-authored SVG corrections were batched by section (learn/represent/align, analyze/monitoring/advisor, regression/inference); 20 new method-accurate workflow SVGs closed the examples-page coverage gap and 5 new advisor-surface SVGs reversed the v2.1 diagram-free choice; thin v4–v6 method pages were extended with new executable worked examples (binomial+poisson GLM, PACE-vs-standard-FPCA, ITP-vs-t_perm_test). Whole-site `mkdocs build --strict` green offline; blocking human diagram review approved. 12/12 requirements validated; 8 phases, 9 plans.

**Grounding invariant (v2.0):** every recommendation cites computed diagnostics and states an expected effect; the LLM never fabricates numbers.

**Design source of truth (v2.0):** `.planning/design/llm-cluster-narration.md`

## Current Milestone: v11.0 fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs

**Goal:** Bump `fdars-core` 0.23.0 → 0.33.0, expose the new upstream surface through PyO3 bindings and the Python API, extend the AI advisor where relevant (grounding invariant preserved), and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Same shape as v4.0/v5.0/v6.0.

**Target features:**
- **Crate bump `fdars-core 0.23.0 → 0.33.0`** as an isolated regression gate on the ~772-test baseline; keep `parallel`, do NOT enable `linalg` (research still notes MSRV/linalg status at 0.33); rebuild via maturin.
- **New bindings** — expose the capabilities added across 0.24–0.33 through PyO3 + the Python API, grouped by capability family (exact surface confirmed during research); layout-correct column-major round-trips, `Result`/dict conversions, `#[non_exhaustive]` fallback arms.
- **Advisor extension (where relevant)** — grounded diagnostics for new aspects; grounding invariant + MCP `_DIAGNOSTICS_METHODS` guard-sync held as hard constraints (single atomic commits, as v4.0 Phase 28 / v5.0 Phase 34 / v6.0 Phase 40).
- **Docs** — new dedicated pages + method-accurate hand-authored inline SVGs + runnable offline `FDARS_FENCE_OK` worked examples; whole-site `mkdocs build --strict` green; blocking human diagram review before close.

**Key context:** Large jump (10 minors) — unlike the prior additive-only waves (v4/v5/v6 each moved 3 minors), 0.24→0.33 may include **breaking changes**; research must map the full changelog, flag any breaking signature changes to existing bindings, and confirm a clean bump path. Crosses binding + advisor + docs code (`Cargo.toml`, `src/*_mod.rs`, `src/lib.rs`, `python/fdars/`, `python/fdars/advisor`, `python/fdars/mcp`, `docs/`). Genuine unknowns → research warranted: exact 0.24–0.33 changelog + new function signatures + result-struct field names, any breaking changes to existing bindings, MSRV/linalg status at 0.33, advisor scope per new capability, worked-example datasets. Package currently `0.9.0`; a code milestone bumps it (semver `vX.Y.Z` tag triggers PyPI publish) — decide the exact bump (likely `0.10.0`) at close. Docs build is ~19–25 min (executed fences run real compute) — keep fence data small. Large scope — the roadmap phases it (bump → binding groups ∥ → advisor → docs), same as v4.0/v5.0/v6.0.

## Last Shipped Milestone: v10.0 Diagram Quality & Accessibility Pass (shipped 2026-09-02)

_All 16 requirements validated; 6 phases (60–65), 8 plans; whole-site `mkdocs build --strict` green offline (~1267s); SVGO idempotence green across all 159 SVGs; blocking human diagram review APPROVED. Docs-only — no crate/binding/advisor/package changes. Full detail: `.planning/milestones/v10.0-ROADMAP.md`. Next milestone: TBD via `/gsd-new-milestone`._

**Goal:** Bring all hand-authored inline SVGs to one consistently high, defect-free, accessible bar — every diagram well-made (no mismatched lines / misaligned geometry), STYLE_SPEC-conformant, accessible, with cards/thumbs synced to their concept diagrams. Diagram-focused successor to v7.0's Documentation Quality Pass.

**Delivered:** a scored 156-SVG audit (`60-AUDIT.md`) gating the milestone; 90 concept diagrams corrected across three parallel worktree-isolated section batches (learn/represent/align ∥ analyze/monitoring/advisor ∥ regression/inference/examples) — universal long-form `<title>`/`<desc>`/`aria-labelledby` + title-matching `aria-label`, 5 Major geometry/method-accuracy fixes (elastic-clustering full redraw; concurrent-regression label overflow; 3 ex-canadian panel clipping; shift-registration "elastic warp" removed → rigid-only); method-accuracy win keeping the canonical Magnitude/Shape/Amplitude outlier taxonomy (audit's "→Phase?" speculation refuted against docs prose); 3 new sklearn concept diagrams (COVER-01); elastic-clustering thumbnail re-synced + 58 gallery thumbs made decorative-accessible (`aria-hidden`); STYLE_SPEC.md refreshed to the current 93-diagram reality; whole-site `--strict` + SVGO/determinism gates green; human diagram review approved.

## Last Shipped Milestone: v9.0 scikit-learn API Compatibility (shipped 2026-09-02)

_All 28 requirements validated (Phase 59 docs closed via a documented override — deliverables shipped, formal VERIFICATION.md skipped); 5 phases, 17 plans; `tests/sklearn/` suite 4294 passed / 0 failed; whole-site `mkdocs build --strict` green offline. Package bumped 0.8.0 → 0.9.0 and released to PyPI (tag `v0.9.0`). Full detail: `.planning/milestones/v9.0-ROADMAP.md`. Next milestone: TBD via `/gsd-new-milestone`._

**Goal:** Add a scikit-learn-compatible estimator layer (`fdars.sklearn`) over the current bindings so functional-data methods plug natively into `Pipeline`/`GridSearchCV`/`cross_val_score`, interoperate with native sklearn estimators, and offer `fit`/`transform`/`predict` ergonomics — every wrapped estimator passing the full `check_estimator` battery, no exemptions.

**Delivered:** `[sklearn]` optional extra + gated `fdars.sklearn` subpackage + shared `_BaseFdarsEstimator` (BaseEstimator contract, `argvals` constructor param, float32→64 cast, tags-API 1.3–1.8 feature-detect shim); ~30-candidate triage → reason-coded `EXCLUDED_METHODS` registry; **28 estimators** across five families (FPCA/smoother/imputer/interpolator/basis/depth transformers; FPC/PLS/GLM/nonparametric regressors; logistic/LDA/QDA/KNN/DD/elastic-multinomial classifiers; FunctionalKMeans/fuzzy-c-means/GMM clusterers; LRT/outliergram/MS-plot/tvdmss/muod/depthgram outlier detectors via stored-reference depth scoring); full-matrix `parametrize_with_checks` gate over all 28 with zero exemptions (COMPLY-01, 1387 checks) + native-sklearn interop (FPCATransformer → RandomForestClassifier, COMPLY-02); sklearn-compliance CI across Python 3.9–3.14; new "scikit-learn API" docs section (concept + per-family reference + coverage/EXCLUDE list + Pipeline & GridSearchCV worked examples + hand-authored data-flow SVG).

## Last Shipped Milestone: v8.0 Advisor — New Capabilities (shipped 2026-08-31)

_All 27 requirements validated; 5 phases, 16 plans, 41 tasks; suite 1045 passed / 10 skipped; whole-site `mkdocs build --strict` green offline; blocking human diagram review approved. Package bumped 0.7.0 → 0.8.0. Full detail: `.planning/milestones/v8.0-ROADMAP.md`. Next milestone: TBD via `/gsd-new-milestone`._

**Goal:** Extend the fdars AI advisor beyond its current single-shot, recommend-only, per-result interpretation surface with four new capabilities — with the grounding invariant (fdars computes every number; the LLM only interprets/cites) and the MCP-LLM-free compute boundary held as hard constraints throughout.

**Target features:**
- **Fill deferred advisor aspects** — dedicated grounded coverage for **PACE-FPCA** and **elastic-multinomial** (both deferred at v6.0 init as `PACE-ADV`/`MULTINOM-ADV`) and **ITP interval-inference** (deferred at v6.0 as vector-valued; needs a grounded-scalar reduction for the vector-valued ITP p-curves). Extends the existing `_ASPECT_PRIMERS` / `build_diagnostics` pattern. Foundational — do early.
- **Comparative method-selection** — a recommender that ranks/picks among candidate methods from comparative diagnostics (e.g. scalar-on-function: FPC-LM vs PLS vs kernel; which clustering method fits best), not just per-result advice on one method. Likely a new task family / entry point over multiple `build_diagnostics` runs.
- **Pipeline diagnostic report** — generate a multi-aspect narrative report for an end-to-end analysis (represent → smooth → cluster/regress → monitor …), aggregating diagnostics across stages instead of single-result interpretation.
- **Closed-loop auto-tuning (capstone)** — turn today's manual recommend → re-run → compare into an autonomous, bounded loop: advisor proposes a parameter/method change, applies it, re-runs, compares, and iterates until a target diagnostic improves or a step budget is hit. Exposed **both as a Python API and as an MCP agentic surface**; the compute path stays LLM-free (fdars runs every computation; the loop only orchestrates).
- **Eval + docs gate:** an eval strategy for "good advice" (auto-tuning + comparative selection); new pages + method-accurate hand-authored inline SVG diagrams (v7.0 standard) + offline `FDARS_FENCE_OK` worked examples; whole-site `mkdocs build --strict` green; blocking human diagram review before close.

**Key context:** First advisor-capability milestone since v3.0 — crosses `python/fdars/advisor/` (`__init__.py`, `_prompts.py`, `_schema.py`, `providers/`), `python/fdars/mcp/`, tests, and `docs/`. Build on the shipped surface, do NOT re-build it: `build_diagnostics` (14 aspects), `advise` (3 task families + `describe_cluster_differences`), 4 providers, MCP (3 tools, provably LLM-free, stdio), Agent Skill. All four capabilities selected for this one milestone (foundation-first roadmap; auto-tuning capstone last). Genuine unknowns → research warranted: agentic-loop design, eval strategy for "good advice", and the exact grounded-scalar reduction for vector-valued ITP interval inference. Package currently `0.7.0`; a code milestone bumps it (semver `vX.Y.Z` tag triggers PyPI publish) — decide the bump at close.

## Last Shipped Milestone: v7.0 Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth (shipped 2026-08-23)

_Docs-only quality milestone (no crate bump, no new bindings). 12/12 requirements validated; 8 phases, 9 plans; whole-site `mkdocs build --strict` green offline; blocking human diagram review approved. Full detail: `.planning/milestones/v7.0-ROADMAP.md`._

**Goal:** Bring the whole docs site to one consistently high bar — audit and fix every hand-authored inline SVG, add concept diagrams to the pages that lacked them, and extend the thin newer pages to full parity with the mature ones. Closest in spirit to v1.0's overhaul.

**Delivered:** a full 61-diagram 4-axis scored inventory (visual/STYLE_SPEC/XML/method-accuracy) gated the milestone; SVG corrections batched by section (learn/represent/align, analyze/monitoring/advisor, regression/inference); 20 new example-page workflow SVGs + 5 new advisor-surface SVGs (reversing the v2.1 diagram-free choice); thin v4–v6 method pages extended with new executable worked examples (binomial+poisson GLM, PACE-vs-standard-FPCA, ITP-vs-t_perm_test).

## Last Shipped Milestone: v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (shipped 2026-08-22)

_All 23 requirements validated; suite 772 passed / 4 skipped; whole-site `mkdocs build --strict` green offline; blocking human diagram review approved (caught + fixed inverted hypograph/epigraph asymmetry). Full detail: `.planning/milestones/v6.0-ROADMAP.md`._

**Goal:** Bump `fdars-core` 0.20.0 → 0.23.0, expose the new upstream surface through PyO3 bindings and the Python API across three capability groups, extend the AI advisor where relevant (grounding invariant preserved), and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Same shape as v4.0/v5.0.

**Target features:**
- Crate bump `fdars-core 0.20.0 → 0.23.0` (0.21/0.22/0.23 all additive/non-breaking, existing signatures unchanged) as an isolated regression gate on the ~560-test baseline; keep `parallel`, do NOT enable `linalg` (verify MSRV in research); rebuild via maturin.
- **Group A — Regression** (extend `fdars.regression`): `concurrent_regression` / `ConcurrentRegrResult`, `functional_glm` (exponential-family GLM over FPC scores).
- **Group B — FPCA & Classification**: `pace_fpca` / `PaceFpcaConfig` / `PaceFpcaResult` (sparse/irregular PACE FPCA — BLUP scores, fitted trajectories, prediction-variance bands); `elastic_multinomial` / `ElasticMultinomialResult` (OvR multinomial classifier, extend `fdars.classification`).
- **Group C — Depth / Outliers / Interval Inference**: new depth methods (hypograph/epigraph, half-region HRD/MHRD, extremal, ERL, L-∞, total-variation + MSSI) extending the v5.0 `functional_depth` dispatcher; outlier detectors (`tvdmss`, `muod`, `sequential_transform_outliers`, depthgram) extending `fdars.outliers`; interval-wise testing (`itp_one_pop` / `itp_two_pop` / `itp_flm`, `ItpResult`) extending `fdars.inference`.
- **Advisor extension (where relevant):** grounded diagnostics for the new aspects (e.g. ITP interval inference, outlier detectors — potentially closing the Phase-34 functional-boxplot-outlier deferral); grounding invariant + MCP `_DIAGNOSTICS_METHODS` guard-sync in single atomic commits, exactly as v4.0 Phase 28 / v5.0 Phase 34. Exact per-capability scope confirmed during research.
- **Docs:** new dedicated pages + method-accurate hand-authored inline SVG diagrams + runnable offline `FDARS_FENCE_OK` worked examples; whole-site `mkdocs build --strict` green.

**Key context:** Crosses binding + advisor + docs code (`Cargo.toml`, `src/*_mod.rs`, `src/lib.rs`, `python/fdars/`, `python/fdars/advisor`, `python/fdars/mcp`, `docs/`). Upstream 0.21→0.23 is additive/non-breaking, so the bump should not disturb existing bindings — risk concentrates in new-binding correctness (column-major layout round-trips, `Result`/dict conversions, `#[non_exhaustive]` fallback arms) and method-accuracy of the new diagrams/examples. Open questions for research: exact 0.23 signatures + `ConcurrentRegrResult`/`PaceFpcaResult`/`ElasticMultinomialResult`/`ItpResult` field names, how `pace_fpca` consumes sparse/irregular input, whether `functional_glm` re-fits or takes a fitted handle, MSRV/`linalg` status at 0.23, advisor scope per capability, and worked-example datasets. Grounding invariant remains the hard constraint on advisor work. Docs build is ~19 min (executed fences run real compute) — keep fence data small. Large scope — the roadmap phases it (bump → three binding groups ∥ → advisor → docs), same as v4.0/v5.0.

## Last Shipped Milestone: v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (shipped 2026-08-18)

_All 21 requirements validated; suite 560 passed / 4 skipped; whole-site `mkdocs build --strict` green offline; human diagram review approved. Full detail: `.planning/milestones/v5.0-ROADMAP.md`._


**Goal:** Upgrade the pinned `fdars-core` from 0.17.0 to 0.20.0, expose the new upstream functional-inference + depth/boxplot + basis/smoothing capabilities through PyO3 bindings and the Python API, extend the v3.0 AI advisor where relevant, and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Same shape as v4.0.

**Target features:**
- Crate bump `fdars-core 0.17.0 → 0.20.0` (0.18 = audit-only, 0.19 = inference suite, 0.20 = quick wins; all additive/non-breaking, no new Rust/Python deps); keep `parallel`, do NOT enable `linalg` (needs Rust 1.84 > MSRV 1.83); rebuild via maturin; the ~426-test suite is the regression gate.
- New bindings — **Group A, Functional inference** (NEW `fdars.inference` submodule, mirroring the v4.0 `fdars.represent`/`fdars.scoring` new-submodule pattern): two-sample permutation tests (`t_perm_test`, `f_perm_test`, `two_sample_mean_test`), simultaneous confidence bands (`mean_scb`, `scb_two_sample_test`), FLM inference on a fitted model (`flm_f_test`, `flm_gof_test`, `oneway_anova_vstat`). All return `TestResult` → PyDict; permutation tests take a deterministic `seed`.
- New bindings — **Group B, Depth & functional boxplot** (extend `fdars.depth`): `functional_depth` unified dispatcher (`DepthMethod` variants via string param + `#[non_exhaustive]` fallback arm), `functional_boxplot` → `FunctionalBoxplotResult` PyDict (median / central region / fence / outlier flags).
- New bindings — **Group C, Basis & smoothing quick wins** (extend `fdars.basis`/`fdars.smoothing`): `constant_basis` intercept column, AIC smoothing-parameter selection (`CvCriterion::Aic`, `aic_smoother`, `smooth_basis_aic`); `CvCriterion` is now `#[non_exhaustive]` → forward-compatible fallback arm required.
- Advisor extension (where relevant): an `inference` diagnostics aspect (summarize `TestResult` p-values/statistics, grounded) and/or functional-boxplot outlier diagnostics; grounding invariant + MCP `_DIAGNOSTICS_METHODS` guard-sync (single atomic commit) exactly as v4.0 Phase 28. Exact scope confirmed during discuss/research.
- Docs: new dedicated pages + method-accurate hand-authored inline SVG diagrams + runnable offline `FDARS_FENCE_OK` worked examples for inference (two-sample tests, SCB bands, functional ANOVA), functional boxplot, and the basis/smoothing additions; whole-site `mkdocs build --strict` green.

**Key context:** Crosses back into binding + advisor + docs code (`Cargo.toml`, `src/*_mod.rs`, `src/lib.rs`, `python/fdars/`, `python/fdars/advisor`, `python/fdars/mcp`, `docs/`). Upstream 0.18→0.20 is additive/non-breaking (existing signatures unchanged), so the bump should not disturb existing bindings — risk concentrates in new-binding correctness (column-major layout round-trips, `Result` conversions, `#[non_exhaustive]` fallback arms) and method-accuracy of the new diagrams/examples. Open questions for research: exact 0.20 signatures + `TestResult`/`FunctionalBoxplotResult` field names, how FLM inference consumes a fitted `FregreLmResult` (handle vs re-fit), advisor scope per capability, and worked-example datasets (two-sample tests need two groups). Grounding invariant remains the hard constraint on advisor work. Docs build is ~18 min (executed fences run real compute) — keep fence data small. Large scope — the roadmap phases it (bump → bindings ∥ → advisor → docs), same as v4.0.

## Last Shipped Milestone: v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (shipped 2026-08-17)

**Goal:** Upgrade the pinned `fdars-core` from 0.14.0 to 0.17.0, expose the new upstream functional-data capabilities through PyO3 bindings and the Python API, extend the v3.0 AI advisor to cover the relevant new capabilities, and document everything to the project's method-accurate standard (hand-authored SVG diagrams + runnable worked examples).

**Target features:**
- Crate bump `fdars-core 0.14.0 → 0.17.0` (all upstream changes 0.15→0.17 are additive/non-breaking); rebuild via maturin; verify the full existing binding + advisor test suite stays green (perf wins — parallel CV folds, faer FPCA SVD, parallel elastic-FPCA — come for free, no new API to bind).
- New bindings — Interpolation & representation: `spline_interpolate`, interpolation/spline with `ExtrapolationPolicy` (Boundary/Exception/Fill/Periodic), `impute_missing_values` + `ImputationMethod` (Linear/Mean/Constant).
- New bindings — Functional statistics & scoring: `functional_variance`/`functional_std`/`functional_covariance`, `depth_based_median`, `trim_mean`; scoring metrics `functional_mae`/`mse`/`mape`/`msle`/`explained_variance`.
- New bindings — Alignment / registration: `least_squares_shift_registration` + `ShiftRegistrationResult`; registration-quality scores (`least_squares_score`, `pairwise_correlation_score`, `sobolev_least_squares_score`); banded elastic alignment (`karcher_mean_with_band`, `*_distance_matrix_with_band`, `band_frac`).
- Advisor extension: wire relevant new capabilities (scoring metrics, imputation, registration quality) into `build_diagnostics` / grounded task families / MCP surface, preserving the grounding invariant.
- Docs: new/updated inline SVG concept diagrams + runnable worked examples across `represent/`, `analyze/`, `align/` (and advisor pages); full `mkdocs build --strict` green.

**Key context:** Crosses back into binding + advisor code (`Cargo.toml`, `src/*_mod.rs`, `python/fdars/`, `python/fdars/advisor`, `python/fdars/mcp`, `pyproject.toml` if extras change) — the v1.0 "docs-only, no code changes" framing no longer applies (v2.0/v3.0 already crossed this line). The grounding invariant remains the hard constraint on any advisor work. Upstream 0.15→0.17 is non-breaking, so the bump should not disturb existing bindings; risk concentrates in new-binding correctness (column-major layout, `Result` conversions) and method-accuracy of the new diagrams/examples. Large scope — the roadmap phases the three binding groups + advisor + docs.

## Requirements

### Validated

<!-- Existing capabilities inferred from the codebase map — the product being documented. -->

- ✓ PyO3 binding layer exposing `fdars-core` compute to Python (`fdars` package) — existing
- ✓ MkDocs (Material) documentation site with sections: learn, represent, smooth, align, analyze, regression, monitoring, reference, examples — existing
- ✓ ~50 hand-authored inline SVG concept diagrams in `docs/assets/diagrams/` (plus cards/ and thumb/) — existing
- ✓ Build-time inline figures via `markdown-exec` + `scripts/docs_fig.py` (`PYTHONPATH=scripts`) — existing
- ✓ 17 narrative example pages in `docs/examples/*.md` backed by datasets in `docs/data/` — existing
- ✓ Released at v0.2.0 with R-parity phase 1 complete — existing
- ✓ Documentation tooling foundation — `STYLE_SPEC.md`, SVGO check-only lint gate in CI (idempotence, all 43 diagrams), build determinism (`svg.hashsalt` + `<dc:date>` suppression — verified byte-identical across builds for deterministic content), `pymdownx.snippets` dataset includes, `pytest-markdown-docs` doc-test harness (one-page CI gate), and the `DOCS_FAST` helper — Phase 1
- ✓ Nav + reference-API audit — `02-AUDIT.md` maps all 42 method-section pages on style/accuracy axes (D-02 rollup), a full R-era grep report (4 leftovers, all in `spm.svg`), and a ranked GAP-0001..0011 / EX-0001..0008 list with a user Selection column gating Phase 3 — Phase 2
- ✓ Tool / MCP surface (TOOL-01, TOOL-02, TOOL-03) — `fdars.mcp` subpackage (optional `[mcp]` extra, Python 3.10+): `HandleRegistry` (by-reference handles, fail-closed), `MCPServer("fdars-advisor")` exposing `fdars_build_diagnostics`, `fdars_run_method` (5-method dispatch), and `fdars_compare_run` (observable before/after delta) over a transport-agnostic handler layer with a stdio entry point; grounding invariant preserved (fdars does the numbers, no LLM in the compute path). Verified 4/4 must-haves, 111 tests pass — Phase 12
- ✓ Agent Skill surface (SKILL-01, SKILL-02) — `.claude/skills/fdars-advisor/` packages the interpret→recommend→re-run→compare loop as an Anthropic Agent Skill: spec-valid `SKILL.md` (git-URL install documented as the authoritative execution environment) + an offline walkthrough script (Canadian Weather → smoothing → deterministic before/after delta) with an env-gated `advise()` grounded-advice step, driven by `tests/test_skill.py` (6 tests). Human UAT (2026-08-10) confirmed the LLM path produces grounded advice citing diagnostics values with a real key — Phase 13

**v2.0 — Grounded AI analysis advisor (Phases 10–13):**
- ✓ Deterministic, offline `build_diagnostics(result, method, …)` core — fdars-computed, no LLM/network dependency (CORE-01/04) — v2.0
- ✓ Grounded `advise()` returning a schema-validated `Advice` via Claude structured outputs, every recommendation carrying `action`/`kind`/`rationale`/`expected_effect`/`evidence` (CORE-02/03) — v2.0
- ✓ Three advisor task families — interpretation, parameter guidance, method guidance — plus `describe_cluster_differences` specialization (CORE-05, ADVISE-01/02/03) — v2.0
- ✓ Python API surface (recommend-only): advisor registered in the public `fdars` API, offline + env-gated integration tests, `examples/advisor_recipe.py` (PYAPI-01/02/03) — v2.0
- ✓ Tool/MCP surface (agentic): coarse-grained tools + stdio MCP server + re-run/compare before/after loop (TOOL-01/02/03) — v2.0
- ✓ Agent Skill surface: `SKILL.md` + walkthrough packaging the interpret→recommend→re-run→compare loop, execution environment documented (SKILL-01/02) — v2.0

**v1.0 — Documentation Overhaul (Phases 1–9):**
- ✓ Shared SVG style spec + SVGO/determinism/doc-test CI guardrails and `DOCS_FAST` path (FND-01..06) — v1.0
- ✓ Nav + reference-API audit deriving the diagram-gap / new-example scope, incl. R-era grep report (AUD-01/02/03) — v1.0
- ✓ Six section diagram sweeps — learn/represent/align/analyze/regression/monitoring, all method-accurate and style-conformant (DIA-01..06) — v1.0
- ✓ Examples sweep — every page runs against the current API, richer narratives, improved figures, five new worked examples (EX-01..04) — v1.0
- ✓ All diagrams remain hand-authored inline SVG (no programmatic generation) — v1.0

**v2.1 — Document the AI Advisor (Phases 14–18):**
- ✓ AI Advisor overview page + grounding-invariant & advisor-loop SVGs (CONCEPT-01/02/03, ADVDIA-01/02) — v2.1
- ✓ Python API page — recommend-only surface + offline worked example that runs in the docs build (PYDOC-01/02/03) — v2.1
- ✓ Tool / MCP server page — 3 tools, by-reference handle model, stdio, re-run/compare loop (MCPDOC-01/02/03) — v2.1
- ✓ Agent Skill page — git-URL install + interpret→recommend→re-run→compare walkthrough (SKILLDOC-01/02) — v2.1
- ✓ "AI Advisor" nav section wired into `mkdocs.yml`; full `mkdocs build --strict` green (NAVDOC-01/02) — v2.1

**v3.0 — Provider-Agnostic Advisor, Full-Library Coverage (Phases 19–24):**
- ✓ Custom `Provider` protocol + Anthropic/OpenAI(-compatible)/Gemini/Ollama adapters, centralized validate-and-retry + `_check_grounding` guard (PROV/GROUND) — v3.0
- ✓ Deterministic offline `build_diagnostics` + three grounded task families for all 12 fdars aspects via one shared schema/prompt (ASPECT) — v3.0
- ✓ MCP + Agent Skill surface integration; MCP boundary stays provably LLM-free; provider selection Python-API-only (SURF) — v3.0
- ✓ Python 3.9–3.14 CI matrix with version-gated extras + bare-venv smoke proof + aspect×provider offline grounding matrix (QUAL) — v3.0
- ✓ Provider-setup + per-aspect coverage docs section, executed offline `build_diagnostics` fences, `mkdocs build --strict` green (DOCS) — v3.0

**v4.0 — fdars-core 0.17 Upgrade (Phases 25–29, in progress):**
- ✓ `fdars-core` bumped 0.14.0 → 0.17.0 (parallel-only, no `linalg`); full binding + advisor suite green (259 passed / 4 skipped / 0 failed), zero FPCA tolerance changes needed — the faer SVD `1e-8·σ₁` drift never surfaced (DEP-01/02) — Phase 25
- ✓ New `fdars.represent` submodule (spline interpolation + extrapolation policy + missing-value imputation) and functional statistics in `fdars.fdata` (variance/std/covariance, depth-based median resolving to the actual curve, trimmed mean), plus six `Fdata` methods (`interpolate/impute/var/std/cov/median`); layout-correct via multi-curve transposition tests; 328 passed / 4 skipped (REPR-01/02/03, STAT-01/02) — Phase 26
- ✓ New `fdars.scoring` submodule (5 prediction-scoring metrics — mae/mse/mape/msle/explained_variance, `ValueError` on MAPE-near-zero / MSLE≤−1) and `fdars.alignment` extensions — least-squares shift registration (dict result + `fd.shift_register()`), 3 registration-quality scores (Sobolev uniform-grid guarded), and banded elastic alignment (`*_with_band`, transposition-tested); 388 passed / 4 skipped (STAT-03, ALGN-01/02/03) — Phase 27
- ✓ Advisor extended to the new capabilities: `scoring` as diagnostics aspect #13 (full grounded treatment; guard-synced atomic commit; `_RUNNABLE_METHODS` still 6), imputation-quality on the `represent` aspect, and registration-quality on the `alignment` aspect — every new diagnostic fdars-computed and citing a real number (grounding invariant preserved), offline-deterministic, no numpy scalars; 426 passed / 4 skipped (ADV-01/02) — Phase 28
- ✓ Docs sweep: 6 new dedicated pages (represent/interpolation + imputation, analyze/functional-statistics + scoring-metrics, align/shift-registration + banded-alignment) + advisor `aspects.md` update, each with a runnable offline worked example emitting `FDARS_FENCE_OK`, plus 6 new method-accurate hand-authored inline SVG diagrams (SVGO-idempotent; human PNG review); whole-site `mkdocs build --strict` green offline (DOCS-01/02/03) — Phase 29

### Active

<!-- v11.0 — fdars-core 0.33 Upgrade. Requirements scoped in REQUIREMENTS.md; refined by the roadmapper. -->

**v11.0 — fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs (in progress):**

- [ ] Crate bump `fdars-core 0.23.0 → 0.33.0` (parallel-only, no linalg); full binding + advisor suite green as the regression gate; any breaking changes to existing bindings absorbed
- [ ] New PyO3 bindings + Python API for the capabilities added across 0.24–0.33 (grouped by capability family; exact surface derived from research)
- [ ] Advisor extension (where relevant) — grounded diagnostics for new aspects; grounding invariant + MCP guard-sync preserved
- [ ] Docs — new pages + method-accurate hand-authored SVGs + runnable offline `FDARS_FENCE_OK` worked examples; whole-site `mkdocs build --strict` green; blocking human diagram review

**v10.0 — Diagram Quality & Accessibility Pass (Phases 60–65, shipped 2026-09-02):**

- [x] Diagram quality audit — scored inventory of all 156 SVGs on 4 axes (design/geometry, STYLE_SPEC, accessibility, sync) → ranked worklists + COVER/SYNC lists — Phase 60 (AUDIT-01/02)
- [x] Concept-diagram corrections — 90 diagrams across 3 parallel section batches: universal long-form a11y + 5 Major geometry/method-accuracy fixes + STYLE_SPEC conformance — Phases 61/62/63 (DEFECT-01/02/03, A11Y-01/02, SPEC-01)
- [x] Cards/thumbs sync + new coverage — elastic-clustering thumb re-sync, 58 thumbs `aria-hidden`, 3 new sklearn concept diagrams — Phase 64 (SYNC-01/02, A11Y-03, COVER-01)
- [x] STYLE_SPEC refresh + gates + human review — spec refreshed to 93-diagram reality; SVGO/determinism + whole-site `--strict` green; blocking human diagram review approved — Phase 65 (SPEC-02, GATE-01/02/03)

**v9.0 — scikit-learn API Compatibility (Phases 55–59, shipped 2026-09-02):**

- [x] Foundation & packaging — `[sklearn]` optional extra + gated `fdars.sklearn` subpackage + shared `_BaseFdarsEstimator` (BaseEstimator contract, `argvals` constructor param, float32→64 cast, tags-API 1.3–1.8 feature-detect shim) — Phase 55 (FND-01..04)
- [x] Compliance triage & coverage — ~30 candidates run through `check_estimator` → PASS/EXCLUDE verdicts + reason-coded `EXCLUDED_METHODS` registry + go/no-go gate — Phase 55 (TRIAGE-01..03)
- [x] Transformers — FPCA, B-spline/local-poly smoothers, imputer/interpolator, basis, depth as `TransformerMixin`; `Pipeline([smoother, fpca])` — Phase 56 (XFORM-01..06)
- [x] Regressors & classifiers — FPC/PLS/GLM/nonparametric `RegressorMixin`; logistic/LDA/QDA/KNN/DD/elastic-multinomial `ClassifierMixin`; `Pipeline` + `GridSearchCV` — Phase 57 (REG-01/02, CLF-01/02, PRED-01)
- [x] Clusterers, outliers & compliance gate — FunctionalKMeans/fuzzy-c-means/GMM `ClusterMixin`; 6 outlier detectors via stored-reference depth scoring `OutlierMixin`; full-matrix `parametrize_with_checks` over all 28 with zero exemptions (COMPLY-01) + native-sklearn interop (COMPLY-02); CI 3.9–3.14 — Phase 58 (CLUS-01/02, OUT-01/02, COMPLY-01/02)
- [x] Documentation & release — new "scikit-learn API" docs section (concept + per-family + coverage/EXCLUDE list + Pipeline & GridSearchCV worked examples + hand-authored data-flow SVG); pkg 0.8.0 → 0.9.0 released to PyPI (tag `v0.9.0`) — Phase 59 (DOCS-01..03, REL-01) — docs phase closed via documented override (VERIFICATION.md skipped; deliverables shipped, `--strict` green)

**v8.0 — Advisor: New Capabilities (Phases 50–54, shipped 2026-08-31):**

- [x] Deferred advisor aspects — grounded PACE-FPCA / elastic-multinomial / ITP (detection+localisation) scalars + extended primers — Phase 50 (ASPECT-01..05, COMPAT-01..03)
- [x] Comparative method-selection — `compare_methods()` deterministic fdars winner + "comparison" task family + LLM-free `fdars_compare_methods` MCP tool — Phase 51 (COMPARE-01..04)
- [x] Pipeline diagnostic report — per-stage provenance + deterministic Python cross-stage caveats + LLM-free `fdars_build_pipeline_report` MCP tool — Phase 52 (PIPE-01..04)
- [x] Closed-loop auto-tuning (capstone) — bounded loop; Python `auto_tune()` (schema-validated numeric delta) + LLM-free heuristic `fdars_auto_tune` MCP tool; Goodhart guard — Phase 53 (TUNE-01..06)
- [x] Eval strategy + docs — deterministic offline eval (no LLM-judge) + 3 pages/SVGs + offline fences + `--strict` green + human diagram review — Phase 54 (EVAL-01/02, DOCS-01..03)

**v7.0 — Documentation Quality Pass (Phases 42–49, shipped 2026-08-23):**

- [x] SVG audit & fix — full 61-diagram 4-axis scored inventory (visual/STYLE_SPEC/XML/method-accuracy); corrections batched by section; SVGO idempotence + determinism gate green — Phases 42–45
- [x] Diagram coverage — 20 new example-page workflow SVGs + 5 new advisor-surface SVGs (reversing the v2.1 diagram-free choice) — Phases 46–47
- [x] Page depth — thin v4–v6 method pages extended to mature-page parity + new executable worked examples (binomial+poisson GLM, PACE-vs-standard-FPCA, ITP-vs-t_perm_test) — Phase 48
- [x] Whole-site gate — `mkdocs build --strict` green offline; worked examples `FDARS_FENCE_OK`; blocking human diagram review approved — Phase 49

**v6.0 — fdars-core 0.23 Upgrade (Phases 36–41, shipped 2026-08-22):**

- [x] Crate bump `fdars-core 0.20.0 → 0.23.0` (parallel-only, no linalg); full binding + advisor suite green as the regression gate — ✓ Phase 36 (600 passed / 4 skipped / 0 failed; zero drift; zero wildcard arms needed — existing CvCriterion/ProjectionBasisType arms already present)
- [x] Group A — Regression: `concurrent_regression` + `functional_glm` extending `fdars.regression` — ✓ Phase 37 (2 bindings + 2 PyDict converters; `beta_curve (p,m)` transposition-guarded at p=3,n=10; 4 GLM families via `#[non_exhaustive]` `GlmFamily` string dispatch; embedded `fpca` excluded; `functional_glm` takes no argvals per core; 620 passed / 4 skipped)
- [x] Group B — FPCA & Classification: `pace_fpca` (sparse/PACE FPCA) + `elastic_multinomial` extending `fdars.classification` — ✓ Phase 38 (pyfda's first `#[pyclass]` `PyIrregFdata` + `fdars.pace_fpca` submodule with dtype-agnostic ragged-list guards + 10-key dict / transposition-guarded eigenfunctions·scores; `elastic_multinomial` with CR-01 label guard, `class_models` omitted; 643 passed / 4 skipped)
- [x] Group C — Depth / Outliers / Interval Inference: new depth methods + outlier detectors (`tvdmss`/`muod`/`sequential_transform`/depthgram) + interval-wise testing (`itp_*`) extending `fdars.depth`/`fdars.outliers`/`fdars.inference` — ✓ Phase 39 (3 plans: 9 new `functional_depth` variants →13 total; 4 deterministic outlier detectors with `list[int]`/`list[dict]` results; 3 ITP tests via new `itp_result_to_pydict` with `ProjectionBasisType` dispatch + seed determinism; 681 passed / 4 skipped)
- [x] Advisor extension (where relevant) — grounded diagnostics for new aspects; grounding invariant + MCP guard-sync (single atomic commit) preserved — ✓ Phase 40 (extended 4 existing aspects: `outliers` for tvdmss/muod/sequential_transform/depthgram closing the Phase-34 deferral, `regression` for functional_glm/concurrent_regression, plus Group B `classification` elastic_multinomial + `fpca` pace_fpca; ITP deferred; all diagnostics native float/int, MCP guard-sync a no-op; 772 passed / 4 skipped)
- [x] Docs — new pages + method-accurate hand-authored SVGs + runnable offline `FDARS_FENCE_OK` worked examples; `mkdocs build --strict` green — ✓ Phase 41 (DOCS-08..11: new Regression / PACE-FPCA + elastic-multinomial / depth-outliers-inference pages + 6 hand-authored SVGs; advisor aspects.md; whole-site strict build green; blocking human diagram review caught + fixed inverted hypograph/epigraph asymmetry; 772 passed / 4 skipped)

**v5.0 — fdars-core 0.20 Upgrade (Phases 30–35, shipped):**
- ✓ Crate bump 0.17.0 → 0.20.0 (parallel-only, no linalg); 426-test regression gate green, zero drift; `CvCriterion` wildcard arm — Phase 30
- ✓ Group A — `fdars.inference` submodule: two-sample permutation tests + SCB bands + FLM inference (`TestResult` → PyDict, deterministic seed; FLM re-fits internally; CR-01 negative-label guard) — Phase 31
- ✓ Group B — `functional_depth` unified dispatcher + `functional_boxplot` (7-key dict, outliers as int list, transposition-guarded) extending `fdars.depth` — Phase 32
- ✓ Group C — `constant_basis` + AIC smoothing selection (`smooth_basis_aic`, `optim_bandwidth(criterion="aic")`) extending `fdars.basis`/`fdars.smoothing` — Phase 33
- ✓ Advisor extension — `inference` diagnostics aspect (#14) summarizing TestResult stats + significance flags; grounding invariant + MCP guard-sync preserved (boxplot-outlier diagnostics deferred) — Phase 34
- ✓ Docs — new Inference section + functional-inference page, analyze/functional-boxplot page, basis/smoothing fold-ins, advisor aspects.md #14; 4 new SVGs; whole-site `--strict` build green; human diagram review approved — Phase 35

### Out of Scope

- Programmatic/tool-generated diagrams — user chose to keep diagrams hand-authored inline SVG
- Dark-mode / theming rework of SVGs — not part of this milestone's intent
- R-parity feature work — tracked separately (see `PARITY_PLAN.md`)
- Binding upstream internals with no public API — the 0.15→0.17 performance wins (parallel CV folds, faer FPCA SVD, parallel elastic-FPCA) are inherited via the crate bump, not separately exposed
- HTTP/SSE MCP transport (HTTP-01 / FUT-01) — still deferred; stdio only

## Context

- **Site build:** MkDocs Material (`mkdocs.yml`); diagrams referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`. Inline figures use `markdown-exec` importing `docs_fig` from `scripts/` (canonical mechanism is `PYTHONPATH=scripts`; `docs/hooks.py` is a fallback). A `site/` build output and a docs CI workflow already exist.
- **Diagram style today:** `viewBox="0 0 720 300"`, inline `<style>` classes (`.ttl/.sub/.lab/.sm/.mono`), system-ui fonts, muted Bootstrap-ish palette, `role="img"` + `aria-label`. This is the de-facto baseline the shared style spec will formalize.
- **Datasets:** `docs/data/` (canadian weather, growth, phoneme, tecator, sonar, wine) drive the narrative examples; standalone scripts also live in top-level `examples/`.
- **Codebase map:** see `.planning/codebase/` (ARCHITECTURE, STRUCTURE, STACK, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS).

## Constraints

- **Authoring**: Diagrams stay hand-authored inline SVG — max conceptual control, edited by hand against a shared style spec.
- **Accuracy**: Diagrams and example outputs must be method-accurate; correctness is validated by section review on the built site, not assumed.
- **Compatibility**: Examples must run against the *current* `fdars` API and existing datasets in `docs/data/`.
- **Process**: Work proceeds section-by-section (learn/, align/, analyze/, regression/, monitoring/, represent/, examples/) with a review gate per section before moving on.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep diagrams as hand-authored inline SVG | Max control over the conceptual look; matches existing baseline | ✓ Good — held through all six v1.0 sweeps |
| Formalize a shared SVG style spec before rollout | Consistency across ~50 diagrams needs one standard | ✓ Good — `STYLE_SPEC.md` + SVGO idempotence gate (all 43 diagrams) |
| Full sweep of all diagrams + all example pages | User wants the whole doc set brought to one bar | ✓ Good — v1.0 shipped all six diagram sections + examples sweep |
| Review per doc section via the built site | User validates accuracy/style in batches before rollout continues | ✓ Good — per-section review gates held |
| Derive coverage/new-example list from nav + reference-API audit | Systematic gap detection over guesswork | ✓ Good — `02-AUDIT.md` (Phase 2): ranked GAP/EX list + Selection gate |
| Diagrams prioritized over examples | User's stated priority order | ✓ Good — diagrams (Phases 3–8) before examples (Phase 9) |
| One deterministic core shared by all advisor surfaces | fdars computes numbers; the LLM only interprets — grounding invariant | ✓ Good — `build_diagnostics` shared by Python/MCP/Skill (v2.0) |
| Grounding invariant enforced by Pydantic schema + system prompt | Evidence must cite diagnostic values; no fabricated numbers | ✓ Good — `Advice` schema + human UAT confirmed (v2.0) |
| `anthropic`/`mcp` as optional extras; core works offline | Keep CI network-free; LLM tests env-gated | ✓ Good — offline tests pass, integration skips without key (v2.0) |
| MCP transport = stdio only; HTTP/SSE deferred | Matches local/CI usage; keep tool layer transport-agnostic | ✓ Good — stdio shipped; HTTP deferred to a future milestone (v2.0) |
| Advisor docs live in a new top-level "AI Advisor" nav section | The v2.0 feature shipped without user-facing docs; a dedicated section makes it discoverable | ✓ Good — section + 4 pages wired, `--strict` build green (v2.1) |
| Only the Python API page carries an executed offline fence; MCP/Skill fences illustrative | The docs build must not depend on the `[mcp]`/`[advisor]` extras, Python 3.10+, or an API key | ✓ Good — build stays offline; fence execution proven via `FDARS_FENCE_OK` sentinel (v2.1) |
| Per-page human review gate on the built site, self-served during the autonomous run | User authorized a fully-autonomous run; orchestrator self-reviewed each page against source + rendered diagrams | ✓ Good — caught a diagram label-overlap and 7 stale cross-refs, fixed inline (v2.1) |
| Bump `fdars-core` to 0.17.0 as an isolated regression gate before any new bindings | Isolate the sole numeric change (faer FPCA SVD drift) on a green baseline so binding-correctness issues can't hide behind an upgrade regression | ✓ Good — suite green with zero test changes; drift never exceeded existing tolerances (v4.0 Phase 25) |
| Blocking human diagram method-accuracy review before milestone close | Method-accuracy is the docs' core value; a diagram that misdepicts the method is worse than none | ✓ Good — v6.0 review caught an inverted hypograph/epigraph asymmetry the executors + verifier missed; corrected against shipped-binding ground truth (v6.0 Phase 41) |
| Disable worktree isolation for docs phases; run executors sequentially on main | Doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path — a worktree executor would build the wrong tree and fail verification | ✓ Good — sequential execution kept the ~22-min whole-site fences building against the real tree (v6.0 Phase 41) |
| sklearn tags/validate compat shim spans 1.3→1.8 (not just 1.3–1.6); `[sklearn]` extra pinned with a `python_version` marker | Dev/CI runs sklearn 1.8 on Python ≥3.10 (where `_more_tags` is removed); the `<1.7` cap only applies to the Python-3.9 wheel. Feature-detect, never version-compare | ✓ Good — FPCATransformer passed 47/47 check_estimator on sklearn 1.8 (v9.0 Phase 55) |
| Triage EXCLUDE reserved for genuinely-structural mismatch; skeleton predict-quality failures are PASS-WITH-FIXES deferred to the family phase | Under no-exemptions "full coverage", a naive skeleton failing `check_regressors_train` is an implementation-quality signal (fix = stored-model predict in Phase 57), not a reason to drop the family | ✓ Good — reclassified 12 EXCLUDE→PASS-WITH-FIXES; go/no-go GO on all 6 families (v9.0 Phase 55, user-approved) |
| Full 28-estimator `parametrize_with_checks` gate as the milestone lock; zero exemptions, non-compliant methods EXCLUDED not exempted | The milestone bar is provable sklearn compliance; an exemption would hollow out the guarantee | ✓ Good — all 28 PASS (1387 gate checks), 0 PASS-WITH-FIXES; excluded methods stay in the functional API (v9.0 Phase 58) |
| Outlier detectors score via stored-reference `modified_band_1d(X, X_fit_)` depth | `check_methods_subset_invariance` requires `score_samples(X[mask]) == score_samples(X)[mask]`; re-fitting per call violates it | ✓ Good — all 6 detectors subset-invariant; 283/283 outlier checks pass (v9.0 Phase 58) |
| Close v9.0 with a documented Phase-59 verification override rather than back-filling a VERIFICATION.md | Docs deliverables demonstrably shipped (live site, `--strict` green, PyPI release); a retroactive verification doc adds ceremony without new signal | — Pending — override recorded in MILESTONES.md/STATE.md; revisit if docs drift (v9.0 close) |
| Run the three SVG-correction phases (61/62/63) in parallel via isolated git worktrees, not sequentially on main | The three section batches edit disjoint concept-SVG sets and run no doc build during correction (that's Phase 65 only), so the v6.0 "sequential-on-main" reason does not apply; parallelism cut wall-clock ~3× | ✓ Good — disjoint sets merged to main with zero conflicts; all 90 corrected concurrently (v10.0, user-approved) |
| Consolidate the blocking human diagram review into the final gate phase (65) rather than per-correction-phase | Per-phase verifiers flag visual items for diagram work by nature; one whole-set review over the corrected site is stronger and avoids fragmenting the human gate | ✓ Good — 61/63 visual items carried forward to GATE-03; single review approved the full set (v10.0) |
| Complete Phase 64–65 inline (orchestrator) when the account hit a session-quota limit mid-run, instead of spawning executor/verifier subagents | Remaining work was small, concrete, and fully checkable (doc edit + SVGO/build gates); the one irreducible human gate (GATE-03) was preserved | ✓ Good — gates run directly, milestone closed cleanly without waiting on quota reset (v10.0) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-02 — started milestone v11.0 (fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs). Bump 0.23.0 → 0.33.0 (parallel-only, no linalg), expose the new upstream surface via PyO3 bindings + Python API, extend the advisor where relevant (grounding invariant preserved), document to the method-accurate standard. Same shape as v4.0/v5.0/v6.0; 10-minor jump may carry breaking changes (research to confirm). Phases continue from Phase 66. Next: research → requirements → roadmap.*
