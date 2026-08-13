# Stack Research

**Domain:** PyO3 Rust-to-Python binding layer — fdars-core 0.14.0 → 0.17.0 upgrade
**Researched:** 2026-08-13
**Confidence:** HIGH (all signatures verified against docs.rs/fdars-core/0.17.0; Cargo caret semantics and lock behaviour verified against local Cargo.lock)

---

## Decision Summary

The upgrade is a single-line Cargo.toml change. No new Rust dependencies are required, no PyO3/numpy crate version changes are needed, and no Python packaging extras need adding. The `linalg` feature is opt-in and should NOT be enabled in this milestone (see rationale). The binding implementation uses the existing `convert.rs` layer without any modification.

---

## 1. Cargo.toml Change — Exact Line

**Current (`Cargo.toml` line 18):**
```toml
fdars-core = { version = "0.14.0", features = ["parallel"] }
```

**Required change:**
```toml
fdars-core = { version = "0.17.0", features = ["parallel"] }
```

### Caret semantics — why an explicit bump is required

Cargo's default caret requirement `"0.14.0"` is equivalent to `^0.14.0`, which resolves to `>=0.14.0, <0.15.0`. The current `Cargo.lock` records `version = "0.14.0" checksum = "93dab17c..."`. This means Cargo will never resolve 0.15.0 or later unless the version string is changed. Writing `"0.17.0"` shifts the ceiling to `<0.18.0`, allowing Cargo to pick 0.17.x. After the change, run `cargo update` (or `maturin develop`) to regenerate `Cargo.lock` — the existing checksum entry will be replaced by the 0.17.0 checksum. Commit the updated `Cargo.lock`.

### The `parallel` feature — keep it

The `parallel` feature enables rayon-based parallelism throughout fdars-core and has been the only enabled feature since the project started. In 0.17.0 it additionally covers parallel CV folds, parallel elastic-FPCA (vert/horiz/joint), and the banded elastic distance parallelism introduced in 0.16.0. There is no reason to remove it.

### The `linalg` feature — do NOT enable

The `linalg` feature gates `faer` + `anofox-regression` (faster SVD for FPCA, 1.8–4.1x speedup, plus `ridge_regression_fit`).

Do not enable it in this milestone for three reasons:

1. **MSRV conflict.** `linalg` requires Rust 1.84+. pyfda's declared MSRV is `rust-version = "1.83"` in `Cargo.toml`. Enabling `linalg` would silently break CI on any Rust 1.83 runner or force an undeclared MSRV bump — both bad outcomes.
2. **WASM incompatibility.** Upstream marks `linalg` as not WASM-compatible. pyfda does not currently ship WASM wheels, but enabling an incompatible feature without investigation is unnecessary risk.
3. **No new public API to bind.** The FPCA speedup is internal. No functions in the 0.17.0 new-API list are gated solely behind `linalg`. The performance win is inherited if `linalg` is ever added in a future milestone after an MSRV bump to 1.84.

---

## 2. MSRV, Cargo.lock, and Transitive Dependency Implications

**MSRV:** No change required. `rust-version = "1.83"` in `Cargo.toml` is compatible with fdars-core 0.17.0 + `parallel` feature only.

**Transitive dependencies (current lock):**
```
fdars-core 0.14.0 → getrandom, nalgebra, num-complex, rand, rand_distr, rayon, rustfft
```

Upstream release notes for 0.15.0 and 0.16.0 both explicitly state **"no new dependencies"** for the additive APIs being bound. The `linalg` feature would add `faer` and `anofox-regression`, but since it is not being enabled those do not appear. After bumping the version string, regenerate `Cargo.lock` and commit it; CI will validate the resolved dependency tree.

**PyO3 crate version:** No change. `pyo3 = { version = "0.28", features = ["extension-module", "abi3-py39"] }` is compatible with fdars-core 0.17.0 (fdars-core has no PyO3 dependency of its own).

