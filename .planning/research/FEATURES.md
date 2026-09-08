# Feature Research

**Domain:** FDA software-description paper — structure, comparison-table design, case-study conventions, table-stakes vs differentiators
**Researched:** 2026-09-08
**Confidence:** MEDIUM (web search + FDApy HTML page extracted; scikit-fda JSS section structure confirmed from search snippet; JOSS requirements from official docs; peer-package capability facts cross-checked against CRAN task view and PyPI docs)

---

## Purpose of This Document

This file answers four questions for the v14.0 arXiv preprint milestone:

(a) **Section skeleton** — recommended ordering for the fdars paper with what each section must contain.

(b) **Comparison-table design** — which peer packages to compare, which capability dimensions to use as rows, and how to state coverage honestly.

(c) **Case-study conventions** — what illustrative examples look like in comparable papers, keyed to the available `docs/data/` datasets (canadian_weather, growth, phoneme, tecator, sonar, wine).

(d) **Table stakes vs differentiators vs anti-features** — what a software paper must include, what can distinguish fdars, and what to explicitly omit (including benchmarks as excluded per project brief).

---

## Feature Landscape

### Table Stakes (Paper Must Have These)

Every credible FDA software paper in 2024 is expected to have these. Missing any makes reviewers reject the manuscript as incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Abstract (≤ 250 words, method-accurate) | All academic papers require it | LOW | Lead with "breadth of FDA method coverage" + sklearn compat + provenance; mention the differentiators in sentence 3 |
| Statement of need / motivation | JOSS mandatory; JSS expected; arXiv audience expects justification | LOW | State the Python FDA gap explicitly: only scikit-fda and FDApy exist, each with narrow scope; reference CRAN FDA richness as the benchmark |
| Brief FDA background (1-2 paragraphs) | Readers outside FDA community need orientation | LOW | Reference Ramsay & Silverman (2005) and Gertheiss et al. (2024) as the review paper; keep it to ≤ 1 page |
| Software architecture / design section | Explains what makes the package work; required by JOSS "Software design" section | MEDIUM | Cover Rust/PyO3/zero-copy qualitatively (no benchmarks), module map, Fdata container, sklearn layer |
| Capability tour by method family | Shows breadth; every FDA software paper does this | HIGH | Use code snippets, not wall of text; group by: represent/smooth → FPCA → depth/outliers → registration → regression families → inference → FTS/Fréchet/density → multi-domain → monitoring |
| Comparison with related software | JOSS mandatory ("State of the field"); JSS standard | MEDIUM | Formal table is expected by FDA community; narrative alone is insufficient |
| Illustrative case studies on real datasets | Demonstrates the paper's claims work in practice | HIGH | At least 2-3 studies; one per major capability cluster; use bundled docs/data/ datasets |
| Availability / installation section | Users need to know how to install | LOW | pip install fdars, optional extras, GitHub URL, CITATION.cff |
| References (grounded from _references_map.json) | Required; v13.0 already produced the bibliography | LOW | Use existing _references_map.json to generate refs.bib |

### Differentiators (Competitive Advantage)

Features that set fdars apart from scikit-fda and FDApy and justify "why a new package exists."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Breadth of FDA method coverage (437 callables, 31 modules) | scikit-fda covers ~6 capability clusters; fdars covers all major FDA families including FTS, Fréchet, density FDA, conformal, SPM, XAI — no other Python package covers this breadth | LOW to write | State coverage numbers derived from live `_capability_map.json`; be honest about coverage depth vs breadth tradeoff |
| PACE FPCA for sparse/irregular data | scikit-fda lacks PACE BLUP scoring; FDApy lacks PACE entirely | LOW | Python FDA gap: PACE was R-only (fdapace) and Matlab-only (PACE toolbox); fdars closes the Python gap |
| Full sklearn compatibility (28 estimators, zero check_estimator exemptions) | FDApy: no sklearn layer; scikit-fda: partial sklearn compat (some estimators) | LOW | v9.0 delivered this; emphasize Pipeline/GridSearchCV interop with example |
| AI advisor + scientific provenance layer | No other FDA package has an LLM-backed analysis advisor or a curated paper→callable provenance map | LOW | Unique; describe the grounding invariant (fdars computes, LLM interprets) in 1 paragraph; mention the MCP tool and capability skill |
| Functional time series (13 functions: FTSM, DPCA, fplsr, ACF/PACF, stationarity, long-run cov, spectral density) | No Python FDA package covers FTS; R has ftsa + freqdom.fda; Python has nothing equivalent | LOW | This is a genuine Python gap; state it clearly in comparison table |
| Fréchet regression + density FDA (LQD/Wasserstein) | No CRAN package for Fréchet regression; no PyPI package with LQD framing | LOW | Another genuine Python (and largely R) gap |
| Functional SPM / statistical process monitoring | No dedicated functional SPC package exists in any language | LOW | Genuine multi-language gap; highlight |
| Conformal prediction + tolerance bands for functional data | Only unmaintained R GitHub package; no Python equivalent | LOW | Emerging area; state with appropriate hedging |
| Rust core + zero-copy PyO3 architecture (qualitative only, no benchmarks) | Enables the broad capability surface without sacrificing correctness; GIL release via PyReadonly | LOW to write | Do NOT include benchmark numbers (user explicitly excluded); describe architecture qualitatively as "correctness-first, compute-second" |

