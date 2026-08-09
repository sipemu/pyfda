"""fdars.advisor — Grounded AI analysis advisor for fdars results.

Provides two complementary primitives:

* :func:`build_diagnostics` — **offline, deterministic** diagnostics builder.
  Takes an fdars result dict (or wrapper object) and computes a plain-Python,
  JSON-serialisable diagnostics dict from fdars + NumPy only. No LLM, no
  network, no RNG, no wall-clock dependency.  Two calls on the same input
  always return an equal dict.

* :func:`advise` — **grounded Claude call** that interprets the diagnostics
  and returns a schema-validated :class:`Advice` object.  Requires the
  ``anthropic`` package (``pip install fdars[advisor]``).  The LLM reasons
  only over numbers present in the diagnostics; it never fabricates values.

Pydantic models (:class:`Advice`, :class:`Recommendation`) follow the schema
from ``.planning/design/llm-cluster-narration.md``.  When ``pydantic`` is not
installed the classes still exist (as plain dataclass-style objects) so that
importing this module and calling ``build_diagnostics`` both succeed without
any optional dependency installed.  The Pydantic-backed definitions are
required only when ``advise`` is called (they are used as the
``output_format`` for ``client.messages.parse``).

Anthropic SDK version floor
---------------------------
The minimum ``anthropic`` version that supports
``client.messages.parse(output_format=<PydanticModel>)`` and the
``claude-opus-4-8`` model is **0.72.0**.  This decision is RESOLVED here in
Phase 10.  The ``[advisor]`` optional extra (declaring
``anthropic>=0.72.0`` in ``pyproject.toml``) is DECLARED and TESTED in
Phase 11 per the phase split — do not add the extra to pyproject.toml in this
phase.

Grounding invariant
-------------------
Every ``Recommendation`` carries an ``evidence`` list whose entries each cite
a specific value that appears in the diagnostics dict.  The system prompt
reinforces this at the LLM level.  The schema makes ``evidence`` a required
field so the model cannot omit it.
"""

from __future__ import annotations

import json
from typing import List, Literal

import numpy as np

# ---------------------------------------------------------------------------
# SDK version floor (Phase 10 open decision — RESOLVED)
# ---------------------------------------------------------------------------

ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"

# ---------------------------------------------------------------------------
# Schema — Pydantic models (with graceful fallback when pydantic is absent)
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


__all__ = ["build_diagnostics", "advise", "Advice", "Recommendation"]


# ---------------------------------------------------------------------------
# Offline diagnostics builder
# ---------------------------------------------------------------------------

def build_diagnostics(
    result,
    method: str,
    *,
    argvals=None,
    **kwargs,
) -> dict:
    """Build a deterministic, JSON-serialisable diagnostics dict from an fdars result.

    This function is **offline and deterministic**: it uses only NumPy and
    (optionally) fdars submodules.  It never imports ``anthropic``, opens a
    network connection, uses any RNG, or reads wall-clock time.  Two calls on
    the same input always return an equal dict.

    Parameters
    ----------
    result : dict or AlignmentResult
        Native fdars output dict (or a ``fdars.results`` wrapper whose ``.raw``
        attribute is the underlying dict).
    method : {"alignment"}
        The fdars method that produced ``result``.  Additional methods will be
        added in Phase 10-02 (fpca, basis, smoothing, clustering).
    argvals : array_like, optional
        Shared evaluation grid, shape ``(m,)``.  Used for amplitude/phase
        distance computations when ``aligned_data`` is present.
    **kwargs
        Reserved for future per-method options.

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``list``,
        ``str``, ``bool``, ``int``, ``None``).  No NumPy scalars.

    Raises
    ------
    ValueError
        If ``method`` is not in the currently supported set.
    """
    _supported = {"alignment"}
    method_lc = method.lower()
    if method_lc not in _supported:
        raise ValueError(
            f"build_diagnostics: unsupported method {method!r}. "
            f"Supported: {sorted(_supported)!r}. "
            "Additional methods (fpca, basis, smoothing, clustering) "
            "will be added in Phase 10-02."
        )

    # Unwrap result wrappers (e.g. fdars.results.AlignmentResult).
    raw: dict = getattr(result, "raw", result)
    if not isinstance(raw, dict):
        raw = dict(raw)

    if method_lc == "alignment":
        return _build_alignment_diagnostics(raw, argvals=argvals)

    # Unreachable given the check above, but kept for future branches.
    raise ValueError(f"Unhandled method: {method!r}")


