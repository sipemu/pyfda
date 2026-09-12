---
phase: 85-manuscript-scaffold-pipeline-infrastructure
reviewed: 2026-09-08T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - paper/code/paper_utils.py
  - paper/code/gen_figures.py
  - Makefile
  - paper/paper.tex
  - paper/refs.bib
  - CITATION.cff
  - paper/sections/intro.tex
  - paper/sections/design.tex
  - paper/sections/represent.tex
  - paper/sections/capabilities.tex
  - paper/sections/comparison.tex
  - paper/sections/casestudies.tex
  - paper/sections/availability.tex
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 85: Code Review Report

**Reviewed:** 2026-09-08T00:00:00Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Reviewed the Phase 85 paper pipeline infrastructure: two Python helpers (`paper_utils.py`, `gen_figures.py`), the Makefile paper targets, the LaTeX scaffold (`paper.tex` + seven section stubs), the stub bibliography (`refs.bib`), and `CITATION.cff`.

The core pipeline mechanics are sound. `data_path()`'s traversal guard correctly blocks absolute paths and `..` components; the matplotlib PDF `metadata={"CreationDate": None}` suppression is confirmed correct against the matplotlib 3.x source (line 162 of `backend_pdf.py` strips `None`-valued keys). The `_SCRIPTS` path calculation (`parent × 3` from `paper/code/paper_utils.py` to repo root) is verified correct. The Makefile `PYTHONPATH` override on the `paper-figures` recipe correctly sets `scripts:paper/code` for that command.

Two warnings and one info item require attention before later phases build on this scaffold.

## Warnings

### WR-01: `CITATION.cff` preferred-citation missing `journal` field

**File:** `CITATION.cff:26-37`
**Issue:** The `preferred-citation` block declares `type: article` but omits the `journal` field. The CFF 1.2.0 schema does not make `journal` a hard-required field, so `cffconvert` will not fail validation, but GitHub's "Cite this repository" feature and Zenodo's auto-import will both render the citation without a journal, producing an incomplete bibliographic record. Once the arXiv preprint is submitted and has a DOI/URL, this stub will need both `journal: arXiv` (or the venue name) and the `identifiers` entry updated from the repository URL to the actual arXiv ID. If this field is forgotten at submission time, the citation record on GitHub will be malformed indefinitely.

**Fix:**
```yaml
preferred-citation:
  type: article
  title: "fdars: Functional Data Analysis in Rust with Python Bindings"
  authors:
    - family-names: "Müller"
      given-names: "Simon"
      email: "sm@data-zoo.de"
  year: 2026
  journal: "arXiv preprint"          # add: update to venue at submission
  identifiers:
    - type: url
      value: "https://github.com/sipemu/pyfda"
      description: "Repository (arXiv URL added at submission)"
```
At minimum, add a `# TODO: add journal and arXiv URL at submission` comment so the field is not overlooked during Phase 90 / release tagging.

---

### WR-02: `data_path()` traversal guard has no containment check after resolution

**File:** `paper/code/paper_utils.py:68-78`
**Issue:** The guard checks `p.is_absolute() or ".." in p.parts`, which correctly blocks the documented threat (T-85-01: direct `..` traversal). However, it permits subdirectory-style names such as `"subdir/file.csv"`, resolving to `docs/data/subdir/file.csv`. This stays within `docs/data/` for real paths and is therefore safe in practice, but the function contract (`name` described as "Filename relative to `docs/data/`") implies a flat filename, and the guard does not enforce that the resolved path actually remains inside `docs/data/`. A symlink planted inside `docs/data/` could redirect a permitted name to an arbitrary location without triggering the current check.

The risk is low in a controlled repository environment, but the docstring says "Must not contain `..` or be an absolute path" — a caller reading only the docstring would not know that `"../../../etc/passwd"` is blocked but `"subdir/../../etc/passwd"` resolves correctly because `..` appears in `Path("subdir/../../etc/passwd").parts`. (It does — tested.) The residual concern is symlinks, not `..`.

**Fix:** Add a `Path.is_relative_to()` containment assertion after resolution (Python 3.9+):
```python
root = Path(__file__).resolve().parent.parent.parent
data_dir = root / "docs" / "data"
resolved = (data_dir / name).resolve()
if not resolved.is_relative_to(data_dir):
    raise ValueError(
        f"data_path: resolved path escapes docs/data/: {resolved}"
    )
if not resolved.exists():
    raise FileNotFoundError(f"dataset not found: {resolved}")
return resolved
```
This replaces the `p.is_absolute() or ".." in p.parts` pre-check (which can be dropped, as `resolve()` + `is_relative_to()` subsumes it) and covers symlink escapes as well.

---

## Info

### IN-01: `gen_figures.py` uses legacy `np.random.seed()` global RNG

**File:** `paper/code/gen_figures.py:33`
**Issue:** `np.random.seed(20260908)` mutates NumPy's global legacy RNG. While this is deterministic and works, NumPy has deprecated the global seed API in favour of `np.random.default_rng()` since NumPy 1.17. If a future figure function calls any library that also seeds the global RNG before or after `_smoke()`, the seed will be contaminated and determinism of downstream draws within the same process is not guaranteed. This is an INFO item because `main()` currently calls only `_smoke()`, but it is a latent hazard as Phase 88/89 append additional figure functions.

**Fix:** Switch to the new Generator API:
```python
def _smoke() -> None:
    rng = np.random.default_rng(20260908)
    y = rng.standard_normal(50).cumsum()
    x = np.arange(len(y))
    ...
```
Each figure function gets its own `rng = np.random.default_rng(<seed>)` instance, making draws independent of global state and of each other's execution order.

---

_Reviewed: 2026-09-08T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
