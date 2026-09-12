# Introduction

## Statement of need {#statement-of-need .unnumbered}

Functional data analysis (FDA) addresses data where the fundamental observation is a curve, surface, or trajectory evaluated over a continuum---temperature records over a year, spectroscopic absorption profiles, or gait acceleration waveforms. Rather than treating each observed value as an independent scalar, FDA represents entire trajectories as elements of a function space, enabling operations such as depth-based centrality ranking, elastic alignment of phase variation, FPCA-based dimension reduction, and scalar- or function-on-function regression. Practitioners working in Python have relatively few mature options. `scikit-fda` 0.10.1 [@ramoscarreno_scikitfda_2024] is the strongest existing Python peer: it provides representation and basis smoothing, elastic registration, functional depth and outlier detection, dense FPCA, clustering, classification, and scalar-on-function regression. However, as documented in Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}, it does not cover functional time series forecasting, statistical process monitoring, conformal prediction and tolerance bands, density/Fréchet/metric-space methods, or sparse PACE FPCA; it offers no grounded parameter advisor and no scientific-provenance layer. `FDApy` 1.0.3 [@happ_greven_2018] focuses on representation, multivariate FPCA, and simulation, and does not address the remaining families at all. In R, the relevant methods are distributed across multiple packages: `fda` covers representation, smoothing, registration, and dense FPCA; `fda.usc` adds depth, classification, and scalar-on-function regression; `refund` provides scalar- and function-on-function regression and several FPCA variants; `funData`/`tidyfun` offer data-structure infrastructure. No single R package spans all the method families listed in Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}, and coordinating across these packages requires manual data conversion at each interface boundary. The Matlab toolkits fdaM (\~2014) and PACE (v2.17, 2015) remain in partial maintenance and cannot be used in Python workflows without external bridges.