**numpy crate version:** No change. `numpy = "0.28"` for zero-copy array exchange is unaffected.

**maturin build backend:** No change. `maturin>=1.0,<2.0` in `pyproject.toml` is compatible.

---

## 3. New Rust Dependencies

**None.** The upstream 0.15.0 and 0.16.0 release notes both state "no new dependencies." The new API (interpolation helpers, functional stats, scoring metrics, alignment registration) is implemented using existing transitive deps (`nalgebra`, `rayon`, `rustfft`). No new crate entries will appear in `Cargo.lock` beyond the fdars-core version number change itself.

---

## 4. New Public API — Exact Signatures

All signatures verified against `docs.rs/fdars-core/0.17.0`. `Result<T, FdarError>` indicates fallible functions whose errors must be converted via the existing `convert::to_pyresult()` helper. Functions returning a plain type are infallible.

### 4a. Interpolation & Representation — `fdars_core::helpers`

This is a new module introduced in 0.15.0–0.16.0 (`fdars_core::helpers`). All items are re-exported at the crate root. No equivalent module existed in 0.14.0.

**Enums:**

```rust
// InterpolationMethod — #[non_exhaustive]
pub enum InterpolationMethod {
    Linear,        // linear interpolation between adjacent points
    CubicHermite,  // monotone, C1-continuous cubic Hermite splines
}

// ExtrapolationPolicy — controls behavior when query point falls outside domain
pub enum ExtrapolationPolicy {
    Boundary,      // clamp to nearest boundary value (t < t_min → val at t_min)
    Exception,     // return FdarError::InvalidParameter for out-of-range queries
    Fill(f64),     // substitute this constant value for out-of-range queries
    Periodic,      // wrap query points modulo domain length (((t-t_min)%L+L)%L)
}

// ImputationMethod
pub enum ImputationMethod {
    Linear,        // linear interpolation between nearest non-NaN neighbors
    Mean,          // replace NaN with curve's mean of its non-NaN values
    Constant(f64), // replace NaN with user-supplied constant
}
```

**Functions:**

```rust
// Basic resampling — INFALLIBLE (boundary-clamps by default)
pub fn fdata_interpolate(
    data: &FdMatrix,
    argvals: &[f64],      // original grid, length m, sorted
    new_argvals: &[f64],  // target grid, length m_new, sorted, within original domain
    method: InterpolationMethod,
) -> FdMatrix             // shape (n, m_new)

// Resampling with explicit extrapolation control — FALLIBLE
pub fn fdata_interpolate_with_policy(
    data: &FdMatrix,
    argvals: &[f64],
    new_argvals: &[f64],
    method: InterpolationMethod,
    policy: ExtrapolationPolicy,
) -> Result<FdMatrix, FdarError>

// B-spline fit-per-curve + evaluate at arbitrary query points — FALLIBLE
pub fn spline_interpolate(
    data: &FdMatrix,
    argvals: &[f64],
    query_points: &[f64],
    order: usize,           // spline order: 1=linear, 4=cubic; must be in [1, m)
) -> Result<FdMatrix, FdarError>

// B-spline with explicit extrapolation control — FALLIBLE
pub fn spline_interpolate_with_policy(
    data: &FdMatrix,
    argvals: &[f64],
    query_points: &[f64],
    order: usize,
    policy: ExtrapolationPolicy,
) -> Result<FdMatrix, FdarError>

// NaN gap-filling — FALLIBLE
// Error: InvalidDimension if argvals.len() != data.ncols();
//        InvalidParameter if an entire curve is NaN
pub fn impute_missing_values(
    data: &FdMatrix,
    argvals: &[f64],        // sorted, matches data column count
    method: ImputationMethod,
) -> Result<FdMatrix, FdarError>
```

