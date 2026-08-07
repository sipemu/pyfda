# Phase 2: Audit Master Document

**Phase:** 02-audit
**Date:** 2026-08-07
**Status:** In progress — learn/ section complete; remaining sections populated by Plans 02–03.

## Purpose

This document is the single git-diffable source of truth for the Phase 2 audit. It scopes all diagram-sweep phases (Phases 3–9) by providing:

1. A **Page→Diagram Coverage Table** — classifying every nav content page on two independent axes (style, accuracy) plus a rollup label.
2. An **R-era Grep Report** — every R-era hit with file:line, grouped by section.
3. A **Ranked Gap + New-Example List** — user-selectable candidates (GAP-#### for coverage/style/accuracy gaps; EX-#### for new-example candidates).

### D-02 Rollup Rule (explicit)

For each page with a diagram:
- **`accurate`** — BOTH axes clean: style axis = `conforms` AND accuracy axis = `accurate`.
- **`inconsistent`** — at least one axis is off: style is `legacy-outlier` OR accuracy is `inaccurate/misleading` (or both).
- **`missing`** — no diagram exists for a page that warrants one.

This two-axis detail exists so sweeps can distinguish a **restyle** (legacy-outlier but accurate, lower effort) from a **redraw** (inaccurate, higher effort).

### D-06 Selection Gate

The `Selection` column in Section 3 is blank by default. **The user marks it before Phase 3 begins.** Phase 3 planning reads only the selected items.

---

## 1. Page→Diagram Coverage Table

**Columns:** `Page` | `Diagram` | `Style axis` | `Accuracy axis` | `Rollup` | `Warrants diagram?` | `Needs method-verification`

**Style-axis verdicts are grep-reproducible** against `docs/assets/diagrams/*.svg` by checking:
- `viewBox="0 0 720` — width 720 (grep: `viewBox="0 0 720`)
- Five CSS classes: `.ttl`, `.sub`, `.lab`, `.sm`, `.mono` (grep each in the `<style>` block)
- `system-ui` font stack (grep: `system-ui`)
- `role="img"` and `aria-label` on the root `<svg>` element

`conforms` = all markers present. `legacy-outlier` = one or more markers absent (with names of failing markers recorded).

### learn/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| learn/introduction.md | introduction.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — three-panel input→Fdata→output flow correctly depicts the constructor call `Fdata(X, argvals)` and the resulting curve family. Dots in Panel 1 represent raw point observations; Panel 3 shows multiple curves with a mean highlighted. Matches API semantics. | accurate | yes — essential orientation diagram showing the core abstraction (raw data → functional object) that the whole library rests on. | — |
| learn/custom-plotting.md | custom-plotting.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — the diagram correctly shows that fdars provides no built-in plot layer (the text caption states this explicitly) and the three panels show the matplotlib workflow: plain curve set → `ax.plot(...)` idioms → styled figure with mean±sd band and median. Consistent with the page's content. | accurate | yes — the page is explicitly a plotting recipe guide; an overview diagram anchoring the matplotlib workflow adds clear value. | — |
| learn/simulation.md | simulation.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — KL parameters panel shows basis eigenfunctions (φ₁ φ₂ φ₃) and a λ-decay bar chart; method panel names `simulate()`, KL expansion, and gaussian_process; output panel shows a family of random curves. Faithfully depicts the Karhunen-Loève simulation pipeline. | accurate | yes — simulation is a technical entry point; showing the KL parameter→sampling pipeline prevents misuse. | — |
| learn/smoothing.md | smoothing.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | inaccurate/misleading — **FINDING CONFIRMED with evidence.** Panel 3 ("Smooth Curve") draws a faint ghost path (the "before" reference) that reuses the noisy coordinates from Panel 1 verbatim, shifted only by 8 px in y. Panel 1 (line 18): `M0 92 L8 70 L16 100 L24 62 ... L156 58`. Panel 3 ghost (line 48): `M0 84 L8 70 L16 100 L24 62 ... L156 58`. Sequences from L8 onward are identical — the Panel 3 ghost is not an independently drawn noisy reference; it is a copy of the jagged polyline from Panel 1. The smooth curve itself (line 49, a cubic Bézier) is correct, but the ghost underlay misrepresents what the noisy data looks like on the smoothed-output panel. Needs a **redraw** (replace the ghost polyline with a path whose coordinates genuinely differ from Panel 1, or remove the ghost entirely). | inconsistent | yes — smoothing is the foundational pre-processing step; a concept diagram is essential. Current diagram warrants a redraw (accuracy axis fails). | — |
| learn/derivatives.md | derivatives.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a monotone rising curve x(t); Panel 2 names `fd.deriv(nderiv)` with nderiv=1→velocity, nderiv=2→accel.; Panel 3 shows two sub-panels with x'(t) velocity and x''(t) acceleration curves with visually appropriate shapes (velocity increasing, acceleration with an inflection). Consistent with finite-differences semantics. | accurate | yes — distinguishing the level, velocity, and acceleration interpretation is non-obvious and frequently misunderstood; the diagram adds clear pedagogical value. | — |
| learn/irregular-sampling.md | irregular-sampling.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows two curves with points on uneven individual grids (different x-positions per curve, tick marks showing the irregular spacing); Panel 2 names the pipeline (kernel smoother → basis expansion → evaluate on common grid); Panel 3 shows the result: curves on a regular shared grid with dots at the common grid points. Faithfully depicts the smooth→regrid operation. | accurate | yes — irregular sampling is a common real-world complication; showing the ragged→common-grid transform is essential to the page's concept. | — |
| learn/index.md | — | — | — | — | no — the learn/ landing page is a section index listing page links. An overview diagram is not warranted; navigation tiles serve the same orientation purpose. | — |

---

## 2. R-era Grep Report

**Scope:** `docs/assets/diagrams/*.svg` AND `docs/**/*.md` (all sections including `reference/` and `examples/`). Patterns searched: `extendr`, `autoplot`, `ggplot`, `%>%`, `<-` (R assignment), `library(`, `require(`, R package names (`fda`, `dplyr`, `tidyr`, `purrr`, `magrittr`, `ggplot2`), `.R` file extension references.

Full cross-section report (all sections) is produced in Plan 03. Here, only the **learn/** section is filled; the scope statement and format are fixed for Plans 02–03 to expand into.

### learn/

**Diagrams** (`docs/assets/diagrams/introduction.svg`, `custom-plotting.svg`, `simulation.svg`, `smoothing.svg`, `derivatives.svg`, `irregular-sampling.svg`):

(no R-era hits in learn/ diagrams)

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/learn/introduction.md | 52 | `mirroring the R package's \`fdata\`` | Legitimate narrative prose — explaining the conceptual origin of the `Fdata` class. Not an R-era leftover to remove; it is an intentional cross-reference explaining fdars's design lineage. |
| docs/learn/introduction.md | 81 | `It mirrors the R package's \`fdata\` S3 class.` | Same as above — intentional design explanation. Retain. |
| docs/learn/introduction.md | 238 | `Unlike R's \`var(fd)\`, fdars does not expose...` | Intentional API comparison note informing Python users. Retain. |
| docs/learn/introduction.md | 567 | `Functional Data Analysis: The R Package \`fda.usc\`. *Journal of Statistical Software*` | Citation in references section for the fda.usc R package. Standard academic citation. Retain. |
| docs/learn/custom-plotting.md | 13 | `mirrors the ggplot2 walkthrough from the R package` | Intentional narrative comparison — the page explicitly translates R/ggplot2 plotting idioms to matplotlib. This ggplot2 mention is the page's stated purpose. **Warrants review**: the page frames its own content as a "translation from ggplot2" which may be R-era framing rather than Python-first authoring. Not a remove-immediately item but flagged for editorial review during the learn/ sweep (Phase 3). |
| docs/learn/custom-plotting.md | 67 | `because ggplot2 maps *columns* of a data frame to aesthetics` | Same page, same framing — part of the ggplot2→matplotlib translation narrative. See above flag. |
| docs/learn/custom-plotting.md | 88 | `This is the matplotlib translation of ggplot2's \`color = group\` aesthetic` | Same. |
| docs/learn/custom-plotting.md | 128 | `In ggplot2 this is \`scale_color_viridis_c\`` | Same. |

**Summary for learn/:** No SVG diagrams have R-era hits. Introduction.md has R-era references that are intentional design-lineage and citation prose — all retain. custom-plotting.md uses ggplot2 extensively as a comparative framing device — the ggplot2 mentions are intentional but the page's overall R-first framing warrants an editorial note for the Phase 3 learn/ sweep. No `extendr`, `autoplot`, `%>%`, or hard R code identifiers appear anywhere in learn/.

---

## 3. Ranked Gap + New-Example List

### ID Schemes

- **`GAP-####`** — a coverage, style, or accuracy gap: a page that warrants a diagram but has none (`missing`), a diagram whose rollup is `inconsistent` (style or accuracy fails), or a significant documentation gap surfaced during section sweeps.
- **`EX-####`** — a new worked example candidate: a capability or method that lacks a worked example and would benefit from one.
- **`Selection`** column — **left blank here; marked by the user before Phase 3 begins** (D-06). Options: `selected`, `deferred`, `dropped`, or `[baseline-locked]` for the five Phase 9 examples.

The reference-API coverage sweep (Plan 03) populates additional EX-#### rows. The ranking signals below apply to all items:
1. Capability has zero accurate diagram AND zero worked example (highest urgency).
2. Method centrality / user value (core methods first).
3. Authoring effort (lower effort → earlier).

### Ranked List

| ID | Type | Section | Description | Priority signals | Selection |
|----|------|---------|-------------|-----------------|-----------|
| GAP-0001 | accuracy gap | learn/ | `smoothing.svg` — Panel 3 ghost path reuses Panel 1's noisy coordinates verbatim (confirmed: smoothing.svg:48 vs smoothing.svg:18, sequences from L8 onward identical). The diagram currently misrepresents what the noisy reference looks like against the smooth output. Needs a **redraw** of the ghost path (or removal). | (1) Only diagram for a foundational concept page; (2) confirmed inaccuracy undermines the page's teaching purpose; (3) ghost path fix is a small authoring change. | |
| EX-0001 | new example | Phase 9 (baseline-locked) | **Conformal Coverage Guarantee** — end-to-end demonstration of `fdars.conformal` producing a time-varying prediction band `ŷ(t)±q(t)` with guaranteed coverage, contrasted against a naive scalar interval. | Baseline-locked for Phase 9. | [baseline-locked] |
| EX-0002 | new example | Phase 9 (baseline-locked) | **Function-on-Scalar Regression** — worked example using `fdars.regression.function_on_scalar` to model a functional response from scalar predictors, foregrounding the `β(t)` coefficient curve interpretation. | Baseline-locked for Phase 9. | [baseline-locked] |
| EX-0003 | new example | Phase 9 (baseline-locked) | **Outlier-Detection Workflow** — end-to-end example using `fdars.outliers` to identify functional outliers, with interpretation guidance (magnitude vs shape outliers). | Baseline-locked for Phase 9. | [baseline-locked] |
| EX-0004 | new example | Phase 9 (baseline-locked) | **Tolerance Bands vs Conformal Comparison** — side-by-side comparison of `fdars.tolerance` and `fdars.conformal` bands, illustrating the distributional vs coverage-guarantee distinction. | Baseline-locked for Phase 9. | [baseline-locked] |
| EX-0005 | new example | Phase 9 (baseline-locked) | **Functional Depth Centrality Ordering** — example using `fdars.depth` functions (Fraiman-Muniz, Modified Band) to rank curves by centrality, with a visualization of the depth ordering. | Baseline-locked for Phase 9. | [baseline-locked] |

*Rows EX-0006 onwards and additional GAP-#### rows will be added by Plans 02–03 after the reference-API sweep and remaining section audits.*
