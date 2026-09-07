# Feature Research

**Domain:** Functional data analysis — scientific provenance and cross-language implementation landscape
**Researched:** 2026-09-07
**Confidence:** MEDIUM (web search cross-checked for canonical papers; DOIs spot-verified against publisher URLs)

---

## Purpose of This Document

This is the authoring backbone for v13.0 Scientific Provenance & Cross-Language Implementations.
It maps every `fdars` submodule family to:
- its foundational paper(s) — author, year, journal, DOI or stable URL
- alternative implementations in R, Python, and Matlab — package + representative function + stable URL
- honest notes on ambiguity, contested attributions, and genuine gaps

The curation unit is **paper-level** (many callables share one root paper). Callable-to-paper indexing happens in the references JSON; this document supplies the raw material for that index.

---

## Part A — Foundational Papers per Method Family

### A1. Functional Data Representation & Basis Expansion
**fdars modules:** `basis`, `_Fdata`, `represent`, `smoothing` (partially)

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |
| *Functional Data Analysis with R and Matlab* | Ramsay, J.O., Hooker, G. & Graves, S. | 2009 | Springer (book) | https://doi.org/10.1007/978-0-387-98185-7 |
| "Spline estimators for the functional linear model" | Cardot, H., Ferraty, F. & Sarda, P. | 2003 | Statistica Sinica 13: 571-591 | https://www3.stat.sinica.edu.tw/statistica/oldpdf/A13n31.pdf |

**Callables covered:** `bspline_basis`, `bspline_basis_from_knots`, `fourier_basis`, `fourier_basis_with_period`, `constant_basis`, `pspline_fit_1d`, `pspline_fit_gcv`, `smooth_basis_gcv`, `smooth_basis_aic`, `fdata_to_basis_1d`, `basis_to_fdata_1d`, `basis_nbasis_cv`, `select_basis_auto_1d`, `_Fdata.to_basis`, `_Fdata.from_basis`

**Notes:** Ramsay & Silverman (2005) is the unambiguous single root for B-spline and Fourier basis FDA. P-spline smoothing has a separate root: Eilers & Marx (1996) "Flexible smoothing with B-splines and penalties" *Statist. Sci.* 11(2): 89-121 (DOI: 10.1214/ss/1038425655), cited alongside Ramsay & Silverman in the fdars smoothing context.

---

### A2. Functional Statistics & Descriptive Analysis
**fdars modules:** `fdata`, `_Fdata` (mean/var/std/cov/norm/center)

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |
| "Trimmed means for functional data" | Fraiman, R. & Muniz, G. | 2001 | *TEST* 10: 419-440 | https://link.springer.com/article/10.1007/BF02595706 |

**Callables covered:** `mean_1d`, `mean_2d`, `functional_variance`, `functional_std`, `functional_covariance`, `norm_lp_1d`, `center_1d`, `normalize`, `normalize_with_argvals`, `deriv_1d`, `deriv_2d`, `geometric_median_1d`, `geometric_median_2d`, `depth_based_median`, `trim_mean`, `_Fdata.mean`, `_Fdata.var`, `_Fdata.std`, `_Fdata.cov`, `_Fdata.center`, `_Fdata.norm`, `_Fdata.normalize`, `_Fdata.deriv`, `_Fdata.median`

**CORRECTION NOTE — Fraiman & Muniz date:** The paper is **2001**, not 1991. The "1991" date commonly cited in the FDA literature is a misattribution to a pre-print or working-paper circulated informally. The published journal paper in *TEST* is 2001. Curators should use 2001.

---

### A3. Kernel Smoothing & Bandwidth Selection
**fdars modules:** `smoothing`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |
| *Nonparametric Functional Statistics* | Ferraty, F. & Vieu, P. | 2006 | Springer (book) | https://doi.org/10.1007/0-387-36620-2 |

**Callables covered:** `nadaraya_watson`, `local_linear`, `local_polynomial`, `gcv_smoother`, `cv_smoother`, `optim_bandwidth`, `smoothing_matrix_nw`, `knn_smoother`, `knn_gcv`, `knn_lcv`

**Notes:** Nadaraya-Watson estimator has a classical scalar origin (Nadaraya 1964; Watson 1964) but the FDA framing — including bandwidth selection via GCV for functional data — is standardized in Ferraty & Vieu (2006). Ramsay & Silverman (2005) covers penalized spline smoothing.

---

### A4. Functional Depth
**fdars modules:** `depth`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "On the concept of depth for functional data" (band/modified-band depth) | Lopez-Pintado, S. & Romo, J. | 2009 | *JASA* 104(486): 718-734 | https://doi.org/10.1198/jasa.2009.0015 |
| "Trimmed means for functional data" (FM depth) | Fraiman, R. & Muniz, G. | 2001 | *TEST* 10: 419-440 | https://link.springer.com/article/10.1007/BF02595706 |
| "Mathematics and the picturing of data" (halfspace / Tukey depth) | Tukey, J.W. | 1975 | *Proc. Int. Congress Math.* Vol. 2: 523-531 | (no DOI; proceedings volume) |
| "A half-region depth for functional data" (HRD/MHRD) | Lopez-Pintado, S. & Romo, J. | 2011 | *CSDA* 55(4): 1679-1695 | https://doi.org/10.1016/j.csda.2010.10.029 |
| "A topologically valid definition of depth for functional data" | Nieto-Reyes, A. & Battey, H. | 2016 | *Statist. Sci.* 31(1): 61-79 | https://doi.org/10.1214/15-STS532 |

**Callables covered:** `fraiman_muniz_1d`, `fraiman_muniz_2d`, `band_1d`, `modified_band_1d`, `modified_epigraph_index_1d`, `modal_1d`, `modal_2d`, `random_projection_1d`, `random_projection_2d`, `random_projection_deriv_1d`, `random_tukey_1d`, `random_tukey_2d`, `functional_spatial_1d`, `functional_spatial_2d`, `kernel_functional_spatial_1d`, `kernel_functional_spatial_2d`, `functional_depth`, `functional_boxplot`

**ANTI-FEATURE NOTE:** This module cannot have a single root paper. The `functional_depth` dispatcher unifies at least 7 distinct methods, each with its own root paper. The references JSON needs method-keyed entries, not a module-level single citation. Modal depth traces specifically to Cuevas, Febrero & Fraiman (2007) "Robust estimation and classification for functional data via projection-based depth notions" *CSDA*; ERL/extremal depth to Narisetty & Nair (2016); epigraph/hypograph indices to Lopez-Pintado & Romo (2012).

---

### A5. Functional Boxplot & Outlier Visualization
**fdars modules:** `depth` (functional_boxplot), `outliers`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Functional boxplots" | Sun, Y. & Genton, M.G. | 2011 | *JCGS* 20(2): 316-334 | https://doi.org/10.1198/jcgs.2011.09224 |
| "Outlier detection in functional data by depth measures..." | Febrero-Bande, M., Galeano, P. & Gonzalez-Manteiga, W. | 2008 | *Environmetrics* 19(4): 331-345 | https://doi.org/10.1002/env.878 |
| "Multivariate functional data visualization and outlier detection" (MS-Plot) | Dai, W. & Genton, M.G. | 2018 | *JCGS* 27(4): 923-934 | https://doi.org/10.1080/10618600.2018.1473781 |
| "Directional outlyingness for multivariate functional data" | Dai, W. & Genton, M.G. | 2019 | *CSDA* 131: 50-65 | https://doi.org/10.1016/j.csda.2018.03.017 |

