# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- ✅ **v2.1 — Document the AI Advisor** — Phases 14–18 (shipped 2026-08-11)
- ✅ **v3.0 — Provider-Agnostic Advisor, Full-Library Coverage** — Phases 19–24 (shipped 2026-08-12)
- ✅ **v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs** — Phases 25–29 (shipped 2026-08-17)
- ✅ **v5.0 — fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing** — Phases 30–35 (shipped 2026-08-18)
- ✅ **v6.0 — fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference** — Phases 36–41 (shipped 2026-08-22)
- ✅ **v7.0 — Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth** — Phases 42–49 (shipped 2026-08-23)
- ✅ **v8.0 — Advisor: New Capabilities** — Phases 50–54 (shipped 2026-08-31)
- ✅ **v9.0 — scikit-learn API Compatibility** — Phases 55–59 (shipped 2026-09-02)
- ✅ **v10.0 — Diagram Quality & Accessibility Pass** — Phases 60–65 (shipped 2026-09-02)
- ✅ **v11.0 — fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs** — Phases 66–73 (shipped 2026-09-05)
- ✅ **v12.0 — Docs Depth, Card Coverage & AI Capability Skill** — Phases 74–79 (shipped 2026-09-06)
- 🚧 **v13.0 — Scientific Provenance & Cross-Language Implementations** — Phases 80–84 (in progress)

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

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout. Full detail: `.planning/milestones/v2.0-ROADMAP.md`.

- [x] Phase 10: Advisor Core Primitive (completed 2026-08-09)
- [x] Phase 11: Python API Surface (completed 2026-08-09)
- [x] Phase 12: Tool / MCP Surface (completed 2026-08-09)
- [x] Phase 13: Agent Skill Surface (completed 2026-08-10)

</details>

<details>
<summary>✅ v2.1 Document the AI Advisor (Phases 14–18) — SHIPPED 2026-08-11</summary>

Gave the published MkDocs site a first-class, method-accurate "AI Advisor" section documenting the shipped v2.0 grounded advisor. Full detail: `.planning/milestones/v2.1-ROADMAP.md`.

- [x] Phase 14: Advisor Concept & Diagrams (completed 2026-08-11)
- [x] Phase 15: Python API Page (completed 2026-08-11)
- [x] Phase 16: Tool / MCP Server Page (completed 2026-08-11)
- [x] Phase 17: Agent Skill Page (completed 2026-08-11)
- [x] Phase 18: Nav & Build Integration (completed 2026-08-11)

</details>

<details>
<summary>✅ v3.0 Provider-Agnostic Advisor, Full-Library Coverage (Phases 19–24) — SHIPPED 2026-08-12</summary>

Made the fdars AI advisor work with any LLM backend through a custom `Provider` protocol, and gave every fdars analysis aspect its own advisor — grounding invariant preserved on every backend. Full detail: `.planning/milestones/v3.0-ROADMAP.md`.

- [x] Phase 19: Provider Foundation & Grounding Contract (completed 2026-08-12)
- [x] Phase 20: Additional Provider Adapters (completed 2026-08-12)
- [x] Phase 21: Per-Aspect Advisor Coverage (completed 2026-08-12)
- [x] Phase 22: Surface Integration (completed 2026-08-12)
- [x] Phase 23: Packaging & CI (completed 2026-08-12)
- [x] Phase 24: Documentation (completed 2026-08-12)

</details>

<details>
<summary>✅ v4.0 fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs (Phases 25–29) — SHIPPED 2026-08-17</summary>

Upgraded `fdars-core` 0.14.0 → 0.17.0 and exposed the new upstream functional-data capabilities through PyO3 bindings + the Python API, extended the advisor, and documented everything to the method-accurate standard. Full detail: `.planning/milestones/v4.0-ROADMAP.md`.

- [x] Phase 25: Crate Bump + Regression Gate (completed 2026-08-14)
- [x] Phase 26: Interpolation, Imputation & Functional Statistics Bindings (completed 2026-08-15)
- [x] Phase 27: Scoring Metrics & Alignment/Registration Bindings (completed 2026-08-15)
- [x] Phase 28: Advisor Extension (completed 2026-08-16)
- [x] Phase 29: Docs — Diagrams & Worked Examples (completed 2026-08-17)

