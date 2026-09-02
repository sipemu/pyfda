# Project Research Summary

**Project:** pyfda — fdars-core 0.33 Upgrade (v11.0)
**Domain:** PyO3 binding layer + Python API + AI advisor + MkDocs site over the Rust `fdars-core` functional-data-analysis crate
**Researched:** 2026-09-02
**Confidence:** MEDIUM (HIGH on stack + pitfalls; MEDIUM on features + architecture — sourced from crates.io/docs.rs, not an exhaustive fdars-core source audit)

## Executive Summary

pyfda v11.0 is a **clean, additive-only crate upgrade** (`fdars-core` 0.23.0 → 0.33.0) that exposes the new upstream surface as PyO3 bindings + Python API, extends the AI advisor where relevant (grounding invariant preserved), and documents it — the same shape as v4.0/v5.0/v6.0. The bump itself is trivial (a single `Cargo.toml` line); the binding work is substantive (~35 new functions across ~7 new/extended modules, up to 2 new opaque `#[pyclass]` handles, and up to 4 new/extended advisor aspects).

The 10-minor jump (vs. the prior 3-minor additive waves) triples the chance of a **silent numeric drift or a changed default** that `cargo build` won't catch, so the established protocol is non-negotiable: **isolate the bump in its own phase and gate it on the full ~772-test Python suite before any binding work.** Sources converge that MSRV at 0.33.0 is **1.81** (pyfda pins 1.83 — satisfied with headroom), the `parallel`-only build is unchanged, and **no new capability is `linalg`-gated** — so the user decision to stay parallel-only holds with zero cost to coverage. Notably, the original `linalg` deferral reason (faer needing Rust 1.84) is now **obsolete** (faer ^0.23 MSRV is 1.81) — a note for a *future* milestone, not this one.

Key risks and mitigations: (1) **numeric drift** across the jump → isolated bump + full regression gate (Phase 66); (2) **row-major↔column-major transposition bugs** in new multi-array bindings → route every 2D arg through `numpy2d_to_fdmatrix`, test with non-square `n_obs ≠ n_points` fixtures; (3) **grounding-invariant / MCP guard-sync** violations in the advisor → only fdars-computed scalars in diagnostic dicts, atomic `_DIAGNOSTICS_METHODS`+`_ASPECT_PRIMERS` commits, `json.dumps` serialization test per aspect; (4) **method-inaccurate diagrams** for unfamiliar new methods → blocking human diagram review as the hard close gate (the v6.0 hypograph/epigraph lesson); (5) **docs build contamination** → docs phase runs sequentially on `main`, never in worktrees (fences hardcode the main-tree `.venv/bin/mkdocs`).

## Key Findings

### Recommended Stack

A **single-line `Cargo.toml` change** (`fdars-core = "0.23.0"` → `"0.33.0"`, `parallel` feature retained) is all the bump requires. No forced toolchain, PyO3, numpy, or maturin change; MSRV 1.81 at 0.33.0 is satisfied by pyfda's 1.83 pin. Feature flags are unchanged (`parallel` still the only one needed; a new optional `serde` feature exists but is not needed). Zero transitive-dependency changes under `parallel`-only (nalgebra/rayon/rustfft/rand/rand_distr all identical 0.23↔0.33). One **soft deprecation** at 0.30: four 2D depth functions (`fraiman_muniz_2d`, `modal_2d`, `random_projection_2d`, `random_tukey_2d`) are `#[deprecated]` — warning only, migrate in a binding phase, not the bump phase. See `STACK.md`.

**Core technologies (all unchanged):**
- PyO3 0.28 (abi3-py39), numpy 0.28, maturin 1.x — no bump forced by the upgrade
- Rust MSRV 1.83 (fdars-core 0.33 needs only 1.81) — headroom preserved
- `fdars-core` `parallel` feature only; `linalg` stays OFF (no new capability needs it)
- Package version → **`0.10.0`** at close (semver `v0.10.0` tag triggers PyPI publish; decided at close)

### Expected Features

~35 new functions across ~7 new/extended upstream modules, all non-`linalg`-gated and bindable with the current build. The four researchers converged on the *surface* but diverged slightly on the exact module grouping (7–13 groups) — the roadmapper should treat the groupings below as candidate binding waves to confirm during phase planning. See `FEATURES.md` / `ARCHITECTURE.md`.

