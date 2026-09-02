---
phase: 55-compliance-triage-foundation
plan: "01"
subsystem: sklearn-layer
tags: [sklearn, fpca, base-class, compat-shim, triage, tracer]
dependency_graph:
  requires: []
  provides:
    - python/fdars/sklearn/__init__.py
    - python/fdars/sklearn/_base.py
    - python/fdars/sklearn/_coverage.py
    - python/fdars/sklearn/_skeletons.py (FPCATransformer)
    - tests/sklearn/conftest.py
    - tests/sklearn/test_foundation.py
    - tests/sklearn/test_triage.py
  affects:
    - pyproject.toml (new [sklearn] extra + scikit-learn in [dev])
tech_stack:
  added:
    - scikit-learn>=1.3 (optional extra [sklearn]; dev dependency)
  patterns:
    - deferred-import gate (mirrors fdars.mcp / fdars.advisor)
    - hand-rolled validate_data + Tags-API compat shim (sklearn 1.3-1.8)
    - SVD sign canonicalization for idempotent FPCA
    - parametrize_with_checks triage harness (fail-per-check, not fail-fast)
key_files:
  created:
    - python/fdars/sklearn/__init__.py
    - python/fdars/sklearn/_base.py
    - python/fdars/sklearn/_coverage.py
    - python/fdars/sklearn/_skeletons.py
    - tests/sklearn/conftest.py
    - tests/sklearn/test_foundation.py
    - tests/sklearn/test_triage.py
  modified:
    - pyproject.toml
decisions:
  - "Hand-rolled shim in _base.py covers sklearn 1.3-1.8 without sklearn-compat (SUS-rated)"
  - "Python-version markers on [sklearn] and [dev] extras so 3.9 uses <1.7 cap, 3.10+ uses >=1.3"
  - "_BaseFdarsEstimator._sign_canonicalize is a @staticmethod (not module-level function)"
  - "FPCATransformer verdict: PASS (47/47 parametrize_with_checks checks green on sklearn 1.8.0)"
metrics:
  duration_minutes: 6
  completed_date: "2026-08-31"
  tasks_completed: 3
  commits: 3
status: complete
actuals:
  tokens: 18500
  tasks: 3
  commits: 3
---

# Phase 55 Plan 01: [sklearn] Extra + Gated Subpackage + FPCATransformer Summary

One-liner: JWT-style gated `fdars.sklearn` subpackage with hand-rolled sklearn 1.3-1.8 shim and production FPCATransformer passing all 47 `parametrize_with_checks` checks on sklearn 1.8.0.

## What Was Built

The complete Phase 55 Plan 01 tracer: the `[sklearn]` optional extra, the gated `python/fdars/sklearn/` subpackage (mirroring `fdars.mcp`/`fdars.advisor`), the shared `_BaseFdarsEstimator` base class with hand-rolled compat shim, the `_coverage.py` EXCLUDED_METHODS registry pre-seeded with 13 structural pre-excludes, and the production `FPCATransformer` that passes the full `parametrize_with_checks` battery on sklearn 1.8.0.

**FPCATransformer triage verdict: PASS** - all 47 checks green with zero exemptions, confirmed viable-core FPCA member.

## Deviations from Plan

### Dev-Environment Reconciliation (orchestrator-noted, not bugs)

**1. [Rule 1 - Reconciliation] sklearn 1.8.0 on Python 3.14 (not 1.6)**
- **Found during:** Pre-execution environment check
- **Issue:** Orchestrator note documented that the dev venv runs sklearn 1.8.0 / Python 3.14, not 1.6 as the plan text implied. In sklearn 1.8: `_more_tags()`/`_get_tags()` are REMOVED (not just deprecated); `validate_data` is the only path; `__sklearn_tags__` is the only tags API.
- **Fix:** The hand-rolled shim in `_base.py` spans 1.3-1.8 correctly: `validate_data` public function (1.6+ primary path) with fallback to `_validate_data` private method (1.3-1.5); `_HAS_TAGS_DATACLASS` flag detected via `try: from sklearn.utils import Tags`; `__sklearn_tags__` overridden when Tags is available, `_more_tags()` defined only on the fallback branch. On 1.8.0, `_HAS_TAGS_DATACLASS=True` and `_more_tags` is never defined or called.
- **Shim branch active on 1.8.0:** validate_data public function path (1.6+); `_HAS_TAGS_DATACLASS=True`.

**2. [Rule 2 - Extra pin markers] Python-version markers on [sklearn] extra**
- **Found during:** Task 1 implementation
- **Issue:** Plan text specified flat `scikit-learn>=1.3,<1.7` but orchestrator note required python_version markers so Python >=3.10 (including the 3.14 dev env) can use current sklearn without the <1.7 cap.
- **Fix:** Two entries in both `[sklearn]` and `[dev]` extras:
  - `scikit-learn>=1.3,<1.7; python_version < '3.10'`
  - `scikit-learn>=1.3; python_version >= '3.10'`
  This keeps the Python 3.9 wheel valid while matching the 1.8 dev/test reality.

