# Phase 67: Functional Time Series (`fdars.fts`) — Research

**Researched:** 2026-09-02
**Domain:** PyO3 binding — new `fdars.fts` submodule over fdars-core 0.33 `fts`
**Confidence:** HIGH — all findings read directly from 0.33 registry source and existing project files this session

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Bind the FULL fts module — all 13 public functions (user decision):
  - Forecasting: `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`
  - Dimension reduction / spectral: `fplsr`, `dpca`, `dpca_reconstruct`, `spectral_density`
  - Diagnostics: `functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance`

### Claude's Discretion (convention-driven)
- Return shape: every function returns a documented PyDict built from the fdars-core result struct
- Binding style: thin native 1:1 `#[pyfunction]` wrappers only — no pure-Python convenience layer for fts
- `ncomp` default: `ncomp=3` via `#[pyo3(signature = ...)]`
- Transposition safety: route all 2D array inputs through `convert::numpy2d_to_fdmatrix`; every function that takes 2D data gets a non-square (`n_obs ≠ n_points`) test fixture
- Determinism: where upstream takes a seed, expose it with `seed=42` default
- Error handling: propagate `FdarError` → `PyValueError` via `convert::to_pyresult`; any `#[non_exhaustive]` enum gets an `Err`-returning wildcard arm

### Deferred Ideas (OUT OF SCOPE)
- Advisor `fts` aspect (ADV-01) — Phase 72
- `fdars.fts` docs page with runnable offline worked example (DOCS-01) — Phase 73
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FTS-01 | New `fdars.fts` submodule registered and importable; `ftsm` model fit + `ftsm_forecast` / multistep forecasting exposed with a PyDict result (transposition-guarded on non-square input) | §3 exact signatures; §4 struct fields; §5 conversion pattern; §8 registration edits |
| FTS-02 | Time-series diagnostics — `functional_acf` / `functional_pacf`, `stationarity_test`, `long_run_covariance` — with deterministic seeds | §3 exact signatures (seed params); §4 FacfResult, StationarityResult, LongRunCovResult fields; §7 seed convention |
| FTS-03 | Dimension-reduction extras — `fplsr`, `dpca`, `dpca_reconstruct`, `spectral_density` — each returning a documented PyDict | §3 exact signatures; §4 FplsrResult, DpcaResult, DpcaReconstruction, SpectralDensityResult fields |
</phase_requirements>

---

## Summary

Phase 67 creates `src/fts_mod.rs` — a new PyO3 binding submodule that wraps all 13 public functions in fdars-core 0.33's `fts` module. The pattern is identical to every existing `*_mod.rs`: thin `#[pyfunction]` wrappers, `convert::numpy2d_to_fdmatrix` for 2D inputs, `convert::to_pyresult` for error propagation, and `PyDict` returns with struct fields as keys.

The critical pre-research task (confirmed): result struct field names could NOT be assumed from docs.rs (which 404'd on some). They have now been read verbatim from `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/fts/mod.rs` and the three implementation files. Every PyDict key in the plan must match the exact field names in §4.

No enums are involved in fts — zero `#[non_exhaustive]` enum arguments in any of the 13 functions. The enum/wildcard-arm concern from STATE.md applies to Phases 69 (Fréchet metric-space) and 71 (Shapelet), not Phase 67.

**Primary recommendation:** Write `fts_mod.rs` as three coherent groups matching the upstream submodule split (forecast, acf/diagnostics, spectral), register once in `lib.rs` and `__init__.py`, write tests with a non-square `(n_obs=40, n_points=25)` fixture.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| FPCA-based FTS model fit (`ftsm`) | API / Backend (Rust) | — | Pure computation; all state in returned struct |
| FTS forecasting (`ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`) | API / Backend (Rust) | — | Stateless calls; `FtsmResult` passed by value |
| Functional PLS forecasting (`fplsr`) | API / Backend (Rust) | — | Per-evaluation-point scalar PLS internally |
| Spectral density operator (`spectral_density`) | API / Backend (Rust) | — | FFT-based; rustfft; no Python layer |
| Dynamic FPCA (`dpca`, `dpca_reconstruct`) | API / Backend (Rust) | — | Filter/score computation; inverse-FFT internals |
| ACF / PACF / stationarity / LRC diagnostics | API / Backend (Rust) | — | All seeded MC; deterministic given seed |
| First-difference (`functional_difference`) | API / Backend (Rust) | — | Pure array operation; no argvals needed |
| PyDict assembly + numpy conversion | PyO3 boundary (fts_mod.rs) | — | Row-major↔column-major in `convert.rs` |
| Submodule registration | Module registry (lib.rs + __init__.py) | — | Standard macro + name-list pattern |

---

## Section 1: Research Gap Resolved — 0.31/0.32 Field Names

STATE.md flagged: "0.31/0.32 changelog absent from published CHANGELOG + some 0.33 config-struct fields returned docs.rs 404 — confirm result-struct/config field names against 0.33 source per binding group before writing PyDict converters."

**Status: RESOLVED.** All result struct definitions live in `fts/mod.rs` (the `pub` re-export file), with fields read verbatim below. No config structs are used by any fts function — all parameters are passed positionally/via `#[pyo3(signature = ...)]`. The field name risk was real: `FtsmResult` has `ar_models: Vec<ArModelResult>` (a nested struct), which would not be guessable from docs.rs alone.

---

## Section 2: No Enums in fts API

All 13 public fts functions take only primitive types (`usize`, `u64`, `f64`, `Option<usize>`, `Option<f64>`) plus `&FdMatrix` and `&[f64]`. **No `#[non_exhaustive]` enum arguments anywhere in the fts module.** The enum/wildcard-arm concern from STATE.md applies exclusively to Phases 69 and 71.

---

## Section 3: Exact Function Signatures (all 13 functions)

Sources: read verbatim from registry files this session.
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/fts/forecast.rs]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/fts/acf.rs]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/fts/spectral.rs]

