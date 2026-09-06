# Phase 74: Deepen Regression-Family Thin Pages - Context

**Gathered:** 2026-09-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Bring the five thin v11.0-era regression-family method pages up to mature-page
parity so a reader can decide when to use each method, cross-navigate to related
methods, choose parameters, interpret results, and copy runnable examples:

- `docs/regression/frechet-regression.md`
- `docs/regression/function-on-function.md`
- `docs/regression/additive-sof.md`
- `docs/regression/concurrent-regression.md`
- `docs/regression/functional-glm.md`

"Parity" (per DEPTH-01) = a "When to use" decision section, a "See also"
cross-reference block, parameter-selection + result-interpretation guidance, ≥3
caution/tip/note admonition boxes, and ≥3 runnable inline `FDARS_FENCE_OK`
worked examples per page.

**In scope:** prose depth, structure, worked examples, admonitions, cross-refs,
and API-accuracy corrections on these five pages only.

**Out of scope:** the analyze-family thin pages (Phase 75), flagship example
pages (Phase 76), section-landing thumbnails/cards (Phase 77), the capability
skill (Phase 78), and the consolidated whole-site `--strict` build / SVGO /
human-review gate (Phase 79). No `fdars-core` bump, no new PyO3 bindings. The
concept SVG diagrams for these pages already exist and are not re-authored here.

</domain>

<decisions>
## Implementation Decisions

### Page Depth & Structure
- **Depth target:** Hit the parity bar solidly at mature-page *quality*, sized
  to each method's actual surface — do not pad to a fixed length. A method with
  a smaller API surface may yield a shorter page and still be at parity.
- **Restructure approach:** Mirror the mature numbered-section template used by
  pages like `scalar-on-function.md` — a motivating "When to use" / decision
  section near the top, numbered worked-method sections in the body, a
  diagnostics/interpretation section, and a "See also" cross-reference block at
  the bottom. Preserve correct existing prose and examples; restructure and
  expand around them rather than rewriting from scratch.
- **Exec'd visualizations:** Add ≥1 `html="1"` exec'd matplotlib plot per page
  where it genuinely clarifies the method (matching the mature pages' visual
  standard). Not every fence needs a plot — only where it aids understanding.

### Worked Examples & Data
- **Data source:** Prefer small, self-contained synthetic simulations built
  *inside* each fence (deterministic, offline, fast) — as `frechet-regression.md`
  already does. Use existing `docs/data/` datasets only where a method has a
  natural real-data fit.
- **Count:** ≥3 runnable inline fences per page (meets the bar); add more only
  where a distinct method variant warrants its own example.
- **Sentinel:** Every runnable example must emit `FDARS_FENCE_OK` when run
  offline under `.venv` (the fence-level accuracy check). Fences stay small
  (few observations / grid points) to bound the ~25-min whole-site strict build
  that runs once in Phase 79.

### Cross-Reference & Accuracy
- **See also:** Each page links to related methods within the regression family
  and the regression index (3–5 links), so the five pages cross-navigate.
- **Admonitions:** ≥3 per page mixing `note` / `tip` / `warning` / `info`,
  method-specific (parameter guidance, caveats, return-type gotchas).
- **API accuracy:** Every method claim, function name, and signature must be
  accurate against the shipped v11.0 bindings — no stale/renamed API, no R-era
  prose. Runnable fences are self-verifying; verify remaining prose claims
  against the current `fdars` surface. Keep a "methods in R but not (yet) in
  Python" note only where it is accurate (mature-page pattern).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Mature-page template** to mirror: `docs/regression/scalar-on-function.md`
  (When-to-use intro, numbered worked sections, note/tip/warning/info
  admonitions, cross-validation, diagnostics, method comparison, See also).
- Other mature regression pages for pattern reference: `function-on-scalar.md`,
  `robust-regression.md`, `regression-diagnostics.md`, `elastic-regression.md`.
- Existing concept SVG diagrams for the five pages already live under
  `docs/assets/diagrams/` — reference them, do not re-author.

### Established Patterns
- Live code execution via `markdown-exec` fences: ` ```python exec="1" ` with
  `source="above"` and optional `html="1"` for matplotlib figure capture.
- Offline-fence sentinel: fences print `FDARS_FENCE_OK`; the whole-site
  `mkdocs build --strict` under `.venv` proves every fence runs (Phase 79 gate).
- Admonition syntax: `!!! note "Title"`, `!!! tip`, `!!! warning`, `!!! info`.
- Bindings surface accessed as `fdars.<module>.<fn>` / `Fdata` methods.

### Integration Points
- Pages already wired into `docs/regression/` nav and the regression `index.md`.
- Fences run against the current `fdars` package built into the main-tree
  `.venv` — phase runs SEQUENTIALLY on `main`, `use_worktrees: false`.

</code_context>

<specifics>
## Specific Ideas

- Model the section flow on `docs/regression/scalar-on-function.md`.
- `frechet-regression.md` already simulates SPD matrices inside its fence and
  carries a return-type warning — keep that pattern and extend it.
- Per-page success is checkable locally with the fence sentinel; the
  consolidated `--strict` build is deferred to Phase 79 (DEPTH-03), but each
  page must carry `FDARS_FENCE_OK` fences that pass here.

</specifics>

<deferred>
## Deferred Ideas

- Analyze-family thin pages (`functional-time-series`, `density-fda`,
  `multi-domain`, `shapelets`, `advanced-clustering`) → Phase 75 (DEPTH-02).
- Flagship end-to-end example pages → Phase 76 (EXMP).
- Section-landing thumbnails + cards for these pages → Phase 77 (CARD-03).
- Whole-site strict build / SVGO / human diagram review → Phase 79 (GATE).

</deferred>
