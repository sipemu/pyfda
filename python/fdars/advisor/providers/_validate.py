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

    Strategy: collect every numeric token — including negative values and
    decimals — from each evidence string, then match each cited number
    *numerically* against the scalar values in the diagnostics dict.  A citation
    is grounded when it equals some diagnostic scalar **at the citation's own
    decimal precision** (i.e. rounding-tolerant).  This clears three classes of
    false positive that plagued the original exact-string heuristic:

    1. **Index/label integers** (``"cluster 2"`` → ``2``): grounded because ``2``
       equals a real diagnostic scalar (a cluster index / count) when rounded.
    2. **Rounded citations** (``"near 1.9"`` for a stored ``1.9034…``): grounded
       because ``round(1.9034…, 1) == 1.9``.
    3. **Negative numbers** (``"-28.9375"``): the leading sign is now preserved
       by :func:`_extract_numbers`, so it matches the stored ``-28.9375``.
    4. **Array subscripts** (``"explained_variance_ratio[2]=0.9987"``): the
       positional index ``2`` is stripped before extraction, so only the cited
       value ``0.9987`` is checked.
    5. **Scientific notation** (``"5.22e-05"``): parsed as one token and matched
       by relative tolerance, so it grounds against the stored small float.
    6. **Digits inside identifiers** (``"t2_max"``, ``"depth_q90"``,
       ``"depth_q10"``): the digit-runs that belong to the *name* (the ``2`` of
       Hotelling T², the ``90``/``10`` quantile labels) are never extracted — only
       the value to the right of the ``=``/``:``/space is checked — so citations
       of legitimate diagnostics with digit-bearing field names no longer
       false-positive.

    Fabricated values still raise: a cited ``0.87`` that equals no diagnostic
    scalar at 2-decimal precision is rejected, so the guard keeps catching
    genuinely hallucinated statistics.  Evidence items with no numeric tokens
    pass unchecked (qualitative statements are valid).

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
    diag_numbers = _flatten_diagnostics_numbers(diagnostics)
    for rec in advice.recommendations:  # type: ignore[union-attr]
        for ev in rec.evidence:
            for token in _extract_numbers(ev):
                if not _is_grounded_number(token, diag_numbers):
                    raise GroundingViolationError(
                        f"Evidence item cites value {token!r} not found in diagnostics: "
                        f"{ev!r}"
                    )


