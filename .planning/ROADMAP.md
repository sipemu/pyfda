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
- ✅ **v13.0 — Scientific Provenance & Cross-Language Implementations** — Phases 80–84 (shipped 2026-09-07)
- 🚧 **v14.0 — fdars Software Paper — arXiv Preprint** — Phases 85–90 (active)

## Phases

Active milestone: **v14.0 — fdars Software Paper — arXiv Preprint** (Phases 85–90).

- [x] **Phase 85: Manuscript Scaffold + Pipeline Infrastructure** - `paper/` tree, `article`-class `paper.tex` skeleton (natbib+BibTeX, no timestamps), `CITATION.cff`, deterministic `paper/code/` framework reusing `docs_fig.py` + `docs/data/` (completed 2026-09-08)
- [x] **Phase 86: Single-Source-of-Truth Wiring + CI Gate** - `assert_coverage.py` (counts from `_capability_map.json`) + `gen_refs_bib.py` (`refs.bib` from `_references_map.json`) drift tripwires + `.github/workflows/paper.yml` offline gate + tectonic PDF compile (completed 2026-09-08)
- [ ] **Phase 87: Comparison Table + Evidence File** - version-stamped `comparison_evidence.md` (peer spot-check) + the capability-dimension × peer-package comparison table (`\input`-ed, fdars column grounded from `_capability_map.json`)
- [ ] **Phase 88: Front Matter, Design/Architecture & Capability Tour** - Abstract, Intro/statement-of-need, FDA background, data-representation, software-design/architecture, advisor+provenance section, and the capability tour with executed-script snippets
- [ ] **Phase 89: Case Studies + Reproducible Figures** - four real-dataset case studies (phoneme/growth, tecator/canadian_weather, canadian_weather_precip FTS, wine/sonar sklearn Pipeline) with committed deterministic figures
- [ ] **Phase 90: Close Gate + Citable Release** - snippet-runs + coverage-drift + determinism gates, clean-dir arXiv `pdflatex+bibtex` compile, blocking human read-through, and the citable 0.13.0 release (bump + tag + CITATION/DOI wiring)

## Phase Details

### Phase 85: Manuscript Scaffold + Pipeline Infrastructure

**Goal**: A `paper/` project exists with a compiling minimal manuscript skeleton and a deterministic reproducible-code framework, locking every tooling decision (plain `article`, natbib+BibTeX, no timestamp macros, `Agg`/seeded matplotlib, data reuse) that later phases depend on.
**Depends on**: Nothing (first phase of milestone)
**Requirements**: MANU-01, MANU-08, PIPE-01, PIPE-02
**Success Criteria** (what must be TRUE):

  1. `paper/paper.tex` uses `\documentclass{article}` with natbib + BibTeX (no biblatex/biber, no `\today`/timestamp macros) and `\input`s per-section stub files that together compile to a minimal PDF (via CI tectonic — no local TeX assumed).
  2. `CITATION.cff` (v1.2.0) is `cffconvert`-valid with a `preferred-citation` block and the author block placeholdered to Simon Müller <sm@data-zoo.de>.
  3. `paper/code/paper_utils.py` imports and reuses `scripts/docs_fig.py` (`fig()`/colors) and resolves datasets through a `data_path()` helper pointing at `docs/data/` — no dataset is copied or duplicated.
  4. A one-command Makefile target regenerates all pipeline outputs; matplotlib runs on the `Agg` backend with module-top rcParams and per-figure `np.random.seed`, and a re-run of the pipeline leaves `git diff paper/figures/` empty (deterministic PDF output with suppressed `CreationDate`).

**Plans**: 2 plans

- [x] 85-01-PLAN.md — Reproducible figure pipeline (tracer): paper_utils.py reusing docs_fig.py + data_path(), seeded figure script, one-command Makefile runner, determinism gate (empty git diff)
- [x] 85-02-PLAN.md — LaTeX manuscript skeleton (article + natbib/BibTeX, seven section stubs, no timestamps) + cffconvert-valid CITATION.cff

### Phase 86: Single-Source-of-Truth Wiring + CI Gate

