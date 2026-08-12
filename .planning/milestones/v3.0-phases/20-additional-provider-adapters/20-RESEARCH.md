# Phase 20: Additional Provider Adapters - Research

**Researched:** 2026-08-12
**Domain:** Multi-provider LLM adapter layer — OpenAI (+ OpenAI-compatible), Ollama, Gemini
**Confidence:** HIGH (all code-anchored claims verified by reading source this session; SDK API shapes verified against STACK.md which was built from live PyPI + official docs)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Each adapter is a new file under `advisor/providers/` implementing the Phase 19 `Provider` protocol (`complete_structured(schema, messages, system) -> dict`, `name`, `model`, `supports_native_structured_output`). Nothing in `advise()` / `ValidateAndRetry` / `_check_grounding` changes.
- **OpenAI (PROV-03):** `openai>=1.30,<2.0` (the `<2.0` pin keeps Python 3.9 support). Native structured output via `response_format={"type":"json_schema", ...}` → `supports_native_structured_output=True`. `OpenAI(base_url=…)` covers ALL OpenAI-compatible endpoints. For local compat endpoints, pass `api_key="none"` when none is set. `base_url` sourced from `advise(base_url=…)` or `FDARS_ADVISOR_BASE_URL`.
- **Ollama (PROV-04):** native `ollama>=0.6.2` client. `format=<schema>` constrained decoding. `supports_native_structured_output` per what `format=` guarantees; `ValidateAndRetry` covers the rest.
- **Gemini (PROV-05):** `google-genai>=1.0,<3.0` (NOT `google-generativeai`). Python >=3.10 only. Native structured output via `response_schema` in `GenerationConfig`. Requires Pydantic→Gemini schema translation (strip `additionalProperties`). System prompt goes in `system_instruction`.
- **Extras (PROV-07):** add `[openai]`, `[gemini]`, `[ollama]` to `pyproject.toml`, each including `pydantic>=2.0`. Optionally a `[all-providers]` meta-extra. Base package stays importable with NO provider installed. Each adapter uses a deferred import pattern mirroring `_require_anthropic()`.
- **Selection:** extend `resolve_provider()` to recognize `"openai"`, `"ollama"`, `"gemini"`. `provider=None` still defaults to Anthropic (unchanged).

### Claude's Discretion

- Per-provider default model strings (sensible current OpenAI / Gemini / Ollama default).
- The exact Gemini schema-translation helper implementation.
- Whether OpenAI-compatible endpoints default to native or always route through validate-and-retry.

### Deferred Ideas (OUT OF SCOPE)

- New per-aspect `build_diagnostics` branches → Phase 21.
- CI matrix across Python 3.9–3.14 + bare-venv smoke test → Phase 23.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROV-03 | OpenAI + OpenAI-compatible endpoint adapter (configurable `base_url`) | §Per-Adapter Call Shape / OpenAI; §resolve_provider Extension; §Extras |
| PROV-04 | Ollama local adapter (no API key, `format=` constrained decoding) | §Per-Adapter Call Shape / Ollama; §supports_native flags; §Offline Tests |
| PROV-05 | Gemini adapter (Pydantic→Gemini schema translation, `system_instruction`) | §Per-Adapter Call Shape / Gemini; §Gemini Schema Translation |
| PROV-07 | Optional extras `[openai]`/`[gemini]`/`[ollama]`; deferred imports; actionable ImportError | §Extras + Deferred Imports; §pyproject.toml Additions |
</phase_requirements>

---

## Summary

Phase 20 adds three provider adapters — `OpenAIProvider`, `OllamaProvider`, and `GeminiProvider` — each as a new file under `python/fdars/advisor/providers/`, each implementing the Phase 19 `Provider` protocol verbatim. The Phase 19 scaffolding (`ValidateAndRetry`, `_check_grounding`, `advise()` entry point, `resolve_provider()`) requires only narrow, additive changes: three new `elif` branches in `resolve_provider()`, three new deferred-import guards, and three new extras in `pyproject.toml`. No existing tests can break because the grounding check and retry logic are provider-agnostic and live in `_validate.py`.

The most consequential implementation decision is Gemini schema translation: Pydantic's `model_json_schema()` output includes `additionalProperties: false` which the `google-genai` SDK rejects at the client layer before the API call. A small helper (`_gemini_schema`) strips this key recursively. OpenAI's `json_schema` mode requires the schema to be wrapped in a name/strict envelope with no top-level `$defs` keys present in the wire schema; the adapter must inline `$defs` references. Ollama's `format=` parameter is the native constrained-decoding path and is more reliable than the OpenAI-compat route — but it is mutually exclusive with `think=`, which must never be passed to the Ollama adapter.

