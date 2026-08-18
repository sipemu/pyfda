# Phase 31 — Confirmed fdars-core 0.20.0 Signatures

**Source:** Direct read of vendored crate at
`~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.20.0/src/`

**Date recorded:** 2026-08-17

This file is the authoritative reference for every binding in plans 31-01, 31-02, and 31-03.
Do not derive signatures from docs.rs; read this file instead.

---

## 1. `TestResult` (inference/mod.rs)

```rust
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[non_exhaustive]
pub struct TestResult {
    pub statistic: f64,
    pub p_value: f64,
    pub n_perm: usize,
}
```

- **`#[non_exhaustive]`** — never struct-literal it; always access fields individually.
- `n_perm == 0` for all asymptotic/SCB paths; `n_perm == n_perm_arg` for permutation tests.

---

## 2. `ToleranceBand` (tolerance/types.rs)

```rust
#[derive(Debug, Clone, PartialEq)]
#[non_exhaustive]
pub struct ToleranceBand {
    pub lower: Vec<f64>,
    pub upper: Vec<f64>,
    pub center: Vec<f64>,
    pub half_width: Vec<f64>,
}
```

- **`#[non_exhaustive]`** — access each field individually.
- All four fields are `Vec<f64>` of length `m` (grid points).
- Used by `mean_scb` (returns `ToleranceBand`).
- Expose to Python as: `{"lower": ndarray, "upper": ndarray, "center": ndarray, "half_width": ndarray}`.

---

## 3. `MultiplierDistribution` (tolerance/types.rs)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum MultiplierDistribution {
    /// Standard normal multipliers
    Gaussian,
    /// Rademacher multipliers (+1/-1 with equal probability)
    Rademacher,
}
```

- **`#[non_exhaustive]`** — all match arms must include a wildcard `_ =>` fallback.
- Module path: `fdars_core::tolerance::MultiplierDistribution`
- Python string convention: `"gaussian"` → `Gaussian`, `"rademacher"` → `Rademacher`.
- Wildcard must return `PyValueError::new_err("multiplier must be 'gaussian' or 'rademacher'")`.

---

## 4. `DEFAULT_N_PERM` (inference/permutation.rs)

```rust
pub const DEFAULT_N_PERM: usize = 999;
```

- Use as the Python default for `n_perm` in `t_perm_test` and `f_perm_test`.
- Both functions return `FdarError::InvalidParameter` when `n_perm == 0`.

---

## 5. `t_perm_test` (inference/permutation.rs)

```rust
pub fn t_perm_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    n_perm: usize,
    seed: u64,
) -> Result<TestResult, FdarError>
```

- Uses integrated L2 distance between sample-mean curves (sqrt ∫ (mean_a − mean_b)² dt).
- `seed` is `u64` (NOT Option) — wrap as `seed: Option<u64>` in Python, resolve with
  `seed.unwrap_or(0)` (fixed default 0 per locked decision D).
- Errors: `InvalidDimension` if columns mismatch, argvals length mismatch, or <2 rows per sample;
  `InvalidParameter` if `n_perm == 0`.
- Accessible as `fdars_core::inference::t_perm_test`.

---

## 6. `f_perm_test` (inference/permutation.rs)

```rust
pub fn f_perm_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    n_perm: usize,
    seed: u64,
) -> Result<TestResult, FdarError>
```

- Uses integrated F-statistic (k=2 case of functional ANOVA via `integrated_f_statistic`).
- Identical parameter shape and error conditions to `t_perm_test`.
- `seed` is `u64` — same `unwrap_or(0)` wrapping strategy.
- Accessible as `fdars_core::inference::f_perm_test`.

---

## 7. `two_sample_mean_test` (inference/hotelling.rs)

```rust
pub fn two_sample_mean_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    ncomp: usize,
) -> Result<TestResult, FdarError>
```

- Asymptotic Hotelling-T² on a shared FPC basis fitted on pooled data.
- **NO seed parameter** — deterministic chi-square asymptotic test.
- Returns `TestResult` with `n_perm = 0` always.
- `ncomp` default: `5` (per locked decision D); docstring should note keep small vs min(n_a, n_b).
- Errors: `InvalidDimension` (columns mismatch, argvals mismatch, <2 rows);
  `InvalidParameter` if `ncomp < 1` (`ncomp == 0`).
- Accessible as `fdars_core::inference::two_sample_mean_test`.

---

## 8. `mean_scb` (inference/scb.rs, wraps tolerance::scb_mean_degras)

