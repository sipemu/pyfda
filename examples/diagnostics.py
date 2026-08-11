"""Prediction diagnostics for partial-domain functional regression.

Given a fitted FunctionalPartialRegressor and test data, computes
per-observation diagnostic scores to explain *why* a prediction is bad.

Six diagnostic dimensions:

  1. Score-space novelty: is this test curve far from training?
  2. X reconstruction error: are the estimated scores reliable?
  3. Leverage: is the prediction driven by few training observations?
  4. Feature contribution to error: which feature caused the bad fit?
  5. Score estimation disagreement: do truncated and PACE agree?
  6. Conformal flag: did the model already "know" it was uncertain?

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from numpy.typing import NDArray
from scipy.stats import chi2

import sys
sys.path.insert(0, ".")
from partial_predictor_sklearn import (
    FunctionalPartialRegressor,
    _trapezoidal_weights,
    _scores_pace,
    _scores_truncated,
)


@dataclass
class DiagnosticResult:
    """Per-observation diagnostics (n_test rows)."""

    # 1. Score-space novelty: Mahalanobis distance of test scores
    #    from training distribution.  Large = extrapolation risk.
    novelty: NDArray             # (n,)
    novelty_pvalue: NDArray      # (n,)  chi2 p-value

    # 2. X reconstruction: ||X_obs - X_reconstructed||_L2 / ||X_obs||_L2
    #    per observation.  Large = scores don't represent this curve well.
    x_reconstruction_error: NDArray  # (n,)

    # 3. Leverage: hat matrix diagonal.  Large = prediction is sensitive
    #    to this observation (or driven by few neighbors).
    leverage: NDArray            # (n,)

    # 4. Feature-wise contribution to prediction error (if y_true given)
    #    Which feature's contribution C^(j) is most misaligned with Y?
    feature_error: Optional[NDArray] = None  # (n, p)

    # 5. Score estimation disagreement: ||xi_pace - xi_truncated|| / ||xi_pace||
    #    Large = partial observation is too short for reliable estimation.
    score_disagreement: Optional[NDArray] = None  # (n,)

    # 6. Conformal flag: is this observation's band abnormally wide?
    band_width: Optional[NDArray] = None  # (n,) mean width per obs

    # Composite "suspicion" score (higher = more likely problematic)
    suspicion: Optional[NDArray] = None  # (n,)


def diagnose(
    reg: FunctionalPartialRegressor,
    X: NDArray,
    y_true: Optional[NDArray] = None,
    argvals_predict: Optional[NDArray] = None,
) -> DiagnosticResult:
    """Run all diagnostics on test data.

    Parameters
    ----------
    reg : fitted FunctionalPartialRegressor
    X : (n, n_features * m_c)
        Test predictors (full or partial).
    y_true : (n, m_y), optional
        Ground truth Y (enables error decomposition).
    argvals_predict : (m_c,), optional
        Partial grid. If None, inferred from X shape.

    Returns
    -------
    DiagnosticResult
    """
    X = np.asarray(X, dtype=np.float64)
    if y_true is not None:
        y_true = np.asarray(y_true, dtype=np.float64)
        if y_true.ndim == 1:
            y_true = y_true.reshape(-1, 1)

    p = reg.n_features
    m = reg.n_points_

    # Determine partial grid
    m_c = X.shape[1] // p
    if argvals_predict is not None:
        argvals_partial = np.asarray(argvals_predict, dtype=np.float64)
    elif m_c == m:
        argvals_partial = reg.argvals_
    else:
        argvals_partial = reg.argvals_[:m_c]

    X_list = [X[:, j * m_c : (j + 1) * m_c] for j in range(p)]
    idx = np.searchsorted(reg.argvals_, argvals_partial)
    n = X.shape[0]
    K = len(reg.mfpca_["eigenvalues"])

    # ── 1. Score-space novelty ────────────────────────────────────────
    scores_test, score_var = _estimate_scores(reg, X_list, idx, argvals_partial)
    train_scores = reg.mfpca_["scores"]
    eigvals = reg.mfpca_["eigenvalues"]
    # Mahalanobis: D² = sum_k (xi_k / sqrt(lambda_k))^2
    D2 = np.sum(scores_test ** 2 / eigvals, axis=1)
    novelty_pval = 1 - chi2.cdf(D2, df=K)

    # ── 2. X reconstruction error ─────────────────────────────────────
    # Reconstruct X on the observed domain from estimated scores:
    # X_hat^(j)(t) = mu^(j)(t) + sum_k xi_k * phi_k^(j)(t) / w_j
    x_recon_error = np.zeros(n)
    x_norm = np.zeros(n)
    quad_c = _trapezoidal_weights(argvals_partial)
    for j in range(p):
        mu_c = reg.mfpca_["mean"][j * m : (j + 1) * m][idx]
        w_j = reg.mfpca_["weights"][j]
        Phi_j_c = reg.mfpca_["eigenfunctions"][:, j * m : (j + 1) * m][:, idx]
        # Reconstruct (in scaled space, then unscale)
        X_hat_scaled = scores_test @ Phi_j_c  # (n, m_c)
        X_obs_scaled = (X_list[j] - mu_c) * w_j
        diff = X_obs_scaled - X_hat_scaled
        x_recon_error += np.sum(diff ** 2 * quad_c, axis=1)
        x_norm += np.sum(X_obs_scaled ** 2 * quad_c, axis=1)
    x_recon_error = np.sqrt(x_recon_error / np.maximum(x_norm, 1e-12))

    # ── 3. Leverage ───────────────────────────────────────────────────
    # Hat matrix: H = S_test @ (S_train^T S_train)^{-1} @ S_test^T
    # Diagonal only:
    gram = train_scores.T @ train_scores + 1e-10 * np.eye(K)
    gram_inv = np.linalg.inv(gram)
    # h_ii = s_i^T @ gram_inv @ s_i
    leverage = np.sum((scores_test @ gram_inv) * scores_test, axis=1)

    # ── 4. Feature contribution to error ──────────────────────────────
    feature_error = None
    if y_true is not None and reg.regressor_ is None:
        # Use feature_contributions to decompose error
        C, y_pred, mu_y = reg.feature_contributions(X)
        residual = y_true - y_pred  # (n, m_y)
        m_y = y_true.shape[1]

        # For each feature j, how much does removing it improve the error?
        # Approx: correlation between C^(j) and the residual
        feature_error = np.zeros((n, p))
        for j in range(p):
            # Per-obs: how aligned is C^(j) with the overall prediction error?
            # If C^(j) overshoots, it contributes to the error
            y_without_j = y_pred - C[:, j, :]
            err_with = np.mean((y_true - y_pred) ** 2, axis=1)
            err_without = np.mean((y_true - y_without_j) ** 2, axis=1)
            # Negative = feature j is helping; positive = feature j is hurting
            feature_error[:, j] = err_with - err_without

    # ── 5. Score estimation disagreement ──────────────────────────────
    score_disagreement = None
    if reg.sigma2_ is not None and m_c < m:
        # Compare PACE vs truncated
        scores_pace, _ = _scores_pace(
            X_list, idx, reg.mfpca_, reg.sigma2_,
        )
        scores_trunc = _scores_truncated(
            X_list, idx, _trapezoidal_weights(argvals_partial), reg.mfpca_,
        )
        diff_norm = np.linalg.norm(scores_pace - scores_trunc, axis=1)
        pace_norm = np.linalg.norm(scores_pace, axis=1)
        score_disagreement = diff_norm / np.maximum(pace_norm, 1e-12)

    # ── 6. Conformal band width (if calibrated) ──────────────────────
    band_width = None
    if hasattr(reg, "conformal_q_sim_"):
        bw = reg.conformal_q_sim_ * reg.sigma_t_  # (m_y,)
        band_width = np.full(n, np.mean(bw))

    # ── Composite suspicion score ─────────────────────────────────────
    # Normalize each diagnostic to [0, 1] via percentile rank, then average
    def _prank(v):
        from scipy.stats import rankdata
        return rankdata(v) / len(v)

    components = [_prank(D2), _prank(x_recon_error), _prank(leverage)]
    if score_disagreement is not None:
        components.append(_prank(score_disagreement))
    suspicion = np.mean(components, axis=0)

    return DiagnosticResult(
        novelty=D2,
        novelty_pvalue=novelty_pval,
        x_reconstruction_error=x_recon_error,
        leverage=leverage,
        feature_error=feature_error,
        score_disagreement=score_disagreement,
        band_width=band_width,
        suspicion=suspicion,
    )


def _estimate_scores(reg, X_list, idx, argvals_partial):
    """Extract scores using the fitted model's method."""
    if reg.method == "pace" and reg.sigma2_ is not None:
        return _scores_pace(X_list, idx, reg.mfpca_, reg.sigma2_)
    quad_c = _trapezoidal_weights(argvals_partial)
    scores = _scores_truncated(X_list, idx, quad_c, reg.mfpca_)
    return scores, None


