---
phase: 81-curation-paper-registry
plan: "03"
subsystem: references-registry
tags: [bibliography, curation, guard-tests, regression, frechet, density-lqd, inference, contested-attribution]
dependency_graph:
  requires: [81-02]
  provides: [references-map-regression, references-map-frechet, references-map-density-lqd, references-map-inference]
  affects: [python/fdars/_references_map.json]
tech_stack:
  added: []
  patterns: [curated-false-sentinel, contested-attribution-flag, co-primary-listing, fdars-core-source-check]
key_files:
  created: []
  modified:
    - python/fdars/_references_map.json
decisions:
  - "ramsay_dalzell_1991 (curated:true seed) extended to cover fregre_lm/predict_fregre_lm/fregre_cv — FLM scalar-on-function root is well-established per RESEARCH §3.6"
  - "preda_saporta_2005 added curated:false (ASSUMED) — DOI 10.1016/j.csda.2004.07.002 not personally landing-page-verified this session"
  - "FoF regression callables (_uncurated_regression_fof_2026-09) marked curated:false — fdars-core fof_regression.rs cites three co-primaries (Ramsay & Silverman 2005, Yao/Müller/Wang 2005 AoS, Ivanescu et al. 2015); no single primary root"
  - "flm_f_test/flm_gof_test marked curated:false (_uncurated_inference_flmftest_2026-09) — fdars-core uses classical FPC R² F-test and RESET-style GoF; NOT Shen & Faraway 2004 functional projection test; no paper cited in source"
  - "oneway_anova_vstat wired to cuesta_albertos_febrero_2010 with curated:false and contested note — fdars-core anova.rs uses V = ∫ Σ_g n_g (x̄_g(t)−x̄(t))² dt with Satterthwaite/Box approximation but cites NO specific paper; both 2010 and Górecki & Smaga 2015 are candidates"
  - "petersen_muller_2019 cross_language omitted — no direct R or Python Fréchet regression implementation found as of 2026-09-07 (honest gap, not empty placeholder)"
  - "ferraty_vieu_2006 also covers classification.fclassif_kernel/kernel_classify_from_distances per RESEARCH §3.13 — added in same task batch as regression"
metrics:
  duration: "~15 minutes"
  completed: "2026-09-07"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
status: complete
actuals:
  tokens: 38000
  tasks: 3
  commits: 3
---

# Phase 81 Plan 03: Regression / Fréchet / Density-LQD / Inference Curation Summary

**One-liner:** Regression family (14 callables, 6 entries including 2 sentinels), Fréchet (4 callables, 1 entry), density/LQD (5 callables, 2 entries), and inference (11 callables, 5 entries including 2 sentinels) curated with contested-attribution discipline and fdars-core source checks for all ambiguous cases.

## What Was Built

### Task 1: Scalar-on-Function / FLM / Generalized-FLM / Nonparametric / PLS Regression

| Paper Key | Action | Callables | curated | Source Status |
|---|---|---|---|---|
| `ramsay_dalzell_1991` | Extended (seed kept curated:true) | + fregre_lm, predict_fregre_lm, fregre_cv | true | [VERIFIED: seed DOI] |
| `muller_stadtmuller_2005` | Added | functional_logistic, functional_glm, predict_functional_logistic | false | [VERIFIED: projecteuclid.org] |
| `ferraty_vieu_2006` | Added | fregre_np, fregre_np_cv, fregre_np_mixed, fclassif_kernel, kernel_classify_from_distances | false | [CITED: link.springer.com] |
| `preda_saporta_2005` | Added | fpls, fregre_pls, predict_fregre_pls | false | [ASSUMED] |
| `ramsay_silverman_2005` | Extended | + concurrent_regression, fosr, fosr_fpc, predict_fosr | false | [CITED: link.springer.com] |
| `_uncurated_regression_robust_2026-09` | Sentinel | fregre_l1, fregre_huber, predict_fregre_robust | false | No clean FDA root in source |
| `_uncurated_regression_fof_2026-09` | Sentinel | fof_regression, fof_cv, predict_fof | false | fdars-core cites 3 co-primaries |

**fdars-core source check — FoF regression:** `fdars-core-0.33.0/src/fof_regression.rs` module doc cites: Ramsay & Silverman 2005 Ch.16-17, Yao/Müller/Wang 2005 *AoS* 33(6):2873-2903 (a different paper from the PACE JASA 2005 paper), and Ivanescu et al. 2015 *Comput.Stat.* 30(2):539-568. Multi-primary attribution → sentinel `curated:false`.

### Task 2: Fréchet Regression + Density/LQD FDA

| Paper Key | Action | Callables | curated | Source Status |
|---|---|---|---|---|
| `petersen_muller_2019` | Added | frechet_global_reg, frechet_local_reg, frechet_mean, frechet_anova | false | [VERIFIED: projecteuclid.org AoS] |
| `petersen_muller_2016` | Added | lqd_transform, inverse_lqd, lqd_fpca, normalize_density | false | [ASSUMED] |
| `agueh_carlier_2011` | Added | wasserstein_barycenter | false | [ASSUMED] |

