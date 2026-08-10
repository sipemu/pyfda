---
phase: 12-tool-mcp-surface
plan: 01
subsystem: api
tags: [mcp, model-context-protocol, mcpserver, handle-registry, advisor, pytest-asyncio]

# Dependency graph
requires:
  - phase: 11-python-api-surface
    provides: "advisor.build_diagnostics (offline, deterministic, JSON-serialisable diagnostics for 5 methods)"
  - phase: 10-advisor-core
    provides: "fdars.clustering.kmeans_fd, fdars.datasets.load_canadian_weather"
provides:
  - "[mcp] optional extra (mcp>=2.0.0, Python 3.10+)"
  - "python/fdars/mcp/ subpackage with Python-3.10 import guard"
  - "HandleRegistry (by-reference dataset/result handles) + module-level registry singleton"
  - "MCPServer('fdars-advisor') exposing fdars_build_diagnostics tool"
  - "tests/test_mcp_server.py — in-process Client(mcp) tracer test, skips on 3.9"
affects: [12-02-tool-run-method, 12-03-compare-loop, phase-13-agent-skill]

# Actuals
actuals:
  tokens: 3972
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: [mcp>=2.0.0, mcp-types, pytest-asyncio, anyio, starlette, uvicorn]
  patterns:
    - "In-process HandleRegistry: tools exchange opaque ds-/r- IDs, never raw numpy arrays"
    - "@mcp.tool() type-hint-derived JSON Schema (no hand-written inputSchema)"
    - "Python-3.10 runtime import guard in mcp/__init__.py + module-level pytest skipif"
    - "mcp subpackage NOT registered in fdars.__init__ — imported explicitly (advisor precedent)"

key-files:
  created:
    - python/fdars/mcp/__init__.py
    - python/fdars/mcp/_registry.py
    - python/fdars/mcp/server.py
    - tests/test_mcp_server.py
  modified:
    - pyproject.toml

key-decisions:
  - "list_tools() returns a ListToolsResult with a .tools attribute (mcp 2.0.0) — iterate .tools, not the result object"
  - "call_tool structured_content is None with dict-returning def handlers; the content[0].text JSON fallback is the working path (Open Question 2 resolved)"
  - "synchronous def tool handlers work with MCPServer + async Client(mcp) (Open Question 1 resolved: sync handlers fine)"
  - "with_argvals=True passes dataset argvals into build_diagnostics; result_id resolves a stored fdars result, else the raw data matrix is used"

patterns-established:
  - "Handle registry by-reference: store_dataset/store_result return IDs; get_* raise KeyError naming the offending id (fail closed, T-12-01)"
  - "method validated against closed set {alignment,fpca,basis,smoothing,clustering} before any fdars call (T-12-02)"
  - "autouse fixture calls registry.clear() after each test to prevent module-singleton state leakage"

requirements-completed: [TOOL-01, TOOL-02]

coverage:
  - id: D1
    description: "[mcp] optional extra declared (mcp>=2.0.0, Python 3.10+ note) in pyproject.toml"
    requirement: TOOL-02
    verification:
      - kind: unit
        ref: "grep -qE '^\\s*mcp\\s*=\\s*\\[\"mcp>=2\\.0\\.0\"\\]' pyproject.toml"
        status: pass
    human_judgment: false
  - id: D2
    description: "Python 3.9 raises a clear ImportError naming Python 3.10+; MCP test module skips on 3.9"
    requirement: TOOL-02
    verification:
      - kind: unit
        ref: "python/fdars/mcp/__init__.py version guard + tests/test_mcp_server.py pytestmark skipif"
        status: pass
    human_judgment: false
  - id: D3
    description: "HandleRegistry provides by-reference store; tools exchange opaque IDs, KeyError on unknown id"
    requirement: TOOL-01
    verification:
      - kind: unit
        ref: "python/fdars/mcp/_registry.py HandleRegistry + registry singleton"
        status: pass
    human_judgment: false
  - id: D4
    description: "MCPServer('fdars-advisor') exposes fdars_build_diagnostics; in-process Client(mcp) lists AND invokes it end-to-end returning real clustering diagnostics (method=='clustering', k==4), offline, no ANTHROPIC_API_KEY"
    requirement: TOOL-02
    verification:
      - kind: integration
        ref: "tests/test_mcp_server.py#test_tracer_list_and_call_build_diagnostics"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-08-09
status: complete
---

# Phase 12 Plan 01: TRACER — fdars MCP Tool Surface Summary

**End-to-end MCP tracer: `[mcp]` extra + `HandleRegistry` (by-reference handles) + `MCPServer("fdars-advisor")` exposing `fdars_build_diagnostics`, proven via an in-process `Client(mcp)` that lists and invokes the tool offline against real Canadian Weather clustering diagnostics.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-09T21:01:30Z
- **Completed:** 2026-08-09T21:07Z
- **Tasks:** 2 (1 tracer implementation + 1 blocking-human package-legitimacy checkpoint)
- **Files modified:** 5 (4 created, 1 modified)

## Accomplishments

