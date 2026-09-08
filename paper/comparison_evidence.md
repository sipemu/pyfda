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
| Functional regression (SoF / FoF) | partial | API: LinearRegression, FPCARegression, FPLSRegression; scalar-on-function present; function-on-function not confirmed in API listing — resolving down | arXiv:2211.02566 §3; https://fda.readthedocs.io/en/stable/apilist.html |
| Functional time series | — | Not found in paper or API listing; no fts module | https://fda.readthedocs.io/en/stable/apilist.html |
| Statistical process monitoring | — | Not found in paper or API listing | https://fda.readthedocs.io/en/stable/apilist.html |
| Inference / hypothesis testing | partial | API: ANOVA (one-way), Hotelling T²; limited compared to full inference suite | arXiv:2211.02566 §3; https://fda.readthedocs.io/en/stable/apilist.html |
| Conformal prediction & tolerance bands | — | Not found in paper or API listing | https://fda.readthedocs.io/en/stable/apilist.html |
| Density / Frechet / metric-space | — | Not found in paper or API listing | https://fda.readthedocs.io/en/stable/apilist.html |
| Simulation & datasets | ✓ | Paper §3.1: make_gaussian_process, make_multimodal_samples; fetch_phoneme, fetch_growth, fetch_weather, fetch_cran, fetch_ucr | arXiv:2211.02566 §3.1 |
| Grounded advisor + scientific provenance | — | No grounded parameter advisor or scientific-provenance layer in scikit-fda | arXiv:2211.02566; https://fda.readthedocs.io/en/stable/ |

---

## FDApy

- **Package:** FDApy
- **Version:** 1.0.3
- **Registry:** PyPI
- **Source URL:** https://pypi.org/project/FDApy/
- **Release date:** 2025-02-25
- **Paper:** arXiv:2101.11003 (Golovkine, 2021/2024)
- **Docs:** https://fdapy.readthedocs.io/en/stable/
- Spot-checked: YES (PyPI JSON API, 2026-09-08)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | Docs: grid and basis representations; dense and irregular sampling; smoothing methods | https://fdapy.readthedocs.io/en/stable/ |
| Registration / alignment | — | Not mentioned in paper abstract, docs landing page, or known API; not found | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| Depth & outlier detection | — | Not mentioned in paper abstract or docs | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| FPCA / covariance / PACE sparse FPCA | ✓ | Paper: "(multivariate) functional principal component analysis" explicitly for dense and irregular data; dimension reduction core feature | arXiv:2101.11003 |
| Clustering | partial | scikit-fda paper cites FDApy "provides methods for principal component analysis and clustering"; partial — not primary focus, citation is indirect | arXiv:2211.02566 p.2 |
| Classification | — | Not confirmed in paper or docs | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| Functional regression (SoF / FoF) | — | Not confirmed in paper or docs | https://fdapy.readthedocs.io/en/stable/; arXiv:2101.11003 |
| Functional time series | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Statistical process monitoring | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Inference / hypothesis testing | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Conformal prediction & tolerance bands | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
| Density / Frechet / metric-space | — | Not confirmed | https://fdapy.readthedocs.io/en/stable/ |
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
- Spot-checked: NO (spot-check satisfied by fda.usc below)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | CRAN: "functions for smoothing, plotting and simple regression models"; B-spline, Fourier, polynomial basis | https://cran.r-project.org/web/packages/fda/index.html |
| Registration / alignment | ✓ | CRAN task view: "landmark-based" registration supported; shift and warping | https://cran.r-project.org/web/views/FunctionalData.html |
| Depth & outlier detection | partial | Functional boxplot included; depth measures limited compared to fda.usc; "functional boxplot for descriptives and outlier detection" | https://cran.r-project.org/web/views/FunctionalData.html |
| FPCA / covariance / PACE sparse FPCA | ✓ | CRAN task view: FPCA support; covariance surface; no PACE sparse FPCA (PACE implemented via fdapace, not fda) | https://cran.r-project.org/web/views/FunctionalData.html |
| Clustering | — | Not a primary feature of fda package; clustering attributed to other packages | https://cran.r-project.org/web/views/FunctionalData.html |
| Classification | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional regression (SoF / FoF) | partial | CRAN: "simple regression models"; scalar-on-function via basis; advanced regression in refund | https://cran.r-project.org/web/packages/fda/index.html |
| Functional time series | — | Not found in fda package | https://cran.r-project.org/web/packages/fda/index.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/packages/fda/index.html |
| Inference / hypothesis testing | partial | F-tests for functional linear models; limited | https://cran.r-project.org/web/packages/fda/index.html |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/packages/fda/index.html |
| Density / Frechet / metric-space | — | Not found | https://cran.r-project.org/web/packages/fda/index.html |
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
| Inference / hypothesis testing | partial | F-tests and goodness-of-fit for functional linear models; ANOVA; limited scope | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Conformal prediction & tolerance bands | — | Not found | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
| Density / Frechet / metric-space | — | Not found | https://rdrr.io/cran/fda.usc/man/fda.usc-package.html |
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
| Density / Frechet / metric-space | — | Not found | https://cran.r-project.org/web/packages/refund/index.html |
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
| Registration / alignment | partial | tidyfun/tf: "registration" mentioned in CRAN task view description of tf; not a primary focus | https://cran.r-project.org/web/views/FunctionalData.html |
| Depth & outlier detection | — | Not a primary feature of either package; depth attributed to fda.usc, fdaoutlier | https://cran.r-project.org/web/views/FunctionalData.html |
| FPCA / covariance / PACE sparse FPCA | partial | funData works with companion MFPCA package (separate package); not built-in | https://cran.r-project.org/web/packages/funData/index.html |
| Clustering | — | Not a feature of funData or tidyfun | https://cran.r-project.org/web/views/FunctionalData.html |
| Classification | — | Not a feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional regression (SoF / FoF) | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional time series | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Inference / hypothesis testing | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Density / Frechet / metric-space | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Simulation & datasets | partial | funData: utility simulation via MFPCA; tidyfun: limited | https://cran.r-project.org/web/packages/funData/index.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://cran.r-project.org/web/packages/funData/index.html |

