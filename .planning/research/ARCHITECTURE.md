# Architecture Patterns

**Project:** pyfda — fdars-core 0.23.0 → 0.33.0 Upgrade
**Researched:** 2026-09-02
**Confidence:** MEDIUM (breaking-change assessment from CHANGELOG.md confirmed additive + deprecations only; new-module surface from docs.rs cross-checked against GitHub release notes; exact struct field stability inferred from field-access patterns in the docs)

---

## 1. Breaking Changes: 0.24 → 0.33 against the existing 0.23 surface

**Verdict: No hard breaking changes to any currently-bound function.** The changelog explicitly states every release from 0.24 through 0.33 is "additive and non-breaking — no existing public signature changed." The GitHub release notes for v0.24, v0.27, v0.28, v0.29, v0.32, v0.33 each confirm backward compatibility.

**One soft break introduced in 0.30:** six depth functions were marked `#[deprecated]` in favour of unified dispatchers. They remain functional and will not cause a compile error, but Rust's `#[deprecated]` attribute emits a compiler warning. This affects the following pyfda bindings:

| Deprecated function (depth module) | Used in pyfda file | Status |
|-------------------------------------|--------------------|--------|
| `fraiman_muniz_2d` | `src/depth_mod.rs` | Deprecated (0.30); still compiles |
| `modal_2d` | `src/depth_mod.rs` | Deprecated (0.30); still compiles |
| `random_projection_2d` | `src/depth_mod.rs` | Deprecated (0.30); still compiles |
| `random_tukey_2d` | `src/depth_mod.rs` | Deprecated (0.30); still compiles |

The unified replacements accept a `Dim` parameter. **The bump-gate phase (Phase 1) must build cleanly.** Deprecation warnings in Rust are not errors by default, and pyfda's `Cargo.toml` does not set `#![deny(deprecated)]`, so this will not block the build. The deprecation warnings should be addressed in the new-bindings phase (Phase 2) as part of migration, not the bump phase.

**Struct fields accessed by the existing bindings:** All struct fields accessed by the current `*_mod.rs` converters are still present in 0.33.0 per the docs.rs field listings:
- `ConcurrentRegrResult`: `beta_curve`, `intercept`, `fitted`, `residuals`, `argvals` — confirmed present
- `GmmClusterResult`: `best`, `bic_values`, `icl_values` — confirmed present
- `SpmChart` fields: `t2_phase1`, `spe_phase1`, `t2_limit`, `spe_limit` — confirmed present
- `PaceFpcaResult`: `mean`, `eigenvalues`, `eigenfunctions`, `scores`, `fitted`, `fitted_lower`, `fitted_upper`, `argvals`, `sigma2`, `ncomp` — confirmed present

No rename, no removal.

**Enums:** `GlmFamily` (used in `regression_mod.rs:1120`) and `ProjectionBasisType` (used in `inference_mod.rs:555`) retain their existing variants in 0.33.0. The wildcard fallback arms already present in both files remain sufficient. `CvCriterion` (used in `smoothing_mod.rs`) is unchanged.

**Action for Phase 1 (isolated bump):** Bump `fdars-core = "0.23.0"` to `"0.33.0"` in `Cargo.toml`, run `cargo build` plus full test suite. Expected: green with deprecation warnings for the four 2D depth functions. Zero test changes needed. The deprecation warnings are a known pre-existing risk, not a blocker.

---

## 2. New Capabilities: Integration Patterns

### 2a. Modules new in 0.24 → 0.33 not yet bound in pyfda

Comparison of 0.23.0 module list (confirmed from docs.rs) against 0.33.0:

| New module | First appeared | What it provides | Binding priority |
|------------|---------------|-----------------|-----------------|
| `multi_fdata` | 0.27 | `MultiFunData` + `FdComponent` — multi-domain functional data container | HIGH — new input type needed by MFPCA, FAMM |
| `fts` | 0.27 | Functional time series: FTSM forecast, DPCA, ACF/PACF, stationarity test, long-run covariance | HIGH — new submodule, advisor-relevant |
| `frechet` | 0.27 | Frechet mean/variance/regression/ANOVA over metric-space backends | MEDIUM — new submodule |
| `density_fda` | ~0.27 | LQD transform, LQD-FPCA, Wasserstein barycenter for density-valued curves | MEDIUM |
| `pda` | 0.27 | Principal differential analysis — `Lfd`, `PdaResult`, `principal_differential_analysis` | MEDIUM |
| `fpca_variants` | 0.27 | Derivative FPCA, functional SVD, cross-covariance, dynamical correlation, SSVD | MEDIUM |
| `famm` | 0.24 | Functional additive/mixed models — `fmm`, `dense_flmm`, `fast_fmm`, `multi_famm` | MEDIUM |
| `fof_regression` | 0.24 | Function-on-function regression — `fof_regression`, `fof_re_regression`, predict | HIGH — closes a visible gap |
| `clustering_advanced` | 0.24 | DBSCAN, funFEM, kCFC, align-cluster — extends `fdars.clustering` | MEDIUM |
| `fem_smoothing` | ~0.29 | FEM/PDE surface smoothing for 2D domains — `fem_smooth`, `fem_smooth_gcv` | LOW — specialised |
| `shapelet` | 0.33 | Shapelet discovery, transform, classifier | MEDIUM |

Modules already bound in 0.23 that gained new functions (additive, no signature changes):
- `spm`: adds `mf_spm_phase1`/`mf_spm_monitor`, `spm_amewma_monitor`, `frcc_phase1`/`frcc_monitor`, `profile_phase1`/`profile_monitor`, partial monitoring, `hotelling_t2_regularized`, ARL metrics. The existing `spm_mod.rs` can be extended without restructuring.
- `scalar_on_function`: adds FAM, GKAM, GSAM, group-lasso variable selection, bootstrap CI, `history_index`, `fregre_l1`, `fregre_huber`, `model_selection_ncomp`. Extends `regression_mod.rs`.
- `clustering` / `gmm`: adds `funhddC_cluster` in `gmm` module. Extends `clustering_mod.rs`.
- `smooth_basis`: adds `smooth_monotone`, `smooth_positive`, `FdPar`. Extends `smoothing_mod.rs`.
- `alignment`: adds `karcher_median`, `robust_karcher_mean`, `bayesian_align_pair`, `hierarchical_from_distances`, `kmedoids_from_distances`, `shape_confidence_interval`, `peak_persistence`, `phase_boxplot`. Extends `alignment_mod.rs`.

### 2b. Which new capabilities need `#[pyclass]` opaque handles

The precedent is `PyIrregFdata` in `src/pace_fpca_mod.rs`: use a `#[pyclass]` when the Rust type is a non-trivial struct that Python needs to hold across calls (by-reference semantics) and cannot be transparently serialised to a dict.

| Capability | Needs `#[pyclass]`? | Rationale |
|-----------|--------------------|-----------| 
| `MultiFunData` | YES — new `PyMultiFunData` | Multi-domain container with per-component grids; too complex for a ragged dict; Python needs to construct once and pass to MFPCA/FAMM/SPM-MF functions. Mirror the `PyIrregFdata` pattern exactly: builder `multifdata_from_components(data_list, argvals_list)` plus `#[pyclass(name="PyMultiFunData")]` wrapper. |
| `ShapeletClassifierFit` / `ShapeletTransformFit` | YES — new `PyShapeletFit` | Fitted shapelet state that must be passed to `shapelet_transform`/classify. Stateful handle like a trained model; should not be forced through a PyDict. |
| `FtsmResult` | NO — use PyDict | All fields are `FdMatrix`/`Vec<f64>` — serialisable. Use a 10-key PyDict. No `#[pyclass]` needed. |
| All other new result types | NO — use PyDict converters | `FtsStationarityResult`, `LongRunCovResult`, `SpectralDensityResult`, `FrechetGlobalRegResult`, `LqdFpcaResult`, `FofResult`, `FemSmoothResult`, etc. all return arrays plus scalars; follow the `itp_result_to_pydict`/`pace_fpca_result_to_pydict` pattern. |

