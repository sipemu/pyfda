# Requirements — Milestone v4.0: fdars-core 0.17 Upgrade (New Bindings, Advisor & Docs)

**Milestone goal:** Upgrade the pinned `fdars-core` from 0.14.0 to 0.17.0, expose the new upstream functional-data capabilities through PyO3 bindings + the Python API, extend the v3.0 AI advisor to cover the relevant new capabilities, and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples).

**Scope decisions (locked at milestone start):** all three binding groups (interpolation/representation, functional statistics/scoring, alignment/registration); full project-standard docs treatment (new diagrams **and** worked examples); advisor extended where relevant. Upstream 0.15→0.17 is additive/non-breaking. Research: `.planning/research/SUMMARY.md`.

---

## v4.0 Requirements

### Dependency & Regression (DEP)

- [x] **DEP-01**: `fdars-core` bumped 0.14.0 → 0.17.0 in `Cargo.toml`; `Cargo.lock` regenerated and committed; `parallel` feature retained; `linalg` feature NOT enabled (requires Rust 1.84 > pyfda MSRV 1.83).
- [x] **DEP-02**: The full existing binding + advisor test suite passes against 0.17.0, with FPCA-related tolerances relaxed to absorb the faer SVD numeric drift (results equivalent within `1e-8·σ₁`).

### Interpolation & Representation (REPR)

- [x] **REPR-01**: User can spline-interpolate functional data onto arbitrary off-grid query points (`spline_interpolate` and `spline_interpolate_with_policy`).
- [x] **REPR-02**: User can select an `ExtrapolationPolicy` (Boundary / Exception / Fill(value) / Periodic) for out-of-domain queries via the interpolation bindings (`fdata_interpolate_with_policy` / `spline_interpolate_with_policy`), passed as a string with a forward-compatible fallback arm.
- [x] **REPR-03**: User can impute missing values on a regular grid (`impute_missing_values` with `ImputationMethod` Linear / Mean / Constant); interpolation and imputation are exposed as `Fdata` methods (`fd.interpolate()`, `fd.impute()`).

### Functional Statistics & Scoring (STAT)

- [x] **STAT-01**: User can compute `functional_variance`, `functional_std`, and `functional_covariance`; matrix-returning results are verified layout-correct with a multi-curve round-trip test (guards the column-major #33 bug class).
- [x] **STAT-02**: User can compute `depth_based_median` (binding resolves the returned index to the actual median curve) and `trim_mean`.
- [x] **STAT-03**: User can score functional predictions with `functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, and `functional_explained_variance`; fallible inputs (MAPE near-zero truths, MSLE values ≤ −1) surface as `ValueError`.

### Alignment & Registration (ALGN)

- [x] **ALGN-01**: User can run least-squares shift registration (`least_squares_shift_registration`), receiving the registered curves and per-curve shifts (`ShiftRegistrationResult` marshalled as a dict).
- [x] **ALGN-02**: User can score registration quality with `least_squares_score`, `pairwise_correlation_score`, and `sobolev_least_squares_score` (Sobolev requires a uniform grid; surfaced clearly).
- [x] **ALGN-03**: User can run banded elastic alignment (`karcher_mean_with_band`, `elastic_self_distance_matrix_with_band`, `elastic_cross_distance_matrix_with_band`) with an optional `band_frac` (`None` = unbanded).

### Advisor Extension (ADV)

- [x] **ADV-01**: `scoring` is added as a diagnostics method wired simultaneously into `build_diagnostics`, the advisor `_supported` set, and the MCP `_DIAGNOSTICS_METHODS` guard — in a single atomic commit so `test_diagnostics_methods_match_advisor_supported` stays green (`_RUNNABLE_METHODS` unchanged).
- [ ] **ADV-02**: Imputation-quality diagnostics extend the `represent` aspect and registration-quality diagnostics extend the `alignment` aspect; every new diagnostic is fdars-computed and cites a real number (grounding invariant preserved; offline determinism tests added).

### Docs — Diagrams & Worked Examples (DOCS)

- [ ] **DOCS-01**: New/updated hand-authored inline SVG concept diagrams for the new methods across `represent/`, `analyze/`, and `align/`, each method-accurate and passing the SVGO idempotence + build-determinism gates.
- [ ] **DOCS-02**: Runnable offline worked examples for the new capabilities against existing `docs/data/` datasets; executed `markdown-exec` fences stay network-free/deterministic and emit the `FDARS_FENCE_OK` sentinel.
- [ ] **DOCS-03**: The AI Advisor docs section is updated for the new scoring / registration-quality / imputation coverage; full `mkdocs build --strict` passes offline.

---

## Future Requirements (deferred)

- Exposing the 0.15→0.17 internal performance paths as separate API — inherited via the crate bump; no public API to bind.
- HTTP/SSE MCP transport (HTTP-01 / FUT-01) — still deferred; stdio only.
- Additional 0.14.0-era upstream methods not covered by this milestone's three groups (e.g. Bayesian/closed-curve/partial-match alignment, GP/covariance kernels) — candidate for a later coverage milestone.

## Out of Scope

- Programmatic/tool-generated diagrams — diagrams stay hand-authored inline SVG.
- Dark-mode / SVG theming rework.
- Enabling the `linalg` feature / raising pyfda MSRV to 1.84 — deferred until a separate MSRV decision.
- R-parity feature work — tracked separately (`PARITY_PLAN.md`).

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEP-01 | Phase 25 | Complete |
| DEP-02 | Phase 25 | Complete |
| REPR-01 | Phase 26 | Complete |
| REPR-02 | Phase 26 | Complete |
| REPR-03 | Phase 26 | Complete |
| STAT-01 | Phase 26 | Complete |
| STAT-02 | Phase 26 | Complete |
| STAT-03 | Phase 27 | Complete |
| ALGN-01 | Phase 27 | Complete |
| ALGN-02 | Phase 27 | Complete |
| ALGN-03 | Phase 27 | Complete |
| ADV-01 | Phase 28 | Complete |
| ADV-02 | Phase 28 | Pending |
| DOCS-01 | Phase 29 | Pending |
| DOCS-02 | Phase 29 | Pending |
| DOCS-03 | Phase 29 | Pending |

*Traceability filled in by the roadmapper (`ROADMAP.md`). Coverage: 16/16 v4.0 requirements mapped, each to exactly one phase.*