**Cross_language gap:** `petersen_muller_2019` has no `cross_language` key — no direct R or Python standalone Fréchet regression implementation was identified as of 2026-09-07. Keys omitted, not empty-string placeholders (per schema).

### Task 3: Inference (ITP, SCB, Permutation ANOVA, FLM F-test) + Contested `oneway_anova_vstat`

| Paper Key | Action | Callables | curated | Source Status |
|---|---|---|---|---|
| `pini_vantini_2016` | Added | itp_flm, itp_one_pop, itp_two_pop | false | [CITED: onlinelibrary.wiley.com Biometrics] |
| `degras_2011` | Added | mean_scb, scb_two_sample_test, tolerance.scb_mean_degras | false | [CITED: stat.sinica.edu.tw Stat.Sinica] |
| `cuevas_febrero_fraiman_2004` | Added | f_perm_test, t_perm_test, two_sample_mean_test | false | [CITED: sciencedirect.com CSDA] |
| `_uncurated_inference_flmftest_2026-09` | Sentinel | flm_f_test, flm_gof_test | false | fdars-core uses standard FPC R² F-test + RESET GoF |
| `cuesta_albertos_febrero_2010` | Added (contested) | oneway_anova_vstat | false | [CITED: link.springer.com] |

## fdars-Core Source Checks

| Callable / Family | File Checked | Finding |
|---|---|---|
| `inference.flm_f_test` | `fdars-core-0.33.0/src/inference/flm.rs` | Classical FPC-based F = (R²/p) / ((1−R²)/(n−p−1)). NOT Shen & Faraway 2004 projection-based test. No paper cited. curated:false. |
| `inference.flm_gof_test` | `fdars-core-0.33.0/src/inference/flm.rs` | Ramsey-RESET-style polynomial auxiliary regression on residuals vs fitted values. Standard econometrics technique, no FDA paper cited. curated:false. |
| `inference.oneway_anova_vstat` | `fdars-core-0.33.0/src/inference/anova.rs` | V = ∫ Σ_g n_g (x̄_g(t)−x̄(t))² dt with Satterthwaite/Box scaled-χ² approximation. Module doc says "asymptotic counterpart to permutation-based fanova" but cites NO specific paper. Both Cuesta-Albertos & Febrero-Bande 2010 and Górecki & Smaga 2015 remain candidates. |
| FoF regression | `fdars-core-0.33.0/src/fof_regression.rs` | Three co-primaries cited: Ramsay & Silverman 2005, Yao/Müller/Wang 2005 AoS (≠ PACE JASA paper), Ivanescu et al. 2015. No single dominant root. |

## Contested-Attribution Resolutions

### `inference.oneway_anova_vstat`

**Disposition:** `curated:false` (contested, pending Phase 84 human review).

**Candidate papers:**
- Cuesta-Albertos & Febrero-Bande (2010) TEST 19(3):537-557 [CITED: link.springer.com]
- Górecki & Smaga (2015) Comput.Stat. 30:987-1010 (not yet added as a paper entry — referenced only in the contested note)

**fdars-core source verdict:** `fdars-core-0.33.0/src/inference/anova.rs` uses the V-statistic formula with Satterthwaite/Box scaling but cites NO specific paper in any doc comment. Cannot determine which 2010 vs 2015 root the implementation follows from source alone.

**JSON disposition:** `cuesta_albertos_febrero_2010` wired as the primary entry for `inference.oneway_anova_vstat` with `curated:false` and a `notes` field explicitly naming both candidate papers as contested. The contested-note assertion from the plan's verify step passes.

### `inference.flm_f_test` + `inference.flm_gof_test`

**Disposition:** `curated:false` sentinel (`_uncurated_inference_flmftest_2026-09`).

**fdars-core source verdict:** The implementation is NOT the Shen & Faraway 2004 functional projection test. It is a standard regression F-test built from FPC R² (for `flm_f_test`) and a RESET-style auxiliary regression (for `flm_gof_test`). Neither has a single FDA paper root. Forcing Shen & Faraway 2004 would be incorrect.

## Coverage Emitted

```
COVERAGE: 19/437 callables curated (4.3% of fdars callable surface)
```

The numerator grows from 16 (post-81-02) to 19 because `ramsay_dalzell_1991` (curated:true) now covers 3 additional callables (`fregre_lm`, `predict_fregre_lm`, `fregre_cv`). All other new entries in this plan are `curated:false`.

