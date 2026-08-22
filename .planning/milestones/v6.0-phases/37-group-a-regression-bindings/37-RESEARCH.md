# Phase 37: Group A — Regression Bindings - Research

**Researched:** 2026-08-20
**Domain:** PyO3 binding layer — `concurrent_regression` + `functional_glm` in `fdars.regression`
**Confidence:** HIGH (all signatures, struct fields, enum variants, and test patterns read directly from fdars-core v0.23.0 git tag and pyfda source files this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- `fdars.regression.concurrent_regression(predictors, response, argvals, ...)` — `predictors` is a Python `list[np.ndarray]` (slice-of-matrices; one (n_obs × m) matrix per predictor). Returns a `dict` mirroring `ConcurrentRegrResult` fields: `beta_curve`, `intercept`, `fitted`, `residuals`, `argvals`.
- `fdars.regression.functional_glm(data, response, argvals, family=..., n_comp=..., ...)` — returns a `dict` mirroring all `FunctionalGlmResult` fields. Wrapper re-fits FPCA internally (raw data in, no persistent handle) — same pattern as the v5.0 `flm_f_test` binding.
- One converter per result struct (`concurrent_regr_result_to_pydict`, `functional_glm_result_to_pydict`), following the canonical `test_result_to_pydict` pattern in `inference_mod.rs`. `FdMatrix` fields convert via the existing `fdmatrix_to_numpy2d` helper; `Vec<f64>` → 1-D numpy; scalars → Python floats (never numpy scalars).
- `ConcurrentRegrResult.beta_curve` is `(p, m)` (predictors × grid), NOT the pyfda-standard `(n_obs, m)`. Convert faithfully; add an explicit multi-predictor (`p ≥ 2`) transposition guard test.
- `family` is a Python string dispatched to the `#[non_exhaustive]` `GlmFamily` enum via a `match` with a wildcard `_ => PyValueError` fallback listing supported families. String values: `"binomial"`, `"poisson"`, `"gamma"`, `"gaussian"`.
- All fallible calls route through `to_pyresult()` (no `.unwrap()`). Degenerate inputs raise `ValueError`.
- Both functions are registered in `src/regression_mod.rs` + `register_submodule!`.
- Gamma family uses the inverse canonical link (1/μ), NOT log. `functional_glm` AIC magnitude is not comparable to R's `glm()` — document, don't "fix". (Carry to Phase 41 DOCS-08.)

### Claude's Discretion

Everything not pinned above (exact parameter defaults, test data choices, dict key names matching struct fields) is at Claude's discretion, grounded in the v0.23.0 source signatures and existing `regression_mod.rs` conventions. No Fdata convenience methods this phase (submodule functions only, matching the requirements).

### Deferred Ideas (OUT OF SCOPE)

- Advisor coverage of `functional_glm`/`concurrent_regression` — Phase 40 (ADV-05).
- Docs pages + SVGs + worked examples — Phase 41 (DOCS-08).
- PACE-FPCA / elastic_multinomial — Phase 38 (Group B).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REGR-01 | `concurrent_regression` binding: `predictors` as `list[np.ndarray]`, result dict with `beta_curve` at `(p, m)`, multi-predictor transposition guard test | Full signature verified from v0.23.0; struct fields confirmed; test pattern established |
| REGR-02 | `functional_glm` binding: all `FunctionalGlmResult` fields exposed; `GlmFamily` string dispatch; FPCA re-fits internally; Gamma inverse-link caveat documented | Full signature verified; all 15 result fields confirmed; enum variants confirmed `#[non_exhaustive]` |
| REGR-03 | Both functions in `regression_mod.rs` + `register_submodule!`; one PyDict converter each; all fallible paths via `to_pyresult()`; degenerate inputs raise `ValueError` | Patterns established from `inference_mod.rs`; `to_pyresult` confirmed; error types confirmed |
</phase_requirements>

---

## Summary

This phase adds two PyO3 bindings inside `src/regression_mod.rs`: `concurrent_regression` (varying-coefficient functional regression) and `functional_glm` (exponential-family GLM over FPC scores). Both are in fdars-core `v0.23.0` and fully accessible under `fdars_core::concurrent_regression::concurrent_regression` and `fdars_core::scalar_on_function::functional_glm` respectively.

The structural novelty is in `concurrent_regression`'s input: `predictors: &[FdMatrix]` (a slice of matrices) maps to a Python `list[np.ndarray]`. Each element must be individually converted via `numpy2d_to_fdmatrix` and collected into a `Vec<FdMatrix>` before the Rust call. This is the only new pattern; everything else follows exact analogues already in the codebase.

`functional_glm` adds the complexity of a 15-field result struct, a `GlmFamily` string-dispatch (matching the `MultiplierDistribution` dispatch pattern from `inference_mod.rs`), and an `fpca` field that must **not** cross the Python boundary (the embedded `FpcaResult` is consumed internally for fit but not exposed to Python — same pattern as `flm_f_test`/`flm_gof_test`).

**Primary recommendation:** Implement both functions in a single commit to `src/regression_mod.rs` following the four-step pattern: (1) convert inputs, (2) call core function through `to_pyresult()`, (3) convert result struct to `PyDict` via a dedicated private helper, (4) register via `m.add_function(wrap_pyfunction!(...))`. Add a transposition guard test for `beta_curve` at `p = 3` and a `ValueError` test for each documented degenerate-input case.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `concurrent_regression` computation | Rust (fdars-core) | — | Algorithm runs in Rust; Python side is a thin wrapper only |
| `functional_glm` IRLS loop + FPCA | Rust (fdars-core) | — | FPCA re-fit and IRLS both run inside `fdars_core::scalar_on_function::functional_glm` |
| `list[np.ndarray]` → `Vec<FdMatrix>` conversion | PyO3 wrapper (`regression_mod.rs`) | — | Each element converted via existing `numpy2d_to_fdmatrix` helper |
| `GlmFamily` string dispatch | PyO3 wrapper (`regression_mod.rs`) | — | Match on `&str` → `GlmFamily` variant; wildcard arm produces `PyValueError` |
| Result struct → PyDict conversion | PyO3 wrapper (`regression_mod.rs`) | — | Private helper functions (`concurrent_regr_result_to_pydict`, `functional_glm_result_to_pydict`) |
| Python API registration | `regression_mod.rs::register()` | `src/lib.rs` (already wired) | `register_submodule!` in `lib.rs` already registers `fdars.regression`; no new registration needed |

---

## Standard Stack

### Core (all already in Cargo.toml / pyproject.toml)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fdars-core` | 0.23.0 | Rust computation engine providing `concurrent_regression` and `functional_glm` | Locked at v0.23.0 per DEP-05; [VERIFIED: /home/simonm/projects/rust/pyfda/Cargo.toml:line with `fdars-core = { version = "0.23.0"}`] |
| `pyo3` | 0.28 | Rust-Python bindings | Already in Cargo.toml; all existing bindings use this version |
| `numpy` (PyO3) | 0.28 | `PyReadonlyArray1/2`, `PyArray1/2` | Paired with pyo3 0.28; used throughout pyfda for array conversion |
| `pytest` | 9.0.3 | Python test runner | [VERIFIED: `.venv/bin/pytest --version`] |
| `maturin` | 1.13.1 | Build backend for `maturin develop` | [VERIFIED: `.venv/bin/maturin --version`] |

### No New Dependencies

This phase introduces no new Rust crate dependencies and no new Python packages. All required conversion helpers already exist in `src/convert.rs`.

---

## Package Legitimacy Audit

No new packages are introduced in this phase. All dependencies were installed in prior milestones (DEP-05/DEP-06 completed). This section is not applicable.

---

## Architecture Patterns

### System Architecture Diagram

```
Python caller
  |
  | list[np.ndarray]   np.ndarray (2D)   str ("poisson")   np.ndarray (1D)
  v
regression_mod.rs  (#[pyfunction] concurrent_regression / functional_glm)
  |                         |
  | numpy2d_to_fdmatrix()   | numpy2d_to_fdmatrix()
  | per element in list     | family_from_str() -> GlmFamily
  | collect Vec<FdMatrix>   | numpy1d_to_vec(response)
  v                         v
fdars_core::concurrent_regression::concurrent_regression(response, &predictors, ...)
fdars_core::scalar_on_function::functional_glm(data, y, family, ...)
  |                         |
  | Result<ConcurrentRegrResult, FdarError>
  | Result<FunctionalGlmResult, FdarError>
  v
to_pyresult() -- ValueError on Err
  |
concurrent_regr_result_to_pydict()   functional_glm_result_to_pydict()
  |                                   |
  | fdmatrix_to_numpy2d (FdMatrix)    | vec_to_numpy1d (Vec<f64>)
  | vec_to_numpy1d (Vec<f64>)         | scalar (f64/usize) -> Python
  | scalar (f64) -> Python float      | family as &str
  v                                   v
Bound<'py, PyDict>  returned as PyAny to Python
```

### Recommended Project Structure

No new files are needed. All code is added to existing files:

```
src/
├── regression_mod.rs    # ADD: concurrent_regression, functional_glm pyfunction bodies
│                        # ADD: concurrent_regr_result_to_pydict, functional_glm_result_to_pydict
│                        # ADD: family_from_str helper
│                        # ADD: m.add_function() calls in register()
├── convert.rs           # No changes needed
└── lib.rs               # No changes needed (register_submodule! for regression already wired)
tests/
└── test_regression.py   # ADD: new test class for concurrent_regression and functional_glm
                         # (or new test file test_regression_new.py if test_regression.py exists)
```

### Pattern 1: Slice-of-matrices input (`concurrent_regression` predictors)

**What:** Python `list[np.ndarray]` → `Vec<FdMatrix>`. There is no prior precedent in pyfda for accepting a Python list of arrays; all existing functions accept single 2D arrays.

**When to use:** Whenever fdars-core requires `&[FdMatrix]`.

**Example:**
```rust
// Source: derived from existing numpy2d_to_fdmatrix pattern in convert.rs
#[pyfunction]
#[pyo3(signature = (predictors, response, argvals, bandwidth, kernel="gaussian"))]
pub fn concurrent_regression<'py>(
    py: Python<'py>,
    predictors: Vec<PyReadonlyArray2<'py, f64>>,  // Python list[np.ndarray] maps to Vec
    response: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
    bandwidth: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyAny>> {
    // Convert each element
    let pred_mats: Vec<FdMatrix> = predictors
        .into_iter()
        .map(numpy2d_to_fdmatrix)
        .collect::<PyResult<Vec<_>>>()?;
    let resp_mat = numpy2d_to_fdmatrix(response)?;
    let av: Option<Vec<f64>> = argvals.map(numpy1d_to_vec);
    let result = to_pyresult(fdars_core::concurrent_regression::concurrent_regression(
        &resp_mat,
        &pred_mats,
        av.as_deref(),
        bandwidth,
        kernel,
    ))?;
    concurrent_regr_result_to_pydict(py, result)
}
```

**NOTE on Python argument type:** PyO3 0.28 supports `Vec<PyReadonlyArray2<'py, f64>>` as a parameter type — Python `list[np.ndarray]` is accepted. Each element is individually converted in the `map` chain. [VERIFIED: pyo3 0.28 docs — `FromPyObject` is implemented for `Vec<T>` when `T: FromPyObject`] [ASSUMED: the exact FromPyObject impl for Vec<PyReadonlyArray> — verify at execute time by building; fall back to `Bound<'py, PyList>` extraction if Vec<> does not bind cleanly]

### Pattern 2: Struct-to-PyDict converter (private helper)

**What:** A private `fn foo_to_pydict(py, result) -> PyResult<Bound<PyAny>>` that constructs the dict without any `.unwrap()`. Matches `test_result_to_pydict` in `inference_mod.rs:32-41`.

**When to use:** Any time a `#[non_exhaustive]` result struct must be converted to a Python dict. Never access fields via struct literal — always access each named field individually (struct-literal construction of `#[non_exhaustive]` structs is forbidden outside the defining crate).

**Example:**
```rust
// Source: mirrors inference_mod.rs:32-41 (test_result_to_pydict pattern)
fn concurrent_regr_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::concurrent_regression::ConcurrentRegrResult,
) -> PyResult<Bound<'py, PyAny>> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("beta_curve", fdmatrix_to_numpy2d(py, &r.beta_curve))?;
    dict.set_item("intercept", vec_to_numpy1d(py, r.intercept))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &r.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &r.residuals))?;
    dict.set_item("argvals", vec_to_numpy1d(py, r.argvals))?;
    Ok(dict.into_any())
}
```

### Pattern 3: `#[non_exhaustive]` enum dispatch (family_from_str)

**What:** A private helper that maps `&str` → `GlmFamily`, with a wildcard arm producing `PyValueError`. Mirrors `multiplier_from_str` in `inference_mod.rs:227-235`.

**When to use:** Any `#[non_exhaustive]` enum that must be accepted as a Python string.

**Example:**
```rust
// Source: mirrors inference_mod.rs:227-235 (multiplier_from_str pattern)
fn family_from_str(s: &str) -> PyResult<fdars_core::scalar_on_function::GlmFamily> {
    use fdars_core::scalar_on_function::GlmFamily;
    match s {
        "binomial" => Ok(GlmFamily::Binomial),
        "poisson"  => Ok(GlmFamily::Poisson),
        "gamma"    => Ok(GlmFamily::Gamma),
        "gaussian" => Ok(GlmFamily::Gaussian),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "family must be 'binomial', 'poisson', 'gamma', or 'gaussian', got '{s}'"
        ))),
    }
}
```

**NOTE on `#[non_exhaustive]`:** `GlmFamily` IS marked `#[non_exhaustive]` in v0.23.0. [VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/scalar_on_function/mod.rs:341-355 — `#[non_exhaustive]` on line 343, variants: `Binomial`, `Poisson`, `Gamma`, `Gaussian`]. The wildcard `_` arm in the `match` is therefore required even though the enum is fully covered at v0.23 — a future upstream addition would otherwise be a compile error.

### Pattern 4: `functional_glm` — fpca field not exposed

**What:** The `FunctionalGlmResult.fpca: FpcaResult` field is consumed internally for predictions but must NOT be inserted into the Python dict. This mirrors `flm_f_test` / `flm_gof_test` in `inference_mod.rs:411-426`, where `FregreLmResult` is created and used but never returned to Python.

**When to use:** Whenever a result struct embeds another Rust struct for internal use only.

```rust
fn functional_glm_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::scalar_on_function::FunctionalGlmResult,
) -> PyResult<Bound<'py, PyAny>> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("intercept", r.intercept)?;
    dict.set_item("beta_t", vec_to_numpy1d(py, r.beta_t))?;
    dict.set_item("beta_se", vec_to_numpy1d(py, r.beta_se))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, r.fitted_values))?;
    dict.set_item("linear_predictors", vec_to_numpy1d(py, r.linear_predictors))?;
    dict.set_item("ncomp", r.ncomp)?;
    dict.set_item("coefficients", vec_to_numpy1d(py, r.coefficients))?;
    dict.set_item("std_errors", vec_to_numpy1d(py, r.std_errors))?;
    dict.set_item("log_likelihood", r.log_likelihood)?;
    dict.set_item("deviance", r.deviance)?;
    dict.set_item("iterations", r.iterations)?;
    dict.set_item("aic", r.aic)?;
    dict.set_item("bic", r.bic)?;
    // family exposed as string matching the accepted input tokens
    let family_str = match r.family {
        fdars_core::scalar_on_function::GlmFamily::Binomial => "binomial",
        fdars_core::scalar_on_function::GlmFamily::Poisson  => "poisson",
        fdars_core::scalar_on_function::GlmFamily::Gamma    => "gamma",
        fdars_core::scalar_on_function::GlmFamily::Gaussian => "gaussian",
        // wildcard required: GlmFamily is #[non_exhaustive]
        _ => "unknown",
    };
    dict.set_item("family", family_str)?;
    // r.fpca is intentionally NOT inserted — embedded for internal use only
    Ok(dict.into_any())
}
```

### Anti-Patterns to Avoid

- **Accessing `#[non_exhaustive]` structs via struct literals:** Both `ConcurrentRegrResult` and `FunctionalGlmResult` are `#[non_exhaustive]`. Never construct them with `ConcurrentRegrResult { ... }` in binding code — only access individual `.field_name` members. [VERIFIED: v0.23.0 source, `#[non_exhaustive]` on both structs]
- **Using `.unwrap()` on any fallible call:** All `Result`-returning core calls go through `to_pyresult()` (which maps `FdarError` → `PyValueError`). No `expect()` or `unwrap()` anywhere in the two new functions or their converters.
- **Passing `None` for argvals when the caller does not supply it — but not optional in Python API:** The Python `concurrent_regression` signature accepts `argvals` as `Option<PyReadonlyArray1<'py, f64>>`. When `None`, pass `None` to Rust core which then generates a uniform 0..1 grid. Do not synthesise the grid on the Python side.
- **Hardcoding `max_iter=0` or `tol=0.0` in `functional_glm`:** The Rust core interprets `max_iter == 0` as "use default 25" and `tol <= 0.0` as "use default 1e-6". Surface the defaults as explicit Python-side defaults instead (e.g. `max_iter=25, tol=1e-6`) to be transparent to callers.
- **Calling `numpy2d_to_fdmatrix` on entire Python list instead of per-element:** `numpy2d_to_fdmatrix` converts a single `PyReadonlyArray2`. The list must be iterated element-by-element.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Varying-coefficient regression algorithm | Custom kernel smoother + OLS | `fdars_core::concurrent_regression::concurrent_regression` | All edge cases (ridge stabiliser, NaN bandwidth guard, n ≤ p underdetermined guard) are already handled in core |
| FPCA for GLM basis | Custom SVD | `fdars_core::scalar_on_function::functional_glm` (re-fits FPCA internally) | FPCA + IRLS loop are both inside core; re-fitting from raw data is the correct pattern |
| IRLS solver | Custom weighted normal equations | Internal to `fdars_core::scalar_on_function::glm` | Gamma IRLS weight formula (`w = μ²`, NOT `w = 1/μ²`) and Gamma intercept initialisation (`β₀ = 1/mean(y)`) are subtle; core gets these right |
| `FdMatrix` row/column layout conversion | Custom transposition | `fdmatrix_to_numpy2d` from `convert.rs` | Handles the column-major → row-major transposition correctly; hand-rolled transposition is the primary source of past bugs (v4.0 Phases 26/27) |
| Error string formatting for invalid inputs | Custom error messages | `to_pyresult()` + `PyValueError::new_err(format!(...))` | `FdarError` already carries descriptive messages; `to_pyerr()` surfaces them as Python `ValueError` |

**Key insight:** This phase is purely a thin wrapper — the entire computation is in fdars-core. Any logic added in `regression_mod.rs` beyond input validation, type conversion, and dict construction is almost certainly a mistake.

---

## Exact Signatures (v0.23.0 — Authoritative)

### `concurrent_regression`

```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/concurrent_regression.rs:92-98
pub fn concurrent_regression(
    response: &FdMatrix,         // (n, m) functional response
    predictors: &[FdMatrix],     // p matrices each (n, m); p >= 1
    argvals: Option<&[f64]>,     // length m; None -> uniform 0..1
    bandwidth: f64,              // kernel bandwidth > 0 and finite
    kernel: &str,                // "gaussian" | "epanechnikov" | "tricube"
) -> Result<ConcurrentRegrResult, FdarError>
```

**Module path:** `fdars_core::concurrent_regression::concurrent_regression`

**Validated error conditions (from source, lines 102-163):**
- `predictors.is_empty()` → `FdarError::InvalidDimension { parameter: "predictors", ... }`
- `n < 2` → `FdarError::InvalidDimension { parameter: "response", ... }`
- `m == 0` → `FdarError::InvalidDimension { parameter: "response", ... }`
- `pred.nrows() != n` or `pred.ncols() != m` → `FdarError::InvalidDimension { parameter: "predictors[k]", ... }`
- `!bandwidth.is_finite() || bandwidth <= 0.0` → `FdarError::InvalidParameter { parameter: "bandwidth", ... }`
- `argvals.len() != m` → `FdarError::InvalidDimension { parameter: "argvals", ... }`
- `n <= p` (underdetermined system) → `FdarError::InvalidDimension { parameter: "response", ... }`

### `ConcurrentRegrResult` (all fields)

```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/concurrent_regression.rs:36-47
// Verbatim field declarations:
pub beta_curve: FdMatrix,      // (p, m) — rows=predictor index, cols=grid points
pub intercept: Vec<f64>,       // length m — time-varying intercept β₀(t)
pub fitted: FdMatrix,          // (n, m) — fitted functional response curves
pub residuals: FdMatrix,       // (n, m) — response − fitted
pub argvals: Vec<f64>,         // length m — shared evaluation grid
```

**beta_curve orientation (CRITICAL):** `beta_curve.shape() == (p, m)` where rows = predictor index (0..p) and cols = grid points (0..m). This is NOT `(n_obs, m)`. [VERIFIED from concurrent_regression.rs:257 `let mut beta_curve = FdMatrix::zeros(p, m);` and core tests:331 `assert_eq!(r.beta_curve.shape(), (1, m), "beta_curve shape");` and :371 `assert_eq!(r.beta_curve.shape(), (p, m), "beta_curve shape for p=3");`]

**Python dict output shape:**
- `beta_curve` → `ndarray shape (p, m)` via `fdmatrix_to_numpy2d`
- `intercept` → `ndarray shape (m,)` via `vec_to_numpy1d`
- `fitted` → `ndarray shape (n, m)` via `fdmatrix_to_numpy2d`
- `residuals` → `ndarray shape (n, m)` via `fdmatrix_to_numpy2d`
- `argvals` → `ndarray shape (m,)` via `vec_to_numpy1d`

### `functional_glm`

```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/scalar_on_function/glm.rs:509-517
pub fn functional_glm(
    data: &FdMatrix,                      // (n, m) functional predictors
    y: &[f64],                            // scalar response, length n
    family: GlmFamily,                    // Binomial | Poisson | Gamma | Gaussian
    scalar_covariates: Option<&FdMatrix>, // (n, q) optional; None if not used
    ncomp: usize,                         // FPC components; clamped to min(n-1, m) internally
    max_iter: usize,                      // IRLS iterations; 0 → internal default 25
    tol: f64,                             // convergence tol; <= 0.0 → internal default 1e-6
) -> Result<FunctionalGlmResult, FdarError>
```

**Module path:** `fdars_core::scalar_on_function::functional_glm`

**Default handling (from glm.rs:561-562):**
```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/scalar_on_function/glm.rs:561-562
let max_iter = if max_iter == 0 { 25 } else { max_iter };
let tol = if tol <= 0.0 { 1e-6 } else { tol };
```
The wrapper should pass the Python defaults directly (e.g. `max_iter=25, tol=1e-6`) to be transparent to callers rather than relying on the zero-means-default convention.

**ncomp clamping (from glm.rs:556):**
```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/scalar_on_function/glm.rs:556
let ncomp = ncomp.min(n - 1).min(m);
```
The caller does not need to guard ncomp — core clamps it. However, passing `ncomp == 0` after clamping produces a near-degenerate model; the binding need not add an extra guard for this.

**Validated error conditions (from source):**
- `n < 3` → `FdarError::InvalidDimension { parameter: "data", ... }`
- `m == 0` → `FdarError::InvalidDimension { parameter: "data", ... }`
- `y.len() != n` → `FdarError::InvalidDimension { parameter: "y", ... }`
- `scalar_covariates.nrows() != n` → `FdarError::InvalidDimension { parameter: "scalar_covariates", ... }`
- Binomial y ∉ {0.0, 1.0} → `FdarError::InvalidParameter { parameter: "y", ... }`
- Poisson y < 0 or non-integer → `FdarError::InvalidParameter { parameter: "y", ... }`
- Gamma y ≤ 0 → `FdarError::InvalidParameter { parameter: "y", ... }`
- Non-finite y (any family) → `FdarError::InvalidParameter { parameter: "y", ... }`

### `GlmFamily` enum

```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/scalar_on_function/mod.rs:341-355
// Verbatim:
#[derive(Debug, Clone, Copy, PartialEq)]
#[non_exhaustive]
pub enum GlmFamily {
    Binomial,   // logit link; y in {0.0, 1.0}
    Poisson,    // log link; y non-negative integers
    Gamma,      // inverse link (canonical, NOT log); y > 0
    Gaussian,   // identity link; converges in 1 IRLS step
}
```

### `FunctionalGlmResult` (all 15 fields)

```rust
// VERIFIED: /home/simonm/projects/rust/fdars v0.23.0:fdars-core/src/scalar_on_function/mod.rs:362-395
// Verbatim field declarations:
pub intercept: f64,                              // intercept α
pub beta_t: Vec<f64>,                            // functional coef β(t), length m
pub beta_se: Vec<f64>,                           // pointwise SE of β(t), length m
pub gamma: Vec<f64>,                             // scalar covariate coefs, length q (empty if no scalar_covariates)
pub fitted_values: Vec<f64>,                     // fitted means μ = g^{-1}(η), length n
pub linear_predictors: Vec<f64>,                 // η = Xβ, length n
pub ncomp: usize,                                // FPC components actually used
pub coefficients: Vec<f64>,                      // all regression coefs [intercept, γ₁…γ_K, z₁…z_P]
pub std_errors: Vec<f64>,                        // SE of all coefficients (same length as coefficients)
pub log_likelihood: f64,                         // log-likelihood kernel at convergence
pub deviance: f64,                               // GLM deviance D = 2(LL_sat − LL_fit)
pub iterations: usize,                           // IRLS iterations performed
pub fpca: crate::regression::FpcaResult,         // embedded FPCA — DO NOT expose to Python
pub aic: f64,                                    // −2·log_likelihood + 2·p
pub bic: f64,                                    // −2·log_likelihood + p·ln(n)
pub family: GlmFamily,                           // family used (expose as string in Python dict)
```

**Python dict key mapping (14 keys exposed; `fpca` omitted):**

| Dict key | Rust field | Python type |
|----------|------------|-------------|
| `"intercept"` | `r.intercept` | `float` |
| `"beta_t"` | `r.beta_t` | `ndarray (m,)` |
| `"beta_se"` | `r.beta_se` | `ndarray (m,)` |
| `"gamma"` | `r.gamma` | `ndarray (q,)` — empty array if no scalar_covariates |
| `"fitted_values"` | `r.fitted_values` | `ndarray (n,)` |
| `"linear_predictors"` | `r.linear_predictors` | `ndarray (n,)` |
| `"ncomp"` | `r.ncomp` | `int` |
| `"coefficients"` | `r.coefficients` | `ndarray (1+ncomp+q,)` |
| `"std_errors"` | `r.std_errors` | `ndarray (1+ncomp+q,)` |
| `"log_likelihood"` | `r.log_likelihood` | `float` |
| `"deviance"` | `r.deviance` | `float` |
| `"iterations"` | `r.iterations` | `int` |
| `"aic"` | `r.aic` | `float` |
| `"bic"` | `r.bic` | `float` |
| `"family"` | `r.family` (via match) | `str` — `"binomial"`, `"poisson"`, `"gamma"`, `"gaussian"` |

**NOT exposed:** `r.fpca` (embedded `FpcaResult`). The binding does not offer a Python `predict_functional_glm` function this phase (out of scope per CONTEXT.md).

---

## Proposed `#[pyo3(signature = ...)]` Defaults

### `concurrent_regression`

```rust
#[pyo3(signature = (predictors, response, argvals=None, bandwidth=0.2, kernel="gaussian"))]
```

- `argvals=None` — passes `None` to core, which generates a uniform 0..1 grid (matches project convention in `convert.rs:default_grid`)
- `bandwidth=0.2` — [ASSUMED] reasonable default for FDA on [0,1] grids with ~50 points; not pinned in core. Advise user to tune.
- `kernel="gaussian"` — core default used in all tests [VERIFIED: concurrent_regression.rs tests use `"gaussian"`]

### `functional_glm`

```rust
#[pyo3(signature = (data, response, argvals=None, family="gaussian", n_comp=3, scalar_covariates=None, max_iter=25, tol=1e-6))]
```

- `argvals=None` — not consumed by `functional_glm` core (it generates its own grid internally); accept but ignore or add a future `predict` function that uses it. For v0.23 the core does not accept `argvals` as a parameter — the function signature does not include it. [VERIFIED: glm.rs:509-517 — no `argvals` parameter].

**IMPORTANT correction on `functional_glm` Python signature:** The core `functional_glm` does NOT accept `argvals`. The Python API in CONTEXT.md shows `argvals` in the call, but the core function generates its own grid at line 557: `let argvals: Vec<f64> = (0..m).map(|j| j as f64 / (m - 1).max(1) as f64).collect();`. The Python binding signature should therefore be:

```rust
#[pyo3(signature = (data, response, family="gaussian", n_comp=3, scalar_covariates=None, max_iter=25, tol=1e-6))]
```

The CONTEXT.md mention of `argvals` in `functional_glm` is an [ASSUMED] part of the API shape that does not match the actual v0.23.0 core signature — the planner must confirm with the user whether to include it (e.g. for consistency/future predict support) or omit it.

---

## Common Pitfalls

### Pitfall 1: `beta_curve` orientation — `(p, m)` vs `(n_obs, m)`

**What goes wrong:** `beta_curve` in `ConcurrentRegrResult` is `(p, m)` (predictor count × grid points). `fdmatrix_to_numpy2d` returns the correct shape. If the binding author documents or tests it as `(n_obs, m)`, the shape is silently wrong when `p != n`.

**Why it happens:** Every other FdMatrix in pyfda is `(n_obs, n_points)`. `beta_curve` breaks this convention.

**How to avoid:** Comment in the binding: `// beta_curve: shape (p, m) — rows are predictor curves, NOT observations`. Write a test with `p = 3` asserting `result["beta_curve"].shape == (3, m)`.

**Warning signs:** Any test with `p == 1` will NOT catch a transposition bug (shape `(1, m)` is ambiguous). [VERIFIED from PITFALLS.md and core tests at concurrent_regression.rs:371]

### Pitfall 2: `GlmFamily::Gamma` uses inverse link, NOT log

**What goes wrong:** Callers familiar with R's `glm(family=Gamma(link="log"))` assume log-link. The fdars-core Gamma uses the canonical inverse link `g(μ) = 1/μ`. Predictions from `fitted_values` are on the mean scale (already g⁻¹-transformed). Confusing inverse with log leads to wrong interpretation of coefficients.

**Why it happens:** R defaults to log-link for Gamma; fdars-core uses the mathematically canonical inverse link. The module docstring explicitly calls this out. [VERIFIED: glm.rs module doc: "Canonical links only: Gamma uses inverse link (g(μ)=1/μ), NOT log-link."]

**How to avoid:** Document in the Python binding docstring and in Phase 41 (DOCS-08). No code fix needed — the math is correct. The AIC magnitude divergence from R is a separate documented caveat.

### Pitfall 3: `functional_glm` argvals parameter does not exist in core

**What goes wrong:** The CONTEXT.md API sketch shows `argvals` in the `functional_glm` call. The core `functional_glm` does NOT have an `argvals` parameter — it constructs a uniform grid internally from `data.ncols()`. Adding an `argvals` parameter that is silently ignored is confusing; accepting it but not forwarding it is misleading.

**How to avoid:** Check the actual v0.23.0 signature before writing the Python wrapper. [VERIFIED: glm.rs:509-517 — no `argvals` parameter]. Either omit it from the Python API (simplest) or accept it as an `argvals=None` parameter with a note that it is currently unused and reserved for future predict functionality. Raise this as an open question for the planner.

### Pitfall 4: PyO3 `Vec<PyReadonlyArray2>` parameter binding

**What goes wrong:** If PyO3 0.28 does not automatically bind a Python `list[np.ndarray]` to `Vec<PyReadonlyArray2<'py, f64>>`, the function will raise a `TypeError` at runtime that is hard to diagnose.

**How to avoid:** At the start of execution, write a minimal smoke test (`p=1`) that calls `concurrent_regression` with a single-element list and confirms the binding works before implementing the full validation suite. If `Vec<PyReadonlyArray2>` fails, fall back to accepting `Bound<'py, PyList>` and iterating elements manually via `.get_item(i)?.extract::<PyReadonlyArray2<'py, f64>>()`.

### Pitfall 5: `r.ncomp` (usize) and `r.iterations` (usize) must be inserted as Python `int`, not numpy int

**What goes wrong:** `dict.set_item("ncomp", r.ncomp)` where `r.ncomp: usize` will insert a native Python `int` (PyO3 converts usize → Python int automatically). Do not wrap in `vec_to_numpy1d` or similar. However, `r.coefficients: Vec<f64>` has length `1 + ncomp + q` — this is a variable-length 1-D array and must use `vec_to_numpy1d`.

**How to avoid:** Follow the type mapping table exactly. Scalars (`f64`, `usize`) go directly into `dict.set_item`; vectors go via `vec_to_numpy1d`; matrices go via `fdmatrix_to_numpy2d`.

### Pitfall 6: Underdetermined system guard (`n <= p`) for `concurrent_regression`

**What goes wrong:** The Python wrapper must NOT add its own guard for `n <= p` — core already handles this with a clear error message. Adding a Python-side guard with a different threshold or different message creates inconsistency.

**How to avoid:** Pass all dimension checks through `to_pyresult()` and let core error messages surface as `ValueError`. Only add Python-side guards for things the core cannot check (e.g., ragged predictor list where shapes differ — but that too is caught by core per-element shape checks).

---

## Runtime State Inventory

This is a greenfield extension (adding new functions to an existing module). No rename/refactor involved. **No runtime state items apply.**

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| maturin | `maturin develop` build | ✓ | 1.13.1 | — |
| pytest | test execution | ✓ | 9.0.3 | — |
| Python (.venv) | test execution | ✓ | 3.14.6 | — |
| fdars-core 0.23.0 | Rust compilation | ✓ | 0.23.0 in Cargo.toml | — |
| Rust toolchain | Rust compilation | ✓ | >= 1.83 (MSRV) | — |

**Build command:** `.venv/bin/maturin develop --release` (or without `--release` for faster dev builds)
**Test command:** `.venv/bin/pytest tests/ -q`
**Targeted test:** `.venv/bin/pytest tests/test_regression.py -q` (or the new test file)

All dependencies available. No blocking gaps.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` (check for `[tool.pytest.ini_options]`) |
| Quick run command | `.venv/bin/pytest tests/test_regression.py -q` |
| Full suite command | `.venv/bin/pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REGR-01 | `concurrent_regression` returns correct dict structure | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_smoke -x` | ❌ Wave 0 |
| REGR-01 | `beta_curve.shape == (p, m)` for p=3 (transposition guard) | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_beta_curve_shape_p3 -x` | ❌ Wave 0 |
| REGR-01 | `beta_curve` round-trip: each row is a smooth curve over argvals | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_beta_curve_rows_are_curves -x` | ❌ Wave 0 |
| REGR-01 | `concurrent_regression` is deterministic (same inputs → same output) | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_determinism -x` | ❌ Wave 0 |
| REGR-01 | `residuals == response - fitted` element-wise | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_residuals_consistency -x` | ❌ Wave 0 |
| REGR-02 | `functional_glm` Gaussian: correct dict keys + finite fitted_values | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_gaussian_smoke -x` | ❌ Wave 0 |
| REGR-02 | `functional_glm` Binomial: fitted_values in (0,1), family string round-trips | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_binomial_family -x` | ❌ Wave 0 |
| REGR-02 | `functional_glm` Poisson: fitted_values > 0, family="poisson" | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_poisson_family -x` | ❌ Wave 0 |
| REGR-02 | `functional_glm` Gamma: fitted_values > 0, family="gamma" | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_gamma_family -x` | ❌ Wave 0 |
| REGR-02 | Invalid family string raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_invalid_family -x` | ❌ Wave 0 |
| REGR-03 | Empty predictor list raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_empty_predictors_raises -x` | ❌ Wave 0 |
| REGR-03 | Bandwidth ≤ 0 raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_bad_bandwidth_raises -x` | ❌ Wave 0 |
| REGR-03 | Mismatched predictor shape raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestConcurrentRegression::test_mismatched_predictor_raises -x` | ❌ Wave 0 |
| REGR-03 | Binomial y=0.5 raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_binomial_domain_guard -x` | ❌ Wave 0 |
| REGR-03 | Poisson y<0 raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_poisson_domain_guard -x` | ❌ Wave 0 |
| REGR-03 | Gamma y=0 raises `ValueError` | unit | `.venv/bin/pytest tests/test_regression.py::TestFunctionalGlm::test_gamma_domain_guard -x` | ❌ Wave 0 |
| REGR-03 | `fdars.regression.concurrent_regression` importable | unit | `.venv/bin/pytest tests/test_regression.py::TestImportPaths -x` | ❌ Wave 0 |
| REGR-03 | `fdars.regression.functional_glm` importable | unit | `.venv/bin/pytest tests/test_regression.py::TestImportPaths -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `.venv/bin/pytest tests/test_regression.py -q` (fast — synthetic data, no disk I/O)
- **Per wave merge:** `.venv/bin/pytest tests/ -q`
- **Phase gate:** Full suite green + `cargo fmt --check` + `cargo clippy -- -D warnings` before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_regression.py` — all new test classes (TestConcurrentRegression, TestFunctionalGlm, TestImportPaths for new functions) — covers all Req IDs above
- [ ] `maturin develop` build green after adding new `#[pyfunction]`s and updating `register()`

*(Existing test infrastructure covers the existing regression functions. New test file/classes are the only gaps.)*

---

## Security Domain

This phase adds pure computation functions with no network access, no file I/O, no authentication, and no user-supplied code execution. ASVS categories V2, V3, V4, V6 do not apply. V5 (input validation) is satisfied by `to_pyresult()` converting all `FdarError::InvalidDimension`/`InvalidParameter` → Python `ValueError` with descriptive messages. No additional security controls are required.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Binary-only functional logistic | Full exponential-family GLM (Binomial/Poisson/Gamma/Gaussian) via `functional_glm` | fdars-core 0.23.0 (this milestone) | Users can now model count and positive-continuous responses with FDA predictors |
| No varying-coefficient functional regression | `concurrent_regression` (fdaconcur-style pointwise OLS + local-linear smoothing) | fdars-core 0.23.0 (this milestone) | Time-varying predictor effects can now be estimated |

**Deprecated/outdated:** Nothing deprecated in this phase. The existing `functional_logistic` remains; `functional_glm(family="binomial")` is its GLM-framework equivalent.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `bandwidth=0.2` is a reasonable Python-side default for `concurrent_regression` | Proposed defaults | User gets a plausible but possibly non-optimal default; easy to fix by tuning the value |
| A2 | PyO3 0.28 accepts `Vec<PyReadonlyArray2<'py, f64>>` as a parameter type for Python `list[np.ndarray]` | Pattern 1 | Binding raises TypeError at runtime; fall back to `Bound<'py, PyList>` extraction |
| A3 | `functional_glm` Python API does NOT include `argvals` (CONTEXT.md sketch vs. actual core signature) | Proposed defaults | If user expects `argvals` parameter, a clear API mismatch; raise as open question |
| A4 | The existing `tests/test_regression.py` does not already test `concurrent_regression` or `functional_glm` (no test file contents read this session) | Validation Architecture | If tests exist, wave 0 is smaller; double-check at execute time |

---

## Open Questions

1. **`functional_glm` argvals parameter**
   - What we know: The core `functional_glm` does NOT accept an `argvals` parameter (generates a uniform grid internally). CONTEXT.md shows `argvals` in the call syntax.
   - What's unclear: Should the Python binding accept-and-ignore `argvals` for API consistency, or omit it entirely?
   - Recommendation: Omit from the Python signature — accepting a parameter that is silently unused is more confusing than a clean, smaller API. Confirm with user before locking.

2. **`Vec<PyReadonlyArray2>` bindability in PyO3 0.28**
   - What we know: PyO3's `FromPyObject` is implemented for `Vec<T>` when `T: FromPyObject`. `PyReadonlyArray2` should implement `FromPyObject`.
   - What's unclear: Whether there is a lifetime issue with `Vec<PyReadonlyArray2<'py, f64>>` that prevents the auto-impl. This is a [ASSUMED] claim.
   - Recommendation: Add a one-line smoke test at the start of Task 1 execution; if it fails, use `Bound<'py, PyList>` extraction as fallback (add two extra lines of code).

3. **`argvals` in `concurrent_regression` — None vs required**
   - What we know: `concurrent_regression` core accepts `argvals: Option<&[f64]>`. The Python API in CONTEXT.md shows `argvals` as a positional parameter (not optional).
   - What's unclear: Whether to make `argvals` optional (None → uniform grid) or required.
   - Recommendation: Make it optional (`argvals=None`), consistent with other pyfda functions that use `default_grid` from `convert.rs`. Required argvals forces callers to construct a grid unnecessarily.

---

## Project Constraints (from CLAUDE.md)

- All fallible Rust calls route through `to_pyresult()` — no `.unwrap()` or `.expect()`.
- Rust modules use snake_case with `_mod.rs` suffix (target file: `regression_mod.rs`).
- `#[pyfunction]` + `#[pyo3(signature = (...))]` pattern for all new functions.
- Function doc comments use NumPy/Sphinx format (Parameters / Returns / Raises sections).
- All `FdMatrix` fields convert via `fdmatrix_to_numpy2d`; never hand-roll transposition.
- No new submodule — these functions are added to the existing `fdars.regression` submodule.
- The `register_submodule!` macro in `lib.rs` already registers `regression`; only `register()` in `regression_mod.rs` needs new `m.add_function(...)` calls.
- `rustfmt` enforced via CI (`cargo fmt --check`); `clippy -D warnings` enforced.
- Python tests use `pytest`; no linter enforced, but PEP 8 conventions apply.
- `maturin develop` is the dev build command (`.venv/bin/maturin develop`).

---

## Sources

### Primary (HIGH confidence)

- `v0.23.0:fdars-core/src/concurrent_regression.rs` — full function signature, ConcurrentRegrResult struct (lines 36-47, 92-98), all validation error conditions, beta_curve orientation confirmed from `FdMatrix::zeros(p, m)` call at line 257 and test assertions at lines 331, 371
- `v0.23.0:fdars-core/src/scalar_on_function/mod.rs` — GlmFamily enum (lines 341-355) with `#[non_exhaustive]` confirmed, FunctionalGlmResult all 15 fields (lines 362-395)
- `v0.23.0:fdars-core/src/scalar_on_function/glm.rs` — full functional_glm signature (lines 509-517), default handling (lines 561-562), ncomp clamping (line 556), IRLS convergence logic
- `/home/simonm/projects/rust/pyfda/src/regression_mod.rs` — existing binding patterns: `#[pyo3(signature=...)]`, dict construction, `to_pyresult()` usage, `register()` function
- `/home/simonm/projects/rust/pyfda/src/inference_mod.rs` — `test_result_to_pydict` helper pattern (lines 32-41), `multiplier_from_str` wildcard dispatch pattern (lines 227-235), `flm_f_test`/`flm_gof_test` internal-refit pattern (lines 413-426)
- `/home/simonm/projects/rust/pyfda/src/convert.rs` — all conversion helper signatures confirmed

### Secondary (MEDIUM confidence)

- `.planning/research/FEATURES.md` — detailed A1/A2 capability specifications, cross-checked against v0.23.0 source
- `.planning/research/PITFALLS.md` — beta_curve transposition pitfall (Pitfall 1), GlmFamily inverse-link caveat confirmed
- `.planning/phases/37-group-a-regression-bindings/37-CONTEXT.md` — locked decisions
- `.planning/REQUIREMENTS.md` — REGR-01, REGR-02, REGR-03 requirements

### Tertiary (LOW confidence)

- `[ASSUMED]` claims: bandwidth=0.2 default, PyO3 Vec<PyReadonlyArray2> binding compatibility — to be verified at execute time

---

## Metadata

**Confidence breakdown:**
- Function signatures: HIGH — read verbatim from v0.23.0 source this session
- Struct fields: HIGH — read verbatim from v0.23.0 source this session; all 15 FunctionalGlmResult fields and 5 ConcurrentRegrResult fields enumerated with exact names and types
- Enum variants: HIGH — GlmFamily read verbatim from v0.23.0 mod.rs:341-355; `#[non_exhaustive]` confirmed
- beta_curve orientation: HIGH — confirmed from `FdMatrix::zeros(p, m)` in core implementation and test assertions `r.beta_curve.shape() == (p, m)`
- Architecture patterns: HIGH — derived from reading `inference_mod.rs` and `regression_mod.rs` this session
- PyO3 Vec binding: LOW (ASSUMED) — needs runtime verification

**Research date:** 2026-08-20
**Valid until:** 2026-09-20 (stable library; signatures will not change within v0.23.0)
