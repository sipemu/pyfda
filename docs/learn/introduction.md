---
title: Introduction to fdars
---

# Introduction to fdars

This guide introduces **Functional Data Analysis (FDA)** and shows you how to
use fdars's Python API to perform common tasks. By the end, you will understand
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

## The fdars Package

**fdars** provides a comprehensive set of FDA methods implemented in Rust
(via [fdars-core](https://github.com/sipemu/fdars)) and exposed to Python
through [PyO3](https://pyo3.rs).  This gives you:

- **Native speed** -- all heavy computation runs in compiled Rust with
  multithreading, not in Python loops.
- **`Fdata` class** -- a functional data container that bundles data, grid,
  IDs, and metadata into a single object (mirroring the R package's `fdata`).
- **NumPy interface** -- you can also work directly with `numpy.ndarray` for
  full control.
- **Broad coverage** -- depth, distance, smoothing, basis representation, FPCA,
  regression, clustering, alignment, outlier detection, monitoring, and more.

### Installation

```bash
pip install fdars
```

The only runtime dependency is **NumPy**.

---

## Getting Started

### The `Fdata` Class

The central object in fdars is **`Fdata`** -- a functional data container that
bundles observation data, evaluation grid, identifiers, and per-observation
metadata.  It mirrors the R package's `fdata` S3 class.

```python
import numpy as np
import pandas as pd
from fdars import Fdata

# 50 curves observed at 200 equally spaced points on [0, 1]
n_obs = 50
n_points = 200
argvals = np.linspace(0, 1, n_points)

# Create sine curves with random phase shifts
rng = np.random.default_rng(0)
phases = rng.uniform(0, 2 * np.pi, size=n_obs)
X = np.array([np.sin(2 * np.pi * argvals + phi) for phi in phases])

# Wrap in an Fdata object
fd = Fdata(X, argvals=argvals)
print(fd)
# Fdata (1D)  –  50 obs × 200 points  –  range [0.0, 1.0]
```

#### With Identifiers and Metadata

You can attach identifiers and a `pandas.DataFrame` of per-observation
covariates:

```python
meta = pd.DataFrame({
    "group": ["control"] * 25 + ["treatment"] * 25,
    "age": rng.integers(20, 60, size=n_obs),
})
fd = Fdata(
    X, argvals=argvals,
    id=[f"patient_{i}" for i in range(n_obs)],
    metadata=meta,
)
print(fd)
# Fdata (1D)  –  50 obs × 200 points  –  range [0.0, 1.0]  –  metadata: group, age

# Access metadata columns directly
fd.metadata["group"].value_counts()
```

Metadata is preserved when subsetting:

```python
fd_sub = fd[0:10]
print(fd_sub.id[:3])               # ['patient_0', 'patient_1', 'patient_2']
print(fd_sub.metadata["group"][:3]) # 'control', 'control', 'control'
```

!!! info "Row = observation, Column = grid point"
    The underlying `fd.data` array has shape `(n_obs, n_points)` -- the same
    convention used by scikit-learn, making it easy to mix functional and scalar
    analyses.

### Simulating Data

For reproducible experiments, use the built-in simulation module:

```python
from fdars.simulation import simulate

argvals = np.linspace(0, 1, 100)
data = simulate(n=50, argvals=argvals, n_basis=5, seed=42)

fd = Fdata(data, argvals=argvals)
print(fd)  # Fdata (1D)  –  50 obs × 100 points  –  range [0.0, 1.0]

# All examples below use this fd object
```

See the [Simulation Toolbox](simulation.md) guide for details on eigenfunction
types, eigenvalue decays, and Gaussian process generation.

---

## Core Operations

`Fdata` methods delegate to the Rust backend. They return either numpy arrays
(for scalar results) or new `Fdata` objects (for transformed functional data),
preserving metadata.

### Pointwise Mean

```python
mu = fd.mean()
print(mu.shape)  # (100,) -- one value per grid point
```

### Centering

```python
fd_centered = fd.center()
print(fd_centered.shape)  # (50, 100) -- same shape, mean subtracted
print(fd_centered.id[:3])  # metadata preserved
```

After centering, the mean is numerically zero at every grid point.

### Norms

Compute the $L^p$ norm of each curve:

$$
\|x_i\|_p = \left( \int_0^1 |x_i(t)|^p \, dt \right)^{1/p}
$$

```python
l2_norms = fd.norm(p=2.0)
print(l2_norms.shape)  # (50,) -- one norm per curve
print(f"Mean L2 norm: {l2_norms.mean():.4f}")
```

### Normalization

```python
# Center and scale each grid point (like sklearn's StandardScaler)
fd_scaled = fd.normalize("autoscale")

# Or normalize each curve individually
fd_curve = fd.normalize("curve_standardize")
```

Available methods: `"center"`, `"autoscale"`, `"pareto"`, `"range"`,
`"curve_center"`, `"curve_standardize"`, `"curve_range"`.

---

## Key Functionality Overview

### Depth

Depth measures quantify how "central" a curve is within a sample. Deeper curves
are more typical; shallow curves are potential outliers.

```python
# Via Fdata convenience method
fm_depth = fd.depth("fraiman_muniz")
print(f"Most central curve index: {np.argmax(fm_depth)}")

# Or via low-level functions
from fdars.depth import modified_band_1d
mbd = modified_band_1d(fd.data, fd.data)
```

Other depth functions available: `modal`, `band`, `random_projection`,
`random_tukey`, `functional_spatial`, `kernel_functional_spatial`, and
their 2D counterparts.

### Distance Metrics

```python
# Via Fdata convenience method
dist_l2 = fd.distance(method="lp", p=2.0)
print(dist_l2.shape)  # (50, 50)

# Or via low-level functions
from fdars.metric import dtw_self_1d
dist_dtw = dtw_self_1d(fd.data, p=2.0)
print(dist_dtw.shape)  # (50, 50)
```

See also: `hausdorff`, `soft_dtw`, `fourier`, `hshift`, and cross-distance
variants.

### Regression and FPCA

```python
from fdars.regression import fpca

result = fpca(fd.data, fd.argvals, n_comp=3)
scores = result["scores"]        # (50, 3)
rotation = result["rotation"]    # (100, 3) -- eigenfunctions
print(f"Variance explained by PC1: singular_value = {result['singular_values'][0]:.4f}")
```

### Clustering

```python
from fdars.clustering import kmeans_fd

clusters = kmeans_fd(fd.data, fd.argvals, k=3, seed=0)
print(f"Cluster labels: {clusters['cluster']}")
print(f"Total within-cluster SS: {clusters['tot_withinss']:.4f}")
```

### Outlier Detection

```python
from fdars.outliers import outliergram

og = outliergram(fd.data)
n_outliers = og["outliers"].sum()
print(f"Detected {n_outliers} outlier(s)")
```

### Smoothing

```python
from fdars.smoothing import nadaraya_watson, optim_bandwidth

# Pick one noisy curve
x = fd.argvals
y = fd.data[0] + np.random.default_rng(0).normal(0, 0.1, size=len(x))

# Find optimal bandwidth via GCV
bw = optim_bandwidth(x, y)
print(f"Optimal bandwidth: {bw['h_opt']:.4f}")

# Smooth with Nadaraya-Watson
y_hat = nadaraya_watson(x, y, x, bandwidth=bw["h_opt"])
```

---

## Performance Notes

fdars compiles all FDA algorithms to native machine code via Rust. Key
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
    On a dataset of 500 curves with 1000 grid points, fdars computes the full
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
