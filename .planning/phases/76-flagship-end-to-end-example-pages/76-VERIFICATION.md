---
phase: 76-flagship-end-to-end-example-pages
verified: 2026-09-06T08:30:00Z
status: passed
score: 21/21 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 76: Flagship End-to-End Example Pages Verification Report

**Phase Goal:** The examples section gains 2–3 marquee end-to-end walkthroughs for the new methods, matching the mature examples/ standard (narrative + real dataset + runnable offline fences), wired into nav.
**Verified:** 2026-09-06T08:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | docs/examples/frechet-density-regression.md exists as a mature-standard example page (narrative arc + real dataset + Parameters + See also) (EXMP-02) | ✓ VERIFIED | File confirmed at path; bold `**Dataset:**` intro, `## Parameters`, `## See also`, `## References` all present (1 each) |
| 2 | The Fréchet page builds per-station KDE temperature densities from canadian_weather into a (35, 60) density-response matrix and regresses on scalar latitude | ✓ VERIFIED | `gaussian_kde`, `normalize_density`, `t_grid = np.linspace(..., 60)`, `lat = meta["lat"].to_numpy()` all present in fences |
| 3 | Both frechet_global_reg and frechet_local_reg are called; predicted arrays accessed via np.asarray(result['predicted']) and xout passed 2D (reshape(-1,1)) | ✓ VERIFIED | Lines 147/151 use `np.asarray(result_g["predicted"])` / `np.asarray(result_l["predicted"])`; lines 140–141 reshape `lat[tr].reshape(-1, 1)` |
| 4 | wasserstein_barycenter (NOT frechet_mean) is used for the density-space mean | ✓ VERIFIED | `wasserstein_barycenter` appears; structural gate confirms `no_frechet_mean_density: true`; prose note at line 83 explains why |
| 5 | Test-split ISE is computed and reported for global vs local regression | ✓ VERIFIED | `np.trapezoid((pred_g - resp_test)**2, ...)` and `np.trapezoid((pred_l - resp_test)**2, ...)` present; ISE bar chart fence |
| 6 | Fréchet page has >=3 runnable FDARS_FENCE_OK fences, >=1 with html=1; every fence emits sentinel offline under .venv | ✓ VERIFIED | Structural gate: fences=3, html=2; fence runner: ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK |
| 7 | Fréchet page reachable from Examples nav: mkdocs.yml nav line + docs/examples/index.md table row both point at frechet-density-regression.md | ✓ VERIFIED | mkdocs.yml line 199; index.md line 165 — both in correct Examples section |
| 8 | docs/examples/fts-forecast.md exists as a mature-standard example page (narrative arc + real dataset + Parameters + See also) (EXMP-01) | ✓ VERIFIED | File confirmed; bold `**Dataset:**` intro, `## Parameters`, `## See also`, `## References` all present (1 each) |
| 9 | The FTS page loads canadian_weather, sorts 35 stations by latitude, and weekly-aggregates to a (35, 52) functional time series | ✓ VERIFIED | `np.argsort(meta["lat"]...)`, `X_ord[:, :364].reshape(35, 52, 7).mean(axis=2)` present in fences |
| 10 | It fits ftsm(ncomp=3), reports variance explained computed from scores.var(axis=0) (NOT from weights), and forecasts 5 steps with ftsm_forecast_multistep on held-out northern stations | ✓ VERIFIED | `scores.var(axis=0)` at lines 178, 233, 292; structural gate `pve_from_scores: true`, `no_pve_from_weights: true`; `ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)` present |
| 11 | A 5-step RMSE is computed against held-out test stations and reported | ✓ VERIFIED | `rmse = np.sqrt(np.mean((fcast - X_test)**2))` present; structural gate `has_rmse: true` |
| 12 | stationarity_test and functional_acf are shown with n_perm/n_sim gated by fast(999, 99) | ✓ VERIFIED | Lines 101/105: `n_perm=fast(999, 99)` and `n_sim=fast(999, 99)` present; structural gate `fast_gate: true` |
| 13 | FTS page has >=3 runnable FDARS_FENCE_OK fences, >=1 with html=1; every fence emits sentinel offline under .venv | ✓ VERIFIED | Structural gate: fences=4, html=3; fence runner: ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK |
| 14 | FTS page reachable from Examples nav: mkdocs.yml nav line + docs/examples/index.md table row both point at fts-forecast.md | ✓ VERIFIED | mkdocs.yml line 200; index.md line 166 |
| 15 | docs/examples/phoneme-shapelets.md exists as a mature-standard example page (narrative arc + real dataset + Parameters + See also) (EXMP-03) | ✓ VERIFIED | File confirmed; bold `**Dataset:**` intro, `## Parameters`, `## See also`, `## References` all present (1 each) |
| 16 | The phoneme page loads phoneme, builds a 3-class subset (aa/sh/dcl, 30/class) with np.ascontiguousarray, and runs discover_shapelets → shapelet_transform_fit → shapelet_transform → shapelet_classifier_fit | ✓ VERIFIED | All four API calls present; `np.ascontiguousarray(X[idx], dtype=np.float64)` at line 48/96; structural gate all checks true |
| 17 | discover_shapelets is treated as a summary dict ({n_shapelets, quality}), NOT iterated as a list of arrays | ✓ VERIFIED | `disc["n_shapelets"]` accessed at line 107; structural gate `discover_is_dict: true`; note block documents the dict contract |
| 18 | max_candidates=200 caps the search so the whole fence runs in a few seconds offline | ✓ VERIFIED | `max_candidates=200` present in all calls; structural gate `max_cand: true`; fences ran within DOCS_FAST=1 timeout |
| 19 | Train and test accuracy are computed via clf.predict on an 80/20 split; no invented >85% 5-class accuracy claim | ✓ VERIFIED | `.predict(X_te)` present; `test_acc`, `acc` computed; no ">85%", ">90%", "95%" strings found; scaling tip is qualitative only |
| 20 | Phoneme page has >=3 runnable FDARS_FENCE_OK fences, >=1 with html=1; every fence emits sentinel offline under .venv | ✓ VERIFIED | Structural gate: fences=4, html=3; fence runner: ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK |
| 21 | Phoneme page reachable from Examples nav: mkdocs.yml nav line + docs/examples/index.md table row both point at phoneme-shapelets.md | ✓ VERIFIED | mkdocs.yml line 201; index.md line 167 |

