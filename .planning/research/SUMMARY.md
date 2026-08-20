# Project Research Summary

**Project:** pyfda v6.0 — fdars-core 0.20.0 → 0.23.0 upgrade (Regression, PACE-FPCA/Classification, Depth/Outliers/Interval Inference)
**Domain:** PyO3 binding-layer upgrade (Rust functional-data-analysis crate → Python `fdars` package)
**Researched:** 2026-08-20
**Confidence:** HIGH

## Executive Summary

pyfda v6.0 is a **binding-layer upgrade** exposing fdars-core 0.23's new capabilities across three independent functional groups, following the exact shape of the v4.0 (0.17) and v5.0 (0.20) upgrade milestones: crate bump as an isolated regression gate → three parallel binding groups → advisor extension → docs. The bump itself is low-risk — `git diff v0.20.0 v0.23.0 -- fdars-core/Cargo.toml` shows only the version string changed, the transitive dependency graph is additive-only, MSRV actually *drops* to 1.81 (below pyfda's own 1.83 pin), and `linalg` stays off and unneeded (it still gates only `ridge_regression_fit` and still wants Rust 1.84+). No new Python extras, no new dataset files, no CI-matrix changes.

Risk concentrates in **new-binding correctness**, not the upgrade. The dominant novelty is Group B's `pace_fpca`, which takes `&IrregFdata` — a CSR-layout sparse-observation type with no existing Python binding precedent; it needs a new `src/pace_fpca_mod.rs` and a lists-of-arrays Python builder (a plain 2D numpy array compiles but silently produces wrong results). Everything else extends existing `*_mod.rs` files through the established `numpy2d_to_fdmatrix`/`fdmatrix_to_numpy2d` round-trip. Secondary risks are the familiar pyfda hazards: column-major transposition (esp. `beta_curve` shaped `(p, m)` not `(n_obs, m)`), `#[non_exhaustive]` enums needing wildcard arms plus matching Python string maps, the v5.0 CR-01 negative-label guard recurring in `elastic_multinomial`, and preserving the advisor grounding invariant (reduce ITP p-value curves / outlier index vectors to grounded scalars, never numpy aggregates).

