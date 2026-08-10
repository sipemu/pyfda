"""Conformalized Quantile Regression (CQR) for functional responses.

Wraps a FunctionalPartialRegressor with adaptive prediction intervals
whose width varies per observation (unlike vanilla split conformal).

The idea:
  1. Fit base regressor for point predictions  y_hat(t)
  2. Fit two pointwise quantile regressors on MFPCA scores
     at alpha/2 and 1-alpha/2 -> q_lo(X)(t) and q_hi(X)(t)
  3. On the calibration set, compute CQR nonconformity scores
     E_i(t) = max(q_lo(X_i)(t) - Y_i(t), Y_i(t) - q_hi(X_i)(t))
  4. Q = quantile of {sup_t E_i(t)} (or per-t for pointwise) at level
     (1-alpha)*(n+1)/n
  5. Prediction interval: [q_lo(X) - Q, q_hi(X) + Q]

Interface follows puncc_integration.py (composition pattern): pass a
pre-built FunctionalPartialRegressor as the first argument.

Reference: Romano, Patterson, Candès (2019), "Conformalized Quantile
Regression", NeurIPS.

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from numpy.typing import NDArray
from sklearn.base import clone
from sklearn.linear_model import QuantileRegressor

import sys
sys.path.insert(0, ".")
from partial_predictor_sklearn import (
    FunctionalPartialRegressor,
    _trapezoidal_weights,
    _scores_pace,
    _scores_truncated,
)


# ===================================================================
# Helpers
# ===================================================================

def _fit_pointwise_quantile(
    scores: NDArray,
    Y: NDArray,
    quantile: float,
    alpha_reg: float = 0.0,
    solver: str = "highs",
) -> Tuple[NDArray, NDArray]:
    """Fit one linear quantile regression per output grid point.

    Returns (betas (K, m_y), intercepts (m_y,)).
    """
    K = scores.shape[1]
    m_y = Y.shape[1]
    betas = np.zeros((K, m_y))
    intercepts = np.zeros(m_y)
    for t in range(m_y):
        qr = QuantileRegressor(
            quantile=quantile, alpha=alpha_reg, solver=solver,
        )
        qr.fit(scores, Y[:, t])
        betas[:, t] = qr.coef_
        intercepts[t] = qr.intercept_
    return betas, intercepts


def _extract_scores(reg: FunctionalPartialRegressor, X: NDArray) -> NDArray:
    """Extract MFPCA scores from a fitted FunctionalPartialRegressor."""
    X = np.asarray(X, dtype=np.float64)
    p = reg.n_features
    m = reg.n_points_
    m_c = X.shape[1] // p
    Xs = [X[:, j * m_c : (j + 1) * m_c] for j in range(p)]

    if m_c == m:
        argvals_partial = reg.argvals_
    elif reg.argvals_predict is not None:
        argvals_partial = np.asarray(reg.argvals_predict, dtype=np.float64)
    else:
        argvals_partial = reg.argvals_[:m_c]

    idx = np.searchsorted(reg.argvals_, argvals_partial)
    if reg.method == "pace" and reg.sigma2_ is not None:
        scores, _ = _scores_pace(Xs, idx, reg.mfpca_, reg.sigma2_)
    else:
        quad = _trapezoidal_weights(argvals_partial)
        scores = _scores_truncated(Xs, idx, quad, reg.mfpca_)
    return scores


# ===================================================================
# CQR wrapper (composition pattern, like PointwisePunccIntervals)
# ===================================================================

class CQRPunccIntervals:
    """Conformalized Quantile Regression with adaptive band widths.

    Wraps a FunctionalPartialRegressor in the same style as
    PointwisePunccIntervals / SimultaneousPunccIntervals.  Bands have
    *per-observation* widths that adapt to local difficulty (unlike
    split conformal which gives the same width to every test point).

    Parameters
    ----------
    regressor : FunctionalPartialRegressor
        Unfitted regressor; the wrapper clones and fits it internally.
    alpha : float
        Miscoverage target (e.g. 0.1 -> 90% coverage).
    cal_fraction : float
        Fraction held out for CQR calibration.
    simultaneous : bool
        If True, single Q from sup over t (simultaneous coverage).
        If False, per-t Q (pointwise coverage).
    quantile_alpha : float
        L1 regularization for the linear quantile regressors (0 = none).
    seed : int

    Example
    -------
    >>> reg = FunctionalPartialRegressor(
    ...     n_comp=5, n_features=2, method="pace", argvals=t,
    ... )
    >>> cqr = CQRPunccIntervals(reg, alpha=0.1, simultaneous=True)
    >>> cqr.fit(X_train, Y_train)
    >>> y_pred, lower, upper = cqr.predict(X_test)   # triple, like puncc wrappers
    """

    def __init__(
        self,
        regressor: FunctionalPartialRegressor,
        alpha: float = 0.1,
        cal_fraction: float = 0.25,
        simultaneous: bool = True,
        quantile_alpha: float = 0.0,
        seed: int = 42,
    ):
        if not isinstance(regressor, FunctionalPartialRegressor):
            raise TypeError(
                "CQRPunccIntervals requires a FunctionalPartialRegressor "
                "(needs access to MFPCA scores for the quantile regressors)."
            )
        self.regressor = regressor
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.simultaneous = simultaneous
        self.quantile_alpha = quantile_alpha
        self.seed = seed

    def fit(self, X, y):
        """Train base regressor + quantile regressors, then CQR-calibrate."""
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        # Train/cal split (shared by base + quantile + CQR calibration)
        rng = np.random.default_rng(self.seed)
        n = X.shape[0]
        n_cal = max(int(n * self.cal_fraction), 2)
        perm = rng.permutation(n)
        cal_idx, fit_idx = perm[:n_cal], perm[n_cal:]
        X_fit, X_cal = X[fit_idx], X[cal_idx]
        y_fit, y_cal = y[fit_idx], y[cal_idx]

        # Fit base regressor on the training fold
        self.regressor_ = clone(self.regressor)
        self.regressor_.fit(X_fit, y_fit)

        # Extract training-fold MFPCA scores (full-grid projection)
        train_scores = _extract_scores(self.regressor_, X_fit)

        # Fit two pointwise quantile regressors
        self.q_lo_betas_, self.q_lo_intercept_ = _fit_pointwise_quantile(
            train_scores, y_fit, quantile=self.alpha / 2,
            alpha_reg=self.quantile_alpha,
        )
        self.q_hi_betas_, self.q_hi_intercept_ = _fit_pointwise_quantile(
            train_scores, y_fit, quantile=1 - self.alpha / 2,
            alpha_reg=self.quantile_alpha,
        )

        # CQR calibration on held-out set (full-grid scores)
        cal_scores = _extract_scores(self.regressor_, X_cal)
        q_lo_cal = cal_scores @ self.q_lo_betas_ + self.q_lo_intercept_
        q_hi_cal = cal_scores @ self.q_hi_betas_ + self.q_hi_intercept_

        # Nonconformity score: E_i(t) = max(lo - y, y - hi)
        E = np.maximum(q_lo_cal - y_cal, y_cal - q_hi_cal)  # (n_cal, m_y)

        n_cal_actual = len(cal_idx)
        q_level = min(
            np.ceil((1 - self.alpha) * (n_cal_actual + 1)) / n_cal_actual,
            1.0,
        )
        if self.simultaneous:
            sup_E = E.max(axis=1)
            self.conformal_correction_ = float(np.quantile(sup_E, q_level))
        else:
            self.conformal_correction_ = np.quantile(E, q_level, axis=0)

        self.m_y_ = y.shape[1]
        return self

    def predict(self, X, alpha=None) -> Tuple[NDArray, NDArray, NDArray]:
        """Return (y_pred, lower, upper) — matches puncc wrapper API.

        Note: ``alpha`` is reused from fit time; passing a different
        value here only changes which mode (simultaneous/pointwise)
        correction is reapplied — it does NOT re-calibrate.
        """
        if not hasattr(self, "regressor_"):
            raise RuntimeError("Call .fit(X, y) before .predict()")

        # Point prediction via the fitted base regressor
        y_pred = self.regressor_.predict(X)

        # Adaptive quantiles (per observation, per grid point)
        scores = _extract_scores(self.regressor_, X)
        q_lo = scores @ self.q_lo_betas_ + self.q_lo_intercept_
        q_hi = scores @ self.q_hi_betas_ + self.q_hi_intercept_

        # CQR additive correction
        if self.simultaneous:
            correction = self.conformal_correction_
            if not np.isscalar(correction):
                correction = float(np.max(correction))
            lower = q_lo - correction
            upper = q_hi + correction
        else:
            correction = self.conformal_correction_
            if np.isscalar(correction):
                correction = np.full(self.m_y_, correction)
            lower = q_lo - correction
            upper = q_hi + correction

        upper = np.maximum(upper, lower)  # sanity
        return y_pred, lower, upper


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    np.random.seed(0)

    n, m = 300, 40
    t = np.linspace(0, 1, m)

    # Heteroscedastic data: noise varies per sample
    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
    noise_scale = 0.05 + 0.5 * (1 + np.cos(phases1))  # in [0.05, 1.05]
    X1 = X1 + noise_scale[:, None] * np.random.randn(n, m)
    X2 = X2 + 0.2 * np.random.randn(n, m)
    Y = (0.5 * np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
         + 0.3 * np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
         + noise_scale[:, None] * 0.3 * np.random.randn(n, m))
    X = np.hstack([X1, X2])

    X_train, X_test = X[:200], X[200:]
    Y_train, Y_test = Y[:200], Y[200:]
    noise_test = noise_scale[200:]

    print("=" * 75)
    print("CQRPunccIntervals — composition-pattern interface")
    print("=" * 75)

    # --- Wrapper pattern: build base regressor, then wrap ---------
    reg = FunctionalPartialRegressor(
        n_comp=5, n_features=2, method="pace", argvals=t,
    )
    cqr = CQRPunccIntervals(reg, alpha=0.1, simultaneous=True)
    cqr.fit(X_train, Y_train)
    y_pred, lower, upper = cqr.predict(X_test)

    widths = (upper - lower).mean(axis=1)
    cov = np.all((Y_test >= lower) & (Y_test <= upper), axis=1).mean()
    print(f"\nFull domain (n_test={len(X_test)}):")
    print(f"  Simultaneous coverage:     {cov:.0%}")
    print(f"  Band width std across obs: {widths.std():.4f}  (adaptive)")
    print(f"  Band width range:          [{widths.min():.2f}, "
          f"{widths.max():.2f}]")
    print(f"  Correlation(width, σ):     "
          f"{np.corrcoef(widths, noise_test)[0, 1]:+.3f}")

    # --- Partial observation ------------------------------------------
    print(f"\nPartial observation:")
    for frac in [1.0, 0.6, 0.3]:
        c = int(frac * m)
        X_te = X_test if c == m else np.hstack([X1[200:, :c], X2[200:, :c]])
        cqr.regressor_.argvals_predict = t[:c] if c < m else None
        y_p, lo, up = cqr.predict(X_te)
        widths = (up - lo).mean(axis=1)
        cov = np.all((Y_test >= lo) & (Y_test <= up), axis=1).mean()
        print(f"  {frac:4.0%}: cov={cov:.0%}  "
              f"width range=[{widths.min():.2f}, {widths.max():.2f}]  "
              f"corr(w, σ)={np.corrcoef(widths, noise_test)[0, 1]:+.3f}")
