# Phase 12: Tool / MCP Surface - Research

**Researched:** 2026-08-09
**Domain:** MCP (Model Context Protocol) Python SDK — stdio server, tool definitions, by-reference data passing, agentic re-run/compare loop
**Confidence:** MEDIUM

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **MCP transport = stdio only.** Local stdio transport, matching the local/CI usage of the
  advisor. HTTP/SSE (hosted) is explicitly deferred / out of scope for v2.0. Keep the
  tool/handler layer transport-agnostic so a future HTTP transport could be added without
  rewriting tool logic, but only wire stdio now.
- **Compute stays deterministic.** fdars does all numbers; the model only orchestrates. The
  agentic re-run/compare loop must re-run the actual fdars method and diff diagnostics — no
  fabricated numbers. Grounding invariant holds: recommendations cite diagnostic values.
- **Pass data by reference.** Tools must not shuttle large arrays through the model. Use a
  reference/handle scheme (e.g. dataset/result IDs or file paths) so `fdars_run_method` and
  `fdars_build_diagnostics` exchange references, not full matrices, across the tool boundary.
- **Wrap advisor.py, do not reimplement.** The MCP tools must call `advisor.build_diagnostics`,
  `advisor.advise`, and `advisor.describe_cluster_differences` from `python/fdars/advisor.py`.
- **Phase 13 (Agent Skill) is out of scope.** Design tools so a future skill can drive them.

### Claude's Discretion

- File layout within `python/fdars/mcp/` (module structure).
- Handle registry implementation detail (in-process dict vs other).
- Test file location and naming.
- Whether `fdars_run_method` exposes all five methods or a subset.

### Deferred Ideas (OUT OF SCOPE)

- HTTP/REST service surface
- Hosted/cloud deployment
- Non-Anthropic model providers
- Autonomous changes to user data
- Agent Skill (SKILL.md) — Phase 13
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-01 | Coarse-grained tool definitions (`fdars_build_diagnostics`, `fdars_run_method`) with strict schemas | MCP `inputSchema`/`outputSchema` pattern; advisor.py's five supported methods and their diagnostics dict shapes — all verified by reading source |
| TOOL-02 | An MCP server (stdio) exposing those tools that a client can list + invoke | `MCPServer` high-level API with `@mcp.tool()` decorator; `mcp.run(transport="stdio")`; in-process `Client(mcp)` for testing |
| TOOL-03 | An agentic re-run/compare loop that applies a suggested parameter, re-runs the method, and returns an observable before/after diagnostics delta | A `fdars_compare_diagnostics` tool or a dedicated compare step; deterministic delta dict; CI-testable without a live Claude call |
</phase_requirements>

---

## Summary

Phase 12 builds the Tool/MCP surface of the fdars advisor: two coarse-grained MCP tools
(`fdars_build_diagnostics`, `fdars_run_method`) plus a stdio MCP server and an agentic
re-run/compare loop. The advisor's deterministic `build_diagnostics` layer (Phase 10/11) is
already complete; this phase wraps it so a language model can call it via the MCP protocol.

The Python MCP SDK (`mcp` package, v2.0.0) provides a `MCPServer` high-level class with a
`@mcp.tool()` decorator that turns typed Python functions into MCP tools with auto-generated
JSON Schemas. The in-process `Client(mcp)` pattern allows tool listing and invocation in
pytest without spawning a subprocess, satisfying the "no network in CI" constraint from
PYAPI-02. The grounding invariant — fdars computes, the model orchestrates — is enforced by
having each tool call the real fdars API and returning JSON-serialisable diagnostics dicts.

The by-reference constraint is satisfied by an in-process `HandleRegistry` (a module-level
dict) that stores numpy arrays and result dicts under opaque string IDs. Tools exchange only
IDs across the MCP boundary; the actual arrays never appear in tool arguments. This is correct
for a stdio (single-process) server because client and server share the same Python process
when using the in-memory `Client(mcp)` test pattern.

