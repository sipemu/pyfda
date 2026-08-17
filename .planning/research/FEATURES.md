# Feature Research

**Domain:** PyO3 binding layer — fdars-core 0.20.0 new API surface (functional inference + depth/boxplot + basis/smoothing)
**Researched:** 2026-08-17
**Confidence:** HIGH (signatures verified against docs.rs/fdars-core/0.20.0; struct fields verified against dispatch.rs source; conceptual descriptions drawn from upstream docstrings)

---

## Verified Signatures and Struct Definitions

All signatures below were fetched from `docs.rs/fdars-core/0.20.0`. Fields marked **[confirm at plan time]** could not be resolved via the docs.rs HTML path and must be cross-checked against the crate source before binding.

---

## Group A — Functional Inference (`fdars.inference` — NEW submodule)

### Pattern context

This is fdars-core's first standalone inference surface (added in 0.19.0). It mirrors the R `fda` / `fda.usc` ecosystem. All public functions return `Result<_, FdarError>`; input validation fires at entry. `DEFAULT_N_PERM = 999`.

The **permutation test trio** (`t_perm_test`, `f_perm_test`, `scb_two_sample_test`) take two FdMatrix arguments — one per group — plus argvals, permutation count, and a `u64` seed for reproducibility. They return `TestResult`.

The **asymptotic tests** (`two_sample_mean_test`, `oneway_anova_vstat`) have no seed parameter; they use a closed-form or moment-matched chi-square approximation.

The **SCB functions** (`mean_scb`, `scb_two_sample_test`) take an additional `MultiplierDistribution` enum argument. `MultiplierDistribution` variants were not individually resolved via docs.rs HTML (404); **confirm variants at plan time**.

The **FLM inference functions** (`flm_f_test`, `flm_gof_test`) take only `&FregreLmResult` — no data re-passed.

---

### A1. `t_perm_test` — Integrated L2 permutation t-test

**Verified signature:**
```rust
pub fn t_perm_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    n_perm: usize,
    seed: u64,
) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Computes the integrated L2 distance between two group sample-mean curves as the test statistic: `T = integral (m_A(t) - m_B(t))^2 dt`. Under the null (equal population means), observed curves from both groups are pooled and randomly re-split into two groups of the original sizes `n_perm` times; the statistic is recomputed each time. The p-value is the fraction of permuted statistics >= the observed value. Mirrors `fda::tperm.fd` in R.

**Input shape:** Two independent groups of functional curves evaluated on a common grid. Each group is an `(n_group, m)` matrix; the argvals vector has length `m`. Groups need not be the same size. This is a two-sample test — it does NOT accept a group-label vector.

**Dataset fit:** Growth (boys vs girls, 39/54 x 31 points) is the canonical example: two biological groups, same evaluation grid. Sonar (Mine vs Rock, 111/97 x 60 points) is a second option. Canadian Weather by region requires subsetting into two groups and is viable.

**Return:** `TestResult { statistic: f64, p_value: f64, n_perm: usize }` (non-exhaustive; `n_perm` matches the input `n_perm` for permutation tests).

**Python binding I/O contract:**
- Inputs: `data_a: ndarray (n_a, m)`, `data_b: ndarray (n_b, m)`, `argvals: ndarray (m,)`, `n_perm: int = 999`, `seed: int = 0`
- Output: `dict` with keys `statistic`, `p_value`, `n_perm`
- Column-major conversion required for both data arrays (standard `numpy2d_to_fdmatrix`).

---

### A2. `f_perm_test` — Integrated-F permutation test

**Verified signature:**
```rust
pub fn f_perm_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    n_perm: usize,
    seed: u64,
) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Like `t_perm_test` but uses an integrated F-ratio statistic — the pointwise ratio of between-group to within-group variance, integrated over the domain. The F-statistic upweights domain regions where the between-group signal is large relative to the pooled within-group spread. Mirrors `fda::Fperm.fd` in R.

**Input shape:** Identical to `t_perm_test` (two independent groups, common grid).

**Dataset fit:** Same candidates as `t_perm_test`; Growth (sex split) is cleanest.

**Return:** `TestResult` (same struct). `n_perm` stores the input permutation count.

**Python binding I/O contract:** Identical shape to `t_perm_test`; only the function name and internal statistic differ.

**Differentiation from `t_perm_test`:** The integrated-F statistic is more sensitive when group variance also differs between groups; the t-statistic focuses purely on the mean-curve difference. Both are valid — expose both.

---

### A3. `two_sample_mean_test` — Hotelling T-squared on FPC basis

