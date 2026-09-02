# Phase 68: Function-on-Function & Scalar-on-Function Regression — Research

**Researched:** 2026-09-02
**Domain:** PyO3 binding — fdars-core 0.33 `fof_regression` module + `scalar_on_function` additive/selection module
**Confidence:** HIGH — all findings read directly from 0.33 registry source and existing project files this session

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Predict API shape:** Combined-refit, stateless. `predict_fof` / `predict_fof_re` take raw training
  data + response + new_x + argvals + params, fit the fof/fof_re model internally, then predict — NO
  opaque `#[pyclass]` handle, NO dict round-trip. Consistent with Phase 67's combined-function pattern.
  `fof_regression` / `fof_re_regression` still return their full result PyDict.
- **Scope:** Include `fof_cv` — total Phase 68 surface = 10 functions.
- `fdars.regression` extension: `fof_regression`, `predict_fof`, `fof_cv`, `fof_re_regression`,
  `predict_fof_re` — edit `src/regression_mod.rs`.
- NEW `fdars.scalar_on_function` submodule: `fam`, `fregre_gkam`, `fregre_gsam`, `variable_selection`,
  `model_selection_ncomp` — `src/scalar_on_function_mod.rs` + `src/lib.rs` + `python/fdars/__init__.py`.

### Claude's Discretion (convention-driven)
- Return shape: documented PyDict from each result struct; confirm exact 0.33 field names against
  registry source before writing converters.
- Transposition + argvals guard: every 2D input via `convert::numpy2d_to_fdmatrix`; every 2D-input
  function gets a NON-SQUARE (`n_obs ≠ n_points`) fixture.
- Random-effects subject-id validation (REG-02): `fof_re_regression` validates the subject-id vector.
- Enum/`#[non_exhaustive]` args: expose as strings with an `Err`-returning wildcard match arm listing
  valid variants (locked STATE decision).
- Defaults via `#[pyo3(signature=...)]` following existing regression conventions.
- Error handling: `FdarError` → `PyValueError` via `convert::to_pyresult`.

### Deferred Ideas (OUT OF SCOPE)
- Advisor extension for the new regression methods (ADV-01) — Phase 72.
- fof/sof-regression docs page with runnable offline example (DOCS-01) — Phase 73.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REG-01 | Function-on-function regression bound — `fof_regression` (+ `predict_fof`) extending `fdars.regression`, returning a `beta`-surface/result PyDict; transposition- and `argvals`-guarded | §3 exact signatures; §4 FofResult fields; §5 combined-refit predict; §7 transposition; §9 registration edits |
| REG-02 | Function-on-function random-effects regression bound — `fof_re_regression` (+ `predict_fof_re`) with subject-id validation | §3 exact signatures; §4 FofReResult fields; §6 subject-id validation; §5 combined-refit predict |
| REG-03 | Scalar-on-function extensions — `fam`, `fregre_gkam`, `fregre_gsam`, `variable_selection`, `model_selection_ncomp` extending `fdars.scalar_on_function` | §3 exact signatures; §4 additive/selection result struct fields; §8 enum dispatch; §9 registration edits |
</phase_requirements>

---

## Summary

Phase 68 has two disjoint binding groups:

**Group A (FOF — `fdars.regression` extension):** Five functions in `src/fof_regression.rs`.
`fof_regression` and `fof_re_regression` are standard 2D-input + PyDict returns. `predict_fof` and
`predict_fof_re` take `&FofResult`/`&FofReResult` in Rust — the binding uses the Phase-67
combined-refit pattern: accept raw training arrays, refit internally, predict on `new_x`.
`fof_cv` is a standard grid-search CV returning a small PyDict. No enum args in this group.

**Group B (SOF additive/selection — NEW `fdars.scalar_on_function` submodule):** Five functions in
`src/scalar_on_function/additive.rs` (4 functions) and `src/scalar_on_function/fregre_lm.rs`
(`model_selection_ncomp`, which already exists in `regression_mod.rs` and simply needs to move into
the new submodule with its current binding unchanged). The additive functions use config structs
(`FamConfig`, `GkamConfig`, `GsamConfig`) — expose as individual flat keyword params, not Python
config objects. `fregre_gkam` and `variable_selection` take `&[&FdMatrix]` (multi-predictor lists)
— use Python `list[np.ndarray]` input with per-element `numpy2d_to_fdmatrix` conversion. `variable_selection`
takes a `VarSelectPenalty` enum exposed as a string with `Err`-returning wildcard arm.

**Critical finding (docs.rs gap resolved):** All result struct field names have been read verbatim
from the 0.33 registry source this session. The research gap flagged in STATE.md is resolved for
Phase 68.

**Primary recommendation:** Implement Group A first (simpler, extends existing file), then Group B
(new submodule). Both groups are independently parallelizable per ROADMAP annotation.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| FOF regression fit (`fof_regression`, `fof_re_regression`) | API / Backend (Rust) | — | Pure computation; all state in returned struct |
| FOF prediction (`predict_fof`, `predict_fof_re`) | API / Backend (Rust) | — | Combined-refit pattern; no Python handle |
| FOF CV (`fof_cv`) | API / Backend (Rust) | — | Grid search over ncomp pairs; deterministic given seed |
| FAM / GSAM additive fit (`fam`, `fregre_gsam`) | API / Backend (Rust) | — | FPC-score NW; one-pass additive smoother |
| GKAM (`fregre_gkam`) | API / Backend (Rust) | — | Iterative backfitting over L2-distance kernels |
| Variable selection (`variable_selection`) | API / Backend (Rust) | — | Group-lasso coordinate descent |
| Model selection (`model_selection_ncomp`) | API / Backend (Rust) | — | Already bound in `regression_mod.rs`; copy to new submodule |
| PyDict assembly + numpy conversion | PyO3 boundary | — | Row-major ↔ column-major in `convert.rs` |
| Subject-id validation | PyO3 boundary | — | Length check + group-count check in binding before core call |
| Submodule registration | Module registry (`lib.rs` + `__init__.py`) | — | Standard macro + name-list pattern |

---

## Section 1: Research Gap Resolved — 0.31/0.32 Field Names

STATE.md flagged: "0.31/0.32 changelog absent — confirm result-struct/config field names against
0.33 source per binding group before writing PyDict converters."

**Status: RESOLVED.** All result struct definitions for Phase 68 have been read verbatim from the
0.33 registry source this session. The risk was real: `FofResult` contains embedded `FpcaResult`
fields (`fpca_x`, `fpca_y`) that would be dangerous to expose, and `FofReResult` adds random-effects
fields that are entirely absent from any docs.rs snapshot.

Sources read this session:
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/fof_regression.rs:28-601]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/scalar_on_function/additive.rs:63-1353]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/scalar_on_function/mod.rs:37-285]
[VERIFIED: ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/src/scalar_on_function/fregre_lm.rs:362-413]

---

## Section 2: Enums in Phase 68

**Group A (FOF) — zero enums.** `fof_regression`, `fof_cv`, `fof_re_regression` take only
primitive types, `&FdMatrix`, `&[f64]`, `&[usize]`, and a config struct. No `#[non_exhaustive]`
enum arguments.

**Group B (SOF additive) — one enum: `VarSelectPenalty`.**
[VERIFIED: fdars-core-0.33.0/src/scalar_on_function/additive.rs:946-959]

Verbatim variants:
```
pub enum VarSelectPenalty {
    GroupLasso,   // fully implemented — recommended default
    GroupMcp,     // NOT YET IMPLEMENTED — raises FdarError::InvalidParameter
    GroupScad,    // NOT YET IMPLEMENTED — raises FdarError::InvalidParameter
    Ls,           // OLS (no penalty) — fully implemented
}
```