---

## tidyfun

- **Package:** tidyfun (R)
- **Version:** 0.2.0
- **Registry:** CRAN
- **Source URL:** https://cran.r-project.org/web/packages/tidyfun/index.html
- **Release date:** 2026-07-16
- Spot-checked: NO (combined dossier with funData; spot-check satisfied by fda.usc)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | tidyfun: tf S3 vectors with smoothing support; funData: "S4 classes for univariate and multivariate functional data and utility functions" | https://cran.r-project.org/web/packages/tidyfun/index.html; https://cran.r-project.org/web/views/FunctionalData.html |
| Registration / alignment | partial | tidyfun/tf: "registration" mentioned in CRAN task view description of tf; not a primary focus | https://cran.r-project.org/web/views/FunctionalData.html |
| Depth & outlier detection | — | Not a primary feature of either package; depth attributed to fda.usc, fdaoutlier | https://cran.r-project.org/web/views/FunctionalData.html |
| FPCA / covariance / PACE sparse FPCA | partial | funData works with companion MFPCA package (separate package); not built-in | https://cran.r-project.org/web/packages/funData/index.html |
| Clustering | — | Not a feature of funData or tidyfun | https://cran.r-project.org/web/views/FunctionalData.html |
| Classification | — | Not a feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional regression (SoF / FoF) | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
| Functional time series | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Statistical process monitoring | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Inference / hypothesis testing | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Conformal prediction & tolerance bands | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Density / Frechet / metric-space | — | Not found | https://cran.r-project.org/web/views/FunctionalData.html |
| Simulation & datasets | partial | funData: utility simulation via MFPCA; tidyfun: limited | https://cran.r-project.org/web/packages/tidyfun/index.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://cran.r-project.org/web/packages/tidyfun/index.html |

---

## fdaM

- **Package:** fdaM (MATLAB)
- **Platform:** MATLAB
- **Version:** ~2014 (no versioned registry; last known MATLAB release approximately 2014)
- **Source URL:** https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/
- **Maintenance:** Low — mirrored on GitHub (markgewhite/fda, mzerter/fdaM), last commit ~2014
- Spot-checked: NO (historical MATLAB tool; no live registry)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | fdaM: basis-expansion framework mirroring R fda; B-spline, Fourier | https://cran.r-project.org/web/packages/fda/fda.pdf (documented as MATLAB counterpart to R fda) |
| Registration / alignment | ✓ | fdaM: landmark and continuous registration following Ramsay & Silverman | https://cran.r-project.org/web/packages/fda/fda.pdf |
| Depth & outlier detection | — | Not a focus of either fdaM or PACE | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| FPCA / covariance / PACE sparse FPCA | ✓ | PACE: "Functional Principal Component Analysis (FPCA)...for sparsely or densely sampled random trajectories" — the defining capability | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Clustering | partial | PACE: "Functional clustering and dimension reduction" mentioned; partial — not a primary use case | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Classification | — | Not a primary feature of fdaM or PACE | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Functional regression (SoF / FoF) | partial | PACE: "Functional linear and nonlinear regression", "Generalized functional linear models"; fdaM: basic regression; partial — narrower than dedicated packages | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Functional time series | — | Not found as a dedicated module | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Statistical process monitoring | — | Not found | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Inference / hypothesis testing | — | Not confirmed | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Conformal prediction & tolerance bands | — | Not found | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
| Density / Frechet / metric-space | — | Not found | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ |
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
| Representation / basis smoothing | ✓ | fdaM: basis-expansion framework mirroring R fda; B-spline, Fourier | https://cran.r-project.org/web/packages/fda/fda.pdf |
| Registration / alignment | ✓ | fdaM: landmark and continuous registration following Ramsay & Silverman | https://cran.r-project.org/web/packages/fda/fda.pdf |
| Depth & outlier detection | — | Not a focus of either fdaM or PACE | https://anson.ucdavis.edu/~mueller/data/pace.html |
| FPCA / covariance / PACE sparse FPCA | ✓ | PACE: "Functional Principal Component Analysis (FPCA)...for sparsely or densely sampled random trajectories" — the defining capability | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Clustering | partial | PACE: "Functional clustering and dimension reduction" mentioned; partial — not a primary use case | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Classification | — | Not a primary feature of fdaM or PACE | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Functional regression (SoF / FoF) | partial | PACE: "Functional linear and nonlinear regression", "Generalized functional linear models"; fdaM: basic regression; partial — narrower than dedicated packages | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Functional time series | — | Not found as a dedicated module | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Statistical process monitoring | — | Not found | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Inference / hypothesis testing | — | Not confirmed | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Conformal prediction & tolerance bands | — | Not found | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Density / Frechet / metric-space | — | Not found | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Simulation & datasets | partial | fdaM: datasets from Ramsay & Silverman textbook; PACE: limited simulation | https://anson.ucdavis.edu/~mueller/data/pace.html |
| Grounded advisor + scientific provenance | — | No grounded advisor or provenance layer | https://anson.ucdavis.edu/~mueller/data/pace.html |
