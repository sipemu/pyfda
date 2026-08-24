# Phase 51: Comparative Method-Selection - Context

**Gathered:** 2026-08-24
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — all three grey areas accepted as recommended

<domain>
## Phase Boundary

A user can ask the advisor to rank/pick among candidate methods for a task; the **winner is chosen by an fdars-computed deterministic sort** (never the LLM), and the LLM narrates the ranking from each candidate's grounded, correctly-attributed diagnostics. Delivers `compare_methods()` (Python API), a new "comparison" advise task family, and an LLM-free `fdars_compare_methods` MCP tool. Requirements: COMPARE-01..04.

Out of boundary: pipeline report (Phase 52), auto-tuning (Phase 53), any new `build_diagnostics` method slot / `_DIAGNOSTICS_METHODS` key (guard-sync stays a no-op), expanding `_RUNNABLE_METHODS`.

</domain>

<decisions>
## Implementation Decisions

### compare_methods() API & inputs
- **Dual input mode**: the Python API `compare_methods()` accepts BOTH pre-computed result dicts AND `(method, params)` specs it runs internally via `build_diagnostics`; the MCP tool re-runs only (it cannot accept arbitrary Python objects).
- **Labeled candidates**: each candidate carries an explicit label (method name + optional tag); the output ranking is keyed by label (never positional-only), so provenance is unambiguous.
- **Ranking metric**: the caller may specify the target metric key; otherwise default to a per-task-family canonical metric (e.g. clustering→silhouette, regression→CV error, smoothing→GCV). The default mapping is fdars-diagnostic-derived.
- **Ranking direction**: a small metric registry encodes higher-is-better vs lower-is-better per metric; ties broken deterministically by candidate order (stable sort) so the same inputs always yield the same winner.

### Comparison task family & provenance
- **New "comparison" task family** (the 4th advise task family) narrates the fdars-computed ranking; the LLM never chooses the winner.
- **Per-candidate labeled provenance**: diagnostics passed to the LLM as a list of `{label, diagnostics}` blocks (never a flat-merged `{**a, **b}` dict `_check_grounding` cannot attribute); the grounding guard runs per-candidate.
- **Winner authority**: the winner is set from the deterministic fdars sort BEFORE the LLM call and validated so LLM output cannot override it.
- **Winner surfacing**: the fdars-chosen winner is a distinct output field, separate from the LLM narration.

### Incommensurability guard & MCP tool
- **Fail-closed comparability**: candidates must share the same task family AND the ranking metric must be present in every candidate's diagnostics; otherwise raise `ValueError` — incommensurable inputs are rejected, never silently mis-ranked.
- **Missing-metric handling**: if any candidate lacks the chosen metric, reject the whole comparison (fail-closed) rather than dropping a candidate silently.
- **MCP `fdars_compare_methods`**: re-runs each candidate via the existing `_RUNNABLE_METHODS` + `build_diagnostics`, returns the ranking by-reference, and NEVER calls `advise()` (provably LLM-free boundary preserved).
- **Runnable coverage**: a requested candidate method not in the 6 `_RUNNABLE_METHODS` is rejected by the MCP tool with a clear error; the Python API can still compare pre-computed results for such methods.

### Claude's Discretion
- Exact function/param names, the "comparison" Advice/output schema shape, the metric registry's default mapping and direction table, and test-fixture datasets — at Claude's discretion, consistent with the existing advisor patterns and the grounding invariant.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor/__init__.py` — `build_diagnostics` + `advise` (3 task families today) + `_supported` (14 aspects).
- `python/fdars/advisor/_prompts.py` — `_ASPECT_PRIMERS`; task-family system prompts.
- `python/fdars/advisor/_schema.py` — Pydantic `Advice` + `_check_grounding` (flat numeric scan — the reason provenance must be per-candidate, not flat-merged).
- `python/fdars/mcp/server.py` — `MCPServer`, `_RUNNABLE_METHODS` (6), `_DIAGNOSTICS_METHODS`; `fdars_run_method`, `fdars_compare_run` (existing before/after delta) as the analog for a new tool.
- `python/fdars/scoring.py` / `fdars.scoring` — candidate source of shared comparison metrics.

### Established Patterns
- Grounding invariant: fdars computes numbers; LLM interprets/cites. `_check_grounding` flat-scans — per-candidate provenance is mandatory.
- MCP boundary provably LLM-free (`test_mcp_does_not_import_advise`); new tools re-run via existing primitives, never call `advise()`.
- Deterministic offline core; env-gated live LLM tests; no network in CI.

### Integration Points
- New `compare_methods()` public entry point in `advisor/__init__.py` (or a new `advisor/_compare_methods.py` imported there).
- New "comparison" system prompt in `_prompts.py`; possibly a `ComparisonAdvice`/extended schema in `_schema.py`.
- New `fdars_compare_methods` tool in `mcp/server.py`; guard-sync (`_DIAGNOSTICS_METHODS`) unchanged.

</code_context>

<specifics>
## Specific Ideas

- The winner MUST come from the deterministic fdars sort, set before the LLM call and validated — the single most important correctness property of this phase (COMPARE-01).
- Provenance must be per-candidate labeled blocks so `_check_grounding` can attribute every cited number to the right candidate (research PITFALLS: flat-merge collapses provenance).
- Fail-closed on incommensurable comparisons — reject, don't silently mis-rank (COMPARE-03).

</specifics>

<deferred>
## Deferred Ideas

- Expanding `_RUNNABLE_METHODS` beyond the current 6 — deferred (candidate methods outside the 6 are Python-API-only for comparison this phase).
- Drop-with-warning for a candidate missing the metric — rejected in favor of fail-closed.
- Weighted multi-metric aggregation into a single score — out of scope (anti-feature; single shared metric only).

</deferred>
