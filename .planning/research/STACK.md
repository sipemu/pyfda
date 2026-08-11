# Stack Research

**Domain:** Provider-agnostic LLM advisor layer — custom `Provider` protocol + per-backend adapters (Anthropic, OpenAI/OpenAI-compatible, Google Gemini, Ollama local)
**Researched:** 2026-08-12
**Confidence:** MEDIUM (package versions verified against PyPI live pages; structured-output API shapes verified against official docs and Ollama docs; Python version constraints verified)

---

## Context

This STACK.md covers **only the additions needed for v3.0** — provider-agnostic backends plus full-library advisor coverage. The existing stack (MkDocs, SVGO, matplotlib, pytest-markdown-docs — from the v1.0 STACK.md) is unchanged. The existing advisor (anthropic>=0.72.0, pydantic>=2.0) is already shipped; this document prescribes what NEW deps are needed and how to wire them.

The hard constraints from PROJECT.md:

- **No LiteLLM, no pydantic-ai, no LangChain** — custom `Provider` protocol only.
- **Core stays offline** — `build_diagnostics` never imports any provider SDK; tests run without network.
- **Python 3.9–3.14** — the package targets this range; two of the new SDKs require >=3.10 (constraint documented per provider).
- **CI network-free** — integration tests are env-gated; offline adapter mocks required for all backends.

---

## Recommended Stack

### Existing (keep, no changes)

| Technology | Version (current) | Purpose | Notes |
|------------|-------------------|---------|-------|
| `anthropic` | `>=0.72.0` | First-class Anthropic backend | Already in `[advisor]` extra; `client.messages.parse(output_format=Advice)` is the structured-output path |
| `pydantic` | `>=2.0` | Schema validation and structured output | Already in `[advisor]` extra; `.model_json_schema()` used as input to every provider's schema API |

### New Backend SDKs

| Library | Pin | Python floor | Purpose | Why this, not httpx |
|---------|-----|--------------|---------|---------------------|
| `openai` | `>=1.30.0,<2.0` | 3.7.1+ (1.x) | OpenAI + all OpenAI-compatible endpoints via `base_url=` | The 1.x series covers 3.9; the 2.x series (2.54.0 current) requires 3.10. Pin to 1.x to stay within fdars's 3.9 floor. The `base_url` parameter on `OpenAI()` redirects to any endpoint (vLLM, LM Studio, LocalAI, Ollama-OpenAI-compat) with zero additional deps. Native `parse()`/`response_format` structured-output support in 1.x. |
| `google-genai` | `>=1.0.0,<3.0` | 3.10+ | Google Gemini backend | The **only** current SDK — `google-generativeai` was deprecated Nov 2025 and ended support. `google-genai` 2.17.0 (Aug 2026) is GA; pin `<3.0` per upstream warning that 3.0.0 has breaking changes. Native `response_json_schema=` structured-output support. Requires Python 3.10+, so this extra cannot be installed on 3.9. |
| `ollama` | `>=0.5.0` | 3.8+ | Local Ollama backend (no API key, no network) | Official `ollama` Python SDK (0.6.2, Apr 2026). Python >=3.8 — the most permissive floor of all providers. Native `format=` parameter for constrained JSON-schema decoding (introduced Ollama v0.5). Avoid the OpenAI-compat path for Ollama structured outputs — the native client's `format=` is more reliable than `response_format=` through the OpenAI-compat layer. |

**Why NOT plain httpx for any of these:**

- `openai` 1.x is a thin, well-maintained client; the `base_url=` param already covers all OpenAI-compatible endpoints — httpx would replicate it for no benefit.
- `google-genai` handles auth (OAuth / API key / service account), retry, and streaming — not worth reimplementing.
- `ollama` SDK wraps the local REST API simply; httpx would save ~15 KB of dependency but gain nothing.

httpx is acceptable only as an internal implementation detail inside adapters (all three SDKs use it or httpx-core internally).

### Supporting Libraries

| Library | Already present? | Version | Purpose | When needed |
|---------|-----------------|---------|---------|-------------|
| `pydantic` | Yes (`[advisor]`) | `>=2.0` | Schema definition, `.model_json_schema()`, `model_validate_json()` for repair path | Every provider path |
| `json-repair` | NO — do NOT add | — | Third-party JSON repair | **Do not add** — implement a simple 1-retry `model_validate_json` + reprompt loop; a full repair lib is overkill and a dep-bloat risk |

---

## Structured-Output API Shape Per Provider

This is the most consequential section for the adapter implementation.

### Anthropic (existing, keep)

