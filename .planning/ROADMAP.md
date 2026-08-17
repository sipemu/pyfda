# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (shipped 2026-08-17)
- 🚧 **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** — Phases 30–35 (in progress)

## Phases

<details>
<summary>✅ v1.0 Documentation Overhaul (Phases 1–9) — SHIPPED 2026-08-08</summary>

Reworked the MkDocs site's hand-authored SVG diagrams and worked example pages to a consistently high, method-accurate standard, on top of new style/determinism/doc-test guardrails. Full detail: `.planning/milestones/v1.0-ROADMAP.md`.

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

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout (fdars computes the numbers; the LLM only interprets and cites them). Full detail: `.planning/milestones/v2.0-ROADMAP.md`.

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

Made the fdars AI advisor work with any LLM backend (Anthropic, OpenAI/OpenAI-compatible, Google Gemini, local Ollama) through a custom `Provider` protocol, and gave every fdars analysis aspect its own advisor (diagnostics + grounded task families) — with the grounding invariant preserved on every backend. 28/28 requirements complete; suite 259 passed / 4 skipped. Full detail: `.planning/milestones/v3.0-ROADMAP.md`.

- [x] Phase 19: Provider Foundation & Grounding Contract — `Provider` protocol + Anthropic refactor + validate-and-retry + centralized `_check_grounding` (completed 2026-08-12)
- [x] Phase 20: Additional Provider Adapters — OpenAI (+ `base_url`), Ollama (local, no key), Gemini adapters as optional extras (completed 2026-08-12)
- [x] Phase 21: Per-Aspect Advisor Coverage — `build_diagnostics` + three grounded task families for all 12 fdars aspects via one shared schema/prompt (completed 2026-08-12)
- [x] Phase 22: Surface Integration — MCP exposes new aspect diagnostics (LLM-free); provider selection via Python `advise()`; Agent Skill documents coverage (completed 2026-08-12)
- [x] Phase 23: Packaging & CI — Python 3.9–3.14 matrix with version-gated extras + bare-venv smoke + aspect × provider offline grounding matrix (completed 2026-08-12)
- [x] Phase 24: Documentation — provider setup guide + per-aspect coverage page + updated overview/API pages; `mkdocs build --strict` offline (completed 2026-08-12)

</details>

<details>
<summary>✅ v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Phases 25–29) — SHIPPED 2026-08-17</summary>

Upgraded `fdars-core` 0.14.0 → 0.17.0 and exposed the new upstream functional-data capabilities (interpolation/imputation, functional statistics/scoring, shift registration/registration-quality/banded elastic alignment) through PyO3 bindings + the Python API, extended the v3.0 AI advisor to cover the relevant new capabilities (grounding invariant preserved), and documented everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Dependency-ordered: crate bump + regression gate first; two independent binding groups (parallel-eligible); advisor on top; docs last. 16/16 requirements complete; suite 426 passed / 4 skipped; whole-site `mkdocs build --strict` green offline. Full detail: `.planning/milestones/v4.0-ROADMAP.md`.

- [x] Phase 25: Crate Bump + Regression Gate — 0.17.0 pinned (parallel-only, no linalg), suite green, zero FPCA tolerance changes (completed 2026-08-14)
- [x] Phase 26: Interpolation, Imputation & Functional Statistics Bindings — `fdars.represent` + `fdars.fdata` stats + 6 Fdata methods; multi-curve transposition-tested (completed 2026-08-15)
- [x] Phase 27: Scoring Metrics & Alignment/Registration Bindings — `fdars.scoring` + shift registration (+ `fd.shift_register()`) + 3 quality scores + banded elastic alignment (completed 2026-08-15)
- [x] Phase 28: Advisor Extension — `scoring` aspect #13 + imputation-quality (represent) + registration-quality (alignment); grounding invariant + MCP guard-sync preserved (completed 2026-08-16)
- [x] Phase 29: Docs — Diagrams & Worked Examples — 6 new pages + 6 method-accurate hand-authored SVGs + offline FDARS_FENCE_OK worked examples; whole-site strict build green (completed 2026-08-17)