```rust
pub fn mean_scb(
    data: &FdMatrix,
    argvals: &[f64],
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: MultiplierDistribution,
) -> Result<ToleranceBand, FdarError>
```

- Returns `ToleranceBand` (not `TestResult`).
- `multiplier` is a `MultiplierDistribution` enum — accept Python string, match to variant.
- Errors forwarded from `scb_mean_degras`: `InvalidDimension` (<3 rows, 0 cols, argvals mismatch);
  `InvalidParameter` (bandwidth ≤ 0, nb == 0, confidence outside (0,1)).
- Accessible as `fdars_core::inference::mean_scb`.
- Python dict: `{"lower": ndarray, "upper": ndarray, "center": ndarray, "half_width": ndarray}`.

---

## 9. `scb_two_sample_test` (inference/scb.rs)

```rust
pub fn scb_two_sample_test(
    data_a: &FdMatrix,
    data_b: &FdMatrix,
    argvals: &[f64],
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: MultiplierDistribution,
) -> Result<TestResult, FdarError>
```

- Returns `TestResult` with `n_perm = 0`.
- `statistic` = max standardised excursion of the difference band from zero; > 1.0 when null rejected.
- `p_value` = 0.0 (rejected) or 1.0 (not rejected) — binary decision at the requested confidence level.
- `multiplier` is `MultiplierDistribution` — same string-dispatch as `mean_scb`.
- Errors: `InvalidDimension` (column mismatch, argvals mismatch); forwarded SCB errors.
- Accessible as `fdars_core::inference::scb_two_sample_test`.

---

## 10. `flm_f_test` (inference/flm.rs)

```rust
pub fn flm_f_test(fit: &FregreLmResult) -> Result<TestResult, FdarError>
```

- Takes a **reference** to a fitted `FregreLmResult` (non-pyclass Rust struct — never crosses Python boundary).
- The Python wrapper **re-fits the model internally**: accept `data`, `response`, `ncomp` → call
  `fdars_core::scalar_on_function::fregre_lm(&data, &resp, None, ncomp)` → pass `&result` to `flm_f_test`.
- Reads from `FregreLmResult`: `fit.ncomp` (usize), `fit.residuals` (Vec<f64>), `fit.r_squared` (f64).
- Returns `TestResult` with `n_perm = 0`.
- Errors: `InvalidParameter` when `ncomp == 0`, denominator df ≤ 0, or `r_squared` not finite/≥1.
- Accessible as `fdars_core::inference::flm_f_test`.

---

## 11. `flm_gof_test` (inference/flm.rs)

```rust
pub fn flm_gof_test(fit: &FregreLmResult) -> Result<TestResult, FdarError>
```

- Same re-fit strategy as `flm_f_test` (Python accepts `data`, `response`, `ncomp`).
- Reads from `FregreLmResult`: `fit.residuals` (Vec<f64>), `fit.fitted_values` (Vec<f64>).
- Ramsey-RESET-style goodness-of-fit: auxiliary regression of residuals on polynomial expansion of fitted values.
- Returns `TestResult` with `n_perm = 0`; small `p_value` → lack of fit (model mis-specified).
- Errors: `InvalidParameter` when `n ≤ 4` (degenerate aux df), lengths mismatch, non-finite values,
  or fitted values constant (rank-deficient design).
- Accessible as `fdars_core::inference::flm_gof_test`.

---

## 12. `oneway_anova_vstat` (inference/anova.rs)

```rust
pub fn oneway_anova_vstat(
    data: &FdMatrix,
    groups: &[usize],
    argvals: &[f64],
) -> Result<TestResult, FdarError>
```

- Asymptotic one-way functional ANOVA V-statistic (scaled-χ² Satterthwaite approximation).
- **`groups`** is `&[usize]` — **0-indexed** is the documented convention in the crate.
  Labels are sort/dedup/position-matched internally, so any distinct `usize` values work
  (they need not be 0-based, but 0-indexed is documented).
- Returns `TestResult` with `n_perm = 0`.
- Validation: `groups.len() == n`; at least 2 distinct groups; at least 3 observations (`n >= 3`);
  `argvals.len() == m`; `m > 0`.
- Errors: `InvalidDimension` (0 cols, groups len mismatch, argvals len mismatch, n < 3);
  `InvalidParameter` (fewer than 2 distinct groups).
- Python: accept `groups` as a numpy int array (`PyReadonlyArray1<i64>`) or Python list;
  convert to `Vec<usize>` via `numpy1d_to_usize_vec`.
