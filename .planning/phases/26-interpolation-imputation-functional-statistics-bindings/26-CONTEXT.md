# Phase 26: Interpolation, Imputation & Functional Statistics Bindings - Context

**Gathered:** 2026-08-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Bind the fdars-core 0.17.0 interpolation/representation and functional-statistics API into the `fdars` Python package, layout-correct across the numpy(row-major)↔FdMatrix(column-major) boundary, on the green 0.17.0 baseline from Phase 25.

Delivers (REPR-01/02/03, STAT-01/02):
- **Interpolation & representation** (new `fdars.represent` submodule): `spline_interpolate`, `spline_interpolate_with_policy`, `fdata_interpolate_with_policy` with `ExtrapolationPolicy` (Boundary / Exception / Fill(value) / Periodic), and `impute_missing_values` with `ImputationMethod` (Linear / Mean / Constant).
- **Functional statistics** (existing `fdars.fdata` submodule): `functional_variance`, `functional_std`, `functional_covariance`, `depth_based_median`, `trim_mean`.
- **Fdata convenience methods**: `fd.interpolate()`, `fd.impute()`, `fd.var()`, `fd.std()`, `fd.cov()`, `fd.median()` (depth-based).

Out of this phase: scoring metrics + alignment/registration bindings (Phase 27), advisor extension (28), diagrams/examples (29).
</domain>

<decisions>
## Implementation Decisions

### Namespace & Module Placement (user-decided)
- Interpolation + imputation get a NEW `fdars.represent` submodule, backed by a new `src/represent_mod.rs` registered via the `register_submodule!` macro in `src/lib.rs` (mirrors the 16 existing submodules) and added to `_submodule_names` in `python/fdars/__init__.py`. Rationale: aligns the API namespace with the existing docs `represent/` section; a clean home for representation ops rather than bloating `fdata` or exposing a vague `helpers` namespace.
- Functional statistics (`functional_variance/std/covariance`, `depth_based_median`, `trim_mean`) extend the existing `src/fdata_mod.rs` → `fdars.fdata.*`, matching upstream `fdars_core::fdata` placement.

### Fdata Convenience Methods (user-decided — expose ALL three groups)
- `fd.interpolate(query_points, ...)` and `fd.impute(method=...)` — representation ops as methods, matching the existing `fd.deriv()`/`fd.center()`/`fd.normalize()` pattern.
- `fd.var()`, `fd.std()`, `fd.cov()` — functional statistics as methods, alongside the existing `fd.mean()`.
- `fd.median()` — depth-based median as a method, alongside the existing `fd.geometric_median()`. Returns the resolved median curve.
- Each method is a thin wrapper delegating to the module-level native function; module-level functions remain the primary surface.

### depth_based_median Return (user-decided)
- The binding resolves the upstream `usize` index to the ACTUAL median curve (a `1×n_points` numpy array; `fd.median()` returns an `Fdata` row). Never leak a bare integer to the caller.

### Enum Crossing & Result Marshalling (research-grounded; Claude's discretion within these)
- `ExtrapolationPolicy` and `ImputationMethod` cross the PyO3 boundary as **string params + `match` arms** (established convention: `linkage`/`basis_type`/`penalty_type` in existing modules), each with a forward-compatible fallback `_ => Err(PyValueError::new_err(...))` arm since the upstream enums are `#[non_exhaustive]`. `Fill(value)` takes the fill value as an extra `f64` param.
- Any compound/matrix result marshals via the existing `convert.rs` helpers (`fdmatrix_to_numpy2d`, `vec_to_numpy1d`); errors route through `to_pyresult()`.

### Layout Correctness (mandatory)
- Every matrix-returning binding (`functional_covariance` m×m, `spline_interpolate` onto a new grid) MUST go through `fdmatrix_to_numpy2d` and carry a MULTI-CURVE round-trip test (distinct per-curve values) — shape/symmetry checks alone do not catch the column-major #33 transposition class.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/lib.rs` — `register_submodule!` macro + the 16 existing `register_submodule!(m, "<name>", <mod>::register)` lines to extend for `represent`.
- `src/convert.rs` — numpy↔FdMatrix marshalling (`numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `vec_to_numpy1d`), `to_pyresult()`/`to_pyerr()`.
- `src/fdata_mod.rs` — pattern for `#[pyfunction]` fdata ops; extend with the 5 functional-statistics functions.
- `src/basis_mod.rs` / `src/alignment_mod.rs` — reference string-enum bindings (`basis_type`, `linkage`, `penalty_type`) for the `ExtrapolationPolicy`/`ImputationMethod` match pattern.
- `python/fdars/fdata_class.py` — `Fdata` class; add `interpolate()`/`impute()`/`var()`/`std()`/`cov()`/`median()` methods next to `mean()`/`deriv()`/`geometric_median()`.
- `python/fdars/__init__.py` — `_submodule_names` tuple + registration loop to add `represent`.

### Established Patterns
- Dimension suffix `_1d`/`_2d`; thin 5–15 line wrappers; `#[pyo3(signature = (...))]` for defaults; PyReadonlyArray inputs / PyArray outputs.
- Tests in `tests/` (pytest); `.venv/bin/maturin develop` to rebuild `_native` before testing.

### Integration Points
- New `fdars.represent` namespace reachable as both `from fdars.represent import spline_interpolate` and `fdars.represent.spline_interpolate(...)` via the sys.modules injection loop in `__init__.py`.
- `Fdata` methods delegate to the native funcs; must handle argvals/grid consistently with existing methods.

</code_context>

<specifics>
## Specific Ideas

- `functional_covariance` is exposed both module-level (`fdars.fdata.functional_covariance`) and as `fd.cov()`.
- `trim_mean` at α=0 must reproduce the plain mean exactly (assert in tests).
- `spline_interpolate` reuses the already-bound B-spline basis system upstream — no new numerical infrastructure.
- Exact fdars-core 0.17.0 signatures (`ShiftRegistrationResult` is Phase 27; here: `spline_interpolate`, `impute_missing_values`, `functional_*`) should be confirmed against the crate source/docs.rs at plan/execute time before writing wrappers.

</specifics>

<deferred>
## Deferred Ideas

- Scoring metrics, shift registration, registration-quality, banded elastic alignment → Phase 27.
- Advisor/diagnostics for imputation quality → Phase 28 (represent aspect).
- Diagrams + worked examples for these methods → Phase 29.

</deferred>
