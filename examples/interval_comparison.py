"""Coverage and band-width comparison for MFPCA / FPLS / Hybrid.

Evaluates all three partial-domain regressors with conformal prediction
intervals (simultaneous via puncc) at multiple observation horizons.

Metrics:
  - Simultaneous coverage: P(Y(t) in band for ALL t) — target 1-alpha
  - Pointwise coverage:    mean over t of P(Y(t) in band(t))
  - Mean band width:       avg of (upper - lower) over all (n, t)
  - Interval score:        proper scoring rule (Gneiting & Raftery 2007)

Dependencies: numpy, scipy, scikit-learn, puncc.
"""

from __future__ import annotations

import sys, warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
sys.path.insert(0, ".")

import numpy as np
from sklearn.model_selection import train_test_split

from partial_predictor_sklearn import FunctionalPartialRegressor
from fpls_partial import FPLSPartialRegressor
from hybrid_mfpca_pls import MFPCAPLSHybrid
from puncc_integration import SimultaneousPunccIntervals, PointwisePunccIntervals


# ===================================================================
# Metrics
# ===================================================================

def interval_score(y_true, lower, upper, alpha=0.1):
    """Gneiting & Raftery (2007) interval score — lower is better."""
    width = upper - lower
    pen_low = (2 / alpha) * np.maximum(lower - y_true, 0)
    pen_hi  = (2 / alpha) * np.maximum(y_true - upper, 0)
    return float(np.mean(width + pen_low + pen_hi))


def evaluate_intervals(y_true, y_pred, lower, upper, alpha=0.1):
    cov_sim = np.all((y_true >= lower) & (y_true <= upper), axis=1).mean()
    cov_pw  = np.mean((y_true >= lower) & (y_true <= upper))
    width   = np.mean(upper - lower)
    iscore  = interval_score(y_true, lower, upper, alpha=alpha)
    mse     = np.mean((y_true - y_pred) ** 2)
    return dict(mse=mse, cov_sim=cov_sim, cov_pw=cov_pw,
                 width=width, iscore=iscore)


# ===================================================================
# Data simulation (same as previous comparisons for continuity)
# ===================================================================

def simulate(n=300, m=60, seed=0):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    phases1 = rng.uniform(0, 2 * np.pi, n)
    phases2 = rng.uniform(0, 2 * np.pi, n)
    X1 = np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
    X2 = np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
    noise1 = np.array([0.8 * np.sin(10 * np.pi * t + rng.uniform(0, 2 * np.pi))
                        for _ in range(n)])
    X1 = X1 + noise1
    X2 = X2 + 0.3 * rng.standard_normal((n, m))
    Y = (0.5 * np.array([np.sin(2 * np.pi * t + phi) for phi in phases1])
         + 0.3 * np.array([np.cos(4 * np.pi * t + phi) for phi in phases2])
         + 0.15 * rng.standard_normal((n, m)))
    return X1, X2, Y, t


# ===================================================================
# Base regressor factories (share hyperparameters for fair comparison)
# ===================================================================

def build_regressors(K_base: int, K_pls: int, t):
    return {
        "MFPCA (K=8)": FunctionalPartialRegressor(
            n_comp=K_base, n_features=2, method="pace", argvals=t,
        ),
        "FPLS (K=3)": FPLSPartialRegressor(
            n_comp=K_pls, n_features=2, argvals=t,
        ),
        "Hybrid (MFPCA=8, PLS=5)": MFPCAPLSHybrid(
            n_comp=K_base, n_pls=min(5, K_base),
            n_features=2, method="pace", argvals=t,
        ),
    }


# ===================================================================
# Main comparison
# ===================================================================

