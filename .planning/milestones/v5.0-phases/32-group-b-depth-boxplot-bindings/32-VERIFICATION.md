---
phase: 32-group-b-depth-boxplot-bindings
verified: 2026-08-17T00:00:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 32: Group B — Depth/Boxplot Bindings Verification Report

**Phase Goal:** Users can compute unified functional self-depth and a López-Pintado–Romo functional boxplot (median / central region / whiskers / flagged outliers) from the extended `fdars.depth` submodule, layout-correct across the numpy↔FdMatrix boundary.
**Verified:** 2026-08-17
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `fdars.depth.functional_depth(data, method=...)` returns `ndarray(n,)` for all four methods (`fraiman_muniz`, `band`, `modified_band`, `random_projection`) | ✓ VERIFIED | Live: all four shapes confirmed (12,). Tests: `TestFunctionalDepthShape` — 4 tests pass. |
| 2 | Unknown method string raises `ValueError` | ✓ VERIFIED | Live: `functional_depth(X, method='nope')` raised `ValueError: method must be 'fraiman_muniz', 'band', 'modified_band', or 'random_projection', got 'nope'`. Tests: `test_unknown_method_raises` passes. |
| 3 | `functional_depth(data, method='fraiman_muniz', scale=True)` equals `fraiman_muniz_1d(data, data, scale=True)` within tolerance | ✓ VERIFIED | Live: `np.allclose` asserted True. Tests: `TestFunctionalDepthCrossCheck` — 2 tests (scale=True, scale=False) pass. |
| 4 | `random_projection` with an explicit seed is byte-identical across two calls; `seed=None` also byte-identical across two calls | ✓ VERIFIED | Live: `np.array_equal` asserted True for both seed=7 and seed=None. Tests: `TestFunctionalDepthDeterminism` — 2 tests pass. |
| 5 | `fdars.depth.functional_boxplot(data, method=..., factor=1.5)` returns a 7-key dict `{median, central_lower, central_upper, whisker_lower, whisker_upper, outliers, depths}` | ✓ VERIFIED | Live: `set(res.keys())` verified against expected 7-key set. Tests: `TestFunctionalBoxplotDictContract::test_key_set` passes. |
| 6 | Band fields are 1-D ndarrays of length m; `depths` is a 1-D ndarray of length n; `outliers` is a Python list of ints with 0-based row indices in `[0, n)` | ✓ VERIFIED | Live: band fields shape (365,), depths shape (12,), outliers=[0, 3, 6, 11] (list of ints). Tests: `TestFunctionalBoxplotLayoutGuard` — 4 tests including transposition guard pass. |
| 7 | Degenerate inputs (empty data, <2 curves for band/boxplot, nproj=0, negative factor, unknown method) raise `ValueError` with `pytest.raises` coverage | ✓ VERIFIED | Tests: 5 `TestFunctionalDepthValueErrors` tests + 4 `TestFunctionalBoxplotValueErrors` tests — all pass. `cargo clippy -- -D warnings` exits 0 (wildcard arm, no `.unwrap()`). |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/depth_mod.rs` | Extended with `depth_method_from_str`, `functional_depth`, `functional_boxplot` | ✓ VERIFIED | All three present and substantive (lines 414-580). `functional_depth` registered at line 599; `functional_boxplot` at line 600. |
| `tests/test_depth.py` | 27 tests covering DEPTH-01 and DEPTH-02 | ✓ VERIFIED | 27 tests collected and passing in 0.34s. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `depth_method_from_str` (Python str, scale, nproj, seed) | `fdars_core::depth::DepthMethod` | Match arm with `_ => PyValueError` wildcard | ✓ WIRED | Lines 414-432. Wildcard arm confirmed; `clippy -D warnings` exits 0 (no non-exhaustive-match error). |
| `boxplot_result_to_pydict` — band fields `Vec<f64>` length m | `vec_to_numpy1d` | `dict.set_item(key, vec_to_numpy1d(py, r.<field>))` | ✓ WIRED | Lines 442-461. Five band fields + depths via `vec_to_numpy1d`; outliers via `Vec<i64>` → Python list. |
| `boxplot_result_to_pydict` — `outliers Vec<usize>` | Python list of ints | `.into_iter().map(|x| x as i64).collect::<Vec<i64>>()` | ✓ WIRED | Line 452-458. PyO3 converts `Vec<i64>` → Python list (not ndarray). |
| `fdars.depth` submodule | `functional_depth`, `functional_boxplot` | `m.add_function(wrap_pyfunction!(...))` in `register()` | ✓ WIRED | Lines 599-600. Both wired; `import fdars.depth; callable(fdars.depth.functional_depth)` confirmed live. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `functional_depth` | `result` | `fdars_core::depth::functional_depth(&d, m)` | Yes — real fdars-core computation | ✓ FLOWING |
| `functional_boxplot` | `result` | `fdars_core::depth::functional_boxplot(&d, m, factor)` | Yes — real fdars-core computation | ✓ FLOWING |
| boxplot `outliers` | `r.outliers` | `FunctionalBoxplotResult` field from core | Yes — live outliers=[0, 3, 6, 11] confirmed | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 4 methods return `ndarray(n,)` | `python -m pytest tests/test_depth.py -v` | 27 passed / 0 failed in 0.34s | ✓ PASS |
| fraiman_muniz cross-check vs legacy binding | Live `np.allclose` assertion | True | ✓ PASS |
| seed=7 and seed=None byte-identical reproducibility | Live `np.array_equal` assertion | True | ✓ PASS |
| 7-key dict contract + layout guard | Live assertion + `TestFunctionalBoxplotLayoutGuard` | band (365,), depths (12,), outliers list | ✓ PASS |
| Full test suite (no regressions) | `python -m pytest -q --ignore=tests/test_depth.py` | 495 passed, 4 skipped | ✓ PASS |
| `cargo fmt --check` | `cargo fmt --check` | exit 0 | ✓ PASS |
| `cargo clippy -- -D warnings` | `cargo clippy -- -D warnings` | exit 0 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DEPTH-01 | 32-01-PLAN.md | Unified string-dispatched `functional_depth` with `DepthMethod` dispatch and `#[non_exhaustive]` wildcard fallback | ✓ SATISFIED | `functional_depth` present, wired, tested (Truths 1-4); REQUIREMENTS.md marks Complete |
| DEPTH-02 | 32-01-PLAN.md | `functional_boxplot` returning 7-key dict with band fields as 1-D arrays and `outliers` as Python list of ints | ✓ SATISFIED | `functional_boxplot` present, wired, tested (Truths 5-7); REQUIREMENTS.md marks Complete |

**Traceability:** REQUIREMENTS.md lines 98-99 explicitly map both DEPTH-01 and DEPTH-02 to Phase 32 with status "Complete".

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None detected | — | — |

No `TBD`, `FIXME`, `XXX`, `unwrap()`, empty implementations, or placeholder returns found in `src/depth_mod.rs` or `tests/test_depth.py`.

### Human Verification Required

None. All observable truths were verified programmatically via live execution, behavioral spot-checks, and the full test suite.

### Gaps Summary

No gaps. All 7 must-have truths are VERIFIED by live codebase evidence:

- Both `functional_depth` and `functional_boxplot` are substantively implemented in `src/depth_mod.rs` (not stubs).
- Both are wired into the `depth` submodule's `register()` function and importable from Python.
- The data flows from real fdars-core 0.20 dispatch functions through the correct numpy conversion helpers.
- The layout correctness (band fields = length m, not n) is both enforced by core and covered by a transposition guard test with `n=12, m=365`.
- Commits 076e3e5 (RED) and 75d45a7 (GREEN) exist in git history confirming the TDD sequence.
- Full suite: 495 passed + 4 skipped (no regressions); depth suite: 27/27 passed.

---

_Verified: 2026-08-17_
_Verifier: Claude (gsd-verifier)_
