# Architecture Research

**Domain:** PyO3 binding layer integration — fdars-core 0.17 new APIs into existing pyfda v4.0
**Researched:** 2026-08-13
**Confidence:** HIGH (all decisions grounded in actual source files read)

---

## Integration Map: New Functions to Existing Modules

### 1. Interpolation / Extrapolation / Imputation — `src/fdata_mod.rs` (MODIFIED)

**Decision: extend `fdata_mod.rs`, not a new module, not `basis_mod.rs`.**

Rationale: `fdata_mod.rs` owns the functional-data-object operations (`mean_1d`, `center_1d`,
`deriv_1d`, `normalize`, `geometric_median_1d`). Interpolation and imputation are per-object
data-preparation operations — they transform the observation matrix in place or evaluate it at
new grid points. They are not basis-expansion operations (basis projection + reconstruction live
in `basis_mod.rs`), and they are not metrics. Placing them alongside `mean_1d` and `deriv_1d` is
the most cohesive fit. `basis_mod.rs` already has `fdata_to_basis_1d` / `basis_to_fdata_1d` for
the projection-round-trip pattern; `spline_interpolate` is a direct grid-evaluation function, not
a basis-projection, so it does not belong there.

**New `#[pyfunction]` wrappers to add to `src/fdata_mod.rs`:**

| New pyfunction | fdars-core call (expected) | Return type |
|---|---|---|
| `spline_interpolate` | `fdars_core::fdata::spline_interpolate(mat, argvals, new_argvals, policy)` | `Bound<PyArray2<f64>>` |
| `impute_missing_values` | `fdars_core::fdata::impute_missing_values(mat, argvals, method)` | `Bound<PyArray2<f64>>` |

Both follow the `numpy2d_to_fdmatrix` -> compute -> `fdmatrix_to_numpy2d` round-trip already
established at `src/fdata_mod.rs:19-25` (`mean_1d`) and `src/fdata_mod.rs:190-199`
(`geometric_median_1d`).

**Register by appending to the existing `register()` fn in `fdata_mod.rs`:**
```rust
m.add_function(wrap_pyfunction!(spline_interpolate, m)?)?;
m.add_function(wrap_pyfunction!(impute_missing_values, m)?)?;
```

---

### 2. Functional Statistics + Scoring Metrics — TWO targets

#### 2a. Functional statistics -> `src/fdata_mod.rs` (MODIFIED)

**`functional_variance`, `functional_std`, `functional_covariance`, `depth_based_median`, `trim_mean`**

These are descriptive statistics on the functional data matrix. All follow the same pattern as
`mean_1d`: take data (n, m), argvals, return a result array. `depth_based_median` is a
trimming-aware median (uses depth ordering), which is a close sibling to `geometric_median_1d`
already in `fdata_mod.rs`. `trim_mean` is a straight functional mean after trimming extreme-depth
observations. `functional_covariance` returns a 2D matrix (m, m) via `fdmatrix_to_numpy2d`.

**New `#[pyfunction]` wrappers to add to `src/fdata_mod.rs`:**

| New pyfunction | Return type |
|---|---|
| `functional_variance_1d` | `Bound<PyArray1<f64>>` (pointwise variance, length m) |
| `functional_std_1d` | `Bound<PyArray1<f64>>` |
| `functional_covariance_1d` | `Bound<PyArray2<f64>>` (m x m covariance surface) |
| `depth_based_median_1d` | `Bound<PyArray1<f64>>` |
| `trim_mean_1d` | `Bound<PyArray1<f64>>` |

Apply dimension suffix `_1d` consistently with all existing `fdata_mod.rs` functions. If
2D variants exist in fdars-core 0.17, add `_2d` suffixed bindings in the same file.

#### 2b. Scoring metrics -> `src/metric_mod.rs` (MODIFIED)

