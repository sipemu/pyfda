---
phase: 12-tool-mcp-surface
verified: 2026-08-09T22:00:00Z
status: passed
score: 4/4
behavior_unverified: 0
overrides_applied: 0
re_verification: null
---

# Phase 12: Tool MCP Surface — Verification Report

**Phase Goal:** An agent can re-run fdars via tools and compare before/after diagnostics through an MCP server.
**Verified:** 2026-08-09T22:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Coarse-grained tool definitions `fdars_build_diagnostics` and `fdars_run_method` exist with strict input/output schemas and pass data by reference (handles, not arrays) | VERIFIED | `@mcp.tool()` on both in `server.py:54` and `server.py:139`; type-hint-derived JSON schemas; `fdars_run_method` returns only `{"result_id", "method"}` confirmed via live `call_tool` invocation — no arrays in JSON output |
| 2 | An MCP server exposes those tools and a client can list and invoke them successfully | VERIFIED | `MCPServer("fdars-advisor")` in `server.py:41`; `list_tools()` returns all three tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`); 7 MCP tests pass on Python 3.10+, 1 skipped on 3.9 as expected; `pytest tests/test_mcp_server.py -q` exits 0 |
| 3 | An agentic re-run/compare loop (`fdars_compare_run`) applies a suggested parameter, re-runs the method, and returns a before/after diagnostics comparison — the delta is observable | VERIFIED | `fdars_compare_run` in `server.py:239` delegates to `_compare.compare_run`; live invocation returns `{"before_result_id", "after_result_id", "before", "after", "delta"}` with 4 scalar keys (gcv_aic_approx, gcv_bic_approx, optimal_gcv, optimal_edf); `examples/mcp_recipe.py` exits 0 printing the observable delta |
| 4 | The compute path stays deterministic (fdars does the numbers; the model only orchestrates) and recommendations still cite diagnostics per the grounding invariant | VERIFIED | No LLM call in any MCP tool handler; all numbers come from real fdars functions (`kmeans_fd`, `pspline_fit_gcv`, `basis_nbasis_cv`, `regression.fpca`, `karcher_mean`); `test_compare_run_delta_sign` asserts sign of a specific delta key without any live Claude call; recipe exits 0 with `"No ANTHROPIC_API_KEY was required"` |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` [mcp] extra | `mcp>=2.0.0` with Python 3.10+ note | VERIFIED | Line 43: `mcp = ["mcp>=2.0.0"]` with comment "requires Python >=3.10" on line 42 |
| `python/fdars/mcp/__init__.py` | Python 3.10+ ImportError guard, re-exports HandleRegistry/registry/server | VERIFIED | Guard fires at `sys.version_info < (3, 10)` with message naming `fdars[mcp] requires Python 3.10+`; deferred imports to HandleRegistry, registry, server |
| `python/fdars/mcp/_registry.py` | HandleRegistry class + module-level registry singleton | VERIFIED | 152 lines; `HandleRegistry` class with `store_dataset`/`get_dataset`/`store_result`/`get_result`/`clear`; `registry = HandleRegistry()` singleton; `KeyError` naming offending id on miss (T-12-01) |
| `python/fdars/mcp/server.py` | MCPServer instance + all three `@mcp.tool()` handlers + `run_stdio()` | VERIFIED | 383 lines; `mcp = MCPServer("fdars-advisor")`; three synchronous `@mcp.tool()` decorated handlers; `run_stdio()` calling `mcp.run(transport="stdio")`; `if __name__ == "__main__"` guard |
| `python/fdars/mcp/_runner.py` | `run_method` dispatch over five fdars methods | VERIFIED | 205 lines; dispatches `alignment`→`karcher_mean`, `basis`→`basis_nbasis_cv`, `smoothing`→`pspline_fit_gcv`, `fpca`→`regression.fpca`, `clustering`→`kmeans_fd`; closed-set method validation (T-12-02); scalar-only params (T-12-03); `__all__ = ["run_method"]` |
| `python/fdars/mcp/_compare.py` | `compare_run` delta builder | VERIFIED | 192 lines; allowlist-validates `params_after` keys (T-12-03); fetches before from registry; re-runs via `run_method`; builds `build_diagnostics` for both; delta = `after[k] - before[k]` for finite scalar float/int keys only; `math.isfinite` filter; `__all__ = ["compare_run"]` |
| `tests/test_mcp_server.py` | Module-level skipif(<3.10); 7 tests covering all three plans | VERIFIED | 451 lines; `pytestmark = pytest.mark.skipif(sys.version_info < (3, 10), ...)`; autouse `registry.clear()` fixture; 7 async tests: tracer, list/call both tools, run all 5 methods, build diagnostics all 5 methods, compare unit allowlist, compare smoothing, compare delta sign |
| `examples/mcp_recipe.py` | End-to-end offline recipe, Python 3.9 guard, exits 0 | VERIFIED | 121 lines; `sys.version_info < (3, 10)` guard exits 0 on 3.9 with message; drives `registry.store_dataset` → `run_method` → `compare_run` → prints 4 scalar delta keys; exits 0 confirmed live |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `server.py:fdars_build_diagnostics` | `advisor.build_diagnostics` | `registry.get_dataset` → `build_diagnostics(result, method, ...)` | WIRED | `server.py:107-131`; delegates entirely, does not reimplement |
| `server.py:fdars_run_method` | `_runner.run_method` | `run_method(dataset_id, method, ...)` → `registry.store_result` → `{"result_id", "method"}` | WIRED | `server.py:213-231`; arrays stay in registry, only handle crosses JSON boundary |
| `server.py:fdars_compare_run` | `_compare.compare_run` | assembles `params_after` from non-None typed args → `compare_run(dataset_id, method_lc, before_result_id, params_after)` | WIRED | `server.py:336-351`; flat-param schema assembled locally then delegated |
| `_compare.compare_run` | `_runner.run_method` + `advisor.build_diagnostics` | fetches before from `registry.get_result` → `run_method` → `build_diagnostics` ×2 → delta dict | WIRED | `_compare.py:148-183`; complete chain confirmed |
| `fdars_run_method JSON return` | no arrays | only `{"result_id", "method"}` | WIRED | Live check confirmed: `list(result.keys()) == ['result_id', 'method']` |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `_runner.run_method` (clustering) | `cluster`, `centers`, `k` | `fdars.clustering.kmeans_fd(data, argvals, k=..., seed=...)` | Yes — real Rust compute | FLOWING |
| `_runner.run_method` (smoothing) | `fitted`, `edf`, `gcv`, `aic`, `bic` | `fdars.basis.pspline_fit_gcv(data, argvals, n_basis=...)` | Yes — real Rust compute | FLOWING |
| `_runner.run_method` (fpca) | `scores`, `rotation`, `singular_values` | `fdars.regression.fpca(data, argvals, n_comp=...)` | Yes — real Rust compute | FLOWING |
| `_runner.run_method` (basis) | `optimal_nbasis`, `scores`, `criterion` | `fdars.basis.basis_nbasis_cv(data, argvals, lambda_=...)` | Yes — real Rust compute | FLOWING |
| `_runner.run_method` (alignment) | `aligned_data`, `mean`, `converged`, `n_iter` | `fdars.alignment.karcher_mean(data, argvals, lambda_=...)` | Yes — real Rust compute | FLOWING |
| `_compare.compare_run` delta | 4 scalar keys: `gcv_aic_approx`, `gcv_bic_approx`, `optimal_gcv`, `optimal_edf` | `build_diagnostics` (Branch A-prime in `advisor.py:531-554`) on real fdars result | Yes — fdars-computed, confirmed live | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 7 MCP tests pass | `.venv/bin/python -m pytest tests/test_mcp_server.py -q` | `7 passed in 25.53s` | PASS |
| Full suite (111 pass, 1 skip) | `.venv/bin/python -m pytest tests/ -q` | `111 passed, 1 skipped in 22.27s` | PASS |
| mcp_recipe.py exits 0 with delta | `.venv/bin/python examples/mcp_recipe.py` | Exits 0; prints delta with 4 keys (gcv_aic_approx, gcv_bic_approx, optimal_gcv, optimal_edf) | PASS |
| list_tools returns all 3 tools | Python: `[t.name for t in tr.tools]` | `['fdars_build_diagnostics', 'fdars_run_method', 'fdars_compare_run']` | PASS |
| by-reference invariant | `call_tool("fdars_run_method", ...)` returns keys | `['result_id', 'method']` — no arrays | PASS |
| delta non-empty and observable | `call_tool("fdars_compare_run", ...)` delta keys | `['gcv_aic_approx', 'gcv_bic_approx', 'optimal_gcv', 'optimal_edf']` with non-zero values | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| TOOL-01 | 12-01, 12-02 | Coarse-grained tool definitions with strict schemas; pass data by reference (handles, not arrays) | SATISFIED | `fdars_build_diagnostics` + `fdars_run_method` with type-hint-derived schemas; `fdars_run_method` returns only `{result_id, method}`; HandleRegistry enforces by-reference invariant; all five methods dispatch to real fdars functions |
| TOOL-02 | 12-01, 12-02 | An MCP server exposes those tools; client can list and invoke them | SATISFIED | `MCPServer("fdars-advisor")` with 3 `@mcp.tool()` handlers; in-process `Client(mcp)` lists and invokes all tools in tests; `run_stdio()` provides the stdio entry point; Python 3.9 guard raises clear ImportError; MCP module not registered in `fdars.__init__` (no side effects) |
| TOOL-03 | 12-03 | Agentic re-run/compare loop: apply suggested param, re-run, compare before/after diagnostics | SATISFIED | `fdars_compare_run` tool + `_compare.compare_run`; returns `{before_result_id, after_result_id, before, after, delta}`; delta confirmed non-empty with correct sign; `test_compare_run_delta_sign` asserts deterministic numeric assertion without LLM |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | No TBD/FIXME/XXX markers; no FastMCP usage; no async def tool handlers; no hardcoded empty arrays; no return null stubs | — | Clean |

