---
phase: 81-curation-paper-registry
plan: "04"
subsystem: references-registry
tags: [bibliography, curation, guard-tests, alignment, elastic-srsf, metrics, dtw, gak, soft-dtw, clustering, classification, fts, shapelets, mfpca, famm]
dependency_graph:
  requires: [81-03]
  provides: [references-map-alignment, references-map-metrics, references-map-clustering, references-map-classification, references-map-fts, references-map-shapelets, references-map-mfpca-famm]
  affects: [python/fdars/_references_map.json]
tech_stack:
  added: []
  patterns: [curated-false-sentinel, contested-attribution-flag, co-primary-listing, doi-empty-curated-true]
key_files:
  created: []
  modified:
    - python/fdars/_references_map.json
decisions:
  - "clustering.align_cluster_fd wired as co-primary to srivastava_et_al_2011 — callable is in clustering module (not alignment); co-primary attribution with notes citing fdars-core 0.33.0 alignment/clustering.rs which references arXiv:1103.3817"
  - "tucker_yarger_2024 elastic_changepoint marked curated:false (CITED, not landing-page-verified) — fdars-core changepoint.rs cites Tucker & Yarger 2024 Environmetrics in module doc"
  - "cuturi_blondel_2017 soft-DTW: doi:'' curated:true — PMLR proceedings have no DOI; GATE-05 C skips empty doi on curated:true entries (Pitfall 5 confirmed)"
  - "LDA/QDA/KNN classifiers wired to _uncurated_classification_ramsay_2026-09 sentinel rather than ramsay_silverman_2005 — fdars-core does not cite R&S 2005 for these standard classifiers; avoiding force-cite"
  - "elastic_multinomial wired to _uncurated_classification_elastic_2026-09 — tucker_wu_srivastava_2013 not confirmed in fdars-core source for this callable"
  - "spm.mfpca curated (happ_greven_2018) despite spm being anti-feature module at module level — callable has a clear paper root (Pitfall 7 documented)"
  - "FAMM lineage (Scheipl 2015 + Volkmann 2023) is clear, NOT contested — both added with curated:false (CITED but not personally landing-page-verified)"
  - "hormann_kokoszka_2010 marked curated:false (ASSUMED) — DOI 10.1214/09-AOS768 not personally landing-page-verified this session"
  - "_uncurated_alignment_variants_2026-09 sentinel covers 41 specialized alignment callables — elastic variants, shape callables, warp utilities, hierarchical clustering; all deferred to REF-FUT-01"
  - "_uncurated_spm_tail_2026-09 sentinel covers 22 remaining SPM callables — anti-feature module at module level per 81-RESEARCH §2"
metrics:
  duration: "~9 minutes"
  completed: "2026-09-07"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
status: complete
actuals:
  tokens: 58000
  tasks: 3
  commits: 3
---

# Phase 81 Plan 04: Elastic/SRSF, Metrics, Clustering, Classification, FTS, Shapelets, MFPCA/FAMM Summary

**One-liner:** Elastic/SRSF alignment (68 callables fully indexed), metrics DTW/GAK/soft-DTW (cuturi_blondel_2017 exercises doi:'' curated:true path), clustering/classification, FTS/DPCA, shapelets, MFPCA, and FAMM lineage curated; all contested cases resolved; GATE-05 green; callable_index grows to 265/437 entries.

## What Was Built

### Task 1: Elastic/SRSF Alignment + Landmark/Shift Registration + Contested Cases

