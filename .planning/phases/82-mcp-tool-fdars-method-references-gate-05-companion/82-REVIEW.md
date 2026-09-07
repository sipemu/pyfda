---
phase: 82-mcp-tool-fdars-method-references-gate-05-companion
reviewed: 2026-09-07T21:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - python/fdars/mcp/server.py
  - tests/test_guard_sync_version_independent.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
iteration: 2
prior_status: issues_found
prior_findings:
  critical: 0
  warning: 2
  info: 1
---

# Phase 82: Code Review Report (Re-review, Iteration 2)

**Reviewed:** 2026-09-07
**Depth:** standard
**Files Reviewed:** 2
**Status:** clean

## Test Run

```
.venv/bin/python -m pytest tests/test_guard_sync_version_independent.py -q
............
12 passed in 1.33s
```

## Summary

Re-review performed after commit b958fcd applied fixes for WR-01 and WR-02. IN-01 (info severity) was acknowledged out-of-scope and not fixed; it remains on record per 82-REVIEW-FIX.md.

All prior warnings are closed. No new issues were introduced by the fix. The files are clean at standard depth.

### WR-01 verification (AST blind spot — `from fdars import advisor`)

The fix adds `forbidden_fdars_names = {"advisor"}` and a nested `if node.module == "fdars"` branch inside the `ast.ImportFrom` walk (`tests/test_guard_sync_version_independent.py:784-800`).

Verified by simulation:

- `from fdars import advisor` is now caught (alias.name `"advisor"` is in `forbidden_fdars_names`).
- `from fdars import __version__` still passes (`"__version__"` is not in `forbidden_fdars_names`).
- `from fdars.advisor import X` is still caught via the module-level check against `forbidden_modules`.
- `import fdars.advisor` is still caught via the `ast.Import` branch.
- The actual handler (`server.py`) uses only `from fdars import __version__ as _fdars_version` (lines 819 and 920) — both are `__version__`, not `advisor` — so the handler correctly passes the guard.
- The fix is not vacuous: `from fdars import advisor` was a genuine gap before b958fcd and is now caught.

One residual non-actionable gap for the record: a bare `import advisor` (no module prefix) is not caught by the `ast.Import` branch because `"advisor"` is not in `forbidden_modules` (which uses full dotted names). This is not a real attack vector — `import advisor` raises `ModuleNotFoundError` in the test environment because there is no top-level `advisor` package — so this gap does not require action.

### WR-02 verification (Guard Group 3 docstring)

The module docstring now includes a full Guard Group 3 block (lines 33–52) describing GATE-05 primary tests A, B, C, Coverage, and Anti-feature, plus companion tests C and D. The description accurately matches the test functions in the file.

### No new issues introduced

After b958fcd:

- No debug artifacts introduced (no TODO, FIXME, print, debugger).
- `_REFERENCES_MODULES` remains an alias for `_CAPABILITY_MODULES` (single source of truth, `server.py:766`).
- Three-way mirror (`server._REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES == server._CAPABILITY_MODULES`) is preserved and asserted by `test_references_mcp_server_frozenset_matches`.
- Return contract of `fdars_method_references` is unchanged: hit carries `curated/papers/coverage/version`; miss carries `curated:False/sentinel/message/version`; ambiguous carries `curated:False/sentinel/matches/message/version`.
- LLM-free boundary of the handler is intact: no `import fdars.advisor`, no `anthropic`, no `openai`.

## Acknowledged (not fixed, info only, carried forward)

**IN-01** (`python/fdars/mcp/server.py:963-985`): The `NO_CURATED_ENTRY` and `AMBIGUOUS_CALLABLE` sentinel responses omit the `coverage` field that the hit response includes. Minor API inconsistency; callers can guard with `.get("coverage")`. Deferred to a future cleanup pass per 82-REVIEW-FIX.md.

---

_Reviewed: 2026-09-07_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
_Iteration: 2 (post-fix re-review)_