def print_diagnostics(
    diag: DiagnosticResult,
    top_k: int = 10,
    feature_names: Optional[List[str]] = None,
):
    """Pretty-print the most suspicious observations."""
    n = len(diag.suspicion)
    ranking = np.argsort(diag.suspicion)[::-1]

    print(f"{'Obs':>5s} {'Susp':>6s} {'Novelty':>8s} {'p-val':>7s} "
          f"{'ReconErr':>9s} {'Leverage':>9s}", end="")
    if diag.score_disagreement is not None:
        print(f" {'ScoreDisagr':>12s}", end="")
    if diag.feature_error is not None:
        p = diag.feature_error.shape[1]
        if feature_names is None:
            feature_names = [f"X{j+1}" for j in range(p)]
        for fn in feature_names:
            print(f" {'Δ'+fn:>8s}", end="")
    print()
    print("─" * 90)

    for rank in range(min(top_k, n)):
        i = ranking[rank]
        print(f"{i:5d} {diag.suspicion[i]:6.3f} "
              f"{diag.novelty[i]:8.2f} {diag.novelty_pvalue[i]:7.4f} "
              f"{diag.x_reconstruction_error[i]:9.4f} "
              f"{diag.leverage[i]:9.4f}", end="")
        if diag.score_disagreement is not None:
            print(f" {diag.score_disagreement[i]:12.4f}", end="")
        if diag.feature_error is not None:
            for j in range(diag.feature_error.shape[1]):
                print(f" {diag.feature_error[i, j]:8.4f}", end="")
        print()