</details>

<details>
<summary>✅ v5.0 fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing (Phases 30–35) — SHIPPED 2026-08-18</summary>

Upgraded `fdars-core` 0.17.0 → 0.20.0 and exposed the new functional-inference + depth/boxplot + basis/smoothing surface, extended the advisor with an `inference` aspect, and documented it all. Full detail: `.planning/milestones/v5.0-ROADMAP.md`.

- [x] Phase 30: Crate Bump + Regression Gate (completed 2026-08-17)
- [x] Phase 31: Group A — `fdars.inference` Bindings (completed 2026-08-17)
- [x] Phase 32: Group B — Depth/Boxplot Bindings (completed 2026-08-17)
- [x] Phase 33: Group C — Basis/Smoothing Quick Wins (completed 2026-08-17)
- [x] Phase 34: Advisor Extension (completed 2026-08-17)
- [x] Phase 35: Docs — Diagrams & Worked Examples (completed 2026-08-18)

</details>

<details>
<summary>✅ v6.0 fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference (Phases 36–41) — SHIPPED 2026-08-22</summary>

Upgraded `fdars-core` 0.20.0 → 0.23.0 and exposed the new upstream surface across three capability groups, extended the advisor, and documented everything (blocking human diagram review caught + fixed an inverted hypograph/epigraph asymmetry). Full detail: `.planning/milestones/v6.0-ROADMAP.md`.

- [x] Phase 36: Crate Bump + Regression Gate (completed 2026-08-20)
- [x] Phase 37: Group A — Regression Bindings (completed 2026-08-20)
- [x] Phase 38: Group B — FPCA & Classification Bindings (completed 2026-08-21)
- [x] Phase 39: Group C — Depth/Outliers/Interval-Inference Bindings (completed 2026-08-21)
- [x] Phase 40: Advisor Extension (completed 2026-08-21)
- [x] Phase 41: Docs — Diagrams & Worked Examples (completed 2026-08-22)

</details>

<details>
<summary>✅ v7.0 Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth (Phases 42–49) — SHIPPED 2026-08-23</summary>

Docs-only quality pass (no crate bump, no new bindings). A full 61-diagram 4-axis scored inventory gated the milestone; SVG corrections batched by section; 20 new example-page workflow SVGs + 5 new advisor-surface SVGs; thin v4–v6 method pages extended. Whole-site `mkdocs build --strict` green offline; blocking human diagram review approved. Full detail: `.planning/milestones/v7.0-ROADMAP.md`.

- [x] Phase 42: Diagram Audit (completed 2026-08-22)
- [x] Phase 43: SVG Fix — learn / represent / align (completed 2026-08-22)
- [x] Phase 44: SVG Fix — analyze / monitoring / advisor (completed 2026-08-22)
- [x] Phase 45: SVG Fix — regression / inference (completed 2026-08-22)
- [x] Phase 46: Diagram Coverage — examples pages (completed 2026-08-22)
- [x] Phase 47: Diagram Coverage — advisor surface pages (completed 2026-08-22)
- [x] Phase 48: Page Depth (completed 2026-08-22)
- [x] Phase 49: Whole-Site Gate & Human Review (completed 2026-08-23)

</details>

<details>
<summary>✅ v8.0 Advisor: New Capabilities (Phases 50–54) — SHIPPED 2026-08-31</summary>

Extended the fdars AI advisor with four new capabilities (deferred aspects, comparative method-selection, pipeline diagnostic report, closed-loop auto-tuning) — grounding invariant + MCP-LLM-free boundary held throughout. Package 0.7.0 → 0.8.0. Full detail: `.planning/milestones/v8.0-ROADMAP.md`.

- [x] Phase 50: Deferred advisor aspects (completed 2026-08-31)
- [x] Phase 51: Comparative method-selection (completed 2026-08-31)
- [x] Phase 52: Pipeline diagnostic report (completed 2026-08-31)
- [x] Phase 53: Closed-loop auto-tuning (capstone) (completed 2026-08-31)
- [x] Phase 54: Eval strategy + docs (completed 2026-08-31)

</details>

<details>
<summary>✅ v9.0 scikit-learn API Compatibility (Phases 55–59) — SHIPPED 2026-09-02</summary>

