# Phase 71: Shapelets & GAK Metric - Research

**Researched:** 2026-09-04
**Domain:** PyO3 bindings — shapelet discovery/transform/classifier + Global Alignment Kernel
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **GAK train/predict API shape:** Opaque `PyGakGramTrain` handle. `gak_gram_train` returns a
  `PyGakGramTrain` opaque `#[pyclass]`; `gak_gram_predict(handle, new_data)` reuses it. This
  is pyfda's 4th opaque handle (after PyIrregFdata, PyMultiFunData, PyShapeletFit).
  `gak_gram_matrix` (one-shot symmetric full Gram) is ALSO bound.

### Claude's Discretion
- **PyShapeletFit handle:** opaque `#[pyclass]` wrapping `ShapeletTransformFit` (not raw
  `ShapeletSet`). `shapelet_transform_fit` returns it; `shapelet_transform(fit, data)` and
  `shapelet_classifier_fit` consume it. Mirror PyIrregFdata/PyMultiFunData template.
- **Enum string dispatch (mandatory Err arm):**
  - `QualityMeasure`: unit variants → `quality_from_str("info_gain"|"f_statistic")` with
    Err wildcard listing valid names.
  - `ShapeletClassifier`: data-carrying (`Knn { k: usize }`, `Lda`) → `classifier="knn",
    k=...` with Err wildcard listing valid classifier names.
- **Return shape:** PyDict per result struct; `shapelet_transform` returns 2D numpy; `gak` and
  `sigma_gak` return scalars; `gak_gram_matrix` / `gak_gram_predict` return 2D numpy.
- **Precomputed-kernel contract:** `gak_gram_matrix` → symmetric (n,n); `gak_gram_predict` →
  (n_test, n_train). Both directly usable with sklearn `metric="precomputed"`.
- **Transposition:** all 2D input via `numpy2d_to_fdmatrix`; non-square fixtures required.
- **Determinism:** `seed` default where `discover_shapelets` takes one (default 0).
- **Error handling:** `FdarError → PyValueError` via `convert::to_pyresult`; guard opaque-handle
  builders before the core constructor.

### Deferred Ideas (OUT OF SCOPE)
- Advisor extension for shapelet/GAK (ADV-01) — Phase 72.
- shapelet docs page with runnable offline example (DOCS-01) — Phase 73.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SHAPE-01 | New `fdars.shapelet` submodule — `discover_shapelets`, `shapelet_transform_fit` / `shapelet_transform`, `shapelet_classifier_fit`, `shapelet_distance` — with a `PyShapeletFit` opaque handle and the two new enums (`QualityMeasure`, `ShapeletClassifier`) dispatched by string with an `Err` fallback arm | Section 1: exact signatures, struct fields, enum variants; Section 3: dispatch patterns; Section 5: registration mechanics |
| SHAPE-02 | Global-Alignment-Kernel metric bound extending `fdars.metric` — `gak`, `gak_gram_matrix`, `gak_gram_train` / `gak_gram_predict`, `sigma_gak` — Gram output usable as a precomputed kernel | Section 2: exact signatures, GakConfig, GakGramTrain fields; Section 4: Gram shapes; Section 5: metric_mod.rs extension |
</phase_requirements>

---

## Summary

Phase 71 adds two independent pieces of code: a brand-new `src/shapelet_mod.rs` module
(SHAPE-01) and an extension to the existing `src/metric_mod.rs` (SHAPE-02). The shapelet
side introduces two new `#[non_exhaustive]` enums, one opaque handle (`PyShapeletFit`
wrapping `ShapeletTransformFit`), and five bound functions. The GAK side introduces a second
opaque handle (`PyGakGramTrain` wrapping `GakGramTrain`) and five bound functions extending
the metric module, plus a `#[pyclass]` registration inside `metric_mod.rs`.

All upstream types and functions have been read verbatim from the 0.33 registry source; every
claim in this document is `[VERIFIED]` against those sources. The binding mechanics are
identical to the Phase 69/70 patterns already established — the primary planning risk is the
`ShapeletClassifier::Lda` variant (unit variant, no parameters; distinct from `Knn { k }`)
and the `pub(crate)` fields on `GakGramTrain` that cannot be read directly from Python.

**Primary recommendation:** Follow the PyIrregFdata template exactly for both opaque handles;
copy the `penalty_from_str` pattern from `scalar_on_function_mod.rs` for both enum dispatchers;
note that `PyShapeletFit` wraps `ShapeletTransformFit` (not `ShapeletSet`), which carries
both the shapelet set and the training feature matrix.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Shapelet discovery | API/Backend (Rust binding) | — | Pure computation; no Python layer needed |
| Shapelet transform (fit) | API/Backend (Rust binding, opaque handle) | — | Handle lifetime managed by Python GC |
| Shapelet transform (apply) | API/Backend (Rust binding) | — | Takes opaque handle + raw data |
| Shapelet classifier fit | API/Backend (Rust binding) | — | End-to-end; returns prediction accessor |
| Shapelet distance | API/Backend (Rust binding) | — | Takes two 1D slices, returns scalar pair |
| GAK pairwise kernel | API/Backend (Rust binding) | — | `gak(x,y,sigma)` on 1D slices |
| GAK gram (one-shot) | API/Backend (Rust binding) | — | Symmetric (n,n) PSD matrix |
| GAK gram (train/predict) | API/Backend (Rust binding, opaque handle) | sklearn interop | Precomputed-kernel split workflow |
| Sigma heuristic | API/Backend (Rust binding) | — | Returns scalar; no handle needed |

---

## Standard Stack

No new external dependencies. All code uses the established pyfda dependency set:

| Library | Version | Purpose |
|---------|---------|---------|
| `fdars-core` | 0.33.0 | Provides all shapelet + GAK algorithms |
| `pyo3` | 0.28 | `#[pyclass]`, `#[pyfunction]`, `#[pymethods]` |
| `numpy` (pyo3-numpy) | 0.28 | `PyReadonlyArray1/2`, `vec_to_numpy1d`, `fdmatrix_to_numpy2d` |

**Installation:** none — no new Cargo.toml entries.

---

## Package Legitimacy Audit

Not applicable — no new external packages are installed in this phase.

---

## Architecture Patterns

### Recommended Project Structure