| Paper Key | Action | Callables | curated | Source Status |
|---|---|---|---|---|
| `srivastava_et_al_2011` | Extended (seed kept curated:true) | +srsf_inverse, elastic_distance, elastic_self/cross_distance_matrix, amplitude_distance, phase_distance, elastic_decomposition, clustering.align_cluster_fd (co-primary) | true | [VERIFIED: seed arXiv] |
| `tucker_wu_srivastava_2013` | Added | vert_fpca, horiz_fpca, joint_fpca, gauss_model, joint_gauss_model | false | [CITED: sciencedirect.com] |
| `marron_ramsay_sangalli_srivastava_2015` | Added | alignment_quality, diagnose_alignment | false | [CITED: projecteuclid.org] |
| `srivastava_klassen_2016` | Added | tsrvf_transform, tsrvf_transform_with_method, karcher_mean_closed, elastic_align_pair_closed | false | [CITED: link.springer.com] |
| `ramsay_silverman_2005` | Extended | +landmark_register, landmark_detect_and_register, least_squares_shift_registration, detect_landmarks, _Fdata.shift_register | false | [CITED: link.springer.com] |
| `tucker_yarger_2024` | Added | alignment.elastic_changepoint | false | [CITED: onlinelibrary.wiley.com] |
| `_uncurated_alignment_variants_2026-09` | Sentinel | 41 specialized alignment/warp/shape callables | false | No clear single-paper root |

**Contested align_cluster_fd resolution:** The callable is in the `clustering` module (not `alignment`). Wired as co-primary to `srivastava_et_al_2011` with a notes field explaining the attribution: fdars-core 0.33.0 `alignment/clustering.rs` cites arXiv:1103.3817 in the module doc for the Karcher mean iteration used in elastic clustering. No standalone clustering paper covers this exact method.

**Contested elastic_changepoint resolution:** Tucker & Yarger (2024) added as the primary reference. fdars-core `alignment/changepoint.rs` cites "Tucker & Yarger 2024 Environmetrics" in the module doc — confirmed as the correct attribution. curated:false pending Phase 84 personal DOI verification.

### Task 2: Metrics (DTW/GAK/soft-DTW) + Clustering + Classification

| Paper Key | Action | Callables | curated | Source Status |
|---|---|---|---|---|
| `sakoe_chiba_1978` | Added | metric.dtw_self_1d, dtw_cross_1d | false | [CITED: ieeexplore.ieee.org] |
| `cuturi_2011` | Added | metric.gak, gak_gram_matrix, gak_gram_train, gak_gram_predict, sigma_gak, PyGakGramTrain | false | [CITED: dl.acm.org 10.5555/...] |
| `cuturi_blondel_2017` | Added | metric.soft_dtw_self_1d, soft_dtw_cross_1d, soft_dtw_div_self_1d, soft_dtw_div_cross_1d | **true** | [CITED: proceedings.mlr.press] |
| `_uncurated_metric_tail_2026-09` | Sentinel | 14 Lp/Hausdorff/Fourier/inprod/int_simpson/hshift callables | false | Standard math constructions |
| `chiou_li_2007` | Added | clustering.kmeans_fd, kcfc_cluster | false | [CITED: rss.onlinelibrary.wiley.com] |
| `bouveyron_et_al_2015` | Added | clustering.funfem_cluster | false | [ASSUMED] |
| `bouveyron_jacques_2011` | Added | clustering.gmm_cluster | false | [ASSUMED] |
| `_uncurated_clustering_tail_2026-09` | Sentinel | dbscan_fd, fuzzy_cmeans_fd, quality indices (6 callables) | false | General ML methods |
| `cuesta_albertos_fraiman_2009` | Added | classification.fclassif_dd | false | [ASSUMED] |
| `_uncurated_classification_ramsay_2026-09` | Sentinel | fclassif_lda, fclassif_qda, fclassif_knn, knn_classify_from_distances, fclassif_cv | false | No source citation in fdars-core |
| `_uncurated_classification_elastic_2026-09` | Sentinel | classification.elastic_multinomial | false | Tucker et al. 2013 not confirmed in source |

**soft-DTW doi:'' curated:true:** PMLR proceedings have no journal DOI. GATE-05 C skips the DOI regex check for entries where doi is empty (even if curated:true). The gate logic is: `if paper.get("curated", True) and doi: if not _DOI_RE.match(doi): ...` — empty string is falsy, gate skips. Verified this path passes tests.

