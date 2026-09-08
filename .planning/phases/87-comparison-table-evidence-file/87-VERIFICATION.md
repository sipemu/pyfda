---
phase: 87-comparison-table-evidence-file
verified: 2026-09-08T22:47:05Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 87: Comparison Table + Evidence File Verification Report

**Phase Goal:** The highest peer-review-rejection-risk artifact — the comparison-with-related-software table — exists and is defensible, with every competitor cell backed by a version-stamped source, so the capability tour that cites it can be written with confidence.
**Verified:** 2026-09-08T22:47:05Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `paper/comparison_evidence.md` records version-stamped source for all 9 peer packages (scikit-fda, FDApy, fda, fda.usc, refund, funData, tidyfun, fdaM, PACE) | ✓ VERIFIED | `EVIDENCE_OK` — all 9 packages present with version, URL, access date 2026-09-08; 126 dimension rows = 14 dims × 9 packages |
| 2 | `comparison_evidence.md` has ≥1 spot-checked package with version + date | ✓ VERIFIED | 4 packages marked `Spot-checked: YES`; scikit-fda 0.10.1 and fda.usc 2.2.0 confirmed present |
| 3 | `paper/sections/comparison_table.tex` is an `\input`-ed booktabs/adjustbox table with 14 capability-dimension rows × 6 family columns, ✓/partial/— coverage | ✓ VERIFIED | `TABLE_OK` — adjustbox wrap, `\toprule`, label `tab:comparison`, `\FdarsVersion{0.12.0}`, 37 checkmark cells (≥20 required), no bare Unicode checkmark; comparison.tex `\input`s it with prose intro, no placeholder |
| 4 | `paper/paper.tex` preamble loads booktabs and adjustbox before `\begin{document}` | ✓ VERIFIED | `usepackage{booktabs}` line 16, `usepackage{adjustbox}` line 17, both before `\begin{document}`; awk ordering check confirms |
| 5 | `check_comparison.py` exits 0 on the committed evidence+table pair, and non-zero when any non-fdars ✓/partial cell has no matching evidence line | ✓ VERIFIED | `COMPARISON_TRACE_OK` (exit 0); `TRACE_GATE_FIRES` confirmed — removing scikit-fda section → 9 UNSOURCED lines + exit 1; file restored byte-for-byte |
| 6 | `check_comparison.py` additionally asserts every fdars cell is ✓ AND grounded in `_capability_map.json` (COMP-02 grounding) | ✓ VERIFIED | `GROUNDING_GATE_FIRES` confirmed — emptying `fts` submodule → `UNGROUNDED: Functional time series` + exit 1; capability map restored byte-for-byte |
| 7 | `make paper-check` and `paper.yml` run `check_comparison.py` as an enforced gate before tectonic | ✓ VERIFIED | `WIRED_OK` — `check_comparison.py` in `paper-check` recipe (not in `paper:` generation target); paper.yml step after `gen_refs_bib.py` and before `Setup tectonic`; YAML valid; no maturin |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `paper/comparison_evidence.md` | Nine-package version-stamped evidence dossier | ✓ VERIFIED | At `paper/` (not under `sections/`); 9 packages; 126 dimension rows |
| `paper/sections/comparison_table.tex` | Booktabs+adjustbox LaTeX table | ✓ VERIFIED | 37 checkmark cells, `tab:comparison` label, `\FdarsVersion` macro |
| `paper/sections/comparison.tex` | Section with prose intro + `\input` | ✓ VERIFIED | Stub replaced; 2-sentence intro; `\ref{tab:comparison}`; `\input{sections/comparison_table}`; no "Placeholder" |
| `paper/paper.tex` | Preamble with booktabs + adjustbox | ✓ VERIFIED | Lines 16–17 in preamble before `\begin{document}` |
| `paper/code/check_comparison.py` | Stdlib-only SC-3 + COMP-02 gate | ✓ VERIFIED | `from __future__ import annotations`, module docstring; stdlib-only (json, re, sys, pathlib); `DIMENSION_SUBMODULES`, `STATE_MISMATCH`, `ORPHAN_SUBMODULE_KEY` guards all present |
| `Makefile` | `paper-check` target includes `check_comparison.py` | ✓ VERIFIED | Present in `paper-check` recipe; absent from `paper:` generation target |
| `.github/workflows/paper.yml` | Offline gate before tectonic | ✓ VERIFIED | Step after `gen_refs_bib.py`, before `Setup tectonic`; valid YAML; no maturin |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| Every non-fdars ✓/partial table cell | Claim in `comparison_evidence.md` | `check_comparison.py` parse + match | ✓ WIRED | Positive: `COMPARISON_TRACE_OK`; Negative: `TRACE_GATE_FIRES` when scikit-fda section removed |
| fdars ✓ cells | `_capability_map.json` submodule entries | `check_comparison.py` `DIMENSION_SUBMODULES` | ✓ WIRED | Positive: `COMPARISON_TRACE_OK`; Negative: `GROUNDING_GATE_FIRES` when `fts` emptied |
| `comparison_table.tex` | `paper.tex` compiled output | `\input` in `comparison.tex`, `\input` in `paper.tex` | ✓ WIRED | `comparison.tex` `\input{sections/comparison_table}`; chain confirmed |
| `paper-check` (local gate) | `check_comparison.py` | Makefile recipe | ✓ WIRED | `PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/check_comparison.py` in `paper-check` |
| `paper.yml` (CI gate) | `check_comparison.py` | Workflow step before tectonic | ✓ WIRED | Step order: `gen_refs_bib.py` < `check_comparison.py` < `Setup tectonic`; awk confirms |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `comparison_table.tex` fdars column | ✓/partial/— cells | `_capability_map.json` via `check_comparison.py` grounding | Yes — gate fails if submodule absent/empty | ✓ FLOWING |
| `comparison_evidence.md` peer claims | Per-package dimension cells | RESEARCH.md dossiers (transcribed; spot-checked against PyPI/CRAN) | Yes — 4 spot-checked packages | ✓ FLOWING |
| `check_comparison.py` | Table parse + evidence lookup | `comparison_table.tex` + `comparison_evidence.md` + `_capability_map.json` | Yes — live parse, not hardcoded | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate passes on committed state | `.venv/bin/python paper/code/check_comparison.py` | `COMPARISON_TRACE_OK`, exit 0 | ✓ PASS |
| Gate fires when peer evidence removed | Remove scikit-fda section, run gate | 9 `UNSOURCED:` lines, exit 1, file restored | ✓ PASS |
| Grounding gate fires when submodule emptied | Empty `fts` in `_capability_map.json`, run gate | `UNGROUNDED: Functional time series`, exit 1, file restored | ✓ PASS |
| No SyntaxWarning on import | `.venv/bin/python -W error::SyntaxWarning -c "import sys;sys.path.insert(0,'paper/code');import check_comparison"` | exit 0, no warnings | ✓ PASS |
| Repo clean after negative tests | `git diff --quiet paper/comparison_evidence.md python/fdars/_capability_map.json` | exit 0 | ✓ PASS |

