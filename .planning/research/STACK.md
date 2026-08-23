# Stack Research — v8.0 Advisor New Capabilities

**Domain:** Python AI advisor extension — agentic auto-tuning loop, deferred-aspect coverage, comparative method-selection, pipeline diagnostic report, eval strategy
**Researched:** 2026-08-23
**Confidence:** MEDIUM (web-verified; versions confirmed against PyPI and official SDK changelogs)

> **Scope:** This document covers ONLY the stack additions and changes needed for v8.0. The baseline stack (PyO3 0.28, numpy 0.28, fdars-core 0.23.0, mcp>=2.0.0, pydantic>=2, anthropic>=0.72, pytest) is already validated and is not re-researched here.

---

## Decision Summary

All four new capabilities can be built on the **existing stack with no new runtime dependencies**. The only justified changes are:

1. **`anthropic` pin tightened to `>=0.72.0,<1.0`** — the 1.0 release (2026-08-20) drops Python 3.9; fdars must stay on 3.9+ (abi3-py39 wheel guarantee).
2. **`mcp` import path fix in `server.py`** — v2.0.0 renamed the module from `mcp.server` to `mcp.server.mcpserver`; the pin stays `>=2.0.0`.
3. **No new eval library** — the deterministic eval strategy is pure pytest + existing `_check_grounding` pattern + scalar diagnostic comparison.
4. **No agent framework** — the bounded orchestration loop is 15–25 lines of plain Python; any orchestration framework would break the provider-agnostic + LLM-free-compute invariants.

---

## Recommended Stack — What Changes

### Core: MCP SDK — Handle v2 Migration

| Change | Current | Target | Reason |
|--------|---------|--------|--------|
| `mcp` import path | `from mcp.server import MCPServer` | `from mcp.server.mcpserver import MCPServer` | v2.0.0 renamed the module; the decorator API (`@mcp.tool()`) is unchanged |
| `mcp` version pin | `mcp>=2.0.0` | `mcp>=2.0.0` | Already targets v2; no bound change needed |
| `run()` transport arg | `mcp.run(transport="stdio")` | Same | server.py `run_stdio()` already uses this pattern — verify the call site is still correct after import fix |

**Why:** `mcp` 2.0.0 was released 2026-07-28 and is now what `pip install mcp` installs. The pyproject.toml already pins `mcp>=2.0.0`, so the pin is correct. The import in `server.py` may need updating to `from mcp.server.mcpserver import MCPServer`. The `@mcp.tool()` decorator signature is unchanged, so all tool handlers (existing and new) require no modification beyond adding the handler function.

**MCP auto-tuning tool:** The new `fdars_auto_tune` tool follows the exact same pattern as `fdars_compare_run` — synchronous handler (`def`, not `async def`), scalar parameters only, returns a JSON-serialisable dict with handles. The loop runs server-side inside the tool handler; no async machinery is needed because fdars Rust calls release the GIL via PyReadonly wrappers and the loop is CPU-bound Python.

### Core: Anthropic SDK — Guard the Upper Bound

| Pin | Current pyproject.toml | Required v8.0 | Reason |
|-----|------------------------|---------------|--------|
| `[advisor]` extra | `anthropic>=0.72.0` | `anthropic>=0.72.0,<1.0` | anthropic 1.0.0 (2026-08-20) drops Python 3.9, raises requirement to >=3.10; fdars MSRV for Python is 3.9 |
| `output_format` API | Used in `complete_structured` | Keep as-is (0.x) | anthropic 1.0 renames this to `output_config`; the 0.x series API is stable and still available |

**Why:** The anthropic 0.x series (currently ~0.122.x) remains installable on Python 3.9 and keeps the existing `beta.messages.parse(output_format=...)` / `complete_structured` surface intact. The 1.0 line is a major version bump with Python 3.9 removal; adding `<1.0` now prevents silent breakage when users run `pip install fdars[advisor]` and pip resolves to 1.0. A future milestone can handle the 1.0 migration (which would also require auditing the four provider adapters and the mcp surface, since `fdars[mcp]` is already 3.10+).

### Supporting Libraries — No Changes

| Library | Status | Notes |
|---------|--------|-------|
| `pydantic>=2.0` | No change | Existing `Advice`/`Recommendation` schema extended with new models; `model_json_schema()` and `model_validate_json()` stay as the validation mechanism |
| `openai>=1.40,<2.0` | No change | Provider extras unaffected by new capabilities |
| `google-genai>=1.0,<3.0` | No change | Provider extras unaffected |
| `ollama>=0.6.2` | No change | Provider extras unaffected |
| `pytest` + `pytest-asyncio` | No change | Dev extra; pytest-asyncio 1.4.0 supports Python >=3.9; already present |

### Dev/Test — No New Additions

The eval strategy for "good advice" is entirely deterministic and requires no new library:

