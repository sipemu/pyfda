# Architecture Patterns

**Project:** pyfda v6.0 — fdars-core 0.23 Upgrade
**Researched:** 2026-08-20

---

## 1. Module Integration Map: New vs Existing Files

### Group A — Regression

| Capability | Target File | Action |
|---|---|---|
| `concurrent_regression` / `ConcurrentRegrResult` | `src/regression_mod.rs` | **EXTEND** — add binding at bottom, register in existing `register()` |
| `functional_glm` / `FunctionalGlmResult` / `GlmFamily` / `predict_functional_glm` | `src/regression_mod.rs` | **EXTEND** — add `functional_glm` + `predict_functional_glm`, register alongside existing fns |

`concurrent_regression` takes `response: &FdMatrix`, a slice of predictor `&[FdMatrix]`, `argvals: Option<&[f64]>`, `bandwidth: f64`, and `kernel: &str` (string pass-through for `"gaussian"/"epanechnikov"/"tricube"` — no `#[non_exhaustive]` enum). Returns `Result<ConcurrentRegrResult, FdarError>` via `to_pyresult()`.

`functional_glm` takes `data: &FdMatrix`, `y: &[f64]`, `family: GlmFamily` (enum — see §3), `scalar_covariates: Option<&FdMatrix>`, `ncomp: usize`, `max_iter: usize`, `tol: f64`. Returns `Result<FunctionalGlmResult, FdarError>` via `to_pyresult()`.

**No new Rust source files for Group A.** Both functions land in `src/regression_mod.rs`.

### Group B — FPCA & Classification

| Capability | Target File | Action |
|---|---|---|
| `pace_fpca` / `PaceFpcaConfig` / `PaceFpcaResult` | **NEW** `src/pace_fpca_mod.rs` | **NEW FILE** — PACE takes `IrregFdata` (not `FdMatrix`), requiring a new Python-side input path; a dedicated module keeps `regression_mod.rs` coherent |
| `elastic_multinomial` / `ElasticMultinomialResult` / `predict_elastic_multinomial` | `src/classification_mod.rs` | **EXTEND** — add alongside `elastic_logistic` (same file, same registration pattern) |

**`pace_fpca_mod.rs` is a new Rust file** and requires one new `register_submodule!` entry in `src/lib.rs` and a new name in `python/fdars/__init__.py::_submodule_names`. This matches the v4.0 `represent_mod.rs` / `scoring_mod.rs` new-submodule pattern.

`pace_fpca` takes `IrregFdata` — an irregularly-sampled container (offsets + concatenated argvals + values + rangeval). The binding receives the irregular data as lists-of-arrays on the Python side, not a dense `(n, m)` numpy array. `PaceFpcaConfig` is a plain Rust struct (NOT `#[non_exhaustive]`), assembled from individual Python keyword arguments via struct literal.

`elastic_multinomial` lives in `fdars-core/src/elastic_regression/logistic.rs` (same file as `elastic_logistic`). Labels are `&[usize]` (0-indexed class labels) — receive as `PyReadonlyArray1<'py, i64>` and map via `numpy1d_to_usize_vec`.

### Group C — Depth / Outliers / Interval Inference

| Capability | Target File | Action |
|---|---|---|
| 9 new `DepthMethod` variants + new standalone depth fns | `src/depth_mod.rs` | **EXTEND** — extend `depth_method_from_str()` with 9 new arms; add `#[pyfunction]` entries for the new standalone functions |
| `tvdmss` / `muod` / `sequential_transform_outliers` / `depthgram` | `src/outliers_mod.rs` | **EXTEND** |
| `itp_one_pop` / `itp_two_pop` / `itp_flm` / `ItpResult` | `src/inference_mod.rs` | **EXTEND** — `ItpResult → PyDict` mirrors `test_result_to_pydict`; add `basis_type` string helpers |

**No new Rust source files for Group C.**

The `DepthMethod` enum is `#[non_exhaustive]` and gains 9 new variants in 0.23. The existing `depth_method_from_str()` in `depth_mod.rs` uses a wildcard `_ => PyValueError` arm that remains in place; 9 new string-to-variant arms are added above it. The wildcard error message string must be updated to list all 13 valid method names.

---

