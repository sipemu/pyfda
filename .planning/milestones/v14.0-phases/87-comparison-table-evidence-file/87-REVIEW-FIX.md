---
phase: 87-comparison-table-evidence-file
fixed_at: 2026-09-09T00:00:00Z
review_path: .planning/phases/87-comparison-table-evidence-file/87-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 87: Code Review Fix Report

**Fixed at:** 2026-09-09
**Source review:** `.planning/phases/87-comparison-table-evidence-file/87-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 6 (1 critical, 3 warnings, 2 info)
- Fixed: 6
- Skipped: 0

## Fixed Issues

### CR-01: Broken URL in tidyfun evidence — `cran.r-parse.org` is not a real domain

**Files modified:** `paper/comparison_evidence.md`
**Commit:** b4e0608
**Applied fix:** Changed `https://cran.r-parse.org/web/views/FunctionalData.html` to
`https://cran.r-project.org/web/views/FunctionalData.html` on line 215 (tidyfun
Functional regression row). Also ran `grep -nE 'r-parse|r-projct|pypi\.or[^g]|arxiv\.or[^g]'`
across the file — no other malformed URLs found.

---

### WR-01: SC-3 gate does not verify state consistency — evidence `partial` satisfies table `checkmark`

**Files modified:** `paper/code/check_comparison.py`
**Commit:** 1dc2cc6
**Applied fix:** Rewrote the evidence-collection loop in `_check()` to also track
`best_state` (the best evidence state seen across all member packages for a family cell).
After the evidenced/unsourced decision, a new branch emits `STATE_MISMATCH: <col> / <dim>
(table=checkmark, best_evidence=partial)` when the table is checkmark but every matching
evidence entry is only partial. Current data passes cleanly (no real mismatch).

Negative test run: downgraded scikit-fda Registration evidence from `✓` to `partial`
in-memory, confirmed `STATE_MISMATCH: scikit-fda / Registration / alignment
(table=checkmark, best_evidence=partial)` fired (exit 1), then restored the file and
confirmed exit 0. Gate enhanced, no existing checks weakened.

---

### WR-02: `fda` package checkmarks for Registration and FPCA are evidenced only via CRAN task view

**Files modified:** `paper/comparison_evidence.md`
**Commit:** 6628a39
**Applied fix:** For the `fda 6.3.0` section:
- Changed `Spot-checked: NO` to `Spot-checked: YES (CRAN index + fda reference manual PDF, 2026-09-09)`
- Registration / alignment row: added function names `register.fd / landmarkreg` and the
  fda reference manual URL (`https://cran.r-project.org/web/packages/fda/fda.pdf`) as a
  secondary source alongside the CRAN task view URL.
- FPCA / covariance row: added function name `pca.fd` and the same reference manual URL
  as a secondary source.

These are canonical Ramsay `fda` functions documented in the reference manual; the change
strengthens the citation from an aggregating task view to package-level evidence. The
traceability gate still passes (COMPARISON_TRACE_OK).

---

### WR-03: `_norm` contains a duplicate `replace` call — `r'\&'` and `'\\&'` are the same string

**Files modified:** `paper/code/check_comparison.py`
**Commit:** 322bba2
**Applied fix:** Removed the redundant second `.replace("\\&", "&")` call, keeping only
the raw-string form `t.replace(r"\&", "&")`. Verified with
`.venv/bin/python -W error::SyntaxWarning -c "import sys; sys.path.insert(0,'paper/code'); import check_comparison"` — no SyntaxWarning raised.

---

### IN-01: Forward-looking version comment embedded in committed source

**Files modified:** `paper/sections/comparison_table.tex`
**Commit:** d78c57e
**Applied fix:** Replaced `% \FdarsVersion updated to 0.13.0 in Phase 90 (REL-01).`
with `% TODO(REL-01): bump \FdarsVersion to 0.13.0 when Phase 90 releases.` — the
standard TODO marker makes the aspirational nature unambiguous.

---

### IN-02: DIMENSION_SUBMODULES is not validated against the table at startup — silent drift risk

**Files modified:** `paper/code/check_comparison.py`
**Commit:** 08b404c
**Applied fix:** Added a bidirectional key validation block at the start of `main()`.
After `rows = _parse_table(...)`, computes `table_labels = {label for label, _ in rows}`
then `orphan_keys = set(DIMENSION_SUBMODULES.keys()) - table_labels`. If any orphan keys
exist, prints `ORPHAN_SUBMODULE_KEY: <key> (in DIMENSION_SUBMODULES but not in table)`
to stderr and exits 1. Current data passes (14 keys, all matched).

Negative test run: injected `"Stale dimension that no longer exists": ("stale_mod",)` into
DIMENSION_SUBMODULES, confirmed gate fired with `ORPHAN_SUBMODULE_KEY: 'Stale dimension
that no longer exists' ...`, then restored and confirmed exit 0. Both directions now covered.

---

## Post-fix Verification

**check_comparison.py:** `COMPARISON_TRACE_OK` (exit 0)
**No `r-parse` URLs:** `grep -rn 'r-parse' paper/` — CLEAN
**No SyntaxWarning:** `-W error::SyntaxWarning` import of check_comparison — CLEAN
**Pipeline determinism:** `git diff --exit-code paper/figures/ paper/coverage_counts.tex paper/refs.bib` — no changes (fully deterministic)
**All paper gates:** assert_coverage OK, gen_refs_bib OK, COMPARISON_TRACE_OK

Verification ran using `.venv/bin/python` (the project's installed virtual environment,
not the main checkout's system Python).

---

_Fixed: 2026-09-09_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