### Group A — Forecasting (forecast.rs)

**`ftsm`** [VERIFIED: forecast.rs:267]
```
pub fn ftsm(data: &FdMatrix, ncomp: usize, argvals: &[f64]) -> Result<FtsmResult, FdarError>
```
- `data`: time-ordered curves, rows = time steps, columns = grid points (n_obs × n_points)
- `ncomp`: retained FPC components; clamped to `min(ncomp, n, m)` internally; must be ≥ 1 and < n
- `argvals`: evaluation grid, length must equal data columns
- Fully deterministic (Yule-Walker, no RNG). No seed parameter.
- Python binding signature: `ftsm(data, argvals, ncomp=3)`

**`ftsm_forecast`** [VERIFIED: forecast.rs:357-363]
```
pub fn ftsm_forecast(fit: &FtsmResult, h: usize, argvals: &[f64]) -> Result<FtsmForecastResult, FdarError>
```
- `fit`: the result of `ftsm` — passed as a Python dict; the binding must reassemble an `FtsmResult` OR this must be a two-call workflow where the Python side passes original data again.
- **CRITICAL DESIGN CONSTRAINT**: `ftsm_forecast` takes `&FtsmResult` (a Rust struct), NOT raw arrays. The binding cannot simply call it with numpy inputs. **Resolution**: expose as a combined Python function that calls `ftsm` internally and then `ftsm_forecast`, OR the Python API accepts the dict returned by `ftsm` and reconstructs an `FtsmResult`. See §6 for the recommended approach.
- `h`: forecast horizon, must be ≥ 1
- `argvals`: must match the fitted grid length (same as used in `ftsm`)
- Python binding signature: `ftsm_forecast(data, argvals, h=1, ncomp=3)` — fits and forecasts in one call

**`ftsm_forecast_multistep`** [VERIFIED: forecast.rs:382-422]
```
pub fn ftsm_forecast_multistep(fit: &FtsmResult, h: usize, argvals: &[f64]) -> Result<FtsmForecastResult, FdarError>
```
- Identical constraint as `ftsm_forecast`. Same `&FtsmResult` input. `h = 1` gives bit-identical output to `ftsm_forecast`.
- Python binding: `ftsm_forecast_multistep(data, argvals, h=5, ncomp=3)` — fits + forecasts h steps

**`ftsm_update`** [VERIFIED: forecast.rs:449-526]
```
pub fn ftsm_update(fit: &FtsmResult, new_curve: &FdMatrix, argvals: &[f64]) -> Result<FtsmResult, FdarError>
```
- `fit`: frozen FPC loadings from a previous `ftsm` call
- `new_curve`: new observation(s) to append, shape (k_new × m), k_new ≥ 1
- Returns an updated `FtsmResult` (frozen mean+rotation+weights, extended scores, re-fit AR models)
- Python binding: same `&FtsmResult` problem — see §6. Recommended: accept `data` (original series) + `new_curve`, refit `ftsm` on original, then call `ftsm_update`.

**`fplsr`** [VERIFIED: forecast.rs:554-603]
```
pub fn fplsr(data: &FdMatrix, ncomp: usize, argvals: &[f64]) -> Result<FplsrResult, FdarError>
```
- `data`: n × m time-ordered curves; requires n ≥ 3 (lag-1 needs ≥ 2 training rows + 1 forecast origin)
- `ncomp`: clamped to `min(ncomp, n-1, m)` internally; must be ≥ 1
- `argvals`: length m
- Fully deterministic. No seed parameter.
- Python binding: `fplsr(data, argvals, ncomp=3)`

### Group B — Diagnostics (acf.rs)

**`functional_acf`** [VERIFIED: acf.rs:254-372]
```
pub fn functional_acf(
    data: &FdMatrix,
    argvals: &[f64],
    max_lag: Option<usize>,
    n_sim: usize,
    ci: f64,
    seed: u64,
) -> Result<FacfResult, FdarError>
```
- `max_lag`: `None` → `min(20, N/4)`; `Some(0)` → `InvalidParameter`; `Some(v)` must satisfy v < n
- `n_sim`: MC replications for white-noise band; must be ≥ 1 (validated)
- `ci`: confidence level, must be in open interval (0.0, 1.0) (validated)
- `seed`: deterministic RNG seed for MC band
- Python binding: `functional_acf(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)`

**`functional_pacf`** [VERIFIED: acf.rs:401-410]
```
pub fn functional_pacf(
    data: &FdMatrix,
    argvals: &[f64],
    max_lag: Option<usize>,
    n_sim: usize,
    ci: f64,
    seed: u64,
) -> Result<FacfResult, FdarError>
```
- **Identical signature to `functional_acf`** — it is a thin wrapper that delegates to `functional_acf`. Returns the same `FacfResult` (both acf and pacf fields populated).
- Python binding: `functional_pacf(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)`

**`functional_difference`** [VERIFIED: acf.rs:470-486]
```
pub fn functional_difference(data: &FdMatrix) -> Result<FdMatrix, FdarError>
```
- Takes only `data` — **no argvals, no seed, no other parameters**
- Input: n × m; output: (n-1) × m (first-order lag-1 difference)
- Requires n ≥ 2; returns `FdarError::InvalidDimension` for n < 2
- Return type is `FdMatrix` directly (not a struct) — Python binding returns a 2D numpy array, NOT a PyDict
- Python binding: `functional_difference(data)` → numpy array shape (n-1, m)

**`stationarity_test`** [VERIFIED: acf.rs:549-624]
```
pub fn stationarity_test(
    data: &FdMatrix,
    argvals: &[f64],
    n_perm: usize,
    seed: u64,
) -> Result<StationarityResult, FdarError>
```
- `n_perm`: permutation count for MC p-value; must be ≥ 1 (validated)
- `seed`: deterministic Fisher-Yates shuffle seed
- Python binding: `stationarity_test(data, argvals, n_perm=999, seed=42)`