## 2. New Result-Struct → PyDict Conversions

### Pattern Source of Truth

`inference_mod.rs::test_result_to_pydict()` is the canonical template: a private `fn` that takes the result struct by value, accesses fields individually (never struct-literal on a `#[non_exhaustive]` type), calls `dict.set_item()` for each, and returns `PyResult<Bound<'py, PyDict>>`. Apply this pattern to every new result type.

### New Conversions Required

#### `ConcurrentRegrResult → PyDict` (`regression_mod.rs`)

All fields accessed individually (`#[non_exhaustive]`):
- `beta_curve: FdMatrix` — `fdmatrix_to_numpy2d(py, &r.beta_curve)` — shape `(p, m)` (predictor count × grid points)
- `intercept: Vec<f64>` — `vec_to_numpy1d(py, r.intercept)` — length `m`
- `fitted: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, m)`
- `residuals: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, m)`
- `argvals: Vec<f64>` — `vec_to_numpy1d` — length `m`

`beta_curve` shape `(p, m)` is unusual: rows = predictor index, columns = grid points. `fdmatrix_to_numpy2d` returns row-major numpy, so Python sees `(p, m)`. Correct — but guard with a round-trip test at `p > 1`.

#### `FunctionalGlmResult → PyDict` (`regression_mod.rs`)

All fields accessed individually (`#[non_exhaustive]`):
- `intercept: f64` — scalar
- `beta_t: Vec<f64>` — `vec_to_numpy1d` — length `m`
- `beta_se: Vec<f64>` — `vec_to_numpy1d` — length `m`
- `gamma: Vec<f64>` — `vec_to_numpy1d` — length `p_scalar` (may be 0)
- `fitted_values: Vec<f64>` — `vec_to_numpy1d` — length `n`
- `linear_predictors: Vec<f64>` — `vec_to_numpy1d` — length `n`
- `ncomp: usize` — Python int
- `coefficients: Vec<f64>` — `vec_to_numpy1d`
- `std_errors: Vec<f64>` — `vec_to_numpy1d`
- `log_likelihood: f64` — scalar
- `family: GlmFamily` — string via `family_to_str()` helper (see §3)
- Do NOT expose `fpca: FpcaResult` — internal projection handle; excluded per the `fregre_lm`/FLM-inference re-fit-internally precedent

`GlmFamily` is `#[non_exhaustive]`. `FunctionalGlmResult` is `#[non_exhaustive]`.

#### `PaceFpcaResult → PyDict` (`pace_fpca_mod.rs`)

All fields accessed individually (`#[non_exhaustive]`):
- `mean: Vec<f64>` — `vec_to_numpy1d` — length `m`
- `eigenvalues: Vec<f64>` — `vec_to_numpy1d` — length `ncomp`
- `eigenfunctions: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(m, ncomp)` (grid × components)
- `scores: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, ncomp)`
- `fitted: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, m)`
- `fitted_lower: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, m)`
- `fitted_upper: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, m)`
- `argvals: Vec<f64>` — `vec_to_numpy1d`
- `sigma2: f64` — scalar
- `ncomp: usize` — int (may be < requested due to finite-sample eigendecomposition)

`PaceFpcaResult` is `#[non_exhaustive]`. `PaceFpcaConfig` is NOT `#[non_exhaustive]` — safe to use struct literal.

#### `ElasticMultinomialResult → PyDict` (`classification_mod.rs`)

All fields accessed individually (`#[non_exhaustive]`):
- `n_classes: usize` — int
- `classes: Vec<usize>` — `usize_vec_to_numpy1d` (as i64 array)
- `train_probabilities: FdMatrix` — `fdmatrix_to_numpy2d` — shape `(n, K)`
- `predicted_classes: Vec<usize>` — `usize_vec_to_numpy1d`
- `train_accuracy: f64` — scalar
- Do NOT expose `class_models: Vec<ElasticLogisticResult>` — complex nested type

`ElasticMultinomialResult` is `#[non_exhaustive]`.

#### `ItpResult → PyDict` (`inference_mod.rs`)

