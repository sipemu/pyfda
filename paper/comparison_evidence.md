# Comparison Evidence

**Generated:** 2026-09-08
**Access date (all URLs):** 2026-09-08

---

## scikit-fda

- **Package:** scikit-fda
- **Version:** 0.10.1
- **Registry:** PyPI
- **Source URL:** https://pypi.org/project/scikit-fda/
- **Release date:** 2025-04-04
- **Paper:** arXiv:2211.02566 (Ramos-Carreño et al., 2023)
- **Docs:** https://fda.readthedocs.io/en/stable/
- Spot-checked: YES (PyPI JSON API, 2026-09-08)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | FDataGrid (discretized), FDataBasis (basis expansion: BSpline, Fourier, Monomial, Constant); BasisSmoother, NadarayaWatsonSmoother, LocalLinearRegressionSmoother, KNeighborsSmoother; GCV/LOO-CV bandwidth selection | arXiv:2211.02566 §2–3.3.1 |
| Registration / alignment | ✓ | LeastSquaresShiftRegistration, FisherRaoElasticRegistration (SRSF), landmark_elastic_registration, landmark_shift_registration | arXiv:2211.02566 §3.3.2; https://fda.readthedocs.io/en/latest/modules/preprocessing/registration.html |
| Depth & outlier detection | ✓ | IntegratedDepth, BandDepth, ModifiedBandDepth; BoxplotOutlierDetector, MSPlotOutlierDetector | arXiv:2211.02566 §3 |
| FPCA / covariance / PACE sparse FPCA | partial | Paper §3.3.3: FPCA class; dense FPCA only — no PACE sparse FPCA found in scikit-fda docs | arXiv:2211.02566 §3.3.3; https://fda.readthedocs.io/en/stable/apilist.html |
| Clustering | ✓ | API listing: KMeans, FuzzyCMeans, AgglomerativeClustering | arXiv:2211.02566 §3; https://fda.readthedocs.io/en/stable/apilist.html |
| Classification | ✓ | Paper §3 + API: KNeighborsClassifier, LogisticRegression, QDA, MaximumDepthClassifier, NearestCentroid | arXiv:2211.02566 §3; https://fda.readthedocs.io/en/stable/apilist.html |
| Functional regression (SoF / FoF) | ✓ | skfda.ml.regression exports LinearRegression (docstring: "Linear regression with multivariate and functional response": scalar-on-function, function-on-scalar, concurrent), HistoricalLinearRegression (docstring: "a linear regression method where the covariate and the response are both functions" — historical function-on-function), KernelRegression, FPCARegression, FPLSRegression, KNeighborsRegressor. No unrestricted full-surface function-on-function model (cf. refund::pffr) | scikit_fda-0.10.1 wheel, skfda/ml/regression/__init__.py and class docstrings (inspected 2026-09-24) |
| Functional time series | — | Not found in paper or API listing; no fts module | https://fda.readthedocs.io/en/stable/apilist.html |
| Statistical process monitoring | — | Not found in paper or API listing | https://fda.readthedocs.io/en/stable/apilist.html |
| Inference / hypothesis testing | partial | API: ANOVA (one-way), Hotelling T²; limited compared to full inference suite | arXiv:2211.02566 §3; https://fda.readthedocs.io/en/stable/apilist.html |
| Conformal prediction & tolerance bands | — | Not found in paper or API listing | https://fda.readthedocs.io/en/stable/apilist.html |
| Density / Frechet (object-valued data) | — | No density-FDA or Fréchet analysis found. (Distance metrics exist in `skfda.misc.metrics`, but this row covers object-valued data, not pairwise distances.) | https://fda.readthedocs.io/en/stable/apilist.html |
| Simulation & datasets | ✓ | Paper §3.1: make_gaussian_process, make_multimodal_samples; fetch_phoneme, fetch_growth, fetch_weather, fetch_cran, fetch_ucr | arXiv:2211.02566 §3.1 |
| Grounded advisor + scientific provenance | — | No grounded parameter advisor or scientific-provenance layer in scikit-fda | arXiv:2211.02566; https://fda.readthedocs.io/en/stable/ |

