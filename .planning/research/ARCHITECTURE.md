# Architecture Research

**Domain:** PyO3 binding layer — fdars-core 0.20.0 upgrade (inference + depth/boxplot + basis/smoothing)
**Researched:** 2026-08-17
**Confidence:** HIGH (grounded entirely in real file content)

---

## Standard Architecture

All evidence drawn from the live codebase. No inference required — every claim
has a file:line citation.

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Python user layer  (import fdars; fdars.inference.t_perm_test(...))    │
├─────────────────────────────────────────────────────────────────────────┤
│  python/fdars/__init__.py  — _submodule_names tuple + sys.modules loop  │
│  python/fdars/fdata_class.py  — Fdata OOP wrapper                       │
│  python/fdars/advisor/__init__.py  — build_diagnostics + advise()       │
│  python/fdars/mcp/server.py  — _DIAGNOSTICS_METHODS / _RUNNABLE_METHODS │
├─────────────────────────────────────────────────────────────────────────┤
│  PyO3 binding layer  (src/*_mod.rs + src/lib.rs + src/convert.rs)       │
│  ┌──────────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────────────┐  │
│  │inference_mod │ │  depth_mod  │ │  basis_mod │ │  smoothing_mod   │  │
│  │  (NEW file)  │ │  (extend)   │ │  (extend)  │ │  (extend)        │  │
│  └──────────────┘ └─────────────┘ └────────────┘ └──────────────────┘  │
│  convert.rs: numpy2d_to_fdmatrix / fdmatrix_to_numpy2d / to_pyresult()  │
├─────────────────────────────────────────────────────────────────────────┤
│  fdars-core 0.20.0  (Rust crate, Cargo.toml dependency)                 │
│  inference::  depth::  smooth_basis::  basis::                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | File(s) |
|-----------|----------------|---------|
| `_native` pymodule | Root PyO3 extension; registers all submodules via `register_submodule!` macro | `src/lib.rs` |
| `register_submodule!` macro | Creates a `PyModule`, calls the module's `register(m)` fn, attaches to parent | `src/lib.rs:30-36` |
| `*_mod.rs` | One file per functional category; each exports `#[pyfunction]`s + a `register(m)` fn | `src/*_mod.rs` |
| `convert.rs` | numpy (row-major) ↔ FdMatrix (column-major) marshalling; `to_pyresult()` / `to_pyerr()` | `src/convert.rs` |
| `__init__.py` `_submodule_names` | Tuple that drives the `sys.modules` registration loop; both `fdars.X.fn` and `from fdars.X import fn` work | `python/fdars/__init__.py:34-53` |
| `build_diagnostics` `_supported` set | Inner set literal in `advisor/__init__.py` that gates valid method names; must stay in sync with `_DIAGNOSTICS_METHODS` | `python/fdars/advisor/__init__.py:124-133` |
| `_DIAGNOSTICS_METHODS` | `frozenset` in `mcp/server.py`; must equal `_supported`; enforced by `test_diagnostics_methods_match_advisor_supported` | `python/fdars/mcp/server.py:63-82` |
| `_RUNNABLE_METHODS` | Subset of `_DIAGNOSTICS_METHODS`; methods that `fdars_run_method` / `fdars_compare_run` can dispatch without caller-supplied arrays | `python/fdars/mcp/server.py:49-51`, `mcp/_runner.py:59-60` |

---

## Recommended Project Structure — v5.0 Changes

```
src/
├── lib.rs                    # ADD: mod inference_mod; register_submodule!(m, "inference", ...)
├── inference_mod.rs          # NEW FILE — Group A
├── depth_mod.rs              # EXTEND — Group B (functional_depth + functional_boxplot)
├── basis_mod.rs              # EXTEND — Group C (constant_basis)
├── smoothing_mod.rs          # EXTEND — Group C (aic_smoother, smooth_basis_aic, CvCriterion::Aic)
└── convert.rs                # NO CHANGE

python/fdars/
├── __init__.py               # ADD "inference" to _submodule_names tuple
├── advisor/
│   ├── __init__.py           # ADD "inference" to _supported set + dispatch branch
│   └── aspects/
│       └── inference.py      # NEW FILE — _build_inference_diagnostics
└── mcp/
    └── server.py             # ADD "inference" to _DIAGNOSTICS_METHODS (atomic commit with advisor/__init__.py)
```

### Structure Rationale

- **`inference_mod.rs` as a new file:** Mirrors the v4.0 precedent (`represent_mod.rs`, `scoring_mod.rs`). The inference surface is a distinct conceptual category (hypothesis testing, confidence bands, FLM post-hoc); it does not belong in `regression_mod.rs` (regression fits) or `depth_mod.rs` (depth scores).
- **`depth_mod.rs` extended (not a new file):** `functional_depth` and `functional_boxplot` are depth-family operations. Placing them in the existing `depth_mod.rs` keeps the module cohesive and avoids a proliferation of very small files.
- **`basis_mod.rs` and `smoothing_mod.rs` extended:** `constant_basis` is a basis constructor (Group C); AIC smoothing (`aic_smoother`, `smooth_basis_aic`, `CvCriterion::Aic`) extends the existing `CvCriterion` match arm in `smoothing_mod.rs`. Both are additive additions to existing files.

---

## Architectural Patterns

### Pattern 1: New Submodule Registration

**What:** Any new top-level `fdars.X` submodule requires four coordinated edits.
**When to use:** Group A (`fdars.inference`). Not needed for Groups B/C which extend existing modules.

Four files must change in a single commit:

1. `src/lib.rs` — add `mod inference_mod;` and `register_submodule!(m, "inference", inference_mod::register);`
2. `src/inference_mod.rs` — new file with `#[pyfunction]` definitions + `pub fn register(m)`
3. `python/fdars/__init__.py` — add `"inference"` to `_submodule_names` tuple
4. (advisor + MCP sync in the advisor integration commit — see Pattern 4)

**Example (lib.rs additions):**
```rust
mod inference_mod;  // alongside existing mod lines

// inside _native():
register_submodule!(m, "inference", inference_mod::register);
```

**Example (`inference_mod.rs` skeleton):**
```rust
//! Functional inference — two-sample tests, SCB bands, FLM inference.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

// ... #[pyfunction] definitions ...

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(t_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(f_perm_test, m)?)?;
    // etc.
    Ok(())
}
```

### Pattern 2: Struct Result to PyDict

**What:** fdars-core compound result types cross the boundary as `PyDict`. No Rust struct is exposed directly to Python.
**When to use:** All new result types — `TestResult`, `FunctionalBoxplotResult`, `ShiftRegistrationResult` (v4.0 precedent).

Evidence from `regression_mod.rs:35-45` (`fpca` returns dict):
```rust
let dict = pyo3::types::PyDict::new(py);
dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
dict.set_item("singular_values", vec_to_numpy1d(py, result.singular_values))?;
dict.set_item("r_squared", result.r_squared)?;
Ok(dict.into_any())
```

**`TestResult` to PyDict mapping (all inference functions):**

```rust
let dict = pyo3::types::PyDict::new(py);
dict.set_item("statistic", result.statistic)?;        // f64
dict.set_item("p_value", result.p_value)?;            // f64
// permutation-test-specific:
dict.set_item("n_perm", result.n_perm)?;              // usize
dict.set_item("reject", result.reject)?;              // bool (optional, may be absent)
Ok(dict.into_any())
```

Actual field names must be verified against `fdars-core 0.20.0` docs.rs before coding. Placeholder names above follow the project's existing convention (`p_value` not `pval`; `statistic` not `stat`).

**`FunctionalBoxplotResult` to PyDict mapping:**

```rust
let dict = pyo3::types::PyDict::new(py);
dict.set_item("median", fdmatrix_to_numpy2d(py, &result.median))?;        // (1, m) matrix -> ndarray
dict.set_item("central_region", fdmatrix_to_numpy2d(py, &result.central_region))?;  // (2, m)
dict.set_item("fence", fdmatrix_to_numpy2d(py, &result.fence))?;          // (2, m)
dict.set_item("outlier_flags", bool_vec_to_numpy1d(py, result.outlier_flags))?;  // (n,)
Ok(dict.into_any())
```

**Note:** Any `FdMatrix` field (multi-row matrix) must route through `fdmatrix_to_numpy2d`. Single-curve fields (median, fence bounds) are still `FdMatrix` in fdars-core and must use the same converter — do not use `vec_to_numpy1d` on a matrix. This is the column-major transposition pitfall from v4.0 Phase 26.

### Pattern 3: String-Enum Dispatch with non_exhaustive Fallback

**What:** Rust enums cross the boundary as `&str` parameters; a `match` arm maps them to the enum variant, and a wildcard arm raises `PyValueError` for unknown strings. The `_ =>` arm is mandatory because upstream enums are `#[non_exhaustive]`.
**When to use:** `DepthMethod` (Group B), `CvCriterion::Aic` (Group C).

Established pattern from `smoothing_mod.rs:193-201`:
```rust
let crit = match criterion {
    "cv"  => fdars_core::smoothing::CvCriterion::Cv,
    "gcv" => fdars_core::smoothing::CvCriterion::Gcv,
    _ => {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "criterion must be 'cv' or 'gcv'",
        ))
    }
};
```

**Group C extension** — `CvCriterion::Aic` requires updating the message string too:
```rust
"aic" => fdars_core::smoothing::CvCriterion::Aic,   // NEW
_ => return Err(pyo3::exceptions::PyValueError::new_err(
    "criterion must be 'cv', 'gcv', or 'aic'",       // message updated
))
```

Note: `BasisCriterion` in `basis_mod.rs` already has an `"aic"` arm at line 442 for `basis_nbasis_cv`. The Group C work adds AIC to the `smoothing_mod.rs` `CvCriterion` match and exposes `aic_smoother`/`smooth_basis_aic` functions.

**`DepthMethod` dispatcher** (Group B, `functional_depth`):
```rust
let method = match method_str {
    "fraiman_muniz" => fdars_core::depth::DepthMethod::FraimanMuniz,
    "modal"         => fdars_core::depth::DepthMethod::Modal,
    "band"          => fdars_core::depth::DepthMethod::Band,
    // ... other variants as they exist in 0.20.0 ...
    _ => return Err(pyo3::exceptions::PyValueError::new_err(
        format!("unknown depth method: {method_str:?}")
    ))
};
```

Actual `DepthMethod` variants must be verified against docs.rs before coding. The fallback arm is non-negotiable.

### Pattern 4: Advisor and MCP Guard-Sync (Single Atomic Commit)

**What:** Adding a new `build_diagnostics` aspect requires three files to change together; the drift-lock test (`test_diagnostics_methods_match_advisor_supported`) enforces this is atomic.
**When to use:** Adding `"inference"` to the advisor.

The three files that must change in a single commit:
1. `python/fdars/advisor/__init__.py` — add `"inference"` to `_supported` set (line ~124) and add a dispatch branch `if method_lc == "inference": ...`
2. `python/fdars/advisor/aspects/inference.py` — NEW: `_build_inference_diagnostics` function
3. `python/fdars/mcp/server.py` — add `"inference"` to `_DIAGNOSTICS_METHODS` frozenset (line ~63)

The test at `tests/test_mcp_server.py:503-566` compares `_DIAGNOSTICS_METHODS` with the set parsed from the advisor's `ValueError` message. A partial commit that updates only 1 or 2 of these files will fail CI immediately.

**Grounding invariant constraint:** `_build_inference_diagnostics` must compute every value using fdars (e.g., `p_value`, `statistic`, `n_perm` from the `TestResult` dict). The LLM only interprets values that appear in the diagnostics dict. No fabricated numbers.

**`"inference"` is diagnostics-only** (not added to `_RUNNABLE_METHODS`): FLM inference requires a prior fit result that the MCP dataset model cannot supply independently; two-sample tests require two groups. This mirrors `"scoring"` (v4.0 Phase 28), which is in `_DIAGNOSTICS_METHODS` but not `_RUNNABLE_METHODS`.

---

## Data Flow

### New Binding Request Flow (Group A example — t_perm_test)

```
fdars.inference.t_perm_test(group1, group2, n_perm=999, seed=42)
    |
    v
src/inference_mod.rs  t_perm_test()  #[pyfunction]
    | numpy2d_to_fdmatrix(group1)   (row-major -> col-major)
    | numpy2d_to_fdmatrix(group2)
    | fdars_core::inference::t_perm_test(&g1, &g2, n_perm, Some(seed))
    | to_pyresult(result)?           (FdarError -> PyValueError)
    | PyDict::new(py)
    | dict.set_item("statistic", result.statistic)
    | dict.set_item("p_value", result.p_value)
    | dict.set_item("n_perm", result.n_perm)
    v
{"statistic": f64, "p_value": f64, "n_perm": usize}
```

### FLM Inference Data Flow (FLM-consumption question — answered below)

```
# Python user code:
fit = fdars.regression.fregre_lm(data, response, n_comp=5)
# fit is a plain Python dict: {"fitted_values": ndarray, "residuals": ndarray,
#                               "beta_t": ndarray, "r_squared": float,
#                               "coefficients": ndarray, "intercept": float}

result = fdars.inference.flm_f_test(data, response, n_comp=5, n_perm=999, seed=0)
# or, if 0.20.0 exposes a combined fit+test function:
result = fdars.inference.flm_f_test(data, response, n_comp=5, n_perm=999)
```

**FLM-fit consumption decision: RE-FIT inside the inference call (recommended).**

Evidence: `regression_mod.rs` never exposes `FregreLmResult` as a Python object or handle. The existing `predict_fregre_lm` binding (`regression_mod.rs:478-493`) demonstrates the established pattern: it re-fits internally by calling `fdars_core::scalar_on_function::fregre_lm(...)` and then calls `predict_fregre_lm(&fit, ...)` — the Rust struct never leaves Rust. The same pattern applies to `predict_fregre_pls` (line 527) and `predict_fregre_robust` (line 571-578).

This means `flm_f_test` and `flm_gof_test` should accept the raw data + response + `n_comp` (the same inputs as `fregre_lm`) and re-fit internally:

```rust
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=3, n_perm=999, seed=None))]
pub fn flm_f_test<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    // Re-fit inside the binding — FregreLmResult never crosses the boundary.
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(&mat, &resp, None, n_comp))?;
    let result = to_pyresult(fdars_core::inference::flm_f_test(&fit, n_perm, seed))?;
    // map TestResult -> PyDict
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("statistic", result.statistic)?;
    dict.set_item("p_value", result.p_value)?;
    Ok(dict.into_any())
}
```

**Alternative (opaque handle) is explicitly rejected:** Python has no `FregreLmResult` type — it only has the dict returned by `fregre_lm`. Accepting a dict back and re-parsing it to reconstruct a `FregreLmResult` (or requiring the user to pass a handle ID) is more complex and breaks the simple call pattern. The re-fit cost is negligible for the typical inference use case (one-shot fit + test).

**Plan-time flag:** This decision depends on the actual 0.20.0 signature of `fdars_core::inference::flm_f_test`. If the upstream function takes a `FregreLmResult` by reference, the re-fit approach is straightforward. If it exposes a combined `fit_and_test` function, use that. Verify against docs.rs/fdars-core/0.20.0 before implementation.

### Advisor Build-Diagnostics Flow

```
build_diagnostics(test_result_dict, method="inference")
    |
    v _supported check (must include "inference")
    v from fdars.advisor.aspects.inference import _build_inference_diagnostics
    v _build_inference_diagnostics(raw)
        - float(raw["p_value"])       # fdars-computed, no fabrication
        - float(raw["statistic"])
        - int(raw["n_perm"])
        - bool: p_value < 0.05        # derived, still grounded
    v
{"method": "inference", "p_value": float, "statistic": float, "n_perm": int, ...}
```

---

## Module Placement — Explicit Decision Table

| Capability | Module | File | Action |
|------------|--------|------|--------|
| `t_perm_test` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `f_perm_test` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `two_sample_mean_test` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `mean_scb` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `scb_two_sample_test` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `flm_f_test` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `flm_gof_test` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `oneway_anova_vstat` | `fdars.inference` | `src/inference_mod.rs` | NEW file |
| `functional_depth` (dispatcher) | `fdars.depth` | `src/depth_mod.rs` | EXTEND existing |
| `functional_boxplot` | `fdars.depth` | `src/depth_mod.rs` | EXTEND existing |
| `constant_basis` | `fdars.basis` | `src/basis_mod.rs` | EXTEND existing |
| `aic_smoother` | `fdars.smoothing` | `src/smoothing_mod.rs` | EXTEND existing |
| `smooth_basis_aic` | `fdars.smoothing` | `src/smoothing_mod.rs` | EXTEND existing |
| `CvCriterion::Aic` arm | existing match | `src/smoothing_mod.rs` | EXTEND match arm |

### `__init__.py` change

Only `"inference"` is added. Groups B/C extend existing modules — no change to `_submodule_names`.

```python
_submodule_names = (
    "fdata", "depth", "metric", "basis", "smoothing",
    "clustering", "regression", "alignment", "outliers",
    "seasonal", "spm", "classification", "tolerance",
    "conformal", "simulation", "explain", "represent",
    "scoring",
    "inference",   # NEW -- Group A
)
```

---

## Matrix Returns and Transposition Round-Trip Tests

**Rule (from v4.0 Phase 26):** Any binding that returns an `FdMatrix` must use `fdmatrix_to_numpy2d` — never `vec_to_numpy1d` — and must have a multi-curve transposition round-trip test.

Functions requiring a round-trip test:

| Function | Return field | Why |
|----------|-------------|-----|
| `functional_boxplot` -> `median` | `FdMatrix` (1-row matrix) | column-major pitfall |
| `functional_boxplot` -> `central_region` | `FdMatrix` (2-row matrix) | column-major pitfall |
| `functional_boxplot` -> `fence` | `FdMatrix` (2-row matrix) | column-major pitfall |
| `mean_scb` -> lower/upper band | `FdMatrix` (band arrays) | column-major pitfall |
| `scb_two_sample_test` -> any band field | `FdMatrix` | column-major pitfall |

**Scalar/vector-only returns** (`TestResult` from permutation tests) do not require the round-trip test because no `FdMatrix` is involved — `statistic`, `p_value`, and `n_perm` are plain scalars.

**Round-trip test template:**
```python
def test_functional_boxplot_layout():
    """Guard: column-major transposition round-trip for FunctionalBoxplotResult."""
    import numpy as np
    import fdars.depth as depth
    rng = np.random.default_rng(0)
    data = rng.standard_normal((10, 20))  # 10 obs, 20 points
    result = depth.functional_boxplot(data, data)
    # median shape: (1, 20) -- one curve
    assert result["median"].shape == (1, 20), result["median"].shape
    # central_region shape: (2, 20) -- lower and upper envelope
    assert result["central_region"].shape == (2, 20)
    # Values must be finite (no NaN from a bad transposition)
    assert np.all(np.isfinite(result["median"]))
```

---

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `inference_mod.rs` + `convert.rs` | `use crate::convert::*` (direct import) | Same as all other `*_mod.rs` files |
| `depth_mod.rs` + `fdars-core 0.20.0 depth::` | Direct function calls | `functional_depth` dispatcher + `functional_boxplot` |
| `advisor/__init__.py._supported` + `mcp/server.py._DIAGNOSTICS_METHODS` | Must be equal; enforced by `test_diagnostics_methods_match_advisor_supported` | Single atomic commit required; test at `tests/test_mcp_server.py:503` |
| `advisor/aspects/inference.py` + `advisor/__init__.py` | Lazy import via `if method_lc == "inference": from ...aspects.inference import ...` | Same pattern as all 13 existing aspects |

### Upstream API Verification Required Before Coding

The following must be confirmed against docs.rs/fdars-core/0.20.0 during the plan-phase for Group A:

1. Exact `TestResult` field names (`statistic`? `test_stat`? `p_value`? `pval`?)
2. Whether `flm_f_test` takes `&FregreLmResult` directly or provides a combined fit+test fn
3. `FunctionalBoxplotResult` field names and which fields are `FdMatrix` vs `Vec<f64>`
4. `DepthMethod` enum variant names (for the `functional_depth` dispatcher)
5. Whether `CvCriterion` in 0.20.0 for AIC smoothing is the same enum in `fdars_core::smoothing` or a new one — currently `smoothing_mod.rs` has `CvCriterion` with Cv/Gcv arms only; `basis_mod.rs` has `BasisCriterion` with Gcv/Cv/Aic/Bic. The milestone says `CvCriterion::Aic` is new in 0.20 for smoothing — confirm the enum path.
6. `aic_smoother` and `smooth_basis_aic` module path in `fdars_core`

---

## Anti-Patterns

### Anti-Pattern 1: Exposing Rust Structs as Python Objects

**What people do:** Return a `FregreLmResult` as an opaque Python object or add a `PyClass` wrapper so `flm_f_test` can accept it.
**Why it's wrong:** Breaks the thin-wrapper principle. Every existing predict/test function re-fits internally (`predict_fregre_lm`, `predict_fregre_pls`, `predict_fregre_robust` at `regression_mod.rs:486,527,571`). The pattern is established and consistent.
**Do this instead:** Accept `data + response + n_comp` (the fit inputs) and re-fit inside the inference binding. `FregreLmResult` stays in Rust.

### Anti-Pattern 2: Using vec_to_numpy1d on FdMatrix Fields

**What people do:** Return a functional boxplot's median or SCB band bounds via `vec_to_numpy1d(py, result.median.to_row_major())`.
**Why it's wrong:** Column-major layout means the rows/columns are swapped — the resulting array has shape `(m,)` or is transposed, losing the curve structure.
**Do this instead:** Always use `fdmatrix_to_numpy2d(py, &result.median)`. Enforce with a shape assertion in tests.

### Anti-Pattern 3: Partial Advisor/MCP Sync

**What people do:** Add `"inference"` to `advisor/_supported` in one commit, then add it to `_DIAGNOSTICS_METHODS` in a later commit.
**Why it's wrong:** `test_diagnostics_methods_match_advisor_supported` fails immediately on the intermediate state. CI will be red between the two commits.
**Do this instead:** Update `advisor/__init__.py` (both `_supported` set and dispatch branch), `advisor/aspects/inference.py`, and `mcp/server.py` `_DIAGNOSTICS_METHODS` in a single commit.

### Anti-Pattern 4: Hardcoded Enum Variants Without a Fallback Arm

**What people do:** Match only the variants known at authoring time and let Rust's exhaustiveness checker produce a compile error when upstream adds new variants.
**Why it's wrong:** `DepthMethod` and `CvCriterion` are `#[non_exhaustive]` in fdars-core; upstream additions would cause compilation failures.
**Do this instead:** Always include a `_ => PyValueError` arm. This is the pattern established for `CvCriterion` in `smoothing_mod.rs:196-200` and `BasisCriterion` in `basis_mod.rs:444-448`.

---

## Suggested Build Order

The order respects compilation dependencies (bindings before advisor before docs) and parallelism opportunities:

```
Phase 1: Crate bump (fdars-core 0.17 -> 0.20, parallel-only, no linalg)
         Cargo.toml + maturin develop + full suite green as regression gate.
         Unblocks everything else.

Phase 2: New bindings -- parallelizable after Phase 1:
  2A: Group A -- src/inference_mod.rs (new file)
               + lib.rs + __init__.py (new submodule)
  2B: Group B -- src/depth_mod.rs extensions
               (functional_depth dispatcher + functional_boxplot)
  2C: Group C -- src/basis_mod.rs + src/smoothing_mod.rs extensions
               (constant_basis + AIC smoothing)
  NOTE: 2A/2B/2C are independent; can be done sequentially or in parallel.
        Each binding group must have its round-trip tests before merging.

Phase 3: Advisor extension
         Depends on Phase 2A (inference bindings must exist to test the aspect).
         Single atomic commit: advisor/__init__.py + aspects/inference.py +
         mcp/server.py _DIAGNOSTICS_METHODS.
         Functional boxplot outlier diagnostics optionally added to the
         existing "depth" branch in build_diagnostics (no new guard-set entry).

Phase 4: Docs
         Depends on Phases 2 + 3 (all bindings and advisor surface stable).
         New pages + hand-authored SVG diagrams + runnable FDARS_FENCE_OK
         worked examples for inference, functional boxplot, basis/smoothing
         additions. mkdocs build --strict green gate.
```

**Dependency graph:**

```
Phase 1 (crate bump)
    |
    +---- Phase 2A (inference bindings)
    |         |
    +---- Phase 2B (depth extensions)
    |
    +---- Phase 2C (basis/smoothing extensions)
              |
         Phase 3 (advisor -- needs 2A for inference aspect)
              |
         Phase 4 (docs -- needs 2 + 3 complete)
```

---

## Sources

All findings derived from live codebase files:
- `src/lib.rs` — submodule registration macro and full module list
- `src/convert.rs` — numpy ↔ FdMatrix marshalling, `to_pyresult()`
- `src/depth_mod.rs` — existing depth function pattern
- `src/regression_mod.rs` — `fregre_lm` dict return pattern; `predict_fregre_lm` re-fit-inside-binding pattern (lines 486-492)
- `src/represent_mod.rs` — v4.0 new-submodule precedent
- `src/scoring_mod.rs` — v4.0 new-submodule precedent (diagnostics-only in MCP)
- `src/alignment_mod.rs:2103-2121` — `ShiftRegistrationResult` to PyDict + `fdmatrix_to_numpy2d` pattern
- `src/smoothing_mod.rs:193-216` — `CvCriterion` string-enum dispatch + `_ => PyValueError` fallback
- `src/basis_mod.rs:425-476` — `BasisCriterion` ("aic" already present in `basis_nbasis_cv` match)
- `python/fdars/__init__.py:34-53` — `_submodule_names` tuple
- `python/fdars/advisor/__init__.py:124-133` — `_supported` set and dispatch branches
- `python/fdars/mcp/server.py:49-82` — `_RUNNABLE_METHODS` / `_DIAGNOSTICS_METHODS`
- `python/fdars/mcp/_runner.py:59-60` — `_RUNNABLE_METHODS` mirror
- `tests/test_mcp_server.py:503-566` — `test_diagnostics_methods_match_advisor_supported` guard-sync test

---
*Architecture research for: pyfda v5.0 — fdars-core 0.20 upgrade binding integration*
*Researched: 2026-08-17*