**Verified signature:**
```rust
pub fn two_sample_mean_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    ncomp: usize,
) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Projects both groups onto a shared FPC basis (computed from pooled data), reducing each curve to a `ncomp`-dimensional score vector. Applies Hotelling's T-squared to the difference in mean score vectors. The test statistic is scaled by the effective sample size and compared to a chi-squared distribution with `ncomp` degrees of freedom (asymptotic approximation). Mirrors `fda.usc` methodology.

**Input shape:** Two groups, common grid. `ncomp` is a tuning parameter (number of FPC components to retain; typically 2-10). Depends on internal FPCA — no pre-fitted basis object required.

**Dataset fit:** Same as `t_perm_test`. `ncomp` should be small relative to `min(n_a, n_b)`.

**Return:** `TestResult`. `n_perm = 0` always (asymptotic test, no permutations).

**Python binding I/O contract:**
- Inputs: `data_a: ndarray (n_a, m)`, `data_b: ndarray (n_b, m)`, `argvals: ndarray (m,)`, `ncomp: int`
- Output: `dict` with keys `statistic`, `p_value`, `n_perm` (always 0)
- No default for `ncomp` — caller must choose; suggest `ncomp=5` as a reasonable default in the Python wrapper's docstring.

**Dependency on existing feature:** Internally uses FPCA (the same FPCA machinery bound in `fdars.regression.fdata_to_pc_1d`). This is an internal dependency — no existing Python object is consumed.

---

### A4. `mean_scb` — Degras simultaneous confidence band

**Verified signature:**
```rust
pub fn mean_scb(
    data: &FdMatrix,
    argvals: &[f64],
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: MultiplierDistribution,
) -> Result<ToleranceBand, FdarError>
```

**Return type verified:** `ToleranceBand { lower: Vec<f64>, upper: Vec<f64>, center: Vec<f64>, half_width: Vec<f64> }` (non-exhaustive).

**MultiplierDistribution variants:** NOT resolved via docs.rs HTML (404 on enum page). **Confirm variants at plan time** against crate source. Expected to be Gaussian / Rademacher based on the Degras (2011) bootstrap-multiplier methodology.

**Conceptual behavior:** Computes a pointwise-simultaneous confidence band for the true mean function mu(t) using the Degras (2011) multiplier-bootstrap method. At each point t, the band `[center(t) +/- half_width(t)]` is constructed so that `P(mu(t) in [lower(t), upper(t)] for all t) approx confidence`. The bandwidth parameter governs the smoothing of the covariance kernel estimator used internally. `nb` is the number of bootstrap multiplier draws.

**Input shape:** Single-group functional data, shape `(n, m)`. This is NOT a two-sample test — it characterizes one sample's mean.

**Dataset fit:** Canadian Weather (all 35 stations, temperature); Growth (all girls, or all boys, 39 or 54 curves x 31 points). Prefer a dataset with enough curves (n >= 20) for the bootstrap to be meaningful.

**Python binding I/O contract:**
- Inputs: `data: ndarray (n, m)`, `argvals: ndarray (m,)`, `bandwidth: float`, `nb: int`, `confidence: float`, `multiplier: str` (string-dispatch to `MultiplierDistribution` variant — pattern from `fdars.depth`)
- Output: `dict` with keys `lower`, `upper`, `center`, `half_width` (each a 1-D ndarray of length m)

**Complexity note:** The `multiplier` parameter requires a string-to-enum dispatch in the Rust binding. Because `MultiplierDistribution` non-exhaustive status is unknown — **confirm** — the binding must include a fallback `PyValueError` arm for unknown strings.

---

### A5. `scb_two_sample_test` — SCB test for mean difference

**Verified signature:**
```rust
pub fn scb_two_sample_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: MultiplierDistribution,
) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Constructs a simultaneous confidence band around the mean-difference curve `mu_A(t) - mu_B(t)`. Rejects equal-means null when the band excludes zero anywhere on the domain. The `statistic` field encodes the maximum standardized excursion of the difference band from zero. This is geometrically interpretable — the user can visualize the band and see where means differ.

**Input shape:** Two independent groups, common grid. Same parameter set as `mean_scb` plus the second group.

**Dataset fit:** Growth (boys vs girls split) gives a biologically meaningful mean-difference band.

**Python binding I/O contract:**
- Inputs: `data_a: ndarray (n_a, m)`, `data_b: ndarray (n_b, m)`, `argvals: ndarray (m,)`, `bandwidth: float`, `nb: int`, `confidence: float`, `multiplier: str`
- Output: `dict` with keys `statistic`, `p_value`, `n_perm` (n_perm = nb for SCB bootstrap, not standard permutation — verify at plan time which value is stored)

---

### A6. `flm_f_test` — Overall-significance F-test for fitted FLM