Added `fdars.sklearn` — a pure-Python scikit-learn-compatible estimator layer over the current bindings so functional-data methods plug natively into `Pipeline`/`GridSearchCV`/`cross_val_score`, interoperate with native sklearn estimators, and offer `fit`/`transform`/`predict` ergonomics. **28 estimators** across five families pass the full `check_estimator` battery with zero exemptions; non-compliant methods EXCLUDED (reason-coded in `_coverage.py`), not exempted. 5 phases, 17 plans; `tests/sklearn/` 4294 passed / 0 failed; whole-site `mkdocs build --strict` green offline. Package 0.8.0 → 0.9.0, released to PyPI (tag `v0.9.0`). Closed via a documented Phase-59 verification override. Full detail: `.planning/milestones/v9.0-ROADMAP.md`.

- [x] Phase 55: Compliance-Triage & Foundation — `[sklearn]` extra + gated subpackage + `_BaseFdarsEstimator` + ~30-candidate triage → `EXCLUDED_METHODS` registry + go/no-go gate (completed 2026-08-31)
- [x] Phase 56: Transformers — FPCA + smoothers + imputer/interpolator + basis + depth as `TransformerMixin`; `Pipeline([smoother, fpca])` (completed 2026-08-31)
- [x] Phase 57: Regressors & Classifiers — FPC/PLS/GLM/nonparametric regressors + logistic/LDA/QDA/KNN/DD/elastic classifiers; `Pipeline` + `GridSearchCV` (completed 2026-08-31)
- [x] Phase 58: Clusterers & Outlier Detectors + Compliance Gate — KMeans/fuzzy/GMM + 6 detectors (stored-reference depth); full-matrix gate (28 estimators, 0 exemptions) + interop + CI 3.9–3.14 (completed 2026-09-01)
- [x] Phase 59: Documentation & Docs Gate — "scikit-learn API" docs section + coverage/EXCLUDE list + Pipeline & GridSearchCV worked examples + data-flow SVG; `--strict` green; pkg bump + PyPI release (shipped 2026-09-02; closed via verification override)

</details>

<details>
<summary>✅ v10.0 Diagram Quality & Accessibility Pass (Phases 60–65) — SHIPPED 2026-09-02</summary>

- [x] Phase 60: Diagram Quality Audit (2/2 plans) — completed 2026-09-02
- [x] Phase 61: SVG Corrections — learn / represent / align (1/1) — completed 2026-09-02
- [x] Phase 62: SVG Corrections — analyze / monitoring / advisor (1/1) — completed 2026-09-02
- [x] Phase 63: SVG Corrections — regression / inference / examples (1/1) — completed 2026-09-02
- [x] Phase 64: Cards & Thumbnails Sync + New Coverage (1/1) — completed 2026-09-02
- [x] Phase 65: STYLE_SPEC Refresh, Whole-Site Gate & Human Review (1/1) — completed 2026-09-02

Full detail: `.planning/milestones/v10.0-ROADMAP.md`
</details>

<details>
<summary>✅ v11.0 fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs (Phases 66–73) — SHIPPED 2026-09-05</summary>

Bumped `fdars-core` 0.23.0 → 0.33.0 (parallel-only, no linalg; zero drift, 5650-test gate) and exposed the new upstream surface across six capability families through PyO3 bindings + Python API, extended the advisor with new `fts`/`frechet` aspects (grounding invariant + MCP guard-sync held), and documented everything with 8 method-accurate hand-authored SVGs + offline worked examples (whole-site `--strict` green; blocking human diagram review approved). 24/24 requirements validated; package 0.9.0 → 0.10.0 (PyPI tag `v0.10.0` handed to user). Full detail: `.planning/milestones/v11.0-ROADMAP.md`.

