# Feature Research

**Domain:** fdars-core 0.17 new bindings — interpolation/representation, functional statistics & scoring, alignment/registration
**Researched:** 2026-08-13
**Confidence:** MEDIUM (docs.rs/fdars-core 0.17.0 direct fetch + GitHub release notes v0.15/0.16)

> Scope: v4.0 new capabilities only. All existing fdars binding + v3.0 advisor coverage already shipped.
> This document characterises the 14 new methods across 3 groups for: binding implementation,
> SVG diagram authoring, worked examples, and advisor extension.

---

## Per-Method Reference Table

### Group 1 — Interpolation & Representation

#### `spline_interpolate`

| Field | Detail |
|-------|--------|
| **Definition** | Fits an order-k B-spline interpolant per curve (reusing the existing B-spline basis system — fit-then-evaluate, no P-spline smoothing) and evaluates at arbitrary query points. Signature: `spline_interpolate(data: &FdMatrix, argvals: &[f64], query_points: &[f64], order: usize) -> Result<FdMatrix, FdarError>`. Returns n×len(query_points) FdMatrix. Raises `InvalidParameter` if any query point falls outside `[argvals[0], argvals[m-1]]`. |
| **Inputs / Outputs** | In: n×m FdMatrix (curves), m-length sorted argvals, q-length query_points, integer order (1=linear, 2=quadratic, 4=cubic). Out: n×q FdMatrix of interpolated values. Errors: `InvalidDimension` on shape mismatch or empty query_points; `ComputationFailed` on SVD failure. |
| **Basis system reuse** | YES — reuses `fdata_to_basis_1d` / B-spline basis already bound in `src/basis_mod.rs`. No new numerical infrastructure needed. |
| **Best dataset** | **canadian_weather** (35 stations × 365 days) — upsample or resample to new time grid; or **growth** (93 × 31) to upsample sparse age measurements onto a fine grid before computing velocity. |
| **Target docs section** | `represent/` — new page or sub-section of `basis-representation.md`. Table stakes. |
| **Diagram concept** | Three-panel SVG: (left) original sparse evaluation points as dots on a curve; (centre) B-spline interpolant as a smooth continuous line with the knot positions marked; (right) re-evaluated curve at denser query_points, showing how the method differs from linear interpolation at sharp transitions. |
| **Advisor relevance** | LOW — pure data operation, no model choice. Not worth a dedicated advisor aspect. |
| **Complexity** | LOW. Thin wrapper; basis_mod pattern already established. |

#### `spline_interpolate_with_policy` / `fdata_interpolate_with_policy`

| Field | Detail |
|-------|--------|
| **Definition** | Like `spline_interpolate` but adds an `ExtrapolationPolicy` parameter controlling behaviour when query points fall outside `[argvals[0], argvals[m-1]]`. `fdata_interpolate_with_policy` is the FdMatrix-level equivalent. The four policy variants: **Boundary** — clamp: returns spline value at nearest boundary (t_min or t_max); **Exception** — returns `Err(InvalidParameter)` for any out-of-range point (same as `spline_interpolate` base); **Fill(v: f64)** — assigns the constant v to all out-of-range cells; **Periodic** — modulo wrap: maps t to `((t-t_min) % L + L) % L + t_min` before evaluating, making the curve cyclic with period L = t_max - t_min. |
| **Inputs / Outputs** | Same as `spline_interpolate` plus `policy: ExtrapolationPolicy`. Out: same n×q FdMatrix, with out-of-domain cells handled per policy. |
| **Canonical use case** | Periodic: Canadian weather (daily temperature is inherently annual-periodic — day 366 should join to day 1). Fill(0.0): sensor dropout, zero-padding beyond measurement window. Boundary: safe default when small floating-point overruns of domain occur. |
| **Best dataset** | **canadian_weather** — daily temperature naturally periodic over a year. Also **phoneme** if upsampling log-periodograms to a finer frequency grid. |
| **Target docs section** | `represent/` — same page as `spline_interpolate`; one section per policy variant. Table stakes (extrapolation control is expected of any interpolation library). |
| **Diagram concept** | Four-panel SVG showing a single curve that ends at t_max, with query points extending beyond: Boundary panel shows flat horizontal extension; Exception panel shows a red "stop" marker at boundary; Fill panel shows the curve dropping to the fill value (dashed); Periodic panel shows the curve wrapping and repeating its beginning. |
| **Advisor relevance** | LOW for Boundary/Exception/Fill. MEDIUM for Periodic — advisor could flag: "your data appears periodic (Fourier basis detected); consider `ExtrapolationPolicy::Periodic` for extrapolation". |
| **Complexity** | LOW. Same wrapper pattern; enum variant maps directly to PyO3 string or int discriminant. |

#### `impute_missing_values` + `ImputationMethod`

