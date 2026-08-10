---
phase: 12-tool-mcp-surface
reviewed: 2026-08-09T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - python/fdars/mcp/__init__.py
  - python/fdars/mcp/_registry.py
  - python/fdars/mcp/_runner.py
  - python/fdars/mcp/_compare.py
  - python/fdars/mcp/server.py
  - python/fdars/advisor.py
  - examples/mcp_recipe.py
  - tests/test_mcp_server.py
  - pyproject.toml
findings:
  critical: 4
  warning: 5
  info: 3
  total: 12
status: issues_found
---

# Phase 12: Code Review Report

**Reviewed:** 2026-08-09
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Reviewed the new `fdars.mcp` subpackage (handle registry, method runner, compare helper, MCP
server surface) together with `advisor.py` (updated for Branch A-prime) and supporting test and
example files.  The by-reference handle design is sound, the method allowlist is correctly placed
before any fdars call in all three tool handlers, and scalar-only param validation in
`compare_run` is implemented correctly.  However, four blockers were found: a wrong MCP SDK import
path that will crash the server on startup, a missing `data=data` kwarg forwarded to
`build_diagnostics` from `fdars_build_diagnostics` (silently produces degraded diagnostics for
smoothing/basis), a collision risk in 8-hex-char handle IDs under concurrent load, and an
Anthropic SDK `thinking` API usage that does not match the current SDK contract.  Five warnings
and three info items are also noted below.

---

## Critical Issues

### CR-01: Wrong MCP SDK import path — server crashes on startup

**File:** `python/fdars/mcp/server.py:35`
**Issue:** The import `from mcp.server import MCPServer` is almost certainly wrong for `mcp>=2.0.0`.
In the MCP Python SDK 2.x the high-level decorator-based server class is exposed as
`mcp.server.fastmcp.FastMCP` (often re-exported as `from mcp import FastMCP`), not as
`mcp.server.MCPServer`.  The `MCPServer` name does not exist in the public API of any released
`mcp` package version; running `from mcp.server import MCPServer` raises `ImportError` immediately
and the entire `fdars.mcp` subpackage becomes unimportable, silently rendering all three tools
non-functional.  The `# type: ignore[import-untyped]` suppresses the static warning that would
otherwise catch this.  The tests cannot verify this because `mcp` is not installed in CI (confirmed
by environment check during review).

**Fix:** Confirm the correct class name against the installed SDK (`python -c "import mcp; print(dir(mcp))"`).
For `mcp>=2.0.0` with the FastMCP pattern use:
```python
from mcp import FastMCP
mcp = FastMCP("fdars-advisor")
```
and replace every `@mcp.tool()` decorator accordingly.  If the SDK exposes a different entry point,
use that.  Remove `# type: ignore[import-untyped]` once the correct name is confirmed; do not
silence import errors on this boundary.

---

### CR-02: `fdars_build_diagnostics` drops `data=` kwarg — Branch B silently produces empty diagnostics

**File:** `python/fdars/mcp/server.py:121–131`
**Issue:** The `fdars_build_diagnostics` tool handler builds `kwargs` containing only `argvals`
(line 124) and then calls `build_diagnostics(result, method_lc, **kwargs)` (line 126).  For
`method="smoothing"` or `method="basis"`, when `result_id` is `None` the handler sets
`result = {"data": data}` (line 119), which stores the raw data matrix inside the result dict
rather than forwarding it via the `data=` kwarg that Branch B in `_build_smoothing_diagnostics`
and `_build_basis_diagnostics` actually reads from `kwargs.get("data")` (advisor.py lines 496,
606).

This means:
1. When `result_id=None` and `method="smoothing"`, `build_diagnostics` enters Branch A-prime
   because the result dict `{"data": data}` contains neither `"gcv"` nor `"edf"`, so it falls
   through to Branch B, which checks `kwargs.get("data")` — but `data` is **not in kwargs** —
   and then falls through to the all-`None` fallback.  The caller receives an empty diagnostics
   dict with every key `None`.
