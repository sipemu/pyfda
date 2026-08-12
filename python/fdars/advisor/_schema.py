"""fdars.advisor._schema — Pydantic schema for Advice / Recommendation.

Contains the Pydantic models (with graceful fallback when pydantic is absent)
for :class:`Advice` and :class:`Recommendation`.  Importing this module never
touches the anthropic SDK, never opens a network connection, and never imports
any other fdars.advisor submodule (no circular import risk — see RESEARCH.md
Risk 2).

When ``pydantic`` is not installed the classes still exist as plain
dataclass-style stand-ins so that importing ``fdars.advisor`` and calling
``build_diagnostics`` both succeed without any optional dependency installed.
"""

from __future__ import annotations

from typing import List, Literal

# ---------------------------------------------------------------------------
# Pydantic models (with graceful fallback when pydantic is absent)
# ---------------------------------------------------------------------------

# We attempt to import from pydantic.  When pydantic is not installed we
# synthesise equivalent plain-Python classes so that the module is importable
# offline without the [advisor] extra.  The Pydantic-backed classes are
# required for advise() because anthropic.messages.parse uses them as the
# output_format; that code path also needs the anthropic package, which is
# also absent without the extra — so both missing-dependency paths converge at
# the same _require_anthropic() guard inside advise().

try:
    from pydantic import BaseModel as _PydanticBaseModel

    class Recommendation(_PydanticBaseModel):
        """A single actionable recommendation grounded in fdars diagnostics.

        Attributes
        ----------
        action : str
            Concrete step (e.g. ``"increase n_basis to ~15"``).
        kind : {"parameter", "method", "none"}
            Category of the recommendation.
        rationale : str
            Why this action is warranted, tied to a diagnostic.
        expected_effect : str
            What should change in subsequent runs if the action is applied.
        evidence : list[str]
            Each entry cites a specific diagnostic value present in the input.
        """

        action: str
        kind: Literal["parameter", "method", "none"]
        rationale: str
        expected_effect: str
        evidence: List[str]

    class Advice(_PydanticBaseModel):
        """Schema-validated advice returned by :func:`advise`.

        Attributes
        ----------
        interpretation : str
            Plain-language interpretation of the result in domain terms.
        recommendations : list[Recommendation]
            Concrete next actions ordered by priority.
        caveats : list[str]
            Limitations, assumptions, or conditions that qualify the advice.
        """

        interpretation: str
        recommendations: List[Recommendation]
        caveats: List[str]

except ImportError:
    # pydantic is absent — define minimal stand-ins so importing advisor and
    # calling build_diagnostics work fully offline.

    class Recommendation:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic Recommendation model.

        Has the same fields; not schema-validated.  advise() requires pydantic
        and will fail with a clear error before this class is used in that path.
        """

        def __init__(
            self,
            action: str,
            kind: str,
            rationale: str,
            expected_effect: str,
            evidence: List[str],
        ):
            self.action = action
            self.kind = kind
            self.rationale = rationale
            self.expected_effect = expected_effect
            self.evidence = evidence

        def __repr__(self) -> str:
            return (
                f"Recommendation(action={self.action!r}, kind={self.kind!r})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Recommendation):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class Advice:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic Advice model.

        Has the same fields; not schema-validated.  advise() requires pydantic
        and will fail with a clear error before this class is used in that path.
        """

        def __init__(
            self,
            interpretation: str,
            recommendations: List[Recommendation],
            caveats: List[str],
        ):
            self.interpretation = interpretation
            self.recommendations = recommendations
            self.caveats = caveats

        def __repr__(self) -> str:
            n = len(self.recommendations)
            return (
                f"Advice(interpretation=..., recommendations={n}, "
                f"caveats={len(self.caveats)})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Advice):
                return NotImplemented
            return self.__dict__ == other.__dict__
