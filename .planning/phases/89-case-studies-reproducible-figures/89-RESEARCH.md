# Phase 89: Case Studies + Reproducible Figures - Research

**Researched:** 2026-09-09
**Domain:** fdars 0.12.0 case-study analysis pipelines + deterministic figure generation
**Confidence:** HIGH (all four studies executed against fdars 0.12.0 in `.venv` this session; real output numbers captured; signatures verified)

---

## Summary

Phase 89 produces four illustrative case studies, each a narrative worked example with figures
regenerated deterministically by `paper/code/` scripts and committed under `paper/figures/`. This
research validates that each proposed analysis *actually runs* against fdars 0.12.0, captures real
accuracy / R² numbers for honest narrative, and documents the exact call shapes, dataset
orientations, and gotchas the executor needs.

The key make-or-break question is determinism: every study involves either stochastic operations
(train/test splits, RNG seeds in alignment) or parallelism (rayon in Rust). All are pinnable via
`np.random.seed`, `random_state=42` in sklearn, and `n_jobs=1` in `GridSearchCV`. The FTS study
(Study 3) has NO stochastic step — the determinism risk is only float-printing; pin with
`np.round`. The alignment study (Study 2) has elastic alignment which is iterative but
deterministic (no stochastic component confirmed); `karcher_mean` converged=False on 30-curve
subset is expected (max_iter=20, tol=1e-4) but the aligned data is still usable.

**Primary recommendation:** Use the validated pipelines verbatim. The only design choice left
to the executor is the exact subplot layout and figure aesthetic — every analytical call and every
result number is pinned by this research.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Each study is driven by an executed `paper/code/` script that reuses the Phase 85 harness
  (`paper_utils.fig`, `FDARS_COLORS`, `save_figure` with `metadata={"CreationDate": None}`,
  `data_path()`), runs the real fdars analysis, and writes committed figure(s) to `paper/figures/`.
- DETERMINISM IS MANDATORY: `Agg` backend, module-top rcParams, per-figure `np.random.seed` /
  `default_rng`, contiguous float64 arrays, no timestamps. Re-run must leave
  `git diff paper/figures/` EMPTY (SC-5). Wire study-figure generation into `make paper`; the
  determinism gate joins the existing `git diff --exit-code paper/figures/` check.
- Reuse validated fdars call shapes + signature gotchas from 88-RESEARCH.md (int64 labels,
  contiguous float64, `FPCATransformer(n_components=)`, `ftsm_forecast` takes raw data, spm
  unpacked, etc.). Each analysis MUST actually run against fdars 0.12.0.

### Claude's Discretion

Exact plots per study, figure count, subplot layout, dataset choice within each study's listed
pair, and narrative length are at the planner/executor's discretion, provided every figure is
deterministic + committed, every analysis actually runs against fdars 0.12.0, and results are
reported honestly (real accuracy/score numbers from the executed run).

### Deferred Ideas (OUT OF SCOPE)

- Close gate, arXiv ID, citable release, human approval → Phase 90.
- No benchmarks / performance timing (milestone lock).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CASE-01 | Smooth + FPCA + classification on phoneme/growth, with reproducible figures | §Study 1 — validated pipeline + exact output numbers |
| CASE-02 | Registration + functional/scalar-on-function regression on tecator/canadian_weather, with reproducible figures | §Study 2 — validated pipeline + exact output numbers |
| CASE-03 | FTS forecast on `canadian_weather_precip` (dataset structure verified), with reproducible figures | §Study 3 — validated pipeline + exact output numbers |
| CASE-04 | sklearn `Pipeline` + `GridSearchCV` on wine/sonar showcasing the estimator layer, with reproducible figures | §Study 4 — validated pipeline + exact output numbers |
</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Analysis pipelines (fdars calls) | `paper/code/gen_figures.py` | reuse `paper_utils.data_path` | Executed Python; appended to existing `main()` |
| Figures | `paper/figures/*.pdf` | committed artifacts | Deterministic PDFs via `save_figure` |
| LaTeX narrative | `paper/sections/casestudies.tex` | `paper.tex` (`\input`) | Hand-authored prose + `\includegraphics` |
| Executed snippets (optional) | `paper/code/gen_snippets.py` | `paper/snippets/*.tex` | Small inlined code blocks shown in paper (Phase 88 pattern) |

---

## Dataset Facts (All VERIFIED this session)

### shapes and label columns

`[VERIFIED: runtime pandas read + shape checks]`

