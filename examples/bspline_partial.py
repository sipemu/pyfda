"""B-spline coefficient regressor with Bayesian prior for partial observations.

Drop-in alternative to FunctionalPartialRegressor.  Replaces MFPCA's
data-driven basis with a fixed P-spline basis (B-splines with
second-difference smoothness penalty), then maps coefficients to Y(t)
with pointwise OLS.

For partial observations X|_{[a,c]} we use a Gaussian (ridge) prior on
the coefficient vector estimated from training data:

    c | X_obs  ~  N(mu_post, Sigma_post)
    Sigma_post^{-1} = (1/sigma2) B_obs^T B_obs  +  Sigma_prior^{-1}
    mu_post = Sigma_post @ [(1/sigma2) B_obs^T X_obs + Sigma_prior^{-1} mu_prior]

The prior pulls coefficients of basis functions outside the observed
domain toward the training mean, which is the natural Bayesian way of
handling missing input regions.

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import BSpline
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted


# ===================================================================
# Basis construction
# ===================================================================

def _bspline_knots(t_min: float, t_max: float, n_basis: int, degree: int = 3) -> NDArray:
    """Knot sequence for clamped B-splines with `n_basis` basis functions."""
    n_internal = n_basis - degree - 1
    if n_internal < 0:
        raise ValueError(
            f"n_basis must be at least degree+1 = {degree+1}"
        )
    if n_internal > 0:
        internal = np.linspace(t_min, t_max, n_internal + 2)[1:-1]
    else:
        internal = np.array([])
    return np.concatenate([
        np.full(degree + 1, t_min),
        internal,
        np.full(degree + 1, t_max),
    ])


def _bspline_design(
    argvals: NDArray,
    n_basis: int,
    degree: int = 3,
    knots: Optional[NDArray] = None,
) -> Tuple[NDArray, NDArray]:
    """Build B-spline design matrix B of shape (m, n_basis).

    Returns (B, knots).
    """
    if knots is None:
        knots = _bspline_knots(argvals[0], argvals[-1], n_basis, degree)
    B = np.zeros((len(argvals), n_basis))
    eye = np.eye(n_basis)
    for k in range(n_basis):
        spl = BSpline(knots, eye[k], degree, extrapolate=False)
        B[:, k] = spl(argvals)
    # Replace NaN (from extrapolate=False) with 0 — happens at exact boundary
    B = np.nan_to_num(B, nan=0.0)
    return B, knots


def _diff_matrix(n: int, order: int = 2) -> NDArray:
    """Second-difference operator D^k of shape (n-k, n)."""
    D = np.eye(n)
    for _ in range(order):
        D = np.diff(D, axis=0)
    return D


# ===================================================================
# Coefficient fitting
# ===================================================================

def _fit_coefs_full(
    X: NDArray,
    B: NDArray,
    DtD: NDArray,
    lam: float,
) -> NDArray:
    """P-spline coefficients for each row of X.

    Solves  (B^T B + lam * D^T D) c = B^T X  per sample.

    Parameters
    ----------
    X : (n, m)
    B : (m, n_basis)
    DtD : (n_basis, n_basis) — D^T D from the difference operator
    lam : float

    Returns
    -------
    coefs : (n, n_basis)
    """
    M = B.T @ B + lam * DtD
    rhs = B.T @ X.T  # (n_basis, n)
    return np.linalg.solve(M, rhs).T


def _estimate_prior(coefs: NDArray, ridge: float = 1e-6) -> Tuple[NDArray, NDArray]:
    """Estimate Gaussian prior over coefficients from training set.

    Returns (mean, precision_matrix).
    """
    n_basis = coefs.shape[1]
    mu = coefs.mean(axis=0)
    centered = coefs - mu
    Sigma = centered.T @ centered / max(coefs.shape[0] - 1, 1)
    Sigma += ridge * np.eye(n_basis)
    Sigma_inv = np.linalg.inv(Sigma)
    return mu, Sigma_inv


def _fit_coefs_partial_bayes(
    X_partial: NDArray,
    B_partial: NDArray,
    mu_prior: NDArray,
    Sigma_prior_inv: NDArray,
    sigma2: float,
    lam: float,
    DtD: NDArray,
) -> NDArray:
    """Posterior mean coefficients given partial observation.

    Parameters
    ----------
    X_partial : (n_new, m_c)
    B_partial : (m_c, n_basis) — B-spline basis evaluated on observed grid
    mu_prior : (n_basis,)
    Sigma_prior_inv : (n_basis, n_basis)
    sigma2 : scalar noise variance
    lam : smoothness penalty (also retained in the posterior)
    DtD : (n_basis, n_basis)

    Returns
    -------
    coefs : (n_new, n_basis)
    """
    BtB = B_partial.T @ B_partial / sigma2
    prec = BtB + Sigma_prior_inv + lam * DtD
    BtX = B_partial.T @ X_partial.T / sigma2  # (n_basis, n_new)
    rhs = BtX + (Sigma_prior_inv @ mu_prior)[:, None]
    return np.linalg.solve(prec, rhs).T


# ===================================================================
# Sklearn estimator
# ===================================================================

class BSplinePartialRegressor(BaseEstimator, RegressorMixin):
    """Partial-domain functional-on-functional regressor via B-splines.

    Pipeline:
        X (full or partial)
           → P-spline coefficients (Bayesian posterior for partial)
           → pointwise OLS on stacked coefficients
           → Y(t)

    Parameters
    ----------
    n_basis : int
        Number of B-spline basis functions per feature (default 15).
    degree : int
        B-spline degree (default 3 = cubic).
    lam : float
        Smoothness penalty for second differences of coefficients.
        Larger = smoother coefficient curve.  Default 1e-2.
    n_features : int
        Number of functional predictors p.
    argvals : array-like or None
    argvals_predict : array-like or None
    alpha : float
        Conformal miscoverage level for prediction intervals.
    cal_fraction : float
    seed : int
    """

    def __init__(
        self,
        n_basis: int = 15,
        degree: int = 3,
        lam: float = 1e-2,
        n_features: int = 1,
        argvals=None,
        argvals_predict=None,
        alpha: float = 0.1,
        cal_fraction: float = 0.25,
        seed: int = 42,
    ):
        self.n_basis = n_basis
        self.degree = degree
        self.lam = lam
        self.n_features = n_features
        self.argvals = argvals
        self.argvals_predict = argvals_predict
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.seed = seed

    def _split_X(self, X: NDArray, m: int) -> List[NDArray]:
        return [X[:, j * m : (j + 1) * m] for j in range(self.n_features)]

    # ----- fit -------------------------------------------------------

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        p = self.n_features
        if X.shape[1] % p != 0:
            raise ValueError(
                f"X columns {X.shape[1]} not divisible by n_features={p}"
            )
        m = X.shape[1] // p
        self.n_points_ = m

        if self.argvals is None:
            self.argvals_ = np.linspace(0, 1, m)
        else:
            self.argvals_ = np.asarray(self.argvals, dtype=np.float64)

        # Build basis on the full grid (per-feature copies share basis)
        self.B_, self.knots_ = _bspline_design(
            self.argvals_, self.n_basis, self.degree,
        )
        self.D_ = _diff_matrix(self.n_basis, order=2)
        self.DtD_ = self.D_.T @ self.D_

        # Train/cal split for conformal calibration
        rng = np.random.default_rng(self.seed)
        n = X.shape[0]
        n_cal = max(int(n * self.cal_fraction), 2)
        perm = rng.permutation(n)
        cal_idx, train_idx = perm[:n_cal], perm[n_cal:]
        X_train, X_cal = X[train_idx], X[cal_idx]
        y_train, y_cal = y[train_idx], y[cal_idx]
        if sample_weight is not None:
            sample_weight = np.asarray(sample_weight, dtype=np.float64)
            w_train = sample_weight[train_idx]
        else:
            w_train = None

        # Per-feature: fit coefficients + estimate prior + noise variance
        Xs_train = self._split_X(X_train, m)
        self.priors_ = []   # list of (mu_prior, Sigma_prior_inv) per feature
        self.sigma2_ = np.zeros(p)
        coefs_list = []
        for j in range(p):
            coefs_j = _fit_coefs_full(Xs_train[j], self.B_,
                                       self.DtD_, self.lam)
            coefs_list.append(coefs_j)
            mu_j, Sinv_j = _estimate_prior(coefs_j)
            self.priors_.append((mu_j, Sinv_j))
            # Residual variance (in original X space)
            X_hat = coefs_j @ self.B_.T
            res = Xs_train[j] - X_hat
            self.sigma2_[j] = max(np.var(res), 1e-8)

        # Stacked feature matrix: (n_train, p * n_basis)
        self.train_coefs_ = np.hstack(coefs_list)

        # Pointwise OLS on coefficients → Y
        self.regression_ = self._fit_regression(
            self.train_coefs_, y_train, sample_weight=w_train,
        )

        # Conformal calibration on held-out set
        coefs_cal = self._coefs_from_X(X_cal, m)
        y_cal_hat = coefs_cal @ self.regression_["beta"] + \
                     self.regression_["intercept"]
        cal_res = np.abs(y_cal - y_cal_hat)

        self.sigma_t_ = np.maximum(
            1.4826 * np.median(cal_res, axis=0), 1e-12
        )
        norm_res = cal_res / self.sigma_t_
        n_cal_actual = len(cal_idx)
        q_lvl = min(np.ceil((1 - self.alpha) * (n_cal_actual + 1))
                     / n_cal_actual, 1.0)
        self.conformal_q_sim_ = float(
            np.quantile(norm_res.max(axis=1), q_lvl)
        )
        self.conformal_q_pw_ = np.quantile(norm_res, q_lvl, axis=0)

        self.n_outputs_ = y.shape[1]
        return self

    @staticmethod
    def _fit_regression(scores, Y, sample_weight=None):
        K = scores.shape[1]
        if sample_weight is None:
            mu_y = Y.mean(axis=0)
            Yc = Y - mu_y
            beta = np.linalg.solve(
                scores.T @ scores + 1e-8 * np.eye(K),
                scores.T @ Yc,
            )
        else:
            w = sample_weight
            mu_y = (Y * w[:, None]).sum(axis=0) / w.sum()
            Yc = Y - mu_y
            SwS = (scores.T * w) @ scores
            SwY = (scores.T * w) @ Yc
            beta = np.linalg.solve(SwS + 1e-8 * np.eye(K), SwY)
        residuals = Y - (scores @ beta + mu_y)
        return dict(beta=beta, intercept=mu_y, residuals=residuals)

    # ----- helper: extract coefficients from (possibly partial) X ----

    def _coefs_from_X(self, X: NDArray, m_full: int) -> NDArray:
        p = self.n_features
        m_c = X.shape[1] // p
        Xs = self._split_X(X, m_c)
        coefs_list = []
        if m_c == m_full:
            # Full observation: P-spline fit
            for j in range(p):
                coefs_j = _fit_coefs_full(Xs[j], self.B_,
                                           self.DtD_, self.lam)
                coefs_list.append(coefs_j)
        else:
            # Partial observation: Bayesian posterior per feature
            argvals_partial = self._resolve_partial_grid(X)
            B_partial, _ = _bspline_design(
                argvals_partial, self.n_basis, self.degree,
                knots=self.knots_,  # reuse training knots
            )
            for j in range(p):
                mu_j, Sinv_j = self.priors_[j]
                coefs_j = _fit_coefs_partial_bayes(
                    Xs[j], B_partial, mu_j, Sinv_j,
                    self.sigma2_[j], self.lam, self.DtD_,
                )
                coefs_list.append(coefs_j)
        return np.hstack(coefs_list)

    def _resolve_partial_grid(self, X):
        p = self.n_features
        m = self.n_points_
        m_c = X.shape[1] // p
        if m_c == m:
            return self.argvals_
        if self.argvals_predict is not None:
            ap = np.asarray(self.argvals_predict, dtype=np.float64)
            if len(ap) != m_c:
                raise ValueError("argvals_predict length mismatch")
            return ap
        return self.argvals_[:m_c]

    # ----- predict ---------------------------------------------------

    def predict(self, X):
        check_is_fitted(self)
        X = np.asarray(X, dtype=np.float64)
        coefs = self._coefs_from_X(X, self.n_points_)
        return coefs @ self.regression_["beta"] + self.regression_["intercept"]

    def predict_interval(self, X, alpha=None, simultaneous=True):
        check_is_fitted(self)
        if alpha is None:
            alpha = self.alpha
        y_hat = self.predict(X)
        if simultaneous:
            half_w = self.conformal_q_sim_ * self.sigma_t_
        else:
            half_w = self.conformal_q_pw_ * self.sigma_t_
        return y_hat, y_hat - half_w, y_hat + half_w

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
# Demo + comparison vs MFPCA
# ===================================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from partial_predictor_sklearn import FunctionalPartialRegressor

    np.random.seed(0)

    # --- Simulate ----------------------------------------------------
    n, m, p = 300, 60, 2
    t = np.linspace(0, 1, m)
    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
    X1 += 0.3 * np.random.randn(n, m)
    X2 += 0.3 * np.random.randn(n, m)
    Y = (0.5 * np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
         + 0.3 * np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
         + 0.15 * np.random.randn(n, m))
    X = np.hstack([X1, X2])

    X_train, X_test = X[:200], X[200:]
    Y_train, Y_test = Y[:200], Y[200:]

    print("=" * 75)
    print("MFPCA vs B-spline (P-spline, Bayesian prior on partial obs)")
    print("=" * 75)

    methods = {
        "MFPCA (n_comp=8)": lambda: FunctionalPartialRegressor(
            n_comp=8, n_features=2, method="pace", argvals=t),
        "B-spline (15 basis, λ=1e-2)": lambda: BSplinePartialRegressor(
            n_basis=15, lam=1e-2, n_features=2, argvals=t),
        "B-spline (20 basis, λ=1e-3)": lambda: BSplinePartialRegressor(
            n_basis=20, lam=1e-3, n_features=2, argvals=t),
        "B-spline (10 basis, λ=1e-1)": lambda: BSplinePartialRegressor(
            n_basis=10, lam=1e-1, n_features=2, argvals=t),
    }

    print(f"\n   {'Method':<32s} {'100%':>10s} {'60%':>10s} {'30%':>10s}")
    print("   " + "─" * 65)
    for name, factory in methods.items():
        reg = factory()
        reg.fit(X_train, Y_train)
        row = f"   {name:<32s}"
        for frac in [1.0, 0.6, 0.3]:
            c = int(frac * m)
            X_te = X_test if c == m else \
                np.hstack([X1[200:, :c], X2[200:, :c]])
            reg.argvals_predict = t[:c] if c < m else None
            r2 = reg.score(X_te, Y_test)
            row += f"  R²={r2:.3f}"
        print(row)

    # --- Coverage with conformal -------------------------------------
    print(f"\n{'=' * 75}")
    print("Coverage and band width (conformal, simultaneous, α=0.1)")
    print("=" * 75)
    print(f"\n   {'Method':<32s} {'100%':>15s} {'60%':>15s} {'30%':>15s}")
    print("   " + "─" * 90)
    for name, factory in methods.items():
        reg = factory()
        reg.fit(X_train, Y_train)
        row = f"   {name:<32s}"
        for frac in [1.0, 0.6, 0.3]:
            c = int(frac * m)
            X_te = X_test if c == m else \
                np.hstack([X1[200:, :c], X2[200:, :c]])
            reg.argvals_predict = t[:c] if c < m else None
            try:
                y_p, lo, up = reg.predict_interval(X_te)
                cov = np.all((Y_test >= lo) & (Y_test <= up), axis=1).mean()
                width = (up - lo).mean()
                row += f"  cov={cov:.0%} w={width:.2f}"
            except AttributeError:
                row += " " * 18
        print(row)
