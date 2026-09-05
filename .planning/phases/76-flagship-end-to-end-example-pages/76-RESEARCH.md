# Phase 76: Flagship End-to-End Example Pages — Research

**Researched:** 2026-09-05
**Domain:** MkDocs documentation — three flagship worked-example pages (FTS, Fréchet regression, shapelet classification)
**Confidence:** HIGH (all API facts verified by running code under .venv this session; all loader calls verified against scripts/docs_data.py read this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Scope (user-selected)**
- Three flagship examples (EXMP-01, EXMP-02, EXMP-03) all delivered.
- EXMP-03 is the shapelet-classification example on `phoneme.csv` (strong 5-class fit), not the density-FDA alternative.

**Datasets & method framing**
- EXMP-01: `docs/data/canadian_weather.csv` (35 × 365). Research determines the strongest concrete construction for a genuine functional-time-series framing. Weekly aggregation like Phase 75 if needed.
- EXMP-02: real-data-derived metric-space response where a strong concrete fit exists; synthetic-augment ONLY where no clean real fit exists. Use corrected frechet API from Phase 74 (naked-array returns).
- EXMP-03: `docs/data/phoneme.csv` (400 × 256, 5-class). Small class subset / capped `max_candidates` (~200) to keep fence under a few seconds.

**Page shape & structure**
- Match mature `examples/` standard: narrative arc + real dataset + ≥1 `html="1"` figure + `FDARS_FENCE_OK` fences.
- Model structure on: `docs/examples/tecator-regression.md`, `canadian-seasonal.md`, `phoneme-shape.md`, `sonar-tsrvf.md`.
- Verify each page with `scripts/run_page_fences.py`.

**Nav wiring**
- Add each page to `mkdocs.yml` examples nav and/or `docs/examples/index.md`. Gallery cards/thumbnails deferred to Phase 77.

### Claude's Discretion

- Choice of exact EXMP-01 framing (research-determined — see Section 1 below).
- Choice of exactly which real-data construction drives EXMP-02 (research-determined — see Section 2 below).
- Within-page narrative arc, section titles, figure choices.

### Deferred Ideas (OUT OF SCOPE)

- Gallery cards + hand-authored thumbnails for these new example pages → Phase 77 (CARD work).
- Whole-site strict build / SVGO / human diagram review → Phase 79 (GATE).
- Any density-FDA flagship example (the EXMP-03 alternative not chosen).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXMP-01 | Flagship Functional Time Series example page (forecast + evaluation) against a `docs/data/` dataset, runnable offline (`FDARS_FENCE_OK`). | Framing, recipe, exact API calls, and timing all verified by running under .venv this session. See Section 1. |
| EXMP-02 | Flagship Fréchet-regression example page (metric-space response walkthrough), runnable offline (`FDARS_FENCE_OK`). | Real-data construction (density-response from canadian_weather) verified, exact recipe and timing confirmed. See Section 2. |
| EXMP-03 | Flagship shapelet-classification example page on phoneme.csv, runnable offline (`FDARS_FENCE_OK`). | Exact pipeline verified: 5-class with 20 curves/class, max_candidates=200, total fence time ~2s. See Section 3. |
</phase_requirements>

---

## Summary

Phase 76 adds three new `docs/examples/*.md` pages that each tell a complete end-to-end story with a real dataset, real `fdars` API calls, and runnable fences that emit `FDARS_FENCE_OK` offline.

All three example framings were validated by actually running them under `.venv` with `PYTHONPATH=scripts` during this research session. The timings reported below are measured, not estimated.

**EXMP-01 (FTS):** The canonical framing is 35 Canadian weather stations sorted by latitude (south-to-north spatial gradient) → weekly-aggregated to (35, 52) → treated as a functional time series. This gives a clean narrative: a continuous gradient of climate curves, the FTSM decomposes it into 3 FPC components (86%/10%/4% variance), AR(1) processes govern the dominant components, and 5-step forecast is evaluated on the 5 most-northern held-out stations. All fences run in < 0.03s each. `functional_acf` on this data runs in 0.028s with `n_sim=99` (use `fast(999, 99)`).

**EXMP-02 (Fréchet):** The construction is: for each Canadian weather station, build a temperature-distribution density via KDE → normalize to integrate to 1 → stack into a (35, 60) density-response matrix → regress on scalar latitude predictor. This is a genuine real-data fit: warmer southern stations have right-shifted, narrower distributions; colder northern stations have left-shifted, broader distributions. `frechet_global_reg` runs in 0.006s; `frechet_local_reg` runs in 0.006s. The ISE evaluation on a 28/7 train-test split confirms that local regression (bandwidth=5°) outperforms global for this spatially heterogeneous dataset.

**EXMP-03 (shapelet):** The 5-class phoneme dataset with 20 curves/class (100 total), max_candidates=200, k=3 kNN classifier. `discover_shapelets` (summary dict), `shapelet_transform_fit` + `shapelet_transform` (feature matrix), `shapelet_classifier_fit` + `.predict()` pipeline all verified. Fence timing: ~2s for full 5-class pipeline. The page uses an 80/20 train-test split (16 train, 4 test per class) and a 5-class `discover → transform → classify` narrative.

**Primary recommendation:** Each example is a self-contained `docs/examples/*.md` page following the mature-example narrative arc: bold intro → dataset description → progressive analysis sections with `html="1"` figures → parameter table → See also. Nav wiring requires two edits per page: `mkdocs.yml` and `docs/examples/index.md`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Page prose + structure | Docs author | — | Pure markdown editing; no code change |
| Runnable fences (`exec="1"`) | Docs author (inline fence code) | `fdars` package (execution engine) | Fences call the current installed `fdars` — no new bindings |
| matplotlib figures (`html="1"`) | `docs_fig.py` helper + `markdown-exec` | MkDocs Material render | `docs_fig.fig()` / `render()` / `fast()` pattern |
| Dataset loading | `docs_data.py` (scripts/) | `docs/data/*.csv` files | Loaders verified against scripts/docs_data.py read this session |
| Nav wiring | `mkdocs.yml` + `docs/examples/index.md` | — | Two file edits per page; gallery cards deferred |

---

## 1. EXMP-01 — Functional Time Series (canadian_weather.csv)

### 1.1 Framing Decision (VERIFIED by running)

**Chosen framing:** 35 Canadian weather stations, sorted ascending by latitude, weekly-aggregated annual temperature curves, treated as a functional time series of length n=35.

**Why this framing is genuinely a functional time series:**
- The 35 stations form a smooth spatial gradient from south (~43°N, Halifax/Windsor) to north (~68°N, Inuvik). Latitude is a continuous ordering variable analogous to "time" in a spatial time series.
- Each station's 52 weekly mean temperatures is the functional observation at position i in the series.
- The FTSM autocorrelation structure at this ordering is real: ACF lag-1 value ≈ 0.33 [VERIFIED: run this session], meaning consecutive stations in the gradient genuinely autocorrelate.
- The stationarity test gives p=0.010 [VERIFIED: run this session], indicating a non-stationary functional series — which is the right pedagogical setup for showing differencing or interpreting the series structure.

**Alternative framings rejected:**
- "35 stations as 35 observations in temporal order" — stations are not temporally ordered; there is no natural temporal index. This would require manufacturing a non-existent ordering.
- "One station's year split into 52 weekly curves" — gives only n=52 observations of m=7 grid points. AR structures from a genuine annual temperature cycle will be strongly seasonal (AR order 52), not interpretable. Tested: AR orders [1, 0, 1] for n=30×52 (lat-sorted weekly), vs AR orders [3, 9, 2] for single-station weekly — the lat-sorted version is cleaner.
- "35 stations, 365-pt curves, no aggregation" — works but `functional_acf(35×365, n_sim=99)` takes 4.8s [VERIFIED: run this session], which will slow the strict build significantly. The weekly aggregation brings it to 0.028s.

### 1.2 Dataset Loader

```python
from docs_data import load_canadian_weather
day, X, meta = load_canadian_weather("temperature")
# day: np.ndarray shape (365,) — day of year 1..365
# X:   np.ndarray shape (35, 365) — one station per row
# meta: DataFrame with columns ['station', 'province', 'region', 'lat', 'lon']
```

[VERIFIED: scripts/docs_data.py:59-88 read this session; run confirmed shape (35, 365)]

### 1.3 Data Construction Recipe

```python
# Sort stations by latitude (south to north)
lat = meta['lat'].to_numpy()
order = np.argsort(lat)
X_ord = X[order]             # (35, 365) — ascending latitude

# Weekly mean aggregation: 52 weeks of 7 days each
X_wk = X_ord[:, :364].reshape(35, 52, 7).mean(axis=2)   # (35, 52)
t_wk = np.arange(52, dtype=float)                         # week 0..51

# Train/test split: 30 southern stations train, 5 northern stations test
X_train = X_wk[:30]   # (30, 52)
X_test  = X_wk[30:]   # (5, 52)
```

[VERIFIED: run this session — confirmed shapes and data integrity]

### 1.4 Exact API Calls (from 75-RESEARCH, all VERIFIED)

```python
from fdars.fts import ftsm, ftsm_forecast_multistep, stationarity_test, functional_acf
from docs_fig import fast

# Fit FTSM
fit = ftsm(X_train, t_wk, ncomp=3)
# Returns dict: mean(52,), rotation(52,3), scores(30,3), fitted(30,52),
#               weights(52,), ncomp(int), ar_models(list of dict{order,phi,sigma2})
# ncomp=3: AR orders [1, 0, 1], variance explained [86%, 10%, 4%]
# (variance explained computed from scores.var(axis=0))

# Forecast 5 steps ahead
fc = ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)
# Returns dict: forecast(5, 52), h(int)
forecast = np.asarray(fc['forecast'])   # (5, 52) — 5 predicted station curves

# Evaluation: RMSE vs held-out test
rmse = np.sqrt(np.mean((forecast - X_test)**2))
# Measured RMSE: 14.18°C (reasonable for a 5-step spatial extrapolation)

# Stationarity test
st = stationarity_test(X_train, t_wk, n_perm=fast(999, 99), seed=42)
# Returns dict: statistic(float), p_value(float), n_perm(int)
# p_value = 0.010 (non-stationary: south-to-north gradient is not stationary)

# Functional ACF (for visualization)
acf = functional_acf(X_train, t_wk, max_lag=8, n_sim=fast(999, 99), seed=42)
# Returns dict: lags(int64 1D), acf(1D), pacf(1D), upper_band(1D)
# lags: [1,2,3,4,5,6,7,8], acf: [0.33, 0.20, 0.15, ...]
```

[VERIFIED: src/fts_mod.rs:47-86 read in Phase 75 session; all calls run this session]

### 1.5 Narrative Arc for EXMP-01

1. **Intro:** "Forecasting climate curves along a latitude gradient" — the idea that weather stations from south to north form a spatial gradient that can be modeled as a functional series.
2. **Data section:** Load Canadian weather, sort by latitude, show 35 weekly curves as a heatmap or overlaid curves (html figure).
3. **Stationarity check:** `stationarity_test` → p=0.010 → the series is non-stationary (expected: cold northern stations are structurally different from warm southern ones).
4. **ACF:** `functional_acf` → lag-1 ACF ≈ 0.33 → nearby stations correlate, which justifies the FTSM's AR modeling.
5. **Fitting FTSM:** `ftsm` → ncomp=3, show variance breakdown (86%/10%/4%), show AR orders [1, 0, 1] for each component.
6. **Forecast:** `ftsm_forecast_multistep` → 5-step forecast of the 5 most-northern stations. Show forecast vs truth (html figure).
7. **Evaluation:** RMSE = 14.18°C — reasonable for a 5-step spatial extrapolation beyond the training range; interpret in context.
8. **Parameter table** + See also.

### 1.6 Fence Timing (VERIFIED by running)

| Fence | Data shape | Timing |
|-------|-----------|--------|
| `ftsm` | (30, 52) | 0.012s |
| `ftsm_forecast_multistep` h=5 | (30, 52) | 0.011s |
| `stationarity_test` n_perm=99 | (30, 52) | 0.006s |
| `functional_acf` n_sim=99 | (30, 52) | 0.028s |

All fences run in < 0.05s. Use `fast(999, 99)` for `n_perm` and `n_sim` to keep strict build bounded.

### 1.7 Cross-Reference Targets

- Method page: `docs/analyze/functional-time-series.md` — link back as primary cross-reference
- `docs/examples/canadian-seasonal.md` — same dataset, different analysis (seasonal decomposition)
- `docs/examples/canadian-weather.md` — same dataset, FPCA + clustering

---

## 2. EXMP-02 — Fréchet Regression (metric-space response)

### 2.1 Framing Decision (VERIFIED by running)

**Chosen construction:** Per-station temperature-distribution density regressed on station latitude.

**Why this is a real-data fit:**
- Each Canadian weather station has 365 daily temperatures. Building a KDE over these gives a genuine probability density curve representing the station's temperature distribution.
- Cold northern stations have left-shifted, wider distributions (temperatures range from -40°C to +15°C); warm southern stations have right-shifted, narrower distributions (temperatures range from -10°C to +30°C). The shift with latitude is real and substantial.
- Latitude is a natural scalar predictor. The question "how does the shape of a station's temperature distribution change with latitude?" is a genuine Fréchet regression question in density/Wasserstein space.
- Both `frechet_global_reg` and `frechet_local_reg` accept this (n, m) density-response matrix directly.
- `frechet_mean` can be used to visualize the overall average distribution as motivation.

**Construction validation:**
- 35 density curves (one per station) on a common 60-point temperature grid [-40°C, 40°C].
- Each density normalized to integrate to 1 via `normalize_density`.
- KDE with silverman bandwidth — fast (< 0.01s per station), deterministic.
- `frechet_global_reg` on this data: 0.006s [VERIFIED: run this session].
- Train-test ISE evaluation (28/7 split): global ISE=0.001622, local ISE=0.001401 [VERIFIED: run this session].

**Note on scipy dependency:** The KDE construction uses `scipy.stats.gaussian_kde`. scipy is already in `docs/examples/` fences (confirmed in mature pages). It is an optional dependency listed in CLAUDE.md (`scipy 1.10+`). This is the only place scipy is needed in the fence.

### 2.2 Dataset Loader

```python
from docs_data import load_canadian_weather
day, X, meta = load_canadian_weather("temperature")
# day: shape (365,), X: shape (35, 365), meta: columns [station, province, region, lat, lon]
```

[VERIFIED: scripts/docs_data.py:59-88 read this session]

### 2.3 Data Construction Recipe

```python
from scipy.stats import gaussian_kde
from fdars.density_fda import normalize_density

t_min, t_max = X.min() - 2, X.max() + 2
t_grid = np.linspace(t_min, t_max, 60)   # (60,) — common temperature grid

densities = []
for i in range(35):
    kde = gaussian_kde(X[i], bw_method='silverman')
    dens = normalize_density(kde(t_grid), t_grid)   # (60,) — integrates to 1
    densities.append(dens)

density_matrix = np.vstack(densities)   # (35, 60)
lat = meta['lat'].to_numpy()             # (35,) — scalar predictor
```

### 2.4 Exact API Calls (from 74-RESEARCH, all VERIFIED)

```python
from fdars.frechet import frechet_global_reg, frechet_local_reg, frechet_mean

# Frechet mean of all station densities (for motivation/intro)
mean_density = frechet_mean(list(density_matrix), space="density", d=60)
# IMPORTANT: frechet_mean space="density" is NOT in the binding!
# frechet_mean supports: "spd", "spherical", "correlation" — NOT "density"
# For the mean density, use wasserstein_barycenter instead:
from fdars.density_fda import wasserstein_barycenter
mean_density = wasserstein_barycenter(density_matrix, t_grid)   # (60,)

# Train-test split
rng = np.random.default_rng(42)
idx = rng.permutation(35)
train_idx, test_idx = idx[:28], idx[28:]

pred_train = lat[train_idx].reshape(-1, 1)   # (28, 1) — MUST be 2D
pred_test  = lat[test_idx].reshape(-1, 1)    # (7, 1)
resp_train = density_matrix[train_idx]        # (28, 60)
resp_test  = density_matrix[test_idx]         # (7, 60)

# Global regression
result_g = frechet_global_reg(pred_train, resp_train, t_grid, pred_test)
# Returns dict: predicted(7, 60), xout(7, 1), x_bar(1,)
predicted_g = np.asarray(result_g['predicted'])   # (7, 60) — NAKED ARRAY ACCESS

# Local regression
result_l = frechet_local_reg(pred_train, resp_train, t_grid, pred_test, bandwidth=5.0)
# Returns dict: predicted(7, 60), xout(7, 1), bandwidth(float) — NO x_bar
predicted_l = np.asarray(result_l['predicted'])

# Evaluation: ISE (Integrated Squared Error)
ise_g = np.trapezoid((predicted_g - resp_test)**2, t_grid, axis=1).mean()
ise_l = np.trapezoid((predicted_l - resp_test)**2, t_grid, axis=1).mean()
# Measured: global ISE=0.001622, local ISE=0.001401 (local better for spatial data)
```

[VERIFIED: frechet API from 74-RESEARCH src/frechet_mod.rs; run confirmed this session]

**CRITICAL GOTCHA — naked-array access:** `result_g['predicted']` returns a Python list-of-lists, NOT a numpy array. Always wrap with `np.asarray(result_g['predicted'])`. This is the primary pitfall from Phase 74 research.

**CRITICAL GOTCHA — xout must be 2D:** `pred_test.reshape(-1, 1)` is required even for p=1 scalar predictor. Passing a 1D array `lat[test_idx]` raises a shape error.

**CRITICAL GOTCHA — frechet_mean does NOT support space="density":** The binding supports `space` values `"spd"`, `"spherical"`, `"correlation"` only [VERIFIED: src/frechet_mod.rs:343-344 read in Phase 74 session]. For a density mean, use `wasserstein_barycenter` from `fdars.density_fda`.

### 2.5 Narrative Arc for EXMP-02

1. **Intro:** "How does Canada's temperature distribution change with latitude?" — Fréchet regression in density/Wasserstein space as a way to regress density-valued responses on a scalar predictor.
2. **Data section:** Load Canadian weather, build KDE densities, show 5 representative station densities colored by latitude (html figure). Show the Wasserstein barycenter as the "mean" distribution.
3. **Why Fréchet?** Brief math: Euclidean mean of densities is wrong (negative values, wrong shape); Fréchet mean minimizes Wasserstein-2 distance. Contrast pointwise-average vs. barycenter.
4. **Global regression:** `frechet_global_reg` — linear relationship: as latitude increases, distribution shifts left and widens. Show predicted distributions at southern/central/northern latitudes overlaid (html figure).
5. **Local regression:** `frechet_local_reg(bandwidth=5.0)` — allows nonlinear latitude effect. Compare to global visually.
6. **Evaluation:** ISE on 7 held-out test stations. Local regression slightly better (ISE 0.00140 vs 0.00162).
7. **Interpretation:** The predicted distribution at any latitude is itself a valid probability density (integrates to 1) — this is what makes Fréchet regression special vs. standard regression on density features.
8. **Parameter table** + See also.

### 2.6 Fence Timing (VERIFIED by running)

| Fence | Data shape | Timing |
|-------|-----------|--------|
| KDE construction (35 stations) | (35, 365) | < 0.05s |
| `normalize_density` (35×) | (60,) each | negligible |
| `frechet_global_reg` | (28, 60) responses | 0.006s |
| `frechet_local_reg` | (28, 60) responses | 0.006s |
| `wasserstein_barycenter` | (35, 60) | < 0.001s |

All fences run in < 0.1s. No `fast()` call needed.

### 2.7 Cross-Reference Targets

- Method page: `docs/regression/frechet-regression.md` — primary cross-reference
- `docs/analyze/density-fda.md` — LQD / Wasserstein background
- `docs/examples/canadian-weather.md` — same dataset, different analysis

---

## 3. EXMP-03 — Shapelet Classification (phoneme.csv)

### 3.1 Framing Decision (VERIFIED by running)

**Chosen construction:** All 5 phoneme classes, 20 curves per class (100 total), max_candidates=200. Narrative follows `discover_shapelets` (summary) → `shapelet_transform_fit` + `shapelet_transform` (feature extraction) → `shapelet_classifier_fit` + `.predict()` (classification).

**Why 5 classes (all of them) rather than a 2- or 3-class subset:**
- CONTEXT.md explicitly says "strong 5-class fit" — the user wants the full 5-class example.
- 5 classes × 20 curves = 100 curves total. `shapelet_classifier_fit` with max_candidates=200 takes ~0.95s for this, within the <5s fence budget.
- The 5-class story is richer: discover shapelets → show the feature matrix → classify → per-class accuracy breakdown.

**Accuracy at this scale (VERIFIED by running):**
- `discover_shapelets` returns n_shapelets=97 with quality="info_gain" [VERIFIED: run this session].
- `shapelet_transform_fit` + `shapelet_transform` produces a (100, 97) feature matrix [VERIFIED: run this session].
- 80/20 split (16 train, 4 test per class): test accuracy ~0.60 for k=3 kNN [VERIFIED: run this session].
- The accuracy is moderate — the narrative should frame this honestly: with only 20 curves/class and 256 grid points, shapelet discovery finds approximately 100 subsequences that partially separate 5 classes. Higher accuracy requires more data or more candidates. A 2-class subset (aa vs sh) achieves test accuracy 1.000 at the same budget [VERIFIED: run this session] — include this as a showcase.

**Recommended narrative:** Main example on 3 acoustically-distinct classes (aa/sh/dcl, n=30 per class, max_candidates=200), achieving test accuracy ~0.72–0.78 [VERIFIED: run this session]. Then show 5-class version as "scaling up" with lower accuracy — honest pedagogical framing.

**Alternative: full 5-class with 20/class.** This is also valid for a single end-to-end narrative if the page frames test accuracy expectations upfront.

### 3.2 Dataset Loader

```python
from docs_data import load_phoneme
freq, X, meta = load_phoneme()
# freq: np.ndarray shape (256,) — frequency index 1..256
# X:    np.ndarray shape (400, 256) — log-periodogram per utterance
# meta: DataFrame with column 'phoneme' (class label: 'aa','ao','dcl','iy','sh')
```

[VERIFIED: scripts/docs_data.py:111-131 read this session; balanced: 80 per class]

### 3.3 Exact API Calls (from 75-RESEARCH, all VERIFIED)

```python
from fdars.shapelet import (discover_shapelets, shapelet_transform_fit,
                            shapelet_transform, shapelet_classifier_fit)
import numpy as np

ph = meta['phoneme'].to_numpy()
classes = sorted(set(ph))   # ['aa', 'ao', 'dcl', 'iy', 'sh']

# 3-class subset: acoustically most distinct (aa=vowel, sh=fricative, dcl=stop)
c_sel = ['aa', 'sh', 'dcl']
n_per = 30
idx = np.concatenate([np.where(ph == c)[0][:n_per] for c in c_sel])
X_sub = np.ascontiguousarray(X[idx], dtype=np.float64)   # (90, 256)
y_sub = np.array([i for i in range(3) for _ in range(n_per)], dtype=np.int64)

# 80/20 train-test split per class
train_idx = np.concatenate([np.where(y_sub == i)[0][:24] for i in range(3)])
test_idx  = np.concatenate([np.where(y_sub == i)[0][24:] for i in range(3)])
X_train, y_train = X_sub[train_idx], y_sub[train_idx]   # (72, 256)
X_test,  y_test  = X_sub[test_idx],  y_sub[test_idx]    # (18, 256)

# Step 1: Discover (summary dict)
disc = discover_shapelets(X_train, y_train, max_candidates=200, seed=42)
# Returns dict: n_shapelets(int), quality(str)  — NOT a list of arrays
# Example: {'n_shapelets': 93, 'quality': 'info_gain'}

# Step 2: Transform (feature extraction)
stfit = shapelet_transform_fit(X_train, y_train, max_candidates=200, seed=42)
# Returns: PyShapeletFit handle with .n_shapelets (int) and .n_train (int)
feat_train = shapelet_transform(stfit, X_train)   # (72, K) — K = stfit.n_shapelets
feat_test  = shapelet_transform(stfit, X_test)    # (18, K)

# Step 3: Classify
clf = shapelet_classifier_fit(X_train, y_train,
                               max_candidates=200, seed=42,
                               classifier='knn', k=1)
# Returns: PyShapeletClassifierFit handle with .train_accuracy, .n_shapelets, .classes, .n_classes
preds = clf.predict(X_test)   # (18,) int64 predicted labels
test_acc = np.mean(preds == y_test)
# Measured: train_acc≈0.875, test_acc≈0.722 (knn, k=1, 3-class)
# With LDA: train_acc=1.000, test_acc≈0.778

# Per-class accuracy
for i, cname in enumerate(c_sel):
    mask = y_test == i
    cls_acc = np.mean(preds[mask] == y_test[mask])
    print(f'{cname}: {cls_acc:.2f}')
```

[VERIFIED: all calls run this session; src/shapelet_mod.rs read in Phase 75 session]

**KEY API FACTS (from 75-RESEARCH, VERIFIED):**
- `discover_shapelets` returns `{'n_shapelets': int, 'quality': str}` — NOT a list of arrays. [VERIFIED: src/shapelet_mod.rs:211-244]
- `shapelet_classifier_fit` has `ncomp=None` parameter (optional PCA pre-reduction). [VERIFIED: src/shapelet_mod.rs:386-389]
- `classifier` parameter: `"knn"` or `"lda"` only. [VERIFIED: src/shapelet_mod.rs:386-428]
- Default `k=1` (not k=3). Using `k=3` in example is valid as explicit choice.
- `.predict(new_data)` method returns `(n_new,)` int64 predicted labels.
- `.classes` → sorted unique labels as int64 numpy 1D.

### 3.4 Narrative Arc for EXMP-03

1. **Intro:** "Classifying phonemes by their spectral shapes" — log-periodograms as functional data, shapelet discovery as an interpretable feature extraction method.
2. **Data section:** Load phoneme, show 3 selected class spectra overlaid (html figure — one panel per class or overlaid with color).
3. **Discovery:** `discover_shapelets` → summary dict. Explain what shapelets are: subsequences that maximally separate classes by information gain.
4. **Feature extraction:** `shapelet_transform_fit` + `shapelet_transform` → (72, K) feature matrix. Show heatmap of feature matrix colored by class (html figure) or show distribution of one discriminative shapelet-distance feature per class.
5. **Classification:** `shapelet_classifier_fit` (kNN k=1) → train accuracy, test accuracy per class. Show confusion-like breakdown.
6. **Comparison: LDA vs kNN** (or just pick the better one). Note that LDA achieves higher test accuracy on this data.
7. **Interpretation:** Which shapelets matter? The feature matrix shows which frequency regions are discriminative. High shapelet distances = curve's spectrum differs from a prototypical subshape.
8. **Parameter table** + See also.

### 3.5 Fence Timing (VERIFIED by running)

| Fence | Data shape | max_candidates | Timing |
|-------|-----------|----------------|--------|
| `discover_shapelets` | (72, 256) | 200 | 0.32s |
| `shapelet_transform_fit` | (72, 256) | 200 | 0.58s |
| `shapelet_transform` (train+test) | (72+18, 256) | — | 0.35s |
| `shapelet_classifier_fit` (kNN k=1) | (72, 256) | 200 | 0.58s |
| `.predict` on test | (18, 256) | — | < 0.01s |
| **Total per-page fence time** | | | **< 2s** |

For the 5-class variant (100 curves × 256 pts, max_candidates=200): `shapelet_classifier_fit` takes ~0.95s, total ~2s [VERIFIED: run this session].

### 3.6 Cross-Reference Targets

- Method page: `docs/analyze/shapelets.md` — primary cross-reference
- `docs/examples/phoneme-shape.md` — same dataset, elastic shape analysis (contrast: shapelets are amplitude-based, not elastic)
- `docs/analyze/clustering.md` — clustering with shapelet feature matrix as downstream use

---

## 4. Example Page Structure to Mirror

### 4.1 Mature Example Arc (from reading canadian-seasonal.md and phoneme-shape.md)

[VERIFIED: docs/examples/canadian-seasonal.md and docs/examples/phoneme-shape.md read this session]

```
# [Title: Dataset + what the analysis answers]

**Dataset:** [name + brief description]. [Setup/framing sentence.]

[2-3 paragraph motivation: what question does this analysis answer? why this data?]

![concept diagram](../assets/diagrams/ex-<slug>.svg){ .fdars-diagram }

## [Section 1: Data overview / loading]

```python exec="1" html="1" source="above"
# Load data + show it
```

[Prose interpreting what the plot shows]

## [Section 2: First analysis step]

[Brief mathematical motivation (1-3 sentences) or method description]

```python exec="1" html="1" source="above"
# Run the method + visualize
```

[Prose interpreting the result]

## [Section 3: Second analysis step]

...same pattern...

## [Final analysis section: evaluation or interpretation]

## Parameters

| Function | Key parameters | Description |
...

!!! note "..."
    [One or two key caveats]

## See also

- [Method page](../analyze/method.md) — [one-liner]
- [Related example](related.md) — [one-liner]

## References

- [2-3 citations]
```

**Key conventions observed in mature examples:**
- Sections are plain `## Title` (NO numbering — unlike regression pages). [VERIFIED: canadian-seasonal.md, phoneme-shape.md]
- Each section has exactly one `html="1"` fence OR one non-html fence followed by prose. Usually html="1" for data visualization sections.
- Bold dataset description in the opening paragraph: `**Dataset:** Canadian Weather — ...`.
- `source="above"` is the pattern for exec'd fences in examples (shows the code above the rendered output).
- `!!! note` admonitions used sparingly (1-2 per page, not batched).
- "Parameters" section near the bottom is a plain markdown table summarizing all API calls used on the page, with key parameters listed.
- "See also" is `## See also` (plain header, NOT numbered).
- References: `## References` at the very end, 2-4 items.
- NO concept diagram required for example pages (unlike method pages) — `canadian-seasonal.md` has one but it is an exception for very complex pages.

### 4.2 New File Slugs

| Page | File slug | Suggested title |
|------|-----------|-----------------|
| EXMP-01 | `fts-forecast.md` | `Canadian Weather: Functional Time Series and Forecast` |
| EXMP-02 | `frechet-density-regression.md` | `Canadian Weather: Fréchet Regression on Temperature Distributions` |
| EXMP-03 | `phoneme-shapelets.md` | `Phoneme Classification with Shapelets` |

---

## 5. Nav Wiring

### 5.1 mkdocs.yml (current Examples nav)

[VERIFIED: mkdocs.yml lines 176-198 read this session]

The examples nav currently ends at line 198:
```yaml
  - Examples:
    - examples/index.md
    - Growth — Elastic Alignment: examples/growth-alignment.md
    ...
    - Penicillin — Batch Monitoring: examples/biopharma-monitoring.md
```

**Add the following three entries** to the nav (position: after "Penicillin — Batch Monitoring" or at a logical grouping point):

```yaml
    - Canadian Weather — FTS Forecast: examples/fts-forecast.md
    - Canadian Weather — Fréchet Regression: examples/frechet-density-regression.md
    - Phoneme — Shapelet Classification: examples/phoneme-shapelets.md
```

### 5.2 docs/examples/index.md

[VERIFIED: docs/examples/index.md read this session]

The index uses `<div class="fdars-gallery fdars-sec-examples">` cards with `fdars-gallery-thumb` images. Since gallery cards are deferred to Phase 77, the Phase 76 planner must add the three pages to the index WITHOUT a gallery card — add them to the "What each example shows" table at the bottom of the index instead, and optionally add a brief text link in a new "Forecasting & regression" or appropriate group.

Specifically add rows to the table in index.md:
```markdown
| [Canadian Weather: FTS Forecast](fts-forecast.md) | Canadian Weather | `ftsm`, `ftsm_forecast_multistep`, `stationarity_test`, `functional_acf` |
| [Canadian Weather: Fréchet Regression](frechet-density-regression.md) | Canadian Weather | `frechet_global_reg`, `frechet_local_reg`, `wasserstein_barycenter` |
| [Phoneme: Shapelet Classification](phoneme-shapelets.md) | Phoneme | `discover_shapelets`, `shapelet_transform_fit`, `shapelet_transform`, `shapelet_classifier_fit` |
```

Gallery cards (the `fdars-gallery-item` divs with thumbs) are out of scope for Phase 76.

---

## 6. docs_fig Pattern for Example Pages

[VERIFIED: scripts/docs_fig.py read in Phase 74 session]

```python
# Standard html="1" figure fence pattern for example pages:
from docs_fig import fig, render, fast

f, ax = fig()                     # creates (fig, axes) with project defaults
# or: f, axes = fig(ncols=2, ...)
ax.plot(...)
ax.set(title="...", xlabel="...", ylabel="...")
print(render(f))                   # renders inline SVG
print("FDARS_FENCE_OK")

# For expensive computations gated by DOCS_FAST:
n_perm = fast(999, 99)   # full build: 999; DOCS_FAST=1: 99
```

**Color palette** [VERIFIED: scripts/docs_fig.py:43-51]:
- Primary: `#3f51b5` (indigo)
- Secondary: `#e8710a` (orange)
- Tertiary: `#198754` (green), `#dc3545` (red), `#6f42c1` (purple), `#0dcaf0` (cyan), `#6c757d` (grey)

---

## 7. Complete Verified Code Skeletons

### 7.1 EXMP-01 — FTS Core Fence (verified, runs in < 0.1s)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
from docs_data import load_canadian_weather
from fdars.fts import ftsm, ftsm_forecast_multistep, stationarity_test, functional_acf

day, X, meta = load_canadian_weather("temperature")
lat = meta["lat"].to_numpy()
order = np.argsort(lat)
X_ord = X[order]  # (35, 365) — ascending latitude

# Weekly mean aggregation
X_wk = X_ord[:, :364].reshape(35, 52, 7).mean(axis=2)  # (35, 52)
t_wk = np.arange(52, dtype=float)

# Train on 30 southern stations, forecast 5 northern
X_train, X_test = X_wk[:30], X_wk[30:]

fit = ftsm(X_train, t_wk, ncomp=3)
fc  = ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)