**Primary recommendation:** Use `MCPServer` (high-level API) with `@mcp.tool()` decorators.
Define tools in `python/fdars/mcp/server.py`, the handle registry in
`python/fdars/mcp/_registry.py`, and the agentic compare loop in
`python/fdars/mcp/_compare.py`. Gate the entire `mcp/` subpackage behind
`pip install fdars[mcp]` (a new optional extra alongside `[advisor]`), following the same
pattern used for the `[advisor]` extra.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| fdars computation (karcher_mean, kmeans_fd, pspline_fit_gcv, …) | Python library (fdars native) | — | Numbers stay in fdars; tools call them directly |
| Diagnostics building (`build_diagnostics`) | Python library (advisor.py) | — | Already implemented; tools delegate here |
| MCP tool definitions + schemas | MCP server layer (`mcp/server.py`) | — | Decorator + type hints; no custom JSON Schema code needed |
| Stdio transport / protocol | MCP SDK (`MCPServer.run()`) | — | SDK handles framing; tool layer is transport-agnostic |
| Handle registry (by-reference data) | In-process module (`mcp/_registry.py`) | — | Single-process stdio; dict is safe and CI-testable |
| Agentic compare loop | MCP tool (`fdars_compare_run`) | mcp/_compare.py helper | Orchestrated by the model; compare logic is a pure Python helper |
| In-process testing | MCP SDK `Client(mcp)` | pytest | No subprocess, no network; same pattern as SDK test suite |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `mcp` | 2.0.0 | MCP Python SDK — `MCPServer`, `Client`, stdio transport | Official Anthropic/MCP Foundation SDK [CITED: pypi.org/project/mcp] |
| `anyio` | >=4.10 (transitive) | Async I/O backend used by mcp internally | Pulled in by mcp; not directly imported by our code [ASSUMED] |
| `pydantic` | >=2.12.0 (transitive) | Schema validation inside mcp | Already in `[advisor]` extra; mcp 2.0.0 requires pydantic>=2.12.0 [VERIFIED: pip dry-run output] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest-asyncio` | latest | async pytest tests for the async client pattern | Needed because `Client(mcp)` is async [ASSUMED] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `MCPServer` high-level API | low-level `Server` class + manual JSON-RPC | Low-level gives more control but requires manual type-conversion and request parsing; high-level is idiomatic for v2.0 SDK |
| `mcp` optional extra | direct `dependencies` in pyproject.toml | Making it optional keeps fdars importable without mcp (same principle as `[advisor]`); correct because fdars is primarily a computation library |
| in-process `Client(mcp)` | stdio subprocess | Subprocess requires spawning the server binary; in-process has no overhead and is CI-safe |

**Installation (new `[mcp]` extra):**
```bash
pip install fdars[mcp]          # MCP server only
pip install fdars[advisor,mcp]  # advisor + MCP (typical for agentic use)
```

**Version verification:** `mcp==2.0.0` confirmed on PyPI via `pip index versions mcp`.
[VERIFIED: pip registry] — latest version 2.0.0, published 2026-07-28.

---

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `mcp` | PyPI | ~10 months (first release Nov 2024, current 2026-07-28) | unknown (legitimacy check: SUS/too-new/unknown-downloads) | modelcontextprotocol.io → github.com/modelcontextprotocol/python-sdk | SUS | Flagged — planner must add checkpoint:human-verify before install |

**Packages removed due to [SLOP] verdict:** none

**Packages flagged as suspicious [SUS]:** `mcp` — the legitimacy gate returned `SUS` with
reasons `too-new` and `unknown-downloads`. However, `mcp` is the **official Model Context
Protocol Python SDK** from Anthropic and the MCP Foundation, hosted at
github.com/modelcontextprotocol/python-sdk and documented at py.sdk.modelcontextprotocol.io.
The "too-new" signal reflects that the seam's data has a short history window; the project
itself is well-established. The planner MUST include a `checkpoint:human-verify` before the
`pip install fdars[mcp]` Wave 0 task, consistent with the seam protocol — but the package
is safe to use. [CITED: pypi.org/project/mcp/2.0.0, github.com/modelcontextprotocol/python-sdk]

---

## Architecture Patterns

### System Architecture Diagram

```
[Model / Agent]
      |
      | MCP tool call (JSON-RPC over stdio)
      v
[MCPServer (mcp/server.py)]
  fdars_build_diagnostics(dataset_id, method, **params)
  fdars_run_method(dataset_id, method, **params)
  fdars_compare_run(dataset_id, method, before_result_id, params_before, params_after)
      |
      | handle lookup
      v
[HandleRegistry (mcp/_registry.py)]  <-- in-process dict; arrays/results stored here
      |
      | numpy arrays
      v
[advisor.py] --> build_diagnostics() --> diagnostics dict (JSON-serialisable)
[fdars.alignment / fdars.basis / fdars.clustering / …] --> result dict
      |
      | structured JSON response (diagnostics dict or delta dict)
      v
[Model / Agent] -- reasons over numbers, never fabricates them
```

**Data flow for TOOL-03 (agentic re-run/compare):**

```
1. Agent calls fdars_build_diagnostics(dataset_id="...", method="smoothing")
   → returns {before_result_id: "r-abc", diagnostics: {...}}
2. Agent calls fdars_compare_run(dataset_id="...", method="smoothing",
     before_result_id="r-abc", params_after={"lambda_": 0.1})
   → runs pspline_fit_gcv with new lambda_, stores result,
     calls build_diagnostics on both, returns delta dict:
     {before: {...diagnostics...}, after: {...diagnostics...}, delta: {...diffs...}}
3. Agent observes observable delta (optimal_lambda before vs after, GCV change, etc.)
```

### Recommended Project Structure

```
python/fdars/
├── mcp/
│   ├── __init__.py        # exports: server, HandleRegistry, run_stdio
│   ├── _registry.py       # HandleRegistry — in-process handle store
│   ├── _runner.py         # fdars method runners (alignment, basis, smoothing, clustering, fpca)
│   ├── _compare.py        # compare_run() helper — before/after delta builder
│   └── server.py          # MCPServer instance + @mcp.tool() definitions
tests/
├── test_mcp_server.py     # pytest tests using Client(mcp) in-process
examples/
└── mcp_recipe.py          # end-to-end recipe (mirrors advisor_recipe.py)
```

### Pattern 1: MCPServer Tool Registration with Type-Hint Schema

**What:** `@mcp.tool()` converts a Python function's type hints and docstring into an MCP
`inputSchema`. No hand-written JSON Schema required.

**When to use:** All tool definitions in `server.py`.

```python
# Source: github.com/modelcontextprotocol/python-sdk README + mcpserver/server.py
from mcp.server import MCPServer

