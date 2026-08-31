"""Coverage registry for the fdars sklearn layer.

``EXCLUDED_METHODS`` records fdars methods that are NOT wrapped as sklearn
estimators because they have a structural mismatch with the sklearn contract.
Each entry uses reason codes defined below.

``TRIAGE_VERDICTS`` maps skeleton estimator class names to their compliance
verdict after the Phase 55 triage run.  Populated in Plan 03 from
``triage_results.txt`` (sklearn 1.8.0 / Python 3.14, 1379 checks,
1272 PASS / 107 FAIL across 28 estimators).

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
LABEL_DOMAIN
    The native function enforces a strict label domain (e.g. exactly {0.0,
    1.0}) that sklearn's check battery violates with arbitrary integer labels.
ACCURACY_STRUCTURAL
    The skeleton's re-fit-at-predict design cannot achieve the accuracy
    threshold required by ``check_regressors_train`` or
    ``check_classifiers_train``; structural redesign (stored model) required.
OUTLIER_SCORE_STRUCTURAL
    The outlier-detection skeleton always predicts +1 on the training set
    (no inlier/outlier split in the small battery data); ``check_outliers_train``
    / ``check_outliers_fit_predict`` require both {-1, 1} in predictions.
MISSING_DECISION_FUNCTION
    The skeleton exposes ``score_samples`` but not ``decision_function``; the
    ``OutlierMixin`` contract requires ``decision_function`` for
    ``check_outliers_train``.  Fix: add ``decision_function = score_samples``.
NATIVE_ORDER_SENSITIVE
    The underlying native call re-fits on the combined (train + test) dataset;
    predictions on a subset of the test set differ from predictions on the full
    test set, violating ``check_methods_subset_invariance``.
UNFITTED_CHECK_MISSING
    The skeleton does not call ``check_is_fitted`` before ``predict``; the
    ``check_estimators_unfitted`` check expects ``NotFittedError``.
INVALID_ARGVALS_CONSTRAINT
    The native function requires ``argvals`` length >= 2; sklearn's
    ``check_fit2d_1feature`` passes a single-column matrix and expects a
    sklearn-convention error message containing "1 feature(s)" / "n_features=1".
"""

# ---------------------------------------------------------------------------
# Pre-excluded methods (no skeleton written; excluded before triage)
# ---------------------------------------------------------------------------

