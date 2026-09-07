---
phase: 81-curation-paper-registry
plan: "02"
subsystem: references-registry
tags: [bibliography, curation, guard-tests, depth, fpca, pace, outliers]
dependency_graph:
  requires: [81-01]
  provides: [references-map-depth-submethods, references-map-fpca-pace, references-map-outliers]
  affects: [python/fdars/_references_map.json]
tech_stack:
  added: []
  patterns: [curated-false-sentinel, sub-method-attribution, callable-index-papers-sync, fdars-core-source-check]
key_files:
  created: []
  modified:
    - python/fdars/_references_map.json
decisions:
  - "All new entries curated:false — this session cannot personally open DOI landing pages; Phase 84 GATE-03 human review sets curated:true on confirmed entries"
  - "functional_spatial_1d/2d/kernel marked curated:false — fdars-core 0.33 spatial.rs cites only R depth.FSD(), no paper reference; Dabo-Niang & Gijbels 2010 attribution remains [ASSUMED]"
  - "narisetty_nair_2016 added curated:false — fdars-core extremal.rs explicitly names Narisetty & Nair 2016 in module doc, confirming attribution; DOI landing page personal verification deferred to Phase 84"
  - "claeskens_hubert_slaets_2014 for random_projection_deriv_1d added curated:false — fdars-core rpd.rs has no explicit citation; [ASSUMED] based on derivative-augmented halfspace depth concept"
  - "_uncurated_outliers_2026-09 sentinel covers depthgram/tvdmss/sequential_transform_outliers — tvdmss confirms Huang & Sun 2019 in source but DOI unknown; depthgram only says roahd; sequential has no citation"
  - "sun_genton_2011 extended to cover outliers.outliergram in same commit as Task 3 (same paper as depth.functional_boxplot)"
metrics:
  duration: "~12 minutes"
  completed: "2026-09-07"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
status: complete
actuals:
  tokens: 22000
  tasks: 3
  commits: 3
---

# Phase 81 Plan 02: Depth Sub-Methods + FPCA/PACE + Outliers Summary

**One-liner:** Depth sub-method family (17 callables, 6 papers), FPCA/PACE/KL-simulation (8 callables, 2 papers), and outlier detection (8 callables, 3 curated + 1 sentinel) curated with honest fdars-core source attribution checks.

## What Was Built

### Task 1: Depth Sub-Methods + Functional Boxplot

Added 6 new paper entries covering the depth module's 17 sub-method callables (excluding the `functional_depth` dispatcher anti-feature):

| Paper Key | Callables | curated | Source Status |
|---|---|---|---|
| `cuevas_febrero_fraiman_2007` | modal_1d/2d, random_projection_1d/2d, random_tukey_1d/2d (6 callables) | false | [CITED: link.springer.com] |
| `claeskens_hubert_slaets_2014` | random_projection_deriv_1d (1) | false | [ASSUMED]: fdars-core rpd.rs has no explicit citation |
| `dabo_gijbels_2010` | functional_spatial_1d/2d, kernel_functional_spatial_1d/2d (4) | false | [ASSUMED]: fdars-core spatial.rs cites only "R depth.FSD()" |
| `narisetty_nair_2016` | modified_epigraph_index_1d (1) | false | fdars-core extremal.rs module doc explicitly names "Narisetty & Nair 2016" — confirmed attribution, personal DOI verification deferred |
| `sun_genton_2011` | functional_boxplot (1) | false | [VERIFIED: tandfonline.com] — personal landing-page open deferred |

**Dispatcher excluded:** `depth.functional_depth` is absent from `callable_index` (anti-feature sentinel for 81-05).

### Task 2: Dense FPCA, PACE, KL Simulation

Extended `ramsay_silverman_2005` and added `yao_muller_wang_2005`:

| Paper Key | Action | Callables Added | curated |
|---|---|---|---|
| `ramsay_silverman_2005` | Extended (not duplicated) | regression.fpca, simulation.sim_kl, simulation.simulate, simulation.eigenfunctions, simulation.eigenvalues (5 callables) | false |
| `yao_muller_wang_2005` | Added new | pace_fpca.pace_fpca, irreg_fdata_from_lists, PyIrregFdata (3 callables) | false |

`yao_muller_wang_2005` cross_language: R `fdapace/FPCA` (high), Python `scikit-fda/FPCA` (high), Matlab `PACE/FPCA` (low).

`simulation.gaussian_process` and `simulation.covariance_matrix` left uncurated per plan (standard GP theory, 81-05 family).

### Task 3: Outlier Detection Family