| Dataset | CSV shape | fdars orientation | Label / target |
|---------|-----------|-------------------|----------------|
| `phoneme.csv` | (400, 256) — index=phoneme class | `.values.astype(float64)` → (400, 256); `ARG = arange(1, 257)` | index: `['aa', 'ao', 'dcl', 'iy', 'sh']`, 80 per class |
| `wine.csv` | (178, 13) — index=class | `.values.astype(float64)` → (178, 13) | index: 1,2,3 (class counts: 59/71/48); for sklearn: subtract 1 → 0,1,2 as int64 |
| `tecator.csv` | (240, 103) — index=sample | `.iloc[:,:100].astype(float64)` → (240,100) spectra | `tec["fat"].values.astype(float64)` — range 0.9–58.5 |
| `canadian_weather_precip.csv` | (365, 35) — index=day 1–365 | `.T.astype(float64)` → (35, 365); `ARG = arange(1, 366)` | no label — time-series stations |
| `sonar.csv` | (208, 61) incl. label col | `.drop(columns=["label"]).values.astype(float64)` → (208,60) | `sn["label"]`: `Mine`/`Rock` → int64 {0,1} |

**Wine label extraction (verbatim):**
```python
wn = pd.read_csv(data_path("wine.csv"), index_col=0)
Xw = wn.values.astype(np.float64)         # index IS the class column
yw = np.array(wn.index.tolist(), dtype=np.int64) - 1   # 1,2,3 → 0,1,2
```

**Sonar label extraction (verbatim):**
```python
sn = pd.read_csv(data_path("sonar.csv"))   # NO index_col — label is last column
Xs = sn.drop(columns=["label"]).values.astype(np.float64)
lut_s = {"Mine": 1, "Rock": 0}
ys = np.array([lut_s[l] for l in sn["label"].tolist()], dtype=np.int64)
```

### Loader availability

`fdars.datasets.load_growth()`, `load_phoneme()`, `load_tecator()`, `load_wine()`,
`load_sonar()`, `load_canadian_weather(variable='temperature')` all exist and each returns a
`Dataset` dataclass (`.data` = Fdata, `.argvals`, `.y`, `.meta`, `.name`).
`[VERIFIED: runtime, 88-RESEARCH.md §Dataset Suitability]`

The figure scripts use `pd.read_csv(data_path("..."))` per PIPE-01 (no data duplication) — keep
this pattern.

---

## Study 1: Smoothing + FPCA + Classification (CASE-01)

### Dataset choice

**Phoneme** (400 obs × 256 frequency points, 5 balanced classes) is preferred over growth for
classification: it has a genuine multi-class structure (5 phonemes × 80 each), the spectrum is
naturally functional, and it produces a crisp accuracy story.

### Validated pipeline (EXECUTED this session — VERIFIED)

```python
# paper/code/gen_figures.py — _study1() function
import numpy as np
import pandas as pd
from paper_utils import data_path, fig, save_figure, FDARS_COLORS
import fdars
from fdars.sklearn._skeletons import FPCATransformer, FPCLDAClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

np.random.seed(42)

ph = pd.read_csv(data_path("phoneme.csv"), index_col=0)
X = ph.values.astype(np.float64)              # (400, 256)
ARG = np.arange(1, 257, dtype=np.float64)

# Smooth a representative subset (for figure)
sm = fdars.basis.smooth_basis_gcv(X[:20], ARG, n_basis=15, basis_type="bspline")
# sm keys: ['fitted', 'coefficients', 'edf', 'gcv', 'aic', 'bic', 'nbasis']
# sm["fitted"].shape: (20, 256)   sm["nbasis"]: 15

# FPCA
fd = fdars.Fdata(X, argvals=ARG)
pc = fd.to_pc(n_comp=4)
# pc["scores"].shape: (400, 4)
# pc["singular_values"]: [900.055, 518.149, 251.996, 165.088]
# variance explained: [0.693, 0.230, 0.054, 0.023]
# cumulative:         [0.693, 0.922, 0.977, 1.000]

# Build int64 labels (GOTCHA: must be int64 ndarray)
labels_str = ph.index.tolist()
uniq = sorted(set(labels_str))          # ['aa', 'ao', 'dcl', 'iy', 'sh']
lut = {l: i for i, l in enumerate(uniq)}
y = np.array([lut[l] for l in labels_str], dtype=np.int64)

# 5-fold CV: FPCATransformer (n_components) + FPCLDAClassifier (ncomp)
# NOTE SIGNATURE DIFFERENCE: FPCATransformer uses n_components; FPCLDAClassifier uses ncomp
pipe = Pipeline([
    ("fpca", FPCATransformer(n_components=4)),
    ("lda", FPCLDAClassifier(ncomp=4)),
])
cv = cross_val_score(pipe, X, y, cv=5, scoring="accuracy")
# REAL OUTPUT: [0.9, 0.875, 0.812, 0.938, 0.888]  mean: 0.882
```

### Real output numbers (for narrative)

`[VERIFIED: fdars 0.12.0 runtime, executed this session]`

- Smoothing: fitted shape (20, 256), n_basis 15
- FPCA (4 components): variance explained `[0.693, 0.230, 0.054, 0.023]`,
  cumulative `[0.693, 0.922, 0.977, 1.000]` — first 3 PCs explain 97.7%
