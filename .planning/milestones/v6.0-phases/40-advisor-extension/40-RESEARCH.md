# Phase 40: Advisor Extension — Research

**Researched:** 2026-08-21
**Domain:** Python — grounded AI advisor aspect builders, fdars v6.0 result dicts
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**ADV-04 — outliers aspect (locked: EXTEND, no new aspect key)**
- Extend `python/fdars/advisor/aspects/outliers.py`'s `build_diagnostics` so it detects the new v6.0 outlier-detector result dicts (tvdmss / muod / sequential_transform_outliers / depthgram) by key presence and emits grounded SCALAR diagnostics: e.g. `n_outliers` (count), outlier fraction (n_outliers / n_obs), score/threshold ranges (min/max of the fdars-computed score vector) — NEVER raw index lists or numpy aggregates; reduce every value to a Python `float`/`int`. This closes the v5.0 Phase-34 deferral (functional-boxplot outlier diagnostics).
- No new aspect KEY is added (the aspect is already `outliers`); therefore `_DIAGNOSTICS_METHODS`/`_RUNNABLE_METHODS`/`_supported` are UNCHANGED and the MCP guard-sync is a no-op — confirm at plan/exec time that `test_diagnostics_methods_match_advisor_supported` stays green without edits. If (unexpectedly) a new key is required, the aspect-builder + MCP guard change MUST land in one atomic commit.

**ADV-05 — regression aspect + Group B feasibility (decided at plan time)**
- Extend `python/fdars/advisor/aspects/regression.py` so it surfaces grounded diagnostics for the new regression results where a genuine fdars-computed scalar exists: `functional_glm` (deviance, AIC, n_iter/converged), `concurrent_regression` (a fit-summary scalar, e.g. residual RMS). Grounding invariant preserved.
- **Group B advisor coverage (pace_fpca via `fpca` aspect, elastic_multinomial via `classification` aspect):** DECIDE at plan time on feasibility.
- ITP (interval inference) advisor coverage is NOT a locked v6.0 requirement; fold a grounded scalar into the existing `inference` aspect only if trivially available and clearly grounded — otherwise defer.

**Grounding + determinism (hard constraints)**
- Every emitted diagnostic cites an fdars-computed value; the advisor's `_check_grounding` guard must still pass. Offline `build_diagnostics` stays network-free and byte-identical across runs (`json.dumps(..., sort_keys=True)` stable); convert all numpy scalars via `float()`/`int()`.

### Claude's Discretion
Exact scalar diagnostic set per detector/model, whether Group B/ITP are included (feasibility), and prompt-primer wording are at Claude's discretion, grounded in the shipped v6.0 result dicts and the existing aspect-builder patterns.

### Deferred Ideas (OUT OF SCOPE)
- Dedicated advisor aspects for pace_fpca / elastic_multinomial if ADV-05's feasibility check defers them (Future Requirements: PACE-ADV / MULTINOM-ADV).
- Docs update of advisor `aspects.md` for the extended diagnostics — Phase 41 (DOCS-11).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADV-04 | Extend the grounded advisor's existing `outliers` aspect to summarize the new fdars-computed outlier-detector results (tvdmss / muod / sequential_transform_outliers / depthgram) as grounded scalar diagnostics; no new aspect key; `_DIAGNOSTICS_METHODS` unchanged; offline determinism preserved. | Exact result-dict keys read from `src/outliers_mod.rs`; extension pattern read from `aspects/outliers.py`; test pattern read from `test_advisor_inference.py`. |
| ADV-05 | Extend the advisor's existing `regression` aspect for `functional_glm` and `concurrent_regression`; decide Group B (pace_fpca / elastic_multinomial) feasibility from shipped result keys. | Exact result-dict keys read from `src/regression_mod.rs`, `src/pace_fpca_mod.rs`, `src/classification_mod.rs`; feasibility analyzed from available scalar fields. |
</phase_requirements>

---

## Summary

Phase 40 extends two existing advisor aspect builders — `outliers` and `regression` — to surface grounded scalar diagnostics for the four new v6.0 outlier detectors and two new v6.0 regression models. All evidence is grounded in fdars-computed values read directly from the shipped Rust converter functions. No new aspect keys are introduced; the MCP guard-sync is a no-op; `test_diagnostics_methods_match_advisor_supported` stays green without edits.

Group B feasibility (pace_fpca via `fpca` aspect, elastic_multinomial via `classification` aspect) is FEASIBLE for elastic_multinomial (`train_accuracy` is a clearly grounded scalar `float` in the shipped dict) and FEASIBLE for pace_fpca (`eigenvalues` vector yields a variance-explained cumulative via the existing `_eigenvalues_to_variance_cumulative` helper, and `ncomp`/`sigma2` are grounded scalars). Both are included in the plan with a clear implementation path.

ITP (`itp_one_pop`, `itp_two_pop`, `itp_flm`) returns `ItpResult` dicts with vector `adjusted_pvalues` and vector `unadjusted_pvalues` plus a vector `statistic_curve` — no single scalar summary is available without an arbitrary reduction. The existing `inference` aspect already handles scalar p-values; ITP's vector output does not map to the existing pattern without fabrication. **ITP advisor coverage is deferred per CONTEXT.md.**

**Primary recommendation:** Implement ADV-04 (4 new detector branches in outliers.py), ADV-05 regression extension (2 branches: functional_glm and concurrent_regression), plus the two Group B inclusions (elastic_multinomial branch in classification.py and pace_fpca eigenvalue branch in fpca.py), with matching offline tests per the established test_advisor_inference.py pattern.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| ADV-04: outlier scalar reduction | Python advisor layer | — | Pure Python: `aspects/outliers.py`'s `_build_outliers_diagnostics`; calls no fdars functions, only NumPy |
| ADV-05: GLM scalar reduction | Python advisor layer | — | `aspects/regression.py`'s `_build_regression_diagnostics`; key-presence guards only |
| ADV-05: concurrent regression residuals | Python advisor layer | — | Same file; `residuals` is 2-D here (n,m) so same `ndim==2` guard pattern as `fosr` applies |
| Group B: elastic_multinomial train accuracy | Python advisor layer (`classification`) | — | `aspects/classification.py`; `train_accuracy` is a native float scalar in the shipped dict |
| Group B: pace_fpca variance explained | Python advisor layer (`fpca`) | — | `aspects/fpca.py` + `_utils._eigenvalues_to_variance_cumulative`; eigenvalues already available |
| MCP guard-sync | MCP layer (`server.py`, `_runner.py`) | — | No-op: no new aspect keys; confirmed `_DIAGNOSTICS_METHODS` and `_supported` are unchanged |