**`functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, `explained_variance`**

These are prediction-error / goodness-of-fit metrics comparing two functional data sets (truth
vs prediction). The existing `metric_mod.rs` already owns `lp_self_1d`/`lp_cross_1d` (Lp
distance matrices), `int_simpson` (functional integral), and `inprod` (inner product). Scoring
metrics are structurally identical to `lp_cross_1d`: they take two matrices (n, m), compute an
integrated scalar or per-observation scalar, and return a numpy array. They belong in
`metric_mod.rs`, not `fdata_mod.rs`, because they measure relationship between two functional
data objects (a prediction and truth pair), not a property of one.

**New `#[pyfunction]` wrappers to add to `src/metric_mod.rs`:**

| New pyfunction | Inputs | Return type |
|---|---|---|
| `functional_mae_1d` | y_true (n,m), y_pred (n,m), argvals | `Bound<PyArray1<f64>>` per-obs or `f64` scalar |
| `functional_mse_1d` | y_true (n,m), y_pred (n,m), argvals | same |
| `functional_mape_1d` | y_true (n,m), y_pred (n,m), argvals | same |
| `functional_msle_1d` | y_true (n,m), y_pred (n,m), argvals | same |
| `explained_variance_1d` | y_true (n,m), y_pred (n,m), argvals | `f64` scalar |

**Register by appending to the existing `register()` fn in `metric_mod.rs`** (currently ends at
line 504 with `hshift_cross_1d`).

---

### 3. Alignment / Registration — `src/alignment_mod.rs` (MODIFIED)

**`least_squares_shift_registration`, `least_squares_score`, `pairwise_correlation_score`,
`sobolev_least_squares_score`, `karcher_mean_with_band`, `*_distance_matrix_with_band`,
`band_frac`**

All registration functions belong in `alignment_mod.rs`. This module is already the home for
shift-type operations (e.g. `hshift_self_1d` is in `metric_mod.rs` as a distance, but the
registration operation producing shifted data belongs in `alignment_mod.rs`). The existing
landmark registration functions (`landmark_register`, `landmark_detect_and_register`) are already
there as structural precedent for registration methods that return richer result structs. Banded
elastic alignment (`karcher_mean_with_band`, banded distance matrices) are variants of existing
functions in `alignment_mod.rs` (`karcher_mean`, `elastic_self_distance_matrix`) and should sit
adjacent to them.

**New `#[pyfunction]` wrappers to add to `src/alignment_mod.rs`:**

| New pyfunction | fdars-core call | Return type |
|---|---|---|
| `least_squares_shift_registration` | `fdars_core::alignment::least_squares_shift_registration(mat, av)` | dict (see struct below) |
| `least_squares_score` | `fdars_core::alignment::least_squares_score(mat, av)` | `f64` |
| `pairwise_correlation_score` | `fdars_core::alignment::pairwise_correlation_score(mat, av)` | `f64` |
| `sobolev_least_squares_score` | `fdars_core::alignment::sobolev_least_squares_score(mat, av)` | `f64` |
| `karcher_mean_with_band` | `fdars_core::alignment::karcher_mean_with_band(mat, av, band_frac, ...)` | dict (same keys as `karcher_mean`) |
| `elastic_self_distance_matrix_with_band` | banded variant | `Bound<PyArray2<f64>>` |
| `elastic_cross_distance_matrix_with_band` | banded variant | `Bound<PyArray2<f64>>` |
| `band_frac` | utility scalar | `f64` (or omit if trivial constant) |

**Register by appending to the existing `register()` fn in `alignment_mod.rs`** (currently ends
at line 2137 with `warp_inverse_error`).

---

## Enum Crossing Convention

**Decision: string parameter + `match` arm, identical to all existing enum-like parameters.**

This is grounded in three concrete examples already in the codebase:

1. **`linkage` in `alignment_mod.rs:927`** — `hierarchical_from_distances` takes `linkage: &str`
   and maps it to `fdars_core::alignment::Linkage::Single/Complete/Average` via a `match` block.
   This is the closest structural parallel to `ExtrapolationPolicy` and `ImputationMethod`.

2. **`basis_type` in `basis_mod.rs:35`** — `fdata_to_basis_1d` takes `basis_type: &str` and maps
   to integer codes (0/1) via a `match` block with an explicit `PyValueError` for unrecognised
   values.

