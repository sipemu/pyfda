---
phase: 67-functional-time-series-fts
plan: "67-05"
subsystem: testing
tags: [pytest, git, submodule-registration, invariant, sklearn-foundation]

requires:
  - phase: 55-sklearn-foundation
    provides: FND-02 guard contract and Phase-55 _submodule_names baseline commit

provides:
  - FND-02 rewritten as a forward-compatible subset+registration invariant
  - Full test suite green (5366 passed, 0 failed) with fts submodule in place

affects:
  - phases 68-71 (future binding phases that add submodules will continue to pass FND-02)

actuals:
  tokens: 3200
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Parse _submodule_names from git show output (not live module) because __init__.py deletes the name after registration"
    - "Subset invariant: baseline ⊆ current — additive submodules allowed, removals fail"

key-files:
  created: []
  modified:
    - tests/sklearn/test_foundation.py

key-decisions:
  - "Parse _submodule_names from git source (git show HEAD:python/fdars/__init__.py) rather than importing fdars at test-collection time, because __init__.py deletes _submodule_names from the module namespace after the registration loop"
  - "Assert baseline ⊆ current (not equality) so phases 68-71 that add new submodules will not re-trip FND-02"
  - "Retain the git cat-file -e base-present guard with its actionable fetch-depth:0 CI message verbatim"

patterns-established:
  - "FND-02 pattern: recover baseline from git history, parse source with regex, assert subset + per-name import/attribute check"

requirements-completed: [FTS-01]

coverage:
  - id: D1
    description: "FND-02 guard rewritten as subset+registration invariant — no byte-freeze; passes with fts present"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: "tests/sklearn/test_foundation.py::test_fdars_init_unchanged"
        status: pass
      - kind: integration
        ref: "pytest tests/ -q → 5366 passed, 0 failed"
        status: pass
    human_judgment: false

duration: 8min
completed: "2026-09-02"
status: complete
---

# Phase 67 Plan 05: FND-02 Guard Refactored to Subset+Registration Invariant Summary

**FND-02 rewritten to assert Phase-55 baseline _submodule_names ⊆ current set plus per-name import/attribute registration, eliminating the git-diff byte-freeze that broke on every new submodule addition**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-02T20:27:00Z
- **Completed:** 2026-09-02T20:35:17Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Replaced the `git diff --quiet` byte-freeze assertion with a two-part invariant: (1) Phase-55 baseline `_submodule_names` is a subset of the current set, and (2) every current submodule imports as `fdars.<name>` and is attached as a module attribute
- Kept the `git cat-file -e` base-present guard and its actionable fetch-depth:0 CI message verbatim
- Added a helper `_parse_submodule_names()` that reads `_submodule_names` from `git show` output (not from the live module, because `__init__.py` deletes the name after registration with `del _submodule_names`)
- Full suite: 5366 passed, 10 skipped, 0 failed — was 1 failed before this fix

## Task Commits

1. **Task 1: Rewrite test_fdars_init_unchanged as an invariant check** - `4d2a0cc` (refactor)

## Files Created/Modified

- `tests/sklearn/test_foundation.py` — FND-02 body replaced; FND-01 and all FND-03 tests untouched

## Decisions Made

- Parse `_submodule_names` from `git show HEAD:python/fdars/__init__.py` source rather than from the imported `fdars` module, because `__init__.py` explicitly `del`s the name after the registration loop. Using regex on the source file avoids importing fdars in a fragile way or needing to modify `__init__.py`.
- Assert subset (`baseline ⊆ current`) rather than equality, so adding `fts` (Phase 67) or future submodules (phases 68–71) does not re-trip the guard.
- Retain the exact wording and structure of the `git cat-file -e` base-present guard from the original test, including the actionable "set fetch-depth: 0" CI message.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Self-Check: PASSED

- `tests/sklearn/test_foundation.py` exists on disk: FOUND
- Commit `4d2a0cc` exists in git log: FOUND
- `pytest tests/sklearn/test_foundation.py -q` → 15 passed: PASS
- `pytest tests/ -q` → 5366 passed, 0 failed: PASS
- `git diff --name-only HEAD -- . ':!tests/sklearn/test_foundation.py'` → only `.planning/state.json` (pre-existing uncommitted change, not from this task): PASS

## Next Phase Readiness

- FND-02 guard is forward-compatible: phases 68–71 may add new submodules to `_submodule_names` without tripping the guard
- The sklearn-safety invariant (FND-01) remains untouched and independently enforced
- Phase 67 full suite is green; ready for phase closeout

---
*Phase: 67-functional-time-series-fts*
*Completed: 2026-09-02*
