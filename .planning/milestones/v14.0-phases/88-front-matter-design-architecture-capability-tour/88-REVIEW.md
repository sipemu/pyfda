---
phase: 88-front-matter-design-architecture-capability-tour
reviewed: 2026-09-09T04:30:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - paper/code/gen_snippets.py
  - paper/code/assert_coverage.py
  - .github/workflows/paper.yml
  - Makefile
  - paper/sections/abstract.tex
  - paper/sections/intro.tex
  - paper/sections/design.tex
  - paper/sections/represent.tex
  - paper/sections/advisor.tex
  - paper/sections/capabilities.tex
  - paper/sections/availability.tex
  - paper/sections/conclusion.tex
findings:
  critical: 3
  warning: 6
  info: 2
  total: 11
status: issues_found
---

# Phase 88: Code Review Report

**Reviewed:** 2026-09-09T04:30:00Z
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Phase 88 wrote the paper's prose sections (abstract, intro, design, represent, advisor, capabilities, availability, conclusion) and the executed-snippet harness (`gen_snippets.py`) plus the updated `assert_coverage.py` with the new `\nsklearnestimators` macro. The harness design is generally sound: determinism rules are documented and followed (static banner, seeds, shape-not-repr output, LF+UTF-8). The macro derivation in `assert_coverage.py` is correct and the distinction between `\nsklearnestimators` and `\ncoverage` is clearly documented.

The most serious problems are peer-review-blocking: eight citation keys used in `capabilities.tex` do not exist in `refs.bib` — six are key-name mismatches with entries that do exist (same paper, different key), and two are genuinely absent entries (Tarpey 2003 functional k-means; Febrero-Bande et al. 2012 tolerance bands). A second BLOCKER is in `intro.tex`, which cites `scikit-fda 0.10.1` using the Ramsay & Silverman 2005 book key instead of scikit-fda's own software paper. A third BLOCKER is in `design.tex`, which falsely claims that `PyReadonlyArray` wrappers release the GIL — the codebase contains no `py.allow_threads()` calls, so the GIL is held for the full duration of every Rust binding call.

---

## Critical Issues

### CR-01: Eight dangling citation keys in capabilities.tex — PDF will produce [?] citations

**File:** `paper/sections/capabilities.tex:23,41,45,57,64,87,117,132,141`
**Issue:** Eight `\citep{}` keys used in `capabilities.tex` are undefined in `paper/refs.bib`. When compiled, each produces an `[?]` marker and a BibTeX warning. Six are key-name mismatches — the paper cites using one convention but `refs.bib` defines the same work under a different key; two are genuinely missing entries.

**Key-name mismatches (same work exists in bib under a different key):**

| Line | Used key (undefined) | Correct key in refs.bib |
|------|---------------------|------------------------|
| 23 | `ramsay2005functional` | `ramsay_silverman_2005` |
| 41 | `fraiman2001trimmed` | `fraiman_muniz_2001` |
| 45 | `dai2019directional` | `dai_genton_2019` |
| 57, 87 | `yao2005functional` | `yao_muller_wang_2005` |
| 141 | `srivastava2011registration` | `srivastava_et_al_2011` |
| 132 | `petersen2019frechet` | `petersen_muller_2019` |

**Genuinely missing from refs.bib (no equivalent entry):**

| Line | Key | Paper needed |
|------|-----|-------------|
| 64 | `tarpey2003clustering` | Tarpey, T. & Kinateder, K.K.J. (2003). Clustering Functional Data. *Journal of Classification* 20, 93–114. |
| 117 | `febrero2012statistical` | Febrero-Bande, M. et al. (2012). Statistical computing in functional data analysis: The R package fda.usc. *Journal of Statistical Software* 51(4). |

**Fix:** For key mismatches, rename the citation keys in `capabilities.tex` to match the existing `refs.bib` keys listed above. For the two missing entries, add `@misc{tarpey2003clustering, ...}` and `@misc{febrero2012statistical, ...}` to `refs.bib` and re-run `gen_refs_bib.py` if it manages the bib file, or add them manually if `refs.bib` is hand-maintained for these entries.

---

### CR-02: scikit-fda cited with Ramsay & Silverman 2005 book key in intro.tex

**File:** `paper/sections/intro.tex:11`
**Issue:** The sentence introducing scikit-fda uses `\citep{ramsay_silverman_2005}`, which resolves to *Functional Data Analysis* (Ramsay & Silverman, 2005) — the FDA textbook. A peer reviewer will immediately flag this: scikit-fda should be cited via its own software paper (Ramos-Carreño et al., 2024, *Journal of Statistical Software*). Citing the textbook as the reference for a competing software package is factually wrong and will read as an error in the manuscript.