def summarize(diag: DiagnosticResult, threshold: float = 0.8):
    """Categorize observations by dominant issue.

    Returns a dict mapping each suspicious observation (suspicion > threshold)
    to its primary issue and relevant diagnostics.
    """
    n = len(diag.suspicion)
    suspicious = np.where(diag.suspicion > threshold)[0]

    categories = {}
    for i in suspicious:
        reasons = []
        if diag.novelty_pvalue[i] < 0.01:
            reasons.append(("extrapolation",
                           f"Mahalanobis D²={diag.novelty[i]:.1f}, "
                           f"p={diag.novelty_pvalue[i]:.4f}"))
        if diag.x_reconstruction_error[i] > 0.5:
            reasons.append(("poor_reconstruction",
                           f"recon_error={diag.x_reconstruction_error[i]:.3f}"))
        if diag.leverage[i] > 3 * np.median(diag.leverage):
            reasons.append(("high_leverage",
                           f"leverage={diag.leverage[i]:.4f} "
                           f"(median={np.median(diag.leverage):.4f})"))
        if diag.score_disagreement is not None and diag.score_disagreement[i] > 0.5:
            reasons.append(("unreliable_scores",
                           f"PACE/trunc disagree={diag.score_disagreement[i]:.3f}"))
        if diag.feature_error is not None:
            worst_j = np.argmax(diag.feature_error[i])
            if diag.feature_error[i, worst_j] > 0:
                reasons.append(("feature_hurting",
                               f"feature {worst_j} adds error "
                               f"Δ={diag.feature_error[i, worst_j]:.4f}"))
        if not reasons:
            reasons.append(("unknown", "suspicion score high but no single flag"))
        categories[int(i)] = reasons
    return categories


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    np.random.seed(0)

    n_train, n_test, m, p = 200, 50, 40, 2
    t = np.linspace(0, 1, m)
    phases = np.random.uniform(0, 2 * np.pi, n_train + n_test)
    X1 = np.array([np.sin(2 * np.pi * t + p) + 0.2 * np.random.randn(m)
                    for p in phases])
    X2 = np.array([np.cos(4 * np.pi * t + p) + 0.2 * np.random.randn(m)
                    for p in phases])
    Y = 0.5 * X1 + 0.3 * X2 + 0.1 * np.random.randn(n_train + n_test, m)
    X = np.hstack([X1, X2])

    # Inject 5 problematic test observations of different types
    n_total = n_train + n_test
    # Type 1: extrapolation (X far from training)
    X[n_train, :m] = 5 * np.sin(2 * np.pi * t)
    X[n_train, m:] = 5 * np.cos(4 * np.pi * t)
    # Type 2: Y doesn't match the model (non-linear effect)
    Y[n_train + 1] = Y[n_train + 1] ** 3
    # Type 3: noisy feature
    X[n_train + 2, :m] += 3 * np.random.randn(m)
    # Type 4: spike in Y
    Y[n_train + 3, 20] += 5
    # Type 5: phase shift makes partial obs misleading
    X[n_train + 4, :m] = np.sin(2 * np.pi * t + 4.5)  # unusual phase

    X_train, X_test = X[:n_train], X[n_train:]
    Y_train, Y_test = Y[:n_train], Y[n_train:]

    # Fit
    reg = FunctionalPartialRegressor(
        n_comp=5, n_features=2, method="pace", argvals=t,
    )
    reg.fit(X_train, Y_train)

    # --- Full observation diagnostics --------------------------------
    print("=" * 90)
    print("Diagnostics on test set (full observation)")
    print("=" * 90)
    diag = diagnose(reg, X_test, y_true=Y_test)
    print_diagnostics(diag, top_k=10, feature_names=["X1", "X2"])

    # --- Categorize suspicious observations --------------------------
    print(f"\n{'=' * 90}")
    print("Categorized issues (suspicion > 0.8):")
    print("=" * 90)
    cats = summarize(diag, threshold=0.8)
    for obs_idx, reasons in sorted(cats.items()):
        print(f"  Obs {obs_idx}:")
        for reason, detail in reasons:
            print(f"    [{reason}] {detail}")

    # --- Partial observation (60%) -----------------------------------
    print(f"\n{'=' * 90}")
    print("Diagnostics with 60% partial observation")
    print("=" * 90)
    c = int(0.6 * m)
    X_partial = np.hstack([X_test[:, :c], X_test[:, m:m + c]])
    reg.argvals_predict = t[:c]
    diag_partial = diagnose(reg, X_partial, y_true=Y_test,
                             argvals_predict=t[:c])
    print_diagnostics(diag_partial, top_k=10, feature_names=["X1", "X2"])
