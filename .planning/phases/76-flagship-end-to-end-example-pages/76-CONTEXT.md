# Phase 76: Flagship End-to-End Example Pages - Context

**Gathered:** 2026-09-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Add three marquee end-to-end example pages to `docs/examples/`, each matching the
mature `examples/` standard (narrative arc + real `docs/data/` dataset + runnable
offline `FDARS_FENCE_OK` fences), wired into the examples nav:

- **EXMP-01** — Flagship Functional Time Series example (forecast + evaluation).
- **EXMP-02** — Flagship Fréchet-regression example (metric-space response walkthrough).
- **EXMP-03** — Flagship shapelet-classification example on `phoneme.csv`.

**In scope:** three new `docs/examples/*.md` pages, their narrative + runnable
fences against existing `docs/data/` datasets, and wiring each into the examples
nav (`mkdocs.yml` / `docs/examples/index.md` nav entry).

**Out of scope:** the section-landing gallery cards + thumbnails for these pages
(Phase 77, CARD-05 covers three *existing* uncarded example pages;
new-example cards are a Phase 77 concern), the capability skill (Phase 78), and
the whole-site `--strict` / SVGO / human-review gate (Phase 79). No `fdars-core`
bump, no new PyO3 bindings.

</domain>

<decisions>
## Implementation Decisions

### Scope (user-selected)
- **Three flagship examples** (the top of the "2–3" range) — EXMP-01, EXMP-02,
  and EXMP-03 all delivered. EXMP-03 is the shapelet-classification example on
  `phoneme.csv` (strong 5-class fit), not the density-FDA alternative.

### Datasets & method framing
- **EXMP-01 (Functional Time Series):** use `docs/data/canadian_weather.csv`
  (35 × 365 daily temperature curves). Build a genuine functional-time-series
  framing (research determines the strongest concrete construction — e.g. a
  sequence of curves the FTSM can forecast), fit + forecast + evaluate, using the
  corrected `fdars.fts` API established in Phase 75. Keep the series small enough
  to run offline fast (weekly aggregation like Phase 75 if needed).
- **EXMP-02 (Fréchet regression):** build a **real-data-derived metric-space
  response** where a strong concrete fit exists (research picks it — e.g.
  per-group distributions or covariance/SPD objects derived from a `docs/data/`
  dataset regressed on a scalar predictor); synthetic-augment ONLY where no clean
  real fit exists, and record that choice. Use the corrected `fdars.frechet` API
  from Phase 74 (frechet_global_reg / frechet_local_reg; naked-array returns).
- **EXMP-03 (shapelet classification):** `docs/data/phoneme.csv` (400 × 256,
  5-class). Use a small class subset / capped `max_candidates` (≈200) to keep the
  fence under a few seconds offline (per Phase 75 research). Use the corrected
  `discover_shapelets` (dict return) + `shapelet_classifier_fit` API.

### Page shape & structure
- Match the mature `examples/` standard: a narrative arc (motivation → data →
  method → results → interpretation), a real dataset loaded via the `docs_data`
  helpers, ≥1 `html="1"` exec'd figure per page, and runnable fences that emit
  `FDARS_FENCE_OK` offline under `.venv`. Model structure on existing mature
  examples (e.g. `docs/examples/tecator-regression.md`,
  `canadian-seasonal.md`, `phoneme-shape.md`, `sonar-tsrvf.md`).
- Verify each page with the shared `scripts/run_page_fences.py` runner (built in
  Phase 74). Fences are self-verifying for API accuracy.

### Nav wiring
- Add each new page to the examples nav so it is reachable from site navigation
  (`mkdocs.yml` nav under Examples, and/or `docs/examples/index.md`). The
  decorative **gallery cards + thumbnails** for these pages are deferred (a
  Phase 77 / CARD concern) — Phase 76 only guarantees nav reachability.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Mature example exemplars** to mirror: `docs/examples/tecator-regression.md`,
  `docs/examples/canadian-seasonal.md`, `docs/examples/phoneme-shape.md`,
  `docs/examples/sonar-tsrvf.md`, `docs/examples/growth-alignment.md`.
- **Datasets** in `docs/data/`: `canadian_weather.csv` (+`_precip`, +`_meta`),
  `phoneme.csv`, `sonar.csv`, `tecator.csv`, `growth.csv`, `wine.csv`, with
  loaders in the `docs_data` helper (used by existing fences, e.g.
  `load_canadian_weather()` returns `(day, X, meta)`).
- **Corrected method pages** from Phases 74/75 as the API source of truth:
  `docs/regression/frechet-regression.md`, `docs/analyze/functional-time-series.md`,
  `docs/analyze/shapelets.md`.
- **Shared fence runner:** `scripts/run_page_fences.py`.

### Established Patterns
- `markdown-exec` fences (`python exec="1" source="above"`, `html="1"` for
  figures via `docs_fig`); `FDARS_FENCE_OK` sentinel; admonitions.
- Examples nav lives in `mkdocs.yml` (Examples section) and `docs/examples/index.md`.

### Integration Points
- New pages slot into `docs/examples/` and the Examples nav.
- Fences run against the current `fdars` in the main-tree `.venv`; phase runs
  SEQUENTIALLY on `main`, `use_worktrees: false` (standing v12.0 decision).

</code_context>

<specifics>
## Specific Ideas

- EXMP-01 builds on the Phase 75 FTS page (same `fdars.fts` API, corrected);
  the example goes deeper — a full forecast + evaluation narrative.
- EXMP-03 builds on the Phase 75 shapelets page (`discover_shapelets` dict,
  `shapelet_classifier_fit`) applied end-to-end to real phoneme data.
- Keep every fence small and offline; the whole-site `--strict` build (which will
  execute these new fences too) runs once in Phase 79.

</specifics>

<deferred>
## Deferred Ideas

- Gallery cards + hand-authored thumbnails for these new example pages → Phase 77
  (CARD work; CARD-05 covers the three existing uncarded example pages).
- Whole-site strict build / SVGO / human diagram review → Phase 79 (GATE).
- Any density-FDA flagship example (the EXMP-03 alternative not chosen) — not in
  this milestone.

</deferred>
