"""Conformal prediction intervals via the full puncc API.

Uses puncc's core architecture:
  - BasePredictor: wraps the regression model
  - BaseCalibrator: pairs a nonconformity score with a prediction-set builder
  - ConformalPredictor: orchestrates everything with a Splitter (split CP, CV+, etc.)

Two patterns for functional responses Y(t):

  Pattern 1 (pointwise): one conformal predictor per grid point, marginal
            coverage at each t.  Supports both split CP and CV+.

  Pattern 2 (simultaneous): single conformal predictor with a custom
            supremum-normalized nonconformity score, valid joint coverage
            for all t.  Supports both split CP and CV+.

Both accept any sklearn-compatible regressor producing multi-output
predictions.

Dependencies: numpy, scikit-learn, puncc (>=0.8)

    pip install puncc
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from numpy.typing import NDArray
from sklearn.base import BaseEstimator, clone

from deel.puncc.api.calibration import BaseCalibrator
from deel.puncc.api.conformalization import ConformalPredictor
from deel.puncc.api.prediction import BasePredictor
from deel.puncc.api.splitting import KFoldSplitter, RandomSplitter
from deel.puncc.api import nonconformity_scores as puncc_ncs
from deel.puncc.api import prediction_sets as puncc_ps


# ===================================================================
# Adapter wrappers
# ===================================================================

class _GridSliceWrapper:
    """Exposes a single grid-point slice of a multi-output regressor.

    puncc expects the wrapped model to have ``fit`` and ``predict``
    returning 1-D output.  ``fit`` is a no-op here because the parent
    regressor is already trained; puncc sees this via is_trained=True.
    """
    def __init__(self, regressor, idx):
        self.regressor = regressor
        self.idx = idx

    def fit(self, X, y, **kwargs):
        return self

    def predict(self, X):
        return self.regressor.predict(X)[:, self.idx]


class _MultiOutputPuncPredictor:
    """Thin wrapper passing multi-output predictions through puncc.

    puncc's BasePredictor accepts any object with ``fit``/``predict``.
    The predict here returns the full (n, m) matrix; our custom
    nonconformity score consumes that.
    """
    def __init__(self, regressor):
        self.regressor = regressor

    def fit(self, X, y, **kwargs):
        self.regressor.fit(X, y)
        return self

    def predict(self, X):
        return self.regressor.predict(X)


# ===================================================================
# Custom nonconformity score + prediction-set functions for Pattern 2
# ===================================================================

def _make_sup_scaled_score(sigma_t: NDArray):
    """Factory: supremum-normalized residual score for functional Y.

    s_i = max_t |y_pred_i(t) - y_true_i(t)| / sigma(t)

    Returns
    -------
    nonconf_score_func : callable(y_pred, y_true) -> (n,)
    pred_set_func      : callable(y_pred, scores_quantile) -> (lower, upper)
    """
    def nonconf_score(y_pred, y_true):
        return np.max(np.abs(y_true - y_pred) / sigma_t, axis=1)

    def pred_set(y_pred, scores_quantile):
        half_w = scores_quantile * sigma_t
        return y_pred - half_w, y_pred + half_w

    return nonconf_score, pred_set


def _estimate_sigma_t(y_true: NDArray, y_pred: NDArray, method: str = "mad") -> NDArray:
    residuals = y_true - y_pred
    if method == "mad":
        sigma = 1.4826 * np.median(np.abs(residuals), axis=0)
    elif method == "std":
        sigma = np.std(residuals, axis=0, ddof=1)
    elif method == "constant":
        sigma = np.ones(residuals.shape[1])
    else:
        raise ValueError(f"Unknown scale method: {method}")
    return np.maximum(sigma, 1e-12)


# ===================================================================
# Pattern 1: pointwise intervals using puncc's ConformalPredictor per t
# ===================================================================

class PointwisePunccIntervals:
    """One puncc ``SplitCP`` per grid point — pointwise coverage.

    Uses split conformal prediction.  For each grid point, a
    ``deel.puncc.regression.SplitCP`` instance is calibrated on the
    held-out fraction using the built-in ``absolute_difference``
    nonconformity score.  A single copy of the multi-output parent
    regressor is shared across all slices for efficiency.

    Coverage: P(Y(t) in band) >= 1 - alpha marginally at each t.
    Does NOT guarantee joint coverage across t.

    Parameters
    ----------
    regressor : sklearn regressor
    alpha : float
    cal_fraction : float
    seed : int
    """

    def __init__(
        self,
        regressor: BaseEstimator,
        alpha: float = 0.1,
        cal_fraction: float = 0.25,
        seed: int = 42,
    ):
        self.regressor = regressor
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.seed = seed

    def fit(self, X, y):
        """Fit one puncc SplitCP per grid point (parent model shared)."""
        from deel.puncc.regression import SplitCP

        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        m_y = y.shape[1]

        # Manual split (shared across slices)
        rng = np.random.default_rng(self.seed)
        n = X.shape[0]
        n_cal = max(int(n * self.cal_fraction), 2)
        perm = rng.permutation(n)
        cal_idx, fit_idx = perm[:n_cal], perm[n_cal:]

        # Fit parent multi-output regressor once on the training fold
        parent = clone(self.regressor)
        parent.fit(X[fit_idx], y[fit_idx])

        # One puncc SplitCP per grid point, all sharing the parent
        self.conformal_predictors_ = []
        for t_idx in range(m_y):
            wrapper = _GridSliceWrapper(parent, t_idx)
            predictor = BasePredictor(wrapper, is_trained=True)
            cp = SplitCP(predictor=predictor, train=False,
                         random_state=self.seed)
            cp.fit(X_calib=X[cal_idx], y_calib=y[cal_idx, t_idx])
            self.conformal_predictors_.append(cp)

        self.m_y_ = m_y
        return self

    def predict(self, X, alpha=None) -> Tuple[NDArray, NDArray, NDArray]:
        if alpha is None:
            alpha = self.alpha
        X = np.asarray(X, dtype=np.float64)
        n_test = X.shape[0]
        y_pred = np.empty((n_test, self.m_y_))
        lower = np.empty((n_test, self.m_y_))
        upper = np.empty((n_test, self.m_y_))

        for t_idx, cp in enumerate(self.conformal_predictors_):
            y_p, y_lo, y_hi = cp.predict(X, alpha=alpha)
            y_pred[:, t_idx] = y_p
            lower[:, t_idx] = y_lo
            upper[:, t_idx] = y_hi

        return y_pred, lower, upper


# ===================================================================
# Pattern 2: simultaneous band using puncc's ConformalPredictor with
#            a custom sup-normalized nonconformity score
# ===================================================================

class SimultaneousPunccIntervals:
    """Simultaneous conformal band via puncc's SplitCP with custom score.

    Uses puncc's full architecture:

        SplitCP(
            predictor=BasePredictor(multi_output_regressor, is_trained=True),
            train=False,
        )
        + BaseCalibrator(
            nonconf_score_func=sup_normalized_residual,   # our custom
            pred_set_func=sup_normalized_interval,        # our custom
        )

    The custom nonconformity score is the **supremum of normalized
    absolute residuals**:

        s_i = max_t  |y_pred_i(t) - y_true_i(t)|  /  sigma(t)

    where sigma(t) is estimated by MAD on a pilot fit.  The
    corresponding prediction-set function produces

        y_pred(t) +/- q_{1-alpha} * sigma(t)

    giving simultaneous coverage P(Y(t) in band for ALL t) >= 1 - alpha
    with locally adaptive band width.

    Note: puncc's CV+ does not support multi-output custom scores (its
    internal calibrator expects scalar y).  If you need CV+ variants,
    use them per-grid-point (Pattern 1) which gets pointwise CV+ for free.

    Parameters
    ----------
    regressor : sklearn regressor (multi-output)
    alpha : float
    cal_fraction : float
    scale : str
        "mad", "std", or "constant".
    seed : int
    """

    def __init__(
        self,
        regressor: BaseEstimator,
        alpha: float = 0.1,
        cal_fraction: float = 0.25,
        scale: str = "mad",
        seed: int = 42,
    ):
        self.regressor = regressor
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.scale = scale
        self.seed = seed

    def fit(self, X, y):
        """Fit puncc SplitCP with our custom supremum-normalized score."""
        from deel.puncc.regression import SplitCP

        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        # Manual train/calibration split
        rng = np.random.default_rng(self.seed)
        n = X.shape[0]
        n_cal = max(int(n * self.cal_fraction), 2)
        perm = rng.permutation(n)
        cal_idx, fit_idx = perm[:n_cal], perm[n_cal:]

        # Fit parent regressor on training portion
        parent = clone(self.regressor)
        parent.fit(X[fit_idx], y[fit_idx])

        # Estimate sigma(t) from training residuals
        self.sigma_t_ = _estimate_sigma_t(
            y[fit_idx], parent.predict(X[fit_idx]), self.scale,
        )

        # Build custom nonconformity score + prediction-set functions
        nonconf_score, pred_set = _make_sup_scaled_score(self.sigma_t_)

        # puncc SplitCP with pre-fitted multi-output predictor
        wrapped = _MultiOutputPuncPredictor(parent)
        predictor = BasePredictor(wrapped, is_trained=True)
        cp = SplitCP(predictor=predictor, train=False,
                     random_state=self.seed)

        # Swap in our custom calibrator (SplitCP defaults to MAD interval)
        cp.calibrator = BaseCalibrator(
            nonconf_score_func=nonconf_score,
            pred_set_func=pred_set,
        )
        cp.conformal_predictor.calibrator = cp.calibrator

        # Calibrate
        cp.fit(X_calib=X[cal_idx], y_calib=y[cal_idx])
        self.conformal_predictor_ = cp
        self.m_y_ = y.shape[1]
        return self

    def predict(self, X, alpha=None) -> Tuple[NDArray, NDArray, NDArray]:
        if alpha is None:
            alpha = self.alpha
        X = np.asarray(X, dtype=np.float64)
        y_pred, lower, upper = self.conformal_predictor_.predict(X, alpha=alpha)
        return y_pred, lower, upper


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    import sys, warnings
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    sys.path.insert(0, ".")
    from partial_predictor_sklearn import FunctionalPartialRegressor

    np.random.seed(0)

    n, m, p = 200, 40, 2
    t = np.linspace(0, 1, m)
    X1 = np.array([np.sin(2*np.pi*t + phi) + 0.3*np.random.randn(m)
                    for phi in np.random.uniform(0, 2*np.pi, n)])
    X2 = np.array([np.cos(4*np.pi*t + phi) + 0.3*np.random.randn(m)
                    for phi in np.random.uniform(0, 2*np.pi, n)])
    Y = 0.5*X1 + 0.3*X2 + 0.2*np.random.randn(n, m)
    X = np.hstack([X1, X2])

    X_train, X_test = X[:150], X[150:]
    Y_train, Y_test = Y[:150], Y[150:]

    def evaluate(name, y_pred, lower, upper):
        cov_sim = np.all((Y_test >= lower) & (Y_test <= upper), axis=1).mean()
        cov_pw = np.mean((Y_test >= lower) & (Y_test <= upper))
        width = np.mean(upper - lower)
        print(f"   {name:35s}  sim={cov_sim:4.0%}  pw={cov_pw:4.0%}  "
              f"width={width:.4f}")

    # --- Pattern 1 -------------------------------------------------------
    print("=" * 70)
    print("Pattern 1: pointwise intervals (puncc SplitCP per grid point)")
    print("=" * 70)

    reg = FunctionalPartialRegressor(
        n_comp=5, n_features=2, method="pace", argvals=t,
    )
    pw = PointwisePunccIntervals(reg, alpha=0.1)
    pw.fit(X_train, Y_train)
    y_pred, lower, upper = pw.predict(X_test)
    evaluate("Pattern 1 (SplitCP per t)", y_pred, lower, upper)

    # --- Pattern 2 -------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Pattern 2: simultaneous band (puncc SplitCP + custom score)")
    print("=" * 70)

    for scale in ["mad", "std", "constant"]:
        reg = FunctionalPartialRegressor(
            n_comp=5, n_features=2, method="pace", argvals=t,
        )
        sim = SimultaneousPunccIntervals(reg, alpha=0.1, scale=scale)
        sim.fit(X_train, Y_train)
        y_pred, lower, upper = sim.predict(X_test)
        evaluate(f"Pattern 2 (scale={scale})", y_pred, lower, upper)

    print(f"\n{'=' * 70}")
    print("Target: 90% for 'pw' (Pattern 1), 90% for 'sim' (Pattern 2).")
    print(f"{'=' * 70}")
