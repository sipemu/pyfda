"""Capstone predictive-pipeline tests — PRED-01.

Tests
-----
test_gridsearch_predictive_pipeline
    ``GridSearchCV`` over ``Pipeline([Imputer, BSplineSmoother, FPCATransformer,
    FPCLDAClassifier])`` fits + predicts on held-out data (PRED-01).
    Searches over ``fpca__n_components`` and ``clf__ncomp``; asserts
    ``best_estimator_`` is set and predictions cover the training class set.

test_regressor_pipeline_smoke
    ``Pipeline([Imputer, BSplineSmoother, FPCATransformer, FPCRegressor])``
    fits a scalar regression target, predicts a finite float array of the
    right length, and scores a finite value — showing regressors compose in
    a Pipeline too (PRED-01).
"""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from fdars.sklearn._skeletons import (
    BSplineSmoother,
    FPCATransformer,
    FPCLDAClassifier,
    FPCRegressor,
    Imputer,
)

# ---------------------------------------------------------------------------
# Shared deterministic dataset helpers
# ---------------------------------------------------------------------------

_N_OBS = 40        # total observations (small for fast GridSearchCV)
_N_POINTS = 20     # evaluation grid points
_RNG_SEED = 7      # fixed seed for reproducibility


def _make_Xy_clf(n_obs: int = _N_OBS, n_pts: int = _N_POINTS,
                 rng_seed: int = _RNG_SEED):
    """Return (X, y) for a two-class functional classification dataset.

    Generates two separable classes (offset by a mean shift of 3.0) over
    a uniform grid; injects a sparse NaN pattern so the Imputer stage is
    exercised.

    Parameters
    ----------
    n_obs : int
        Total number of curves (split evenly between classes).
    n_pts : int
        Number of evaluation points per curve.
    rng_seed : int
        RNG seed for reproducibility.

    Returns
    -------
    X : ndarray of shape (n_obs, n_pts), with sparse NaN values
    y : ndarray of shape (n_obs,), dtype int, values in {0, 1}
    """
    rng = np.random.default_rng(rng_seed)
    half = n_obs // 2

    # Class 0: base Gaussian noise
    X0 = rng.standard_normal((half, n_pts))
    # Class 1: mean-shifted by 3.0 for good separability
    X1 = rng.standard_normal((half, n_pts)) + 3.0

    X = np.vstack([X0, X1])
    y = np.array([0] * half + [1] * half, dtype=int)

    # Inject sparse NaN pattern so the Imputer stage does real work.
    # Using a stride pattern avoids NaN at first/last columns (boundary
    # safe for linear interpolation) — stride [::5, 2::7] skips col 0.
    X_nan = X.copy()
    X_nan[::5, 2::7] = np.nan

    return X_nan, y


def _make_Xy_reg(n_obs: int = _N_OBS, n_pts: int = _N_POINTS,
                 rng_seed: int = _RNG_SEED):
    """Return (X, y) for a scalar regression dataset over functional X.

    Parameters
    ----------
    n_obs : int
    n_pts : int
    rng_seed : int

    Returns
    -------
    X : ndarray of shape (n_obs, n_pts)
    y : ndarray of shape (n_obs,), continuous float64
    """
    rng = np.random.default_rng(rng_seed + 1)
    X = rng.standard_normal((n_obs, n_pts))
    # y is a linear combination of first few grid points + noise
    y = X[:, 0] * 2.0 + X[:, 1] * (-1.0) + rng.standard_normal(n_obs) * 0.5
    return X, y


# ---------------------------------------------------------------------------
# Task 1 — GridSearchCV over 4-stage predictive pipeline (PRED-01)
# ---------------------------------------------------------------------------


