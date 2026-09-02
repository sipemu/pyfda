---
phase: 58-clusterers-outlier-detectors-compliance-gate
verified: 2026-09-01T12:00:00Z
status: passed
score: 14/14
behavior_unverified: 0
overrides_applied: 0
human_verification: []
---

# Phase 58: Clusterers & Outlier Detectors + Compliance Gate — Verification Report

**Phase Goal:** Ship the clusterer and outlier-detector families as fully compliant ClusterMixin/OutlierMixin estimators, then — with all five families present — lock the full-matrix compliance gate (COMPLY-01) and prove native-sklearn interop (COMPLY-02).
**Verified:** 2026-09-01T12:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | FunctionalKMeans is check_estimator-green ClusterMixin, deterministic under fixed random_state | VERIFIED | `test_clusterers_compliance.py::test_functional_kmeans_compliance` passes; `test_functional_kmeans_deterministic` passes with identical `labels_` on two fits with `random_state=7` |
| 2 | FuzzyFunctionalCMeans exposes integer `n_iter_` equal to `max_iter` (CLUS-02 / WR-03) | VERIFIED | `n_iter_=100`, `max_iter=100`, `isinstance(n_iter_, int)=True`; 139 compliance checks pass |
| 3 | FunctionalGMM exposes integer `n_iter_` equal to `max_iter` (CLUS-02 / WR-03) | VERIFIED | `n_iter_=200`, `max_iter=200`, `isinstance(n_iter_, int)=True`; full battery passes |
| 4 | All 6 outlier detectors pass full parametrize_with_checks battery with zero exemptions (OUT-01 / OUT-02) | VERIFIED | 283 parametrize_with_checks checks pass in `test_outliers_compliance.py` (6 detectors × 47 checks) |
| 5 | All 6 detectors score_samples is subset-invariant (score_samples(X[mask]) == score_samples(X)[mask]) | VERIFIED | Direct empirical check: all 6 return allclose=True; `check_methods_subset_invariance` passes in battery |
| 6 | All 6 detectors expose continuous decision_function = score_samples - offset_ | VERIFIED | All 6 return allclose=True for the alias invariant; `decision_function` inherited from `_BaseFdarsOutlierDetector` |
| 7 | All 6 detectors predict yields {-1, +1} via contamination-derived offset_ | VERIFIED | Direct check with X containing injected outliers: all 6 return both -1 and +1 |
| 8 | MUODDetector raises "n_features=1" ValueError before any native call | VERIFIED | ValueError confirmed with message "MUODDetector requires n_features > 1 (got n_features=1)"; `check_fit2d_1feature` passes |
| 9 | MagnitudeShapeDetector uses method-faithful MS-plot score (MO²+VO²), not pure band-depth; regression-guarded | VERIFIED | `_ms_score` stores `mu_`/`var_` from training; `test_magnitude_shape_distinct_from_band_depth` passes — confirmed different from DepthgramDetector on magnitude outliers |
| 10 | All 28 wrapped estimators PASS in `_coverage.TRIAGE_VERDICTS`; zero PASS-WITH-FIXES | VERIFIED | 28 PASS, 0 PASS-WITH-FIXES confirmed programmatically; `test_no_pass_with_fixes_remaining` passes |
| 11 | Whole `tests/sklearn/` suite green (COMPLY-01 gate) | VERIFIED | `pytest tests/sklearn/ -q` → 4294 passed, 120 warnings in 27.86s, 0 failures |
| 12 | Aggregate `test_compliance_gate.py` runs all 28 estimators × ~50 checks with zero exemptions | VERIFIED | 1387 checks pass; `len(_ALL_WRAPPED) == 28` assertion at module level |
| 13 | FPCATransformer → RandomForestClassifier Pipeline fits and predicts end-to-end (COMPLY-02) | VERIFIED | `test_interop.py::test_fpca_to_random_forest_pipeline` passes: shape (30,), labels in set(y), score in [0,1] |
| 14 | sklearn-compliance CI job wired across Python 3.9–3.14 matrix | VERIFIED | `.github/workflows/ci.yml` `sklearn-compliance` job: matrix `["3.9","3.10","3.11","3.12","3.13","3.14"]`, installs `.[sklearn]`, runs `pytest tests/sklearn/ -v`, `fail-fast: false` |

