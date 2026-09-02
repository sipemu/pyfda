---
phase: 67-functional-time-series-fts
verified: 2026-09-02T20:55:00Z
status: passed
resolved: 2026-09-02T21:20:00Z
score: 3/3 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps_closed:
  - truth: "Full suite passes with zero new failures (regression gate)"
    status: resolved
    resolution: "Gap closed by plan 67-05 (commit 4d2a0cc): the stale FND-02 guard (test_fdars_init_unchanged) was refactored from a byte-freeze git-diff of python/fdars/__init__.py into an invariant check (Phase-55 baseline _submodule_names ⊆ current + every submodule registers). User-chosen approach (refactor to invariant). Full suite re-run independently: 5366 passed, 10 skipped, 0 failed. The additive 'fts' registration is now correctly permitted; robust to Phases 68–71 submodule additions."
---

# Phase 67: Functional Time Series (`fdars.fts`) Verification Report

**Phase Goal:** Users can fit and forecast functional time series and compute time-series diagnostics through a new importable `fdars.fts` submodule.
**Verified:** 2026-09-02T20:55:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `import fdars.fts` works; ftsm fit + single- and multi-step forecasts return a transposition-correct PyDict on non-square (n_obs ≠ n_points) input | ✓ VERIFIED | `.venv/bin/python -c "import fdars.fts"` → OK; 27/27 tests pass including `test_ftsm_shapes_non_square` (mean=(25,), rotation=(25,3), scores=(40,3), fitted=(40,25)); live spot-check confirmed |
| 2 | Users can compute functional_acf/functional_pacf, run stationarity_test, compute long_run_covariance — deterministic where upstream fn takes a seed | ✓ VERIFIED | All 5 functions callable; tests cover seed-determinism (`np.array_equal` on repeated calls), symmetry of cov_matrix within 1e-10; 27/27 tests pass |
| 3 | Users can call fplsr and dpca (and dpca_reconstruct), each returning a documented PyDict | ✓ VERIFIED | fplsr, dpca, dpca_reconstruct all callable; tests assert forecast/fitted/scores shapes, monotone reconstruction_error, valid_range tuple; 27/27 tests pass |

**Score:** 3/3 truths verified (0 present, behavior-unverified)

### Full-Suite Regression Gate

| Test | Result |
|------|--------|
| `pytest tests/test_fts.py -q` | 27 passed — ALL GREEN |
| `pytest tests/ -q` (full suite) | **1 failed**, 5365 passed, 10 skipped |

**Full-suite result: 1 FAILED — `tests/sklearn/test_foundation.py::test_fdars_init_unchanged`**

