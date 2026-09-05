# Phase 72: Advisor Extension - Research

**Researched:** 2026-09-04
**Domain:** Python advisor aspect system + MCP guard-sync
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Exactly ADV-01: new `fts` + `frechet` aspects; extend `regression`/`classification`/`spm`.
  Clustering + density_fda advisor coverage DEFERRED.
- **Grounding invariant (hard):** every diagnostic value is a real fdars-computed native Python
  `float`/`int`/`bool`/`list`/`None` — NO Python-derived synthetic numbers and NO numpy
  scalars entering `json.dumps`. Cast every numpy scalar with `float()`/`int()`; guard optional
  keys.
- **Determinism / serialization:** `json.dumps(build_diagnostics(raw))` succeeds for each new
  aspect + each extended method; two calls on the same input return an equal dict.
- **fts + frechet are DIAGNOSTICS-ONLY:** both go into `_DIAGNOSTICS_METHODS` ONLY — NEITHER
  is added to `_RUNNABLE_METHODS`. `frechet` specifically must NOT be runnable (SC3).
- **Guard-sync atomicity:** the `_DIAGNOSTICS_METHODS`/`_RUNNABLE_METHODS` edits across all
  three mcp files land in the SAME commit as the aspect registration (ADV-02).
- **MCP compute path stays provably LLM-free:** no LLM in the number path.

### Claude's Discretion
- Exact diagnostic fields per new aspect/method are method-accuracy choices — derive from each
  function's real 0.33 result-dict keys. Only surface values fdars actually computes.
- Whether each EXTENDED method (fof/fam/mfpca/shapelet_classifier) is added to
  `_RUNNABLE_METHODS` or stays diagnostics-only: research/planning decides per method; frechet +
  fts stay diagnostics-only regardless.

### Deferred Ideas (OUT OF SCOPE)
- Advisor coverage for advanced clustering (dbscan/kcfc/funfem/align) + density_fda.
- FRE-RUN-01: promote frechet to `_RUNNABLE_METHODS` — future.
- DOCS-01 (Phase 73).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADV-01 | New/extended advisor aspects for bound capabilities — `fts` aspect, `frechet` aspect (diagnostics-only), extend `regression`/`classification`/`spm` for new methods | Sections: Aspect Pattern, Diagnostic Field Lists, Code Examples |
| ADV-02 | MCP guard-sync stays consistent — updated atomically; `test_guard_sync_version_independent.py` and per-aspect `json.dumps` serialization tests pass; MCP compute path provably LLM-free | Sections: Guard-Sync Mechanics, Tests |
</phase_requirements>

---

## Summary

Phase 72 extends the advisor layer to cover the five new fdars capability families added in
Phases 67-71. The work is pure Python: no new PyO3 bindings. Two new aspect files
(`fts.py`, `frechet.py`) are created under `python/fdars/advisor/aspects/`; three existing
aspect files (`regression.py`, `classification.py`, `spm.py`) each gain additional branches
for newly-bound methods. Every new value in every diagnostic dict must trace back to a key in
the real fdars-computed PyDict returned by the corresponding function. No synthetic numbers.

The MCP guard-sync (ADV-02) is a three-location change that MUST land in the same commit as
the aspect code: `python/fdars/mcp/server.py` (_DIAGNOSTICS_METHODS), `_runner.py`
(_RUNNABLE_METHODS unchanged for fts/frechet, extended methods stay diagnostics-only),
`_pipeline.py` (imports _RUNNABLE_METHODS from _runner — no direct change needed), plus
the hard-coded frozenset in `tests/test_guard_sync_version_independent.py`. The advisor
`_supported` set in `__init__.py:build_diagnostics` is a fourth co-equal location that must
be updated atomically.

The LLM-free proof is structural: `build_diagnostics` uses only numpy + fdars submodule
calls (the one live call in `spm.py` is guarded try/except and imports fdars, not anthropic).
The LLM only calls `advise(diagnostics, ...)` AFTER `build_diagnostics` returns — a clean
Stage 1 / Stage 2 separation already enforced by the existing architecture.

**Primary recommendation:** Mirror `regression.py`'s discipline exactly for all new/extended
branches — float()/int() casts on every value, guarded optional keys with `if "key" in raw`,
None fallback for every field, no numpy scalars in the return dict.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Diagnostic field computation | Python advisor layer | fdars native functions | Aspect builders run in Python, call fdars for live values (spm path) |
| Number path (grounding) | Advisor `build_diagnostics` | fdars PyDict result | Strictly pre-LLM; LLM only reads the finished dict |
| Method dispatch | `__init__.py:build_diagnostics` | `_pipeline.py` | Central dispatcher; _pipeline defers to build_diagnostics per stage |
| Guard-sync validation | `test_guard_sync_version_independent.py` | `server.py`, `_runner.py` | Test recovers advisor's supported set via ValueError parsing |
| MCP runnability | `_runner.py:_RUNNABLE_METHODS` | `server.py:_RUNNABLE_METHODS` | These two must be identical; _pipeline.py imports from _runner |

---

## Section 1: Aspect Pattern (Canonical — Read regression.py)

### Function Signature

Every aspect module exposes ONE public function with this signature:

```python
def _build_<aspect>_diagnostics(raw: dict, **kwargs) -> dict:
```

- `raw`: the native fdars output dict (already unwrapped from wrappers by `build_diagnostics`
  before dispatch)
- `**kwargs`: reserved for future per-method options; currently ignored
- Return: a plain-Python dict with `"method"` as the first key set to a string identifying
  the aspect

[VERIFIED: python/fdars/advisor/aspects/regression.py:27-28, spm.py:36-37, classification.py:36-42]

### Registration in `build_diagnostics` (`__init__.py`)

The dispatch table in `python/fdars/advisor/__init__.py:141-157` (the `_supported` set) and
the if-chain at lines 173-232 both MUST be updated. The pattern is:

1. Add the new method string to `_supported` frozenset (line 141-157)
2. Add an `if method_lc == "<aspect>":` branch that imports and calls the new builder

Verbatim extract of the `_supported` set as of Phase 71 completion:

```python
_supported = {
    "alignment", "fpca", "basis", "smoothing", "clustering",
    "depth",
    "outliers",
    "classification",
    "represent",
    "regression", "regression_cv",
    "spm",
    "scoring",
    "inference",
}
```

[VERIFIED: python/fdars/advisor/__init__.py:141-157]

New entries to add: `"fts"`, `"frechet"`.

The dispatch branch template (from line 211-213):

```python
if method_lc == "regression":
    from fdars.advisor.aspects.regression import _build_regression_diagnostics  # noqa: PLC0415
    return _build_regression_diagnostics(raw, **kwargs)
```

[VERIFIED: python/fdars/advisor/__init__.py:211-213]

### The Grounding Discipline (verbatim from regression.py header)

```
All values in the returned dict are native Python types (float, int, bool,
list, None).  No NumPy scalars.  Two calls on the same input always return
an equal, JSON-serialisable dict.
```

[VERIFIED: python/fdars/advisor/aspects/regression.py:17-19]

Cast rules derived from reading regression.py + spm.py:
- Every numpy scalar: `float(np.asarray(raw["key"]).item())` or simply `float(raw["key"])`
- Every int-typed result: `int(raw["key"])`
- Every bool: `bool(x)`
- Every list of floats: `[float(v) for v in arr]`
- Optional key: `float(raw["key"]) if "key" in raw else None`
- Guard for None raw value: `float(x) if x is not None else None`
- 2D array summary (e.g. beta surface): extract shape as `(int(arr.shape[0]), int(arr.shape[1]))`
  or compute stats via float(np.max(arr)) etc.

The `has_<method>` discriminator pattern (from regression.py:159-208):
```python
has_something = "unique_key_for_this_method" in raw
diag["has_something"] = bool(has_something)
if has_something:
    diag["field"] = float(raw["field"]) if "field" in raw else None
else:
    diag["field"] = None
```

[VERIFIED: python/fdars/advisor/aspects/regression.py:159-208]

### Extension vs New Aspect

- **Extend** (`regression.py`, `classification.py`, `spm.py`): add a new `has_<method>` branch
  at the bottom of the existing builder function. The builder dispatches all variants of the
  same top-level method string.
- **New aspect** (`fts.py`, `frechet.py`): create a new file, add to `_supported`,
  add dispatch branch in `build_diagnostics`.

---

## Section 2: Diagnostic Field Lists (Grounded)

