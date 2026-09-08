---
phase: 87-comparison-table-evidence-file
reviewed: 2026-09-09T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - paper/code/check_comparison.py
  - paper/sections/comparison_table.tex
  - paper/sections/comparison.tex
  - paper/comparison_evidence.md
  - paper/paper.tex
  - Makefile
  - .github/workflows/paper.yml
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: issues_found
---

# Phase 87: Code Review Report

**Reviewed:** 2026-09-09T00:00:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Phase 87 delivered the peer-comparison table (`comparison_table.tex`), the evidence
file (`comparison_evidence.md`), and the SC-3/COMP-02 traceability gate
(`check_comparison.py`). The gate executes correctly against the current data and
passes cleanly. The LaTeX table structure is valid (booktabs correct, column count
consistent, adjustbox properly closed). DIMENSION_SUBMODULES labels match the table
parser output exactly on all 14 dimensions, so grounding is sound and cannot
silently drift by label mismatch in the current state.

Three issues require attention before submission:

1. A broken URL in `comparison_evidence.md` (`r-parse.org` instead of `r-project.org`)
   would fail a peer reviewer spot-checking citations — this is the highest-urgency fix.
2. The SC-3 gate has a structural gap: it accepts any non-`none` evidence state as
   satisfying a table `checkmark` cell, so a `partial` evidence entry can "evidence"
   a `checkmark` table cell without triggering a failure. Currently no such mismatch
   exists, but the gap is a latent false-negative in the traceability claim.
3. Two `fda` (R package) checkmark cells are evidenced solely via the CRAN task view
   (an aggregating document) rather than the `fda` package's own documentation — this
   is the weakest evidence in the file and the most likely reviewer pushback point.

---

## Critical Issues

### CR-01: Broken URL in tidyfun evidence — `cran.r-parse.org` is not a real domain

**File:** `paper/comparison_evidence.md:215`
**Issue:** The source URL for the tidyfun / Functional regression row contains
`https://cran.r-parse.org/web/views/FunctionalData.html`. The correct domain is
`cran.r-project.org`. `r-parse.org` does not exist; the link is dead. A peer
reviewer checking citations will reach a 404. This directly undermines the
traceability claim in `comparison.tex` ("all non-fdars cells are sourced").

**Fix:**
```diff
-| Functional regression (SoF / FoF) | — | Not a primary feature | https://cran.r-parse.org/web/views/FunctionalData.html |
+| Functional regression (SoF / FoF) | — | Not a primary feature | https://cran.r-project.org/web/views/FunctionalData.html |
```

---

## Warnings

### WR-01: SC-3 gate does not verify state consistency — evidence `partial` satisfies table `checkmark`

**File:** `paper/code/check_comparison.py:334-348`
**Issue:** The SC-3 check considers a covered cell "evidenced" if at least one member
package has any non-`none` claim for the dimension — regardless of whether the evidence
claim is `checkmark` or `partial`. This means a table cell with state `checkmark` could
be fully satisfied by a `partial` evidence entry without triggering an `UNSOURCED`
failure. In the current data no such mismatch exists (verified: all table-`checkmark`
peer cells have at least one `checkmark` backing in evidence). However, the gate would
silently pass if a future edit upgraded a table cell from `partial` to `checkmark` without
updating the evidence to match.

**Fix:** Add a state-level check. Either fail when the table state is `checkmark` but the
best evidence state is only `partial`, or at minimum emit a warning to stderr:

```python
# In _check(), after evidenced=True is determined, also check state quality:
best_state = "none"
for pkg in member_pkgs:
    for ek, eclaims in evidence.items():
        ek_lower = ek.lower()
        pkg_lower = pkg.lower()
        if ek_lower == pkg_lower or ek_lower.startswith(pkg_lower + " "):
            ev = eclaims.get(dim_label, "none")
            if ev == "checkmark":
                best_state = "checkmark"
            elif ev == "partial" and best_state == "none":
                best_state = "partial"

if evidenced and state == "checkmark" and best_state == "partial":
    misses.append(
        f"STATE_MISMATCH: {col_name} / {dim_label} "
        f"(table=checkmark, best_evidence=partial)"
    )
```

### WR-02: `fda` package checkmarks for Registration and FPCA are evidenced only via CRAN task view

