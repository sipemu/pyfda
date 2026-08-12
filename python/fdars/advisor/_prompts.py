"""fdars.advisor._prompts — System-prompt builder and grounding invariant.

Contains the ``_GROUNDING_INVARIANT`` constant (the single canonical
grounding-invariant sentence) and ``_system_prompt()`` (the full system prompt
for the Claude API calls made by :func:`~fdars.advisor.advise`).

Importing this module never touches the anthropic SDK, never opens a network
connection, and never imports any other fdars.advisor submodule.

Grounding-invariant note (T-19-04)
-----------------------------------
``_GROUNDING_INVARIANT`` is the one canonical copy of the sentence that tells
the LLM to reason only from provided diagnostics.  ``_system_prompt`` embeds
it via string interpolation so there is exactly one definition of the
invariant.  The user-facing diagnostics label in ``advise()``
("Diagnostics (reason only from these values):") is a distinct user-content
label in a different file and a different context — it is intentionally NOT
part of the system-prompt invariant and therefore not deduplicated here.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Grounding invariant (T-19-04 — single canonical constant)
# ---------------------------------------------------------------------------

# This is the one authoritative copy of the sentence that instructs the model
# to reason only from the diagnostics supplied.  _system_prompt is built from
# this constant so the invariant text can never silently diverge between the
# constant and the prompt.
_GROUNDING_INVARIANT = (
    "You reason only from the diagnostics provided in the user message."
)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _system_prompt(task: str, aspect: str = "") -> str:
    """Build the grounded-output system prompt for the given task family.

    The base prompt encodes the grounding invariant (via ``_GROUNDING_INVARIANT``)
    and an FDA primer.  A task-family clause is appended based on ``task``.

    Parameters
    ----------
    task : str
        Task family identifier (case-insensitive).  Supported:
        ``"interpretation"``, ``"parameter"``, ``"method"``.
    aspect : str, optional
        Reserved for Phase 21 per-aspect specialisation.  Unused today;
        accepted so callers can pass it without error.

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
        f"{_GROUNDING_INVARIANT} "
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
    _supported_tasks = {"interpretation", "parameter", "method"}
    if task_lc not in _supported_tasks:
        raise ValueError(
            f"_system_prompt: unsupported task {task!r}. "
            f"Supported: {sorted(_supported_tasks)!r}."
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

    elif task_lc == "parameter":
        # ADVISE-02: parameter guidance grounded in diagnostics.
        task_clause = (
            "Task: parameter.\n"
            "Recommend concrete parameter adjustments for the fdars method. "
            "The parameters you may recommend adjusting are: "
            "lambda_ (warp penalty / smoothing regularisation), "
            "n_basis (number of basis functions), "
            "bandwidth (kernel smoother bandwidth), "
            "n_comp (number of FPCA components), "
            "cluster k (number of clusters), "
            "depth method (which functional depth measure to use). "
            "For each recommendation: "
            "set kind='parameter'; "
            "state a concrete action with a target value or direction "
            "(e.g. 'increase lambda_ from the current value toward 1.0', "
            "'reduce n_basis to the value at the GCV minimum'); "
            "tie the rationale to a specific diagnostic value "
            "(e.g. the GCV curve minimum, the cumulative variance explained, "
            "the warp penalty, the cluster separation); "
            "state the expected_effect in terms of the next run's diagnostics. "
            "Evidence must cite the specific diagnostic value(s) that motivate "
            "the recommendation — do not cite values absent from the input. "
            "Only recommend changes that are clearly supported by the diagnostics."
        )

    elif task_lc == "method":
        # ADVISE-03: method guidance — flag poor-fit methods, suggest alternatives.
        task_clause = (
            "Task: method.\n"
            "Identify when the chosen fdars method is a poor fit for the data "
            "and recommend an alternative. Use the following mappings:\n"
            "- Linear/vertical FPCA + substantial phase variation "
            "(high phase_leakage_indicator or variance concentrated in higher "
            "components) -> recommend elastic FPCA (amplitude/phase decomposition) "
            "to separate amplitude and phase variation before decomposition.\n"
            "- Sparse or irregularly sampled data (irregular argvals spacing, "
            "few observations per curve) -> recommend pre-smoothing to a common "
            "grid before any group-level analysis.\n"
            "- Density-valued, compositional, or strictly positive/constrained data "
            "-> recommend transforming to an unconstrained space "
            "(e.g. log-ratio, Bayes-Hilbert) before applying standard FDA methods.\n"
            "For each recommendation: "
            "set kind='method'; "
            "name the current method and why it is a poor fit; "
            "name the alternative method and what it addresses; "
            "state the expected_effect (what should improve in subsequent analysis). "
            "Evidence must cite the specific diagnostic value(s) that flag the "
            "poor-fit signal (e.g. phase_leakage_indicator value, "
            "cumulative variance pattern, cluster separation). "
            "Only flag a method mismatch when the diagnostics clearly support it."
        )

    return base + "\n" + task_clause
