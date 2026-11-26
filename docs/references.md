# fdars Scientific References

> Curated primary paper references for fdars functional data analysis methods.  
> Generated offline from `python/fdars/_references_map.json`.  
> **143/580 callables** have at least one curated primary-paper entry.  
> Uncurated callables are absent; see the [AI Capability Map](ai-capability-map.md) for the full callable surface.

## Coverage

**143 of 580 public callables** have at least one curated primary-paper entry.
Remaining callables have contested attribution, no single primary paper, or are pending Phase-84 human DOI-landing-page verification.
See [AI Capability Map](ai-capability-map.md) for all 580 callables.

## Methods by Module

### Fdata Class Methods

#### Ramsay, J.O., Dalzell, C.J. (1991) — Some tools for functional data analysis

| Field | Value |
|-------|-------|
| Authors | Ramsay, J.O., Dalzell, C.J. |
| Year | 1991 |
| DOI | `doi:10.1111/j.2517-6161.1991.tb01844.x` |
| URL | [https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.251...](https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.2517-6161.1991.tb01844.x) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `_Fdata.to_pc` — Functional PCA representation of the curves (1-D only).
- `regression.fregre_lm` — Scalar-on-function linear regression via FPCs.
- `regression.predict_fregre_lm` — Predict new responses using a fitted functional linear model.
- `regression.fregre_cv` — Cross-validated selection of number of FPC components using K-fold CV.

---

### fdars.alignment — Elastic alignment, SRSF registration, Karcher mean, elastic FPCA

#### Bauer, M., Charon, N., Klassen, E., Kurtek, S., Needham, T., Pierron, T. (2024) — Elastic Metrics on Spaces of Euclidean Curves: Theory and Algorithms