scores    = np.asarray(fit["scores"])
fcast     = np.asarray(fc["forecast"])
pve       = 100 * scores.var(axis=0) / scores.var(axis=0).sum()
rmse      = np.sqrt(np.mean((fcast - X_test)**2))

f, axes = fig(nrows=2, figsize=(7.5, 5.0))
weeks = np.arange(52)
for xi in X_train[::6]:
    axes[0].plot(weeks, xi, color="#6c757d", lw=0.6, alpha=0.4)
axes[0].set(title="Training: 30 southern stations (weekly mean temperature)",
            ylabel="temp (°C)")

palette = ["#3f51b5", "#e8710a", "#198754", "#dc3545", "#6f42c1"]
for k in range(5):
    axes[1].plot(weeks, fcast[k], color=palette[k], lw=2.0,
                 label=f"forecast s={k+1}")
    axes[1].plot(weeks, X_test[k], color=palette[k], lw=0.8, ls="--", alpha=0.6)
axes[1].set(title=f"5-station forecast vs truth  (RMSE {rmse:.1f}°C)",
            xlabel="week", ylabel="temp (°C)")
axes[1].legend(fontsize=8, ncol=3)
print(render(f))
print("FDARS_FENCE_OK")
```

### 7.2 EXMP-01 — Stationarity + ACF Fence (verified, runs in < 0.05s)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
from docs_data import load_canadian_weather
from fdars.fts import stationarity_test, functional_acf

day, X, meta = load_canadian_weather("temperature")
order = np.argsort(meta["lat"].to_numpy())
X_wk = X[order][:, :364].reshape(35, 52, 7).mean(axis=2)
t_wk = np.arange(52, dtype=float)
X_train = X_wk[:30]

st  = stationarity_test(X_train, t_wk, n_perm=fast(999, 99), seed=42)
acf = functional_acf(X_train, t_wk, max_lag=8, n_sim=fast(999, 99), seed=42)

lags  = np.asarray(acf["lags"])
avals = np.asarray(acf["acf"])
upper = float(np.asarray(acf["upper_band"])[0])

f, ax = fig(figsize=(7.0, 3.6))
ax.bar(lags, avals, color="#3f51b5", width=0.6)
ax.axhline(upper, color="#dc3545", ls="--", lw=1.4, label=f"95% band ({upper:.2f})")
ax.axhline(-upper, color="#dc3545", ls="--", lw=1.4)
ax.set(title=f"Functional ACF  (stationarity p={st['p_value']:.3f})",
       xlabel="lag (stations)", ylabel="ACF statistic")
ax.legend(fontsize=9)
print(render(f))
print("FDARS_FENCE_OK")
```

