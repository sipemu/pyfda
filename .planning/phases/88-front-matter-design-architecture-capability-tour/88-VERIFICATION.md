---
phase: 88-front-matter-design-architecture-capability-tour
verified: 2026-09-09T08:00:00Z
status: passed
score: 8/8
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Read each prose section (abstract, intro, design, represent, advisor, capabilities, availability, conclusion) in the built site or compiled PDF"
    expected: "Sections are coherent, well-paced, method-accurate, and read as a professional software-paper draft; no obvious errors, awkward transitions, or missing content"
    why_human: "Prose quality, cohesion, and narrative flow cannot be verified programmatically; this is the Phase 90 GATE-04 human read-through"
    deferred_to: "Phase 90 (GATE-04)"
---

# Phase 88: Front Matter, Design/Architecture & Capability Tour — Verification Report

**Phase Goal:** Experiment-free prose complete — Python FDA gap, data model, Rust/PyO3 + sklearn + advisor architecture, and a breadth-showing capability tour of minimal runnable snippets, each sourced from an EXECUTED paper/code/ script.
**Verified:** 2026-09-09T08:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Front matter reads coherently: Abstract, Introduction & statement of need framing the Python FDA gap, and a brief FDA-background section | ✓ VERIFIED | `abstract.tex`: 5-sentence abstract using macros only, no hardcoded counts; `intro.tex`: `\section{Introduction}` with Statement of need, FDA background, Contributions — all 8 `\citep` keys resolve in refs.bib; scikit-fda cited via `ramoscarreno_scikitfda_2024`, not the Ramsay textbook key (CR-02 fixed) |
| 2 | design.tex describes Rust core + PyO3 boundary HONESTLY (no false GIL-release claim, no literal "zero-copy for matrices"), module map, Fdata container, sklearn layer qualitatively (no benchmarks) | ✓ VERIFIED | `grep "GIL\|allow_threads\|release.*GIL"` returns 0 hits; `grep -i "zero.copy"` returns 0 hits; module map has 11 method-family items including `seasonal` and `multi_fdata` (WR-04 fixed); PyO3 boundary described as "read-only view without an extra data copy, with row-major↔column-major layout conversion" (accurate per `src/convert.rs`); `\nexcludedmethods{}` macro replaces the former hardcoded "13" (WR-01 fixed); no benchmark/performance claims found |
| 3 | advisor.tex is a SEPARATE advisor+provenance contribution section (not part of design.tex) | ✓ VERIFIED | `paper/paper.tex` wires `\input{sections/design}` at line 65 and `\input{sections/advisor}` at line 69 as separate `\section{}` blocks; `advisor.tex` opens with `\section{Grounded AI Advisor and Scientific Provenance}` |
| 4 | represent.tex explains Fdata (argvals/grids/rangeval) + irregular/sparse as `pace_fpca.PyIrregFdata` via `irreg_fdata_from_lists` (NOT a fabricated top-level IrregFdata) | ✓ VERIFIED | `represent.tex` line 76: `\texttt{fdars.pace\_fpca.PyIrregFdata}` and line 80: `irreg\_fdata\_from\_lists`; line 100–101 explicitly states "There is no top-level \texttt{fdars.IrregFdata} class" |
| 5 | capabilities.tex is a breadth capability tour with each snippet `\input`-ed from a generated `paper/snippets/*.tex` produced by EXECUTING `gen_snippets.py` | ✓ VERIFIED | 14 `\input{snippets/<family>}` lines verified in `capabilities.tex`; all 14 `.tex` files exist under `paper/snippets/`; `gen_snippets.py --check` exits 0 (no drift); `git diff paper/snippets/` is clean |
| 6 | `gen_snippets.py --check` exits 0; snippets are byte-stable on regen; drift gate fires on mutation | ✓ VERIFIED | `gen_snippets.py --check` → "gen_snippets: OK (no drift)", exit 0; mutation test: appended `% DRIFT TEST` to `represent.tex` → exit 1 with `DRIFT: stale/missing snippets`; regenerated + `git diff paper/snippets/` clean (exit 0) |
| 7 | availability.tex (PyPI install, plot extra, Python 3.9–3.14, MIT) + conclusion.tex present and non-stub | ✓ VERIFIED | `availability.tex`: `pip install fdars`, "PyPI", "3.9 through 3.14", "MIT licence"; conclusion.tex: 4 sentences using `\npubliccallables{}`, `\nsubmodules{}`, `\ndocpapers{}` macros only; no hardcoded integers |
| 8 | All offline pipeline gates pass: `gen_snippets.py --check`, `assert_coverage.py --check`, `gen_refs_bib.py --check`, `check_comparison.py --check` | ✓ VERIFIED | All four gates exit 0: "gen_snippets: OK", "assert_coverage: OK", "gen_refs_bib: OK", "COMPARISON_TRACE_OK" |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