**Verified signature:**
```rust
pub fn flm_f_test(fit: &FregreLmResult) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Tests whether the functional predictor has ANY effect. Uses the classical regression F-formula: `F = (R_sq/p) / ((1 - R_sq)/(n - p - 1))`, where p is the number of FPC components retained in the model and n is the sample size. The p-value is from an F-distribution with degrees of freedom `(p, n - p - 1)`. Returns an error for degenerate fits (zero components, invalid R-squared, non-positive df).

**Input shape:** A **fitted** `FregreLmResult` object — the output of the existing `fdars.regression` FLM fitting function. No raw data needed; all necessary quantities (R-squared, n, p, residuals) are stored in the fit struct.

**FregreLmResult fields (verified):** `intercept`, `beta_t`, `gamma`, `r_squared`, `r_squared_adj`, `residual_se`, `aic`, `bic`, `gcv`, `fitted_values`, `residuals`, `beta_se`, `std_errors`, `fpca`, `coefficients`, `ncomp`.

**Python dependency:** The Python binding MUST consume the existing `FregreLmResult` dict that `fdars.regression` already returns. Two options: (1) accept the raw dict fields and reconstruct the Rust struct internally, or (2) expose a new "fitted model handle" type. Option 1 matches the v4.0 pattern for `ShiftRegistrationResult`; **preferred approach** is to accept the relevant scalar fields (r_squared, n_obs, ncomp) directly as Python floats/ints rather than demanding the user re-pass the full dict — simpler API, avoids a handle registry. **Confirm binding strategy at plan time.**

**Dataset fit:** Tecator NIR spectra -> fat content scalar response (the canonical FLM benchmark: 240 spectra x 100 wavelengths, fat% as response).

---

### A7. `flm_gof_test` — Ramsey-RESET goodness-of-fit test

**Verified signature:**
```rust
pub fn flm_gof_test(fit: &FregreLmResult) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Residual-based lack-of-fit test. Regresses FLM residuals against polynomial terms of the fitted values (RESET-style specification check) and reports an F-statistic for whether any polynomial term is significant. A significant result (small p-value) indicates the linear model fails to capture the conditional mean structure — the functional predictor has a nonlinear effect on the scalar response.

**Input shape:** Same as `flm_f_test` — a fitted `FregreLmResult`.

**Dataset fit:** Tecator (same as `flm_f_test`; natural to run both tests after fitting one model).

**Binding note:** Same binding strategy question as `flm_f_test` — these two functions should be bound symmetrically.

---

### A8. `oneway_anova_vstat` — Asymptotic one-way functional ANOVA (V-statistic)

**Verified signature:**
```rust
pub fn oneway_anova_vstat(
    data: &FdMatrix,
    groups: &[usize],
    argvals: &[f64],
) -> Result<TestResult, FdarError>
```

**Conceptual behavior:** Tests whether K >= 2 groups share a common mean curve. The V-statistic is the Simpson-integrated between-group sum of squares: `V = n * integral sum_k n_k/n (m_k(t) - m(t))^2 dt`. The null p-value uses a scaled chi-squared approximation (Satterthwaite moment-matching) to handle the unknown functional covariance. `TestResult.n_perm = 0` always (asymptotic). The existing permutation-based `fanova` function in `fdars.depth` (already bound) is the complementary alternative — the V-statistic version avoids the cost of permutation resampling.

**Input shape:** Single combined data matrix `(n_total, m)`, with a `groups: &[usize]` slice of length `n_total` containing integer group labels. This is the standard "pooled matrix + label vector" encoding, distinct from the two separate matrices used by the two-sample tests. **Confirm 0-indexed vs 1-indexed at plan time.**

**Dataset fit:** Canadian Weather by region (Atlantic/Pacific/Continental — 3 groups, ~35 stations total) is the natural K=3 example. Phoneme (5 classes x 80 curves each, 400 total, 256 points) is ideal for a K=5 test but is a larger dataset.

**Python binding I/O contract:**
- Inputs: `data: ndarray (n, m)`, `groups: ndarray (n,)` of int, `argvals: ndarray (m,)`
- Output: `dict` with keys `statistic`, `p_value`, `n_perm` (always 0)
- `groups` should accept a Python list or 1-D int array — binding converts to `Vec<usize>`.

**Dependency on existing feature:** Complements the existing permutation `fanova` in `fdars.depth` — expose together, document as "asymptotic (fast) vs permutation (exact)".

---

## Group B — Depth & Functional Boxplot (extend `fdars.depth`)

### B1. `functional_depth` — Unified self-depth dispatcher

**Verified signature:**
```rust
pub fn functional_depth(
    data: &FdMatrix,
    method: DepthMethod,
) -> Result<Vec<f64>, FdarError>
```

**DepthMethod enum (verified from dispatch.rs source):**
```rust
pub enum DepthMethod {
    FraimanMuniz { scale: bool },
    Band,
    ModifiedBand,
    RandomProjection { nproj: usize, seed: u64 },
}
```