- Classification (FPCATransformer + FPCLDAClassifier, n_comp=4, 5-fold CV):
  fold scores `[0.900, 0.875, 0.813, 0.938, 0.888]`, **mean accuracy 0.882 (88.2%)**
- Note: `fclassif_knn(X, y, ncomp=4, k=5)` on the full data returns `accuracy: 0.8725`
  (training-set metric, not CV; report only the CV number in narrative)

### Figures to produce

**Figure `study1_phoneme.pdf`** — suggested two-panel layout:
1. **Left panel:** raw phoneme spectra (one color per class, e.g., 5 colors from FDARS_COLORS)
   with 3–5 smoothed curves overlaid (BSpline GCV, 15 basis); demonstrates smoothing.
2. **Right panel:** FPCA scores scatter (PC1 vs PC2, color-coded by class); 5 colored clusters
   demonstrate separability. Add per-class ellipse or convex hull optionally.

**Determinism:** `np.random.seed(42)` before `train_test_split`; FPCA and basis are deterministic
(no stochastic step). `cross_val_score` with default `KFold` is deterministic for these data.

### Determinism pinning

```python
np.random.seed(42)   # top of function, before any call
# No sklearn random_state needed: FPCATransformer + FPCLDAClassifier are deterministic
# KFold(5) with no shuffle is also deterministic
```

---

## Study 2: Registration + Scalar-on-Function Regression (CASE-02)

### Dataset choice

**Tecator** (240 meat samples × 100 spectral channels, fat content scalar response) — clean
scalar-on-function regression story: raw spectra → register to Karcher mean → FPC regression →
predict fat content.

### Validated pipeline (EXECUTED this session — VERIFIED)

```python
# paper/code/gen_figures.py — _study2() function
import numpy as np
import pandas as pd
from paper_utils import data_path, fig, save_figure, FDARS_COLORS
import fdars
from fdars.sklearn._skeletons import FPCRegressor
from sklearn.model_selection import cross_val_score

np.random.seed(42)

tec = pd.read_csv(data_path("tecator.csv"), index_col=0)
Xt = tec.iloc[:, :100].values.astype(np.float64)     # (240, 100) spectra
yfat = tec["fat"].values.astype(np.float64)           # scalar response, range 0.9–58.5
ARGt = np.arange(1, 101, dtype=np.float64)            # 100 spectral channels

# Step 1: registration — align curves to elastic Karcher mean (subset for speed)
km = fdars.alignment.karcher_mean(Xt[:30], ARGt, max_iter=20)
# km keys: ['mean', 'mean_srsf', 'aligned_data', 'gammas', 'n_iter', 'converged']
# km["aligned_data"].shape: (30, 100)   km["converged"]: False (max_iter hit — ok)

# Align ALL curves to that mean
aligned = fdars.alignment.align_to_target(Xt, km["mean"], ARGt)
# aligned keys: ['aligned_data', 'gammas', 'distances']
# aligned["aligned_data"].shape: (240, 100)
Xa = aligned["aligned_data"]

# Step 2: scalar-on-function regression (FPC regression)
sof = fdars.regression.fregre_lm(Xt, yfat, n_comp=5)
# sof keys: ['fitted_values', 'residuals', 'beta_t', 'r_squared', 'coefficients', 'intercept']
# REAL OUTPUT: R^2 = 0.9287   beta_t.shape: (100,)

# Step 3: sklearn FPCRegressor cross-validation
cv = cross_val_score(FPCRegressor(n_components=5), Xt, yfat, cv=5, scoring="r2")
# REAL OUTPUT: [0.903, 0.405, 0.883, 0.922, 0.914]  mean: 0.805
# NOTE: fold 2 (idx=1) has low R^2 — this is real; report mean honestly
```

### Real output numbers (for narrative)

`[VERIFIED: fdars 0.12.0 runtime, executed this session]`

- Alignment: `karcher_mean(Xt[:30], ARGt)` → `aligned_data.shape (30, 100)`, `converged: False`
  (max_iter=20 reached, which is expected and documented); `align_to_target` aligns all 240
  curves → `aligned_data.shape (240, 100)`, `distances.shape (240,)`.
- Scalar-on-function regression (`fregre_lm`, 5 components): **R² = 0.9287** on training data
- FPCRegressor 5-fold CV: fold scores `[0.903, 0.405, 0.883, 0.922, 0.914]`,
  **mean CV R² = 0.805**
- Fat content range: 0.9–58.5 (wide range — regression problem is well-conditioned)
- `beta_t.shape (100,)` — the functional coefficient (100-point spectral curve)

### Key gotcha: `fregre_lm` vs `FPCRegressor` parameter names

`[VERIFIED: runtime inspect.signature this session]`

| Function | Package | Param | Value |
|----------|---------|-------|-------|
| `fdars.regression.fregre_lm` | native | `n_comp` | integer |
| `fdars.sklearn._skeletons.FPCRegressor` | sklearn | `n_components` | integer (default 10) |

These are DIFFERENT parameter names. Do NOT mix them.