### Code-Review Fix Verification

All 11 findings from `88-REVIEW.md` were addressed in commits `54d6bad`, `faca110`, `e1a5201`, `d889fd5`, `1851a6a`, `1146a83`.

| Finding | Fix Verified |
|---------|-------------|
| CR-01: 8 dangling citation keys in capabilities.tex | ✓ 0 dangling keys — all 20 unique keys resolve across refs.bib + refs_manual.bib |
| CR-02: scikit-fda mis-cited with Ramsay 2005 key | ✓ `intro.tex:11` uses `\citep{ramoscarreno_scikitfda_2024}` |
| CR-03: False GIL-release claim in design.tex | ✓ `grep "GIL\|allow_threads"` in `design.tex` returns 0 hits |
| WR-01: Hardcoded "13" for excluded methods | ✓ `design.tex` uses `\nexcludedmethods{}` macro; `coverage_counts.tex` has `\newcommand{\nexcludedmethods}{13}` |
| WR-02: Dead "Regenerate refs.bib" step in paper.yml | ✓ Step removed from workflow |
| WR-03: `assert_coverage.py` missing `encoding="utf-8"` | ✓ Both `write_text` and `read_text` calls now have `encoding="utf-8"` |
| WR-04: `seasonal` and `multi_fdata` missing from module map | ✓ Both added to `design.tex` Module Map description block |
| WR-05: `_run()` compile filename generic `"<snippet>"` | ✓ Snippet name passed to `compile()` as `f"<snippet:{name}>"` |
| WR-06: `_SNIPPETS_DIR` resolution undocumented | ✓ Comment added above `_SNIPPETS_DIR` |
| IN-01: "Rust-accelerated" implies benchmark | ✓ Changed to "Rust-backed" (conclusion) and "implemented through a Rust core" (abstract) |
| IN-02: `\checkmark` missing `amssymb` package | ✓ `\usepackage{amssymb}` added to `paper/paper.tex` preamble |

### Dangling Citation Check

**Command:** `grep -hEo '\\cite[pt]?\{...\}|\\citealt\{...\}|\\citet\{...\}' paper/sections/*.tex` → extract keys → cross-reference against refs.bib + refs_manual.bib

**Result:** 0 dangling keys. 20 unique citation keys used; all 20 defined in `paper/refs.bib` (18 keys) or `paper/refs_manual.bib` (2 keys: `ramoscarreno_scikitfda_2024`, `febrerobande_fdausc_2012`).

**`paper.tex` bibliography declaration:** `\bibliography{refs,refs_manual}` — confirmed.

### Hardcoded Integer Check

No hardcoded count integers (30/409/28/47/27/13) found in `paper/sections/*.tex`. All counts use macros from `coverage_counts.tex`:

| Macro | Value | Used in |
|-------|-------|---------|
| `\nsubmodules` | 30 | abstract, intro, design, capabilities, conclusion |
| `\npubliccallables` | 409 | abstract, intro, design, capabilities, conclusion |
| `\nsklearnestimators` | 28 | abstract, intro, design, availability |
| `\ncoverage` | 28 | capabilities, advisor |
| `\ndocpapers` | 47 | advisor, conclusion |
| `\nexcludedmethods` | 13 | design (WR-01 fix) |
| `\nfdata` | 27 | design |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `paper/sections/abstract.tex` | 5-sentence abstract, no placeholder, macros only | ✓ VERIFIED | Uses `\nsubmodules`, `\npubliccallables`, `\nsklearnestimators`; "Rust-backed" not "Rust-accelerated" |
| `paper/sections/intro.tex` | Introduction + statement of need + FDA background | ✓ VERIFIED | 3 subsections; `ramoscarreno_scikitfda_2024` for scikit-fda; 8 `\citep` keys all resolved |
| `paper/sections/design.tex` | Architecture + module map + Fdata + sklearn layer, honest boundary | ✓ VERIFIED | No GIL-release claim, no "zero-copy" literal; `seasonal` + `multi_fdata` in module map; `\nexcludedmethods{}` macro |
| `paper/sections/represent.tex` | Fdata data model + PyIrregFdata/irreg_fdata_from_lists | ✓ VERIFIED | `PyIrregFdata` and `irreg_fdata_from_lists` named correctly; explicit "no top-level IrregFdata" statement |
| `paper/sections/advisor.tex` | Separate section: build_diagnostics, advise, auto_tune, references_map, MCP tool | ✓ VERIFIED | Separate `\section{}` from design; all three entry points documented; grounding invariant explained |
| `paper/sections/capabilities.tex` | Breadth tour, 14 families, all via `\input{snippets/...}` | ✓ VERIFIED | 14 `\input` commands; 14 snippet files exist; `gen_snippets.py --check` exits 0 |
| `paper/code/gen_snippets.py` | 14-entry SNIPPETS list, generate + `--check` drift gate | ✓ VERIFIED | 14 entries confirmed; drift gate fires on mutation (exit 1); clean check exits 0 |
| `paper/snippets/*.tex` (14 files) | Machine-generated, byte-stable, no timestamps | ✓ VERIFIED | All 14 present; `git diff paper/snippets/` clean after regen |
| `paper/sections/availability.tex` | PyPI, plot extra, Python 3.9–3.14, MIT | ✓ VERIFIED | All facts present; verified against `pyproject.toml` |
| `paper/sections/conclusion.tex` | 4-sentence close, macros only, no benchmarks | ✓ VERIFIED | Uses `\npubliccallables`, `\nsubmodules`, `\ndocpapers`; "Rust-backed" |
| `paper/coverage_counts.tex` | 8 macros including `\nexcludedmethods` | ✓ VERIFIED | 8 macros present; regenerated cleanly by `assert_coverage.py` |
| `paper/refs_manual.bib` | Contains `ramoscarreno_scikitfda_2024` + `febrerobande_fdausc_2012` | ✓ VERIFIED | Both entries present; `\bibliography{refs,refs_manual}` in paper.tex |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `paper/paper.tex` | `paper/sections/abstract.tex` | `\input{sections/abstract}` inside `\begin{abstract}` | ✓ WIRED | Line 61-63 confirmed |
| `paper/paper.tex` | `paper/sections/advisor.tex` | `\input{sections/advisor}` (separate from design) | ✓ WIRED | Lines 65 (design) and 69 (advisor) are distinct |
| `capabilities.tex` | `paper/snippets/*.tex` (14 files) | 14 `\input{snippets/<family>}` lines | ✓ WIRED | All 14 targets exist and are confirmed generated by `gen_snippets.py` |
| `gen_snippets.py` | `fdars` API (live execution) | `exec()` in fresh namespace with `data_path` injected | ✓ WIRED | `--check` exits 0 confirming live execution produces byte-identical output |
| `paper/paper.tex` | `paper/refs_manual.bib` | `\bibliography{refs,refs_manual}` | ✓ WIRED | Confirmed in paper.tex |
| `paper/sections/design.tex` | `\nexcludedmethods{}` macro | `assert_coverage.py` → `coverage_counts.tex` | ✓ WIRED | Macro present in coverage_counts.tex; consumed in design.tex |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Snippet drift gate: clean state exits 0 | `gen_snippets.py --check` | "gen_snippets: OK (no drift)", exit 0 | ✓ PASS |
| Snippet drift gate: mutation fires | Append `% DRIFT TEST` to `represent.tex` → `--check` | "DRIFT: stale/missing snippets", exit 1 | ✓ PASS |
| Snippets byte-stable on regen | `gen_snippets.py` (generate) → `git diff paper/snippets/` | exit 0 (clean) | ✓ PASS |
| Coverage macro drift gate | `assert_coverage.py --check` | "assert_coverage: OK", exit 0 | ✓ PASS |
| Refs drift gate | `gen_refs_bib.py --check` | "gen_refs_bib: OK", exit 0 | ✓ PASS |
| Comparison traceability gate | `check_comparison.py --check` | "COMPARISON_TRACE_OK", exit 0 | ✓ PASS |
| All 14 snippet families exist | `ls paper/snippets/*.tex \| wc -l` | 14 files | ✓ PASS |
| 0 dangling citation keys | Cross-ref 20 used keys vs refs.bib + refs_manual.bib | All 20 OK | ✓ PASS |

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|------------|-------------|--------|---------|
| MANU-02 | Abstract, Introduction, statement of need, FDA background | ✓ SATISFIED | `abstract.tex` + `intro.tex` verified; scikit-fda cited correctly |
| MANU-03 | Software design & architecture — Rust core + PyO3 + module map + Fdata + sklearn (qualitative, no benchmarks) | ✓ SATISFIED | `design.tex` verified: honest boundary, correct module map, macros, no benchmarks |
| MANU-04 | Data-representation model — Fdata, argvals/grids, irregular/sparse PyIrregFdata | ✓ SATISFIED | `represent.tex` verified: correct container name, correct factory function, no fabricated top-level IrregFdata |
| MANU-05 | Capability tour by method family, snippets from executed scripts, never hand-copied | ✓ SATISFIED | `capabilities.tex` + 14 `paper/snippets/*.tex` generated by `gen_snippets.py`; drift gate confirms execution provenance |
| MANU-06 | Dedicated grounded AI advisor + scientific-provenance section as novel contribution | ✓ SATISFIED | `advisor.tex` is a separate `\section{}` documenting build_diagnostics, advise, auto_tune, references_map, MCP tool; differentiator grounded in comparison_evidence.md + Table |
| MANU-07 | Availability section (PyPI/extras/Python 3.9–3.14/MIT) + Conclusion | ✓ SATISFIED | `availability.tex` + `conclusion.tex` verified; all facts traceable to pyproject.toml; macros only in conclusion |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `paper/sections/comparison_table.tex` | 4 | `% TODO(REL-01): bump \FdarsVersion to 0.13.0...` | ℹ️ Info | References formal requirement REL-01 (Phase 90 task); satisfies debt-marker gate (tracked item); file was touched by Phase 88 commit 54d6bad but TODO originated in Phase 87 |

