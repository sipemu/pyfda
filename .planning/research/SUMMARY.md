# Project Research Summary

**Project:** pyfda — scikit-learn API Compatibility (v9.0)
**Domain:** scikit-learn-compatible estimator layer over a functional-data-analysis library (PyO3 bindings)
**Researched:** 2026-08-31
**Confidence:** HIGH

## Executive Summary

v9.0 adds a new pure-Python `fdars.sklearn` estimator layer that wraps existing functional-data algorithms as scikit-learn `BaseEstimator` subclasses for seamless `Pipeline` / `GridSearchCV` / `cross_val_score` integration and interop with native sklearn estimators. The layer operates on plain `(n_obs, n_points)` ndarrays with `argvals` as a constructor parameter (defaulting to `np.arange(n_features)`), and calls `fdars._native.*` functions directly — never constructing an `Fdata` inside an estimator (the `Fdata` wrapper introduces dtype side-effects that break `check_estimator`'s dtype-casting checks). It is gated as an optional `[sklearn]` extra exactly like `advisor/` and `mcp/`; no `fdars-core` bump and no advisor changes.

The defining constraint is **full `check_estimator` compliance with no exemptions**: any fdars method that cannot pass the full battery is *excluded* from the sklearn layer (it remains available through the existing functional API) and recorded in a coverage registry — never exempted. The single most important research finding is that this makes a **compliance-triage phase mandatory and first**: skeleton every candidate estimator, run `parametrize_with_checks` per estimator, and record PASS / PASS-WITH-FIXES / EXCLUDE before committing to real implementation. Researchers converged on a consolidated EXCLUDE list of ~9 method categories that predictably fail due to structural incompatibilities.

Key risks and mitigations: (1) **sklearn version/Python-matrix skew** — pin `scikit-learn>=1.3,<1.7` (1.7 drops Python 3.9; floor 1.3 for `validate_data`/`n_features_in_`), bridge the 1.3→1.6 tags-API change with a try/import shim; (2) **the classic sklearn-contract traps** (constructor-param mutation, missing trailing-underscore attrs, `clone` round-trips) — centralize in a shared base class; (3) **functional-data-specific check failures** (tiny-sample, 1-feature, dtype-cast, FPCA SVD sign non-idempotence) — Python-layer guards + sign canonicalization, surfaced early by triage.

## Key Findings

### Recommended Stack

Pin `scikit-learn>=1.3,<1.7` as the `[sklearn]` optional extra. sklearn 1.7 (2026) requires Python 3.10+, which would break the fdars ABI3-py39 guarantee, so 1.6 is the hard ceiling for the 3.9–3.14 matrix; 1.3 is the floor for the public `validate_data` / `n_features_in_` conventions. Three breaking API changes land at 1.6 and must be bridged: `_validate_data` → public `validate_data`; `_more_tags`/`_get_tags` → `__sklearn_tags__()` dataclass; `_xfail_checks` → `expected_failed_checks`. Handle via a small try/import compat guard (or the `sklearn-compat` shim) rather than version-string comparisons. Use `parametrize_with_checks` (built into sklearn) as the CI compliance gate — it surfaces each check as a named pytest case and continues past failures, unlike `check_estimator` which aborts.

**Core technologies:**
- `scikit-learn>=1.3,<1.7`: the estimator contract + `check_estimator`/`parametrize_with_checks` battery — the only new runtime dep; version-capped for the Python 3.9 floor.
- `parametrize_with_checks` (in-tree): per-estimator CI compliance gate — fail-per-check, not fail-fast.
- try/import tags-API compat shim (or `sklearn-compat`): bridge 1.3–1.5 vs 1.6 tags/validation API without version branching.
- scikit-fda: **design reference only, not a dependency** — its `FDataGrid` input contract is the opposite of this milestone's plain-ndarray requirement.

**What NOT to add:** no scikit-fda dependency; no new numerical deps (sklearn wraps the existing `_native` compute); no fdars-core bump.

### Expected Features

~30 candidate estimator classes across five categories map cleanly onto sklearn mixins (final counts pending triage): Transformers (~9), Regressors (~6), Classifiers (~6), Clusterers (~3), Outlier detectors (~6). `FPCATransformer` is the central grid-changing hub — it converts `(n_obs, n_points)` functional data to `(n_obs, n_components)` scores, unlocking the whole Pipeline story; build and validate it first.

**Must have (table stakes):**
- `FPCATransformer` — grid-changing FPCA scores; central Pipeline dependency (needs SVD sign canonicalization for `check_fit_idempotent`).
- Smoothing transformers (B-spline / local-polynomial), imputation, basis representation, depth transform.
- Core predictors: FPC-based regression + PLS; FPC-based classifiers (logistic / LDA / QDA / KNN) — all needing `LabelEncoder` in `fit` for check_estimator's arbitrary labels.
- `FunctionalKMeans` clusterer; the classic outlier trio (LRT / outliergram / magnitude-shape).

**Should have (competitive / differentiators over scikit-fda):**
- Robust FPC regression, Gaussian-only GLM regressor, DD-classifier, elastic-multinomial classifier, nonparametric regression.
- Fuzzy c-means / functional GMM clusterers; newer outlier detectors (tvdmss, muod, depthgram) — these return typed index lists, so a continuous `decision_function` must be synthesized for `OutlierMixin`.

**Defer / EXCLUDE (not exempt — stays in functional API):**
- Registration/alignment (order-sensitive, needs template), CV-based smoothing (self-tuning), `pace_fpca` (IrregFdata input), `functional_glm` non-Gaussian, `elastic_multinomial` where non-compliant, `concurrent_regression` (list-of-matrices input), `cluster_optim` (is itself a hyperparameter search), inference tests (no fit/predict contract), SPM monitoring.

### Architecture Approach

New optional subpackage `python/fdars/sklearn/` mirroring the `advisor/`/`mcp/` pattern: gated in its own `__init__.py` with a `try: from sklearn.base import BaseEstimator` guard; `fdars/__init__.py` is **not** modified. A shared `_BaseFdarsEstimator(BaseEstimator)` centralizes the contract; per-aspect subclasses compose the sklearn mixins and call `fdars._native.*` directly with validated numpy arrays.

**Major components:**
1. `sklearn/_base.py` — `_BaseFdarsEstimator`: stores `argvals` verbatim in `__init__`, resolves to `self.argvals_` in `fit`, sets `n_features_in_` via `validate_data`, casts float32→float64 before native calls, hosts the tags-API compat shim.
2. `sklearn/_transformers.py`, `_regressors.py`, `_classifiers.py`, `_clusterers.py`, `_outliers.py` — the estimator families.
3. `sklearn/_coverage.py` — the EXCLUDED_METHODS registry (reason-coded), populated by triage and finalized as families are implemented.
4. Docs section under `docs/sklearn/` wired into MkDocs nav with offline `markdown-exec` fences.

### Critical Pitfalls

1. **Constructor-param mutation / non-verbatim storage** — every `__init__` arg (esp. `argvals`) must be stored exactly as received; resolve the effective grid only in `fit` → `self.argvals_`. Writing back to `self.argvals` breaks `clone`/`get_params` round-trips, which `check_estimator` catches immediately.
2. **1-sample / 1-feature error-message substrings are a contract** — `check_fit2d_1sample` needs one of `"1 sample"`/`"n_samples=1"`/`"one sample"`/`"1 class"`; `check_fit2d_1feature` needs `"1 feature(s)"`/`"n_features=1"`. Raw Rust/fdars-core error text won't satisfy these — add Python-layer guards before any native call.
3. **FPCA SVD sign ambiguity** — canonicalize component sign (largest-abs element positive) in the Python wrapper, or `check_fit_idempotent` fails intermittently.
4. **Minimum sample/grid requirements** — methods needing a minimum n_samples/n_points/k/df (FPCA n_components, smoothing df, clustering k) are the ones that force EXCLUSION; detect via triage, guard with compliant messages where fixable.
5. **sklearn 1.3→1.6 tags/validation API drift + Python 3.9–3.14 skew** — bridge with the try/import shim; CI must exercise both API paths across the matrix.

## Implications for Roadmap

Suggested 5-phase structure (continues numbering from v8.0 which ended at Phase 54 → this milestone starts at Phase 55):

### Phase 1 (55): Compliance-Triage & Foundation
**Rationale:** The no-exemptions constraint means scope is *discovered*, not assumed. Skeletoning every candidate and running the check battery first prevents implementing then discarding non-compliant estimators.
**Delivers:** `_BaseFdarsEstimator` base class + `[sklearn]` extra pin + `_coverage.py` registry + a PASS/PASS-WITH-FIXES/EXCLUDE list for all ~30 candidates.
**Addresses:** the shared base-class contract; the definitive coverage list.
**Avoids:** Pitfalls 1–5 (centralized in the base class); late discovery of structural non-compliance.
**Go/No-Go gate:** at least a viable core PASSes (≈1 FPCA, 2 smoothers, 2 regressors, 2 classifiers, 1 clusterer, 2 outliers).

### Phase 2 (56): Transformers (incl. FPCA)
**Rationale:** FPCATransformer is the central grid-changing hub the predictors depend on; transformers also carry the strictest dtype/shape checks.
**Delivers:** FPCATransformer (sign-canonicalized), smoothers, imputer, basis representation, depth transform + a `Pipeline([smoother, fpca])` end-to-end test.
**Uses:** `parametrize_with_checks` gate; direct `_native.*` calls.
**Implements:** `sklearn/_transformers.py`.

### Phase 3 (57): Regressors & Classifiers
**Rationale:** Straightforward once FPCATransformer + base patterns exist; all classifiers reuse the `X_fit_` + `LabelEncoder` patterns.
**Delivers:** FPC/PLS regressors; logistic/LDA/QDA/KNN classifiers (+ differentiators that pass) + a `Pipeline([imputer, smoother, fpca, classifier])` end-to-end test.

### Phase 4 (58): Clusterers & Outlier Detectors
**Rationale:** Distinct concerns (determinism/seeding for clustering; synthesized `decision_function` for outliers) warrant their own phase.
**Delivers:** FunctionalKMeans (+ fuzzy c-means/GMM if compliant); LRT/outliergram/magnitude-shape (+ tvdmss/muod/depthgram if compliant).

### Phase 5 (59): Documentation & Docs Gate
**Rationale:** Fence examples depend on working estimators, so docs come last.
**Delivers:** `docs/sklearn/` section + per-category pages + Pipeline & GridSearchCV worked examples (offline `FDARS_FENCE_OK`) + method-accurate hand-authored SVG(s) + the published coverage/EXCLUDE list; whole-site `mkdocs build --strict` green; blocking human diagram review.

### Phase Ordering Rationale
- Triage first because scope is discovered under the no-exemptions rule (dependency: everything downstream needs the PASS/EXCLUDE verdict).
- Transformers before predictors because FPCATransformer is the Pipeline hub the predictors consume.
- Clusterers/outliers separated for their determinism and decision_function specifics.
- Docs last because offline fences require working estimators (standing v6.0 rule: docs phase runs sequentially on `main`, not in worktrees).

### Research Flags
- **Phase 2 (56):** may need a short targeted check if the PASS-WITH-FIXES list is large — exact error-message substrings per sklearn version; determinism of rayon-parallel paths under fixed `random_state`.
- **Phases 3–5:** standard patterns established in Phases 1–2 — skip research-phase.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official sklearn docs/release notes verified current (2026-08-31); version drift validated against a real-world case. |
| Features | HIGH | Direct fdars source inspection + scikit-fda reference + sklearn contracts; EXCLUDE list from check_estimator behavior. PASS-WITH-FIXES boundary refinable by triage. |
| Architecture | HIGH | Full fdars codebase read; BaseEstimator contract verified against the developer guide. |
| Pitfalls | MEDIUM | sklearn source + docs + issue tracker; some specifics (exact error substrings, tags dataclass fields) are version-specific and confirmed at triage. |

**Overall confidence:** HIGH

### Gaps to Address
- Exact PASS/EXCLUDE boundary for borderline estimators (ShiftRegistration on n=2; GLMRegressor tags for response domain; the newer outlier detectors' `decision_function`) — resolved by the Phase-1 triage scan.
- Determinism of rayon-parallel clustering under fixed `random_state` (drives the `non_deterministic` tag decision) — confirm in Phase 4.
- Whether `sklearn-compat` fully covers the 1.4–1.6 tags API vs. a hand-rolled try/import guard — decide in Phase 1.

## Sources

### Primary (HIGH confidence)
- scikit-learn "Developing scikit-learn estimators" developer guide — BaseEstimator contract, tags API, validate_data/n_features_in_.
- scikit-learn install page + 1.6 release highlights — Python support matrix, `validate_data`/`__sklearn_tags__`/`expected_failed_checks` changes.
- scikit-learn `check_estimator` / `parametrize_with_checks` API docs — the compliance battery.
- fdars source (`python/fdars/__init__.py`, `fdata_class.py`, `advisor/`, `mcp/`) — registration/gating pattern, native boundary.

### Secondary (MEDIUM confidence)
- scikit-fda docs (0.10.x) + arXiv paper — FDA estimator API shape as a design reference.
- sklearn issue tracker / PR history — error-message-substring contracts, version-drift failure reports.

---
*Research completed: 2026-08-31*
*Ready for roadmap: yes*
