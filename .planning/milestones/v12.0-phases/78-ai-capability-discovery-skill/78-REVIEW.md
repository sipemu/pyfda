---
phase: 78-ai-capability-discovery-skill
reviewed: 2026-09-06T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - scripts/generate_capability_dataset.py
  - python/fdars/mcp/server.py
  - tests/test_capability_accuracy.py
  - tests/test_guard_sync_version_independent.py
  - tests/test_mcp_import_smoke.py
  - python/fdars/_capability_map.json
  - python/fdars/_capability_curation.json
  - .claude/skills/fdars-capabilities/SKILL.md
  - docs/llms.txt
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: resolved
resolution: |
  0 Critical. All 5 findings fixed 2026-09-06:
  - WR-01: added test_capability_curation_keys_resolve (Py3.9-safe) which caught 8 real
    stale curation keys authored in 78-01; corrected them to live method names
    (kmeans_functional→kmeans_fd, norm_1d→norm_lp_1d, ftsm_fit→ftsm, pred_mae→functional_mae,
    kl_simulation→sim_kl, bootstrap_confidence_band→inference.mean_scb,
    cov_surface_1d→fdata.functional_covariance) and dropped clustering.cluster_optim
    (no live target). Their `when` guidance now actually applies to the map.
  - WR-02: fdars_list_capabilities now reads fdars.__version__ dynamically (no hardcoded 0.4.0).
  - WR-03: MCP import-smoke now covers all 7 tools (added compare_methods, build_pipeline_report, auto_tune).
  - IN-01: removed unused sys/Path imports from test_capability_accuracy.py.
  - IN-02: corrected the generator docstring (stale curation is caught by the new test, not the drift test).
  Map + llms.txt regenerated (byte-stable, run-to-run deterministic); full guard/capability/import-smoke suite green (9 passed); advisor+MCP regression suite unaffected (67 passed pre-fix).
---

# Phase 78: Code Review Report

**Reviewed:** 2026-09-06
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Phase 78 ships a generator-driven capability-discovery skill covering 30 fdars submodules
and 437 callables. The three primary files under review — generator, MCP tool, and guard-sync
test — are structurally sound. The generator correctly uses `__all__` (not `dir()`), never
calls/executes any introspected method (only reads attributes and inspects signatures), and
the JSON output is deterministic (`sort_keys=True` plus fully sorted iteration). The MCP tool
is provably LLM-free (static JSON load via `importlib.resources`, frozenset allowlist before
load, no network I/O). The guard-sync test correctly blocks `mcp` from module-level import on
Python 3.9 and implements the three-way literal mirror.

Three warnings are raised: (1) stale curation keys silently vanish with no test coverage,
contradicting the code comment that claims they surface as failures; (2) the hardcoded
`"version": "0.4.0"` string in `fdars_list_capabilities` will drift on the next package
release without any test catching it; (3) the smoke test's tool-coverage gap (three tools
added in Phases 51-53 never added to the import smoke). Two info items cover unused imports
and a minor documentation inaccuracy.

---

## Warnings

### WR-01: Stale curation keys silently dropped — contradicts code comment claiming detection

**File:** `scripts/generate_capability_dataset.py:223-228`

**Issue:** The curation merge loop at lines 223-228:

```python
for key, when_text in curation.items():
    if "." not in key:
        continue
    mod_name, fn_name = key.split(".", 1)
    if mod_name in dataset and fn_name in dataset[mod_name]:
        dataset[mod_name][fn_name]["when"] = when_text
```

silently drops any curation key whose callable was renamed or removed. If a developer
adds `"fdata.old_name": "..."` to `_capability_curation.json` and `old_name` is later
removed from fdars, the curation entry is skipped without any warning or test failure.
The docstring for `generate_capability_dataset()` at line 175 explicitly states:
*"a renamed or removed method still fails the accuracy test"* — this is **false for
curation keys**. The SKILL-02 accuracy test (`test_capability_map_no_drift`) compares
only the introspected `purpose` and `sig` fields and strips `when` fields on both sides
(see `test_capability_accuracy.py:_strip_when`). A stale curation key neither causes the
regenerated JSON to differ from the committed copy nor triggers the importability test.

The curation file currently has 30 entries; as the fdars API evolves, stale `when`
entries will accumulate invisibly and the skill's "when to use" guidance will silently
cover methods that no longer exist.

**Fix:** Add a validation step in the generator (or as a separate test) that logs a
warning or raises for any curation key that does not resolve in the dataset:

```python
# In generate_capability_dataset(), after the curation merge loop:
stale = [
    key for key, _ in curation.items()
    if "." in key and (
        key.split(".", 1)[0] not in dataset
        or key.split(".", 1)[1] not in dataset.get(key.split(".", 1)[0], {})
    )
]
if stale:
    print(
        f"WARNING: {len(stale)} stale curation key(s) — "
        "method renamed or removed:\n" + "\n".join(f"  {k}" for k in stale),
        file=sys.stderr,
    )
```

