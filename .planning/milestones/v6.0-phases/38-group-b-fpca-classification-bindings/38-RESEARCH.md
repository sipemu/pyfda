# Phase 38: Group B — FPCA & Classification Bindings - Research

**Researched:** 2026-08-20
**Domain:** PyO3 0.28 binding layer — `IrregFdata` builder + `pace_fpca` + `elastic_multinomial`
**Confidence:** HIGH (all facts read directly from `v0.23.0` git tag source and pyfda main-branch source this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Expose `fdars.irreg_fdata_from_lists(argvals_list, values_list)` accepting two Python lists of 1-D array-likes; build `IrregFdata::from_lists`; return an opaque Python handle (`#[pyclass]`). If `#[pyclass]` proves heavy, fallback is `pace_fpca` accepting the two lists directly internally.
- Reject a plain dense 2-D numpy array with a clear `ValueError`. Validate `len(argvals[i]) == len(values[i])` per-curve, raising `ValueError` on mismatch.
- `fdars.pace_fpca(data, ncomp=..., bandwidth=..., work_grid=None, alpha=..., sigma2=...)` where `data` is the IrregFdata handle. `PaceFpcaConfig` is NOT `#[non_exhaustive]` — build by struct literal from flat kwargs.
- Returns a `dict` mirroring all 10 `PaceFpcaResult` fields. `eigenfunctions (m,ncomp)` and `scores (n,ncomp)` are transposition-guarded tests. Lives in new `src/pace_fpca_mod.rs`.
- `fdars.classification.elastic_multinomial(data, labels, argvals, ...)` → dict from `ElasticMultinomialResult`. Labels must be 0-indexed contiguous; negative/non-contiguous-label guard → `ValueError` before `i64→usize`.
- `train_probabilities (n,K)` transposition-guarded at K≥3.
- New `*_to_pydict` converters; `FdMatrix→fdmatrix_to_numpy2d`, `Vec→1-D numpy`, scalars→Python float. All fallible calls via `to_pyresult()`; no `.unwrap()`.

### Claude's Discretion

- `#[pyclass]`-handle vs lists-directly choice for IrregFdata (resolved based on v0.23.0 source).
- Exact kwarg defaults.
- Dict key names (= struct field names).

### Deferred Ideas (OUT OF SCOPE)

- Advisor coverage of `pace_fpca` / `elastic_multinomial` — Phase 40 (ADV-05).
- Docs pages + SVGs + worked examples — Phase 41 (DOCS-09).
- Group C depth/outliers/ITP — Phase 39.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PACE-01 | Expose `IrregFdata` builder `fdars.irreg_fdata_from_lists(argvals_list, values_list)` accepting two Python lists of 1-D arrays (ragged); reject dense 2-D array with `ValueError`; validate per-curve length match | IrregFdata struct + `from_lists` constructor fully read from source; binding approach decided (see §4); validation logic specified |
| PACE-02 | `fdars.pace_fpca(data, ...)` → dict with all 10 `PaceFpcaResult` fields; `PaceFpcaConfig` kwargs (5 fields, not `#[non_exhaustive]`); `eigenfunctions`/`scores` layout transposition-guarded; new `src/pace_fpca_mod.rs` | All field names, types, shapes, defaults read verbatim from v0.23.0 source; converter map specified |
| CLASS-01 | `fdars.classification.elastic_multinomial(data, labels, argvals, ...)` → dict; negative/non-contiguous-label guard before `i64→usize`; `train_probabilities (n,K)` transposition-guarded at K≥3 | `elastic_multinomial` full signature + `ElasticMultinomialResult` fields read verbatim; label guard pattern verified against existing `oneway_anova_vstat` analogue |
</phase_requirements>

---

## Summary

Phase 38 exposes three fdars-core 0.23 capabilities to Python: the `IrregFdata` sparse/irregular functional-data container, PACE FPCA over that container, and K-class elastic multinomial classification. The primary implementation risk is `IrregFdata`: no existing pyfda binding uses a `#[pyclass]` opaque handle — this phase introduces the first one.

The `IrregFdata::from_lists` constructor signature, all five `PaceFpcaConfig` fields (not `#[non_exhaustive]`, struct-literal safe), all ten `PaceFpcaResult` fields, and the full `elastic_multinomial` / `ElasticMultinomialResult` have been read verbatim from the `v0.23.0` git tag. No assumptions remain on the Rust API surface. One decision is resolved here: use the `#[pyclass]` opaque handle approach (not the "two-lists-directly-to-pace_fpca" fallback), because the handle allows independent validation, a clear Python type for the PACE input, and reuse if future pace-prediction functions are added.

**Primary recommendation:** Write `src/pace_fpca_mod.rs` first as the tracer (it introduces both the `#[pyclass]` handle and the new module registration path). Once `maturin develop` green + a round-trip smoke test passes, add `elastic_multinomial` to `src/classification_mod.rs` — structurally simpler because it reuses the existing `FdMatrix` input path.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `IrregFdata` builder (PACE-01) | PyO3 wrapper layer (`src/pace_fpca_mod.rs`) | fdars-core `irreg_fdata::IrregFdata` | Python-side extraction of lists; Rust-side CSR construction in core |
| `pace_fpca` (PACE-02) | PyO3 wrapper layer (`src/pace_fpca_mod.rs`) | fdars-core `pace_fpca::pace_fpca` | Thin wrapper; all computation in core |
| `elastic_multinomial` (CLASS-01) | PyO3 wrapper layer (`src/classification_mod.rs`) | fdars-core `elastic_regression::elastic_multinomial` | Extends existing classification module |
| Label validation | PyO3 wrapper layer | — | Negative-label guard must fire before `i64→usize` cast, in pyfda binding, not in core |
| Dense-array rejection | PyO3 wrapper layer | — | `irreg_fdata_from_lists` accepts only `list`, never `np.ndarray` as the outer container |

---

## Standard Stack

No new external packages. All bindings use existing pyfda dependencies.

### Existing Converters Used

| Converter | Location | Used by |
|-----------|----------|---------|
| `numpy2d_to_fdmatrix` | `src/convert.rs:29-42` | `elastic_multinomial` data input |
| `fdmatrix_to_numpy2d` | `src/convert.rs:44-58` | `eigenfunctions`, `scores`, `fitted`, `fitted_lower`, `fitted_upper`, `train_probabilities` |
| `numpy1d_to_vec` | `src/convert.rs:60-62` | argvals in `elastic_multinomial` |
| `vec_to_numpy1d` | `src/convert.rs:64-67` | `mean`, `eigenvalues`, `argvals` in PACE result; `predicted_classes` counts |
| `usize_vec_to_numpy1d` | `src/convert.rs:75-78` | `classes`, `predicted_classes` in elastic_multinomial result |
| `to_pyresult` | `src/convert.rs:90-93` | All fallible calls |

[VERIFIED: src/convert.rs:29-93]

---

## Package Legitimacy Audit

No external packages installed in this phase. N/A.

---

## Architecture Patterns

### Binding 1: IrregFdata `#[pyclass]` opaque handle

**Decision:** Use the `#[pyclass]` opaque handle approach (not lists-directly-to-pace_fpca). Justification:

1. Validates once at construction, not re-validates on every `pace_fpca` call.
2. Provides a named Python type users can inspect (`type(fd)` → `fdars.pace_fpca.PyIrregFdata`).
3. Clean precedent: no impedance mismatch when/if `predict_elastic_multinomial`-style functions for new sparse curves are added (they can accept the same handle).
4. `#[pyclass]` in PyO3 0.28 is straightforward when the inner type is `Clone` — `IrregFdata` derives `Clone` [VERIFIED: fdars-core/src/irreg_fdata/mod.rs:32-33].

**PyO3 0.28 `#[pyclass]` pattern:**

```rust
// src/pace_fpca_mod.rs
use pyo3::prelude::*;
use fdars_core::irreg_fdata::IrregFdata;
use crate::convert::to_pyerr;
use pyo3::exceptions::PyValueError;

/// Opaque handle wrapping fdars-core IrregFdata for irregular/sparse functional data.
#[pyclass(name = "PyIrregFdata")]
pub struct PyIrregFdata {
    pub inner: IrregFdata,
}

#[pyfunction]
pub fn irreg_fdata_from_lists<'py>(
    py: Python<'py>,
    argvals_list: &Bound<'py, pyo3::types::PyList>,
    values_list: &Bound<'py, pyo3::types::PyList>,
) -> PyResult<Py<PyIrregFdata>> {
    // ... validation and construction ...
    Py::new(py, PyIrregFdata { inner })
}
```

**Registering the class:** `m.add_class::<PyIrregFdata>()?` in the `register` fn of `pace_fpca_mod.rs`, called from `register_submodule!(m, "pace_fpca", pace_fpca_mod::register)` in `lib.rs`.

**Consuming in `pace_fpca`:**

```rust
#[pyfunction]
pub fn pace_fpca<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,       // PyO3 passes &T for #[pyclass] params
    ncomp: usize,
    bandwidth: f64,
    sigma2: f64,
    work_grid: Option<Vec<f64>>,
    alpha: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let config = fdars_core::pace_fpca::PaceFpcaConfig {
        ncomp, bandwidth, sigma2,
        work_grid: work_grid.unwrap_or_else(|| {
            let m = 51usize;
            (0..m).map(|i| i as f64 / (m - 1) as f64).collect()
        }),
        alpha,
    };
    let result = to_pyresult(fdars_core::pace_fpca::pace_fpca(&data.inner, &config))?;
    pace_fpca_result_to_pydict(py, result)
}
```

Note: `data: &PyIrregFdata` (not `Py<PyIrregFdata>`) is the correct PyO3 0.28 parameter form when you only need a borrow. PyO3 automatically extracts a `&T` from a Python `PyIrregFdata` object.

### Binding 2: List-of-arrays extraction in PyO3 0.28

**How to extract `Vec<Vec<f64>>` from a Python `list[np.ndarray | list[float]]`:**

PyO3 0.28 does NOT auto-`FromPyObject` for `Vec<Vec<f64>>` from a Python list-of-ndarrays (FromPyObject only handles homogeneous Python sequences of the base type). The correct approach is manual per-element downcast:

```rust
fn extract_list_of_vecs<'py>(
    list: &Bound<'py, pyo3::types::PyList>,
) -> PyResult<Vec<Vec<f64>>> {
    use numpy::PyReadonlyArray1;
    list.iter()
        .enumerate()
        .map(|(i, item)| {
            // Accept either a 1-D numpy array or a Python list/tuple of floats
            if let Ok(arr) = item.downcast::<numpy::PyArray1<f64>>() {
                Ok(arr.readonly().as_array().to_vec())
            } else if let Ok(seq) = item.downcast::<pyo3::types::PyList>() {
                seq.iter()
                    .map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else {
                Err(PyValueError::new_err(format!(
                    "argvals_list[{i}]: expected a 1-D numpy array or list of floats, \
                     got {}",
                    item.get_type().name().unwrap_or("?")
                )))
            }
        })
        .collect()
}
```

[ASSUMED] PyO3 0.28 exact `downcast` API (training knowledge; verify the `downcast` vs `extract` idiom against installed PyO3 0.28 docs at execution start.)

**Dense-array rejection:** The outer `argvals_list` parameter is typed as `&Bound<'py, PyList>`. A numpy 2-D array is a `PyArray2`, not a `PyList`, so PyO3 will fail the Python-to-Rust extraction before the function body runs. However, to produce a helpful error instead of a generic PyO3 TypeError, accept `&Bound<'py, PyAny>` and add an explicit check:

```rust
#[pyfunction]
pub fn irreg_fdata_from_lists<'py>(
    py: Python<'py>,
    argvals_list: &Bound<'py, pyo3::types::PyAny>,
    values_list: &Bound<'py, pyo3::types::PyAny>,
) -> PyResult<Py<PyIrregFdata>> {
    // Reject dense 2-D numpy array explicitly
    if argvals_list.is_instance_of::<numpy::PyArray2<f64>>()
        || values_list.is_instance_of::<numpy::PyArray2<f64>>()
    {
        return Err(PyValueError::new_err(
            "irreg_fdata_from_lists: received a 2-D numpy array; \
             pass two Python lists of 1-D arrays (one per curve), not a dense matrix. \
             For dense functional data, use fdars.fdata functions directly.",
        ));
    }
    let av_list = argvals_list.downcast::<pyo3::types::PyList>()
        .map_err(|_| PyValueError::new_err(
            "argvals_list must be a Python list of 1-D arrays"))?;
    let vl_list = values_list.downcast::<pyo3::types::PyList>()
        .map_err(|_| PyValueError::new_err(
            "values_list must be a Python list of 1-D arrays"))?;
    // ... extract, validate, construct
}
```

[ASSUMED] `numpy::PyArray2::<f64>::is_instance_of` API form (verify against PyO3 0.28 numpy bindings at execution start).

### Binding 3: IrregFdata construction and validation

`IrregFdata::from_lists` panics on mismatch [VERIFIED: fdars-core/src/irreg_fdata/mod.rs:56-66]. The binding MUST validate before calling it:

```rust
// Validate lists have equal length
if av_vecs.len() != vl_vecs.len() {
    return Err(PyValueError::new_err(format!(
        "irreg_fdata_from_lists: argvals_list has {} curves but values_list has {} curves",
        av_vecs.len(), vl_vecs.len()
    )));
}
// Validate per-curve length match
for i in 0..av_vecs.len() {
    if av_vecs[i].len() != vl_vecs[i].len() {
        return Err(PyValueError::new_err(format!(
            "irreg_fdata_from_lists: curve {i}: argvals has {} points but values has {}",
            av_vecs[i].len(), vl_vecs[i].len()
        )));
    }
}
let inner = IrregFdata::from_lists(&av_vecs, &vl_vecs);
```

Note: `IrregFdata::from_lists` is a valid public constructor at v0.23.0. A second constructor `from_flat` (fallible, returns `Result`) also exists but is for R interop and not needed here [VERIFIED: fdars-core/src/irreg_fdata/mod.rs:71-108].

### Binding 4: `PaceFpcaConfig` — struct-literal construction

`PaceFpcaConfig` is NOT `#[non_exhaustive]` [VERIFIED: fdars-core/src/pace_fpca.rs:51-52 — doc comment: "No `#[non_exhaustive]` — follows the `crate::elastic_regression::ElasticPcrConfig` convention for config structs"]. Struct-literal construction in the wrapper is safe and expected:

```rust
let config = fdars_core::pace_fpca::PaceFpcaConfig {
    ncomp,
    bandwidth,
    sigma2,
    work_grid: work_grid.unwrap_or_else(default_work_grid_51),
    alpha,
};
```

**Verified defaults** [VERIFIED: fdars-core/src/pace_fpca.rs:72-83 `impl Default for PaceFpcaConfig`]:

| Field | Default |
|-------|---------|
| `ncomp` | `3` |
| `bandwidth` | `0.1` |
| `sigma2` | `0.01` |
| `work_grid` | 51 uniform points on [0,1]: `(0..51).map(|i| i as f64 / 50.0).collect()` |
| `alpha` | `0.05` |

### Binding 5: `PaceFpcaResult` — all 10 fields

**Verbatim struct definition** [VERIFIED: fdars-core/src/pace_fpca.rs:97-120]:

```rust
#[non_exhaustive]
pub struct PaceFpcaResult {
    pub mean: Vec<f64>,           // length m
    pub eigenvalues: Vec<f64>,    // length ncomp (ACTUAL, may be < config.ncomp)
    pub eigenfunctions: FdMatrix, // shape m × ncomp (column-major)
    pub scores: FdMatrix,         // shape n × ncomp (column-major)
    pub fitted: FdMatrix,         // shape n × m (column-major)
    pub fitted_lower: FdMatrix,   // shape n × m (column-major)
    pub fitted_upper: FdMatrix,   // shape n × m (column-major)
    pub argvals: Vec<f64>,        // length m (echoed from config.work_grid)
    pub sigma2: f64,              // echoed from config.sigma2
    pub ncomp: usize,             // ACTUAL component count extracted
}
```

`PaceFpcaResult` IS `#[non_exhaustive]` — access fields individually, never struct-literal.

**Python dict layout:**

| Dict key | Converter | Python shape/type | Notes |
|----------|-----------|-------------------|-------|
| `"mean"` | `vec_to_numpy1d` | `(m,)` | Kernel-smoothed mean on work grid |
| `"eigenvalues"` | `vec_to_numpy1d` | `(ncomp,)` | Use `result.ncomp` for count, not `config.ncomp` |
| `"eigenfunctions"` | `fdmatrix_to_numpy2d` | `(m, ncomp)` | Column k = k-th eigenfunction; access as `ef[:, k]` |
| `"scores"` | `fdmatrix_to_numpy2d` | `(n, ncomp)` | Row i = FPC scores for curve i |
| `"fitted"` | `fdmatrix_to_numpy2d` | `(n, m)` | Fitted trajectories on work grid |
| `"fitted_lower"` | `fdmatrix_to_numpy2d` | `(n, m)` | Lower pointwise confidence band |
| `"fitted_upper"` | `fdmatrix_to_numpy2d` | `(n, m)` | Upper pointwise confidence band |
| `"argvals"` | `vec_to_numpy1d` | `(m,)` | Work grid echoed from config |
| `"sigma2"` | scalar | `float` | Measurement-error variance used |
| `"ncomp"` | scalar | `int` | ACTUAL components extracted (may be < requested) |

**Transposition guard shapes:** Choose test data with n≠m≠ncomp so a transpose bugs are distinguishable. For example: n=6 curves, m=21 grid points, ncomp=2 (verified from core test `small_irreg_data` [VERIFIED: fdars-core/src/pace_fpca.rs:632-651]).

**`ncomp` truncation:** `result.ncomp` may be less than `config.ncomp` when the smoothed covariance yields fewer positive eigenvalues [VERIFIED: fdars-core/src/pace_fpca.rs:394-407]. The binding echoes `result.ncomp` in the dict and uses it (not `config.ncomp`) for all shape extractions.

### Binding 6: `elastic_multinomial` and `ElasticMultinomialResult`

**Verbatim function signature** [VERIFIED: fdars-core/src/elastic_regression/logistic.rs:252-260]:

```rust
pub fn elastic_multinomial(
    data: &FdMatrix,      // n × m
    y: &[usize],          // class labels in 0..K (contiguous), length n
    argvals: &[f64],      // length m
    ncomp_beta: usize,    // B-spline basis functions for beta per OvR model
    lambda: f64,          // roughness penalty on beta
    max_iter: usize,      // IRLS max iterations per OvR binary fit
    tol: f64,             // convergence tolerance
) -> Result<ElasticMultinomialResult, FdarError>
```

**Verbatim `ElasticMultinomialResult` struct** [VERIFIED: fdars-core/src/elastic_regression/logistic.rs:214-227]:

```rust
#[non_exhaustive]
pub struct ElasticMultinomialResult {
    pub n_classes: usize,                  // K
    pub classes: Vec<usize>,               // sorted 0..K
    pub class_models: Vec<ElasticLogisticResult>, // K OvR models — NOT exposed to Python
    pub train_probabilities: FdMatrix,     // shape n × K (row-normalised, each row sums to 1)
    pub predicted_classes: Vec<usize>,     // length n
    pub train_accuracy: f64,
}
```

`ElasticMultinomialResult` IS `#[non_exhaustive]`.

**Python dict layout (expose 5 of 6 fields; omit `class_models`):**

| Dict key | Converter | Python shape/type | Notes |
|----------|-----------|-------------------|-------|
| `"n_classes"` | scalar | `int` | K |
| `"classes"` | `usize_vec_to_numpy1d` | `(K,)` int64 | Always `[0, 1, ..., K-1]` |
| `"train_probabilities"` | `fdmatrix_to_numpy2d` | `(n, K)` | Each row sums to 1.0; transposition-guarded at K≥3 |
| `"predicted_classes"` | `usize_vec_to_numpy1d` | `(n,)` int64 | Training predictions |
| `"train_accuracy"` | scalar | `float` | |

**Do NOT expose `class_models`:** `Vec<ElasticLogisticResult>` is a complex nested type; omitting it matches the ARCHITECTURE.md decision [CITED: .planning/research/ARCHITECTURE.md:111-112] and the `FunctionalGlmResult.fpca` omission precedent.

**Label parameter:** `elastic_multinomial` takes `y: &[usize]`. The pyfda binding receives a `PyReadonlyArray1<'py, i64>` (matching all existing classification functions). The CR-01 negative-label guard must fire before the `i64→usize` cast:

```rust
#[pyfunction]
#[pyo3(signature = (data, labels, argvals, ncomp_beta=10, lambda_=0.1, max_iter=100, tol=1e-4))]
pub fn elastic_multinomial<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp_beta: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);

    // CR-01 guard: negative labels wrap to usize::MAX without this check
    let raw = labels.as_array();
    if raw.iter().any(|&x| x < 0) {
        return Err(PyValueError::new_err(
            "elastic_multinomial: labels must be non-negative 0-indexed integers; \
             got at least one negative value. Remap to 0..K before calling.",
        ));
    }
    let lab: Vec<usize> = raw.iter().map(|&x| x as usize).collect();

    let result = to_pyresult(fdars_core::elastic_regression::elastic_multinomial(
        &mat, &lab, &av, ncomp_beta, lambda_, max_iter, tol,
    ))?;
    elastic_multinomial_result_to_pydict(py, result)
}
```

Note: `lambda` is a Python keyword; use `lambda_` as the Rust parameter name and expose as `lambda` in the `#[pyo3(signature = (...))]`.

**`ElasticLogisticResult` fields** (for reference if partial dict is added later) [VERIFIED: fdars-core/src/elastic_regression/logistic.rs:11-33]: `alpha: f64`, `beta: Vec<f64>`, `probabilities: Vec<f64>`, `predicted_classes: Vec<usize>`, `accuracy: f64`, `loss: f64`, `gammas: FdMatrix`, `aligned_srsfs: FdMatrix`, `n_iter: usize`.

### Module Registration Pattern

**`lib.rs` changes needed:**

```rust
// Add after existing mod declarations:
mod pace_fpca_mod;

// Add inside _native pymodule fn:
register_submodule!(m, "pace_fpca", pace_fpca_mod::register);
```

[VERIFIED: src/lib.rs:8-63 — existing pattern; `pace_fpca` is the 20th submodule]

**`pace_fpca_mod.rs` register fn:**

```rust
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyIrregFdata>()?;
    m.add_function(wrap_pyfunction!(irreg_fdata_from_lists, m)?)?;
    m.add_function(wrap_pyfunction!(pace_fpca, m)?)?;
    Ok(())
}
```

**`python/fdars/__init__.py` change:**

Add `"pace_fpca"` to `_submodule_names` tuple [VERIFIED: python/fdars/__init__.py:34-54 — current list has 19 names; `"pace_fpca"` becomes the 20th]:

```python
_submodule_names = (
    "fdata", "depth", "metric", "basis", "smoothing", "clustering",
    "regression", "alignment", "outliers", "seasonal", "spm",
    "classification", "tolerance", "conformal", "simulation", "explain",
    "represent", "scoring", "inference",
    "pace_fpca",   # NEW — Phase 38
)
```

This makes `fdars.pace_fpca.irreg_fdata_from_lists(...)` and `fdars.pace_fpca.pace_fpca(...)` and `fdars.pace_fpca.PyIrregFdata` accessible via both import patterns.

**`classification_mod.rs` register fn extension:**

```rust
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // ... existing 8 functions ...
    m.add_function(wrap_pyfunction!(elastic_multinomial, m)?)?;
    Ok(())
}
```

### Recommended Project Structure

```
src/
├── pace_fpca_mod.rs        # NEW: PyIrregFdata class + irreg_fdata_from_lists + pace_fpca
├── classification_mod.rs   # EXTEND: add elastic_multinomial
├── lib.rs                  # EXTEND: mod pace_fpca_mod + register_submodule!
└── convert.rs              # unchanged
python/fdars/
└── __init__.py             # EXTEND: add "pace_fpca" to _submodule_names
tests/
└── test_pace_fpca.py       # NEW: PACE + IrregFdata tests
└── test_classification.py  # EXTEND: elastic_multinomial tests
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSR sparse storage | Custom Python-side offset vec | `IrregFdata::from_lists` in core | Core handles all layout, range computation, memory efficiency |
| Per-curve Cholesky solve | Manual numpy.linalg | `pace_fpca` in core | Core handles ridge stabilisation retry, NaN-mean guard, all 6 pipeline steps |
| SRSF warping + OvR | Custom logistic | `elastic_multinomial` in core | SRSF transform, Armijo line search, warp update are all in core |
| JSON-serialise `FdMatrix` | `serde` feature on | `fdmatrix_to_numpy2d` | Already in convert.rs; serde not enabled and not needed |

---

## Runtime State Inventory

Phase 38 is a greenfield binding phase (no rename/refactor). This section is skipped.

---

## Common Pitfalls

### Pitfall 1: `from_lists` panics if called before validating list length mismatch

**What goes wrong:** `IrregFdata::from_lists` calls `assert_eq!` on the outer list lengths and per-curve pair lengths [VERIFIED: fdars-core/src/irreg_fdata/mod.rs:54-66]. A Python `ValueError` from an assertion panic in Rust produces an ugly `PanicException`, not a `ValueError`.

**How to avoid:** Validate `av_vecs.len() == vl_vecs.len()` and for each `i` that `av_vecs[i].len() == vl_vecs[i].len()` BEFORE calling `from_lists`. Raise `PyValueError` with a curve-index-specific message.

**Warning signs:** Test with mismatched outer lengths and with mismatched inner lengths; both must raise `ValueError`, not `PanicException`.

### Pitfall 2: `PaceFpcaResult.ncomp` may be less than `config.ncomp` — never hardcode the requested count

**What goes wrong:** `result.ncomp` (actual) ≤ `config.ncomp` (requested) [VERIFIED: fdars-core/src/pace_fpca.rs:97 doc comment and line 397 `actual_ncomp`]. If the binding uses `config.ncomp` to size dict arrays instead of `result.ncomp`, matrix dimensions can be wrong or indexing panics.

**How to avoid:** Always echo `result.ncomp` in the dict. Use `result.ncomp` for shapes. Write a test with small data where `actual_ncomp < config.ncomp`.

### Pitfall 3: `eigenfunctions` shape is `(m, ncomp)` — column k is the k-th eigenfunction

**What goes wrong:** `eigenfunctions` is `FdMatrix` with `nrows=m, ncols=ncomp` [VERIFIED: fdars-core/src/pace_fpca.rs:105 "shape m × ncomp"]. `fdmatrix_to_numpy2d` returns `(m, ncomp)` in Python — correct. If transposed to `(ncomp, m)`, the k-th eigenfunction is at `ef[k, :]` (wrong) instead of `ef[:, k]` (correct).

**How to avoid:** The transposition guard test must assert `result["eigenfunctions"].shape == (m, ncomp)` with n≠m≠ncomp in the synthetic data. Also test column orthonormality: `np.allclose(ef.T @ ef, np.eye(ncomp), atol=0.15)`.

### Pitfall 4: `elastic_multinomial` takes `y: &[usize]` from Python `i64` — negative labels wrap silently

**What goes wrong:** `numpy1d_to_usize_vec` casts `i64 → usize` without a sign check [VERIFIED: src/convert.rs:71-73: `arr.as_array().iter().map(|&x| x as usize).collect()`]. A label of `-1` becomes `usize::MAX`, which the core will reject with a confusing `InvalidParameter` about contiguous range.

**How to avoid:** Inline the CR-01 pattern from `oneway_anova_vstat` [VERIFIED: src/inference_mod.rs:532-537]: check `raw.iter().any(|&x| x < 0)` and raise `PyValueError` with a human-readable message before the cast.

### Pitfall 5: `class_models` must not be exposed — `ElasticLogisticResult` is `#[non_exhaustive]`

**What goes wrong:** `class_models: Vec<ElasticLogisticResult>` is a nested type. Attempting to struct-literal it for test helpers fails compilation; serialising it field-by-field is possible but adds surface area not required for CLASS-01.

**How to avoid:** Do not expose `class_models` in the dict for v6.0. Access `r.n_classes`, `r.classes`, `r.train_probabilities`, `r.predicted_classes`, `r.train_accuracy` individually (all non-exhaustive-safe field access).

### Pitfall 6: `pace_fpca` returns `ComputationFailed` for too-narrow bandwidth — test must handle this

**What goes wrong:** If a test uses bandwidth too narrow for the data range, `mean_irreg` returns NaN for some work-grid points, and `pace_fpca` returns `Err(ComputationFailed)` [VERIFIED: fdars-core/src/pace_fpca.rs:369-384]. The NaN-mean guard is explicit in the source.

**How to avoid:** In tests use `bandwidth ≥ 0.15` for data on [0,1] with 3–5 points per curve. See the core test `small_irreg_data` which uses `bandwidth=0.2` [VERIFIED: fdars-core/src/pace_fpca.rs:663-665].

### Pitfall 7: `#[pyclass]` handle and `pace_fpca` function name collision

**What goes wrong:** Both the `#[pyclass]` wrapper and the module sub-function are logically named after the same concept. The registered Python function must be `pace_fpca`, but the Rust binding function for `fdars_core::pace_fpca::pace_fpca` cannot also be named `pace_fpca` in the same Rust module without aliasing.

**How to avoid:** In `pace_fpca_mod.rs`, use the Rust function name `run_pace_fpca` or qualify the core call. The `#[pyfunction]` decorator macro lets you expose it as `pace_fpca` to Python regardless of the Rust name:

```rust
#[pyfunction(name = "pace_fpca")]
pub fn run_pace_fpca<'py>(...) -> PyResult<...> {
    let result = to_pyresult(fdars_core::pace_fpca::pace_fpca(&data.inner, &config))?;
    ...
}
```

[ASSUMED] `#[pyfunction(name = "...")]` syntax in PyO3 0.28 (likely; verify against installed PyO3 docs at execution start). Alternative: rename the Rust fn `py_pace_fpca` and use `#[pyo3(name = "pace_fpca")]`.

---

## Code Examples

### IrregFdata round-trip (builder → pace_fpca → check shapes)

```python
# Source: verified from v0.23.0 pace_fpca.rs test small_irreg_data + shape smoke test
import numpy as np
import fdars.pace_fpca as pf

argvals_list = [
    np.array([0.1, 0.4, 0.7]),
    np.array([0.0, 0.3, 0.6, 0.9]),
    np.array([0.2, 0.5, 0.8]),
    np.array([0.0, 0.25, 0.5, 0.75, 1.0]),
    np.array([0.1, 0.5, 0.9]),
    np.array([0.0, 0.4, 0.8]),
]
values_list = [
    np.array([(i+1) * np.sin(t) for t in av])
    for i, av in enumerate(argvals_list)
]

fd = pf.irreg_fdata_from_lists(argvals_list, values_list)
# fd is a PyIrregFdata opaque handle

result = pf.pace_fpca(fd, ncomp=2, bandwidth=0.2, sigma2=0.01, alpha=0.05)
n, m, ncomp = 6, 51, result["ncomp"]

assert result["eigenfunctions"].shape == (m, ncomp)  # (m, ncomp), NOT (ncomp, m)
assert result["scores"].shape == (n, ncomp)
assert result["fitted"].shape == (n, m)
assert result["ncomp"] <= 2
```

### elastic_multinomial K=3 probability shape guard

```python
# Source: verified from v0.23.0 logistic.rs ElasticMultinomialResult
import numpy as np
import fdars.classification as cls

n, m, K = 30, 32, 3
rng = np.random.default_rng(42)
data = rng.standard_normal((n, m))
labels = np.array([i % K for i in range(n)], dtype=np.int64)
argvals = np.linspace(0, 1, m)

result = cls.elastic_multinomial(
    data, labels, argvals, ncomp_beta=5, lambda_=0.1, max_iter=30, tol=1e-3
)
assert result["train_probabilities"].shape == (n, K)  # NOT (K, n)
assert np.allclose(result["train_probabilities"].sum(axis=1), 1.0, atol=1e-6)
assert result["n_classes"] == K

# Negative label guard
import pytest
with pytest.raises(ValueError, match="non-negative"):
    cls.elastic_multinomial(
        data, np.array([-1, 0, 1] * (n // 3), dtype=np.int64),
        argvals, ncomp_beta=5, lambda_=0.1, max_iter=5, tol=1e-3
    )
```

### Dense-array rejection

```python
import pytest
import numpy as np
import fdars.pace_fpca as pf

data_2d = np.zeros((5, 10))  # Dense 2-D array — must be rejected
with pytest.raises(ValueError, match="2-D numpy array"):
    pf.irreg_fdata_from_lists(data_2d, data_2d)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dense shared-grid FPCA (`fpca_1d`) | PACE sparse FPCA (`pace_fpca`) for irregular data | fdars-core 0.23 | Enables truly sparse longitudinal functional data |
| Binary-only `elastic_logistic` | K-class OvR `elastic_multinomial` | fdars-core 0.23 | Extends elastic classification to K≥2 classes |
| No Python-facing `#[pyclass]` in pyfda | `PyIrregFdata` opaque handle (Phase 38) | This phase | First `#[pyclass]` in pyfda; precedent for future opaque handles |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `#[pyfunction(name = "pace_fpca")]` attribute syntax in PyO3 0.28 | Code Examples / Pitfall 7 | Use `#[pyo3(name = "...")]` instead; compile error catches it immediately |
| A2 | `numpy::PyArray2::<f64>::is_instance_of` API form for dense-array rejection | Binding 2 | May need `item.is_instance_of::<PyArray2<f64>>()` form; verify against installed PyO3 numpy 0.28 docs at execution start |
| A3 | Per-element `downcast::<numpy::PyArray1<f64>>()` works in PyO3 0.28 for extracting ndarray elements from a Python list | Binding 2 | Might need `extract::<PyReadonlyArray1<f64>>()` instead; verify at execution start |
| A4 | `data: &PyIrregFdata` (not `Py<PyIrregFdata>`) is the correct parameter form in PyO3 0.28 for borrowing a `#[pyclass]` | Binding 1 | Compile error catches immediately; alternative is `data: Py<PyIrregFdata>` then `data.get()` |
| A5 | `elastic_multinomial` default hyperparams for pyfda binding (ncomp_beta=10, lambda=0.1, max_iter=100, tol=1e-4) | Binding 6 | Core has no defaults; pyfda binding chooses reasonable values. Verify against elastic_logistic binding defaults if they exist |

**If this table is empty:** Not applicable — 5 assumptions to verify at execution start.

---

## Open Questions

1. **PyO3 0.28 `#[pyclass]` borrow form for `pace_fpca` parameter**
   - What we know: PyO3 0.28 accepts `data: &T` for a `#[pyclass]` in most cases.
   - What's unclear: Whether lifetime annotations or `PyRef<'_, T>` are needed instead of `&T` in some compiler configurations.
   - Recommendation: Write the tracer with `data: &PyIrregFdata` first; if compile fails, switch to `data: PyRef<'_, PyIrregFdata>` and access `data.inner`.

2. **Default hyperparams for `elastic_multinomial` in the pyfda binding**
   - What we know: `fdars_core::elastic_multinomial` has no `Default` config struct.
   - What's unclear: What defaults are consistent with `elastic_logistic` usability.
   - Recommendation: Check if `elastic_logistic` in `classification_mod.rs` exposes defaults (it currently does not appear in the pyfda binding — `elastic_logistic` is not in `classification_mod.rs`); use ncomp_beta=10, lambda=0.1, max_iter=100, tol=1e-4 as reasonable starting points.

3. **Whether `predict_elastic_multinomial` should be bound in Phase 38**
   - What we know: `predict_elastic_multinomial` exists in core [VERIFIED: fdars-core/src/elastic_regression/logistic.rs:390-440]. CLASS-01 does not require it — `predicted_classes` in the training result dict is sufficient.
   - What's unclear: Whether omitting it creates friction for test authors wanting to run prediction on held-out data.
   - Recommendation: Defer to Phase 41 docs or a follow-up; bind only `elastic_multinomial` for CLASS-01.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Rust toolchain | maturin develop | check at build | 1.83+ | — |
| Python venv with fdars | pytest | use `.venv` | 3.14.6 detected | — |
| maturin | build | not confirmed in shell path | 1.x | `pip install maturin` |
| fdars-core 0.23.0 | all bindings | in Cargo.lock (Phase 36 completed) | 0.23.0 | — |

[ASSUMED] maturin available in `.venv` (standard project setup per CLAUDE.md).

Build command: `maturin develop --release` (or `maturin develop` for debug).
Test command: `pytest tests/test_pace_fpca.py tests/test_classification.py -x -v`.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (detected in `tests/` directory) |
| Config file | none detected — invoked directly |
| Quick run command | `pytest tests/test_pace_fpca.py tests/test_classification.py -x -v` |
| Full suite command | `pytest tests/ -x -v` |
| Build command | `maturin develop` (debug) or `maturin develop --release` (perf tests) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PACE-01 | `irreg_fdata_from_lists` accepts two lists of 1-D arrays | unit | `pytest tests/test_pace_fpca.py::test_irreg_fdata_round_trip -x` | ❌ Wave 0 |
| PACE-01 | `irreg_fdata_from_lists` rejects dense 2-D numpy array with `ValueError` | unit | `pytest tests/test_pace_fpca.py::test_dense_array_rejection -x` | ❌ Wave 0 |
| PACE-01 | `irreg_fdata_from_lists` rejects ragged-mismatch lists with `ValueError` | unit | `pytest tests/test_pace_fpca.py::test_ragged_mismatch_rejection -x` | ❌ Wave 0 |
| PACE-02 | `pace_fpca` result dict has all 10 keys with correct shapes | unit | `pytest tests/test_pace_fpca.py::test_pace_result_shapes -x` | ❌ Wave 0 |
| PACE-02 | `eigenfunctions.shape == (m, ncomp)` (not transposed) | unit | `pytest tests/test_pace_fpca.py::test_eigenfunctions_transposition_guard -x` | ❌ Wave 0 |
| PACE-02 | `scores.shape == (n, ncomp)` with n≠m≠ncomp | unit | `pytest tests/test_pace_fpca.py::test_scores_transposition_guard -x` | ❌ Wave 0 |
| PACE-02 | `result["ncomp"] <= config_ncomp` (truncation handled) | unit | `pytest tests/test_pace_fpca.py::test_ncomp_truncation -x` | ❌ Wave 0 |
| PACE-02 | `pace_fpca` called twice with same args → identical result | unit | `pytest tests/test_pace_fpca.py::test_pace_determinism -x` | ❌ Wave 0 |
| CLASS-01 | `elastic_multinomial` with K=3 labels → `train_probabilities.shape == (n, K)` | unit | `pytest tests/test_classification.py::test_elastic_multinomial_shape_k3 -x` | ❌ Wave 0 |
| CLASS-01 | Row sums of `train_probabilities` are all 1.0 | unit | `pytest tests/test_classification.py::test_train_probabilities_row_sum -x` | ❌ Wave 0 |
| CLASS-01 | Negative label `[-1, 0, 1]` raises `ValueError` (not usize wrapping) | unit | `pytest tests/test_classification.py::test_negative_label_guard -x` | ❌ Wave 0 |
| CLASS-01 | Non-contiguous labels `[0, 2]` raise `ValueError` | unit | `pytest tests/test_classification.py::test_noncontiguous_label_guard -x` | ❌ Wave 0 |
| CLASS-01 | `train_accuracy` is between 0 and 1 | unit | `pytest tests/test_classification.py::test_elastic_multinomial_accuracy_range -x` | ❌ Wave 0 |

### Build Gate

Before any test:
```bash
maturin develop   # must exit 0 with no clippy errors
```

### Sampling Rate

- **Per task commit:** `pytest tests/test_pace_fpca.py tests/test_classification.py -x`
- **Per wave merge:** `pytest tests/ -x`
- **Phase gate:** Full suite green before moving to Phase 39

### Wave 0 Gaps

- [ ] `tests/test_pace_fpca.py` — covers PACE-01 + PACE-02 (all rows above)
- [ ] `tests/test_classification.py` — extend existing (add elastic_multinomial rows above)
- [ ] `src/pace_fpca_mod.rs` — the new Rust module file
- [ ] Build passes: `maturin develop` exits 0

*(existing `tests/test_classification.py` not found in test listing — may be under `test_basic.py` or not exist; confirm at execution start.)*

---

## Security Domain

This phase introduces no networked endpoints, credential handling, or file I/O. ASVS categories V2/V3/V4/V6 are not applicable. V5 input validation applies — all degenerate inputs are covered by the `ValueError` guards listed in the test map.

---

## Sources

### Primary (HIGH confidence — read directly from v0.23.0 source this session)

- `fdars-core v0.23.0:fdars-core/src/irreg_fdata/mod.rs` — `IrregFdata` struct fields (`offsets`, `argvals`, `values`, `rangeval`), `from_lists` constructor (lines 47-97), `from_flat` constructor (lines 99-127), `n_obs`/`n_points`/`get_obs`/`total_points`/`obs_counts`/`min_obs`/`max_obs` accessors
- `fdars-core v0.23.0:fdars-core/src/pace_fpca.rs` — `PaceFpcaConfig` struct (lines 51-83 incl. Default), `PaceFpcaResult` struct (lines 97-120), `pace_fpca` function signature (line 272), all validation error conditions (lines 276-356), `actual_ncomp` truncation logic (line 397), NaN-mean guard (lines 369-384)
- `fdars-core v0.23.0:fdars-core/src/elastic_regression/logistic.rs` — `ElasticLogisticResult` struct (lines 11-33), `elastic_multinomial` function signature (lines 252-260), `ElasticMultinomialResult` struct (lines 214-227), label contiguity validation (lines 279-304), `predict_elastic_multinomial` (lines 390-440)
- `fdars-core v0.23.0:fdars-core/src/lib.rs` — confirmed `pub use irreg_fdata::{IrregFdata, KernelType}` and `pub use pace_fpca::{pace_fpca, PaceFpcaConfig, PaceFpcaResult}` and `elastic_multinomial`/`predict_elastic_multinomial` re-exports
- `pyfda:src/convert.rs:1-93` — all converter functions and signatures
- `pyfda:src/lib.rs:1-63` — `register_submodule!` macro, current 19 submodule registrations
- `pyfda:src/classification_mod.rs:1-279` — existing classification bindings, `numpy1d_to_usize_vec` usage, `register` function
- `pyfda:src/inference_mod.rs:32-41` (test_result_to_pydict pattern), `src/inference_mod.rs:523-542` (oneway_anova_vstat CR-01 guard pattern)
- `pyfda:python/fdars/__init__.py:1-89` — `_submodule_names` tuple, submodule registration loop

### Secondary (HIGH confidence — milestone research, read this session or prior session)

- `.planning/research/FEATURES.md` — Group B capability specifications, `PaceFpcaConfig`/`PaceFpcaResult` field tables, `ElasticMultinomialResult` field table
- `.planning/research/ARCHITECTURE.md` — converter map, `#[non_exhaustive]` anti-pattern list, `class_models` omission decision
- `.planning/research/PITFALLS.md` — `IrregFdata` dense-array pitfall, `eigenfunctions` transposition pitfall, `actual_ncomp` truncation pitfall, `elastic_multinomial` CR-01 label guard pitfall

---

## Metadata

**Confidence breakdown:**
- IrregFdata binding approach: HIGH — struct read verbatim; `#[pyclass]` decision grounded in source
- PaceFpcaConfig/Result fields: HIGH — read verbatim from v0.23.0 source
- ElasticMultinomialResult fields: HIGH — read verbatim from v0.23.0 source
- PyO3 0.28 `#[pyclass]` borrow form: MEDIUM — training knowledge; 3 specific idioms flagged as [ASSUMED] for execution-start verification
- elastic_multinomial default kwargs: LOW — core has no config struct; pyfda binding chooses values

**Research date:** 2026-08-20
**Valid until:** 2026-09-20 (stable; pinned to v0.23.0 tag)
