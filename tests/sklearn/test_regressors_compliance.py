"""Per-regressor compliance tests for fdars sklearn regressors.

Each test function uses ``parametrize_with_checks`` to run the full
scikit-learn estimator battery for ONE regressor in isolation.  This
keeps each regressor's battery independently selectable and fast —
no need to run the whole 28-estimator triage each time.

Scope (Plan 01 — Wave 1 / Phase 57)
-------------------------------------
* ``test_fpc_regressor_compliance``  — FPCRegressor promoted to PASS (REG-01)
* ``test_pls_regressor_compliance``  — PLSRegressor promoted to PASS (REG-01)

Key design decisions
---------------------
* Stored-model predict: ``predict_fregre_lm`` / ``predict_fregre_pls`` re-fit
  on the STORED training data only (``X_fit_``, ``y_fit_``), then predict the
  passed ``X``.  No ``np.vstack``; each test row is independent of siblings —
  satisfying ``check_methods_subset_invariance``.
* Raised ``n_components`` default to 10 so ``check_regressors_train`` achieves
  R² > 0.5 on sklearn's battery data (~100 obs, ~20 features).
* Shared ``_require_y`` guard raises ``ValueError`` with the substring
  ``"requires y to be passed"`` so ``check_requires_y_none`` passes.
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

from fdars.sklearn._skeletons import FPCRegressor, PLSRegressor


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
