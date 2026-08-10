# Milestones

## v2.0 Grounded AI analysis advisor (Shipped: 2026-08-10)

**Phases completed:** 4 phases, 11 plans, 14 tasks

**Key accomplishments:**

- JWT-style submodule injection + sys.modules registration makes `fdars.advisor` a first-class public API, with `[advisor]` optional extra pinning `anthropic>=0.72.0` + `pydantic>=2.0`.
- Full `TestBuildDiagnosticsOffline` suite (real dataset, determinism, ImportError guard) plus env-gated `TestAdvisorIntegration` class; all offline tests pass network-free, integration test skips cleanly without `ANTHROPIC_API_KEY`.
- Standalone `examples/advisor_recipe.py` script: load Canadian Weather → cluster via kmeans_fd → offline build_diagnostics → optional LLM interpretation guarded by ANTHROPIC_API_KEY; exits 0 without a key (PYAPI-03).
- End-to-end MCP tracer: `[mcp]` extra + `HandleRegistry` (by-reference handles) + `MCPServer("fdars-advisor")` exposing `fdars_build_diagnostics`, proven via an in-process `Client(mcp)` that lists and invokes the tool offline against real Canadian Weather clustering diagnostics.
- Expanded the proven MCP tracer into the full coarse-grained tool set: `_runner.py` with five-method fdars dispatch by reference, `fdars_run_method` returning only `{result_id, method}` (arrays in registry), `run_stdio()` stdio entry point, and three offline tests covering both tools across all five methods.
- Closed the TOOL-03 agentic re-run/compare loop: `_compare.py` delta builder, `fdars_compare_run` tool with flat-param MCP schema, three deterministic tests, and `examples/mcp_recipe.py` running the full register → run → compare loop offline.
- TDD tracer proves the fdars-advisor skill end-to-end — SKILL.md manifest (agentskills.io-compliant frontmatter), offline walkthrough script (Canadian Weather -> smoothing -> 4-key delta), and 6-function pytest module driving both artifacts.
- All three Plan 02 expansion deliverables (env-gated advise() walkthrough step, complete SKILL.md body with Grounded Advice + Grounding Invariant, and three edge tests) were pre-built in Plan 01 and verified green in 6/6 tests at wave-2 start.

**Requirements:** 16/16 v2.0 requirements complete (CORE, ADVISE, PYAPI, TOOL, SKILL — all mapped to Phases 10–13). All four v2.0 phases `phase_complete` + `verification_status: passed`.

**Closeout:** override_closeout — 1 acknowledged deferred item at close: Phase 12 `12-CONTEXT.md` listed 3 "Open questions for research" (MCP SDK/version, tool JSON-schema design, by-reference data passing) that were in fact resolved during Phase 12 execution (mcp 2.0.0 stdio, `HandleRegistry`, network-free tests). Recorded in STATE.md → Deferred Items. Human UAT (2026-08-10) confirmed the real-key LLM advisor path produces grounded advice citing fdars-computed diagnostics.

---
