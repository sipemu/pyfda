# Requirements — Milestone v6.0: fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference

**Source:** milestone goals (2026-08-20) + `.planning/research/SUMMARY.md` (fdars-core v0.23.0 tag research, HIGH confidence).

**Shape:** same as v4.0/v5.0 — crate bump (isolated regression gate) → three parallel binding groups → advisor extension → docs. All signatures below were read directly from the `v0.23.0` git tag of the local `fdars-core` checkout; exact field names/params re-confirmed at plan time.

Prior-milestone requirements: see `.planning/milestones/v5.0-REQUIREMENTS.md` (and earlier). REQ-ID numbering continues across milestones.

## v6.0 Requirements

### Crate Upgrade

- [x] **DEP-05**: `fdars-core` bumped 0.20.0 → 0.23.0 in `Cargo.toml` with `features = ["parallel"]` (do NOT enable `linalg` — still gates only `ridge_regression_fit` and still wants Rust 1.84+; MSRV verified 1.81 ≤ pyfda 1.83); `maturin develop` build green. Bump is dependency-additive (single-field `Cargo.toml` diff upstream).
- [x] **DEP-06**: Regression gate — the full existing binding + advisor suite (~560 tests) passes unchanged as the sole success criterion, with any new `#[non_exhaustive]` upstream enums reached by existing code given wildcard fallback arms. Isolated commit before any new binding work.

### Group A — Regression (extend `fdars.regression`)

- [x] **REGR-01**: User can fit a concurrent (varying-coefficient) functional regression via `fdars.regression.concurrent_regression(predictors, response, argvals, ...)` — `predictors` a `list[np.ndarray]` (slice-of-matrices) — receiving a dict from `ConcurrentRegrResult`; the `beta_curve` field is shaped `(p, m)` (predictors × grid, NOT `(n_obs, m)`) and is round-tripped correctly, verified by a multi-predictor (`p ≥ 2`) transposition guard test.
- [x] **REGR-02**: User can fit an exponential-family functional GLM over FPC scores via `fdars.regression.functional_glm(data, response, argvals, family=..., n_comp=..., ...)` → dict (`FunctionalGlmResult`, all fields exposed); `family` dispatches a `#[non_exhaustive]` `GlmFamily` (Binomial/Poisson/Gamma/Gaussian) via string with a `ValueError` wildcard fallback; the wrapper re-fits FPCA internally (raw data in, no persistent handle). Gamma's inverse canonical link (1/μ) and the non-R-comparable AIC magnitude are documented.
- [x] **REGR-03**: Both functions are registered in `src/regression_mod.rs` + `register_submodule!`, with a `ConcurrentRegrResult`/`FunctionalGlmResult` → PyDict converter each; all fallible paths go through `to_pyresult()` (no `.unwrap()`); degenerate inputs (mismatched grids, too few curves, invalid family/ncomp) raise `ValueError`.

### Group B — FPCA & Classification

- [x] **PACE-01**: A new sparse/irregular functional-data input path is exposed — `fdars` gains an `IrregFdata` builder (e.g. `fdars.irreg_fdata_from_lists(argvals_list, values_list)`) accepting two Python lists of 1-D arrays (ragged per-curve grids) and constructing the fdars-core CSR-layout `IrregFdata`; passing a plain dense 2-D array is rejected with a `ValueError` (not silently misinterpreted). Exact interface confirmed by a plan-time spike (no existing PyO3 precedent in pyfda).
- [x] **PACE-02**: User can run PACE sparse/irregular FPCA via `fdars.pace_fpca(irreg_fdata, config...)` → dict (`PaceFpcaResult`, all 10 fields incl. eigenfunctions `(m, ncomp)`, scores `(n, ncomp)`, and per-curve confidence bands) with a `PaceFpcaConfig` (NOT `#[non_exhaustive]` — struct-literal safe); `eigenfunctions`/`scores` layout is transposition-guarded; `actual_ncomp` truncation handled. Lives in the new `src/pace_fpca_mod.rs`.
- [x] **CLASS-01**: User can fit a K-class one-vs-rest elastic multinomial classifier via `fdars.classification.elastic_multinomial(data, labels, argvals, ...)` → dict (`ElasticMultinomialResult`; `train_probabilities` `(n, K)` transposition-guarded at `K ≥ 3`); labels must be 0-indexed contiguous (`0..K`) — a negative/non-contiguous-label guard (v5.0 CR-01 pattern) raises a helpful `ValueError` rather than wrapping `i64→usize`.

### Group C — Depth / Outliers / Interval Inference (extend `fdars.depth` / `fdars.outliers` / `fdars.inference`)