### Figures to produce

**Figure `study2_tecator.pdf`** — suggested two-panel layout:
1. **Left panel:** raw spectra (grey) + aligned spectra (colored or mean highlighted);
   demonstrates what registration does to the curves.
2. **Right panel:** actual vs fitted fat content scatter (`sof["fitted_values"]` vs `yfat`),
   with R²=0.93 annotated; demonstrates regression quality.

**Determinism:** `np.random.seed(42)` top of function. `karcher_mean` and `align_to_target`
are deterministic (iterative gradient descent, no random init). `fregre_lm` is deterministic
(linear algebra). `FPCRegressor` cross-val with default `KFold` is deterministic.

---

## Study 3: Functional Time Series Forecast (CASE-03)

### Dataset choice and structure

`canadian_weather_precip.csv` (365 rows = days, 35 columns = stations) — VERIFIED this session.
`[VERIFIED: runtime pd.read_csv shape=(365,35)]`

**FTS orientation (the critical question from CONTEXT.md):**
- Treat each STATION as one functional observation (a 365-point daily precipitation curve).
- Transpose: `Xfts = cw.T.values.astype(float64)` → shape **(35, 365)**.
- This means "time index" = stations (35), "curves" = 365-day daily profiles.
- `ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)` then forecasts 3 additional curves
  of shape (365,) each.

This is the only structurally valid FTS approach with this dataset (35 stations, not enough
for multi-year slicing as originally contemplated). 35 observations is shallow for FTS but
produces a demonstrable forecast; the narrative should state this clearly.

**Alternative:** `canadian_weather.csv` temperature (same shape, same approach) works
identically; precip (as specified by CONTEXT.md) is validated and preferred.

### Validated pipeline (EXECUTED this session — VERIFIED)

```python
# paper/code/gen_figures.py — _study3() function
import numpy as np
import pandas as pd
from paper_utils import data_path, fig, save_figure, FDARS_COLORS
import fdars

np.random.seed(42)

cw = pd.read_csv(data_path("canadian_weather_precip.csv"), index_col=0)
# shape: (365, 35) — days × stations
Xfts = cw.T.values.astype(np.float64)      # (35, 365) — stations × days
ARGd = np.arange(1, 366, dtype=np.float64)  # day 1..365

# GOTCHA: ftsm_forecast takes RAW DATA + ARGVALS, not a model object
# Signature: ftsm_forecast(data, argvals, h=1, ncomp=3)
fc = fdars.fts.ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)
# fc keys: ['forecast', 'h']
# fc["forecast"].shape: (3, 365)  fc["h"]: 3
# fc["forecast"][0, :5]: [1.802, 1.861, 1.826, 1.703, 1.702]  (rounded)

# For context: ftsm (model) for decomposition display
model = fdars.fts.ftsm(Xfts, ARGd, ncomp=3)
# model keys: ['mean', 'rotation', 'scores', 'fitted', 'weights', 'ncomp', 'ar_models']
# model["scores"].shape: (35, 3)
```

### Real output numbers (for narrative)

`[VERIFIED: fdars 0.12.0 runtime, executed this session]`

- `Xfts.shape: (35, 365)` — 35 station precipitation curves, 365 daily points each
- `ftsm_forecast`: `forecast.shape (3, 365)`, `h: 3`
- `forecast[0, :5]: [1.802, 1.861, 1.826, 1.703, 1.702]` (rounded to 3dp for determinism)
- `ftsm` model: `scores.shape (35, 3)`, 3 functional principal components extracted

### Figures to produce

**Figure `study3_fts_precip.pdf`** — suggested two-panel layout:
1. **Left panel:** the 35 observed station precipitation curves (grey) + FTS mean curve
   (`model["mean"]`, highlighted); demonstrates the functional structure.
2. **Right panel:** 3 forecast curves (`fc["forecast"][0]`, `[1]`, `[2]` — 3 steps ahead)
   alongside the observed mean; demonstrates what the forecast looks like.

**Determinism:** `np.random.seed(42)` at top (no stochastic calls in fts — it's deterministic
linear algebra + VAR fitting). Float output pinned via `np.round(..., 3)` in narrative; figures
only plot curves (no printed float values in figure titles/annotations except rounded).

---

## Study 4: sklearn Pipeline + GridSearchCV (CASE-04)

### Dataset choice

**Wine** (178 samples × 13 features, 3 classes) is the best choice for Study 4:
- Clean 3-class problem; all numeric features; 178 samples fit well for 5-fold CV.
- Wine.csv structure: `index_col=0` → index IS the class (1, 2, 3); subtract 1 for 0-indexed labels.
- `FPCATransformer` treats the 13 numeric features as a functional observation (a 13-point
  profile) — not a traditional FDA interpretation, but valid as "functional preprocessing" and
  a correct demonstration of the estimator layer.
- GridSearchCV over `n_components` shows the hyperparameter-tuning story cleanly.

