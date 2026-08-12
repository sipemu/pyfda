"""Validate-and-retry wrapper and grounding checker for fdars.advisor.

Two responsibilities in one file (both run at the call boundary between
advise() and an LLM adapter):

1. ``ValidateAndRetry`` — wraps any ``Provider`` to add schema validation and
   repair retry for non-native providers.  Native providers (Anthropic) skip
   the repair loop entirely.

2. ``_check_grounding`` — centralized grounding check called by ``advise()``
   after ``complete_structured()`` returns, regardless of provider.  Raises
   ``GroundingViolationError`` if an evidence item cites a numeric value absent
   from the diagnostics dict.
"""
from __future__ import annotations

import re


class GroundingViolationError(ValueError):
    """Raised when an Advice recommendation cites a value absent from diagnostics."""


class ValidateAndRetry:
    """Wraps any Provider to add schema validation and repair retry.

    For providers with ``supports_native_structured_output=True`` (e.g.
    Anthropic), the wrapper delegates directly to the underlying provider and
    returns the result without modification — the provider already enforces
    schema.

    For providers with ``supports_native_structured_output=False`` (e.g. Ollama
    returning raw JSON), the wrapper runs Pydantic validation on the returned
    dict and attempts a repair retry up to ``MAX_RETRIES`` times before raising
    deterministically.  It never fabricates a result.
    """

    MAX_RETRIES = 2  # hardcoded; never exceed 2 structural repair retries

    def __init__(self, provider: object) -> None:
        self._provider = provider

    @property
    def name(self) -> str:
        return self._provider.name  # type: ignore[union-attr]

    @property
    def model(self) -> str:
        return self._provider.model  # type: ignore[union-attr]

    @property
    def supports_native_structured_output(self) -> bool:
        return self._provider.supports_native_structured_output  # type: ignore[union-attr]

    def complete_structured(self, schema: type, messages: list, system: str) -> object:
        """Run completion through the wrapped provider.

        Native path: delegate directly — provider enforces schema, return as-is.
        Non-native path: run ``_fallback_with_retry``.
        """
        if self._provider.supports_native_structured_output:  # type: ignore[union-attr]
            # Native path: provider returns a validated schema instance already.
            return self._provider.complete_structured(schema, messages, system)  # type: ignore[union-attr]
        return self._fallback_with_retry(schema, messages, system)

    def _fallback_with_retry(
        self, schema: type, messages: list, system: str
    ) -> object:
        """Non-native path: validate JSON dict from provider, retry with repair prompt.

        Raises
        ------
        ValueError
            After ``MAX_RETRIES`` failed validation attempts — never fabricates.
        """
        from pydantic import ValidationError  # noqa: PLC0415

        attempt = 0
        last_error: Exception | None = None
        current_messages = list(messages)

        while attempt < self.MAX_RETRIES:
            raw = self._provider.complete_structured(schema, current_messages, system)  # type: ignore[union-attr]
            try:
                if isinstance(raw, dict):
                    return schema.model_validate(raw)  # type: ignore[union-attr]
                # Already an instance (shouldn't happen in fallback path, but safe)
                return raw
            except ValidationError as exc:
                last_error = exc
                attempt += 1
                if attempt < self.MAX_RETRIES:
                    # Repair prompt — must re-include original messages (grounding)
                    repair_msg = {
                        "role": "user",
                        "content": (
                            "Your previous response did not conform to the required "
                            f"JSON structure. Errors:\n{exc}\n\n"
                            "Return only a valid JSON object. "
                            "Reason only from the diagnostics in the earlier message."
                        ),
                    }
                    current_messages = list(messages) + [repair_msg]

        raise ValueError(
            f"Provider {self._provider.name!r} failed to return valid structured output "  # type: ignore[union-attr]
            f"after {self.MAX_RETRIES} attempts. Last error: {last_error}"
        )


# ---------------------------------------------------------------------------
# Grounding check — called in advise() after complete_structured() returns
# ---------------------------------------------------------------------------

def _check_grounding(advice: object, diagnostics: dict) -> None:
    """Raise GroundingViolationError if evidence cites a number absent from diagnostics.

    Strategy: collect all numeric tokens (integers and floats) that appear in
    every evidence string across all recommendations.  For each such token,
    verify it appears somewhere in the flattened string representation of the
    diagnostics values.  Evidence items with no numeric tokens pass unchecked
    (they are qualitative statements, which is valid).

    This is a lightweight heuristic — it catches clearly fabricated values
    (e.g. "k=7" when diagnostics has k=4) but is deliberately lenient on
    floating-point formatting to avoid false positives.

    Parameters
    ----------
    advice : Advice
        Schema-validated Advice instance returned by ``complete_structured``.
    diagnostics : dict
        The original diagnostics dict passed to ``advise()``.

    Raises
    ------
    GroundingViolationError
        When any evidence item cites a numeric value not found in the
        diagnostics.  Raises immediately — never triggers a repair retry,
        because retrying on grounding failure rewards fabrication.
    """
    diag_text = _flatten_diagnostics_text(diagnostics)
    for rec in advice.recommendations:  # type: ignore[union-attr]
        for ev in rec.evidence:
            nums = _extract_numbers(ev)
            for n in nums:
                if n not in diag_text:
                    raise GroundingViolationError(
                        f"Evidence item cites value {n!r} not found in diagnostics: "
                        f"{ev!r}"
                    )


def _flatten_diagnostics_text(d: dict) -> set:
    """Return a set of string representations of all scalar values in a nested dict.

    Adds multiple float representations to reduce false positives from
    floating-point formatting differences (e.g. ``0.3124`` appears as
    ``"0.3124"``, ``"0.312"``, and ``"0.3124"`` in the set).
    """
    result: set = set()

    def _recurse(obj: object) -> None:
        if isinstance(obj, dict):
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                _recurse(v)
        elif obj is not None:
            result.add(str(obj))
            if isinstance(obj, float):
                result.add(f"{obj:.3f}")
                result.add(f"{obj:.4f}")

    _recurse(d)
    return result


def _extract_numbers(text: str) -> list:
    """Extract decimal numeric tokens from an evidence string.

    Matches both integers (``4``) and decimals (``0.312``).  The word-boundary
    anchor ``\\b`` avoids matching substrings of larger numbers.
    """
    return re.findall(r"\b\d+\.?\d*\b", text)
