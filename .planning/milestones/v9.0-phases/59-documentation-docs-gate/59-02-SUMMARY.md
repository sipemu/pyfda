---
phase: 59-documentation-docs-gate
plan: "02"
subsystem: docs
tags: [docs, sklearn, mkdocs, reference, coverage]
status: complete

dependency_graph:
  requires:
    - docs/sklearn/index.md (Plan 01)
    - mkdocs.yml scikit-learn API section (Plan 01)
  provides:
    - docs/sklearn/transformers.md
    - docs/sklearn/regressors-classifiers.md
    - docs/sklearn/clusterers-outliers.md
    - docs/sklearn/coverage.md
    - mkdocs.yml nav (4 new pages)
  affects:
    - docs site sklearn section (now complete except GridSearchCV example)
    - forward link from index.md to coverage.md (now resolves)

tech_stack:
  added: []
  patterns:
    - fdars-section-hero div idiom (matching docs/advisor/index.md)
    - reference table pattern (estimator | mixin | source | params)
    - MkDocs admonition for honesty caveat and notes

key_files:
  created:
    - docs/sklearn/transformers.md
    - docs/sklearn/regressors-classifiers.md
    - docs/sklearn/clusterers-outliers.md
    - docs/sklearn/coverage.md
  modified:
    - mkdocs.yml

decisions:
  - Coverage page derived from _coverage.py (TRIAGE_VERDICTS + EXCLUDED_METHODS) with automated verify — cannot drift from registry
  - Method-accuracy honesty warning placed in clusterers-outliers.md as MkDocs !!! warning admonition
  - Task 2 verify used direct string search (not regex) because plan's regex missing 'Imputer' suffix variant; all 28 names confirmed present by both approaches
  - GLMRegressor documented as Gaussian FPC-OLS (not beta_t trapezoidal) per CONTEXT.md honesty requirement
  - Stored-FPC predict pattern documented for LDA/QDA/KNN/DD/ElasticMultinomial classifiers

metrics:
  duration: 391s
  completed: "2026-09-01T20:25:55Z"
  tasks: 3
  commits: 3

actuals:
  tokens: 18000
  tasks: 3
  commits: 3
---

# Phase 59 Plan 02: Per-Family Reference Pages + Coverage Page Summary

Authored three per-family reference pages (transformers; regressors & classifiers;
clusterers & outlier detectors) and the coverage/EXCLUDE page derived from
`_coverage.py`, wired all four into the `scikit-learn API` nav section.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Per-family reference pages (transformers, regressors/classifiers, clusterers/outliers) | faac9d1 | docs/sklearn/transformers.md, regressors-classifiers.md, clusterers-outliers.md (new, 426 lines) |
| 2 | Coverage/EXCLUDE page derived from _coverage.py | 0717d20 | docs/sklearn/coverage.md (new, 93 lines) |
| 3 | Wire 4 pages into mkdocs.yml nav | 9ddf013 | mkdocs.yml (+4 lines) |

## What Was Built

### Task 1: Three reference pages

**`docs/sklearn/transformers.md`** — 8 `TransformerMixin` estimators with
`fdars-section-hero` intro, reference table (estimator | sklearn mixin | fdars source
| key params), and per-estimator detail sections. FPCATransformer documented as the
dimensionality-reduction hub with SVD sign canonicalization note.

**`docs/sklearn/regressors-classifiers.md`** — 5 regressors + 6 classifiers with
reference tables and detail sections. Key accuracy notes included:
- Stored-FPC predict pattern documented for FPCLDAClassifier, FPCQDAClassifier,
  FPCKNNClassifier, DDClassifier, ElasticMultinomialClassifier — native method
  provides the FPC basis only; final prediction is a stored sklearn model.
- GLMRegressor documented as Gaussian FPC-OLS (not beta_t trapezoidal).
- LogisticFPCClassifier: binary-only (`multi_class=False`).

**`docs/sklearn/clusterers-outliers.md`** — 3 clusterers + 6 outlier detectors.
Method-accuracy honesty `!!! warning` admonition:
- `MagnitudeShapeDetector` is method-faithful: MS-plot MO/VO decomposition against
  stored training statistics (`mu_`, `var_`).
- Other 5 detectors use modified-band-depth surrogate; true methods available in
  `fdars.outliers`.

### Task 2: Coverage/EXCLUDE page

**`docs/sklearn/coverage.md`** — derived from `python/fdars/sklearn/_coverage.py`:
- 28-row WRAPPED table (all PASS; family, sklearn mixin, fdars source, verdict).
- Reason-code definition table (8 codes with plain-language descriptions).
- 13-row EXCLUDED table covering all `EXCLUDED_METHODS` entries: alignment
  (elastic_align_pair, karcher_mean), pace_fpca, non-Gaussian GLM (binomial,
  poisson), concurrent_regression, fosr, cluster_optim, four inference tests
  (t_perm_test, f_perm_test, oneway_anova_vstat, mean_scb), spm_monitor.
- Source-of-truth note; "EXCLUDED ≠ EXEMPTED" admonition.

### Task 3: mkdocs.yml nav

Added 4 entries after `sklearn/index.md` in the `scikit-learn API` section.
The forward link from `index.md` to `coverage.md` (written in Plan 01) now resolves.

## Verification

**Task 1:** All 28 TRIAGE_VERDICTS names confirmed in page content:
```
ALL 28 NAMES FOUND in page content
```
(Plan's regex missed `Imputer`; direct string search confirmed all 28 present.)

Method-accuracy honesty warning: 6 matches for `MagnitudeShapeDetector` on
`clusterers-outliers.md`; `modified-band-depth surrogate` present.

**Task 2:** All 13 `EXCLUDED_METHODS` `functional_api` paths confirmed present:
```
ALL functional_api refs present
```

**Task 3:** All 5 sklearn paths confirmed in mkdocs.yml content.
Whole-site `mkdocs build --strict` launched as background verify (DOCS_FAST=1).

## Deviations from Plan

### Minor: Plan verify regex gap for `Imputer`

The plan's automated verify script uses a regex that matches class names ending in
specific suffixes (`Transformer`, `Smoother`, etc.) — `Imputer` has none of those
suffixes so the regex returned it as "missing" even though `Imputer` appears 8 times
on `transformers.md`. Supplemented with a direct string-search check that confirmed
all 28 names truly present. No content change required; this is a gap in the plan's
own verify script, not in the authored pages.

## Known Stubs

None. All 28 estimators documented; all exclusions listed; all functional_api paths
present on the coverage page.

## Self-Check

- [x] docs/sklearn/transformers.md exists (written)
- [x] docs/sklearn/regressors-classifiers.md exists (written)
- [x] docs/sklearn/clusterers-outliers.md exists (written)
- [x] docs/sklearn/coverage.md exists (written)
- [x] mkdocs.yml contains all 5 sklearn/* nav paths
- [x] All 28 TRIAGE_VERDICTS names in page content (verified)
- [x] All 13 EXCLUDED_METHODS functional_api refs in coverage.md (verified)
- [x] Method-accuracy honesty warning present on clusterers-outliers.md
- [x] Commit faac9d1 (Task 1), 0717d20 (Task 2), 9ddf013 (Task 3)