**Non-exhaustive status:** Flagged in PROJECT.md as `#[non_exhaustive]` — **confirm at plan time**. If non-exhaustive, the binding match arm must include a wildcard fallback that returns `PyValueError`.

**Conceptual behavior:** Computes the **self-depth** of every curve with respect to the sample itself — i.e., how central each curve is within its own group. Unlike the lower-level functions (`fraiman_muniz_1d`, `band_1d`, etc.) which accept a separate `ref_data` parameter, `functional_depth` uses `data` as both the set of curves to score AND the reference distribution. Returns a `Vec<f64>` of length `n` (one depth value per observation, higher = more central).

**Input shape:** Single-group matrix `(n, m)`. The method parameter selects the depth algorithm and its internal hyperparameters.

**Python binding I/O contract:**
- Inputs: `data: ndarray (n, m)`, `method: str` (e.g., `"fraiman_muniz"`, `"band"`, `"modified_band"`, `"random_projection"`), plus method-specific kwargs — **preferred API**: keyword args `scale: bool = True`, `nproj: int = 50`, `seed: int = 0` passed alongside `method` string, with the binding constructing the `DepthMethod` variant.
- Output: `ndarray (n,)` of depth values

**Dataset fit:** Canadian Weather (35 stations x 365 days) is canonical for depth examples (already used in the existing `fdars.depth` docs).

**Complexity:** LOW — thin dispatcher over already-bound functions. The main implementation work is the string-to-enum dispatch with `#[non_exhaustive]` fallback.

---

### B2. `functional_boxplot` — Lopez-Pintado–Romo functional boxplot

**Verified signature:**
```rust
pub fn functional_boxplot(
    data: &FdMatrix,
    method: DepthMethod,
    factor: f64,
) -> Result<FunctionalBoxplotResult, FdarError>
```

**FunctionalBoxplotResult fields (verified from dispatch.rs source):**
```rust
pub struct FunctionalBoxplotResult {
    pub median: Vec<f64>,          // deepest curve (pointwise at evaluation grid)
    pub central_lower: Vec<f64>,   // lower bound of 50% central region
    pub central_upper: Vec<f64>,   // upper bound of 50% central region
    pub whisker_lower: Vec<f64>,   // lower fence = central_lower - factor * spread
    pub whisker_upper: Vec<f64>,   // upper fence = central_upper + factor * spread
    pub outliers: Vec<usize>,      // row indices of observations outside fence
    pub depths: Vec<f64>,          // per-curve depth scores (same as functional_depth)
}
```

**Non-exhaustive status:** **Confirm at plan time.**

**Conceptual behavior:** Implements the Lopez-Pintado & Romo (2009) functional boxplot algorithm:
1. Compute self-depth for all n curves.
2. Identify the **median curve**: the deepest observation (highest depth score). Unlike a pointwise median, this is an actual observed curve.
3. Construct the **50% central region** (CR_50): the pointwise envelope of the top 50% deepest curves. `central_lower[t] = min over top-50%-deepest curves at t`, `central_upper[t] = max`.
4. Inflate the central region by `factor` (default 1.5 by convention, same as Tukey boxplot) to obtain **whisker/fence** bounds.
5. Any curve that exits the fence at any point t is flagged as an **outlier** (its row index is added to `outliers`).

This is a **numeric-only** operation — no plotting is done. The result struct is designed to be passed to a separate plotting function (in Python: `fdars.plot`).

**`factor` parameter:** Analogous to Tukey's 1.5 x IQR factor. `factor=1.5` is the standard choice; expose with default 1.5.

**Input shape:** Single-group matrix `(n, m)` plus a `DepthMethod` selection.

**Python binding I/O contract:**
- Inputs: `data: ndarray (n, m)`, `method: str`, `factor: float = 1.5`, plus method-specific kwargs (same pattern as `functional_depth`)
- Output: `dict` with keys `median` (ndarray m,), `central_lower` (ndarray m,), `central_upper` (ndarray m,), `whisker_lower` (ndarray m,), `whisker_upper` (ndarray m,), `outliers` (list[int]), `depths` (ndarray n,)

**Dataset fit:** Canadian Weather (35 stations x 365 days) is the canonical example — Lopez-Pintado & Romo's original paper uses temperature curves. Expect ~2-4 outlier stations at factor=1.5.

**Complexity:** MEDIUM — the struct-to-dict conversion is straightforward but `outliers: Vec<usize>` requires conversion to a Python list (not a numpy array). The `DepthMethod` string dispatch is shared with `functional_depth`.

