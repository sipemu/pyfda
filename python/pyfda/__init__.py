"""pyfda – Functional Data Analysis for Python, powered by Rust.

High-performance functional data analysis toolkit providing:
- Functional data operations (mean, derivatives, norms)
- Depth measures (Fraiman-Muniz, modal, band, random projection, etc.)
- Distance metrics (Lp, Hausdorff, DTW, elastic, Fourier)
- Basis representations (B-splines, P-splines, Fourier)
- Nonparametric smoothing (Nadaraya-Watson, local polynomial, k-NN)
- Clustering (k-means, fuzzy c-means, GMM)
- Regression (FPC linear, PLS, nonparametric, robust, FOSR, FANOVA)
- Elastic alignment (SRSF, Karcher mean, elastic FPCA)
- Outlier detection (LRT, outliergram, magnitude-shape)
- Seasonal analysis (SAZED, autoperiod, STL, peak detection)
- Statistical process monitoring (Phase I/II, EWMA, CUSUM)
- Classification (LDA, QDA, k-NN, kernel with cross-validation)
- Tolerance bands (FPCA, conformal, Degras SCB)
- Conformal prediction (split, jackknife+)
- Simulation (Karhunen-Loeve, Gaussian processes)
- Explainability (SHAP, PDP, permutation importance, significant regions)

All computations are performed in Rust via fdars-core for maximum performance.
"""

import sys as _sys

from pyfda import _native

__version__ = "0.1.0"

# Register submodules at expected paths so both access patterns work:
#   from pyfda.depth import fraiman_muniz_1d
#   from pyfda import depth; depth.fraiman_muniz_1d(...)
_submodule_names = (
    "fdata",
    "depth",
    "metric",
    "basis",
    "smoothing",
    "clustering",
    "regression",
    "alignment",
    "outliers",
    "seasonal",
    "spm",
    "classification",
    "tolerance",
    "conformal",
    "simulation",
    "explain",
)

for _name in _submodule_names:
    _submod = getattr(_native, _name)
    _sys.modules[f"{__name__}.{_name}"] = _submod

# Clean up namespace
del _name, _submod, _submodule_names
