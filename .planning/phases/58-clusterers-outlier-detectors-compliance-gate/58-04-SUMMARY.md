---
phase: 58-clusterers-outlier-detectors-compliance-gate
plan: "04"
subsystem: sklearn-compliance
tags: [sklearn, compliance, ci, interop, capstone]
status: complete

dependency_graph:
  requires: ["58-03"]
  provides: ["COMPLY-01", "COMPLY-02"]
  affects: [".github/workflows/ci.yml", "tests/sklearn/"]

tech_stack:
  added: []
  patterns:
    - "parametrize_with_checks zero-exemption aggregate gate over all 28 wrapped estimators"
    - "FPCATransformer → RandomForestClassifier Pipeline (fdars → native sklearn interop)"
    - "sklearn-compliance CI job (matrix Python 3.9–3.14, [sklearn] extra installed)"

key_files:
  created:
    - tests/sklearn/test_compliance_gate.py
    - tests/sklearn/test_interop.py
  modified:
    - tests/sklearn/test_triage.py
    - .github/workflows/ci.yml

decisions:
  - "test_triage.py reconcile strategy: update estimator list to battery-valid hyperparameters (ncomp=10, n_components=10, contamination=0.1) rather than retire the file — keeps secondary regression check, other references intact"
  - "test_compliance_gate.py is the authoritative COMPLY-01 gate (primary); test_triage.py is a secondary regression check"
  - "sklearn-compliance CI job mirrors test-python structure but installs .[sklearn] and runs tests/sklearn/ only; existing test-python job unchanged (importorskip on sklearn)"

metrics:
  duration: "~5 minutes"
  completed: "2026-09-01"
  tasks: 3
  commits: 3

estimate:
  tokens: 52000

actuals:
  tokens: 14000
  tasks: 3
  commits: 3
---

# Phase 58 Plan 04: Compliance Gate Capstone Summary

**One-liner:** Full-matrix parametrize_with_checks gate over all 28 wrapped estimators locked with zero exemptions (COMPLY-01); FPCATransformer → RandomForestClassifier Pipeline interop proven (COMPLY-02); sklearn-compliance CI job wired across Python 3.9–3.14.

## What Was Built

### Task 1: Aggregate compliance gate + reconcile test_triage.py

Created `tests/sklearn/test_compliance_gate.py` as the authoritative COMPLY-01 gate:
- `_ALL_WRAPPED` list: all 28 wrapped estimators with battery-valid hyperparameters (`ncomp=10` / `n_components=10` for classifiers/regressors, `contamination=0.1` for all six detectors, `n_bootstrap=50` for `LRTOutlierDetector`, `n_clusters=2` for clusterers).
- `test_full_matrix_compliance`: `@parametrize_with_checks(_ALL_WRAPPED)` with body `check(estimator)` — zero exemptions, zero `xfail`, zero `skip`. Runs ~1400 checks total.
- `test_no_pass_with_fixes_remaining`: asserts `TRIAGE_VERDICTS` has zero `PASS-WITH-FIXES` values among wrapped estimators and exactly 28 clean-`PASS` entries.
- Module-level assertion: `len(_ALL_WRAPPED) == 28`.

Reconciled `tests/sklearn/test_triage.py`:
- Updated module docstring: replaced "intentionally does NOT assert all-green" language with Phase 58 closure note explaining all 28 are `PASS` and the authoritative gate is `test_compliance_gate.py`.
- Updated `_ALL_SKELETONS`: changed `ncomp=1`/`n_components=1` to `ncomp=10`/`n_components=10` for classifiers and regressors; added `contamination=0.1` to all six outlier detectors; annotated former EXCLUDE-predicted entries as now PASS.
- Updated `test_sklearn_triage` docstring: reflects all-green status; original triage purpose documented in history note.
- Decision: retained `test_triage.py` rather than deleting it — other docs and CI references exist; it now serves as a secondary regression check over the same 28 estimators.

Result: `pytest tests/sklearn/test_compliance_gate.py tests/sklearn/test_triage.py -q` → **2773 passed, 0 failed**.

### Task 2: Interop test — FPCATransformer → RandomForestClassifier Pipeline (COMPLY-02)

Created `tests/sklearn/test_interop.py`:
- `test_fpca_to_random_forest_pipeline()`: builds a 30-curve two-class dataset (class 0 = Gaussian noise, class 1 = noise +3.0 shift on a 20-point grid; `RandomState(42)`).
- Fits `Pipeline([("fpca", FPCATransformer(n_components=5)), ("rf", RandomForestClassifier(n_estimators=20, random_state=0))])`.
- Asserts: `predict` shape `(n_obs,)`; all predicted labels in `set(y)`; `score` returns `float` in `[0.0, 1.0]`.
- COMPLY-02 proven: FPCATransformer emits plain float64 ndarray scores; RandomForestClassifier receives them as standard 2D features — no `Fdata` objects cross the boundary.