---

## What to Extend — Exact File Inventory

All changes are Python-only. No maturin rebuild. No changes to Rust code.

| File | Change Type | Why |
|------|-------------|-----|
| `python/fdars/advisor/aspects/outliers.py` | Extend `_build_outliers_diagnostics` | Add 4 new detector branches (tvdmss, muod, sequential_transform_outliers, depthgram) |
| `python/fdars/advisor/aspects/regression.py` | Extend `_build_regression_diagnostics` | Add 2 new model branches (functional_glm, concurrent_regression) |
| `python/fdars/advisor/aspects/classification.py` | Extend (add elastic_multinomial branch) | Group B: `train_accuracy` is a grounded scalar |
| `python/fdars/advisor/aspects/fpca.py` | Extend (add pace_fpca eigenvalue branch) | Group B: `eigenvalues` → variance_explained_cumulative via existing helper |
| `python/fdars/advisor/_prompts.py` | Update `_ASPECT_PRIMERS["outliers"]` and `_ASPECT_PRIMERS["regression"]` | Add explanation of new diagnostic fields to the per-aspect primer clause |
| `tests/test_advisor_outliers_v6.py` | New test file | Offline grounding + determinism tests for all 4 new detector branches |
| `tests/test_advisor_regression_v6.py` | New test file | Offline tests for functional_glm + concurrent_regression branches |
| `tests/test_advisor_group_b.py` | New test file | Offline tests for elastic_multinomial (classification) + pace_fpca (fpca) branches |
| `python/fdars/mcp/server.py` | NO CHANGE | `_DIAGNOSTICS_METHODS` unchanged — no new aspect key |
| `python/fdars/mcp/_runner.py` | NO CHANGE | `_RUNNABLE_METHODS` unchanged |
| `python/fdars/advisor/__init__.py` | NO CHANGE | `_supported` set unchanged — existing `"outliers"`, `"regression"`, `"classification"`, `"fpca"` keys cover all new branches |

---

## ADV-04: Exact Result-Dict Keys for New Outlier Detectors

All keys verified by reading `src/outliers_mod.rs` lines 164–495 this session.

### tvdmss → `fdars.outliers.tvdmss`
[VERIFIED: src/outliers_mod.rs:165-187]

Keys emitted by `tvdmss_to_pydict`:
```
"magnitude_outliers"  list[int]   — indices of magnitude outliers
"shape_outliers"      list[int]   — indices of shape outliers
"tvd"                 ndarray(n,) — Total Variation Depth scores per curve
"mss"                 ndarray(n,) — Modified Shape Similarity scores per curve
```
Verbatim from source (lines 172-186):
```rust
dict.set_item("magnitude_outliers", r.magnitude_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("shape_outliers", r.shape_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("tvd", vec_to_numpy1d(py, r.tvd))?;
dict.set_item("mss", vec_to_numpy1d(py, r.mss))?;
```

**No "outliers" boolean array. No "n_obs" directly. No seed (deterministic by construction).**

Grounded scalars to emit:
| Output key | Source | Reduction |
|------------|--------|-----------|
| `n_magnitude_outliers` | `len(raw["magnitude_outliers"])` | `int()` |
| `n_shape_outliers` | `len(raw["shape_outliers"])` | `int()` |
| `n_obs` | `len(raw["tvd"])` (ndarray length) | `int()` |
| `magnitude_outlier_fraction` | n_magnitude_outliers / n_obs | `float()` |
| `shape_outlier_fraction` | n_shape_outliers / n_obs | `float()` |
| `tvd_range` | `[float(np.min(tvd)), float(np.max(tvd))]` | list[float] |
| `mss_range` | `[float(np.min(mss)), float(np.max(mss))]` | list[float] |
| `has_tvdmss` | `True` (key-presence flag) | `bool` |

Detection trigger: `"tvd" in raw and "mss" in raw` (distinct from outliergram's `"mei"/"mbd"` and magnitude_shape's `"magnitude"/"shape"` because tvdmss ALSO has `"shape_outliers"` as a list-of-int, not a score array).

**Disambiguation note:** Both `tvdmss` and `muod` emit a `"shape_outliers"` key as `list[int]`. `tvdmss` additionally has `"tvd"` and `"mss"`. `muod` additionally has `"amplitude_outliers"` and three `*_index` arrays. Use the presence of `"tvd"` to identify tvdmss and `"amplitude_outliers"` to identify muod — these keys are unique per detector.

### muod → `fdars.outliers.muod`
[VERIFIED: src/outliers_mod.rs:237-267]

Keys emitted by `muod_to_pydict`:
```
"shape_outliers"      list[int]   — indices of shape outliers
"magnitude_outliers"  list[int]   — indices of magnitude outliers
"amplitude_outliers"  list[int]   — indices of amplitude outliers
"shape_index"         ndarray(n,) — shape outlyingness score per curve
"magnitude_index"     ndarray(n,) — magnitude outlyingness score per curve
"amplitude_index"     ndarray(n,) — amplitude outlyingness score per curve
```
Verbatim from source (lines 248-266):
```rust
dict.set_item("shape_outliers", r.shape_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("magnitude_outliers", r.magnitude_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("amplitude_outliers", r.amplitude_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("shape_index", vec_to_numpy1d(py, r.shape_index))?;
dict.set_item("magnitude_index", vec_to_numpy1d(py, r.magnitude_index))?;
dict.set_item("amplitude_index", vec_to_numpy1d(py, r.amplitude_index))?;
```