| Field | Detail |
|-------|--------|
| **Definition** | Replaces NaN entries in a regular-grid FdMatrix per curve using one of three strategies. Signature: `impute_missing_values(data: &FdMatrix, argvals: &[f64], method: ImputationMethod) -> Result<FdMatrix, FdarError>`. **Linear**: for each NaN at position j, linearly interpolates between nearest left and right non-NaN neighbours in the same curve; at boundary positions, extends from the nearest valid value. **Mean**: replaces each NaN with the mean of all non-NaN values in that curve. **Constant(v: f64)**: replaces all NaN entries with the constant v. Grid must be regular (argvals sorted, length = m). Returns a new FdMatrix with NaN entries filled; all non-NaN values preserved. |
| **Inputs / Outputs** | In: n×m FdMatrix (may contain NaN), m-length sorted argvals, ImputationMethod enum. Out: n×m FdMatrix with no NaN. Errors: dimension mismatch, unsorted argvals. |
| **Canonical use case** | Pre-processing before smoothing or depth computation when curves have dropout/sensor gaps. Sensor array where some channels fail per observation. |
| **Best dataset** | No real missing data in vendored datasets. Use **canadian_weather** or **growth** with synthetically injected NaN (mask 5-10% of values at random); this is a standard and convincing demonstration approach for docs. |
| **Target docs section** | `represent/` — new "Imputation" page or sub-section. Table stakes for real-data pipelines. |
| **Diagram concept** | Single-panel SVG: a curve with three gap segments shown as dotted lines; arrows and labels show Linear method filling the interior gap with a straight ramp, and the boundary gap with a horizontal extension from the last valid point. A small legend shows Mean and Constant as horizontal fill lines at different levels. |
| **Advisor relevance** | HIGH — advisor should detect NaN presence in input data and recommend appropriate ImputationMethod before further analysis. Worth a new diagnostic field (`nan_frac_per_curve`, `has_boundary_nans`) and recommendation task. |
| **Complexity** | LOW. Enum wrapping is a standard PyO3 pattern. |

---

### Group 2 — Functional Statistics & Scoring

#### `functional_variance` / `functional_std`

| Field | Detail |
|-------|--------|
| **Definition** | Pointwise Bessel-corrected sample variance across n curves at each of m evaluation points. Formula: `var[j] = Σᵢ (data[i,j] − mean[j])² / (n−1)`. `functional_std[j] = sqrt(var[j])`. `functional_std` delegates to `functional_variance` so the relationship `std²[j] == var[j]` holds exactly. Both return `Result<Vec<f64>, FdarError>`; `InvalidDimension` if n < 2. |
| **Inputs / Outputs** | In: n×m FdMatrix (n≥2). Out: length-m vector of pointwise variance / std. Both are pointwise (not integrated) — they are functions of t, not scalars. |
| **Canonical use case** | Visualise how variation across curves changes over the domain. High variance at a domain location indicates that curves disagree there (e.g., temperature spread is larger in winter months than summer in Canadian weather). |
| **Best dataset** | **canadian_weather** (35 × 365) — shows spatially structured variance (higher in winter); **growth** (93 × 31) — shows variance spike at the pubertal spurt age. |
| **Target docs section** | `analyze/` — new "Functional Summary Statistics" page, alongside covariance. Table stakes (expected alongside `mean`). |
| **Diagram concept** | Two-panel SVG: (left) overlaid curves with the mean shown as a bold line; (right) pointwise std as a shaded band ±1 std around the mean, with the std curve itself plotted below. The band is visually widest where curves diverge most. |
| **Advisor relevance** | HIGH — variance is a core diagnostic. Advisor already exposes mean; std should appear alongside it. Diagnostic fields: `max_pointwise_std`, `min_pointwise_std`, `std_peak_location` (argval index of maximum std). |
| **Complexity** | LOW. Same conversion pattern as `mean_1d`. |

#### `functional_covariance`