Private helper `itp_result_to_pydict()` mirrors `test_result_to_pydict()`:
- `adjusted_pvalues: Vec<f64>` — `vec_to_numpy1d` — length = `n_basis`
- `raw_pvalues: Vec<f64>` — `vec_to_numpy1d` — length = `n_basis`
- `basis_type: ProjectionBasisType` — string via `basis_type_to_str()` helper (see §3)
- `n_basis: usize` — int (always read from result; may differ from requested for B-splines due to knot clamping)
- `n_perm: usize` — int

`ItpResult` is `#[non_exhaustive]`.

#### New Outlier Result Types (`outliers_mod.rs`)

All four new detectors return `Result<T, FdarError>` via `to_pyresult()`.

**`TvdMssOutliers → PyDict`** (`#[non_exhaustive]`):
- `magnitude_outliers: Vec<usize>` — `.into_iter().map(|x| x as i64).collect::<Vec<i64>>()`
- `shape_outliers: Vec<usize>` — same
- `tvd: Vec<f64>` — `vec_to_numpy1d`
- `mss: Vec<f64>` — `vec_to_numpy1d`

**`MuodResult → PyDict`** (`#[non_exhaustive]`):
- `shape_outliers`, `magnitude_outliers`, `amplitude_outliers: Vec<usize>` — lists of i64
- `shape_index`, `magnitude_index`, `amplitude_index: Vec<f64>` — `vec_to_numpy1d`

**`SeqTransformOutliers → PyDict`** (`#[non_exhaustive]`):
- `per_transform_outliers: Vec<(SeqTransform, Vec<usize>)>` — Python list of `(str, list[int])` tuples; `SeqTransform` variant → string via `seq_transform_to_str()` helper
- `union_outliers: Vec<usize>` — list of i64

`SeqTransform` is `#[non_exhaustive]` — the `seq_transform_to_str()` helper needs a wildcard arm returning `"unknown"`.

**`DepthgramResult → PyDict`** (`#[non_exhaustive]`):
- `mbd_mei_d`, `mei_mbd_d`, `mbd_mei_t`, `mei_mbd_t`, `mbd_mei_t2`, `mei_mbd_t2: Vec<f64>` — `vec_to_numpy1d`
- `shape_outliers`, `magnitude_outliers: Vec<usize>` — lists of i64
- `mbd`, `mei: Vec<f64>` — `vec_to_numpy1d`

#### New Standalone Depth Functions (`depth_mod.rs`)

The new standalone depth functions (`hypograph_index_1d`, `epigraph_index_1d`, `modified_hypograph_index_1d`, `half_region_depth_1d`, `modified_half_region_depth_1d`, `extremal_depth_1d`, `extreme_rank_length_depth_1d`, `linfinity_depth_1d`) all return `Result<Vec<f64>, FdarError>` — map via `to_pyresult()` then `vec_to_numpy1d`. No new dict conversion needed.

`total_variation_depth_1d` returns `Result<TvdMssResult, FdarError>` with fields `tvd: Vec<f64>` and `mss: Vec<f64>` — wrap as a 2-key PyDict.

---

## 3. Enum Handling: `#[non_exhaustive]` Fallback Arms and String Dispatch

### `GlmFamily` (Group A, both directions)

`GlmFamily` is `#[non_exhaustive]`. String-to-enum helper for the Python binding parameter:
```rust
fn glm_family_from_str(s: &str) -> PyResult<fdars_core::scalar_on_function::GlmFamily> {
    match s {
        "binomial" => Ok(GlmFamily::Binomial),
        "poisson"  => Ok(GlmFamily::Poisson),
        "gamma"    => Ok(GlmFamily::Gamma),
        "gaussian" => Ok(GlmFamily::Gaussian),
        _ => Err(PyValueError::new_err(format!(
            "family must be 'binomial', 'poisson', 'gamma', or 'gaussian', got '{s}'"
        ))),
    }
}
```
Enum-to-string helper for the result dict (wildcard arm for forward-compat):
```rust
fn family_to_str(f: &GlmFamily) -> &'static str {
    match f {
        GlmFamily::Binomial => "binomial",
        GlmFamily::Poisson  => "poisson",
        GlmFamily::Gamma    => "gamma",
        GlmFamily::Gaussian => "gaussian",
        _ => "unknown",
    }
}
```

### `ProjectionBasisType` (Group C, ITP)