**`long_run_covariance`** [VERIFIED: acf.rs:673-727]
```
pub fn long_run_covariance(
    data: &FdMatrix,
    argvals: &[f64],
    bandwidth: Option<usize>,
) -> Result<LongRunCovResult, FdarError>
```
- `bandwidth`: `None` → `⌊N^{1/3}⌋`; `Some(0)` → returns C_0 (sample covariance, valid, not rejected); no upper validation
- No seed — fully deterministic
- Python binding: `long_run_covariance(data, argvals, bandwidth=None)`

### Group C — Spectral (spectral.rs)

**`spectral_density`** [VERIFIED: spectral.rs:114-181]
```
pub fn spectral_density(
    data: &FdMatrix,
    argvals: &[f64],
    bandwidth: Option<usize>,
) -> Result<SpectralDensityResult, FdarError>
```
- `bandwidth`: `None` → `max(1, ⌊N^{1/3}⌋)`; `Some(0)` → `InvalidParameter` (rejected — different from `long_run_covariance` which accepts 0)
- No seed — fully deterministic (FFT-based)
- Python binding: `spectral_density(data, argvals, bandwidth=None)`

**`dpca`** [VERIFIED: spectral.rs:266-364]
```
pub fn dpca(
    data: &FdMatrix,
    argvals: &[f64],
    ncomp: usize,
    bandwidth: Option<usize>,
    filter_lag: Option<usize>,
) -> Result<DpcaResult, FdarError>
```
- `ncomp`: must be in `1..=m`; validated (not clamped silently)
- `bandwidth`: forwarded to `spectral_density`; `Some(0)` → rejected
- `filter_lag`: `None` → uses resolved bandwidth; `Some(L)` where `L >= N/2` → `InvalidParameter`
- No seed — deterministic
- Python binding: `dpca(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)`

**`dpca_reconstruct`** [VERIFIED: spectral.rs:381-482]
```
pub fn dpca_reconstruct(
    data: &FdMatrix,
    argvals: &[f64],
    dpca: &DpcaResult,
) -> Result<DpcaReconstruction, FdarError>
```
- Same `&DpcaResult` opaque-handle problem as `ftsm_forecast`/`ftsm_update`
- **Resolution**: combine with `dpca` — Python function `dpca_reconstruct(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)` calls `dpca` internally, then `dpca_reconstruct`. Returns merged dict with all fields from both `DpcaResult` and `DpcaReconstruction`.
- Python binding: `dpca_reconstruct(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)`

---

## Section 4: Exact Result Struct Fields (verbatim from 0.33 source)

All struct definitions read from `fts/mod.rs` [VERIFIED: fdars-core-0.33.0/src/fts/mod.rs:46-237].

### `FtsmResult` [mod.rs:191-206]
Fields verbatim:
```
pub mean: Vec<f64>            // mean curve μ(u), length m → numpy 1D (m,)
pub rotation: FdMatrix        // FPC loadings φ_k, shape m × ncomp → numpy 2D (m, ncomp)
pub scores: FdMatrix          // FPC score time-series β_{t,k}, shape n × ncomp → numpy 2D (n, ncomp)
pub fitted: FdMatrix          // Reconstructed fitted curves, shape n × m → numpy 2D (n, m)
pub weights: Vec<f64>         // Simpson integration weights, length m → numpy 1D (m,)
pub ncomp: usize              // Effective retained components → int
pub ar_models: Vec<ArModelResult>  // Per-component AR diagnostics → list of dicts
```

**Nested struct `ArModelResult`** [mod.rs:174-181] — each element of `ar_models`:
```
pub order: usize    // Selected AR order p (0 = white noise) → int
pub phi: Vec<f64>   // AR coefficients φ_1..φ_p → numpy 1D (p,)
pub sigma2: f64     // Innovation variance → float
```
The `ar_models` list must be serialized as a Python list of dicts, each with keys `"order"`, `"phi"`, `"sigma2"`.

### `FtsmForecastResult` [mod.rs:214-220]
Fields verbatim:
```
pub forecast: FdMatrix  // Forecast curves, shape h × m → numpy 2D (h, m)
pub h: usize            // Forecast horizon → int
```

### `FplsrResult` [mod.rs:230-237]
Fields verbatim:
```
pub forecast: FdMatrix  // One-step-ahead forecast, shape 1 × m → numpy 2D (1, m)
pub fitted: FdMatrix    // In-sample lag-1 fitted curves, shape (n-1) × m → numpy 2D (n-1, m)
pub ncomp: usize        // Effective PLS components used → int
```

### `FacfResult` [mod.rs:124-134]
Fields verbatim:
```
pub lags: Vec<u32>       // Lag values 1..=max_lag → numpy 1D int array (max_lag,)
pub acf: Vec<f64>        // Functional autocorrelation ρ_h → numpy 1D (max_lag,)
pub pacf: Vec<f64>       // Functional PACF (scalar Durbin-Levinson) → numpy 1D (max_lag,)
pub upper_band: Vec<f64> // MC white-noise confidence band → numpy 1D (max_lag,)
```
Note: `lags` is `Vec<u32>` — convert to numpy int64 array via `PyArray1::<i64>::from_vec` (cast u32→i64) or `PyArray1::<u32>`. Check existing `usize_vec_to_numpy1d` in convert.rs as pattern; u32 needs its own cast.

### `StationarityResult` [mod.rs:142-149]
Fields verbatim:
```
pub statistic: f64  // Test statistic T (KPSS-style partial-sum L2 norm) → float
pub p_value: f64    // MC permutation p-value → float
pub n_perm: usize   // Number of permutations used → int
```

### `LongRunCovResult` [mod.rs:157-166]
Fields verbatim:
```
pub cov_matrix: Vec<f64>  // m×m long-run covariance (column-major flat Vec) → numpy 2D (m, m)
pub m: usize              // Grid dimension → int
pub bandwidth: usize      // Bandwidth used → int
pub n_curves: usize       // Number of curves N → int
```
`cov_matrix` is flat column-major length m×m. Must be reshaped to (m, m) numpy array. Use `PyArray2::from_vec2` with explicit reshape, same pattern as `fdmatrix_to_numpy2d` but for a flat Vec rather than FdMatrix.