---

## FDApy

- **Package:** FDApy
- **Version:** 1.0.3
- **Registry:** PyPI
- **Source URL:** https://pypi.org/project/FDApy/
- **Release date:** 2025-02-25
- **Paper:** Golovkine (2025), Journal of Open Source Software 10(107):7526, doi:10.21105/joss.07526 (preprint arXiv:2101.11003)
- **Docs:** https://fdapy.readthedocs.io/en/stable/
- Spot-checked: YES (PyPI JSON API, 2026-09-08)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | Docs: grid and basis representations; dense and irregular sampling; smoothing methods | https://fdapy.readthedocs.io/en/stable/ |
| Registration / alignment | — | Not mentioned in paper abstract, docs landing page, or known API; not found | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| Depth & outlier detection | — | Not mentioned in paper abstract or docs | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| FPCA / covariance / PACE sparse FPCA | ✓ | Paper: "(multivariate) functional principal component analysis" explicitly for dense and irregular data; dimension reduction core feature | arXiv:2101.11003 |
| Clustering | — | FDApy 1.0.3 wheel contains no clustering module (only misc, preprocessing/{dim_reduction,smoothing}, representation, simulation, visualization); "clustering" is listed in the lazy-loader of FDApy/__init__.py but not shipped. (The scikit-fda paper, arXiv:2211.02566 p.2, describes an older FDApy.) | https://pypi.org/project/FDApy/1.0.3/ (wheel inspected 2026-09-24) |
| Classification | — | Not confirmed in paper or docs | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| Functional regression (SoF / FoF) | — | Not confirmed in paper or docs | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| Functional time series | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Statistical process monitoring | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Inference / hypothesis testing | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Conformal prediction & tolerance bands | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Density / Frechet (object-valued data) | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Simulation & datasets | ✓ | Docs: "large simulation toolbox, based on basis decomposition" | https://fdapy.readthedocs.io/en/stable/ |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://fdapy.readthedocs.io/en/stable/ |

---

## fda 6.3.0

- **Package:** fda (R)
- **Version:** 6.3.0
- **Registry:** CRAN
- **Source URL:** https://cran.r-project.org/web/packages/fda/index.html
- **Release date:** 2025-05-21
- **Reference:** Ramsay, J.O. and Silverman, B.W. (2005). Functional Data Analysis. Springer.
- Spot-checked: YES (CRAN index + fda reference manual PDF, 2026-09-09)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | CRAN: "functions for smoothing, plotting and simple regression models"; B-spline, Fourier, polynomial basis | https://cran.r-project.org/web/packages/fda/index.html |
| Registration / alignment | ✓ | fda reference manual: register.fd / landmarkreg — landmark and continuous registration (Ramsay & Silverman (2005), ch. 7); shift and warping | https://cran.r-project.org/web/views/FunctionalData.html; https://cran.r-project.org/web/packages/fda/fda.pdf |
| Depth & outlier detection | partial | Functional boxplot included; depth measures limited compared to fda.usc; "functional boxplot for descriptives and outlier detection" | https://cran.r-project.org/web/views/FunctionalData.html |
| FPCA / covariance / PACE sparse FPCA | ✓ | fda reference manual: pca.fd — FPCA on functional objects; covariance surface; no PACE sparse FPCA (PACE implemented via fdapace, not fda) | https://cran.r-project.org/web/views/FunctionalData.html; https://cran.r-project.org/web/packages/fda/fda.pdf |
| Clustering | — | Not a primary feature of fda package; clustering attributed to other packages | https://cran.r-project.org/web/views/FunctionalData.html |
| Classification | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional regression (SoF / FoF) | partial | CRAN: "simple regression models"; scalar-on-function via basis; advanced regression in refund | https://cran.r-project.org/web/packages/fda/index.html |
| Functional time series | — | Not found in fda package | https://cran.r-project.org/web/packages/fda/index.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/packages/fda/index.html |
| Inference / hypothesis testing | partial | Exports Fperm.fd (permutation F-test for functional linear models) and tperm.fd (permutation t-test for two groups of functional data) | ls("package:fda") on fda 6.3.0 |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/packages/fda/index.html |
| Density / Frechet (object-valued data) | — | Not found | https://cran.r-project.org/web/packages/fda/index.html |
| Simulation & datasets | ✓ | CRAN: "data sets and script files working many examples including all but one of the 76 figures" | https://cran.r-project.org/web/packages/fda/index.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://cran.r-project.org/web/packages/fda/index.html |

