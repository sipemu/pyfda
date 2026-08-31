"""Coverage registry for the fdars sklearn layer.

``EXCLUDED_METHODS`` records fdars methods that are NOT wrapped as sklearn
estimators because they have a structural mismatch with the sklearn contract.
Each entry uses reason codes defined below.

``TRIAGE_VERDICTS`` maps skeleton estimator class names to their compliance
verdict after the Phase 55 triage run.  Populated in Plan 03 once
``parametrize_with_checks`` results are available.

Reason codes
------------
ORDER_SENSITIVE
    The method's output depends on sample ordering within the batch; violates
    ``check_methods_subset_invariance``.
IRREGULAR_INPUT
    The method requires irregular functional data (``IrregFdata``), not a plain
    ``(n_obs, n_points)`` ndarray.
RESPONSE_DOMAIN
    The method's response domain constraints (e.g. y in {0,1}) are violated by
    the arbitrary arrays that ``check_estimators_dtypes`` supplies.
NON_STANDARD_INPUT
    The method's input type is a non-standard container (list-of-matrices,
    paired arrays) that cannot be expressed as a single 2D ndarray.
NON_STANDARD_OUTPUT
    The method returns a 2D or non-scalar output (e.g. functional response)
    that is incompatible with ``RegressorMixin.score()`` and
    ``check_estimators_dtypes``.
HYPERPARAMETER_SEARCH
    The method IS itself a hyperparameter search; nesting it inside sklearn's
    ``GridSearchCV`` is structurally wrong.
NOT_AN_ESTIMATOR
    The method is a statistical test or inferential procedure with no
    fit/predict/transform contract.
SEQUENTIAL_STREAMING
    The method is a stateful streaming algorithm; it cannot be cast to the
    stateless batch fit/transform pattern.
"""

# ---------------------------------------------------------------------------
# Pre-excluded methods (no skeleton written; excluded before triage)
# ---------------------------------------------------------------------------

EXCLUDED_METHODS: dict[str, dict] = {
    # --- Alignment (registration) ---
    "alignment.elastic_registration": {
        "reason": "ORDER_SENSITIVE",
        "failing_check": "check_methods_subset_invariance",
        "functional_api": "fdars.alignment.elastic_registration",
    },
    "alignment.karcher_mean": {
        "reason": "ORDER_SENSITIVE",
        "failing_check": "check_methods_subset_invariance",
        "functional_api": "fdars.alignment.karcher_mean",
    },
    # --- FPCA on irregular grids ---
    "pace_fpca.pace_fpca": {
        "reason": "IRREGULAR_INPUT",
        "failing_check": "check_n_features_in",
        "functional_api": "fdars.pace_fpca.pace_fpca",
    },
    # --- Non-Gaussian GLM ---
    "regression.functional_glm_binomial": {
        "reason": "RESPONSE_DOMAIN",
        "failing_check": "check_estimators_dtypes",
        "functional_api": "fdars.regression.functional_glm (family='binomial')",
    },
    "regression.functional_glm_poisson": {
        "reason": "RESPONSE_DOMAIN",
        "failing_check": "check_estimators_dtypes",
        "functional_api": "fdars.regression.functional_glm (family='poisson')",
    },
    # --- Non-standard inputs/outputs ---
    "regression.concurrent_regression": {
        "reason": "NON_STANDARD_INPUT",
        "failing_check": None,  # excluded by design; input is list-of-matrices
        "functional_api": "fdars.regression.concurrent_regression",
    },
    "regression.fosr": {
        "reason": "NON_STANDARD_OUTPUT",
        "failing_check": "check_estimators_dtypes",
        "functional_api": "fdars.regression.fosr",
    },
    # --- Hyperparameter search ---
    "clustering.cluster_optim": {
        "reason": "HYPERPARAMETER_SEARCH",
        "failing_check": None,  # excluded by design; is itself a grid search
        "functional_api": "fdars.clustering.cluster_optim",
    },
    # --- Inference tests ---
    "inference.t_perm_test": {
        "reason": "NOT_AN_ESTIMATOR",
        "failing_check": None,
        "functional_api": "fdars.inference.t_perm_test",
    },
    "inference.f_perm_test": {
        "reason": "NOT_AN_ESTIMATOR",
        "failing_check": None,
        "functional_api": "fdars.inference.f_perm_test",
    },
    "inference.anova_perm_test": {
        "reason": "NOT_AN_ESTIMATOR",
        "failing_check": None,
        "functional_api": "fdars.inference.anova_perm_test",
    },
    "inference.scb": {
        "reason": "NOT_AN_ESTIMATOR",
        "failing_check": None,
        "functional_api": "fdars.inference.scb",
    },
    # --- SPM monitoring ---
    "spm.spm_monitoring": {
        "reason": "SEQUENTIAL_STREAMING",
        "failing_check": None,  # stateful streaming; cannot be batch fit/transform
        "functional_api": "fdars.spm.spm_monitoring",
    },
    # Note: ElasticMultinomialClassifier is a triage candidate, NOT pre-excluded.
    # Triage result lands in TRIAGE_VERDICTS after Plan 03 run.
}

# ---------------------------------------------------------------------------
# Triage verdicts (populated after Phase 55 Plan 03 triage run)
# ---------------------------------------------------------------------------

TRIAGE_VERDICTS: dict[str, str] = {
    # Populated by Plan 03 after parametrize_with_checks results are reviewed.
    # Format: "ClassName": "PASS" | "PASS-WITH-FIXES: <description>" | "EXCLUDE: <reason>"
    #
    # Examples (do not uncomment -- these are placeholders):
    # "FPCATransformer": "PASS",
    # "BSplineSmoother": "PASS-WITH-FIXES: add 1-sample guard",
    # "LRTOutlierDetector": "PASS-WITH-FIXES: add threshold_ attribute",
    # "ElasticMultinomialClassifier": "EXCLUDE: requires >=3 classes; check_estimators_dtypes fails",
}
