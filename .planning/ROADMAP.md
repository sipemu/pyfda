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
