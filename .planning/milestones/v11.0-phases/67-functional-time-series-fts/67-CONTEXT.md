# Phase 67: Functional Time Series (`fdars.fts`) - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

Deliver a new importable `fdars.fts` submodule that binds fdars-core 0.33's `fts`
module (a new `src/fts_mod.rs`, registered in `src/lib.rs`, exposed via
`python/fdars/__init__.py`). Users can fit and forecast functional time series and
compute time-series diagnostics.

In scope (FTS-01, FTS-02, FTS-03): thin PyO3 bindings over the fts functions, each
returning a documented PyDict, transposition-correct on non-square (`n_obs ≠ n_points`)
input.

Out of scope: advisor `fts` aspect (ADV-01 → Phase 72), docs page (DOCS-01 → Phase 73),
any other binding family (Phases 68–71).

Parallelizable: new `src/fts_mod.rs` is disjoint from other binding groups.

</domain>

<decisions>
## Implementation Decisions

### Binding Scope
- **Bind the FULL fts module — all 13 public functions** (user decision):
  - Forecasting: `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`
  - Dimension reduction / spectral: `fplsr`, `dpca`, `dpca_reconstruct`, `spectral_density`
  - Diagnostics: `functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance`
- Rationale: all are already compiled in 0.33, disjoint, and each is a thin wrapper — excluding the 4 optional extras (`ftsm_update`, `dpca_reconstruct`, `spectral_density`, `functional_difference`) would only leave value on the table and invite a follow-up phase.

### Claude's Discretion (convention-driven — not asked)
- **Return shape:** every function returns a documented PyDict built from the fdars-core result struct (matches project convention for structured returns). Struct fields map to dict keys; verify exact 0.33 field names against registry source before writing the PyDict converter (STATE research-gap note).
- **Binding style:** thin native 1:1 `#[pyfunction]` wrappers only, consistent with all 20 existing `*_mod.rs` submodules. No pure-Python convenience/class layer for fts.
- **`ncomp` default:** `ncomp=3` via `#[pyo3(signature = ...)]`, matching the established default in `pace_fpca_mod.rs` and `conformal_mod.rs`.
- **Transposition safety:** route all 2D array inputs through `convert::numpy2d_to_fdmatrix` (row-major↔column-major); every function that takes 2D data gets a non-square (`n_obs ≠ n_points`) test fixture (locked STATE decision — square fixtures hide layout bugs).
- **Determinism:** where an upstream fts function accepts a seed, expose it with a fixed default (convention: `seed=42` as in `conformal_mod.rs`) so results are deterministic.
- **Error handling:** propagate `FdarError` → `PyValueError` via `convert::to_pyresult`; any `#[non_exhaustive]` enum argument gets an `Err`-returning wildcard arm listing valid variants (locked STATE decision).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/convert.rs` — `numpy2d_to_fdmatrix` (transposition), `to_pyresult`/`to_pyerr` (error mapping), argvals/grid helpers.
- Pattern module to mirror: any thin `*_mod.rs` (e.g. `pace_fpca_mod.rs`, `seasonal_mod.rs`) — `#[pyfunction]` + `#[pyo3(signature=...)]` + PyDict return.
- `src/lib.rs` — `register_submodule!(m, "fts", fts_mod::register);` alongside the existing 20; add `mod fts_mod;`.
- `python/fdars/__init__.py` — dynamic submodule registration loop; add `fts` to `_submodule_names`.

### fdars-core 0.33 fts API surface (from registry source)
- `fts::acf`: `functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance`
- `fts::forecast`: `ftsm(data, ncomp, argvals) -> FtsmResult`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr(data, ncomp, argvals) -> FplsrResult`
- `fts::spectral`: `dpca`, `dpca_reconstruct`, `spectral_density`
- Result structs (fields to become PyDict keys): `FtsmResult`, `FtsmForecastResult`, `FplsrResult`, `DpcaResult`, `DpcaReconstruction`, `SpectralDensityResult`, `FacfResult`, `StationarityResult`, `LongRunCovResult`, `ArModelResult`.

### Integration Points
- `src/lib.rs` submodule registration; `python/fdars/__init__.py` name list; new tests under `tests/` with a non-square fixture.

</code_context>

<specifics>
## Specific Ideas

- Confirm exact 0.33 result-struct field names against `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/src/fts/` before writing PyDict converters — the 0.31/0.32 changelog gap means field names cannot be assumed from docs.rs.
- ftsm/fplsr take `argvals: &[f64]` — the binding must accept/derive the evaluation grid consistently with how other 2D-input bindings handle argvals.

</specifics>

<deferred>
## Deferred Ideas

- Advisor `fts` aspect (ADV-01) — Phase 72.
- `fdars.fts` docs page with runnable offline worked example (DOCS-01) — Phase 73.

</deferred>
