---
phase: 80-schema-data-home-primary-guard-tests
reviewed: 2026-09-07T12:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - python/fdars/_references_map.json
  - tests/test_guard_sync_version_independent.py
  - docs/authoring/references-schema.md
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 80: Code Review Report (Iteration 3 / Final)

**Reviewed:** 2026-09-07T12:00:00Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** clean

## Summary

Final re-review after the docs-example fix applied between iteration 2 and iteration 3.
The previously open warning (WR-01: stale "Shipped example" block in
`docs/authoring/references-schema.md` claiming 11 entries and showing the removed
`smoothing.gcv_smoother`) is confirmed fully resolved.

All four verification tasks pass:

**1. Docs example exactly matches the live JSON.**

`docs/authoring/references-schema.md` line 100 correctly states "10 `callable_index`
entries". The callable_index block in the example (lines 121-133) enumerates exactly
the same 10 keys as the live file, in the same arrangement. `smoothing.gcv_smoother`
is absent from both the docs example and the live JSON.
`eilers_marx_1996.callables` correctly shows `["basis.basis_nbasis_cv"]` on both sides.
A grep for `smoothing.gcv_smoother` across the schema doc returns no matches.

**2. No executable code fences introduced.**

All code blocks use plain ` ```python `, ` ```json `, or bare ` ``` ` fences. No
` ```{exec} ` or any markdown-exec trigger is present. MkDocs build safety is unchanged.

**3. GATE-05 A invariant confirmed — all 8 guard tests green.**

`pytest tests/test_guard_sync_version_independent.py -q` returns `8 passed` (0.77s)
with no skips or failures. The three GATE-05 Group 3 tests (internal consistency,
cross-file resolution, structural DOI/URL gate) and the Group 1/2 guard tests all pass.

Internal consistency spot-check (Python):
- `callable_index` count: 10
- from_papers == from_index: True
- Symmetric difference: empty on both sides

**4. No new Critical/Warning issues in any of the three files.**

- `python/fdars/_references_map.json` — 5 papers, 10 callable_index entries,
  GATE-05 A consistent; all DOIs match the `^10\.\d{4,9}/\S+$` regex; all URLs parse
  to allowed domains; the single cross-language entry (fraiman_muniz_2001 / R /
  fda.usc) carries all four required fields (package, function, url, confidence).
- `tests/test_guard_sync_version_independent.py` — guard logic is correct; sentinel
  string is unique and will not appear in any real method name; `ast.literal_eval` is
  applied only to the bracketed substring already validated to start with `[` and end
  with `]`; Python-version guards are correctly placed (companion tests skip on 3.9
  via explicit `sys.version_info` check before `pytest.importorskip`); no mcp import
  at module level; `from __future__ import annotations` on line 34 covers the
  `frozenset[str]` subscript annotations used throughout.
- `docs/authoring/references-schema.md` — no stale content, no exec fences, no
  dead cross-references to removed callables; pitfall documentation, GATE descriptions,
  and worked examples all consistent with the current JSON and test file.

All reviewed files meet quality standards. No issues found.

---

_Reviewed: 2026-09-07T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