2. Even when `result_id` points to a stored smoothing result (Branch A-prime path via a prior
   `fdars_run_method`), any code that wants to trigger a fresh Branch B re-run via
   `fdars_build_diagnostics` (the documented "chaining" use case) will silently get the all-None
   fallback.

The `_compare.compare_run` correctly passes `data=data` (line 163–164), so the compare tool is
unaffected.  Only `fdars_build_diagnostics` is broken for these cases.

**Fix:**
```python
kwargs: dict = {}
if with_argvals:
    kwargs["argvals"] = argvals
    kwargs["data"] = data     # required for Branch B (smoothing/basis re-run)

diagnostics = build_diagnostics(result, method_lc, **kwargs)
```

---

### CR-03: 8-hex-char handle IDs have meaningful collision probability under concurrent use

**File:** `python/fdars/mcp/_registry.py:66,110`
**Issue:** Handle IDs are generated as `uuid4().hex[:8]` — only 32 bits of entropy.  The
birthday-paradox collision probability exceeds 1 % after ~9 300 stored handles and 50 % after
~77 000 handles.  In an in-process server shared across multiple concurrent tool calls (the
documented deployment pattern), two nearly-simultaneous calls to `store_dataset` or
`store_result` can produce the same ID, causing the second write to silently overwrite the first.
The caller receives a valid-looking handle that now points to different data.  For a data-analysis
server where handle aliasing means computing diagnostics on the wrong dataset, this is a data
correctness bug, not merely a theoretical concern.

Note: `uuid4()` produces 128-bit random IDs; truncating to 8 hex chars (32 bits) throws away
96 bits of collision resistance with no benefit because the full hex is not user-visible.

**Fix:** Use the full UUID to eliminate collision risk:
```python
# In store_dataset:
ds_id = f"ds-{uuid.uuid4().hex}"   # 32-char hex, 128-bit collision resistance

# In store_result:
r_id = f"r-{uuid.uuid4().hex}"
```

---

### CR-04: `thinking={"type": "adaptive"}` is not a valid Anthropic SDK parameter

**File:** `python/fdars/advisor.py:991–997`
**Issue:** The `advise` function passes `thinking={"type": "adaptive"}` to
`client.messages.parse`.  The Anthropic Python SDK does not accept a `thinking` top-level
parameter to `messages.parse` (or `messages.create`).  Extended thinking is enabled via the
`betas=["interleaved-thinking-2025-05-14"]` header and a `thinking` content block param, but
the exact API surface differs from what is coded here.  Additionally, `{"type": "adaptive"}` is
not a documented value for the extended-thinking block (`{"type": "thinking", "budget_tokens":
N}` is the form used in current Anthropic docs).  This call will raise a `TypeError` or an
`anthropic.BadRequestError` at runtime for every call to `advise()`, making the entire LLM
interpretation path non-functional.

**Fix:** Check current SDK docs for the correct extended-thinking invocation, or remove the
thinking parameter entirely if the intent is just structured output:
```python
# Option A — structured output only, no extended thinking:
response = client.messages.parse(
    model=model,
    max_tokens=16000,
    system=system,
    output_format=Advice,
    messages=[{"role": "user", "content": user_content}],
)

# Option B — structured output + extended thinking (verify SDK version first):
response = client.messages.parse(
    model=model,
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 8000},
    system=system,
    output_format=Advice,
    messages=[{"role": "user", "content": user_content}],
    betas=["interleaved-thinking-2025-05-14"],
)
```

---

## Warnings

### WR-01: `fdars_run_method` does not validate method before delegating to runner — no fast-fail at tool boundary

