# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (shipped 2026-08-17)
- ✅ **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** — Phases 30–35 (shipped 2026-08-18)

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

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v5.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1,3.0,4.0,5.0}-phases/`._