### Anti-Features (Explicitly Exclude)

Things that would weaken the paper or that are explicitly out of scope.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Performance benchmarks (wall-clock, throughput, memory) | User explicitly excluded; Rust architecture mentioned only qualitatively; benchmark wars invite reviewer nitpicking and distract from breadth narrative | One sentence: "Performance benefits of the Rust backend are not the focus of this work; the design prioritizes correctness and breadth of method coverage." |
| API tutorial / exhaustive function listing | This is documentation, not a paper; JOSS explicitly says API docs belong in software docs, not the paper | Link to docs site; use a few illustrative code snippets only |
| Derivation of FDA methods | The paper is a software paper, not a methods paper | Reference the original papers (from _references_map.json) and keep method descriptions to one sentence each |
| Ablation studies or training-loss curves | These are ML training paper conventions; FDA software papers do not include them | Not applicable |
| Simulated-data benchmarks | Even without wall-clock numbers, synthetic comparison experiments on simulated data are out of scope (user excluded benchmarks) | Show real-data case studies instead |
| Section on future work that promises unbounded features | Weak in software papers; reviewers hold authors accountable | Keep conclusions tight: what is delivered, not what might be added |
| Overstating coverage depth for the long tail | _references_map.json has 28/437 curated entries — honesty required | State coverage as "breadth-first with 57 foundational papers documented; per-method depth varies" |

---

## (a) Recommended Section Skeleton

This skeleton is concrete and orderable — each section maps to a phase in the writing roadmap.

```
§1   Abstract                            [~200 words; write last]
§2   Introduction & Statement of Need    [~600 words]
§3   Brief FDA Background                [~300 words]
§4   Software Architecture               [~500 words + module-map figure]
§5   Data Representation                 [~300 words + code snippet]
§6   Capability Tour                     [~1200 words + code snippets, organized by family]
  §6.1  Representation, Smoothing & Basis
  §6.2  Functional Depth & Outlier Detection
  §6.3  Registration & Alignment
  §6.4  Dimension Reduction (FPCA — dense and PACE)
  §6.5  Functional Regression Families
  §6.6  Classification & Clustering
  §6.7  Statistical Inference
  §6.8  Functional Time Series
  §6.9  Fréchet Regression & Density FDA
  §6.10 Statistical Process Monitoring
  §6.11 scikit-learn Estimator Layer
  §6.12 AI Advisor & Scientific Provenance Layer
§7   Comparison with Related Software    [~400 words + formal table]
§8   Illustrative Case Studies           [~800 words + 3-4 figures]
  §8.1  Smooth + FPCA + classify on phoneme or growth
  §8.2  Registration + regression on canadian_weather or tecator
  §8.3  Functional time series on canadian_weather precipitation
  §8.4  (Optional) sklearn Pipeline on wine or sonar
§9   Availability & Installation         [~150 words]
§10  Conclusion                          [~200 words]
Acknowledgements
References                               [from paper/refs.bib generated by _references_map.json]
```

### What Each Section Must Contain

**§2 Introduction & Statement of Need**
- The FDA problem: infinite-dimensional data, standard statistics fails
- Why Python is the right ecosystem (NumPy/sklearn/matplotlib ecosystem)
- The Python FDA gap: only scikit-fda (narrow: one-dimensional, no FTS/Fréchet/SPM) and FDApy (narrow: FPCA + dimension reduction, no regression/classification/inference)
- R has richness spread across 30+ packages (fda, fda.usc, refund, fdapace, fdasrvf, ftsa, fdaoutlier, fdatest, etc.) but no Python package consolidates this surface
- What fdars provides: ~437 callables, 31 modules, sklearn compat, AI advisor
- Target audience: researchers in statistics, biomedical science, chemometrics, industrial QC, data scientists with Python backgrounds

