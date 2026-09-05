# Phase 70: Multi-Domain Data, FAMM & Advanced Clustering — Research

**Researched:** 2026-09-03
**Domain:** PyO3 binding — fdars-core 0.33 `multi_fdata`, `famm`, `spm/mfpca`, `clustering_advanced` modules
**Confidence:** HIGH — all findings read directly from 0.33 registry source and existing project files this session

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **MULTI-03 multivariate-SPM scope:** Bind `mfpca` + `spe_multivariate` into `fdars.spm`. `mfpca`
  (spm/mfpca.rs:246) takes `variables: &[&FdMatrix]` + `MfpcaConfig`; `spe_multivariate`
  (spm/stats.rs:275) is the multivariate SPE monitoring statistic. Together = complete
  multi-domain-monitoring pair. Skip `frcc` and other multi-domain monitors (deferred).

### Claude's Discretion (convention-driven)
- **PyMultiFunData handle:** mirror `PyIrregFdata` exactly (opaque `#[pyclass]`, constructed via a
  `#[pyfunction]` builder that takes component curves from Python — a list of 2D numpy arrays plus
  a list of argvals vectors per component — routed through `numpy2d_to_fdmatrix` for each
  component). The `MultiFunData::new` constructor is the only constructor; takes
  `Vec<FdComponent>` with each `FdComponent { data: FdMatrix, argvals: Vec<f64> }`.
- **Submodule organization:** new `fdars.multi_fdata` (handle + builder) and new `fdars.famm`
  (mixed models); `fdars.spm` and `fdars.clustering` extended in place.
- **Return shape:** documented PyDicts from result structs (mfpca → MfpcaResult; famm → their result
  structs; clustering → labels/result dicts). Confirm exact 0.33 field names.
- **Transposition:** every 2D input via `numpy2d_to_fdmatrix`; multi-variable inputs as a list of 2D
  arrays; non-square (`n_obs ≠ n_points`) fixtures throughout (MULTI-04 explicitly
  transposition-guarded).
- **Enum/`#[non_exhaustive]` args:** clustering/famm/mfpca configs likely `#[non_exhaustive]` →
  `Default::default()` + field mutation; no enum dispatch here (no string-selected enum in these APIs).
- **Determinism:** `seed` default where an upstream fn takes one (dbscan/kcfc/funfem/align_cluster all
  carry `seed` in their configs; MfpcaConfig does not).
- **Error handling:** `FdarError` → `PyValueError` via `convert::to_pyresult`.

### Deferred Ideas (OUT OF SCOPE)
- `frcc` + other multi-domain SPM monitors — deferred (MULTI-03 scoped to mfpca + spe_multivariate).
- Advisor `spm`/`clustering` aspect extensions for the new methods (ADV-01) — Phase 72.
- multi-domain/FAMM + clustering docs pages (DOCS-01) — Phase 73.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MULTI-01 | New `PyMultiFunData` opaque `#[pyclass]` handle (mirroring `PyIrregFdata`) + builder from component curves; registered and constructible from Python | §1 full MultiFunData API; §2 PyMultiFunData handle contract; §5 registration |
| MULTI-02 | Mixed-model bindings `dense_flmm`, `fast_fmm`, `multi_famm` → `fdars.famm`; CRITICAL: none of these consume `MultiFunData` (plain FdMatrix only) | §3 exact FAMM signatures; §3 result fields; §5 registration |
| MULTI-03 | Multivariate SPM `mfpca` + `spe_multivariate` extending `fdars.spm`; CRITICAL: both take `&[&FdMatrix]` slices, not MultiFunData | §4 mfpca+spe_multivariate signatures; §5 spm_mod.rs extension |
| MULTI-04 | Advanced clustering `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd` extending `fdars.clustering`; all take plain `(&FdMatrix, &[f64], &Config)` | §6 exact clustering signatures; §6 result structs; §5 clustering_mod.rs extension |
</phase_requirements>

---

## Summary

Phase 70 delivers a new `PyMultiFunData` opaque handle (the project's second opaque `#[pyclass]`
after `PyIrregFdata`), two new submodules (`fdars.multi_fdata`, `fdars.famm`), and four additions
to two existing submodules (`fdars.spm` gets `mfpca` + `spe_multivariate`; `fdars.clustering` gets
the four advanced algorithms).

**Critical discovery — MultiFunData is NOT consumed by FAMM, MFPCA, or clustering:** None of
`famm.rs`, `spm/mfpca.rs`, or `clustering_advanced.rs` imports or uses `MultiFunData`. All three
function families take plain `FdMatrix` or `&[&FdMatrix]` slices. `multi_fdata.rs` and `famm.rs`
are completely disjoint modules in the crate. The `PyMultiFunData` handle is a **standalone
opaque container** — its practical use is holding multi-domain data for Python code, but the
existing FAMM/MFPCA/clustering bindings do NOT accept it as an input parameter. The planner must
NOT generate tasks that pass `PyRef<PyMultiFunData>` to FAMM or MFPCA functions.

**FAMM take plain 2D matrices:** `dense_flmm` and `fast_fmm` take `(&FdMatrix, &[usize], Option<&FdMatrix>, &Config)`. `multi_famm` takes `(&[FdMatrix], &[usize], Option<&FdMatrix>, &Config)` — a plain Rust slice of FdMatrix, which the binding builds from a Python list of 2D numpy arrays (same Vec<FdMatrix> / Vec<&FdMatrix> pattern as `concurrent_regression` in phase 68).

**MFPCA takes `&[&FdMatrix]`:** The `mfpca` function signature is `mfpca(variables: &[&FdMatrix], config: &MfpcaConfig)`. From Python, this is a list of 2D numpy arrays, converted to Vec<FdMatrix> then a Vec<&FdMatrix> ref-vector (exact pattern from phase 68 `concurrent_regression`).

**Primary recommendation:** Sequence: (1) `multi_fdata_mod.rs` — standalone handle + builder, (2) `famm_mod.rs` — all plain-FdMatrix FAMM functions, (3) extend `spm_mod.rs` for mfpca + spe_multivariate, (4) extend `clustering_mod.rs` for the four advanced algorithms. Steps 2–4 are independent of step 1.

---

## Section 1: MultiFunData — Full API (multi_fdata.rs)