3. **`penalty_type` in `alignment_mod.rs:692`** — `elastic_align_pair_penalized` takes
   `penalty_type: &str` and maps to `fdars_core::alignment::WarpPenaltyType::FirstOrder/
   SecondOrder/Combined`.

No existing binding in this codebase uses a Python `enum.Enum` class crossing the PyO3 boundary.
The established pattern is `str` parameter with a `match` block that raises `PyValueError` for
invalid values.

**Applied to new enums:**

`ExtrapolationPolicy` — bind as `extrapolation: &str` with values `"boundary"`, `"exception"`,
`"fill"`, `"periodic"`. Default `"boundary"`. Match to `fdars_core::fdata::ExtrapolationPolicy`.
Error on unrecognised: `PyValueError::new_err("extrapolation must be 'boundary', 'exception', 'fill', or 'periodic'")`.

`ImputationMethod` — bind as `method: &str` with values `"linear"`, `"mean"`, `"constant"`.
Default `"linear"`. Match to `fdars_core::fdata::ImputationMethod`.

---

## Result Struct Crossing Convention

**Decision: return `PyDict` (not a Python class), consistent with all existing compound-result
bindings.**

Evidence from every existing compound-result function in this codebase:

- `elastic_align_pair` (alignment_mod.rs:35): returns `Bound<PyDict>` with keys `f_aligned`,
  `gamma`, `distance`.
- `karcher_mean` (alignment_mod.rs:71): returns `Bound<PyDict>` with six keys.
- `elastic_depth` (alignment_mod.rs:393): returns `Bound<PyDict>` with five keys.
- `pspline_fit_1d` (basis_mod.rs:115): returns `Bound<PyAny>` (which is a `PyDict`).

There is no existing precedent for a `#[pyclass]` result struct. The `fdars.results` module in
the Python layer provides optional typed wrappers (e.g. `AlignmentResult`) over these raw dicts,
but the native boundary always returns `PyDict`.

**`ShiftRegistrationResult` -> returned as `PyDict` from `least_squares_shift_registration`:**

```rust
// Expected dict keys (subject to actual fdars-core 0.17 struct):
dict.set_item("shifts", vec_to_numpy1d(py, result.shifts))?;
dict.set_item("aligned_data", fdmatrix_to_numpy2d(py, &result.aligned_data))?;
dict.set_item("score", result.score)?;
```

Rationale: a `#[pyclass]` would require implementing `__repr__`, `__eq__`, and property
accessors, significant overhead with no concrete user-facing benefit, since all existing
user-facing convenience is already provided by the Python-layer `fdars.results` wrappers.

---

## Fdata Class Methods vs Module-Level Functions

**Decision: `fd.impute()` and `fd.interpolate()` as Fdata methods; scoring metrics and alignment
functions stay module-level only.**

**Promote to Fdata methods (`python/fdars/fdata_class.py`):**

- `fd.interpolate(new_argvals, extrapolation="boundary")` -- delegates to
  `fdars.fdata.spline_interpolate(self.data, self.argvals, new_argvals, extrapolation)` and
  returns a new `Fdata` with updated `argvals` and `data`. This is the same pattern as the
  existing `fd.deriv()`, `fd.center()`, `fd.normalize()` -- transformations that return a new
  `Fdata`.

- `fd.impute(method="linear")` -- delegates to
  `fdars.fdata.impute_missing_values(self.data, self.argvals, method)` and returns a new `Fdata`.
  NaN-filling is a natural Fdata-level concern.

**Keep as module-level only (no Fdata method):**

- `fdars.fdata.functional_variance_1d`, `functional_std_1d`, `functional_covariance_1d`,
  `depth_based_median_1d`, `trim_mean_1d` -- these could optionally become `fd.variance()` etc.,
  but `fd.mean()` is the only existing statistical summary promoted to a Fdata method. Adding
  five more in one milestone would over-expand the class interface. Keep module-level; promote
  selectively after usage patterns are established in docs.

- All scoring metrics (`functional_mae_1d`, etc.) -- these take two functional data objects
  (truth and prediction), which makes them a poor fit for an instance method. They stay
  module-level in `fdars.metric`.

