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

| Estimator | Family | Failing checks (examples) | Status |
|-----------|--------|---------------------------|--------|
| MagnitudeShapeDetector | outlier | check_outliers_train, ... (4) | Resolved |
| MUODDetector | outlier | check_outliers_train, check_fit2d_1feature (3) | Resolved |
| LRTOutlierDetector | outlier | (3) | Resolved |
| TVDMSSDetector | outlier | check_outliers_train (2) | Resolved |
| OutliergramDetector | outlier | (2) | Resolved |
| DepthgramDetector | outlier | check_outliers_train (2) | Resolved |
| FuzzyFunctionalCMeans | clusterer | (1) | Resolved |
| FunctionalGMM | clusterer | (1) | Resolved |
| ElasticMultinomialClassifier | classifier | (1) | Resolved |

These are **not regressions** — they are unpromoted triage candidates from
Phase 55's foundation that later phases (57 regressors/classifiers,
58 clusterers/outliers) will address. Per the executor SCOPE BOUNDARY rule,
they are not fixed here.

## Resolution — all items RESOLVED by Phases 57–58

- **Status:** resolved

Recorded at v9.0 milestone close, 2026-09-02.

Every estimator listed above was promoted to a fully compliant wrapper by the
later phases that owned it (57 classifiers, 58 clusterers/outliers). Final
evidence, from Phase 58's compliance gate (`58-VERIFICATION.md`):

- All 28 wrapped estimators are `"PASS"` in `_coverage.TRIAGE_VERDICTS`; **zero
  PASS-WITH-FIXES**, and none of these 9 appear in `EXCLUDED_METHODS`.
- `test_compliance_gate.py` runs all 28 estimators × ~50 checks → **1387 checks
  pass, zero exemptions**.
- `test_outliers_compliance.py` → 283 `parametrize_with_checks` cases pass (6
  detectors × 47 checks); `test_classifiers_compliance.py` and
  `test_clusterers_compliance.py` green.
- Whole `tests/sklearn/` suite: **4294 passed, 0 failures**.

The rows below carry `Status = Resolved` so the milestone-close artifact audit no
longer treats them as open — they were superseded, not exempted.