Sonar was also tested but FPCKNNClassifier in a pipeline underperformed (0.467 mean accuracy,
worse than chance for Mine/Rock) — likely because the KNN step re-does its own FPCA internally on
already-transformed FPCA scores. Use wine + LDA as the primary study.

### Validated pipeline (EXECUTED this session — VERIFIED)

```python
# paper/code/gen_figures.py — _study4() function
import numpy as np
import pandas as pd
from paper_utils import data_path, fig, save_figure, FDARS_COLORS
import fdars
from fdars.sklearn._skeletons import FPCATransformer
from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import GridSearchCV, cross_val_score

np.random.seed(42)

wn = pd.read_csv(data_path("wine.csv"), index_col=0)
Xw = wn.values.astype(np.float64)                          # (178, 13)
yw = np.array(wn.index.tolist(), dtype=np.int64) - 1       # 0,1,2 (int64!)

pipe = Pipeline([
    ("fpca", FPCATransformer(n_components=3)),              # n_components, not ncomp
    ("lda", LinearDiscriminantAnalysis()),
])

param_grid = {"fpca__n_components": [2, 3, 5, 8]}
gs = GridSearchCV(pipe, param_grid, cv=5, scoring="accuracy", refit=True, n_jobs=1)
gs.fit(Xw, yw)
# REAL OUTPUT: best_params_ {'fpca__n_components': 8}  best_score_: 0.961
# cv_results_ mean_test_score: [0.697, 0.759, 0.916, 0.961]  (for ncomp = 2, 3, 5, 8)

# Refit CV to verify
cv = cross_val_score(gs.best_estimator_, Xw, yw, cv=5, scoring="accuracy")
# REAL OUTPUT: [0.917, 0.944, 0.972, 0.971, 1.0]  mean: 0.961
```

### Real output numbers (for narrative)

`[VERIFIED: fdars 0.12.0 runtime + sklearn, executed this session]`

- Dataset: 178 samples × 13 features, 3 wine classes (59/71/48 per class)
- GridSearchCV over `n_components ∈ {2, 3, 5, 8}`:
  - n_components=2: mean CV accuracy 0.697
  - n_components=3: mean CV accuracy 0.759
  - n_components=5: mean CV accuracy 0.916
  - n_components=8: mean CV accuracy **0.961** (best)
- **Best CV accuracy: 0.961 (96.1%)**
- Best estimator (n_components=8) 5-fold revalidation: `[0.917, 0.944, 0.972, 0.971, 1.000]`,
  mean 0.961

### Key gotcha: `FPCATransformer` vs `FPCLDAClassifier` parameter names

`[VERIFIED: runtime inspect.signature this session]`

| Estimator | Param | Note |
|-----------|-------|------|
| `FPCATransformer` | `n_components` (sklearn convention) | Used as Pipeline step for dimensionality reduction |
| `FPCLDAClassifier` | `ncomp` (fdars convention) | Built-in FPCA+LDA; ncomp ≠ n_components |
| `FPCKNNClassifier` | `ncomp` (fdars convention) | NOT n_components |
| `FPCRegressor` | `n_components` (sklearn convention) | default 10 |

For Study 4, use `FPCATransformer` (n_components) + sklearn `LinearDiscriminantAnalysis` —
this shows the composability story cleanly (fdars transformer + vanilla sklearn estimator).

### Figures to produce

**Figure `study4_wine_gridsearch.pdf`** — suggested two-panel layout:
1. **Left panel:** GridSearchCV mean CV accuracy vs n_components (bar or line chart);
   shows the hyperparameter-search story. Use `gs.cv_results_["mean_test_score"]`.
2. **Right panel:** FPCA scores scatter (PC1 vs PC2 of best estimator) colored by class;
   shows the separability achieved by the optimal n_components=8.

**Determinism:** `np.random.seed(42)` at top; `n_jobs=1` in GridSearchCV (prevents parallel
ordering variance); `random_state=42` in LogisticRegression if used (use LDA instead — no
random_state needed and avoids convergence warnings). `KFold` default is deterministic.

---

## Signature Reference Table (All VERIFIED this session)

`[VERIFIED: fdars 0.12.0 runtime, inspect.signature, executed calls]`

