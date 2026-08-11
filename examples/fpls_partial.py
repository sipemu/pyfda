"""Multivariate Functional Partial Least Squares (MFPLS).

Drop-in alternative to FunctionalPartialRegressor (MFPCA).  Uses NIPALS
on the stacked multivariate functional predictors with quadrature
weights, so the scores maximize covariance with Y (supervised) instead
of variance of X (unsupervised).

Differences from MFPCA:

  - Components are supervised: Cov(score, Y) maximized, not Var(X)
  - Usually needs fewer components for the same prediction quality
  - No natural PACE analog — partial observations handled by truncated
    projection via the "effective weights" W* = W (P^T W)^{-1}

Compatible with scikit-learn's cross_validate, GridSearchCV, Pipeline.

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.utils.validation import check_is_fitted


# ===================================================================
# Helpers (shared pattern with MFPCA code)
# ===================================================================

def _trapezoidal_weights(argvals: NDArray) -> NDArray:
    m = len(argvals)
    dt = np.diff(argvals)
    w = np.empty(m)
    w[0] = dt[0] / 2
    w[-1] = dt[-1] / 2
    if m > 2:
        w[1:-1] = (dt[:-1] + dt[1:]) / 2
    return w


# ===================================================================
# MFPLS via NIPALS
# ===================================================================

def _mfpls(
    X_list: List[NDArray],
    argvals: NDArray,
    Y: NDArray,
    n_comp: int,
    max_iter: int = 500,
    tol: float = 1e-8,
) -> dict:
    """Multivariate Functional PLS via NIPALS.

    Maximizes Cov(<X, w_k>, <Y, q_k>) subject to ||w_k|| = 1 over
    the stacked multi-feature function space with quadrature inner
    product, then deflates.

    Parameters
    ----------
    X_list : list of ndarray, each (n, m)
        p functional predictors on a common grid.
    argvals : ndarray (m,)
    Y : ndarray (n, m_y)
        Functional response.
    n_comp : int
    max_iter, tol : NIPALS convergence

    Returns
    -------
    dict with:
        W          : (K, p*m)    — X-weights (functional)
        P          : (K, p*m)    — X-loadings
        Q          : (K, m_y)    — Y-loadings
        T          : (n, K)      — X-scores (training)
        W_star     : (K, p*m)    — effective weights for prediction
        mean_x     : (p*m,)      — concatenated X mean
        mean_y     : (m_y,)      — Y mean
        feature_weights : (p,)   — per-feature scaling
        n_features, n_points
    """
    p = len(X_list)
    n, m = X_list[0].shape
    quad_x = _trapezoidal_weights(argvals)

    # --- Centering + per-feature scaling (same as MFPCA) -----------
    means_x, centered, feature_weights = [], [], np.empty(p)
    for j in range(p):
        mu = X_list[j].mean(axis=0)
        means_x.append(mu)
        Xc = X_list[j] - mu
        avg_norm = np.sqrt(np.mean(np.sum(Xc ** 2 * quad_x, axis=1)))
        feature_weights[j] = 1.0 / max(avg_norm, 1e-12)
        centered.append(Xc * feature_weights[j])

    E = np.hstack(centered)  # (n, p*m)
    W_x = np.tile(quad_x, p)  # (p*m,) quadrature weights

    mean_y = Y.mean(axis=0)
    F = Y - mean_y

    K = min(n_comp, n - 1, p * m)
    W = np.zeros((K, p * m))     # X-weights
    P = np.zeros((K, p * m))     # X-loadings
    Q = np.zeros((K, Y.shape[1]))  # Y-loadings
    T = np.zeros((n, K))          # X-scores

    for k in range(K):
        # Initialize u with column of F of largest norm
        u = F[:, np.argmax(np.sum(F ** 2, axis=0))].copy()

        for _ in range(max_iter):
            # X-weight: w ∝ E^T @ (u * I) — in L2(X) inner product, weights
            # only apply when computing <X, w>, so w itself is just a
            # direction in the raw feature space.  We keep w normalized
            # in the L2 functional metric: ||w||^2 = sum w^2 * W_x
            w = E.T @ u
            w_fnorm = np.sqrt(np.sum(w ** 2 * W_x))
            if w_fnorm < 1e-12:
                break
            w = w / w_fnorm

            # X-score: t = <E, w>_L2 = E @ (W_x * w)  (n,)
            t = E @ (W_x * w)

            # Y-loading: q = F^T t / (t^T t), normalized
            q = F.T @ t
            q_norm = np.linalg.norm(q)
            if q_norm < 1e-12:
                break
            q = q / q_norm

            u_new = F @ q
            if np.linalg.norm(u_new - u) < tol * max(1.0, np.linalg.norm(u)):
                u = u_new
                break
            u = u_new

        # Deflation
        tt = t @ t
        if tt < 1e-12:
            break
        p_load = (E.T @ t) / tt  # X-loading (raw)
        c = (F.T @ t) / tt       # Y-loading (regression coefficient)

        W[k] = w
        P[k] = p_load
        Q[k] = c
        T[:, k] = t

        E = E - np.outer(t, p_load)
        F = F - np.outer(t, c)

    # Trim unused components (if NIPALS broke early)
    valid = np.any(W != 0, axis=1)
    W, P, Q, T = W[valid], P[valid], Q[valid], T[:, valid]

    # Effective weights for out-of-sample projection:
    # W_star = W @ (P^T W)^{-1}  (in standard PLS column notation)
    # In row-major: W_star_row = (P W^T)^{-1} W  applied to rows
    PWt = P @ (W_x * W).T  # K x K, with quadrature metric on W
    W_star = np.linalg.solve(PWt, W)  # (K, p*m)

    return dict(
        W=W, P=P, Q=Q, T=T, W_star=W_star,
        mean_x=np.hstack(means_x),
        mean_y=mean_y,
        feature_weights=feature_weights,
        n_features=p,
        n_points=m,
        quad_x=quad_x,
    )


def _scores_from_partial_pls(
    X_list: List[NDArray],
    idx: NDArray,
    argvals_partial: NDArray,
    pls: dict,
) -> NDArray:
    """Estimate PLS scores from partial observations via truncated
    projection using the effective weights W_star restricted to [a, c].

    The scale factor handles the shorter integration domain.
    """
    p = pls["n_features"]
    m = pls["n_points"]
    m_c = len(idx)
    K = pls["W_star"].shape[0]
    n_new = X_list[0].shape[0]

    # Quadrature on partial grid
    quad_c = _trapezoidal_weights(argvals_partial)

    scores = np.zeros((n_new, K))
    for k in range(K):
        w_star = pls["W_star"][k]  # (p*m,)
        num = np.zeros(n_new)
        den = 0.0
        for j in range(p):
            # Restrict to observed region for feature j
            w_c = w_star[j * m : (j + 1) * m][idx]
            mu_c = pls["mean_x"][j * m : (j + 1) * m][idx]
            fw = pls["feature_weights"][j]
            Xc = (X_list[j] - mu_c) * fw
            num += Xc @ (w_c * quad_c)

            # Denominator: use full-grid norm of w_star (partial would
            # underweight longer-support components, empirically worse).
            # For a pure scaling correction, we use the partial norm.
            den += np.sum(w_c ** 2 * quad_c)

        # Scale by full/partial norm ratio to correct for shorter integral
        full_den = np.sum(w_star ** 2 * np.tile(pls["quad_x"], p))
        scores[:, k] = num * (full_den / max(den, 1e-12))
        scores[:, k] /= full_den  # normalize back
        # Simplified: scores[:, k] = num / max(den, 1e-12) would also work
    return scores


# ===================================================================
# Sklearn estimator
# ===================================================================

class FPLSPartialRegressor(BaseEstimator, RegressorMixin):
    """Partial-domain functional-on-functional regressor via MFPLS.

    Drop-in replacement for FunctionalPartialRegressor, but supervised:
    components maximize covariance with Y instead of variance of X.

    Parameters
    ----------
    n_comp : int
        Number of PLS components.
    n_features : int
        Number of functional predictors p.
    argvals : array-like or None
        Grid for X (length m).
    argvals_predict : array-like or None
        Partial grid for prediction (length m_c).

    Attributes (after fit)
    ----------------------
    pls_ : dict with W, P, Q, T, W_star, mean_x, mean_y, feature_weights
    n_points_ : int
    """

    def __init__(
        self,
        n_comp: int = 5,
        n_features: int = 1,
        argvals=None,
        argvals_predict=None,
    ):
        self.n_comp = n_comp
        self.n_features = n_features
        self.argvals = argvals
        self.argvals_predict = argvals_predict

    def _split_X(self, X: NDArray, m: int) -> List[NDArray]:
        return [X[:, j * m : (j + 1) * m] for j in range(self.n_features)]

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        p = self.n_features
        if X.shape[1] % p != 0:
            raise ValueError(
                f"X has {X.shape[1]} columns, not divisible by n_features={p}"
            )
        m = X.shape[1] // p
        self.n_points_ = m

        if self.argvals is None:
            self.argvals_ = np.linspace(0, 1, m)
        else:
            self.argvals_ = np.asarray(self.argvals, dtype=np.float64)

        X_list = self._split_X(X, m)
        self.pls_ = _mfpls(X_list, self.argvals_, y, self.n_comp)
        self.n_outputs_ = y.shape[1]
        return self

    def _resolve_partial_grid(self, X):
        p = self.n_features
        m = self.n_points_
        m_c = X.shape[1] // p
        if X.shape[1] % p != 0:
            raise ValueError(f"X columns not divisible by n_features={p}")
        if m_c == m:
            return self.argvals_
        if self.argvals_predict is not None:
            ap = np.asarray(self.argvals_predict, dtype=np.float64)
            if len(ap) != m_c:
                raise ValueError("argvals_predict length mismatch")
            return ap
        return self.argvals_[:m_c]

    def predict(self, X):
        check_is_fitted(self)
        X = np.asarray(X, dtype=np.float64)
        argvals_partial = self._resolve_partial_grid(X)
        m_c = len(argvals_partial)
        X_list = self._split_X(X, m_c)

        # Map partial grid to full grid indices
        idx = np.searchsorted(self.argvals_, argvals_partial)

        if m_c == self.n_points_:
            # Full observation: use stored training projection formula
            # scores_new = X_centered_stacked @ W_star^T (with quadrature)
            W_x = np.tile(self.pls_["quad_x"], self.n_features)
            X_centered_stacked = np.hstack([
                (X_list[j] - self.pls_["mean_x"][j * self.n_points_:
                                                 (j + 1) * self.n_points_])
                * self.pls_["feature_weights"][j]
                for j in range(self.n_features)
            ])
            scores = X_centered_stacked @ (W_x * self.pls_["W_star"]).T
        else:
            scores = _scores_from_partial_pls(
                X_list, idx, argvals_partial, self.pls_,
            )

        y_pred = scores @ self.pls_["Q"] + self.pls_["mean_y"]
        return y_pred

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
# Comparison demo: MFPCA vs FPLS
# ===================================================================

if __name__ == "__main__":
    import sys, time
    sys.path.insert(0, ".")
    from partial_predictor_sklearn import FunctionalPartialRegressor
    from sklearn.model_selection import cross_validate

    np.random.seed(0)

    # --- Simulate functional data with strong X-Y dependence ----------
    n, m, p = 300, 60, 2
    t = np.linspace(0, 1, m)

    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])

    # Add noise modes orthogonal to Y (to penalize unsupervised methods)
    noise1 = np.array([0.8 * np.sin(10 * np.pi * t + np.random.uniform(0, 2 * np.pi))
                        for _ in range(n)])
    X1 = X1 + noise1  # X1 dominated by high-freq noise
    X2 = X2 + 0.3 * np.random.randn(n, m)

    # Response depends only on low-frequency content of X1, X2
    Y = (0.5 * np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
         + 0.3 * np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
         + 0.15 * np.random.randn(n, m))

    X = np.hstack([X1, X2])

    X_train, X_test = X[:200], X[200:]
    Y_train, Y_test = Y[:200], Y[200:]

    print("=" * 75)
    print("MFPCA vs FPLS — prediction quality at different K and horizons")
    print("=" * 75)
    print()
    print(f"   Setup: n_train=200, n_test=100, p=2 features, m={m} grid points")
    print( "   Y depends on low-freq modes of X; X has high-freq noise dominant")
    print( "   → unsupervised methods waste components on noise")
    print()

    for K in [2, 3, 5, 8, 12]:
        print(f"   K = {K} components:")
        for name, Cls in [
            ("MFPCA", lambda K=K: FunctionalPartialRegressor(
                n_comp=K, n_features=2, method="pace", argvals=t)),
            ("FPLS",  lambda K=K: FPLSPartialRegressor(
                n_comp=K, n_features=2, argvals=t)),
        ]:
            reg = Cls()
            reg.fit(X_train, Y_train)

            for frac in [1.0, 0.6, 0.3]:
                c = int(frac * m)
                X_te = X_test.copy() if c == m else \
                    np.hstack([X1[200:, :c], X2[200:, :c]])
                reg.argvals_predict = t[:c] if c < m else None
                y_hat = reg.predict(X_te)
                mse = np.mean((Y_test - y_hat) ** 2)
                r2 = reg.score(X_te, Y_test)
                if frac == 1.0:
                    print(f"     {name:6s} 100%: MSE={mse:.4f}  R²={r2:.4f}", end="")
                else:
                    print(f"   {int(frac*100)}%: MSE={mse:.4f}  R²={r2:.4f}", end="")
            print()
        print()

    # --- Cross-validation comparison ---------------------------------
    print("=" * 75)
    print("5-fold CV (full domain)")
    print("=" * 75)
    for name, Cls in [("MFPCA", FunctionalPartialRegressor),
                      ("FPLS",  FPLSPartialRegressor)]:
        print(f"\n   {name}:")
        for K in [3, 5, 8]:
            if name == "MFPCA":
                reg = Cls(n_comp=K, n_features=2, method="pace", argvals=t)
            else:
                reg = Cls(n_comp=K, n_features=2, argvals=t)
            t0 = time.perf_counter()
            cv = cross_validate(reg, X, Y, cv=5,
                                scoring="neg_mean_squared_error")
            elapsed = time.perf_counter() - t0
            print(f"     K={K}: MSE={-cv['test_score'].mean():.4f} "
                  f"+/- {cv['test_score'].std():.4f}  ({elapsed:.2f}s)")