- **Offline deterministic tests (run in CI, always):**
  - `Advice` schema validation — already enforced by Pydantic in `complete_structured`
  - `_check_grounding` guard — already exists in `_validate.py`; tests assert it does not raise on valid advice
  - Diagnostic improvement metric: `assert diagnostics_after[target_key] > diagnostics_before[target_key]` — pure Python scalar comparison, no network
  - Step-budget enforcement: `assert result["steps_taken"] <= max_steps` — plain integer check
  - Loop terminates on improvement: `assert result["improved"]` — boolean flag in the return dict

- **Env-gated tests (skipped in CI without API key, run on merges or manually):**
  - Full auto-tuning loop end-to-end with a real LLM provider — same pattern as existing `test_advisor_live_integration.py`
  - Comparative method-selection advice grounding — same env-gated pattern

No external eval framework (DeepEval, MLflow, Braintrust, etc.) is warranted. The existing `pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"))` pattern in the test suite is the correct gating mechanism.

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **LangGraph / LangChain** | Framework lock-in; introduces an LLM in the orchestration path by design; incompatible with the provider-agnostic protocol; the framework owns tool-dispatch, displacing the MCP surface | Plain `for step in range(max_steps)` loop in `advisor/_autotuner.py` calling `Provider.complete_structured()` |
| **AutoGen / CrewAI / Smolagents** | Same framework lock-in; multi-agent abstractions are unnecessary overhead for a single bounded loop with one LLM proposing scalar parameter changes | Same plain loop |
| **anthropic>=1.0** | Drops Python 3.9 — breaks the fdars abi3-py39 compatibility guarantee; renames `output_format` → `output_config`, requiring all four provider adapters to be updated simultaneously | Pin `anthropic>=0.72.0,<1.0` until a dedicated migration milestone |
| **Async MCP handlers for auto-tuning** | The existing `fdars_run_method` and `fdars_compare_run` handlers are sync by design (fdars is sync/Rust, GIL released via PyReadonly); switching to async for the new tool would require `asyncio.run_in_executor` with no gain | Keep sync `def` handlers; the bounded loop completes in milliseconds to seconds |
| **DeepEval / Braintrust / MLflow eval** | Heavyweight eval frameworks with their own LLM-judge pipelines and network dependencies; the fdars eval is "did the target diagnostic improve?" — a scalar comparison | Pure pytest assertions on before/after diagnostic dicts |
| **httpx / aiohttp direct** | The Provider protocol already wraps the HTTP client inside each adapter; adding a raw HTTP client in the advisor layer would bypass the validate-and-retry + grounding guard chain | Use the existing `Provider.complete_structured()` path |
| **Any vector store or embedding library** | Comparative method-selection is a ranking over `build_diagnostics` output dicts — structured scalars, not semantic search over text | Pure Python sorting/ranking on diagnostic scalar values |

---

## Auto-Tuning Loop Design — Stack Implications

The closed-loop auto-tuning is a **pure Python orchestration loop** that calls the existing Provider protocol for parameter proposals and fdars/MCP runner for execution. No new library is needed because:

1. **LLM call path** — uses `advise()` / `Provider.complete_structured(TuneProposal, ...)` with a new `TuneProposal` Pydantic schema. Same `_check_grounding` guard applies.
2. **Execution path** — calls `run_method()` from `mcp/_runner.py` directly (Python API) or dispatches via `fdars_run_method` MCP tool (agentic surface). No new fdars bindings required; the six runnable methods already cover the primary tuning targets.
3. **Termination** — `for step in range(max_steps)` with an `if diagnostic_improved: break` check. The `max_steps` parameter is a required integer argument to `auto_tune()`.
4. **State** — carried in a plain Python dict `{"history": [...], "best_result_id": str, "steps_taken": int, "improved": bool}`; no external state store.

**MCP surface for auto-tuning:** A new `fdars_auto_tune` tool in `server.py` with the same flat-scalar parameter design as `fdars_compare_run`. The tool executes the entire bounded loop inside the synchronous handler and returns a summary dict. The LLM that calls this MCP tool is the orchestrating agent — it is NOT inside the compute path. The Provider called inside `auto_tune()` for parameter proposals is in the **Python API path only**; the MCP tool itself stays provably LLM-free (every computation runs fdars; the loop logic is pure Python). This preserves the MCP-LLM-free boundary.

---

## New Pydantic Schemas Required (additions to `_schema.py`)

No new library. Two new Pydantic model classes in `advisor/_schema.py`:

| Schema | Fields | Used By |
|--------|--------|---------|
| `TuneProposal` | `param_name: str`, `param_value: float \| int`, `rationale: str`, `expected_effect: str` | `auto_tune()` — LLM returns this as structured output |
| `TuneResult` | `steps_taken: int`, `improved: bool`, `target_metric_before: float`, `target_metric_after: float`, `history: list[dict]` | Return type of `auto_tune()` — fully JSON-serialisable |

