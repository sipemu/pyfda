"""Fast bias-correction diagnostic.

Answers two questions on your real data:

  1. IS there systematic bias?    (look at mean residual curves)
  2. Is the bias PREDICTABLE from X?  (fit a tiny bias model, check CV R²)

If both yes -> bias_correction.py will help.
If only (1) -> the bias is constant; just shift the predictions.
If only (2) is moderate -> may help, run full bias correction to verify.
If neither -> don't bother.

Uses training Y once (to compute residuals).  Once you have a verdict
and decide to use bias correction, deployment needs X only.

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
from numpy.typing import NDArray
from sklearn.base import clone
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

import sys
sys.path.insert(0, ".")
from partial_predictor_sklearn import (
    FunctionalPartialRegressor,
    _trapezoidal_weights,
    _scores_pace,
    _scores_truncated,
)


@dataclass
class BiasCheckResult:
    """Diagnostic summary."""
    cutoff_grid: NDArray              # (n_cutoffs,)
    cutoff_times: NDArray             # (n_cutoffs,)

    # Per-cutoff descriptors
    mean_residual: NDArray            # (n_cutoffs, m_y) — mean residual curve
    rmse: NDArray                     # (n_cutoffs,) — overall RMSE per cutoff
    mean_abs_bias: NDArray            # (n_cutoffs,) — max |mean residual(t)|

    # Bias predictability: cross-validated R² of a small bias model
    bias_r2: NDArray                  # (n_cutoffs,) — R² of bias model on residuals
    bias_r2_overall: float            # pooled R² across all cutoffs

    # Bias as fraction of total Y variance (signal strength)
    bias_var_ratio: NDArray           # (n_cutoffs,) — Var[mean_resid] / Var[Y]

    # Verdict
    verdict: str


def _extract_scores_at(reg, X_partial, argvals_partial):
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


def diagnose_bias(
    regressor: FunctionalPartialRegressor,
    X: NDArray,
    y: NDArray,
    cutoff_grid: Optional[Sequence[int]] = None,
    cal_fraction: float = 0.3,
    cv_folds: int = 5,
    seed: int = 42,
) -> BiasCheckResult:
    """Fast check for whether bias correction would help.

    Parameters
    ----------
    regressor : FunctionalPartialRegressor
        Unfitted base regressor.
    X, y : array-like
        Training data with both X and Y available.  After diagnosis,
        deployment will only need X.
    cutoff_grid : sequence of int or None
        Grid of cutoffs to evaluate.  Default: 5 evenly spaced from
        20% to 100% of the domain.
    cal_fraction : float
        Fraction of data held out from base training for residual
        evaluation.
    cv_folds : int
        CV folds for the bias-model R² estimate.
    seed : int

    Returns
    -------
    BiasCheckResult with diagnostics and a textual verdict.
    """
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 1:
        y = y.reshape(-1, 1)

    # Train/eval split: base regressor only sees train portion
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    n_eval = max(int(n * cal_fraction), 10)
    perm = rng.permutation(n)
    eval_idx, fit_idx = perm[:n_eval], perm[n_eval:]

    base = clone(regressor)
    base.fit(X[fit_idx], y[fit_idx])

    p = base.n_features
    m = base.n_points_
    argvals = base.argvals_

    if cutoff_grid is None:
        cutoff_grid = np.linspace(0.2, 1.0, 5)
        cutoff_grid = np.unique(np.maximum(3, (cutoff_grid * m).astype(int)))
    else:
        cutoff_grid = np.asarray(cutoff_grid, dtype=int)

    X_eval, y_eval = X[eval_idx], y[eval_idx]
    y_var_total = float(np.var(y_eval))

    rmses = np.zeros(len(cutoff_grid))
    mean_residuals = np.zeros((len(cutoff_grid), y.shape[1]))
    mean_abs_bias = np.zeros(len(cutoff_grid))
    bias_var_ratios = np.zeros(len(cutoff_grid))
    bias_r2s = np.zeros(len(cutoff_grid))
    cutoff_times = np.zeros(len(cutoff_grid))

    # Bias model: pointwise OLS over Y(t), with polynomial-augmented scores
    # Use a single ridge model over all m_y outputs to keep CV cheap
    score_pool, resid_pool = [], []  # for overall R²

    for k_idx, c in enumerate(cutoff_grid):
        cutoff_t = float(argvals[c - 1])
        cutoff_times[k_idx] = cutoff_t

        X_eval_partial = np.hstack([
            X_eval[:, j * m : j * m + c] for j in range(p)
        ])

        base.argvals_predict = argvals[:c]
        y_hat = base.predict(X_eval_partial)
        base.argvals_predict = None

        resid = y_eval - y_hat                              # (n_eval, m_y)
        rmses[k_idx] = float(np.sqrt(np.mean(resid ** 2)))
        mean_residuals[k_idx] = resid.mean(axis=0)
        mean_abs_bias[k_idx] = float(np.max(np.abs(mean_residuals[k_idx])))
        bias_var_ratios[k_idx] = float(np.var(mean_residuals[k_idx]) /
                                         max(y_var_total, 1e-12))

        # CV R² of a tiny bias model on the residuals
        scores = _extract_scores_at(base, X_eval_partial, argvals[:c])

        # Reduce residual to a small target (mean over output grid) for a
        # fast scalar CV — full functional R² is messier and slower
        resid_target = resid.mean(axis=1)  # (n_eval,)

        pipe = make_pipeline(
            PolynomialFeatures(degree=2, include_bias=False),
            Ridge(alpha=1.0),
        )
        try:
            cv_r2 = cross_val_score(
                pipe, scores, resid_target,
                cv=min(cv_folds, len(eval_idx) // 5),
                scoring="r2",
            ).mean()
        except ValueError:
            cv_r2 = 0.0
        bias_r2s[k_idx] = float(cv_r2)

        score_pool.append(scores)
        resid_pool.append(resid_target)

    # Pooled R²: bias model on all cutoffs jointly with cutoff_t as feature
    # (this is what BiasCorrectedRegressor actually does, so it's the most
    # relevant single number)
    feat_pool = np.vstack([
        np.hstack([s, np.full((len(s), 1), cutoff_times[i])])
        for i, s in enumerate(score_pool)
    ])
    targ_pool = np.concatenate(resid_pool)
    pipe = make_pipeline(
        PolynomialFeatures(degree=2, include_bias=False),
        Ridge(alpha=1.0),
    )
    try:
        bias_r2_overall = float(cross_val_score(
            pipe, feat_pool, targ_pool, cv=cv_folds, scoring="r2",
        ).mean())
    except ValueError:
        bias_r2_overall = 0.0

    # Verdict
    bias_grows = (mean_abs_bias[-1] > 1.5 * mean_abs_bias[0]
                  and mean_abs_bias[-1] > 0.05)
    if bias_r2_overall > 0.1:
        verdict = ("STRONG: bias is predictable from X "
                   f"(pooled CV R² = {bias_r2_overall:.3f}). "
                   "Apply BiasCorrectedRegressor.")
    elif bias_r2_overall > 0.02:
        verdict = (f"MODEST: some predictable bias "
                   f"(pooled CV R² = {bias_r2_overall:.3f}). "
                   "Try BiasCorrectedRegressor; gains may be small.")
    elif bias_grows:
        verdict = (f"CONSTANT BIAS DETECTED but not predictable from X "
                   f"(CV R² = {bias_r2_overall:.3f}, |mean bias| grows from "
                   f"{mean_abs_bias[0]:.3f} to {mean_abs_bias[-1]:.3f}). "
                   "Just shift Y_hat by mean residual per cutoff — no model needed.")
    else:
        verdict = (f"NO BIAS to correct "
                   f"(CV R² = {bias_r2_overall:.3f}, |mean bias| ~ "
                   f"{mean_abs_bias.mean():.3f}). "
                   "Skip bias correction.")

    return BiasCheckResult(
        cutoff_grid=np.asarray(cutoff_grid),
        cutoff_times=cutoff_times,
        mean_residual=mean_residuals,
        rmse=rmses,
        mean_abs_bias=mean_abs_bias,
        bias_r2=bias_r2s,
        bias_r2_overall=bias_r2_overall,
        bias_var_ratio=bias_var_ratios,
        verdict=verdict,
    )


def print_bias_check(result: BiasCheckResult):
    """Pretty-print the diagnostic."""
    print(f"{'cutoff':>8s} {'t*':>8s} {'rmse':>8s} {'|μ_R|':>8s} "
          f"{'CV R²':>8s} {'σ²(R)/σ²(Y)':>13s}")
    print("─" * 60)
    for i in range(len(result.cutoff_grid)):
        print(f"{result.cutoff_grid[i]:>8d} "
              f"{result.cutoff_times[i]:>8.3f} "
              f"{result.rmse[i]:>8.4f} "
              f"{result.mean_abs_bias[i]:>8.4f} "
              f"{result.bias_r2[i]:>+8.3f} "
              f"{result.bias_var_ratio[i]:>13.4f}")
    print()
    print(f"  Pooled CV R² of bias model: {result.bias_r2_overall:+.4f}")
    print()
    print(f"VERDICT: {result.verdict}")


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    np.random.seed(0)

    n, m = 400, 60
    t = np.linspace(0, 1, m)
    phases1 = np.random.uniform(0, 2 * np.pi, n)
    phases2 = np.random.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
    X1 += 0.2 * np.random.randn(n, m)
    X2 += 0.2 * np.random.randn(n, m)
    X = np.hstack([X1, X2])

    # ----- Scenario A: per-curve quadratic bias (CORRECTABLE) ---------
    phi1c = (phases1 - phases1.mean()) / phases1.std()
    bias_curve = 1.2 * (phi1c ** 2)[:, None] * t[None, :]
    Y_A = 0.5 * X1 + 0.3 * X2 + bias_curve + 0.05 * np.random.randn(n, m)

    # ----- Scenario B: pure linear (NO bias to correct) ---------------
    Y_B = 0.5 * X1 + 0.3 * X2 + 0.15 * np.random.randn(n, m)

    # ----- Scenario C: constant bias that grows with t ----------------
    Y_C = 0.5 * X1 + 0.3 * X2 + 0.4 * t[None, :] + 0.05 * np.random.randn(n, m)

    for label, Y in [("A: per-curve nonlinear bias (correctable)", Y_A),
                      ("B: linear, no bias",                       Y_B),
                      ("C: constant additive bias growing with t", Y_C)]:
        print("=" * 75)
        print(f"Scenario {label}")
        print("=" * 75)
        reg = FunctionalPartialRegressor(
            n_comp=5, n_features=2, method="pace", argvals=t,
        )
        result = diagnose_bias(reg, X, Y, cv_folds=5)
        print_bias_check(result)
        print()