All findings read from `/home/simonm/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/multi_fdata.rs`.

### Structs

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/multi_fdata.rs:36-49]

```rust
pub struct FdComponent {
    pub data: FdMatrix,     // column-major; rows = observations, cols = evaluation points
    pub argvals: Vec<f64>,  // argvals.len() == data.ncols() — enforced by MultiFunData::new
}
```

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/multi_fdata.rs:83-88]

```rust
#[non_exhaustive]
pub struct MultiFunData {
    components: Vec<FdComponent>,  // private field — no direct access
}
```

`MultiFunData` is `#[non_exhaustive]` — struct-literal construction is impossible outside the crate. Only `MultiFunData::new` can create instances.

### Constructor — the ONLY constructor

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/multi_fdata.rs:118-157]

```rust
pub fn new(components: Vec<FdComponent>) -> Result<Self, FdarError>
```

Invariants enforced:
1. `components` must be non-empty → `FdarError::InvalidParameter`
2. All components share the same `data.nrows()` (n_obs) → `FdarError::InvalidDimension`
3. Each component: `argvals.len() == data.ncols()` → `FdarError::InvalidDimension`

There is **no `from_*` constructor**. `new` is the single entry point.

### Accessor methods — public

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/multi_fdata.rs:160-210]

```rust
pub fn n_obs(&self) -> usize                                // components[0].data.nrows()
pub fn n_components(&self) -> usize                         // components.len()
pub fn component(&self, k: usize) -> Result<&FdComponent, FdarError>
pub fn argvals(&self, k: usize) -> Result<&[f64], FdarError>
```

`component(k)` and `argvals(k)` both return `FdarError::InvalidParameter` for out-of-bounds `k`.
The `data` field of each `FdComponent` is `pub`, accessible through `component(k)?.data`.

---

## Section 2: PyMultiFunData Handle — Full Specification (MULTI-01)

### Struct definition

Mirror `PyIrregFdata` exactly [VERIFIED: src/pace_fpca_mod.rs:24-27]:

```rust
#[pyclass(name = "PyMultiFunData")]
pub struct PyMultiFunData {
    pub inner: fdars_core::multi_fdata::MultiFunData,
}
```

### Builder function signature

The builder takes a list of 2D numpy arrays (one per variable/domain) **and** a list of argvals
vectors (one per component). This matches the `FdComponent { data, argvals }` structure.

```rust
#[pyfunction]
pub fn multi_fdata_from_components<'py>(
    py: Python<'py>,
    data_list: &Bound<'py, PyList>,    // list of 2D numpy arrays, one per component
    argvals_list: &Bound<'py, PyList>, // list of 1D numpy arrays, one per component
) -> PyResult<Py<PyMultiFunData>>
```

**Builder logic:**
1. Guard: both lists same length (else `PyValueError`).
2. For each index `k`:
   a. Convert `data_list[k]` via `numpy2d_to_fdmatrix` (validates 2D, dtype f64, handles row→col-major transpose).
   b. Convert `argvals_list[k]` via `extract_ragged_vecs` (single element) or a 1D numpy read. Simpler: downcast to `PyReadonlyArray1<f64>` and call `numpy1d_to_vec`.
   c. Build `FdComponent { data: mat, argvals: av }`.
3. Call `to_pyresult(MultiFunData::new(components))?` — this validates all 3 invariants.
4. Wrap in `Py::new(py, PyMultiFunData { inner })`.

**Reject guard:** If `data_list[k]` is 1D (ndim == 1), reject with a clear error message pointing to the dense-matrix requirement.

### Accessor `#[pymethods]` on PyMultiFunData

Expose the four public Rust methods as Python properties/methods:

```rust
#[pymethods]
impl PyMultiFunData {
    #[getter]
    pub fn n_obs(&self) -> usize { self.inner.n_obs() }

    #[getter]
    pub fn n_components(&self) -> usize { self.inner.n_components() }
}
```

`component(k)` and `argvals(k)` are optional accessors — the planner may add them as `#[pyo3(name = "component")]` returning a numpy array and `#[pyo3(name = "argvals")]` returning a 1D array. These are low-risk additions but not required by any requirement.

### Module registration

```rust
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyMultiFunData>()?;
    m.add_function(wrap_pyfunction!(multi_fdata_from_components, m)?)?;
    Ok(())
}
```

---

## Section 3: FAMM Bindings — Full Specification (MULTI-02)

**CRITICAL FINDING:** None of the three FAMM functions accept or reference `MultiFunData`. All take plain `FdMatrix` inputs. [VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/famm.rs — grepped: 0 references to `multi_fdata` or `MultiFunData`]

### 3.1 `dense_flmm`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/famm.rs:1039-1044]

```rust
pub fn dense_flmm(
    data: &FdMatrix,                    // n_total × m, column-major
    subject_ids: &[usize],              // length n_total — curve-to-subject mapping
    covariates: Option<&FdMatrix>,      // n_total × p, or None
    config: &DenseFlmmConfig,
) -> Result<DenseFlmmResult, FdarError>
```

**`DenseFlmmConfig`** [VERIFIED: famm.rs:922-951]: NOT `#[non_exhaustive]` — can be struct-literal constructed.

```rust
pub struct DenseFlmmConfig {
    pub ncomp: usize,        // default 3
    pub max_iter: usize,     // default 50
    pub tol: f64,            // default 1e-10
    pub random_slopes: bool, // default false; true → FdarError::InvalidParameter (not yet impl)
}
```

**`DenseFlmmResult`** [VERIFIED: famm.rs:965-1002]: IS `#[non_exhaustive]`.

```rust
pub struct DenseFlmmResult {
    pub mean_function: Vec<f64>,    // length m
    pub beta_functions: FdMatrix,   // p × m (one row per covariate)
    pub random_effects: FdMatrix,   // n_subjects × m
    pub fitted: FdMatrix,           // n_total × m
    pub residuals: FdMatrix,        // n_total × m
    pub random_variance: Vec<f64>,  // length m
    pub sigma2_eps: f64,
    pub sigma2_u: Vec<f64>,         // length k (per FPC component)
    pub sigma2_slope: Vec<f64>,     // length k (zero-filled when random_slopes=false)
    pub ncomp: usize,
    pub n_subjects: usize,
    pub eigenvalues: Vec<f64>,      // length k
    pub n_iter: usize,
    pub converged: bool,
}
```

