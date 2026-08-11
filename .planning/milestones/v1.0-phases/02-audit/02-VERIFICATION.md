---
phase: 02-audit
verified: 2026-08-07T00:00:00Z
status: passed
score: 3/3 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 2: Audit Verification Report

**Phase Goal:** An evidence-based, user-selectable list of diagram coverage gaps and new-example candidates is produced from a systematic nav + API sweep.
**Verified:** 2026-08-07
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | A written audit document maps every page in the nav to its diagram(s) and classifies each as accurate, inconsistent, or missing — no page is omitted. | VERIFIED | All 42 method-section content pages confirmed present (grep check: 6 learn/ + 7 represent/ + 6 align/ + 12 regression/ + 3 monitoring/ + 8 analyze/ = 42/42). Each row carries the 7-column schema and a rollup label. All 6 index pages included and judged. |
| 2 | The audit document contains a grep report that flags all R-era content (extendr, autoplot, R-specific identifiers) found in diagrams and prose, with file locations. | VERIFIED | §2 covers all sections including reference/ and examples/. spm.svg lines 5, 31, 55, 56 confirmed by direct file inspection. LEFTOVER vs PROSE-OK annotation present throughout. Grep commands documented and reproducible. 6/6 preliminary findings reconciled. |
| 3 | The audit produces a ranked list of diagram coverage gaps and new-example candidates that the user can select from before Phase 3 begins. | VERIFIED | §3 contains 11 GAP-#### rows + 8 EX-#### rows (EX-0001..EX-0005 baseline-locked, EX-0006..EX-0008 additive). Each row carries three ranking signals (zero-example/zero-accurate-diagram, method centrality, authoring effort) and a priority rank (P1-P4). Selection column present and blank for user to mark. User instruction at top of §3 per D-06. |

**Score:** 3/3 truths verified

---

### Completeness check (AUD-01): nav cross-reference

mkdocs.yml nav method-section content-page count:
- learn/: 6 (introduction, custom-plotting, simulation, smoothing, derivatives, irregular-sampling)
- represent/: 7 (fpca, elastic-fpca, basis-representation, andrews-transformation, depth-functions, streaming-depth, distance-metrics)
- align/: 6 (elastic-alignment, advanced-alignment, landmark-registration, tsrvf, alignment-comparison, shape-analysis)
- regression/: 12 (scalar-on-function, function-on-scalar, classification, elastic-regression, scalar-on-shape, cross-validation, regression-diagnostics, uncertainty-quantification, explainability, conformal-prediction, conformal-classification, robust-regression)
- monitoring/: 3 (spm, advanced-spm, profile-partial-monitoring)
- analyze/: 8 (tolerance-bands, clustering, gmm-clustering, elastic-clustering, outlier-detection, seasonal-analysis, equivalence-testing, covariance-functions)

**Total: 42 content pages. All 42 confirmed present in coverage table by grep. No page omitted.**

Index pages (6, one per section) are each present as a separate row with a "no — not warranted" verdict.

### 7-column schema (AUD-01 / D-01/D-02/D-04)

Column header confirmed: `Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification`

Present in every section sub-table header row. D-02 rollup rule explicitly stated in preamble: accurate (both axes clean), inconsistent (either axis off), missing (no diagram + warranted).

### Style-axis grep-reproducibility (D-03)

Spot-checked smoothing.svg and introduction.svg against claimed verdicts:
- smoothing.svg: viewBox `0 0 720 300`, role=img, aria-label, .ttl/.sub/.lab/.sm/.mono CSS classes, system-ui — all present. Verdict `conforms` in audit is correct.
- introduction.svg: identical STYLE_SPEC markers — all present. Verdict `conforms` correct.

The audit records the five marker checks per row by name, making verdicts reproducible by grep. No verdicts were eyeballed without evidence.

### Rollup label consistency (D-02)

Spot-checked across sections:
- smoothing.md: style=`conforms`, accuracy=`inaccurate/misleading` → rollup=`inconsistent`. Correct per D-02.
- clustering.md: style=`legacy-outlier`, accuracy=`accurate` → rollup=`inconsistent`. Correct per D-02.
- conformal-prediction.md: style=`conforms`, accuracy=`inaccurate/misleading` → rollup=`inconsistent`. Correct per D-02.
- equivalence-testing.md: style=`conforms`, accuracy=`accurate` → rollup=`accurate`. Correct per D-02.
- spm.md: style=`legacy-outlier`, accuracy=`inaccurate/misleading` → rollup=`inconsistent`. Correct per D-02.

No rollup label was found inconsistent with its two axes.

### Smoothing.svg coordinate-reuse finding (AUD-01 specifics)

The audit claims:
- Panel 1 (line 18): `M0 92 L8 70 L16 100 L24 62 ...`
- Panel 3 ghost (line 48): `M0 84 L8 70 L16 100 L24 62 ...`