**Callables covered:** `functional_boxplot`, `magnitude_shape`, `outliergram`, `depthgram`, `muod`, `tvdmss`, `sequential_transform_outliers`, `detect_outliers_lrt`, `detect_outliers_lrt_with_dist`

**Notes:** `tvdmss` traces to Huang & Sun (2019); `depthgram` to Aleman-Gomez et al. (2022); `muod` (MUOD) to Ojo et al. (2021). Individual citations needed per callable in the references JSON.

---

### A6. Functional Principal Component Analysis (FPCA)
**fdars modules:** `regression` (fpca), `pace_fpca`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) — FPCA chapters | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |
| "Functional data analysis for sparse longitudinal data" (PACE) | Yao, F., Muller, H.-G. & Wang, J.-L. | 2005 | *JASA* 100(470): 577-590 | https://doi.org/10.1198/016214504000001745 |

**Callables covered:** `regression.fpca`, `pace_fpca.pace_fpca`, `pace_fpca.PyIrregFdata`, `pace_fpca.irreg_fdata_from_lists`, `_Fdata.to_pc`

**Notes:** Standard dense FPCA traces to Ramsay & Silverman (2005). PACE FPCA for sparse/irregular data is unambiguously Yao, Muller & Wang (2005). These are distinct methods requiring distinct reference entries.

---

### A7. Scalar-on-Function & Functional Linear Regression
**fdars modules:** `regression`, `scalar_on_function`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Functional linear model" | Cardot, H., Ferraty, F. & Sarda, P. | 1999 | *Statist. Probab. Lett.* 45: 11-22 | https://doi.org/10.1016/S0167-7152(99)00036-X |
| "Spline estimators for the functional linear model" | Cardot, H., Ferraty, F. & Sarda, P. | 2003 | *Statistica Sinica* 13: 571-591 | https://www3.stat.sinica.edu.tw/statistica/oldpdf/A13n31.pdf |
| *Functional Data Analysis* (2nd ed.) — regression chapters | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |
| "Functional additive models" (FAM/GKAM) | Muller, H.-G. & Yao, F. | 2008 | *JASA* 103(484): 1534-1544 | https://doi.org/10.1198/016214508000000516 |
| "An ANOVA test for functional data" (fanova) | Cuevas, A., Febrero, M. & Fraiman, R. | 2004 | *CSDA* 47(1): 111-122 | https://doi.org/10.1016/j.csda.2003.10.021 |

**Callables covered:** `fregre_lm`, `fregre_cv`, `fregre_pls`, `fpls`, `model_selection_ncomp`, `bootstrap_ci_fregre_lm`, `predict_fregre_lm`, `predict_fregre_pls`, `fregre_huber`, `fregre_l1`, `fregre_np`, `fregre_np_cv`, `fregre_np_mixed`, `functional_logistic`, `functional_glm`, `bootstrap_ci_functional_logistic`, `predict_functional_logistic`, `fosr`, `fosr_fpc`, `predict_fosr`, `concurrent_regression`, `fof_regression`, `fof_re_regression`, `fof_cv`, `predict_fof`, `predict_fof_re`, `fanova`, `scalar_on_function.fam`, `scalar_on_function.fregre_gkam`, `scalar_on_function.fregre_gsam`, `scalar_on_function.variable_selection`, `scalar_on_function.model_selection_ncomp`

**Notes:** This module spans ~7 different root papers. Concurrent/varying-coefficient regression (`concurrent_regression`) traces to Ramsay (1996) / Hastie & Tibshirani (1993), treated in FDA context by Ramsay & Silverman (2005). Function-on-function regression (`fof_regression`) traces to Yao et al. (2005) extensions and Ivanescu et al. (2015). Flag for curators: require per-callable citations for this module.

---

### A8. Frechet Regression & Non-Euclidean Response
**fdars modules:** `frechet`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Frechet regression for random objects with Euclidean predictors" | Petersen, A. & Muller, H.-G. | 2019 | *Ann. Statist.* 47(2): 691-719 | https://doi.org/10.1214/17-AOS1624 |

**Callables covered:** `frechet_mean`, `frechet_global_reg`, `frechet_local_reg`, `frechet_anova`

**Notes:** Petersen & Muller (2019) is the unambiguous single root for Frechet regression. Paper was published 2019 (appeared online 2018). The `frechet_mean` for SPD matrices also relates to Moakher (2005) "A differential geometric approach to the geometric mean of symmetric positive-definite matrices" *SIAM J. Matrix Anal. Appl.* 26(3): 735-747 for the Karcher mean formula, but the regression framing is fully the Petersen & Muller (2019) paper.

---

### A9. Density FDA — LQD Transform & Wasserstein
**fdars modules:** `density_fda`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Functional data analysis for density functions by transformation to a Hilbert space" (LQD) | Petersen, A. & Muller, H.-G. | 2016 | *Ann. Statist.* 44(1): 183-218 | https://doi.org/10.1214/15-AOS1363 |

**Callables covered:** `lqd_transform`, `inverse_lqd`, `lqd_fpca`, `wasserstein_barycenter`, `normalize_density`

**Notes:** LQD transform is unambiguously Petersen & Muller (2016). The `wasserstein_barycenter` is conceptually related to Agueh & Carlier (2011) "Barycenters in the Wasserstein space" *SIAM J. Math. Anal.* 43(2): 904-924 but the density-FDA framing is Petersen & Muller (2016/2019). Curators may want to note both.

---

### A10. Elastic / Fisher-Rao Registration & SRSF Framework
**fdars modules:** `alignment` (most elastic_* and karcher_* callables)

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Registration of functional data using Fisher-Rao metric" (SRSF framework) | Srivastava, A., Wu, W., Kurtek, S., Klassen, E. & Marron, J.S. | 2011 | *arXiv:1103.3817* | https://arxiv.org/abs/1103.3817 |
| *Functional and Shape Data Analysis* (book) | Srivastava, A. & Klassen, E.P. | 2016 | Springer | https://doi.org/10.1007/978-1-4939-4020-2 |
| "Functional Data Analysis of Amplitude and Phase Variation" (review) | Marron, J.S., Ramsay, J.O., Sangalli, L.M. & Srivastava, A. | 2015 | *Statist. Sci.* 30(4) | https://doi.org/10.1214/15-STS524 |

**Callables covered:** `elastic_align_pair`, `elastic_align_pair_closed`, `elastic_align_pair_constrained`, `elastic_align_pair_multires`, `elastic_align_pair_penalized`, `elastic_changepoint`, `elastic_cross_distance_matrix`, `elastic_cross_distance_matrix_with_band`, `elastic_decomposition`, `elastic_depth`, `elastic_distance`, `elastic_distance_closed`, `elastic_logistic`, `elastic_outlier_detection`, `elastic_partial_match`, `elastic_regression`, `elastic_self_distance_matrix`, `elastic_self_distance_matrix_with_band`, `karcher_mean`, `karcher_mean_closed`, `karcher_mean_with_band`, `karcher_median`, `robust_karcher_mean`, `shape_mean`, `shape_distance`, `shape_self_distance_matrix`, `shape_confidence_interval`, `srsf_transform`, `srsf_inverse`, `tsrvf_transform`, `tsrvf_transform_with_method`, `vert_fpca`, `horiz_fpca`, `horiz_fpns`, `joint_fpca`, `amplitude_distance`, `amplitude_self_distance_matrix`, `phase_distance`, `phase_self_distance_matrix`, `phase_boxplot`, `gauss_model`, `joint_gauss_model`, `bayesian_align_pair`, `curve_geodesic`, `warp_complexity`, `warp_smoothness`, `warp_inverse_error`, `warp_statistics`, `reparameterize_curve`, `invert_warp`, `compose_warps`, `transfer_alignment`, `pairwise_consistency`