```python
# client.messages.parse with Pydantic output_format — already used in advisor.py
response = client.messages.parse(
    model=model,
    max_tokens=16000,
    thinking={"type": "adaptive"},
    system=system_prompt,
    output_format=Advice,          # Pydantic BaseModel → SDK converts to JSON schema
    messages=[{"role": "user", "content": user_content}],
)
advice = response.parsed_output   # Advice instance, schema-validated
```

- **Confidence:** HIGH — already shipping in v2.0.
- **Fallback:** Not needed; `messages.parse` raises on schema failure.
- **Beta header:** SDK injects `"structured-outputs-2025-12-15"` beta header automatically.

### OpenAI (new)

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://api.openai.com/v1",   # or http://localhost:1234/v1 for LM Studio etc.
)

# 1.x structured-output path (compatible with 3.9):
response = client.chat.completions.create(
    model=model,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Advice",
            "strict": True,
            "schema": Advice.model_json_schema(),
        },
    },
    messages=[{"role": "system", "content": system_prompt},
              {"role": "user", "content": user_content}],
)
raw_json = response.choices[0].message.content
advice = Advice.model_validate_json(raw_json)  # validate; retry on ValidationError
```

- **OpenAI-compatible endpoints (vLLM, LM Studio, LocalAI, Ollama-compat):** Set `base_url=` and `api_key="ollama"` (or any string). These endpoints implement the same `/v1/chat/completions` API surface. However, not all of them reliably support `json_schema` with `strict: true` — vLLM and LM Studio do; LocalAI has partial support; Ollama's OpenAI-compat layer may not honor the schema. Use the **validate-and-retry fallback** for all OpenAI-compat endpoints.
- **Validate-and-retry fallback:** Catch `pydantic.ValidationError` or `json.JSONDecodeError`, reprompt with the error message included once, then raise if second attempt also fails.
- **Python 3.9:** Use `openai>=1.30.0,<2.0`. The 2.x series (current: 2.54.0) requires Python 3.10+.

### Google Gemini (new)

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model=model,                                        # e.g. "gemini-2.0-flash"
    contents=user_content,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_json_schema=Advice.model_json_schema(),
    ),
)
raw_json = response.text
advice = Advice.model_validate_json(raw_json)
```

- **Python floor:** `google-genai >=1.0,<3.0` requires Python >=3.10. The `[gemini]` extra must declare `python_requires` or carry a runtime guard so users on 3.9 get a clear error.
- **Schema subset:** Gemini supports a subset of JSON Schema. Deep nesting and `anyOf`/`oneOf` may be rejected. The `Advice` schema (flat object with nested `Recommendation` list) is within supported bounds — verify in adapter tests.
- **Version pin rationale:** Pin `<3.0` because upstream (googleapis/python-genai) explicitly warns users to pin `<3.0.0` ahead of a breaking-change release.
- **Validate-and-retry:** Apply the same retry pattern as OpenAI (one retry on `ValidationError`).

### Ollama (new, local)

```python
import ollama

response = ollama.chat(
    model=model,                        # e.g. "llama3.2", "mistral"
    messages=[{"role": "user", "content": full_prompt}],
    format=Advice.model_json_schema(),  # dict accepted directly since Ollama v0.5
    options={"temperature": 0},         # lower temperature improves schema adherence
)
raw_json = response.message.content
advice = Advice.model_validate_json(raw_json)
```

- **No API key, no network call from CI** — Ollama is a local daemon; tests can mock `ollama.chat`.
- **Python floor:** `ollama>=0.5.0` requires Python >=3.8 — no constraint on 3.9.
- **Constrained decoding:** Ollama applies grammar-constrained decoding from the JSON schema since v0.5. More reliable than prompting alone with weaker local models, but still imperfect — the validate-and-retry fallback is required.
- **Include schema in prompt:** Add the JSON schema to the prompt text as a reference ("Respond with JSON matching this schema: …"). This significantly improves adherence on smaller models.
- **Not the OpenAI-compat path:** The native `ollama` SDK `format=` parameter is preferred over routing through `OpenAI(base_url="http://localhost:11434/v1")` for Ollama, because the OpenAI-compat layer's `response_format=json_schema` support is inconsistent across Ollama versions.

---

## Validate-and-Retry Fallback (shared across all backends)

For providers where structured-output guarantees are weaker (OpenAI-compat endpoints, Gemini with complex schemas, Ollama with small models), implement a single shared retry helper inside the adapter base class:

```python
def _parse_with_retry(raw_json: str, model_cls, call_fn, max_retries: int = 1):
    """Try model_validate_json; on failure reprompt once with the error."""
    try:
        return model_cls.model_validate_json(raw_json)
    except (json.JSONDecodeError, ValidationError) as exc:
        if max_retries == 0:
            raise
        repair_prompt = (
            f"Your previous response was not valid JSON matching the schema. "
            f"Error: {exc}. Please correct and respond with only valid JSON."
        )
        raw_json = call_fn(repair_prompt)
        return model_cls.model_validate_json(raw_json)  # raise on second failure
```

Do NOT add `json-repair` or `instructor` as deps — this simple loop covers the actual failure modes (missing fields, markdown-fenced JSON, type coercion errors) without extra dependencies.

---

## Optional Extras Design

```toml
# pyproject.toml additions

[project.optional-dependencies]
# Existing
advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]
mcp    = ["mcp>=2.0.0"]           # Python 3.10+ (note already in pyproject.toml)

# New per-provider extras
openai = ["openai>=1.30.0,<2.0", "pydantic>=2.0"]
gemini = ["google-genai>=1.0.0,<3.0", "pydantic>=2.0"]
ollama = ["ollama>=0.5.0", "pydantic>=2.0"]

# Meta-extra for "I want everything" — install all at once
all-providers = [
    "fdars[advisor]",
    "fdars[openai]",
    "fdars[gemini]",
    "fdars[ollama]",
]
```

**Rationale:**

- `[advisor]` stays as-is (backward compatibility for existing Anthropic users).
- Each `[openai]`, `[gemini]`, `[ollama]` includes `pydantic>=2.0` because every adapter needs it for `.model_json_schema()` and `model_validate_json()`. This is a ~1MB dep but already required via `[advisor]`; installing any provider extra effectively brings it in.
- `pydantic` is NOT added to the base `dependencies` list — `build_diagnostics` and the offline core must remain importable without it.
- `[all-providers]` is a convenience meta-extra for docs examples and test environments.
- `[gemini]` and `[openai 2.x]` both require Python 3.10+; the extras can be installed but the runtime guard in the adapter should check `sys.version_info >= (3, 10)` and raise `ImportError` with a clear message on 3.9.

**Python 3.9 constraint table:**

| Extra | Python 3.9 installable? | Notes |
|-------|------------------------|-------|
| `[advisor]` (Anthropic) | Yes | anthropic 0.72+ supports 3.9 |
| `[openai]` (1.x pin) | Yes | openai 1.x supports 3.7.1+ |
| `[gemini]` | No (runtime error) | google-genai requires 3.10+ |
| `[ollama]` | Yes | ollama SDK supports 3.8+ |

---

## What NOT to Add

| Do NOT add | Why | Use instead |
|-----------|-----|-------------|
| `litellm` | Explicitly rejected per PROJECT.md; ~70MB dep; version churn; opaque routing; not needed when each adapter is 50 lines | Custom `Provider` protocol with per-backend adapters |
| `pydantic-ai` | Explicitly rejected per PROJECT.md; heavy framework; forces opinionated agent patterns | Custom `Provider` protocol |
| `langchain` / `langchain-*` | Explicitly rejected per PROJECT.md; massive dep tree; unnecessary abstraction | Custom `Provider` protocol |
| `instructor` | Third-party retry/repair framework; adds a dep for functionality covered by a ~20-line retry helper | Inline `_parse_with_retry` in adapter base |
| `json-repair` | Overkill; the failure modes (markdown fences, type coercion) are handled by reprompt; real schema violations should surface as errors | `model_validate_json` + one reprompt |
| `openai>=2.0` | Requires Python 3.10+, breaking 3.9 support; 2.x API shape changed from 1.x | `openai>=1.30.0,<2.0` |
| `google-generativeai` | Deprecated since Nov 2025, support ended; no new features | `google-genai` |
| `aiohttp` / async-first design | The current advisor is sync; fdars users expect sync; adding async doubles the surface without clear benefit for this use case | Sync `Provider` protocol; add async adapter later if needed |

---

## Provider Protocol Design (implementation note)

The `Provider` protocol that all adapters implement should be minimal:

```python
# python/fdars/advisor/provider.py
from typing import Protocol, runtime_checkable
from fdars.advisor import Advice

@runtime_checkable
class Provider(Protocol):
    def complete(self, system: str, user: str, output_cls: type) -> Advice:
        """Call the LLM and return a schema-validated Advice object."""
        ...
```