**Diagram opportunity:** The functional boxplot is highly visual — the central region, whiskers, median, and flagged outliers map directly to a band-plot SVG. This is the most diagram-rich new feature in the milestone.

---

## Group C — Basis & Smoothing Quick Wins

### C1. `constant_basis` — All-ones intercept column

**Verified presence in module:** Listed in `fdars_core::basis` index. **Exact signature NOT verified** — docs.rs fn page returned 404.

**Expected signature [confirm at plan time]:**
```rust
pub fn constant_basis(argvals: &[f64]) -> Vec<f64>
```

**Confirm:** parameter name (`t` or `argvals`), return type (plain `Vec<f64>` or `Result`), and whether it returns a 1-D vector or an `(m, 1)` matrix.

**Conceptual behavior:** Returns a vector of all 1.0s of length `m` (the number of evaluation points). This is the m x 1 constant/intercept column used in penalized regression when a constant term is included in the basis expansion. Adding this as the first column of a basis matrix ensures the model has a free intercept that is not penalized. It is the functional-data analog of an intercept column in a design matrix.

**Input shape:** `argvals: ndarray (m,)` -> output `ndarray (m,)` (all ones). Trivial computation, but having it as a named function makes basis construction explicit and matches the style of `bspline_basis`, `fourier_basis`.

**Python binding I/O contract:**
- Input: `argvals: ndarray (m,)`
- Output: `ndarray (m,)` of 1.0s

**Dataset fit:** N/A — demonstrated inline in basis-construction examples (e.g., `np.column_stack([constant_basis(t), bspline_basis(t, nbasis=8)])`).

**Complexity:** LOW — trivially thin.

---

### C2. `smooth_basis_aic` — AIC-optimal basis roughness penalty

**Verified signature:**
```rust
pub fn smooth_basis_aic(
    data: &FdMatrix,
    argvals: &[f64],
    basis_type: &BasisType,
    nbasis: usize,
    lfd_order: usize,
    log_lambda_range: (f64, f64),
    n_grid: usize,
) -> Option<SmoothBasisResult>
```

**SmoothBasisResult fields (verified):** `coefficients: FdMatrix`, `fitted: FdMatrix`, `edf: f64`, `aic: f64`, `gcv: f64`, `bic: f64`, `penalty_matrix: Vec<f64>`, `nbasis: usize` (non-exhaustive).

**BasisType enum string map:** Shared with existing `smooth_basis_gcv` binding — `"bspline"` / `"fourier"` matching the existing `basis_type` string convention in `basis_mod.rs`. **Confirm exact strings at plan time.**

**Conceptual behavior:** Identical in structure to `smooth_basis_gcv` (already bound) — grid-searches `log10(lambda)` over `log_lambda_range` at `n_grid` points — but selects the smoothing parameter lambda by minimizing AIC rather than GCV. AIC = `n * log(RSS/n) + 2 * EDF` where EDF is the effective degrees of freedom computed from the hat-matrix trace. AIC penalizes model complexity more lightly than GCV for small n, often yielding smoother fits; GCV has better theoretical properties for large n. Exposing both gives the user a practical choice.

**Return type:** `Option<SmoothBasisResult>` (returns `None` if the grid search fails or data is degenerate) — the binding converts `None` to `PyValueError("smooth_basis_aic failed")`, matching the pattern for `smooth_basis_gcv`.

**Python binding I/O contract:**
- Inputs: `data: ndarray (n, m)`, `argvals: ndarray (m,)`, `basis_type: str`, `nbasis: int`, `lfd_order: int`, `log_lambda_range: tuple[float, float]`, `n_grid: int`
- Output: `dict` with keys `coefficients` (ndarray n x nbasis), `fitted` (ndarray n x m), `edf`, `aic`, `gcv`, `bic`, `nbasis`

**Dataset fit:** Canadian Weather (35 x 365) or Tecator (240 x 100). A natural comparison: run `smooth_basis_gcv` and `smooth_basis_aic` on the same data and compare the selected lambda and EDF.

**Complexity:** LOW — literal copy-paste of the `smooth_basis_gcv` binding with the function name changed. The `BasisType` dispatch is already written.

---

### C3. `BasisCriterion::Aic` — AIC criterion for `basis_nbasis_cv`

**Verified:** `BasisCriterion` enum has four variants: `Gcv`, `Cv`, `Aic`, `Bic`. The `Aic` variant is confirmed at docs.rs/fdars-core/0.20.0.

**`basis_nbasis_cv` signature (verified):**
```rust
pub fn basis_nbasis_cv(
    data: &FdMatrix,
    argvals: &[f64],
    nbasis_range: &[usize],
    basis_type: &BasisType,
    criterion: BasisCriterion,
    n_folds: usize,
    lambda: f64,
) -> Option<BasisNbasisCvResult>
```