mcp = MCPServer("fdars-advisor")

@mcp.tool()
def fdars_build_diagnostics(
    dataset_id: str,
    method: str,
    result_id: str | None = None,
) -> dict:
    """Build deterministic diagnostics for an fdars result.

    Parameters map to advisor.build_diagnostics(). Data is accessed
    by reference via dataset_id / result_id from the handle registry.
    Returns a JSON-serialisable diagnostics dict.
    """
    from fdars.mcp._registry import registry
    from fdars.advisor import build_diagnostics
    # ... resolve handles, call build_diagnostics, return dict
    ...
```

[CITED: github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/mcpserver/server.py]

### Pattern 2: stdio Entry Point

**What:** `MCPServer.run(transport="stdio")` is synchronous and blocks until the connection
closes. Wire it at `if __name__ == "__main__"` in server.py or expose as a `run_stdio()`
function callable from a console-script.

```python
# Source: mcp.server.mcpserver.server.MCPServer.run signature (verified)
def run_stdio():
    """Entry point for stdio MCP server — called by fdars-mcp-server console script."""
    mcp.run(transport="stdio")   # synchronous; blocks until EOF on stdin

if __name__ == "__main__":
    run_stdio()
```

[CITED: py.sdk.modelcontextprotocol.io]

### Pattern 3: In-Process Client for Testing

**What:** `Client(mcp)` accepts the `MCPServer` instance directly, providing an in-memory
transport with zero subprocess overhead. Fully CI-safe; no network, no API key.

```python
# Source: github.com/modelcontextprotocol/python-sdk README (verified in-process pattern)
import asyncio
import pytest
from mcp import Client
from fdars.mcp.server import mcp  # the MCPServer instance

@pytest.mark.asyncio
async def test_list_tools():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = [t.name for t in tools.tools]
        assert "fdars_build_diagnostics" in names
        assert "fdars_run_method" in names

@pytest.mark.asyncio
async def test_build_diagnostics_offline():
    from fdars.mcp._registry import registry
    ds_id = registry.store_dataset(data_array, argvals_array)
    async with Client(mcp) as client:
        result = await client.call_tool(
            "fdars_build_diagnostics",
            {"dataset_id": ds_id, "method": "clustering"}
        )
        diag = result.structured_content
        assert diag["method"] == "clustering"
```

[CITED: github.com/modelcontextprotocol/python-sdk README]

### Pattern 4: Handle Registry (by-reference data passing)

**What:** An in-process dict keyed by opaque string IDs. `store_dataset()` and
`store_result()` return IDs; `get_dataset()` and `get_result()` return the actual arrays.
For a stdio (single-process) server this is the correct approach: no serialisation overhead,
no file I/O, no network.

```python
# Source: designed for this phase — no existing pattern in SDK
# python/fdars/mcp/_registry.py
import uuid
from typing import Any
import numpy as np

class HandleRegistry:
    def __init__(self):
        self._datasets: dict[str, tuple[np.ndarray, np.ndarray]] = {}  # id -> (data, argvals)
        self._results: dict[str, dict] = {}  # id -> result dict

    def store_dataset(self, data: np.ndarray, argvals: np.ndarray) -> str:
        ds_id = f"ds-{uuid.uuid4().hex[:8]}"
        self._datasets[ds_id] = (data, argvals)
        return ds_id

    def get_dataset(self, ds_id: str) -> tuple[np.ndarray, np.ndarray]:
        if ds_id not in self._datasets:
            raise KeyError(f"Unknown dataset_id: {ds_id!r}")
        return self._datasets[ds_id]

    def store_result(self, result: dict) -> str:
        r_id = f"r-{uuid.uuid4().hex[:8]}"
        self._results[r_id] = result
        return r_id

    def get_result(self, r_id: str) -> dict:
        if r_id not in self._results:
            raise KeyError(f"Unknown result_id: {r_id!r}")
        return self._results[r_id]

    def clear(self):
        self._datasets.clear()
        self._results.clear()

