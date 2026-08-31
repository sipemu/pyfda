# Phase 53: Closed-Loop Auto-Tuning (capstone) - Context

**Gathered:** 2026-08-24
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — all four grey areas accepted as recommended

<domain>
## Phase Boundary

Turn the manual recommend → re-run → compare workflow into an autonomous, bounded loop: the advisor proposes a parameter change, applies it within a declared range, re-runs fdars, compares diagnostics, and iterates until a target diagnostic improves or a step budget is hit. Exposed BOTH as a Python API (`auto_tune()`, LLM proposal via a schema-validated numeric delta) AND as an MCP agentic tool (`fdars_auto_tune`, heuristic/LLM-free proposal). The compute path stays LLM-free throughout — fdars runs every computation; the loop only orchestrates. Requirements: TUNE-01..06.

Out of boundary: eval strategy + docs (Phase 54); any new `build_diagnostics` method slot / `_DIAGNOSTICS_METHODS` key (guard-sync stays a no-op); expanding `_RUNNABLE_METHODS`.

## Research note
This is the milestone's genuine-unknown phase — the research SUMMARY flags it for `--research-phase` during planning. Phase-level research WILL run (convergence math, oscillation detection, heuristic-proposal specifics, the tunable-param registry) before the planner.

</domain>

<decisions>
## Implementation Decisions

### Loop core & termination
- **Loop core**: new `python/fdars/advisor/_tuning.py` with `run_tuning_loop(initial, method, target_metric, propose_fn, max_steps, ...)`; `propose_fn` is INJECTABLE (LLM for the API, heuristic for MCP, mock for tests) → the whole loop is fully offline-testable without an API key (TUNE-01).
- **Termination (bounded)**: required `max_steps` PLUS convergence detection (Δtarget < ε for K consecutive steps) PLUS oscillation detection (param revisit / metric ping-pong). The loop NEVER runs unbounded (TUNE-02).
- **"Improve" direction**: reuse the Phase-51 metric registry (higher/lower-is-better); the caller names the target metric.
- **"Apply" step**: mutate the method's scalar param by the proposed delta WITHIN a declared valid range → re-run via fdars (run_method) → rebuild diagnostics → compare.

### Proposal mechanism (grounding)
- **Python API proposal**: the LLM returns a STRUCTURED numeric `parameter_delta` (schema-validated, within the declared range) — NEVER parsed from prose; the LLM never sets a number directly in the numeric path (TUNE-03).
- **MCP proposal**: a DETERMINISTIC heuristic (LLM-free) — gradient-sign / grid step on the target metric (TUNE-04).
- **Schema**: new `TuneProposal {param, delta-or-new_value, rationale}`; new `TuneResult` + `TuningTrace`; plus an OPTIONAL `Recommendation.parameter_delta` field (backward-compatible with the 3 existing task families — TUNE-06).
- **Range safety**: each tunable param declares a valid range; out-of-range proposals are clamped/rejected; an unparseable proposal exits the loop (no numeric-path retry).

### Guard diagnostics (Goodhart) & trace
- **Guard diagnostics (TUNE-05)**: optional watched non-target metrics; if a guard metric degrades past a threshold while the target improves, flag/stop (Goodhart protection).
- **TuningTrace**: records each step {proposal, params, target before/after, guards, accepted} → returned in `TuneResult`.
- **Accept policy**: accept a step only if the target improves AND guards don't degrade; else reject/terminate.
- **Determinism**: a fixed `propose_fn` + fixed data ⇒ fully deterministic and offline-testable.

### Surfaces & scope
- **Tunable methods**: a small tunable-param registry over the EXISTING 6 runnable methods (e.g. smoothing bandwidth, basis nbasis, clustering k) — each with a clear scalar param + target metric. No `_RUNNABLE_METHODS` expansion.
- **MCP `fdars_auto_tune`**: orchestrates run_method + compare + heuristic proposal; provably LLM-free (never calls `advise()`); returns by-reference.
- **`max_steps`**: default 10, hard cap 20 (bounds LLM cost).
- **Eval hook**: `auto_tune()` returns a trace rich enough for the Phase-54 deterministic eval; eval itself is Phase 54.

### Claude's Discretion
- Exact convergence ε / K, oscillation-detection algorithm, heuristic step rule, the tunable-param registry contents + ranges, schema field names, and test fixtures — at Claude's discretion, informed by phase-level RESEARCH.md, consistent with the grounding invariant + LLM-free-MCP boundary.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor/_compare_methods.py` — the compare/delta primitive + metric registry (direction) + union-grounding — the loop's "compare" step and metric-direction source.
- `python/fdars/advisor/_pipeline.py` — Phase-52 aggregation/provenance patterns.
- `python/fdars/mcp/_compare.py` / `_compare_methods.py` / `_pipeline.py` — the before/after delta + LLM-free MCP tool patterns to mirror for `fdars_auto_tune`.
- `python/fdars/mcp/server.py` — `_RUNNABLE_METHODS` (6), `fdars_run_method`, handle registry.
- `python/fdars/advisor/_schema.py` — `Advice`/`Recommendation` + `_check_grounding`; add `TuneProposal`/`TuneResult`/`TuningTrace` + optional `Recommendation.parameter_delta`.
- `python/fdars/advisor/providers/` — Provider protocol for the LLM proposal path (structured output).

### Established Patterns
- Grounding invariant: fdars computes every number; the LLM only proposes via a schema-validated numeric delta, never in the numeric path.
- MCP provably LLM-free (`test_mcp_does_not_import_advise`, `test_tool_never_imports_advise`); new tools never call `advise()`; heuristic proposal only.
- Deterministic offline core (injectable propose_fn); env-gated live LLM tests; no CI network.
- Guard-sync no-op (no new method slot).

### Integration Points
- New `_tuning.py` + `auto_tune()` in `advisor/` (imported into `__init__.py`).
- `_schema.py`: `TuneProposal`/`TuneResult`/`TuningTrace` + optional `Recommendation.parameter_delta`.
- `_prompts.py`: a "parameter_proposal"/tuning system prompt for the LLM propose_fn.
- `mcp/server.py` + `mcp/_tuning.py`: `fdars_auto_tune` (heuristic, LLM-free); guard-sync unchanged.

</code_context>

<specifics>
## Specific Ideas

- The single most important invariant: the LLM never sets a number in the numeric path. Proposals flow ONLY through a schema-validated numeric `parameter_delta`; the MCP tool uses a heuristic and never calls `advise()`.
- The loop MUST be bounded and offline-testable from day one — injectable `propose_fn` + `max_steps` + convergence + oscillation, all exercisable in CI with a mock and no API key (research PITFALLS: non-termination, oscillation, non-determinism).
- Guard diagnostics defend against Goodhart — optimizing the target must not silently wreck a watched metric.

</specifics>

<deferred>
## Deferred Ideas

- Python-API-only cut (defer the MCP tool) — rejected; ship both surfaces this phase.
- max_steps cap above 20 — rejected; cap at 20 to bound LLM cost.
- Multi-parameter / joint tuning — out of scope; single scalar param per loop this phase.
- Eval harness — Phase 54 (auto_tune returns a trace rich enough to feed it).
</deferred>