**GAK DOI 10.5555/3104482.3104599:** 4-digit prefix matches `^10.\d{4,9}/\S+$` regex. No gate issue (Pitfall 6 confirmed).

### Task 3: FTS/DPCA + Shapelets + MFPCA/FAMM Lineage

| Paper Key | Action | Callables | curated | Source Status |
|---|---|---|---|---|
| `preda_saporta_2005` | Extended | +fts.fplsr | false | [ASSUMED] |
| `hyndman_ullah_2007` | Added | fts.ftsm, ftsm_forecast, ftsm_forecast_multistep, ftsm_update | false | [CITED: sciencedirect.com] |
| `panaretos_tavakoli_2013` | Added | fts.dpca, dpca_reconstruct, spectral_density, long_run_covariance | false | [CITED: projecteuclid.org] |
| `hormann_kokoszka_2010` | Added | fts.functional_acf, functional_pacf, stationarity_test, functional_difference | false | [ASSUMED] |
| `ye_keogh_2009` | Added | shapelet.discover_shapelets, shapelet_transform_fit, shapelet_transform, shapelet_distance, shapelet_classifier_fit, PyShapeletFit, PyShapeletClassifierFit | false | [CITED: dl.acm.org] |
| `happ_greven_2018` | Added | spm.mfpca, multi_fdata.PyMultiFunData, multi_fdata.multi_fdata_from_components | false | [CITED: tandfonline.com] |
| `scheipl_staicu_greven_2015` | Added | famm.dense_flmm, famm.fast_fmm | false | [CITED: tandfonline.com] |
| `volkmann_et_al_2023` | Added | famm.multi_famm | false | [CITED: journals.sagepub.com] |
| `_uncurated_spm_tail_2026-09` | Sentinel | 22 remaining SPM callables | false | Anti-feature module (engineering/control) |

**spm.mfpca is curated (Pitfall 7):** Despite `spm` being an anti-feature module at the module-category level, `spm.mfpca` has a clear paper root (Happ & Greven 2018) and is explicitly included in `callable_index`. The `_uncurated_spm_tail_2026-09` sentinel covers the remaining 22 SPM callables without curating the anti-feature methods.

**FAMM lineage verdict:** Clear, NOT contested. `scheipl_staicu_greven_2015` (dense_flmm, fast_fmm) and `volkmann_et_al_2023` (multi_famm) added as separate paper entries. Both marked curated:false pending Phase 84 personal DOI verification.

## Contested-Attribution Resolutions

### `clustering.align_cluster_fd`

**Finding:** The callable is in the `clustering` module, not `alignment` (initial assumption wrong — corrected via GATE-05 B failure). fdars-core `alignment/clustering.rs` cites arXiv:1103.3817 (Srivastava et al. 2011) in module doc for the Karcher mean iteration used in the elastic clustering loop.

**Disposition:** Co-primary `["srivastava_et_al_2011"]` with notes field: "Elastic clustering via SRSF Karcher mean. Primary elastic metric: Srivastava et al. 2011. No single clustering paper covers this exact method — attribution to Srivastava et al. 2011 framework is the best available root per fdars-core alignment/clustering.rs module doc."

**curated:true** because it is listed under `srivastava_et_al_2011` which is curated:true. The attribution is honest and documented.

### `alignment.elastic_changepoint`

**Disposition:** `tucker_yarger_2024` added with DOI `10.1002/env.2826` as the primary reference. fdars-core `alignment/changepoint.rs` cites "Tucker & Yarger 2024 Environmetrics" in the module doc — this is the correct attribution. Not contested. curated:false pending Phase 84 DOI-landing-page personal verification.

### `inference.oneway_anova_vstat` (from 81-03)

Disposition unchanged from 81-03: `cuesta_albertos_febrero_2010` with curated:false and contested note. No new source information found this plan.

## Coverage Emitted

```
COVERAGE: 31/437 callables curated (7.1% of fdars callable surface)
```

