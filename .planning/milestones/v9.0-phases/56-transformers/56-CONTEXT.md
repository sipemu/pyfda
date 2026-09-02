# Phase 56: Transformers - Context

**Gathered:** 2026-08-31
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss — determined-implementation phase; fixes precisely specified by Phase-55 triage in `_coverage.py`)

<domain>
## Phase Boundary

Ship the transformer family as fully `check_estimator`-compliant `TransformerMixin` estimators, FPCATransformer first (the grid-changing hub the predictors consume). Delivers XFORM-01..06.

Phase 55 already: created `_BaseFdarsEstimator` + the 1.3→1.8 tags/validate compat shim, the `[sklearn]` extra, and skeletons for all families; FPCATransformer already PASSES full `check_estimator` (47/47). This phase's real work is: bring the 3 PASS-WITH-FIXES transformers to full green, confirm the 5 already-PASS transformers stay green, and add the Pipeline chain test.

In scope: `python/fdars/sklearn/` transformer estimators + their tests. Out of scope: regressors/classifiers (Phase 57), clusterers/outliers + full-matrix compliance gate (Phase 58), docs (Phase 59), any fdars-core bump, any advisor change, any edit to `python/fdars/__init__.py`.
</domain>

<decisions>
## Implementation Decisions

### Transformer roster & per-estimator fixes (from Phase-55 `_coverage.py` verdicts)
- **Already PASS — keep green, do not regress:** FPCATransformer, BSplineSmoother, LocalPolynomialSmoother, DepthTransformer, NormTransformer.
- **Promote to full PASS (the fix is specified):**
  - **BasisRepresentation** — add a 1-feature guard emitting the sklearn-convention error substring (`"1 feature(s)"` / `"n_features=1"`).
  - **Imputer** — complete the `ensure_all_finite`/`force_all_finite` cross-version compat shim + `accept_sparse=False`; keep the `_HAS_TAGS_DATACLASS`-guarded `__sklearn_tags__`/`_more_tags` (CR-01 from the Phase-55 review already applied).
  - **SplineInterpolator** — make the output grid a constructor param (stored verbatim → resolved in fit) so `transform` is idempotent/subset-invariant; add `y=None` to `fit`; guard spline `order` to native `[1,3)` with a sklearn-convention message.

### Contract (unchanged from Phase 55, re-assert)
- Every transformer subclasses `_BaseFdarsEstimator`, stores constructor args verbatim, resolves `argvals_` in fit, sets `n_features_in_` via `validate_data(dtype="numeric")` then `.astype(np.float64)`, calls `fdars._native.*` directly, and NEVER constructs an `Fdata`.
- Grid-changing transformers (FPCA → scores; smoothers/interpolator → possibly new grid) must set output shape deterministically so `Pipeline([smoother, fpca])` chains.
- FPCA components keep SVD sign canonicalization (with the WR-01 all-zero-sign guard already applied).

### Compliance gate
- Each transformer must pass the FULL `parametrize_with_checks` battery on the installed sklearn (1.8). Add/extend a transformer-scoped test that runs the battery per transformer (fast subset — do NOT re-run the whole 28-estimator 1379-check triage each time).
- XFORM-06: an explicit `Pipeline([smoother, fpca])` fit→transform round-trip test.

### Claude's Discretion
Module organization (keep in `_skeletons.py` or split a `_transformers.py`), test file layout, and exact guard wording are at Claude's discretion, guided by `_coverage.py` verdict notes, `55-RESEARCH.md`, and sklearn conventions.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/sklearn/_base.py` — `_BaseFdarsEstimator`, `_HAS_TAGS_DATACLASS`, `validate_data` shim, `_sign_canonicalize` (all-zero guarded), float32→float64 cast helper.
- `python/fdars/sklearn/_skeletons.py` — existing transformer skeletons (FPCATransformer is the keep-forever reference implementation; module-level `_pairwise_l2` helper extracted in Phase 55).
- `python/fdars/sklearn/_coverage.py` — `TRIAGE_VERDICTS` (per-estimator fix notes), `EXCLUDED_METHODS`.
- `tests/sklearn/` — `conftest.py`, `test_foundation.py`, `test_triage.py`, `test_coverage.py`, `test_go_no_go.py`.

### Established Patterns
- Native compute via `fdars._native.*`; `nadaraya_watson` is per-curve (loop rows in smoother transform).
- Optional `[sklearn]` extra gating; base package sklearn-free.
- Dev/CI: Python 3.14 + sklearn 1.8 in `.venv`; shim feature-detects across 1.3→1.8.

### Integration Points
- `python/fdars/sklearn/` (transformers + tests). No change to `python/fdars/__init__.py`, Rust, advisor, mcp.
</code_context>

<specifics>
## Specific Ideas
- Per-estimator fixes are the exact strings in `_coverage.py` `TRIAGE_VERDICTS`. Full research detail: `.planning/phases/55-compliance-triage-foundation/55-RESEARCH.md` and `.planning/research/`.
- Hard constraints (repeat): FULL check_estimator, no exemptions; plain `(n_obs, n_points)` ndarray input + `argvals` constructor param; no fdars-core bump.
</specifics>

<deferred>
## Deferred Ideas
- Regressors/classifiers (Phase 57), clusterers/outliers + full-matrix gate (Phase 58), docs (Phase 59).
- `set_output(transform="pandas")` (FUT-01).
</deferred>