```
src/
├── shapelet_mod.rs      # NEW — PyShapeletFit #[pyclass] + 5 #[pyfunction]s
├── metric_mod.rs        # EXTEND — add PyGakGramTrain #[pyclass] + 5 GAK #[pyfunction]s
├── lib.rs               # EXTEND — add `mod shapelet_mod;` + `register_submodule!(m, "shapelet", ...)`
python/fdars/
├── __init__.py          # EXTEND — add "shapelet" to _submodule_names tuple
tests/
├── test_shapelet.py     # NEW — SHAPE-01 tests
├── test_gak.py          # NEW — SHAPE-02 tests
```

### System Architecture Diagram

```
Python caller
     │
     ├── fdars.shapelet.discover_shapelets(data, labels, ...)
     │         → ndarray (n, m)  → numpy2d_to_fdmatrix → discover_shapelets → ShapeletSet
     │                                                                          (inside ShapeletTransformFit)
     │
     ├── fdars.shapelet.shapelet_transform_fit(data, labels, ...) → PyShapeletFit (opaque)
     │         ↳ wraps ShapeletTransformFit { shapelets: ShapeletSet, features: FdMatrix }
     │
     ├── fdars.shapelet.shapelet_transform(fit: PyShapeletFit, data) → ndarray (n, K)
     │
     ├── fdars.shapelet.shapelet_classifier_fit(fit: PyShapeletFit, labels, ...) → PyDict
     │         ↳ discover+transform+inner-classifier; returns labels/accuracy/classes PyDict
     │
     ├── fdars.shapelet.shapelet_distance(shapelet, series) → (float, int)
     │
     ├── fdars.metric.gak(x, y, sigma) → float  [scalar]
     ├── fdars.metric.sigma_gak(data) → float   [scalar]
     ├── fdars.metric.gak_gram_matrix(data, sigma=None) → ndarray (n, n)  [symmetric PSD]
     ├── fdars.metric.gak_gram_train(data, sigma=None) → PyGakGramTrain (opaque)
     │         ↳ wraps GakGramTrain { gram: FdMatrix, log_self: Vec<f64> [pub(crate)],
     │                                sigma: f64, train_rows: Vec<Vec<f64>> [pub(crate)] }
     │         ↳ exposes: .gram → ndarray (n, n);  .sigma → float;  .n_train → int
     └── fdars.metric.gak_gram_predict(train: PyGakGramTrain, new_data) → ndarray (n_test, n_train)
```

---

## Section 1 — SHAPE-01: Shapelet Functions & PyShapeletFit Handle

### 1.1 Exact Function Signatures (fdars-core 0.33.0)

All signatures verified against the 0.33 registry source. Line numbers cited are the `pub fn`
declaration lines.

**`discover_shapelets`**
[VERIFIED: shapelet/discovery.rs:399-403]
```rust
pub fn discover_shapelets(
    data: &FdMatrix,
    labels: &[usize],
    config: &ShapeletDiscoveryConfig,
) -> Result<ShapeletSet, FdarError>
```
- `data`: column-major FdMatrix, rows = curves, cols = evaluation points
- `labels`: integer class per curve; must have ≥2 distinct values; `0`-based but any usize works (internally remapped)
- `config`: `ShapeletDiscoveryConfig` (see §1.4)
- Returns: `ShapeletSet` — the fitted state for `shapelet_transform`

**`shapelet_transform_fit`**
[VERIFIED: shapelet/transform.rs:242-246]
```rust
pub fn shapelet_transform_fit(
    data: &FdMatrix,
    labels: &[usize],
    config: &ShapeletDiscoveryConfig,
) -> Result<ShapeletTransformFit, FdarError>
```
- Returns: `ShapeletTransformFit` — THIS is what `PyShapeletFit` wraps (not `ShapeletSet` alone)
- Internally calls `discover_shapelets` then `shapelet_transform` on the training data
- `ShapeletTransformFit` holds both the shapelet set AND the training (n×K) feature matrix

**`shapelet_transform`**
[VERIFIED: shapelet/transform.rs:96-97]
```rust
pub fn shapelet_transform(shapelets: &ShapeletSet, data: &FdMatrix) -> Result<FdMatrix, FdarError>
```
- Takes `&ShapeletSet` (not `ShapeletTransformFit`); call `.shapelets()` on the handle
- Returns FdMatrix of shape (n, K) where K = number of shapelets discovered
- **Binding note:** the Python function signature should be `shapelet_transform(fit, data)` where `fit` is `&PyShapeletFit`; inside, call `fit.inner.shapelets()` to get `&ShapeletSet`

**`shapelet_classifier_fit`**
[VERIFIED: shapelet/classifier.rs:238-242]
```rust
pub fn shapelet_classifier_fit(
    data: &FdMatrix,
    labels: &[usize],
    config: &ShapeletClassifierConfig,
) -> Result<ShapeletClassifierFit, FdarError>
```
- Returns `ShapeletClassifierFit` — NOT an opaque handle; the binding converts it to a PyDict
- Takes raw data + labels, NOT `PyShapeletFit` — it runs full discovery+transform+classify internally
- **Binding design:** accepts `PyShapeletFit`-LESS path — takes numpy array directly, builds `ShapeletClassifierConfig` from string dispatch

**`shapelet_distance`**
[VERIFIED: shapelet/distance.rs:246-250]
```rust
pub fn shapelet_distance(
    shapelet_z: &[f64],
    series: &[f64],
    best_so_far: f64,
) -> Result<(f64, usize), FdarError>
```
- `shapelet_z`: pre-z-normalized shapelet values (1D slice)
- `series`: raw series (1D slice; per-window z-normalization happens inside)
- `best_so_far`: early-abandon bound; pass `f64::INFINITY` to disable
- Returns `(min_distance, best_offset)` — best_offset is the start index of the best-matching window
- **Binding:** takes two `PyReadonlyArray1<f64>`, optional `best_so_far=f64::INFINITY`, returns Python tuple `(float, int)`

### 1.2 PyShapeletFit Opaque Handle

**What it wraps:** `fdars_core::shapelet::ShapeletTransformFit`

[VERIFIED: shapelet/transform.rs:152-157]
```rust
#[non_exhaustive]
pub struct ShapeletTransformFit {
    pub shapelets: ShapeletSet,   // discovered, z-normalized set (ordered by quality desc)
    pub features: FdMatrix,       // training n×K feature matrix (columns = shapelet distances)
}
```

`ShapeletTransformFit` exposes:
- `.shapelets()` → `&ShapeletSet`
- `.features()` → `&FdMatrix` (shape: n_train × K)
- `.transform(new_data: &FdMatrix)` → `Result<FdMatrix, FdarError>` (n_new × K)