**§3 Brief FDA Background**
- Functional observations as elements of L2; evaluation grids; basis expansions
- Key concepts: smoothing, FPCA, registration, depth, regression
- Point to Ramsay & Silverman (2005) and Gertheiss et al. (2024) for full treatments
- One equation at most (Karhunen-Loève expansion for FPCA is the canonical one to include)

**§4 Software Architecture**
- Layer diagram: Rust fdars-core → PyO3 zero-copy → Python API (Fdata + modules) → sklearn layer → AI advisor
- Rust/PyO3 binding model: qualitative "zero-copy via PyReadonly; GIL released for parallel Rust computation" — no benchmarks
- Module map table: 31 modules, callable counts per module (from _capability_map.json)
- Fdata container: data matrix (n_obs × n_points), argvals, rangeval, ids, metadata
- Optional extras: [sklearn], [mcp], [plot]

**§5 Data Representation**
- FDataGrid (discretized observations on shared grid) via fdars.Fdata
- Basis expansion path: fdata_to_basis_1d, bspline_basis, fourier_basis
- IrregFdata for PACE/sparse path (pace_fpca.PyIrregFdata)
- Contrast with scikit-fda (FDataGrid / FDataBasis), FDApy (DenseFunctionalData / IrregularFunctionalData)
- One code snippet: constructing an Fdata object from a numpy array

**§6 Capability Tour**
- For each subsection: 1-3 sentence description + 3-8 line code snippet
- Code snippets must execute against current fdars API (enforced by reproducible pipeline gate)
- Each snippet uses a dataset from docs/data/ or generates minimal synthetic data
- No derivations; cite foundational paper by name only (full citation in References)

**§7 Comparison with Related Software**
- Formal table (see section (b) below for design)
- Narrative: 2-3 paragraphs explaining the table. Key messages:
  (1) R ecosystem is the richest but fragmented across many packages
  (2) Python FDA options are narrow (scikit-fda: one-dimensional focus; FDApy: FPCA/dimension reduction only)
  (3) fdars consolidates the Python surface; Matlab (fdaM + PACE) is the closest in breadth but limited to Ramsay-era methods

**§8 Illustrative Case Studies**
- See section (c) below for design

**§9 Availability & Installation**
- pip install fdars
- pip install "fdars[sklearn,mcp,plot]" for full install
- GitHub URL: https://github.com/[owner]/pyfda
- License, CITATION.cff pointer
- Documentation: link to MkDocs site
- Python version support: 3.9-3.13

**§10 Conclusion**
- fdars delivers breadth of FDA methods in Python with correctness as the primary goal
- sklearn compatibility enables immediate use in existing ML workflows
- The AI advisor + provenance layer is a novel addition to the FDA software landscape
- No future-work promises that can't be delivered

---

## (b) Comparison-Table Design

### Recommended Table Structure

The table has **peer packages as columns** and **capability dimensions as rows**.

**Columns (Packages):**
| Column ID | Package | Language | Primary Reference |
|-----------|---------|----------|-------------------|
| fdars | fdars (this paper) | Python | — |
| skfda | scikit-fda | Python | Ramos-Carreño et al. (2024) JSS |
| FDApy | FDApy | Python | Golovkine (2025) JOSS |
| fda | fda (Ramsay) | R | Ramsay & Silverman (2005) + Ramsay et al. (2009) |
| fda.usc | fda.usc | R | Febrero-Bande & Oviedo de la Fuente (2012) JSS |
| refund | refund | R | Goldsmith et al. (2020) |
| fdapace | fdapace / PACE | R + Matlab | Yao, Müller & Wang (2005) |
| fdaM | fdaM (Ramsay) | Matlab | Ramsay & Silverman (2005) |

**Note on roahd:** roahd (R Journal 2019) is intentionally omitted from the main table because it covers only depth + outlier visualization and would create an imbalanced sparse column. Mention it in the narrative as a specialized depth package.

**Note on fdasrvf / fdasrsf:** These cover elastic registration only. Include a row note pointing to them rather than a full column.

**Rows (Capability Dimensions):**