**Score:** 21/21 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/examples/frechet-density-regression.md` | New flagship Fréchet example page | ✓ VERIFIED | 292-line page, created in commit c3584f9 |
| `docs/examples/fts-forecast.md` | New flagship FTS example page | ✓ VERIFIED | 315-line page, created in commit 149852a |
| `docs/examples/phoneme-shapelets.md` | New flagship shapelet example page | ✓ VERIFIED | Created in commit 2ff5f0a |
| `mkdocs.yml` | Three Examples nav lines appended | ✓ VERIFIED | Lines 199–201 in Examples section after Penicillin entry |
| `docs/examples/index.md` | Three table rows appended | ✓ VERIFIED | Lines 165–167 in "What each example shows" table |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| frechet-density-regression.md fences | fdars.frechet + fdars.density_fda + .venv | `from fdars.frechet import ...`; `from fdars.density_fda import ...` | ✓ WIRED | All 3 fences emit FDARS_FENCE_OK under installed .venv |
| fts-forecast.md fences | fdars.fts + .venv | `from fdars.fts import ftsm, ftsm_forecast_multistep, stationarity_test, functional_acf` | ✓ WIRED | All 4 fences emit FDARS_FENCE_OK under installed .venv |
| phoneme-shapelets.md fences | fdars.shapelet + .venv | `from fdars.shapelet import discover_shapelets, shapelet_transform_fit, shapelet_transform, shapelet_classifier_fit` | ✓ WIRED | All 4 fences emit FDARS_FENCE_OK under installed .venv |
| mkdocs.yml nav (Examples section) | frechet-density-regression.md | `Canadian Weather — Fréchet Regression: examples/frechet-density-regression.md` | ✓ WIRED | Line 199, inside Examples section (line 176) |
| mkdocs.yml nav (Examples section) | fts-forecast.md | `Canadian Weather — FTS Forecast: examples/fts-forecast.md` | ✓ WIRED | Line 200 |
| mkdocs.yml nav (Examples section) | phoneme-shapelets.md | `Phoneme — Shapelet Classification: examples/phoneme-shapelets.md` | ✓ WIRED | Line 201 |
| docs/examples/index.md table | frechet-density-regression.md | Row with `(frechet-density-regression.md)` | ✓ WIRED | Line 165 |
| docs/examples/index.md table | fts-forecast.md | Row with `(fts-forecast.md)` | ✓ WIRED | Line 166 |
| docs/examples/index.md table | phoneme-shapelets.md | Row with `(phoneme-shapelets.md)` | ✓ WIRED | Line 167 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| frechet-density-regression.md | `density_matrix` (35,60) | `load_canadian_weather("temperature")` → `gaussian_kde` → `normalize_density` | Yes — live execution confirmed by fence runner | ✓ FLOWING |
| fts-forecast.md | `X_wk` (35,52) | `load_canadian_weather("temperature")` → weekly reshape | Yes — live execution confirmed | ✓ FLOWING |
| phoneme-shapelets.md | `X_sub` (90,256) | `load_phoneme()` → 3-class subset with `ascontiguousarray` | Yes — live execution confirmed | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| frechet-density-regression.md — all fences emit sentinel | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/examples/frechet-density-regression.md` | ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| fts-forecast.md — all fences emit sentinel | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/examples/fts-forecast.md` | ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| phoneme-shapelets.md — all fences emit sentinel | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/examples/phoneme-shapelets.md` | ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| Structural gate — frechet page | node one-liner (PLAN 01) | STRUCT OK fences=3 html=2 | ✓ PASS |
| Structural gate — fts page | node one-liner (PLAN 02) | STRUCT OK fences=4 html=3 | ✓ PASS |
| Structural gate — phoneme page | node one-liner (PLAN 03) | STRUCT OK fences=4 html=3 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| EXMP-01 | 76-02-PLAN.md | Flagship FTS example page (forecast + evaluation) against a docs/data/ dataset, runnable offline | ✓ SATISFIED | fts-forecast.md exists, 4 fences all pass, nav-wired; REQUIREMENTS.md row marked [x] |
| EXMP-02 | 76-01-PLAN.md | Flagship Fréchet-regression example page (metric-space response walkthrough), runnable offline | ✓ SATISFIED | frechet-density-regression.md exists, 3 fences all pass, nav-wired; REQUIREMENTS.md row marked [x] |
| EXMP-03 | 76-03-PLAN.md | Third flagship example page (shapelet classification) | ✓ SATISFIED | phoneme-shapelets.md exists, 4 fences all pass, nav-wired; REQUIREMENTS.md row marked [x] |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No TBD/FIXME/XXX/HACK/PLACEHOLDER markers found in any of the three pages | — | None |
| — | — | No diagram/thumb image references found (gallery cards correctly deferred to Phase 77) | — | None |

