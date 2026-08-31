"""Per-classifier compliance tests for fdars sklearn classifiers.

Each test function uses ``parametrize_with_checks`` to run the full
scikit-learn estimator battery for ONE classifier in isolation.  This
keeps each classifier's battery independently selectable and fast.

Scope (Plan 02 — Wave 2 / Phase 57)
-------------------------------------
* ``test_fpc_lda_compliance``          — FPCLDAClassifier (CLF-01)
* ``test_fpc_qda_compliance``          — FPCQDAClassifier (CLF-01)
* ``test_fpc_knn_compliance``          — FPCKNNClassifier (CLF-01)
* ``test_dd_compliance``               — DDClassifier (CLF-02)
* ``test_logistic_fpc_compliance``     — LogisticFPCClassifier (CLF-01)
* ``test_elastic_multinomial_compliance`` — ElasticMultinomialClassifier (CLF-02)

Key design decisions
---------------------
* Reconstructed stored-model predict: all classifiers store FPC components +
  mean from training FPCA, then project new data via ``_fpc_project``.
  Never calls the transductive native (fclassif_lda/qda/knn/dd) in predict.
* LabelEncoder in fit: ``classes_`` + ``label_encoder_`` stored;
  predict inverse-transforms to original labels.
* ``FPCKNNClassifier`` rejects continuous targets
  (``check_classifiers_regression_target``).
* ``LogisticFPCClassifier`` is binary-only; >2 classes raises ValueError.
* ``ElasticMultinomialClassifier`` uses FPC scores + sklearn OvR
  LogisticRegression (Option A); exposes ``n_iter_``.

Usage
-----
Run a single classifier battery::

    pytest tests/sklearn/test_classifiers_compliance.py::test_fpc_lda_compliance -v

Run all classifier compliance tests::

    pytest tests/sklearn/test_classifiers_compliance.py -q
"""

from __future__ import annotations

from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import (
    DDClassifier,
    ElasticMultinomialClassifier,
    FPCKNNClassifier,
    FPCLDAClassifier,
    FPCQDAClassifier,
    LogisticFPCClassifier,
)


# ---------------------------------------------------------------------------
# CLF-01 compliance tests (Plan 02 / Phase 57)
# ---------------------------------------------------------------------------


@parametrize_with_checks([FPCLDAClassifier(ncomp=10)])
def test_fpc_lda_compliance(estimator, check):
    """Full parametrize_with_checks battery for FPCLDAClassifier (CLF-01).

    Verifies:
    - ``check_classifiers_train``: accuracy meets battery threshold.
    - ``check_methods_subset_invariance``: stored FPC basis + sklearn LDA.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    - ``check_classifiers_classes``: LabelEncoder + classes_ + inverse_transform.
    """
    check(estimator)


@parametrize_with_checks([FPCQDAClassifier(ncomp=10)])
def test_fpc_qda_compliance(estimator, check):
    """Full parametrize_with_checks battery for FPCQDAClassifier (CLF-01).

    Verifies:
    - ``check_classifiers_train``: accuracy meets battery threshold.
    - ``check_methods_subset_invariance``: stored FPC basis + sklearn QDA.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    - ``check_classifiers_classes``: LabelEncoder + classes_ + inverse_transform.
    """
    check(estimator)


@parametrize_with_checks([FPCKNNClassifier(ncomp=10)])
def test_fpc_knn_compliance(estimator, check):
    """Full parametrize_with_checks battery for FPCKNNClassifier (CLF-01).

    Verifies:
    - ``check_classifiers_train``: accuracy meets battery threshold.
    - ``check_methods_subset_invariance``: numpy kNN over stored FPC scores.
    - ``check_classifiers_regression_target``: continuous y raises ValueError.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    """
    check(estimator)


@parametrize_with_checks([DDClassifier()])
def test_dd_compliance(estimator, check):
    """Full parametrize_with_checks battery for DDClassifier (CLF-02).

    Verifies:
    - ``check_classifiers_train``: nearest-centroid in FPC space achieves
      threshold accuracy on separable battery data.
    - ``check_methods_subset_invariance``: stored components + per-class centroids.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    """
    check(estimator)


# ---------------------------------------------------------------------------
# CLF-01/CLF-02 compliance tests for Logistic and Elastic (Plan 02 / Phase 57)
# ---------------------------------------------------------------------------


@parametrize_with_checks([LogisticFPCClassifier(n_components=10)])
def test_logistic_fpc_compliance(estimator, check):
    """Full parametrize_with_checks battery for LogisticFPCClassifier (CLF-01).

    Verifies:
    - ``check_estimators_fit_returns_self``: fit returns self (root cause of
      21-check cascade).
    - ``check_classifiers_train``: binary LabelEncoder to {0.0,1.0} for native.
    - ``check_methods_subset_invariance``: predict_functional_logistic on stored
      train (no vstack).
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    """
    check(estimator)


@parametrize_with_checks([ElasticMultinomialClassifier(ncomp_beta=5)])
def test_elastic_multinomial_compliance(estimator, check):
    """Full parametrize_with_checks battery for ElasticMultinomialClassifier (CLF-02).

    Option A: FPC scores + sklearn OvR LogisticRegression.

    Verifies:
    - ``check_estimators_unfitted`` + ``check_fit_check_is_fitted``:
      check_is_fitted before predict.
    - ``check_fit2d_1feature``: 1-feature input raises "n_features=1" message.
    - ``check_methods_subset_invariance``: stored FPC basis + sklearn OvR.
    - ``check_non_transformer_estimators_n_iter``: n_iter_ exposed.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    """
    check(estimator)
