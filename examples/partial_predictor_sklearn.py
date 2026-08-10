"""Sklearn-compatible partial-domain functional regressor.

Wraps the MFPCA + truncated/PACE pipeline into a scikit-learn estimator
so you can use cross_validate, GridSearchCV, Pipeline, etc.

Convention:
  X is a 2-D array of shape (n_samples, p * m) — p functional features
  concatenated along columns. Each feature occupies m consecutive columns
  (the same regular grid for all features).

  y is a 2-D array of shape (n_samples, m_y) — the functional response
  evaluated on a (possibly different) regular grid.

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigh
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted


# ===================================================================
# Low-level helpers (self-contained, no external FDA library needed)
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


def _mfpca(
    X_list: List[NDArray],
    argvals: NDArray,
    n_comp: int,
) -> dict:
    p = len(X_list)
    n, m = X_list[0].shape
    quad_w = _trapezoidal_weights(argvals)

    means, centered, weights = [], [], np.empty(p)
    for j in range(p):
        mu = X_list[j].mean(axis=0)
        means.append(mu)
        Xc = X_list[j] - mu
        avg_norm = np.sqrt(np.mean(np.sum(Xc ** 2 * quad_w, axis=1)))
        weights[j] = 1.0 / max(avg_norm, 1e-12)
        centered.append(Xc * weights[j])

    Z = np.hstack(centered)
    W = np.tile(quad_w, p)
    G = (Z * W) @ Z.T / (n - 1)

    n_comp = min(n_comp, n - 1, p * m)
    eigvals, eigvecs = eigh(G, subset_by_index=[n - n_comp, n - 1])
    eigvals, eigvecs = eigvals[::-1], eigvecs[:, ::-1]
    pos = eigvals > 1e-12
    eigvals, eigvecs = eigvals[pos], eigvecs[:, pos]
    K = len(eigvals)

    phi = np.zeros((K, p * m))
    for k in range(K):
        phi[k] = Z.T @ eigvecs[:, k] / np.sqrt(eigvals[k] * (n - 1))

    scores = (Z * W) @ phi.T

    return dict(
        eigenvalues=eigvals, eigenfunctions=phi, scores=scores,
        mean=np.hstack(means), weights=weights,
        n_features=p, n_points=m,
    )


def _estimate_noise(X_list, argvals, mfpca):
    p, m, K = mfpca["n_features"], mfpca["n_points"], len(mfpca["eigenvalues"])
    quad_w = _trapezoidal_weights(argvals)
    domain_len = argvals[-1] - argvals[0]
    sigma2 = np.zeros(p)
    for j in range(p):
        w_j = mfpca["weights"][j]
        mu_j = mfpca["mean"][j * m : (j + 1) * m]
        Xc = (X_list[j] - mu_j) * w_j
        total_var = np.sum(np.var(Xc, axis=0, ddof=1) * quad_w) / domain_len
        explained = sum(
            mfpca["eigenvalues"][k]
            * np.sum(mfpca["eigenfunctions"][k, j * m : (j + 1) * m] ** 2 * quad_w)
            / domain_len
            for k in range(K)
        )
        sigma2[j] = max(total_var - explained, 1e-10)
    return sigma2


def _scores_truncated(X_list, idx, quad_c, mfpca):
    p, m = mfpca["n_features"], mfpca["n_points"]
    K = len(mfpca["eigenvalues"])
    n_new = X_list[0].shape[0]
    scores = np.zeros((n_new, K))
    for k in range(K):
        num, den = np.zeros(n_new), 0.0
        for j in range(p):
            phi_c = mfpca["eigenfunctions"][k, j * m : (j + 1) * m][idx]
            mu_c = mfpca["mean"][j * m : (j + 1) * m][idx]
            Xc = (X_list[j] - mu_c) * mfpca["weights"][j]
            num += Xc @ (phi_c * quad_c)
            den += np.sum(phi_c ** 2 * quad_c)
        scores[:, k] = num / max(den, 1e-12)
    return scores


def _scores_pace(X_list, idx, mfpca, sigma2):
    """PACE score estimation via Woodbury identity.

    Instead of building and factorizing the full (p*m_c x p*m_c)
    covariance matrix, exploits the low-rank + diagonal structure:

        Sigma_obs = Phi @ Lambda @ Phi^T + D

    Using the Woodbury identity the BLUP reduces to a (K x K) solve:

        xi = M^{-1} @ Phi^T @ D^{-1} @ X_obs
        M  = Lambda^{-1} + Phi^T @ D^{-1} @ Phi     (K x K)

    Conditional variance: diag(M^{-1}).

    Complexity: O(K^2 * p*m_c + K^3) instead of O((p*m_c)^3).
    """
    p, m = mfpca["n_features"], mfpca["n_points"]
    K = len(mfpca["eigenvalues"])
    n_new = X_list[0].shape[0]
    m_c = len(idx)
    m_obs = p * m_c

    # --- Build stacked observations and eigenfunctions ------------------
    X_obs = np.zeros((n_new, m_obs))
    Phi_obs = np.zeros((K, m_obs))
    for j in range(p):
        mu_c = mfpca["mean"][j * m : (j + 1) * m][idx]
        X_obs[:, j * m_c : (j + 1) * m_c] = (X_list[j] - mu_c) * mfpca["weights"][j]
        for k in range(K):
            Phi_obs[k, j * m_c : (j + 1) * m_c] = (
                mfpca["eigenfunctions"][k, j * m : (j + 1) * m][idx]
            )

    # --- D^{-1}: inverse of diagonal noise matrix ----------------------
    # D = block_diag(sigma2[0]*I, sigma2[1]*I, ..., sigma2[p-1]*I)
    d_inv = np.empty(m_obs)
    for j in range(p):
        d_inv[j * m_c : (j + 1) * m_c] = 1.0 / sigma2[j]

    # --- Woodbury: M = Lambda^{-1} + Phi^T D^{-1} Phi  (K x K) -------
    # Phi_scaled = Phi * sqrt(d_inv)  so  Phi^T D^{-1} Phi = Phi_scaled @ Phi_scaled^T
    Phi_d = Phi_obs * d_inv  # (K, m_obs) — each row scaled by d_inv

    M = np.diag(1.0 / mfpca["eigenvalues"]) + Phi_d @ Phi_obs.T  # (K, K)

    # --- Solve: scores = M^{-1} @ Phi^T @ D^{-1} @ X_obs^T ------------
    # Phi^T D^{-1} X_obs^T = Phi_d @ X_obs^T  (K, n_new)
    rhs = Phi_d @ X_obs.T  # (K, n_new)
    scores = np.linalg.solve(M, rhs).T  # (n_new, K)

    # --- Conditional variance: diag(M^{-1}) ----------------------------
    M_inv = np.linalg.inv(M)  # K x K — tiny
    score_var = np.maximum(np.diag(M_inv), 0.0)

    return scores, np.tile(score_var, (n_new, 1))


def _fit_regression(scores, Y, sample_weight=None):
    """Pointwise OLS from MFPCA scores to Y(t), optionally weighted.

    If sample_weight is provided, solves weighted least squares:
        beta = (S^T W S)^{-1} S^T W Y_c
    where W = diag(sample_weight).
    """
    K = scores.shape[1]
    if sample_weight is None:
        mu_y = Y.mean(axis=0)
        Yc = Y - mu_y
        gram_inv = np.linalg.inv(scores.T @ scores + 1e-10 * np.eye(K))
        beta = gram_inv @ (scores.T @ Yc)
    else:
        w = np.asarray(sample_weight, dtype=np.float64)
        w_sum = w.sum()
        mu_y = (Y * w[:, None]).sum(axis=0) / w_sum
        Yc = Y - mu_y
        SwS = (scores.T * w) @ scores  # (K, K)
        SwY = (scores.T * w) @ Yc       # (K, m_y)
        beta = np.linalg.solve(SwS + 1e-10 * np.eye(K), SwY)
    residuals = Y - (scores @ beta + mu_y)
    return dict(beta=beta, intercept=mu_y, residuals=residuals)


# ===================================================================
# Sklearn estimator
# ===================================================================

class FunctionalPartialRegressor(BaseEstimator, RegressorMixin):
    """Partial-domain functional-on-functional regressor.

    Fits MFPCA on p stacked functional predictors, then a configurable
    regression model from scores to Y(t).  At prediction time, accepts
    partially observed X (fewer columns) and estimates scores via
    truncated projection or PACE.

    Compatible with scikit-learn's ``cross_validate``, ``GridSearchCV``,
    ``Pipeline``, etc.

    Parameters
    ----------
    n_comp : int, default=5
        Number of MFPCA components.
    n_features : int, default=1
        Number of functional predictors p.  X must have shape
        ``(n_samples, p * m)`` where ``m`` is the grid size.
    method : str, default="pace"
        Score estimation for partial data: ``"truncated"`` or ``"pace"``.
    base_regressor : sklearn estimator or None, default=None
        Regressor mapping scores to Y(t).  If None, uses pointwise OLS.
        Any sklearn regressor that supports multi-output (or will be
        wrapped in ``MultiOutputRegressor``).  Examples::

            from sklearn.ensemble import HistGradientBoostingRegressor
            base_regressor=HistGradientBoostingRegressor()

            from sklearn.ensemble import RandomForestRegressor
            base_regressor=RandomForestRegressor(n_estimators=100)
    alpha : float, default=0.1
        Miscoverage level for conformal prediction intervals.
    cal_fraction : float, default=0.25
        Fraction of training data for conformal calibration.
    simultaneous : bool, default=True
        If True, conformal band valid for all t simultaneously.
    argvals : array-like or None, default=None
        Evaluation grid of length m.  If None, uses ``np.linspace(0, 1, m)``.
    argvals_predict : array-like or None, default=None
        Partial grid [a, c] for prediction.  If None, uses full grid.

    Examples
    --------
    Linear (default):

    >>> reg = FunctionalPartialRegressor(n_comp=5, n_features=2)
    >>> reg.fit(X, Y)

    Non-linear with gradient boosting:

    >>> from sklearn.ensemble import HistGradientBoostingRegressor
    >>> reg = FunctionalPartialRegressor(
    ...     n_comp=5, n_features=2,
    ...     base_regressor=HistGradientBoostingRegressor(max_depth=3),
    ... )

    Non-linear with random forest:

    >>> from sklearn.ensemble import RandomForestRegressor
    >>> reg = FunctionalPartialRegressor(
    ...     n_comp=5, n_features=2,
    ...     base_regressor=RandomForestRegressor(n_estimators=200),
    ... )
    """

    def __init__(
        self,
        n_comp: int = 5,
        n_features: int = 1,
        method: str = "pace",
        base_regressor=None,
        alpha: float = 0.1,
        cal_fraction: float = 0.25,
        simultaneous: bool = True,
        argvals=None,
        argvals_predict=None,
    ):
        self.n_comp = n_comp
        self.n_features = n_features
        self.method = method
        self.base_regressor = base_regressor
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.simultaneous = simultaneous
        self.argvals = argvals
        self.argvals_predict = argvals_predict

    def _split_X(self, X: NDArray, m: int) -> List[NDArray]:
        """Split stacked X (n, p*m) into list of p arrays (n, m)."""
        return [X[:, j * m : (j + 1) * m] for j in range(self.n_features)]

    def fit(self, X, y, sample_weight=None):
        """Fit MFPCA + regression on full-domain training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features * m)
            Stacked functional predictors on the full grid.
        y : array-like of shape (n_samples, m_y)
            Functional response on the full grid.
        sample_weight : array-like of shape (n_samples,), optional
            Per-sample weights for the score→Y regression step.  Use
            this to downweight outliers detected via Y-FPCA scores
            (see examples/outlier_detection.py).

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        if sample_weight is not None:
            sample_weight = np.asarray(sample_weight, dtype=np.float64)

        p = self.n_features
        total_cols = X.shape[1]
        if total_cols % p != 0:
            raise ValueError(
                f"X has {total_cols} columns, not divisible by "
                f"n_features={p}"
            )
        m = total_cols // p
        self.n_points_ = m

        # Resolve argvals
        if self.argvals is None:
            self.argvals_ = np.linspace(0, 1, m)
        else:
            self.argvals_ = np.asarray(self.argvals, dtype=np.float64)
            if len(self.argvals_) != m:
                raise ValueError(
                    f"argvals length {len(self.argvals_)} != grid size {m}"
                )

        # --- Train / calibration split for conformal intervals --------
        rng = np.random.default_rng(42)
        n = X.shape[0]
        n_cal = max(int(n * self.cal_fraction), 2)
        perm = rng.permutation(n)
        cal_idx, train_idx = perm[:n_cal], perm[n_cal:]

        X_train, X_cal = X[train_idx], X[cal_idx]
        y_train, y_cal = y[train_idx], y[cal_idx]
        if sample_weight is not None:
            w_train = sample_weight[train_idx]
        else:
            w_train = None

        # Split and fit MFPCA on training portion
        X_list = self._split_X(X_train, m)
        self.mfpca_ = _mfpca(X_list, self.argvals_, self.n_comp)

        # Regression: scores -> Y(t)
        if self.base_regressor is None:
            # Default: pointwise OLS (fast, linear, supports sample_weight)
            self.regression_ = _fit_regression(
                self.mfpca_["scores"], y_train, sample_weight=w_train,
            )
            self.regressor_ = None
        else:
            # Pluggable sklearn regressor (non-linear)
            from sklearn.base import clone
            from sklearn.multioutput import MultiOutputRegressor

            from sklearn.multioutput import MultiOutputRegressor
            reg = clone(self.base_regressor)
            # Check if regressor supports multi-output natively
            try:
                reg.fit(self.mfpca_["scores"][:2], y_train[:2])  # quick probe
                reg = clone(self.base_regressor)  # reset
                reg.fit(self.mfpca_["scores"], y_train)
            except ValueError:
                reg = MultiOutputRegressor(clone(self.base_regressor), n_jobs=-1)
                reg.fit(self.mfpca_["scores"], y_train)
            self.regressor_ = reg
            # Store residuals for conformal calibration
            y_train_hat = reg.predict(self.mfpca_["scores"])
            self.regression_ = dict(
                beta=None,
                intercept=y_train.mean(axis=0),
                residuals=y_train - y_train_hat,
            )

        # Noise variance (for PACE)
        if self.method == "pace":
            self.sigma2_ = _estimate_noise(X_list, self.argvals_, self.mfpca_)
        else:
            self.sigma2_ = None

        # --- Conformal calibration on held-out set --------------------
        y_cal_hat = self._predict_raw(X_cal, self.argvals_)
        cal_residuals = np.abs(y_cal - y_cal_hat)

        # Local scale: MAD per grid point
        self.sigma_t_ = np.median(cal_residuals, axis=0) * 1.4826
        self.sigma_t_ = np.maximum(self.sigma_t_, 1e-12)

        # Normalized scores
        norm_res = cal_residuals / self.sigma_t_

        q_level = min(np.ceil((1 - self.alpha) * (n_cal + 1)) / n_cal, 1.0)
        # Simultaneous: supremum over t
        self.conformal_q_sim_ = float(
            np.quantile(norm_res.max(axis=1), q_level)
        )
        # Pointwise
        self.conformal_q_pw_ = np.quantile(norm_res, q_level, axis=0)

        self.n_outputs_ = y.shape[1]
        return self

    def _resolve_partial_grid(self, X):
        """Determine argvals_partial from X shape and settings."""
        p = self.n_features
        m = self.n_points_
        m_c = X.shape[1] // p
        if X.shape[1] % p != 0:
            raise ValueError(
                f"X has {X.shape[1]} columns, not divisible by n_features={p}"
            )
        if m_c == m:
            return self.argvals_
        if self.argvals_predict is not None:
            ap = np.asarray(self.argvals_predict, dtype=np.float64)
            if len(ap) != m_c:
                raise ValueError(
                    f"argvals_predict length {len(ap)} != partial grid {m_c}"
                )
            return ap
        return self.argvals_[:m_c]

    def _estimate_scores(self, X, argvals_partial):
        """Extract scores from (possibly partial) X."""
        m_c = len(argvals_partial)
        X_list = self._split_X(X, m_c)
        idx = np.searchsorted(self.argvals_, argvals_partial)
        score_var = None
        if self.method == "pace" and self.sigma2_ is not None:
            scores, score_var = _scores_pace(
                X_list, idx, self.mfpca_, self.sigma2_
            )
        else:
            quad_c = _trapezoidal_weights(argvals_partial)
            scores = _scores_truncated(X_list, idx, quad_c, self.mfpca_)
        return scores, score_var

    def _predict_from_scores(self, scores):
        """Map scores to Y(t) using the fitted regressor."""
        if self.regressor_ is not None:
            return self.regressor_.predict(scores)
        return scores @ self.regression_["beta"] + self.regression_["intercept"]

    def _predict_raw(self, X, argvals_partial):
        """Core prediction returning only y_hat."""
        scores, _ = self._estimate_scores(X, argvals_partial)
        return self._predict_from_scores(scores)

    def _predict_with_scores(self, X, argvals_partial):
        """Prediction returning (y_hat, scores, score_variances)."""
        scores, score_var = self._estimate_scores(X, argvals_partial)
        y_hat = self._predict_from_scores(scores)
        return y_hat, scores, score_var

    def predict(self, X):
        """Predict Y(t) from (possibly partial) X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features * m_c)
            Functional predictors, either full (m_c = m) or partial
            (m_c < m, matching argvals_predict).

        Returns
        -------
        y_pred : ndarray of shape (n_samples, m_y)
        """
        check_is_fitted(self)
        X = np.asarray(X, dtype=np.float64)
        argvals_partial = self._resolve_partial_grid(X)
        return self._predict_raw(X, argvals_partial)

    def predict_interval(self, X, alpha=None, simultaneous=None):
        """Predict Y(t) with conformal prediction intervals.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features * m_c)
            Functional predictors (full or partial).
        alpha : float or None
            Miscoverage level. If None, uses self.alpha from fit.
            Note: if different from fit-time alpha, the conformal quantile
            is reused (calibrated at fit-time alpha).
        simultaneous : bool or None
            If True, simultaneous band (all t). If False, pointwise.
            If None, uses self.simultaneous.

        Returns
        -------
        y_pred : ndarray (n_samples, m_y)
            Point prediction.
        lower : ndarray (n_samples, m_y)
            Lower prediction band.
        upper : ndarray (n_samples, m_y)
            Upper prediction band.
        """
        check_is_fitted(self)
        X = np.asarray(X, dtype=np.float64)
        argvals_partial = self._resolve_partial_grid(X)
        y_hat, scores, score_var = self._predict_with_scores(X, argvals_partial)

        if simultaneous is None:
            simultaneous = self.simultaneous

        # Conformal band
        if simultaneous:
            half_w = self.conformal_q_sim_ * self.sigma_t_
        else:
            half_w = self.conformal_q_pw_ * self.sigma_t_

        return y_hat, y_hat - half_w, y_hat + half_w

    def predict_interval_parametric(self, X, alpha=None):
        """Predict Y(t) with parametric (Gaussian) prediction intervals.

        Only available with method="pace" and base_regressor=None (linear).
        Gives tighter pointwise bands than conformal but requires Gaussian
        assumptions and linearity.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features * m_c)
        alpha : float or None
            Miscoverage level. Default: self.alpha.

        Returns
        -------
        y_pred : ndarray (n_samples, m_y)
        lower : ndarray (n_samples, m_y)
        upper : ndarray (n_samples, m_y)
        """
        from scipy.stats import norm as sp_norm

        check_is_fitted(self)
        if self.method != "pace":
            raise ValueError("Parametric intervals require method='pace'")
        if self.regressor_ is not None:
            raise ValueError(
                "Parametric intervals only available with linear regression "
                "(base_regressor=None). Use predict_interval() for conformal "
                "intervals with non-linear models."
            )

        X = np.asarray(X, dtype=np.float64)
        argvals_partial = self._resolve_partial_grid(X)
        y_hat, scores, score_var = self._predict_with_scores(X, argvals_partial)

        if alpha is None:
            alpha = self.alpha

        sigma2_y = np.var(self.regression_["residuals"], axis=0, ddof=1)
        pred_var = score_var @ (self.regression_["beta"] ** 2) + sigma2_y
        z = sp_norm.ppf(1 - alpha / 2)
        half_w = z * np.sqrt(pred_var)

        return y_hat, y_hat - half_w, y_hat + half_w

    def score(self, X, y, sample_weight=None):
        """Mean R^2 across grid points (functional R^2).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features * m_c)
        y : array-like of shape (n_samples, m_y)
        sample_weight : ignored

        Returns
        -------
        score : float
            Mean over grid points of pointwise R^2.
        """
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2, axis=0)
        ss_tot = np.sum((y - y.mean(axis=0)) ** 2, axis=0)
        r2 = 1 - ss_res / np.maximum(ss_tot, 1e-12)
        return float(r2.mean())

    # ----- Feature attribution (linear regression path only) ---------

    def _check_linear(self):
        if self.regressor_ is not None:
            raise ValueError(
                "Analytical attribution requires the default linear "
                "regression (base_regressor=None).  For non-linear "
                "models, use permutation_importance() or SHAP on scores."
            )

    def coefficient_surfaces(self):
        """Coefficient surface B^(j)(t, s) per feature j.

        Y_hat(s) - mu_Y(s) = sum_j integral (X^(j)(t) - mu^(j)(t))
                                          * B^(j)(t, s) dt

        where  B^(j)(t, s) = sum_k w_j * beta_k(s) * phi_k^(j)(t).

        Returns
        -------
        B : ndarray (p, m, m_y)
            B[j, :, :] is the coefficient surface for feature j.
        """
        check_is_fitted(self)
        self._check_linear()

        K = self.mfpca_["eigenfunctions"].shape[0]
        p = self.n_features
        m = self.n_points_
        m_y = self.regression_["beta"].shape[1]

        B = np.empty((p, m, m_y))
        beta = self.regression_["beta"]  # (K, m_y)
        for j in range(p):
            # Phi_j: (K, m) — eigenfunctions for feature j
            Phi_j = self.mfpca_["eigenfunctions"][:, j * m : (j + 1) * m]
            w_j = self.mfpca_["weights"][j]
            B[j] = w_j * Phi_j.T @ beta  # (m, m_y)
        return B

    def feature_contributions(self, X):
        """Per-observation contribution decomposition:

            Y_hat_i(s) = mu_Y(s) + sum_j C_i^(j)(s)

        Each C_i^(j)(s) is a curve showing how much feature j contributes
        to the prediction at each output grid point s.

        Parameters
        ----------
        X : array-like (n, n_features * m_c)
            Full or partial observations.

        Returns
        -------
        contributions : ndarray (n, p, m_y)
            contributions[i, j, :] = C_i^(j)(s).
        y_pred : ndarray (n, m_y)
            The full prediction (for convenience / sanity check).
        mean_y : ndarray (m_y,)
            The intercept.
        """
        check_is_fitted(self)
        self._check_linear()

        X = np.asarray(X, dtype=np.float64)
        argvals_partial = self._resolve_partial_grid(X)
        m_c = len(argvals_partial)
        X_list = self._split_X(X, m_c)
        idx = np.searchsorted(self.argvals_, argvals_partial)
        quad_c = _trapezoidal_weights(argvals_partial)

        n = X.shape[0]
        p = self.n_features
        m = self.n_points_
        m_y = self.regression_["beta"].shape[1]

        # B_j restricted to observed domain per feature
        beta = self.regression_["beta"]
        contributions = np.zeros((n, p, m_y))
        for j in range(p):
            Phi_j = self.mfpca_["eigenfunctions"][:, j * m : (j + 1) * m]
            Phi_j_c = Phi_j[:, idx]  # (K, m_c) restricted
            mu_j_c = self.mfpca_["mean"][j * m : (j + 1) * m][idx]
            w_j = self.mfpca_["weights"][j]
            B_j_c = w_j * Phi_j_c.T @ beta  # (m_c, m_y)

            Xc = X_list[j] - mu_j_c  # (n, m_c)
            # Integrate: (n, m_c) @ (m_c, m_y) with quadrature
            contributions[:, j, :] = (Xc * quad_c) @ B_j_c

        y_pred = self.regression_["intercept"] + contributions.sum(axis=1)
        return contributions, y_pred, self.regression_["intercept"]

    def global_importance(self, X=None, kind: str = "contribution",
                           norm: str = "l2"):
        """Per-feature global importance.

        Two families of importance measures:

        ``kind="contribution"`` (RECOMMENDED):
            Uses the variance of actual per-sample contributions
            C_i^(j)(s), which is the correct measure of how much each
            feature actually influences predictions on real data.
            Unaffected by per-feature scaling artifacts.

        ``kind="coefficient"``:
            Uses the magnitude of the coefficient surface B^(j)(t,s).
            WARNING: this is biased by MFPCA's per-feature L2
            normalization — features with small amplitude get inflated
            coefficient surfaces.  Only use if you trust that features
            are on comparable scales without normalization.

        Parameters
        ----------
        X : array-like (n, n_features * m), required for "contribution"
        kind : str
            "contribution" or "coefficient".
        norm : str
            "l2", "l1", or "max".

        Returns
        -------
        ndarray (p,)
            Importance per feature (larger = more influential).
        """
        if kind == "contribution":
            if X is None:
                raise ValueError("X required for kind='contribution'")
            C, _, _ = self.feature_contributions(X)
            # C shape: (n, p, m_y)
            # Quadrature over output grid (uniform proxy if unknown)
            m_y = C.shape[2]
            qy = np.full(m_y, 1.0 / m_y)

            p = C.shape[1]
            imp = np.empty(p)
            for j in range(p):
                Cj = C[:, j, :]  # (n, m_y)
                if norm == "l2":
                    # RMS of ||C_j||_L2 across observations
                    per_obs = np.sqrt((Cj ** 2 * qy).sum(axis=1))
                    val = np.sqrt((per_obs ** 2).mean())
                elif norm == "l1":
                    per_obs = (np.abs(Cj) * qy).sum(axis=1)
                    val = per_obs.mean()
                elif norm == "max":
                    val = np.abs(Cj).max()
                else:
                    raise ValueError(f"Unknown norm: {norm}")
                imp[j] = val
            return imp

        elif kind == "coefficient":
            B = self.coefficient_surfaces()
            qx = _trapezoidal_weights(self.argvals_)
            m_y = B.shape[2]
            qy = np.full(m_y, 1.0 / m_y)
            p = B.shape[0]
            imp = np.empty(p)
            for j in range(p):
                if norm == "l2":
                    val = np.sqrt(((B[j] ** 2) * qx[:, None] * qy[None, :]).sum())
                elif norm == "l1":
                    val = (np.abs(B[j]) * qx[:, None] * qy[None, :]).sum()
                elif norm == "max":
                    val = np.abs(B[j]).max()
                else:
                    raise ValueError(f"Unknown norm: {norm}")
                imp[j] = val
            return imp
        else:
            raise ValueError(f"kind must be 'contribution' or 'coefficient'")

    # ----- Fallback for non-linear regressors ------------------------

    def permutation_importance(self, X, y, n_repeats: int = 10,
                               random_state: int = 0):
        """Permutation importance on the MFPCA score features.

        For each feature j, permutes the corresponding feature block of
        X and measures MSE degradation.  Works with any regressor
        (linear or non-linear).

        Parameters
        ----------
        X : array-like (n, n_features * m)
        y : array-like (n, m_y)
        n_repeats : int
        random_state : int

        Returns
        -------
        mean : ndarray (p,) — mean importance per feature
        std  : ndarray (p,) — std across repeats
        """
        check_is_fitted(self)
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        m = self.n_points_
        p = self.n_features
        rng = np.random.default_rng(random_state)

        baseline = np.mean((y - self.predict(X)) ** 2)
        importances = np.zeros((p, n_repeats))
        for j in range(p):
            for r in range(n_repeats):
                X_perm = X.copy()
                perm = rng.permutation(X.shape[0])
                X_perm[:, j * m : (j + 1) * m] = X[perm, j * m : (j + 1) * m]
                permuted_mse = np.mean((y - self.predict(X_perm)) ** 2)
                importances[j, r] = permuted_mse - baseline
        return importances.mean(axis=1), importances.std(axis=1)


