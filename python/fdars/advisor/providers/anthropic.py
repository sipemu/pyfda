"""Anthropic LLM adapter for fdars.advisor.

Wraps the ``anthropic`` SDK's ``messages.parse`` API into the ``Provider``
protocol interface.  The Anthropic backend uses native structured output
(``output_format=Advice``), so ``ValidateAndRetry`` returns the result
directly without a repair loop.

The ``anthropic`` import is deliberately deferred to ``__init__`` (inside a
function body) so that ``import fdars`` and ``build_diagnostics()`` both work
with no LLM SDK installed.  The deferred-import tower is:

    advise()
      └─ resolve_provider()              (imported lazily inside advise())
           └─ AnthropicProvider.__init__ (module imported inside resolve_provider)
                └─ _require_anthropic()  (import anthropic inside function body)
"""
from __future__ import annotations


class AnthropicProvider:
    """Adapter that delegates to ``anthropic.Anthropic().messages.parse``.

    Parameters
    ----------
    model : str
        Claude model identifier.  Default ``"claude-opus-4-8"``.
    api_key : str or None
        Explicit API key.  When ``None``, the SDK reads ``ANTHROPIC_API_KEY``
        from the environment (the same behavior as today's ``advise()``).
    """

    name = "anthropic"
    supports_native_structured_output = True

    def __init__(
        self,
        model: str = "claude-opus-4-8",
        api_key: "str | None" = None,
    ) -> None:
        # Deferred imports — only triggered from resolve_provider(), never at
        # module load.  _require_anthropic() does `import anthropic` inside
        # its own body, so the sys.modules["anthropic"] = None monkeypatch in
        # test_advise_raises_importerror_without_anthropic still fires here.
        from fdars.advisor import _require_anthropic, _require_pydantic  # noqa: PLC0415

        ant = _require_anthropic()
        _require_pydantic()
        self.model = model
        self._client = ant.Anthropic(api_key=api_key) if api_key else ant.Anthropic()

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        """Call ``client.messages.parse`` with the grounded system prompt.

        Parameters
        ----------
        schema : type
            Pydantic model class used as ``output_format`` (e.g. ``Advice``).
        messages : list[dict]
            Conversation messages.
        system : str
            System prompt (contains the grounding invariant).

        Returns
        -------
        object
            Validated Pydantic instance (e.g. ``Advice``).

        Raises
        ------
        ValueError
            When ``response.parsed_output`` is ``None`` — the model responded
            with a refusal or thinking-only block (GROUND-04).
        """
        response = self._client.messages.parse(
            model=self.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=system,
            output_format=schema,
            messages=messages,
        )
        parsed = response.parsed_output
        if parsed is None:
            raise ValueError(
                "AnthropicProvider: the API did not return a parseable output. "
                "The model may have responded with only a thinking block or a refusal. "
                f"Raw response stop_reason: {response.stop_reason!r}"
            )
        return parsed