</details>

### 🚧 v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Phases 30–35)

Upgrade the pinned `fdars-core` 0.17.0 → 0.20.0 (parallel-only, no `linalg`) and expose the new upstream functional-inference + depth/boxplot + basis/smoothing surface through PyO3 bindings + the Python API, extend the v3.0 grounded advisor with an inference diagnostics aspect (grounding invariant preserved), and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Same shape as v4.0: crate bump + regression gate first (BLOCKS everything), three independent binding groups (parallel-eligible after the bump), advisor on top (needs the inference bindings), docs last (run against the real shipped bindings).

- [x] **Phase 30: Crate Bump + Regression Gate** - Bump 0.17→0.20, add the `CvCriterion` wildcard fallback arm, full ~426-test suite green as the sole gate (completed 2026-08-17)
- [x] **Phase 31: Group A — `fdars.inference` Bindings** - New submodule: two-sample permutation tests + SCB bands + FLM inference + one-way ANOVA V-stat (`TestResult`/`ToleranceBand` → PyDict, deterministic seed) (completed 2026-08-17)
- [x] **Phase 32: Group B — Depth/Boxplot Bindings** - `functional_depth` unified dispatcher + `functional_boxplot` extending `fdars.depth` (completed 2026-08-17)
- [x] **Phase 33: Group C — Basis/Smoothing Quick Wins** - `constant_basis` + AIC basis/kernel selection extending `fdars.basis`/`fdars.smoothing` (completed 2026-08-17)
- [x] **Phase 34: Advisor Extension** - `inference` diagnostics aspect; grounding invariant + MCP `_DIAGNOSTICS_METHODS` guard-sync (single atomic commit) preserved (completed 2026-08-17)
- [ ] **Phase 35: Docs — Diagrams & Worked Examples** - New pages + method-accurate hand-authored SVGs + runnable offline `FDARS_FENCE_OK` examples; `mkdocs build --strict` green

## Phase Details (v5.0)

### Phase 30: Crate Bump + Regression Gate

**Goal**: `fdars-core` is pinned at 0.20.0 and the entire existing binding + advisor suite still passes, on a green baseline, before any new binding work begins.
**Depends on**: Nothing (first phase of v5.0; continues from v4.0 Phase 29)
**Requirements**: DEP-03, DEP-04
**Success Criteria** (what must be TRUE):

  1. `Cargo.toml` pins `fdars-core = { version = "0.20.0", features = ["parallel"] }` (no `linalg`) and `maturin develop` builds green.
  2. The existing `optim_bandwidth` binding compiles against 0.20.0's now-`#[non_exhaustive]` `CvCriterion` because a wildcard `_ => PyValueError` fallback arm was added — the crate does NOT compile without it.
  3. The full existing binding + advisor suite (~426 tests) passes unchanged — no new tests, no tolerance relaxations — as the sole success criterion.
  4. The bump lands as an isolated commit before any new-binding work, so any downstream binding issue cannot hide behind an upgrade regression.

**Plans**: 1 plan

- [x] 30-01-PLAN.md — Bump fdars-core 0.17→0.20 + CvCriterion #[non_exhaustive] wildcard fix + full ~426-test regression gate green

### Phase 31: Group A — `fdars.inference` Bindings

