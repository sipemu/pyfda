# pyfda – Functional Data Analysis for Python

[![CI](https://github.com/sipemu/pyfda/actions/workflows/ci.yml/badge.svg)](https://github.com/sipemu/pyfda/actions/workflows/ci.yml)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![Status: Experimental](https://img.shields.io/badge/status-experimental-orange)

High-performance Functional Data Analysis for Python, powered by a Rust backend ([fdars-core](https://github.com/sipemu/fdars)).

## Modules

| Module | Description |
|---|---|
| `pyfda.fdata` | Functional data operations (mean, derivatives, norms, centering) |
| `pyfda.depth` | Depth functions (Fraiman-Muniz, modal, band, random projection, …) |
| `pyfda.metric` | Distance metrics (Lp, Hausdorff, DTW, soft-DTW, Fourier, h-shift) |
| `pyfda.basis` | Basis representations (B-splines, P-splines, Fourier) |
| `pyfda.smoothing` | Nonparametric smoothing (Nadaraya-Watson, local polynomial, k-NN) |
| `pyfda.clustering` | Clustering (k-means, fuzzy c-means, GMM) |
| `pyfda.regression` | Regression (FPC linear, PLS, nonparametric, robust, FOSR, FANOVA) |
| `pyfda.alignment` | Elastic alignment (SRSF, Karcher mean, elastic FPCA) |
| `pyfda.outliers` | Outlier detection (LRT, outliergram, magnitude-shape) |
| `pyfda.seasonal` | Seasonal analysis (SAZED, autoperiod, STL, peak detection) |
| `pyfda.spm` | Statistical process monitoring (Phase I/II, EWMA, CUSUM) |
| `pyfda.classification` | Classification (LDA, QDA, k-NN, kernel with cross-validation) |
| `pyfda.tolerance` | Tolerance bands (FPCA, conformal, Degras SCB) |
| `pyfda.conformal` | Conformal prediction (split, jackknife+) |
| `pyfda.simulation` | Simulation (Karhunen-Loève, Gaussian processes) |
| `pyfda.explain` | Explainability (SHAP, PDP, permutation importance, significant regions) |

## Quick Start

### Installation

```sh
git clone https://github.com/sipemu/pyfda.git
cd pyfda
python -m venv .venv && source .venv/bin/activate
pip install maturin numpy
maturin develop --release
```

### Usage

```python
import numpy as np
import pyfda

# Create functional data: 30 curves on [0, 1]
t = np.linspace(0, 1, 100)
X = np.array([np.sin(2 * np.pi * t + p) + np.random.normal(0, 0.1, 100)
              for p in np.random.uniform(0, np.pi, 30)])

# Functional mean and derivatives
from pyfda.fdata import mean_1d, deriv_1d
mu = mean_1d(X, t)
dX = deriv_1d(X, t, nderiv=1)

# Depth measures
from pyfda.depth import fraiman_muniz_1d, band_1d
depths_fm = fraiman_muniz_1d(X, t)
depths_band = band_1d(X, t)

# Distance matrix (L2)
from pyfda.metric import lp_self_1d
D = lp_self_1d(X, t, p=2.0)

# Clustering
from pyfda.clustering import kmeans_1d
result = kmeans_1d(X, t, n_clusters=2, seed=42)

# Smoothing
from pyfda.smoothing import nadaraya_watson_1d
X_smooth = nadaraya_watson_1d(X, t, bandwidth=0.05)

# Simulation
from pyfda.simulation import simulate_kl
curves = simulate_kl(n_obs=50, n_points=100, n_basis=5, seed=123)
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

The minimum supported Rust version is **1.81**.

## License

MIT — see [LICENSE](LICENSE).
