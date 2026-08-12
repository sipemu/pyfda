# Phase 22: Surface Integration - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous smart-discuss — builds on Phases 19–21; MCP + Skill are existing surfaces from v2.0)

<domain>
## Phase Boundary

The MCP tool surface and the Agent Skill expose the new per-aspect coverage (from Phase 21), and provider selection (from Phases 19–20) is reachable from the Python API — while the MCP boundary stays LLM-free and provider selection lives only in `advise()`.

In scope (REQ-IDs): SURF-01, SURF-02, SURF-03.

Out of scope: packaging/CI matrix + bare-venv smoke (Phase 23); docs-site pages (Phase 24). This phase touches `python/fdars/mcp/` and `.claude/skills/fdars-advisor/` only.
</domain>

<decisions>
## Implementation Decisions

### Grounded in code + research (ARCHITECTURE.md: MCP stays LLM-free; provider selection only in Python API)

- **SURF-01 — MCP exposes new aspects, stays compute-only.** `python/fdars/mcp/_runner.py` has `_SUPPORTED_METHODS` (a frozenset that "mirrors advisor._supported", T-12-02) and `run_method` which RUNS an fdars computation on a stored dataset; `fdars_build_diagnostics` then builds diagnostics from a result. Extend the MCP surface so the Phase-21 aspects are reachable **while keeping every tool handler LLM-free** (no `advise()` call inside any MCP handler — the grounding invariant / no-LLM-in-compute-path holds).
  - **Nuance (for research/planner):** not every new aspect is a runnable `run_method` (depth needs a reference sample; represent needs data+argvals; regression needs a response `y`; SPM needs Phase-1 fit inputs). Determine which new aspects are exposed via `run_method` (runnable) vs which are diagnostics-only over a caller-supplied result via `fdars_build_diagnostics`. Keep `_SUPPORTED_METHODS` consistent with `advisor._supported` where a method is genuinely runnable; for diagnostics-only aspects, ensure `fdars_build_diagnostics` accepts them. Do NOT silently claim a method is runnable if the fdars binding needs inputs the MCP dataset model can't supply — document the mapping.
- **SURF-02 — provider selection via Python API only.** `advise(provider=…, model=…)` already exists (Phases 19–20). This criterion is mostly a guardrail + verification: confirm provider/model selection is reachable through the Python API and that NO MCP tool handler calls `advise()` (MCP stays compute-only). Add/keep a test asserting no MCP handler imports/calls `advise()`.
- **SURF-03 — Agent Skill doc.** Update `.claude/skills/fdars-advisor/SKILL.md` (and the walkthrough script if needed) to document: (a) provider selection including the local/offline path (Ollama, OpenAI-compatible `base_url`), and (b) the FULL per-aspect advisor coverage (all aspects, not just "clustering, smoothing, FPCA, alignment, basis"). Keep the SKILL.md spec-valid (agentskills.io frontmatter). The `compatibility`/install note may reference the new provider extras — but the actual PyPI release carrying them is a later version bump handled at ship (not this phase); wording should not overclaim what's on PyPI today.

### Claude's Discretion

The exact runnable-vs-diagnostics-only split per aspect for the MCP surface, whether new MCP tool params are needed, and the precise SKILL.md wording — at Claude's discretion, guided by the actual `_runner.py`/`server.py`/`_registry.py` capabilities and the fdars bindings.
</decisions>

<code_context>
## Existing Code Insights

- `python/fdars/mcp/_runner.py` — `_SUPPORTED_METHODS` frozenset (line ~51, mirrors `advisor._supported`) + `run_method(ds_id, method, **params)`; no arrays accepted as tool args (threat T-12-03).
- `python/fdars/mcp/_registry.py` — HandleRegistry (by-reference handles).
- `python/fdars/mcp/server.py` — `MCPServer("fdars-advisor")` exposing `fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run` over stdio; these are compute-only, no LLM.
- `python/fdars/advisor/__init__.py` — `_supported` now has all aspects (Phase 21); `advise(provider=, model=, aspect=)` (Phases 19–21).
- `.claude/skills/fdars-advisor/SKILL.md` — currently lists "clustering, smoothing, FPCA, alignment, or basis"; compatibility note references git-URL install + `[mcp]`/`[advisor]` extras. Needs provider-selection + full-coverage update.
- Tests: `tests/test_mcp_server.py`, `tests/test_skill.py` (existing; keep green + extend).
</code_context>

<specifics>
## Specific Ideas

- Add a test asserting NO MCP handler calls `advise()` (grep/AST or import-graph check) — locks the "MCP stays LLM-free" invariant.
- Extend `tests/test_mcp_server.py` to cover at least one newly-exposed aspect through the MCP tool path (offline, by-reference handle), asserting compute-only behavior.
- Keep the MCP tests network-free and stdio/in-process (`Client(mcp)`), matching the existing v2.0 pattern.
- SKILL.md: enumerate the full aspect list and a short "choosing a provider (incl. local Ollama / OpenAI-compatible)" section; keep frontmatter spec-valid.
</specifics>

<deferred>
## Deferred Ideas

- Packaging the provider extras into a PyPI release + CI matrix → Phase 23.
- Docs-site provider setup guide + per-aspect pages → Phase 24 (SKILL.md here is the Agent-Skill doc, distinct from the MkDocs site).
- HTTP/SSE MCP transport → out of scope (FUT-01).
</deferred>
