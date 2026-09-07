---
phase: 83-docs-llms-txt-skill-extension
fixed_at: 2026-09-07T00:00:00Z
review_path: .planning/phases/83-docs-llms-txt-skill-extension/83-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 83: Code Review Fix Report

**Fixed at:** 2026-09-07T00:00:00Z
**Source review:** .planning/phases/83-docs-llms-txt-skill-extension/83-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03)
- Fixed: 3
- Skipped: 0

## Fixed Issues

### WR-01: llms.txt presents two contradictory callable totals in the same file

**Files modified:** `scripts/generate_capability_dataset.py`, `docs/llms.txt`, `docs/references.md`, `.claude/skills/fdars-capabilities/SKILL.md`
**Commit:** e262e0f
**Applied fix:**

In `_provenance_section_lines`, the Coverage line now reads:
```
Coverage: 28 of 437 callables (including 28 Fdata class methods) have curated primary-paper entries.
```
The `n_fdata_methods` variable is derived live from `cap_data.get("_Fdata", {})` — never hardcoded. The closing blockquote was reworded from `> Uncurated callables (409 of 437) are absent from this section.` to `> 409 of 437 total callables are not yet curated and are absent from this section.` — removing the bare parenthetical that collided with the "409 public callables" header figure.

IN-01 fixed simultaneously: `_emit_references_page` intro blockquote no longer contains the tautological `(authoring: 28/437)` parenthetical; text reads `have at least one curated primary-paper entry.`

IN-02 fixed simultaneously: `SKILL.md` line 78 comment updated from `# Browse the full 409-callable digest:` to `# Browse the full API digest (409 public module callables + 28 Fdata class methods = 437 total):`.

Docs regenerated via `PYTHONPATH= .venv/bin/python scripts/generate_capability_dataset.py --references`. Regeneration confirmed deterministic: `docs/llms.txt` changed 4 lines, `docs/references.md` changed 2 lines.

**Reconciled coverage wording:**
- `docs/llms.txt` header: "409 public callables" (30 public submodules, excludes `_Fdata`)
- `docs/llms.txt` provenance section: "28 of 437 callables (including 28 Fdata class methods)"
- `docs/llms.txt` closing blockquote: "409 of 437 total callables are not yet curated"
- `docs/references.md` intro: "**28/437 callables** have at least one curated primary-paper entry"

No reader or machine consumer can conflate the "409 public callables" count with the coverage denominator.

---

### WR-02: test_references_skill_boundary.py missing Path B test

**Files modified:** `tests/test_references_skill_boundary.py`
**Commit:** 766f098
**Applied fix:**

Added `test_references_curated_false_hit_returns_path_b`: asserts that `clustering.align_cluster_fd` (in `callable_index`, sole backing paper `_uncurated_align_cluster_fd_2026-09` with `curated: false`) returns `curated: False`, has `papers` in the result, and does NOT have `sentinel == "NO_CURATED_ENTRY"`. Updated module docstring to accurately list all three paths (A/B/C). Test is gated with `pytest.importorskip("mcp")` consistent with the other two tests.

**Test results:** 3/3 passed (Python 3.14.7, mcp available in .venv). Path B test ran live against the MCP handler rather than skipping.

---

### WR-03: check_references_render.py does not assert _uncurated sentinel absence

**Files modified:** `scripts/check_references_render.py`
**Commit:** 2597b71
**Applied fix:**

Added `check_no_sentinel_leakage(docs_dir, repo_root)` as check [5]. The function reads both `docs/references.md` and `docs/llms.txt`, counts `_uncurated` occurrences, and calls `sys.exit(1)` with a descriptive error message if any are found. Called from `main()` after the existing four checks. Module docstring updated to list check [5]. Stdlib-only (pathlib, sys).

**Checker output:**
```
Running fast render/nav-validity check for docs/references.md ...
  [1] docs/references.md exists: OK
  [2] Code-fence balance: OK (0 markers, all paired)
  [3] Nav placement: OK ('Scientific References: references.md' at mkdocs.yml line 170)
  [4] Internal links: OK (2 relative .md link(s) resolve: ai-capability-map.md, ai-capability-map.md)
  [5] Sentinel leakage: OK (no '_uncurated' in references.md or llms.txt)
RENDER_VALIDITY_OK
```

---

## Verification Notes

All verification ran in the main checkout (workflow.use_worktrees=false).

- `grep -c "_uncurated" docs/references.md docs/llms.txt` → 0/0
- `PYTHONPATH= .venv/bin/python scripts/check_references_render.py` → RENDER_VALIDITY_OK (5/5 checks)
- `pytest tests/test_references_skill_boundary.py -v` → 3 passed in 0.73s

---

_Fixed: 2026-09-07T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