**Conceptual behavior of `Aic` variant:** When `criterion = BasisCriterion::Aic`, the function evaluates each candidate `nbasis` value by fitting a penalized smoother and selecting the one that minimizes AIC (using the hat-matrix trace to compute EDF, same as `smooth_basis_aic`). This is additive to the existing `Gcv`/`Cv`/`Bic` variants — the binding extension is a string-dispatch addition: accept `"aic"` as a valid `criterion` string alongside the existing accepted strings.

**Python binding impact:** The existing `basis_nbasis_cv` binding in `smoothing_mod.rs` likely already accepts a `criterion: &str` parameter. Adding `"aic"` to the match arm is the full scope of the change. **Confirm the existing binding's criterion string map at plan time.**

**Complexity:** TRIVIAL — one match arm addition in an existing binding. Not a new function — an extension of an existing one.

---

## Feature Landscape Summary

### Table Stakes (Users Expect These)

For an FDA library offering "functional inference" as a capability:

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Two-sample permutation t-test (`t_perm_test`) | Every FDA text covers this; mirrors R `fda::tperm.fd` | LOW | Thin binding; column-major for both groups |
| Two-sample permutation F-test (`f_perm_test`) | Paired with t-test; slightly different statistic | LOW | Same binding pattern as t-test |
| One-way functional ANOVA (`oneway_anova_vstat`) | Groups > 2 is the natural generalization | LOW | Grouped-data input; no permutation cost |
| Functional boxplot (`functional_boxplot`) | Visual outlier detection; Lopez-Pintado & Romo is THE classic reference | MEDIUM | Struct to dict; DepthMethod dispatch |
| Unified depth dispatcher (`functional_depth`) | Makes self-depth first-class; avoids calling specific `fraiman_muniz_1d` etc. | LOW | String dispatch over DepthMethod |
| AIC smoothing selection (`smooth_basis_aic`) | AIC is familiar to any statistician; GCV alone is not sufficient | LOW | Copy of GCV binding with function swap |

### Differentiators (Beyond the Baseline)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Degras SCB for the mean (`mean_scb`) | Simultaneous bands (not pointwise) for the mean — statistically correct for functional inference | MEDIUM | `MultiplierDistribution` enum; `ToleranceBand` to dict |
| SCB two-sample test (`scb_two_sample_test`) | Geometrically interpretable rejection (see where means differ); unique to FDA | MEDIUM | Same complexity as `mean_scb` |
| Hotelling T-squared on FPC basis (`two_sample_mean_test`) | Bridges multivariate and functional testing; asymptotic, no resampling cost | LOW | FPC computed internally |
| FLM overall-significance F-test (`flm_f_test`) | First-class inference for the existing regression surface | MEDIUM | Binding strategy for `FregreLmResult` handle is the key design choice |
| FLM goodness-of-fit / RESET test (`flm_gof_test`) | Model diagnostic after fitting; uncommon in Python FDA libraries | MEDIUM | Same handle-strategy issue as `flm_f_test` |
| `BasisCriterion::Aic` in `basis_nbasis_cv` | Completes criterion coverage (GCV/CV/AIC/BIC); all four now exposed | TRIVIAL | One match arm |
| `constant_basis` intercept column | Explicit, named, basis-construction primitive; makes model building transparent | TRIVIAL | All-ones vector |

### Anti-Features (Do Not Build These)

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| Plotting inside `functional_boxplot` binding | Users expect "boxplot" to show a plot | Mixing computation and I/O in a Rust binding is wrong; breaks the offline docs build | Return `FunctionalBoxplotResult` dict; let `fdars.plot` handle visualization separately |
| Exposing `MultiplierDistribution` as an integer enum | Simpler for binding | Opaque to the user; breaks discoverability | String dispatch with clear error messages for unknown strings |
| Re-fitting the model inside `flm_f_test` / `flm_gof_test` | Avoids a "handle" complexity | Regression is expensive; re-fitting would silently change results if args differed | Accept the fit dict fields directly; document the pattern |
| Exposing `smooth_basis_gcv_with_config` / `basis_nbasis_cv_with_config` | "More control" | The config-struct API duplicates the primary function and adds binding complexity with no Python benefit | Bind only the primary `smooth_basis_aic` and `basis_nbasis_cv` |

---

## Feature Dependencies

```
functional_boxplot
    └──requires──> functional_depth (DepthMethod dispatch shared; boxplot reuses depth internals)

flm_f_test
    └──requires──> FregreLmResult (fitted via existing fdars.regression FLM fitting)
flm_gof_test
    └──requires──> FregreLmResult (same)

oneway_anova_vstat ──complements──> existing fdars.depth.fanova (permutation ANOVA)
    note: V-statistic is asymptotic (fast); fanova is permutation (exact)

smooth_basis_aic ──mirrors──> existing smooth_basis_gcv (same signature, AIC criterion)
BasisCriterion::Aic ──extends──> existing basis_nbasis_cv (add "aic" to criterion dispatch)

mean_scb ──returns──> ToleranceBand (same struct as fdars.tolerance — already bound)
scb_two_sample_test ──returns──> TestResult (same as permutation tests)
```

