# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- 🚧 **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (in progress)

## Phases

<details>
<summary>✅ v1.0 Documentation Overhaul (Phases 1–9) — SHIPPED 2026-08-08</summary>

Reworked the MkDocs site's hand-authored SVG diagrams and worked example pages to a consistently high, method-accurate standard, on top of new style/determinism/doc-test guardrails.

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

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout (fdars computes the numbers; the LLM only interprets and cites them).

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

<details open>
<summary>🚧 v3.0 Provider-Agnostic Advisor, Full-Library Coverage (Phases 19–24) — IN PROGRESS</summary>

Make the fdars AI advisor work with any LLM backend (Anthropic, OpenAI/OpenAI-compatible, Google Gemini, local Ollama) through a custom `Provider` protocol, and give every fdars analysis aspect its own advisor (diagnostics + grounded task families) like clustering has today — with the grounding invariant preserved on every backend. Dependency-ordered: the provider/grounding foundation ships first and blocks everything; adapters and per-aspect diagnostics are then independent (parallel-eligible); surfaces, packaging/CI, and docs assemble on top; docs last.

### Summary

- [x] **Phase 19: Provider Foundation & Grounding Contract** - `Provider` protocol + Anthropic-adapter refactor + validate-and-retry + centralized `_check_grounding`; provider selection via params/env. Blocks all downstream work. (completed 2026-08-12)
- [ ] **Phase 20: Additional Provider Adapters** - OpenAI (+ `base_url`), Ollama (local, no key), Gemini adapters behind the protocol, each an optional extra. Parallel-eligible with Phase 21.
- [ ] **Phase 21: Per-Aspect Advisor Coverage** - `build_diagnostics` + grounded task families for represent/basis, depth/outliers, classification, regression/CV, monitoring/SPM. Parallel-eligible with Phase 20.
- [ ] **Phase 22: Surface Integration** - MCP exposes new aspect diagnostics (LLM-free); provider selection wired through the Python `advise()`; Agent Skill documents providers + full coverage.
- [ ] **Phase 23: Packaging & CI** - Per-provider extras finalized; Python 3.9–3.14 matrix with version/extra gating; bare-venv smoke; two-layer offline + env-gated live tests.
- [ ] **Phase 24: Documentation** - Provider setup guide + per-aspect advisor pages + updated overview/API pages; docs build stays offline (`mkdocs build --strict`).

### Phase Details

### Phase 19: Provider Foundation & Grounding Contract

**Goal**: The advisor runs behind a uniform `Provider` protocol with the grounding/retry machinery centralized, so every later adapter and aspect inherits a checked grounding contract instead of re-implementing it. This is a pure refactor: existing Anthropic behavior and outputs are unchanged.
**Depends on**: Nothing (first phase of v3.0; builds on shipped v2.0 advisor)
**Requirements**: PROV-01, PROV-02, PROV-06, GROUND-01, GROUND-02, GROUND-03, GROUND-04
**Success Criteria** (what must be TRUE):

  1. `advise()` runs through a `Provider` protocol with an `AnthropicProvider` adapter, and every existing advisor test (offline + env-gated integration) passes unchanged — same public behavior and outputs.
  2. A provider with native structured output returns a schema-validated `Advice` via the native path; a provider without it goes through a validate-and-retry path (Pydantic validation, ≤2 retries with full diagnostics re-included) that fails deterministically after the cap with no fabrication.
  3. A centralized `_check_grounding` check runs on every provider path and rejects any `Advice` whose recommendations cite numbers not present in the diagnostics.
  4. A provider refusal or empty response raises a clear error rather than yielding a vacuously-valid `Advice`.
  5. The user selects provider and model via explicit `advise(provider=…, model=…)` params and/or env vars (`FDARS_ADVISOR_PROVIDER` / `_MODEL` / `_BASE_URL` + per-provider keys) with documented precedence; `provider=None` reproduces today's Anthropic default.

**Plans**: 3 plans

