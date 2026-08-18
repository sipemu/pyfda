# Milestones

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
