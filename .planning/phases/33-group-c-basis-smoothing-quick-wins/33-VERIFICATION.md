---
phase: 33-group-c-basis-smoothing-quick-wins
verified: 2026-08-17T21:30:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 33: Group-C Basis/Smoothing Quick Wins — Verification Report

**Phase Goal:** Users can construct a constant intercept basis and select AIC-optimal basis/kernel smoothing parameters, via additive extensions to `fdars.basis` and `fdars.smoothing`.
**Verified:** 2026-08-17
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `fdars.basis.constant_basis(argvals)` returns an all-ones 1-D ndarray of length `len(argvals)` (BASIS-01) | VERIFIED | Live: `c = b.constant_basis(np.linspace(0,1,20)); c.shape==(20,), np.allclose(c,1.0)` → PASS. Empty input returns `(0,)`. Rust: `fdars_core::basis::constant_basis(&av)` (infallible) returned via `vec_to_numpy1d`. Registered at `basis_mod.rs:762`. |
| 2 | `fdars.basis.smooth_basis_aic(...)` returns a valid dict with keys `{fitted, coefficients, edf, gcv, aic, bic, nbasis}` on valid data; degenerate input (`n_basis=1`) raises ValueError (BASIS-02) | VERIFIED | Live: Canadian Weather (35x365), `n_basis=10`: all expected keys present, `aic=-3390.76`, `edf=7.97`, `fitted.shape==(35,365)`. Degenerate `n_basis=1` raises `ValueError("smooth_basis_aic failed")`. 11/11 tests pass. |
| 3 | `fdars.basis.basis_nbasis_cv(criterion='aic')` runs and returns `result['criterion']=='aic'` (BASIS-02) | VERIFIED | Live: `b.basis_nbasis_cv(X, day, nbasis_min=4, nbasis_max=8, criterion='aic')` → `optimal_nbasis=8, criterion='aic'`. Pre-existing Rust dispatch at `basis_mod.rs:537`. Unknown criterion raises ValueError. |
| 4 | `fdars.smoothing.optim_bandwidth(criterion='aic')` returns a sane bandwidth and `result['criterion']=='aic'` (Phase-30 stopgap output arm replaced) (BASIS-03) | VERIFIED | Live: `h_opt=0.0956, criterion='aic'`. GCV non-regression also confirmed: `criterion='gcv'`. Explicit `CvCriterion::Aic => "aic"` output arm at `smoothing_mod.rs:213`. Wildcard `_ => "unknown"` retained for `#[non_exhaustive]` forward-compat. |
| 5 | Unknown criterion string raises ValueError on both `optim_bandwidth` and `basis_nbasis_cv` (BASIS-01/02/03 robustness) | VERIFIED | Live: `sm.optim_bandwidth(x, y, criterion='banana')` → `ValueError: criterion must be 'cv', 'gcv', or 'aic'`. `b.basis_nbasis_cv(X, day, criterion='banana')` → ValueError. |