### 2c. New `#[non_exhaustive]` enums requiring forward-compatible fallback arms

| Enum | Module | Status | Binding impact |
|------|--------|--------|---------------|
| `GlmFamily` | `scalar_on_function` | No new variants in 0.33 | Existing wildcard arm in `regression_mod.rs:1120` already correct |
| `ProjectionBasisType` | crate root | No new variants in 0.33 | Existing wildcard arm in `inference_mod.rs:555` already correct |
| `CvCriterion` | `smooth_basis` | No new variants in 0.33 | Existing wildcard arm already correct |
| `DepthMethod` | `depth` | May have new variants if new depth algorithms added | Wildcard arm in `depth_mod.rs` must remain; audit when binding |
| `QualityMeasure` | `shapelet` | New enum in 0.33: `InformationGain`, `FStatistic` | New shapelet binding needs a wildcard arm from day one |
| `ShapeletClassifier` | `shapelet` | New enum in 0.33: `Knn`, `Lda` | New shapelet binding needs a wildcard arm |
| `SpdMetric` | `frechet` | New enum in 0.27: Frobenius/Power/LogCholesky | New frechet binding must add wildcard arm |

---

## 3. New Input Types and `src/convert.rs` Extensions

### 3a. `MultiFunData` — the main new input type

`MultiFunData::new(Vec<FdComponent>)` takes components where each `FdComponent` holds an `FdMatrix` plus a `Vec<f64>` grid. The Python-side construction pattern mirrors `PyIrregFdata`:

```
# Python user:
comp_a = fdars.multi_fdata.component_from_array(data_a, argvals_a)
comp_b = fdars.multi_fdata.component_from_array(data_b, argvals_b)
mfd = fdars.multi_fdata.multifdata_from_components([comp_a, comp_b])
result = fdars.spm.mf_spm_phase1(mfd, ncomp=3)
```

Conversion path: each Python `data_i` (numpy 2D row-major) goes through `numpy2d_to_fdmatrix()` (existing) then into `FdComponent { data: mat, argvals: av }` then `Vec<FdComponent>` then `MultiFunData::new()`. No new conversion primitive needed in `src/convert.rs`. The builder function lives in a new `src/multi_fdata_mod.rs`.

### 3b. FEM 2D surface smoothing — irregular mesh input

`fem_smooth(x, y, z, triangles, lambda)` takes coordinate/value vectors handled by `numpy1d_to_vec` (existing), but `triangles` is an integer index matrix. Requires a new conversion: `numpy2d_i64_to_usize_vec` returning a flat `Vec<usize>` with row-major layout. Add to `src/convert.rs` — small addition, reusable.

### 3c. Frechet density responses

`frechet_global_reg(responses, predictors, space)` with `WassersteinDensitySpace` takes density curves as `Vec<Vec<f64>>`. The ragged-list extraction pattern already exists in `pace_fpca_mod.rs` as `extract_list_of_vecs`.

**Recommendation:** Factor `extract_list_of_vecs` from `src/pace_fpca_mod.rs` into `src/convert.rs` as a public helper `extract_ragged_vecs`. Then reuse in both PACE and Frechet density bindings. This is the only non-trivial `convert.rs` refactor in this upgrade.

### 3d. Shapelet discovery — no new conversions

`discover_shapelets(data, min_len, max_len, top_k, config)` takes dense 2D data via `PyReadonlyArray2<f64>` (standard) plus scalar parameters. No new conversion needed.

### 3e. Summary of `src/convert.rs` changes