Use check-mark symbols with optional qualifiers: ✓ (full), ◑ (partial), — (absent).

```
Row ID   | Capability Dimension             | What "full" means for fdars
---------|----------------------------------|-----------------------------
R01      | Data representation              | Grid + basis + irregular (IrregFdata)
R02      | Smoothing & basis estimation     | B-spline, Fourier, local-poly, kernel, P-spline GCV/AIC
R03      | Standard FPCA (dense)            | Covariance operator, eigenfunctions, scores, reconstruction
R04      | PACE FPCA (sparse/irregular)     | BLUP scores, fitted trajectories, prediction variance
R05      | Functional depth                 | ≥5 depth methods unified via dispatcher
R06      | Outlier detection                | ≥4 methods (magnitude/shape/tvdmss/muod/depthgram)
R07      | Registration & alignment         | Landmark, shift, elastic (SRSF/Fisher-Rao), banded
R08      | Scalar-on-function regression    | FPC, PLS, nonparametric kernel, robust, GLM family
R09      | Function-on-scalar regression    | fosr / function-on-scalar families
R10      | Function-on-function regression  | pffr / FOF families
R11      | Concurrent / varying-coeff regression | concurrent_regression
R12      | Functional classification        | kNN, LDA, QDA, DD-classifier, elastic multinomial
R13      | Functional clustering            | k-means, FunFEM, KCFC, DBSCAN, GMM, fuzzy c-means
R14      | Functional inference             | Permutation tests, SCBs, ITP interval testing, ANOVA
R15      | Functional time series           | FTSM forecasting, DPCA, ACF/PACF, long-run cov, stationarity
R16      | Fréchet / metric-space regression | Fréchet mean + local/global regression for non-Euclidean responses
R17      | Density FDA                      | LQD transform, Wasserstein barycenter
R18      | Multi-domain FDA                 | PyMultiFunData, MFPCA, FAMM
R19      | Statistical process monitoring   | T2/SPE, CUSUM, EWMA, ARL estimation
R20      | Conformal prediction (functional)| Conformal prediction bands, tolerance bands
R21      | scikit-learn compatibility       | BaseEstimator, Pipeline, check_estimator
R22      | Scientific provenance            | Curated paper→callable map, MCP reference tool
R23      | AI analysis advisor              | LLM-backed grounded advice with diagnostics
```

### Honest Coverage Statements

**fdars honest qualifiers:**
- R01: ✓ (grid + basis + IrregFdata)
- R02: ✓ (B-spline, Fourier, P-spline, kernel, local-poly, GCV, AIC)
- R03: ✓ (via regression.fpca)
- R04: ✓ (PACE BLUP, prediction variance — unique in Python)
- R05: ✓ (≥9 depth methods via functional_depth dispatcher)
- R06: ✓ (tvdmss, muod, depthgram, sequential_transform, LRT, outliergram, magnitude_shape)
- R07: ✓ (elastic/SRSF full surface, landmark, shift, banded, Bayesian)
- R08: ✓ (FPC, PLS, kernel, Huber, L1, additive, GLM, logistic)
- R09: ✓ (fosr, fosr_fpc, function-on-scalar families)
- R10: ✓ (fof_regression, fof_re_regression, fof_cv)
- R11: ✓ (concurrent_regression)
- R12: ✓ (9 classifiers)
- R13: ✓ (11 clustering methods)
- R14: ✓ (permutation tests, SCB, ITP, ANOVA — ITP unique in Python)
- R15: ✓ (13 FTS functions — unique in Python)
- R16: ✓ (unique in Python; no CRAN or PyPI equivalent)
- R17: ✓ (unique in Python with full LQD framing)
- R18: ✓ (PyMultiFunData, mfpca, spe_multivariate, FAMM)
- R19: ✓ (unique across all languages)
- R20: ✓ (unique in Python)
- R21: ✓ (28 estimators, zero check_estimator exemptions)
- R22: ✓ (unique: 57 papers, 243 entries, MCP tool, fdars-capabilities skill)
- R23: ✓ (unique: grounding invariant, 14 aspects, 4 providers, MCP server)

