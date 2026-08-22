# Phase 39: Group C — Depth / Outliers / Interval-Inference Bindings - Research

**Researched:** 2026-08-21
**Domain:** PyO3 binding layer — `depth_mod.rs`, `outliers_mod.rs`, `inference_mod.rs`
**Confidence:** HIGH — all signatures read directly from `fdars-core v0.23.0` git tag

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **DEPTH-03:** Add 9 new `DepthMethod` variants to `depth_method_from_str` dispatcher: `hypograph_index`, `modified_hypograph_index`, `epigraph_index`, `half_region`, `modified_half_region`, `extremal`, `extreme_rank_length`, `l_infinity`, `total_variation`. (13 total). Update `#[non_exhaustive]` wildcard error message. No signature change to `functional_depth`/`functional_boxplot`.
- **OUTL-01..04:** Each detector takes a config struct — build from flat Python kwargs. `tvdmss` → `TvdMssOutliers`, `muod` → `MuodResult`, `sequential_transform_outliers` → `SeqTransformOutliers` (with `SeqTransform` string-dispatch), `depthgram` → `DepthgramResult`. Outlier index sets as `list[int]`; scores as 1-D numpy / floats. `seed=None` → fixed default for reproducibility.
- **ITP-01..04:** `itp_one_pop`, `itp_two_pop`, `itp_flm` in `fdars.inference`. New `itp_result_to_pydict` helper (distinct from `test_result_to_pydict`). `adjusted_pvalues`/`raw_pvalues` as 1-D numpy arrays. `ProjectionBasisType` string-dispatch with `ValueError` wildcard. `itp_flm` re-fits internally. `seed=None` → fixed default.
- **Converters:** `Vec<usize>` outlier index sets → Python `list[int]`; `Vec<f64>` scores/p-values → 1-D numpy; scalars → Python float (never numpy scalar). All fallible calls via `to_pyresult()`; no `.unwrap()`.

### Claude's Discretion

- Plan split (1 sequential vs 3 parallel depth/outliers/ITP plans).
- Exact config-kwarg defaults (confirmed from source: see below).
- Dict key names (= struct field names verbatim).

### Deferred Ideas (OUT OF SCOPE)

- Advisor `outliers`-aspect extension — Phase 40 (ADV-04).
- Docs pages + SVGs + worked examples — Phase 41 (DOCS-10).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEPTH-03 | 9 new `DepthMethod` variants in `functional_depth`/`functional_boxplot` dispatcher | All 9 variants confirmed in v0.23.0 `dispatch.rs`; all parameter-free; min-n guards documented |
| OUTL-01 | `fdars.outliers.tvdmss(data, argvals, ...)` → dict with outlier indices + scores | `TvdMssConfig` (3 fields, all f64, no seed), `TvdMssOutliers` (4 fields) confirmed |
| OUTL-02 | `fdars.outliers.muod(data, argvals, ...)` → dict with 3 outlier sets + 3 score vectors | `MuodConfig` (1 field factor: f64), `MuodResult` (6 fields) confirmed |
| OUTL-03 | `fdars.outliers.sequential_transform_outliers(...)` → dict; `transforms` string-dispatches `SeqTransform` | `SeqTransform` (5 variants: T0/T1/T2/D1/D2), `SeqTransformConfig` (2 fields), `SeqTransformOutliers` (2 fields) confirmed |
| OUTL-04 | `fdars.outliers.depthgram(data, argvals, ...)` → dict; random seed if applicable | `DepthgramConfig` (2 fields), `DepthgramResult` (10 fields) confirmed; no seed field |
| ITP-01 | `fdars.inference.itp_one_pop(data, argvals, mu0=None, ...)` → dict with vector p-values | Full signature confirmed; `ItpResult` (5 fields) confirmed |
| ITP-02 | `fdars.inference.itp_two_pop(data_a, data_b, argvals, ..., seed=None)` → dict | Full signature confirmed; permutation seed confirmed |
| ITP-03 | `fdars.inference.itp_flm(data, response, argvals, ..., basis_type=...)` → dict | Full signature confirmed; `ProjectionBasisType` (2 variants: Bspline/Fourier) confirmed |
| ITP-04 | Register 3 ITP functions in `src/inference_mod.rs`; new `itp_result_to_pydict` helper | Pattern confirmed from existing `test_result_to_pydict`; distinct because p-values are `Vec<f64>` not `f64` |
</phase_requirements>

---

## Summary

Phase 39 exposes three independent areas of the fdars-core v0.23.0 surface across three existing Rust modules. Every signature, struct field, enum variant, and error condition was read directly from the v0.23.0 git tag; no training-data guessing is used for any binding shape.

**Depth (DEPTH-03):** `depth_method_from_str` in `src/depth_mod.rs` gains 9 new arms. All 9 new `DepthMethod` variants are parameter-free (no `scale`, `nproj`, or `seed` arguments beyond the shared dispatcher kwargs), so the dispatcher call site is a trivial enum literal match. The `functional_depth` and `functional_boxplot` Rust function signatures are unchanged. The only per-variant subtlety is the minimum-n guard: `HypographIndex`, `EpigraphIndex`, `HalfRegion`, `ModifiedHalfRegion`, `ExtremeRankLength` require `n >= 2`; `Extremal` and `TotalVariation` require `n >= 3`; `ModifiedHypographIndex` and `LInfinity` work for any `n >= 1`. These guards are already enforced inside `fdars_core::depth::functional_depth`; the PyO3 wrapper just passes through and lets `to_pyresult()` surface them.

**Outliers (OUTL-01..04):** Four new detectors, each taking a config struct built from flat kwargs and returning a `#[non_exhaustive]` result struct. None of the four config structs has a `seed` field: `TvdMssConfig` (3 f64 fields), `MuodConfig` (1 f64 field), `DepthgramConfig` (2 f64 fields) are fully deterministic. `SeqTransformConfig` carries a `DepthMethod` field (handled via the existing dispatcher) and an `emp_factor: f64`. The `sequential_transform_outliers` binding needs a string-to-`SeqTransform` dispatcher analogous to `depth_method_from_str`. Index sets (`Vec<usize>`) are exposed as Python `list[int]` via `.into_iter().map(|x| x as i64).collect::<Vec<i64>>()` (the pattern used in `boxplot_result_to_pydict`). Score vectors (`Vec<f64>`) go via `vec_to_numpy1d`.