**File:** `python/fdars/mcp/server.py:213–231`
**Issue:** `fdars_run_method` delegates to `run_method` without a pre-check of `method` at the
tool boundary (unlike `fdars_build_diagnostics` and `fdars_compare_run`, both of which validate
`method_lc` against `_SUPPORTED_METHODS` before any work).  The validation happens inside
`run_method`, but the error message will then read "run_method: unsupported method" rather than
"fdars_run_method: unsupported method", which is misleading when the error surfaces to the MCP
client.  This is an inconsistency in error reporting rather than a security gap (the allowlist
is still checked), but it degrades debuggability.
**Fix:** Add the same guard pattern used in `fdars_build_diagnostics` (lines 100–105) at the top
of `fdars_run_method`, before calling `run_method`.

---

### WR-02: `fdars_build_diagnostics` stores diagnostics in registry without returning the handle

**File:** `python/fdars/mcp/server.py:129`
**Issue:** Line 129 calls `registry.store_result(diagnostics)` but discards the returned
`r_id`.  The docstring says "Also stored in the registry as a new result handle (not returned,
but available via the registry)" — but since the handle is silently dropped, there is no way for
the caller to retrieve it.  This means the registry accumulates unreachable entries on every
`fdars_build_diagnostics` call (one per call), with no way to reference or clear them short of
`registry.clear()`.  The stated purpose ("available for potential chaining") is not fulfilled
without returning the handle.  This is a correctness gap versus the documented intent.
**Fix:** Either return the stored handle in the response dict, or do not store diagnostics results
(let callers call `fdars_run_method` first and use the chain explicitly).

---

### WR-03: Anthropic version check crashes on non-PEP-440 pre-release version strings

**File:** `python/fdars/advisor.py:767–773`
**Issue:** The version comparison does `int(x) for x in anthropic.__version__.split(".")[:3]`.
This crashes with `ValueError: invalid literal for int() with base 10` for any pre-release
version string such as `"0.72.0rc1"` or `"0.73.0.dev20250101"`, because `"0rc1"` cannot be
parsed as an integer.  Pre-release SDK builds are common in CI environments.
**Fix:** Use `packaging.version.Version` for comparison, or strip non-numeric suffixes:
```python
import re
def _parse_version(s: str) -> tuple:
    return tuple(int(x) for x in re.split(r"[^0-9]+", s) if x.isdigit())[:3]
```

---

### WR-04: `fdars_compare_run` re-uses `method_lc` (lowercased) but `compare_run` will lowercase again — double-lowercase is harmless but delegation contract is fragile

**File:** `python/fdars/mcp/server.py:351`
**Issue:** `fdars_compare_run` validates `method_lc = method.lower()` (line 330) and then passes
`method_lc` (already lowercased) to `compare_run` (line 351).  Inside `compare_run`, the first
thing `run_method` does is `method.lower()` again (runner line 142).  More importantly,
`compare_run` passes the already-lowercased string to `build_diagnostics`, which also calls
`method.lower()`.  This is harmless but indicates the casing contract is not specified: the
server tool pre-lowercases, the runner re-lowercases, the advisor re-lowercases.  If someone
calls `compare_run` directly (not via the tool), they get the same result; but the duplication
hides the actual API contract (does `compare_run` accept mixed case or not?).  The docstring for
`compare_run` says "Case-insensitive", but its internal call to `run_method` expects the raw
`method` string — not the pre-lowercased one — since `run_method` documents it as
"Case-insensitive" too.  Passing `method_lc` to `compare_run` instead of the original `method`
silently changes `compare_run`'s observable input, which is a subtle contract violation (the
before/after stored method name in the registry will always be lowercase even if the caller
passed mixed case).
**Fix:** Pass the original `method` (not `method_lc`) to `compare_run`, as the runner is
documented to handle casing internally.  Remove the pre-lowercasing in the tool handler and let
each internal layer own its own normalization.

---

### WR-05: `_build_basis_diagnostics` Branch B calls itself recursively without a depth guard