**PyDict fields for `dense_flmm`:**
```python
{
    "mean_function":   np.ndarray,  # (m,)
    "beta_functions":  np.ndarray,  # (p, m)
    "random_effects":  np.ndarray,  # (n_subjects, m)
    "fitted":          np.ndarray,  # (n_total, m)
    "residuals":       np.ndarray,  # (n_total, m)
    "random_variance": np.ndarray,  # (m,)
    "sigma2_eps":      float,
    "sigma2_u":        np.ndarray,  # (k,)
    "sigma2_slope":    np.ndarray,  # (k,)
    "ncomp":           int,
    "n_subjects":      int,
    "eigenvalues":     np.ndarray,  # (k,)
    "n_iter":          int,
    "converged":       bool,
}
```

**Python binding input contract:**
- `data: PyReadonlyArray2<f64>` → `numpy2d_to_fdmatrix`
- `subject_ids: Vec<i64>` → `.into_iter().map(|v| v as usize).collect::<Vec<usize>>()`
- `covariates: Option<PyReadonlyArray2<f64>>` → `Option<FdMatrix>` via `numpy2d_to_fdmatrix`
- `ncomp=3, max_iter=50, tol=1e-10` as keyword args, all with defaults

### 3.2 `fast_fmm`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/famm.rs:1524-1529]

```rust
pub fn fast_fmm(
    data: &FdMatrix,
    subject_ids: &[usize],
    covariates: Option<&FdMatrix>,
    config: &FastFmmConfig,
) -> Result<FastFmmResult, FdarError>
```

**`FastFmmConfig`** [VERIFIED: famm.rs:1441-1475]: NOT `#[non_exhaustive]`.

```rust
pub struct FastFmmConfig {
    pub smooth_window: usize,      // default 3 (1 = no smoothing; must be ≥ 1)
    pub max_iter: usize,           // default 30 (must be ≥ 1)
    pub tol: f64,                  // default 1e-8
    pub compute_inference: bool,   // default true (Wald t-stats and p-values)
}
```

**`FastFmmResult`** [VERIFIED: famm.rs:1487-1502]: IS `#[non_exhaustive]`.

```rust
pub struct FastFmmResult {
    pub beta_matrix: FdMatrix,  // p × m
    pub t_stats: FdMatrix,      // p × m (zero-filled when compute_inference=false or p=0)
    pub p_values: FdMatrix,     // p × m (one-filled when compute_inference=false or p=0)
    pub sigma2_eps: Vec<f64>,   // length m
    pub sigma2_u: Vec<f64>,     // length m
    pub n_grid: usize,          // = m
}
```

**PyDict fields for `fast_fmm`:**
```python
{
    "beta_matrix": np.ndarray,  # (p, m)
    "t_stats":     np.ndarray,  # (p, m)
    "p_values":    np.ndarray,  # (p, m)
    "sigma2_eps":  np.ndarray,  # (m,)
    "sigma2_u":    np.ndarray,  # (m,)
    "n_grid":      int,
}
```

**Note:** When `p == 0` (no covariates), `beta_matrix`, `t_stats`, `p_values` are all zero-sized (0 × m) matrices. The binding should still emit them as numpy arrays of shape (0, m).

### 3.3 `multi_famm`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/famm.rs:1340-1345]

```rust
pub fn multi_famm(
    data: &[FdMatrix],             // D matrices, each n_total × m; ALL must share ncols = m
    subject_ids: &[usize],
    covariates: Option<&FdMatrix>,
    config: &MultiFammConfig,
) -> Result<MultiFammResult, FdarError>
```

**`MultiFammConfig`** [VERIFIED: famm.rs:1272-1292]: NOT `#[non_exhaustive]`.

```rust
pub struct MultiFammConfig {
    pub ncomp: usize,    // default 3
    pub max_iter: usize, // default 50
    pub tol: f64,        // default 1e-10
}
```

**`MultiFammResult`** [VERIFIED: famm.rs:1304-1315]: IS `#[non_exhaustive]`.

```rust
pub struct MultiFammResult {
    pub components: Vec<DenseFlmmResult>,  // length D
    pub stacked_fitted: FdMatrix,          // (n_total × D) × m
    pub stacked_residuals: FdMatrix,       // (n_total × D) × m
    pub n_dims: usize,                     // = D
}
```

**`multi_famm` Python binding:** Takes a Python list of 2D numpy arrays (one per dimension). Build `Vec<FdMatrix>` from the list, then pass `&vec_of_fdmat`. The `&[FdMatrix]` slice is formed via `vec_of_fdmat.as_slice()` as `&[FdMatrix]`. All dimensions must share the same ncols (upstream validates and returns FdarError::InvalidDimension).

**PyDict fields for `multi_famm`:** `multi_famm` returns a compact summary dict; the per-dimension DenseFlmmResult contents are serialized as list-of-dicts:
```python
{
    "n_dims":             int,
    "stacked_fitted":     np.ndarray,  # (n_total * n_dims, m)
    "stacked_residuals":  np.ndarray,  # (n_total * n_dims, m)
    "components":         list[dict],  # each dict = dense_flmm result for that dimension
}
```
Each element of `"components"` is a dict with the same 14 keys as the `dense_flmm` PyDict.

---

## Section 4: MFPCA and SPE Multivariate — Full Specification (MULTI-03)

**CRITICAL FINDING:** Neither `mfpca` nor `spe_multivariate` accepts `MultiFunData`. Both take plain `&[&FdMatrix]` slices. [VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/spm/mfpca.rs — 0 references to `multi_fdata` or `MultiFunData`]

### 4.1 `mfpca`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/spm/mfpca.rs:246]

```rust
pub fn mfpca(
    variables: &[&FdMatrix],  // P matrices, each n × m_p (may differ in m_p)
    config: &MfpcaConfig,
) -> Result<MfpcaResult, FdarError>
```

**`MfpcaConfig`** [VERIFIED: mfpca.rs:47-62]: NOT `#[non_exhaustive]`.

```rust
pub struct MfpcaConfig {
    pub ncomp: usize,    // default 5
    pub weighted: bool,  // default true (weight each var by 1/std_dev before SVD)
}
```