- [x] Phase 66: Isolated Crate Bump + Regression Gate — 0.23.0 → 0.33.0 on the ~772-test baseline; 0.24–0.33 changelog/match-arm audit (`66-AUDIT.md`) (completed 2026-09-02)
- [x] Phase 67: Functional Time Series (`fdars.fts`) — 13-function submodule: FTSM fit/forecast/update, ACF/PACF/stationarity/long-run-covariance, fPLSR, spectral density, DPCA (completed 2026-09-02)
- [x] Phase 68: Function-on-Function & Scalar-on-Function Regression — `fof_regression` + FOF family in `fdars.regression`; new `fdars.scalar_on_function` (additive/generalized SoF + variable/model selection) (completed 2026-09-02)
- [x] Phase 69: Fréchet Regression & Density FDA — `convert.rs` ragged-list refactor; new `fdars.frechet` (`frechet_mean` SPD/spherical/correlation) and `fdars.density_fda` (LQD/Wasserstein) (completed 2026-09-03)
- [x] Phase 70: Multi-Domain Data, FAMM & Advanced Clustering — `PyMultiFunData`/`fdars.multi_fdata`; `fdars.famm`; `mfpca`/`spe_multivariate` in `fdars.spm`; DBSCAN/KCFC/FunFEM/elastic clustering (completed 2026-09-04)
- [x] Phase 71: Shapelets & GAK Metric — new `fdars.shapelet` (2 opaque fit handles + 2 enums) + 5 GAK functions in `fdars.metric` (sklearn precomputed-kernel shapes) (completed 2026-09-04)
- [x] Phase 72: Advisor Extension — new `fts`/`frechet` aspects + grounded fof/fam/gkam/shapelet/mfpca/spe_multivariate diagnostics; atomic MCP guard-sync (completed 2026-09-04)
- [x] Phase 73: Documentation & Release — per-family method-accurate pages + 8 SVGs + offline fences; whole-site `--strict` green; human diagram review; pkg 0.9.0 → 0.10.0 + tag `v0.10.0` (completed 2026-09-05)

</details>

<details>
<summary>✅ v12.0 Docs Depth, Card Coverage & AI Capability Skill (Phases 74–79) — SHIPPED 2026-09-06</summary>

Brought the v11.0-era thin method pages (regression + analyze families) to mature-page parity, added 2 flagship end-to-end example pages, completed section-landing card coverage (16 new hand-authored SVG thumbnails), and shipped the first non-advisor Agent Skill (`fdars-capabilities`) + an `llms.txt` capability digest (30 modules, 409 callables) + an LLM-free `fdars_list_capabilities` MCP tool guarded by the three-way GATE-04 guard-sync. Docs + skill — no crate bump, no new bindings. 20/20 requirements validated; 6 phases, 27 plans; whole-site `--strict` green offline; SVGO/determinism green (0/122 unstable); blocking human diagram review approved; grounding invariant + MCP LLM-free boundary preserved. Full detail: `.planning/milestones/v12.0-ROADMAP.md`.

- [x] Phase 74: Deepen Regression-Family Thin Pages (completed 2026-09-05)
- [x] Phase 75: Deepen Analyze-Family Thin Pages (completed 2026-09-05)
- [x] Phase 76: Flagship End-to-End Example Pages (completed 2026-09-06)
- [x] Phase 77: Section-Landing Card Coverage (completed 2026-09-06)
- [x] Phase 78: AI Capability-Discovery Skill (completed 2026-09-06)
- [x] Phase 79: Close Gate — Strict Build, SVGO/Determinism, Human Review & Release (completed 2026-09-06)

</details>

### 🚧 v13.0 Scientific Provenance & Cross-Language Implementations (Phases 80–84) — IN PROGRESS

**Milestone Goal:** When asked "what is method X, where does it come from, and how else could I do it?", every fdars AI surface returns *grounded* scientific provenance — foundational papers with DOIs/links — plus cross-language implementation pointers (R, Python, Matlab) for the covered public callables. A code + docs + skill milestone; no `fdars-core` bump and no new numerical bindings. Builds directly on v12.0's capability-discovery infrastructure (`_capability_map.json`, `fdars_list_capabilities`, `fdars-capabilities` skill, `llms.txt`, GATE-04 guard-sync).

**Standing execution constraints (all phases):**