EXCLUDED_METHODS: dict[str, dict] = {
    # --- Alignment (registration) ---
    # elastic_registration does not exist as a standalone function; the elastic
    # registration workflow uses elastic_align_pair / karcher_mean separately.
    "alignment.elastic_align_pair": {
        "reason": "ORDER_SENSITIVE",
        "failing_check": "check_methods_subset_invariance",
        "functional_api": "fdars.alignment.elastic_align_pair",
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
        "functional_api": "fdars.regression.functional_glm",
    },
    "regression.functional_glm_poisson": {
        "reason": "RESPONSE_DOMAIN",
        "failing_check": "check_estimators_dtypes",
        "functional_api": "fdars.regression.functional_glm",
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
    "inference.oneway_anova_vstat": {
        "reason": "NOT_AN_ESTIMATOR",
        "failing_check": None,
        "functional_api": "fdars.inference.oneway_anova_vstat",
    },
    "inference.mean_scb": {
        "reason": "NOT_AN_ESTIMATOR",
        "failing_check": None,
        "functional_api": "fdars.inference.mean_scb",
    },
    # --- SPM monitoring ---
    "spm.spm_monitor": {
        "reason": "SEQUENTIAL_STREAMING",
        "failing_check": None,  # stateful streaming; cannot be batch fit/transform
        "functional_api": "fdars.spm.spm_monitor",
    },
    # ---------------------------------------------------------------------------
    # Triage-discovered excludes (empirically from triage_results.txt)
    # ---------------------------------------------------------------------------
    # SplineInterpolator: 13 failing checks; native spline_interpolate enforces
    # order in [1, 3) but sklearn's battery passes order=4 via dtype cycling;
    # combined non-idempotency, non-subset-invariance, and pickle failures are
    # all rooted in the output_argvals design -- structural incompatibility.
    "represent.spline_interpolate": {
        "reason": "NON_STANDARD_INPUT",
        "failing_check": "check_fit_score_takes_y",
        "functional_api": "fdars.represent.spline_interpolate",
    },
    # LogisticFPCClassifier: 21 failing checks; native functional_logistic
    # enforces y in {0.0, 1.0} exactly; sklearn battery uses arbitrary integer
    # labels (0, 1, 2, -1, etc.).  All failures trace to this label domain
    # constraint -- structural incompatibility.
    "regression.functional_logistic": {
        "reason": "LABEL_DOMAIN",
        "failing_check": "check_estimators_fit_returns_self",
        "functional_api": "fdars.regression.functional_logistic",
    },
    # ElasticMultinomialClassifier: 10 failing checks; multiple structural
    # issues: unfitted check (missing check_is_fitted), accuracy failure on
    # sklearn battery data, methods_subset_invariance violation from vstack
    # re-fit, native requires argvals length >= 2.
    "classification.elastic_multinomial": {
        "reason": "UNFITTED_CHECK_MISSING",
        "failing_check": "check_estimators_unfitted",
        "functional_api": "fdars.classification.elastic_multinomial",
    },
    # LRTOutlierDetector: 3 failing checks; per-obs augment-and-re-detect
    # approach always classifies training data as inliers (returns only +1),
    # violating check_outliers_train / check_outliers_fit_predict which require
    # both {-1, 1} present.  Non-deterministic and slow in CI.
    "outliers.detect_outliers_lrt_with_dist": {
        "reason": "OUTLIER_SCORE_STRUCTURAL",
        "failing_check": "check_outliers_fit_predict",
        "functional_api": "fdars.outliers.detect_outliers_lrt_with_dist",
    },
    # MUODDetector: 3 failing checks; missing decision_function (structural --
    # requires OutlierMixin wiring) and native muod requires >= 2 columns
    # (check_fit2d_1feature exposes wrong error message string).
    "outliers.muod": {
        "reason": "MISSING_DECISION_FUNCTION",
        "failing_check": "check_outliers_train",
        "functional_api": "fdars.outliers.muod",
    },
    # GLMRegressor: 6 failing checks; re-fit-at-predict on vstack causes
    # non-idempotent predictions (check_methods_subset_invariance),
    # missing n_iter_, and accuracy below 0.5 threshold.  Structural:
    # a stored-model design would be needed for compliance.
    "regression.functional_glm": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_regressors_train",
        "functional_api": "fdars.regression.functional_glm",
    },
    # NonparametricRegressor: 4 failing checks; re-fit on vstack causes
    # predictions on a subset to differ from predictions on the full set
    # (check_methods_subset_invariance) and accuracy fails check_regressors_train.
    "regression.fregre_np": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_regressors_train",
        "functional_api": "fdars.regression.fregre_np",
    },
    # FPCRegressor: 4 failing checks; re-fit-at-predict on vstack pattern
    # cannot achieve R2 > 0.5 on sklearn battery data; structurally the same
    # re-fit accuracy gap as GLMRegressor.
    "regression.fregre_lm": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_regressors_train",
        "functional_api": "fdars.regression.fregre_lm",
    },
    # RobustFPCRegressor: 4 failing checks; same re-fit accuracy structural
    # failure as FPCRegressor (fregre_l1 / fregre_huber).
    "regression.fregre_l1": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_regressors_train",
        "functional_api": "fdars.regression.fregre_l1",
    },
    # FPCLDAClassifier: 6 failing checks; vstack re-fit pattern causes
    # accuracy < 0.83 threshold (check_classifiers_train) and subset
    # invariance violation; also missing label-type validation.
    "classification.fclassif_lda": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_classifiers_train",
        "functional_api": "fdars.classification.fclassif_lda",
    },
    # FPCQDAClassifier: same structural failures as FPCLDAClassifier.
    "classification.fclassif_qda": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_classifiers_train",
        "functional_api": "fdars.classification.fclassif_qda",
    },
    # DDClassifier: same vstack + accuracy structural failures.
    "classification.fclassif_dd": {
        "reason": "ACCURACY_STRUCTURAL",
        "failing_check": "check_classifiers_train",
        "functional_api": "fdars.classification.fclassif_dd",
    },
    # MagnitudeShapeDetector: 4 failing checks; always predicts +1 on small
    # battery data (check_outliers_train / check_outliers_fit_predict),
    # plus 1-sample crash in check_methods_subset_invariance (native requires
    # >= 2 rows) -- structural scoring mismatch.
    "outliers.magnitude_shape": {
        "reason": "OUTLIER_SCORE_STRUCTURAL",
        "failing_check": "check_outliers_fit_predict",
        "functional_api": "fdars.outliers.magnitude_shape",
    },
}

