# Research Summary: fdars v3.0 — Provider-Agnostic AI Advisor + Full-Library Coverage

**Project:** fdars v3.0 (functional data analysis library with AI advisor system)  
**Domain:** Multi-provider LLM advisor layer with per-aspect (depth, regression, monitoring, classification) diagnostic builders  
**Researched:** 2026-08-12  
**Confidence:** HIGH (direct codebase analysis + verified against official provider SDK docs)

---

## Executive Summary

fdars v3.0 transforms the single-provider (Anthropic-only) AI advisor into a provider-agnostic system with full-library coverage across seven analysis aspects (represent, clustering, smoothing, FPCA, alignment, basis, depth, outliers, regression, monitoring, classification). The research surfaces a **critical prerequisite**: the existing advisor is tightly coupled to Anthropic's SDK. Any provider work requires refactoring it into an extensible `Provider` protocol first — this is not optional scaffolding but the single blocking dependency for every downstream feature.

The recommended approach is a **dependency-ordered three-phase sequence**: (A) Provider protocol + Anthropic refactor (foundation, no new features), (B) per-provider adapters (OpenAI, Gemini, Ollama — parallel to Phase A), (C) per-aspect diagnostic builders (depth, regression, monitoring, classification — parallelizable with B). The grounding invariant — "fdars computes every number; the LLM only interprets" — is the hard constraint that must be enforced identically across all providers. This requires **centralized validation** (`_check_grounding` function) and a **unified retry contract** (max 2 retries with diagnostics re-included on repair) built into the base `Provider` layer **before any adapter is written**.