```tex
% Current (wrong):
\texttt{scikit-fda}~0.10.1 \citep{ramsay_silverman_2005} is the strongest

% Fix — add entry to refs.bib and cite it:
\texttt{scikit-fda}~0.10.1 \citep{ramos_carreno_2024} is the strongest
```

**Fix:** Add a `@misc{ramos_carreno_2024, ...}` entry to `refs.bib` for: Ramos-Carreño, C., Suárez-García, A., et al. (2024). "scikit-fda: A Python Package for Functional Data Analysis." *Journal of Statistical Software* 109(2), and update `intro.tex` line 11 to `\citep{ramos_carreno_2024}`.

---

### CR-03: design.tex falsely claims PyReadonlyArray releases the GIL

**File:** `paper/sections/design.tex:22-24`
**Issue:** The text states that `PyReadonlyArray` wrappers "hold a read-only view of the caller's array without copying it and **release the GIL for the duration of the Rust call**." This is factually incorrect. A grep of the entire `src/` directory finds zero calls to `py.allow_threads()`, `Python::allow_threads()`, or any equivalent GIL-release primitive. In PyO3 0.28, `#[pyfunction]` holds the GIL for the full duration of the call; `PyReadonlyArray` does not release it — it merely ensures the array data is not mutated from Python while Rust holds the reference. The GIL is held through every binding call in this codebase.

This claim will be questioned in peer review, particularly because the paper also claims the Rust core uses Rayon for parallelism with `features = ["parallel"]`; readers will assume GIL-free parallel execution but the GIL prevents multi-threaded Python code from benefiting.

```rust
// Evidence: no allow_threads anywhere in src/
// $ grep -rn "allow_threads" src/  → (no output)
```

**Fix:** Replace the GIL-release claim with an accurate description:
```tex
% Replace lines 22-24 with:
\texttt{PyReadonlyArray} wrappers, which hold a read-only view of the caller's
array for the duration of the Rust call without an extra data copy, and prevent
concurrent Python mutation of the array during Rust execution.
```

Note: if GIL release is desirable, add `py.allow_threads(|| { ... })` wrappers around the core computation in each binding function. Until that is done, the claim must be removed.

---

## Warnings

### WR-01: Hardcoded integer "13" for EXCLUDED_METHODS count in design.tex

**File:** `paper/sections/design.tex:143`
**Issue:** The text says "13 methods, listed in `fdars.sklearn.EXCLUDED_METHODS`". This integer is hardcoded in prose. `EXCLUDED_METHODS` currently has 13 entries (verified), so it matches today, but if entries are added or removed in a future phase, the prose will silently diverge. All other counts in the paper use machine-derived macros (`\nsubmodules`, `\npubliccallables`, `\nsklearnestimators`). This count should either use a macro or be documented as a fixed architectural decision.

**Fix (option A — add a macro to assert_coverage.py):**
```python
# In _derive_counts():
from fdars.sklearn import EXCLUDED_METHODS
"nexcludedmethods": len(EXCLUDED_METHODS),
```
Then use `\nexcludedmethods{}` in design.tex line 143.

**Fix (option B — phrase it invariantly):** Replace "13 methods" with "a set of methods" or "methods whose interfaces preclude the stateless fit/transform contract" to avoid any specific count.

---

### WR-02: Dead workflow step — "Regenerate refs.bib" in paper.yml always a no-op

**File:** `.github/workflows/paper.yml:61-64`
**Issue:** The workflow runs `gen_refs_bib.py --check` (step at line 56-59), which exits 1 if `refs.bib` is stale, halting the pipeline. The immediately following "Regenerate refs.bib" step (line 61-64) can only execute if `--check` passed — meaning `refs.bib` is already current, so regeneration is always a no-op. This step never has any effect in CI and will mislead future maintainers into thinking CI regenerates and commits `refs.bib`.

**Fix:** Remove the "Regenerate refs.bib" step from `paper.yml`. Developers regenerate locally via `make paper-refs` before committing.

---

### WR-03: assert_coverage.py write_text missing encoding parameter (locale portability)

**File:** `paper/code/assert_coverage.py:156`
**Issue:** `_OUT.write_text(content)` has no `encoding="utf-8"` argument. The `_render` function emits the Unicode en-dash in the comment line ("— do not edit") and potentially Unicode characters from author names in future. On Windows systems or CI environments where `PYTHONUTF8=1` is not set, `write_text` uses the locale encoding. This can cause a `UnicodeEncodeError` or a silent encoding mismatch between generate and `--check` modes (one writing with locale encoding, the other reading with `utf-8`).

Compare: `gen_snippets.py:375` correctly uses `target.write_text(content, encoding="utf-8")` and `target.read_text(encoding="utf-8")`.

```python
# Fix: assert_coverage.py line 156
_OUT.write_text(content, encoding="utf-8")
# And line 147:
committed = _OUT.read_text(encoding="utf-8")
```

