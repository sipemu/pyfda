"""Per-transformer compliance tests for fdars sklearn transformers.

Each test function uses ``parametrize_with_checks`` to run the full
scikit-learn estimator battery for ONE transformer in isolation.  This
keeps each transformer's battery independently selectable and fast —
no need to run the whole 28-estimator triage each time.

Scope (Plan 01 — Wave 1)
------------------------
* ``test_imputer_compliance``   — Imputer promoted to PASS in XFORM-03
* ``test_fpca_compliance``      — FPCATransformer regression guard (XFORM-01)
* ``test_bspline_smoother_compliance``     — BSplineSmoother regression guard (XFORM-02)
* ``test_local_poly_smoother_compliance``  — LocalPolynomialSmoother regression guard (XFORM-02)
* ``test_depth_transformer_compliance``    — DepthTransformer regression guard (XFORM-05)
* ``test_norm_transformer_compliance``     — NormTransformer regression guard (XFORM-05)

Scope (Plan 02 — Wave 2, add below this comment block)
-------------------------------------------------------
* ``test_basis_representation_compliance`` — BasisRepresentation (XFORM-04)
* ``test_spline_interpolator_compliance``  — SplineInterpolator (XFORM-04)

Usage
-----
Run a single transformer battery::

    pytest tests/sklearn/test_transformers_compliance.py::test_imputer_compliance -v

Run all transformer compliance tests::

    pytest tests/sklearn/test_transformers_compliance.py -q
"""

from __future__ import annotations

import pytest
from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import (
    BSplineSmoother,
    DepthTransformer,
    FPCATransformer,
    Imputer,
    LocalPolynomialSmoother,
    NormTransformer,
    # Plan 02 imports (add when wave-2 tasks are promoted to PASS):
    # BasisRepresentation,
    # SplineInterpolator,
)


# ---------------------------------------------------------------------------
# Wave-1 compliance tests
# ---------------------------------------------------------------------------


@parametrize_with_checks([Imputer()])
def test_imputer_compliance(estimator, check):
    """Full parametrize_with_checks battery for Imputer.

    Verifies XFORM-03: ensure_all_finite/force_all_finite cross-version shim
    + accept_sparse=False are correctly wired so all sklearn checks pass.
    """
    check(estimator)


@parametrize_with_checks([FPCATransformer(n_components=1)])
def test_fpca_compliance(estimator, check):
    """Regression guard for FPCATransformer (XFORM-01).

    FPCATransformer was the tracer estimator proven PASS in Phase 55 Plan 01.
    This test ensures it stays green while Plan 01/02 edits the same file.
    """
    check(estimator)


@parametrize_with_checks([BSplineSmoother()])
def test_bspline_smoother_compliance(estimator, check):
    """Regression guard for BSplineSmoother (XFORM-02).

    BSplineSmoother passed 47/47 checks in the Phase-55 triage.
    """
    check(estimator)


@parametrize_with_checks([LocalPolynomialSmoother()])
def test_local_poly_smoother_compliance(estimator, check):
    """Regression guard for LocalPolynomialSmoother (XFORM-02).

    LocalPolynomialSmoother passed 47/47 checks in the Phase-55 triage.
    """
    check(estimator)


@parametrize_with_checks([DepthTransformer()])
def test_depth_transformer_compliance(estimator, check):
    """Regression guard for DepthTransformer (XFORM-05).

    DepthTransformer passed 47/47 checks in the Phase-55 triage.
    """
    check(estimator)


@parametrize_with_checks([NormTransformer()])
def test_norm_transformer_compliance(estimator, check):
    """Regression guard for NormTransformer (XFORM-05).

    NormTransformer passed 47/47 checks in the Phase-55 triage.
    """
    check(estimator)


# ---------------------------------------------------------------------------
# Plan 02 placeholders — add test functions here when BasisRepresentation
# and SplineInterpolator are promoted from PASS-WITH-FIXES to PASS.
#
# @parametrize_with_checks([BasisRepresentation(n_basis=3)])
# def test_basis_representation_compliance(estimator, check):
#     """Full parametrize_with_checks battery for BasisRepresentation (XFORM-04)."""
#     check(estimator)
#
# @parametrize_with_checks([SplineInterpolator()])
# def test_spline_interpolator_compliance(estimator, check):
#     """Full parametrize_with_checks battery for SplineInterpolator (XFORM-04)."""
#     check(estimator)
# ---------------------------------------------------------------------------
