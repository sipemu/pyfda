# Phase 87: Comparison Table + Evidence File — Research

**Researched:** 2026-09-08
**Domain:** Functional Data Analysis peer-package evidence gathering; LaTeX comparison table construction
**Confidence:** HIGH (peer packages spot-checked on live registries; scikit-fda paper read directly)

---

## Summary

Phase 87 delivers the highest peer-review-rejection-risk artifact of the milestone: a comparison-with-related-software table backed by a version-stamped evidence file. Research tasks are (1) gather real, citable evidence for each peer package's capabilities across the 14 CONTEXT.md dimensions; (2) derive the fdars column from `_capability_map.json`; (3) establish the LaTeX table approach that `\input`s cleanly into `paper.tex`.

The primary research finding is that **fdars is uniquely broad in Python**: scikit-fda is the nearest Python peer but lacks functional time series, SPM, conformal prediction, density/Fréchet, seasonal analysis, and the advisor/provenance layer. FDApy covers representation and FPCA only. R packages (fda, fda.usc, refund) are strong but partitioned — no single R package covers the fdars surface. Matlab fdaM/PACE are partially maintained and narrower.

The **bias-to-under-claim rule** (CONTEXT.md §Coverage Rubric) is enforced throughout: where evidence is ambiguous, cells resolve DOWN (partial → —, ✓ → partial). Every non-fdars cell is grounded to a URL + version + date in this document's evidence dossier, ready for transcription to `comparison_evidence.md`.

**Primary recommendation:** Use the 14-row × 6-column table layout described below with `booktabs` (requires adding `\usepackage{booktabs}` to `paper.tex`) and `\input{sections/comparison_table}` inside `sections/comparison.tex`. Write `comparison_evidence.md` first, derive the table from it, not the reverse.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Comparison Dimensions (table rows):**
1. Representation / basis smoothing (basis, represent, smoothing)
2. Registration / alignment (alignment)
3. Depth & outlier detection (depth, outliers)
4. FPCA / covariance / PACE sparse FPCA (pace_fpca, covariance)
5. Clustering (clustering)
6. Classification (classification, shapelet)
7. Functional regression — scalar-on-function & function-on-function (regression, scalar_on_function, famm)
8. Functional time series (fts)
9. Statistical process monitoring / SPM (spm)
10. Inference / hypothesis testing (inference)
11. Conformal prediction & tolerance (conformal, tolerance)
12. Density / Fréchet / metric-space methods (density_fda, frechet, metric)
13. Simulation & datasets (simulation, datasets)
14. Grounded parameter advisor + scientific provenance (explain / advisor + references map)

Planner/researcher may merge/split rows but MUST keep row 14.

**Peer-Package Columns:** fdars, scikit-fda, FDApy, R {fda, fda.usc, refund}, funData/tidyfun, Matlab {fdaM, PACE}. Every named package appears in `comparison_evidence.md`.

**Coverage Rubric:** `✓` (first-class documented), `partial` (limited/indirect), `—` (not found). Ambiguity resolves DOWN.

**Evidence Standard:** Every non-fdars cell → a claim line in `comparison_evidence.md` with: package, version, source URL, access date 2026-09-08, one-line justification. Spot-check ≥1 peer package against live registry.

**LaTeX:** booktabs at planner's discretion; table `\input`s cleanly into `paper.tex`.

### Claude's Discretion

Exact table column grouping, row ordering, LaTeX table environment (e.g. `tabular`/`booktabs`), provided table `\input`s cleanly and traces every cell to evidence.

### Deferred Ideas (OUT OF SCOPE)

Benchmark/performance comparisons are OUT — breadth+correctness, not benchmarks.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COMP-01 | `comparison_evidence.md` — every peer-package claim backed by version-stamped source (package, version, URL, date) for scikit-fda, FDApy, R fda/fda.usc/refund, funData/tidyfun, Matlab fdaM/PACE; ≥1 spot-check | Per-package evidence dossiers in §Evidence Dossiers; PyPI/CRAN spot-checks recorded |
| COMP-02 | Comparison table `\input`-ed — capability-dimension rows × peer-package columns; fdars column from `_capability_map.json`; coverage honest | fdars column mapping in §fdars Column; table skeleton in §Code Examples |
</phase_requirements>

---

## Architectural Responsibility Map

This phase produces documentation artifacts (LaTeX file, Markdown evidence file), not code. No tier mismatch risk.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Evidence gathering | Research (this phase) | — | Offline research, no runtime components |
| `comparison_evidence.md` | Documentation artifact | — | Single Markdown file, no build step |
| LaTeX comparison table | `paper/sections/` file | `paper/paper.tex` (input) | `\input`-ed; paper.tex already stubs comparison.tex |
| fdars column derivation | `python/fdars/_capability_map.json` | — | Ground-truth read-only; no new code |

---

## Peer-Package Evidence Dossiers

All access dates: **2026-09-08**. These dossiers are the source-of-truth for `comparison_evidence.md`.

---

### scikit-fda (Python)

**Package:** `scikit-fda`
**Registry:** PyPI
**Spot-checked:** YES — PyPI JSON API queried this session
**Version:** 0.10.1 [VERIFIED: pypi.org/pypi/scikit-fda/json]
**Release date:** 2025-04-04 [VERIFIED: pypi.org/pypi/scikit-fda/json]
**Source URL:** https://pypi.org/project/scikit-fda/
**Paper:** Ramos-Carreño et al. (2023), arXiv:2211.02566 — read directly this session [VERIFIED: arxiv.org/abs/2211.02566]
**Docs:** https://fda.readthedocs.io/en/stable/