def _build_alignment_diagnostics(raw: dict, *, argvals=None) -> dict:
    """Compute alignment-specific diagnostics from a karcher_mean-style result.

    All values are cast to plain Python types (``float``, ``list``, ``bool``,
    ``int``) so repeated runs are byte-identical and the result is
    JSON-serialisable.
    """
    diag: dict = {"method": "alignment"}

    # -- Karcher / template mean summary ------------------------------------
    mean_raw = raw.get("mean")
    if mean_raw is not None:
        mean_arr = np.asarray(mean_raw, dtype=float)
        diag["mean_length"] = int(mean_arr.shape[0])
        diag["mean_min"] = float(np.min(mean_arr))
        diag["mean_max"] = float(np.max(mean_arr))
        diag["mean_avg"] = float(np.mean(mean_arr))
        # Full mean curve as a plain list for downstream reference
        diag["mean_curve"] = [float(v) for v in mean_arr]
    else:
        diag["mean_length"] = None
        diag["mean_min"] = None
        diag["mean_max"] = None
        diag["mean_avg"] = None
        diag["mean_curve"] = None

    # -- Warp / amplitude / phase separation --------------------------------
    aligned_raw = raw.get("aligned_data")
    if aligned_raw is not None and mean_raw is not None and argvals is not None:
        aligned_arr = np.asarray(aligned_raw, dtype=float)
        mean_arr = np.asarray(mean_raw, dtype=float)
        av_arr = np.asarray(argvals, dtype=float)

        # Lazy import inside build_diagnostics — importing advisor never forces
        # a heavy import chain on its own.
        from fdars import alignment as _alignment  # noqa: PLC0415

        amp_dists = []
        phase_dists = []
        for curve in aligned_arr:
            try:
                amp = float(_alignment.amplitude_distance(curve, mean_arr, av_arr, 0.0))
                phase = float(_alignment.phase_distance(curve, mean_arr, av_arr, 0.0))
            except Exception:
                amp = float("nan")
                phase = float("nan")
            amp_dists.append(amp)
            phase_dists.append(phase)

        diag["n_obs"] = int(aligned_arr.shape[0])
        diag["amplitude_distances"] = amp_dists
        diag["phase_distances"] = phase_dists
        diag["amplitude_mean"] = float(np.nanmean(amp_dists))
        diag["amplitude_max"] = float(np.nanmax(amp_dists))
        diag["phase_mean"] = float(np.nanmean(phase_dists))
        diag["phase_max"] = float(np.nanmax(phase_dists))
    elif aligned_raw is not None:
        aligned_arr = np.asarray(aligned_raw, dtype=float)
        diag["n_obs"] = int(aligned_arr.shape[0])
        diag["amplitude_distances"] = None
        diag["phase_distances"] = None
        diag["amplitude_mean"] = None
        diag["amplitude_max"] = None
        diag["phase_mean"] = None
        diag["phase_max"] = None
    else:
        diag["n_obs"] = None
        diag["amplitude_distances"] = None
        diag["phase_distances"] = None
        diag["amplitude_mean"] = None
        diag["amplitude_max"] = None
        diag["phase_mean"] = None
        diag["phase_max"] = None

    # -- Convergence --------------------------------------------------------
    converged_raw = raw.get("converged")
    diag["converged"] = bool(converged_raw) if converged_raw is not None else None

    n_iter_raw = raw.get("n_iter")
    diag["n_iter"] = int(n_iter_raw) if n_iter_raw is not None else None

    return diag


# ---------------------------------------------------------------------------
# Anthropic import guard
# ---------------------------------------------------------------------------