**Handle structure:**
```rust
#[pyclass(name = "PyShapeletFit")]
pub struct PyShapeletFit {
    pub inner: fdars_core::shapelet::ShapeletTransformFit,
}
```

**Accessors to expose via `#[pymethods]`:**
- `n_shapelets() -> usize` → `self.inner.shapelets().len()`
- `n_train() -> usize` → `self.inner.features().nrows()`

**ShapeletSet fields** (inside `inner.shapelets`):
[VERIFIED: shapelet/discovery.rs:88-93]
```rust
#[non_exhaustive]
pub struct ShapeletSet {
    pub shapelets: Vec<Shapelet>,   // ordered by quality descending
    pub quality: QualityMeasure,    // the measure used during scoring
}
```

`ShapeletSet` methods:
- `.len()` → usize
- `.is_empty()` → bool
- `.shapelets()` → `&[Shapelet]`
- `.quality()` → `QualityMeasure`

**Shapelet fields** (individual shapelet, `#[non_exhaustive]`):
[VERIFIED: shapelet/distance.rs:131-142]
```rust
#[non_exhaustive]
pub struct Shapelet {
    pub values: Vec<f64>,      // z-normalized subsequence values
    pub series_idx: usize,     // index of source training series
    pub start: usize,          // start offset within source series
    pub length: usize,         // length L of the subsequence
    pub quality: f64,          // discriminative quality score (higher = better)
}
```

### 1.3 ShapeletClassifierFit — PyDict Return (NOT an opaque handle)

`shapelet_classifier_fit` returns `ShapeletClassifierFit`. The binding converts this to a
Python dict. Do NOT wrap it in a `#[pyclass]` handle — the classifier result is consumed
once, not reused across calls.

[VERIFIED: shapelet/classifier.rs:84-95]
```rust
#[non_exhaustive]
pub struct ShapeletClassifierFit {
    pub transform: ShapeletTransformFit,    // fitted shapelet transform + training features
    pub classifier: ClassifFit,             // inner classifier (knn or lda) on K features
    pub config: ShapeletClassifierConfig,   // config used
    pub classes: Vec<usize>,               // sorted-unique original labels (index → caller's label)
}
```

**`ShapeletClassifierFit` methods the binding uses:**
- `.train_accuracy()` → `f64` (training-set accuracy; NOT a generalization estimate)
- `.shapelets()` → `&ShapeletSet`
- `.predict(new_data: &FdMatrix)` → `Result<Vec<usize>, FdarError>`

**PyDict keys for `shapelet_classifier_fit` return:**
| Key | Type | Notes |
|-----|------|-------|
| `n_shapelets` | int | `result.shapelets().len()` |
| `train_accuracy` | float | `result.train_accuracy()` (training only, not generalization) |
| `classes` | 1D array (int64) | `result.classes` — caller's original label → class index mapping |
| `n_classes` | int | `result.classes.len()` |

**Prediction:** expose a separate `shapelet_classifier_predict(fit_dict, new_data)` function
OR, simpler, make `shapelet_classifier_fit` return a `PyShapeletClassifier` opaque handle
(preferred: mirrors Phase 70 pattern). See §3 for the recommended design.

**DECISION GAP — escalate to planner:** The CONTEXT.md says `shapelet_classifier_fit`
consumes the `PyShapeletFit` handle, but the upstream signature takes raw `data + labels +
ShapeletClassifierConfig` — it runs discovery internally, independent of a pre-fitted
`PyShapeletFit`. The binding must choose one of:
1. **Independent path (recommended):** `shapelet_classifier_fit(data, labels, ...)` — same as
   upstream; does not consume `PyShapeletFit`. `PyShapeletFit` is only for the
   `shapelet_transform_fit → shapelet_transform` two-step.
2. **Bridging path:** Accept `PyShapeletFit` + labels and re-discover using its config.
   This is non-idiomatic and requires storing config in the handle.

**Recommend option 1** — matches upstream semantics exactly. The CONTEXT.md note about
"consuming the handle" likely refers to the `shapelet_transform(fit, data)` call, not the
classifier.

### 1.4 ShapeletDiscoveryConfig — All Fields and Defaults

[VERIFIED: shapelet/discovery.rs:51-79]
```rust
pub struct ShapeletDiscoveryConfig {
    pub min_length: usize,              // default: 3
    pub max_length: usize,              // default: 0 (sentinel → ncols at fit time)
    pub max_candidates: Option<usize>,  // default: Some(10_000)
    pub max_shapelets: usize,           // default: 0 (sentinel → min(10*n, 1000))
    pub quality: QualityMeasure,        // default: QualityMeasure::InfoGain
    pub seed: u64,                      // default: 0
}
```

**Sentinel values:**
- `max_length = 0` → resolved to `ncols` (series length) at fit time
- `max_shapelets = 0` → resolved to `min(10 * n_train, 1000)` at fit time
- `max_candidates = None` → exhaustive enumeration (no cap)

**NOT `#[non_exhaustive]`** (verified: no `#[non_exhaustive]` attribute on this struct, only
the annotation on lines 88-89 which belongs to `ShapeletSet`). Safe to use struct-update
syntax: `ShapeletDiscoveryConfig { max_shapelets: 5, ..Default::default() }`.

**Python binding signature for `discover_shapelets` / `shapelet_transform_fit`:**
```rust
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0))]
```
- `max_candidates=0` → map to `None` in the config (disable cap, exhaustive) OR use
  `max_candidates=10000` as the default and `0` as the "exhaustive" sentinel — recommend
  using `Option<usize>` internally with `None` when caller passes `0`.
- `quality`: string → `QualityMeasure` via `quality_from_str` (see §3)

### 1.5 ShapeletClassifierConfig

[VERIFIED: shapelet/classifier.rs:61-74]
```rust
#[derive(Default)]
pub struct ShapeletClassifierConfig {
    pub discovery: ShapeletDiscoveryConfig,   // length range, candidate cap, K, seed
    pub classifier: ShapeletClassifier,       // default: Knn { k: 1 }
    pub ncomp: Option<usize>,                 // default: None (= K, full rank)
}
```

**Python binding signature for `shapelet_classifier_fit`:**
```rust
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0,
                    classifier="knn", k=1, ncomp=None))]
```

---

## Section 2 — SHAPE-02: GAK Functions & PyGakGramTrain Handle

### 2.1 Exact Function Signatures (fdars-core 0.33.0)