Python binding pattern (matching `family_from_str` in `regression_mod.rs:1070-1081`):
```rust
fn penalty_from_str(s: &str) -> PyResult<fdars_core::scalar_on_function::VarSelectPenalty> {
    use fdars_core::scalar_on_function::VarSelectPenalty;
    match s {
        "group_lasso" => Ok(VarSelectPenalty::GroupLasso),
        "ls"          => Ok(VarSelectPenalty::Ls),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "penalty must be 'group_lasso' or 'ls', got '{s}' \
             (GroupMcp/GroupScad not yet implemented upstream)"
        ))),
    }
}
```
Note: `GroupMcp` and `GroupScad` raise `FdarError::InvalidParameter` from upstream even if passed
through — the binding proactively rejects them with a more informative message. The wildcard arm is
still mandatory because `VarSelectPenalty` is `#[non_exhaustive]`.

**Config struct kernel strings** (`fam`, `fregre_gkam`, `fregre_gsam`) — the kernel parameter is
a `String` field, not an enum. Valid values as used in upstream: `"gaussian"`, `"epanechnikov"`,
`"tricube"`. These are validated inside `nadaraya_watson`; invalid strings produce `FdarError`. No
special Rust match arm needed — pass the string directly. Default `"gaussian"` in all three configs.

---

## Section 3: Exact Function Signatures (all 10 functions)

### Group A — FOF (extending `src/regression_mod.rs`)

**`fof_regression`** [VERIFIED: fof_regression.rs:113-120]
```rust
pub fn fof_regression(
    x_data: &FdMatrix,     // (n × m_x) functional predictor
    y_data: &FdMatrix,     // (n × m_y) functional response
    x_argvals: &[f64],     // length m_x
    y_argvals: &[f64],     // length m_y
    ncomp_x: usize,        // predictor FPC components (≥ 1)
    ncomp_y: usize,        // response FPC components (≥ 1)
) -> Result<FofResult, FdarError>
```
Errors: `InvalidDimension` if n_x ≠ n_y, n < 3, argvals length mismatch. `InvalidParameter` if
ncomp_x or ncomp_y == 0. `ComputationFailed` if FPCA or OLS fails.

Python binding signature: `fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)`
- Both `x_data` and `y_data` require `PyReadonlyArray2<'py, f64>` → `numpy2d_to_fdmatrix`
- Both argvals require `PyReadonlyArray1<'py, f64>` → `numpy1d_to_vec`
- Returns PyDict (see §4)

**`predict_fof`** [VERIFIED: fof_regression.rs:341-376]
```rust
pub fn predict_fof(fit: &FofResult, new_x: &FdMatrix) -> Result<FdMatrix, FdarError>
```
Errors: `InvalidDimension` if `new_x.ncols()` does not match the predictor grid used during fitting.

**Combined-refit Python binding** (per locked CONTEXT.md decision):
```
predict_fof(x_data, y_data, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)
```
Internal: call `fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x, ncomp_y)?`, then
`predict_fof(&fit, &new_x_mat)?`. Returns numpy 2D array of shape `(n_new, m_y)`, NOT a PyDict.

**`fof_cv`** [VERIFIED: fof_regression.rs:419-428]
```rust
pub fn fof_cv(
    x_data: &FdMatrix,
    y_data: &FdMatrix,
    x_argvals: &[f64],
    y_argvals: &[f64],
    ncomp_x_max: usize,    // maximum predictor components to try
    ncomp_y_max: usize,    // maximum response components to try
    n_folds: usize,        // number of CV folds
    seed: u64,             // random seed for fold assignment
) -> Result<FofCvResult, FdarError>
```
Errors: `InvalidDimension` if n < n_folds. `ComputationFailed` if no valid (ncomp_x, ncomp_y) pair
produces CV errors (degenerate data).

Python binding signature: `fof_cv(x_data, y_data, x_argvals, y_argvals, ncomp_x_max=5, ncomp_y_max=5, n_folds=5, seed=42)`

**`fof_re_regression`** [VERIFIED: fof_regression.rs:675-682]
```rust
pub fn fof_re_regression(
    x_data: &FdMatrix,        // (n × m_x) functional predictor
    y_data: &FdMatrix,        // (n × m_y) functional response
    subject_ids: &[usize],    // subject identifier per observation, length n
    x_argvals: &[f64],        // length m_x
    y_argvals: &[f64],        // length m_y
    config: &FofReConfig,     // ncomp_x, ncomp_y, max_iter, tol
) -> Result<FofReResult, FdarError>
```
Errors: `InvalidDimension` if n_x ≠ n_y, n < 3, argvals length mismatch, `subject_ids.len() ≠ n`.
`InvalidParameter` if ncomp_x or ncomp_y == 0.

Python binding signature:
`fof_re_regression(x_data, y_data, subject_ids, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)`
- `subject_ids`: `PyReadonlyArray1<'py, i64>` → `numpy1d_to_usize_vec` (matches `fanova` pattern in `regression_mod.rs:401`)
- Config struct built from individual keyword params — do NOT accept a Python dict config object.
- Returns PyDict (see §4)

**`predict_fof_re`** [VERIFIED: fof_regression.rs:943-979]
```rust
pub fn predict_fof_re(fit: &FofReResult, new_x: &FdMatrix) -> Result<FdMatrix, FdarError>
```
New subjects (unseen `subject_ids`) receive population-level fixed-effect prediction only (no random
effect contributed). This is the correct and intended behaviour.

**Combined-refit Python binding:**
```
predict_fof_re(x_data, y_data, subject_ids, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)
```
Internal: build `FofReConfig`, call `fof_re_regression(...)`, then `predict_fof_re(&fit, &new_x_mat)?`.
Returns numpy 2D array of shape `(n_new, m_y)`.

---

### Group B — SOF additive/selection (new `src/scalar_on_function_mod.rs`)

**`fam`** [VERIFIED: scalar_on_function/additive.rs:430-436]
```rust
pub fn fam(
    data: &FdMatrix,                  // (n × m) functional predictor
    y: &[f64],                        // scalar response, length n
    argvals: &[f64],                  // length m
    scalar_covariates: Option<&FdMatrix>,  // (n × q) optional; None if unused
    config: &FamConfig,               // ncomp, bandwidth, kernel, n_grid_bandwidth
) -> Result<FamResult, FdarError>
```
`FamConfig` fields [VERIFIED: additive.rs:67-76]:
```
pub ncomp: usize           // 0 = auto-select via GCV (default: 0)
pub bandwidth: f64         // 0.0 = auto-select per component via GCV (default: 0.0)
pub kernel: String         // "gaussian" | "epanechnikov" | "tricube" (default: "gaussian")
pub n_grid_bandwidth: usize  // bandwidth-grid points for optim_bandwidth (default: 20)
```

Python binding signature:
`fam(data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel="gaussian", n_grid_bandwidth=20)`
- Builds `FamConfig { ncomp, bandwidth, kernel: kernel.to_string(), n_grid_bandwidth }` internally.
- `scalar_covariates`: `Option<PyReadonlyArray2<'py, f64>>` → `Option<FdMatrix>` via `.map(numpy2d_to_fdmatrix).transpose()?`
  (same pattern as `fregre_np_cv` in `regression_mod.rs:901-903`)
- Returns PyDict (see §4)

**`fregre_gkam`** [VERIFIED: scalar_on_function/additive.rs:564-569]
```rust
pub fn fregre_gkam(
    predictors: &[&FdMatrix],         // slice of P functional predictors, each (n × m_p)
    y: &[f64],                        // scalar response, length n
    argvals_list: &[&[f64]],          // one argvals slice per predictor
    scalar_covariates: Option<&FdMatrix>,
    config: &GkamConfig,              // bandwidth, kernel, max_iter, epsilon
) -> Result<GkamResult, FdarError>
```
`GkamConfig` fields [VERIFIED: additive.rs:94-102]:
```
pub bandwidth: f64   // 0.0 = auto via LOO-CV (default: 0.0)
pub kernel: String   // (default: "gaussian")
pub max_iter: usize  // maximum backfitting iterations (default: 50)
pub epsilon: f64     // convergence threshold (default: 1e-6)
```