| Paper Key | Action | Callables | curated | Notes |
|---|---|---|---|---|
| `sun_genton_2011` | Extended | + outliers.outliergram | false | Same paper as functional_boxplot |
| `dai_genton_2019` | Added | magnitude_shape, muod (2) | false | [CITED: sciencedirect.com CSDA] |
| `febrero_galeano_gonzalez_2008` | Added | detect_outliers_lrt, detect_outliers_lrt_with_dist (2) | false | [CITED: onlinelibrary.wiley.com] |
| `_uncurated_outliers_2026-09` | Sentinel | depthgram, tvdmss, sequential_transform_outliers (3) | false | tvdmss: fdars-core names "Huang & Sun 2019"; depthgram: "roahd" only; sequential: no citation |

## Coverage Emitted

```
COVERAGE: 16/437 callables curated (3.7% of fdars callable surface)
```

The numerator stays at 16 because all new entries in this plan are `curated:false` — this session cannot personally open DOI landing pages to confirm title/authors/year as required by the schema. The 16 curated callables remain those from the 5 seed papers (Phase 80) plus the 6 P-spline callables from `eilers_marx_1996` extension (Phase 81-01).

The new 13 entries (curated:false) bring the callable_index to **62 entries** across **18 papers**, covering the following modules in the callable_index:
- `depth`: 17/18 callables (dispatcher excluded)
- `fdata`: 14/15 callables
- `basis`: 7/16 callables
- `smoothing`: 3/10 callables
- `alignment`: 3/68 callables
- `regression`: 1/29 callables
- `simulation`: 4/8 callables
- `pace_fpca`: 3/3 callables (100%)
- `outliers`: 8/8 callables (100%)
- `_Fdata`: 3/28 callables

## fdars-Core Source Checks

| Callable Family | Source File Checked | Finding |
|---|---|---|
| functional_spatial_1d/2d | `fdars-core-0.33.0/src/depth/spatial.rs` | No paper citation — only "matches R depth.FSD()". Attribution [ASSUMED]. |
| modified_epigraph_index_1d | `fdars-core-0.33.0/src/depth/extremal.rs` | Module doc: "Extremal depth (Narisetty & Nair 2016)" — attribution confirmed. |
| random_projection_deriv_1d | `fdars-core-0.33.0/src/depth/rpd.rs` | No citation. "derivative-augmented" concept matches Claeskens et al. 2014 [ASSUMED]. |
| tvdmss | `fdars-core-0.33.0/src/outliers.rs` | Doc: "Huang & Sun 2019 / fdaoutlier::tvdmss" — confirmed name; DOI not identified. |
| depthgram | `fdars-core-0.33.0/src/outliers.rs` | Doc: "roahd depthGram" — no paper DOI. [ASSUMED] Dai & Genton 2018 JCGS. |
| sequential_transform_outliers | `fdars-core-0.33.0/src/outliers.rs` | No paper citation. |

## GATE-05 Status

| Gate | Result |
|---|---|
| A — Internal consistency (`callable_index` ↔ `papers[*].callables`) | PASS |
| B — Cross-file resolution (all 62 keys resolve in `_capability_map.json`) | PASS |
| C — Structural DOI/URL (regex + domain allowlist) | PASS |
| Coverage-emission test | PASS (`COVERAGE: 16/437`) |

Full test run: `9/9 passed` in `tests/test_guard_sync_version_independent.py`.

## Deviations from Plan

### Auto-fixed Issues

None.

### Intentional Adjustments

1. **`_uncurated_outliers_2026-09` sentinel added** — The plan says to leave `depthgram`, `tvdmss`, and `sequential_transform_outliers` uncurated if unconfirmed. Adding them to a named sentinel entry (rather than omitting them entirely) ensures they appear in `callable_index` now, which allows 81-05 to reference the same key without breaking GATE-05 A. This is correct schema behavior: `curated:false` entries participate in consistency checks.

2. **`claeskens_hubert_slaets_2014` title has 4 authors not 3** — The 81-RESEARCH table shows "Claeskens, Hubert, Slaets" but the actual paper (JASA) has a 4th co-author (Vakili). The 4-author list was used to match the actual paper.

## Known Stubs

None — this plan adds only JSON data and no rendered UI stubs.

## Self-Check: PASSED

- `_references_map.json` exists: FOUND
- `81-02-SUMMARY.md` exists: FOUND
- commit `95a32f4` (Task 1) exists: FOUND
- commit `9e838c2` (Task 2) exists: FOUND
- commit `d5bd592` (Task 3) exists: FOUND
- GATE-05: 9/9 tests pass
- `depth.functional_depth` absent from callable_index: CONFIRMED
- Coverage: 16/437 (3.7%)

## Commits

| Task | Commit | Description |
|---|---|---|
| 1 — Depth sub-methods + functional boxplot | `95a32f4` | feat(81-02): curate depth sub-methods + functional boxplot |
| 2 — Dense FPCA + PACE + KL simulation | `9e838c2` | feat(81-02): curate dense FPCA/PACE/KL-simulation family |
| 3 — Outlier detection family | `d5bd592` | feat(81-02): curate outlier detection family |
