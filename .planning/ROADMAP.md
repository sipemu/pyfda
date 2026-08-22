# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (shipped 2026-08-17)
- ✅ **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** — Phases 30–35 (shipped 2026-08-18)
- ✅ **v6.0 — fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference** — Phases 36–41 (shipped 2026-08-22)
- 🚧 **v7.0 — Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth** — Phases 42–49 (in progress)

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

Upgraded `fdars-core` 0.14.0 → 0.17.0 and exposed the new upstream functional-data capabilities (interpolation/imputation, functional statistics/scoring, shift registration/registration-quality/banded elastic alignment) through PyO3 bindings + the Python API, extended the v3.0 AI advisor to cover the relevant new capabilities (grounding invariant preserved), and documented everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). 16/16 requirements complete; suite 426 passed / 4 skipped; whole-site `mkdocs build --strict` green offline. Full detail: `.planning/milestones/v4.0-ROADMAP.md`.

- [x] Phase 25: Crate Bump + Regression Gate — 0.17.0 pinned (parallel-only, no linalg), suite green, zero FPCA tolerance changes (completed 2026-08-14)
- [x] Phase 26: Interpolation, Imputation & Functional Statistics Bindings — `fdars.represent` + `fdars.fdata` stats + 6 Fdata methods; multi-curve transposition-tested (completed 2026-08-15)
- [x] Phase 27: Scoring Metrics & Alignment/Registration Bindings — `fdars.scoring` + shift registration (+ `fd.shift_register()`) + 3 quality scores + banded elastic alignment (completed 2026-08-15)
- [x] Phase 28: Advisor Extension — `scoring` aspect #13 + imputation-quality (represent) + registration-quality (alignment); grounding invariant + MCP guard-sync preserved (completed 2026-08-16)
- [x] Phase 29: Docs — Diagrams & Worked Examples — 6 new pages + 6 method-accurate hand-authored SVGs + offline FDARS_FENCE_OK worked examples; whole-site strict build green (completed 2026-08-17)

</details>

<details>
<summary>✅ v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Phases 30–35) — SHIPPED 2026-08-18</summary>

