# Phase 28: Advisor Extension - Context

**Gathered:** 2026-08-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend the shipped v3.0 grounded AI advisor to cover the relevant new v4.0 capabilities, preserving the grounding invariant (fdars computes every number; the LLM only interprets and cites) and keeping the MCP guard-sync test green. Built on Phases 25–27 (all bindings shipped; suite at 388 passed / 4 skipped).

Delivers (ADV-01, ADV-02):
- **`scoring` diagnostics aspect (NEW, method #13):** new `python/fdars/advisor/aspects/scoring.py` builder + `_supported` entry in `advisor/__init__.py` + `_DIAGNOSTICS_METHODS` entry in `mcp/server.py` — wired in a SINGLE atomic commit so `test_diagnostics_methods_match_advisor_supported` (tests/test_mcp_server.py:503) stays green. `_RUNNABLE_METHODS` stays 6 (scoring needs caller-supplied y_true/y_pred the MCP dataset model can't provide — diagnostics-only in MCP).
- **Imputation-quality diagnostics** extend the EXISTING `represent` aspect (`aspects/represent.py`) — already in `_supported`, so no guard-sync change.
- **Registration-quality diagnostics** extend the EXISTING `alignment` aspect (`aspects/alignment.py`) — already in `_supported`, so no guard-sync change.
- **Offline determinism tests** proving each new aspect/method produces byte-identical, JSON-serialisable output for the same input (no numpy scalars, no network).

Out of this phase: docs for the new advisor coverage (Phase 29).
</domain>

<decisions>
## Implementation Decisions

### Grounded coverage depth (user-decided)
- `scoring` gets the FULL grounded treatment matching all 12 existing aspects: a `build_diagnostics` builder AND an `_ASPECT_PRIMERS["scoring"]` entry in `advisor/_prompts.py`, so `advise()` supports the interpretation/parameter/method task families for scoring — with the grounding invariant enforced (evidence must cite a real computed metric value).

### Scoring diagnostics input (user-decided)
- The CALLER computes the 5 `fdars.scoring` metrics (mae/mse/mape/msle/explained_variance) and passes them as the `result` dict; `build_diagnostics(result, method="scoring", ...)` summarizes/interprets those already-fdars-computed numbers. This keeps the grounding invariant clean (fdars did the arithmetic; the builder only organizes and the LLM only cites) and keeps the `build_diagnostics` signature narrow — no y_true/y_pred parameters added. Mirrors the established pattern where the builder consumes fdars output rather than recomputing.

### Aspect placement (research-determined — Claude's discretion within these)
- Imputation-quality → extend `aspects/represent.py` (represent already operates on INPUT data per the [21-03] decision; imputation quality is a representation concern). Registration-quality → extend `aspects/alignment.py`. Neither changes `_supported`/`_DIAGNOSTICS_METHODS` (both aspects already present), so no guard-sync churn for ADV-02 — only ADV-01 (`scoring`) touches the guarded sets.
- Every new diagnostic value must come from a bound fdars function (e.g. the `fdars.scoring.*` metrics, `impute_missing_values` residuals, the `least_squares_score`/`pairwise_correlation_score`/`sobolev_least_squares_score` quality scores) — NEVER Python-side arithmetic. Evidence strings cite a real number, reusing the v3.0 generic evidence helper that scans diagnostics for the first numeric value.

### Atomicity & guard-sync (mandatory)
- ADV-01's three edits — `aspects/scoring.py` (+ dispatch in `__init__.py`), `_supported` set, and `_DIAGNOSTICS_METHODS` — land in ONE commit; `test_diagnostics_methods_match_advisor_supported` must pass at that commit. Do not split them across commits (it would red the guard test mid-phase).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor/__init__.py` — `build_diagnostics(result, method, ...)`, the `_supported` set (12 aspects, lines ~124–134), and the `method_lc == "..."` dispatch chain (e.g. line ~154 alignment, ~186 represent) to extend.
- `python/fdars/advisor/aspects/` — one module per aspect (`represent.py`, `alignment.py`, … `_utils.py` shared helpers). Add `scoring.py`; extend `represent.py` + `alignment.py`.
- `python/fdars/advisor/_prompts.py` — `_ASPECT_PRIMERS` dict (line 45; `represent` at 66) — add a `scoring` primer; `_supported_tasks = {interpretation, parameter, method}`.
- `python/fdars/advisor/_schema.py` — the `Advice` schema (grounding: evidence cites diagnostic values).
- `python/fdars/mcp/server.py` — `_DIAGNOSTICS_METHODS` (12, line ~63) and `_RUNNABLE_METHODS` (6, line ~49); add `scoring` to `_DIAGNOSTICS_METHODS` only.
- `tests/test_mcp_server.py:503` — `test_diagnostics_methods_match_advisor_supported` (parses the advisor error message / set, asserts set equality). Must stay green.

### Established Patterns
- v3.0 aspects: deterministic offline builder returning a JSON-serialisable dict (plain floats/ints/strings — NO numpy scalars), plus a primer clause. Offline determinism tests assert byte-identical repeat output, network-free.
- The `[21-03]` `_utils.py` shared helper (skewness, elbow, etc.) — reuse where relevant.

### Integration Points
- `advise()` reads `_ASPECT_PRIMERS[aspect]`; `build_diagnostics` dispatches by `method`; MCP `fdars_build_diagnostics` guards on `_DIAGNOSTICS_METHODS`. The grounding `_check_grounding` guard applies to any `advise()` output.

</code_context>

<specifics>
## Specific Ideas

- Read the existing `aspects/represent.py` and `aspects/depth.py` (raw-ndarray input) as the closest analogs before writing `scoring.py`.
- The scoring `result` dict keys should be the 5 metric names (`functional_mae`/`mse`/`mape`/`msle`/`explained_variance` or a documented subset) → the builder summarizes them (e.g. which error is largest, whether explained_variance is high/low) with each diagnostic citing the fdars-computed value.
- Imputation-quality diagnostics on `represent`: e.g. fraction of points imputed, and a residual/consistency measure computed via a bound fdars function — not Python math.
- Registration-quality diagnostics on `alignment`: summarize the 3 fdars quality scores (`least_squares_score`, `pairwise_correlation_score`, `sobolev_least_squares_score`).

</specifics>

<deferred>
## Deferred Ideas

- Docs pages / diagrams for the new advisor coverage (scoring/imputation/registration) → Phase 29.
- Making scoring MCP-runnable (`_RUNNABLE_METHODS`) — intentionally NOT done; it needs caller-supplied y_true/y_pred outside the MCP dataset model.
</deferred>