def _require_anthropic():
    """Import and return the ``anthropic`` module, or raise a clear ImportError.

    Raises
    ------
    ImportError
        When the ``anthropic`` package is not installed.  The error message
        contains ``pip install fdars[advisor]`` (install hint, CORE-04) and
        ``anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}`` (version floor, Phase 10
        resolved decision).
    """
    try:
        import anthropic  # noqa: PLC0415
        return anthropic
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires the anthropic SDK. "
            f"Install it with: pip install fdars[advisor]\n"
            f"Requires: anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}"
        ) from exc


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _system_prompt(task: str) -> str:
    """Build the grounded-output system prompt for the given task family.

    The base prompt encodes the grounding invariant and an FDA primer.
    A task-family clause is appended based on ``task``.

    Parameters
    ----------
    task : str
        Task family identifier (case-insensitive).  Currently supported:
        ``"interpretation"``.  Additional task clauses (``"parameter"``,
        ``"method"``) will be added in Phase 10-02.

    Returns
    -------
    str
        The complete system prompt to pass to the Claude API.

    Raises
    ------
    ValueError
        If ``task`` is not in the currently supported set.
    """
    task_lc = task.lower().strip()

    # -- Grounding invariant (MUST be present verbatim) ---------------------
    base = (
        "You are a functional data analysis (FDA) advisor. "
        "You reason only from the diagnostics provided in the user message. "
        "Every evidence item in each Recommendation must cite a specific "
        "diagnostic value that appears in the input — do not omit this. "
        "Omit any claim not supported by a provided value. "
        "Never fabricate numbers or invent values not present in the diagnostics. "
        "Never estimate or assume numerical results that are not explicitly given.\n\n"
        # FDA primer so the model interprets results with method-accuracy
        "FDA primer:\n"
        "- Amplitude variation: variability in the height/magnitude of curves "
        "(captured by amplitude_distance; large values indicate shape differences).\n"
        "- Phase variation: variability in the timing/location of features "
        "(captured by phase_distance; large values indicate time-warping is substantial).\n"
        "- Karcher mean (template mean): the elastic Frechet mean of a set of curves, "
        "computed iteratively by warping each curve toward the current mean; "
        "convergence is indicated by the converged flag and n_iter count.\n"
        "- Warp penalty (lambda_): regularisation strength on the warping functions; "
        "higher values penalise large warps and preserve more phase variation in the aligned curves.\n"
        "- GCV (generalised cross-validation): a model-selection criterion for smoothing "
        "and basis representation; lower GCV indicates better generalisation.\n"
        "- Variance explained: cumulative proportion of total functional variation "
        "captured by the leading FPCA components.\n"
    )

    # -- Task-family clause -------------------------------------------------
    _supported_tasks = {"interpretation"}
    if task_lc not in _supported_tasks:
        raise ValueError(
            f"_system_prompt: unsupported task {task!r}. "
            f"Supported: {sorted(_supported_tasks)!r}. "
            "Additional task clauses (parameter, method) will be added in Phase 10-02."
        )

    if task_lc == "interpretation":
        task_clause = (
            "Task: interpretation.\n"
            "Explain what the computed result means in domain terms: "
            "describe the amplitude and phase variation balance, "
            "whether the alignment converged and in how many iterations, "
            "and what the mean curve summary implies about the underlying process. "
            "Set recommendation kind to 'none' unless a concrete parameter or "
            "method change is clearly warranted by the diagnostics. "
            "When kind is 'none', set action to a concise interpretation summary "
            "rather than a blank string."
        )

    return base + "\n" + task_clause


# ---------------------------------------------------------------------------
# advise — grounded LLM call
# ---------------------------------------------------------------------------

def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
) -> Advice:
    """Return schema-validated :class:`Advice` for the given diagnostics.

    Calls the Claude API via ``client.messages.parse`` with adaptive thinking
    and the grounding-invariant system prompt.  Returns the validated
    :class:`Advice` object.

    Requires the ``anthropic`` package (``pip install fdars[advisor]``).

    Parameters
    ----------
    diagnostics : dict
        Output from :func:`build_diagnostics`.
    task : str
        Task family (``"interpretation"``; more added in Phase 10-02).
    domain_context : str
        Free-text description of the problem domain, dataset, or analysis goal.
        Helps the model ground its interpretation in the user's context.
    model : str, optional
        Claude model identifier.  Default ``"claude-opus-4-8"``.

    Returns
    -------
    Advice
        Schema-validated advice object with ``interpretation``,
        ``recommendations``, and ``caveats``.

    Raises
    ------
    ImportError
        When the ``anthropic`` package is not installed.
    """
    anthropic = _require_anthropic()
    client = anthropic.Anthropic()

    system = _system_prompt(task)

    user_content = (
        f"Domain context: {domain_context}\n\n"
        f"Task: {task}\n\n"
        "Diagnostics (reason only from these values):\n"
        + json.dumps(diagnostics, sort_keys=True, indent=2)
    )

    response = client.messages.parse(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=system,
        output_format=Advice,
        messages=[{"role": "user", "content": user_content}],
    )

    return response.parsed_output


# ---------------------------------------------------------------------------
# Offline determinism check (importable, side-effect-free)
# ---------------------------------------------------------------------------

def _selfcheck_alignment_diagnostics() -> None:
    """Verify that build_diagnostics(alignment) is deterministic on a fixed input.

    Uses only inline fixed arrays (no RNG). Asserts that two calls on the same
    input return an equal, JSON-serialisable dict.

    Raises
    ------
    AssertionError
        If two calls return different dicts (should never happen).
    """
    synthetic = {
        "mean": [0.0, 1.0, 2.0, 1.0, 0.0],
        "aligned_data": [
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.1, 1.1, 2.0, 0.9, 0.0],
        ],
        "converged": True,
        "n_iter": 3,
    }
    av = [0.0, 0.25, 0.5, 0.75, 1.0]
    d1 = build_diagnostics(synthetic, method="alignment", argvals=av)
    d2 = build_diagnostics(synthetic, method="alignment", argvals=av)
    assert d1 == d2, (
        "build_diagnostics(alignment) is not deterministic: "
        f"first call returned {d1}, second call returned {d2}"
    )
    # Verify JSON-serialisability (no numpy scalars, no non-serialisable types).
    json.dumps(d1)