**scikit-fda honest qualifiers:**
- R01: ✓ (FDataGrid + FDataBasis, no true IrregFdata)
- R02: ✓
- R03: ✓
- R04: ◑ (partial: no PACE BLUP scoring)
- R05: ✓ (FM, band, modified band, projection-based)
- R06: ✓ (outliergram, boxplot-based; fewer methods than fdars)
- R07: ✓ (elastic via ElasticRegistration; shift; landmark)
- R08: ✓ (LinearFunctionalRegression, FPC-based)
- R09: — (not covered natively)
- R10: — (not covered)
- R11: — (not covered)
- R12: ✓ (kNN, nearest centroid, DDClassifier, nearest class centroid)
- R13: ✓ (FuzzyKMeans, KMeans functional)
- R14: ◑ (partial: Hotelling T2 via hotelling_t2; no ITP; no functional SCB)
- R15: — (no functional time series)
- R16: — (no Fréchet regression)
- R17: — (no density FDA / LQD)
- R18: — (multivariate on same domain only; no multi-domain MFPCA)
- R19: — (no SPM)
- R20: — (no conformal prediction)
- R21: ✓ (sklearn API is core design; most estimators check_estimator compliant)
- R22: — (no provenance layer)
- R23: — (no AI advisor)

**FDApy honest qualifiers:**
- R01: ✓ (DenseFunctionalData, IrregularFunctionalData; multi-dimensional domains)
- R02: ✓ (P-splines smoothing)
- R03: ✓ (FPCA via diagonalization of covariance operator)
- R04: ✓ (MFPCA for sparse/irregular via IrregularFunctionalData)
- R05: — (no depth methods as of v1.x)
- R06: — (no outlier detection)
- R07: — (no registration)
- R08: — (no regression)
- R09: — (no regression)
- R10: — (no regression)
- R11: — (no regression)
- R12: — (no classification)
- R13: — (no clustering)
- R14: — (no inference)
- R15: — (no FTS)
- R16: — (no Fréchet)
- R17: — (no density FDA)
- R18: ✓ (multi-dimensional domains, multiFunData)
- R19: — (no SPM)
- R20: — (no conformal)
- R21: — (no sklearn layer)
- R22: — (no provenance)
- R23: — (no AI advisor)

**fda (R) honest qualifiers:**
- R01: ✓ (fd class, basis expansions, evaluation grid)
- R02: ✓ (smooth.basis, penalized spline)
- R03: ✓ (pca.fd)
- R04: — (no PACE; use fdapace separately)
- R05: ◑ (limited: no dedicated depth functions; use fda.usc or ddalpha)
- R06: — (no outlier detection)
- R07: ✓ (register.fd: landmark + shift)
- R08: ✓ (fRegress: FPC and penalized regression)
- R09: ✓ (fRegress: function-on-scalar)
- R10: ◑ (fRegress has limited FOF support; refund needed for pffr)
- R11: ✓ (fRegress with pointwise basis)
- R12: — (no classification)
- R13: — (no clustering; use fda.usc)
- R14: — (no permutation tests; use fda.usc or fdANOVA)
- R15: — (no FTS; use ftsa)
- R16: — (no Fréchet)
- R17: — (no density FDA)
- R18: — (no multi-domain)
- R19: — (no SPM)
- R20: — (no conformal)
- R21: — (no sklearn equiv)
- R22: — (no provenance)
- R23: — (no AI)

**fda.usc (R) honest qualifiers:**
- R01: ✓ (fdata class)
- R02: ✓ (optim.np, kernel smoothing)
- R03: ✓ (fdata.comp via FPCA)
- R04: — (no PACE)
- R05: ✓ (depth.FM, depth.BD, depth.mode, depth.RP — comprehensive)
- R06: ✓ (fdata.outliers, Febrero-Bande et al. methods)
- R07: — (no registration; use fda or fdasrvf)
- R08: ✓ (fregre.np, fregre.lm, fregre.pls, fregre.gsam)
- R09: — (use refund)
- R10: — (use refund)
- R11: — (no concurrent)
- R12: ✓ (classif.knn, classif.lda, classif.qda, classif.kernel)
- R13: ✓ (kmeans.fd, fclust functions)
- R14: ✓ (fanova.onefactor, Wilcoxon functional test)
- R15: — (no FTS)
- R16: — (no Fréchet)
- R17: — (no density FDA)
- R18: — (no multi-domain)
- R19: — (no SPM)
- R20: — (no conformal)
- R21: — (no sklearn)
- R22: — (no provenance)
- R23: — (no AI)

