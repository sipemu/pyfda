"""Partial-domain functional prediction via MFPCA.

Two score estimation methods:
  - Approach 1: Truncated projection (fast, no distributional assumptions)
  - Approach 2: PACE / conditional expectation (optimal under Gaussian model)

Both combined with conformal prediction intervals.

Dependencies: numpy, scipy (no fdars required).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigh


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class MFPCAResult:
    """Result of multivariate FPCA."""
    eigenvalues: NDArray          # (K,)
    eigenfunctions: NDArray       # (K, p*m) — stacked across features
    scores: NDArray               # (n, K)
    mean: NDArray                 # (p*m,) — stacked means
    weights: NDArray              # (p,) — per-feature scaling weights
    n_features: int               # p
    n_points: int                 # m (grid points per feature)
    cumulative_variance: NDArray  # (K,)


@dataclass
class PredictionResult:
    """Prediction with intervals."""
    y_hat: NDArray                        # (n_new, m) — point predictions
    lower: NDArray                        # (n_new, m) — lower band
    upper: NDArray                        # (n_new, m) — upper band
    scores: NDArray                       # (n_new, K) — estimated scores
    score_variances: Optional[NDArray] = None  # (n_new, K) — PACE only


# ---------------------------------------------------------------------------
# MFPCA
# ---------------------------------------------------------------------------

def mfpca(
    X_list: List[NDArray],
    argvals: NDArray,
    n_comp: int = 5,
    weights: Optional[NDArray] = None,
) -> MFPCAResult:
    """Multivariate FPCA on p functional features.

    Parameters
    ----------
    X_list : list of ndarray, each (n, m)
        p functional predictors, all on the same grid.
    argvals : ndarray (m,)
        Common evaluation grid.
    n_comp : int
        Number of principal components to retain.
    weights : ndarray (p,), optional
        Per-feature scaling weights. Default: normalize each feature
        by its L2 norm so all contribute equally.

    Returns
    -------
    MFPCAResult
    """
    p = len(X_list)
    n, m = X_list[0].shape
    dt = np.diff(argvals)
    # Trapezoidal quadrature weights
    quad_w = np.empty(m)
    quad_w[0] = dt[0] / 2
    quad_w[-1] = dt[-1] / 2
    quad_w[1:-1] = (dt[:-1] + dt[1:]) / 2

    # --- Per-feature centering and scaling --------------------------------
    means = []
    centered = []
    if weights is None:
        weights = np.empty(p)
        for j in range(p):
            mu_j = X_list[j].mean(axis=0)
            means.append(mu_j)
            Xc = X_list[j] - mu_j
            # Normalize by average L2 norm
            avg_norm = np.sqrt(np.mean(np.sum(Xc ** 2 * quad_w, axis=1)))
            weights[j] = 1.0 / max(avg_norm, 1e-12)
            centered.append(Xc * weights[j])
    else:
        for j in range(p):
            mu_j = X_list[j].mean(axis=0)
            means.append(mu_j)
            centered.append((X_list[j] - mu_j) * weights[j])

    # --- Stack: (n, p*m) -------------------------------------------------
    Z = np.hstack(centered)  # (n, p*m)
    mean_stacked = np.hstack(means)  # (p*m,)

    # --- Covariance in the dual space (n x n) for efficiency -------------
    # Build W = diag of quadrature weights, tiled p times
    W = np.tile(quad_w, p)  # (p*m,)

    # Gram matrix G_{ij} = <Z_i, Z_j>_L2 = sum_t Z_i(t) Z_j(t) w(t)
    G = (Z * W) @ Z.T  # (n, n)
    G /= n - 1

    # Eigendecomposition of the Gram matrix
    n_comp = min(n_comp, n - 1, p * m)
    eigvals, eigvecs = eigh(G, subset_by_index=[n - n_comp, n - 1])

    # Reverse to descending order
    eigvals = eigvals[::-1]
    eigvecs = eigvecs[:, ::-1]

    # Discard near-zero eigenvalues
    pos = eigvals > 1e-12
    eigvals = eigvals[pos]
    eigvecs = eigvecs[:, pos]
    K = len(eigvals)

    # --- Recover eigenfunctions from dual eigenvectors --------------------
    # phi_k(t) = (1 / sqrt(lambda_k * (n-1))) * sum_i v_{ik} * Z_i(t)
    phi = np.zeros((K, p * m))
    for k in range(K):
        phi[k] = Z.T @ eigvecs[:, k]
        phi[k] /= np.sqrt(eigvals[k] * (n - 1))

    # --- Scores -----------------------------------------------------------
    # xi_{ik} = <Z_i, phi_k>_L2
    scores = (Z * W) @ phi.T  # (n, K)

    # --- Cumulative variance explained ------------------------------------
    total_var = np.trace(G)
    cum_var = np.cumsum(eigvals) / total_var

    return MFPCAResult(
        eigenvalues=eigvals,
        eigenfunctions=phi,
        scores=scores,
        mean=mean_stacked,
        weights=weights,
        n_features=p,
        n_points=m,
        cumulative_variance=cum_var,
    )


# ---------------------------------------------------------------------------
# Regression: MFPCA scores -> Y(t)
# ---------------------------------------------------------------------------

@dataclass
class FPCRegressionResult:
    """Fitted FPC regression."""
    beta: NDArray         # (K, m_y) — coefficient per PC per grid point
    intercept: NDArray    # (m_y,) — intercept (mean of Y)
    residuals: NDArray    # (n, m_y) — training residuals
    r_squared: NDArray    # (m_y,) — pointwise R^2


def fit_fpc_regression(
    scores: NDArray,
    Y: NDArray,
) -> FPCRegressionResult:
    """Pointwise linear regression from MFPCA scores to Y(t).

    Parameters
    ----------
    scores : ndarray (n, K)
        MFPCA scores from training data.
    Y : ndarray (n, m_y)
        Functional response on the full grid.

    Returns
    -------
    FPCRegressionResult
    """
    n, K = scores.shape
    m_y = Y.shape[1]

    mu_y = Y.mean(axis=0)  # (m_y,)
    Y_c = Y - mu_y

    # OLS: beta = (S^T S)^{-1} S^T Y_c
    # scores are orthogonal by construction, so S^T S ≈ diag(lambda)
    # but use general OLS for robustness
    gram = scores.T @ scores  # (K, K)
    gram_inv = np.linalg.inv(gram + 1e-10 * np.eye(K))
    beta = gram_inv @ (scores.T @ Y_c)  # (K, m_y)

    fitted = scores @ beta + mu_y
    residuals = Y - fitted

    ss_res = np.sum(residuals ** 2, axis=0)
    ss_tot = np.sum(Y_c ** 2, axis=0)
    r_squared = 1 - ss_res / np.maximum(ss_tot, 1e-12)

    return FPCRegressionResult(
        beta=beta,
        intercept=mu_y,
        residuals=residuals,
        r_squared=r_squared,
    )


# ---------------------------------------------------------------------------
# Truncated score estimation from partial observation
# ---------------------------------------------------------------------------

def estimate_scores_truncated(
    X_partial_list: List[NDArray],
    argvals_partial: NDArray,
    argvals_full: NDArray,
    mfpca_result: MFPCAResult,
) -> NDArray:
    """Estimate MFPCA scores from partially observed X|_{[a,c]}.

    Parameters
    ----------
    X_partial_list : list of ndarray, each (n_new, m_c)
        Partial observations of p features on [a, c].
    argvals_partial : ndarray (m_c,)
        Grid on [a, c].
    argvals_full : ndarray (m,)
        Full training grid [a, b].
    mfpca_result : MFPCAResult
        Fitted MFPCA from training.

    Returns
    -------
    ndarray (n_new, K)
        Estimated scores.
    """
    p = mfpca_result.n_features
    m = mfpca_result.n_points
    m_c = len(argvals_partial)
    K = len(mfpca_result.eigenvalues)
    n_new = X_partial_list[0].shape[0]

    # Quadrature weights for [a, c]
    dt_c = np.diff(argvals_partial)
    quad_c = np.empty(m_c)
    quad_c[0] = dt_c[0] / 2
    quad_c[-1] = dt_c[-1] / 2
    if m_c > 2:
        quad_c[1:-1] = (dt_c[:-1] + dt_c[1:]) / 2

    # Find indices in the full grid corresponding to [a, c]
    # Assumes argvals_partial is a prefix of argvals_full
    idx = np.searchsorted(argvals_full, argvals_partial)

    scores = np.zeros((n_new, K))

    for k in range(K):
        # Extract the k-th eigenfunction, restricted to [a, c] for each feature
        numerator = np.zeros(n_new)
        denominator = 0.0

        for j in range(p):
            # Eigenfunction for feature j, restricted to observed grid
            phi_j_full = mfpca_result.eigenfunctions[k, j * m : (j + 1) * m]
            phi_j_c = phi_j_full[idx]

            # Mean for feature j, restricted to observed grid
            mu_j_full = mfpca_result.mean[j * m : (j + 1) * m]
            mu_j_c = mu_j_full[idx]

            w_j = mfpca_result.weights[j]

            # Center and scale the partial observation
            X_centered = (X_partial_list[j] - mu_j_c) * w_j  # (n_new, m_c)

            # Numerator: integral of X_centered * phi over [a, c]
            numerator += X_centered @ (phi_j_c * quad_c)  # (n_new,)

            # Denominator: integral of phi^2 over [a, c]
            denominator += np.sum(phi_j_c ** 2 * quad_c)

        scores[:, k] = numerator / max(denominator, 1e-12)

    return scores


# ---------------------------------------------------------------------------
# PACE: score estimation via conditional expectation (Approach 2)
# ---------------------------------------------------------------------------

def estimate_noise_variance(
    X_list: List[NDArray],
    argvals: NDArray,
    mfpca_result: MFPCAResult,
) -> NDArray:
    """Estimate per-feature measurement noise variance sigma_j^2.

    Uses the difference between sample variance and the variance explained
    by the K retained components.  For dense regular grids this is:
        sigma_j^2 = max(0, mean_t Var[X^(j)(t)] - sum_k lambda_k ||phi_k^(j)||^2)

    Parameters
    ----------
    X_list : list of ndarray, each (n, m)
    argvals : ndarray (m,)
    mfpca_result : MFPCAResult

    Returns
    -------
    ndarray (p,)
        Noise variance per feature.
    """
    p = mfpca_result.n_features
    m = mfpca_result.n_points
    K = len(mfpca_result.eigenvalues)

    dt = np.diff(argvals)
    quad_w = np.empty(m)
    quad_w[0] = dt[0] / 2
    quad_w[-1] = dt[-1] / 2
    quad_w[1:-1] = (dt[:-1] + dt[1:]) / 2
    domain_len = argvals[-1] - argvals[0]

    sigma2 = np.zeros(p)
    for j in range(p):
        w_j = mfpca_result.weights[j]
        mu_j = mfpca_result.mean[j * m : (j + 1) * m]
        Xc = (X_list[j] - mu_j) * w_j
        # Average pointwise variance (integrated)
        total_var = np.sum(np.var(Xc, axis=0, ddof=1) * quad_w) / domain_len

        # Variance explained by the K components
        explained = 0.0
        for k in range(K):
            phi_j = mfpca_result.eigenfunctions[k, j * m : (j + 1) * m]
            explained += mfpca_result.eigenvalues[k] * np.sum(phi_j ** 2 * quad_w) / domain_len

        sigma2[j] = max(total_var - explained, 1e-10)

    return sigma2


def estimate_scores_pace(
    X_partial_list: List[NDArray],
    argvals_partial: NDArray,
    argvals_full: NDArray,
    mfpca_result: MFPCAResult,
    sigma2: NDArray,
) -> Tuple[NDArray, NDArray]:
    """Estimate MFPCA scores via PACE using the Woodbury identity.

    Exploits the low-rank + diagonal structure of Sigma_obs:

        Sigma_obs = Phi @ Lambda @ Phi^T + D

    The BLUP reduces to a (K x K) solve instead of (p*m_c x p*m_c):

        xi = M^{-1} @ Phi^T @ D^{-1} @ X_obs
        M  = Lambda^{-1} + Phi^T @ D^{-1} @ Phi     (K x K)

    Conditional variance: diag(M^{-1}).

    Complexity: O(K^2 * p*m_c + K^3)  instead of  O((p*m_c)^3).

    Parameters
    ----------
    X_partial_list : list of ndarray, each (n_new, m_c)
        Partial observations on [a, c].
    argvals_partial : ndarray (m_c,)
        Grid on [a, c].
    argvals_full : ndarray (m,)
        Full training grid.
    mfpca_result : MFPCAResult
    sigma2 : ndarray (p,)
        Per-feature noise variances.

    Returns
    -------
    scores : ndarray (n_new, K)
        BLUP score estimates.
    score_variances : ndarray (n_new, K)
        Conditional variance of each score.
    """
    p = mfpca_result.n_features
    m = mfpca_result.n_points
    m_c = len(argvals_partial)
    K = len(mfpca_result.eigenvalues)
    n_new = X_partial_list[0].shape[0]

    # Map partial grid to full grid indices
    idx = np.searchsorted(argvals_full, argvals_partial)

    m_obs = p * m_c

    # --- Build stacked observations and eigenfunctions ------------------
    X_obs = np.zeros((n_new, m_obs))
    Phi_obs = np.zeros((K, m_obs))
    for j in range(p):
        mu_j = mfpca_result.mean[j * m : (j + 1) * m]
        w_j = mfpca_result.weights[j]
        X_obs[:, j * m_c : (j + 1) * m_c] = (X_partial_list[j] - mu_j[idx]) * w_j
        for k in range(K):
            phi_j = mfpca_result.eigenfunctions[k, j * m : (j + 1) * m]
            Phi_obs[k, j * m_c : (j + 1) * m_c] = phi_j[idx]

    # --- D^{-1}: inverse of block-diagonal noise matrix -----------------
    d_inv = np.empty(m_obs)
    for j in range(p):
        d_inv[j * m_c : (j + 1) * m_c] = 1.0 / sigma2[j]

    # --- Woodbury: M = Lambda^{-1} + Phi^T D^{-1} Phi  (K x K) --------
    Phi_d = Phi_obs * d_inv  # (K, m_obs) — rows scaled by d_inv
    M = np.diag(1.0 / mfpca_result.eigenvalues) + Phi_d @ Phi_obs.T  # (K, K)

    # --- Scores: M^{-1} @ Phi^T @ D^{-1} @ X_obs^T --------------------
    rhs = Phi_d @ X_obs.T  # (K, n_new)
    scores = np.linalg.solve(M, rhs).T  # (n_new, K)

    # --- Conditional variance: diag(M^{-1}) ----------------------------
    M_inv = np.linalg.inv(M)  # K x K — tiny
    score_variances = np.maximum(np.diag(M_inv), 0.0)
    score_variances = np.tile(score_variances, (n_new, 1))  # (n_new, K)

    return scores, score_variances


# ---------------------------------------------------------------------------
# Parametric prediction intervals from PACE (Approach 2 intervals)
# ---------------------------------------------------------------------------

def parametric_prediction_band(
    y_hat: NDArray,
    score_variances: NDArray,
    regression: FPCRegressionResult,
    alpha: float = 0.1,
) -> Tuple[NDArray, NDArray]:
    """Parametric prediction band from PACE conditional variances.

    Var[Y_hat(t)] = sum_k beta_k(t)^2 * Var[xi_k | X_obs] + sigma_Y^2(t)

    Parameters
    ----------
    y_hat : ndarray (n_new, m_y)
    score_variances : ndarray (n_new, K)
    regression : FPCRegressionResult
    alpha : float

    Returns
    -------
    lower, upper : ndarray (n_new, m_y)
    """
    from scipy.stats import norm as sp_norm

    K, m_y = regression.beta.shape

    # Residual variance per grid point
    sigma2_y = np.var(regression.residuals, axis=0, ddof=1)  # (m_y,)

    # Prediction variance: sum_k beta_k(t)^2 * var_k + sigma2_y(t)
    # score_variances: (n_new, K), beta: (K, m_y)
    pred_var = score_variances @ (regression.beta ** 2) + sigma2_y  # (n_new, m_y)

    z = sp_norm.ppf(1 - alpha / 2)
    half_width = z * np.sqrt(pred_var)

    return y_hat - half_width, y_hat + half_width


# ---------------------------------------------------------------------------
# Predict Y(t) from partial X
# ---------------------------------------------------------------------------

def predict_from_partial(
    scores: NDArray,
    regression: FPCRegressionResult,
) -> NDArray:
    """Predict Y(t) from estimated scores.

    Parameters
    ----------
    scores : ndarray (n_new, K)
    regression : FPCRegressionResult

    Returns
    -------
    ndarray (n_new, m_y)
    """
    return scores @ regression.beta + regression.intercept


# ---------------------------------------------------------------------------
# Conformal prediction intervals
# ---------------------------------------------------------------------------

@dataclass
class ConformalCalibration:
    """Calibrated conformal prediction."""
    sigma_t: NDArray        # (m_y,) — local MAD of residuals per grid point
    quantile: float         # calibrated quantile for simultaneous band
    quantile_pw: NDArray    # (m_y,) — pointwise quantiles
    alpha: float


def calibrate_conformal(
    residuals: NDArray,
    alpha: float = 0.1,
) -> ConformalCalibration:
    """Calibrate conformal prediction from held-out residuals.

    Parameters
    ----------
    residuals : ndarray (n_cal, m_y)
        Prediction residuals on calibration set.
    alpha : float
        Miscoverage level (e.g., 0.1 for 90% bands).

    Returns
    -------
    ConformalCalibration
    """
    n_cal, m_y = residuals.shape
    abs_res = np.abs(residuals)

    # Local scale: MAD per grid point (for adaptive bands)
    sigma_t = np.median(abs_res, axis=0) * 1.4826  # consistent estimator
    sigma_t = np.maximum(sigma_t, 1e-12)

    # Normalized residuals
    norm_res = abs_res / sigma_t  # (n_cal, m_y)

    # Simultaneous: supremum over t
    sup_scores = norm_res.max(axis=1)  # (n_cal,)
    q_level = np.ceil((1 - alpha) * (n_cal + 1)) / n_cal
    q_level = min(q_level, 1.0)
    quantile = np.quantile(sup_scores, q_level)

    # Pointwise quantiles (for pointwise bands)
    quantile_pw = np.quantile(norm_res, q_level, axis=0)  # (m_y,)

    return ConformalCalibration(
        sigma_t=sigma_t,
        quantile=quantile,
        quantile_pw=quantile_pw,
        alpha=alpha,
    )


def prediction_band(
    y_hat: NDArray,
    calibration: ConformalCalibration,
    simultaneous: bool = True,
) -> Tuple[NDArray, NDArray]:
    """Compute prediction band.

    Parameters
    ----------
    y_hat : ndarray (n_new, m_y)
    calibration : ConformalCalibration
    simultaneous : bool
        If True, gives a simultaneous band (valid for all t jointly).
        If False, gives pointwise bands (valid marginally at each t).

    Returns
    -------
    lower, upper : ndarray (n_new, m_y)
    """
    if simultaneous:
        half_width = calibration.quantile * calibration.sigma_t  # (m_y,)
    else:
        half_width = calibration.quantile_pw * calibration.sigma_t

    return y_hat - half_width, y_hat + half_width


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

class PartialPredictor:
    """Predict Y(t) from partially observed X^(1),...,X^(p)|_{[a,c]}.

    Two score estimation methods:
      - ``"truncated"`` (approach 1): fast, renormalized projection
      - ``"pace"`` (approach 2): BLUP under Gaussian model, optimal MSE

    Prediction intervals via:
      - Conformal calibration (distribution-free, used with both methods)
      - Parametric bands from PACE conditional variances (``"pace"`` only,
        available as ``result.lower_parametric`` / ``result.upper_parametric``
        when ``intervals="both"`` or ``intervals="parametric"``)

    Usage
    -----
    >>> pred = PartialPredictor(n_comp=5, method="pace")
    >>> pred.fit(X_list_train, Y_train, argvals)
    >>> result = pred.predict(X_list_partial, argvals_partial)
    >>> result.y_hat    # point predictions
    >>> result.lower    # conformal lower band
    >>> result.upper    # conformal upper band
    """

    def __init__(
        self,
        n_comp: int = 5,
        alpha: float = 0.1,
        cal_fraction: float = 0.25,
        simultaneous: bool = True,
        method: str = "pace",
        intervals: str = "conformal",
        seed: int = 42,
    ):
        """
        Parameters
        ----------
        n_comp : int
            Number of MFPCA components.
        alpha : float
            Miscoverage level for prediction intervals.
        cal_fraction : float
            Fraction of training data held out for conformal calibration.
        simultaneous : bool
            If True, simultaneous band (valid for all t). If False, pointwise.
        method : str
            Score estimation method: ``"truncated"`` or ``"pace"``.
        intervals : str
            Interval method: ``"conformal"``, ``"parametric"`` (PACE only),
            or ``"both"``.
        seed : int
            Random seed for train/calibration split.
        """
        if method not in ("truncated", "pace"):
            raise ValueError(f"method must be 'truncated' or 'pace', got '{method}'")
        if intervals not in ("conformal", "parametric", "both"):
            raise ValueError(f"intervals must be 'conformal', 'parametric', or 'both'")
        if intervals in ("parametric", "both") and method != "pace":
            raise ValueError("parametric intervals require method='pace'")

        self.n_comp = n_comp
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.simultaneous = simultaneous
        self.method = method
        self.intervals = intervals
        self.seed = seed

        self.mfpca_: Optional[MFPCAResult] = None
        self.regression_: Optional[FPCRegressionResult] = None
        self.calibration_: Optional[ConformalCalibration] = None
        self.sigma2_: Optional[NDArray] = None
        self.argvals_: Optional[NDArray] = None

    def fit(
        self,
        X_list: List[NDArray],
        Y: NDArray,
        argvals: NDArray,
    ) -> "PartialPredictor":
        """Fit the predictor.

        Parameters
        ----------
        X_list : list of ndarray, each (n, m)
            p functional predictors on the full grid [a, b].
        Y : ndarray (n, m_y)
            Functional response on the full grid.
        argvals : ndarray (m,)
            Evaluation grid.

        Returns
        -------
        self
        """
        n = X_list[0].shape[0]
        self.argvals_ = argvals

        # --- Train / calibration split -----------------------------------
        rng = np.random.default_rng(self.seed)
        n_cal = max(int(n * self.cal_fraction), 2)
        perm = rng.permutation(n)
        cal_idx = perm[:n_cal]
        train_idx = perm[n_cal:]

        X_train = [X[train_idx] for X in X_list]
        X_cal = [X[cal_idx] for X in X_list]
        Y_train = Y[train_idx]
        Y_cal = Y[cal_idx]

        # --- MFPCA on training set ---------------------------------------
        self.mfpca_ = mfpca(X_train, argvals, n_comp=self.n_comp)

        # --- Regression: scores -> Y(t) ----------------------------------
        self.regression_ = fit_fpc_regression(self.mfpca_.scores, Y_train)

        # --- Noise variance estimation (needed for PACE) -----------------
        if self.method == "pace":
            self.sigma2_ = estimate_noise_variance(
                X_train, argvals, self.mfpca_
            )

        # --- Conformal calibration on held-out set -----------------------
        if self.intervals in ("conformal", "both"):
            cal_scores = self._estimate_scores(X_cal, argvals)
            Y_cal_hat = predict_from_partial(cal_scores, self.regression_)
            cal_residuals = Y_cal - Y_cal_hat
            self.calibration_ = calibrate_conformal(cal_residuals, self.alpha)

        return self

    def _estimate_scores(
        self,
        X_list: List[NDArray],
        argvals_partial: NDArray,
    ) -> NDArray:
        """Estimate scores using the configured method (returns scores only)."""
        if self.method == "pace":
            scores, _ = estimate_scores_pace(
                X_list, argvals_partial, self.argvals_,
                self.mfpca_, self.sigma2_,
            )
            return scores
        else:
            return estimate_scores_truncated(
                X_list, argvals_partial, self.argvals_, self.mfpca_,
            )

    def predict(
        self,
        X_partial_list: List[NDArray],
        argvals_partial: NDArray,
    ) -> PredictionResult:
        """Predict Y(t) from partially observed X|_{[a,c]}.

        Parameters
        ----------
        X_partial_list : list of ndarray, each (n_new, m_c)
            Partial observations of p features on [a, c].
        argvals_partial : ndarray (m_c,)
            Grid on [a, c], must be a prefix of the training grid.

        Returns
        -------
        PredictionResult
        """
        score_variances = None

        if self.method == "pace":
            scores, score_variances = estimate_scores_pace(
                X_partial_list, argvals_partial, self.argvals_,
                self.mfpca_, self.sigma2_,
            )
        else:
            scores = estimate_scores_truncated(
                X_partial_list, argvals_partial, self.argvals_, self.mfpca_,
            )

        y_hat = predict_from_partial(scores, self.regression_)

        # --- Intervals ---------------------------------------------------
        if self.intervals == "parametric":
            lower, upper = parametric_prediction_band(
                y_hat, score_variances, self.regression_, self.alpha,
            )
        elif self.intervals == "conformal":
            lower, upper = prediction_band(
                y_hat, self.calibration_, self.simultaneous,
            )
        else:  # "both" — use conformal as primary, parametric available via score_variances
            lower, upper = prediction_band(
                y_hat, self.calibration_, self.simultaneous,
            )

        return PredictionResult(
            y_hat=y_hat,
            lower=lower,
            upper=upper,
            scores=scores,
            score_variances=score_variances,
        )

    def predict_full(
        self,
        X_list: List[NDArray],
    ) -> PredictionResult:
        """Predict Y(t) from fully observed X (convenience wrapper)."""
        return self.predict(X_list, self.argvals_)

    def prediction_variance(
        self,
        result: PredictionResult,
    ) -> NDArray:
        """Compute pointwise prediction variance from PACE results.

        Only available when method="pace".

        Parameters
        ----------
        result : PredictionResult
            Must have score_variances (from PACE prediction).

        Returns
        -------
        ndarray (n_new, m_y)
            Pointwise prediction variance.
        """
        if result.score_variances is None:
            raise ValueError("score_variances not available (use method='pace')")

        sigma2_y = np.var(self.regression_.residuals, axis=0, ddof=1)
        return result.score_variances @ (self.regression_.beta ** 2) + sigma2_y


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    np.random.seed(0)

    # --- Simulate data ---------------------------------------------------
    n = 200
    m = 100
    t = np.linspace(0, 1, m)

    X1 = np.array([np.sin(2 * np.pi * t + phi) + 0.3 * np.random.randn(m)
                    for phi in np.random.uniform(0, 2 * np.pi, n)])
    X2 = np.array([np.cos(4 * np.pi * t + phi) + 0.3 * np.random.randn(m)
                    for phi in np.random.uniform(0, 2 * np.pi, n)])
    Y = 0.5 * X1 + 0.3 * X2 + np.random.randn(n, m) * 0.2

    X1_train, X1_test = X1[:150], X1[150:]
    X2_train, X2_test = X2[:150], X2[150:]
    Y_train, Y_test = Y[:150], Y[150:]

    horizons = {"Full": m, "60%": 60, "30%": 30}

    # --- Compare both methods --------------------------------------------
    for method in ["truncated", "pace"]:
        print(f"\n{'='*50}")
        print(f"Method: {method.upper()}")
        print(f"{'='*50}")

        pred = PartialPredictor(
            n_comp=5, alpha=0.1, cal_fraction=0.25,
            method=method, intervals="conformal",
        )
        pred.fit([X1_train, X2_train], Y_train, t)

        for name, c_idx in horizons.items():
            t_p = t[:c_idx]
            if c_idx == m:
                res = pred.predict_full([X1_test, X2_test])
            else:
                res = pred.predict(
                    [X1_test[:, :c_idx], X2_test[:, :c_idx]], t_p
                )

            # Simultaneous coverage
            covered = np.all(
                (Y_test >= res.lower) & (Y_test <= res.upper), axis=1
            )
            # Mean prediction error
            rmse = np.sqrt(np.mean((Y_test - res.y_hat) ** 2))
            # Average band width
            avg_width = np.mean(res.upper - res.lower)

            print(f"  {name:5s}: coverage={covered.mean():.0%}  "
                  f"RMSE={rmse:.4f}  band_width={avg_width:.4f}")

            # Show PACE conditional variance if available
            if res.score_variances is not None:
                pred_var = pred.prediction_variance(res)
                print(f"         avg prediction std = {np.sqrt(pred_var.mean()):.4f}")

    # --- Parametric vs conformal bands (PACE only) -----------------------
    print(f"\n{'='*50}")
    print("PACE: parametric vs conformal intervals (30% obs)")
    print(f"{'='*50}")
    print("  Note: conformal gives simultaneous coverage (all t at once)")
    print("        parametric gives pointwise coverage (each t separately)\n")

    for intervals in ["conformal", "parametric"]:
        pred = PartialPredictor(
            n_comp=5, alpha=0.1, cal_fraction=0.25,
            method="pace", intervals=intervals,
        )
        pred.fit([X1_train, X2_train], Y_train, t)
        res = pred.predict([X1_test[:, :30], X2_test[:, :30]], t[:30])

        # Simultaneous coverage: Y(t) in band for ALL t
        cov_sim = np.all(
            (Y_test >= res.lower) & (Y_test <= res.upper), axis=1
        ).mean()
        # Pointwise coverage: average across t of P(Y(t) in band)
        cov_pw = np.mean(
            (Y_test >= res.lower) & (Y_test <= res.upper), axis=0
        ).mean()
        avg_width = np.mean(res.upper - res.lower)
        print(f"  {intervals:12s}: simult_cov={cov_sim:.0%}  "
              f"pointwise_cov={cov_pw:.0%}  band_width={avg_width:.4f}")