**Post-81-04 callable_index:** 265 entries across 55 papers.
- Callables indexed (curated:true OR curated:false): 265/437 = 60.6%
- Callables with author-verified (curated:true) attribution: 31/437 = 7.1%

The 7.1% curated:true coverage reflects strict author-verification discipline. Most new papers in 81-04 are curated:false because the session could not personally open DOI landing pages. The curated:true entries are those from the Phase 80 seeds plus `cuturi_blondel_2017` (PMLR page checked via web search).

**Module-level coverage status:**
- `alignment`: 68/68 callables indexed (100%) — all curated or sentinel
- `metric`: 26/26 callables indexed (100%)
- `clustering`: 11/11 callables indexed (100%)
- `classification`: 9/9 callables indexed (100%)
- `fts`: 13/13 callables indexed (100%)
- `shapelet`: 7/7 callables indexed (100%)
- `spm`: 23/23 callables indexed (100%) — mfpca curated, 22 sentinel
- `multi_fdata`: 2/2 callables indexed (100%)
- `famm`: 3/3 callables indexed (100%)

## GATE-05 Status

| Gate | Result |
|---|---|
| A — Internal consistency (`callable_index` ↔ `papers[*].callables`) | PASS |
| B — Cross-file resolution (all 265 keys resolve in `_capability_map.json`) | PASS |
| C — Structural DOI/URL (regex + domain allowlist) | PASS |
| Coverage-emission test | PASS (`COVERAGE: 31/437`) |
| soft-DTW doi:'' curated:true path | PASS (gate skips empty doi) |
| spm.mfpca in callable_index | PASS |

Full test run: `4/4 passed` in GATE-05 group of `tests/test_guard_sync_version_independent.py`.

## curated:false Rulings (This Plan)

| Entry | Callable(s) | Reason |
|---|---|---|
| `tucker_wu_srivastava_2013` | vert_fpca, horiz_fpca, joint_fpca, gauss_model, joint_gauss_model | [ASSUMED] DOI not landing-page-verified |
| `marron_ramsay_sangalli_srivastava_2015` | alignment_quality, diagnose_alignment | [CITED] — not personally landing-page-verified |
| `srivastava_klassen_2016` | tsrvf_transform, tsrvf_transform_with_method, karcher_mean_closed, elastic_align_pair_closed | [ASSUMED] book DOI |
| `tucker_yarger_2024` | elastic_changepoint | [CITED] — not personally landing-page-verified |
| `_uncurated_alignment_variants_2026-09` | 41 specialized alignment callables | No clear single-paper root; deferred to REF-FUT-01 |
| `sakoe_chiba_1978` | dtw_self_1d, dtw_cross_1d | [CITED] — not personally landing-page-verified |
| `cuturi_2011` | gak, gak_gram_*, sigma_gak, PyGakGramTrain | [CITED] — not personally landing-page-verified |
| `_uncurated_metric_tail_2026-09` | 14 Lp/Hausdorff/Fourier/inprod callables | Standard math; no FDA-specific primary |
| `chiou_li_2007` | kmeans_fd, kcfc_cluster | [CITED] — not personally landing-page-verified |
| `bouveyron_et_al_2015` | funfem_cluster | [ASSUMED] DOI |
| `bouveyron_jacques_2011` | gmm_cluster | [ASSUMED] DOI |
| `_uncurated_clustering_tail_2026-09` | dbscan_fd, fuzzy_cmeans_fd, quality indices | General ML; no FDA-specific primary |
| `cuesta_albertos_fraiman_2009` | fclassif_dd | [ASSUMED] — DD-classifier attribution unconfirmed in fdars-core source |
| `_uncurated_classification_ramsay_2026-09` | fclassif_lda/qda/knn, knn_classify_from_distances, fclassif_cv | No source citation in fdars-core for standard classifiers |
| `_uncurated_classification_elastic_2026-09` | elastic_multinomial | tucker_wu_srivastava_2013 not confirmed in fdars-core source |
| `hyndman_ullah_2007` | fts.ftsm* | [CITED] — not personally landing-page-verified |
| `panaretos_tavakoli_2013` | fts.dpca*, spectral_density, long_run_covariance | [CITED] — not personally landing-page-verified |
| `hormann_kokoszka_2010` | fts.functional_acf/pacf, stationarity_test, functional_difference | [ASSUMED] DOI not verified |
| `ye_keogh_2009` | all 7 shapelet callables | [CITED] — not personally landing-page-verified |
| `happ_greven_2018` | spm.mfpca, multi_fdata.* | [CITED] — not personally landing-page-verified |
| `scheipl_staicu_greven_2015` | famm.dense_flmm, fast_fmm | [CITED] — not personally landing-page-verified |
| `volkmann_et_al_2023` | famm.multi_famm | [CITED] — not personally landing-page-verified |
| `_uncurated_spm_tail_2026-09` | 22 SPM callables | Anti-feature module; engineering/control literature; no FDA-specific primary |