**Notes:** Srivastava et al. (2011) arXiv is the primary technical reference; the 2016 book is the full treatment. Landmark registration (`landmark_register`) traces to Ramsay & Silverman (2005). Shift registration (`least_squares_shift_registration`) is also Ramsay & Silverman (2005). Banded elastic alignment (`*_with_band`) references the Sakoe-Chiba band constraint from Sakoe & Chiba (1978) IEEE paper. Bayesian alignment (`bayesian_align_pair`) traces to Cheng et al. (2016) "Bayesian registration of functions and curves" *Bayesian Anal.* 11(2): 447-475. This module is the largest in fdars and requires many distinct paper entries keyed by sub-method.

---

### A11. Shift Registration & Landmark Registration
**fdars modules:** `alignment` (least_squares_shift_*, landmark_*, alignment_quality, diagnose_alignment, peak_persistence, lambda_cv, detect_landmarks, align_to_target)

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) — registration chapters | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |

**Callables covered:** `least_squares_shift_registration`, `least_squares_score`, `pairwise_correlation_score`, `sobolev_least_squares_score`, `align_to_target`, `alignment_quality`, `diagnose_alignment`, `peak_persistence`, `lambda_cv`, `detect_landmarks`, `landmark_register`, `landmark_detect_and_register`

---

### A12. Metrics — Lp, DTW, GAK, Hausdorff
**fdars modules:** `metric`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Fast global alignment kernels" (GAK) | Cuturi, M. | 2011 | *ICML 2011* Proc. 28th ICML: 929-936 | https://dl.acm.org/doi/10.5555/3104482.3104599 |
| "Dynamic programming algorithm optimization for spoken word recognition" (DTW + Sakoe-Chiba band) | Sakoe, H. & Chiba, S. | 1978 | *IEEE Trans. Acoust.* ASSP-26: 43-49 | https://doi.org/10.1109/TASSP.1978.1163055 |
| "Soft-DTW: a differentiable loss function for time-series" | Cuturi, M. & Blondel, M. | 2017 | *ICML 2017* | https://proceedings.mlr.press/v70/cuturi17a.html |

**Callables covered:** `lp_self_1d`, `lp_cross_1d`, `lp_self_2d`, `lp_cross_2d`, `dtw_self_1d`, `dtw_cross_1d`, `soft_dtw_self_1d`, `soft_dtw_cross_1d`, `soft_dtw_div_self_1d`, `soft_dtw_div_cross_1d`, `gak`, `gak_gram_matrix`, `gak_gram_train`, `gak_gram_predict`, `sigma_gak`, `PyGakGramTrain`, `hausdorff_self_1d`, `hausdorff_cross_1d`, `hausdorff_self_2d`, `hausdorff_cross_2d`, `hshift_self_1d`, `hshift_cross_1d`, `fourier_self_1d`, `fourier_cross_1d`, `inprod`, `int_simpson`

**Notes:** Lp distances for functional data are described in Ramsay & Silverman (2005) and Ferraty & Vieu (2006). GAK is unambiguously Cuturi (2011). DTW is Sakoe & Chiba (1978). Soft-DTW is Cuturi & Blondel (2017). Hausdorff distance has no single FDA root paper; it is a classical metric described in a functional data context by Ferraty & Vieu (2006).

---

### A13. Clustering
**fdars modules:** `clustering`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Model-based clustering of time series in group-specific functional subspaces" (KCFC / FunFEM ancestor) | Bouveyron, C. & Jacques, J. | 2011 | *Adv. Data Anal. Classif.* 5(4): 281-300 | https://doi.org/10.1007/s11634-011-0095-6 |
| "The discriminative functional mixture model..." (FunFEM) | Bouveyron, C., Come, E. & Jacques, J. | 2015 | *Ann. Appl. Stat.* 9(4): 1726-1760 | https://doi.org/10.1214/15-AOAS861 |
| "Functional clustering and identifying substructures of longitudinal data" (KCFC) | Chiou, J.-M. & Li, P.-L. | 2007 | *JRSSB* 69(4): 679-699 | https://doi.org/10.1111/j.1467-9868.2007.00605.x |

**Callables covered:** `kmeans_fd`, `kcfc_cluster`, `funfem_cluster`, `dbscan_fd`, `fuzzy_cmeans_fd`, `gmm_cluster`, `align_cluster_fd`, `silhouette_score`, `silhouette_score_data`, `calinski_harabasz`, `calinski_harabasz_data`, `hierarchical_from_distances`, `hierarchical_cut`, `kmedoids_from_distances`

**Notes:** K-means for functional data follows James & Sugar (2003) *JASA* 98(461): 178-186 (DOI: 10.1198/016214503388619113). KCFC is Chiou & Li (2007). FunFEM is Bouveyron et al. (2015) built on Bouveyron & Jacques (2011). DBSCAN for functional data is a direct application of Ester et al. (1996) with no FDA-specific founding paper. Elastic clustering (`align_cluster_fd`) combines Srivastava et al. (2011) alignment with k-means; closest reference is Tucker et al. (2013) or Sangalli et al. (2010) *CSDA* "k-mean alignment for curve clustering." Flag for curators: `kcfc_cluster`, `dbscan_fd`, `align_cluster_fd` have contested or ambiguous single roots.

---

### A14. Classification
**fdars modules:** `classification`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Nonparametric Functional Statistics* — classification chapters | Ferraty, F. & Vieu, P. | 2006 | Springer (book) | https://doi.org/10.1007/0-387-36620-2 |
| "K-class elastic multinomial regression" (elastic multinomial) | Tucker, J.D., Wu, W. & Srivastava, A. | 2013 | *Electron. J. Stat.* 7: 1100-1128 | https://doi.org/10.1214/13-EJS816 |

**Callables covered:** `fclassif_lda`, `fclassif_qda`, `fclassif_knn`, `fclassif_kernel`, `fclassif_dd`, `fclassif_cv`, `elastic_multinomial`, `kernel_classify_from_distances`, `knn_classify_from_distances`

**Notes:** LDA/QDA/kNN via FPC scores is standard material in Ferraty & Vieu (2006) and Ramsay & Silverman (2005). DD-classifier traces to Li et al. (2012) "DD-classifier: Nonparametric classification procedure based on DD-plot" *JASA* 107(499): 737-753 (DOI: 10.1080/01621459.2012.695630). Elastic multinomial is Tucker et al. (2013).

---

### A15. Functional Inference — Tests & SCBs
**fdars modules:** `inference`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "An ANOVA test for functional data" (permutation tests) | Cuevas, A., Febrero, M. & Fraiman, R. | 2004 | *CSDA* 47(1): 111-122 | https://doi.org/10.1016/j.csda.2003.10.021 |
| "Simultaneous confidence bands for nonparametric regression with functional data" (SCB) | Degras, D. | 2011 | *Statistica Sinica* 21(4): 1735-1765 | https://www3.stat.sinica.edu.tw/sstest/j21n4/J21N412/J21N412.html |
| "Interval-wise testing for functional data" (ITP) | Pini, A. & Vantini, S. | 2017 | *J. Nonparam. Stat.* 29(2): 407-424 | https://doi.org/10.1080/10485252.2017.1306627 |

