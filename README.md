# fdars – Functional Data Analysis for Python

[![CI](https://github.com/sipemu/pyfda/actions/workflows/ci.yml/badge.svg)](https://github.com/sipemu/pyfda/actions/workflows/ci.yml)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![Status: Experimental](https://img.shields.io/badge/status-experimental-orange)

High-performance Functional Data Analysis for Python, powered by a Rust backend ([fdars-core](https://github.com/sipemu/fdars)).

## The `Fdata` Class

The central object in fdars is `Fdata` — a functional data container that bundles
observation data, evaluation grid, identifiers, and metadata into a single object
(mirroring the R package's `fdata` class).

```python
import numpy as np
import pandas as pd
from fdars import Fdata

# Create functional data: 30 sine curves on [0, 1]
t = np.linspace(0, 1, 100)
X = np.array([np.sin(2 * np.pi * t + p) + np.random.normal(0, 0.1, 100)
              for p in np.random.uniform(0, np.pi, 30)])

# Attach metadata as a pandas DataFrame
meta = pd.DataFrame({"group": ["A"] * 15 + ["B"] * 15,
                      "score": np.random.randn(30)})
fd = Fdata(X, argvals=t, metadata=meta)
fd
# Fdata (1D)  –  30 obs × 100 points  –  range [0.0, 1.0]  –  metadata: group, score

# Subset — metadata DataFrame and IDs are preserved
fd_sub = fd[0:10]
fd_sub.metadata  # DataFrame with 10 rows

# Methods delegate to the Rust backend
mu = fd.mean()                    # pointwise mean
fd_c = fd.center()                # centered Fdata
d1 = fd.deriv(nderiv=1)           # first derivative (returns Fdata)
norms = fd.norm(p=2.0)            # L2 norms per curve
depths = fd.depth("fraiman_muniz") # depth values
D = fd.distance(method="lp")      # self-distance matrix

# 2D surfaces work the same way
surfaces = np.random.randn(5, 8, 10)       # 5 surfaces on 8×10 grid
fd2d = Fdata(surfaces, argvals=(np.arange(8), np.arange(10)))
```

You can still call low-level functions directly with raw NumPy arrays:

```python
from fdars.depth import fraiman_muniz_1d
from fdars.metric import lp_self_1d
from fdars.clustering import kmeans_fd

depths = fraiman_muniz_1d(X, X)
D = lp_self_1d(X, t, p=2.0)
result = kmeans_fd(X, t, k=3, seed=42)
```

## Modules

| Module | Description |
|---|---|
| `fdars.Fdata` | Functional data container (1D curves, 2D surfaces) with metadata |
| `fdars.fdata` | Low-level functional data operations (mean, derivatives, norms, centering) |
| `fdars.depth` | Depth functions (Fraiman-Muniz, modal, band, random projection, …) |
| `fdars.metric` | Distance metrics (Lp, Hausdorff, DTW, soft-DTW, Fourier, h-shift) |
| `fdars.basis` | Basis representations (B-splines, P-splines, Fourier) |
| `fdars.smoothing` | Nonparametric smoothing (Nadaraya-Watson, local polynomial, k-NN) |
| `fdars.clustering` | Clustering (k-means, fuzzy c-means, GMM) |
| `fdars.regression` | Regression (FPC linear, PLS, nonparametric, robust, FOSR, FANOVA) |
| `fdars.alignment` | Elastic alignment (SRSF, Karcher mean, elastic FPCA) |
| `fdars.outliers` | Outlier detection (LRT, outliergram, magnitude-shape) |
| `fdars.seasonal` | Seasonal analysis (SAZED, autoperiod, STL, peak detection) |
| `fdars.spm` | Statistical process monitoring (Phase I/II, EWMA, CUSUM) |
| `fdars.classification` | Classification (LDA, QDA, k-NN, kernel with cross-validation) |
| `fdars.tolerance` | Tolerance bands (FPCA, conformal, Degras SCB) |
| `fdars.conformal` | Conformal prediction (split, jackknife+) |
| `fdars.simulation` | Simulation (Karhunen-Loève, Gaussian processes) |
| `fdars.explain` | Explainability (SHAP, PDP, permutation importance, significant regions) |

## Quick Start

```sh
git clone https://github.com/sipemu/pyfda.git
cd pyfda
python -m venv .venv && source .venv/bin/activate
pip install maturin numpy
maturin develop --release
```

The package exposes 16 submodules wrapping 130+ functions with zero-copy NumPy conversion. Requires Python >= 3.9.

**[Documentation](https://sipemu.github.io/pyfda/)**

## Development

```sh
# Install dev dependencies
pip install maturin numpy pytest matplotlib

# Build in development mode
maturin develop

# Run tests
pytest tests/

# Build documentation
pip install mkdocs-material
mkdocs serve
```

## MSRV

The minimum supported Rust version is **1.83**.

## License

MIT — see [LICENSE](LICENSE).
