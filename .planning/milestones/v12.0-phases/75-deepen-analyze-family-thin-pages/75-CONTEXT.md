# Phase 75: Deepen Analyze-Family Thin Pages - Context

**Gathered:** 2026-09-05
**Status:** Ready for planning
**Mode:** Decisions carried forward from Phase 74 (identical parity work, disjoint page family) — smart-discuss did not re-ask already-decided grey areas per the autonomous contract.

<domain>
## Phase Boundary

Bring the five thin v11.0-era analyze-family method pages up to mature-page
parity (DEPTH-02), the analyze-section twin of Phase 74's regression work:

- `docs/analyze/functional-time-series.md`
- `docs/analyze/density-fda.md`
- `docs/analyze/multi-domain.md`
- `docs/analyze/shapelets.md`
- `docs/analyze/advanced-clustering.md`

"Parity" (per DEPTH-02) = a "When to use" decision section, a "See also"
cross-reference block, parameter-selection + result-interpretation guidance, ≥3
caution/tip/note admonition boxes, and ≥3 runnable inline `FDARS_FENCE_OK`
worked examples per page.

**In scope:** prose depth, structure, worked examples, admonitions, cross-refs,
and API-accuracy corrections on these five analyze pages only.

**Out of scope:** the regression-family pages (Phase 74, done), flagship example
pages (Phase 76), section-landing thumbnails/cards (Phase 77), the capability
skill (Phase 78), and the consolidated whole-site `--strict` / SVGO / human-review
gate (Phase 79). No `fdars-core` bump, no new PyO3 bindings. Concept SVG diagrams
for these pages already exist and are not re-authored here.

</domain>

<decisions>
## Implementation Decisions

Carried forward verbatim from Phase 74 (`74-CONTEXT.md`), accepted by the user
("Accept all"). Same approach; only the page family, method APIs, dataset fits,
and cross-reference targets differ (Claude's discretion within this approach).

### Page Depth & Structure
- **Depth target:** Hit the parity bar solidly at mature-page *quality*, sized
  to each method's actual surface — do not pad to a fixed length.
- **Restructure approach:** Mirror the mature numbered-section template used by
  the mature analyze pages (e.g. `docs/analyze/clustering.md`,
  `outlier-detection.md`, `seasonal-analysis.md`, `functional-statistics.md`):
  "When to use" / decision section near the top, numbered worked-method sections
  in the body, a diagnostics/interpretation section, and a "See also" block at
  the bottom. Preserve correct existing prose/examples; restructure and expand
  around them rather than rewriting from scratch.
- **Exec'd visualizations:** Add ≥1 `html="1"` exec'd matplotlib plot per page
  where it genuinely clarifies the method.

### Worked Examples & Data
- **Data source:** Prefer small, self-contained synthetic simulations built
  *inside* each fence (deterministic, offline, fast). Use existing `docs/data/`
  datasets where a method has a natural real-data fit (e.g. a time-series dataset
  for `functional-time-series`). Success criterion 4 explicitly names the
  existing `docs/data/` datasets — use them where they fit, do not invent files.
- **Count:** ≥3 runnable inline fences per page; add more only where a distinct
  method variant warrants its own example.
- **Sentinel:** Every runnable example must emit `FDARS_FENCE_OK` when run offline
  under `.venv`. Fences stay small to bound the ~25-min whole-site strict build
  that runs once in Phase 79. Verify per-page with the shared
  `scripts/run_page_fences.py` runner built in Phase 74.

### Cross-Reference & Accuracy
- **See also:** Each page links to related methods within the analyze family and
  the analyze index (3–5 links), so the five pages cross-navigate.
- **Admonitions:** ≥3 per page mixing `note` / `tip` / `warning` / `info`,
  method-specific (parameter guidance, caveats, return-type gotchas).
- **API accuracy:** Every method claim, function name, and signature must be
  accurate against the shipped v11.0 bindings — no stale/renamed API, no R-era
  prose. Runnable fences are self-verifying; verify remaining prose claims
  against the current `fdars` surface (research will map the exact API surface,
  as in Phase 74). Keep a "methods in R but not (yet) in Python" note only where
  accurate.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Mature-page templates** to mirror: `docs/analyze/clustering.md`,
  `docs/analyze/outlier-detection.md`, `docs/analyze/seasonal-analysis.md`,
  `docs/analyze/functional-statistics.md`.
- **Phase 74 exemplars** (the just-completed regression pages) show the exact
  applied parity pattern: `docs/regression/frechet-regression.md` (tracer) and
  its four siblings.
- **Shared fence runner** built in Phase 74: `scripts/run_page_fences.py`
  (`PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py <page.md>`).
- Existing concept SVG diagrams for the five pages under `docs/assets/diagrams/`.

### Established Patterns
- `markdown-exec` fences: ` ```python exec="1" ` with `source="above"` and
  optional `html="1"` for matplotlib capture; `docs_fig` helper in `scripts/`.
- Offline-fence sentinel: fences print `FDARS_FENCE_OK`.
- Admonitions: `!!! note "Title"`, `!!! tip`, `!!! warning`, `!!! info`.
- Bindings accessed as `fdars.<module>.<fn>` / `Fdata` methods.

### Integration Points
- Pages already wired into `docs/analyze/` nav and the analyze `index.md`.
- Fences run against the current `fdars` in the main-tree `.venv`; phase runs
  SEQUENTIALLY on `main`, `use_worktrees: false` (standing v12.0 decision).

</code_context>

<specifics>
## Specific Ideas

- Model section flow on the mature analyze pages named above; apply the exact
  parity pattern proven on the Phase 74 regression pages.
- `functional-time-series` is a natural fit for a real `docs/data/` time-series
  dataset (also the basis for the Phase 76 flagship FTS example) — check for a
  fitting dataset; fall back to a small synthetic series if timing is a concern.
- Per-page success is checkable locally with the fence sentinel; the consolidated
  `--strict` build is deferred to Phase 79 (DEPTH-03).

</specifics>

<deferred>
## Deferred Ideas

- Flagship end-to-end example pages (incl. the FTS flagship) → Phase 76 (EXMP).
- Section-landing thumbnails + cards for these pages → Phase 77 (CARD-04).
- Whole-site strict build / SVGO / human diagram review → Phase 79 (GATE).
- DEPTH-FUT-01: depth sweep of any older thin pages beyond this v11.0-era set.

</deferred>