**Score:** 5/5 truths verified (0 behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/basis_mod.rs` | `constant_basis` + `smooth_basis_aic` added | VERIFIED | Both functions present, substantive (not stubs), and registered in `register()` at lines 762 and 771. |
| `src/smoothing_mod.rs` | `optim_bandwidth` AIC input arm + explicit AIC output arm | VERIFIED | `"aic" => CvCriterion::Aic` at line 196; `CvCriterion::Aic => "aic"` at line 213; wildcard fallback retained at line 215. |
| `tests/test_basis_smoothing.py` | 11 tests covering all 3 tasks | VERIFIED | 11 tests, all pass in 0.93s. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `constant_basis` binding | `fdars_core::basis::constant_basis` | `numpy1d_to_vec` → infallible core call → `vec_to_numpy1d` | VERIFIED | `basis_mod.rs:29-30` |
| `smooth_basis_aic` binding | `fdars_core::smooth_basis::smooth_basis_aic` | `numpy2d_to_fdmatrix`, `parse_smooth_basis_type` → `Option::None → PyValueError` → PyDict field map | VERIFIED | `basis_mod.rs:465-487`; identical to GCV binding except the core call |
| `optim_bandwidth` input `"aic"` | `fdars_core::smoothing::CvCriterion::Aic` | string match arm at `smoothing_mod.rs:196` | VERIFIED | Input dispatch wired; error message updated to list all three |
| `CvCriterion::Aic` output | `"aic"` in result dict | explicit match arm at `smoothing_mod.rs:213` | VERIFIED | Replaces Phase-30 `_ => "unknown"` stopgap for this variant |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `constant_basis` return | `result` (Vec of 1.0s) | `fdars_core::basis::constant_basis` — infallible, length-of-grid | Yes | FLOWING |
| `smooth_basis_aic` dict fields | `fitted`, `coefficients`, `edf`, `gcv`, `aic`, `bic`, `nbasis` | `fdars_core::smooth_basis::smooth_basis_aic` returns `Option<SmoothBasisResult>` | Yes — `aic=-3390.76`, `edf=7.97`, `fitted.shape==(35,365)` | FLOWING |
| `optim_bandwidth` result | `h_opt`, `criterion`, `value` | `fdars_core::smoothing::optim_bandwidth` returns `OptimBandwidthResult` | Yes — `h_opt=0.0956` (positive finite, grid-search result) | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `constant_basis(linspace(0,1,20))` returns all-ones shape `(20,)` | Python inline | `shape==(20,), allclose(1.0)` | PASS |
| `constant_basis(array([]))` returns `(0,)` without panic | Python inline | `shape==(0,)` | PASS |
| `optim_bandwidth(criterion='aic')` returns finite `h_opt` and `criterion=='aic'` | Python inline | `h_opt=0.0956, criterion='aic'` | PASS |
| `optim_bandwidth(criterion='gcv')` still returns `criterion=='gcv'` | Python inline | `criterion='gcv'` | PASS |
| `optim_bandwidth(criterion='banana')` raises ValueError | Python inline | `ValueError: criterion must be 'cv', 'gcv', or 'aic'` | PASS |
| `smooth_basis_aic` returns dict with all 7 keys on Canadian Weather | Python inline | All keys present, `aic=-3390.76` | PASS |
| `smooth_basis_aic(n_basis=1)` raises ValueError | Python inline | `ValueError: smooth_basis_aic failed` | PASS |
| `basis_nbasis_cv(criterion='aic')` returns `criterion=='aic'` | Python inline | `optimal_nbasis=8, criterion='aic'` | PASS |
| `basis_nbasis_cv(criterion='banana')` raises ValueError | Python inline | ValueError raised | PASS |
| Full `tests/test_basis_smoothing.py` (11 tests) | `pytest -q` | `11 passed in 0.93s` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| BASIS-01 | 33-01-PLAN.md | `fdars.basis.constant_basis(argvals)` → all-ones ndarray | SATISFIED | Live smoke check + 3 pytest tests pass; registered in `basis_mod.rs:762` |
| BASIS-02 | 33-01-PLAN.md | `fdars.basis.smooth_basis_aic(...)` → dict; `basis_nbasis_cv(criterion="aic")` → criterion reported | SATISFIED | Live smoke check + 4 pytest tests pass; Rust dispatch at lines 537/566 |
| BASIS-03 | 33-01-PLAN.md | `fdars.smoothing.optim_bandwidth(criterion="aic")` → sane bandwidth; output arm reports `"aic"` | SATISFIED | Live smoke check + 3 pytest tests pass; Rust at lines 196/213 |

All three requirements marked `[x] Complete` in REQUIREMENTS.md traceability table, mapped to Phase 33.

### Anti-Patterns Found

None. Scan of `src/basis_mod.rs`, `src/smoothing_mod.rs`, `tests/test_basis_smoothing.py`:
- No `TBD`, `FIXME`, `XXX`, `TODO`, `HACK`, or `PLACEHOLDER` markers.
- No bare `.unwrap()` on fallible paths (the two `.unwrap()` present — `checked_div` + `PyArray2::from_vec2` — are on infallible or pre-validated paths in pre-existing code, not in Phase-33 additions).
- No stub patterns (return null/empty/placeholder).
- `cargo fmt --check` exits clean.
- `cargo clippy -- -D warnings` exits clean (5.21s compile, `Finished dev profile`).

### Informational Note: BASIS-02 Placement Deviation

REQUIREMENTS.md prose for BASIS-02 says `fdars.smoothing.smooth_basis_aic(...)`. The implementation places `smooth_basis_aic` in `fdars.basis` (beside its GCV twin `smooth_basis_gcv`), not `fdars.smoothing`. This is a documented Claude's-Discretion decision recorded in both `33-CONTEXT.md` and `33-01-PLAN.md` under "Placement decision": the closest existing analog `smooth_basis_gcv` lives in `fdars.basis`, so the AIC twin follows. The function is fully wired and functional at `fdars.basis.smooth_basis_aic`. This note is informational only — not a gap.

### Human Verification Required

None. All must-haves are verifiable programmatically and confirmed by live smoke checks and the pytest suite.

---

_Verified: 2026-08-17_
_Verifier: Claude (gsd-verifier)_
