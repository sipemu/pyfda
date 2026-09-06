# Phase 77: Section-Landing Card Coverage - Context

**Gathered:** 2026-09-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Bring five section-landing galleries to 100% card coverage by adding a
hand-authored inline-SVG thumbnail (`docs/assets/thumb/<slug>.svg`) plus a
`fdars-gallery` card entry (in the section `index.md`) for every currently
uncarded focus-section page. 21 new thumbnails + card entries total:

- **CARD-01 — align** (2): `shift-registration`, `banded-alignment`
- **CARD-02 — represent** (3): `pace-fpca`, `interpolation`, `imputation`
- **CARD-03 — regression** (5): `concurrent-regression`, `functional-glm`,
  `function-on-function`, `additive-sof`, `frechet-regression`
- **CARD-04 — analyze** (8): `functional-time-series`, `density-fda`,
  `advanced-clustering`, `multi-domain`, `shapelets`, `functional-boxplot`,
  `functional-statistics`, `scoring-metrics`
- **CARD-05 — examples** (3): `functional-outlier-workflow`,
  `canadian-depth-centrality`, `tolerance-vs-conformal`
- **CARD-06** — all new thumbnails are hand-authored inline SVG,
  STYLE_SPEC-conformant, decorative-accessible (`aria-hidden` card pattern), and
  pass SVGO idempotence + build-determinism.

**In scope:** 21 new `docs/assets/thumb/*.svg` thumbnails + 21 `fdars-gallery`
card entries in the five section `index.md` files, matching the existing card +
thumbnail house style.

**Out of scope:** the deferred no-gallery landing pages (Advisor 7 pages +
sklearn 5 pages — CARD-FUT-01), the capability skill (Phase 78), and the
whole-site `--strict` / SVGO-gate / human-review (Phase 79 runs the consolidated
GATE-02 determinism gate). No `fdars-core` bump, no new PyO3 bindings. **The 3
new Phase 76 flagship example pages are NOT carded here** — CARD-05 names only the
3 existing uncarded example pages; the new examples stay nav-reachable but
uncarded this milestone (per REQUIREMENTS).

</domain>

<decisions>
## Implementation Decisions

### Thumbnail authoring (user-accepted)
- **Author fresh** minimal 320×180 inline-SVG line-art for each new thumbnail,
  matching the existing 58 thumbnails in `docs/assets/thumb/` (viewBox
  `0 0 320 180`, `role="img"` + `aria-label`, 2–4 method-colored paths,
  `fill="none"`, rounded line caps). Thumbnails are the *smaller decorative*
  versions — do NOT down-scale the full, detailed concept diagrams in
  `docs/assets/diagrams/`; author concise thumbnails depicting each method's
  core concept.
- **Section hue:** reuse each section's established thumbnail hue (derive the
  exact hex from existing thumbs in that section so new cards blend into their
  gallery). Research maps the per-section hue.

### Determinism (CARD-06 / GATE-02)
- Run the repo's SVGO config on each new thumbnail during authoring and confirm
  **idempotence** (a second SVGO pass is a no-op) so the consolidated Phase 79
  GATE-02 (SVGO idempotence + build-determinism) passes cleanly. Match the
  established two-pass approach used for the existing thumbnail set.
- Each thumbnail must be STYLE_SPEC-conformant
  (`docs/assets/diagrams/STYLE_SPEC.md`) and decorative-accessible: the `<img>`
  card uses `class="fdars-gallery-thumb" aria-hidden="true" ... alt=""`, and the
  SVG itself carries `role="img"` + a descriptive `aria-label`.

### Card entries
- Each new card follows the exact existing `fdars-gallery-item` pattern:
  ```html
  <a class="fdars-gallery-item" href="<slug>/">
  <img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/<slug>.svg" alt="">
  <div class="fdars-gallery-title">Title Case</div>
  <div class="fdars-gallery-desc">One-line description.</div>
  </a>
  ```
  Insert each card into the correct `fdars-gallery` block in the section
  `index.md`, in a sensible order relative to existing cards.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- **58 existing thumbnails** in `docs/assets/thumb/` set the house style
  (e.g. `clustering.svg` ~1.3 KB: viewBox 0 0 320 180, single-hue line-art,
  `role="img"`/`aria-label`).
- **Card pattern** lives in each section `index.md` inside a
  `<div class="fdars-gallery fdars-sec-<section>">` block (verified in
  `docs/align/index.md`).
- **STYLE_SPEC:** `docs/assets/diagrams/STYLE_SPEC.md`.
- **Full concept diagrams** for many target pages exist in
  `docs/assets/diagrams/<slug>.svg` — reference for the concept, but thumbnails
  are authored fresh/minimal, not down-scaled from these.
- **Landing index files:** `docs/align/index.md`, `docs/represent/index.md`,
  `docs/regression/index.md`, `docs/analyze/index.md`, `docs/examples/index.md`.

### Established Patterns
- Card: `fdars-gallery-item` anchor → `fdars-gallery-thumb` img (`aria-hidden`,
  `alt=""`) → title → desc.
- Thumbnail SVG: `aria-hidden` on the `<img>`; SVG has `role="img"` + `aria-label`.
- SVGO idempotence + build-determinism gate (consolidated at Phase 79 GATE-02).

### Integration Points
- Thumbnails drop into `docs/assets/thumb/`; cards into the 5 section `index.md`s.
- Phase runs SEQUENTIALLY on `main`, `use_worktrees: false` (standing v12.0).

</code_context>

<specifics>
## Specific Ideas

- All 21 target slugs are confirmed missing thumbnails; the target pages already
  exist (many were deepened in Phases 74/75).
- Group work by section (align / represent / regression / analyze / examples) so
  each section's gallery reaches 100% as a unit.
- Verify each thumbnail renders (e.g. `rsvg-convert` smoke render) and is
  SVGO-idempotent; verify each card's `href`/`src` resolves.

</specifics>

<deferred>
## Deferred Ideas

- Gallery/cards for the Advisor (7) + sklearn (5) landing pages → CARD-FUT-01
  (deliberate no-gallery pattern; separate design call).
- Gallery cards for the 3 new Phase 76 flagship example pages — not in this
  milestone's CARD scope.
- Whole-site strict build / consolidated SVGO-determinism gate / human diagram
  review → Phase 79 (GATE).

</deferred>
