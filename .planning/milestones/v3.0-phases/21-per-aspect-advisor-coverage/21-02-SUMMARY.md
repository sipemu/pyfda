---
phase: 21-per-aspect-advisor-coverage
plan: "02"
subsystem: advisor
status: complete
tags: [advisor, diagnostics, outliers, classification, tdd, aspect-coverage]
completed: 2026-08-12
duration_minutes: 4

dependency_graph:
  requires: [21-01]
  provides: [21-03, 21-04, 21-05]
  affects:
    - python/fdars/advisor/__init__.py
    - python/fdars/advisor/aspects/outliers.py
    - python/fdars/advisor/aspects/classification.py
    - tests/test_advisor.py

tech_stack:
  added: []
  patterns:
    - key-presence guard pattern for multi-shape result dicts
    - explicit n_classes param forwarding (BLOCKER #5 resolution)
    - TDD RED/GREEN with per-class test organization

key_files:
  created:
    - python/fdars/advisor/aspects/outliers.py
    - python/fdars/advisor/aspects/classification.py
  modified:
    - python/fdars/advisor/__init__.py
    - tests/test_advisor.py

decisions:
  - Added n_classes as explicit keyword param to build_diagnostics() per BLOCKER #5 — not via **kwargs, discoverable via inspect.signature()
  - CV error_rate read from raw["error_rate"] (fclassif_cv actual key), emitted as cv_error_rate (Correction #2)
  - accuracy guarded with "if 'accuracy' in raw" (Correction #6); CV path derives accuracy = 1.0 - error_rate
  - n_outliers/outlier_fraction emitted as None for magnitude_shape results (no "outliers" key guard)
  - Determinism tests in both TestBuildDiagnosticsOffline (plan verify target) and TestOutliersAndClassification (detailed)

metrics:
  tasks_completed: 3
  tasks_total: 3
  commits: 4
  files_created: 2
  files_modified: 2
  lines_added: 597
  test_count_before: 28
  test_count_after: 41

actuals:
  tokens: 2390
  tasks: 3
  commits: 4
---

# Phase 21 Plan 02: Outliers + Classification Aspect Coverage Summary

**One-liner:** Outliers builder (4 result shapes, key-presence guarded) and classification builder (point-estimate + CV, corrected keys) with determinism tests; advisor test suite grows from 28 to 41 passing.

## What Was Built

### Task 1: Outliers builder + dispatch + prompt clause (ASPECT-02)

`python/fdars/advisor/aspects/outliers.py` — `_build_outliers_diagnostics(raw, **kwargs) -> dict`

Handles four fdars outlier result shapes by key-presence inference (ASVS V5):

| Shape | Keys present | Builder behavior |
|-------|-------------|------------------|
| `detect_outliers_lrt` | `outliers`, `threshold` | n_outliers, outlier_fraction, threshold all emitted |
| `detect_outliers_lrt_with_dist` | `outliers`, `threshold`, `null_distribution` | same as LRT |
| `outliergram` | `mei`, `mbd`, `outliers` | has_outliergram=True, mei_range/mbd_range emitted |
| `magnitude_shape` | `magnitude`, `shape` only | has_magnitude_shape=True; n_outliers=None (CRITICAL: no "outliers" key) |

`_supported` set gains `"outliers"` and `"classification"` in `build_diagnostics()`.

Prompt clause: `_ASPECT_PRIMERS["outliers"]` was already present from 21-01; verified `outlier_fraction` token present.

### Task 2: Classification builder + dispatch + prompt clause (ASPECT-03)

`python/fdars/advisor/aspects/classification.py` — `_build_classification_diagnostics(raw, *, n_classes=None, **kwargs) -> dict`

Handles two shapes:
- Point-estimate (`fclassif_lda` etc.): reads `accuracy` directly; derives `error_rate = 1 - accuracy`
- CV (`fclassif_cv`): reads `raw["error_rate"]` (CORRECTION #2: actual key, not `cv_error_rate`); emits as `cv_error_rate`; guards `accuracy` (CORRECTION #6: no accuracy in CV result); derives accuracy = 1.0 - error_rate for CV path

BLOCKER #5 resolution: `n_classes: int | None = None` added as explicit keyword param to `build_diagnostics()`, documented in docstring, forwarded only to classification branch. Visible via `inspect.signature(build_diagnostics).parameters`.

Prompt clause: `_ASPECT_PRIMERS["classification"]` verified; `error_rate` token present.

### Task 3: Determinism tests

Tests added to `tests/test_advisor.py`:

**`TestBuildDiagnosticsOffline`** (the plan's verify target):
- `test_outliers_deterministic` — LRT + magnitude_shape fixtures; equal dicts + byte-identical JSON + no numpy scalars
- `test_classification_deterministic` — point-estimate + CV fixtures; same guarantees

**`TestOutliersAndClassification`** (detailed per-shape):
- `test_outliers_lrt_shape`, `test_outliers_magnitude_shape`, `test_outliers_outliergram_shape`
- `test_classification_point_estimate`, `test_classification_n_classes_none_when_omitted`
- `test_classification_cv_shape`, `test_classification_n_classes_explicit_param`
- `test_outliers_deterministic`, `test_classification_deterministic` (also here for completeness)

**`TestOutliersClassificationPrompts`**:
- `test_outliers_prompt_clause` — `outlier_fraction` in outliers prompt, not in base
- `test_classification_prompt_clause` — `error_rate` in classification prompt

## Determinism Confirmation

Both aspects confirmed byte-identical `json.dumps(sort_keys=True)` across two calls:

```
outliers (LRT):       d1 == d2 ✓, json identical ✓, no np.generic ✓
outliers (mag/shape): m1 == m2 ✓, json identical ✓, no np.generic ✓
classification (PE):  p1 == p2 ✓, json identical ✓, no np.generic ✓
classification (CV):  c1 == c2 ✓, json identical ✓, no np.generic ✓
```

## Final Test Results

```
tests/test_advisor.py tests/test_advisor_providers.py: 41 passed, 1 skipped
(baseline was 28 passed, 1 skipped — +13 new tests)
```

## Deviations from Plan

### Auto-added: tests in both TestBuildDiagnosticsOffline and new test classes

The plan called for adding determinism tests to `TestBuildDiagnosticsOffline`. I added those, and also added `TestOutliersAndClassification` and `TestOutliersClassificationPrompts` as separate classes for more granular per-shape and per-prompt testing. This is additive — all existing tests remain untouched.

No other deviations. Plan executed exactly as written.

## Known Stubs

None.

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes at trust boundaries. The two new builder files are pure offline NumPy computation. No threat flags.

## Self-Check

- [x] `python/fdars/advisor/aspects/outliers.py` exists
- [x] `python/fdars/advisor/aspects/classification.py` exists
- [x] All 4 task commits exist (0637ab6, d1301db, 49362ba, f8b2948)
- [x] 41 passed, 1 skipped (advisor + provider suites)
- [x] SUMMARY.md written