No blockers. The single TODO references `REL-01`, a formal requirement ID in REQUIREMENTS.md assigned to Phase 90.

### Decision Coverage

Phase 88 CONTEXT.md decisions cross-checked against shipped artifacts:

| Decision | Honored |
|----------|---------|
| Snippet sourcing via exec() + --check drift gate (MANU-06) | ✓ gen_snippets.py pattern confirmed |
| LaTeX `listings` (not `minted`) — no -shell-escape needed | ✓ `\usepackage{listings}` in paper.tex |
| `data_path` injected into exec namespace (PIPE-01 no-copy) | ✓ paper_utils.data_path used in snippets |
| `\nsklearnestimators` distinct from `\ncoverage` (Pitfall 6) | ✓ Both macros present, different values (28 vs 28 — coincidental per SUMMARY) |
| PyIrregFdata named exactly (not IrregFdata) per RESEARCH | ✓ represent.tex and fpca snippet use correct name |
| No benchmark claims; qualitative architecture only | ✓ "We make no performance claims here" in intro.tex |
| scikit-fda cited with its own software paper, not Ramsay 2005 | ✓ CR-02 fix confirmed |
| advisor.tex uses build_diagnostics only (LLM-free, offline) | ✓ advisor_diag snippet confirmed; advise() only in prose |

### Human Verification Required

#### 1. Full Prose Read-Through

**Test:** Read `paper/paper.tex` (compiled PDF or built MkDocs site) covering all sections: Abstract → Introduction → Design → Represent → Capabilities → Comparison → Advisor → Availability → Conclusion.
**Expected:** Sections are coherent, well-paced, method-accurate, and professionally written; no obvious factual errors, awkward transitions, or missing subsections; the statement of need is convincing; the capability tour reads as a genuine breadth demonstration.
**Why human:** Prose quality, narrative cohesion, and scientific tone cannot be assessed by grep or spot-checks.
**Deferred to:** Phase 90 (GATE-04 blocking human read-through)

---

**Note on PDF compilation:** The tectonic PDF compile is CI-only (no local TeX assumed) per milestone design. All locally verifiable must-haves pass. The CI compilation is the Phase 90 GATE-04 backstop; this phase is `passed` on local evidence.

---

_Verified: 2026-09-09T08:00:00Z_
_Verifier: Claude (gsd-verifier)_
