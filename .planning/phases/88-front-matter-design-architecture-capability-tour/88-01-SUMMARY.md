---
phase: 88-front-matter-design-architecture-capability-tour
plan: "01"
subsystem: paper-pipeline
status: complete
tags: [snippets, listings, sklearn-macro, paper-scaffold, ci-wiring]
completed: 2026-09-09

dependency_graph:
  requires:
    - 87-04 (comparison table + comparison_evidence.md produced in prior phase)
    - paper/code/assert_coverage.py (extended; TRIAGE_VERDICTS import added)
    - paper/code/paper_utils.py (data_path injected into snippet exec namespace)
  provides:
    - paper/code/gen_snippets.py (generate + --check drift gate)
    - paper/snippets/represent.tex (tracer snippet: script -> exec -> .tex -> \input)
    - paper/coverage_counts.tex (7 macros incl. nsklearnestimators=28)
    - paper/paper.tex (listings preamble + 3 new \input lines)
    - paper/sections/abstract.tex (compileable stub)
    - paper/sections/advisor.tex (compileable stub)
    - paper/sections/conclusion.tex (compileable stub)
    - paper/sections/capabilities.tex (intro + \input{snippets/represent})
    - Makefile (paper-snippets target + paper-check snippet gate)
    - .github/workflows/paper.yml (maturin build + path-filter + drift gate)
  affects:
    - All Wave-2 plans (88-02 through 88-05) consume gen_snippets.py SNIPPETS list
    - Phase 90 GATE-02 validates snippet drift gate in final review

tech_stack:
  added:
    - LaTeX listings package (fdarsinput/fdarsoutput lstdefinestyle in paper.tex)
    - paper/code/gen_snippets.py (new executed-snippet harness)
    - paper/snippets/ directory (new generated-artifact location)
  patterns:
    - generate + --check drift gate (mirrors assert_coverage.py; proven Phase 86 pattern)
    - exec() in fresh namespace with contextlib.redirect_stdout capture
    - data_path injection into exec namespace (PIPE-01 no-data-copy lock)
    - maturin develop --release in paper.yml (mirrors ci.yml)

key_files:
  created:
    - paper/code/gen_snippets.py
    - paper/snippets/represent.tex
    - paper/sections/abstract.tex
    - paper/sections/advisor.tex
    - paper/sections/conclusion.tex
  modified:
    - paper/code/assert_coverage.py (nsklearnestimators macro added)
    - paper/coverage_counts.tex (7 macros, regenerated)
    - paper/paper.tex (listings preamble + UTF-8 literate map + 3 new \input lines)
    - paper/sections/capabilities.tex (intro + \input{snippets/represent})
    - Makefile (paper-snippets target + paper-check gate)
    - .github/workflows/paper.yml (maturin + scikit-learn + path-filter + drift gate)

