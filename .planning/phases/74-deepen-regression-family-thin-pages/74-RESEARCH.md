# Phase 74: Deepen Regression-Family Thin Pages — Research

**Researched:** 2026-09-05
**Domain:** MkDocs documentation depth — regression-family method pages
**Confidence:** HIGH (all API facts verified directly from Rust binding source this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Page Depth & Structure**
- Depth target: Hit the parity bar solidly at mature-page *quality*, sized to each method's actual surface — do not pad to a fixed length. A method with a smaller API surface may yield a shorter page and still be at parity.
- Restructure approach: Mirror the mature numbered-section template used by pages like `scalar-on-function.md` — a motivating "When to use" / decision section near the top, numbered worked-method sections in the body, a diagnostics/interpretation section, and a "See also" cross-reference block at the bottom. Preserve correct existing prose and examples; restructure and expand around them rather than rewriting from scratch.
- Exec'd visualizations: Add ≥1 `html="1"` exec'd matplotlib plot per page where it genuinely clarifies the method (matching the mature pages' visual standard). Not every fence needs a plot — only where it aids understanding.

**Worked Examples & Data**
- Data source: Prefer small, self-contained synthetic simulations built *inside* each fence (deterministic, offline, fast) — as `frechet-regression.md` already does. Use existing `docs/data/` datasets only where a method has a natural real-data fit.
- Count: ≥3 runnable inline fences per page (meets the bar); add more only where a distinct method variant warrants its own example.
- Sentinel: Every runnable example must emit `FDARS_FENCE_OK` when run offline under `.venv`. Fences stay small (few observations / grid points) to bound the ~25-min whole-site strict build that runs once in Phase 79.

**Cross-Reference & Accuracy**
- See also: Each page links to related methods within the regression family and the regression index (3–5 links), so the five pages cross-navigate.
- Admonitions: ≥3 per page mixing `note` / `tip` / `warning` / `info`, method-specific (parameter guidance, caveats, return-type gotchas).
- API accuracy: Every method claim, function name, and signature must be accurate against the shipped v11.0 bindings — no stale/renamed API, no R-era prose. Runnable fences are self-verifying; verify remaining prose claims against the current `fdars` surface. Keep a "methods in R but not (yet) in Python" note only where it is accurate (mature-page pattern).

### Claude's Discretion

(None specified beyond the locked decisions above.)

### Deferred Ideas (OUT OF SCOPE)

- Analyze-family thin pages → Phase 75 (DEPTH-02)
- Flagship end-to-end example pages → Phase 76 (EXMP)
- Section-landing thumbnails + cards for these pages → Phase 77 (CARD-03)
- Whole-site strict build / SVGO / human diagram review → Phase 79 (GATE)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEPTH-01 | The regression-family thin pages — `frechet-regression`, `function-on-function`, `additive-sof`, `concurrent-regression`, `functional-glm` — each reach the parity bar: a "When to use" decision section, a "See also" cross-reference block, parameter-selection + result-interpretation guidance, ≥3 caution/tip/note admonition boxes, and ≥3 runnable inline `FDARS_FENCE_OK` worked examples per page. | Full API surface verified per-page below; mature-page template dissected; cross-ref targets enumerated; all known pitfalls and API discrepancies documented. |
</phase_requirements>

---

## Summary

Phase 74 is a docs-only depth pass on five regression-family pages that shipped at 20–35% parity in v11.0. Every piece of research below was obtained by reading the actual Rust binding sources (`src/frechet_mod.rs`, `src/regression_mod.rs`, `src/scalar_on_function_mod.rs`) and the existing page files directly — no training-memory API claims.

The critical finding: **the five thin pages contain several stale or wrong API details that must be corrected as part of expanding them.** These are catalogued precisely per page in the API Surface section. The mature template (`scalar-on-function.md`) provides a clear, reproducible section skeleton. Synthetic in-fence simulation is the right data strategy for all five methods; none has a uniquely compelling real-dataset fit that warrants departing from the fence-size discipline.

**Primary recommendation:** Each page gets a dedicated PLAN.md task. Task author reads this research file, reads the existing thin page, reads the mature template section skeleton documented below, then writes prose + fences that (a) preserve correct existing content, (b) fix confirmed API errors, (c) add missing sections per the template, and (d) keep fences small and deterministic.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Page prose, structure, sections | Docs author | — | Pure markdown editing; no code change |
| Runnable fences (`exec="1"`) | Docs author (inline fence code) | `fdars` package (execution engine) | Fences call the current installed `fdars` — no new bindings |
| matplotlib figures (`html="1"`) | `docs_fig.py` helper + `markdown-exec` | MkDocs Material render | `docs_fig.fig()` / `render()` / `fast()` pattern — see Code Examples section |
| API accuracy | Rust binding sources (source of truth) | Installed `.venv` package | All claims must trace to `src/*_mod.rs` |

---

## 1. Mature-Page Template (from `scalar-on-function.md`)

The section skeleton to mirror — in this order:

```
# Page Title

[1–2 paragraph intro: what the method does, one-liner on how fdars estimates it]

![concept diagram](../assets/diagrams/<slug>.svg){ .fdars-diagram }

## [Decision section — "The estimation challenge" or "When to use"]

[Summary table: method | fdars function | key parameter | idea]
[Quick rule / "Start with X" recommendation]

[≥1 exec'd matplotlib figure showing a representative result — html="1"]

---

## 1. [First method / first variant]

[Mathematical exposition — brief]

[Code block: import + fit + key result extraction]

[Dict-key table: key | type | description]

[!!! note / tip / warning specific to this method]

---

## 2. [Second method / variant]

... (repeat pattern for each API function)

---

## [N-1]. Cross-validating / parameter selection

[fregre_cv / fof_cv / fregre_np_cv pattern]

---

## [N]. Diagnostics / Interpretation / Comparing methods

[Fitted-vs-residuals, coefficient recovery, or method comparison]

[exec'd matplotlib figure]

---

## Method selection guide

| Method | Best when | Speed | Interpretability |
...

## References

[2–5 primary statistical references]

---

[See also block — at the bottom, 3–5 links]
```

**Key formatting conventions observed in `scalar-on-function.md`:**

- Section numbers are Arabic integers in `## N. Title` form.
- A non-exec'd code block immediately after the numbered-section header shows the basic call; an `exec="1"` block (usually `source="above"` or standalone) provides the runnable example.
- The method-selection guide table lives in its own un-numbered section near the bottom, before References.
- Admonition syntax: `!!! note "Title"`, `!!! tip`, `!!! warning`, `!!! info` — all three types used on the same page.
- "Methods in R but not (yet) in Python" note appears as `!!! note "Methods available in the R package but not (yet) in Python"` — use this exact phrasing.
- "See also" is NOT a numbered section — it is a plain bullet list at the very end (no `##` header in `scalar-on-function.md`, but other mature pages use `## See also`). Use `## See also` for the five thin pages.

---

## 2. Existing Thin-Page Content to Preserve

### 2.1 `frechet-regression.md`

**Already correct and to preserve:**
- The mathematical intro (Fréchet mean formulation with weights, SPD simulation example)
- The `frechet_mean` API reference table (parameters, return-type-by-space table)
- The `!!! warning "Return type: naked array, not a dict"` admonition — keep verbatim
- The `frechet_global_reg` and `frechet_local_reg` API tables
- The `frechet_anova` group-label note and parameter table
- All three statistical references

**Requires correction:**
1. `frechet_anova` default `n_perm`: page says `n_perm=99`, Rust binding says `n_perm=999` (default), and the signature is `(responses, argvals, group_labels, n_perm=999, seed=42)`. [VERIFIED: src/frechet_mod.rs:56]
2. `frechet_anova` return keys: page says `statistic | p_value | Plus 7 additional summary keys`. Actual keys are: `statistic`, `p_value_asymptotic`, `p_value_permutation`, `n_perm`, `group_frechet_variances`, `pooled_frechet_variance`, `fn_statistic`, `un_statistic`, `group_labels`. There is NO plain `p_value` key. [VERIFIED: src/frechet_mod.rs:94-110]
3. `frechet_anova` parameter order: page shows `(objects, group_labels, space, d, n_perm=99)` — the actual binding takes `(responses, argvals, group_labels, n_perm=999, seed=42)` with NO `objects`, NO `space`, NO `d` parameter. The current `frechet_anova` works only on density-response data (2D matrix), NOT on generic metric-space objects. [VERIFIED: src/frechet_mod.rs:56-64]
4. `frechet_local_reg` return dict: page says returns a `3-key dict` matching `frechet_global_reg`. The local variant dict keys are `predicted | xout | bandwidth` (NOT `x_bar`). [VERIFIED: src/frechet_mod.rs:221-228]
5. `frechet_global_reg` xout type: page shows `xout: np.ndarray (n_out,)` but the binding takes `xout: PyReadonlyArray2` — shape `(n_out, p)` for multi-predictor. [VERIFIED: src/frechet_mod.rs:146-153]

**Missing sections (to add):**
- "When to use" decision section (what kind of data triggers Fréchet regression vs linear SoF)
- Parameter selection guidance for bandwidth in `frechet_local_reg`
- Result interpretation section (how to read the predicted density/SPD output)
- ≥1 `html="1"` exec'd matplotlib figure
- "See also" block
- At least 2 more worked examples (currently has 1 runnable fence)

---

### 2.2 `function-on-function.md`

**Already correct and to preserve:**
- Mathematical intro (bivariate coefficient surface, truncated FPCA approach)
- The `fof_regression` API table (parameters and return keys)
- The note about `fpca_x`/`fpca_y` being excluded from the result dict
- The random-effects variant table at the bottom
- All three references

**Requires correction:**
1. `predict_fof` parameter order: page shows `predict_fof(x_data, y_data, x_argvals, y_argvals, ncomp_x, ncomp_y, new_x)`. Actual binding order is `predict_fof(x_data, y_data, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)` — `new_x` is the THIRD positional argument, not the last. [VERIFIED: src/regression_mod.rs:1339-1340]
2. `fof_cv` parameter: page shows `ncomp_x_range=[2, 3, 4]` as if it takes a list. Actual binding takes `ncomp_x_max=5, ncomp_y_max=5, n_folds=5, seed=42` — there is NO `ncomp_x_range` parameter. [VERIFIED: src/regression_mod.rs:1397]
3. `predict_fof_re` parameter order: page shows `predict_fof_re(x_data, y_data, x_argvals, y_argvals, subject_ids, ncomp_x, ncomp_y, new_x)`. Actual binding: `predict_fof_re(x_data, y_data, subject_ids, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)`. [VERIFIED: src/regression_mod.rs:1610]
4. `fof_re_regression` signature: page does not show `max_iter`/`tol` params. Actual binding has `max_iter=50, tol=1e-10`. Return dict has 13 keys: `intercept, beta_surface, fitted, residuals, r_squared_t, r_squared, ncomp_x, ncomp_y, coef_matrix, random_effects, sigma2_u, sigma2_eps, n_subjects`. [VERIFIED: src/regression_mod.rs:1519-1564]

**Missing sections (to add):**
- "When to use" decision section (FoF vs concurrent vs SoF)
- Parameter selection for `ncomp_x`/`ncomp_y` via `fof_cv`
- Result interpretation (how to read `beta_surface`, when `r_squared_t` diverges from `r_squared`)
- ≥1 `html="1"` exec'd matplotlib figure (beta surface heatmap is natural)
- "See also" block
- Runnable fences — currently only 1 exec fence; needs ≥2 more

---

### 2.3 `additive-sof.md`

**Already correct and to preserve:**
- Mathematical intro (additive functional model formulation)
- The `fam` API parameter and return-key tables
- The `fregre_gsam`, `fregre_gkam` brief API descriptions
- The `variable_selection` penalty note (`"group_mcp"` and `"group_scad"` raise `ValueError`)
- All three references

**Requires correction:**
1. `fam` defaults in the existing exec'd fence: the fence calls `fam(data, y, t, ncomp=3, bandwidth=0.5, ...)`. The actual Rust default is `ncomp=0` (auto via GCV) and `bandwidth=0.0` (auto per component via GCV). The fence is syntactically valid (the user can pass 3 and 0.5), but the API reference table claims default is 3 and 0.5, which is wrong. [VERIFIED: src/scalar_on_function_mod.rs:75]
2. `model_selection_ncomp` parameter name: page shows `ncomp_max=6` but the actual binding param is `max_comp` (not `ncomp_max`). [VERIFIED: src/scalar_on_function_mod.rs:423]
3. `variable_selection` return dict: page shows only `active_predictors` and `coefficients`. Actual dict has 9 keys: `active_predictors, coefficients, fitted_values, residuals, intercept, lambda, r_squared, iterations, converged`. [VERIFIED: src/scalar_on_function_mod.rs:381-397]
4. `fregre_gkam` return dict: page omits `iterations` and `r_squared`. Actual dict: `fitted_values, residuals, component_fits, intercept, bandwidths, iterations, converged, r_squared`. [VERIFIED: src/scalar_on_function_mod.rs:280-292]
5. The module path for all `additive-sof` functions is `fdars.scalar_on_function` (NOT `fdars.regression`). The page correctly states this but the planner must know it when writing fences.

**Missing sections (to add):**
- "When to use" decision section (FAM vs linear SoF vs GKAM)
- Backfitting convergence guidance for `fregre_gkam`
- Variable selection interpretation (what `active_predictors` means, choosing lambda)
- ≥1 `html="1"` exec'd matplotlib figure (partial-effect curves from `component_fits` is natural)
- "See also" block
- Currently has 1 exec fence; needs ≥2 more

---

### 2.4 `concurrent-regression.md`

**Already correct and to preserve:**
- Mathematical theory section (weighted OLS at each grid point, kernel table)
- The parameters table (exactly matches binding)
- The returns dict table (exactly matches binding)
- The `!!! note "beta_curve shape: (p, m)"` admonition — keep verbatim
- The exec'd matplotlib figure (already present — `html="1"`)
- The bandwidth and kernel-choice caveats section
- The "Model scope: local-at-each-t" section
- All three references

**This page has significantly more content than the others** — bandwidth/kernel guidance exists. What is missing:
- "When to use" decision section at the top (concurrent vs FoF vs SoF)
- Manual bandwidth CV example (the page notes `fregre_np_cv` exists for the concurrent model — but `fregre_np_cv` is for NP scalar-on-function regression; the concurrent model has no built-in CV, so users must code it manually. This needs a worked example fence)
- A prediction / out-of-sample example fence (the page shows fitting but not predicting on new data — there is no `predict_concurrent_regression` in the binding, so prediction is by matrix algebra on `beta_curve`)
- ≥2 more runnable fences (currently has 1 exec fence)
- "See also" block
- The `!!! warning "No built-in bandwidth CV"` admonition (mentioned in prose but not as a formal admonition)

---

### 2.5 `functional-glm.md`

**Already correct and to preserve:**
- The two-stage theory section (FPCA projection → GLM in score space)
- The link-function table (`gaussian`/`binomial`/`poisson`/`gamma`)
- The `!!! warning "Gamma family uses the inverse canonical link"` — keep verbatim
- The `!!! note "AIC is not comparable to R glm() AIC"` — keep verbatim
- The full parameters table and 15-key return dict table
- The exec'd matplotlib figure (binomial + poisson example with `html="1"`)
- All four references

**This is the best-documented of the five pages.** What is missing:
- "When to use" decision section (functional GLM vs functional logistic vs SoF linear)
- A Gaussian family example (the existing fence shows binomial + Poisson; a Gaussian example closes the loop and proves `family="gaussian"` reduces to the SoF linear model)
- Parameter selection section (how to choose `n_comp` for GLM, using `model_selection_ncomp` or inspecting deviance/AIC)
- Gamma response example with a tip about `y > 0` constraint
- ≥1 more runnable fence (currently 1 exec fence; needs ≥2 more non-html fences or 1 more html fence)
- "See also" block

---

## 3. Exact API Surface — Per Page

All function names, parameter names, defaults, and return keys are [VERIFIED] by reading the Rust binding source this session.

### 3.1 `frechet-regression.md` — `fdars.frechet` submodule

**Module:** `from fdars.frechet import ...`

**Registered functions** [VERIFIED: src/frechet_mod.rs:489-494]:
- `frechet_anova`
- `frechet_global_reg`
- `frechet_local_reg`
- `frechet_mean`

**`frechet_mean(objects, space, d, weights=None)`** [VERIFIED: src/frechet_mod.rs:343-344]
- `objects`: Python `list` of `np.ndarray` (2D for spd/correlation, 1D for spherical)
- `space`: `str` — `"spd"`, `"spherical"`, or `"correlation"`
- `d`: `int` — ambient dimension
- `weights`: optional `np.ndarray` (n,)
- Returns: `np.ndarray (d, d)` for spd/correlation; `np.ndarray (d,)` for spherical
- Raises `ValueError` for: wrong space string, non-positive SPD diagonal, non-symmetric, non-unit-norm spherical, non-unit-diagonal correlation

**`frechet_global_reg(predictors, responses, argvals, xout)`** [VERIFIED: src/frechet_mod.rs:146-153]
- `predictors`: `np.ndarray (n, p)` — scalar predictor matrix (multi-predictor OK)
- `responses`: `np.ndarray (n, m)` — density-response matrix
- `argvals`: `np.ndarray (m,)` — strictly increasing evaluation grid
- `xout`: `np.ndarray (n_out, p)` — must be 2D even for p=1
- Returns dict: `predicted (n_out, m)`, `xout (n_out, p)`, `x_bar (p,)`
- Raises `ValueError` if argvals not strictly increasing, or dimension mismatch

**`frechet_local_reg(predictors, responses, argvals, xout, bandwidth)`** [VERIFIED: src/frechet_mod.rs:206-213]
- Same first 4 params as global; adds required `bandwidth: float`
- Returns dict: `predicted (n_out, m)`, `xout (n_out, p)`, `bandwidth (float)` — NO `x_bar`
- Raises `ValueError` if bandwidth <= 0

**`frechet_anova(responses, argvals, group_labels, n_perm=999, seed=42)`** [VERIFIED: src/frechet_mod.rs:56-64]
- `responses`: `np.ndarray (n, m)` — density-response matrix (NOT generic metric-space objects)
- `argvals`: `np.ndarray (m,)` — strictly increasing
- `group_labels`: `np.ndarray (n,)` int64 — contiguous 0..k
- Returns dict (9 keys): `statistic`, `p_value_asymptotic`, `p_value_permutation`, `n_perm`, `group_frechet_variances (k,)`, `pooled_frechet_variance`, `fn_statistic`, `un_statistic`, `group_labels (n,)`
- NO `p_value` key. NO `space`/`d`/`objects` params.

**R-methods-not-in-Python note for frechet-regression.md:**
- Wasserstein barycenter estimation is NOT in `fdars` (the `frechet_global_reg` uses signed-weight quantile averaging, which allows negative weights — not equivalent to Wasserstein barycenter)
- SPD-geodesic regression (along the SPD manifold using the affine-invariant metric) is not directly exposed — `frechet_mean` with `space="spd"` uses Frobenius metric only

---

### 3.2 `function-on-function.md` — `fdars.regression` submodule

**Module:** `from fdars.regression import ...`

**Registered functions** (FoF-specific) [VERIFIED: src/regression_mod.rs:1220-1224]:
- `fof_regression`
- `predict_fof`
- `fof_cv`
- `fof_re_regression`
- `predict_fof_re`

**`fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)`** [VERIFIED: src/regression_mod.rs:1275-1276]
- Returns dict (9 keys): `intercept (m_y,)`, `beta_surface (m_y, m_x)`, `fitted (n, m_y)`, `residuals (n, m_y)`, `r_squared_t (m_y,)`, `r_squared`, `ncomp_x`, `ncomp_y`, `coef_matrix (ncomp_x, ncomp_y)`
- `beta_surface` shape: `(m_y, m_x)` — rows = response grid, cols = predictor grid

**`predict_fof(x_data, y_data, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)`** [VERIFIED: src/regression_mod.rs:1339-1340]
- `new_x` is the THIRD positional argument (before argvals)
- Returns `np.ndarray (n_new, m_y)`

**`fof_cv(x_data, y_data, x_argvals, y_argvals, ncomp_x_max=5, ncomp_y_max=5, n_folds=5, seed=42)`** [VERIFIED: src/regression_mod.rs:1397]
- Parameters: `ncomp_x_max` and `ncomp_y_max` (NOT `ncomp_x_range`)
- Returns dict: `candidates (list of (int,int))`, `cv_errors (n_candidates,)`, `optimal (int,int)`, `min_cv_mse`

**`fof_re_regression(x_data, y_data, subject_ids, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)`** [VERIFIED: src/regression_mod.rs:1519]
- `subject_ids`: int64 array, non-negative, ≥2 distinct groups
- Returns dict (13 keys): same 9 as `fof_regression` plus `random_effects (n_subjects, m_y)`, `sigma2_u (ncomp_y,)`, `sigma2_eps`, `n_subjects`

**`predict_fof_re(x_data, y_data, subject_ids, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10)`** [VERIFIED: src/regression_mod.rs:1610]
- `new_x` is FOURTH positional argument (after `subject_ids`)
- Returns `np.ndarray (n_new, m_y)`

**R-methods-not-in-Python note for function-on-function.md:**
- Basis-expansion FoF (using B-spline or Fourier basis for both X and Y) is not directly exposed; the FPCA approach in `fof_regression` is the only estimator
- Historical covariance/cross-covariance inspection tools from R's `fda` are not in `fdars`

---

### 3.3 `additive-sof.md` — `fdars.scalar_on_function` submodule

**Module:** `from fdars.scalar_on_function import ...`

**Registered functions** [VERIFIED: src/scalar_on_function_mod.rs:454-460]:
- `fam`
- `fregre_gkam`
- `fregre_gsam`
- `variable_selection`
- `model_selection_ncomp`

**`fam(data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel="gaussian", n_grid_bandwidth=20)`** [VERIFIED: src/scalar_on_function_mod.rs:75-76]
- Default `ncomp=0` means auto via GCV (NOT 3)
- Default `bandwidth=0.0` means auto per component via GCV (NOT 0.5)
- Default `n_grid_bandwidth=20` (NOT 10 as the page shows in one place, and NOT 5 as the fence uses)
- Returns dict (7 keys): `fitted_values (n,)`, `residuals (n,)`, `component_fits (list of 1D arrays, one per FPC)`, `intercept`, `bandwidths (ncomp,)`, `ncomp`, `r_squared`

**`fregre_gsam(data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel="gaussian", n_grid_bandwidth=20)`** [VERIFIED: src/scalar_on_function_mod.rs:157-158]
- Identical signature to `fam`; returns identical 7-key dict

**`fregre_gkam(predictors, y, argvals_list, scalar_covariates=None, bandwidth=0.0, kernel="gaussian", max_iter=50, epsilon=1e-6)`** [VERIFIED: src/scalar_on_function_mod.rs:240-241]
- `predictors`: `list` of `np.ndarray (n, m_p)`
- `argvals_list`: `list` of `np.ndarray (m_p,)`
- Returns dict (8 keys): `fitted_values (n,)`, `residuals (n,)`, `component_fits (list of 1D)`, `intercept`, `bandwidths (P,)`, `iterations`, `converged`, `r_squared`

**`variable_selection(predictors, y, argvals_list, scalar_covariates=None, ncomp=3, penalty="group_lasso", lambda_=0.0, max_iter=100, epsilon=1e-5, lambda_n_grid=20)`** [VERIFIED: src/scalar_on_function_mod.rs:337-338]
- Supported penalties: `"group_lasso"`, `"ls"` only
- Returns dict (9 keys): `active_predictors (bool, P,)`, `coefficients (list)`, `fitted_values (n,)`, `residuals (n,)`, `intercept`, `lambda`, `r_squared`, `iterations`, `converged`

**`model_selection_ncomp(data, response, max_comp=10, criterion="gcv")`** [VERIFIED: src/scalar_on_function_mod.rs:423]
- Parameter name is `max_comp` (NOT `ncomp_max` as the thin page shows)
- Returns dict: `best_ncomp`, `criteria` (list of `(ncomp, aic, bic, gcv)` tuples)

**R-methods-not-in-Python note for additive-sof.md:**
- `"group_mcp"` and `"group_scad"` penalties in `variable_selection` raise `ValueError` — not yet implemented in fdars-core 0.33 (this is already correctly noted on the page)

---

### 3.4 `concurrent-regression.md` — `fdars.regression` submodule

**Module:** `import fdars.regression as reg` or `from fdars.regression import concurrent_regression`

**Registered function** [VERIFIED: src/regression_mod.rs:1218]:
- `concurrent_regression`

**`concurrent_regression(predictors, response, argvals=None, bandwidth=0.2, kernel="gaussian")`** [VERIFIED: src/regression_mod.rs:1037]
- `predictors`: `list[np.ndarray (n, m)]` — non-empty list
- `response`: `np.ndarray (n, m)`
- `argvals`: optional `np.ndarray (m,)`; `None` → uniform [0,1] grid
- Kernels: `"gaussian"`, `"epanechnikov"`, `"tricube"`
- Returns dict (5 keys): `beta_curve (p, m)`, `intercept (m,)`, `fitted (n, m)`, `residuals (n, m)`, `argvals (m,)`
- Raises `ValueError`: empty predictor list, bandwidth ≤ 0, shape mismatches, n ≤ p

**Important:** there is NO `predict_concurrent_regression` function. To predict on new data, callers must manually apply `beta_curve` and `intercept` to new predictor matrices:
```python
# Manual prediction (no predict_ function exists):
y_new = np.asarray(result["intercept"]) + sum(
    new_x[k] * np.asarray(result["beta_curve"])[k] for k in range(p)
)
```

**R-methods-not-in-Python note for concurrent-regression.md:**
- Built-in cross-validation for bandwidth selection (`fregre.np.cv`-style) is NOT provided for the concurrent model — callers must implement manual CV over `bandwidth` values using held-out prediction MSE

---

### 3.5 `functional-glm.md` — `fdars.regression` submodule

**Module:** `import fdars.regression as reg` or `from fdars.regression import functional_glm`

**Registered function** [VERIFIED: src/regression_mod.rs:1219]:
- `functional_glm`

**`functional_glm(data, response, family="gaussian", n_comp=3, scalar_covariates=None, max_iter=25, tol=1e-6)`** [VERIFIED: src/regression_mod.rs:1168]
- Families: `"gaussian"`, `"binomial"`, `"poisson"`, `"gamma"` (dispatched via `family_from_str`) [VERIFIED: src/regression_mod.rs:1070-1080]
- Domain constraints: binomial `y ∈ {0.0, 1.0}`; poisson `y ≥ 0`; gamma `y > 0`
- Returns dict (15 keys): `intercept`, `beta_t (m,)`, `beta_se (m,)`, `gamma (K,)`, `fitted_values (n,)`, `linear_predictors (n,)`, `ncomp`, `coefficients (K+1,)`, `std_errors (K+1,)`, `log_likelihood`, `deviance`, `iterations`, `aic`, `bic`, `family` [VERIFIED: src/regression_mod.rs:1096-1127]
- `r.fpca` is intentionally NOT in the returned dict (internal use only)

**Gotchas already documented on the page (keep):**
- Gamma uses inverse canonical link `g(μ)=1/μ`, NOT log-link
- AIC is from the score-space GLM, not comparable to R's `glm()` AIC

**Note:** `functional_logistic` is a separate function (`fdars.regression.functional_logistic`) that pre-dates `functional_glm`. It returns a different dict: `probabilities, predicted_classes, beta_t, intercept, coefficients`. The GLM page should note that for binary classification the specialized `functional_logistic` (with `bootstrap_ci_functional_logistic`) may be more appropriate — it returns predicted classes directly.

---

## 4. Cross-Reference Targets ("See also" links per page)

Each page should link 3–5 related pages. Confirmed nav destinations from `docs/regression/` [VERIFIED: docs/regression/ directory listing]:

**`frechet-regression.md`** → See also:
- [Scalar-on-Function Regression](scalar-on-function.md) — Euclidean response alternative
- [Regression Diagnostics](regression-diagnostics.md) — diagnostics applicable after fitting
- [Uncertainty Quantification](uncertainty-quantification.md) — bootstrap CI for regression
- [Regression index](index.md)
- (Optional) link to `docs/examples/` Fréchet example when Phase 76 ships — omit for now

**`function-on-function.md`** → See also:
- [Concurrent Regression](concurrent-regression.md) — another functional-response method
- [Function-on-Scalar Regression](function-on-scalar.md) — scalar-predictor analogue
- [Scalar-on-Function Regression](scalar-on-function.md) — scalar-response analogue
- [Cross-Validation](cross-validation.md) — `fof_cv` tie-in
- [Regression index](index.md)

**`additive-sof.md`** → See also:
- [Scalar-on-Function Regression](scalar-on-function.md) — linear SoF baseline
- [Robust Regression](robust-regression.md) — when outliers are also present
- [Cross-Validation](cross-validation.md) — bandwidth/ncomp selection
- [Regression index](index.md)

**`concurrent-regression.md`** → See also:
- [Function-on-Function Regression](function-on-function.md) — functional-response with global β
- [Scalar-on-Function Regression](scalar-on-function.md) — scalar-response alternative
- [Function-on-Scalar Regression](function-on-scalar.md) — scalar-predictor alternative
- [Regression Diagnostics](regression-diagnostics.md)
- [Regression index](index.md)

**`functional-glm.md`** → See also:
- [Scalar-on-Function Regression](scalar-on-function.md) — Gaussian GLM specialization
- [Classification](classification.md) — binary response classification alternative
- [Uncertainty Quantification](uncertainty-quantification.md) — bootstrap CI for functional models
- [Cross-Validation](cross-validation.md) — `model_selection_ncomp` for GLM
- [Regression index](index.md)

---

## 5. Fence Patterns and Data Strategy

### 5.1 docs_fig helper conventions [VERIFIED: scripts/docs_fig.py]

```python
# Standard exec'd figure fence pattern:
```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render          # fig() wraps plt.subplots; render() → inline SVG
from fdars.regression import ...

rng = np.random.default_rng(42)           # always deterministic seed
...
f, ax = fig()
ax.plot(...)
ax.set(title="...", xlabel="...", ylabel="...")
print(render(f))                           # html="1" captures this print
print("FDARS_FENCE_OK")                    # required sentinel
```

For expensive operations (permutations etc.), use `fast()`:
```python
from docs_fig import fig, render, fast
result = some_fn(..., n_perm=fast(999, 99))  # full build uses 999; DOCS_FAST=1 uses 99
```

**Color palette** (matches mkdocs-material indigo theme) [VERIFIED: scripts/docs_fig.py:43-51]:
- Primary: `#3f51b5` (indigo)
- Secondary: `#e8710a` (orange)
- Tertiary: `#198754` (green), `#dc3545` (red), `#6f42c1` (purple), `#0dcaf0` (cyan), `#6c757d` (grey)

### 5.2 Synthetic simulation pattern (preferred)

Keep n small (15–30 observations), m small (20–60 grid points) for each fence. The whole-site strict build (~25 min) runs once in Phase 79; per-page fences must be individually cheap.

Template for each page's first worked example:
```python exec="1" source="above"
import numpy as np
from fdars.<module> import <function>

rng = np.random.default_rng(42)
n, m = 20, 30
t = np.linspace(0, 1, m)
# ... construct data ...
result = <function>(...)
print(f"<key>: {np.asarray(result['<key>']).shape}")
print("FDARS_FENCE_OK")
```

### 5.3 Real dataset opportunities

Based on `docs/data/` contents [VERIFIED: docs/data/README.md]:

| Method | Natural real-data fit | Dataset |
|--------|-----------------------|---------|
| `fam` / `fregre_gsam` | NIR spectra → fat/protein content | `tecator.csv` (240 obs, 100 grid pts) — fat/protein are scalar responses, spectra are functional predictor |
| `functional_glm` (binomial) | Sonar mine vs rock binary | `sonar.csv` (208 obs, 60 bands) — binary `label` column |
| `fof_regression` | Canadian weather temperature → precipitation | `canadian_weather.csv` (35 obs, 365 pts) — both temperature and precipitation are functional |
| `concurrent_regression` | Growth study | `growth.csv` (93 obs, 31 pts) — small enough but the concurrent model needs same-grid predictor and response |
| `frechet_global_reg` | No strong fit in current datasets (needs density-response data) | Prefer synthetic |

**Recommendation:** Use real datasets as optional Section 2+ examples after the synthetic Section 1 example; keep them gated with FDARS_FENCE_OK. Tecator is the most natural fit for `fam` (mature pages already use it for SoF examples). Do NOT use datasets that are too large for fast build iteration (365-point Canadian weather fences may be slow — test first or use a subset).

---

## 6. Common Pitfalls

### Pitfall 1: Stale `frechet_anova` API
**What goes wrong:** Using the page's current API description `frechet_anova(objects, group_labels, space, d, n_perm=99)` — this signature does not exist. The actual function accepts density-response matrices, not generic metric-space object lists.
**Root cause:** The page was written from an R-era description of generic Fréchet ANOVA; the Python binding was implemented for density-only data.
**How to avoid:** Always call `frechet_anova(responses, argvals, group_labels)` and access `p_value_asymptotic` / `p_value_permutation` (not `p_value`).

### Pitfall 2: `predict_fof` argument order
**What goes wrong:** `predict_fof(x_data, y_data, x_argvals, y_argvals, ncomp_x, ncomp_y, new_x)` raises a shape error because argvals are interpreted as `new_x`.
**Root cause:** The thin page listed `new_x` as the last argument; the binding puts it third.
**How to avoid:** `predict_fof(x_data, y_data, new_x, x_argvals, y_argvals)` — new_x before argvals.

### Pitfall 3: `fam` / `fregre_gsam` defaults
**What goes wrong:** Caller assumes `ncomp=3` and `bandwidth=0.5` are the defaults and relies on the API table; the actual defaults are `ncomp=0` (auto) and `bandwidth=0.0` (auto).
**Root cause:** The thin page documented incorrect defaults.
**How to avoid:** Pass explicit values if you need fixed components/bandwidth; use `ncomp=0` intentionally for auto-selection.

### Pitfall 4: `fof_cv` parameter name
**What goes wrong:** `fof_cv(..., ncomp_x_range=[2,3,4])` raises `TypeError: unexpected keyword argument`.
**Root cause:** The thin page invented `ncomp_x_range`; the real params are `ncomp_x_max` and `ncomp_y_max`.
**How to avoid:** Use `fof_cv(x_data, y_data, x_argvals, y_argvals, ncomp_x_max=5, ncomp_y_max=5)`.

### Pitfall 5: Concurrent regression — no predict function
**What goes wrong:** Caller searches for `predict_concurrent_regression` and finds nothing; or assumes `beta_curve` shape is `(n, m)` instead of `(p, m)`.
**Root cause:** The concurrent model's beta is per-predictor (rows = predictors), not per-observation. The `(p, m)` note is on the page but easy to miss.
**How to avoid:** Read `beta_curve` as rows=predictors. Prediction requires manual multiply: `y_pred(t) = intercept(t) + sum_k(beta_curve[k, :] * x_k(t))`.

### Pitfall 6: GLM family names and link functions
**What goes wrong:** Passing `family="Gamma"` (capital G) raises `ValueError`; expecting log-link for gamma produces wrong results.
**Root cause:** Family strings are lowercase-only; gamma uses inverse canonical link not log.
**How to avoid:** Always lowercase: `"gaussian"`, `"binomial"`, `"poisson"`, `"gamma"`. Note explicitly that gamma link is `1/μ`.

### Pitfall 7: `frechet_global_reg` / `frechet_local_reg` xout must be 2D
**What goes wrong:** Passing `xout = np.array([0.5, 1.0])` (1D) raises a shape error; the binding expects `np.ndarray (n_out, p)`.
**Root cause:** The page listed `xout (n_out,)` which only works for p=1 with a 2D array of shape (n_out, 1).
**How to avoid:** Always reshape: `xout = np.array([[0.5], [1.0]])` for p=1 scalar predictors.

---

## 7. Code Examples

### Fence-1 pattern: minimal exec block with FDARS_FENCE_OK

```python exec="1" source="above"
import numpy as np
from fdars.regression import fof_regression

rng = np.random.default_rng(42)
n, mx, my = 20, 20, 15
tx = np.linspace(0, 1, mx)
ty = np.linspace(0, 1, my)
X = np.array([np.sin(2 * np.pi * tx + rng.uniform(0, 0.3)) for _ in range(n)])
Y = np.array([np.cos(np.pi * ty + rng.uniform(0, 0.3)) for _ in range(n)])

fit = fof_regression(X, Y, tx, ty, ncomp_x=3, ncomp_y=3)
print(f"beta_surface shape: {np.asarray(fit['beta_surface']).shape}")
print(f"r_squared: {fit['r_squared']:.4f}")
print("FDARS_FENCE_OK")
```

### Fence-2 pattern: html figure with beta surface heatmap (FoF example)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render

rng = np.random.default_rng(0)
n, mx, my = 25, 20, 15
tx = np.linspace(0, 1, mx)
ty = np.linspace(0, 1, my)
X = np.array([rng.standard_normal() * np.sin(2 * np.pi * tx)
              + rng.standard_normal() * np.cos(4 * np.pi * tx) for _ in range(n)])
Y = np.array([rng.standard_normal() * np.cos(np.pi * ty) for _ in range(n)])

from fdars.regression import fof_regression
fit = fof_regression(X, Y, tx, ty, ncomp_x=3, ncomp_y=3)
beta = np.asarray(fit["beta_surface"])  # (my, mx)

f, ax = fig()
im = ax.imshow(beta, aspect="auto", origin="lower",
               extent=[tx[0], tx[-1], ty[0], ty[-1]], cmap="RdBu_r")
f.colorbar(im, ax=ax, shrink=0.8)
ax.set(title="Estimated coefficient surface β(s,t)",
       xlabel="predictor grid s", ylabel="response grid t")
print(render(f))
print("FDARS_FENCE_OK")
```

### Fence-3 pattern: GLM gaussian example (closes the "reduces to linear" claim)

```python exec="1" source="above"
import numpy as np
from fdars.regression import functional_glm, fregre_lm

rng = np.random.default_rng(7)
n, m = 30, 50
t = np.linspace(0, 1, m)
beta_true = np.sin(4 * np.pi * t)
X = np.array([rng.standard_normal() * np.sin(2 * np.pi * t)
              + rng.standard_normal() * np.cos(2 * np.pi * t) for _ in range(n)])
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * rng.standard_normal(n)

glm_g = functional_glm(X, y, family="gaussian", n_comp=3)
lm = fregre_lm(X, y, n_comp=3)

print(f"GLM (gaussian) r_squared-proxy (corr): "
      f"{np.corrcoef(np.asarray(glm_g['fitted_values']), y)[0,1]:.4f}")
print(f"fregre_lm r_squared: {lm['r_squared']:.4f}")
print("FDARS_FENCE_OK")
```

### Fence-4 pattern: concurrent regression manual prediction

```python exec="1" source="above"
import numpy as np
from fdars.regression import concurrent_regression

rng = np.random.default_rng(3)
n, m = 20, 40
t = np.linspace(0, 1, m)
x1 = np.array([np.sin(2 * np.pi * t) + rng.normal(0, 0.1, m) for _ in range(n)])
y  = x1 * np.sin(np.pi * t) + rng.normal(0, 0.05, (n, m))

res = concurrent_regression([x1], y, t)
beta = np.asarray(res["beta_curve"])   # shape (1, m) — p=1 predictor

# Manual prediction on new data:
x_new = np.sin(2 * np.pi * t + 0.5)  # shape (m,)
y_pred = np.asarray(res["intercept"]) + beta[0] * x_new  # shape (m,)

print(f"beta_curve shape: {beta.shape}  (p=1 predictor × m={m} grid points)")
print(f"y_pred shape: {y_pred.shape}")
print("FDARS_FENCE_OK")
```

---

## 8. Environment Availability

> Step 2.6: All code runs against the installed `.venv` package — no new bindings, no new tools. The `fdars` package is already compiled under `.venv` from the v11.0 milestone. No external dependencies beyond what is in the current venv.

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| `fdars` (compiled) | All fences | Yes | `.venv/_native.abi3.so` exists |
| `matplotlib` | `html="1"` fences | Yes | Used extensively by existing mature pages |
| `docs_fig.py` | `fig()`/`render()` pattern | Yes | `scripts/docs_fig.py` present |
| `markdown-exec` | Fence execution | Yes | Already wired into `mkdocs.yml` |
| `numpy` | All fences | Yes | Required by fdars |

---

## Validation Architecture

> `workflow.nyquist_validation` is explicitly `false` in `.planning/config.json`. Section skipped.

---

## Security Domain

> This is a docs-only phase — prose and inline code examples only, no API surface changes, no authentication, no data ingestion beyond the already-approved `docs/data/` CSV files. `security_enforcement` is enabled but no ASVS categories apply to static documentation editing.

---

## Open Questions

1. **Tecator real-data fence build speed.** The page instructs "prefer synthetic" and Tecator is 240 obs × 100 pts. Loading it in a fence is fine (`load_tecator()` is fast), but if `fam` with `ncomp=0` (auto-GCV) over 240 observations at `n_grid_bandwidth=20` is slow, the fence may push Phase 79's strict build over budget. Recommendation: run a local timing check with `DOCS_FAST` unset before including it; fall back to synthetic if > 3 seconds.

2. **`frechet_global_reg` on density data.** The function is designed for density-response data (responses are density curves that must integrate to 1). A synthetic fence must simulate valid density curves. The simplest approach: use normalized Gaussian bumps as density approximations. This has not been validated in a fence yet.

3. **`fof_re_regression` convergence on tiny n.** The random-effects model uses REML EM with `max_iter=50, tol=1e-10`. With n=20 and only 2 groups, convergence may be slow or fail. Verify that a minimal example (n=20, 2 subjects) converges before including in the worked-example fence.

---

## Assumptions Log

> All claims about API surface are [VERIFIED] by reading Rust source files this session. No [ASSUMED] API claims.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Tecator fence is fast enough for the strict build | Section 5.3 | Would need to fall back to synthetic example in the fam/gsam section |
| A2 | `frechet_global_reg` accepts normalized-Gaussian-bump density curves as valid input (the binding checks that argvals is strictly increasing but does not enforce ∫f(x)dx=1 on the responses) | Section 7 | Synthetic fence may raise ValueError — verify before committing |
| A3 | `fof_re_regression` with n=20, 2 groups converges in ≤50 EM iterations | Section 7 | Fence would timeout or return a degenerate result — use larger n or more groups |

**Verified claim count:** All API names, parameter names, defaults, and return keys in Section 3 are [VERIFIED: src/*.rs] by reading the binding sources this session.

---

## Sources

### Primary (HIGH confidence)
- `src/frechet_mod.rs` — frechet_mean, frechet_global_reg, frechet_local_reg, frechet_anova signatures and return dicts
- `src/regression_mod.rs` — fof_regression, predict_fof, fof_cv, fof_re_regression, predict_fof_re, concurrent_regression, functional_glm signatures and return dicts
- `src/scalar_on_function_mod.rs` — fam, fregre_gsam, fregre_gkam, variable_selection, model_selection_ncomp signatures and return dicts
- `docs/regression/scalar-on-function.md` — mature-page template and section skeleton
- `scripts/docs_fig.py` — fig/render/fast helpers and color palette

### Secondary (MEDIUM confidence)
- Existing thin pages — content to preserve vs. content to fix
- `docs/data/README.md` — dataset shapes and loaders for real-data fence candidates
- `docs/regression/index.md` — confirmed nav structure and available cross-reference targets

---

## Metadata

**Confidence breakdown:**
- API surface (function names, params, defaults, return keys): HIGH — all verified from Rust source this session
- Template structure: HIGH — read directly from scalar-on-function.md
- API discrepancies to fix: HIGH — directly confirmed by comparing page text to Rust signatures
- Cross-reference targets: HIGH — verified against directory listing
- Fence timing (Tecator etc.): ASSUMED — not run

**Research date:** 2026-09-05
**Valid until:** This research is tied to the v11.0 fdars bindings. Valid until a new fdars-core version lands (no bump planned in v12.0 per REQUIREMENTS.md).
