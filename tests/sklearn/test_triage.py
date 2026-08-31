"""Compliance triage harness for Phase 55.

Run the full triage battery with::

    pytest tests/sklearn/test_triage.py -v --tb=short -rA 2>&1 | tee triage_results.txt

Then review triage_results.txt to assign PASS / PASS-WITH-FIXES / EXCLUDE
verdicts and populate ``_coverage.TRIAGE_VERDICTS`` accordingly.

Verdict assignment rule
-----------------------
All checks PASS
    -> PASS

Checks fail only due to fixable guards (1-sample message, float cast, etc.)
    -> PASS-WITH-FIXES: list the specific fixes required

Checks fail due to structural incompatibility (algorithm requirements, wrong
output shape, requires IrregFdata input, etc.)
    -> EXCLUDE: record in EXCLUDED_METHODS with failing_check name

Plan scope
----------
* Plan 01: FPCATransformer tracer only (47/47 PASS, verified production-quality).
* Plan 02 (this expansion): all ~28 remaining candidate skeleton classes added
  to ``_ALL_SKELETONS``; full ``parametrize_with_checks`` battery run across
  all five families (transformers, regressors, classifiers, clusterers, outlier
  detectors).  Results captured to ``triage_results.txt`` at repo root for
  Plan 03 verdict assignment.

Note: The harness intentionally does NOT assert all-green.  Failures are expected
and informative -- each failing check name drives EXCLUDE decisions in Plan 03.
"""

from __future__ import annotations

import pytest
from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import (
    # Transformers
    BSplineSmoother,
    LocalPolynomialSmoother,
    BasisRepresentation,
    FPCATransformer,
    Imputer,
    SplineInterpolator,
    DepthTransformer,
    NormTransformer,
    # Regressors
    FPCRegressor,
    PLSRegressor,
    RobustFPCRegressor,
    GLMRegressor,
    NonparametricRegressor,
    # Classifiers
    FPCLDAClassifier,
    FPCQDAClassifier,
    FPCKNNClassifier,
    DDClassifier,
    LogisticFPCClassifier,
    ElasticMultinomialClassifier,
    # Clusterers
    FunctionalKMeans,
    FuzzyFunctionalCMeans,
    FunctionalGMM,
    # Outlier Detectors
    LRTOutlierDetector,
    OutliergramDetector,
    MagnitudeShapeDetector,
    TVDMSSDetector,
    MUODDetector,
    DepthgramDetector,
)


# ---------------------------------------------------------------------------
# Estimator list -- Plan 02: all 28 candidate skeletons across all five families
# ---------------------------------------------------------------------------
# Each estimator is constructed with the minimal valid hyperparameters that
# allow check_estimator to run (n_components=1 or n_clusters=2 where needed).
# Predicted EXCLUDE candidates are included so triage empirically confirms.

_ALL_SKELETONS = [
    # --- Transformers ---
    FPCATransformer(n_components=1),   # tracer: PASS (47/47 in Plan 01)
    BSplineSmoother(),
    LocalPolynomialSmoother(),
    BasisRepresentation(n_basis=3),
    Imputer(),
    SplineInterpolator(),
    DepthTransformer(),
    NormTransformer(),
    # --- Regressors ---
    FPCRegressor(n_components=1),
    PLSRegressor(n_components=1),
    RobustFPCRegressor(n_components=1),
    GLMRegressor(n_components=1),
    NonparametricRegressor(),
    # --- Classifiers ---
    FPCLDAClassifier(ncomp=1),
    FPCQDAClassifier(ncomp=1),
    FPCKNNClassifier(ncomp=1, k=1),
    DDClassifier(),
    LogisticFPCClassifier(n_components=1),
    ElasticMultinomialClassifier(ncomp_beta=3),  # EXCLUDE predicted -- triage confirms
    # --- Clusterers ---
    FunctionalKMeans(n_clusters=2),
    FuzzyFunctionalCMeans(n_clusters=2),
    FunctionalGMM(n_clusters=2),   # EXCLUDE predicted -- triage confirms
    # --- Outlier Detectors ---
    LRTOutlierDetector(n_bootstrap=50),  # reduced bootstrap for speed
    OutliergramDetector(),
    MagnitudeShapeDetector(),
    TVDMSSDetector(),              # EXCLUDE predicted -- triage confirms
    MUODDetector(),                # EXCLUDE predicted -- triage confirms
    DepthgramDetector(),           # EXCLUDE predicted -- triage confirms
]


# ---------------------------------------------------------------------------
# Triage harness
# ---------------------------------------------------------------------------

@parametrize_with_checks(_ALL_SKELETONS)
def test_sklearn_triage(estimator, check):
    """Run each parametrize_with_checks case as an independent test.

    A PASS confirms the estimator is fully sklearn-compliant for that check.
    A FAIL is informative: record the failing check name in TRIAGE_VERDICTS
    and classify as PASS-WITH-FIXES (if fixable) or EXCLUDE (structural).

    This harness surfaces ALL failing checks independently so no single
    failure masks others -- contrast with check_estimator() which aborts at
    the first failure.
    """
    check(estimator)
