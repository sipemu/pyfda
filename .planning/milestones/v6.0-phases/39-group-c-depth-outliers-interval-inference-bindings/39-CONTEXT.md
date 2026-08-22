# Phase 39: Group C — Depth / Outliers / Interval-Inference Bindings - Context

**Gathered:** 2026-08-21
**Status:** Ready for planning
**Mode:** Smart-discuss (autonomous) — grey areas resolved from milestone research + a direct v0.23.0 source peek; full-autonomy run

<domain>
## Phase Boundary

Expose fdars-core 0.23's remaining new surface across three independent areas:
- **Depth** (extend the v5.0 `functional_depth` dispatcher in `fdars.depth`): 9 new `DepthMethod` variants.
- **Outliers** (extend `fdars.outliers`): 4 new detectors.
- **Interval inference** (extend the v5.0 `fdars.inference` submodule): 3 interval-wise tests (ITP).

Requirements: DEPTH-03, OUTL-01, OUTL-02, OUTL-03, OUTL-04, ITP-01, ITP-02, ITP-03, ITP-04 (9 REQ-IDs — the milestone's largest binding phase). The three areas touch distinct modules (`depth_mod.rs`, `outliers_mod.rs`, `inference_mod.rs`) and are mutually independent — the planner may split into parallel plans.

</domain>

<decisions>
## Implementation Decisions

### Depth (DEPTH-03)
- Add the 9 new `DepthMethod` variants to the existing string dispatcher (`depth_method_from_str`) in `depth_mod.rs`: `hypograph_index`, `modified_hypograph_index`, `epigraph_index`, `half_region`, `modified_half_region`, `extremal`, `extreme_rank_length`, `l_infinity`, `total_variation` (existing: fraiman_muniz, band, modified_band, random_projection → 13 total). Update the `#[non_exhaustive]` wildcard error message to list all supported methods. `functional_boxplot`'s `method` param accepts the new variants too. No signature change to `functional_depth`/`functional_boxplot` — just dispatch coverage + tests.

### Outliers (OUTL-01..04) — extend fdars.outliers
- Each detector takes a config struct in core — build it by struct literal (or Default + overrides) from flat Python kwargs, exact fields read at execute time:
  - `fdars.outliers.tvdmss(data, argvals, ...)` → dict from `TvdMssOutliers` (`TvdMssConfig`).
  - `fdars.outliers.muod(data, argvals, ...)` → dict from `MuodResult` (`MuodConfig`) — amplitude/magnitude/shape index sets + scores.
  - `fdars.outliers.sequential_transform_outliers(data, argvals, transforms=[...], ...)` → dict from `SeqTransformOutliers`; `transforms` maps a `#[non_exhaustive]` `SeqTransform` enum via string with a `ValueError` wildcard fallback.
  - `fdars.outliers.depthgram(data, argvals, ...)` → dict from the depthgram result (`DepthgramConfig`) — the two depth indices + flagged outliers.
- Outlier index sets exposed as Python `list[int]`; scores/thresholds as 1-D numpy / floats. Any permutation/random component takes `seed=None` → fixed default for byte-identical offline reproducibility (plan-time audit of the config structs for a seed field).

### Interval inference (ITP-01..04) — extend fdars.inference
- `fdars.inference.itp_one_pop(data, argvals, mu0=..., ...)`, `.itp_two_pop(data_a, data_b, argvals, ..., seed=None)`, `.itp_flm(data, response, argvals, ..., basis_type=...)`.
- Each returns a dict from `ItpResult { adjusted_pvalues: Vec (vector p-values), raw_pvalues: Vec, basis_type, n_basis, n_perm }` via a NEW `itp_result_to_pydict` helper (distinct from `test_result_to_pydict` — results are p-value VECTORS, exposed as 1-D numpy arrays). `basis_type` maps `#[non_exhaustive]` `ProjectionBasisType` via string with a `ValueError` fallback. `itp_flm` re-fits internally (no persistent handle). Permutation `seed=None` → fixed default.

### Converters / errors
- New `*_to_pydict` converters mirroring `test_result_to_pydict`; FdMatrix→`fdmatrix_to_numpy2d`, Vec<f64>→1-D numpy, Vec<usize>/index sets→Python `list[int]`, scalars→Python float (never numpy scalar). All fallible calls via `to_pyresult()`; no `.unwrap()`. Degenerate inputs (mismatched grids, too few curves, invalid method/transform/basis strings, bad params) raise `ValueError`.

### Claude's Discretion
The plan split (1 sequential plan vs 3 parallel depth/outliers/ITP plans), exact config-kwarg defaults, and dict key names (= struct field names) are at Claude's discretion, grounded in the v0.23.0 source. No advisor work here (Phase 40 owns ADV-04 outliers-aspect extension); no docs here (Phase 41, DOCS-10).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/depth_mod.rs` — existing `functional_depth`/`functional_boxplot` + `depth_method_from_str` string dispatcher (v5.0) — extend the match.
- `src/outliers_mod.rs` — existing outlier bindings (target for the 4 new detectors).
- `src/inference_mod.rs` — v5.0 `TestResult`→PyDict converter + `#[non_exhaustive]` wildcard precedent + seed=None→default pattern; extend with the 3 ITP fns + new `itp_result_to_pydict`.
- `src/convert.rs` — `fdmatrix_to_numpy2d`, `to_pyresult`, etc.
- fdars-core v0.23.0 (tag) at `/home/simonm/projects/rust/fdars`: `src/depth/dispatch.rs` (DepthMethod + 9 new variants), `src/outliers.rs` (tvdmss/muod/sequential_transform_outliers/depthgram + config structs + SeqTransform), `src/inference/itp.rs` (itp_* + ItpResult), `src/basis/projection.rs` (ProjectionBasisType).

### Established Patterns
- Thin `#[pyfunction]` wrappers; `#[pyo3(signature=...)]` defaults; dict returns; column-major↔row-major transposition + guard tests; `#[non_exhaustive]` enum string dispatch with wildcard `_ => PyValueError`; seed=None→fixed default for deterministic permutation tests.

### Integration Points
- `src/depth_mod.rs` (dispatcher extension), `src/outliers_mod.rs` (4 new fns + converters), `src/inference_mod.rs` (3 ITP fns + new converter), `src/lib.rs` (registration if any new fns need adding to a submodule's register()), `tests/` (new/extended pytest coverage: depth-method coverage, outlier detectors incl. seed determinism, ITP vector-p-value shape + basis dispatch + degenerate ValueError).

</code_context>

<specifics>
## Specific Ideas

Extend the depth dispatcher first (trivial match + tests), then outlier detectors, then ITP (needs the new `itp_result_to_pydict`). Keep test data small (synthetic or existing small datasets). Mirror the v5.0 `fdars.inference` binding structure for ITP.

</specifics>

<deferred>
## Deferred Ideas

- Advisor `outliers`-aspect extension (grounded diagnostics for the new detectors) — Phase 40 (ADV-04); ITP surfaced to advisor is also Phase 40.
- Docs pages + SVGs + worked examples (depth methods fold-in, functional-outliers page, interval-inference page) — Phase 41 (DOCS-10).

</deferred>
