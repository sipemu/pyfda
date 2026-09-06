# fdars AI Capability Map

This page is the human-readable companion to the machine-readable [`llms.txt`](https://sipemu.github.io/pyfda/llms.txt) digest. It lists every public callable in the `fdars` library, grouped by submodule.

**30 submodules &middot; 409 public callables** — all generated offline from the committed capability map. AI agents: use `fdars_list_capabilities()` (MCP tool) or [llms.txt](https://sipemu.github.io/pyfda/llms.txt) for the machine-readable form.

## Module Index

| Module | Purpose | Functions |
|--------|---------|-----------|
| [`fdars.alignment`](#alignment) | Elastic alignment, SRSF registration, Karcher mean, elastic FPCA | 68 |
| [`fdars.basis`](#basis) | Basis representations — B-spline, Fourier, functional PCA | 16 |
| [`fdars.classification`](#classification) | Functional classifiers — k-nearest neighbours, SVM, centroid-based | 9 |
| [`fdars.clustering`](#clustering) | Functional k-means, fuzzy, GMM, and elastic clustering | 11 |
| [`fdars.conformal`](#conformal) | Conformal prediction and classification bands | 7 |
| [`fdars.covariance`](#covariance) | Kernel covariance functions for Gaussian processes over functions | 14 |
| [`fdars.datasets`](#datasets) | Built-in datasets — Canadian weather, Tecator, phoneme, growth, and more | 7 |
| [`fdars.density_fda`](#density_fda) | Density-based functional data analysis and Wasserstein distances | 5 |
| [`fdars.depth`](#depth) | Functional depth measures — Fraiman-Muniz, band, modal, random-projection | 18 |
| [`fdars.explain`](#explain) | Functional explainability — SHAP, FCI, GRAD-CAM, and attribution maps | 46 |
| [`fdars.famm`](#famm) | Functional additive mixed models (FAMM) for longitudinal data | 3 |
| [`fdars.fdata`](#fdata) | Core functional data operations — mean, deriv, norm, integrate, reconstruct | 15 |
| [`fdars.frechet`](#frechet) | Fréchet regression for metric-space responses | 4 |
| [`fdars.fts`](#fts) | Functional time series — forecasting, correlation, spectral analysis | 13 |
| [`fdars.inference`](#inference) | Functional inference — two-sample tests, interval-wise testing | 11 |
| [`fdars.metric`](#metric) | Functional distance and similarity metrics — L2, L1, Mahalanobis, DTW | 26 |
| [`fdars.metrics`](#metrics) | Regression and classification scoring metrics for functional outputs | 5 |
| [`fdars.multi_fdata`](#multi_fdata) | Multi-domain functional data — paired domains, joint analysis | 2 |
| [`fdars.outliers`](#outliers) | Functional outlier detection — depth-based, magnitude, shape outliers | 8 |
| [`fdars.pace_fpca`](#pace_fpca) | PACE: Principal Analysis by Conditional Expectation for sparse data | 3 |
| [`fdars.regression`](#regression) | Functional regression — scalar-on-function, function-on-scalar, GLM | 29 |
| [`fdars.represent`](#represent) | Dimensionality reduction and functional representation tools | 4 |
| [`fdars.scalar_on_function`](#scalar_on_function) | Scalar-on-function regression with regularisation | 5 |
| [`fdars.scoring`](#scoring) | Functional scoring — penalised, tolerance-band, and integrated scores | 5 |
| [`fdars.seasonal`](#seasonal) | Seasonal functional decomposition and periodic pattern analysis | 18 |
| [`fdars.shapelet`](#shapelet) | Functional shapelets — pattern-based classification and feature learning | 7 |
| [`fdars.simulation`](#simulation) | Simulation of functional data — GPs, Brownian motion, Ornstein-Uhlenbeck | 8 |
| [`fdars.smoothing`](#smoothing) | Functional smoothing — kernel, basis, and roughness-penalised methods | 10 |
| [`fdars.spm`](#spm) | Statistical process monitoring — T2, SPE, control charts | 23 |
| [`fdars.tolerance`](#tolerance) | Functional tolerance bands — simultaneous and pointwise coverage | 9 |

## Module Details

### `fdars.alignment` {#alignment}

Elastic alignment, SRSF registration, Karcher mean, elastic FPCA.

[Reference docs](https://sipemu.github.io/pyfda/reference/alignment/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `align_to_target` | `(data, target, argvals, lambda_=0.0)` | Align all curves to a single target curve. |
| `alignment_quality` | `(data, argvals, lambda_=0.0, max_iter=20, tol=0.0001)` | Comprehensive alignment quality metrics. |
| `amplitude_distance` | `(curve1, curve2, argvals, lambda_=0.0)` | Amplitude distance between two curves. |
| `amplitude_self_distance_matrix` | `(data, argvals, lambda_=0.0)` | Amplitude self distance matrix (same as elastic self distance matrix). |
| `bayesian_align_pair` | `(f1, f2, argvals, n_samples=1000, burn_in=200, step_size=0.1, proposal_variance=1.0, seed=42)` | Bayesian pairwise alignment via pCN MCMC on the Hilbert sphere. |
| `compose_warps` | `(warp1, warp2, argvals)` | Compose two warping functions. |
| `curve_geodesic` | `(f1, f2, argvals, n_points=10, lambda_=0.0)` | Compute the geodesic path between two 1-D curves in the elastic metric. |
| `detect_landmarks` | `(curve, argvals, kind='peak', min_prominence=0.0)` | Detect landmarks (peaks, valleys, zero-crossings, inflections) in a curve. |
| `diagnose_alignment` | `(data, argvals, lambda_=0.0, max_iter=20, tol=0.0001, over_alignment_threshold=1.0, under_alignment_threshold=1e-06, max_bending_energy=100.0, min_improvement_ratio=0.5)` | Diagnose alignment quality for every curve after Karcher mean computation. |
| `elastic_align_pair` | `(curve1, curve2, argvals, lambda_=0.0)` | Pairwise elastic alignment of two curves. |
| `elastic_align_pair_closed` | `(f1, f2, argvals, lambda_=0.0)` | Align closed (periodic) curve f2 to f1 with rotation search. |
| `elastic_align_pair_constrained` | `(f1, f2, argvals, landmark_targets, landmark_sources, lambda_=0.0)` | Landmark-constrained elastic alignment. |
| `elastic_align_pair_multires` | `(f1, f2, argvals, coarsen_factor=4, n_refine_steps=10, step_size=0.01, lambda_=0.0)` | Multi-resolution elastic alignment (coarse DP + gradient refinement). |
| `elastic_align_pair_penalized` | `(curve1, curve2, argvals, lambda_=0.0, penalty_type='first_order', second_order_weight=0.1)` | Elastic alignment with configurable penalty type. |
| `elastic_changepoint` | `(data, argvals, kind='amplitude', lam=0.0, max_iter=30, n_mc=200, seed=42, ncomp=5, pca_method='joint')` | Detect a distributional changepoint in a sequence of curves (elastic). |
| `elastic_cross_distance_matrix` | `(data1, data2, argvals, lambda_=0.0)` | Elastic cross distance matrix. |
| `elastic_cross_distance_matrix_with_band` | `(data1, data2, argvals, lambda_=0.0, band_frac=None)` | Elastic cross-distance matrix with optional Sakoe–Chiba band. |
| `elastic_decomposition` | `(f1, f2, argvals, lambda_=0.0)` | Elastic phase-amplitude decomposition of two curves. |
| `elastic_depth` | `(data, argvals, lambda_=0.0)` | Elastic depth (depth under elastic metric). |
| `elastic_distance` | `(curve1, curve2, argvals, lambda_=0.0)` | Elastic (Fisher-Rao) distance between two curves. |
| `elastic_distance_closed` | `(f1, f2, argvals, lambda_=0.0)` | Elastic distance between two closed curves. |
| `elastic_logistic` | `(data, argvals, labels, ncomp_beta=10, lambda_=0.0, max_iter=20, tol=0.0001)` | Elastic logistic regression. |
| `elastic_outlier_detection` | `(data, argvals, lambda_=0.0, alpha=0.05, use_median=True)` | Elastic outlier detection using distances and Tukey fence. |
| `elastic_partial_match` | `(template, target, argvals_template, argvals_target, lambda_=0.0, min_span=0.5)` | Elastic partial matching: find best-aligned subcurve of a longer curve. |
| `elastic_regression` | `(data, argvals, response, ncomp_beta=10, lambda_=0.0, max_iter=20, tol=0.0001)` | Elastic scalar-on-function regression. |
| `elastic_self_distance_matrix` | `(data, argvals, lambda_=0.0)` | Elastic self distance matrix. |
| `elastic_self_distance_matrix_with_band` | `(data, argvals, lambda_=0.0, band_frac=None)` | Elastic self-distance matrix with optional Sakoe–Chiba band. |
| `gauss_model` | `(data, argvals, ncomp=3, n_samples=100, lambda_=0.0, max_iter=20, tol=0.0001, seed=42)` | Generate random curves from a fitted Gaussian model on aligned data. |
| `hierarchical_cut` | `(dist_mat, k=2, linkage='single')` | Hierarchical clustering then cut to produce k clusters (convenience function). |
| `hierarchical_from_distances` | `(dist_mat, linkage='single')` | Hierarchical agglomerative clustering from a precomputed distance matrix. |
| `horiz_fpca` | `(data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=0.0001)` | Horizontal (phase) FPCA. |
| `horiz_fpns` | `(data, argvals, ncomp=3, lambda_=0.0, max_iter=20, tol=0.0001)` | Horizontal Functional Principal Nested Spheres (FPNS) analysis. |
| `invert_warp` | `(warp, argvals)` | Invert a warping function. |
| `joint_fpca` | `(data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=0.0001)` | Joint (amplitude + phase) FPCA. |
| `joint_gauss_model` | `(data, argvals, ncomp=3, n_samples=100, balance_c=1.0, lambda_=0.0, max_iter=20, tol=0.0001, seed=42)` | Generate random curves from a joint Gaussian model preserving amplitude-phase correlation. |
| `karcher_mean` | `(data, argvals, lambda_=0.0, max_iter=20, tol=0.0001)` | Karcher (Frechet) mean under the elastic metric. |
| `karcher_mean_closed` | `(data, argvals, max_iter=20, tol=0.0001, lambda_=0.0)` | Karcher mean for closed (periodic) curves. |
| `karcher_mean_with_band` | `(data, argvals, lambda_=0.0, max_iter=20, tol=0.0001, band_frac=None)` | Karcher (Fréchet) mean under the elastic metric with optional Sakoe–Chiba band. |
| `karcher_median` | `(data, argvals, lambda_=0.0, max_iter=20, tol=0.001)` | Karcher median under the elastic metric. |
| `kmedoids_from_distances` | `(dist_mat, k=2, max_iter=100, seed=42)` | K-medoids clustering from a precomputed distance matrix. |
| `lambda_cv` | `(data, argvals, lambdas=None, n_folds=5, max_iter=15, tol=0.001, seed=42)` | Cross-validation for the elastic alignment regularisation parameter lambda. |
| `landmark_detect_and_register` | `(data, argvals, kind='peak', min_prominence=0.0, expected_count=0)` | Detect landmarks and register in one call. |
| `landmark_register` | `(data, argvals, landmarks, target=None)` | Register curves to common landmark positions. |
| `least_squares_score` | `(registered, argvals)` | Least-squares registration score: mean Simpson-weighted L2 spread of the |
| `least_squares_shift_registration` | `(data, argvals, max_shift)` | Register curves by a per-curve rigid horizontal shift (least-squares). |
| `pairwise_consistency` | `(data, argvals, lambda_=0.0, max_triplets=0)` | Pairwise alignment consistency via triplet checks. |
| `pairwise_correlation_score` | `(registered, argvals)` | Pairwise correlation registration score: mean functional Pearson correlation |
| `peak_persistence` | `(data, argvals, lambdas, max_iter=10, tol=0.001)` | Peak persistence diagram for choosing the alignment regularisation parameter. |
| `phase_boxplot` | `(gammas, argvals, factor=1.5)` | Phase (warping) box plot for functional data. |
| `phase_distance` | `(curve1, curve2, argvals, lambda_=0.0)` | Phase distance between two curves. |
| `phase_self_distance_matrix` | `(data, argvals, lambda_=0.0)` | Phase self distance matrix. |
| `reparameterize_curve` | `(curve, argvals, gamma)` | Apply a warping function to a curve (reparameterize). |
| `robust_karcher_mean` | `(data, argvals, lambda_=0.0, max_iter=20, tol=0.001, trim_fraction=0.1)` | Robust Karcher mean (trimmed). |
| `shape_confidence_interval` | `(data, argvals, n_bootstrap=200, confidence_level=0.95, lambda_=0.0, max_iter=15, tol=0.001, seed=42)` | Bootstrap confidence intervals for the elastic Karcher mean. |
| `shape_distance` | `(curve1, curve2, argvals, lambda_=0.0)` | Shape distance (quotient space distance). |
| `shape_mean` | `(data, argvals, quotient='reparameterization', lambda_=0.0, max_iter=20, tol=0.0001)` | Shape mean of a set of curves. |
| `shape_self_distance_matrix` | `(data, argvals, quotient='reparameterization', lambda_=0.0)` | Pairwise shape distance matrix. |
| `sobolev_least_squares_score` | `(registered, argvals, lambda_=0.0)` | Sobolev least-squares registration score: LS spread plus a derivative-penalty |
| `srsf_inverse` | `(srsf, argvals, initial_value=0.0)` | Inverse SRSF transform. |
| `srsf_transform` | `(curve, argvals)` | SRSF (Square Root Slope Function) transform. |
| `transfer_alignment` | `(source_data, target_data, argvals, lambda_=0.0, max_iter=15, tol=0.001)` | Align curves from a target population to a source population's coordinate system. |
| `tsrvf_transform` | `(data, argvals, max_iter=20, tol=0.0001, lambda_=0.0)` | TSRVF (Transported SRSF) transform. |
| `tsrvf_transform_with_method` | `(data, argvals, max_iter=20, tol=0.0001, lambda_=0.0, method='log_map')` | TSRVF transform with configurable transport method. |
| `vert_fpca` | `(data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=0.0001)` | Vertical (amplitude) FPCA on aligned data. |
| `warp_complexity` | `(warp, argvals)` | Warp complexity (geodesic distance from identity). |
| `warp_inverse_error` | `(warp, argvals)` | Compute the L2 error of a warp inverse: &#124;&#124;gamma(gamma_inv(t)) - t&#124;&#124;. |
| `warp_smoothness` | `(warp, argvals)` | Warp smoothness (bending energy). |
| `warp_statistics` | `(gammas, argvals, confidence_level=0.95)` | Warp statistics: mean, variance, confidence bands, Karcher mean warp. |

### `fdars.basis` {#basis}

Basis representations — B-spline, Fourier, functional PCA.

[Reference docs](https://sipemu.github.io/pyfda/reference/basis/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `basis_nbasis_cv` | `(data, argvals, nbasis_min=4, nbasis_max=20, basis_type='bspline', criterion='gcv', n_folds=5, lambda_=0.0)` | Cross-validated selection of number of basis functions. |
| `basis_to_fdata_1d` | `(coefficients, argvals, n_basis, basis_type='bspline')` | Reconstruct functional data from basis coefficients. |
| `bspline_basis` | `(argvals, nknots, order=4)` | Evaluate a B-spline basis at given points. |
| `bspline_basis_from_knots` | `(argvals, knots, order=4)` | Evaluate a B-spline basis from a given knot vector. |
| `constant_basis` | `(argvals)` | Evaluate the constant (intercept) basis on a grid of evaluation points. |
| `construct_bspline_knots` | `(t_min, t_max, nknots, order=4)` | Construct B-spline knot vector. |
| `fdata_to_basis_1d` | `(data, argvals, n_basis, basis_type='bspline')` | Project functional data onto a B-spline or Fourier basis. |
| `fourier_basis` | `(argvals, n_basis)` | Evaluate a Fourier basis at given points. |
| `fourier_basis_with_period` | `(argvals, n_basis, period)` | Evaluate a Fourier basis with specified period at given points. |
| `fourier_fit_1d` | `(data, argvals, nbasis)` | Fit Fourier basis to functional data using least squares. |
| `pspline_fit_1d` | `(data, argvals, n_basis, lambda_, order=2)` | Fit P-splines to 1D functional data. |
| `pspline_fit_gcv` | `(data, argvals, n_basis, order=2)` | P-spline fit with GCV-selected smoothing parameter. |
| `select_basis_auto_1d` | `(data, argvals, criterion='gcv', nbasis_min=0, nbasis_max=0, lambda_pspline=Ellipsis, use_seasonal_hint=True)` | Automatic basis selection (GCV/AIC/BIC) for 1D data. |
| `select_fourier_nbasis_gcv` | `(data, argvals, min_nbasis, max_nbasis)` | Select optimal number of Fourier basis functions via GCV. |
| `smooth_basis_aic` | `(data, argvals, n_basis, basis_type='bspline', lfd_order=2, log_lambda_min=Ellipsis, log_lambda_max=4.0, n_grid=25)` | Smooth functional data using basis expansion with AIC-optimal lambda. |
| `smooth_basis_gcv` | `(data, argvals, n_basis, basis_type='bspline', lfd_order=2, log_lambda_min=Ellipsis, log_lambda_max=4.0, n_grid=25)` | Smooth functional data using basis expansion with GCV. |

### `fdars.classification` {#classification}

Functional classifiers — k-nearest neighbours, SVM, centroid-based.

[Reference docs](https://sipemu.github.io/pyfda/reference/classification/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `elastic_multinomial` | `(data, labels, argvals, ncomp_beta=10, lambda_=0.1, max_iter=100, tol=0.0001)` | K-class elastic multinomial classifier for functional data (one-vs-rest). |
| `fclassif_cv` | `(data, argvals, labels, method='lda', ncomp=3, nfold=5)` | Cross-validated classification. |
| `fclassif_dd` | `(data, labels)` | Depth-based DD-classifier for functional data. |
| `fclassif_kernel` | `(data, argvals, labels, h_func=1.0, h_scalar=1.0)` | Kernel classification for functional data. |
| `fclassif_knn` | `(data, labels, ncomp=3, k=5)` | k-NN classification for functional data. |
| `fclassif_lda` | `(data, labels, ncomp=3)` | LDA classification for functional data via FPC scores. |
| `fclassif_qda` | `(data, labels, ncomp=3)` | QDA classification for functional data. |
| `kernel_classify_from_distances` | `(func_dists, labels, h_func=1.0, h_scalar=1.0)` | Kernel classification from a precomputed functional distance matrix. |
| `knn_classify_from_distances` | `(dist_matrix, labels, k=5)` | k-NN classification from a precomputed distance matrix. |

### `fdars.clustering` {#clustering}

Functional k-means, fuzzy, GMM, and elastic clustering.

[Reference docs](https://sipemu.github.io/pyfda/reference/clustering/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `align_cluster_fd` | `(data, argvals, k=2, max_iter=20, seed=42, use_amplitude_only=True, elastic_lambda=0.0, karcher_max_iter=15, karcher_tol=0.0001)` | Elastic-alignment functional clustering. |
| `calinski_harabasz` | `(dist_matrix, labels)` | Calinski-Harabasz index for cluster quality (from distance matrix). |
| `calinski_harabasz_data` | `(data, argvals, labels)` | Calinski-Harabasz index for cluster quality (from data and argvals). |
| `dbscan_fd` | `(data, argvals, eps=0.5, min_points=3)` | Density-based spatial clustering of functional data (DBSCAN). |
| `funfem_cluster` | `(data, argvals, k=2, ncomp=10, p_disc=0, max_iter=50, tol=1e-06, seed=42)` | Fisher-EM discriminative functional clustering (FunFEM). |
| `fuzzy_cmeans_fd` | `(data, argvals, k, fuzziness=2.0, max_iter=100, tol=1e-06, seed=42)` | Fuzzy C-means clustering for functional data. |
| `gmm_cluster` | `(data, argvals, k_range, nbasis=5, max_iter=200, tol=1e-06, seed=42)` | GMM clustering for functional data (via basis projection). |
| `kcfc_cluster` | `(data, argvals, k=2, ncomp=3, max_iter=50, seed=42)` | K-means with per-cluster FPCA (KCFC) clustering for functional data. |
| `kmeans_fd` | `(data, argvals, k, max_iter=100, tol=1e-06, seed=42)` | K-means clustering for functional data. |
| `silhouette_score` | `(dist_matrix, labels)` | Silhouette score for cluster quality assessment (from distance matrix). |
| `silhouette_score_data` | `(data, argvals, labels)` | Silhouette score for cluster quality assessment (from data and argvals). |

### `fdars.conformal` {#conformal}

Conformal prediction and classification bands.

[Reference docs](https://sipemu.github.io/pyfda/reference/conformal/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `conformal_classif` | `(data, labels, test_data, ncomp=3, classifier='lda', cal_fraction=0.25, alpha=0.1, seed=42)` | Conformal classification prediction sets. |
| `conformal_elastic_logistic` | `(data, labels, test_data, argvals, lambda=0.0, cal_fraction=0.25, alpha=0.1, seed=42)` | Conformal elastic logistic regression prediction sets. |
| `conformal_elastic_pcr` | `(data, response, test_data, argvals, ncomp=3, pca_method="vertical", lambda=0.0, cal_fraction=0.25, alpha=0.1, seed=42)` | Conformal elastic PCR prediction intervals. |
| `conformal_elastic_regression` | `(data, response, test_data, argvals, ncomp_beta=3, lambda=0.0, cal_fraction=0.25, alpha=0.1, seed=42)` | Conformal elastic regression prediction intervals. |
| `conformal_fregre_lm` | `(data, response, test_data, ncomp=3, cal_fraction=0.25, alpha=0.1, seed=42)` | Conformal regression prediction intervals. |
| `conformal_fregre_np` | `(data, response, test_data, argvals, cal_fraction=0.25, alpha=0.1, h_func=1.0, h_scalar=1.0, seed=42)` | Conformal nonparametric regression. |
| `conformal_logistic` | `(data, response, test_data, ncomp=3, max_iter=100, tol=1e-06, cal_fraction=0.25, alpha=0.1, seed=42)` | Conformal logistic regression prediction sets. |

### `fdars.covariance` {#covariance}

Kernel covariance functions for Gaussian processes over functions.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `kernel_add` | `(k1, k2)` | Sum of two kernels. |
| `kernel_brownian` | `(variance: 'float' = 1.0)` | Brownian-motion (Wiener) kernel: ``variance * min(s, t)``. |
| `kernel_exponential` | `(lengthscale: 'float' = 1.0, variance: 'float' = 1.0)` | Exponential kernel (Matern nu=1/2): ``variance * exp(-&#124;s-t&#124; / l)``. |
| `kernel_gaussian` | `(lengthscale: 'float' = 1.0, variance: 'float' = 1.0)` | Squared-exponential (RBF) kernel: ``variance * exp(-(s-t)^2 / (2 l^2))``. |
| `kernel_linear` | `(variance: 'float' = 1.0, center: 'float' = 0.0)` | Linear kernel: ``variance * (s-c) * (t-c)``. |
| `kernel_matern` | `(lengthscale: 'float' = 1.0, nu: 'float' = 1.5, variance: 'float' = 1.0)` | Matern kernel for ``nu`` in {0.5, 1.5, 2.5} (closed forms). |
| `kernel_mult` | `(k1, k2)` | Product of two kernels. |
| `kernel_periodic` | `(lengthscale: 'float' = 1.0, period: 'float' = 1.0, variance: 'float' = 1.0)` | Periodic kernel: ``variance * exp(-2 sin^2(pi&#124;s-t&#124;/p) / l^2)``. |
| `kernel_polynomial` | `(degree: 'int' = 2, variance: 'float' = 1.0, offset: 'float' = 1.0)` | Polynomial kernel: ``variance * (s*t + offset)^degree``. |
| `kernel_whitenoise` | `(variance: 'float' = 1.0)` | White-noise kernel: ``variance`` on the diagonal (s == t), else 0. |
| `make_gaussian_process` | `(argvals, kernel, n: 'int' = 1, mean=0.0, jitter: 'float' = 1e-08, seed: 'int &#124; None' = None)` | Sample ``n`` Gaussian-process curves from ``kernel`` on ``argvals``. |
| `r_bridge` | `(n: 'int' = 1, argvals=None, n_points: 'int &#124; None' = None, sigma: 'float' = 1.0, seed: 'int &#124; None' = None)` | Sample ``n`` Brownian-bridge paths B(t) - (t/T) B(T) (R ``r.bridge``). |
| `r_brownian` | `(n: 'int' = 1, argvals=None, n_points: 'int &#124; None' = None, sigma: 'float' = 1.0, seed: 'int &#124; None' = None)` | Sample ``n`` standard Brownian-motion paths (R ``r.brownian``). |
| `r_ou` | `(n: 'int' = 1, argvals=None, n_points: 'int &#124; None' = None, theta: 'float' = 1.0, mu: 'float' = 0.0, sigma: 'float' = 1.0, x0: 'float &#124; None' = None, seed: 'int &#124; None' = None)` | Sample ``n`` Ornstein-Uhlenbeck paths (R ``r.ou``). |

### `fdars.datasets` {#datasets}

Built-in datasets — Canadian weather, Tecator, phoneme, growth, and more.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `Dataset` | `(data: 'Fdata', argvals: 'Any', y: 'Optional[np.ndarray]', meta: 'Any', name: 'str' = '', description: 'str' = '', _extras: 'Dict[str, Any]' = <factory>) -> None` | Container for a loaded example dataset. |
| `load_canadian_weather` | `(variable: 'str' = 'temperature', return_fdata: 'bool' = True)` | Canadian Weather: daily curves for 35 stations over a 365-day year. |
| `load_growth` | `(return_fdata: 'bool' = True)` | Berkeley Growth Study: heights (cm) of 39 boys & 54 girls at 31 ages. |
| `load_phoneme` | `(return_fdata: 'bool' = True)` | Phoneme: log-periodograms (256 freqs) for 5 phoneme classes. |
| `load_sonar` | `(return_fdata: 'bool' = True)` | Sonar (UCI): 60-band sonar return energies for 208 objects. |
| `load_tecator` | `(return_fdata: 'bool' = True)` | Tecator: 100-channel NIR absorbance spectra of 240 meat samples. |
| `load_wine` | `(return_fdata: 'bool' = True)` | Wine (UCI): 13 chemical measurements for 178 wines of 3 cultivars. |

### `fdars.density_fda` {#density_fda}

Density-based functional data analysis and Wasserstein distances.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `inverse_lqd` | `(psi, t_grid, target_argvals)` | Compute the inverse LQD transform: reconstruct a density from its LQD representation. |
| `lqd_fpca` | `(density_matrix, argvals, ncomp=3, n_quantile_pts=None)` | Functional PCA of densities via the LQD transform. |
| `lqd_transform` | `(density, argvals, n_quantile_pts=None)` | Compute the log-quantile density (LQD) transform of a density function. |
| `normalize_density` | `(vals, argvals)` | Normalize a density function to integrate to 1. |
| `wasserstein_barycenter` | `(density_matrix, argvals, weights=None)` | Compute the Wasserstein Fréchet mean (barycenter) of a collection of densities. |

### `fdars.depth` {#depth}

Functional depth measures — Fraiman-Muniz, band, modal, random-projection.

[Reference docs](https://sipemu.github.io/pyfda/reference/depth/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `band_1d` | `(data, ref_data)` | Band depth for 1D functional data. |
| `fraiman_muniz_1d` | `(data, ref_data, scale=True)` | Fraiman-Muniz depth for 1D functional data. |
| `fraiman_muniz_2d` | `(data, ref_data, scale=True)` | Fraiman-Muniz depth for 2D functional data. |
| `functional_boxplot` | `(data, method='modified_band', factor=1.5, scale=True, nproj=50, seed=None)` | Canonical López-Pintado–Romo depth-fence functional boxplot (numeric only). |
| `functional_depth` | `(data, method='fraiman_muniz', scale=True, nproj=50, seed=None)` | Unified self-depth dispatcher for functional data. |
| `functional_spatial_1d` | `(data, ref_data, argvals=None)` | Functional spatial depth for 1D data. |
| `functional_spatial_2d` | `(data, ref_data)` | Functional spatial depth for 2D data. |
| `kernel_functional_spatial_1d` | `(data, ref_data, argvals, h=1.0)` | Kernel functional spatial depth for 1D data. |
| `kernel_functional_spatial_2d` | `(data, ref_data, h=1.0)` | Kernel functional spatial depth for 2D data. |
| `modal_1d` | `(data, ref_data, h=1.0)` | Modal depth for 1D functional data. |
| `modal_2d` | `(data, ref_data, h=1.0)` | Modal depth for 2D functional data. |
| `modified_band_1d` | `(data, ref_data)` | Modified band depth for 1D functional data. |
| `modified_epigraph_index_1d` | `(data, ref_data)` | Modified epigraph index for 1D functional data. |
| `random_projection_1d` | `(data, ref_data, n_proj=50)` | Random projection depth for 1D functional data. |
| `random_projection_2d` | `(data, ref_data, n_proj=50)` | Random projection depth for 2D functional data. |
| `random_projection_deriv_1d` | `(data, ref_data, argvals=None, n_proj=50, n_deriv=1, seed=None)` | Random-projection depth using curves and their derivatives (RPD). |
| `random_tukey_1d` | `(data, ref_data, n_proj=50)` | Random Tukey depth for 1D functional data. |
| `random_tukey_2d` | `(data, ref_data, n_proj=50)` | Random Tukey depth for 2D functional data. |

### `fdars.explain` {#explain}

Functional explainability — SHAP, FCI, GRAD-CAM, and attribution maps.

[Reference docs](https://sipemu.github.io/pyfda/reference/explain/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `anchor_explanation` | `(data, response, ncomp=3, observation=0, precision_threshold=0.95, n_bins=4)` | Anchor explanation (linear model). |
| `anchor_explanation_logistic` | `(data, labels, ncomp=3, observation=0, precision_threshold=0.95, n_bins=4)` | Anchor explanation (logistic model). |
| `andrews_loadings` | `(rotation, n_grid=100)` | Andrews-curve loadings for a rotation/loading matrix. |
| `andrews_transform` | `(data, n_grid=100)` | Andrews-curve transform of functional/multivariate data. |
| `beta_decomposition` | `(data, response, ncomp=3)` | Beta function decomposition. |
| `beta_decomposition_logistic` | `(data, labels, ncomp=3)` | Beta decomposition for a logistic regression model. |
| `calibration_diagnostics` | `(data, labels, ncomp=3, n_groups=10)` | Calibration diagnostics for a logistic model. |
| `conditional_permutation_importance` | `(data, response, ncomp=3, n_bins=5, n_perm=10, seed=42)` | Conditional permutation importance for a linear regression model. |
| `conditional_permutation_importance_logistic` | `(data, labels, ncomp=3, n_bins=5, n_perm=10, seed=42)` | Conditional permutation importance for a logistic regression model. |
| `conformal_prediction_residuals` | `(data, response, test_data, ncomp=3, cal_fraction=0.25, alpha=0.1, seed=42)` | Split-conformal prediction intervals. |
| `counterfactual_logistic` | `(data, labels, ncomp=3, observation=0, max_iter=100, step_size=0.1)` | Counterfactual explanation (logistic model, gradient descent). |
| `counterfactual_regression` | `(data, response, ncomp=3, observation=0, target_value=0.0)` | Counterfactual explanation (linear regression). |
| `dfbetas_dffits` | `(data, response, ncomp=3)` | DFBETAS and DFFITS diagnostics. |
| `domain_selection` | `(data, response, ncomp=3, window_width=5, threshold=0.0)` | Domain selection / interval importance (linear model). |
| `domain_selection_logistic` | `(data, labels, ncomp=3, window_width=5, threshold=0.0)` | Domain selection / interval importance (logistic model). |
| `expected_calibration_error` | `(data, labels, ncomp=3, n_bins=10)` | Expected calibration error (ECE, MCE, ACE). |
| `explanation_stability` | `(data, response, ncomp=3, n_boot=100, seed=42)` | Bootstrap stability analysis (linear model). |
| `explanation_stability_logistic` | `(data, labels, ncomp=3, n_boot=100, seed=42)` | Bootstrap stability analysis (logistic model). |
| `fpc_ale` | `(data, response, ncomp=3, component=0, n_bins=10)` | ALE plot for an FPC component (linear model). |
| `fpc_ale_logistic` | `(data, labels, ncomp=3, component=0, n_bins=10)` | ALE plot for an FPC component (logistic model). |
| `fpc_permutation_importance` | `(data, response, ncomp=3, n_perm=10, seed=42)` | FPC-based permutation importance. |
| `fpc_permutation_importance_logistic` | `(data, labels, ncomp=3, n_perm=10, seed=42)` | FPC permutation importance for a logistic model. |
| `fpc_shap_values` | `(data, response, ncomp=3)` | FPC SHAP values. |
| `fpc_shap_values_logistic` | `(data, labels, ncomp=3, n_samples=100, seed=42)` | Kernel SHAP values for a logistic model. |
| `fpc_vif` | `(data, response, ncomp=3)` | Variance inflation factors for FPC scores. |
| `fpc_vif_logistic` | `(data, labels, ncomp=3)` | Variance inflation factors for a logistic model. |
| `friedman_h_statistic` | `(data, response, ncomp=3, component_j=0, component_k=1, n_grid=20)` | Friedman H-statistic for interaction between two FPC components (linear model). |
| `friedman_h_statistic_logistic` | `(data, labels, ncomp=3, component_j=0, component_k=1, n_grid=20)` | Friedman H-statistic for a logistic model. |
| `functional_pdp` | `(data, response, ncomp=3, component=0, n_grid=50)` | Functional partial dependence plot. |
| `functional_pdp_logistic` | `(data, labels, ncomp=3, component=0, n_grid=50)` | Functional PDP/ICE for a logistic regression model. |
| `functional_saliency` | `(data, response, ncomp=3)` | Functional saliency maps (linear model). |
| `functional_saliency_logistic` | `(data, labels, ncomp=3)` | Functional saliency maps (logistic model, gradient-based). |
| `influence_diagnostics` | `(data, response, ncomp=3)` | Influence diagnostics (Cook's distance, leverage). |
| `lime_explanation` | `(data, response, ncomp=3, observation=0, n_samples=100, kernel_width=1.0, seed=42)` | LIME explanation for a linear regression model. |
| `lime_explanation_logistic` | `(data, labels, ncomp=3, observation=0, n_samples=100, kernel_width=1.0, seed=42)` | LIME explanation for a logistic regression model. |
| `loo_cv_press` | `(data, response, ncomp=3)` | LOO-CV / PRESS diagnostics. |
| `pointwise_importance` | `(data, response, ncomp=3)` | Pointwise variable importance for a linear regression model. |
| `pointwise_importance_logistic` | `(data, labels, ncomp=3)` | Pointwise variable importance for a logistic regression model. |
| `prediction_intervals` | `(data, response, new_data, ncomp=3, confidence_level=0.95)` | Prediction intervals for new observations. |
| `prototype_criticism` | `(data, ncomp=3, n_prototypes=5, n_criticisms=5)` | Prototype/criticism selection (MMD-based). |
| `regression_depth` | `(data, response, ncomp=3, n_boot=100, depth_type='fraiman_muniz', seed=42)` | Regression depth diagnostics (linear model). |
| `regression_depth_logistic` | `(data, labels, ncomp=3, n_boot=100, depth_type='fraiman_muniz', seed=42)` | Regression depth diagnostics (logistic model). |
| `significant_regions` | `(lower, upper)` | Significant regions of the beta function. |
| `significant_regions_from_se` | `(beta_t, beta_se, z_alpha=1.96)` | Significant regions from beta(t) and its standard error. |
| `sobol_indices` | `(data, response, ncomp=3)` | Sobol sensitivity indices (linear model). |
| `sobol_indices_logistic` | `(data, labels, ncomp=3, n_samples=1000, seed=42)` | Sobol sensitivity indices (logistic model, Saltelli MC). |

### `fdars.famm` {#famm}

Functional additive mixed models (FAMM) for longitudinal data.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `dense_flmm` | `(data, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10)` | Fit a Functional Linear Mixed Model (FLMM) via REML-EM. |
| `fast_fmm` | `(data, subject_ids, covariates=None, smooth_window=3, max_iter=30, tol=1e-08, compute_inference=True)` | Fit a fast Functional Mixed Model (FMM) with optional Wald inference. |
| `multi_famm` | `(data_list, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10)` | Fit a multi-variable Functional Additive Mixed Model (multiFAMM). |

### `fdars.fdata` {#fdata}

Core functional data operations — mean, deriv, norm, integrate, reconstruct.

[Reference docs](https://sipemu.github.io/pyfda/reference/fdata/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `center_1d` | `(data)` | Center functional data by subtracting the pointwise mean. |
| `depth_based_median` | `(data)` | Return the depth-based median curve of 1D functional data. |
| `deriv_1d` | `(data, argvals, nderiv=1)` | Compute numerical derivatives of 1D functional data. |
| `deriv_2d` | `(data, argvals_s, argvals_t)` | Compute numerical derivatives of 2D functional data. |
| `functional_covariance` | `(data)` | Compute the Bessel-corrected m×m covariance surface of 1D functional data. |
| `functional_std` | `(data)` | Compute the Bessel-corrected pointwise standard deviation of 1D functional data. |
| `functional_variance` | `(data)` | Compute the Bessel-corrected pointwise variance of 1D functional data. |
| `geometric_median_1d` | `(data, argvals, max_iter=100, tol=1e-08)` | Compute the geometric (L1) median of 1D functional data. |
| `geometric_median_2d` | `(data, argvals_s, argvals_t, max_iter=100, tol=1e-08)` | Compute the geometric (L1) median of 2D functional data. |
| `mean_1d` | `(data)` | Compute the pointwise mean of 1D functional data. |
| `mean_2d` | `(data)` | Compute the pointwise mean of 2D functional data. |
| `norm_lp_1d` | `(data, argvals, p=2.0)` | Compute Lp norms of 1D functional data. |
| `normalize` | `(data, method='center')` | Normalize functional data. |
| `normalize_with_argvals` | `(data, argvals, method='center', p=2.0)` | Normalize functional data (with argvals for Lp normalization). |
| `trim_mean` | `(data, alpha=0.0)` | Compute the depth-trimmed mean of 1D functional data. |

### `fdars.frechet` {#frechet}

Fréchet regression for metric-space responses.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `frechet_anova` | `(responses, argvals, group_labels, n_perm=999, seed=42)` | Fréchet ANOVA: test equality of Fréchet means across groups. |
| `frechet_global_reg` | `(predictors, responses, argvals, xout)` | Global Fréchet linear regression for density-response functional data. |
| `frechet_local_reg` | `(predictors, responses, argvals, xout, bandwidth)` | Local Fréchet regression for density-response functional data. |
| `frechet_mean` | `(objects, space, d, weights=None)` | Fréchet mean over a metric space, dispatched by space name. |

### `fdars.fts` {#fts}

Functional time series — forecasting, correlation, spectral analysis.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `dpca` | `(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)` | Fit Dynamic Functional Principal Components Analysis (DPCA). |
| `dpca_reconstruct` | `(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)` | Fit DPCA and reconstruct the functional time series from dynamic components. |
| `fplsr` | `(data, argvals, ncomp=3)` | Functional Partial Least Squares Regression (fPLSR) one-step-ahead forecast. |
| `ftsm` | `(data, argvals, ncomp=3)` | Fit a Functional Time Series Model (FTSM) via FPCA + Yule-Walker AR fitting. |
| `ftsm_forecast` | `(data, argvals, h=1, ncomp=3)` | Fit an FTSM and produce a single- or multi-horizon forecast (single-step variant). |
| `ftsm_forecast_multistep` | `(data, argvals, h=5, ncomp=3)` | Fit an FTSM and produce a multi-step forecast (iterative multi-step variant). |
| `ftsm_update` | `(data, new_curve, argvals, ncomp=3)` | Online update of an FTSM with one or more new curves. |
| `functional_acf` | `(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)` | Compute the functional autocorrelation function (ACF) with Monte Carlo bands. |
| `functional_difference` | `(data)` | Compute the first-order functional difference (lag-1 differencing). |
| `functional_pacf` | `(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)` | Compute the functional partial autocorrelation function (PACF) with Monte Carlo bands. |
| `long_run_covariance` | `(data, argvals, bandwidth=None)` | Estimate the long-run covariance operator of a functional time series. |
| `spectral_density` | `(data, argvals, bandwidth=None)` | Estimate the spectral density operator of a functional time series. |
| `stationarity_test` | `(data, argvals, n_perm=999, seed=42)` | Test stationarity of functional time series via permutation test. |

### `fdars.inference` {#inference}

Functional inference — two-sample tests, interval-wise testing.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `f_perm_test` | `(data_a, data_b, argvals, n_perm=999, seed=None)` | Functional two-sample permutation *F*-test. |
| `flm_f_test` | `(data, response, n_comp=5)` | Functional linear model overall-significance F-test. |
| `flm_gof_test` | `(data, response, n_comp=5)` | Functional linear model goodness-of-fit test (Ramsey-RESET style). |
| `itp_flm` | `(data, response, argvals, basis_type='bspline', nbasis=5, n_perm=999, seed=None)` | Interval-wise testing procedure for the functional linear model. |
| `itp_one_pop` | `(data, argvals, mu0=None, basis_type='bspline', nbasis=5, n_perm=999, seed=None)` | Interval-wise testing procedure for a single functional population. |
| `itp_two_pop` | `(data_a, data_b, argvals, basis_type='bspline', nbasis=5, n_perm=999, seed=None)` | Interval-wise testing procedure for two functional populations. |
| `mean_scb` | `(data, argvals, bandwidth, nb=200, confidence=0.95, multiplier='gaussian')` | Simultaneous confidence band for the mean function (Degras). |
| `oneway_anova_vstat` | `(data, groups, argvals)` | One-way functional ANOVA V-statistic (asymptotic scaled-χ² test). |
| `scb_two_sample_test` | `(data_a, data_b, argvals, bandwidth, nb=200, confidence=0.95, multiplier='gaussian')` | Two-sample mean-equality test via a simultaneous confidence band for the |
| `t_perm_test` | `(data_a, data_b, argvals, n_perm=999, seed=None)` | Functional two-sample permutation *t*-test. |
| `two_sample_mean_test` | `(data_a, data_b, argvals, ncomp=5)` | Functional two-sample mean-equality test via Hotelling-T² on a shared FPC |

### `fdars.metric` {#metric}

Functional distance and similarity metrics — L2, L1, Mahalanobis, DTW.

[Reference docs](https://sipemu.github.io/pyfda/reference/metric/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `PyGakGramTrain` | `(...)` | Opaque handle wrapping fdars-core GakGramTrain for incremental GAK Gram computation. |
| `dtw_cross_1d` | `(data1, data2, p=2.0, w=0)` | DTW cross distance for 1D data. |
| `dtw_self_1d` | `(data, p=2.0, w=0)` | DTW distance matrix (self) for 1D data. |
| `fourier_cross_1d` | `(data1, data2, n_basis=5)` | Fourier coefficient distance (cross). |
| `fourier_self_1d` | `(data, n_basis=5)` | Fourier coefficient distance (self) for 1D data. |
| `gak` | `(x, y, sigma)` | Global Alignment Kernel between two 1-D time series. |
| `gak_gram_matrix` | `(data, sigma=None)` | Global Alignment Kernel Gram matrix (one-shot, symmetric). |
| `gak_gram_predict` | `(train, new_data)` | Compute the GAK Gram matrix between new data and the training set. |
| `gak_gram_train` | `(data, sigma=None)` | Fit a GAK Gram handle for incremental train/predict computation. |
| `hausdorff_cross_1d` | `(data1, data2, argvals)` | Hausdorff cross distance for 1D data. |
| `hausdorff_cross_2d` | `(data1, data2, argvals_s, argvals_t)` | Hausdorff cross distance for 2D data. |
| `hausdorff_self_1d` | `(data, argvals)` | Hausdorff distance matrix (self) for 1D data. |
| `hausdorff_self_2d` | `(data, argvals_s, argvals_t)` | Hausdorff self distance for 2D data. |
| `hshift_cross_1d` | `(data1, data2, argvals, max_shift=0)` | Horizontal shift distance (cross). |
| `hshift_self_1d` | `(data, argvals, max_shift=0)` | Horizontal shift distance (self) for 1D data. |
| `inprod` | `(data1, data2, argvals=None)` | Inner product between two functional data sets (Simpson-integrated). |
| `int_simpson` | `(data, argvals=None)` | Simpson's-rule integral of each curve. |
| `lp_cross_1d` | `(data1, data2, argvals, p=2.0)` | Lp distance matrix (cross) between two 1D functional datasets. |
| `lp_cross_2d` | `(data1, data2, argvals_s, argvals_t, p=2.0)` | Lp cross distance for 2D data. |
| `lp_self_1d` | `(data, argvals, p=2.0)` | Lp distance matrix (self) for 1D functional data. |
| `lp_self_2d` | `(data, argvals_s, argvals_t, p=2.0)` | Lp distance matrix (self) for 2D functional data. |
| `sigma_gak` | `(data)` | Heuristic GAK bandwidth: median pairwise Euclidean distance, floored at 1e-8. |
| `soft_dtw_cross_1d` | `(data1, data2, gamma=1.0)` | Soft-DTW cross distance for 1D data. |
| `soft_dtw_div_cross_1d` | `(data1, data2, gamma=1.0)` | Soft-DTW divergence cross distance. |
| `soft_dtw_div_self_1d` | `(data, gamma=1.0)` | Soft-DTW divergence distance matrix (self) for 1D data. |
| `soft_dtw_self_1d` | `(data, gamma=1.0)` | Soft-DTW distance matrix (self) for 1D data. |

### `fdars.metrics` {#metrics}

Regression and classification scoring metrics for functional outputs.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `pred_mae` | `(y_true, y_pred) -> 'float'` | Mean absolute error (R ``pred.MAE``). |
| `pred_mse` | `(y_true, y_pred) -> 'float'` | Mean squared error (R ``pred.MSE``). |
| `pred_r2` | `(y_true, y_pred) -> 'float'` | Coefficient of determination R^2 (R ``pred.R2``). |
| `pred_rmse` | `(y_true, y_pred) -> 'float'` | Root mean squared error (R ``pred.RMSE``). |
| `prediction_metrics` | `(y_true, y_pred) -> 'dict'` | All four ``pred.*`` metrics as a dict (``mae``, ``mse``, ``rmse``, ``r2``). |

### `fdars.multi_fdata` {#multi_fdata}

Multi-domain functional data — paired domains, joint analysis.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `PyMultiFunData` | `(...)` | Opaque handle wrapping fdars-core MultiFunData for multi-domain functional data. |
| `multi_fdata_from_components` | `(data_list, argvals_list)` | Build a PyMultiFunData handle from lists of 2-D data arrays and 1-D argvals vectors. |

### `fdars.outliers` {#outliers}

Functional outlier detection — depth-based, magnitude, shape outliers.

[Reference docs](https://sipemu.github.io/pyfda/reference/outliers/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `depthgram` | `(data, outliergram_factor=1.5, boxplot_factor=1.5)` | Depthgram functional outlier detection. |
| `detect_outliers_lrt` | `(data, alpha=0.05, n_bootstrap=200, trim=0.1, smo=0.02)` | LRT-based outlier detection with bootstrap. |
| `detect_outliers_lrt_with_dist` | `(data, alpha=0.05, n_bootstrap=200, trim=0.1, smo=0.02, seed=42)` | LRT-based outlier detection with bootstrap (returns threshold and null distribution). |
| `magnitude_shape` | `(data)` | Magnitude-shape outlyingness. |
| `muod` | `(data, factor=1.5)` | MUOD (Massive Unsupervised Outlier Detection) for functional data. |
| `outliergram` | `(data, factor=1.5)` | Outliergram (MEI vs MBD plot). |
| `sequential_transform_outliers` | `(data, transforms, depth_method='modified_band', emp_factor=1.5)` | Sequential transform outlier detection. |
| `tvdmss` | `(data, emp_factor_mss=1.5, emp_factor_tvd=1.5, central_region_tvd=0.5)` | TVD-MSS functional outlier detection. |

### `fdars.pace_fpca` {#pace_fpca}

PACE: Principal Analysis by Conditional Expectation for sparse data.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `PyIrregFdata` | `(...)` | Opaque handle wrapping fdars-core IrregFdata for irregular/sparse functional data. |
| `irreg_fdata_from_lists` | `(argvals_list, values_list)` | Build an IrregFdata handle from two Python lists of ragged 1-D arrays. |
| `pace_fpca` | `(data, ncomp=3, bandwidth=0.1, sigma2=0.01, work_grid=None, alpha=0.05)` | Run PACE FPCA on irregular/sparse functional data. |

### `fdars.regression` {#regression}

Functional regression — scalar-on-function, function-on-scalar, GLM.

[Reference docs](https://sipemu.github.io/pyfda/reference/regression/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `bootstrap_ci_fregre_lm` | `(data, response, n_comp=3, n_boot=200, alpha=0.05, seed=42)` | Bootstrap confidence intervals for beta(t) from a functional linear model. |
| `bootstrap_ci_functional_logistic` | `(data, labels, n_comp=3, n_boot=200, alpha=0.05, seed=42, max_iter=25, tol=1e-06)` | Bootstrap confidence intervals for beta(t) from a functional logistic model. |
| `concurrent_regression` | `(predictors, response, argvals=None, bandwidth=0.2, kernel='gaussian')` | Concurrent (varying-coefficient) functional regression. |
| `fanova` | `(data, groups, n_perm=999)` | Functional ANOVA. |
| `fof_cv` | `(x_data, y_data, x_argvals, y_argvals, ncomp_x_max=5, ncomp_y_max=5, n_folds=5, seed=42)` | Cross-validated selection of FPC component counts for function-on-function regression. |
| `fof_re_regression` | `(x_data, y_data, subject_ids, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)` | Function-on-function random-effects regression (mixed model). |
| `fof_regression` | `(x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)` | Function-on-function linear regression via FPC basis decomposition. |
| `fosr` | `(response, predictors, lambda_=0.0)` | Function-on-scalar regression (FOSR). |
| `fosr_fpc` | `(data, predictors, n_comp=3)` | Function-on-scalar regression via FPCs (FOSR-FPC). |
| `fpca` | `(data, argvals, n_comp=3)` | Functional principal component analysis (FPCA). |
| `fpls` | `(data, argvals, response, n_comp=3)` | Functional PLS (Partial Least Squares). |
| `fregre_cv` | `(data, response, k_min=1, k_max=10, n_folds=5)` | Cross-validated selection of number of FPC components using K-fold CV. |
| `fregre_huber` | `(data, response, n_comp=3, huber_k=1.345)` | Huber M-estimation regression for functional data. |
| `fregre_l1` | `(data, response, n_comp=3)` | L1 robust regression for functional data. |
| `fregre_lm` | `(data, response, n_comp=3)` | Scalar-on-function linear regression via FPCs. |
| `fregre_np` | `(dist_matrix, response, h=0.0)` | Nonparametric kernel regression for functional data (from distance matrix). |
| `fregre_np_cv` | `(data, response, argvals, n_folds=5, h_range=None, scalar_covariates=None)` | Cross-validated bandwidth selection for nonparametric functional regression. |
| `fregre_np_mixed` | `(data, response, argvals, h_func, h_scalar=1.0, scalar_covariates=None)` | Nonparametric functional regression mixing functional and scalar predictors. |
| `fregre_pls` | `(data, argvals, response, n_comp=3)` | Scalar-on-function PLS regression. |
| `functional_glm` | `(data, response, family='gaussian', n_comp=3, scalar_covariates=None, max_iter=25, tol=1e-06)` | Functional generalised linear model (GLM) via FPC scores. |
| `functional_logistic` | `(data, labels, n_comp=3, max_iter=25, tol=1e-06)` | Functional logistic regression. |
| `model_selection_ncomp` | `(data, response, max_comp=10, criterion='gcv')` | Cross-validated selection of number of FPC components. |
| `predict_fof` | `(x_data, y_data, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)` | Predict functional responses for new predictor curves using a function-on-function model. |
| `predict_fof_re` | `(x_data, y_data, subject_ids, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)` | Predict functional responses using a function-on-function random-effects model. |
| `predict_fosr` | `(response, predictors, new_predictors, lambda_=0.0)` | Predict new functional responses from a fitted FOSR model. |
| `predict_fregre_lm` | `(data_fit, response, new_data, n_comp=3)` | Predict new responses using a fitted functional linear model. |
| `predict_fregre_pls` | `(data, argvals, response, new_data, n_comp=3)` | Predict new responses using a fitted PLS regression. |
| `predict_fregre_robust` | `(data, response, new_data, n_comp=3, method='l1', huber_k=1.345)` | Predict new responses using a fitted robust regression (L1 or Huber). |
| `predict_functional_logistic` | `(data, labels, new_data, n_comp=3, max_iter=25, tol=1e-06)` | Predict probabilities for new data using a fitted functional logistic model. |

### `fdars.represent` {#represent}

Dimensionality reduction and functional representation tools.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `fdata_interpolate_with_policy` | `(data, argvals, query_points, policy='exception', fill_value=0.0, method='linear')` | Interpolate functional data with explicit extrapolation control (linear/cubic variant). |
| `impute_missing_values` | `(data, argvals, method='linear', constant_value=0.0)` | Impute NaN values in a functional data matrix. |
| `spline_interpolate` | `(data, argvals, query_points, order=4)` | Interpolate functional data onto a new set of query points using B-splines. |
| `spline_interpolate_with_policy` | `(data, argvals, query_points, policy='exception', fill_value=0.0, order=4)` | Interpolate functional data with explicit extrapolation control (spline variant). |

### `fdars.scalar_on_function` {#scalar_on_function}

Scalar-on-function regression with regularisation.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `fam` | `(data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel='gaussian', n_grid_bandwidth=20)` | Fit a Functional Additive Model (FAM) with a single functional predictor. |
| `fregre_gkam` | `(predictors, y, argvals_list, scalar_covariates=None, bandwidth=0.0, kernel='gaussian', max_iter=50, epsilon=1e-06)` | Fit a Generalised Kernel Additive Model (GKAM) with multiple functional predictors. |
| `fregre_gsam` | `(data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel='gaussian', n_grid_bandwidth=20)` | Fit a Generalised Structured Additive Model (GSAM) with a single functional predictor. |
| `model_selection_ncomp` | `(data, response, max_comp=10, criterion='gcv')` | Select the optimal number of FPC components for scalar-on-function regression. |
| `variable_selection` | `(predictors, y, argvals_list, scalar_covariates=None, ncomp=3, penalty='group_lasso', lambda_=0.0, max_iter=100, epsilon=1e-05, lambda_n_grid=20)` | Functional variable selection via group-lasso penalised regression. |

### `fdars.scoring` {#scoring}

Functional scoring — penalised, tolerance-band, and integrated scores.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `functional_explained_variance` | `(y_true, y_pred, argvals)` | Functional Explained Variance Score integrated over `argvals`. |
| `functional_mae` | `(y_true, y_pred, argvals)` | Functional Mean Absolute Error integrated over `argvals`. |
| `functional_mape` | `(y_true, y_pred, argvals)` | Functional Mean Absolute Percentage Error integrated over `argvals`. |
| `functional_mse` | `(y_true, y_pred, argvals)` | Functional Mean Squared Error integrated over `argvals`. |
| `functional_msle` | `(y_true, y_pred, argvals)` | Functional Mean Squared Logarithmic Error integrated over `argvals`. |

### `fdars.seasonal` {#seasonal}

Seasonal functional decomposition and periodic pattern analysis.

[Reference docs](https://sipemu.github.io/pyfda/reference/seasonal/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `analyze_peak_timing` | `(data, argvals, period, smooth_nbasis=None)` | Analyze peak timing variability. |
| `autoperiod` | `(data, argvals, n_candidates=None, gradient_steps=None)` | Autoperiod algorithm for period detection. |
| `cfd_autoperiod` | `(data, argvals, cluster_tolerance=None, min_cluster_size=None)` | CFD autoperiod for period detection. |
| `classify_seasonality` | `(data, argvals, period, strength_threshold=None, timing_threshold=None)` | Classify seasonality type. |
| `detect_multiple_periods` | `(data, argvals, max_periods=3, min_confidence=1.5, min_strength=0.1)` | Detect multiple seasonal periods by iterative residual peeling. |
| `detect_peaks` | `(data, argvals, min_distance=None, min_prominence=None, smooth_first=False, smooth_nbasis=None)` | Detect peaks in functional data. |
| `detect_seasonality_changes` | `(data, argvals, period, threshold, window_size, min_duration)` | Detect seasonality change points. |
| `estimate_period_acf` | `(data, argvals, max_lag=None)` | Estimate the dominant seasonal period via autocorrelation (ACF). |
| `estimate_period_fft` | `(data, argvals)` | Estimate period using FFT periodogram. |
| `instantaneous_period` | `(data, argvals)` | Instantaneous period estimation via Hilbert transform. |
| `lomb_scargle_fdata` | `(data, argvals, oversampling=None, nyquist_factor=None)` | Lomb-Scargle periodogram for functional data. |
| `matrix_profile_fdata` | `(data, subsequence_length=None, exclusion_zone=None)` | Matrix Profile analysis for functional data. |
| `sazed` | `(data, argvals, tolerance=None)` | SAZED period detection algorithm. |
| `seasonal_strength` | `(data, argvals, period, method='variance')` | Seasonal strength measure (variance method). |
| `seasonal_strength_wavelet` | `(data, argvals, period)` | Seasonal strength using wavelet method. |
| `seasonal_strength_windowed` | `(data, argvals, period, window_size, method='variance')` | Time-varying seasonal strength using windowed estimation. |
| `ssa_fdata` | `(data, window_length=None, n_components=None)` | Singular Spectrum Analysis for functional data. |
| `stl_decompose` | `(data, period, s_window=None, t_window=None, robust=False)` | STL decomposition of functional data. |

### `fdars.shapelet` {#shapelet}

Functional shapelets — pattern-based classification and feature learning.

[Reference docs](https://sipemu.github.io/pyfda/reference/index/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `PyShapeletClassifierFit` | `(...)` | Opaque handle wrapping fdars-core ShapeletClassifierFit. |
| `PyShapeletFit` | `(...)` | Opaque handle wrapping fdars-core ShapeletTransformFit. |
| `discover_shapelets` | `(data, labels, min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality='info_gain', seed=0)` | Discover shapelets in labeled functional data and return a summary dict. |
| `shapelet_classifier_fit` | `(data, labels, min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality='info_gain', seed=0, classifier='knn', k=1, ncomp=None)` | Fit a shapelet-based classifier on labeled functional data. |
| `shapelet_distance` | `(shapelet_z, series, best_so_far=Ellipsis)` | Compute the shapelet distance between a z-normalized shapelet and a series. |
| `shapelet_transform` | `(fit, data)` | Apply a fitted shapelet transform to new functional data. |
| `shapelet_transform_fit` | `(data, labels, min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality='info_gain', seed=0)` | Fit a shapelet transform on labeled functional data. |

### `fdars.simulation` {#simulation}

Simulation of functional data — GPs, Brownian motion, Ornstein-Uhlenbeck.

[Reference docs](https://sipemu.github.io/pyfda/reference/simulation/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `add_error_curve` | `(data, sd, seed=None)` | Add curve-level Gaussian noise to functional data. |
| `add_error_pointwise` | `(data, sd, seed=None)` | Add pointwise Gaussian noise to functional data. |
| `covariance_matrix` | `(argvals, kernel='gaussian', length_scale=0.2, variance=1.0)` | Compute covariance matrix from a kernel. |
| `eigenfunctions` | `(argvals, n_basis, efun_type='fourier')` | Compute eigenfunctions. |
| `eigenvalues` | `(n_basis, eval_type='linear')` | Compute eigenvalues. |
| `gaussian_process` | `(n, argvals, kernel='gaussian', length_scale=0.2, variance=1.0, seed=None)` | Generate Gaussian process samples. |
| `sim_kl` | `(n, phi, big_m, lambda_, seed=None)` | Simulate functional data via Karhunen-Loeve expansion (low-level). |
| `simulate` | `(n, argvals, n_basis=5, efun_type='fourier', eval_type='linear', seed=None)` | Simulate functional data via Karhunen-Loeve expansion. |

### `fdars.smoothing` {#smoothing}

Functional smoothing — kernel, basis, and roughness-penalised methods.

[Reference docs](https://sipemu.github.io/pyfda/reference/smoothing/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `cv_smoother` | `(x, y, bandwidth, kernel='gaussian')` | LOO-CV score for a kernel smoother. |
| `gcv_smoother` | `(x, y, bandwidth, kernel='gaussian')` | GCV score for a kernel smoother. |
| `knn_gcv` | `(x, y, max_k)` | Global LOO-CV for kNN k selection. |
| `knn_lcv` | `(x, y, max_k)` | Local (per-observation) LOO-CV for kNN k selection. |
| `knn_smoother` | `(x, y, x_new, k)` | K-nearest neighbors smoother. |
| `local_linear` | `(x, y, x_new, bandwidth, kernel='gaussian')` | Local linear regression smoother. |
| `local_polynomial` | `(x, y, x_new, bandwidth, degree=1, kernel='gaussian')` | Local polynomial regression smoother. |
| `nadaraya_watson` | `(x, y, x_new, bandwidth, kernel='gaussian')` | Nadaraya-Watson kernel smoother. |
| `optim_bandwidth` | `(x, y, criterion='gcv', kernel='gaussian', n_grid=50, h_min=None, h_max=None)` | Optimal bandwidth selection via cross-validation. |
| `smoothing_matrix_nw` | `(x, bandwidth, kernel='gaussian')` | Smoothing matrix for Nadaraya-Watson. |

### `fdars.spm` {#spm}

Statistical process monitoring — T2, SPE, control charts.

[Reference docs](https://sipemu.github.io/pyfda/reference/spm/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `arl0_ewma_t2` | `(eigenvalues, ucl, lambda_, n_simulations=10000, max_run_length=5000, seed=42)` | In-control ARL for EWMA T-squared chart. |
| `arl0_spe` | `(spe_df, spe_scale, ucl, n_simulations=10000, max_run_length=5000, seed=42)` | In-control ARL for SPE chart. |
| `arl0_t2` | `(eigenvalues, ucl, n_simulations=10000, max_run_length=5000, seed=42)` | In-control ARL for T-squared chart (ARL0). |
| `arl1_t2` | `(eigenvalues, ucl, shift, n_simulations=10000, max_run_length=5000, seed=42)` | Out-of-control ARL for T-squared chart (ARL1). |
| `ewma_scores` | `(scores, lambda_)` | EWMA smoothing of FPC scores. |
| `hotelling_t2` | `(scores, eigenvalues)` | Hotelling T^2 statistic. |
| `hotelling_t2_regularized` | `(scores, eigenvalues, epsilon)` | Hotelling T^2 with eigenvalue regularization. |
| `mfpca` | `(variables, ncomp=5, weighted=True)` | Multivariate Functional Principal Component Analysis (MFPCA). |
| `nelson_rules` | `(values, center, sigma)` | Apply Nelson rules to monitoring data. |
| `select_ncomp` | `(eigenvalues, method='cumulative_variance', threshold=0.95)` | Select the number of principal components. |
| `spe_control_limit` | `(spe_values, alpha)` | Compute SPE control limit using moment-matched chi-squared approximation. |
| `spe_limit_robust` | `(spe_values, alpha=0.05, method='empirical')` | Robust SPE (squared prediction error) control limit. |
| `spe_moment_match_diagnostic` | `(spe_values)` | Diagnostic for SPE moment-match chi-squared approximation. |
| `spe_multivariate` | `(standardized_vars, reconstructed_vars, argvals_list)` | Multivariate Squared Prediction Error (SPE) monitoring statistic. |
| `spm_cusum` | `(train_data, sequential_data, argvals, ncomp=5, alpha=0.05, k=0.5, h=5.0, multivariate=False)` | Functional CUSUM control chart (fit Phase I + monitor). |
| `spm_ewma` | `(train_data, sequential_data, argvals, ncomp=5, alpha=0.05, lam=0.2)` | Functional EWMA control chart (fit Phase I + monitor). |
| `spm_monitor` | `(mean, loadings, weights, eigenvalues, t2_limit, spe_limit, new_data, argvals)` | SPM Phase II monitoring. |
| `spm_phase1` | `(data, argvals, ncomp=3, alpha=0.05)` | SPM Phase I estimation. |
| `t2_control_limit` | `(ncomp, alpha)` | Compute T-squared control limit from chi-squared distribution. |
| `t2_limit_robust` | `(t2_values, ncomp, alpha=0.05, method='empirical')` | Robust Hotelling T^2 control limit. |
| `t2_pc_contributions` | `(scores, eigenvalues)` | Per-PC T-squared contributions. |
| `t2_pc_significance` | `(contributions, alpha)` | Test per-PC T-squared contributions for Bonferroni-adjusted significance. |
| `western_electric_rules` | `(values, center, sigma)` | Apply Western Electric rules to monitoring data. |

### `fdars.tolerance` {#tolerance}

Functional tolerance bands — simultaneous and pointwise coverage.

[Reference docs](https://sipemu.github.io/pyfda/reference/tolerance/)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `conformal_prediction_band` | `(data, coverage=0.95, cal_fraction=0.25, seed=42)` | Conformal prediction band. |
| `elastic_tolerance_band` | `(data, argvals, ncomp=3, nb=200, coverage=0.95, band_type='simultaneous', max_iter=20, seed=42)` | Elastic tolerance band (amplitude only, after alignment). |
| `elastic_tolerance_band_with_config` | `(data, argvals, ncomp_amplitude=3, ncomp_phase=3, nb=200, coverage=0.95, band_type='pointwise', max_iter=20, tol=0.0001, seed=42)` | Joint amplitude and phase elastic tolerance bands. |
| `equivalence_test` | `(data1, data2, delta, alpha=0.05, nb=1000, seed=42)` | Functional equivalence test (TOST). |
| `equivalence_test_one_sample` | `(data, mu0, delta, alpha=0.05, nb=1000, seed=42)` | One-sample equivalence test. |
| `exponential_family_tolerance_band` | `(data, family='gaussian', ncomp=3, nb=200, coverage=0.95, seed=42)` | Exponential family tolerance band. |
| `fpca_tolerance_band` | `(data, ncomp=3, nb=1000, coverage=0.95, seed=42)` | FPCA-based tolerance band. |
| `phase_tolerance_band` | `(data, argvals, ncomp=3, nb=200, coverage=0.95, band_type='simultaneous', max_iter=20, seed=42)` | Phase tolerance band on warping functions. |
| `scb_mean_degras` | `(data, argvals, bandwidth=0.0, nb=1000, confidence=0.95)` | Simultaneous confidence band (Degras method). |
