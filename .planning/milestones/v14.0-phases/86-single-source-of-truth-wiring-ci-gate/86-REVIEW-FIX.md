---
phase: 86-single-source-of-truth-wiring-ci-gate
fixed_at: 2026-09-08T00:00:00Z
review_path: .planning/phases/86-single-source-of-truth-wiring-ci-gate/86-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 86: Code Review Fix Report

**Fixed at:** 2026-09-08T00:00:00Z
**Source review:** .planning/phases/86-single-source-of-truth-wiring-ci-gate/86-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5
- Fixed: 5
- Skipped: 0

## Fixed Issues

### CR-01: gen_refs_bib.py emits `year = {None},` for JSON null year fields

**Files modified:** `paper/code/gen_refs_bib.py`, `paper/refs.bib`
**Commit:** 02b9165
**Applied fix:**
- Changed `year = paper.get("year", "")` to `year = paper.get("year") or ""` so JSON `null`
  values are coerced to empty string instead of Python `None`.
- Applied the same `or []` guard to `authors` and `or ""` guard to `title` for consistency.
- Made author/title/year lines conditional on truthiness (mirror the existing doi/url pattern),
  so sparse entries like `dabo_gijbels_2010` produce no invalid BibTeX fields.
- Regenerated `paper/refs.bib` with the fix; verified `! grep -q '{None}' paper/refs.bib`
  and `grep -cE '^@misc\{' paper/refs.bib` equals 47.

---

### WR-01: No drift gate for refs.bib — committed copy can silently go stale

**Files modified:** `paper/code/gen_refs_bib.py`, `.github/workflows/paper.yml`
**Commit:** 3c9124a
**Applied fix:**
- Refactored `main()` to delegate content derivation to a new `_build_content()` helper so
  both generate and check modes share identical logic.
- Added `--check` mode (symmetric to `assert_coverage.py --check`): regenerates in memory,
  compares byte-for-byte against committed `paper/refs.bib`, exits 1 on mismatch with a
  clear DRIFT message.
- Added module docstring section documenting `--check` usage.
- Inserted "Assert refs.bib not stale (PIPE-04 drift gate)" step in `paper.yml` before the
  Regenerate step so CI fails when the committed file is stale.
- Verified `--check` exits 0 on current file and exits 1 after mutation (file restored).

---

### WR-02: assert_coverage.py docstring says "non-dunder" but code filters all underscore-prefixed names

**Files modified:** `paper/code/assert_coverage.py`
**Commit:** 9e5c6fc
**Applied fix:**
- Updated module docstring (`\nfdata` macro description) to say "non-underscore-prefixed" instead
  of "non-dunder" to accurately describe the actual filter `not m.startswith("_")`.
- Updated inline comment on the `fdata_public` list comprehension from "non-dunder entries"
  to "non-underscore-prefixed entries (public API surface)".
- Chose option (a) from the review: fix docstring to match code (the code's filter is the
  correct semantic for a public API count).
- Confirmed `assert_coverage.py --check` still passes (nfdata unchanged, coverage_counts.tex
  is byte-identical: `git diff --exit-code paper/coverage_counts.tex` is clean).

---

### WR-03: Community CI action wtfjoke/setup-tectonic@v4 pinned to mutable tag

**Files modified:** `.github/workflows/paper.yml`
**Commit:** da1d98e
**Applied fix:**
- Resolved commit SHA for the v4 tag via `git ls-remote https://github.com/wtfjoke/setup-tectonic.git v4`
  (SHA: `eb29fd68b7d3f76011906b6e45ea4320c8de5d2f`).
- Pinned the action to the immutable SHA: `wtfjoke/setup-tectonic@eb29fd68b7d3f76011906b6e45ea4320c8de5d2f  # v4`
- YAML syntax verified after the change.

---

### IN-01: No make paper-check target for local drift verification

**Files modified:** `Makefile`
**Commit:** 6a43609
**Applied fix:**
- Added `.PHONY paper-check` target that runs both drift --check invocations:
  `assert_coverage.py --check` and `gen_refs_bib.py --check`.
- Added `paper-check` to the `.PHONY` declaration line.
- Verified `make -n paper-check` lists both invocations.

---

## Verification

All post-fix gate checks run in the main checkout (workflow.use_worktrees=false):

```
assert_coverage: OK (no drift)        # assert_coverage.py --check
gen_refs_bib: OK (no drift)           # gen_refs_bib.py --check
NO_NONE                                # ! grep -q '{None}' paper/refs.bib
ENTRY_COUNT_OK                         # grep -cE '^@misc\{' paper/refs.bib == 47
PIPELINE_DETERMINISTIC                 # git diff --exit-code paper/figures/ paper/coverage_counts.tex paper/refs.bib
```

---

_Fixed: 2026-09-08T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