| Field | Detail |
|-------|--------|
| **Definition** | M×M Bessel-corrected sample covariance matrix. Entry formula: `cov[j₁,j₂] = Σᵢ (data[i,j₁]−mean[j₁])(data[i,j₂]−mean[j₂]) / (n−1)`. Symmetric; diagonal equals `functional_variance`. Stored column-major. Complexity: O(n·m²) — potentially expensive for large m. Returns `Result<FdMatrix, FdarError>`; requires n≥2. |
| **Inputs / Outputs** | In: n×m FdMatrix (n≥2). Out: m×m FdMatrix (symmetric covariance surface). Python binding returns 2D numpy array. |
| **Canonical use case** | Input to FPCA (eigendecomposition of the covariance operator); visualise the covariance surface as a heatmap; compute correlation surface by normalising with std. |
| **Best dataset** | **canadian_weather** (m=365) — covariance surface is interpretable (winter-winter correlation, summer-summer, cross-season); **tecator** (m=100) — quick compute, meaningful spectral covariance. |
| **Target docs section** | `analyze/` — same "Functional Summary Statistics" page, or a sub-section of the existing `covariance-functions.md`. Differentiator (the covariance *surface* vs scalar covariance). |
| **Diagram concept** | Heatmap SVG of an m×m symmetric covariance surface (colour-coded, warm=high, cool=low) with the diagonal highlighted and correlation bands visible as off-diagonal ridges. Alternatively a 3D wireframe conceptual sketch in 2D projection. |
| **Advisor relevance** | MEDIUM — large covariance is already diagnosable via FPCA variance explained; the covariance function adds interpretability. Diagnostic: `covariance_trace` (sum of diagonal = total variance), `covariance_off_diag_max` (strength of temporal correlation). |
| **Complexity** | MEDIUM. Binding itself is low-complexity, but the return type is FdMatrix (2D), which requires `numpy2d_to_fdmatrix` pattern in reverse; the existing `basis_to_fdata_2d` pattern covers this. |

#### `depth_based_median`

| Field | Detail |
|-------|--------|
| **Definition** | Returns the **index** (usize) of the deepest curve under the Fraiman-Muniz depth measure — the functional data analogue of the (scalar) median. This is not the geometric median (which minimises L2 distance to all others) but the sample observation with the highest depth score, i.e., the most "central" curve. Distinct from `geometric_median` (iterative Weiszfeld, continuous L2). Formula: `i* = argmax_i D_FM(X_i)` where `D_FM(X_i) = (1/m) Σⱼ [1 − |F̂ⱼ(X_i(tⱼ)) − 0.5|] × (m/(m−1))` and F̂ⱼ is the empirical CDF at grid point tⱼ. Returns `Result<usize, FdarError>`; the actual curve is retrieved as `data.row(i_star)`. |
| **Inputs / Outputs** | In: n×m FdMatrix (n≥1). Out: usize index into the FdMatrix row order. Errors: `InvalidDimension` (n=0), `ComputationFailed` (empty depth vector, degenerate). |
| **Key distinction** | `depth_based_median` → returns an observed sample curve; `geometric_median` → returns a new (possibly interpolated) curve not in the sample. The depth-based median is more robust to outliers but constrained to the observed set. |
| **Best dataset** | **canadian_weather** — the median station is a meaningful representative; **phoneme** — median curve per class for class-representative visualisation. |
| **Target docs section** | `analyze/` — same "Functional Summary Statistics" page. Table stakes (as natural a concept as the scalar median). |
| **Diagram concept** | SVG showing n curves in light grey, the cross-sectional mean as a red dashed line, and the depth-based median as a bold blue line (selected from the actual curves). A depth score bar chart inset shows each curve's depth with the maximum highlighted. Contrast with geometric_median shown as a separate dotted line to illustrate the index-vs-continuous distinction. |
| **Advisor relevance** | HIGH — the depth-based median is already used implicitly in `trim_mean`; exposing it directly as a diagnostic (e.g., "median curve shape") strengthens outlier and centrality reports. Diagnostic: `median_curve_index`, `median_depth_score`, `median_vs_mean_l2_dist`. |
| **Complexity** | LOW. Returns a scalar index; the Python binding can additionally return the actual median curve as a 1D numpy array. |

#### `trim_mean`

| Field | Detail |
|-------|--------|
| **Definition** | Depth-trimmed mean: excludes the `floor(alpha × n)` least-deep curves (ranked by Fraiman-Muniz depth) and returns the pointwise mean of the remaining `n − floor(alpha × n)` curves. Formula: `trim_mean(alpha) = (1/|S_alpha|) Σᵢ∈S_alpha X_i(t)` where `S_alpha = {i : D_FM(X_i) ≥ quantile(D_FM, alpha)}`. At alpha=0 it equals the standard mean exactly. Signature: `trim_mean(data: &FdMatrix, alpha: f64) -> Result<Vec<f64>, FdarError>`; alpha in [0,1). |
| **Inputs / Outputs** | In: n×m FdMatrix (n≥1), alpha ∈ [0,1). Out: length-m vector (pointwise mean of retained curves). Errors: alpha outside [0,1), empty data. |
| **Canonical use case** | Robust central tendency when outlier curves are present (classic Febrero-Manteiga trim). Alpha=0.2 removes the 20% most peripheral curves before averaging — much more stable than the mean under functional outlier contamination. |
| **Best dataset** | **canadian_weather** — a handful of Arctic stations are peripheral; trim_mean at alpha=0.1-0.2 excludes them and gives a "typical Canadian" temperature profile. **Tecator** — robustness demo with fat-content outlier spectra. |
| **Target docs section** | `analyze/` — same "Functional Summary Statistics" page. Differentiator (robust functional mean is not standard in beginner FDA toolkits). |
| **Diagram concept** | Three-panel SVG: (left) all n curves with the standard mean; (centre) curves colour-coded by depth score (deep=dark, peripheral=light), with floor(alpha*n) peripheral curves visually faded; (right) only the retained curves with the trim_mean shown as a bolder, cleaner central line compared to the naive mean from panel 1. |
| **Advisor relevance** | HIGH — trim_mean is already used conceptually in the outlier-detection aspect (robust centre). Expose directly: diagnostic `trim_mean_alpha`, `trim_mean_n_excluded`, `trim_mean_vs_mean_max_deviation`. The advisor can recommend increasing alpha when outlier detection flags many peripheral curves. |
| **Complexity** | LOW. Same binding pattern as `mean_1d`; alpha is a Python float. |

