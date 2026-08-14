# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- 🚧 **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (in progress)

## Phases

<details>
<summary>✅ v1.0 Documentation Overhaul (Phases 1–9) — SHIPPED 2026-08-08</summary>

Reworked the MkDocs site's hand-authored SVG diagrams and worked example pages to a consistently high, method-accurate standard, on top of new style/determinism/doc-test guardrails.

- [x] Phase 1: Foundation — SVG style spec, SVGO lint gate, deterministic builds, snippets, pytest-markdown-docs, DOCS_FAST (completed 2026-08-07)
- [x] Phase 2: Audit — nav + reference-API audit → diagram coverage map + ranked gap list (completed 2026-08-07)
- [x] Phase 3: learn/ Diagrams — conform, fix coordinate-reuse bug, close gaps (completed 2026-08-08)
- [x] Phase 4: represent/ Diagrams — remove R-era content, conform, close gaps (completed 2026-08-08)
- [x] Phase 5: align/ Diagrams — conform, fix phase-vs-amplitude split, close gaps (completed 2026-08-08)
- [x] Phase 6: analyze/ Diagrams — migrate legacy outliers, conform, close gaps (completed 2026-08-08)
- [x] Phase 7: regression/ Diagrams — redraw conformal band, conform, close gaps (completed 2026-08-08)
- [x] Phase 8: monitoring/ Diagrams — remove R-era content, redraw control limits, close gaps (completed 2026-08-08)
- [x] Phase 9: Examples Sweep — all pages correct against current API, enriched narrative, improved figures, five new examples (completed 2026-08-08)

</details>

<details>
<summary>✅ v2.0 Grounded AI analysis advisor (Phases 10–13) — SHIPPED 2026-08-10</summary>

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout (fdars computes the numbers; the LLM only interprets and cites them).

- [x] Phase 10: Advisor Core Primitive — offline `build_diagnostics` + grounded `advise` (Claude structured outputs) + cluster-difference specialization + `[advisor]` extra (completed 2026-08-09)
- [x] Phase 11: Python API Surface — recommend-only advisor on the public `fdars` API, offline + env-gated tests, `examples/advisor_recipe.py` (completed 2026-08-09)
- [x] Phase 12: Tool / MCP Surface — coarse-grained tools + stdio MCP server + agentic re-run/compare loop (completed 2026-08-09)
- [x] Phase 13: Agent Skill Surface — `SKILL.md` + walkthrough packaging the interpret→recommend→re-run→compare workflow, documented execution environment (completed 2026-08-10)

</details>

<details>
<summary>✅ v2.1 Document the AI Advisor (Phases 14–18) — SHIPPED 2026-08-11</summary>

Gave the published MkDocs site a first-class, method-accurate "AI Advisor" section documenting the shipped v2.0 grounded advisor. Documentation-only; every page method-accurate against `python/fdars/advisor.py`, `python/fdars/mcp/`, and `.claude/skills/fdars-advisor/`; full `mkdocs build --strict` green. Full detail: `.planning/milestones/v2.1-ROADMAP.md`.

- [x] Phase 14: Advisor Concept & Diagrams — overview page + grounding-invariant & advisor-loop inline SVGs (completed 2026-08-11)
- [x] Phase 15: Python API Page — `build_diagnostics`/`advise`/`describe_cluster_differences` + offline worked example that runs in the build (completed 2026-08-11)
- [x] Phase 16: Tool / MCP Server Page — three tools, by-reference handle model, stdio, re-run/compare loop (completed 2026-08-11)
- [x] Phase 17: Agent Skill Page — git-URL install + interpret→recommend→re-run→compare walkthrough (completed 2026-08-11)
- [x] Phase 18: Nav & Build Integration — "AI Advisor" nav section wired; full `--strict` build clean (completed 2026-08-11)

</details>

<details>
<summary>✅ v3.0 Provider-Agnostic Advisor, Full-Library Coverage (Phases 19–24) — SHIPPED 2026-08-12</summary>