**ITP (ITP-01..04):** Three functions returning `ItpResult`, a new struct with `adjusted_pvalues: Vec<f64>` and `raw_pvalues: Vec<f64>` (vector p-values, not scalars), plus `basis_type: ProjectionBasisType`, `n_basis: usize`, `n_perm: usize`. A new `itp_result_to_pydict` helper is required because the existing `test_result_to_pydict` returns `{statistic: f64, p_value: f64, n_perm: usize}` while `ItpResult` returns vector arrays. `ProjectionBasisType` has exactly two variants (`Bspline`, `Fourier`) and is `#[non_exhaustive]`. `itp_flm` uses a scalar response vector (`y: &[f64]`) not a functional matrix; `basis_type` maps `"bspline"` / `"fourier"` strings.

**Primary recommendation:** Split into three parallel plans (depth / outliers / ITP). The only shared edit is `src/lib.rs` module registration — depth changes nothing in `lib.rs`, outliers adds 4 functions to the existing `outliers` submodule registration, ITP adds 3 functions to the existing `inference` submodule registration. Sequencing constraint: `lib.rs` touches are additive (`.add_function` calls appended) and can be merged without conflict.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| DepthMethod dispatch | PyO3 binding (`depth_mod.rs`) | fdars-core dispatch.rs | Dispatcher lives in pyfda; core is the enum definition |
| Outlier config structs | PyO3 binding (`outliers_mod.rs`) | fdars-core outliers.rs | Config built in Rust binding from flat Python kwargs |
| SeqTransform string dispatch | PyO3 binding (`outliers_mod.rs`) | fdars-core outliers.rs | New dispatcher analogous to `depth_method_from_str` |
| ITP basis dispatch | PyO3 binding (`inference_mod.rs`) | fdars-core basis/projection.rs | `ProjectionBasisType` string-to-enum mapping |
| Row-major/column-major conversion | `src/convert.rs` | — | `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d` unchanged |
| Index sets → Python list[int] | PyO3 binding (per module) | — | Inline cast: `x as i64`, collected into Vec then set as list |
| Score vectors → numpy 1-D | `convert.rs::vec_to_numpy1d` | — | Existing helper, no change |

---

## Standard Stack

### Core (no new dependencies)

This phase adds no new Rust or Python dependencies. All required fdars-core functions exist at v0.23.0 (already bumped in Phase 36).

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| `fdars-core` | 0.23.0 | New depth/outlier/ITP functions | Already in `Cargo.toml` |
| `pyo3` | 0.28 | PyO3 macros and bindings | Unchanged |
| `numpy` (pyo3) | 0.28 | Array conversions | Unchanged |

**Installation:** No new packages. Rebuild with `maturin develop` after editing `.rs` files.

---

## Package Legitimacy Audit

No new packages are installed in this phase.

| Package | Registry | Verdict | Disposition |
|---------|----------|---------|-------------|
| (none) | — | — | N/A |

---

## Architecture Patterns

### System Architecture Diagram

```
Python caller
    │
    ├─ fdars.depth.functional_depth(data, method="hypograph_index")
    │       ↓
    │   depth_mod.rs::functional_depth
    │       ↓ depth_method_from_str("hypograph_index", ...)
    │       → DepthMethod::HypographIndex
    │       ↓ fdars_core::depth::functional_depth(&d, DepthMethod::HypographIndex)
    │       → Vec<f64> → vec_to_numpy1d → ndarray(n,)
    │
    ├─ fdars.outliers.tvdmss(data, argvals, emp_factor_mss=1.5, ...)
    │       ↓
    │   outliers_mod.rs::tvdmss
    │       ↓ TvdMssConfig { emp_factor_mss, emp_factor_tvd, central_region_tvd }
    │       ↓ numpy2d_to_fdmatrix(data)
    │       ↓ fdars_core::outliers::tvdmss(&mat, config)
    │       → TvdMssOutliers { magnitude_outliers: Vec<usize>, shape_outliers: Vec<usize>,
    │                           tvd: Vec<f64>, mss: Vec<f64> }
    │       → tvdmss_result_to_pydict → dict
    │
    └─ fdars.inference.itp_one_pop(data, argvals, mu0=None, basis_type="bspline", ...)
            ↓
        inference_mod.rs::itp_one_pop
            ↓ basis_type_from_str("bspline") → ProjectionBasisType::Bspline
            ↓ numpy2d_to_fdmatrix(data)
            ↓ fdars_core::inference::itp::itp_one_pop(&mat, &av, mu0, basis_type, nbasis, n_perm, seed)
            → ItpResult { adjusted_pvalues: Vec<f64>, raw_pvalues: Vec<f64>,
                           basis_type, n_basis, n_perm }
            → itp_result_to_pydict → dict
```

### Recommended Project Structure (files touched)

```
src/
├── depth_mod.rs      # EXTEND: depth_method_from_str — 9 new match arms + updated error message
├── outliers_mod.rs   # EXTEND: 4 new pub fns + 4 new to_pydict helpers + seq_transform_from_str dispatcher
├── inference_mod.rs  # EXTEND: 3 new pub fns (itp_*) + itp_result_to_pydict helper + basis_type_from_str dispatcher
└── lib.rs            # EXTEND: 7 new add_function calls across 2 submodules (outliers: +4, inference: +3)

tests/
├── test_depth.py     # EXTEND: new TestFunctionalDepthNewVariants class
├── test_outliers.py  # NEW: tests for tvdmss, muod, sequential_transform_outliers, depthgram
└── test_inference.py # EXTEND: new TestItp* classes for itp_one_pop, itp_two_pop, itp_flm
```

### Pattern 1: Extending `depth_method_from_str` (DEPTH-03)

**What:** Add 9 new parameter-free match arms to the existing dispatcher. All 9 new variants take no extra parameters beyond the shared `scale`, `nproj`, `seed` kwargs (which are already in the dispatcher signature and unused by the new variants).

**When to use:** Whenever `DepthMethod` gains a new parameter-free variant.