**PyO3 binding notes for interpolation group:**
- All `FdMatrix` I/O uses existing `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d` — no new converter needed.
- `InterpolationMethod` and `ExtrapolationPolicy` should be accepted as `&str` from Python and matched to enum variants in the wrapper, following the same pattern as `NormalizationMethod` in `fdata_mod.rs`.
- `ExtrapolationPolicy::Fill(f64)` and `ImputationMethod::Constant(f64)` require an extra `f64` parameter (e.g. `fill_value: f64 = 0.0`) with a `#[pyo3(signature = (...))]` default when not applicable.
- `fdata_interpolate` is infallible — the wrapper returns `Bound<'py, PyArray2<f64>>` directly, no `PyResult` wrapping.
- All `Result`-returning functions use `to_pyresult(fdars_core::helpers::xyz(...))`.
- **Target module:** New `src/helpers_mod.rs`; register as `"helpers"` submodule in `src/lib.rs`.

### 4b. Functional Statistics — `fdars_core::fdata`

These extend the existing `fdata` module. Add to `src/fdata_mod.rs` and include in its `register()` function.

```rust
// Pointwise sample variance (Bessel-corrected, ddof = n-1) — FALLIBLE
// Error: InvalidDimension if n < 2
pub fn functional_variance(data: &FdMatrix) -> Result<Vec<f64>, FdarError>

// Pointwise sample std dev (ddof = n-1) — FALLIBLE
// Error: InvalidDimension if n < 2
pub fn functional_std(data: &FdMatrix) -> Result<Vec<f64>, FdarError>

// M×M sample covariance matrix (Bessel-corrected) — FALLIBLE
// Error: InvalidDimension if n < 2; InvalidParameter if m² overflows
pub fn functional_covariance(data: &FdMatrix) -> Result<FdMatrix, FdarError>

// Index of deepest curve under Fraiman-Muniz depth — FALLIBLE
// Error: InvalidDimension if n < 1
pub fn depth_based_median(data: &FdMatrix) -> Result<usize, FdarError>

// Depth-trimmed mean — FALLIBLE
// Error: if alpha outside [0,1) or data has zero rows
pub fn trim_mean(data: &FdMatrix, alpha: f64) -> Result<Vec<f64>, FdarError>
```

**PyO3 binding notes for functional stats group:**
- `functional_variance` → `PyResult<Bound<'py, PyArray1<f64>>>` via `vec_to_numpy1d`.
- `functional_std` → same.
- `functional_covariance` → `PyResult<Bound<'py, PyArray2<f64>>>` via `fdmatrix_to_numpy2d`.
- `depth_based_median` → `PyResult<usize>`. PyO3 converts `usize` to Python `int` natively; no array helper needed. Document in the Python docstring that this is a 0-based row index into the data matrix, not a curve value.
- `trim_mean` → `PyResult<Bound<'py, PyArray1<f64>>>` with `alpha: f64` parameter.
- All five use `to_pyresult(fdars_core::fdata::xyz(...))`.

### 4c. Scoring Metrics — `fdars_core::scoring`

New `scoring` module (did not exist in 0.14.0). Create `src/scoring_mod.rs` and register as `"scoring"` submodule in `src/lib.rs`.

```rust
// All five take (y_true, y_pred, argvals) — FALLIBLE
// Return scalar f64 (Simpson-integrated over argvals domain)
// Error: InvalidDimension if shapes of y_true, y_pred, argvals are inconsistent,
//        or n < 1, or m < 2

pub fn functional_mae(
    y_true: &FdMatrix,
    y_pred: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>

pub fn functional_mse(
    y_true: &FdMatrix,
    y_pred: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>

pub fn functional_mape(
    y_true: &FdMatrix,
    y_pred: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>

pub fn functional_msle(
    y_true: &FdMatrix,
    y_pred: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>

pub fn functional_explained_variance(
    y_true: &FdMatrix,
    y_pred: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>
```