All result-dict keys below are VERIFIED from reading the Phase 67-71 SUMMARY files which record
the actual shipped PyDict keys. Every value claimed to be in the result dict was asserted by
tests in the corresponding phase.

### 2A. NEW ASPECT: `fts` (diagnostics-only, method string `"fts"`)

The `fts` aspect covers multiple function result shapes. Use `has_<fn>` discriminators to
distinguish them.

#### `ftsm` result dict

Keys: `"mean"` (m,), `"rotation"` (m, ncomp), `"scores"` (n, ncomp), `"fitted"` (n, m),
`"weights"` (m,), `"ncomp"` (int), `"ar_models"` (list of dicts with `"order"`, `"phi"`,
`"sigma2"`)

[VERIFIED: .planning/phases/67-functional-time-series-fts/67-01-SUMMARY.md — line 106:
"ftsm PyDict return: mean (m,), rotation (m, ncomp), scores (n, ncomp), fitted (n, m),
weights (m,), ncomp int, ar_models list of dicts"]

Diagnostic fields for `ftsm`:
- `has_ftsm = "ncomp" in raw and "ar_models" in raw` — discriminator
- `ncomp`: `int(raw["ncomp"])` — number of FTS components fitted
- `n_obs`: `int(np.asarray(raw["scores"]).shape[0])` — from scores array
- `n_points`: `int(np.asarray(raw["mean"]).shape[0])` — evaluation grid size
- `n_ar_models`: `int(len(raw["ar_models"]))` — should equal ncomp
- `ar_max_order`: `int(max(m["order"] for m in raw["ar_models"]))` if ar_models non-empty else None
- `ar_sigma2_max`: `float(max(m["sigma2"] for m in raw["ar_models"]))` — largest residual variance
- `fitted_rmse`: `float(np.sqrt(np.mean(np.asarray(raw["fitted"])**2)))` — overall reconstruction quality

NOTE: `ar_models` contains plain Python dicts (list of dicts assembled inline from PyList/PyDict
in Rust). Values like `m["order"]`, `m["sigma2"]` are native Python int/float from Rust binding.
Cast defensively anyway: `int(m["order"])`, `float(m["sigma2"])`.

#### `ftsm_forecast` / `ftsm_forecast_multistep` result dict

Keys: `"forecast"` (h, m), `"h"` (int)

[VERIFIED: .planning/phases/67-functional-time-series-fts/67-02-SUMMARY.md — line 14:
"ftsm_forecast #[pyfunction]: combined-function pattern, returns {forecast (h,m), h}"]

Diagnostic fields for forecast results:
- `has_forecast = "forecast" in raw and "h" in raw` — discriminator
- `h`: `int(raw["h"])` — forecast horizon
- `n_points`: `int(np.asarray(raw["forecast"]).shape[1])` — m evaluation points
- `forecast_mean`: `float(np.mean(np.asarray(raw["forecast"])))` — average forecast value

#### `stationarity_test` result dict

Keys: `"statistic"` (float), `"p_value"` (float), `"n_perm"` (int)

[VERIFIED: .planning/phases/67-functional-time-series-fts/67-03-SUMMARY.md — line 15:
"stationarity_test: PyDict {statistic, p_value, n_perm} with seed=42 default, deterministic"]

Diagnostic fields for stationarity:
- `has_stationarity = "p_value" in raw and "n_perm" in raw` — discriminator
- `stationarity_statistic`: `float(raw["statistic"])` if present else None
- `stationarity_p_value`: `float(raw["p_value"])` — permutation p-value in [0,1]
- `n_perm`: `int(raw["n_perm"])` — number of permutations used

#### `functional_acf` / `functional_pacf` result dict

Keys: `"lags"` (int64 array), `"acf"` (array), `"pacf"` (array), `"upper_band"` (array)

[VERIFIED: .planning/phases/67-functional-time-series-fts/67-03-SUMMARY.md — line 14:
"functional_acf: PyDict {lags (int64), acf, pacf, upper_band} with seed=42 default"]

Diagnostic fields for acf/pacf:
- `has_acf = "acf" in raw and "upper_band" in raw` — discriminator
- `n_lags`: `int(len(np.asarray(raw["lags"])))` — number of lags computed
- `acf_at_lag1`: `float(np.asarray(raw["acf"])[0])` if acf present and len>0 else None — first-lag autocorrelation
- `acf_decay`: derived as `float(np.asarray(raw["acf"])[-1])` (last lag value) — proxy for decay to zero

#### `dpca` result dict

Keys: `"filters"` (array), `"scores"` (N-2L, ncomp), `"eigenvalues"` (array), `"n_freqs"` (int),
`"filter_lag"` (int), `"ncomp"` (int), `"valid_range"` (tuple)

[VERIFIED: .planning/phases/67-functional-time-series-fts/67-04-SUMMARY.md — line 65:
"dpca bound returning {filters, scores (N-2L, ncomp), eigenvalues, n_freqs, filter_lag, ncomp,
valid_range tuple}"]

Diagnostic fields for dpca:
- `has_dpca = "filter_lag" in raw and "n_freqs" in raw` — discriminator (unique to dpca)
- `dpca_ncomp`: `int(raw["ncomp"])` — dynamic PCA components
- `n_freqs`: `int(raw["n_freqs"])` — frequency count
- `filter_lag`: `int(raw["filter_lag"])` — lag window
- `dpca_eigenvalues`: `[float(v) for v in np.asarray(raw["eigenvalues"])]` — dynamic eigenvalue spectrum

#### `fplsr` result dict

Keys: `"forecast"` (1, m), `"fitted"` (n-1, m), `"ncomp"` (int)

[VERIFIED: .planning/phases/67-functional-time-series-fts/67-02-SUMMARY.md — line 16:
"fplsr #[pyfunction]: standalone fit, returns {forecast (1,m), fitted (n-1,m), ncomp}"]

Diagnostic fields for fplsr:
- `has_fplsr = "fitted" in raw and "ncomp" in raw and "forecast" in raw and np.asarray(raw["forecast"]).shape[0] == 1` — discriminator (fplsr has 1-row forecast unlike ftsm 7-key)
- `fplsr_ncomp`: `int(raw["ncomp"])` — PLS components used
- `fplsr_fitted_rmse`: `float(np.sqrt(np.mean(np.asarray(raw["fitted"])**2)))` — leave-one-out fit quality

**Discriminator design note:** The `fts` aspect handles multiple result shapes that share some
keys. The safest discriminator hierarchy:
1. `stationarity_test`: `"n_perm" in raw` (unique)
2. `functional_acf/pacf`: `"upper_band" in raw` (unique)
3. `dpca`: `"filter_lag" in raw` (unique)
4. `fplsr`: `"fitted" in raw and "forecast" in raw and "ncomp" in raw and np.asarray(raw["forecast"]).ndim == 2 and np.asarray(raw["forecast"]).shape[0] == 1`
5. `ftsm`: `"ar_models" in raw` (unique to ftsm)
6. `ftsm_forecast`: `"h" in raw` (unique)

The builder tests each discriminator independently (not mutually exclusive) and sets `has_<fn>`
booleans plus the associated fields, with None fallback when the discriminator is False.

---

### 2B. NEW ASPECT: `frechet` (diagnostics-only, method string `"frechet"`)

#### `frechet_anova` result dict

Keys: 9-key PyDict. From 69-02-SUMMARY: "frechet_anova returns 9-key PyDict with permutation
p-value in [0,1]" and "pre-validate contiguous 0..k group labels"

[VERIFIED: .planning/phases/69-frechet-regression-density-fda/69-02-SUMMARY.md — line 57:
"fdars.frechet submodule importable; frechet_anova returns 9-key PyDict with permutation
p-value in [0,1]"]

To confirm exact key names, read the source:
[ASSUMED] Typical frechet_anova keys include: `"statistic"`, `"p_value"`, `"n_groups"`,
`"n_obs"`, `"n_perm"`, `"group_means"` (list of arrays), `"group_sizes"` (list or array),
`"total_variance"`, `"between_variance"` — the exact 9 keys must be READ from
`src/frechet_mod.rs` before writing the builder (the summary does not enumerate them).

**Action required by planner:** Task 1 of the frechet aspect plan must read
`src/frechet_mod.rs` frechet_anova binding to enumerate the 9 keys before writing fields.

Safely groundable fields (keys confirmed present from tests):
- `has_anova = "p_value" in raw and "n_groups" in raw` — (n_groups-like key confirmed by group-label pre-validation context) [ASSUMED key name]
- `anova_p_value`: `float(raw["p_value"])` — permutation p-value in [0,1] [VERIFIED: 69-02 D1]
- `n_perm`: `int(raw["n_perm"])` if present else None — [ASSUMED key name]
- `n_obs`: from `"n_obs"` in raw if present else infer from group_sizes [ASSUMED]

#### `frechet_global_reg` / `frechet_local_reg` result dicts

Both return a 3-key PyDict.

[VERIFIED: .planning/phases/69-frechet-regression-density-fda/69-02-SUMMARY.md — line 65:
"frechet_global_reg returns 3-key PyDict; predicted shape (N_OUT, M)"]
[VERIFIED: .planning/phases/69-frechet-regression-density-fda/69-02-SUMMARY.md — line 73:
"frechet_local_reg returns 3-key PyDict; bandwidth echoed"]

[ASSUMED] Keys: `"predicted"` (N_OUT, M array), `"bandwidth"` (float), and one more key.
The exact 3 keys must be READ from `src/frechet_mod.rs` before writing fields.

**Action required by planner:** Task 1 must read `src/frechet_mod.rs` global_reg/local_reg
bindings to enumerate the 3 keys.

Safely groundable:
- `has_global_reg = "predicted" in raw and "bandwidth" not in raw` — [ASSUMED: global_reg
  has no bandwidth; local_reg has bandwidth echoed]
- `has_local_reg = "bandwidth" in raw` — [ASSUMED: unique to local_reg]
- `predicted_n_obs`: `int(np.asarray(raw["predicted"]).shape[0])` if "predicted" in raw else None
- `bandwidth`: `float(raw["bandwidth"])` if "bandwidth" in raw else None [VERIFIED by test assertion 69-02 D3]

#### `frechet_mean` result

Returns a numpy array directly (NOT a dict) — `PyAny` with `.into_any()` unifying PyArray1
(spherical) or PyArray2 (spd/corr).

[VERIFIED: .planning/phases/69-frechet-regression-density-fda/69-03-SUMMARY.md — line 125:
"branches return different numpy types (PyArray2 vs PyArray1); .into_any() unifies"]

**Key insight for frechet aspect:** `frechet_mean` does NOT return a dict. The `build_diagnostics`
wrapper in `__init__.py` has coercion logic that calls `dict(raw)` only when raw is not a dict,
not an array, and not Fdata-like. For `frechet_mean` (which returns a numpy array), the
raw value will be an ndarray — the `hasattr(raw, "__array__")` guard at line 164 prevents
`dict(raw)` from being attempted.

[VERIFIED: python/fdars/advisor/__init__.py:163-171]

```python
if (
    not isinstance(raw, dict)
    and not hasattr(raw, "__array__")  # numpy arrays pass through unchanged
    and not hasattr(raw, "data")       # Fdata-like objects pass through unchanged
):
    raw = dict(raw)
```

For `frechet_mean`, the builder receives a numpy array, not a dict. The builder must handle
this: check `isinstance(raw, dict)` vs array, and if array: compute shape/stats from the array
directly.

**Recommended approach:** The `frechet` aspect builder accepts both array returns (frechet_mean)
and dict returns (anova/global_reg/local_reg). Use discriminators:
- `isinstance(raw, dict)` → True for anova/reg results
- `hasattr(raw, "__array__")` or `isinstance(raw, np.ndarray)` → True for frechet_mean

Frechet mean diagnostics (array input):
- `has_frechet_mean = not isinstance(raw, dict) and hasattr(raw, "__array__")` — discriminator
- `frechet_mean_dim`: `int(np.asarray(raw).shape[-1])` — last dimension = d
- `frechet_mean_ndim`: `int(np.asarray(raw).ndim)` — 1 for spherical, 2 for spd/corr
- `frechet_mean_trace`: `float(np.trace(np.asarray(raw)))` if ndim==2 else None — for spd/corr

---

### 2C. EXTENDED ASPECT: `regression.py` — new branches

The new regression functions live in `fdars.regression` (fof_regression, fof_re_regression)
and `fdars.scalar_on_function` (fam, fregre_gkam, fregre_gsam). However, from the
build_diagnostics dispatch perspective, all go through method string `"regression"` — the
planner must decide whether to extend `regression.py` or add a new `"scalar_on_function"` method
string. Given that `regression_cv` already has its own method string, and that
`scalar_on_function` is a separate Python submodule, the recommended approach is:

**Add new method string `"scalar_on_function"`** for fam/gkam/gsam, keeping `"regression"` for
fof/fof_re. This avoids cluttering the regression aspect with unrelated branches and is
consistent with how `regression_cv` is handled separately.

Alternatively, extend `regression.py` with a `has_fof_regression` / `has_scalar_on_function`
branch — the CONTEXT.md says "extend existing regression aspect". Follow the CONTEXT.md:
extend `regression.py` with new branches.

#### `fof_regression` result dict (9 keys, fpca_x/fpca_y excluded)

[VERIFIED: .planning/phases/68-function-on-function-scalar-on-function-regression/68-01-SUMMARY.md
— line 89: "returned 9-key PyDict excludes fpca_x/fpca_y"]
[VERIFIED: .planning/phases/68-function-on-function-scalar-on-function-regression/68-01-SUMMARY.md
— line 91: "beta_surface shape (m_y, m_x) = (18, 25)"]

The 9 keys must be confirmed from `src/regression_mod.rs` but from test assertions:
- `"beta_surface"` (m_y, m_x) — [VERIFIED: 68-01 D2]
- `"fitted"` (n, m_y) — inferred from function semantics (FOF fitted response)
- `"residuals"` — likely present (consistent with other regression variants)
[ASSUMED] other keys: `"ncomp_x"`, `"ncomp_y"`, `"n_obs"`, etc. — must READ regression_mod.rs

Safely groundable discriminator: `"beta_surface" in raw` — unique to fof_regression
(existing regression variants use `"beta_t"` or `"beta"`, not `"beta_surface"`)

Diagnostic fields:
- `has_fof_regression = "beta_surface" in raw` — discriminator
- `beta_surface_shape`: `[int(np.asarray(raw["beta_surface"]).shape[0]), int(np.asarray(raw["beta_surface"]).shape[1])]` — [m_y, m_x]
- `beta_surface_max_abs`: `float(np.max(np.abs(np.asarray(raw["beta_surface"]))))` — effect magnitude
- `fof_n_obs`: `int(np.asarray(raw["fitted"]).shape[0])` if "fitted" in raw else None

#### `fof_re_regression` result dict (13 keys, fpca internals excluded)

[VERIFIED: .planning/phases/68-function-on-function-scalar-on-function-regression/68-02-SUMMARY.md
— line 119: "fof_re_regression bound with REG-02 validation; returns 13-key PyDict;
fpca_x/fpca_y intentionally excluded"]
[VERIFIED: 68-02 D3: "random_effects (5,18), sigma2_u (3,), n_subjects=5"]

Keys confirmed: `"random_effects"` (n_subjects, m_y), `"sigma2_u"` (array), `"n_subjects"` (int).
Other 10 keys must be READ from `src/regression_mod.rs`.

Discriminator: `"random_effects" in raw and "n_subjects" in raw` — unique to fof_re_regression

Diagnostic fields:
- `has_fof_re_regression = "random_effects" in raw and "n_subjects" in raw`
- `n_subjects`: `int(raw["n_subjects"])` — [VERIFIED from 68-02 D3]
- `sigma2_u_max`: `float(np.max(np.asarray(raw["sigma2_u"])))` if "sigma2_u" in raw else None — largest variance component
- `re_dims`: `[int(np.asarray(raw["random_effects"]).shape[0]), int(np.asarray(raw["random_effects"]).shape[1])]` if "random_effects" in raw else None

#### `fam` result dict (7 keys)

[VERIFIED: .planning/phases/68-function-on-function-scalar-on-function-regression/68-03-SUMMARY.md
— line 65: "fam returns correct 7-key PyDict with fitted_values.shape==(30,) and
component_fits as list"]

Keys confirmed: `"fitted_values"` (n,), `"component_fits"` (list of arrays).
Other 5 keys must be READ from `src/scalar_on_function_mod.rs`.
`fregre_gsam` returns the same 7 keys (68-03 D3).

Discriminator: `"component_fits" in raw and "fitted_values" in raw` — shared by fam/gsam.
Distinguishing fam from gsam: [ASSUMED] both have the same 7 keys — they are diagnostically
equivalent so a single discriminator covers both.

Diagnostic fields:
- `has_fam = "component_fits" in raw`
- `fam_n_obs`: `int(np.asarray(raw["fitted_values"]).shape[0])` if "fitted_values" in raw else None
- `fam_n_components`: `int(len(raw["component_fits"]))` if "component_fits" in raw else None
- `fam_fitted_residual_std`: FORBIDDEN — residuals may not be in the fam dict; only use keys that exist

[ASSUMED] Additional fam keys may include `"r_squared"`, `"coefficients"`, `"lambda_"`, etc.
— must READ `src/scalar_on_function_mod.rs` for the complete 7-key set before adding fields.

#### `fregre_gkam` result dict

[VERIFIED: .planning/phases/68-function-on-function-scalar-on-function-regression/68-03-SUMMARY.md
— line 84: "fregre_gkam on 2-predictor list returns converged as bool, bandwidths.shape==(2,)"]

Discriminator: `"converged" in raw and "bandwidths" in raw` — unique to gkam

Diagnostic fields:
- `has_fregre_gkam = "converged" in raw and "bandwidths" in raw`
- `gkam_converged`: `bool(raw["converged"])` — convergence flag
- `gkam_bandwidths`: `[float(v) for v in np.asarray(raw["bandwidths"])]` — per-predictor bandwidths
- `gkam_n_predictors`: `int(len(np.asarray(raw["bandwidths"])))` if "bandwidths" in raw else None

#### `fregre_gsam` result dict

Returns same 7 keys as fam. [VERIFIED: 68-03 D3: "fregre_gsam returns same 7 keys as fam"]

The `has_fam` discriminator (`"component_fits" in raw`) covers both. No separate gsam branch needed.

---

### 2D. EXTENDED ASPECT: `classification.py` — new branch

#### `shapelet_classifier_fit` — opaque handle, NOT a dict

**Critical insight:** `shapelet_classifier_fit` returns a `PyShapeletClassifierFit` OPAQUE
HANDLE, not a dict.

[VERIFIED: .planning/phases/71-shapelets-gak-metric/71-01-SUMMARY.md — line 49:
"shapelet_classifier_fit returns PyShapeletClassifierFit opaque handle (not dict) so
predict() is stateful"]

The opaque handle exposes Python-accessible attributes via `#[pymethods]`:
- `.train_accuracy` (float)
- `.classes` (int64 numpy array)
- `.n_classes` (int, probably — matches test "n_classes == 2")
- `.n_shapelets` (int — from test D6: "n_shapelets > 0")

[VERIFIED: .planning/phases/71-shapelets-gak-metric/71-01-SUMMARY.md — D6:
"PyShapeletClassifierFit handle with n_shapelets > 0, train_accuracy in [0,1], int64 classes
array, n_classes == 2"]

The `build_diagnostics` call chain handles this: `raw = getattr(result, "raw", result)` at
`__init__.py:161` — if the handle has no `.raw` attribute, `raw` IS the handle itself. Then
the `not isinstance(raw, dict)` check at line 163 triggers. The handle does NOT have `__array__`
or `data` attributes, so `dict(raw)` would be attempted — which will FAIL for an opaque PyO3
handle.

**Required approach:** The classification aspect builder must detect opaque handles by presence
of `.train_accuracy` attribute BEFORE the `isinstance(raw, dict)` check. Or alternatively,
add `hasattr(raw, "train_accuracy")` to the guard in `build_diagnostics.__init__.py` to
prevent the `dict(raw)` coercion.

The safest fix: in `__init__.py:build_diagnostics`, add a guard for the shapelet handle:
```python
# After the existing guards, before dict(raw):
if hasattr(raw, "train_accuracy") and hasattr(raw, "n_shapelets"):
    # Shapelet classifier opaque handle — extract attributes
    raw = {
        "train_accuracy": float(raw.train_accuracy),
        "n_shapelets": int(raw.n_shapelets),
        "n_classes": int(raw.n_classes) if hasattr(raw, "n_classes") else None,
    }
```

OR: add the attribute extraction inside `_build_classification_diagnostics` at the top
before any key-access on raw, checking `not isinstance(raw, dict)` and handling the handle.

**Recommended:** Handle it inside `_build_classification_diagnostics` since that is where the
shapelet branch lives — mirrors how `elastic_multinomial` is handled as a branch.

The `has_shapelet_classifier` discriminator: `hasattr(raw, "train_accuracy")` (if raw is a
handle object) OR `"train_accuracy" in raw and "n_shapelets" in raw` (if already converted
to dict). Using presence of `"n_shapelets"` as the dict-path discriminator is safe because
existing regression/fof paths never produce this key.

Diagnostic fields (attribute-extracted then stored as native Python):
- `has_shapelet_classifier = "n_shapelets" in raw` (after handle-to-dict conversion)
- `shapelet_n_shapelets`: `int(raw["n_shapelets"])` — [VERIFIED: n_shapelets > 0]
- `shapelet_train_accuracy`: `float(raw["train_accuracy"])` — [VERIFIED: in [0,1]]
- `shapelet_n_classes`: `int(raw["n_classes"])` if "n_classes" in raw else None — [VERIFIED: == 2 for binary]

**Flag:** `shapelet_train_accuracy` comes from `raw.train_accuracy` (a `#[pymethods]` getter).
It IS fdars-computed (the Rust struct stores it from the training result). NOT synthetic. [VERIFIED]

---

### 2E. EXTENDED ASPECT: `spm.py` — new branches

#### `mfpca` result dict (6 keys)

[VERIFIED: .planning/phases/70-multi-domain-data-famm-advanced-clustering/70-03-SUMMARY.md
— line 48: "mfpca #[pyfunction] in fdars.spm returns 6-key PyDict (scores, eigenfunctions,
eigenvalues, means, scales, grid_sizes)"]
[VERIFIED: 70-03 D1: "test_mfpca_returns_six_key_dict" and "test_mfpca_scores_shape"]

Keys: `"scores"` (n, ncomp), `"eigenfunctions"` (PyList of P arrays), `"eigenvalues"` (array),
`"means"` (PyList of P arrays), `"scales"` (array? or scalar?), `"grid_sizes"` (array or list).

From test descriptions: "mfpca scores_shape" means scores is 2D; "eigenfunctions list length"
means eigenfunctions is a Python list of length P (number of variables).

[ASSUMED] `"scales"` and `"grid_sizes"` types — must READ `src/spm_mod.rs` for exact types.
From context "mfpca (scores/eigenfunctions/eigenvalues/means/scales/grid_sizes)" in 70-03:
`grid_sizes` is likely a list of ints (grid size per variable); `scales` is likely a list
of floats (one per variable/component).

Discriminator: `"eigenfunctions" in raw and "scales" in raw` — unique to mfpca (spm_phase1
uses "eigenvalues" but not "eigenfunctions" or "scales").

Diagnostic fields:
- `has_mfpca = "eigenfunctions" in raw and "scales" in raw`
- `mfpca_ncomp`: `int(np.asarray(raw["eigenvalues"]).shape[0])` if "eigenvalues" in raw else None
- `mfpca_n_obs`: `int(np.asarray(raw["scores"]).shape[0])` if "scores" in raw else None
- `mfpca_eigenvalues`: `[float(v) for v in np.asarray(raw["eigenvalues"])]` if "eigenvalues" in raw else None
- `mfpca_variance_explained_cumulative`: computed from eigenvalues using `_eigenvalues_to_variance_cumulative` from `_utils.py`
- `mfpca_n_variables`: `int(len(raw["eigenfunctions"]))` if "eigenfunctions" in raw else None — P (number of functional variables)

**Note:** Import `_eigenvalues_to_variance_cumulative` from `fdars.advisor.aspects._utils`
(mirrors `spm.py` line 33: `from fdars.advisor.aspects._utils import ...`).

#### `spe_multivariate` result (naked array, NOT a dict)

[VERIFIED: .planning/phases/70-multi-domain-data-famm-advanced-clustering/70-03-SUMMARY.md
— line 65: "spe_multivariate #[pyfunction] in fdars.spm returning a naked (n,) 1-D numpy array"]
[VERIFIED: 70-03 D2: "test_spe_multivariate_is_not_dict"]

`spe_multivariate` returns a raw numpy array. Like `frechet_mean`, the `build_diagnostics`
`hasattr(raw, "__array__")` guard at `__init__.py:165` prevents `dict(raw)` coercion.

The spm builder receives the numpy array directly when `spe_multivariate` output is passed.
Discriminator: `not isinstance(raw, dict) and hasattr(raw, "__array__")` — the array is 1D.

Diagnostic fields (raw is a 1D numpy array):
- `has_spe_multivariate = hasattr(raw, "__array__") and not isinstance(raw, dict)`
- `spe_mv_n_obs`: `int(len(np.asarray(raw)))` — number of observations
- `spe_mv_max`: `float(np.max(np.asarray(raw)))` — maximum multivariate SPE value
- `spe_mv_mean`: `float(np.mean(np.asarray(raw)))` — mean SPE value
- `spe_mv_all_nonneg`: `bool(float(np.min(np.asarray(raw))) >= 0.0)` — [VERIFIED: 70-03 "non-negative residuals" test]

---

## Section 3: Guard-Sync Mechanics (ADV-02)

### The Three Locations

Guard-sync requires FOUR co-equal locations to change atomically:

1. **`python/fdars/advisor/__init__.py:141-157`** — the `_supported` frozenset inside `build_diagnostics`
2. **`python/fdars/mcp/server.py:66-86`** — `_DIAGNOSTICS_METHODS` frozenset
3. **`python/fdars/mcp/_runner.py:59-61`** — `_RUNNABLE_METHODS` (may NOT change for phase 72)
4. **`tests/test_guard_sync_version_independent.py:38-57`** — `_EXPECTED_DIAGNOSTICS_METHODS` literal

The `_pipeline.py` at line 106 does `from fdars.mcp._runner import _RUNNABLE_METHODS` — no
direct copy there, so `_pipeline.py` requires no change.

[VERIFIED: python/fdars/mcp/_pipeline.py:106 — "from fdars.mcp._runner import _RUNNABLE_METHODS"]
[VERIFIED: python/fdars/mcp/server.py:52-86 — both frozensets]
[VERIFIED: python/fdars/mcp/_runner.py:59-61 — _RUNNABLE_METHODS frozenset]
[VERIFIED: tests/test_guard_sync_version_independent.py:38-57 — _EXPECTED_DIAGNOSTICS_METHODS]

### What Changes in Each Location

#### Location 1: `__init__.py` `_supported` set

Add `"fts"` and `"frechet"` to the set:
```python
_supported = {
    "alignment", "fpca", "basis", "smoothing", "clustering",
    "depth",
    "outliers",
    "classification",
    "represent",
    "regression", "regression_cv",
    "spm",
    "scoring",
    "inference",
    "fts",      # ADV-01 Phase 72 — diagnostics-only
    "frechet",  # ADV-01 Phase 72 — diagnostics-only
}
```

Also add two `if method_lc == ...` dispatch branches after line 229 (inference branch).

[VERIFIED: python/fdars/advisor/__init__.py:141-157 — current set without fts/frechet]

#### Location 2: `server.py` `_DIAGNOSTICS_METHODS`

Add `"fts"` and `"frechet"` to `_DIAGNOSTICS_METHODS`. Do NOT add to `_RUNNABLE_METHODS`.

Current `_DIAGNOSTICS_METHODS` [VERIFIED: server.py:66-86]:
```
{"alignment","fpca","basis","smoothing","clustering","depth",
 "outliers","classification","represent","regression","regression_cv",
 "spm","scoring","inference"}
```

New `_DIAGNOSTICS_METHODS` (add to the diagnostics-only block):
```python
_DIAGNOSTICS_METHODS = frozenset({
    "alignment", "fpca", "basis", "smoothing", "clustering", "depth",
    "outliers", "classification", "represent",
    "regression", "regression_cv",
    "spm",
    "scoring",
    "inference",
    "fts",      # ADV-01 Phase 72 — diagnostics-only; fts needs caller-supplied result
    "frechet",  # ADV-01 Phase 72 — diagnostics-only; frechet must NOT be runnable (SC3)
})
```

`_RUNNABLE_METHODS` stays UNCHANGED at `{"alignment","fpca","basis","smoothing","clustering","depth"}`.

[VERIFIED: server.py:52-54 — _RUNNABLE_METHODS = frozenset({"alignment","fpca","basis","smoothing","clustering","depth"})]

#### Location 3: `_runner.py` `_RUNNABLE_METHODS`

NO CHANGE. Stays at `{"alignment","fpca","basis","smoothing","clustering","depth"}`.

Extended methods (fof/fam/mfpca/shapelet_classifier) are diagnostics-only: they require
caller-supplied result dicts (e.g. fof needs both x_data and y_data; shapelet needs labels;
mfpca needs a list of arrays) that the MCP dataset model cannot provide at run_method time.
The existing pattern ("diagnostics-only aspects — NOT dispatchable by run_method") applies here.

**Per-method runnable determination:**
- `fof_regression` → **diagnostics-only**. Needs x_data + y_data separately; no single-array dataset model
- `fof_re_regression` → **diagnostics-only**. Needs subject IDs (extra param not in _runner signature)
- `fam` / `fregre_gkam` / `fregre_gsam` → **diagnostics-only**. Multi-predictor input (list of arrays) incompatible with current registry
- `shapelet_classifier_fit` → **diagnostics-only**. Returns opaque handle not a dict; MCP runner returns raw result dicts
- `mfpca` → **diagnostics-only**. Needs list of 2D arrays as input — incompatible with single-dataset registry
- `spe_multivariate` → **diagnostics-only** (returns naked array; needs multiple list inputs)
- `fts.*` → **diagnostics-only** (new aspect string `"fts"`)
- `frechet.*` → **diagnostics-only** (new aspect string `"frechet"`, SC3 hard constraint)

#### Location 4: `test_guard_sync_version_independent.py` `_EXPECTED_DIAGNOSTICS_METHODS`

Add `"fts"` and `"frechet"` to the hard-coded frozenset:

```python
_EXPECTED_DIAGNOSTICS_METHODS: frozenset[str] = frozenset({
    "alignment", "fpca", "basis", "smoothing", "clustering", "depth",
    "outliers", "classification", "represent",
    "regression", "regression_cv",
    "spm",
    "scoring",
    "inference",
    "fts",     # ADV-01 Phase 72
    "frechet", # ADV-01 Phase 72
})
```

[VERIFIED: tests/test_guard_sync_version_independent.py:38-57 — current set (14 entries)]

### What the Guard-Sync Test Asserts

The test has two parts [VERIFIED: test_guard_sync_version_independent.py]:

1. **`test_guard_sync_version_independent` (runs on Python 3.9+):** calls
   `build_diagnostics({}, "__sentinel__")`, parses the ValueError message to extract the
   `Supported: [...]` list, converts to frozenset, asserts it equals `_EXPECTED_DIAGNOSTICS_METHODS`.
   Fails if advisor has an entry the literal lacks (stale literal) OR literal has entry that
   advisor lacks (phantom entry).

2. **`test_guard_sync_mcp_server_matches_expected` (Python 3.10+ only, internally guarded):**
   imports `fdars.mcp.server._DIAGNOSTICS_METHODS` and asserts it equals `_EXPECTED_DIAGNOSTICS_METHODS`.

Both tests must pass. The 4-location atomic commit ensures they do.

### Atomicity Requirement

The single commit must include ALL of:
- `python/fdars/advisor/aspects/fts.py` (new file)
- `python/fdars/advisor/aspects/frechet.py` (new file)
- `python/fdars/advisor/aspects/regression.py` (extended — fof/fof_re/fam/gkam branches)
- `python/fdars/advisor/aspects/classification.py` (extended — shapelet branch)
- `python/fdars/advisor/aspects/spm.py` (extended — mfpca/spe_multivariate branches)
- `python/fdars/advisor/__init__.py` (`_supported` + dispatch branches)
- `python/fdars/mcp/server.py` (`_DIAGNOSTICS_METHODS`)
- `tests/test_guard_sync_version_independent.py` (`_EXPECTED_DIAGNOSTICS_METHODS`)
- New test files for per-aspect serialization

This is a single feat commit + a test commit, or one combined commit. The pattern from Phase 67
and prior advisor phases is separate feat + test commits; the guard-sync requirement means the
test commit must include the guard-sync test update AND the aspect test files together.

---

## Section 4: Tests

### Pattern: Per-Aspect Serialization Test

Mirror `test_advisor_regression_v6.py` and `test_advisor_group_b.py`:

```python
"""Tests for [fts/frechet] advisor diagnostics — Phase 72 (ADV-01).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
"""
import json
import numpy as np
import pytest

def check_no_numpy(obj):
    """Fail if any value in obj is a numpy scalar (np.generic subclass)."""
    assert not isinstance(obj, np.generic), (
        f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
    )
    if isinstance(obj, dict):
        for v in obj.values():
            check_no_numpy(v)
    elif isinstance(obj, list):
        for v in obj:
            check_no_numpy(v)

class TestFtsAspect:
    @pytest.fixture(scope="class")
    def ftsm_result(self):
        from fdars import fts
        import numpy as np
        rng = np.random.default_rng(42)
        N, M = 40, 25  # non-square, mirrors the established fixture
        data = rng.standard_normal((N, M))
        argvals = np.linspace(0.0, 1.0, M)
        return fts.ftsm(data, argvals, ncomp=3)

    def test_fts_json_serializable(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        json.dumps(diag, sort_keys=True)  # must not raise

    def test_fts_no_numpy_scalars(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        check_no_numpy(diag)

    def test_fts_deterministic(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(ftsm_result, method="fts")
        d2 = build_diagnostics(ftsm_result, method="fts")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_fts_method_field(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        assert diag["method"] == "fts"
```

[ASSUMED] The exact fixture shape (N=40, M=25) matches the established non-square fts fixture.

Separate test files:
- `tests/test_advisor_fts.py` — covers ftsm, stationarity, acf, dpca, fplsr branches
- `tests/test_advisor_frechet.py` — covers anova, global_reg, local_reg, frechet_mean branches

### Guard-Sync Test Update

In `test_guard_sync_version_independent.py`, the ONLY change is adding `"fts"` and `"frechet"`
to the `_EXPECTED_DIAGNOSTICS_METHODS` frozenset. No logic changes.

### Extending Existing Aspect Tests

- `test_advisor_regression_v6.py` → add a `TestFofRegression` class with fof_regression fixture
- `tests/test_advisor_group_b.py` or a new file → add `TestShapeletClassifier` class
- A new `tests/test_advisor_spm_v11.py` → `TestMfpca` class

### Grounding Check Pattern

Per `test_advisor_grounding.py` pattern [VERIFIED: tests/test_advisor_grounding.py]:
```python
from fdars.advisor.providers._validate import _check_grounding, GroundingViolationError
# Build advice with fabricated value → must raise GroundingViolationError
# Build advice with real value → must NOT raise
```

For per-aspect tests, the simpler check is `json.dumps(diag)` succeeds + `check_no_numpy(diag)`.
A full grounding test requires the LLM provider and is in `test_advisor_live_integration.py`.

---

## Section 5: LLM-Free Proof (ADV-02)

The number path is LLM-free by structural separation enforced at module load time:

1. `python/fdars/advisor/__init__.py` never imports `anthropic` at module load. The `advise()`
   function imports the provider only when called. [VERIFIED: __init__.py:447-453 — deferred import]

2. `build_diagnostics()` uses only `numpy` and (optionally) one fdars submodule call (the live
   `spm.spe_moment_match_diagnostic` call in `spm.py`, guarded by try/except). No LLM.
   [VERIFIED: python/fdars/advisor/aspects/spm.py:139-147 — try/except guarded live call]

3. New aspect files (`fts.py`, `frechet.py`) and the extended branches in existing aspects
   MUST NOT import `anthropic` or any provider. They use only `numpy` + `fdars` submodule calls.

4. The separation is asserted by the test structure: per-aspect tests call `build_diagnostics`
   without any ANTHROPIC_API_KEY — if the builder imported anthropic it would raise ImportError
   in CI environments without the key, and tests would fail.

5. MCP `_pipeline.py` compute path: `build_pipeline_report_mcp` calls `run_method` then
   `build_diagnostics` then `build_pipeline_report(run_llm=False)` — all three are LLM-free.
   [VERIFIED: python/fdars/mcp/_pipeline.py:1-19 — "fully deterministic and LLM-free"]

---

## Section 6: Architecture Patterns

### System Architecture Diagram

```
fdars function call (e.g. fts.ftsm(...))
  |
  v
raw PyDict / opaque handle (fdars-computed values only)
  |
  v
build_diagnostics(result, method="fts")
  |-- method dispatch (if method_lc == "fts":)
  |-- _build_fts_diagnostics(raw)
  |     |-- numpy operations on fdars values
  |     |-- float()/int()/bool() casts
  |     `-- returns plain-Python dict
  `-- returns grounded dict (no numpy scalars, JSON-serializable)
  |
  v
advise(diagnostics, task="interpretation", ...)   <-- LLM boundary
  |-- LLM reads pre-computed dict (cannot fabricate)
  `-- returns Advice (grounding check applied)
```

### Recommended Project Structure (new files)

```
python/fdars/advisor/aspects/
├── fts.py          # NEW — _build_fts_diagnostics (multi-function: ftsm/acf/stationarity/dpca/fplsr)
├── frechet.py      # NEW — _build_frechet_diagnostics (multi-result: anova/reg/mean)
├── regression.py   # EXTEND — add fof_regression, fof_re_regression, fam, gkam branches
├── classification.py # EXTEND — add shapelet_classifier branch (handle-to-dict conversion)
└── spm.py          # EXTEND — add mfpca, spe_multivariate branches

tests/
├── test_advisor_fts.py          # NEW — per-aspect json.dumps serialization + no-numpy
├── test_advisor_frechet.py      # NEW — per-aspect json.dumps serialization + no-numpy
├── test_advisor_spm_v11.py      # NEW — mfpca + spe_multivariate branches
└── test_guard_sync_version_independent.py  # EXTEND — add "fts"/"frechet" to frozenset
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cumulative variance from eigenvalues | Custom loop | `_eigenvalues_to_variance_cumulative` from `_utils.py` | Shared helper already exists in project; used by fpca.py and spm.py |
| Numpy scalar type check | isinstance(x, float) | `isinstance(x, np.generic)` in `check_no_numpy` | np.generic catches all numpy scalar subclasses; plain float() cast at build time prevents the issue |
| Guard-sync test | Custom assert | Parse ValueError message from build_diagnostics | Existing pattern in test_guard_sync_version_independent.py recovers supported set from error message |

---

## Common Pitfalls

### Pitfall 1: opaque handle passed as `raw` without conversion
**What goes wrong:** `shapelet_classifier_fit` returns `PyShapeletClassifierFit` — not a dict.
`build_diagnostics` at `__init__.py:163-171` attempts `dict(raw)` if raw is not a dict, not
an array, and not Fdata-like. A PyO3 opaque `#[pyclass]` handle has no `__array__` attribute
and no `data` attribute — so `dict(raw)` is attempted, which will raise TypeError.

**How to avoid:** Add handle detection in `_build_classification_diagnostics` at the function
top: `if not isinstance(raw, dict): raw = {"train_accuracy": float(raw.train_accuracy), ...}`.
Or add a guard in `build_diagnostics.__init__.py` before `dict(raw)` using
`hasattr(raw, "train_accuracy")`.

**Warning signs:** `TypeError: cannot convert 'PyShapeletClassifierFit' to a Python dict`

### Pitfall 2: numpy scalars leaking into the return dict
**What goes wrong:** `ar_sigma2_max = max(m["sigma2"] for m in raw["ar_models"])` — `ar_models`
is a list of Python dicts built from PyList/PyDict in Rust. The values in these dicts ARE
native Python floats (PyDict set_item from Rust sets them as f64 → Python float). BUT
`np.max(array_of_floats)` returns a numpy scalar. Always cast.

**How to avoid:** Always `float(x)` or `int(x)` every numeric value before assigning to `diag`.
Run `check_no_numpy(diag)` in tests.

### Pitfall 3: forgetting the guard-sync test update
**What goes wrong:** New aspects added to `_supported` in `__init__.py` and to `server.py`
`_DIAGNOSTICS_METHODS` but the `_EXPECTED_DIAGNOSTICS_METHODS` literal in
`test_guard_sync_version_independent.py` is not updated.

`test_guard_sync_version_independent` will fail with:
```
advisor._supported != _EXPECTED_DIAGNOSTICS_METHODS
  In advisor only: {'fts', 'frechet'}
  In expected only: set()
```

**How to avoid:** The test file update is part of the atomic commit. The MAINTENANCE NOTE in
the test file (line 34-36) explicitly says to update all three in one atomic commit.

### Pitfall 4: frechet_mean array instead of dict
**What goes wrong:** `frechet_mean` returns a numpy array (not a dict). If the frechet aspect
builder does `raw.get("key")` without first checking `isinstance(raw, dict)`, it will crash.

**How to avoid:** The frechet builder starts with `isinstance(raw, dict)` check and routes
to the array path (frechet_mean) or dict path (anova/global_reg/local_reg).

### Pitfall 5: spe_multivariate is not a dict
**What goes wrong:** Same as frechet_mean — `spe_multivariate` returns a naked numpy array.
The spm builder must check `isinstance(raw, dict)` vs array and handle both.

**How to avoid:** Add `has_spe_multivariate = hasattr(raw, "__array__") and not isinstance(raw, dict)`
branch at the TOP of `_build_spm_diagnostics`, before any dict key access.

### Pitfall 6: stale SUMMARY key lists
**What goes wrong:** The SUMMARY files list key counts (e.g. "9-key PyDict") but do NOT always
enumerate all key names. Guessing key names from the count leads to KeyError at runtime.

**How to avoid:** Before writing each builder branch, READ the corresponding Rust binding file
(`src/frechet_mod.rs`, `src/regression_mod.rs`, `src/scalar_on_function_mod.rs`,
`src/shapelet_mod.rs`, `src/spm_mod.rs`) to enumerate the actual PyDict `set_item` calls.

---

## Code Examples

### Pattern: New aspect file skeleton (frechet.py)

```python
"""fdars.advisor.aspects.frechet — Fréchet diagnostics builder.

Handles three result shapes from fdars.frechet:
- frechet_anova: 9-key PyDict  → has_anova discriminator
- frechet_global_reg / frechet_local_reg: 3-key PyDict → has_global_reg / has_local_reg
- frechet_mean: naked numpy array (spd (d,d), spherical (d,), corr (d,d))

All values returned are native Python types. No NumPy scalars. Deterministic.
"""
from __future__ import annotations
import numpy as np

def _build_frechet_diagnostics(raw, **kwargs) -> dict:
    diag: dict = {"method": "frechet"}

    # Detect frechet_mean (returns numpy array, not dict)
    if not isinstance(raw, dict):
        arr = np.asarray(raw)
        diag["has_frechet_mean"] = True
        diag["has_anova"] = False
        diag["has_global_reg"] = False
        diag["has_local_reg"] = False
        diag["frechet_mean_ndim"] = int(arr.ndim)
        diag["frechet_mean_dim"] = int(arr.shape[-1])
        diag["frechet_mean_trace"] = float(np.trace(arr)) if arr.ndim == 2 else None
        # Fill anova/reg fields as None
        diag["anova_p_value"] = None
        diag["predicted_n_obs"] = None
        diag["bandwidth"] = None
        return diag

    # Dict result paths
    diag["has_frechet_mean"] = False
    has_anova = "p_value" in raw and "n_perm" in raw  # frechet_anova unique keys
    has_local_reg = "bandwidth" in raw                  # frechet_local_reg unique
    has_global_reg = "predicted" in raw and not has_local_reg
    diag["has_anova"] = bool(has_anova)
    diag["has_global_reg"] = bool(has_global_reg)
    diag["has_local_reg"] = bool(has_local_reg)

    if has_anova:
        diag["anova_p_value"] = float(raw["p_value"]) if "p_value" in raw else None
        diag["n_perm"] = int(raw["n_perm"]) if "n_perm" in raw else None
    else:
        diag["anova_p_value"] = None
        diag["n_perm"] = None

    if has_global_reg or has_local_reg:
        pred = np.asarray(raw["predicted"]) if "predicted" in raw else None
        diag["predicted_n_obs"] = int(pred.shape[0]) if pred is not None else None
        diag["bandwidth"] = float(raw["bandwidth"]) if "bandwidth" in raw else None
    else:
        diag["predicted_n_obs"] = None
        diag["bandwidth"] = None

    diag["frechet_mean_ndim"] = None
    diag["frechet_mean_dim"] = None
    diag["frechet_mean_trace"] = None

    return diag
```

[ASSUMED] Key names for anova (`"p_value"`, `"n_perm"`) and the discriminator logic —
READ `src/frechet_mod.rs` before finalizing field names.

### Pattern: Extending spm.py with mfpca branch

```python
# At the bottom of _build_spm_diagnostics, before `return diag`:

# -- spe_multivariate: receives naked array, not dict (Pitfall 5) ----------
# The build_diagnostics wrapper calls this builder with raw=<numpy array>
# when spe_multivariate output is passed directly.
has_spe_mv = not isinstance(raw, dict) and hasattr(raw, "__array__")
# (Note: if raw IS a dict but has "spe" key — that's spm_phase1, handled above)
# This branch only fires when a naked array is passed (spe_multivariate output).
# In practice, the spm builder is called via build_diagnostics("spm", result)
# where result is either the spm_phase1 dict OR the spe_multivariate array.
if has_spe_mv:
    spe_mv = np.asarray(raw)
    diag["has_spe_multivariate"] = True
    diag["spe_mv_n_obs"] = int(len(spe_mv))
    diag["spe_mv_max"] = float(np.max(spe_mv))
    diag["spe_mv_mean"] = float(np.mean(spe_mv))
    diag["spe_mv_all_nonneg"] = bool(float(np.min(spe_mv)) >= 0.0)
    # Fill mfpca fields as None
    diag["has_mfpca"] = False
    diag["mfpca_ncomp"] = None
    diag["mfpca_n_obs"] = None
    diag["mfpca_n_variables"] = None
    diag["mfpca_eigenvalues"] = None
    diag["mfpca_variance_explained_cumulative"] = None
else:
    diag["has_spe_multivariate"] = False
    diag["spe_mv_n_obs"] = None
    diag["spe_mv_max"] = None
    diag["spe_mv_mean"] = None
    diag["spe_mv_all_nonneg"] = None

    # -- mfpca branch (6-key PyDict, distinct from spm_phase1) ----------------
    has_mfpca = isinstance(raw, dict) and "eigenfunctions" in raw and "scales" in raw
    diag["has_mfpca"] = bool(has_mfpca)
    if has_mfpca:
        from fdars.advisor.aspects._utils import _eigenvalues_to_variance_cumulative  # noqa: PLC0415
        eigen_raw = raw.get("eigenvalues")
        eigen_arr = np.asarray(eigen_raw, dtype=float) if eigen_raw is not None else None
        diag["mfpca_ncomp"] = int(len(eigen_arr)) if eigen_arr is not None else None
        scores_raw = raw.get("scores")
        diag["mfpca_n_obs"] = int(np.asarray(scores_raw).shape[0]) if scores_raw is not None else None
        eigenfn_raw = raw.get("eigenfunctions")
        diag["mfpca_n_variables"] = int(len(eigenfn_raw)) if eigenfn_raw is not None else None
        if eigen_arr is not None:
            diag["mfpca_eigenvalues"] = [float(v) for v in eigen_arr]
            diag["mfpca_variance_explained_cumulative"] = _eigenvalues_to_variance_cumulative(eigen_arr)
        else:
            diag["mfpca_eigenvalues"] = None
            diag["mfpca_variance_explained_cumulative"] = None
    else:
        diag["mfpca_ncomp"] = None
        diag["mfpca_n_obs"] = None
        diag["mfpca_n_variables"] = None
        diag["mfpca_eigenvalues"] = None
        diag["mfpca_variance_explained_cumulative"] = None
```

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `frechet_anova` key names include `"p_value"` and `"n_perm"` as discriminators | 2B | Builder discriminator fails; KeyError in builder |
| A2 | `fam` and `fregre_gsam` have same 7 keys — `"component_fits"` and `"fitted_values"` confirmed | 2C | Discriminator based on these two keys may not be unique |
| A3 | `fregre_gkam` has keys `"converged"` and `"bandwidths"` as unique discriminators | 2C | Builder discriminator fails |
| A4 | `mfpca` key `"scales"` is present and list-like (not scalar) | 2E | Used in discriminator — must be absent from spm_phase1 |
| A5 | `shapelet_classifier_fit` handle has `.n_classes` accessible as a Python attribute | 2D | n_classes field would be None in output |
| A6 | `fof_regression` 9-key PyDict includes key `"fitted"` (for n_obs inference) | 2C | Cannot infer n_obs |
| A7 | `fplsr` discriminator works: `"fitted" in raw and "forecast" in raw and forecast.shape[0]==1` | 2A | Could misclassify other result shapes |
| A8 | fam/gsam residuals are NOT in the result dict (so no residual_std field is safe) | 2C | If residuals ARE present, we're leaving a diagnostic on the table |
| A9 | `frechet_global_reg` has no `"bandwidth"` key (discriminating it from local_reg) | 2B | Discriminator logic reversal |
| A10 | frechet_anova 9 keys include some form of group count accessible as int | 2B | n_groups field would fail |

**Highest-risk assumptions:** A1, A6, A9 — these drive discriminators. All three require
reading the Rust source files before finalizing the builder.

---

## Open Questions

1. **Exact 9-key set for frechet_anova**
   - What we know: 9-key PyDict, p_value in [0,1], permutation-based
   - What's unclear: key names for group count, group variance, total variance
   - Recommendation: READ `src/frechet_mod.rs` `frechet_anova` binding before writing builder

2. **Exact 3-key set for frechet_global_reg / frechet_local_reg**
   - What we know: predicted (N_OUT, M), bandwidth (local_reg), 3 keys total
   - What's unclear: third key name (coefficients? intercept? fitted_values?)
   - Recommendation: READ `src/frechet_mod.rs`

3. **Exact 7-key set for fam / fregre_gsam**
   - What we know: fitted_values (n,), component_fits (list), 7 keys total
   - What's unclear: remaining 5 keys (r_squared? lambda_? aic?)
   - Recommendation: READ `src/scalar_on_function_mod.rs`

4. **fof_re_regression 13 keys beyond random_effects/sigma2_u/n_subjects**
   - What we know: 3 keys confirmed, 10 unknown
   - Recommendation: READ `src/regression_mod.rs` fof_re_regression binding

5. **`mfpca` scales type and grid_sizes type**
   - What we know: both are in the 6-key dict; eigenfunctions and means are PyLists of arrays
   - What's unclear: are scales/grid_sizes lists of floats/ints or numpy arrays?
   - Recommendation: READ `src/spm_mod.rs` + `tests/test_spm_mfpca.py`

---

## Environment Availability

Step 2.6: SKIPPED — this phase is pure Python code/config changes. No external dependencies
beyond the already-compiled fdars extension (required for running tests with real fdars outputs;
already present from Phases 66-71).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already configured) |
| Config file | `pyproject.toml` (existing, no change) |
| Quick run command | `pytest tests/test_advisor_fts.py tests/test_advisor_frechet.py tests/test_guard_sync_version_independent.py -x -q` |
| Full suite command | `pytest tests/ -x -q` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADV-01 | fts aspect json.dumps serializes without error | unit | `pytest tests/test_advisor_fts.py -x -q` | ❌ Wave 0 |
| ADV-01 | frechet aspect json.dumps serializes without error | unit | `pytest tests/test_advisor_frechet.py -x -q` | ❌ Wave 0 |
| ADV-01 | No numpy scalars in fts/frechet diagnostics | unit | above | ❌ Wave 0 |
| ADV-01 | fof_regression branch in regression aspect | unit | `pytest tests/test_advisor_regression_v6.py -x -q` | ✅ (extend) |
| ADV-01 | shapelet_classifier branch in classification aspect | unit | `pytest tests/test_advisor_group_b.py -x -q` | ✅ (extend) |
| ADV-01 | mfpca branch in spm aspect | unit | `pytest tests/test_advisor_spm_v11.py -x -q` | ❌ Wave 0 |
| ADV-02 | Guard-sync test passes (advisor._supported == expected) | unit | `pytest tests/test_guard_sync_version_independent.py -x -q` | ✅ (extend) |
| ADV-02 | Determinism: two calls on same input return equal dict | unit | per-aspect test files | ❌ Wave 0 |

### Wave 0 Gaps

- [ ] `tests/test_advisor_fts.py` — covers ADV-01 fts aspect
- [ ] `tests/test_advisor_frechet.py` — covers ADV-01 frechet aspect
- [ ] `tests/test_advisor_spm_v11.py` — covers ADV-01 mfpca + spe_multivariate branches

Framework already installed — no install step needed.

---

## Security Domain

`security_enforcement` — present by default (no explicit `false` in config).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A (no auth paths) |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | All key accesses guarded; `raw` treated as untrusted; missing keys → None (mirrors spm.py line 23-27 security note) |
| V6 Cryptography | no | N/A |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed result dict with unexpected key types | Tampering | Guard all key accesses with `if "key" in raw`; wrap in try/except where needed |
| numpy scalar injection via unguarded cast | Tampering (data integrity) | Always float()/int() cast; check_no_numpy in tests |
| Opaque handle breaking dict assumption | Spoofing | isinstance(raw, dict) guard before any dict access |

---

## Sources

### Primary (HIGH confidence)

- `python/fdars/advisor/aspects/regression.py` — canonical grounded aspect pattern, read verbatim
- `python/fdars/advisor/__init__.py` — dispatch table and `_supported` frozenset, read verbatim
- `python/fdars/advisor/aspects/spm.py` — live fdars call pattern + security notes, read verbatim
- `python/fdars/advisor/aspects/classification.py` — `has_elastic_multinomial` branch pattern, read verbatim
- `python/fdars/mcp/server.py` — `_RUNNABLE_METHODS` + `_DIAGNOSTICS_METHODS`, read verbatim (lines 52-86)
- `python/fdars/mcp/_runner.py` — `_RUNNABLE_METHODS` (authoritative copy), read verbatim (lines 59-61)
- `python/fdars/mcp/_pipeline.py` — `from fdars.mcp._runner import _RUNNABLE_METHODS`, read verbatim (line 106)
- `tests/test_guard_sync_version_independent.py` — guard-sync test mechanics + `_EXPECTED_DIAGNOSTICS_METHODS`, read verbatim

### Secondary (MEDIUM confidence — Phase SUMMARY files, verified by test assertions)

- `.planning/phases/67-functional-time-series-fts/67-01-SUMMARY.md` — ftsm PyDict keys
- `.planning/phases/67-functional-time-series-fts/67-02-SUMMARY.md` — ftsm_forecast/fplsr keys
- `.planning/phases/67-functional-time-series-fts/67-03-SUMMARY.md` — stationarity/acf/pacf/long_run_covariance keys
- `.planning/phases/67-functional-time-series-fts/67-04-SUMMARY.md` — dpca/spectral_density keys
- `.planning/phases/69-frechet-regression-density-fda/69-02-SUMMARY.md` — frechet_anova (9-key), global/local_reg (3-key) shapes
- `.planning/phases/69-frechet-regression-density-fda/69-03-SUMMARY.md` — frechet_mean return type (array)
- `.planning/phases/68-function-on-function-scalar-on-function-regression/68-01-SUMMARY.md` — fof_regression (9-key, beta_surface)
- `.planning/phases/68-function-on-function-scalar-on-function-regression/68-02-SUMMARY.md` — fof_re_regression (13-key, random_effects, sigma2_u, n_subjects)
- `.planning/phases/68-function-on-function-scalar-on-function-regression/68-03-SUMMARY.md` — fam/gsam (7-key, fitted_values, component_fits), gkam (converged, bandwidths)
- `.planning/phases/71-shapelets-gak-metric/71-01-SUMMARY.md` — PyShapeletClassifierFit handle (train_accuracy, n_shapelets, n_classes)
- `.planning/phases/70-multi-domain-data-famm-advanced-clustering/70-03-SUMMARY.md` — mfpca (6-key: scores, eigenfunctions, eigenvalues, means, scales, grid_sizes), spe_multivariate (naked array)

### Tertiary (LOW confidence — to be verified before use)

- Exact key names for `frechet_anova` 9-key dict beyond `p_value`/`n_perm`
- Exact remaining keys of `fof_regression` beyond `beta_surface`/`fitted`
- Exact fam 7-key set beyond `fitted_values`/`component_fits`
- `mfpca` `scales` and `grid_sizes` concrete Python types

---

## Metadata

**Confidence breakdown:**
- Aspect pattern: HIGH — read from canonical source files this session
- Guard-sync mechanics: HIGH — read all four locations verbatim this session
- ftsm/acf/stationarity/dpca/fplsr diagnostic fields: HIGH — keys confirmed by test assertions in SUMMARY files
- frechet field lists: MEDIUM — shapes confirmed; exact key names partially assumed (see Assumptions Log)
- fof/fam/mfpca field lists: MEDIUM — partial key confirmation from SUMMARY test assertions; full enumeration requires reading Rust sources
- shapelet_classifier handle: HIGH — handle attributes confirmed by test in 71-01-SUMMARY
- LLM-free proof: HIGH — structural separation verified in source

**Research date:** 2026-09-04
**Valid until:** 2026-09-18 (stable — no upstream changes expected in this window)
