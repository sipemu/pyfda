---
phase: 86-single-source-of-truth-wiring-ci-gate
reviewed: 2026-09-08T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - paper/code/assert_coverage.py
  - paper/code/gen_refs_bib.py
  - .github/workflows/paper.yml
  - Makefile
findings:
  critical: 1
  warning: 3
  info: 1
  total: 5
status: issues_found
---

# Phase 86: Code Review Report

**Reviewed:** 2026-09-08T00:00:00Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 86 wires the single-source-of-truth drift tripwires and CI gate for the arXiv paper
milestone. The `assert_coverage.py` path resolution is correct (`.parent.parent.parent` reaches
the repo root), the `--check` drift comparison is byte-exact with no false positives from
whitespace, the counting semantics match the canonical `_coverage_counts()` denominator
(437 = sum of all values including `_Fdata`; 28 curated callables), and the CI step ordering
correctly runs all pipeline gates before tectonic.

One blocker was found: `gen_refs_bib.py` emits `year = {None},` for entries where the JSON
stores `year: null` (Python `None`), producing invalid BibTeX that is already committed to
`paper/refs.bib`. Three warnings cover: a symmetric drift gate missing for `refs.bib`, a
docstring/code semantic mismatch in `assert_coverage.py`, and a community CI action pinned
to a mutable tag rather than a commit SHA.

---

## Critical Issues

### CR-01: `gen_refs_bib.py` emits `year = {None},` for JSON `null` year fields

**File:** `paper/code/gen_refs_bib.py:63`
**Issue:** The year extraction uses `paper.get('year', '')`. Python's `dict.get(key, default)`
only returns the default when the key is **absent**. When the JSON stores `"year": null`, the
key is present and its value is Python `None`, so `get('year', '')` returns `None` — not `''`.
The f-string `f"  year   = {{{year}}},"` then renders as `  year   = {None},`, which is invalid
BibTeX. This is already materialised in the committed `paper/refs.bib`:

```
@misc{dabo_gijbels_2010,
  author = {},
  title  = {{}},
  year   = {None},          ← invalid BibTeX value
  note   = {Type: journal},
}
```

The same bug would affect any future entry with `"year": null`. This causes BibTeX/tectonic
to either warn or silently emit a malformed year in the compiled PDF.

**Fix:** Change line 63 in `gen_refs_bib.py` from:

```python
# Before
year = paper.get("year", "")
```

to:

```python
# After — handles both missing key (get returns None) and explicit null (value is None)
year = paper.get("year") or ""
```

The same `or ""` idiom is already used for `doi` and `url` on lines 63–64, so this
is the consistent fix.

---

## Warnings

### WR-01: No drift gate for `refs.bib` — committed copy can silently go stale

**File:** `.github/workflows/paper.yml:40-41`
**Issue:** `assert_coverage.py` has a `--check` mode that exits non-zero when
`paper/coverage_counts.tex` is stale (PIPE-03). No equivalent gate exists for
`paper/refs.bib`. The CI workflow regenerates `refs.bib` at step PIPE-04 and then
compiles with the fresh version, but the **committed** `refs.bib` is never compared
against the regenerated output. A developer can change `_references_map.json`, skip
`python paper/code/gen_refs_bib.py`, commit, and CI will silently compile against a
different `refs.bib` than the one in the repository — breaking reproducibility.

**Fix:** Add a `--check` mode to `gen_refs_bib.py` (mirror the pattern in
`assert_coverage.py`) and insert a drift-gate step in the workflow before PIPE-04:

```yaml
# In paper.yml, before the "Regenerate refs.bib" step:
- name: Assert refs.bib not stale (drift gate)
  run: python paper/code/gen_refs_bib.py --check
```

`gen_refs_bib.py --check` should regenerate in memory, compare to the committed file,
and exit 1 on mismatch — identical semantics to `assert_coverage.py --check`.

---

### WR-02: `assert_coverage.py` docstring says "non-dunder" but code filters all underscore-prefixed names

**File:** `paper/code/assert_coverage.py:63`
**Issue:** The module docstring (line 22) and function docstring (line 52) both describe
`nfdata` as counting "non-dunder" `_Fdata` methods. The code on line 63 filters with
`not m.startswith("_")`, which excludes **all** underscore-prefixed names — not just dunders.
These two filters differ: "non-dunder" means `not (m.startswith("__") and m.endswith("__"))`,
while the code excludes single-underscore private methods too.

Currently there are no single-underscore methods in `_Fdata` (only `__init__` is excluded),
so the counts are identical. But if a single-underscore private helper is ever added to
`_Fdata` in `_capability_map.json`, the code's `nfdata` count would differ from what the
docstring describes — and silently produce the wrong macro value.

**Fix:** Either (a) align the docstring to say "non-underscore-prefixed" (which matches the
code's actual intent and is the right behaviour for a public-method count), or (b) change
the filter to strictly match the docstring:

```python
# Option (a) — fix docstring to match code (preferred):
# "public (non-underscore-prefixed) methods in the '_Fdata' key"
fdata_public = [m for m in cap.get("_Fdata", {}) if not m.startswith("_")]

# Option (b) — fix code to match docstring:
fdata_public = [
    m for m in cap.get("_Fdata", {})
    if not (m.startswith("__") and m.endswith("__"))
]
```

Option (a) is the correct semantic for "public API count".

---

### WR-03: Community CI action `wtfjoke/setup-tectonic@v4` pinned to mutable tag

**File:** `.github/workflows/paper.yml:43-45`
**Issue:** The workflow uses `wtfjoke/setup-tectonic@v4`, a third-party community action
pinned to a **tag** (`v4`) rather than an immutable commit SHA. Tags in GitHub can be
force-pushed, meaning the action's code can change under the workflow at any time without
any diff appearing in `paper.yml`. This is a supply-chain integrity risk: a compromised or
re-tagged `v4` could execute arbitrary code in the CI context with access to `GITHUB_TOKEN`.

**Fix:** Pin to the full commit SHA for the `v4` release:

```yaml
# Before
- uses: wtfjoke/setup-tectonic@v4
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

# After — pin to immutable SHA (check https://github.com/wtfjoke/setup-tectonic/releases for current v4 SHA)
- uses: wtfjoke/setup-tectonic@<SHA>  # v4
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Info

### IN-01: No `make paper-check` target for local drift verification of `refs.bib`

**File:** `Makefile:39-50`
**Issue:** The `paper-coverage` target regenerates `coverage_counts.tex` (generate mode,
not check mode). There is no Makefile convenience target that runs
`python paper/code/assert_coverage.py --check` or the equivalent for `refs.bib`. A developer
preparing a PR cannot easily run the same drift gate that CI runs without knowing the exact
command-line flags. This is a discoverability gap — the CI gate and the local workflow
diverge ergonomically.

**Fix:** Add a `paper-check` (or `paper-gate`) phony target that runs both drift checks:

```makefile
.PHONY: paper-check
paper-check:  ## Run the CI drift gates locally (exits 1 if any file is stale)
	python paper/code/assert_coverage.py --check
	python paper/code/gen_refs_bib.py --check
```

This depends on WR-01 being fixed first (adding `--check` to `gen_refs_bib.py`).

---

_Reviewed: 2026-09-08T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
