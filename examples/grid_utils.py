"""Grid alignment and interpolation utilities for functional data.

Handles the common preprocessing scenario:

- Each sample i has its own grid t_i (length m_i, may vary across samples).
- Within one sample, all p features AND the response share the same grid t_i.
- Missing values (NaN) may appear in X features.
- Goal: interpolate everything onto a common, evenly spaced grid.

Dependencies: numpy, scipy.
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import interp1d


# ===================================================================
# Single-curve interpolation
# ===================================================================

def interpolate_curve(
    t_source: NDArray,
    values: NDArray,
    t_target: NDArray,
    method: str = "linear",
    extrapolate: str = "nearest",
) -> NDArray:
    """Interpolate one curve (or multiple co-located curves) to a new grid.

    Parameters
    ----------
    t_source : ndarray (m_src,)
        Original grid points.
    values : ndarray (m_src,) or (p, m_src)
        Curve values.  If 2-D, each row is a separate feature on the
        same grid (all features of one sample).
    t_target : ndarray (m_tgt,)
        Target grid points.
    method : str
        Interpolation: "linear", "cubic", "nearest", "quadratic".
    extrapolate : str
        How to handle target points outside the source range:
        "nearest" (extend boundary values), "nan" (leave as NaN),
        "zero" (fill with 0).

    Returns
    -------
    ndarray (m_tgt,) or (p, m_tgt)
        Interpolated values on the target grid.
    """
    is_1d = values.ndim == 1
    if is_1d:
        values = values.reshape(1, -1)

    p, m_src = values.shape
    m_tgt = len(t_target)
    result = np.empty((p, m_tgt), dtype=np.float64)

    for j in range(p):
        y = values[j]
        mask = np.isfinite(y)
        if mask.sum() < 2:
            result[j] = np.nan
            continue

        t_valid = t_source[mask]
        y_valid = y[mask]

        f = interp1d(
            t_valid, y_valid, kind=method,
            bounds_error=False, fill_value=np.nan,
        )
        result[j] = f(t_target)

        # Handle extrapolation
        nans = np.isnan(result[j])
        if nans.any():
            left = t_target < t_valid[0]
            right = t_target > t_valid[-1]
            if extrapolate == "nearest":
                result[j, left] = y_valid[0]
                result[j, right] = y_valid[-1]
            elif extrapolate == "zero":
                result[j, left] = 0.0
                result[j, right] = 0.0
            # "nan": leave as-is

    return result[0] if is_1d else result


# ===================================================================
# Grid construction
# ===================================================================

def make_common_grid(
    grids: List[NDArray],
    n_points: int = 100,
    t_min: Optional[float] = None,
    t_max: Optional[float] = None,
    range_mode: str = "intersection",
) -> NDArray:
    """Create an evenly spaced common grid from a collection of sample grids.

    Parameters
    ----------
    grids : list of ndarray
        n grids, one per sample. Each may have different length.
    n_points : int
        Number of points in the common grid.
    t_min, t_max : float, optional
        Override domain bounds.
    range_mode : str
        How to determine the domain:
        - "intersection": max of all mins, min of all maxs (no extrapolation)
        - "union": min of all mins, max of all maxs (may require extrapolation)
        - "median": use the median of mins/maxs (robust to outlier grids)

    Returns
    -------
    ndarray (n_points,)
        Evenly spaced grid.
    """
    mins = np.array([g[0] for g in grids])
    maxs = np.array([g[-1] for g in grids])

    if t_min is None:
        if range_mode == "intersection":
            t_min = float(np.max(mins))
        elif range_mode == "union":
            t_min = float(np.min(mins))
        else:
            t_min = float(np.median(mins))

    if t_max is None:
        if range_mode == "intersection":
            t_max = float(np.min(maxs))
        elif range_mode == "union":
            t_max = float(np.max(maxs))
        else:
            t_max = float(np.median(maxs))

    if t_min >= t_max:
        raise ValueError(
            f"Empty domain [{t_min}, {t_max}]. "
            f"Grid ranges don't overlap sufficiently."
        )

    return np.linspace(t_min, t_max, n_points)


# ===================================================================
# Align X features (all samples to one common grid)
# ===================================================================

def align_X(
    X_per_sample: List[NDArray],
    grids: List[NDArray],
    n_points: int = 100,
    t_min: Optional[float] = None,
    t_max: Optional[float] = None,
    range_mode: str = "intersection",
    method: str = "linear",
    extrapolate: str = "nearest",
) -> Tuple[List[NDArray], NDArray]:
    """Align X features from per-sample grids to a common evenly spaced grid.

    Parameters
    ----------
    X_per_sample : list of ndarray
        n arrays.  Each is either:
        - shape (p, m_i): p features for sample i on grid of length m_i
        - shape (m_i,): single feature (p=1)
    grids : list of ndarray
        n arrays, each (m_i,) — the grid for sample i.
    n_points : int
        Common grid size.
    t_min, t_max : float, optional
        Override domain bounds.
    range_mode : str
        "intersection", "union", or "median".
    method : str
        Interpolation method.
    extrapolate : str
        Extrapolation mode: "nearest", "nan", "zero".

    Returns
    -------
    X_aligned : list of ndarray
        p arrays, each (n, n_points) — one per feature, ready for stacking.
    t_common : ndarray (n_points,)
        The common grid.

    Example
    -------
    >>> # 50 samples, 3 features each, varying grid lengths
    >>> X_samples = [np.random.randn(3, np.random.randint(60, 120))
    ...             for _ in range(50)]
    >>> grids = [np.linspace(0, 1, x.shape[1]) for x in X_samples]
    >>> X_aligned, t = align_X(X_samples, grids, n_points=100)
    >>> X_aligned[0].shape  # (50, 100) — feature 1
    >>> X_aligned[1].shape  # (50, 100) — feature 2
    """
    n = len(X_per_sample)
    t_common = make_common_grid(grids, n_points, t_min, t_max, range_mode)

    # Determine p from the first sample
    first = X_per_sample[0]
    if first.ndim == 1:
        p = 1
    else:
        p = first.shape[0]

    # Pre-allocate output: p features, each (n, n_points)
    result = [np.empty((n, n_points), dtype=np.float64) for _ in range(p)]

    for i in range(n):
        xi = X_per_sample[i]
        if xi.ndim == 1:
            xi = xi.reshape(1, -1)

        interpolated = interpolate_curve(
            grids[i], xi, t_common, method=method, extrapolate=extrapolate,
        )
        for j in range(p):
            result[j][i] = interpolated[j]

    return result, t_common


# ===================================================================
# Align Y response (same structure: per-sample grids)
# ===================================================================

def align_Y(
    Y_per_sample: List[NDArray],
    grids: List[NDArray],
    n_points: int = 100,
    t_min: Optional[float] = None,
    t_max: Optional[float] = None,
    range_mode: str = "intersection",
    method: str = "linear",
    extrapolate: str = "nearest",
) -> Tuple[NDArray, NDArray]:
    """Align Y response from per-sample grids to a common evenly spaced grid.

    Parameters
    ----------
    Y_per_sample : list of ndarray
        n arrays, each (m_i,) — one response curve per sample.
    grids : list of ndarray
        n arrays, each (m_i,) — the grid for sample i.
    n_points : int
        Common grid size.
    t_min, t_max : float, optional
        Override domain bounds.
    range_mode : str
        "intersection", "union", or "median".
    method : str
        Interpolation method.
    extrapolate : str
        Extrapolation mode.

    Returns
    -------
    Y_aligned : ndarray (n, n_points)
    t_common : ndarray (n_points,)
    """
    n = len(Y_per_sample)
    t_common = make_common_grid(grids, n_points, t_min, t_max, range_mode)
    Y_aligned = np.empty((n, n_points), dtype=np.float64)

    for i in range(n):
        Y_aligned[i] = interpolate_curve(
            grids[i], Y_per_sample[i], t_common,
            method=method, extrapolate=extrapolate,
        )

    return Y_aligned, t_common


# ===================================================================
# Combined alignment
# ===================================================================

def align_all(
    X_per_sample: List[NDArray],
    grids_X: List[NDArray],
    Y_per_sample: List[NDArray],
    grids_Y: List[NDArray],
    n_points_x: int = 100,
    n_points_y: Optional[int] = None,
    range_mode: str = "intersection",
    method: str = "linear",
) -> Tuple[List[NDArray], NDArray, NDArray, NDArray]:
    """Align X and Y from per-sample grids to common evenly spaced grids.

    X and Y may have different grids (even within the same sample)
    and get their own common grids.

    Parameters
    ----------
    X_per_sample : list of ndarray, each (p, m_i) or (m_i,)
    grids_X : list of ndarray, each (m_i,)
    Y_per_sample : list of ndarray, each (m_i_y,)
    grids_Y : list of ndarray, each (m_i_y,)
    n_points_x : int
    n_points_y : int or None (defaults to n_points_x)
    range_mode : str
    method : str

    Returns
    -------
    X_aligned : list of ndarray, each (n, n_points_x)
    t_x : ndarray (n_points_x,)
    Y_aligned : ndarray (n, n_points_y)
    t_y : ndarray (n_points_y,)
    """
    if n_points_y is None:
        n_points_y = n_points_x

    X_aligned, t_x = align_X(
        X_per_sample, grids_X, n_points_x,
        range_mode=range_mode, method=method,
    )
    Y_aligned, t_y = align_Y(
        Y_per_sample, grids_Y, n_points_y,
        range_mode=range_mode, method=method,
    )
    return X_aligned, t_x, Y_aligned, t_y


# ===================================================================
# Same-grid shortcut: X and Y share grids within each sample
# ===================================================================

def align_XY_same_grid(
    X_per_sample: List[NDArray],
    Y_per_sample: List[NDArray],
    grids: List[NDArray],
    n_points_x: int = 100,
    n_points_y: Optional[int] = None,
    range_mode: str = "intersection",
    method: str = "linear",
) -> Tuple[List[NDArray], NDArray, NDArray, NDArray]:
    """Align X and Y when both share the same per-sample grid.

    This is the common case: for sample i, all p features and the
    response are observed on the same grid t_i.

    Parameters
    ----------
    X_per_sample : list of ndarray, each (p, m_i) or (m_i,)
    Y_per_sample : list of ndarray, each (m_i,)
    grids : list of ndarray, each (m_i,)
    n_points_x : int
    n_points_y : int or None
    range_mode : str
    method : str

    Returns
    -------
    X_aligned : list of ndarray, each (n, n_points_x)
    t_x : ndarray (n_points_x,)
    Y_aligned : ndarray (n, n_points_y)
    t_y : ndarray (n_points_y,)

    Example
    -------
    >>> # 100 samples, 3 features, grid varies per sample
    >>> samples_X = []
    >>> samples_Y = []
    >>> grids = []
    >>> for _ in range(100):
    ...     m_i = np.random.randint(50, 150)
    ...     t_i = np.sort(np.random.uniform(0, 1, m_i))
    ...     grids.append(t_i)
    ...     samples_X.append(np.random.randn(3, m_i))  # 3 features
    ...     samples_Y.append(np.random.randn(m_i))
    >>> X_aligned, t_x, Y_aligned, t_y = align_XY_same_grid(
    ...     samples_X, samples_Y, grids, n_points_x=100,
    ... )
    """
    return align_all(
        X_per_sample, grids,
        Y_per_sample, grids,
        n_points_x, n_points_y,
        range_mode=range_mode, method=method,
    )


# ===================================================================
# Stack / unstack helpers for sklearn
# ===================================================================

def stack_features(X_list: List[NDArray]) -> NDArray:
    """Stack p aligned feature arrays into (n, p*m) for sklearn."""
    return np.hstack(X_list)


def unstack_features(X: NDArray, n_features: int) -> List[NDArray]:
    """Unstack (n, p*m) back into p arrays of (n, m)."""
    m = X.shape[1] // n_features
    return [X[:, j * m : (j + 1) * m] for j in range(n_features)]


# ===================================================================
# Diagnostics
# ===================================================================

def grid_summary(grids: List[NDArray]) -> dict:
    """Summary statistics of a collection of per-sample grids.

    Returns
    -------
    dict with keys: n_samples, lengths (min/median/max),
    range_min, range_max, intersection, union.
    """
    lengths = np.array([len(g) for g in grids])
    mins = np.array([g[0] for g in grids])
    maxs = np.array([g[-1] for g in grids])

    return {
        "n_samples": len(grids),
        "length_min": int(lengths.min()),
        "length_median": int(np.median(lengths)),
        "length_max": int(lengths.max()),
        "range_min": (float(mins.min()), float(maxs.min())),
        "range_max": (float(mins.max()), float(maxs.max())),
        "intersection": (float(mins.max()), float(maxs.min())),
        "union": (float(mins.min()), float(maxs.max())),
    }


# ===================================================================
# Demo
# ===================================================================

if __name__ == "__main__":
    np.random.seed(42)

    # --- Simulate: per-sample grids, 3 features --------------------------
    n = 80
    p = 3

    samples_X = []
    samples_Y = []
    grids = []

    for i in range(n):
        # Each sample has a different grid length and spacing
        m_i = np.random.randint(60, 150)
        # Slightly irregular grid with per-sample jitter
        t_start = np.random.uniform(-0.05, 0.05)
        t_end = np.random.uniform(0.95, 1.05)
        t_i = np.sort(np.random.uniform(t_start, t_end, m_i))
        grids.append(t_i)

        # 3 features on this grid, with NaN in feature 1
        x = np.array([
            np.sin(2 * np.pi * t_i + np.random.uniform(0, 2*np.pi)),
            np.cos(4 * np.pi * t_i + np.random.uniform(0, 2*np.pi)),
            0.5 * np.sin(np.pi * t_i) + 0.1 * np.random.randn(m_i),
        ])  # (3, m_i)

        # Inject NaN in feature 1
        nan_mask = np.random.rand(m_i) < 0.03
        x[0, nan_mask] = np.nan

        samples_X.append(x)
        samples_Y.append(0.5 * x[0] + 0.3 * x[1] + 0.1 * np.random.randn(m_i))

    # --- Grid summary ----------------------------------------------------
    summary = grid_summary(grids)
    print("Grid summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # --- Align to common grid --------------------------------------------
    X_aligned, t_x, Y_aligned, t_y = align_XY_same_grid(
        samples_X, samples_Y, grids, n_points_x=100,
    )

    print(f"\nAfter alignment:")
    print(f"  Features: {len(X_aligned)}, each {X_aligned[0].shape}")
    print(f"  t_x: [{t_x[0]:.4f}, {t_x[-1]:.4f}], {len(t_x)} points")
    print(f"  Y: {Y_aligned.shape}")
    print(f"  NaN in X: {sum(np.isnan(x).sum() for x in X_aligned)}")
    print(f"  NaN in Y: {np.isnan(Y_aligned).sum()}")

    # --- Stack for sklearn -----------------------------------------------
    X_stacked = stack_features(X_aligned)
    print(f"\n  Stacked X: {X_stacked.shape}  (ready for FunctionalPartialRegressor)")

    # --- Partial observation (60%) ---------------------------------------
    c_idx = int(0.6 * len(t_x))
    X_partial = stack_features([x[:, :c_idx] for x in X_aligned])
    print(f"  Partial X (60%): {X_partial.shape}")