Grounded scalars to emit:
| Output key | Source | Reduction |
|------------|--------|-----------|
| `n_magnitude_outliers` | `len(raw["magnitude_outliers"])` | `int()` |
| `n_shape_outliers` | `len(raw["shape_outliers"])` | `int()` |
| `n_amplitude_outliers` | `len(raw["amplitude_outliers"])` | `int()` |
| `n_obs` | `len(raw["shape_index"])` | `int()` |
| `magnitude_outlier_fraction` | n_magnitude_outliers / n_obs | `float()` |
| `shape_outlier_fraction` | n_shape_outliers / n_obs | `float()` |
| `amplitude_outlier_fraction` | n_amplitude_outliers / n_obs | `float()` |
| `shape_index_range` | `[float(np.min), float(np.max)]` of `shape_index` | list[float] |
| `magnitude_index_range` | `[float(np.min), float(np.max)]` of `magnitude_index` | list[float] |
| `amplitude_index_range` | `[float(np.min), float(np.max)]` of `amplitude_index` | list[float] |
| `has_muod` | `True` | `bool` |

Detection trigger: `"amplitude_outliers" in raw` (unique to muod).

### sequential_transform_outliers → `fdars.outliers.sequential_transform_outliers`
[VERIFIED: src/outliers_mod.rs:342-371]

Keys emitted by `seq_transform_to_pydict`:
```
"per_transform_outliers"  list[dict]  — each dict has "transform": str, "outliers": list[int]
"union_outliers"          list[int]   — union of all per-transform outlier index sets
```
Verbatim from source (lines 348-370):
```rust
let per_transform: Vec<Bound<'_, PyDict>> = r.per_transform_outliers.into_iter().map(|(t, idxs)| {
    let sub = PyDict::new(py);
    sub.set_item("transform", seq_transform_variant_str(&t))?;
    sub.set_item("outliers", idxs.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
    Ok(sub)
}).collect::<PyResult<Vec<_>>>()?;
dict.set_item("per_transform_outliers", per_transform)?;
dict.set_item("union_outliers", r.union_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
```

**Note: There is no n_obs key and no score vector. n_obs cannot be derived from this result without additional context. The builder will emit `n_union_outliers` as the only clearly grounded count, and `n_transforms` as a count of detector stages applied.**

Grounded scalars to emit:
| Output key | Source | Reduction |
|------------|--------|-----------|
| `n_union_outliers` | `len(raw["union_outliers"])` | `int()` |
| `n_transforms` | `len(raw["per_transform_outliers"])` | `int()` |
| `has_sequential_transform` | `True` | `bool` |

Detection trigger: `"union_outliers" in raw` (unique to this detector). Note: `per_transform_outliers` is a list-of-dicts not an array; n_obs is not recoverable without the original data, so do NOT attempt to derive an outlier fraction here — that would be fabrication.

### depthgram → `fdars.outliers.depthgram`
[VERIFIED: src/outliers_mod.rs:429-457]

Keys emitted by `depthgram_to_pydict` (10 keys total):
```
"mbd_mei_d"          ndarray(n,)
"mei_mbd_d"          ndarray(n,)
"mbd_mei_t"          ndarray(n,)
"mei_mbd_t"          ndarray(n,)
"mbd_mei_t2"         ndarray(n,)
"mei_mbd_t2"         ndarray(n,)
"shape_outliers"     list[int]
"magnitude_outliers" list[int]
"mbd"                ndarray(n,)
"mei"                ndarray(n,)
```
Verbatim from source (lines 434-456):
```rust
dict.set_item("mbd_mei_d", vec_to_numpy1d(py, r.mbd_mei_d))?;
dict.set_item("mei_mbd_d", vec_to_numpy1d(py, r.mei_mbd_d))?;
dict.set_item("mbd_mei_t", vec_to_numpy1d(py, r.mbd_mei_t))?;
dict.set_item("mei_mbd_t", vec_to_numpy1d(py, r.mei_mbd_t))?;
dict.set_item("mbd_mei_t2", vec_to_numpy1d(py, r.mbd_mei_t2))?;
dict.set_item("mei_mbd_t2", vec_to_numpy1d(py, r.mei_mbd_t2))?;
dict.set_item("shape_outliers", r.shape_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("magnitude_outliers", r.magnitude_outliers.into_iter().map(|x| x as i64).collect::<Vec<i64>>())?;
dict.set_item("mbd", vec_to_numpy1d(py, r.mbd))?;
dict.set_item("mei", vec_to_numpy1d(py, r.mei))?;
```

**Detection challenge:** depthgram shares `"mbd"/"mei"` keys with the existing `outliergram` branch. The existing branch already handles `"mei"` and `"mbd"` but does NOT have `"mbd_mei_d"`. Detection trigger: `"mbd_mei_d" in raw` (unique to depthgram). The existing `outliergram` branch must be checked BEFORE the generic `has_outliergram` (`"mei" in raw and "mbd" in raw`) fallback, or the depthgram case must be tested first with the stricter key.

Grounded scalars to emit:
| Output key | Source | Reduction |
|------------|--------|-----------|
| `n_obs` | `len(raw["mbd"])` | `int()` |
| `n_shape_outliers` | `len(raw["shape_outliers"])` | `int()` |
| `n_magnitude_outliers` | `len(raw["magnitude_outliers"])` | `int()` |
| `shape_outlier_fraction` | n_shape_outliers / n_obs | `float()` |
| `magnitude_outlier_fraction` | n_magnitude_outliers / n_obs | `float()` |
| `mbd_range` | `[float(np.min(mbd)), float(np.max(mbd))]` | list[float] |
| `mei_range` | `[float(np.min(mei)), float(np.max(mei))]` | list[float] |
| `has_depthgram` | `True` | `bool` |

---

## ADV-04: Existing Outliers Builder Structure

[VERIFIED: python/fdars/advisor/aspects/outliers.py:1-121]