- All alignment/registration functions -- already module-level in `fdars.alignment`. The existing
  Fdata class has no alignment method, and shift registration is not a single-object operation.

---

## Advisor Extension Integration Points

### Which new capabilities warrant advisor extension

**Extend: scoring metrics, imputation, registration quality.**

These three produce diagnostics that are meaningful to interpret. Functional
variance/std and banded alignment variants are compute primitives that speak for themselves
numerically and do not benefit from LLM interpretation.

### New method strings vs new diagnostic keys on existing aspects

**Decision: add new diagnostic keys to existing aspects rather than new method strings, except
for scoring metrics which warrant a new `"scoring"` method string.**

**Scoring metrics -> new `"scoring"` method string in `build_diagnostics`:**

Scoring metrics compare predictions to truth. This is structurally distinct from all 12 existing
aspects (alignment, fpca, basis, smoothing, clustering, depth, outliers, classification, represent,
regression, regression_cv, spm). None of the existing aspects produce MAE/MSE/explained-variance
keys. Adding `"scoring"` as a 13th aspect follows the established pattern:

1. Add `"scoring"` to `_supported` in `advisor/__init__.py:build_diagnostics`.
2. Create `python/fdars/advisor/aspects/scoring.py` with `_build_scoring_diagnostics(raw)`.
3. Add the `if method_lc == "scoring":` dispatch block in `build_diagnostics`.
4. Add a `"scoring"` entry to `_ASPECT_PRIMERS` in `advisor/_prompts.py`.

**Imputation -> new diagnostic keys on the `"represent"` aspect:**

Imputation is a data-preparation step for the represent/grid aspect. The existing `represent`
aspect builder in `advisor/aspects/represent.py` already examines `n_points`, `is_uniform_grid`.
Add imputation-quality keys (e.g. `imputed_fraction`, `imputed_pattern`) to
`_build_represent_diagnostics`. No new method string needed.

**Registration quality -> new diagnostic keys on the `"alignment"` aspect:**

`least_squares_score`, `pairwise_correlation_score`, `sobolev_least_squares_score` are
scalar quality metrics for a registration result. They map naturally into
`advisor/aspects/alignment.py`'s `_build_alignment_diagnostics`, alongside the existing
`health_score` and amplitude/phase distance keys. Add keys `shift_registration_score`,
`pairwise_correlation_score`, `sobolev_score` when the input result dict contains them.

### MCP `_DIAGNOSTICS_METHODS` and `_RUNNABLE_METHODS` changes

**`_DIAGNOSTICS_METHODS` change:** Add `"scoring"` -> becomes 13 methods.

**`_RUNNABLE_METHODS` change:** No change. Scoring requires caller-supplied y_true and y_pred
arrays, which the MCP dataset model (single data + argvals handle) cannot supply at `run_method`
time. This is the same reason `outliers`, `classification`, `regression`, `regression_cv`, `spm`
are diagnostics-only. `"scoring"` joins that diagnostics-only tier.

**`_runner.py`:** No change. `_RUNNABLE_METHODS` stays at 6.

### Guard/advisor-sync test maintenance

The key test is `tests/test_mcp_server.py:test_diagnostics_methods_match_advisor_supported`
(line 503). This test:
1. Imports `_DIAGNOSTICS_METHODS` from `fdars.mcp.server`.
2. Triggers `build_diagnostics("bad_method")` to extract `advisor._supported` from the error
   message via `ast.literal_eval`.
3. Asserts `_DIAGNOSTICS_METHODS == advisor_supported`.

To keep this test green after adding `"scoring"`:
- Add `"scoring"` to `_supported` in `advisor/__init__.py`.
- Add `"scoring"` to `_DIAGNOSTICS_METHODS` in `mcp/server.py`.
- Both changes must land in the same commit/phase or the test will fail between steps.

No changes needed to `test_mcp_server.py` itself -- the test detects drift automatically by
comparing the two sets, so it self-validates any correct update.

---

## Dependency-Ordered Build Sequence