**Callables covered:** `t_perm_test`, `f_perm_test`, `two_sample_mean_test`, `mean_scb`, `scb_two_sample_test`, `flm_f_test`, `flm_gof_test`, `oneway_anova_vstat`, `itp_one_pop`, `itp_two_pop`, `itp_flm`

**Notes:** Two-sample permutation tests (`t_perm_test`, `f_perm_test`) trace to Cuevas et al. (2004). SCBs trace to Degras (2011). The V-statistic one-way ANOVA (`oneway_anova_vstat`) traces to Zhang & Liang (2014) "One-way ANOVA for functional data via globalizing the pointwise F-test" *Scand. J. Statist.* 41(1): 51-71 — flag for curator verification. ITP (`itp_*`) is unambiguously Pini & Vantini (2017).

---

### A16. Functional Time Series
**fdars modules:** `fts`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Forecasting functional time series" (FTSM) | Hyndman, R.J. & Shang, H.L. | 2009 | *J. Korean Statist. Soc.* 38(3): 199-211 | https://doi.org/10.1016/j.jkss.2009.06.002 |
| "Dynamic functional principal components" (DPCA) | Hormann, S., Kidzinski, L. & Hallin, M. | 2015 | *JRSSB* 77(2): 319-348 | https://doi.org/10.1111/rssb.12076 |

**Callables covered:** `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr`, `functional_acf`, `functional_pacf`, `long_run_covariance`, `spectral_density`, `dpca`, `dpca_reconstruct`, `stationarity_test`, `functional_difference`

**Notes:** FTSM (FPCA + Yule-Walker AR) is Hyndman & Shang (2009). DPCA is Hormann, Kidzinski & Hallin (2015). Functional PLS for FTS (`fplsr`) is described in Aue, Norinho & Hormann (2015) "On the prediction of stationary functional time series" *JASA* 110(509): 378-392. Long-run covariance estimation traces to Hormann & Kokoszka (2010) "Weakly dependent functional data" *Ann. Statist.* 38(3): 1845-1884. Stationarity test traces to Horvath, Kokoszka & Rice (2014) "Testing stationarity of functional time series" *J. Econometrics* 179: 66-82. Each sub-method needs a separate entry in the references JSON.

---

### A17. Shapelets
**fdars modules:** `shapelet`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Time series shapelets: a new primitive for data mining" | Ye, L. & Keogh, E. | 2009 | *KDD 2009*, pp. 947-956 | https://dl.acm.org/doi/10.1145/1557019.1557122 |
| "Time series shapelets: a novel technique..." (journal version) | Ye, L. & Keogh, E. | 2011 | *Data Min. Knowl. Discov.* 22: 149-182 | https://doi.org/10.1007/s10618-010-0179-5 |

**Callables covered:** `discover_shapelets`, `shapelet_transform_fit`, `shapelet_transform`, `shapelet_classifier_fit`, `shapelet_distance`, `PyShapeletFit`, `PyShapeletClassifierFit`

**Notes:** Ye & Keogh (2009) is the original KDD conference paper; the 2011 journal version is the more complete reference. The shapelets approach for functional data classification is a direct application with no separate FDA-specific foundational paper. Information-gain quality criterion is from the same paper.

---

### A18. Multivariate Functional Data & MFPCA
**fdars modules:** `multi_fdata`, `spm` (mfpca, spe_multivariate), `famm`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Multivariate functional principal component analysis for data observed on different (dimensional) domains" | Happ, C. & Greven, S. | 2018 | *JASA* 113(522): 649-659 | https://doi.org/10.1080/01621459.2016.1273115 |

**Callables covered:** `PyMultiFunData`, `multi_fdata_from_components`, `mfpca`, `spe_multivariate`, `dense_flmm`, `fast_fmm`, `multi_famm`

**Notes:** MFPCA is unambiguously Happ & Greven (2018). The Functional Linear Mixed Model (`dense_flmm`, `fast_fmm`, `multi_famm`) traces to Greven & Scheipl (2017) "A general framework for functional regression modelling" *Stat. Model.* 17(1-2): 1-35 and Scheipl, Staicu & Greven (2015) "Functional additive mixed models" *JCGS* 24(2): 477-501 (DOI: 10.1080/10618600.2014.901914). Multiple plausible attributions; flag for curator.

---

### A19. Statistical Process Monitoring / SPM
**fdars modules:** `spm`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Multivariate quality control" (Hotelling T-squared origin) | Hotelling, H. | 1947 | Chapter in *Techniques of Statistical Analysis* | (no DOI; historical) |
| "Control procedures for residuals associated with principal component analysis" (T²/SPE pattern) | Jackson, J.E. & Mudholkar, G.S. | 1979 | *Technometrics* 21(3): 341-349 | https://doi.org/10.1080/00401706.1979.10489779 |

**Callables covered:** `spm_phase1`, `spm_monitor`, `spm_ewma`, `spm_cusum`, `hotelling_t2`, `hotelling_t2_regularized`, `t2_control_limit`, `t2_limit_robust`, `t2_pc_contributions`, `t2_pc_significance`, `spe_control_limit`, `spe_limit_robust`, `spe_moment_match_diagnostic`, `arl0_t2`, `arl1_t2`, `arl0_spe`, `arl0_ewma_t2`, `select_ncomp`, `ewma_scores`, `nelson_rules`, `western_electric_rules`

**ANTI-FEATURE NOTE:** Functional data SPM is an extension of classical multivariate SPC with no single canonical FDA-SPM paper. Curators should cite Jackson & Mudholkar (1979) as the T²/SPE root and note that the functional extension follows Colosimo & Pacella (2007) *Int. J. Prod. Res.* 45(23): 5563-5581 or Woodall et al. (2004) *J. Qual. Technol.* 36(3): 309-320. Forcing a single FDA citation would mislead.

---

### A20. Conformal Prediction & Tolerance Bands
**fdars modules:** `conformal`, `tolerance`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Conformal prediction: a gentle introduction" | Angelopoulos, A.N. & Bates, S. | 2023 | *Found. Trends Mach. Learn.* 16(4): 494-591 | https://doi.org/10.1561/2200000101 |

**Callables covered:** `conformal_classif`, `conformal_fregre_lm`, `conformal_fregre_np`, `conformal_logistic`, `conformal_elastic_regression`, `conformal_elastic_pcr`, `conformal_elastic_logistic`, `fpca_tolerance_band`, `elastic_tolerance_band`, `elastic_tolerance_band_with_config`, `exponential_family_tolerance_band`, `phase_tolerance_band`, `conformal_prediction_band`, `equivalence_test`, `equivalence_test_one_sample`, `scb_mean_degras`

**ANTI-FEATURE NOTE:** Conformal prediction for functional data is a 2020-present research frontier with no consensus single foundational FDA paper. The CP framework root is Vovk, Gammerman & Shafer (2005) book + Angelopoulos & Bates (2023) survey. Functional conformal prediction is described in Diquigiovanni, Fontana & Vantini (2022) "Conformal prediction bands for multivariate functional data" *J. Multivar. Anal.* 189: 104879 (DOI: 10.1016/j.jmva.2021.104879) — a plausible functional-specific reference, but the field remains active and contested.

---

### A21. Simulation & GP Sampling
**fdars modules:** `simulation`, `covariance`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) — simulation / Karhunen-Loeve chapters | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |
| *Gaussian Processes for Machine Learning* (kernel definitions) | Rasmussen, C.E. & Williams, C.K.I. | 2006 | MIT Press (book) | https://gaussianprocess.org/gpml/ |