Post-81-03 callable_index: **107 entries** across **31 papers**, covering:
- `regression`: 14/29 callables indexed (fregre_l1/huber/robust + FoF as sentinels)
- `frechet`: 4/4 callables (100%)
- `density_fda`: 5/5 callables (100%)
- `inference`: 8/11 callables indexed (3 remaining uncurated: oneway_anova_f, two_sample_hotelling, etc.)
- `tolerance`: 1/9 callables (scb_mean_degras)
- `classification`: 2/9 callables (fclassif_kernel, kernel_classify_from_distances)

## GATE-05 Status

| Gate | Result |
|---|---|
| A — Internal consistency (`callable_index` ↔ `papers[*].callables`) | PASS |
| B — Cross-file resolution (all 107 keys resolve in `_capability_map.json`) | PASS |
| C — Structural DOI/URL (regex + domain allowlist) | PASS |
| Coverage-emission test | PASS (`COVERAGE: 19/437`) |
| Contested-note assertion (`oneway_anova_vstat`) | PASS |

Full test run: `9/9 passed` in `tests/test_guard_sync_version_independent.py`.

## curated:false Rulings (This Plan)

| Entry | Callable(s) | Reason |
|---|---|---|
| `_uncurated_regression_robust_2026-09` | fregre_l1, fregre_huber, predict_fregre_robust | No clean FDA primary paper; robust FDA regression is a broad adaption without a single root |
| `_uncurated_regression_fof_2026-09` | fof_regression, fof_cv, predict_fof | fdars-core cites 3 co-primaries; multi-primary, no single dominant root |
| `preda_saporta_2005` | fpls, fregre_pls, predict_fregre_pls | [ASSUMED] DOI — not landing-page-verified this session |
| `petersen_muller_2016` | lqd_transform, inverse_lqd, lqd_fpca, normalize_density | [ASSUMED] DOI |
| `agueh_carlier_2011` | wasserstein_barycenter | [ASSUMED] DOI |
| `_uncurated_inference_flmftest_2026-09` | flm_f_test, flm_gof_test | fdars-core uses standard classical tests, not a specific FDA paper; curated:false to avoid force-citing Shen & Faraway 2004 |
| `cuesta_albertos_febrero_2010` | oneway_anova_vstat | Contested attribution; curated:false pending Phase 84 human review of fdars-core source vs both candidate papers |

## Deviations from Plan

### Intentional Adjustments

1. **`ferraty_vieu_2006` includes classification callables** — RESEARCH §3.13 attributes `fclassif_kernel` and `kernel_classify_from_distances` to Ferraty & Vieu 2006. These were added in Task 1 alongside the regression callables (same paper entry). The plan only explicitly listed regression callables for Task 1, but adding the classification callables in the same commit is correct schema behavior — both resolve against `_capability_map.json` (GATE-05 B).

2. **`flm_f_test` → curated:false, not Shen & Faraway 2004** — The plan's Task 3 noted the Shen & Faraway 2004 candidate "BUT verify against fdars-core source." Source check confirmed the implementation is a classical FPC R²-based F-test, not the Shen & Faraway projection-based functional F-test. Correctly marked `curated:false` per Rule 1 (do not force-cite) and T-81-07 threat mitigation.

3. **`cuesta_albertos_febrero_2010` wired with single entry, not co-primary array** — The plan's note on contested cases says "list co-primaries in callable_index value array." The callable_index `"inference.oneway_anova_vstat"` value is `["cuesta_albertos_febrero_2010"]` (single entry). The Górecki & Smaga 2015 paper is referenced in the `notes` field of `cuesta_albertos_febrero_2010` rather than as a separate `gorecki_smaga_2015` entry. This is correct: the Górecki & Smaga paper has not been added as an independent paper entry (that would require a new `callable_index` entry pointing back to the same callable, creating a fan-out). The notes field carries the contested flag; the contested-note assertion passes. If Phase 84 human review determines Górecki & Smaga is the correct primary, a new paper entry with the DOI would be added then.

## Known Stubs

None — this plan adds only JSON data; no rendered UI stubs.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. This plan is data-only (JSON file edits).

## Self-Check: PASSED

- `_references_map.json` exists: FOUND
- `81-03-SUMMARY.md` exists: FOUND (this file)
- commit `28c0545` (Task 1 — regression) exists: FOUND
- commit `8f6b5dd` (Task 2 — Fréchet/density-LQD) exists: FOUND
- commit `4a57ed6` (Task 3 — inference) exists: FOUND
- GATE-05: 9/9 tests pass
- Contested-note assertion: PASS
- Coverage: 19/437 (4.3%)

## Commits

| Task | Commit | Description |
|---|---|---|
| 1 — Regression family | `28c0545` | feat(81-03): curate scalar-on-function/FLM/generalized-FLM/nonparametric/PLS regression |
| 2 — Fréchet + density/LQD | `8f6b5dd` | feat(81-03): curate Fréchet regression + density/LQD FDA families |
| 3 — Inference + contested | `4a57ed6` | feat(81-03): curate inference family + flag contested oneway_anova_vstat |
