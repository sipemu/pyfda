---
phase: 89-case-studies-reproducible-figures
plan: "03"
subsystem: paper/code, paper/figures, paper/sections
tags: [case-studies, fts, functional-time-series, forecast, determinism, latex]
status: complete

dependency_graph:
  requires:
    - "paper/code/paper_utils.py (Phase 85 harness)"
    - "paper/code/casestudy1.py (module pattern; gen_figures.py lazy-stub wired by 89-01)"
    - "docs/data/canadian_weather_precip.csv (Study 3 dataset)"
    - "fdars 0.12.0 (.venv compiled, fts module: ftsm + ftsm_forecast)"
    - "paper/sections/casestudies.tex finalized shell (89-01)"
  provides:
    - "paper/code/casestudy3.py (Study-3 FTS pipeline, auto-registered via gen_figures.py lazy import)"
    - "paper/figures/cs3_precip_curves.pdf (deterministic committed figure)"
    - "paper/figures/cs3_precip_forecast.pdf (deterministic committed figure)"
    - "paper/sections/casestudy3.tex (Study-3 narrative subsection)"
  affects: []

tech_stack:
  added:
    - "fdars.fts.ftsm (FTS decomposition: mean curve + VAR on FPC scores)"
    - "fdars.fts.ftsm_forecast (3-step-ahead FTS forecast, takes raw data NOT model dict)"
  patterns:
    - "casestudyN.py module pattern: main() seeds seed(42), runs pipeline, saves figures via paper_utils.save_figure"
    - "Xfts = cw.T.values.astype(np.float64) — transpose (365,35)->( 35,365) before FTS calls"
    - "ftsm_forecast(Xfts, ARGd, h=3, ncomp=3) — raw data input (Pitfall 3 avoided)"

key_files:
  created:
    - paper/code/casestudy3.py
    - paper/figures/cs3_precip_curves.pdf
    - paper/figures/cs3_precip_forecast.pdf
    - paper/sections/casestudy3.tex
  modified: []

decisions:
  - "Reported forecast[0,:5] = [1.802, 1.861, 1.826, 1.703, 1.702] as live computed value — matches 89-RESEARCH exactly (same fdars version)"
  - "Honest shallow-sample caveat in both code docstring and casestudy3.tex narrative (A4 from 89-RESEARCH)"
  - "Two separate figures (curves + forecast) rather than two-panel single figure — mirrors casestudy1 pattern of one figure per concept"
  - "ftsm called for decomposition figure; ftsm_forecast called separately on raw Xfts (Pitfall 3 consciously avoided)"
  - "Citations: hyndman_ullah_2007 + hormann_kokoszka_2010 — both resolve in refs.bib"
  - "No 89-01-owned files (casestudies.tex, gen_figures.py, Makefile, paper.yml) modified"

metrics:
  duration_seconds: 480
  completed: 2026-09-09
  tasks: 2
  commits: 2
  files_created: 4
  files_modified: 0

actuals:
  tokens: 8500
  tasks: 2
  commits: 2
---

# Phase 89 Plan 03: Case Study 3 (FTS forecast on Canadian weather precipitation) Summary

**One-liner:** Functional time-series decomposition (ftsm, 3 components) + 3-step-ahead forecast (ftsm_forecast) on transposed canadian_weather_precip (35 stations × 365 days), with two byte-stable committed figures and an honest shallow-sample caveat in LaTeX.

## What Was Built

### Task 1: casestudy3.py — FTS pipeline + two deterministic figures

Created `paper/code/casestudy3.py` following the casestudy1.py module pattern. The `main()` function:

1. Seeds `np.random.seed(42)` (belt-and-suspenders; ftsm is deterministic VAR)
2. Loads `canadian_weather_precip.csv` (365 × 35 days × stations)
3. Transposes: `Xfts = cw.T.values.astype(np.float64)` → shape (35, 365)
4. Decomposes: `model = fdars.fts.ftsm(Xfts, ARGd, ncomp=3)` → mean curve (365,), scores (35,3)
5. Forecasts: `fc = fdars.fts.ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)` → forecast (3,365)
   - Pitfall 3 consciously avoided: passes raw Xfts + ARGd, NOT the model dict
6. Prints `forecast shape: (3, 365)` and `forecast[0, :5]: [1.802 1.861 1.826 1.703 1.702]`
7. Writes `cs3_precip_curves.pdf` (35 station curves + FTS mean)
8. Writes `cs3_precip_forecast.pdf` (3 forecast curves + observed mean)

Re-run byte-stability verified: two consecutive executions produce identical PDFs (`diff -q` clean). Forecast values match 89-RESEARCH §Study 3 (same fdars 0.12.0 runtime).

### Task 2: casestudy3.tex — FTS forecast narrative subsection

Created `paper/sections/casestudy3.tex` as `\subsection{Functional Time Series Forecasting: Canadian Weather Precipitation}` with:
- Problem framing: 35 stations, each a 365-day precipitation curve; stations as FTS index
- Methods paragraph: ftsm decomposition + ftsm_forecast h=3 ncomp=3; analysis reproduced by `paper/code/casestudy3.py`
- Two `\begin{figure}` environments, each with `\includegraphics` for `cs3_precip_curves.pdf` and `cs3_precip_forecast.pdf`, captions, and `\label`
- Honest caveat paragraph: 35 observations is shallow for VAR estimation (illustrative demo, not statistically optimal)
- Citations: `\citep{hyndman_ullah_2007,hormann_kokoszka_2010}` — both resolve in `paper/refs.bib`
- No benchmark claims, no dates, no hardcoded integers, no Placeholder text

No 89-01-owned files modified (casestudies.tex, gen_figures.py, Makefile, paper.yml all untouched).

## Deviations from Plan

None. The plan executed exactly as written. Real output numbers matched 89-RESEARCH exactly (forecast[0,:5] = [1.802, 1.861, 1.826, 1.703, 1.702]).

## Commits

| Hash | Message |
|------|---------|
| e8b6c8f | feat(89-03): casestudy3.py — FTS decomposition + 3-step forecast + two deterministic figures |
| 1eff223 | feat(89-03): casestudy3.tex — FTS forecast subsection with honest shallow-sample caveat |

## Known Stubs

None. Both figures are committed with real data; the narrative references them via `\includegraphics`; the analysis runs end-to-end against fdars 0.12.0.

## Threat Flags

None. No new network endpoints, auth paths, or schema changes introduced.

## Self-Check: PASSED

- paper/code/casestudy3.py: FOUND
- paper/figures/cs3_precip_curves.pdf: FOUND
- paper/figures/cs3_precip_forecast.pdf: FOUND
- paper/sections/casestudy3.tex: FOUND
- casestudy3.py runs without error on fdars 0.12.0: VERIFIED (forecast shape (3,365) confirmed)
- Byte-stability (two runs, diff -q clean): VERIFIED
- `.T.values` pattern present in casestudy3.py: VERIFIED
- casestudy3.tex: \subsection not \section: VERIFIED
- casestudy3.tex: both \includegraphics paths present: VERIFIED
- casestudy3.tex: no Placeholder, no benchmark, no date: VERIFIED
- All cite keys resolve in refs.bib: VERIFIED (hyndman_ullah_2007, hormann_kokoszka_2010)
- No 89-01-owned files modified: VERIFIED (git diff --quiet clean)
- Commits e8b6c8f, 1eff223: FOUND in git log