**3. [Rule 1 - Test strategy] Shim path test on installed version only**
- **Found during:** Task 2 implementation
- **Issue:** Plan success fact "exercises 1.3 and 1.6 paths" cannot be a live 1.3 run in a 1.8-only dev env.
- **Fix:** `test_validate_shim_sets_n_features_in` verifies the shim is active on the installed version by checking its side effect (`n_features_in_` is set after fit); `test_has_tags_dataclass_is_bool` verifies `_HAS_TAGS_DATACLASS` is a bool without hard-coding which branch is active; `test_hast_tags_consistent_with_sklearn_version` verifies the flag correctly reflects whether `Tags` is importable. These tests pass on any sklearn version from 1.3 to 1.8.

**4. [Rule 3 - TDD clarification] Task 3 TDD RED/GREEN collapse**
- **Found during:** Task 3 execution
- **Issue:** Task 3 is `tdd="true"` with FPCATransformer already implemented in Task 1. The RED phase (write failing test) was the act of creating `test_triage.py` before verifying it passes; since the FPCATransformer implementation was production-quality from the tracer task, the test immediately passed (GREEN without iterative fix cycles).
- **Fix:** Proceeded as specified - the test file creation IS the RED artifact, and the immediate PASS on 47/47 checks confirms the implementation was correct from the start.

## Verification Results

| Check | Result |
|-------|--------|
| `import fdars` with zero sklearn | PASS - no sklearn in sys.modules |
| `import fdars.sklearn` with sklearn absent | PASS - raises `ImportError` with `pip install fdars[sklearn]` |
| `git diff --quiet -- python/fdars/__init__.py` | PASS - returns 0 (file unchanged) |
| `pytest tests/sklearn/test_foundation.py` | PASS - 15/15 |
| `pytest tests/sklearn/test_triage.py` | PASS - 47/47 |
| `pytest tests/sklearn/` | PASS - 62/62 total |
| FPCATransformer check_fit_idempotent | PASS - SVD sign canonicalization holds |
| FPCATransformer check_estimators_dtypes | PASS - float32 accepted and upcast |
| FPCATransformer check_fit2d_1sample | PASS - ValueError with "n_samples=1" substring |
| FPCATransformer clone/get_params/set_params | PASS - verbatim storage round-trips |

## sklearn Environment Facts (for Plan 02 / Phase 56)

| Fact | Value |
|------|-------|
| sklearn version in dev env | 1.8.0 |
| Python version | 3.14.7 |
| Active shim branch | validate_data public function (1.6+ path) |
| _HAS_TAGS_DATACLASS | True (Tags dataclass available) |
| _more_tags() available | False (removed in 1.8) |
| FPCATransformer verdict | PASS (47/47 checks) |
| checks run | 47 via parametrize_with_checks |

## Key Architecture Decisions

1. **Hand-rolled shim NOT `sklearn-compat`:** `sklearn-compat` is SUS-rated per RESEARCH Package Legitimacy Audit; the 15-line hand-rolled shim is simpler, zero-dependency, and fully adequate.
2. **`_sign_canonicalize` is a `@staticmethod`:** implemented on `_BaseFdarsEstimator`, not as a module-level function; plan said "static method" which is what was implemented.
3. **FPCATransformer NEVER constructs Fdata:** calls `fdars._native.regression.fpca(X, argvals, n_comp)` directly with validated numpy arrays (FND-04).
4. **`argvals` stored verbatim:** `__init__` stores None / list / array unchanged; `_resolve_argvals(n_pts)` converts only at fit time. Required for clone/get_params round-trip.

## Known Stubs

None - FPCATransformer is a complete, production-quality implementation. TRIAGE_VERDICTS is intentionally empty (populated by Plan 03 after full triage run over ~30 candidates).

## Threat Surface Scan

No new network endpoints, auth paths, or trust boundary crossings. The sklearn layer adds numpy arrays as a new input surface — validated by `validate_data(dtype="numeric")` (NaN/inf rejection enforced by default) before any native call. T-55-01 (input tampering) and T-55-SC (scikit-learn legitimacy) are both mitigated per the plan threat register.

## Self-Check: PASSED

- `python/fdars/sklearn/__init__.py`: FOUND
- `python/fdars/sklearn/_base.py`: FOUND
- `python/fdars/sklearn/_coverage.py`: FOUND
- `python/fdars/sklearn/_skeletons.py`: FOUND
- `tests/sklearn/conftest.py`: FOUND
- `tests/sklearn/test_foundation.py`: FOUND
- `tests/sklearn/test_triage.py`: FOUND
- Commit `06d8919`: FOUND (feat(55-01): [sklearn] extra + gated subpackage)
- Commit `8ba5862`: FOUND (test(55-01): foundation contract tests)
- Commit `4fb2b2c`: FOUND (test(55-01): triage harness 47/47 PASS)
- `pytest tests/sklearn/` 62/62 PASS: CONFIRMED
- `git diff --quiet -- python/fdars/__init__.py` returns 0: CONFIRMED