`ProjectionBasisType` is `#[non_exhaustive]`. Two helpers in `inference_mod.rs`:
```rust
fn basis_type_from_str(s: &str) -> PyResult<ProjectionBasisType> {
    match s {
        "bspline" => Ok(ProjectionBasisType::Bspline),
        "fourier" => Ok(ProjectionBasisType::Fourier),
        _ => Err(PyValueError::new_err(
            format!("basis_type must be 'bspline' or 'fourier', got '{s}'")))
    }
}
fn basis_type_to_str(b: &ProjectionBasisType) -> &'static str {
    match b {
        ProjectionBasisType::Bspline => "bspline",
        ProjectionBasisType::Fourier => "fourier",
        _ => "unknown",
    }
}
```

### `SeqTransform` (Group C, outliers)

`SeqTransform` is `#[non_exhaustive]`. Helper in `outliers_mod.rs`:
```rust
fn seq_transform_to_str(t: &SeqTransform) -> &'static str {
    match t {
        SeqTransform::T0 => "t0",
        SeqTransform::T1 => "t1",
        SeqTransform::T2 => "t2",
        SeqTransform::D1 => "d1",
        SeqTransform::D2 => "d2",
        _ => "unknown",
    }
}
```

### `DepthMethod` Extension (Group C, `depth_mod.rs`)

The existing `depth_method_from_str()` gains 9 new match arms before the existing wildcard:
```
"hypograph_index"          => DepthMethod::HypographIndex
"modified_hypograph_index" => DepthMethod::ModifiedHypographIndex
"epigraph_index"           => DepthMethod::EpigraphIndex
"half_region"              => DepthMethod::HalfRegion
"modified_half_region"     => DepthMethod::ModifiedHalfRegion
"extremal"                 => DepthMethod::Extremal
"extreme_rank_length"      => DepthMethod::ExtremeRankLength
"linfinity"                => DepthMethod::LInfinity
"total_variation"          => DepthMethod::TotalVariation
```
The wildcard error message must list all 13 valid method names.

---

## 4. Column-Major Layout Concerns

### Functions Requiring `numpy2d_to_fdmatrix` on Input

| Function | Matrices In | Matrices Out | Transposition Guard Needed |
|---|---|---|---|
| `concurrent_regression` | `response (n,m)`, each predictor `(n,m)` | `beta_curve (p,m)`, `fitted (n,m)`, `residuals (n,m)` | YES — `beta_curve` shape `(p,m)` unusual; round-trip test with `p > 1` required |
| `functional_glm` | `data (n,m)`, optional `scalar_covariates (n,q)` | `beta_t (m,)`, `fitted_values (n,)` — 1D outputs only | Standard |
| `elastic_multinomial` | `data (n,m)` | `train_probabilities (n,K)` matrix | YES — test K=3; verify numpy shape `(n,K)` |
| `pace_fpca` | `IrregFdata` (custom, not FdMatrix) | `eigenfunctions (m,ncomp)`, `scores (n,ncomp)`, `fitted/lower/upper (n,m)` | YES — `eigenfunctions (m,ncomp)` transposition must be guarded; `(n,ncomp)` scores too |
| `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` | `data (n,m)` | all 1D Vec or `Vec<usize>` outlier lists — no matrix outputs | Standard |
| `itp_one_pop`, `itp_two_pop`, `itp_flm` | `data (n,m)` or two `(n,m)` samples | `adjusted_pvalues`, `raw_pvalues` — 1D Vec | Standard |
| New standalone depth fns | `data (n,m)`, `ref_data (n,m)` | `Vec<f64>` → 1D array | Standard |

### PACE-FPCA Input: `IrregFdata` — New Input Pattern

`pace_fpca` consumes `fdars_core::irreg_fdata::IrregFdata` (offsets + concatenated argvals + values + rangeval). There is no precedent for this input type in the existing 19 binding modules — it is the primary implementation risk in Group B.

The Python-facing API should accept:
- `argvals_list: list[np.ndarray]` — per-curve observation times
- `values_list: list[np.ndarray]` — per-curve observed values

The binding constructs `IrregFdata::new(argvals_list, values_list)` on the Rust side by iterating the Python lists and extracting each 1D array. `IrregFdata::new` panics if list lengths differ or any pair has mismatched lengths — catch this before the call.