Result: `pytest tests/sklearn/test_interop.py -q` → **1 passed**.

### Task 3: Wire the [sklearn] compliance job into CI

Added `sklearn-compliance` job to `.github/workflows/ci.yml`:
- `strategy.matrix.python-version: ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]` with `fail-fast: false`.
- Mirrors `test-python` structure: checkout + `dtolnay/rust-toolchain@stable` + `Swatinem/rust-cache@v2` (key: `sklearn-pyX.Y`) + `actions/setup-python@v5`.
- Installs: `maturin numpy pandas pytest` → `maturin develop --release` → `pip install -e ".[sklearn]"` (triggers version marker: `scikit-learn<1.7` on Python 3.9, current on 3.10+; shim spans sklearn 1.3→1.8).
- Runs: `pytest tests/sklearn/ -v` (the full compliance tree: test_compliance_gate, test_triage, test_interop, all per-family suites, test_coverage, test_foundation, test_go_no_go, test_predictive_pipeline, test_transformer_pipeline).
- The existing `test-python` job is unchanged: it runs `pytest tests/ -v` without `.[sklearn]`, and `conftest.py`'s `pytest.importorskip("sklearn")` gates the whole `tests/sklearn/` subtree — no failures.

YAML validation: `python -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/ci.yml')); j=d['jobs']['sklearn-compliance']; ..."` → OK.

## test_triage.py Reconcile Decision

**Strategy chosen: update parameters, retain file as secondary check.**

`test_triage.py` was intentionally non-asserting (well, it does assert via `check(estimator)` but was running estimators with `ncomp=1`/`n_components=1` which fail `check_classifiers_train` / `check_regressors_train`). The failures were "informative" during triage (Phase 55) but became noise after all candidates were fixed in Phases 56-58.

The reconcile approach updates the hyperparameters to match the per-family compliance suites rather than deleting the file:
- Rationale: `test_triage.py` is the only file that runs ALL 28 estimators in a single `parametrize_with_checks` call outside of `test_compliance_gate.py`. Keeping it as a secondary check provides defence-in-depth.
- `test_compliance_gate.py` is designated the authoritative gate (COMPLY-01).
- Before fix: **18 failures** (ncomp=1 failing `check_classifiers_train`, `check_regressors_train` for FPCRegressor, RobustFPCRegressor, GLMRegressor, FPCLDAClassifier, FPCQDAClassifier, FPCKNNClassifier — each with 3 variants).
- After fix: **0 failures**.

## Verification Results

```
pytest tests/sklearn/ -q
4293 passed, 120 warnings in 16.83s
```

All 4293 checks across the full `tests/sklearn/` tree pass. This includes:
- `test_compliance_gate.py`: ~1400 checks (28 estimators × ~50 checks each)
- `test_triage.py`: ~1400 checks (same 28 estimators, secondary check)
- `test_interop.py`: 1 check (COMPLY-02)
- All per-family compliance suites
- `test_coverage.py`, `test_foundation.py`, `test_go_no_go.py`, `test_predictive_pipeline.py`, `test_transformer_pipeline.py`

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Hash | Task | Description |
|------|------|-------------|
| d8b72ad | Task 1 | feat(58-04): aggregate compliance gate + reconcile test_triage.py |
| 24219b6 | Task 2 | feat(58-04): interop test FPCATransformer → RandomForestClassifier (COMPLY-02) |
| c760b52 | Task 3 | chore(58-04): wire sklearn-compliance CI job across Python 3.9–3.14 matrix |

## Self-Check: PASSED

- [x] `tests/sklearn/test_compliance_gate.py` exists and has 2 test functions
- [x] `tests/sklearn/test_interop.py` exists and has 1 test function
- [x] `.github/workflows/ci.yml` has `sklearn-compliance` job with Python 3.9–3.14 matrix
- [x] `tests/sklearn/test_triage.py` updated (docstring + hyperparameters)
- [x] `pytest tests/sklearn/ -q` → 4293 passed, 0 failed
- [x] d8b72ad, 24219b6, c760b52 exist in git log
- [x] `import fdars` still works (version 0.4.0)
- [x] TRIAGE_VERDICTS: 28 PASS, 0 PASS-WITH-FIXES (asserted by test_no_pass_with_fixes_remaining)