**Must have (table stakes — fill obvious gaps in the existing surface):**
- **Function-on-function regression** (`fof_regression`, `fof_re_regression` + random effects) — extends `fdars.regression`
- **Advanced clustering** (`dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd`) — new `fdars.clustering_advanced` surface
- **SoF regression extensions** (`fam`, `fregre_gkam`, `fregre_gsam`, variable/model selection) — extends `fdars.scalar_on_function`
- **FPCA variants** (`fsvd`, `fpca_der`, `cross_covariance`, `dynamical_correlation`, `ssvd`)
- **Deprecated-depth migration** — move off the four 0.30-deprecated 2D depth functions

**Should have (differentiators — new analysis paradigms):**
- **Functional time series** (`fts`): `ftsm` + forecast/multistep, `functional_acf`/`pacf`, `stationarity_test`, `long_run_covariance`, `fplsr`, `dpca` — new `fdars.fts` submodule
- **Fréchet regression / metric-space** (`frechet_mean`, `frechet_global_reg`, `frechet_local_reg`, `frechet_anova`) — new `fdars.frechet` submodule
- **Density FDA** (`lqd_fpca`, `lqd_transform`, `inverse_lqd`, `wasserstein_barycenter`, `normalize_density`) — new `fdars.density_fda` submodule
- **Multi-domain data + FAMM** (`MultiFunData`/`FdComponent` opaque handle; `dense_flmm`, `fast_fmm`, `multi_famm`; multivariate SPM) — new `PyMultiFunData` `#[pyclass]`
- **Shapelets + GAK metric** (`discover_shapelets`, `shapelet_*`, `gak`, `gak_gram_*`, `sigma_gak`) — new `fdars.shapelet` + `metric` extension; new `PyShapeletFit` handle + 2 new enums

**Defer (out of scope this milestone / candidates for later):**
- **FEM smoothing** (`fem_smooth`, `fem_smooth_gcv`, `fem_predict`) — non-standard mesh input shape (needs a new triangle-index conversion path); lowest priority
- **PDA** (`principal_differential_analysis`) — specialized ODE estimation
- Enabling `linalg` (now MSRV-unblocked) — explicit user decision to stay parallel-only this milestone

### Architecture Approach

No hard breaking changes to any currently-bound function across 0.24→0.33 — the bump gate should pass all 772 tests with zero test changes (one soft deprecation aside). New capabilities slot into pyfda's existing thin-wrapper architecture: new `src/*_mod.rs` modules registered via `register_submodule!` in `lib.rs`, PyDict result converters in the pattern of `itp_result_to_pydict`, `#[non_exhaustive]`/string-dispatch enums with mandatory `Err`-returning fallback arms, and up to two new opaque `#[pyclass]` handles mirroring the existing `PyIrregFdata`. See `ARCHITECTURE.md`.

**Major components:**
1. **Isolated bump gate** (Phase 66) — one-line `Cargo.toml` change + full 772-test regression run + changelog/match-arm audit
2. **New binding modules** — `fts`, `frechet`, `density_fda`, `multi_fdata`, `shapelet` submodules + `regression`/`clustering`/`scalar_on_function`/`metric`/`famm`/`spm` extensions
3. **Conversion-layer additions** — factor `extract_ragged_vecs` out of `pace_fpca_mod.rs` into `convert.rs` (ragged density/Fréchet inputs); add an i64→usize path for FEM mesh indices (only if FEM is bound)
4. **Advisor extension** — new `fts`/`frechet` aspects + extended `regression`/`classification`/`spm` aspects; grounding invariant + atomic MCP guard-sync
5. **Docs** — new pages + hand-authored SVGs + offline `FDARS_FENCE_OK` fences; sequential on `main`

### Critical Pitfalls