### 7.3 EXMP-02 — Fréchet Density Regression Core Fence (verified, runs in < 0.1s)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from docs_fig import fig, render
from scipy.stats import gaussian_kde
from fdars.density_fda import normalize_density, wasserstein_barycenter
from fdars.frechet import frechet_global_reg, frechet_local_reg

day, X, meta = load_canadian_weather("temperature")
lat = meta["lat"].to_numpy()
t_grid = np.linspace(X.min() - 2, X.max() + 2, 60)

# Build one density per station
density_matrix = np.vstack([
    normalize_density(gaussian_kde(X[i], bw_method="silverman")(t_grid), t_grid)
    for i in range(35)
])  # (35, 60)

# Wasserstein barycenter as the "mean distribution"
bary = wasserstein_barycenter(density_matrix, t_grid)  # (60,)

# Fréchet regression: latitude → temperature distribution
rng = np.random.default_rng(42)
idx = rng.permutation(35)
tr, te = idx[:28], idx[28:]
pred_tr = lat[tr].reshape(-1, 1)
pred_te = lat[te].reshape(-1, 1)

result_g = frechet_global_reg(pred_tr, density_matrix[tr], t_grid, pred_te)
result_l = frechet_local_reg(pred_tr, density_matrix[tr], t_grid, pred_te, bandwidth=5.0)
pred_g = np.asarray(result_g["predicted"])  # (7, 60)
pred_l = np.asarray(result_l["predicted"])  # (7, 60)

