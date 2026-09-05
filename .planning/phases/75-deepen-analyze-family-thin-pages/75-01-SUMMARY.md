---
phase: 75-deepen-analyze-family-thin-pages
plan: "01"
subsystem: docs
tags: [docs, analyze, functional-time-series, parity, DEPTH-02]
status: complete

dependency_graph:
  requires: []
  provides: [functional-time-series-parity]
  affects: [docs/analyze/functional-time-series.md]

tech_stack:
  added: []
  patterns:
    - UNNUMBERED mature analyze template (plain ## headings, method-selector table)
    - functional_acf html="1" ACF bar plot fence
    - Canadian weather real-data fence (weekly subsample 35×52)
    - fast() guard on n_perm for stationarity_test

key_files:
  modified:
    - docs/analyze/functional-time-series.md

decisions:
  - "Used UNNUMBERED template (plain ## headings), not numbered regression template"
  - "Canadian weather fence uses load_canadian_weather() returning (day, X, meta) tuple; subsample to weekly means data[:, ::7] for build speed"
  - "ACF html=1 fence uses max_lag=8, n_sim=fast(999,99) to bound build time"
  - "stationarity_test uses n_perm=fast(999,19) to stay under 1 second locally"

metrics:
  duration_seconds: 203
  completed_date: "2026-09-05"
  tasks_completed: 1
  tasks_total: 1
  commits: 1
  files_changed: 1

estimate:
  tokens: 64000
  raw_tokens: 42000

actuals:
  tokens: 17500
  tasks: 1
  commits: 1
---

# Phase 75 Plan 01: Functional Time Series — Summary

**One-liner:** Restructured `functional-time-series.md` to mature analyze parity — UNNUMBERED template, method-selector table, When-to-use decision section, all 8 API errors corrected (ftsm_update arg order, max_lag not lags, ACF/PACF return dict, ar_models key, spectral_density full-spectrum, dpca no order=, long_run_covariance default None), 3 exec fences (html ACF plot + real data + ftsm/stationarity), 8 admonitions, See also — both verify gates pass.

## What Was Built

The tracer plan for Phase 75. Brought `docs/analyze/functional-time-series.md` from a thin (~35% parity) v11.0 page to full mature-page parity per DEPTH-02:

**Structure added:**
- Method-selector table at top (9 functions/methods, key outputs)
- `## When to use` decision section (FTSM vs FPLSR vs DPCA; stationarity workflow; quick-start rule)
- `## See also` linking to seasonal-analysis, functional-statistics, clustering, index
- `## Parameter Selection and Result Interpretation` subsection (choosing ncomp, max_lag, reading upper_band, non-stationary differencing workflow)
- `## Methods available in R but not yet in Python` (cointegration, Hilbert AR(p), lag-1 only differencing)
- All method sections restructured with theory, syntax, Parameters/Returns tables, admonitions

**API errors corrected (8/8 from RESEARCH):**
1. `ftsm_update` signature: `new_curve` is second positional arg (before `argvals`), is 2D `(k_new, m)` — not `new_obs` not a 1D array
2. `functional_acf`/`functional_pacf` parameter: `max_lag` (not `lags`); `n_sim` and `ci` params added
3. ACF/PACF return dict: `lags (int64 1D)`, `acf (1D)`, `pacf (1D)`, `upper_band (1D)` — previously omitted entirely
4. `ftsm` return dict: `ar_models` key documented (list of dicts with `order`, `phi`, `sigma2`)
5. `spectral_density`: `bandwidth=None` param (no `freq=`); returns full-spectrum dict (`freqs`/`re`/`im`/`m`/`n_curves`/`bandwidth`)
6. `dpca`: no `order=` param; correct params are `bandwidth=None`, `filter_lag=None`; 7-key return dict documented
7. `dpca_reconstruct`: `fitted_reconstruction (N-2L, m)` and `reconstruction_error (ncomp,)` keys added
8. `long_run_covariance`: default `bandwidth=None` (not 1.0); `bandwidth=0` returns sample covariance only

**Fences (3 exec, all FDARS_FENCE_OK):**
- Fence 1: `ftsm` + `ftsm_forecast` + `stationarity_test` (synthetic 20×30, `n_perm=fast(999,19)`)
- Fence 2: `functional_acf` ACF bar plot with 95% upper_band, `html="1"` figure (`max_lag=8`, `n_sim=fast(999,99)`)
- Fence 3: Canadian weather real data (`load_canadian_weather()` → weekly subsample 35×52), `ftsm` + `ftsm_forecast`

**Admonitions (8 total):**
- `!!! tip` — choosing ncomp from weights
- `!!! note` — reading ar_models (per-component AR)
- `!!! info` — Canadian weather subsampling rationale
- `!!! warning` — no `lags=` parameter (it's `max_lag`)
- `!!! info` — spectral_density returns ALL frequencies (index freqs/re/im)
- `!!! warning` — no `order=` in dpca (it's `filter_lag`)
- `!!! note` — long_run_covariance default bandwidth=None not 1.0
- `!!! warning` — ftsm_update arg order (new_curve is second)

## Verification Results

**Structural gate (node one-liner):** STRUCT OK fences=3 adm=8 html=1
- `## When to use` ✓
- `## See also` ✓
- 3 FDARS_FENCE_OK tokens ✓ (>= 3)
- 8 admonitions ✓ (>= 3)
- 1 html="1" fence ✓
- `ftsm_update(data, new_curve, argvals` ✓; no `new_obs` ✓
- `max_lag` present ✓; no `lags=` kwarg on functional_acf/pacf ✓
- `ar_models` present ✓
- no `spectral_density(...freq...)` ✓; no `dpca(...order...)` ✓

**Fence gate:** ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Bug fix] Fixed Canadian weather loader call**
- **Found during:** Fence 2 (real-data fence) verification
- **Issue:** The page called `load_canadian_weather()` and accessed `weather["temperature"]`, but the loader returns a `(day, X, meta)` tuple, not a dict.
- **Fix:** Changed to `_day, X_full, _meta = load_canadian_weather()` and used `X_full[:, ::7]` for the subsampled data array.
- **Files modified:** `docs/analyze/functional-time-series.md`
- **Commit:** 205cbd7

## Known Stubs

None — all method sections have working fences or non-exec syntax blocks. No placeholder text or hardcoded empty values.

## Self-Check

- [x] `docs/analyze/functional-time-series.md` exists and is modified
- [x] Commit `205cbd7` exists (`git log --oneline -1` → `205cbd7 docs(75-01): bring functional-time-series.md...`)
- [x] Structural gate passes: STRUCT OK fences=3 adm=8 html=1
- [x] Fence gate passes: ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK

## Self-Check: PASSED
