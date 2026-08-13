# Project Research Summary

**Project:** pyfda — fdars-core 0.17 Upgrade (New Bindings, Advisor & Docs)
**Domain:** PyO3/maturin binding layer + functional-data-analysis library + MkDocs docs + grounded LLM advisor
**Researched:** 2026-08-13
**Confidence:** HIGH

## Executive Summary

pyfda v4.0 is a **crate-bump milestone plus a substantial additive API surface**. Upgrading `fdars-core` from 0.14.0 to 0.17.0 unlocks new public functions across three groups — interpolation/extrapolation/imputation, functional statistics/scoring metrics, and shift registration/registration-quality/banded elastic alignment. The upgrade itself is **one line in `Cargo.toml`** (caret semantics lock `^0.14.0` to `<0.15.0`, so an explicit bump is required) and the upstream diff 0.15→0.17 is **explicitly additive and non-breaking** — no existing binding signatures change and no new Rust or Python dependencies are introduced.

The recommended approach is a **strict dependency-ordered sequence**: bump the crate and run a full regression pass FIRST (the faer FPCA SVD path introduced in 0.15 makes FPCA results equivalent only within `1e-8·σ₁`, so any tighter exact-equality test or doc fence must be relaxed before new work begins), then land the three binding groups (two are parallel-eligible), then extend the v3.0 AI advisor "where relevant," then do the method-accurate docs (hand-authored SVG diagrams + runnable offline worked examples) last so executed fences run against the real compiled API.