**Score:** 14/14 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/sklearn/_skeletons.py` | `_BaseFdarsOutlierDetector` with contamination/offset_/decision_function; all 6 detectors + 3 clusterers | VERIFIED | All classes present, substantive, wired; no stubs |
| `python/fdars/sklearn/_coverage.py` | All 28 TRIAGE_VERDICTS = "PASS"; EXCLUDED_METHODS structural-only; MappingProxyType read-only | VERIFIED | 28 PASS / 0 PASS-WITH-FIXES; `MappingProxyType` wrapping confirmed |
| `tests/sklearn/test_outliers_compliance.py` | 6 per-detector `@parametrize_with_checks` functions + MS regression guard | VERIFIED | 7 test functions; 283 checks pass |
| `tests/sklearn/test_clusterers_compliance.py` | 3 per-clusterer batteries + FunctionalKMeans determinism test | VERIFIED | 4 test functions; 139 checks pass |
| `tests/sklearn/test_compliance_gate.py` | `_ALL_WRAPPED` (28 estimators), `test_full_matrix_compliance`, `test_no_pass_with_fixes_remaining` | VERIFIED | 1387 checks pass; PASS-WITH-FIXES assertion green |
| `tests/sklearn/test_interop.py` | `test_fpca_to_random_forest_pipeline` (COMPLY-02) | VERIFIED | 1 test passes |
| `tests/sklearn/test_triage.py` | Reconciled to all-green with battery-valid parameters; docstring updated | VERIFIED | ~1400 checks pass; no ncomp=1 regressions |
| `.github/workflows/ci.yml` | `sklearn-compliance` job with Python 3.9–3.14 matrix, `.[sklearn]` install | VERIFIED | YAML parses; all required fields confirmed |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `_BaseFdarsOutlierDetector._set_offset` | all 6 detector `fit` methods | `self._set_offset(train_scores)` call at end of each `fit` | VERIFIED | Confirmed in code at lines 2622, 2714, 2855, 2962, 3073, 3174 |
| `MagnitudeShapeDetector._ms_score` | `score_samples` / `_score_samples_validated` | `self._ms_score(X, self.mu_, self.var_)` vs stored training stats | VERIFIED | Distinct from `modified_band_1d` surrogate used by others; regression guard passes |
| `modified_band_1d(X, self.X_fit_)` | 5 detectors (LRT/Outliergram/TVDMSS/MUOD/Depthgram) score_samples | subset-invariant depth call against stored `X_fit_` | VERIFIED | All 5 return allclose=True for subset-invariance |
| `FPCATransformer` | `RandomForestClassifier` | `Pipeline([("fpca",...), ("rf",...)])` — plain float64 ndarray | VERIFIED | No Fdata used; pipeline fits and predicts correctly |
| `test_compliance_gate._ALL_WRAPPED` | `TRIAGE_VERDICTS` | `test_no_pass_with_fixes_remaining` assertion | VERIFIED | 28 PASS, 0 PASS-WITH-FIXES enforced at test level |
| `FuzzyFunctionalCMeans.n_iter_` | `max_iter` | `self.n_iter_ = self.max_iter` in fit | VERIFIED | WR-03 resolved; `check_non_transformer_estimators_n_iter` passes |
| `FunctionalGMM.n_iter_` | `max_iter` | `self.n_iter_ = self.max_iter` in fit | VERIFIED | WR-03 resolved; battery passes |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `MagnitudeShapeDetector` | `score_samples` | `_ms_score(X, self.mu_, self.var_)` — mu_/var_ stored from training X | Yes | FLOWING |
| `LRTOutlierDetector` | `score_samples` | `_native.depth.modified_band_1d(X, self.X_fit_)` — X_fit_ stored at fit | Yes | FLOWING |
| `_BaseFdarsOutlierDetector` | `offset_` | `np.percentile(train_scores, 100.0 * contamination)` in `_set_offset` | Yes | FLOWING |
| `FuzzyFunctionalCMeans` | `n_iter_` | `self.max_iter` (native exposes no iteration count) | Yes (honest upper bound) | FLOWING |
| `test_compliance_gate` | `_ALL_WRAPPED` | All 28 estimator constructors imported from `_skeletons` | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Whole sklearn/ suite green (COMPLY-01) | `pytest tests/sklearn/ -q` | 4294 passed, 0 failed in 27.86s | PASS |
| Outlier detector compliance | `pytest tests/sklearn/test_outliers_compliance.py -q` | 283 passed in 1.12s | PASS |
| Clusterer compliance | `pytest tests/sklearn/test_clusterers_compliance.py -q` | 139 passed in 1.32s | PASS |
| Interop test (COMPLY-02) | `pytest tests/sklearn/test_interop.py -q` | 1 passed in 0.51s | PASS |
| Aggregate compliance gate | `pytest tests/sklearn/test_compliance_gate.py -q` | 1387 passed in 9.20s | PASS |
| MagnitudeShapeDetector subset invariance | Direct Python check | allclose=True; predict yields both -1, +1 | PASS |
| FunctionalKMeans determinism | `test_functional_kmeans_deterministic` | `labels_` identical across two fits | PASS |
| COMPLY-01 zero-PASS-WITH-FIXES gate | `test_no_pass_with_fixes_remaining` | 28 PASS, 0 PASS-WITH-FIXES | PASS |
| `import fdars` unchanged | `python -c "import fdars"` + git diff check vs bf1a606 | OK; `__init__.py` diff is empty | PASS |
| CI YAML validation | Python yaml.safe_load check | `sklearn-compliance` job valid; 3.14 matrix present | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CLUS-01 | 58-03 | FunctionalKMeans as check_estimator-green ClusterMixin, deterministic | SATISFIED | Compliance battery + determinism test both green |
| CLUS-02 | 58-03 | FuzzyFunctionalCMeans, FunctionalGMM as ClusterMixin with n_iter_ | SATISFIED | n_iter_=max_iter confirmed; batteries green |
| OUT-01 | 58-01, 58-02 | LRT/Outliergram/MagnitudeShape as OutlierMixin with decision_function + predict | SATISFIED | 283 compliance checks; subset-invariance verified |
| OUT-02 | 58-02 | TVDMSS/MUOD/Depthgram as OutlierMixin with synthesized decision_function | SATISFIED | All 3 pass `check_estimator` battery including `check_fit2d_1feature` (MUOD) |
| COMPLY-01 | 58-04 | All 28 estimators pass parametrize_with_checks CI job across Python 3.9–3.14 | SATISFIED | 4294 tests pass; CI job wired; 28/28 PASS in _coverage.py |
| COMPLY-02 | 58-04 | FPCATransformer scores → RandomForestClassifier in one Pipeline | SATISFIED | test_interop.py passes; Pipeline fits, predicts, scores correctly |

**Note on REQUIREMENTS.md checkboxes:** COMPLY-01 and COMPLY-02 still appear unchecked (`- [ ]`) in REQUIREMENTS.md, and the traceability table shows "Pending". This is a documentation lag — the implementation is fully verified. The ROADMAP.md also shows Phase 58 as "3/4 plans" (Plan 04 checkbox unchecked). Both are minor documentation artifacts requiring update but do not reflect missing implementation.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| No TBD/FIXME/XXX found | — | — | — | — |
| No stubs or hollow props found | — | — | — | — |
| No disabled tests found | — | — | — | — |

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| test_outliers_compliance.py | OUT-01, OUT-02 | 283 | 0 | No | Behavioral (parametrize_with_checks) | PASS |
| test_clusterers_compliance.py | CLUS-01, CLUS-02 | 139 | 0 | No | Behavioral + value-level determinism | PASS |
| test_compliance_gate.py | COMPLY-01 | 1388 | 0 | No | Behavioral + structural assertion | PASS |
| test_interop.py | COMPLY-02 | 1 | 0 | No | Behavioral (shape, labels, score range) | PASS |

**Disabled tests on requirements:** 0
**Circular patterns detected:** 0
**Insufficient assertions:** 0

### Decision Coverage

No CONTEXT.md decisions block to check. All key decisions from PLAN frontmatter are visible in the executed code:

- `contamination=0.1` (not "auto") — confirmed in all 6 detector `__init__` signatures
- `modified_band_1d(X, X_fit_)` for 5 detectors — confirmed in `score_samples` implementations
- `MagnitudeShapeDetector` uses method-faithful `_ms_score` (MO²+VO²) — confirmed + regression-guarded
- `n_iter_ = max_iter` for FuzzyFunctionalCMeans and FunctionalGMM — confirmed in fit
- `test_triage.py` retained as secondary check (not deleted) — confirmed reconciled to all-green

---

## Human Verification

N/A — Infrastructure/library phase with no user-facing elements.
All acceptance criteria are verifiable programmatically. All behavioral tests pass.

---

## Gaps Summary

No gaps. All 14 observable truths verified, all artifacts substantive and wired, all tests green, no anti-patterns.

**Minor documentation items (not blockers):**
1. REQUIREMENTS.md COMPLY-01 / COMPLY-02 checkboxes remain unchecked — documentation lag only.
2. ROADMAP.md shows Phase 58 as "3/4 plans" complete — Plan 04 checkbox unchecked — documentation lag only.

These are documentation inconsistencies that do not affect the codebase or the empirically verified behavior.

---

_Verified: 2026-09-01T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