**File:** `python/fdars/advisor.py:504–505`
**Issue:** Branch B in `_build_basis_diagnostics` calls `_build_basis_diagnostics(cv_result)`
recursively.  If `fdars.basis.basis_nbasis_cv` returns a result dict that also lacks
`n_basis_values` and `gcv` (e.g., because of an unexpected fdars API change or a future return
format change), this triggers infinite recursion until Python raises `RecursionError`.  The same
pattern exists in `_build_smoothing_diagnostics` (line 614).
**Fix:** Add a `_recurse` guard parameter or restructure to avoid recursion:
```python
# Branch B inside _build_basis_diagnostics:
cv_result = _basis.basis_nbasis_cv(data_arr, av_arr)
# Call the sub-logic directly, not recursively, to avoid unbounded recursion
# if fdars ever returns an unexpected structure:
if "n_basis_values" not in cv_result or "gcv" not in cv_result:
    # fallback — unexpected structure from fdars
    diag.update({k: None for k in [...expected keys...]})
    return diag
return _build_basis_diagnostics(cv_result)
```

---

## Info

### IN-01: `pyproject.toml` missing `[project.scripts]` entry for `fdars-mcp-server`

**File:** `pyproject.toml`
**Issue:** `server.py` defines `run_stdio()` and documents it as "the console-script entry point
for the `fdars-mcp-server` command" (line 362).  However, `pyproject.toml` contains no
`[project.scripts]` table, so `pip install fdars[mcp]` does not install the `fdars-mcp-server`
executable.  The docstring reference is misleading until the entry point is wired up.
**Fix:** Add to `pyproject.toml`:
```toml
[project.scripts]
fdars-mcp-server = "fdars.mcp.server:run_stdio"
```

---

### IN-02: Registry `clear()` clears all state globally — no per-test scoping possible

**File:** `python/fdars/mcp/_registry.py:140–147`, `tests/test_mcp_server.py:44–49`
**Issue:** The module-level singleton `registry` is a plain Python object; `clear()` wipes both
`_datasets` and `_results`.  The autouse `_clear_registry` fixture in the test suite calls
`registry.clear()` in teardown (after `yield`), meaning any dataset registered in a fixture that
runs before the first test body is already present when the next test's setup runs.  More
specifically, the `dataset_id` fixture registers a dataset in setup (before yield), but if a
prior test raised an exception the autouse fixture still clears on teardown, so state from a
failed test does not bleed.  This is correct.  However, the `clear()` call happens *after*
`yield` in the autouse fixture, meaning the registry is never clean at the *start* of a test
(only after the previous test ends).  Tests that run first in a session start with an empty
registry only by accident.  If test ordering changes or if `_clear_registry` is overridden,
fixture-order-sensitive leaks can appear.
**Fix:** Add a pre-yield clear in addition to the post-yield clear:
```python
@pytest.fixture(autouse=True)
def _clear_registry():
    from fdars.mcp._registry import registry
    registry.clear()   # ensure clean state at test start
    yield
    registry.clear()   # cleanup after test
```

---

### IN-03: `examples/mcp_recipe.py` accesses `ds.argvals` but the `datasets` API likely returns `ds.data.argvals`

**File:** `examples/mcp_recipe.py:62`
**Issue:** Line 62 reads `day = np.asarray(ds.argvals, dtype=float)`.  The `datasets.load_canadian_weather()`
function returns a `CanadianWeather` (or similar) named tuple / dataclass.  Based on the Fdata
class design described in `CLAUDE.md` (where `.argvals` is a property of `Fdata`, not of the
dataset container), `ds.argvals` may raise `AttributeError` at runtime if the top-level dataset
object does not expose `argvals` directly (it may require `ds.data.argvals`).  The test fixture
(test file line 63) does `np.asarray(ds.argvals, dtype=float)` identically, so if this is wrong
it breaks both the example and the tests.  Without the compiled extension available in this review
environment the call cannot be verified, but it should be validated against the actual
`datasets.load_canadian_weather()` return type.
**Fix:** Verify via `python -c "from fdars import datasets; ds = datasets.load_canadian_weather(); print(dir(ds))"` and update accordingly.

---

_Reviewed: 2026-08-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