#### `functional_mae` / `functional_mse` / `functional_mape` / `functional_msle` / `functional_explained_variance`

| Field | Detail |
|-------|--------|
| **Definition** | Five integrated functional scoring metrics, all in `fdars_core::scoring`, all with the same signature: `fn(y_true: MatrixRef, y_pred: MatrixRef, argvals: &[f64]) -> Result<f64, FdarError>`. Integration is via Simpson's rule. Each returns a single scalar (curve-averaged integrated score). Exact formulas: **MAE**: `(1/n) Σᵢ ∫|y_true_i(t) − y_pred_i(t)| dt`. **MSE**: `(1/n) Σᵢ ∫(y_true_i(t) − y_pred_i(t))² dt`. **MAPE**: `(1/n) Σᵢ ∫|y_true_i(t) − y_pred_i(t)| / |y_true_i(t)| dt`; raises `InvalidParameter` if any `|y_true| < NUMERICAL_EPS` (no epsilon in denominator — inputs near zero are rejected). **MSLE**: `(1/n) Σᵢ ∫(ln(1+y_true_i(t)) − ln(1+y_pred_i(t)))² dt`; raises `InvalidParameter` if any value ≤ −1. **explained_variance**: `(1/n) Σᵢ (1 − SS_res_i / SS_tot_i)` where `SS_res_i = ∫(residual_i(t) − mean_residual_i)² dt` and `SS_tot_i = ∫(y_true_i(t) − mean_true_i)² dt` (both integrated); special cases: SS_tot ≈ 0 and SS_res ≈ 0 → 1.0; SS_tot ≈ 0 and SS_res > 0 → 0.0. Range: (−∞, 1]. |
| **Key distinction from pointwise metrics** | These are domain-integrated scalars, not per-grid-point vectors. A model that gets one time window badly wrong but is accurate elsewhere may still score well — the integral weight matters. This is a genuine functional extension of the scalar metrics, not a simple column-wise average. |
| **Inputs / Outputs** | In: n×m `y_true`, n×m `y_pred`, m-length `argvals`. Out: single f64 scalar. Python: returns Python float. |
| **Canonical use case** | Evaluate functional regression predictions (e.g., tecator fat-content prediction from spectra → compare predicted vs true spectral residuals). Evaluate smoothing quality (aligned curves vs raw). Compare registration quality across methods. |
| **Best dataset** | **tecator** — NIR spectra regression, compare predicted vs true absorbance curves; **canadian_weather** — FPCA reconstruction vs original, reporting functional MSE by retained component count; **growth** — evaluate smoothing fit vs raw data. |
| **Target docs section** | `analyze/` — new "Functional Scoring Metrics" page. Also cross-linked from regression and smoothing sections. Differentiator (scikit-fda provides only pointwise metrics; domain-integrated versions are more theoretically sound for functional data). |
| **Diagram concept** | Two-panel SVG: (left) a pair of curves — y_true (bold) and y_pred (dashed) — with the absolute error |y_true − y_pred| shaded as a region between them; (right) bar chart or number strip showing the scalar scores (MAE, MSE, MAPE) computed from that region integral. The shading visually explains why the integral collapses the curve comparison to a single number. |
| **Advisor relevance** | HIGH — the natural evaluation surface for regression, smoothing, and alignment. Advisor should include: `functional_mse`, `functional_mae` in regression and smoothing diagnostics; `functional_explained_variance` as the primary quality score for regression. New diagnostic aspect: `"scoring"` covering all five metrics. |
| **Complexity** | LOW for binding (uniform signature, scalar output). MEDIUM for advisor integration (five metrics, three existing aspects to update). |

---

### Group 3 — Alignment / Registration

#### `least_squares_shift_registration`