**refund (R) honest qualifiers:**
- R01: ◑ (fdata objects not its own representation; delegates to fda)
- R02: ◑ (penalized spline via pfr/pffr; not standalone smoothing)
- R03: ✓ (fpca.sc, fpca.face, fpca.ssvd, fpca2s — excellent sparse FPCA)
- R04: ✓ (fpca.sc with sparse data; not PACE but comparable quality)
- R05: — (no depth)
- R06: — (no outlier detection)
- R07: — (use registr separately)
- R08: ✓ (pfr: penalized FPC, spline, FPCR)
- R09: ✓ (fosr, fosr2s)
- R10: ✓ (pffr: function-on-function, excellent)
- R11: ✓ (peer, ccb for concurrent)
- R12: — (no classification)
- R13: — (no clustering)
- R14: ◑ (limited inference; use fdANOVA separately)
- R15: — (no FTS)
- R16: — (no Fréchet)
- R17: — (no density FDA)
- R18: — (no multi-domain)
- R19: — (no SPM)
- R20: — (no conformal)
- R21: — (no sklearn)
- R22: — (no provenance)
- R23: — (no AI)

**fdapace / PACE (R + Matlab) honest qualifiers:**
- R01: ◑ (sparse trajectory input; no basis expansion)
- R02: ◑ (covariance smoothing only, not general basis)
- R03: ✓ (dense FPCA via pca_fd / pca.fd path)
- R04: ✓ (PACE BLUP: the definitive reference implementation)
- R05: — (no depth; PACE Matlab has trajectory boxplot only)
- R06: — (no systematic outlier detection)
- R07: ◑ (PACE-WARP in Matlab: time synchronization; limited)
- R08: ✓ (PACE-REG in Matlab; fdapace: FLM scalar-on-function)
- R09: — (limited)
- R10: — (PACE-SVD in Matlab only; R fdapace limited)
- R11: — (PACE-GRM: generalized repeated measures, not classic concurrent)
- R12: — (no general classification; PACE has FSIM for functional index models)
- R13: ◑ (PACE-KCFC in Matlab: k-center functional clustering)
- R14: — (no formal testing module)
- R15: — (no FTS)
- R16: — (no Fréchet)
- R17: — (no density FDA)
- R18: — (no multi-domain)
- R19: — (no SPM)
- R20: — (no conformal)
- R21: — (no sklearn)
- R22: — (no provenance)
- R23: — (no AI)

**fdaM (Matlab, Ramsay) honest qualifiers:**
- R01: ✓ (basis expansion: B-spline, Fourier, constant; fd objects)
- R02: ✓ (smooth_basis, penalized spline, GCV)
- R03: ✓ (pca_fd)
- R04: — (no PACE; use PACE toolbox separately)
- R05: — (no depth functions in fdaM)
- R06: — (no outlier detection)
- R07: ✓ (register_fd: landmark + shift)
- R08: ✓ (fRegress: FPC and penalized)
- R09: ✓ (fRegress: function-on-scalar)
- R10: ◑ (limited in fdaM; no full pffr equivalent)
- R11: ✓ (fRegress with pointwise basis = concurrent)
- R12: — (no classification)
- R13: — (no clustering)
- R14: — (no formal inference module)
- R15: — (no FTS)
- R16: — (no Fréchet)
- R17: — (no density FDA)
- R18: — (no multi-domain)
- R19: — (no SPM)
- R20: — (no conformal)
- R21: — (no sklearn)
- R22: — (no provenance)
- R23: — (no AI)

### Dependency: Comparison Table Needs Peer Coverage Verification

**Flag for roadmap author:** The peer coverage facts above are based on web search and CRAN task-view inspection (MEDIUM confidence). Before final manuscript submission, each ◑ and ✓ entry for peer packages should be spot-checked against the package documentation or a test run. This is a Phase deliverable — assign a verification step. The fdars column is grounded from the live `_capability_map.json` (HIGH confidence).

---

## (c) Illustrative Case Study Conventions

### What Comparable Papers Do

FDA software papers use real datasets that are canonical in the field. The preferred figure types are:

1. **Trajectory plots** — raw or smoothed functional observations over the evaluation grid; demonstrates representation
2. **Mean and variance band** — sample mean ± 1 SD functional band; demonstrates functional statistics
3. **Eigenfunction plots** — first 2-3 FPCA modes; demonstrates dimension reduction
4. **Depth rank plot / functional boxplot** — central tube + outlier flags; demonstrates depth
5. **Aligned vs unaligned trajectories** — before/after registration; demonstrates alignment
6. **Regression coefficient function** — scalar-on-function regression beta(t) over the grid; demonstrates regression
7. **Classification decision boundary or confusion matrix** — demonstrates classification
8. **Forecasting plot** — future trajectory fan; demonstrates FTS