- The MCP tool `fdars_method_references()` stays provably LLM-free (mirror GATE-04 → GATE-05): static `importlib.resources` JSON load, `_REFERENCES_MODULES` DERIVED from `_CAPABILITY_MODULES`, no `provider`/`model` keys, explicit `{"curated": false, "sentinel": "NO_CURATED_ENTRY"}` for the tail. The hybrid curated/LLM-fallback lives ONLY in the extended skill (flagged ungrounded), never in the tool.
- Curation is PAPER-LEVEL (~40–100 papers with a callable→paper index), sub-method-keyed, partial-but-honest across ~409 callables. Author-verify every entry against its DOI landing page before commit (F&M is **2001**, not 1991). Six anti-feature families (functional depth as a category, scoring metrics, SPM, seasonal, XAI/explain, conformal) return the `curated:false` sentinel, not forced citations. Report `N/409` explicitly.
- Docs / `llms.txt` emit OFFLINE from committed JSON (no `fdars` import at build), consistent with v12.0's `generate_capability_dataset.py`.
- Content/docs phases run SEQUENTIALLY on `main` with `use_worktrees: false` (doc-build fences hardcode the main-tree `.venv/bin/mkdocs`). The whole-site `mkdocs build --strict` (~25 min) + guard-sync + DOI/link gates run ONCE, consolidated at the CLOSE phase (Phase 84).
- A BLOCKING HUMAN citation-accuracy review (papers verified against DOI landing pages by a human, not an LLM) is a hard close gate — parallel to the standing v6.0 blocking diagram review; autonomous execution stops there.

- [ ] **Phase 80: Schema, Data Home & Primary Guard Tests** - `_references_map.json` stub + schema/author-verification workflow + maturin include + primary GATE-05 tests + offline DOI/URL structural gate
- [ ] **Phase 81: Curation — Paper Registry** - hand-authored, author-verified paper-level entries + sub-method callable index + R/Python/Matlab pointers + anti-feature sentinels + honest `N/409` coverage (bulk / critical path)
- [ ] **Phase 82: MCP Tool `fdars_method_references` + GATE-05 Companion** - LLM-free static lookup tool + `_REFERENCES_MODULES` + curated/sentinel return shape + Guard Group 3 companion tests (can parallel Phase 81)
- [ ] **Phase 83: Docs, llms.txt & Skill Extension** - `docs/references.md` + `--references` offline emit + `llms.txt` provenance section + `mkdocs.yml` nav + `fdars-capabilities` hybrid protocol
- [ ] **Phase 84: Close Gate — Strict Build, Guard-Sync, DOI Gate & Blocking Citation-Accuracy Review** - whole-site `--strict` offline + all GATE-05 groups + DOI/URL gate + blocking human citation-accuracy review + grounding/guard-sync confirmation + release handoff

## Phase Details

### Phase 80: Schema, Data Home & Primary Guard Tests

**Goal**: The references data home exists with a locked, validated schema and a small verified stub, so all downstream curation/tool/docs work is validated from day one — the schema is never authored free-form.
**Depends on**: Nothing new in v13.0 (first phase; picks up from Phase 79). Runs on `main`, `use_worktrees: false`.
**Requirements**: SCHEMA-01, SCHEMA-02, SCHEMA-03, SCHEMA-04
**Success Criteria** (what must be TRUE):

  1. A committed `python/fdars/_references_map.json` (paper-keyed `papers` + flat `callable_index`, same identifier space as `_capability_curation.json`) is packaged as wheel data via maturin `include` and loads via `importlib.resources`; it is seeded with a small (3–5 paper) author-verified stub spanning distinct capability families.
  2. A documented author-verification workflow + JSON schema doc governs curation (paper-level unit, sub-method-keyed callable claims, cross-language entry shape with `version` + Matlab `confidence`, the `curated:false` tail convention, the personal DOI-landing-page verification bar).
  3. Primary GATE-05 tests (Python 3.9+, no `mcp`) pass: internal consistency (`callable_index` keys == union of `papers[*].callables`) and cross-file (every `callable_index` key resolves to a real callable in `_capability_map.json`, `_Fdata` special-cased).
  4. An offline structural DOI/URL gate (DOI regex `^10\.\d{4,9}/\S+$`; URL well-formedness + domain allowlist) runs in CI with no live network resolve; any live resolve is opt-in (`FDARS_ONLINE_CHECKS=1`) and never runs under `pytest`/`mkdocs build`.

**Plans**: 1/2 plans executed