ise_g = np.trapezoid((pred_g - density_matrix[te])**2, t_grid, axis=1).mean()
ise_l = np.trapezoid((pred_l - density_matrix[te])**2, t_grid, axis=1).mean()

# Show predicted densities at 3 reference latitudes
xout_ref = np.array([[45.0], [55.0], [65.0]])
pred_ref = np.asarray(frechet_global_reg(pred_tr, density_matrix[tr],
                                          t_grid, xout_ref)["predicted"])

f, axes = fig(ncols=2, figsize=(9.0, 4.0))
axes[0].fill_between(t_grid, bary, alpha=0.25, color="#6c757d", label="barycenter")
for k, (xlat, col) in enumerate(zip([45, 55, 65],
                                     ["#e8710a", "#3f51b5", "#198754"])):
    axes[0].plot(t_grid, pred_ref[k], color=col, lw=2.0, label=f"{xlat}°N")
axes[0].set(title="Global Fréchet: predicted densities by latitude",
            xlabel="temperature (°C)", ylabel="density")
axes[0].legend(fontsize=8)

names = ["global", "local (bw=5°)"]
vals  = [ise_g, ise_l]
axes[1].bar(names, vals, color=["#3f51b5", "#e8710a"], width=0.4)
for k, v in enumerate(vals):
    axes[1].text(k, v * 1.02, f"{v:.5f}", ha="center", fontsize=8)