Two scope gray areas surfaced for planning/discuss to resolve: (1) whether the outlier detectors get a **new** advisor aspect vs extend the existing `outliers` aspect (Architecture said no new aspect keys; Features suggested a new aspect #15) — either way this closes the v5.0 Phase-34 functional-boxplot-outlier deferral; and (2) whether PACE-FPCA gets any advisor treatment or is **bindings + docs only** (Features judged its grounding surface insufficient).

## Key Findings

### Recommended Stack

Single-line change: `fdars-core = { version = "0.23.0", features = ["parallel"] }` (from `0.20.0`). Keep `parallel`, do **not** enable `linalg`. Rebuild via maturin; the ~560-test suite is the regression gate. See `STACK.md` for the full verdict.

**Core technologies (unchanged):**
- fdars-core 0.23.0 (`parallel` only) — the compute engine; bump is additive/non-breaking
- PyO3 0.28 (abi3-py39) + numpy 0.28 crate — binding boundary; all new functions bind through it
- maturin — build backend; no config change
- MkDocs Material + markdown-exec — docs with executed offline `FDARS_FENCE_OK` fences

### Expected Features

See `FEATURES.md` for full signatures and result-struct field lists.

**Group A — Regression (extend `fdars.regression`):**
- `concurrent_regression` / `ConcurrentRegrResult` — varying-coefficient regression; input `predictors: list[np.ndarray]` (slice-of-matrices); `beta_curve` is `(p, m)`
- `functional_glm` / `FunctionalGlmResult` (15 fields) — exponential-family GLM (Binomial/Poisson/Gamma/Gaussian) via IRLS over FPC scores; re-fits FPCA internally; Gamma uses inverse canonical link 1/μ (document; AIC not comparable to R `glm()`)

**Group B — FPCA & Classification:**
- `pace_fpca` / `PaceFpcaConfig` / `PaceFpcaResult` (10 fields incl. per-curve confidence bands) — sparse/irregular PACE FPCA; **new `IrregFdata` input** (two lists-of-1D-arrays per curve); no existing dense dataset works → synthetic inline fence data
- `elastic_multinomial` / `ElasticMultinomialResult` — OvR K-class extension of existing `elastic_logistic`; requires 0-indexed contiguous labels (CR-01 guard); phoneme.csv (subsample to 3 classes, m ≤ 64) drives the fence

**Group C — Depth / Outliers / Interval Inference:**
- 9 new `DepthMethod` variants (HypographIndex, ModifiedHypographIndex, EpigraphIndex, HalfRegion, ModifiedHalfRegion, Extremal, ExtremeRankLength, LInfinity, TotalVariation) — extend the v5.0 `functional_depth` dispatcher (→ 13 methods total)
- 4 outlier detectors (`tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram`) extending `fdars.outliers` — closes the v5.0 Phase-34 deferral
- 3 interval-wise tests (`itp_one_pop`, `itp_two_pop`, `itp_flm`) / `ItpResult` extending `fdars.inference`; returns **vector** (closure-adjusted) p-values → needs a new `itp_result_to_pydict` distinct from `test_result_to_pydict`

**Defer / out of scope:** `linalg`-gated `ridge_regression_fit`; HEAD's 0.24-bound work (FAM, mixed models, FoF-RE) — not in 0.23.

### Architecture Approach

See `ARCHITECTURE.md`. Mirrors v5.0 exactly. **1 new Rust file** (`src/pace_fpca_mod.rs`) because of the `IrregFdata` input; **6 extended files** (`regression_mod.rs`, `classification_mod.rs`, `depth_mod.rs`, `outliers_mod.rs`, `inference_mod.rs`, `lib.rs`). Five new result-struct→PyDict helpers following the canonical `test_result_to_pydict()` pattern. Four enum dispatch patterns need forward-compatible wildcard arms **and** Python string maps: `DepthMethod` (extend), `GlmFamily`, `SeqTransform`, `ProjectionBasisType`.

**Major components:**
1. Crate bump + regression gate — `Cargo.toml` one-liner, `cargo build`, ~560-test suite
2. Three parallel binding groups (A/B/C) — thin `#[pyfunction]`s + PyDict converters + transposition guards
3. Advisor extension — existing aspect builders detect new result-dict keys; grounded scalar diagnostics; MCP `_DIAGNOSTICS_METHODS` guard-sync in a single atomic commit
4. Docs — new pages + method-accurate hand-authored inline SVGs + offline `FDARS_FENCE_OK` fences

### Critical Pitfalls

Top items from `PITFALLS.md` (20 total: 13 binding + 7 advisor/docs):

1. **`beta_curve` transposition** — shape `(p, m)`, not the pyfda-standard `(n_obs, m)`; add a multi-predictor (`p ≥ 2`) transposition guard test (v4.0 Phase 27 pattern).
2. **`IrregFdata` passed as a 2D array** — compiles but silently wrong; build `irreg_fdata_from_lists(argvals_list, values_list)` before any PACE binding work.
3. **`elastic_multinomial` negative/non-contiguous labels** — `i64→usize` wraps to `usize::MAX` (v5.0 CR-01); add the label guard → helpful `ValueError`.
4. **`DepthMethod`/`SeqTransform` dispatcher gaps** — Rust catches missing wildcard arms, but NOT missing Python string mappings for the 9 new depth variants / SeqTransform sequence.
5. **ITP determinism + numpy-scalar leak** — permutation seed must default to 0 for offline determinism; reduce `ItpResult` vectors to `float()` (not `np.float64`) for JSON/grounding.
6. **Advisor grounding for new aspects** — store scalar counts / score ranges / p-value extrema, never raw index lists or numpy aggregates; land aspect builder + MCP guard in one atomic commit.

## Implications for Roadmap

Suggested structure continues numbering from v5.0's Phase 35 → **starts at Phase 36**. Six phases, same shape as v4.0/v5.0.

### Phase 36: Crate bump + regression gate
**Rationale:** Isolate the sole (near-zero) numeric change on a green baseline before any new bindings, so binding-correctness issues can't hide behind an upgrade regression (v4.0/v5.0 precedent).
**Delivers:** `Cargo.toml` 0.20.0 → 0.23.0, maturin rebuild, full ~560-test suite green.
**Avoids:** enabling `linalg` (still Rust 1.84+); MSRV verified 1.81 ≤ 1.83.

### Phase 37: Group A — Regression bindings
**Rationale:** Standard extension of `fdars.regression`; independent of B and C.
**Delivers:** `concurrent_regression` + `functional_glm` + `GlmFamily` dispatch + PyDict converters.
**Avoids:** `beta_curve (p,m)` transposition bug; documents Gamma inverse link + AIC caveat.

### Phase 38: Group B — FPCA & Classification bindings
**Rationale:** Contains the one novel input pattern; do `elastic_multinomial` first, then `pace_fpca` after the `IrregFdata` builder is settled.
**Delivers:** new `src/pace_fpca_mod.rs` (IrregFdata builder + `pace_fpca`) + `elastic_multinomial` with CR-01 label guard.
**Research flag:** IrregFdata Python constructor interface — resolve at plan/discuss time.

### Phase 39: Group C — Depth / Outliers / Interval Inference bindings
**Rationale:** Largest pitfall surface; extend depth dispatcher (trivial match) → outlier detectors → ITP (new converter).
**Delivers:** 9 depth variants, 4 outlier detectors, 3 ITP functions + `ProjectionBasisType`/`SeqTransform` dispatch + `itp_result_to_pydict`.
**Research flag:** audit `outliers_mod.rs` for existing seed parameter.

### Phase 40: Advisor extension
**Rationale:** Depends on the binding groups; grounded diagnostics need the shipped result dicts.
**Delivers:** existing aspect builders (regression, fpca, classification, outliers, inference) detect new result keys and emit grounded scalar diagnostics; MCP guard-sync single atomic commit. Closes the Phase-34 boxplot-outlier deferral.
**Research flag:** finalize outlier scalar spec (n_outliers, fraction, score ranges); resolve the two scope gray areas (new outliers aspect vs extend; PACE advisor treatment or defer).

### Phase 41: Docs
**Rationale:** Depends on shipped bindings + advisor.
**Delivers:** new dedicated pages + method-accurate hand-authored inline SVGs (depth asymmetry, PACE irregular observations, ITP closure direction) + offline `FDARS_FENCE_OK` worked examples (canadian_weather, tecator, phoneme, synthetic PACE/ITP data); whole-site `mkdocs build --strict` green.
**Avoids:** slow build — PACE/ITP fences use n ≤ 20 synthetic data; keep total build under ~25 min.

### Phase Ordering Rationale

- Bump-first isolates numeric risk on a green baseline (proven in v4.0/v5.0).
- Groups A/B/C are mutually independent (distinct `*_mod.rs` files) → parallelizable, ~3× wall-clock over sequential.
- Advisor after bindings (needs the result dicts); docs last (needs both).

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 38:** `IrregFdata` list-of-arrays PyO3 binding pattern — no pyfda precedent.
- **Phase 40:** advisor outlier scalar spec + the two scope gray areas.

Phases with standard patterns (lighter planning):
- **Phases 36, 37, 39:** established bump/binding/dispatcher patterns from v4.0/v5.0.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Read from `git show v0.23.0:fdars-core/Cargo.toml`; single-field diff; MSRV/linalg verified |
| Features | HIGH | All signatures, result fields, enum variants read directly from v0.23.0 source |
| Architecture | HIGH | File-by-file changes mapped; patterns match v5.0 precedents |
| Pitfalls | HIGH | 20 pitfalls from v0.23.0 source + v4.0/v5.0 code-review reports (CR-01, WR-01, WR-02) |

**Overall confidence:** HIGH. Main risk is execution complexity (IrregFdata + four enum dispatchers + three parallel groups), not research uncertainty.

### Gaps to Address

- **IrregFdata Python builder interface** (Phase 38): recommend `fdars.irreg_fdata_from_lists(argvals_list, values_list)`; confirm at plan time (MEDIUM — no existing PyO3 precedent in pyfda).
- **`outliers_mod.rs` seed audit** (Phase 39): confirm whether outlier detectors expose a seed; add for deterministic offline tests.
- **Advisor outlier scalar spec** (Phase 40): finalize exact grounded diagnostics.
- **Advisor scope gray areas** (Phase 40): (1) new `outliers` aspect vs extend existing; (2) PACE advisor treatment vs bindings+docs only.
- **Docs fence performance** (Phase 41): PACE/ITP fences use n ≤ 20 synthetic; keep build < ~25 min.

## Sources

### Primary (HIGH confidence)
- Local fdars-core checkout `/home/simonm/projects/rust/fdars` at the **`v0.23.0` git tag** — Cargo.toml, `src/{concurrent_regression,pace_fpca,outliers}.rs`, `src/scalar_on_function/glm.rs`, `src/elastic_regression/logistic.rs`, `src/depth/*`, `src/inference/itp.rs`, `lib.rs`
- pyfda repo — `src/{convert,lib,inference_mod,depth_mod,regression_mod,classification_mod}.rs`, `python/fdars/__init__.py`, `advisor/`, `mcp/server.py`, `Cargo.toml`, `pyproject.toml`
- pyfda `.planning/milestones/v5.0-*` and `v4.0-*` — prior-upgrade precedent + code-review fix reports (CR-01, WR-01, WR-02)

### Secondary (MEDIUM confidence)
- Advisor scope recommendations — analogical reasoning from v4.0/v5.0 aspect patterns; exact boundaries confirmed at discuss/plan time

### Detailed research files
- `STACK.md`, `FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md` (all committed, v6.0)

---
*Research completed: 2026-08-20*
*Ready for roadmap: yes*
