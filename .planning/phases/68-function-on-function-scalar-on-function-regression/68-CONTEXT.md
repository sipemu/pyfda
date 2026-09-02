# Phase 68: Function-on-Function & Scalar-on-Function Regression - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

Close the visible gap in the regression surface by binding fdars-core 0.33's
function-on-function regression (incl. random effects) into the existing
`fdars.regression` submodule, and the additive/generalized scalar-on-function models +
selection routines into a NEW `fdars.scalar_on_function` submodule.

In scope (REG-01, REG-02, REG-03):
- **`fdars.regression` extensions** (edit `src/regression_mod.rs`): `fof_regression`, `predict_fof` (predict), `fof_re_regression`, `predict_fof_re`, and `fof_cv`.
- **NEW `fdars.scalar_on_function` submodule** (`src/scalar_on_function_mod.rs` + `src/lib.rs` + `python/fdars/__init__.py`): `fam`, `fregre_gkam`, `fregre_gsam`, `variable_selection`, `model_selection_ncomp`.

Out of scope: advisor extensions for these methods (ADV-01 → Phase 72), docs page
(DOCS-01 → Phase 73), other binding families (67, 69, 70, 71).

Parallelizable: touches `regression_mod.rs` + a new `scalar_on_function_mod.rs`; disjoint
from other groups' module files.

</domain>

<decisions>
## Implementation Decisions

### Predict API shape (user decision)
- **Combined-refit, stateless.** `predict_fof` / `predict_fof_re` take raw training data +
  response + new_x + argvals + params, fit the fof/fof_re model internally, then predict —
  NO opaque `#[pyclass]` handle, NO dict round-trip. Consistent with Phase 67's
  combined-function pattern and all 20 existing stateless native modules. Stateful
  fit-once/predict-many belongs to the pure-Python / sklearn layer, not the native binding.
- `fof_regression` / `fof_re_regression` still return their full result PyDict (beta
  surface + fitted state + diagnostics) for inspection.

### Scope (user decision)
- **Include `fof_cv`** — bind the fof cross-validation routine too (already in 0.33,
  disjoint, natural companion to `fof_regression`, mirrors the existing regression-CV
  surface). Total Phase 68 surface = 10 functions.

### Claude's Discretion (convention-driven)
- **Return shape:** documented PyDict from each result struct (`FofResult`, `FofReResult`,
  and the additive/generalized/selection result structs); confirm exact 0.33 field names
  against registry source before writing converters.
- **Transposition + argvals guard:** every 2D input via `convert::numpy2d_to_fdmatrix`;
  every 2D-input function gets a NON-SQUARE (`n_obs ≠ n_points`) fixture; `argvals` handled
  the same way as existing 2D-input regression bindings.
- **Random-effects subject-id validation (REG-02):** `fof_re_regression` validates the
  subject-id vector (length matches n_obs; raises `ValueError` on mismatch/degenerate groups).
- **Enum/`#[non_exhaustive]` args:** additive/generalized models likely take a GLM family
  (e.g. `GlmFamily`) and/or link/smoothing enums — expose as strings with an `Err`-returning
  wildcard match arm listing valid variants (locked STATE decision).
- **Defaults** via `#[pyo3(signature=...)]` following existing regression conventions
  (`ncomp=3`, `lambda=0.0`, `seed=42` where applicable).
- **Error handling:** `FdarError` → `PyValueError` via `convert::to_pyresult`.

</decisions>

<code_context>
## Existing Code Insights

### fdars-core 0.33 API surface (from registry source)
- `fof_regression.rs`: `fof_regression` (:113), `predict_fof` (:341, takes `&FofResult`), `fof_cv` (:419), `fof_re_regression` (:675), `predict_fof_re` (:943, takes `&FofReResult`)
- `scalar_on_function/additive.rs`: `fam` (:430), `fregre_gkam` (:564), `fregre_gsam` (:842), `variable_selection` (:1188)
- `scalar_on_function/fregre_lm.rs`: `model_selection_ncomp` (:362)

### Reusable Assets
- `src/regression_mod.rs` — existing regression bindings; extend it for the fof functions (mirror its `#[pyfunction]` + PyDict style).
- `src/convert.rs` — `numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `to_pyresult`.
- Phase 67's `src/fts_mod.rs` — fresh worked example of the combined-function pattern for struct-ref inputs and of new-submodule registration.
- `src/lib.rs` register_submodule! block + `python/fdars/__init__.py` name list — add `scalar_on_function`.

### Integration Points
- Extend `regression` submodule (existing) + register new `scalar_on_function` submodule; new tests under `tests/`.

</code_context>

<specifics>
## Specific Ideas

- Confirm exact 0.33 field names of `FofResult`, `FofReResult`, and the additive/generalized/selection result structs against `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/src/{fof_regression.rs,scalar_on_function/}` — the 0.31/0.32 changelog gap means docs.rs may 404.
- The additive/generalized SoF models (`fam`/`fregre_gkam`/`fregre_gsam`) are the most parameter-heavy; check for config structs / enum args and non-square-fixture needs.
- FND-02 guard (refactored in Phase 67) now tolerates the new `scalar_on_function` submodule registration — the full suite must stay green.

</specifics>

<deferred>
## Deferred Ideas

- Advisor extension for the new regression methods (ADV-01) — Phase 72.
- fof/sof-regression docs page with runnable offline example (DOCS-01) — Phase 73.

</deferred>
