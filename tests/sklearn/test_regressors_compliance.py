"""Per-regressor compliance tests for fdars sklearn regressors.

Each test function uses ``parametrize_with_checks`` to run the full
scikit-learn estimator battery for ONE regressor in isolation.  This
keeps each regressor's battery independently selectable and fast —
no need to run the whole 28-estimator triage each time.

Scope (Plan 01 — Wave 1 / Phase 57)
-------------------------------------
* ``test_fpc_regressor_compliance``  — FPCRegressor promoted to PASS (REG-01)
* ``test_pls_regressor_compliance``  — PLSRegressor promoted to PASS (REG-01)

Scope (Plan 02 — Wave 2 / Phase 57)
-------------------------------------
* ``test_robust_fpc_regressor_compliance`` — RobustFPCRegressor (REG-02)
* ``test_glm_regressor_compliance``        — GLMRegressor (REG-02)
* ``test_nonparametric_regressor_compliance`` — NonparametricRegressor (REG-02)

Key design decisions
---------------------
* Stored-model predict: predict re-fits on STORED training data only.
  No ``np.vstack``; each test row is independent of siblings —
  satisfying ``check_methods_subset_invariance``.
* Raised ``n_components`` default to 10 so ``check_regressors_train`` achieves
  R² > 0.5 on sklearn's battery data (~100 obs, ~20 features).
* Shared ``_require_y`` guard raises ``ValueError`` with the substring
  ``"requires y to be passed"`` so ``check_requires_y_none`` passes.
* GLMRegressor exposes ``n_iter_`` set in fit for
  ``check_non_transformer_estimators_n_iter``.
* ``score()`` is NOT overridden — inherited from ``RegressorMixin``
  (``r2_score(y, predict(X))``).

Usage
-----
Run a single regressor battery::

    pytest tests/sklearn/test_regressors_compliance.py::test_fpc_regressor_compliance -v

Run all regressor compliance tests::

    pytest tests/sklearn/test_regressors_compliance.py -q
"""

from __future__ import annotations

from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import (
    FPCRegressor,
    GLMRegressor,
    NonparametricRegressor,
    PLSRegressor,
    RobustFPCRegressor,
)


# ---------------------------------------------------------------------------
# Wave-1 compliance tests (Plan 01 / Phase 57 — REG-01)
# ---------------------------------------------------------------------------


@parametrize_with_checks([FPCRegressor()])
def test_fpc_regressor_compliance(estimator, check):
    """Full parametrize_with_checks battery for FPCRegressor (REG-01).

    Verifies:
    - ``check_regressors_train``: R² > 0.5 on battery data (n_components=10
      default so enough FPCs are used on sklearn's ~100x~20 design).
    - ``check_methods_subset_invariance``: predict(X[mask]) == predict(X)[mask]
      because predict re-fits on STORED train only (no vstack).
    - ``check_requires_y_none``: fit(X, y=None) raises ValueError containing
      the substring ``"requires y to be passed"`` via the shared ``_require_y``
      guard.
    - ``score()`` is inherited from RegressorMixin — NOT overridden.
    """
    check(estimator)


@parametrize_with_checks([PLSRegressor()])
def test_pls_regressor_compliance(estimator, check):
    """Full parametrize_with_checks battery for PLSRegressor (REG-01).

    Verifies:
    - ``check_regressors_train``: R² > 0.5 on battery data (PLS converges
      fast with default n_components=3 on sklearn's battery data).
    - ``check_methods_subset_invariance``: predict(X[mask]) == predict(X)[mask]
      because predict re-fits on STORED train only (no vstack).
    - ``check_requires_y_none``: fit(X, y=None) raises ValueError containing
      the substring ``"requires y to be passed"`` via the shared ``_require_y``
      guard.
    - ``score()`` is inherited from RegressorMixin — NOT overridden.
    """
    check(estimator)


# ---------------------------------------------------------------------------
# Wave-2 compliance tests (Plan 02 / Phase 57 — REG-02)
# ---------------------------------------------------------------------------


@parametrize_with_checks([RobustFPCRegressor(n_components=10)])
def test_robust_fpc_regressor_compliance(estimator, check):
    """Full parametrize_with_checks battery for RobustFPCRegressor (REG-02).

    Verifies:
    - ``check_regressors_train``: R² > 0.5 on battery data (n_components=10).
    - ``check_methods_subset_invariance``: predict uses
      ``predict_fregre_robust(X_fit_, y_fit_, X_new, ...)`` — stored train only.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    """
    check(estimator)


@parametrize_with_checks([GLMRegressor(n_components=10)])
def test_glm_regressor_compliance(estimator, check):
    """Full parametrize_with_checks battery for GLMRegressor (REG-02).

    Verifies:
    - ``check_regressors_train``: R² > 0.5 via stored-model grid inner product.
    - ``check_methods_subset_invariance``: predict uses stored intercept_/beta_t_.
    - ``check_non_transformer_estimators_n_iter``: n_iter_ set in fit.
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    - ``check_fit2d_1feature``: 1-feature input raises with "n_features=1" message.
    """
    check(estimator)


@parametrize_with_checks([NonparametricRegressor()])
def test_nonparametric_regressor_compliance(estimator, check):
    """Full parametrize_with_checks battery for NonparametricRegressor (REG-02).

    Verifies:
    - ``check_regressors_train``: R² > 0.5 via Nadaraya-Watson on stored train.
    - ``check_methods_subset_invariance``: predict uses
      ``_pairwise_l2(X_new, X_fit_)`` (new-vs-train only, no vstack).
    - ``check_requires_y_none``: fit(X, y=None) raises via ``_require_y``.
    """
    check(estimator)
