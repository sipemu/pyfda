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
from typing import List

import numpy as np

# ---------------------------------------------------------------------------
# SDK version floors (Phase 10 resolved; Phase 20 additions)
# ---------------------------------------------------------------------------

ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"
ADVISOR_OPENAI_MIN_VERSION = "1.40.0"
ADVISOR_OLLAMA_MIN_VERSION = "0.6.2"

# ---------------------------------------------------------------------------
# Schema — re-exported from advisor._schema
# ---------------------------------------------------------------------------

from fdars.advisor._schema import Advice, Recommendation  # noqa: E402


__all__ = [
    "build_diagnostics",
    "advise",
    "describe_cluster_differences",
    "Advice",
    "Recommendation",
]


# ---------------------------------------------------------------------------
# Offline diagnostics builder
# ---------------------------------------------------------------------------

def build_diagnostics(
    result,
    method: str,
    *,
    argvals=None,
    n_classes: "int | None" = None,
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
    method : {"alignment", "fpca", "basis", "smoothing", "clustering", "depth", \
"outliers", "classification", "represent", "regression", "regression_cv", "spm"}
        The fdars method that produced ``result``.  For ``"represent"``, pass
        the raw data dict (``{"data": ..., "argvals": ...}``) or an Fdata-like
        object with ``.data``/``.argvals`` attributes directly — not an fdars
        method output.
    argvals : array_like, optional
        Shared evaluation grid, shape ``(m,)``.  Used for amplitude/phase
        distance computations when ``aligned_data`` is present.
    n_classes : int, optional
        Ground-truth class count for the ``"classification"`` aspect; cannot be
        inferred from a result dict (which contains only predicted labels), so
        the caller supplies it.  Ignored by all other methods.
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
    _supported = {
        "alignment", "fpca", "basis", "smoothing", "clustering",  # existing
        "depth",                                                    # ASPECT-02 (plan 21-01)
        "outliers",                                                 # ASPECT-02 (plan 21-02)
        "classification",                                           # ASPECT-03 (plan 21-02)
        "represent",                                               # ASPECT-01 (plan 21-03)
        "regression", "regression_cv",                              # ASPECT-04 (plan 21-04)
        "spm",                                                      # ASPECT-05 (plan 21-05)
        "scoring",                                                  # ADV-01 (plan 28-01)
        "inference",                                               # ADV-03 (plan 34-01) - diagnostics-only
    }
    method_lc = method.lower()
    if method_lc not in _supported:
        raise ValueError(
            f"build_diagnostics: unsupported method {method!r}. "
            f"Supported: {sorted(_supported)!r}."
        )

    # Unwrap result wrappers (e.g. fdars.results.AlignmentResult).
    raw = getattr(result, "raw", result)
    # Coerce to dict ONLY when the value is not already a dict, not an
    # ndarray/array-like (depth returns a score array — `__array__` present),
    # and not an Fdata-like object (`.data` attribute present — represent branch
    # in plan 21-03 accepts Fdata directly).  Both array and Fdata inputs must
    # reach their builder without `dict(raw)` being attempted.
    if (
        not isinstance(raw, dict)
        and not hasattr(raw, "__array__")
        and not hasattr(raw, "data")
    ):
        raw = dict(raw)

    if method_lc == "alignment":
        from fdars.advisor.aspects.alignment import _build_alignment_diagnostics  # noqa: PLC0415
        return _build_alignment_diagnostics(raw, argvals=argvals)

    if method_lc == "fpca":
        from fdars.advisor.aspects.fpca import _build_fpca_diagnostics  # noqa: PLC0415
        return _build_fpca_diagnostics(raw)

    if method_lc == "basis":
        from fdars.advisor.aspects.basis import _build_basis_diagnostics  # noqa: PLC0415
        return _build_basis_diagnostics(raw, **kwargs)

    if method_lc == "smoothing":
        from fdars.advisor.aspects.smoothing import _build_smoothing_diagnostics  # noqa: PLC0415
        return _build_smoothing_diagnostics(raw, **kwargs)

    if method_lc == "clustering":
        from fdars.advisor.aspects.clustering import _build_clustering_diagnostics  # noqa: PLC0415
        return _build_clustering_diagnostics(raw, argvals=argvals, **kwargs)

    if method_lc == "depth":
        from fdars.advisor.aspects.depth import _build_depth_diagnostics  # noqa: PLC0415
        return _build_depth_diagnostics(raw, **kwargs)

    if method_lc == "outliers":
        from fdars.advisor.aspects.outliers import _build_outliers_diagnostics  # noqa: PLC0415
        return _build_outliers_diagnostics(raw, **kwargs)

    if method_lc == "classification":
        from fdars.advisor.aspects.classification import _build_classification_diagnostics  # noqa: PLC0415
        return _build_classification_diagnostics(raw, n_classes=n_classes, **kwargs)

    if method_lc == "represent":
        from fdars.advisor.aspects.represent import _build_represent_diagnostics  # noqa: PLC0415
        return _build_represent_diagnostics(raw, **kwargs)

    if method_lc == "regression":
        from fdars.advisor.aspects.regression import _build_regression_diagnostics  # noqa: PLC0415
        return _build_regression_diagnostics(raw, **kwargs)

    if method_lc == "regression_cv":
        from fdars.advisor.aspects.regression_cv import _build_regression_cv_diagnostics  # noqa: PLC0415
        return _build_regression_cv_diagnostics(raw, **kwargs)

    if method_lc == "spm":
        from fdars.advisor.aspects.spm import _build_spm_diagnostics  # noqa: PLC0415
        return _build_spm_diagnostics(raw, **kwargs)

    if method_lc == "scoring":
        from fdars.advisor.aspects.scoring import _build_scoring_diagnostics  # noqa: PLC0415
        return _build_scoring_diagnostics(raw, **kwargs)

    if method_lc == "inference":
        from fdars.advisor.aspects.inference import _build_inference_diagnostics  # noqa: PLC0415
        return _build_inference_diagnostics(raw, **kwargs)

    # Unreachable given the check above, but kept for safety.
    raise ValueError(f"Unhandled method: {method!r}")


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
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires the anthropic SDK. "
            f"Install it with: pip install fdars[advisor]\n"
            f"Requires: anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}"
        ) from exc

    installed = tuple(
        int(x) for x in anthropic.__version__.split(".")[:3]
    )
    floor = tuple(
        int(x) for x in ADVISOR_ANTHROPIC_MIN_VERSION.split(".")[:3]
    )
    if installed < floor:
        raise ImportError(
            f"fdars advisor requires anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}; "
            f"found {anthropic.__version__}. "
            f"Run: pip install 'anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}'"
        )
    return anthropic


