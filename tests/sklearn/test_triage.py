"""Compliance triage harness — Phase 55 origin, reconciled in Phase 58 Plan 04.

Phase 58 closure note
---------------------
All 28 wrapped estimators across all five families now carry a "PASS" verdict
in ``_coverage.TRIAGE_VERDICTS``.  The harness is GREEN.

The authoritative aggregate gate (COMPLY-01) lives in::

    tests/sklearn/test_compliance_gate.py

that file runs ``parametrize_with_checks`` over all 28 estimators with ZERO
exemptions and asserts that ``_coverage.TRIAGE_VERDICTS`` contains no
PASS-WITH-FIXES entries.

This file is retained as a secondary regression check.  The estimator list
is now constructed with the same battery-valid hyperparameters as the
per-family compliance suites (ncomp=10, n_components=10, contamination=0.1,
n_bootstrap=50 for LRT) so every case passes.

History
-------
* Phase 55 Plan 01: FPCATransformer tracer (47/47 PASS).
* Phase 55 Plan 02: all 28 candidates added; full battery run; results
  captured to triage_results.txt for verdict assignment.
* Phase 55 Plan 03: verdicts assigned; 9 PASS + 19 PASS-WITH-FIXES.
* Phases 56-58: all 19 PASS-WITH-FIXES candidates fixed to PASS.
* Phase 58 Plan 04: harness updated to battery-valid parameters; now green.
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
    # --- Transformers (8) ---
    FPCATransformer(n_components=10),   # tracer: PASS (47/47 in Plan 01)
    BSplineSmoother(),
    LocalPolynomialSmoother(),
    BasisRepresentation(n_basis=3),
    Imputer(),
    SplineInterpolator(),
    DepthTransformer(),
    NormTransformer(),
    # --- Regressors (5) ---
    FPCRegressor(n_components=10),       # n_components=10 required for check_regressors_train
    PLSRegressor(n_components=3),
    RobustFPCRegressor(n_components=10),
    GLMRegressor(n_components=10),
    NonparametricRegressor(),
    # --- Classifiers (6) ---
    FPCLDAClassifier(ncomp=10),          # ncomp=10 required for check_classifiers_train
    FPCQDAClassifier(ncomp=10),
    FPCKNNClassifier(ncomp=10),
    DDClassifier(),
    LogisticFPCClassifier(n_components=10),
    ElasticMultinomialClassifier(ncomp_beta=5),  # PASS after Phase 57 CLF-02 fix
    # --- Clusterers (3) ---
    FunctionalKMeans(n_clusters=2),
    FuzzyFunctionalCMeans(n_clusters=2),
    FunctionalGMM(n_clusters=2),        # PASS after Phase 58 Plan 03 fix
    # --- Outlier Detectors (6) ---
    LRTOutlierDetector(n_bootstrap=50, contamination=0.1),
    OutliergramDetector(contamination=0.1),
    MagnitudeShapeDetector(contamination=0.1),
    TVDMSSDetector(contamination=0.1),  # PASS after Phase 58 Plan 02 fix
    MUODDetector(contamination=0.1),   # PASS after Phase 58 Plan 02 fix
    DepthgramDetector(contamination=0.1),  # PASS after Phase 58 Plan 02 fix
]


# ---------------------------------------------------------------------------
# Triage harness
# ---------------------------------------------------------------------------

@parametrize_with_checks(_ALL_SKELETONS)
def test_sklearn_triage(estimator, check):
    """Run each parametrize_with_checks case as an independent test.

    Phase 58 Plan 04: all 28 estimators now PASS every check.  This harness
    is a secondary green regression check; the authoritative COMPLY-01 gate
    is ``test_compliance_gate.py::test_full_matrix_compliance``.

    Original purpose (Phase 55): surface all failing checks independently
    so no single failure masks others.  Each failing check name drove EXCLUDE
    decisions in Plan 03.  All 19 PASS-WITH-FIXES candidates have since been
    fixed in Phases 56-58.
    """
    check(estimator)