FDApy (arXiv 2101.11003v2) uses: Canadian weather (35 city temperature + precipitation lines), Primary Biliary Cirrhosis (irregular longitudinal biomarkers), NBA shooting position density maps. All plotted as line trajectories.

scikit-fda paper uses: Canadian weather (smooth + classify), Berkeley growth curves, phoneme log-periodograms (classification). Datasets are also bundled in the package (fetch_weather, fetch_growth, fetch_phoneme equivalents).

The FDApy pattern of **3 datasets × 1 primary figure each** is the minimum expected. A richer paper uses **3-4 datasets × 2 figure panels each** (raw + analyzed).

### Recommended Case Studies for fdars

The available `docs/data/` datasets and their natural case-study mappings:

**Study 1: Smoothing + FPCA + Classification (phoneme.csv or growth.csv)**

- Dataset: `phoneme.csv` — log-periodograms of 5 phoneme classes; OR `growth.csv` — Berkeley growth curves (boys/girls)
- Pipeline: smooth raw profiles → FPCA (show first 2 eigenfunctions) → classify with functional kNN or LDA
- Figures: (a) raw trajectories colored by class, (b) first 2 eigenfunctions, (c) classification accuracy table
- Why it works: demonstrates the most frequently cited FDA pipeline (smooth → reduce → classify); datasets are canonical in the FDA literature and appear in scikit-fda and FDApy papers as well
- Code: ~15 lines using `fdars.smoothing.nadaraya_watson` + `fdars.regression.fpca` + `fdars.classification.fclassif_lda`

**Study 2: Registration + Scalar-on-Function Regression (canadian_weather.csv or tecator.csv)**

- Dataset preferred: `tecator.csv` — fat/moisture/protein content from NIR absorbance spectra; OR `canadian_weather.csv` — predict annual precipitation from temperature curves
- Pipeline: (1) elastic registration to remove phase variation, (2) scalar-on-function FPC regression, (3) show regression coefficient function beta(t)
- Figures: (a) unregistered vs registered absorbance curves, (b) regression coefficient function with CI
- Why it works: showcases two key fdars capability clusters (alignment + regression) that scikit-fda does not cover together; tecator is the chemometrics community benchmark
- Code: ~20 lines using `fdars.alignment.karcher_mean` + `fdars.regression.fregre_lm`

**Study 3: Functional Time Series Forecasting (canadian_weather.csv precipitation)**

- Dataset: `canadian_weather_precip.csv` — daily precipitation across 35 Canadian cities, multiple years
- Pipeline: treat each city×year as a functional observation → FTSM model → 1-step-ahead forecast
- Figures: (a) observed precipitation trajectories, (b) forecasted trajectories with uncertainty bands
- Why it works: demonstrates fdars FTS capability which is absent from all Python FDA alternatives; connects to the Hyndman & Shang (2009) classic paper; uses the most famous FDA dataset
- Code: ~15 lines using `fdars.fts.ftsm` + `fdars.fts.ftsm_forecast`

**Study 4 (Optional): sklearn Pipeline on wine.csv or sonar.csv**

- Dataset: `wine.csv` (13 features, 3 classes) or `sonar.csv` (60 frequency features, 2 classes)
- Pipeline: FPCATransformer → RandomForestClassifier (native sklearn estimator) via sklearn Pipeline
- Figures: (a) cross-validation accuracy by number of FPCs, (b) Pipeline diagram (reference the docs SVG)
- Why it works: demonstrates sklearn compatibility uniquely; none of the peer packages (FDApy, fdaM, PACE) have this; shows interop with native sklearn estimators
- Code: ~10 lines using `fdars.sklearn.FPCATransformer` + sklearn `Pipeline` + `cross_val_score`

### Conventions for the Reproducible Pipeline

- All case-study figures must be generated by `paper/code/` and committed to `paper/figures/`
- Use `numpy.random.seed(42)` or Rust seeded methods for determinism
- No network access at figure-generation time (offline gate)
- Each case study should produce ≤ 2 figures with meaningful axis labels
- Figure resolution: 150 dpi minimum for arXiv (PDF vector preferred via matplotlib savefig PDF)
- Figure size: 3.5 inches wide (single column) or 7 inches wide (double column) for arXiv preprint

