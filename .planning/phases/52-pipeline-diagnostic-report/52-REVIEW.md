---
phase: 52-pipeline-diagnostic-report
reviewed: 2026-08-30T00:00:00Z
depth: deep
files_reviewed: 8
files_reviewed_list:
  - python/fdars/advisor/_pipeline.py
  - python/fdars/advisor/__init__.py
  - python/fdars/advisor/_prompts.py
  - python/fdars/advisor/_schema.py
  - python/fdars/mcp/_pipeline.py
  - python/fdars/mcp/server.py
  - tests/test_pipeline_report.py
  - tests/test_pipeline_report_advise.py
findings:
  critical: 0
  warning: 6
  info: 1
  total: 7
status: resolved
---

# Phase 52: Code Review Report

**Reviewed:** 2026-08-30
**Depth:** deep
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Phase 52 introduces `build_pipeline_report()` (offline aggregation + LLM narrative),
`pipeline_report()`, `_compute_cross_stage_caveats()` (deterministic caveat rule table),
`PipelineReport` schema, the "pipeline" task family, and the `fdars_build_pipeline_report`
LLM-free MCP tool.

The hard invariants are upheld:

- **Aggregation is a list of per-stage labeled blocks** — `_normalize_stages` never
  flat-merges. Each block carries `{"stage": str, "aspect": str, "diagnostics": dict}`.
- **Union grounding via `{"_stages": [...]}` is correctly implemented** —
  `_build_stages_union` mirrors the Phase-51 `_candidates` wrapper exactly;
  `_flatten_diagnostics_numbers` recurses into the list without key-collision loss.
- **Caveats are Python-authoritative** — `_compute_cross_stage_caveats` runs before
  any LLM call; `report.caveats` is overwritten with the Python-computed list at line 713,
  regardless of what the LLM emits.
- **MCP tool is provably LLM-free** — no `advise` import, no provider call, all
  validation before any run, by-reference return with only handle strings crossing
  the boundary.
- **NumPy scalar leaks are absent** — all `value` fields in caveats use `float()` or
  `int()` conversions; `np.float64` is handled correctly.
- **No ZeroDivisionError for `n_obs=0`** — the guard `n_obs > 0` prevents the
  `n_outliers / n_obs` division.

Six warnings and one info item were found, documented below. No critical (security,
data-loss, or crash) issues.

---

## Warnings

### WR-01: Dead import `_check_grounding` in `pipeline_report()`

**File:** `python/fdars/advisor/_pipeline.py:666`

**Issue:** `_check_grounding` is imported inside `pipeline_report()` but never called.
`pipeline_report()` uses the dedicated adapter `_check_grounding_pipeline()` (line 707),
not the `_check_grounding` function from `_validate`. The import is dead code. Beyond
the wasted deferred import on the first call, it misleads readers into assuming the
standard `_check_grounding` path applies here, when in fact a custom adapter is used.

```python
# Line 666 — imported but never referenced after this point:
from fdars.advisor.providers._validate import _check_grounding  # noqa: PLC0415
# ...
# Line 707 — actual call:
_check_grounding_pipeline(report, union_diagnostics)
```

**Fix:** Remove the unused import at line 666:

```python
# Remove this line:
# from fdars.advisor.providers._validate import _check_grounding  # noqa: PLC0415
from fdars.advisor.providers._validate import (  # noqa: PLC0415
    GroundingViolationError,
    _extract_numbers,
    _flatten_diagnostics_numbers,
    _is_grounded_number,
)
# (these four are already imported inside _check_grounding_pipeline)
```

---

### WR-02: Dead code in `build_pipeline_report()` when `run_llm=True`

**File:** `python/fdars/advisor/_pipeline.py:484-487`

**Issue:** When `run_llm=True`, `build_pipeline_report()` calls `_normalize_stages()`
(line 484) and assembles `result = {"stages": blocks}` (line 487), then immediately
discards both by delegating to `pipeline_report()` which calls `_normalize_stages()`
again on the same original `stages` input (line 655). For entries containing raw result
dicts (no `"method"` key), `build_diagnostics()` is called **twice** — once in the
discarded path, once in `pipeline_report()`. The `blocks` variable and `result` dict
at lines 484–487 are unreachable dead code when `run_llm=True`.

