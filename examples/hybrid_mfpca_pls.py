"""Hybrid: MFPCA basis + PACE partial-obs + PLS regression.

Combines the strengths of both approaches:
  - MFPCA eigenfunctions + PACE for principled partial-observation
    score estimation (handles missing parts of X via covariance)
  - sklearn's PLSRegression for the scores→Y mapping, which finds
    supervised components that correlate with Y (not just explain X)

Think of it as: use MFPCA+PACE as a *feature extractor* that handles
partial data well, then PLS as a supervised regression on those features.

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.cross_decomposition import PLSRegression
from sklearn.utils.validation import check_is_fitted

# Reuse MFPCA + PACE machinery from the existing file
import sys
sys.path.insert(0, ".")
from partial_predictor_sklearn import (
    _mfpca, _estimate_noise, _scores_truncated, _scores_pace,
    _trapezoidal_weights,
)


class MFPCAPLSHybrid(BaseEstimator, RegressorMixin):
    """Hybrid: MFPCA+PACE feature extraction + PLS regression.

    Pipeline:
        X (full or partial)
           → MFPCA scores (via truncated projection or PACE)
           → PLSRegression
           → Y(t)

    Parameters
    ----------
    n_comp : int
        Number of MFPCA components (feature extraction dimension).
    n_pls : int or None
        Number of PLS components.  If None, uses ``min(n_comp, m_y)``.
    n_features : int
        Number of functional predictors p.
    method : str
        Score estimation for partial data: "truncated" or "pace".
    argvals : array-like or None
    argvals_predict : array-like or None
    """

    def __init__(
        self,
        n_comp: int = 8,
        n_pls: Optional[int] = None,
        n_features: int = 1,
        method: str = "pace",
        argvals=None,
        argvals_predict=None,
    ):
        self.n_comp = n_comp
        self.n_pls = n_pls
        self.n_features = n_features
        self.method = method
        self.argvals = argvals
        self.argvals_predict = argvals_predict

    def _split_X(self, X, m):
        return [X[:, j * m : (j + 1) * m] for j in range(self.n_features)]

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        p = self.n_features
        if X.shape[1] % p != 0:
            raise ValueError("X columns not divisible by n_features")
        m = X.shape[1] // p
        self.n_points_ = m

        self.argvals_ = (np.linspace(0, 1, m) if self.argvals is None
                         else np.asarray(self.argvals, dtype=np.float64))

        # 1. MFPCA on full training data
        X_list = self._split_X(X, m)
        self.mfpca_ = _mfpca(X_list, self.argvals_, self.n_comp)

        # 2. Noise variance for PACE
        if self.method == "pace":
            self.sigma2_ = _estimate_noise(X_list, self.argvals_, self.mfpca_)
        else:
            self.sigma2_ = None

        # 3. Extract training scores (no partial obs during fit)
        train_scores = self.mfpca_["scores"]

        # 4. PLSRegression on (scores → Y)
        n_pls = self.n_pls or min(len(self.mfpca_["eigenvalues"]), y.shape[1])
        n_pls = min(n_pls, train_scores.shape[1])
        self.pls_ = PLSRegression(n_components=n_pls, scale=False)
        self.pls_.fit(train_scores, y)
        return self

    def _resolve_partial_grid(self, X):
        p = self.n_features
        m = self.n_points_
        m_c = X.shape[1] // p
        if m_c == m:
            return self.argvals_
        if self.argvals_predict is not None:
            return np.asarray(self.argvals_predict, dtype=np.float64)
        return self.argvals_[:m_c]

    def predict(self, X):
        check_is_fitted(self)
        X = np.asarray(X, dtype=np.float64)
        argvals_partial = self._resolve_partial_grid(X)
        m_c = len(argvals_partial)
        X_list = self._split_X(X, m_c)
        idx = np.searchsorted(self.argvals_, argvals_partial)

        # Extract scores using the MFPCA basis (PACE or truncated)
        if self.method == "pace" and self.sigma2_ is not None:
            scores, _ = _scores_pace(X_list, idx, self.mfpca_, self.sigma2_)
        else:
            quad_c = _trapezoidal_weights(argvals_partial)
            scores = _scores_truncated(X_list, idx, quad_c, self.mfpca_)

        # Apply PLS regression on the scores
        return self.pls_.predict(scores)

    def score(self, X, y, sample_weight=None):
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2, axis=0)
        ss_tot = np.sum((y - y.mean(axis=0)) ** 2, axis=0)
        r2 = 1 - ss_res / np.maximum(ss_tot, 1e-12)
        return float(r2.mean())


# ===================================================================
# Comparison demo
# ===================================================================

if __name__ == "__main__":
    from partial_predictor_sklearn import FunctionalPartialRegressor
    from fpls_partial import FPLSPartialRegressor
    from sklearn.model_selection import cross_validate

    np.random.seed(0)

    # Same dataset as fpls_partial.py for direct comparison
    n, m, p = 300, 60, 2
    t = np.linspace(0, 1, m)
    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
    noise1 = np.array([0.8 * np.sin(10 * np.pi * t + np.random.uniform(0, 2 * np.pi))
                        for _ in range(n)])
    X1 = X1 + noise1
    X2 = X2 + 0.3 * np.random.randn(n, m)
    Y = (0.5 * np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
         + 0.3 * np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
         + 0.15 * np.random.randn(n, m))
    X = np.hstack([X1, X2])
    X_train, X_test = X[:200], X[200:]
    Y_train, Y_test = Y[:200], Y[200:]

    print("=" * 75)
    print("Three-way comparison: MFPCA vs FPLS vs HYBRID (MFPCA+PACE + PLS)")
    print("=" * 75)
    print()

    def eval_at_horizons(name, reg_factory):
        reg = reg_factory()
        reg.fit(X_train, Y_train)
        row = f"   {name:30s}"
        for frac in [1.0, 0.6, 0.3]:
            c = int(frac * m)
            X_te = (X_test if c == m
                     else np.hstack([X1[200:, :c], X2[200:, :c]]))
            reg.argvals_predict = t[:c] if c < m else None
            y_hat = reg.predict(X_te)
            mse = np.mean((Y_test - y_hat) ** 2)
            r2 = reg.score(X_te, Y_test)
            row += f"  {frac:4.0%}: R²={r2:.3f}"
        print(row)

    for K in [3, 5, 8, 12]:
        print(f"   K = {K} components (horizon: 100% / 60% / 30%):")
        eval_at_horizons(
            "MFPCA (unsupervised)",
            lambda K=K: FunctionalPartialRegressor(
                n_comp=K, n_features=2, method="pace", argvals=t),
        )
        eval_at_horizons(
            "FPLS (supervised)",
            lambda K=K: FPLSPartialRegressor(
                n_comp=K, n_features=2, argvals=t),
        )
        # Hybrid: use K MFPCA components, then PLS on scores
        eval_at_horizons(
            f"Hybrid MFPCA({K}) + PLS",
            lambda K=K: MFPCAPLSHybrid(
                n_comp=K, n_pls=min(K, 5),
                n_features=2, method="pace", argvals=t),
        )
        print()

    # --- Cross-validation comparison ---------------------------------
    print("=" * 75)
    print("5-fold CV — full domain")
    print("=" * 75)

    methods = {
        "MFPCA only": lambda K: FunctionalPartialRegressor(
            n_comp=K, n_features=2, method="pace", argvals=t),
        "FPLS only": lambda K: FPLSPartialRegressor(
            n_comp=K, n_features=2, argvals=t),
        "Hybrid (K, 3 PLS)": lambda K: MFPCAPLSHybrid(
            n_comp=K, n_pls=min(3, K), n_features=2, method="pace", argvals=t),
        "Hybrid (K, 5 PLS)": lambda K: MFPCAPLSHybrid(
            n_comp=K, n_pls=min(5, K), n_features=2, method="pace", argvals=t),
    }
    for name, factory in methods.items():
        print(f"\n   {name}:")
        for K in [3, 5, 8, 12]:
            reg = factory(K)
            cv = cross_validate(reg, X, Y, cv=5,
                                scoring="neg_mean_squared_error")
            print(f"     K={K:2d}: MSE={-cv['test_score'].mean():.4f} "
                  f"+/- {cv['test_score'].std():.4f}")