```rust
// Source: src/depth_mod.rs::depth_method_from_str (existing structure)
// Add after "random_projection" arm:
"hypograph_index" => Ok(DepthMethod::HypographIndex),
"modified_hypograph_index" => Ok(DepthMethod::ModifiedHypographIndex),
"epigraph_index" => Ok(DepthMethod::EpigraphIndex),
"half_region" => Ok(DepthMethod::HalfRegion),
"modified_half_region" => Ok(DepthMethod::ModifiedHalfRegion),
"extremal" => Ok(DepthMethod::Extremal),
"extreme_rank_length" => Ok(DepthMethod::ExtremeRankLength),
"l_infinity" => Ok(DepthMethod::LInfinity),
"total_variation" => Ok(DepthMethod::TotalVariation),
// Update wildcard:
other => Err(PyValueError::new_err(format!(
    "method must be one of 'fraiman_muniz', 'band', 'modified_band', \
     'random_projection', 'hypograph_index', 'modified_hypograph_index', \
     'epigraph_index', 'half_region', 'modified_half_region', 'extremal', \
     'extreme_rank_length', 'l_infinity', 'total_variation', got '{other}'"
))),
```

**Important:** `DepthMethod::TotalVariation` dispatches to `fdars_core::depth::functional_depth`, which internally calls `total_variation_depth_1d(data, data)?.tvd` — the `.tvd` field extraction is in the core dispatcher, not in the PyO3 wrapper. The PyO3 wrapper just calls `functional_depth` unchanged.

### Pattern 2: Outlier Config Struct Binding

**What:** Build a Rust config struct from flat Python kwargs, call the core function, convert the `#[non_exhaustive]` result struct field by field to a PyDict.

**When to use:** For all 4 new outlier detectors.

```rust
// Source: pattern from existing detect_outliers_lrt_with_dist in src/outliers_mod.rs
#[pyfunction]
#[pyo3(signature = (data, emp_factor_mss=1.5, emp_factor_tvd=1.5, central_region_tvd=0.5))]
pub fn tvdmss<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    emp_factor_mss: f64,
    emp_factor_tvd: f64,
    central_region_tvd: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let config = fdars_core::outliers::TvdMssConfig {
        emp_factor_mss,
        emp_factor_tvd,
        central_region_tvd,
    };
    let r = to_pyresult(fdars_core::outliers::tvdmss(&mat, config))?;
    tvdmss_to_pydict(py, r)
}
```

**Note on struct literals:** `TvdMssConfig`, `MuodConfig`, and `DepthgramConfig` are NOT `#[non_exhaustive]` — they can be struct-literal constructed safely. Only the result structs (`TvdMssOutliers`, `MuodResult`, `SeqTransformOutliers`, `DepthgramResult`) are `#[non_exhaustive]` — access fields individually, never destructure.

**Note on `SeqTransformConfig`:** This struct carries a `DepthMethod` field (not serde-serializable), so it is NOT `#[non_exhaustive]`. The binding must construct it via struct literal, obtaining `depth_method` from `depth_method_from_str` (reuse the existing helper). The Python-facing kwargs are: `depth_method: str = "modified_band"`, `emp_factor: f64 = 1.5`.

### Pattern 3: SeqTransform String Dispatcher

**What:** New dispatcher analogous to `depth_method_from_str`, for the `transforms` list argument in `sequential_transform_outliers`.

```rust
// Source: fdars_core v0.23.0 outliers.rs::SeqTransform — verified variants below
fn seq_transform_from_str(s: &str) -> PyResult<fdars_core::outliers::SeqTransform> {
    match s {
        "T0" => Ok(fdars_core::outliers::SeqTransform::T0),
        "T1" => Ok(fdars_core::outliers::SeqTransform::T1),
        "T2" => Ok(fdars_core::outliers::SeqTransform::T2),
        "D1" => Ok(fdars_core::outliers::SeqTransform::D1),
        "D2" => Ok(fdars_core::outliers::SeqTransform::D2),
        other => Err(PyValueError::new_err(format!(
            "transform must be one of 'T0', 'T1', 'T2', 'D1', 'D2', got '{other}'"
        ))),
    }
}
```

**Python binding signature:** `transforms` is a Python `list[str]` — in PyO3, accept it as `Vec<String>`, iterate with `seq_transform_from_str`.

### Pattern 4: `itp_result_to_pydict` Helper

**What:** New dict converter for `ItpResult`, distinct from `test_result_to_pydict`. The key difference: p-values are `Vec<f64>` (1-D numpy arrays), not scalars; `basis_type` is a string.

```rust
// Source: fdars-core v0.23.0 inference/itp.rs::ItpResult fields (verified)
fn itp_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::inference::itp::ItpResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("adjusted_pvalues", vec_to_numpy1d(py, r.adjusted_pvalues))?;
    dict.set_item("raw_pvalues", vec_to_numpy1d(py, r.raw_pvalues))?;
    dict.set_item("basis_type", match r.basis_type {
        fdars_core::basis::projection::ProjectionBasisType::Bspline => "bspline",
        fdars_core::basis::projection::ProjectionBasisType::Fourier => "fourier",
        _ => "unknown",  // wildcard required: #[non_exhaustive]
    })?;
    dict.set_item("n_basis", r.n_basis)?;
    dict.set_item("n_perm", r.n_perm)?;
    Ok(dict)
}
```

### Pattern 5: `basis_type_from_str` Dispatcher

**What:** New string-to-`ProjectionBasisType` dispatcher in `inference_mod.rs`. `ProjectionBasisType` is `#[non_exhaustive]` with exactly 2 variants at v0.23.0.

```rust
// Source: fdars-core v0.23.0 basis/projection.rs lines 19-26 (verified)
fn basis_type_from_str(s: &str) -> PyResult<fdars_core::basis::projection::ProjectionBasisType> {
    match s {
        "bspline" => Ok(fdars_core::basis::projection::ProjectionBasisType::Bspline),
        "fourier" => Ok(fdars_core::basis::projection::ProjectionBasisType::Fourier),
        other => Err(PyValueError::new_err(format!(
            "basis_type must be 'bspline' or 'fourier', got '{other}'"
        ))),
    }
}
```

### Pattern 6: `mu0` Optional Array (itp_one_pop)

**What:** `mu0` is `Option<&[f64]>` in core. In PyO3, accept `mu0: Option<PyReadonlyArray1<'py, f64>>` and convert via `mu0.map(|a| numpy1d_to_vec(a))`.