```
Phase A: Crate bump (Cargo.toml)
    fdars-core 0.14.0 -> 0.17.0
    Run: maturin develop && pytest tests/test_basic.py tests/test_advisor.py
    Gate: full suite green (no existing binding broken by additive 0.15-0.17 bump)

Phase B: Interpolation / Imputation bindings
    Files modified: src/fdata_mod.rs (add spline_interpolate, impute_missing_values)
    Files modified: python/fdars/fdata_class.py (add fd.interpolate(), fd.impute())
    Depends on: Phase A
    Gate: tests for new functions; fd.interpolate() and fd.impute() round-trip tests

Phase C: Functional statistics + scoring metrics bindings
    Files modified: src/fdata_mod.rs (add variance/std/covariance/depth_based_median/trim_mean)
    Files modified: src/metric_mod.rs (add functional_mae/mse/mape/msle/explained_variance)
    Depends on: Phase A
    Gate: statistical output tests; scoring metrics vs known values

Phase D: Alignment / registration bindings
    Files modified: src/alignment_mod.rs (add shift registration, quality scores, banded variants)
    Depends on: Phase A
    Gate: ShiftRegistrationResult dict keys verified; score scalar outputs verified

Phase E: Advisor extension
    Files modified: python/fdars/advisor/__init__.py (add "scoring" to _supported + dispatch)
    Files new:      python/fdars/advisor/aspects/scoring.py
    Files modified: python/fdars/advisor/aspects/represent.py (imputation keys)
    Files modified: python/fdars/advisor/aspects/alignment.py (registration quality keys)
    Files modified: python/fdars/advisor/_prompts.py (add "scoring" to _ASPECT_PRIMERS)
    Files modified: python/fdars/mcp/server.py (add "scoring" to _DIAGNOSTICS_METHODS)
    Depends on: Phase B (impute for represent), Phase C (scoring metrics), Phase D (reg quality)
    Gate: test_diagnostics_methods_match_advisor_supported passes; offline diagnostics
          round-trip green; grounding invariant holds for scoring aspect

Phase F: Docs (diagrams + worked examples)
    Depends on: Phases A-E fully green
    Files: docs/represent/, docs/analyze/, docs/align/ pages; new/updated SVGs
    Gate: mkdocs build --strict
```

---

## Component Responsibilities (Integration View)

| File | Change Type | What Changes |
|------|-------------|-------------|
| `Cargo.toml` | Modified | `fdars-core = "0.17.0"` |
| `src/fdata_mod.rs` | Modified | +7 pyfunctions: spline_interpolate, impute_missing_values, functional_variance_1d, functional_std_1d, functional_covariance_1d, depth_based_median_1d, trim_mean_1d |
| `src/metric_mod.rs` | Modified | +5 pyfunctions: functional_mae_1d, functional_mse_1d, functional_mape_1d, functional_msle_1d, explained_variance_1d |
| `src/alignment_mod.rs` | Modified | +7 pyfunctions: least_squares_shift_registration, least_squares_score, pairwise_correlation_score, sobolev_least_squares_score, karcher_mean_with_band, elastic_self_distance_matrix_with_band, elastic_cross_distance_matrix_with_band |
| `src/lib.rs` | NOT modified | No new submodules; all new functions go into existing registered modules |
| `python/fdars/__init__.py` | NOT modified | No new submodule names; _submodule_names unchanged |
| `python/fdars/fdata_class.py` | Modified | +2 methods: fd.interpolate(), fd.impute() |
| `python/fdars/advisor/__init__.py` | Modified | Add "scoring" to _supported; add dispatch block |
| `python/fdars/advisor/aspects/scoring.py` | NEW file | _build_scoring_diagnostics(raw) |
| `python/fdars/advisor/aspects/represent.py` | Modified | +imputation diagnostic keys |
| `python/fdars/advisor/aspects/alignment.py` | Modified | +registration quality score keys |
| `python/fdars/advisor/_prompts.py` | Modified | Add "scoring" entry to _ASPECT_PRIMERS |
| `python/fdars/mcp/server.py` | Modified | Add "scoring" to _DIAGNOSTICS_METHODS (13 total) |
| `python/fdars/mcp/_runner.py` | NOT modified | _RUNNABLE_METHODS stays at 6 |

