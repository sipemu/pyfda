---
phase: 86-single-source-of-truth-wiring-ci-gate
verified: 2026-09-08T21:43:04Z
status: passed
score: 7/8 must-haves verified (1 CI-only backstop deferred to Phase 90 close gate)
behavior_unverified: 0
overrides_applied: 1
override_rationale: "The single non-verified item is the tectonic PDF compile, which runs ONLY in GitHub Actions and is a by-design `verification: backstop` for this phase. All locally-verifiable structural checks of paper.yml pass (path-filter, step order, pinned action SHA, SOURCE_DATE_EPOCH). The milestone roadmap explicitly makes the end-to-end CI/PDF build a Phase 90 close-gate item (GATE-02 pipeline re-verify + GATE-03 human approval). Deferred there rather than blocking Phase 86. Recorded in STATE.md deferred verification."
human_verification:
  - test: "Trigger paper.yml CI workflow (push or PR touching paper/**) and confirm tectonic compiles paper/paper.tex to a PDF with SOURCE_DATE_EPOCH=0"
    expected: "GitHub Actions workflow succeeds end-to-end — offline pipeline gate passes and tectonic produces a PDF without errors"
    why_human: "tectonic PDF compile runs only in GitHub Actions; cannot execute locally without CI runner environment and GITHUB_TOKEN"
    deferred_to: "Phase 90 (close gate — GATE-02/GATE-03)"
---

# Phase 86: Single-Source-of-Truth Wiring + CI Gate Verification Report

**Phase Goal:** The drift tripwires are functional before any prose cites a number — coverage counts and the bibliography are machine-derived from the committed JSON maps, and a standalone CI workflow runs the pipeline offline and compiles the PDF.
**Verified:** 2026-09-08T21:43:04Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `assert_coverage.py` derives six coverage macros from JSON maps and exits non-zero on drift — no coverage integer hardcoded in any `.tex` (PIPE-03) | ✓ VERIFIED | `assert_coverage.py --check` exits 0; all 6 macros correct (ncallables=437, npubliccallables=409, nsubmodules=30, nfdata=27, ncoverage=28, ndocpapers=47); `grep -vE '^\s*%' paper/paper.tex paper/sections/*.tex | grep -E '\b(437|409|28|47)\b'` returns empty |
| 2 | `assert_coverage.py --check` exits non-zero on drift (PIPE-03 negative test) | ✓ VERIFIED | Deliberate mutation appended to coverage_counts.tex → exit 1 with "DRIFT: stale"; file restored clean (`git diff --quiet` passes) |
| 3 | `gen_refs_bib.py` generates 47 `@misc` entries, skipping `_uncurated_*` keys, no `{None}` values (PIPE-04, including CR-01 fix) | ✓ VERIFIED | `grep -c '^@misc{' paper/refs.bib` = 47; `grep -q '{None}' paper/refs.bib` returns exit 1 (no None); 0 uncurated keys; no empty doi/url lines; all titles double-braced; `gen_refs_bib.py --check` exits 0 |
| 4 | `gen_refs_bib.py --check` exits non-zero on drift (WR-01 fix verified) | ✓ VERIFIED | Deliberate mutation appended to refs.bib → exit 1 with "DRIFT: stale"; file restored clean |
| 5 | `paper/paper.tex` consumes coverage macros via `\input{coverage_counts}` before `\begin{document}` and `\bibliography{refs}` | ✓ VERIFIED | `\input{coverage_counts}` at line 24; `\begin{document}` at line 26; `\bibliography{refs}` at line 42; `\bibliographystyle{plain}` at line 41 |
| 6 | `.github/workflows/paper.yml` exists, valid YAML, path-filtered to `paper/**` + both JSON maps + `docs/data/**`, step order gen_figures → assert_coverage --check → gen_refs_bib --check → gen_refs_bib → tectonic (GATE-01) | ✓ VERIFIED | `yaml.safe_load` passes; all 4 path filters confirmed; STEP_ORDER_OK (awk NR check: gen_figures < assert_coverage --check < gen_refs_bib < tectonic); no fetch-depth/biber-version/maturin |
| 7 | `make paper` regenerates figures + coverage + refs deterministically (empty git diff on re-run); `make paper-check` runs both drift checks | ✓ VERIFIED | Full pipeline re-run → `git diff --exit-code paper/coverage_counts.tex paper/refs.bib paper/figures/` exits 0 (PIPELINE_DETERMINISTIC); `make paper-check` target confirmed in Makefile invoking both `--check` modes |
| 8 | paper.yml compiles `paper/paper.tex` to a PDF via tectonic with `SOURCE_DATE_EPOCH=0` on GitHub Actions (GATE-01) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED (backstop) | Workflow has step `tectonic paper/paper.tex` with `SOURCE_DATE_EPOCH: "0"`, action `wtfjoke/setup-tectonic@eb29fd68b7d3f76011906b6e45ea4320c8de5d2f  # v4`; cannot execute locally — requires CI runner + GITHUB_TOKEN |