registry = HandleRegistry()  # module-level singleton
```

[ASSUMED — designed here; no existing pattern in MCP SDK]

### Anti-Patterns to Avoid

- **Embedding numpy arrays in tool arguments:** Even small arrays embedded in JSON violate
  the "pass by reference" constraint and will fail for real datasets (365-point × 35-obs
  Canadian Weather = 12,775 floats per call). Always use handles.
- **Reimplementing `build_diagnostics` inside the tool:** The tool MUST call
  `advisor.build_diagnostics`; duplicating diagnostics logic breaks the single-core invariant.
- **Async tool handlers with blocking fdars calls:** `fdars` is synchronous Rust; calling it
  directly in an async tool handler is fine (GIL is released in PyReadonly wrappers). Do not
  wrap in `asyncio.run_in_executor` unless profiling shows a problem.
- **MCPServer in `__init__.py`:** The `mcp` server instance must live in `mcp/server.py`,
  not `__init__.py`, so tests can import it without triggering side effects from `fdars.__init__`.
- **Registering `mcp` in `fdars._submodule_names`:** The `mcp` subpackage is a pure-Python
  module (not a native Rust submodule) — follow the advisor pattern: import explicitly in
  `__init__.py` with `_sys.modules["fdars.mcp"] = mcp_module` rather than adding to
  `_submodule_names`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema for tool inputs | Manual `inputSchema` dicts | `@mcp.tool()` with type hints | SDK derives schema from function signature; type hints ARE the schema |
| stdio framing / JSON-RPC | Custom stdio protocol | `MCPServer.run(transport="stdio")` | The SDK handles all protocol details, buffering, and error codes |
| Tool result serialisation | `json.dumps(...)` in return | Return plain Python dict/list/str | SDK serialises `structured_content`; `dict` return is supported |
| In-process test transport | Subprocess + pipe | `Client(mcp)` in-memory | SDK provides this pattern; no subprocess needed |
| Async event loop management | `asyncio.run()` in tests | `pytest-asyncio` with `@pytest.mark.asyncio` | Cleaner fixture lifecycle; consistent with SDK test suite |

**Key insight:** The MCP SDK v2.0 high-level API (`MCPServer`) is designed so tool authors write
plain Python functions with type hints — protocol mechanics are invisible. All complexity lives
in the SDK, not in our tool code.

---

## Advisor.py: Verified Method Signatures and Diagnostics Shapes

These values were verified by reading `python/fdars/advisor.py` in this session.

### Supported methods [VERIFIED: python/fdars/advisor.py:226]

```python
_supported = {"alignment", "fpca", "basis", "smoothing", "clustering"}
```
Verbatim quote from line 226: `_supported = {"alignment", "fpca", "basis", "smoothing", "clustering"}`

`fdars_run_method` MUST support exactly these five method names.

### `build_diagnostics` signature [VERIFIED: python/fdars/advisor.py:188-195]

```python
def build_diagnostics(
    result,
    method: str,
    *,
    argvals=None,
    **kwargs,
) -> dict:
```

Returns a plain-Python, JSON-serialisable `dict`. Key output keys per method:

**alignment** [VERIFIED: python/fdars/advisor.py:265-342]:
`method`, `mean_length`, `mean_min`, `mean_max`, `mean_avg`, `mean_curve`,
`n_obs`, `amplitude_distances`, `phase_distances`, `amplitude_mean`, `amplitude_max`,
`phase_mean`, `phase_max`, `converged`, `n_iter`

**fpca** [VERIFIED: python/fdars/advisor.py:349-418]:
`method`, `n_components`, `n_obs`, `eigenvalues`, `explained_variance_ratio`,
`cumulative_variance_explained`, `total_variance`, `phase_leakage_indicator`,
`phase_leakage_flagged`

**basis** [VERIFIED: python/fdars/advisor.py:426-516]:
`method`, `n_basis_values`, `gcv_curve`, `edf`, `gcv_aic_approx`, `gcv_bic_approx`,
`optimal_n_basis`, `optimal_gcv`, `optimal_edf`

**smoothing** [VERIFIED: python/fdars/advisor.py:519-600]:
`method`, `lambda_values`, `gcv_curve`, `edf`, `gcv_aic_approx`, `gcv_bic_approx`,
`optimal_lambda`, `optimal_gcv`, `optimal_edf`

**clustering** [VERIFIED: python/fdars/advisor.py:607-715]:
`method`, `k`, `cluster_means`, `cluster_sizes`, `pairwise_amplitude_distance`,
`pairwise_phase_distance`, `mean_amplitude_separation`, `mean_phase_separation`

### `advise` signature [VERIFIED: python/fdars/advisor.py:915-922]

```python
def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
) -> Advice:
```

`task` accepts: `"interpretation"`, `"parameter"`, `"method"` [VERIFIED: python/fdars/advisor.py:835]
Verbatim: `_supported_tasks = {"interpretation", "parameter", "method"}`

### `describe_cluster_differences` signature [VERIFIED: python/fdars/advisor.py:989-996]

```python
def describe_cluster_differences(
    result,
    *,
    argvals=None,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    run_llm: bool = True,
    **kwargs,
):
```

Returns `Advice` when `run_llm=True`, raw `dict` when `run_llm=False`.

---

## Tool Schema Design

### `fdars_build_diagnostics`

```python
@mcp.tool()
def fdars_build_diagnostics(
    dataset_id: str,
    method: str,
    result_id: str | None = None,
    with_argvals: bool = True,
) -> dict:
    """Build offline diagnostics for an fdars result.

    dataset_id: handle to the dataset stored in the registry (data + argvals arrays).
    method: one of 'alignment', 'fpca', 'basis', 'smoothing', 'clustering'.
    result_id: if provided, use a stored result dict; otherwise uses dataset_id raw.
    with_argvals: pass argvals to build_diagnostics for distance metrics (default True).

    Returns: JSON-serialisable diagnostics dict (see advisor.build_diagnostics).
    """