Python binding signature:
`fregre_gkam(predictors, y, argvals_list, scalar_covariates=None, bandwidth=0.0, kernel="gaussian", max_iter=50, epsilon=1e-6)`
- `predictors`: `Vec<PyReadonlyArray2<'py, f64>>` (list of numpy arrays from Python) — same pattern as
  `concurrent_regression` in `regression_mod.rs:1038-1048`
- `argvals_list`: `Vec<PyReadonlyArray1<'py, f64>>` → convert each with `numpy1d_to_vec`; collect into
  `Vec<Vec<f64>>`, then build `&[&[f64]]` references for the Rust call.
- Critical: the Rust call expects `&[&FdMatrix]` (slice of references). Build `Vec<FdMatrix>` first,
  then collect refs: `let pred_refs: Vec<&FdMatrix> = pred_mats.iter().collect();`
- Returns PyDict (see §4)

**`fregre_gsam`** [VERIFIED: scalar_on_function/additive.rs:842-847]
```rust
pub fn fregre_gsam(
    data: &FdMatrix,                  // (n × m) — single functional predictor
    y: &[f64],
    argvals: &[f64],
    scalar_covariates: Option<&FdMatrix>,
    config: &GsamConfig,              // ncomp, bandwidth, kernel, n_grid_bandwidth
) -> Result<GsamResult, FdarError>
```
`GsamConfig` fields [VERIFIED: additive.rs:119-128]:
```
pub ncomp: usize             // 0 = auto-select via GCV (default: 0)
pub bandwidth: f64           // 0.0 = auto per component (default: 0.0)
pub kernel: String           // (default: "gaussian")
pub n_grid_bandwidth: usize  // (default: 20)
```

Python binding signature:
`fregre_gsam(data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel="gaussian", n_grid_bandwidth=20)`
- Identical input shape to `fam` (single predictor, not a list).
- Returns PyDict (see §4)

**`variable_selection`** [VERIFIED: scalar_on_function/additive.rs:1188-1193]
```rust
pub fn variable_selection(
    predictors: &[&FdMatrix],
    y: &[f64],
    argvals_list: &[&[f64]],
    scalar_covariates: Option<&FdMatrix>,
    config: &VarSelectConfig,         // ncomp, penalty, lambda, max_iter, epsilon, lambda_n_grid
) -> Result<VarSelectResult, FdarError>
```
`VarSelectConfig` fields [VERIFIED: additive.rs:965-979]:
```
pub ncomp: usize              // FPC components per predictor; 0 = auto via GCV (default: 3)
pub penalty: VarSelectPenalty // GroupLasso | Ls only (GroupMcp/GroupScad rejected upstream)
pub lambda: f64               // 0.0 = CV-select over grid (default: 0.0)
pub max_iter: usize           // coordinate-descent iterations (default: 100)
pub epsilon: f64              // convergence threshold (default: 1e-5)
pub lambda_n_grid: usize      // grid size for lambda selection (default: 20)
```

Python binding signature:
`variable_selection(predictors, y, argvals_list, scalar_covariates=None, ncomp=3, penalty="group_lasso", lambda_=0.0, max_iter=100, epsilon=1e-5, lambda_n_grid=20)`
- Note: use `lambda_` (trailing underscore) to avoid collision with Python keyword `lambda`, matching
  the `fosr` binding convention in `regression_mod.rs:357`.
- Multi-predictor list input: same pattern as `fregre_gkam`.
- `penalty` string → `VarSelectPenalty` via `penalty_from_str` (see §2).
- Returns PyDict (see §4)

**`model_selection_ncomp`** [VERIFIED: scalar_on_function/fregre_lm.rs:362-368]
```rust
pub fn model_selection_ncomp(
    data: &FdMatrix,
    y: &[f64],
    scalar_covariates: Option<&FdMatrix>,
    max_ncomp: usize,
    criterion: SelectionCriterion,    // Aic | Bic | Gcv
) -> Result<ModelSelectionResult, FdarError>
```
`SelectionCriterion` [VERIFIED: scalar_on_function/mod.rs:267-275] — NOT `#[non_exhaustive]`:
```
pub enum SelectionCriterion { Aic, Bic, Gcv }
```

**IMPORTANT:** This function is already bound in `regression_mod.rs:434-458` as `model_selection_ncomp`.
The existing binding is identical to what Phase 68 needs. **Copy the existing binding verbatim** into
`scalar_on_function_mod.rs` (do not modify `regression_mod.rs` — it stays in the `regression` submodule
where it historically lives). The new `scalar_on_function` submodule adds a second registration of
the same logic, appropriate since the method conceptually belongs to the SoF family.

Python binding signature: `model_selection_ncomp(data, response, max_comp=10, criterion="gcv")`
(identical to the existing binding in `regression_mod.rs:433`)

---

## Section 4: Exact Result Struct Fields (verbatim from 0.33 source)

### `FofResult` [VERIFIED: fof_regression.rs:30-53]
Verbatim fields:
```
pub intercept: Vec<f64>       // α(s), length m_y → numpy 1D (m_y,)
pub beta_surface: FdMatrix    // β(s,t), shape (m_y × m_x) → numpy 2D (m_y, m_x)
pub fitted: FdMatrix          // fitted response curves (n × m_y) → numpy 2D (n, m_y)
pub residuals: FdMatrix       // residual curves (n × m_y) → numpy 2D (n, m_y)
pub r_squared_t: Vec<f64>     // per-grid-point R², length m_y → numpy 1D (m_y,)
pub r_squared: f64            // overall R² → float
pub ncomp_x: usize            // predictor FPC components used → int
pub ncomp_y: usize            // response FPC components used → int
pub fpca_x: FpcaResult        // INTENTIONALLY NOT EXPOSED (internal FPCA state)
pub fpca_y: FpcaResult        // INTENTIONALLY NOT EXPOSED (internal FPCA state)
pub coef_matrix: FdMatrix     // B: Y-scores = X-scores * B, shape (ncomp_x × ncomp_y) → numpy 2D
```
PyDict keys to expose (9 keys — do NOT expose `fpca_x` or `fpca_y`):
`"intercept"`, `"beta_surface"`, `"fitted"`, `"residuals"`, `"r_squared_t"`, `"r_squared"`,
`"ncomp_x"`, `"ncomp_y"`, `"coef_matrix"`

**CRITICAL — `beta_surface` shape:** `beta_surface` is shape `(m_y × m_x)` in FdMatrix convention
(rows=m_y, cols=m_x). `fdmatrix_to_numpy2d` will return shape `(m_y, m_x)` — this is correct and
intended. Document clearly: rows index response grid, columns index predictor grid.

**CRITICAL — `coef_matrix` shape:** `(ncomp_x × ncomp_y)` — rows=predictor components,
cols=response components. Same reshape via `fdmatrix_to_numpy2d`.

### `FofCvResult` [VERIFIED: fof_regression.rs:387-396]
Verbatim fields:
```
pub candidates: Vec<(usize, usize)>  // (ncomp_x, ncomp_y) pairs tested → list of 2-tuples
pub cv_errors: Vec<f64>              // integrated CV-MSE per candidate → numpy 1D
pub optimal: (usize, usize)          // best (ncomp_x, ncomp_y) → tuple (int, int)
pub min_cv_mse: f64                  // minimum integrated CV-MSE → float
```
PyDict keys (4 keys): `"candidates"`, `"cv_errors"`, `"optimal"`, `"min_cv_mse"`

Conversion for `candidates: Vec<(usize, usize)>`:
```rust
let candidates_list: Vec<(i64, i64)> = result.candidates.iter()
    .map(|&(x, y)| (x as i64, y as i64))
    .collect();
dict.set_item("candidates", candidates_list)?;
```
Conversion for `optimal: (usize, usize)`:
```rust
dict.set_item("optimal", (result.optimal.0 as i64, result.optimal.1 as i64))?;
```