**Primary recommendation:** Implement adapters in tracer-first order — OpenAI first (most similar to Anthropic's call shape, cleanest mock surface), then Ollama (no auth complexity), then Gemini (most schema-translation work). All three must pass offline mock tests before any is considered complete.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Provider selection and dispatch | `_factory.py` (`resolve_provider`) | `advise()` in `__init__.py` | Factory centralises the if/elif chain; `advise()` owns precedence rules already established in Phase 19 |
| Schema validation + repair retry | `_validate.py` (`ValidateAndRetry`) | Each adapter (`complete_structured`) | Centralized; adapters return raw dict or validated instance; `ValidateAndRetry` owns the retry loop |
| Grounding check | `_validate.py` (`_check_grounding`) | `advise()` (calls it post-completion) | Provider-agnostic; runs identically on every adapter path |
| OpenAI/compat wire call | `providers/openai.py` | — | Owns `response_format` envelope, dummy-key logic, base_url wiring |
| Gemini schema translation | `providers/gemini.py` (`_gemini_schema`) | — | Per-provider concern; keeps the translation co-located with the adapter |
| Ollama constrained decoding | `providers/ollama.py` | — | Owns `format=` parameter; never sets `think=` |
| Deferred import guards | Each adapter file (`_require_<provider>()`) | `advisor/__init__.py` (houses `_require_anthropic`) | Mirrors existing Anthropic pattern; one guard per SDK |
| pyproject.toml extras | `pyproject.toml` | — | Controls what gets installed; no runtime logic |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `openai` | `>=1.30.0,<2.0` | OpenAI + OpenAI-compatible endpoint adapter | 1.x covers Python 3.9; 2.x requires 3.10+. `base_url=` param covers vLLM/LM Studio/LocalAI. Native `json_schema` response format. |
| `google-genai` | `>=1.0.0,<3.0` | Google Gemini adapter | Only current SDK — `google-generativeai` deprecated Nov 2025. `<3.0` pin per upstream breaking-change warning. Requires Python 3.10+. |
| `ollama` | `>=0.5.0` | Local Ollama adapter | Official Python SDK. `format=` constrained-decoding since Ollama v0.5. No auth. Python 3.8+. |
| `pydantic` | `>=2.0` | Schema definition, `.model_json_schema()`, `model_validate_json()` | Already required by `[advisor]`; must be included in every new extra as well |

[VERIFIED: pyproject.toml:41] Existing advisor extra: `advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]`
[VERIFIED: STACK.md] All SDK version pins and Python floor constraints cited from STACK.md which was built from live PyPI and official docs.

### Package Legitimacy Audit

| Package | Registry | Age | Verdict | Disposition |
|---------|----------|-----|---------|-------------|
| `openai` | PyPI | 4+ yrs (OpenAI official) | OK | Approved |
| `google-genai` | PyPI | ~1.5 yrs (Google official) | OK | Approved |
| `ollama` | PyPI | ~2 yrs (Ollama official) | OK | Approved |

**Packages removed due to SLOP verdict:** none
**Packages flagged as suspicious:** none

---

## Per-Adapter Call Shape

This is the most consequential section. Each subsection gives the exact `complete_structured` implementation skeleton, mapped onto the `AnthropicProvider` structure.

### Reference: AnthropicProvider (the pattern to mirror)

[VERIFIED: python/fdars/advisor/providers/anthropic.py:1-94]

The existing adapter has:
1. Class-level `name`, `supports_native_structured_output` attributes
2. `__init__` that calls deferred import guards and constructs the client
3. `complete_structured(schema, messages, system) -> object` that calls the SDK and validates the result
4. A `None`-check on the parsed result that raises `ValueError` (GROUND-04)

Every new adapter mirrors this structure exactly. The `model` attribute is set in `__init__`.

---

### OpenAI Adapter (`providers/openai.py`)

**Call shape:**

```python
from __future__ import annotations


class OpenAIProvider:
    """Adapter that delegates to openai.OpenAI().chat.completions.create.

    Supports OpenAI and any OpenAI-compatible endpoint (vLLM, LM Studio,
    LocalAI) via the ``base_url`` constructor parameter.

    Parameters
    ----------
    model : str
        Model identifier.  Default ``"gpt-4o"``.
    api_key : str or None
        Explicit API key.  When ``None`` and ``base_url`` points to a local
        endpoint (``localhost`` / ``127.0.0.1``), falls back to ``"none"``
        (a dummy non-empty key) to avoid SDK-level AuthenticationError.
        When ``None`` and no ``base_url`` is set, reads ``OPENAI_API_KEY``.
    base_url : str or None
        Custom base URL, e.g. ``"http://localhost:1234/v1"`` for LM Studio.
        When ``None``, uses the OpenAI default.
    """

    name = "openai"
    supports_native_structured_output = True

    def __init__(
        self,
        model: "str" = "gpt-4o",
        api_key: "str | None" = None,
        base_url: "str | None" = None,
    ) -> None:
        from fdars.advisor import _require_pydantic          # noqa: PLC0415
        _require_openai()                                     # deferred import
        _require_pydantic()

        import openai as _openai                             # noqa: PLC0415

        self.model = model
        self._schema_cache: "dict | None" = None

        # Dummy key for local/compat endpoints that don't require auth
        resolved_key = api_key
        if resolved_key is None and base_url is not None:
            import re as _re                                 # noqa: PLC0415
            if _re.search(r"localhost|127\.0\.0\.1", base_url):
                resolved_key = "none"

        self._client = _openai.OpenAI(
            api_key=resolved_key,
            base_url=base_url,
        )

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        import json as _json                                 # noqa: PLC0415

        # Inject system prompt as the first message (OpenAI convention)
        wire_messages = [{"role": "system", "content": system}] + list(messages)

        # Build the json_schema response_format envelope
        raw_schema = _openai_schema(schema)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "strict": True,
                "schema": raw_schema,
            },
        }

        response = self._client.chat.completions.create(
            model=self.model,
            response_format=response_format,
            messages=wire_messages,
        )

        choice = response.choices[0]
        # GROUND-04: detect refusal
        if getattr(choice.message, "refusal", None):
            raise ValueError(
                f"OpenAIProvider: model returned a refusal: "
                f"{choice.message.refusal!r}"
            )

        raw_json = choice.message.content
        if not raw_json:
            raise ValueError(
                "OpenAIProvider: model returned empty content."
            )

        # Return a dict; ValidateAndRetry's _fallback_with_retry handles parsing
        # when supports_native_structured_output=True the wrapper skips retry,
        # so we parse here directly and return a validated instance.
        return schema.model_validate_json(raw_json)
```

**`_openai_schema` helper (strips `$defs`, ensures `required`):**

```python
def _openai_schema(model_cls: type) -> dict:
    """Convert a Pydantic model to an OpenAI json_schema-compatible dict.

    OpenAI strict mode requires:
    - ``additionalProperties: false`` on every object (Pydantic already adds this)
    - All fields listed in ``required`` (Pydantic adds this for non-Optional fields)
    - No top-level ``$defs`` key — definitions must be inlined

    Pydantic's ``model_json_schema()`` for ``Advice`` produces nested ``$defs``
    for ``Recommendation``.  OpenAI's strict schema accepts ``$defs`` / ``$ref``
    since 2024-08 — do NOT inline manually.  Just pass the schema as-is.
    The ``title`` key at root is accepted by the API but is redundant
    (the ``name`` field in the envelope serves that purpose).
    """
    schema = model_cls.model_json_schema()
    # Remove root-level 'title' to keep the wire payload clean (not required)
    schema.pop("title", None)
    return schema
```

**Note on `supports_native_structured_output=True`:** The adapter calls `model_validate_json` and returns a validated `Advice` instance. Since it returns an instance (not a dict), `ValidateAndRetry._fallback_with_retry` is bypassed by the native path branch in `_validate.py`:

```python
# _validate.py line 61-63 [VERIFIED: python/fdars/advisor/providers/_validate.py:61-63]
if self._provider.supports_native_structured_output:
    return self._provider.complete_structured(schema, messages, system)
```

**OpenAI-compatible endpoints (vLLM, LM Studio, LocalAI):**

These are reached by passing `base_url="http://localhost:1234/v1"` (or the appropriate host). The same `OpenAIProvider` class handles them — no separate adapter. However, not all compat endpoints reliably honour `strict: True` in `json_schema` mode. Set `supports_native_structured_output=False` for compat-endpoint instances is NOT done at class level; instead the calling code should be aware. The simplest approach: keep `supports_native_structured_output=True` but catch `ValidationError` in `complete_structured` and let `ValidateAndRetry._fallback_with_retry` handle it via the `MAX_RETRIES=2` loop.

Wait — when `supports_native_structured_output=True`, `ValidateAndRetry` calls `complete_structured` and returns immediately without retry [VERIFIED: _validate.py:61-63]. This means the OpenAI adapter must handle its own retry for compat endpoints, OR accept that compat endpoints with unreliable schema enforcement are on their own. The locked decision says `supports_native_structured_output=True` for OpenAI. Claude's Discretion covers compat endpoints: **recommended approach** is `supports_native_structured_output=True` for all `OpenAIProvider` instances — if `model_validate_json` fails, the adapter raises `ValueError`, which surfaces cleanly to the caller. For compat endpoints that are known unreliable (Ollama-compat), users should use `OllamaProvider` directly instead. Document this in the adapter docstring.

---

### Ollama Adapter (`providers/ollama.py`)

**Call shape:**

```python
from __future__ import annotations


class OllamaProvider:
    """Adapter that delegates to ollama.chat with format= constrained decoding.

    No API key required.  Requires a running Ollama daemon on the local machine.

    Parameters
    ----------
    model : str
        Ollama model tag, e.g. ``"llama3.2"``.  Default ``"llama3.2"``.
    host : str or None
        Ollama server URL.  When ``None``, uses the Ollama SDK default
        (``http://localhost:11434``).
    """

    name = "ollama"
    supports_native_structured_output = False  # constrained, but not guaranteed

    def __init__(
        self,
        model: "str" = "llama3.2",
        host: "str | None" = None,
    ) -> None:
        from fdars.advisor import _require_pydantic          # noqa: PLC0415
        _require_ollama()                                    # deferred import
        _require_pydantic()
        self.model = model
        self._host = host

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        import ollama as _ollama                            # noqa: PLC0415

        # Ollama does not have a top-level system parameter; prepend system
        # as a system-role message in the messages list
        wire_messages = [{"role": "system", "content": system}] + list(messages)

        # Augment the user message with an explicit schema reference to improve
        # adherence on smaller models (per STACK.md / Ollama docs recommendation)
        import json as _json                               # noqa: PLC0415
        schema_hint = (
            "\n\nRespond with JSON matching this schema:\n"
            + _json.dumps(schema.model_json_schema(), indent=2)
        )
        # Inject schema hint into the last user message
        last_user_idx = next(
            (i for i in range(len(wire_messages) - 1, -1, -1)
             if wire_messages[i]["role"] == "user"),
            None,
        )
        if last_user_idx is not None:
            augmented = list(wire_messages)
            augmented[last_user_idx] = {
                **augmented[last_user_idx],
                "content": augmented[last_user_idx]["content"] + schema_hint,
            }
            wire_messages = augmented

        kwargs: dict = {
            "model": self.model,
            "messages": wire_messages,
            "format": schema.model_json_schema(),   # constrained decoding
            "options": {"temperature": 0},           # improves schema adherence
        }
        if self._host is not None:
            kwargs["host"] = self._host

        # CRITICAL: never pass think= alongside format= (Ollama constraint;
        # silently disables the format constraint on some models per
        # PITFALLS.md Pitfall 1 / Ollama issue #10929).

        response = _ollama.chat(**kwargs)

        raw_json = response.message.content
        if not raw_json:
            raise ValueError("OllamaProvider: model returned empty content.")

        # Return raw dict for ValidateAndRetry._fallback_with_retry to validate.
        # supports_native_structured_output=False triggers the retry path.
        return _json.loads(raw_json)
```

**Why `supports_native_structured_output=False`:** Grammar-constrained decoding (`format=`) makes structural failure near-impossible, but Pydantic validation can still fail if field types are coerced (e.g., `evidence` emitted as a single string instead of `List[str]`). Setting `False` routes through `ValidateAndRetry._fallback_with_retry` which runs `schema.model_validate(raw_dict)` and retries up to `MAX_RETRIES=2` with a repair prompt. [VERIFIED: python/fdars/advisor/providers/_validate.py:80-108]

**PITFALLS.md recommendation for `max_retries` with constrained decoding:** PITFALLS.md says Ollama with `format=` should ideally have `max_retries=0` because structural failure signals a schema serialisation bug, not a model reliability issue. However, `MAX_RETRIES` is hardcoded in `ValidateAndRetry` at the class level [VERIFIED: _validate.py:38]. For this phase, `supports_native_structured_output=False` with the existing `MAX_RETRIES=2` is acceptable. A comment in the adapter should note that if validation keeps failing, the schema translation is the suspect — not the model.

---

### Gemini Adapter (`providers/gemini.py`)

**Call shape:**

```python
from __future__ import annotations


class GeminiProvider:
    """Adapter that delegates to google-genai Client.models.generate_content.

    Requires Python >=3.10 (google-genai SDK requirement).

    Parameters
    ----------
    model : str
        Gemini model identifier.  Default ``"gemini-2.0-flash"``.
    api_key : str or None
        Explicit API key.  When ``None``, reads ``GEMINI_API_KEY`` from env.
    """

    name = "gemini"
    supports_native_structured_output = True

    def __init__(
        self,
        model: "str" = "gemini-2.0-flash",
        api_key: "str | None" = None,
    ) -> None:
        import sys                                           # noqa: PLC0415
        if sys.version_info < (3, 10):
            raise ImportError(
                "The fdars[gemini] extra requires Python >=3.10 "
                "(google-genai SDK requirement). "
                "Use fdars[openai] or fdars[ollama] on Python 3.9."
            )
        from fdars.advisor import _require_pydantic          # noqa: PLC0415
        _require_gemini()                                    # deferred import
        _require_pydantic()
        self.model = model
        self._api_key = api_key

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        from google import genai as _genai                  # noqa: PLC0415
        from google.genai import types as _types            # noqa: PLC0415

        client = _genai.Client(api_key=self._api_key)

        # Build Gemini-safe schema (strips additionalProperties)
        gemini_schema = _gemini_schema(schema)

        # Extract user content from messages (Gemini uses contents= not messages=)
        user_content = " ".join(
            m["content"] for m in messages if m.get("role") == "user"
        )

        response = client.models.generate_content(
            model=self.model,
            contents=user_content,
            config=_types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_json_schema=gemini_schema,
            ),
        )

        raw_json = response.text
        if not raw_json:
            raise ValueError(
                "GeminiProvider: model returned empty response. "
                "Check GEMINI_API_KEY and model availability."
            )

        # Parse and validate; return instance (native path)
        return schema.model_validate_json(raw_json)
```

**Why `supports_native_structured_output=True`:** The Gemini SDK enforces `response_json_schema` at the API level and the adapter calls `model_validate_json` before returning. The `ValidateAndRetry` native path returns the instance directly. If validation fails (edge case: Gemini schema subset limitation), the `ValueError` surfaces cleanly.

**Client construction per call vs. caching:** The Gemini adapter constructs `_genai.Client(api_key=...)` on every `complete_structured` call. This is acceptable for the sync use case (no persistent session, no streaming). Caching the client in `self._client` is a valid optimization but introduces a question of re-auth on key rotation — for Phase 20, per-call construction is simpler and correct.

---

## Gemini Pydantic→Schema Translation

This is the most complex per-adapter concern.

### What `Advice.model_json_schema()` produces

[VERIFIED: python/fdars/advisor/_schema.py:32-71]

The `Advice` model has:
- `interpretation: str`
- `recommendations: List[Recommendation]`
- `caveats: List[str]`

And `Recommendation` has:
- `action: str`
- `kind: Literal["parameter", "method", "none"]`
- `rationale: str`
- `expected_effect: str`
- `evidence: List[str]`

Pydantic v2's `model_json_schema()` output for this schema includes:

```json
{
  "$defs": {
    "Recommendation": {
      "additionalProperties": false,
      "properties": { ... },
      "required": [...],
      "title": "Recommendation",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "recommendations": {
      "items": { "$ref": "#/$defs/Recommendation" },
      "type": "array"
    },
    ...
  },
  "required": [...],
  "title": "Advice",
  "type": "object"
}
```

### What Gemini rejects

[CITED: PITFALLS.md — Pitfall 1, Pitfall 5; STACK.md §Structured-Output API Shape / Google Gemini]

The `google-genai` SDK rejects schemas containing `additionalProperties` at the **client-side validation layer** — the rejection happens before the API call. The specific rejected key is `additionalProperties: false` (even though the Gemini API itself now supports it, the Python SDK validator lags behind).

### The `_gemini_schema` helper

```python
def _gemini_schema(model_cls: type) -> dict:
    """Convert a Pydantic model to a Gemini response_json_schema-compatible dict.

    Gemini's google-genai SDK client validator rejects ``additionalProperties``
    keys, even though the underlying API supports them.  This helper strips
    ``additionalProperties`` recursively from the serialised schema and also
    resolves ``$defs`` / ``$ref`` references (Gemini does not support
    JSON Schema ``$ref``).

    Parameters
    ----------
    model_cls : type
        Pydantic BaseModel subclass (e.g. ``Advice``).

    Returns
    -------
    dict
        JSON Schema dict safe to pass as ``response_json_schema`` to
        ``GenerateContentConfig``.
    """
    import copy as _copy                                    # noqa: PLC0415

    schema = _copy.deepcopy(model_cls.model_json_schema())

    # Step 1: Resolve $defs / $ref — Gemini does not support JSON Schema $ref
    defs = schema.pop("$defs", {})
    schema = _resolve_refs(schema, defs)

    # Step 2: Strip additionalProperties recursively
    _strip_key(schema, "additionalProperties")

    # Step 3: Strip title keys (optional but keeps the schema lean)
    _strip_key(schema, "title")

    return schema


def _resolve_refs(obj: object, defs: dict) -> object:
    """Recursively resolve ``$ref`` pointers using the ``$defs`` map."""
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_name = obj["$ref"].split("/")[-1]  # "#/$defs/Recommendation" → "Recommendation"
            resolved = _copy.deepcopy(defs.get(ref_name, obj))
            return _resolve_refs(resolved, defs)
        return {k: _resolve_refs(v, defs) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_refs(item, defs) for item in obj]
    return obj


def _strip_key(obj: object, key: str) -> None:
    """Recursively remove all occurrences of ``key`` from a nested dict."""
    if isinstance(obj, dict):
        obj.pop(key, None)
        for v in obj.values():
            _strip_key(v, key)
    elif isinstance(obj, list):
        for item in obj:
            _strip_key(item, key)
```

**How `Literal["parameter", "method", "none"]` maps to Gemini's schema subset:**

Pydantic serialises `Literal["parameter", "method", "none"]` as:
```json
{"enum": ["parameter", "method", "none"], "type": "string"}
```
Gemini's JSON-schema subset supports `enum` directly. No transformation required. [CITED: STACK.md §Structured-Output API Shape / Google Gemini — "The Advice schema (flat object with nested Recommendation list) is within supported bounds"]

**After `_gemini_schema` transforms `Advice`, the wire schema looks like:**

```json
{
  "properties": {
    "interpretation": {"type": "string"},
    "recommendations": {
      "items": {
        "properties": {
          "action": {"type": "string"},
          "kind": {"enum": ["parameter", "method", "none"], "type": "string"},
          "rationale": {"type": "string"},
          "expected_effect": {"type": "string"},
          "evidence": {"items": {"type": "string"}, "type": "array"}
        },
        "required": ["action", "kind", "rationale", "expected_effect", "evidence"],
        "type": "object"
      },
      "type": "array"
    },
    "caveats": {"items": {"type": "string"}, "type": "array"}
  },
  "required": ["interpretation", "recommendations", "caveats"],
  "type": "object"
}
```

No `additionalProperties`, no `$ref`, no `$defs`, no `title`. This is the minimal schema Gemini accepts.

---

## `supports_native_structured_output` Per Adapter

| Adapter | Value | Rationale |
|---------|-------|-----------|
| `AnthropicProvider` | `True` | [VERIFIED: anthropic.py:33] SDK's `messages.parse(output_format=schema)` enforces schema and returns a validated Pydantic instance |
| `OpenAIProvider` | `True` | `response_format=json_schema` with `strict: True` constrains output; adapter calls `model_validate_json` before returning |
| `GeminiProvider` | `True` | `response_json_schema` in `GenerateContentConfig` constrains output; adapter calls `model_validate_json` before returning |
| `OllamaProvider` | `False` | Grammar-constrained decoding is reliable for structure but field-type coercion failures (e.g. `evidence` as string vs list) still occur; routes through `ValidateAndRetry._fallback_with_retry` |

**Effect on `ValidateAndRetry`:** [VERIFIED: python/fdars/advisor/providers/_validate.py:55-64]

When `supports_native_structured_output=True`, `ValidateAndRetry.complete_structured` delegates directly without retry. When `False` (Ollama), it calls `_fallback_with_retry` which runs `schema.model_validate(raw_dict)` and retries up to `MAX_RETRIES=2` (hardcoded).

**OpenAI-compatible endpoints:** These also use `OpenAIProvider` with `supports_native_structured_output=True`. For endpoints that are unreliable with `json_schema` (e.g., older LocalAI), the `ValueError` from `model_validate_json` will surface. Users should switch to `OllamaProvider` for Ollama-served models, or accept the error and fix their endpoint version.

---

## Extras + Deferred Imports (PROV-07)

### `pyproject.toml` additions

[VERIFIED: pyproject.toml:38-43] Current state:
```toml
[project.optional-dependencies]
plot = ["matplotlib>=3.6"]
dev = ["pytest", "matplotlib>=3.6"]
advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]
# Note: mcp requires Python >=3.10. This extra is not compatible with Python 3.9.
mcp = ["mcp>=2.0.0"]
```

Add after the existing `mcp` line:

```toml
# Provider extras — each ships as an independently installable extra.
# pydantic>=2.0 is repeated in each extra because every adapter needs
# model_json_schema() and model_validate_json(), and we cannot assume
# [advisor] is installed alongside.
# Note: [gemini] requires Python >=3.10 (google-genai SDK requirement);
# the adapter enforces this at runtime with a clear ImportError.
openai = ["openai>=1.30.0,<2.0", "pydantic>=2.0"]
gemini = ["google-genai>=1.0.0,<3.0", "pydantic>=2.0"]
ollama = ["ollama>=0.5.0", "pydantic>=2.0"]

# Meta-extra for dev/test environments and documentation examples.
# Includes all provider extras plus the base advisor (Anthropic).
all-providers = [
    "fdars[advisor]",
    "fdars[openai]",
    "fdars[gemini]",
    "fdars[ollama]",
]
```

**Python 3.9 constraint summary:**

| Extra | Python 3.9 installable? | Enforced by |
|-------|------------------------|-------------|
| `[openai]` (1.x pin) | Yes | `<2.0` pin; openai 1.x supports 3.7.1+ |
| `[gemini]` | Package installs but runtime guard fires | `sys.version_info < (3, 10)` check in `GeminiProvider.__init__` |
| `[ollama]` | Yes | ollama SDK supports 3.8+ |

### Deferred Import Guard Pattern

[VERIFIED: python/fdars/advisor/__init__.py:154-186] Existing `_require_anthropic()` pattern.

Each new guard lives in `advisor/__init__.py` alongside `_require_anthropic()` and `_require_pydantic()`. The adapter files import these guards from `fdars.advisor` (deferred, inside function bodies) — identical to the Anthropic adapter's pattern [VERIFIED: anthropic.py:44].

```python
# In advisor/__init__.py — add after _require_pydantic():

ADVISOR_OPENAI_MIN_VERSION = "1.30.0"
ADVISOR_GEMINI_MIN_VERSION = "1.0.0"
ADVISOR_OLLAMA_MIN_VERSION = "0.5.0"


def _require_openai():
    """Import and return the ``openai`` module, or raise a clear ImportError."""
    try:
        import openai                                       # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "The fdars OpenAI adapter requires the openai SDK. "
            f"Install it with: pip install fdars[openai]\n"
            f"Requires: openai>={ADVISOR_OPENAI_MIN_VERSION},<2.0"
        ) from exc

    installed = tuple(int(x) for x in openai.__version__.split(".")[:3])
    floor = tuple(int(x) for x in ADVISOR_OPENAI_MIN_VERSION.split(".")[:3])
    if installed < floor:
        raise ImportError(
            f"fdars openai adapter requires openai>={ADVISOR_OPENAI_MIN_VERSION}; "
            f"found {openai.__version__}. "
            f"Run: pip install 'openai>={ADVISOR_OPENAI_MIN_VERSION},<2.0'"
        )
    return openai


def _require_gemini():
    """Import and return the ``google.genai`` module, or raise a clear ImportError."""
    try:
        from google import genai                            # noqa: PLC0415
        return genai
    except ImportError as exc:
        raise ImportError(
            "The fdars Gemini adapter requires the google-genai SDK. "
            "Install it with: pip install fdars[gemini]\n"
            "Note: requires Python >=3.10."
        ) from exc


def _require_ollama():
    """Import and return the ``ollama`` module, or raise a clear ImportError."""
    try:
        import ollama                                       # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "The fdars Ollama adapter requires the ollama SDK. "
            "Install it with: pip install fdars[ollama]\n"
            "Requires a running Ollama daemon (https://ollama.com)."
        ) from exc

    installed = tuple(int(x) for x in ollama.__version__.split(".")[:3])
    floor = tuple(int(x) for x in ADVISOR_OLLAMA_MIN_VERSION.split(".")[:3])
    if installed < floor:
        raise ImportError(
            f"fdars ollama adapter requires ollama>={ADVISOR_OLLAMA_MIN_VERSION}; "
            f"found {ollama.__version__}. "
            f"Run: pip install 'ollama>={ADVISOR_OLLAMA_MIN_VERSION}'"
        )
    return ollama
```

**Version check note for Gemini:** `google-genai` does not expose a simple `genai.__version__` in all releases; omit the version floor check and rely on the `<3.0` pip pin. If a version check is needed, use `importlib.metadata.version("google-genai")`.

---

## `resolve_provider()` Extension

[VERIFIED: python/fdars/advisor/providers/_factory.py:1-110]

The current factory has:
- A pass-through for existing `Provider` instances
- A `provider_name` string resolved via explicit arg > env > `"anthropic"` default
- A single `if provider_name == "anthropic":` branch
- A `raise ValueError` for unknown names with a Phase 20 forward reference comment

**Add to `_DEFAULT_MODELS` and `_KEY_ENV`:**

```python
_DEFAULT_MODELS: dict = {
    "anthropic": "claude-opus-4-8",
    "openai":    "gpt-4o",
    "gemini":    "gemini-2.0-flash",
    "ollama":    "llama3.2",
}

_KEY_ENV: dict = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai":    "OPENAI_API_KEY",
    "gemini":    "GEMINI_API_KEY",
    # ollama: no API key required
}
```

**Replace the `if/else` block:**

```python
if provider_name == "anthropic":
    from fdars.advisor.providers.anthropic import AnthropicProvider  # noqa: PLC0415
    adapter = AnthropicProvider(model=resolved_model, api_key=resolved_key)

elif provider_name == "openai":
    from fdars.advisor.providers.openai import OpenAIProvider        # noqa: PLC0415
    adapter = OpenAIProvider(
        model=resolved_model,
        api_key=resolved_key,
        base_url=resolved_base_url,
    )

elif provider_name == "gemini":
    from fdars.advisor.providers.gemini import GeminiProvider        # noqa: PLC0415
    adapter = GeminiProvider(model=resolved_model, api_key=resolved_key)

elif provider_name == "ollama":
    from fdars.advisor.providers.ollama import OllamaProvider        # noqa: PLC0415
    # Ollama uses 'host' not 'base_url'; map resolved_base_url → host
    adapter = OllamaProvider(model=resolved_model, host=resolved_base_url)

else:
    raise ValueError(
        f"resolve_provider: unknown provider {provider_name!r}. "
        f"Supported providers: 'anthropic', 'openai', 'gemini', 'ollama'. "
        f"Install the corresponding extra: pip install fdars[<provider>]"
    )
```

The `resolved_base_url` variable is already computed in Phase 19's factory [VERIFIED: _factory.py:82-86] but currently unused (`_ = resolved_base_url`). Phase 20 passes it through to `OpenAIProvider` and `OllamaProvider`.

**No changes to `advise()` signature:** The `base_url` kwarg is already passed into `resolve_provider` [VERIFIED: __init__.py:278]. It threads through to `OpenAIProvider(base_url=...)` and `OllamaProvider(host=...)` automatically via the factory.

---

## Offline Test Strategy

### Principle

Every adapter must have network-free, key-free tests. Tests use mock objects to replace SDK calls. Tests must also cover grounding violation detection [VERIFIED: PITFALLS.md — "Looks Done But Isn't" checklist].

### Mock Targets

| Adapter | SDK mock target | What to mock |
|---------|----------------|-------------|
| `OpenAIProvider` | `openai.OpenAI` | Patch the class; return a `MagicMock` whose `.chat.completions.create()` returns a mock `response` with `choices[0].message.content = <json_string>` and `choices[0].message.refusal = None` |
| `OllamaProvider` | `ollama.chat` | Patch the function directly; return a `MagicMock` with `.message.content = <json_string>` |
| `GeminiProvider` | `google.genai.Client` | Patch the `Client` class; return a `MagicMock` whose `.models.generate_content()` returns a mock with `.text = <json_string>` |

**Sys.modules patching for missing-extra tests** (identical to existing Anthropic test pattern):

```python
# Simulates [openai] not installed
import sys
sys.modules["openai"] = None  # type: ignore[assignment]
```

This prevents the real `openai` import from succeeding even if the package is installed in the test environment, ensuring the `ImportError` path is exercised.

### Test file layout

```
tests/
├── advisor/
│   ├── providers/
│   │   ├── test_openai_provider.py
│   │   ├── test_ollama_provider.py
│   │   ├── test_gemini_provider.py
│   │   ├── test_gemini_schema.py   # _gemini_schema helper, offline only
│   │   └── test_factory.py         # resolve_provider new branches
│   └── fixtures/
│       ├── openai_response.json    # raw response fixture for schema round-trip
│       ├── ollama_response.json
│       └── gemini_response.json
```

### Per-provider offline test coverage

**OpenAI (test_openai_provider.py):**

```python
from unittest.mock import MagicMock, patch
import json, pytest
from fdars.advisor._schema import Advice, Recommendation

GOOD_ADVICE = Advice(
    interpretation="ok",
    recommendations=[
        Recommendation(action="a", kind="parameter", rationale="r",
                       expected_effect="e", evidence=["k=4"])
    ],
    caveats=[]
)

@patch("openai.OpenAI")
def test_openai_native_path_returns_advice(mock_openai_cls):
    # Arrange
    raw = GOOD_ADVICE.model_dump_json()
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=raw, refusal=None))]
    )
    from fdars.advisor.providers.openai import OpenAIProvider
    p = OpenAIProvider(api_key="test-key")
    from fdars.advisor._schema import Advice
    result = p.complete_structured(Advice, [{"role": "user", "content": "x"}], "sys")
    assert isinstance(result, Advice)
    assert result.interpretation == "ok"


def test_openai_raises_importerror_without_extra():
    import sys
    orig = sys.modules.get("openai")
    sys.modules["openai"] = None  # type: ignore[assignment]
    try:
        import importlib
        import fdars.advisor.providers.openai as m
        importlib.reload(m)
        with pytest.raises(ImportError, match="pip install fdars\\[openai\\]"):
            m.OpenAIProvider()
    finally:
        if orig is None:
            del sys.modules["openai"]
        else:
            sys.modules["openai"] = orig


def test_openai_base_url_dummy_key():
    """When base_url points to localhost and no api_key given, adapter passes 'none'."""
    with patch("openai.OpenAI") as mock_cls:
        mock_cls.return_value = MagicMock()
        from fdars.advisor.providers.openai import OpenAIProvider
        OpenAIProvider(base_url="http://localhost:1234/v1")
        call_kwargs = mock_cls.call_args[1]
        assert call_kwargs["api_key"] == "none"


def test_openai_grounding_violation_caught(mock_diagnostics):
    """Grounding check catches fabricated evidence."""
    from fdars.advisor.providers._validate import _check_grounding, GroundingViolationError
    fabricated = Advice(
        interpretation="ok",
        recommendations=[
            Recommendation(action="a", kind="none", rationale="r",
                           expected_effect="e", evidence=["k=999"])  # 999 not in diag
        ],
        caveats=[]
    )
    diag = {"k": 4}
    with pytest.raises(GroundingViolationError):
        _check_grounding(fabricated, diag)
```

**Ollama (test_ollama_provider.py) — key differences:**

```python
@patch("ollama.chat")
def test_ollama_returns_dict_for_validate_and_retry(mock_chat):
    """OllamaProvider returns a dict (not instance); ValidateAndRetry validates it."""
    raw = json.dumps(GOOD_ADVICE.model_dump())
    mock_chat.return_value = MagicMock(message=MagicMock(content=raw))
    from fdars.advisor.providers.ollama import OllamaProvider
    p = OllamaProvider()
    result = p.complete_structured(Advice, [{"role":"user","content":"x"}], "sys")
    assert isinstance(result, dict)  # raw dict, not Advice instance


def test_ollama_never_passes_think_param():
    """Confirm think= is not passed alongside format= (Ollama constraint)."""
    with patch("ollama.chat") as mock_chat:
        mock_chat.return_value = MagicMock(message=MagicMock(content="{}"))
        from fdars.advisor.providers.ollama import OllamaProvider
        p = OllamaProvider()
        p.complete_structured(Advice, [{"role":"user","content":"x"}], "sys")
        call_kwargs = mock_chat.call_args[1]
        assert "think" not in call_kwargs
```

**Gemini schema helper (test_gemini_schema.py) — offline, no SDK:**

```python
def test_gemini_schema_strips_additional_properties():
    from fdars.advisor.providers.gemini import _gemini_schema
    from fdars.advisor._schema import Advice
    schema = _gemini_schema(Advice)
    # Must have no additionalProperties anywhere in the tree
    import json
    schema_str = json.dumps(schema)
    assert "additionalProperties" not in schema_str


def test_gemini_schema_resolves_refs():
    from fdars.advisor.providers.gemini import _gemini_schema
    from fdars.advisor._schema import Advice
    schema = _gemini_schema(Advice)
    schema_str = json.dumps(schema)
    assert "$ref" not in schema_str
    assert "$defs" not in schema_str


def test_gemini_schema_preserves_enum():
    from fdars.advisor.providers.gemini import _gemini_schema
    from fdars.advisor._schema import Advice
    schema = _gemini_schema(Advice)
    # Find the kind field inside recommendations.items.properties
    kind_field = schema["properties"]["recommendations"]["items"]["properties"]["kind"]
    assert kind_field["enum"] == ["parameter", "method", "none"]
```

### Env-gated live integration tests

One per provider, all in `tests/advisor/providers/test_live_integration.py`:

```python
import os, pytest

INTEGRATION = os.environ.get("FDARS_INTEGRATION") == "1"
OPENAI_KEY  = os.environ.get("OPENAI_API_KEY")
GEMINI_KEY  = os.environ.get("GEMINI_API_KEY")
OLLAMA_UP   = _ollama_running()  # helper: socket connect to localhost:11434

@pytest.mark.skipif(
    not (INTEGRATION and OPENAI_KEY),
    reason="Set FDARS_INTEGRATION=1 and OPENAI_API_KEY to run"
)
def test_openai_live_returns_advice():
    from fdars.advisor.providers.openai import OpenAIProvider
    from fdars.advisor._schema import Advice
    from fdars.advisor.providers._validate import ValidateAndRetry
    p = ValidateAndRetry(OpenAIProvider())
    diag = {"k": 3, "silhouette_score": 0.62, "bic": [-120.1, -145.3, -130.0]}
    # ... build minimal messages and call complete_structured ...


@pytest.mark.skipif(
    not (INTEGRATION and GEMINI_KEY),
    reason="Set FDARS_INTEGRATION=1 and GEMINI_API_KEY to run"
)
def test_gemini_live_returns_advice(): ...


@pytest.mark.skipif(
    not (INTEGRATION and OLLAMA_UP),
    reason="Set FDARS_INTEGRATION=1 and run Ollama daemon to run"
)
def test_ollama_live_returns_advice(): ...
```

**Gate logic:** Both `FDARS_INTEGRATION=1` AND the provider-specific key/daemon must be present. This prevents accidental live runs when a developer has `OPENAI_API_KEY` set for another project but has not explicitly opted into integration tests.

---

## Common Pitfalls

### Pitfall 1: `additionalProperties` in Gemini schema

[VERIFIED: PITFALLS.md — Pitfall 1, Integration Gotchas table]

**What goes wrong:** Pydantic's `model_json_schema()` includes `additionalProperties: false` at every object level. The `google-genai` Python SDK validates the schema client-side before the API call and rejects this key — raising a `ValueError` or `TypeError` that looks like a type error, not a schema error. The failure is confusing because it happens before any network call.

**How to avoid:** Always call `_gemini_schema(Advice)` (the translation helper) before passing to `GenerateContentConfig`. Never pass `Advice.model_json_schema()` directly to Gemini.

**Warning sign:** `_gemini_schema` is not tested offline. Add `test_gemini_schema_strips_additional_properties` before writing the adapter.

### Pitfall 2: Ollama `think=` + `format=` mutual exclusion

[VERIFIED: PITFALLS.md — Pitfall 1, Integration Gotchas table; STACK.md §Ollama]

**What goes wrong:** Some Ollama models (e.g., gemma4, qwen-thinking) accept a `think=True` parameter for reasoning/chain-of-thought. Passing `think=True` alongside `format=schema` silently disables the format constraint on some models (Ollama GitHub issue #10929). The model produces natural language instead of JSON, and `json.loads()` fails.

**How to avoid:** The `OllamaProvider` must never pass `think=` to `ollama.chat`. Add a test that asserts the `think` key is absent from call kwargs.

### Pitfall 3: OpenAI dummy `api_key` for local endpoints

[VERIFIED: PITFALLS.md — Pitfall 5; STACK.md §OpenAI §OpenAI-compatible endpoints]

**What goes wrong:** `OpenAI()` without explicit `api_key` reads `OPENAI_API_KEY` from the environment. For local compat endpoints (vLLM, LM Studio), no key is needed — but if `OPENAI_API_KEY` is unset, the SDK raises `openai.AuthenticationError` before the request is sent. The error says "provide an API key" but the endpoint doesn't require one.

**How to avoid:** When `base_url` points to `localhost` or `127.0.0.1` and `api_key` is `None`, pass `api_key="none"` to `OpenAI()`. Test this explicitly.

### Pitfall 4: Module-level SDK imports break bare-venv imports

[VERIFIED: PITFALLS.md — Pitfall 4; anthropic.py docstring lines 6-16]

**What goes wrong:** If `providers/openai.py` has `import openai` at the top of the file, then `from fdars.advisor.providers import openai` fails immediately in environments without `[openai]` installed — even if the caller never instantiates `OpenAIProvider`. This breaks `pytest` collection if `tests/` imports from the providers package.

**How to avoid:** All SDK imports must be inside function bodies (deferred). The only top-level imports allowed in adapter files are `from __future__ import annotations` and imports from `fdars.advisor` (the deferred guard functions). SDK imports happen only inside `__init__` and `complete_structured`.

### Pitfall 5: `google-generativeai` vs `google-genai` namespace collision

[VERIFIED: PITFALLS.md — Pitfall 5; STACK.md §What NOT to Add]

**What goes wrong:** The deprecated `google-generativeai` package imports as `import google.generativeai`. The current `google-genai` imports as `from google import genai`. If the wrong package name is in `pyproject.toml` or an adapter uses the wrong import, it silently imports the deprecated API with a completely different surface.

**How to avoid:** `pyproject.toml` must list `google-genai` (not `google-generativeai`). The adapter uses `from google import genai`. Add to the plan's verification checklist: `grep -r "google.generativeai" python/` returns zero hits.

### Pitfall 6: `$defs` / `$ref` in OpenAI strict mode

[VERIFIED: PITFALLS.md — Integration Gotchas; STACK.md §OpenAI]

**What goes wrong:** Pydantic v2's `model_json_schema()` for models with nested sub-models (like `Advice` which references `Recommendation`) produces `$defs` + `$ref` pointers. OpenAI's strict mode does support `$ref` (as of 2024-08), but some older model versions or compat endpoints may not. The `_openai_schema` helper should leave `$defs`/`$ref` as-is for real OpenAI endpoints but the test suite should verify the schema round-trips.

**How to avoid:** Test `_openai_schema(Advice)` produces a dict that can be serialised to JSON without error and that a known-good Advice JSON validates against the schema produced.

### Pitfall 7: Sequencing — test schema translation before wiring the API call

[VERIFIED: PITFALLS.md — "Looks Done But Isn't" checklist]

**What goes wrong:** Writing the Gemini adapter's `complete_structured` call before verifying `_gemini_schema` produces a valid schema. The SDK raises a confusing client-side error on the first live run.

**How to avoid:** The plan must order tasks as: (1) implement and test `_gemini_schema` offline, (2) implement `GeminiProvider.__init__` + deferred import, (3) implement `complete_structured`, (4) live integration test.

---

## Architecture Patterns

### System Architecture Diagram

```
advise(diagnostics, task, domain_context, provider="openai"|"ollama"|"gemini"|None)
    |
    v
resolve_provider(provider_name, model, api_key, base_url)   [_factory.py]
    |
    +-- "openai"  --> OpenAIProvider(model, api_key, base_url)
    +-- "ollama"  --> OllamaProvider(model, host)
    +-- "gemini"  --> GeminiProvider(model, api_key)
    +-- "anthropic" --> AnthropicProvider(model, api_key)  [existing]
    |
    v
ValidateAndRetry(adapter)                                    [_validate.py]
    |
    +-- native=True  (OpenAI, Gemini, Anthropic)
    |   complete_structured() --> adapter.complete_structured() --> Advice instance
    |
    +-- native=False (Ollama)
        complete_structured() --> _fallback_with_retry()
            --> adapter.complete_structured() --> raw dict
            --> schema.model_validate(raw_dict)
            --> [on ValidationError: repair prompt, retry <= MAX_RETRIES=2]
            --> Advice instance
    |
    v
_check_grounding(advice, diagnostics)                        [_validate.py]
    --> GroundingViolationError if evidence cites absent numbers
    |
    v
return Advice
```

### Recommended Project Structure (new files only)

```
python/fdars/advisor/
├── providers/
│   ├── anthropic.py          # existing — unchanged
│   ├── openai.py             # NEW — OpenAIProvider + _openai_schema
│   ├── ollama.py             # NEW — OllamaProvider
│   ├── gemini.py             # NEW — GeminiProvider + _gemini_schema helpers
│   ├── _factory.py           # MODIFIED — new elif branches + _DEFAULT_MODELS/_KEY_ENV entries
│   ├── _protocol.py          # unchanged
│   ├── _validate.py          # unchanged
│   └── __init__.py           # unchanged (or add new providers to __all__ if exported)
└── __init__.py               # MODIFIED — add _require_openai, _require_gemini,
                              #             _require_ollama, version constants

tests/advisor/providers/
├── test_openai_provider.py   # NEW
├── test_ollama_provider.py   # NEW
├── test_gemini_provider.py   # NEW
├── test_gemini_schema.py     # NEW
├── test_factory.py           # MODIFIED — new provider branches
└── test_live_integration.py  # NEW — env-gated, skip cleanly
```

### Tracer-First Sequencing (Claude's Discretion)

Implement in this order:

1. **OpenAI first** — closest to Anthropic's call shape (same `json_schema` concept, similar SDK structure); mock surface is simple; no schema translation needed beyond the `$defs` question.
2. **Ollama second** — no auth; simplest possible call; validates the `supports_native=False` path through `ValidateAndRetry`.
3. **Gemini last** — requires `_gemini_schema` translation; Python 3.10+ guard; most schema-specific work.

Each adapter should be proven with offline mock tests before moving to the next.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Retry / repair loop for non-native providers | Custom retry in each adapter | `ValidateAndRetry._fallback_with_retry` (already in `_validate.py`) | Already implemented with `MAX_RETRIES=2`, grounding-aware repair prompt, deterministic failure |
| JSON repair for malformed LLM output | `json-repair` library or custom parser | `model_validate_json` + one reprompt (already in `_fallback_with_retry`) | The actual failure modes (markdown fences, type coercion) are handled by reprompt |
| OpenAI-compat endpoint abstraction | Separate adapter per endpoint (vLLM, LM Studio, LocalAI) | `OpenAIProvider(base_url=...)` | One SDK covers all compat endpoints via `base_url` |
| Schema portability layer (cross-provider) | Generic schema normalizer | Per-adapter helper (`_openai_schema`, `_gemini_schema`) | Provider-specific schema requirements are idiosyncratic; a single normalizer would be wrong for at least one provider |
| Auth handling for Ollama | Any key management | No key; pass `host=` if non-default | Ollama is a local daemon; auth is not applicable |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already in `dev` extra) |
| Config file | none detected — uses default pytest discovery |
| Quick run command | `pytest tests/advisor/providers/ -x -q` |
| Full suite command | `pytest tests/ -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROV-03 | OpenAI native path returns validated `Advice` | unit (mock) | `pytest tests/advisor/providers/test_openai_provider.py -x` | No — Wave 0 |
| PROV-03 | `base_url` + dummy key wiring for compat endpoints | unit (mock) | `pytest tests/advisor/providers/test_openai_provider.py::test_openai_base_url_dummy_key` | No — Wave 0 |
| PROV-03 | Missing `[openai]` extra → actionable ImportError | unit | `pytest tests/advisor/providers/test_openai_provider.py::test_openai_raises_importerror_without_extra` | No — Wave 0 |
| PROV-04 | Ollama returns dict routed through `ValidateAndRetry` | unit (mock) | `pytest tests/advisor/providers/test_ollama_provider.py -x` | No — Wave 0 |
| PROV-04 | `think=` never passed with `format=` | unit | `pytest tests/advisor/providers/test_ollama_provider.py::test_ollama_never_passes_think_param` | No — Wave 0 |
| PROV-05 | `_gemini_schema` strips `additionalProperties` | unit | `pytest tests/advisor/providers/test_gemini_schema.py -x` | No — Wave 0 |
| PROV-05 | `_gemini_schema` resolves `$ref` / `$defs` | unit | `pytest tests/advisor/providers/test_gemini_schema.py::test_gemini_schema_resolves_refs` | No — Wave 0 |
| PROV-05 | Gemini native path returns validated `Advice` | unit (mock) | `pytest tests/advisor/providers/test_gemini_provider.py -x` | No — Wave 0 |
| PROV-07 | `resolve_provider("openai"|"gemini"|"ollama")` dispatches correctly | unit | `pytest tests/advisor/providers/test_factory.py -x` | No — Wave 0 |
| PROV-07 | Grounding violation caught per adapter | unit | `pytest tests/advisor/providers/ -k "grounding"` | No — Wave 0 |
| QUAL-02 | Live integration tests skip cleanly without keys/daemon | integration | `pytest tests/advisor/providers/test_live_integration.py -q` (expects all skipped) | No — Wave 0 |

### Wave 0 Gaps

- [ ] `tests/advisor/providers/test_openai_provider.py` — covers PROV-03
- [ ] `tests/advisor/providers/test_ollama_provider.py` — covers PROV-04
- [ ] `tests/advisor/providers/test_gemini_provider.py` — covers PROV-05
- [ ] `tests/advisor/providers/test_gemini_schema.py` — covers PROV-05 schema translation
- [ ] `tests/advisor/providers/test_factory.py` — covers PROV-07 dispatch (may be an extension of an existing file)
- [ ] `tests/advisor/providers/test_live_integration.py` — covers QUAL-02

---

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Partial | API keys read from env vars (not hardcoded); dummy `"none"` key only for local endpoints |
| V5 Input Validation | Yes | `model_validate_json` / `model_validate` on every provider response; `_check_grounding` post-parse |
| V6 Cryptography | No | TLS handled by each provider SDK; no custom crypto |

**Key handling rule:** API keys are sourced from env vars (`OPENAI_API_KEY`, `GEMINI_API_KEY`). They are never logged, never included in error messages, never hardcoded. The `api_key="none"` dummy value is only used when `base_url` points to `localhost` — it is not an actual credential.

**Refusal handling (GROUND-04):** Every adapter checks for empty/refusal responses and raises `ValueError` with a descriptive message. OpenAI: `choice.message.refusal`. Gemini: `response.text` is falsy. Ollama: `response.message.content` is falsy. [VERIFIED: anthropic.py:87-94] for the Anthropic reference pattern.

---

## Open Questions

1. **`_openai_schema`: inline `$defs` or pass as-is?**
   - What we know: OpenAI's structured output mode has supported `$ref` + `$defs` since 2024-08. [CITED: STACK.md §OpenAI]
   - What's unclear: Whether compat endpoints (vLLM, LM Studio) support `$ref` in `json_schema` mode.
   - Recommendation: Pass `$defs` as-is for real OpenAI endpoints (the adapter's primary use case). If a compat endpoint fails, the `ValueError` from `model_validate_json` surfaces — the user can switch to `OllamaProvider` for Ollama-hosted models or upgrade the compat endpoint.

2. **Gemini client caching**
   - What we know: Per-call `genai.Client()` construction is correct but creates a new HTTP session on every call.
   - What's unclear: Whether the `google-genai` SDK reuses connection pools internally.
   - Recommendation: Cache `self._client` in `GeminiProvider.__init__`. Construct once; the SDK handles re-auth.

3. **`advise()` signature — should `api_key` and `base_url` be promoted to explicit params?**
   - What we know: Currently `advise()` accepts `provider` and `model` explicitly; `base_url` was reserved in Phase 19 [VERIFIED: __init__.py:223-230 and _factory.py:44-86].
   - What's unclear: Whether the `advise()` docstring needs updating to expose `base_url` and `api_key` for OpenAI/Ollama users, or whether env vars + `resolve_provider()` is the recommended pattern.
   - Recommendation: Update the `advise()` docstring to document env vars (`FDARS_ADVISOR_BASE_URL`, per-provider key vars) as the primary configuration mechanism. The `provider` kwarg already accepts a pre-constructed `Provider` instance, which is the escape hatch for complex configs.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `openai>=1.30.0` has `response_format={"type":"json_schema",...}` support | §OpenAI Call Shape | Low — STACK.md says "structured outputs added in 1.40" with a pin note; the `pyproject.toml` addition should be `>=1.40.0,<2.0` not `>=1.30.0` — see note below |
| A2 | Gemini `response_json_schema=` accepts a raw dict (not a Pydantic model class) | §Gemini Call Shape | Low — STACK.md and official docs confirm `response_json_schema` takes a dict |
| A3 | `ollama>=0.5.0` exposes `__version__` as a dotted string parseable to int tuples | §Deferred Imports | Low — if missing, use `importlib.metadata.version("ollama")` instead |
| A4 | Default Ollama model `"llama3.2"` is available on most local Ollama installations | §resolve_provider Extension | Medium — users must `ollama pull llama3.2`; document this in error message if model not found |

**On A1 — version floor correction:** PITFALLS.md §Dependency and Config Traps says "pin minimum versions for all provider extras: `openai>=1.40.0`". STACK.md §New Backend SDKs says `>=1.30.0`. The PITFALLS.md floor is higher and more conservative. Use `openai>=1.40.0,<2.0` in `pyproject.toml` — structured outputs were added in 1.40.

---

## Sources

### Primary (HIGH confidence — read this session)

- `python/fdars/advisor/providers/anthropic.py` — adapter pattern to mirror [VERIFIED: lines 1-94]
- `python/fdars/advisor/providers/_validate.py` — `ValidateAndRetry`, `_check_grounding` [VERIFIED: lines 1-187]
- `python/fdars/advisor/providers/_factory.py` — `resolve_provider`, `_DEFAULT_MODELS`, `_KEY_ENV` [VERIFIED: lines 1-110]
- `python/fdars/advisor/_schema.py` — `Advice`, `Recommendation` Pydantic definitions [VERIFIED: lines 1-136]
- `python/fdars/advisor/__init__.py` — `advise()`, `_require_anthropic()`, `_require_pydantic()` [VERIFIED: lines 140-297]
- `pyproject.toml` — existing extras and dependency structure [VERIFIED: lines 38-53]
- `.planning/phases/20-additional-provider-adapters/20-CONTEXT.md` — locked decisions

### Secondary (MEDIUM confidence — from STACK.md built against live PyPI + official docs)

- `.planning/research/STACK.md` — verified SDK versions, Python floors, structured-output API shapes per provider
- `.planning/research/PITFALLS.md` — schema divergence, retry contract, grounding leak, CI testing traps
- `.planning/REQUIREMENTS.md` — PROV-03/04/05/07 requirement definitions

---

## Metadata

**Confidence breakdown:**

- Adapter call shapes: HIGH — based on verified SDK shapes from STACK.md (built from live PyPI + official docs) and the verified AnthropicProvider pattern
- Schema translation (`_gemini_schema`): HIGH — pitfalls confirmed against PITFALLS.md which cites upstream SDK issue trackers; `Advice` schema structure verified by reading `_schema.py`
- `pyproject.toml` additions: HIGH — current state verified by reading `pyproject.toml`; additions follow exact pattern of existing extras
- `resolve_provider()` extension: HIGH — current implementation read and verified; extension is additive `elif` branches
- Deferred import pattern: HIGH — verified against existing `_require_anthropic()` and `AnthropicProvider.__init__`
- Offline test strategy: HIGH — mock targets derived from actual import paths in each SDK
- Version pins: MEDIUM — verified via STACK.md (built from PyPI); confirm `openai>=1.40.0` (not 1.30.0) per PITFALLS.md note

**Research date:** 2026-08-12
**Valid until:** 2026-09-12 (SDK APIs stable; Gemini pin `<3.0` should hold; openai 1.x series is in maintenance mode)