**Callables covered:** `sim_kl`, `simulate`, `eigenfunctions`, `eigenvalues`, `covariance_matrix`, `gaussian_process`, `add_error_curve`, `add_error_pointwise`, `kernel_gaussian`, `kernel_exponential`, `kernel_brownian`, `kernel_matern`, `kernel_periodic`, `kernel_linear`, `kernel_polynomial`, `kernel_whitenoise`, `kernel_add`, `kernel_mult`, `make_gaussian_process`, `r_brownian`, `r_bridge`, `r_ou`

---

### A22. Seasonality & Period Detection
**fdars modules:** `seasonal`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "STL: A seasonal-trend decomposition procedure based on loess" | Cleveland, R.B., Cleveland, W.S., McRae, J.E. & Terpenning, I. | 1990 | *J. Official Statist.* 6(1): 3-73 | https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/stl-a-seasonal-trend-decomposition-procedure-based-on-loess.pdf |

**Callables covered:** `stl_decompose`, `autoperiod`, `cfd_autoperiod`, `estimate_period_acf`, `estimate_period_fft`, `instantaneous_period`, `sazed`, `lomb_scargle_fdata`, `matrix_profile_fdata`, `detect_peaks`, `detect_seasonality_changes`, `detect_multiple_periods`, `seasonal_strength`, `seasonal_strength_wavelet`, `seasonal_strength_windowed`, `classify_seasonality`, `ssa_fdata`, `analyze_peak_timing`

**ANTI-FEATURE NOTE:** The `seasonal` module is the most heterogeneous in provenance. Each sub-method has its own root paper from distinct research communities: STL (Cleveland et al. 1990), Lomb-Scargle periodogram (Lomb 1976; Scargle 1982), SSA (Broomhead & King 1986), Matrix Profile (Yeh et al. 2016 ICDM), SAZED (Talagala et al. 2021). A single root citation for this module does not exist. Curators must list sub-method-level citations.

---

### A23. Scoring Metrics
**fdars modules:** `scoring`, `metrics`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| *Functional Data Analysis* (2nd ed.) — regression evaluation | Ramsay, J.O. & Silverman, B.W. | 2005 | Springer (book) | https://doi.org/10.1007/b98888 |