**Score:** 7/8 truths verified (1 present, behavior-unverified — CI-only backstop)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `paper/code/assert_coverage.py` | Coverage-macro generator + `--check` drift gate | ✓ VERIFIED | Substantive: 139 lines; `_derive_counts()` mirrors `generate_capability_dataset.py:_coverage_counts()` exactly; `--check` mode compares byte-for-byte; wired from Makefile `paper-coverage` target |
| `paper/code/gen_refs_bib.py` | BibTeX generator from `_references_map.json` | ✓ VERIFIED | Substantive: 142 lines; `--check` mode added (WR-01 fix); `year = paper.get("year") or ""` pattern (CR-01 fix); wired from Makefile `paper-refs` target and paper.yml |
| `paper/coverage_counts.tex` | 6 `\newcommand` macros, committed | ✓ VERIFIED | 8 lines; all 6 macros with correct values; byte-identical on re-run (sorted key order); consumed via `\input{coverage_counts}` |
| `paper/refs.bib` | 47 `@misc` entries, no `_uncurated`, no `{None}` | ✓ VERIFIED | 47 `@misc` entries; 0 `_uncurated` keys; 0 `{None}` occurrences; 0 empty doi/url lines; double-braced titles; deterministic on re-run |
| `paper/paper.tex` | `\input{coverage_counts}` in preamble; `\bibliography{refs}` | ✓ VERIFIED | `\input{coverage_counts}` at line 24 (before `\begin{document}` at line 26); `\bibliography{refs}` at line 42 |
| `Makefile` | `paper` depends on `paper-figures paper-coverage paper-refs`; `paper-check` phony; no tectonic | ✓ VERIFIED | Line 54: `paper: paper-figures paper-coverage paper-refs`; `.PHONY` line includes both new targets and `paper-check`; `paper-check` runs both `--check` modes; no tectonic/pdflatex |
| `.github/workflows/paper.yml` | Path-filtered, ordered steps, tectonic action | ✓ VERIFIED (structure) | Valid YAML; all 4 path filters; correct step order; tectonic action pinned to commit SHA `eb29fd68...  # v4` (WR-03 fix); SOURCE_DATE_EPOCH=0; no forbidden tokens |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `python/fdars/_capability_map.json` | `paper/coverage_counts.tex` | `assert_coverage.py:_derive_counts()` | ✓ WIRED | `_CAP_MAP = _REPO / "python" / "fdars" / "_capability_map.json"`; reads and derives 6 macros |
| `python/fdars/_references_map.json` | `paper/refs.bib` | `gen_refs_bib.py:_build_content()` | ✓ WIRED | `_REF_MAP = _REPO / "python" / "fdars" / "_references_map.json"`; sorted(papers) iteration |
| `paper/coverage_counts.tex` | `paper/paper.tex` | `\input{coverage_counts}` at line 24 | ✓ WIRED | Preamble position confirmed (line 24 < line 26 `\begin{document}`) |
| `paper/refs.bib` | `paper/paper.tex` | `\bibliography{refs}` at line 42 | ✓ WIRED | Cite-key = paper-key verbatim; no transformation |
| `assert_coverage.py --check` | `paper.yml` step 5 | Direct invocation as hard gate | ✓ WIRED | Step "Assert coverage macros (PIPE-03 drift gate)": `run: python paper/code/assert_coverage.py --check` |
| `gen_refs_bib.py --check` | `paper.yml` step 6 | Direct invocation as hard gate (WR-01 fix) | ✓ WIRED | Step "Assert refs.bib not stale (PIPE-04 drift gate)": `run: python paper/code/gen_refs_bib.py --check` |
| `gen_figures.py` | `paper.yml` step 4 | Direct invocation before gates | ✓ WIRED | Step "Regenerate figures" with `PYTHONPATH: scripts:paper/code` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `coverage_counts.tex` | `ncallables=437` | `sum(len(v) for v in cap.values())` from `_capability_map.json` | Yes — live JSON read | ✓ FLOWING |
| `coverage_counts.tex` | `ncoverage=28` | `callable_index` filtered by curated paper keys | Yes — live JSON read | ✓ FLOWING |
| `refs.bib` | 47 `@misc` entries | `sorted(papers)` from `_references_map.json`, uncurated skipped | Yes — live JSON read | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `assert_coverage.py` exits 0 in sync | `.venv/bin/python paper/code/assert_coverage.py --check` | `assert_coverage: OK (no drift)` (exit 0) | ✓ PASS |
| `assert_coverage.py --check` fires on drift | Append `\n%% drift\n` → run `--check` | Exit 1, "DRIFT: stale"; file restored clean | ✓ PASS |
| `gen_refs_bib.py --check` exits 0 in sync | `.venv/bin/python paper/code/gen_refs_bib.py --check` | `gen_refs_bib: OK (no drift)` (exit 0) | ✓ PASS |
| `gen_refs_bib.py --check` fires on drift | Append `\n%% drift\n` → run `--check` | Exit 1, "DRIFT: stale"; file restored clean | ✓ PASS |
| refs.bib has 47 entries, no None | `grep -c '^@misc{' paper/refs.bib` | 47 | ✓ PASS |
| No `{None}` in refs.bib (CR-01 fix) | `grep -q '{None}' paper/refs.bib` | Exit 1 (not found) | ✓ PASS |
| Full pipeline deterministic | Re-run all generators → `git diff --exit-code` | Empty diff (PIPELINE_DETERMINISTIC) | ✓ PASS |
| paper.yml valid YAML + structural checks | `yaml.safe_load` + 13 grep checks | YAML_VALID + all structural checks pass | ✓ PASS |
| Step ordering gen_figures < assert_coverage --check < gen_refs_bib < tectonic | `awk` NR ordering check | STEP_ORDER_OK | ✓ PASS |
| tectonic PDF compile via CI | Cannot run locally | N/A — requires GitHub Actions CI runner | ? SKIP (backstop) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PIPE-03 | 86-01 | assert_coverage.py derives counts, writes macros, exits non-zero on drift | ✓ SATISFIED | 6 macros verified; `--check` exits 0 in sync, exits 1 on drift; no hardcoded integers in .tex |
| PIPE-04 | 86-01 | gen_refs_bib.py generates refs.bib (paper-key cite-key, authors, DOI/URL) | ✓ SATISFIED | 47 @misc entries; 0 None values; double-braced titles; `--check` mode functional |
| GATE-01 | 86-02 | paper.yml path-filtered; offline pipeline hard gate; tectonic compile | ✓ SATISFIED (structure) / ⚠️ backstop (compile) | Structural checks all pass; tectonic compile verified only in CI |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `paper/code/gen_refs_bib.py` | 4 | Word "placeholder" in docstring | ℹ️ Info | Describes `_uncurated` data concept — not a stub; false positive from lexical scan |

