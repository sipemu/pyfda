---
phase: 85-manuscript-scaffold-pipeline-infrastructure
plan: "01"
subsystem: paper-pipeline
status: complete
tags:
  - paper
  - reproducible-figures
  - determinism
  - PIPE-01
  - PIPE-02
dependencies:
  requires:
    - scripts/docs_fig.py
    - docs/data/
  provides:
    - paper/code/paper_utils.py
    - paper/code/gen_figures.py
    - paper/figures/smoke.pdf
    - Makefile paper/paper-figures targets
  affects:
    - paper/
tech_stack:
  added:
    - paper/code/ (new Python figure pipeline)
    - paper/figures/ (committed deterministic PDF output)
  patterns:
    - docs_fig.py reuse (import, not reimplement)
    - data_path() resolving docs/data/ (zero duplication)
    - save_figure() with suppressed CreationDate (PIPE-02)
key_files:
  created:
    - paper/code/paper_utils.py
    - paper/code/gen_figures.py
    - paper/code/.gitkeep
    - paper/figures/smoke.pdf
  modified:
    - Makefile
decisions:
  - "Import fig/FDARS_COLORS from docs_fig (not reimplemented) — reuses established Agg+rcParams block via import side-effect"
  - "data_path() resolves paper/code/ as three levels below repo root (parent×3), matching docs_data.py which is two levels from scripts/"
  - "save_figure() passes metadata={\"CreationDate\": None} — suppresses PDF timestamp so git diff paper/figures/ is empty on re-run (PIPE-02, T-85-02)"
  - "np.random.seed(20260908) called at top of _smoke() before any stochastic draw — per-figure seeding per PIPE-02"
  - "Makefile paper targets use plain `python` (same convention as existing docs targets) — user activates .venv before make"
  - "paper: depends only on paper-figures (no tectonic/pdflatex — PDF compile is CI-only, GATE-01 Phase 86)"
metrics:
  duration_minutes: 2
  completed_date: "2026-09-08"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
actuals:
  tokens: 6000
  tasks: 3
  commits: 3
requirements:
  - PIPE-01
  - PIPE-02
---

# Phase 85 Plan 01: Manuscript Scaffold + Pipeline Infrastructure Summary

**One-liner:** Deterministic PDF figure pipeline using docs_fig.py import + seeded draws + suppressed CreationDate, proven byte-identical by git diff gate on committed smoke.pdf.

## What Was Built

A three-file paper figure pipeline that satisfies both PIPE-01 and PIPE-02 in a single proven vertical slice:

**`paper/code/paper_utils.py`** — shared helper module:
- Re-exports `fig` and `FDARS_COLORS` from `scripts/docs_fig.py` via sys.path injection (`_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"`). Importing `docs_fig` runs its module-top `matplotlib.use("Agg")` and `plt.rcParams.update` — backend and style are active without repeating them.
- `data_path(name)`: rejects traversal (`..` in parts or absolute path via `ValueError`; T-85-01), resolves against `docs/data/` in the repo root, raises `FileNotFoundError` if absent. No dataset is copied.
- `save_figure(figure, path)`: calls `figure.savefig(path, format="pdf", bbox_inches="tight", metadata={"CreationDate": None})` then `plt.close(figure)`. Suppressed `CreationDate` is what makes re-runs produce byte-identical PDF output (T-85-02).

**`paper/code/gen_figures.py`** — pipeline entry point:
- Imports `fig`, `save_figure` from `paper_utils`.
- `_smoke()`: calls `np.random.seed(20260908)` before any stochastic draw, builds a cumulative random walk figure using the `fig()` factory, writes to `paper/figures/smoke.pdf` via `save_figure`.
- `main()` calls `_smoke()` — Phases 88/89 append additional figure calls here.
- Guard: `if __name__ == "__main__": main()`.

**`Makefile`** — two new targets added (existing docs targets untouched):
- `PAPER_PYTHONPATH := scripts:paper/code` — both `scripts/` (for docs_fig) and `paper/code/` (for paper_utils) on PYTHONPATH.
- `paper-figures`: runs `PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_figures.py`.
- `paper`: depends on `paper-figures` (one-command runner).
- No tectonic/pdflatex invocation — CI-only (GATE-01, Phase 86).

**`paper/figures/smoke.pdf`** — first committed deterministic figure proving the gate.

## Verification Results

All plan verification criteria passed:

| Check | Result |
|-------|--------|
| `gen_figures.py` runs under `PYTHONPATH=scripts:paper/code` | PASS |
| `smoke.pdf` created | PASS |
| `p.fig.__module__ == 'docs_fig'` (reuse, not reimplementation) | PASS |
| `len(p.FDARS_COLORS) == 7` | PASS |
| `data_path('growth.csv').is_absolute() and .exists()` | PASS |
| `data_path('../secret')` raises `ValueError` | PASS |
| `MAKE_OK` (PHONY, PAPER_PYTHONPATH, gen_figures, no tectonic) | PASS |
| Second `gen_figures.py` run: `git diff --exit-code paper/figures/` | PASS (empty diff) |
| `make paper` with venv active: `git diff --exit-code paper/figures/` | PASS (empty diff) |

## Deviations from Plan

None — plan executed exactly as written.

The plan's Task 3 `<automated>` verify block included an inline `git commit` step as part of the verification sequence. Instead, smoke.pdf was committed in its own atomic commit (`feat(85-01): commit initial deterministic smoke.pdf`) prior to the re-run check, which satisfies the same acceptance criteria while keeping the commit history clean.

## Known Stubs

None. The smoke figure is intentionally minimal (it is the determinism-gate proof artifact, not a manuscript figure). The `main()` function in `gen_figures.py` will be extended with real figure functions in Phases 88/89.

## Self-Check

**Created files:**

- `paper/code/paper_utils.py` — FOUND (commit 41580a2)
- `paper/code/gen_figures.py` — FOUND (commit 41580a2)
- `paper/code/.gitkeep` — FOUND (commit 41580a2)
- `paper/figures/smoke.pdf` — FOUND (commit 2ac41b8)
- `Makefile` (modified) — FOUND (commit fe007b5)

**Commits:**

- `41580a2` feat(85-01): add paper_utils.py, gen_figures.py, and .gitkeep
- `fe007b5` feat(85-01): add paper/paper-figures Makefile targets
- `2ac41b8` feat(85-01): commit initial deterministic smoke.pdf

## Self-Check: PASSED
