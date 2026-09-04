# Phase 72: Advisor Extension - Context

**Gathered:** 2026-09-04
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

Extend the AI advisor so it produces GROUNDED diagnostics for the new v11.0 capability
families, holding the grounding invariant and MCP guard-sync as hard constraints. This is a
Python-advisor + MCP change — NO new PyO3 bindings.

In scope (ADV-01, ADV-02):
- **NEW aspects (diagnostics-only):** `python/fdars/advisor/aspects/fts.py` and
  `.../frechet.py`, each with a `_build_<aspect>_diagnostics(raw, **kwargs) -> dict`
  mirroring the existing aspect pattern.
- **EXTEND existing aspects** for the new methods:
  - `regression.py` — function-on-function (`fof_regression`, `fof_re_regression`) and the
    additive/generalized scalar-on-function models (`fam`, `fregre_gkam`, `fregre_gsam`).
  - `classification.py` — the shapelet classifier (`shapelet_classifier_fit` result).
  - `spm.py` — multivariate FPCA (`mfpca`) + `spe_multivariate`.
- **MCP guard-sync (ADV-02):** update `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` across
  `python/fdars/mcp/{server.py,_runner.py,_pipeline.py}` ATOMICALLY (single commit) with the
  aspect changes. `test_guard_sync_version_independent.py` + a per-aspect
  `json.dumps(build_diagnostics(...))` serialization test pass.

Out of scope (user decision — deferred): advisor coverage for advanced clustering
(dbscan/kcfc/funfem/align) and density_fda (they are bound + usable; advisor diagnostics are
additive, deferrable to a future milestone). GAK is a metric, not a diagnostics-producing
analysis. Docs (DOCS-01 → Phase 73). FRE-RUN-01 (promote frechet to runnable — future).

</domain>

<decisions>
## Implementation Decisions

### Advisor coverage scope (user decision)
- **Exactly ADV-01:** new `fts` + `frechet` aspects; extend `regression`/`classification`/`spm`.
  Clustering + density_fda advisor coverage DEFERRED.

### Hard constraints (locked — STATE grounding invariant + ADV-02)
- **Grounding invariant:** every diagnostic value is a real fdars-computed native Python
  `float`/`int`/`bool`/`list`/`None` — NO Python-derived synthetic numbers and NO numpy
  scalars entering `json.dumps`. Follow the existing aspect discipline (see the
  regression.py header note: "All values native Python types. No NumPy scalars. Two calls on
  the same input always return an equal, JSON-serialisable dict."). Cast every numpy scalar
  with `float(...)`/`int(...)`; guard optional keys.
- **Determinism / serialization:** `json.dumps(build_diagnostics(raw))` succeeds for each new
  aspect + each extended method; two calls on the same input return an equal dict.
- **fts + frechet are DIAGNOSTICS-ONLY:** both go into `_DIAGNOSTICS_METHODS` ONLY — NEITHER
  is added to `_RUNNABLE_METHODS`. SC3 emphasizes `frechet` specifically must NOT be runnable.
- **Guard-sync atomicity:** the `_DIAGNOSTICS_METHODS`/`_RUNNABLE_METHODS` edits across all
  three mcp files land in the SAME commit as the aspect registration (ADV-02); the version-
  independent guard-sync test proves the three copies stay consistent.
- **MCP compute path stays provably LLM-free:** no LLM in the number path — the diagnostics
  are pure fdars-computed scalars; the LLM only interprets the already-computed dict.

### Claude's Discretion (research-informed)
- The exact diagnostic FIELDS per new aspect/method are method-accuracy choices — derive them
  from each function's real 0.33 result-dict keys (e.g. fts: ncomp, forecast horizon,
  stationarity p-value, acf decay; frechet: n_obs, frechet variance, group variances/p-value;
  fof: r_squared-like fit + beta-surface dims; mfpca: eigenvalue share / ncomp; shapelet
  classifier: train_accuracy, n_shapelets, n_classes). Only surface values fdars actually
  computes.
- Whether each EXTENDED method (fof/fam/mfpca/shapelet_classifier) is added to
  `_RUNNABLE_METHODS` or stays diagnostics-only depends on whether the MCP runner can execute
  it with registered data without a new registration protocol — default to diagnostics-only
  (interpret the result dict) unless the existing aspect already runs analogous methods and the
  addition is trivial. Research/planning decides per method; frechet + fts stay diagnostics-only
  regardless.

</decisions>

<code_context>
## Existing Code Insights

### Structure
- `python/fdars/advisor/aspects/` — one module per aspect (alignment, basis, classification,
  clustering, depth, fpca, inference, outliers, regression, regression_cv, represent, scoring,
  smoothing, spm) + `_utils.py`. Each exposes `_build_<aspect>_diagnostics(raw, **kwargs)`.
- `python/fdars/advisor/_pipeline.py` + `__init__.py` — `build_diagnostics` dispatch.
- `python/fdars/mcp/server.py` — `_RUNNABLE_METHODS` (:52) and `_DIAGNOSTICS_METHODS` (:66,
  the superset adding diagnostics-only aspects). Copies also in `_runner.py` (:59) and
  referenced in `_pipeline.py` (:121).
- `tests/test_guard_sync_version_independent.py` — the guard-sync consistency gate.

### Pattern to mirror
- `regression.py` — canonical grounded aspect: guarded optional-key access, `float()`/`int()`
  casts, native-only return, JSON-serialisable, deterministic. Copy its discipline for
  `fts.py`/`frechet.py` and the extensions.
- The existing per-aspect advisor tests (`tests/test_advisor_*.py`) + grounding test
  (`tests/test_advisor_grounding.py`) — mirror for the new aspects.

### Integration Points
- New aspect files + registration in the advisor dispatch (`_pipeline.py`/`__init__.py`);
  atomic edits to the 3 mcp guard-set files; new tests (per-aspect serialization + extend
  guard-sync).

</code_context>

<specifics>
## Specific Ideas

- Read each new method's REAL 0.33 result-dict keys (from the Phase 67-71 SUMMARYs / the bound
  PyDicts) so every diagnostic maps to a value fdars actually computes — no invented metrics.
- Confirm the exact three-file guard-set update mechanics + what `test_guard_sync_version_independent.py`
  asserts (so the atomic single-commit requirement is met and the test passes).
- Run `test_advisor_grounding.py` (or its equivalent) against the new aspects to prove
  native-scalar grounding.
- Whole-suite must stay green; the advisor/MCP tests are the gate here (no docs build in this phase).

</specifics>

<deferred>
## Deferred Ideas

- Advisor coverage for advanced clustering (dbscan/kcfc/funfem/align) + density_fda — future milestone.
- FRE-RUN-01: promote the `frechet` aspect to `_RUNNABLE_METHODS` once a density/metric-space dataset registration protocol is designed — future.
- All new-capability docs pages (DOCS-01) — Phase 73.

</deferred>