- [ ] **DEPTH-03**: `fdars.depth.functional_depth(..., method=...)` gains the 9 new fdars-core 0.23 `DepthMethod` variants — `hypograph_index`, `modified_hypograph_index`, `epigraph_index`, `half_region`, `modified_half_region`, `extremal`, `extreme_rank_length`, `l_infinity`, `total_variation` (13 methods total). The Python string map covers every new variant and the `#[non_exhaustive]` wildcard error message lists all supported methods; `functional_boxplot`'s `method` param accepts them too.
- [ ] **OUTL-01**: User can detect magnitude/shape outliers via `fdars.outliers.tvdmss(data, argvals, ...)` → dict (outlier indices as a Python `list[int]`, plus fdars-computed scores/threshold).
- [ ] **OUTL-02**: User can run the MUOD (massive unsupervised outlier detection) detector via `fdars.outliers.muod(data, argvals, ...)` → dict (amplitude/magnitude/shape index sets + scores).
- [ ] **OUTL-03**: User can run the sequential-transform outlier detector via `fdars.outliers.sequential_transform_outliers(data, argvals, transforms=[...], ...)` → dict; the `transforms` sequence maps to `#[non_exhaustive]` `SeqTransform` variants via string with a `ValueError` wildcard fallback.
- [ ] **OUTL-04**: User can compute a depthgram / depthgram-based outlier detection via `fdars.outliers.depthgram(data, argvals, ...)` → dict (the two depth indices + flagged outliers). All four detectors: any permutation/random component takes a `seed` exposed as `seed=None` → fixed default for byte-identical offline reproducibility (plan-time audit of `outliers_mod.rs` for existing seed params); registered with `to_pyresult()` guards; degenerate inputs raise `ValueError`.
- [ ] **ITP-01**: User can run a one-population interval-wise test via `fdars.inference.itp_one_pop(data, argvals, mu0=..., ...)` → dict (`ItpResult`), returning **vector** closure-adjusted p-values (`adjusted_pvalues`) + unadjusted p-values + the test statistic curve.
- [ ] **ITP-02**: User can run a two-population interval-wise test via `fdars.inference.itp_two_pop(data_a, data_b, argvals, ...)` → dict (`ItpResult`); permutation `seed` exposed as `seed=None` → fixed default.
- [ ] **ITP-03**: User can run an interval-wise FLM test via `fdars.inference.itp_flm(data, response, argvals, ...)` → dict (`ItpResult`); `basis_type` maps a `#[non_exhaustive]` `ProjectionBasisType` via string with a `ValueError` wildcard fallback; re-fits internally (no persistent handle).
- [ ] **ITP-04**: The three ITP functions are registered in `src/inference_mod.rs` + `register_submodule!` via a **new** `itp_result_to_pydict` helper (distinct from `test_result_to_pydict`, since results are p-value vectors not scalars); vectors are exposed as 1-D arrays; all fallible paths via `to_pyresult()`; degenerate inputs raise `ValueError`.

### Advisor Extension (grounding invariant preserved)

- [ ] **ADV-04**: The grounded advisor's **existing `outliers` aspect** is extended to summarize the new fdars-computed outlier-detector results as grounded scalar diagnostics (e.g. `n_outliers`, outlier fraction, score/threshold ranges — never raw index lists or numpy aggregates), closing the v5.0 Phase-34 functional-boxplot-outlier deferral. No new aspect key is added; the `build_diagnostics` dispatch detects the new result-dict keys. `_DIAGNOSTICS_METHODS`/`_RUNNABLE_METHODS` unchanged (or, if touched, changed in a single atomic commit keeping `test_diagnostics_methods_match_advisor_supported` green); offline determinism (no numpy scalars, byte-identical `json.dumps`) preserved.
- [ ] **ADV-05**: The advisor's existing `regression` aspect surfaces grounded diagnostics for the new regression results (`functional_glm` deviance/AIC, `concurrent_regression` fit summary) where a real fdars-computed scalar is available; grounding invariant preserved. Advisor coverage of the Group B capabilities (`pace_fpca` via the `fpca` aspect, `elastic_multinomial` via the `classification` aspect) is **decided at plan time** on feasibility — included only if a genuinely grounded scalar diagnostic exists, otherwise left as bindings + docs only.

### Documentation