# ===================================================================
# Custom scorers for interval evaluation in cross_validate
# ===================================================================

def _coverage_scorer(estimator, X, y):
    """Simultaneous coverage: fraction of curves fully inside the band."""
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    _, lower, upper = estimator.predict_interval(X)
    covered = np.all((y >= lower) & (y <= upper), axis=1)
    return float(covered.mean())


def _pointwise_coverage_scorer(estimator, X, y):
    """Mean pointwise coverage across grid points."""
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    _, lower, upper = estimator.predict_interval(X, simultaneous=False)
    return float(np.mean((y >= lower) & (y <= upper)))


def _band_width_scorer(estimator, X, y):
    """Negative mean band width (higher = tighter = better for sklearn)."""
    _, lower, upper = estimator.predict_interval(X)
    return -float(np.mean(upper - lower))


def _interval_score_scorer(estimator, X, y):
    """Negative interval score (Gneiting & Raftery, 2007).

    Proper scoring rule for prediction intervals.  Lower = better,
    so we negate for sklearn convention (higher = better).

    IS = (upper - lower)
         + (2/alpha) * (lower - y) * 1[y < lower]
         + (2/alpha) * (y - upper) * 1[y > upper]
    """
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    _, lower, upper = estimator.predict_interval(X)
    alpha = estimator.alpha
    width = upper - lower
    penalty_low = (2 / alpha) * np.maximum(lower - y, 0)
    penalty_high = (2 / alpha) * np.maximum(y - upper, 0)
    is_score = np.mean(width + penalty_low + penalty_high)
    return -is_score