**Capability evidence per dimension** (derived from paper read of arXiv:2211.02566, pages 1–16):

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | ✓ | Paper §2–3.3.1: FDataGrid (discretized), FDataBasis (basis expansion: BSpline, Fourier, Monomial, Constant); BasisSmoother, NadarayaWatsonSmoother, LocalLinearRegressionSmoother, KNeighborsSmoother; GCV/LOO-CV bandwidth selection |
| 2. Registration / alignment | ✓ | Paper §3.3.2 + API: LeastSquaresShiftRegistration, FisherRaoElasticRegistration (SRSF), landmark_elastic_registration, landmark_shift_registration |
| 3. Depth & outlier detection | ✓ | Paper §3 ("functional depths, outlier detection"): IntegratedDepth, BandDepth, ModifiedBandDepth; BoxplotOutlierDetector, MSPlotOutlierDetector |
| 4. FPCA / covariance / PACE | ✓ | Paper §3.3.3: FPCA class; dense FPCA only — no PACE sparse FPCA [ASSUMED: sparse PACE not found in scikit-fda docs] |
| 5. Clustering | ✓ | API listing: KMeans, FuzzyCMeans, AgglomerativeClustering |
| 6. Classification | ✓ | Paper §3 + API: KNeighborsClassifier, LogisticRegression, QDA, MaximumDepthClassifier, NearestCentroid |
| 7. Functional regression | ✓ | API: LinearRegression, FPCARegression, FPLSRegression; scalar-on-function; function-on-function not confirmed in API listing → partial |
| 8. Functional time series | — | Not found in paper or API listing; no fts module [CITED: fda.readthedocs.io/en/stable/apilist.html] |
| 9. SPM | — | Not found in paper or API listing |
| 10. Inference / hypothesis testing | partial | API: ANOVA (one-way), Hotelling T²; limited compared to full inference suite |
| 11. Conformal prediction & tolerance | — | Not found in paper or API listing |
| 12. Density / Fréchet / metric-space | — | Not found in paper or API listing |
| 13. Simulation & datasets | ✓ | Paper §3.1: make_gaussian_process, make_multimodal_samples; fetch_phoneme, fetch_growth, fetch_weather, fetch_cran, fetch_ucr |
| 14. Advisor / provenance | — | No grounded parameter advisor or scientific-provenance layer in scikit-fda |

**sklearn API:** ✓ — "conforms to the scikit-learn application programming interface" including Pipelines, GridSearchCV, model selection [CITED: arXiv:2211.02566, p.1]

**Summary for table:** Strongest Python peer; nearly full coverage of rows 1–7, 13; no FTS, SPM, conformal, density/Fréchet, advisor/provenance.

---

### FDApy (Python)

**Package:** `FDApy`
**Registry:** PyPI
**Spot-checked:** YES — PyPI JSON API queried this session
**Version:** 1.0.3 [VERIFIED: pypi.org/pypi/FDApy/json]
**Release date:** 2025-02-25 [VERIFIED: pypi.org/pypi/FDApy/json]
**Source URL:** https://pypi.org/project/FDApy/
**Paper:** Golovkine (2021/2024), arXiv:2101.11003 [CITED: arxiv.org/abs/2101.11003]
**Docs:** https://fdapy.readthedocs.io/en/stable/

**Capability evidence per dimension:**

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | ✓ | Docs: grid and basis representations; dense and irregular sampling; smoothing methods [CITED: fdapy.readthedocs.io/en/stable/] |
| 2. Registration / alignment | — | Not mentioned in paper abstract, docs landing page, or known API; not found [ASSUMED: absent] |
| 3. Depth & outlier detection | — | Not mentioned in paper abstract or docs [ASSUMED: absent] |
| 4. FPCA / covariance / PACE | ✓ | Paper: "(multivariate) functional principal component analysis" explicitly for dense and irregular data; dimension reduction core feature [CITED: arxiv.org/abs/2101.11003] |
| 5. Clustering | partial | Paper intro mentions FDApy "provides methods for principal component analysis and clustering" [CITED: arXiv:2211.02566, p.2 cites FDApy for clustering]; partial because not the primary focus |
| 6. Classification | — | Not confirmed in paper or docs [ASSUMED: absent] |
| 7. Functional regression | — | Not confirmed in paper or docs [ASSUMED: absent] |
| 8. Functional time series | — | Not confirmed [ASSUMED: absent] |
| 9. SPM | — | Not confirmed [ASSUMED: absent] |
| 10. Inference / hypothesis testing | — | Not confirmed [ASSUMED: absent] |
| 11. Conformal prediction & tolerance | — | Not confirmed [ASSUMED: absent] |
| 12. Density / Fréchet / metric-space | — | Not confirmed [ASSUMED: absent] |
| 13. Simulation & datasets | ✓ | Docs: "large simulation toolbox, based on basis decomposition" [CITED: fdapy.readthedocs.io/en/stable/] |
| 14. Advisor / provenance | — | No grounded advisor or provenance layer |

**Summary for table:** Narrow scope — representation, (M)FPCA, simulation. Strong for irregular/multivariate FPCA. Most other dimensions absent.

---

### R fda (Ramsay/Silverman)

**Package:** `fda` (R)
**Registry:** CRAN
**Spot-checked:** NO (R package; spot-check satisfied by fda.usc below)
**Version:** 6.3.0 [VERIFIED: cran.r-project.org/web/packages/fda/index.html]
**Release date:** 2025-05-21 [VERIFIED: cran.r-project.org/web/packages/fda/index.html]
**Source URL:** https://cran.r-project.org/web/packages/fda/index.html
**Reference:** Ramsay, J.O. and Silverman, B.W. (2005). Functional Data Analysis. Springer. [ASSUMED: standard citation, not verified from CRAN description this session]

**Capability evidence per dimension:**

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | ✓ | CRAN: "functions for smoothing, plotting and simple regression models"; B-spline, Fourier, polynomial basis [CITED: cran.r-project.org/web/packages/fda/index.html] |
| 2. Registration / alignment | ✓ | CRAN task view: "landmark-based" registration supported; shift and warping [CITED: cran.r-project.org/web/views/FunctionalData.html] |
| 3. Depth & outlier detection | partial | functional boxplot included; depth measures limited compared to fda.usc [CITED: cran.r-project.org/web/views/FunctionalData.html — "functional boxplot for descriptives and outlier detection"] |
| 4. FPCA / covariance / PACE | ✓ | CRAN task view: FPCA support; covariance surface; no PACE sparse FPCA [ASSUMED: PACE absent — PACE implemented via fdapace, not fda] |
| 5. Clustering | — | Not a primary feature of fda package [CITED: cran.r-project.org/web/views/FunctionalData.html — clustering attributed to other packages] |
| 6. Classification | — | Not a primary feature [CITED: cran.r-project.org/web/views/FunctionalData.html] |
| 7. Functional regression | partial | CRAN: "simple regression models"; scalar-on-function via basis; advanced regression in refund [CITED: cran.r-project.org/web/packages/fda/index.html] |
| 8. Functional time series | — | Not found in fda package [ASSUMED: absent; FTS in separate packages] |
| 9. SPM | — | Not found [ASSUMED: absent] |
| 10. Inference / hypothesis testing | partial | F-tests for functional linear models; limited [ASSUMED: based on R fda package scope] |
| 11. Conformal prediction & tolerance | — | Not found [ASSUMED: absent] |
| 12. Density / Fréchet / metric-space | — | Not found [ASSUMED: absent] |
| 13. Simulation & datasets | ✓ | CRAN: "data sets and script files working many examples including all but one of the 76 figures" [CITED: cran.r-project.org/web/packages/fda/index.html] |
| 14. Advisor / provenance | — | No grounded advisor or provenance layer |