---

## fda.usc

- **Package:** fda.usc (R)
- **Version:** 2.2.0
- **Registry:** CRAN
- **Source URL:** https://cran.r-project.org/web/packages/fda.usc/index.html
- **Release date:** 2024-11-09
- **Paper:** Febrero-Bande M. and Oviedo de la Fuente M. (2012). Journal of Statistical Software 51(4):1–28.
- Spot-checked: YES (CRAN index page fetched, 2026-09-08)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | Package description: "definition, transformation, and representation of functional datasets through derivatives, kernel methods, and basis representations" | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Registration / alignment | — | Not mentioned in package description or task view entry for fda.usc; registration attributed to fda and fdasrvf | https://cran.r-project.org/web/views/FunctionalData.html |
| Depth & outlier detection | ✓ | Package description: "depth measurements, atypical curves detection"; multiple depth methods (FM, mode, RP, RT, RPD); outliers.lrt, outliers.depth.pond | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| FPCA / covariance / PACE sparse FPCA | partial | FPCA available (mentioned in regression methods); not the primary focus; covariance estimation present | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Clustering | partial | Package: "k-means" functional clustering; limited | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Classification | ✓ | Package: "supervised classification" — k-NN, kernel, depth-based classifiers, k-fold CV | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Functional regression (SoF / FoF) | ✓ | Package: "functional regression models with a scalar response" via PCA, PLS, basis expansion, nonparametric; GLM, GAM extensions; F-tests | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Functional time series | — | Not found in package description | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Statistical process monitoring | — | Not found | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Inference / hypothesis testing | ✓ | fda.usc 2.2.0 exports cov.test.fdata, dcor.test, dfv.test, fanova.hetero, fanova.onefactor, fanova.RPm, fdata.bootstrap, fEqDistrib.test, flm.Ftest, flm.test, fmean.test.fdata, fregre.bootstrap, MMD.test, MMDA.test, rp.flm.test, XYRP.test | ls("package:fda.usc") on fda.usc 2.2.0 |
| Conformal prediction & tolerance bands | — | Not found | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Density / Frechet (object-valued data) | — | No density-FDA or Fréchet analysis found. (`metric.lp` and the `semimetric.*` family provide distances, which this row does not cover.) | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Simulation & datasets | partial | Datasets included; simulation methods not the primary focus | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |

---

## refund

