# Requirements: pyfda — v3.0 Provider-Agnostic Advisor, Full-Library Coverage

**Defined:** 2026-08-12
**Core Value:** The fdars AI advisor must work with any LLM backend — cloud or local — while the grounding invariant holds everywhere: fdars computes every number, the LLM only interprets and cites it. Every fdars analysis aspect gets advisor coverage on par with clustering.

## v1 Requirements

Requirements for this milestone (v3.0). Each maps to roadmap phases.

### Provider Abstraction (PROV)

- [ ] **PROV-01**: A `Provider` protocol defines a uniform structured-completion interface (`complete_structured(schema, messages, system)`, `name`, `model`, `supports_native_structured_output`) that all backends implement.
- [ ] **PROV-02**: The existing Anthropic path is refactored into an `AnthropicProvider` adapter behind the protocol with no change to `advise()`'s public behavior or outputs (existing advisor tests stay green).
- [ ] **PROV-03**: An `OpenAIProvider` adapter supports OpenAI and any OpenAI-compatible endpoint via a configurable `base_url` (vLLM / LM Studio / LocalAI).
- [ ] **PROV-04**: An `OllamaProvider` adapter runs fully local with no API key.
- [ ] **PROV-05**: A `GeminiProvider` adapter supports Google Gemini (with the required Pydantic→Gemini schema translation).
- [ ] **PROV-06**: The user selects provider and model via explicit `advise(provider=…, model=…)` parameters and/or environment variables (`FDARS_ADVISOR_PROVIDER` / `_MODEL` / `_BASE_URL` + per-provider API keys), with documented precedence.
- [ ] **PROV-07**: Each provider ships as an optional extra (`[openai]`, `[gemini]`, `[ollama]` alongside existing `[advisor]`); the base package imports and the offline core runs without any provider installed (a missing extra raises an actionable ImportError).

### Grounding Across Providers (GROUND)

- [ ] **GROUND-01**: Providers with native structured output / tool-use (Anthropic, OpenAI) return schema-validated `Advice` via the native path.
- [ ] **GROUND-02**: Providers/models without reliable native structured output use a validate-and-retry/repair path (Pydantic validation, ≤2 retries with the full diagnostics re-included) and fail deterministically after the cap — no silent fabrication.
- [ ] **GROUND-03**: A centralized grounding check (`_check_grounding`) enforces, on every provider, that recommendations cite computed diagnostic values and that the LLM introduces no numbers absent from the diagnostics.
- [ ] **GROUND-04**: Provider refusals or empty responses raise a clear error rather than yielding a vacuously-valid `Advice`.

### Per-Aspect Advisor Coverage (ASPECT)

- [ ] **ASPECT-01**: `build_diagnostics` supports represent/basis with deterministic, offline diagnostics.
- [ ] **ASPECT-02**: `build_diagnostics` supports depth and outliers.
- [ ] **ASPECT-03**: `build_diagnostics` supports classification.
- [ ] **ASPECT-04**: `build_diagnostics` supports regression and regression-CV (`fregre_lm` / `fregre_pls` / `fregre_cv`).
- [ ] **ASPECT-05**: `build_diagnostics` supports monitoring/SPM (Phase-1 T²/SPE, `spe_moment_match_diagnostic`), excluding stochastic ARL.
- [ ] **ASPECT-06**: Every fdars analysis aspect (clustering, smoothing, alignment, basis/represent, depth/outliers, classification, regression/FPCA, monitoring/SPM) offers grounded advice task families (interpretation, parameter guidance, method guidance) through the same schema + grounding machinery — no per-aspect duplication.
- [ ] **ASPECT-07**: Aspect is always caller-specified (never auto-detected from result keys) to avoid key-collision misrouting.

### Surface Integration (SURF)

- [ ] **SURF-01**: The MCP tool surface exposes the new aspect diagnostics/methods while remaining LLM-free (compute-only; grounding invariant preserved).
- [ ] **SURF-02**: Provider selection is available through the Python API `advise()`; the MCP tools do not call `advise()`.
- [ ] **SURF-03**: The Agent Skill documents provider selection (including local/offline) and the full per-aspect advisor coverage.