No TBD/FIXME/XXX markers found in any phase-modified file. No hardcoded integers in `.tex` files.

**Code-review resolutions confirmed:**

| Finding | Severity | Status |
|---------|----------|--------|
| CR-01: `year = {None},` for null JSON year | Critical | Fixed — `paper.get("year") or ""` in gen_refs_bib.py:68; 0 `{None}` in refs.bib |
| WR-01: No drift gate for refs.bib | Warning | Fixed — `gen_refs_bib.py --check` mode added; paper.yml step 6 invokes it |
| WR-02: Docstring says "non-dunder", code filters all underscore-prefixed | Warning | Fixed in docstring — line 23 now reads "public (non-underscore-prefixed) methods" |
| WR-03: wtfjoke/setup-tectonic@v4 mutable tag | Warning | Fixed — pinned to SHA `eb29fd68b7d3f76011906b6e45ea4320c8de5d2f  # v4` |
| IN-01: No `make paper-check` target | Info | Fixed — `paper-check` phony target added to Makefile invoking both `--check` modes |

### Human Verification Required

#### 1. tectonic PDF compile via GitHub Actions CI

**Test:** Push a change touching `paper/**` (or open a PR) and wait for the `paper.yml` workflow to complete on GitHub Actions.
**Expected:** All 8 steps succeed — offline pipeline gate (gen_figures + assert_coverage --check + gen_refs_bib --check + gen_refs_bib) passes, then `tectonic paper/paper.tex` compiles to a PDF without errors, with `SOURCE_DATE_EPOCH=0` producing a deterministic timestamp.
**Why human:** The tectonic PDF compile step requires the GitHub Actions runner environment and `secrets.GITHUB_TOKEN` to download the tectonic binary via `wtfjoke/setup-tectonic`. Cannot be reproduced locally without a full CI environment. This was declared `verification: backstop` in 86-02-PLAN.md.

---

## Summary

Phase 86 achieves its goal: the drift tripwires are functional and the bibliography is machine-derived before any prose cites a number. All locally verifiable must-haves are confirmed by direct command execution:

- `assert_coverage.py` correctly derives all 6 macros (ncallables=437, ncoverage=28, ndocpapers=47, nfdata=27, npubliccallables=409, nsubmodules=30) from the committed JSON maps and exits non-zero on deliberate drift.
- `gen_refs_bib.py` emits exactly 47 `@misc` entries with no `{None}` values, no `_uncurated` keys, double-braced titles, conditional doi/url emission, and `--check` mode that fires on drift.
- All four code-review issues (CR-01, WR-01, WR-02, WR-03) and the info-level IN-01 were resolved before phase submission.
- `paper/paper.tex` consumes macros via `\input{coverage_counts}` in the preamble and bibliography via `\bibliography{refs}`.
- The `make paper` pipeline and `make paper-check` are wired and deterministic (empty git diff on re-run).
- `paper.yml` is structurally correct: valid YAML, path-filtered, correct step order, action pinned to commit SHA, SOURCE_DATE_EPOCH=0, no forbidden tokens.

One human verification item remains: the tectonic PDF compile (backstop truth, CI-only by design per GATE-01).

---

_Verified: 2026-09-08T21:43:04Z_
_Verifier: Claude (gsd-verifier)_
