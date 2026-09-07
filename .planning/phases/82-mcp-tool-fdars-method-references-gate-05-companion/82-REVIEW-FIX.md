---
phase: 82-mcp-tool-fdars-method-references-gate-05-companion
fixed_at: 2026-09-07T00:00:00Z
review_path: .planning/phases/82-mcp-tool-fdars-method-references-gate-05-companion/82-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 82: Code Review Fix Report

**Fixed at:** 2026-09-07
**Source review:** `.planning/phases/82-mcp-tool-fdars-method-references-gate-05-companion/82-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (critical_warning scope; IN-01 excluded)
- Fixed: 2
- Skipped: 0

## Fixed Issues

### WR-01: AST boundary test misses `from fdars import advisor` import form

**Files modified:** `tests/test_guard_sync_version_independent.py`
**Commit:** b958fcd
**Applied fix:** Added `forbidden_fdars_names = {"advisor"}` and a nested check inside the `ast.ImportFrom` branch: when `node.module == "fdars"`, each alias name is asserted not in `forbidden_fdars_names`. This catches `from fdars import advisor` while leaving `from fdars import __version__` (the handler's legitimate import) untouched since `__version__` is not in the forbidden set. The existing checks for `from fdars.advisor import X` and `import fdars.advisor` are preserved unchanged.

Verification: All 12 guard tests pass (`12 passed in 1.43s`). Syntax check via `ast.parse()` confirms no structural corruption. Verification ran in the main checkout.

### WR-02: Test module-level docstring not updated for Guard Group 3

**Files modified:** `tests/test_guard_sync_version_independent.py`
**Commit:** b958fcd
**Applied fix:** Extended the module docstring (after the Guard Group 2 section) with a full Guard Group 3 block describing GATE-05 primary tests A, B, C, Coverage, Anti-feature, and companion tests C and D. A maintainer reading the header now learns that the file also guards the LLM-free boundary of `fdars_method_references` and the `_REFERENCES_MODULES` frozenset mirror.

Verification: All 12 guard tests pass. Syntax check clean. Verification ran in the main checkout.

## Skipped Issues

None — all in-scope findings were fixed.

## Acknowledged (out of scope)

### IN-01: `coverage` field absent from sentinel and ambiguous responses

**File:** `python/fdars/mcp/server.py:963-985`
**Reason:** Info severity — excluded from `critical_warning` fix scope.
**Original issue:** The `NO_CURATED_ENTRY` and `AMBIGUOUS_CALLABLE` sentinel responses omit a `coverage` field that the hit response includes. Minor API inconsistency; the RESEARCH.md design intent matches the current behavior. Callers can guard with `.get("coverage")`. No fix applied; issue is on record for a future cleanup pass.

---

_Fixed: 2026-09-07_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
