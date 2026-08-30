# Phase 52: Pipeline Diagnostic Report - Context

**Gathered:** 2026-08-24
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — all three grey areas accepted as recommended

<domain>
## Phase Boundary

A user can generate ONE grounded multi-aspect narrative report for an end-to-end analysis (represent → smooth → cluster/regress → monitor), with diagnostics aggregated across stages under strict per-stage provenance and Python-computed cross-stage caveats. Proves the per-stage isolation the auto-tuning capstone (Phase 53) depends on. Delivers `build_pipeline_report()`, `pipeline_report()`, a new "pipeline" advise task family, and an LLM-free `fdars_build_pipeline_report` MCP tool. Requirements: PIPE-01..04.

Out of boundary: auto-tuning (Phase 53); eval + docs (Phase 54); any new `build_diagnostics` method slot / `_DIAGNOSTICS_METHODS` key (guard-sync stays a no-op).

</domain>

<decisions>
## Implementation Decisions

### Stage spec & aggregation
- **Stage input**: an ordered list of stage entries `{stage_name, aspect, result-or-precomputed-diagnostics}`; `build_pipeline_report()` runs `build_diagnostics` per stage (or accepts precomputed diagnostics dicts).
- **Provenance structure**: aggregate as per-stage labeled blocks — a list of `{stage, aspect, diagnostics}` — NEVER a flat `{**a, **b}` merge. Reuse the Phase-51 union-grounding pattern (`{"_stages": [...]}` wrapper) for the grounding CHECK so `_flatten_diagnostics_numbers` collects every stage's numbers without key-collision loss.
- **Stage ordering**: preserve caller-declared order (typically represent → smooth → cluster/regress → monitor); the report follows that order.
- **Aspect reuse**: each stage's diagnostics come from the EXISTING `build_diagnostics` aspects — no new aspect key → guard-sync stays a no-op (`_DIAGNOSTICS_METHODS` unchanged).

### Pipeline task family & narrative
- **New "pipeline" task family** (the 5th advise task family) narrates the multi-stage report, grounded per-stage.
- **Report structure**: per-stage summary sections + an overall narrative + a DISTINCT structured cross-stage-caveats field.
- **Grounding**: union grounding across all stages (fabrication caught — every cited number must exist in some stage's real diagnostics) with per-stage attribution preserved in the LLM PROMPT (the Phase-51 lesson — do NOT over-reject with per-stage-strict checks, and do NOT flat-merge what is sent to the LLM).
- **Schema**: a dedicated `PipelineReport` schema (stages + narrative + caveats), validated like `Advice`.

### Cross-stage signal detection & MCP
- **Caveat rules**: a small DETERMINISTIC Python rule table computed from real diagnostics (NOT the LLM) — e.g. high `imputed_fraction` (represent) → FPCA/clustering reliability caveat; high outlier count → downstream caveat; low cumulative variance explained → clustering caveat.
- **Caveat authority**: caveats are Python-computed from thresholds on real fdars numbers (grounded), surfaced as structured items; the LLM narrates them but never invents them.
- **Thresholds**: documented constants (approximate guidance), overridable via params; conservative defaults.
- **MCP `fdars_build_pipeline_report`**: re-runs each stage via the existing runnable methods + `build_diagnostics`, aggregates by-reference, and NEVER calls `advise()` (provably LLM-free boundary preserved).

### Claude's Discretion
- Exact function/param names, `PipelineReport` schema field names, the caveat rule set/threshold constants (conservative, documented), and test-fixture datasets — at Claude's discretion, consistent with existing advisor patterns + grounding invariant.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor/__init__.py` — `build_diagnostics` + `advise` (4 task families now, incl. "comparison" from Phase 51) + `compare_methods`.
- `python/fdars/advisor/_compare_methods.py` — Phase-51 per-candidate provenance + union-grounding (`{"_candidates":[...]}`) — the direct analog for the pipeline `{"_stages":[...]}` aggregation.
- `python/fdars/advisor/_prompts.py` — task-family system prompts + `_ASPECT_PRIMERS`.
- `python/fdars/advisor/_schema.py` — `Advice`, `_check_grounding`, `_flatten_diagnostics_numbers` (recurses into lists — the mechanism union-grounding relies on).
- `python/fdars/mcp/server.py` + `mcp/_compare_methods.py` — Phase-51 LLM-free MCP tool pattern to mirror for `fdars_build_pipeline_report`.

### Established Patterns
- Grounding invariant: fdars computes numbers; LLM narrates/cites. Union-grounding catches fabrication while preserving per-stage prompt provenance (Phase 51 WR-03 resolution).
- MCP boundary provably LLM-free (`test_mcp_does_not_import_advise`, `test_tool_never_imports_advise`); new tools never call `advise()`.
- Deterministic offline core; env-gated live LLM tests; no CI network.

### Integration Points
- New `build_pipeline_report()` + `pipeline_report()` in `advisor/` (new `_pipeline.py` imported into `__init__.py`).
- New "pipeline" system prompt in `_prompts.py`; `PipelineReport` in `_schema.py`.
- New `fdars_build_pipeline_report` tool in `mcp/server.py` (+ helper); guard-sync (`_DIAGNOSTICS_METHODS`) unchanged.

</code_context>

<specifics>
## Specific Ideas

- Per-stage isolation is the load-bearing property: the capstone (Phase 53) reuses this aggregation, so provenance must never collapse (list-of-blocks + union-grounding, exactly as Phase 51).
- Cross-stage caveats MUST be deterministic Python functions of real diagnostics (grounded) — the LLM narrates them, never generates them (PIPE-03 + grounding invariant).

</specifics>

<deferred>
## Deferred Ideas

- Minimal single-caveat cut (imputed-fraction only) — rejected; ship the small rule table (imputed-fraction, outliers, low-variance) this phase.
- Auto-detecting the pipeline stage order from data — out of scope; caller declares order.
- A visual/HTML dashboard rendering — out of scope (narrative report only; docs diagram comes in Phase 54).

</deferred>