# ---------------------------------------------------------------------------
# Triage verdicts (populated after Phase 55 Plan 03 -- triage_results.txt)
# ---------------------------------------------------------------------------
# Source: triage_results.txt (sklearn 1.8.0 / Python 3.14)
# 28 estimators, 1379 checks total: 1272 PASSED, 107 FAILED
#
# Verdict rules applied:
#   PASS            -- zero failing checks
#   PASS-WITH-FIXES -- all failures fixable with a guard/wrapper/attribute add
#   EXCLUDE         -- at least one failure from structural incompatibility
#
# Format: "ClassName": "<VERDICT>[: <note>]"
# ---------------------------------------------------------------------------

TRIAGE_VERDICTS: dict[str, str] = {
    # -----------------------------------------------------------------------
    # TRANSFORMERS
    # -----------------------------------------------------------------------
    # 0 failures (47/47 checks)
    "FPCATransformer": "PASS",
    # 0 failures (47/47 checks)
    "BSplineSmoother": "PASS",
    # 0 failures (47/47 checks)
    "LocalPolynomialSmoother": "PASS",
    # 1 failure: check_fit2d_1feature -- native emits wrong error message;
    # fixable by adding a Python-layer 1-feature guard with sklearn-convention
    # message ("1 feature(s)" substring required).
    "BasisRepresentation": "PASS-WITH-FIXES: add 1-feature guard emitting sklearn-convention message",
    # 4 failures: check_dtype_object + 3 sparse checks (check_estimator_sparse_tag,
    # check_estimator_sparse_array, check_estimator_sparse_matrix).
    # Root cause: ensure_all_finite / force_all_finite compat shim is incomplete
    # for the NaN-path when dtype=object or sparse input arrives.
    # Fixable: extend shim to use ensure_all_finite="allow-nan" (1.8+) in
    # both fit branches; add accept_sparse=False to validate_data call.
    "Imputer": "PASS-WITH-FIXES: complete ensure_all_finite compat shim + accept_sparse=False",
    # 13 failures: ALL trace to native spline_interpolate enforcing order in
    # [1, 3) while sklearn's battery constructs float32/float64 variants with
    # order up to 4; combined with non-idempotency (fit changes output_argvals_
    # so second transform on same X differs) and subset invariance violation.
    # Structural -- requires native API change or fixed-order design.
    "SplineInterpolator": "EXCLUDE: native order constraint [1,3) + non-idempotent output_argvals_ design; check_fit_score_takes_y",
    # 0 failures (47/47 checks)
    "DepthTransformer": "PASS",
    # 0 failures (47/47 checks)
    "NormTransformer": "PASS",

    # -----------------------------------------------------------------------
    # REGRESSORS
    # -----------------------------------------------------------------------
    # 4 failures: check_regressors_train x3 (R2 <= 0.5) + check_requires_y_none.
    # Root cause: re-fit-at-predict on vstack([X_fit_, X_new]) achieves poor
    # accuracy on sklearn's battery data (random Gaussian, 1 component).
    # Structural -- a stored-model predict (no refit) is required.
    "FPCRegressor": "EXCLUDE: re-fit-at-predict pattern; check_regressors_train (R2 <= 0.5)",
    # 1 failure: check_requires_y_none -- wrong error message when y=None.
    # Fixable: add explicit None check emitting required sklearn message.
    "PLSRegressor": "PASS-WITH-FIXES: add y=None guard with sklearn-convention error message",
    # 4 failures: same re-fit accuracy structural failure as FPCRegressor.
    "RobustFPCRegressor": "EXCLUDE: re-fit-at-predict pattern; check_regressors_train (R2 <= 0.5)",
    # 6 failures: check_regressors_train x3 (R2 <= 0.5) + check_non_transformer_estimators_n_iter
    # (missing n_iter_) + check_methods_subset_invariance (re-fit makes subset
    # predictions differ) + check_requires_y_none. Structural re-fit design.
    "GLMRegressor": "EXCLUDE: re-fit-at-predict non-idempotent; check_regressors_train + check_methods_subset_invariance",
    # 4 failures: check_regressors_train x3 (R2 <= 0.5) + check_methods_subset_invariance
    # (distance-based re-fit on vstack makes predictions context-dependent) +
    # check_requires_y_none. Structural.
    "NonparametricRegressor": "EXCLUDE: distance-based re-fit; check_regressors_train + check_methods_subset_invariance",

    # -----------------------------------------------------------------------
    # CLASSIFIERS
    # -----------------------------------------------------------------------
    # 6 failures: check_classifiers_train x3 (accuracy < 0.83) +
    # check_classifiers_regression_target (no label-type validation) +
    # check_methods_subset_invariance (vstack predict always returns class 0) +
    # check_requires_y_none. Structural vstack accuracy failure.
    "FPCLDAClassifier": "EXCLUDE: vstack re-fit; check_classifiers_train (accuracy < 0.83) + check_methods_subset_invariance",
    # Same structural failures as FPCLDAClassifier.
    "FPCQDAClassifier": "EXCLUDE: vstack re-fit; check_classifiers_train (accuracy < 0.83) + check_methods_subset_invariance",
    # 2 failures: check_classifiers_regression_target (no label-type validation) +
    # check_requires_y_none (wrong error message). Fixable guards.
    "FPCKNNClassifier": "PASS-WITH-FIXES: add label-type validation (check_type_of_target) + y=None guard",
    # 6 failures: same vstack re-fit accuracy structural failure as FPCLDAClassifier.
    "DDClassifier": "EXCLUDE: vstack re-fit; check_classifiers_train (accuracy < 0.83) + check_methods_subset_invariance",
    # 21 failures: native functional_logistic enforces y in {0.0, 1.0} exactly;
    # sklearn battery uses arbitrary integer labels (0,1,2,-1,...).  All 21
    # failures trace to this label domain constraint -- structural.
    "LogisticFPCClassifier": "EXCLUDE: native label domain {0.0, 1.0}; check_estimators_fit_returns_self (and 20 others)",
    # 10 failures: missing check_is_fitted call (check_estimators_unfitted) +
    # missing check_fit_check_is_fitted + accuracy failure (check_classifiers_train)
    # + check_methods_subset_invariance (always predicts 0 on subset) +
    # native argvals >= 2 constraint (check_fit2d_1feature) + missing n_iter_.
    # Multiple structural issues.
    "ElasticMultinomialClassifier": "EXCLUDE: missing check_is_fitted + accuracy structural + argvals >= 2; check_estimators_unfitted",

    # -----------------------------------------------------------------------
    # CLUSTERERS
    # -----------------------------------------------------------------------
    # 0 failures (47/47 checks)
    "FunctionalKMeans": "PASS",
    # 1 failure: check_non_transformer_estimators_n_iter (missing n_iter_ attr).
    # Fixable: add self.n_iter_ = 1 (or actual iteration count) in fit().
    "FuzzyFunctionalCMeans": "PASS-WITH-FIXES: add n_iter_ attribute to fit()",
    # 1 failure: check_non_transformer_estimators_n_iter (missing n_iter_ attr).
    # Fixable: add self.n_iter_ = 1 in fit().
    "FunctionalGMM": "PASS-WITH-FIXES: add n_iter_ attribute to fit()",

    # -----------------------------------------------------------------------
    # OUTLIER DETECTORS
    # -----------------------------------------------------------------------
    # 3 failures: check_outliers_fit_predict + check_outliers_train x2.
    # Root cause: per-obs augment-and-re-detect always produces only +1 on
    # battery training data (no outliers detected in small normal sets).
    # Structural: outlier_score_structural.
    "LRTOutlierDetector": "EXCLUDE: always predicts +1 on battery data; check_outliers_fit_predict + check_outliers_train",
    # 2 failures: check_outliers_train x2 (missing decision_function).
    # Fixable: add decision_function = score_samples alias.
    "OutliergramDetector": "PASS-WITH-FIXES: add decision_function = score_samples alias",
    # 4 failures: check_outliers_fit_predict + check_outliers_train x2
    # (always +1) + check_methods_subset_invariance (1-sample crash native).
    # Structural: score synthesis never produces -1 on battery data.
    "MagnitudeShapeDetector": "EXCLUDE: score synthesis always +1 on battery data; check_outliers_fit_predict",
    # 2 failures: check_outliers_train x2 (missing decision_function).
    # Fixable: add decision_function = score_samples alias.
    "TVDMSSDetector": "PASS-WITH-FIXES: add decision_function = score_samples alias",
    # 3 failures: check_outliers_train x2 (missing decision_function) +
    # check_fit2d_1feature (native requires >= 2 cols, wrong error message).
    # Fixable for decision_function; check_fit2d_1feature fixable with guard.
    # Marking PASS-WITH-FIXES: both fixes are guard/attribute adds.
    "MUODDetector": "PASS-WITH-FIXES: add decision_function alias + 1-feature guard with sklearn-convention message",
    # 2 failures: check_outliers_train x2 (missing decision_function).
    # Fixable: add decision_function = score_samples alias.
    "DepthgramDetector": "PASS-WITH-FIXES: add decision_function = score_samples alias",
}