**`gak`**
[VERIFIED: metric/gak.rs:155-163]
```rust
pub fn gak(x: &[f64], y: &[f64], sigma: f64) -> f64
```
- Takes two 1D slices (NOT FdMatrix)
- Returns normalized TGAK similarity in `[0, 1]`; `gak(x, x, σ) == 1.0` exactly
- Returns `0.0` (not error) if `sigma <= 0` or either series is empty
- **Binding:** two `PyReadonlyArray1<f64>` + `sigma: f64` (required, no default — caller must
  supply or use `sigma_gak` first). Returns Python float.

**`sigma_gak`**
[VERIFIED: metric/gak.rs:191-221]
```rust
pub fn sigma_gak(data: &FdMatrix) -> f64
```
- Takes FdMatrix (rows = curves)
- Returns median pairwise Euclidean distance, floored at `1e-8`; ALWAYS returns `> 0`
- Returns `max(1e-8, 1.0)` = 1.0 if fewer than 2 curves or 0 evaluation points
- This is a plain `f64` return — infallible (no `Result`)
- **Binding:** `PyReadonlyArray2<f64>` → `numpy2d_to_fdmatrix` → `sigma_gak` → Python float

**`gak_gram_matrix`**
[VERIFIED: metric/gak.rs:255-258]
```rust
pub fn gak_gram_matrix(data: &FdMatrix, config: &GakConfig) -> Result<FdMatrix, FdarError>
```
- Returns symmetric (n, n) PSD Gram with unit diagonal; symmetric by assignment (bit-exact)
- `config.sigma = None` → auto-selected via `sigma_gak`
- **Binding:** `(data: PyReadonlyArray2<f64>, sigma: Option<f64> = None)` → `GakConfig { sigma }` → returns `fdmatrix_to_numpy2d`
- Shape: always `(n, n)` where n = data.nrows()

**`gak_gram_train`**
[VERIFIED: metric/gak.rs:414-422]
```rust
pub fn gak_gram_train(data: &FdMatrix, config: &GakConfig) -> Result<GakGramTrain, FdarError>
```
- Returns `GakGramTrain` — THIS is what `PyGakGramTrain` wraps
- The returned `gram` field is the (n_train, n_train) Gram directly usable as sklearn train kernel
- `sigma` field records the resolved bandwidth (whether from config or heuristic)

**`gak_gram_predict`**
[VERIFIED: metric/gak.rs:458-531]
```rust
pub fn gak_gram_predict(train: &GakGramTrain, new_data: &FdMatrix) -> Result<FdMatrix, FdarError>
```
- Takes `&GakGramTrain` + new_data
- Returns FdMatrix of shape **(n_test, n_train)** — rows = test curves, cols = training curves
- Uses `train.sigma` (stored bandwidth) and `train.log_self` (stored training diagonals)
- **Critical:** `new_data.ncols()` must equal the training evaluation-grid width or error

### 2.2 GakConfig — Fields and Non-exhaustive Status

[VERIFIED: metric/gak.rs:52-56]
```rust
#[non_exhaustive]
pub struct GakConfig {
    pub sigma: Option<f64>,   // None → auto via sigma_gak; Some(s) → use s (must be > 0)
}
```
- IS `#[non_exhaustive]` — use struct-update syntax NOT available from outside the crate
- Construct with `GakConfig { sigma: Some(s) }` (works because `sigma` is `pub`) or via
  `GakConfig::with_sigma(s)` (pub constructor) or `GakConfig::default()` (sigma = None)
- **Binding:** build from `sigma: Option<f64>` param: `GakConfig { sigma }`

### 2.3 GakGramTrain — Fields and PyGakGramTrain Handle

[VERIFIED: metric/gak.rs:349-373]
```rust
#[non_exhaustive]
pub struct GakGramTrain {
    pub gram: FdMatrix,               // n_train × n_train, PSD, unit diagonal, symmetric
    pub(crate) log_self: Vec<f64>,    // NOT accessible from pyfda (pub(crate))
    pub sigma: f64,                   // resolved bandwidth (> 0); accessible
    pub(crate) train_rows: Vec<Vec<f64>>, // NOT accessible (pub(crate))
}
```

**Critical:** `log_self` and `train_rows` are `pub(crate)` — they are accessible FROM
`gak_gram_predict` in fdars-core because that function lives in the same crate, but NOT from
pyfda code. The `PyGakGramTrain` handle wraps the whole `GakGramTrain` struct (including these
private fields); `gak_gram_predict` in fdars-core accesses them directly when given `&GakGramTrain`.

Public accessor exposed on `GakGramTrain`:
- `GakGramTrain::log_self()` → `&[f64]` (the pub accessor, not the field directly) — but
  this is not needed from Python

**Handle structure:**
```rust
#[pyclass(name = "PyGakGramTrain")]
pub struct PyGakGramTrain {
    pub inner: fdars_core::metric::gak::GakGramTrain,
}
```

**Accessors to expose via `#[pymethods]`:**
- `gram() -> PyResult<Bound<'py, PyArray2<f64>>>` — returns `fdmatrix_to_numpy2d(py, &self.inner.gram)`
- `sigma() -> f64` — returns `self.inner.sigma`
- `n_train() -> usize` — returns `self.inner.gram.nrows()`

**Import path for the type:** `fdars_core::metric::gak::GakGramTrain` — note `gak` is a
submodule of `metric`. Check if it is re-exported at `fdars_core::metric::GakGramTrain` or
needs the full path.

### 2.4 Gram Shape Contract (confirmed)

[VERIFIED: metric/gak.rs:793-836 (test_gram_predict_shape + test_gram_train_shape_psd)]
- `gak_gram_matrix` → shape `(n, n)` symmetric PSD, unit diagonal
- `gak_gram_train` → `.gram` shape `(n_train, n_train)`
- `gak_gram_predict` → shape `(n_test, n_train)` — rows = test, cols = training
- **sklearn precomputed-kernel contract:** pass `fit.gram` to `SVC(kernel='precomputed').fit(K, y)`; pass predict result directly to `.predict(K_test)` where `K_test.shape == (n_test, n_train)`
- Column-major note: `fdmatrix_to_numpy2d` already handles the column-major → row-major reshape. No extra transposition needed.

---

## Section 3 — Enum String Dispatch

### 3.1 QualityMeasure — Complete Variant Set

[VERIFIED: shapelet/discovery.rs:33-41]
```rust
#[non_exhaustive]
pub enum QualityMeasure {
    #[default]
    InfoGain,      // information gain on optimal distance-split threshold (Ye/Keogh)
    FStatistic,    // one-way ANOVA F-statistic grouped by label
}
```