- [ ] **DOCS-08**: New/updated Regression docs covering `concurrent_regression` + `functional_glm` — method-accurate hand-authored inline SVG(s) + a runnable offline worked example emitting `FDARS_FENCE_OK` (small/synthetic or subsampled data to protect the build); documents the Gamma inverse link + AIC caveat.
- [ ] **DOCS-09**: New FPCA/Classification docs — a PACE-FPCA page (method-accurate SVG showing irregular/sparse observations + recovered eigenfunctions; executed fence using **small inline synthetic sparse data**, n ≤ 20) and elastic-multinomial coverage (phoneme.csv subsampled to 3 classes, m ≤ 64 for fence speed).
- [ ] **DOCS-10**: New/updated Depth-Outliers-Inference docs — the 9 new depth methods folded into the depth page, a functional-outliers page for the 4 detectors (method-accurate SVG), and an interval-wise-inference page for `itp_*` (SVG showing closure-adjusted p-value intervals; correct closure direction); each new page carries a runnable offline `FDARS_FENCE_OK` worked example.
- [ ] **DOCS-11**: Advisor `aspects.md` updated for the extended `outliers`/`regression` diagnostics; all new pages wired into `mkdocs.yml` nav; whole-site `mkdocs build --strict` passes offline (exit 0); every new SVG is SVGO-idempotent and determinism-clean; blocking human diagram method-accuracy review (rsvg-convert PNG check: depth asymmetry, PACE irregular observations, ITP closure direction).

## Future Requirements (deferred)

- **PLOT-01** (carried): `fdars.plot.plot_functional_boxplot()` helper rendering the v5.0 `functional_boxplot` numeric result (central region + whiskers + median + outliers). Numeric binding shipped in v5.0; plot helper still a convenience add-on.
- **HTTP-01 / FUT-01** (carried): HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0).
- **PACE-ADV / MULTINOM-ADV**: dedicated advisor aspects for PACE-FPCA and elastic multinomial, if ADV-05's plan-time feasibility check defers them.

## Out of Scope

- `linalg`-gated capabilities (`ridge_regression_fit`) — feature stays off (Rust 1.84+ > MSRV 1.83).
- fdars-core HEAD 0.24-bound work (FAM / functional additive models, denseFLMM/multiFAMM/fastFMM mixed models, FoF-RE regression) — not part of the published 0.23.0 crate; out of this milestone.
- Programmatic/tool-generated diagrams — diagrams stay hand-authored inline SVG (project constraint).
- New Python extras / new dataset files / CI-matrix changes — research confirmed none are needed.
- Dark-mode / theming rework of SVGs.

## Traceability

REQ-ID → Phase mapping. 23/23 v6.0 requirements mapped, each to exactly one phase — 100% coverage, no orphans, no duplicates.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEP-05 | Phase 36 | Complete |
| DEP-06 | Phase 36 | Complete |
| REGR-01 | Phase 37 | Complete |
| REGR-02 | Phase 37 | Complete |
| REGR-03 | Phase 37 | Complete |
| PACE-01 | Phase 38 | Complete |
| PACE-02 | Phase 38 | Complete |
| CLASS-01 | Phase 38 | Complete |
| DEPTH-03 | Phase 39 | Pending |
| OUTL-01 | Phase 39 | Pending |
| OUTL-02 | Phase 39 | Pending |
| OUTL-03 | Phase 39 | Pending |
| OUTL-04 | Phase 39 | Pending |
| ITP-01 | Phase 39 | Pending |
| ITP-02 | Phase 39 | Pending |
| ITP-03 | Phase 39 | Pending |
| ITP-04 | Phase 39 | Pending |
| ADV-04 | Phase 40 | Pending |
| ADV-05 | Phase 40 | Pending |
| DOCS-08 | Phase 41 | Pending |
| DOCS-09 | Phase 41 | Pending |
| DOCS-10 | Phase 41 | Pending |
| DOCS-11 | Phase 41 | Pending |

**Coverage summary:** 36→2 (DEP), 37→3 (REGR), 38→3 (PACE/CLASS), 39→9 (DEPTH/OUTL/ITP), 40→2 (ADV), 41→4 (DOCS). Total 23/23 ✓

## Plan-time verification spikes (from research — resolve before coding the affected binding)

- **PACE-01 / PACE-02:** `IrregFdata` list-of-arrays PyO3 constructor interface — no existing pyfda precedent; spike before writing `pace_fpca`.
- **OUTL-01..04:** audit `outliers_mod.rs` / fdars-core 0.23 outlier signatures for existing `seed` parameters; add seed exposure where random components exist.
- **ADV-05:** confirm whether `pace_fpca` / `elastic_multinomial` expose a genuinely grounded scalar diagnostic before committing advisor coverage.
- **REGR-01:** confirm `ConcurrentRegrResult.beta_curve` orientation `(p, m)` against the multi-predictor transposition test.