**`MfpcaResult`** [VERIFIED: mfpca.rs:64-85]: IS `#[non_exhaustive]`. Fields exposed to Python:

```rust
pub struct MfpcaResult {
    pub scores: FdMatrix,                     // n × ncomp
    pub eigenfunctions: Vec<FdMatrix>,        // P entries; each m_p × ncomp
    pub eigenvalues: Vec<f64>,                // length ncomp
    pub means: Vec<Vec<f64>>,                 // P entries; each length m_p
    pub scales: Vec<f64>,                     // length P (per-variable std-devs)
    pub grid_sizes: Vec<usize>,               // length P
    // pub(super) combined_rotation: FdMatrix  -- NOT exposed (pub(super), private)
    // pub(super) scale_threshold: f64         -- NOT exposed (pub(super), private)
}
```

`combined_rotation` and `scale_threshold` are `pub(super)` — they are accessible within the `spm` crate module but NOT from `pyfda` bindings. The planner must not attempt to read these fields in the binding. The binding exposes only the 6 public fields.

**PyDict fields for `mfpca`:**
```python
{
    "scores":         np.ndarray,        # (n, ncomp)
    "eigenfunctions": list[np.ndarray],  # P entries; each (m_p, ncomp)
    "eigenvalues":    np.ndarray,        # (ncomp,)
    "means":          list[np.ndarray],  # P entries; each (m_p,)
    "scales":         np.ndarray,        # (P,)  — per-variable std-devs
    "grid_sizes":     list[int],         # P ints
}
```

**Python binding — Vec<FdMatrix> / Vec<&FdMatrix> pattern** (same as `concurrent_regression`, phase 68):

```rust
// Python: variables = [arr1, arr2, ...]  (list of 2D numpy arrays)
let mats: Vec<FdMatrix> = list
    .iter()
    .enumerate()
    .map(|(i, item)| {
        let arr = item.downcast::<PyReadonlyArray2<f64>>(...)?;
        numpy2d_to_fdmatrix(arr)
    })
    .collect::<PyResult<Vec<_>>>()?;
let refs: Vec<&FdMatrix> = mats.iter().collect();
let result = to_pyresult(fdars_core::spm::mfpca::mfpca(&refs, &config))?;
```

**Building the `eigenfunctions` Python list:** Iterate `result.eigenfunctions` (Vec<FdMatrix>) and convert each via `fdmatrix_to_numpy2d`. Build a `PyList` of numpy arrays.

**Building the `means` Python list:** Iterate `result.means` (Vec<Vec<f64>>) and convert each via `vec_to_numpy1d`.

### 4.2 `spe_multivariate`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/spm/stats.rs:275-280]

```rust
pub fn spe_multivariate(
    standardized_vars: &[&FdMatrix],   // P matrices, each n × m_p (centered+scaled data)
    reconstructed_vars: &[&FdMatrix],  // P matrices, each n × m_p (mfpca reconstructions)
    argvals_list: &[&[f64]],           // P argval vectors
) -> Result<Vec<f64>, FdarError>
```

Returns `Vec<f64>` of length n (per-observation multivariate SPE statistics). Converts to a 1D numpy array — NOT a PyDict.

**Python binding signature:**
```rust
#[pyfunction]
pub fn spe_multivariate<'py>(
    py: Python<'py>,
    standardized_vars: &Bound<'py, PyList>,   // list of 2D arrays
    reconstructed_vars: &Bound<'py, PyList>,  // list of 2D arrays
    argvals_list: &Bound<'py, PyList>,         // list of 1D arrays
) -> PyResult<Bound<'py, PyArray1<f64>>>
```

All three lists are converted in parallel: Vec<FdMatrix> / Vec<&FdMatrix> for the 2D inputs; Vec<Vec<f64>> / Vec<&[f64]> for argvals. Return `vec_to_numpy1d(py, result)`.

**spm_mod.rs public API — currently re-exports from submodules:**

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/spm/mod.rs:98]

```rust
pub use mfpca::{mfpca, MfpcaConfig, MfpcaResult};
// and spe_multivariate is in stats.rs — no re-export but accessible as:
// fdars_core::spm::stats::spe_multivariate
```

The binding must use the full paths:
- `fdars_core::spm::mfpca::mfpca(&refs, &config)` (or via re-export `fdars_core::spm::mfpca(...)`)
- `fdars_core::spm::stats::spe_multivariate(...)` (not re-exported at spm level)

---

## Section 5: Registration Mechanics

### 5.1 Two new files + two modified files

| Action | File | Notes |
|--------|------|-------|
| CREATE | `src/multi_fdata_mod.rs` | `PyMultiFunData` class + `multi_fdata_from_components` builder |
| CREATE | `src/famm_mod.rs` | `dense_flmm`, `fast_fmm`, `multi_famm` bindings |
| MODIFY | `src/spm_mod.rs` | Append `mfpca` + `spe_multivariate` bindings; extend `register` fn |
| MODIFY | `src/clustering_mod.rs` | Append 4 advanced clustering bindings; extend `register` fn |

### 5.2 `src/lib.rs` changes

[VERIFIED: src/lib.rs:1-73] — current last two entries are `frechet` and `density_fda` from phase 69.

Add after `density_fda_mod`:
```rust
mod multi_fdata_mod;
mod famm_mod;
```

Add in `_native` function:
```rust
register_submodule!(m, "multi_fdata", multi_fdata_mod::register);
register_submodule!(m, "famm", famm_mod::register);
```

The `spm` and `clustering` submodules are already registered — their `register` functions are extended in-place; no new `register_submodule!` calls needed.

### 5.3 `python/fdars/__init__.py` changes

[VERIFIED: python/fdars/__init__.py:38-63] — current tuple ends at `"density_fda"`.

Append two names to `_submodule_names`:
```python
"multi_fdata",  # Phase 70 — PyMultiFunData opaque handle + builder
"famm",         # Phase 70 — Functional Additive Mixed Models (dense_flmm, fast_fmm, multi_famm)
```

`spm` and `clustering` are already in the tuple — no change needed.

### 5.4 FND-02 guard compatibility

[VERIFIED: STATE.md decision Phase 67] — FND-02 asserts the Phase-55 baseline is a subset of current registrations, and per-name import/attribute registration is intact. Adding `"multi_fdata"` and `"famm"` to `_submodule_names` is additive — FND-02 is satisfied without modification.