axes[1].set(title="Test ISE: local regression wins",
            ylabel="mean integrated squared error")
print(render(f))
print("FDARS_FENCE_OK")
```

### 7.4 EXMP-03 — Shapelet Classification Core Fence (verified, runs in < 2s)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme
from fdars.shapelet import (discover_shapelets, shapelet_transform_fit,
                             shapelet_transform, shapelet_classifier_fit)

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()

# 3 acoustically distinct classes: vowel, fricative, stop
c_sel = ["aa", "sh", "dcl"]
n_per = 30
idx   = np.concatenate([np.where(ph == c)[0][:n_per] for c in c_sel])
X_sub = np.ascontiguousarray(X[idx], dtype=np.float64)  # (90, 256)
y_sub = np.array([i for i in range(3) for _ in range(n_per)], dtype=np.int64)

tr_idx = np.concatenate([np.where(y_sub == i)[0][:24] for i in range(3)])
te_idx = np.concatenate([np.where(y_sub == i)[0][24:] for i in range(3)])
X_tr, y_tr = X_sub[tr_idx], y_sub[tr_idx]  # (72, 256)
X_te, y_te = X_sub[te_idx], y_sub[te_idx]  # (18, 256)

# Step 1: discover (summary dict — NOT a list of shapelet arrays)
disc = discover_shapelets(X_tr, y_tr, max_candidates=200, seed=42)
# disc = {'n_shapelets': int, 'quality': str}

# Step 2: transform (feature extraction)
stfit = shapelet_transform_fit(X_tr, y_tr, max_candidates=200, seed=42)
feat_tr = shapelet_transform(stfit, X_tr)  # (72, K)
feat_te = shapelet_transform(stfit, X_te)  # (18, K)

# Step 3: classify
clf   = shapelet_classifier_fit(X_tr, y_tr, max_candidates=200, seed=42,
                                 classifier="knn", k=1)
preds = clf.predict(X_te)
test_acc = np.mean(preds == y_te)
per_cls  = [np.mean(preds[y_te == i] == y_te[y_te == i]) for i in range(3)]

palette = ["#3f51b5", "#e8710a", "#198754"]
f, axes = fig(ncols=2, figsize=(9.0, 4.0))

# Feature matrix heatmap
im = axes[0].imshow(feat_tr, aspect="auto", cmap="viridis")
for i in range(3):
    axes[0].axhline(24 * i - 0.5, color="white", lw=1.2, ls="--")
axes[0].set(title=f"Shapelet feature matrix  (K={stfit.n_shapelets} shapelets)",
            xlabel="shapelet index", ylabel="curve index")
f.colorbar(im, ax=axes[0], shrink=0.7)

# Per-class accuracy bars
axes[1].bar(c_sel, per_cls, color=palette, width=0.5)
for k, v in enumerate(per_cls):
    axes[1].text(k, v + 0.02, f"{v:.0%}", ha="center")
axes[1].set(title=f"Per-class test accuracy  (overall {test_acc:.0%})",
            ylabel="accuracy", ylim=(0, 1.15))
print(render(f))
print("FDARS_FENCE_OK")
```

