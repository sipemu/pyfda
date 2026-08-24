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
        "shape outlyingness captures shape-direction outliers. "
        "For tvdmss: n_magnitude_outliers and n_shape_outliers are the separate "
        "counts of magnitude- and shape-direction outliers; tvd_range and mss_range "
        "are the [min, max] spans of the Total-Variation-Depth and "
        "Modified-Shape-Similarity score vectors. "
        "For muod: n_muod_magnitude_outliers, n_muod_shape_outliers, and n_amplitude_outliers "
        "are the three distinct outlier counts; magnitude_index_range, "
        "shape_index_range, and amplitude_index_range summarise the respective "
        "outlyingness score spans. "
        "For depthgram: n_depthgram_shape_outliers and n_depthgram_magnitude_outliers are the "
        "depthgram-identified counts; depthgram_mbd_range and depthgram_mei_range span the "
        "MBD and MEI depth scores. "
        "For sequential_transform_outliers: n_union_outliers is the size of the "
        "union across all transform stages; n_transforms is the number of "
        "sequential detector stages applied.\n"
    ),
    "classification": (
        "- Functional classification: accuracy is the proportion correctly "
        "classified. error_rate = 1 - accuracy. fold_error_std measures "
        "instability across CV folds. best_ncomp is the number of FPC components "
        "that minimises CV error. "
        "For elastic_multinomial: train_accuracy is the in-sample proportion "
        "correctly classified (distinct from cross-validation accuracy); "
        "train_error_rate = 1 - train_accuracy; n_classes is the fdars-computed "
        "number of classes. "
        "overfitting_gap is the difference between train_accuracy and the "
        "caller-supplied holdout or CV accuracy (a positive value indicates "
        "in-sample overfitting; larger values indicate more severe overfitting); "
        "overfitting_gap is None when no holdout accuracy was supplied. "
        "n_classes_flagged is True when n_classes > 2 (multiclass rather than "
        "binary), derived from the fdars-computed class count. "
        "Only cite values present in the diagnostics; do not supply thresholds "
        "or reference values not present.\n"
    ),
    "fpca": (
        "- Functional PCA (FPCA): n_components is the number of retained components; "
        "cumulative_variance_explained shows the running fraction of total variance "
        "captured. phase_leakage_indicator is the fraction of variance outside the "
        "leading component — high values (> 0.5) suggest phase variation leaking into "
        "the amplitude decomposition. "
        "For PACE-FPCA (sparse/irregular data): pace_sigma2 is the fdars-computed noise "
        "variance. pace_noise_signal_ratio is sigma2 divided by the total signal variance "
        "(sum of PACE eigenvalues) — higher values indicate more noise relative to signal "
        "and lower signal-to-noise ratio; None when total signal variance is zero. "
        "pace_truncated_rank_flagged is True when the fdars-computed ncomp is below the "
        "number of available eigenvalues (the decomposition was truncated below full rank). "
        "pace_mean_prediction_band_width is the mean over all observations and time points "
        "of (fitted_upper - fitted_lower) — wider bands indicate more predictive uncertainty. "
        "Only cite values present in the diagnostics; do not supply thresholds "
        "or reference values not present.\n"
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
        "its magnitude. "
        "For functional_glm: deviance measures model fit (lower = better fit for "
        "the chosen exponential family); aic and bic enable model comparison across "
        "ncomp values (lower = preferred); iterations is the IRLS iteration count "
        "to convergence; family names the exponential-family distribution used. "
        "For concurrent_regression: concurrent_residual_rms is the root-mean-squared "
        "residual over the full n x m grid — a single scalar summary of overall fit "
        "quality; n_predictors is the number of functional predictor curves.\n"
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
    "inference": (
        "- Functional inference: statistic is the fdars-computed test statistic "
        "(e.g. permutation F-statistic or Hotelling T² value); p_value is the "
        "fdars-computed permutation or asymptotic p-value; n_perm is the number "
        "of permutations used. n_perm == 0 denotes an asymptotic test (e.g. "
        "Hotelling T²) while n_perm > 0 denotes a permutation test — "
        "is_permutation_test is the derived boolean flag. "
        "significant_at_0.01 / significant_at_0.05 / significant_at_0.10 are "
        "derived significance flags (p_value < alpha); strongest_significance_level "
        "is the smallest alpha at which the result is significant. "
        "Interpret these values in the context of the study design and sample "
        "size — do not claim significance or non-significance beyond the "
        "p_value and alpha levels already provided. "
        "For ITP (interval-wise testing procedure): the ITP result is reduced to "
        "DETECTION and LOCALISATION scalars — these answer fundamentally different "
        "questions and must be cited together, never in isolation. "
        "DETECTION (whether any interval is significant): itp_min_adjusted_pvalue "
        "is the minimum adjusted p-value over all projection-basis intervals; "
        "itp_detected_at_0.05 is True when itp_min_adjusted_pvalue < 0.05. "
        "Do NOT interpret itp_min_adjusted_pvalue alone as evidence of global "
        "significance — a small minimum p-value may arise from a single localised "
        "interval while the majority of intervals are non-significant. "
        "LOCALISATION (where and how many intervals are significant): "
        "itp_n_significant_0.05 is the count of basis intervals with adjusted "
        "p-value below 0.05; itp_fraction_significant_0.05 is the proportion "
        "(count / n_basis); itp_first_significant_basis is the index of the first "
        "significant interval (None when none are significant). "
        "Always cite itp_n_significant_0.05 and itp_fraction_significant_0.05 "
        "alongside itp_min_adjusted_pvalue when describing ITP results — "
        "localisation (where significance occurs) is distinct from detection "
        "(whether any significance occurs). "
        "Only cite values present in the diagnostics; do not supply thresholds "
        "or reference values not present.\n"
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
    _supported_tasks = {"interpretation", "parameter", "method", "comparison"}
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

    elif task_lc == "comparison":
        # COMPARE-02: comparison task family — narrates the fdars-computed ranking.
        # The winner and ranking are ALREADY DECIDED by fdars; the model explains,
        # it does NOT select the winner.
        task_clause = (
            "Task: comparison.\n"
            "The ranking and winner supplied in the user message are already "
            "decided by fdars deterministic computation — you narrate and explain "
            "the ranking, you do NOT choose or re-rank the candidates. "
            "For each candidate in the ranking, explain WHY it ranks where it does "
            "by citing that candidate's own diagnostic values from the labeled "
            "diagnostics block provided for it. "
            "Reference each candidate by its explicit label exactly as supplied. "
            "When discussing a candidate, cite only values present in that "
            "candidate's own diagnostics block — do not cite a value from one "
            "candidate's block as evidence for a claim about a different candidate. "
            "The winner field in the user message identifies the best candidate "
            "per the fdars sort; do not claim any other candidate is the winner. "
            "Set recommendation kind to 'none' unless a concrete follow-up action "
            "is clearly warranted by one candidate's diagnostics. "
            "Only cite values present in the candidate's own diagnostics; do not "
            "supply thresholds or reference values not present in the diagnostics."
        )

    return base + "\n" + task_clause