---

## Section 6: Advanced Clustering — Full Specification (MULTI-04)

All four algorithms live in `clustering_advanced.rs` and take `(&FdMatrix, &[f64], &Config)`. None uses `MultiFunData`.

### 6.1 `dbscan_fd`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/clustering_advanced.rs:157-162]

```rust
pub fn dbscan_fd(
    data: &FdMatrix,
    argvals: &[f64],
    config: &DbscanConfig,
) -> Result<DbscanResult, FdarError>
```

**`DbscanConfig`** [VERIFIED: clustering_advanced.rs:64-88]: IS `#[non_exhaustive]`.

```rust
pub struct DbscanConfig {
    pub eps: f64,          // default 0.5 (neighbourhood radius in L2 distance units)
    pub min_points: usize, // default 3 (min curves including self for core-point)
}
```

**`DbscanResult`** [VERIFIED: clustering_advanced.rs:91-105]: IS `#[non_exhaustive]`.

```rust
pub struct DbscanResult {
    pub cluster: Vec<Option<usize>>,  // None = noise, Some(c) = cluster index (0-based)
    pub n_clusters: usize,
    pub n_noise: usize,
    pub distances: FdMatrix,           // n × n pairwise L2 distance matrix
}
```

**DBSCAN noise encoding:** `cluster` is `Vec<Option<usize>>`. Python representation: convert `None` to `-1i64` (noise) and `Some(c)` to `c as i64`. Use `usize_vec_to_numpy1d` is insufficient here — a custom conversion via `numpy` `int64` array.

**PyDict fields for `dbscan_fd`:**
```python
{
    "cluster":    np.ndarray,  # (n,) dtype=int64; -1 = noise, 0..n_clusters-1 = cluster id
    "n_clusters": int,
    "n_noise":    int,
    "distances":  np.ndarray,  # (n, n) pairwise L2 distance matrix
}
```

**Noise encoding implementation:**
```rust
let cluster_i64: Vec<i64> = result.cluster.iter().map(|c| match c {
    None => -1,
    Some(v) => *v as i64,
}).collect();
dict.set_item("cluster", vec_to_numpy1d_i64(py, cluster_i64))?;
```

Note: `vec_to_numpy1d` in `convert.rs` produces `f64` arrays [VERIFIED: convert.rs:67]. For `i64` output, the binding needs a local `into_pyarray` call or a new `vec_i64_to_numpy1d` helper. The simplest is:
```rust
use numpy::IntoPyArray;
dict.set_item("cluster", cluster_i64.into_pyarray(py))?;
```

**Python binding signature:**
```rust
#[pyfunction]
#[pyo3(signature = (data, argvals, eps=0.5, min_points=3))]
pub fn dbscan_fd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    eps: f64,
    min_points: usize,
) -> PyResult<Bound<'py, PyDict>>
```

### 6.2 `kcfc_cluster`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/clustering_advanced.rs:371-375]

```rust
pub fn kcfc_cluster(
    data: &FdMatrix,
    argvals: &[f64],
    config: &KcfcConfig,
) -> Result<KcfcResult, FdarError>
```

**`KcfcConfig`** [VERIFIED: clustering_advanced.rs:275-288]: IS `#[non_exhaustive]`.

```rust
pub struct KcfcConfig {
    pub k: usize,        // default 2 (must be ≥ 1 and ≤ n)
    pub ncomp: usize,    // default 3 (clamped to min(n_k, m) internally)
    pub max_iter: usize, // default 50
    pub seed: u64,       // default 42
}
```

**`KcfcResult`** [VERIFIED: clustering_advanced.rs:304-320]: IS `#[non_exhaustive]`.

```rust
pub struct KcfcResult {
    pub cluster: Vec<usize>,                    // length n (0-based)
    pub fpca_models: Vec<Option<FpcaResult>>,   // length k — NOT exposed in Python dict
    pub reconstruction_errors: FdMatrix,         // n × k
    pub iterations: usize,
    pub converged: bool,
}
```

`fpca_models` contains internal Rust `FpcaResult` structs which are not `#[pyclass]` — omit from the PyDict (same pattern as phase 68: exclude `fpca_x`/`fpca_y` from fof_regression).

**PyDict fields for `kcfc_cluster`:**
```python
{
    "cluster":                np.ndarray,  # (n,) dtype=int64
    "reconstruction_errors":  np.ndarray,  # (n, k)
    "iterations":             int,
    "converged":              bool,
}
```

**Python binding signature:**
```rust
#[pyfunction]
#[pyo3(signature = (data, argvals, k=2, ncomp=3, max_iter=50, seed=42))]
pub fn kcfc_cluster<'py>(...)
```

### 6.3 `funfem_cluster`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/clustering_advanced.rs:701-705]

```rust
pub fn funfem_cluster(
    data: &FdMatrix,
    argvals: &[f64],
    config: &FunFemConfig,
) -> Result<FunFemResult, FdarError>
```

**`FunFemConfig`** [VERIFIED: clustering_advanced.rs:632-650]: IS `#[non_exhaustive]`.

```rust
pub struct FunFemConfig {
    pub k: usize,        // default 2
    pub ncomp: usize,    // default 10 (global FPC components; clamped to min(n,m))
    pub p_disc: usize,   // default 0 (auto = min(k-1, ncomp_eff)); discriminative subspace dim
    pub max_iter: usize, // default 50
    pub tol: f64,        // default 1e-6
    pub seed: u64,       // default 42
}
```

**`FunFemResult`** [VERIFIED: clustering_advanced.rs:668-681]: IS `#[non_exhaustive]`.

```rust
pub struct FunFemResult {
    pub cluster: Vec<usize>,         // length n (0-based)
    pub membership: FdMatrix,        // n × k (soft membership)
    pub disc_subspace: FdMatrix,     // ncomp_eff × p_disc_eff (discriminative directions)
    pub log_likelihood: f64,
    pub iterations: usize,
    pub converged: bool,
}
```

