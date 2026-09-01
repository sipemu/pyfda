"""Authoritative COMPLY-01 aggregate compliance gate — Phase 58 Plan 04.

This file is the single full-matrix ``parametrize_with_checks`` gate over
ALL 28 wrapped estimators across all five families (transformers, regressors,
classifiers, clusterers, outlier detectors) with ZERO exemptions.

Phase 58 promoted every candidate to PASS:
  * Plans 01-02 fixed the six clusterers and six outlier detectors.
  * Plans 56-57 fixed all transformers, regressors, and classifiers.
  * Final verdict: 28 / 28 PASS, 0 PASS-WITH-FIXES, 0 EXCLUDE.

How to run
----------
Run the aggregate gate (all 28, ~1400 checks)::

    pytest tests/sklearn/test_compliance_gate.py -q

Run a single estimator from this gate::

    pytest tests/sklearn/test_compliance_gate.py -k FPCATransformer -v

For per-family batteries run the family-specific compliance files (faster
for focused debugging)::

    pytest tests/sklearn/test_transformers_compliance.py -q
    pytest tests/sklearn/test_regressors_compliance.py -q
    pytest tests/sklearn/test_classifiers_compliance.py -q
    pytest tests/sklearn/test_clusterers_compliance.py -q
    pytest tests/sklearn/test_outliers_compliance.py -q
"""

from __future__ import annotations

import pytest
from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._coverage import TRIAGE_VERDICTS
from fdars.sklearn._skeletons import (
    # Transformers (8)
    BSplineSmoother,
    LocalPolynomialSmoother,
    BasisRepresentation,
    FPCATransformer,
    Imputer,
    SplineInterpolator,
    DepthTransformer,
    NormTransformer,
    # Regressors (5)
    FPCRegressor,
    PLSRegressor,
    RobustFPCRegressor,
    GLMRegressor,
    NonparametricRegressor,
    # Classifiers (6)
    FPCLDAClassifier,
    FPCQDAClassifier,
    FPCKNNClassifier,
    DDClassifier,
    LogisticFPCClassifier,
    ElasticMultinomialClassifier,
    # Clusterers (3)
    FunctionalKMeans,
    FuzzyFunctionalCMeans,
    FunctionalGMM,
    # Outlier detectors (6)
    LRTOutlierDetector,
    OutliergramDetector,
    MagnitudeShapeDetector,
    TVDMSSDetector,
    MUODDetector,
    DepthgramDetector,
)

# ---------------------------------------------------------------------------
# All 28 wrapped estimators with the SAME battery-valid hyperparameters used
# in the per-family compliance files.  The parameter choices are required for
# the battery to pass (e.g. ncomp=10 satisfies check_classifiers_train,
# n_components=10 satisfies check_regressors_train, contamination=0.1 is the
# OutlierMixin convention, n_bootstrap=50 speeds up LRT).
# ---------------------------------------------------------------------------

_ALL_WRAPPED = [
    # --- Transformers ---
    FPCATransformer(n_components=10),
    BSplineSmoother(),
    LocalPolynomialSmoother(),
    BasisRepresentation(n_basis=3),
    Imputer(),
    SplineInterpolator(),
    DepthTransformer(),
    NormTransformer(),
    # --- Regressors ---
    FPCRegressor(n_components=10),
    PLSRegressor(n_components=3),
    RobustFPCRegressor(n_components=10),
    GLMRegressor(n_components=10),
    NonparametricRegressor(),
    # --- Classifiers ---
    FPCLDAClassifier(ncomp=10),
    FPCQDAClassifier(ncomp=10),
    FPCKNNClassifier(ncomp=10),
    DDClassifier(),
    LogisticFPCClassifier(n_components=10),
    ElasticMultinomialClassifier(ncomp_beta=5),
    # --- Clusterers ---
    FunctionalKMeans(n_clusters=2),
    FuzzyFunctionalCMeans(n_clusters=2),
    FunctionalGMM(n_clusters=2),
    # --- Outlier Detectors ---
    LRTOutlierDetector(n_bootstrap=50, contamination=0.1),
    OutliergramDetector(contamination=0.1),
    MagnitudeShapeDetector(contamination=0.1),
    TVDMSSDetector(contamination=0.1),
    MUODDetector(contamination=0.1),
    DepthgramDetector(contamination=0.1),
]