### Testing, Packaging & CI (QUAL)

- [ ] **QUAL-01**: Two-layer offline tests — per-aspect diagnostics fixtures × per-provider adapter fixtures (recorded responses / mocks) — cover the aspect × provider contract without network.
- [ ] **QUAL-02**: Env-gated live integration tests, one per provider, skip cleanly without keys / a local server.
- [ ] **QUAL-03**: CI matrix covers Python 3.9–3.14 with correct extra/version gating (`openai<2.0` on 3.9; `[gemini]`/`[mcp]` 3.10+); a bare-venv smoke test proves the core imports with no provider extra installed.
- [ ] **QUAL-04**: All offline tests (core + aspect + adapter) run network-free and deterministically.

### Documentation (DOCS)

- [ ] **DOCS-01**: A provider setup guide covers all four backends (keys, `base_url`, local Ollama, selection/precedence).
- [ ] **DOCS-02**: Per-aspect advisor pages document diagnostics + task families for each fdars aspect.
- [ ] **DOCS-03**: The AI Advisor overview and Python API pages are updated to reflect provider-agnostic operation and full-library coverage; the docs build stays offline (`mkdocs build --strict`).

## v2 Requirements

Deferred to a future release (v3.x+). Tracked but not in this roadmap.

### Deferred (FUT)

- **FUT-01**: HTTP/SSE transport for the MCP server (remote access; deferred per the v2.0 decision — MCP stays stdio).
- **FUT-02**: ARL-aware / stochastic SPM advisor (separate from the deterministic `build_diagnostics` guarantee).
- **FUT-03**: Cross-aspect compound diagnostics ("given my smoothing and clustering, what should I do?").
- **FUT-04**: Per-provider DEBUG-level logging.
- **FUT-05**: Streaming responses.
- **FUT-06**: Additional providers (AWS Bedrock, Azure OpenAI, Mistral, etc.).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Third-party LLM abstraction libs (LiteLLM, pydantic-ai, LangChain) | Custom `Provider` protocol only — avoids heavy transitive deps and keeps the grounding/retry contract under our control |
| Auto-detection of aspect from result keys | Key collisions (e.g. `r_squared`, `edf`) make it unreliable; aspect is always caller-specified |
| fdars-core / Rust compute changes | The advisor consumes existing fdars outputs; no core changes in this milestone |
| Stochastic ARL inside `build_diagnostics` | Would break the offline determinism guarantee |
| HTTP/SSE MCP transport | Deferred (FUT-01); MCP stays stdio for local/CI usage |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROV-01 | Phase 19 | Pending |
| PROV-02 | Phase 19 | Pending |
| PROV-06 | Phase 19 | Pending |
| GROUND-01 | Phase 19 | Pending |
| GROUND-02 | Phase 19 | Pending |
| GROUND-03 | Phase 19 | Pending |
| GROUND-04 | Phase 19 | Pending |
| PROV-03 | Phase 20 | Pending |
| PROV-04 | Phase 20 | Pending |
| PROV-05 | Phase 20 | Pending |
| PROV-07 | Phase 20 | Pending |
| ASPECT-01 | Phase 21 | Pending |
| ASPECT-02 | Phase 21 | Pending |
| ASPECT-03 | Phase 21 | Pending |
| ASPECT-04 | Phase 21 | Pending |
| ASPECT-05 | Phase 21 | Pending |
| ASPECT-06 | Phase 21 | Pending |
| ASPECT-07 | Phase 21 | Pending |
| SURF-01 | Phase 22 | Pending |
| SURF-02 | Phase 22 | Pending |
| SURF-03 | Phase 22 | Pending |
| QUAL-01 | Phase 23 | Pending |
| QUAL-02 | Phase 23 | Pending |
| QUAL-03 | Phase 23 | Pending |
| QUAL-04 | Phase 23 | Pending |
| DOCS-01 | Phase 24 | Pending |
| DOCS-02 | Phase 24 | Pending |
| DOCS-03 | Phase 24 | Pending |