These are additions to the existing `_schema.py`, not replacements of `Advice`/`Recommendation`.

---

## Version Compatibility Matrix

| Package | Current Pin | v8.0 Pin | Python Constraint | Notes |
|---------|-------------|----------|-------------------|-------|
| `mcp` | `>=2.0.0` | `>=2.0.0` | `>=3.10` (mcp extra already gated) | One-line import path fix in server.py required |
| `anthropic` | `>=0.72.0` | `>=0.72.0,<1.0` | `>=3.9` for 0.x; 1.0 requires `>=3.10` | Add `<1.0` upper bound — highest priority change |
| `pydantic` | `>=2.0` | `>=2.0` | `>=3.9` | No change; new schemas use same BaseModel API |
| `openai` | `>=1.40,<2.0` | `>=1.40,<2.0` | `>=3.9` | No change |
| `google-genai` | `>=1.0,<3.0` | `>=1.0,<3.0` | `>=3.10` (already enforced by adapter) | No change |
| `ollama` | `>=0.6.2` | `>=0.6.2` | `>=3.9` | No change |
| `pytest-asyncio` | present in dev | no change | `>=3.9` | Already present; latest 1.4.0 |

---

## Installation Delta (pyproject.toml changes only)

```toml
# Change: tighten anthropic upper bound to prevent 1.0 breakage on Python 3.9
advisor = ["anthropic>=0.72.0,<1.0", "pydantic>=2.0"]

# No other changes to optional-dependencies.
# New auto-tuning Python API uses no new extras.
# New fdars_auto_tune MCP tool reuses the existing [mcp] extra.
```

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| Plain `for` loop in `advisor/_autotuner.py` | LangGraph stateful graph | LangGraph owns the tool-dispatch loop, displacing the MCP surface; framework lock-in; cannot guarantee LLM-free compute path |
| `Provider.complete_structured(TuneProposal, ...)` | Anthropic tool_use with input_schema | Tool_use would embed the parameter-proposal schema in the Anthropic-specific API call and require the Anthropic adapter to be extended without benefiting other providers; the existing `complete_structured` path works across all four providers |
| Pure pytest assertions for eval | DeepEval / Braintrust | Both require network calls or LLM judges; CI must be offline-capable; the deterministic "did target diagnostic improve" check is sufficient and auditable |
| `anthropic>=0.72.0,<1.0` | Upgrading to `anthropic>=1.0` | anthropic 1.0 drops Python 3.9, breaking the fdars abi3-py39 guarantee and the full test matrix |
| Keeping sync MCP handlers | Async `async def` handlers | fdars Rust functions are synchronous; wrapping in executor adds overhead with no benefit; existing sync handlers work correctly |

---

## Sources

- MCP Python SDK releases — [github.com/modelcontextprotocol/python-sdk/releases](https://github.com/modelcontextprotocol/python-sdk/releases) — v2.0.0 stable confirmed 2026-07-28 (MEDIUM confidence, web-verified)
- MCP v2 migration guide — [py.sdk.modelcontextprotocol.io/migration/](https://py.sdk.modelcontextprotocol.io/migration/) — import path changes and decorator continuity confirmed (MEDIUM confidence, webfetch)
- MCP v2 what's new — [py.sdk.modelcontextprotocol.io/whats-new/](https://py.sdk.modelcontextprotocol.io/whats-new/) — server API and stdio transport confirmed (MEDIUM confidence, webfetch)
- Anthropic SDK PyPI — [pypi.org/project/anthropic/](https://pypi.org/project/anthropic/) — 1.0.0 released 2026-08-20, Python >=3.10 requirement confirmed (MEDIUM confidence, webfetch)
- Anthropic SDK 1.0 breaking changes — [github.com/anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) — output_format → output_config, Python 3.9 removed (MEDIUM confidence, web-verified via multiple issue trackers)
- Pydantic PyPI — [pypi.org/project/pydantic/](https://pypi.org/project/pydantic/) — v2.11 current, stable API (MEDIUM confidence, web)
- Bounded agentic loop patterns — [tinyagents.dev/blog/what-is-the-agent-loop](https://tinyagents.dev/blog/what-is-the-agent-loop) + [medium.com/@oshan.nanayakkara](https://medium.com/@oshan.nanayakkara/agentic-loop-in-python-a-practical-guide-to-multi-turn-ai-agents-111f59909548) — step-budget loop, no framework needed (LOW confidence, web)
- Deterministic eval — [arxiv.org/pdf/2606.22737](https://arxiv.org/pdf/2606.22737) GroundEval deterministic scoring approach; schema-validity + citation-check as baseline (LOW confidence, web)

---

*Stack research for: fdars v8.0 Advisor — New Capabilities*
*Researched: 2026-08-23*
