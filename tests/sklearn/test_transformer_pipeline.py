"""Capstone cross-transformer tests for the fdars sklearn transformer family.

Tests
-----
test_smoother_fpca_pipeline_roundtrip
    ``Pipeline([BSplineSmoother, FPCATransformer])`` fits and transforms a
    deterministic synthetic dataset to a finite ``(n_obs, 2)`` score matrix;
    ``fit_transform`` is consistent with ``fit`` then ``transform``.
    Covers XFORM-06 (grid-changing chain round-trip).

test_fpca_fit_idempotent
    Two separate ``FPCATransformer`` instances fitted on the same data produce
    identical ``components_`` (up to floating-point noise).
    Regression guard for XFORM-01 (SVD sign canonicalization).

test_transformers_never_construct_fdata
    Source-level parametrized check that none of the 8 transformer classes
    contains an ``Fdata(`` call and each routes compute through ``_native``.
    Covers the contract: estimators call ``fdars._native.*`` directly, never
    constructing an Fdata (STRIDE T-56-05).
"""

from __future__ import annotations

import inspect

import numpy as np
import pytest
from sklearn.pipeline import Pipeline

from fdars.sklearn._skeletons import (
    BasisRepresentation,
    BSplineSmoother,
    DepthTransformer,
    FPCATransformer,
    Imputer,
    LocalPolynomialSmoother,
    NormTransformer,
    SplineInterpolator,
)

# ---------------------------------------------------------------------------
# Shared deterministic test dataset
# ---------------------------------------------------------------------------

_N_OBS = 20
_N_POINTS = 50
_RNG_SEED = 42


def _make_X() -> np.ndarray:
    """Return a small deterministic (n_obs, n_points) float64 dataset."""
    rng = np.random.default_rng(_RNG_SEED)
    return rng.standard_normal((_N_OBS, _N_POINTS))


# ---------------------------------------------------------------------------
# Task 1 — Pipeline round-trip and FPCA idempotence
# ---------------------------------------------------------------------------


def test_smoother_fpca_pipeline_roundtrip():
    """Pipeline([BSplineSmoother, FPCATransformer]) round-trip — XFORM-06.

    Asserts:
    * Output shape is (n_obs, n_components=2).
    * All output values are finite (no NaN, no Inf).
    * ``fit_transform(X)`` matches ``fit(X).transform(X)`` element-wise.
    """
    X = _make_X()
    n_obs = X.shape[0]
    n_components = 2

    pipe = Pipeline([
        ("smoother", BSplineSmoother()),
        ("fpca", FPCATransformer(n_components=n_components)),
    ])

    # fit then transform
    pipe.fit(X)
    X_transformed = pipe.transform(X)

    assert X_transformed.shape == (n_obs, n_components), (
        f"Expected shape ({n_obs}, {n_components}), got {X_transformed.shape}"
    )
    assert np.all(np.isfinite(X_transformed)), (
        "Pipeline output contains non-finite values (NaN or Inf)"
    )

    # fit_transform must be consistent with fit + transform
    pipe2 = Pipeline([
        ("smoother", BSplineSmoother()),
        ("fpca", FPCATransformer(n_components=n_components)),
    ])
    X_fit_transform = pipe2.fit_transform(X)

    # Both pipelines receive the same data — their fit_transform / fit+transform
    # results must be numerically identical.
    assert X_fit_transform.shape == (n_obs, n_components), (
        f"fit_transform shape mismatch: {X_fit_transform.shape}"
    )
    assert np.allclose(X_transformed, X_fit_transform, rtol=1e-10, atol=1e-12), (
        "fit_transform result diverges from fit-then-transform"
    )


def test_fpca_fit_idempotent():
    """Two independent FPCATransformer fits on the same data yield identical components_.

    This is the regression guard for the SVD sign canonicalization introduced
    in Plan 01 (XFORM-01).  The sign-flip applied per component ensures that
    repeated fits always produce the same ``components_`` array.
    """
    X = _make_X()

    fpca1 = FPCATransformer(n_components=3)
    fpca2 = FPCATransformer(n_components=3)

    fpca1.fit(X)
    fpca2.fit(X)

    assert fpca1.components_.shape == fpca2.components_.shape, (
        "components_ shape mismatch between two fits"
    )
    assert np.allclose(fpca1.components_, fpca2.components_, rtol=1e-10, atol=1e-12), (
        "FPCA fit is NOT idempotent — SVD sign canonicalization may be broken. "
        f"Max abs diff: {np.max(np.abs(fpca1.components_ - fpca2.components_))}"
    )


# ---------------------------------------------------------------------------
# Task 2 — Static contract: no transformer constructs an Fdata
# ---------------------------------------------------------------------------

_TRANSFORMER_CLASSES = [
    FPCATransformer,
    BSplineSmoother,
    LocalPolynomialSmoother,
    BasisRepresentation,
    Imputer,
    SplineInterpolator,
    DepthTransformer,
    NormTransformer,
]


@pytest.mark.parametrize("cls", _TRANSFORMER_CLASSES, ids=[c.__name__ for c in _TRANSFORMER_CLASSES])
def test_transformers_never_construct_fdata(cls):
    """Assert each transformer class is Fdata-free and routes compute via _native.

    Source-level check — no instantiation of Fdata is required.  Protects
    against future edits reintroducing ``Fdata(`` calls that would cause
    dtype side-effects and break ``check_estimator`` (STRIDE T-56-05).

    For each transformer class asserts:
    * Source contains no ``Fdata(`` call.
    * Source contains ``_native`` (routes through the native layer).
    """
    source = inspect.getsource(cls)

    assert "Fdata(" not in source, (
        f"{cls.__name__} contains an 'Fdata(' call — estimators must call "
        "fdars._native.* directly and NEVER construct an Fdata object."
    )
    assert "_native" in source, (
        f"{cls.__name__} does not reference '_native' — estimators must route "
        "compute through fdars._native.*."
    )