Made the fdars AI advisor work with any LLM backend (Anthropic, OpenAI/OpenAI-compatible, Google Gemini, local Ollama) through a custom `Provider` protocol, and gave every fdars analysis aspect its own advisor (diagnostics + grounded task families) — with the grounding invariant preserved on every backend. Dependency-ordered: provider/grounding foundation first (blocking); adapters and per-aspect diagnostics parallel-eligible; surfaces, packaging/CI, and docs on top; docs last. 28/28 requirements complete; suite 259 passed / 4 skipped. Full detail: `.planning/milestones/v3.0-ROADMAP.md`.

- [x] Phase 19: Provider Foundation & Grounding Contract — `Provider` protocol + Anthropic refactor + validate-and-retry + centralized `_check_grounding` (completed 2026-08-12)
- [x] Phase 20: Additional Provider Adapters — OpenAI (+ `base_url`), Ollama (local, no key), Gemini adapters as optional extras (completed 2026-08-12)
- [x] Phase 21: Per-Aspect Advisor Coverage — `build_diagnostics` + three grounded task families for all 12 fdars aspects via one shared schema/prompt (completed 2026-08-12)
- [x] Phase 22: Surface Integration — MCP exposes new aspect diagnostics (LLM-free); provider selection via Python `advise()`; Agent Skill documents coverage (completed 2026-08-12)
- [x] Phase 23: Packaging & CI — Python 3.9–3.14 matrix with version-gated extras + bare-venv smoke + aspect × provider offline grounding matrix (completed 2026-08-12)
- [x] Phase 24: Documentation — provider setup guide + per-aspect coverage page + updated overview/API pages; `mkdocs build --strict` offline (completed 2026-08-12)

</details>

<details open>
<summary>🚧 v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Phases 25–29) — IN PROGRESS</summary>

Upgrade the pinned `fdars-core` from 0.14.0 to 0.17.0, expose the new upstream functional-data capabilities (interpolation/imputation, functional statistics/scoring, shift registration/registration-quality/banded elastic alignment) through PyO3 bindings + the Python API, extend the v3.0 AI advisor to cover the relevant new capabilities, and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Upstream 0.15→0.17 is additive/non-breaking; risk concentrates in new-binding correctness (column-major layout, `Result` conversions) and diagram/example method-accuracy — not in the bump.

Dependency-ordered: the crate bump + regression gate ships first (isolates the sole numeric change — faer FPCA SVD drift — and unblocks all binding work); the two binding groups are then independent (parallel-eligible after the gate); the advisor extension assembles on top of the bound functions; docs last, so executed fences and diagrams run against the real shipped bindings.

### Summary

- [x] **Phase 25: Crate Bump + Regression Gate** - Bump `fdars-core` 0.14.0→0.17.0, regenerate `Cargo.lock`, rebuild via maturin, full existing suite green with FPCA tolerances relaxed to absorb the faer SVD drift. Blocks all binding work. (completed 2026-08-14)
- [ ] **Phase 26: Interpolation, Imputation & Functional Statistics Bindings** - Spline/interpolation `_with_policy` + `ExtrapolationPolicy`, `impute_missing_values` + `ImputationMethod`, `functional_variance/std/covariance`, `depth_based_median`, `trim_mean`; `fd.interpolate()`/`fd.impute()` methods; multi-curve round-trip transposition tests. Parallel-eligible with Phase 27.
- [ ] **Phase 27: Scoring Metrics & Alignment/Registration Bindings** - `functional_mae/mse/mape/msle/explained_variance`; `least_squares_shift_registration` (+ result dict); registration-quality scores; banded `*_with_band` elastic alignment. Parallel-eligible with Phase 26.
- [ ] **Phase 28: Advisor Extension** - `scoring` diagnostics method + imputation-quality on `represent` + registration-quality on `alignment`, MCP guard-sync updated in one atomic commit; grounding invariant preserved; offline determinism tests. Depends on Phases 26 + 27.
- [ ] **Phase 29: Docs — Diagrams & Worked Examples** - New/updated inline SVG concept diagrams + runnable offline worked examples across `represent/`, `analyze/`, `align/` (and advisor pages); `mkdocs build --strict` green. Last.

