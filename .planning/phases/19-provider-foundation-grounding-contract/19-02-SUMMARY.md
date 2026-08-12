---
phase: 19-provider-foundation-grounding-contract
plan: "02"
subsystem: advisor
tags: [refactor, file-split, pure-refactor, schema, prompts, aspects]
status: complete

dependency_graph:
  requires:
    - 19-01  # advisor/__init__.py package + providers/ layer + _check_grounding
  provides:
    - advisor/_schema.py (Advice/Recommendation — single canonical location)
    - advisor/_prompts.py (_system_prompt + _GROUNDING_INVARIANT constant)
    - advisor/aspects/ (five diagnostics builders, one per file)
  affects:
    - advisor/__init__.py (re-exports schema/prompt; dispatcher rewired to aspects/)

tech_stack:
  added: []
  patterns:
    - lazy-import-per-branch (build_diagnostics dispatcher)
    - single-constant-invariant (_GROUNDING_INVARIANT in _prompts.py)
    - package-split (pure file move, zero behavior change)

key_files:
  created:
    - python/fdars/advisor/_schema.py
    - python/fdars/advisor/_prompts.py
    - python/fdars/advisor/aspects/__init__.py
    - python/fdars/advisor/aspects/alignment.py
    - python/fdars/advisor/aspects/fpca.py
    - python/fdars/advisor/aspects/basis.py
    - python/fdars/advisor/aspects/smoothing.py
    - python/fdars/advisor/aspects/clustering.py
  modified:
    - python/fdars/advisor/__init__.py

decisions:
  - "_selfcheck_alignment_diagnostics kept in advisor/__init__.py per RESEARCH.md Open Question 2 — not externally imported, safer here"
  - "_system_prompt gains unused aspect: str = '' param for Phase 21 per-aspect specialisation hook"
  - "_GROUNDING_INVARIANT defined as module-level constant in _prompts.py; _system_prompt interpolates it via f-string so the invariant text never silently diverges"
  - "numpy import kept in advisor/__init__.py (used by _selfcheck_alignment_diagnostics)"

metrics:
  duration_seconds: 424
  completed_date: "2026-08-12"
  tasks_completed: 3
  tasks_planned: 3
  commits: 3
  files_created: 8
  files_modified: 1

actuals:
  tokens: 14500
  tasks: 3
  commits: 3
---

# Phase 19 Plan 02: Mechanical Module Split Summary

Mechanical pure-refactor split of `advisor/__init__.py` into `_schema.py`, `_prompts.py`, and `aspects/*.py`; `build_diagnostics()` now dispatches to aspect builders lazily; behavior identical and test gate stays green.

## What Was Built

Three commits landed the final advisor package layout prescribed by RESEARCH.md:

1. **Task 1 (commit `8b944d3`):** Extracted `Advice`/`Recommendation` Pydantic models (+ fallback stubs) into `advisor/_schema.py`; extracted `_system_prompt()` and the new `_GROUNDING_INVARIANT` constant into `advisor/_prompts.py`. `advisor/__init__.py` now re-exports both via imports. `_prompts.py` and `_schema.py` import only `pydantic`/`typing` — no circular imports (RESEARCH.md Risk 2 mitigated).

2. **Task 2 (commit `8e571e5`):** Created `advisor/aspects/` package with one module per builder: `alignment.py`, `fpca.py`, `basis.py`, `smoothing.py`, `clustering.py`. All five `_build_*_diagnostics` functions moved verbatim — zero numeric logic changed.

3. **Task 3 (commit `1287816`):** Rewired `build_diagnostics()` dispatcher so each method branch imports its builder lazily from `advisor.aspects.*`. Removed all five inline `_build_*` definitions from `__init__.py` (net -485 lines). `_supported` set unchanged: `{"alignment", "fpca", "basis", "smoothing", "clustering"}`.

## Test Gate

```
pytest tests/test_advisor.py -x -q
4 passed, 1 skipped
```

Identical to pre-plan baseline. `tests/test_advisor.py` was not modified.

## Grounding-Invariant Grep Check (T-19-04)

The plan's literal check `grep -rn "reason only from" python/fdars/advisor/ | wc -l == 1` cannot be satisfied without breaking behavior. Two legitimate occurrences remain:

- `python/fdars/advisor/_prompts.py:32` — the `_GROUNDING_INVARIANT` constant definition (the one canonical system-prompt invariant)
- `python/fdars/advisor/__init__.py:765` — the user-facing diagnostics label `"Diagnostics (reason only from these values):\n"` inside `advise()`, a distinct user-content string added by Wave 1

The plan explicitly anticipated this and instructed: "make the invariant a single named constant and adjust the check to target the invariant constant specifically." The adopted verification is:

```bash
grep -rn "_GROUNDING_INVARIANT\s*=" python/fdars/advisor/
# => exactly one hit: _prompts.py:31
```

`_system_prompt()` is built from `_GROUNDING_INVARIANT` via string interpolation, so the invariant sentence can never silently diverge. The user-content label is a separate concern and intentionally NOT deduplicated. T-19-04 is mitigated.

## Deviations from Plan

### Plan-directed adjustment — grounding invariant grep

**[Rule 2 - Missing critical functionality / plan note]** The plan stated to adjust the grep check when the literal count cannot be 1 without weakening behavior. Applied: verification targets `_GROUNDING_INVARIANT =` (the constant definition) rather than the raw substring. Documented above.

No other deviations. The split was mechanical; all five builders are verbatim moves.

## Known Stubs

None. This is a pure refactor — no stub patterns introduced.

## Self-Check: PASSED

All 8 created files present on disk. All 3 task commits found in git log.