Alternatively, add a `test_curation_keys_all_resolve()` test in
`test_capability_accuracy.py` that loads both the committed map and the curation file
and asserts every curation key has a matching entry.

---

### WR-02: `"version": "0.4.0"` hardcoded in `fdars_list_capabilities` — no test guards drift

**File:** `python/fdars/mcp/server.py:821`

**Issue:** The `fdars_list_capabilities` return dict contains:

```python
"version": "0.4.0",  # fdars.__version__ at generate time
```

This string is a literal that will not update when the fdars package is released at a
new version. MCP clients that read `"version"` to understand which capability surface
they are looking at will see a stale version identifier. The comment *"fdars.__version__
at generate time"* documents intent, but no test enforces that this literal equals
`fdars.__version__`. The GATE-04 guard tests check module set and LLM-free boundary but
do not assert the version field.

Combined with the fact that `python/fdars/__init__.py` defines `__version__ = "0.4.0"`
while `pyproject.toml` already has `version = "0.10.0"`, the version string is already
inconsistent with the package distribution metadata.

**Fix:** Read the version dynamically at call time instead of hardcoding it:

```python
import fdars as _fdars_pkg  # already imported at module top

return {
    "modules": modules,
    "version": _fdars_pkg.__version__,
    "module_count": len(modules),
    "callable_count": sum(len(v) for v in modules.values()),
}
```

Or at minimum add a guard-sync assertion in the companion test (Python 3.10+) that
verifies the returned `"version"` matches `fdars.__version__`.

---

### WR-03: `test_mcp_import_smoke.py` tool-coverage gap — three Phase 51-53 tools absent

**File:** `tests/test_mcp_import_smoke.py:77-87`

**Issue:** The `expected_tool_names` set checked in `test_mcp_v2_server_import_and_tools_load`
covers only four tools:

```python
expected_tool_names = {
    "fdars_build_diagnostics",
    "fdars_run_method",
    "fdars_compare_run",
    "fdars_list_capabilities",
}
```

Three tools registered in `server.py` during Phases 51-53 are absent from the smoke
test: `fdars_compare_methods`, `fdars_build_pipeline_report`, and `fdars_auto_tune`.
While these were present before Phase 78 and this is technically a pre-existing gap, the
Phase 78 work explicitly extended this test to add `fdars_list_capabilities` and the
comment at line 13 lists "Plan 78-04" alongside plans 12 and 22, implying the test was
reviewed and deliberately updated. The gap means an import-time regression in any of the
three absent tools would not be caught by this smoke test.

**Fix:** Extend `expected_tool_names` and the import block to include all seven tools:

```python
from fdars.mcp.server import (  # noqa: PLC0415
    fdars_build_diagnostics,
    fdars_compare_run,
    fdars_compare_methods,
    fdars_build_pipeline_report,
    fdars_auto_tune,
    fdars_list_capabilities,
    fdars_run_method,
)

expected_tool_names = {
    "fdars_build_diagnostics",
    "fdars_run_method",
    "fdars_compare_run",
    "fdars_compare_methods",
    "fdars_build_pipeline_report",
    "fdars_auto_tune",
    "fdars_list_capabilities",
}
```

---

## Info

### IN-01: Unused imports `sys` and `Path` in `test_capability_accuracy.py`

**File:** `tests/test_capability_accuracy.py:31,33`

**Issue:** `import sys` (line 31) and `from pathlib import Path` (line 33) are imported
at module level but never referenced in any function body or expression in the file. The
module docstring at line 19 even explicitly lists the imports this file uses and correctly
omits `Path`, but fails to catch that `sys` is also unused. The module docstring
states *"This module imports ONLY stdlib (`json`, `sys`, `inspect`, `importlib.resources`) plus
`pytest` and `fdars`"* which at least documents `sys` as intentional, but no code path
uses it.

**Fix:** Remove the two unused imports:

```python
# Remove these two lines:
# import sys          # line 31 — never referenced
# from pathlib import Path  # line 33 — never referenced
```

---

### IN-02: Generator docstring incorrectly claims curation-renamed-method detection

**File:** `scripts/generate_capability_dataset.py:175-176`

**Issue:** The `generate_capability_dataset()` docstring states:

> *"Introspected `purpose` and `sig` are always sourced from live code (never overwritten
> by curation) so a renamed or removed method still fails the accuracy test."*

This is only partially true. A renamed or removed method causes the SKILL-02
*importability* test (`test_capability_map_all_importable`) to fail if the map was not
regenerated, and causes the *no-drift* test to fail if the map was regenerated. However,
a stale **curation** key for a renamed or removed method does not fail any test (see
WR-01). The docstring overstates the protection provided.

**Fix:** Qualify the claim to scope it accurately:

```
Introspected ``purpose`` and ``sig`` are always sourced from live code
(never overwritten by curation), so a renamed or removed callable fails the
accuracy test when the map is regenerated.  Stale curation keys (``when``
entries whose callable no longer exists) are currently silently dropped —
see the maintenance note in the module docstring.
```

---

_Reviewed: 2026-09-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