def main():
    ALPHA = 0.1
    TARGET = 1 - ALPHA

    X1, X2, Y, t = simulate(n=300, m=60, seed=0)
    m = len(t)
    X = np.hstack([X1, X2])

    X_train, X_test, Y_train, Y_test, idx_tr, idx_te = train_test_split(
        X, Y, np.arange(len(X)), test_size=100, random_state=0,
    )
    X1_test, X2_test = X1[idx_te], X2[idx_te]

    # Helper: partial X at horizon c
    def partial_test(c):
        return np.hstack([X1_test[:, :c], X2_test[:, :c]])

    horizons = [1.0, 0.6, 0.3]
    regressors = build_regressors(K_base=8, K_pls=3, t=t)

    # Build a matrix of results: rows = (method, wrapper), cols = horizon
    # For each base method, evaluate with pointwise and simultaneous conformal

    print("=" * 95)
    print(f"Conformal intervals — target coverage {TARGET:.0%}")
    print("Metrics at horizons 100% / 60% / 30%")
    print("=" * 95)

    for base_name, base_reg in regressors.items():
        print(f"\n{'─' * 95}")
        print(f"{base_name}")
        print(f"{'─' * 95}")

        for wrapper_name, Wrapper in [
            ("pointwise (puncc SplitCP per t)", PointwisePunccIntervals),
            ("simultaneous (puncc + sup-norm)", SimultaneousPunccIntervals),
        ]:
            # Refit fresh regressor for each wrapper (conformal does train/cal split)
            reg = type(base_reg)(**base_reg.get_params())
            if isinstance(Wrapper, type) and issubclass(
                Wrapper, SimultaneousPunccIntervals):
                cp = Wrapper(reg, alpha=ALPHA, scale="mad")
            else:
                cp = Wrapper(reg, alpha=ALPHA)
            cp.fit(X_train, Y_train)

            row = f"  {wrapper_name:36s}"
            for frac in horizons:
                c = int(frac * m)
                if c == m:
                    X_te = X_test
                    reg.argvals_predict = None
                else:
                    X_te = partial_test(c)
                    reg.argvals_predict = t[:c]

                y_pred, lower, upper = cp.predict(X_te)
                r = evaluate_intervals(Y_test, y_pred, lower, upper, ALPHA)
                marker = "✓" if r["cov_sim"] >= TARGET - 0.05 else " "
                row += (f"  [{frac:.0%}] "
                        f"sim={r['cov_sim']:.0%}{marker} "
                        f"w={r['width']:.3f} IS={r['iscore']:.3f} |")
            print(row)

    # =================================================================
    # Summary table: best band width per horizon (at target coverage)
    # =================================================================
    print()
    print("=" * 95)
    print("Interval score (lower = better) — penalizes both width and miscoverage")
    print("=" * 95)

    # Recompute systematically for a clean table
    results = {}  # {(method, wrapper): {frac: iscore}}
    for base_name, base_reg in regressors.items():
        for wrapper_name, Wrapper in [
            ("pw",  PointwisePunccIntervals),
            ("sim", SimultaneousPunccIntervals),
        ]:
            reg = type(base_reg)(**base_reg.get_params())
            if Wrapper is SimultaneousPunccIntervals:
                cp = Wrapper(reg, alpha=ALPHA, scale="mad")
            else:
                cp = Wrapper(reg, alpha=ALPHA)
            cp.fit(X_train, Y_train)
            row_scores = {}
            for frac in horizons:
                c = int(frac * m)
                X_te = X_test if c == m else partial_test(c)
                reg.argvals_predict = None if c == m else t[:c]
                y_pred, lower, upper = cp.predict(X_te)
                r = evaluate_intervals(Y_test, y_pred, lower, upper, ALPHA)
                row_scores[frac] = (r["cov_sim"], r["width"], r["iscore"])
            results[(base_name, wrapper_name)] = row_scores

    # Pretty table
    print(f"\n{'Method':<30s} {'Wrapper':<6s}  " +
          "  ".join(f"{int(f*100)}%"
                     .center(24) for f in horizons))
    print("─" * 95)
    for (method, wrapper), scores in results.items():
        row = f"{method:<30s} {wrapper:<6s}  "
        for frac in horizons:
            cov, width, iscore = scores[frac]
            row += f"IS={iscore:.3f} (cov={cov:.0%}){' ' * 3}"
        print(row)


if __name__ == "__main__":
    main()