### `FofReResult` [VERIFIED: fof_regression.rs:568-600]
Verbatim fields:
```
pub intercept: Vec<f64>       // α(s) = mean_y(s), length m_y → numpy 1D (m_y,)
pub beta_surface: FdMatrix    // β(s,t), shape (m_y × m_x) → numpy 2D (m_y, m_x)
pub fitted: FdMatrix          // fitted response including fixed+random effects (n × m_y)
pub residuals: FdMatrix       // residual curves (n × m_y) → numpy 2D (n, m_y)
pub r_squared_t: Vec<f64>     // per-grid-point R², length m_y → numpy 1D (m_y,)
pub r_squared: f64            // overall R² → float
pub ncomp_x: usize            // predictor FPC components used → int
pub ncomp_y: usize            // response FPC components used → int
pub fpca_x: FpcaResult        // INTENTIONALLY NOT EXPOSED
pub fpca_y: FpcaResult        // INTENTIONALLY NOT EXPOSED
pub coef_matrix: FdMatrix     // B: Y-scores ≈ X-scores * B, (ncomp_x × ncomp_y) → numpy 2D
pub random_effects: FdMatrix  // subject-level random intercept functions (n_subjects × m_y)
pub sigma2_u: Vec<f64>        // per-Y-component random intercept variance (length ncomp_y)
pub sigma2_eps: f64           // mean residual variance across Y-score components → float
pub n_subjects: usize         // number of unique subjects → int
```
PyDict keys to expose (13 keys — `fpca_x` and `fpca_y` excluded):
`"intercept"`, `"beta_surface"`, `"fitted"`, `"residuals"`, `"r_squared_t"`, `"r_squared"`,
`"ncomp_x"`, `"ncomp_y"`, `"coef_matrix"`, `"random_effects"`, `"sigma2_u"`, `"sigma2_eps"`,
`"n_subjects"`

`random_effects` shape: `(n_subjects × m_y)` — `fdmatrix_to_numpy2d` returns `(n_subjects, m_y)`.

### `FamResult` [VERIFIED: scalar_on_function/additive.rs:146-169]
Verbatim fields:
```
pub fitted_values: Vec<f64>     // ŷ (length n) → numpy 1D (n,)
pub residuals: Vec<f64>         // y − ŷ (length n) → numpy 1D (n,)
pub component_fits: Vec<Vec<f64>> // f_k(ξ_k) per observation; outer index = component
                                 // length = ncomp + scalar_covariates.ncols() → list of numpy 1D
pub intercept: f64              // mean response μ_y → float
pub bandwidths: Vec<f64>        // per-component optimal bandwidth → numpy 1D
pub ncomp: usize                // FPC components used → int
pub r_squared: f64              // R² → float
pub fpca: FpcaResult            // INTENTIONALLY NOT EXPOSED
```
PyDict keys (7 keys — `fpca` excluded): `"fitted_values"`, `"residuals"`, `"component_fits"`,
`"intercept"`, `"bandwidths"`, `"ncomp"`, `"r_squared"`

Conversion for `component_fits: Vec<Vec<f64>>`:
```rust
use pyo3::types::PyList;
let cf_list = PyList::empty(py);
for cf in result.component_fits {
    cf_list.append(vec_to_numpy1d(py, cf))?;
}
dict.set_item("component_fits", cf_list)?;
```

### `GkamResult` [VERIFIED: scalar_on_function/additive.rs:171-192]
Verbatim fields:
```
pub fitted_values: Vec<f64>     // ŷ (length n) → numpy 1D (n,)
pub residuals: Vec<f64>         // y − ŷ → numpy 1D (n,)
pub component_fits: Vec<Vec<f64>> // f_k per predictor (q × n) → list of numpy 1D
pub intercept: f64              // mean response → float
pub bandwidths: Vec<f64>        // per-predictor bandwidth (length q) → numpy 1D
pub iterations: usize           // backfitting iterations performed → int
pub converged: bool             // whether backfitting converged → bool
pub r_squared: f64              // R² → float
```
PyDict keys (8 keys): `"fitted_values"`, `"residuals"`, `"component_fits"`, `"intercept"`,
`"bandwidths"`, `"iterations"`, `"converged"`, `"r_squared"`

### `GsamResult` [VERIFIED: scalar_on_function/additive.rs:194-218]
Verbatim fields:
```
pub fitted_values: Vec<f64>     // ŷ (length n) → numpy 1D (n,)
pub residuals: Vec<f64>         // y − ŷ → numpy 1D (n,)
pub component_fits: Vec<Vec<f64>> // f_j per component → list of numpy 1D
pub intercept: f64              // mean response → float
pub bandwidths: Vec<f64>        // per-component bandwidth → numpy 1D
pub ncomp: usize                // FPC components used → int
pub r_squared: f64              // R² → float
pub fpca: FpcaResult            // INTENTIONALLY NOT EXPOSED
```
PyDict keys (7 keys — `fpca` excluded): `"fitted_values"`, `"residuals"`, `"component_fits"`,
`"intercept"`, `"bandwidths"`, `"ncomp"`, `"r_squared"`

### `VarSelectResult` [VERIFIED: scalar_on_function/additive.rs:998-1019]
Verbatim fields:
```
pub active_predictors: Vec<bool>   // whether each predictor is active (length P) → numpy bool 1D
pub coefficients: Vec<Vec<f64>>    // group-lasso coef per predictor (P × K_p) → list of numpy 1D
pub fitted_values: Vec<f64>        // ŷ (length n) → numpy 1D (n,)
pub residuals: Vec<f64>            // y − ŷ → numpy 1D (n,)
pub intercept: f64                 // mean response → float
pub lambda: f64                    // selected or provided λ → float
pub r_squared: f64                 // R² → float
pub iterations: usize              // coordinate-descent iterations → int
pub converged: bool                // whether CD converged → bool
pub fpcas: Vec<FpcaResult>         // INTENTIONALLY NOT EXPOSED
```
PyDict keys (9 keys — `fpcas` excluded): `"active_predictors"`, `"coefficients"`, `"fitted_values"`,
`"residuals"`, `"intercept"`, `"lambda"`, `"r_squared"`, `"iterations"`, `"converged"`

Conversion for `active_predictors: Vec<bool>`:
```rust
dict.set_item("active_predictors", bool_vec_to_numpy1d(py, result.active_predictors))?;
```
`bool_vec_to_numpy1d` [VERIFIED: src/convert.rs:81-83] already exists in `convert.rs`.

Conversion for `coefficients: Vec<Vec<f64>>` (analogous to `component_fits`):
```rust
let coef_list = PyList::empty(py);
for c in result.coefficients {
    coef_list.append(vec_to_numpy1d(py, c))?;
}
dict.set_item("coefficients", coef_list)?;
```

### `ModelSelectionResult` [VERIFIED: scalar_on_function/mod.rs:280-285]
Fields identical to the existing `regression_mod.rs:434-458` binding — no change needed:
```
pub best_ncomp: usize               // best number of FPC components → int
pub criteria: Vec<(usize, f64, f64, f64)>  // (ncomp, AIC, BIC, GCV) per candidate → list of tuples
```
PyDict keys (2 keys): `"best_ncomp"`, `"criteria"`

---

## Section 5: Combined-Refit Predict Architecture

`predict_fof` and `predict_fof_re` each take a Rust struct reference (`&FofResult` / `&FofReResult`)
as their primary input. Python cannot pass a Rust struct. The Phase-67 combined-function pattern is
the correct resolution per locked CONTEXT.md.

### `predict_fof` binding:
```rust
#[pyfunction]
#[pyo3(signature = (x_data, y_data, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3))]
pub fn predict_fof<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    new_x: PyReadonlyArray2<'py, f64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x: usize,
    ncomp_y: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let new_x_mat = numpy2d_to_fdmatrix(new_x)?;
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);
    let fit = to_pyresult(fdars_core::fof_regression::fof_regression(
        &x_mat, &y_mat, &ax, &ay, ncomp_x, ncomp_y,
    ))?;
    let predicted = to_pyresult(fdars_core::fof_regression::predict_fof(&fit, &new_x_mat))?;
    Ok(fdmatrix_to_numpy2d(py, &predicted).into_any())
}
```
Returns numpy 2D of shape `(n_new, m_y)`.

