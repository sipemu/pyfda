---
phase: 85-manuscript-scaffold-pipeline-infrastructure
verified: 2026-09-08T21:00:04Z
status: passed
score: 9/9
behavior_unverified: 0
overrides_applied: 0
re_verification: null
gaps: []
deferred: []
behavior_unverified_items: []
human_verification: []
---

# Phase 85: Manuscript Scaffold + Pipeline Infrastructure — Verification Report

**Phase Goal:** A `paper/` project exists with a compiling minimal manuscript skeleton and a deterministic reproducible-code framework, locking every tooling decision (plain `article`, natbib+BibTeX, no timestamp macros, `Agg`/seeded matplotlib, data reuse) that later phases depend on.
**Verified:** 2026-09-08T21:00:04Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `paper/paper.tex` uses `\documentclass{article}` with natbib + BibTeX, no biblatex/biber, no `\today`/timestamp macros | ✓ VERIFIED | grep confirms `\documentclass[12pt,a4paper]{article}`, `\usepackage[numbers,sort&compress]{natbib}`, `\bibliography{refs}`; negative grep finds no biblatex/biber/addbibresource/printbibliography and no `\today`/`\currenttime` in `paper.tex` or any section stub |
| 2 | `paper/paper.tex` `\input`s exactly seven per-section stub files, each with a `\section` heading and a placeholder paragraph | ✓ VERIFIED | `ls paper/sections/*.tex | wc -l` = 7; all seven confirmed to contain exactly one `\section{}` heading and a placeholder sentence; `paper.tex` contains exactly seven `\input{sections/...}` directives |
| 3 | The author block names Simon Müller with sm@data-zoo.de and `\date{}` is empty | ✓ VERIFIED | `paper.tex` contains `\author{Simon M\"{u}ller\\\texttt{sm@data-zoo.de}}` and `\date{}` — no timestamp macro present |
| 4 | `CITATION.cff` declares cff-version 1.2.0, a `preferred-citation` block, and author Müller / Simon / sm@data-zoo.de | ✓ VERIFIED | `cff-version: "1.2.0"` present; `preferred-citation` block with `type: article`, paper title, same author; `family-names: "Müller"`, `given-names: "Simon"`, `email: "sm@data-zoo.de"` confirmed; journal field and arXiv URL placeholder present (Phase 90 deferred) |
| 5 | `cffconvert --validate` exits zero against `CITATION.cff` | ✓ VERIFIED | `.venv/bin/cffconvert --validate -i CITATION.cff` output: "Citation metadata are valid according to schema version 1.2.0." Exit code: 0 |
| 6 | `paper/code/paper_utils.py` imports `fig` and `FDARS_COLORS` from `docs_fig` (not reimplemented) and `fig.__module__ == 'docs_fig'` | ✓ VERIFIED | Runtime check: `p.fig.__module__ == 'docs_fig'` (True); `len(p.FDARS_COLORS) == 7` (True); no `def fig` or `FDARS_COLORS =` in `paper_utils.py` — these are re-exported imports only |
| 7 | `data_path(name)` resolves into `docs/data/` and rejects traversal via post-resolution containment check; no dataset duplicated | ✓ VERIFIED | `data_path('growth.csv')` returns absolute path `/home/simonm/projects/rust/pyfda/docs/data/growth.csv`, exists; `data_path('../secret')` raises `ValueError`; implementation uses `resolved.is_relative_to(data_dir)` post-resolution containment check (commit 4fa22c4) |
| 8 | `make paper` / `paper-figures` target regenerates figures in one command; matplotlib on Agg backend with per-figure seeding; `save_figure` suppresses `CreationDate` | ✓ VERIFIED | Makefile defines `PAPER_PYTHONPATH := scripts:paper/code`, `paper-figures` invokes `gen_figures.py` under that PYTHONPATH; `docs_fig` import side-effect activates Agg + rcParams; `gen_figures.py` uses `np.random.default_rng(20260908)` (per-figure, deterministic); `save_figure` calls `metadata={"CreationDate": None}`; `make paper` exits 0 |
| 9 | Re-running `make paper` leaves `git diff paper/figures/` empty (byte-identical deterministic PDF) | ✓ VERIFIED | Pipeline run twice: `git diff --exit-code paper/figures/` returns exit code 0 both times — committed `smoke.pdf` is byte-identical on regeneration |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

### Backstop Item (not scored — CI-only, deferred to Phase 86)

| Item | Verification | Status |
|------|-------------|--------|
| `paper/paper.tex` + section stubs + `refs.bib` compile to a minimal PDF via CI tectonic with a BibTeX pass | `verification: backstop` in 85-02-PLAN.md frontmatter | NOT GATED LOCALLY — Phase 86 installs CI tectonic gate |