### Phase Details

### Phase 25: Crate Bump + Regression Gate

**Goal**: The pinned `fdars-core` is upgraded to 0.17.0 and the entire existing binding + advisor suite proves green on the new engine, isolating the sole numeric behavior change (faer FPCA SVD drift) before any new binding work begins.
**Depends on**: Nothing (first phase of v4.0; builds on shipped v3.0)
**Requirements**: DEP-01, DEP-02
**Success Criteria** (what must be TRUE):

  1. `Cargo.toml` pins `fdars-core = "0.17.0"` with the `parallel` feature retained and the `linalg` feature NOT enabled (MSRV 1.83 preserved); `Cargo.lock` is regenerated and committed, and `maturin develop` builds the extension green.
  2. The full existing binding + advisor test suite passes against 0.17.0, with FPCA-related tolerances relaxed so results are equivalent within `1e-8·σ₁` and no exact-equality FPCA test or doc fence breaks on the faer SVD drift.
  3. No existing binding signature or public behavior changes — the additive/non-breaking 0.15→0.17 diff is confirmed against the live suite, not assumed.

**Plans**: 1 plan

- [x] 25-01-PLAN.md — Bump fdars-core 0.14.0→0.17.0, regenerate Cargo.lock, maturin build, full suite green with minimally-scoped FPCA tolerance relaxations (DEP-01, DEP-02)

### Phase 26: Interpolation, Imputation & Functional Statistics Bindings

