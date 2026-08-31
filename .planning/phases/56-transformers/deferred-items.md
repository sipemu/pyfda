# Deferred Items — Phase 56 (Transformers)

Discovered during 56-03 execution while running the full `tests/sklearn/` tree
for the plan's `<verification>` block (`.venv/bin/pytest tests/sklearn/ -q`).

## Pre-existing non-transformer triage failures (OUT OF SCOPE for Phase 56)

The full sklearn tree run reported **87 failed, 1796 passed**. Every failure is
in `tests/sklearn/test_triage.py` on **non-transformer** estimators that Phase 56
does not touch. All 8 transformers, `test_transformers_compliance.py`, and the new
`test_transformer_pipeline.py` are 100% green (400/400 transformer-scoped cases pass).

Failing estimators (belong to future phases — regressors/classifiers/clusterers/
outlier-detectors per the `_skeletons.py` phase plan):

| Estimator | Family | Failing checks (examples) |
|-----------|--------|---------------------------|
| MagnitudeShapeDetector | outlier | check_outliers_train, ... (4) |
| MUODDetector | outlier | check_outliers_train, check_fit2d_1feature (3) |
| LRTOutlierDetector | outlier | (3) |
| TVDMSSDetector | outlier | check_outliers_train (2) |
| OutliergramDetector | outlier | (2) |
| DepthgramDetector | outlier | check_outliers_train (2) |
| FuzzyFunctionalCMeans | clusterer | (1) |
| FunctionalGMM | clusterer | (1) |
| ElasticMultinomialClassifier | classifier | (1) |

These are **not regressions** — they are unpromoted triage candidates from
Phase 55's foundation that later phases (57 regressors/classifiers,
58 clusterers/outliers) will address. Per the executor SCOPE BOUNDARY rule,
they are not fixed here.