### Probe Execution

No conventional `scripts/*/tests/probe-*.sh` probes declared for this phase. The plan's verification commands serve as probes — all ran and passed above.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| COMP-01 | 87-01 | `comparison_evidence.md` — every peer-package claim backed by a version-stamped source; ≥1 spot-checked | ✓ SATISFIED | All 9 packages with version/URL/date; 4 marked `Spot-checked: YES` including scikit-fda 0.10.1 and fda.usc 2.2.0 |
| COMP-02 | 87-01, 87-02 | Comparison table `\input`-ed; fdars column grounded from `_capability_map.json`; coverage honest | ✓ SATISFIED | `TABLE_OK` + `WIRED_OK` + `GROUNDING_GATE_FIRES` negative test confirms machine enforcement |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `paper/sections/comparison_table.tex` | 4 | `TODO(REL-01): bump \FdarsVersion to 0.13.0 when Phase 90 releases.` | ℹ️ Info | References formal requirement REL-01 tracked in REQUIREMENTS.md (Phase 90); not an unresolved debt marker — passes debt-marker gate |

No `TBD`, `FIXME`, or `XXX` markers found in any phase-modified file. The single `TODO` references REL-01, a formal tracked requirement for Phase 90, satisfying the debt-marker gate.

### Code Review Integration

Code review (87-REVIEW.md) found 1 critical + 3 warnings + 2 info. All 6 findings were fixed before this verification ran (87-REVIEW-FIX.md):

- **CR-01** (FIXED, commit b4e0608): `cran.r-parse.org` broken URL corrected to `cran.r-project.org`
- **WR-01** (FIXED, commit 1dc2cc6): `STATE_MISMATCH` guard added — `partial` evidence no longer silently satisfies `checkmark` table cells
- **WR-02** (FIXED, commit 6628a39): `fda` Registration/FPCA cells now cite `register.fd`/`pca.fd` from fda reference manual PDF (package-level, not just CRAN task view); `Spot-checked: NO` changed to `YES`
- **WR-03** (FIXED, commit 322bba2): Redundant `\\&` replace call removed; no SyntaxWarning
- **IN-01** (FIXED, commit d78c57e): Forward-looking Phase 90 comment converted to `TODO(REL-01):` marker
- **IN-02** (FIXED, commit 08b404c): `ORPHAN_SUBMODULE_KEY` bidirectional validation added to `main()`

Post-fix `COMPARISON_TRACE_OK` confirmed. All URL and SyntaxWarning checks clean.

### Human Verification Required

None. The tectonic PDF render is CI-only and is designated as a Phase 90 GATE-03 backstop (explicitly per both plans). This is a by-design deferred backstop, not a gap — it mirrors the Phase 86 approach where CI-only steps are not local failures.

**CI backstop for Phase 90 (deferred by design):**
- **Test:** tectonic compiles paper.tex with comparison_table.tex `\input` into a PDF showing the table
- **Expected:** table renders with correct column count, booktabs rules, and fdars version in caption
- **Why deferred:** No local LaTeX toolchain; tectonic runs only in CI (paper.yml); Phase 90 GATE-03 is the blocking human read-through that confirms PDF correctness
- **Deferred to:** Phase 90

### Gaps Summary

No gaps. All 7 must-haves verified. All three success criteria (COMP-01, COMP-02, SC-3 traceability) achieved with machine enforcement. The code review findings that were outstanding at submission time have all been addressed. Repo is clean.

---

_Verified: 2026-09-08T22:47:05Z_
_Verifier: Claude (gsd-verifier)_