- [x] 19-01-PLAN.md — TRACER: advisor.py→advisor/ package + Provider protocol + AnthropicProvider + ValidateAndRetry + resolve_provider + centralized _check_grounding; wire advise() end-to-end (green gate)
- [x] 19-02-PLAN.md — Mechanical split: _schema.py, _prompts.py, aspects/*.py; build_diagnostics dispatches lazily (green gate)
- [x] 19-03-PLAN.md — Offline provider/grounding test suite with in-memory fake providers (protocol, retry-cap, refusal, grounding-reject, precedence)

### Phase 20: Additional Provider Adapters

**Goal**: Any of OpenAI (including OpenAI-compatible local endpoints), Ollama (fully local), and Gemini can back the advisor through the Phase 19 protocol, each installable as its own optional extra, with the grounding invariant holding on every backend.
**Depends on**: Phase 19
**Requirements**: PROV-03, PROV-04, PROV-05, PROV-07
**Success Criteria** (what must be TRUE):

  1. `advise(provider="openai", …)` works against OpenAI and any OpenAI-compatible endpoint via a configurable `base_url` (vLLM / LM Studio / LocalAI).
  2. `advise(provider="ollama", …)` produces grounded advice fully locally with no API key.
  3. `advise(provider="gemini", …)` works against Google Gemini, with the Pydantic→Gemini schema translation applied so structured output validates.
  4. Each provider installs as an optional extra (`[openai]`, `[gemini]`, `[ollama]`); the base package imports and the offline core runs with no provider installed, and a missing extra raises an actionable ImportError.

**Plans**: 3 plans

  - [x] 20-01-PLAN.md — Tracer: OpenAI adapter end-to-end + phase-wide plumbing (extras, deferred guards, resolve_provider extension) [PROV-03, PROV-07]
  - [x] 20-02-PLAN.md — Ollama adapter (local, no key; validate-and-retry / `supports_native=False` path) [PROV-04]
  - [x] 20-03-PLAN.md — Gemini adapter (`_gemini_schema` translation) + env-gated live integration tests [PROV-05]

### Phase 21: Per-Aspect Advisor Coverage

**Goal**: Every fdars analysis aspect — not just clustering — has deterministic offline diagnostics and grounded advice task families, driven by the same schema, prompt, and grounding machinery with no per-aspect duplication.
**Depends on**: Phase 19
**Requirements**: ASPECT-01, ASPECT-02, ASPECT-03, ASPECT-04, ASPECT-05, ASPECT-06, ASPECT-07
**Success Criteria** (what must be TRUE):

  1. `build_diagnostics` produces deterministic, offline diagnostics for represent/basis, depth & outliers, classification, regression & regression-CV (`fregre_lm`/`fregre_pls`/`fregre_cv`), and monitoring/SPM (Phase-1 T²/SPE, `spe_moment_match_diagnostic`, excluding stochastic ARL).
  2. Every aspect (clustering, smoothing, alignment, basis/represent, depth/outliers, classification, regression/FPCA, monitoring/SPM) offers the three grounded task families (interpretation, parameter guidance, method guidance) through the shared schema + grounding machinery — no per-aspect prompt or schema duplication.
  3. The aspect is always caller-specified and never auto-detected from result keys, so key collisions (e.g. `r_squared`, `edf`) cannot misroute a request.
  4. Each new aspect's diagnostics pass an offline determinism test (same input → byte-identical JSON-serialisable output, no numpy scalars).

**Plans**: TBD

### Phase 22: Surface Integration

**Goal**: The MCP tool surface and the Agent Skill expose the new per-aspect coverage, and provider selection is reachable from the Python API — while the MCP boundary stays LLM-free and provider selection lives only in `advise()`.
**Depends on**: Phase 20, Phase 21
**Requirements**: SURF-01, SURF-02, SURF-03
**Success Criteria** (what must be TRUE):

  1. The MCP tools expose the new aspect diagnostics/methods and remain compute-only (no `advise()` call in a tool handler; grounding invariant preserved).
  2. Provider selection is available through the Python API `advise()`, and the MCP tools do not call `advise()`.
  3. The Agent Skill's `SKILL.md` documents provider selection (including the local/offline path) and the full per-aspect advisor coverage.

**Plans**: TBD

### Phase 23: Packaging & CI

**Goal**: The full aspect × provider contract is proven network-free and deterministically, the extras/version matrix is correct across Python 3.9–3.14, and the core provably imports with no provider extra installed.
**Depends on**: Phase 20, Phase 21, Phase 22
**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04
**Success Criteria** (what must be TRUE):

  1. Two-layer offline tests (per-aspect diagnostics fixtures × per-provider adapter fixtures with recorded responses/mocks) cover the aspect × provider contract with no network, and all offline tests (core + aspect + adapter) run deterministically.
  2. Env-gated live integration tests, one per provider, skip cleanly when keys / a local server are absent.
  3. The CI matrix covers Python 3.9–3.14 with correct extra/version gating (`openai<2.0` on 3.9; `[gemini]`/`[mcp]` 3.10+).
  4. A bare-venv smoke test proves the core imports and the offline `build_diagnostics` runs with no provider extra installed.

**Plans**: TBD

### Phase 24: Documentation

**Goal**: The published AI Advisor docs section reflects provider-agnostic operation and full-library coverage, with executed offline fences running against the real shipped implementation and the docs build staying offline.
**Depends on**: Phase 23
**Requirements**: DOCS-01, DOCS-02, DOCS-03
**Success Criteria** (what must be TRUE):

  1. A provider setup guide covers all four backends — keys, `base_url`, local Ollama, and selection/precedence.
  2. Per-aspect advisor pages document the diagnostics and task families for each fdars aspect.
  3. The AI Advisor overview and Python API pages are updated for provider-agnostic operation and full-library coverage, and `mkdocs build --strict` passes offline with any executed fences running against the current implementation.

**Plans**: TBD
**UI hint**: yes

### Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 19. Provider Foundation & Grounding Contract | 3/3 | Complete    | 2026-08-12 |
| 20. Additional Provider Adapters | 0/? | Not started | - |
| 21. Per-Aspect Advisor Coverage | 0/? | Not started | - |
| 22. Surface Integration | 0/? | Not started | - |
| 23. Packaging & CI | 0/? | Not started | - |
| 24. Documentation | 0/? | Not started | - |

</details>

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md`, `v2.0-ROADMAP.md`, `v2.1-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1}-phases/`._