- **Package:** refund (R)
- **Version:** 0.1-40
- **Registry:** CRAN
- **Source URL:** https://cran.r-project.org/web/packages/refund/index.html
- **Release date:** 2026-03-21
- **Key functions:** pfr (scalar-on-function), pffr (function-on-function), fpca.sc, fpca.face
- Spot-checked: NO (spot-check satisfied by fda.usc above)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | partial | Basis representations used internally for regression; not a primary standalone smoothing package | https://cran.r-project.org/web/packages/refund/index.html |
| Registration / alignment | — | Not a focus of refund | https://cran.r-project.org/web/packages/refund/index.html |
| Depth & outlier detection | — | Not found | https://cran.r-project.org/web/packages/refund/index.html |
| FPCA / covariance / PACE sparse FPCA | ✓ | Package: fpca.sc (smoothed FPCA), fpca.face, fpca.ssvd, fpca2s, mfpca.sc (multilevel FPCA), fpca.lfda (longitudinal) | https://rdrr.io/cran/refund/ |
| Clustering | — | Not a focus of refund | https://cran.r-project.org/web/packages/refund/index.html |
| Classification | — | Not a focus of refund | https://cran.r-project.org/web/packages/refund/index.html |
| Functional regression (SoF / FoF) | ✓ | Package description: "Methods for regression for functional data, including function-on-scalar, scalar-on-function, and function-on-function regression"; pfr, pffr, fgam, peer, fpcr | https://cran.r-project.org/web/packages/refund/index.html |
| Functional time series | — | Not found | https://cran.r-project.org/web/packages/refund/index.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/packages/refund/index.html |
| Inference / hypothesis testing | partial | Inference within regression models (Wald tests, confidence bands); not standalone hypothesis testing module | https://cran.r-project.org/web/packages/refund/index.html |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/packages/refund/index.html |
| Density / Frechet (object-valued data) | — | Not found | https://cran.r-project.org/web/packages/refund/index.html |
| Simulation & datasets | partial | Some datasets bundled; no dedicated simulation toolbox | https://cran.r-project.org/web/packages/refund/index.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://cran.r-project.org/web/packages/refund/index.html |

---

## funData

- **Package:** funData (R)
- **Version:** 1.3-9
- **Registry:** CRAN
- **Source URL:** https://cran.r-project.org/web/packages/funData/index.html
- **Release date:** 2024-02-14
- **Paper:** Happ-Kurz C. (2020). Journal of Statistical Software 93(5):1–38.
- Spot-checked: NO (combined dossier with tidyfun; spot-check satisfied by fda.usc)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | funData: "S4 classes for univariate and multivariate functional data and utility functions"; tidyfun: tf S3 vectors with smoothing support | https://cran.r-project.org/web/packages/funData/index.html; https://cran.r-project.org/web/views/FunctionalData.html |
| Registration / alignment | ✓ | tf 0.5.0 (attached by tidyfun, which Depends: tf (>= 0.5.0)) exports tf_register (method = "srvf", "srvf_mv", "cc", "affine", "landmark"), tf_register_shape (elastic shape registration), tf_estimate_warps, tf_warp | tf 0.5.0 NAMESPACE and man/tf_register.Rd (CRAN tarball); https://cran.r-project.org/package=tf |
| Depth & outlier detection | partial | tf 0.5.0 exports tf_depth (depth = "MBD", "MHI", "FM", "FSD", "RPD") and tf_fmedian; tidyfun 0.2.0 exports geom_fboxplot / stat_fboxplot (functional boxplots); no dedicated outlier-detection procedures | tf 0.5.0 and tidyfun 0.2.0 NAMESPACE, tf man/tf_depth.Rd (CRAN tarballs) |
| FPCA / covariance / PACE sparse FPCA | partial | funData works with companion MFPCA package (separate package); not built-in | https://cran.r-project.org/web/packages/funData/index.html |
| Clustering | — | Not a feature of funData or tidyfun | https://cran.r-project.org/web/views/FunctionalData.html |
| Classification | — | Not a feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional regression (SoF / FoF) | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional time series | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Inference / hypothesis testing | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Density / Frechet (object-valued data) | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Simulation & datasets | ✓ | funData exports simFunData, simMultiFunData; tf exports tf_rgp (Gaussian-process samples); datasets: tf (growth, gait, pinch), tidyfun (chf_df, dti_df) | funData 1.3-9, tf 0.5.0, tidyfun 0.2.0 NAMESPACE and data/ (CRAN tarballs) |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://cran.r-project.org/web/packages/funData/index.html |

---

## tidyfun