---

## Key Architectural Constraints Upheld

**Grounding invariant:** The `"scoring"` aspect advisor extension follows the same pattern as all
11 existing aspects -- `_build_scoring_diagnostics` computes all numbers from fdars, the LLM only
interprets. Scoring metrics (MAE, MSE etc.) are computed by fdars-core via the native bindings,
not by the advisor layer.

**MCP LLM-free boundary:** `fdars_build_diagnostics` for `"scoring"` works identically to all
other diagnostics-only aspects. The user provides a pre-computed scoring result dict; the tool
builds diagnostics from it. No LLM is in the compute path.

**Row-major / column-major layout:** All new `fdata_mod.rs` and `metric_mod.rs` functions use the
existing `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d` helpers from `src/convert.rs`. No new
conversion utilities needed.

**ABI3 stable:** No change to the PyO3 compilation model. New functions are thin `#[pyfunction]`
wrappers, same pattern as the 100+ already existing.

**No new submodules:** All new bindings integrate into existing modules. `src/lib.rs` and
`python/fdars/__init__.py` are not modified, which means zero risk to the submodule registration
plumbing.

---

## Anti-Patterns to Avoid

### Adding a new Rust submodule for these bindings

**What people do:** Create a new `fdars.scoring` or `fdars.represent` native submodule, which
requires changes to `src/lib.rs` (new `mod` declaration + `register_submodule!` call) and
`python/fdars/__init__.py` (new name in `_submodule_names`).

**Why it's wrong:** Coordination hazard that risks breaking the existing import plumbing for no
cohesion benefit. The new functions fit naturally into existing module semantics.

**Do this instead:** Add to existing modules (fdata = per-object ops, metric = comparison/
distance, alignment = registration).

### Binding enums as Python `enum.Enum` classes

**What people do:** Declare `#[pyclass] enum ExtrapolationPolicy` with `Boundary`, `Exception`,
`Fill`, `Periodic` variants; register it in `lib.rs`.

**Why it's wrong:** Forces `fdars.fdata.ExtrapolationPolicy.BOUNDARY` syntax that diverges from
every other parameter in the library. All existing enum-like parameters are strings
(`linkage: &str` at alignment_mod.rs:927, `basis_type: &str` at basis_mod.rs:35,
`penalty_type: &str` at alignment_mod.rs:692).

**Do this instead:** Use `extrapolation: &str` with `match` + `PyValueError` for invalid values.

### Implementing `ShiftRegistrationResult` as a `#[pyclass]`

**What people do:** Define a Python class for the struct so users can write `result.shifts`.

**Why it's wrong:** The entire library uses dict access from the native boundary. There is no
existing `#[pyclass]` result type in any of the 18 `*_mod.rs` files. Breaks the `fdars.results`
wrapper pattern.

**Do this instead:** Return `Bound<PyDict>`. Add an optional typed wrapper in
`python/fdars/results.py` if attribute access is needed.

### Adding advisor logic for every new binding

**What people do:** Build a new advisor aspect for `functional_variance_1d` and banded alignment.

**Why it's wrong:** Compute primitives produce a number that is self-explanatory. Inflating the
advisor surface with trivial cases weakens signal-to-noise in the advisor output.

**Do this instead:** Only extend the advisor where interpretation adds value -- scoring metrics
(what does MAE 0.8 mean in context?), imputation quality (is imputed_fraction dangerously high?),
registration quality (is pairwise_correlation_score better or worse than expected?).

---

*Architecture analysis: 2026-08-13*
*Grounded in: src/lib.rs, src/convert.rs, src/alignment_mod.rs, src/basis_mod.rs,*
*src/metric_mod.rs, src/fdata_mod.rs (register fn), python/fdars/__init__.py,*
*python/fdars/fdata_class.py, python/fdars/advisor/__init__.py,*
*python/fdars/advisor/_prompts.py, python/fdars/mcp/server.py,*
*python/fdars/mcp/_runner.py, tests/test_mcp_server.py:503*