**File:** `paper/comparison_evidence.md:87, 89`
**Issue:** The `fda 6.3.0` section awards `checkmark` to both "Registration / alignment"
(line 87) and "FPCA / covariance / PACE sparse FPCA" (line 89) with the CRAN task view
(`/web/views/FunctionalData.html`) as the sole source. The task view aggregates multiple
R packages and does not constitute package-level evidence for `fda` specifically. A
reviewer checking that the `fda` package itself provides first-class registration or FPCA
support would need to be directed to the `fda` package manual or a package-specific URL.
Note the `fda` section is also the only one marked `Spot-checked: NO` with no compensating
package-level URL.

**Fix:** Replace or supplement the task view source with a package-level URL. Acceptable
alternatives:

- `https://cran.r-project.org/web/packages/fda/index.html` (CRAN index with the
  official package description) — add this as a secondary source.
- `https://cran.r-project.org/web/packages/fda/fda.pdf` (the 290-page reference manual
  which documents `register.fd`, `smooth.basisPar`, and `pca.fd` explicitly).

Minimum fix — add the package manual URL as a secondary source in both rows:
```
| Registration / alignment | ✓ | ... | https://cran.r-project.org/web/views/FunctionalData.html; https://cran.r-project.org/web/packages/fda/fda.pdf |
| FPCA / covariance / PACE sparse FPCA | ✓ | ... | https://cran.r-project.org/web/views/FunctionalData.html; https://cran.r-project.org/web/packages/fda/fda.pdf |
```

### WR-03: `_norm` contains a duplicate `replace` call — `r'\&'` and `'\\&'` are the same string

**File:** `paper/code/check_comparison.py:113`
**Issue:** The normalization line is:
```python
t = t.replace(r"\&", "&").replace("\\&", "&")
```
In Python, `r"\&"` and `"\\&"` are identical byte sequences (`backslash` + `&`). The
second `replace` call is therefore completely redundant — it can never replace anything
the first call did not already handle. This is not currently causing incorrect behaviour,
but it is misleading: a future maintainer might read this as intentionally handling a
different case (e.g., double-escaped `\\&`) and rely on it. The Python 3.12+ `SyntaxWarning`
for invalid escape sequences already flags `"\&"` as a deprecated form.

**Fix:** Remove the redundant call and use the raw-string form only:
```python
t = t.replace(r"\&", "&")
```

---

## Info

### IN-01: Forward-looking version comment embedded in committed source

**File:** `paper/sections/comparison_table.tex:4`
**Issue:** The file contains the comment:
```
% \FdarsVersion updated to 0.13.0 in Phase 90 (REL-01).
```
This is a planning note for a future phase committed into the source, not a description
of the current state. The macro itself currently defines `0.12.0` (correct for the current
package version). The comment creates ambiguity: a reader or tool cannot tell whether the
update has already occurred.

**Fix:** Remove the forward-looking comment or replace it with a standard `TODO:` marker
that is understood as aspirational:
```latex
% TODO(REL-01): bump \FdarsVersion to 0.13.0 when Phase 90 releases.
```
Alternatively, remove it entirely and rely on the git history.

### IN-02: DIMENSION_SUBMODULES is not validated against the table at startup — silent drift risk for future rows

**File:** `paper/code/check_comparison.py:71-86`
**Issue:** `DIMENSION_SUBMODULES` is a hardcoded dict whose keys must exactly match the
normalized dimension labels produced by the table parser. Currently all 14 keys match
perfectly. However, if a new capability dimension is added to `comparison_table.tex`
without a corresponding entry in `DIMENSION_SUBMODULES`, the new row will receive
`submodules=()` (empty tuple) and immediately fail with `UNGROUNDED` — which is correct
behavior and will catch the drift. The reverse case is invisible: an entry in
`DIMENSION_SUBMODULES` whose key does not match any table row is never exercised and
silently decays. A startup validation asserting no orphan keys exist in
`DIMENSION_SUBMODULES` would make the check fully bidirectional.

**Fix:** Add an assertion in `main()` after `rows` is parsed:

```python
table_labels = {label for label, _ in rows}
orphan_keys = set(DIMENSION_SUBMODULES.keys()) - table_labels
if orphan_keys:
    for k in sorted(orphan_keys):
        print(f"ORPHAN_SUBMODULE_KEY: {k!r} (in DIMENSION_SUBMODULES but not in table)",
              file=sys.stderr)
    sys.exit(1)
```

---

_Reviewed: 2026-09-09T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