**IMPORTANT name correction:** The crate-level name is `functional_explained_variance`, not `explained_variance`. The milestone context used `explained_variance` as a shorthand; use the exact upstream identifier when writing the binding and the Python-side name.

**PyO3 binding notes for scoring group:**
- Both `y_true` and `y_pred` are `PyReadonlyArray2<'py, f64>`, each converted via `numpy2d_to_fdmatrix`.
- `argvals` is `PyReadonlyArray1<'py, f64>`, converted via `numpy1d_to_vec`, passed as `&[f64]` via `.as_slice()` / reference to the owned `Vec`.
- Return type for all five: `PyResult<f64>` — no array wrapping.
- All five use `to_pyresult(fdars_core::scoring::xyz(...))`.
- These pure scoring functions have no state and are natural candidates for the advisor's `build_diagnostics` pipeline.

### 4d. Alignment / Registration — `fdars_core::alignment`

These extend the existing `alignment_mod.rs`. No new file needed.

#### Shift registration

```rust
// Struct (non_exhaustive) — access fields by name, never by destructuring pattern
pub struct ShiftRegistrationResult {
    pub registered_data: FdMatrix,  // aligned curves, same shape as input (n × m)
    pub shifts: Vec<f64>,           // per-curve horizontal shifts δᵢ, length n
                                    // positive = rightward shift, negative = leftward
}

// FALLIBLE — rigid horizontal shift registration via golden-section search
// Error: various InvalidDimension/InvalidParameter conditions
pub fn least_squares_shift_registration(
    data: &FdMatrix,
    argvals: &[f64],  // sorted ascending
    max_shift: f64,   // half-width of shift search interval, must be > 0
) -> Result<ShiftRegistrationResult, FdarError>
```

**PyO3 binding note:** Destructure `ShiftRegistrationResult` into a `PyDict` with keys `"registered_data"` (via `fdmatrix_to_numpy2d`) and `"shifts"` (via `vec_to_numpy1d`). The struct is `#[non_exhaustive]` — field access by name is stable; pattern destructuring is not.

#### Registration quality scores

```rust
// Mean Simpson-weighted L2 spread of registered curves — FALLIBLE
pub fn least_squares_score(
    registered: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>

// Mean pairwise Pearson correlation over all n(n-1)/2 curve pairs — FALLIBLE
// Requires n >= 2
pub fn pairwise_correlation_score(
    registered: &FdMatrix,
    argvals: &[f64],
) -> Result<f64, FdarError>

// LS spread + derivative-penalty term weighted by lambda — FALLIBLE
pub fn sobolev_least_squares_score(
    registered: &FdMatrix,
    argvals: &[f64],
    lambda: f64,    // non-negative weight for derivative penalty
) -> Result<f64, FdarError>
```

**PyO3 binding notes:** All three return `PyResult<f64>`. `registered` is `PyReadonlyArray2<'py, f64>` via `numpy2d_to_fdmatrix`.

#### Banded elastic alignment

```rust
// Karcher mean with optional Sakoe-Chiba band — INFALLIBLE
// Returns same KarcherMeanResult as existing karcher_mean
pub fn karcher_mean_with_band(
    data: &FdMatrix,
    argvals: &[f64],
    max_iter: usize,
    tol: f64,
    lambda: f64,
    band_frac: Option<f64>,  // None = exact DP; Some(0.2) = 20% band, 4-6× faster
) -> KarcherMeanResult

// Banded elastic self distance matrix — INFALLIBLE
pub fn elastic_self_distance_matrix_with_band(
    data: &FdMatrix,
    argvals: &[f64],
    lambda: f64,
    band_frac: Option<f64>,
) -> FdMatrix

// Banded elastic cross distance matrix — INFALLIBLE
pub fn elastic_cross_distance_matrix_with_band(
    data1: &FdMatrix,
    data2: &FdMatrix,
    argvals: &[f64],
    lambda: f64,
    band_frac: Option<f64>,
) -> FdMatrix
```