- Accessible as `fdars_core::inference::oneway_anova_vstat`.

---

## 13. `fregre_lm` and `FregreLmResult` (scalar_on_function/fregre_lm.rs)

### Signature:
```rust
pub fn fregre_lm(
    data: &FdMatrix,
    y: &[f64],
    scalar_covariates: Option<&FdMatrix>,
    ncomp: usize,
) -> Result<FregreLmResult, FdarError>
```

- **NO argvals parameter** — uses a uniform [0, 1] grid internally.
- `scalar_covariates: Option<&FdMatrix>` — pass `None` for the pure functional model (always the case
  in the inference re-fit wrappers).
- Accessible as `fdars_core::scalar_on_function::fregre_lm`.

### `FregreLmResult` fields used by inference tests:
```rust
pub struct FregreLmResult {
    pub fitted_values: Vec<f64>,  // length n — used by flm_gof_test
    pub residuals: Vec<f64>,      // length n — used by flm_f_test + flm_gof_test
    pub beta_t: Vec<f64>,         // length m — not used by inference tests
    pub r_squared: f64,           // scalar — used by flm_f_test
    pub coefficients: Vec<f64>,   // FPC coefficient vector — not used by inference tests
    pub intercept: f64,           // scalar — not used by inference tests
    pub ncomp: usize,             // number of FPC components actually used — used by flm_f_test
}
```

(Also has `ncomp: usize` field confirmed from `flm.rs` reading `fit.ncomp`.)

---

## Summary: Python Signatures for Plan 31-01 (this plan)

| Function | Python signature | Returns | n_perm |
|---|---|---|---|
| `t_perm_test` | `(data_a, data_b, argvals, n_perm=999, seed=None)` | `{statistic, p_value, n_perm}` | = arg |
| `f_perm_test` | `(data_a, data_b, argvals, n_perm=999, seed=None)` | `{statistic, p_value, n_perm}` | = arg |
| `two_sample_mean_test` | `(data_a, data_b, argvals, ncomp=5)` | `{statistic, p_value, n_perm}` | always 0 |

## Summary: Python Signatures for Plan 31-02

| Function | Python signature | Returns | n_perm |
|---|---|---|---|
| `mean_scb` | `(data, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian")` | `{lower, upper, center, half_width}` (each ndarray) | N/A |
| `scb_two_sample_test` | `(data_a, data_b, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian")` | `{statistic, p_value, n_perm}` | always 0 |

## Summary: Python Signatures for Plan 31-03

| Function | Python signature | Returns | n_perm |
|---|---|---|---|
| `flm_f_test` | `(data, response, ncomp=3)` | `{statistic, p_value, n_perm}` | always 0 |
| `flm_gof_test` | `(data, response, ncomp=3)` | `{statistic, p_value, n_perm}` | always 0 |
| `oneway_anova_vstat` | `(data, groups, argvals)` | `{statistic, p_value, n_perm}` | always 0 |

---

## Key Reminders for Binding Authors

1. **Seed default:** `seed.unwrap_or(0)` — fixed default 0 (NOT 42) per locked decision D.
2. **`#[non_exhaustive]` structs:** NEVER struct-literal `TestResult` or `ToleranceBand` in tests/wrappers.
   Access fields individually (`result.statistic`, `result.p_value`, `result.n_perm`).
3. **`MultiplierDistribution` match:** always include `_ => return Err(PyValueError::new_err(...))` wildcard.
4. **`fregre_lm` re-fit:** takes `data, y, None, ncomp` — NO argvals parameter (uses uniform grid internally).
5. **`oneway_anova_vstat` groups:** `Vec<usize>` — convert from `PyReadonlyArray1<i64>` via `numpy1d_to_usize_vec`.
6. **No `.unwrap()`:** route all `Result<T, FdarError>` through `to_pyresult()`.
7. **Module paths:**
   - Permutation/Hotelling: `fdars_core::inference::{t_perm_test, f_perm_test, two_sample_mean_test}`
   - SCB: `fdars_core::inference::{mean_scb, scb_two_sample_test}`
   - FLM: `fdars_core::inference::{flm_f_test, flm_gof_test}`
   - ANOVA: `fdars_core::inference::oneway_anova_vstat`
   - Fregre: `fdars_core::scalar_on_function::fregre_lm`
   - MultiplierDistribution: `fdars_core::tolerance::MultiplierDistribution`
