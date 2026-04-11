---
title: Introduction to pyfda
---

# Introduction to pyfda

This guide introduces **Functional Data Analysis (FDA)** and shows you how to
use pyfda's Python API to perform common tasks. By the end, you will understand
the data layout, core operations, and the breadth of functionality available.

---

## What Is Functional Data Analysis?

In classical statistics every observation is a number or a vector.
In **functional data analysis** every observation is an *entire function* --
a curve, a spectrum, a trajectory, or a surface measured over a continuum.

Examples of functional data appear everywhere:

- **Spectroscopy** -- absorbance spectra measured at hundreds of wavelengths
- **Growth curves** -- height-over-age profiles for a cohort of children
- **Finance** -- intraday price trajectories
- **Environmental science** -- daily temperature profiles across weather stations
- **Manufacturing** -- quality profiles recorded along a production line

The key insight of FDA is that these are not just high-dimensional vectors; they
have a *smoothness structure* that can be exploited for better estimation,
prediction, and interpretation.

!!! note "Infinite-dimensional observations"
    Mathematically, each observation lives in a function space such as
    $L^2([0, 1])$.  In practice we observe each function on a discrete grid,
    but FDA methods respect the underlying continuity.

---

## The pyfda Package

**pyfda** provides a comprehensive set of FDA methods implemented in Rust
(via [fdars-core](https://github.com/sipemu/fdars)) and exposed to Python
through [PyO3](https://pyo3.rs).  This gives you:

- **Native speed** -- all heavy computation runs in compiled Rust with
  multithreading, not in Python loops.
- **NumPy interface** -- input and output are ordinary `numpy.ndarray` objects.
  No wrapper classes to learn.
- **Broad coverage** -- depth, distance, smoothing, basis representation, FPCA,
  regression, clustering, alignment, outlier detection, monitoring, and more.

### Installation

```bash
pip install pyfda
```

The only runtime dependency is **NumPy**.

---

## Getting Started

### Data Layout

pyfda expects functional data as a **2D NumPy array** of shape
`(n_obs, n_points)`, where:

- `n_obs` is the number of curves (observations),
- `n_points` is the number of grid points at which each curve is evaluated.

A separate 1D array `argvals` of length `n_points` holds the evaluation grid
(e.g., time stamps or wavelengths).

```python
import numpy as np

# 50 curves observed at 200 equally spaced points on [0, 1]
n_obs = 50
n_points = 200
argvals = np.linspace(0, 1, n_points)

# For demonstration, create sine curves with random phase shifts
rng = np.random.default_rng(0)
phases = rng.uniform(0, 2 * np.pi, size=n_obs)
data = np.array([np.sin(2 * np.pi * argvals + phi) for phi in phases])
print(data.shape)  # (50, 200)
```

!!! info "Row = observation, Column = grid point"
    This is the same convention used by scikit-learn for tabular data, making
    it easy to mix functional and scalar analyses.

### Simulating Data

For reproducible experiments, use the built-in simulation module instead of
hand-crafting arrays:

```python
from pyfda.simulation import simulate

argvals = np.linspace(0, 1, 100)
data = simulate(n=50, argvals=argvals, n_basis=5, seed=42)
print(data.shape)  # (50, 100)
```

See the [Simulation Toolbox](simulation.md) guide for details on eigenfunction
types, eigenvalue decays, and Gaussian process generation.

---

## Core Operations

The `pyfda.fdata` module provides fundamental operations that work directly on
the `(n_obs, n_points)` data matrix.

### Pointwise Mean

```python
from pyfda.fdata import mean_1d

mu = mean_1d(data)
print(mu.shape)  # (100,) -- one value per grid point
```

The result is the pointwise average across all 50 curves.

### Centering

```python
from pyfda.fdata import center_1d

centered = center_1d(data)
print(centered.shape)  # (50, 100) -- same shape, mean subtracted
```

After centering, `mean_1d(centered)` is numerically zero at every grid point.

### Norms

Compute the $L^p$ norm of each curve:

$$
\|x_i\|_p = \left( \int_0^1 |x_i(t)|^p \, dt \right)^{1/p}
$$

```python
from pyfda.fdata import norm_lp_1d

l2_norms = norm_lp_1d(data, argvals, p=2.0)
print(l2_norms.shape)  # (50,) -- one norm per curve
print(f"Mean L2 norm: {l2_norms.mean():.4f}")
```

### Normalization

```python
from pyfda.fdata import normalize

# Center and scale each grid point (like sklearn's StandardScaler)
data_scaled = normalize(data, method="autoscale")

# Or normalize each curve individually
data_curve = normalize(data, method="curve_standardize")
```

Available methods: `"center"`, `"autoscale"`, `"pareto"`, `"range"`,
`"curve_center"`, `"curve_standardize"`, `"curve_range"`.

---

## Key Functionality Overview

### Depth

Depth measures quantify how "central" a curve is within a sample. Deeper curves
are more typical; shallow curves are potential outliers.

```python
from pyfda.depth import fraiman_muniz_1d, modified_band_1d

# Fraiman-Muniz depth
fm_depth = fraiman_muniz_1d(data, data)
print(f"Most central curve index: {np.argmax(fm_depth)}")

# Modified band depth
mbd = modified_band_1d(data, data)
```

Other depth functions available: `modal_1d`, `band_1d`, `random_projection_1d`,
`random_tukey_1d`, `functional_spatial_1d`, `kernel_functional_spatial_1d`, and
their 2D counterparts.

### Distance Metrics

```python
from pyfda.metric import lp_self_1d, dtw_self_1d

# L2 distance matrix
dist_l2 = lp_self_1d(data, argvals, p=2.0)
print(dist_l2.shape)  # (50, 50)

# DTW distance matrix
dist_dtw = dtw_self_1d(data, p=2.0)
print(dist_dtw.shape)  # (50, 50)
```

See also: `hausdorff_self_1d`, `soft_dtw_self_1d`, `fourier_self_1d`,
`hshift_self_1d`, and cross-distance variants.

### Regression and FPCA

```python
from pyfda.regression import fpca

result = fpca(data, argvals, n_comp=3)
scores = result["scores"]        # (50, 3)
rotation = result["rotation"]    # (100, 3) -- eigenfunctions
print(f"Variance explained by PC1: singular_value = {result['singular_values'][0]:.4f}")
```

### Clustering

```python
from pyfda.clustering import kmeans_fd

clusters = kmeans_fd(data, argvals, k=3, seed=0)
print(f"Cluster labels: {clusters['cluster']}")
print(f"Total within-cluster SS: {clusters['tot_withinss']:.4f}")
```

### Outlier Detection

```python
from pyfda.outliers import outliergram

og = outliergram(data)
n_outliers = og["outliers"].sum()
print(f"Detected {n_outliers} outlier(s)")
```

### Smoothing

```python
from pyfda.smoothing import nadaraya_watson, optim_bandwidth

# Pick one noisy curve
x = argvals
y = data[0] + np.random.default_rng(0).normal(0, 0.1, size=len(x))

# Find optimal bandwidth via GCV
bw = optim_bandwidth(x, y)
print(f"Optimal bandwidth: {bw['h_opt']:.4f}")

# Smooth with Nadaraya-Watson
y_hat = nadaraya_watson(x, y, x, bandwidth=bw["h_opt"])
```

---

## Performance Notes

pyfda compiles all FDA algorithms to native machine code via Rust. Key
performance characteristics:

- **No GIL contention** -- Rust computations release the Python GIL, so they
  can run alongside other Python threads.
- **Parallelism** -- distance matrices, depth calculations, and other
  embarrassingly parallel tasks use Rayon for automatic multithreading.
- **Zero-copy where possible** -- NumPy arrays are passed directly to Rust
  without copying when memory layouts are compatible.
- **Small overhead** -- the Python/Rust boundary crossing adds only
  microseconds per call, so even small problems benefit.

!!! tip "Benchmarks"
    On a dataset of 500 curves with 1000 grid points, pyfda computes the full
    $500 \times 500$ L2 distance matrix in milliseconds -- orders of magnitude
    faster than a pure-Python double loop.

---

## Next Steps

- [Simulation Toolbox](simulation.md) -- learn how to generate realistic
  synthetic data for experiments and benchmarks.
- [Smoothing](smoothing.md) -- remove noise while preserving shape.
- [Working with Derivatives](derivatives.md) -- extract velocity and
  acceleration from functional observations.
- [Depth Functions](../represent/depth-functions.md) -- deep dive into
  centrality measures.
- [Clustering](../analyze/clustering.md) -- group curves by shape.
- [FPCA](../represent/fpca.md) -- dimensionality reduction for curves.