```

The returned dict is also stored in the registry as a new `result_id` (for chaining).

### `fdars_run_method`

```python
@mcp.tool()
def fdars_run_method(
    dataset_id: str,
    method: str,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict:
    """Run an fdars method on a registered dataset and return a result_id.

    dataset_id: handle to data + argvals in the registry.
    method: one of 'alignment', 'fpca', 'basis', 'smoothing', 'clustering'.
    lambda_: warp penalty (alignment) or smoothing regularisation (smoothing).
    n_basis: number of basis functions (basis method).
    n_comp: number of FPCA components (fpca method).
    k: number of clusters (clustering method).
    seed: RNG seed (clustering method, for reproducibility).

    Returns: {'result_id': '<id>', 'method': '<method>'} — result stored in registry.
    """
```

**Design rationale for coarse-grained params:** Each parameter maps directly to one of the
advisor's ADVISE-02 parameters: `lambda_`, `n_basis`, `bandwidth`, `n_comp`, `cluster k`.
[VERIFIED: python/fdars/advisor.py:862-879] The tool exposes only the parameters that the
advisor's `parameter` task can recommend — not every fdars parameter.

### `fdars_compare_run` (TOOL-03)

```python
@mcp.tool()
def fdars_compare_run(
    dataset_id: str,
    method: str,
    before_result_id: str,
    params_after: dict,
) -> dict:
    """Re-run method with new parameters and return before/after diagnostics delta.

    dataset_id: handle to dataset in registry.
    before_result_id: result_id from a prior fdars_run_method or fdars_build_diagnostics call.
    params_after: dict of parameter overrides (same keys as fdars_run_method params).

    Returns: {
        'before_result_id': str,
        'after_result_id': str,
        'before': <diagnostics dict>,
        'after': <diagnostics dict>,
        'delta': {key: after_val - before_val for numeric keys where both are scalar}
    }

    The delta dict contains only keys where both before and after have a finite scalar value.
    The observable delta is the primary output for TOOL-03.
    """
```

**Why a third tool rather than a client loop:** TOOL-03 requires the compare loop to be
testable without a live model. `fdars_compare_run` can be called directly in pytest with
fixed `params_after` and the delta asserted. A "client loop" calling two separate tools
would require orchestration outside pytest.

---

## By-Reference Data Passing: Design Decision

**Chosen mechanism:** In-process `HandleRegistry` singleton in `mcp/_registry.py`.

**Rationale:**
- The stdio server runs in a single Python process. When `Client(mcp)` is used (in-process
  test pattern), client and server are in the same process — the registry is shared.
- No serialisation needed. Arrays never enter JSON.
- Fully testable: tests call `registry.store_dataset(data, argvals)` before calling the tool.
- Consistent with MCP protocol guidance on stateful tools [CITED: modelcontextprotocol.io/docs/concepts/tools §Stateful Tools]:
  "return an explicit handle from a creation tool and accept that handle as an argument on subsequent calls."

**Alternative considered — file paths under `docs/data/`:**
- Would require writing temporary files (unsuitable for a CI path).
- Breaks if datasets are not on disk (e.g., synthetic test data).
- Rejected.

**Lifetime / cleanup:**
- The registry accumulates handles across the server's lifetime (no eviction by default).
- Tests call `registry.clear()` in a pytest fixture to prevent state leakage between tests.
- For long-running sessions, the registry grows proportionally to datasets loaded.
  For this phase's scope (local/CI single-session use) this is acceptable.

**Pre-population for CI tests:**
Tests pre-load the Canadian Weather dataset from `docs/data/canadian_weather.csv` (a real
dataset already used in `test_advisor.py`) using `registry.store_dataset()` before each test.
This mirrors the pattern in `test_advisor.py::test_clustering_with_real_dataset`.

---

## Agentic Re-run/Compare Loop: Observable Delta

### Delta dict shape

```python
{
    "before_result_id": "r-abc123",
    "after_result_id": "r-def456",
    "before": {<full diagnostics dict from build_diagnostics>},
    "after":  {<full diagnostics dict from build_diagnostics>},
    "delta":  {
        # Only scalar float/int keys where both before and after are finite:
        "optimal_lambda": -0.42,      # after - before
        "optimal_gcv": -0.003,
        "optimal_edf": 1.2,
        # Bool keys preserved with both values:
        # "phase_leakage_flagged_before": True, "phase_leakage_flagged_after": False
    }
}
```

### Deterministic CI demo

`fdars_compare_run` is fully deterministic when `seed` is set (clustering) or when
`pspline_fit_gcv` / `basis_nbasis_cv` are used (they are deterministic for fixed inputs).
CI tests can assert:
- `result["delta"]["optimal_lambda"]` has correct sign given the parameter change
- `result["after"]["optimal_gcv"] < result["before"]["optimal_gcv"]` (improvement)
- `result["after_result_id"]` is stored in registry

**No ANTHROPIC_API_KEY required** for any TOOL-01/02/03 test path. The advisor's LLM call
(`advise`) is NOT invoked by any MCP tool in Phase 12; tools expose only `build_diagnostics`
(offline) and `fdars_run_method` (offline fdars compute). The model orchestrates by reading
the returned diagnostics dicts and deciding which parameters to try next.

---

## Python Version Compatibility Issue

**Critical constraint:** `mcp>=2.0.0` requires Python >=3.10.
[VERIFIED: pypi.org/pypi/mcp/2.0.0/json — `requires_python: ">=3.10"`]

`fdars` itself supports Python 3.9-3.14 (pyproject.toml `requires-python = ">=3.9"`).
[VERIFIED: /home/simonm/projects/rust/pyfda/pyproject.toml:9]

**Resolution:** The `[mcp]` extra is incompatible with Python 3.9. The pyproject.toml
`[project.optional-dependencies]` entry for `mcp` must document this constraint.
Options:
1. Add a comment in pyproject.toml noting that `[mcp]` requires Python >=3.10.
2. Do not add a `python_requires` marker to the extra itself (pip doesn't support that syntax).
3. The `mcp/server.py` module should guard at import time with a runtime check:
   ```python
   import sys
   if sys.version_info < (3, 10):
       raise ImportError(
           "fdars[mcp] requires Python 3.10+. "
           "The mcp package does not support Python 3.9."
       )
   ```

The project's CI tests on Python 3.9 must skip MCP tests (use `pytest.mark.skipif` on
`sys.version_info < (3, 10)`).

---

## Common Pitfalls

### Pitfall 1: Python 3.9 Incompatibility

**What goes wrong:** `from fdars.mcp import server` raises `ImportError` on Python 3.9 CI
runners because `mcp` requires >=3.10.

**Why it happens:** The mcp package uses `match` statements and `ExceptionGroup` (3.10+
features) internally.

**How to avoid:** Guard the import in `mcp/__init__.py` with the runtime version check
(shown above). Skip MCP tests on Python 3.9 with `pytest.mark.skipif(sys.version_info <
(3, 10), reason="mcp requires Python 3.10+")`.

**Warning signs:** `ImportError: mcp requires Python 3.10+` at import; alternatively, a
`SyntaxError` from the mcp package itself on 3.9.

### Pitfall 2: Blocking fdars Calls in Async Tool Handlers

**What goes wrong:** If `@mcp.tool()` registers an async function, the event loop blocks
while fdars computes (Rust does release the GIL via PyReadonly wrappers, but the Python
asyncio loop is single-threaded).

**Why it happens:** Mixing sync fdars calls inside `async def` tool handlers.

**How to avoid:** Use synchronous tool handlers (`def`, not `async def`). The MCP SDK
supports synchronous handlers [CITED: py.sdk.modelcontextprotocol.io]. fdars is designed for
synchronous Python callers.

**Warning signs:** Other async tasks starve during a long fdars computation.

### Pitfall 3: Handle Registry State Leakage Between Tests

**What goes wrong:** A test stores a dataset under ID `"ds-001"`, the next test retrieves
unexpected data from the same ID.

**Why it happens:** The registry is a module-level singleton; pytest reuses the module
across tests.

**How to avoid:** Add a `pytest fixture` (autouse or per-test) that calls `registry.clear()`
after each test. Use `uuid`-based IDs (not fixed strings) so collisions are impossible even
without clearing.

**Warning signs:** Tests pass in isolation but fail in sequence.

### Pitfall 4: Returning NumPy Scalars or Arrays from Tools

**What goes wrong:** The MCP SDK serialises tool return values to JSON. NumPy scalars and
arrays are not JSON-serialisable by default, causing `TypeError: Object of type float32 is
not JSON serializable`.

**Why it happens:** `fdars_run_method` calls fdars which returns numpy arrays. If the tool
returns a dict containing those arrays, serialisation fails.

**How to avoid:** Always call `build_diagnostics` (which converts all values to plain Python
types) before returning, or ensure the `_runner.py` helpers convert all numpy types. The
return value from `fdars_run_method` should be `{"result_id": str, "method": str}` only —
the actual arrays stay in the registry.

**Warning signs:** `TypeError: Object of type ndarray is not JSON serializable` in the MCP
SDK serialiser.

### Pitfall 5: Registering `mcp` in `fdars.__init__` Unconditionally

**What goes wrong:** Adding `from fdars import mcp` and `_sys.modules["fdars.mcp"] = mcp`
to `fdars/__init__.py` without an `[mcp]` guard causes an `ImportError` for all fdars users
without the extra.

**Why it happens:** The mcp package is not installed by default.

**How to avoid:** Use lazy import with try/except in `__init__.py`, or simply do not
register the `mcp` subpackage there — users import it explicitly as `from fdars.mcp import
server` or `from fdars.mcp.server import mcp`. Follow the precedent of `advisor.py`
(registered explicitly) rather than the native submodule loop.

**Warning signs:** `ModuleNotFoundError: No module named 'mcp'` when doing `import fdars`
without the extra installed.

### Pitfall 6: `params_after` as a Nested Dict in Tool Arguments

**What goes wrong:** Passing `params_after: dict` as a tool argument means the MCP schema
becomes `{"type": "object"}` with no property constraints — the model may pass arbitrary
keys that the runner does not handle.

**How to avoid:** Either flatten the params (expose each param as a top-level optional arg
on `fdars_compare_run`, matching `fdars_run_method`) or validate `params_after` keys against
a known allowlist in the tool handler. Flattened args are safer because the MCP schema is
fully specified from type hints.

---

## Packaging: `[mcp]` Extra

Add to `pyproject.toml` `[project.optional-dependencies]`:

```toml
mcp = ["mcp>=2.0.0"]
# Note: mcp requires Python >=3.10. This extra is not compatible with Python 3.9.
```

[VERIFIED: /home/simonm/projects/rust/pyfda/pyproject.toml:38-41] — current extras are
`plot`, `dev`, `advisor`. The `mcp` extra follows the same pattern.

The `[advisor]` extra (`anthropic>=0.72.0`, `pydantic>=2.0`) does NOT need to be pulled
into `[mcp]` — the MCP tools in Phase 12 call `build_diagnostics` (offline, no anthropic)
and `fdars_run_method` (no anthropic). Only if a future tool calls `advise()` would both
extras be needed together.

---

## Testing Without Network

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already in `dev` extra) |
| Async support | pytest-asyncio (new dep for MCP tests) |
| Config file | `pyproject.toml` or `pytest.ini` |
| Quick run command | `pytest tests/test_mcp_server.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-01 | `fdars_build_diagnostics` returns correct diagnostics dict for each of 5 methods | unit | `pytest tests/test_mcp_server.py::test_build_diagnostics_all_methods -x` | ❌ Wave 0 |
| TOOL-01 | `fdars_run_method` returns result_id and stores result for each of 5 methods | unit | `pytest tests/test_mcp_server.py::test_run_method_all_methods -x` | ❌ Wave 0 |
| TOOL-02 | `list_tools()` returns both tools; `call_tool()` succeeds in-process | integration | `pytest tests/test_mcp_server.py::test_list_and_call_tools -x` | ❌ Wave 0 |
| TOOL-03 | `fdars_compare_run` returns before/after/delta with observable numeric change | unit | `pytest tests/test_mcp_server.py::test_compare_run_smoothing -x` | ❌ Wave 0 |
| TOOL-03 | Delta dict has correct sign for a known parameter change | unit | `pytest tests/test_mcp_server.py::test_compare_run_delta_sign -x` | ❌ Wave 0 |

**No ANTHROPIC_API_KEY required** for any of the above tests. All tests use `build_diagnostics`
(offline) and fdars native methods (offline). The `advise()` LLM call is not invoked in Phase 12.

### Wave 0 Gaps

- [ ] `tests/test_mcp_server.py` — full test file covering TOOL-01/02/03
- [ ] `python/fdars/mcp/__init__.py`, `_registry.py`, `_runner.py`, `_compare.py`, `server.py` — all new files
- [ ] `pip install "fdars[mcp]"` or `pip install "mcp>=2.0.0"` in dev venv
- [ ] `pip install pytest-asyncio` in dev venv

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| FastMCP (previous high-level API in mcp 1.x) | `MCPServer` (new high-level API in mcp 2.0) | mcp 2.0.0 (2026-07-28) | `FastMCP` class no longer exists in v2.0; use `MCPServer` |
| SSE transport as default | stdio as default for `mcp.run()` | mcp 2.0 | `mcp.run()` defaults to stdio; no transport arg needed for stdio servers |
| `mcp.types` in 1.x | `mcp-types` separate package (2.0) | mcp 2.0 | `mcp-types==2.0.0` is a transitive dep; import paths unchanged for tool authors |

**Deprecated/outdated:**

- `FastMCP` class: appeared in mcp 1.x documentation and many online tutorials. In mcp 2.0,
  the class is `MCPServer` from `mcp.server`. Do not reference `FastMCP` in code. [CITED: github.com/modelcontextprotocol/python-sdk — v2 README shows `MCPServer`]

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python >=3.10 | `mcp` package | ✓ | 3.14.5 (system + venv) | Python 3.9 CI runners: skip MCP tests |
| `mcp` package | TOOL-01/02/03 | ✗ (not installed) | — (latest: 2.0.0) | Install via `pip install "mcp>=2.0.0"` |
| `pytest-asyncio` | async MCP tests | ✗ (not installed) | — | Install via `pip install pytest-asyncio` |
| `fdars` (compiled) | All tools | ✓ | 0.2.0 (installed in venv) | — |
| `advisor.py` | `fdars_build_diagnostics` | ✓ | Phase 11 complete | — |
| `docs/data/canadian_weather.csv` | test fixtures | ✓ | present | — |

**Missing dependencies with no fallback:** none that block execution for the test suite.

**Missing dependencies with fallback:**
- `mcp` package — install in venv as Wave 0 task; Python 3.9 CI runners skip MCP tests.

---

## Security Domain

Security enforcement is enabled (`security_enforcement: true`, ASVS level 1 in config.json).
[VERIFIED: /home/simonm/projects/rust/pyfda/.planning/config.json]

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | stdio server is local; no auth layer |
| V3 Session Management | no | stateless per call; handle registry is in-process |
| V4 Access Control | no | local process; no multi-user access |
| V5 Input Validation | yes | validate `method` against allowlist; validate `params_after` keys; `dataset_id`/`result_id` must exist in registry (KeyError on unknown) |
| V6 Cryptography | no | no secrets, no crypto |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unknown `dataset_id` passed to tool | Tampering | Registry raises `KeyError`; tool returns `isError: true` with descriptive message |
| Unknown `method` string | Tampering | Validate against `{"alignment","fpca","basis","smoothing","clustering"}` before calling fdars; return `ValueError` as tool execution error |
| Malformed `params_after` keys | Tampering | Allowlist check against known param names; reject unknown keys |
| Large-array injection via `params_after` | Tampering | `params_after` contains only scalar values (float, int); arrays are never accepted as params |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pytest-asyncio` is the standard way to run async pytest tests for the MCP `Client(mcp)` pattern | Testing | Could use `asyncio.run()` in each test instead; low risk |
| A2 | Synchronous tool handlers (not `async def`) work correctly with `MCPServer` | Architecture Patterns | If SDK only supports async handlers, all tool defs need `async def`; medium risk |
| A3 | `anyio`, `pydantic>=2.12.0`, and other transitive deps of `mcp` are compatible with the existing venv (no conflicts with `pydantic>=2.0` from `[advisor]`) | Standard Stack | `[advisor]` uses `pydantic>=2.0`; `mcp` requires `pydantic>=2.12.0`; overlap is safe if resolved to >=2.12 |
| A4 | `result.structured_content` on a `call_tool` result contains the returned dict | Testing | Alternative: `result.content[0].text` and JSON-parse; planner should verify against SDK source |
| A5 | `fdars_compare_run` flattening params (not nested dict) is feasible without MCP schema limitations | Tool Schema Design | Pitfall 6 discusses; low risk if we align param names with `fdars_run_method` |

---

## Open Questions

1. **`MCPServer` sync vs async tool handlers**
   - What we know: `MCPServer.run()` docstring says "synchronous function"; tool handlers
     in examples use `def` not `async def`
   - What's unclear: Whether the SDK also supports `async def` handlers (the client pattern
     uses `await client.call_tool(...)` suggesting async context)
   - Recommendation: Use `def` (synchronous) handlers; test with `async with Client(mcp)`
     — if this fails, switch to `async def` handlers

2. **`result.structured_content` vs `result.content[0].text`**
   - What we know: The README shows `result.structured_content` in the client example; the
     MCP spec defines `structuredContent` as the primary JSON field
   - What's unclear: Whether `MCPServer` with `def` handlers returning a `dict` populates
     `structured_content` automatically or only `content[0].text`
   - Recommendation: Assert both in tests; fall back to JSON-parsing `content[0].text` if
     `structured_content` is None

3. **Handle registry persistence across in-process client contexts**
   - What we know: Registry is module-level; `Client(mcp)` creates a new session per
     `async with` block
   - What's unclear: Whether `MCPServer` state (including registry references) persists
     across separate `Client(mcp)` context managers in the same test process
   - Recommendation: Design tests to store and retrieve within a single `async with Client`
     block; add a `yield` fixture that pre-populates the registry

---

## Sources

### Primary (MEDIUM confidence — official documentation, read this session)

- [CITED: modelcontextprotocol.io/docs/concepts/tools] — Tool schema, `inputSchema`, `outputSchema`, stateful tools / handle pattern, error handling
- [CITED: github.com/modelcontextprotocol/python-sdk README] — `MCPServer` class, `@mcp.tool()` decorator, `Client(mcp)` in-process pattern
- [CITED: github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/mcpserver/server.py] — `MCPServer.tool()` and `MCPServer.run()` method signatures
- [CITED: github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/stdio.py] — `stdio_server()` context manager signature
- [CITED: pypi.org/project/mcp/2.0.0] — Package metadata, requires-python >=3.10, version 2.0.0

### Secondary (MEDIUM confidence — verified via tool in this session)

- [VERIFIED: python/fdars/advisor.py] — All method names, diagnostics dict keys, `build_diagnostics` signature, `advise` signature, `describe_cluster_differences` signature
- [VERIFIED: pyproject.toml] — existing optional-dependencies structure (`plot`, `dev`, `advisor`)
- [VERIFIED: pip dry-run output] — mcp 2.0.0 transitive deps including pydantic>=2.12.0
- [VERIFIED: pypi.org/pypi/mcp/2.0.0/json via WebFetch] — requires_python >=3.10

### Tertiary (LOW confidence — training knowledge or inferred)

- [ASSUMED] — `pytest-asyncio` is the standard async test runner for mcp client tests
- [ASSUMED] — `anyio` transitive dep compatibility

---

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM — mcp 2.0.0 confirmed on PyPI; SDK patterns verified from official GitHub source; `MCPServer` API confirmed from source file; Python version constraint verified from PyPI metadata
- Architecture: MEDIUM — by-reference registry pattern is designed here (not from SDK); MCP stateful-tools pattern cites official spec
- Pitfalls: MEDIUM — Python 3.9 incompatibility verified; others inferred from SDK design and project conventions

**Research date:** 2026-08-09
**Valid until:** 2026-09-08 (30 days; mcp is in active development, check for v2.x releases)