### `predict_fof_re` binding — analogous:
```rust
#[pyo3(signature = (x_data, y_data, subject_ids, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10))]
pub fn predict_fof_re<'py>( ... ) -> PyResult<Bound<'py, PyAny>> {
    // Build FofReConfig from flat params
    let config = fdars_core::fof_regression::FofReConfig {
        ncomp_x, ncomp_y, max_iter, tol,
    };
    let sid = numpy1d_to_usize_vec(subject_ids);
    let fit = to_pyresult(fdars_core::fof_regression::fof_re_regression(
        &x_mat, &y_mat, &sid, &ax, &ay, &config,
    ))?;
    let predicted = to_pyresult(fdars_core::fof_regression::predict_fof_re(&fit, &new_x_mat))?;
    Ok(fdmatrix_to_numpy2d(py, &predicted).into_any())
}
```
Returns numpy 2D of shape `(n_new, m_y)`.

**Important:** `FofReConfig` is NOT `#[non_exhaustive]` [VERIFIED: fof_regression.rs:526-527]:
```
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
pub struct FofReConfig { ... }
```
This means struct literal construction is allowed (no `..Default::default()` needed for exhaustive
construction). Use field-by-field assignment to be safe: `FofReConfig { ncomp_x, ncomp_y, max_iter, tol }`.

---

## Section 6: Random-Effects Subject-ID Validation (REG-02)

`fof_re_regression` accepts `subject_ids: &[usize]` — a 0-based integer group label per observation.

**Upstream validation (already performed by fdars-core):**
- `subject_ids.len() != n` → `FdarError::InvalidDimension` (propagated to `ValueError`)
- `config.ncomp_x == 0` or `config.ncomp_y == 0` → `FdarError::InvalidParameter`
- n < 3 → `FdarError::InvalidDimension`

**Additional validation required in the PyO3 binding (REG-02, CONTEXT.md):**
```rust
// Validate subject_ids length matches n_obs
if sid.len() != x_mat.nrows() {
    return Err(pyo3::exceptions::PyValueError::new_err(format!(
        "subject_ids length {} does not match x_data rows {}",
        sid.len(), x_mat.nrows()
    )));
}
// Validate ≥ 2 unique groups (upstream build_subject_map does not enforce this;
// a single-group fit is meaningless for mixed models)
let n_subjects = {
    let mut sorted = sid.clone();
    sorted.sort_unstable();
    sorted.dedup();
    sorted.len()
};
if n_subjects < 2 {
    return Err(pyo3::exceptions::PyValueError::new_err(
        "subject_ids must contain at least 2 distinct subjects for random-effects regression"
    ));
}
```

**Python API convention:** Accept `subject_ids` as `PyReadonlyArray1<'py, i64>` and convert via
`numpy1d_to_usize_vec` (matching `fanova` pattern in `regression_mod.rs:401`). Users pass `np.array([0,0,1,1,2], dtype=np.int64)` or similar. Document that IDs must be non-negative integers.

---

## Section 7: Transposition Handling

[VERIFIED: src/convert.rs:25-42]

`numpy2d_to_fdmatrix` converts numpy row-major `(n_obs, n_points)` → FdMatrix column-major
`(nrows=n_obs, ncols=n_points)`. This is correct for all 2D inputs in Phase 68.

**FOF functions have TWO 2D inputs each:** `x_data` (n × m_x) and `y_data` (n × m_y) — both must
go through `numpy2d_to_fdmatrix`. These can have different column counts (m_x ≠ m_y), which is the
normal FOF case. Test fixture must reflect this:

```python
N, MX, MY = 30, 25, 18   # N_obs=30, m_x=25, m_y=18 — all three deliberately different
assert N != MX and N != MY and MX != MY
```

**Non-square fixture requirement per STATE.md:** Use `(N, MX, MY) = (30, 25, 18)`. This catches:
- n_obs=30, m_x=25 (x non-square)
- n_obs=30, m_y=18 (y non-square)
- m_x=25, m_y=18 (x and y grids differ — the typical FOF use case)

**For `fof_re_regression`:** Same fixture; add `subject_ids = [i // 6 for i in range(N)]` giving 5
subjects with 6 observations each.

**SOF additive functions:** Standard `(N=30, M=20)` non-square fixture. `fregre_gkam` and
`variable_selection` with multiple predictors: use 2 predictors of shapes `(N, M1)` and `(N, M2)`
with `M1 ≠ M2` (e.g., `(30, 20)` and `(30, 15)`).

---

## Section 8: Enum and Config Struct Patterns

### `VarSelectPenalty` dispatch (from §2):
```rust
fn penalty_from_str(s: &str) -> PyResult<fdars_core::scalar_on_function::VarSelectPenalty> {
    use fdars_core::scalar_on_function::VarSelectPenalty;
    match s {
        "group_lasso" => Ok(VarSelectPenalty::GroupLasso),
        "ls"          => Ok(VarSelectPenalty::Ls),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "penalty must be 'group_lasso' or 'ls', got '{s}' \
             (GroupMcp/GroupScad not yet implemented upstream)"
        ))),
    }
}
```
**Mandatory wildcard arm:** `VarSelectPenalty` is `#[non_exhaustive]` [VERIFIED: additive.rs:945].

### `SelectionCriterion` dispatch (for `model_selection_ncomp`):
Copy the existing pattern verbatim from `regression_mod.rs:443-447`:
```rust
let crit = match criterion {
    "aic" => fdars_core::scalar_on_function::SelectionCriterion::Aic,
    "bic" => fdars_core::scalar_on_function::SelectionCriterion::Bic,
    _ => fdars_core::scalar_on_function::SelectionCriterion::Gcv,
};
```
`SelectionCriterion` is NOT `#[non_exhaustive]` [VERIFIED: mod.rs:267], so the existing default-arm
(rather than `Err`-arm) pattern is acceptable for this one function. Do NOT change it to an `Err`-arm
for the copy into the new module — preserve the existing behaviour.

### Config structs built from flat params:
All three additive functions use config structs (`FamConfig`, `GkamConfig`, `GsamConfig`). These are
`#[non_exhaustive]` [VERIFIED: additive.rs:65, 92, 116], so they cannot be struct-literal constructed.
Use the `Default` impl + field assignment:
```rust
let mut config = fdars_core::scalar_on_function::FamConfig::default();
config.ncomp = ncomp;
config.bandwidth = bandwidth;
config.kernel = kernel.to_string();
config.n_grid_bandwidth = n_grid_bandwidth;
```

### `FofReConfig` — NOT `#[non_exhaustive]`:
Direct struct literal allowed:
```rust
let config = fdars_core::fof_regression::FofReConfig { ncomp_x, ncomp_y, max_iter, tol };
```

### Multi-predictor list pattern (from `concurrent_regression` in `regression_mod.rs:1038-1058`):
```rust
// Accept as Vec<PyReadonlyArray2<...>> (Python list of 2D arrays)
let pred_mats: Vec<fdars_core::matrix::FdMatrix> = predictors
    .into_iter()
    .map(numpy2d_to_fdmatrix)
    .collect::<PyResult<Vec<_>>>()?;
let pred_refs: Vec<&fdars_core::matrix::FdMatrix> = pred_mats.iter().collect();

// Accept argvals_list as Vec<PyReadonlyArray1<...>>
let argvals_vecs: Vec<Vec<f64>> = argvals_list.into_iter().map(numpy1d_to_vec).collect();
let argvals_refs: Vec<&[f64]> = argvals_vecs.iter().map(|v| v.as_slice()).collect();

// Then call:
fdars_core::scalar_on_function::fregre_gkam(
    &pred_refs, &y, &argvals_refs, sc.as_ref(), &config
)?;
```