# ---------------------------------------------------------------------------
# Pydantic import guard
# ---------------------------------------------------------------------------

def _require_pydantic():
    """Import and return the ``pydantic`` module, or raise a clear ImportError.

    Raises
    ------
    ImportError
        When the ``pydantic`` package is not installed.  The error message
        contains ``pip install fdars[advisor]`` so users know how to fix it.
    """
    try:
        import pydantic  # noqa: PLC0415
        return pydantic
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires pydantic for structured output. "
            "Install it with: pip install fdars[advisor]"
        ) from exc


# ---------------------------------------------------------------------------
# Provider import guards (Phase 20 — OpenAI, Gemini, Ollama)
# ---------------------------------------------------------------------------

def _require_openai():
    """Import and return the ``openai`` module, or raise a clear ImportError.

    Raises
    ------
    ImportError
        When the ``openai`` package is not installed or is below the version
        floor.  The error message contains ``pip install fdars[openai]``.
    """
    try:
        import openai  # noqa: PLC0415
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
    """Import and return the ``google.genai`` module, or raise a clear ImportError.

    Note: google-genai requires Python >=3.10.  The adapter enforces this at
    runtime with a clear ImportError before calling this guard.

    Raises
    ------
    ImportError
        When the ``google-genai`` package is not installed.  The error message
        contains ``pip install fdars[gemini]`` and notes the Python >=3.10
        requirement.
    """
    try:
        from google import genai  # noqa: PLC0415
        return genai
    except ImportError as exc:
        raise ImportError(
            "The fdars Gemini adapter requires the google-genai SDK. "
            "Install it with: pip install fdars[gemini]\n"
            "Note: requires Python >=3.10."
        ) from exc


