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

from fdars.advisor._schema import Advice, Recommendation, PipelineReport  # noqa: E402


__all__ = [
    "build_diagnostics",
    "advise",
    "describe_cluster_differences",
    "compare_methods",
    "build_pipeline_report",
    "pipeline_report",
    "auto_tune",
    "Advice",
    "Recommendation",
    "PipelineReport",
]

from fdars.advisor._compare_methods import compare_methods  # noqa: E402
from fdars.advisor._pipeline import build_pipeline_report, pipeline_report  # noqa: E402


# ---------------------------------------------------------------------------
# Offline diagnostics builder
# ---------------------------------------------------------------------------

def build_diagnostics(
    result,
    method: str,
    *,
    argvals=None,
    n_classes: "int | None" = None,
    holdout_accuracy: "float | None" = None,
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
"outliers", "classification", "represent", "regression", "regression_cv", \
"spm", "scoring", "inference"}
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
    holdout_accuracy : float, optional
        Caller-supplied holdout or CV accuracy for the ``"classification"`` aspect.
        Used by the ``elastic_multinomial`` branch to compute the overfitting gap
        (train_accuracy minus holdout_accuracy).  The ``elastic_multinomial`` result
        has no holdout accuracy of its own; passing this value enables the gap.
        When ``None`` (default) the gap is ``None`` (not fabricated).
        Ignored by all other methods (ASPECT-02).
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
        "fts",      # ADV-01 Phase 72 — diagnostics-only
        "frechet",  # ADV-01 Phase 72 — diagnostics-only
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
        return _build_classification_diagnostics(
            raw, n_classes=n_classes, holdout_accuracy=holdout_accuracy, **kwargs
        )

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

    if method_lc == "fts":
        from fdars.advisor.aspects.fts import _build_fts_diagnostics  # noqa: PLC0415
        return _build_fts_diagnostics(raw, **kwargs)

    if method_lc == "frechet":
        from fdars.advisor.aspects.frechet import _build_frechet_diagnostics  # noqa: PLC0415
        return _build_frechet_diagnostics(raw, **kwargs)

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
# auto_tune — LLM-backed closed-loop parameter tuning (TUNE-03)
# ---------------------------------------------------------------------------


