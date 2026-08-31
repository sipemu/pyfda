# Milestones

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