### `SpectralDensityResult` [mod.rs:49-62]
Fields verbatim:
```
pub freqs: Vec<f64>        // Fourier frequencies θ_j = 2πj/N, length n_curves → numpy 1D (N,)
pub re: Vec<Vec<f64>>      // Real part of operator at each freq; re[k] is flat m×m col-major → list of numpy 2D (m, m)
pub im: Vec<Vec<f64>>      // Imaginary part; same structure → list of numpy 2D (m, m)
pub m: usize               // Grid dimension → int
pub n_curves: usize        // Number of curves N → int
pub bandwidth: usize       // Bartlett bandwidth used → int
```
`re` and `im` are `Vec<Vec<f64>>` where each inner `Vec` is a flat column-major m×m matrix. Python conversion: iterate `re`/`im`, reshape each inner Vec to (m, m) numpy 2D array, collect into Python list. Alternatively, stack all frequencies into a 3D numpy array of shape (N, m, m) — this is more useful for users and should be the chosen approach.

### `DpcaResult` [mod.rs:79-97]
Fields verbatim:
```
pub filters: Vec<FdMatrix>      // Dynamic eigen-filters; filters[c] is (2L+1) × m FdMatrix → list of numpy 2D
pub scores: FdMatrix            // Dynamic scores, shape (N-2L) × ncomp → numpy 2D
pub eigenvalues: Vec<Vec<f64>>  // Per-component eigenvalue trajectory; eigenvalues[c] has length n_freqs → list of numpy 1D
pub n_freqs: usize              // Number of Fourier frequencies N → int
pub filter_lag: usize           // Filter half-width L → int
pub ncomp: usize                // Retained dynamic components → int
pub valid_range: (usize, usize) // Interior time range (L, N-1-L) → tuple (int, int)
```
`filters`: convert each `FdMatrix` via `fdmatrix_to_numpy2d` → collect into Python list.
`eigenvalues`: each inner `Vec<f64>` → `vec_to_numpy1d` → Python list of 1D arrays.
`valid_range`: `(usize, usize)` → Python tuple `(int, int)`.

### `DpcaReconstruction` [mod.rs:107-115]
Fields verbatim:
```
pub fitted: FdMatrix                  // Reconstructed curves over interior, shape (N-2L) × m → numpy 2D
pub reconstruction_error: Vec<f64>   // Per-K integrated-L2 error, length ncomp → numpy 1D
pub valid_range: (usize, usize)       // Interior range matching DpcaResult → tuple (int, int)
```

### `functional_difference` return (not a struct)
Returns `FdMatrix` directly → convert via `fdmatrix_to_numpy2d` → numpy 2D (n-1, m). No PyDict.

---

## Section 5: Transposition Handling

[VERIFIED: src/convert.rs:25-42]

The conversion function `numpy2d_to_fdmatrix` (line 29):
```rust
pub fn numpy2d_to_fdmatrix(arr: PyReadonlyArray2<'_, f64>) -> PyResult<FdMatrix> {
    let (nrows, ncols) = arr.as_array().dim();
    let arr_ref = arr.as_array();
    let mut col_major = vec![0.0; nrows * ncols];
    for i in 0..nrows {
        for j in 0..ncols {
            col_major[i + j * nrows] = arr_ref[[i, j]];
        }
    }
    FdMatrix::from_column_major(col_major, nrows, ncols).map_err(to_pyerr)
}
```
This converts numpy row-major (n_obs, n_points) → FdMatrix column-major (nrows=n_obs, ncols=n_points). Every fts function receives `data` as `&FdMatrix` where rows=time steps, cols=grid points — this matches the numpy convention (observation in a row). The conversion is already correct for all fts functions.

**All functions taking 2D data**: `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr`, `functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance`, `spectral_density`, `dpca`, `dpca_reconstruct`.

**Non-square fixture requirement**: use `n_obs=40, n_points=25` (confirmed non-square; square `n_obs=n_points` hides row/col swap bugs). A square fixture would pass even with transposed data for symmetric functions.

**Analog**: `conformal_mod.rs:42` and `regression_mod.rs:31` show the canonical pattern:
```rust
let mat = numpy2d_to_fdmatrix(data)?;  // all 2D inputs go through here
```

---

## Section 6: FtsmResult / DpcaResult Opaque-Handle Design (CRITICAL)

`ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, and `dpca_reconstruct` all take a Rust struct reference (`&FtsmResult` or `&DpcaResult`) as their primary input. Python cannot pass a Rust struct — the planner must choose an architecture.

### Recommended Architecture: Combined Python Functions

For `ftsm_forecast` and `ftsm_forecast_multistep`:
- Python function `ftsm_forecast(data, argvals, h=1, ncomp=3)` — calls Rust `ftsm` first, then `ftsm_forecast` (or `ftsm_forecast_multistep`), returns `FtsmForecastResult` dict.
- This is the simplest approach and matches the "thin wrapper" contract.
- Users wanting to forecast at multiple horizons call `ftsm_forecast_multistep` directly with a larger `h`.

For `ftsm_update`:
- Python function `ftsm_update(data, new_curve, argvals, ncomp=3)` — calls `ftsm` on `data` first, then `ftsm_update` with the new curve, returns updated `FtsmResult` dict.
- Note: `ftsm_update` freezes the mean/rotation from the original fit and only re-fits AR models. The binding correctly reflects this by doing a full `ftsm` fit on `data` before the update call.

For `dpca_reconstruct`:
- Python function `dpca_reconstruct(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)` — calls `dpca` first (getting a `DpcaResult`), then `dpca_reconstruct`, returns a merged dict with all fields from both structs.
- Users who need just the DPCA filters/scores without reconstruction use `dpca`.

**Alternative considered**: `#[pyclass]` opaque handle (like `PyIrregFdata` in `pace_fpca_mod.rs`). This is the right approach when the struct must be passed back to multiple separate functions. However, for Phase 67 the combined-function approach is simpler and preserves the "thin wrapper" contract. The opaque-handle approach would be appropriate only if the plan-checker or CONTEXT.md required it — they do not.