**PyO3 binding notes for banded group:**
- `band_frac: Option<f64>` — expose from Python as `band_frac: Option<f64>` with `#[pyo3(signature = (..., band_frac=None))]`. PyO3 0.28 handles `Option<f64>` natively; Python callers pass `None` or a float.
- `karcher_mean_with_band` returns `KarcherMeanResult` — use the same dict decomposition as the existing `karcher_mean` binding (keys: `mean`, `mean_srsf`, `aligned_data`, `gammas`, `n_iter`, `converged`).
- Both distance-matrix variants are infallible — return `Bound<'py, PyArray2<f64>>` directly via `fdmatrix_to_numpy2d`.
- `band_frac=None` falls back to the exact (unbanded) DP; `band_frac=Some(0.2)` restricts to 20% of grid length and runs 4–6× faster with minor approximation error.

---

## 5. Python Packaging Extras — No Changes Required

All new API is pure Rust computation. No new Python runtime dependencies are introduced.

- Interpolation helpers, functional stats, scoring metrics → core package (no extra)
- Shift registration and banded alignment → core package (no extra)
- Advisor wiring that consumes scoring metrics remains inside the existing `[advisor]` extra boundary

The existing extras in `pyproject.toml` are unchanged:
```toml
plot      = ["matplotlib>=3.6"]
dev       = ["pytest", "matplotlib>=3.6"]
advisor   = ["anthropic>=0.72.0", "pydantic>=2.0"]
mcp       = ["mcp>=2.0.0"]
openai    = ["openai>=1.40,<2.0", "pydantic>=2.0"]
gemini    = ["google-genai>=1.0,<3.0", "pydantic>=2.0"]
ollama    = ["ollama>=0.6.2", "pydantic>=2.0"]
all-providers = [...]
```

---

## 6. Module Placement Summary

| New Content | Target Location |
|-------------|----------------|
| `fdata_interpolate`, `fdata_interpolate_with_policy`, `spline_interpolate`, `spline_interpolate_with_policy`, `impute_missing_values`, `InterpolationMethod`, `ExtrapolationPolicy`, `ImputationMethod` | New `src/helpers_mod.rs`; register as `"helpers"` in `src/lib.rs` |
| `functional_variance`, `functional_std`, `functional_covariance`, `depth_based_median`, `trim_mean` | Extend existing `src/fdata_mod.rs` |
| `functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, `functional_explained_variance` | New `src/scoring_mod.rs`; register as `"scoring"` in `src/lib.rs` |
| `least_squares_shift_registration`, `least_squares_score`, `pairwise_correlation_score`, `sobolev_least_squares_score`, `karcher_mean_with_band`, `elastic_self_distance_matrix_with_band`, `elastic_cross_distance_matrix_with_band` | Extend existing `src/alignment_mod.rs` |

---

## 7. Existing convert.rs Layer — No Changes Required

The existing `convert.rs` provides every primitive needed for the new bindings:

| Converter | Used by new bindings |
|-----------|---------------------|
| `numpy2d_to_fdmatrix` | All new FdMatrix inputs |
| `fdmatrix_to_numpy2d` | `functional_covariance`, `registered_data`, distance matrices |
| `numpy1d_to_vec` | `argvals`, `query_points`, `shifts` |
| `vec_to_numpy1d` | `functional_variance`, `functional_std`, `trim_mean`, `shifts` |
| `to_pyresult` | Every `Result<T, FdarError>` conversion |
| `to_pyerr` | Direct error wrapping where needed |

The `usize` return of `depth_based_median` converts to Python `int` natively through PyO3 — no converter needed.

---

## 8. Signature Uncertainty Flags

All core signatures are HIGH confidence (verified via docs.rs individual function pages).

| Item | Confidence | Note |
|------|------------|------|
| `fdata_interpolate` infallibility | HIGH | Docs show plain `FdMatrix` return, no `Result` wrapper |
| `karcher_mean_with_band` infallibility | HIGH | Docs show plain `KarcherMeanResult` return, same as `karcher_mean` |
| `elastic_*_with_band` infallibility | HIGH | Docs show plain `FdMatrix` return |
| `ShiftRegistrationResult` fields | HIGH | Struct page verified: `registered_data: FdMatrix`, `shifts: Vec<f64>` |
| `functional_explained_variance` exact name | HIGH | Scoring module page confirms this is the full name (not `explained_variance`) |
| `InterpolationMethod` variants | HIGH | Enum page verified: `Linear`, `CubicHermite` (#[non_exhaustive]) |
| `ExtrapolationPolicy::Fill(f64)` | HIGH | Enum page verified with all four variants |
| `linalg` MSRV = 1.84 | MEDIUM | Stated in docs summary; not verified against upstream `Cargo.toml` MSRV field directly |

---

## 9. Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| `linalg` feature MSRV bump (Rust 1.84 required) | Medium | Do not enable `linalg`; MSRV stays at 1.83 |
| `#[non_exhaustive]` on `ShiftRegistrationResult` | Low | Access fields by name in wrapper code, not via pattern destructuring |
| `InterpolationMethod` is `#[non_exhaustive]` | Low | Add `_ => Err(PyValueError::new_err(...))` arm in the match |
| `depth_based_median` returns 0-based `usize` index | Low | Document in Python docstring that the return is a row index, not a value |
| `band_frac=None` = exact DP (not a no-op) | Low | Default `band_frac=None` in pyo3 signature to preserve existing accuracy; document that Some(0.2) trades accuracy for ~5x speed |
| Column-major layout for all new FdMatrix I/O | Low | Existing `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d` handle this — unchanged from all existing bindings |
| `scoring` module path (`fdars_core::scoring::functional_explained_variance`, not `explained_variance`) | Low | Use the exact upstream name when writing the binding |