### Dependency Notes

- `functional_boxplot` shares the `DepthMethod` enum dispatch with `functional_depth` — implement both in the same binding block in `depth_mod.rs`.
- `flm_f_test` and `flm_gof_test` consume `FregreLmResult` from `fdars_core::scalar_on_function`, not `fdars_core::regression` (FPCA/PLS). The existing `fdars.regression` Python surface binds FPCA/PLS; the FLM binding lives in a different upstream module. **The `inference_mod.rs` binding will need to import `fdars_core::scalar_on_function::FregreLmResult`** — this is a cross-module dependency in the Rust binding layer.
- `mean_scb` returns `ToleranceBand` — this type is already used by `fdars.tolerance`. The conversion function `toleranceband_to_pydict` (or equivalent) may already exist in `convert.rs`. **Check at plan time.**
- `oneway_anova_vstat` produces `TestResult.n_perm = 0` consistently — document this convention so users do not mistake it for a permutation test that ran zero permutations.

---

## Input Data Shapes by Method

| Method | Input Shape | Dataset Recommendation |
|--------|-------------|----------------------|
| `t_perm_test` | Two separate `(n_a, m)` and `(n_b, m)` arrays | Growth: boys (39x31) vs girls (54x31) |
| `f_perm_test` | Two separate `(n_a, m)` and `(n_b, m)` arrays | Growth: boys vs girls |
| `two_sample_mean_test` | Two separate `(n_a, m)` and `(n_b, m)` + `ncomp` | Growth: boys vs girls |
| `mean_scb` | Single `(n, m)` + bandwidth, nb, confidence | Canadian Weather temperature (35x365) |
| `scb_two_sample_test` | Two separate `(n_a, m)` and `(n_b, m)` + SCB params | Growth: boys vs girls |
| `flm_f_test` | Fitted `FregreLmResult` (scalar fields from dict) | Tecator NIR -> fat% |
| `flm_gof_test` | Fitted `FregreLmResult` (scalar fields from dict) | Tecator NIR -> fat% |
| `oneway_anova_vstat` | Pooled `(n, m)` + `groups: (n,)` int array | Canadian Weather by region (3 regions, ~35 stations) |
| `functional_depth` | Single `(n, m)` + method string | Canadian Weather temperature (35x365) |
| `functional_boxplot` | Single `(n, m)` + method string + factor | Canadian Weather temperature (35x365) |
| `constant_basis` | `argvals (m,)` | Used inline in basis-construction examples |
| `smooth_basis_aic` | `(n, m)` data + `(m,)` argvals + basis params | Canadian Weather (35x365) or Tecator (240x100) |
| `BasisCriterion::Aic` | Same as `basis_nbasis_cv` — `(n, m)` + params | Canadian Weather (35x365) |

---

## MVP Definition for v5.0 Milestone

### Launch With (binding phase)

The binding phase delivers all functions. There is no partial launch — the goal is to expose the full 0.20.0 surface.

Priority order within the binding phase (by risk/dependency):

- **New `inference_mod.rs`** — Group A in full: 8 functions + `TestResult -> dict` conversion. The `FregreLmResult` handle strategy and `MultiplierDistribution` enum are the two open design questions; resolve both before writing code.
- **`functional_depth` + `functional_boxplot`** in `depth_mod.rs` — Group B: DepthMethod dispatch + FunctionalBoxplotResult dict. Lower risk than Group A (no new struct import dependencies).
- **`constant_basis` + `smooth_basis_aic` + `BasisCriterion::Aic`** in `basis_mod.rs` / `smoothing_mod.rs` — Group C: trivially thin or one-match-arm extensions.

### Add After Binding (advisor phase)

- Inference diagnostics aspect in `build_diagnostics`: summarize `TestResult` p-values/statistics, grounded. Scope: confirm whether a full 14th aspect is warranted or the inference results are better surfaced via the existing interpretation task family.
- Functional-boxplot outlier diagnostics: expose outlier indices and depths as a structured diagnostic (parallels the existing depth-based outlier diagnostics in `fdars.outliers`).

### Future Consideration