---

## Section 7: argvals Convention

[VERIFIED: src/convert.rs:8-23] — `default_grid` function:
```rust
pub fn default_grid(argvals: Option<PyReadonlyArray1<'_, f64>>, m: usize) -> Vec<f64> {
    match argvals {
        Some(a) => numpy1d_to_vec(a),
        None => (0..m).map(|i| i as f64 / (m - 1) as f64).collect(),  // uniform [0,1]
    }
}
```

For fts functions, `argvals` is **required** (not optional) at the Rust level — upstream validates `argvals.len() != m` and returns `InvalidDimension`. **Do not use `default_grid`** — accept `argvals: PyReadonlyArray1<'py, f64>` as a required parameter in all fts bindings (same as `regression_mod.rs:28`).

The binding signature pattern from `regression_mod.rs:24-28`:
```rust
#[pyo3(signature = (data, argvals, n_comp=3))]
pub fn fpca<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
```
Apply this pattern to all fts functions: `argvals` is a required positional parameter. Exceptions: `functional_difference` has no argvals at all (Rust signature takes only `&FdMatrix`).

---

## Section 8: Registration Mechanics

### `src/lib.rs` — two edits required [VERIFIED: src/lib.rs:1-65]

**Edit 1** — add module declaration after line 30 (after `mod tolerance_mod;`):
```rust
mod fts_mod;
```

**Edit 2** — add submodule registration after line 62 (after `pace_fpca` line):
```rust
register_submodule!(m, "fts", fts_mod::register);
```

The `register_submodule!` macro pattern [VERIFIED: lib.rs:32-38]:
```rust
macro_rules! register_submodule {
    ($parent:expr, $name:expr, $register_fn:path) => {{
        let sub = pyo3::types::PyModule::new($parent.py(), $name)?;
        $register_fn(&sub)?;
        $parent.add_submodule(&sub)?;
    }};
}
```

### `python/fdars/__init__.py` — one edit required [VERIFIED: __init__.py:34-55]

Add `"fts"` to `_submodule_names` tuple after `"pace_fpca"` (line 54):
```python
_submodule_names = (
    ...
    "pace_fpca",  # Phase 38
    "fts",        # Phase 67 — Functional Time Series
)
```

Also update the module docstring (line 1-22) to add a `"Functional time series (FTS model, ACF, stationarity, DPCA)"` bullet.

---

## Section 9: Module Template — `src/fts_mod.rs`

Based on the canonical pattern from `regression_mod.rs` (simplest PyDict-returning module) and `conformal_mod.rs` (seed pattern):

```rust
//! Functional time series bindings.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// Group A: Forecasting functions (ftsm, ftsm_forecast, etc.)
// Group B: Diagnostics (functional_acf, functional_pacf, etc.)
// Group C: Spectral (spectral_density, dpca, dpca_reconstruct)

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ftsm, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_forecast, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_forecast_multistep, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_update, m)?)?;
    m.add_function(wrap_pyfunction!(fplsr, m)?)?;
    m.add_function(wrap_pyfunction!(spectral_density, m)?)?;
    m.add_function(wrap_pyfunction!(dpca, m)?)?;
    m.add_function(wrap_pyfunction!(dpca_reconstruct, m)?)?;
    m.add_function(wrap_pyfunction!(functional_acf, m)?)?;
    m.add_function(wrap_pyfunction!(functional_pacf, m)?)?;
    m.add_function(wrap_pyfunction!(functional_difference, m)?)?;
    m.add_function(wrap_pyfunction!(stationarity_test, m)?)?;
    m.add_function(wrap_pyfunction!(long_run_covariance, m)?)?;
    Ok(())
}
```

---

## Section 10: PyDict Conversion Helpers Needed

The following conversions do not yet exist in `convert.rs` and must be handled inline in `fts_mod.rs`:

**1. `Vec<ArModelResult>` → Python list of dicts** (for `FtsmResult.ar_models`):
```rust
// Inline in ftsm PyDict builder:
let py_ar_list = PyList::empty(py);
for ar in &result.ar_models {
    let ar_dict = PyDict::new(py);
    ar_dict.set_item("order", ar.order)?;
    ar_dict.set_item("phi", vec_to_numpy1d(py, ar.phi.clone()))?;
    ar_dict.set_item("sigma2", ar.sigma2)?;
    py_ar_list.append(ar_dict)?;
}
dict.set_item("ar_models", py_ar_list)?;
```

**2. `Vec<f64>` flat column-major m×m → numpy 2D (m, m)** (for `LongRunCovResult.cov_matrix`):
```rust
// Must reshape flat Vec<f64> (column-major) to (m, m) row-major numpy:
// Option: use PyArray2::from_vec2 with explicit reordering, or call fdmatrix_to_numpy2d
// with FdMatrix::from_column_major(cov_matrix, m, m)
let fd_cov = fdars_core::matrix::FdMatrix::from_column_major(result.cov_matrix, result.m, result.m)
    .map_err(to_pyerr)?;
dict.set_item("cov_matrix", fdmatrix_to_numpy2d(py, &fd_cov))?;
```

