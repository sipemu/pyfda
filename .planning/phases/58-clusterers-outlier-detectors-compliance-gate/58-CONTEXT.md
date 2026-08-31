# Phase 58: Clusterers & Outlier Detectors + Compliance Gate - Context

**Gathered:** 2026-08-31
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss) — determined-implementation phase; fixes specified by triage verdicts + the established stored-reference subset-invariance pattern from Phase 57.

<domain>
## Phase Boundary

Ship the clusterer (`ClusterMixin`) and outlier-detector (`OutlierMixin`) families as fully `check_estimator`-compliant, then — with all five families present — lock the full-matrix compliance gate (COMPLY-01) and prove native-sklearn interop (COMPLY-02). Delivers CLUS-01, CLUS-02, OUT-01, OUT-02, COMPLY-01, COMPLY-02.

State entering Phase 58: 20/28 estimators PASS. Remaining 8: FuzzyFunctionalCMeans + FunctionalGMM (clusterers, need `n_iter_`); LRTOutlierDetector, OutliergramDetector, MagnitudeShapeDetector, TVDMSSDetector, MUODDetector, DepthgramDetector (outlier detectors, need continuous `decision_function` + subset-invariant scoring + contamination-based predict). This phase must also FINALIZE the compliance gate so the whole suite is green and reconcile `test_triage.py`.

Out of scope: docs (Phase 59), fdars-core bump, advisor changes, `python/fdars/__init__.py` edits.
</domain>

<decisions>
## Implementation Decisions

### Clusterers (`ClusterMixin`) — CLUS-01, CLUS-02
- **FunctionalKMeans** — already PASS; add a regression test asserting it stays green + is deterministic under a fixed `random_state` (map `random_state` → u64 seed; confirm rayon-parallel path is reproducible under a fixed seed — if not, set the `non_deterministic` tag or force a deterministic path).
- **FuzzyFunctionalCMeans / FunctionalGMM** — PASS-WITH-FIXES: add the `n_iter_` fitted attribute in `fit()` (from the native iteration count / config) so `check_non_transformer_estimators_n_iter` passes. (This resolves the deferred Phase-57 review WR-03.)

### Outlier detectors (`OutlierMixin`) — OUT-01, OUT-02
The `OutlierMixin` contract needs: `fit(X)`, `score_samples(X)` (continuous, higher = more inlier or a documented convention), `decision_function(X)` (continuous; `predict` = sign of `decision_function` shifted by an `offset_` from `contamination`), and `predict(X)` returning {-1 (outlier), +1 (inlier)}.
- **THE key requirement — subset-invariance:** `score_samples(X[mask])` MUST equal `score_samples(X)[mask]`. So each point is scored against a STORED training reference captured at fit, NOT against the current test batch. (This is the fix for the deferred Phase-57 review CR-03 on MagnitudeShapeDetector, which computed outlyingness relative to batch statistics.) Store the training reference at fit (e.g. training depth band / population curves / per-point depth reference); in `score_samples`, compute each test point's score against the stored reference independently.
- Per-detector fixes (from `_coverage.py`):
  - **LRTOutlierDetector** — proper continuous `decision_function` + `contamination` param so `predict` yields both {-1,+1} on the battery; store training reference.
  - **MagnitudeShapeDetector** — proper subset-invariant `decision_function` + `contamination`; score each curve's magnitude/shape outlyingness vs the STORED training population (fixes CR-03).
  - **OutliergramDetector / TVDMSSDetector / DepthgramDetector** — add `decision_function = score_samples` alias; ensure `score_samples` is subset-invariant vs stored reference.
  - **MUODDetector** — `decision_function` alias + 1-feature guard with sklearn-convention message.
- For index-list-returning natives (tvdmss/muod/depthgram), synthesize a continuous score from the underlying quantity (TVD / shape index / depth) computed per-point vs the stored reference — not the binary flag.
- `contamination` (default `"auto"` or a float, sklearn convention) sets `offset_` so `predict` produces both classes on typical data.

