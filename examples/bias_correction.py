"""Bias-corrected wrapper for partial-domain functional regression.

Approach 3 from earlier discussion: train a separate "bias estimator"
that predicts the residual curve given:
  - MFPCA scores from the partial observation
  - The cutoff t* itself (as a scalar covariate)

At deployment, where only X (no Y) is available, we extract the same
features and add the predicted bias to the point prediction.

This corrects systematic bias that increases with t (or with smaller
observation horizons) without distributional assumptions on Y.  Pair
with conformal intervals on top of the corrected predictor for valid
coverage.

Interface follows puncc_integration.py — composition pattern:
   bc = BiasCorrectedRegressor(reg, cutoff_grid=[10, 20, 30, 40])
   bc.fit(X, y)
   y_corr = bc.predict(X_partial)

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Union

import numpy as np
from numpy.typing import NDArray
from sklearn.base import clone
from sklearn.linear_model import Ridge

import sys
sys.path.insert(0, ".")
from partial_predictor_sklearn import (
    FunctionalPartialRegressor,
    _trapezoidal_weights,
    _scores_pace,
    _scores_truncated,
)


# ===================================================================
# Shared helper (same as cqr_intervals._extract_scores)
# ===================================================================

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


def _build_partial_X(X: NDArray, n_features: int, m: int, cutoff_idx: int) -> NDArray:
    """Slice stacked X (n, p*m) to keep first cutoff_idx points per feature."""
    return np.hstack([
        X[:, j * m : j * m + cutoff_idx] for j in range(n_features)
    ])


# ===================================================================
# Bias-corrected regressor
# ===================================================================

class BiasCorrectedRegressor:
    """Bias-corrected wrapper for FunctionalPartialRegressor.

    Training (using calibration split):
      1. Fit base regressor on the training portion.
      2. On the calibration portion, simulate "as if observed up to
         cutoff k" for each k in cutoff_grid:
            - Build partial X
            - Predict Y_hat via the base regressor
            - Residual R = Y - Y_hat
            - Features: (MFPCA scores from partial X) + (cutoff time)
            - Target: R(s)
      3. Fit one bias regressor across all cutoffs jointly.

    Deployment (only X available):
      1. Determine cutoff from X.shape
      2. Predict Y_hat via base regressor (handles partial natively)
      3. Predict bias R_hat via the bias regressor
      4. Return Y_hat + R_hat

    Parameters
    ----------
    regressor : FunctionalPartialRegressor
        Base regressor.  Cloned and fit internally.
    cutoff_grid : sequence of int or None
        Cutoff indices into argvals (e.g. [10, 20, 30, 40]).
        If None, uses 5 evenly spaced cutoffs across the domain.
    bias_regressor : sklearn estimator or None
        Maps (scores, cutoff_t) -> residual curve.  Default: Ridge.
        Use HistGradientBoostingRegressor wrapped in MultiOutputRegressor
        for non-linear bias patterns.
    cal_fraction : float
        Fraction of data held out for bias-model training.  Default 0.4
        (need enough samples per cutoff for stable residual estimation).
    seed : int

    Example
    -------
    >>> from sklearn.linear_model import Ridge
    >>> reg = FunctionalPartialRegressor(
    ...     n_comp=5, n_features=2, method="pace", argvals=t,
    ... )
    >>> bc = BiasCorrectedRegressor(
    ...     reg,
    ...     cutoff_grid=[15, 25, 35, 45],
    ...     bias_regressor=Ridge(alpha=0.5),
    ... )
    >>> bc.fit(X_train, Y_train)
    >>>
    >>> # At deployment: X_partial has 25 grid points per feature
    >>> y_corrected = bc.predict(X_partial)
    """

    def __init__(
        self,
        regressor: FunctionalPartialRegressor,
        cutoff_grid: Optional[Sequence[int]] = None,
        bias_regressor=None,
        cal_fraction: float = 0.4,
        seed: int = 42,
    ):
        if not isinstance(regressor, FunctionalPartialRegressor):
            raise TypeError(
                "BiasCorrectedRegressor requires a FunctionalPartialRegressor."
            )
        self.regressor = regressor
        self.cutoff_grid = cutoff_grid
        self.bias_regressor = bias_regressor
        self.cal_fraction = cal_fraction
        self.seed = seed

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        # ---- split: base-train / bias-train ----------------------------
        rng = np.random.default_rng(self.seed)
        n = X.shape[0]
        n_cal = max(int(n * self.cal_fraction), 10)
        perm = rng.permutation(n)
        cal_idx, fit_idx = perm[:n_cal], perm[n_cal:]

        # Fit the base regressor on the train fold
        self.regressor_ = clone(self.regressor)
        self.regressor_.fit(X[fit_idx], y[fit_idx])

        p = self.regressor_.n_features
        m = self.regressor_.n_points_
        argvals = self.regressor_.argvals_

        # ---- pick cutoff_grid if not provided --------------------------
        if self.cutoff_grid is None:
            # 5 cutoffs evenly spaced in [20%, 100%]
            cutoff_grid = np.linspace(0.2, 1.0, 5)
            cutoff_grid = np.unique(np.maximum(2, (cutoff_grid * m).astype(int)))
        else:
            cutoff_grid = np.asarray(self.cutoff_grid, dtype=int)
            if cutoff_grid.min() < 2 or cutoff_grid.max() > m:
                raise ValueError(
                    f"cutoff_grid values must be in [2, {m}], got "
                    f"[{cutoff_grid.min()}, {cutoff_grid.max()}]"
                )
        self.cutoff_grid_ = cutoff_grid

        # ---- build bias training set ----------------------------------
        X_cal, y_cal = X[cal_idx], y[cal_idx]
        n_cal_actual = len(cal_idx)

        features_blocks, targets_blocks = [], []
        for cutoff_idx in cutoff_grid:
            cutoff_t = float(argvals[cutoff_idx - 1])
            X_cal_partial = _build_partial_X(X_cal, p, m, cutoff_idx)

            # Base prediction at this cutoff
            self.regressor_.argvals_predict = argvals[:cutoff_idx]
            y_hat = self.regressor_.predict(X_cal_partial)
            self.regressor_.argvals_predict = None  # reset

            resid = y_cal - y_hat  # (n_cal, m_y)

            # Features: scores at this cutoff + cutoff time
            scores = _extract_scores_at_cutoff(
                self.regressor_, X_cal_partial, argvals[:cutoff_idx],
            )
            cutoff_col = np.full((n_cal_actual, 1), cutoff_t)
            features_blocks.append(np.hstack([scores, cutoff_col]))
            targets_blocks.append(resid)

        features = np.vstack(features_blocks)  # (n_cal * n_cutoffs, K+1)
        targets = np.vstack(targets_blocks)    # (n_cal * n_cutoffs, m_y)

        # ---- fit bias regressor --------------------------------------
        if self.bias_regressor is None:
            bias_reg = Ridge(alpha=1.0)
        else:
            bias_reg = clone(self.bias_regressor)

        # Wrap in MultiOutputRegressor if base doesn't handle multi-y
        try:
            bias_reg.fit(features[:5], targets[:5])  # probe
            bias_reg = clone(bias_reg)
            bias_reg.fit(features, targets)
        except ValueError:
            from sklearn.multioutput import MultiOutputRegressor
            base = (clone(self.bias_regressor) if self.bias_regressor is not None
                    else Ridge(alpha=1.0))
            bias_reg = MultiOutputRegressor(base, n_jobs=-1)
            bias_reg.fit(features, targets)

        self.bias_regressor_ = bias_reg
        self.n_features_ = p
        self.n_points_ = m
        self.argvals_ = argvals
        self.m_y_ = y.shape[1]
        return self

    def predict(self, X, return_components: bool = False):
        """Predict bias-corrected Y(t) from (full or partial) X.

        The cutoff is inferred from X.shape — it's the number of grid
        points observed per feature.

        Parameters
        ----------
        X : array-like (n, n_features * m_c)
        return_components : bool
            If True, also returns the base prediction and the bias term
            separately for diagnostics.

        Returns
        -------
        y_corrected : (n, m_y)
        (or (y_corrected, y_base, bias) if return_components=True)
        """
        X = np.asarray(X, dtype=np.float64)
        p = self.n_features_
        m = self.n_points_
        m_c = X.shape[1] // p
        if X.shape[1] % p != 0:
            raise ValueError("X columns not divisible by n_features")
        if m_c > m:
            raise ValueError(
                f"X has more columns ({m_c}) per feature than training "
                f"grid ({m})"
            )

        cutoff_t = float(self.argvals_[m_c - 1])

        # Base prediction (FunctionalPartialRegressor handles partial X)
        if m_c < m:
            self.regressor_.argvals_predict = self.argvals_[:m_c]
        else:
            self.regressor_.argvals_predict = None
        y_base = self.regressor_.predict(X)

        # Bias prediction
        scores = _extract_scores_at_cutoff(
            self.regressor_, X, self.argvals_[:m_c],
        )
        feat = np.hstack([scores, np.full((len(X), 1), cutoff_t)])
        bias = self.bias_regressor_.predict(feat)

        y_corrected = y_base + bias

        if return_components:
            return y_corrected, y_base, bias
        return y_corrected


def _extract_scores_at_cutoff(
    reg: FunctionalPartialRegressor,
    X_partial: NDArray,
    argvals_partial: NDArray,
) -> NDArray:
    """Extract scores using the base reg's basis on the partial grid."""
    p = reg.n_features
    m = reg.n_points_
    m_c = len(argvals_partial)
    Xs = [X_partial[:, j * m_c : (j + 1) * m_c] for j in range(p)]
    idx = np.searchsorted(reg.argvals_, argvals_partial)
    if reg.method == "pace" and reg.sigma2_ is not None:
        scores, _ = _scores_pace(Xs, idx, reg.mfpca_, reg.sigma2_)
    else:
        quad = _trapezoidal_weights(argvals_partial)
        scores = _scores_truncated(Xs, idx, quad, reg.mfpca_)
    return scores