`PaceFpcaConfig` is assembled as a Rust struct literal (NOT `#[non_exhaustive]` — per-module doc explicitly follows `ElasticPcrConfig` convention for config structs).

### Concurrent Regression: `predictors: &[FdMatrix]` — List-of-Arrays Pattern

`concurrent_regression` takes a slice of FdMatrix. The Python-facing API accepts `predictors: list[np.ndarray]` where each element is `(n, m)`. The binding iterates the Python list, calls `numpy2d_to_fdmatrix` on each element, collects into `Vec<FdMatrix>`, and passes `&predictors`. This is also a new input pattern — explicit test at `p=2` required.

---

## 5. Advisor Integration Points

### New Aspects vs. Extending Existing

All new capabilities map to existing aspects. No new aspect key is required.

| Capability | Advisor Action | Aspect Key |
|---|---|---|
| `concurrent_regression` | Extend `_build_regression_diagnostics`: detect by `"beta_curve"` key in result dict; emit `max_beta_range`, `mean_beta_t` variability summary | `"regression"` (existing) |
| `functional_glm` | Extend `_build_regression_diagnostics`: detect by `"log_likelihood"` key; emit `log_likelihood`, `glm_family`, `ncomp`, `beta_t` summary | `"regression"` (existing) |
| `pace_fpca` | Extend `_build_fpca_diagnostics`: detect by `"sigma2"` + `"fitted_lower"` keys; emit `explained_variance_ratio`, `sigma2`, `mean_band_width` (from `fitted_upper - fitted_lower`) | `"fpca"` (existing) |
| `elastic_multinomial` | Extend `_build_classification_diagnostics`: detect by `"train_probabilities"` key; emit multi-class `train_accuracy`, `n_classes` | `"classification"` (existing) |
| New depth method strings | No change needed — `functional_depth`/`functional_boxplot` output shape unchanged; dispatcher extension is transparent to advisor | `"depth"` (no change) |
| `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` | Extend `_build_outliers_diagnostics`: detect by keys `"tvd"`/`"shape_index"`/`"per_transform_outliers"`/`"mbd_mei_d"` respectively; close v5.0 Phase 34 deferral of boxplot-outlier advisor work | `"outliers"` (existing) |
| `itp_one_pop`, `itp_two_pop`, `itp_flm` | Extend `_build_inference_diagnostics`: detect by `"adjusted_pvalues"` array key (vs scalar `"p_value"` in `TestResult`); emit `min_adjusted_pvalue`, `n_significant_components`, `basis_type`, `n_basis` | `"inference"` (existing #14) |

### Grounding Invariant + MCP Guard-Sync Protocol

Exactly as in v4.0 Phase 28 / v5.0 Phase 34:

Since no new aspect key is being added to `_supported`, the guard-sync commit scope is **aspect builder files only** — `advisor/__init__.py::_supported` and `mcp/server.py::_DIAGNOSTICS_METHODS` do not change. The advisor aspect builder extensions in `aspects/regression.py`, `aspects/fpca.py`, `aspects/classification.py`, `aspects/outliers.py`, and `aspects/inference.py` land together in one atomic commit.

If at plan time it is decided to add a new key (e.g. `"concurrent_regression"` or `"itp"` as distinct from `"inference"`), then the three-file guard-sync (advisor `_supported`, MCP `_DIAGNOSTICS_METHODS`, aspect dispatch branch in `advisor/__init__.py`) must land in a single atomic commit to keep `test_diagnostics_methods_match_advisor_supported` green.

---

## 6. Build Order and Phase Dependencies

### Dependency Graph

```
Phase N:   Crate Bump 0.20 → 0.23 + Regression Gate
              |
              +-- Phase N+1: Group A — Regression Bindings
              |   (src/regression_mod.rs — extend)
              |   INDEPENDENT of N+2 and N+3
              |
              +-- Phase N+2: Group B — FPCA/Classification Bindings
              |   (src/pace_fpca_mod.rs NEW + src/classification_mod.rs extend)
              |   (src/lib.rs, python/fdars/__init__.py)
              |   INDEPENDENT of N+1 and N+3
              |
              +-- Phase N+3: Group C — Depth/Outliers/ITP Inference Bindings
                  (src/depth_mod.rs + src/outliers_mod.rs + src/inference_mod.rs — extend)
                  INDEPENDENT of N+1 and N+2
                         |
              Phase N+4: Advisor Extension
              (aspects/regression.py, aspects/fpca.py, aspects/classification.py,
               aspects/outliers.py, aspects/inference.py — single atomic guard-sync commit)
              DEPENDS ON: N+1 (regression result shapes), N+2 (FPCA/classification shapes),
                          N+3 (outlier/ITP result shapes)
                         |
              Phase N+5: Docs — Diagrams & Worked Examples
              DEPENDS ON: N+1 through N+4
```

Phases N+1, N+2, N+3 are mutually independent and parallel-eligible after the bump gate. This mirrors v4.0 (Phases 26+27 parallel) and v5.0 (Phases 31+32+33 parallel) exactly.

### Bump Gate Notes (Phase N)

Unlike v5.0 (where `CvCriterion` became `#[non_exhaustive]` blocking compilation), 0.21→0.23 adds new `DepthMethod` variants but `depth_mod.rs::depth_method_from_str()` uses string dispatch — no Rust compilation failure on bump. The new top-level modules (`concurrent_regression`, `pace_fpca`) are additive. The bump should be clean: change only `Cargo.toml`, rebuild, run ~560-test suite as the gate.

MSRV at 0.23 is **Rust 1.81** (lowered from 1.83 in the prior pyfda build). pyfda's CI targets 1.83+ — no change needed. Do NOT enable `linalg` (requires Rust 1.84+; faer 0.23+).

### Suggested Phase Numbers (continuing from v5.0 Phase 35)

| Phase | Name | Target Files |
|---|---|---|
| 36 | Crate Bump 0.20 → 0.23 + Regression Gate | `Cargo.toml` only |
| 37 | Group A — Regression Bindings | `src/regression_mod.rs` |
| 38 | Group B — FPCA & Classification Bindings | `src/pace_fpca_mod.rs` (NEW), `src/classification_mod.rs`, `src/lib.rs`, `python/fdars/__init__.py` |
| 39 | Group C — Depth/Outliers/ITP Inference Bindings | `src/depth_mod.rs`, `src/outliers_mod.rs`, `src/inference_mod.rs` |
| 40 | Advisor Extension | `python/fdars/advisor/aspects/*.py` (5 files) — single atomic commit |
| 41 | Docs — Diagrams & Worked Examples | `docs/`, `mkdocs.yml` |

---

## 7. Anti-Patterns to Avoid

### Anti-Pattern 1: Struct-Literal on `#[non_exhaustive]` Result Types

Writing `let r = ConcurrentRegrResult { beta_curve: ..., ... }` in pyfda (outside `fdars-core`) fails to compile. Access fields individually via `r.beta_curve`, `r.intercept`, etc. Affected types: `ConcurrentRegrResult`, `FunctionalGlmResult` (`#[non_exhaustive]`), `PaceFpcaResult`, `ElasticMultinomialResult`, `TvdMssOutliers`, `MuodResult`, `SeqTransformOutliers`, `DepthgramResult`, `ItpResult`.

`PaceFpcaConfig` is the exception — NOT `#[non_exhaustive]` by design; struct literal construction is safe and expected.

### Anti-Pattern 2: Missing Wildcard Arm on `#[non_exhaustive]` Enum Helpers

New `GlmFamily` / `ProjectionBasisType` / `SeqTransform` match arms require wildcard fallbacks returning `"unknown"` (for enum-to-string) or `PyValueError` (for string-to-enum). Applies to all four new helpers: `family_to_str`, `basis_type_from_str`, `basis_type_to_str`, `seq_transform_to_str`.

### Anti-Pattern 3: Exposing `fpca: FpcaResult` from `FunctionalGlmResult`

`FpcaResult` is a complex nested type used internally for projection. Expose only the scalar/vector fields of `FunctionalGlmResult` in the PyDict. Follow the FLM inference precedent: the inference functions in v5.0 Phase 31 re-fit `fregre_lm` internally without the `FregreLmResult` ever crossing the Python boundary.

### Anti-Pattern 4: `pace_fpca` Accepting Dense `(n, m)` Numpy Array

PACE FPCA is specifically designed for irregularly sampled data. Accepting a dense `FdMatrix` would discard the per-curve observation timing information. Users with dense data should use `fdars.regression.fpca`. The `pace_fpca_mod.rs` binding must accept `list[np.ndarray]` inputs.

### Anti-Pattern 5: Advisor Guard-Sync Split Across Multiple Commits

If any new aspect key is added: all three files (`advisor/__init__.py::_supported`, `mcp/server.py::_DIAGNOSTICS_METHODS`, aspect dispatch branch) must change in one atomic commit. Splitting causes `test_diagnostics_methods_match_advisor_supported` to fail in between. Even if only aspect builders change (no new key), group all advisor file changes in one commit.

---

## 8. File Change Summary

### New Files

| File | Type | Trigger |
|---|---|---|
| `src/pace_fpca_mod.rs` | NEW Rust binding module | `pace_fpca` takes `IrregFdata`, not `FdMatrix` — new input path warrants dedicated module |

### Modified Files

| File | Change |
|---|---|
| `Cargo.toml` | `fdars-core = "0.23.0"` (parallel only, no linalg) |
| `src/lib.rs` | `mod pace_fpca_mod;` + one new `register_submodule!(m, "pace_fpca", pace_fpca_mod::register)` |
| `src/regression_mod.rs` | Add `concurrent_regression` + `functional_glm` + `predict_functional_glm` bindings and register |
| `src/depth_mod.rs` | Extend `depth_method_from_str()` with 9 arms; add 9+ new standalone depth `#[pyfunction]`s; update docstrings |
| `src/outliers_mod.rs` | Add `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` bindings and register |
| `src/inference_mod.rs` | Add `itp_one_pop`, `itp_two_pop`, `itp_flm` bindings + `itp_result_to_pydict` helper + `basis_type_*` helpers |
| `src/classification_mod.rs` | Add `elastic_multinomial` + `predict_elastic_multinomial` bindings and register |
| `python/fdars/__init__.py` | Add `"pace_fpca"` to `_submodule_names` |
| `python/fdars/advisor/aspects/regression.py` | Detect `ConcurrentRegrResult`-style (`"beta_curve"`) and `FunctionalGlmResult`-style (`"log_likelihood"`) dicts |
| `python/fdars/advisor/aspects/fpca.py` | Detect `PaceFpcaResult`-style (`"sigma2"` + `"fitted_lower"`) dicts |
| `python/fdars/advisor/aspects/classification.py` | Detect `ElasticMultinomialResult`-style (`"train_probabilities"`) dicts |
| `python/fdars/advisor/aspects/outliers.py` | Add `tvdmss`/`muod`/`sequential_transform`/`depthgram` sub-branches; close v5.0 Phase 34 deferral |
| `python/fdars/advisor/aspects/inference.py` | Detect `ItpResult`-style (`"adjusted_pvalues"` array key) dicts |

---

## Sources

- Direct inspection of `fdars-core` v0.23.0 source via `git show v0.23.0:fdars-core/src/...`
- `fdars-core/src/lib.rs` diff v0.20.0..v0.23.0 confirming the exact new re-exports
- `src/inference_mod.rs` — v5.0 `TestResult→PyDict` + `#[non_exhaustive]` wildcard precedent (pyfda main branch, verified)
- `src/depth_mod.rs` — v5.0 `depth_method_from_str()` + `boxplot_result_to_pydict()` precedent (pyfda main branch, verified)
- `src/regression_mod.rs`, `src/classification_mod.rs`, `src/outliers_mod.rs` — existing binding patterns (pyfda main branch, verified)
- `python/fdars/advisor/__init__.py` — `_supported` set + dispatch pattern (verified: 14 aspects including `"inference"`)
- `python/fdars/mcp/server.py` — `_DIAGNOSTICS_METHODS` (14 entries) + `_RUNNABLE_METHODS` (6 entries) guard pattern (verified)
- `.planning/milestones/v5.0-ROADMAP.md` — Phase 30–35 precedent structure (bump → three parallel groups → advisor → docs)
- `.planning/PROJECT.md` — v6.0 milestone definition and target feature list