def _flatten_diagnostics_numbers(d: dict) -> list:
    """Return every numeric scalar (as ``float``) found in a nested dict/list.

    Both dict **values** and numeric dict **keys** are collected.  Numeric keys
    matter because cluster/group identifiers (e.g. ``{"0": {...}, "2": {...}}``)
    are legitimate labels the advisor references as ``"cluster 2"``; treating
    them as grounded values clears the index-reference false-positive class
    without loosening the check for genuine fabrications.

    Booleans are excluded (``bool`` is a subclass of ``int`` in Python but is
    never a cited statistic).  Non-numeric scalars are ignored — grounding only
    concerns numbers.
    """
    result: list = []

    def _coerce(obj: object) -> None:
        if isinstance(obj, bool):
            return
        if isinstance(obj, (int, float)):
            result.append(float(obj))
        elif isinstance(obj, str):
            # Some builders store numeric values (or keys) as strings; recover them.
            try:
                result.append(float(obj))
            except ValueError:
                pass

    def _recurse(obj: object) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                _coerce(k)  # numeric keys are groundable labels (cluster ids)
                _recurse(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                _recurse(v)
        else:
            _coerce(obj)

    _recurse(d)
    return result


def _is_grounded_number(token: str, diag_numbers: list) -> bool:
    """Return True if ``token`` matches a diagnostic scalar at the token's precision.

    The citation's own number of decimal places sets the comparison tolerance:
    a citation of ``1.9`` (1 decimal) is grounded by any diagnostic value that
    rounds to ``1.9`` at 1 decimal; a citation of ``0.4158`` (4 decimals)
    requires a match at 4 decimals.  This mirrors how a human cites a rounded
    statistic while still rejecting fabricated values that round to nothing real.
    """
    try:
        value = float(token)
    except ValueError:
        return False

    # Scientific-notation citations (``5.22e-05``) cannot use decimal-place
    # rounding: counting characters after the ``.`` is meaningless once an
    # exponent is present (it would over-count wildly).  Instead compare with a
    # *relative* tolerance keyed off the mantissa's precision — one unit in its
    # last written decimal place — so a rounded citation (``5.22e-05``) grounds
    # against the stored full-precision float while a fabricated ``9.99e-05``
    # does not.
    if "e" in token or "E" in token:
        mantissa = re.split(r"[eE]", token, maxsplit=1)[0]
        sig_decimals = len(mantissa.split(".", 1)[1]) if "." in mantissa else 0
        rel_tol = 10 ** (-sig_decimals) if sig_decimals > 0 else 1e-9
        import math  # noqa: PLC0415

        for diag in diag_numbers:
            if diag == 0.0:
                if value == 0.0:
                    return True
            elif math.isclose(value, diag, rel_tol=rel_tol):
                return True
        return False

    # Plain integer/decimal citation: the number of decimal places explicitly
    # written sets the rounding tolerance.
    if "." in token:
        decimals = len(token.split(".", 1)[1])
    else:
        decimals = 0

    cited = round(value, decimals)
    for diag in diag_numbers:
        if round(diag, decimals) == cited:
            return True
    return False


# Positional list/array subscripts (``field[2]``) are *references*, not cited
# values — the index must never be treated as a grounded statistic.  Strip the
# whole ``[ int ]`` substring before number extraction.  (Dict-key index
# integers cited in prose, e.g. ``"cluster 2"``, are unaffected: they carry no
# brackets and remain groundable via the numeric-key path in
# :func:`_flatten_diagnostics_numbers`.)
_SUBSCRIPT_RE = re.compile(r"\[\s*\d+\s*\]")

# Numeric-token pattern.  The scientific-notation alternative is ordered FIRST so
# a value like ``5.22e-05`` is consumed as ONE token rather than being split into
# mantissa ``5.22`` and exponent ``-05``.
#
# The lookbehind ``(?<![A-Za-z0-9_.])`` is the heart of the value-only design: a
# numeric literal is extracted only when its first character is NOT glued to a
# preceding *identifier* character (a letter, digit, underscore, or dot).  This
# realizes identifier-token stripping as a single guard — a digit-run that is part
# of a NAME (``t2``, ``depth_q90``, ``depth_q10``, ``chi2``, ``arl0``, ``pc1``) is
# preceded by a letter/underscore and therefore rejected, while a genuinely cited
# value — always separated from its identifier by ``=``, ``:`` or whitespace
# (``k=7``, ``cluster 2``, ``t2_max = 999.9``, ``-28.9375``, ``5.22e-05``) — has a
# non-identifier char (or nothing) before it and survives.  The dot in the class
# also prevents splitting the fractional tail of a larger number.  The optional
# leading sign is captured only when it directly precedes a digit run, so
# hyphenated words are unaffected.
#
# This single lookbehind eliminates the WHOLE digits-in-identifier false-positive
# class (t2_*, depth_q90/q10, cluster labels, component ids), subsuming the two
# prior special-case patches: array subscripts are still stripped by
# ``_SUBSCRIPT_RE`` below, and standalone dict-key indices (``cluster 2``) still
# survive extraction and ground via the numeric-key path in
# :func:`_flatten_diagnostics_numbers`.
_NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_.])-?\d*\.?\d+[eE][+-]?\d+"  # scientific notation, whole token
    r"|(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?"          # plain integer / decimal
)


def _extract_numbers(text: str) -> list:
    """Extract only cited *values* — numeric literals, never identifier digits.

    Matches integers (``4``), decimals (``0.312``), **negative** values
    (``-28.9375``) and **scientific-notation** floats (``5.22e-05``,
    ``5.22e+05``) as single tokens.

    Crucially, a digit-run that is part of an *identifier* is not extracted:
    ``t2_max``, ``depth_q90``, ``depth_q10`` yield only their right-hand value,
    because :data:`_NUMBER_RE`'s lookbehind rejects a numeric literal glued to a
    preceding letter/underscore/digit/dot.  A cited value is always separated
    from its identifier by ``=``, ``:`` or whitespace, so it survives.  Positional
    array/list subscripts (``field[2]``) are additionally stripped first, so the
    index digit is never mistaken for a cited value.
    """
    text = _SUBSCRIPT_RE.sub("", text)
    return _NUMBER_RE.findall(text)