The main risks are not in the bump but in **new-binding correctness and docs accuracy**: numpy(row-major)↔FdMatrix(column-major) transposition bugs in the new matrix-returning functions (the exact class upstream fixed as #33), the grounding invariant when extending `build_diagnostics`, and keeping new executed doc fences offline/deterministic. All are known, testable, and mapped to owning phases below.

## Key Findings

### Recommended Stack

A **single-line dependency bump** with no transitive or packaging changes. Change `fdars-core = { version = "0.14.0", ... }` to `"0.17.0"`, regenerate/commit `Cargo.lock`, keep `features = ["parallel"]`. All 20 new functions are pure-Rust compute — no new Python runtime deps, so **no new extras** are needed.

**Core technologies (unchanged):**
- **fdars-core 0.17.0** (`parallel` feature): the upgraded compute engine — purpose is the new API surface; recommended because all changes are additive/non-breaking.
- **PyO3 0.28 (abi3-py39) + numpy 0.28 crate + maturin 1.x**: existing binding toolchain — unchanged; new wrappers reuse `convert.rs` converters as-is.
- **Do NOT enable the `linalg` feature**: it gates faer/anofox-regression and requires Rust 1.84 (> pyfda MSRV 1.83) and is WASM-incompatible; its speedups are internal with no exclusively-gated public API.

### Expected Features

Fourteen documented method families (≈20 pyfunctions incl. `_with_policy`/`_with_band` variants), all thin wrappers over established FDA methods.

**Must have (table stakes):**
- **Interpolation & representation** — `spline_interpolate` (order-k B-spline per curve, off-grid eval; reuses the already-bound basis system), `*_with_policy` + `ExtrapolationPolicy{Boundary,Exception,Fill(f64),Periodic}`, `impute_missing_values` + `ImputationMethod{Linear,Mean,Constant}`.
- **Functional statistics** — `functional_variance/std/covariance`, `depth_based_median` (Fraiman–Muniz depth; returns an **index**, distinct from `geometric_median`), `trim_mean` (α=0 ≡ mean).
- **Scoring metrics** — `functional_mae/mse/mape/msle/functional_explained_variance` (Simpson-integrated scalars, `Result`-returning).
- **Shift registration** — `least_squares_shift_registration` (rigid horizontal shift δ to the cross-sectional mean via golden-section L2 min) + `ShiftRegistrationResult`.
- **Registration-quality scores** — `least_squares_score` (L2 spread, lower=better), `pairwise_correlation_score` (centered functional Pearson, higher=better), `sobolev_least_squares_score` (adds derivative penalty; requires uniform grid).

**Should have (differentiator):**
- **Banded elastic alignment** — `karcher_mean_with_band`, `elastic_self/cross_distance_matrix_with_band` (`band_frac: Option<f64>`; Sakoe–Chiba corridor, ~4–6× faster on large grids). Result struct identical to unbanded.

**Defer (out of scope):** the 0.15→0.17 internal perf wins (parallel CV folds, faer FPCA SVD, parallel elastic-FPCA) — inherited via the bump, no API to bind.

### Architecture Approach

New functions integrate into the existing three-layer stack (PyO3 wrappers `src/*_mod.rs` → `convert.rs` marshalling → Python API/`Fdata`/advisor) with **no redesign**. Enums cross the boundary as **string params + `match` arms** (established convention: `linkage`/`basis_type`/`penalty_type`), with a fallback arm since upstream enums are `#[non_exhaustive]`. Compound results return as **`PyDict`** (every existing compound-result function does; no `#[pyclass]` result type exists). `fd.interpolate()`/`fd.impute()` become `Fdata` methods; stats/scoring stay module-level functions.

**Major components / placement:**
1. **Interpolation + imputation bindings** — 4 interpolation fns + `impute_missing_values` + enum handling. *Placement is the one open decision (see Gaps):* new `src/helpers_mod.rs` (upstream `fdars_core::helpers` parity, STACK.md) vs extend `fdata_mod.rs` (smaller footprint, ARCHITECTURE.md).
2. **Functional stats + scoring bindings** — stats extend `fdata_mod.rs`; scoring is new `src/scoring_mod.rs` (upstream `fdars_core::scoring`) or extends `metric_mod.rs`.
3. **Alignment/registration bindings** — extend existing `alignment_mod.rs` (shift registration + 3 quality scores + 3 banded fns).
4. **Advisor extension** — `"scoring"` becomes diagnostics method #13; imputation-quality extends the `represent` aspect; registration-quality extends the `alignment` aspect. `_RUNNABLE_METHODS` stays 6 (scoring needs caller-supplied y_true/y_pred the MCP dataset model can't provide).

### Critical Pitfalls

1. **Column-major transposition (#33 class)** — every new matrix-returning binding (`functional_covariance`, interpolation on a new grid, banded distance matrices) must go through `fdmatrix_to_numpy2d` and carry a **multi-curve round-trip test** (shape/symmetry checks alone won't catch scrambling).
2. **faer FPCA SVD numeric drift** — after the bump, FPCA results shift within `1e-8·σ₁`; relax any FPCA test/doc-fence tolerance to ~`atol=1e-6` in the crate-bump phase *before* new binding work.
3. **Banded naming ambiguity** — bind `*_with_band` (`band_frac: Option<f64>`, `None` = unbanded), NOT the 0.14 `*_banded` (`f64`, where `0.0` does not disable the band).
4. **`depth_based_median` returns a `usize` index** — resolve to the actual curve row in the binding, else users get a bare integer.
5. **Result-error propagation** — all 10 new scoring/quality fns return `Result<T, FdarError>`; no `.unwrap()`, route through `to_pyresult()`, and add `ValueError` tests (MAPE has **no epsilon guard** → errors on near-zero truths; `sobolev_least_squares_score` needs a uniform grid).
6. **Grounding-invariant + guard-sync** — new advisor diagnostics must call the bound fdars functions (never Python math) and cite a real number; `_DIAGNOSTICS_METHODS` and `advisor._supported` must update in the **same commit** to keep `test_diagnostics_methods_match_advisor_supported` green.
7. **Offline/deterministic docs** — new executed fences use fixed seeds, base extras only, and emit the `FDARS_FENCE_OK` sentinel; diagrams pass SVGO idempotence + build-determinism gates and a human PNG method-accuracy review.

## Implications for Roadmap

Suggested phase structure (continues numbering from v3.0 → starts at **Phase 25**):

### Phase 25: Crate Bump + Regression Gate
**Rationale:** Hard dependency gate for everything else; isolates the one numeric behavior change (faer FPCA SVD) from new-binding work.
**Delivers:** `Cargo.toml` → 0.17.0, regenerated `Cargo.lock`, `maturin develop` green, full existing suite (259+ tests) passing with FPCA tolerances relaxed to absorb the `1e-8·σ₁` drift.
**Avoids:** silent caret non-upgrade; FPCA exact-equality test/fence breakage.

### Phase 26: Interpolation, Imputation & Functional Statistics Bindings
**Rationale:** Foundational table-stakes; `spline_interpolate` reuses the bound basis system; earliest matrix-returning phase → establishes the transposition-test pattern.
**Delivers:** interpolation/`_with_policy` + `ExtrapolationPolicy`, `impute_missing_values` + `ImputationMethod`, `functional_variance/std/covariance`, `depth_based_median`, `trim_mean`; `fd.interpolate()`/`fd.impute()` methods; multi-curve round-trip tests.
**Uses:** existing `convert.rs`, string-enum + `#[non_exhaustive]` fallback convention.
**Avoids:** transposition (#33), `depth_based_median` index bug, off-grid/NaN edge cases.

### Phase 27: Scoring Metrics & Alignment/Registration Bindings
**Rationale:** Independent of Phase 26 → **parallel-eligible** after Phase 25; groups the `Result`-heavy scoring + registration surface.
**Delivers:** `functional_mae/mse/mape/msle/functional_explained_variance`; `least_squares_shift_registration` + `ShiftRegistrationResult` (PyDict); `least_squares/pairwise_correlation/sobolev_least_squares_score`; banded `*_with_band` alignment.
**Avoids:** `.unwrap()` panics, MAPE zero-guard / Sobolev uniform-grid surprises, banded naming confusion.

### Phase 28: Advisor Extension (grounding-invariant preserved)
**Rationale:** Depends on Phases 26+27 (needs the bound functions to call); highest-complexity deliverable.
**Delivers:** `"scoring"` diagnostics method, imputation-quality on `represent`, registration-quality on `alignment`, MCP guard-sync updated in one commit; offline determinism + grounding tests.
**Avoids:** grounding-invariant regression; MCP guard-sync test failure.

### Phase 29: Docs — Diagrams + Worked Examples
**Rationale:** Last; executed fences must run against the shipped bindings.
**Delivers:** new/updated inline SVG concept diagrams + runnable offline worked examples across `represent/`, `analyze/`, `align/` and advisor pages; `mkdocs build --strict` green.
**Avoids:** non-deterministic fences; method-inaccurate diagrams (human PNG review).

### Phase Ordering Rationale
- **Bump first** isolates the sole numeric change and unblocks all binding work.
- **26 ∥ 27** are independent binding groups; both must precede the advisor.
- **Advisor after bindings** because diagnostics call the bound functions.
- **Docs last** so executed fences and diagrams reflect the real, green API.

### Research Flags
Phases likely needing deeper planning-time research:
- **Phase 28 (Advisor):** guard-sync interdependencies + grounding-invariant patterns for the new aspects/method.
- **Phase 29 (Docs):** SVGO/determinism gate workflow + per-diagram method-accuracy review checklist.

Standard patterns (skip research-phase):
- **Phases 25, 26, 27:** established bump/binding conventions, exact signatures already verified.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | One-line bump; all 20 signatures verified on docs.rs/0.17.0; "no new deps" stated in 0.15/0.16 notes |
| Features | HIGH | 14 method families with exact formulas/signatures from docs.rs; dataset + docs-section mapping from repo reads |
| Architecture | HIGH | Enum/struct/method conventions each cited to real repo examples with line refs; advisor points grounded in `_supported`/guard test |
| Pitfalls | HIGH | Layout/transposition, banded naming, Result propagation, grounding-sync all source-verified; faer tolerance MEDIUM (stated, not run) |

**Overall confidence:** HIGH

### Gaps to Address
- **Module placement (helpers/scoring):** new `src/helpers_mod.rs` + `src/scoring_mod.rs` (upstream-module parity) vs extend `fdata_mod.rs`/`metric_mod.rs` (smaller footprint). Planner decides in Phase 26/27; leaning to whichever keeps pyfda boundaries aligned with upstream fdars-core modules where cleaner.
- **Exact struct field names** (`ShiftRegistrationResult`, `impute_missing_values` outputs): confirm against the crate source once the bump is applied, before writing wrappers.
- **`band_frac` shape:** confirmed as an `Option<f64>` parameter on `karcher_mean_with_band` (not a standalone fn) — reverify at bind time.
- **faer FPCA tolerance:** exact magnitude of drift on the real suite unverified; discover empirically in Phase 25.
- **`functional_covariance` / `sobolev` API polish:** whether covariance is also an `Fdata` method and whether Python-side pre-validates a uniform grid for a friendlier error.

## Sources

### Primary (HIGH confidence)
- `docs.rs/fdars-core/0.17.0` — all new function/struct/enum signatures, module index (`helpers`, `scoring`)
- `github.com/sipemu/fdars` — release notes v0.15.0 (FEAT-01/02, PERF-01/02) & v0.16.0 (FEAT-03/04/05, PERF-03), PR #41 (v0.17.0 FEAT-06/07, PERF-04); note the committed CHANGELOG file is stale at 0.14.0
- Repo source: `Cargo.toml`, `Cargo.lock`, `src/convert.rs`, `src/lib.rs`, `src/{alignment,basis,metric,fdata}_mod.rs`, `python/fdars/{__init__,fdata_class}.py`, `python/fdars/advisor/*`, `python/fdars/mcp/*`, `.planning/codebase/*`, `.planning/RETROSPECTIVE.md`

### Secondary (MEDIUM confidence)
- faer FPCA SVD equivalence "within `1e-8·σ₁`" — release-note prose, not yet run against the live suite
- `linalg` MSRV 1.84 constraint — docs prose; upstream `rust-version` field not directly inspected

---
*Research completed: 2026-08-13*
*Ready for roadmap: yes*