- **Package:** tidyfun (R)
- **Version:** 0.2.0
- **Registry:** CRAN
- **Source URL:** https://cran.r-project.org/web/packages/tidyfun/index.html
- **Release date:** 2026-07-16
- **Companion:** tf 0.5.0 (CRAN, 2026-07-14), attached via Depends: tf (>= 0.5.0); supplies depth, registration and simulation functions
- Spot-checked: NO (combined dossier with funData; spot-check satisfied by fda.usc)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | tidyfun: tf S3 vectors with smoothing support; funData: "S4 classes for univariate and multivariate functional data and utility functions" | https://cran.r-project.org/web/packages/tidyfun/index.html; https://cran.r-project.org/web/views/FunctionalData.html |
| Registration / alignment | ✓ | tf 0.5.0 (attached by tidyfun, which Depends: tf (>= 0.5.0)) exports tf_register (method = "srvf", "srvf_mv", "cc", "affine", "landmark"), tf_register_shape (elastic shape registration), tf_estimate_warps, tf_warp | tf 0.5.0 NAMESPACE and man/tf_register.Rd (CRAN tarball); https://cran.r-project.org/package=tf |
| Depth & outlier detection | partial | tf 0.5.0 exports tf_depth (depth = "MBD", "MHI", "FM", "FSD", "RPD") and tf_fmedian; tidyfun 0.2.0 exports geom_fboxplot / stat_fboxplot (functional boxplots); no dedicated outlier-detection procedures | tf 0.5.0 and tidyfun 0.2.0 NAMESPACE, tf man/tf_depth.Rd (CRAN tarballs) |
| FPCA / covariance / PACE sparse FPCA | partial | funData works with companion MFPCA package (separate package); not built-in | https://cran.r-project.org/web/packages/funData/index.html |
| Clustering | — | Not a feature of funData or tidyfun | https://cran.r-project.org/web/views/FunctionalData.html |
| Classification | — | Not a feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional regression (SoF / FoF) | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional time series | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Inference / hypothesis testing | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Density / Frechet (object-valued data) | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Simulation & datasets | ✓ | funData exports simFunData, simMultiFunData; tf exports tf_rgp (Gaussian-process samples); datasets: tf (growth, gait, pinch), tidyfun (chf_df, dti_df) | funData 1.3-9, tf 0.5.0, tidyfun 0.2.0 NAMESPACE and data/ (CRAN tarballs) |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://cran.r-project.org/web/packages/tidyfun/index.html |

---

## fdaM

- **Package:** fdaM (MATLAB)
- **Platform:** MATLAB
- **Version:** fdaM.zip dated 2017-08-08 (no versioned registry; newest archive members modified 2017-08-01)
- **Source URL:** https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/
- **Maintenance:** Low — no release since the 2017-08-08 archive; not actively developed
- Spot-checked: NO (historical MATLAB tool; no live registry)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | fdaM: basis-expansion framework mirroring R fda; B-spline, Fourier (create_bspline_basis.m, create_fourier_basis.m, smooth_basis.m) | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/fdaM.zip |
| Registration / alignment | ✓ | fdaM: landmark and continuous registration following Ramsay & Silverman (landmarkreg.m, register_fd.m) | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/fdaM.zip |
| Depth & outlier detection | — | Not a focus of either fdaM or PACE | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| FPCA / covariance / PACE sparse FPCA | ✓ | PACE: "Functional Principal Component Analysis (FPCA)...for sparsely or densely sampled random trajectories" — the defining capability | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Clustering | partial | PACE item (14): "Generalized functional distances for sparsely sampled functional data, which can be used for functional clustering and other distance-based applications"; no dedicated clustering routine | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Classification | partial | PACE item (8): generalized functional linear regression "can also be used for classification of functional data via binary regression (PACE-GLM)"; no dedicated classifiers | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Functional regression (SoF / FoF) | ✓ | PACE item (3): "Functional linear regression ... for cases where the predictor is a random function and the response is a scalar or a random function (PACE-REG)"; items (9), (10), (17): quadratic, additive (FAM) and quantile functional regression; fdaM: fRegress.m, fRegress_CV.m, linmod.m ("Fits an unrestricted or full functional linear model") | https://anson.ucdavis.edu/~mueller/data/pace.html; https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/fdaM.zip |
| Functional time series | — | Not found as a dedicated module | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Statistical process monitoring | — | Not found | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Inference / hypothesis testing | partial | fdaM: Fperm_fd.m, tperm_fd.m (permutation F- and t-tests); PACE item (4): "Diagnostics and bootstrap inference for functional linear regression (PACE-REG)"; no general testing suite | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/fdaM.zip; https://anson.ucdavis.edu/~mueller/data/pace.html |
| Conformal prediction & tolerance bands | — | Not found | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Density / Frechet (object-valued data) | — | Not found | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Simulation & datasets | partial | fdaM: datasets from Ramsay & Silverman textbook; PACE: limited simulation | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/; https://anson.ucdavis.edu/~mueller/data/pace.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |

---

## PACE

- **Package:** PACE (MATLAB); R port: fdapace 0.6.0
- **Platform:** MATLAB (primary); R port
- **Version:** MATLAB PACE v2.17 (June 2015); R port fdapace 0.6.0 (2024-07-03)
- **Source URL:** https://anson.ucdavis.edu/~mueller/data/pace.html
- **R port URL:** https://cran.r-project.org/web/packages/fdapace/index.html
- Spot-checked: NO (historical MATLAB tool; R port URL confirmed)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | PACE item (1): "Fitting of both sparsely and densely sampled random functions from noisy measurements by Functional Principal Component Analysis (FPCA)" — FPCA-based representation with local-linear smoothing | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Registration / alignment | ✓ | PACE item (13): "Time-synchronization based on pairwise warping (alignment, registration) for both sparsely and densely sampled functions (PACE-WARP)" | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Depth & outlier detection | — | Not a focus of either fdaM or PACE | https://anson.ucdavis.edu/~mueller/data/pace.html |
| FPCA / covariance / PACE sparse FPCA | ✓ | PACE: "Functional Principal Component Analysis (FPCA)...for sparsely or densely sampled random trajectories" — the defining capability | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Clustering | partial | PACE item (14): "Generalized functional distances for sparsely sampled functional data, which can be used for functional clustering and other distance-based applications"; no dedicated clustering routine | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Classification | partial | PACE item (8): generalized functional linear regression "can also be used for classification of functional data via binary regression (PACE-GLM)"; no dedicated classifiers | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Functional regression (SoF / FoF) | ✓ | PACE item (3): "Functional linear regression ... for cases where the predictor is a random function and the response is a scalar or a random function (PACE-REG)"; items (9), (10), (17): quadratic, additive (FAM) and quantile functional regression; fdaM: fRegress.m, fRegress_CV.m, linmod.m ("Fits an unrestricted or full functional linear model") | https://anson.ucdavis.edu/~mueller/data/pace.html; https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/fdaM.zip |
| Functional time series | — | Not found as a dedicated module | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Statistical process monitoring | — | Not found | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Inference / hypothesis testing | partial | fdaM: Fperm_fd.m, tperm_fd.m (permutation F- and t-tests); PACE item (4): "Diagnostics and bootstrap inference for functional linear regression (PACE-REG)"; no general testing suite | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/fdaM.zip; https://anson.ucdavis.edu/~mueller/data/pace.html |
| Conformal prediction & tolerance bands | — | Not found | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Density / Frechet (object-valued data) | — | Not found | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Simulation & datasets | partial | fdaM: datasets from Ramsay & Silverman textbook; PACE: limited simulation | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://anson.ucdavis.edu/~mueller/data/pace.html |