`fdars` is designed to fill this gap. It is the only Python library, to our knowledge, that covers all 30 method families---spanning 409 public callables---in a single importable package, with scikit-learn compatibility and a grounded advisor and scientific-provenance layer absent from all compared packages (see Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}). We make no performance claims here; the design section (§[2](#sec:design){reference-type="ref" reference="sec:design"}) describes the architecture qualitatively.

## Background: functional data analysis {#background-functional-data-analysis .unnumbered}

Functional data analysis treats data as realisations of a random process $X(t)$, $t \in \mathcal{T}$, where each observation is an element of an infinite-dimensional function space rather than a finite-dimensional vector [@ramsay_silverman_2005; @ramsay_dalzell_1991]. In practice, observations are recorded at discrete evaluation points and represented via basis expansions (B-splines, Fourier), kernel smoothing, or directly as dense grids; when observations are sparse and irregular, methods such as PACE [@yao_muller_wang_2005] recover the latent smooth trajectory from noisy longitudinal measurements. Functional principal component analysis (FPCA) reduces dimension by projecting onto a data-adaptive orthonormal basis of eigenfunctions, playing the role that PCA plays in multivariate analysis [@ramsay_silverman_2005]. Elastic registration [@srivastava_klassen_2016; @marron_ramsay_sangalli_srivastava_2015] separates amplitude from phase variation by aligning curves under a group of diffeomorphic reparametrisations before downstream inference. Further families---including regression, depth, clustering, functional time series [@hormann_kokoszka_2010; @hyndman_ullah_2007], and process monitoring---extend classical multivariate techniques to the functional setting; @ferraty_vieu_2006 and @ramsay_silverman_2005 survey the field comprehensively.

## Contributions and paper outline {#contributions-and-paper-outline .unnumbered}

This paper describes `fdars`, documenting: (1) the software design and Rust/PyO3 architecture (§[2](#sec:design){reference-type="ref" reference="sec:design"}); (2) the data-representation model and `Fdata` container (§[3](#sec:represent){reference-type="ref" reference="sec:represent"}); (3) a capability tour by method family, with executed, script-sourced code snippets (§[4](#sec:capabilities){reference-type="ref" reference="sec:capabilities"}); (4) the grounded AI advisor and scientific-provenance contribution, which are absent from all compared packages (§[6](#sec:advisor){reference-type="ref" reference="sec:advisor"}); and (5) availability and installation information (§[9](#sec:availability){reference-type="ref" reference="sec:availability"}).

# Software Design and Architecture {#sec:design}

## Layered Architecture

<figure id="fig:architecture" data-latex-placement="ht">

<figcaption>Three-layer architecture of <code>fdars</code>. NumPy arrays cross the PyO3 boundary with a row-major <span class="math inline">→</span> column-major layout conversion (<code>src/convert.rs</code>); <code>PyReadonlyArray</code> wrappers prevent concurrent Python mutation without an extra data copy.</figcaption>
</figure>

`fdars` is organised as three cooperating layers (Figure [1](#fig:architecture){reference-type="ref" reference="fig:architecture"}).

**Computation core.** Numerical algorithms live in the external Rust crate `fdars-core`, which provides the `FdMatrix` linear-algebra abstraction backed by `nalgebra` and data-parallel loops via `rayon`. `fdars-core` 0.14.0 is the minimum required version declared in `Cargo.toml`, compiled with the `parallel` feature to enable rayon-backed parallelism. No Python objects cross into this layer; all communication occurs through the binding layer described next, and `fdars-core` exports no Python-facing symbols.

**PyO3 binding layer.** A set of 30 Rust modules (one per functional category) exposes `fdars-core` algorithms to Python via [PyO3](https://pyo3.rs) 0.28. Each binding function is annotated `#[pyfunction]` and accepts NumPy arrays through `PyReadonlyArray` wrappers, which hold a read-only view of the caller's array for the duration of the Rust call without an extra data copy, and prevent concurrent Python mutation of the array during Rust execution. Default parameter values are declared with `#[pyo3(signature = (...))]` at the function level, allowing idiomatic Python keyword-argument syntax at call sites. All modules are registered via a shared macro (`registersubmodule!`) in `src/lib.rs` that creates a `PyModule`, calls the module's `register` function, and attaches the submodule to the parent extension --- so adding a new algorithm family requires only one new `mod.rs` file and one macro invocation.

**Boundary convention.** The PyO3 boundary involves a layout conversion: NumPy stores two-dimensional arrays in C (row-major) order, while `fdars-core`'s `FdMatrix` is column-major. The conversion function `numpy2dtofdmatrix` (see `src/convert.rs`) performs an explicit element-wise transpose: given an $(n_\mathrm{obs} \times
n_\mathrm{points})$ NumPy array in C order it builds the column-major flat vector required by `FdMatrix::fromcolumnmajor`. The reverse function `fdmatrixtonumpy2d` calls `torowmajor()` before allocating the output array. The `PyReadonlyArray` wrapper avoids an extra data copy for the view itself, but a layout conversion is always present at the 2D matrix boundary. Errors from `fdars-core` propagate as Rust `Result<T, FdarError>` values and are converted to Python `ValueError` exceptions by the helper `topyresult` in `src/convert.rs`, so users receive descriptive error messages rather than opaque panics.

**Python API layer.** On top of the native extension, a pure-Python layer provides idiomatic Python-level conveniences: the `Fdata` object-oriented container (Section [3](#sec:represent){reference-type="ref" reference="sec:represent"}), the `clusteroptim` parameter-search orchestrator, the grounded advisor module (Section [6](#sec:advisor){reference-type="ref" reference="sec:advisor"}), plotting utilities (`fdars.plot`), ergonomic dataset loaders (`fdars.datasets`), and the scikit-learn estimator wrappers described in Section [2.4](#subsec:sklearn){reference-type="ref" reference="subsec:sklearn"}. The module registry in `python/fdars/init.py` iterates over a fixed list of submodule names, attaches each to `sys.modules`, and injects pure-Python helpers into native submodule namespaces via `augment.install()`, so both `fdars.depth.fraimanmuniz1d` and `from fdars.depth import fraimanmuniz1d` resolve correctly.

## Module Map

`fdars` exposes 30 public submodules and 409 public callables organised by method family:

Representation, basis and smoothing

: `fdata`, `represent`, `basis`, `smoothing` --- functional object construction, derivative estimation, basis expansion, GCV-penalised smoothing, interpolation, resampling; `multifdata` --- opaque container for multivariate functional data (`PyMultiFunData`), grouping multiple `FdMatrix` components under a single handle for joint analysis.

Alignment

: `alignment` --- elastic registration via the square-root slope function (SRSF) framework [@srivastava_et_al_2011], including pairwise warping and Karcher mean under the elastic metric.

Depth, outliers and scoring

: `depth`, `outliers`, `scoring` --- Fraiman--Muniz depth [@fraiman_muniz_2001], band depth [@lopez_pintado_romo_2009], the outliergram [@arribas_gil_romo_2014], MUOD, and magnitude-shape (MS) detection [@dai_genton_2019].

FPCA and sparse/longitudinal PACE

: `fdata` (via `Fdata.topc`), `pacefpca` --- dense FPCA and the PACE algorithm for irregularly observed trajectories [@yao_muller_wang_2005].

Clustering and classification

: `clustering`, `classification`, `shapelet` --- $k$-means for functional data, fuzzy $c$-means, Gaussian mixture models; $k$-NN, LDA, QDA, and DD-classifiers.

Regression

: `regression`, `scalaronfunction`, `famm` --- scalar-on-function (FPC-based and non-parametric), function-on-function regression, and functional additive mixed models.

Functional time series and seasonal decomposition

: `fts` --- functional time-series modelling via the FTSM framework [@hyndman_ullah_2007] with multi-step forecasting; `seasonal` --- seasonal decomposition for functional time series (trend, seasonal component, and remainder extraction).

Statistical process monitoring

: `spm` --- phase-1 baseline estimation and phase-2 monitoring via functional $T^2$ and SPE statistics.

Conformal prediction and tolerance bands

: `conformal`, `tolerance` --- FPCA-based tolerance bands and conformal scalar-on-function prediction intervals.

Density, Fréchet and metric

: `densityfda`, `frechet`, `metric` --- log-quantile-density FPCA, Wasserstein barycenter [@agueh_carlier_2011], Fréchet mean [@petersen_muller_2016], and $L^p$/DTW distance matrices.

Inference, explanation and simulation

: `inference`, `explain`, `simulation` --- functional ANOVA, permutation and bootstrap tests; shapelet explanation; Gaussian-process and basis-expansion simulation.

This organisation mirrors the taxonomy used in the comparison table (Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}); see Section [5](#sec:comparison){reference-type="ref" reference="sec:comparison"} for a side-by-side evaluation of method coverage across peer packages.

## The `Fdata` Container {#subsec:fdata}

At the Python level, `Fdata` is the central object for dense functional data. It bundles the $(n_\mathrm{obs} \times n_\mathrm{points})$ observation matrix with a shared evaluation grid (`argvals`), a domain interval (`rangeval`), optional observation identifiers (`id`), optional variable names (`names`), and optional sample-level metadata (`metadata`). The container exposes 27 public methods --- including `mean`, `center`, `depth`, `topc`, `tobasis`, `deriv`, `norm`, `distance`, `cov`, and `geometricmedian` --- each of which delegates to the appropriate binding or pure-Python function and returns results in a consistent format (NumPy arrays or dicts). Section [3](#sec:represent){reference-type="ref" reference="sec:represent"} describes the data model in detail.

## Scikit-learn Estimator Layer {#subsec:sklearn}

A pure-Python scikit-learn-compatible layer wraps the most commonly used bindings as `BaseEstimator`/`TransformerMixin` subclasses (`fdars.sklearn.skeletons`). 28 estimators pass the full `checkestimator` battery [@pedregosa_sklearn_2011], covering smoothing and basis transformers, FPCA-based regression and classification, depth-based classifiers and outlier detectors, and functional clustering estimators (e.g., `FPCATransformer`, `FPCRegressor`, `FunctionalKMeans`, `LRTOutlierDetector`).

Conformance with `checkestimator` carries concrete guarantees: the estimator's `getparams`/`setparams` round-trip correctly (enabling hyperparameter grid search), `clone` produces an independent copy, and each estimator is picklable (required for multi-process cross-validation via `GridSearchCV(njobs=-1)`). These estimators therefore integrate without modification into `sklearn.pipeline.Pipeline` and cross-validation utilities, as illustrated in the capability tour (Section [4](#sec:capabilities){reference-type="ref" reference="sec:capabilities"}).

Some methods in `fdars` are deliberately excluded from the estimator layer (13 methods, listed in `fdars.sklearn.EXCLUDEDMETHODS`) because their interfaces do not fit the stateless `fit`/`transform` contract --- for example, paired elastic alignment (`alignment.elasticalignpair`), the Karcher mean (`alignment.karchermean`), and the PACE FPCA (`pacefpca.pacefpca`, which requires ragged per-observation grids rather than a rectangular matrix). This boundary is documented transparently so that users building custom pipelines know which methods to call directly.

# Data Representation {#sec:represent}

Functional data analysis treats each observation as a function --- a curve, surface, or trajectory --- rather than a finite-dimensional vector. `fdars` provides two complementary representations tailored to the two most common sampling regimes: densely observed data on a shared grid, and sparsely or irregularly observed longitudinal data with per-subject grids of differing length.

<figure id="fig:datamodel" data-latex-placement="ht">

<figcaption>The <code>Fdata</code> data model. An <span class="math inline">(<em>n</em><sub>obs</sub> × <em>n</em><sub>points</sub>)</span> NumPy observation matrix shares a common <code>argvals</code> evaluation grid and domain <code>rangeval</code>, with optional per-observation <code>id</code>, axis <code>names</code>, and sample-level <code>metadata</code>. For irregularly sampled data, <code>PyIrregFdata</code> stores per-observation grids of differing length, consumed exclusively by the PACE FPCA algorithm.</figcaption>
</figure>

## Dense Data: the `Fdata` Container

For the common case in which all $n_\mathrm{obs}$ functions are observed at the same $n_\mathrm{points}$ grid points, `fdars` uses the `Fdata` class (`python/fdars/fdataclass.py`) (Figure [2](#fig:datamodel){reference-type="ref" reference="fig:datamodel"}). A `Fdata` object bundles:

- **`data`** --- an $(n_\mathrm{obs} \times n_\mathrm{points})$ NumPy array. Observations occupy rows; column index runs over the evaluation grid. The constructor validates shape and raises `ValueError` when dimensions are inconsistent.

- **`argvals`** --- a one-dimensional array of $n_\mathrm{points}$ grid points (the evaluation abscissae). When omitted, a uniform grid on $[0, 1]$ is inferred. For the Berkeley Growth Study, for example, `argvals` holds the 31 measurement ages (years $1$--$18$).

- **`rangeval`** --- a two-tuple $(\mathrm{min}, \mathrm{max})$ giving the functional domain. If not supplied it is derived automatically from `argvals`. Methods such as `deriv` and `normalize` use `rangeval` to orient the domain of each functional observation.

- **`id`** --- an optional sequence of string labels identifying each observation (e.g. subject codes).

- **`names`** --- an optional dictionary carrying axis-label metadata (e.g. `{"x": "Age (years)", "y": "Height (cm)"}`).

- **`metadata`** --- an optional `pandas.DataFrame` (or dict convertible to one) with one row per observation, storing sample-level covariates such as sex or group membership.

The capability tour (Section [4](#sec:capabilities){reference-type="ref" reference="sec:capabilities"}) opens with an executed snippet that constructs an `Fdata` object from the Growth dataset and prints its `repr`; the output confirms the $(n_\mathrm{obs} \times
n_\mathrm{points})$ shape and the inferred `rangeval`. Key read-only properties (`nobs`, `npoints`, `rangeval`, `data`, `argvals`) expose the container fields without copying.

`Fdata` exposes 27 public methods. The most commonly used are `mean()` (cross-sectional pointwise mean), `center()` (subtract the mean to produce a centred `Fdata`), `deriv(nderiv=1)` (numerical differentiation), `norm()` ($L^2$ norm of each curve), `normalize()` (scale each curve to unit norm), `depth(method=...)` (functional depth via Fraiman--Muniz, band depth, or other methods), `topc(ncomp=...)` (dense FPCA, returning scores, rotation, singular values, and centred data), `tobasis(type=...)` (basis expansion), `distance(method=...)` (pairwise distance matrix), `cov()` (Bessel-corrected pointwise covariance surface), and `geometricmedian()` (the $L^1$ functional median). Each method delegates to the appropriate PyO3 binding and returns results in consistent format (NumPy arrays or dicts).

`Fdata` supports standard arithmetic operators (`+`, `-`, `*`, `/`) enabling functional arithmetic, a `getitem` slice interface for sub-sampling observations, and `len` returning `nobs`. Observations can be concatenated via `concat()`, downsampled via `downsample()`, imputed via `impute()`, and interpolated onto a new grid via `interpolate()`. All computationally intensive operations delegate to the PyO3 binding layer described in Section [2](#sec:design){reference-type="ref" reference="sec:design"}; the Python class holds no redundant copies of the underlying array.

## Irregular and Sparse Data: `PyIrregFdata` {#subsec:irreg}

Many longitudinal studies produce functional observations sampled at different, subject-specific time points --- a regime sometimes called *sparse functional data* [@yao_muller_wang_2005]. The dense $(n_\mathrm{obs} \times n_\mathrm{points})$ matrix of `Fdata` is not applicable here because the per-subject grids differ in both length and location.

`fdars` represents irregularly sampled functional data through the `fdars.pacefpca.PyIrregFdata` container, constructed with the factory function:

``` {.python language="Python" style="fdarsinput"}
from fdars.pace_fpca import irreg_fdata_from_lists
irreg = irreg_fdata_from_lists(argvals_list, values_list)
```

where `argvalslist` is a Python list of per-observation grid arrays (each of arbitrary length) and `valueslist` is the corresponding list of observed values. The result is a `PyIrregFdata` object that the PACE FPCA algorithm (`fdars.pacefpca.pacefpca`) accepts as its primary input:

``` {.python language="Python" style="fdarsinput"}
result = fdars.pace_fpca.pace_fpca(irreg, ncomp=2, bandwidth=0.1)
```

PACE (Principal Analysis by Conditional Expectation, @yao_muller_wang_2005) estimates mean and covariance functions via local polynomial smoothing and recovers FPCA scores for each subject even when individual trajectories are observed at only a handful of time points. The capability tour (Section [4](#sec:capabilities){reference-type="ref" reference="sec:capabilities"}) demonstrates this path with a synthetic irregularly sampled dataset; see also the FPCA family snippet.

There is no top-level `fdars.IrregFdata` class; the public container is `PyIrregFdata` and the sole public constructor is `irregfdatafromlists`. This design confines the irregular representation to the `pacefpca` module, which is the only analysis algorithm in `fdars` that currently operates on ragged input.

**Differentiator.** Among Python FDA packages (see Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}), scikit-fda provides dense FPCA but no PACE sparse FPCA; FDApy supports irregular sampling in its FPCA but does not provide the breadth of analysis methods available in `fdars`. The `PyIrregFdata` + PACE path in `fdars` thus extends the library's applicability to longitudinal cohort data without requiring pre-interpolation onto a common grid.

# Capability Tour {#sec:capabilities}

`fdars` exposes 409 public callables across 30 submodules, covering the full breadth of functional data analysis methods surveyed in Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}. The 28 callables backed by at least one curated peer-reviewed reference are tracked in the machine-readable scientific-provenance layer (Section [6](#sec:advisor){reference-type="ref" reference="sec:advisor"}).

Each method family in `fdars` follows the same boundary convention described in Section [2](#sec:design){reference-type="ref" reference="sec:design"}: the user constructs or passes an `Fdata` object (or a NumPy array directly for lower-level calls), which the PyO3 binding converts to an `FdMatrix`, forwards to `fdars-core`, and converts back to a NumPy result. High-level `Fdata` methods wrap this boundary transparently. The scikit-learn estimator layer (Section [2.4](#subsec:sklearn){reference-type="ref" reference="subsec:sklearn"}) exposes the same methods as stateless `fit`/`transform` objects for pipeline composition.

The following minimal, executable snippets walk one representative per method family; each is sourced from a script that runs against the live `fdars` API and has its output deterministically captured (see `paper/code/gensnippets.py`). The snippets serve as both documentation and regression tests: the CI drift gate (`make paper-check`) verifies that regenerating them produces no diff against the committed sources.

## Data Representation {#data-representation}

The `Fdata` container bundles an $(n_\text{obs} \times n_\text{points})$ observation matrix with a shared evaluation grid (`argvals`), an optional range specification (`rangeval`), per-observation identifiers, and arbitrary metadata. The snippet below constructs an `Fdata` object from the Berkeley growth study [@ramsay_silverman_2005] and prints its canonical representation:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
from fdars import Fdata
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
fd = Fdata(X, argvals=ARG,
           names={"x": "Age (years)", "y": "Height (cm)"})
print(repr(fd))
print("mean shape:", fd.mean().shape)
```

``` {style="fdarsoutput"}
Fdata (1D)  –  93 obs × 31 points  –  range [1.0, 18.0]
mean shape: (31,)
```

The printed representation reports the container's shape ($n_\text{obs} \times n_\text{points}$), its evaluation range, and the attached axis names, while `fd.mean()` returns the pointwise average curve. Figure [3](#fig:tour-represent){reference-type="ref" reference="fig:tour-represent"} plots the full sample together with this mean: all curves share a single age grid, the shared-grid convention on which every downstream method in this section builds. Metadata and per-observation identifiers travel with the matrix, so a subset or transformed result stays self-describing.

<figure id="fig:tour-represent" data-latex-placement="H">
<embed src="figures/tour_represent.pdf" style="width:82.0%" />
<figcaption>Berkeley growth study: all height curves (grey) sharing one age grid, with the pointwise sample mean (blue) computed by <code>Fdata.mean()</code>. The <code>Fdata</code> container bundles this matrix, grid, identifiers, and metadata into one object.</figcaption>
</figure>

## Basis Representation and Smoothing

fdars provides B-spline and Fourier basis expansions for functional data via `fdars.basis`. `fdatatobasis1d` returns a `(coefficients, nbasis)` tuple, while `smoothbasisgcv` selects the smoothing penalty via generalised cross-validation and returns a dict including the fitted curves, AIC, BIC, and effective degrees of freedom:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
res = fdars.basis.fdata_to_basis_1d(
    X[:5], ARG, n_basis=8, basis_type="bspline")
coefs, nbasis = res
print("coefficients shape:", coefs.shape, "| n_basis:", nbasis)
sm = fdars.basis.smooth_basis_gcv(
    X[:5], ARG, n_basis=8, basis_type="bspline")
print("smoothing keys:", list(sm.keys()))
print("fitted shape:", sm["fitted"].shape)
```

``` {style="fdarsoutput"}
coefficients shape: (5, 8) | n_basis: 8
smoothing keys: ['fitted', 'coefficients', 'edf', 'gcv', 'aic', 'bic', 'nbasis']
fitted shape: (5, 31)
```

`fdatatobasis1d` projects each curve onto a fixed-size basis and returns the coefficient matrix alongside the basis count, whereas `smoothbasisgcv` additionally *chooses* the smoothing penalty by minimising the generalised cross-validation score, trading data fidelity against roughness. Figure [4](#fig:tour-basis){reference-type="ref" reference="fig:tour-basis"} overlays five raw growth curves with their GCV-selected B-spline reconstructions: the fitted curves follow the observations closely while suppressing sampling noise, neither interpolating every point nor flattening genuine curvature. The returned AIC/BIC and effective degrees of freedom quantify this fit--complexity balance for model comparison.

<figure id="fig:tour-basis" data-latex-placement="H">
<embed src="figures/tour_basis.pdf" style="width:82.0%" />
<figcaption>B-spline smoothing of five growth curves: raw observations (points) and their reconstructions (lines) with the smoothing dimension selected by generalised cross-validation.</figcaption>
</figure>

## Depth and Outlier Detection

Functional depth ranks observations by centrality relative to the full sample [@fraiman_muniz_2001]. fdars offers modified band depth, Fraiman--Muniz depth, random Tukey depth, and mode depth via the `Fdata.depth()` method. The `fdars.outliers` submodule adds shape-, magnitude-, and amplitude-based outlier detection via MUOD [@dai_genton_2019]:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
from fdars import Fdata
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
fd = Fdata(X, argvals=ARG)
depths = fd.depth(method="fraiman_muniz")
print("depths shape:", depths.shape)
print("most central obs:", int(np.argmax(depths)))
out = fdars.outliers.muod(X)
print("shape outliers:", out["shape_outliers"])
print("amplitude outliers:", out["amplitude_outliers"])
```

``` {style="fdarsoutput"}
depths shape: (93,)
most central obs: 43
shape outliers: [41, 55, 70]
amplitude outliers: [0, 28]
```

Depth assigns each curve a centrality score relative to the whole sample; the curve of maximum depth is the functional median. MUOD complements this by decomposing atypicality into three indices---shape, magnitude, and amplitude---so that a curve unusual in *form* is flagged separately from one merely shifted in *level*. Figure [5](#fig:tour-depth){reference-type="ref" reference="fig:tour-depth"} shades each growth curve by its Fraiman--Muniz depth (deeper curves drawn more opaque), highlights the functional median, and marks the MUOD-flagged curves in red. Read honestly, depth is a sample-relative ordering and the outlier flags are cutoff-dependent *candidates* for inspection rather than definitive verdicts.

<figure id="fig:tour-depth" data-latex-placement="H">
<embed src="figures/tour_depth.pdf" style="width:82.0%" />
<figcaption>Growth curves shaded by Fraiman–Muniz depth (deeper curves more opaque). The deepest curve (orange) is the functional median; curves flagged by MUOD as shape, magnitude, or amplitude outliers are drawn in red.</figcaption>
</figure>

## Functional PCA and Sparse/Irregular FPCA {#sec:fpca-snippet}

Dense FPCA is available via `Fdata.topc()`, which returns scores, rotation, singular values, and centred data. For sparse or irregularly observed longitudinal data fdars provides PACE (principal analysis by conditional expectation) through `fdars.pacefpca.irregfdatafromlists` (the `PyIrregFdata` container) and `fdars.pacefpca.pacefpca` [@yao_muller_wang_2005]. This distinguishes fdars from peer libraries that support dense FPCA only:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
from fdars import Fdata
from fdars.pace_fpca import irreg_fdata_from_lists, pace_fpca
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
fd = Fdata(X, argvals=ARG)
pc = fd.to_pc(n_comp=3)
sv = np.round(pc["singular_values"], 2).tolist()
print("FPCA scores shape:", pc["scores"].shape)
print("singular values:", sv)
np.random.seed(42)
sizes = np.random.randint(5, 15, size=30)
argvals_list = [
    np.sort(np.random.uniform(1, 18, s)).tolist() for s in sizes
]
values_list = [np.sin(av).tolist() for av in argvals_list]
irreg = irreg_fdata_from_lists(argvals_list, values_list)
pace = pace_fpca(irreg, ncomp=2)
print("PACE scores shape:", pace["scores"].shape)
print("ncomp:", pace["ncomp"])
```

``` {style="fdarsoutput"}
FPCA scores shape: (93, 3)
singular values: [227.54, 93.02, 43.73]
PACE scores shape: (30, 2)
ncomp: 2
```

The dense path returns scores, the eigenfunction `rotation` matrix, and singular values; the PACE path recovers the same structure from curves observed at subject-specific, irregularly spaced times. The most useful way to read an FPCA fit is through its *modes of variation*: the mean curve perturbed by $\pm 2$ standard deviations along each eigenfunction. Figure [6](#fig:tour-fpca){reference-type="ref" reference="fig:tour-fpca"} shows the first two for the growth data---the dominant component is an overall size/level mode, while the second is a timing contrast that crosses near mid-adolescence, corresponding to *when* the pubertal growth spurt occurs. The percentage in each panel title is the live share of variance that component explains.

<figure id="fig:tour-fpca" data-latex-placement="H">
<embed src="figures/tour_fpca.pdf" />
<figcaption>First two FPCA modes of variation: the mean growth curve (grey) perturbed by <span class="math inline">±2</span> standard deviations along each principal eigenfunction. PC1 is an overall-size mode; PC2 is a growth-timing contrast. Variance shares are computed live from the singular values.</figcaption>
</figure>

## Clustering

Functional $k$-means [@bouveyron_jacques_2011] partitions observations by minimising within-cluster $L^2$ distance in the curve space. `fdars.clustering.kmeansfd` accepts a fixed random seed for deterministic results and returns cluster assignments, centroids, total within-cluster sum of squares, and a convergence flag:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
km = fdars.clustering.kmeans_fd(X, ARG, k=3, seed=42)
print("cluster sizes:", np.bincount(km["cluster"]).tolist())
print("converged:", km["converged"])
```

``` {style="fdarsoutput"}
cluster sizes: [56, 22, 15]
converged: True
```

Each iteration assigns every curve to its nearest centroid in $L^2$ and recomputes centroids as within-cluster mean curves, until the assignment stabilises. Figure [7](#fig:tour-clustering){reference-type="ref" reference="fig:tour-clustering"} colours the growth curves by their cluster label and overlays the three centroids: the partition separates primarily by overall growth level and attained final height. As with any $k$-means, the number of clusters $k$ is supplied by the user and the result is a descriptive summary of the sample's dominant variation---not evidence of discrete underlying subpopulations. The fixed `seed` makes the initialisation, and hence the reported partition, reproducible.

<figure id="fig:tour-clustering" data-latex-placement="H">
<embed src="figures/tour_clustering.pdf" style="width:82.0%" />
<figcaption>Functional <span class="math inline"><em>k</em></span>-means (<span class="math inline"><em>k</em> = 3</span>, fixed seed): thin curves are cluster members, bold curves the cluster centroids. Cluster sizes are shown in the legend.</figcaption>
</figure>

## Classification

fdars provides functional linear discriminant analysis, functional $k$-nearest neighbours, depth-based DD-classifiers, and elastic-distance classifiers through `fdars.classification`. The FPCA-$k$NN classifier (`fclassifknn`) projects observations onto the leading principal components and applies $k$-NN in the score space:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
ph = pd.read_csv(data_path("phoneme.csv"), index_col=0)
Xp = ph.values.astype(np.float64)
labels_str = ph.index.tolist()
uniq = list(dict.fromkeys(labels_str))
lut = {l: i for i, l in enumerate(uniq)}
y = np.array([lut[l] for l in labels_str], dtype=np.int64)
res = fdars.classification.fclassif_knn(
    Xp[:100], y[:100], ncomp=3, k=5)
print("accuracy:", res["accuracy"])
```

``` {style="fdarsoutput"}
accuracy: 0.9
```

Projecting onto a handful of principal components before applying $k$-NN keeps the classifier robust to the high dimensionality of raw curves while retaining the between-class signal. Figure [8](#fig:tour-classification){reference-type="ref" reference="fig:tour-classification"} shows why this works on the phoneme data: the five class-mean log-periodogram spectra are visibly distinct in both amplitude and spectral shape, so a low-dimensional FPCA projection preserves enough separation for accurate assignment. The snippet reports held-out accuracy on a subset; the same classifier is evaluated under full cross-validation in Case Study 1 (Section [7](#sec:casestudies){reference-type="ref" reference="sec:casestudies"}).

<figure id="fig:tour-classification" data-latex-placement="H">
<embed src="figures/tour_classification.pdf" style="width:82.0%" />
<figcaption>Class-mean log-periodogram spectra for the five phonemes. The visible separation across the frequency band is the signal the FPCA-<span class="math inline"><em>k</em></span>NN classifier projects onto and exploits.</figcaption>
</figure>

## Regression

`fdars.regression` covers scalar-on-function (SoF) regression via functional linear models with FPCA projection (`fregrelm`), PLS (`fregrepls`), and robust variants, as well as function-on-function (FoF) regression via `fofregression` [@yao_muller_wang_2005]. The snippet demonstrates SoF regression on the Tecator near-infrared spectra dataset, predicting fat content from 100-channel absorbance curves:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
from fdars import Fdata
tec = pd.read_csv(data_path("tecator.csv"), index_col=0)
Xt = tec.iloc[:, :100].values.astype(np.float64)
yfat = tec["fat"].values.astype(np.float64)
WAV = np.arange(1, 101, dtype=float)
# 2nd-derivative spectra (standard NIR preprocessing): smooth,
# then differentiate twice to expose the fat absorption bands.
sm = fdars.basis.smooth_basis_gcv(
    Xt, WAV, n_basis=40, basis_type="bspline")
d2 = Fdata(sm["fitted"], argvals=WAV).deriv().deriv().data
sof = fdars.regression.fregre_lm(d2, yfat, n_comp=15)
print("R^2:", round(sof["r_squared"], 4))
```

``` {style="fdarsoutput"}
R^2: 0.9739
```

Following standard near-infrared practice, the snippet first converts the raw absorbance curves to *second-derivative* spectra---smoothing with a B-spline basis and differentiating twice---which removes baseline and scatter effects and sharpens the fat absorption bands. `fregrelm` then projects these curves onto their leading FPCA components, fits an ordinary linear model in that score space, and returns the fitted values, residuals, the reconstructed coefficient function $\beta(t)$, and the coefficient of determination. Figure [9](#fig:tour-regression){reference-type="ref" reference="fig:tour-regression"} plots fitted against observed fat content: points cluster tightly along the identity line. The $R^2$ shown in the figure is computed live from the fit; the second-derivative preprocessing lifts it well above a fit on the raw spectra (Case Study [7.2](#subsec:cs2-tecator){reference-type="ref" reference="subsec:cs2-tecator"} reports the cross-validated gain). PLS and robust variants (for collinear or contaminated predictors) and function-on-function regression share the same call convention.

<figure id="fig:tour-regression" data-latex-placement="H">
<embed src="figures/tour_regression.pdf" style="width:82.0%" />
<figcaption>Scalar-on-function regression of Tecator fat content on the second-derivative absorbance spectra: fitted vs observed values with the live <span class="math inline"><em>R</em><sup>2</sup></span>. The dashed line marks a perfect fit.</figcaption>
</figure>

## Functional Time Series

The `fdars.fts` submodule implements functional time-series models (FTSM) for data whose observed unit is a curve indexed by time---for example one diurnal air-pollution profile per day. `ftsmforecast` takes the raw data matrix and grid directly and returns multi-step-ahead curve forecasts:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
pm = pd.read_csv(data_path("pm10_graz.csv"), index_col=0)
X = pm.T.values.astype(np.float64)        # 182 days x 48 half-hours
ARG = pm.index.values.astype(np.float64)  # half-hour intervals
fc = fdars.fts.ftsm_forecast(np.sqrt(X), ARG, h=3, ncomp=3)
print("forecast shape:", fc["forecast"].shape, "| h:", fc["h"])
```

``` {style="fdarsoutput"}
forecast shape: (3, 48) | h: 3
```

FTSM decomposes the observed curve sequence into functional principal components, models the temporal dynamics of the resulting score series with a vector autoregression, and reconstructs the next $h$ curves from the forecast scores. Figure [10](#fig:tour-fts){reference-type="ref" reference="fig:tour-fts"} shows a genuine example: the Graz PM10 dataset [@aue_norinho_hormann_2015] records 48 half-hourly PM10 concentrations per day over 182 consecutive days, so the curves form a real temporal sequence and forecasting the next day's diurnal profile is a substantive task. The three forecast curves---back-transformed from the variance-stabilising square-root scale---sit within the envelope of observed days and preserve the characteristic diurnal shape. Because the reconstruction is low-rank, the forecasts capture the leading modes of variation rather than fine minute-to-minute fluctuation. Case Study [7.3](#subsec:cs3-fts){reference-type="ref" reference="subsec:cs3-fts"} validates these next-day forecasts against held-out days and simple baselines.

<figure id="fig:tour-fts" data-latex-placement="H">
<embed src="figures/tour_fts.pdf" style="width:82.0%" />
<figcaption>FTSM forecast of the next three daily PM10 curves (bold) over the 182 observed daily curves (grey) from the Graz dataset. Each curve is one day’s diurnal PM10 profile; the next-day forecasts are validated against held-out days in Case Study <a href="#subsec:cs3-fts" data-reference-type="ref" data-reference="subsec:cs3-fts">7.3</a>.</figcaption>
</figure>

## Statistical Process Monitoring

`fdars.spm` adapts Hotelling $T^2$ and squared prediction error (SPE) control charts to functional data by first estimating in-control variation via `spmphase1` and then monitoring new batches with `spmmonitor`. Phase-1 output components (mean, loadings, weights, eigenvalues, and control limits) are passed as explicit positional arguments to the monitoring function:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
p1 = fdars.spm.spm_phase1(X[:46], ARG, ncomp=3, alpha=0.05)
mon = fdars.spm.spm_monitor(
    p1["mean"], p1["loadings"], p1["weights"],
    p1["eigenvalues"], p1["t2_limit"], p1["spe_limit"],
    X[46:], ARG,
)
print("T2 alarms:", int(mon["t2_alarm"].sum()))
print("SPE alarms:", int(mon["spe_alarm"].sum()))
```

``` {style="fdarsoutput"}
T2 alarms: 5
SPE alarms: 2
```

Phase 1 characterises in-control variation from a reference set of curves and derives the $T^2$ and SPE control limits; Phase 2 then scores each new curve on these two statistics and flags any that exceed a limit. Figure [11](#fig:tour-spm){reference-type="ref" reference="fig:tour-spm"} shows the resulting $T^2$ chart, with out-of-control curves marked in red above the upper control limit. For this illustration the Phase-2 "batch" is simply the second half of the same growth sample, so the alarms reflect ordinary between-subject variability rather than a genuine process fault---the figure demonstrates the charting mechanics, not a real monitoring incident.

<figure id="fig:tour-spm" data-latex-placement="H">
<embed src="figures/tour_spm.pdf" style="width:82.0%" />
<figcaption>Phase-2 Hotelling <span class="math inline"><em>T</em><sup>2</sup></span> control chart: the per-curve <span class="math inline"><em>T</em><sup>2</sup></span> statistic against the Phase-1 upper control limit (UCL). Curves exceeding the UCL are flagged (red).</figcaption>
</figure>

## Conformal and Tolerance Bands

`fdars.tolerance` constructs simultaneous tolerance bands for functional data via bootstrap FPCA [@febrerobande_fdausc_2012]. `fpcatoleranceband` returns upper/lower band curves, a centre curve, and the half-width vector; a fixed `seed` argument makes the bootstrap resampling reproducible:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
tol = fdars.tolerance.fpca_tolerance_band(
    X, ncomp=3, nb=200, coverage=0.95, seed=42)
print("tolerance keys:", list(tol.keys()))
print("band half-width shape:", tol["half_width"].shape)
```

``` {style="fdarsoutput"}
tolerance keys: ['upper', 'lower', 'center', 'half_width']
band half-width shape: (31,)
```

The band is built by repeatedly resampling an FPCA model and calibrating a half-width so that the resulting envelope is expected to contain the target fraction of curves *simultaneously* across the whole grid---a stronger guarantee than a pointwise interval. Figure [12](#fig:tour-tolerance){reference-type="ref" reference="fig:tour-tolerance"} draws the 95% band over the growth sample: most curves fall inside it, and the band widens through adolescence where between-subject spread is largest. The coverage is a bootstrap estimate rather than an exact finite-sample guarantee, and the fixed `seed` pins the reported band.

<figure id="fig:tour-tolerance" data-latex-placement="H">
<embed src="figures/tour_tolerance.pdf" style="width:82.0%" />
<figcaption>Bootstrap-FPCA 95% simultaneous tolerance band (shaded) with its centre curve, drawn over the growth sample. The band widens where between-subject variability grows.</figcaption>
</figure>

## Metrics, Density, and Fréchet Analysis

`fdars.metric` provides $L^p$ pairwise distance matrices (`lpself1d`) and dynamic time warping (`dtwself1d`) for functional observations. Beyond pairwise distances, fdars also provides density-FDA methods (LQD FPCA and Wasserstein barycenters) in `fdars.densityfda`, and Fréchet means, regression, and ANOVA for object-valued data in `fdars.frechet` [@petersen_muller_2019]; see Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"} for the full peer comparison. The snippet illustrates the metric family representative:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
D = fdars.metric.lp_self_1d(X, ARG, p=2.0)
print("L2 distance matrix shape:", D.shape)
Ddtw = fdars.metric.dtw_self_1d(X[:10])
print("DTW[0,1]:", round(float(Ddtw[0, 1]), 2))
```

``` {style="fdarsoutput"}
L2 distance matrix shape: (93, 93)
DTW[0,1]: 1813.09
```

`lpself1d` integrates the pointwise $L^p$ difference between every pair of curves, while `dtwself1d` instead allows elastic time-warping before measuring distance. Figure [13](#fig:tour-metric){reference-type="ref" reference="fig:tour-metric"} renders the $L^2$ distance matrix as a heatmap: the dark diagonal is each curve's zero self-distance, and the off-diagonal block structure exposes groups of mutually similar growth trajectories. Such a distance matrix is the shared input to downstream methods---clustering, $k$-NN classification, and multidimensional scaling---so the metric family underpins much of the rest of the tour.

<figure id="fig:tour-metric" data-latex-placement="H">
<embed src="figures/tour_metric.pdf" style="width:74.0%" />
<figcaption>Pairwise <span class="math inline"><em>L</em><sup>2</sup></span> distance matrix over the growth curves. The dark diagonal is self-distance; off-diagonal blocks mark groups of similar curves.</figcaption>
</figure>

## Elastic Alignment

`fdars.alignment` implements elastic registration under the square-root slope function (SRSF) framework [@srivastava_et_al_2011]. `karchermean` estimates the Karcher mean curve by iteratively aligning observations and re-estimating the mean; the returned dict includes the aligned data matrix, phase-warping functions ($\gamma$), and a convergence flag:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
from fdars import Fdata
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
girls = growth.values.T[39:].astype(np.float64)   # 54 Berkeley girls
# Smooth to B-spline coefficients, re-evaluate on a DENSE age grid
# (the 31-age grid is too coarse for a stable velocity), then differentiate.
sm = fdars.basis.smooth_basis_gcv(
    girls, ARG, n_basis=12, basis_type="bspline")
dense = np.linspace(ARG.min(), ARG.max(), 120)
fit = fdars.basis.basis_to_fdata_1d(
    sm["coefficients"], dense, 12, "bspline")
vel = Fdata(fit, argvals=dense).deriv().data
# Elastic registration of the velocity curves (aligns the spurt peak).
res = fdars.alignment.karcher_mean(vel, dense, max_iter=50)
print("karcher keys:", list(res.keys()))
print("aligned shape:", res["aligned_data"].shape)
print("warping gammas:", res["gammas"].shape)
```

``` {style="fdarsoutput"}
karcher keys: ['mean', 'mean_srsf', 'aligned_data', 'gammas', 'n_iter', 'converged']
aligned shape: (54, 120)
warping gammas: (54, 120)
```

Elastic registration separates two kinds of variation that ordinary averaging conflates: *amplitude* (how large a feature is) and *phase* (when it occurs). The classic illustration is the Berkeley growth study: each girl's growth-*velocity* curve---the derivative of her smoothed height curve---has a pubertal growth spurt, but the spurt occurs at a different age for each child. Figure [14](#fig:tour-alignment){reference-type="ref" reference="fig:tour-alignment"} shows the consequence. Before registration the spurt peaks are spread across ages, so the cross-sectional mean (red, left) smears them into a low, rounded bump; after `karchermean` registration the curves tighten and the Karcher mean (red, right) recovers a sharp spurt at its true amplitude. The returned warping functions $\gamma$ record exactly how each curve's age axis was deformed---a first-class output describing the phase variation that was removed, not a nuisance by-product.

<figure id="fig:tour-alignment" data-latex-placement="H">
<embed src="figures/tour_alignment.pdf" />
<figcaption>Elastic SRSF registration of Berkeley girls’ growth-velocity curves (ages 5–18), before (left) and after (right) <code>karchermean</code> alignment. Registering the pubertal-spurt peak tightens the sample; the Karcher mean (red, right) recovers a sharp spurt that the naive cross-sectional mean (red, left) smears out.</figcaption>
</figure>

Because the warping functions are a first-class output, they can be analysed in their own right. Registering all Berkeley children---boys and girls---to a common growth-velocity template yields one $\gamma$ per child, and colouring them by sex exposes a genuine biological contrast (Figure [15](#fig:tour-warping){reference-type="ref" reference="fig:tour-warping"}). The girls' warping functions lie systematically below the boys': to reach the shared template landmarks---above all the pubertal spurt---a girl's age axis is mapped to *earlier* ages than a boy's. This is the well-documented earlier maturation of girls (peak height velocity roughly two years sooner), isolated here as pure *phase* variation---a timing difference the warping functions make explicit and quantifiable, separate from any difference in spurt amplitude. The identity diagonal marks a child who needs no warping (developmental clock exactly on the template); deviations below it mark earlier development, above it later.

<figure id="fig:tour-warping" data-latex-placement="H">
<embed src="figures/tour_warping.pdf" style="width:82.0%" />
<figcaption>SRSF warping functions <span class="math inline"><em>γ</em></span> from registering all Berkeley children’s growth-velocity curves to a common Karcher template, coloured by sex (thin curves: individuals; bold: per-sex mean). Girls’ warping functions lie below boys’, mapping the shared spurt landmark to earlier ages—the <span class="math inline"> ∼ 2</span>-year-earlier maturation of girls as phase variation. The dashed diagonal is the no-warp identity.</figcaption>
</figure>

## Grounded AI Advisor (LLM-Free Diagnostics)

`fdars.advisor.builddiagnostics` computes method-specific structured diagnostics from any fdars result dict in a fully offline, deterministic manner---no LLM provider is required. The LLM-assisted `advise()` function takes these diagnostics and a user-specified task description and queries a configured language model to generate grounded parameter recommendations; it is described further in Section [6](#sec:advisor){reference-type="ref" reference="sec:advisor"}. The snippet demonstrates the offline diagnostic step for FPCA:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
import fdars
from fdars import Fdata
growth = pd.read_csv(data_path("growth.csv"), index_col=0)
ARG = growth.index.values.astype(float)
X = growth.values.T.astype(np.float64)
fd = Fdata(X, argvals=ARG)
pc = fd.to_pc(n_comp=3)
diag = fdars.advisor.build_diagnostics(pc, "fpca", argvals=ARG)
cum = np.round(diag["cumulative_variance_explained"], 3).tolist()
print("cumulative variance explained:", cum)
```

``` {style="fdarsoutput"}
cumulative variance explained: [0.831, 0.969, 1.0]
```

The diagnostic reduces a full result dict to the small set of scalars a practitioner would actually inspect---here, the per-component and cumulative variance explained. Figure [16](#fig:tour-advisor){reference-type="ref" reference="fig:tour-advisor"} plots exactly these quantities as a scree chart: the first component dominates and the cumulative curve saturates quickly, which is the concrete signal the advisor uses to recommend how many components to retain. Because every number is computed from the data rather than generated by a language model, the resulting guidance is *grounded*: the optional `advise()` step passes these diagnostics to an LLM only to phrase and contextualise a recommendation the numbers already support (Section [6](#sec:advisor){reference-type="ref" reference="sec:advisor"}).

<figure id="fig:tour-advisor" data-latex-placement="H">
<embed src="figures/tour_advisor.pdf" style="width:82.0%" />
<figcaption>The advisor’s offline FPCA diagnostic: per-component (bars) and cumulative (line) variance explained. These are the exact, computed quantities its grounded, LLM-free guidance reasons over.</figcaption>
</figure>

## scikit-learn Compatibility {#sec:sklearn-snippet}

fdars exposes 28 scikit-learn-compatible estimators (all passing `checkestimator`) through `fdars.sklearn.skeletons`, spanning smoothers, transformers, regressors, classifiers, clusterers, and outlier detectors. Estimators compose with the standard `Pipeline` API, enabling functional preprocessing steps inside any scikit-learn workflow:

``` {.python language="Python" style="fdarsinput"}
import numpy as np, pandas as pd
from fdars.sklearn._skeletons import FPCATransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_score
tec = pd.read_csv(data_path("tecator.csv"), index_col=0)
Xt = tec.iloc[:, :100].values.astype(np.float64)
yfat = tec["fat"].values.astype(np.float64)
pipe = Pipeline([
    ("fpca", FPCATransformer(n_components=5)),
    ("ridge", RidgeCV()),
])
scores = cross_val_score(pipe, Xt, yfat, cv=5, scoring="r2")
print("mean R^2 (5-fold):", round(float(scores.mean()), 3))
```

``` {style="fdarsoutput"}
mean R^2 (5-fold): 0.784
```

# Comparison with Related Software {#sec:comparison}

**fdars** is uniquely broad among Python functional data analysis libraries: it covers the full analytical pipeline from representation and alignment through depth, clustering, classification, regression, functional time series, statistical process monitoring, conformal prediction, and density/Fréchet methods, in a single Rust-backed package with a scikit-learn--compatible API. Where capability evidence for peer packages was ambiguous, coverage is resolved conservatively (partial rather than $\checkmark$, --- rather than partial); all non-**fdars** cells are sourced in `paper/comparisonevidence.md`.

Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"} summarises the capability coverage of **fdars** against the most widely used Python and R functional data analysis packages and the historical MATLAB tools that define the field.

::: adjustbox
max width=

  **Capability**                               **fdars**     **scikit-fda**    **FDApy**     **R (fda / fda.usc / refund)**   **funData / tidyfun**   **Matlab (fdaM / PACE)**
  ------------------------------------------ -------------- ---------------- -------------- -------------------------------- ----------------------- --------------------------
  Representation / basis smoothing            $\checkmark$    $\checkmark$    $\checkmark$            $\checkmark$                $\checkmark$              $\checkmark$
  Registration / alignment                    $\checkmark$    $\checkmark$        ---                 $\checkmark$                  *partial*               $\checkmark$
  Depth & outlier detection                   $\checkmark$    $\checkmark$        ---                 $\checkmark$                     ---                      ---
  FPCA / covariance / PACE sparse FPCA        $\checkmark$     *partial*      $\checkmark$            $\checkmark$                  *partial*               $\checkmark$
  Clustering                                  $\checkmark$    $\checkmark$     *partial*               *partial*                       ---                   *partial*
  Classification                              $\checkmark$    $\checkmark$        ---                 $\checkmark$                     ---                      ---
  Functional regression (SoF / FoF)           $\checkmark$     *partial*          ---                 $\checkmark$                     ---                   *partial*
  Functional time series                      $\checkmark$        ---             ---                     ---                          ---                      ---
  Statistical process monitoring              $\checkmark$        ---             ---                     ---                          ---                      ---
  Inference / hypothesis testing              $\checkmark$     *partial*          ---                  *partial*                       ---                      ---
  Conformal prediction & tolerance bands      $\checkmark$        ---             ---                     ---                          ---                      ---
  Density / Fréchet / metric-space            $\checkmark$        ---             ---                     ---                          ---                      ---
  Simulation & datasets                       $\checkmark$    $\checkmark$    $\checkmark$            $\checkmark$                  *partial*                *partial*
  Grounded advisor + scientific provenance    $\checkmark$        ---             ---                     ---                          ---                      ---
  **sklearn-compatible API**                  $\checkmark$    $\checkmark$        ---                     ---                          ---                      ---
  **Language**                                Rust/Python        Python          Python                    R                            R                      MATLAB

  : Capability comparison of **fdars** 0.13.0 with related functional data analysis software. $\checkmark$ = first-class documented support; *partial* = limited, indirect, or requires glue code; --- = no support found. Ambiguity resolves down (see text). Peer versions accessed 2026-09-08: scikit-fda 0.10.1; FDApy 1.0.3; fda 6.3.0; fda.usc 2.2.0; refund 0.1-40; funData 1.3-9; tidyfun 0.2.0; fdaM \~2014; PACE v2.17. {#tab:comparison}
:::

# Grounded AI Advisor and Scientific Provenance {#sec:advisor}

A recurring challenge in applied functional data analysis is *parameter selection*: bandwidth for kernel smoothing, the number of basis functions, the number of FPCA components, or the number of clusters. While numerical criteria (GCV, AIC, silhouette score) narrow the range, interpreting their output in the context of a specific analytical goal --- and translating that interpretation into a revised parameter setting --- requires domain and methodological knowledge. `fdars` addresses this through a *grounded parameter advisor* paired with a *scientific-provenance layer*, both absent from peer FDA packages (see Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"} and the evidence in `paper/comparisonevidence.md`).

<figure id="fig:advisor" data-latex-placement="ht">

<figcaption>Advisor and scientific-provenance data flow. <code>builddiagnostics</code> is entirely deterministic (no LLM); <code>advise</code> queries a user-configured language-model provider using only the structured diagnostics as context; <code>autotune</code> iterates both in a bounded closed-loop. The provenance map (<code>referencesmap.json</code>) feeds <code>fdarsmethodreferences</code>, an MCP tool that resolves callable names to peer-reviewed papers at query time.</figcaption>
</figure>

## The Grounded Advisor

The advisor exposes three public entry points in `fdars.advisor`:

**`builddiagnostics` --- the LLM-free grounding step.**

``` {style="fdarsinput"}
build_diagnostics(
    result, method, *, argvals=None, ...
)
```

It accepts the result dictionary returned by an `fdars` analysis function (e.g. the dict returned by `Fdata.topc`) and a method identifier string (e.g. `"fpca"`, `"smoothing"`, `"clustering"`) and returns a structured diagnostics dictionary derived entirely from deterministic computation on the result. The content of the diagnostics dict is method-specific: for `fpca` it includes cumulative explained-variance ratios, component count, reconstruction error, and a phase-leakage indicator; for `smoothing` it includes GCV score, effective degrees of freedom, AIC/BIC, and residual norm; for `clustering` it includes within-cluster sum of squares, silhouette score (where applicable), and a convergence flag. No language model is involved; the diagnostics are fully reproducible given the same result input, and can be inspected, logged, or tested independently of the LLM step. Supported method identifiers include `alignment`, `basis`, `classification`, `clustering`, `depth`, `fpca`, `frechet`, `fts`, `inference`, `outliers`, `regression`, `regressioncv`, `represent`, `scoring`, `smoothing`, and `spm`. The capability tour (Section [4](#sec:capabilities){reference-type="ref" reference="sec:capabilities"}) demonstrates `builddiagnostics` on an FPCA result.

**`advise` --- the provider-agnostic LLM entry point.**

``` {style="fdarsinput"}
advise(
    diagnostics, *, task, domain_context,
    provider=None, model=...,
) -> Advice
```

It accepts the diagnostics dict produced by `builddiagnostics` --- never raw data or a result dict directly --- and calls a user-configured language-model provider (Anthropic, OpenAI, or Ollama) to generate parameter recommendations framed in terms of the supplied task description and domain context. Provider credentials are entirely the user's responsibility; the library imposes no default provider and does not embed API keys. Because the LLM receives only the structured, deterministic diagnostics as its context, its recommendations trace back to computed facts rather than free-form interpretation of raw arrays. This *grounding invariant* is what distinguishes the advisor from a plain LLM chat interface applied to a data summary: the diagnostics constitute an explicit, auditable evidence layer that the language model reasons over, and the same diagnostics can be separately inspected by the user to verify that the LLM's advice is consistent with the numbers.

**`autotune` --- closed-loop parameter search.**

``` {style="fdarsinput"}
auto_tune(
    dataset_id, method, *, target_metric=None,
    max_steps=10, guard=True, ...
)
```

A closed-loop parameter search that iterates `builddiagnostics` $\to$ `advise` $\to$ re-fit in a bounded loop (at most `maxsteps` iterations). The `guard=True` default activates the *grounding guard*, which rejects any proposed parameter change that cannot be mapped back to a diagnostic fact using a pattern-matching check on the advisor response text. The guard prevents unconstrained free-form generation from driving the search and ensures that the loop terminates on a recognisable improvement signal rather than on arbitrary LLM output.

The design separates the deterministic grounding step (`builddiagnostics`) from the probabilistic recommendation step (`advise`), ensuring that the pipeline can be tested and audited at the boundary between the two. In particular, `builddiagnostics` can be unit-tested against known result dicts without any LLM dependency, and the diagnostics dict format is stable across provider changes.

## Scientific-Provenance Layer

`fdars` ships a machine-readable provenance map, `python/fdars/referencesmap.json`, that links each public callable to the foundational papers from which its algorithm derives. The map contains 47 curated-eligible papers (with DOIs or arXiv identifiers) and covers 28 callables with at least one author-verified paper entry. Each paper record carries the title, authors, year, identifier, method family, the list of `fdars` callables that implement it, cross-language implementation pointers (R, Python, and MATLAB equivalents with per-entry confidence assessments), and a `curated` boolean indicating whether the entry has been manually verified against the primary source. Entries marked `curated: false` are present as cross-reference candidates but are explicitly flagged so that downstream tooling can distinguish author-verified citations from unverified suggestions.

The provenance map is served at runtime through the `fdarsmethodreferences` MCP (Model Context Protocol) tool [@anthropic_mcp_2024], which the `fdars-advisor` skill registers. Given a callable name, the tool returns the associated paper entries, DOIs, and cross-language pointers --- making the provenance queryable by any MCP-compatible development environment (e.g. Claude Desktop, VS Code Copilot) without requiring a network call at query time, since the full map is bundled with the package. The same map drives the offline-generated References documentation page in the MkDocs site (`docs/references/`), ensuring that the paper-level provenance visible to readers and the provenance queryable by the advisor are always derived from the same source of truth and never diverge silently.

## Differentiator

The evidence dossiers in `paper/comparisonevidence.md` confirm that none of the peer FDA packages surveyed --- scikit-fda, FDApy, R `fda`, `fda.usc`, `refund`, `funData`/`tidyfun`, or Matlab `fdaM`/PACE --- provides either a grounded parameter advisor or a machine-readable scientific-provenance layer (see the "Grounded advisor + scientific provenance" row in Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}, which shows only for `fdars`). These two contributions address distinct barriers to adoption: the advisor lowers the methodological cost of parameter selection for applied users, while the provenance layer gives researchers a traceable link from any `fdars` result back to the peer-reviewed literature from which the method derives.

# Case Studies {#sec:casestudies}

The four studies below illustrate `fdars` on real datasets spanning smoothing and functional principal component analysis, elastic registration with scalar-on-function regression, functional time-series forecasting, and composable scikit-learn pipelines with hyperparameter search. Each study is reproduced by a committed `paper/code/casestudyN.py` script that generates the accompanying figures deterministically; re-running any script leaves `git diff paper/figures/` empty.

## Smoothing, FPCA, and Classification: Phoneme Data {#subsec:cs1-phoneme}

The phoneme dataset consists of 400 log-periodogram curves recorded across 256 frequency points, representing five phoneme classes (*aa*, *ao*, *dcl*, *iy*, *sh*) with 80 observations each [@ferraty_vieu_2006]. Each curve is a digitised acoustic spectrum, and the classification task is to recover the phoneme class from its spectral shape. This study demonstrates three core `fdars` capabilities in sequence: penalised smoothing, functional principal component analysis (FPCA), and cross-validated classification.

#### Smoothing.

Raw log-periodogram curves carry measurement noise. We apply GCV-penalised B-spline smoothing (`fdars.basis.smoothbasisgcv`) with 15 basis functions to a representative subset of 20 curves, selecting the penalty automatically via generalised cross-validation [@craven_wahba_1979; @eilers_marx_1996]. Figure [18](#fig:cs1-smooth){reference-type="ref" reference="fig:cs1-smooth"} shows the raw spectra alongside the fitted smooth curves for each class; the smoothed curves retain the phoneme-specific spectral peaks while suppressing high-frequency noise.

#### FPCA.

FPCA is performed on all 400 curves via `Fdata.topc(ncomp=4)` [@ramsay_silverman_2005]. The first four principal components explain $[69.3, 23.0, 5.4, 2.3]\%$ of total variance, with the first three components jointly accounting for 97.7% of variation. The scores scatter in Figure [19](#fig:cs1-fpca){reference-type="ref" reference="fig:cs1-fpca"} shows clear class separation in the PC1--PC2 plane, confirming that the dominant modes of variation align with phoneme identity.

#### Classification.

We evaluate a scikit-learn `Pipeline` that chains an `FPCATransformer` (4 components) with an `FPCLDAClassifier` (linear discriminant analysis on FPCA scores) by 5-fold cross-validation [@preda_saporta_2005]. The pipeline achieves a mean CV accuracy of 86.3% on held-out data (fold scores: $[0.850, 0.850, 0.863, 0.875, 0.875]$), demonstrating that four functional principal components capture the class-discriminating structure of the phoneme spectra. The analysis is reproduced exactly by `paper/code/casestudy1.py`, which generates both figures deterministically (re-running the script leaves `git diff paper/figures/` empty).

<figure id="fig:cs1-smooth" data-latex-placement="H">
<embed src="figures/cs1_phoneme_smooth.pdf" style="width:85.0%" />
<figcaption>Phoneme log-periodogram spectra (400 curves, 5 classes). Light traces: raw curves (3 per class); bold traces: GCV B-spline smoothed curves (15 basis functions, penalty selected by GCV). Colours identify phoneme classes (<em>aa</em>, <em>ao</em>, <em>dcl</em>, <em>iy</em>, <em>sh</em>).</figcaption>
</figure>

<figure id="fig:cs1-fpca" data-latex-placement="H">
<embed src="figures/cs1_phoneme_fpca.pdf" style="width:75.0%" />
<figcaption>FPCA scores scatter for the phoneme data (PC1 vs PC2, colour-coded by class). The first two principal components explain 69.3% and 23.0% of variance respectively; the five phoneme classes are well-separated in this projection, consistent with the 86.3% 5-fold CV classification accuracy achieved by <code>FPCATransformer</code> + <code>FPCLDAClassifier</code>.</figcaption>
</figure>

## Registration and Scalar-on-Function Regression: Tecator Data {#subsec:cs2-tecator}

The tecator dataset consists of 240 near-infrared absorbance spectra of meat samples measured at 100 spectral channels, with fat content (ranging from 0.9% to 58.5%) recorded as a scalar response for each sample [@ramsay_silverman_2005]. The spectra exhibit phase variability --- curves that carry the same shape but are shifted or compressed along the spectral axis --- which motivates a registration step before regression. This study demonstrates two additional `fdars` capabilities: elastic curve registration via the square-root velocity framework [@srivastava_klassen_2016] and scalar-on-function FPC regression [@preda_saporta_2005].

#### Registration.

We estimate an elastic Karcher mean from a representative subset of 30 curves using `fdars.alignment.karchermean` (Fisher--Rao gradient descent, capped at 20 iterations) and then align all 240 spectra to that mean with `fdars.alignment.aligntotarget`. The iteration cap is chosen for computational efficiency; convergence is not required for the registration to be illustrative [@srivastava_klassen_2016]. Figure [20](#fig:cs2-align){reference-type="ref" reference="fig:cs2-align"} shows the 30 raw spectra (grey) alongside their registered counterparts and the Karcher mean (highlighted), revealing how elastic alignment reduces phase dispersion while preserving the characteristic spectral peaks.

#### Scalar-on-function regression.

Following standard near-infrared practice, we first convert the absorbance curves to *second-derivative* spectra---B-spline smoothing followed by double differentiation---which removes baseline and scatter effects and sharpens the fat absorption bands. Fat content is then modelled as a linear functional of the second-derivative spectrum via FPC regression (`fdars.regression.fregrelm`, fifteen functional principal components) [@preda_saporta_2005]. Fitting on all 240 samples yields a training $R^2 = 0.974$, appreciably higher than the fit on the raw absorbance spectra. Figure [21](#fig:cs2-fit){reference-type="ref" reference="fig:cs2-fit"} plots actual against fitted fat content; the scatter follows the diagonal closely throughout the range, with the reference line $y = x$ shown for comparison.

#### Cross-validation.

To assess generalisation, we evaluate `FPCRegressor` (15 components) on the same second-derivative spectra via 5-fold cross-validation using `sklearn.modelselection.crossvalscore`. The fold-level $R^2$ scores are $[0.934, 0.831, 0.940, 0.971, 0.962]$, giving a mean CV $R^2 = 0.928$ --- a substantial out-of-sample gain over the raw-spectra baseline, confirming that the second-derivative preprocessing improves generalisation and not merely the training fit. The complete analysis is reproduced deterministically by `paper/code/casestudy2.py`, which writes both figures via the `paperutils.savefigure` harness (re-running the script leaves `git diff paper/figures/` empty).

<figure id="fig:cs2-align" data-latex-placement="H">
<embed src="figures/cs2_tecator_align.pdf" style="width:85.0%" />
<figcaption>Tecator near-infrared spectra before and after elastic registration (30 of 240 curves shown). Grey traces: raw spectra exhibiting phase variability. Coloured traces: spectra aligned to the Karcher mean via the square-root velocity framework <span class="citation" data-cites="srivastava_klassen_2016"></span>. Bold trace: estimated Karcher mean used as the registration target (alignment iterations capped at 20).</figcaption>
</figure>

<figure id="fig:cs2-fit" data-latex-placement="H">
<embed src="figures/cs2_tecator_fit.pdf" style="width:75.0%" />
<figcaption>Scalar-on-function FPC regression on the tecator data: actual versus fitted fat content for all 240 meat samples, using second-derivative spectra (<code>fdars.regression.fregrelm</code>, 15 components). The dashed line marks perfect prediction (<span class="math inline"><em>y</em> = <em>x</em></span>). Training <span class="math inline"><em>R</em><sup>2</sup> = 0.974</span>; 5-fold CV <span class="math inline"><em>R</em><sup>2</sup> = 0.928</span> (mean; fold scores <span class="math inline">[0.934, 0.831, 0.940, 0.971, 0.962]</span>).</figcaption>
</figure>

## Functional Time Series Forecasting: Daily PM10 Air Pollution {#subsec:cs3-fts}

The Graz PM10 dataset [@aue_norinho_hormann_2015] records the concentration of airborne particulate matter (aerodynamic diameter $<10\,\mu$m, in $\mu$g/m$^3$) at half-hourly resolution at the Graz-Mitte station, from 2010-10-01 to 2011-03-31. Reshaping the record into one curve per day gives a genuine functional time series: 182 consecutive daily curves, each a 48-point diurnal PM10 profile. Unlike a cross-sectional collection, the curves are ordered in real calendar time, so forecasting *the next day's* pollution profile is a substantive task [@hyndman_ullah_2007; @hormann_kokoszka_2010]. We model on the variance-stabilising square-root scale (as recommended for this dataset) and back-transform forecasts to $\mu$g/m$^3$.

#### Decomposition.

The FTS mean curve and principal components are extracted via `fdars.fts.ftsm(X, ARG, ncomp=3)`, which fits the functional principal component decomposition and a vector autoregressive (VAR) model on the FPC score series. Figure [22](#fig:cs3-curves){reference-type="ref" reference="fig:cs3-curves"} shows the 175 training-day curves together with the FTS mean, exposing the characteristic diurnal structure and the wide day-to-day amplitude variation the model must capture.

#### Out-of-sample forecast and validation.

We hold out the final $H = 7$ days (2011-03-25 to 2011-03-31), fit the model on the preceding 175 days, and forecast $H$ days ahead with `fdars.fts.ftsmforecast(X, ARG, h=7, ncomp=3)`. Each forecast curve is compared to the corresponding held-out actual curve by root-mean-square error (RMSE, $\mu$g/m$^3$), against two baselines: *climatology* (the training mean curve) and *persistence* (the last observed day). Averaged over the seven held-out days the FTS forecast attains a mean RMSE of $13.68$, beating both climatology ($15.52$) and persistence ($17.17$); at the one-day-ahead horizon the margin is largest ($6.08$ versus $10.60$ and $11.27$). Figure [23](#fig:cs3-forecast){reference-type="ref" reference="fig:cs3-forecast"} shows the one-day-ahead forecast against the actual and climatology curves (left) and the RMSE at each horizon (right). The full analysis is reproduced exactly by `paper/code/casestudy3.py`, which writes both figures deterministically.

#### Honest caveat.

Forecast skill decays with horizon: the FTS advantage over climatology is clear at short horizons but narrows further out, where a low-rank curve model cannot anticipate day-specific pollution events. The study is an honest, reproducible demonstration that `fdars`' FTS interface produces skilful next-day functional forecasts on a real temporal dataset --- not a claim of state-of-the-art air-quality forecasting.

<figure id="fig:cs3-curves" data-latex-placement="H">
<embed src="figures/cs3_pm10_curves.pdf" style="width:85.0%" />
<figcaption>Graz PM10: the 175 training-day diurnal curves (grey) and the FTS mean curve (solid, <code>ftsm</code>, 3 components). Each day contributes one 48-point functional observation; the <span class="math inline"><em>x</em></span>-axis is the hour of day.</figcaption>
</figure>

<figure id="fig:cs3-forecast" data-latex-placement="H">
<embed src="figures/cs3_pm10_forecast.pdf" style="width:95.0%" />
<figcaption>Out-of-sample validation of the FTS next-day PM10 forecast (7 held-out days). <em>Left:</em> the one-day-ahead forecast (2011-03-25) against the actual curve and the climatology baseline. <em>Right:</em> RMSE (<span class="math inline"><em>μ</em></span>g/m<span class="math inline"><sup>3</sup></span>) at each forecast horizon for the FTS model, climatology, and persistence; the FTS forecast leads at short horizons.</figcaption>
</figure>

## Composable scikit-learn Pipelines: Wine Data {#subsec:cs4-wine}

The wine dataset comprises 178 samples described by 13 chemical measurements, partitioned into three cultivar classes (59, 71, and 48 samples respectively). This study demonstrates a different facet of `fdars`: rather than a single functional method, it showcases the *composability* of the `fdars` scikit-learn estimator layer, which exposes 28 estimators that plug natively into `sklearn.pipeline.Pipeline` and `sklearn.modelselection. GridSearchCV` [@ramoscarreno_scikitfda_2024]. Here each 13-measurement sample is treated as a short functional profile subjected to *functional preprocessing*; this is not a traditional functional-data interpretation of the wine measurements, but it exercises the estimator interface exactly as a genuine functional problem would.

#### Pipeline.

We compose an `fdars` `FPCATransformer` --- which projects each sample onto its leading functional principal components [@ramsay_silverman_2005] --- with a vanilla `sklearn.discriminantanalysis.LinearDiscriminantAnalysis` classifier [@preda_saporta_2005]. Because `FPCATransformer` obeys the scikit-learn transformer contract, this heterogeneous pipeline (an `fdars` transformer feeding an off-the-shelf scikit-learn estimator) requires no glue code.

#### Hyperparameter tuning.

The number of retained principal components is tuned by `GridSearchCV` over the grid $\{2, 3, 5, 8\}$, using 5-fold cross-validation with a single worker to guarantee deterministic split ordering. Mean cross-validated accuracy rises monotonically with the number of retained components: $0.697$, $0.759$, $0.916$, and $0.961$ for $2$, $3$, $5$, and $8$ components respectively (Figure [24](#fig:cs4-gridsearch){reference-type="ref" reference="fig:cs4-gridsearch"}). The best configuration retains eight components and attains a mean 5-fold CV accuracy of $0.961$. Figure [25](#fig:cs4-scores){reference-type="ref" reference="fig:cs4-scores"} shows the FPCA scores of the best estimator projected onto their first two components, coloured by cultivar; the three classes form well-separated groups, consistent with the high cross-validated accuracy.

The analysis is reproduced exactly by `paper/code/casestudy4.py`, which computes all reported accuracies live and generates both figures deterministically (re-running the script leaves `git diff paper/figures/` empty).

<figure id="fig:cs4-gridsearch" data-latex-placement="H">
<embed src="figures/cs4_wine_gridsearch.pdf" style="width:75.0%" />
<figcaption><code>GridSearchCV</code> tuning of the FPCA dimensionality for the wine pipeline (<code>FPCATransformer</code> + <code>LinearDiscriminantAnalysis</code>). Bars show mean 5-fold cross-validated accuracy for each number of retained functional principal components; accuracy increases with dimensionality, and the best configuration retains eight components (dashed line marks the best accuracy).</figcaption>
</figure>

<figure id="fig:cs4-scores" data-latex-placement="H">
<embed src="figures/cs4_wine_scores.pdf" style="width:75.0%" />
<figcaption>FPCA scores for the wine data at the best <code>GridSearchCV</code> configuration (first two of eight retained components), coloured by cultivar class. The three cultivars form well-separated groups, consistent with the cross-validated classification accuracy achieved by the composed <code>FPCATransformer</code> + <code>LinearDiscriminantAnalysis</code> pipeline.</figcaption>
</figure>

# Validation and Correctness {#sec:validation}

## Development methodology disclosure {#development-methodology-disclosure .unnumbered}

`fdars` and the underlying `fdars-core` Rust crate were developed with substantial assistance from Anthropic's Claude Code, an AI coding assistant. All algorithms, architecture decisions, and final code were specified, reviewed, and verified by the author; Claude Code served as an implementation accelerator throughout the development lifecycle. Because much of the implementation was produced with AI assistance, independent validation is treated as a first-class design constraint rather than an afterthought: every layer of the stack is guarded by automated checks that run on each commit, and this manuscript is itself a reproducibility artefact whose code snippets and figures are regenerated and verified in CI.

## Rust layer

The numerical algorithms reside in the `fdars-core` crate. The PyO3 binding layer (`pyfda`) is held to consistent code-quality standards enforced in CI: `cargo fmt --check` enforces formatting, `cargo clippy -- -D warnings` promotes warnings to errors, and `cargo test` runs the binding-layer unit tests against both the current stable Rust toolchain and the declared MSRV (Rust 1.83).

## Python test suite

The `tests/` directory is exercised by `pytest` on every CI run across Python 3.9 through 3.14. Tests cover the `Fdata` container, numerical operations (smoothing, depth, alignment, regression, monitoring, covariance sampling), the AI advisor and MCP server, and the ergonomic dataset loaders.

## Cross-language parity

`tests/testrparity.py` validates `fdars` numerical outputs against known-correct mathematical ground truth, mirroring the smoke-test properties used when the R-parity bindings were added. Tests span seven batches covering depth measures, [L]{.smallcaps}$^2$ inner products, Simpson integration, landmark registration, nonparametric regression, functional monitoring (CUSUM and EWMA), elastic changepoint detection, and prediction metrics. Each test checks a mathematically verifiable property---integrals of known functions, determinism under fixed seeds, correct output shapes, and expected statistical behaviour (e.g. that a CUSUM chart detects a known mean shift)--- complementing the scientific-provenance map (47 peer-reviewed method papers documented in `referencesmap.json`).

## scikit-learn API compliance

28 estimators in `fdars.sklearn` pass the scikit-learn `checkestimator` conformance suite [@pedregosa_sklearn_2011], run from `tests/sklearn/` in CI across all supported Python versions. Passing `checkestimator` guarantees that the estimators honour scikit-learn's fit--predict contract, are picklable, and compose correctly inside `Pipeline` and `GridSearchCV`.

## Reproducibility as validation

This manuscript is itself a validation artefact. Every code snippet in Section [4](#sec:capabilities){reference-type="ref" reference="sec:capabilities"} and every figure in Section [7](#sec:casestudies){reference-type="ref" reference="sec:casestudies"} is produced by a committed `paper/code/` script. CI drift gates (`make paper-check`) verify that regenerating snippets, coverage macros, and the reference bibliography leaves no diff against the committed sources; `make paper-verify` confirms byte-stable figure reproduction in the same Python environment. No printed example can silently diverge from the live API.

# Availability and Installation {#sec:availability}

`fdars` is available from the Python Package Index (PyPI) and can be installed with:

    pip install fdars

Prebuilt binary wheels are provided for Linux (x86 and aarch64), macOS (x86 and aarch64), and Windows (x86). The package targets the CPython stable ABI (`abi3-py39`) and supports Python 3.9 through 3.14.

An optional `plot` extra installs `matplotlib` for the built-in visualisation utilities:

    pip install fdars[plot]

An optional `sklearn` extra installs `scikit-learn` and enables the `fdars.sklearn` estimator layer, which exposes 28 estimators compatible with the scikit-learn API:

    pip install fdars[sklearn]

The source code is released under the MIT licence and is hosted at <https://github.com/sipemu/pyfda>. Documentation, including worked examples and API reference, is available at <https://sipemu.github.io/pyfda/>.

# Conclusion

`fdars` is a broad, method-accurate, Rust-backed Python library for functional data analysis. It exposes 409 public callables across 30 method families---spanning representation, basis smoothing, elastic alignment, functional depth and outlier detection, FPCA (dense and sparse PACE), clustering, classification, scalar- and function-on-function regression, functional time series, statistical process monitoring, conformal prediction, density and Fréchet methods, and metric computations---together with a full scikit-learn-compatible estimator layer, as documented in Table [1](#tab:comparison){reference-type="ref" reference="tab:comparison"}. Two contributions distinguish `fdars` from all peer FDA packages surveyed in that table: a grounded parameter-advisor module that structures method diagnostics into an LLM-interpretable representation for context-aware guidance, and a machine-readable scientific-provenance layer linking 47 documented papers to the callables they underpin via a queryable MCP tool. The library is under active development; the `fdars` codebase, issue tracker, and documentation are maintained at <https://github.com/sipemu/pyfda>.
