# Phase 40: Advisor Extension - Context

**Gathered:** 2026-08-21
**Status:** Ready for planning
**Mode:** Smart-discuss (autonomous) — grey areas resolved from the milestone requirements + research; full-autonomy run. Decisions ADV-04/ADV-05 were locked with the user at milestone definition (extend existing `outliers` aspect; Group B decided at plan time).

<domain>
## Phase Boundary

Extend the grounded AI advisor so its EXISTING aspect builders surface grounded scalar diagnostics for the v6.0 bindings — with the grounding invariant preserved (every diagnostic is an fdars-computed number; the LLM only interprets/cites; offline-deterministic; no numpy scalars; byte-identical `json.dumps`). Python-only (no Rust rebuild): `python/fdars/advisor/aspects/*.py` (+ `_prompts.py`/`__init__.py` dispatch if needed) and, only if a new aspect key were added, the MCP `python/fdars/mcp/{server,_runner}.py` guard-sync in a SINGLE atomic commit.

Requirements: ADV-04 (extend the `outliers` aspect — closes the v5.0 Phase-34 functional-boxplot-outlier deferral), ADV-05 (extend the `regression` aspect; Group B advisor coverage decided at plan time on feasibility).

</domain>

<decisions>
## Implementation Decisions

### ADV-04 — outliers aspect (locked: EXTEND, no new aspect key)
- Extend `python/fdars/advisor/aspects/outliers.py`'s `build_diagnostics` so it detects the new v6.0 outlier-detector result dicts (tvdmss / muod / sequential_transform_outliers / depthgram) by key presence and emits grounded SCALAR diagnostics: e.g. `n_outliers` (count), outlier fraction (n_outliers / n_obs), score/threshold ranges (min/max of the fdars-computed score vector) — NEVER raw index lists or numpy aggregates; reduce every value to a Python `float`/`int`. This closes the v5.0 Phase-34 deferral (functional-boxplot outlier diagnostics).
- No new aspect KEY is added (the aspect is already `outliers`); therefore `_DIAGNOSTICS_METHODS`/`_RUNNABLE_METHODS`/`_supported` are UNCHANGED and the MCP guard-sync is a no-op — confirm at plan/exec time that `test_diagnostics_methods_match_advisor_supported` stays green without edits. If (unexpectedly) a new key is required, the aspect-builder + MCP guard change MUST land in one atomic commit.

### ADV-05 — regression aspect + Group B feasibility (decided at plan time)
- Extend `python/fdars/advisor/aspects/regression.py` so it surfaces grounded diagnostics for the new regression results where a genuine fdars-computed scalar exists: `functional_glm` (deviance, AIC, n_iter/converged), `concurrent_regression` (a fit-summary scalar, e.g. residual RMS). Grounding invariant preserved.
- **Group B advisor coverage (pace_fpca via `fpca` aspect, elastic_multinomial via `classification` aspect):** DECIDE at plan time on feasibility. Default per milestone research: pace_fpca/elastic_multinomial have insufficient grounding surface → leave as bindings + docs only (deferred). Include only if a genuinely grounded scalar diagnostic exists (e.g. pace_fpca eigenvalue/variance-explained; elastic_multinomial train accuracy). Do NOT fabricate.
- ITP (interval inference) advisor coverage is NOT a locked v6.0 requirement; fold a grounded scalar into the existing `inference` aspect only if trivially available and clearly grounded — otherwise defer.

### Grounding + determinism (hard constraints)
- Every emitted diagnostic cites an fdars-computed value; the advisor's `_check_grounding` guard must still pass. Offline `build_diagnostics` stays network-free and byte-identical across runs (`json.dumps(..., sort_keys=True)` stable); convert all numpy scalars via `float()`/`int()`.

### Claude's Discretion
Exact scalar diagnostic set per detector/model, whether Group B/ITP are included (feasibility), and prompt-primer wording are at Claude's discretion, grounded in the shipped v6.0 result dicts and the existing aspect-builder patterns.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor/aspects/outliers.py`, `regression.py`, `inference.py`, `fpca.py`, `classification.py` — the per-aspect `build_diagnostics` builders to extend (v3.0/v4.0/v5.0 established the pattern: detect result keys, emit grounded scalar dicts).
- `python/fdars/advisor/aspects/_utils.py` — shared scalar-reduction helpers (float coercion, range summaries).
- `python/fdars/advisor/_prompts.py` (`_ASPECT_PRIMERS`) + `__init__.py` dispatch.
- `python/fdars/mcp/{server,_runner}.py` — `_RUNNABLE_METHODS`/`_SUPPORTED_METHODS` guards (mirror-synced; `test_diagnostics_methods_match_advisor_supported`).
- v4.0 Phase 28 / v5.0 Phase 34 — the direct precedents for "extend advisor aspect + guard-sync single atomic commit + grounding invariant preserved".

### Established Patterns
- Aspect `build_diagnostics(result, ...)` returns a plain dict of grounded scalars; offline-deterministic; no LLM in the diagnostics path; `_check_grounding` enforces evidence cites a value.

### Integration Points
- `python/fdars/advisor/aspects/{outliers,regression}.py` (+ maybe `fpca`/`classification`/`inference`), `_prompts.py`/`__init__.py` if primers change; `tests/` advisor offline tests (grounding + determinism) extended; MCP guard files ONLY if a new aspect key is added (not expected).

</code_context>

<specifics>
## Specific Ideas

Mirror v5.0 Phase 34 exactly: extend the existing aspect builder(s), add offline grounding + determinism tests for the new diagnostics, keep the MCP guard-sync test green (ideally with no guard edit). No numpy scalars in any emitted dict.

</specifics>

<deferred>
## Deferred Ideas

- Dedicated advisor aspects for pace_fpca / elastic_multinomial if ADV-05's feasibility check defers them (Future Requirements: PACE-ADV / MULTINOM-ADV).
- Docs update of advisor `aspects.md` for the extended diagnostics — Phase 41 (DOCS-11).

</deferred>