| Change | Type | Priority |
|--------|------|----------|
| Factor `extract_list_of_vecs` into `extract_ragged_vecs` | Refactor (non-breaking) | MEDIUM — needed for frechet and avoids duplication |
| Add `numpy2d_i64_to_usize_vec` | New function | LOW — needed only for FEM mesh input |
| All other new bindings | None — use existing primitives | — |

---

## 4. Advisor Integration: Which New Capabilities Are Advisor-Relevant

The grounding invariant requires every diagnostic value to be computed by fdars (not the LLM). New capabilities slot into the advisor only when they produce scalar or bounded-vector outputs diagnosable with a crisp narrative.

### 4a. Strongly advisor-relevant (new aspect or major extension)

| Capability | Proposed advisor slot | Diagnostic scalars |
|------------|----------------------|-------------------|
| **Functional time series (`fts`)** | New aspect `"fts"` (#15) | AR order, explained variance ratio, lag-1 autocorrelation magnitude, stationarity p-value, forecast RMSE |
| **Function-on-function regression (`fof_regression`)** | Extend `"regression"` aspect or new sub-aspect | R-squared, RMSE, cross-validated RMSE from `FofCvResult`, ncomp for both predictor and response |
| **Frechet regression (`frechet`)** | New aspect `"frechet"` (#16) | Frechet R-squared, ANOVA p-value (where applicable) |
| **Shapelet classifier (`shapelet`)** | Extend `"classification"` aspect | Accuracy, top-K shapelet lengths, quality measure score |

### 4b. Moderately advisor-relevant (extend existing aspects)

| Capability | Existing aspect | Extension |
|------------|----------------|-----------|
| `spm` multivariate monitoring (`mf_spm_*`, `mfpca`) | `"spm"` | Add multivariate T2/SPE scalars; chart-in-control fraction; number of MF components |
| Advanced scalar-on-function (FAM, GKAM, variable selection) | `"regression"` | Selected-variables count, FAM component count, permutation test p-value |
| PDA (`principal_differential_analysis`) | `"fpca"` | Differential operator order; residual norm |
| Density FDA (`lqd_fpca`) | `"fpca"` | Extend with LQD variance-explained, reconstruction error |
| FPCA variants (`fpca_der`, `fsvd`) | `"fpca"` | Cross-covariance singular values, dynamical correlation |

### 4c. Not advisor-relevant (defer)

- `fem_smoothing` — surface fitting utility; no standard diagnostic scalar applies
- `clustering_advanced` (DBSCAN, funFEM, kCFC) — defer unless these become primary clustering methods
- `frechet` SPD/network/sphere metric-space backends — outputs are matrix-valued; no grounded scalar reduction obvious
- `density_fda` standalone transforms — utility functions, not fit results; `lqd_fpca` is the exception (diagnosable via `"fpca"` aspect)

### 4d. MCP `_DIAGNOSTICS_METHODS` guard-sync protocol

Adding new aspects (`"fts"`, `"frechet"`) requires a **single atomic commit** that simultaneously:
1. Adds the new `_build_fts_diagnostics` function in `python/fdars/advisor/aspects/fts.py`
2. Adds `"fts"` to `_DIAGNOSTICS_METHODS` in `python/fdars/mcp/server.py`
3. Adds the aspect primer in `_ASPECT_PRIMERS` in `python/fdars/advisor/_prompts.py`

Do NOT add new aspects to `_RUNNABLE_METHODS` without confirming the MCP dataset model can supply all required inputs at run time. `"fts"` requires time-ordered data — feasible (time ordering is implicit in row order of a registered dataset handle). `"frechet"` with density responses requires a different data registration protocol — defer `_RUNNABLE_METHODS` addition for `"frechet"` until that protocol is defined.

---

## 5. Recommended Build Order / Phase Grouping

This mirrors the v4.0/v5.0/v6.0 shape: isolated bump → binding groups (parallelisable) → advisor → docs.

### Phase 1 — Isolated Crate Bump (sequential, regression gate)

**Goal:** Bump `fdars-core 0.23.0 → 0.33.0` in `Cargo.toml`. Rebuild. Run all 772 baseline tests.

**Risk:** Deprecation warnings for four 2D depth functions (`fraiman_muniz_2d`, `modal_2d`, `random_projection_2d`, `random_tukey_2d`). Not a compile error; not a test failure. Record the warning count. Do NOT migrate them in this phase — keep the diff minimal.

**Gate:** All 772 tests pass / 0 failures. Only `Cargo.toml` and `Cargo.lock` change.

**Files touched:** `Cargo.toml` (one line bump), `Cargo.lock` (auto-updated).

### Phase 2 — Binding Groups (parallelisable after Phase 1 lands)

Split into independent groups by capability family. Each group produces a new or extended `src/*_mod.rs`, Python-layer wiring in `python/fdars/__init__.py`, and new tests.

**Group A — Functional Time Series (`fts`)** — highest user value, new submodule
- New file: `src/fts_mod.rs`
- Binds: `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `functional_acf`, `functional_pacf`, `stationarity_test`, `long_run_covariance`
- Result converters: `ftsm_result_to_pydict` (10-key dict), `facf_result_to_pydict`, `stationarity_result_to_pydict`
- No `#[pyclass]` needed (all results serialisable to dicts)
- Register in `lib.rs` as `"fts"`
- Can run in parallel with Groups B, D, E

**Group B — Function-on-Function Regression (`fof_regression`)** — closes a visible gap
- Extend: `src/regression_mod.rs` (add `fof_regression`, `fof_re_regression`, `fof_cv`, `predict_fof`)
- Result converters: `fof_result_to_pydict`, `fof_re_result_to_pydict`, `fof_cv_result_to_pydict`
- No new submodule; extends existing `fdars.regression` Python namespace
- Can run in parallel with Groups A, D, E

**Group C — Multi-domain Data + MFPCA + Advanced SPM** (sequential within group)
- New file: `src/multi_fdata_mod.rs` — `PyMultiFunData` `#[pyclass]` plus builder
- Extend: `src/spm_mod.rs` — add `mf_spm_phase1`, `mf_spm_monitor`, `mfpca` (uses `PyMultiFunData`)
- Register `multi_fdata` as a new submodule in `lib.rs`
- Python: add `fdars.multi_fdata` and extend `fdars.spm`
- Note: Groups C and F both touch `spm_mod.rs` — run C and F sequentially, not in parallel

**Group D — Frechet Regression + Density FDA** (can run in parallel with A/B/E)
- New file: `src/frechet_mod.rs`
- Binds: `frechet_mean`, `frechet_global_reg` (Wasserstein backend initially), `frechet_local_reg`, `frechet_anova`
- New file: `src/density_fda_mod.rs`
- Binds: `lqd_transform`, `inverse_lqd`, `lqd_fpca`, `wasserstein_barycenter`
- Factor `extract_list_of_vecs` from `pace_fpca_mod.rs` into `convert.rs` as `extract_ragged_vecs` (prerequisite within this group)

**Group E — Shapelet Classifier** (can run in parallel with A/B/D)
- New file: `src/shapelet_mod.rs`
- `PyShapeletFit` `#[pyclass]` for `ShapeletClassifierFit`
- Binds: `discover_shapelets`, `shapelet_transform_fit`, `shapelet_classifier_fit`, predict
- New enums: `QualityMeasure`, `ShapeletClassifier` — both need wildcard arms
- Register as `fdars.shapelet`

**Group F — Depth 2D deprecation migration + alignment/smoothing extensions** (sequential with C; lower priority)
- Update `src/depth_mod.rs`: migrate four deprecated 2D depth variants to unified Dim-parameterised calls
- Extend `src/alignment_mod.rs`: add `karcher_median`, `robust_karcher_mean`, `bayesian_align_pair`, `hierarchical_from_distances`, `kmedoids_from_distances`
- Extend `src/smoothing_mod.rs`: add `smooth_monotone`, `smooth_positive`
- Extend `src/clustering_mod.rs`: add `clustering_advanced` (DBSCAN, funFEM, kCFC, align-cluster) and `gmm::funhddC_cluster`
- This group can run after Phase 1; does not block Groups A/B/D/E

### Phase 3 — Advisor Extension (sequential, after all binding groups land)

- Add `"fts"` aspect (#15) in `python/fdars/advisor/aspects/fts.py`
- Add `"frechet"` aspect (#16) in `python/fdars/advisor/aspects/frechet.py`
- Extend `"regression"` aspect for `fof_regression` diagnostics
- Extend `"classification"` aspect for shapelet accuracy/top-K shapelet lengths
- Extend `"spm"` aspect for multivariate monitoring scalars
- Atomic MCP guard-sync commit for each new aspect (single commit: aspect file + `_DIAGNOSTICS_METHODS` + `_ASPECT_PRIMERS`)

### Phase 4 — Documentation (sequential, after advisor phase lands)

- New pages: `fts/`, `fof-regression/`, `frechet/`, `multi-fdata/`, `shapelet/`
- Method-accurate hand-authored inline SVG per new page
- Runnable offline `FDARS_FENCE_OK` worked examples per page
- Whole-site `mkdocs build --strict` green
- Blocking human diagram review before close

---

## 6. Component Boundary Summary

### Existing boundaries — unchanged role, extended content

| Component | File | Role in upgrade |
|-----------|------|----------------|
| Conversion layer | `src/convert.rs` | Add `extract_ragged_vecs` (factored from `pace_fpca_mod.rs`); add `numpy2d_i64_to_usize_vec` for FEM mesh indices |
| Module registry | `src/lib.rs` | Add `register_submodule!` calls for new modules: `fts`, `multi_fdata`, `frechet`, `density_fda`, `shapelet` |
| Fdata OOP container | `python/fdars/fdata_class.py` | Potentially add `.forecast()` method wrapping `ftsm` + `ftsm_forecast`; decide based on whether time-series fits the Fdata API contract |
| Advisor aspects | `python/fdars/advisor/aspects/` | New files: `fts.py`, `frechet.py`; extend `regression.py`, `classification.py`, `spm.py` |
| MCP guard | `python/fdars/mcp/server.py` | Atomic guard-sync for new aspects only |

### New boundaries introduced by this upgrade

| Component | File | What it does |
|-----------|------|-------------|
| `PyMultiFunData` opaque handle | `src/multi_fdata_mod.rs` | Multi-domain functional data container; builder `multifdata_from_components(data_list, argvals_list)` validates shapes and wraps `MultiFunData::new()` |
| `PyShapeletFit` opaque handle | `src/shapelet_mod.rs` | Fitted shapelet classifier/transform state; wraps `ShapeletClassifierFit` for cross-boundary persistence |
| `fdars.fts` submodule | `src/fts_mod.rs` + `python/fdars/__init__.py` | Functional time series: FTSM, forecast, ACF/PACF, stationarity |
| `fdars.multi_fdata` submodule | `src/multi_fdata_mod.rs` + `python/fdars/__init__.py` | Multi-domain data construction |
| `fdars.frechet` submodule | `src/frechet_mod.rs` + `python/fdars/__init__.py` | Frechet regression and ANOVA |
| `fdars.density_fda` submodule | `src/density_fda_mod.rs` + `python/fdars/__init__.py` | Density-valued functional data (LQD transform, Wasserstein barycenter) |
| `fdars.shapelet` submodule | `src/shapelet_mod.rs` + `python/fdars/__init__.py` | Shapelet discovery, transform, classification |

---

## 7. Architecture Anti-Patterns to Avoid

### Do not bypass `extract_ragged_vecs` for Frechet density inputs

The `extract_list_of_vecs` function in `pace_fpca_mod.rs` handles dtype-agnostic ragged list input with proper error messages. Factor it into `convert.rs` rather than re-implementing per module. Two implementations of the same ragged-list validation will drift.

### Do not add `MultiFunData` construction to `convert.rs`

`convert.rs` is for primitive type conversions (numpy ↔ FdMatrix, Vec ↔ numpy1d). Higher-level object construction belongs in the module file. The `multifdata_from_components` builder lives in `src/multi_fdata_mod.rs`, not `src/convert.rs`.

### Do not add `#[pyclass]` for `FtsmResult`

Unlike `PyIrregFdata` (which must be created once and passed to a compute function), `FtsmResult` is a pure output type. Convert it to a PyDict immediately — no cross-call persistence needed. The precedent is every other result type in pyfda.

### Do not register `multi_fdata` as an extension of `pace_fpca`

`PyMultiFunData` is a general multi-domain container used by MFPCA in SPM, FAMM, and potentially future modules. It must be its own registered submodule (`fdars.multi_fdata`), not nested under `fdars.pace_fpca`.

### Do not add new aspects to `_RUNNABLE_METHODS` without a dataset model

The `fdars_run_method` MCP tool requires constructing the full input from a pre-registered dataset handle. For `"fts"`, time-ordering is implicit in row order — a registered dataset handle is sufficient. For `"frechet"` with density-valued responses, do NOT add to `_RUNNABLE_METHODS` without first defining a dataset registration protocol for density responses.

### Do not run Groups C and F in parallel worktrees

Both groups extend `src/spm_mod.rs`. Run them sequentially (C first, then F) to avoid merge conflicts, as in the v6.0 sequential-on-main lesson.

---

## 8. Scalability and Build Considerations

| Concern | Impact | Mitigation |
|---------|--------|------------|
| Docs build time | Each new submodule adds ~1-2 min of fence execution; 5 new submodules adds ~10 min to the current ~22 min build | Keep fence datasets small (50 obs, 100 grid points); use `DOCS_FAST=1` during development |
| `linalg` feature flag | Still off at 0.33 (MSRV check needed at bump time); `fem_smoothing` and some `famm` functions may require `linalg` | If `linalg` needed for specific new functions, skip those in initial binding; defer to a later milestone when MSRV resolves |
| Parallel binding phases | Groups A/B/D/E can run in parallel worktrees after Phase 1 lands | Same pattern as v6.0 Groups A/B/C; do not share worktrees for groups that touch the same `*_mod.rs` |
| Test suite growth | From 772 tests; each new module should add ~20-40 tests | Target total ~900-1000 tests after all groups |
| Deprecation warnings at compile | Four `#[deprecated]` depth calls produce Rust warnings | These are expected from Phase 1 onward; suppressed or migrated in Group F |

---

## Sources

- `docs.rs/fdars-core/0.23.0` through `0.33.0` — module lists and public API, webfetch (LOW confidence; cross-checked across multiple versions for convergence)
- `crates.io/api/v1/crates/fdars-core/versions` — confirmed 0.23–0.33 version sequence, webfetch (LOW)
- `github.com/sipemu/fdars` release notes for v0.24, v0.27, v0.28, v0.29, v0.32, v0.33 — each confirms "additive and non-breaking", webfetch (LOW; convergent = MEDIUM confidence on no-breaking-changes verdict)
- `github.com/sipemu/fdars/blob/main/CHANGELOG.md` — explicit "additive and non-breaking" statement for 0.24–0.30; 0.30 deprecations confirmed, webfetch (LOW; convergent with release notes = MEDIUM)
- `src/convert.rs`, `src/lib.rs`, `src/pace_fpca_mod.rs`, `src/inference_mod.rs`, `src/regression_mod.rs`, `src/clustering_mod.rs`, `src/spm_mod.rs` — current pyfda binding patterns (direct file read, HIGH)
- `.planning/PROJECT.md` — milestone history, integration constraints, prior upgrade lessons (direct file read, HIGH)
- `.planning/codebase/ARCHITECTURE.md` — component responsibilities (direct file read, HIGH)
