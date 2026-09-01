"""Per-outlier-detector compliance tests for fdars sklearn outlier detectors.

Each test function uses ``parametrize_with_checks`` to run the full
scikit-learn estimator battery for ONE detector in isolation.  This
keeps each detector's battery independently selectable and fast.

Scope (Plan 01 — Tracer / Phase 58)
-------------------------------------
* ``test_magnitude_shape_compliance`` — MagnitudeShapeDetector (OUT-01)

  Proves green (via stored-reference subset-invariant depth scoring):

  * ``check_outliers_train``: both -1 and +1 produced via contamination offset.
  * ``check_methods_subset_invariance``: stored-reference depth (CR-03 fix).
  * ``check_outliers_fit_predict``: fit_predict consistent with predict(fit(X)).
  * ``check_estimators_dtypes``: float32 input upcast to float64 before native.

Key design decisions
---------------------
* Stored-reference depth scoring: score_samples scores each new curve against
  the STORED ``X_fit_`` from training via
  ``_native.depth.modified_band_1d(X_new, self.X_fit_)``.
  This is subset-invariant by construction.
* contamination=0.1 (fixed float, not "auto") guarantees both {-1,+1} on the
  battery's small datasets — offset_ = 10th-percentile of training scores.
* decision_function(X) = score_samples(X) - offset_ (continuous shift).
* predict(X) = np.where(decision_function(X) >= 0, 1, -1).astype(np.int64).

Usage
-----
Run MagnitudeShapeDetector battery::

    pytest tests/sklearn/test_outliers_compliance.py::test_magnitude_shape_compliance -v

Run all outlier compliance tests::

    pytest tests/sklearn/test_outliers_compliance.py -q
"""

from __future__ import annotations

from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import MagnitudeShapeDetector


# ---------------------------------------------------------------------------
# OUT-01 compliance tests (Plan 01 / Phase 58)
# ---------------------------------------------------------------------------


@parametrize_with_checks([MagnitudeShapeDetector(contamination=0.1)])
def test_magnitude_shape_compliance(estimator, check):
    """Full parametrize_with_checks battery for MagnitudeShapeDetector (OUT-01).

    Verifies:
    - ``check_outliers_train``: both -1 and +1 produced via contamination-
      derived offset_ (10th-percentile of training depth scores).
    - ``check_methods_subset_invariance``: stored-reference MBD depth
      ``modified_band_1d(X_new, X_fit_)`` — resolves Phase-57 review CR-03.
    - ``check_outliers_fit_predict``: fit_predict consistent with predict.
    - ``check_estimators_dtypes``: float32 inputs upcast to float64.
    """
    check(estimator)