---

## Sources

- `docs.rs/fdars-core/0.17.0/fdars_core/` — module index, feature flags [HIGH — official docs]
- `docs.rs/fdars-core/0.17.0/fdars_core/fdata/fn.functional_variance.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/fdata/fn.functional_std.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/fdata/fn.functional_covariance.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/fdata/fn.depth_based_median.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/fdata/fn.trim_mean.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/index.html` — module contents [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/fn.spline_interpolate.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/fn.spline_interpolate_with_policy.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/fn.fdata_interpolate.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/fn.fdata_interpolate_with_policy.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/fn.impute_missing_values.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/enum.ImputationMethod.html` — variants verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/enum.ExtrapolationPolicy.html` — variants verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/helpers/enum.InterpolationMethod.html` — variants verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/scoring/fn.functional_mae.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/scoring/fn.functional_mse.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/scoring/fn.functional_mape.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/scoring/fn.functional_msle.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/scoring/fn.functional_explained_variance.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.least_squares_shift_registration.html` — signature + struct fields [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/struct.ShiftRegistrationResult.html` — struct definition [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.karcher_mean_with_band.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.elastic_self_distance_matrix_with_band.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.elastic_cross_distance_matrix_with_band.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.least_squares_score.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.pairwise_correlation_score.html` — signature verified [HIGH]
- `docs.rs/fdars-core/0.17.0/fdars_core/alignment/fn.sobolev_least_squares_score.html` — signature verified [HIGH]
- `github.com/sipemu/fdars/releases` — 0.15.0 and 0.16.0 release notes [MEDIUM — GitHub page]
- `/home/simonm/projects/rust/pyfda/Cargo.toml` + `Cargo.lock` — current pin and dependency tree [HIGH — local source]

---

*Stack research for: pyfda v4.0 — fdars-core 0.14.0 → 0.17.0 upgrade*
*Researched: 2026-08-13*
