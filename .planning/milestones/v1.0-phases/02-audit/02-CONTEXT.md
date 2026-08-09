# Phase 2: Audit - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce the evidence-based audit artifact that scopes Phases 3–9. Nothing user-visible on the site changes in this phase — the deliverable is a written audit document. Locked by ROADMAP success criteria AUD-01..AUD-03:

1. A page→diagram coverage map covering **every** nav page — no page omitted — classifying each diagram.
2. A grep report flagging all R-era content (`extendr`, `autoplot`, R-specific identifiers) across diagrams and prose, with file:line locations.
3. A **ranked, user-selectable** list of diagram coverage gaps and candidate new worked examples that the user picks from **before Phase 3 begins**.

This phase clarifies HOW to build the audit; the WHAT is fixed by the roadmap. Fixing diagrams/examples is the domain of Phases 3–9, not this phase. New capabilities belong in other phases.

</domain>

<decisions>
## Implementation Decisions

### Classification Taxonomy (AUD-01)
- **D-01:** Classify each existing diagram on **two independent axes**: (a) **style** — `conforms` vs `legacy-outlier` (off-spec viewBox / fonts / palette / missing accessibility attrs vs STYLE_SPEC.md), and (b) **accuracy** — `accurate` vs `inaccurate/misleading` (does the SVG faithfully depict what the method does). Pages that warrant a diagram but have none = `missing`. — **Reversibility:** reversible.
- **D-02:** Derive the ROADMAP's flat label (`accurate` / `inconsistent` / `missing`) as a **rollup column** from the two axes, so success criterion #1 is still literally satisfied. Rollup rule: `missing` if no diagram; else `accurate` only if BOTH axes are clean (conforms + accurate); else `inconsistent`. The two-axis detail exists so the sweeps can tell a **restyle** (legacy-outlier but accurate) apart from a **redraw** (inaccurate) — very different fix effort.
- **D-03:** Make the **style axis grep-checkable/reproducible**, not eyeballed: check each SVG for the STYLE_SPEC markers — `viewBox="0 0 720 ..."` (width 720), presence of the five CSS classes (`.ttl/.sub/.lab/.sm/.mono`), system-ui fonts, and `role="img"` + `aria-label`. Record which markers fail per diagram. (The Phase 1 SVGO gate is optimization-only and does NOT enforce STYLE_SPEC conformance — this audit is the mechanism that catalogs off-spec style.)

### Method-Accuracy Verification Depth (AUD-01)
- **D-04:** Default to **inspect-and-flag**: judge accuracy by expert inspection of each SVG against method knowledge. Where accuracy genuinely cannot be settled by eye, record a **`needs method-verification` flag** naming exactly what to check (e.g. "confirm conformal band is time-varying `ŷ(t)±q(t)` against `fdars.conformal`", "confirm scalar-on-function shows `β(t)` curve", "confirm SPM shows distinct Phase I / Phase II limits"). The flagged verification is **resolved during that section's sweep**, not now. Keeps the audit MVP-sized.

### Claude's Discretion
- **Accuracy-check escalation (D-04 boundary):** user said "you decide." Claude MAY run a quick `fdars` sanity check during the audit for a specific flagged diagram **only where it is cheap and decisive** — i.e. where a 5-minute check prevents mis-scoping a sweep target. Otherwise inspect-and-flag and defer full verification to the sweep. Do NOT turn the audit into a verification pass over all method-semantic diagrams.
- **Coverage denominator ("warrants a diagram" rule):** user said "you decide." Default: denominator = every **content page in the six method sections** (learn/represent/align/analyze/regression/monitoring). For each such page the audit records **`warrants a diagram? yes/no` + a one-line reason**, so `missing` only counts pages that genuinely warrant one. **Exclude** the auto-generated `reference/` API pages and section `index.md` landing pages **unless** an overview diagram clearly helps (judged per-page, noted with reason). Reference pages still appear in the R-era grep report (D-08).
- **New-example sourcing & ranking:** user said "you decide." Default: treat **Phase 9's five named examples as the committed baseline** (conformal coverage guarantee, function-on-scalar regression, outlier-detection workflow, tolerance-bands vs conformal comparison, functional depth centrality ordering). Run a **reference-API coverage sweep** — documented/exampled capabilities vs `fdars` exported functions across the 16 reference modules — to surface additional under-documented capabilities as **optional candidates**. Present ONE ranked list (baseline five + extras). Suggested ranking signals: (1) capability has zero worked example / zero accurate diagram, (2) method centrality / user value, (3) authoring effort. The five stay locked; extras are the user's to accept or drop at the selection gate.

### Audit Artifact Shape (AUD-01..AUD-03)
- **D-05:** The audit is a **single master Markdown file** at `.planning/phases/02-audit/02-AUDIT.md`. One git-diffable source of truth; each sweep reads its section's rows. Contents:
  1. **Page→diagram coverage table** — one row per nav content page: page path, diagram file (if any), style axis, accuracy axis, rollup label, `warrants a diagram?`, and any `needs method-verification` flag.
  2. **R-era grep report** — every hit with `file:line` (D-08).
  3. **Ranked gap + new-example list** — the user-selectable section (D-06, D-07).
- **D-06:** The ranked list is **user-selectable in-document**: give each gap/candidate a stable ID and a priority/selection column the user marks before Phase 3. Phase 3's plan-phase reads the selected set. — **Reversibility:** reversible.

