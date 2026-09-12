# Phase 89: Case Studies + Reproducible Figures - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous — grey areas proposed and auto-accepted with sensible defaults)

<domain>
## Phase Boundary

The paper demonstrates fdars end-to-end on real datasets — FOUR illustrative case studies, each a narrative worked example whose figures are regenerated DETERMINISTICALLY by the pipeline and committed under `paper/figures/`. (Prose sections from Phase 88; close gate + release is Phase 90.)

The four studies (datasets confirmed present in `docs/data/` with `fdars.datasets` loaders):
- **Study 1 (CASE-01):** smoothing + FPCA + classification on phoneme/growth.
- **Study 2 (CASE-02):** registration + functional/scalar-on-function regression on tecator/canadian_weather.
- **Study 3 (CASE-03):** functional-time-series forecast on `canadian_weather_precip` (365 days × 35 stations — structure verified to support the slicing).
- **Study 4 (CASE-04):** sklearn `Pipeline` + `GridSearchCV` on wine/sonar showcasing the estimator layer.

Requirements: CASE-01, CASE-02, CASE-03, CASE-04.

</domain>

<decisions>
## Implementation Decisions

### Figure Generation & Determinism (the hard gate)
- Each study is driven by an executed `paper/code/` script that reuses the Phase 85 harness (`paper_utils.fig`, `FDARS_COLORS`, `save_figure` with `metadata={"CreationDate": None}`, `data_path()`), runs the real fdars analysis, and writes committed figure(s) to `paper/figures/`.
- DETERMINISM IS MANDATORY: `Agg` backend, module-top rcParams, per-figure `np.random.seed`/`default_rng`, contiguous float64 arrays, no timestamps. A re-run must leave `git diff paper/figures/` EMPTY for every case-study figure (SC-5). Wire study-figure generation into `make paper`; the determinism gate joins the existing `git diff --exit-code paper/figures/` check.
- Reuse the validated fdars call shapes + signature gotchas from 88-RESEARCH.md (int64 labels, contiguous float64, FPCATransformer(n_components=), ftsm_forecast takes raw data, spm unpacked, etc.). Each analysis MUST actually run against fdars 0.12.0.

### Case-study Narrative (casestudies.tex)
- `paper/sections/casestudies.tex` (Phase 85 stub) becomes a worked-example section: one subsection per study — problem framing, the fdars method used (grounded, honest), `\includegraphics` of the committed figure(s) with a caption, and a short interpretation. Prefer referencing the executed script and, where illustrative, `\input` a small executed snippet (same harness as Phase 88) so the shown code is provably current.
- All counts via macros (no hardcoded integers). Peer-review-safe, under-claiming; NO benchmark/performance claims (breadth + correctness only).

### Analysis Scope per Study (kept minimal + illustrative, not exhaustive)
- Study 1: smooth (basis/smoothing) → FPCA (scores/components plot) → classification (train/predict, report accuracy honestly). Figure(s): smoothed curves + FPCA components/scores, optionally a classification result.
- Study 2: register (alignment) curves → regression (scalar-on-function on tecator fat content, and/or function-on-function). Figure(s): registered curves + regression fit/coefficient.
- Study 3: FTS forecast on canadian_weather_precip (slice into functional time series, `ftsm_forecast` on RAW data per the gotcha) → forecast vs actual. Figure: forecast curve(s).
- Study 4: sklearn Pipeline (an fdars transformer + estimator) + GridSearchCV on wine or sonar → best params + CV score. Figure: CV/score or decision illustration. Showcases the 28-estimator sklearn layer.
- If any specific analysis cannot be made to run/deterministic, choose the nearest working fdars method for that family (research validates each) — never fabricate a result or ship a non-deterministic figure.

### CI
- `paper.yml` already builds fdars (maturin, Phase 88) and runs the pipeline + `git diff paper/figures/` determinism gate offline before tectonic — the case-study figures ride that existing gate. Confirm the workflow covers the new scripts (they run under `make paper`). FreeType/font cross-platform variance is the known residual determinism risk (CI is the arbiter — Phase 90).

### Claude's Discretion
Exact plots per study, figure count, subplot layout, dataset choice within each study's listed pair, and narrative length are at the planner/executor's discretion, provided every figure is deterministic + committed, every analysis actually runs against fdars 0.12.0, and results are reported honestly (real accuracy/score numbers from the executed run, not invented).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 85 harness: `paper/code/paper_utils.py` (`fig`, `FDARS_COLORS`, `save_figure`, `data_path`), `make paper` figure pipeline + determinism gate.
- Phase 88 snippet harness (`gen_snippets.py`) + validated fdars call shapes/gotchas (88-RESEARCH.md) — reuse for any shown snippet.
- `fdars.datasets`: load_growth, load_phoneme, load_tecator, load_canadian_weather, load_wine, load_sonar — plus raw CSVs in docs/data/ (canadian_weather_precip.csv = 365×35 for FTS).
- Coverage macros + comparison table + refs.bib/refs_manual.bib (Phases 86–88).
- `paper/sections/casestudies.tex` stub (Phase 85) wired via paper.tex \input (Phase 88).

### Established Patterns
- Deterministic seeded figures; Agg backend; committed PDFs byte-identical on re-run; CI-only tectonic; honest reporting.

### Integration Points
- Study figures → `paper/figures/`; scripts → `paper/code/`; narrative → `paper/sections/casestudies.tex`; all ride `make paper` + the determinism gate + paper.yml.

</code_context>

<specifics>
## Specific Ideas

Milestone determinism risk (STATE): "non-deterministic matplotlib — Agg + fixed rcParams + per-figure seed + suppressed CreationDate; FreeType/font variance across platforms is the residual risk — generate/verify figures in CI (Phase 89 determinism gate)." Honor exactly: local `git diff paper/figures/` empty on re-run is the hard gate; CI is the cross-platform arbiter at Phase 90.

</specifics>

<deferred>
## Deferred Ideas

- Close gate, arXiv ID, citable release, human approval → Phase 90.
- No benchmarks/performance timing (milestone lock).

</deferred>