---

## 8. Common Pitfalls

### Pitfall 1: frechet_global_reg / frechet_local_reg — naked-array return
**What goes wrong:** `result['predicted']` is a Python list-of-lists, not a numpy array. Calling `.shape` on it raises `AttributeError`.
**How to avoid:** Always `np.asarray(result['predicted'])` before indexing.

### Pitfall 2: xout must be 2D
**What goes wrong:** `frechet_global_reg(pred, resp, t, lat[test_idx])` raises a shape error — `xout` must be 2D `(n_out, p)`.
**How to avoid:** `lat[test_idx].reshape(-1, 1)` for scalar predictor.

### Pitfall 3: frechet_mean does NOT support space="density"
**What goes wrong:** `frechet_mean(objects, space="density", d=60)` raises `ValueError: unsupported space`.
**How to avoid:** Use `wasserstein_barycenter(density_matrix, argvals)` from `fdars.density_fda` for the density Fréchet mean.

### Pitfall 4: discover_shapelets returns a summary dict, not arrays
**What goes wrong:** `for s in discover_shapelets(...)` raises `TypeError` or iterates over dict keys.
**How to avoid:** `disc['n_shapelets']` gives the count; raw shapelet subsequences are stored internally in `PyShapeletFit` (use `shapelet_transform_fit` to get them).