**PyDict fields for `funfem_cluster`:**
```python
{
    "cluster":         np.ndarray,  # (n,) dtype=int64
    "membership":      np.ndarray,  # (n, k) soft assignment
    "disc_subspace":   np.ndarray,  # (ncomp_eff, p_disc_eff) discriminative directions
    "log_likelihood":  float,
    "iterations":      int,
    "converged":       bool,
}
```

**Python binding signature:**
```rust
#[pyfunction]
#[pyo3(signature = (data, argvals, k=2, ncomp=10, p_disc=0, max_iter=50, tol=1e-6, seed=42))]
pub fn funfem_cluster<'py>(...)
```

### 6.4 `align_cluster_fd`

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/clustering_advanced.rs:1335-1339]

```rust
pub fn align_cluster_fd(
    data: &FdMatrix,
    argvals: &[f64],
    config: &AlignClusterConfig,
) -> Result<AlignClusterResult, FdarError>
```

**`AlignClusterConfig`** [VERIFIED: clustering_advanced.rs:1264-1296]: IS `#[non_exhaustive]`.

```rust
pub struct AlignClusterConfig {
    pub k: usize,                // default 2
    pub max_iter: usize,         // default 20
    pub seed: u64,               // default 42
    pub use_amplitude_only: bool,// default true (shape-invariant; false = full elastic dist)
    pub elastic_lambda: f64,     // default 0.0 (penalty for full elastic dist)
    pub karcher_max_iter: usize, // default 15
    pub karcher_tol: f64,        // default 1e-4
}
```

**`AlignClusterResult`** [VERIFIED: clustering_advanced.rs:1302-1314]: IS `#[non_exhaustive]`.

```rust
pub struct AlignClusterResult {
    pub cluster: Vec<usize>,       // length n (0-based)
    pub templates: Vec<Vec<f64>>,  // k entries, each length m (per-cluster template curves)
    pub distances: FdMatrix,       // n × k elastic distance matrix
    pub iterations: usize,
    pub converged: bool,
}
```

`templates` is `Vec<Vec<f64>>` — convert each inner Vec via `vec_to_numpy1d`, collect into a `PyList`.

**PyDict fields for `align_cluster_fd`:**
```python
{
    "cluster":    np.ndarray,        # (n,) dtype=int64
    "templates":  list[np.ndarray],  # k entries, each (m,)
    "distances":  np.ndarray,        # (n, k)
    "iterations": int,
    "converged":  bool,
}
```

**Python binding signature:**
```rust
#[pyfunction]
#[pyo3(signature = (data, argvals, k=2, max_iter=20, seed=42, use_amplitude_only=true, elastic_lambda=0.0, karcher_max_iter=15, karcher_tol=1e-4))]
#[allow(clippy::too_many_arguments)]
pub fn align_cluster_fd<'py>(...)
```

---

## Section 7: Non-exhaustive Config Handling Pattern

All four clustering configs and all three FAMM result structs are `#[non_exhaustive]`. The MFPCA and FAMM configs are NOT `#[non_exhaustive]` (they can be struct-literal-built). The established pattern in this project for `#[non_exhaustive]` configs is `Default::default()` + field mutation:

[VERIFIED: src/clustering_mod.rs:158-167 — `gmm_cluster` example]

```rust
let mut config = fdars_core::SomeConfig::default();
config.field1 = value1;
config.field2 = value2;
```

This is always safe because `Default::default()` calls the crate's own constructor (no `#[non_exhaustive]` restriction applies to `Default`). For configs that are NOT `#[non_exhaustive]` (DenseFlmmConfig, MultiFammConfig, FastFmmConfig, MfpcaConfig), struct-literal construction is also fine but the `Default::default()` + mutation pattern is consistent and preferred.

There are NO string-dispatched enums in any Phase 70 function family. The only enum in `spm_mod.rs` (NcompMethod) is already bound.

---

## Section 8: Fixtures and Test Architecture

### Non-square fixture requirements (transposition guard)

All 2D binding tests MUST use non-square matrices where `n_obs ≠ n_points`. Established sizes from prior phases: `(20, 30)` or `(15, 25)`.

### Multi-variable fixture for mfpca and multi_famm

```python
import numpy as np
rng = np.random.default_rng(42)
n_obs = 20
# Variable 1: 30 grid points
var1 = rng.standard_normal((n_obs, 30))   # non-square: 20 obs × 30 pts
# Variable 2: 25 grid points (different domain)
var2 = rng.standard_normal((n_obs, 25))   # non-square: 20 obs × 25 pts
av1 = np.linspace(0, 1, 30)
av2 = np.linspace(0, 2, 25)
```

### Subject-ID fixture for FAMM (dense_flmm, fast_fmm, multi_famm)

```python
n_subjects = 5
n_visits = 4
n_total = n_subjects * n_visits  # 20 curves total
subject_ids = np.repeat(np.arange(n_subjects), n_visits).astype(np.int64)  # [0,0,0,0, 1,1,1,1, ...]
data = rng.standard_normal((n_total, 30))   # 20 × 30 non-square
```

**FAMM subject_ids dtype:** upstream expects `&[usize]`. Python passes `np.int64` array. The binding converts via `numpy1d_to_usize_vec` [VERIFIED: src/convert.rs:72]:
```rust
pub fn numpy1d_to_usize_vec(arr: PyReadonlyArray1<'_, i64>) -> Vec<usize>
```
This accepts `i64` input and casts to `usize`. Expose `subject_ids` as `PyReadonlyArray1<'_, i64>`.

### DbscanResult noise encoding fixture

```python
result = fdars.clustering.dbscan_fd(data, argvals, eps=0.5, min_points=3)
labels = result["cluster"]  # int64 array; -1 = noise
n_clusters = result["n_clusters"]
n_noise = result["n_noise"]
assert labels.dtype == np.int64
# Noise points:
noise_mask = labels == -1
```

### KcfcResult fpca_models omission test

```python
result = fdars.clustering.kcfc_cluster(data, argvals, k=3)
assert "fpca_models" not in result  # internal state; omitted
assert "reconstruction_errors" in result
assert result["reconstruction_errors"].shape == (n_obs, 3)
```

---

## Section 9: Crate Public Path Verification

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/lib.rs]

Relevant re-exports for binding use:

