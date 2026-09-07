---
phase: 80-schema-data-home-primary-guard-tests
fixed_at: 2026-09-07T11:00:00Z
review_path: .planning/phases/80-schema-data-home-primary-guard-tests/80-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 80: Code Review Fix Report

**Fixed at:** 2026-09-07T11:00:00Z
**Source review:** .planning/phases/80-schema-data-home-primary-guard-tests/80-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (CR-01, WR-01, WR-02; IN-01 excluded by fix_scope=critical_warning)
- Fixed: 3
- Skipped: 0

## Fixed Issues

### CR-01: Incorrect Paper Attribution — `smoothing.gcv_smoother` Attributed to P-Splines Paper

**Files modified:** `python/fdars/_references_map.json`
**Commit:** 6829967
**Applied fix:** Removed `smoothing.gcv_smoother` from `eilers_marx_1996.callables` (leaving only `basis.basis_nbasis_cv`) and removed the `"smoothing.gcv_smoother": ["eilers_marx_1996"]` entry from `callable_index`. Both sides removed simultaneously so GATE-05 A internal-consistency invariant (`frozenset(callable_index.keys()) == frozenset(union of papers[*].callables)`) continues to hold. The callable is now uncurated — it falls into the `curated:false` tail for Phase 81/82 to handle with a correct citation.

### WR-01: GATE-05 C Does Not Enforce `url` Presence for `curated: true` Entries

**Files modified:** `tests/test_guard_sync_version_independent.py`
**Commit:** 6bc6398
**Applied fix:** Added a presence check before the existing URL well-formedness block:
```python
if paper.get("curated", True) and not url:
    errors.append(
        f"papers[{key!r}] is curated:true but has no url (url is required)"
    )
```
A `curated: true` paper with an empty or absent `url` now fails GATE-05 C. All existing seed entries carry non-empty `url` values so no data fix was needed.

### WR-02: GATE-05 C Does Not Validate Required `cross_language` Sub-Fields

**Files modified:** `tests/test_guard_sync_version_independent.py`
**Commit:** 6bc6398
**Applied fix:** Added required-field presence iteration inside the `cross_language` loop (before the URL domain/scheme check):
```python
for required_field in ("package", "function", "url", "confidence"):
    if required_field not in cl_entry:
        errors.append(
            f"papers[{key!r}].cross_language[{lang!r}] missing required "
            f"field {required_field!r}"
        )
```
Every `cross_language` entry must now carry `package`, `function`, `url`, and `confidence`. The existing `fraiman_muniz_2001.cross_language.R` seed entry already carries all four fields, so no data fix was needed.

## Skipped Issues

None.

## Verification

**Verification environment:** main checkout (workflow.use_worktrees=false).

After applying both fixes, all 8 tests in `tests/test_guard_sync_version_independent.py` pass:

```
........                                                                 [100%]
8 passed in 0.86s
```

GATE-05 A, B, and C are all green. JSON syntax verified via `node -e JSON.parse`. Python syntax verified via `python -c ast.parse`.

---

_Fixed: 2026-09-07T11:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_

---

## Iteration 2 Fix Pass

**Fixed at:** 2026-09-07T11:45:00Z
**Source review:** `.planning/phases/80-schema-data-home-primary-guard-tests/80-REVIEW.md` (re-review pass 2)
**Findings in scope:** 1 (WR-01 new)
**Fixed:** 1
**Skipped:** 0

### WR-01 (iter 2): `references-schema.md` "Shipped example" Shows Pre-Fix Seed — Stale Documentation

**Files modified:** `docs/authoring/references-schema.md`
**Commit:** 3a46732
**Applied fix:**
Three targeted edits to the "Shipped example (Phase 80 seed)" section at lines 100-134:

1. Line 100: Changed "11 `callable_index` entries" to "10 `callable_index` entries".
2. Lines 117-119: Removed `"smoothing.gcv_smoother"` from `eilers_marx_1996.callables`
   so the array now shows only `["basis.basis_nbasis_cv"]`, matching the live JSON.
3. Line 131: Removed the `"smoothing.gcv_smoother": ["eilers_marx_1996"],` line from
   the `callable_index` block, leaving exactly 10 entries.

**Verification:**
- Tier 1 (re-read): all three changes confirmed present; surrounding prose intact.
- Tier 2: file is Markdown with only a `json` display fence — no executable fences
  introduced; mkdocs-safe (no `python`/`pycon`/`exec` blocks added).
- Count cross-check: example `callable_index` now has 10 entries
  (3 + 2 + 3 + 1 + 1), matching both the live `python/fdars/_references_map.json`
  and the updated count claim on line 100.
- Verification ran in the main checkout (`workflow.use_worktrees = false`).

---

_Fixed (iter 2): 2026-09-07T11:45:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