`_build_outliers_diagnostics(raw: dict, **kwargs) -> dict`:
- Infers `n_obs` from the first present array among `("outliers", "magnitude", "shape", "mei", "mbd")` (line 73)
- Checks `"outliers" in raw` for n_outliers/fraction (line 83)
- Checks `"threshold" in raw` (line 95)
- Checks `"magnitude" in raw and "shape" in raw` → `has_magnitude_shape` (line 98)
- Checks `"mei" in raw and "mbd" in raw` → `has_outliergram` (line 110)
- Returns a single flat dict with ALL fields always present (as `None` when inapplicable)

**Extension strategy:** The function currently handles 4 shapes. We add 4 new detection blocks at the END, following the same `if key in raw:` / else pattern. The `n_obs` inference at the top (line 73) must be extended to include `"tvd"` (tvdmss) and `"shape_index"` (muod) as additional probe keys in the priority list. The existing blocks are unchanged.

**Key ordering conflict to fix:** The existing `has_outliergram` block (line 110) triggers on `"mei" in raw and "mbd" in raw`. A depthgram result ALSO has both `"mei"` and `"mbd"`, so the depthgram detection MUST be checked first (with `"mbd_mei_d" in raw`) before the generic outliergram fallback. This is the only ordering constraint.

---

## ADV-05: Exact Result-Dict Keys for New Regression Models

### functional_glm → `fdars.regression.functional_glm`
[VERIFIED: src/regression_mod.rs:1095-1126]

15 keys emitted by `functional_glm_result_to_pydict` (the comment at line 1088 says "14 non-fpca struct fields plus a derived 'family' string"):
```
"intercept"           float
"beta_t"              ndarray(m,)
"beta_se"             ndarray(m,)
"gamma"               ndarray(q,)  — scalar covariate coefficients; empty if none
"fitted_values"       ndarray(n,)
"linear_predictors"   ndarray(n,)
"ncomp"               int
"coefficients"        ndarray(ncomp,)
"std_errors"          ndarray(ncomp,)
"log_likelihood"      float
"deviance"            float
"iterations"          int          — NOTE: key is "iterations", NOT "n_iter"
"aic"                 float
"bic"                 float
"family"              str          — "binomial", "poisson", "gamma", or "gaussian"
```
Verbatim from source (lines 1100-1124):
```rust
dict.set_item("intercept", r.intercept)?;
dict.set_item("log_likelihood", r.log_likelihood)?;
dict.set_item("deviance", r.deviance)?;
dict.set_item("iterations", r.iterations)?;
dict.set_item("aic", r.aic)?;
dict.set_item("bic", r.bic)?;
dict.set_item("family", family_str)?;
```

**CRITICAL:** The CONTEXT.md and requirements doc refer to `n_iter/converged` — the actual key is `"iterations"` (an int) and there is NO `"converged"` key in the shipped dict. The builder must use `"iterations"` not `"n_iter"`.

Grounded scalars to emit:
| Output key | Source | Reduction |
|------------|--------|-----------|
| `n_obs` | `len(raw["fitted_values"])` via existing n_obs path | `int()` |
| `deviance` | `float(raw["deviance"])` | `float()` |
| `aic` | `float(raw["aic"])` | `float()` |
| `bic` | `float(raw["bic"])` | `float()` |
| `log_likelihood` | `float(raw["log_likelihood"])` | `float()` |
| `iterations` | `int(raw["iterations"])` | `int()` |
| `ncomp` | `int(raw["ncomp"])` | `int()` |
| `family` | `str(raw["family"])` | `str` — string, not numeric; safe for grounding |
| `has_functional_glm` | `True` | `bool` |
| `residuals` handling | `raw.get("residuals")` is absent — GLM has no residuals key | → existing residual block yields `None` for all residual fields |

Detection trigger: `"deviance" in raw` (unique to functional_glm among all existing regression result shapes; none of `fregre_lm/pls/l1/huber/np/fosr/fosr_fpc` expose a `"deviance"` key).

### concurrent_regression → `fdars.regression.concurrent_regression`
[VERIFIED: src/regression_mod.rs:988-1000]

5 keys emitted by `concurrent_regr_result_to_pydict`:
```
"beta_curve"  ndarray(p, m) — coefficient curves; p predictors × m grid points
"intercept"   ndarray(m,)   — intercept curve
"fitted"      ndarray(n, m) — fitted functional responses
"residuals"   ndarray(n, m) — residuals; 2-D (n × m), NOT 1-D
"argvals"     ndarray(m,)   — evaluation grid
```
Verbatim from source (lines 994-999):
```rust
dict.set_item("beta_curve", fdmatrix_to_numpy2d(py, &r.beta_curve))?;
dict.set_item("intercept", vec_to_numpy1d(py, r.intercept))?;
dict.set_item("fitted", fdmatrix_to_numpy2d(py, &r.fitted))?;
dict.set_item("residuals", fdmatrix_to_numpy2d(py, &r.residuals))?;
dict.set_item("argvals", vec_to_numpy1d(py, r.argvals))?;
```

**Key fact:** `residuals` is shape `(n, m)` — 2-D, same as `fosr`/`fosr_fpc`. The existing `res.ndim == 1` guard in the regression builder (line 86) will correctly produce `None` for all residual scalar fields. We need to add a NEW branch for concurrent_regression that computes a fit scalar from the 2-D residuals.

Grounded scalars to emit:
| Output key | Source | Reduction |
|------------|--------|-----------|
| `n_obs` | `np.asarray(raw["fitted"]).shape[0]` via existing `"fitted"` path | `int()` |
| `n_predictors` | `np.asarray(raw["beta_curve"]).shape[0]` | `int()` — rows of beta_curve = p predictors |
| `residual_rms` | `float(np.sqrt(np.mean(np.asarray(raw["residuals"])**2)))` | `float()` — RMS over all n×m cells |
| `residual_max_abs` | `float(np.max(np.abs(np.asarray(raw["residuals"]))))` | `float()` |
| `has_concurrent_regression` | `True` | `bool` |

Detection trigger: `"beta_curve" in raw` (unique to concurrent_regression; no other existing regression variant exposes this key — `fosr`/`fosr_fpc` use `"beta"` not `"beta_curve"`).

---