def test_gridsearch_predictive_pipeline():
    """GridSearchCV over Pipeline([Imputer, BSplineSmoother, FPCATransformer,
    FPCLDAClassifier]) fits and predicts end-to-end — PRED-01.

    Pipeline stages
    ---------------
    1. imputer  : Imputer()       — fills NaN values via linear interpolation
    2. smoother : BSplineSmoother() — Nadaraya-Watson per-curve smoothing
    3. fpca     : FPCATransformer  — maps (n_obs, n_pts) -> (n_obs, n_comp) scores
    4. clf      : FPCLDAClassifier — LDA on FPC scores (applies a 2nd FPCA pass
                                     since its X input is the score matrix)

    Grid searched
    -------------
    ``fpca__n_components``: [2, 3]
    ``clf__ncomp``        : [1, 2]

    The grid is intentionally small (2x2 = 4 candidates, cv=3 = 12 fits) to
    stay well under a minute.  FPCLDAClassifier.fit caps its ncomp at
    min(ncomp, n_obs-1, n_features), so values up to 2 are safe when the
    upstream FPCATransformer produces >= 2 score columns and n_train >= 3.

    Assertions
    ----------
    - grid.fit(X_train, y_train) succeeds; best_estimator_ is set.
    - grid.predict(X_test) returns len(X_test) labels, all in set(y_train).
    - grid.best_params_ contains both searched stage__param keys.
    """
    X, y = _make_Xy_clf()

    X_train, X_test, y_train, _ = train_test_split(
        X, y, test_size=0.25, random_state=_RNG_SEED, stratify=y
    )

    pipe = Pipeline([
        ("imputer", Imputer()),
        ("smoother", BSplineSmoother()),
        ("fpca", FPCATransformer()),
        ("clf", FPCLDAClassifier()),
    ])

    param_grid = {
        "fpca__n_components": [2, 3],
        "clf__ncomp": [1, 2],
    }

    grid = GridSearchCV(pipe, param_grid=param_grid, cv=3, refit=True)
    grid.fit(X_train, y_train)

    # best_estimator_ must be set after fit
    assert grid.best_estimator_ is not None, (
        "GridSearchCV did not set best_estimator_ after fit"
    )

    # predict on held-out data
    y_pred = grid.predict(X_test)

    assert len(y_pred) == len(X_test), (
        f"predict returned {len(y_pred)} labels; expected {len(X_test)}"
    )
    assert set(y_pred).issubset(set(y_train)), (
        f"predict returned labels outside the training class set: "
        f"{set(y_pred)} not subset of {set(y_train)}"
    )

    # best_params_ must include both searched keys
    assert "fpca__n_components" in grid.best_params_, (
        "best_params_ missing 'fpca__n_components'"
    )
    assert "clf__ncomp" in grid.best_params_, (
        "best_params_ missing 'clf__ncomp'"
    )


# ---------------------------------------------------------------------------
# Task 2 — Regressor pipeline smoke test (PRED-01)
# ---------------------------------------------------------------------------


def test_regressor_pipeline_smoke():
    """Pipeline([Imputer, BSplineSmoother, FPCATransformer, FPCRegressor])
    fits a scalar target, predicts a finite float array, and scores a
    finite value — showing regressors compose in a Pipeline too (PRED-01).

    Pipeline stages
    ---------------
    1. imputer  : Imputer()
    2. smoother : BSplineSmoother()
    3. fpca     : FPCATransformer(n_components=4)   maps curves -> scores
    4. reg      : FPCRegressor(n_components=3)      FPC regression on scores

    Assertions
    ----------
    - pipe.fit(X, y) succeeds.
    - pipe.predict(X) returns an ndarray of shape (n_obs,) with all finite values.
    - pipe.score(X, y) returns a finite scalar.
    """
    X, y = _make_Xy_reg()
    n_obs = X.shape[0]

    pipe = Pipeline([
        ("imputer", Imputer()),
        ("smoother", BSplineSmoother()),
        ("fpca", FPCATransformer(n_components=4)),
        ("reg", FPCRegressor(n_components=3)),
    ])

    pipe.fit(X, y)

    y_pred = pipe.predict(X)

    assert y_pred.shape == (n_obs,), (
        f"predict returned shape {y_pred.shape}; expected ({n_obs},)"
    )
    assert np.all(np.isfinite(y_pred)), (
        "predict returned non-finite values (NaN or Inf)"
    )

    score_val = pipe.score(X, y)
    assert np.isfinite(score_val), (
        f"score returned non-finite value: {score_val}"
    )