**Callables covered:** `functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, `functional_explained_variance`, `pred_mae`, `pred_mse`, `pred_rmse`, `pred_r2`, `prediction_metrics`

**ANTI-FEATURE NOTE:** These are standard scalar metrics integrated over the domain. No FDA-specific founding paper exists. Forcing a single citation would be an overreach. The appropriate note for these callables is "domain-integrated extensions of standard prediction metrics; see standard ML/statistics references (e.g., Hastie, Tibshirani & Friedman 2009)."

---

### A24. Explainability / XAI
**fdars modules:** `explain`

| Paper | Authors | Year | Venue | DOI / URL |
|-------|---------|------|-------|-----------|
| "Why should I trust you? Explaining the predictions of any classifier" (LIME) | Ribeiro, M.T., Singh, S. & Guestrin, C. | 2016 | *KDD 2016* | https://dl.acm.org/doi/10.1145/2939672.2939778 |
| "A unified approach to interpreting model predictions" (SHAP) | Lundberg, S.M. & Lee, S.-I. | 2017 | *NeurIPS 2017* | https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html |
| "Anchors: High-precision model-agnostic explanations" | Ribeiro, M.T., Singh, S. & Guestrin, C. | 2018 | *AAAI 2018* | https://ojs.aaai.org/index.php/AAAI/article/view/11491 |

**Callables covered:** All `explain.*` callables

**ANTI-FEATURE NOTE:** The `explain` module applies standard ML XAI techniques (LIME, SHAP, Anchors, ALE, PDP, permutation importance) to functional regression/classification models via FPC scores. Root papers are ML-community XAI papers listed above, not FDA-specific. No dedicated FDA-XAI foundational paper exists. Forcing FDA-specific citations would mislead.

---

## Part B — Cross-Language Implementation Landscape

### B1. R Implementation Landscape

| fdars Family | R Package | Representative Function | CRAN / URL | Gap? |
|---|---|---|---|---|
| Basis expansion & smoothing | `fda` (Ramsay) | `create.bspline.basis`, `smooth.basis` | https://cran.r-project.org/package=fda | No gap |
| Basis expansion & smoothing | `refund` | `pfr`, `pffr` | https://cran.r-project.org/package=refund | No gap |
| Functional statistics (mean/var/cov) | `fda` | `mean.fd`, `var.fd` | https://cran.r-project.org/package=fda | No gap |
| Functional statistics | `fda.usc` | `func.mean`, `func.var` | https://cran.r-project.org/package=fda.usc | No gap |
| FM depth | `fda.usc` | `depth.FM` | https://cran.r-project.org/package=fda.usc | No gap |
| Band depth / modified band depth | `fda.usc` | `depth.mode`, `depth.BD` | https://cran.r-project.org/package=fda.usc | No gap |
| Functional depth (unified) | `ddalpha` | `depthf.FM1`, `depthf.BD` | https://cran.r-project.org/package=ddalpha | No gap |
| Functional boxplot | `fdaoutlier` | `functional_boxplot` | https://cran.r-project.org/package=fdaoutlier | No gap |
| Outlier detection (MS-plot, MUOD, TVDMSS) | `fdaoutlier` | `msplot`, `muod`, `tvdmss`, `dir_out` | https://cran.r-project.org/package=fdaoutlier | No gap |
| FPCA (dense) | `fda` | `pca.fd` | https://cran.r-project.org/package=fda | No gap |
| PACE FPCA (sparse) | `fdapace` | `FPCA` | https://cran.r-project.org/package=fdapace | No gap |
| Kernel smoothing | `fda.usc` | `optim.np`, `fdata.comp` | https://cran.r-project.org/package=fda.usc | No gap |
| Scalar-on-function regression | `refund` | `pfr` | https://cran.r-project.org/package=refund | No gap |
| Scalar-on-function regression | `fda.usc` | `fregre.np`, `fregre.lm` | https://cran.r-project.org/package=fda.usc | No gap |
| Functional GLM | `refund` | `pfr` (with family arg) | https://cran.r-project.org/package=refund | No gap |
| Concurrent regression | `refund` | `ccb`, `peer` | https://cran.r-project.org/package=refund | No gap |
| Function-on-function regression | `refund` | `pffr` | https://cran.r-project.org/package=refund | No gap |
| Function-on-scalar regression | `refund` | `fosr` | https://cran.r-project.org/package=refund | No gap |
| Elastic / SRSF registration | `fdasrvf` | `time_warping`, `elastic.regression` | https://cran.r-project.org/package=fdasrvf | No gap |
| Shift / landmark registration | `fda` | `register.fd` | https://cran.r-project.org/package=fda | No gap |
| DTW metrics | `dtw` | `dtw` | https://cran.r-project.org/package=dtw | No gap |
| GAK metric | `dtwclust` | `GAK` | https://cran.r-project.org/package=dtwclust | No gap |
| k-means clustering (functional) | `fda.usc` | `kmeans.fd` | https://cran.r-project.org/package=fda.usc | No gap |
| FunFEM clustering | `funFEM` | `funFEM` | https://cran.r-project.org/package=funFEM | No gap |
| MFPCA | `MFPCA` | `MFPCA` | https://cran.r-project.org/package=MFPCA | No gap |
| Multi-domain data container | `funData` | `funData`, `multiFunData` | https://cran.r-project.org/package=funData | No gap |
| Functional inference (perm tests) | `fda.usc` | `fanova.onefactor` | https://cran.r-project.org/package=fda.usc | No gap |
| ITP interval testing | `fdatest` (GitHub only) | `IWT1`, `IWT2`, `IWTlm` | https://github.com/alessiapini/fdatest | GAP: not on CRAN |
| Functional time series (FTSM) | `ftsa` | `fts`, `ftsm`, `forecast.fts` | https://cran.r-project.org/package=ftsa | No gap |
| DPCA | `freqdom.fda` | `fts.dpca`, `fts.spectral.density` | https://cran.r-project.org/package=freqdom.fda | No gap |
| Frechet regression | NO standard R package | — | — | GAP: research code only |
| Density FDA (LQD/Wasserstein) | NO CRAN package | — | — | GAP: `fdadensity` on GitHub only |
| Shapelets | NO R package | — | — | GAP: no CRAN or major R shapelets package |
| Functional SPM | NO dedicated R package | — | — | GAP: `fda.usc` has partial SPC; no dedicated FDA-SPM package |
| Conformal prediction (functional) | `conformalInference.fd` (GitHub) | `conformal.fd` | https://github.com/Paolo-Bosc/conformalInference.fd | GAP: not on CRAN |
| XAI for functional models | NO FDA-specific R package | — | — | GAP: general `DALEX`, `iml` exist but not FDA-aware |
| Elastic classification | `fdasrvf` | `elastic.logistic`, `elastic.mlogistic` | https://cran.r-project.org/package=fdasrvf | No gap |

---

### B2. Python Implementation Landscape

| fdars Family | Python Package | Representative Function/Class | PyPI / URL | Gap? |
|---|---|---|---|---|
| Basis expansion & smoothing | `scikit-fda` | `BSplineBasis`, `FourierBasis`, `BasisSmoother` | https://pypi.org/project/scikit-fda/ | No gap |
| Functional statistics | `scikit-fda` | `FDataGrid.mean()`, `.var()`, `.cov()` | https://fda.readthedocs.io | No gap |
| FM depth / band depth | `scikit-fda` | `fraiman_muniz_depth`, `band_depth`, `modified_band_depth` | https://fda.readthedocs.io | No gap |
| Functional boxplot | `scikit-fda` | `FunctionalBoxplot` | https://fda.readthedocs.io | No gap |
| FPCA (dense) | `scikit-fda` | `FPCA` | https://fda.readthedocs.io | No gap |
| PACE FPCA (sparse) | NO mature Python package | — | — | GAP: `scikit-fda` has partial support; no PACE BLUP scoring |
| Kernel smoothing | `scikit-fda` | `KernelSmoother` | https://fda.readthedocs.io | No gap |
| Scalar-on-function regression | `scikit-fda` | `LinearFunctionalRegression` | https://fda.readthedocs.io | No gap |
| Functional GLM (logistic) | `scikit-fda` | partial via `LinearFunctionalRegression` | https://fda.readthedocs.io | Partial gap: no standalone functional GLM family dispatch |
| Elastic / SRSF registration | `fdasrsf` | `time_warping`, `elastic_regression` | https://pypi.org/project/fdasrsf/ | No gap |
| Elastic / SRSF registration | `scikit-fda` | `ElasticRegistration` | https://fda.readthedocs.io | No gap (second option) |
| DTW metrics | `tslearn` | `dtw`, `dtw_path` | https://pypi.org/project/tslearn/ | No gap |
| GAK metric | `tslearn` | `GlobalAlignmentKernel` | https://pypi.org/project/tslearn/ | No gap |
| Soft-DTW | `tslearn` | `SoftDTW` | https://pypi.org/project/tslearn/ | No gap |
| k-means clustering (functional) | `scikit-fda` | `FuzzyKMeans`, `KMeans` | https://fda.readthedocs.io | No gap |
| FunFEM clustering | NO Python package | — | — | GAP: no Python port |
| MFPCA | NO mature Python package | — | — | GAP: scikit-fda lacks multi-domain MFPCA |
| Functional inference (perm tests) | `scikit-fda` | `hotelling_t2` (partial) | https://fda.readthedocs.io | Partial gap |
| ITP interval testing | NO Python package | — | — | GAP: R-only |
| Functional time series | NO dedicated Python package | — | — | GAP: `statsmodels` handles scalar TS; no functional TS |
| Frechet regression | NO Python package | — | — | GAP: research code only |
| Density FDA (LQD/Wasserstein) | `POT` (partial) | `ot.barycenter_sinkhorn` | https://pypi.org/project/POT/ | Partial gap: Wasserstein barycenter only; not LQD-framed |
| Shapelets | `tslearn` | `ShapeletModel` | https://pypi.org/project/tslearn/ | No gap |
| Shapelets | `sktime` | `ShapeletTransformClassifier` | https://pypi.org/project/sktime/ | No gap (second option) |
| Functional SPM | NO FDA-specific Python package | — | — | GAP: no functional SPC Python package |
| Conformal prediction | `MAPIE` (general) | `MapieRegressor` | https://pypi.org/project/mapie/ | Partial gap: general CP, not FDA-specific |
| XAI for functional models | `shap`, `lime` | standard APIs | https://pypi.org/project/shap/ | Partial gap: not FDA-aware |
| Outlier detection | `scikit-fda` | `OutliergramOutlierDetector`, `FunctionalBoxplotOutlierDetector` | https://fda.readthedocs.io | No gap for common methods |

---

### B3. Matlab Implementation Landscape

| fdars Family | Matlab Toolbox | Representative Function | URL | Gap? |
|---|---|---|---|---|
| Basis expansion & smoothing | `fdaM` (Ramsay) | `create_bspline_basis`, `smooth_basis` | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| Functional statistics | `fdaM` | `mean_fd`, `var_fd` | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| FPCA (dense) | `fdaM` | `pca_fd` | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| PACE FPCA (sparse) | `PACE` (UC Davis) | `FPCA` | https://anson.ucdavis.edu/~mueller/data/pace.html | No gap |
| Kernel smoothing | `fdaM` | `smooth_basis`, kernel functions | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| Scalar-on-function regression | `fdaM` | `fRegress` | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| Concurrent regression | `fdaM` | `fRegress` (pointwise basis) | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| Elastic / SRSF registration | `fdasrvf_MATLAB` | `time_warping`, `ElasticFunctionData` | https://github.com/jdtuck/fdasrvf_MATLAB | No gap |
| Shift / landmark registration | `fdaM` | `register_fd` | https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/ | No gap |
| Functional depth | NO dedicated Matlab toolbox | — | — | GAP: depth functions scattered across paper-specific research code |
| Functional boxplot | `PACE` (partial) | trajectory boxplot | https://anson.ucdavis.edu/~mueller/data/pace.html | Partial gap |
| Outlier detection | NO Matlab toolbox | — | — | GAP: no equivalent to fdaoutlier |
| k-means clustering | NO dedicated Matlab FDA package | — | — | GAP: custom code in papers |
| FunFEM clustering | NO Matlab implementation | — | — | GAP |
| MFPCA | NO Matlab toolbox | — | — | GAP: research code only |
| ITP interval testing | NO Matlab toolbox | — | — | GAP: R-only |
| Functional time series | NO dedicated Matlab toolbox | — | — | GAP: PACE has trajectory tools; no FTSM/DPCA |
| Frechet regression | NO Matlab toolbox | — | — | GAP |
| Density FDA (LQD) | NO Matlab toolbox | — | — | GAP |
| Shapelets | NO FDA Matlab toolbox | — | — | GAP |
| Functional SPM | Statistics and ML Toolbox | `hotelling` | https://www.mathworks.com/products/statistics.html | Partial gap: classical Hotelling T2; no functional version |
| Conformal prediction | NO Matlab toolbox | — | — | GAP |

---

## Feature Landscape (Per Milestone Taxonomy)

### Table Stakes
Families with a clear single root paper and obvious R + Matlab equivalents. Curation is straightforward; attribution is uncontested.

| Family | fdars Module | Root Paper | R Pkg | Python Pkg | Matlab Pkg |
|--------|-------------|------------|-------|------------|------------|
| B-spline / Fourier basis | `basis` | Ramsay & Silverman (2005) | `fda` | `scikit-fda` | `fdaM` |
| Penalized smoothing (GCV/AIC) | `smoothing` | Ramsay & Silverman (2005) | `fda`, `refund` | `scikit-fda` | `fdaM` |
| Functional mean / var / cov | `fdata` | Ramsay & Silverman (2005) | `fda`, `fda.usc` | `scikit-fda` | `fdaM` |
| FM depth | `depth.fraiman_muniz_*` | Fraiman & Muniz (2001) | `fda.usc::depth.FM` | `scikit-fda` | GAP |
| Band depth / modified band | `depth.band_1d`, `modified_band_1d` | Lopez-Pintado & Romo (2009) | `fda.usc`, `fdaoutlier` | `scikit-fda` | GAP |
| Functional boxplot | `depth.functional_boxplot` | Sun & Genton (2011) | `fdaoutlier` | `scikit-fda` | `PACE` (partial) |
| FPCA (dense) | `regression.fpca` | Ramsay & Silverman (2005) | `fda`, `fdapace` | `scikit-fda` | `fdaM`, `PACE` |
| PACE FPCA (sparse) | `pace_fpca` | Yao, Muller & Wang (2005) | `fdapace` | GAP | `PACE` |
| Scalar-on-function FPC regression | `regression.fregre_lm` | Cardot et al. (1999/2003) | `refund`, `fda.usc` | `scikit-fda` | `fdaM` |
| Elastic / SRSF registration | `alignment` (elastic_*) | Srivastava et al. (2011) | `fdasrvf` | `fdasrsf` | `fdasrvf_MATLAB` |
| GAK metric | `metric.gak*` | Cuturi (2011) | `dtwclust::GAK` | `tslearn` | GAP |
| DTW metric | `metric.dtw_*` | Sakoe & Chiba (1978) | `dtw` | `tslearn` | GAP |
| Functional ANOVA (permutation) | `inference`, `regression.fanova` | Cuevas et al. (2004) | `fda.usc` | `scikit-fda` (partial) | GAP |
| Simultaneous confidence bands | `inference.mean_scb` | Degras (2011) | `fda` (partial) | GAP | GAP |
| Functional time series (FTSM) | `fts.ftsm*` | Hyndman & Shang (2009) | `ftsa` | GAP | GAP |
| DPCA | `fts.dpca` | Hormann et al. (2015) | `freqdom.fda` | GAP | GAP |
| Shapelets | `shapelet` | Ye & Keogh (2009) | GAP | `tslearn`, `sktime` | GAP |
| Multi-domain MFPCA | `spm.mfpca`, `multi_fdata` | Happ & Greven (2018) | `MFPCA`, `funData` | GAP | GAP |

### Differentiators
Families where fdars' provenance documentation is more valuable because implementations are scattered, new, or cross-language gaps exist.

| Family | fdars Module | Root Paper | Why Differentiating |
|--------|-------------|------------|---------------------|
| Frechet regression on metric spaces | `frechet` | Petersen & Muller (2019) | No CRAN, no PyPI, no Matlab toolbox. Research code only. fdars is a notable implementation. |
| Density FDA (LQD/Wasserstein) | `density_fda` | Petersen & Muller (2016) | No CRAN/PyPI package with LQD framing; `POT` Python covers Wasserstein barycenter only. |
| ITP interval-wise testing | `inference.itp_*` | Pini & Vantini (2017) | Only in unmaintained GitHub R package (`fdatest`); no Python or Matlab. |
| FunFEM clustering | `clustering.funfem_cluster` | Bouveyron et al. (2015) | R `funFEM` CRAN exists; no Python or Matlab port. |
| Functional time series (full: ACF/PACF, long-run cov, DPCA) | `fts` | Hormann et al. (2015); Hyndman & Shang (2009) | R has `ftsa` + `freqdom.fda`; Python has nothing dedicated; Matlab gap. |
| MUOD / TVDMSS / depthgram / sequential outlier | `outliers` | Dai & Genton (2018/2019) etc. | R `fdaoutlier` covers these; Python and Matlab lack equivalents. |
| Functional XAI (LIME/SHAP applied to FDA models) | `explain` | Ribeiro et al. (2016); Lundberg & Lee (2017) | No R/Python/Matlab package applies XAI specifically to functional regression/classification models. |
| Conformal prediction for functional data | `conformal`, `tolerance` | Angelopoulos & Bates (2023) | Only an unmaintained GitHub R package; no Python or Matlab. |
| Functional SPM (T2/SPE on FPC scores) | `spm` | Jackson & Mudholkar (1979) extended to FDA | No dedicated functional SPC package in any language. |
| Soft-DTW | `metric.soft_dtw_*` | Cuturi & Blondel (2017) | Python `tslearn` has it; no R CRAN package; no Matlab. |
| Elastic multinomial classification | `classification.elastic_multinomial` | Tucker et al. (2013) | `fdasrvf` R covers this; no Python sklearn-compatible version. |
| Bayesian alignment | `alignment.bayesian_align_pair` | Cheng et al. (2016) | Research code only; no standard package in any language. |
| PACE FPCA in Python | `pace_fpca` | Yao et al. (2005) | R `fdapace` and Matlab `PACE` exist; no mature Python equivalent. |

### Anti-Features (Do Not Force a Single Citation)
Families where assigning a single foundational paper would be misleading or inaccurate.

| Family | fdars Module | Why Ambiguous / Anti-Feature |
|--------|-------------|------------------------------|
| Functional depth (as a category) | `depth` | At least 7 distinct root papers across methods. The `functional_depth` dispatcher unifies them; no single citation fits the module. |
| Scoring metrics (MAE/MSE/MAPE etc.) | `scoring`, `metrics` | Standard scalar metrics integrated over domain. No FDA-specific founding paper. |
| Functional SPM | `spm` | T2/SPE traces to Hotelling (1947) and Jackson & Mudholkar (1979); functional extension is spread across applied papers without a single canonical FDA-SPM paper. |
| Seasonal decomposition | `seasonal` | Each sub-method has its own root paper from distinct research communities (STL, Lomb-Scargle, SSA, Matrix Profile, SAZED). |
| XAI for functional models | `explain` | Root papers are ML-community XAI papers (LIME, SHAP, Anchors). No canonical FDA-XAI paper exists. |
| Conformal prediction | `conformal`, `tolerance` | Active 2020-present research frontier; no single paper has achieved consensus for functional data. |

---

## Feature Dependencies

```
Paper-level curation (REFERENCES_MAP JSON)
    requires ---> Callable-to-paper index (callable_refs field in JSON)
                      requires ---> Part A per-family tables (this document)