1. **Silent numeric drift across the 10-minor jump** (HIGH — v4.0 faer-SVD precedent) → isolate the bump; gate on the full ~772-test Python suite, not `cargo test` alone; document any tolerance change.
2. **Row-major↔column-major transposition on non-square inputs** → route every 2D argument through `numpy2d_to_fdmatrix`; every new binding needs a fixture with `n_obs ≠ n_points` (square fixtures hide the bug).
3. **`argvals` omission/duplication** → annotate each binding `// argvals: mandatory | optional | absent`; test both paths (wrong default grid silently corrupts non-uniform data).
4. **Missing `Err` arm on new enum dispatch** (`QualityMeasure`, `ShapeletClassifier`) → wildcard arm must return `PyValueError` listing valid variants, not `Ok(None)`; test asserts `ValueError` on invalid input.
5. **Grounding-invariant / guard-sync violation in the advisor** → only fdars-computed scalars in diagnostic dicts (no Python-derived numbers, no numpy scalars into `json.dumps`); atomic commit of aspect + `_DIAGNOSTICS_METHODS` + `_ASPECT_PRIMERS`; `test_guard_sync_version_independent.py` must pass.
6. **Method-inaccurate diagrams + docs-build contamination** → blocking human diagram review before close (v6.0 lesson); docs phase sequential on `main` with `use_worktrees=false`; keep fences small (build is ~19–25 min).

## Implications for Roadmap

Suggested shape mirrors v4/v5/v6 exactly: **isolated bump → parallel binding groups → advisor → docs.** Phase numbering continues from Phase 66 (v10.0 ended at 65). The exact number and boundaries of the binding phases should be set by the roadmapper against the requirement scope selected in REQUIREMENTS.md — the grouping below is the researchers' recommendation, not a fixed contract.

### Phase 66: Isolated Crate Bump + Regression Gate
**Rationale:** Numeric-drift detection is the highest-risk failure in a 10-minor jump; isolate it from all binding work.
**Delivers:** `Cargo.toml` 0.23.0 → 0.33.0; maturin rebuild; full 772-test suite green; changelog audit (0.24–0.33, incl. the 0.31/0.32 gap) + grep of every existing `match str_arg { … }` block against the 0.33 API.
**Avoids:** Pitfalls #1 (drift), #4 (removed/renamed enum variants).

### Phases 67–71: New Binding Groups (parallelizable after 66, except as noted)
**Rationale:** Additive, disjoint module sets — parallel worktrees cut wall-clock (v10.0 precedent), except groups sharing `spm_mod.rs` must be sequential.
**Delivers (candidate grouping):**
- **FTS** — `fdars.fts` submodule (~8–13 fns, forecast/ACF/PACF/stationarity/dpca/fplsr)
- **Function-on-function regression** — extend `fdars.regression` (fof + random effects)
- **Fréchet + Density FDA** — two new submodules; needs the `extract_ragged_vecs` `convert.rs` refactor first
- **Multi-domain data + FAMM + advanced clustering** — `PyMultiFunData` handle → SPM multivariate extensions → clustering; **sequential within the phase** (multi_fdata before spm), and the only group touching `spm_mod.rs`
- **Shapelet + GAK metric** — `fdars.shapelet` submodule (`PyShapeletFit` + 2 enums) + `metric` GAK extension
**Uses:** existing `register_submodule!`, PyDict-converter, opaque-`#[pyclass]` patterns.
**Avoids:** Pitfalls #2 (transposition), #3 (argvals), #4 (enum arms).

### Phase 72: Advisor Extension
**Rationale:** Depends on all new bindings being live and callable.
**Delivers:** new `fts`/`frechet` aspects + extended `regression`/`classification`/`spm` aspects; grounded fdars-computed scalars; atomic guard-sync; `json.dumps` test per aspect. Keep `frechet` diagnostics-only initially (defer from `_RUNNABLE_METHODS` until a density-dataset registration protocol is designed).
**Avoids:** Pitfalls #5 (grounding/guard-sync).

### Phase 73: Documentation
**Rationale:** Docs build runs real compute against the main tree; must be last and sequential.
**Delivers:** new pages (fts / fof-regression / frechet / density-fda or multi-fdata / shapelet) each with a method-accurate hand-authored inline SVG + offline `FDARS_FENCE_OK` worked example; whole-site `mkdocs build --strict` green; blocking human diagram review.
**Avoids:** Pitfalls #6 (method-inaccuracy, worktree contamination, slow fences, stale cross-refs).

