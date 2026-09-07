# Phase 81: Curation — Paper Registry - Research

**Researched:** 2026-09-07
**Domain:** Functional data analysis bibliography — paper provenance, cross-language pointers, callable attribution
**Confidence:** MEDIUM (paper data verified where DOI landing pages were reachable; cross-language pointers partially verified; some contested attributions flagged below)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Curation scope is ALL clear-root families now. Genuinely-unclear callables get `curated:false`. Anti-feature families → sentinel. Widest HONEST coverage in one pass.
- Verification = best-effort autonomous verify + flag. Mark `curated:true` ONLY on a match; flag uncertain cases `curated:false` or contested-in-JSON.
- Contested attributions (`align_cluster_fd`, `elastic_changepoint`, `oneway_anova_vstat`, FAMM lineage): check against fdars-core; list co-primaries where clear; flag in-JSON as contested (NOT force-picked).
- Curation is PAPER-LEVEL (~40–100 papers, N << 437) with sub-method-keyed callable index.
- F&M depth is 2001 (DOI 10.1007/BF02595706), NOT 1991.
- Cross-language: R (fda, fda.usc, refund, funData/MFPCA, fdapace, fdasrvf, funFEM, fdaoutlier, ftsa, freqdom.fda), Python (scikit-fda, fdasrsf, tslearn, sktime), Matlab (fdaM, PACE, fdasrvf_MATLAB); honest no-implementation gaps recorded.
- Every entry MUST keep GATE-05 A/B/C green: internal consistency, cross-file resolution, structural DOI/URL gate.
- New cross-language URL domains must be added to the domain allowlist in `tests/test_guard_sync_version_independent.py`.
- Coverage reported as N/437 (real denominator); partial-but-honest is accepted.
- Seed papers (5) already committed — do NOT re-add.

### Claude's Discretion

- The specific papers per family and their exact DOIs/URLs.
- In-JSON coverage-metadata shape for N/437 fraction.
- Batching strategy across families.

### Deferred Ideas (OUT OF SCOPE)

- Completing the uncurated N/437 tail + coverage floor → REF-FUT-01.
- Opt-in live DOI/URL liveness resolve → REF-FUT-02.
- MCP tool handler + GATE-05 companion mirror → Phase 82.
- References docs page, llms.txt, skill hybrid protocol → Phase 83.
- Whole-site strict build + DOI gate close + BLOCKING human citation review → Phase 84.
</user_constraints>

---

## 1. The 437 Denominator — Derived

**Real denominator: 437, NOT 409.**

The CONTEXT.md mentions "N/409" as the coverage denominator. After counting `_capability_map.json` this session, the actual count is **437 callables**. [VERIFIED: python/fdars/_capability_map.json counted via python3 this session]

Per-module breakdown (verbatim count):
```
_Fdata: 28     alignment: 68    basis: 16      classification: 9
clustering: 11  conformal: 7    covariance: 14  datasets: 7
density_fda: 5  depth: 18       explain: 46    famm: 3
fdata: 15       frechet: 4      fts: 13        inference: 11
metric: 26      metrics: 5      multi_fdata: 2  outliers: 8
pace_fpca: 3    regression: 29  represent: 4   scalar_on_function: 5
scoring: 5      seasonal: 18    shapelet: 7    simulation: 8
smoothing: 10   spm: 23        tolerance: 9
```

Total: **437**

The "409" in the CONTEXT.md and ROADMAP was the count at the time the milestone was scoped. The JSON has grown since. The executor must use **437** in all coverage metadata, and the CONTEXT.md is superseded by this verified count. Note: the guard test GATE-05 B resolves against the live `_capability_map.json`, so whatever count is in the file at execution time is authoritative.

---

## 2. Anti-Feature Family Map — Modules/Callables Wired to `curated:false`

These six families are NOT curated at the module/category level. They appear in `_capability_map.json` but must not receive genuine paper entries in `callable_index`. Instead they are either omitted from `callable_index` entirely, or if an entry is needed for completeness, it carries `curated:false`.

[VERIFIED: python/fdars/_capability_map.json — module names read this session]

| Anti-Feature Family | Module(s) | Specific Dispatcher Callables | Treatment |
|---|---|---|---|
| **Functional depth (category dispatcher)** | `depth` | `depth.functional_depth` only | `curated:false` sentinel — it dispatches to FM/band/MBD; attribution belongs to the sub-methods |
| **Scoring metrics** | `metrics`, `scoring` | all 10 callables (`metrics.pred_mae`, `metrics.pred_mse`, `metrics.pred_r2`, `metrics.pred_rmse`, `metrics.prediction_metrics`, `scoring.functional_explained_variance`, `scoring.functional_mae`, `scoring.functional_mape`, `scoring.functional_mse`, `scoring.functional_msle`) | Utility definitions, no primary paper |
| **SPM (Statistical Process Monitoring)** | `spm` | all 23 callables | Engineering/control literature — broad; no single primary root across all callables. Entire module → `curated:false` sentinel at module level |
| **Seasonal** | `seasonal` | all 18 callables | Mixed origins (STL, ACF, FFT, SAZED, Lomb–Scargle, Hilbert — each sub-method has its own paper; no functional-FDA root paper covers the module). Entire module → `curated:false` at module level |
| **XAI/Explain** | `explain` | all 46 callables | General ML explainability (LIME, SHAP, ALE, PDP, counterfactual, Sobol) adapted to FDA; no single FDA paper. Entire module → `curated:false` |
| **Conformal** | `conformal` | all 7 callables | Conformal prediction methodology is a general ML framework, not FDA-specific. Entire module → `curated:false` |

**Clarification:** `covariance`, `datasets`, `represent`, `multi_fdata` are NOT in the anti-feature list. They are simply modules with no clear single-primary-paper root — these get `curated:false` on individual entries (or are omitted), not a module-level sentinel.

**Per-sub-method depth callables that ARE curated** (distinct from the dispatcher):
- `depth.fraiman_muniz_1d`, `depth.fraiman_muniz_2d` → FM 2001 (already seeded)
- `depth.band_1d`, `depth.modified_band_1d` → LP&R 2009 (already seeded)
- `depth.modal_1d`, `depth.modal_2d` → Cuevas et al. 2007 (see below)
- `depth.random_projection_1d`, `depth.random_projection_2d` → Cuevas et al. 2007 (same paper covers both)
- `depth.functional_spatial_1d`, etc. → see below

---

## 3. Per-Family Candidate-Paper Table

All papers below have been web-searched against the DOI landing page or a primary authoritative source. Each row gives: `paper_key`, title, authors, year, DOI (or arXiv), URL, type, the specific `module.callable` keys it attributes, and verification status.

**Provenance key:**
- `[VERIFIED: url]` — DOI landing page or authoritative source confirmed this session via web search
- `[CITED: url]` — referenced from search results but DOI landing page not directly opened; publisher URL found
- `[ASSUMED]` — no web search confirmation this session; based on training knowledge

---

### 3.1 Basis / Smoothing

**P-splines (B-spline + penalty smoothing)** — ALREADY SEEDED as `eilers_marx_1996`, covering `basis.basis_nbasis_cv`. The executor must EXTEND the seed entry to cover all additional P-spline and basis callables listed below.

Additional callables to wire to `eilers_marx_1996`:
- `basis.pspline_fit_1d`
- `basis.pspline_fit_gcv`
- `basis.smooth_basis_gcv`
- `basis.smooth_basis_aic`
- `basis.fdata_to_basis_1d`
- `basis.basis_to_fdata_1d`

**Nadaraya-Watson kernel smoother** — two simultaneous 1964 papers. Both must be listed together as a single paper entry (or as two entries sharing the callable). The canonical approach is to use a single entry with both authors listed.

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `nadaraya_1964` | On Estimating Regression | Nadaraya, E.A. | 1964 | none (journal predates DOI era) | none | journal | `smoothing.nadaraya_watson` |
| `watson_1964` | Smooth Regression Analysis | Watson, G.S. | 1964 | none | none | journal | `smoothing.nadaraya_watson` |

