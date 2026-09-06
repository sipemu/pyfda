# Phase 75: Deepen Analyze-Family Thin Pages — Research

**Researched:** 2026-09-05
**Domain:** MkDocs documentation depth — analyze-family method pages
**Confidence:** HIGH (all API facts verified directly from Rust binding source this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Page Depth & Structure**
- Depth target: Hit the parity bar solidly at mature-page *quality*, sized to each method's actual surface — do not pad to a fixed length.
- Restructure approach: Mirror the mature numbered-section template used by the mature analyze pages (e.g. `docs/analyze/clustering.md`, `outlier-detection.md`, `seasonal-analysis.md`, `functional-statistics.md`). Preserve correct existing prose/examples; restructure and expand around them rather than rewriting from scratch.
- Exec'd visualizations: Add ≥1 `html="1"` exec'd matplotlib plot per page where it genuinely clarifies the method.

**Worked Examples & Data**
- Data source: Prefer small, self-contained synthetic simulations built *inside* each fence (deterministic, offline, fast). Use existing `docs/data/` datasets where a method has a natural real-data fit (e.g. a time-series dataset for `functional-time-series`). Success criterion 4 explicitly names the existing `docs/data/` datasets — use them where they fit, do not invent files.
- Count: ≥3 runnable inline fences per page; add more only where a distinct method variant warrants its own example.
- Sentinel: Every runnable example must emit `FDARS_FENCE_OK` when run offline under `.venv`. Fences stay small to bound the ~25-min whole-site strict build that runs once in Phase 79.

**Cross-Reference & Accuracy**
- See also: Each page links to related methods within the analyze family and the analyze index (3–5 links), so the five pages cross-navigate.
- Admonitions: ≥3 per page mixing `note` / `tip` / `warning` / `info`, method-specific (parameter guidance, caveats, return-type gotchas).
- API accuracy: Every method claim, function name, and signature must be accurate against the shipped v11.0 bindings — no stale/renamed API, no R-era prose. Runnable fences are self-verifying; verify remaining prose claims against the current `fdars` surface. Keep a "methods in R but not (yet) in Python" note only where accurate.

### Claude's Discretion

(None specified beyond the locked decisions above.)

### Deferred Ideas (OUT OF SCOPE)

- Flagship end-to-end example pages (incl. the FTS flagship) → Phase 76 (EXMP)
- Section-landing thumbnails + cards for these pages → Phase 77 (CARD-04)
- Whole-site strict build / SVGO / human diagram review → Phase 79 (GATE)
- DEPTH-FUT-01: depth sweep of any older thin pages beyond this v11.0-era set
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEPTH-02 | The analyze-family thin pages — `functional-time-series`, `density-fda`, `multi-domain`, `shapelets`, `advanced-clustering` — each reach the parity bar: a "When to use" decision section, a "See also" cross-reference block, parameter-selection + result-interpretation guidance, ≥3 caution/tip/note admonition boxes, and ≥3 runnable inline `FDARS_FENCE_OK` worked examples per page. | Full API surface verified per-page below; mature-page template dissected from clustering.md and outlier-detection.md; cross-ref targets enumerated; all known discrepancies documented. |
</phase_requirements>

---

## Summary

Phase 75 is a docs-only depth pass on five analyze-family pages that shipped at 20–35% parity in v11.0. All API research below was obtained by reading the Rust binding sources (`src/fts_mod.rs`, `src/density_fda_mod.rs`, `src/shapelet_mod.rs`, `src/clustering_mod.rs`, `src/spm_mod.rs`, `src/famm_mod.rs`, `src/multi_fdata_mod.rs`) and the existing page files directly — no training-memory API claims.

**Critical finding:** The five thin pages contain several important API errors and structural omissions that must be corrected as part of expanding them. The most serious: `functional-time-series.md` lists `ftsm_update` with a wrong signature (missing `new_curve` 2D argument at position 2), `density-fda.md` shows `inverse_lqd(lqd, argvals)` with the wrong signature (the actual binding takes three arguments: `psi, t_grid, target_argvals`), and `multi-domain.md` claims `multi_fdata_from_components` output is "usable as input to `dense_flmm` and `multi_famm`" which is incorrect in fdars-core 0.33 (both FAMM functions take plain numpy arrays, not a `PyMultiFunData` handle). The `lqd_transform` on the density-fda page also omits the optional `n_quantile_pts` parameter. These discrepancies are the highest-priority corrections.

The mature analyze-page template is well established across `clustering.md`, `outlier-detection.md`, and `seasonal-analysis.md`. Synthetic in-fence simulation is the right primary data strategy; `canadian_weather.csv` (35 × 365 daily temperature) is the natural real-data fit for `functional-time-series`, and `sonar.csv` (208 × 60 energy bands) fits `shapelets` and `advanced-clustering` classification examples.

**Primary recommendation:** Each page gets a dedicated PLAN.md task. Task author reads this research, reads the existing thin page, fixes all documented API errors, and adds the missing structural sections per the template, keeping fences small and deterministic.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Page prose, structure, sections | Docs author | — | Pure markdown editing; no code change |
| Runnable fences (`exec="1"`) | Docs author (inline fence code) | `fdars` package (execution engine) | Fences call the current installed `fdars` — no new bindings |
| matplotlib figures (`html="1"`) | `docs_fig.py` helper + `markdown-exec` | MkDocs Material render | `docs_fig.fig()` / `render()` / `fast()` pattern |
| API accuracy | Rust binding sources (source of truth) | Installed `.venv` package | All claims must trace to `src/*_mod.rs` |

---

## 1. Mature-Page Template (from `clustering.md` and `outlier-detection.md`)

The analyze-family mature pages use a slightly different skeleton from the regression pages. Derived from reading `clustering.md` and `outlier-detection.md` this session:

```
# Page Title

[1–2 paragraph intro explaining what problem this method solves, what "flavours" exist]

[Summary table: type | description | example  — OR method | function | targets | key output]

---

![concept diagram](../assets/diagrams/<slug>.svg){ .fdars-diagram }

## [First method / first algorithm or sub-problem]

### Theory

[Mathematical exposition — brief; key equation]

[exec'd matplotlib figure (html="1" source="above") — FIRST exec'd block, sets visual tone]

**Parameters** / **Returns** table

[!!! note / tip / warning specific to this method]

---

## [Second method / algorithm]

[Same structure: brief math, code block, parameters, returns, admonition]

---

## [Third method if applicable]

---

## Selecting the optimal [k / ncomp / eps / etc.]

[Parameter selection guidance — the CV or index-based approach]

[exec'd figure showing criterion vs. parameter value]

---

## Full example — [describe the scenario]

[Larger, integrative exec'd fence combining fitting + quality assessment]

---

## See also

- [Related page](page.md) — [one-line description]
- ...

## References

- [2–5 primary statistical references]
```

**Key formatting conventions (from reading the mature pages):**

- Sections are NOT numbered in the analyze pages (unlike regression) — they use plain `## Title` headers. The regression template used numbers; the analyze template does NOT. Mirror the analyze template for Phase 75 pages.
- A method-selector summary table appears NEAR THE TOP (before the diagram in `outlier-detection.md`, after the diagram in `clustering.md`) — choose whichever order is clearer per page. For pages with ≥3 distinct methods, put the table before the diagram.
- Non-exec'd code block immediately before the exec'd block shows the "what you'd call" syntax.
- Admonitions scattered through sections, NOT batched at the end.
- "See also" is `## See also` (plain `##`, not numbered). Bullet list format. `## References` comes after.
- `clustering.md` uses the existing `Fdata` class briefly; the thin pages need not — plain numpy calls are standard.
- The `fast()` pattern from `docs_fig.py` must gate expensive permutation parameters: `n_perm=fast(999, 19)`.

---

## 2. Existing Thin-Page Content to Preserve

### 2.1 `functional-time-series.md`

**Already correct and to preserve:**
- The FTSM mathematical intro (mean + FPCA decomposition, score AR forecast equations)
- The diagram link
- The `ftsm` API parameter table and return-key table (all 7 keys are correct)
- The `ftsm_forecast` parameter table (correct: `h=1` default)
- The `stationarity_test` parameter table (correct: `n_perm=999, seed=42`)
- The three statistical references
- The existing exec'd fence (it runs correctly: `ftsm`, `ftsm_forecast`, `stationarity_test`)

**Requires correction:**
1. `ftsm_update` signature in the "Additional Functions" table: page shows `ftsm_update(data, argvals, new_obs, ncomp=3)`. Actual binding signature is `ftsm_update(data, new_curve, argvals, ncomp=3)` — `new_curve` (2D array) is the SECOND argument, before `argvals`. [VERIFIED: src/fts_mod.rs:207]
2. `functional_acf` / `functional_pacf` signatures: the page shows `functional_acf(data, argvals, lags, seed=42)`. Actual signature is `functional_acf(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)` — the parameter is `max_lag` (not `lags`), there is NO `lags` parameter, and `n_sim` and `ci` are new parameters not shown on the page. [VERIFIED: src/fts_mod.rs:297]
3. `functional_acf` and `functional_pacf` return dict: page omits the return structure entirely for these functions. Actual return: dict with keys `lags` (int64 1D), `acf` (1D), `pacf` (1D), `upper_band` (1D). [VERIFIED: src/fts_mod.rs:315-320]
4. `ftsm` return dict: page omits the `ar_models` key. Actual return has 7 keys: `mean (m,)`, `rotation (m, ncomp)`, `scores (n, ncomp)`, `fitted (n, m)`, `weights (m,)`, `ncomp (int)`, **`ar_models` (list of dicts, each with `order`, `phi`, `sigma2`)**. [VERIFIED: src/fts_mod.rs:69-86]
5. `spectral_density` return: page shows `spectral_density(data, argvals, freq)` returning an unnamed array. Actual: `spectral_density(data, argvals, bandwidth=None)` returning a dict with keys `freqs (N,)`, `re (list of N (m,m) arrays)`, `im (list of N (m,m) arrays)`, `m (int)`, `n_curves (int)`, `bandwidth (int)`. It does NOT accept a single frequency; it returns ALL Fourier frequencies. [VERIFIED: src/fts_mod.rs:538-575]
6. `dpca` return: page shows `dpca(data, argvals, ncomp=3, order=1)` — there is NO `order` parameter. Actual: `dpca(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)`. Return dict has 7 keys: `filters (list of ncomp arrays)`, `scores (N-2L, ncomp)`, `eigenvalues (list of ncomp arrays)`, `n_freqs`, `filter_lag`, `ncomp`, `valid_range (tuple)`. [VERIFIED: src/fts_mod.rs:646-658]
7. `dpca_reconstruct` return: page shows same as `dpca`. Actual: `dpca_reconstruct` returns ALL `dpca` keys PLUS `fitted_reconstruction (N-2L, m)` and `reconstruction_error (ncomp,)`. [VERIFIED: src/fts_mod.rs:694-718]
8. `long_run_covariance` signature: page shows `long_run_covariance(data, argvals, bandwidth=1.0)`. Actual default is `bandwidth=None` (auto-selects ⌊N^{1/3}⌋), not 1.0. Return keys: `cov_matrix (m, m)`, `m (int)`, `bandwidth (int)`, `n_curves (int)`. [VERIFIED: src/fts_mod.rs:471-496]

**Missing sections (to add):**
- "When to use" decision section (FTSM vs DPCA vs FPLSR; stationary vs non-stationary)
- `functional_acf` / `functional_pacf` worked examples (currently not in any fence)
- `fplsr` worked example (currently not in any fence)
- `long_run_covariance` brief API note
- Parameter selection guidance: how to choose `ncomp` (inspect `weights` from `ftsm`)
- Result interpretation section (how to read `ar_models`, what `upper_band` means)
- ≥1 `html="1"` exec'd matplotlib figure (ACF plot or forecast vs. original is natural)
- "See also" block

---

### 2.2 `density-fda.md`

**Already correct and to preserve:**
- The LQD mathematical intro (quantile function, LQD formula, Wasserstein barycenter concept)
- The diagram link
- `normalize_density` API table (correct: two params, returns 1D)
- `lqd_transform` basic signature (correct: `density, argvals`)
- `wasserstein_barycenter` API table (correct: `density_matrix (n,m)`, optional weights)
- `lqd_fpca` 6-key return dict (all 6 keys: `mean, singular_values, loadings, scores, fve, ncomp`)
- The two statistical references

**Requires correction:**
1. `inverse_lqd` signature: page shows `inverse_lqd(lqd, argvals)` (two params). Actual binding takes THREE arguments: `inverse_lqd(psi, t_grid, target_argvals)` — the quantile grid must be provided separately from the target reconstruction grid. [VERIFIED: src/density_fda_mod.rs:133]
2. `lqd_transform` optional parameter: page omits `n_quantile_pts`. Actual signature is `lqd_transform(density, argvals, n_quantile_pts=None)` where `n_quantile_pts` controls the quantile grid resolution (default `max(m, 101)`). [VERIFIED: src/density_fda_mod.rs:91]
3. `lqd_fpca` has an optional `n_quantile_pts=None` parameter not shown on the page. [VERIFIED: src/density_fda_mod.rs:236]
4. The page prose states `lqd_transform` returns values on the "unconstrained L² representation space" without clarifying that the OUTPUT GRID is the UNIFORM QUANTILE GRID `(n_q,)`, NOT the original `argvals` grid. This must be clarified: you cannot directly compare LQD output to the input `argvals` grid. The `inverse_lqd` call requires passing this `t_grid` explicitly. [VERIFIED: src/density_fda_mod.rs:83]

**Missing sections (to add):**
- "When to use" decision section (when densities appear as data; contrast with standard FPCA of raw curves)
- `inverse_lqd` worked example (the page never shows reconstruction — needed for "round-trip" proof)
- `wasserstein_barycenter` worked example (the page mentions it in intro but the only fence skips it)
- Parameter selection guidance: `ncomp` selection via `fve` cumulative variance
- Result interpretation: how to read LQD loadings (modes of density shape variation)
- ≥1 `html="1"` exec'd matplotlib figure (overlay of original densities + barycenter, or LQD FPCA score plot)
- "See also" block

---

### 2.3 `multi-domain.md`

**Already correct and to preserve:**
- The MFPCA mathematical intro (joint variance maximization, score formula)
- The diagram link
- `mfpca` parameter table (variables as list, ncomp, weighted)
- `mfpca` return-key table (all 6 keys: `scores, eigenfunctions, eigenvalues, means, scales, grid_sizes`)
- The `!!! warning "Pass a list, not a stacked array"` admonition — keep verbatim
- The `len(result['eigenvalues'])` note for getting component count — keep verbatim
- The two statistical references

**Requires correction:**
1. `dense_flmm` and `multi_famm` are described as accepting a `PyMultiFunData` handle (the page says `multi_fdata_from_components` returns "a `PyMultiFunData` opaque handle usable as input to `dense_flmm` and `multi_famm`"). This is **WRONG in fdars-core 0.33**: both `dense_flmm` and `multi_famm` take plain numpy arrays, NOT a `PyMultiFunData` handle. `PyMultiFunData` is a standalone container — it has no function that consumes it. [VERIFIED: src/famm_mod.rs:96-300, src/multi_fdata_mod.rs:18]
2. `dense_flmm` module: page references `fdars.famm` without showing the import path. The function is in `fdars.famm`, not in `fdars.multi_fdata`. [VERIFIED: src/famm_mod.rs:306-310]
3. `dense_flmm` return dict: page says "14-key dict" but doesn't list the keys. Actual 14 keys: `sigma2_eps (float)`, `ncomp (int)`, `n_subjects (int)`, `n_iter (int)`, `converged (bool)`, `mean_function (m,)`, `random_variance (m,)`, `sigma2_u (ncomp,)`, `sigma2_slope (ncomp,)`, `eigenvalues (ncomp,)`, `beta_functions (p, m)`, `random_effects (n_subjects, m)`, `fitted (n_total, m)`, `residuals (n_total, m)`. [VERIFIED: src/famm_mod.rs:29-51]
4. `multi_famm` return dict: page says "returns a dict" without structure. Actual 4-key dict: `n_dims (int)`, `stacked_fitted (n_total*n_dims, m)`, `stacked_residuals (n_total*n_dims, m)`, `components (list of 14-key dict — same as dense_flmm)`. [VERIFIED: src/famm_mod.rs:290-299]
5. `multi_famm` signature: page shows it as taking a `PyMultiFunData` handle. Actual: `multi_famm(data_list, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10)` — `data_list` is a Python list of 2D numpy arrays. [VERIFIED: src/famm_mod.rs:241]
6. `mfpca` `ncomp` parameter: page shows `ncomp=5` as default. Actual Rust signature: `ncomp: usize` — the default appears to be set from `MfpcaConfig::default()`. Based on reading spm_mod.rs lines 909-912, `config.ncomp = ncomp` after `MfpcaConfig::default()`, and the Python binding wraps it with signature `(variables, ncomp=5, weighted=True)`. The page shows `ncomp=5` correctly. [VERIFIED: src/spm_mod.rs:882-913]

**Missing sections (to add):**
- "When to use" decision section (MFPCA vs per-variable FPCA; FLMM vs standard regression; when grids differ across variables)
- `dense_flmm` worked example (currently no exec fence for FLMM at all)
- `multi_famm` worked example
- Parameter selection guidance: how to choose `ncomp` in `mfpca` (inspect `eigenvalues`)
- Result interpretation: reading `eigenfunctions` list (per-variable loadings), reading `stacked_fitted`
- ≥1 `html="1"` exec'd matplotlib figure (MFPCA scores scatter across 2 components is natural)
- "See also" block

---

### 2.4 `shapelets.md`

**Already correct and to preserve:**
- The shapelet mathematical intro (information-gain based discovery, minimum-distance feature)
- The diagram link
- `shapelet_transform_fit` API table (params: `data, labels, quality, seed`)
- `PyShapeletFit` opaque handle description (`.n_shapelets`, `.n_train`)
- `shapelet_transform` API table (correct: takes `fit` handle + new data)
- `shapelet_classifier_fit` API table (params: data, labels, quality, classifier, k)
- `PyShapeletClassifierFit` attributes listed (`.train_accuracy`, `.predict`, `.classes`, `.n_classes`)
- The GAK mathematical intro (alignment kernel formula)
- The GAK API reference table (sigma_gak, gak, gak_gram_matrix, gak_gram_train, gak_gram_predict)
- All three statistical references

**Requires correction:**
1. `shapelet_transform_fit` default `seed`: page shows `seed=0`, which is correct. But the full signature is also missing `min_length=3, max_length=0, max_candidates=10000, max_shapelets=0` — these parameters are real and matter for controlling the search space. The page lists only `quality` and `seed`. [VERIFIED: src/shapelet_mod.rs:276-280]
2. `shapelet_classifier_fit` signature: page shows `shapelet_classifier_fit(data, labels, quality="info_gain", classifier="knn", k=1)`. Actual full signature includes `min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality="info_gain", seed=0, classifier="knn", k=1, ncomp=None`. The `ncomp` parameter for PCA pre-reduction of features is not mentioned anywhere on the page. [VERIFIED: src/shapelet_mod.rs:386-389]
3. `discover_shapelets` return: page says "Returns a list of 1D numpy arrays — the raw shapelet subsequences." Actual: `discover_shapelets` returns a DICT with keys `n_shapelets (int)`, `quality (str)` — NOT a list of arrays. To get the actual shapelet arrays, use `shapelet_transform_fit` and access `.n_shapelets`. [VERIFIED: src/shapelet_mod.rs:211-244]
4. `shapelet_distance` return: page shows "Returns the minimum-distance match... as a scalar float." Actual: returns a `tuple of (float, int)` — `(min_distance, best_offset)`. [VERIFIED: src/shapelet_mod.rs:462-466]
5. `gak_gram_train` / `gak_gram_predict`: page's table shows `gak_gram_train(data, sigma=None)` returns `PyGakGramTrain` — correct. But `gak_gram_predict` is listed as `gak_gram_predict(train_handle, new_data)` returning `(n_test, n_train)` — also correct. The page notes "Pass `sigma=None` to any function to use the automatic `sigma_gak` heuristic" which is correct. These are fine as-is.

**Missing sections (to add):**
- "When to use" decision section (shapelets vs. elastic distances vs. FPCA features for classification)
- `discover_shapelets` corrected usage (return is a summary dict, not raw shapelet arrays)
- `shapelet_distance` corrected usage (returns tuple, not scalar)
- Search space parameter guidance (`min_length`, `max_length`, `max_candidates` control quality/speed tradeoff)
- `ncomp` parameter for `shapelet_classifier_fit` (optional PCA pre-reduction)
- GAK practical example (SVM with precomputed kernel)
- Result interpretation: how to interpret `.train_accuracy`, how to use `.predict()`
- ≥1 `html="1"` exec'd matplotlib figure (shapelet overlay on training curves, or distance feature distribution)
- "See also" block

---

### 2.5 `advanced-clustering.md`

**Already correct and to preserve:**
- The intro paragraph (four methods and their targeting: DBSCAN-FD, KCFC, FunFEM, Align-and-Cluster)
- The diagram link
- `dbscan_fd` full API table (params: `eps, min_points`; return keys: `cluster, n_clusters, n_noise, distances`)
- `kcfc_cluster` full API table (params: `k, ncomp, max_iter, seed`; return keys: `cluster, reconstruction_errors, iterations, converged`)
- The existing exec'd fence (correct and runnable)
- All three statistical references

**Requires correction:**
1. `funfem_cluster` in the "Additional Clustering Functions" table: the page gives description only. Actual signature: `funfem_cluster(data, argvals, k=2, ncomp=10, p_disc=0, max_iter=50, tol=1e-6, seed=42)` and return dict is 6 keys: `cluster (n,)`, `membership (n, k)`, `disc_subspace (ncomp_eff, p_disc_eff)`, `log_likelihood (float)`, `iterations (int)`, `converged (bool)`. The `p_disc=0` auto-selects `min(k-1, ncomp_eff)`. [VERIFIED: src/clustering_mod.rs:441-474]
2. `align_cluster_fd` in the "Additional Clustering Functions" table: page says "returns `templates` (list of 1D arrays)". Actual return dict has 5 keys: `cluster (n,)`, `templates (list of k 1D arrays)`, `distances (n, k)`, `iterations (int)`, `converged (bool)`. Also the full signature is `align_cluster_fd(data, argvals, k=2, max_iter=20, seed=42, use_amplitude_only=True, elastic_lambda=0.0, karcher_max_iter=15, karcher_tol=1e-4)`. The `use_amplitude_only` parameter (default True) is not mentioned anywhere on the page. [VERIFIED: src/clustering_mod.rs:512-551]
3. `dbscan_fd` cluster labels: page says "-1 indicates a noise point, 0..k-1 are cluster ids" — this is correct. But the cluster array dtype is `int64` (not plain int) because negative -1 requires signed type. The page does not specify dtype; add a note. [VERIFIED: src/clustering_mod.rs:328-338]
4. The current exec'd fence uses `kcfc` return key `kfc['cluster']` shape — this is correct. But `reconstruction_errors` key is not used in any fence; it is the primary diagnostic for KCFC and must appear in a worked example.

**Missing sections (to add):**
- "When to use" decision section (DBSCAN-FD vs KCFC vs FunFEM vs align-and-cluster vs basic k-means)
- `funfem_cluster` full worked example with membership inspection
- `align_cluster_fd` worked example with template overlay
- `eps` parameter selection guidance for DBSCAN-FD (using `distances` matrix from the result)
- KCFC `reconstruction_errors` interpretation (use as cluster membership confidence)
- FunFEM `membership` interpretation (probabilistic soft assignments unlike KCFC)
- ≥1 `html="1"` exec'd matplotlib figure (DBSCAN noise-flagging visualization, or KCFC cluster-separated plot)
- "See also" block

---

## 3. Exact API Surface — Per Page

All function names, parameter names, defaults, and return keys are [VERIFIED] by reading the Rust binding source this session.

### 3.1 `functional-time-series.md` — `fdars.fts` submodule

**Module:** `from fdars.fts import ...`

**Registered functions** [VERIFIED: src/fts_mod.rs:725-740]:
- `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr`
- `spectral_density`, `dpca`, `dpca_reconstruct`
- `functional_acf`, `functional_pacf`, `functional_difference`
- `stationarity_test`, `long_run_covariance`

**`ftsm(data, argvals, ncomp=3)`** [VERIFIED: src/fts_mod.rs:47-58]
- Returns dict (7 keys): `mean (m,)`, `rotation (m, ncomp)`, `scores (n, ncomp)`, `fitted (n, m)`, `weights (m,)`, `ncomp (int)`, `ar_models (list of dict{order, phi, sigma2})`
- `ncomp` clamped internally to `min(ncomp, n-1, m)` — never raises if ncomp too large

**`ftsm_forecast(data, argvals, h=1, ncomp=3)`** [VERIFIED: src/fts_mod.rs:115-132]
- Returns dict (2 keys): `forecast (h, m)`, `h (int)`

**`ftsm_forecast_multistep(data, argvals, h=5, ncomp=3)`** [VERIFIED: src/fts_mod.rs:160-177]
- Returns dict (2 keys): `forecast (h, m)`, `h (int)`
- At h=1, output is bit-identical to `ftsm_forecast`

**`ftsm_update(data, new_curve, argvals, ncomp=3)`** [VERIFIED: src/fts_mod.rs:207]
- `new_curve`: 2D array `(k_new, m)` — NOT `new_obs` and NOT a 1D array
- `new_curve` is the SECOND argument, before `argvals`
- Returns: same 7-key dict as `ftsm`, with scores extended to `(n+k_new, ncomp)`

**`fplsr(data, argvals, ncomp=3)`** [VERIFIED: src/fts_mod.rs:248-264]
- Returns dict (3 keys): `forecast (1, m)`, `fitted (n-1, m)`, `ncomp (int)`
- One-step-ahead forecast; requires `n_obs >= 3`

**`functional_acf(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)`** [VERIFIED: src/fts_mod.rs:297]
- `max_lag=None` → `min(20, N/4)` auto-selected
- Returns dict (4 keys): `lags (int64 1D)`, `acf (1D)`, `pacf (1D)`, `upper_band (1D)`

**`functional_pacf(data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42)`** [VERIFIED: src/fts_mod.rs:353]
- Same signature and return dict as `functional_acf`

**`functional_difference(data)`** [VERIFIED: src/fts_mod.rs:398-405]
- Takes ONLY `data` (no `argvals`)
- Returns naked 2D array `(n-1, m)` — NOT a dict
- `lag=1` is fixed (not a parameter)

**`stationarity_test(data, argvals, n_perm=999, seed=42)`** [VERIFIED: src/fts_mod.rs:430-446]
- Returns dict (3 keys): `statistic (float)`, `p_value (float)`, `n_perm (int)`

**`long_run_covariance(data, argvals, bandwidth=None)`** [VERIFIED: src/fts_mod.rs:471-496]
- `bandwidth=None` auto-selects ⌊N^{1/3}⌋; `bandwidth=0` returns sample covariance C_0
- Returns dict (4 keys): `cov_matrix (m, m)`, `m (int)`, `bandwidth (int)`, `n_curves (int)`

**`spectral_density(data, argvals, bandwidth=None)`** [VERIFIED: src/fts_mod.rs:538-575]
- `bandwidth=0` raises ValueError (unlike `long_run_covariance`)
- Returns dict (6 keys): `freqs (N,)`, `re (list of N arrays, each (m, m))`, `im (list of N arrays, each (m, m))`, `m (int)`, `n_curves (int)`, `bandwidth (int)`
- To get 3D: `np.stack(result["re"])` → `(N, m, m)`

**`dpca(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)`** [VERIFIED: src/fts_mod.rs:646-658]
- Returns dict (7 keys): `filters (list of ncomp arrays, each (2L+1, m))`, `scores (N-2L, ncomp)`, `eigenvalues (list of ncomp arrays, each (N,))`, `n_freqs (int)`, `filter_lag (int)`, `ncomp (int)`, `valid_range (tuple(int, int))`

**`dpca_reconstruct(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)`** [VERIFIED: src/fts_mod.rs:694-718]
- Returns: all 7 keys from `dpca` PLUS `fitted_reconstruction (N-2L, m)` AND `reconstruction_error (ncomp,)`

**R-methods-not-in-Python note for functional-time-series.md:**
- Cointegration testing for functional time series is not exposed in `fdars`
- Hilbert-space-valued AR(p) fitting beyond what `ftsm` auto-selects is not exposed
- `functional_difference` is lag-1 only; higher-order differencing requires chaining calls

---

### 3.2 `density-fda.md` — `fdars.density_fda` submodule

**Module:** `from fdars.density_fda import ...`

**Registered functions** [VERIFIED: src/density_fda_mod.rs:273-280]:
- `normalize_density`, `lqd_transform`, `inverse_lqd`, `wasserstein_barycenter`, `lqd_fpca`

**`normalize_density(vals, argvals)`** [VERIFIED: src/density_fda_mod.rs:42-53]
- `vals`: non-negative density values `(m,)` — need not integrate to 1
- Returns 1D array `(m,)` normalized so ∫f dt ≈ 1
- Raises `ValueError` if any value is negative or integral is effectively zero

**`lqd_transform(density, argvals, n_quantile_pts=None)`** [VERIFIED: src/density_fda_mod.rs:91-106]
- `density`: STRICTLY positive values `(m,)` — stricter than `normalize_density`
- `n_quantile_pts=None` → `max(m, 101)` quantile grid points
- Returns 1D array `(n_q,)` on the UNIFORM QUANTILE GRID — shape `n_q`, NOT `m`

**`inverse_lqd(psi, t_grid, target_argvals)`** [VERIFIED: src/density_fda_mod.rs:133-149]
- THREE positional arguments (no defaults)
- `psi`: LQD values `(n_q,)` on quantile grid
- `t_grid`: uniform quantile grid `(n_q,)` corresponding to `psi` (i.e. `np.linspace(0, 1, n_q)`)
- `target_argvals`: the reconstruction grid `(m,)` where you want the density back
- Returns 1D array `(m,)` — reconstructed density on `target_argvals`

**`wasserstein_barycenter(density_matrix, argvals, weights=None)`** [VERIFIED: src/density_fda_mod.rs:179-196]
- `density_matrix`: `(n, m)` — each row must be a valid probability density (non-negative, integrating to 1)
- `weights`: non-negative `(n,)` summing to 1; `None` → uniform
- Returns 1D array `(m,)` — the Wasserstein barycenter density

**`lqd_fpca(density_matrix, argvals, ncomp=3, n_quantile_pts=None)`** [VERIFIED: src/density_fda_mod.rs:236-266]
- `density_matrix`: `(n, m)` — each row must be STRICTLY positive density
- Returns dict (6 keys): `mean (n_q,)`, `singular_values (k,)`, `loadings (n_q, k)`, `scores (n, k)`, `fve (k,)`, `ncomp (int)`
- Note: `mean` and `loadings` are on the QUANTILE grid `(n_q,)`, not `(m,)`

**R-methods-not-in-Python note for density-fda.md:**
- Fréchet regression on density responses (via Wasserstein geodesics) is in `fdars.frechet` — cross-reference there
- Density-on-scalar regression is not directly exposed beyond what `frechet_global_reg` provides

---

### 3.3 `multi-domain.md` — `fdars.spm` (mfpca) and `fdars.famm` (dense_flmm, multi_famm)

**Module:** `from fdars.spm import mfpca` / `from fdars.famm import dense_flmm, multi_famm`

**`mfpca(variables, ncomp=5, weighted=True)`** [VERIFIED: src/spm_mod.rs:881-948]
- `variables`: Python **list** of 2D arrays `(n, m_p)` — one per domain, may have different `m_p`
- `ncomp=5` default (NOT 3)
- `weighted=True` normalizes each variable by 1/std before joint SVD
- Returns dict (6 keys): `scores (n, ncomp)`, `eigenfunctions (list of P arrays, each (m_p, ncomp))`, `eigenvalues (ncomp,)`, `means (list of P arrays, each (m_p,))`, `scales (P,)`, `grid_sizes (list of P ints)`
- Raises `ValueError` if any element of `variables` is not a 2D float64 array
- Note: there is NO `n_comp` key in the result — get component count from `len(result['eigenvalues'])`

**`dense_flmm(data, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10)`** [VERIFIED: src/famm_mod.rs:95-123]
- Takes plain numpy arrays — NOT a `PyMultiFunData` handle
- `data`: `(n_total, m)` — all observations stacked
- `subject_ids`: `(n_total,)` dtype int64, 0-based curve-to-subject mapping
- Returns dict (14 keys): `sigma2_eps (float)`, `ncomp (int)`, `n_subjects (int)`, `n_iter (int)`, `converged (bool)`, `mean_function (m,)`, `random_variance (m,)`, `sigma2_u (ncomp,)`, `sigma2_slope (ncomp,)`, `eigenvalues (ncomp,)`, `beta_functions (p, m)` [p=0 if no covariates], `random_effects (n_subjects, m)`, `fitted (n_total, m)`, `residuals (n_total, m)`

**`multi_famm(data_list, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10)`** [VERIFIED: src/famm_mod.rs:242-299]
- `data_list`: Python **list** of 2D numpy arrays — NOT a `PyMultiFunData` handle
- All arrays must share the same `n_total` (rows) and same `m` (columns)
- Returns dict (4 keys): `n_dims (int)`, `stacked_fitted (n_total*n_dims, m)`, `stacked_residuals (n_total*n_dims, m)`, `components (list of dict)` — each component dict has the same 14 keys as `dense_flmm`

**`multi_fdata_from_components(data_list, argvals_list)`** — `fdars.multi_fdata` submodule [VERIFIED: src/multi_fdata_mod.rs:62-80]
- Returns `PyMultiFunData` opaque handle with `.n_obs` and `.n_components` accessors
- As of fdars-core 0.33, NO FAMM or MFPCA function accepts this handle — it is a standalone container only

**R-methods-not-in-Python note for multi-domain.md:**
- The full `multiFAMM` R package's tensor-product basis approach is not directly replicated; `multi_famm` uses per-dimension FLMM fitting instead

---

### 3.4 `shapelets.md` — `fdars.shapelet` and `fdars.metric`

**Module:** `from fdars.shapelet import ...` / `from fdars.metric import gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict`

**Registered in `fdars.shapelet`** [VERIFIED: src/shapelet_mod.rs:472-480]:
- `discover_shapelets`, `shapelet_transform_fit`, `shapelet_transform`, `shapelet_classifier_fit`, `shapelet_distance`
- Classes: `PyShapeletFit`, `PyShapeletClassifierFit`

**`discover_shapelets(data, labels, min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality="info_gain", seed=0)`** [VERIFIED: src/shapelet_mod.rs:212-244]
- Returns dict (2 keys): `n_shapelets (int)`, `quality (str)` — NOT a list of arrays
- `max_length=0` → uses full series length
- `max_candidates=0` → exhaustive search
- `max_shapelets=0` → auto: `min(10*n, 1000)`

**`shapelet_transform_fit(data, labels, min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality="info_gain", seed=0)`** [VERIFIED: src/shapelet_mod.rs:276-307]
- `labels`: `(n,)` dtype int64 — must be non-negative integers
- `quality`: `"info_gain"` or `"f_statistic"` — other strings raise `ValueError`
- Returns `PyShapeletFit` opaque handle with `.n_shapelets` and `.n_train` properties

**`shapelet_transform(fit, data)`** [VERIFIED: src/shapelet_mod.rs:335-347]
- Returns 2D array `(n_new, K)` — K = `fit.n_shapelets`

**`shapelet_classifier_fit(data, labels, min_length=3, max_length=0, max_candidates=10000, max_shapelets=0, quality="info_gain", seed=0, classifier="knn", k=1, ncomp=None)`** [VERIFIED: src/shapelet_mod.rs:386-428]
- `classifier`: `"knn"` or `"lda"` — other strings raise `ValueError`
- `k=1` default (NOT k=3 — the page shows `k=3` in the example; that's fine as a usage example, but the DEFAULT is k=1)
- `ncomp=None` → no PCA pre-reduction of features; `ncomp=K` means reduce to K principal components before classifying
- Returns `PyShapeletClassifierFit` opaque handle with:
  - `.n_shapelets` — number of shapelets
  - `.train_accuracy` — training accuracy (NOT a generalization estimate)
  - `.classes` — sorted unique labels as int64 numpy 1D
  - `.n_classes` — number of classes
  - `.predict(new_data)` method → `(n_new,)` int64 predicted labels

**`shapelet_distance(shapelet_z, series, best_so_far=inf)`** [VERIFIED: src/shapelet_mod.rs:457-466]
- `shapelet_z`: pre-z-normalized shapelet subsequence `(L,)` — NOT a raw subsequence
- `series`: raw series `(m,)` with `m >= L`; per-window z-normalization done internally
- Returns `tuple (float, int)` — `(min_distance, best_offset)` — NOT a scalar float

**GAK functions in `fdars.metric`** [VERIFIED: src/metric_mod.rs:87-198]:
- `gak(x, y, sigma)` → `float` — single kernel value between two 1D curves
- `sigma_gak(data)` → `float` — heuristic bandwidth (median pairwise distance)
- `gak_gram_matrix(data, sigma=None)` → `(n, n)` symmetric PSD Gram matrix, unit diagonal
- `gak_gram_train(data, sigma=None)` → `PyGakGramTrain` opaque handle
- `gak_gram_predict(train, new_data)` → `(n_test, n_train)` Gram matrix

---

### 3.5 `advanced-clustering.md` — `fdars.clustering` submodule

**Module:** `from fdars.clustering import ...`

**Registered functions** [VERIFIED: src/clustering_mod.rs:554-567]:
- `kmeans_fd`, `fuzzy_cmeans_fd`, `gmm_cluster`, `silhouette_score`, `calinski_harabasz`
- `silhouette_score_data`, `calinski_harabasz_data`
- `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd`

**`dbscan_fd(data, argvals, eps=0.5, min_points=3)`** [VERIFIED: src/clustering_mod.rs:311-338]
- Returns dict (4 keys): `cluster (n,)` int64 (-1=noise, 0..k-1=clusters), `n_clusters (int)`, `n_noise (int)`, `distances (n, n)` pairwise L2 matrix
- `distances` key is useful for eps selection: scan histogram of distances to find gap

**`kcfc_cluster(data, argvals, k=2, ncomp=3, max_iter=50, seed=42)`** [VERIFIED: src/clustering_mod.rs:372-401]
- Returns dict (4 keys): `cluster (n,)` int64, `reconstruction_errors (n, k)` — per-observation per-cluster reconstruction error, `iterations (int)`, `converged (bool)`
- The `reconstruction_errors` matrix is the KCFC-specific diagnostic: `result["reconstruction_errors"][i, c]` = FPCA reconstruction error of observation `i` when assigned to cluster `c`

**`funfem_cluster(data, argvals, k=2, ncomp=10, p_disc=0, max_iter=50, tol=1e-6, seed=42)`** [VERIFIED: src/clustering_mod.rs:441-474]
- `ncomp=10` default (NOT 3) — global FPC components before discriminant projection
- `p_disc=0` → auto-select `min(k-1, ncomp_eff)` for discriminative subspace dimension
- Returns dict (6 keys): `cluster (n,)` int64, `membership (n, k)`, `disc_subspace (ncomp_eff, p_disc_eff)`, `log_likelihood (float)`, `iterations (int)`, `converged (bool)`
- `membership` rows sum to 1 (soft probabilistic assignments)

**`align_cluster_fd(data, argvals, k=2, max_iter=20, seed=42, use_amplitude_only=True, elastic_lambda=0.0, karcher_max_iter=15, karcher_tol=1e-4)`** [VERIFIED: src/clustering_mod.rs:512-551]
- `use_amplitude_only=True` → amplitude-only (shape-invariant) elastic distance
- `use_amplitude_only=False` → full elastic distance (penalized by `elastic_lambda`)
- Returns dict (5 keys): `cluster (n,)` int64, `templates (list of k 1D arrays, each (m,))`, `distances (n, k)`, `iterations (int)`, `converged (bool)`

---

## 4. API Discrepancy Summary (Highest-Priority Corrections)

| Page | Discrepancy | Severity |
|------|-------------|----------|
| `functional-time-series.md` | `ftsm_update` signature wrong: page shows `(data, argvals, new_obs, ncomp)`, actual is `(data, new_curve, argvals, ncomp)` | HIGH — calling fence will pass wrong type |
| `functional-time-series.md` | `functional_acf`/`pacf` params: page shows `lags`, actual is `max_lag`; `n_sim`, `ci` missing | HIGH — `lags` kwarg raises TypeError |
| `functional-time-series.md` | `spectral_density` signature: page shows `(data, argvals, freq)`, actual is `(data, argvals, bandwidth=None)` returning full spectrum not a single-freq value | HIGH — completely wrong usage |
| `functional-time-series.md` | `dpca` has no `order` param; page shows `order=1`; actual params are `bandwidth`, `filter_lag` | HIGH — `order` raises TypeError |
| `functional-time-series.md` | `ftsm` return dict missing `ar_models` key; `long_run_covariance` default bandwidth shown as 1.0, actual None | MEDIUM |
| `density-fda.md` | `inverse_lqd` takes 3 args: `psi, t_grid, target_argvals`; page shows only 2 | HIGH — calling with 2 args raises TypeError |
| `density-fda.md` | `lqd_transform` output is on quantile grid `(n_q,)` not `(m,)`; prose does not clarify | MEDIUM — leads to misuse in downstream code |
| `density-fda.md` | `lqd_fpca` has `n_quantile_pts=None` param not shown; `lqd_transform` same | LOW — optional param only |
| `multi-domain.md` | `dense_flmm` and `multi_famm` do NOT accept `PyMultiFunData`; page says they do | HIGH — would raise TypeError in fdars-core 0.33 |
| `multi-domain.md` | `multi_famm` takes `data_list` (list of arrays), not a `PyMultiFunData`; page implies handle input | HIGH — calling fence will fail |
| `multi-domain.md` | `dense_flmm` and `multi_famm` return dicts undocumented; page says "14-key dict" without listing keys | MEDIUM |
| `shapelets.md` | `discover_shapelets` returns dict `{n_shapelets, quality}`, not a list of arrays | HIGH — prose/example incorrect |
| `shapelets.md` | `shapelet_distance` returns `(float, int)` tuple, not scalar float | MEDIUM |
| `shapelets.md` | `shapelet_classifier_fit` has `ncomp=None` param not shown; default `k=1` (page shows `k=3` in example, which is valid as usage but default should be documented) | LOW |
| `advanced-clustering.md` | `funfem_cluster` and `align_cluster_fd` return dicts undocumented; `use_amplitude_only` param for `align_cluster_fd` not shown | MEDIUM |

---

## 5. Cross-Reference Targets ("See also" links per page)

Confirmed nav destinations from `docs/analyze/` directory listing [VERIFIED: docs/analyze/ directory].

**`functional-time-series.md`** → See also:
- [Seasonal Analysis](seasonal-analysis.md) — periodic decomposition as complement to FTS forecasting
- [Functional Statistics](functional-statistics.md) — mean, covariance, and variance functions used inside FTSM
- [Clustering](clustering.md) — grouping time series by their score trajectories
- [Analyze index](index.md)
- (Optional) [Functional Time Series example](../examples/functional-time-series.md) — when Phase 76 ships; omit for now

**`density-fda.md`** → See also:
- [Fréchet Regression](../regression/frechet-regression.md) — regression when the response is a density (Wasserstein space)
- [Functional Statistics](functional-statistics.md) — standard FPCA and covariance for non-density functional data
- [Outlier Detection](outlier-detection.md) — detecting outlier densities
- [Analyze index](index.md)

**`multi-domain.md`** → See also:
- [Clustering](clustering.md) — cluster subjects using MFPCA scores as features
- [Functional Statistics](functional-statistics.md) — single-domain FPCA (the building block)
- [Outlier Detection](outlier-detection.md) — magnitude-shape outlier detection applicable to MFPCA scores
- [Analyze index](index.md)

**`shapelets.md`** → See also:
- [Clustering](clustering.md) — cluster by shapelet feature matrix rows
- [Advanced Clustering](advanced-clustering.md) — align-and-cluster as complement to shapelet classification
- [Distance Metrics](../represent/distance-metrics.md) — GAK cross-reference already on the page
- [Outlier Detection](outlier-detection.md) — anomaly detection complement
- [Analyze index](index.md)

**`advanced-clustering.md`** → See also:
- [Clustering](clustering.md) — basic k-means and fuzzy c-means as the baseline methods
- [GMM Clustering](gmm-clustering.md) — model-based clustering companion
- [Elastic Clustering](elastic-clustering.md) — elastic distance approach (related to `align_cluster_fd`)
- [Outlier Detection](outlier-detection.md) — DBSCAN-FD noise points as outlier candidates
- [Analyze index](index.md)

---

## 6. Worked-Example Data Strategy

### 6.1 docs_fig helper (unchanged from Phase 74)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.fts import ftsm_forecast

rng = np.random.default_rng(42)
n, m = 25, 30
t = np.linspace(0, 1, m)
data = np.array([np.sin(2 * np.pi * t + rng.uniform(0, 0.5)) + 0.1 * rng.standard_normal(m)
                 for _ in range(n)])

fc = ftsm_forecast(data, t, h=3, ncomp=3)
forecast = np.asarray(fc["forecast"])  # (3, 30)

f, ax = fig()
for xi in data[-5:]:
    ax.plot(t, xi, color="#6c757d", lw=0.8, alpha=0.5, label="_")
for k in range(3):
    ax.plot(t, forecast[k], lw=2.0,
            color=["#3f51b5", "#e8710a", "#198754"][k],
            label=f"h={k+1}")
ax.set(title="FTSM: 3-step forecast vs. recent history",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
print("FDARS_FENCE_OK")
```

For expensive parameters, use `fast()`:
```python
from docs_fig import fast
st = stationarity_test(data, t, n_perm=fast(999, 19), seed=42)
```

### 6.2 Real-dataset opportunities

[VERIFIED: docs/data/README.md]

| Page | Natural fit | Dataset | Shape | Loader | Notes |
|------|-------------|---------|-------|--------|-------|
| `functional-time-series.md` | Daily temperature curves treated as a time-ordered series of annual curves | `canadian_weather.csv` | 35 × 365 | `load_canadian_weather()` | Strong natural fit: 35 time steps, each a 365-point temperature curve. Fence must be quick — consider subsampling to 52 weekly means or taking a subset of stations for the fence |
| `density-fda.md` | NIR spectral bands as proxy densities | `tecator.csv` | 240 × 100 | `load_tecator()` | After normalization, NIR spectra can be treated as density-like shapes; weaker conceptual fit |
| `shapelets.md` | Phoneme spectral curves, 5-class classification | `phoneme.csv` | 400 × 256 | `load_phoneme()` | Strong fit: 5 phoneme classes, natural classification task; 256 pts × 400 obs may be slow for exhaustive shapelet search — use `max_candidates=500` or a 2-class subset |
| `advanced-clustering.md` | Sonar mine vs. rock spectral energy | `sonar.csv` | 208 × 60 | `load_sonar()` | 2-class version for KCFC/FunFEM clustering; 60 pts is fast |
| `multi-domain.md` | No strong real fit in current datasets (needs multiple co-observed functional variables per subject) | — | — | — | Use synthetic: simulate 2 variables per subject |

**Recommendation:** Use real datasets as Section 2+ examples after the synthetic Section 1 fence. Canadian weather at 35 × 365 is the strongest real-data argument for `functional-time-series`, but 365-column fences may be slow during the strict build — subsample to 52 weekly means (`data[:, ::7]`) to get 35 × 52 which is much faster. Test first.

### 6.3 Synthetic simulation pattern per page

Keep n small (15–25 observations), m small (20–50 grid points) for each fence.

**Functional time-series (minimal fence):**
```python exec="1" source="above"
import numpy as np
from fdars.fts import ftsm, stationarity_test
from docs_fig import fast

rng = np.random.default_rng(42)
n, m = 20, 30
t = np.linspace(0, 1, m)
data = np.array([np.sin(2 * np.pi * t + rng.uniform(0, 0.5)) + 0.1 * rng.standard_normal(m)
                 for _ in range(n)])

fit = ftsm(data, t, ncomp=3)
st  = stationarity_test(data, t, n_perm=fast(999, 19), seed=42)

print(f"ncomp: {fit['ncomp']}")
print(f"ar_models: {[m['order'] for m in fit['ar_models']]}  (AR orders per component)")
print(f"stationarity p: {st['p_value']:.3f}")
print("FDARS_FENCE_OK")
```

**Density FDA (minimal fence with round-trip):**
```python exec="1" source="above"
import numpy as np
from fdars.density_fda import normalize_density, lqd_transform, inverse_lqd

rng = np.random.default_rng(42)
m = 50
t = np.linspace(0, 1, m)
raw = np.abs(np.sin(np.pi * t + 0.2)) + 0.01
norm = normalize_density(raw, t)       # (m,)
psi  = lqd_transform(norm, t)          # (n_q,) — quantile grid
n_q  = len(psi)
t_q  = np.linspace(0, 1, n_q)          # the quantile grid
recon = inverse_lqd(psi, t_q, t)       # back to (m,) on original grid

print(f"norm integral: {np.trapezoid(norm, t):.4f}")
print(f"psi shape: {psi.shape}  (quantile grid, != m={m})")
print(f"recon integral: {np.trapezoid(recon, t):.4f}")
print("FDARS_FENCE_OK")
```

**Multi-domain MFPCA (minimal fence):**
```python exec="1" source="above"
import numpy as np
from fdars.spm import mfpca

rng = np.random.default_rng(42)
n, m1, m2 = 20, 30, 25
t1 = np.linspace(0, 1, m1)
t2 = np.linspace(0, 1, m2)
V1 = np.array([np.sin(2 * np.pi * t1 + rng.uniform(0, 0.3)) for _ in range(n)])
V2 = np.array([np.cos(np.pi * t2 + rng.uniform(0, 0.3)) for _ in range(n)])

result = mfpca([V1, V2], ncomp=2)

print(f"scores shape: {np.asarray(result['scores']).shape}")  # (20, 2)
print(f"eigenfunctions: {[np.asarray(ef).shape for ef in result['eigenfunctions']]}")
print(f"n components: {len(result['eigenvalues'])}")
print("FDARS_FENCE_OK")
```

**Shapelets (minimal fence with prediction):**
```python exec="1" source="above"
import numpy as np
from fdars.shapelet import shapelet_transform_fit, shapelet_transform, shapelet_classifier_fit

rng = np.random.default_rng(42)
m = 40
t = np.linspace(0, 1, m)
n_per_class = 8
X_train = np.vstack([
    np.array([np.sin(2*np.pi*t + rng.uniform(-0.1, 0.1)) for _ in range(n_per_class)]),
    np.array([np.cos(2*np.pi*t + rng.uniform(-0.1, 0.1)) for _ in range(n_per_class)]),
])
y_train = np.array([0]*n_per_class + [1]*n_per_class, dtype=np.int64)

fit    = shapelet_transform_fit(X_train, y_train, max_candidates=200, seed=42)
X_feat = shapelet_transform(fit, X_train)
clf    = shapelet_classifier_fit(X_train, y_train, max_candidates=200, seed=42, classifier="lda")

print(f"n_shapelets: {fit.n_shapelets}")
print(f"feature matrix shape: {X_feat.shape}  (n_train, n_shapelets)")
print(f"train_accuracy: {clf.train_accuracy:.3f}")
print("FDARS_FENCE_OK")
```

**Advanced clustering (minimal fence with funfem):**
```python exec="1" source="above"
import numpy as np
from fdars.clustering import funfem_cluster, dbscan_fd

rng = np.random.default_rng(42)
n, m = 30, 40
t = np.linspace(0, 1, m)
X = np.vstack([
    np.array([np.sin(2*np.pi*t + rng.uniform(-0.2, 0.2)) for _ in range(15)]),
    np.array([np.cos(2*np.pi*t + rng.uniform(-0.2, 0.2)) for _ in range(15)]),
])

fem = funfem_cluster(X, t, k=2, ncomp=5, seed=42)
db  = dbscan_fd(X, t, eps=0.6, min_points=3)

print(f"funfem cluster labels: {np.asarray(fem['cluster']).tolist()[:6]} ...")
print(f"funfem membership[0]: {np.asarray(fem['membership'])[0].round(3).tolist()}")
print(f"dbscan n_clusters: {db['n_clusters']}  n_noise: {db['n_noise']}")
print("FDARS_FENCE_OK")
```

---

## 7. Common Pitfalls

### Pitfall 1: `inverse_lqd` called with wrong arguments
**What goes wrong:** `inverse_lqd(psi, argvals)` raises `TypeError: inverse_lqd() missing 1 required positional argument: 'target_argvals'`.
**Root cause:** The page shows the old 2-argument signature; the actual binding requires 3 arguments: `psi`, the quantile grid `t_grid`, and the target reconstruction grid.
**How to avoid:** `t_grid = np.linspace(0, 1, len(psi))` — the quantile grid is always uniform [0,1] with `n_q` points. Then call `inverse_lqd(psi, t_grid, original_argvals)`.

### Pitfall 2: LQD output grid mismatch
**What goes wrong:** `psi = lqd_transform(density, t)` returns an array of length `n_q` (default `max(m, 101)`), NOT length `m`. Passing `psi` directly back to a function expecting the original `(m,)` grid raises a shape error.
**Root cause:** The LQD transform operates in quantile space `[0,1]` with its own grid. The page does not clarify the output shape.
**How to avoid:** After `lqd_transform`, note that `len(psi) >= m`. Always pair `lqd_transform` with `inverse_lqd` using `t_grid = np.linspace(0, 1, len(psi))`.

### Pitfall 3: `multi_famm` / `dense_flmm` called with a `PyMultiFunData` handle
**What goes wrong:** `dense_flmm(mfd, subject_ids)` where `mfd` is a `PyMultiFunData` raises `TypeError` (the binding expects `PyReadonlyArray2`, not `PyMultiFunData`).
**Root cause:** The page incorrectly documents `PyMultiFunData` as input to FAMM functions. In fdars-core 0.33, `PyMultiFunData` is a standalone container only.
**How to avoid:** Pass `dense_flmm(data_2d_array, subject_ids)` or `multi_famm([V1, V2], subject_ids)` with raw 2D numpy arrays.

### Pitfall 4: `ftsm_update` arg order
**What goes wrong:** `ftsm_update(data, argvals, new_curve, ncomp=3)` — placing `argvals` before `new_curve` — processes `argvals` as the new curve matrix, raising a shape error.
**Root cause:** The page shows the wrong argument order.
**How to avoid:** `ftsm_update(data, new_curve, argvals, ncomp=3)` — `new_curve` is second.

### Pitfall 5: `spectral_density(data, argvals, freq)` — wrong usage
**What goes wrong:** Passing a frequency value as the third argument raises `TypeError` because the function has no `freq` parameter; `bandwidth` is the third (optional) parameter.
**Root cause:** The page describes `spectral_density` as accepting a target frequency, analogous to the R function. The Python binding returns ALL Fourier frequencies, not a single one.
**How to avoid:** Call `spectral_density(data, argvals)` and then index the `freqs` / `re` / `im` output lists to select the frequency of interest.

### Pitfall 6: `discover_shapelets` returns a dict, not shapelet arrays
**What goes wrong:** `for s in discover_shapelets(...)` raises `TypeError: cannot unpack dict`; or `np.vstack(discover_shapelets(...))` fails because the return is a 2-key dict.
**Root cause:** The page describes the return as "list of 1D numpy arrays — the raw shapelet subsequences."
**How to avoid:** `result = discover_shapelets(...)` gives `result['n_shapelets']` and `result['quality']`. To get raw shapelet arrays, use `shapelet_transform_fit` which stores shapelets internally in the `PyShapeletFit` handle.

### Pitfall 7: `shapelet_distance` returns a tuple, not a float
**What goes wrong:** `d = shapelet_distance(s, x)` → `d = (0.123, 14)` — unpacking as a scalar fails.
**Root cause:** The page says "returns... as a scalar float."
**How to avoid:** `dist, offset = shapelet_distance(s, x)` — the tuple is `(min_distance, best_start_index)`.

### Pitfall 8: `align_cluster_fd` with `use_amplitude_only=False` is slower
**What goes wrong:** Setting `use_amplitude_only=False` enables full elastic distance computation, which is significantly slower (may be impractical for n > 100 in a fence).
**Root cause:** The parameter is not documented on the page; users may accidentally set it to False.
**How to avoid:** Keep `use_amplitude_only=True` (the default) for fence examples. Add a `!!! warning` admonition noting the speed difference.

---

## 8. Code Examples

### FTS: ACF plot fence (html="1")

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
from fdars.fts import functional_acf

rng = np.random.default_rng(42)
n, m = 25, 30
t = np.linspace(0, 1, m)
data = np.array([np.sin(2 * np.pi * t + 0.3 * k / n) + 0.1 * rng.standard_normal(m)
                 for k in range(n)])

acf = functional_acf(data, t, max_lag=8, n_sim=fast(999, 99), seed=42)
lags = np.asarray(acf["lags"])
acf_vals = np.asarray(acf["acf"])
upper = np.asarray(acf["upper_band"])

f, ax = fig(figsize=(7.0, 3.6))
ax.bar(lags, acf_vals, color="#3f51b5", width=0.6, label="functional ACF")
ax.axhline(upper[0], color="#dc3545", ls="--", lw=1.4, label="95% band")
ax.set(title="Functional ACF of synthetic time series",
       xlabel="lag", ylabel="ACF statistic")
ax.legend()
print(render(f))
print("FDARS_FENCE_OK")
```

### Density FDA: round-trip + barycenter fence

```python exec="1" source="above"
import numpy as np
from fdars.density_fda import normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter, lqd_fpca

rng = np.random.default_rng(42)
m, n = 50, 12
t = np.linspace(0.01, 0.99, m)

raw = np.array([np.abs(np.sin(np.pi * t + rng.uniform(0, 0.5))) + 0.02 for _ in range(n)])
norms = np.array([normalize_density(raw[i], t) for i in range(n)])

psi_list = [lqd_transform(norms[i], t) for i in range(n)]
n_q = len(psi_list[0])
t_q = np.linspace(0, 1, n_q)
recon = inverse_lqd(psi_list[0], t_q, t)  # round-trip: density 0

bary = wasserstein_barycenter(norms, t)
fp = lqd_fpca(norms, t, ncomp=2)

print(f"norm integral (density 0): {np.trapezoid(norms[0], t):.4f}")
print(f"recon integral (round-trip): {np.trapezoid(recon, t):.4f}")
print(f"barycenter integral: {np.trapezoid(bary, t):.4f}")
print(f"lqd_fpca scores shape: {np.asarray(fp['scores']).shape}")
print("FDARS_FENCE_OK")
```

### Multi-domain: MFPCA + dense_flmm fence

```python exec="1" source="above"
import numpy as np
from fdars.spm import mfpca
from fdars.famm import dense_flmm

rng = np.random.default_rng(42)
n_subj, n_visits, m = 8, 3, 20
n_total = n_subj * n_visits
t = np.linspace(0, 1, m)

# MFPCA: 2 functional variables, different grid lengths
V1 = np.array([np.sin(2 * np.pi * t + rng.uniform(0, 0.3)) for _ in range(n_subj)])
V2 = np.array([np.cos(np.pi * t + rng.uniform(0, 0.3)) for _ in range(n_subj)])
mp = mfpca([V1, V2], ncomp=2)
print(f"mfpca scores shape: {np.asarray(mp['scores']).shape}")

# dense_flmm: longitudinal repeated-measures design
data = np.array([np.sin(2 * np.pi * t + rng.uniform(0, 0.3)) for _ in range(n_total)])
subject_ids = np.repeat(np.arange(n_subj, dtype=np.int64), n_visits)
flmm = dense_flmm(data, subject_ids, ncomp=2)
print(f"dense_flmm n_subjects: {flmm['n_subjects']}  converged: {flmm['converged']}")
print("FDARS_FENCE_OK")
```

### Advanced clustering: DBSCAN eps selection fence

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.clustering import dbscan_fd

rng = np.random.default_rng(42)
n, m = 25, 40
t = np.linspace(0, 1, m)
X = np.vstack([
    np.array([np.sin(2*np.pi*t + rng.uniform(-0.2, 0.2)) for _ in range(13)]),
    np.array([np.cos(2*np.pi*t + rng.uniform(-0.2, 0.2)) for _ in range(12)]),
])

db = dbscan_fd(X, t, eps=0.5, min_points=3)
dist = np.asarray(db["distances"])

# Sort each row's nearest-neighbor distances (k=4th NN for eps selection)
knn_dist = np.sort(dist, axis=1)[:, 4]  # 4th nearest neighbor distance
knn_sorted = np.sort(knn_dist)

f, ax = fig(figsize=(7.0, 3.6))
ax.plot(knn_sorted, color="#3f51b5", lw=1.8)
ax.axhline(0.5, color="#e8710a", ls="--", lw=1.4, label="eps=0.5")
ax.set(title="4th-NN distance (sorted): eps selection guide",
       xlabel="observation rank", ylabel="4th-NN L2 distance")
ax.legend()
print(render(f))
print("FDARS_FENCE_OK")
```

---

## 9. Environment Availability

Step 2.6: All code runs against the installed `.venv` package — no new bindings, no new tools. The `fdars` package is already compiled under `.venv` from the v11.0 milestone. No external dependencies beyond what is in the current venv.

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| `fdars` (compiled) | All fences | Yes | `.venv/_native.abi3.so` exists |
| `matplotlib` | `html="1"` fences | Yes | Used extensively by existing mature pages |
| `docs_fig.py` | `fig()`/`render()`/`fast()` pattern | Yes | `scripts/docs_fig.py` present |
| `markdown-exec` | Fence execution | Yes | Already wired into `mkdocs.yml` |
| `numpy` | All fences | Yes | Required by fdars |
| `docs_data.py` | Real dataset loaders | Yes | `scripts/docs_data.py` with `load_canadian_weather()`, `load_phoneme()`, `load_sonar()` |

---

## Validation Architecture

> `workflow.nyquist_validation` is explicitly `false` in `.planning/config.json`. Section skipped.

---

## Security Domain

> This is a docs-only phase — prose and inline code examples only, no API surface changes, no authentication, no data ingestion beyond the already-approved `docs/data/` CSV files. `security_enforcement` is enabled but no ASVS categories apply to static documentation editing.

---

## Open Questions

1. **Canadian weather fence build speed.** The `canadian_weather.csv` has 35 obs × 365 grid points. Running `ftsm(data, t, ncomp=3)` on 35 × 365 should be fast (FTSM is FPCA + AR fitting). Running `stationarity_test` with `n_perm=999` on 35 × 365 may take several seconds. Use `fast(999, 19)` to keep strict-build cost bounded. Recommendation: test locally with `DOCS_FAST=1` unset before including real data; fall back to weekly-mean subsample (35 × 52) if > 3 seconds.

2. **Phoneme dataset fence timing for shapelets.** Phoneme is 400 × 256. Even a 2-class subset (80+80 curves × 256 pts) with `max_candidates=200` and exhaustive shapelet search may be slow. Consider a 30+30 synthetic version for the fence and reference phoneme in a `!!! tip "Real data"` admonition without running it as a fence.

3. **KCFC / FunFEM with very small n.** These methods are EM-based. With n=20–30 and k=2, convergence is typically fast (< 50 iterations). Verify locally before committing fences to the page.

4. **`dense_flmm` convergence on small n.** The REML-EM with `max_iter=50` and `tol=1e-10` on 24 observations (8 subjects × 3 visits) may not converge to the tight tolerance. A `!!! note "Convergence"` admonition with `converged` check is essential; planner should include a fallback instruction if convergence fails (raise `max_iter`, loosen `tol`).

---

## Assumptions Log

> All claims about API surface are [VERIFIED] by reading Rust source files this session. No [ASSUMED] API claims.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Canadian weather fence with `n_perm=fast(999,19)` completes in < 3 seconds | Section 9 | Would need synthetic fallback |
| A2 | Phoneme 2-class shapelet fence with `max_candidates=200` completes in < 5 seconds | Section 9 | Would need fully synthetic fence |
| A3 | `dense_flmm` with n=24, n_subjects=8, ncomp=2 converges within 50 iterations | Section 8 | Fence would print `converged: False`; add `max_iter=100` fallback note |
| ~~A4~~ | ~~mfpca ncomp=5 default~~ | ~~Section 3.3~~ | RESOLVED: `#[pyo3(signature = (variables, ncomp=5, weighted=true))]` confirmed at src/spm_mod.rs:881 [VERIFIED: src/spm_mod.rs:881] |

**Verified claim count:** All API names, parameter names, defaults, and return keys in Section 3 are [VERIFIED: src/*.rs] by reading the binding sources this session.

---

## Sources

### Primary (HIGH confidence)
- `src/fts_mod.rs` — all FTS function signatures, return dicts, and `register()` listing
- `src/density_fda_mod.rs` — normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter, lqd_fpca signatures and return types
- `src/shapelet_mod.rs` — shapelet_transform_fit, shapelet_transform, shapelet_classifier_fit, discover_shapelets, shapelet_distance; PyShapeletFit and PyShapeletClassifierFit class definitions
- `src/clustering_mod.rs` — dbscan_fd, kcfc_cluster, funfem_cluster, align_cluster_fd signatures and return dicts; register() listing
- `src/spm_mod.rs` (lines 882–948) — mfpca signature and return dict
- `src/famm_mod.rs` — dense_flmm, multi_famm, fast_fmm signatures, return dicts, and `dense_flmm_result_to_pydict` helper (keys)
- `src/multi_fdata_mod.rs` — PyMultiFunData class and its standalone-container-only status in fdars-core 0.33
- `src/metric_mod.rs` (lines 87–198) — gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict signatures
- `docs/analyze/clustering.md` — mature-page template (section structure, heading style, admonition placement)
- `docs/analyze/outlier-detection.md` — mature-page template cross-check
- `docs/data/README.md` — confirmed dataset shapes, loaders, and license status

### Secondary (MEDIUM confidence)
- Existing thin pages (`functional-time-series.md`, `density-fda.md`, `multi-domain.md`, `shapelets.md`, `advanced-clustering.md`) — content to preserve vs. content to fix
- `docs/analyze/index.md` — confirmed nav structure and available cross-reference targets
- `docs/analyze/seasonal-analysis.md`, `functional-statistics.md` — additional mature-page pattern references

---

## Metadata

**Confidence breakdown:**
- API surface (function names, params, defaults, return keys): HIGH — all verified from Rust source this session
- API discrepancies to fix: HIGH — directly confirmed by comparing page text to Rust signatures
- Mature-page template structure: HIGH — read directly from clustering.md and outlier-detection.md
- Cross-reference targets: HIGH — verified against directory listing
- Fence timing (Canadian weather, phoneme): ASSUMED — not run this session

**Research date:** 2026-09-05
**Valid until:** This research is tied to the v11.0 fdars bindings. Valid until a new fdars-core version lands (no bump planned in v12.0 per REQUIREMENTS.md).