- Declared the `[mcp]` optional extra (`mcp>=2.0.0`, Python 3.10+ note) — installs cleanly, `mcp==2.0.0` resolved.
- Built `HandleRegistry` (in-process by-reference store): `store_dataset`/`get_dataset`/`store_result`/`get_result`/`clear`, `ds-`/`r-` uuid IDs, `KeyError` naming the offending id on miss (fail-closed, threat T-12-01).
- Stood up `MCPServer("fdars-advisor")` with one synchronous `@mcp.tool()` `fdars_build_diagnostics` that validates `method` against the closed set (T-12-02) and **delegates** to `advisor.build_diagnostics` (no reimplementation).
- Proved the full stack end-to-end (packaging → registry → server → tool → advisor → in-process Client) with a passing async tracer test; **offline, no `ANTHROPIC_API_KEY`, no network**.
- Confirmed `import fdars` (no extra) is unaffected — the mcp guard lives only in `fdars/mcp/__init__.py`. Full suite: 105 passed, 1 skipped.

## Task Commits

1. **Task 1: TRACER — [mcp] extra, HandleRegistry, MCPServer, tracer test** - `e55c0bd` (feat)
2. **Deviation fix (Task 1 tracer feedback): list_tools .tools iteration** - `bb63ab9` (fix)

**Checkpoint (Task 2):** `checkpoint:human-verify` gate="blocking-human" for `mcp` package legitimacy — APPROVED by user (verified `mcp==2.0.0` is the official Model Context Protocol Python SDK at pypi.org/project/mcp + github.com/modelcontextprotocol/python-sdk). Install proceeded post-approval.

**Plan metadata:** committed separately after this SUMMARY.

## Files Created/Modified

- `pyproject.toml` - Added `[mcp]` extra (`mcp>=2.0.0`) with Python 3.10+ compatibility note.
- `python/fdars/mcp/__init__.py` - Subpackage entry with `sys.version_info < (3, 10)` ImportError guard; exports HandleRegistry, registry, server.
- `python/fdars/mcp/_registry.py` - `HandleRegistry` class + module-level `registry` singleton (by-reference handles, KeyError fail-closed).
- `python/fdars/mcp/server.py` - `mcp = MCPServer("fdars-advisor")` + `fdars_build_diagnostics` `@mcp.tool()` (method allowlist validation, delegates to advisor.build_diagnostics).
- `tests/test_mcp_server.py` - Module-level `skipif(<3.10)`, autouse `registry.clear()` fixture, async tracer test (Client(mcp) list + call).

## Decisions Made

- **`list_tools()` returns `ListToolsResult`; iterate `.tools`** — matches research Pattern 3 (`tools.tools`), confirmed against installed mcp 2.0.0.
- **`structured_content` is `None` for dict-returning `def` handlers** — the `content[0].text` JSON fallback is the working unwrap path (resolves Open Question 2).
- **Synchronous `def` tool handlers work with async `Client(mcp)`** (resolves Open Question 1; no `async def` needed for fdars sync compute).
- **`result_id` optional** — when provided, `get_result` resolves the stored fdars result; otherwise the raw data matrix is wrapped as `{"data": data}`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `list_tools()` response iterated incorrectly**
- **Found during:** Task 1 tracer feedback gate (running the tracer `<verify>` after the blocking-human checkpoint approval).
- **Issue:** The test iterated the `list_tools()` result directly (`for t in tools_response`), which yields tuples in mcp 2.0.0 — `AttributeError: 'tuple' object has no attribute 'name'`. The SDK returns a `ListToolsResult` whose Tool list lives on the `.tools` attribute.
- **Fix:** Iterate `tools_response.tools` (aligns with research Pattern 3's `tools.tools`). Confirmed the `call_tool` `structured_content` is `None` and exercised the `content[0].text` JSON fallback.
- **Files modified:** tests/test_mcp_server.py
- **Verification:** `pytest tests/test_mcp_server.py -x -q` → 1 passed; full suite 105 passed, 1 skipped.
- **Committed in:** bb63ab9

---

**Total deviations:** 1 auto-fixed (1 bug, in test harness — real API-shape finding, exactly what the tracer exists to surface).
**Impact on plan:** No scope creep. The tracer caught a real mcp-2.0.0 API-shape assumption before Plan 02/03 expand the tool set.

## Issues Encountered

- The first tracer run failed on the `list_tools` iteration (see Deviation 1). Resolved by inspecting the live SDK response shape and correcting the test — no production-code change needed; the server/registry/tool path was correct on the first pass.

## User Setup Required

None - no external service configuration required. The `[mcp]` extra is installed in the dev venv; no env vars or credentials needed (all tests offline).

## Next Phase Readiness

- The MCP architecture is validated end-to-end. Plan 02 can now add `fdars_run_method` (+ `run_stdio`) and Plan 03 the `fdars_compare_run` compare loop, reusing HandleRegistry and the proven `MCPServer` + in-process `Client(mcp)` test pattern.
- Open Questions 1 and 2 from 12-RESEARCH.md are now resolved (sync handlers OK; `content[0].text` JSON fallback is the unwrap path). Plan 02/03 tests should use `.tools` and the text-fallback unwrap.
- Note for CI: `pytest-asyncio` and `mcp>=2.0.0` are required for these tests on Python 3.10+; 3.9 runners skip the module cleanly.

## Self-Check: PASSED

All created files exist on disk (pyproject.toml, python/fdars/mcp/{__init__,_registry,server}.py, tests/test_mcp_server.py, this SUMMARY). Both task commits (e55c0bd, bb63ab9) present in git history.

---
*Phase: 12-tool-mcp-surface*
*Completed: 2026-08-09*
