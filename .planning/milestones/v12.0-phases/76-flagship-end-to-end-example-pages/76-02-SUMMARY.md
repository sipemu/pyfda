---
phase: 76-flagship-end-to-end-example-pages
plan: "02"
subsystem: docs
tags: [functional-time-series, ftsm, stationarity, functional-acf, canadian-weather, mkdocs, example-page, forecast]

requires:
  - phase: 76-01
    provides: frechet-density-regression.md tracer — proven nav-wiring + fence-runner pattern
  - phase: 75-fts-and-shapelets
    provides: corrected fdars.fts API (ftsm, ftsm_forecast_multistep, stationarity_test, functional_acf), run_page_fences.py

provides:
  - docs/examples/fts-forecast.md — mature EXMP-01 flagship FTS example page
  - mkdocs.yml nav entry for fts-forecast
  - docs/examples/index.md table row for fts-forecast

affects:
  - phase: 76-03 (shapelets example — same serialization pattern)
  - phase: 77 (CARD — gallery card + thumb for this new page)
  - phase: 79 (GATE — whole-site --strict build will exec this page's fences)

actuals:
  tokens: 4472   # 17888 diff chars / 4
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Mature example page pattern: bold Dataset intro + plain ## sections + html figure fences + Parameters table + See also + References"
    - "Latitude-gradient FTS framing: 35 Canadian stations sorted south-to-north, weekly-aggregated (35, 52) treated as functional time series"
    - "PVE from scores.var(axis=0) — NOT from fit['weights'] which is a (m,) quadrature-weight vector"
    - "fast(999, 99) gating for stationarity_test and functional_acf to keep fence times bounded"
    - "Weekly aggregation required for functional_acf: (30,52) runs in ~0.028s vs ~4.8s for (30,365)"

key-files:
  created:
    - docs/examples/fts-forecast.md
  modified:
    - mkdocs.yml
    - docs/examples/index.md

key-decisions:
  - "Four-fence structure: (1) data overview html figure, (2) stationarity+ACF html figure, (3) non-html numbers/metrics fence (fit summary + RMSE), (4) forecast vs truth html figure — 4 sentinels, 3 html fences, exceeds minimum requirements"
  - "PVE computed from scores.var(axis=0)/scores.var(axis=0).sum() in the non-html fence and referenced in the forecast html fence title — the anti-pattern grep check required renaming the admonition title from 'PVE comes from scores — not from weights' to 'Variance explained: use scores, not weights' to avoid triggering the pve.*weights antipattern pattern"
  - "Did not add concept diagram image reference — SVG does not exist; Phase 77 adds gallery cards and Phase 79 is the SVGO/diagram gate"
  - "Weekly aggregation (35, 52) carried through all fences — ensures functional_acf fence runs fast and all timings stay under 0.05s"

patterns-established:
  - "EXMP-01 nav-wiring: appended one mkdocs.yml line after the Fréchet (76-01) entry + one index.md table row — establishes slot for Plan 76-03 shapelets"

requirements-completed: [EXMP-01]

coverage:
  - id: D1
    description: "docs/examples/fts-forecast.md exists as a mature-standard example page (Dataset intro, plain sections, Parameters, See also, References)"
    requirement: EXMP-01
    verification:
      - kind: automated_ui
        ref: "node structural gate — fences=4 html=3, all checks pass (STRUCT OK)"
        status: pass
      - kind: other
        ref: "PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/examples/fts-forecast.md — ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "Nav wiring: mkdocs.yml nav line + docs/examples/index.md table row both present and point to fts-forecast.md"
    requirement: EXMP-01
    verification:
      - kind: automated_ui
        ref: "node structural gate — nav_line: true, index_row: true"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-05
status: complete
---

# Phase 76 Plan 02: FTS Forecast Example — Summary

**Flagship example page `fts-forecast.md` (EXMP-01): 35 Canadian weather stations sorted south-to-north by latitude and weekly-aggregated to (35, 52), treating the spatial gradient as a functional time series; FTSM fits ncomp=3 components with PVE from `scores.var(axis=0)`, forecasts 5 northern held-out stations via `ftsm_forecast_multistep`, reports stationarity (p≈0.010) and lag-1 ACF (≈0.33) — all 4 fences emit `FDARS_FENCE_OK` offline, nav-wired in mkdocs.yml and index.md.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-05T21:48:55Z
- **Completed:** 2026-09-05T21:52:13Z
- **Tasks:** 1
- **Files modified:** 3 (1 created, 2 appended)

## Accomplishments

- Created `docs/examples/fts-forecast.md` — 315-line mature-standard example page with: bold `**Dataset:**` intro, narrative arc (motivation → latitude-gradient framing tip → data overview + html figure → stationarity + ACF html figure → FTSM fit numbers fence → forecast vs truth html figure → Parameters → See also → References)
- 3 `html="1"` figure fences and 1 non-html metrics fence, all 4 emitting `FDARS_FENCE_OK`
- Honored all RESEARCH pitfalls: PVE computed from `scores.var(axis=0)` (not `weights`), weekly aggregation for fast `functional_acf`, `fast(999, 99)` gating, no diagram image reference
- Appended one nav line to `mkdocs.yml` after the 76-01 Fréchet entry; appended one row to `docs/examples/index.md` "What each example shows" table
- Both verification gates passed: structural node check (STRUCT OK fences=4 html=3) and fence runner (ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK)

## Task Commits

1. **Task 1: Build fts-forecast.md end-to-end + nav-wire it** — `149852a` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `docs/examples/fts-forecast.md` — new 315-line flagship example page (EXMP-01)
- `mkdocs.yml` — appended one Examples nav line for fts-forecast (after frechet-density-regression)
- `docs/examples/index.md` — appended one row to the What-each-example-shows table

## Decisions Made

- Four-fence structure (data figure + stationarity/ACF figure + non-html metrics + forecast figure) exceeds the ≥3 sentinel + ≥1 html=1 minimum while keeping each fence focused
- No concept diagram image reference — SVG does not exist; Phase 77 handles gallery cards and Phase 79 the SVGO/diagram gate
- PVE antipattern fix: the admonition title was renamed from "PVE comes from scores — not from `weights`" to "Variance explained: use scores, not `weights`" because the structural gate grep `/pve[^\n]*weights/i` flagged the heading as the antipattern; the implementation itself correctly uses `scores.var(axis=0)` throughout
- Weekly aggregation `X_wk = X_ord[:, :364].reshape(35, 52, 7).mean(axis=2)` carried through all 4 fences for consistent, fast execution

## Deviations from Plan

None — plan executed exactly as written. The admonition title rename was a minor wording adjustment to avoid a false-positive antipattern grep match (not a plan deviation).

## Issues Encountered

None.

## Known Stubs

None — all four fences produce live outputs from the installed `.venv` package.

## Threat Flags

None — docs-only: one new markdown page + two nav edits. No network surface, no auth paths, no user input.

## Self-Check

Verified after writing SUMMARY:
- `docs/examples/fts-forecast.md` exists: FOUND
- Commit `149852a` exists: FOUND (via `git rev-parse --short HEAD`)
- Structural gate: STRUCT OK fences=4 html=3
- Fence gate: ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK

## Self-Check: PASSED

## Next Phase Readiness

- EXMP-01 (FTS) delivered and verified — the latitude-gradient framing, FTSM fit + 5-step forecast + RMSE evaluation, stationarity + ACF narrative are all proven
- Plan 76-03 (shapelet classification) can follow the identical nav-wiring pattern (append after this plan's fts-forecast entry)
- Phase 77 can now add a gallery card + thumbnail SVG for fts-forecast.md

---
*Phase: 76-flagship-end-to-end-example-pages*
*Completed: 2026-09-05*