No debt markers, no stubs, no placeholder implementations found in any of the 7 modified/created files.

---

### Human Verification Required

None. All success criteria are fully verifiable programmatically and have been confirmed by live test execution and behavioral spot-checks. No visual, UI, or external-service-dependent behavior is involved.

---

## Gaps Summary

No gaps. All four phase success criteria are met:

1. Tool definitions exist with strict schemas and the by-reference invariant is enforced and tested.
2. The MCP server exposes all three tools and an in-process client can list and invoke them (7 tests pass).
3. The `fdars_compare_run` compare loop returns an observable before/after/delta dict — the delta is non-empty and correct in sign for a known parameter change.
4. The compute path is deterministic — every number comes from fdars; no LLM is in the critical path; `examples/mcp_recipe.py` exits 0 offline printing 4 scalar delta keys.

Requirements TOOL-01, TOOL-02, and TOOL-03 are all marked Complete in REQUIREMENTS.md and are verified in the codebase.

---

### Phase Commits Verified

All 9 commits documented in the SUMMARYs are confirmed in git history:

- `e55c0bd` feat(12-01): TRACER — fdars MCP surface
- `bb63ab9` fix(12-01): list_tools .tools iteration fix
- `190fa9e` feat(12-02): `_runner.py`
- `161854e` feat(12-02): server.py extensions
- `55b38b3` test(12-02): extended tests
- `e64ca20` test(12-03): failing tests (TDD RED)
- `599a9cf` feat(12-03): `_compare.py` (TDD GREEN)
- `a3b6fe7` feat(12-03): `fdars_compare_run` + Branch A-prime advisor fix
- `e6786be` feat(12-03): tests + `mcp_recipe.py`

---

_Verified: 2026-08-09T22:00:00Z_
_Verifier: Claude (gsd-verifier)_
