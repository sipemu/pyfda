# Phase 69: Fréchet Regression & Density FDA — Research

**Researched:** 2026-09-03
**Domain:** PyO3 binding — fdars-core 0.33 `frechet` module + `density_fda` module + `convert.rs` refactor
**Confidence:** HIGH — all findings read directly from 0.33 registry source and existing project files this session

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Density-default + common spaces.**
  - `frechet_global_reg`, `frechet_local_reg`, `frechet_anova`: bind the **non-generic
    density/distribution-response** variants (Petersen–Müller quantile averaging; clean
    numpy 2D I/O) as the default path.
  - `frechet_mean` (generic-only) + the string-dispatch backend: support the **3
    statistically-common spaces — SPD (covariance/PD matrices), spherical (directional /
    unit-norm data), correlation (correlation matrices)**. Each gets its own numpy input
    contract + validation (SPD symmetric-PD; spherical unit-norm; correlation unit-diagonal).
  - **Skip `network` + `point_process`** metric spaces (niche graph/event spaces with
    awkward bespoke input formats) — deferred to a dedicated later phase.
  - String dispatch: a `space_from_str`-style match with an **`Err`-returning wildcard arm**
    listing the valid backend names (`"spd"`, `"spherical"`, `"correlation"`) — mandatory
    for the metric-space selection (locked STATE enum-arm decision generalizes here).

### Claude's Discretion (convention-driven)
- **FRE-03 refactor shape:** Fully relocate + rename: move `extract_list_of_vecs` from
  `pace_fpca_mod.rs` into `convert.rs` as `pub fn extract_ragged_vecs`, update the single
  pace_fpca call site to import it. No re-export shim (single source of truth).
  Preserve/extend the non-uniform per-observation-length validation and add a unit/behavior
  test on ragged input.
- **Return shape:** documented PyDict per result struct; confirm exact 0.33 field names
  against registry source before writing converters.
- **Transposition + argvals:** 2D matrix inputs via `convert::numpy2d_to_fdmatrix`;
  ragged/density inputs via the new `extract_ragged_vecs`; non-square fixtures where 2D.
- **density_fda functions** take `&[f64]` / vecs (vals, argvals) — route through the ragged
  helper / 1D converters; `normalize_density` returns a Vec<f64> (naked 1D array), the
  others return PyDicts (confirm per-function in research).
- **Determinism:** expose `seed` with a fixed default where an upstream fn takes one.
- **Error handling:** `FdarError` → `PyValueError` via `convert::to_pyresult`.

### Deferred Ideas (OUT OF SCOPE)
- `network` + `point_process` metric spaces for Fréchet — dedicated later phase.
- FRE-RUN-01: promote the `frechet` advisor aspect from diagnostics-only to `_RUNNABLE_METHODS` (future).
- Advisor `frechet` aspect (ADV-01, diagnostics-only) — Phase 72.
- Fréchet docs page (DOCS-01) — Phase 73.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FRE-01 | New `fdars.frechet` submodule — `frechet_mean`, `frechet_global_reg`, `frechet_local_reg`, `frechet_anova` exposed (metric-space backend chosen via string dispatch, `Err` fallback arm), each returning a documented PyDict | §3 exact signatures; §4 result-struct fields; §5 space-dispatch patterns; §9 registration |
| FRE-02 | New `fdars.density_fda` submodule — `lqd_transform` / `inverse_lqd`, `lqd_fpca`, `wasserstein_barycenter`, `normalize_density` exposed | §6 exact density_fda signatures; §7 density result fields; §9 registration |
| FRE-03 | Shared ragged-list helper (`extract_ragged_vecs`) factored into `src/convert.rs` (out of `pace_fpca_mod.rs`); validated on non-uniform per-observation lengths | §2 full refactor spec; §8 test architecture |
</phase_requirements>

---

## Summary

Phase 69 delivers two new submodules plus a prerequisite refactor of the shared ragged-list
conversion helper. The three deliverables are disjoint enough to parallelize the two new
module files after the `convert.rs` refactor lands.

**Group A (convert.rs refactor — FRE-03, sequenced first):** Relocate the private
`extract_list_of_vecs` function from `src/pace_fpca_mod.rs` (lines 33–65) to
`src/convert.rs` as `pub fn extract_ragged_vecs`. It accepts a `PyList` of 1-D numpy
arrays, plain Python lists, or tuples per curve, validates per-curve lengths, and returns
`Vec<Vec<f64>>`. Both the density_fda and frechet metric-space bindings consume it. The
pace_fpca_mod.rs call site switches to `crate::convert::extract_ragged_vecs`.

**Group B (frechet submodule — FRE-01):** Three density-default functions
(`frechet_global_reg`, `frechet_local_reg`, `frechet_anova`) take numpy 2D matrices via the
standard `numpy2d_to_fdmatrix` path. `frechet_mean` is the only generic function; it uses a
`space_from_str` string-dispatch match selecting among `SpdMatrixSpace`, `SphericalSpace`,
`CorrelationMatrixSpace` — each with its own input marshalling from Python. `frechet_mean`
returns a 1D numpy array for density (the default space), or a 1D array (for SPD/correlation
objects) or 1D array (for spherical unit vectors). See §5 for per-space numpy contracts.

**Group C (density_fda submodule — FRE-02):** Five functions, all taking `&[f64]` slices
or an FdMatrix. `normalize_density` returns a naked numpy 1D array. The remaining four
return PyDicts. `lqd_fpca` exposes a nested `LqdFpcaResult` with a `FpcaResult` sub-struct;
the binding exposes all `FpcaResult` fields flattened into the top-level dict (excluding
`centered` per convention), plus `fve`.

**Critical finding:** All result-struct field names are read verbatim from the 0.33 registry
source. `FrechetGlobalRegResult`, `FrechetLocalRegResult`, `FrechetAnovaResult`, and
`LqdFpcaResult` are all `#[non_exhaustive]` — field-by-field access only (no struct literal
construction by binding code). The signed-weight note in the regression doc comments is an
important correctness constraint: `frechet_global_reg` and `frechet_local_reg` use the
sort-based isotonic projection (NOT `wasserstein_barycenter`) because Petersen–Müller weights
can be **negative**.

**Primary recommendation:** Wave the refactor (FRE-03) first as its own plan wave, then
parallelize the frechet_mod.rs and density_fda_mod.rs as separate Wave-2 plans.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| FRE-03 refactor (`extract_ragged_vecs`) | PyO3 boundary (convert.rs) | — | Shared conversion utility consumed at the Python/Rust boundary |
| `frechet_global_reg` / `frechet_local_reg` (density-default) | API / Backend (Rust) | — | 2D FdMatrix I/O; pure computation |
| `frechet_anova` (density-default) | API / Backend (Rust) | — | Permutation test; seeded RNG |
| `frechet_mean` (generic-dispatch) | API / Backend (Rust) | PyO3 boundary | Per-space object marshalling in binding; Rust computes |
| Space construction (SPD/spherical/correlation) | PyO3 boundary | — | Binding unmarshals numpy → `Vec<f64>` objects; dispatches to space |
| `normalize_density`, `lqd_transform`, `inverse_lqd` | API / Backend (Rust) | — | Pure 1D-vector operations; no FdMatrix involved |
| `wasserstein_barycenter` | API / Backend (Rust) | — | FdMatrix (n densities × m grid points) I/O |
| `lqd_fpca` | API / Backend (Rust) | — | FdMatrix + SVD; returns LqdFpcaResult |
| PyDict assembly + numpy conversion | PyO3 boundary | — | Row-major ↔ column-major in convert.rs |
| Submodule registration | Module registry (lib.rs + `__init__.py`) | — | Standard macro + name-list pattern |

---

## Section 1: Research Gap Status

STATE.md flagged: "0.31/0.32 changelog absent — confirm result-struct/config field names
against 0.33 source per binding group before writing PyDict converters."

**Status: RESOLVED for Phase 69.** All result struct definitions have been read verbatim from
the 0.33 registry source this session:

[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/mod.rs:53-109]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/regression.rs:236-349]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/anova.rs:124-204]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/mean.rs:40-54]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/spaces/spd.rs:46-75]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/spaces/spherical.rs:31-49]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/frechet/spaces/correlation.rs:25-43]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/density_fda.rs:88-100, 127-624]

---

## Section 2: FRE-03 Refactor — Full Specification

### Current state

`extract_list_of_vecs` is private to `pace_fpca_mod.rs` at lines 33–65.
[VERIFIED: src/pace_fpca_mod.rs:33-65]

Verbatim current function (this is exactly what gets relocated and renamed):

```rust
fn extract_list_of_vecs(list: &Bound<'_, PyList>) -> PyResult<Vec<Vec<f64>>> {
    list.iter()
        .enumerate()
        .map(|(i, item)| {
            if let Ok(arr) = item.extract::<numpy::PyReadonlyArray1<f64>>() {
                Ok(arr.as_array().to_vec())
            } else if let Ok(seq) = item.cast::<PyList>() {
                seq.iter()
                    .map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else if let Ok(tup) = item.cast::<PyTuple>() {
                tup.iter()
                    .map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else {
                let type_name = item.get_type().name()
                    .map(|s| s.to_string())
                    .unwrap_or_else(|_| "?".to_string());
                Err(PyValueError::new_err(format!(
                    "irreg_fdata_from_lists: element [{}] is not a 1-D numpy array or \
                     list of floats; got {}", i, type_name
                )))
            }
        })
        .collect()
}
```

### Relocated + renamed form in `src/convert.rs`

```rust
use pyo3::types::{PyList, PyTuple};
use pyo3::exceptions::PyValueError;

/// Extract a Python list of 1-D arrays / lists / tuples into a Vec<Vec<f64>>.
///
/// Accepts each element as:
/// - A 1-D numpy f64 array (zero-copy via PyReadonlyArray1)
/// - A plain Python list of floats
/// - A Python tuple of floats
///
/// Error messages use `caller_name` to produce context-specific messages
/// (e.g. "frechet_mean: element [2] ..." vs "irreg_fdata_from_lists: element [2] ...").
pub fn extract_ragged_vecs(
    list: &Bound<'_, PyList>,
    caller_name: &str,
) -> PyResult<Vec<Vec<f64>>> {
    list.iter()
        .enumerate()
        .map(|(i, item)| {
            if let Ok(arr) = item.extract::<numpy::PyReadonlyArray1<f64>>() {
                Ok(arr.as_array().to_vec())
            } else if let Ok(seq) = item.cast::<PyList>() {
                seq.iter().map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else if let Ok(tup) = item.cast::<PyTuple>() {
                tup.iter().map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else {
                let type_name = item.get_type().name()
                    .map(|s| s.to_string())
                    .unwrap_or_else(|_| "?".to_string());
                Err(PyValueError::new_err(format!(
                    "{caller_name}: element [{i}] is not a 1-D numpy array or \
                     list of floats; got {type_name}"
                )))
            }
        })
        .collect()
}
```

**Signature change from the original:** Adds a `caller_name: &str` parameter so that error
messages are context-specific. The original hard-coded `"irreg_fdata_from_lists"` in the
message.

### Call-site update in `src/pace_fpca_mod.rs`

Remove the private `fn extract_list_of_vecs(...)` definition (lines 33–65). Replace each
call to `extract_list_of_vecs(av_list)?` with
`crate::convert::extract_ragged_vecs(av_list, "irreg_fdata_from_lists")?` and similarly for
`vl_list`.

**Current call sites in pace_fpca_mod.rs:**
[VERIFIED: src/pace_fpca_mod.rs:127-128]
```rust
let av_vecs = extract_list_of_vecs(av_list)?;
let vl_vecs = extract_list_of_vecs(vl_list)?;
```
Updated to:
```rust
let av_vecs = crate::convert::extract_ragged_vecs(av_list, "irreg_fdata_from_lists")?;
let vl_vecs = crate::convert::extract_ragged_vecs(vl_list, "irreg_fdata_from_lists")?;
```

**`use` changes in `pace_fpca_mod.rs`:**
- Remove `use pyo3::types::{PyDict, PyList, PyTuple};` (keep `PyDict` if still used; drop
  `PyList` and `PyTuple` if they were only needed by the helper — check remaining usages).
- The current import [VERIFIED: src/pace_fpca_mod.rs:14]:
  `use pyo3::types::{PyDict, PyList, PyTuple};`
  After refactor, `PyList` and `PyTuple` are no longer referenced in pace_fpca_mod.rs (they
  move to convert.rs). Keep `PyDict` for the dict builder. Add imports to convert.rs:
  `use pyo3::types::{PyList, PyTuple};`

**`use` changes in convert.rs:**
Add at the top (after existing imports):
```rust
use numpy::PyReadonlyArray1 as _; // already imported via the existing use line
use pyo3::types::{PyList, PyTuple};
use pyo3::exceptions::PyValueError;
```
Check existing convert.rs imports [VERIFIED: src/convert.rs:1-6]:
```rust
use fdars_core::matrix::FdMatrix;
use fdars_core::FdarError;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
```
Add: `use pyo3::types::{PyList, PyTuple};` — `PyValueError` is available via `pyo3::prelude::*`
(as `pyo3::exceptions::PyValueError`; use the explicit path in the function body).

### Additional validation to ADD in the public function

The original `extract_list_of_vecs` does **not** validate that all inner vecs have the same
length. The density_fda inputs do NOT require uniform length (density values on different grids
per observation are fine — ragged is the point). However, a calling context that DOES require
uniform length (e.g., if a future caller needs a rectangular matrix) should validate after the
call. No length uniformity check belongs inside `extract_ragged_vecs` itself — it is a
general-purpose helper.