**3. `Vec<Vec<f64>>` re/im at each frequency → 3D numpy (N, m, m)** (for `SpectralDensityResult`):
The flat column-major inner Vec must be reshaped to (m, m) for each frequency, then stacked to (N, m, m). Recommended implementation:
```rust
// Per frequency k: re[k] is flat col-major m×m → convert to row-major → stack
// Simplest: build a Vec of Vec<Vec<f64>> and use PyArray3 (if available)
// OR: collect each as numpy 2D and put into a Python list (simpler, less numpy)
let m = result.m;
let re_list = PyList::empty(py);
for freq_re in &result.re {
    let fd_re = fdars_core::matrix::FdMatrix::from_column_major(freq_re.clone(), m, m)
        .map_err(to_pyerr)?;
    re_list.append(fdmatrix_to_numpy2d(py, &fd_re))?;
}
// Repeat for im
```
This yields Python lists of (m, m) arrays. Users can `np.stack(result["re"])` to get (N, m, m).

**4. `Vec<FdMatrix>` → Python list of numpy 2D** (for `DpcaResult.filters`):
```rust
let filters_list = PyList::empty(py);
for f in &result.filters {
    filters_list.append(fdmatrix_to_numpy2d(py, f))?;
}
dict.set_item("filters", filters_list)?;
```

**5. `Vec<Vec<f64>>` eigenvalue trajectories → Python list of numpy 1D** (for `DpcaResult.eigenvalues`):
```rust
let ev_list = PyList::empty(py);
for ev in result.eigenvalues {
    ev_list.append(vec_to_numpy1d(py, ev))?;
}
dict.set_item("eigenvalues", ev_list)?;
```

**6. `(usize, usize)` tuple → Python tuple** (for `DpcaResult.valid_range` and `DpcaReconstruction.valid_range`):
```rust
dict.set_item("valid_range", (result.valid_range.0, result.valid_range.1))?;
```

**7. `Vec<u32>` lags → numpy int array** (for `FacfResult.lags`):
```rust
// u32 → cast to i64 for consistency with usize_vec_to_numpy1d pattern
use numpy::PyArray1;
let lags_i64: Vec<i64> = result.lags.into_iter().map(|v| v as i64).collect();
dict.set_item("lags", PyArray1::from_vec(py, lags_i64))?;
```

---

## Section 11: Complete PyDict Key Tables (for planner task actions)

### `ftsm` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"mean"` | numpy 1D | (m,) | `result.mean` |
| `"rotation"` | numpy 2D | (m, ncomp) | `result.rotation` |
| `"scores"` | numpy 2D | (n, ncomp) | `result.scores` |
| `"fitted"` | numpy 2D | (n, m) | `result.fitted` |
| `"weights"` | numpy 1D | (m,) | `result.weights` |
| `"ncomp"` | int | scalar | `result.ncomp` |
| `"ar_models"` | list of dict | len=ncomp | `result.ar_models` each with `"order"`, `"phi"`, `"sigma2"` |

### `ftsm_forecast` / `ftsm_forecast_multistep` return:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"forecast"` | numpy 2D | (h, m) | `result.forecast` |
| `"h"` | int | scalar | `result.h` |

### `ftsm_update` returns:
Same as `ftsm` (returns an updated `FtsmResult`).

### `fplsr` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"forecast"` | numpy 2D | (1, m) | `result.forecast` |
| `"fitted"` | numpy 2D | (n-1, m) | `result.fitted` |
| `"ncomp"` | int | scalar | `result.ncomp` |

### `functional_acf` / `functional_pacf` return:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"lags"` | numpy 1D int | (max_lag,) | `result.lags` (Vec<u32>) |
| `"acf"` | numpy 1D | (max_lag,) | `result.acf` |
| `"pacf"` | numpy 1D | (max_lag,) | `result.pacf` |
| `"upper_band"` | numpy 1D | (max_lag,) | `result.upper_band` |

### `functional_difference` returns:
numpy 2D of shape (n-1, m) — **no PyDict**.

### `stationarity_test` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"statistic"` | float | scalar | `result.statistic` |
| `"p_value"` | float | scalar | `result.p_value` |
| `"n_perm"` | int | scalar | `result.n_perm` |

### `long_run_covariance` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"cov_matrix"` | numpy 2D | (m, m) | `result.cov_matrix` reshaped from flat col-major |
| `"m"` | int | scalar | `result.m` |
| `"bandwidth"` | int | scalar | `result.bandwidth` |
| `"n_curves"` | int | scalar | `result.n_curves` |

### `spectral_density` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"freqs"` | numpy 1D | (N,) | `result.freqs` |
| `"re"` | list of numpy 2D | N × (m, m) | `result.re`, each inner Vec reshaped |
| `"im"` | list of numpy 2D | N × (m, m) | `result.im`, each inner Vec reshaped |
| `"m"` | int | scalar | `result.m` |
| `"n_curves"` | int | scalar | `result.n_curves` |
| `"bandwidth"` | int | scalar | `result.bandwidth` |

### `dpca` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"filters"` | list of numpy 2D | ncomp × (2L+1, m) | `result.filters` |
| `"scores"` | numpy 2D | (N-2L, ncomp) | `result.scores` |
| `"eigenvalues"` | list of numpy 1D | ncomp × (N,) | `result.eigenvalues` |
| `"n_freqs"` | int | scalar | `result.n_freqs` |
| `"filter_lag"` | int | scalar | `result.filter_lag` |
| `"ncomp"` | int | scalar | `result.ncomp` |
| `"valid_range"` | tuple (int, int) | — | `result.valid_range` |

### `dpca_reconstruct` returns (merged dict from DpcaResult + DpcaReconstruction):
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| All keys from `dpca` above | — | — | `DpcaResult` |
| `"fitted_reconstruction"` | numpy 2D | (N-2L, m) | `DpcaReconstruction.fitted` |
| `"reconstruction_error"` | numpy 1D | (ncomp,) | `DpcaReconstruction.reconstruction_error` |
| (valid_range from DpcaReconstruction matches DpcaResult — use one) | — | — | — |

Note: use key `"fitted_reconstruction"` for `DpcaReconstruction.fitted` to avoid collision with the `DpcaResult` dict which has no `"fitted"` key, but naming clarity matters — alternatively name it `"fitted"` since `DpcaResult` does not have a `"fitted"` field.

---

## Section 12: Test Architecture