This is a regression introduced by Phase 67. The test was passing at pre-Phase-67 HEAD (commit `4a9e21c`); Phase 67 commit `68a2991` modified `python/fdars/__init__.py` (adding `"fts"` to `_submodule_names`), causing the FND-02 git-diff guard to fire.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/fts_mod.rs` | New PyO3 submodule with register() and all 13 #[pyfunction]s | ✓ VERIFIED | 741 lines; all 13 functions defined and registered; substantive implementations with docstrings and correct PyDict assembly |
| `src/lib.rs` | Registers fts submodule via register_submodule! | ✓ VERIFIED | Line 29: `mod fts_mod;`; line 64: `register_submodule!(m, "fts", fts_mod::register)` |
| `python/fdars/__init__.py` | Adds "fts" to _submodule_names | ✓ VERIFIED | Line 56: `"fts",  # Phase 67 — Functional Time Series (FTSM fit/forecast, ACF, stationarity, DPCA)` |
| `tests/test_fts.py` | Non-square fixture + 27 tests covering all 3 SCs | ✓ VERIFIED | N=40, M=25, `assert N != M` guard; 27 tests covering ftsm, forecast family, diagnostics family, spectral/DR family |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `python/fdars/__init__.py` | `fdars._native.fts` | `_submodule_names` tuple + for-loop registration | ✓ WIRED | `"fts"` present at line 56; `import fdars.fts` verified live |
| `src/lib.rs` | `src/fts_mod.rs` | `mod fts_mod;` + `register_submodule!(m, "fts", fts_mod::register)` | ✓ WIRED | Lines 29 and 64 confirmed |
| `src/fts_mod.rs::register()` | All 13 #[pyfunction]s | `m.add_function(wrap_pyfunction!(...))` | ✓ WIRED | All 13 wrap_pyfunction! lines confirmed in register() |
| `ftsm_result_to_dict` helper | `ftsm` and `ftsm_update` | Private fn called by both | ✓ WIRED | DRYs 7-key PyDict assembly; code confirms reuse |
| `dpca_result_to_dict` helper | `dpca` and `dpca_reconstruct` | Private fn called by both | ✓ WIRED | DRYs DpcaResult PyDict assembly; code confirms reuse |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `fts_mod.rs::ftsm` | result struct | `fdars_core::fts::ftsm(&mat, ncomp, &av)` | Yes — native Rust computation | ✓ FLOWING |
| `fts_mod.rs::ftsm_forecast` | forecast matrix | `fdars_core::fts::ftsm_forecast(&fit, h, &av)` | Yes — combined-function pattern | ✓ FLOWING |
| `fts_mod.rs::long_run_covariance` | cov_matrix | `fdars_core::fts::long_run_covariance` + `FdMatrix::from_column_major` reshape | Yes — col-major reshape applied correctly | ✓ FLOWING |
| `fts_mod.rs::spectral_density` | re/im per-freq | `fdars_core::fts::spectral_density` + per-freq `FdMatrix::from_column_major` | Yes — per-frequency reshape applied | ✓ FLOWING |
| `fts_mod.rs::dpca_reconstruct` | reconstruction | `fdars_core::fts::dpca` (internal fit) + `fdars_core::fts::dpca_reconstruct` | Yes — combined-function pattern | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `import fdars.fts` works | `.venv/bin/python -c "import fdars.fts; print('import OK')"` | `import OK` | ✓ PASS |
| All 13 functions present and callable | Python check via `getattr`/`callable` on all 13 names | `All 13 present and callable: True` | ✓ PASS |
| Phase test suite (27 tests) | `.venv/bin/pytest tests/test_fts.py -q` | `27 passed in 2.54s` | ✓ PASS |
| Transposition correct on non-square fixture | Live Python check mean=(25,), rotation=(25,3), scores=(40,3), fitted=(40,25) | All shapes correct: True | ✓ PASS |
| Full suite regression gate | `.venv/bin/pytest tests/ -q` | **1 failed**, 5365 passed, 10 skipped (145s) | ✗ FAIL |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FTS-01 | 67-01, 67-02 | fdars.fts submodule importable; ftsm + forecast/multistep/update returning transposition-correct PyDict | ✓ SATISFIED | SC1 VERIFIED; import works; 27 tests pass; non-square shapes confirmed |
| FTS-02 | 67-03 | functional_acf/pacf, stationarity_test, long_run_covariance exposed with deterministic seeds | ✓ SATISFIED | SC2 VERIFIED; all 4 functions callable; seed-determinism tests pass; cov_matrix symmetry test passes |
| FTS-03 | 67-02, 67-04 | fplsr and dpca (+ dpca_reconstruct) returning documented PyDicts | ✓ SATISFIED | SC3 VERIFIED; fplsr returns {forecast,fitted,ncomp}; dpca returns {filters,scores,eigenvalues,valid_range,...}; dpca_reconstruct returns merged dict with reconstruction; 27 tests pass |

All three requirement IDs from PLAN frontmatter (FTS-01, FTS-02, FTS-03) are accounted for. REQUIREMENTS.md traceability table marks all three Complete for Phase 67. No orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers found in any phase-modified file | — | — | — | — |

No debt markers, no stub patterns, no hardcoded empty returns found in `src/fts_mod.rs` or `tests/test_fts.py`.

### Human Verification Required

None — all three success criteria are mechanically verifiable and confirmed by live test execution.

### Gaps Summary

**One gap blocking clean close:**

The full test suite (`pytest tests/ -q`) reports **1 failed**: `tests/sklearn/test_foundation.py::test_fdars_init_unchanged`.

**Root cause:** The FND-02 guard diffs `python/fdars/__init__.py` against the Phase 55 base commit (`bf1a60638c`). Phase 67 legitimately added two lines to that file (the `"fts"` submodule name and a docstring bullet) in commit `68a2991`. This modification is the only correct way to make `import fdars.fts` resolve via the existing submodule registration loop. The FND-02 test was not updated to reflect the new expected state of the file.

**Nature of the failure:** The guard's intent was to verify Phase 55 did not break the init file. The guard's implementation (frozen git diff against a specific commit) is fragile — any new submodule addition will break it. Phase 67 is the first to trigger it.

**Resolution options (any one suffices):**
1. Update `PHASE_55_BASE` in `test_fdars_init_unchanged` to a commit hash that includes the Phase 67 `__init__.py` change (e.g., `68a2991` or later), OR
2. Change the test to assert specific properties of `__init__.py` (e.g., imports cleanly, `_submodule_names` contains the expected list) rather than a frozen git-diff assertion, OR
3. Accept a documented waiver: the FND-02 guard is understood to be superseded now that multiple phases legitimately extend `_submodule_names`.

The phase **goal** (fdars.fts importable, all 13 functions bound, 3 SCs met, 27 tests all green) is fully achieved. The gap is a stale foundation-contract test that did not account for the submodule extension pattern used by Phase 67.

---

_Verified: 2026-09-02T20:55:00Z_
_Verifier: Claude (gsd-verifier)_