**Goal**: Users can run the full functional-inference surface (two-sample tests, simultaneous confidence bands, FLM post-hoc inference, one-way ANOVA V-statistic) from a new, importable `fdars.inference` submodule with deterministic, reproducible results.
**Depends on**: Phase 30
**Requirements**: INFER-01, INFER-02, INFER-03, INFER-04, INFER-05, INFER-06, INFER-07, INFER-08, INFER-09
**Success Criteria** (what must be TRUE):

  1. User can run `t_perm_test` and `f_perm_test` (two-sample integrated-L2/-F permutation tests) and `two_sample_mean_test` (asymptotic Hotelling T² on a shared FPC basis), each returning a `{statistic, p_value, n_perm}` dict.
  2. User can compute a Degras simultaneous confidence band via `mean_scb` → `{lower, upper, center, half_width}` dict and run `scb_two_sample_test` on the mean-difference curve → `TestResult` dict, with the `multiplier` selected by string and a `ValueError` fallback for unknown values.
  3. User can run `flm_f_test` and `flm_gof_test` on a functional linear model (the wrapper re-fits `fregre_lm` internally from raw data/response/n_comp — no persistent handle) and `oneway_anova_vstat` for a grouped asymptotic ANOVA V-statistic, each returning a dict.
  4. The `fdars.inference` submodule is registered (`src/inference_mod.rs` + `register_submodule!` in `lib.rs` + `_submodule_names`) and importable both as `fdars.inference.fn` and `from fdars.inference import fn`; all `seed=None` params resolve to a fixed default for byte-identical reproducibility across two calls.
  5. Degenerate inputs (mismatched grids, too few curves, invalid params) raise `ValueError` — no `.unwrap()`, all fallible functions routed through `to_pyresult()`.

**Plans**: 3 plans

- [x] 31-01-PLAN.md — Submodule scaffold + verification spike (all 8 signatures) + end-to-end tracer (t_perm_test) + f_perm_test + two_sample_mean_test (INFER-01/02/03/09)
- [x] 31-02-PLAN.md — Degras SCB bands: mean_scb (ToleranceBand → dict) + scb_two_sample_test; string multiplier + ValueError fallback (INFER-04/05)
- [x] 31-03-PLAN.md — FLM re-fit inference (flm_f_test + flm_gof_test) + oneway_anova_vstat (0-indexed groups) (INFER-06/07/08)

### Phase 32: Group B — Depth/Boxplot Bindings

**Goal**: Users can compute unified functional self-depth and a López-Pintado–Romo functional boxplot (median / central region / whiskers / flagged outliers) from the extended `fdars.depth` submodule, layout-correct across the numpy↔FdMatrix boundary.
**Depends on**: Phase 30
**Requirements**: DEPTH-01, DEPTH-02
**Success Criteria** (what must be TRUE):

  1. User can call `fdars.depth.functional_depth(data, method="fraiman_muniz"|"band"|"modified_band"|"random_projection", **kwargs)` → `ndarray (n,)`, with `method` dispatched to a `DepthMethod` variant and a `#[non_exhaustive]` wildcard fallback raising `ValueError` on unknown methods.
  2. User can call `fdars.depth.functional_boxplot(data, method=..., factor=1.5, **kwargs)` → dict `{median, central_lower, central_upper, whisker_lower, whisker_upper, outliers, depths}` with band fields as 1-D arrays via the numpy conversion helper and `outliers` as a Python list of ints.
  3. A multi-curve transposition round-trip test guards the column-major layout of every `FdMatrix`-returning boxplot field (finite values, correct shapes) — no silent transposition.

**Plans**: 1 plan

- [x] 32-01-PLAN.md — functional_depth (string→DepthMethod dispatch) + functional_boxplot (7-key dict) extending fdars.depth, with layout round-trip guard

### Phase 33: Group C — Basis/Smoothing Quick Wins

**Goal**: Users can construct a constant intercept basis and select AIC-optimal basis/kernel smoothing parameters, via additive extensions to `fdars.basis` and `fdars.smoothing`.
**Depends on**: Phase 30
**Requirements**: BASIS-01, BASIS-02, BASIS-03
**Success Criteria** (what must be TRUE):

  1. User can call `fdars.basis.constant_basis(argvals)` → an all-ones intercept-column `ndarray` (exact signature/dimension confirmed at plan time).
  2. User can select an AIC-optimal basis roughness penalty via `fdars.smoothing.smooth_basis_aic(...)` → dict and pass `criterion="aic"` to `basis_nbasis_cv` (`BasisCriterion::Aic`).
  3. User can select an AIC-optimal kernel bandwidth via `aic_smoother` and/or `criterion="aic"` on the existing bandwidth-selection binding (`CvCriterion::Aic`), with the `CvCriterion` match carrying the forward-compatible `#[non_exhaustive]` fallback arm added in Phase 30.

