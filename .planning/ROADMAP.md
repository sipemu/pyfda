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
- 🚧 **v8.0 — Advisor: New Capabilities** — Phases 50–54 (in progress)

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

### 🚧 v8.0 Advisor: New Capabilities (In Progress)

**Milestone Goal:** Extend the fdars AI advisor beyond its current single-shot, recommend-only, per-result interpretation surface with four new capabilities — deferred-aspect coverage, comparative method-selection, pipeline diagnostic reports, and a closed-loop auto-tuning capstone — while holding the two hard invariants throughout: the **grounding invariant** (fdars computes every number; the LLM only interprets/cites and proposes parameters via a schema-validated numeric field) and the **MCP-LLM-free compute boundary** (no new MCP tool calls `advise()`; MCP proposals are heuristic). Zero new runtime dependencies — everything extends the shipped `build_diagnostics` / `advise` / Provider-protocol / MCP surface. Foundation-first: deferred aspects first (they unblock accurate diagnostics for every later LLM call), then comparative → pipeline (a strict complexity/dependency gradient proving per-stage isolation), then the auto-tuning capstone, then eval + docs gate last.

**Standing constraints every phase inherits:** grounding invariant (every emitted scalar is fdars-computed native `float`/`int`, no numpy scalars, no fabricated numbers); MCP boundary provably LLM-free (new MCP tools re-run via existing runnable methods / heuristic proposals; no MCP tool calls `advise()`); guard-sync (`_DIAGNOSTICS_METHODS` ↔ `build_diagnostics._supported`) changes stay atomic (a no-op for all four capabilities per research — no new method slot — but primer/`_supported` edits still commit atomically); provider-agnostic, offline-deterministic core with env-gated LLM tests and NO network in CI; docs stay hand-authored inline SVG (STYLE_SPEC), worked-example fences run OFFLINE emitting `FDARS_FENCE_OK` with small/synthetic data; whole-site `mkdocs build --strict` green offline; docs phase runs sequentially on `main` (NOT in worktrees — fences hardcode the main-tree `.venv/bin/mkdocs` path); a BLOCKING human diagram method-accuracy review before milestone close (the v6.0 lesson).

- [x] **Phase 50: Deferred Advisor Aspects (+ compat pre-flight)** - Land the blocking compat fixes, then add grounded PACE-FPCA / elastic-multinomial / ITP scalars + primers (completed 2026-08-23)
- [x] **Phase 51: Comparative Method-Selection** - Deterministic fdars-computed ranking over N candidate methods + "comparison" task family + MCP tool (completed 2026-08-24)
- [x] **Phase 52: Pipeline Diagnostic Report** - Multi-stage diagnostic aggregation with per-stage provenance + "pipeline" task family + MCP tool (completed 2026-08-30)
- [x] **Phase 53: Closed-Loop Auto-Tuning (capstone)** - Bounded propose→apply→re-run→compare loop; Python-API (LLM proposal) + MCP (heuristic, LLM-free) surfaces (completed 2026-08-30)
- [ ] **Phase 54: Eval Strategy + Docs Gate** - Deterministic eval fixtures + new pages + method-accurate SVGs + offline fences + whole-site strict build + blocking human diagram review

## Phase Details

### Phase 50: Deferred Advisor Aspects (+ compat pre-flight)

**Goal**: The three deferred advisor aspects — PACE-FPCA, elastic-multinomial, and ITP interval-inference — emit grounded, fdars-computed scalars with extended primers, so every later LLM call in this milestone targets richer, more accurate diagnostics. Blocking compatibility fixes on the *existing* surface land first as a pre-flight so the advisor keeps importing and the guard-sync test runs on every Python version.
**Depends on**: Nothing (first phase of milestone; foundational — must not be merged into a later phase)
**Requirements**: COMPAT-01, COMPAT-02, COMPAT-03, ASPECT-01, ASPECT-02, ASPECT-03, ASPECT-04, ASPECT-05
**Success Criteria** (what must be TRUE):

  1. The existing advisor imports and runs on Python 3.9 (abi3-py39) with `anthropic` pinned `>=0.72.0,<1.0`, the MCP server's 3 existing tools import and run over stdio via the `mcp` v2 `MCPServer` path unchanged, and the guard-sync test (`_DIAGNOSTICS_METHODS` ↔ `build_diagnostics._supported`) runs on all supported Python versions (no longer skipped on the 3.9 baseline).
  2. `build_diagnostics` emits grounded PACE-FPCA scalars (noise/signal `sigma2` ratio, truncated-rank flag, mean prediction-band width) and elastic-multinomial classification scalars (overfitting gap, class-count flag), each computed from the fdars result as native `float`/`int` (no numpy scalars), offline-deterministic.
  3. The ITP aspect reduces the vector-valued adjusted-p-curve to grounded **detection AND localisation** scalars together (min adjusted p-value; count + proportion of significant intervals; first significant basis; detected-at-0.05) — never a single misleading global scalar.
  4. `_ASPECT_PRIMERS` is extended for the three aspects and `advise()` returns grounded interpretation for each, verified across providers (offline grounding matrix + env-gated live); the grounding invariant and guard-sync are preserved in atomic commits (guard-sync a no-op — no new method slot).

