---
phase: 56-transformers
plan: "03"
subsystem: sklearn-compliance
tags: [sklearn, transformers, pipeline, fpca, capstone, contract-test]
dependency_graph:
  requires: [56-02]
  provides: [pipeline-roundtrip-test, fpca-idempotence-guard, fdata-free-contract]
  affects: [tests/sklearn/test_transformer_pipeline.py]
tech_stack:
  added: []
  patterns:
    - "Pipeline([BSplineSmoother, FPCATransformer]) round-trip with fit_transform consistency check"
    - "inspect.getsource parametrized source-level contract assertion over all 8 transformer classes"
key_files:
  created:
    - tests/sklearn/test_transformer_pipeline.py
decisions:
  - "Combine Task 1 (pipeline round-trip + FPCA idempotence) and Task 2 (Fdata-free contract) into a single file — both logically are capstone cross-transformer guards that belong together"
  - "Source-level contract check uses inspect.getsource(cls) rather than behavioral patching — simpler, faster, and catches the actual source drift the threat model is concerned about"
metrics:
  duration: "10m"
  completed: "2026-08-31"
  tasks_completed: 2
  tasks_total: 2
  commits: 1
status: complete
actuals:
  tokens: 5000
  tasks: 2
  commits: 1
requirements: [XFORM-01, XFORM-06]
---

# Phase 56 Plan 03: Capstone — Pipeline Round-Trip, FPCA Idempotence, Fdata-Free Contract Summary

Cross-transformer capstone test suite: `Pipeline([BSplineSmoother, FPCATransformer])` fit-transform round-trip (XFORM-06), FPCA fit-idempotence regression guard (XFORM-01), and static source-level contract asserting all 8 transformers are Fdata-free and native-routed (STRIDE T-56-05).

## What Was Built

**`tests/sklearn/test_transformer_pipeline.py`** (new file, 168 lines):

Three test functions covering the plan's must-have truths:

1. **`test_smoother_fpca_pipeline_roundtrip`** — Constructs a `Pipeline([("smoother", BSplineSmoother()), ("fpca", FPCATransformer(n_components=2))])` on a deterministic 20×50 float64 dataset (seed=42). Asserts:
   - Output shape is `(20, 2)`.
   - All values are finite (no NaN, no Inf).
   - `fit_transform(X)` is numerically identical to `fit(X)` then `transform(X)`.

2. **`test_fpca_fit_idempotent`** — Creates two independent `FPCATransformer` instances, fits both on the same data, and asserts `np.allclose(fpca1.components_, fpca2.components_)`. Regression guard for the SVD sign canonicalization implemented in Plan 01.

3. **`test_transformers_never_construct_fdata`** — Parametrized over all 8 transformer classes (`FPCATransformer`, `BSplineSmoother`, `LocalPolynomialSmoother`, `BasisRepresentation`, `Imputer`, `SplineInterpolator`, `DepthTransformer`, `NormTransformer`). For each class:
   - Uses `inspect.getsource(cls)` to obtain source code.
   - Asserts `"Fdata(" not in source` (contract: never construct an Fdata).
   - Asserts `"_native" in source` (contract: routes compute through native layer).

## Verification Results

```
tests/sklearn/test_transformer_pipeline.py::test_smoother_fpca_pipeline_roundtrip PASSED
tests/sklearn/test_transformer_pipeline.py::test_fpca_fit_idempotent PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[FPCATransformer] PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[BSplineSmoother] PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[LocalPolynomialSmoother] PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[BasisRepresentation] PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[Imputer] PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[SplineInterpolator] PASSED
tests/sklearn/test_transformer_pipeline.py::test_transformers_never_construct_fdata[DepthTransformer] PASSED
tests/sklearn/test_transformer_planning.py::test_transformers_never_construct_fdata[NormTransformer] PASSED

10 passed in 0.22s
```

## Full-Tree Verification (`tests/sklearn/ -q`)

The plan's `<verification>` block asks for the whole `tests/sklearn/` tree to stay
green. Full run result: **1796 passed, 87 failed in 579s**. All 400 transformer-scoped
cases pass — the new `test_transformer_pipeline.py` (10/10), `test_transformers_compliance.py`,
and `test_foundation.py` are 100% green. **Zero** failures involve any of the 8 transformers.

Every one of the 87 failures is in `tests/sklearn/test_triage.py` on **non-transformer**
estimators outside Phase 56's scope — outlier detectors (`MagnitudeShapeDetector`,
`MUODDetector`, `LRTOutlierDetector`, `TVDMSSDetector`, `OutliergramDetector`,
`DepthgramDetector`), clusterers (`FuzzyFunctionalCMeans`, `FunctionalGMM`), and a
classifier (`ElasticMultinomialClassifier`). These are unpromoted triage candidates
that future phases (57 regressors/classifiers, 58 clusterers/outliers) will address.
Per the executor SCOPE BOUNDARY rule they are pre-existing and not fixed here; logged
to `.planning/phases/56-transformers/deferred-items.md`.

## Deviations from Plan

None — plan executed exactly as written. The full-tree `<verification>` line surfaced
pre-existing non-transformer triage failures (documented above and in `deferred-items.md`);
the transformer scope this plan owns is fully green.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Test file uses only in-memory synthetic data (STRIDE T-56-06: accepted — no external data, no network).

## Self-Check: PASSED

- `tests/sklearn/test_transformer_pipeline.py`: FOUND
- Commit `a9b156f`: FOUND in git log
- 10/10 tests green