| Function | Signature | Keys returned |
|----------|-----------|---------------|
| `fdars.basis.smooth_basis_gcv` | `(data, argvals, n_basis, basis_type='bspline', ...)` | `fitted, coefficients, edf, gcv, aic, bic, nbasis` |
| `fdars.Fdata.to_pc` | `(n_comp=3)` — NOTE: `n_comp` not `n_components` | `scores, rotation, singular_values, mean, centered, weights` |
| `fdars.classification.fclassif_knn` | `(data, labels, ncomp=3, k=5)` — NO argvals | `predicted, accuracy` |
| `fdars.regression.fregre_lm` | `(data, response, n_comp=5)` | `fitted_values, residuals, beta_t, r_squared, coefficients, intercept` |
| `fdars.alignment.karcher_mean` | `(data, argvals, lambda_=0.0, max_iter=20, tol=1e-4)` | `mean, mean_srsf, aligned_data, gammas, n_iter, converged` |
| `fdars.alignment.align_to_target` | `(data, target, argvals, lambda_=0.0)` | `aligned_data, gammas, distances` |
| `fdars.fts.ftsm` | `(data, argvals, ncomp=3)` | `mean, rotation, scores, fitted, weights, ncomp, ar_models` |
| `fdars.fts.ftsm_forecast` | `(data, argvals, h=1, ncomp=3)` — RAW DATA, not model | `forecast (h, n_points), h` |
| `FPCATransformer.__init__` | `(self, argvals=None, n_components=3)` | sklearn transform |
| `FPCLDAClassifier.__init__` | `(self, argvals=None, ncomp=3)` | sklearn predict |
| `FPCKNNClassifier.__init__` | `(self, argvals=None, ncomp=3, k=3)` | sklearn predict |
| `FPCRegressor.__init__` | `(self, argvals=None, n_components=10)` | sklearn predict |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deterministic figure saving | Custom savefig | `paper_utils.save_figure` | Sets `metadata={"CreationDate": None}` |
| Agg backend + rcParams | Module-level `plt.rcParams` calls | Import `paper_utils` (re-exports `docs_fig` which sets Agg + rcParams) | Already proven; do NOT re-set backend after import |
| Data loading | Copy CSVs / hardcode paths | `data_path("name.csv")` | PIPE-01 lock; security validated (no traversal) |
| Figure function structure | Ad hoc scripts | Append `_study1()`, `_study2()`, etc. to `gen_figures.py main()` | Existing pattern; determinism gate rides this |
| Float printing for annotations | Raw `repr(float)` | `round(float(x), n)` or `np.round(arr, n)` | Platform-portable; avoids `0.9287153...789` vs `...788` |
| Random state in GridSearchCV | Let `n_jobs` default | `n_jobs=1` explicitly | Prevents parallel-ordering nondeterminism |

---

## Common Pitfalls

### Pitfall 1: Mixing `n_comp` and `n_components` across estimators
**What goes wrong:** `FPCLDAClassifier(n_components=4)` → `TypeError: unexpected keyword argument`.
**Why:** fdars estimators use two different conventions: `FPCATransformer` uses sklearn's
`n_components`, the native classifiers (`FPCLDAClassifier`, `FPCKNNClassifier`) use fdars's
`ncomp`. See Signature Reference Table.
**How to avoid:** Use the Signature Reference Table. Confirmed signatures via `inspect.signature`
this session.

### Pitfall 2: Pipeline with double-FPCA
**What goes wrong:** `Pipeline([("fpca", FPCATransformer(...)), ("knn", FPCKNNClassifier(...))])`
performs FPCA twice — `FPCKNNClassifier` does its own internal FPCA on the already-reduced
scores, leading to near-random accuracy (validated: 0.467 on sonar).
**Why:** `FPCKNNClassifier` internally calls `fclassif_knn` which does FPCA internally.
**How to avoid:** Either (a) use `FPCATransformer` + a pure sklearn estimator (validated:
`LinearDiscriminantAnalysis`), OR (b) use `FPCLDAClassifier` alone (without FPCATransformer
preceding it). For Study 4, use option (a): `FPCATransformer + LinearDiscriminantAnalysis`.

### Pitfall 3: `ftsm_forecast` takes raw data, not a model
**What goes wrong:** `fdars.fts.ftsm_forecast(model, ARGd, h=3)` → wrong result or error.
**Why:** `ftsm_forecast(data, argvals, h=1, ncomp=3)` refits internally; the `ftsm` model
dict is NOT the input.
**How to avoid:** Always pass `Xfts` (the raw data array) and `ARGd` directly.
Documented in 88-RESEARCH.md §8.

### Pitfall 4: `karcher_mean` reports `converged: False` — not an error
**What goes wrong:** Script checks `assert km["converged"]` → AssertionError.
**Why:** `converged: False` means `max_iter=20` was reached, not that the result is unusable.
The aligned curves are still valid for the figure and subsequent regression.
**How to avoid:** Do not assert `converged`; print it (informational). Use a small subset
(≤30 curves) for the karcher step in the figure to keep runtime acceptable.

### Pitfall 5: Wine class labels are 1-indexed
**What goes wrong:** `yw = np.array(wn.index.tolist(), dtype=np.int64)` gives labels 1,2,3 →
sklearn's `LinearDiscriminantAnalysis` works, but consistency is easier with 0-indexed.
**How to avoid:** Always subtract 1: `yw = np.array(wn.index.tolist(), dtype=np.int64) - 1`.
Both work; 0-indexed is the sklearn convention.