Cross-language implementation pointers (Part B)
    enhances ---> Skill hybrid-protocol answers ("alternatives in R/Matlab?")

fdars_method_references MCP tool
    requires ---> REFERENCES_MAP JSON (static, via importlib.resources)
    provides ---> curated entry OR explicit "ungrounded, flag it" signal

fdars-capabilities skill extension
    extends ---> v12.0 capability-discovery skill
    uses ---> MCP tool as grounded source
    falls back to ---> LLM synthesis FLAGGED as ungrounded
```

### Dependency Notes

- **Paper-level JSON requires this document:** The Part A tables are the direct authoring source for the `_references_map.json` file to be created in v13.0. Each family section maps to one or more top-level entries in that JSON.
- **Anti-feature families require explicit ungrounded signal:** For families marked anti-feature above (seasonal, scoring, SPM, XAI), the MCP tool should return an explicit "no single curated entry — ungrounded synthesis permitted, flag it" signal rather than a forced single paper.
- **Multi-paper families require method-keyed entries:** The `depth`, `alignment`, `regression`, and `fts` modules each require multiple JSON entries, keyed by the specific method or callable group, not at the module level.

---

## MVP Definition

### Phase 1: Core reference map (essential for roadmap)
- Cover all 24 families (A1-A24) with at least one curated paper entry per family
- Priority: A1-A18 (non-seasonal, non-conformal) have HIGH curation confidence
- Callable-to-paper index covering the ~300 non-XAI/non-SPM callables

### Phase 2: MCP tool + skill extension
- `fdars_method_references(method)` LLM-free static lookup via `importlib.resources`
- `fdars-capabilities` skill extended with hybrid protocol (curated first, flagged-LLM fallback)

### Phase 3: Docs surface
- References page on the MkDocs site
- Per-method "References" blocks on method pages
- `llms.txt` extended with provenance data

### Defer
- DOI network validation (offline JSON sufficient for v13.0 gate)
- Automated citation count or impact factor scraping
- Full XAI `explain` module citation coverage (anti-feature risk; low demand)

---

## Sources

- [Ramsay & Silverman (2005) Springer](https://link.springer.com/book/10.1007/b98888)
- [Ramsay, Hooker & Graves (2009) Springer](https://link.springer.com/book/10.1007/978-0-387-98185-7)
- [Fraiman & Muniz (2001) TEST](https://link.springer.com/article/10.1007/BF02595706)
- [Lopez-Pintado & Romo (2009) JASA](https://doi.org/10.1198/jasa.2009.0015)
- [Lopez-Pintado & Romo (2011) CSDA](https://doi.org/10.1016/j.csda.2010.10.029)
- [Nieto-Reyes & Battey (2016) Statist. Sci.](https://doi.org/10.1214/15-STS532)
- [Yao, Muller & Wang (2005) JASA](https://www.tandfonline.com/doi/abs/10.1198/016214504000001745)
- [Srivastava et al. (2011) arXiv](https://arxiv.org/abs/1103.3817)
- [Srivastava & Klassen (2016) Springer book](https://doi.org/10.1007/978-1-4939-4020-2)
- [Marron et al. (2015) Statist. Sci.](https://doi.org/10.1214/15-STS524)
- [Petersen & Muller (2019) Ann. Statist.](https://doi.org/10.1214/17-AOS1624)
- [Petersen & Muller (2016) Ann. Statist. LQD](https://doi.org/10.1214/15-AOS1363)
- [Hyndman & Shang (2009) J. Korean Statist. Soc.](https://doi.org/10.1016/j.jkss.2009.06.002)
- [Hormann, Kidzinski & Hallin (2015) JRSSB](https://doi.org/10.1111/rssb.12076)
- [Cuturi (2011) ICML](https://dl.acm.org/doi/10.5555/3104482.3104599)
- [Cuturi & Blondel (2017) ICML](https://proceedings.mlr.press/v70/cuturi17a.html)
- [Sakoe & Chiba (1978) IEEE Trans. Acoust.](https://doi.org/10.1109/TASSP.1978.1163055)
- [Ye & Keogh (2009) KDD](https://dl.acm.org/doi/10.1145/1557019.1557122)
- [Ye & Keogh (2011) DMKD](https://doi.org/10.1007/s10618-010-0179-5)
- [Bouveyron & Jacques (2011) ADAC](https://doi.org/10.1007/s11634-011-0095-6)
- [Bouveyron, Come & Jacques (2015) Ann. Appl. Stat.](https://doi.org/10.1214/15-AOAS861)
- [Happ & Greven (2018) JASA](https://doi.org/10.1080/01621459.2016.1273115)
- [Sun & Genton (2011) JCGS](https://doi.org/10.1198/jcgs.2011.09224)
- [Dai & Genton (2018) JCGS](https://doi.org/10.1080/10618600.2018.1473781)
- [Dai & Genton (2019) CSDA](https://doi.org/10.1016/j.csda.2018.03.017)
- [Pini & Vantini (2017) J. Nonparam. Stat.](https://doi.org/10.1080/10485252.2017.1306627)
- [Degras (2011) Statistica Sinica](https://www3.stat.sinica.edu.tw/sstest/j21n4/J21N412/J21N412.html)
- [Cuevas, Febrero & Fraiman (2004) CSDA](https://doi.org/10.1016/j.csda.2003.10.021)
- [Jackson & Mudholkar (1979) Technometrics](https://doi.org/10.1080/00401706.1979.10489779)
- [Cardot, Ferraty & Sarda (1999) Statist. Probab. Lett.](https://doi.org/10.1016/S0167-7152(99)00036-X)
- [Muller & Yao (2008) JASA](https://doi.org/10.1198/016214508000000516)
- [Tucker, Wu & Srivastava (2013) EJS](https://doi.org/10.1214/13-EJS816)
- [Chiou & Li (2007) JRSSB](https://doi.org/10.1111/j.1467-9868.2007.00605.x)
- [Angelopoulos & Bates (2023) Found. Trends](https://doi.org/10.1561/2200000101)
- [scikit-fda documentation](https://fda.readthedocs.io/)
- [R fda CRAN](https://cran.r-project.org/package=fda)
- [R fda.usc CRAN](https://cran.r-project.org/package=fda.usc)
- [R refund CRAN](https://cran.r-project.org/package=refund)
- [R fdapace CRAN](https://cran.r-project.org/package=fdapace)
- [R fdasrvf CRAN](https://cran.r-project.org/package=fdasrvf)
- [R fdaoutlier CRAN](https://cran.r-project.org/package=fdaoutlier)
- [R MFPCA CRAN](https://cran.r-project.org/package=MFPCA)
- [R funFEM CRAN](https://cran.r-project.org/package=funFEM)
- [R ftsa CRAN](https://cran.r-project.org/package=ftsa)
- [R freqdom.fda CRAN](https://cran.r-project.org/package=freqdom.fda)
- [fdasrsf Python PyPI](https://pypi.org/project/fdasrsf)
- [fdasrvf Matlab GitHub](https://github.com/jdtuck/fdasrvf_MATLAB)
- [fdaM Matlab McGill](https://www.psych.mcgill.ca/misc/fda/downloads/FDAfuns/)
- [PACE Matlab UC Davis](https://anson.ucdavis.edu/~mueller/data/pace.html)
- [CRAN Task View Functional Data Analysis](https://cran.r-project.org/view=FunctionalData)

---

*Feature research for: v13.0 Scientific Provenance & Cross-Language Implementations (fdars)*
*Researched: 2026-09-07*
