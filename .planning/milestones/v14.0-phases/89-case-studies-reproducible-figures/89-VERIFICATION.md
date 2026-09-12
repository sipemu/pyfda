---
phase: 89-case-studies-reproducible-figures
verified: 2026-09-09T10:30:00Z
status: passed
score: 10/10
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Open paper/figures/cs1_phoneme_smooth.pdf and cs1_phoneme_fpca.pdf and confirm the smoothed curves correspond visually to the correct phoneme class shapes, and that the FPCA scatter shows credible class separation."
    expected: "Five class-coloured clusters visible in FPCA scatter; smoothed curves per class look phoneme-appropriate (no mixing of class shapes)."
    why_human: "Correctness of CR-01 (per-class selection) is code-verifiable; visual plausibility of the class shape separation is not — a figure could be technically correct but visually uninformative."
  - test: "Tectonic PDF compile in CI: confirm paper.yml green after a figure-regeneration push."
    expected: "CI step 'Assert figures byte-stable' exits 0; tectonic PDF compiles without warnings or missing-ref errors."
    why_human: "Tectonic PDF compile and cross-platform FreeType determinism are CI-only (deferred to Phase 90 close gate)."
---

# Phase 89: Case Studies + Reproducible Figures — Verification Report

**Phase Goal:** Four illustrative case studies, each a narrative worked example whose figures regenerate DETERMINISTICALLY and are committed under `paper/figures/`.
**Verified:** 2026-09-09T10:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | casestudy1.py runs smooth+FPCA+classification on phoneme; commits deterministic cs1_*.pdf; casestudy1.tex narrative exists | VERIFIED | Script exits 0, prints `CV accuracy: 0.863`; both PDFs committed; tex exists at `paper/sections/casestudy1.tex` |
| 2 | casestudy2.py runs registration+regression on tecator; cs2_*.pdf; casestudy2.tex | VERIFIED | Script exits 0, prints `train R2: 0.929`, `CV R2: 0.805`; both PDFs committed; tex exists |
| 3 | casestudy3.py runs FTS forecast on canadian_weather_precip; cs3_*.pdf; casestudy3.tex | VERIFIED | Script exits 0, prints `forecast shape: (3, 365)`, `forecast[0, :5]: [1.802 1.861 1.826 1.703 1.702]`; both PDFs committed; tex exists |
| 4 | casestudy4.py runs sklearn Pipeline+GridSearchCV on wine; cs4_*.pdf; casestudy4.tex | VERIFIED | Script exits 0, prints `best: {'fpca__n_components': 8} 0.961`; both PDFs committed; tex exists |
| 5 | Re-running gen_figures.py leaves `git diff paper/figures/` EMPTY (determinism gate) | VERIFIED | Two consecutive runs of gen_figures.py executed; `git diff --exit-code paper/figures/` returned exit 0 with no output |
| 6 | Determinism gate exists in Makefile (paper-verify target) + paper.yml (git diff step after regeneration, before tectonic) | VERIFIED | `paper-verify` target at Makefile:59–61; `Assert figures byte-stable` step at paper.yml:51–52, positioned after Regenerate (line 44), before Setup tectonic (line 74) |
| 7 | CR-01: casestudy1.py selects phoneme curves BY CLASS MEMBERSHIP | VERIFIED | Code uses `class_rows_pre = {cls: [...] for cls in uniq_pre}` + `selected = [idx for cls in uniq_pre for idx in class_rows_pre[cls][:4]]`; `sm["fitted"]` is ordered class-by-class so the `ci*4` offset in the plot loop is correct |
| 8 | CR-02: Study-1 CV accuracy consistent at 0.863/86.3% everywhere; no 88.2% remnant | VERIFIED | Live output prints `CV accuracy: 0.863`; casestudy1.tex body (line 39) and caption (line 64) both say "86.3%"; fold vector in tex `[0.850, 0.850, 0.863, 0.875, 0.875]` matches REAL OUTPUT comment; no "88.2" found anywhere |
| 9 | WR-01: FPCA variance fractions computed LIVE from pc["singular_values"]; tex values (69.3%/23.0%) match | VERIFIED | casestudy1.py:140–141 computes `prop_var = sv ** 2 / float(np.sum(sv ** 2))`; f-string axis labels use `round(float(prop_var[0]) * 100, 1)`; live output `Variance explained: [0.693, 0.23, 0.054, 0.023]` matches casestudy1.tex:29 `[69.3, 23.0, 5.4, 2.3]%` |
| 10 | WR-02: gen_figures.py imports casestudy2/3/4 DIRECTLY (no silent try/except ImportError) | VERIFIED | gen_figures.py:54–59: bare `import casestudy2; casestudy2.main()` etc. with no try/except; comment at line 52–53 confirms intent |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

---