**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 50-01-PLAN.md — Compat pre-flight (isolated first commit): anthropic <1.0 pin, mcp v2 server+3-tool load smoke, version-independent guard-sync test on 3.9 (COMPAT-01..03)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 50-02-PLAN.md — Tracer (ITP detection+localisation) + PACE-FPCA / elastic-multinomial grounded scalars + extended primers, guard-sync no-op (ASPECT-01..04)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 50-03-PLAN.md — Cross-provider grounding: new aspects added to offline aspect×provider matrix + env-gated live coverage (ASPECT-05)

### Phase 51: Comparative Method-Selection

**Goal**: A user can ask the advisor to rank/pick among candidate methods for a task, and the *winner is chosen by an fdars-computed deterministic sort* (never by the LLM) with the LLM narrating the ranking from each candidate's grounded, correctly-attributed diagnostics.
**Depends on**: Phase 50
**Requirements**: COMPARE-01, COMPARE-02, COMPARE-03, COMPARE-04
**Success Criteria** (what must be TRUE):

  1. `compare_methods()` runs `build_diagnostics` over N candidate methods and returns a deterministic, fdars-computed ranking on a shared metric — the same inputs always yield the same winner, and the LLM never chooses it.
  2. A "comparison" advise task family narrates the ranking, citing each candidate's grounded diagnostics with correct per-candidate provenance (labeled candidates, never flat-merged dicts that `_check_grounding` cannot attribute).
  3. Comparison guards against incommensurable comparisons — only comparable candidates on a shared metric are ranked; incommensurable inputs are rejected rather than silently mis-ranked.
  4. An `fdars_compare_methods` MCP tool exposes the comparison and stays provably LLM-free — it re-runs via existing runnable methods and never calls `advise()`.

**Plans**: 3/3 plans executed
**Wave 1**

- [x] 51-01-PLAN.md — Deterministic ranking core (metric registry, dual-input, fail-closed guard, winner-is-sort) [TRACER; COMPARE-01, COMPARE-03]

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 51-02-PLAN.md — "comparison" task family: per-candidate provenance + winner authority narration [COMPARE-01, COMPARE-02]
- [x] 51-03-PLAN.md — `fdars_compare_methods` MCP tool, LLM-free, by-reference ranking [COMPARE-04]

### Phase 52: Pipeline Diagnostic Report

**Goal**: A user can generate one grounded multi-aspect narrative report for an end-to-end analysis (represent → smooth → cluster/regress → monitor), with diagnostics aggregated across stages under strict per-stage provenance and cross-stage caveats surfaced — proving the per-stage isolation the auto-tuning capstone depends on.
**Depends on**: Phase 51
**Requirements**: PIPE-01, PIPE-02, PIPE-03, PIPE-04
**Success Criteria** (what must be TRUE):

  1. `build_pipeline_report()` aggregates diagnostics across the end-to-end stages with per-stage provenance (stage-prefixed keys / per-stage objects, never a flat `{**diag_a, **diag_b}` merge).
  2. `pipeline_report()` produces a grounded multi-aspect narrative report over the aggregated stages, each cited value correctly attributed to its stage.
  3. Cross-stage signal detection surfaces downstream caveats (e.g. a high imputed fraction in the represent stage raises an FPCA caveat downstream).
  4. An `fdars_build_pipeline_report` MCP tool exposes the report and stays LLM-free (never calls `advise()`).

**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 52-01-PLAN.md — TRACER: build_pipeline_report() offline aggregation core (per-stage list-of-blocks + {"_stages":[...]} union payload) (PIPE-01)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 52-02-PLAN.md — deterministic cross-stage caveat rule table + PipelineReport schema + "pipeline" task family narrative under union grounding (PIPE-02, PIPE-03)
- [x] 52-03-PLAN.md — fdars_build_pipeline_report LLM-free MCP tool (by-reference, guard-sync no-op) (PIPE-04)

### Phase 53: Closed-Loop Auto-Tuning (capstone)

