"""Go/no-go viable-core gate (TRIAGE-03).

Asserts that a viable core of PASS or PASS-WITH-FIXES estimators exists before
Phase 56 family implementation begins.  The required minimum per family is:

  * >= 1 FPCA transformer
  * >= 2 smoothers / transformers (non-FPCA)
  * >= 2 regressors
  * >= 2 classifiers
  * >= 1 clusterer
  * >= 2 outlier detectors

Only PASS and PASS-WITH-FIXES verdicts count toward the core.
PASS-WITH-FIXES is viable: the required fix is applied in Phase 56-58 real
implementation; the structural contract can be met.
EXCLUDE does not count.

If any family falls short, the test fails with an explicit message naming the
family and its count -- this is the milestone-blocking signal.

Source of truth: TRIAGE_VERDICTS in python/fdars/sklearn/_coverage.py
(derived from triage_results.txt: sklearn 1.8.0 / Python 3.14,
1379 checks, 1272 PASS / 107 FAIL across 28 estimators).
"""

from __future__ import annotations

import pytest

# Skip entire module if sklearn is not installed.
pytest.importorskip("sklearn")

from fdars.sklearn._coverage import TRIAGE_VERDICTS  # noqa: E402


# ---------------------------------------------------------------------------
# Family membership map
# ---------------------------------------------------------------------------
# Each estimator is mapped to exactly one family.
# Families: fpca, smoother, regressor, classifier, clusterer, outlier
# ---------------------------------------------------------------------------

FAMILY_MAP: dict[str, str] = {
    # FPCA transformers
    "FPCATransformer": "fpca",
    # Smoothers / transformers (non-FPCA)
    "BSplineSmoother": "smoother",
    "LocalPolynomialSmoother": "smoother",
    "BasisRepresentation": "smoother",
    "Imputer": "smoother",
    "DepthTransformer": "smoother",
    "NormTransformer": "smoother",
    # Regressors
    "FPCRegressor": "regressor",
    "PLSRegressor": "regressor",
    "RobustFPCRegressor": "regressor",
    "GLMRegressor": "regressor",
    "NonparametricRegressor": "regressor",
    # Classifiers
    "FPCLDAClassifier": "classifier",
    "FPCQDAClassifier": "classifier",
    "FPCKNNClassifier": "classifier",
    "DDClassifier": "classifier",
    "LogisticFPCClassifier": "classifier",
    "ElasticMultinomialClassifier": "classifier",
    # Clusterers
    "FunctionalKMeans": "clusterer",
    "FuzzyFunctionalCMeans": "clusterer",
    "FunctionalGMM": "clusterer",
    # Outlier detectors
    "LRTOutlierDetector": "outlier",
    "OutliergramDetector": "outlier",
    "MagnitudeShapeDetector": "outlier",
    "TVDMSSDetector": "outlier",
    "MUODDetector": "outlier",
    "DepthgramDetector": "outlier",
    # SplineInterpolator is a transformer/smoother (excluded from core)
    "SplineInterpolator": "smoother",
}

# Minimum viable count per family.
MINIMUMS: dict[str, int] = {
    "fpca": 1,
    "smoother": 2,
    "regressor": 2,
    "classifier": 2,
    "clusterer": 1,
    "outlier": 2,
}


# ---------------------------------------------------------------------------
# Helper: count viable (PASS or PASS-WITH-FIXES) members per family
# ---------------------------------------------------------------------------

def _count_viable() -> dict[str, list[str]]:
    """Return {family: [list of viable estimator names]}."""
    result: dict[str, list[str]] = {f: [] for f in MINIMUMS}
    for cls_name, verdict in TRIAGE_VERDICTS.items():
        family = FAMILY_MAP.get(cls_name)
        if family is None:
            continue  # unknown family, skip
        if verdict.startswith("PASS"):  # covers PASS and PASS-WITH-FIXES
            result[family].append(cls_name)
    return result


# ---------------------------------------------------------------------------
# Informational summary (printed when running pytest -s or -v)
# ---------------------------------------------------------------------------

def test_print_viable_core_summary() -> None:
    """Print per-family PASS/PASS-WITH-FIXES counts (informational)."""
    viable = _count_viable()
    print("\n--- Viable Core Summary (TRIAGE-03) ---")
    for family, members in viable.items():
        minimum = MINIMUMS[family]
        status = "OK" if len(members) >= minimum else "SHORT"
        print(f"  {family:12s}: {len(members):2d} viable  "
              f"(min={minimum})  [{status}]")
        for m in sorted(members):
            verdict = TRIAGE_VERDICTS[m]
            tag = "PASS" if verdict == "PASS" else "PASS-WITH-FIXES"
            print(f"    - {m} [{tag}]")
    print("---------------------------------------")


# ---------------------------------------------------------------------------
# Gate assertions (one per family)
# ---------------------------------------------------------------------------

def test_fpca_viable_core() -> None:
    """>=1 FPCA transformer must be PASS or PASS-WITH-FIXES."""
    viable = _count_viable()
    family = "fpca"
    count = len(viable[family])
    minimum = MINIMUMS[family]
    assert count >= minimum, (
        f"FPCA family short-fall: need >= {minimum} viable FPCA transformer(s), "
        f"got {count}. "
        f"Viable members: {viable[family]}. "
        f"BLOCKED: Phase 56 FPCA transformer implementation cannot proceed."
    )