### Non-square fixture (REQUIRED by STATE.md and CONTEXT.md)
```python
import numpy as np
import fdars.fts as fts

N, M = 40, 25   # N observations, M grid points — deliberately non-square
assert N != M    # Guard: square fixtures hide row/col swap bugs

rng = np.random.default_rng(42)
argvals = np.linspace(0.0, 1.0, M)

# AR(1)-driven functional data for meaningful FTS tests
def make_ar1_curves(n, m, phi=0.7, seed=0):
    rng2 = np.random.default_rng(seed)
    f1 = np.sin(np.pi * argvals)
    eps = rng2.standard_normal((n, m)) * 0.2
    scores = np.zeros(n)
    scores[0] = rng2.standard_normal()
    for t in range(1, n):
        scores[t] = phi * scores[t-1] + rng2.standard_normal()
    return scores[:, None] * f1[None, :] + eps

data = make_ar1_curves(N, M)
assert data.shape == (N, M)   # (40, 25) — non-square
```

### Shape assertions (transposition guard):
```python
# ftsm
r = fts.ftsm(data, argvals, ncomp=3)
assert r["mean"].shape == (M,)        # (25,) — grid dimension
assert r["rotation"].shape == (M, 3)  # (25, 3)
assert r["scores"].shape == (N, 3)    # (40, 3) — n_obs
assert r["fitted"].shape == (N, M)    # (40, 25)
assert len(r["ar_models"]) == 3
assert set(r["ar_models"][0].keys()) == {"order", "phi", "sigma2"}
```

### Minimum test coverage required:
1. **Import smoke** — `import fdars.fts as fts; from fdars.fts import ftsm, functional_acf`
2. **ftsm end-to-end + shape assertions** — non-square fixture, verify all PyDict keys + shapes
3. **ftsm_forecast / ftsm_forecast_multistep** — h=1 and h=3; verify (h, M) shape; verify h=1 gives identical output from both functions
4. **ftsm_update** — update with 1 new curve; verify scores extend by 1 row
5. **fplsr** — non-square fixture; verify (1, M) forecast shape and (N-1, M) fitted shape
6. **functional_acf determinism** — same seed → bit-identical result
7. **functional_pacf** — delegates to functional_acf; shapes match
8. **functional_difference** — output shape (N-1, M); round-trip via cumsum within 1e-10
9. **stationarity_test determinism** — same seed → same p_value
10. **long_run_covariance** — cov_matrix shape (M, M); symmetric within 1e-10; bandwidth=None uses default
11. **spectral_density** — shapes: freqs (N,), re list of N arrays each (M, M), n_curves=N
12. **dpca** — scores shape (N-2L, ncomp); filters list length ncomp; valid_range tuple
13. **dpca_reconstruct** — reconstruction_error monotone non-increasing; fitted shape (N-2L, M)
14. **Error guard** — stationarity_test with n_perm=0 raises ValueError; functional_acf with n_sim=0 raises ValueError; ftsm with ncomp=0 raises ValueError

---

## Section 13: `u32` Lags Conversion Note

`FacfResult.lags` is `Vec<u32>`, not `Vec<usize>`. The existing `usize_vec_to_numpy1d` in `convert.rs` returns `i64` via a cast. For `Vec<u32>`, use:
```rust
let lags_i64: Vec<i64> = result.lags.into_iter().map(|v| v as i64).collect();
dict.set_item("lags", PyArray1::from_vec(py, lags_i64))?;
```
Alternatively cast to `u32` numpy array — but `i64` is consistent with the `usize_vec_to_numpy1d` pattern.

---

## Standard Stack

No new dependencies. Phase 67 uses exclusively:
- `fdars-core 0.33.0` (already in `Cargo.toml` at `parallel` feature)
- `pyo3 0.28` (already in `Cargo.toml`)
- `numpy 0.28` (already in `Cargo.toml`)
- `convert.rs` utilities (project-local)

No packages to install. No package legitimacy audit required.

---

## Architecture Patterns

### Recommended Project Structure Addition
```
src/
├── fts_mod.rs       # NEW — all 13 fts bindings (Group A: forecast, Group B: acf, Group C: spectral)
├── lib.rs           # EDIT — add mod fts_mod; + register_submodule!(m, "fts", fts_mod::register);
├── convert.rs       # NO CHANGE — existing helpers sufficient
```

### Pattern: Thin PyFunction with argvals required
```rust
// Source: regression_mod.rs:24-45 (canonical 2D-input + argvals + PyDict return)
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3))]
pub fn ftsm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::ftsm(&mat, ncomp, &av))?;
    // ... build PyDict ...
}
```

### Pattern: Seed default = 42 (from conformal_mod.rs)
```rust
// Source: conformal_mod.rs:31
#[pyo3(signature = (data, response, test_data, ncomp=3, cal_fraction=0.25, alpha=0.1, seed=42))]
```

Apply to: `functional_acf`, `functional_pacf`, `stationarity_test`.

### Anti-Patterns to Avoid
- **Accepting `Option<Vec<f64>>` for argvals and defaulting to linspace**: fts functions validate `argvals.len() != m` and raise `InvalidDimension` if mismatch. Argvals must be explicit.
- **Passing a Python dict back into forecast functions**: `ftsm_forecast` requires `&FtsmResult`, not a Python dict. Use combined function (re-run `ftsm`) rather than trying to deserialize a dict to Rust struct.
- **Assuming `functional_pacf` returns only pacf**: both `functional_acf` and `functional_pacf` return the full `FacfResult` with acf, pacf, upper_band, and lags all populated.
- **Using a square fixture (e.g., 20×20)**: hides row-major↔column-major bugs. Always use N ≠ M.

---

## Common Pitfalls

