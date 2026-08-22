---
audit_acknowledged:
  milestone: v6.0
  at: 2026-08-22
  questions_digest: 46b4497f1a8fd17e6012a25b675996d1b1398583f16210dafbad995387379c98
---

# Phase 12 Context: Tool / MCP Surface

**Captured:** 2026-08-09 (inline during /gsd-plan-phase 12 — no full discuss-phase)
**Phase goal:** An agent can re-run fdars via tools and compare before/after diagnostics through an MCP server.
**Requirements:** TOOL-01, TOOL-02, TOOL-03

## Locked decisions

- **MCP transport = stdio only.** Local stdio transport, matching the local/CI usage of the
  advisor. HTTP/SSE (hosted) is **explicitly deferred / out of scope** for v2.0
  (see REQUIREMENTS.md "Out of scope (v2.0)" and design doc open decision #2). Do not build
  an HTTP/SSE server in this phase. Keep the tool/handler layer transport-agnostic so a future
  HTTP transport could be added without rewriting tool logic, but only wire stdio now.

- **Compute stays deterministic.** fdars does all numbers; the model only orchestrates. The
  agentic re-run/compare loop must re-run the *actual* fdars method and diff diagnostics — no
  fabricated numbers. Grounding invariant holds: recommendations cite diagnostic values.

- **Pass data by reference.** Tools must not shuttle large arrays through the model. Use a
  reference/handle scheme (e.g. dataset/result IDs or file paths) so `fdars_run_method` and
  `fdars_build_diagnostics` exchange references, not full matrices, across the tool boundary.

## Scope fences

- **In scope (Phase 12):** coarse-grained tool definitions `fdars_build_diagnostics` and
  `fdars_run_method` with strict input/output schemas (TOOL-01); an MCP server (stdio) exposing
  them that a client can list + invoke (TOOL-02); an agentic re-run/compare loop that applies a
  suggested parameter, re-runs, and returns an observable before/after diagnostics delta (TOOL-03).

- **Out of scope (defer to Phase 13):** the Anthropic Agent Skill (`SKILL.md` + packaging,
  SKILL-01/02). Phase 12 tools will be *referenced by* Phase 13's skill — design the tools so a
  skill can drive them, but do not author the skill here.

- **Out of scope (v2.0):** HTTP/REST surface, hosted deployment, non-Anthropic providers,
  autonomous mutation of user data.

## Foundations already built (do not rebuild)

- `python/fdars/advisor.py` provides `build_diagnostics(result, method, ...)` (offline,
  deterministic), `advise(diagnostics, ...)` (grounded Claude call, schema-validated `Advice`),
  and `describe_cluster_differences`. Phase 10 core; Phase 11 API surface + `[advisor]` extra +
  tests + `examples/advisor_recipe.py`.

- The MCP tools should wrap this existing deterministic layer, not reimplement diagnostics.

## Open questions for research

- Which Python MCP SDK / package and version; stdio server entry-point pattern.
- Tool input/output JSON-schema design for `fdars_run_method` (which methods, which params) and
  `fdars_build_diagnostics`.

- By-reference data-passing mechanism that fits both a local stdio server and CI testability.
- How to test an MCP server + client (list tools, invoke) without network and without an
  Anthropic API key (deterministic compute path only).