- [x] 80-01-PLAN.md — `_references_map.json` seed stub (5 author-verified papers) + Group 3 GATE-05 guard tests A/B/C in one atomic commit (SCHEMA-01, SCHEMA-03, SCHEMA-04)
- [ ] 80-02-PLAN.md — `docs/authoring/references-schema.md` schema spec + author-verification workflow (SCHEMA-02)

**UI hint**: no

### Phase 81: Curation — Paper Registry

**Goal**: `_references_map.json` carries author-verified, sub-method-accurate paper provenance + cross-language pointers across the table-stakes and differentiator families — the substantive, correctness-critical body of the milestone — with the anti-feature families honestly wired to the uncurated sentinel and coverage reported as `N/409`.
**Depends on**: Phase 80 (schema locked; primary guard tests validate every entry as curation grows). Runs on `main`, `use_worktrees: false`.
**Requirements**: CURATE-01, CURATE-02, CURATE-03, CURATE-04, CURATE-05
**Success Criteria** (what must be TRUE):

  1. Paper-level entries populate the families with clear roots (basis/smoothing, functional statistics, FM/band/modified-band depth, functional boxplot, dense FPCA + PACE, scalar-on-function & FLM, Fréchet regression, density/LQD FDA, elastic/SRSF registration, shift/landmark registration, metrics incl. GAK/DTW/soft-DTW, clustering, classification, inference incl. ITP/SCB, FTS incl. DPCA, shapelets, MFPCA/FAMM) — each entry's authors/year/title verified against its DOI landing page.
  2. The `callable_index` records sub-method-level attribution (e.g. `band_1d` vs `modified_band_1d` point to distinct papers, never a shared over-broad pointer); contested/multi-primary attributions list co-primaries or are flagged in-JSON rather than force-picked.
  3. Cross-language pointers (R / Python / Matlab) with package + representative function + `version` + specific-function URL are populated per covered paper; Matlab marked `confidence: low` unless verified; honest "no implementation in language X" gaps recorded explicitly.
  4. The six anti-feature families are wired to the `curated:false` sentinel path (absent from `callable_index` at the module-category level), so the tool returns the explicit uncurated signal rather than a forced module-level citation.
  5. Coverage is measured and honest — the achieved `N/409` fraction is recorded and emitted by the primary guard test; only author-verified entries carry provenance (no LLM-synthesized placeholder ships as curated).

**Plans**: TBD
**UI hint**: no

### Phase 82: MCP Tool `fdars_method_references` + GATE-05 Companion

