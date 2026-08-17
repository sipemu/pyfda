# Requirements: pyfda — v5.0 fdars-core 0.20 Upgrade (Functional Inference + Depth/Boxplot + Basis/Smoothing)

**Defined:** 2026-08-17
**Core Value:** Expose fdars-core 0.20.0's new functional-inference + depth/boxplot + basis/smoothing surface through method-accurate PyO3 bindings, the grounded advisor, and provably-correct docs — the grounding invariant intact throughout.

## v1 Requirements

Requirements for milestone v5.0. Each maps to a roadmap phase. All 13 new bindings are in scope — this is a full-surface upgrade, not a partial launch. Signatures/field names verified against docs.rs/fdars-core/0.20.0 (see `.planning/research/`); five items flagged for plan-time verification (docs.rs 404s / cross-module questions).

### Crate Upgrade

- [x] **DEP-03**: `fdars-core` bumped 0.17.0 → 0.20.0 in `Cargo.toml` with `features = ["parallel"]` (do NOT enable `linalg` — needs Rust 1.84 > MSRV 1.83); `maturin develop` build green. (0.18 was never published; upgrade path is 0.17 → 0.20 directly.)
- [x] **DEP-04**: Regression gate — the existing `optim_bandwidth` binding compiles against 0.20.0's now-`#[non_exhaustive]` `CvCriterion` (add a wildcard `_ => PyValueError` fallback arm), and the full existing binding + advisor suite (~426 tests) passes unchanged as the sole success criterion. Isolated commit before any new binding work.

### Functional Inference (new `fdars.inference` submodule)

- [ ] **INFER-01**: User can run a two-sample integrated-L2 permutation t-test via `fdars.inference.t_perm_test(data_a, data_b, argvals, n_perm=999, seed=None)` and receive a dict `{statistic, p_value, n_perm}`.
- [ ] **INFER-02**: User can run a two-sample integrated-F permutation test via `fdars.inference.f_perm_test(...)` returning the same dict shape.
- [ ] **INFER-03**: User can run an asymptotic two-sample mean test (Hotelling T² on a shared FPC basis) via `fdars.inference.two_sample_mean_test(data_a, data_b, argvals, ncomp)` → dict (`n_perm=0`, seedless).
- [ ] **INFER-04**: User can compute a Degras simultaneous confidence band for the mean via `fdars.inference.mean_scb(...)` → dict of `{lower, upper, center, half_width}` 1-D arrays (`ToleranceBand`); `multiplier` selected by string with a `ValueError` fallback.
- [ ] **INFER-05**: User can run an SCB test for the mean-difference curve via `fdars.inference.scb_two_sample_test(...)` → dict (`TestResult`).
- [ ] **INFER-06**: User can run an overall-significance F-test on a fitted functional linear model via `fdars.inference.flm_f_test(...)` → dict; the wrapper re-fits `fregre_lm` internally (accepts raw data/response/n_comp — no persistent handle).
- [ ] **INFER-07**: User can run a Ramsey–RESET goodness-of-fit / lack-of-fit test on a fitted FLM via `fdars.inference.flm_gof_test(...)` → dict; bound symmetrically with INFER-06.
- [ ] **INFER-08**: User can run an asymptotic one-way functional ANOVA V-statistic via `fdars.inference.oneway_anova_vstat(data, groups, argvals)` → dict (`n_perm=0`); complements the existing permutation `fanova`.
- [ ] **INFER-09**: The `fdars.inference` submodule is registered (`src/inference_mod.rs` + `register_submodule!` in `lib.rs` + `_submodule_names`) and importable; all `u64` seeds are exposed as Python `seed=None` resolving to a fixed default for byte-identical reproducibility; degenerate inputs (mismatched grids, too few curves, invalid params) raise `ValueError` (no `.unwrap()`, all fallible fns via `to_pyresult()`).

### Depth & Functional Boxplot (extend `fdars.depth`)

- [ ] **DEPTH-01**: User can compute self-depth for a sample via `fdars.depth.functional_depth(data, method="fraiman_muniz"|"band"|"modified_band"|"random_projection", **kwargs)` → `ndarray (n,)`; `method` dispatches to a `DepthMethod` variant with a `#[non_exhaustive]` wildcard fallback.
- [ ] **DEPTH-02**: User can compute a López-Pintado–Romo functional boxplot via `fdars.depth.functional_boxplot(data, method=..., factor=1.5, **kwargs)` → dict `{median, central_lower, central_upper, whisker_lower, whisker_upper, outliers, depths}` (band fields as 1-D arrays via the numpy conversion helper with a round-trip shape test; `outliers` as a Python list of ints).

### Basis & Smoothing Quick Wins (extend `fdars.basis` / `fdars.smoothing`)

- [ ] **BASIS-01**: User can construct an all-ones intercept column via `fdars.basis.constant_basis(argvals)` → `ndarray` (exact signature/dimension confirmed at plan time).
- [ ] **BASIS-02**: User can select an AIC-optimal basis roughness penalty via `fdars.smoothing.smooth_basis_aic(...)` → dict, and pass `criterion="aic"` to `basis_nbasis_cv` (`BasisCriterion::Aic`, already confirmed present).
- [ ] **BASIS-03**: User can select an AIC-optimal kernel bandwidth via `aic_smoother` and/or `criterion="aic"` on the existing bandwidth-selection binding (`CvCriterion::Aic`).

### Advisor Extension