## ADV-05: Existing Regression Builder Structure

[VERIFIED: python/fdars/advisor/aspects/regression.py:1-130]

`_build_regression_diagnostics(raw, **kwargs) -> dict`:
- Infers `n_obs` from `"fitted_values"` (line 63) or `"fitted"` (line 65); `None` otherwise
- Guards `r_squared` presence (line 73)
- Guards `residuals` 1-D (line 86 — `res.ndim == 1`)
- Guards `"beta_t" in raw` for `beta_t_range` (line 107)
- `has_fosr`: `"fitted" in raw and ndim == 2` (line 124)

**Extension strategy:** Add two new detection blocks BEFORE the `return diag` statement:
1. `if "deviance" in raw:` — functional_glm branch
2. `if "beta_curve" in raw:` — concurrent_regression branch

The existing `n_obs` inference already handles `"fitted_values"` (GLM) and `"fitted"` (concurrent_regression via the 2-D path), so those still yield correct n_obs values without change. The existing `has_fosr` flag will be `True` for concurrent_regression (it has `"fitted"` as 2-D) — this is a harmless false positive since concurrent_regression callers can also check `has_concurrent_regression`.

---

## Group B Feasibility Decision

### elastic_multinomial via `classification` aspect — INCLUDE

[VERIFIED: src/classification_mod.rs:278-295]

`elastic_multinomial_result_to_pydict` emits 5 keys:
```
"n_classes"           int
"classes"             ndarray(K,) — 0-indexed class labels
"train_probabilities" ndarray(n, K)
"predicted_classes"   ndarray(n,)
"train_accuracy"      float        — scalar; fdars-computed (correct/n_obs)
```
Verbatim from source (lines 283-295):
```rust
dict.set_item("n_classes", r.n_classes)?;
dict.set_item("classes", usize_vec_to_numpy1d(py, r.classes))?;
dict.set_item("train_probabilities", fdmatrix_to_numpy2d(py, &r.train_probabilities))?;
dict.set_item("predicted_classes", usize_vec_to_numpy1d(py, r.predicted_classes))?;
dict.set_item("train_accuracy", r.train_accuracy)?;
```

**Verdict: FEASIBLE.** `train_accuracy` is a native Rust `f64` field written directly as a Python float (no conversion wrapper) — it is genuinely fdars-computed. `n_classes` is an `int`. These are both grounded scalars the advisor can cite.

Extend `python/fdars/advisor/aspects/classification.py`: add a detection block for `"train_accuracy" in raw` (unique to elastic_multinomial — the existing LDA/QDA/kNN/kernel/DD results only have `"accuracy"`, never `"train_accuracy"`; `fclassif_cv` has `"error_rate"` and `"fold_errors"`).

**IMPORTANT:** The existing `classification.py` builder already populates `diag["n_classes"]` from the CALLER-SUPPLIED `n_classes` parameter (line 99). The `elastic_multinomial` result dict also has a `"n_classes"` key in the RAW dict. In the new branch, use `int(raw["n_classes"])` to override the caller-supplied value with the fdars-computed one. Emit:
- `n_classes`: `int(raw["n_classes"])` — override caller-supplied None with fdars-computed count
- `train_accuracy`: `float(raw["train_accuracy"])`
- `train_error_rate`: `float(1.0 - raw["train_accuracy"])`
- `has_elastic_multinomial`: `bool(True)`

Primer addition for `_ASPECT_PRIMERS["classification"]`: add a sentence about elastic multinomial train accuracy vs. CV accuracy.

### pace_fpca via `fpca` aspect — INCLUDE

[VERIFIED: src/pace_fpca_mod.rs:164-188]

`pace_fpca_result_to_pydict` emits 10 keys:
```
"mean"          ndarray(m,)
"eigenvalues"   ndarray(ncomp,)    — already-scaled eigenvalues; ncomp = ACTUAL count
"eigenfunctions" ndarray(m, ncomp)
"scores"        ndarray(n, ncomp)
"fitted"        ndarray(n, m)
"fitted_lower"  ndarray(n, m)
"fitted_upper"  ndarray(n, m)
"argvals"       ndarray(m,)
"sigma2"        float               — measurement error variance (echoed from config)
"ncomp"         int                 — ACTUAL components extracted
```
Verbatim from source (lines 169-187):
```rust
dict.set_item("eigenvalues", vec_to_numpy1d(py, r.eigenvalues))?;
dict.set_item("sigma2", r.sigma2)?;
dict.set_item("ncomp", r.ncomp)?;
```

**Verdict: FEASIBLE.** `eigenvalues` is a Vec<f64> already of length `ncomp` (actual). The existing `_eigenvalues_to_variance_cumulative` helper in `_utils.py` converts eigenvalues to cumulative variance explained ratios — this is the exact same operation the existing `fpca` aspect uses for the standard FPCA result. `sigma2` and `ncomp` are also grounded scalars.

**CRITICAL note (VERIFIED: python/fdars/advisor/aspects/fpca.py:16-57):** The existing `_build_fpca_diagnostics` detects `sv_raw = raw.get("singular_values")` — it checks for `"singular_values"`, not `"eigenvalues"`. The pace_fpca result has `"eigenvalues"` directly (not `"singular_values"`). Use `"eigenvalues" in raw` to detect pace_fpca — this key is NOT present in the standard FPCA result (which has `"singular_values"`). The detection is unambiguous.

Extend `python/fdars/advisor/aspects/fpca.py`: add detection block for `"eigenvalues" in raw`. Emit:
- `ncomp`: `int(raw["ncomp"])`
- `sigma2`: `float(raw["sigma2"])`
- `variance_explained_cumulative`: `_eigenvalues_to_variance_cumulative(raw["eigenvalues"])` (list[float])
- `variance_explained_first`: first element of cumulative list (`float`)
- `has_pace_fpca`: `bool(True)`

---

## ITP Advisor Coverage — DEFER

