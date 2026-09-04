# Requirements: pyfda — v11.0 fdars-core 0.33 Upgrade

**Defined:** 2026-09-02
**Core Value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API. (This upgrade milestone additionally holds: fdars computes every number; the advisor only interprets/cites — the grounding invariant.)

## v11.0 Requirements

Requirements for this milestone. Each maps to a roadmap phase (Phases 66+, continuing from v10.0's Phase 65).

### Crate Bump & Regression Gate

- [x] **DEP-01**: `fdars-core` pinned at `0.33.0` (from `0.23.0`) with the `parallel` feature only (no `linalg`); `Cargo.toml` + `Cargo.lock` updated; maturin `develop` build green
- [x] **DEP-02**: The full existing Python suite (~772 tests) passes against the bumped crate with zero new failures; any numeric-tolerance change is documented; MSRV 1.83 unchanged
- [x] **DEP-03**: A 0.24→0.33 changelog + API audit is recorded — every existing `match`-arm/enum-variant string in `src/*_mod.rs` is verified to still exist at 0.33, and the four 0.30-deprecated 2D depth functions are noted for migration

### Functional Time Series (`fdars.fts`)

- [x] **FTS-01**: New `fdars.fts` submodule registered and importable; `ftsm` model fit + `ftsm_forecast` / multistep forecasting exposed with a PyDict result (transposition-guarded on non-square input)
- [x] **FTS-02**: Time-series diagnostics exposed — `functional_acf` / `functional_pacf`, `stationarity_test`, `long_run_covariance` — with deterministic seeds where the upstream function takes one
- [x] **FTS-03**: Dimension-reduction/forecasting extras exposed as available at 0.33 — `fplsr` and/or `dpca` (functional PLS regression / dynamic PCA) — each returning a documented PyDict

### Regression — Function-on-Function & Scalar-on-Function (`fdars.regression`, `fdars.scalar_on_function`)

- [x] **REG-01**: Function-on-function regression bound — `fof_regression` (+ `predict`) extending `fdars.regression`, returning a `beta`-surface/result PyDict; transposition- and `argvals`-guarded
- [x] **REG-02**: Function-on-function random-effects regression bound — `fof_re_regression` (+ `predict_fof_re`) with subject-id validation
- [x] **REG-03**: Scalar-on-function extensions bound — additive/generalized models (`fam`, `fregre_gkam`, `fregre_gsam`) and variable/model selection (`variable_selection`, `model_selection_ncomp`) extending `fdars.scalar_on_function`

### Fréchet Regression & Density FDA (`fdars.frechet`, `fdars.density_fda`)

- [x] **FRE-01**: New `fdars.frechet` submodule — `frechet_mean`, `frechet_global_reg`, `frechet_local_reg`, `frechet_anova` exposed (metric-space backend chosen via string dispatch, `Err` fallback arm), each returning a documented PyDict
- [x] **FRE-02**: New `fdars.density_fda` submodule — `lqd_transform` / `inverse_lqd`, `lqd_fpca`, `wasserstein_barycenter`, `normalize_density` exposed
- [x] **FRE-03**: A shared ragged-list input helper (`extract_ragged_vecs`) is factored into `src/convert.rs` (out of `pace_fpca_mod.rs`) and used by the density/Fréchet inputs; validated on non-uniform per-observation lengths

### Multi-Domain Data, FAMM & Advanced Clustering (`fdars.multi_fdata`, `fdars.famm`, `fdars.clustering`)

- [x] **MULTI-01**: New `PyMultiFunData` opaque `#[pyclass]` handle (mirroring `PyIrregFdata`) + a builder from component curves; registered and constructible from Python
- [x] **MULTI-02**: Mixed-model bindings exposed — `dense_flmm`, `fast_fmm`, `multi_famm` — consuming `PyMultiFunData` where required, returning documented PyDicts
- [x] **MULTI-03**: Multivariate/multi-domain SPM bindings exposed extending `fdars.spm` (e.g. MFPCA / multi-domain monitoring), sequenced after `PyMultiFunData` within the phase
- [x] **MULTI-04**: Advanced clustering bound — `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd` — each returning a labels/result PyDict, transposition-guarded

### Shapelets & GAK Metric (`fdars.shapelet`, `fdars.metric`)

- [x] **SHAPE-01**: New `fdars.shapelet` submodule — `discover_shapelets`, `shapelet_transform_fit` / `shapelet_transform`, `shapelet_classifier_fit`, `shapelet_distance` — with a `PyShapeletFit` opaque handle and the two new enums (`QualityMeasure`, `ShapeletClassifier`) dispatched by string with an `Err` fallback arm
- [ ] **SHAPE-02**: Global-Alignment-Kernel metric bound extending `fdars.metric` — `gak`, `gak_gram_matrix`, `gak_gram_train` / `gak_gram_predict`, `sigma_gak` — Gram output usable as a precomputed kernel

### Advisor Extension (grounding invariant preserved)

- [ ] **ADV-01**: New/extended advisor aspects for the bound capabilities — at least an `fts` aspect and a `frechet` aspect (diagnostics-only), plus extension of existing `regression`/`classification`/`spm` aspects for the new methods — every diagnostic a real fdars-computed native `float`/`int` scalar (no Python-derived or numpy scalars)
- [ ] **ADV-02**: MCP `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` guard-sync stays consistent — updated atomically with each aspect (single commit); `test_guard_sync_version_independent.py` and a per-aspect `json.dumps(build_diagnostics(...))` serialization test pass; MCP compute path stays provably LLM-free

### Documentation

- [ ] **DOCS-01**: One dedicated method-accurate page per new capability family (fts, fof/sof-regression, frechet, density-fda, multi-domain/FAMM, clustering, shapelet) wired into `mkdocs.yml` nav, each with a runnable offline worked example emitting `FDARS_FENCE_OK`
- [ ] **DOCS-02**: One hand-authored, STYLE_SPEC-conformant, SVGO-idempotent inline SVG concept diagram per new family, method-accurate against the shipped binding
- [ ] **DOCS-03**: Advisor `aspects.md` updated for the new/extended aspects; whole-site `mkdocs build --strict` green offline; blocking human diagram method-accuracy review approved before close

### Release

- [ ] **REL-01**: Package version bumped `0.9.0 → 0.10.0` in `Cargo.toml` + `pyproject.toml` at close; semver tag `v0.10.0` (triggers PyPI publish) — decided/applied at milestone close

## Future Requirements

Deferred to a later milestone. Tracked but not in this roadmap.

### Deferred fdars-core 0.33 capabilities

- **FEM-01**: FEM smoothing (`fem_smooth`, `fem_smooth_gcv`, `fem_predict`) — deferred; needs a new mesh/triangle-index conversion path (i64→usize) unlike any current binding
- **PDA-01**: Principal differential analysis (`principal_differential_analysis`) — specialized ODE estimation; deferred
- **FRE-RUN-01**: Promote the `frechet` advisor aspect from diagnostics-only to `_RUNNABLE_METHODS` once a density/metric-space dataset registration protocol is designed
- **LINALG-01**: Enable the `linalg` feature + bind its surface (e.g. `ridge_regression_fit`) — now MSRV-unblocked at 0.33 (faer ^0.23 MSRV 1.81), but explicitly out of scope this milestone

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Enabling `linalg` this milestone | User decision: stay `parallel`-only (parity with every prior wave); no v11.0 capability needs it |
| FEM smoothing / PDA bindings | Deferred (see Future) — non-standard input shape / niche; not in the four selected binding groups |
| PyO3 / numpy / maturin version bumps | Research confirms the 0.33 bump forces none; keep the toolchain fixed |
| Programmatic/tool-generated diagrams | Standing constraint — diagrams stay hand-authored inline SVG |
| Dark-mode / palette / typography re-theme of SVGs | Standing deferral (DIAG-FUT-01b / DIAG-FUT-03) |
| HTTP/SSE MCP transport | Standing deferral (HTTP-01) — stdio only |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEP-01 | Phase 66 | Complete |
| DEP-02 | Phase 66 | Complete |
| DEP-03 | Phase 66 | Complete |
| FTS-01 | Phase 67 | Complete |
| FTS-02 | Phase 67 | Complete |
| FTS-03 | Phase 67 | Complete |
| REG-01 | Phase 68 | Complete |
| REG-02 | Phase 68 | Complete |
| REG-03 | Phase 68 | Complete |
| FRE-01 | Phase 69 | Complete |
| FRE-02 | Phase 69 | Complete |
| FRE-03 | Phase 69 | Complete |
| MULTI-01 | Phase 70 | Complete |
| MULTI-02 | Phase 70 | Complete |
| MULTI-03 | Phase 70 | Complete |
| MULTI-04 | Phase 70 | Complete |
| SHAPE-01 | Phase 71 | Complete |
| SHAPE-02 | Phase 71 | Pending |
| ADV-01 | Phase 72 | Pending |
| ADV-02 | Phase 72 | Pending |
| DOCS-01 | Phase 73 | Pending |
| DOCS-02 | Phase 73 | Pending |
| DOCS-03 | Phase 73 | Pending |
| REL-01 | Phase 73 | Pending |

**Coverage:**

- v11.0 requirements: 24 total
- Mapped to phases: 24 ✓
- Unmapped: 0

---
*Requirements defined: 2026-09-02*
*Last updated: 2026-09-02 — traceability populated by roadmap (Phases 66–73; all 24 mapped, 0 unmapped)*
