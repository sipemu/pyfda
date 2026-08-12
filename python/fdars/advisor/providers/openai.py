"""OpenAI LLM adapter for fdars.advisor.

Wraps the ``openai`` SDK's ``chat.completions.create`` API into the ``Provider``
protocol interface using native structured output (``response_format=json_schema``).

This adapter handles both the public OpenAI API and any OpenAI-compatible local
endpoint (vLLM, LM Studio, LocalAI) via the ``base_url`` constructor parameter.

For local/compat endpoints that do not require authentication, pass a dummy
``api_key="none"`` to avoid SDK-level ``AuthenticationError``.  The adapter
detects ``localhost``/``127.0.0.1`` base URLs and applies this automatically.

All SDK imports are deliberately deferred to ``__init__``/method bodies so that
``import fdars`` and ``build_diagnostics()`` both work with no provider SDK
installed (Pitfall 4 — bare-venv compatibility).

Note on OpenAI-compatible endpoints (vLLM/LM Studio/LocalAI)
-------------------------------------------------------------
These are reached via ``base_url="http://localhost:1234/v1"``.  Not all compat
endpoints reliably honour ``strict: True`` in ``json_schema`` mode — if
``model_validate_json`` fails, a ``ValueError`` is raised and surfaced to the
caller.  For Ollama-served models, use ``OllamaProvider`` (which uses the
native ``format=`` constrained-decoding path) instead.

``supports_native_structured_output=True`` is set for all ``OpenAIProvider``
instances: the adapter calls ``model_validate_json`` and returns a validated
``Advice`` instance, so ``ValidateAndRetry``'s native path returns it directly.
"""
from __future__ import annotations

import re as _re


def _openai_schema(model_cls: type) -> dict:
    """Convert a Pydantic model to an OpenAI ``json_schema``-compatible dict.

    OpenAI strict mode (``strict: True``) requires:

    - ``additionalProperties: false`` on every object (Pydantic v2 already
      emits this).
    - All fields listed in ``required`` (Pydantic adds this for non-Optional
      fields).

    OpenAI's ``json_schema`` mode has supported ``$defs``/``$ref`` since
    2024-08, so Pydantic's nested ``$defs`` for ``Recommendation`` are passed
    as-is (do **not** inline manually — Pitfall 6).

    The root-level ``title`` key is redundant (the ``name`` field in the
    ``json_schema`` envelope serves that purpose) and is removed to keep the
    wire payload clean.

    Parameters
    ----------
    model_cls : type
        Pydantic ``BaseModel`` subclass (e.g. ``Advice``).

    Returns
    -------
    dict
        JSON Schema dict safe to pass as ``schema`` inside the OpenAI
        ``response_format`` envelope.
    """
    schema = model_cls.model_json_schema()
    schema.pop("title", None)
    return schema


class OpenAIProvider:
    """Adapter that delegates to ``openai.OpenAI().chat.completions.create``.

    Supports the public OpenAI API and any OpenAI-compatible endpoint (vLLM,
    LM Studio, LocalAI) via the ``base_url`` constructor parameter.

    Parameters
    ----------
    model : str
        Model identifier.  Default ``"gpt-4o"``.
    api_key : str or None
        Explicit API key.  When ``None`` and ``base_url`` points to a local
        endpoint (``localhost`` / ``127.0.0.1``), falls back to ``"none"``
        (a dummy non-empty key) to avoid SDK-level ``AuthenticationError``
        for keyless local compat endpoints (Pitfall 3).  When ``None`` and no
        local ``base_url`` is set, the SDK reads ``OPENAI_API_KEY`` from the
        environment.
    base_url : str or None
        Custom base URL, e.g. ``"http://localhost:1234/v1"`` for LM Studio.
        When ``None``, uses the OpenAI default.
    """

    name = "openai"
    supports_native_structured_output = True

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: "str | None" = None,
        base_url: "str | None" = None,
    ) -> None:
        # Deferred imports — only triggered from resolve_provider(), never at
        # module load.  Keeps bare-venv import of fdars working without openai.
        from fdars.advisor import _require_openai, _require_pydantic  # noqa: PLC0415

        _openai_mod = _require_openai()
        _require_pydantic()

        self.model = model

        # Dummy key for local/compat endpoints that don't require auth.
        # Security (T-20-02): when base_url is set, use "none" so the real
        # OPENAI_API_KEY is never forwarded to a local endpoint.
        resolved_key = api_key
        if resolved_key is None and base_url is not None:
            if _re.search(r"localhost|127\.0\.0\.1", base_url):
                resolved_key = "none"

        self._client = _openai_mod.OpenAI(api_key=resolved_key, base_url=base_url)

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        """Call ``chat.completions.create`` with a json_schema response format.

        Parameters
        ----------
        schema : type
            Pydantic model class (e.g. ``Advice``) used to constrain the
            response format and validate the returned JSON.
        messages : list[dict]
            Conversation messages (without system role; system is injected
            as the first message per OpenAI convention).
        system : str
            System prompt (contains the grounding invariant).

        Returns
        -------
        object
            Validated Pydantic instance (e.g. ``Advice``).

        Raises
        ------
        ValueError
            When ``choice.message.refusal`` is non-empty (GROUND-04 parity
            with ``AnthropicProvider``), or when ``choice.message.content``
            is falsy (empty / None response from the model).
        """
        # Inject system prompt as the first message (OpenAI convention).
        wire_messages = [{"role": "system", "content": system}] + list(messages)

        # Build the json_schema response_format envelope.
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

        # GROUND-04: detect refusal — mirrors AnthropicProvider behavior.
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

        # Parse and validate; return a Pydantic instance so ValidateAndRetry's
        # native path (supports_native_structured_output=True) returns directly.
        return schema.model_validate_json(raw_json)