**Goal**: The drift tripwires are functional before any prose cites a number — coverage counts and the bibliography are machine-derived from the committed JSON maps, and a standalone CI workflow runs the pipeline offline and compiles the PDF.
**Depends on**: Phase 85
**Requirements**: PIPE-03, PIPE-04, GATE-01
**Success Criteria** (what must be TRUE):

  1. `assert_coverage.py` derives public + total callable counts from `_capability_map.json`, writes `coverage_counts.tex` macros consumed by the manuscript, and exits non-zero on drift — no coverage integer is hardcoded in any `.tex` file.
  2. `gen_refs_bib.py` generates `paper/refs.bib` from `_references_map.json` (paper-key → cite-key, authors joined, DOI/URL fields) with a resolved strategy for the missing `journal` field (venue added during a curation pass, or `@misc` emitted).
  3. `.github/workflows/paper.yml` is path-filtered to `paper/**` + `_capability_map.json` + `_references_map.json` + `docs/data/**`, runs the reproducible pipeline offline as a hard gate, then compiles the PDF via `tectonic` (`wtfjoke/setup-tectonic@v4`).
  4. Introducing a drift (e.g. a stale hardcoded count or a missing ref) causes the CI gate to fail rather than pass silently.

**Plans**: 2 plans

- [x] 86-01-PLAN.md — Generators + machine-derived outputs (tracer): `assert_coverage.py` (six coverage macros + `--check` drift gate) + `gen_refs_bib.py` (47 `@misc` entries), commit `coverage_counts.tex` + regenerated `refs.bib`, `\input{coverage_counts}` in `paper.tex`, extend `make paper`
- [x] 86-02-PLAN.md — CI gate: `.github/workflows/paper.yml` path-filtered to `paper/**` + both JSON maps + `docs/data/**`, offline pipeline hard gate before tectonic PDF compile, drift-fires negative test

### Phase 87: Comparison Table + Evidence File

**Goal**: The highest peer-review-rejection-risk artifact — the comparison-with-related-software table — exists and is defensible, with every competitor cell backed by a version-stamped source, so the capability tour that cites it can be written with confidence.
**Depends on**: Phase 86
**Requirements**: COMP-01, COMP-02
**Success Criteria** (what must be TRUE):

  1. `comparison_evidence.md` records, for scikit-fda, FDApy, R fda/fda.usc/refund, funData/tidyfun, and Matlab fdaM/PACE, a version-stamped source (package, version, URL, date) for every peer-package claim, with ≥1 peer package spot-checked against CRAN/PyPI/arXiv.
  2. An `\input`-ed comparison table (capability-dimension rows × peer-package columns) renders in the manuscript, with the fdars column grounded from `_capability_map.json` and coverage stated honestly (✓ / partial / —).
  3. Every non-fdars cell in the table traces to a claim in `comparison_evidence.md`.

**Plans**: 2 plans

- [x] 87-01-PLAN.md — Core artifact set (tracer): version-stamped `comparison_evidence.md` (all nine peer packages, spot-checks), the `\input`-ed booktabs/adjustbox comparison table, `paper.tex` preamble additions, and `check_comparison.py` traceability gate
- [ ] 87-02-PLAN.md — Enforce + ground: extend `check_comparison.py` with the fdars-column grounding assertion from `_capability_map.json`, then wire it into `make paper-check` and `paper.yml` (before tectonic)

### Phase 88: Front Matter, Design/Architecture & Capability Tour

**Goal**: The experiment-free prose of the paper is complete — a reader can understand the Python FDA gap, the data model, the Rust/PyO3 + sklearn + advisor architecture, and can see the breadth of the library through minimal runnable, executed-script-sourced snippets.
**Depends on**: Phase 86 (drift gates live); reads the Phase 87 comparison table
**Requirements**: MANU-02, MANU-03, MANU-04, MANU-05, MANU-06, MANU-07
**Success Criteria** (what must be TRUE):

  1. Front matter reads coherently: Abstract, an Introduction & statement of need framing the Python FDA gap, and a brief FDA-background section.
  2. The software design & architecture section describes the Rust core + PyO3 zero-copy boundary, a module map, the `Fdata` container, and the sklearn estimator layer qualitatively (no benchmarks); a separate section presents the grounded AI advisor + scientific-provenance layer as a contribution absent from peer FDA packages.
  3. The data-representation section explains `Fdata`, argvals/grids, and irregular/sparse (`IrregFdata`) representation.
  4. The capability tour walks method families with minimal runnable code snippets, each snippet sourced from an executed `paper/code/` script (never hand-copied).
  5. An Availability & installation section (PyPI, extras, Python 3.9–3.14) and a Conclusion are present.

**Plans**: TBD

### Phase 89: Case Studies + Reproducible Figures

