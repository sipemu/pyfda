"""Interop test — FPCATransformer → RandomForestClassifier Pipeline (COMPLY-02).

Proves that an fdars transformer composes end-to-end with a native sklearn
estimator inside a single ``Pipeline``.  The FPCATransformer maps functional
data ``(n_obs, n_points) → (n_obs, n_components)`` score matrix; the
RandomForestClassifier receives the scores as plain ndarray features.

COMPLY-02: fdars transformer scores → native sklearn estimator in one Pipeline.

Usage
-----
Run the interop test::

    pytest tests/sklearn/test_interop.py -v

"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from fdars.sklearn._skeletons import FPCATransformer


# ---------------------------------------------------------------------------
# Deterministic dataset — two Gaussian-shifted curve groups
# ---------------------------------------------------------------------------

_N_PER_CLASS = 15   # 15 obs per class → 30 total; fast for RF
_N_POINTS = 20      # evaluation grid points
_RNG_SEED = 42      # fixed seed for reproducibility


def _make_Xy(n_per_class: int = _N_PER_CLASS, n_pts: int = _N_POINTS,
             seed: int = _RNG_SEED):
    """Return (X, y) for a two-class functional classification dataset.

    Class 0: Gaussian noise on a 20-point grid.
    Class 1: Same noise shifted by +3.0 (well-separated for RF to learn).

    Parameters
    ----------
    n_per_class : int
        Observations per class.
    n_pts : int
        Number of evaluation points per curve.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    X : ndarray of shape (2 * n_per_class, n_pts)
    y : ndarray of shape (2 * n_per_class,), dtype int, values in {0, 1}
    """
    rng = np.random.RandomState(seed)
    X0 = rng.randn(n_per_class, n_pts)
    X1 = rng.randn(n_per_class, n_pts) + 3.0
    X = np.vstack([X0, X1]).astype(np.float64)
    y = np.array([0] * n_per_class + [1] * n_per_class, dtype=int)
    return X, y


# ---------------------------------------------------------------------------
# COMPLY-02: FPCATransformer → RandomForestClassifier pipeline
# ---------------------------------------------------------------------------


def test_fpca_to_random_forest_pipeline():
    """Pipeline([FPCATransformer, RandomForestClassifier]) fits + predicts end-to-end.

    COMPLY-02: fdars functional transformer (FPCATransformer) produces FPC
    score arrays consumed directly by a native sklearn classifier
    (RandomForestClassifier) inside one sklearn Pipeline.

    No Fdata object is used — the transformer accepts and emits plain
    float64 ndarrays, so the native sklearn stage sees its usual 2D
    feature matrix.

    Assertions
    ----------
    - pipe.fit(X, y) completes without error.
    - pipe.predict(X) returns an ndarray of shape (n_obs,).
    - Every predicted label is drawn from the training class set.
    - pipe.score(X, y) returns a float in [0.0, 1.0].
    """
    X, y = _make_Xy()
    n_obs = X.shape[0]

    pipe = Pipeline([
        ("fpca", FPCATransformer(n_components=5)),
        ("rf", RandomForestClassifier(n_estimators=20, random_state=0)),
    ])

    pipe.fit(X, y)

    y_pred = pipe.predict(X)

    assert y_pred.shape == (n_obs,), (
        f"predict returned shape {y_pred.shape}; expected ({n_obs},)"
    )
    assert set(y_pred).issubset(set(y)), (
        f"predict returned labels outside the training class set: "
        f"{set(y_pred)} not a subset of {set(y)}"
    )

    score_val = pipe.score(X, y)
    assert isinstance(score_val, float), (
        f"score() returned {type(score_val).__name__}; expected float"
    )
    assert 0.0 <= score_val <= 1.0, (
        f"score() returned {score_val!r}; expected value in [0.0, 1.0]"
    )