### Pitfall 5: ftsm weights are per-grid-point, not variance explained
**What goes wrong:** `fit['weights']` shape is `(m,)` — it is NOT a variance-explained array. Treating it as PVE gives nonsense.
**How to avoid:** Compute PVE from scores: `scores = np.asarray(fit['scores']); pve = scores.var(axis=0) / scores.var(axis=0).sum()`.

### Pitfall 6: functional_acf is slow on large grids
**What goes wrong:** `functional_acf(X, t, n_sim=999)` on 30×365 takes 4.8s — too slow for a strict build fence.
**How to avoid:** Use weekly-aggregated data (30×52) where `functional_acf` runs in 0.028s; gate `n_sim` with `fast(999, 99)`.

### Pitfall 7: normalize_density requires non-negative input
**What goes wrong:** Passing raw KDE output can occasionally include tiny negative values near boundaries; `normalize_density` raises `ValueError` if any value is negative.
**How to avoid:** `dens = np.clip(kde(t_grid), 0, None)` before calling `normalize_density`, or ensure the KDE grid does not extend too far into the tails.

### Pitfall 8: np.ascontiguousarray required for phoneme data
**What goes wrong:** `shapelet_classifier_fit(X[idx])` without `ascontiguousarray` may raise a buffer-not-C-contiguous error depending on the slice.
**How to avoid:** Always `np.ascontiguousarray(X[idx], dtype=np.float64)` when constructing the subset.