The three ITP functions (`itp_one_pop`, `itp_two_pop`, `itp_flm`) return `ItpResult` containing vector `adjusted_pvalues` (1-D, length m) and `unadjusted_pvalues` (1-D, length m) plus `statistic_curve` (1-D, length m). There is no single scalar p-value — the entire inference result is a pointwise vector. The minimum adjusted p-value could be reported, but this would require choosing an arbitrary reduction (min, fraction-significant, etc.) that the grounding guard cannot validate against a single fdars-supplied scalar. Defer per CONTEXT.md.

---

## MCP Guard-Sync Confirmation

[VERIFIED: python/fdars/mcp/server.py:63-83]

`_DIAGNOSTICS_METHODS` currently contains (verbatim from source lines 64-82):
```python
_DIAGNOSTICS_METHODS = frozenset({
    "alignment", "fpca", "basis", "smoothing", "clustering", "depth",
    "outliers", "classification", "represent", "regression", "regression_cv",
    "spm", "scoring", "inference",
})
```

`_supported` in `advisor/__init__.py` (lines 125-135) contains the identical set.

All new branches (`tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` for ADV-04; `functional_glm`, `concurrent_regression` for ADV-05; `elastic_multinomial` for classification; `pace_fpca` for fpca) are extensions to EXISTING aspect keys: `"outliers"`, `"regression"`, `"classification"`, `"fpca"`. No new keys added.

**Conclusion: `test_diagnostics_methods_match_advisor_supported` stays green without any changes to server.py, _runner.py, or `__init__.py`'s `_supported` set.**

---

## Architecture Patterns

### Pattern 1: Key-Presence Branch Detection

Each new detector is identified by a discriminator key unique to its result shape. Branches are checked in order; the FIRST matching block fires. All existing branches are preserved unchanged.

```python
# Detection order matters — depthgram BEFORE outliergram (shared mei/mbd keys)
if "mbd_mei_d" in raw:
    # depthgram branch
    ...
    diag["has_depthgram"] = True

elif "amplitude_outliers" in raw:
    # muod branch
    ...
    diag["has_muod"] = True

elif "tvd" in raw and "mss" in raw:
    # tvdmss branch
    ...
    diag["has_tvdmss"] = True

elif "union_outliers" in raw:
    # sequential_transform_outliers branch
    ...
    diag["has_sequential_transform"] = True

# Existing outliergram block — unchanged, fires last (mei/mbd without mbd_mei_d)
# Source: aspects/outliers.py:110
```

### Pattern 2: Float Coercion for List-of-int Index Sets

Index sets (e.g. `magnitude_outliers`) are `list[int]` in the fdars result — they are already Python native types. Use `len()` to get the count; no `np.asarray` needed.

```python
# Source: aspects/outliers.py:84-86 (existing pattern for bool array)
if "magnitude_outliers" in raw and isinstance(raw["magnitude_outliers"], list):
    n_magnitude_outliers = int(len(raw["magnitude_outliers"]))
```

### Pattern 3: 2-D Residual Summary (concurrent_regression)

Mirrors the existing 1-D guard — extend with a 2-D path:

```python
# Source: aspects/regression.py:85-95 (1-D guard)
res = np.asarray(raw.get("residuals", []))
if res.ndim == 1 and res.size > 0:
    # ... existing scalar residual stats ...
else:
    # existing None assignments

# NEW: 2-D concurrent_regression residual path
if "beta_curve" in raw:
    res_2d = np.asarray(raw.get("residuals", np.zeros((0,0))))
    if res_2d.ndim == 2 and res_2d.size > 0:
        diag["residual_rms"] = float(np.sqrt(np.mean(res_2d ** 2)))
        diag["residual_max_abs"] = float(np.max(np.abs(res_2d)))
    else:
        diag["residual_rms"] = None
        diag["residual_max_abs"] = None
    diag["n_predictors"] = int(np.asarray(raw["beta_curve"]).shape[0])
    diag["has_concurrent_regression"] = True
```

### Anti-Patterns to Avoid