- Plotting support for functional boxplot in `fdars.plot` — the numeric result is the binding deliverable; a `plot_functional_boxplot()` helper is useful but not required for v5.0 correctness.
- HTTP/SSE MCP transport — deferred since v2.0; not relevant to this milestone.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| `t_perm_test` | HIGH | LOW | P1 |
| `f_perm_test` | HIGH | LOW | P1 |
| `functional_boxplot` | HIGH | MEDIUM | P1 |
| `functional_depth` | HIGH | LOW | P1 |
| `smooth_basis_aic` | HIGH | LOW | P1 |
| `oneway_anova_vstat` | HIGH | LOW | P1 |
| `two_sample_mean_test` | MEDIUM | LOW | P1 |
| `constant_basis` | MEDIUM | TRIVIAL | P1 |
| `BasisCriterion::Aic` | LOW | TRIVIAL | P1 |
| `mean_scb` | MEDIUM | MEDIUM | P2 |
| `scb_two_sample_test` | MEDIUM | MEDIUM | P2 |
| `flm_f_test` | MEDIUM | MEDIUM | P2 |
| `flm_gof_test` | MEDIUM | MEDIUM | P2 |

**Priority key:**
- P1: Bind in the core bindings phase (all present — no optional items)
- P2: Bind in the core bindings phase but design questions must be resolved first (MultiplierDistribution variants; FregreLmResult handle strategy)
- P3: Not used — all features are in scope for this milestone

---

## Open Questions (Confirm at Plan Time)

1. **`MultiplierDistribution` variants**: 404 on enum doc page. Fetch from source (`src/inference/mod.rs` or equivalent). Required before binding `mean_scb` and `scb_two_sample_test`.
2. **`flm_f_test` / `flm_gof_test` binding strategy**: Accept extracted scalar fields (`r_squared: f64, ncomp: usize, n_obs: usize, residuals: ndarray`) rather than a handle object? Or reconstruct a minimal `FregreLmResult`-compatible struct? The v4.0 `ShiftRegistrationResult` binding accepted dict fields for a simpler API — prefer that pattern unless `FregreLmResult`'s F-test computation uses deeper fields.
3. **`DepthMethod` non-exhaustive status**: PROJECT.md says `#[non_exhaustive]` — confirm whether a wildcard fallback is required in the Rust binding match arm.
4. **`oneway_anova_vstat` group indexing**: 0-indexed or 1-indexed `usize` group labels? The binding should accept Python int arrays and document the expected base.
5. **`ToleranceBand` in `convert.rs`**: Does a `toleranceband_to_pydict` conversion already exist (from `fdars.tolerance` bindings)? Reuse if so; write once if not.
6. **`constant_basis` exact signature**: Confirm the parameter name (`t` vs `argvals`), return type (plain `Vec<f64>` vs `Result`), and dimension (1-D vector vs 2-D `(m, 1)` matrix).
7. **`scb_two_sample_test` `n_perm` field value**: Is `n_perm` set to `nb` (bootstrap draws) or 0 in the returned `TestResult`? Impacts how the Python dict documents this field.
8. **Existing `basis_nbasis_cv` Python binding**: Does it already accept a `criterion: str` parameter? If so, confirm the current accepted values before adding `"aic"`.

---

## Sources

- `docs.rs/fdars-core/0.20.0/fdars_core/inference/` — verified (WebFetch; function signatures and TestResult fields verified; HIGH confidence)
- `docs.rs/fdars-core/0.20.0/fdars_core/depth/dispatch/index.html` — verified (dispatch module; DepthMethod + FunctionalBoxplotResult fields verified from dispatch.rs source view; HIGH confidence)
- `docs.rs/fdars-core/0.20.0/fdars_core/smooth_basis/` — verified (smooth_basis_aic signature + SmoothBasisResult fields + BasisCriterion variants; HIGH confidence)
- `docs.rs/fdars-core/0.20.0/fdars_core/tolerance/struct.ToleranceBand.html` — verified (ToleranceBand fields; HIGH confidence)
- `docs.rs/fdars-core/0.20.0/fdars_core/scalar_on_function/` — verified (FregreLmResult fields; HIGH confidence)
- `docs.rs/fdars-core/0.20.0/fdars_core/basis/` — `constant_basis` listed in module index; fn page returned 404 — signature UNVERIFIED
- `MultiplierDistribution` enum — doc page returned 404 — variants UNVERIFIED
- `/home/simonm/projects/rust/pyfda/.planning/PROJECT.md` — milestone context and binding patterns from v4.0
- `/home/simonm/projects/rust/pyfda/src/depth_mod.rs` / `basis_mod.rs` / `smoothing_mod.rs` — existing binding patterns
- `/home/simonm/projects/rust/pyfda/docs/data/README.md` — dataset shapes and group structure for example selection

---
*Feature research for: pyfda v5.0 — fdars-core 0.20.0 binding (inference + depth/boxplot + basis/smoothing)*
*Researched: 2026-08-17*