| Field | Detail |
|-------|--------|
| **Definition** | Rigid horizontal (time-axis) alignment. For each curve `X_i`, finds the scalar shift `δ_i ∈ [−max_shift, max_shift]` that minimises the Simpson-weighted L2 distance between the time-shifted curve and the cross-sectional sample mean: `δ_i = argmin_δ ∫(X_i(t+δ) − μ(t))² dt`. Search method: golden-section search over the bracket `[−max_shift, max_shift]` (assumes unimodal objective). After each δ_i is found, the shifted curve is re-evaluated at the original grid via linear interpolation. Signature: `least_squares_shift_registration(data: &FdMatrix, argvals: &[f64], max_shift: f64) -> Result<ShiftRegistrationResult, FdarError>`. `ShiftRegistrationResult` contains aligned curves (n×m FdMatrix) and per-curve shift values (length-n Vec<f64>). Recommended `max_shift = 0.25 × (argvals.last − argvals.first)`. |
| **Contrast with karcher_mean** | `karcher_mean` (elastic): finds arbitrary monotone warp functions γ_i (time compression/expansion); can handle both stretching and shifting; Fisher-Rao / SRVF framework. `least_squares_shift_registration` (rigid): finds only a constant translation δ_i; computationally much cheaper; appropriate when curves are identical in shape but delayed. |
| **Inputs / Outputs** | In: n×m FdMatrix, m-length sorted argvals, positive max_shift scalar. Out: ShiftRegistrationResult → 2D aligned curves array + 1D shifts array. |
| **Canonical use case** | Annual temperature cycles where different stations are offset by a few days (phase lag due to climate zone). Growth velocity curves where the spurt timing differs by a constant offset per child. |
| **Best dataset** | **canadian_weather** — daily temperature; station-to-station phase offsets are approximately rigid shifts. **growth** — velocity curves differ mainly in spurt timing (though elastic is more accurate, shift registration is the instructive simpler baseline to contrast against). |
| **Target docs section** | `align/` — new "Shift Registration" page, positioned *before* `elastic-alignment.md` as the simpler baseline. Table stakes (shift registration is the entry-level alignment method; users expect it). |
| **Diagram concept** | Three-panel SVG: (left) misaligned curves with peaks at different t positions; (centre) illustration of the horizontal shift δ as a horizontal arrow on a single curve, with the objective (L2 to mean) shown as a shaded area; (right) registered curves with peaks aligned and the mean sharpened. Contrast with elastic alignment's curved warp by showing a straight horizontal arrow vs a curved warp arrow. |
| **Advisor relevance** | HIGH — shift registration produces per-curve shifts that are diagnostically meaningful. New advisor aspect `"shift_registration"`: diagnostics `mean_shift`, `max_abs_shift`, `shift_std`, `shift_range`, `convergence_flag`. The advisor can recommend: "large shift_std suggests phase variation is not purely rigid — consider elastic alignment." |
| **Complexity** | MEDIUM. ShiftRegistrationResult is a struct with two output arrays; binding requires unpacking into a Python dict (same pattern as `karcher_mean` result dict). |

#### `least_squares_score` / `pairwise_correlation_score` / `sobolev_least_squares_score`

| Field | Detail |
|-------|--------|
| **Definition** | Three registration quality scalars, all returning `Result<f64, FdarError>`. **least_squares_score**: `(1/n) Σᵢ ∫(registered_i(t) − μ(t))² dt` via Simpson; lower is better; absolute (not normalised); no zero-variance issue. **pairwise_correlation_score**: `mean over (i<k) of [⟨f̃_i, f̃_k⟩_L2 / (‖f̃_i‖_L2 × ‖f̃_k‖_L2)]` where `f̃_i = X_i − μ_i` (Simpson-weighted per-curve mean centering); this is centered functional Pearson correlation (not cosine similarity); range [−1, 1]; higher is better. **sobolev_least_squares_score**: `LS_score + λ × (1/n) Σᵢ ∫(X_i′(t) − μ′(t))² dt`; derivative approximated by 5-point stencil via `gradient_uniform`; requires uniform grid when λ > 0; lower is better; λ=0 reduces exactly to `least_squares_score`. |
| **Relationship** | These three scores are registration quality metrics, not objective functions — they evaluate the output of any alignment method (shift, elastic, landmark) on a common aligned dataset. They should be computed on the *same* aligned curves and compared across methods or parameter choices. |
| **Inputs / Outputs** | `least_squares_score`: In: registered n×m FdMatrix + argvals. `pairwise_correlation_score`: In: registered n×m FdMatrix + argvals. `sobolev_least_squares_score`: In: registered n×m FdMatrix + argvals + lambda (f64 ≥ 0). All Out: single f64 scalar. |
| **Canonical use case** | Compare shift registration vs elastic registration on the same dataset — which produces lower L2 spread or higher pairwise correlation? Parameter sweep for `max_shift` or `band_frac` using these scores as the objective. |
| **Best dataset** | **growth** — compare three registration methods side by side; **canadian_weather** — quantify how much phase variation the shift alignment removes. |
| **Target docs section** | `align/` — new "Registration Quality Scores" page, or a sub-section of the shift-registration or alignment-comparison page. Differentiator (explicit quality metrics for alignment are not common in beginner-level FDA tools). |
| **Diagram concept** | Three-panel SVG illustrating each score conceptually on the same set of registered curves: panel 1 shows the L2 shaded area to the mean (least_squares_score); panel 2 shows two curves with their centered versions and an inner-product annotation (pairwise_correlation_score); panel 3 shows the curves plus their derivative deviations highlighted (sobolev score adds derivative penalty). |
| **Advisor relevance** | HIGH — these are natural additions to the alignment advisor aspect. Current alignment diagnostics use L2 distances; adding `pairwise_correlation_score` as a higher-level quality flag and `least_squares_score` as a normalised spread improves actionability. Diagnostic fields: `ls_score`, `pairwise_corr_score`, `sobolev_score` (at a default lambda). Advisor recommendation: "pairwise_corr_score below 0.7 suggests poor alignment — increase max_iter or switch to elastic alignment." |
| **Complexity** | LOW for binding (scalar outputs). MEDIUM for advisor wiring (three new diagnostic fields in alignment aspect). |