def auto_tune(
    dataset_id: str,
    method: str,
    *,
    target_metric: "str | None" = None,
    max_steps: int = 10,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    provider: "str | object | None" = None,
    guard: bool = True,
    # Test seams: injectable run_method and build_diagnostics (same as run_tuning_loop)
    _run_method: "callable | None" = None,
    _build_diagnostics: "callable | None" = None,
    **initial_params,
) -> "TuneResult":  # noqa: F821
    """Run the closed-loop tuning orchestrator with an LLM-backed propose_fn.

    The LLM proposes a SINGLE parameter change per iteration via the
    ``parameter_proposal`` task clause.  The proposal is read ONLY from the
    schema-validated ``Recommendation.parameter_delta`` field — never from prose.
    The orchestrator clamps ``parameter_delta.new_value`` to the declared range
    before it enters the numeric path.  A missing/wrong-param ``parameter_delta``
    exits the loop with ``stop_reason='parse_failure'`` and NO second LLM call
    (the LLM never re-enters the numeric path).

    Grounding-invariant hard boundary (TUNE-03, T-53B-01)
    -------------------------------------------------------
    The LLM's ONLY numeric contribution is ``TuneProposal.new_value``, which is:

    1. Read from ``Recommendation.parameter_delta.new_value`` (schema-validated).
    2. Clamped to the param's declared range (never rejected for out-of-range).
    3. Int-cast when ``param_type`` is ``int``.
    4. The single number from the LLM that ever enters the fdars numeric path.

    Prose is never parsed.  A bad proposal (no ``parameter_delta``, wrong param
    name) exits the loop immediately with ``parse_failure`` — no retry.

    Parameters
    ----------
    dataset_id : str
        Opaque dataset handle registered in the MCP registry.  May be any
        string when ``_run_method`` and ``_build_diagnostics`` are injected.
    method : str
        The fdars method to tune (``"smoothing"``, ``"basis"``, ``"fpca"``,
        ``"clustering"``).  Raises ``ValueError`` for non-tuneable methods
        (``"alignment"``, ``"depth"``).
    target_metric : str or None, optional
        Diagnostic metric key to optimise.  When ``None``, the default for the
        method is read from ``_PARAM_REGISTRY``.
    max_steps : int, optional
        Maximum number of loop iterations (hard cap; default 10, max 20).
    domain_context : str, optional
        Free-text description of the problem domain passed to ``advise()``.
    model : str, optional
        LLM model identifier (default ``"claude-opus-4-8"``).
    provider : str or Provider or None, optional
        LLM provider forwarded to ``advise()``.  ``None`` uses the Anthropic
        default.  Pass a fake ``Provider`` instance for offline testing — no
        API key required.
    guard : bool, optional
        When ``True`` (default), guard thresholds from ``_PARAM_REGISTRY`` are
        applied.  When ``False``, no guard check is performed.
    _run_method : callable or None
        Test seam: replaces the real fdars run_method (same seam as
        ``run_tuning_loop``).  Allows offline testing without the MCP registry.
    _build_diagnostics : callable or None
        Test seam: replaces the real ``build_diagnostics``.
    **initial_params
        Starting param values.  When omitted the default from ``_PARAM_REGISTRY``
        is used for the tunable scalar (e.g. ``n_basis=15`` for smoothing).

    Returns
    -------
    TuneResult
        Complete result including the ``TuningTrace`` (all steps) and summary
        fields: ``improved``, ``initial_target_value``, ``final_target_value``,
        ``improvement_pct``.

    Raises
    ------
    ValueError
        When ``method`` is not in ``_PARAM_REGISTRY`` or is not tuneable
        (e.g. ``"alignment"`` or ``"depth"``).
    """
    # Deferred imports — LLM-free at module load (TUNE-01, T-53A-04)
    from fdars.advisor._tuning import (  # noqa: PLC0415
        _PARAM_REGISTRY,
        _UnparseableProposalError,
        _is_improvement,
        run_tuning_loop,
    )
    from fdars.advisor._schema import TuneResult  # noqa: PLC0415

    method_lc = method.lower().strip()

    # WR-04: validate max_steps before any fdars call (max_steps=0 would
    # produce zero steps and then hit a TypeError on list-valued metrics in
    # the initial_target fallback path).
    if max_steps < 1:
        raise ValueError(
            f"auto_tune: max_steps must be >= 1, got {max_steps}."
        )

    # ------------------------------------------------------------------
    # Validate method and resolve spec
    # ------------------------------------------------------------------
    if method_lc not in _PARAM_REGISTRY:
        raise ValueError(
            f"auto_tune: method {method!r} not in _PARAM_REGISTRY. "
            f"Supported: {sorted(_PARAM_REGISTRY)!r}."
        )
    spec = _PARAM_REGISTRY[method_lc]
    if not spec.get("tuneable", False):
        raise ValueError(
            f"auto_tune: {method!r} is not tuneable. "
            f"Reason: {spec.get('reason', 'no reason given')}."
        )

    # ------------------------------------------------------------------
    # Resolve target_metric and guard_thresholds from spec
    # ------------------------------------------------------------------
    if target_metric is None:
        target_metric = spec["target_metric"]

    guard_thresholds = spec.get("guard_metrics") if guard else None

    # ------------------------------------------------------------------
    # Resolve initial_params (caller override or spec default)
    # ------------------------------------------------------------------
    param_name = spec["param"]
    if param_name not in initial_params:
        initial_params = {param_name: spec["default"], **initial_params}

    # ------------------------------------------------------------------
    # Build intercepting build_diagnostics to share current_diag with
    # the LLM propose_fn closure (avoids a double fdars call each step).
    # ------------------------------------------------------------------
    _current_diag_holder: "list" = [None]

    if _build_diagnostics is not None:
        _real_build_diagnostics = _build_diagnostics
    else:
        # deferred import — offline tests inject _build_diagnostics instead
        _real_build_diagnostics = build_diagnostics

    def _intercepting_build(result, _method, argvals=None, **kwargs):
        diag = _real_build_diagnostics(result, _method, argvals=argvals, **kwargs)
        _current_diag_holder[0] = diag
        return diag

    # ------------------------------------------------------------------
    # Build the LLM propose_fn closure (grounding-invariant hard boundary)
    # ------------------------------------------------------------------
    param_range = spec["range"]
    param_type = spec["param_type"]

    def _llm_propose_fn(current_params, history):
        """LLM propose_fn: calls advise(task='parameter_proposal'), extracts +
        clamps Recommendation.parameter_delta.new_value.

        Raises _UnparseableProposalError when:
          - no Recommendation has a non-None parameter_delta
          - parameter_delta.param does not match spec['param']
          - parameter_delta.new_value is not numeric (TypeError/ValueError)

        On out-of-range new_value: clamps to spec['range'], does NOT exit.
        The LLM is called exactly once per step — no retry on bad proposal.
        """
        current_diag = _current_diag_holder[0]
        if current_diag is None:
            raise _UnparseableProposalError(
                "auto_tune: current diagnostics not available for LLM proposal."
            )

        # Build user content: current diagnostics ONLY in the Diagnostics block
        # (Pitfall 1: history is outside the Diagnostics block so _check_grounding
        # only sees current_diag numbers)
        current_val = current_params.get(param_name, spec["default"])
        lo, hi = param_range
        user_history_section = ""
        if history:
            import json as _json  # noqa: PLC0415
            user_history_section = (
                "\n\nTuning history (reference only — do NOT cite these values "
                "as evidence; cite only values from the Diagnostics section below):\n"
                + _json.dumps(history, indent=2)
            )
        user_addendum = (
            f"\n\nTuning context: adjusting parameter '{param_name}' for method '{method_lc}'.\n"
            f"Current value: {current_val}. Valid range: [{lo}, {hi}].\n"
            f"Target metric: '{target_metric}'."
            + user_history_section
        )

        # advise() builds the user message as:
        #   f"Domain context: {domain_context}\n\nTask: {task}\n\n"
        #   "Diagnostics (reason only from these values):\n" + json.dumps(diagnostics)
        # Our addendum goes into domain_context so it appears BEFORE the diagnostics
        # block — this keeps the history numbers outside the Diagnostics section
        # that _check_grounding reads.
        effective_domain_context = (
            domain_context + user_addendum if domain_context
            else user_addendum.lstrip()
        )

        advice = advise(
            current_diag,
            task="parameter_proposal",
            domain_context=effective_domain_context,
            model=model,
            provider=provider,
            aspect=method_lc,
        )

        # Extract the first Recommendation with a valid parameter_delta for our param
        for rec in advice.recommendations:
            if rec.parameter_delta is None:
                continue
            pd = rec.parameter_delta
            if pd.param != param_name:
                # Wrong param name — exit with parse_failure (no retry)
                raise _UnparseableProposalError(
                    f"auto_tune: LLM proposed param {pd.param!r} "
                    f"but expected {param_name!r}. Exiting with parse_failure."
                )
            # Validate new_value is numeric
            try:
                raw_val = float(pd.new_value)
            except (TypeError, ValueError) as exc:
                raise _UnparseableProposalError(
                    f"auto_tune: parameter_delta.new_value is not numeric: "
                    f"{pd.new_value!r}. Exiting with parse_failure."
                ) from exc

            # Clamp to declared range (T-53B-02: out-of-range → clamp, not reject)
            clamped = max(lo, min(hi, raw_val))
            if param_type is int:
                clamped = int(round(clamped))

            return {param_name: clamped}

        # No usable parameter_delta found — exit with parse_failure (no retry)
        raise _UnparseableProposalError(
            "auto_tune: LLM returned no usable parameter_delta. "
            "Exiting with parse_failure."
        )

    # ------------------------------------------------------------------
    # Run the loop core
    # ------------------------------------------------------------------
    trace = run_tuning_loop(
        dataset_id=dataset_id,
        method=method_lc,
        initial_params=initial_params,
        target_metric=target_metric,
        propose_fn=_llm_propose_fn,
        max_steps=max_steps,
        guard_thresholds=guard_thresholds,
        propose_fn_label="llm",
        _run_method=_run_method,
        _build_diagnostics=_intercepting_build,
    )

    # ------------------------------------------------------------------
    # Assemble TuneResult
    # ------------------------------------------------------------------
    if trace.steps:
        initial_target = trace.steps[0].target_before
    else:
        # WR-04 fix: fallback when no steps were recorded (e.g. max_steps=0
        # path — validated below but guard here defensively).  For list-valued
        # metrics (fpca cumulative_variance_explained) extract the last element
        # before arithmetic so we don't hit TypeError.
        raw = trace.final_diagnostics.get(target_metric, 0.0)
        if isinstance(raw, (list, tuple)):
            raw = raw[-1] if raw else 0.0
        initial_target = float(raw)
    final_target = trace.final_diagnostics.get(target_metric, initial_target)
    # For list-valued metrics (e.g. cumulative_variance_explained), extract scalar
    if isinstance(final_target, list):
        final_target = final_target[-1] if final_target else initial_target

    from fdars.advisor._compare_methods import _METRIC_REGISTRY  # noqa: PLC0415
    target_direction = _METRIC_REGISTRY[target_metric]  # already validated in run_tuning_loop
    improved = _is_improvement(final_target, initial_target, target_direction)

    # WR-01 fix: improvement_pct is sign-aware — positive always means improvement.
    # For "lower"-direction metrics a real improvement means final < initial, so the
    # raw arithmetic difference is negative; we negate to make positive = better.
    improvement_pct: "float | None" = None
    if initial_target != 0.0:
        raw_pct = (final_target - initial_target) / abs(initial_target) * 100.0
        improvement_pct = raw_pct if target_direction == "higher" else -raw_pct

    return TuneResult(
        trace=trace,
        improved=improved,
        initial_target_value=float(initial_target),
        final_target_value=float(final_target),
        improvement_pct=improvement_pct,
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