```python
# --- 2. Normalise stages to labeled blocks (IN CALLER ORDER) ---  <- runs for both paths
blocks = _normalize_stages(stages, argvals=argvals, **kwargs)      # line 484

# --- 3. Assemble the offline result ---                            <- only meaningful for run_llm=False
result: dict = {"stages": blocks}                                  # line 487

# --- 4. Offline vs. LLM path ---
if not run_llm:
    return result                     # blocks/result used here

# --- 5. LLM narrative path ---
return pipeline_report(
    stages,           # <-- original stages, not blocks; pipeline_report re-normalizes
    ...
)
```

`build_diagnostics` is deterministic so correctness is preserved, but the double execution
is wasteful and the dead `blocks`/`result` objects are confusing.

**Fix:** Move `_normalize_stages` to execute only in the offline branch, or pass the
already-normalized `blocks` into `pipeline_report()` instead of re-normalizing from
`stages`:

```python
if not run_llm:
    blocks = _normalize_stages(stages, argvals=argvals, **kwargs)
    return {"stages": blocks}

# LLM path — normalize once inside pipeline_report
return pipeline_report(
    stages, argvals=argvals, domain_context=domain_context,
    model=model, provider=provider, **kwargs,
)
```

---

### WR-03: Dead parameter `argvals_from_dataset` in `build_pipeline_report_mcp()`

**File:** `python/fdars/mcp/_pipeline.py:55`