- **Using index lists as scalar evidence:** `raw["magnitude_outliers"]` is `list[int]` — never assign the list itself to a diagnostic key. Only `len()` of the list is grounded.
- **Fabricating n_obs for sequential_transform_outliers:** The result has no array from which n_obs can be recovered. Do NOT emit an `outlier_fraction` for this detector.
- **Checking `"mbd" in raw` before `"mbd_mei_d"`:** This would misfire depthgram into the outliergram branch. Check the more specific key first.
- **Using `"iterations"` vs `"n_iter"`:** The actual key is `"iterations"` (`regression_mod.rs:1112`); the requirements doc says "n_iter" loosely — the Rust source is authoritative.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Eigenvalue → variance explained | Custom cumsum logic | `_eigenvalues_to_variance_cumulative` from `_utils.py` | Already tested; handles zero-total edge case |
| Numpy scalar coercion | Custom casting | `float()` / `int()` wrapping | Established pattern throughout all existing aspect builders |
| Recursive numpy check in tests | Custom walker | Copy `check_no_numpy` from `test_advisor_inference.py:247-255` | Canonical pattern; checks `np.generic` subclasses |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing; version installed in .venv) |
| Config file | `pyproject.toml` (pytest section exists) |
| Quick run command | `pytest tests/test_advisor_outliers_v6.py tests/test_advisor_regression_v6.py tests/test_advisor_group_b.py -x` |
| Full suite command | `pytest tests/ -x --tb=short` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADV-04 | tvdmss grounded scalars emitted | unit offline | `pytest tests/test_advisor_outliers_v6.py::TestTvdmss -x` | ❌ Wave 0 |
| ADV-04 | muod grounded scalars emitted | unit offline | `pytest tests/test_advisor_outliers_v6.py::TestMuod -x` | ❌ Wave 0 |
| ADV-04 | sequential_transform_outliers scalars emitted | unit offline | `pytest tests/test_advisor_outliers_v6.py::TestSeqTransform -x` | ❌ Wave 0 |
| ADV-04 | depthgram scalars emitted | unit offline | `pytest tests/test_advisor_outliers_v6.py::TestDepthgram -x` | ❌ Wave 0 |
| ADV-04 | depthgram detected before outliergram | unit offline | `pytest tests/test_advisor_outliers_v6.py::TestOrdering -x` | ❌ Wave 0 |
| ADV-04 | determinism: byte-identical json.dumps for all 4 new branches | unit offline | `pytest tests/test_advisor_outliers_v6.py::TestDeterminism -x` | ❌ Wave 0 |
| ADV-04 | no numpy scalars in output (check_no_numpy) | unit offline | included in determinism test class | ❌ Wave 0 |
| ADV-04 | MCP guard-sync test stays green | integration | `pytest tests/test_mcp_server.py::test_diagnostics_methods_match_advisor_supported -x` | ✅ exists |
| ADV-05 | functional_glm scalars: deviance/aic/bic/log_likelihood/iterations/ncomp | unit offline | `pytest tests/test_advisor_regression_v6.py::TestFunctionalGlm -x` | ❌ Wave 0 |
| ADV-05 | concurrent_regression: residual_rms, n_predictors | unit offline | `pytest tests/test_advisor_regression_v6.py::TestConcurrentRegression -x` | ❌ Wave 0 |
| ADV-05 | regression determinism + no numpy for new branches | unit offline | `pytest tests/test_advisor_regression_v6.py::TestDeterminism -x` | ❌ Wave 0 |
| ADV-05 (Group B) | elastic_multinomial: n_classes/train_accuracy/train_error_rate | unit offline | `pytest tests/test_advisor_group_b.py::TestElasticMultinomial -x` | ❌ Wave 0 |
| ADV-05 (Group B) | pace_fpca: ncomp/sigma2/variance_explained_cumulative | unit offline | `pytest tests/test_advisor_group_b.py::TestPaceFpca -x` | ❌ Wave 0 |
| ADV-05 (Group B) | Group B determinism + no numpy | unit offline | `pytest tests/test_advisor_group_b.py::TestDeterminism -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_advisor_outliers_v6.py tests/test_advisor_regression_v6.py tests/test_advisor_group_b.py tests/test_mcp_server.py::test_diagnostics_methods_match_advisor_supported -x`
- **Per wave merge:** `pytest tests/ -x --tb=short`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_advisor_outliers_v6.py` — covers ADV-04 all 4 detector branches
- [ ] `tests/test_advisor_regression_v6.py` — covers ADV-05 functional_glm + concurrent_regression
- [ ] `tests/test_advisor_group_b.py` — covers elastic_multinomial + pace_fpca advisor branches

*(Existing test infrastructure is sufficient for framework/config; only new test files are needed.)*

---

## Offline Test Pattern (from test_advisor_inference.py precedent)

The canonical test structure for a new `build_diagnostics` branch is:

```python
# Source: tests/test_advisor_inference.py (full file read this session)

# 1. Fixed synthetic result dict (no fdars call, no RNG)
_TVDMSS_RESULT = {
    "magnitude_outliers": [2, 5],    # list[int] — already native Python
    "shape_outliers": [7],
    "tvd": [0.8, 0.7, 0.3, 0.6, 0.9, 0.4, 0.7, 0.1, 0.8, 0.6],  # n=10
    "mss": [0.2, 0.3, 0.7, 0.4, 0.1, 0.6, 0.3, 0.9, 0.2, 0.4],
}

# 2. Basic correctness
def test_tvdmss_build_diagnostics_basic():
    from fdars.advisor import build_diagnostics
    diag = build_diagnostics(_TVDMSS_RESULT, method="outliers")
    assert diag["method"] == "outliers"
    assert diag["n_obs"] == 10
    assert diag["n_magnitude_outliers"] == 2
    assert diag["n_shape_outliers"] == 1
    assert isinstance(diag["magnitude_outlier_fraction"], float)
    assert abs(diag["magnitude_outlier_fraction"] - 0.2) < 1e-9
    assert diag["has_tvdmss"] is True
    json.dumps(diag, sort_keys=True)

# 3. No numpy + determinism
def test_tvdmss_deterministic():
    from fdars.advisor import build_diagnostics
    d1 = build_diagnostics(_TVDMSS_RESULT, method="outliers")
    d2 = build_diagnostics(_TVDMSS_RESULT, method="outliers")
    assert d1 == d2
    s1 = json.dumps(d1, sort_keys=True)
    s2 = json.dumps(d2, sort_keys=True)
    assert s1 == s2
    def check_no_numpy(obj):  # source: test_advisor_inference.py:247-255
        assert not isinstance(obj, np.generic)
        if isinstance(obj, dict):
            for v in obj.values(): check_no_numpy(v)
        elif isinstance(obj, list):
            for v in obj: check_no_numpy(v)
    check_no_numpy(d1)

# 4. Grounding check (values discoverable in json.dumps)
def test_tvdmss_grounding():
    from fdars.advisor import build_diagnostics
    from fdars.advisor.providers._validate import _extract_numbers
    diag = build_diagnostics(_TVDMSS_RESULT, method="outliers")
    diag_json = json.dumps(diag, sort_keys=True)
    found = set(_extract_numbers(diag_json))
    # n_magnitude_outliers=2 must be discoverable
    assert any("2" in n or n in "2" for n in found)