---

## Section 9: Registration Mechanics

### Edit 1: `src/lib.rs` — add module declaration [VERIFIED: src/lib.rs:1-67]

Add after line 29 (`mod fts_mod;`):
```rust
mod scalar_on_function_mod;
```

Add after line 64 (`register_submodule!(m, "fts", fts_mod::register);`):
```rust
register_submodule!(m, "scalar_on_function", scalar_on_function_mod::register);
```

### Edit 2: `src/regression_mod.rs` — add 5 FOF functions to `register` [VERIFIED: regression_mod.rs:1195-1221]

Add to the `pub fn register(m: ...)` block (after line 1218 `functional_glm`):
```rust
m.add_function(wrap_pyfunction!(fof_regression, m)?)?;
m.add_function(wrap_pyfunction!(predict_fof, m)?)?;
m.add_function(wrap_pyfunction!(fof_cv, m)?)?;
m.add_function(wrap_pyfunction!(fof_re_regression, m)?)?;
m.add_function(wrap_pyfunction!(predict_fof_re, m)?)?;
```

### Edit 3: `python/fdars/__init__.py` — add `"scalar_on_function"` to name list [VERIFIED: __init__.py:35-57]

Add after line 56 (`"fts",`):
```python
"scalar_on_function",  # Phase 68 — Scalar-on-Function additive/selection regression
```

Also update the module docstring bullet on line 20 to include the new submodule capabilities.

### New file: `src/scalar_on_function_mod.rs`

```rust
//! Scalar-on-function additive and variable selection regression bindings.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// [fam, fregre_gkam, fregre_gsam, variable_selection, model_selection_ncomp bindings]

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fam, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_gkam, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_gsam, m)?)?;
    m.add_function(wrap_pyfunction!(variable_selection, m)?)?;
    m.add_function(wrap_pyfunction!(model_selection_ncomp, m)?)?;
    Ok(())
}
```

---

## Section 10: PyDict Key Tables (for planner task actions)

### `fof_regression` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"intercept"` | numpy 1D | (m_y,) | `result.intercept` |
| `"beta_surface"` | numpy 2D | (m_y, m_x) | `result.beta_surface` via `fdmatrix_to_numpy2d` |
| `"fitted"` | numpy 2D | (n, m_y) | `result.fitted` |
| `"residuals"` | numpy 2D | (n, m_y) | `result.residuals` |
| `"r_squared_t"` | numpy 1D | (m_y,) | `result.r_squared_t` |
| `"r_squared"` | float | scalar | `result.r_squared` |
| `"ncomp_x"` | int | scalar | `result.ncomp_x` |
| `"ncomp_y"` | int | scalar | `result.ncomp_y` |
| `"coef_matrix"` | numpy 2D | (ncomp_x, ncomp_y) | `result.coef_matrix` |

`fpca_x` and `fpca_y` are NOT exposed — they are internal FPCA state reused by `predict_fof`.

### `predict_fof` returns:
numpy 2D of shape `(n_new, m_y)` — **no PyDict**.

### `fof_cv` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"candidates"` | list of (int, int) | len=n_candidates | `result.candidates` |
| `"cv_errors"` | numpy 1D | (n_candidates,) | `result.cv_errors` |
| `"optimal"` | tuple (int, int) | — | `result.optimal` |
| `"min_cv_mse"` | float | scalar | `result.min_cv_mse` |

### `fof_re_regression` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"intercept"` | numpy 1D | (m_y,) | `result.intercept` |
| `"beta_surface"` | numpy 2D | (m_y, m_x) | `result.beta_surface` |
| `"fitted"` | numpy 2D | (n, m_y) | `result.fitted` |
| `"residuals"` | numpy 2D | (n, m_y) | `result.residuals` |
| `"r_squared_t"` | numpy 1D | (m_y,) | `result.r_squared_t` |
| `"r_squared"` | float | scalar | `result.r_squared` |
| `"ncomp_x"` | int | scalar | `result.ncomp_x` |
| `"ncomp_y"` | int | scalar | `result.ncomp_y` |
| `"coef_matrix"` | numpy 2D | (ncomp_x, ncomp_y) | `result.coef_matrix` |
| `"random_effects"` | numpy 2D | (n_subjects, m_y) | `result.random_effects` |
| `"sigma2_u"` | numpy 1D | (ncomp_y,) | `result.sigma2_u` |
| `"sigma2_eps"` | float | scalar | `result.sigma2_eps` |
| `"n_subjects"` | int | scalar | `result.n_subjects` |

### `predict_fof_re` returns:
numpy 2D of shape `(n_new, m_y)` — **no PyDict**.

### `fam` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"fitted_values"` | numpy 1D | (n,) | `result.fitted_values` |
| `"residuals"` | numpy 1D | (n,) | `result.residuals` |
| `"component_fits"` | list of numpy 1D | ncomp entries | `result.component_fits` |
| `"intercept"` | float | scalar | `result.intercept` |
| `"bandwidths"` | numpy 1D | (ncomp,) | `result.bandwidths` |
| `"ncomp"` | int | scalar | `result.ncomp` |
| `"r_squared"` | float | scalar | `result.r_squared` |

### `fregre_gkam` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"fitted_values"` | numpy 1D | (n,) | `result.fitted_values` |
| `"residuals"` | numpy 1D | (n,) | `result.residuals` |
| `"component_fits"` | list of numpy 1D | q entries | `result.component_fits` |
| `"intercept"` | float | scalar | `result.intercept` |
| `"bandwidths"` | numpy 1D | (q,) | `result.bandwidths` |
| `"iterations"` | int | scalar | `result.iterations` |
| `"converged"` | bool | scalar | `result.converged` |
| `"r_squared"` | float | scalar | `result.r_squared` |

### `fregre_gsam` returns:
Same keys as `fam` (7 keys) — identical struct layout, different estimation method.

### `variable_selection` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"active_predictors"` | numpy 1D bool | (P,) | `result.active_predictors` via `bool_vec_to_numpy1d` |
| `"coefficients"` | list of numpy 1D | P entries, each (K_p,) | `result.coefficients` |
| `"fitted_values"` | numpy 1D | (n,) | `result.fitted_values` |
| `"residuals"` | numpy 1D | (n,) | `result.residuals` |
| `"intercept"` | float | scalar | `result.intercept` |
| `"lambda"` | float | scalar | `result.lambda` |
| `"r_squared"` | float | scalar | `result.r_squared` |
| `"iterations"` | int | scalar | `result.iterations` |
| `"converged"` | bool | scalar | `result.converged` |

### `model_selection_ncomp` returns:
| Key | Type | Shape | Source field |
|-----|------|-------|--------------|
| `"best_ncomp"` | int | scalar | `result.best_ncomp` |
| `"criteria"` | list of (int, float, float, float) | max_comp entries | `result.criteria` |

---

## Section 11: Test Architecture

### Non-square fixtures (REQUIRED):

**FOF fixture:**
```python
import numpy as np
N, MX, MY = 30, 25, 18   # n_obs=30, m_x=25, m_y=18 — all three distinct
assert N != MX and N != MY and MX != MY

rng = np.random.default_rng(42)
x_argvals = np.linspace(0.0, 1.0, MX)
y_argvals = np.linspace(0.0, 1.0, MY)

# FOF training data: X drives Y via integral coupling
x_data = rng.standard_normal((N, MX))
# Y constructed to have true FOF signal
x_scores = x_data @ np.sin(np.pi * x_argvals[:, None]).reshape(-1, 1)
y_data = x_scores @ np.cos(np.pi * y_argvals[None, :]) + 0.1 * rng.standard_normal((N, MY))
assert x_data.shape == (N, MX)
assert y_data.shape == (N, MY)

# new_x for predict (n_new = 10, same m_x = 25)
new_x = rng.standard_normal((10, MX))

# subject_ids for RE: 5 subjects × 6 obs each
subject_ids = np.array([i // 6 for i in range(N)], dtype=np.int64)
assert len(np.unique(subject_ids)) == 5
```