#### `karcher_mean_with_band` + banded distance matrices

| Field | Detail |
|-------|--------|
| **Definition** | `karcher_mean_with_band(curves, argvals, band_frac: Option<f64>) -> KarcherMeanResult`: computes the same Fisher-Rao Karcher mean as `karcher_mean` (intrinsic Fréchet mean on the SRVF elastic manifold; Srivastava et al. 2011 arXiv:1103.3817) but when `band_frac` is given, restricts the dynamic-programming alignment step to a **Sakoe–Chiba band** of width `band_frac × domain_length`. The band confines the warp search to a diagonal strip in the (t_i, t_j) DP table, reducing per-pair complexity from O(m²) to O(m × band_frac × m) and achieving 4–6× measured speedup. `band_frac=None` gives the exact unconstrained Karcher mean (identical to `karcher_mean`). `elastic_self_distance_matrix_with_band` and `elastic_cross_distance_matrix_with_band` apply the same banding to pairwise distance computation. |
| **Sakoe-Chiba band** | Classic DTW constraint (Sakoe & Chiba 1978 IEEE TASL): only DP cells within `|i − j| ≤ B` (where B = band_frac × m) are evaluated. For smooth functional data where warps are mild, the global optimum lies within a narrow band, so the restricted search is accurate; for data with large phase variation, a wider band (larger band_frac) is needed. |
| **Inputs / Outputs** | `karcher_mean_with_band`: In: n×m FdMatrix, m-length argvals, optional band_frac (f64 ∈ (0,1]). Out: KarcherMeanResult dict (aligned_data, mean, warp functions, convergence info — same keys as existing `karcher_mean`). Distance matrix variants: Out: Vec<Vec<f64>> square or rectangular matrix. |
| **Canonical use case** | Large-sample elastic alignment (n ≥ 200) where full unconstrained Karcher iteration is slow. Distance matrix computation for elastic clustering on large datasets. |
| **Best dataset** | **phoneme** (400 × 256) — large enough to see the speed benefit; elastic distance matrix for clustering. **canadian_weather** (35 × 365) — moderate size, fine grid, good for demonstrating band_frac parameter sweep with quality scores. |
| **Target docs section** | `align/` — sub-section of `elastic-alignment.md` or new "Banded Elastic Alignment" page under `advanced-alignment.md`. Differentiator (scaling elastic alignment to large datasets is a genuine practitioner need). |
| **Diagram concept** | SVG showing the DP table as a grid with the Sakoe–Chiba band highlighted as a diagonal stripe; outside the band shaded grey (not evaluated); inside the band colour-coded by accumulated cost. A second smaller panel shows two curves being aligned — the warp path can only travel within the stripe. Label `band_frac` as the stripe half-width parameter. |
| **Advisor relevance** | MEDIUM — `band_frac` is a speed/accuracy tradeoff parameter. Advisor recommendation: "dataset has n={n} curves with m={m} grid points; elastic distance matrix is O(n²m²); recommend band_frac=0.2 for 4× speedup with minimal accuracy loss for smooth curves." Diagnostic: `band_frac_used`, `n_dp_cells_evaluated`, `estimated_speedup_ratio`. |
| **Complexity** | LOW for `karcher_mean_with_band` (same result struct as `karcher_mean`; add one optional f64 param). LOW for distance matrix variants (return 2D array). |