Key risk: Schema feature incompatibility across providers (OpenAI requires nullable unions; Gemini rejects `additionalProperties`; Ollama's constrained decoding silently fails if `think=True` is set simultaneously). This is avoidable only by writing schema-portability tests for all four providers during Phase A, not retroactively.

---

## Key Findings

### Recommended Stack

Four LLM provider SDKs plus the existing Anthropic dependency. The stack research prioritizes **minimum version pins** and **Python 3.9 floor compatibility** — a hard constraint from the project's MSRV.

**Core provider dependencies:**
- **`anthropic>=0.72.0`** — Anthropic (first-class, already shipping in v2.0; keep for backward compatibility)
- **`openai>=1.30.0,<2.0`** — OpenAI + all OpenAI-compatible endpoints (vLLM, LM Studio, LocalAI); 1.x supports Python 3.9, 2.x requires 3.10+
- **`google-genai>=1.0.0,<3.0`** — Google Gemini (replacement for deprecated `google-generativeai`); requires Python 3.10+ (creates a runtime guard for 3.9)
- **`ollama>=0.5.0`** — Local Ollama (no API key, no network); most permissive Python floor (3.8+)
- **`pydantic>=2.0`** — Required by every provider for `.model_json_schema()` and `model_validate_json()` — not added to base dependencies (offline `build_diagnostics` must importable without pydantic)

**NOT adding:** LiteLLM, pydantic-ai, LangChain, instructor, json-repair (per PROJECT.md explicit rejections; custom Protocol + thin adapters cover all needs).

**Installation model (extras):**
```
[advisor]           = anthropic>=0.72.0 + pydantic>=2.0
[openai]            = openai>=1.30.0,<2.0 + pydantic>=2.0
[gemini]            = google-genai>=1.0.0,<3.0 + pydantic>=2.0 (Python 3.10+ enforced at runtime)
[ollama]            = ollama>=0.5.0 + pydantic>=2.0
[all-providers]     = fdars[advisor] + fdars[openai] + fdars[gemini] + fdars[ollama]
```

The base `fdars` package is importable without any provider extra. The offline `build_diagnostics` works with zero extras installed.

---

### Expected Features

**Must have (table stakes — P1):**
- `Provider` protocol + `AnthropicProvider` refactor (blocking all provider work; existing tests must not regress)
- `OpenAIProvider` with `base_url` parameter (covers OpenAI + all OpenAI-compatible local endpoints; highest demand after Anthropic)
- `OllamaProvider` (local/offline path, no API key; validates grounding invariant on constrained models)
- Validate-and-retry contract + centralized `_check_grounding` guard (required by all non-Anthropic providers to maintain grounding)
- `build_diagnostics` branches for depth, outliers, regression, regression_cv, spm, represent, classification
- Per-provider optional extras in `pyproject.toml` (`[openai]`, `[gemini]`, `[ollama]`)
- Refactor existing advisors onto provider layer without breaking offline paths
- MCP runner extension to new aspects

**Should have (competitive — P2):**
- `GeminiProvider` (third major cloud provider; completes the triad with Anthropic + OpenAI)
- Per-provider logging (DEBUG level only)
- Extensive per-provider integration tests with recorded-response fixtures (offline)

**Defer (v3.x+):**
- HTTP/SSE transport for MCP (remote access; deferred per v2.0 decision)
- ARL-aware SPM advisor (stochastic design; separate from deterministic `build_diagnostics`)
- Cross-aspect compound diagnostics ("given my smoothing and clustering, what should I do?")

---

### Architecture Approach

Convert the single-provider monolith (`advisor.py`, 1161 lines) into a package with three subpackages: `providers/` (protocol + 4 adapters), `aspects/` (9 per-aspect builders), and schema/prompt helpers. Key components:

1. **`Provider` protocol** — Runtime-checkable; all adapters implement `complete_structured(schema, messages, system) -> dict` + `supports_native_structured_output` flag
2. **Per-provider adapters** — Anthropic/OpenAI use native mode; Gemini/Ollama use JSON-mode with schema injection
3. **`ValidateAndRetry` wrapper** — Schema validation + repair-prompt retry (max 1 retry) + `_check_grounding` guard
4. **Per-aspect diagnostic builders** — Pure NumPy, offline, deterministic; lazy-imported
5. **Shared dispatcher + prompt system** — Single `_system_prompt(task, aspect)` function with base grounding invariant + aspect-specific clauses
6. **MCP tool layer** — `_SUPPORTED_METHODS` extended; tools remain compute-only

---

### Critical Pitfalls

1. **Schema Features Don't Port Across Providers** — OpenAI requires nullable unions; Gemini rejects `additionalProperties`; Ollama's constrained decoding silently fails if `think=True` is set. **Mitigation:** `schema_for(provider)` serializers per adapter; `test_schema_round_trip[provider]` offline tests with stored response fixtures.

2. **Validate-and-Retry Without Hard Contract** — Retry loops lacking ceiling, error state, or fabrication check lead to infinite loops, silent fabrication, or latency surprises. **Mitigation:** Define `max_retries=1` in `Provider` protocol before any adapter; repair prompts must re-include diagnostics; use constrained decoding instead of retries for local models.

3. **Grounding-Invariant Leaks** — New adapters omit system prompt, inject incorrectly, or return empty `Advice` without raising error. **Mitigation:** Centralize `_check_grounding(advice, diagnostics)` as post-generation validator; write `test_grounding_check_catches_fabrication` per adapter.

4. **Offline/CI Testing Traps** — Import-at-module-level breaks pytest in bare venvs; Python 3.9 vs. 3.10+ typing breaks 3.9 CI; env var leakage causes unexpected live tests. **Mitigation:** Deferred imports via `_require_*()` guards; recorded response fixtures per provider; gate integration tests on `FDARS_INTEGRATION=1` + provider key; Python 3.9 CI matrix.

5. **Dependency and Config Traps** — Version drift in `openai` breaks API; `base_url` without `api_key` triggers auth error; Gemini SDK namespace collision. **Mitigation:** Min version pins with comments; adapter maps `api_key=None` to dummy for local endpoints; use `google-genai` not deprecated `google-generativeai`; no SDK imports at package init.

6. **Prompt Sprawl & Diagnostic Key Divergence** — 7 aspects × 3 tasks × 4 providers = 84 naive test paths; temptation to duplicate prompts and use inconsistent key names. **Mitigation:** Single `_system_prompt(task, aspect)` function; shared `DiagnosticsKeys` namespace; two-layer test strategy (9 offline aspect + 4 provider fixture + 1 live per provider = 14 tests, not 84).

---

## Implications for Roadmap

### Phase A: Provider Protocol + Anthropic Adapter Refactor

**Rationale:** Foundation. Blocks all downstream work.

**Delivers:**
- `Provider` protocol + `AnthropicAdapter` + `ValidateAndRetry` + `resolve_provider()` factory
- Refactored `advise()` with optional `provider=` parameter (default: Anthropic)
- Package restructure: `advisor/` with `_schema.py`, `_prompts.py`, `providers/`, `aspects/`
- All 5 existing aspect builders moved to `advisor/aspects/`

**Tests:** Existing advisor tests pass unchanged; offline unit tests for retry path; bare-venv smoke test.

**Duration:** 4–6 weeks.

---

### Phase B: Per-Provider Adapter Implementation

**Rationale:** Can run in parallel with C after A completes. Validates grounding across all providers.

**Delivers:**
- `OpenAIAdapter` (with `base_url` for local endpoints)
- `GeminiAdapter` (structured output + json fallback)
- `OllamaAdapter` (local, constrained decoding)
- Per-adapter optional extras; offline fixture tests; grounding violation tests
- Python 3.9 compatibility guard for Gemini

**Tests:** 4 offline schema round-trip; 4 offline grounding violation; env-gated integration per provider.

**Duration:** 6–8 weeks (1.5–2 weeks per adapter).

---

### Phase C: Per-Aspect Diagnostic Builders

**Rationale:** Can run in parallel with B after A completes. Offline, deterministic, no provider dependency.

**Delivers:**
- `advisor/aspects/_base.py` (shared helpers)
- Five new aspect builders: depth, regression, monitoring, classification, represent
- Extended dispatcher; extended `_system_prompt()` with per-aspect clauses
- MCP extension; `DiagnosticsKeys` namespace

**Tests:** 7 offline determinism tests; `test_diagnostics_key_consistency`; MCP tool tests.

**Duration:** 8–10 weeks (1–1.5 weeks per aspect builder; SPM is highest complexity).

---

### Phase D: Surface Updates + Packaging + Testing Strategy

**Rationale:** Assembly and validation after A+B+C complete.

**Delivers:**
- Finalized `pyproject.toml` with all optional extras
- CI matrix (Python 3.9–3.14, per-provider integration tests env-gated)
- Bare-venv smoke test; test-strategy documentation
- Updated SKILL.md; walkthrough script gains `--provider` flag

**Duration:** 2–3 weeks.

---

### Phase E: Documentation

**Rationale:** Last phase; documents shipped system.

**Delivers:**
- Provider setup guide (env vars, credentials, Python 3.9 limitation for Gemini)
- Per-aspect advisor pages (depth, regression, monitoring, classification, represent)
- Updated advisor overview; updated API docs

**Duration:** 2–4 weeks.

---

## Phase Ordering Rationale

1. **Phase A first** — Blocking dependency for all other work. Provider protocol + ValidateAndRetry + `_check_grounding` must exist before any adapter.

2. **Phases B and C parallelizable** — No hard dependency on each other. Both depend on Phase A's package structure.

3. **Phase B validates grounding** — Offline fixture tests catch schema portability bugs before they ship.

4. **Phase C exploits parallelism within aspects** — Depth, regression, monitoring, classification can be built in parallel.

5. **Phase D is assembly** — Shorter, can proceed serially.

6. **Phase E is documentation** — Deferring it does not block functionality.

---

## Research Flags

**Phases likely needing deeper research during planning:**
- **Phase B:** Schema-portability per provider (OpenAI `nullable`, Gemini `additionalProperties`, Ollama `think+format` conflict). Confirm Ollama structured-output stability (issue #10929).
- **Phase C:** SPM diagnostics complexity (highest in all aspects). Validate `spe_moment_match_diagnostic` fdars function signature.

**Phases with standard patterns (skip dedicated research-phase):**
- **Phase A:** Well-established pattern (refactoring existing code). Standard planning sufficient.
- **Phase D:** Standard CI/packaging patterns.
- **Phase E:** No research needed; documentation follows shipped interface.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | HIGH | All four provider SDKs verified against live PyPI + official docs. Version pins, Python floors, structured-output API shapes confirmed. Anthropic already shipping provides reference implementation. |
| **Features** | HIGH | Derived directly from existing `advisor.py`, v2.0 shipped coverage, and fdars library inventory. Per-aspect diagnostics cross-checked against fdars module signatures. MVP aligns with dependency graph. |
| **Architecture** | HIGH | Direct codebase analysis (`advisor.py` 1161 lines, MCP, SKILL.md, PROJECT.md). Package refactoring confirmed against existing `sys.modules` injection. Component boundaries derived from code inspection. |
| **Pitfalls** | MEDIUM | Derived from codebase patterns + provider SDK docs + GitHub issues (Ollama #10929, Gemini #1815/#706, OpenAI). Community writeups on validate-and-retry cited with LOW confidence (needs Phase B validation). Grounding leaks extrapolated from Anthropic pattern — extent on new providers unknown until Phase B integration tests. |

**Overall confidence:** **HIGH** for roadmap structure and phase ordering. **MEDIUM** for detailed pitfall mitigation (will be refined during Phase B implementation).

### Gaps to Address

1. **Ollama structured-output reliability** — Constrained decoding working since v0.5, but `think+format` conflict (issue #15260) indicates evolving behavior. Mitigation: Phase B planning includes Ollama spike to confirm v0.5+ stability.

2. **Gemini 2.5 vs. 2.0 inconsistency** — Structured output fails on Gemini 2.5 with prior tool calls in history, but succeeds on 2.0. Unknown if bug or expected. Mitigation: Phase B planning includes live Gemini test with/without message history.

3. **Google-genai namespace stability** — Switch from deprecated `google-generativeai` to `google-genai` documented; `google-genai` 3.0.0 warned to have breaking changes. Mitigation: Phase B monitoring of release notes; Phase D CI version check.

4. **SPM diagnostics completeness** — `spe_moment_match_diagnostic` fdars function signature and kurtosis return format need validation. Mitigation: Phase C planning includes spike on fdars monitoring module.

5. **Multi-tenant CI secrets management** — Env var gating for integration tests recommended but not yet deployed. Mitigation: Phase D CI setup enforces strict gating and fails fast if key missing.

---

## Summary for Roadmapper

**Critical prerequisite:** Provider protocol + Anthropic refactor (Phase A) blocks all downstream work. No adapters, no aspects, no MCP can proceed until this phase ships.

**Parallelization opportunity:** Phases B and C are independent and can run in parallel after Phase A.

**Risk mitigation:** Phase B must include offline schema-portability tests for all four providers (stored response fixtures). Phase C must include offline determinism tests for all 9 aspects. These validation gates prevent silent schema mismatches and diagnostic key divergence from shipping.

**Testing strategy:** Two-layer approach (offline aspect tests + provider tests) avoids 84-path combinatorial explosion. Live end-to-end tests capped at 4 (one per provider).

**Confidence:** HIGH for phase ordering and structure. MEDIUM for detailed pitfall mitigation (will be refined during Phase B implementation).

---

*Research completed: 2026-08-12*  
*Synthesized by: gsd-synthesizer agent*  
*Ready for roadmap creation: yes*