def _require_ollama():
    """Import and return the ``ollama`` module, or raise a clear ImportError.

    Raises
    ------
    ImportError
        When the ``ollama`` package is not installed or is below the version
        floor.  The error message contains ``pip install fdars[ollama]``.
    """
    try:
        import ollama  # noqa: PLC0415
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


# ---------------------------------------------------------------------------
# System prompt — re-exported from advisor._prompts
# ---------------------------------------------------------------------------

from fdars.advisor._prompts import _system_prompt  # noqa: E402


# ---------------------------------------------------------------------------
# advise — grounded LLM call
# ---------------------------------------------------------------------------

def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
    provider: "str | object | None" = None,
    aspect: str = "",
) -> Advice:
    """Return schema-validated :class:`Advice` for the given diagnostics.

    Routes through :func:`~fdars.advisor.providers.resolve_provider` to select
    the LLM backend, calls ``complete_structured``, then runs a centralized
    grounding check before returning.  The grounding check (GROUND-03) runs on
    every provider path — it is NOT inside the provider adapter.

    Requires the ``anthropic`` package (``pip install fdars[advisor]``) when
    ``provider`` is ``None`` or ``"anthropic"`` (the default).

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
    provider : str or Provider or None, optional
        LLM provider.  ``None`` (default) reproduces today's Anthropic behavior
        exactly.  Pass a provider name (``"anthropic"``) or an existing
        ``Provider`` instance to override.
    aspect : str, optional
        Selects the per-aspect FDA primer clause injected into the system
        prompt (e.g. ``"depth"``, ``"outliers"``).  Default ``""`` reproduces
        prior behavior exactly — no aspect clause is added (ASPECT-06).

    Returns
    -------
    Advice
        Schema-validated advice object with ``interpretation``,
        ``recommendations``, and ``caveats``.

    Raises
    ------
    ImportError
        When the ``anthropic`` package is not installed (and provider is None
        or ``"anthropic"``).
    GroundingViolationError
        When the returned Advice cites a numeric value absent from diagnostics.
    """
    _require_pydantic()

    # Lazy import: resolve_provider pulls in the providers layer only here,
    # so import fdars never touches an LLM SDK.
    from fdars.advisor.providers._factory import resolve_provider  # noqa: PLC0415
    from fdars.advisor.providers._validate import _check_grounding  # noqa: PLC0415

    p = resolve_provider(provider=provider, model=model)

    system = _system_prompt(task, aspect)

    user_content = (
        f"Domain context: {domain_context}\n\n"
        f"Task: {task}\n\n"
        "Diagnostics (reason only from these values):\n"
        + json.dumps(diagnostics, sort_keys=True, indent=2)
    )

    messages = [{"role": "user", "content": user_content}]
    advice = p.complete_structured(Advice, messages, system)

    # GROUND-03: centralized grounding check — runs on every provider path,
    # not inside the adapter.  Raises GroundingViolationError immediately;
    # never triggers a repair retry (retrying on grounding failure rewards
    # fabrication).
    _check_grounding(advice, diagnostics)

    return advice


# ---------------------------------------------------------------------------
# Cluster-difference specialization (CORE-05)
# ---------------------------------------------------------------------------