---

## Feature Dependencies

```
Section skeleton (§) depends on:
  §5 Data Representation → must show Fdata and IrregFdata APIs correctly
  §6 Capability Tour → each snippet must execute against current fdars (CI gate)
  §7 Comparison Table → peer coverage facts need spot-check verification
  §8 Case Studies → figures must come from paper/code/ reproducible pipeline

Comparison table depends on:
  _capability_map.json → fdars column is grounded HERE; do not hand-derive
  Peer coverage spot-check → phase deliverable; MEDIUM confidence until done

Case studies depend on:
  docs/data/ datasets (existing, no new downloads needed)
  fdars installed in the paper/code/ Python environment

refs.bib depends on:
  python/fdars/_references_map.json (57 papers from v13.0)
  LaTeX formatting pass to convert JSON to BibTeX
```

### Dependency Notes

- **Comparison table column for fdars is authoritative from _capability_map.json:** The live 437-callable map is the ground truth; do not re-derive capability counts manually. Pull them at LaTeX generation time.
- **Peer coverage is MEDIUM confidence until verified:** The table above is research-quality but should be spot-checked against current package versions before paper submission. Assign a verification sub-task.
- **Case study code must execute against current fdars API:** The reproducible pipeline gate enforces this. A snippet that fails the pipeline must be fixed before the phase closes.
- **FTS case study (§8.3) requires canadian_weather_precip.csv as a time-series of curves:** Verify the dataset structure supports multiple-year slicing before writing the phase plan.

---

## MVP Definition

### Phase A: Manuscript Scaffold

Write §§1-4 (abstract placeholder, intro, FDA background, architecture). These sections depend on no experimental results and can be written first.

- [ ] §2 Introduction with explicit Python FDA gap argument
- [ ] §3 FDA background (≤ 300 words, Karhunen-Loève equation, ≤ 3 key references)
- [ ] §4 Architecture (module-map table from _capability_map.json, layer diagram figure)

### Phase B: Capability Tour + Comparison Table

- [ ] §6 Capability tour with runnable snippets (one per subsection from §6.1-§6.12)
- [ ] §7 Comparison table (formal LaTeX table using the row/column design above)

### Phase C: Case Studies + Figures

- [ ] §8.1-§8.3 case studies written with figures from reproducible pipeline
- [ ] paper/figures/ committed with deterministic output

### Phase D: Close + Polish

- [ ] §1 Abstract (write last when everything is stable)
- [ ] §5 Data Representation (short section, write during Phase B alongside capability tour)
- [ ] §9 Availability
- [ ] §10 Conclusion
- [ ] refs.bib generated from _references_map.json
- [ ] CITATION.cff authored
- [ ] PDF compile via CI tectonic (no local TeX needed)
- [ ] Human manuscript read-through approved

---

## Sources

- [FDApy arXiv 2101.11003v2 HTML](https://arxiv.org/html/2101.11003v2)
- [FDApy JOSS 10.21105/joss.07526](https://joss.theoj.org/papers/10.21105/joss.07526)
- [scikit-fda JSS v109i02](https://www.jstatsoft.org/article/view/v109i02)
- [scikit-fda arXiv 2211.02566](https://arxiv.org/abs/2211.02566)
- [JOSS Paper Format official docs](https://joss.readthedocs.io/en/latest/paper.html)
- [roahd R Journal 2019](https://journal.r-project.org/articles/RJ-2019-032/)
- [fda.usc JSS v051i04](https://www.jstatsoft.org/article/view/v051i04)
- [refund GitHub](https://github.com/refunders/refund)
- [PACE Matlab UC Davis description](https://www.stat.ucdavis.edu/PACE/description.html)
- [CRAN Task View Functional Data Analysis](https://cran.r-project.org/view=FunctionalData)
- [Gertheiss et al. (2024) FDA review arXiv 2312.05523](https://arxiv.org/abs/2312.05523)
- [fdars _capability_map.json — 437 callables, 31 modules](file:///home/simonm/projects/rust/pyfda/python/fdars/_capability_map.json)
- [sktime NeurIPS 2019 paper](http://learningsys.org/neurips19/assets/papers/sktime_ml_systems_neurips2019.pdf)
- [tslearn JMLR 2020](https://www.jmlr.org/papers/v21/20-091.html)

---

*Feature research for: v14.0 fdars Software Paper — arXiv Preprint*
*Researched: 2026-09-08*