**Goal**: The paper demonstrates fdars end-to-end on real datasets — four illustrative case studies, each a narrative worked example whose figures are regenerated deterministically by the pipeline and committed under `paper/figures/`.
**Depends on**: Phase 86 (pipeline + determinism gate); needs `fdars` installed in the paper env + verified dataset structures
**Requirements**: CASE-01, CASE-02, CASE-03, CASE-04
**Success Criteria** (what must be TRUE):

  1. Study 1 runs smooth + FPCA + classification on phoneme/growth (`docs/data/`) with reproducible committed figures.
  2. Study 2 runs registration + functional/scalar-on-function regression on tecator/canadian_weather with reproducible committed figures.
  3. Study 3 runs a functional-time-series forecast on `canadian_weather_precip` (dataset structure verified to support the slicing) with reproducible committed figures.
  4. Study 4 runs a sklearn `Pipeline` + `GridSearchCV` on wine/sonar showcasing the estimator layer with reproducible committed figures.
  5. Re-running the pipeline leaves `git diff paper/figures/` empty for every case-study figure.

**Plans**: TBD

### Phase 90: Close Gate + Citable Release

**Goal**: The manuscript is provably correct, self-contained for arXiv, human-approved, and shipped as a citable release — the milestone's core-value gates all pass and the paired 0.13.0 package tag is prepared.
**Depends on**: Phases 87, 88, 89 (all sections + figures)
**Requirements**: GATE-02, GATE-03, GATE-04, REL-01
**Success Criteria** (what must be TRUE):

  1. Correctness gate is green: every manuscript code snippet executes against the current `fdars`, `assert_coverage.py` re-runs clean (catching late binding additions), and the determinism check passes (byte-identical figures on re-run).
  2. arXiv self-containment holds: a clean-directory `pdflatex + bibtex` compile of the submission sources succeeds with all figures committed under `paper/figures/`.
  3. A blocking human read-through of the manuscript (prose accuracy, comparison table, citations) is approved before close.
  4. A citable 0.13.0 release is prepared: version bumped in `Cargo.toml`/`pyproject.toml`/`__version__`, `CITATION.cff` + arXiv/Zenodo DOI wiring finalized, and a semver `v0.13.0` tag prepared/handed to the user for PyPI publish.

**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 85. Manuscript Scaffold + Pipeline Infrastructure | 2/2 | Complete    | 2026-09-08 |
| 86. Single-Source-of-Truth Wiring + CI Gate | 2/2 | Complete    | 2026-09-08 |
| 87. Comparison Table + Evidence File | 0/2 | Planned | - |
| 88. Front Matter, Design/Architecture & Capability Tour | 0/0 | Not started | - |
| 89. Case Studies + Reproducible Figures | 0/0 | Not started | - |
| 90. Close Gate + Citable Release | 0/0 | Not started | - |

---

## Shipped Milestones (archived detail)

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

<details>
<summary>✅ v13.0 Scientific Provenance & Cross-Language Implementations (Phases 80–84) — SHIPPED 2026-09-07</summary>

Gave every fdars AI surface grounded scientific provenance — author-verified foundational papers with DOIs + cross-language (R/Python/Matlab) implementation pointers — via a single committed `_references_map.json`, a provably LLM-free `fdars_method_references()` MCP tool, an offline-generated References page + `llms.txt` provenance section, and a hybrid curated/ungrounded skill protocol. Paper-level, sub-method-keyed, partial-but-honest (28/437 curated:true; 437 = 409 public + 28 Fdata methods). Code + docs + skill — no `fdars-core` bump. Full detail: `.planning/milestones/v13.0-ROADMAP.md`.

- [x] Phase 80: Schema, Data Home & Primary Guard Tests — `_references_map.json` + schema doc + GATE-05 A/B/C + offline DOI/URL gate (completed 2026-09-07)
- [x] Phase 81: Curation — Paper Registry — 57 papers / 243 callable_index entries across 17 families + anti-feature sentinels + honest N/437 coverage (completed 2026-09-07)
- [x] Phase 82: MCP Tool `fdars_method_references` + GATE-05 Companion — LLM-free static lookup + `_REFERENCES_MODULES` mirror + Guard Group 3 (C)/(D) (completed 2026-09-07)
- [x] Phase 83: Docs, llms.txt & Skill Extension — `--references` offline emit → `docs/references.md` + llms.txt provenance + nav + `fdars-capabilities` hybrid protocol (completed 2026-09-07)
- [x] Phase 84: Close Gate — whole-site `--strict` green + all GATE-05 groups + DOI gate + blocking human citation review + reversible pkg tick 0.11.0→0.12.0 (completed 2026-09-07)

</details>

---

_Full phase detail for shipped milestones is archived under `.planning/milestones/` (`v1.0-ROADMAP.md` … `v13.0-ROADMAP.md`). Phase directories are archived under `.planning/milestones/v{...}-phases/`._