def describe_cluster_differences(
    result,
    *,
    argvals=None,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    run_llm: bool = True,
    provider: "str | object | None" = None,
    **kwargs,
):
    """Interpret cluster differences from an fdars clustering result.

    This function is a **specialization** built on top of
    :func:`build_diagnostics` (clustering branch) and :func:`advise`.  It does
    not reimplement the diagnostics; it calls
    ``build_diagnostics(result, method="clustering", argvals=argvals, **kwargs)``
    to produce the deterministic, offline cluster feature report, then
    optionally interprets that report via the Claude API.

    **Stage 1 — offline cluster feature report** (no LLM, no network):

    Calls :func:`build_diagnostics` with ``method="clustering"`` to compute:

    - Per-cluster Karcher means (``cluster_means``)
    - Cluster sizes (``cluster_sizes``)
    - Pairwise amplitude/phase distance between cluster means
      (``pairwise_amplitude_distance``, ``pairwise_phase_distance``) when
      ``argvals`` is provided
    - Scalar separation summaries (``mean_amplitude_separation``,
      ``mean_phase_separation``)

    **Stage 2 — grounded LLM interpretation** (requires anthropic, optional):

    When ``run_llm=True``, passes the cluster feature report to
    :func:`advise` with ``task="interpretation"`` and returns a
    schema-validated :class:`Advice` object.  The LLM reasons only over the
    computed diagnostics and cites specific values in each recommendation.

    Parameters
    ----------
    result : dict or clustering result wrapper
        Native fdars clustering result dict (e.g. from
        ``fdars.clustering.kmeans``) with keys ``centers``, ``cluster``,
        and ``k``.  A wrapper whose ``.raw`` attribute is the underlying
        dict is also accepted (unwrapped by :func:`build_diagnostics`).
    argvals : array_like, optional
        Shared evaluation grid, shape ``(m,)``.  Required for pairwise
        amplitude/phase distance computation between cluster means.  When
        absent, distance keys in the feature report are ``None``.
    domain_context : str, optional
        Free-text description of the problem domain or analysis goal.
        Passed to :func:`advise` to help ground the interpretation.
    model : str, optional
        Claude model identifier.  Default ``"claude-opus-4-8"``.
    run_llm : bool, optional
        When ``True`` (default), call :func:`advise` and return an
        :class:`Advice` object.  When ``False``, return the raw clustering
        diagnostics dict (the Stage 1 feature report) without any LLM or
        network call — fully offline and exercisable in CI without an API key.
    provider : str or Provider or None, optional
        LLM provider forwarded to :func:`advise`.  ``None`` (default) uses the
        Anthropic default, reproducing today's behavior exactly.
    **kwargs
        Forwarded to :func:`build_diagnostics` (reserved for future
        per-method options).

    Returns
    -------
    Advice
        Schema-validated advice when ``run_llm=True``.  Includes a
        plain-language ``interpretation`` of the cluster differences,
        grounded ``recommendations``, and ``caveats``.
    dict
        Raw clustering diagnostics dict (``{"method": "clustering", ...}``)
        when ``run_llm=False``.  Offline path — no anthropic import or
        network call.

    Raises
    ------
    ImportError
        When ``run_llm=True`` and the ``anthropic`` package is not installed.
        The error message names ``pip install fdars[advisor]``.

    Notes
    -----
    This is the design's "cluster-difference feature report" specialization.
    It follows the Stage 1 (deterministic builder) + Stage 2 (grounded LLM
    interpretation) pattern that all later specialization surfaces share.
    The grounding invariant applies: every ``Recommendation`` must cite a
    specific diagnostic value present in the feature report.

    Examples
    --------
    Offline path — inspect the feature report without an API call:

    >>> result = {"centers": [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]],
    ...           "cluster": [0, 0, 1, 1], "k": 2}
    >>> diag = describe_cluster_differences(
    ...     result, argvals=[0.0, 0.5, 1.0], run_llm=False
    ... )
    >>> diag["method"]
    'clustering'
    >>> diag["k"]
    2
    """
    diagnostics = build_diagnostics(
        result, method="clustering", argvals=argvals, **kwargs
    )
    if not run_llm:
        return diagnostics
    return advise(
        diagnostics,
        task="interpretation",
        domain_context=domain_context,
        model=model,
        provider=provider,
    )


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
