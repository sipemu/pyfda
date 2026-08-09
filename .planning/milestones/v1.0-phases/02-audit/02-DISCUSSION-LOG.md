# Phase 2: Audit - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-07
**Phase:** 2-Audit
**Areas discussed:** Classification taxonomy, Method-accuracy depth, Audit artifact shape, Gaps + new-examples

---

## Classification Taxonomy

| Option | Description | Selected |
|--------|-------------|----------|
| Two-axis + rollup | Score each diagram on style (conforms/legacy-outlier) and accuracy (accurate/inaccurate); missing for diagram-less pages; derive ROADMAP's flat label as a rollup column | ✓ |
| Flat 3-bucket | accurate / inconsistent / missing exactly as ROADMAP states; 'inconsistent' lumps style + method | |
| You decide | Claude picks the rubric | |

**User's choice:** Two-axis + rollup
**Notes:** Separates restyle (legacy-outlier + accurate) from redraw (inaccurate) — different sweep effort. Claude added: make the style axis grep-checkable (viewBox 720, five CSS classes, role/aria-label) so it's reproducible.

---

## Method-Accuracy Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Inspect + flag | Expert inspection; record needs-method-verification flags; resolve during the sweep | |
| Verify-now for flagged | Run fdars for conformal/scalar-on-function/SPM diagrams during the audit to lock ground truth | |
| You decide | Claude chooses per-diagram | ✓ |

**User's choice:** You decide
**Notes:** Recorded default = inspect-and-flag to keep audit MVP-sized; Claude may run a quick fdars sanity check only where cheap and decisive to avoid mis-scoping a sweep target; full verification defers to Phases 7–8.

---

## Audit Artifact Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Single master MD | One .planning/phases/02-audit/02-AUDIT.md: coverage table + grep report + ranked gap/example list | ✓ |
| Machine-readable + summary | YAML/JSON coverage map plus human MD summary | |
| Per-section files | One audit file per doc section | |
| You decide | Claude picks format | |

**User's choice:** Single master MD
**Notes:** One git-diffable source of truth; each sweep reads its section's rows.

---

## Gaps + New-Examples

### Coverage denominator ("warrants a diagram" rule)

| Option | Description | Selected |
|--------|-------------|----------|
| Concept pages, judged per-page | Six method sections; each page marked warrants-a-diagram yes/no with reason; reference/ and index pages excluded unless overview helps | |
| All nav content pages | Every non-reference page uniformly warrants a diagram | |
| You decide | Claude applies judgment | ✓ |

**User's choice:** You decide
**Notes:** Recorded default = concept-pages-judged-per-page; reference/ API pages and section index pages excluded unless an overview diagram clearly helps.

### New worked-example sourcing & ranking

| Option | Description | Selected |
|--------|-------------|----------|
| Widen then rank; 5 as baseline | Phase 9's five locked as baseline; reference-API sweep surfaces extra candidates; ranked list; user selects | |
| Reconfirm the 5 only | Validate the five named in Phase 9; no widening | |
| You decide | Claude chooses how far to widen and how to rank | ✓ |

**User's choice:** You decide
**Notes:** Recorded default = widen-then-rank with the five as the locked baseline; reference-API coverage sweep adds optional candidates; ranking by coverage-gap / method centrality / authoring effort; user selects at the in-document gate before Phase 3.

---

## Claude's Discretion

- Method-accuracy escalation boundary (D-04): inspect-and-flag default, cheap-and-decisive fdars checks allowed.
- Coverage denominator: concept pages in the six method sections, judged per-page.
- New-example sourcing & ranking: widen-then-rank, Phase 9's five as baseline.

## Deferred Ideas

- Actually fixing diagrams / removing R-era content / writing new examples — Phases 3–9.
- Full method-semantic verification (β(t), conformal bands, SPM I/II) — Phases 7–8.
- A11Y-01 (long-form title/desc + aria-labelledby) — v2.
- EX2-01 (editorial consolidation of overlapping example pages) — v2.