### Pitfall 6: `fregre_lm` key name is `fitted_values` (not `fitted`)
**What goes wrong:** `sof["fitted"]` → KeyError.
**Why:** `fregre_lm` returns `fitted_values`; `to_pc` returns `fitted` (different module).
**How to avoid:** Use `sof["fitted_values"]` for regression, `pc["scores"]` for FPCA.
Keys fully documented in the Signature Reference Table.

### Pitfall 7: GridSearchCV `n_jobs` default is 1 on some systems but not others
**What goes wrong:** On a multi-core CI machine, `n_jobs=-1` causes parallel-ordered CV splits
that may not be byte-identical to a single-core local run; the figure (if it plots per-fold
scores) shows different ordering.
**How to avoid:** Always set `n_jobs=1` explicitly in GridSearchCV. This also avoids
`loky`/`multiprocessing` backend nondeterminism.

---

## Determinism Pinning Summary

`[VERIFIED: all determinism claims confirmed by running scripts twice locally this session]`

| Study | Stochastic step | Pin via |
|-------|-----------------|---------|
| Study 1 | `np.random.seed` | `np.random.seed(42)` at top; no `random_state` needed (FPCATransformer + FPCLDAClassifier are deterministic) |
| Study 2 | None (iterative but deterministic) | `np.random.seed(42)` at top; `karcher_mean` and `fregre_lm` are pure linear algebra |
| Study 3 | None | `np.random.seed(42)` at top (ftsm is deterministic VAR fit); float rounding for annotations |
| Study 4 | None (LDA is deterministic) | `np.random.seed(42)` at top; `n_jobs=1` in `GridSearchCV` |

**Residual risk:** FreeType/font rendering variance across platforms (CI vs local) can cause
non-empty `git diff paper/figures/`. This is the known cross-platform determinism risk from
Phase 89 CONTEXT.md. The local gate (`git diff` empty on re-run same machine) is the Phase 89
requirement; cross-platform is Phase 90 CI gate.

---

## Figure Generation Integration

### Append to `gen_figures.py main()`

The executor appends four figure functions to `paper/code/gen_figures.py`:

```python
def _study1_phoneme() -> None:
    """Study 1: FPCA scores and smoothed spectra for phoneme data."""
    ...  # see §Study 1 validated pipeline

def _study2_tecator() -> None:
    """Study 2: registration and scalar-on-function regression on tecator."""
    ...  # see §Study 2 validated pipeline

def _study3_fts_precip() -> None:
    """Study 3: FTS forecast on Canadian weather precipitation."""
    ...  # see §Study 3 validated pipeline

def _study4_wine_gridsearch() -> None:
    """Study 4: sklearn Pipeline + GridSearchCV on wine."""
    ...  # see §Study 4 validated pipeline


def main() -> None:
    _smoke()                  # existing
    _study1_phoneme()
    _study2_tecator()
    _study3_fts_precip()
    _study4_wine_gridsearch()
```

Each function calls `_FIGURES_DIR.mkdir(parents=True, exist_ok=True)` and closes with
`save_figure(f, _FIGURES_DIR / "studyX_name.pdf")`.

### Figure names

| Study | Figure file | Description |
|-------|-------------|-------------|
| 1 | `study1_phoneme.pdf` | smoothed spectra + FPCA scores scatter |
| 2 | `study2_tecator.pdf` | aligned spectra + actual-vs-fitted scatter |
| 3 | `study3_fts_precip.pdf` | station curves + 3-step forecast |
| 4 | `study4_wine_gridsearch.pdf` | CV accuracy vs n_components + FPCA scores scatter |

### `casestudies.tex` structure

```latex
\section{Case Studies}
% Four subsections, each: problem framing + \includegraphics + caption + interpretation.
% Prefer \input{snippets/study1_snippet} for small shown code blocks (Phase 88 harness).
% All counts via macros (\nsubmodules etc.); no hardcoded integers.
% No benchmark/performance claims.

\subsection{Smoothing, FPCA, and Classification: Phoneme Data}
% Study 1 — phoneme, accuracy 88.2%

\subsection{Registration and Scalar-on-Function Regression: Tecator Data}
% Study 2 — tecator, training R² 0.9287, CV R² 0.805 mean

\subsection{Functional Time Series Forecasting: Canadian Weather Precipitation}
% Study 3 — canadian_weather_precip, 35 stations × 365 days → 3-step forecast

\subsection{Composable sklearn Pipelines: Wine Data}
% Study 4 — wine, best CV accuracy 0.961 at n_components=8
```

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| fdars 0.12.0 (compiled) | All studies | ✓ (.venv) | 0.12.0 | maturin develop |
| numpy | All studies | ✓ | (in .venv) | — |
| pandas | CSV reads | ✓ | (in .venv) | — |
| scikit-learn | Studies 1, 4 | ✓ | (in .venv) | add to paper.yml pip install (Phase 88) |
| matplotlib | Figures | ✓ | (in .venv) | — |
| paper_utils | Figures | ✓ (`paper/code/paper_utils.py`) | — | — |