**Exactly 2 variants.** The enum IS `#[non_exhaustive]` — wildcard arm is mandatory in all
match expressions.

**String → enum dispatch function:**
```rust
fn quality_from_str(s: &str) -> PyResult<fdars_core::shapelet::QualityMeasure> {
    use fdars_core::shapelet::QualityMeasure;
    match s {
        "info_gain" => Ok(QualityMeasure::InfoGain),
        "f_statistic" => Ok(QualityMeasure::FStatistic),
        _ => Err(PyValueError::new_err(format!(
            "quality must be 'info_gain' or 'f_statistic', got '{s}'"
        ))),
    }
}
```

### 3.2 ShapeletClassifier — Complete Variant Set

[VERIFIED: shapelet/classifier.rs:41-52]
```rust
#[non_exhaustive]
pub enum ShapeletClassifier {
    Knn { k: usize },   // k-nearest-neighbors; default k=1
    Lda,                // linear discriminant analysis (unit variant — no parameters)
}
// Default: Knn { k: 1 }
```

**Exactly 2 variants.** IS `#[non_exhaustive]` — wildcard arm mandatory. `Lda` is a unit
variant (no associated data). There is NO SVM, linear, or other variant.

**String → enum dispatch function:**
```rust
fn classifier_from_str(classifier: &str, k: usize) -> PyResult<fdars_core::shapelet::ShapeletClassifier> {
    use fdars_core::shapelet::ShapeletClassifier;
    match classifier {
        "knn" => Ok(ShapeletClassifier::Knn { k }),
        "lda" => Ok(ShapeletClassifier::Lda),
        _ => Err(PyValueError::new_err(format!(
            "classifier must be 'knn' or 'lda', got '{classifier}'"
        ))),
    }
}
```

**Python binding parameter convention for `shapelet_classifier_fit`:**
```
classifier: str = "knn"   # "knn" or "lda"
k: usize = 1              # only used when classifier="knn"; ignored for "lda"
```

---

## Section 4 — Verified Binding Signatures

Complete binding signatures for every function. All upstream types verified in §1 and §2.

### 4.1 shapelet_mod.rs — All Functions

```rust
// discover_shapelets → ShapeletSet (used internally; also bound standalone)
#[pyfunction]
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0))]
pub fn discover_shapelets<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,  // i64 from Python; cast to usize internally
    min_length: usize,
    max_length: usize,
    max_candidates: usize,  // 0 = exhaustive (maps to None in config)
    max_shapelets: usize,
    quality: &str,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>>
// Returns dict with keys: n_shapelets (int), quality (str)
// Note: ShapeletSet cannot be returned directly — convert to summary dict OR return PyShapeletFit

// shapelet_transform_fit → PyShapeletFit (opaque handle)
#[pyfunction]
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0))]
pub fn shapelet_transform_fit<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    ...
) -> PyResult<Py<PyShapeletFit>>  // returns opaque handle

// shapelet_transform → 2D numpy (n_new, K)
#[pyfunction]
pub fn shapelet_transform<'py>(
    py: Python<'py>,
    fit: &PyShapeletFit,                // borrows the opaque handle
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>>

// shapelet_classifier_fit → PyDict
#[pyfunction]
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0,
                    classifier="knn", k=1, ncomp=None))]
pub fn shapelet_classifier_fit<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    ...
    ncomp: Option<usize>,
) -> PyResult<Bound<'py, PyDict>>
// Dict keys: n_shapelets (int), train_accuracy (float), classes (1D int64 array), n_classes (int)
// NOTE: predict is NOT exposed in this dict — caller must re-fit for prediction,
//       OR expose shapelet_classifier_predict(fit_handle, new_data) as separate function.

// shapelet_distance → (float, int) tuple
#[pyfunction]
#[pyo3(signature = (shapelet_z, series, best_so_far=f64::INFINITY))]
pub fn shapelet_distance<'py>(
    py: Python<'py>,
    shapelet_z: PyReadonlyArray1<'py, f64>,
    series: PyReadonlyArray1<'py, f64>,
    best_so_far: f64,
) -> PyResult<(f64, usize)>  // Python tuple (float, int)
```

**Label type note:** Upstream uses `&[usize]` for labels. Python callers typically pass integer
numpy arrays. Use `PyReadonlyArray1<'py, i64>` and cast each element to `usize` inside the
binding (matches the pattern in `frechet_mod.rs::frechet_anova`). Guard for negative values.

### 4.2 metric_mod.rs — GAK Extension

```rust
// gak → float scalar
#[pyfunction]
pub fn gak<'py>(
    _py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    sigma: f64,
) -> PyResult<f64>
// Returns Python float; no Result wrapping needed (gak is infallible in 0.33)

// sigma_gak → float scalar
#[pyfunction]
pub fn sigma_gak<'py>(
    _py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<f64>
// Returns Python float; sigma_gak is infallible (always returns > 0)

// gak_gram_matrix → 2D numpy (n, n)
#[pyfunction]
#[pyo3(signature = (data, sigma=None))]
pub fn gak_gram_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    sigma: Option<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>>

// gak_gram_train → PyGakGramTrain opaque handle
#[pyfunction]
#[pyo3(signature = (data, sigma=None))]
pub fn gak_gram_train<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    sigma: Option<f64>,
) -> PyResult<Py<PyGakGramTrain>>

// gak_gram_predict → 2D numpy (n_test, n_train)
#[pyfunction]
pub fn gak_gram_predict<'py>(
    py: Python<'py>,
    train: &PyGakGramTrain,
    new_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>>
```

---

## Section 5 — Registration Mechanics

### 5.1 New src/shapelet_mod.rs

[VERIFIED: src/lib.rs:38-44 — register_submodule! macro template]

```rust
// In lib.rs — add two lines:
mod shapelet_mod;
// ...
register_submodule!(m, "shapelet", shapelet_mod::register);
```

`shapelet_mod::register` must call:
```rust
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyShapeletFit>()?;
    m.add_function(wrap_pyfunction!(discover_shapelets, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_transform_fit, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_transform, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_classifier_fit, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_distance, m)?)?;
    Ok(())
}
```

### 5.2 Extend src/metric_mod.rs

Add `PyGakGramTrain` `#[pyclass]` definition + `#[pymethods]` impl, and five new
`#[pyfunction]`s. Extend the existing `register` function at the bottom of `metric_mod.rs`:

```rust
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // ... existing registrations (int_simpson, inprod, lp_*, hausdorff_*, dtw_*, etc.) ...
    m.add_class::<PyGakGramTrain>()?;
    m.add_function(wrap_pyfunction!(gak, m)?)?;
    m.add_function(wrap_pyfunction!(sigma_gak, m)?)?;
    m.add_function(wrap_pyfunction!(gak_gram_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(gak_gram_train, m)?)?;
    m.add_function(wrap_pyfunction!(gak_gram_predict, m)?)?;
    Ok(())
}
```

### 5.3 python/fdars/__init__.py

[VERIFIED: python/fdars/__init__.py:40-67 — _submodule_names tuple]

Add `"shapelet"` to `_submodule_names`. The `metric` submodule is already registered (line 43);
only `shapelet` is new. Insert after `"famm"` (last entry):

```python
_submodule_names = (
    # ... existing names ...
    "famm",     # Phase 70
    "shapelet", # Phase 71 — Shapelets: discovery, transform, classifier
)
```

**FND-02 guard:** The test at `tests/sklearn/test_foundation.py` parses `_submodule_names`
from git source (HEAD baseline = Phase-55 names) and asserts the current set is a superset.
Adding `"shapelet"` satisfies the superset invariant. The test does NOT check for `metric`
additions (extends existing module, not a new submodule name).

### 5.4 fdars-core Import Paths

Verify these import paths compile (all confirmed in shapelet/mod.rs and metric/gak.rs):

```rust
// Shapelet types
use fdars_core::shapelet::{
    discover_shapelets, shapelet_transform, shapelet_transform_fit,
    shapelet_classifier_fit,
    QualityMeasure, ShapeletDiscoveryConfig, ShapeletSet,
    ShapeletClassifier, ShapeletClassifierConfig, ShapeletClassifierFit,
    ShapeletTransformFit,
    shapelet_distance,
};

// GAK types
use fdars_core::metric::gak::{gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict, GakConfig, GakGramTrain};
// OR if re-exported at crate root:
use fdars_core::{gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict, GakConfig};
```

Check the fdars-core crate root re-exports to confirm the short path:
[VERIFIED: shapelet/mod.rs:31-36 — all shapelet types re-exported at `fdars_core::shapelet::*`]
GAK path needs verification against `fdars_core/src/lib.rs` or `fdars_core/src/metric/mod.rs`.

---

## Section 6 — Fixtures

### 6.1 Shapelet Fixtures (SHAPE-01)

Non-square data (n_obs ≠ n_points) is required to catch transposition bugs:

```python
# tests/test_shapelet.py
import numpy as np
RNG = np.random.default_rng(42)

# Labeled 2-class dataset: n_obs=20, n_points=30 (non-square)
N_OBS, N_PTS = 20, 30
DATA = np.zeros((N_OBS, N_PTS))
LABELS = np.zeros(N_OBS, dtype=np.int64)
for i in range(N_OBS):
    is_class1 = i % 2 == 1
    LABELS[i] = int(is_class1)
    DATA[i] = 0.01 * i + np.arange(N_PTS) * 0.001 + RNG.standard_normal(N_PTS) * 0.05
    if is_class1:
        mid = N_PTS // 2
        DATA[i, mid:mid+6] += np.array([1,2,3,3,2,1])  # triangular motif

# Train/test split (different row counts — catches transpose)
TRAIN, TRAIN_Y = DATA[:16], LABELS[:16]
TEST, TEST_Y = DATA[16:], LABELS[16:]   # n_test=4 ≠ n_train=16

# Two 1D series for gak()
X1 = np.array([0.0, 1.0, 2.0, 3.0, 2.0, 1.0])
X2 = np.array([0.0, 0.5, 1.0, 2.0, 1.5, 0.5])
```

### 6.2 GAK Fixtures (SHAPE-02)

```python
# tests/test_gak.py
import numpy as np
RNG = np.random.default_rng(7)

# Non-square Gram fixture: n_train=8, n_points=25 (8≠25)
N_TRAIN, N_PTS = 8, 25
TRAIN_MAT = RNG.standard_normal((N_TRAIN, N_PTS))

# Test set: n_test=3 ≠ n_train=8 (non-square Gram)
N_TEST = 3
TEST_MAT = RNG.standard_normal((N_TEST, N_PTS))

# Two 1D series for pairwise gak()
X = np.array([0.0, 1.0, 2.0, 3.0])
Y = np.array([0.0, 1.0, 2.0, 3.0])  # identical → gak should be ≈ 1.0

# Self-similarity reference
Z = np.array([3.0, 2.0, 1.0, 0.0])
```

**Key shape-contract tests:**
- `gak_gram_matrix(TRAIN_MAT)` → shape `(8, 8)`, diagonal all 1.0, symmetric
- `fit = gak_gram_train(TRAIN_MAT)`; `fit.gram` → shape `(8, 8)`, `fit.sigma > 0`, `fit.n_train == 8`
- `gak_gram_predict(fit, TEST_MAT)` → shape `(3, 8)` — verify `n_test ≠ n_train` both before and after

---

## Section 7 — Common Pitfalls

### Pitfall 1: Confusing PyShapeletFit's inner type
**What goes wrong:** Wrapping `ShapeletSet` instead of `ShapeletTransformFit` in `PyShapeletFit`.
**Why it matters:** `ShapeletTransformFit` carries both the shapelet set AND the training
feature matrix; `shapelet_transform` on a handle requires access to `inner.shapelets()`,
which is `ShapeletTransformFit::shapelets()` → `&ShapeletSet`.
**Fix:** `PyShapeletFit.inner: ShapeletTransformFit`. Call `fit.inner.shapelets()` to get
`&ShapeletSet` before passing to `fdars_core::shapelet::shapelet_transform`.

### Pitfall 2: pub(crate) fields in GakGramTrain
**What goes wrong:** Trying to access `train.inner.log_self` or `train.inner.train_rows`
from pyfda's Rust code. These are `pub(crate)` to fdars-core, not visible from pyfda.
**Fix:** Pass the whole `&train.inner` to `gak_gram_predict` — that function lives in
fdars-core and accesses the private fields directly. The pyfda binding never needs to
touch `log_self` or `train_rows` itself.

### Pitfall 3: Wrong Gram predict shape / transposition
**What goes wrong:** Returning `(n_train, n_test)` instead of `(n_test, n_train)` for
`gak_gram_predict`. sklearn `SVC(kernel='precomputed').predict(K)` requires `K.shape ==
(n_test, n_train)`.
**Fix:** The upstream always returns `(n_test, n_train)`; `fdmatrix_to_numpy2d` preserves
this. Verify with a non-square test fixture where `n_test ≠ n_train`.

