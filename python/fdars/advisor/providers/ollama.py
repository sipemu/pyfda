"""Ollama LLM adapter for fdars.advisor.

Wraps the ``ollama`` SDK's ``chat`` function into the ``Provider`` protocol
interface using grammar-constrained decoding (``format=<json_schema>``).

Unlike the OpenAI and Anthropic adapters, ``OllamaProvider`` runs **fully
locally with no API key** — it connects to a running Ollama daemon
(https://ollama.com) on the local machine (or at a custom ``host``).

Structured output strategy
--------------------------
Ollama's ``format=`` parameter enables grammar-constrained decoding: the model
is forced to emit a JSON object that matches the supplied schema.  This is
structurally reliable but field-type coercion (e.g. ``evidence`` as a
``str`` rather than a ``list[str]``) can still fail for smaller local models,
so ``supports_native_structured_output = False``.  ``ValidateAndRetry``
handles Pydantic validation and up to ``MAX_RETRIES=2`` repair retries before
raising deterministically.

Critical constraint: the ``format=`` grammar constraint must not be disabled
---
Some Ollama builds silently ignore ``format=`` if another conflicting
generation parameter is present (Ollama issue #10929).  This adapter never
passes any parameter that conflicts with constrained decoding.  The
``format=`` path is the correctness-critical path.

If repeated validation failures occur at runtime (``ValidateAndRetry`` raises
``ValueError`` after ``MAX_RETRIES`` attempts), this points at schema
serialization complexity for the current model — try a larger local model or
switch to the OpenAI adapter with a compat-endpoint URL.

Deferred imports
----------------
Only ``from __future__ import annotations`` appears at module level.  The
``ollama`` SDK import is deferred to method bodies so that ``import fdars`` and
``build_diagnostics()`` both work with no provider SDK installed (bare-venv
compatibility, Pitfall 4).
"""
from __future__ import annotations


class OllamaProvider:
    """Adapter that delegates to ``ollama.chat`` with format-constrained decoding.

    Connects to a local Ollama daemon (no API key required).  Returns a raw
    dict from ``json.loads(response.message.content)`` so that
    ``ValidateAndRetry._fallback_with_retry`` runs Pydantic schema validation
    and repair retries (``supports_native_structured_output = False``).

    Parameters
    ----------
    model : str
        Ollama model tag to pull and run.  Default ``"llama3.2"``.
    host : str or None
        Custom Ollama daemon URL, e.g. ``"http://192.168.1.10:11434"``.
        When ``None``, the ``ollama`` SDK uses its own default
        (``http://localhost:11434``).
    """

    name = "ollama"
    supports_native_structured_output = False

    def __init__(
        self,
        model: str = "llama3.2",
        host: "str | None" = None,
    ) -> None:
        # Deferred imports — only triggered from resolve_provider(), never at
        # module load.  Keeps bare-venv import of fdars working without ollama.
        from fdars.advisor import _require_ollama, _require_pydantic  # noqa: PLC0415

        _require_ollama()
        _require_pydantic()

        self.model = model
        self._host = host

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> dict:
        """Call ``ollama.chat`` with ``format=<json_schema>`` constrained decoding.

        Prepends the grounding system prompt as a ``{"role": "system", ...}``
        message (Ollama has no separate top-level ``system`` parameter in the
        ``chat`` API).

        Optionally appends a JSON-schema hint to the last user message to
        improve adherence on smaller local models.

        Parameters
        ----------
        schema : type
            Pydantic model class whose ``model_json_schema()`` drives the
            grammar constraint (e.g. ``Advice``).
        messages : list[dict]
            Conversation messages (without system role; injected here).
        system : str
            System prompt (contains the grounding invariant).

        Returns
        -------
        dict
            Raw dict from ``json.loads(response.message.content)``.  NOT a
            validated Pydantic instance — ``ValidateAndRetry._fallback_with_retry``
            handles validation and repair retries.

        Raises
        ------
        ValueError
            When ``response.message.content`` is falsy (empty / None response
            from the model).

        Notes
        -----
        No conflicting generation parameters are passed alongside ``format=``.
        Some Ollama builds silently ignore the grammar constraint when certain
        generation control parameters are present (Ollama issue #10929).
        To preserve constrained decoding, keep the call kwargs minimal.
        """
        import json  # noqa: PLC0415
        import ollama  # noqa: PLC0415

        # Build the schema dict for constrained decoding.
        json_schema = schema.model_json_schema()

        # Prepend system prompt as a system-role message (Ollama chat convention).
        # Append a lightweight JSON-schema hint to the last user message to
        # nudge smaller models toward the required structure.
        hint = (
            f"\n\nReturn your answer as a JSON object conforming to this schema:\n"
            f"{json.dumps(json_schema, indent=2)}"
        )
        wire_messages = [{"role": "system", "content": system}]
        user_msgs = list(messages)
        if user_msgs:
            last = dict(user_msgs[-1])
            last["content"] = str(last.get("content", "")) + hint
            wire_messages += user_msgs[:-1] + [last]
        else:
            wire_messages += user_msgs

        # Build the call kwargs.  host is only added when non-None.
        # CRITICAL: keep call_kwargs minimal — additional generation-control
        # keys can silently disable format= constrained decoding on some
        # Ollama builds (Ollama issue #10929).
        call_kwargs: dict = {
            "model": self.model,
            "messages": wire_messages,
            "format": json_schema,
            "options": {"temperature": 0},
        }
        if self._host is not None:
            call_kwargs["host"] = self._host

        response = ollama.chat(**call_kwargs)

        content = response.message.content
        if not content:
            raise ValueError(
                "OllamaProvider: model returned empty content. "
                "Ensure the Ollama daemon is running and the model is pulled "
                f"('ollama pull {self.model}')."
            )

        return json.loads(content)