---

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `spline_interpolate` | Every FDA toolkit can resample curves to new grids | LOW | Reuses existing B-spline basis_mod infrastructure |
| `impute_missing_values` | Real sensor data has gaps; preprocessing is assumed | LOW | Simple enum wrapper; three clearly distinct strategies |
| `functional_variance` / `functional_std` | Natural companions to `mean_1d` / `mean_2d` already bound | LOW | Pointwise, not integrated; same binding pattern as mean |
| `depth_based_median` | The functional median is as fundamental as the scalar median | LOW | Returns index; Python convenience wrapper extracts the curve |
| `functional_mae` / `functional_mse` | Any regression or smoothing evaluation needs error metrics | LOW | Uniform signature across all five; scalar output |
| `least_squares_shift_registration` | Rigid shift is the entry-level alignment; users expect it before elastic | MEDIUM | ShiftRegistrationResult struct → Python dict |
| `ExtrapolationPolicy` enum | Extrapolation control is expected in any interpolation library | LOW | Four clear variants; maps cleanly to PyO3 string discriminant |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `functional_mape` / `functional_msle` / `functional_explained_variance` | Simpson-integrated functional extensions — not column-wise averages; more theoretically correct for FDA | LOW-binding / MEDIUM-docs | MAPE has a strict zero-guard; MSLE has domain constraint ≥ −1 |
| `functional_covariance` | Full M×M covariance surface rather than scalar — enables covariance-surface visualisation and serves FPCA | MEDIUM | O(n·m²) — needs performance warning in docs for large m |
| `trim_mean` | Depth-trimmed robust mean — outlier-resistant centrality not available in most beginner toolkits | LOW | alpha parameter makes it a continuous spectrum from mean to deepest-curve |
| Registration quality scores (three) | Explicit quantitative comparison of alignment quality across methods/parameters — few FDA libraries expose these | LOW | The three scores form a natural comparison battery |
| `karcher_mean_with_band` + distance matrices | Scales elastic alignment to large datasets via Sakoe–Chiba band; 4–6× speedup measured | LOW | Same result dict as existing `karcher_mean`; one new optional param |
| `pairwise_correlation_score` | Centered functional Pearson (not cosine similarity) — higher interpretability than L2 spread alone | LOW | Requires centering per-curve first; semantically clearer for practitioners |
| `sobolev_least_squares_score` | Penalises rough registrations; captures smoothness of alignment not just amplitude fit | LOW | Requires uniform grid for derivative computation |

### Anti-Features (Do Not Build)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Automatic `band_frac` selection | Users want "just work" | Optimal band depends on phase variation magnitude — cannot be determined without domain knowledge; silently choosing a bad value corrupts alignment | Expose `band_frac` explicitly with docs guidance: "start at 0.2, widen if quality score degrades" |
| MAPE on zero-containing data with epsilon fallback | Users want MAPE to "just work" on any data | Epsilon-smoothed MAPE has undefined statistical meaning; misleads users about metric validity | fdars-core correctly rejects near-zero data — document this and recommend MSE or MSLE for such cases |
| Returning the median curve instead of its index | Intuitive user expectation | `depth_based_median` is defined as an index into the observed sample; returning the curve directly creates confusion with `geometric_median` which returns a new curve | Return both: index (from binding) and a convenience wrapper that also extracts `data[i_star]` as a separate Python helper |

---

## Feature Dependencies

```
spline_interpolate
    └──reuses──> basis_mod B-spline infrastructure (already bound)

spline_interpolate_with_policy
    └──extends──> spline_interpolate (same core; adds ExtrapolationPolicy)

fdata_interpolate_with_policy
    └──parallel to──> spline_interpolate_with_policy (FdMatrix-level wrapper)

impute_missing_values
    └──independent──> (no fdars binding dependency; NaN handling is self-contained)

functional_variance / functional_std
    └──used by──> functional_covariance (diagonal property)
    └──used by──> trim_mean (depth ranking depends on Fraiman-Muniz, not variance)

depth_based_median
    └──reuses──> Fraiman-Muniz depth (already bound in depth_mod)

trim_mean
    └──reuses──> Fraiman-Muniz depth (already bound in depth_mod)

functional_mae / functional_mse / functional_mape / functional_msle / functional_explained_variance
    └──independent──> (new scoring module; self-contained Simpson integration)

least_squares_shift_registration
    └──independent for binding──> (self-contained)
    └──compared against──> karcher_mean (existing binding)

least_squares_score / pairwise_correlation_score / sobolev_least_squares_score
    └──consume output of──> any registration method (shift or elastic)
    └──pairwise_correlation requires──> argvals for Simpson integration

karcher_mean_with_band
    └──extends──> existing karcher_mean (same result struct; adds optional band_frac)
    └──enables──> elastic_self_distance_matrix_with_band (same banding logic)

advisor "shift_registration" aspect
    └──consumes──> ShiftRegistrationResult + quality scores
    └──references──> existing alignment aspect for comparative recommendations

advisor "scoring" aspect
    └──consumes──> functional_mae / mse / mape / msle / explained_variance
    └──cross-links into──> existing regression_cv and smoothing aspects
```