```

---

## _ASPECT_PRIMERS Extensions

The `"outliers"` primer in `_prompts.py` (line 53) currently reads:
```
"- Functional outlier detection: outlier_fraction is the proportion flagged. ..."
```
It should be extended to mention:
- `tvdmss`: `n_magnitude_outliers`/`n_shape_outliers` as separate magnitude/shape counts; `tvd_range`/`mss_range` as the score spans.
- `muod`: three distinct counts (magnitude/shape/amplitude); `*_index_range` as the outlyingness spans.
- `depthgram`: MBD+MEI combined diagram; `n_shape_outliers`/`n_magnitude_outliers`.
- `sequential_transform_outliers`: `n_union_outliers` = union across all transform stages; `n_transforms` = how many stages were applied.

The `"regression"` primer (line 94) should add: `deviance` measures model fit for GLM (lower = better fit); `aic`/`bic` for model comparison; `iterations` for convergence; `residual_rms` for concurrent regression overall fit quality.

---

## Common Pitfalls

### Pitfall 1: Depthgram/Outliergram Key Collision
**What goes wrong:** `depthgram` result has `"mei"` and `"mbd"` → existing outliergram branch fires, producing wrong diagnostics.
**Why it happens:** Detection order: the generic `has_outliergram` check is too broad.
**How to avoid:** Check `"mbd_mei_d" in raw` FIRST before `"mei" in raw and "mbd" in raw`.
**Warning signs:** `has_depthgram` is never True in tests even when feeding a depthgram result.

### Pitfall 2: "iterations" vs "n_iter" in functional_glm
**What goes wrong:** `raw.get("n_iter")` returns None; diagnostic is silently None rather than the actual iteration count.
**Why it happens:** Requirements doc says "n_iter" loosely but the Rust source uses `r.iterations` → `dict.set_item("iterations", ...)`.
**How to avoid:** Use `raw.get("iterations")` — confirmed from `regression_mod.rs:1112`.
**Warning signs:** `iterations` diagnostic is always None; test with a GLM result reveals the key.

### Pitfall 3: concurrent_regression residuals are 2-D
**What goes wrong:** Applying the existing 1-D residual stats path to a 2-D array silently computes wrong values (or crashes on `.ndim != 1`).
**Why it happens:** `concurrent_regression` returns `residuals` shape `(n, m)` (confirmed `regression_mod.rs:997`); `fosr`/`fosr_fpc` same.
**How to avoid:** Use the existing `res.ndim == 1` guard; add a separate 2-D branch for concurrent_regression. The `has_fosr` flag also fires for concurrent_regression (both have 2-D `"fitted"`); `has_concurrent_regression` is the specific discriminator.
**Warning signs:** `residual_mean` is not None for a concurrent_regression result.

### Pitfall 4: n_obs not recoverable from sequential_transform_outliers
**What goes wrong:** Attempting `len(raw["union_outliers"])` gives n_union_outliers (outlier count), not n_obs. `per_transform_outliers` is a list-of-dicts with no per-curve-count.
**Why it happens:** The SeqTransformOutliers struct does not carry the observation count; it only carries outlier indices.
**How to avoid:** Do NOT emit `outlier_fraction` for this detector. Only emit `n_union_outliers` and `n_transforms` as grounded scalars.
**Warning signs:** `outlier_fraction` would be computed as `len(union) / len(union)` = 1.0, which is wrong.

### Pitfall 5: tvdmss vs muod disambiguation
**What goes wrong:** Both have `"shape_outliers"` (list[int]) and `"magnitude_outliers"` (list[int]). Checking `"shape_outliers" in raw` is not sufficient to identify either.
**Why it happens:** Overlapping key names across detectors.
**How to avoid:** Use `"tvd" in raw and "mss" in raw` for tvdmss; `"amplitude_outliers" in raw` for muod.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `_extract_numbers` in `fdars.advisor.providers._validate` behaves as in the inference test (extracts numeric strings from JSON) | Grounding test pattern | Test would fail to prove grounding if extraction behavior differs |

**If this table is empty of items other than A1:** All key facts were verified from source files read this session. The `fpca.py` aspect was read and confirmed to use `"singular_values"` (not `"eigenvalues"`) as its detection input — pace_fpca's `"eigenvalues"` key is distinct. The `classification.py` builder's use of `"n_classes"` as an OUTPUT key (from caller parameter) was read and the elastic_multinomial detection trigger was updated to use `"train_accuracy" in raw` (not `"n_classes" in raw`) to avoid any collision.

---

## Sources

### Primary (HIGH confidence — read from source files this session)

- `src/outliers_mod.rs:165-495` — exact keys for tvdmss, muod, sequential_transform_outliers, depthgram result dicts
- `src/regression_mod.rs:988-1126` — exact keys for concurrent_regression and functional_glm result dicts
- `src/pace_fpca_mod.rs:164-188` — exact 10 keys for PaceFpcaResult
- `src/classification_mod.rs:278-295` — exact 5 keys for ElasticMultinomialResult
- `python/fdars/advisor/aspects/outliers.py:1-121` — existing `_build_outliers_diagnostics` structure
- `python/fdars/advisor/aspects/regression.py:1-130` — existing `_build_regression_diagnostics` structure
- `python/fdars/advisor/aspects/inference.py:1-222` — precedent for grounded scalar emission and test structure
- `python/fdars/advisor/aspects/_utils.py:1-55` — `_eigenvalues_to_variance_cumulative` helper
- `python/fdars/advisor/aspects/fpca.py:16-57` — existing `_build_fpca_diagnostics`; uses `"singular_values"` detection (not `"eigenvalues"`); confirms pace_fpca detection trigger is unambiguous
- `python/fdars/advisor/aspects/classification.py:1-133` — existing `_build_classification_diagnostics`; `"n_classes"` is an OUTPUT key (from caller param); `"train_accuracy"` is the safe elastic_multinomial detection trigger
- `python/fdars/advisor/__init__.py:125-135` — `_supported` set verbatim
- `python/fdars/advisor/_prompts.py:45-143` — `_ASPECT_PRIMERS` verbatim
- `python/fdars/mcp/server.py:63-83` — `_DIAGNOSTICS_METHODS` verbatim
- `python/fdars/mcp/_runner.py:59-61` — `_RUNNABLE_METHODS` verbatim
- `tests/test_advisor_inference.py:1-420` — canonical offline test pattern

---

## Metadata

**Confidence breakdown:**
- Result-dict key inventory: HIGH — read from Rust source, not docs or training memory
- Extension strategy: HIGH — directly mirrors established patterns in existing aspect files
- MCP guard-sync: HIGH — sets read verbatim and confirmed identical
- Group B feasibility: HIGH — `train_accuracy` (float scalar), `eigenvalues` (ndarray) confirmed in source
- ITP deferral: HIGH — vector-only output confirmed; no grounded scalar available

**Research date:** 2026-08-21
**Valid until:** This research is against the already-shipped (compiled) v6.0 extension module. Python-only phase — valid indefinitely unless fdars-core is bumped again.
