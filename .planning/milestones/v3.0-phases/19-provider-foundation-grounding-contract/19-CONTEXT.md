# Phase 19: Provider Foundation & Grounding Contract - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous smart-discuss — decisions grounded in `.planning/research/ARCHITECTURE.md` + `SUMMARY.md`)

<domain>
## Phase Boundary

The advisor runs behind a uniform `Provider` protocol with the grounding/retry machinery centralized, so every later adapter and aspect inherits a checked grounding contract instead of re-implementing it. **This is a pure refactor: existing Anthropic behavior and outputs are unchanged.**

In scope (REQ-IDs): PROV-01, PROV-02, PROV-06, GROUND-01, GROUND-02, GROUND-03, GROUND-04.

Out of scope for this phase: OpenAI/Ollama/Gemini adapters (Phase 20), new per-aspect `build_diagnostics` branches (Phase 21), MCP/Skill surface changes (Phase 22), packaging/CI matrix (Phase 23), docs (Phase 24).
</domain>

<decisions>
## Implementation Decisions

### Grounded in research (ARCHITECTURE.md — HIGH confidence, direct code analysis)

- **`advisor.py` becomes a package `advisor/`** with `providers/` and `aspects/` subpackages. `advisor/__init__.py` re-exports the current public names so the existing `sys.modules["fdars.advisor"] = advisor` injection in `python/fdars/__init__.py` keeps working with zero public-API change.
- **Extraction point:** the inline Anthropic call currently in `advise()` (≈ lines 980–1007 of the existing `advisor.py`) moves into `AnthropicProvider.complete_structured(...)`. Everything else (schema, prompt builder, dispatcher, offline diagnostics builders) moves file-to-file unchanged.
- **`Provider` protocol surface (PROV-01):** `complete_structured(schema, messages, system) -> dict`, plus `name: str`, `model: str`, and a `supports_native_structured_output: bool` capability flag.
- **Grounding centralized (GROUND-03):** a single `_check_grounding(advice, diagnostics)` validator (in the base provider layer) runs on **every** provider path — it rejects any `Advice` whose recommendations cite numbers absent from the diagnostics. Not per-adapter.
- **Validate-and-retry (GROUND-02):** one shared `ValidateAndRetry` wrapper. Native path used when `supports_native_structured_output` is true; otherwise prompt-JSON → Pydantic validate → repair-retry with the **full diagnostics re-included**, `max_retries=2` hardcoded, deterministic failure after the cap (raise, never fabricate).
- **Refusal/empty handling (GROUND-04):** a provider refusal or empty response raises a clear error, never a vacuously-valid `Advice()`.
- **Selection/precedence (PROV-06):** a `resolve_provider()` factory reads explicit `advise(provider=…, model=…)` params first, then env vars (`FDARS_ADVISOR_PROVIDER` / `FDARS_ADVISOR_MODEL` / `FDARS_ADVISOR_BASE_URL` + per-provider API keys). `provider=None` reproduces today's Anthropic default (backward compatible).
- **`anthropic` stays a deferred import** via the existing `_require_anthropic()` pattern; base package still imports with no provider installed.

### Claude's Discretion

Exact module/file names within `advisor/providers/` and `advisor/base.py`, the precise `_check_grounding` numeric-citation matching heuristic, and test organization — at Claude's discretion, guided by existing conventions and `test_advisor.py`.
</decisions>

<code_context>
## Existing Code Insights

- `python/fdars/advisor.py` — single ~1160-line module: `build_diagnostics()`, `advise()` (inline Anthropic `client.messages.parse`), `Advice`/`Recommendation` Pydantic schema, `_system_prompt()`, offline diagnostics builders.
- `python/fdars/__init__.py` — injects `fdars.advisor` into `sys.modules`; must keep working when `advisor.py` becomes `advisor/`.
- `tests/test_advisor.py` — offline `TestBuildDiagnosticsOffline` + env-gated `TestAdvisorIntegration`. **All must stay green unchanged** (this is the pure-refactor guardrail).
- `pyproject.toml` — `[advisor] = anthropic>=0.72.0, pydantic>=2.0` (unchanged this phase).

Codebase specifics to be confirmed during plan-phase research (exact line numbers, current `advise()` signature).
</code_context>

<specifics>
## Specific Ideas

- The pure-refactor guarantee is the acceptance gate: `pytest tests/test_advisor.py` passes identically before and after, and `provider=None` output is unchanged.
- Add unit tests for: native vs fallback path selection, `_check_grounding` rejection of fabricated numbers, retry cap → deterministic raise, refusal → raise, and env/param precedence resolution. These can use a fake in-memory Provider (no network).
</specifics>

<deferred>
## Deferred Ideas

- Real OpenAI/Ollama/Gemini adapters → Phase 20 (this phase only needs the protocol + Anthropic adapter + a test-only fake provider to exercise the fallback/grounding paths).
</deferred>