### Pitfall 1: `&FtsmResult` / `&DpcaResult` Parameter
**What goes wrong:** Binding `ftsm_forecast` or `dpca_reconstruct` directly as a Python function that accepts a dict — Rust cannot deserialize a PyDict to a struct.
**Why it happens:** The upstream API is designed for Rust-to-Rust call chains.
**How to avoid:** Use the combined-function pattern: refit inside the binding. For `ftsm_forecast`, call `fdars_core::fts::ftsm(&mat, ncomp, &av)?` first, then immediately call `fdars_core::fts::ftsm_forecast(&fit, h, &av)?`.
**Warning signs:** Compiler error "cannot convert PyDict to FtsmResult".

### Pitfall 2: Column-major cov_matrix not reshaped
**What goes wrong:** `LongRunCovResult.cov_matrix` is a flat `Vec<f64>` in column-major order. If exposed directly as a 1D numpy array (shape m²) or reshaped row-by-row without the column-major→row-major transposition, the matrix will be transposed.
**How to avoid:** Use `FdMatrix::from_column_major(cov_matrix, m, m)` then `fdmatrix_to_numpy2d`, which correctly transposes to row-major.

### Pitfall 3: spectral_density bandwidth=Some(0) rejected
**What goes wrong:** Unlike `long_run_covariance` which accepts `bandwidth=Some(0)` and returns C_0, `spectral_density` rejects `bandwidth=Some(0)` with `InvalidParameter`.
**How to avoid:** In Python docs, note that `bandwidth=None` (auto) is safe; `bandwidth=0` raises ValueError. Do not expose `bandwidth=0` as a "get C_0" shortcut for spectral_density.

### Pitfall 4: `u32` lags type in FacfResult
**What goes wrong:** `FacfResult.lags` is `Vec<u32>` — passing to `vec_to_numpy1d` (which expects `Vec<f64>`) will fail to compile.
**How to avoid:** Cast explicitly: `result.lags.into_iter().map(|v| v as i64).collect::<Vec<i64>>()`.

### Pitfall 5: fplsr requires n ≥ 3
**What goes wrong:** `fplsr` needs at least 3 rows (2 lag-1 training pairs + 1 forecast origin). A test with n=2 will get `InvalidParameter`.
**How to avoid:** Use n ≥ 10 in all fplsr tests.

### Pitfall 6: dpca filter_lag default
**What goes wrong:** `dpca` with `filter_lag=None` uses the resolved bandwidth (typically `⌊N^{1/3}⌋`). For N=40, default bandwidth is `⌊3.4⌋ = 3`, so filter_lag=3, yielding scores shape `(40 - 6, ncomp) = (34, ncomp)`. Tests must compute the expected interior rows: `N - 2*filter_lag`.
**How to avoid:** Always assert `result["scores"].shape == (N - 2 * result["filter_lag"], ncomp)` rather than hard-coding the interior row count.

---

## Assumptions Log

> All claims in this research were verified by reading the source files this session. The Assumptions Log is empty.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | — | — | — |

**All claims verified by reading fdars-core 0.33.0 registry source and pyfda project files this session. No `[ASSUMED]` tags in this document.**

---

## Open Questions

None. The fts API surface is fully documented in the 0.33 source, the project conventions are established, and the registration mechanics are clear from existing modules.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 67 is a code-only change (new Rust source file + two registration edits + new test file). No new external dependencies. The build environment (maturin + Rust 1.83+ + cargo) was confirmed working by Phase 66 (crate bump + regression gate passed).

---

## Validation Architecture

`workflow.nyquist_validation` is `false` in `.planning/config.json`. Section skipped per config.

---

## Security Domain

Phase 67 adds no networked components, no authentication, no cryptography, no external service calls. All computations are pure numerical Rust, called synchronously from Python. ASVS categories V2-V6 do not apply. Input validation (V5) is handled by fdars-core's own guards (returning `FdarError::InvalidDimension` / `InvalidParameter`), which are propagated to Python as `ValueError` via `to_pyresult`.

---

## Sources

### Primary (HIGH confidence — read directly from source files this session)
- `fdars-core-0.33.0/src/fts/mod.rs` — all 10 result struct definitions (lines 46–237)
- `fdars-core-0.33.0/src/fts/forecast.rs` — `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr` signatures and implementations
- `fdars-core-0.33.0/src/fts/acf.rs` — `functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance` signatures and implementations
- `fdars-core-0.33.0/src/fts/spectral.rs` — `spectral_density`, `dpca`, `dpca_reconstruct` signatures and implementations
- `src/convert.rs` — `numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `vec_to_numpy1d`, `numpy1d_to_vec`, `to_pyresult`, `default_grid`
- `src/lib.rs` — `register_submodule!` macro and registration pattern (lines 32–65)
- `python/fdars/__init__.py` — `_submodule_names` list and registration loop (lines 34–90)
- `src/pace_fpca_mod.rs` — `#[pyclass]` opaque handle pattern and PyDict conversion pattern
- `src/regression_mod.rs` — canonical 2D-input + argvals + PyDict return pattern (lines 1–46)
- `src/conformal_mod.rs` — seed=42 default pattern

### Secondary (for context)
- `.planning/phases/67-functional-time-series-fts/67-CONTEXT.md` — locked decisions
- `.planning/REQUIREMENTS.md` — FTS-01, FTS-02, FTS-03
- `.planning/STATE.md` — blockers and concerns

---

## Metadata

**Confidence breakdown:**
- Function signatures: HIGH — read verbatim from 0.33 registry source this session
- Struct field names: HIGH — read verbatim from 0.33 `fts/mod.rs` this session; this was the key risk flagged in STATE.md, now resolved
- Registration mechanics: HIGH — read from `src/lib.rs` and `python/fdars/__init__.py` this session
- Conversion helpers: HIGH — read from `src/convert.rs` and analog modules this session
- Architecture (combined-function approach): MEDIUM — pattern not yet implemented in project; but is the simplest viable approach given no opaque handle requirement in CONTEXT.md

**Research date:** 2026-09-02
**Valid until:** 2026-12-01 (fdars-core stable; only invalid if crate version bumps again)
