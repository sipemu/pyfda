# Phase 32: Group B — Depth/Boxplot Bindings - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — decisions fully determined by research + Phase 31 precedent; no open user decisions to surface

<domain>
## Phase Boundary

Extend the existing `fdars.depth` submodule with two new functions from fdars-core 0.20: `functional_depth` (unified self-depth dispatcher) and `functional_boxplot` (López-Pintado–Romo functional boxplot — numeric median / 50% central region / whiskers / flagged outliers / per-curve depths). Covers DEPTH-01, DEPTH-02. Depends on Phase 30 (green 0.20 baseline). Does NOT include plotting (numeric result only; `fdars.plot` helper is deferred → PLOT-01), the advisor boxplot-outlier diagnostics (Phase 34, optional), or docs (Phase 35).

</domain>

<decisions>
## Implementation Decisions (locked by research + Phase 31 conventions)

### API surface
- `fdars.depth.functional_depth(data, method="fraiman_muniz"|"band"|"modified_band"|"random_projection", **kwargs)` → `ndarray (n,)` of self-depth values. `method` is dispatched to the `DepthMethod` enum by string, with a `#[non_exhaustive]` wildcard `_ => PyValueError` fallback for unknown method strings. Per-variant kwargs (defaults): `scale: bool = True` (FraimanMuniz), `nproj: int = 50` + `seed: int|None = None`→0 (RandomProjection). `Band`/`ModifiedBand` take no extra params.
- `fdars.depth.functional_boxplot(data, method=..., factor=1.5, **kwargs)` → PyDict `{median, central_lower, central_upper, whisker_lower, whisker_upper, outliers, depths}`. The five band fields (`median`/`central_lower`/`central_upper`/`whisker_lower`/`whisker_upper`) are `Vec<f64>` → 1-D ndarrays of length m (via the per-field `vec_to_numpy1d` helper, NOT `fdmatrix_to_numpy2d`); `outliers` is `Vec<usize>` → a **Python list of ints** (row indices, not an ndarray); `depths` is `Vec<f64>` → 1-D ndarray of length n. `factor` default 1.5 (Tukey convention). Shares the `DepthMethod` string-dispatch helper with `functional_depth`.
- Module-level functions only (matching the DEPTH-01/02 requirement text). Fdata convenience methods (`fd.functional_depth()`/`fd.functional_boxplot()`) are NOT in scope — deferred as a possible future add (the v4.0 Fdata-method pattern exists but the requirements specify module-level).

### Correctness & conventions (from research PITFALLS + Phase 31 precedent)
- Verified 0.20 signatures (docs.rs + Phase 31 spike): `functional_depth(data: &FdMatrix, method: DepthMethod) -> Result<Vec<f64>, FdarError>`; `functional_boxplot(data: &FdMatrix, method: DepthMethod, factor: f64) -> Result<FunctionalBoxplotResult, FdarError>`. `DepthMethod` and `FunctionalBoxplotResult` are `#[non_exhaustive]` → field access only, no struct-literal construction in tests.
- No `.unwrap()`; route fallible calls through `to_pyresult()`; degenerate inputs (empty data, too few curves, unknown method, invalid nproj) raise `ValueError` with `pytest.raises` tests.
- `RandomProjection` `seed` exposed as `seed=None`→fixed default 0 for byte-identical reproducibility (mirror the Phase 31 seed contract); add a determinism test for `method="random_projection"`.
- Build a `DepthMethod`-from-string helper (mirrors the Phase 31 `multiplier_from_str` pattern) reused by both functions.
- Correctness test: `functional_depth(data, method="fraiman_muniz")` should agree with the existing lower-level `fraiman_muniz_1d(data, data)` self-depth (same reference == data), within tolerance — a cross-check that the dispatcher wires the right algorithm.

### Layout guard (the #33 transposition class)
- Even though the boxplot band fields are `Vec<f64>` (1-D, no transposition risk), add a shape/finite round-trip test on a MULTI-curve input asserting each band field has length m (== argvals/points), `depths` has length n, `outliers` are valid 0-based row indices in `[0, n)`, and all band values are finite — guarding against any silent length/orientation mistake.

### Claude's Discretion
- Test file layout (extend `tests/test_depth.py` or a new `tests/test_functional_boxplot.py`), fixture construction, and internal helper factoring are at Claude's discretion, following existing `src/depth_mod.rs` + `tests/` conventions.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/depth_mod.rs` — the existing depth submodule to EXTEND (already has `fraiman_muniz_1d`, `band_1d`, etc.); add `functional_depth` + `functional_boxplot` + a `depth_method_from_str` helper here. No new submodule registration needed (already registered in lib.rs).
- `src/convert.rs` — `numpy2d_to_fdmatrix`, `vec_to_numpy1d` (used in Phase 31 for ToleranceBand fields), `to_pyresult()`.
- `src/inference_mod.rs` (Phase 31) — the `multiplier_from_str` string-dispatch + `#[non_exhaustive]` fallback pattern and the `seed=None`→0 idiom to mirror.

### Established Patterns
- String-enum dispatch + `_ => PyValueError` fallback; compound result → PyDict; `Vec<usize>` → Python list of ints; `Vec<f64>` → `vec_to_numpy1d`.
- fdars-core 0.20.0 source vendored at `/home/simonm/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.20.0/src/depth/` (dispatch.rs holds `DepthMethod` + `FunctionalBoxplotResult` + `functional_depth`/`functional_boxplot`) — authoritative signature reference.

### Integration Points
- Edits confined to `src/depth_mod.rs` + `tests/`. Build via `maturin develop`; test via pytest. rustfmt + clippy `-D warnings` clean.

</code_context>

<specifics>
## Specific Ideas

- Dataset for tests + the canonical example: Canadian Weather temperature (35 stations × daily grid) — López-Pintado–Romo's original functional-boxplot dataset; expect a small number of flagged outlier stations at factor=1.5. Keep test data small; use `nproj` small (e.g. 20) in RandomProjection tests for speed.

</specifics>

<deferred>
## Deferred Ideas

- `fdars.plot.plot_functional_boxplot()` visual helper → PLOT-01 (future); the numeric dict is this phase's deliverable.
- `fd.functional_depth()` / `fd.functional_boxplot()` Fdata convenience methods → possible future add (not required by DEPTH-01/02).
- Advisor functional-boxplot outlier diagnostics → Phase 34 (optional, ADV-03 scope).
- Docs page + SVG + worked example → Phase 35 (DOCS-05).

</deferred>