# Sanity: the list above must contain exactly 28 estimators (one per wrapped class).
assert len(_ALL_WRAPPED) == 28, (
    f"_ALL_WRAPPED has {len(_ALL_WRAPPED)} entries; expected 28. "
    "Update this list when adding or retiring a wrapped estimator."
)


# ---------------------------------------------------------------------------
# COMPLY-01: Full-matrix aggregate gate — ZERO exemptions
# ---------------------------------------------------------------------------


@parametrize_with_checks(_ALL_WRAPPED)
def test_full_matrix_compliance(estimator, check):
    """All 28 wrapped estimators pass the complete parametrize_with_checks battery.

    This is the authoritative COMPLY-01 gate.  Every estimator must pass every
    sklearn estimator check with ZERO exemptions.  No ``pytest.mark.xfail`` or
    ``pytest.skip`` is permitted here.

    The battery runs ~50 checks per estimator (~1400 total).  Each check is an
    independent parametrized test case so any regression is immediately
    locatable by estimator and check name.
    """
    check(estimator)


# ---------------------------------------------------------------------------
# _coverage.py assertion: zero PASS-WITH-FIXES among wrapped estimators
# ---------------------------------------------------------------------------

# The 28 class names that must appear in TRIAGE_VERDICTS with verdict "PASS".
_WRAPPED_NAMES: set[str] = {type(est).__name__ for est in _ALL_WRAPPED}


def test_no_pass_with_fixes_remaining():
    """Assert that _coverage.TRIAGE_VERDICTS contains ZERO PASS-WITH-FIXES values.

    At milestone-close (Phase 58 Plan 04) every wrapped estimator carries a
    "PASS" verdict.  This test encodes that invariant so any future regression
    to PASS-WITH-FIXES is caught immediately in CI.

    Checks enforced
    ---------------
    1. Every verdict value for a wrapped estimator starts with "PASS".
    2. None of the wrapped-estimator verdicts contains the substring
       "PASS-WITH-FIXES".
    3. The count of wrapped estimators whose verdict == "PASS" (exact) is 28.

    Note: EXCLUDED_METHODS is asserted structural-only (no PASS or
    PASS-WITH-FIXES values) by the existing test_coverage.py suite.
    """
    wrapped_verdicts = {
        name: verdict
        for name, verdict in TRIAGE_VERDICTS.items()
        if name in _WRAPPED_NAMES
    }

    # 1. All verdicts start with "PASS"
    not_passing = {
        name: v for name, v in wrapped_verdicts.items()
        if not v.startswith("PASS")
    }
    assert not not_passing, (
        f"Wrapped estimators with non-PASS verdict: {not_passing}. "
        "These must be fixed or removed from the wrapped set before milestone close."
    )

    # 2. None contain "PASS-WITH-FIXES"
    still_with_fixes = {
        name: v for name, v in wrapped_verdicts.items()
        if "PASS-WITH-FIXES" in v
    }
    assert not still_with_fixes, (
        f"Wrapped estimators still carrying PASS-WITH-FIXES: {still_with_fixes}. "
        "Apply the outstanding fixes before locking the compliance gate."
    )

    # 3. Exactly 28 clean-PASS verdicts
    clean_pass = {name: v for name, v in wrapped_verdicts.items() if v == "PASS"}
    assert len(clean_pass) == 28, (
        f"Expected exactly 28 wrapped estimators with verdict 'PASS'; "
        f"got {len(clean_pass)}: {sorted(clean_pass)}. "
        "Update _ALL_WRAPPED and TRIAGE_VERDICTS to stay in sync."
    )