Each backend adapter (`AnthropicProvider`, `OpenAIProvider`, `GeminiProvider`, `OllamaProvider`) implements `complete()` and handles its own import guard (`try: import openai; except ImportError: raise ImportError("pip install fdars[openai]")`).

The existing `advise()` function in `advisor.py` should be refactored to:

```python
def advise(diagnostics, *, task, domain_context, provider: Provider | None = None, model: str | None = None) -> Advice:
    if provider is None:
        provider = _default_provider(model)  # backward compat: defaults to Anthropic
    ...
```

This preserves backward compatibility (existing callers with no `provider` arg keep working) while enabling provider injection for tests and new backends.

---

## Version Compatibility

| Package | Compatible Python | Compatible with `pydantic>=2.0` | Notes |
|---------|-------------------|--------------------------------|-------|
| `anthropic>=0.72.0` | 3.8+ | Yes | Already shipping |
| `openai>=1.30.0,<2.0` | 3.7.1+ | Yes | Use 1.x for 3.9 compat |
| `google-genai>=1.0.0,<3.0` | 3.10+ | Yes | Pin <3.0 per upstream warning |
| `ollama>=0.5.0` | 3.8+ | Yes | Best Python floor |
| `pydantic>=2.0` | 3.8+ | — | Required by all adapters |
| `mcp>=2.0.0` | 3.10+ | Yes | Unchanged from current |

---

## Installation

```bash
# Anthropic (existing)
pip install "fdars[advisor]"

# OpenAI + OpenAI-compatible (vLLM, LM Studio, LocalAI)
pip install "fdars[openai]"

# Google Gemini (Python 3.10+ only)
pip install "fdars[gemini]"

# Ollama local (Python 3.8+, no API key)
pip install "fdars[ollama]"

# All providers at once (for docs examples and test envs)
pip install "fdars[all-providers]"

# Dev environment with all providers + tests
pip install "fdars[all-providers,dev,mcp]"
```

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| `openai>=1.30.0,<2.0` | `openai>=2.0` | 2.x requires Python 3.10+, breaking 3.9; 1.x has full structured-output support and covers 3.9 |
| `openai` SDK with `base_url=` | Separate deps per compatible endpoint | One SDK covers Ollama-compat, vLLM, LM Studio, LocalAI — no per-server dep needed |
| `google-genai` | `google-generativeai` | Deprecated Nov 2025; new features only in `google-genai` |
| `google-genai <3.0` | Latest unconstrained | Upstream warns 3.0.0 has breaking changes; pin to stay stable |
| `ollama` native SDK | `OpenAI(base_url="http://localhost:11434/v1")` for Ollama | The native SDK's `format=` constrained decoding is more reliable than the OpenAI-compat `response_format` layer for local models |
| Inline `_parse_with_retry` | `instructor` library | `instructor` adds a hard dep for ~20 lines of retry logic; not worth it |

---

## Sources

- [openai PyPI](https://pypi.org/project/openai/) — version 2.54.0 (Aug 2026), Python >=3.10 for 2.x (LOW, websearch)
- [OpenAI structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) — parse() method, json_schema response_format (LOW, webfetch)
- [google-genai PyPI](https://pypi.org/project/google-genai/) — version 2.17.0 (Aug 2026), Python >=3.10 (LOW, webfetch)
- [googleapis/python-genai GitHub](https://github.com/googleapis/python-genai) — response_json_schema param, pin <3.0 warning (LOW, webfetch)
- [google-generativeai deprecated](https://github.com/google-gemini/deprecated-generative-ai-python) — deprecated Nov 2025 (LOW, websearch)
- [ollama PyPI](https://pypi.org/project/ollama/) — version 0.6.2 (Apr 2026), Python >=3.8 (LOW, webfetch)
- [Ollama structured outputs docs](https://docs.ollama.com/capabilities/structured-outputs) — format= parameter, JSON schema, Pydantic, temperature=0 (LOW, webfetch)
- [LM Studio OpenAI compat structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output) — json_schema mode confirmed (LOW, websearch)
- [vLLM structured outputs](https://docs.vllm.ai/en/v0.8.2/features/structured_outputs.html) — guided_json via OpenAI-compat (LOW, websearch)
- [Gemini structured output docs](https://ai.google.dev/gemini-api/docs/structured-output) — response_json_schema, Pydantic support (LOW, webfetch)
- Existing codebase: `python/fdars/advisor.py` — Anthropic adapter patterns, `_require_anthropic()` guard model

---

*Stack research for: fdars v3.0 — provider-agnostic LLM advisor backends*
*Researched: 2026-08-12*