---

### WR-04: modules `seasonal` and `multi_fdata` omitted from design.tex Module Map

**File:** `paper/sections/design.tex:50-105`
**Issue:** The Module Map `\begin{description}` block enumerates 11 method families but omits two submodules that are registered in `lib.rs` and listed in `__init__.py`: `seasonal` (seasonal decomposition for functional time series) and `multi_fdata` (the `PyMultiFunData` opaque container for multivariate functional data). The macro `\nsubmodules{}` (derived from `_capability_map.json`) counts 30 public modules including these two, so the prose module map is understated relative to the claimed count.

**Fix:** Add a bullet or item for `seasonal` under the Functional time series description, and add `multi_fdata` under a Representation entry or create a brief item for multivariate functional data containers.

---

### WR-05: _run() in gen_snippets.py provides no per-snippet error attribution

**File:** `paper/code/gen_snippets.py:51-73`
**Issue:** When `exec()` raises an exception, the traceback filename is `<snippet>` (from `compile(..., "<snippet>", "exec")`) with no indication of which snippet name failed. In a 14-snippet batch, a failure in snippet 7 of 14 produces a traceback that says `File "<snippet>", line N` with no "which snippet?" context. This makes CI failures harder to diagnose.

**Fix:** Wrap the `exec` call in `_run()` to re-raise with context, or pass the snippet name to `_run()` and use it as the compile filename:
```python
def _run(source: str, name: str = "<snippet>", extra_ns: dict | None = None) -> str:
    ...
    exec(compile(textwrap.dedent(source), name, "exec"), ns)
```
Then call `_run(source, name=name, extra_ns=_EXTRA_NS)` in `main()`.

---

### WR-06: gen_snippets.py SNIPPETS_DIR path silently resolves relative to gen_snippets.py, not CWD

**File:** `paper/code/gen_snippets.py:47`
**Issue:** `_SNIPPETS_DIR = Path(__file__).resolve().parent.parent / "snippets"` resolves to `paper/snippets/`. The tectonic compile command in `paper.yml` is `tectonic paper/paper.tex`, which runs from the repo root. Tectonic sets its working directory to the directory of the main `.tex` file (`paper/`). The `\input{snippets/represent}` in `capabilities.tex` therefore resolves to `paper/snippets/represent.tex` — which is correct.

However, there is a latent risk: if `gen_snippets.py` is ever invoked from a working directory other than the repo root, `Path(__file__)` is still correct (it is absolute), so the output path is stable. This is not a bug as written, but worth noting that the PYTHONPATH usage comment at the top of the file claims `PYTHONPATH=scripts:paper/code python paper/code/gen_snippets.py` — meaning the invocation is from the repo root. The `Makefile` and CI both follow this convention correctly.

**Fix:** No code change needed, but document in the module docstring that `_SNIPPETS_DIR` is resolved relative to the script, not CWD, so the script is safe to invoke from any directory.

---

## Info

### IN-01: "Rust-accelerated" label in abstract/conclusion is qualitative — appropriate but unverified

**File:** `paper/sections/abstract.tex:9`, `paper/sections/conclusion.tex:5`
**Issue:** The abstract and conclusion describe fdars as "Rust-accelerated" without any supporting measurement. The milestone design explicitly forbids benchmarks. The qualifier is qualitative (architecture-level statement) and the intro explicitly says "We make no performance claims here." The usage is defensible but a reviewer may ask for a parenthetical qualification (e.g., "leveraging Rust for compute-intensive operations").

**Fix (optional):** Consider replacing "Rust-accelerated" with "Rust-backed" or "powered by a Rust computation core" in abstract and conclusion to emphasize architecture over implied speedup.

---

### IN-02: paper.tex does not explicitly declare \usepackage{amssymb}; \checkmark usage relies on tectonic auto-resolution

**File:** `paper/paper.tex:1-77`, `paper/sections/advisor.tex:107`
**Issue:** `\checkmark{}` is used in text mode in `advisor.tex:107`. The `amsmath` package (loaded in `paper.tex`) does not define `\checkmark` — it is defined in `amssymb`. `comparison_table.tex` uses `$\checkmark$` in math mode. Both forms require `amssymb`. The `paper.tex` preamble does not include `\usepackage{amssymb}`. Tectonic auto-fetches TeX Live packages, and since `comparison_table.tex` was introduced in Phase 87 and presumably compiled successfully (Phase 87 was archived), tectonic must be resolving `\checkmark` from its pre-bundled fonts. However the dependency is implicit — if compilation moves to a different TeX engine or a constrained tectonic bundle, this will break.

**Fix:** Add `\usepackage{amssymb}` to `paper/paper.tex` after the `\usepackage{amsmath}` line to make the dependency explicit.

---

_Reviewed: 2026-09-09T04:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