Upgraded `fdars-core` 0.17.0 → 0.20.0 (parallel-only, no `linalg`) and exposed the new upstream functional-inference + depth/boxplot + basis/smoothing surface through PyO3 bindings + the Python API — a new `fdars.inference` submodule (two-sample tests, Degras SCB bands, FLM post-hoc inference, one-way ANOVA V-statistic), `fdars.depth.functional_depth`/`functional_boxplot`, and `fdars.basis.constant_basis`/`smooth_basis_aic` + `optim_bandwidth(criterion="aic")` — extended the grounded advisor with an `inference` diagnostics aspect (#14; grounding invariant + guard-sync preserved), and documented it all to the method-accurate standard. 21/21 requirements complete; suite 560 passed / 4 skipped; whole-site `mkdocs build --strict` green offline. Full detail: `.planning/milestones/v5.0-ROADMAP.md`.

- [x] Phase 30: Crate Bump + Regression Gate — 0.20.0 pinned (parallel-only, no linalg) + `CvCriterion` wildcard arm; 426-test baseline green, zero drift (completed 2026-08-17)
- [x] Phase 31: Group A — `fdars.inference` Bindings — new submodule: two-sample permutation tests + SCB bands + FLM inference + ANOVA V-stat (`TestResult`/`ToleranceBand` → PyDict, deterministic seed) (completed 2026-08-17)
- [x] Phase 32: Group B — Depth/Boxplot Bindings — `functional_depth` dispatcher + `functional_boxplot` (7-key dict, transposition-guarded) extending `fdars.depth` (completed 2026-08-17)
- [x] Phase 33: Group C — Basis/Smoothing Quick Wins — `constant_basis` + `smooth_basis_aic` + `optim_bandwidth(criterion="aic")` (Phase-30 stopgap fixed) (completed 2026-08-17)
- [x] Phase 34: Advisor Extension — `inference` diagnostics aspect (#14); grounding invariant + MCP guard-sync (single atomic commit) preserved (completed 2026-08-17)
- [x] Phase 35: Docs — Diagrams & Worked Examples — new Inference section + boxplot page + basis/smoothing fold-ins + aspects.md; 4 method-accurate hand-authored SVGs; whole-site strict build green; human review approved (completed 2026-08-18)

</details>

<details>
<summary>✅ v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (Phases 36–41) — SHIPPED 2026-08-22</summary>

Upgraded `fdars-core` 0.20.0 → 0.23.0 (parallel-only, no `linalg`; MSRV verified 1.81 ≤ 1.83) and exposed the new upstream surface through PyO3 bindings + the Python API across three independent capability groups — Group A Regression (`concurrent_regression` + `functional_glm`), Group B FPCA & Classification (`pace_fpca` over a new sparse/irregular `IrregFdata` input + `elastic_multinomial`), Group C Depth/Outliers/Interval-Inference (9 new depth methods + 4 outlier detectors + 3 interval-wise ITP tests) — extended the grounded advisor's `outliers` and `regression` aspects (closing the v5.0 Phase-34 boxplot-outlier deferral; grounding invariant + MCP guard-sync preserved), and documented everything to the method-accurate standard (new pages + hand-authored inline SVGs + offline `FDARS_FENCE_OK` worked examples; blocking human diagram review, which caught and corrected an inverted hypograph/epigraph asymmetry). 23/23 requirements complete; suite 772 passed / 4 skipped; whole-site `mkdocs build --strict` green offline. Full detail: `.planning/milestones/v6.0-ROADMAP.md`.

- [x] Phase 36: Crate Bump + Regression Gate — 0.23.0 pinned (parallel-only, no linalg), wildcard fallback arms for newly-`#[non_exhaustive]` upstream enums, ~560-test suite green as the sole gate; isolated bump commit (completed 2026-08-20)
- [x] Phase 37: Group A — Regression Bindings — `concurrent_regression` (`beta_curve` `(p,m)` transposition-guarded) + `functional_glm` (`GlmFamily` string dispatch, re-fits FPCA internally; Gamma inverse-link + AIC caveat) extending `fdars.regression` (completed 2026-08-20)
- [x] Phase 38: Group B — FPCA & Classification Bindings — new `src/pace_fpca_mod.rs`: `IrregFdata` lists-of-arrays builder + `pace_fpca`; `elastic_multinomial` (CR-01 label guard) extending `fdars.classification` (completed 2026-08-21)
- [x] Phase 39: Group C — Depth/Outliers/Interval-Inference Bindings — 9 new `DepthMethod` variants + 4 outlier detectors (`tvdmss`/`muod`/`sequential_transform_outliers`/`depthgram`) + 3 ITP tests (`itp_one_pop`/`itp_two_pop`/`itp_flm`) with a new `itp_result_to_pydict` (completed 2026-08-21)
- [x] Phase 40: Advisor Extension — extended the `outliers` aspect (new detector scalars; closes the Phase-34 deferral) + `regression` aspect (GLM deviance/AIC, concurrent fit summary) + Group B (`elastic_multinomial` `train_accuracy`, `pace_fpca` variance-explained); grounding invariant + guard-sync preserved (completed 2026-08-21)
- [x] Phase 41: Docs — Diagrams & Worked Examples — new Regression / PACE-FPCA + elastic-multinomial / depth-outliers-inference pages + 6 method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples; advisor aspects.md update; whole-site `mkdocs build --strict` green; blocking human diagram review (caught + fixed inverted hypograph/epigraph asymmetry) (completed 2026-08-22)

</details>

### 🚧 v7.0 Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth (In Progress)

**Milestone Goal:** Bring the whole docs site to one consistently high, method-accurate bar — audit and fix every hand-authored inline SVG concept diagram on four axes, add concept diagrams to the pages that still lack them (examples + advisor surface pages), and extend the thin v4–v6 method pages to full parity with the mature ones. Docs-only quality milestone (no crate bump, no new bindings, no advisor logic change); closest in spirit to the v1.0 overhaul. Same shape: audit → SVG fixes batched by section → new diagrams → page depth → build/review gate.

**Standing constraints every phase inherits:** diagrams stay hand-authored inline SVG; the SVGO idempotence + build-determinism CI gate must stay green; worked-example fences run OFFLINE against the current `fdars` API emitting `FDARS_FENCE_OK` with small data (synthetic `n ≤ 20` / subsampled datasets); the whole-site `mkdocs build --strict` must be green offline; docs phases run sequentially on `main` (NOT in worktrees — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path); a per-section review gate on the built site; a BLOCKING human diagram method-accuracy review before milestone close (the v6.0 hypograph/epigraph lesson).

- [x] **Phase 42: Diagram Audit** - Score all concept diagrams on the four fix axes → ranked per-section fix list; confirm coverage-gap + thin-page lists (completed 2026-08-22)
- [x] **Phase 43: SVG Fix — learn / represent / align** - Correct that batch on all four axes; per-section built-site review (completed 2026-08-22)
- [x] **Phase 44: SVG Fix — analyze / monitoring / advisor** - Correct that batch on all four axes; per-section built-site review (completed 2026-08-22)
- [x] **Phase 45: SVG Fix — regression / inference** - Correct that batch on all four axes; per-section built-site review (completed 2026-08-22)
- [x] **Phase 46: Diagram Coverage — examples pages** - Add a method-accurate concept SVG to each `examples/` worked-example page (completed 2026-08-22)
- [ ] **Phase 47: Diagram Coverage — advisor surface pages** - Add a method-accurate concept SVG to each of the 5 advisor surface pages
- [ ] **Phase 48: Page Depth** - Extend thin v4–v6 method pages to mature structure + new offline worked examples/cross-links
- [ ] **Phase 49: Whole-Site Gate & Human Review** - `mkdocs build --strict` green offline; per-section review + blocking human diagram method-accuracy review before close

## Phase Details

### Phase 42: Diagram Audit

**Goal**: A ranked, per-section diagram fix list — every concept diagram in `docs/assets/diagrams/` scored on the four fix axes — plus a confirmed diagram-coverage gap list and thin-page extension list, so the downstream fix/coverage/depth phases execute against evidence rather than guesswork.
**Depends on**: Nothing (first phase of milestone; gates all downstream v7.0 work)
**Requirements**: AUDIT-01
**Success Criteria** (what must be TRUE):

  1. The audit report inventories every concept diagram in `docs/assets/diagrams/` (cards/ and thumb/ excluded), each scored on all four axes — visual/layout quality, STYLE_SPEC conformance, XML source formatting, and method-accuracy against the shipped `fdars` bindings.
  2. The report groups findings into a ranked, per-section fix list aligned to the docs sections (learn, represent, align, analyze, monitoring, advisor, regression, inference) so each downstream fix phase has an explicit, evidence-backed worklist.
  3. The report confirms which `docs/examples/*.md` pages and which of the 5 advisor surface pages lack a concept SVG (the DIACOV coverage gap).
  4. The report confirms the thin-page extension list — the sub-mature v4–v6 method pages that DEPTH-01/02 must bring to full structure.

**Plans**: 1/1 plans executed

- [x] 42-01-PLAN.md — Inventory + 4-axis score all 61 concept diagrams (visual/STYLE_SPEC/XML/method-accuracy), reconcile count, derive ranked per-section fix list (43/44/45), coverage-gap list, and thin-page list → 42-AUDIT.md

**UI hint**: yes

### Phase 43: SVG Fix — learn / represent / align

**Goal**: Every concept diagram in the learn, represent, and align sections is corrected on all four fix axes and verified on the built site, so this batch meets the consistently-high, method-accurate bar.
**Depends on**: Phase 42
**Requirements**: SVGFIX-01, SVGFIX-02, SVGFIX-03, SVGFIX-04 (learn/represent/align batch)
**Success Criteria** (what must be TRUE):

  1. Every flagged diagram in learn/represent/align renders on the built site with no overlapping labels and consistent spacing, alignment, and sizing (rendered PNG check).
  2. Every diagram in this batch conforms to `STYLE_SPEC.md` — palette, system-ui fonts, `viewBox`, the `.ttl/.sub/.lab/.sm/.mono` CSS classes, and `role="img"` + `aria-label`.
  3. Every diagram in this batch is method-accurate against the shipped `fdars` bindings — no diagram misdepicts what its method does.
  4. This batch's XML source is clean and hand-editable and passes the SVGO idempotence + build-determinism CI gate (byte-identical rebuilds).
  5. Each section in the batch passes a review on the built site before the batch is considered done.

**Plans**: 1/1 plans executed

Plans:

- [x] 43-01-PLAN.md — Correct all 12 flagged learn/represent/align SVGs on the four fix axes (tracer smoothing.svg → represent/ XML+subtitle batch → align/ + ex-sonar STYLE_SPEC migration); per-diagram SVGO idempotence + per-section PNG review; one commit per section

**UI hint**: yes

### Phase 44: SVG Fix — analyze / monitoring / advisor

**Goal**: Every concept diagram in the analyze, monitoring, and advisor sections is corrected on all four fix axes and verified on the built site.
**Depends on**: Phase 43
**Requirements**: SVGFIX-01, SVGFIX-02, SVGFIX-03, SVGFIX-04 (analyze/monitoring/advisor batch)
**Success Criteria** (what must be TRUE):

  1. Every flagged diagram in analyze/monitoring/advisor renders on the built site with no overlapping labels and consistent spacing, alignment, and sizing (rendered PNG check).
  2. Every diagram in this batch conforms to `STYLE_SPEC.md` (palette, fonts, `viewBox`, CSS classes, `role="img"` + `aria-label`).
  3. Every diagram in this batch is method-accurate against the shipped `fdars` bindings.
  4. This batch's XML source is clean and hand-editable and passes the SVGO idempotence + build-determinism CI gate.
  5. Each section in the batch passes a built-site review before the batch is considered done.

**Plans**: 1/1 plans executed

- [x] 44-01-PLAN.md — correct the 6 flagged analyze/ diagrams (outlier-detection method-accuracy + bottom-row overflow, scoring-metrics label re-spacing, redundant-override cleanup); monitoring/ + advisor/ have no flagged diagrams

**UI hint**: yes

### Phase 45: SVG Fix — regression / inference

**Goal**: Every concept diagram in the regression and inference sections is corrected on all four fix axes and verified on the built site, completing the full-set SVG fix sweep across all concept diagrams.
**Depends on**: Phase 44
**Requirements**: SVGFIX-01, SVGFIX-02, SVGFIX-03, SVGFIX-04 (regression/inference batch)
**Success Criteria** (what must be TRUE):

  1. Every flagged diagram in regression/inference renders on the built site with no overlapping labels and consistent spacing, alignment, and sizing (rendered PNG check).
  2. Every diagram in this batch conforms to `STYLE_SPEC.md` (palette, fonts, `viewBox`, CSS classes, `role="img"` + `aria-label`).
  3. Every diagram in this batch is method-accurate against the shipped `fdars` bindings (special care on the depth/interval-inference diagrams per the v6.0 hypograph/epigraph lesson).
  4. This batch's XML source is clean and hand-editable and passes the SVGO idempotence + build-determinism CI gate.
  5. Across Phases 43–45, all concept diagrams on the AUDIT-01 fix list have been corrected — no flagged diagram remains unaddressed.

**Plans**: 1/1 plans executed

- [x] 45-01-PLAN.md — Correct the 4 flagged regression/inference diagrams on all four fix axes (functional-glm Gamma-link verified, elastic-multinomial de-cramp, scalar-on-function β(t), permutation-test XML); 15 OK diagrams byte-unchanged

**UI hint**: yes

### Phase 46: Diagram Coverage — examples pages

**Goal**: Each `docs/examples/*.md` worked-example page carries a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG wired into the page, closing the examples half of the coverage gap.
**Depends on**: Phase 42
**Requirements**: DIACOV-01
**Success Criteria** (what must be TRUE):

  1. Every `docs/examples/*.md` page identified by the AUDIT-01 gap list now references a hand-authored inline concept SVG that renders on the built site.
  2. Each new example-page diagram is method-accurate against what that example demonstrates and conforms to `STYLE_SPEC.md` (palette, fonts, `viewBox`, CSS classes, `role="img"` + `aria-label`).
  3. Each new SVG passes the SVGO idempotence + build-determinism CI gate (byte-identical rebuilds).
  4. Each affected examples page passes a built-site review.

**Plans**: 2/2 plans executed

- [x] 46-01-PLAN.md — Tracer (ex-canadian-weather) + canadian & andrews-wine families (9 diagrams)
- [x] 46-02-PLAN.md — Tecator + monitoring + misc groups (11 diagrams)

**UI hint**: yes

### Phase 47: Diagram Coverage — advisor surface pages

**Goal**: Each of the 5 advisor surface pages (`python-api`, `mcp`, `providers`, `agent-skill`, `aspects`) carries a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG, reversing the v2.1 choice to leave those pages diagram-free.
**Depends on**: Phase 42
**Requirements**: DIACOV-02
**Success Criteria** (what must be TRUE):

  1. Each of the 5 advisor surface pages now references a hand-authored inline concept SVG that renders on the built site.
  2. Each new advisor-page diagram is method-accurate against the shipped advisor surface it depicts (`python/fdars/advisor/`, `python/fdars/mcp/`, `.claude/skills/fdars-advisor/`) and preserves the grounding-invariant framing where relevant.
  3. Each new SVG conforms to `STYLE_SPEC.md` and passes the SVGO idempotence + build-determinism CI gate.
  4. Each affected advisor page passes a built-site review.

**Plans**: 1 plan

- [ ] 47-01-PLAN.md — Author 5 method-accurate STYLE_SPEC advisor concept SVGs (python-api, mcp, providers, agent-skill, aspects) tracer-first + embed each; mcp/python-api provably LLM-free

**UI hint**: yes

### Phase 48: Page Depth

**Goal**: The thin v4–v6 method pages are extended to the mature-page structure (intro, method explanation, worked example, parameters, caveats/interpretation) with new offline worked examples and cross-links where they add value, so page depth is consistent across the site.
**Depends on**: Phase 42
**Requirements**: DEPTH-01, DEPTH-02, DEPTH-03
**Success Criteria** (what must be TRUE):

  1. The thin v6.0 method pages (`regression/concurrent-regression`, `regression/functional-glm`, `represent/pace-fpca`, `inference/interval-inference`) each follow the mature structure — intro, method explanation, worked example, parameters, caveats/interpretation.
  2. The thin v4/v5 method pages (`represent/interpolation`, `represent/imputation`, `analyze/scoring-metrics`, `analyze/functional-statistics`, plus any other sub-~200-line method page surfaced by AUDIT-01) each follow the mature structure.
  3. Extended pages gain new worked examples and/or cross-links where they add value, and every worked example runs offline against the current `fdars` API emitting `FDARS_FENCE_OK`, with fence data kept small (synthetic `n ≤ 20`; subsampled datasets).
  4. Each extended page passes a built-site review.

**Plans**: TBD
**UI hint**: yes

### Phase 49: Whole-Site Gate & Human Review

**Goal**: The whole documentation site passes its final quality gate — a green offline `mkdocs build --strict`, a per-section built-site review, and a blocking human diagram method-accuracy review before milestone close — so the site is shippable at the consistently-high bar.
**Depends on**: Phase 43, Phase 44, Phase 45, Phase 46, Phase 47, Phase 48
**Requirements**: GATE-01, GATE-02
**Success Criteria** (what must be TRUE):

  1. Whole-site `mkdocs build --strict` exits 0 offline after all changes, with every worked-example fence emitting `FDARS_FENCE_OK`.
  2. The SVGO idempotence + build-determinism CI gate is green across all changed and added diagrams.
  3. A per-section review has been held on the built site across all touched sections.
  4. A blocking human diagram method-accuracy review passes — no diagram misdepicts its method — before the milestone is closed.

**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 42 → 43 → 44 → 45 → 46 → 47 → 48 → 49

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 42. Diagram Audit | v7.0 | 1/1 | Complete    | 2026-08-22 |
| 43. SVG Fix — learn/represent/align | v7.0 | 1/1 | Complete    | 2026-08-22 |
| 44. SVG Fix — analyze/monitoring/advisor | v7.0 | 1/1 | Complete    | 2026-08-22 |
| 45. SVG Fix — regression/inference | v7.0 | 1/1 | Complete    | 2026-08-22 |
| 46. Diagram Coverage — examples | v7.0 | 2/2 | Complete    | 2026-08-22 |
| 47. Diagram Coverage — advisor | v7.0 | 0/TBD | Not started | - |
| 48. Page Depth | v7.0 | 0/TBD | Not started | - |
| 49. Whole-Site Gate & Human Review | v7.0 | 0/TBD | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v6.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{1.0,2.0,2.1,3.0,4.0,5.0,6.0}-phases/`._