```rust
// multi_fdata
pub mod multi_fdata;
pub use multi_fdata::{FdComponent, MultiFunData};

// famm
pub mod famm;
// dense_flmm, fast_fmm, multi_famm, DenseFlmmConfig, MultiFammConfig, FastFmmConfig
// accessed as fdars_core::famm::dense_flmm(...)

// spm/mfpca
pub use spm::mfpca::{mfpca, MfpcaConfig, MfpcaResult};  // re-exported at spm level
// spm/stats::spe_multivariate — NOT re-exported; use fdars_core::spm::stats::spe_multivariate

// clustering_advanced — NOT re-exported at crate root; use full paths:
// fdars_core::clustering_advanced::dbscan_fd(...)
// fdars_core::clustering_advanced::kcfc_cluster(...)
// fdars_core::clustering_advanced::funfem_cluster(...)
// fdars_core::clustering_advanced::align_cluster_fd(...)
```

---

## Section 10: Architecture Patterns

### System Architecture — Phase 70 Data Flow

```
Python                      Binding Layer              fdars-core 0.33
──────                      ─────────────              ───────────────

# MULTI-01: MultiFunData handle
[list of 2D arrays]  →  multi_fdata_from_components  →  MultiFunData::new(Vec<FdComponent>)
[list of 1D argvals]       (builds FdComponent per     →  PyMultiFunData { inner }
                            component; validates)

# MULTI-02: FAMM (plain 2D inputs — no MultiFunData)
2D array + subject_ids  →  dense_flmm binding  →  famm::dense_flmm(&FdMatrix, &[usize], ...)
                        →  DenseFlmmResult     ←
                        →  PyDict (14 keys)    ←

list[2D arrays] + sids  →  multi_famm binding  →  famm::multi_famm(&[FdMatrix], ...)
                        →  MultiFammResult     ←
                        →  PyDict (4 keys)     ←

# MULTI-03: MFPCA (list of 2D arrays → &[&FdMatrix])
list[2D arrays]         →  mfpca binding       →  spm::mfpca::mfpca(&[&FdMatrix], &config)
                        →  MfpcaResult         ←
                        →  PyDict (6 keys)     ←

3× list[2D arrays]      →  spe_multivariate    →  spm::stats::spe_multivariate(...)
+ list[1D argvals]      →  Vec<f64>            ←
                        →  np.ndarray (n,)     ←

# MULTI-04: Advanced clustering (plain 2D + argvals)
2D + argvals            →  dbscan_fd           →  clustering_advanced::dbscan_fd(...)
                        →  DbscanResult        ←  cluster: Vec<Option<usize>>
                        →  PyDict, -1=noise    ←
```

### Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| MultiFunData handle | API/Binding | — | Opaque Rust type; Python has no direct access to FdComponent fields |
| FAMM fitting | API/Binding | fdars-core (REML-EM solver) | Computation in Rust; binding marshals inputs/outputs |
| MFPCA | API/Binding | fdars-core (SVD) | Joint SVD across variables in Rust |
| Advanced clustering | API/Binding | fdars-core (DBSCAN/FPCA/Fisher-EM/elastic) | All algorithms in Rust |
| Noise encoding (-1) | API/Binding | — | Vec<Option<usize>> → i64 conversion is a binding concern |

---

## Section 11: Common Pitfalls

### Pitfall 1: Assuming FAMM/MFPCA/clustering accept PyMultiFunData

**What goes wrong:** Writing a binding that accepts `PyRef<PyMultiFunData>` and extracts components for FAMM or MFPCA.
**Why it happens:** The CONTEXT.md says "consume PyMultiFunData where required" — research confirms NO function in famm.rs, spm/mfpca.rs, or clustering_advanced.rs accepts MultiFunData.
**How to avoid:** `PyMultiFunData` is a standalone container only. FAMM/MFPCA/clustering bindings take plain numpy inputs.

### Pitfall 2: Transposition on multi_famm

**What goes wrong:** Passing dimensions that share ncols correctly but forgetting that each dimension's 2D array also needs the row→col-major conversion.
**Why it happens:** `numpy2d_to_fdmatrix` handles the transpose — but if called on each array in the list correctly, multi_famm validates that all dimensions share the same ncols after the conversion.
**How to avoid:** Apply `numpy2d_to_fdmatrix` to each element in the list, then validate shapes before calling the Rust function. Non-square fixtures catch this.

### Pitfall 3: DbscanResult noise as None vs usize

**What goes wrong:** Using `usize_vec_to_numpy1d` on `cluster` (which is `Vec<Option<usize>>`, not `Vec<usize>`).
**Why it happens:** Other clustering results use `Vec<usize>` for cluster; DBSCAN differs.
**How to avoid:** Explicitly map `None → -1i64`, `Some(c) → c as i64` before building the array.

### Pitfall 4: spe_multivariate argvals as &[&[f64]] not Vec<Vec<f64>>

**What goes wrong:** Trying to pass per-observation argvals slices (the signature takes `argvals_list: &[&[f64]]`) by creating Vec<Vec<f64>> and then getting lifetime errors when trying to take references.
**Why it happens:** The Rust lifetime of `Vec<Vec<f64>>` elements must outlive the `&[&[f64]]` reference.
**How to avoid:** Collect into `Vec<Vec<f64>>` first, then build `Vec<&[f64]>` from references to those Vecs:
```rust
let av_vecs: Vec<Vec<f64>> = ...;
let av_refs: Vec<&[f64]> = av_vecs.iter().map(|v| v.as_slice()).collect();
to_pyresult(fdars_core::spm::stats::spe_multivariate(&std_refs, &rec_refs, &av_refs))?
```

### Pitfall 5: MfpcaResult combined_rotation / scale_threshold are pub(super)

**What goes wrong:** Attempting to read `result.combined_rotation` or `result.scale_threshold` in the pyfda binding.
**Why it happens:** These fields look public (`pub(super)`) but are only accessible within the `spm` module family.
**How to avoid:** Expose only the 6 public fields: `scores`, `eigenfunctions`, `eigenvalues`, `means`, `scales`, `grid_sizes`.

### Pitfall 6: FunFemConfig p_disc = 0 semantics

**What goes wrong:** Exposing `p_disc=0` as "auto" without documenting it in the binding docstring.
**Why it happens:** `p_disc: 0` means "auto = min(k-1, ncomp_eff)" — not "zero dimensions".
**How to avoid:** Document in the docstring that `p_disc=0` (default) selects the dimension automatically as `min(k-1, ncomp_eff)`.