def make_interval_scorers():
    """Return a dict of scorers for use with cross_validate.

    Usage::

        scorers = make_interval_scorers()
        cv = cross_validate(reg, X, y, cv=5, scoring=scorers)
        # cv["test_coverage"]       -- simultaneous coverage per fold
        # cv["test_band_width"]     -- negative mean band width per fold
        # cv["test_interval_score"] -- negative interval score per fold
    """
    return {
        "neg_mse": "neg_mean_squared_error",
        "coverage": _coverage_scorer,
        "pointwise_coverage": _pointwise_coverage_scorer,
        "band_width": _band_width_scorer,
        "interval_score": _interval_score_scorer,
    }


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    from sklearn.model_selection import cross_validate, GridSearchCV
    from sklearn.ensemble import (
        HistGradientBoostingRegressor,
        RandomForestRegressor,
    )

    np.random.seed(42)

    # --- Simulate data with NON-LINEAR effects ---------------------------
    n, m, p = 200, 30, 2
    t = np.linspace(0, 1, m)

    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) + 0.3 * np.random.randn(m)
                    for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) + 0.3 * np.random.randn(m)
                    for phi in phases2])

    # Non-linear response: interaction + quadratic terms
    Y = (0.5 * X1 + 0.3 * X2
         + 0.4 * X1 * X2          # interaction
         + 0.2 * X1 ** 2          # quadratic
         + 0.15 * np.random.randn(n, m))

    X = np.hstack([X1, X2])

    # -----------------------------------------------------------------
    # 1. Compare linear vs non-linear regressors
    # -----------------------------------------------------------------
    print("=" * 60)
    print("1. Linear vs non-linear: 5-fold CV with intervals")
    print("=" * 60)

    regressors = {
        "OLS (linear)": None,
        "RandomForest": RandomForestRegressor(
            n_estimators=50, max_depth=5, random_state=42, n_jobs=-1,
        ),
    }

    scorers = make_interval_scorers()

    for name, base_reg in regressors.items():
        reg = FunctionalPartialRegressor(
            n_comp=5, n_features=2, method="pace", alpha=0.1,
            base_regressor=base_reg, argvals=t,
        )
        cv = cross_validate(reg, X, Y, cv=5, scoring=scorers)

        print(f"\n   {name}:")
        print(f"     MSE:        {-cv['test_neg_mse'].mean():.4f} "
              f"+/- {cv['test_neg_mse'].std():.4f}")
        print(f"     Coverage:   {cv['test_coverage'].mean():.0%} "
              f"+/- {cv['test_coverage'].std():.0%}")
        print(f"     Band width: {-cv['test_band_width'].mean():.4f}")
        print(f"     Int. score: {-cv['test_interval_score'].mean():.4f}")

    # -----------------------------------------------------------------
    # 2. GridSearchCV: joint tuning of n_comp + regressor
    # -----------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("2. GridSearchCV: n_comp + max_depth")
    print("=" * 60)

    reg = FunctionalPartialRegressor(
        n_features=2, method="pace", alpha=0.1, argvals=t,
        base_regressor=RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1),
    )
    param_grid = {
        "n_comp": [3, 5, 7],
    }
    gs = GridSearchCV(reg, param_grid, cv=5,
                      scoring=_interval_score_scorer, refit=True)
    gs.fit(X, Y)

    print(f"   Best params: {gs.best_params_}")
    print(f"   Best interval score: {-gs.best_score_:.4f}")

    # -----------------------------------------------------------------
    # 3. Non-linear model across observation horizons
    # -----------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("3. Partial-domain: linear vs HGBR")
    print("=" * 60)

    n_train = 150
    for name, base_reg in [("OLS", None),
                           ("RF", RandomForestRegressor(
                               n_estimators=50, max_depth=5,
                               random_state=42, n_jobs=-1))]:
        print(f"\n   {name}:")
        reg = FunctionalPartialRegressor(
            n_comp=5, n_features=2, method="pace", alpha=0.1,
            base_regressor=base_reg, argvals=t,
        )
        reg.fit(X[:n_train], Y[:n_train])

        for frac in [1.0, 0.6, 0.3]:
            c = int(frac * m)
            X_test = np.hstack([X1[n_train:, :c], X2[n_train:, :c]])
            reg.argvals_predict = t[:c] if c < m else None

            y_hat, lower, upper = reg.predict_interval(X_test)
            mse = np.mean((Y[n_train:] - y_hat) ** 2)
            cov = np.all(
                (Y[n_train:] >= lower) & (Y[n_train:] <= upper), axis=1
            ).mean()
            width = np.mean(upper - lower)
            print(f"     {frac:4.0%}: MSE={mse:.4f}  cov={cov:.0%}  "
                  f"width={width:.4f}")
