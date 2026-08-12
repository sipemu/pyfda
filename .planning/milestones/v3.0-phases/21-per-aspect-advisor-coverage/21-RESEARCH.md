# Phase 21: Per-Aspect Advisor Coverage — Research

**Researched:** 2026-08-12
**Domain:** fdars advisor build_diagnostics extension — pure NumPy offline branches + prompt layer
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **New `build_diagnostics` branches**, each a new file under `advisor/aspects/` (mirroring the existing 5), added to the dispatcher `_supported` set in `advisor/__init__.py`. Each is PURE NumPy over the fdars result dict — deterministic, offline, network-free, JSON-serialisable (no numpy scalars leak):
  - **depth** (ASPECT-02) — LOW: summary stats over the returned depth vector (min/median/max, ranking spread, most/least central).
  - **outliers** (ASPECT-02) — LOW: outlier flags/counts, magnitude-vs-shape split, threshold used.
  - **classification** (ASPECT-03) — LOW: class balance, accuracy/confusion summary if present, per-class support.
  - **represent** (ASPECT-01) — LOW: basis/FPCA representation quality (variance captured, n components/nbasis, reconstruction error). Reuse the existing FPCA eigenvalue→variance logic; reconcile with the existing `basis`/`fpca` aspects (extend or add `represent` as its own method string — Claude's discretion, but do not duplicate the eigenvalue→variance code).
  - **regression** + **regression_cv** (ASPECT-04) — MEDIUM: `fregre_lm`/`fregre_pls` fit quality (r², residual skew/spread), and cross-validation summary (`fregre_cv`: chosen hyperparam, CV error curve summary).
  - **spm** (ASPECT-05) — HIGH (the only high-complexity branch): Phase-1 monitoring — T² and SPE exceedance rates, `spe_moment_match_diagnostic` (a real fdars function), eigenvalue→variance conversion (reuse FPCA branch logic). **Exclude** stochastic ARL (`arl0_t2`) — it would break the offline determinism guarantee.
- **ASPECT-06 (task families, no duplication):** the three task families (interpretation, parameter guidance, method guidance) already flow through the shared `_system_prompt(task, aspect)` + `Advice` schema built in Phases 19. Extend the per-aspect clause coverage so every aspect (old + new) has an appropriate FDA-primer clause — do NOT add a new function/schema per aspect. One shared prompt builder, one schema.
- **ASPECT-07 (caller-specified aspect):** `build_diagnostics(result, method, …)` already takes an explicit `method`; keep it caller-specified and NEVER auto-detect the aspect from result keys (key collisions like `r_squared`/`edf` make auto-detection unsafe). Preserve/verify this and add a test asserting no auto-detection path exists.
- **Determinism gate (per success criterion 4):** each new aspect gets an offline determinism test — same input → byte-identical JSON-serialisable output, no numpy scalar types.

### Claude's Discretion

Exact diagnostic field names per aspect, whether `represent` is a new method string vs an extension of `basis`/`fpca`, and the precise SPM exceedance-rate formulation — at Claude's discretion, guided by FEATURES.md's per-aspect reference table and the actual fdars result keys. Verify SPM's `spe_moment_match_diagnostic` signature against the code at plan/execute time.

### Deferred Ideas (OUT OF SCOPE)

- Exposing the new aspects through MCP tools + the Agent Skill → Phase 22.
- Stochastic ARL SPM diagnostics → out of scope entirely (FUT-02, breaks determinism).
- Cross-aspect compound diagnostics → out of scope (FUT-03).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ASPECT-01 | `build_diagnostics` supports represent/basis | `represent` as new method string; pure NumPy over `data`/`argvals` inputs; shared `_eigenvalues_to_variance` helper for cumulative variance |
| ASPECT-02 | `build_diagnostics` supports depth and outliers | depth functions return `ndarray (n,)` directly (not dict); outliers: `detect_outliers_lrt` → dict `{outliers, threshold}`, `outliergram` → dict `{mei, mbd, outliers}`, `magnitude_shape` → dict `{magnitude, shape}` |
| ASPECT-03 | `build_diagnostics` supports classification | `fclassif_*` → dict `{predicted, accuracy}`; `fclassif_cv` → dict `{error_rate, fold_errors, best_ncomp}` |
| ASPECT-04 | `build_diagnostics` supports regression and regression-CV | `fregre_lm`/`fregre_pls` → dict with `fitted_values`, `residuals`, `beta_t`, `r_squared` (lm also has `coefficients`, `intercept`); `fregre_cv` → dict `{optimal_k, min_cv_error, k_values, cv_errors, oof_predictions, fold_assignments, fold_errors}` |
| ASPECT-05 | `build_diagnostics` supports monitoring/SPM | `spm_phase1` → dict `{t2, spe, t2_limit, spe_limit, mean, loadings, weights, eigenvalues}`; `spe_moment_match_diagnostic(spe_values)` → dict `{excess_kurtosis, theoretical_kurtosis, is_adequate}` |
| ASPECT-06 | Every aspect has grounded task families through shared schema + prompt | Extend `_system_prompt` aspect clauses in `_prompts.py` only; schema and `Advice`/`Recommendation` unchanged |
| ASPECT-07 | Aspect always caller-specified, never auto-detected | `_supported` set check + `ValueError` path already enforced at `advisor/__init__.py:115-121`; add assertion test |
</phase_requirements>

---

## Summary

Phase 21 adds seven new `build_diagnostics` branches (depth, outliers, classification, represent, regression, regression_cv, spm) and per-aspect prompt clauses for the `_system_prompt` builder. Every branch follows the same pattern as the five existing aspects (clustering, smoothing, fpca, alignment, basis): a new file under `advisor/aspects/`, a `_build_<aspect>_diagnostics(raw, **kwargs) -> dict` function, lazy import in the dispatcher, and the method string added to `_supported`. No schema, no provider, no LLM changes.

The critical research finding is that **depth functions do NOT return dicts** — they return numpy arrays directly (shape `(n,)`). The `build_diagnostics` dispatcher therefore cannot `raw.get("depth_scores")` from a result dict; instead the caller must pass the score array itself, and the branch signature must accept it. This is a **FEATURES.md discrepancy** (see Section 2 below for full details).

The SPM branch is the only one that makes a live fdars call (`spe_moment_match_diagnostic`) inside `build_diagnostics`. This call is deterministic (pure computation, no RNG) so it does not break the offline guarantee. `arl0_t2` IS stochastic and is explicitly excluded.

**Primary recommendation:** Implement depth first (tracer, LOW complexity, reveals the non-dict input pattern), then outliers, classification, represent, regression, regression_cv, and SPM last. Extract a shared `_eigenvalues_to_variance` helper into `advisor/aspects/_utils.py` before starting represent or spm.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Offline diagnostics computation | `advisor/aspects/<aspect>.py` | `advisor/aspects/_utils.py` (shared helpers) | Each aspect owns its own computation; shared NumPy utilities live in a single helper module |
| Dispatcher routing | `advisor/__init__.py` | — | `_supported` set + lazy import pattern already established |
| Prompt specialization | `advisor/_prompts.py` | — | Single `_system_prompt(task, aspect)` builder; aspect clauses added inline |
| Schema validation | `advisor/_schema.py` | — | `Advice`/`Recommendation` unchanged; no per-aspect schema |
| Test coverage | `tests/test_advisor.py` | — | Existing file extended with new `TestBuildDiagnosticsOffline` methods per aspect |

---

## 1. Exact Result Keys Per Aspect — Verified Against Rust Bindings

### 1a. depth — IMPORTANT: Returns numpy array, NOT a dict

[VERIFIED: src/depth_mod.rs:24-33]

All depth functions (`fraiman_muniz_1d`, `modal_1d`, `random_projection_1d`, `random_tukey_1d`, `band_1d`, `modified_band_1d`, `modified_epigraph_index_1d`, `functional_spatial_1d`, `kernel_functional_spatial_1d`, `random_projection_deriv_1d`) return:

```
PyResult<Bound<'py, PyArray1<f64>>>
```

That is, a **1-D numpy array of shape `(n,)`**, NOT a Python dict. There is no key `"depth_scores"` or similar — the function IS the depth scores.

**FEATURES.md discrepancy confirmed:** FEATURES.md says "Inputs: depth scores array (n,), method name, ref_data shape." This is accurate but implies the build_diagnostics caller passes the raw ndarray, not a dict produced by fdars. The CONTEXT.md description ("result dict") is misleading for depth: the `result` parameter to `build_diagnostics` for the depth branch must be the score array itself (or a dict wrapper with a well-known key).

**Recommended resolution:** Accept the score array directly when `method="depth"`. The branch signature becomes:

```python
def _build_depth_diagnostics(raw, *, method_name: str = "unknown", **kwargs) -> dict:
    # raw is np.ndarray (n,) or array-like — the depth scores returned by fdars.depth.*
    scores = np.asarray(raw, dtype=float)
```

This is consistent with how the caller receives the output: `scores = fdars.depth.fraiman_muniz_1d(data, ref_data)` returns an ndarray. The dispatcher must document this clearly.

**Diagnostic fields to compute** (pure NumPy over the score array):

```
n_obs            int     len(scores)
depth_min        float   float(np.min(scores))
depth_max        float   float(np.max(scores))
depth_mean       float   float(np.mean(scores))
depth_median     float   float(np.median(scores))
depth_q10        float   float(np.percentile(scores, 10))
depth_q90        float   float(np.percentile(scores, 90))
depth_histogram  list    10-bucket counts: [int(v) for v in np.histogram(scores, bins=10)[0]]
method_name      str     caller-supplied string e.g. "fraiman_muniz"
```

No fdars call inside the builder — pure NumPy only.

---

### 1b. outliers — Three distinct result shapes depending on which function was called

[VERIFIED: src/outliers_mod.rs:28-46, 64-76, 88-100]

| Function | Return keys | Types |
|----------|-------------|-------|
| `detect_outliers_lrt(data, alpha, ...)` | `outliers` (bool array n,), `threshold` (float) | dict |
| `detect_outliers_lrt_with_dist(...)` | `outliers` (bool array n,), `threshold` (float), `null_distribution` (array n_boot,) | dict |
| `outliergram(data, factor)` | `mei` (array n,), `mbd` (array n,), `outliers` (bool array n,) | dict |
| `magnitude_shape(data)` | `magnitude` (array n,), `shape` (array n,) | dict |

**Key design decision:** The `outliers` method string covers results from any of these four functions. The builder infers which was called by key presence.

**Recommended diagnostic fields:**

```
n_obs                int    len(outliers_array) — inferred from result["outliers"] or magnitude/shape array
n_outliers           int    int(np.sum(result["outliers"]))                    # when "outliers" key present
outlier_fraction     float  float(n_outliers / n_obs)                         # when "outliers" key present
threshold            float  float(result["threshold"])                         # when "threshold" key present
has_magnitude_shape  bool   "magnitude" in raw and "shape" in raw
magnitude_range      list   [float(np.min(magnitude)), float(np.max(magnitude))]  # when present
shape_range          list   [float(np.min(shape)), float(np.max(shape))]          # when present
has_outliergram      bool   "mei" in raw and "mbd" in raw
mei_range            list   [float(np.min(mei)), float(np.max(mei))]              # when present
mbd_range            list   [float(np.min(mbd)), float(np.max(mbd))]              # when present
```

**Important:** `magnitude_shape` does NOT return `outliers` or `threshold` — it only returns `magnitude` and `shape` arrays. Do not assume `n_outliers` is computable from a pure `magnitude_shape` result. The builder must guard: `if "outliers" in raw`.

Note: `detect_outliers_lrt` uses a fixed `seed=42` in its internal bootstrap call [VERIFIED: src/outliers_mod.rs:39], making it deterministic. `detect_outliers_lrt_with_dist` also defaults `seed=42` [VERIFIED: src/outliers_mod.rs:125-127]. The builder is pure NumPy over the already-computed result, so determinism is not at risk.

---

### 1c. classification — Two result shapes

[VERIFIED: src/classification_mod.rs:24-40, 109-158]

**Point-estimate functions** (`fclassif_lda`, `fclassif_qda`, `fclassif_knn`, `fclassif_kernel`, `fclassif_dd`, `knn_classify_from_distances`, `kernel_classify_from_distances`):

```
predicted   ndarray (n,)  usize (integer class labels)
accuracy    float
```

**Cross-validation function** (`fclassif_cv`):

```
error_rate   float
fold_errors  ndarray (nfold,)
best_ncomp   usize (int)
```

**FEATURES.md discrepancy:** FEATURES.md mentions `"cv_error_rate"` as a key. The actual key from `fclassif_cv` is `"error_rate"` [VERIFIED: src/classification_mod.rs:155]. The builder must read `raw.get("error_rate")` not `raw.get("cv_error_rate")`, but may emit it as `cv_error_rate` in the diagnostics dict to distinguish from point-estimate accuracy.

**Recommended diagnostic fields:**

```
n_obs            int    int(len(raw["predicted"])) if "predicted" in raw else infer from fold_errors
accuracy         float  float(raw["accuracy"]) if "accuracy" in raw else None
error_rate       float  round(1.0 - accuracy, 10) if accuracy is not None else None
cv_error_rate    float  float(raw["error_rate"]) if "error_rate" in raw else None
fold_error_std   float  float(np.std(raw["fold_errors"])) if "fold_errors" in raw else None
best_ncomp       int    int(raw["best_ncomp"]) if "best_ncomp" in raw else None
n_classes        int    kwargs.get("n_classes") — caller must supply; cannot infer from result dict
```

`n_classes` cannot be inferred from the result dict (which contains only predicted labels, not ground-truth class count). Expose it as an optional `**kwargs` parameter: `build_diagnostics(result, "classification", n_classes=3)`.

---

### 1d. represent — New method string, pure NumPy over Fdata-like input

[VERIFIED: src/basis_mod.rs:426-476 (basis_nbasis_cv), python/fdars/advisor/aspects/fpca.py:12-82]

`represent` is recommended as a **new method string** (not an extension of `basis` or `fpca`). The reason: `represent` operates on the raw functional data matrix and evaluation grid — not on the output of a specific fdars function. The `basis` advisor operates on a GCV curve result dict; the `fpca` advisor operates on FPCA decomposition scores/singular_values. `represent` is a pre-analysis data-quality check.

**Input API:** The builder accepts either:
- A dict with keys `data` (array n×m) and `argvals` (array m,), optionally `rangeval` (tuple of 2 floats)
- An `Fdata` object whose `.data` and `.argvals` attributes give the same

**Recommended diagnostic fields:**

```
n_obs                int    int(data.shape[0])
n_points             int    int(data.shape[1])
argvals_min          float  float(np.min(argvals))
argvals_max          float  float(np.max(argvals))
argvals_spacing_mean float  float(np.mean(np.diff(argvals))) if len(argvals) > 1 else None
argvals_spacing_std  float  float(np.std(np.diff(argvals)))  if len(argvals) > 1 else None
is_uniform_grid      bool   bool(spacing_std / spacing_mean < 0.01) if spacing_mean > 0 else True
data_range_min       float  float(np.min(data))
data_range_max       float  float(np.max(data))
data_range_mean      float  float(np.mean(data))
```

No fdars call needed. No eigenvalue/variance computation for `represent` — that belongs to the `fpca` branch.

**No shared eigenvalue helper needed for represent.** Only `fpca` and `spm` share the eigenvalue→variance pattern. Extract the helper for those two only.

---

### 1e. regression — Two method strings, keys vary by function

[VERIFIED: src/regression_mod.rs:112-132, 153-173, 219-252, 271-291, 353-376, 801-824]

**`fregre_lm`** returns:
```
fitted_values  ndarray (n,)
residuals      ndarray (n,)
beta_t         ndarray (m,)   — functional coefficient curve
r_squared      float
coefficients   ndarray (n_comp,)
intercept      float
```

**`fregre_pls`** returns:
```
fitted_values  ndarray (n,)
residuals      ndarray (n,)
beta_t         ndarray (m,)
r_squared      float
```
(no `coefficients` or `intercept` keys)

**`fregre_l1`**, **`fregre_huber`** return:
```
fitted_values  ndarray (n,)
residuals      ndarray (n,)
beta_t         ndarray (m,)
```
(NO `r_squared` key — FEATURES.md incorrectly implies all regression functions return r_squared)

**`fregre_np`** returns:
```
fitted_values  ndarray (n,)
residuals      ndarray (n,)
h_func         float   — selected bandwidth
r_squared      float
```
(no `beta_t` key)

**`fosr`** returns:
```
fitted         ndarray (n, m)   — note: "fitted" not "fitted_values"
beta           ndarray (p, m)
residuals      ndarray (n, m)   — 2D, not 1D
r_squared      float
```

**`fosr_fpc`** returns:
```
intercept      ndarray (m,)
beta           ndarray (p, m)
fitted         ndarray (n, m)
residuals      ndarray (n, m)
r_squared_t    ndarray (m,)
r_squared      float
ncomp          int
```

**FEATURES.md discrepancy confirmed:** The reference table implies `residuals` are always 1-D and `r_squared` is always present. This is wrong for `fregre_l1`, `fregre_huber` (no `r_squared`) and `fosr`/`fosr_fpc` (2-D `residuals`, key `"fitted"` not `"fitted_values"`).

**Recommended diagnostic fields for `method="regression"`:**

```
n_obs             int    infer from fitted_values shape[0], or fitted shape[0] for fosr
r_squared         float  float(raw["r_squared"]) if "r_squared" in raw else None
residual_mean     float  float(np.mean(residuals_1d)) if 1D residuals present, else None
residual_std      float  float(np.std(residuals_1d))  if 1D residuals present, else None
residual_max_abs  float  float(np.max(np.abs(residuals_1d))) if 1D residuals present, else None
residual_skew     float  scipy-free skew: m3/m2^1.5 via NumPy, or None if 1D not present
beta_t_range      list   [float(np.min(beta_t)), float(np.max(beta_t))] if "beta_t" in raw else None
has_fosr          bool   "fitted" in raw and raw["fitted"] is 2D (ndim == 2 check on fitted)
```

Skewness without scipy: `m3 = np.mean((r - r.mean())**3); m2 = np.var(r); skew = m3 / m2**1.5 if m2 > 0 else 0.0`. Keep it pure NumPy.

---

### 1f. regression_cv — fregre_cv keys verified

[VERIFIED: src/regression_mod.rs:648-677]

**`fregre_cv`** returns:
```
optimal_k        usize (int)
min_cv_error     float
k_values         ndarray (k_max - k_min + 1,)  — usize array
cv_errors        ndarray (k_max - k_min + 1,)  — float array
oof_predictions  ndarray (n,)
fold_assignments ndarray (n,)
fold_errors      ndarray (n_folds,)
```

**`model_selection_ncomp`** returns:
```
best_ncomp  usize (int)
criteria    list of (usize, f64, f64, f64) tuples — (ncomp, aic, bic, gcv)
```
[VERIFIED: src/regression_mod.rs:433-456]

**FEATURES.md discrepancy confirmed:** FEATURES.md says `"cv_errors"` is a "list" and `"k_values"` is a "list". The actual Rust binding returns numpy arrays. The builder casts them to Python lists.

FEATURES.md also mentions "optional `min_cv_error`" — this is NOT optional in `fregre_cv`, it is always present. `model_selection_ncomp` does NOT return `cv_errors` or `k_values` at the top level; instead it returns `criteria` (list of tuples). The `regression_cv` builder must handle BOTH source functions.

**Recommended diagnostic fields for `method="regression_cv"`:**

```
optimal_k        int    int(raw["optimal_k"]) if "optimal_k" in raw else int(raw["best_ncomp"])
min_cv_error     float  float(raw["min_cv_error"]) if "min_cv_error" in raw else None
cv_curve         list   [float(v) for v in raw["cv_errors"]] if "cv_errors" in raw else extract from criteria
k_values         list   [int(v) for v in raw["k_values"]] if "k_values" in raw else [c[0] for c in raw.get("criteria", [])]
cv_curve_range   list   [float(min(cv_curve)), float(max(cv_curve))] if cv_curve else None
elbow_present    bool   True if the curve has a local minimum NOT at index 0 or -1
```

For `model_selection_ncomp` results, extract GCV values from the `criteria` tuples (index 3 of each tuple is `gcv`).

---

### 1g. spm — Full verification of spm_phase1 and spe_moment_match_diagnostic

[VERIFIED: src/spm_mod.rs:27-56, 235-247]

**`spm_phase1(data, argvals, ncomp, alpha)`** returns:
```
t2          ndarray (n,)
spe         ndarray (n,)
t2_limit    float        — direct scalar (result.t2_limit.ucl)
spe_limit   float        — direct scalar (result.spe_limit.ucl)
mean        ndarray (m,)
loadings    ndarray (m, ncomp)
weights     ndarray (m,)
eigenvalues ndarray (ncomp,)
```

**`spe_moment_match_diagnostic(spe_values)`** signature and returns:
[VERIFIED: src/spm_mod.rs:235-247]
```
Input:   spe_values — 1-D array (n,)
Returns: dict with keys:
  excess_kurtosis       float
  theoretical_kurtosis  float
  is_adequate           bool
```

This is a pure deterministic computation (kurtosis moments from the distribution), no RNG. Safe to call inside `build_diagnostics`.

**FEATURES.md accuracy confirmation:** FEATURES.md correctly identifies `spe_kurtosis_excess` as coming from `spe_moment_match_diagnostic`. The actual key returned by fdars is `excess_kurtosis` [VERIFIED: src/spm_mod.rs:244]. The builder should emit this as `spe_kurtosis_excess` in the diagnostics dict (a meaningful rename for the LLM's context) and also emit `spe_moment_match_adequate` from the `is_adequate` field.

**Eigenvalue→variance reuse:** The FPCA builder computes this at `advisor/aspects/fpca.py:37-44`:

```python
eigenvalues = (sv ** 2) / denom   # from singular values
total_var = float(eigenvalues.sum())
evr = eigenvalues / total_var
cum_list = [float(v) for v in np.cumsum(evr)]
```

For SPM, `spm_phase1` returns `eigenvalues` directly (not singular values) — the `/denom` step is NOT needed. The variance computation simplifies to:

```python
total_var = float(eigenvalues.sum())
evr = eigenvalues / total_var if total_var > 0 else np.zeros_like(eigenvalues)
cum_list = [float(v) for v in np.cumsum(evr)]
```

**Recommended diagnostic fields for `method="spm"`:**

```
n_obs                         int    int(len(raw["t2"]))
ncomp                         int    int(len(raw["eigenvalues"]))
t2_limit                      float  float(raw["t2_limit"])
spe_limit                     float  float(raw["spe_limit"])
t2_max                        float  float(np.max(raw["t2"]))
t2_mean                       float  float(np.mean(raw["t2"]))
t2_exceedance_rate            float  float(np.mean(np.asarray(raw["t2"]) > raw["t2_limit"]))
spe_max                       float  float(np.max(raw["spe"]))
spe_mean                      float  float(np.mean(raw["spe"]))
spe_exceedance_rate           float  float(np.mean(np.asarray(raw["spe"]) > raw["spe_limit"]))
eigenvalues                   list   [float(v) for v in raw["eigenvalues"]]
variance_explained_cumulative list   [float(v) for v in np.cumsum(evr)]  -- computed as above
spe_kurtosis_excess           float  float(mmd["excess_kurtosis"])  -- from spe_moment_match_diagnostic
spe_moment_match_adequate     bool   bool(mmd["is_adequate"])
```

The `spe_moment_match_diagnostic` call inside the builder:

```python
from fdars import spm as _spm
mmd = _spm.spe_moment_match_diagnostic(np.asarray(raw["spe"], dtype=float))
```

This is the ONLY live fdars call in any builder. It is deterministic. If `fdars` is not installed, the builder should gracefully set `spe_kurtosis_excess = None` and `spe_moment_match_adequate = None` rather than raising.

**EXCLUDED:** `arl0_t2` [VERIFIED: src/spm_mod.rs:381-401] — stochastic (seed-dependent Monte Carlo simulation). Confirmed deferred to FUT-02.

---

## 2. FEATURES.md Discrepancy Table

| Aspect | FEATURES.md claim | Actual (from Rust) | Action |
|--------|-------------------|---------------------|--------|
| depth | "result dict with depth scores" | Returns `ndarray (n,)` directly, no dict | Builder accepts array as `raw`, not dict |
| classification | key `"cv_error_rate"` | Actual key is `"error_rate"` in `fclassif_cv` | Builder reads `raw["error_rate"]`, emits as `cv_error_rate` |
| classification | "accuracy" always present | `fclassif_cv` has NO `accuracy` key — only `error_rate`, `fold_errors`, `best_ncomp` | Guard with `if "accuracy" in raw` |
| regression | `r_squared` always present | `fregre_l1`, `fregre_huber` do NOT return `r_squared` | Guard with `if "r_squared" in raw` |
| regression | `residuals` always 1-D | `fosr`, `fosr_fpc` return 2-D `residuals` (n, m) | Guard with `np.asarray(residuals).ndim == 1` before computing stats |
| regression | key `"fitted_values"` always present | `fosr`/`fosr_fpc` use key `"fitted"` not `"fitted_values"` | Check both keys |
| regression_cv | `"cv_errors"` is a list | Actually a numpy array from `fregre_cv` | Cast: `[float(v) for v in raw["cv_errors"]]` |
| regression_cv | `model_selection_ncomp` has `cv_errors`/`k_values` keys | It has `best_ncomp` + `criteria` (list of tuples) | Handle both sources |
| spm | `spe_kurtosis_excess` key from `spe_moment_match_diagnostic` | Actual key is `excess_kurtosis` | Rename in diagnostics dict |

---

## 3. SPM Deep Dive (HIGH Complexity)

### spm_phase1 output — confirmed exact

[VERIFIED: src/spm_mod.rs:43-55]

The dict-set calls are:
```rust
dict.set_item("t2", vec_to_numpy1d(py, result.t2_phase1))?;       // (n,)
dict.set_item("spe", vec_to_numpy1d(py, result.spe_phase1))?;     // (n,)
dict.set_item("t2_limit", result.t2_limit.ucl)?;                  // f64
dict.set_item("spe_limit", result.spe_limit.ucl)?;                // f64
dict.set_item("mean", vec_to_numpy1d(py, result.fpca.mean.clone()))?;         // (m,)
dict.set_item("loadings", fdmatrix_to_numpy2d(py, &result.fpca.rotation))?;  // (m, ncomp)
dict.set_item("weights", vec_to_numpy1d(py, result.fpca.weights.clone()))?;  // (m,)
dict.set_item("eigenvalues", vec_to_numpy1d(py, result.eigenvalues.clone()))?; // (ncomp,)
```

The `t2_limit` and `spe_limit` values are FLOATS (the `ucl` field of a control limit struct). They are NOT dicts. The builder reads them directly: `float(raw["t2_limit"])`.

### spe_moment_match_diagnostic — confirmed exact

[VERIFIED: src/spm_mod.rs:235-247]

```rust
let (excess_kurtosis, theoretical_kurtosis, is_adequate) =
    to_pyresult(fdars_core::spm::spe_moment_match_diagnostic(&sv))?;
dict.set_item("excess_kurtosis", excess_kurtosis)?;
dict.set_item("theoretical_kurtosis", theoretical_kurtosis)?;
dict.set_item("is_adequate", is_adequate)?;
```

Call pattern in the builder:
```python
import numpy as np
from fdars import spm as _spm

spe_arr = np.asarray(raw["spe"], dtype=float)
mmd = _spm.spe_moment_match_diagnostic(spe_arr)
# mmd["excess_kurtosis"]  -> float
# mmd["is_adequate"]      -> bool
```

### T²/SPE exceedance rate formulation

The exceedance rate is the fraction of Phase I observations that exceed the control limit:

```python
t2_arr = np.asarray(raw["t2"], dtype=float)
t2_exceedance_rate = float(np.mean(t2_arr > float(raw["t2_limit"])))
```

For a well-calibrated Phase I chart, this should be approximately `alpha` (default 0.05). If significantly higher, Phase I data may contain outliers or the chart is miscalibrated. The LLM prompt clause must explain this comparison.

### Eigenvalue→variance (SPM vs FPCA difference)

- FPCA builder: eigenvalues computed from `sv^2 / (n-1)` because `spm_phase1` returns singular values in the FPCA subresult, not eigenvalues
- SPM builder: `spm_phase1` returns `eigenvalues` directly (already computed in Rust), so NO `sv^2/(n-1)` step needed

Shared helper `_eigenvalues_to_variance_cumulative(eigenvalues: np.ndarray) -> list[float]`:

```python
def _eigenvalues_to_variance_cumulative(eigenvalues: np.ndarray) -> list:
    """Compute cumulative explained variance from eigenvalues (already scaled)."""
    ev = np.asarray(eigenvalues, dtype=float)
    total = float(ev.sum())
    if total <= 0.0:
        return [0.0] * len(ev)
    evr = ev / total
    return [float(v) for v in np.cumsum(evr)]
```

This helper is used in `aspects/spm.py` and can optionally be used in `aspects/fpca.py` after extracting. It should live in `advisor/aspects/_utils.py` (new file, single function initially, grows as needed).

---

## 4. represent vs basis/fpca

### Decision: `represent` is a new method string

Rationale:
- `basis` operates on the OUTPUT of `basis_nbasis_cv` (a GCV curve result dict).
- `fpca` operates on the OUTPUT of `fdars.regression.fpca` (scores + singular values).
- `represent` operates on the INPUT data matrix and evaluation grid — a pre-analysis data quality check, not a method output.

The three are orthogonal: a user can call `build_diagnostics(fdata_dict, "represent")` BEFORE choosing basis or FPCA. Merging into `basis` or `fpca` would conflate data-quality checking with method-output interpretation.

### Shared eigenvalue→variance helper placement

Only `fpca` and `spm` share the eigenvalue-to-variance pattern. `represent` does NOT use it. Place the helper in `advisor/aspects/_utils.py` and import it in both `aspects/fpca.py` and `aspects/spm.py`. The existing `fpca.py` can be refactored to use the helper (a safe, pure-logic extract) or left as-is if that risks regression; the planner should make this call based on risk appetite.

---

## 5. Dispatcher and Prompt Extension

### Extending `_supported` in `advisor/__init__.py`

[VERIFIED: python/fdars/advisor/__init__.py:115]

Current line 115:
```python
_supported = {"alignment", "fpca", "basis", "smoothing", "clustering"}
```

New set:
```python
_supported = {
    "alignment", "fpca", "basis", "smoothing", "clustering",  # existing
    "depth", "outliers", "classification",                      # ASPECT-02, 03
    "represent",                                                # ASPECT-01
    "regression", "regression_cv",                              # ASPECT-04
    "spm",                                                      # ASPECT-05
}
```

New dispatch branches follow the exact same lazy-import pattern:

```python
if method_lc == "depth":
    from fdars.advisor.aspects.depth import _build_depth_diagnostics
    return _build_depth_diagnostics(raw, **kwargs)
```

### Extending `_system_prompt` in `_prompts.py`

[VERIFIED: python/fdars/advisor/_prompts.py:40-167]

The current signature is `_system_prompt(task: str, aspect: str = "") -> str`. The `aspect` parameter is already accepted but unused (reserved for Phase 21). The extension adds aspect-specific clauses to the FDA primer section.

**Pattern:** Add an aspect-primer mapping BEFORE the task clause:

```python
_ASPECT_PRIMERS = {
    "depth": (
        "- Functional depth: measures how central each curve is relative to the sample. "
        "High depth = central/representative curve. Low depth = peripheral/outlier-like curve. "
        "depth_q10 is the 10th percentile of depth scores; a low value indicates many peripheral curves.\n"
    ),
    "outliers": (
        "- Functional outlier detection: outlier_fraction is the proportion flagged. "
        "A threshold derived from the null distribution (LRT) or a geometrical criterion (outliergram). "
        "magnitude outlyingness captures amplitude-direction outliers; shape outlyingness captures shape-direction outliers.\n"
    ),
    "classification": (
        "- Functional classification: accuracy is the proportion correctly classified. "
        "error_rate = 1 - accuracy. fold_error_std measures instability across CV folds. "
        "best_ncomp is the number of FPC components that minimizes CV error.\n"
    ),
    "represent": (
        "- Functional data representation: n_points is the number of evaluation grid points per curve. "
        "is_uniform_grid indicates whether the argvals spacing is regular. "
        "Sparse grids (n_points < 20) and irregular grids may require pre-smoothing before group analysis.\n"
    ),
    "regression": (
        "- Functional regression: r_squared measures goodness-of-fit (0–1). "
        "residual_skew > 0 indicates right-skewed residuals; large residual_max_abs may flag influential outlier observations. "
        "beta_t is the functional coefficient curve; beta_t_range summarises its magnitude.\n"
    ),
    "regression_cv": (
        "- Functional regression CV: optimal_k is the number of FPC components minimising CV error. "
        "elbow_present indicates whether the CV curve has a clear minimum away from the boundary. "
        "If optimal_k is at the k_max boundary, more components should be tested.\n"
    ),
    "spm": (
        "- Functional SPM Phase I: t2_exceedance_rate is the fraction of in-control observations exceeding "
        "the T² limit; for a well-calibrated chart this should approximately equal the design alpha. "
        "spe_kurtosis_excess from spe_moment_match_diagnostic measures departure of SPE from the "
        "moment-matched chi-squared approximation — high values indicate the approximation is inadequate. "
        "variance_explained_cumulative shows how much variation the chosen ncomp components capture.\n"
    ),
}
```

Inject the aspect primer into `_system_prompt`:

```python
def _system_prompt(task: str, aspect: str = "") -> str:
    aspect_primer = _ASPECT_PRIMERS.get(aspect.lower(), "")
    base = (
        "You are a functional data analysis (FDA) advisor. "
        f"{_GROUNDING_INVARIANT} "
        # ... existing base text ...
        "- Variance explained: cumulative proportion ...\n"
        + aspect_primer   # appended after existing FDA primer lines
    )
    # rest unchanged
```

**Critical constraint:** The `advise()` call in `__init__.py` currently passes `_system_prompt(task)` without the aspect argument [VERIFIED: python/fdars/advisor/__init__.py:368]. For ASPECT-06, the caller must pass `aspect` to `advise()`, or `advise()` must carry it through from a new parameter. The simplest approach: add `aspect: str = ""` parameter to `advise()` and thread it to `_system_prompt(task, aspect)`. This is a one-line change to `advise()` and a one-line change to the `_system_prompt` call inside it.

**No new schema, no new prompt function, no new Advice class.**

---

## 6. Determinism Requirements

### Rule: no numpy scalar types in output

The existing pattern (from `clustering.py` and `fpca.py`) is the canonical template:

```python
# CORRECT — native Python float
float(np.mean(scores))

# CORRECT — native Python int
int(np.sum(labels == ki))

# CORRECT — native Python bool
bool(phase_leakage_indicator > 0.5)

# WRONG — np.float64 leaks into output
np.mean(scores)
```

Every scalar value must be wrapped in `float()`, `int()`, or `bool()`. Every array value must be cast to a Python list with `[float(v) for v in arr]`.

### Determinism test pattern (per aspect)

Each aspect gets a test method in `tests/test_advisor.py` inside `TestBuildDiagnosticsOffline`:

```python
def test_depth_deterministic(self):
    import json
    from fdars.advisor import build_diagnostics
    import numpy as np

    scores = np.array([0.1, 0.5, 0.9, 0.3, 0.7, 0.4])
    d1 = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")
    d2 = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")
    assert d1 == d2
    s1 = json.dumps(d1, sort_keys=True)
    s2 = json.dumps(d2, sort_keys=True)
    assert s1 == s2, "json.dumps not byte-identical"
    # Verify no numpy scalar types
    def check_no_numpy(obj):
        import numpy as np
        assert not isinstance(obj, np.generic), f"numpy scalar leaked: {type(obj)}"
        if isinstance(obj, dict):
            for v in obj.values(): check_no_numpy(v)
        elif isinstance(obj, list):
            for v in obj: check_no_numpy(v)
    check_no_numpy(d1)
```

### Test for ASPECT-07 (no auto-detection)

```python
def test_no_auto_detection(self):
    """A result dict that looks like regression must NOT be routed to regression
    when method='clustering' is passed — ValueError is expected."""
    from fdars.advisor import build_diagnostics
    with pytest.raises(ValueError, match="unsupported method"):
        build_diagnostics({"r_squared": 0.9}, method="not_a_real_method")

def test_wrong_method_does_not_rerout(self):
    """Passing method='depth' for a dict-shaped result must run depth branch,
    not silently re-route to outliers just because keys look outlier-like."""
    from fdars.advisor import build_diagnostics
    import numpy as np
    # depth branch accepts an array
    scores = np.array([0.1, 0.5, 0.9])
    diag = build_diagnostics(scores, method="depth")
    assert diag["method"] == "depth"
    assert "n_obs" in diag
```

---

## 7. Tracer-First Sequencing

**Recommended implementation order:**

| Step | Aspect | Complexity | Why first/last |
|------|--------|------------|----------------|
| 1 | `depth` | LOW | Establishes the non-dict input pattern; smoke-tests the dispatcher extension; fully offline; determinism test is trivially synthetic |
| 2 | `outliers` | LOW | Dict input (normal pattern); tests multi-key presence logic; `detect_outliers_lrt` result is deterministic (fixed seed in Rust) |
| 3 | `classification` | LOW | Straightforward dict; tests the two-result-shape pattern (point-estimate vs CV) |
| 4 | `represent` | LOW | Pure NumPy on raw data; establishes `_utils.py` scaffold |
| 5 | `regression` | MEDIUM | Multi-variant output; tests optional-key guarding; skewness calculation |
| 6 | `regression_cv` | MEDIUM | Two source functions (`fregre_cv` vs `model_selection_ncomp`); elbow detection |
| 7 | `spm` | HIGH | Live fdars call inside builder; eigenvalue→variance; most diagnostic fields |

Between steps 3 and 4, create `advisor/aspects/_utils.py` with `_eigenvalues_to_variance_cumulative`. Refactor `spm.py` to use it.

**Tracer definition (depth):** Phase is "proven end-to-end" when:
- `advisor/aspects/depth.py` exists and `_build_depth_diagnostics` passes the determinism test
- `_supported` set in `__init__.py` includes `"depth"`
- `_system_prompt("interpretation", "depth")` returns a string containing "depth_q10"
- `test_depth_deterministic` passes
- `test_no_auto_detection` passes

---

## 8. Test Data — Offline Synthetic Fixtures

### depth
```python
scores_fixed = np.array([0.05, 0.2, 0.5, 0.8, 0.95, 0.3, 0.45, 0.6, 0.15, 0.7])
# n=10, min=0.05, max=0.95, q10≈0.065, q90≈0.905
```

### outliers — LRT result
```python
lrt_result = {
    "outliers": np.array([False, False, True, False, False]),
    "threshold": 2.47,
}
```

### outliers — outliergram result
```python
og_result = {
    "mei": np.array([0.3, 0.5, 0.9, 0.4, 0.2]),
    "mbd": np.array([0.6, 0.7, 0.1, 0.65, 0.55]),
    "outliers": np.array([False, False, True, False, False]),
}
```

### outliers — magnitude_shape result
```python
ms_result = {
    "magnitude": np.array([0.1, 0.3, 2.5, 0.2, 0.15]),
    "shape": np.array([0.05, 0.1, 0.8, 0.07, 0.06]),
}
```

### classification — point-estimate
```python
clf_result = {
    "predicted": np.array([0, 0, 1, 1, 2, 2]),
    "accuracy": 0.8333,
}
```

### classification — CV
```python
cv_result = {
    "error_rate": 0.18,
    "fold_errors": np.array([0.15, 0.20, 0.17, 0.22, 0.16]),
    "best_ncomp": 4,
}
```

### represent
```python
represent_input = {
    "data": np.random.RandomState(42).randn(20, 50),  # use fixed seed for determinism
    "argvals": np.linspace(0, 1, 50),
}
```

Or better (no RNG): use `np.ones((20, 50))` with argvals `np.linspace(0, 1, 50)` — fully deterministic.

### regression — fregre_lm result
```python
regr_result = {
    "fitted_values": np.array([1.1, 2.0, 3.2, 0.9, 2.5]),
    "residuals": np.array([0.1, -0.2, 0.3, -0.1, 0.2]),
    "beta_t": np.linspace(-0.5, 0.5, 30),
    "r_squared": 0.82,
    "coefficients": np.array([0.3, -0.1, 0.05]),
    "intercept": 0.15,
}
```

### regression — fregre_l1 result (no r_squared)
```python
regr_l1_result = {
    "fitted_values": np.array([1.0, 2.1, 3.0, 1.0, 2.4]),
    "residuals": np.array([0.2, -0.3, 0.5, -0.2, 0.3]),
    "beta_t": np.linspace(-0.3, 0.3, 30),
}
```

### regression_cv — fregre_cv result
```python
cv_regr_result = {
    "optimal_k": 3,
    "min_cv_error": 0.045,
    "k_values": np.array([1, 2, 3, 4, 5]),
    "cv_errors": np.array([0.12, 0.07, 0.045, 0.046, 0.048]),
    "oof_predictions": np.zeros(20),
    "fold_assignments": np.zeros(20, dtype=int),
    "fold_errors": np.array([0.04, 0.05, 0.04, 0.05, 0.04]),
}
```

### spm — synthetic Phase I result (avoid live fdars call for core test)
```python
spm_result = {
    "t2": np.array([1.2, 3.4, 0.8, 5.1, 2.3, 4.0, 1.5, 2.7, 0.9, 3.1]),
    "spe": np.array([0.05, 0.12, 0.03, 0.25, 0.08, 0.18, 0.04, 0.09, 0.02, 0.11]),
    "t2_limit": 4.5,
    "spe_limit": 0.20,
    "eigenvalues": np.array([2.1, 0.8, 0.3]),
}
```

For the SPM branch, the builder calls `fdars.spm.spe_moment_match_diagnostic(spe_values)` — this requires a compiled fdars install. The SPM test therefore belongs in a separate test class that requires `fdars` to be importable (which it is in the dev environment). Use `pytest.importorskip("fdars")` as the guard.

---

## Architecture Patterns

### Recommended Project Structure (new files)

```
python/fdars/advisor/
├── aspects/
│   ├── __init__.py          # existing — add new aspects to docstring
│   ├── _utils.py            # NEW — shared helpers (_eigenvalues_to_variance_cumulative)
│   ├── depth.py             # NEW — _build_depth_diagnostics
│   ├── outliers.py          # NEW — _build_outliers_diagnostics
│   ├── classification.py    # NEW — _build_classification_diagnostics
│   ├── represent.py         # NEW — _build_represent_diagnostics
│   ├── regression.py        # NEW — _build_regression_diagnostics
│   ├── regression_cv.py     # NEW — _build_regression_cv_diagnostics
│   └── spm.py               # NEW — _build_spm_diagnostics
│   # existing: alignment.py, basis.py, clustering.py, fpca.py, smoothing.py
├── __init__.py              # extend _supported + add 7 dispatch branches
├── _prompts.py              # add _ASPECT_PRIMERS dict + inject into _system_prompt
├── _schema.py               # NO CHANGES
└── providers/               # NO CHANGES
```

### Pattern: Builder file structure (every aspect)

```python
"""fdars.advisor.aspects.<aspect> — <Aspect> diagnostics builder."""
from __future__ import annotations
import numpy as np

def _build_<aspect>_diagnostics(raw, **kwargs) -> dict:
    """Compute <aspect> diagnostics.

    Parameters
    ----------
    raw : <type>
        <description of expected input — dict or array>

    Returns
    -------
    dict
        Plain-Python dict. All values are native Python types (float, int, bool,
        list, str, None). No numpy scalars.
    """
    diag: dict = {"method": "<aspect>"}
    # ... computation ...
    return diag
```

### Pattern: Dispatcher extension (one block per new aspect)

```python
# In advisor/__init__.py, inside build_diagnostics(), after existing if-blocks:

if method_lc == "depth":
    from fdars.advisor.aspects.depth import _build_depth_diagnostics  # noqa: PLC0415
    return _build_depth_diagnostics(raw, **kwargs)
```

The `raw` unwrapping (lines 124-126 in `__init__.py`) runs before any branch — new branches receive the unwrapped raw dict/array.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Skewness computation | Custom higher-moment formula | Pure NumPy: `m3/m2^1.5` | scipy not guaranteed in all envs; the formula is 3 lines |
| Eigenvalue→variance | Copy from `fpca.py` | `_utils._eigenvalues_to_variance_cumulative` | Prevent divergence between fpca/spm |
| `json.dumps` byte-identity | Custom serialisation | `json.dumps(d, sort_keys=True)` (already pattern in codebase) | Standard library; no deps |
| Elbow detection | Custom algorithm | Identify first index `i` where `cv_errors[i] < cv_errors[i-1]` and `cv_errors[i] < cv_errors[i+1]` | 2-line NumPy; no signal-processing library needed |

---

## Common Pitfalls

### Pitfall 1: Depth functions return arrays, not dicts

**What goes wrong:** `raw.get("depth_scores")` returns `None`; builder silently produces all-None diagnostics.
**Why it happens:** All depth functions in `depth_mod.rs` return `PyArray1<f64>`, not a dict. The conventions document in FEATURES.md implies a dict.
**How to avoid:** Accept the raw ndarray directly when `method="depth"`. Document the API clearly: `build_diagnostics(scores_array, method="depth")`.
**Warning signs:** `diag["n_obs"]` is `None` when you expected an integer.

### Pitfall 2: numpy scalar types leaking into output

**What goes wrong:** `json.dumps(diag, sort_keys=True)` raises `TypeError: Object of type float64 is not JSON serializable`.
**Why it happens:** `np.mean(scores)` returns `np.float64`, not `float`.
**How to avoid:** Wrap every scalar: `float(np.mean(scores))`, `int(len(arr))`, `bool(condition)`.
**Warning signs:** `type(diag["depth_mean"])` is `numpy.float64` not `float`.

### Pitfall 3: `fregre_l1`/`fregre_huber` have no `r_squared`

**What goes wrong:** `KeyError: 'r_squared'` in the regression builder.
**Why it happens:** These robust regression functions return only `fitted_values`, `residuals`, `beta_t`.
**How to avoid:** `r_squared = float(raw["r_squared"]) if "r_squared" in raw else None`.
**Warning signs:** Test with a synthetic fregre_l1 result dict that has no `r_squared` key.

### Pitfall 4: `fosr`/`fosr_fpc` residuals are 2-D

**What goes wrong:** `np.mean(residuals)` succeeds but `residual_skew` is computed over a 2-D array, producing wrong scalar.
**Why it happens:** `fosr` residuals have shape `(n, m)`.
**How to avoid:** `if np.asarray(raw.get("residuals", [])).ndim == 1:` before residual stats.
**Warning signs:** `residual_mean` is unexpectedly close to 0 (mean over all n×m values).

### Pitfall 5: SPM `spe_moment_match_diagnostic` requires installed fdars

**What goes wrong:** `ImportError` when running SPM tests without a compiled fdars build.
**Why it happens:** `spe_moment_match_diagnostic` is a native Rust function.
**How to avoid:** Wrap in try/except in the builder: if fdars is unavailable, set kurtosis fields to `None`. In tests, use `pytest.importorskip("fdars.spm")`.
**Warning signs:** SPM tests fail in CI before `maturin develop` has run.

### Pitfall 6: `fclassif_cv` has no `accuracy` key

**What goes wrong:** `diag["accuracy"]` is `None` when the caller passed a CV result expecting accuracy to be computed.
**Why it happens:** `fclassif_cv` returns `error_rate`, not `accuracy`.
**How to avoid:** Guard: `accuracy = 1.0 - float(raw["error_rate"])` ONLY if `"error_rate"` is present AND `"accuracy"` is NOT present (compute derived accuracy from CV error_rate).
**Warning signs:** `diag["accuracy"]` is None even though `diag["cv_error_rate"]` is 0.18.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (detected: `tests/test_advisor.py` exists) |
| Config file | `pyproject.toml` (pytest config via `[tool.pytest]`) |
| Quick run command | `pytest tests/test_advisor.py -x -q` |
| Full suite command | `pytest tests/ -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ASPECT-01 | `build_diagnostics(data, "represent")` returns deterministic dict | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_represent_deterministic -x` | No — Wave 0 |
| ASPECT-02a | `build_diagnostics(scores, "depth")` returns deterministic dict | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_depth_deterministic -x` | No — Wave 0 |
| ASPECT-02b | `build_diagnostics(lrt_result, "outliers")` returns deterministic dict | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_outliers_deterministic -x` | No — Wave 0 |
| ASPECT-03 | `build_diagnostics(clf_result, "classification")` returns deterministic dict | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_classification_deterministic -x` | No — Wave 0 |
| ASPECT-04a | `build_diagnostics(regr_result, "regression")` returns deterministic dict | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_regression_deterministic -x` | No — Wave 0 |
| ASPECT-04b | `build_diagnostics(cv_result, "regression_cv")` returns deterministic dict | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_regression_cv_deterministic -x` | No — Wave 0 |
| ASPECT-05 | `build_diagnostics(spm_result, "spm")` returns deterministic dict (requires fdars) | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_spm_deterministic -x` | No — Wave 0 |
| ASPECT-06 | `_system_prompt("interpretation", "depth")` contains depth-specific clause | unit | `pytest tests/test_advisor.py::TestPrompts::test_aspect_clauses -x` | No — Wave 0 |
| ASPECT-07 | `build_diagnostics(x, "bad_method")` raises ValueError | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_no_auto_detection -x` | Existing test covers ValueError; extend for new aspects |

### Wave 0 Gaps

- `TestBuildDiagnosticsOffline` test methods for: depth, outliers, classification, represent, regression, regression_cv, spm
- `TestPrompts` class with `test_aspect_clauses` verifying all 7 new aspect clauses appear in `_system_prompt` output
- Synthetic fixtures as documented in Section 8

---

## Security Domain

`security_enforcement: true` in config. ASVS level 1 applies.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Not applicable — offline computation layer, no user auth |
| V3 Session Management | No | Stateless function calls |
| V4 Access Control | No | Library, not networked |
| V5 Input Validation | Yes — LOW risk | Guard all `raw.get()` accesses; never assume key presence; validate array shapes before NumPy ops |
| V6 Cryptography | No | No cryptographic operations |

**Input validation pattern:** All builders must treat `raw` as untrusted input. Guard every key access. If an expected key is missing, emit `None` rather than raising unhandled `KeyError`. The depth branch must validate `raw` is array-like before `np.asarray`. SPM branch must validate `"t2"` and `"spe"` are present before calling `spe_moment_match_diagnostic`.

---

## Project Constraints (from CLAUDE.md)

| Directive | Impact on This Phase |
|-----------|---------------------|
| No per-aspect schema duplication | All builders return plain `dict`; `Advice`/`Recommendation` in `_schema.py` unchanged |
| Python 3.9+ compatibility | No walrus operators, no `match` statements, no `3.10+`-only syntax in new files |
| No linter/formatter detected | Code style follows PEP 8; function docstrings in NumPy format |
| `from __future__ import annotations` in all Python files | Required in all new `aspects/*.py` files |
| No external deps beyond NumPy in offline paths | All 7 builders use only `numpy`; SPM builder uses `fdars.spm` with graceful fallback |
| GSD workflow enforced | Work proceeds through `/gsd-execute-phase` |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `represent` data input is a dict with `"data"` and `"argvals"` keys, or the caller passes an `Fdata` object with `.data`/`.argvals` attributes | Section 1d | If caller API differs, the builder's `raw.get("data")` returns None silently |
| A2 | `fregre_cv` result always contains `k_values` as a usize array (not a list of Python ints) | Section 1f | Cast `[int(v) for v in raw["k_values"]]` handles both; risk is low |
| A3 | `_system_prompt` aspect clause injection via `_ASPECT_PRIMERS` dict is sufficient; no `aspect` routing inside the task clauses themselves is needed | Section 5 | If task clauses need aspect-specific text, the dict approach must be extended |

---

## Open Questions

1. **`advise()` aspect parameter threading**
   - What we know: `_system_prompt(task, aspect)` already accepts `aspect`, but `advise()` does not expose it and passes `_system_prompt(task)` (no aspect).
   - What's unclear: Should `advise()` gain an `aspect: str = ""` parameter in this phase, or is the aspect clause enhancement deferred to a prompt-only update?
   - Recommendation: Add `aspect: str = ""` to `advise()` in this phase — it's a one-line change and is the only way to deliver ASPECT-06. Without it, the prompt extension has no effect on LLM calls.

2. **`represent` input shape for `Fdata` objects**
   - What we know: `Fdata` objects have `.data` (ndarray) and `.argvals` (list or ndarray) attributes per `fdata_class.py`.
   - What's unclear: Does `.data` return the raw matrix directly or wrapped?
   - Recommendation: Use `getattr(raw, "data", raw.get("data"))` pattern to handle both Fdata objects and raw dicts transparently.

---

## Sources

### Primary (HIGH confidence)
- `src/depth_mod.rs` — all depth function signatures and return types [VERIFIED this session]
- `src/outliers_mod.rs` — `detect_outliers_lrt`, `outliergram`, `magnitude_shape` signatures and return types [VERIFIED this session]
- `src/classification_mod.rs` — `fclassif_lda`/`qda`/`knn`/`kernel`/`cv`/`dd` signatures and return types [VERIFIED this session]
- `src/regression_mod.rs` — `fregre_lm`, `fregre_pls`, `fregre_l1`, `fregre_huber`, `fregre_cv`, `model_selection_ncomp`, `fosr`, `fosr_fpc` [VERIFIED this session]
- `src/spm_mod.rs` — `spm_phase1` and `spe_moment_match_diagnostic` signatures and return types [VERIFIED this session]
- `src/basis_mod.rs` — `basis_nbasis_cv` signature [VERIFIED this session]
- `python/fdars/advisor/__init__.py` — `_supported` set line 115, dispatcher pattern [VERIFIED this session]
- `python/fdars/advisor/aspects/fpca.py` — eigenvalue→variance computation lines 37-44 [VERIFIED this session]
- `python/fdars/advisor/aspects/clustering.py` — builder pattern template [VERIFIED this session]
- `python/fdars/advisor/_prompts.py` — `_system_prompt` structure and `aspect` parameter stub [VERIFIED this session]
- `.planning/research/FEATURES.md` — per-aspect diagnostics reference table [read this session]
- `.planning/phases/21-per-aspect-advisor-coverage/21-CONTEXT.md` — locked decisions [read this session]

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` — ASPECT-01..07 requirement text [read this session]

**Research date:** 2026-08-12
**Valid until:** 2026-09-12 (stable Rust API; changes only on fdars-core version bump)