Direct file inspection confirmed both lines exactly as claimed. From L8 onward (segment `L8 70`) the coordinate sequences are identical — the ghost path in Panel 3 is a verbatim copy of the Panel 1 noisy polyline. Finding is correctly recorded with file:line evidence.

### R-era report: spm.svg lines 5, 31, 55, 56 (AUD-02)

All four LEFTOVER claims verified by direct file inspection:
- Line 5: `Functional Data Analysis in R, powered by Rust` — exact match
- Line 31: `autoplot() — visualization` — exact match (HTML entity `&#x2014;` is em-dash)
- Line 55: `Rust Backend (extendr)` — exact match
- Line 56: `zero-copy R ↔ Rust` embedded in longer text element — confirmed present

The audit's four LEFTOVER annotations for spm.svg are correct. No other file in the codebase carries genuine R-era leftovers.

### Six preliminary findings reconciliation (AUD-02)

| Finding | Audit verdict | Verification |
|---------|--------------|--------------|
| spm.svg autoplot + extendr | CONFIRMED — spm.svg:31 and :55 | VERIFIED by file inspection |
| basis-representation.svg R-era | NOT FOUND — all text uses Python fdata_to_basis_1d | CONSISTENT with preliminary finding being wrong; audit correctly notes this |
| elastic-alignment.svg phase/amplitude split | CONFIRMED (needs verification) — warp inset at :55-61 present but small | VERIFIED as captured with file:line |
| conformal-prediction.svg scalar interval | CONFIRMED — output panel :54-62 shows scalar constant band | VERIFIED — finding captured with line references and specific text |
| scalar-on-function.svg β(t) prominence | CONFIRMED (partial) — β̂(t) inset at :59-64 present but secondary | VERIFIED as captured with file:line |
| smoothing.svg coordinate reuse | CONFIRMED — :18 vs :48, sequences from L8 identical | VERIFIED by direct line inspection |

### Ranked list (AUD-03)

- 11 GAP-#### rows (GAP-0001..GAP-0011), each with type (restyle/redraw/verify/accuracy gap), tracing to a §1 coverage row with rollup `inconsistent` or (implicitly) `missing`.
- 8 EX-#### rows: EX-0001..EX-0005 marked `[baseline-locked]`; EX-0006..EX-0008 have blank Selection for user to mark.
- Three ranking signal columns present: zero-example/zero-accurate-diagram, method centrality/user value (high/med/low), authoring effort (low/med/high).
- Priority rank column (P1-P4) present; table sorted P1 → P4.
- D-06 user instruction present at top of §3: "mark the Selection column in this document before Phase 3 begins."

### Reference-API coverage sweep (AUD-03 / Plan 03 Task 2)

All 16 reference modules from mkdocs.yml nav (fdata, depth, metric, basis, smoothing, clustering, regression, alignment, outliers, seasonal, spm, classification, tolerance, conformal, simulation, explain) appear as rows in the API coverage sweep sub-table. Each row contains: module, key capabilities, has-example?, has-accurate-diagram?, under-documented capabilities. 17 example pages confirmed in mkdocs.yml — count matches the sweep's stated coverage base.

### Codebase purity (read-only audit constraint)

`git diff --name-only 8d7a71d HEAD` shows only `.planning/` files modified:
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/02-audit/02-01-SUMMARY.md`
- `.planning/phases/02-audit/02-02-SUMMARY.md`
- `.planning/phases/02-audit/02-03-SUMMARY.md`
- `.planning/phases/02-audit/02-AUDIT.md`

No files under `docs/` were modified. The constraint is satisfied.

### Requirements coverage

| Requirement | Phase | Status | Evidence |
|-------------|-------|--------|---------|
| AUD-01 | Phase 2 | SATISFIED | Coverage table covers all 42 content pages with 7-column schema, D-02 rollup, grep-reproducible style axis |
| AUD-02 | Phase 2 | SATISFIED | Full R-era grep report with file:line, LEFTOVER/PROSE-OK, all sections including reference/ and examples/, 6/6 findings reconciled |
| AUD-03 | Phase 2 | SATISFIED | Ranked user-selectable list with 11 GAPs + 8 EX candidates, 3 ranking signals, Selection column, 16-module API sweep |

### Anti-patterns

No anti-patterns found. The artifact is a planning document; no TBD/FIXME/XXX markers, no stubs, no placeholder prose.

---

## Minor observation (non-blocking)

The spm.svg line 56 LEFTOVER claim in the audit ("zero-copy R ↔ Rust") is the text fragment within a longer `<text>` element that also contains "10–200x speedups", "nalgebra linear algebra", "rayon parallelism". The audit quotes the R-era phrase correctly; the full element contains additional non-R-era content. This is immaterial because the audit's intent is to flag the element for removal as part of the full Phase 8 redraw, which is correct.

---

## Human Verification Required

None — this is a documentation audit artifact. All success criteria are verifiable against the codebase without running the application.

---

_Verified: 2026-08-07_
_Verifier: Claude (gsd-verifier)_