**Plans**: 1 plan

- [x] 33-01-PLAN.md — constant_basis + smooth_basis_aic (basis_mod) + optim_bandwidth criterion="aic" output-arm fix (smoothing_mod) + basis_nbasis_cv "aic" test coverage (BASIS-01/02/03)

### Phase 34: Advisor Extension

**Goal**: The grounded advisor gains an `inference` diagnostics aspect that summarizes fdars-computed test statistics and p-values, with the grounding invariant and the advisor/MCP guard-sync preserved.
**Depends on**: Phase 31 (calls the inference bindings)
**Requirements**: ADV-03
**Success Criteria** (what must be TRUE):

  1. `build_diagnostics(test_result, method="inference")` produces a grounded diagnostics dict summarizing `TestResult` p-values/statistics — every value fdars-computed (no fabricated numbers), diagnostics-only (not added to `_RUNNABLE_METHODS`).
  2. The `build_diagnostics` dispatch + advisor `_supported` set + MCP `_DIAGNOSTICS_METHODS` change land in a SINGLE atomic commit, keeping `test_diagnostics_methods_match_advisor_supported` green.
  3. Offline determinism is preserved — no numpy scalars, byte-identical `json.dumps` output — and the grounding invariant holds (LLM only interprets and cites diagnostic values).

**Plans**: 1 plan

- [x] 34-01-PLAN.md — `inference` aspect builder + three-file guard-sync (advisor `_supported`/dispatch + MCP `_DIAGNOSTICS_METHODS` + `_ASPECT_PRIMERS`) in a single atomic commit + offline test suite (ADV-03)

**UI hint**: no

### Phase 35: Docs — Diagrams & Worked Examples

**Goal**: The published MkDocs site documents the new inference, functional-boxplot, and basis/smoothing capabilities to the project's method-accurate standard, with the whole site building strict-green offline against the real shipped bindings.
**Depends on**: Phase 31, Phase 32, Phase 33, Phase 34
**Requirements**: DOCS-04, DOCS-05, DOCS-06, DOCS-07
**Success Criteria** (what must be TRUE):

  1. New functional-inference page(s) cover two-sample tests, SCB bands, and functional ANOVA — each with a method-accurate hand-authored inline SVG and a runnable offline worked example emitting `FDARS_FENCE_OK` at small params (`n_perm=19`, SCB `nb=50`, synthetic/subset data).
  2. A new functional-boxplot page carries a method-accurate hand-authored SVG (central region / whiskers / median / flagged outliers) + a runnable offline worked example; the basis/smoothing additions (`constant_basis` + AIC selection) are documented with example(s) and the advisor `aspects.md` is updated to reflect the new `inference` aspect.
  3. All new pages are wired into `mkdocs.yml` nav and the whole-site `mkdocs build --strict` passes offline (exit 0); every new SVG is SVGO-idempotent and determinism-clean.
  4. A blocking human diagram method-accuracy review gate is satisfied before the milestone closes.

**Plans**: TBD
**UI hint**: yes

## Progress (v5.0)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 30. Crate Bump + Regression Gate | 0/1 | Not started | - |
| 31. Group A — `fdars.inference` Bindings | 0/3 | Not started | - |
| 32. Group B — Depth/Boxplot Bindings | 0/? | Not started | - |
| 33. Group C — Basis/Smoothing Quick Wins | 0/1 | Planned | - |
| 34. Advisor Extension | 0/1 | Planned | - |
| 35. Docs — Diagrams & Worked Examples | 0/? | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md`, `v2.0-ROADMAP.md`, `v2.1-ROADMAP.md`, `v3.0-ROADMAP.md`, `v4.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1,3.0,4.0}-phases/`._