---

## MVP Definition

This is a v4.0 milestone, not a greenfield launch. The ordering criterion is: (1) foundational bindings before docs that depend on them, (2) table-stakes before differentiators, (3) advisor work after bindings it depends on.

### Bind First (Phase A — crate bump + foundational)

All are required for the milestone; ordering by dependency:

- [x] Crate bump fdars-core 0.14.0 → 0.17.0 and verify existing suite green
- [x] `functional_variance`, `functional_std`, `functional_covariance` — foundational stats
- [x] `depth_based_median`, `trim_mean` — complete the depth-based statistics cluster
- [x] `spline_interpolate` + `ExtrapolationPolicy` + `spline_interpolate_with_policy` — interpolation
- [x] `impute_missing_values` + `ImputationMethod` — preprocessing prerequisite for examples

### Bind Second (Phase B — scoring + alignment)

- [x] `functional_mae` / `mse` / `mape` / `msle` / `explained_variance` — scoring module
- [x] `least_squares_shift_registration` + `ShiftRegistrationResult` — shift alignment
- [x] `least_squares_score` / `pairwise_correlation_score` / `sobolev_least_squares_score` — quality scores
- [x] `karcher_mean_with_band` + banded distance matrix variants — banded elastic

### Extend Advisor (Phase C)

- [x] Imputation diagnostic (nan_frac, has_boundary_nans, method recommendation)
- [x] Scoring metrics in regression/smoothing aspects (functional_mse, explained_variance)
- [x] Shift registration aspect (shifts distribution, quality scores)
- [x] Alignment aspect extension (add quality scores to existing alignment diagnostics)

### Docs (Phase D — each binding group gets diagrams + worked examples)

- [x] represent/ — spline_interpolate, ExtrapolationPolicy, impute_missing_values pages/sections
- [x] analyze/ — functional statistics + scoring metrics pages
- [x] align/ — shift registration + quality scores + banded elastic alignment pages

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| `functional_variance` / `functional_std` | HIGH (foundational; gaps feel glaring) | LOW | P1 |
| `depth_based_median` | HIGH (obvious companion to existing depth) | LOW | P1 |
| `spline_interpolate` | HIGH (resampling is expected) | LOW | P1 |
| `impute_missing_values` | HIGH (real data has missing values) | LOW | P1 |
| `functional_mae` / `mse` | HIGH (regression/smoothing evaluation) | LOW | P1 |
| `least_squares_shift_registration` | HIGH (entry-level alignment) | MEDIUM | P1 |
| `trim_mean` | MEDIUM (useful but not urgent) | LOW | P2 |
| `functional_covariance` | MEDIUM (advanced visualisation; needed for FPCA grounding) | MEDIUM | P2 |
| `ExtrapolationPolicy` + `spline_interpolate_with_policy` | MEDIUM (edge-case control; periodic is high value) | LOW | P2 |
| `functional_mape` / `msle` / `explained_variance` | MEDIUM (richer diagnostics; MAPE has domain restriction) | LOW | P2 |
| Registration quality scores (all three) | MEDIUM (differentiator; pairs with shift registration) | LOW | P2 |
| `karcher_mean_with_band` + distance matrices | MEDIUM (needed for large-scale users) | LOW | P2 |
| Advisor: scoring aspect | HIGH (closes the regression/smoothing grounding gap) | MEDIUM | P1 |
| Advisor: shift_registration aspect | HIGH (new method needs advisor coverage) | MEDIUM | P2 |
| Advisor: imputation diagnostics | MEDIUM (preprocessing advice) | LOW | P2 |

---

## Sources

- `docs.rs/fdars-core/0.17.0` — direct module/function documentation fetch (MEDIUM confidence; webfetch provider)
- `github.com/sipemu/fdars` releases page — v0.15.0 and v0.16.0 release notes confirming which functions shipped in which version (MEDIUM confidence; webfetch provider)
- `github.com/sipemu/fdars` alignment_references.md — Srivastava et al. 2011 arXiv:1103.3817 for Karcher mean; Sakoe & Chiba 1978 IEEE TASL for banded DP constraint
- Existing pyfda docs (`docs/align/elastic-alignment.md`, `docs/align/landmark-registration.md`, `docs/represent/basis-representation.md`, `docs/analyze/outlier-detection.md`) — established tone, diagram conventions, and cross-linking patterns (HIGH confidence; direct file read)
- `docs/data/README.md` — dataset shapes and contents for example selection (HIGH confidence; direct file read)
- `.planning/PROJECT.md` — current milestone scope and v4.0 target features list (HIGH confidence; direct file read)

---

*Feature research for: fdars v4.0 — fdars-core 0.17 new bindings (interpolation, functional stats, alignment)*
*Researched: 2026-08-13*