### R-era Grep Report (AUD-02)
- **D-08:** Grep scope covers **both diagrams and prose** — i.e. `docs/assets/diagrams/*.svg` AND `docs/**/*.md` (all sections including `reference/` and `examples/`). Patterns: `extendr`, `autoplot`, and other R-specific identifiers (e.g. `ggplot`, `%>%`, `<-` assignment, R package names) at Claude's discretion. Report every hit as `file:line` with the matched text, grouped by section so each sweep can find its own R-era removals.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase spec & scope
- `.planning/ROADMAP.md` §"Phase 2: Audit" — the three success criteria (AUD-01..AUD-03) that define done; also §Phases 3–9 for the diagram/example findings the audit must confirm and systematize (smoothing coordinate bug, R-era in basis-representation/spm, phase-vs-amplitude split, legacy outliers, conformal band redraw, β(t)).
- `.planning/REQUIREMENTS.md` §Foundation/Audit — AUD-01, AUD-02, AUD-03 text and the DIA-01..DIA-06 section-sweep definitions (what each sweep expects the audit to have scoped).
- `.planning/PROJECT.md` — milestone intent, Out-of-Scope (no programmatic diagrams; no fdars code changes), Key Decisions table (evidence-based scope, review gate per section).

### The conformance yardstick (from Phase 1)
- `docs/assets/diagrams/STYLE_SPEC.md` — the palette, five CSS classes, viewBox-720 convention, stroke weights, accessibility attrs. The style axis (D-01/D-03) is measured against this.
- `.planning/phases/01-foundation/01-CONTEXT.md` — Phase 1 decisions; note D-03 there: STYLE_SPEC conformance is a **human review-gate** concern, not machine-enforced by the SVGO gate — which is exactly why this audit must catalog it.

### What the audit sweeps
- `mkdocs.yml` §`nav:` — the authoritative page list the coverage map must cover in full (learn/represent/align/analyze/regression/monitoring/examples/reference). No page omitted (AUD-01).
- `docs/assets/diagrams/` — the 43 `.svg` diagrams to classify (plus `STYLE_SPEC.md`; there are also `cards/` and `thumb/` subdirs per PROJECT.md).
- `docs/**/*.md` — the concept/example/reference pages for the coverage map and the R-era grep (D-08).
- Reference API surface: the 16 `reference/*.md` pages + the `fdars` exported functions (see `.planning/codebase/STRUCTURE.md` / `src/*_mod.rs`, `python/fdars/`) for the reference-API coverage sweep that sources new-example candidates.

### Codebase maps
- `.planning/codebase/` — ARCHITECTURE, STRUCTURE, STACK, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS (STRUCTURE + INTEGRATIONS most relevant for mapping nav↔diagram↔module).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/STYLE_SPEC.md` (Phase 1) — the concrete conformance spec the style axis is scored against; its grep-able markers (viewBox 720, five classes, role/aria) drive D-03.
- `mkdocs.yml` §`nav:` — already enumerates every page; the coverage-map denominator derives directly from it. Six method sections + examples + reference already grouped.
- 43 existing diagrams in `docs/assets/diagrams/` — the classification population. Filenames map 1:1 to concept pages (e.g. `smoothing.svg` ↔ `learn/smoothing.md`), which makes the page→diagram join mostly mechanical.

### Established Patterns
- Diagrams referenced in pages as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }` — grep for this pattern to build the page→diagram join and detect pages with no diagram.
- Roadmap Phases 3–9 already encode a **preliminary** audit (specific bugs and R-era hits per section). The audit's job is to make that systematic, evidence-based, and complete — confirm each pre-identified finding with file:line and surface anything missed, not to re-invent from scratch.

### Integration Points
- Output `02-AUDIT.md` is consumed by every subsequent sweep's plan-phase (Phases 3–9) — its section rows and selected-gap IDs are the input scope for those phases.
- The user-selection gate (D-06) sits between this phase and Phase 3: Phase 3 planning must read the user's selections from `02-AUDIT.md`.

</code_context>

<specifics>
## Specific Ideas

- The two-axis rubric exists specifically to separate **restyle** (legacy-outlier + accurate) from **redraw** (inaccurate) so sweep planning can estimate effort correctly.
- Known findings the audit must confirm with evidence (from ROADMAP Phases 3–9), not assume: smoothing "smoothed" panel reuses noisy coordinates; `basis-representation.svg` and `spm.svg` contain R-era content; align elastic-alignment lacks a clear phase-vs-amplitude split; conformal-prediction.svg shows a scalar interval instead of a time-varying band `ŷ(t)±q(t)`; scalar-on-function should foreground `β(t)`; multiple analyze/ diagrams are legacy-outliers.
- Phase 9's five new examples are the locked baseline for the new-example list; the reference-API sweep only adds optional candidates around them.

</specifics>

<deferred>
## Deferred Ideas

- **Actually fixing** any diagram, removing R-era content, or writing new examples — that is Phases 3–9. This phase only produces the map, the grep report, and the ranked list.
- **Full method-semantic verification** of regression/monitoring diagrams against `fdars` (β(t), conformal functional bands, SPM Phase I/II) — deferred to Phases 7–8 sweeps per D-04; only `needs method-verification` flags are recorded now.
- **A11Y-01** (STATE.md): long-form `<title>`/`<desc>` + `aria-labelledby` for complex diagrams — v2. (The audit may note accessibility gaps it sees, but remediation is out of scope.)
- **EX2-01** (STATE.md): editorial consolidation of overlapping example pages (sonar-tsrvf vs phoneme-shape; Andrews-wine series) — v2.

None from this discussion required scope redirection — discussion stayed within phase scope.

</deferred>

---

*Phase: 2-Audit*
*Context gathered: 2026-08-07*
