# Phase 71: Shapelets & GAK Metric - Context

**Gathered:** 2026-09-04
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

The final binding phase: a new `fdars.shapelet` submodule (with a fitted-state opaque
handle + classifier) and the Global-Alignment-Kernel metric extending `fdars.metric`
(with its Gram matrix usable as a precomputed sklearn kernel).

In scope:
- **SHAPE-01 — new `fdars.shapelet` submodule:** `discover_shapelets`,
  `shapelet_transform_fit` (→ `PyShapeletFit` opaque handle), `shapelet_transform`
  (consumes the handle), `shapelet_classifier_fit`, `shapelet_distance`. Two new
  `#[non_exhaustive]` enums dispatched by string with an `Err` fallback arm:
  `QualityMeasure` (InfoGain / FStatistic) and `ShapeletClassifier` (Knn{k}, …).
- **SHAPE-02 — GAK metric extending `fdars.metric`:** `gak`, `gak_gram_matrix`,
  `gak_gram_train` (→ `PyGakGramTrain` opaque handle), `gak_gram_predict` (consumes the
  handle), `sigma_gak`. Gram output usable as a precomputed kernel (`metric="precomputed"`).

Out of scope: advisor extensions (ADV-01 → Phase 72), docs (DOCS-01 → Phase 73).

Parallelizable: new `src/shapelet_mod.rs` + `metric` extension; disjoint from other groups
(worktrees disabled here anyway — sequential on main).

</domain>

<decisions>
## Implementation Decisions

### GAK train/predict API shape (user decision)
- **Opaque `PyGakGramTrain` handle.** `gak_gram_train` returns a `PyGakGramTrain` opaque
  `#[pyclass]` (wrapping `GakGramTrain`); `gak_gram_predict(handle, new_data)` reuses it —
  no wasteful refit. Consistent with `PyShapeletFit` in this same phase and with the
  sklearn precomputed-kernel workflow (fit kernel once on train, reuse for test batches).
  `gak_gram_matrix` (the one-shot symmetric full Gram) is ALSO bound (already required) for
  simple single-shot use. This is pyfda's 4th opaque handle (after PyIrregFdata,
  PyMultiFunData, PyShapeletFit).

### Claude's Discretion (convention-driven)
- **PyShapeletFit handle:** required by SHAPE-01 — opaque `#[pyclass]` wrapping the fitted
  `ShapeletSet`; `shapelet_transform_fit` returns it, `shapelet_transform(fit, data)` and
  `shapelet_classifier_fit` consume it. Mirror the PyIrregFdata/PyMultiFunData/PyShapeletFit
  opaque-handle template.
- **Enum string dispatch (mandatory Err arm — locked STATE decision):**
  - `QualityMeasure`: unit variants → simple `quality_from_str("info_gain"|"f_statistic")`
    with an `Err`-returning wildcard listing valid names.
  - `ShapeletClassifier`: **data-carrying** (`Knn { k: usize }`, plus any others) → the
    string dispatch also takes the classifier's parameter(s) (e.g. `classifier="knn", k=...`);
    Err wildcard lists valid classifier names. Confirm the full variant set + their fields
    in research.
- **Return shape:** documented PyDict per result struct where a function returns structured
  data; `shapelet_transform` returns an FdMatrix → 2D numpy array; `gak(x,y,sigma)` and
  `sigma_gak` return scalars; `gak_gram_matrix` / `gak_gram_predict` return 2D numpy Gram
  matrices. Confirm exact 0.33 result-struct field names in research.
- **Precomputed-kernel contract:** `gak_gram_matrix` returns a symmetric (n,n) matrix;
  `gak_gram_predict` returns (n_test, n_train) — both directly usable with sklearn
  `metric="precomputed"` / `kernel="precomputed"`. Test this shape contract.
- **Transposition:** every 2D input via `numpy2d_to_fdmatrix`; NON-SQUARE (`n_obs ≠ n_points`)
  fixtures. `gak(x, y, sigma)` takes two 1D series.
- **Determinism:** `seed` default where `discover_shapelets` / classifiers take one.
- **Error handling:** `FdarError` → `PyValueError` via `convert::to_pyresult`; guard opaque-handle
  builders before the core constructor (like irreg_fdata_from_lists).

</decisions>

<code_context>
## Existing Code Insights

### fdars-core 0.33 API surface (from registry source)
- `shapelet/discovery.rs`: `discover_shapelets` (:399); `QualityMeasure` enum (:33 — InfoGain[default], FStatistic).
- `shapelet/transform.rs`: `shapelet_transform_fit` (:242 → fitted ShapeletSet), `shapelet_transform(shapelets: &ShapeletSet, data: &FdMatrix)` (:96).
- `shapelet/classifier.rs`: `shapelet_classifier_fit` (:238); `ShapeletClassifier` enum (:44 — Knn{k}, …).
- `shapelet/distance.rs`: `shapelet_distance` (:246).
- `metric/gak.rs`: `gak(x,y,sigma)` (:155), `sigma_gak(data)` (:191), `gak_gram_matrix(data, &GakConfig)` (:255), `gak_gram_train(data, &GakConfig) -> GakGramTrain` (:414), `gak_gram_predict(train: &GakGramTrain, new_data)` (:458).

### Reusable Assets
- `src/pace_fpca_mod.rs` / `src/multi_fdata_mod.rs` — opaque `#[pyclass]` handle template (PyIrregFdata / PyMultiFunData) for PyShapeletFit + PyGakGramTrain.
- `src/scalar_on_function_mod.rs` (`penalty_from_str`) + `src/frechet_mod.rs` (space dispatch) — string→enum Err-arm dispatch analogs.
- `src/metric_mod.rs` — the module to EXTEND for GAK; follow its style + register.
- `src/convert.rs` — numpy2d_to_fdmatrix, numpy1d_to_vec, to_pyresult.

### Integration Points
- NEW `src/shapelet_mod.rs`; MODIFY `src/metric_mod.rs` (add 5 GAK fns + PyGakGramTrain handle); MODIFY `src/lib.rs` (1 new submodule) + `python/fdars/__init__.py` (1 name: shapelet); new tests.

</code_context>

<specifics>
## Specific Ideas

- Confirm the FULL `ShapeletClassifier` variant set + each variant's fields (Knn{k} plus any others) — drives the classifier string-dispatch signature.
- Confirm `GakConfig` fields + `#[non_exhaustive]` status (→ Default::default() + mutation), and `discover_shapelets` config/params (min/max length, seed?).
- PyShapeletFit + PyGakGramTrain opaque handles: guard builders before the core call; add sensible accessors (e.g. n_shapelets).
- FND-02 guard (Phase 67) tolerates the new `shapelet` submodule — full suite must stay green.

</specifics>

<deferred>
## Deferred Ideas

- Advisor extension for shapelet/GAK (ADV-01) — Phase 72.
- shapelet docs page with runnable offline example (DOCS-01) — Phase 73.

</deferred>
