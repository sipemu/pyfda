---
phase: 88-front-matter-design-architecture-capability-tour
fixed_at: 2026-09-09T05:30:00Z
review_path: .planning/phases/88-front-matter-design-architecture-capability-tour/88-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 11
skipped: 0
status: all_fixed
---

# Phase 88: Code Review Fix Report

**Fixed at:** 2026-09-09T05:30:00Z
**Source review:** `.planning/phases/88-front-matter-design-architecture-capability-tour/88-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 11
- Fixed: 11
- Skipped: 0

## Fixed Issues

### CR-01: Eight dangling citation keys in capabilities.tex

**Files modified:** `paper/sections/capabilities.tex`, `paper/refs_manual.bib`, `paper/paper.tex`
**Commit:** 54d6bad
**Applied fix:**
- Renamed 6 key mismatches in capabilities.tex to match existing refs.bib entries:
  `ramsay2005functional` → `ramsay_silverman_2005`,
  `fraiman2001trimmed` → `fraiman_muniz_2001`,
  `dai2019directional` → `dai_genton_2019` (already present — sentence is about directional outlyingness specifically),
  `yao2005functional` → `yao_muller_wang_2005` (both occurrences, lines 57 and 87),
  `srivastava2011registration` → `srivastava_et_al_2011`,
  `petersen2019frechet` → `petersen_muller_2019`.
- `tarpey2003clustering` → substituted `bouveyron_jacques_2011` (canonical model-based functional clustering ref, contextually appropriate).
- `febrero2012statistical` → created `paper/refs_manual.bib` with `@article{febrerobande_fdausc_2012}` (real entry, accurate venue/year); updated `paper/paper.tex` bibliography from `\bibliography{refs}` to `\bibliography{refs,refs_manual}`.

**Dangling-citation check result:** PASS — 0 dangling keys. All 20 cite keys used across `paper/sections/*.tex` are defined in refs.bib or refs_manual.bib.

---

### CR-02: scikit-fda mis-cited with Ramsay & Silverman 2005 key

**Files modified:** `paper/sections/intro.tex`, `paper/refs_manual.bib`, `paper/paper.tex`
**Commit:** 54d6bad
**Applied fix:** Changed `\citep{ramsay_silverman_2005}` on the scikit-fda sentence (intro.tex:11) to `\citep{ramoscarreno_scikitfda_2024}`. Added `@article{ramoscarreno_scikitfda_2024}` to `paper/refs_manual.bib` (Ramos-Carreño et al. 2024, Journal of Statistical Software vol 109).

---

### CR-03: design.tex falsely claims PyReadonlyArray releases the GIL

**Files modified:** `paper/sections/design.tex`
**Commit:** 54d6bad
**Applied fix:** Removed the false GIL-release claim "release the GIL for the duration of the Rust call". Replaced with accurate description: "PyReadonlyArray wrappers, which hold a read-only view of the caller's array for the duration of the Rust call without an extra data copy, and prevent concurrent Python mutation of the array during Rust execution." No `py.allow_threads()` calls exist in `src/`; the GIL is held throughout.

---

### WR-01: Hardcoded integer "13" for EXCLUDED_METHODS count in design.tex

**Files modified:** `paper/code/assert_coverage.py`, `paper/coverage_counts.tex`, `paper/sections/design.tex`
**Commit:** faca110
**Applied fix:**
- Added `EXCLUDED_METHODS` to the import from `fdars.sklearn` in assert_coverage.py.
- Added `"nexcludedmethods": len(EXCLUDED_METHODS)` to `_derive_counts()` return dict.
- Updated module docstring to document the new `\nexcludedmethods` macro.
- Regenerated `paper/coverage_counts.tex` — now includes `\newcommand{\nexcludedmethods}{13}`.
- Replaced `13 methods` in design.tex:143 with `\nexcludedmethods{} methods`.
- `assert_coverage.py --check`: OK (no drift).

---

### WR-02: Dead "Regenerate refs.bib" step in paper.yml

**Files modified:** `.github/workflows/paper.yml`
**Commit:** e1a5201
**Applied fix:** Removed the "Regenerate refs.bib (PIPE-04)" step (lines 61-64). The preceding `gen_refs_bib.py --check` gate halts CI if refs.bib is stale, making the regenerate step a perpetual no-op. The `--check` gate was preserved.

---

### WR-03: assert_coverage.py `_OUT.write_text()` missing `encoding="utf-8"`

**Files modified:** `paper/code/assert_coverage.py`
**Commit:** faca110
**Applied fix:** Added `encoding="utf-8"` to both `_OUT.write_text(content, encoding="utf-8")` (generate mode, line 156) and `_OUT.read_text(encoding="utf-8")` (check mode, line 147). Mirrors the pattern already used correctly in gen_snippets.py.

---

### WR-04: design.tex module map omits `seasonal` and `multi_fdata`

**Files modified:** `paper/sections/design.tex`
**Commit:** d889fd5
**Applied fix:**
- Added `seasonal` (seasonal decomposition for functional time series) to the "Functional time series and seasonal decomposition" item.
- Added `multi_fdata` (PyMultiFunData opaque container for multivariate functional data) to the "Representation, basis and smoothing" item.
- Both are confirmed registered in `src/lib.rs` and counted in `\nsubmodules{30}`.

---

### WR-05: gen_snippets.py compile() filename is `"<snippet>"` for all snippets

**Files modified:** `paper/code/gen_snippets.py`
**Commit:** 1851a6a
**Applied fix:** Added `name: str = "<snippet>"` parameter to `_run()`. Changed `compile(..., "<snippet>", "exec")` to `compile(..., f"<snippet:{name}>", "exec")`. Updated `main()` call site to `_run(source, name=name, extra_ns=_EXTRA_NS)`. CI tracebacks now identify which snippet failed.

---

### WR-06: gen_snippets.py `_SNIPPETS_DIR` resolution undocumented

**Files modified:** `paper/code/gen_snippets.py`
**Commit:** 1851a6a
**Applied fix:** Added one-line comment above `_SNIPPETS_DIR`: "Path is resolved relative to `__file__`, not CWD — safe to invoke from any directory."

---

### IN-01: "Rust-accelerated" language in abstract/conclusion

**Files modified:** `paper/sections/conclusion.tex`, `paper/sections/abstract.tex`
**Commit:** 1146a83
**Applied fix:**
- conclusion.tex: "Rust-accelerated" → "Rust-backed".
- abstract.tex: "accelerated through a Rust core" → "implemented through a Rust core".
Both changes avoid implying benchmark claims while accurately describing the architecture.

---

### IN-02: `\checkmark` needs amssymb (paper.tex)

**Files modified:** `paper/paper.tex`
**Commit:** 1146a83
**Applied fix:** Added `\usepackage{amssymb}` to paper.tex preamble after `\usepackage{amsmath}`. Makes the `\checkmark` dependency explicit (used in advisor.tex and comparison_table.tex) rather than relying on tectonic auto-resolution.

---

## Post-fix Verification

Verification ran in the main checkout (workflow.use_worktrees = false).

1. **Dangling citation check:** PASS — 0 dangling keys. 20 unique keys used across `paper/sections/*.tex`; all 20 defined in refs.bib + refs_manual.bib.

2. **assert_coverage.py --check:** PASS — exits 0, no drift. New `\nexcludedmethods{13}` macro included in coverage_counts.tex.

3. **gen_snippets.py --check:** PASS — exits 0, no drift.

4. **git diff paper/figures/ paper/coverage_counts.tex paper/refs.bib paper/snippets/:** Clean — no uncommitted changes to generated artifacts.

5. **Hardcoded count integers in prose:** None found — grep for raw count integers (13, 28, 30, 409, 437) in `paper/sections/*.tex` returns no unprotected hits.

6. **SyntaxWarning check:** No SyntaxWarnings from assert_coverage.py or gen_snippets.py.

---

_Fixed: 2026-09-09T05:30:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
