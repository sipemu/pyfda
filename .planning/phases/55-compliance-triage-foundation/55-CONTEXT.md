# Phase 55: Compliance-Triage & Foundation - Context

**Gathered:** 2026-08-31
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss — infrastructure/foundation phase, grey-area questioning skipped; enriched from v9.0 research)

<domain>
## Phase Boundary

Establish the shared sklearn-contract base class + the `[sklearn]` optional extra, then **discover the definitive scope** by skeletoning every candidate estimator and running the `check_estimator` battery — producing a per-estimator PASS / PASS-WITH-FIXES / EXCLUDE verdict *before* any real family implementation (phases 56–58). Delivers FND-01..04 and TRIAGE-01..03.

In scope: `python/fdars/sklearn/` subpackage skeleton + gating; `_BaseFdarsEstimator`; `[sklearn]` extra pin; skeleton (not full implementation) of ~30 candidate estimators sufficient to run the check battery; the `_coverage.py` EXCLUDED_METHODS registry; the go/no-go viable-core gate.

Out of scope: real per-family implementation (56–58), docs (59), any fdars-core bump, any advisor/MCP change, any edit to `python/fdars/__init__.py`.
</domain>

<decisions>
## Implementation Decisions

### Packaging & Gating (FND-01, FND-02)
- `scikit-learn` is an optional extra `[sklearn]` pinned `>=1.3,<1.7` (1.7 drops Python 3.9; floor 1.3 for public `validate_data`/`n_features_in_`). Base package imports with zero sklearn installed.
- New subpackage `python/fdars/sklearn/` gated exactly like `advisor/` and `mcp/`: a `try: import sklearn` guard in `sklearn/__init__.py` raising an actionable `ImportError` naming the extra. **`python/fdars/__init__.py` is NOT modified** (git diff must be empty for that file) — mirror the deferred-import pattern already used by advisor/mcp.

### Base Class Contract (FND-03, FND-04)
- `_BaseFdarsEstimator(BaseEstimator)` centralizes: constructor args (incl. `argvals`) stored **verbatim** in `__init__` (no mutation, no conversion); resolve to `self.argvals_` (default `np.arange(n_features)`) only in `fit`; `n_features_in_` set via `validate_data`; float32→float64 cast before any native call; 1-sample / 1-feature Python-layer guards emitting the sklearn error-substring contracts (`"1 sample"`, `"1 feature(s)"`, etc.).
- Estimators call `fdars._native.*` directly with validated numpy arrays — **never construct an `Fdata`** inside an estimator (Fdata's dtype side-effects break check_estimator's dtype-casting checks).
- FPCA components get SVD **sign canonicalization** (largest-abs element positive) for `check_fit_idempotent`.
- Tags-API compat: bridge sklearn 1.3–1.5 vs 1.6 (`_more_tags`/`_get_tags` → `__sklearn_tags__`, `_validate_data` → `validate_data`) via a small hand-rolled try/import shim in the base class. **Open for the planner:** whether to use the `sklearn-compat` PyPI shim instead — flag a research-phase during `/gsd-plan-phase` if this or the triage harness needs it (Notes on the ROADMAP phase say the same).

### Triage & Coverage (TRIAGE-01..03)
- Compliance gate = `parametrize_with_checks` (in-tree; fail-per-check, not fail-fast), wired as a pytest job.
- Every ~30 candidate estimator gets a *skeleton* run through the battery → recorded PASS / PASS-WITH-FIXES / EXCLUDE verdict.
- `sklearn/_coverage.py` `EXCLUDED_METHODS` records each excluded fdars method with its failing-check / structural reason; each excluded method must remain callable via the existing functional API.
- Research-predicted EXCLUDE list (confirm empirically, do not assume): registration/alignment, CV-based smoothing, `pace_fpca` (IrregFdata), non-Gaussian `functional_glm`, `elastic_multinomial` where non-compliant, `concurrent_regression` (list-of-matrices), `cluster_optim` (is itself a hyperparameter search), inference tests, SPM monitoring.
- Go/no-go gate: a viable core must PASS (≈1 FPCA, 2 smoothers, 2 regressors, 2 classifiers, 1 clusterer, 2 outlier detectors) before family implementation begins.

### Claude's Discretion
All remaining implementation choices (skeleton module layout, exact triage-harness shape, verdict-recording format, whether to adopt `sklearn-compat`) are at Claude's discretion, guided by the research (`.planning/research/`), success criteria, and codebase conventions.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Optional-extra + deferred-import + actionable-ImportError pattern: `python/fdars/advisor/__init__.py`, `python/fdars/mcp/__init__.py` — copy this gating shape for `sklearn/__init__.py`.
- `python/fdars/__init__.py` — central registration/export; must stay unchanged this phase.
- `python/fdars/fdata_class.py` — shows how `Fdata` methods call `_native.*` directly; the sklearn layer calls the same entry points but never builds an `Fdata`.
- Codebase maps in `.planning/codebase/` (ARCHITECTURE, CONVENTIONS, STRUCTURE, STACK, TESTING, INTEGRATIONS, CONCERNS).
- Existing `pyproject.toml` `[project.optional-dependencies]` with `advisor`/`mcp`/`openai`/`gemini`/`ollama`/`all-providers` — add `[sklearn]` alongside.

### Established Patterns
- Native compute via `fdars._native.*`; numpy row-major ↔ FdMatrix column-major conversion at the boundary.
- Optional deps imported lazily / gated; base package must import with none installed.
- Python 3.9–3.14 ABI3 matrix; tests via pytest.

### Integration Points
- `pyproject.toml` (`[sklearn]` extra), `python/fdars/sklearn/` (new), test suite (`parametrize_with_checks` job). No change to `python/fdars/__init__.py`, Cargo/Rust, advisor, or mcp.
</code_context>

<specifics>
## Specific Ideas

- Full research detail: `.planning/research/SUMMARY.md` (+ STACK/FEATURES/ARCHITECTURE/PITFALLS.md).
- Hard milestone constraints (repeat): FULL check_estimator compliance, NO exemptions — non-compliant methods are EXCLUDED to the functional API and recorded in `_coverage.py`, never exempted; plain `(n_obs, n_points)` ndarray input with `argvals` as a constructor param; no fdars-core bump; no advisor changes.
</specifics>

<deferred>
## Deferred Ideas

- `set_output(transform="pandas")` DataFrame output (FUT-01).
- Re-evaluating EXCLUDED methods if fdars-core later exposes stored-model / template-free variants (FUT-02).
- sklearn 1.7+ support once Python 3.9 is dropped (FUT-03).
</deferred>