---

## Section 12: Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Multi-domain container | Custom Python dict packing | `PyMultiFunData` opaque handle | Validates invariants once at construction; type-safe |
| FAMM variance components | Custom REML EM | `dense_flmm` / `fast_fmm` | Complex numerical convergence; already tested |
| Functional DBSCAN | Custom L2 distance + BFS | `dbscan_fd` | Precomputed distance matrix + BFS already in core |
| Per-cluster FPCA | Custom FPCA per cluster | `kcfc_cluster` | k-means++ init + FPCA reconstruction error loop |
| Fisher-EM discriminative clustering | Custom subspace GMM | `funfem_cluster` | Cholesky-inversion + SVD discriminative subspace |
| Elastic k-means | Custom Karcher mean loop | `align_cluster_fd` | Karcher mean over elastic metric with empty-cluster reinit |
| Multivariate SPE integration | Custom Simpson integration | `spe_multivariate` | Per-variable non-uniform quadrature already correct |
| i64 noise encoding | Custom dtype gymnastics | `.into_pyarray(py)` on `Vec<i64>` | Direct numpy-rust conversion via `IntoPyArray` trait |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run | `pytest tests/test_multi_fdata.py tests/test_famm.py tests/test_clustering_advanced.py tests/test_spm_mfpca.py -x` |
| Full suite | `pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| MULTI-01 | `multi_fdata_from_components` builds handle; `n_obs`, `n_components` correct | unit | `pytest tests/test_multi_fdata.py -x` | New file |
| MULTI-01 | Wrong-shape 1D input raises ValueError | unit | same | |
| MULTI-01 | Mismatched nrows across components raises ValueError | unit | same | |
| MULTI-02 | `dense_flmm` returns 14-key dict; shapes correct | unit | `pytest tests/test_famm.py::test_dense_flmm -x` | New file |
| MULTI-02 | `fast_fmm` returns 6-key dict; p=0 gives (0,m) shaped arrays | unit | `pytest tests/test_famm.py::test_fast_fmm -x` | |
| MULTI-02 | `multi_famm` returns 4-key dict; components list has D entries | unit | `pytest tests/test_famm.py::test_multi_famm -x` | |
| MULTI-03 | `mfpca` returns 6-key dict; eigenfunctions list has P entries | unit | `pytest tests/test_spm_mfpca.py -x` | New file |
| MULTI-03 | `spe_multivariate` returns (n,) array | unit | same | |
| MULTI-04 | `dbscan_fd` cluster dtype=int64; -1=noise | unit | `pytest tests/test_clustering_advanced.py -x` | New file |
| MULTI-04 | `kcfc_cluster` no `fpca_models` key in result | unit | same | |
| MULTI-04 | `funfem_cluster` membership shape (n,k) | unit | same | |
| MULTI-04 | `align_cluster_fd` templates list length k | unit | same | |

### Wave 0 Gaps

- [ ] `tests/test_multi_fdata.py` — covers MULTI-01
- [ ] `tests/test_famm.py` — covers MULTI-02
- [ ] `tests/test_spm_mfpca.py` — covers MULTI-03
- [ ] `tests/test_clustering_advanced.py` — covers MULTI-04

---

## Security Domain

Security enforcement is not applicable to this phase. All new functions are pure computation (numerical algorithms); no network I/O, auth, or user-input parsing. Error handling follows established patterns: `FdarError → PyValueError via to_pyresult`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | (none) | — | All claims verified from source this session |

This table is empty: all claims in this research were verified by reading the 0.33 registry source files directly.

---

## Sources

### Primary (HIGH confidence — read directly from source this session)

- `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/multi_fdata.rs` — MultiFunData struct, FdComponent, MultiFunData::new, all accessors (lines 1–383)
- `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/famm.rs` — dense_flmm (1039), multi_famm (1340), fast_fmm (1524) + all Config/Result structs (lines 1–1688)
- `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/spm/mfpca.rs` — mfpca (246), MfpcaConfig, MfpcaResult (lines 1–400)
- `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/spm/stats.rs` — spe_multivariate (275) (lines 250–342)
- `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/clustering_advanced.rs` — dbscan_fd (157), kcfc_cluster (371), funfem_cluster (701), align_cluster_fd (1335) + all Config/Result structs
- `src/pace_fpca_mod.rs` — PyIrregFdata template (lines 1–213)
- `src/spm_mod.rs` — existing spm bindings + register function (lines 1–873)
- `src/clustering_mod.rs` — existing clustering bindings + register function (lines 1–298)
- `src/lib.rs` — current module list + register_submodule! pattern (lines 1–73)
- `src/convert.rs` — available helpers (grep: numpy2d_to_fdmatrix, numpy1d_to_usize_vec, usize_vec_to_numpy1d, extract_ragged_vecs, bool_vec_to_numpy1d)
- `python/fdars/__init__.py` — current _submodule_names tuple (lines 38–63)

### Confirming grep

- `grep -rn "MultiFunData|multi_fdata" famm.rs` → 0 results [VERIFIED: no FAMM function uses MultiFunData]
- `grep -rn "MultiFunData|multi_fdata" spm/mfpca.rs` → 0 results [VERIFIED: mfpca takes &[&FdMatrix]]
- `grep -rn "MultiFunData|multi_fdata" clustering_advanced.rs` → 0 results [VERIFIED: all 4 algorithms take plain FdMatrix]

---

## Metadata

**Confidence breakdown:**
- MULTI-01 PyMultiFunData handle contract: HIGH — read multi_fdata.rs in full; single constructor confirmed
- MULTI-02 FAMM signatures + result fields: HIGH — read famm.rs in full; all struct fields quoted verbatim
- MULTI-03 mfpca + spe_multivariate: HIGH — read mfpca.rs and stats.rs in full; pub(super) fields identified
- MULTI-04 clustering signatures: HIGH — read clustering_advanced.rs in full; noise encoding confirmed
- MultiFunData NOT consumed by FAMM/MFPCA/clustering: HIGH — grep confirmed 0 references in all three modules

**Research date:** 2026-09-03
**Valid until:** 2026-10-03 (stable Rust crate — 0.33 pinned in Cargo.toml)
