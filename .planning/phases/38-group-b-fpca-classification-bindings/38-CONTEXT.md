# Phase 38: Group B — FPCA & Classification Bindings - Context

**Gathered:** 2026-08-20
**Status:** Ready for planning
**Mode:** Smart-discuss (autonomous) — grey areas resolved from milestone research + a direct v0.23.0 source peek; full-autonomy run

<domain>
## Phase Boundary

Expose fdars-core 0.23's sparse/irregular PACE FPCA and its K-class elastic multinomial classifier to Python:
- A new sparse/irregular functional-data input path (`IrregFdata` builder) + `pace_fpca` in a NEW `src/pace_fpca_mod.rs`.
- `elastic_multinomial` extending the existing `fdars.classification` submodule.

Requirements: PACE-01, PACE-02, CLASS-01. This is the milestone's one structurally-novel phase (the `IrregFdata` input has no PyO3 precedent in pyfda) — the tracer front-loads that risk.

</domain>

<decisions>
## Implementation Decisions

### IrregFdata builder (PACE-01)
- Expose a top-level `fdars.irreg_fdata_from_lists(argvals_list, values_list)` that accepts two Python lists of 1-D array-likes (one per curve, ragged) and builds fdars-core's `IrregFdata` via `IrregFdata::from_lists(argvals_list: &[Vec<f64>], values_list: &[Vec<f64>])`.
- Return an opaque Python handle wrapping the Rust `IrregFdata` (a `#[pyclass]`) so `pace_fpca` can consume it by reference — this is the clean way to pass a non-array Rust type across the boundary. (If a `#[pyclass]` wrapper proves heavy, an acceptable fallback is to have `pace_fpca` itself accept the two lists directly and build `IrregFdata` internally — decided in the tracer based on what's cleanest; either satisfies PACE-01/02.)
- Reject a plain dense 2-D numpy array with a clear `ValueError` (never silently misinterpret it as ragged lists). Per-curve `len(argvals[i]) == len(values[i])` validated → `ValueError` on mismatch.

### pace_fpca (PACE-02) — new src/pace_fpca_mod.rs
- `fdars.pace_fpca(data, ncomp=..., bandwidth=..., work_grid=None, alpha=...)` where `data` is the IrregFdata handle (or the two lists per the tracer decision). `PaceFpcaConfig` is NOT `#[non_exhaustive]` → build it by struct literal from flat Python kwargs (ncomp, bandwidth, work_grid, alpha; defaults read from core at execute time).
- Returns a `dict` mirroring `PaceFpcaResult`: `mean` (1-D), `eigenvalues` (1-D), `eigenfunctions` (m,ncomp), `scores` (n,ncomp), `fitted` / `fitted_lower` / `fitted_upper` (n,m), `argvals` (1-D), `ncomp` (int). `eigenfunctions (m,ncomp)` and `scores (n,ncomp)` are transposition-guarded (choose n≠m≠ncomp in the test so a transpose can't pass). `pace_fpca` returns `Result` → `to_pyresult()`.
- New module registered: `src/pace_fpca_mod.rs` + `register_submodule!`/top-level function in `lib.rs` + `_submodule_names`/`__init__.py` as appropriate.

### elastic_multinomial (CLASS-01) — extend fdars.classification
- `fdars.classification.elastic_multinomial(data, labels, argvals, ...)` → dict from `ElasticMultinomialResult`. Labels must be 0-indexed contiguous (`0..K`); add the v5.0 CR-01 negative/non-contiguous-label guard (check before the `i64→usize` conversion) → helpful `ValueError`, never a `usize::MAX` wrap.
- `train_probabilities (n,K)` transposition-guarded at K≥3 (K≠n).

### Converters / errors
- New `*_to_pydict` converters (pace, elastic_multinomial) mirroring `test_result_to_pydict`; FdMatrix→`fdmatrix_to_numpy2d`, Vec→1-D numpy, scalars→Python float. All fallible calls via `to_pyresult()`; no `.unwrap()`. Degenerate inputs (ragged list mismatch, dense-array-to-builder, invalid ncomp/labels, too few curves) raise `ValueError`.

### Claude's Discretion
The `#[pyclass]`-handle vs lists-directly choice for IrregFdata (resolved in the tracer), exact kwarg defaults, and dict key names (= struct field names) are at Claude's discretion, grounded in the v0.23.0 source. No advisor work here (Phase 40); no docs here (Phase 41).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/classification_mod.rs` — target for `elastic_multinomial`; existing `elastic_logistic` (binary) is the direct analogue to generalize to K-class OvR.
- `src/inference_mod.rs` — converter + `#[non_exhaustive]` wildcard precedent; `src/convert.rs` — `numpy2d_to_fdmatrix`/`fdmatrix_to_numpy2d`/`to_pyresult`.
- `src/lib.rs` — `register_submodule!` macro + top-level function registration pattern.
- fdars-core v0.23.0 (tag) at `/home/simonm/projects/rust/fdars`: `src/irreg_fdata/mod.rs` (`IrregFdata::from_lists`), `src/pace_fpca.rs` (`pace_fpca`, `PaceFpcaConfig`, `PaceFpcaResult`), `src/elastic_regression/logistic.rs` (`elastic_multinomial`, `ElasticMultinomialResult`).

### Established Patterns
- Thin `#[pyfunction]` wrappers; `#[pyo3(signature=...)]` defaults; dict returns; column-major↔row-major transposition at the boundary + guard tests; `#[pyclass]` opaque handles are NOT yet used in pyfda — this phase introduces the first, if the handle approach is chosen.

### Integration Points
- NEW `src/pace_fpca_mod.rs`; edits to `src/classification_mod.rs`, `src/lib.rs` (register new module/function), `python/fdars/__init__.py` (if a new submodule/top-level symbol is added), `tests/` (new pytest coverage incl. transposition + label guards + IrregFdata validation).

</code_context>

<specifics>
## Specific Ideas

Front-load the `IrregFdata` binding in the tracer (compile + a real sparse round-trip through `pace_fpca`) before expanding. Use small inline synthetic sparse data for tests (no existing docs/data dataset is irregular). `elastic_multinomial` tests can subsample phoneme.csv or use synthetic multi-class data.

</specifics>

<deferred>
## Deferred Ideas

- Advisor coverage of pace_fpca / elastic_multinomial — Phase 40 (ADV-05, decided at plan time there).
- Docs pages + SVGs + worked examples (PACE irregular-observations diagram; synthetic sparse fence) — Phase 41 (DOCS-09).
- Group C depth/outliers/ITP — Phase 39.

</deferred>