### Prose/Script Number Consistency

| Study | Metric | Script live output | tex prose | Match |
|-------|--------|--------------------|-----------|-------|
| Study 1 | CV accuracy | 0.863 (86.3%) | 86.3% | MATCH |
| Study 1 | Fold scores | [0.850, 0.850, 0.8625, 0.875, 0.875] → rounded [0.850, 0.850, 0.863, 0.875, 0.875] | [0.850, 0.850, 0.863, 0.875, 0.875] | MATCH |
| Study 1 | FPCA variance PC1/PC2 | 69.3% / 23.0% | 69.3% / 23.0% | MATCH |
| Study 2 | Training R² | 0.929 | 0.929 | MATCH |
| Study 2 | CV mean R² | 0.805 | 0.805 | MATCH |
| Study 2 | Fold scores | [0.903, 0.405, 0.883, 0.922, 0.914] | [0.903, 0.405, 0.883, 0.922, 0.914] | MATCH |
| Study 3 | Forecast shape | (3, 365) | shape $(3, 365)$ | MATCH |
| Study 4 | Best CV accuracy | 0.961 at n=8 | 0.961 at 8 components | MATCH |
| Study 4 | Grid accuracy vector | [0.697, 0.759, 0.916, 0.961] | $0.697, 0.759, 0.916, 0.961$ | MATCH |

All prose numbers match their corresponding live script output. No fabricated or stale values found.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `paper/code/casestudy1.py` | Study-1 pipeline | VERIFIED | 166 lines; class-membership selection; live variance computation |
| `paper/code/casestudy2.py` | Study-2 pipeline | VERIFIED | 155 lines; karcher_mean + fregre_lm + FPCRegressor CV |
| `paper/code/casestudy3.py` | Study-3 pipeline | VERIFIED | 136 lines; ftsm + ftsm_forecast; Xfts transpose pattern |
| `paper/code/casestudy4.py` | Study-4 pipeline | VERIFIED | 161 lines; Pipeline + GridSearchCV + n_jobs=1 |
| `paper/code/gen_figures.py` | Orchestration driver | VERIFIED | Direct imports for casestudy1–4; no try/except swallow |
| `paper/figures/cs1_phoneme_smooth.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs1_phoneme_fpca.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs2_tecator_align.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs2_tecator_fit.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs3_precip_curves.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs3_precip_forecast.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs4_wine_gridsearch.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/figures/cs4_wine_scores.pdf` | Committed figure | VERIFIED | Present; byte-stable on re-run |
| `paper/sections/casestudy1.tex` | Study-1 narrative | VERIFIED | \subsection; two \includegraphics; all cites resolve |
| `paper/sections/casestudy2.tex` | Study-2 narrative | VERIFIED | \subsection; two \includegraphics; all cites resolve |
| `paper/sections/casestudy3.tex` | Study-3 narrative | VERIFIED | \subsection; two \includegraphics; honest shallow-sample caveat |
| `paper/sections/casestudy4.tex` | Study-4 narrative | VERIFIED | \subsection; \nsklearnestimators macro (no hardcoded 28); all cites resolve |
| `paper/sections/casestudies.tex` | Four-input shell | VERIFIED | \section + four \input lines; finalized |
| `Makefile paper-verify target` | Local determinism gate | VERIFIED | Two-step: regenerate → `git diff --exit-code paper/figures/` |
| `.github/workflows/paper.yml Assert byte-stable step` | CI determinism gate | VERIFIED | Step at line 51–52, ordered after Regenerate (44), before tectonic (74) |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `gen_figures.py` | `casestudy1.main()` | top-level `import casestudy1` + call in `main()` | WIRED | Lines 23, 51 |
| `gen_figures.py` | `casestudy2.main()` | direct `import casestudy2` in `main()` body | WIRED | Lines 54–55 (no try/except) |
| `gen_figures.py` | `casestudy3.main()` | direct `import casestudy3` in `main()` body | WIRED | Lines 56–57 (no try/except) |
| `gen_figures.py` | `casestudy4.main()` | direct `import casestudy4` in `main()` body | WIRED | Lines 58–59 (no try/except) |
| `casestudies.tex` | casestudy1–4.tex | `\input{sections/casestudyN}` | WIRED | All four \input lines present |
| `Makefile paper-verify` | `gen_figures.py` + git diff | `PYTHONPATH=... python paper/code/gen_figures.py && git diff --exit-code paper/figures/` | WIRED | Makefile:60–61 |
| `paper.yml Assert step` | committed figures | `git diff --exit-code paper/figures/` ordered after Regenerate, before tectonic | WIRED | Lines 51–52, 44, 74 |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| gen_figures.py exits 0 (all 4 studies run) | `PYTHONPATH=scripts:paper/code .venv/bin/python paper/code/gen_figures.py` | Exit 0; printed CV accuracy: 0.863, train R2: 0.929, forecast shape: (3, 365), best: 0.961 | PASS |
| Second run produces byte-identical figures | `PYTHONPATH=scripts:paper/code .venv/bin/python paper/code/gen_figures.py && git diff --exit-code paper/figures/` | Exit 0, no diff output | PASS |
| CR-02: casestudy1.py prints 0.863 (not 0.882) | live output above | `CV accuracy: 0.863` | PASS |
| WR-01: variance fractions are live (69.3%/23.0%) | live output above | `Variance explained: [0.693, 0.23, 0.054, 0.023]` | PASS |
| Study-4 best accuracy 0.961 at n=8 | live output above | `best: {'fpca__n_components': 8} 0.961` | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| CASE-01 | 89-01-PLAN.md | Study 1 — smooth + FPCA + classification on phoneme, reproducible figures | SATISFIED | casestudy1.py runs; cs1_*.pdf committed; casestudy1.tex complete |
| CASE-02 | 89-02-PLAN.md | Study 2 — registration + regression on tecator, reproducible figures | SATISFIED | casestudy2.py runs; cs2_*.pdf committed; casestudy2.tex complete |
| CASE-03 | 89-03-PLAN.md | Study 3 — FTS forecast on canadian_weather_precip, reproducible figures | SATISFIED | casestudy3.py runs; cs3_*.pdf committed; casestudy3.tex complete |
| CASE-04 | 89-04-PLAN.md | Study 4 — sklearn Pipeline + GridSearchCV on wine, reproducible figures | SATISFIED | casestudy4.py runs; cs4_*.pdf committed; casestudy4.tex complete |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | — | — | — |

No TBD/FIXME/XXX/PLACEHOLDER markers in any case-study `.py` or `.tex` file. No hardcoded count integers where macros exist. No benchmark claims. No dangling `\citep` keys (all 9 unique keys verified in `paper/refs.bib` or `paper/refs_manual.bib`). All `\includegraphics` paths resolve to committed files.

---

### Human Verification Required

The following items require human review before Phase 90 close. They do not block Phase 89 completion per the Phase 86–88 precedent (CI-only gates deferred to Phase 90).

#### 1. Visual plausibility of Study-1 class separation figures

**Test:** Open `paper/figures/cs1_phoneme_smooth.pdf` and `cs1_phoneme_fpca.pdf` and inspect them.
**Expected:** Smoothed curves per class show class-appropriate spectral shapes (CR-01 was code-verified; visual confirmation is the final check). FPCA scatter shows five distinct clusters.
**Why human:** CR-01 fix is code-verifiable by inspecting the selection logic, but visual plausibility of the class shape separation cannot be confirmed programmatically.

#### 2. Tectonic PDF compile passes in CI

**Test:** Verify that the `paper.yml` CI run is green after the Phase 89 commits are present (tectonic compile step).
**Expected:** PDF compiles without missing-reference errors; all four `\input{sections/casestudyN}` resolve.
**Why human:** Tectonic and cross-platform FreeType determinism are CI-only per the Phase 86–88 precedent; deferred to Phase 90 close gate.

---

### Post-Review Fix Confirmation

The code review (89-REVIEW.md, 2026-09-09) found 2 critical and 4 lower-severity issues. All 6 were fixed in commit f9fc58c (CR-01/CR-02/WR-01), f769246 (WR-02), and 73bba5d (IN-01/IN-02).

| Finding | Fix Applied | Verified |
|---------|-------------|---------|
| CR-01: wrong phoneme class curves in figure | Per-class index selection via `class_rows_pre` dict | VERIFIED — code inspected, logic correct, figures regenerated deterministically |
| CR-02: 88.2% vs 86.3% accuracy conflict | Reconciled to live value 0.863/86.3%; tex fold vector updated | VERIFIED — no "88.2" found anywhere; live output 0.863 confirmed |
| WR-01: hardcoded variance fractions | Live computation from `pc["singular_values"]` | VERIFIED — `prop_var = sv**2 / sum(sv**2)` present at line 141 |
| WR-02: silent ImportError swallow in gen_figures.py | Direct imports, no try/except | VERIFIED — gen_figures.py:52–59 confirmed |
| IN-01: double ftsm fit comment | Explanatory comment added | VERIFIED — no correctness impact |
| IN-02: independent FPCATransformer note | Equivalence comment added | VERIFIED — no correctness impact |

---

### Gaps Summary

No gaps found. All 10 must-have truths verified against the codebase with concrete command output. The two human verification items (visual figure check, CI PDF compile) are backstop items deferred to Phase 90 per the established milestone pattern — they do not block Phase 89 completion.

---

_Verified: 2026-09-09T10:30:00Z_
_Verifier: Claude (gsd-verifier)_