**SOF additive fixture:**
```python
N, M = 30, 20   # n_obs=30, m_points=20 — non-square
argvals = np.linspace(0.0, 1.0, M)
data = rng.standard_normal((N, M))
y = np.sin(np.pi * data.mean(axis=1)) + 0.1 * rng.standard_normal(N)

# Multi-predictor fixture for fregre_gkam and variable_selection:
M2 = 15   # second predictor has different grid size
data2 = rng.standard_normal((N, M2))
argvals2 = np.linspace(0.0, 1.0, M2)
```

### Shape assertions (transposition guard):
```python
# fof_regression
r = reg.fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)
assert r["beta_surface"].shape == (MY, MX)   # (18, 25) — NOT (25, 18)
assert r["fitted"].shape == (N, MY)           # (30, 18)
assert r["intercept"].shape == (MY,)          # (18,)
assert r["r_squared_t"].shape == (MY,)        # (18,)
assert r["coef_matrix"].shape == (3, 3)       # (ncomp_x, ncomp_y)

# predict_fof
pred = reg.predict_fof(x_data, y_data, new_x, x_argvals, y_argvals)
assert pred.shape == (10, MY)   # (10, 18)

# fof_re_regression
r_re = reg.fof_re_regression(x_data, y_data, subject_ids, x_argvals, y_argvals)
assert r_re["random_effects"].shape == (5, MY)  # n_subjects=5, m_y=18
assert r_re["sigma2_u"].shape == (3,)            # ncomp_y=3
```

### Minimum test coverage required:
1. **Import smoke** — `import fdars.regression as reg; import fdars.scalar_on_function as sof`
2. **`fof_regression` end-to-end + shape assertions** — non-square `(30, 25, 18)` fixture
3. **`predict_fof`** — verify `(10, 18)` output; same result as fitting then predicting on new_x
4. **`fof_cv`** — verify `candidates` is a list of 2-tuples; `optimal` is a 2-tuple; `min_cv_mse > 0`
5. **`fof_re_regression` + shape assertions** — subject_ids with 5 groups; verify `random_effects` shape `(5, 18)`, `n_subjects == 5`
6. **`predict_fof_re`** — verify `(10, 18)` output
7. **Subject-id validation** — wrong length raises `ValueError`; single group raises `ValueError`
8. **`fam`** — non-square `(30, 20)` fixture; verify `fitted_values` shape `(30,)`, `component_fits` is a list
9. **`fregre_gkam`** — 2-predictor list `[(30,20), (30,15)]`; verify `converged` is bool, `bandwidths` shape `(2,)`
10. **`fregre_gsam`** — single predictor; verify output keys match `fam` keys
11. **`variable_selection`** — 2-predictor list; verify `active_predictors` shape `(2,)`; `coefficients` is a list of 2 arrays; penalty="group_lasso" and penalty="ls" both work; invalid penalty raises `ValueError`
12. **`model_selection_ncomp`** — verify `best_ncomp >= 1`; `criteria` is a list of tuples; criterion="aic"/"bic"/"gcv" all work
13. **Error guards** — `fof_regression` with ncomp_x=0 raises `ValueError`; `fof_cv` with n_folds > n raises `ValueError`

---

## Section 12: Common Pitfalls

### Pitfall 1: Exposing `fpca_x`/`fpca_y` from `FofResult`/`FofReResult`
**What goes wrong:** `FpcaResult` contains `FdMatrix` fields; trying to expose it as a dict-of-dicts
is significant work and exposes internal state not needed by users.
**How to avoid:** Explicitly skip `fpca_x`, `fpca_y` (FOF) and `fpca`/`fpcas` (additive) when
building PyDicts. Only the 9/13/7/8/7/9/2 keys listed in §10 are exposed.

### Pitfall 2: `beta_surface` shape confusion
**What goes wrong:** `FofResult.beta_surface` is `(m_y × m_x)` in FdMatrix — rows index response
grid, cols index predictor grid. A test with a square fixture `(MX == MY)` would not catch if the
shape is swapped.
**How to avoid:** Use `(N, MX, MY) = (30, 25, 18)` and assert `r["beta_surface"].shape == (MY, MX) == (18, 25)`.

### Pitfall 3: `fregre_gkam` / `variable_selection` multi-predictor binding
**What goes wrong:** Rust signature is `&[&FdMatrix]` (slice of references) but Rust cannot build
this directly from a `Vec<FdMatrix>` without intermediate collection. Forgetting the reference
collection step produces a lifetime error.
**How to avoid:** Always build `Vec<FdMatrix>` first, then `Vec<&FdMatrix>`:
```rust
let pred_mats: Vec<FdMatrix> = predictors.into_iter().map(numpy2d_to_fdmatrix).collect::<PyResult<_>>()?;
let pred_refs: Vec<&FdMatrix> = pred_mats.iter().collect();
```

### Pitfall 4: `FamConfig` / `GkamConfig` / `GsamConfig` are `#[non_exhaustive]`
**What goes wrong:** Struct literal construction `FamConfig { ncomp: 3, ... }` fails to compile with
`#[non_exhaustive]` unless in the same crate.
**How to avoid:** Use `Default::default()` + field mutation:
```rust
let mut cfg = fdars_core::scalar_on_function::FamConfig::default();
cfg.ncomp = ncomp;
cfg.bandwidth = bandwidth;
```

### Pitfall 5: `VarSelectPenalty::GroupMcp`/`GroupScad` crash at runtime, not compile time
**What goes wrong:** Even if the enum variant can be matched, `variable_selection` internally returns
`FdarError::InvalidParameter` for `GroupMcp`/`GroupScad`. A user passing `penalty="group_mcp"` would
get a confusing error.
**How to avoid:** Reject at the binding level with a clear message (see §2). The `Err` arm in
`penalty_from_str` provides a better error than the upstream one.

### Pitfall 6: `model_selection_ncomp` already exists in `regression_mod.rs`
**What goes wrong:** If the planner adds `model_selection_ncomp` to `regression_mod.rs` AGAIN (for
the fof group), there will be a duplicate `#[pyfunction]` compile error.
**How to avoid:** `model_selection_ncomp` goes into `scalar_on_function_mod.rs` ONLY. The existing
binding in `regression_mod.rs` stays and is NOT touched by Phase 68. Phase 68 adds a second
registration of the same underlying logic in the new submodule.

### Pitfall 7: `fof_cv` seed type
**What goes wrong:** `fof_cv` takes `seed: u64`. Python users typically pass ints; PyO3 coerces
Python `int` to `u64` automatically, but negative values will wrap. Default `seed=42u64`.

### Pitfall 8: subject_ids single-group degeneracy
**What goes wrong:** `fof_re_regression` with all observations in one group is technically valid at
the upstream level (the REML EM loop will converge, but the random intercept variance is undefined).
**How to avoid:** Binding validates `n_subjects ≥ 2` before calling upstream (see §6).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Config struct construction | Manual Python dict→Rust config converter | `Default::default()` + field mutation | `#[non_exhaustive]` prevents struct literals |
| Multi-predictor list input | Custom Python wrapper class | `Vec<PyReadonlyArray2>` (identical to `concurrent_regression`) | Already established pattern in `regression_mod.rs:1038` |
| Subject-id validation | Complex unique-count algorithm | `sid.sort_unstable(); sid.dedup(); sid.len()` | Simple, allocation-minimal |
| `FpcaResult` serialization | Dict-of-dicts embedded FPCA | Skip `fpca_x`/`fpca_y`/`fpca`/`fpcas` entirely | Internal state; not needed for user inspection |
| Predict-from-dict | Deserialize PyDict → Rust struct | Combined-refit pattern (refit internally) | Phase-67 precedent; avoids opaque handles |

---

## Standard Stack