For the frechet metric-space binding (SPD, spherical, correlation), each "object" is a single
Vec<f64> — the ragged helper is called with a 1-element-per-observation list. No length
uniformity check is needed inside the helper for these callers either (they validate object
length against `d` or `d*d` in the space's own check).

**Conclusion:** No new validation is added inside `extract_ragged_vecs`. The per-caller
validation contract is documented in the function's docstring.

### Non-uniform-length test to ADD

```rust
#[test]
fn extract_ragged_vecs_accepts_nonuniform_lengths() {
    Python::with_gil(|py| {
        // Create a Python list of two 1-D arrays of DIFFERENT lengths
        let a1 = numpy::PyArray1::from_vec(py, vec![1.0_f64, 2.0]).into_any();
        let a2 = numpy::PyArray1::from_vec(py, vec![3.0_f64, 4.0, 5.0]).into_any();
        let list = pyo3::types::PyList::new(py, [a1, a2]).unwrap();
        let result = extract_ragged_vecs(list.as_ref(), "test").unwrap();
        assert_eq!(result[0].len(), 2);
        assert_eq!(result[1].len(), 3);
    });
}
```

This test REPLACES the "validate non-uniform-length" requirement from CONTEXT.md with a
behavioral test that the helper correctly handles them (it does not reject them — that is
correct).

---

## Section 3: FRE-01 Fréchet Regression — Exact Signatures

### `frechet_global_reg` (density-default)
[VERIFIED: frechet/regression.rs:236-262]

```rust
pub fn frechet_global_reg(
    predictors: &FdMatrix,    // (n × p) scalar predictors — numpy 2D (n_obs, n_preds)
    responses: &FdMatrix,     // (n × m) density responses — numpy 2D (n_obs, n_grid)
    argvals: &[f64],          // length m — density evaluation grid
    xout: &FdMatrix,          // (n_out × p) predictor values to predict at — numpy 2D
) -> Result<FrechetGlobalRegResult, FdarError>
```

Validation (from `validate_reg_input`, frechet/regression.rs:171-213):
- `predictors.nrows() == 0` → `FdarError::InvalidDimension`
- `responses.nrows() != predictors.nrows()` → `FdarError::InvalidDimension`
- `argvals.len() != responses.ncols()` → `FdarError::InvalidDimension`
- `argvals` not strictly increasing → `FdarError::InvalidParameter`
- `xout.ncols() != predictors.ncols()` → `FdarError::InvalidDimension`

Python binding signature:
`frechet_global_reg(predictors, responses, argvals, xout)`
- `predictors`: `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- `responses`: `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- `argvals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- `xout`: `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- Returns PyDict (see §4)

**KEY CORRECTNESS NOTE:** `frechet_global_reg` uses `signed_quantile_average` (sort-based
isotonic projection), NOT `wasserstein_barycenter`, because Petersen–Müller weights can be
**negative** for extrapolation. This is by design in the upstream and must NOT be confused
with `wasserstein_barycenter`. The binding simply calls the upstream and converts the result;
no special handling is needed.

### `frechet_local_reg` (density-default)
[VERIFIED: frechet/regression.rs:317-349]

```rust
pub fn frechet_local_reg(
    predictors: &FdMatrix,    // (n × p) scalar predictors
    responses: &FdMatrix,     // (n × m) density responses
    argvals: &[f64],          // length m
    xout: &FdMatrix,          // (n_out × p)
    bandwidth: f64,           // must be > 0.0 and finite
) -> Result<FrechetLocalRegResult, FdarError>
```

Validation: same as `frechet_global_reg` plus `bandwidth <= 0.0 || !bandwidth.is_finite()`
→ `FdarError::InvalidParameter`.

Python binding signature:
`frechet_local_reg(predictors, responses, argvals, xout, bandwidth)`
- All 2D args via `numpy2d_to_fdmatrix`; `argvals` via `numpy1d_to_vec`
- `bandwidth`: `f64` (required positional — no sensible default exists for user's data scale)
- Returns PyDict (see §4)

### `frechet_anova` (density-default)
[VERIFIED: frechet/anova.rs:124-204]

```rust
pub fn frechet_anova(
    responses: &FdMatrix,      // (n × m) density responses
    argvals: &[f64],           // length m
    group_labels: &[usize],    // length n — contiguous 0..k
    n_perm: usize,             // 0 → use default 999 replications
    seed: u64,                 // RNG seed for permutation p-value
) -> Result<FrechetAnovaResult, FdarError>
```

Validation:
- `group_labels.len() != responses.nrows()` → `FdarError::InvalidDimension`
- `argvals.len() != responses.ncols()` → `FdarError::InvalidDimension`
- fewer than 2 distinct groups → `FdarError::InvalidParameter`
- group labels not contiguous 0..k → `FdarError::InvalidParameter`

Python binding signature:
`frechet_anova(responses, argvals, group_labels, n_perm=999, seed=42)`
- `responses`: `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- `argvals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- `group_labels`: `PyReadonlyArray1<'py, i64>` → `numpy1d_to_usize_vec`
- `n_perm=999`, `seed=42` as defaults (matching existing bindings like `fanova`)
- Returns PyDict (see §4)

### `frechet_mean` (generic dispatch)
[VERIFIED: frechet/mean.rs:40-54]

```rust
pub fn frechet_mean<S: MetricSpace>(
    space: &S,
    objects: &[S::Object],   // varies per space — see §5
    weights: Option<&[f64]>, // None → uniform 1/n
) -> Result<S::Object, FdarError>
```

**The generic is not object-safe** — `frechet_mean::<SpdMatrixSpace>(...)` is a monomorphized
call, not a trait object call. The binding dispatches via a match on the space string, calling
the concrete monomorphization per arm. This is the correct approach.

Python binding signature:
`frechet_mean(objects, space, argvals=None, weights=None)`
- `objects`: `&Bound<'py, PyList>` — a Python list of per-object arrays
- `space`: `&str` — one of `"spd"`, `"spherical"`, `"correlation"`; wildcard arm → `ValueError`
- `argvals`: `Option<PyReadonlyArray1<'py, f64>>` — REQUIRED for `"spd"` and `"correlation"`
  to communicate matrix dimension d (argvals.len() == d). For `"spherical"` gives d. Actually:
  **argvals is NOT needed** — `d` is inferred from the object array length (d*d for SPD/corr,
  d for spherical). Use a `d: usize` parameter instead.
- `weights`: `Option<PyReadonlyArray1<'py, f64>>` — optional, length must equal n objects

**Better binding signature after source review:**
`frechet_mean(objects, space, d, weights=None)`
- `d: usize` — ambient dimension. For SPD/correlation: objects are d×d matrices → each object
  is a (d, d) numpy array flattened to `Vec<f64>` of length d*d. For spherical: each object
  is a (d,) numpy unit vector → `Vec<f64>` of length d.
- Returns numpy 1D array of the Fréchet mean object (length d for spherical; d*d for SPD/corr,
  in column-major order matching the space's flat storage).

See §5 for per-space input marshalling.

---

## Section 4: Result Struct Fields (verbatim from 0.33 source)

### `FrechetGlobalRegResult`
[VERIFIED: frechet/mod.rs:60-67]

All three fields declared `#[non_exhaustive]`:
```
pub predicted: FdMatrix    // n_out × m densities — numpy 2D (n_out, m)
pub xout: FdMatrix         // n_out × p — numpy 2D (n_out, p) — echo of input xout
pub x_bar: Vec<f64>        // length p — column means of training predictors → numpy 1D (p,)
```
PyDict keys (3 keys): `"predicted"`, `"xout"`, `"x_bar"`

`predicted` shape: `(n_out, m)` via `fdmatrix_to_numpy2d`. Rows are predicted densities.
`xout` shape: `(n_out, p)` — this echoes the input; exposing it is useful for callers.

### `FrechetLocalRegResult`
[VERIFIED: frechet/mod.rs:74-81]

```
pub predicted: FdMatrix    // n_out × m — numpy 2D (n_out, m)
pub xout: FdMatrix         // n_out × p — numpy 2D (n_out, p)
pub bandwidth: f64         // the bandwidth used → float
```
PyDict keys (3 keys): `"predicted"`, `"xout"`, `"bandwidth"`

### `FrechetAnovaResult`
[VERIFIED: frechet/mod.rs:90-109]

```
pub statistic: f64                   // Dubey–Müller Tₙ statistic → float
pub p_value_asymptotic: f64          // χ²(k−1) p-value (secondary) → float
pub p_value_permutation: f64         // seeded-permutation p-value (primary) → float
pub n_perm: usize                    // number of permutations used → int
pub group_frechet_variances: Vec<f64> // V̂ₗ per group, length k → numpy 1D (k,)
pub pooled_frechet_variance: f64     // V̂ₚ → float
pub fn_statistic: f64                // Fₙ variance-contrast component → float
pub un_statistic: f64                // Uₙ pairwise-dispersion component → float
pub group_labels: Vec<usize>         // contiguous 0..k echo → usize_vec_to_numpy1d → numpy 1D i64
```
PyDict keys (9 keys): `"statistic"`, `"p_value_asymptotic"`, `"p_value_permutation"`,
`"n_perm"`, `"group_frechet_variances"`, `"pooled_frechet_variance"`, `"fn_statistic"`,
`"un_statistic"`, `"group_labels"`

Conversion for `group_labels: Vec<usize>`:
```rust
dict.set_item("group_labels", usize_vec_to_numpy1d(py, result.group_labels))?;
```
`usize_vec_to_numpy1d` [VERIFIED: src/convert.rs:76-78] already exists in convert.rs.

### `frechet_mean` return type (per space)

`frechet_mean` returns `S::Object` where `S::Object = Vec<f64>` for all three implemented
spaces. The result is:
- **SPD**: `Vec<f64>` length d*d (column-major flat d×d matrix) → `vec_to_numpy1d` gives a
  1D (d*d,) array. Consider reshaping in the binding to (d, d) 2D for usability.
- **Spherical**: `Vec<f64>` length d (unit vector) → `vec_to_numpy1d` gives 1D (d,) array.
- **Correlation**: `Vec<f64>` length d*d (column-major) → same as SPD, reshape to (d, d).

**Recommendation:** For SPD and correlation, return a 2D (d, d) numpy array reshaped from the
flat column-major result. For spherical, return 1D (d,) numpy array. Use the `PyArray2`/
`PyArray1` return path. The simplest approach: return `PyAny` and branch by space type.

---

## Section 5: Per-Space Input Marshalling (frechet_mean generic dispatch)

### `SpdMatrixSpace`
[VERIFIED: frechet/spaces/spd.rs:46-75]

```rust
pub struct SpdMatrixSpace { pub d: usize, pub metric: SpdMetric }
impl SpdMatrixSpace {
    pub fn new(d: usize, metric: SpdMetric) -> Result<Self, FdarError>
}
```

`SpdMetric` [VERIFIED: frechet/spaces/spd.rs:32-39]:
```
pub enum SpdMetric { Frobenius, Power(f64), LogCholesky }
// #[non_exhaustive]
```

For Phase 69 (CONTEXT.md: "SPD spaces"), default to `SpdMetric::Frobenius`. The metric
parameter is an implementation detail the Python binding can hide initially (default Frobenius,
no metric string dispatch needed unless a later phase extends it).

**Object representation:** One SPD matrix = a (d, d) numpy array (symmetric positive-definite).
The binding must flatten it to a column-major `Vec<f64>` of length d*d.

**Python → Rust marshalling:**
```rust
// Each object in the Python list is a (d, d) numpy 2D array
// Flatten to column-major Vec<f64> for SpdMatrixSpace
fn spd_object_from_numpy<'py>(
    arr: PyReadonlyArray2<'py, f64>,
    d: usize,
    i: usize,
) -> PyResult<Vec<f64>> {
    let (nrows, ncols) = arr.as_array().dim();
    if nrows != d || ncols != d {
        return Err(PyValueError::new_err(format!(
            "frechet_mean(space='spd'): object [{i}] must be a ({d}, {d}) array, \
             got ({nrows}, {ncols})"
        )));
    }
    // Column-major from numpy row-major: element (i,j) → index i + j*d
    let a = arr.as_array();
    let mut flat = vec![0.0f64; d * d];
    for r in 0..d {
        for c in 0..d {
            flat[r + c * d] = a[[r, c]];
        }
    }
    Ok(flat)
}
```

**Validation to perform in binding (not in Rust upstream):**
- Symmetric: for i,j: `|M[i,j] - M[j,i]| < 1e-8` — warn or error if not symmetric.
- Positive-definite: the space itself validates via Cholesky for LogCholesky metric;
  Frobenius does not validate PD. For Phase 69 (Frobenius default), no PD check required
  by upstream — but the binding SHOULD check the diagonal is positive: for i in 0..d:
  `flat[i + i*d] > 0.0`. Full Cholesky check is too expensive for the binding; a diagonal
  positivity check catches the most common mistakes.

**Space construction:** `SpdMatrixSpace::new(d, SpdMetric::Frobenius)?`

**Result marshalling:** `Vec<f64>` length d*d → reshape to (d, d) numpy 2D:
```rust
PyArray2::from_vec2(py,
    &(0..d).map(|r| (0..d).map(|c| result[r + c * d]).collect()).collect::<Vec<_>>()
).unwrap()
```

### `SphericalSpace`
[VERIFIED: frechet/spaces/spherical.rs:31-49]

```rust
pub struct SphericalSpace { pub d: usize }
impl SphericalSpace { pub fn new(d: usize) -> Result<Self, FdarError> }
```

**Object representation:** One spherical object = a unit vector of length d — a (d,) numpy 1D
array.

**Python → Rust marshalling:**
```rust
fn spherical_object_from_numpy<'py>(
    arr: PyReadonlyArray1<'py, f64>,
    d: usize,
    i: usize,
) -> PyResult<Vec<f64>> {
    let v = arr.as_array().to_vec();
    if v.len() != d {
        return Err(PyValueError::new_err(format!(
            "frechet_mean(space='spherical'): object [{i}] must have length {d}, got {}", v.len()
        )));
    }
    Ok(v)
}
```

**Validation in binding:** check unit norm `|‖v‖ - 1| < 1e-6` for each object. This is a
contract the upstream does NOT enforce per call (it documents that callers must supply unit
vectors). A norm check is fast and catches the most common mistake.

**Space construction:** `SphericalSpace::new(d)?`

**Result marshalling:** `Vec<f64>` length d → `vec_to_numpy1d(py, result)` → numpy 1D (d,).

**Input format for Python:** the `objects` parameter accepts a Python list where each element
is a 1-D numpy array of length d. Use `extract_ragged_vecs` to get `Vec<Vec<f64>>`, then
validate each inner vec's length and norm.

### `CorrelationMatrixSpace`
[VERIFIED: frechet/spaces/correlation.rs:25-43]

```rust
pub struct CorrelationMatrixSpace { pub d: usize }
impl CorrelationMatrixSpace { pub fn new(d: usize) -> Result<Self, FdarError> }
```

**Object representation:** One correlation matrix = a d×d numpy 2D array with unit diagonal
and values in [-1, 1]. Stored as flat column-major `Vec<f64>` length d*d.

**Python → Rust marshalling:** identical to SPD (use the same flattening loop; same `d*d`
shape check).

**Validation in binding:**
- Diagonal entries == 1.0: for i in 0..d: `|flat[i + i*d] - 1.0| < 1e-8`. A non-unit
  diagonal means the matrix is not a correlation matrix.
- Symmetry: same check as SPD.

**Space construction:** `CorrelationMatrixSpace::new(d)?`

**Result marshalling:** `Vec<f64>` length d*d → reshape to (d, d) numpy 2D (same as SPD).

### `space_from_str` match pattern

```rust
fn frechet_mean_dispatch<'py>(
    py: Python<'py>,
    objects_list: &Bound<'py, PyList>,
    space: &str,
    d: usize,
    weights_opt: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyAny>> {
    let weights: Option<Vec<f64>> = weights_opt.map(|w| numpy1d_to_vec(w));
    let weights_ref: Option<&[f64]> = weights.as_deref();

    match space {
        "spd" => {
            let objects: Vec<Vec<f64>> = objects_list.iter().enumerate()
                .map(|(i, item)| {
                    let arr = item.extract::<PyReadonlyArray2<f64>>()?;
                    spd_object_from_numpy(arr, d, i)
                })
                .collect::<PyResult<_>>()?;
            let spdspace = to_pyresult(
                fdars_core::frechet::SpdMatrixSpace::new(d, fdars_core::frechet::SpdMetric::Frobenius)
            )?;
            let mean = to_pyresult(fdars_core::frechet::frechet_mean(&spdspace, &objects, weights_ref))?;
            // Reshape flat column-major d*d to (d,d) numpy 2D
            Ok(PyArray2::from_vec2(py,
                &(0..d).map(|r| (0..d).map(|c| mean[r + c * d]).collect()).collect::<Vec<_>>()
            ).unwrap().into_any())
        }
        "spherical" => {
            let objects: Vec<Vec<f64>> = objects_list.iter().enumerate()
                .map(|(i, item)| {
                    let arr = item.extract::<PyReadonlyArray1<f64>>()?;
                    spherical_object_from_numpy(arr, d, i)
                })
                .collect::<PyResult<_>>()?;
            // Unit-norm validation
            for (i, obj) in objects.iter().enumerate() {
                let norm: f64 = obj.iter().map(|x| x * x).sum::<f64>().sqrt();
                if (norm - 1.0).abs() > 1e-6 {
                    return Err(PyValueError::new_err(format!(
                        "frechet_mean(space='spherical'): object [{i}] has norm {norm:.6}, \
                         expected unit vector (|norm - 1| < 1e-6)"
                    )));
                }
            }
            let sphspace = to_pyresult(fdars_core::frechet::SphericalSpace::new(d))?;
            let mean = to_pyresult(fdars_core::frechet::frechet_mean(&sphspace, &objects, weights_ref))?;
            Ok(vec_to_numpy1d(py, mean).into_any())
        }
        "correlation" => {
            let objects: Vec<Vec<f64>> = objects_list.iter().enumerate()
                .map(|(i, item)| {
                    let arr = item.extract::<PyReadonlyArray2<f64>>()?;
                    corr_object_from_numpy(arr, d, i)
                })
                .collect::<PyResult<_>>()?;
            let corrspace = to_pyresult(fdars_core::frechet::CorrelationMatrixSpace::new(d))?;
            let mean = to_pyresult(fdars_core::frechet::frechet_mean(&corrspace, &objects, weights_ref))?;
            Ok(PyArray2::from_vec2(py,
                &(0..d).map(|r| (0..d).map(|c| mean[r + c * d]).collect()).collect::<Vec<_>>()
            ).unwrap().into_any())
        }
        _ => Err(PyValueError::new_err(format!(
            "space must be 'spd', 'spherical', or 'correlation', got '{space}'"
        ))),
    }
}
```

The wildcard arm lists all valid names — mandatory per locked STATE decision.

**NOTE:** `SpdMetric` is `#[non_exhaustive]` [VERIFIED: frechet/spaces/spd.rs:32], so the
binding can only use it via `SpdMetric::Frobenius` (the default). `SpdMetric::Power` and
`SpdMetric::LogCholesky` are still available as named variants — they are just not exposed
as a Python parameter in Phase 69.

---

## Section 6: FRE-02 Density FDA — Exact Signatures

### `normalize_density`
[VERIFIED: density_fda.rs:127-161]

```rust
pub fn normalize_density(vals: &[f64], argvals: &[f64]) -> Result<Vec<f64>, FdarError>
```

Python binding signature: `normalize_density(vals, argvals)`
- `vals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec` → `&[f64]`
- `argvals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec` → `&[f64]`
- **Returns: naked numpy 1D array** (NOT a PyDict) — matches CONTEXT.md convention for
  single-array returns.
- Returns `vec_to_numpy1d(py, result)`.

Validation upstream:
- `vals.len() != argvals.len()` → `FdarError::InvalidDimension`
- `argvals.len() < 2` → `FdarError::InvalidParameter`
- `argvals` not strictly increasing → `FdarError::InvalidParameter`
- any value `< 0.0` → `FdarError::InvalidParameter`
- integral `< 1e-15` → `FdarError::InvalidParameter`

### `lqd_transform`
[VERIFIED: density_fda.rs:201-271]

```rust
pub fn lqd_transform(
    density: &[f64],
    argvals: &[f64],
    n_quantile_pts: Option<usize>,
) -> Result<Vec<f64>, FdarError>
```

Python binding signature: `lqd_transform(density, argvals, n_quantile_pts=None)`
- `density`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- `argvals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- `n_quantile_pts`: `Option<usize>` → default None (upstream applies `argvals.len().max(101)`)
- **Returns: naked numpy 1D array** (the LQD ψ values on the uniform quantile grid).
- Returns `vec_to_numpy1d(py, result)`.

`lqd_transform` requires **strictly positive** density (not just non-negative) — this is
stricter than `normalize_density`. Upstream error: `FdarError::InvalidParameter` if any
`density[i] <= 0.0`.

### `inverse_lqd`
[VERIFIED: density_fda.rs:301-383]

```rust
pub fn inverse_lqd(
    psi: &[f64],
    t_grid: &[f64],
    target_argvals: &[f64],
) -> Result<Vec<f64>, FdarError>
```

Python binding signature: `inverse_lqd(psi, t_grid, target_argvals)`
- All three: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- **Returns: naked numpy 1D array** (the reconstructed density on `target_argvals`).
- Returns `vec_to_numpy1d(py, result)`.

### `wasserstein_barycenter`
[VERIFIED: density_fda.rs:407-535]

```rust
pub fn wasserstein_barycenter(
    density_matrix: &FdMatrix,    // (n × m) — n densities, m grid points
    argvals: &[f64],              // length m
    weights: Option<&[f64]>,      // length n, summing to 1; None → uniform 1/n
) -> Result<Vec<f64>, FdarError>
```

Python binding signature: `wasserstein_barycenter(density_matrix, argvals, weights=None)`
- `density_matrix`: `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- `argvals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- `weights`: `Option<PyReadonlyArray1<'py, f64>>` → `Option<Vec<f64>>` (same pattern as
  `optional_1d` pattern elsewhere: `.map(numpy1d_to_vec)`)
- **Returns: naked numpy 1D array** (the Wasserstein Fréchet mean density, length m).
- Returns `vec_to_numpy1d(py, result)`.

### `lqd_fpca`
[VERIFIED: density_fda.rs:563-624]

```rust
pub fn lqd_fpca(
    density_matrix: &FdMatrix,    // (n × m) — n densities, m grid points
    argvals: &[f64],              // length m
    ncomp: usize,                 // number of PCs to retain (≥ 1)
    n_quantile_pts: Option<usize>, // LQD quantile grid length; None → argvals.len().max(101)
) -> Result<LqdFpcaResult, FdarError>
```

Python binding signature: `lqd_fpca(density_matrix, argvals, ncomp=3, n_quantile_pts=None)`
- `density_matrix`: `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- `argvals`: `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- `ncomp=3`, `n_quantile_pts=None` as defaults
- **Returns PyDict** (see §7).

---

## Section 7: Density FDA Result Fields

### `normalize_density`, `lqd_transform`, `inverse_lqd`, `wasserstein_barycenter` returns

All four return a naked numpy 1D array (NOT PyDict). This is consistent with the design
decision in CONTEXT.md and with single-array transforms throughout the codebase (e.g.,
`functional_difference` in fts_mod.rs returns a naked array).

### `LqdFpcaResult`
[VERIFIED: density_fda.rs:88-100]

```
pub fpca: FpcaResult    // FPCA result in LQD space (see FpcaResult fields below)
pub fve: Vec<f64>       // fraction of variance explained, cumulative → numpy 1D
```

`FpcaResult` fields [VERIFIED: regression.rs:49-62]:
```
pub singular_values: Vec<f64>   // length ncomp → numpy 1D
pub rotation: FdMatrix          // m × ncomp loadings → numpy 2D (m, ncomp)
pub scores: FdMatrix            // n × ncomp scores → numpy 2D (n, ncomp)
pub mean: Vec<f64>              // mean LQD function, length n_q → numpy 1D
pub centered: FdMatrix          // n × n_q centered LQD data — INTENTIONALLY NOT EXPOSED
pub weights: Vec<f64>           // integration weights — INTENTIONALLY NOT EXPOSED (internal)
```

**Convention:** Expose `rotation` as `"loadings"` (clearer for Python users — matching the
existing `pace_fpca` convention which uses `"eigenfunctions"`, not `"rotation"`). Expose
`singular_values` directly. Omit `centered` and `weights` (internal SVD state).

PyDict keys for `lqd_fpca` (6 keys):
```
"mean"             → vec_to_numpy1d(py, result.fpca.mean)          # numpy 1D (n_q,)
"singular_values"  → vec_to_numpy1d(py, result.fpca.singular_values) # numpy 1D (ncomp,)
"loadings"         → fdmatrix_to_numpy2d(py, &result.fpca.rotation) # numpy 2D (n_q, ncomp)
"scores"           → fdmatrix_to_numpy2d(py, &result.fpca.scores)   # numpy 2D (n, ncomp)
"fve"              → vec_to_numpy1d(py, result.fve)                  # numpy 1D (ncomp,)
"ncomp"            → result.fpca.scores.ncols() as i64              # int (actual components)
```

**NOTE on `rotation` (FdMatrix) shape:** `FpcaResult.rotation` is `(m × ncomp)` in FdMatrix
(nrows=m=n_q, ncols=ncomp). `fdmatrix_to_numpy2d` returns numpy `(m, ncomp)`. Column k is
the k-th loading/eigenfunction. Consistent with `pace_fpca` which exposes `eigenfunctions`
as `(m, ncomp)` [VERIFIED: src/pace_fpca_mod.rs:174].

---

## Section 8: Registration Mechanics

### New files
- `src/frechet_mod.rs` — all frechet bindings
- `src/density_fda_mod.rs` — all density_fda bindings

### Edit 1: `src/lib.rs`
[VERIFIED: src/lib.rs:1-69]

Add after line 30 (`mod scalar_on_function_mod;`):
```rust
mod frechet_mod;
mod density_fda_mod;
```

Add after line 66 (`register_submodule!(m, "scalar_on_function", scalar_on_function_mod::register);`):
```rust
register_submodule!(m, "frechet", frechet_mod::register);
register_submodule!(m, "density_fda", density_fda_mod::register);
```

### Edit 2: `python/fdars/__init__.py`
[VERIFIED: python/fdars/__init__.py:36-59]

Add after line 58 (`"scalar_on_function",  # Phase 68 ...`):
```python
"frechet",      # Phase 69 — Fréchet regression & mean over metric spaces
"density_fda",  # Phase 69 — Density FDA: LQD transform, Wasserstein barycenter, FPCA
```

Also update the module docstring (line 21) to add:
```python
- Fréchet regression (global, local, ANOVA) and Fréchet mean over metric spaces
- Density functional data analysis (LQD transform, Wasserstein barycenter, density FPCA)
```

### New `src/frechet_mod.rs` skeleton

```rust
//! Fréchet regression and Fréchet mean over metric spaces (FRE-01).

use crate::convert::{
    extract_ragged_vecs, fdmatrix_to_numpy2d, numpy1d_to_vec, numpy2d_to_fdmatrix,
    to_pyresult, usize_vec_to_numpy1d, vec_to_numpy1d,
};
use numpy::{PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// [frechet_global_reg, frechet_local_reg, frechet_anova, frechet_mean bindings]

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(frechet_global_reg, m)?)?;
    m.add_function(wrap_pyfunction!(frechet_local_reg, m)?)?;
    m.add_function(wrap_pyfunction!(frechet_anova, m)?)?;
    m.add_function(wrap_pyfunction!(frechet_mean, m)?)?;
    Ok(())
}
```

### New `src/density_fda_mod.rs` skeleton

```rust
//! Density functional data analysis: LQD transform, Wasserstein barycenter, density FPCA.

use crate::convert::{
    fdmatrix_to_numpy2d, numpy1d_to_vec, numpy2d_to_fdmatrix,
    to_pyresult, vec_to_numpy1d,
};
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::PyDict;

// [normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter, lqd_fpca bindings]

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(normalize_density, m)?)?;
    m.add_function(wrap_pyfunction!(lqd_transform, m)?)?;
    m.add_function(wrap_pyfunction!(inverse_lqd, m)?)?;
    m.add_function(wrap_pyfunction!(wasserstein_barycenter, m)?)?;
    m.add_function(wrap_pyfunction!(lqd_fpca, m)?)?;
    Ok(())
}
```

---

## Section 9: PyDict Key Tables (for planner task actions)

### `frechet_global_reg` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"predicted"` | numpy 2D | (n_out, m) | `result.predicted` via `fdmatrix_to_numpy2d` |
| `"xout"` | numpy 2D | (n_out, p) | `result.xout` via `fdmatrix_to_numpy2d` |
| `"x_bar"` | numpy 1D | (p,) | `result.x_bar` via `vec_to_numpy1d` |

### `frechet_local_reg` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"predicted"` | numpy 2D | (n_out, m) | `result.predicted` via `fdmatrix_to_numpy2d` |
| `"xout"` | numpy 2D | (n_out, p) | `result.xout` via `fdmatrix_to_numpy2d` |
| `"bandwidth"` | float | scalar | `result.bandwidth` |

### `frechet_anova` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"statistic"` | float | scalar | `result.statistic` |
| `"p_value_asymptotic"` | float | scalar | `result.p_value_asymptotic` |
| `"p_value_permutation"` | float | scalar | `result.p_value_permutation` |
| `"n_perm"` | int | scalar | `result.n_perm as i64` |
| `"group_frechet_variances"` | numpy 1D | (k,) | `result.group_frechet_variances` |
| `"pooled_frechet_variance"` | float | scalar | `result.pooled_frechet_variance` |
| `"fn_statistic"` | float | scalar | `result.fn_statistic` |
| `"un_statistic"` | float | scalar | `result.un_statistic` |
| `"group_labels"` | numpy 1D i64 | (n,) | `result.group_labels` via `usize_vec_to_numpy1d` |

### `frechet_mean` returns:
| Space | Return type | Shape | Conversion |
|-------|-------------|-------|------------|
| `"spd"` | numpy 2D | (d, d) | flat Vec<f64> (col-major) → `PyArray2::from_vec2` |
| `"spherical"` | numpy 1D | (d,) | `vec_to_numpy1d(py, result)` |
| `"correlation"` | numpy 2D | (d, d) | same as "spd" |

### `normalize_density` returns: numpy 1D (m,) — NO PyDict
### `lqd_transform` returns: numpy 1D (n_q,) — NO PyDict
### `inverse_lqd` returns: numpy 1D (m,) — NO PyDict
### `wasserstein_barycenter` returns: numpy 1D (m,) — NO PyDict

### `lqd_fpca` returns:
| Key | Type | Shape | Source |
|-----|------|-------|--------|
| `"mean"` | numpy 1D | (n_q,) | `result.fpca.mean` |
| `"singular_values"` | numpy 1D | (ncomp,) | `result.fpca.singular_values` |
| `"loadings"` | numpy 2D | (n_q, ncomp) | `result.fpca.rotation` via `fdmatrix_to_numpy2d` |
| `"scores"` | numpy 2D | (n, ncomp) | `result.fpca.scores` via `fdmatrix_to_numpy2d` |
| `"fve"` | numpy 1D | (ncomp,) | `result.fve` |
| `"ncomp"` | int | scalar | `result.fpca.scores.ncols() as i64` |

---

## Section 10: Test Architecture

### Non-square and per-space fixtures (REQUIRED)

#### Density-default frechet functions (frechet_global_reg, frechet_local_reg, frechet_anova)

```python
import numpy as np

N, M = 40, 50   # n_obs=40 densities on m=50 grid points — non-square
N_OUT = 10      # prediction points
N_PRED = 2      # predictor dimension (p=2 multi-dim predictors)

rng = np.random.default_rng(42)
argvals = np.linspace(-3.0, 3.0, M)  # strictly increasing grid

# Density responses: n×m matrix of probability densities
# Each row is a truncated Gaussian-like density on argvals
from scipy.stats import norm
predictors = rng.standard_normal((N, N_PRED))  # (N, N_PRED) — non-square vs N
responses = np.zeros((N, M))
for i in range(N):
    mu = predictors[i, 0]  # shift density mean by first predictor
    raw = norm.pdf(argvals, loc=mu, scale=0.8)
    responses[i] = raw / np.trapz(raw, argvals)  # normalize to unit integral

xout = rng.standard_normal((N_OUT, N_PRED))  # (N_OUT, N_PRED) — all three dims differ

assert predictors.shape == (N, N_PRED)     # (40, 2)
assert responses.shape == (N, M)           # (40, 50)
assert xout.shape == (N_OUT, N_PRED)       # (10, 2)
assert N != M and N != N_OUT and M != N_OUT  # all distinct — non-square check

# frechet_anova: 3 groups
group_labels = np.array([i // (N // 3) for i in range(N)], dtype=np.int64)
group_labels = np.clip(group_labels, 0, 2)  # ensure contiguous 0,1,2
assert set(group_labels) == {0, 1, 2}
```

#### SPD matrix space (`frechet_mean(space='spd')`)

```python
D = 3   # 3×3 SPD matrices

def make_spd(rng, d):
    """Make a random d×d SPD matrix."""
    A = rng.standard_normal((d, d))
    return A @ A.T + np.eye(d) * 0.1  # guaranteed PD

objects_spd = [make_spd(rng, D) for _ in range(5)]  # list of 5 (3,3) arrays
assert all(m.shape == (D, D) for m in objects_spd)
result_spd = fdars.frechet.frechet_mean(objects_spd, space="spd", d=D)
assert result_spd.shape == (D, D)
```

#### Spherical space (`frechet_mean(space='spherical')`)

```python
D_SPH = 4  # unit vectors on S^3

def make_unit_vec(rng, d):
    v = rng.standard_normal(d)
    return v / np.linalg.norm(v)

objects_sph = [make_unit_vec(rng, D_SPH) for _ in range(6)]  # list of 6 (4,) arrays
assert all(np.abs(np.linalg.norm(v) - 1.0) < 1e-10 for v in objects_sph)
result_sph = fdars.frechet.frechet_mean(objects_sph, space="spherical", d=D_SPH)
assert result_sph.shape == (D_SPH,)
assert abs(np.linalg.norm(result_sph) - 1.0) < 1e-4  # result should also be unit-norm
```

#### Correlation matrix space (`frechet_mean(space='correlation')`)

```python
D_COR = 3  # 3×3 correlation matrices

def make_corr(rng, d):
    """Make a random d×d correlation matrix."""
    A = rng.standard_normal((d, d))
    C = A @ A.T + np.eye(d) * 0.5
    # Normalize to correlation matrix
    D_diag = np.sqrt(np.diag(C))
    return C / np.outer(D_diag, D_diag)

objects_cor = [make_corr(rng, D_COR) for _ in range(4)]
assert all(abs(m[i, i] - 1.0) < 1e-10 for m in objects_cor for i in range(D_COR))
result_cor = fdars.frechet.frechet_mean(objects_cor, space="correlation", d=D_COR)
assert result_cor.shape == (D_COR, D_COR)
assert all(abs(result_cor[i, i] - 1.0) < 1e-6 for i in range(D_COR))
```

#### Density FDA functions

```python
N_DENS, M_DENS = 20, 60  # n densities on m grid points — non-square
argvals_dens = np.linspace(0.0, 1.0, M_DENS)

# Density matrix: each row is a Beta-like density
density_matrix = np.zeros((N_DENS, M_DENS))
for i in range(N_DENS):
    a, b = 1 + i * 0.2, 2.0
    from scipy.stats import beta as sp_beta
    raw = sp_beta.pdf(argvals_dens, a, b)
    density_matrix[i] = raw / np.trapz(raw, argvals_dens)

# Single density for normalize/lqd
density_single = density_matrix[0].copy()  # (M_DENS,) array

# lqd_transform requires strictly positive values
assert (density_single > 0).all()
```

#### `extract_ragged_vecs` refactor test

```python
# Test: ragged (non-uniform length) input accepted by the helper
# (tested indirectly via irreg_fdata_from_lists — existing tests continue to pass)
av_list = [np.array([0.0, 0.5, 1.0]), np.array([0.0, 0.25, 0.5, 0.75, 1.0])]
vl_list = [np.array([1.0, 2.0, 1.0]), np.array([1.0, 1.5, 2.0, 1.5, 1.0])]
# These non-uniform lists work via irreg_fdata_from_lists (existing path)
handle = fdars.pace_fpca.irreg_fdata_from_lists(av_list, vl_list)
# No error → refactor preserved pace_fpca behavior
```

---

## Section 11: Sequence and Wave Plan

The three deliverables map naturally to waves:

**Wave 1 (prerequisite, sequential):**
- Plan P01: `convert.rs` refactor — add `extract_ragged_vecs`, update `pace_fpca_mod.rs`
  call sites, re-run existing pace_fpca tests to confirm no regression.

**Wave 2 (parallel after P01):**
- Plan P02: `src/frechet_mod.rs` — all 4 frechet functions + lib.rs + `__init__.py`
- Plan P03: `src/density_fda_mod.rs` — all 5 density_fda functions + lib.rs + `__init__.py`

These two plans edit DISJOINT files — P02 touches `src/frechet_mod.rs` + lib.rs; P03 touches
`src/density_fda_mod.rs` + lib.rs (different lines). The `__init__.py` edit adds two different
lines. The planner should sequence them as separate commits or use a merge approach.

**FND-02 guard:** Phase 67 refactored the FND-02 guard to a subset+registration invariant
that parses `_submodule_names` from the source file. Adding two new names to `_submodule_names`
and two new `register_submodule!` calls in `lib.rs` satisfies the guard automatically (new
names are a superset of the old baseline). The test does NOT need updating.

---

## Section 12: Common Pitfalls

### Pitfall 1: Signed-Weight Fréchet Regression Confusion
**What goes wrong:** Developer tries to replace the internal `signed_quantile_average` call in
`frechet_global_reg` / `frechet_local_reg` with `wasserstein_barycenter`, thinking they are
equivalent.
**Why it happens:** Both are density averaging methods. But Petersen–Müller regression weights
CAN be negative; `wasserstein_barycenter` requires non-negative weights.
**How to avoid:** The binding simply calls `fdars_core::frechet::frechet_global_reg(...)` —
no direct use of `wasserstein_barycenter`. This pitfall is an upstream implementation detail
that the binding layer doesn't control. Document in the binding's docstring that these are
signed-weight global linear weights (not Wasserstein barycenters).

### Pitfall 2: FdMatrix Column-Major vs Row-Major for Density Matrices
**What goes wrong:** `responses` shape `(n, m)` passes through `numpy2d_to_fdmatrix`.
FdMatrix is column-major with `nrows=n, ncols=m`. Upstream accesses `responses[(i, j)]` which
is observation i, grid point j — correct.
**Why it happens:** The conversion [VERIFIED: src/convert.rs:25-42] correctly handles this;
the danger is writing test assertions with the wrong shape expectation.
**How to avoid:** Assert `result["predicted"].shape == (N_OUT, M)` not `(M, N_OUT)`.

### Pitfall 3: `#[non_exhaustive]` on Result Structs
**What goes wrong:** Binding code tries struct-literal construction for `FrechetGlobalRegResult`,
`FrechetAnovaResult`, etc.
**Why it happens:** All three result structs are `#[non_exhaustive]` [VERIFIED: frechet/mod.rs:59,73,88].
**How to avoid:** Access fields by name only (no struct construction in binding code). Use
`result.predicted`, `result.xout`, etc.

### Pitfall 4: `frechet_anova` Group Label Validation
**What goes wrong:** User passes group labels [0, 1, 3] (skipping 2). Upstream raises
`FdarError::InvalidParameter` with "group labels must be contiguous 0..4".
**Why it happens:** `frechet_anova` requires contiguous labels starting at 0 (BTreeSet
invariant checked internally). A user passing scikit-learn-style labels may use non-contiguous
integers.
**How to avoid:** The binding should add a pre-validation error message clarifying the
contiguous requirement, before calling upstream. Upstream message is clear but generic.

### Pitfall 5: `SpdMetric` is `#[non_exhaustive]`
**What goes wrong:** Binding code tries to exhaustively match on `SpdMetric` in a future
extension without a wildcard arm.
**Why it happens:** `SpdMetric` is `#[non_exhaustive]` [VERIFIED: frechet/spaces/spd.rs:32].
**How to avoid:** Phase 69 only uses `SpdMetric::Frobenius` — no matching needed. Document
this for the next phase.

### Pitfall 6: `lqd_transform` Strictly Positive vs `normalize_density` Non-Negative
**What goes wrong:** User calls `lqd_transform` with an unnormalized density that has zero
tails (e.g., a histogram with zero bins). Gets `FdarError::InvalidParameter`.
**Why it happens:** `lqd_transform` requires `density[i] > 0.0` for ALL i (log(0) = -∞).
`normalize_density` only requires `vals[i] >= 0.0`.
**How to avoid:** Document clearly in the Python binding docstring. Users should call
`normalize_density` first (which validates non-negative but not strictly positive), then add
a small epsilon if needed before `lqd_transform`. This is a genuine limitation of the LQD
transform.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Density averaging | Custom quantile averaging | `frechet_global_reg` / `frechet_local_reg` upstream | Signed-weight isotonic projection edge cases |
| Wasserstein barycenter | Custom W1/W2 averaging | `wasserstein_barycenter` upstream | CDF inversion, dedup, renormalization correctness |
| LQD transform | Custom log-quantile embedding | `lqd_transform` / `inverse_lqd` upstream | Quantile interpolation + θ_ψ rescaling correctness |
| SPD geodesics | Custom matrix log/exp | `SpdMatrixSpace` Frobenius/LogCholesky | nalgebra SymmetricEigen; Cholesky factorization |
| Spherical Karcher mean | Custom Riemannian GD | `SphericalSpace::weighted_frechet_mean` | Antipodal degeneracy handling; log/exp maps |
| Permutation test | Custom permutation p-value | `frechet_anova` upstream | Seeded per-permutation RNG; bit-identical parallel path |
| Ragged list marshalling | Custom `PyList`→`Vec<Vec>` | `extract_ragged_vecs` (the FRE-03 output) | Type dispatch (array/list/tuple); error messages |

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `python -m pytest tests/test_frechet.py tests/test_density_fda.py -x` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FRE-03 | `extract_ragged_vecs` in `convert.rs`; pace_fpca tests still pass | unit | `python -m pytest tests/test_pace_fpca.py -x` | ✅ existing |
| FRE-03 | Non-uniform-length ragged input accepted | unit | `python -m pytest tests/test_convert.py -x` | ❌ Wave 0 |
| FRE-01 | `frechet_global_reg` returns (n_out, m) predicted + 3-key dict | unit | `python -m pytest tests/test_frechet.py::test_global_reg -x` | ❌ Wave 0 |
| FRE-01 | `frechet_local_reg` returns (n_out, m) predicted + 3-key dict | unit | `python -m pytest tests/test_frechet.py::test_local_reg -x` | ❌ Wave 0 |
| FRE-01 | `frechet_anova` returns 9-key dict + permutation p-value < 1 | unit | `python -m pytest tests/test_frechet.py::test_anova -x` | ❌ Wave 0 |
| FRE-01 | `frechet_mean(space='spd')` returns (d,d) array | unit | `python -m pytest tests/test_frechet.py::test_mean_spd -x` | ❌ Wave 0 |
| FRE-01 | `frechet_mean(space='spherical')` returns unit vector | unit | `python -m pytest tests/test_frechet.py::test_mean_spherical -x` | ❌ Wave 0 |
| FRE-01 | `frechet_mean(space='correlation')` returns (d,d) unit-diagonal | unit | `python -m pytest tests/test_frechet.py::test_mean_correlation -x` | ❌ Wave 0 |
| FRE-01 | Invalid space string → ValueError listing valid names | unit | `python -m pytest tests/test_frechet.py::test_mean_invalid_space -x` | ❌ Wave 0 |
| FRE-02 | `normalize_density` returns numpy 1D; integrates to 1 | unit | `python -m pytest tests/test_density_fda.py::test_normalize -x` | ❌ Wave 0 |
| FRE-02 | `lqd_transform` → uniform density → ψ ≡ 0 | unit | `python -m pytest tests/test_density_fda.py::test_lqd_uniform -x` | ❌ Wave 0 |
| FRE-02 | `inverse_lqd(lqd_transform(dens))` round-trips density | unit | `python -m pytest tests/test_density_fda.py::test_lqd_round_trip -x` | ❌ Wave 0 |
| FRE-02 | `wasserstein_barycenter` returns (m,) array integrating to 1 | unit | `python -m pytest tests/test_density_fda.py::test_wass_bary -x` | ❌ Wave 0 |
| FRE-02 | `lqd_fpca` returns 6-key dict; correct shapes | unit | `python -m pytest tests/test_density_fda.py::test_lqd_fpca -x` | ❌ Wave 0 |

### Wave 0 Gaps
- [ ] `tests/test_frechet.py` — covers all FRE-01 requirements
- [ ] `tests/test_density_fda.py` — covers all FRE-02 requirements
- [ ] `tests/test_convert.py` (or append to existing) — covers FRE-03 `extract_ragged_vecs`
- [ ] Existing `tests/test_pace_fpca.py` — re-run unchanged to verify FRE-03 refactor

---

## Environment Availability

Step 2.6: Skipped — Phase 69 is purely code/binding changes. The build toolchain (Rust 1.83+,
maturin, Python) was verified green in Phase 66 (DEP-01/02/03).

---

## Security Domain

Security enforcement is enabled; this is a pure scientific computation library with no
network surface, authentication, or user-controlled data access beyond numpy array inputs.
ASVS input validation (V5) applies.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `validate_reg_input` in upstream; binding pre-validates shapes/monotonicity |
| V6 Cryptography | no | — |

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Invalid numpy array shapes causing panic | Tampering | `numpy2d_to_fdmatrix` + upstream `validate_reg_input` return FdarError |
| Non-unit-norm spherical input silently corrupting results | Tampering | Binding validates `|‖v‖ - 1| < 1e-6` per object |
| Non-positive density causing log(-∞) | Tampering | Upstream validates `density[i] > 0.0` in `lqd_transform` |
| Negative weights in `wasserstein_barycenter` | Tampering | Upstream validates `w[i] >= 0.0` |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `frechet_mean` for the density (Wasserstein) space is not exposed directly — only SPD/spherical/correlation are supported via string dispatch; density-space mean is implicit in `frechet_global_reg`/`frechet_local_reg` | §3 | If user needs explicit density Fréchet mean, expose `WassersteinDensitySpace` separately |
| A2 | Exposing `"loadings"` (not `"rotation"`) as the key for `lqd_fpca` result is the right convention | §7 | Could conflict with advisor aspect expectations; check Phase 72 |
| A3 | `d: usize` is the right parameter name for `frechet_mean` (dimension of objects) | §3 | Planner may prefer `n_dim` or `dim` |

**If this table is effectively empty of HIGH-risk items:** All claims in this research were
verified or cited against the 0.33 registry source this session — no user confirmation
required before execution.

---

## Sources

### Primary (HIGH confidence)

All findings read directly from the 0.33 registry source this session:

- [VERIFIED: fdars-core-0.33.0/src/frechet/mod.rs:53-109] — `FrechetGlobalRegResult`, `FrechetLocalRegResult`, `FrechetAnovaResult` field definitions
- [VERIFIED: fdars-core-0.33.0/src/frechet/mean.rs:40-54] — `frechet_mean` signature
- [VERIFIED: fdars-core-0.33.0/src/frechet/regression.rs:236-349] — `frechet_global_reg`, `frechet_local_reg` signatures and validation
- [VERIFIED: fdars-core-0.33.0/src/frechet/anova.rs:124-204] — `frechet_anova` signature and validation
- [VERIFIED: fdars-core-0.33.0/src/frechet/spaces/spd.rs:32-75] — `SpdMatrixSpace`, `SpdMetric` definitions
- [VERIFIED: fdars-core-0.33.0/src/frechet/spaces/spherical.rs:31-49] — `SphericalSpace` definition
- [VERIFIED: fdars-core-0.33.0/src/frechet/spaces/correlation.rs:25-43] — `CorrelationMatrixSpace` definition
- [VERIFIED: fdars-core-0.33.0/src/frechet/space.rs:1-80] — `MetricSpace` trait, `WassersteinDensitySpace`
- [VERIFIED: fdars-core-0.33.0/src/density_fda.rs:88-624] — all density_fda functions + `LqdFpcaResult`
- [VERIFIED: fdars-core-0.33.0/src/regression.rs:49-62] — `FpcaResult` fields
- [VERIFIED: src/pace_fpca_mod.rs:33-65] — `extract_list_of_vecs` (function to relocate)
- [VERIFIED: src/pace_fpca_mod.rs:127-128] — call sites to update
- [VERIFIED: src/convert.rs:1-93] — existing conversion utilities
- [VERIFIED: src/lib.rs:1-69] — registration pattern
- [VERIFIED: python/fdars/__init__.py:36-94] — submodule name list

---

## Metadata

**Confidence breakdown:**
- FRE-03 refactor spec: HIGH — read source directly this session
- FRE-01 frechet signatures + result fields: HIGH — read source directly this session
- FRE-01 space marshalling patterns (per-space numpy contracts): HIGH — read space source
- FRE-02 density_fda signatures + result fields: HIGH — read source directly this session
- Registration mechanics: HIGH — existing lib.rs + __init__.py read directly

**Research date:** 2026-09-03
**Valid until:** 2026-10-03 (stable library release; 30-day window)