| Field | Value |
|-------|-------|
| Authors | Bauer, M., Charon, N., Klassen, E., Kurtek, S., Needham, T., Pierron, T. |
| Year | 2024 |
| DOI | `doi:10.1007/s00332-024-10035-5` |
| URL | [https://doi.org/10.1007/s00332-024-10035-5](https://doi.org/10.1007/s00332-024-10035-5) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.ab_elastic_distance_pl` — Exact (a, b) elastic distance between two piecewise-linear curves.
- `alignment.ab_elastic_match_pl` — Exact (a, b) elastic matching of two piecewise-linear curves (polygons).

---

#### Beskos, A., Pinski, F.J., Sanz-Serna, J.M., Stuart, A.M. (2011) — Hybrid Monte Carlo on Hilbert spaces

| Field | Value |
|-------|-------|
| Authors | Beskos, A., Pinski, F.J., Sanz-Serna, J.M., Stuart, A.M. |
| Year | 2011 |
| DOI | `doi:10.1016/j.spa.2011.06.003` |
| URL | [https://doi.org/10.1016/j.spa.2011.06.003](https://doi.org/10.1016/j.spa.2011.06.003) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.bayesian_align_group` — Bayesian group alignment by MCMC with posterior credible bands for warps and template.

---

#### Cheng, W., Dryden, I.L., Huang, X. (2016) — Bayesian Registration of Functions and Curves

| Field | Value |
|-------|-------|
| Authors | Cheng, W., Dryden, I.L., Huang, X. |
| Year | 2016 |
| DOI | `doi:10.1214/15-BA957` |
| URL | [https://doi.org/10.1214/15-BA957](https://doi.org/10.1214/15-BA957) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.bayesian_align_pair` — Bayesian pairwise alignment via pCN MCMC on the Hilbert sphere.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdasrvf` | `pair_align_functions_bayes` | high |

---

#### Gertheiss, J., Goldsmith, J., Staicu, A.M. (2017) — A note on modeling sparse exponential-family functional response curves

| Field | Value |
|-------|-------|
| Authors | Gertheiss, J., Goldsmith, J., Staicu, A.M. |
| Year | 2017 |
| DOI | `doi:10.1016/j.csda.2016.07.010` |
| URL | [https://doi.org/10.1016/j.csda.2016.07.010](https://doi.org/10.1016/j.csda.2016.07.010) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.gfpca_two_step` — Two-step generalized FPCA of exponential-family curves (registr ``gfpca_twoStep``).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `registr` | `gfpca_twoStep` | high |

---

#### Hall, P., Müller, H.G., Yao, F. (2008) — Modelling Sparse Generalized Longitudinal Observations with Latent Gaussian Processes

| Field | Value |
|-------|-------|
| Authors | Hall, P., Müller, H.G., Yao, F. |
| Year | 2008 |
| DOI | `doi:10.1111/j.1467-9868.2008.00656.x` |
| URL | [https://doi.org/10.1111/j.1467-9868.2008.00656.x](https://doi.org/10.1111/j.1467-9868.2008.00656.x) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.gfpca_two_step` — Two-step generalized FPCA of exponential-family curves (registr ``gfpca_twoStep``).

---

#### Jaakkola, T.S., Jordan, M.I. (1997) — A Variational Approach to Bayesian Logistic Regression Models and their Extensions

| Field | Value |
|-------|-------|
| Authors | Jaakkola, T.S., Jordan, M.I. |
| Year | 1997 |
| URL | [https://proceedings.mlr.press/r1/jaakkola97a.html](https://proceedings.mlr.press/r1/jaakkola97a.html) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `alignment.gfpca_variational` — Generalized FPCA of exponential-family curves by variational EM (registr ``bfpca`` / ``fpca_gauss``).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `registr` | `bfpca` | high |

---

#### Kulis, B., Jordan, M.I. (2012) — Revisiting k-means: New Algorithms via Bayesian Nonparametrics

| Field | Value |
|-------|-------|
| Authors | Kulis, B., Jordan, M.I. |
| Year | 2012 |
| URL | [https://icml.cc/2012/papers/291.pdf](https://icml.cc/2012/papers/291.pdf) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `alignment.elastic_dpmeans` — Elastic DP-means clustering: the number of clusters follows from a distance penalty.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdasrvf` | `dpmeans_align` | high |

---

#### Lahiri, S., Robinson, D., Klassen, E. (2015) — Precise matching of PL curves in R^N in the square root velocity framework

| Field | Value |
|-------|-------|
| Authors | Lahiri, S., Robinson, D., Klassen, E. |
| Year | 2015 |
| DOI | `doi:10.4310/GIC.2015.v2.n3.a1` |
| URL | [https://doi.org/10.4310/GIC.2015.v2.n3.a1](https://doi.org/10.4310/GIC.2015.v2.n3.a1) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.ab_elastic_distance_pl` — Exact (a, b) elastic distance between two piecewise-linear curves.
- `alignment.ab_elastic_match_pl` — Exact (a, b) elastic matching of two piecewise-linear curves (polygons).

---

#### Lu, Y., Herbei, R., Kurtek, S. (2017) — Bayesian Registration of Functions With a Gaussian Process Prior

| Field | Value |
|-------|-------|
| Authors | Lu, Y., Herbei, R., Kurtek, S. |
| Year | 2017 |
| DOI | `doi:10.1080/10618600.2017.1336444` |
| URL | [https://doi.org/10.1080/10618600.2017.1336444](https://doi.org/10.1080/10618600.2017.1336444) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.bayesian_align_group` — Bayesian group alignment by MCMC with posterior credible bands for warps and template.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdasrvf` | `time_warping_bayes` | high |

---

#### Marron, J.S., Ramsay, J.O., Sangalli, L.M., Srivastava, A. (2015) — Functional Data Analysis of Amplitude and Phase Variation

| Field | Value |
|-------|-------|
| Authors | Marron, J.S., Ramsay, J.O., Sangalli, L.M., Srivastava, A. |
| Year | 2015 |
| DOI | `doi:10.1214/15-STS524` |
| URL | [https://projecteuclid.org/journals/statistical-science/vo...](https://projecteuclid.org/journals/statistical-science/volume-30/issue-4/Functional-Data-Analysis-of-Amplitude-and-Phase-Variation/10.1214/15-STS524.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `alignment.alignment_quality` — Comprehensive alignment quality metrics.
- `alignment.diagnose_alignment` — Diagnose alignment quality for every curve after Karcher mean computation.

---

#### Needham, T., Kurtek, S. (2020) — Simplifying Transforms for General Elastic Metrics on the Space of Plane Curves

| Field | Value |
|-------|-------|
| Authors | Needham, T., Kurtek, S. |
| Year | 2020 |
| DOI | `doi:10.1137/19M1265132` |
| URL | [https://doi.org/10.1137/19M1265132](https://doi.org/10.1137/19M1265132) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.ab_transform` — Kurtek-Needham F-transform of a planar curve for the (a, b) elastic metric.
- `alignment.ab_transform_inverse` — Inverse of ``ab_transform``: the planar curve starting at the origin with transform ``f``.
- `alignment.ab_closure_residual` — Closure residual c(1) − c(0) of the planar curve an (a, b) F-transform represents.
- `alignment.ab_project_closed` — Project a planar (a, b) F-transform onto the closed-curve manifold, preserving its L² norm.
- `alignment.curve_shape_align_pair` — Align curve ``beta2`` to ``beta1`` in elastic shape space (rotation, scale, seed, warp).
- `alignment.curve_shape_distance` — Elastic shape distance between two R^d curves under the chosen quotient.
- `alignment.curve_shape_self_distance_matrix` — Symmetric matrix of pairwise elastic shape distances between R^d curves.
- `alignment.curve_shape_karcher_mean` — Karcher (Fréchet) mean shape of R^d curves in elastic shape space.
- `alignment.curve_shape_karcher_median` — Karcher (geometric) median shape of R^d curves in elastic shape space.
- `alignment.curve_shape_depth` — Elastic amplitude and phase depth of R^d curves.
- `alignment.curve_shape_outlier_detection` — Shape outlier detection for R^d curves by distance to the Karcher median (or mean).
- `alignment.curve_shape_confidence_interval` — Confidence region of the centre shape of R^d curves (bootstrap or fdasrvf model-based).

---

#### Ramsay, J.O., Li, X. (1998) — Curve Registration

| Field | Value |
|-------|-------|
| Authors | Ramsay, J.O., Li, X. |
| Year | 1998 |
| DOI | `doi:10.1111/1467-9868.00129` |
| URL | [https://doi.org/10.1111/1467-9868.00129](https://doi.org/10.1111/1467-9868.00129) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.continuous_registration` — Ramsay-Li continuous registration with smooth monotone warps (R fda register.fd).

---

#### Srivastava, A., Wu, W., Kurtek, S., Klassen, E., Marron, J.S. (2011) — Registration of functional data using Fisher-Rao metric

| Field | Value |
|-------|-------|
| Authors | Srivastava, A., Wu, W., Kurtek, S., Klassen, E., Marron, J.S. |
| Year | 2011 |
| URL | [https://arxiv.org/abs/1103.3817](https://arxiv.org/abs/1103.3817) |
| Type | preprint |
| Status | Curated |

**Callables implementing this method:**

- `alignment.karcher_mean` — Karcher (Frechet) mean under the elastic metric.
- `alignment.elastic_align_pair` — Pairwise elastic alignment of two curves.
- `alignment.srsf_transform` — SRSF (Square Root Slope Function) transform.
- `alignment.srsf_inverse` — Inverse SRSF transform.
- `alignment.elastic_distance` — Elastic (Fisher-Rao) distance between two curves.
- `alignment.elastic_self_distance_matrix` — Elastic self distance matrix.
- `alignment.elastic_cross_distance_matrix` — Elastic cross distance matrix.
- `alignment.amplitude_distance` — Amplitude distance between two curves.
- `alignment.phase_distance` — Phase distance between two curves.
- `alignment.elastic_decomposition` — Elastic phase-amplitude decomposition of two curves.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Matlab | `fdasrvf_MATLAB` | `multiple_align_functions` | low |
| Python | `fdasrsf` | `fdawarp` | high |
| R | `fdasrvf` | `multiple_align_functions` | high |

---

#### Srivastava, A., Klassen, E.P. (2016) — Functional and Shape Data Analysis

| Field | Value |
|-------|-------|
| Authors | Srivastava, A., Klassen, E.P. |
| Year | 2016 |
| DOI | `doi:10.1007/978-1-4939-4020-2` |
| URL | [https://link.springer.com/book/10.1007/978-1-4939-4020-2](https://link.springer.com/book/10.1007/978-1-4939-4020-2) |
| Type | book |
| Status | Curated |

**Callables implementing this method:**

- `alignment.tsrvf_transform` — TSRVF (Transported SRSF) transform.
- `alignment.tsrvf_transform_with_method` — TSRVF transform with configurable transport method.
- `alignment.karcher_mean_closed` — Karcher mean for closed (periodic) curves.
- `alignment.elastic_align_pair_closed` — Align closed (periodic) curve f2 to f1 with rotation search.
- `alignment.curve_shape_align_pair` — Align curve ``beta2`` to ``beta1`` in elastic shape space (rotation, scale, seed, warp).
- `alignment.curve_shape_distance` — Elastic shape distance between two R^d curves under the chosen quotient.
- `alignment.curve_shape_self_distance_matrix` — Symmetric matrix of pairwise elastic shape distances between R^d curves.
- `alignment.curve_shape_karcher_mean` — Karcher (Fréchet) mean shape of R^d curves in elastic shape space.
- `alignment.curve_shape_karcher_median` — Karcher (geometric) median shape of R^d curves in elastic shape space.
- `alignment.curve_shape_depth` — Elastic amplitude and phase depth of R^d curves.
- `alignment.curve_shape_outlier_detection` — Shape outlier detection for R^d curves by distance to the Karcher median (or mean).
- `alignment.curve_shape_confidence_interval` — Confidence region of the centre shape of R^d curves (bootstrap or fdasrvf model-based).
- `alignment.curve_shape_boxplot` — Elastic shape box plot of the curves summarised by a Karcher median (fdasrvf ``curve_boxplot``).
- `alignment.curve_shape_boxplot_from_aligned` — Elastic shape box plot from SRVFs and curves already aligned to a median.
- `alignment.curve_shape_karcher_covariance` — Sample covariance of the Karcher shooting vectors (tangent space at the mean).
- `alignment.curve_shape_pca` — Principal component analysis of curve shapes in the tangent space at the Karcher mean.
- `alignment.curve_shape_tsrvf` — TSRVF of R^d curves: align to the Karcher mean and map into its tangent space.
- `alignment.curve_shape_tangent_to_curve` — Map a tangent vector at the Karcher mean back to a curve (inverse of ``curve_shape_tsrvf``).

---

#### Steyer, L., Stöcker, A., Greven, S. (2023) — Elastic Analysis of Irregularly or Sparsely Sampled Curves

| Field | Value |
|-------|-------|
| Authors | Steyer, L., Stöcker, A., Greven, S. |
| Year | 2023 |
| DOI | `doi:10.1111/biom.13706` |
| URL | [https://doi.org/10.1111/biom.13706](https://doi.org/10.1111/biom.13706) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.sparse_elastic_align_pair` — Elastic alignment of two sparsely observed curves treated as polygons (elasdics ``align_curves``).
- `alignment.sparse_elastic_mean` — Elastic (Fréchet) mean of sparsely observed curves with a spline SRV (elasdics ``compute_elastic_mean``).
- `alignment.sparse_curves_from_irreg` — Convert 1-D irregular functional data into sparse curves for the sparse elastic functions.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `elasdics` | `align_curves` | low |

---

#### Tang, R., Müller, H.G. (2008) — Pairwise curve synchronization for functional data

| Field | Value |
|-------|-------|
| Authors | Tang, R., Müller, H.G. |
| Year | 2008 |
| DOI | `doi:10.1093/biomet/asn047` |
| URL | [https://doi.org/10.1093/biomet/asn047](https://doi.org/10.1093/biomet/asn047) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.pairwise_synchronization` — Tang-Mueller pairwise curve synchronisation (R fdapace WFDA).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdapace` | `WFDA` | high |

---

#### Tucker, J.D., Wu, W., Srivastava, A. (2013) — Generative models for functional data using phase and amplitude separation

| Field | Value |
|-------|-------|
| Authors | Tucker, J.D., Wu, W., Srivastava, A. |
| Year | 2013 |
| DOI | `doi:10.1016/j.csda.2012.12.001` |
| URL | [https://www.sciencedirect.com/science/article/abs/pii/S01...](https://www.sciencedirect.com/science/article/abs/pii/S0167947312004227) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.vert_fpca` — Vertical (amplitude) FPCA on aligned data.
- `alignment.horiz_fpca` — Horizontal (phase) FPCA.
- `alignment.joint_fpca` — Joint (amplitude + phase) FPCA.
- `alignment.gauss_model` — Generate random curves from a fitted Gaussian model on aligned data.
- `alignment.joint_gauss_model` — Generate random curves from a joint Gaussian model preserving amplitude-phase correlation.
- `alignment.jfpca_fit` — Fit a reusable joint amplitude + phase FPCA (jfPCA) model for out-of-sample projection.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `fdasrsf` | `fdavpca` | high |
| R | `fdasrvf` | `jointFPCA` | high |

---

#### Tucker, J.D., Yarger, D. (2024) — Elastic functional changepoint detection of climate impacts from localized sources

| Field | Value |
|-------|-------|
| Authors | Tucker, J.D., Yarger, D. |
| Year | 2024 |
| DOI | `doi:10.1002/env.2826` |
| URL | [https://onlinelibrary.wiley.com/doi/10.1002/env.2826](https://onlinelibrary.wiley.com/doi/10.1002/env.2826) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.elastic_changepoint` — Detect a distributional changepoint in a sequence of curves (elastic).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `fdasrsf` | `ElasticChangePoint` | high |
| R | `fdasrvf` | `elastic.changepoint` | high |

---

#### Wrobel, J., Bauer, A. (2021) — registr 2.0: Incomplete Curve Registration for Exponential Family Functional Data

| Field | Value |
|-------|-------|
| Authors | Wrobel, J., Bauer, A. |
| Year | 2021 |
| DOI | `doi:10.21105/joss.02964` |
| URL | [https://doi.org/10.21105/joss.02964](https://doi.org/10.21105/joss.02964) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.register_fpca` — Joint registration and generalized FPCA of exponential-family curves (registr ``register_fpca``).
- `alignment.register_fpca_regular` — Joint registration and generalized FPCA of exponential-family curves on a common grid.
- `alignment.register_expfam` — One exponential-family registration pass of every curve to a population-mean template (registr ``registr``).

---

#### Wrobel, J., Zipunnikov, V., Schrack, J., Goldsmith, J. (2019) — Registration for Exponential Family Functional Data

| Field | Value |
|-------|-------|
| Authors | Wrobel, J., Zipunnikov, V., Schrack, J., Goldsmith, J. |
| Year | 2019 |
| DOI | `doi:10.1111/biom.12963` |
| URL | [https://doi.org/10.1111/biom.12963](https://doi.org/10.1111/biom.12963) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.register_fpca` — Joint registration and generalized FPCA of exponential-family curves (registr ``register_fpca``).
- `alignment.register_fpca_regular` — Joint registration and generalized FPCA of exponential-family curves on a common grid.
- `alignment.register_expfam` — One exponential-family registration pass of every curve to a population-mean template (registr ``registr``).
- `alignment.gfpca_variational` — Generalized FPCA of exponential-family curves by variational EM (registr ``bfpca`` / ``fpca_gauss``).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `registr` | `register_fpca` | low |

---

#### Xie, W., Kurtek, S., Bharath, K., Sun, Y. (2017) — A Geometric Approach to Visualization of Variability in Functional Data

| Field | Value |
|-------|-------|
| Authors | Xie, W., Kurtek, S., Bharath, K., Sun, Y. |
| Year | 2017 |
| DOI | `doi:10.1080/01621459.2016.1256813` |
| URL | [https://doi.org/10.1080/01621459.2016.1256813](https://doi.org/10.1080/01621459.2016.1256813) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `alignment.elastic_boxplots` — Elastic amplitude and phase functional box plots (fdasrsf ``ampbox`` / ``phbox``).
- `alignment.amplitude_boxplot_from_aligned` — Elastic amplitude box plot from curves already aligned to a median.
- `alignment.elastic_phase_boxplot` — Elastic phase box plot of warping functions on the Hilbert sphere.

---

### fdars.basis — Basis representations — B-spline, Fourier, functional PCA

#### Daubechies, I. (1992) — Ten Lectures on Wavelets

| Field | Value |
|-------|-------|
| Authors | Daubechies, I. |
| Year | 1992 |
| DOI | `doi:10.1137/1.9781611970104` |
| URL | [https://doi.org/10.1137/1.9781611970104](https://doi.org/10.1137/1.9781611970104) |
| Type | book |
| Status | Curated |

**Callables implementing this method:**

- `basis.wavelet_decompose` — Multi-level orthogonal discrete wavelet transform (Mallat pyramid) of one signal.
- `basis.wavelet_decompose_matrix` — Multi-level discrete wavelet transform of every row (curve) of a matrix.
- `basis.wavelet_reconstruct` — Inverse discrete wavelet transform: rebuild a signal from its coefficient pyramid.
- `basis.wavelet_max_level` — Maximum useful DWT depth for a signal length and wavelet family.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `PyWavelets` | `wavedec` | high |

---

#### Eilers, P.H.C., Marx, B.D. (1996) — Flexible smoothing with B-splines and penalties

| Field | Value |
|-------|-------|
| Authors | Eilers, P.H.C., Marx, B.D. |
| Year | 1996 |
| DOI | `doi:10.1214/ss/1038425655` |
| URL | [https://projecteuclid.org/journals/statistical-science/vo...](https://projecteuclid.org/journals/statistical-science/volume-11/issue-2/Flexible-smoothing-with-B-splines-and-penalties/10.1214/ss/1038425655.full) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `basis.basis_nbasis_cv` — Cross-validated selection of number of basis functions.
- `basis.pspline_fit_1d` — Fit P-splines to 1D functional data.
- `basis.pspline_fit_gcv` — P-spline fit with GCV-selected smoothing parameter.
- `basis.smooth_basis_gcv` — Smooth functional data using basis expansion with GCV.
- `basis.smooth_basis_aic` — Smooth functional data using basis expansion with AIC-optimal lambda.
- `basis.fdata_to_basis_1d` — Project functional data onto a B-spline or Fourier basis.
- `basis.basis_to_fdata_1d` — Reconstruct functional data from basis coefficients.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `scikit-fda` | `BSplineSmoother` | high |
| R | `mgcv` | `s(..., bs="ps")` | high |

---

### fdars.classification — Functional classifiers — k-nearest neighbours, SVM, centroid-based

#### Cuesta-Albertos, J.A., Fraiman, R. (2009) — Impartial trimmed means for functional data

| Field | Value |
|-------|-------|
| Authors | Cuesta-Albertos, J.A., Fraiman, R. |
| Year | 2009 |
| DOI | `doi:10.1007/978-3-7908-2349-3_12` |
| URL | [https://link.springer.com/chapter/10.1007/978-3-7908-2349...](https://link.springer.com/chapter/10.1007/978-3-7908-2349-3_12) |
| Type | book_chapter |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `classification.fclassif_dd` — Depth-based DD-classifier for functional data.

---

### fdars.clustering — Functional k-means, fuzzy, GMM, and elastic clustering

#### Bouveyron, C., Côme, E., Jacques, J. (2015) — The discriminative functional mixture model for a comparative analysis of bike sharing systems

| Field | Value |
|-------|-------|
| Authors | Bouveyron, C., Côme, E., Jacques, J. |
| Year | 2015 |
| DOI | `doi:10.1214/15-AOAS861` |
| URL | [https://projecteuclid.org/journals/annals-of-applied-stat...](https://projecteuclid.org/journals/annals-of-applied-statistics/volume-9/issue-4/The-discriminative-functional-mixture-model-for-a-comparative-analysis-of/10.1214/15-AOAS861.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `clustering.funfem_cluster` — Fisher-EM discriminative functional clustering (FunFEM).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `funFEM` | `funFEM` | high |

---

#### Bouveyron, C., Jacques, J. (2011) — Model-based clustering of time series in group-specific functional subspaces

| Field | Value |
|-------|-------|
| Authors | Bouveyron, C., Jacques, J. |
| Year | 2011 |
| DOI | `doi:10.1007/s11634-011-0095-6` |
| URL | [https://link.springer.com/article/10.1007/s11634-011-0095-6](https://link.springer.com/article/10.1007/s11634-011-0095-6) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `clustering.gmm_cluster` — GMM clustering for functional data (via basis projection).

---

#### Chiou, J.M., Li, P.L. (2007) — Functional clustering and identifying substructures of longitudinal data

| Field | Value |
|-------|-------|
| Authors | Chiou, J.M., Li, P.L. |
| Year | 2007 |
| DOI | `doi:10.1111/j.1467-9868.2007.00605.x` |
| URL | [https://rss.onlinelibrary.wiley.com/doi/full/10.1111/j.14...](https://rss.onlinelibrary.wiley.com/doi/full/10.1111/j.1467-9868.2007.00605.x) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `clustering.kmeans_fd` — K-means clustering for functional data.
- `clustering.kcfc_cluster` — K-means with per-cluster FPCA (KCFC) clustering for functional data.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdapace` | `kCFC` | high |

---

#### Sangalli, L.M., Secchi, P., Vantini, S., Vitelli, V. (2010) — k-mean alignment for curve clustering

| Field | Value |
|-------|-------|
| Authors | Sangalli, L.M., Secchi, P., Vantini, S., Vitelli, V. |
| Year | 2010 |
| DOI | `doi:10.1016/j.csda.2009.12.008` |
| URL | [https://doi.org/10.1016/j.csda.2009.12.008](https://doi.org/10.1016/j.csda.2009.12.008) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `clustering.align_cluster_fd` — Elastic-alignment functional clustering.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdasrvf` | `kmeans_align` | high |

---

### fdars.conformal — Conformal prediction and classification bands

#### Wang, F., Kurtek, S., Zhang, Y. (2026) — Joint Registration and Conformal Prediction for Partially Observed Functional Data

| Field | Value |
|-------|-------|
| Authors | Wang, F., Kurtek, S., Zhang, Y. |
| Year | 2026 |
| DOI | `doi:10.1080/10618600.2026.2634823` |
| URL | [https://doi.org/10.1080/10618600.2026.2634823](https://doi.org/10.1080/10618600.2026.2634823) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `conformal.partial_conformal_fit` — Fit the partial-curve conformal model: random split, elastic Karcher template, registration.
- `conformal.partial_conformal_fit_with_template` — Fit the partial-curve conformal model with a supplied template (all curves calibrate).
- `conformal.partial_conformal_predict` — Conformal amplitude band and phase set for a curve observed on a grid prefix.
- `conformal.partial_conformal_predict_observed` — Conformal amplitude band and phase set for a curve observed on a prefix, fragments or sparse times.
- `conformal.partial_conformal_select_bandwidth` — Held-out bandwidth selection for partial-curve conformal prediction.

---

### fdars.density_fda — Density-based functional data analysis and Wasserstein distances

#### Agueh, M., Carlier, G. (2011) — Barycenters in the Wasserstein space

| Field | Value |
|-------|-------|
| Authors | Agueh, M., Carlier, G. |
| Year | 2011 |
| DOI | `doi:10.1137/100805741` |
| URL | [https://epubs.siam.org/doi/10.1137/100805741](https://epubs.siam.org/doi/10.1137/100805741) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `density_fda.wasserstein_barycenter` — Compute the Wasserstein Fréchet mean (barycenter) of a collection of densities.

---

#### Petersen, A., Müller, H.G. (2016) — Functional data analysis for density functions by transformation to a Hilbert space

| Field | Value |
|-------|-------|
| Authors | Petersen, A., Müller, H.G. |
| Year | 2016 |
| DOI | `doi:10.1214/15-AOS1363` |
| URL | [https://projecteuclid.org/journals/annals-of-statistics/v...](https://projecteuclid.org/journals/annals-of-statistics/volume-44/issue-1/Functional-data-analysis-for-density-functions-by-transformation-to-a/10.1214/15-AOS1363.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `density_fda.lqd_transform` — Compute the log-quantile density (LQD) transform of a density function.
- `density_fda.inverse_lqd` — Compute the inverse LQD transform: reconstruct a density from its LQD representation.
- `density_fda.lqd_fpca` — Functional PCA of densities via the LQD transform.
- `density_fda.normalize_density` — Normalize a density function to integrate to 1.

---

### fdars.depth — Functional depth measures — Fraiman-Muniz, band, modal, random-projection

#### Claeskens, G., Hubert, M., Slaets, L., Vakili, K. (2014) — Multivariate functional halfspace depth

| Field | Value |
|-------|-------|
| Authors | Claeskens, G., Hubert, M., Slaets, L., Vakili, K. |
| Year | 2014 |
| DOI | `doi:10.1080/01621459.2013.856795` |
| URL | [https://www.tandfonline.com/doi/abs/10.1080/01621459.2013...](https://www.tandfonline.com/doi/abs/10.1080/01621459.2013.856795) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `depth.random_projection_deriv_1d` — Random-projection depth using curves and their derivatives (RPD).

---

#### Cuevas, A., Febrero, M., Fraiman, R. (2007) — Robust estimation and classification for functional data via projection-based depth notions

| Field | Value |
|-------|-------|
| Authors | Cuevas, A., Febrero, M., Fraiman, R. |
| Year | 2007 |
| DOI | `doi:10.1007/s00180-007-0053-0` |
| URL | [https://link.springer.com/article/10.1007/s00180-007-0053-0](https://link.springer.com/article/10.1007/s00180-007-0053-0) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `depth.modal_1d` — Modal depth for 1D functional data.
- `depth.modal_2d` — Modal depth for 2D functional data.
- `depth.random_projection_1d` — Random projection depth for 1D functional data.
- `depth.random_projection_2d` — Random projection depth for 2D functional data.
- `depth.random_tukey_1d` — Random Tukey depth for 1D functional data.
- `depth.random_tukey_2d` — Random Tukey depth for 2D functional data.

---

#### Unknown (n.d.) — (title pending verification)

| Field | Value |
|-------|-------|
| Authors | Unknown |
| Year | n.d. |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `depth.functional_spatial_1d` — Functional spatial depth for 1D data.
- `depth.functional_spatial_2d` — Functional spatial depth for 2D data.
- `depth.kernel_functional_spatial_1d` — Kernel functional spatial depth for 1D data.
- `depth.kernel_functional_spatial_2d` — Kernel functional spatial depth for 2D data.

---

#### Fraiman, R., Muniz, G. (2001) — Trimmed means for functional data

| Field | Value |
|-------|-------|
| Authors | Fraiman, R., Muniz, G. |
| Year | 2001 |
| DOI | `doi:10.1007/BF02595706` |
| URL | [https://link.springer.com/article/10.1007/BF02595706](https://link.springer.com/article/10.1007/BF02595706) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `depth.fraiman_muniz_1d` — Fraiman-Muniz depth for 1D functional data.
- `depth.fraiman_muniz_2d` — Fraiman-Muniz depth for 2D functional data.
- `_Fdata.depth` — Compute depth values for each observation.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `scikit-fda` | `fraiman_muniz_depth` | high |
| R | `fda.usc` | `depth.FM` | high |

---

#### López-Pintado, S., Romo, J. (2009) — On the concept of depth for functional data

| Field | Value |
|-------|-------|
| Authors | López-Pintado, S., Romo, J. |
| Year | 2009 |
| DOI | `doi:10.1198/jasa.2009.0108` |
| URL | [https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.0108](https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.0108) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `depth.band_1d` — Band depth for 1D functional data.
- `depth.modified_band_1d` — Modified band depth for 1D functional data.
- `alignment.phase_boxplot` — Phase (warping) box plot for functional data.
- `alignment.phase_boxplot_classify` — Classify new warping functions against a phase box plot fitted on ``gammas``.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `scikit-fda` | `BandDepth` | high |
| R | `fda.usc` | `depth.mode` | high |

---

#### Narisetty, N.N., Nair, V.N. (2016) — Extremal depth for functional data and applications

| Field | Value |
|-------|-------|
| Authors | Narisetty, N.N., Nair, V.N. |
| Year | 2016 |
| DOI | `doi:10.1080/01621459.2015.1110033` |
| URL | [https://www.tandfonline.com/doi/full/10.1080/01621459.201...](https://www.tandfonline.com/doi/full/10.1080/01621459.2015.1110033) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `depth.modified_epigraph_index_1d` — Modified epigraph index for 1D functional data.

---

#### Sun, Y., Genton, M.G. (2011) — Functional boxplots

| Field | Value |
|-------|-------|
| Authors | Sun, Y., Genton, M.G. |
| Year | 2011 |
| DOI | `doi:10.1198/jcgs.2011.09224` |
| URL | [https://www.tandfonline.com/doi/abs/10.1198/jcgs.2011.09224](https://www.tandfonline.com/doi/abs/10.1198/jcgs.2011.09224) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `depth.functional_boxplot` — Canonical López-Pintado–Romo depth-fence functional boxplot (numeric only).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdaoutlier` | `functional_boxplot` | high |

---

### fdars.explain — Functional explainability — SHAP, FCI, GRAD-CAM, and attribution maps

#### Goode, K., Tucker, J.D., Ries, D., Hofmann, H. (2026) — Explainable Machine Learning for Functional Data

| Field | Value |
|-------|-------|
| Authors | Goode, K., Tucker, J.D., Ries, D., Hofmann, H. |
| Year | 2026 |
| DOI | `doi:10.6339/25-JDS1212` |
| URL | [https://doi.org/10.6339/25-JDS1212](https://doi.org/10.6339/25-JDS1212) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `explain.elastic_pfi` — Model-agnostic permutation feature importance over jfPCA (or any) PC scores.
- `explain.veesa_pipeline` — End-to-end VEESA pipeline: jfPCA fit, exact training scores, then elastic PFI.

---

### fdars.famm — Functional additive mixed models (FAMM) for longitudinal data

#### Scheipl, F., Staicu, A.M., Greven, S. (2015) — Functional additive mixed models

| Field | Value |
|-------|-------|
| Authors | Scheipl, F., Staicu, A.M., Greven, S. |
| Year | 2015 |
| DOI | `doi:10.1080/10618600.2014.901914` |
| URL | [https://www.tandfonline.com/doi/abs/10.1080/10618600.2014...](https://www.tandfonline.com/doi/abs/10.1080/10618600.2014.901914) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `famm.dense_flmm` — Fit a Functional Linear Mixed Model (FLMM) via REML-EM.
- `famm.fast_fmm` — Fit a fast Functional Mixed Model (FMM) with optional Wald inference.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `refund` | `pfr` | high |

---

#### Volkmann, A., Stöcker, A., Scheipl, F., Greven, S. (2023) — Multivariate functional additive mixed models

| Field | Value |
|-------|-------|
| Authors | Volkmann, A., Stöcker, A., Scheipl, F., Greven, S. |
| Year | 2023 |
| DOI | `doi:10.1177/1471082X211056158` |
| URL | [https://journals.sagepub.com/doi/full/10.1177/1471082X211...](https://journals.sagepub.com/doi/full/10.1177/1471082X211056158) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `famm.multi_famm` — Fit a multi-variable Functional Additive Mixed Model (multiFAMM).

---

### fdars.fdata — Core functional data operations — mean, deriv, norm, integrate, reconstruct

#### Gervini, D. (2008) — Robust functional estimation using the median and spherical principal components

| Field | Value |
|-------|-------|
| Authors | Gervini, D. |
| Year | 2008 |
| DOI | `doi:10.1093/biomet/asn031` |
| URL | [https://academic.oup.com/biomet/article/95/3/587/217534](https://academic.oup.com/biomet/article/95/3/587/217534) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `fdata.geometric_median_1d` — Compute the geometric (L1) median of 1D functional data.
- `fdata.geometric_median_2d` — Compute the geometric (L1) median of 2D functional data.
- `_Fdata.geometric_median` — Compute the geometric (L1) median curve or surface.

---

#### Ramsay, J.O., Silverman, B.W. (2005) — Functional Data Analysis

| Field | Value |
|-------|-------|
| Authors | Ramsay, J.O., Silverman, B.W. |
| Year | 2005 |
| DOI | `doi:10.1007/b98888` |
| URL | [https://link.springer.com/book/10.1007/b98888](https://link.springer.com/book/10.1007/b98888) |
| Type | book |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `fdata.mean_1d` — Compute the pointwise mean of 1D functional data.
- `fdata.mean_2d` — Compute the pointwise mean of 2D functional data.
- `fdata.functional_covariance` — Compute the Bessel-corrected m×m covariance surface of 1D functional data.
- `fdata.functional_variance` — Compute the Bessel-corrected pointwise variance of 1D functional data.
- `fdata.functional_std` — Compute the Bessel-corrected pointwise standard deviation of 1D functional data.
- `fdata.norm_lp_1d` — Compute Lp norms of 1D functional data.
- `fdata.deriv_1d` — Compute numerical derivatives of 1D functional data.
- `fdata.deriv_2d` — Compute numerical derivatives of 2D functional data.
- `fdata.center_1d` — Center functional data by subtracting the pointwise mean.
- `fdata.trim_mean` — Compute the depth-trimmed mean of 1D functional data.
- `fdata.normalize` — Normalize functional data.
- `regression.fpca` — Functional principal component analysis (FPCA).
- `regression.concurrent_regression` — Concurrent (varying-coefficient) functional regression.
- `regression.fosr` — Function-on-scalar regression (FOSR).
- `regression.fosr_fpc` — Function-on-scalar regression via FPCs (FOSR-FPC).
- `regression.predict_fosr` — Predict new functional responses from a fitted FOSR model.
- `simulation.sim_kl` — Simulate functional data via Karhunen-Loeve expansion (low-level).
- `simulation.simulate` — Simulate functional data via Karhunen-Loeve expansion.
- `simulation.eigenfunctions` — Compute eigenfunctions.
- `simulation.eigenvalues` — Compute eigenvalues.
- `alignment.landmark_register` — Register curves to common landmark positions.
- `alignment.landmark_detect_and_register` — Detect landmarks and register in one call.
- `alignment.least_squares_shift_registration` — Register curves by a per-curve rigid horizontal shift (least-squares).
- `alignment.detect_landmarks` — Detect landmarks (peaks, valleys, zero-crossings, inflections) in a curve.
- `_Fdata.shift_register` — Register curves by a per-curve rigid horizontal shift (least-squares).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `scikit-fda` | `FPCA` | high |
| R | `fda` | `pca.fd` | high |

---

### fdars.frechet — Fréchet regression for metric-space responses

#### Petersen, A., Müller, H.G. (2019) — Fréchet regression for random objects with Euclidean predictors

| Field | Value |
|-------|-------|
| Authors | Petersen, A., Müller, H.G. |
| Year | 2019 |
| DOI | `doi:10.1214/17-AOS1624` |
| URL | [https://projecteuclid.org/journals/annals-of-statistics/v...](https://projecteuclid.org/journals/annals-of-statistics/volume-47/issue-2/Fr%c3%a9chet-regression-for-random-objects-with-Euclidean-predictors/10.1214/17-AOS1624.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `frechet.frechet_global_reg` — Global Fréchet linear regression for density-response functional data.
- `frechet.frechet_local_reg` — Local Fréchet regression for density-response functional data.
- `frechet.frechet_mean` — Fréchet mean over a metric space, dispatched by space name.
- `frechet.frechet_anova` — Fréchet ANOVA: test equality of Fréchet means across groups.

---

### fdars.fts — Functional time series — forecasting, correlation, spectral analysis

#### Hörmann, S., Kokoszka, P. (2010) — Weakly dependent functional data

| Field | Value |
|-------|-------|
| Authors | Hörmann, S., Kokoszka, P. |
| Year | 2010 |
| DOI | `doi:10.1214/09-AOS768` |
| URL | [https://projecteuclid.org/journals/annals-of-statistics/v...](https://projecteuclid.org/journals/annals-of-statistics/volume-38/issue-3/Weakly-dependent-functional-data/10.1214/09-AOS768.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `fts.functional_acf` — Compute the functional autocorrelation function (ACF) with Monte Carlo bands.
- `fts.functional_pacf` — Compute the functional partial autocorrelation function (PACF) with Monte Carlo bands.
- `fts.stationarity_test` — Test stationarity of functional time series via permutation test.
- `fts.functional_difference` — Compute the first-order functional difference (lag-1 differencing).

---

#### Hyndman, R.J., Ullah, M.S. (2007) — Robust forecasting of mortality and fertility rates: a functional data approach

| Field | Value |
|-------|-------|
| Authors | Hyndman, R.J., Ullah, M.S. |
| Year | 2007 |
| DOI | `doi:10.1016/j.csda.2006.07.028` |
| URL | [https://www.sciencedirect.com/science/article/abs/pii/S01...](https://www.sciencedirect.com/science/article/abs/pii/S0167947306002775) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `fts.ftsm` — Fit a Functional Time Series Model (FTSM) via FPCA + Yule-Walker AR fitting.
- `fts.ftsm_forecast` — Fit an FTSM and produce a single- or multi-horizon forecast (single-step variant).
- `fts.ftsm_forecast_multistep` — Fit an FTSM and produce a multi-step forecast (iterative multi-step variant).
- `fts.ftsm_update` — Online update of an FTSM with one or more new curves.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `ftsa` | `ftsm` | high |

---

#### Panaretos, V.M., Tavakoli, S. (2013) — Fourier analysis of stationary time series in function space

| Field | Value |
|-------|-------|
| Authors | Panaretos, V.M., Tavakoli, S. |
| Year | 2013 |
| DOI | `doi:10.1214/13-AOS1086` |
| URL | [https://projecteuclid.org/journals/annals-of-statistics/v...](https://projecteuclid.org/journals/annals-of-statistics/volume-41/issue-2/Fourier-analysis-of-stationary-time-series-in-function-space/10.1214/13-AOS1086.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `fts.dpca` — Fit Dynamic Functional Principal Components Analysis (DPCA).
- `fts.dpca_reconstruct` — Fit DPCA and reconstruct the functional time series from dynamic components.
- `fts.spectral_density` — Estimate the spectral density operator of a functional time series.
- `fts.long_run_covariance` — Estimate the long-run covariance operator of a functional time series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `freqdom.fda` | `dpca` | high |

---

### fdars.inference — Functional inference — two-sample tests, interval-wise testing

#### Anderson, M.J. (2001) — A new method for non-parametric multivariate analysis of variance

| Field | Value |
|-------|-------|
| Authors | Anderson, M.J. |
| Year | 2001 |
| DOI | `doi:10.1111/j.1442-9993.2001.01070.pp.x` |
| URL | [https://doi.org/10.1111/j.1442-9993.2001.01070.pp.x](https://doi.org/10.1111/j.1442-9993.2001.01070.pp.x) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `inference.permanova` — PERMANOVA (Anderson 2001) permutation test of group differences on a distance matrix.
- `alignment.elastic_phase_amplitude_test` — Separate PERMANOVA tests of group differences in amplitude and in phase.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `vegan` | `adonis2` | high |

---

#### Cuesta-Albertos, J.A., Febrero-Bande, M. (2010) — A simple multiway ANOVA for functional data

| Field | Value |
|-------|-------|
| Authors | Cuesta-Albertos, J.A., Febrero-Bande, M. |
| Year | 2010 |
| DOI | `doi:10.1007/s11749-010-0185-3` |
| URL | [https://link.springer.com/article/10.1007/s11749-010-0185-3](https://link.springer.com/article/10.1007/s11749-010-0185-3) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `inference.oneway_anova_vstat` — One-way functional ANOVA V-statistic (asymptotic scaled-χ² test).

---

#### Cuevas, A., Febrero, M., Fraiman, R. (2004) — An ANOVA test for functional data

| Field | Value |
|-------|-------|
| Authors | Cuevas, A., Febrero, M., Fraiman, R. |
| Year | 2004 |
| DOI | `doi:10.1016/j.csda.2003.10.021` |
| URL | [https://www.sciencedirect.com/science/article/abs/pii/S01...](https://www.sciencedirect.com/science/article/abs/pii/S0167947303001567) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `inference.f_perm_test` — Functional two-sample permutation *F*-test.
- `inference.t_perm_test` — Functional two-sample permutation *t*-test.
- `inference.two_sample_mean_test` — Functional two-sample mean-equality test via Hotelling-T² on a shared FPC

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fda.usc` | `fanova.onefactor` | high |

---

#### Degras, D. (2011) — Simultaneous confidence bands for nonparametric regression with functional data

| Field | Value |
|-------|-------|
| Authors | Degras, D. |
| Year | 2011 |
| DOI | `doi:10.5705/ss.2009.207` |
| URL | [https://www3.stat.sinica.edu.tw/sstest/j21n4/J21N412/J21N...](https://www3.stat.sinica.edu.tw/sstest/j21n4/J21N412/J21N412.html) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `inference.mean_scb` — Simultaneous confidence band for the mean function (Degras).
- `inference.scb_two_sample_test` — Two-sample mean-equality test via a simultaneous confidence band for the
- `tolerance.scb_mean_degras` — Simultaneous confidence band (Degras method).

---

#### Pini, A., Vantini, S. (2016) — The interval testing procedure: A general framework for inference in functional data analysis

| Field | Value |
|-------|-------|
| Authors | Pini, A., Vantini, S. |
| Year | 2016 |
| DOI | `doi:10.1111/biom.12476` |
| URL | [https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12476](https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12476) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `inference.itp_flm` — Interval-wise testing procedure for the functional linear model.
- `inference.itp_one_pop` — Interval-wise testing procedure for a single functional population.
- `inference.itp_two_pop` — Interval-wise testing procedure for two functional populations.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdatest` | `ITP1bspline` | high |

---

### fdars.metric — Functional distance and similarity metrics — L2, L1, Mahalanobis, DTW

#### Blondel, M., Mensch, A., Vert, J.P. (2021) — Differentiable Divergences Between Time Series

| Field | Value |
|-------|-------|
| Authors | Blondel, M., Mensch, A., Vert, J.P. |
| Year | 2021 |
| URL | [https://arxiv.org/abs/2201.12484](https://arxiv.org/abs/2201.12484) |
| Type | conference |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `metric.soft_dtw_div_self_1d` — Soft-DTW divergence distance matrix (self) for 1D data.
- `metric.soft_dtw_div_cross_1d` — Soft-DTW divergence cross distance.

---

#### Chen, L., Ng, R. (2004) — On The Marriage of Lp-norms and Edit Distance

| Field | Value |
|-------|-------|
| Authors | Chen, L., Ng, R. |
| Year | 2004 |
| DOI | `doi:10.1016/B978-012088469-8.50070-X` |
| URL | [https://doi.org/10.1016/B978-012088469-8.50070-X](https://doi.org/10.1016/B978-012088469-8.50070-X) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `erp_distance` | high |

---

#### Chen, L., Özsu, M.T., Oria, V. (2005) — Robust and fast similarity search for moving object trajectories

| Field | Value |
|-------|-------|
| Authors | Chen, L., Özsu, M.T., Oria, V. |
| Year | 2005 |
| DOI | `doi:10.1145/1066157.1066213` |
| URL | [https://doi.org/10.1145/1066157.1066213](https://doi.org/10.1145/1066157.1066213) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `edr_distance` | high |

---

#### Cuturi, M. (2011) — Fast global alignment kernels

| Field | Value |
|-------|-------|
| Authors | Cuturi, M. |
| Year | 2011 |
| URL | [https://icml.cc/2011/papers/489_icmlpaper.pdf](https://icml.cc/2011/papers/489_icmlpaper.pdf) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.gak` — Global Alignment Kernel between two 1-D time series.
- `metric.gak_gram_matrix` — Global Alignment Kernel Gram matrix (one-shot, symmetric).
- `metric.gak_gram_train` — Fit a GAK Gram handle for incremental train/predict computation.
- `metric.gak_gram_predict` — Compute the GAK Gram matrix between new data and the training set.
- `metric.sigma_gak` — Heuristic GAK bandwidth: median pairwise Euclidean distance, floored at 1e-8.
- `metric.PyGakGramTrain` — Opaque handle wrapping fdars-core GakGramTrain for incremental GAK Gram computation.
- `metric.gak_triangular` — Triangular Global Alignment Kernel (Cuturi 2011) between two 1-D series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `tslearn` | `gak` | high |
| R | `dtwclust` | `GAK` | high |

---

#### Cuturi, M., Blondel, M. (2017) — Soft-DTW: a differentiable loss function for time-series

| Field | Value |
|-------|-------|
| Authors | Cuturi, M., Blondel, M. |
| Year | 2017 |
| URL | [https://proceedings.mlr.press/v70/cuturi17a.html](https://proceedings.mlr.press/v70/cuturi17a.html) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.soft_dtw_self_1d` — Soft-DTW distance matrix (self) for 1D data.
- `metric.soft_dtw_cross_1d` — Soft-DTW cross distance for 1D data.
- `metric.soft_dtw_barycenter` — Soft-DTW barycenter of a set of curves (L-BFGS with random restarts).
- `metric.soft_dtw_alignment` — Soft-DTW value plus the expected alignment matrix (tslearn soft_dtw_alignment).
- `metric.soft_dtw_distance_windowed` — Soft-DTW value between two series under an optional global window.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `tslearn` | `soft_dtw` | high |

---

#### Herrmann, M., Webb, G.I. (2021) — Early abandoning and pruning for elastic distances including dynamic time warping

| Field | Value |
|-------|-------|
| Authors | Herrmann, M., Webb, G.I. |
| Year | 2021 |
| DOI | `doi:10.1007/s10618-021-00782-4` |
| URL | [https://doi.org/10.1007/s10618-021-00782-4](https://doi.org/10.1007/s10618-021-00782-4) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.dtw_distance_early_abandon` — Early-abandoning windowed DTW: the distance, or None once it must exceed `cutoff`.
- `metric.dtw_nearest_neighbor` — Exact 1-NN search under windowed DTW with a lower-bound cascade (UCR-suite style).
- `metric.dtw_k_nearest_neighbors` — Exact k-NN search under windowed DTW with a lower-bound cascade.

---

#### Herrmann, M., Webb, G.I. (2023) — Amercing: An intuitive and effective constraint for dynamic time warping

| Field | Value |
|-------|-------|
| Authors | Herrmann, M., Webb, G.I. |
| Year | 2023 |
| DOI | `doi:10.1016/j.patcog.2023.109333` |
| URL | [https://doi.org/10.1016/j.patcog.2023.109333](https://doi.org/10.1016/j.patcog.2023.109333) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `adtw_distance` | high |

---

#### Itakura, F. (1975) — Minimum prediction residual principle applied to speech recognition

| Field | Value |
|-------|-------|
| Authors | Itakura, F. |
| Year | 1975 |
| DOI | `doi:10.1109/TASSP.1975.1162641` |
| URL | [https://doi.org/10.1109/TASSP.1975.1162641](https://doi.org/10.1109/TASSP.1975.1162641) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.dtw_window_mask` — Boolean admissibility grid of a DTW global window for series lengths n and m.
- `metric.dtw_distance_windowed` — DTW distance between two series under an optional global window (O(m) memory).
- `metric.dtw_path` — DTW optimal warping path and accumulated cost under an optional global window.
- `metric.dtw_path_multivariate` — Dependent multichannel DTW optimal warping path and accumulated cost.
- `metric.dtw_distance_multivariate` — Dependent multichannel DTW distance between two (d, m) series.
- `metric.dtw_pairwise_distance_multivariate` — Pairwise dependent multichannel DTW distance matrix of a collection of series.

---

#### Jeong, Y.S., Jeong, M.K., Omitaomu, O.A. (2011) — Weighted dynamic time warping for time series classification

| Field | Value |
|-------|-------|
| Authors | Jeong, Y.S., Jeong, M.K., Omitaomu, O.A. |
| Year | 2011 |
| DOI | `doi:10.1016/j.patcog.2010.09.022` |
| URL | [https://doi.org/10.1016/j.patcog.2010.09.022](https://doi.org/10.1016/j.patcog.2010.09.022) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `wdtw_distance` | high |

---

#### Keogh, E. (2002) — Exact indexing of dynamic time warping

| Field | Value |
|-------|-------|
| Authors | Keogh, E. |
| Year | 2002 |
| DOI | `doi:10.1016/B978-155860869-6/50043-3` |
| URL | [https://doi.org/10.1016/B978-155860869-6/50043-3](https://doi.org/10.1016/B978-155860869-6/50043-3) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.lb_keogh` — LB_Keogh lower bound on the windowed DTW distance between a query and a candidate.
- `metric.lb_envelope` — LB_Keogh envelope of a series for a Sakoe-Chiba band of the given radius.
- `metric.lb_envelope_windowed` — LB_Keogh envelope of a candidate series under any DTW window, for a query length.
- `metric.dtw_nearest_neighbor` — Exact 1-NN search under windowed DTW with a lower-bound cascade (UCR-suite style).
- `metric.dtw_k_nearest_neighbors` — Exact k-NN search under windowed DTW with a lower-bound cascade.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `tslearn` | `lb_keogh` | high |
| R | `dtwclust` | `lb_keogh` | high |

---

#### Keogh, E.J., Pazzani, M.J. (2001) — Derivative Dynamic Time Warping

| Field | Value |
|-------|-------|
| Authors | Keogh, E.J., Pazzani, M.J. |
| Year | 2001 |
| DOI | `doi:10.1137/1.9781611972719.1` |
| URL | [https://doi.org/10.1137/1.9781611972719.1](https://doi.org/10.1137/1.9781611972719.1) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `ddtw_distance` | high |

---

#### Kim, S.W., Park, S., Chu, W.W. (2001) — An index-based approach for similarity search supporting time warping in large sequence databases

| Field | Value |
|-------|-------|
| Authors | Kim, S.W., Park, S., Chu, W.W. |
| Year | 2001 |
| DOI | `doi:10.1109/ICDE.2001.914875` |
| URL | [https://doi.org/10.1109/ICDE.2001.914875](https://doi.org/10.1109/ICDE.2001.914875) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.lb_kim` — LB_Kim lower bound on DTW from first / last / min / max features (O(1) after O(n)).

---

#### Lemire, D. (2009) — Faster retrieval with a two-pass dynamic-time-warping lower bound

| Field | Value |
|-------|-------|
| Authors | Lemire, D. |
| Year | 2009 |
| DOI | `doi:10.1016/j.patcog.2008.11.030` |
| URL | [https://doi.org/10.1016/j.patcog.2008.11.030](https://doi.org/10.1016/j.patcog.2008.11.030) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.lb_improved` — LB_Improved lower bound on windowed DTW (Lemire 2009), at least as tight as LB_Keogh.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `dtwclust` | `lb_improved` | high |

---

#### Marteau, P.F. (2009) — Time Warp Edit Distance with Stiffness Adjustment for Time Series Matching

| Field | Value |
|-------|-------|
| Authors | Marteau, P.F. |
| Year | 2009 |
| DOI | `doi:10.1109/TPAMI.2008.76` |
| URL | [https://doi.org/10.1109/TPAMI.2008.76](https://doi.org/10.1109/TPAMI.2008.76) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `twe_distance` | high |

---

#### Paparrizos, J., Gravano, L. (2015) — k-Shape: Efficient and Accurate Clustering of Time Series

| Field | Value |
|-------|-------|
| Authors | Paparrizos, J., Gravano, L. |
| Year | 2015 |
| DOI | `doi:10.1145/2723372.2737793` |
| URL | [https://doi.org/10.1145/2723372.2737793](https://doi.org/10.1145/2723372.2737793) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.sbd` — Shape-based distance (Paparrizos and Gravano 2015) and the optimal signed lag.
- `metric.sbd_distance_matrix` — Pairwise shape-based distance matrix of a set of curves.
- `clustering.kshape_fd` — k-Shape clustering of curves by shape-based distance (Paparrizos & Gravano 2015).
- `clustering.sbd_kmedoids` — k-medoids clustering of curves on the shape-based distance (SBD) matrix.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `tslearn` | `KShape` | high |
| R | `dtwclust` | `SBD` | high |

---

#### Petitjean, F., Ketterlin, A., Gançarski, P. (2011) — A global averaging method for dynamic time warping, with applications to clustering

| Field | Value |
|-------|-------|
| Authors | Petitjean, F., Ketterlin, A., Gançarski, P. |
| Year | 2011 |
| DOI | `doi:10.1016/j.patcog.2010.09.013` |
| URL | [https://doi.org/10.1016/j.patcog.2010.09.013](https://doi.org/10.1016/j.patcog.2010.09.013) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.dtw_barycenter_averaging` — DTW Barycenter Averaging (DBA, Petitjean et al. 2011) of a set of curves.
- `metric.dtw_barycenter_averaging_multivariate` — DTW Barycenter Averaging of multivariate (d, m) series (tslearn DBA on (n, sz, d) data).
- `clustering.dtw_kmeans` — DTW k-means clustering with DBA centroids (tslearn TimeSeriesKMeans(metric="dtw")).
- `clustering.dtw_kmeans_multivariate` — DTW k-means of multivariate (d, m) series with multivariate DBA centroids.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `tslearn` | `dtw_barycenter_averaging` | high |
| R | `dtwclust` | `DBA` | high |

---

#### Sakoe, H., Chiba, S. (1978) — Dynamic programming algorithm optimization for spoken word recognition

| Field | Value |
|-------|-------|
| Authors | Sakoe, H., Chiba, S. |
| Year | 1978 |
| DOI | `doi:10.1109/TASSP.1978.1163055` |
| URL | [https://ieeexplore.ieee.org/document/1163055](https://ieeexplore.ieee.org/document/1163055) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.dtw_self_1d` — DTW distance matrix (self) for 1D data.
- `metric.dtw_cross_1d` — DTW cross distance for 1D data.
- `metric.dtw_distance_windowed` — DTW distance between two series under an optional global window (O(m) memory).
- `metric.dtw_window_mask` — Boolean admissibility grid of a DTW global window for series lengths n and m.
- `metric.dtw_path` — DTW optimal warping path and accumulated cost under an optional global window.
- `metric.dtw_path_multivariate` — Dependent multichannel DTW optimal warping path and accumulated cost.
- `metric.dtw_distance_multivariate` — Dependent multichannel DTW distance between two (d, m) series.
- `metric.dtw_pairwise_distance_multivariate` — Pairwise dependent multichannel DTW distance matrix of a collection of series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `tslearn` | `dtw` | high |
| R | `dtw` | `dtw` | high |

---

#### Stefan, A., Athitsos, V., Das, G. (2013) — The Move-Split-Merge Metric for Time Series

| Field | Value |
|-------|-------|
| Authors | Stefan, A., Athitsos, V., Das, G. |
| Year | 2013 |
| DOI | `doi:10.1109/TKDE.2012.88` |
| URL | [https://doi.org/10.1109/TKDE.2012.88](https://doi.org/10.1109/TKDE.2012.88) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `msm_distance` | high |

---

#### Tan, C.W., Petitjean, F., Webb, G.I. (2019) — Elastic bands across the path: A new framework and method to lower bound DTW

| Field | Value |
|-------|-------|
| Authors | Tan, C.W., Petitjean, F., Webb, G.I. |
| Year | 2019 |
| DOI | `doi:10.1137/1.9781611975673.59` |
| URL | [https://doi.org/10.1137/1.9781611975673.59](https://doi.org/10.1137/1.9781611975673.59) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.lb_enhanced` — LB_Enhanced lower bound on windowed DTW (Tan et al. 2019) with v boundary bands.

---

#### Vlachos, M., Kollios, G., Gunopulos, D. (2002) — Discovering similar multidimensional trajectories

| Field | Value |
|-------|-------|
| Authors | Vlachos, M., Kollios, G., Gunopulos, D. |
| Year | 2002 |
| DOI | `doi:10.1109/ICDE.2002.994784` |
| URL | [https://doi.org/10.1109/ICDE.2002.994784](https://doi.org/10.1109/ICDE.2002.994784) |
| Type | conference |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `lcss_distance` | high |

---

#### Webb, G.I., Petitjean, F. (2021) — Tight lower bounds for dynamic time warping

| Field | Value |
|-------|-------|
| Authors | Webb, G.I., Petitjean, F. |
| Year | 2021 |
| DOI | `doi:10.1016/j.patcog.2021.107895` |
| URL | [https://doi.org/10.1016/j.patcog.2021.107895](https://doi.org/10.1016/j.patcog.2021.107895) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.lb_webb` — LB_Webb lower bound on windowed DTW (Webb and Petitjean 2021).

---

#### Zhao, J., Itti, L. (2018) — shapeDTW: Shape Dynamic Time Warping

| Field | Value |
|-------|-------|
| Authors | Zhao, J., Itti, L. |
| Year | 2018 |
| DOI | `doi:10.1016/j.patcog.2017.09.020` |
| URL | [https://doi.org/10.1016/j.patcog.2017.09.020](https://doi.org/10.1016/j.patcog.2017.09.020) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `metric.elastic_ts_distance` — Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
- `metric.elastic_ts_pairwise_distance` — Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
- `metric.elastic_ts_cost_matrix` — Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
- `metric.elastic_ts_alignment_path` — Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
- `metric.elastic_ts_distance_multivariate` — Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
- `metric.elastic_ts_pairwise_distance_multivariate` — Pairwise elastic-distance matrix of a collection of multivariate series.
- `metric.elastic_ts_cost_matrix_multivariate` — Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
- `metric.elastic_ts_alignment_path_multivariate` — Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `aeon` | `shape_dtw_distance` | high |

---

### fdars.outliers — Functional outlier detection — depth-based, magnitude, shape outliers

#### Arribas-Gil, A., Romo, J. (2014) — Shape outlier detection and visualization for functional data: the outliergram

| Field | Value |
|-------|-------|
| Authors | Arribas-Gil, A., Romo, J. |
| Year | 2014 |
| DOI | `doi:10.1093/biostatistics/kxu006` |
| URL | [https://academic.oup.com/biostatistics/article/15/4/603/2...](https://academic.oup.com/biostatistics/article/15/4/603/269095) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `outliers.outliergram` — Outliergram (MEI vs MBD plot).

---

#### Dai, W., Genton, M.G. (2019) — Directional outlyingness for multivariate functional data

| Field | Value |
|-------|-------|
| Authors | Dai, W., Genton, M.G. |
| Year | 2019 |
| DOI | `doi:10.1016/j.csda.2018.03.017` |
| URL | [https://www.sciencedirect.com/science/article/abs/pii/S01...](https://www.sciencedirect.com/science/article/abs/pii/S016794731830077X) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `outliers.magnitude_shape` — Magnitude-shape outlyingness.
- `outliers.muod` — MUOD (Massive Unsupervised Outlier Detection) for functional data.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdaoutlier` | `msplot` | high |

---

#### Febrero, M., Galeano, P., González-Manteiga, W. (2008) — Outlier detection in functional data by depth measures with application to identify abnormal NOx levels

| Field | Value |
|-------|-------|
| Authors | Febrero, M., Galeano, P., González-Manteiga, W. |
| Year | 2008 |
| DOI | `doi:10.1002/env.878` |
| URL | [https://onlinelibrary.wiley.com/doi/abs/10.1002/env.878](https://onlinelibrary.wiley.com/doi/abs/10.1002/env.878) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `outliers.detect_outliers_lrt` — LRT-based outlier detection with bootstrap.
- `outliers.detect_outliers_lrt_with_dist` — LRT-based outlier detection with bootstrap (returns threshold and null distribution).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fda.usc` | `foutliers` | high |

---

### fdars.pace_fpca — PACE: Principal Analysis by Conditional Expectation for sparse data

#### Ji, H., Müller, H.G. (2017) — Optimal Designs for Longitudinal and Functional Data

| Field | Value |
|-------|-------|
| Authors | Ji, H., Müller, H.G. |
| Year | 2017 |
| DOI | `doi:10.1111/rssb.12192` |
| URL | [https://doi.org/10.1111/rssb.12192](https://doi.org/10.1111/rssb.12192) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `pace_fpca.optimal_design` — Greedy optimal design: choose the work-grid points that best reduce a PACE criterion.
- `pace_fpca.design_criterion` — Score a set of design points (work-grid indices) against a fitted PACE model.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fdapace` | `FOptDes` | high |

---

#### Yao, F., Müller, H.G., Wang, J.L. (2005) — Functional data analysis for sparse longitudinal data

| Field | Value |
|-------|-------|
| Authors | Yao, F., Müller, H.G., Wang, J.L. |
| Year | 2005 |
| DOI | `doi:10.1198/016214504000001745` |
| URL | [https://www.tandfonline.com/doi/abs/10.1198/0162145040000...](https://www.tandfonline.com/doi/abs/10.1198/016214504000001745) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `pace_fpca.pace_fpca` — Run PACE FPCA on irregular/sparse functional data.
- `pace_fpca.irreg_fdata_from_lists` — Build an IrregFdata handle from two Python lists of ragged 1-D arrays.
- `pace_fpca.PyIrregFdata` — Opaque handle wrapping fdars-core IrregFdata for irregular/sparse functional data.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Matlab | `PACE` | `FPCA` | low |
| Python | `scikit-fda` | `FPCA` | high |
| R | `fdapace` | `PACE` | high |

---

### fdars.regression — Functional regression — scalar-on-function, function-on-scalar, GLM

#### Ferraty, F., Vieu, P. (2006) — Nonparametric Functional Data Analysis

| Field | Value |
|-------|-------|
| Authors | Ferraty, F., Vieu, P. |
| Year | 2006 |
| DOI | `doi:10.1007/0-387-36620-2` |
| URL | [https://link.springer.com/book/10.1007/0-387-36620-2](https://link.springer.com/book/10.1007/0-387-36620-2) |
| Type | book |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `regression.fregre_np` — Nonparametric kernel regression for functional data (from distance matrix).
- `regression.fregre_np_cv` — Cross-validated bandwidth selection for nonparametric functional regression.
- `regression.fregre_np_mixed` — Nonparametric functional regression mixing functional and scalar predictors.
- `classification.fclassif_kernel` — Kernel classification for functional data.
- `classification.kernel_classify_from_distances` — Kernel classification from a precomputed functional distance matrix.

---

#### Müller, H.G., Stadtmüller, U. (2005) — Generalized functional linear models

| Field | Value |
|-------|-------|
| Authors | Müller, H.G., Stadtmüller, U. |
| Year | 2005 |
| DOI | `doi:10.1214/009053604000001156` |
| URL | [https://projecteuclid.org/journals/annals-of-statistics/v...](https://projecteuclid.org/journals/annals-of-statistics/volume-33/issue-2/Generalized-functional-linear-models/10.1214/009053604000001156.full) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `regression.functional_logistic` — Functional logistic regression.
- `regression.functional_glm` — Functional generalised linear model (GLM) via FPC scores.
- `regression.predict_functional_logistic` — Predict probabilities for new data using a fitted functional logistic model.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `fda.usc` | `fregre.glm` | high |

---

#### Preda, C., Saporta, G. (2005) — PLS regression on a stochastic process

| Field | Value |
|-------|-------|
| Authors | Preda, C., Saporta, G. |
| Year | 2005 |
| DOI | `doi:10.1016/j.csda.2004.07.002` |
| URL | [https://www.sciencedirect.com/science/article/abs/pii/S01...](https://www.sciencedirect.com/science/article/abs/pii/S0167947304002208) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `regression.fpls` — Functional PLS (Partial Least Squares).
- `regression.fregre_pls` — Scalar-on-function PLS regression.
- `regression.predict_fregre_pls` — Predict new responses using a fitted PLS regression.
- `fts.fplsr` — Functional Partial Least Squares Regression (fPLSR) one-step-ahead forecast.

---

### fdars.scalar_on_function — Scalar-on-function regression with regularisation

#### Kundu, M.G., Harezlak, J., Randolph, T.W. (2016) — Longitudinal functional models with structured penalties

| Field | Value |
|-------|-------|
| Authors | Kundu, M.G., Harezlak, J., Randolph, T.W. |
| Year | 2016 |
| DOI | `doi:10.1177/1471082X15626291` |
| URL | [https://doi.org/10.1177/1471082X15626291](https://doi.org/10.1177/1471082X15626291) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `scalar_on_function.lpeer` — Longitudinal PEER: structured-penalty regression with a subject random intercept.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `refund` | `lpeer` | high |

---

#### Randolph, T.W., Harezlak, J., Feng, Z. (2012) — Structured penalties for functional linear models—partially empirical eigenvectors for regression

| Field | Value |
|-------|-------|
| Authors | Randolph, T.W., Harezlak, J., Feng, Z. |
| Year | 2012 |
| DOI | `doi:10.1214/12-EJS676` |
| URL | [https://doi.org/10.1214/12-EJS676](https://doi.org/10.1214/12-EJS676) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `scalar_on_function.peer` — PEER structured-penalty scalar-on-function regression with GCV / REML / fixed lambda.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `refund` | `peer` | high |

---

#### Reiss, P.T., Huo, L., Zhao, Y., Kelly, C., Ogden, R.T. (2015) — Wavelet-domain regression and predictive inference in psychiatric neuroimaging

| Field | Value |
|-------|-------|
| Authors | Reiss, P.T., Huo, L., Zhao, Y., Kelly, C., Ogden, R.T. |
| Year | 2015 |
| DOI | `doi:10.1214/15-AOAS829` |
| URL | [https://doi.org/10.1214/15-AOAS829](https://doi.org/10.1214/15-AOAS829) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `scalar_on_function.wcr` — Wavelet-domain scalar-on-function regression (PCR or PLS on DWT coefficients).

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `refund.wave` | `wcr` | high |

---

#### Zhao, Y., Ogden, R.T., Reiss, P.T. (2012) — Wavelet-based LASSO in functional linear regression

| Field | Value |
|-------|-------|
| Authors | Zhao, Y., Ogden, R.T., Reiss, P.T. |
| Year | 2012 |
| DOI | `doi:10.1080/10618600.2012.679241` |
| URL | [https://doi.org/10.1080/10618600.2012.679241](https://doi.org/10.1080/10618600.2012.679241) |
| Type | journal |
| Status | Curated |

**Callables implementing this method:**

- `scalar_on_function.wnet` — Wavelet-domain elastic-net scalar-on-function regression with cross-validated lambda.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `refund.wave` | `wnet` | high |

---

### fdars.shapelet — Functional shapelets — pattern-based classification and feature learning

#### Ye, L., Keogh, E. (2009) — Time series shapelets: a new primitive for data mining

| Field | Value |
|-------|-------|
| Authors | Ye, L., Keogh, E. |
| Year | 2009 |
| DOI | `doi:10.1145/1557019.1557122` |
| URL | [https://dl.acm.org/doi/10.1145/1557019.1557122](https://dl.acm.org/doi/10.1145/1557019.1557122) |
| Type | conference |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `shapelet.discover_shapelets` — Discover shapelets in labeled functional data and return a summary dict.
- `shapelet.shapelet_transform_fit` — Fit a shapelet transform on labeled functional data.
- `shapelet.shapelet_transform` — Apply a fitted shapelet transform to new functional data.
- `shapelet.shapelet_distance` — Compute the shapelet distance between a z-normalized shapelet and a series.
- `shapelet.shapelet_classifier_fit` — Fit a shapelet-based classifier on labeled functional data.
- `shapelet.PyShapeletFit` — Opaque handle wrapping fdars-core ShapeletTransformFit.
- `shapelet.PyShapeletClassifierFit` — Opaque handle wrapping fdars-core ShapeletClassifierFit.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| Python | `sktime` | `ShapeletTransform` | high |

---

### fdars.smoothing — Functional smoothing — kernel, basis, and roughness-penalised methods

#### Craven, P., Wahba, G. (1979) — Smoothing noisy data with spline functions

| Field | Value |
|-------|-------|
| Authors | Craven, P., Wahba, G. |
| Year | 1979 |
| DOI | `doi:10.1007/BF01404567` |
| URL | [https://link.springer.com/article/10.1007/BF01404567](https://link.springer.com/article/10.1007/BF01404567) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `smoothing.gcv_smoother` — GCV score for a kernel smoother.
- `smoothing.optim_bandwidth` — Optimal bandwidth selection via cross-validation.

---

#### Nadaraya, E.A., Watson, G.S. (1964) — On Estimating Regression (Nadaraya); Smooth Regression Analysis (Watson)

| Field | Value |
|-------|-------|
| Authors | Nadaraya, E.A., Watson, G.S. |
| Year | 1964 |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `smoothing.nadaraya_watson` — Nadaraya-Watson kernel smoother.

---

### fdars.spm — Statistical process monitoring — T2, SPE, control charts

#### Happ, C., Greven, S. (2018) — Multivariate functional principal component analysis for data observed on different (dimensional) domains

| Field | Value |
|-------|-------|
| Authors | Happ, C., Greven, S. |
| Year | 2018 |
| DOI | `doi:10.1080/01621459.2016.1273115` |
| URL | [https://www.tandfonline.com/doi/abs/10.1080/01621459.2016...](https://www.tandfonline.com/doi/abs/10.1080/01621459.2016.1273115) |
| Type | journal |
| Status | Pending DOI verification |

**Callables implementing this method:**

- `spm.mfpca` — Multivariate Functional Principal Component Analysis (MFPCA).
- `multi_fdata.PyMultiFunData` — Opaque handle wrapping fdars-core MultiFunData for multi-domain functional data.
- `multi_fdata.multi_fdata_from_components` — Build a PyMultiFunData handle from lists of 2-D data arrays and 1-D argvals vectors.

**Cross-language implementations:**

| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `MFPCA` | `MFPCA` | high |

---

### fdars.tolerance — Functional tolerance bands — simultaneous and pointwise coverage

#### Adams, J., Berman, B., Michalenko, J., Tucker, J.D. (2025) — Conformal Anomaly Detection for Functional Data with Elastic Distance Metrics

| Field | Value |
|-------|-------|
| Authors | Adams, J., Berman, B., Michalenko, J., Tucker, J.D. |
| Year | 2025 |
| URL | [https://arxiv.org/abs/2504.01172](https://arxiv.org/abs/2504.01172) |
| Type | preprint |
| Status | Curated |

**Callables implementing this method:**

- `tolerance.elastic_conformal_anomaly` — Inductive conformal anomaly detection with elastic amplitude / phase nonconformity scores.
- `tolerance.elastic_nonconformity` — Elastic nonconformity score of one curve against a template.

---

#### Vovk, V., Gammerman, A., Shafer, G. (2005) — Algorithmic Learning in a Random World

| Field | Value |
|-------|-------|
| Authors | Vovk, V., Gammerman, A., Shafer, G. |
| Year | 2005 |
| DOI | `doi:10.1007/b106715` |
| URL | [https://doi.org/10.1007/b106715](https://doi.org/10.1007/b106715) |
| Type | book |
| Status | Curated |

**Callables implementing this method:**

- `tolerance.elastic_conformal_anomaly` — Inductive conformal anomaly detection with elastic amplitude / phase nonconformity scores.

---