**Goal**: Users can spline-interpolate onto off-grid points with a chosen extrapolation policy, impute missing values on a regular grid, and compute functional variance/std/covariance plus depth-based median and trimmed mean — all layout-correct across the numpy↔FdMatrix boundary.
**Depends on**: Phase 25
**Requirements**: REPR-01, REPR-02, REPR-03, STAT-01, STAT-02
**Success Criteria** (what must be TRUE):

  1. User can spline-interpolate functional data onto arbitrary off-grid query points via `spline_interpolate` / `spline_interpolate_with_policy`, and select an `ExtrapolationPolicy` (Boundary / Exception / Fill(value) / Periodic) passed as a string with a forward-compatible fallback arm for out-of-domain queries.
  2. User can impute missing values on a regular grid with `impute_missing_values` (`ImputationMethod` Linear / Mean / Constant), and both interpolation and imputation are reachable as `Fdata` methods (`fd.interpolate()`, `fd.impute()`).
  3. User can compute `functional_variance`, `functional_std`, and `functional_covariance`, and the matrix-returning covariance is proven layout-correct by a multi-curve round-trip test (guards the column-major #33 transposition bug class — shape/symmetry checks alone are insufficient).
  4. User can compute `depth_based_median` — the binding resolves the returned `usize` index to the actual median curve, never a bare integer — and `trim_mean` (α=0 reproducing the mean).

**Plans**: 2 plans

- [ ] 26-01-PLAN.md — New `fdars.represent` submodule: `spline_interpolate` (tracer, end-to-end) + `spline_interpolate_with_policy`/`fdata_interpolate_with_policy` (ExtrapolationPolicy string enum) + `impute_missing_values` (ImputationMethod) + `fd.interpolate()`/`fd.impute()` methods; multi-curve transposition round-trip test (REPR-01, REPR-02, REPR-03)
- [ ] 26-02-PLAN.md — Functional statistics in `fdars.fdata`: `functional_variance`/`functional_std`/`functional_covariance` (m×m round-trip test) + `depth_based_median` (index→curve) + `trim_mean` (α=0==mean) + `fd.var()`/`fd.std()`/`fd.cov()`/`fd.median()` methods (STAT-01, STAT-02)

**UI hint**: yes

### Phase 27: Scoring Metrics & Alignment/Registration Bindings

**Goal**: Users can score functional predictions with five error metrics and run least-squares shift registration, registration-quality scoring, and banded elastic alignment — with every fallible input surfacing as a clean `ValueError` rather than a Rust panic.
**Depends on**: Phase 25
**Requirements**: STAT-03, ALGN-01, ALGN-02, ALGN-03
**Success Criteria** (what must be TRUE):

  1. User can score functional predictions with `functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, and `functional_explained_variance`; fallible inputs (MAPE near-zero truths, MSLE values ≤ −1) surface as `ValueError` via `to_pyresult()` with no `.unwrap()` panics.
  2. User can run `least_squares_shift_registration` and receive the registered curves plus per-curve shifts, with `ShiftRegistrationResult` marshalled as a dict.
  3. User can score registration quality with `least_squares_score`, `pairwise_correlation_score`, and `sobolev_least_squares_score`, and the Sobolev score's uniform-grid requirement is surfaced clearly (not a silent wrong answer).
  4. User can run banded elastic alignment (`karcher_mean_with_band`, `elastic_self_distance_matrix_with_band`, `elastic_cross_distance_matrix_with_band`) with an optional `band_frac` where `None` means unbanded, and the banded distance matrices are proven layout-correct by a multi-curve round-trip test.

**Plans**: TBD
**UI hint**: yes

### Phase 28: Advisor Extension (grounding-invariant preserved)

**Goal**: The v3.0 advisor covers the relevant new capabilities — a `scoring` diagnostics method, imputation-quality on `represent`, registration-quality on `alignment` — with every new diagnostic fdars-computed and citing a real number, and the MCP guard-sync kept green.
**Depends on**: Phase 26, Phase 27
**Requirements**: ADV-01, ADV-02
**Success Criteria** (what must be TRUE):

  1. `scoring` is added as a diagnostics method wired simultaneously into `build_diagnostics`, the advisor `_supported` set, and the MCP `_DIAGNOSTICS_METHODS` guard in a single atomic commit, so `test_diagnostics_methods_match_advisor_supported` stays green and `_RUNNABLE_METHODS` is unchanged.
  2. Imputation-quality diagnostics extend the `represent` aspect and registration-quality diagnostics extend the `alignment` aspect, and each new diagnostic calls a bound fdars function (never Python math) and cites a real computed number — the grounding invariant is preserved.
  3. New offline determinism tests prove each new aspect/method produces byte-identical JSON-serialisable output for the same input (no numpy scalars, no network).

**Plans**: TBD

### Phase 29: Docs — Diagrams & Worked Examples

**Goal**: The published site documents every new capability to the project's method-accurate standard — new/updated hand-authored inline SVG diagrams and runnable offline worked examples across `represent/`, `analyze/`, `align/` and the advisor pages — with the full strict build green against the real shipped bindings.
**Depends on**: Phase 28
**Requirements**: DOCS-01, DOCS-02, DOCS-03
**Success Criteria** (what must be TRUE):

  1. New/updated hand-authored inline SVG concept diagrams for the new methods exist across `represent/`, `analyze/`, and `align/`, each method-accurate (human PNG review) and passing the SVGO idempotence + build-determinism gates.
  2. Runnable offline worked examples for the new capabilities run against existing `docs/data/` datasets; every executed `markdown-exec` fence stays network-free and deterministic (fixed seeds, base extras only) and emits the `FDARS_FENCE_OK` sentinel.
  3. The AI Advisor docs section is updated for the new scoring / registration-quality / imputation coverage, and full `mkdocs build --strict` passes offline against the current implementation.

**Plans**: TBD
**UI hint**: yes

### Progress

**Execution Order:**
Phases execute in numeric order: 25 → 26 ∥ 27 → 28 → 29 (26 and 27 are parallel-eligible after 25).

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 25. Crate Bump + Regression Gate | 1/1 | Complete    | 2026-08-14 |
| 26. Interpolation, Imputation & Functional Statistics Bindings | 0/2 | Not started | - |
| 27. Scoring Metrics & Alignment/Registration Bindings | 0/TBD | Not started | - |
| 28. Advisor Extension | 0/TBD | Not started | - |
| 29. Docs — Diagrams & Worked Examples | 0/TBD | Not started | - |

</details>

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md`, `v2.0-ROADMAP.md`, `v2.1-ROADMAP.md`, `v3.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1,3.0}-phases/`._
