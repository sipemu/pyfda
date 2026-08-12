# Phase 20: Additional Provider Adapters - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous smart-discuss — decisions grounded in `.planning/research/STACK.md` + `ARCHITECTURE.md`; builds on the Phase 19 `Provider` protocol)

<domain>
## Phase Boundary

Any of OpenAI (incl. OpenAI-compatible local endpoints), Ollama (fully local), and Gemini can back the advisor through the **Phase 19 `Provider` protocol**, each installable as its own optional extra, with the grounding invariant holding on every backend.

In scope (REQ-IDs): PROV-03, PROV-04, PROV-05, PROV-07.

Out of scope: new per-aspect `build_diagnostics` branches (Phase 21); MCP/Skill surface changes (Phase 22); the CI matrix / bare-venv smoke automation (Phase 23 — this phase only adds the extras to `pyproject.toml` and offline adapter tests); docs (Phase 24).
</domain>

<decisions>
## Implementation Decisions

### Grounded in research (STACK.md — versions verified against live PyPI; ARCHITECTURE.md build order)

- **Each adapter is a new file under `advisor/providers/`** implementing the Phase 19 `Provider` protocol (`complete_structured(schema, messages, system) -> dict`, `name`, `model`, `supports_native_structured_output`). Nothing in `advise()` / `ValidateAndRetry` / `_check_grounding` changes — the centralized grounding + retry contract from Phase 19 already covers every provider; adapters only implement `complete_structured`.
- **OpenAI (PROV-03):** use `openai>=1.30,<2.0` (the `<2.0` pin keeps Python 3.9 support — openai 2.x requires 3.10+). Native structured output via `response_format={"type":"json_schema", ...}` → `supports_native_structured_output=True`. The `OpenAI(base_url=…)` constructor param covers ALL OpenAI-compatible endpoints (vLLM/LM Studio/LocalAI) — no separate deps. For local compat endpoints, pass a dummy `api_key="none"` when none is set to avoid SDK-level auth errors. `base_url` sourced from `advise(base_url=…)` param or `FDARS_ADVISOR_BASE_URL` (Phase 19 precedence).
- **Ollama (PROV-04):** use the native `ollama>=0.6.2` client (no API key). Prefer `format=<schema>` (constrained-grammar decoding, more reliable than routing Ollama through the OpenAI base_url path). If a given local model's structured output is unreliable, the Phase 19 `ValidateAndRetry` fallback already handles it — set `supports_native_structured_output` per what `format=` guarantees and let the centralized retry cover the rest.
- **Gemini (PROV-05):** use `google-genai>=1.0,<3.0` (NOT the deprecated `google-generativeai`). This SDK requires Python ≥3.10, so the `[gemini]` extra is 3.10+ only. Native structured output via `response_schema` in `GenerationConfig` — requires a **Pydantic→Gemini schema translation** step (Gemini rejects `additionalProperties`; nested `Recommendation` list + `Literal` fields must map to Gemini's JSON-schema subset). System prompt goes in `system_instruction`, not a message role.
- **Extras (PROV-07):** add `[openai]`, `[gemini]`, `[ollama]` to `pyproject.toml`, each including `pydantic>=2.0`; optionally a convenience `[all-providers]` meta-extra for dev/test. Base package still imports with NO provider installed. Each adapter uses a **deferred import** (`_require_openai()` / `_require_gemini()` / `_require_ollama()` pattern, mirroring `_require_anthropic()`); a missing extra raises an **actionable ImportError** naming the `pip install fdars[<extra>]` command.
- **Selection:** extend Phase 19's `resolve_provider()` to recognize `"openai"`, `"ollama"`, `"gemini"` (currently anthropic-only). `provider=None` still defaults to Anthropic (unchanged).

### Claude's Discretion

Per-provider default model strings (e.g. a sensible current OpenAI / Gemini / Ollama default), the exact Gemini schema-translation helper implementation, and whether OpenAI-compatible endpoints default to native or always route through validate-and-retry — at Claude's discretion, guided by STACK.md's open questions. Document the chosen defaults.
</decisions>

<code_context>
## Existing Code Insights

- `python/fdars/advisor/providers/` (from Phase 19): `_protocol.py` (Provider), `anthropic.py` (AnthropicProvider — the adapter pattern to mirror), `_validate.py` (ValidateAndRetry, `_check_grounding`, GroundingViolationError), `_factory.py` (`resolve_provider` — extend here), `__init__.py`.
- `_check_grounding` is called centrally in `advise()` after `complete_structured()` — new adapters inherit it for free.
- `pyproject.toml` — `[advisor] = anthropic>=0.72.0, pydantic>=2.0`, `[mcp] = mcp>=2.0.0`. Add the three new provider extras alongside.
- Phase 19 established: deferred provider imports, offline core, `FDARS_ADVISOR_PROVIDER`/`_MODEL`/`_BASE_URL` env precedence.
</code_context>

<specifics>
## Specific Ideas

- Offline adapter tests must mock each SDK (`openai.OpenAI`, `ollama.chat`, `google.genai` client) — no network, no keys. Cover: native path returns validated `Advice`; missing-extra → actionable ImportError; `base_url` wiring for OpenAI-compat; Gemini schema translation produces a Gemini-valid schema; provider-string resolution in `resolve_provider`.
- Env-gated live integration test per provider (one each) that skips cleanly without keys / without a running Ollama server. (The full CI matrix + bare-venv smoke automation is Phase 23; this phase just needs the tests to exist and skip cleanly.)
- Grounding invariant must be exercised per provider (fabricated-number rejection) using the centralized check — at least via mocks.
</specifics>

<deferred>
## Deferred Ideas

- New per-aspect diagnostics (depth/outliers/regression/spm/represent/classification) → Phase 21.
- CI matrix across Python 3.9–3.14 + bare-venv smoke test → Phase 23 (this phase only edits `pyproject.toml` extras and adds offline tests).
</deferred>