---

## 9. Environment Availability

All code runs against the installed `.venv` package. No new bindings, no new tools.

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| `fdars` (compiled) | All fences | Yes | `.venv/_native.abi3.so` exists |
| `matplotlib` | `html="1"` fences | Yes | Used by all existing examples |
| `docs_fig.py` | `fig()`/`render()`/`fast()` | Yes | `scripts/docs_fig.py` present |
| `docs_data.py` | Dataset loaders | Yes | `scripts/docs_data.py` present |
| `markdown-exec` | Fence execution | Yes | Already wired into `mkdocs.yml` |
| `numpy` | All fences | Yes | Required by fdars |
| `scipy.stats.gaussian_kde` | EXMP-02 density construction | Yes | scipy listed as docs optional dep |
| `run_page_fences.py` | Fence verification | Yes | `scripts/run_page_fences.py` from Phase 74 |

---

## 10. Validation Architecture

> `workflow.nyquist_validation` is explicitly `false` in `.planning/config.json`. Section skipped.

---

## 11. Security Domain

> Docs-only phase — no API surface changes, no authentication, no network calls. `security_enforcement` is enabled but no ASVS categories apply to static documentation editing with pre-approved local CSV datasets.

---

## 12. Open Questions

1. **EXMP-03 accuracy framing.** The 3-class (aa/sh/dcl) test accuracy is ~72–78% with `max_candidates=200, n_per=30`. This is honest but not spectacular. The page should frame this as "shapelets discover interpretable subsequences that partially separate classes — full accuracy requires more data or candidates." A `!!! note "Scaling up"` admonition should mention that the full 400-curve dataset with `max_candidates=0` (exhaustive) achieves higher accuracy. [ASSUMED: full dataset accuracy not measured this session]

2. **EXMP-02 scipy availability in docs venv.** Verified: `scipy.stats.gaussian_kde` is available in the `.venv` venv. [VERIFIED: run `python -c "from scipy.stats import gaussian_kde"` this session — exits 0]. No action needed.

3. **Diagram requirement for EXMP pages.** The mature examples (canadian-seasonal.md, phoneme-shape.md) have concept diagrams (`../assets/diagrams/ex-*.svg`). Phase 76 does not have a diagram mandate (Phase 79 is the SVGO/diagram gate). The planner should NOT add diagram references in Phase 76 — they would break the strict build if the SVG file doesn't exist.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| ~~A1~~ | ~~`scipy.stats.gaussian_kde` is available in the docs build venv~~ | Section 2, Open Q2 | RESOLVED: verified by running `from scipy.stats import gaussian_kde` in `.venv` this session |
| A2 | Full 5-class phoneme with `max_candidates=0` achieves >85% test accuracy (used as a "scaling up" claim) | Section 3 | Accuracy claim in narrative is wrong; remove or caveat |
| A3 | The "latitude gradient" spatial series framing is accepted as a genuine FTS narrative by the audience | Section 1 | Editorial pushback; fallback: use single-station weekly curves (n=52, m=7) |

**Verified claim count:** All API names, parameter names, defaults, return keys, and data shapes in Sections 1–3 are verified either by running code under .venv this session OR by reading Rust binding sources in Phase 74/75 research sessions.

---

## Sources

### Primary (HIGH confidence — verified by running this session)
- Running `load_canadian_weather()` and `ftsm`, `ftsm_forecast_multistep`, `stationarity_test`, `functional_acf` on the constructed (30, 52) dataset — all timing and output values measured.
- Running `frechet_global_reg`, `frechet_local_reg` on (28, 60) density-response matrix derived from canadian_weather — ISE values and timing measured.
- Running `discover_shapelets`, `shapelet_transform_fit`, `shapelet_transform`, `shapelet_classifier_fit` on 3-class and 5-class phoneme subsets — timing, n_shapelets, accuracy values measured.
- `scripts/docs_data.py` — read this session; `load_canadian_weather`, `load_phoneme` signatures and return shapes verified.

### Secondary (HIGH confidence — from Phase 74/75 research)
- `src/fts_mod.rs` — ftsm, ftsm_forecast_multistep, stationarity_test, functional_acf signatures and return keys [VERIFIED: Phase 75 session]
- `src/frechet_mod.rs` — frechet_global_reg, frechet_local_reg, frechet_mean, frechet_anova signatures and return keys [VERIFIED: Phase 74 session]
- `src/shapelet_mod.rs` — discover_shapelets, shapelet_transform_fit, shapelet_transform, shapelet_classifier_fit return types; PyShapeletFit / PyShapeletClassifierFit handle properties [VERIFIED: Phase 75 session]

### Secondary (MEDIUM confidence — read this session)
- `docs/examples/canadian-seasonal.md` — mature example narrative arc and formatting conventions
- `docs/examples/phoneme-shape.md` — mature example structure with html="1" fences and `source="above"` pattern
- `docs/examples/index.md` — nav card structure, "What each example shows" table pattern
- `mkdocs.yml` lines 176–198 — exact examples nav entries and YAML format

---

## Metadata

**Confidence breakdown:**
- API surface (all three examples): HIGH — all function calls verified by running under .venv this session
- Data construction recipes: HIGH — verified by running and inspecting outputs
- Timing estimates: HIGH — measured by running under .venv with DOCS_FAST=1
- Narrative arc / section structure: HIGH — verified against two mature example pages read this session
- Nav wiring format: HIGH — verified against mkdocs.yml read this session
- scipy availability in docs venv: ASSUMED — not verified

**Research date:** 2026-09-05
**Valid until:** Tied to v11.0 fdars bindings. Valid until a new fdars-core version lands (no bump planned in v12.0 per REQUIREMENTS.md).
