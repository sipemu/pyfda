---
title: fdars - Functional Data Analysis for Python
---

<div style="text-align: center; margin-bottom: 1.5rem;">
<h1 style="margin-bottom: 0.3rem;">fdars</h1>
<p style="font-size: 1.15rem; color: var(--md-default-fg-color--light);">
High-performance Functional Data Analysis for Python, powered by Rust
</p>
</div>

[![PyPI](https://img.shields.io/pypi/v/fdars)](https://pypi.org/project/fdars)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/sipemu/pyfda/actions/workflows/ci.yml/badge.svg)](https://github.com/sipemu/pyfda/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

**fdars** is a high-performance Python toolkit for functional data analysis powered
by a Rust backend. Treat entire curves, spectra, and trajectories as single
observations -- then smooth, align, decompose, and analyze them.

Built on [fdars-core](https://github.com/sipemu/fdars), the same engine that
drives the [fdars R package](https://github.com/sipemu/fdars), fdars gives you
native-speed computation with a familiar NumPy interface.

---

## The `Fdata` Class

The central object in fdars is **`Fdata`** -- a functional data container that
bundles observation data, evaluation grid, identifiers, and per-observation
metadata into a single object (mirroring the R package's `fdata` class).

```python
import numpy as np
import pandas as pd
from fdars import Fdata

# Create functional data from a (n_obs, n_points) array + grid
t = np.linspace(0, 1, 100)
X = np.random.randn(30, 100)

# Attach metadata as a pandas DataFrame
meta = pd.DataFrame({
    "group": ["control"] * 15 + ["treatment"] * 15,
    "age": np.random.randint(20, 60, 30),
})
fd = Fdata(X, argvals=t, metadata=meta)
fd
# Fdata (1D)  –  30 obs × 100 points  –  range [0.0, 1.0]  –  metadata: group, age

# Methods delegate to the Rust backend
mu = fd.mean()                     # pointwise mean
fd_c = fd.center()                 # centered Fdata
d1 = fd.deriv(nderiv=1)            # first derivative (returns Fdata)
norms = fd.norm(p=2.0)             # L2 norms per curve
depths = fd.depth("fraiman_muniz") # depth values
D = fd.distance(method="lp")       # self-distance matrix

# Subset -- metadata DataFrame and IDs are preserved
fd_sub = fd[0:10]
fd_sub.metadata  # DataFrame with 10 rows
```

See the [Fdata reference](reference/fdata.md) and
[Introduction](learn/introduction.md) for a full walkthrough.

---

<!-- ===== Learn ===== -->
<div class="fdars-section-heading fdars-learn">Learn</div>
<p class="fdars-section-desc">Tutorials and guides to get started with functional data analysis in Python.</p>

<div class="fdars-gallery">
<a class="fdars-gallery-item" href="learn/introduction/">
<div class="fdars-gallery-title">Introduction to fdars</div>
<div class="fdars-gallery-desc">What is FDA? Core concepts, data layout, and your first analysis with fdars.</div>
</a>
<a class="fdars-gallery-item" href="learn/simulation/">
<div class="fdars-gallery-title">Simulation Toolbox</div>
<div class="fdars-gallery-desc">Generate synthetic curves with Karhunen-Loeve expansions and Gaussian processes.</div>
</a>
<a class="fdars-gallery-item" href="learn/smoothing/">
<div class="fdars-gallery-title">Smoothing</div>
<div class="fdars-gallery-desc">Nadaraya-Watson, local polynomial, k-NN, and basis smoothing with automatic bandwidth selection.</div>
</a>
<a class="fdars-gallery-item" href="learn/derivatives/">
<div class="fdars-gallery-title">Working with Derivatives</div>
<div class="fdars-gallery-desc">Compute first, second, and higher-order derivatives of functional data.</div>
</a>
</div>

<!-- ===== Represent ===== -->
<div class="fdars-section-heading fdars-represent">Represent</div>
<p class="fdars-section-desc">Basis expansions, dimensionality reduction, depth, and distances for functional data.</p>

<div class="fdars-gallery">
<a class="fdars-gallery-item" href="represent/fpca/">
<div class="fdars-gallery-title">Functional PCA</div>
<div class="fdars-gallery-desc">Extract dominant modes of variation with weighted FPCA.</div>
</a>
<a class="fdars-gallery-item" href="represent/basis-representation/">
<div class="fdars-gallery-title">Basis Representation</div>
<div class="fdars-gallery-desc">B-spline, Fourier, and P-spline basis expansions with automatic selection.</div>
</a>
<a class="fdars-gallery-item" href="represent/depth-functions/">
<div class="fdars-gallery-title">Depth Functions</div>
<div class="fdars-gallery-desc">Fraiman-Muniz, band, modal, random projection, Tukey, and spatial depth.</div>
</a>
<a class="fdars-gallery-item" href="represent/distance-metrics/">
<div class="fdars-gallery-title">Distance Metrics</div>
<div class="fdars-gallery-desc">Lp, Hausdorff, DTW, Soft-DTW, Fourier, and horizontal-shift distances.</div>
</a>
</div>

<!-- ===== Align ===== -->
<div class="fdars-section-heading fdars-align">Align</div>
<p class="fdars-section-desc">Curve registration and elastic alignment methods.</p>

<div class="fdars-gallery">
<a class="fdars-gallery-item" href="align/elastic-alignment/">
<div class="fdars-gallery-title">Elastic Alignment</div>
<div class="fdars-gallery-desc">SRSF-based alignment, Karcher mean, and elastic FPCA.</div>
</a>
<a class="fdars-gallery-item" href="align/shape-analysis/">
<div class="fdars-gallery-title">Shape Analysis</div>
<div class="fdars-gallery-desc">Shape-preserving registration and geodesic computations.</div>
</a>
</div>

<!-- ===== Regression ===== -->
<div class="fdars-section-heading fdars-regression">Regression</div>
<p class="fdars-section-desc">Functional regression, classification, and prediction.</p>

<div class="fdars-gallery">
<a class="fdars-gallery-item" href="regression/scalar-on-function/">
<div class="fdars-gallery-title">Scalar-on-Function</div>
<div class="fdars-gallery-desc">FPC linear, PLS, and nonparametric regression with a scalar response.</div>
</a>
<a class="fdars-gallery-item" href="regression/function-on-scalar/">
<div class="fdars-gallery-title">Function-on-Scalar</div>
<div class="fdars-gallery-desc">FOSR and FANOVA for predicting functional responses.</div>
</a>
<a class="fdars-gallery-item" href="regression/classification/">
<div class="fdars-gallery-title">Classification</div>
<div class="fdars-gallery-desc">LDA, QDA, k-NN, and kernel classifiers with cross-validation.</div>
</a>
<a class="fdars-gallery-item" href="regression/elastic-regression/">
<div class="fdars-gallery-title">Elastic Regression</div>
<div class="fdars-gallery-desc">Regression models in the SRSF space for phase-invariant prediction.</div>
</a>
<a class="fdars-gallery-item" href="regression/explainability/">
<div class="fdars-gallery-title">Explainability</div>
<div class="fdars-gallery-desc">SHAP, PDP, permutation importance, and significant region detection.</div>
</a>
<a class="fdars-gallery-item" href="regression/conformal-prediction/">
<div class="fdars-gallery-title">Conformal Prediction</div>
<div class="fdars-gallery-desc">Distribution-free prediction intervals with split conformal and jackknife+.</div>
</a>
<a class="fdars-gallery-item" href="regression/robust-regression/">
<div class="fdars-gallery-title">Robust Regression</div>
<div class="fdars-gallery-desc">Depth-weighted and trimmed regression resistant to outliers.</div>
</a>
</div>

<!-- ===== Monitoring ===== -->
<div class="fdars-section-heading fdars-monitoring">Monitoring</div>
<p class="fdars-section-desc">Statistical process monitoring for functional profiles.</p>

<div class="fdars-gallery">
<a class="fdars-gallery-item" href="monitoring/spm/">
<div class="fdars-gallery-title">Process Monitoring</div>
<div class="fdars-gallery-desc">Phase I/II control charts, EWMA, CUSUM for functional quality profiles.</div>
</a>
</div>

<!-- ===== Analyze ===== -->
<div class="fdars-section-heading fdars-analyze">Analyze</div>
<p class="fdars-section-desc">Clustering, outlier detection, tolerance bands, and seasonal decomposition.</p>

<div class="fdars-gallery">
<a class="fdars-gallery-item" href="analyze/clustering/">
<div class="fdars-gallery-title">Clustering</div>
<div class="fdars-gallery-desc">K-means, fuzzy c-means, and GMM clustering for functional data.</div>
</a>
<a class="fdars-gallery-item" href="analyze/outlier-detection/">
<div class="fdars-gallery-title">Outlier Detection</div>
<div class="fdars-gallery-desc">LRT, outliergram, and magnitude-shape methods for anomaly detection.</div>
</a>
<a class="fdars-gallery-item" href="analyze/tolerance-bands/">
<div class="fdars-gallery-title">Tolerance Bands</div>
<div class="fdars-gallery-desc">FPCA-based tolerance bands, conformal bands, and Degras SCBs.</div>
</a>
<a class="fdars-gallery-item" href="analyze/seasonal-analysis/">
<div class="fdars-gallery-title">Seasonal Analysis</div>
<div class="fdars-gallery-desc">SAZED, autoperiod, STL, and peak detection for periodic functional data.</div>
</a>
<a class="fdars-gallery-item" href="analyze/equivalence-testing/">
<div class="fdars-gallery-title">Equivalence Testing</div>
<div class="fdars-gallery-desc">TOST-based equivalence tests for functional means.</div>
</a>
<a class="fdars-gallery-item" href="analyze/covariance-functions/">
<div class="fdars-gallery-title">Covariance Functions</div>
<div class="fdars-gallery-desc">Gaussian, exponential, Matern, and periodic covariance kernels.</div>
</a>
</div>

---

## Installation

```bash
pip install fdars
```

fdars ships pre-built wheels for Linux, macOS, and Windows on Python 3.9+.
The only runtime dependency is **NumPy**.

!!! tip "Development install"
    To build from source (requires a Rust toolchain):
    ```bash
    git clone https://github.com/sipemu/pyfda.git
    cd fdars
    pip install maturin
    maturin develop --release
    ```

---

## Quick Example

A minimal end-to-end workflow: create an `Fdata` object, compute depth
rankings, and cluster.

```python
import numpy as np
import pandas as pd
from fdars import Fdata
from fdars.simulation import simulate
from fdars.clustering import kmeans_fd

# 1. Simulate 60 curves on a regular grid
argvals = np.linspace(0, 1, 100)
data = simulate(n=60, argvals=argvals, n_basis=7, seed=42)

# 2. Wrap in an Fdata object with metadata
meta = pd.DataFrame({"batch": np.repeat(["A", "B", "C"], 20)})
fd = Fdata(data, argvals=argvals, metadata=meta)
print(fd)
# Fdata (1D)  –  60 obs × 100 points  –  range [0.0, 1.0]  –  metadata: batch

# 3. Rank curves by Fraiman-Muniz depth
depths = fd.depth("fraiman_muniz")
deepest = np.argmax(depths)
print(f"Most central curve: {deepest}, depth = {depths[deepest]:.4f}")

# 4. Center the data
fd_c = fd.center()     # returns Fdata with metadata preserved

# 5. Cluster into 3 groups
result = kmeans_fd(fd.data, fd.argvals, k=3, seed=0)
print(f"Cluster sizes: {np.bincount(result['cluster'])}")
```

!!! info "Rust under the hood"
    Every method call on `Fdata` crosses into compiled Rust code via
    [PyO3](https://pyo3.rs).  There is no Python loop over the 60
    curves -- the entire computation runs at native speed with
    multithreaded parallelism where applicable.

---

## Package Modules

| Module | Description |
|--------|-------------|
| [`fdars.Fdata`](reference/fdata.md) | **Functional data container** — the main entry point (1D curves, 2D surfaces, metadata) |
| `fdars.fdata` | Low-level functional data operations: mean, center, derivatives, norms, normalization |
| `fdars.depth` | Fraiman-Muniz, modal, band, random projection, Tukey, spatial depth |
| `fdars.metric` | Lp, Hausdorff, DTW, Soft-DTW, Fourier, horizontal-shift |
| `fdars.basis` | B-spline, Fourier, P-spline basis operations |
| `fdars.smoothing` | Nadaraya-Watson, local polynomial, k-NN, bandwidth CV |
| `fdars.clustering` | K-means, fuzzy c-means, GMM |
| `fdars.regression` | FPCA, PLS, nonparametric, robust, FOSR, FANOVA |
| `fdars.alignment` | SRSF alignment, Karcher mean, elastic FPCA |
| `fdars.outliers` | LRT, outliergram, magnitude-shape |
| `fdars.seasonal` | SAZED, autoperiod, STL, peak detection |
| `fdars.spm` | Phase I/II, EWMA, CUSUM process monitoring |
| `fdars.classification` | LDA, QDA, k-NN, kernel classifiers |
| `fdars.tolerance` | FPCA, conformal, Degras tolerance/confidence bands |
| `fdars.conformal` | Split conformal, jackknife+ prediction |
| `fdars.simulation` | Karhunen-Loeve simulation, Gaussian processes |
| `fdars.explain` | SHAP, PDP, permutation importance, significant regions |