**Issue:** `argvals_from_dataset: bool = True` is declared in the function signature
and documented ("When `True` (default), pass the dataset's `argvals` array to
`build_diagnostics` for distance metrics"), but the parameter is **never read** in
the function body. `argvals` are unconditionally passed to `build_diagnostics` on
line 162 regardless of the flag's value:

```python
def build_pipeline_report_mcp(
    dataset_id: str,
    stages: list[dict],
    *,
    argvals_from_dataset: bool = True,   # declared here
) -> dict:
    ...
    data, argvals = registry.get_dataset(dataset_id)   # always resolves argvals
    ...
    diag = build_diagnostics(raw_result, aspect, argvals=argvals)   # always passes them
```

Calling `build_pipeline_report_mcp(..., argvals_from_dataset=False)` does nothing —
`argvals` is always forwarded. The docstring claim is false.

**Fix:** Either (a) remove the parameter and update the docstring to reflect that
argvals are always passed, or (b) implement the intended conditional logic:

```python
# Option (a) — remove unused parameter:
def build_pipeline_report_mcp(
    dataset_id: str,
    stages: list[dict],
) -> dict:
    ...
    diag = build_diagnostics(raw_result, aspect, argvals=argvals)

# Option (b) — implement the logic:
    diag = build_diagnostics(
        raw_result, aspect,
        argvals=(argvals if argvals_from_dataset else None),
    )
```

---

### WR-04: Tautological `elif` in Rule-2 fallback chain

**File:** `python/fdars/advisor/_pipeline.py:328`

**Issue:** Inside the `elif n_out is not None and n_obs is None:` branch (line 320),
the nested `elif n_out is not None:` condition at line 328 is **always True** — the
outer `elif` guarantees `n_out is not None` is already satisfied. The inner condition
therefore acts as a plain `else` but hides that fact. A reader must trace back to the
outer condition to understand why `elif n_out is not None` will never evaluate to False,
making the logic harder to follow than necessary.

```python
elif n_out is not None and n_obs is None:      # line 320: guarantees n_out is not None
    n_union = diag.get("n_union_outliers")
    if n_union is not None:
        fraction_value = float(n_union) / 100.0
        raw_value = int(n_union)
    elif n_out is not None:                     # line 328: ALWAYS True here (tautology)
        fraction_value = float(n_out) / 100.0
        raw_value = int(n_out)
```

**Fix:** Replace with `else` to express the intent clearly:

```python
elif n_out is not None and n_obs is None:
    n_union = diag.get("n_union_outliers")
    if n_union is not None:
        fraction_value = float(n_union) / 100.0
        raw_value = int(n_union)
    else:                                       # n_union absent; use n_out count
        fraction_value = float(n_out) / 100.0
        raw_value = int(n_out)
```

---

### WR-05: Silent miss in Rule-2 when `n_obs=0` and `n_union_outliers` is also absent

**File:** `python/fdars/advisor/_pipeline.py:317`

**Issue:** The Rule-2 outlier fallback chain has a gap for the degenerate case
`n_obs=0, n_outliers>0, outlier_fraction=None, n_union_outliers=None`. In this
configuration:

1. Branch 1 (`n_obs > 0`): False — skip.
2. Branch 2 (`n_obs is None`): False — `n_obs` is `0`, not `None` — skip.
3. Final `n_union` fallback: `n_union_outliers` is absent — skip.

Result: `fraction_value` remains `None` and **no caveat fires** even though the stage
flagged a positive number of outliers. This is a silent miss that cannot be distinguished
from a stage with zero outliers.

```python
n_out = diag.get("n_outliers")
n_obs = diag.get("n_obs")
if n_out is not None and n_obs is not None and n_obs > 0:    # n_obs=0 fails here
    fraction_value = float(n_out) / float(n_obs)
    raw_value = fraction_value
elif n_out is not None and n_obs is None:                    # n_obs=0 fails here (not None)
    ...
# n_obs=0, n_out>0 falls through all branches -> fraction_value stays None -> no caveat
```

While `n_obs=0` in a real dataset is degenerate (fdars would typically raise before
reaching this point), the caveat function should not silently pass a broken input — it
should treat `n_obs=0` with `n_out>0` as 100% outlier fraction and fire Rule-2.

**Fix:** Add an explicit guard for the `n_obs=0` case:

```python
if n_out is not None and n_obs is not None and n_obs > 0:
    fraction_value = float(n_out) / float(n_obs)
    raw_value = fraction_value
elif n_out is not None and n_obs is not None and n_obs == 0 and int(n_out) > 0:
    # Degenerate: n_obs=0 with outliers flagged — treat as 100% outlier fraction.
    fraction_value = 1.0
    raw_value = int(n_out)
elif n_out is not None and n_obs is None:
    ...
```

---

### WR-06: Missing result key in stage entry raises `TypeError` instead of `ValueError`

**File:** `python/fdars/advisor/_pipeline.py:163-174`

**Issue:** `_resolve_result()` returns `None` when a stage entry has no recognised key
(`"diagnostics"`, `"result"`, or `"value"`). This `None` is passed directly to
`build_diagnostics(None, aspect, ...)`. Inside `build_diagnostics`:

```python
raw = getattr(None, "raw", None)  # -> None
# Not dict, no __array__, no .data -> falls through to:
raw = dict(None)  # -> TypeError: 'NoneType' object is not iterable
```

A user who passes `{"stage_name": "foo", "aspect": "fpca"}` (missing the result key)
receives an opaque `TypeError` with no indication of which stage caused it or what the
expected keys are.

**Fix:** Validate in `_normalize_stages` that the resolved value is not `None` before
calling `build_diagnostics`:

```python
value = _resolve_result(entry, stage_name)
if value is None:
    raise ValueError(
        f"build_pipeline_report: stage entry at index {i} (stage_name={stage_name!r}) "
        "has no result value. Provide one of the keys: 'diagnostics', 'result', or 'value'."
    )
```

---

## Info

### IN-01: `assert` used for runtime invariant enforcement in production code

**File:** `python/fdars/advisor/_pipeline.py:340`

**Issue:** `assert raw_value is not None` is used to enforce a structural invariant
in production code. Python's `-O` (optimized) flag silently strips all `assert`
statements, so this guard would disappear in optimized deployments. Static analysis
of the code confirms the invariant is maintained by the preceding logic (every code path
that sets `fraction_value` also sets `raw_value`), so this is not a crash risk in
practice. However, using `assert` for production invariants is a project convention
violation and a maintainability concern.

**Fix:** Replace with an explicit conditional (or document that this is an unreachable
guard):

```python
# Replace:
assert raw_value is not None  # guaranteed by the logic above

# With:
if raw_value is None:  # pragma: no cover — structural invariant; unreachable by construction
    raise AssertionError(
        "_compute_cross_stage_caveats: raw_value is None despite fraction_value being set. "
        "This is a logic bug in the fallback chain."
    )
```

---

_Reviewed: 2026-08-30_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
