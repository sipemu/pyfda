"""fdars – Functional Data Analysis for Python, powered by Rust.

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
- Functional time series (FTSM fit/forecast, ACF, stationarity, DPCA)
- Scalar-on-function regression (FAM, GKAM, GSAM additive models, variable selection)
- Fréchet regression (global, local, ANOVA) over density/metric spaces
- Density functional data analysis (LQD transform, Wasserstein barycenter, density FPCA)
- Multi-domain data (multi_fdata) — PyMultiFunData handle for multi-domain functional data
- Functional Additive Mixed Models (famm) — dense_flmm, fast_fmm, multi_famm

All computations are performed in Rust via fdars-core for maximum performance.
"""

import sys as _sys

from fdars import _native
from fdars.fdata_class import Fdata

__version__ = "0.4.0"

# Register submodules at expected paths so both access patterns work:
#   from fdars.depth import fraiman_muniz_1d
#   from fdars import depth; depth.fraiman_muniz_1d(...)
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
    "represent",
    "scoring",
    "inference",
    "pace_fpca",  # Phase 38 — PACE FPCA + IrregFdata opaque handle
    "fts",        # Phase 67 — Functional Time Series (FTSM fit/forecast, ACF, stationarity, DPCA)
    "scalar_on_function",  # Phase 68 — Scalar-on-Function additive/selection regression
    "frechet",             # Phase 69 — Fréchet regression & mean over metric spaces
    "density_fda",         # Phase 69 — Density FDA: LQD transform, Wasserstein barycenter, FPCA
    "multi_fdata",         # Phase 70 — PyMultiFunData opaque handle + builder (multi-domain container)
    "famm",                # Phase 70 — Functional Additive Mixed Models (dense_flmm, fast_fmm, multi_famm)
    "shapelet",            # Phase 71 — Shapelets: discovery, transform, classifier (SHAPE-01)
)

for _name in _submodule_names:
    _submod = getattr(_native, _name)
    _sys.modules[f"{__name__}.{_name}"] = _submod
    # Also expose as a package attribute so `import fdars; fdars.depth.<fn>` works
    # (not only `from fdars import depth`).
    setattr(_sys.modules[__name__], _name, _submod)

# Pure-Python convenience layers (built on top of the native modules).
from fdars import datasets, results, metrics, covariance  # noqa: E402
from fdars import plot  # noqa: E402  (matplotlib imported lazily inside plot.*)
from fdars import _augment as _augment  # noqa: E402
from fdars import advisor  # noqa: E402  (anthropic imported lazily inside advisor.*)

# Inject pure-Python orchestration helpers (e.g. clustering.cluster_optim) into
# the native submodule namespaces so they are reachable at the R-style path.
_augment.install()

# Register advisor in sys.modules so `from fdars.advisor import build_diagnostics`
# resolves via the package namespace (same pattern as native submodule loop above).
_sys.modules["fdars.advisor"] = advisor

__all__ = [
    "Fdata",
    *(_submodule_names),
    "datasets",
    "results",
    "plot",
    "metrics",
    "covariance",
    "advisor",
]

# Clean up namespace
del _name, _submod, _submodule_names