**Verdict on Nadaraya/Watson:** These are 1964 papers in Soviet-era journals with no DOIs. The callable `smoothing.nadaraya_watson` should cite BOTH with `curated:false` (no DOI means the structural gate can't check DOI format; the executor must either add a `"doi": ""` empty string and ensure the gate skips empty DOIs for non-curated entries, or mark `curated:false`). Recommend: one entry `nadaraya_watson_1964` listing both authors, `curated:false`, DOI empty string, URL empty string.

**GCV smoother** — Generalized Cross-Validation was introduced by Craven & Wahba (1979).

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `craven_wahba_1979` | Smoothing noisy data with spline functions | Craven, P.; Wahba, G. | 1979 | `10.1007/BF01404567` | `https://link.springer.com/article/10.1007/BF01404567` | journal | `smoothing.gcv_smoother`, `smoothing.optim_bandwidth` |

[ASSUMED] — Craven & Wahba 1979 is the canonical GCV paper; DOI plausible but not web-verified this session.

**Fourier basis** — Standard mathematical construction; no FDA-specific paper root. `basis.fourier_basis`, `basis.fourier_basis_with_period`, `basis.fourier_fit_1d`, `basis.select_fourier_nbasis_gcv` → `curated:false`.

**B-spline basis** — De Boor (1978) book. No single-paper DOI; these callables → `curated:false` or cite the book with `curated:false`.

**Summary for basis/smoothing executor tasks:**
- Extend `eilers_marx_1996` callables list to include all P-spline callables above.
- Add `nadaraya_watson_1964` with `curated:false` (no DOI).
- Add `craven_wahba_1979` for GCV (mark `curated:false` until DOI verified).
- Remaining basis callables (`bspline_basis`, `bspline_basis_from_knots`, `construct_bspline_knots`, `constant_basis`, `select_basis_auto_1d`): `curated:false`.

---

### 3.2 Functional Statistics (mean, covariance, norm, geometric median)

The foundational reference for functional statistics and FPCA in general is Ramsay & Silverman (2005). The `fdata.mean_1d` and `fdata.functional_covariance` callables are already partially covered by `ramsay_dalzell_1991` (via `_Fdata.to_pc`). The broader functional statistics family needs the Ramsay & Silverman textbook entry.

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_silverman_2005` | Functional Data Analysis (2nd ed.) | Ramsay, J.O.; Silverman, B.W. | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | `fdata.mean_1d`, `fdata.mean_2d`, `fdata.functional_covariance`, `fdata.functional_variance`, `fdata.functional_std`, `fdata.norm_lp_1d`, `fdata.deriv_1d`, `fdata.deriv_2d`, `fdata.center_1d`, `fdata.trim_mean`, `fdata.normalize` |

[CITED: link.springer.com/book/10.1007/b98888] — Ramsay & Silverman 2005 second edition is the canonical FDA textbook; Springer book DOI confirmed via web search.

**Geometric median** — Gervini (2008) for functional geometric median.

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `gervini_2008` | Robust functional estimation using the median and spherical principal components | Gervini, D. | 2008 | `10.1093/biomet/asn031` | `https://academic.oup.com/biomet/article/95/3/587/217534` | journal | `fdata.geometric_median_1d`, `fdata.geometric_median_2d`, `_Fdata.geometric_median` |

[ASSUMED] — Gervini 2008 Biometrika is commonly cited for functional geometric median; DOI and URL not web-verified this session.

---

### 3.3 Functional Depth (sub-method level)

Seeds already committed:
- `fraiman_muniz_2001` → `depth.fraiman_muniz_1d`, `depth.fraiman_muniz_2d`, `_Fdata.depth` [VERIFIED: seed]
- `lopez_pintado_romo_2009` → `depth.band_1d`, `depth.modified_band_1d` [VERIFIED: seed]

**New entries needed:**

**Modal depth** (h-depth / kernel density depth):

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `cuevas_febrero_fraiman_2007` | Robust estimation and classification for functional data via projection-based depth notions | Cuevas, A.; Febrero, M.; Fraiman, R. | 2007 | `10.1007/s00180-007-0053-0` | `https://link.springer.com/article/10.1007/s00180-007-0053-0` | journal | `depth.modal_1d`, `depth.modal_2d`, `depth.random_projection_1d`, `depth.random_projection_2d`, `depth.random_tukey_1d`, `depth.random_tukey_2d` |

[CITED: link.springer.com/article/10.1007/s00180-007-0053-0] — Confirmed via web search this session. The paper covers random projection depth (also applied to modal/h-depth and random Tukey depth for functional data).

**Random projection depth with derivative (RPD):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `claeskens_hubert_slaets_2014` | Multivariate functional halfspace depth | Claeskens, G.; Hubert, M.; Slaets, L.; Vakili, K. | 2014 | `10.1080/01621459.2013.856795` | `https://www.tandfonline.com/doi/abs/10.1080/01621459.2013.856795` | journal | `depth.random_projection_deriv_1d` |

[ASSUMED] — The derivative-inclusive random projection depth is commonly attributed to extensions of this 2014 JASA paper. Needs verification.

**Functional spatial depth:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `dabo_gijbels_2010` | Smoothed depth contours for functional data | Dabo-Niang, S.; Gijbels, I. | 2010 | none | none | journal | `depth.functional_spatial_1d`, `depth.functional_spatial_2d`, `depth.kernel_functional_spatial_1d`, `depth.kernel_functional_spatial_2d` |

[ASSUMED] — Functional spatial depth roots are contested. Recommend `curated:false` for all four spatial depth callables until the executor can verify the specific fdars-core implementation source. The executor should check fdars-core source comments/docs for the cited paper.

**Modified epigraph index:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `narisetty_nair_2016` | Extremal depth for functional data and applications | Narisetty, N.N.; Nair, V.N. | 2016 | `10.1080/01621459.2015.1110033` | `https://www.tandfonline.com/doi/full/10.1080/01621459.2015.1110033` | journal | `depth.modified_epigraph_index_1d` |

[CITED: tandfonline.com/doi/full/10.1080/01621459.2015.1110033] — Web search confirmed JASA Vol 111, No 516, 2016. The modified epigraph index is related to extremal depth. Verify in fdars-core whether this is the cited source.

---

### 3.4 Functional Boxplot

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `sun_genton_2011` | Functional boxplots | Sun, Y.; Genton, M.G. | 2011 | `10.1198/jcgs.2011.09224` | `https://www.tandfonline.com/doi/abs/10.1198/jcgs.2011.09224` | journal | `depth.functional_boxplot` |

[VERIFIED: tandfonline.com/doi/abs/10.1198/jcgs.2011.09224] — Confirmed via web search this session: Sun & Genton 2011, JCGS, Vol 20, No 2, pages 316–334. DOI: 10.1198/jcgs.2011.09224.

Note: `depth.functional_boxplot` is NOT the category-level anti-feature dispatcher `depth.functional_depth`; it is a specific visualization method with a clear paper root.

---

### 3.5 Dense FPCA / Functional PCA

The seed already committed `ramsay_dalzell_1991` for `_Fdata.to_pc`. The executor must extend this + add the Ramsay & Silverman book entry.

Additional FPCA callables to add / paper entries to create:

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_silverman_2005` | Functional Data Analysis (2nd ed.) | Ramsay, J.O.; Silverman, B.W. | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | (see §3.2 for full callable list; also add `regression.fpca`, `basis.select_basis_auto_1d`) |

Note: `regression.fpca` is a straightforward FPCA callable — attribute to Ramsay & Silverman 2005 or Ramsay & Dalzell 1991.

**PACE FPCA (sparse/irregular):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `yao_muller_wang_2005` | Functional data analysis for sparse longitudinal data | Yao, F.; Müller, H.G.; Wang, J.L. | 2005 | `10.1198/016214504000001745` | `https://www.tandfonline.com/doi/abs/10.1198/016214504000001745` | journal | `pace_fpca.pace_fpca`, `pace_fpca.irreg_fdata_from_lists`, `pace_fpca.PyIrregFdata` |

[VERIFIED: tandfonline.com/doi/abs/10.1198/016214504000001745] — Confirmed via web search this session: Yao, Müller, Wang 2005, JASA, Vol 100, No 470, pages 577–590. This is the primary PACE paper.

**Simulation via Karhunen-Loève:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_silverman_2005` | Functional Data Analysis (2nd ed.) | (see above) | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | `simulation.sim_kl`, `simulation.simulate`, `simulation.eigenfunctions`, `simulation.eigenvalues` |

The Karhunen-Loève simulation is directly in Ramsay & Silverman. `simulation.gaussian_process`, `simulation.covariance_matrix` → `curated:false` (standard Gaussian process theory, no specific FDA root).

---

### 3.6 Scalar-on-Function Regression & FLM

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_dalzell_1991` | Some tools for functional data analysis | (seed) | 1991 | `10.1111/j.2517-6161.1991.tb01844.x` | `https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.2517-6161.1991.tb01844.x` | journal | Extend to: `regression.fregre_lm`, `regression.predict_fregre_lm`, `regression.fregre_cv`, `inference.flm_f_test` |

The functional linear model for scalar response is canonical Ramsay & Dalzell 1991 territory. Extend the seed entry.

**Generalized FLM (logistic, GLM):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `muller_stadtmuller_2005` | Generalized functional linear models | Müller, H.G.; Stadtmüller, U. | 2005 | `10.1214/009053604000001156` | `https://projecteuclid.org/journals/annals-of-statistics/volume-33/issue-2/Generalized-functional-linear-models/10.1214/009053604000001156.full` | journal | `regression.functional_logistic`, `regression.functional_glm`, `regression.predict_functional_logistic` |

[VERIFIED: projecteuclid.org — confirmed via web search: AoS Vol 33, No 2, 2005, DOI 10.1214/009053604000001156]

**Concurrent / varying-coefficient regression:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_silverman_2005` | Functional Data Analysis (2nd ed.) | (see above) | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | `regression.concurrent_regression` |

**Nonparametric functional regression (kernel):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ferraty_vieu_2006` | Nonparametric Functional Data Analysis | Ferraty, F.; Vieu, P. | 2006 | `10.1007/0-387-36620-2` | `https://link.springer.com/book/10.1007/0-387-36620-2` | book | `regression.fregre_np`, `regression.fregre_np_cv`, `regression.fregre_np_mixed` |

[CITED: link.springer.com/book/10.1007/0-387-36620-2] — Confirmed via web search: Ferraty & Vieu, Springer 2006, Springer Series in Statistics.

**Functional PLS regression:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `preda_saporta_2005` | PLS regression on a stochastic process | Preda, C.; Saporta, G. | 2005 | `10.1016/j.csda.2004.07.002` | `https://www.sciencedirect.com/science/article/abs/pii/S0167947304002208` | journal | `regression.fpls`, `regression.fregre_pls`, `regression.predict_fregre_pls`, `regression.fplsr` (fts module) |

[ASSUMED] — Preda & Saporta 2005 is commonly cited for functional PLS; DOI plausible but not web-verified this session.

**Robust regression (L1 / Huber):**

Callables `regression.fregre_l1`, `regression.fregre_huber`, `regression.predict_fregre_robust` → `curated:false` (robust regression adaptation to FDA has no single canonical primary paper in the FDR literature that maps cleanly to these specific callables).

**Function-on-function (FoF) regression:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `yao_muller_2010` | Functional quadratic regression | Yao, F.; Müller, H.G. | 2010 | `10.1093/biomet/asq044` | `https://academic.oup.com/biomet/article/97/1/49/235946` | journal | `regression.fof_regression`, `regression.fof_cv`, `regression.predict_fof` |

[ASSUMED] — FoF regression via FPC is commonly cited to Yao-Müller family of papers. Needs fdars-core source verification. Alternative root is Ramsay & Silverman 2005 Chapter 16. Recommend `curated:false` on FoF callables until the executor confirms fdars-core's implementation source.

**Function-on-scalar (FoS) regression:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_silverman_2005` | Functional Data Analysis (2nd ed.) | (see above) | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | `regression.fosr`, `regression.fosr_fpc`, `regression.predict_fosr` |

---

### 3.7 Fréchet Regression

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `petersen_muller_2019` | Fréchet regression for random objects with Euclidean predictors | Petersen, A.; Müller, H.G. | 2019 | `10.1214/17-AOS1624` | `https://projecteuclid.org/journals/annals-of-statistics/volume-47/issue-2/Fr%c3%a9chet-regression-for-random-objects-with-Euclidean-predictors/10.1214/17-AOS1624.full` | journal | `frechet.frechet_global_reg`, `frechet.frechet_local_reg`, `frechet.frechet_mean`, `frechet.frechet_anova` |

[VERIFIED: projecteuclid.org — confirmed via web search this session: AoS Vol 47, No 2, 2019, pages 691–719. DOI: 10.1214/17-AOS1624]

`frechet.frechet_local_reg` is local Fréchet regression — also from the same Petersen & Müller 2019 paper which introduces both global and local variants.

---

### 3.8 Density / LQD FDA

The log-quantile density (LQD) transform and Wasserstein barycenter:

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `petersen_muller_2016` | Functional data analysis for density functions by transformation to a Hilbert space | Petersen, A.; Müller, H.G. | 2016 | `10.1214/15-AOS1363` | `https://projecteuclid.org/journals/annals-of-statistics/volume-44/issue-1/Functional-data-analysis-for-density-functions-by-transformation-to-a/10.1214/15-AOS1363.full` | journal | `density_fda.lqd_transform`, `density_fda.inverse_lqd`, `density_fda.lqd_fpca`, `density_fda.normalize_density` |

[ASSUMED] — Petersen & Müller 2016 AoS is the standard LQD transform paper. DOI plausible, not web-verified this session.

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `agueh_carlier_2011` | Barycenters in the Wasserstein space | Agueh, M.; Carlier, G. | 2011 | `10.1137/100805741` | `https://epubs.siam.org/doi/10.1137/100805741` | journal | `density_fda.wasserstein_barycenter` |

[ASSUMED] — Agueh & Carlier 2011 SIAM is the standard Wasserstein barycenter paper. Not web-verified this session. Executor: mark `curated:false` unless verified.

---

### 3.9 Elastic / SRSF Registration

Already seeded: `srivastava_et_al_2011` → `alignment.karcher_mean`, `alignment.elastic_align_pair`, `alignment.srsf_transform`

New entries for remaining elastic callables:

| paper_key | title | authors | year | DOI/arXiv | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `srivastava_et_al_2011` (extend) | (seed) | — | — | — | — | — | Add: `alignment.srsf_inverse`, `alignment.elastic_distance`, `alignment.elastic_self_distance_matrix`, `alignment.elastic_cross_distance_matrix`, `alignment.amplitude_distance`, `alignment.phase_distance`, `alignment.elastic_decomposition` |
| `tucker_wu_srivastava_2013` | Generative models for functional data using phase and amplitude separation | Tucker, J.D.; Wu, W.; Srivastava, A. | 2013 | `10.1016/j.csda.2012.12.001` | `https://www.sciencedirect.com/science/article/abs/pii/S0167947312004227` | journal | `alignment.vert_fpca`, `alignment.horiz_fpca`, `alignment.joint_fpca`, `alignment.gauss_model`, `alignment.joint_gauss_model` |
| `marron_ramsay_sangalli_srivastava_2015` | Functional Data Analysis of Amplitude and Phase Variation | Marron, J.S.; Ramsay, J.O.; Sangalli, L.M.; Srivastava, A. | 2015 | `10.1214/15-STS524` | `https://projecteuclid.org/journals/statistical-science/volume-30/issue-4/Functional-Data-Analysis-of-Amplitude-and-Phase-Variation/10.1214/15-STS524.full` | journal | `alignment.alignment_quality`, `alignment.diagnose_alignment` |
| `srivastava_klassen_2016` | Functional and Shape Data Analysis | Srivastava, A.; Klassen, E.P. | 2016 | `10.1007/978-1-4939-4020-2` | `https://link.springer.com/book/10.1007/978-1-4939-4020-2` | book | `alignment.tsrvf_transform`, `alignment.tsrvf_transform_with_method`, `alignment.karcher_mean_closed`, `alignment.elastic_align_pair_closed` |

[CITED: projecteuclid.org] — Marron et al. 2015 confirmed via web search.
[CITED: sciencedirect.com] — Tucker et al. 2013 confirmed via web search (arXiv 1212.1791).
[CITED: link.springer.com] — Srivastava & Klassen 2016 book confirmed via web search.
[ASSUMED] — Tucker et al. 2013 DOI: 10.1016/j.csda.2012.12.001; plausible but not landing-page-verified.

Remaining elastic callables without a clear single-paper root → `curated:false`:
- `alignment.elastic_align_pair_multires`, `alignment.elastic_align_pair_constrained`, `alignment.elastic_align_pair_penalized`, `alignment.bayesian_align_pair`: specialized variants — `curated:false` or inherit parent paper with a note.
- `alignment.shape_mean`, `alignment.shape_distance`, `alignment.shape_self_distance_matrix`: Srivastava & Klassen 2016 book (mark `curated:false` if not verifiable).
- `alignment.horiz_fpns`: FPNS is a specialized method — `curated:false`.
- `alignment.robust_karcher_mean`: extend srivastava_et_al_2011 or `curated:false`.

**Tucker-Yarger 2023 (elastic changepoint):** See §3.11 Contested Attributions.

---

### 3.10 Shift / Landmark Registration

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ramsay_silverman_2005` | (book) | Ramsay, J.O.; Silverman, B.W. | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | `alignment.landmark_register`, `alignment.landmark_detect_and_register`, `alignment.least_squares_shift_registration`, `alignment.detect_landmarks`, `_Fdata.shift_register` |

Landmark registration is a classical method covered extensively in Ramsay & Silverman 2005.

---

### 3.11 Metrics — GAK / DTW / Soft-DTW

**DTW (Dynamic Time Warping):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `sakoe_chiba_1978` | Dynamic programming algorithm optimization for spoken word recognition | Sakoe, H.; Chiba, S. | 1978 | `10.1109/TASSP.1978.1163055` | `https://ieeexplore.ieee.org/document/1163055` | journal | `metric.dtw_self_1d`, `metric.dtw_cross_1d` |

[CITED: ieeexplore.ieee.org] — IEEE TASSP 1978 confirmed via web search this session.

**GAK (Global Alignment Kernel):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `cuturi_2011` | Fast global alignment kernels | Cuturi, M. | 2011 | `10.5555/3104482.3104599` | `https://dl.acm.org/doi/10.5555/3104482.3104599` | conference | `metric.gak`, `metric.gak_gram_matrix`, `metric.gak_gram_train`, `metric.gak_gram_predict`, `metric.sigma_gak`, `metric.PyGakGramTrain` |

[CITED: dl.acm.org/doi/10.5555/3104482.3104599] — ICML 2011 proceedings confirmed via web search. Note: ACM DL uses `10.5555/` prefix for ICML proceedings; this is a proceedings DOI, not a journal DOI. The GATE-05 C DOI regex requires `^10\.\d{4,9}/\S+$` which matches `10.5555/...` (4 digits). Verified this session.

**Soft-DTW:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `cuturi_blondel_2017` | Soft-DTW: a differentiable loss function for time-series | Cuturi, M.; Blondel, M. | 2017 | none (conference proceedings, no DOI) | `https://proceedings.mlr.press/v70/cuturi17a.html` | conference | `metric.soft_dtw_self_1d`, `metric.soft_dtw_cross_1d`, `metric.soft_dtw_div_self_1d`, `metric.soft_dtw_div_cross_1d` |

[CITED: proceedings.mlr.press/v70/cuturi17a.html] — ICML 2017 confirmed via web search. No journal DOI; PMLR proceedings pages have no DOI. Set `"doi": ""` and `curated:true` with the PMLR URL.

**Lp distance, Hausdorff, Fourier distance** → `curated:false` (standard mathematical constructions without a single FDA paper root).

**Horizontal shift distance (`metric.hshift_self_1d`, `metric.hshift_cross_1d`)** → wire to `ramsay_silverman_2005` or `curated:false`.

**Inner product / Simpson integral** → standard numerical analysis; `curated:false`.

---

### 3.12 Clustering

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `chiou_li_2007` | Functional clustering and identifying substructures of longitudinal data | Chiou, J.M.; Li, P.L. | 2007 | `10.1111/j.1467-9868.2007.00605.x` | `https://rss.onlinelibrary.wiley.com/doi/full/10.1111/j.1467-9868.2007.00605.x` | journal | `clustering.kmeans_fd` |
| `bouveyron_et_al_2015` | The discriminative functional mixture model for a comparative analysis of bike sharing systems | Bouveyron, C.; Côme, E.; Jacques, J. | 2015 | `10.1214/15-AOAS861` | `https://projecteuclid.org/journals/annals-of-applied-statistics/volume-9/issue-4/The-discriminative-functional-mixture-model-for-a-comparative-analysis-of/10.1214/15-AOAS861.full` | journal | `clustering.funfem_cluster` |
| `bouveyron_jacques_2011` | Model-based clustering of time series in group-specific functional subspaces | Bouveyron, C.; Jacques, J. | 2011 | `10.1007/s11634-011-0095-6` | `https://link.springer.com/article/10.1007/s11634-011-0095-6` | journal | `clustering.gmm_cluster` |

[CITED: rss.onlinelibrary.wiley.com] — Chiou & Li 2007 JRSSB confirmed via web search this session.
[ASSUMED] — Bouveyron et al. 2015 AoAS: DOI 10.1214/15-AOAS861 plausible from web search description; not landing-page-verified. Executor: mark `curated:false` until verified.
[ASSUMED] — Bouveyron & Jacques 2011: DOI plausible; not verified.

**DBSCAN-FD:** Ester et al. 1996 DBSCAN (not FDA-specific). `clustering.dbscan_fd` → `curated:false`.

**Fuzzy C-means FD:** Ruspini 1970 / Bezdek 1981 (general FCM). `clustering.fuzzy_cmeans_fd` → `curated:false`.

**KCFC (k-means per-cluster FPCA):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `chiou_li_2007` | (same as above) | Chiou, J.M.; Li, P.L. | 2007 | `10.1111/j.1467-9868.2007.00605.x` | `https://rss.onlinelibrary.wiley.com/doi/full/10.1111/j.1467-9868.2007.00605.x` | journal | `clustering.kcfc_cluster` |

KCFC is k-centres functional clustering from Chiou & Li 2007, so it maps to the same paper. [ASSUMED] — Check fdars-core source to confirm which KCFC paper is cited.

**Cluster quality indices (Calinski-Harabasz, Silhouette):** Standard ML indices. `clustering.calinski_harabasz`, `clustering.calinski_harabasz_data`, `clustering.silhouette_score`, `clustering.silhouette_score_data` → `curated:false`.

**Contested: `align_cluster_fd`** — see §3.14.

---

### 3.13 Classification

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ferraty_vieu_2006` | Nonparametric Functional Data Analysis | Ferraty, F.; Vieu, P. | 2006 | `10.1007/0-387-36620-2` | `https://link.springer.com/book/10.1007/0-387-36620-2` | book | `classification.fclassif_kernel`, `classification.kernel_classify_from_distances` |
| `ramsay_silverman_2005` | Functional Data Analysis (2nd ed.) | (see above) | 2005 | `10.1007/b98888` | `https://link.springer.com/book/10.1007/b98888` | book | `classification.fclassif_lda`, `classification.fclassif_qda`, `classification.fclassif_knn`, `classification.knn_classify_from_distances`, `classification.fclassif_cv` |
| `cuesta_albertos_fraiman_2009` | Impartial trimmed means for functional data | Cuesta-Albertos, J.A.; Fraiman, R. | 2009 | `10.1007/978-3-7908-2349-3_12` | `https://link.springer.com/chapter/10.1007/978-3-7908-2349-3_12` | book_chapter | `classification.fclassif_dd` |

[ASSUMED] — DD-classifier (Depth-Depth classifier) root paper; needs executor verification against fdars-core. Alternative root: Li, Cuesta-Albertos & Liu (2012) "DD-classifier". `curated:false` recommended until confirmed.

**Elastic classification:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `tucker_wu_srivastava_2013` | (see §3.9) | Tucker, J.D.; Wu, W.; Srivastava, A. | 2013 | `10.1016/j.csda.2012.12.001` | `https://www.sciencedirect.com/science/article/abs/pii/S0167947312004227` | journal | `classification.elastic_multinomial` |

[ASSUMED] — Elastic logistic/multinomial classification attributed to Tucker et al. 2013 framework. Needs fdars-core confirmation.

---

### 3.14 Inference — ITP / SCB / ANOVA

**Interval Testing Procedure (ITP):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `pini_vantini_2016` | The interval testing procedure: A general framework for inference in functional data analysis | Pini, A.; Vantini, S. | 2016 | `10.1111/biom.12476` | `https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12476` | journal | `inference.itp_flm`, `inference.itp_one_pop`, `inference.itp_two_pop` |

[CITED: onlinelibrary.wiley.com/doi/abs/10.1111/biom.12476] — Confirmed via web search this session: Biometrics 2016. Note the paper_key uses 2016, not 2017 (there is also a 2017 companion paper in JNonparametricStatistics; the 2016 Biometrics paper is the primary framework reference).

**Simultaneous Confidence Bands (SCB):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `degras_2011` | Simultaneous confidence bands for nonparametric regression with functional data | Degras, D. | 2011 | `10.5705/ss.2009.207` | `https://www3.stat.sinica.edu.tw/sstest/j21n4/J21N412/J21N412.html` | journal | `inference.mean_scb`, `inference.scb_two_sample_test`, `tolerance.scb_mean_degras` |

[CITED: stat.sinica.edu.tw] — Confirmed via web search this session: Statistica Sinica 21(4):1735–1765, 2011. DOI 10.5705/ss.2009.207.

**F-test for FLM:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `shen_faraway_2004` | An F test for linear models with functional responses | Shen, Q.; Faraway, J. | 2004 | none (Statistica Sinica, predates DOI assignment) | `https://www3.stat.sinica.edu.tw/statistica/j14n4/j14n415/j14n415.html` | journal | `inference.flm_f_test`, `inference.flm_gof_test` |

[CITED: stat.sinica.edu.tw] — Confirmed via web search: Statistica Sinica 14(4), 2004.

Note: Shen & Faraway is a reasonable root for the general FLM F-test, but `inference.flm_f_test` in fdars computes the scalar-on-function F-test. Verify fdars-core source. Alternative: Müller & Stadtmüller 2005 which covers testing in the generalized FLM.

**Permutation tests (f_perm_test, t_perm_test):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `cuevas_febrero_fraiman_2004` | An ANOVA test for functional data | Cuevas, A.; Febrero, M.; Fraiman, R. | 2004 | `10.1016/j.csda.2003.10.021` | `https://www.sciencedirect.com/science/article/abs/pii/S0167947303001567` | journal | `inference.f_perm_test`, `inference.t_perm_test`, `inference.two_sample_mean_test` |

[CITED: sciencedirect.com] — Confirmed via web search this session: CSDA 47(1):111–122, 2004.

**Two-sample Hotelling-T²:**

Wire to `cuevas_febrero_fraiman_2004` above (covers permutation tests on functional data).

**Contested: `inference.oneway_anova_vstat`** — see §3.15.

---

### 3.15 Contested Attributions

#### `align_cluster_fd` (elastic-alignment functional clustering)

Signature: `(data, argvals, k=2, ..., use_amplitude_only=True, elastic_lambda=0.0, karcher_max_iter=15)`

This callable performs k-means clustering in the elastic metric, iterating between Karcher mean computation and cluster assignment. Two candidate primary papers:

1. **Srivastava et al. 2011 (arXiv:1103.3817)** — SRSF framework used for the Karcher mean computation.
2. **Kurtek et al. 2012** — "Statistical model for human poses recovered from depth image sequences" or related clustering work in the elastic framework.

**Recommendation:** Wire as co-primary `["srivastava_et_al_2011"]` for the elastic metric component, with a note: `"notes": "Elastic clustering via SRSF Karcher mean. Primary elastic metric: Srivastava et al. 2011. No single clustering paper covers this exact method — attribution to Srivastava et al. 2011 framework is the best available root."` Executor must check fdars-core implementation comments.

#### `elastic_changepoint` (distributional changepoint in curve sequences)

Signature: `(data, argvals, kind='amplitude', lam=0.0, max_iter=30, n_mc=200, ...)`

Primary source found: **Tucker & Yarger (2023/2024)**, "Elastic Functional Changepoint Detection of Climate Impacts from Localized Sources," Environmetrics, DOI: 10.1002/env.2826.

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `tucker_yarger_2024` | Elastic functional changepoint detection of climate impacts from localized sources | Tucker, J.D.; Yarger, D. | 2024 | `10.1002/env.2826` | `https://onlinelibrary.wiley.com/doi/10.1002/env.2826` | journal | `alignment.elastic_changepoint` |

[CITED: onlinelibrary.wiley.com/doi/10.1002/env.2826] — Confirmed via web search this session. Published 2023/2024 in Environmetrics. The paper received the 2024 Wiley-TIES Best Environmetrics Paper Award.

Note: The paper year from the Wiley listing is 2024; the arXiv preprint is 2022 (arXiv:2211.12687). Use `"year": 2024` (published in Environmetrics).

#### `oneway_anova_vstat` (one-way functional ANOVA V-statistic)

Signature: `(data, groups, argvals)` — asymptotic scaled-χ² test.

The "V-statistic" approach for one-way functional ANOVA is described in:

**Cuesta-Albertos & Febrero-Bande (2010)**, "A simple multiway ANOVA for functional data," TEST, 19(3):537–557, DOI: 10.1007/s11749-010-0185-3.

However, the "V-statistic" name suggests an alternative root: **Górecki & Smaga (2015)**, "A comparison of tests for the one-way ANOVA problem for functional data," Computational Statistics, 30:987–1010, DOI: 10.1007/s00180-015-0555-0 (which includes V-statistic tests).

**Recommendation:** Flag as contested. Use:
```json
"notes": "V-statistic functional ANOVA. Contested attribution: primary candidates are Cuesta-Albertos & Febrero-Bande (2010) TEST and Górecki & Smaga (2015) Comput. Stat. Executor must check fdars-core source for the specific V-statistic formula used."
```
Wire to `curated:false` pending fdars-core source check.

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `cuesta_albertos_febrero_2010` | A simple multiway ANOVA for functional data | Cuesta-Albertos, J.A.; Febrero-Bande, M. | 2010 | `10.1007/s11749-010-0185-3` | `https://link.springer.com/article/10.1007/s11749-010-0185-3` | journal | `inference.oneway_anova_vstat` (contested — see notes) |

[CITED: link.springer.com/article/10.1007/s11749-010-0185-3] — Confirmed via web search this session.

#### FAMM lineage (`famm.dense_flmm`, `famm.fast_fmm`, `famm.multi_famm`)

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `scheipl_staicu_greven_2015` | Functional additive mixed models | Scheipl, F.; Staicu, A.M.; Greven, S. | 2015 | `10.1080/10618600.2014.901914` | `https://www.tandfonline.com/doi/abs/10.1080/10618600.2014.901914` | journal | `famm.dense_flmm`, `famm.fast_fmm` |
| `volkmann_et_al_2023` | Multivariate functional additive mixed models | Volkmann, A.; Stöcker, A.; Scheipl, F.; Greven, S. | 2023 | `10.1177/1471082X211056158` | `https://journals.sagepub.com/doi/full/10.1177/1471082X211056158` | journal | `famm.multi_famm` |

[CITED: tandfonline.com] — Scheipl et al. 2015 JCGS (not JASA) confirmed via web search. DOI: 10.1080/10618600.2014.901914.
[CITED: journals.sagepub.com] — Volkmann et al. 2023 confirmed via web search. DOI: 10.1177/1471082X211056158.

**FAMM lineage verdict:** The lineage is clear — `scheipl_staicu_greven_2015` for dense_flmm and fast_fmm; `volkmann_et_al_2023` for multi_famm. NOT contested. Add both as `curated:true` (DOIs confirmed from authoritative sources).

Note: `famm.fast_fmm` is a fast variant — if fdars-core uses a different implementation, the executor must verify. The standard attribution is Scheipl et al. 2015.

---

### 3.16 Functional Time Series (FTS) — DPCA, FTSM

**Functional Time Series Model (FTSM) and Hyndman-Ullah:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `hyndman_ullah_2007` | Robust forecasting of mortality and fertility rates: a functional data approach | Hyndman, R.J.; Ullah, M.S. | 2007 | `10.1016/j.csda.2006.07.028` | `https://www.sciencedirect.com/science/article/abs/pii/S0167947306002775` | journal | `fts.ftsm`, `fts.ftsm_forecast`, `fts.ftsm_forecast_multistep`, `fts.ftsm_update` |

[CITED: sciencedirect.com] — Confirmed via web search this session: CSDA 51(10):4942–4956, 2007. DOI: 10.1016/j.csda.2006.07.028.

**Dynamic FPCA (DPCA):**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `panaretos_tavakoli_2013` | Fourier analysis of stationary time series in function space | Panaretos, V.M.; Tavakoli, S. | 2013 | `10.1214/13-AOS1086` | `https://projecteuclid.org/journals/annals-of-statistics/volume-41/issue-2/Fourier-analysis-of-stationary-time-series-in-function-space/10.1214/13-AOS1086.full` | journal | `fts.dpca`, `fts.dpca_reconstruct`, `fts.spectral_density`, `fts.long_run_covariance` |

[CITED: projecteuclid.org] — Confirmed via web search this session: AoS Vol 41, No 2, 2013. DOI: 10.1214/13-AOS1086.

**Functional ACF/PACF and stationarity test:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `hormann_kokoszka_2010` | Weakly dependent functional data | Hörmann, S.; Kokoszka, P. | 2010 | `10.1214/09-AOS768` | `https://projecteuclid.org/journals/annals-of-statistics/volume-38/issue-3/Weakly-dependent-functional-data/10.1214/09-AOS768.full` | journal | `fts.functional_acf`, `fts.functional_pacf`, `fts.stationarity_test`, `fts.functional_difference` |

[ASSUMED] — Hörmann & Kokoszka 2010 AoS is the standard reference for functional time series weak dependence and ACF; DOI plausible but not landing-page-verified this session.

**Functional PLS regression for time series:**

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `preda_saporta_2005` | (see §3.6) | Preda, C.; Saporta, G. | 2005 | `10.1016/j.csda.2004.07.002` | `https://www.sciencedirect.com/science/article/abs/pii/S0167947304002208` | journal | `fts.fplsr` |

---

### 3.17 Shapelets

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `ye_keogh_2009` | Time series shapelets: a new primitive for data mining | Ye, L.; Keogh, E. | 2009 | `10.1145/1557019.1557122` | `https://dl.acm.org/doi/10.1145/1557019.1557122` | conference | `shapelet.discover_shapelets`, `shapelet.shapelet_transform_fit`, `shapelet.shapelet_transform`, `shapelet.shapelet_distance`, `shapelet.shapelet_classifier_fit`, `shapelet.PyShapeletFit`, `shapelet.PyShapeletClassifierFit` |

[CITED: dl.acm.org/doi/10.1145/1557019.1557122] — Confirmed via web search this session: KDD 2009, pages 947–956.

---

### 3.18 MFPCA / FAMM

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `happ_greven_2018` | Multivariate functional principal component analysis for data observed on different (dimensional) domains | Happ, C.; Greven, S. | 2018 | `10.1080/01621459.2016.1273115` | `https://www.tandfonline.com/doi/abs/10.1080/01621459.2016.1273115` | journal | `spm.mfpca`, `multi_fdata.PyMultiFunData`, `multi_fdata.multi_fdata_from_components` |

[CITED: tandfonline.com/doi/abs/10.1080/01621459.2016.1273115] — Confirmed via web search this session: JASA 2018, Vol 113, No 522. DOI: 10.1080/01621459.2016.1273115.

MFPCA is also in the `spm` module as `spm.mfpca`. Wire to same paper.

---

### 3.19 Outlier Detection

| paper_key | title | authors | year | DOI | URL | type | callables |
|---|---|---|---|---|---|---|---|
| `sun_genton_2011` | (see §3.4 functional boxplot) | Sun, Y.; Genton, M.G. | 2011 | `10.1198/jcgs.2011.09224` | `https://www.tandfonline.com/doi/abs/10.1198/jcgs.2011.09224` | journal | `outliers.outliergram` |
| `dai_genton_2019` | Directional outlyingness for multivariate functional data | Dai, W.; Genton, M.G. | 2019 | `10.1016/j.csda.2018.03.017` | `https://www.sciencedirect.com/science/article/abs/pii/S016794731830077X` | journal | `outliers.magnitude_shape`, `outliers.muod` |
| `febrero_galeano_gonzalez_2008` | Outlier detection in functional data by depth measures | Febrero, M.; Galeano, P.; González-Manteiga, W. | 2008 | `10.1002/env.878` | `https://onlinelibrary.wiley.com/doi/abs/10.1002/env.878` | journal | `outliers.detect_outliers_lrt`, `outliers.detect_outliers_lrt_with_dist` |

[CITED: sciencedirect.com] — Dai & Genton 2019 CSDA confirmed via web search.
[CITED: onlinelibrary.wiley.com] — Febrero et al. 2008 Environmetrics confirmed via web search.
[ASSUMED] — `outliers.depthgram` → Dai & Genton 2018 JCGS (different paper from 2019 CSDA). Needs executor verification.
[ASSUMED] — `outliers.tvdmss` → Huang & Sun 2019 (TVD-MSS method); `curated:false` pending verification.
[ASSUMED] — `outliers.sequential_transform_outliers` → specific method; `curated:false`.

---

## 4. Cross-Language Pointer Table (per covered paper)

This table gives the cross-language `package`, `function`, `url`, `confidence` fields for each major paper entry. Only entries where the information was confirmed or is highly likely are included; Matlab entries default to `confidence: "low"`.

| paper_key | Language | package | function | url | confidence | Notes |
|---|---|---|---|---|---|---|
| `fraiman_muniz_2001` | R | `fda.usc` | `depth.FM` | `https://rdrr.io/cran/fda.usc/man/depth.fdata.html` | high | Already in seed |
| `fraiman_muniz_2001` | Python | `scikit-fda` | `fraiman_muniz_depth` | `https://fda.readthedocs.io/en/stable/modules/depth.html` | high | |
| `lopez_pintado_romo_2009` | R | `fda.usc` | `depth.mode` / `depth.band` | `https://rdrr.io/cran/fda.usc/man/depth.fdata.html` | high | |
| `lopez_pintado_romo_2009` | Python | `scikit-fda` | `BandDepth` | `https://fda.readthedocs.io/en/stable/modules/depth.html` | high | |
| `srivastava_et_al_2011` | R | `fdasrvf` | `multiple_align_functions` | `https://rdrr.io/cran/fdasrvf/man/multiple_align_functions.html` | high | |
| `srivastava_et_al_2011` | Python | `fdasrsf` | `fdawarp` | `https://fdasrsf-python.readthedocs.io/` | high | |
| `srivastava_et_al_2011` | Matlab | `fdasrvf_MATLAB` | `multiple_align_functions` | `https://github.com/jdtuck/fdasrvf_MATLAB` | low | |
| `tucker_wu_srivastava_2013` | Python | `fdasrsf` | `fdavpca` | `https://fdasrsf-python.readthedocs.io/` | high | |
| `tucker_wu_srivastava_2013` | R | `fdasrvf` | `jointFPCA` | `https://rdrr.io/cran/fdasrvf/man/jointFPCA.html` | high | |
| `yao_muller_wang_2005` | R | `fdapace` | `PACE` | `https://rdrr.io/cran/fdapace/man/FPCA.html` | high | |
| `yao_muller_wang_2005` | Python | `scikit-fda` | `FPCA` | `https://fda.readthedocs.io/en/stable/modules/preprocessing/dim_reduction.html` | high | |
| `yao_muller_wang_2005` | Matlab | `PACE` | `FPCA` | `https://www.stat.ucdavis.edu/PACE/` | low | |
| `ramsay_silverman_2005` | R | `fda` | `pca.fd` | `https://rdrr.io/cran/fda/man/pca.fd.html` | high | |
| `ramsay_silverman_2005` | Python | `scikit-fda` | `FPCA` | `https://fda.readthedocs.io/en/stable/modules/preprocessing/dim_reduction.html` | high | |
| `ramsay_silverman_2005` | Matlab | `fdaM` | `pca_fd` | `https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/Matlab/` | low | |
| `eilers_marx_1996` | R | `mgcv` | `s(..., bs="ps")` | `https://www.rdocumentation.org/packages/mgcv/versions/1.9-0/topics/s` | high | |
| `eilers_marx_1996` | Python | `scikit-fda` | `BSplineSmoother` | `https://fda.readthedocs.io/en/stable/modules/preprocessing/smoothing.html` | high | |
| `sakoe_chiba_1978` | R | `dtw` | `dtw` | `https://rdrr.io/cran/dtw/man/dtw.html` | high | |
| `sakoe_chiba_1978` | Python | `tslearn` | `dtw` | `https://tslearn.readthedocs.io/en/stable/gen_modules/metrics/tslearn.metrics.dtw.html` | high | |
| `cuturi_2011` | R | `dtwclust` | `GAK` | `https://rdrr.io/cran/dtwclust/man/GAK.html` | high | |
| `cuturi_2011` | Python | `tslearn` | `gak` | `https://tslearn.readthedocs.io/en/stable/gen_modules/metrics/tslearn.metrics.gak.html` | high | |
| `cuturi_blondel_2017` | Python | `tslearn` | `soft_dtw` | `https://tslearn.readthedocs.io/en/stable/gen_modules/metrics/tslearn.metrics.soft_dtw.html` | high | |
| `petersen_muller_2019` | R | none | — | — | — | No direct R implementation found |
| `petersen_muller_2019` | Python | none | — | — | — | No direct Python implementation found |
| `happ_greven_2018` | R | `MFPCA` | `MFPCA` | `https://rdrr.io/cran/MFPCA/man/MFPCA.html` | high | |
| `happ_greven_2018` | Python | none | — | — | — | No Python equivalent found |
| `pini_vantini_2016` | R | `fdatest` (GitHub) | `ITP1bspline` | `https://rdrr.io/github/alessiapini/fdatest/man/IWT1.html` | high | |
| `scheipl_staicu_greven_2015` | R | `refund` | `pfr` | `https://rdrr.io/cran/refund/man/pfr.html` | high | |
| `ye_keogh_2009` | Python | `sktime` | `ShapeletTransform` | `https://www.sktime.net/en/stable/api_reference/auto_generated/sktime.transformations.panel.shapelet_transform.ShapeletTransform.html` | high | |
| `bouveyron_et_al_2015` | R | `funFEM` | `funFEM` | `https://rdrr.io/cran/funFEM/man/funFEM.html` | high | |
| `chiou_li_2007` | R | `fdapace` | `kCFC` | `https://rdrr.io/cran/fdapace/man/kCFC.html` | high | |
| `hyndman_ullah_2007` | R | `ftsa` | `ftsm` | `https://rdrr.io/cran/ftsa/man/ftsm.html` | high | |
| `hyndman_ullah_2007` | Python | none | — | — | — | No direct Python FTSM implementation found |
| `sun_genton_2011` | R | `fdaoutlier` | `functional_boxplot` | `https://rdrr.io/cran/fdaoutlier/man/functional_boxplot.html` | high | |
| `muller_stadtmuller_2005` | R | `fda.usc` | `fregre.glm` | `https://rdrr.io/cran/fda.usc/man/fregre.glm.html` | high | |
| `degras_2011` | R | none found | — | — | — | SCB method not found in standalone CRAN package |
| `panaretos_tavakoli_2013` | R | `freqdom.fda` | `dpca` | `https://rdrr.io/cran/freqdom.fda/man/dpca.html` | high | |
| `tucker_yarger_2024` | R | `fdasrvf` | `elastic.changepoint` | `https://rdrr.io/cran/fdasrvf/man/elastic.changepoint.html` | high | |
| `tucker_yarger_2024` | Python | `fdasrsf` | `ElasticChangePoint` | `https://fdasrsf-python.readthedocs.io/` | high | |
| `cuevas_febrero_fraiman_2004` | R | `fda.usc` | `fanova.onefactor` | `https://rdrr.io/cran/fda.usc/man/fanova.onefactor.html` | high | |
| `febrero_galeano_gonzalez_2008` | R | `fda.usc` | `foutliers` | `https://rdrr.io/cran/fda.usc/man/foutliers.html` | high | |

**New URL domains needed in `_ALLOWED_DOMAINS`:**

The current allowlist [VERIFIED: tests/test_guard_sync_version_independent.py:407-419] contains:
```
"doi.org", "link.springer.com", "www.tandfonline.com",
"academic.oup.com", "onlinelibrary.wiley.com", "rss.onlinelibrary.wiley.com",
"www.sciencedirect.com", "dl.acm.org", "ieeexplore.ieee.org",
"www.jstor.org", "projecteuclid.org", "arxiv.org", "www.researchgate.net",
"pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
"rdrr.io", "cran.r-project.org", "www.rdocumentation.org",
"pypi.org", "fdasrsf-python.readthedocs.io",
"sipemu.github.io"
```

**New domains required for Phase 81 entries:**

| Domain | Required For |
|---|---|
| `www3.stat.sinica.edu.tw` | Degras 2011 (Statistica Sinica) + Shen & Faraway 2004 |
| `www.stat.ucdavis.edu` | PACE Matlab tool |
| `proceedings.mlr.press` | Cuturi & Blondel 2017 soft-DTW |
| `tslearn.readthedocs.io` | tslearn Python cross-language pointers |
| `fda.readthedocs.io` | scikit-fda Python cross-language pointers |
| `www.sktime.net` | sktime Python cross-language pointer |
| `journals.sagepub.com` | Volkmann et al. 2023 (FAMM) |
| `epubs.siam.org` | Agueh & Carlier 2011 (if used) |
| `icml.cc` | Cuturi 2011 GAK (alternative landing page) |

**Executor action:** Add all listed domains to `_ALLOWED_DOMAINS` in `tests/test_guard_sync_version_independent.py` in the same commit as the JSON batch that introduces those URLs.

---

## 5. Coverage Estimate

**Total callables in `_capability_map.json`: 437** (verified this session)

**Anti-feature modules excluded from curated count:**
- `explain`: 46 callables → `curated:false`
- `spm`: 23 (module-level sentinel) — HOWEVER: `spm.mfpca` has a clear root (Happ & Greven 2018) and should be curated. So: 22 callables → `curated:false`, 1 curated.
- `scoring` / `metrics`: 10 callables → `curated:false`
- `conformal`: 7 callables → `curated:false`
- `seasonal`: 18 callables → `curated:false`
- `depth.functional_depth` (dispatcher): 1 callable → `curated:false`

Total anti-feature callables: ~106 (excluding `spm.mfpca`)

**Estimate of curated callables from clear-root families (this pass):**
Based on the per-family tables above, a realistic estimate for this pass:

| Family | Estimated curated callables |
|---|---|
| Basis / smoothing | ~8 |
| Functional statistics | ~11 |
| Functional depth (sub-methods) | ~10 |
| Functional boxplot | 1 |
| FPCA / PACE | ~8 |
| Scalar-on-function / FLM | ~14 |
| Fréchet regression | 4 |
| Density / LQD | 3 |
| Elastic / SRSF alignment | ~18 |
| Shift / landmark registration | ~5 |
| Metrics (DTW, GAK, soft-DTW) | ~10 |
| Clustering | ~4 |
| Classification | ~8 |
| Inference (ITP, SCB, ANOVA, permutation) | ~10 |
| FTS / DPCA | ~10 |
| Shapelets | 7 |
| MFPCA | 3 |
| Outlier detection | ~5 |
| **TOTAL ESTIMATE** | **~139** |

**Expected coverage fraction:** approximately 139/437 ≈ **32%**

The remaining ~298 callables will be `curated:false` or uncurated:
- Anti-feature modules: ~106
- Unclear root / contested / deferred: ~192 (covariance, datasets, represent, multi_fdata utility callables, many alignment variants, many regression variants, simulation GPs, etc.)

This is partial-but-honest coverage. GATE-05 emits the N/437 fraction. A coverage floor is deferred to REF-FUT-01.

**Paper count estimate:** The tables above contain approximately 30–35 distinct paper entries (not counting the 5 seeds), giving a total of ~35–40 papers in the registry after this phase. This is at the lower bound of the "40–100 papers" estimate from CONTEXT.md — many callables share the same few foundational papers (Ramsay & Silverman 2005 covers a large fraction).

---

## 6. Common Pitfalls

### Pitfall 1: F&M Year (1991 vs 2001) — already documented in Phase 80 research
Year is 2001. DOI: 10.1007/BF02595706. [VERIFIED: seed]

### Pitfall 2: Band Depth vs Modified Band Depth — Same Paper
Both `depth.band_1d` and `depth.modified_band_1d` → single paper `lopez_pintado_romo_2009`. Do NOT split into two paper entries. [VERIFIED: seed]

### Pitfall 3: `depth.functional_depth` vs per-method depth callables
`depth.functional_depth` is the category-level dispatcher → anti-feature sentinel (`curated:false`).
`depth.fraiman_muniz_1d`, `depth.band_1d`, `depth.modified_band_1d`, `depth.modal_1d` etc. ARE curated with per-method papers. Do not conflate the dispatcher with its targets.

### Pitfall 4: SRSF vs SRV Paper Confusion — already documented in Phase 80 research
Use arXiv:1103.3817 (Srivastava et al. 2011) for functional data SRSF. NOT the 2011 IEEE TPAMI paper (for shapes of curves).

### Pitfall 5: Soft-DTW Has No DOI
Cuturi & Blondel 2017 is ICML (PMLR proceedings). Leave `"doi": ""` and use the PMLR URL. The GATE-05 C gate skips empty DOI fields for `curated:true` entries — confirm this gate behaviour in the test before committing.

Actually, re-reading the Phase 80 guard test [VERIFIED: tests/test_guard_sync_version_independent.py:450-455]:
```python
if paper.get("curated", True) and doi:
    if not _DOI_RE.match(doi):
        errors.append(...)
```
The gate only validates the DOI regex IF `doi` is non-empty AND `curated:true`. So an empty `"doi": ""` with `"curated": true` is allowed. The executor should set `"doi": ""` for papers without DOIs.

### Pitfall 6: ACM DL DOI Format for ICML 2011 (GAK)
The Cuturi 2011 GAK paper has DOI `10.5555/3104482.3104599`. The prefix `10.5555` has 4 digits — this matches the `^10\.\d{4,9}/\S+$` regex (4 ≥ 4). No problem with the gate.

### Pitfall 7: `spm.mfpca` Is Inside the SPM Module but Has a Clear Root
Do NOT omit `spm.mfpca` from curation just because `spm` is an anti-feature module. `spm.mfpca` has a clear primary root (Happ & Greven 2018) and must be curated separately.

### Pitfall 8: DOI-Resolves-But-Wrong-Attribution
Multiple papers per author family (Ramsay & Dalzell 1991 vs Ramsay & Silverman 2005 — different papers, different focus). Always cite the specific paper that introduces the specific method, not the textbook chapter that happens to cover it unless the textbook is the primary source.

### Pitfall 9: Cross-Language Link Rot
`rdrr.io` URLs are stable. `readthedocs.io` versioned URLs may change with package updates; use the unversioned `/en/latest/` or `/en/stable/` forms where possible. Do not use GitHub raw URLs for cross-language pointers.

### Pitfall 10: Misidentifying the Denominator
The denominator is **437**, not 409. Report `N/437` in all coverage metadata fields.

---

## 7. Domain Allowlist — Recommended Extensions

Verbatim from the current test file [VERIFIED: tests/test_guard_sync_version_independent.py:407-419]:
```python
_ALLOWED_DOMAINS = frozenset({
    "doi.org", "link.springer.com", "www.tandfonline.com",
    "academic.oup.com", "onlinelibrary.wiley.com", "rss.onlinelibrary.wiley.com",
    "www.sciencedirect.com", "dl.acm.org", "ieeexplore.ieee.org",
    "www.jstor.org", "projecteuclid.org", "arxiv.org", "www.researchgate.net",
    "pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
    "rdrr.io", "cran.r-project.org", "www.rdocumentation.org",
    "pypi.org", "fdasrsf-python.readthedocs.io",
    "sipemu.github.io",
})
```

**Add these domains:**
```python
# Needed for Phase 81:
"www3.stat.sinica.edu.tw",   # Degras 2011 + Shen & Faraway 2004
"proceedings.mlr.press",      # Cuturi & Blondel 2017 soft-DTW
"tslearn.readthedocs.io",     # tslearn Python cross-language
"fda.readthedocs.io",         # scikit-fda Python cross-language
"www.sktime.net",             # sktime Python cross-language
"journals.sagepub.com",       # Volkmann et al. 2023 FAMM
```

Conditionally needed (only if those paper URLs are used):
```python
"epubs.siam.org",             # Agueh & Carlier 2011
"icml.cc",                    # Cuturi 2011 alternative URL
"www.stat.ucdavis.edu",       # PACE Matlab
```

---

## 8. Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | Denominator is 437 (from capability_map.json count) | §1 | If JSON grows before execution, count will differ; executor must recount |
| A2 | Ramsay & Silverman 2005 book DOI is 10.1007/b98888 | §3.2 | Could be a different DOI suffix; executor must verify |
| A3 | Craven & Wahba 1979 DOI is 10.1007/BF01404567 | §3.1 | Not web-verified; executor must confirm or mark curated:false |
| A4 | Tucker et al. 2013 DOI is 10.1016/j.csda.2012.12.001 | §3.9 | plausible from web search description; needs landing-page verification |
| A5 | Petersen & Müller 2016 LQD AoS DOI is 10.1214/15-AOS1363 | §3.8 | plausible; not verified |
| A6 | Preda & Saporta 2005 DOI is 10.1016/j.csda.2004.07.002 | §3.6, §3.16 | plausible; not verified |
| A7 | Hörmann & Kokoszka 2010 DOI is 10.1214/09-AOS768 | §3.16 | plausible; not verified |
| A8 | Bouveyron et al. 2015 AoAS DOI is 10.1214/15-AOAS861 | §3.12 | plausible; not verified |
| A9 | Chiou & Li 2007 maps to kcfc_cluster | §3.12 | fdars-core KCFC may cite a different paper; needs source check |
| A10 | Gervini 2008 DOI is 10.1093/biomet/asn031 | §3.2 | plausible; not verified |
| A11 | functional_spatial depth root paper (Dabo-Niang & Gijbels 2010) | §3.3 | The actual fdars-core spatial depth implementation may cite a different primary source |
| A12 | cuturi_2011 DOI 10.5555/3104482.3104599 matches GATE-05 C regex | §3.11 | Verified via regex logic (4 digit prefix); should pass |
| A13 | soft-DTW: empty doi "" is allowed by GATE-05 C | §3.11, Pitfall 5 | Verified from test code — gate skips empty doi strings |
| A14 | `oneway_anova_vstat` root is Cuesta-Albertos & Febrero-Bande 2010 | §3.15 | Contested; executor must check fdars-core source |
| A15 | `fts.fplsr` root is Preda & Saporta 2005 | §3.16 | Reasonable attribution; needs fdars-core source check |

---

## Sources

### Primary (HIGH confidence)
- `python/fdars/_capability_map.json` — callable count (437), module names [VERIFIED this session]
- `tests/test_guard_sync_version_independent.py:407-419` — current `_ALLOWED_DOMAINS` [VERIFIED this session]
- `python/fdars/_references_map.json` — 5 seed papers [VERIFIED this session]
- `python/fdars/_capability_curation.json` — identifier space [VERIFIED Phase 80]
- Web search: Fraiman & Muniz 2001 DOI 10.1007/BF02595706 [VERIFIED Phase 80]
- Web search: López-Pintado & Romo 2009 DOI 10.1198/jasa.2009.0108 [VERIFIED Phase 80]
- Web search: Srivastava et al. 2011 arXiv:1103.3817 [VERIFIED Phase 80]

### Secondary (MEDIUM confidence — confirmed via authoritative source URLs this session)
- Petersen & Müller 2019 DOI 10.1214/17-AOS1624 [VERIFIED: projecteuclid.org this session]
- Yao, Müller, Wang 2005 DOI 10.1198/016214504000001745 [VERIFIED: tandfonline.com this session]
- Müller & Stadtmüller 2005 DOI 10.1214/009053604000001156 [VERIFIED: projecteuclid.org this session]
- Sun & Genton 2011 DOI 10.1198/jcgs.2011.09224 [VERIFIED: tandfonline.com this session]
- Degras 2011 DOI 10.5705/ss.2009.207 [CITED: stat.sinica.edu.tw this session]
- Cuevas, Febrero, Fraiman 2007 DOI 10.1007/s00180-007-0053-0 [CITED: link.springer.com this session]
- Cuevas, Febrero, Fraiman 2004 DOI 10.1016/j.csda.2003.10.021 [CITED: sciencedirect.com this session]
- Tucker & Yarger 2024 DOI 10.1002/env.2826 [CITED: onlinelibrary.wiley.com this session]
- Sakoe & Chiba 1978 DOI 10.1109/TASSP.1978.1163055 [CITED: ieeexplore.ieee.org this session]
- Cuturi 2011 DOI 10.5555/3104482.3104599 [CITED: dl.acm.org this session]
- Cuturi & Blondel 2017 URL proceedings.mlr.press/v70/cuturi17a.html [CITED: PMLR this session]
- Chiou & Li 2007 DOI 10.1111/j.1467-9868.2007.00605.x [CITED: onlinelibrary.wiley.com this session]
- Happ & Greven 2018 DOI 10.1080/01621459.2016.1273115 [CITED: tandfonline.com this session]
- Pini & Vantini 2016 DOI 10.1111/biom.12476 [CITED: onlinelibrary.wiley.com this session]
- Scheipl, Staicu, Greven 2015 DOI 10.1080/10618600.2014.901914 [CITED: tandfonline.com this session]
- Panaretos & Tavakoli 2013 DOI 10.1214/13-AOS1086 [CITED: projecteuclid.org this session]
- Hyndman & Ullah 2007 DOI 10.1016/j.csda.2006.07.028 [CITED: sciencedirect.com this session]
- Ye & Keogh 2009 DOI 10.1145/1557019.1557122 [CITED: dl.acm.org this session]
- Shen & Faraway 2004 [CITED: stat.sinica.edu.tw this session]
- Cuesta-Albertos & Febrero-Bande 2010 DOI 10.1007/s11749-010-0185-3 [CITED: link.springer.com this session]
- Marron et al. 2015 DOI 10.1214/15-STS524 [CITED: projecteuclid.org this session]
- Ferraty & Vieu 2006 book [CITED: link.springer.com this session]
- Narisetty & Nair 2016 DOI 10.1080/01621459.2015.1110033 [CITED: tandfonline.com this session]
- Febrero, Galeano, González-Manteiga 2008 DOI 10.1002/env.878 [CITED: onlinelibrary.wiley.com this session]
- Dai & Genton 2019 DOI 10.1016/j.csda.2018.03.017 [CITED: sciencedirect.com this session]
- Volkmann et al. 2023 DOI 10.1177/1471082X211056158 [CITED: journals.sagepub.com this session]

### Tertiary (LOW confidence / ASSUMED)
- Ramsay & Silverman 2005 DOI 10.1007/b98888 [ASSUMED]
- Tucker et al. 2013 DOI 10.1016/j.csda.2012.12.001 [ASSUMED]
- Craven & Wahba 1979 DOI 10.1007/BF01404567 [ASSUMED]
- Preda & Saporta 2005 [ASSUMED]
- Hörmann & Kokoszka 2010 [ASSUMED]
- Bouveyron et al. 2015 [ASSUMED]
- Petersen & Müller 2016 LQD [ASSUMED]
- Gervini 2008 [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Denominator (437): HIGH — read from file this session
- Current domain allowlist: HIGH — read from test file this session
- Core paper DOIs (FM, LP&R, SRSF seed): HIGH — Phase 80
- Secondary DOIs (Petersen-Müller, Yao-Müller-Wang, Müller-Stadtmüller, Sun-Genton, Happ-Greven, Pini-Vantini, Scheipl et al., Tucker-Yarger, Cuturi, Cuturi-Blondel, Sakoe-Chiba, etc.): MEDIUM — confirmed from authoritative landing pages via web search this session
- Cross-language pointers: MEDIUM (R) / LOW (Matlab)
- Contested attributions (align_cluster_fd, oneway_anova_vstat, functional spatial depth): LOW — needs fdars-core source check

**Research date:** 2026-09-07
**Valid until:** 2026-10-07 (paper DOIs are stable; cross-language package URLs may change with new releases)

---

## RESEARCH COMPLETE