No new dependencies. Phase 68 uses exclusively:
- `fdars-core 0.33.0` (already in `Cargo.toml` at `parallel` feature)
- `pyo3 0.28` (already in `Cargo.toml`)
- `numpy 0.28` (already in `Cargo.toml`)
- `convert.rs` utilities (project-local)

No packages to install. No package legitimacy audit required.

---

## Architecture Patterns

### Recommended Project Structure Changes
```
src/
├── regression_mod.rs         # EDIT — add 5 fof functions to existing register() block
├── scalar_on_function_mod.rs # NEW — 5 sof additive/selection bindings
├── lib.rs                    # EDIT — mod scalar_on_function_mod; + register_submodule!
python/fdars/
├── __init__.py               # EDIT — add "scalar_on_function" to _submodule_names
tests/
├── test_fof_regression.py    # NEW — tests for the 5 fof functions (fdars.regression)
├── test_scalar_on_function.py # NEW — tests for the 5 sof functions (fdars.scalar_on_function)
```

### Pattern: Thin `#[pyfunction]` with required argvals (from `regression_mod.rs:23-45`)
```rust
#[pyfunction]
#[pyo3(signature = (x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3))]
pub fn fof_regression<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x: usize,
    ncomp_y: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);
    let result = to_pyresult(fdars_core::fof_regression::fof_regression(
        &x_mat, &y_mat, &ax, &ay, ncomp_x, ncomp_y,
    ))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("intercept", vec_to_numpy1d(py, result.intercept))?;
    dict.set_item("beta_surface", fdmatrix_to_numpy2d(py, &result.beta_surface))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &result.residuals))?;
    dict.set_item("r_squared_t", vec_to_numpy1d(py, result.r_squared_t))?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("ncomp_x", result.ncomp_x)?;
    dict.set_item("ncomp_y", result.ncomp_y)?;
    dict.set_item("coef_matrix", fdmatrix_to_numpy2d(py, &result.coef_matrix))?;
    Ok(dict.into_any())
}
```

### Pattern: Option<FdMatrix> scalar_covariates (from `fregre_np_cv` in `regression_mod.rs:900-903`)
```rust
let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;
// then pass: sc.as_ref()
```

### Pattern: Multi-predictor list (from `concurrent_regression` in `regression_mod.rs:1044-1050`)
```rust
let pred_mats: Vec<fdars_core::matrix::FdMatrix> = predictors
    .into_iter()
    .map(numpy2d_to_fdmatrix)
    .collect::<PyResult<Vec<_>>>()?;
let pred_refs: Vec<&fdars_core::matrix::FdMatrix> = pred_mats.iter().collect();
```

### Pattern: Combined-refit predict (from Phase 67 `ftsm_forecast`)
```rust
// 1. Refit the model from raw data
let fit = to_pyresult(fdars_core::fof_regression::fof_regression(
    &x_mat, &y_mat, &ax, &ay, ncomp_x, ncomp_y,
))?;
// 2. Predict on new data using the fitted model
let predicted = to_pyresult(fdars_core::fof_regression::predict_fof(&fit, &new_x_mat))?;
// 3. Return numpy 2D (not a PyDict)
Ok(fdmatrix_to_numpy2d(py, &predicted).into_any())
```

### Anti-Patterns to Avoid
- **Square fixture (MX == MY):** Hides `(m_y, m_x)` vs `(m_x, m_y)` swap in `beta_surface`.
- **Exposing embedded `FpcaResult`:** Not needed by users; difficult to serialize; intentionally excluded.
- **`Dict`-to-`FofResult` reconstruction:** Python cannot deserialize a PyDict to a Rust struct. Use combined-refit.
- **Struct-literal on `#[non_exhaustive]` config:** Compile error. Use `default()` + mutation.

---

## Assumptions Log

All claims in this research were verified by reading the fdars-core 0.33.0 registry source and
pyfda project files this session. The Assumptions Log is empty.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | — | — | — |

**All claims verified by reading fdars-core 0.33.0 registry source and pyfda project files this session.**

---

## Open Questions

None. The Phase 68 API surface is fully documented in the 0.33 source, the project conventions are
established, and the registration mechanics are clear from existing modules and the Phase 67 precedent.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 68 is a code-only change (two Rust source file edits + one new file + two
registration edits + two test files). No new external dependencies. The build environment (maturin +
Rust 1.83+ + cargo) was confirmed working by Phase 66 (crate bump + regression gate passed) and by
Phase 67 (successful `maturin develop` + test run).

---

## Validation Architecture

`workflow.nyquist_validation` is `false` in `.planning/config.json`. Section skipped per config.

---

## Security Domain

Phase 68 adds no networked components, no authentication, no cryptography, no external service calls.
All computations are pure numerical Rust, called synchronously from Python. ASVS categories V2-V6
do not apply. Input validation (V5) is handled by fdars-core's own guards (`FdarError::InvalidDimension`
/ `InvalidParameter`) plus the additional subject-id validation added in the binding (§6), both
propagated to Python as `ValueError` via `to_pyresult`.

---

## Sources

### Primary (HIGH confidence — read directly from source files this session)
- `fdars-core-0.33.0/src/fof_regression.rs` (lines 1-980) — all FOF function signatures, `FofResult`, `FofCvResult`, `FofReResult`, `FofReConfig` fields, `predict_fof`, `predict_fof_re` implementations
- `fdars-core-0.33.0/src/scalar_on_function/additive.rs` (lines 63-1353) — `FamConfig`, `GkamConfig`, `GsamConfig`, `VarSelectConfig`, `VarSelectPenalty`, `FamResult`, `GkamResult`, `GsamResult`, `VarSelectResult` fields; `fam`, `fregre_gkam`, `fregre_gsam`, `variable_selection` signatures
- `fdars-core-0.33.0/src/scalar_on_function/mod.rs` (lines 1-703) — `SelectionCriterion`, `ModelSelectionResult`, `GlmFamily` (for context); module re-exports confirming public paths
- `fdars-core-0.33.0/src/scalar_on_function/fregre_lm.rs` (lines 362-413) — `model_selection_ncomp` signature
- `fdars-core-0.33.0/src/lib.rs` (lines 95, 110) — confirming `pub mod fof_regression` and `pub mod scalar_on_function` at crate root
- `src/regression_mod.rs` (all 1222 lines) — existing binding patterns, `family_from_str`, `concurrent_regression`, `model_selection_ncomp`, `predict_fregre_lm` (combined-refit pattern)
- `src/lib.rs` (all 67 lines) — `register_submodule!` macro, current submodule list, line numbers for edits
- `python/fdars/__init__.py` (lines 1-79) — `_submodule_names` tuple, docstring, registration loop
- `src/convert.rs` (all 94 lines) — `numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `numpy1d_to_usize_vec`, `bool_vec_to_numpy1d`, `to_pyresult`
- `src/fts_mod.rs` (Phase 67 output) — combined-function pattern precedent (via 67-RESEARCH.md §6)

### Secondary (for context)
- `.planning/phases/68-function-on-function-scalar-on-function-regression/68-CONTEXT.md` — locked decisions
- `.planning/REQUIREMENTS.md` — REG-01, REG-02, REG-03
- `.planning/STATE.md` — blockers and concerns
- `.planning/phases/67-functional-time-series-fts/67-RESEARCH.md` — combined-function pattern worked example

---

## Metadata

**Confidence breakdown:**
- Function signatures (all 10): HIGH — read verbatim from 0.33 registry source this session
- Result struct field names: HIGH — read verbatim from 0.33 source; this was the key risk flagged in STATE.md, now resolved
- Registration mechanics: HIGH — read from `src/lib.rs` and `python/fdars/__init__.py` this session
- Enum/config patterns: HIGH — `VarSelectPenalty`, `FamConfig`, `FofReConfig` non-exhaustive status all verified from source
- Combined-refit architecture: HIGH — Phase 67 precedent implemented and tested; Phase 68 applies identical pattern

**Research date:** 2026-09-02
**Valid until:** 2026-12-01 (fdars-core stable; only invalid if crate version bumps again)