# ===================================================================
# Demo: bias grows with t, then is corrected
# ===================================================================

if __name__ == "__main__":
    from sklearn.linear_model import Ridge

    np.random.seed(0)

    # ---- Simulate data with per-observation t-dependent bias ----------
    n, m = 400, 60
    t = np.linspace(0, 1, m)
    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
    X1 += 0.2 * np.random.randn(n, m)
    X2 += 0.2 * np.random.randn(n, m)

    # Per-curve QUADRATIC-in-phase bias that grows with t.
    # The linear MFPCA pipeline cannot represent quadratic functions
    # of the latent phase, so residuals grow with t.
    phi1_centered = (phases1 - phases1.mean()) / phases1.std()
    bias_per_curve = 1.2 * (phi1_centered ** 2)[:, None] * t[None, :]
    Y = (0.5 * X1 + 0.3 * X2
         + bias_per_curve         # per-curve bias growing with t
         + 0.05 * np.random.randn(n, m))   # smaller noise => bias visible
    X = np.hstack([X1, X2])

    X_train, X_test = X[:250], X[250:]
    Y_train, Y_test = Y[:250], Y[250:]

    print("=" * 75)
    print("Bias correction demo")
    print("=" * 75)
    print("\nData has a per-curve bias  1.2 * φ^2 * t  that depends quadratically")
    print("on each curve's latent phase φ.  The linear MFPCA regression cannot")
    print("represent this (it's nonlinear in scores), so residuals grow with t.\n")

    # ---- Baseline (no correction) ------------------------------------
    base = FunctionalPartialRegressor(
        n_comp=5, n_features=2, method="pace", argvals=t,
    )
    base.fit(X_train, Y_train)
    y_base = base.predict(X_test)
    resid_base = Y_test - y_base  # (n_test, m)

    # ---- Bias-corrected (polynomial-feature Ridge bias model) ---------
    # The true bias is quadratic in latent phase => the linear scores
    # alone don't explain it.  Use PolynomialFeatures(degree=2) to give
    # the bias model the quadratic interactions it needs.
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures

    base_bc = FunctionalPartialRegressor(
        n_comp=5, n_features=2, method="pace", argvals=t,
    )
    bc = BiasCorrectedRegressor(
        base_bc,
        cutoff_grid=[15, 25, 35, 45, 55],
        bias_regressor=make_pipeline(
            PolynomialFeatures(degree=2, include_bias=False),
            Ridge(alpha=1.0),
        ),
        cal_fraction=0.4,
    )
    bc.fit(X_train, Y_train)

    # ---- Evaluate at multiple horizons -------------------------------
    print(f"   {'Horizon':>10s}  {'Baseline':>22s}  {'Corrected':>22s}")
    print( "   " + " " * 12 + f"{'rmse / |mean bias|':>22s}  "
          f"{'rmse / |mean bias|':>22s}")
    print("   " + "─" * 60)
    for frac in [1.0, 0.75, 0.5, 0.3]:
        c = int(frac * m)
        X_te = X_test if c == m else _build_partial_X(X_test, 2, m, c)
        base.argvals_predict = t[:c] if c < m else None
        y_base_p = base.predict(X_te)
        y_corr_p = bc.predict(X_te)

        # RMSE pointwise & bias magnitude
        res_base = Y_test - y_base_p
        res_corr = Y_test - y_corr_p
        rmse_base = np.sqrt(np.mean(res_base ** 2))
        rmse_corr = np.sqrt(np.mean(res_corr ** 2))
        mb_base = np.abs(res_base.mean(axis=0)).max()
        mb_corr = np.abs(res_corr.mean(axis=0)).max()
        print(f"   {int(frac*100):>9d}%  "
              f"  rmse={rmse_base:.3f}  bias={mb_base:.3f}  "
              f"  rmse={rmse_corr:.3f}  bias={mb_corr:.3f}")

    # ---- Decompose for several test samples --------------------------
    print("\n   Decomposition for first 3 test observations (full horizon):")
    y_corr, y_base_v, bias_v = bc.predict(X_test[:3], return_components=True)
    # True bias for these observations
    phi1_test = (phases1[250:253] - phases1.mean()) / phases1.std()
    true_bias = 1.2 * (phi1_test ** 2)[:, None] * t[None, :]
    for i in range(3):
        true_b_max = true_bias[i].max()
        bias_pred_max = bias_v[i].max()
        print(f"     obs {i}: true_bias_max={true_b_max:+.3f}  "
              f"predicted_bias_max={bias_pred_max:+.3f}")

    # ---- Try a non-linear bias model ---------------------------------
    print(f"\n{'=' * 75}")
    print("Same problem with HistGradientBoostingRegressor as bias model")
    print("=" * 75)
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
        base_gbr = FunctionalPartialRegressor(
            n_comp=5, n_features=2, method="pace", argvals=t,
        )
        bc_gbr = BiasCorrectedRegressor(
            base_gbr,
            cutoff_grid=[15, 25, 35, 45, 55],
            bias_regressor=HistGradientBoostingRegressor(
                max_depth=4, max_iter=200, random_state=0,
            ),
            cal_fraction=0.4,
        )
        bc_gbr.fit(X_train, Y_train)
        print(f"   {'Horizon':>10s}  {'GBR-corrected':>22s}")
        print("   " + "─" * 35)
        for frac in [1.0, 0.75, 0.5, 0.3]:
            c = int(frac * m)
            X_te = X_test if c == m else _build_partial_X(X_test, 2, m, c)
            y_corr_p = bc_gbr.predict(X_te)
            res = Y_test - y_corr_p
            rmse = np.sqrt(np.mean(res ** 2))
            mb = np.abs(res.mean(axis=0)).max()
            print(f"   {int(frac*100):>9d}%  "
                  f"  rmse={rmse:.3f}  bias={mb:.3f}")
    except ImportError:
        print("   (HistGradientBoostingRegressor not available)")
