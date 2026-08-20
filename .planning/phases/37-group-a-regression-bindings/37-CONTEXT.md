# Phase 37: Group A — Regression Bindings - Context

**Gathered:** 2026-08-20
**Status:** Ready for planning
**Mode:** Smart-discuss (autonomous) — grey areas resolved from milestone research (`.planning/research/FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md`), full-autonomy run

<domain>
## Phase Boundary

Expose fdars-core 0.23's two new regression estimators through the existing `fdars.regression` PyO3 submodule, layout-correct across the numpy↔FdMatrix boundary:
- `concurrent_regression` / `ConcurrentRegrResult` — concurrent (varying-coefficient) functional regression.
- `functional_glm` / `FunctionalGlmResult` — exponential-family GLM over FPC scores.

Requirements: REGR-01, REGR-02, REGR-03. Extends `src/regression_mod.rs` (+ `register_submodule!` already wired). No new submodule, no new Rust module file.

</domain>

<decisions>
## Implementation Decisions

### Python API surface
- `fdars.regression.concurrent_regression(predictors, response, argvals, ...)` — `predictors` is a Python `list[np.ndarray]` (slice-of-matrices; one (n_obs × m) matrix per predictor). Returns a `dict` mirroring `ConcurrentRegrResult` fields: `beta_curve`, `intercept`, `fitted`, `residuals`, `argvals`.
- `fdars.regression.functional_glm(data, response, argvals, family=..., n_comp=..., ...)` — returns a `dict` mirroring all `FunctionalGlmResult` fields. Wrapper re-fits FPCA internally (raw data in, no persistent handle) — same pattern as the v5.0 `flm_f_test` binding.
- Exact remaining kwargs (penalty/lambda, max_iter, tol, intercept flag) are read from the v0.23.0 signatures at plan/execute time and surfaced with fdars-core's own defaults via `#[pyo3(signature = (...))]`.

### Result → PyDict conversion
- One converter per result struct (`concurrent_regr_result_to_pydict`, `functional_glm_result_to_pydict`), following the canonical `test_result_to_pydict` pattern in `inference_mod.rs`. `FdMatrix` fields convert via the existing `fdmatrix_to_numpy2d` helper; `Vec<f64>` → 1-D numpy; scalars → Python floats (never numpy scalars).

### Layout / transposition
- `ConcurrentRegrResult.beta_curve` is `(p, m)` (predictors × grid), NOT the pyfda-standard `(n_obs, m)`. Convert it faithfully and add an explicit multi-predictor (`p ≥ 2`) transposition guard test (v4.0 Phase 27 pattern) so a silent transpose can't pass.
- `functional_glm` matrix outputs (fitted values / any coefficient matrix) transposition-checked the same way.

### GlmFamily dispatch
- `family` is a Python string dispatched to the `#[non_exhaustive]` `GlmFamily` enum via a `match` with a wildcard `_ => PyValueError` fallback listing supported families. String values: `"binomial"`, `"poisson"`, `"gamma"`, `"gaussian"` (exact tokens confirmed against the enum at execute time).

### Error handling
- All fallible calls route through `to_pyresult()` (no `.unwrap()`). Degenerate inputs raise `ValueError`: mismatched grids/lengths, too few curves, invalid family, invalid/zero `n_comp`, ragged predictor list.

### Docs-facing caveats (carry to Phase 41 DOCS-08)
- Gamma family uses the inverse canonical link (1/μ), NOT log.
- `functional_glm` AIC magnitude is not comparable to R's `glm()` — document, don't "fix".

### Claude's Discretion
Everything not pinned above (exact parameter defaults, test data choices, dict key names matching struct fields) is at Claude's discretion, grounded in the v0.23.0 source signatures and existing `regression_mod.rs` conventions. No Fdata convenience methods this phase (submodule functions only, matching the requirements).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/regression_mod.rs` — the target module (existing FLM/FPCA regression bindings + `register_submodule!` wiring).
- `src/inference_mod.rs` — the canonical `TestResult`→PyDict converter pattern (v5.0) + `#[non_exhaustive]` wildcard dispatch precedent.
- `src/convert.rs` — `numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `to_pyresult`, `to_pyerr`.
- fdars-core v0.23.0 source at `/home/simonm/projects/rust/fdars` (tag `v0.23.0`): `src/concurrent_regression.rs`, `src/scalar_on_function/glm.rs` — authoritative signatures + result-struct fields.

### Established Patterns
- Thin `#[pyfunction]` wrappers; `#[pyo3(signature = (...))]` for defaults; dict returns for structured results; column-major FdMatrix ↔ row-major numpy transposition at the boundary; transposition-guard tests for any matrix in/out.

### Integration Points
- `src/regression_mod.rs` (new `#[pyfunction]`s + converters), `register_submodule!` in `lib.rs` (already registers `regression`), `tests/` (new pytest coverage incl. transposition guards).

</code_context>

<specifics>
## Specific Ideas

Follow the v0.23.0 source signatures exactly; mirror the v5.0 `fdars.inference` binding structure (converter helper + dict result + deterministic tests). Keep worked-example data small (Phase 41 owns docs; this phase's tests can use synthetic or existing small datasets).

</specifics>

<deferred>
## Deferred Ideas

- Advisor coverage of `functional_glm`/`concurrent_regression` — Phase 40 (ADV-05), not here.
- Docs pages + SVGs + worked examples — Phase 41 (DOCS-08).
- PACE-FPCA / elastic_multinomial — Phase 38 (Group B).

</deferred>