**Goal**: The LLM-free `fdars_method_references()` MCP tool ships alongside `fdars_list_capabilities`, returning curated provenance or an explicit uncurated sentinel, with the full GATE-05 three-way mirror enforced in the same commit — the provable LLM-free boundary is closed.
**Depends on**: Phase 80 (needs the file + schema to exist; can start as soon as the stub lands and run in PARALLEL with Phase 81's curation). Runs on `main`, `use_worktrees: false`.
**Requirements**: MCP-01, MCP-02, MCP-03, MCP-04
**Success Criteria** (what must be TRUE):

  1. `fdars_method_references(method)` is a synchronous `@mcp.tool()` handler added after `fdars_list_capabilities` that loads the committed JSON via `importlib.resources`, accepts `"module.callable"` (preferred) or a suffix-resolved bare `"callable"`, and makes no model/provider call and no synthesis.
  2. On a hit it returns `{"method", "curated": true, "papers": [...with implementations...], "coverage": "N/409", "version"}`; on a miss it returns `{"method", "curated": false, "sentinel": "NO_CURATED_ENTRY", "message", "version"}` — never an empty dict or an error.
  3. `_REFERENCES_MODULES` is derived from / asserted equal to `_CAPABILITY_MODULES` and gates input before any JSON load.
  4. GATE-05 companion tests (Python 3.10+) land in `tests/test_guard_sync_version_independent.py` as Guard Group 3 in the SAME commit as the tool: LLM-free boundary (no `provider`/`model` keys; known-absent callable returns `curated:false` with no `doi`; no advisor/provider import) and frozenset literal mirror (`_REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES == _CAPABILITY_MODULES`).

**Plans**: TBD
**UI hint**: no

### Phase 83: Docs, llms.txt & Skill Extension

**Goal**: The provenance surface is public and consumable — a family-grouped References page (offline-generated with an honest coverage fraction), an extended `llms.txt` provenance section, and the `fdars-capabilities` skill carrying the hybrid curated/ungrounded protocol — so a reader or agent can find "where method X comes from and how else to do it."
**Depends on**: Phase 81 (needs meaningful curation coverage for a useful page) and Phase 82 (skill references the concrete tool). Runs on `main`, `use_worktrees: false`.
**Requirements**: DOCS-01, DOCS-02, DOCS-03, SKILL-01, SKILL-02
**Success Criteria** (what must be TRUE):

  1. `scripts/generate_capability_dataset.py --references` reads `_references_map.json` OFFLINE (no `fdars` import) and emits `docs/references.md` — a family-grouped method→paper→implementation cross-index with a prominent Coverage section stating `N of 409 callables have curated entries`.
  2. The `llms.txt` emit gains a `## Scientific Provenance & Cross-Language Implementations` section (per-entry `module.function — Authors (Year) doi:… ; R/Python/Matlab pointers`) with an explicit coverage fraction and the "uncurated methods absent; synthesize-but-flag-ungrounded" note — emitted offline.
  3. `docs/references.md` is wired into `mkdocs.yml` nav under the AI/capability section and renders under a `--strict` build.
  4. `.claude/skills/fdars-capabilities/SKILL.md` gains a `## Scientific Provenance Protocol` section encoding the hybrid (prefer curated; on `curated:false` synthesize but structurally flag `grounded:false`, never present synthesized as curated), non-duplicating the `fdars-advisor` boundary, and its walkthrough + tests demonstrate BOTH the curated-hit and the visibly-labelled ungrounded-fallback paths.

**Plans**: TBD
**UI hint**: no

### Phase 84: Close Gate — Strict Build, Guard-Sync, DOI Gate & Blocking Citation-Accuracy Review

**Goal**: The whole milestone is proven correct and shippable in one pass — the site builds strict and offline, all guard-sync groups and the structural DOI/URL gate are green, the coverage fraction is reported, a human confirms citation accuracy against DOI landing pages, the grounding/LLM-free boundaries still hold, and any release tick is handed off.
**Depends on**: Phases 80, 81, 82, 83 (all data, tool, docs, and skill must land before the single whole-site gate). Runs on `main`, `use_worktrees: false`.
**Requirements**: GATE-01, GATE-02, GATE-03, GATE-04
**Success Criteria** (what must be TRUE):

  1. Whole-site `mkdocs build --strict` is green OFFLINE with the new References page rendering and any executed fences emitting `FDARS_FENCE_OK`.
  2. All GATE-05 groups (primary A/B + companion C/D) are green and the offline structural DOI/URL gate is green; the coverage `N/409` fraction is reported and reviewed.
  3. A BLOCKING HUMAN citation-accuracy review is approved before close — a sample of curated entries verified against DOI landing pages by a human (not an LLM): authors/year/title match, sub-method attribution correct, cross-language pointers resolve. Autonomous execution stops at this gate.
  4. The grounding invariant + MCP LLM-free boundary are confirmed intact (full advisor/MCP/guard-sync suite incl. Guard Group 3 green); any reversible package-version tick is committed and any irreversible publish (tag/PyPI) stays human-gated and is handed off, not executed autonomously.

**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:** Phases execute in numeric order: 80 → 81 → 82 → 83 → 84 (all sequential on `main`, `use_worktrees: false`). Phase 82 (MCP tool) MAY run in parallel with Phase 81 (curation) once the Phase 80 stub lands, but is listed sequentially for the standing main-tree constraint.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 80. Schema, Data Home & Primary Guard Tests | v13.0 | 1/2 | In Progress|  |
| 81. Curation — Paper Registry | v13.0 | 0/TBD | Not started | - |
| 82. MCP Tool `fdars_method_references` + GATE-05 Companion | v13.0 | 0/TBD | Not started | - |
| 83. Docs, llms.txt & Skill Extension | v13.0 | 0/TBD | Not started | - |
| 84. Close Gate — Strict Build, Guard-Sync, DOI Gate & Blocking Review | v13.0 | 0/TBD | Not started | - |

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v12.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{...}-phases/`._