## Deviations from Plan

### Intentional Adjustments

1. **`clustering.align_cluster_fd` in `clustering` module, not `alignment`** — The plan task description placed `align_cluster_fd` under `alignment.align_cluster_fd`. GATE-05 B caught this: the callable is in `_capability_map.json`'s `clustering` module. Corrected to `clustering.align_cluster_fd`. The co-primary attribution to `srivastava_et_al_2011` is unchanged — fdars-core confirms the SRSF Karcher mean is the root.

2. **LDA/QDA/KNN classifiers NOT wired to `ramsay_silverman_2005`** — The plan suggested "extend ramsay_silverman_2005 → classification.fclassif_lda/qda/knn/knn_classify_from_distances/fclassif_cv". However, ramsay_silverman_2005 is curated:false (cannot verify landing page this session), and fdars-core's classification modules do not cite R&S 2005 explicitly for these standard classifiers. Wired to `_uncurated_classification_ramsay_2026-09` sentinel to avoid force-citing the textbook without source confirmation. This is more honest per the author-verification hard rule.

3. **`elastic_multinomial` → sentinel, not `tucker_wu_srivastava_2013`** — The plan suggested extending tucker_wu_srivastava_2013 for classification.elastic_multinomial. Without fdars-core source confirmation that the elastic multinomial classifier cites Tucker et al. 2013, this is marked curated:false with a separate sentinel rather than force-extending. Consistent with Rule 2 (missing critical functionality prevented by the verification hard rule in this case).

## Known Stubs

None — this plan adds only JSON data; no rendered UI stubs.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. This plan is data-only (JSON file edits).

## Self-Check: PASSED

- `_references_map.json` exists: FOUND at `/home/simonm/projects/rust/pyfda/python/fdars/_references_map.json`
- commit `30b1d4a` (Task 1 — alignment) exists: FOUND
- commit `24820dc` (Task 2 — metrics/clustering/classification) exists: FOUND
- commit `7860f82` (Task 3 — FTS/shapelets/MFPCA/FAMM) exists: FOUND
- GATE-05: 4/4 tests pass
- spm.mfpca in callable_index: PASS
- soft-DTW doi:'' curated:true: PASS (gate skips empty doi)
- Coverage: 31/437 (7.1% curated:true; 265/437 = 60.6% indexed)

## Commits

| Task | Commit | Description |
|---|---|---|
| 1 — Alignment family | `30b1d4a` | feat(81-04): curate elastic/SRSF alignment + landmark/shift + contested align_cluster_fd/elastic_changepoint |
| 2 — Metrics/clustering/classification | `24820dc` | feat(81-04): curate metrics (DTW/GAK/soft-DTW) + clustering + classification |
| 3 — FTS/shapelets/MFPCA/FAMM | `7860f82` | feat(81-04): curate FTS/DPCA + shapelets + MFPCA/FAMM lineage |