def test_smoother_viable_core() -> None:
    """>=2 smoother/transformer (non-FPCA) estimators must be PASS or PASS-WITH-FIXES."""
    viable = _count_viable()
    family = "smoother"
    count = len(viable[family])
    minimum = MINIMUMS[family]
    assert count >= minimum, (
        f"Smoother family short-fall: need >= {minimum} viable smoother(s), "
        f"got {count}. "
        f"Viable members: {viable[family]}. "
        f"BLOCKED: Phase 56 smoother implementation cannot proceed."
    )


def test_regressor_viable_core() -> None:
    """>=2 regressor estimators must be PASS or PASS-WITH-FIXES.

    Phase 55 triage result: only 1 viable regressor (PLSRegressor).
    The remaining 4 regressors (FPCRegressor, RobustFPCRegressor,
    GLMRegressor, NonparametricRegressor) are EXCLUDED due to the
    re-fit-at-predict structural pattern causing accuracy failures.

    If this test fails, Phase 57 (Regressors) must restructure its
    implementation plan to use a stored-model approach before it can
    achieve sklearn compliance.
    """
    viable = _count_viable()
    family = "regressor"
    count = len(viable[family])
    minimum = MINIMUMS[family]
    assert count >= minimum, (
        f"Regressor family short-fall: need >= {minimum} viable regressor(s), "
        f"got {count} ({viable[family]}). "
        f"All excluded regressors (FPCRegressor, RobustFPCRegressor, "
        f"GLMRegressor, NonparametricRegressor) fail check_regressors_train "
        f"due to the re-fit-at-predict vstack design (ACCURACY_STRUCTURAL). "
        f"BLOCKED: Phase 57 Regressor implementation must adopt a stored-model "
        f"predict design before this gate can pass."
    )


def test_classifier_viable_core() -> None:
    """>=2 classifier estimators must be PASS or PASS-WITH-FIXES.

    Phase 55 triage result: only 1 viable classifier (FPCKNNClassifier).
    The remaining classifiers (FPCLDAClassifier, FPCQDAClassifier,
    DDClassifier) fail check_classifiers_train (accuracy < 0.83) due to
    the vstack re-fit pattern; LogisticFPCClassifier is excluded due to
    label domain constraint; ElasticMultinomialClassifier has multiple
    structural issues.

    If this test fails, Phase 57 (Classifiers) must restructure its
    implementation plan.
    """
    viable = _count_viable()
    family = "classifier"
    count = len(viable[family])
    minimum = MINIMUMS[family]
    assert count >= minimum, (
        f"Classifier family short-fall: need >= {minimum} viable classifier(s), "
        f"got {count} ({viable[family]}). "
        f"Excluded classifiers: FPCLDAClassifier/FPCQDAClassifier/DDClassifier "
        f"(ACCURACY_STRUCTURAL), LogisticFPCClassifier (LABEL_DOMAIN), "
        f"ElasticMultinomialClassifier (UNFITTED_CHECK_MISSING + structural). "
        f"BLOCKED: Phase 57 Classifier implementation must adopt a stored-model "
        f"predict design and label-type validation before this gate can pass."
    )


def test_clusterer_viable_core() -> None:
    """>=1 clusterer estimator must be PASS or PASS-WITH-FIXES."""
    viable = _count_viable()
    family = "clusterer"
    count = len(viable[family])
    minimum = MINIMUMS[family]
    assert count >= minimum, (
        f"Clusterer family short-fall: need >= {minimum} viable clusterer(s), "
        f"got {count}. "
        f"Viable members: {viable[family]}. "
        f"BLOCKED: Phase 58 Clusterer implementation cannot proceed."
    )


def test_outlier_viable_core() -> None:
    """>=2 outlier detector estimators must be PASS or PASS-WITH-FIXES."""
    viable = _count_viable()
    family = "outlier"
    count = len(viable[family])
    minimum = MINIMUMS[family]
    assert count >= minimum, (
        f"Outlier detector family short-fall: need >= {minimum} viable "
        f"outlier detector(s), got {count}. "
        f"Viable members: {viable[family]}. "
        f"BLOCKED: Phase 58 Outlier Detector implementation cannot proceed."
    )


# ---------------------------------------------------------------------------
# Overall gate: all families at minimum -> go signal for Phase 56
# ---------------------------------------------------------------------------

def test_overall_go_no_go() -> None:
    """All families must meet their minimum -- this is the Phase 56 go signal.

    A failure here names every family that falls short and provides the
    explicit NO-GO signal for Phase 56 family implementation.
    """
    viable = _count_viable()
    gaps: list[str] = []
    for family, minimum in MINIMUMS.items():
        count = len(viable[family])
        if count < minimum:
            gaps.append(
                f"{family}: {count}/{minimum} viable "
                f"(members: {viable[family]})"
            )
    if gaps:
        pytest.fail(
            "VIABLE CORE GATE: NO-GO -- the following families fall short of "
            "their minimum:\n"
            + "\n".join(f"  - {gap}" for gap in gaps)
            + "\n\nPhase 56 implementation must not begin until these families "
            "are resolved. See TRIAGE_VERDICTS in _coverage.py for excluded "
            "estimators and their structural reasons."
        )