### Pitfall 4: ShapeletClassifier::Lda is a UNIT variant
**What goes wrong:** Treating `Lda` as `Lda {}` (struct-like) or `Lda(x)` (tuple-like).
**Fix:** `ShapeletClassifier::Lda` takes no fields. The match arm in the binding is simply:
`"lda" => Ok(ShapeletClassifier::Lda)`.

### Pitfall 5: Labels must be usize, Python passes i64
**What goes wrong:** Upstream `discover_shapelets` takes `&[usize]`; Python integer arrays
are `i64`. Using `PyReadonlyArray1<'py, usize>` panics at the PyO3 boundary.
**Fix:** Accept `PyReadonlyArray1<'py, i64>`, then convert: `.as_array().iter().map(|&v| v as usize).collect()`. Guard for negative values before the cast.

### Pitfall 6: max_candidates sentinel semantics
**What goes wrong:** Python caller passes `max_candidates=0` expecting "exhaustive" but the
binding maps `0` to `Some(0)` (zero-cap) instead of `None` (exhaustive).
**Fix:** Map Python `max_candidates=0` to `config.max_candidates = None` (exhaustive) inside
the binding. Use a sentinel of `0` or expose `Option<usize>` with Python `None`.

### Pitfall 7: GakConfig is #[non_exhaustive]
**What goes wrong:** `GakConfig { sigma: Some(s), ..Default::default() }` fails to compile
from outside the crate because the struct is `#[non_exhaustive]`.
**Fix:** Construct as `GakConfig { sigma }` (only one field; this is fine even for
`#[non_exhaustive]` structs with a single public field when the struct is instantiated by
setting all named fields — no `..` syntax needed). Alternatively use `GakConfig::with_sigma(s)`.

---

## Section 8 — Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Shapelet distance calculation | Custom sliding-window Euclidean | `fdars_core::shapelet::shapelet_distance` | z-normalization, early abandon, constant-window guard all in core |
| Gram matrix construction | NumPy/Python loop over `gak()` | `fdars_core::metric::gak::gak_gram_matrix` | Log-space DP to avoid underflow; parallel upper-triangle; bit-exact symmetry |
| Bandwidth selection | Custom heuristic | `fdars_core::metric::gak::sigma_gak` or `GakConfig::default()` | Median-distance heuristic with floor; identical to tslearn's approach |
| Enum dispatch | `if/else` chains | Dedicated `quality_from_str` / `classifier_from_str` functions | Centralizes the Err message; one place to update when enum gains variants |
| Label type conversion | Direct cast without guard | Explicit `i64 → usize` with negativity check | Rust `as usize` of a negative i64 wraps silently |

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `python -m pytest tests/test_shapelet.py tests/test_gak.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SHAPE-01 | `shapelet_transform_fit` returns `PyShapeletFit` handle with correct `n_shapelets`, `n_train` | unit | `pytest tests/test_shapelet.py::test_fit_handle_accessors -x` | ❌ Wave 0 |
| SHAPE-01 | `shapelet_transform` output shape `(n_new, K)` with `n_new ≠ n_train` (non-square) | unit | `pytest tests/test_shapelet.py::test_transform_shape -x` | ❌ Wave 0 |
| SHAPE-01 | `shapelet_classifier_fit` dict keys: n_shapelets, train_accuracy, classes, n_classes | unit | `pytest tests/test_shapelet.py::test_classifier_dict_keys -x` | ❌ Wave 0 |
| SHAPE-01 | `discover_shapelets` returns dict with `n_shapelets > 0` on a 2-class dataset | unit | `pytest tests/test_shapelet.py::test_discover -x` | ❌ Wave 0 |
| SHAPE-01 | `shapelet_distance` returns `(float, int)` tuple; distance ~0 for exact match | unit | `pytest tests/test_shapelet.py::test_distance -x` | ❌ Wave 0 |
| SHAPE-01 | Invalid quality string → `ValueError` | unit | `pytest tests/test_shapelet.py::test_quality_err_arm -x` | ❌ Wave 0 |
| SHAPE-01 | Invalid classifier string → `ValueError` | unit | `pytest tests/test_shapelet.py::test_classifier_err_arm -x` | ❌ Wave 0 |
| SHAPE-02 | `gak(x, x, sigma)` == 1.0; `gak(x, y, sigma)` in `[0,1]` | unit | `pytest tests/test_gak.py::test_gak_self_similarity -x` | ❌ Wave 0 |
| SHAPE-02 | `sigma_gak(data)` returns float > 0 | unit | `pytest tests/test_gak.py::test_sigma_gak -x` | ❌ Wave 0 |
| SHAPE-02 | `gak_gram_matrix` → shape `(n, n)`, diagonal all 1.0, symmetric | unit | `pytest tests/test_gak.py::test_gram_matrix_shape -x` | ❌ Wave 0 |
| SHAPE-02 | `gak_gram_train` → handle `.gram` shape `(n_train, n_train)`, `.sigma > 0`, `.n_train` correct | unit | `pytest tests/test_gak.py::test_gram_train_handle -x` | ❌ Wave 0 |
| SHAPE-02 | `gak_gram_predict` → shape `(n_test, n_train)` with `n_test ≠ n_train` (transposition check) | unit | `pytest tests/test_gak.py::test_gram_predict_shape -x` | ❌ Wave 0 |
| SHAPE-02 | `gak_gram_predict(fit, train_data)` reproduces `fit.gram` within 1e-12 | unit | `pytest tests/test_gak.py::test_gram_predict_reproduces_train -x` | ❌ Wave 0 |
| FND-02 | `"shapelet"` in `_submodule_names`; `fdars.shapelet` importable; all 5 functions + class registered | integration | `pytest tests/sklearn/test_foundation.py -x` | ✅ (adds "shapelet") |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_shapelet.py tests/test_gak.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_shapelet.py` — covers SHAPE-01 (7 tests)
- [ ] `tests/test_gak.py` — covers SHAPE-02 (6 tests)
- [ ] `src/shapelet_mod.rs` — new module (blank file, then filled per plan)

---

## Security Domain

