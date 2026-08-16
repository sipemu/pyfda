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
# Per-aspect FDA primer clauses (Phase 21, ASPECT-06)
# ---------------------------------------------------------------------------

# Each entry is a short FDA-primer clause string specific to one analysis
# aspect.  _system_prompt appends the matching clause (or nothing for "") after
# the shared FDA-primer block and before the task clause.  Using "" as the key
# would return "" via .get("", ""), so aspect="" reproduces prior behavior
# exactly — no entry for "" is intentional.
_ASPECT_PRIMERS: dict = {
    "depth": (
        "- Functional depth: measures how central each curve is relative to the "
        "sample. High depth = central/representative curve. "
        "Low depth = peripheral/outlier-like curve. "
        "depth_q10 is the 10th percentile of depth scores; a low depth_q10 "
        "value indicates many peripheral curves in the sample.\n"
    ),
    "outliers": (
        "- Functional outlier detection: outlier_fraction is the proportion "
        "flagged. A threshold derived from the null distribution (LRT) or a "
        "geometrical criterion (outliergram). "
        "magnitude outlyingness captures amplitude-direction outliers; "
        "shape outlyingness captures shape-direction outliers.\n"
    ),
    "classification": (
        "- Functional classification: accuracy is the proportion correctly "
        "classified. error_rate = 1 - accuracy. fold_error_std measures "
        "instability across CV folds. best_ncomp is the number of FPC components "
        "that minimises CV error.\n"
    ),
    "alignment": (
        "- Functional alignment registration quality: three fdars scores summarise "
        "how well the curves were registered. "
        "least_squares_score (lower is better): mean L2 spread of registered curves "
        "around their cross-sectional mean — a high value indicates residual "
        "amplitude variation after alignment. "
        "pairwise_correlation_score (higher is better, range ≈ [-1, 1]): mean "
        "functional Pearson correlation across all pairs — values near 1 indicate "
        "well-aligned shape agreement. "
        "sobolev_score (lower is better, lambda_=0.0): identical to "
        "least_squares_score when lambda_ is 0; increases with lambda_ to "
        "penalise highly oscillatory warps.\n"
    ),
    "represent": (
        "- Functional data representation: n_points is the number of evaluation "
        "grid points per curve. is_uniform_grid indicates whether the argvals "
        "spacing is regular. Sparse grids (n_points < 20) and irregular grids "
        "may require pre-smoothing before group-level analysis. "
        "imputed_fraction is the fraction of data cells that were NaN and "
        "subsequently imputed; a high imputed_fraction (> 0.2) indicates the "
        "representation relies heavily on imputed values and downstream results "
        "should be interpreted cautiously. "
        "imputation_mae is the fdars-computed functional mean absolute error "
        "between the original observed cells and the imputed reconstruction; "
        "a non-zero imputation_mae means the imputer altered observed values "
        "and larger values indicate less consistent imputation.\n"
    ),
    "regression": (
        "- Functional regression: r_squared measures goodness-of-fit (0-1). "
        "residual_skew > 0 indicates right-skewed residuals; large "
        "residual_max_abs may flag influential outlier observations. "
        "beta_t is the functional coefficient curve; beta_t_range summarises "
        "its magnitude.\n"
    ),
    "regression_cv": (
        "- Functional regression CV: optimal_k is the number of FPC components "
        "minimising CV error. elbow_present indicates whether the CV curve has a "
        "clear minimum away from the boundary. If optimal_k is at the k_max "
        "boundary, more components should be tested.\n"
    ),
    "spm": (
        "- Functional SPM Phase I: t2_exceedance_rate is the fraction of "
        "in-control observations exceeding the T² limit; for a "
        "well-calibrated chart this should approximately equal the design alpha. "
        "spe_kurtosis_excess from spe_moment_match_diagnostic measures departure "
        "of SPE from the moment-matched chi-squared approximation -- high values "
        "indicate the approximation is inadequate. "
        "variance_explained_cumulative shows how much variation the chosen ncomp "
        "components capture.\n"
    ),
    "scoring": (
        "- Functional prediction scoring: five fdars metrics measure prediction "
        "quality. functional_mae (mean absolute error) and functional_mse (mean "
        "squared error) penalise large pointwise deviations; functional_mse "
        "is more sensitive to outlier curves because errors are squared. "
        "functional_mape (mean absolute percentage error) is scale-free but "
        "inflates when true values are near zero. functional_msle (mean squared "
        "log error) penalises under-prediction more than over-prediction. "
        "functional_explained_variance measures the fraction of functional "
        "variance captured by the model: high >= 0.9, moderate 0.5-0.9, "
        "low < 0.5. largest_error_metric names the metric with the highest "
        "absolute value among the present error metrics; explained_variance_band "
        "gives the qualitative band derived from functional_explained_variance.\n"
    ),
}


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _system_prompt(task: str, aspect: str = "") -> str:
    """Build the grounded-output system prompt for the given task family.

    The base prompt encodes the grounding invariant (via ``_GROUNDING_INVARIANT``)
    and an FDA primer.  A per-aspect clause (from ``_ASPECT_PRIMERS``) is
    appended after the FDA primer when ``aspect`` is non-empty.  A task-family
    clause is appended last based on ``task``.

    Parameters
    ----------
    task : str
        Task family identifier (case-insensitive).  Supported:
        ``"interpretation"``, ``"parameter"``, ``"method"``.
    aspect : str, optional
        Selects the per-aspect FDA primer clause from ``_ASPECT_PRIMERS``
        (e.g. ``"depth"``, ``"outliers"``).  Default ``""`` reproduces
        prior behavior exactly — no aspect clause is added (ASPECT-06).

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

    # -- Per-aspect primer clause (Phase 21, ASPECT-06) ---------------------
    # Appended after FDA primer, before task clause.  aspect="" returns ""
    # from .get so this block is a no-op for default callers.
    aspect_primer = _ASPECT_PRIMERS.get(aspect.lower(), "")
    base = base + aspect_primer

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