decisions:
  - Use LaTeX listings (not minted): no -shell-escape, no pygments CI dependency, tectonic-friendly
  - Inject data_path into exec namespace so snippets use data_path("growth.csv") — robust to cwd, consistent with paper_utils convention (PIPE-01)
  - nsklearnestimators derived from TRIAGE_VERDICTS.values() == "PASS" at runtime — machine-derived, never hardcoded, distinct from ncoverage (Pitfall 6)
  - UTF-8 literate map in \lstset: en-dash and multiplication sign typeset cleanly from captured Fdata repr output
  - Widen paper.yml path filter to include python/fdars/** and src/** — API changes re-trigger snippet gate (highest-risk "stale snippets" concern)
  - Step order in paper.yml: maturin build -> all offline drift gates -> tectonic (fail-fast before expensive PDF compile)

metrics:
  duration_minutes: 22
  completed: 2026-09-09T06:02:46Z
  tasks_completed: 3
  commits: 4

actuals:
  tokens: 18500
  tasks: 3
  commits: 4
---

# Phase 88 Plan 01: Executed-Snippet Harness Tracer + Paper Scaffold Summary

gen_snippets.py proven end-to-end on the represent family (growth.csv -> Fdata -> repr captured); paper.tex loads listings with fdarsinput/fdarsoutput styles; \nsklearnestimators macro machine-derived from TRIAGE_VERDICTS; Makefile + paper.yml wired with maturin build and drift gate before tectonic.

## What Was Built

### Task 1: gen_snippets.py Harness (Tracer)

Created `paper/code/gen_snippets.py` — the executed-snippet harness for capability-tour LaTeX fragments. Architecture mirrors the proven `assert_coverage.py` pattern (generate / `--check` drift gate):

- `_run(source, extra_ns)`: execs source in a fresh dict namespace under `contextlib.redirect_stdout(io.StringIO())`, returns captured stdout verbatim.
- `_render(source, output)`: emits a static banner (no timestamp), a `lstlisting[style=fdarsinput]` source block, and (when non-empty) a `lstlisting[style=fdarsoutput]` output block.  Single trailing LF, UTF-8 — byte-stable across runs.
- `data_path` from `paper_utils` injected into every exec namespace so snippets use `data_path("growth.csv")` and are robust to cwd (PIPE-01 no-copy lock).
- SNIPPETS list seeded with `("represent", ...)` using the verified RESEARCH body.
- `--check` mode: regenerates each fragment in memory, compares byte-for-byte against the committed file, prints `DRIFT:` + path list to stderr and `sys.exit(1)` on mismatch.

Generated `paper/snippets/represent.tex`: contains source + captured `Fdata (1D) -- 93 obs x 31 points -- range [1.0, 18.0]` / `mean shape: (31,)` output. Byte-stable on re-run (verified by two consecutive runs + diff). Drift gate fires on mutation (verified by append test). No date or timestamp anywhere in the fragment.

### Task 2: \nsklearnestimators + Listings Preamble + Section Stubs

**assert_coverage.py** extended: `_derive_counts()` now imports `fdars.sklearn.TRIAGE_VERDICTS` and computes `sum(1 for v in TRIAGE_VERDICTS.values() if v == "PASS")` — machine-derived, never hardcoded. Raises `RuntimeError` with clear message if fdars not importable. Macro is distinct from `\ncoverage` (curated-paper-backed callables — coincidental 28-28 collision, Pitfall 6).

**coverage_counts.tex** regenerated with 7 sorted macros: `ncallables`, `ncoverage`, `ndocpapers`, `nfdata`, `npubliccallables`, `nsklearnestimators`, `nsubmodules`. Passes `--check`.

**paper.tex** preamble additions:
- `\usepackage{listings}` (after `adjustbox`, before `\begin{document}`)
- `\lstdefinestyle{fdarsinput}`: Python syntax, boxed, `\ttfamily\small`, `breaklines=true`
- `\lstdefinestyle{fdarsoutput}`: plain monospace, no frame
- `\lstset{literate=...}`: maps `--` -> `--`, `–` -> `--`, `×` -> `$\times$` for clean typesetting of Fdata repr characters
- `\begin{abstract}` now `\input{sections/abstract}`
- `\input{sections/advisor}` inserted after `\input{sections/comparison}`
- `\input{sections/conclusion}` inserted after `\input{sections/availability}`

**New stub files** (compileable, no placeholder language, no timestamps):
- `paper/sections/abstract.tex`: one-sentence abstract using `\nsubmodules` and `\nsklearnestimators` macros
- `paper/sections/advisor.tex`: `\section{Grounded AI Advisor and Scientific Provenance}` + one stub sentence
- `paper/sections/conclusion.tex`: `\section{Conclusion}` + one stub sentence citing `\nsubmodules`

**capabilities.tex** replaced placeholder with: intro paragraph citing `\npubliccallables`, `\nsubmodules`, `\ncoverage`, and `Table~\ref{tab:comparison}`; subsection "Data Representation"; `\input{snippets/represent}` tracer; marker comment for Plan 88-02 expansion.

### Task 3: Makefile + paper.yml Wiring

**Makefile**:
- `paper-snippets` target: `PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_snippets.py`
- Added `paper-snippets` to `.PHONY`
- `paper:` prerequisite list extended: `paper-figures paper-coverage paper-refs paper-snippets`
- `paper-check:` appended: `PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_snippets.py --check`

**paper.yml**:
- Added `dtolnay/rust-toolchain@stable` + `Swatinem/rust-cache@v2` steps
- Added "Create venv and build fdars (maturin develop)" step: `python -m venv .venv; pip install maturin numpy pandas scipy scikit-learn matplotlib; maturin develop --release`
- All existing offline steps updated to run under `.venv` activation for consistent fdars availability (assert_coverage now imports fdars.sklearn)
- Added "Assert snippets not stale (MANU-05 / GATE-02 drift gate)" step: `PYTHONPATH=scripts:paper/code python paper/code/gen_snippets.py --check`
- Step order preserved: build -> figures -> assert_coverage -> refs -> comparison -> **snippets** -> tectonic
- Path filter widened (both push + pull_request): added `python/fdars/**` and `src/**` so an API change in the Rust/Python source re-triggers the snippet gate (Pitfall 5)
- YAML validates via `yaml.safe_load`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Drift test left stale committed represent.tex**
- **Found during:** Task 1 post-commit cleanup
- **Issue:** The plan's second verification block (`SNIPPET_DRIFT_GATE_FIRES`) appended `% drift` to represent.tex and restored from backup. However the first Task 1 commit was made BEFORE the mutation test, so the committed file was clean. A subsequent re-run of `gen_snippets.py` in overall verification revealed that HEAD had the `% drift` line from a prior run of the generate mode that was committed.
- **Fix:** Re-ran `gen_snippets.py` to regenerate the clean version and committed the correction.
- **Files modified:** `paper/snippets/represent.tex`
- **Commit:** `3d2315c`

None other — plan executed as written.

## Tracer Feedback Gate

The tracer (Task 1) proves the full path:

1. `gen_snippets.py` (generate mode) → runs `fdars.Fdata(growth.values.T.astype(float64), ...)`, captures `repr` + `mean shape`, writes `paper/snippets/represent.tex`
2. `represent.tex` contains the static banner, `fdarsinput` source block, `fdarsoutput` captured-output block — no timestamp, no raw floats
3. Re-run produces byte-identical file (determinism gate passes)
4. `--check` mode exits 0 on clean commit, exits 1 on mutated file (drift gate fires)
5. `capabilities.tex` `\input{snippets/represent}` resolves (file exists)
6. `make paper-check` includes the drift gate as last step
7. `paper.yml` builds fdars via maturin, runs the gate before tectonic

Wave-2 plans (88-02) can safely expand `SNIPPETS` in `gen_snippets.py` and add `\input` lines to `capabilities.tex` with confidence the harness mechanism is proven.

## Known Stubs

| File | Description |
|------|-------------|
| `paper/sections/abstract.tex` | One-sentence placeholder; expanded in Phase 88 Plan 03 |
| `paper/sections/advisor.tex` | Section title + one sentence; expanded in Phase 88 Plan 04 |
| `paper/sections/conclusion.tex` | Section title + one sentence; expanded in Phase 88 Plan 05 |

These stubs compile cleanly (no `\today`, no "Placeholder" language) and are intentional scaffolding for Wave-2 prose plans. They do not block the plan's goal (harness + tracer + scaffold) from being achieved.

## Self-Check: PASSED

- `paper/code/gen_snippets.py` exists: FOUND
- `paper/snippets/represent.tex` exists: FOUND
- `paper/sections/abstract.tex` exists: FOUND
- `paper/sections/advisor.tex` exists: FOUND
- `paper/sections/conclusion.tex` exists: FOUND
- `fa8bdde` (gen_snippets.py + represent.tex): FOUND
- `b94cef8` (assert_coverage + paper.tex + stubs + capabilities): FOUND
- `8f10864` (Makefile + paper.yml): FOUND
- `3d2315c` (represent.tex drift artifact fix): FOUND
- `gen_snippets.py --check` exits 0 on clean repo: VERIFIED
- `assert_coverage.py --check` exits 0: VERIFIED
- `git diff paper/` empty after regeneration: VERIFIED