Input validation is the only ASVS category that applies. GAK and shapelets are pure numeric
computation; no authentication, session, access control, or cryptography involved.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `to_pyresult` for FdarError; explicit guards for label types, sigma > 0, empty matrices |
| V6 Cryptography | no | — |

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Negative labels cast to usize → silent wrap | Tampering | Guard: check all labels ≥ 0 before cast |
| sigma ≤ 0 → log-domain -inf cascade | Tampering | Upstream validates; binding should also validate before calling |
| Empty matrix → panic in core | DoS | `gak_gram_matrix` / `gak_gram_predict` return `FdarError::InvalidDimension`; `to_pyresult` converts |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `fdars_core::shapelet::*` re-exports include all named types (verified in shapelet/mod.rs but crate-root re-exports not checked) | §5.4 | Compile error; fix by using `fdars_core::shapelet::classifier::ShapeletClassifier` etc. |
| A2 | `fdars_core::metric::gak::*` is the correct import path for GAK types from pyfda | §5.4 | Compile error if types are only pub(crate) or re-exported differently |
| A3 | `shapelet_classifier_fit` is bound without taking `PyShapeletFit` (independent path) | §1.3 | If users expect to reuse a fitted `PyShapeletFit` for classification, API mismatch |
| A4 | `discover_shapelets` is bound as a standalone function returning a summary dict (not `PyShapeletFit`) | §4.1 | If planner expects it to return a handle, type mismatch |

For A1 and A2: the executor should run `cargo check` after adding the import; fix the path if
needed. These are the most likely compile-time issues.

---

## Open Questions

1. **`discover_shapelets` Python return type**
   - What we know: returns `ShapeletSet` which contains `Vec<Shapelet>` and a `QualityMeasure`
   - What's unclear: should the binding return a summary dict `{n_shapelets, quality}` or a
     `PyShapeletFit` opaque handle (which would require re-running the transform)?
   - Recommendation: return a summary dict `{n_shapelets: int, quality: str}` for the
     standalone `discover_shapelets` binding. The full discovery+transform pipeline is
     `shapelet_transform_fit` → `PyShapeletFit`.

2. **`shapelet_classifier_predict` — expose or not?**
   - What we know: `ShapeletClassifierFit::predict(new_data)` exists in core and is callable
   - What's unclear: CONTEXT.md lists `shapelet_classifier_fit` returning a dict; prediction
     is not mentioned
   - Recommendation: Return a `PyShapeletClassifierFit` opaque handle (3rd opaque handle in
     this phase) with `n_shapelets`, `train_accuracy`, `classes`, and `.predict(new_data)`
     as a `#[pymethod]`. This is consistent with how every other fitted model in pyfda works.
     Alternatively, return dict + expose a separate `shapelet_classifier_predict(labels_array, new_data)`.

3. **GAK import path from pyfda**
   - What we know: `fdars_core::metric::gak` is the submodule where types are defined
   - What's unclear: whether crate root re-exports `GakGramTrain` / `GakConfig` at
     `fdars_core::GakConfig` etc.
   - Recommendation: Use `fdars_core::metric::gak::GakGramTrain` explicitly; resolve at
     compile time.

---

## Sources

### Primary (HIGH confidence)
- `[VERIFIED: shapelet/discovery.rs:33-79]` — QualityMeasure enum, ShapeletDiscoveryConfig fields, discover_shapelets signature
- `[VERIFIED: shapelet/discovery.rs:88-120]` — ShapeletSet struct fields and methods
- `[VERIFIED: shapelet/classifier.rs:41-52]` — ShapeletClassifier enum (Knn + Lda only)
- `[VERIFIED: shapelet/classifier.rs:61-96]` — ShapeletClassifierConfig, ShapeletClassifierFit
- `[VERIFIED: shapelet/classifier.rs:238-277]` — shapelet_classifier_fit signature
- `[VERIFIED: shapelet/transform.rs:96-97]` — shapelet_transform signature
- `[VERIFIED: shapelet/transform.rs:152-157]` — ShapeletTransformFit struct fields
- `[VERIFIED: shapelet/transform.rs:242-246]` — shapelet_transform_fit signature
- `[VERIFIED: shapelet/distance.rs:131-142]` — Shapelet struct fields
- `[VERIFIED: shapelet/distance.rs:246-250]` — shapelet_distance signature
- `[VERIFIED: shapelet/mod.rs:31-36]` — shapelet re-exports at fdars_core::shapelet::*
- `[VERIFIED: metric/gak.rs:52-64]` — GakConfig struct (non_exhaustive, single sigma field)
- `[VERIFIED: metric/gak.rs:155-163]` — gak() signature
- `[VERIFIED: metric/gak.rs:191-221]` — sigma_gak() signature and floor behavior
- `[VERIFIED: metric/gak.rs:255-258]` — gak_gram_matrix() signature
- `[VERIFIED: metric/gak.rs:349-373]` — GakGramTrain struct fields (pub vs pub(crate))
- `[VERIFIED: metric/gak.rs:414-422]` — gak_gram_train() signature
- `[VERIFIED: metric/gak.rs:458-531]` — gak_gram_predict() signature and (n_test, n_train) shape
- `[VERIFIED: metric/gak.rs:793-836]` — tests confirming predict shape and train reproducibility
- `[VERIFIED: src/lib.rs:1-77]` — register_submodule! macro and current module list
- `[VERIFIED: src/metric_mod.rs:483-505]` — metric_mod register() function to extend
- `[VERIFIED: src/pace_fpca_mod.rs:24-27]` — PyIrregFdata #[pyclass] opaque handle template
- `[VERIFIED: src/multi_fdata_mod.rs:38-56]` — PyMultiFunData handle + pymethods template
- `[VERIFIED: src/scalar_on_function_mod.rs:25-37]` — penalty_from_str Err-arm dispatch template
- `[VERIFIED: src/frechet_mod.rs:354-482]` — frechet_mean wildcard Err arm template
- `[VERIFIED: python/fdars/__init__.py:40-103]` — _submodule_names tuple + FND-02 registration loop

### Secondary (MEDIUM confidence)
- `[CITED: tests/sklearn/test_foundation.py:57-158]` — FND-02 guard: parses _submodule_names from git HEAD; adding "shapelet" to tuple satisfies the superset invariant

---

## Metadata

**Confidence breakdown:**
- Function signatures + struct fields: HIGH — read verbatim from 0.33 registry source
- Enum variant sets: HIGH — read verbatim, both enums have exactly 2 variants each
- pub(crate) field restriction: HIGH — confirmed directly in GakGramTrain source
- GAK Gram shape contract: HIGH — confirmed in test assertions in 0.33 source
- Registration mechanics: HIGH — confirmed against current lib.rs and __init__.py
- Classifier predict design: MEDIUM — CONTEXT.md is ambiguous; three options identified

**Research date:** 2026-09-04
**Valid until:** 2026-10-04 (stable — fdars-core 0.33 is pinned)
