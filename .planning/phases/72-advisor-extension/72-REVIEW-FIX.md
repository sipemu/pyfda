---
phase: 72-advisor-extension
fixed_at: 2026-09-04T00:00:00Z
review_path: .planning/phases/72-advisor-extension/72-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 72: Code Review Fix Report

**Fixed at:** 2026-09-04
**Source review:** .planning/phases/72-advisor-extension/72-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (CR-01, WR-01, WR-02, WR-03; IN-01/IN-02 excluded per fix_scope=critical_warning)
- Fixed: 4
- Skipped: 0

## Fixed Issues

### CR-01: Shapelet classifier spuriously triggers `has_elastic_multinomial = True`

**Files modified:** `python/fdars/advisor/aspects/classification.py`, `tests/test_advisor_group_b.py`
**Commit:** 7b265c2
**Applied fix:** Tightened the elastic_multinomial discriminator from
`"train_accuracy" in raw` to `"train_accuracy" in raw and "n_shapelets" not in raw`.
The shapelet coercion dict (built in `__init__.py` before dispatch) carries
`"train_accuracy"`, causing `has_elastic_multinomial=True` to fire for every
shapelet classifier result — a wrong method-type signal to the LLM that also
incorrectly computed and emitted `train_error_rate` on the shapelet path.
Added two new regression tests: `test_shapelet_has_elastic_multinomial_false`
(live shapelet fixture) and `test_shapelet_and_elastic_mutually_exclusive_synthetic`
(synthetic coercion dict) asserting the two discriminators are mutually exclusive.

### WR-01: `spm.py` mfpca input populates `ncomp` and `eigenvalues` from mfpca eigenvalues

**Files modified:** `python/fdars/advisor/aspects/spm.py`, `tests/test_advisor_spm_v11.py`
**Commit:** e7d85dd
**Applied fix:** Moved `has_mfpca` computation to before the spm_phase1 eigenvalue
blocks so both can be gated on `not has_mfpca`. The spm_phase1 sentinel fields
`diag["ncomp"]`, `diag["eigenvalues"]`, and `diag["variance_explained_cumulative"]`
are now `None` for mfpca input; the mfpca-specific keys (`mfpca_ncomp`,
`mfpca_eigenvalues`, `mfpca_variance_explained_cumulative`) carry the real values
unchanged. The duplicate `has_mfpca = ...` assignment near the mfpca branch was
replaced with a comment noting the early computation. Added
`test_mfpca_ncomp_eigenvalues_spm_phase1_fields_none` asserting all three
spm_phase1 sentinel fields are `None` for mfpca input while mfpca-specific fields
remain populated.

### WR-02: `fts.py` acf/dpca branches access keys without guards

**Files modified:** `python/fdars/advisor/aspects/fts.py`
**Commit:** ed9951c
**Applied fix:** Two key accesses violated the ASVS V5 guarded-access contract
stated in the module docstring:
- `raw["lags"]` (acf branch, line 104): replaced with
  `np.asarray(raw["lags"]) if "lags" in raw else np.array([])`
- `raw["eigenvalues"]` (dpca branch, line 130): replaced with
  `raw.get("eigenvalues")` and an explicit `None` branch for
  `diag["dpca_eigenvalues"]`, consistent with every other key access in the file.
All existing 37 fts tests continue to pass.

### WR-03: `server.py` and `advisor/__init__.py` docstrings list 14 instead of 16 methods

**Files modified:** `python/fdars/mcp/server.py`, `python/fdars/advisor/__init__.py`
**Commit:** f37f0e7
**Applied fix:** Updated two docstrings:
- `server.py:117`: "fourteen" → "sixteen"; added `'fts'` and `'frechet'` to method list.
- `__init__.py:106-108`: added `"fts"` and `"frechet"` to the method parameter
  type annotation string.
Dispatch code and frozensets were already correct; only the docstring text was stale.

## Skipped Issues

None — all four in-scope findings were fixed.

---

**Verification:** All fixes verified via re-read (Tier 1) and pytest (Tier 2).
Tests ran in the main checkout (workflow.use_worktrees=false).

Full suite result: **5650 passed, 10 skipped, 120 warnings** (no failures).
Targeted suite (group_b + spm_v11 + fts + guard_sync): **125 passed**.

---

_Fixed: 2026-09-04_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
