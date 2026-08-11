# Phase 16: Tool / MCP Server Page - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss grey areas auto-answered with recommended defaults per the autonomous-run instruction; grounded in the shipped `python/fdars/mcp/` source).

<domain>
## Phase Boundary

Author a new `docs/advisor/mcp.md` page documenting the fdars-advisor MCP server: the three tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`), stdio setup (`run_stdio`), the by-reference `HandleRegistry` model, and a concrete re-run/compare before-after loop mirroring `examples/mcp_recipe.py`. Covers MCPDOC-01, MCPDOC-02, MCPDOC-03. `mkdocs.yml` nav wiring is Phase 18.

</domain>

<decisions>
## Implementation Decisions

### Page & Content
- Page path: `docs/advisor/mcp.md` (the exact target the Phase 15 page already forward-links to as `mcp.md`).
- The page uses ILLUSTRATIVE (non-executed) `python` fences — NOT an executed docs-build fence. Rationale: the MCP surface requires the `[mcp]` extra (`mcp>=2.0.0`, Python 3.10+); the docs build must not depend on that optional extra or a specific Python floor. Code shown must still be real and runnable if the reader installs `fdars[mcp]`, mirroring `examples/mcp_recipe.py`.
- Document all three tools with their roles, parameters, and return shapes (verified against `python/fdars/mcp/server.py`): `fdars_build_diagnostics` (method + dataset/result handles → diagnostics dict), `fdars_run_method` (method + params on a registered dataset → returns ONLY `{result_id, method}`, arrays stay in the registry), `fdars_compare_run` (method + `before_result_id` + after-params → observable before/after `delta`).
- Explain the by-reference `HandleRegistry` model: `store_dataset`/`store_result` mint opaque handle ids; arrays never cross the tool boundary; tools exchange handles. This is the grounding/efficiency property to make explicit.
- Document stdio setup via `run_stdio()` (the stdio entry point) and how a client launches the server.
- Walk the agentic re-run/compare loop with a concrete example matching `_runner.py` (5-method dispatch) and `_compare.py` (before/after scalar delta), following the register → run → compare sequence in `examples/mcp_recipe.py`.

### Cross-links & Nav
- Cross-link back to the overview (`index.md`) and the Python API page (`python-api.md`); forward-link to the Agent Skill page (`agent-skill.md`, Phase 17 — annotate "coming in Phase 17").
- `mkdocs.yml` nav wiring deferred to Phase 18 (NAVDOC-01).

### Claude's Discretion
- Exact prose, section order, and whether tool parameters are shown as tables or definition lists — subject to method-accuracy against `server.py`.
- Which method the compare-loop example uses (smoothing is the shipped example in `mcp_recipe.py`; keep consistent unless another reads clearer).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/mcp/server.py` — `MCPServer("fdars-advisor")`, `@mcp.tool()` `fdars_build_diagnostics(method, result_id=None, ...)`, `fdars_run_method(method, ...)` returning `{result_id, method}`, `fdars_compare_run(method, before_result_id, ...)` returning a delta, and `run_stdio()`.
- `python/fdars/mcp/_registry.py` — `HandleRegistry` with `store_dataset`/`get_dataset`, `store_result`/`get_result`, `clear`.
- `python/fdars/mcp/_runner.py` — `run_method` dispatching 5 methods (alignment, fpca→`fdars.regression.fpca`, basis→`basis_nbasis_cv`, smoothing→`pspline_fit_gcv`, clustering→`kmeans_fd`).
- `python/fdars/mcp/_compare.py` — `compare_run(ds_id, method, before_id, params_after)` builds before/after diagnostics and a scalar `delta`.
- `examples/mcp_recipe.py` — the end-to-end register → run → compare recipe to mirror.

### Established Patterns
- Grounding invariant holds on the tool surface too: fdars computes the numbers; the tools exchange handles and diagnostics, no LLM in the compute path.
- `[mcp]` extra: `mcp>=2.0.0`, Python 3.10+ (guarded by `sys.version_info < (3, 10)` in the runner).

### Integration Points
- New file `docs/advisor/mcp.md`.
- `mkdocs.yml` nav deferred to Phase 18.

</code_context>

<specifics>
## Specific Ideas

- Tool names, parameter names, and return shapes MUST be verified against `python/fdars/mcp/server.py`, `_runner.py`, `_compare.py` before writing — do not invent tool signatures. In particular: `fdars_run_method` returns only `{result_id, method}` (arrays stay in the registry), and `fdars_compare_run` takes a flat `before_result_id` + after-params and returns a before/after `delta`.
- The docs build must NOT require the `[mcp]` extra or Python 3.10+ — MCP fences are illustrative, not executed.

</specifics>

<deferred>
## Deferred Ideas

- Agent Skill page (Phase 17) — cross-linked only.
- `mkdocs.yml` nav wiring + full-build gate (Phase 18).
- HTTP/SSE transport — out of scope (deferred from v2.0; stdio only).

</deferred>