- [ ] **ADV-03**: The grounded advisor gains an `inference` diagnostics aspect that summarizes fdars-computed `TestResult` p-values/statistics (diagnostics-only, not in `_RUNNABLE_METHODS`); the `build_diagnostics` dispatch + `advisor` `_supported` set + MCP `_DIAGNOSTICS_METHODS` change in a single atomic commit (keeping `test_diagnostics_methods_match_advisor_supported` green); grounding invariant + offline determinism (no numpy scalars, byte-identical `json.dumps`) preserved. Exact scope (full aspect vs. folding into an existing aspect, plus optional functional-boxplot outlier diagnostics) confirmed at discuss/plan.

### Documentation

- [ ] **DOCS-04**: New functional-inference docs page(s) covering two-sample tests, SCB bands, and functional ANOVA — each with a method-accurate hand-authored inline SVG diagram and a runnable offline worked example emitting `FDARS_FENCE_OK` (small params: `n_perm=19`, SCB `nb=50`, small/synthetic data to protect the ~18-min build).
- [ ] **DOCS-05**: New functional-boxplot docs page — method-accurate hand-authored SVG (central region / whiskers / median / flagged outliers) + runnable offline worked example.
- [ ] **DOCS-06**: Basis/smoothing additions documented (constant_basis + AIC selection) with example(s); advisor `aspects.md` updated to reflect the new `inference` aspect.
- [ ] **DOCS-07**: All new pages wired into `mkdocs.yml` nav; whole-site `mkdocs build --strict` passes offline (exit 0); every new SVG is SVGO-idempotent and determinism-clean; blocking human diagram method-accuracy review.

## v2 / Future Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Plotting

- **PLOT-01**: `fdars.plot.plot_functional_boxplot()` helper rendering the `functional_boxplot` numeric result (central region band + whiskers + median + outliers). The numeric binding is the v5.0 deliverable; the plot helper is a convenience add-on.

### Accessibility / Editorial (carried from prior milestones)

- **A11Y-01**: Long-form `<title>`/`<desc>` + `aria-labelledby` for complex diagrams.
- **EX2-01**: Editorial consolidation of overlapping worked examples.

### Transport

- **HTTP-01 / FUT-01**: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| `linalg` feature flag | Requires Rust 1.84 > pyfda MSRV 1.83; pulls in faer/anofox-regression not needed for v5.0 targets |
| Plotting inside the `functional_boxplot` binding | Mixing compute + I/O in a Rust binding breaks the offline docs build; visualization belongs in `fdars.plot` (see PLOT-01) |
| Persistent `FregreLmResult` handle / pyclass | `FregreLmResult` is a non-pyclass Rust struct; FLM inference re-fits internally instead — avoids a handle registry |
| `MultiplierDistribution` as an integer enum | Opaque to users; use string dispatch with clear `ValueError` on unknown values |
| `*_with_config` API variants (`smooth_basis_gcv_with_config`, `basis_nbasis_cv_with_config`) | Config-struct duplicates the primary function with no Python benefit; bind only the primary functions |
| HTTP/SSE MCP transport | Still deferred; stdio only (tracked as HTTP-01/FUT-01) |
| R-parity feature work | Tracked separately in `PARITY_PLAN.md` |
| Re-exposing 0.15→0.20 internal performance wins | Inherited via the crate bump; no separate public API to bind |

## Traceability

Which phases cover which requirements. Populated during roadmap creation (Step 10).

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEP-03 | Phase 30 | Complete |
| DEP-04 | Phase 30 | Complete |
| INFER-01 | Phase 31 | Pending |
| INFER-02 | Phase 31 | Pending |
| INFER-03 | Phase 31 | Pending |
| INFER-04 | Phase 31 | Pending |
| INFER-05 | Phase 31 | Pending |
| INFER-06 | Phase 31 | Pending |
| INFER-07 | Phase 31 | Pending |
| INFER-08 | Phase 31 | Pending |
| INFER-09 | Phase 31 | Pending |
| DEPTH-01 | Phase 32 | Pending |
| DEPTH-02 | Phase 32 | Pending |
| BASIS-01 | Phase 33 | Pending |
| BASIS-02 | Phase 33 | Pending |
| BASIS-03 | Phase 33 | Pending |
| ADV-03 | Phase 34 | Pending |
| DOCS-04 | Phase 35 | Pending |
| DOCS-05 | Phase 35 | Pending |
| DOCS-06 | Phase 35 | Pending |
| DOCS-07 | Phase 35 | Pending |

**Coverage:**

- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0 ✓

### Plan-time verification spikes (from research — resolve before coding the affected binding)

- `MultiplierDistribution` enum variants (docs.rs 404) — before INFER-04/05.
- `flm_f_test`/`flm_gof_test` re-fit strategy + `fdars_core::scalar_on_function::FregreLmResult` cross-module import — before INFER-06/07.
- `constant_basis` exact signature/dimension (docs.rs 404) — before BASIS-01.
- `smooth_basis_aic` existence + `aic_smoother`/`CvCriterion::Aic` surface (docs.rs partial) — before BASIS-02/03.
- `DepthMethod` `#[non_exhaustive]` confirmation + `oneway_anova_vstat` group-label base (0- vs 1-indexed) — before DEPTH-01 / INFER-08.

---
*Requirements defined: 2026-08-17*
*Last updated: 2026-08-17 after roadmap creation — traceability filled (21/21 mapped to Phases 30–35)*