**Goal**: The manual recommend → re-run → compare workflow becomes an autonomous, bounded loop — the advisor proposes a parameter change, applies it, re-runs fdars, compares diagnostics, and iterates until a target diagnostic improves or a step budget is hit — exposed both as a Python API (LLM proposal via a schema-validated numeric delta) and as an MCP agentic tool (heuristic, LLM-free proposal), with the compute path staying LLM-free throughout (fdars runs every computation; the loop only orchestrates).
**Depends on**: Phase 52
**Requirements**: TUNE-01, TUNE-02, TUNE-03, TUNE-04, TUNE-05, TUNE-06
**Success Criteria** (what must be TRUE):

  1. A shared `_tuning.py` loop core (propose → apply → re-run fdars → compare → check target-vs-budget → iterate) with an injectable proposal/advisor function is fully offline-testable without an API key, and terminates boundedly — required `max_steps` plus convergence and oscillation detection mean the loop never runs unbounded.
  2. `auto_tune()` (Python API) uses the LLM for proposals via a structured, schema-validated numeric `parameter_delta` — never parsed from prose; the LLM never sets a number directly in the numeric path.
  3. An `fdars_auto_tune` MCP tool uses a heuristic (LLM-free) proposal, preserving the provably-LLM-free MCP boundary; optional guard diagnostics detect off-target (Goodhart) degradation during tuning.
  4. `TuningTrace` / `TuneProposal` / `TuneResult` schemas plus an optional `Recommendation.parameter_delta` field are added, backward-compatible with the 3 existing task families.

**Plans**: 3/3 plans executed
**Wave 1**

- [x] 53-01-PLAN.md — TRACER: bounded loop core + _PARAM_REGISTRY + tuning schemas, offline mock-propose_fn (TUNE-01/02/05/06)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 53-02-PLAN.md — LLM proposal path: auto_tune() + parameter_proposal prompt clause, schema-validated clamped delta (TUNE-03)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 53-03-PLAN.md — fdars_auto_tune MCP tool + LLM-free heuristic propose_fn, by-reference (TUNE-04)

### Phase 54: Eval Strategy + Docs Gate

**Goal**: The milestone closes on a proven quality bar — a deterministic eval strategy that measures "good advice" for auto-tuning + comparative selection (no LLM-as-judge in CI), plus new/updated docs pages for the four capabilities with method-accurate hand-authored SVGs and offline worked examples, gated by a green whole-site strict build and a blocking human diagram review.
**Depends on**: Phase 50, Phase 51, Phase 52, Phase 53
**Requirements**: EVAL-01, EVAL-02, DOCS-01, DOCS-02, DOCS-03
**Success Criteria** (what must be TRUE):

  1. Deterministic eval fixtures — where the correct comparative ranking or auto-tune convergence direction is known from the data — assert diagnostic improvement + grounding-pass; there is no LLM-as-judge in CI and live LLM eval is env-gated (skips without a key; CI stays network-free).
  2. New/updated docs pages cover the four capabilities with method-accurate hand-authored inline SVG diagrams at the v7.0 STYLE_SPEC standard.
  3. Each capability page carries a runnable offline `FDARS_FENCE_OK` worked example on small/synthetic data (the auto-tune example uses the offline/injectable path — no network in the docs build).
  4. Whole-site `mkdocs build --strict` is green offline and a blocking human diagram method-accuracy review passes before the milestone is closed.

**Plans**: 4 plans
- [ ] 54-01-PLAN.md — Deterministic offline eval fixtures (comparative winner + auto-tune improving direction), env-gated live, no LLM-judge
- [ ] 54-02-PLAN.md — 3 method-accurate hand-authored SVGs (comparative / pipeline / auto-tune), STYLE_SPEC + SVGO-idempotent
- [ ] 54-03-PLAN.md — 3 new advisor pages + aspects.md deferred-scalar update + offline FDARS_FENCE_OK fences + nav wiring
- [ ] 54-04-PLAN.md — SVGO gate + whole-site `mkdocs build --strict` offline + BLOCKING human diagram review
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 50 → 51 → 52 → 53 → 54

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 50. Deferred Advisor Aspects (+ compat pre-flight) | v8.0 | 3/3 | Complete    | 2026-08-23 |
| 51. Comparative Method-Selection | v8.0 | 3/3 | Complete    | 2026-08-24 |
| 52. Pipeline Diagnostic Report | v8.0 | 3/3 | Complete    | 2026-08-30 |
| 53. Closed-Loop Auto-Tuning (capstone) | v8.0 | 3/3 | Complete    | 2026-08-30 |
| 54. Eval Strategy + Docs Gate | v8.0 | 0/TBD | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v7.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1,3.0,4.0,5.0,6.0,7.0}-phases/`._