### Compliance gate — COMPLY-01
- With all 5 families present, the full-matrix `parametrize_with_checks` gate must be green for EVERY wrapped estimator, zero exemptions. Finalize the compliance test so the aggregate (all per-family compliance suites) is green.
- **Reconcile `test_triage.py`:** it has been red for unpromoted skeletons all milestone. Now that all 28 candidates are PASS, either (a) `test_triage.py` goes fully green (all 28 pass parametrize_with_checks), or (b) it is repurposed/retired in favor of the per-family compliance suites as the authoritative gate. Decide and make the whole `tests/sklearn/` suite green so CI is clean. Confirm `_coverage.py` has 0 remaining PASS-WITH-FIXES among wrapped estimators (all PASS) and EXCLUDED_METHODS holds only genuinely-structural design exclusions.
- CI matrix note: the gate is described as running across Python 3.9–3.14 / sklearn 1.3–1.6 + 1.8; the dev env is 3.14+1.8. Wire the `[sklearn]` compliance job into CI config (`.github/workflows/ci.yml`) so it runs on the matrix; the shim already spans 1.3→1.8.

### Interop — COMPLY-02
- A test proving `Pipeline([FPCATransformer(), RandomForestClassifier()])` (fdars transformer → native sklearn estimator) fits + predicts end-to-end.

### Claude's Discretion
Stored-reference representation per detector, contamination default, the test_triage.py reconcile approach, and CI wiring specifics are at Claude's discretion, guided by `_coverage.py` verdicts, the OutlierMixin contract, and sklearn conventions.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/sklearn/_skeletons.py` — clusterer + outlier skeletons; `_fpc_fit_scores`/`_fpc_project`/`_pairwise_l2`/`_require_y`/`_reject_continuous_target` helpers from Phases 56–57; FPCATransformer.
- `python/fdars/sklearn/_coverage.py` — TRIAGE_VERDICTS (flip the last 8 to PASS), EXCLUDED_METHODS (structural only).
- `fdars._native.depth` / `fdars._native.outliers` — functional depth + outlier detectors (tvdmss/muod/depthgram/magnitude_shape/etc.) for stored-reference scoring.
- `tests/sklearn/` — compliance-harness pattern from Phases 56–57; `test_triage.py` (to reconcile).
- `.github/workflows/ci.yml` — Python 3.9–3.14 matrix to wire the `[sklearn]` compliance job into.

### Established Patterns
- Subset-invariant reconstructed scoring: store training reference at fit, score per-point vs stored reference (Phase 57 classifiers established this).
- `random_state` → u64 seed for stochastic natives; LabelEncoder where relevant.
- Native compute via `fdars._native.*`; never construct Fdata; sklearn 1.8 dev env; shim spans 1.3→1.8.

### Integration Points
- `python/fdars/sklearn/` (clusterers + outliers + tests), `.github/workflows/ci.yml` (compliance job). No `__init__.py`/Rust/advisor/mcp changes.
</code_context>

<specifics>
## Specific Ideas
- Deferred Phase-57 review items to resolve HERE: **CR-03** (MagnitudeShapeDetector subset-invariance) + **WR-03** (FuzzyCMeans/GMM `n_iter_`).
- Per-detector fixes are the exact strings in `_coverage.py` `TRIAGE_VERDICTS`.
- Hard constraints: FULL check_estimator, no exemptions; plain `(n_obs, n_points)` ndarray + `argvals` constructor param; no fdars-core bump.
</specifics>

<deferred>
## Deferred Ideas
- Docs (Phase 59): the "scikit-learn API" section + Pipeline/GridSearchCV fences + SVG + human review + version bump.
- `set_output(transform="pandas")` (FUT-01); sklearn 1.7+ once Python 3.9 dropped (FUT-03).
</deferred>
