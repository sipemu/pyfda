# API Reference

Complete reference for all `fdars` modules.

```python
from fdars import Fdata  # main entry point
```

## Modules

| Module | Description |
|--------|-------------|
| [**Fdata**](fdata.md) | **Functional data container** — the main entry point (1D curves, 2D surfaces, metadata, methods) |
| [fdata](fdata.md#low-level-functions) | Low-level functional data operations: mean, centering, derivatives, norms, median, normalization |
| [depth](depth.md) | Depth measures for functional data (Fraiman-Muniz, modal, band, projection, spatial) |
| [metric](metric.md) | Distance metrics and matrices (Lp, Hausdorff, DTW, Soft-DTW, Fourier, horizontal shift) |
| [basis](basis.md) | Basis representations: B-spline, Fourier, P-spline fitting, automatic selection |
| [smoothing](smoothing.md) | Nonparametric smoothing: Nadaraya-Watson, local polynomial, k-NN, bandwidth selection |
| [clustering](clustering.md) | Clustering: k-means, fuzzy C-means, GMM, silhouette, Calinski-Harabasz |
| [regression](regression.md) | Regression: FPCA, FPLS, scalar-on-function, function-on-scalar, ANOVA, logistic |
| [alignment](alignment.md) | Elastic alignment and shape analysis: SRSF, Karcher mean, warping, elastic FPCA |
| [outliers](outliers.md) | Outlier detection: LRT bootstrap, outliergram, magnitude-shape |
| [seasonal](seasonal.md) | Seasonal analysis: period detection (SAZED, autoperiod), STL decomposition, peaks |
| [spm](spm.md) | Statistical Process Monitoring: Phase I/II control charts, Hotelling T-squared |
| [classification](classification.md) | Classification: LDA, QDA, k-NN, kernel, cross-validation |
| [tolerance](tolerance.md) | Tolerance and confidence bands: FPCA-based, conformal, Degras SCB, equivalence test |
| [conformal](conformal.md) | Conformal prediction: regression intervals, nonparametric, classification sets |
| [simulation](simulation.md) | Simulation: Karhunen-Loeve expansion, Gaussian processes, covariance matrices |
| [explain](explain.md) | Explainability: permutation importance, PDP, SHAP values, significant regions |

## Conventions

- **Array inputs**: All array parameters accept `numpy.ndarray`. Data matrices have shape `(n_obs, n_points)`.
- **Return types**: Functions return `numpy.ndarray`, `float`, `dict`, or `list` depending on the output.
- **Optional parameters**: Shown with `=default` in signatures. Pass `None` for auto-selection where noted.
- **Errors**: Invalid inputs raise `ValueError` with a descriptive message.