**Missing dependencies with no fallback:** None. All are already in `.venv`.

---

## Validation Architecture

| Behavior | Test Type | Automated Command |
|----------|-----------|-------------------|
| Study figure scripts run without error | integration | `PYTHONPATH=scripts:paper/code python paper/code/gen_figures.py` |
| Figures unchanged on re-run | determinism gate | `git diff --exit-code paper/figures/` (existing gate, Phase 85) |
| Coverage macros current | drift gate | `python paper/code/assert_coverage.py --check` (existing) |

**Wave 0 gaps:** No new test infrastructure needed — the determinism gate already exists in
`make paper`/`paper.yml`. The figure functions are appended to the existing `gen_figures.py`.

---

## Security Domain

Not applicable — documentation + a local pipeline script. No ASVS categories apply.

---

## Package Legitimacy Audit

No new external packages. fdars, sklearn, pandas, numpy, matplotlib are existing deps.

| Package | Verdict | Note |
|---------|---------|------|
| fdars 0.12.0 | OK | project's own compiled package |
| scikit-learn | OK | existing dep (Phase 88 paper.yml already adds it) |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `karcher_mean(Xt[:30])` finishes in acceptable time for the CI figure step | §Study 2 | LOW — tested locally ~1-3 seconds; 30-curve subset chosen for speed |
| A2 | FreeType/font rendering is byte-identical between re-runs on the same machine | §Determinism Pinning | LOW — confirmed local re-run empty diff; cross-platform is Phase 90 |
| A3 | `FPCATransformer` + `LinearDiscriminantAnalysis` pipeline on wine.csv gives deterministic results | §Study 4 | LOW — verified locally twice same output |
| A4 | `ftsm_forecast` on 35 stations is a valid FTS demo (study is illustrative, not statistically optimal) | §Study 3 | LOW — 35 obs is thin for VAR fitting; narrative should describe the dataset size honestly |

**If this table is empty:** All claims were verified — no user confirmation needed. Table above lists LOW-risk items only.

---

## Open Questions

1. **Alignment figure for Study 2:** Show raw vs aligned spectra as overlaid line plots or as a
   difference (warp function / gammas)? Either is visually effective; executor's discretion.
2. **Precip vs temperature for Study 3:** Both datasets have the same shape and the same FTS
   approach validates. CONTEXT.md specifies precip (`canadian_weather_precip.csv`); use it.
3. **Snippet inclusion in casestudies.tex:** Should the executor add executed snippet fragments
   (Phase 88 pattern) for selected study code, or rely on `\includegraphics` + prose only?
   Recommendation: include one small snippet per study (the key call: `to_pc`, `fregre_lm`,
   `ftsm_forecast`, `GridSearchCV.fit`) via the Phase 88 `gen_snippets.py` harness.
   Executor's discretion.
4. **`karcher_mean converged: False` in narrative:** Should the narrative mention this? YES —
   briefly, honestly: "alignment iterations were limited to 20 for computational efficiency;
   convergence is not required for the registration to be illustrative."

---

## Sources

### Primary (HIGH confidence — all executed this session)

- fdars 0.12.0 imported in `.venv` this session; all 4 study pipelines RUN, outputs captured.
- `docs/data/phoneme.csv`, `tecator.csv`, `canadian_weather_precip.csv`, `wine.csv`, `sonar.csv` — shapes verified via `pd.read_csv`.
- `fdars.alignment`, `fdars.basis`, `fdars.regression`, `fdars.fts`, `fdars.Fdata.to_pc`, `fdars.classification.fclassif_knn` — signatures via `inspect.signature`.
- `fdars.sklearn._skeletons.FPCATransformer`, `FPCLDAClassifier`, `FPCKNNClassifier`, `FPCRegressor` — all signatures verified.
- Phase 88 RESEARCH.md — gotchas (int64 labels, contiguous float64, `ftsm_forecast` raw data, `FPCATransformer(n_components=)`).
- `paper/code/paper_utils.py`, `gen_figures.py` — read directly; pattern confirmed.

### Secondary (MEDIUM confidence)

- 88-RESEARCH.md §Dataset Suitability — shapes cross-referenced (all confirmed independently this session).

---

## Metadata

**Confidence breakdown:**
- Study 1 pipeline + numbers: HIGH — executed, output captured
- Study 2 pipeline + numbers: HIGH — executed, output captured; alignment converged=False documented
- Study 3 pipeline + numbers: HIGH — executed, output captured; dataset structure verified
- Study 4 pipeline + numbers: HIGH — executed, output captured; double-FPCA pitfall discovered and documented
- Determinism: HIGH — all studies have pinnable random state; residual FreeType risk documented
- Signature reference table: HIGH — all via `inspect.signature` or TypeError/AttributeError probing

**Research date:** 2026-09-09
**Valid until:** 2026-12-09 (re-check if fdars bumps past 0.12.0 — Phase 90 REL-01 bumps to 0.13.0)