### Phase Ordering Rationale
- Bump gates everything (drift detection before binding work builds on a shifted baseline).
- Binding groups are additive + mostly disjoint → parallel worktrees, except the multi-domain/SPM group (shared `spm_mod.rs`, internal sequential dependency).
- Advisor after bindings (needs callable functions); docs last + sequential on `main` (real-compute fences, `use_worktrees=false`).

### Research Flags
Phases likely needing deeper research during planning:
- **Bump phase (66):** confirm the 0.31/0.32 changelog (missing from published CHANGELOG — check GitHub source tags/diff.rs) and cross-check result-struct field names against 0.33 source before the binding phases.
- **FTS phase:** FTSM AR-order selection + forecast strategy (iterated vs. direct h-step); stationarity-test null.
- **Fréchet + Density phase:** LQD transform vs. R `fda` reference; Wasserstein formula; ragged-input conversion.
- **Multi-domain/FAMM phase:** `MultiFunData` same-obs-count validation; `dense_flmm` REML stopping criterion; exact struct fields.
- **Shapelet/GAK phase:** exact `ShapeletDiscoveryConfig`/`GakConfig` fields (docs.rs 404 at 0.33 — read source); z-norm divide-by-zero; GAK Gram PSD + sklearn precomputed-kernel integration.

Phases with standard patterns (lighter research):
- **Function-on-function regression:** closes a visible gap; established v4–v6 binding pattern.
- **Advisor + docs:** well-worn project protocols (guard-sync, `FDARS_FENCE_OK`, human diagram review).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | crates.io/docs.rs: MSRV 1.81, clean deps, no forced toolchain bump, `parallel`-only unchanged |
| Features | MEDIUM | Capability inventory + signatures from docs.rs; some config-struct fields returned 404 at 0.33 (inferred from CHANGELOG) |
| Architecture | MEDIUM | "Additive/non-breaking" converges across 6 release notes + CHANGELOG; struct-field stability inferred from docs.rs, not source |
| Pitfalls | HIGH | Every pitfall derives from verified project history (v4–v6 Key Decisions) or direct codebase inspection |

**Overall confidence:** MEDIUM

### Gaps to Address
- **0.31/0.32 changelog gap** — not on the published CHANGELOG; confirm no surprise API change via GitHub source tags before finalizing binding scope (bump-phase pre-work). If an internal break exists, the Phase-66 regression gate catches it.
- **Exact result-struct + config field names** (`density_fda`, `frechet`, `multi_fdata`, `shapelet`, FEM) — cross-check against 0.33 source before implementing each group's PyDict converters.
- **Per-group advisor scope** — which new groups produce grounded scalar diagnostics worth an aspect vs. diagnostics-only; resolve during Phase 72 planning.
- **`MetricSpace` (Fréchet) bindability** — a Rust trait, not a concrete type; needs a string-dispatch strategy (like `DepthMethod`) at binding time, not a research blocker.
- **`funhddC_cluster` / deprecated-2D-depth presence** — verify actual public API at 0.33 during the bump phase.

## Sources

### Primary (HIGH confidence)
- crates.io API — fdars-core version registry, `rust_version` (MSRV 1.81), Cargo feature manifest, transitive-dep manifests for 0.23.0 vs 0.33.0
- docs.rs — fdars-core 0.23.0–0.33.0 module indexes, struct/function pages (signatures + fields)
- pyfda source inspection — `convert.rs`, `lib.rs` `register_submodule!`, existing `*_mod.rs` patterns, advisor `server.py` frozensets + `_validate.py` grounding guard
- PROJECT.md Key Decisions + MEMORY.md — v4–v6 precedents (faer drift, hypograph/epigraph, worktree-vs-main, guard-sync)

### Secondary (MEDIUM confidence)
- GitHub release notes — v0.24, v0.27, v0.28, v0.29, v0.32, v0.33
- fdars-core CHANGELOG.md — additive-only claim (0.31/0.32 entries absent)

### Tertiary (LOW confidence)
- docs.rs field-access inferences for struct field names (not an exhaustive source-code audit) — cross-check per group before implementation

---
*Research completed: 2026-09-02*
*Ready for roadmap: yes*