```rust
// Signature pattern (mirrors functional_spatial_1d in depth_mod.rs):
#[pyo3(signature = (data, argvals, mu0=None, basis_type="bspline", nbasis=10, n_perm=999, seed=None))]
pub fn itp_one_pop<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    mu0: Option<PyReadonlyArray1<'py, f64>>,
    basis_type: &str,
    nbasis: usize,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mu0_vec = mu0.map(|a| numpy1d_to_vec(a));
    let bt = basis_type_from_str(basis_type)?;
    let s = seed.unwrap_or(0);
    let r = to_pyresult(fdars_core::inference::itp::itp_one_pop(
        &mat, &av, mu0_vec.as_deref(), bt, nbasis, n_perm, s,
    ))?;
    itp_result_to_pydict(py, r)
}
```

### Anti-Patterns to Avoid

- **Struct-literal on `#[non_exhaustive]` result structs:** `TvdMssOutliers`, `MuodResult`, `SeqTransformOutliers`, `DepthgramResult`, `ItpResult` are all `#[non_exhaustive]` — never pattern-match them exhaustively; access fields individually.
- **Using `test_result_to_pydict` for ITP:** `ItpResult` has `Vec<f64>` p-value arrays, not `f64` scalars. Using the wrong converter silently discards data.
- **Exposing `SeqTransformOutliers.per_transform_outliers` as nested Vec<Vec>:** The field is `Vec<(SeqTransform, Vec<usize>)>`. In Python, expose as `list[dict]` with keys `"transform"` (string) and `"outliers"` (list[int]).
- **Passing `data` and `argvals` to outlier core functions:** `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` take only `&FdMatrix` (no argvals). The Python binding signature should accept `argvals` but not forward it (or omit argvals entirely if the function does not use them). Confirm: none of these 4 functions use a grid.
- **Using `.unwrap()` on any fallible result:** All `Result<T, FdarError>` must go through `to_pyresult()`.
- **Exposing `basis_type: ProjectionBasisType` as an integer:** The legacy `from_i32`/`to_i32` encoding (0=Bspline, 1=Fourier) exists in core for internal use; Python callers should use string tokens `"bspline"` / `"fourier"`.

---

## Verified Source Facts

### DEPTH-03: DepthMethod Variants (all 9 new)

Read from: `fdars-core v0.23.0:fdars-core/src/depth/dispatch.rs`

```
// VERIFIED: fdars-core/src/depth/dispatch.rs (git tag v0.23.0)
// Verbatim enum variants:
HypographIndex,
ModifiedHypographIndex,
EpigraphIndex,
HalfRegion,
ModifiedHalfRegion,
Extremal,
ExtremeRankLength,
LInfinity,
TotalVariation,
```
[VERIFIED: fdars-core/src/depth/dispatch.rs (v0.23.0 git tag)]

**Python string → Rust variant map (13 total):**

| Python string | Rust variant | Has payload | Min n |
|---------------|-------------|-------------|-------|
| `"fraiman_muniz"` | `FraimanMuniz { scale }` | yes (`scale: bool`) | 1 |
| `"band"` | `Band` | no | 2 |
| `"modified_band"` | `ModifiedBand` | no | 2 |
| `"random_projection"` | `RandomProjection { nproj, seed }` | yes | 1 |
| `"hypograph_index"` | `HypographIndex` | **no** | 2 |
| `"modified_hypograph_index"` | `ModifiedHypographIndex` | **no** | 1 |
| `"epigraph_index"` | `EpigraphIndex` | **no** | 2 |
| `"half_region"` | `HalfRegion` | **no** | 2 |
| `"modified_half_region"` | `ModifiedHalfRegion` | **no** | 2 |
| `"extremal"` | `Extremal` | **no** | 3 |
| `"extreme_rank_length"` | `ExtremeRankLength` | **no** | 2 |
| `"l_infinity"` | `LInfinity` | **no** | 1 |
| `"total_variation"` | `TotalVariation` | **no** | 3 |

[VERIFIED: fdars-core/src/depth/dispatch.rs (v0.23.0 git tag)]

**Key insight:** `TotalVariation` dispatches to `total_variation_depth_1d(data, data)?.tvd` inside `functional_depth` — the `.tvd` field extraction is inside core, not in the PyO3 wrapper. This is already tested in the core dispatch tests (`all_nine_new_variants_round_trip`).

### OUTL-01: TvdMss

Read from: `fdars-core v0.23.0:fdars-core/src/outliers.rs` lines 464–560

**`TvdMssConfig` fields** (NOT `#[non_exhaustive]` — safe for struct literal):
```
// VERIFIED: fdars-core/src/outliers.rs:467-476 (v0.23.0 git tag)
pub struct TvdMssConfig {
    pub emp_factor_mss: f64,     // default 1.5
    pub emp_factor_tvd: f64,     // default 1.5
    pub central_region_tvd: f64, // default 0.5
}
```
[VERIFIED: fdars-core/src/outliers.rs:467-476 (v0.23.0 git tag)]

**`TvdMssOutliers` fields** (`#[non_exhaustive]` — field-by-field access only):
```
// VERIFIED: fdars-core/src/outliers.rs:492-502 (v0.23.0 git tag)
pub struct TvdMssOutliers {
    pub magnitude_outliers: Vec<usize>,  // list[int]
    pub shape_outliers: Vec<usize>,      // list[int]
    pub tvd: Vec<f64>,                   // ndarray(n,)
    pub mss: Vec<f64>,                   // ndarray(n,)
}
```
[VERIFIED: fdars-core/src/outliers.rs:492-502 (v0.23.0 git tag)]

**Signature:** `tvdmss(data: &FdMatrix, config: TvdMssConfig) -> Result<TvdMssOutliers, FdarError>`
**Min n:** 3 (raises `InvalidDimension` at n < 3 or m == 0)
**No seed field** — fully deterministic.
**No `argvals` parameter** in core function.

**Python dict layout:**
- `"magnitude_outliers"` → `list[int]`
- `"shape_outliers"` → `list[int]`
- `"tvd"` → ndarray(n,)
- `"mss"` → ndarray(n,)

### OUTL-02: MUOD

Read from: `fdars-core v0.23.0:fdars-core/src/outliers.rs` lines 561–703