The CI tectonic compile is intentionally not verified here per the PLAN backstop declaration and the REQUIREMENTS.md "Out of Scope" constraint ("Local LaTeX toolchain setup: None installed; PDF compile is CI-only"). This is a Phase 86 deliverable (GATE-01).

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `paper/paper.tex` | Root LaTeX manuscript | ✓ VERIFIED | Exists, substantive (42 lines), wired to 7 section stubs and refs.bib |
| `paper/refs.bib` | Stub bibliography | ✓ VERIFIED | Exists with valid placeholder `@misc` entry; Phase 86 note present |
| `paper/sections/intro.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Introduction}` |
| `paper/sections/design.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Software Design and Architecture}` |
| `paper/sections/represent.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Data Representation}` |
| `paper/sections/capabilities.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Capabilities}` |
| `paper/sections/comparison.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Comparison with Related Software}` |
| `paper/sections/casestudies.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Case Studies}` |
| `paper/sections/availability.tex` | Section stub | ✓ VERIFIED | Exists, has `\section{Availability and Installation}` |
| `paper/code/paper_utils.py` | Pipeline helper module | ✓ VERIFIED | Exists, substantive (105 lines), imports from docs_fig, wired via PYTHONPATH |
| `paper/code/gen_figures.py` | Pipeline entry point | ✓ VERIFIED | Exists, substantive (55 lines), imports paper_utils, seeded draw, wired via Makefile |
| `paper/figures/smoke.pdf` | Committed deterministic figure | ✓ VERIFIED | Committed at `2ac41b8`, byte-identical on re-run |
| `CITATION.cff` | Citation metadata | ✓ VERIFIED | CFF v1.2.0, cffconvert-valid, preferred-citation block, correct author |
| `Makefile` (paper, paper-figures targets) | One-command runner | ✓ VERIFIED | `PAPER_PYTHONPATH`, `paper`, `paper-figures` all present; no tectonic/pdflatex in recipes |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `paper_utils.py` | `scripts/docs_fig.py` | `from docs_fig import fig, FDARS_COLORS` via sys.path injection (`_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"`) | ✓ WIRED | Runtime confirmed: `fig.__module__ == 'docs_fig'` |
| `gen_figures.py` | `paper_utils.save_figure` | `from paper_utils import fig, save_figure` | ✓ WIRED | Direct import; `save_figure` called in `_smoke()` |
| `gen_figures.py` | `paper/figures/smoke.pdf` | `save_figure(f, _FIGURES_DIR / "smoke.pdf")` | ✓ WIRED | File committed and byte-identical on re-run |
| `Makefile paper target` | `gen_figures.py` | `PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_figures.py` | ✓ WIRED | `make paper` exits 0; git diff clean |
| `paper/paper.tex` | 7 section stubs | `\input{sections/...}` × 7 | ✓ WIRED | All 7 `\input` directives confirmed in paper.tex |
| `paper/paper.tex` | `paper/refs.bib` | `\bibliography{refs}` | ✓ WIRED | `\bibliography{refs}` confirmed; `refs.bib` exists |
| `CITATION.cff` | `cffconvert --validate` | Schema validation | ✓ WIRED | Exits zero, schema version 1.2.0 |
| `data_path()` | `docs/data/` | post-resolution `is_relative_to` containment check | ✓ WIRED | Returns absolute path into `docs/data/`; rejects traversal |

---

### Data-Flow Trace (Level 4)

No dynamic user-facing data rendering — this phase produces static infrastructure files (LaTeX, Python helpers, Makefile, CFF). Data-flow trace is N/A except for `data_path()` which is verified to resolve correctly against the live `docs/data/` directory (not a stub/mock).

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `fig.__module__ == 'docs_fig'` (import, not reimplement) | `python -c "import paper_utils as p; assert p.fig.__module__=='docs_fig'"` | True | ✓ PASS |
| `data_path('growth.csv')` returns absolute existing path | `python -c "p.data_path('growth.csv').is_absolute() and .exists()"` | True, `/home/simonm/projects/rust/pyfda/docs/data/growth.csv` | ✓ PASS |
| `data_path('../secret')` raises ValueError (traversal rejected) | `python -c "try: p.data_path('../secret')↵except ValueError: rejected=True"` | ValueError raised | ✓ PASS |
| `cffconvert --validate` exits zero | `.venv/bin/cffconvert --validate -i CITATION.cff` | "Citation metadata are valid according to schema version 1.2.0." exit 0 | ✓ PASS |
| `make paper` runs without error | `source .venv/bin/activate && make paper` | exit 0 | ✓ PASS |
| Determinism: second run leaves git diff empty | `python gen_figures.py` × 2; `git diff --exit-code paper/figures/` | exit 0 both times | ✓ PASS |
| `np.random.default_rng` is deterministic with fixed seed | Two independent `default_rng(20260908)` instances produce equal arrays | `(y1 == y2).all()` = True | ✓ PASS |