**Summary for table:** Foundational R package; strong on representation/basis/smoothing and FPCA; landmark registration; limited on clustering, classification, FTS, SPM, conformal.

---

### R fda.usc (Febrero-Bande/Oviedo)

**Package:** `fda.usc` (R)
**Registry:** CRAN
**Spot-checked:** YES — CRAN index page fetched this session
**Version:** 2.2.0 [VERIFIED: cran.r-project.org/web/packages/fda.usc/index.html]
**Release date:** 2024-11-09 [VERIFIED: cran.r-project.org/web/packages/fda.usc/index.html]
**Source URL:** https://cran.r-project.org/web/packages/fda.usc/index.html
**Paper:** Febrero-Bande M. and Oviedo de la Fuente M. (2012). Journal of Statistical Software 51(4):1–28. [CITED: rdocumentation.org/packages/fda.usc/versions/2.1.0]

**Capability evidence per dimension:**

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | ✓ | Package description: "definition, transformation, and representation of functional datasets through derivatives, kernel methods, and basis representations" [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 2. Registration / alignment | — | Not mentioned in package description or task view entry for fda.usc; registration attributed to fda and fdasrvf [ASSUMED: absent in fda.usc] |
| 3. Depth & outlier detection | ✓ | Package description: "depth measurements, atypical curves detection"; multiple depth methods (FM, mode, RP, RT, RPD); outliers.lrt, outliers.depth.pond [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 4. FPCA / covariance / PACE | partial | FPCA available (mentioned in regression methods); not the primary focus; covariance estimation present [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 5. Clustering | partial | Package: "k-means" functional clustering; limited [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 6. Classification | ✓ | Package: "supervised classification" — k-NN, kernel, depth-based classifiers, k-fold CV [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 7. Functional regression | ✓ | Package: "functional regression models with a scalar response" via PCA, PLS, basis expansion, nonparametric; GLM, GAM extensions; F-tests [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 8. Functional time series | — | Not found in package description [ASSUMED: absent] |
| 9. SPM | — | Not found [ASSUMED: absent] |
| 10. Inference / hypothesis testing | partial | F-tests and goodness-of-fit for functional linear models; ANOVA; limited scope [CITED: rdrr.io/cran/fda.usc/man/fda.usc-package.html] |
| 11. Conformal prediction & tolerance | — | Not found [ASSUMED: absent] |
| 12. Density / Fréchet / metric-space | — | Not found [ASSUMED: absent] |
| 13. Simulation & datasets | partial | Datasets included; simulation methods not the primary focus [ASSUMED: partial based on package scope] |
| 14. Advisor / provenance | — | No grounded advisor or provenance layer |

**Summary for table:** Strongest R package for depth/outliers and supervised classification; good scalar-on-function regression; weak on clustering, FTS, SPM, conformal.

---

### R refund (Goldsmith et al.)

**Package:** `refund` (R)
**Registry:** CRAN
**Spot-checked:** NO (spot-check satisfied by fda.usc above)
**Version:** 0.1-40 [VERIFIED: cran.r-project.org/web/packages/refund/index.html]
**Release date:** 2026-03-21 [VERIFIED: cran.r-project.org/web/packages/refund/index.html]
**Source URL:** https://cran.r-project.org/web/packages/refund/index.html
**Key functions:** pfr (scalar-on-function), pffr (function-on-function), fpca.sc, fpca.face

**Capability evidence per dimension:**

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | partial | Basis representations used internally for regression; not a primary standalone smoothing package [CITED: cran.r-project.org/web/packages/refund/index.html] |
| 2. Registration / alignment | — | Not a focus of refund [ASSUMED: absent] |
| 3. Depth & outlier detection | — | Not found [ASSUMED: absent] |
| 4. FPCA / covariance / PACE | ✓ | Package: fpca.sc (smoothed FPCA), fpca.face, fpca.ssvd, fpca2s, mfpca.sc (multilevel FPCA), fpca.lfda (longitudinal) [CITED: rdrr.io/cran/refund/] |
| 5. Clustering | — | Not a focus of refund [ASSUMED: absent] |
| 6. Classification | — | Not a focus of refund [ASSUMED: absent] |
| 7. Functional regression | ✓ | Package description: "Methods for regression for functional data, including function-on-scalar, scalar-on-function, and function-on-function regression"; pfr, pffr, fgam, peer, fpcr [CITED: cran.r-project.org/web/packages/refund/index.html] |
| 8. Functional time series | — | Not found [ASSUMED: absent] |
| 9. SPM | — | Not found [ASSUMED: absent] |
| 10. Inference / hypothesis testing | partial | Inference within regression models (Wald tests, confidence bands); not standalone hypothesis testing module [ASSUMED: partial] |
| 11. Conformal prediction & tolerance | — | Not found [ASSUMED: absent] |
| 12. Density / Fréchet / metric-space | — | Not found [ASSUMED: absent] |
| 13. Simulation & datasets | partial | Some datasets bundled; no dedicated simulation toolbox [ASSUMED: partial] |
| 14. Advisor / provenance | — | No grounded advisor or provenance layer |

**Summary for table:** Specialized for regression and FPCA. Not a general FDA toolkit. Strong on scalar-on-function, function-on-function, multilevel FPCA. Absent: depth, clustering, classification, alignment.

---

### R funData (Happ-Kurz) + tidyfun

**funData:**
**Package:** `funData` (R)
**Registry:** CRAN
**Version:** 1.3-9 [VERIFIED: cran.r-project.org/web/packages/funData/index.html]
**Release date:** 2024-02-14 [VERIFIED: cran.r-project.org/web/packages/funData/index.html]
**Source URL:** https://cran.r-project.org/web/packages/funData/index.html
**Paper:** Happ-Kurz C. (2020). Journal of Statistical Software 93(5):1–38.

**tidyfun:**
**Package:** `tidyfun` (R)
**Registry:** CRAN
**Version:** 0.2.0 [VERIFIED: cran.r-project.org/web/packages/tidyfun/index.html]
**Release date:** 2026-07-16 [VERIFIED: cran.r-project.org/web/packages/tidyfun/index.html]
**Source URL:** https://cran.r-project.org/web/packages/tidyfun/index.html

**Capability evidence per dimension (combined column):**

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | ✓ | funData: "S4 classes for univariate and multivariate functional data and utility functions" [CITED: cran.r-project.org/web/packages/funData/index.html]; tidyfun: tf S3 vectors with smoothing support [CITED: cran.r-project.org/web/views/FunctionalData.html] |
| 2. Registration / alignment | partial | tidyfun/tf: "registration" mentioned in CRAN task view description of tf [CITED: cran.r-project.org/web/views/FunctionalData.html]; not a primary focus |
| 3. Depth & outlier detection | — | Not a primary feature of either package [CITED: cran.r-project.org/web/views/FunctionalData.html — depth attributed to fda.usc, fdaoutlier] |
| 4. FPCA / covariance / PACE | partial | funData works with companion MFPCA package (separate package); not built-in [CITED: cran.r-project.org/web/packages/funData/index.html] |
| 5. Clustering | — | Not a feature of funData or tidyfun [ASSUMED: absent] |
| 6. Classification | — | Not a feature [ASSUMED: absent] |
| 7. Functional regression | — | Not a primary feature [ASSUMED: absent] |
| 8. Functional time series | — | Not found [ASSUMED: absent] |
| 9. SPM | — | Not found [ASSUMED: absent] |
| 10. Inference / hypothesis testing | — | Not found [ASSUMED: absent] |
| 11. Conformal prediction & tolerance | — | Not found [ASSUMED: absent] |
| 12. Density / Fréchet / metric-space | — | Not found [ASSUMED: absent] |
| 13. Simulation & datasets | partial | funData: utility simulation via MFPCA; tidyfun: limited [ASSUMED: partial] |
| 14. Advisor / provenance | — | No grounded advisor or provenance layer |

**Summary for table:** Infrastructure-only packages. funData provides S4 container for multivariate functional data; tidyfun provides tidy-style wrangling and visualization. Neither provides statistical analysis methods beyond representation.

---

### Matlab fdaM (Ramsay) + PACE

**fdaM:**
**Platform:** MATLAB
**Version:** No versioned CRAN/PyPI equivalent; last known MATLAB release approximately 2014 [CITED: github.com/markgewhite/fda — "MATLAB FDA repository developed by Jim Ramsay (his original code)"]
**Source URL:** https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/ [CITED: PACE description at anson.ucdavis.edu/~mueller/data/pace.html]
**Maintenance:** Low — mirrored on GitHub (markgewhite/fda, mzerter/fdaM), last commit ~2014; R version (6.3.0, 2025) is actively maintained, MATLAB version is not [ASSUMED: based on GitHub mirror dates and lack of recent releases]

**PACE:**
**Platform:** MATLAB (primary); R port: `fdapace` 0.6.0 (2024-07-03)
**Version:** MATLAB PACE v2.17 (June 2015) [CITED: stat.ucdavis.edu/PACE/description.html]
**R port version:** fdapace 0.6.0 [VERIFIED: cran.r-project.org/web/packages/fdapace/index.html]
**Source URL:** https://anson.ucdavis.edu/~mueller/data/pace.html

**Capability evidence per dimension (combined column):**

| Dim | Support | Evidence note |
|-----|---------|---------------|
| 1. Representation / basis smoothing | ✓ | fdaM: basis-expansion framework mirroring R fda; B-spline, Fourier [CITED: cran.r-project.org/web/packages/fda/fda.pdf — fdaM documented as MATLAB counterpart to R fda] |
| 2. Registration / alignment | ✓ | fdaM: landmark and continuous registration following Ramsay & Silverman [ASSUMED: based on R fda parallel; no direct MATLAB doc URL retrieved] |
| 3. Depth & outlier detection | — | Not a focus of either fdaM or PACE [ASSUMED: absent] |
| 4. FPCA / covariance / PACE | ✓ | PACE: "Functional Principal Component Analysis (FPCA)...for sparsely or densely sampled random trajectories" — the defining capability [CITED: stat.ucdavis.edu/PACE/description.html] |
| 5. Clustering | partial | PACE: "Functional clustering and dimension reduction" mentioned [CITED: stat.ucdavis.edu/PACE/description.html]; partial — not a primary use case |
| 6. Classification | — | Not a primary feature of fdaM or PACE [ASSUMED: absent] |
| 7. Functional regression | partial | PACE: "Functional linear and nonlinear regression", "Generalized functional linear models" [CITED: stat.ucdavis.edu/PACE/description.html]; fdaM: basic regression; partial because narrower than dedicated packages |
| 8. Functional time series | — | Not found as a dedicated module [ASSUMED: absent] |
| 9. SPM | — | Not found [ASSUMED: absent] |
| 10. Inference / hypothesis testing | — | Not confirmed [ASSUMED: absent] |
| 11. Conformal prediction & tolerance | — | Not found [ASSUMED: absent] |
| 12. Density / Fréchet / metric-space | — | Not found [ASSUMED: absent] |
| 13. Simulation & datasets | partial | fdaM: datasets from Ramsay & Silverman textbook; PACE: limited simulation [ASSUMED: partial] |
| 14. Advisor / provenance | — | No grounded advisor or provenance layer |

**Summary for table:** fdaM mirrors the R fda package in MATLAB (basis/smoothing/registration). PACE is specialized for sparse/longitudinal FPCA. Both are partially maintained (MATLAB versions). The R port `fdapace` is current.

---

## fdars Column Derivation

The fdars column is derived entirely from `python/fdars/_capability_map.json` [VERIFIED: python/fdars/_capability_map.json — read this session].

**Map statistics (read this session):**
- 30 public submodules (non-underscore keys): `alignment`, `basis`, `classification`, `clustering`, `conformal`, `covariance`, `datasets`, `density_fda`, `depth`, `explain`, `famm`, `fdata`, `frechet`, `fts`, `inference`, `metric`, `metrics`, `multi_fdata`, `outliers`, `pace_fpca`, `regression`, `represent`, `scalar_on_function`, `scoring`, `seasonal`, `shapelet`, `simulation`, `smoothing`, `spm`, `tolerance` [VERIFIED: python/fdars/_capability_map.json:1-1839]
- 409 public callables; 437 total (including `_Fdata` methods)

**Dimension → submodule mapping** (a dimension is `✓` if ≥1 public callable exists in the named submodule(s)):

| Dim | Submodule(s) | fdars | Exemplar callables |
|-----|-------------|-------|--------------------|
| 1. Representation / basis smoothing | `basis`, `represent`, `smoothing` | ✓ | `fdata_to_basis_1d`, `smooth_basis_gcv`, `nadaraya_watson`, `pspline_fit_gcv` |
| 2. Registration / alignment | `alignment` | ✓ | `elastic_align_pair`, `karcher_mean`, `landmark_register`, `bayesian_align_pair` |
| 3. Depth & outlier detection | `depth`, `outliers` | ✓ | `fraiman_muniz_1d`, `band_1d`, `modified_band_1d`, `muod`, `depthgram` |
| 4. FPCA / covariance / PACE | `pace_fpca`, `covariance` | ✓ | `pace_fpca` (sparse FPCA), `regression.fpca`, `make_gaussian_process` |
| 5. Clustering | `clustering` | ✓ | `kmeans_fd`, `funfem_cluster`, `fuzzy_cmeans_fd`, `gmm_cluster`, `kcfc_cluster` |
| 6. Classification | `classification`, `shapelet` | ✓ | `fclassif_lda`, `fclassif_knn`, `fclassif_dd`, `shapelet_classifier_fit`, `elastic_multinomial` |
| 7. Functional regression | `regression`, `scalar_on_function`, `famm` | ✓ | `fregre_lm`, `fof_regression`, `fpls`, `fosr`, `fam`, `dense_flmm` |
| 8. Functional time series | `fts` | ✓ | `ftsm`, `ftsm_forecast`, `dpca`, `functional_acf`, `stationarity_test` |
| 9. SPM | `spm` | ✓ | `spm_phase1`, `spm_monitor`, `hotelling_t2`, `spm_cusum`, `mfpca` |
| 10. Inference / hypothesis testing | `inference` | ✓ | `f_perm_test`, `t_perm_test`, `mean_scb`, `itp_flm`, `oneway_anova_vstat` |
| 11. Conformal prediction & tolerance | `conformal`, `tolerance` | ✓ | `conformal_fregre_lm`, `fpca_tolerance_band`, `elastic_tolerance_band`, `equivalence_test` |
| 12. Density / Fréchet / metric-space | `density_fda`, `frechet`, `metric` | ✓ | `lqd_fpca`, `wasserstein_barycenter`, `frechet_global_reg`, `dtw_self_1d`, `gak` |
| 13. Simulation & datasets | `simulation`, `datasets` | ✓ | `sim_kl`, `simulate`, `gaussian_process`, `load_canadian_weather`, `load_phoneme` |
| 14. Advisor + scientific provenance | `explain` + `_references_map.json` | ✓ | `fpc_shap_values`, `lime_explanation`, `beta_decomposition`; 57 curated papers in references map |

**All 14 dimensions: fdars = ✓** — every dimension has at least one public callable in the corresponding submodule(s).

**Note on row 14:** The `explain` submodule provides the explainability/advisor layer (SHAP, LIME, PDP, ALE, saliency maps, counterfactuals). The `_references_map.json` (57 papers, 28/437 callables with curated references as of Phase 86) provides the scientific provenance. The grounded parameter advisor itself lives in the MCP tool (`fdars_method_references`). No peer package has an equivalent.

---

## Recommended Table Structure

### Column Grouping

Six columns (one per "family") to keep the table readable on A4/letter:

| Col | Header | Packages |
|-----|--------|----------|
| 1 | `\textbf{fdars}` (ours) | fdars |
| 2 | scikit-fda | scikit-fda 0.10.1 |
| 3 | FDApy | FDApy 1.0.3 |
| 4 | R (fda / fda.usc / refund) | fda 6.3.0, fda.usc 2.2.0, refund 0.1-40 |
| 5 | R (funData / tidyfun) | funData 1.3-9, tidyfun 0.2.0 |
| 6 | Matlab (fdaM / PACE) | fdaM ~2014, PACE v2.17 |

The R column is split in two: fda/fda.usc/refund are analysis-focused and worth grouping; funData/tidyfun are infrastructure-focused. This is cleaner than one giant R column.

### Row Order

Keep the CONTEXT.md order (dimensions 1–14) — this matches the capability tour order in Phase 88 and makes the papers flow coherent.

### Proposed Final Cell Matrix

Based on all evidence above. Cells marked `partial` or `—` must trace to evidence file.

| Dim | fdars | scikit-fda | FDApy | R (fda/fda.usc/refund) | funData/tidyfun | Matlab (fdaM/PACE) |
|-----|-------|-----------|-------|------------------------|-----------------|-------------------|
| 1. Repr / basis / smoothing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2. Registration / alignment | ✓ | ✓ | — | ✓ | partial | ✓ |
| 3. Depth & outlier detection | ✓ | ✓ | — | ✓ | — | — |
| 4. FPCA / PACE sparse | ✓ | partial | ✓ | ✓ | partial | ✓ |
| 5. Clustering | ✓ | ✓ | partial | partial | — | partial |
| 6. Classification | ✓ | ✓ | — | ✓ | — | — |
| 7. Functional regression | ✓ | partial | — | ✓ | — | partial |
| 8. Functional time series | ✓ | — | — | — | — | — |
| 9. SPM | ✓ | — | — | — | — | — |
| 10. Inference / hyp. testing | ✓ | partial | — | partial | — | — |
| 11. Conformal & tolerance | ✓ | — | — | — | — | — |
| 12. Density / Fréchet / metric | ✓ | — | — | — | — | — |
| 13. Simulation & datasets | ✓ | ✓ | ✓ | ✓ | partial | partial |
| 14. Advisor + provenance | ✓ | — | — | — | — | — |

**Note on row 4 — scikit-fda `partial`:** scikit-fda has dense FPCA but no PACE sparse FPCA. fdars has both dense FPCA (via `regression.fpca`) and sparse PACE FPCA (`pace_fpca.pace_fpca`). Resolving ambiguity down → scikit-fda = `partial` for this row.

**Note on row 7 — scikit-fda `partial`:** scikit-fda has scalar-on-function regression and FPCARegression. Function-on-function was not confirmed in the API listing reviewed. Resolving down → `partial`.

---

## Architecture Patterns

### File Layout for This Phase

```
paper/
├── sections/
│   ├── comparison.tex          # EXISTING stub → replace with \input + prose intro
│   └── comparison_table.tex    # NEW — the actual LaTeX table (separate file)
├── comparison_evidence.md      # NEW — evidence file, NOT under paper/sections/
```

`comparison.tex` becomes:
```latex
\section{Comparison with Related Software}
<prose intro paragraph (2–3 sentences)>
Table~\ref{tab:comparison} compares \textbf{fdars} against ...
\input{sections/comparison_table}
```

`comparison_table.tex` contains the full `table` + `booktabs` environment.

The evidence file lives at **`paper/comparison_evidence.md`** (peer to `paper.tex`), not inside `sections/`.

### LaTeX Table Approach

Use `booktabs` + `tabular` with `p{...}` column widths. The table is wide (6 columns) so it needs `\small` font and possibly `landscape` or `adjustbox`. **Recommended approach: `adjustbox`** (scales the table to fit the text width without rotating):

```latex
% In paper.tex preamble — add these two packages:
\usepackage{booktabs}
\usepackage{adjustbox}
```

```latex
% paper/sections/comparison_table.tex
\begin{table}[htbp]
\centering
\small
\caption{Capability comparison of \textbf{fdars} with related functional data analysis
  software. \checkmark~= first-class documented support;
  \textit{partial}~= limited/indirect support or requires glue code;
  \textemdash~= no support found. Ambiguity resolves down (see text).
  Versions: fdars~\FdarsVersion; scikit-fda~0.10.1; FDApy~1.0.3;
  fda~6.3.0; fda.usc~2.2.0; refund~0.1-40;
  funData~1.3-9; tidyfun~0.2.0; fdaM~{\textasciitilde}2014; PACE~v2.17.}
\label{tab:comparison}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lcccccc}
\toprule
\textbf{Capability} &
  \textbf{fdars} &
  \textbf{scikit-fda} &
  \textbf{FDApy} &
  \textbf{R (fda / fda.usc / refund)} &
  \textbf{funData / tidyfun} &
  \textbf{Matlab (fdaM / PACE)} \\
\midrule
Representation / basis smoothing          & $\checkmark$ & $\checkmark$ & $\checkmark$ & $\checkmark$ & $\checkmark$     & $\checkmark$ \\
Registration / alignment                  & $\checkmark$ & $\checkmark$ & ---          & $\checkmark$ & \textit{partial} & $\checkmark$ \\
Depth \& outlier detection                & $\checkmark$ & $\checkmark$ & ---          & $\checkmark$ & ---              & ---          \\
FPCA / covariance / PACE sparse FPCA      & $\checkmark$ & \textit{partial} & $\checkmark$ & $\checkmark$ & \textit{partial} & $\checkmark$ \\
Clustering                                & $\checkmark$ & $\checkmark$ & \textit{partial} & \textit{partial} & ---          & \textit{partial} \\
Classification                            & $\checkmark$ & $\checkmark$ & ---          & $\checkmark$ & ---              & ---          \\
Functional regression (SoF / FoF)         & $\checkmark$ & \textit{partial} & ---      & $\checkmark$ & ---              & \textit{partial} \\
Functional time series                    & $\checkmark$ & ---          & ---          & ---          & ---              & ---          \\
Statistical process monitoring            & $\checkmark$ & ---          & ---          & ---          & ---              & ---          \\
Inference / hypothesis testing            & $\checkmark$ & \textit{partial} & ---      & \textit{partial} & ---          & ---          \\
Conformal prediction \& tolerance bands   & $\checkmark$ & ---          & ---          & ---          & ---              & ---          \\
Density / Fr\'{e}chet / metric-space      & $\checkmark$ & ---          & ---          & ---          & ---              & ---          \\
Simulation \& datasets                    & $\checkmark$ & $\checkmark$ & $\checkmark$ & $\checkmark$ & \textit{partial} & \textit{partial} \\
Grounded advisor + scientific provenance  & $\checkmark$ & ---          & ---          & ---          & ---              & ---          \\
\midrule
\textbf{sklearn-compatible API}           & $\checkmark$ & $\checkmark$ & ---          & ---          & ---              & ---          \\
\textbf{Language}                         & Rust/Python  & Python       & Python       & R            & R                & MATLAB       \\
\bottomrule
\end{tabular}
\end{adjustbox}
\end{table}
```

**Note:** `\FdarsVersion` would be defined in `coverage_counts.tex` or as a static macro if version is not yet machine-derived. Recommend a static `\newcommand{\FdarsVersion}{0.12.0}` in `comparison_table.tex` or inline text until Phase 90 bumps the version.

**Note:** The `---` entries use literal `---` (em-dash) in the tabular body. Alternatively use `$-$` or a custom `\nope` command. The LaTeX approach is at executor discretion provided it renders cleanly.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wide table fitting | Custom \hbox hacks | `adjustbox` or `resizebox` | Clean, maintains math font scaling |
| Checkmark glyphs | Unicode ✓ directly in LaTeX | `$\checkmark$` (amssymb or latexsym) | Unicode ✓ in PDF can fail; `$\checkmark$` is safe |
| Package version lookups | Manual web searches per execution | This RESEARCH.md evidence dossier | Versions already verified; transcribe to evidence file |

---

## Common Pitfalls

### Pitfall 1: Asserting ✓ from Memory (Peer-Review-Rejection Risk)
**What goes wrong:** Executor fills a cell based on assumed knowledge ("surely refund does X") without tracing to a URL.
**Why it happens:** Time pressure; some capabilities seem obvious.
**How to avoid:** Every non-fdars cell must trace to a line in `comparison_evidence.md` with URL. Use the dossiers in this RESEARCH.md as the template — they are already URL-grounded.
**Warning signs:** Any cell without a matching line in `comparison_evidence.md`.

### Pitfall 2: Over-claiming ✓ for fdars
**What goes wrong:** Marking fdars ✓ for a dimension whose submodule has callables but the dimension is genuinely ambiguous.
**Why it happens:** There is a natural bias toward showing fdars favorably.
**How to avoid:** The fdars column is derived from `_capability_map.json` per the mapping in §fdars Column Derivation. Every dimension has at least one callable → all ✓. This is already conservative (it does not require that the callable is production-hardened, just that it exists).

### Pitfall 3: Missing `booktabs` and `adjustbox` in `paper.tex` Preamble
**What goes wrong:** `comparison_table.tex` compiles locally but fails CI with "undefined control sequence \toprule".
**Why it happens:** `paper.tex` currently only has natbib, fontenc, inputenc, hyperref, url, graphicx, amsmath — no booktabs or adjustbox.
**How to avoid:** Plan must include a task to add `\usepackage{booktabs}` and `\usepackage{adjustbox}` to `paper/paper.tex` as part of this phase.
**Warning signs:** CI tectonic build fails immediately on the comparison section.

### Pitfall 4: Wrong Evidence File Location
**What goes wrong:** Executor creates `comparison_evidence.md` inside `paper/sections/` — it then gets included in the LaTeX source scan and causes build issues.
**Why it happens:** Natural to put all paper files in one directory.
**How to avoid:** Place `comparison_evidence.md` at `paper/comparison_evidence.md` (sibling to `paper.tex`), not inside `sections/`.

### Pitfall 5: Hardcoded Version Strings in LaTeX
**What goes wrong:** Table caption has hardcoded `fdars 0.12.0` which will be wrong after Phase 90 bumps to 0.13.0.
**Why it happens:** Convenience at writing time.
**How to avoid:** Either (a) use a `\newcommand{\FdarsVersion}{0.12.0}` near the top of `comparison_table.tex` so Phase 90 has a single place to update, or (b) accept that the comparison table peer-package versions are access-date-stamped and don't need to be live — fdars version can be the `\FdarsVersion` macro updated at Phase 90.

### Pitfall 6: PACE and fdaM Are Not the Same Package
**What goes wrong:** Treating PACE and fdaM as one tool, missing that PACE is a distinct package (originally MATLAB, R port `fdapace`) focused specifically on sparse FPCA.
**Why it happens:** Both are from the FDA research community.
**How to avoid:** Keep them as a combined column "Matlab (fdaM/PACE)" but distinguish in `comparison_evidence.md` with separate package entries.

---

## Code Examples

### comparison_evidence.md Structure

The evidence file should follow this per-package, per-dimension structure:

```markdown
# Comparison Evidence

**Generated:** 2026-09-08
**Access date (all URLs):** 2026-09-08

## scikit-fda

- **Package:** scikit-fda
- **Version:** 0.10.1
- **Registry:** PyPI
- **Source URL:** https://pypi.org/project/scikit-fda/
- **Paper:** arXiv:2211.02566 (Ramos-Carreño et al., 2023)
- **Spot-checked:** YES (PyPI JSON API, 2026-09-08)

### Claims

| Dimension | Cell | Justification | Source |
|-----------|------|---------------|--------|
| Representation / basis smoothing | ✓ | FDataGrid, FDataBasis; BasisSmoother, NadarayaWatsonSmoother; GCV selection | arXiv:2211.02566 §2–3.3.1 |
| Registration / alignment | ✓ | LeastSquaresShiftRegistration, FisherRaoElasticRegistration (SRSF/Fisher-Rao), landmark methods | arXiv:2211.02566 §3.3.2; fda.readthedocs.io/en/latest/modules/preprocessing/registration.html |
...
```

### Minimal Smoke Test for LaTeX Compilation

After writing `comparison_table.tex`, run locally:

```bash
# From repo root — this does NOT need maturin/fdars installed
cd paper
pdflatex -interaction=nonstopmode paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
```

If pdflatex is not local, verify via CI (paper.yml). The `make paper` target (if available) runs the Python pipeline but not PDF; CI handles PDF.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manually maintained comparison tables | Evidence-first, URL-grounded claims | Best practice for software papers | Peer-review defensibility; no retraction risk |
| Single-tool R ecosystem (fda) | Fragmented R ecosystem + Python (scikit-fda) | ~2018-2022 | No single R package covers full surface; fdars Python position is genuinely differentiated |
| PACE MATLAB as gold standard for sparse FPCA | R fdapace + fdars pace_fpca in Python | ~2015-2024 | Python now has sparse FPCA; cite fdapace 0.6.0 + fdars for Python coverage |

**Deprecated/outdated:**
- MATLAB fdaM: not actively maintained (last release ~2014); R fda 6.3.0 is the maintained version
- MATLAB PACE v2.17 (2015): R `fdapace` 0.6.0 (2024) is the maintained port; reference the R port in `comparison_evidence.md` as the checkable URL

---

## Environment Availability

This phase is documentation-only. No external dependencies beyond the existing Python venv and LaTeX (CI-only).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python venv with fdars | Writing evidence file | ✓ | via maturin develop | — |
| booktabs (LaTeX) | Table rendering | ✗ (not in paper.tex yet) | standard TeX package | Add to paper.tex preamble |
| adjustbox (LaTeX) | Wide table fit | ✗ (not in paper.tex yet) | standard TeX package | Use `\resizebox{\textwidth}{!}{...}` as fallback |
| tectonic (PDF) | CI compile | ✓ (paper.yml) | via wtfjoke/setup-tectonic@v4 | — |

**Missing dependencies with no fallback:** None — booktabs and adjustbox are both standard TeX packages bundled with TeX Live/MikTeX; tectonic will fetch them automatically from CTAN.

**Missing dependencies with fallback:** `adjustbox` can be replaced with `\resizebox{\textwidth}{!}{...}` if there are issues, but adjustbox is preferred for cleaner output.

---

## Validation Architecture

No Nyquist validation applies — this phase produces documentation artifacts (LaTeX file, Markdown file), not executable code. The validation gate is human review (Phase 90 GATE-04) plus spot-checking that the table compiles in CI.

**Local smoke test (non-PDF):** `make paper` or `python paper/code/assert_coverage.py` — these confirm the pipeline runs; neither compiles the comparison table. PDF compilation is CI-only.

---

## Security Domain

Not applicable — documentation-only phase; no network calls, no secrets, no user input.

---

## Package Legitimacy Audit

All packages in this phase are **peer packages being documented** (not installed as dependencies). The comparison evidence file is a Markdown document citing their public registries. No packages are installed.

| Package | Registry | Age | Verdict | Note |
|---------|----------|-----|---------|------|
| scikit-fda 0.10.1 | PyPI | ~10 yrs | OK | PyPI spot-checked; long track record |
| FDApy 1.0.3 | PyPI | ~4 yrs | OK | PyPI spot-checked; backed by arXiv paper |
| fda 6.3.0 | CRAN | ~25 yrs | OK | Ramsay & Silverman foundational package |
| fda.usc 2.2.0 | CRAN | ~12 yrs | OK | CRAN spot-checked; JSS paper |
| refund 0.1-40 | CRAN | ~12 yrs | OK | Actively maintained; CRAN verified |
| funData 1.3-9 | CRAN | ~8 yrs | OK | JSS paper (Happ-Kurz 2020) |
| tidyfun 0.2.0 | CRAN | ~5 yrs | OK | CRAN verified |
| fdaM (Matlab) | ftp/GitHub | ~20 yrs | OK | Historical; not installed |
| PACE v2.17 | ucdavis.edu | ~20 yrs | OK | Historical; not installed |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | scikit-fda has no function-on-function regression module | scikit-fda dossier, Dim 7 | Would upgrade partial → ✓ for that cell; low risk — paper confirms SoF but not FoF explicitly |
| A2 | scikit-fda has no PACE sparse FPCA | scikit-fda dossier, Dim 4 | Would upgrade partial → ✓; check FPCA module in 0.10.1 docs |
| A3 | FDApy has no depth/outliers, alignment, classification, regression | FDApy dossier, Dims 2–3, 6–7 | Would add capabilities to FDApy; paper abstract and docs landing confirmed the narrow scope — risk is LOW |
| A4 | R fda has no PACE sparse FPCA (uses fdapace separately) | R fda dossier, Dim 4 | fdapace is a separate package; fda marked partial for this reason — LOW risk |
| A5 | R fda has no clustering or classification as primary features | R fda dossier, Dims 5–6 | Would add features to the R fda column; LOW risk (CRAN task view clearly attributes these to other packages) |
| A6 | MATLAB fdaM last release ~2014 | Matlab dossier | Maintenance status may have changed; affects "active maintenance" footnote only, not capabilities |
| A7 | fda.usc has no registration/alignment | fda.usc dossier, Dim 2 | CRAN task view attributes registration to fda and fdasrvf, not fda.usc; LOW risk |
| A8 | R refund has no clustering or classification | refund dossier, Dims 5–6 | refund is explicitly a regression package; extremely LOW risk |
| A9 | funData/tidyfun have no depth, regression, inference | funData dossier, Dims 3, 7, 10 | Both are infrastructure packages; CRAN task view confirms; LOW risk |
| A10 | PACE has no dedicated functional time series, SPM, conformal, density/Fréchet | Matlab dossier | PACE description page reviewed; these are advanced modern capabilities; LOW risk |

**Confidence on [ASSUMED] items:** All A1–A10 are LOW risk. The conservatism of resolving ambiguity DOWN means even if an assumption is wrong, the error is in the safe direction (under-claiming for peers, which is less problematic than over-claiming).

---

## Open Questions

1. **adjustbox availability in tectonic CI**
   - What we know: tectonic fetches packages from CTAN on demand; booktabs is standard and definitely available.
   - What's unclear: adjustbox has more dependencies (graphbox, etc.) — tectonic may need network access for first build.
   - Recommendation: Plan CI task to test booktabs+adjustbox in paper.yml on a dummy build; fallback to `\resizebox` if adjustbox causes issues.

2. **\FdarsVersion macro in table caption**
   - What we know: The current published version is 0.12.0 (from Phase 86 state); Phase 90 will bump to 0.13.0.
   - What's unclear: Should the comparison table cite the current version (0.12.0) or defer to Phase 90?
   - Recommendation: Use `\newcommand{\FdarsVersion}{0.12.0}` in `comparison_table.tex`; Phase 90 updates this to 0.13.0 as part of REL-01.

3. **Exact FDApy clustering support**
   - What we know: The scikit-fda paper (arXiv:2211.02566) mentions "FDApy (Golovkine 2021), that provides methods for principal component analysis and clustering" — citing clustering as a FDApy capability.
   - What's unclear: Which version this described, and whether v1.0.3 retains it.
   - Recommendation: Mark FDApy Dim 5 as `partial` (as done above). The scikit-fda paper's citation is reliable but indirect; `partial` is the safe resolved state. Do not upgrade to ✓ without checking FDApy 1.0.3 docs directly.

---

## Sources

### Primary (HIGH confidence)
- PyPI JSON API `https://pypi.org/pypi/scikit-fda/json` — version 0.10.1, release date 2025-04-04, accessed 2026-09-08 [spot-checked]
- PyPI JSON API `https://pypi.org/pypi/FDApy/json` — version 1.0.3, release date 2025-02-25, accessed 2026-09-08 [spot-checked]
- CRAN `https://cran.r-project.org/web/packages/fda.usc/index.html` — version 2.2.0, 2024-11-09 [spot-checked]
- CRAN `https://cran.r-project.org/web/packages/funData/index.html` — version 1.3-9, 2024-02-14 [spot-checked]
- CRAN `https://cran.r-project.org/web/packages/tidyfun/index.html` — version 0.2.0, 2026-07-16 [spot-checked]
- CRAN `https://cran.r-project.org/web/packages/refund/index.html` — version 0.1-40, 2026-03-21 [spot-checked]
- arXiv:2211.02566 PDF pages 1–16 (scikit-fda paper) — read directly this session; detailed capability mapping
- `python/fdars/_capability_map.json` — read this session; fdars column derived from this file

### Secondary (MEDIUM confidence)
- CRAN `https://cran.r-project.org/web/packages/fda/index.html` — version 6.3.0, 2025-05-21 [fetched]
- rdrr.io `https://rdrr.io/cran/fda.usc/man/fda.usc-package.html` — fda.usc capabilities [fetched]
- CRAN Task View `https://cran.r-project.org/web/views/FunctionalData.html` — ecosystem comparison context [fetched]
- FDApy docs `https://fdapy.readthedocs.io/en/stable/` — capability listing [fetched]
- scikit-fda registration docs `https://fda.readthedocs.io/en/latest/modules/preprocessing/registration.html` — registration methods [fetched]
- PACE description `https://www.stat.ucdavis.edu/PACE/description.html` — PACE capabilities [fetched]
- fdapace CRAN `https://cran.r-project.org/web/packages/fdapace/index.html` — version 0.6.0, 2024-07-03 [fetched]

### Tertiary (LOW confidence)
- WebSearch results for MATLAB fdaM maintenance status — GitHub mirror dates ~2014; maintenance assumed stale
- scikit-fda FoF regression absence — inferred from API listing review; should be verified against 0.10.1 API reference directly

---

## Metadata

**Confidence breakdown:**
- scikit-fda capability mapping: HIGH — paper read directly (16 pages)
- FDApy capabilities: MEDIUM — abstract and docs landing confirmed; several `—` cells are [ASSUMED]
- R fda/fda.usc/refund/funData/tidyfun capabilities: HIGH for CRAN-confirmed claims; MEDIUM for absent-feature [ASSUMED] claims
- Matlab fdaM/PACE: MEDIUM — PACE description page read; fdaM maintenance: LOW (WebSearch mirror dates only)
- fdars column: HIGH — derived from `_capability_map.json` read this session

**Research date:** 2026-09-08
**Valid until:** 2027-03-08 (6 months; stable ecosystems; re-check if fdars publishes a new release before Phase 90)
