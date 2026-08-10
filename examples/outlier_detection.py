"""Outlier detection for functional response Y using FPCA scores.

Three detection methods based on Y-FPCA scores:

  1. Mahalanobis distance in score space (assumes Gaussian scores)
  2. Robust Mahalanobis via Minimum Covariance Determinant (MCD)
  3. Depth-based (Fraiman-Muniz on scores projected to principal plane)

All return per-observation outlier scores and a boolean mask.  The
sample weights can be fed back into the regressor via ``sample_weight``
(for robust fitting).

Dependencies: numpy, scipy, scikit-learn.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.stats import chi2
from sklearn.covariance import MinCovDet


@dataclass
class OutlierResult:
    """Outlier detection output."""
    distances: NDArray       # (n,) outlier score per observation
    is_outlier: NDArray      # (n,) boolean flag
    threshold: float         # cutoff used
    scores: NDArray          # (n, K) FPCA scores of Y
    eigenvalues: NDArray     # (K,) FPCA eigenvalues
    method: str


# ===================================================================
# FPCA on Y
# ===================================================================

def _fpca_y(Y: NDArray, argvals: NDArray, n_comp: int) -> Tuple[NDArray, NDArray, NDArray]:
    """Simple FPCA on Y via dual eigendecomposition.

    Returns
    -------
    scores : (n, K)
    eigenvalues : (K,)
    mean : (m,)
    """
    n, m = Y.shape
    mu = Y.mean(axis=0)
    Yc = Y - mu

    # Trapezoidal quadrature weights
    dt = np.diff(argvals)
    w = np.empty(m)
    w[0] = dt[0] / 2
    w[-1] = dt[-1] / 2
    if m > 2:
        w[1:-1] = (dt[:-1] + dt[1:]) / 2

    # Dual Gram matrix
    G = (Yc * w) @ Yc.T / (n - 1)

    K = min(n_comp, n - 1)
    from scipy.linalg import eigh
    eigvals, eigvecs = eigh(G, subset_by_index=[n - K, n - 1])
    eigvals, eigvecs = eigvals[::-1], eigvecs[:, ::-1]
    pos = eigvals > 1e-12
    eigvals, eigvecs = eigvals[pos], eigvecs[:, pos]
    K = len(eigvals)

    phi = np.zeros((K, m))
    for k in range(K):
        phi[k] = Yc.T @ eigvecs[:, k] / np.sqrt(eigvals[k] * (n - 1))
    scores = (Yc * w) @ phi.T  # (n, K)
    return scores, eigvals, mu


# ===================================================================
# Detection methods
# ===================================================================

def detect_mahalanobis(
    Y: NDArray,
    argvals: NDArray,
    n_comp: int = 5,
    alpha: float = 0.01,
) -> OutlierResult:
    """Classical Mahalanobis distance on FPCA scores.

    Under Gaussian assumption, D² ~ chi²_K.  Flag if D² > chi²_{K, 1-alpha}.

    Parameters
    ----------
    Y : (n, m)
    argvals : (m,)
    n_comp : int
    alpha : float
        Significance level (e.g. 0.01 flags the top 1% by chi² tail).
    """
    scores, eigvals, _ = _fpca_y(Y, argvals, n_comp)
    # Scores are orthogonal; Sigma = diag(eigvals)
    D2 = np.sum(scores ** 2 / eigvals, axis=1)
    K = len(eigvals)
    threshold = chi2.ppf(1 - alpha, df=K)
    return OutlierResult(
        distances=D2,
        is_outlier=D2 > threshold,
        threshold=float(threshold),
        scores=scores,
        eigenvalues=eigvals,
        method="mahalanobis",
    )


def detect_mcd(
    Y: NDArray,
    argvals: NDArray,
    n_comp: int = 5,
    alpha: float = 0.01,
    support_fraction: float = 0.75,
    random_state: int = 0,
) -> OutlierResult:
    """Robust Mahalanobis via Minimum Covariance Determinant.

    More reliable when a substantial fraction of Y curves are outliers
    (classical Mahalanobis covariance is contaminated by them).

    Parameters
    ----------
    support_fraction : float
        Fraction of data assumed non-outlier when estimating robust
        covariance (default 0.75).  Lower = more tolerant to outliers.
    """
    scores, eigvals, _ = _fpca_y(Y, argvals, n_comp)
    mcd = MinCovDet(
        support_fraction=support_fraction,
        random_state=random_state,
    ).fit(scores)
    D2 = mcd.mahalanobis(scores)
    K = scores.shape[1]
    threshold = chi2.ppf(1 - alpha, df=K)
    return OutlierResult(
        distances=D2,
        is_outlier=D2 > threshold,
        threshold=float(threshold),
        scores=scores,
        eigenvalues=eigvals,
        method="mcd",
    )


def detect_bagplot(
    Y: NDArray,
    argvals: NDArray,
    n_comp: int = 2,
    factor: float = 2.5,
) -> OutlierResult:
    """Bivariate bagplot on first two FPCA scores (Hyndman & Shang 2010).

    Flags observations outside ``factor`` times the half-space depth
    equivalent of the MCD hull in the score plane.

    Implemented here as a simplified robust distance on the first
    n_comp scores (default 2 for 2-D bagplot).
    """
    scores, eigvals, _ = _fpca_y(Y, argvals, n_comp)
    # Robust median via geometric median (Weiszfeld)
    center = scores.mean(axis=0)
    for _ in range(50):
        d = np.linalg.norm(scores - center, axis=1)
        w = 1.0 / np.maximum(d, 1e-6)
        new_center = (w[:, None] * scores).sum(axis=0) / w.sum()
        if np.linalg.norm(new_center - center) < 1e-8:
            break
        center = new_center

    dists = np.linalg.norm(scores - center, axis=1)
    mad = 1.4826 * np.median(np.abs(dists - np.median(dists)))
    threshold = float(np.median(dists) + factor * mad)
    return OutlierResult(
        distances=dists,
        is_outlier=dists > threshold,
        threshold=threshold,
        scores=scores,
        eigenvalues=eigvals,
        method="bagplot",
    )


# ===================================================================
# Weight functions: convert distances to sample weights
# ===================================================================

def weights_from_distances(
    distances: NDArray,
    method: str = "huber",
    threshold: Optional[float] = None,
    scale: Optional[float] = None,
) -> NDArray:
    """Convert outlier distances to sample weights in [0, 1].

    Methods
    -------
    "huber"    : w = 1 if d <= threshold else threshold / d
    "tukey"    : w = (1 - (d/threshold)²)² if d <= threshold else 0
    "hard"     : w = 1 if d <= threshold else 0  (drop outliers)
    "smooth"   : w = exp(-0.5 * (d/scale)²)      (Gaussian decay)

    Returns
    -------
    ndarray (n,) of weights in [0, 1].
    """
    d = np.asarray(distances, dtype=np.float64)
    if threshold is None:
        threshold = float(np.median(d) + 3 * 1.4826 * np.median(
            np.abs(d - np.median(d))
        ))

    if method == "huber":
        w = np.minimum(1.0, threshold / np.maximum(d, 1e-12))
    elif method == "tukey":
        r = d / threshold
        w = np.where(r <= 1.0, (1 - r ** 2) ** 2, 0.0)
    elif method == "hard":
        w = (d <= threshold).astype(np.float64)
    elif method == "smooth":
        if scale is None:
            scale = float(np.median(d))
        w = np.exp(-0.5 * (d / max(scale, 1e-12)) ** 2)
    else:
        raise ValueError(f"Unknown weight method: {method}")

    return w


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    np.random.seed(0)

    # Simulate 200 "clean" curves + 15 outliers
    n_clean = 200
    n_out = 15
    m = 60
    t = np.linspace(0, 1, m)

    phases = np.random.uniform(0, 2 * np.pi, n_clean)
    Y_clean = np.array([np.sin(2 * np.pi * t + phi) for phi in phases])
    Y_clean += 0.1 * np.random.randn(n_clean, m)

    # Outliers: three types
    Y_out = []
    for _ in range(5):  # magnitude outliers (shifted up/down)
        phi = np.random.uniform(0, 2 * np.pi)
        Y_out.append(np.sin(2 * np.pi * t + phi) + np.random.choice([3, -3]))
    for _ in range(5):  # shape outliers (different frequency)
        phi = np.random.uniform(0, 2 * np.pi)
        Y_out.append(2 * np.sin(6 * np.pi * t + phi))
    for _ in range(5):  # spike outliers
        y = np.sin(2 * np.pi * t + np.random.uniform(0, 2 * np.pi))
        y[np.random.randint(10, 50)] += np.random.choice([4, -4])
        Y_out.append(y)
    Y_out = np.array(Y_out)

    Y = np.vstack([Y_clean, Y_out])
    n = n_clean + n_out
    true_outliers = np.zeros(n, dtype=bool)
    true_outliers[n_clean:] = True

    # Shuffle
    perm = np.random.permutation(n)
    Y, true_outliers = Y[perm], true_outliers[perm]

    print("=" * 70)
    print(f"Simulated: {n_clean} clean + {n_out} outlier curves (total n={n})")
    print("=" * 70)

    for name, detector in [
        ("Classical Mahalanobis (5 PCs, alpha=0.01)",
         lambda: detect_mahalanobis(Y, t, n_comp=5, alpha=0.01)),
        ("Robust MCD (5 PCs, support=0.75)",
         lambda: detect_mcd(Y, t, n_comp=5, alpha=0.01, support_fraction=0.75)),
        ("Bagplot (2 PCs, factor=2.5)",
         lambda: detect_bagplot(Y, t, n_comp=2, factor=2.5)),
    ]:
        r = detector()
        detected = r.is_outlier
        tp = int(np.sum(detected & true_outliers))
        fp = int(np.sum(detected & ~true_outliers))
        fn = int(np.sum(~detected & true_outliers))
        tn = int(np.sum(~detected & ~true_outliers))
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        print(f"\n  {name}:")
        print(f"    detected = {detected.sum():3d}  "
              f"(TP={tp} FP={fp} FN={fn})  "
              f"precision={precision:.2f} recall={recall:.2f}")
        print(f"    threshold={r.threshold:.3f}, "
              f"max distance={r.distances.max():.3f}")

    # Weight functions demo
    print(f"\n{'=' * 70}")
    print("Converting distances → sample weights")
    print("=" * 70)
    r = detect_mcd(Y, t, n_comp=5, alpha=0.01)
    for wm in ["huber", "tukey", "hard", "smooth"]:
        w = weights_from_distances(r.distances, method=wm,
                                     threshold=r.threshold)
        print(f"  {wm:7s}: clean mean w = {w[~true_outliers].mean():.3f}, "
              f"outlier mean w = {w[true_outliers].mean():.3f}, "
              f"total weight reduction = "
              f"{1 - w.sum() / len(w):.1%}")