---

### Probe Execution

No phase-declared probe scripts (`scripts/*/tests/probe-*.sh`). Step 7b behavioral spot-checks cover the verification criteria.

---

### Requirements Coverage

| Requirement | Phase Assigned | Description | Status | Evidence |
|-------------|---------------|-------------|--------|---------|
| MANU-01 | Phase 85 | `paper/` LaTeX with `article` class, natbib+BibTeX, per-section files, no timestamp macros | ✓ SATISFIED | `paper/paper.tex` + 7 section stubs verified; no biblatex/`\today` found |
| MANU-08 | Phase 85 | `CITATION.cff` v1.2.0, cffconvert-valid, `preferred-citation` block, author Simon Müller | ✓ SATISFIED | `cffconvert --validate` exits 0; preferred-citation and author verified |
| PIPE-01 | Phase 85 | `paper/code/` reproducible pipeline with one-command runner; `paper_utils.py` reuses `docs_fig.py`; `data_path()` resolves `docs/data/`, no duplication | ✓ SATISFIED | `make paper` runs; `fig.__module__=='docs_fig'`; `data_path` resolves correctly |
| PIPE-02 | Phase 85 | Deterministic figure generation — Agg, rcParams, per-figure seed, suppressed `CreationDate`; `git diff paper/figures/` empty on re-run | ✓ SATISFIED | `metadata={"CreationDate": None}` in `save_figure`; `default_rng(20260908)`; git diff empty × 2 runs |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `CITATION.cff` | 34 | `TODO: update to venue/journal name at submission (Phase 90)` | ℹ️ Info | Intentional deferred stub; references Phase 90 as formal follow-up — not an unresolved debt marker under the debt-marker gate |
| `CITATION.cff` | 37 | `TODO: replace with actual arXiv ID at submission (Phase 90)` | ℹ️ Info | Intentional deferred stub; references Phase 90 — arXiv ID cannot exist before submission |

**Debt-marker gate assessment:** Both `TODO` markers in `CITATION.cff` explicitly reference "Phase 90" as formal follow-up work. The arXiv ID placeholder and journal field are by design deferred to Phase 90 (REL-01, per ROADMAP.md and REQUIREMENTS.md). These do NOT trigger the `TBD`/`FIXME`/`XXX` hard-blocker gate (which covers unreferenced markers); referenced `TODO` with a named phase constitutes auditable follow-up.

No `TBD`, `FIXME`, or `XXX` markers found in any phase-modified file.

---

### Code-Review Fix Verification

The phase SUMMARY references three post-plan code-review fixes. All three are confirmed in the codebase:

| Fix | Commit | Verification |
|-----|--------|-------------|
| IN-01: Replace global `np.random.seed` with per-figure `np.random.default_rng` | `abe453f` | `gen_figures.py` uses `rng = np.random.default_rng(20260908)` — no `np.random.seed` call present |
| WR-01: Add `journal` field and arXiv URL placeholder to `preferred-citation` | `d62171e` | `CITATION.cff` has `journal: "arXiv preprint"` and `identifiers` URL entry pointing to arXiv |
| WR-02: Add post-resolution containment check to `data_path()` | `4fa22c4` | `paper_utils.py` uses `resolved.is_relative_to(data_dir)` after `resolve()` — not a prefix-only check |

---

### Human Verification Required

N/A — Infrastructure/foundation phase (paper scaffold + pipeline tooling) with no user-facing elements. All acceptance criteria are verifiable programmatically. The CI tectonic compile is a backstop item deferred to Phase 86 (GATE-01) by plan design.

---

### Decision Coverage

No CONTEXT.md with `<decisions>` block found for this phase. Decision coverage gate skipped (per verifier-phase-gates Step `verify_decisions` skip condition).

---

### Test Quality Audit

This phase produces no test files. No requirement-linked tests exist to audit. Test quality gate is N/A.

---

## Gaps Summary

No gaps. All 9 observable truths are verified. All 14 required artifacts exist, are substantive, and are wired. All 4 phase requirements (MANU-01, MANU-08, PIPE-01, PIPE-02) are satisfied. The one backstop item (CI tectonic PDF compile) is correctly deferred to Phase 86 per the plan's explicit `backstop:` frontmatter block and the REQUIREMENTS.md constraint.

The phase goal is achieved: a `paper/` project exists with a minimal manuscript skeleton and a proven deterministic reproducible-code framework, with all tooling decisions locked for subsequent phases.

---

_Verified: 2026-09-08T21:00:04Z_
_Verifier: Claude (gsd-verifier)_