**`MuodConfig` fields** (NOT `#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/outliers.rs:564-573 (v0.23.0 git tag)
pub struct MuodConfig {
    pub factor: f64,  // default 1.5
}
```
[VERIFIED: fdars-core/src/outliers.rs:564-573 (v0.23.0 git tag)]

**`MuodResult` fields** (`#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/outliers.rs:579-594 (v0.23.0 git tag)
pub struct MuodResult {
    pub shape_outliers: Vec<usize>,       // list[int]
    pub magnitude_outliers: Vec<usize>,   // list[int]
    pub amplitude_outliers: Vec<usize>,   // list[int]
    pub shape_index: Vec<f64>,            // ndarray(n,)
    pub magnitude_index: Vec<f64>,        // ndarray(n,)
    pub amplitude_index: Vec<f64>,        // ndarray(n,)
}
```
[VERIFIED: fdars-core/src/outliers.rs:579-594 (v0.23.0 git tag)]

**Signature:** `muod(data: &FdMatrix, config: MuodConfig) -> Result<MuodResult, FdarError>`
**Min n:** 3; **min m:** 2 (raises `InvalidDimension` otherwise)
**No seed field** — deterministic.
**No `argvals` parameter** in core function.

**Python dict layout:**
- `"shape_outliers"`, `"magnitude_outliers"`, `"amplitude_outliers"` → `list[int]`
- `"shape_index"`, `"magnitude_index"`, `"amplitude_index"` → ndarray(n,)

### OUTL-03: Sequential Transform Outliers

Read from: `fdars-core v0.23.0:fdars-core/src/outliers.rs` lines 704–865

**`SeqTransform` variants** (`#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/outliers.rs:717-730 (v0.23.0 git tag)
pub enum SeqTransform {
    T0,  // identity
    T1,  // vertical centering (subtract curve mean)
    T2,  // L2 normalization
    D1,  // lag-1 first difference (m → m-1 columns)
    D2,  // identical to D1
}
```
[VERIFIED: fdars-core/src/outliers.rs:717-730 (v0.23.0 git tag)]

**`SeqTransformConfig` fields** (NOT `#[non_exhaustive]`; NOT serde-serializable because carries `DepthMethod`):
```
// VERIFIED: fdars-core/src/outliers.rs:734-748 (v0.23.0 git tag)
pub struct SeqTransformConfig {
    pub depth_method: DepthMethod,  // default DepthMethod::ModifiedBand
    pub emp_factor: f64,            // default 1.5
}
```
[VERIFIED: fdars-core/src/outliers.rs:734-748 (v0.23.0 git tag)]

**`SeqTransformOutliers` fields** (`#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/outliers.rs:754-758 (v0.23.0 git tag)
pub struct SeqTransformOutliers {
    pub per_transform_outliers: Vec<(SeqTransform, Vec<usize>)>,
    pub union_outliers: Vec<usize>,
}
```
[VERIFIED: fdars-core/src/outliers.rs:754-758 (v0.23.0 git tag)]

**Signature:** `sequential_transform_outliers(data: &FdMatrix, sequence: &[SeqTransform], config: SeqTransformConfig) -> Result<SeqTransformOutliers, FdarError>`
**Min n:** 2; D1/D2 steps additionally require `m >= 2` at that step.
**No seed field.**
**No `argvals` parameter** in core function.

**Python dict layout:**
- `"per_transform_outliers"` → `list[dict]` where each dict has `"transform": str` and `"outliers": list[int]`
- `"union_outliers"` → `list[int]`

**PyO3 binding signature:**
```rust
#[pyo3(signature = (data, transforms, depth_method="modified_band", emp_factor=1.5))]
pub fn sequential_transform_outliers<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    transforms: Vec<String>,   // list[str] → Vec<String> for owned iteration
    depth_method: &str,
    emp_factor: f64,
) -> PyResult<Bound<'py, PyDict>>
```

### OUTL-04: Depthgram

Read from: `fdars-core v0.23.0:fdars-core/src/outliers.rs` lines 867–970

**`DepthgramConfig` fields** (NOT `#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/outliers.rs:870-884 (v0.23.0 git tag)
pub struct DepthgramConfig {
    pub outliergram_factor: f64,  // default 1.5
    pub boxplot_factor: f64,      // default 1.5
}
```
[VERIFIED: fdars-core/src/outliers.rs:870-884 (v0.23.0 git tag)]

**`DepthgramResult` fields** (`#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/outliers.rs:893-914 (v0.23.0 git tag)
pub struct DepthgramResult {
    pub mbd_mei_d: Vec<f64>,          // ndarray(n,)
    pub mei_mbd_d: Vec<f64>,          // ndarray(n,)
    pub mbd_mei_t: Vec<f64>,          // ndarray(n,) — equals _d for p=1
    pub mei_mbd_t: Vec<f64>,          // ndarray(n,) — equals _d for p=1
    pub mbd_mei_t2: Vec<f64>,         // ndarray(n,) — equals _d for p=1
    pub mei_mbd_t2: Vec<f64>,         // ndarray(n,) — equals _d for p=1
    pub shape_outliers: Vec<usize>,   // list[int]
    pub magnitude_outliers: Vec<usize>, // list[int]
    pub mbd: Vec<f64>,                // ndarray(n,)
    pub mei: Vec<f64>,                // ndarray(n,)
}
```
[VERIFIED: fdars-core/src/outliers.rs:893-914 (v0.23.0 git tag)]

**Signature:** `depthgram(data: &FdMatrix, config: DepthgramConfig) -> Result<DepthgramResult, FdarError>`
**Min n:** 2; min m: 1 (raises `InvalidDimension` at n < 2 or m == 0)
**No seed field.**
**No `argvals` parameter** in core function.
**Note:** 10-field dict; for univariate data the `_d`, `_t`, `_t2` triplets are identical values.

### ITP-01..04: ItpResult and Function Signatures

Read from: `fdars-core v0.23.0:fdars-core/src/inference/itp.rs`

**`ItpResult` fields** (`#[non_exhaustive]`):
```
// VERIFIED: fdars-core/src/inference/itp.rs:48-62 (v0.23.0 git tag)
pub struct ItpResult {
    pub adjusted_pvalues: Vec<f64>,  // ndarray(n_basis,) — closure-adjusted
    pub raw_pvalues: Vec<f64>,       // ndarray(n_basis,) — pointwise with +1 correction
    pub basis_type: ProjectionBasisType,  // string in Python: "bspline"/"fourier"
    pub n_basis: usize,              // int — actual basis count (may differ from nbasis for B-splines)
    pub n_perm: usize,               // int
}
```
[VERIFIED: fdars-core/src/inference/itp.rs:48-62 (v0.23.0 git tag)]

**`itp_one_pop` signature:**
```
// VERIFIED: fdars-core/src/inference/itp.rs:280-288 (v0.23.0 git tag)
pub fn itp_one_pop(
    data: &FdMatrix,
    argvals: &[f64],
    mu0: Option<&[f64]>,           // null mean; None = zero mean
    basis_type: ProjectionBasisType,
    nbasis: usize,                  // >= 2
    n_perm: usize,                  // >= 1
    seed: u64,
) -> Result<ItpResult, FdarError>
```
[VERIFIED: fdars-core/src/inference/itp.rs:280-288 (v0.23.0 git tag)]

**`itp_two_pop` signature:**
```
// VERIFIED: fdars-core/src/inference/itp.rs:490-498 (v0.23.0 git tag)
pub fn itp_two_pop(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    basis_type: ProjectionBasisType,
    nbasis: usize,                  // >= 2
    n_perm: usize,                  // >= 1
    seed: u64,
) -> Result<ItpResult, FdarError>
```
[VERIFIED: fdars-core/src/inference/itp.rs:490-498 (v0.23.0 git tag)]

**`itp_flm` signature:**
```
// VERIFIED: fdars-core/src/inference/itp.rs:651-659 (v0.23.0 git tag)
pub fn itp_flm(
    data: &FdMatrix,               // functional predictor (n, m)
    y: &[f64],                     // scalar response, length n
    argvals: &[f64],
    basis_type: ProjectionBasisType,
    nbasis: usize,                  // >= 2
    n_perm: usize,                  // >= 1
    seed: u64,
) -> Result<ItpResult, FdarError>
```
[VERIFIED: fdars-core/src/inference/itp.rs:651-659 (v0.23.0 git tag)]

**`ProjectionBasisType` variants** (`#[non_exhaustive]`, exactly 2 variants at v0.23.0):
```
// VERIFIED: fdars-core/src/basis/projection.rs:19-26 (v0.23.0 git tag)
pub enum ProjectionBasisType {
    Bspline,
    Fourier,
}
```
[VERIFIED: fdars-core/src/basis/projection.rs:19-26 (v0.23.0 git tag)]

**Python string tokens:** `"bspline"` → `Bspline`, `"fourier"` → `Fourier`

**Important — n_basis vs nbasis:** For B-splines, knot clamping may reduce the actual number of basis functions below the requested `nbasis`. Always read `result.n_basis` (from `ItpResult`) not the input `nbasis` to know the actual array length of `adjusted_pvalues` and `raw_pvalues`.

**Error conditions per function:**
- `itp_one_pop`: `n < 2`, `argvals.len() != m`, `mu0.len() != m`, `nbasis < 2`, `n_perm == 0`, basis projection failure
- `itp_two_pop`: `n_a < 2 || n_b < 2`, `m_a != m_b`, `argvals.len() != m`, `nbasis < 2`, `n_perm == 0`, basis projection failure
- `itp_flm`: `n < 2`, `y.len() != n`, `argvals.len() != m`, `nbasis < 2`, `n_perm == 0`, basis projection failure

**Divergence from R:** Raw p-values use `(n_ge + 1) / (n_perm + 1)` correction (R uses `n_ge / B`). `itp_flm` uses response-permutation simplification, not partial-residual permutation. Both are deliberate.

### ITP Module Import Path

The ITP functions live at `fdars_core::inference::itp::itp_one_pop` etc. (submodule `itp` inside `inference`). Verify the re-export path in the v0.23.0 lib.rs/inference/mod.rs before coding the `use` statement.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Row-major ↔ column-major conversion | Custom loop | `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d` in `convert.rs` |
| Error propagation | `.unwrap()` or `match` | `to_pyresult()` in `convert.rs` |
| Vec<f64> → numpy | Manual PyArray construction | `vec_to_numpy1d` in `convert.rs` |
| Default uniform grid | Inline linspace | `default_grid()` in `convert.rs` |
| Depth method dispatch | New if-else chain | Extend existing `depth_method_from_str` |

---

## Common Pitfalls

### Pitfall 1: `argvals` forwarded to outlier core functions that don't accept it

**What goes wrong:** `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` take only `&FdMatrix`. Forwarding `argvals` causes a compile error.
**Why it happens:** Inference functions all take `argvals` for the grid, so it's easy to assume outlier functions do too.
**How to avoid:** Accept `argvals` in the Python signature (for API consistency with other submodule functions) but do NOT pass it to the core function. Or accept no argvals at all. Confirm by checking the core function's actual parameter list.
**Warning signs:** Rust compile error "expected 2 arguments, found 3".

### Pitfall 2: Struct-literal construction of `#[non_exhaustive]` result structs

**What goes wrong:** Attempting to match or construct `TvdMssOutliers { magnitude_outliers, .. }` fails to compile in the same crate (for cross-crate callers `#[non_exhaustive]` prevents both exhaustive match and struct literal).
**Why it happens:** Result structs all have `#[non_exhaustive]`.
**How to avoid:** Access fields individually via `r.field_name`. Never use struct-literal syntax or exhaustive pattern-match on result types from a cross-crate dependency.
**Warning signs:** Rust compile error "cannot create non-exhaustive struct using struct expression".

### Pitfall 3: Confusing `test_result_to_pydict` with the new `itp_result_to_pydict`

**What goes wrong:** Using `test_result_to_pydict` for ITP produces a dict with `{"statistic": ..., "p_value": ..., "n_perm": ...}` instead of `{"adjusted_pvalues": ..., "raw_pvalues": ..., "basis_type": ..., "n_basis": ..., "n_perm": ...}`. Python callers get `KeyError` on `adjusted_pvalues`.
**Why it happens:** Both return `PyResult<Bound<'py, PyDict>>`; types match but semantics differ.
**How to avoid:** Create `itp_result_to_pydict` as a new private function with a distinct name. Never pass an `ItpResult` to `test_result_to_pydict`.

### Pitfall 4: `n_basis` vs `nbasis` in ITP dict

**What goes wrong:** Caller assumes `adjusted_pvalues` has length `nbasis` (the requested count), but B-splines can clamp to fewer. Assertions like `assert len(result["adjusted_pvalues"]) == nbasis` fail.
**Why it happens:** The `ItpResult` doc says "actual number of basis functions used may differ from the requested `nbasis`".
**How to avoid:** Expose `result["n_basis"]` in the dict. Test that `len(result["adjusted_pvalues"]) == result["n_basis"]` not `== nbasis`.

### Pitfall 5: `SeqTransformOutliers.per_transform_outliers` serialization

**What goes wrong:** `per_transform_outliers: Vec<(SeqTransform, Vec<usize>)>` — a tuple of enum + vec. Accessing the tuple element naively in PyO3 requires iterating and converting each entry.
**Why it happens:** PyO3 cannot auto-derive a Python representation for `(SeqTransform, Vec<usize>)`.
**How to avoid:** In `seq_transform_to_pydict`, iterate `r.per_transform_outliers` as `for (transform, indices) in r.per_transform_outliers`, create a sub-dict per step with keys `"transform"` (string via a match on SeqTransform variant) and `"outliers"` (list[int]), push to a Python list.

### Pitfall 6: `depth_method_from_str` receives unused `scale`/`nproj`/`seed` for new variants

**What goes wrong:** The 9 new variants ignore `scale`, `nproj`, `seed` kwargs entirely. This is correct behavior — they are no-ops for those variants. The functional signature of `functional_depth` already passes `scale`, `nproj`, `seed` through `depth_method_from_str`; the new variants simply don't use them.
**Warning signs:** None — this is correct and expected. Just don't add an extra check or error if the caller passes `nproj=20` with `method="hypograph_index"`.

### Pitfall 7: ITP Fourier/Bspline string case sensitivity

**What goes wrong:** Caller passes `"Bspline"` or `"BSpline"` and gets a ValueError.
**How to avoid:** Document that strings are lowercase: `"bspline"` and `"fourier"`. This is consistent with other method strings in pyfda (`"fraiman_muniz"`, `"gaussian"`, etc.).

---

## Plan Split Recommendation

**Recommendation: THREE parallel plans.**

The three areas touch completely distinct Rust source files:
- Plan A (Depth): only `src/depth_mod.rs` + `tests/test_depth.py`
- Plan B (Outliers): only `src/outliers_mod.rs` + `tests/test_outliers.py`
- Plan C (ITP): only `src/inference_mod.rs` + `tests/test_inference.py`

The only shared file is `src/lib.rs`, and the changes there are purely additive `.add_function(...)` calls in separate submodule registration blocks. These can be applied in any order and do not conflict.

**Sequencing constraint for lib.rs:** Since GSD wave-parallelism may apply edits simultaneously, have each plan append its own `.add_function` calls to the relevant `register()` function footer (which each own exclusively: `outliers_mod.rs::register` and `inference_mod.rs::register`). Neither plan touches `lib.rs` directly — the registration lives in each module's own `register()` function.

**Wave structure:** All 3 plans can run in Wave 1. `maturin develop` must be run after each plan's Rust edits before running that plan's tests. If running sequentially, a single `maturin develop` after all 3 Rust edits suffices.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (found at `.venv/bin/pytest`) |
| Config file | `pyproject.toml` (standard pytest discovery) |
| Quick run command | `.venv/bin/pytest tests/test_depth.py tests/test_outliers.py tests/test_inference.py -x -q` |
| Full suite command | `.venv/bin/pytest -x -q` |
| Build prerequisite | `maturin develop` (in pyfda root) then run tests |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File |
|--------|----------|-----------|-------------------|------|
| DEPTH-03 | 9 new depth methods return finite (n,) arrays | unit | `.venv/bin/pytest tests/test_depth.py::TestFunctionalDepthNewVariants -x -q` | Wave 0 gap |
| DEPTH-03 | invalid method raises ValueError | unit | `.venv/bin/pytest tests/test_depth.py::TestFunctionalDepthErrors -x -q` | Extend existing |
| DEPTH-03 | functional_boxplot accepts new methods | unit | `.venv/bin/pytest tests/test_depth.py::TestFunctionalBoxplotNewMethods -x -q` | Wave 0 gap |
| OUTL-01 | tvdmss returns dict with 4 keys, index sets are list[int], scores are ndarray | unit | `.venv/bin/pytest tests/test_outliers.py::TestTvdMss -x -q` | Wave 0 gap (new file) |
| OUTL-02 | muod returns dict with 6 keys; 3 list[int] + 3 ndarray | unit | `.venv/bin/pytest tests/test_outliers.py::TestMuod -x -q` | Wave 0 gap |
| OUTL-03 | sequential_transform_outliers: invalid transform raises ValueError | unit | `.venv/bin/pytest tests/test_outliers.py::TestSeqTransform -x -q` | Wave 0 gap |
| OUTL-04 | depthgram returns dict with 10 keys | unit | `.venv/bin/pytest tests/test_outliers.py::TestDepthgram -x -q` | Wave 0 gap |
| ITP-01 | itp_one_pop adjusted_pvalues/raw_pvalues shape == (n_basis,) | unit | `.venv/bin/pytest tests/test_inference.py::TestItpOnePop -x -q` | Wave 0 gap |
| ITP-02 | itp_two_pop seed determinism | unit | `.venv/bin/pytest tests/test_inference.py::TestItpTwoPop -x -q` | Wave 0 gap |
| ITP-03 | itp_flm basis_type string dispatch; invalid basis raises ValueError | unit | `.venv/bin/pytest tests/test_inference.py::TestItpFlm -x -q` | Wave 0 gap |
| ITP-04 | dict keys: adjusted_pvalues, raw_pvalues, basis_type, n_basis, n_perm | unit | included in ITP-01..03 tests | Wave 0 gap |

### Test Data Patterns

Use **synthetic data** (small, fast, CI-safe):
- Depth: `np.random.default_rng(0).standard_normal((10, 20))` — n=10, m=20 satisfies all min-n guards.
- Outliers: `np.random.default_rng(1).standard_normal((15, 30))` — n=15, m=30; plant an outlier as `data[0, :] += 10`.
- ITP: `np.random.default_rng(2).standard_normal((20, 30))` — n=20 for two-sample; `argvals = np.linspace(0, 1, 30)`.

Do NOT rely on dataset-loaded fixtures (Canadian Weather, Berkeley Growth) for new tests — keep them self-contained.

### Sampling Rate

- **Per task commit:** `.venv/bin/pytest tests/test_depth.py tests/test_outliers.py tests/test_inference.py -x -q`
- **Per wave merge:** `.venv/bin/pytest -x -q` (full suite ~560 tests)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_outliers.py` — new file covering OUTL-01..04 (TestTvdMss, TestMuod, TestSeqTransform, TestDepthgram)
- [ ] `tests/test_depth.py` — add `TestFunctionalDepthNewVariants`, `TestFunctionalBoxplotNewMethods` classes
- [ ] `tests/test_inference.py` — add `TestItpOnePop`, `TestItpTwoPop`, `TestItpFlm` classes

---

## Security Domain

`security_enforcement: true` in `.planning/config.json`. `security_asvs_level: 1`.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | All inputs validated by fdars-core (FdarError → PyValueError via `to_pyresult()`) |
| V2 Authentication | no | Library function, no auth |
| V3 Session Management | no | Stateless |
| V4 Access Control | no | No access control |
| V6 Cryptography | no | RNG seeds for test reproducibility only, not security use |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Integer overflow on array index cast `x as i64` | Tampering | fdars-core validates array dims; `usize → i64` safe on 64-bit platforms (all supported targets) |
| Panicking `.unwrap()` crashing the Python process | Denial of service | Never use `.unwrap()` — always `to_pyresult()` |
| Mismatched array dimension causing out-of-bounds | Tampering | fdars-core raises `FdarError::InvalidDimension` propagated by `to_pyresult()` |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `maturin` | Rust→Python build | ✓ | detected via build history | — |
| `.venv/bin/pytest` | Test runner | ✓ | found at path | — |
| `fdars-core` 0.23.0 | All bindings | ✓ | bumped in Phase 36 | — |
| Rust 1.83+ | Compile | ✓ | MSRV met (Phase 36) | — |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `fdars_core::inference::itp` is the correct module path (sub-module, not re-exported at `fdars_core::inference::*`) | ITP signatures | Compile error — fix by checking `fdars-core/src/inference/mod.rs` re-exports at execution start |
| A2 | Python binding signature for outlier detectors should omit `argvals` (core functions don't use it) | OUTL-01..04 | API inconsistency — verify at start of Plan B whether to accept-and-ignore `argvals` for symmetry |
| A3 | `SeqTransform` variant string tokens are uppercase (`"T0"`, `"T1"`, `"T2"`, `"D1"`, `"D2"`) — matching the Rust enum variant names | Pattern 3 | ValueError for all callers — confirm desired casing in CONTEXT.md or default to uppercase to match enum names |

---

## Open Questions

1. **`argvals` in outlier Python signatures**
   - What we know: Core functions `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` take only `&FdMatrix` (no grid parameter).
   - What's unclear: Should the Python binding accept `argvals` for API consistency with `fdars.inference.*` and `fdars.depth.*` even though it doesn't forward it?
   - Recommendation: Omit `argvals` from the Python signature (these are purely depth/stat-based outlier methods that don't need a grid). Document this in docstrings.

2. **ITP module re-export path**
   - What we know: Source lives at `fdars-core/src/inference/itp.rs`.
   - What's unclear: Whether `itp_one_pop` is re-exported at `fdars_core::inference::itp_one_pop` or requires the sub-path `fdars_core::inference::itp::itp_one_pop`.
   - Recommendation: Check `fdars-core/src/inference/mod.rs` at execution start (trivial grep).

3. **SeqTransform string casing**
   - What we know: Rust enum variants are `T0`, `T1`, `T2`, `D1`, `D2`.
   - What's unclear: Whether to use uppercase `"T0"` or lowercase `"t0"` in Python.
   - Recommendation: Use uppercase to match the Rust enum variant names verbatim — consistent with how `DepthMethod::Band` maps to `"band"` NOT `"Band"` (wait, that's lowercase). Actually all existing pyfda string tokens are lowercase (`"fraiman_muniz"`, `"modified_band"`, `"gaussian"`). Recommendation: use lowercase `"t0"`, `"t1"`, `"t2"`, `"d1"`, `"d2"` for consistency.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 4-variant `functional_depth` dispatcher | 13-variant dispatcher | v0.23.0 (this phase) | More depth methods available via the unified API |
| 3 outlier detectors (lrt, outliergram, magnitude_shape) | 7 outlier detectors (+ tvdmss, muod, seq_transform, depthgram) | v0.23.0 (this phase) | Covers fdaoutlier R package parity set |
| No interval-wise tests | 3 ITP tests matching fdatest R package | v0.23.0 (this phase) | Enables localized functional hypothesis testing |

---

## Sources

### Primary (HIGH confidence)

- `fdars-core v0.23.0:fdars-core/src/depth/dispatch.rs` — all 13 `DepthMethod` variants, min-n guards, `functional_depth`/`functional_boxplot` signatures
- `fdars-core v0.23.0:fdars-core/src/outliers.rs` — `TvdMssConfig`, `TvdMssOutliers`, `MuodConfig`, `MuodResult`, `SeqTransform`, `SeqTransformConfig`, `SeqTransformOutliers`, `DepthgramConfig`, `DepthgramResult` — all fields and signatures
- `fdars-core v0.23.0:fdars-core/src/inference/itp.rs` — `ItpResult`, `itp_one_pop`, `itp_two_pop`, `itp_flm` — all fields and signatures
- `fdars-core v0.23.0:fdars-core/src/basis/projection.rs` — `ProjectionBasisType` variants (`Bspline`, `Fourier`)
- `src/depth_mod.rs` (HEAD) — existing `depth_method_from_str`, `functional_depth`, `functional_boxplot` wrappers read directly
- `src/outliers_mod.rs` (HEAD) — existing outlier binding patterns read directly
- `src/inference_mod.rs` (HEAD) — existing `test_result_to_pydict`, `multiplier_from_str`, seed pattern read directly
- `src/convert.rs` (HEAD) — all converter helpers confirmed

### Secondary (MEDIUM confidence)

- `.planning/REQUIREMENTS.md` — REQ-IDs and requirement descriptions
- `.planning/phases/39-group-c-depth-outliers-interval-inference-bindings/39-CONTEXT.md` — locked decisions
- `.planning/research/FEATURES.md` — milestone research context

---

## Metadata

**Confidence breakdown:**
- DepthMethod variants: HIGH — read from v0.23.0 git tag source
- Outlier config/result structs: HIGH — read from v0.23.0 git tag source; all field names verbatim
- ITP signatures and ItpResult: HIGH — read from v0.23.0 git tag source
- ProjectionBasisType variants: HIGH — read from v0.23.0 git tag source
- Test infrastructure: HIGH — `.venv/bin/pytest` confirmed working; 29 depth tests pass in 0.34s
- Plan split recommendation: HIGH — confirmed distinct module files with no shared state

**Research date:** 2026-08-21
**Valid until:** Until fdars-core version is bumped again (next milestone). Source read from pinned v0.23.0 tag.