### Code Review Integration

The 76-REVIEW.md found 0 Critical, 2 Warnings, 3 Info items. Review status is `resolved`.

- **WR-01 (ACF upper_band):** Fix is confirmed present. `fts-forecast.md` line 110 reads `upper = float(np.asarray(acf["upper_band"]).max())` with an explanatory comment at line 108 — the conservative `.max()` envelope replaces the original `[0]` index. Fence re-run passed.
- **WR-02 (ISE re-print in Fréchet integration fence):** Accepted as expected pattern. The density integration check fence does valid integral verification work; ISE values re-printed from the same seed/split are not a correctness issue. Accepted per review resolution.
- **IN-01/02/03:** All accepted as consequence of markdown-exec fence isolation (each fence must be self-contained). No correctness impact.

### Human Verification Required

None. All checks are programmatically verifiable for this docs-only phase. The visual quality of the page narratives and figure aesthetics are the only items that benefit from human review, but these are outside the scope of the phase gate (they are covered by the Phase 79 human review gate for the full milestone).

### Gaps Summary

No gaps. All 21 must-have truths verified, all 5 artifacts substantive and wired, all 9 key links confirmed, all 3 fence gates pass, all 3 requirements satisfied, code review WR-01 fix confirmed in codebase.

---

_Verified: 2026-09-06T08:30:00Z_
_Verifier: Claude (gsd-verifier)_
