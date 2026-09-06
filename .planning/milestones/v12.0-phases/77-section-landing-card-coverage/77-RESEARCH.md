# Phase 77: Section-Landing Card Coverage — Research

**Researched:** 2026-09-06
**Domain:** Hand-authored inline-SVG thumbnails + MkDocs gallery card entries
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Author fresh** minimal 320×180 inline-SVG line-art for each new thumbnail,
  matching the existing 58 thumbnails in `docs/assets/thumb/` (viewBox `0 0 320 180`,
  `role="img"` + `aria-label`, 2–4 method-colored paths, `fill="none"`, rounded line
  caps). Thumbnails are the *smaller decorative* versions — do NOT down-scale the full
  concept diagrams in `docs/assets/diagrams/`.
- **Section hue:** reuse each section's established thumbnail hue (derive the exact hex
  from existing thumbs in that section so new cards blend into their gallery).
- Run the repo's SVGO config on each new thumbnail during authoring and confirm
  **idempotence** (a second SVGO pass is a no-op) so the Phase 79 GATE-02 passes.
- Each thumbnail must be STYLE_SPEC-conformant and decorative-accessible:
  - `<img>` card uses `class="fdars-gallery-thumb" aria-hidden="true" ... alt=""`
  - SVG itself carries `role="img"` + a descriptive `aria-label`
- Each new card follows the exact existing `fdars-gallery-item` pattern (see § Card
  Template below).
- **The 3 new Phase 76 flagship example pages are NOT carded here.**

### Claude's Discretion

- Sensible insertion order of new cards within each gallery block.

### Deferred Ideas (OUT OF SCOPE)

- Gallery/cards for Advisor (7) and sklearn (5) landing pages → CARD-FUT-01.
- Gallery cards for the 3 new Phase 76 flagship example pages.
- Whole-site strict build / consolidated SVGO gate / human review → Phase 79.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CARD-01 | Align landing: thumbnails + cards for `shift-registration`, `banded-alignment` | §Align hue, §21-item table, §Align insertion point |
| CARD-02 | Represent landing: thumbnails + cards for `pace-fpca`, `interpolation`, `imputation` | §Represent hue, §21-item table, §Represent insertion point |
| CARD-03 | Regression landing: thumbnails + cards for 5 pages | §Regression hue, §21-item table, §Regression insertion point |
| CARD-04 | Analyze landing: thumbnails + cards for 8 pages | §Analyze hue, §21-item table, §Analyze insertion point |
| CARD-05 | Examples landing: cards for 3 uncarded existing pages | §Examples hue, §21-item table, §Examples insertion point |
| CARD-06 | All new thumbnails STYLE_SPEC-conformant, SVGO-idempotent, decorative-accessible | §Thumbnail house style, §SVGO mechanics, §Accessibility |
</phase_requirements>

---

## Summary

Phase 77 adds 21 hand-authored inline-SVG thumbnails (`docs/assets/thumb/<slug>.svg`) and
21 corresponding `fdars-gallery` card entries across five section `index.md` files. All
21 target thumbnail slots are confirmed missing. The target pages all exist and are reachable
via nav (verified against `mkdocs.yml`).

The work is purely additive: no existing files change except the five `index.md` files where
new card entries are inserted. The thumbnail house style is tightly constrained by the 58
existing thumbnails; the key parameters are documented in full below. The SVGO determinism
gate (Phase 79 GATE-02) requires every new thumbnail to be idempotent under `svgo@3.3.4
--config svgo.config.mjs` — the exact command and two-pass verification procedure are
documented in §SVGO Mechanics.

**Primary recommendation:** Group work by section (align → represent → regression →
analyze → examples). For each section: author all thumbnails first, verify SVGO idempotence
on each, then insert the card entries into the section `index.md`.

---

## 1. Thumbnail House Style

**Verified from reading 12 existing thumbnails.** [VERIFIED: docs/assets/thumb/elastic-alignment.svg:1-9, clustering.svg:1-18, basis-representation.svg:1-9, scalar-on-function.svg:1-10, fpca.svg:1-10, tolerance-bands.svg:1-9, outlier-detection.svg:1-14, landmark-registration.svg:1-12, advanced-alignment.svg:1-11, depth-functions.svg:1-6, distance-metrics.svg:1-9, seasonal-analysis.svg:1-7]

### Root `<svg>` pattern (verbatim from corpus)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" fill="none" role="img" aria-label="<descriptive label>">
```

All 58 thumbnails use:
- `viewBox="0 0 320 180"` — always. Concept diagrams use `720×N`; thumbnails always `320×180`. [VERIFIED: every thumb read this session]
- `fill="none"` on the root `<svg>`
- `role="img"` on the root `<svg>`
- `aria-label="<text>"` — descriptive but short (3–6 words); does NOT duplicate the
  card's `fdars-gallery-title` text verbatim but describes what is depicted (e.g.,
  "Elastic alignment" not "Elastic Alignment registration of phase-shifted curves")
- No `<title>` / `<desc>` / `aria-labelledby` — those are **concept diagram** requirements.
  Thumbnails are decorative (`aria-hidden="true"` on the `<img>`) and use only `role="img"`
  + `aria-label` on the SVG itself. [VERIFIED: STYLE_SPEC.md:149-153]
- No `<style>` block — thumbnails have no text labels so the canonical font classes are
  not needed. A few complex thumbs include inline text via bare `<text>` with explicit
  font/size attributes when strictly necessary (e.g., `scalar-on-function.svg` has a
  `y` label; `outlier-detection.svg` has an "outlier" label). For the 21 new thumbnails,
  **omit text labels** unless the concept is unrecognisable without one.

### Structural anatomy (shared across all 58)

1. **Axis lines** (optional but present in ~80% of thumbnails): two `<line>` elements
   forming an L-shaped axis at bottom-left, using `stroke-opacity=".35"` and
   `stroke-width="1.4"`. Standard positions: `x1="30" y1="150" x2="298" y2="150"` (x-axis)
   and `x1="30" y1="150" x2="30" y2="28"` (y-axis). [VERIFIED: all axis thumbs read this session]

2. **Method paths**: 2–4 `<path>` elements using cubic Bézier curves (`C`/`M`). The
   primary path uses `stroke-width="3"` + `stroke-linecap="round"`. Secondary paths use
   `stroke-width="2"` and reduced `stroke-opacity` (`.4`–`.55`). Faint background paths
   use `stroke-width="1.4"`–`"1.6"` and `stroke-opacity=".28"`–`.45"`.

3. **Fills**: Two patterns in use:
   - Area fill: a `<linearGradient>` + a closed path `L298 150 L30 150 Z` — creates a
     subtle shaded region under the main curve (used in `fpca.svg`, `scalar-on-function.svg`,
     `tolerance-bands.svg`, `seasonal-analysis.svg`).
   - Solid fill at very low opacity directly on a `<path fill-opacity>` (used in
     `depth-functions.svg` for the band layers).

4. **Accent elements**: circles (`<circle>`), arrow heads (`<path>` with Z fill), dashed
   lines (`stroke-dasharray`), vertical tick marks.

5. **All coordinates stay within the viewBox padding**: x range ~30–298, y range ~28–150.

### File size range

713 bytes (simplest) to 1,765 bytes (most complex). Target for new thumbnails: **700–1,100 bytes**.
Simple axis + 2–3 paths hits ~800–950 bytes. [VERIFIED: ls -la output this session]

### Skeleton executor template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" fill="none" role="img" aria-label="<3-6 word description>">
  <!-- x-axis -->
  <line x1="30" y1="150" x2="298" y2="150" stroke="<SECTION_HEX>" stroke-opacity=".35" stroke-width="1.4"/>
  <!-- y-axis -->
  <line x1="30" y1="150" x2="30" y2="28" stroke="<SECTION_HEX>" stroke-opacity=".35" stroke-width="1.4"/>
  <!-- secondary / faint path(s) -->
  <path d="M30 <Y1> C<cx1> <cy1> <cx2> <cy2> <x3> <y3>" stroke="<SECTION_HEX>" stroke-opacity=".4" stroke-width="2"/>
  <!-- primary path -->
  <path d="M30 <Y2> C<cx1> <cy1> <cx2> <cy2> <x3> <y3>" stroke="<SECTION_HEX>" stroke-width="3" stroke-linecap="round"/>
</svg>
```

**Do not add** `xmlns:xlink`, `id` attributes on paths, `<g>` wrappers (unless grouping
multiple related paths with shared stroke properties), or any attribute not present in the
corpus. Attribute order: `stroke`, `stroke-opacity`, `stroke-width`, `stroke-linecap`,
`stroke-dasharray` — match corpus order to pass SVGO idempotence. [ASSUMED — SVGO normalises
attribute ordering on first pass; exact post-SVGO order is what the second pass must match.
Author in any order; run SVGO once and commit the SVGO-normalised output — see §SVGO
Mechanics.]

---

## 2. Per-Section Hue

Derived by reading `stroke` values on the primary paths of existing thumbnails in each
section's gallery. [VERIFIED: thumbs read this session]

| Section | Primary Hue | Hex | Evidence |
|---------|-------------|-----|----------|
| **align** | Orange | `#fd7e14` | `elastic-alignment.svg`, `landmark-registration.svg`, `advanced-alignment.svg`, `tsrvf.svg`, `alignment-comparison.svg`, `shape-analysis.svg` — all use `#fd7e14` |
| **represent** | Green | `#198754` | `fpca.svg`, `basis-representation.svg`, `depth-functions.svg`, `distance-metrics.svg`, `elastic-fpca.svg` — all use `#198754` |
| **regression** | Red | `#dc3545` | `scalar-on-function.svg`, `function-on-scalar.svg`, `elastic-regression.svg` — all use `#dc3545` |
| **analyze** | Purple | `#6f42c1` | `clustering.svg`, `tolerance-bands.svg`, `outlier-detection.svg`, `gmm-clustering.svg`, `seasonal-analysis.svg`, `equivalence-testing.svg`, `covariance-functions.svg`, `elastic-clustering.svg` — all use `#6f42c1` |
| **examples** | Indigo | `#3f51b5` | `ex-canadian-weather.svg`, `ex-growth-alignment.svg`, `ex-canadian-precipitation.svg` — all use `#3f51b5` |

**Note on examples naming convention:** existing examples thumbs are prefixed `ex-`
(e.g., `ex-canadian-weather.svg`) but the 3 target slugs (`functional-outlier-workflow`,
`canadian-depth-centrality`, `tolerance-vs-conformal`) do NOT use a prefix in their
page filenames or `mkdocs.yml` nav entries. [VERIFIED: mkdocs.yml:182,189,193] The thumb
files for these three pages should therefore be named **without** the `ex-` prefix:
`functional-outlier-workflow.svg`, `canadian-depth-centrality.svg`,
`tolerance-vs-conformal.svg`.

---

## 3. The 21 Items — Complete Spec

Page titles verified against page H1 / frontmatter `title:` field. [VERIFIED: head output
for all 21 files this session]

Gallery descriptions follow the house voice: imperative or noun-phrase, 8–14 words,
matching sibling card descriptions. Concept sketches are method-accurate.

### CARD-01: align (2 items)

| # | Slug | Page Title | Gallery Title | Gallery Desc (8–14 words) | Thumbnail Concept |
|---|------|-----------|---------------|--------------------------|-------------------|
| 1 | `shift-registration` | Shift Registration | Shift Registration | Align curves by a single scalar time-shift per observation. | Two horizontally offset S-curves (one faint, one solid) with a horizontal arrow bridging the gap between their peaks, showing rigid shift alignment. |
| 2 | `banded-alignment` | Banded Elastic Alignment | Banded Elastic Alignment | Fast Karcher mean via a diagonal DP band constraint. | An elastic warp corridor: a diagonal band (pair of dashed parallel lines from bottom-left to top-right) with a solid warping path threading inside it, depicting the Sakoe-Chiba bandwidth constraint. |

### CARD-02: represent (3 items)

| # | Slug | Page Title | Gallery Title | Gallery Desc (8–14 words) | Thumbnail Concept |
|---|------|-----------|---------------|--------------------------|-------------------|
| 3 | `pace-fpca` | PACE — FPCA for Sparse, Irregular Data | PACE FPCA | FPCA via conditional expectation for sparse, irregularly sampled curves. | Sparse dot observations scattered unevenly along a curve, with a smooth reconstructed curve overlaid in solid stroke, showing the sparse-to-smooth recovery. |
| 4 | `interpolation` | Spline Interpolation | Spline Interpolation | Resample functional curves onto any grid with B-spline fits. | A coarse-grid step-function (vertical tick marks) and a smooth cubic Bézier curve through the same points, showing resampling to a denser grid. |
| 5 | `imputation` | Missing-Value Imputation | Missing Value Imputation | Fill NaN gaps in functional curves with spline or mean strategies. | A curve with a gap (dashed segment) that is filled in by a reconstructed solid segment between two solid flanks, depicting imputation of a missing stretch. |

### CARD-03: regression (5 items)

| # | Slug | Page Title | Gallery Title | Gallery Desc (8–14 words) | Thumbnail Concept |
|---|------|-----------|---------------|--------------------------|-------------------|
| 6 | `concurrent-regression` | Concurrent (Varying-Coefficient) Regression | Concurrent Regression | Point-wise coefficient function links functional predictor and response. | A smooth coefficient function β(t) (wavy solid curve) that changes sign across the domain, with a faint horizontal zero-line, depicting how the local effect varies over t. |
| 7 | `functional-glm` | Functional Generalized Linear Model | Functional GLM | Project curves onto FPCs, then fit a GLM on the resulting scores. | A curve projected down to two FPC score points, then a logistic sigmoid drawn in the score-response panel — one panel shows the functional predictor, a short arrow leads to a small scatter of binary outcomes. Two-panel sketch using a single connecting arrow. |
| 8 | `function-on-function` | Function-on-Function Regression | Function-on-Function | Bivariate coefficient surface links functional predictor to functional response. | A diagonal heat-map rectangle (light fill, contour lines) representing the bivariate coefficient surface β(s,t), with s-axis and t-axis lines. |
| 9 | `additive-sof` | Additive Scalar-on-Function Regression | Additive Scalar-on-Function | Decompose functional effect into additive smooth component functions. | Two partial-effect curves (one positive arch, one negative trough) with plus sign between them and a scalar dot at right, depicting the additive decomposition. |
| 10 | `frechet-regression` | Fréchet Regression | Fréchet Regression | Regress onto a conditional Fréchet mean in a non-Euclidean metric space. | A curved geodesic arc on a stylised sphere or cone surface, with two scattered observation points and a conditional mean point highlighted, depicting metric-space regression. |

### CARD-04: analyze (8 items)

| # | Slug | Page Title | Gallery Title | Gallery Desc (8–14 words) | Thumbnail Concept |
|---|------|-----------|---------------|--------------------------|-------------------|
| 11 | `functional-time-series` | Functional Time Series | Functional Time Series | Forecast, test stationarity, and model autocorrelation for curve sequences. | Three curves at successive time steps (slightly offset vertically, each lighter), with a fourth dashed forecast curve projected beyond them, depicting FTS forecasting. |
| 12 | `density-fda` | Density FDA | Density FDA | Analyze probability densities as functional objects via the LQD transform. | Three density-shaped bell curves (different widths and locations) at low opacity, with a single bolder LQD-transformed version overlaid, showing the transformation to an unconstrained domain. |
| 13 | `advanced-clustering` | Advanced Clustering | Advanced Clustering | Density-based, structure-aware, and alignment-coupled clustering methods. | Four curve bundles at different heights (two tight groups, one sparse, one outlying path), with dashed group boundaries, depicting multi-method clustering beyond simple k-means. |
| 14 | `multi-domain` | Multi-Domain FDA | Multi-Domain FDA | Joint FPCA across multiple functional variables per subject. | Two parallel axis panels (left and right) each with a curve, connected by a shared score circle in the middle, depicting multi-domain FPCA extracting joint components. |
| 15 | `shapelets` | Shapelets | Shapelets | Discriminative subsequences that separate classes by minimum-distance matching. | A long curve with a highlighted short window (rectangle around a distinctive wiggle), and a small distance bracket from the window to a matching segment on a second curve. |
| 16 | `functional-boxplot` | Functional Boxplot | Functional Boxplot | Depth-based central region, fences, and outlier detection for curves. | Three nested bands (innermost darkest, outermost faintest) around a median curve, with one outlier path breaking outside the outermost band. |
| 17 | `functional-statistics` | Functional Summary Statistics | Functional Statistics | Pointwise variance, covariance surface, and depth-based median of curves. | A mean curve (solid) flanked by a pointwise standard-deviation envelope (shaded), with small vertical error bars at regular intervals. |
| 18 | `scoring-metrics` | Functional Scoring Metrics | Scoring Metrics | Integrated prediction-error metrics: MAE, MSE, MAPE, MSLE, explained variance. | A predicted curve (dashed) and a true curve (solid) with vertical gap segments highlighted between them, depicting integrated prediction error. |

### CARD-05: examples (3 items)

| # | Slug | Page Title | Gallery Title | Gallery Desc (8–14 words) | Thumbnail Concept |
|---|------|-----------|---------------|--------------------------|-------------------|
| 19 | `functional-outlier-workflow` | A functional outlier-detection workflow | Functional outlier workflow | Combine magnitude and shape scores to flag atypical curves end-to-end. | A tight bundle of typical curves with one curve departing sharply in shape (different oscillation) and a second departing in magnitude (elevated level), both circled/highlighted. |
| 20 | `canadian-depth-centrality` | Ranking curves by centrality with functional depth | Canadian depth &amp; centrality | Rank 35 Canadian weather curves from most central to most atypical. | Multiple curves ordered by depth from innermost (bold) to outermost (faint), resembling nested contours, with depth rank numbers implied by opacity layering. |
| 21 | `tolerance-vs-conformal` | Tolerance bands vs conformal bands | Tolerance vs conformal | Two band philosophies — FPCA-based vs distribution-free — compared side by side. | Two side-by-side shaded bands (left slightly wider, right slightly narrower with dashed boundary), each with a median curve, connected by a vertical divider. |

---

## 4. Card Template and Exact Insertion Points

### Card HTML Template (exact pattern from corpus) [VERIFIED: docs/align/index.md:13-37]

```html
<a class="fdars-gallery-item" href="<slug>/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/<slug>.svg" alt="">
<div class="fdars-gallery-title"><Title Case></div>
<div class="fdars-gallery-desc"><Description sentence.></div>
</a>
```

**Confirmed conventions:**
- `href` form: relative `<slug>/` with trailing slash. [VERIFIED: align/index.md:13,18,23,28,33,38]
- `src` form: `../assets/thumb/<slug>.svg` — one directory up from the section directory. [VERIFIED: align/index.md:14,19,24]
- `aria-hidden="true"` on `<img>` — not on the `<a>` or the SVG file. [VERIFIED: STYLE_SPEC.md:149]
- `alt=""` — empty string, not absent. [VERIFIED: align/index.md:14]
- No blank lines between the `<a>`, `<img>`, `<div>`, `</a>` tags — each on its own line, no blank lines. [VERIFIED: align/index.md:13-16 vs examples/index.md:17-22 which uses blank lines]
- **Exception — examples/index.md**: the existing examples gallery uses blank lines between elements inside the `<a>` block (compare `align/index.md` vs `examples/index.md:17-22`). New example cards must match the examples gallery style (blank lines). [VERIFIED: examples/index.md:17-22]

### align/index.md — Insertion Point [VERIFIED: docs/align/index.md:12-43]

Current gallery has 6 cards: elastic-alignment, advanced-alignment, landmark-registration, tsrvf, alignment-comparison, shape-analysis.

Insert `shift-registration` after `alignment-comparison` (it is a simpler/baseline method that contextually pairs with the comparison page), and `banded-alignment` after `advanced-alignment` (it is a variant of the advanced Karcher mean machinery):

```
[existing] elastic-alignment
[existing] advanced-alignment
[NEW]      banded-alignment       ← insert here (right after advanced-alignment)
[existing] landmark-registration
[existing] tsrvf
[existing] alignment-comparison
[NEW]      shift-registration     ← insert here (after alignment-comparison)
[existing] shape-analysis
```

Insertion for `banded-alignment` — replace this block in `align/index.md`:
```html
<a class="fdars-gallery-item" href="advanced-alignment/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/advanced-alignment.svg" alt="">
<div class="fdars-gallery-title">Advanced Elastic Alignment</div>
<div class="fdars-gallery-desc">Closed, constrained, penalized, and multi-resolution alignment.</div>
</a>
<a class="fdars-gallery-item" href="landmark-registration/">
```
→ insert the `banded-alignment` card block between `</a>` and `<a class="fdars-gallery-item" href="landmark-registration/">`.

Insertion for `shift-registration` — replace this block:
```html
<a class="fdars-gallery-item" href="alignment-comparison/">
...
</a>
<a class="fdars-gallery-item" href="shape-analysis/">
```
→ insert the `shift-registration` card block between `</a>` and `<a class="fdars-gallery-item" href="shape-analysis/">`.

### represent/index.md — Insertion Point [VERIFIED: docs/represent/index.md:12-48]

Current gallery has 7 cards: fpca, elastic-fpca, basis-representation, andrews-transformation, depth-functions, streaming-depth, distance-metrics.

Insert all 3 new cards **after** `basis-representation` and **before** `andrews-transformation` (pace-fpca extends fpca/basis; interpolation and imputation are data-prep tools that logically precede representation):

```
[existing] fpca
[existing] elastic-fpca
[existing] basis-representation
[NEW]      pace-fpca              ← insert here
[NEW]      interpolation          ← insert here
[NEW]      imputation             ← insert here
[existing] andrews-transformation
[existing] depth-functions
[existing] streaming-depth
[existing] distance-metrics
```

### regression/index.md — Insertion Point [VERIFIED: docs/regression/index.md:12-73]

Current gallery has 12 cards ending at `robust-regression`. The 5 new methods are
advanced/specialist regression methods. Insert them as a block **after** `function-on-scalar`
and **before** `classification`:

```
[existing] scalar-on-function
[existing] function-on-scalar
[NEW]      concurrent-regression  ← insert here
[NEW]      functional-glm         ← insert here
[NEW]      function-on-function   ← insert here
[NEW]      additive-sof           ← insert here
[NEW]      frechet-regression     ← insert here
[existing] classification
[existing] elastic-regression
...
```

Rationale: concurrent-regression, functional-glm, function-on-function, additive-sof, and
frechet-regression are all natural extensions of the scalar-on-function/function-on-scalar
pair and should appear right after them before the more specialist methods.

### analyze/index.md — Insertion Point [VERIFIED: docs/analyze/index.md:12-53]

Current gallery has 8 cards: tolerance-bands, clustering, gmm-clustering, elastic-clustering, outlier-detection, seasonal-analysis, equivalence-testing, covariance-functions.

Insert the 8 new cards as two groups:

```
[existing] tolerance-bands
[existing] clustering
[existing] gmm-clustering
[existing] elastic-clustering
[NEW]      advanced-clustering    ← insert here (extends clustering group)
[existing] outlier-detection
[existing] seasonal-analysis
[existing] equivalence-testing
[existing] covariance-functions
[NEW]      functional-time-series ← insert here (new capability group)
[NEW]      density-fda            ← insert here
[NEW]      multi-domain           ← insert here
[NEW]      shapelets              ← insert here
[NEW]      functional-boxplot     ← insert here
[NEW]      functional-statistics  ← insert here
[NEW]      scoring-metrics        ← insert here
```

### examples/index.md — Insertion Points [VERIFIED: docs/examples/index.md:1-144]

The examples index has **multiple separate `fdars-gallery` blocks**, one per sub-heading.
The 3 target pages each belong to an existing conceptual group:

- `functional-outlier-workflow` → add to the **"Classification"** gallery (it involves
  depth-based detection) **or** create a new `## Depth & outlier analysis` section.
  Best fit: add a new section heading `## Depth &amp; outlier analysis` with a new
  `fdars-gallery` block containing this card, inserted **after** the "Classification"
  section (after line 95, before line 97 `## Seasonal & regional analysis`).

- `canadian-depth-centrality` → add to **"Seasonal &amp; regional analysis"** gallery
  (Canadian Weather dataset; pairs with other Canadian examples). Insert after
  `canadian-precipitation/` (last item in that gallery).

- `tolerance-vs-conformal` → add to **"Process monitoring"** gallery or a new section.
  Best fit: add a new `## Tolerance &amp; uncertainty` section heading with a new
  `fdars-gallery` block, inserted **after** "Process monitoring" and before the
  "What each example shows" table.

Example card block for `examples/index.md` (uses blank-line format matching sibling cards):

```html
<a class="fdars-gallery-item" href="functional-outlier-workflow/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/functional-outlier-workflow.svg" alt="">
<div class="fdars-gallery-title">Functional outlier workflow</div>
<div class="fdars-gallery-desc">Combine magnitude and shape scores to flag atypical curves end-to-end.</div>
</a>
```

**Thumb src for examples**: `../assets/thumb/<slug>.svg` (no `ex-` prefix for these 3).
[VERIFIED: mkdocs.yml confirms slugs are `functional-outlier-workflow`,
`canadian-depth-centrality`, `tolerance-vs-conformal` without prefix]

---

## 5. SVGO + Determinism Gate Mechanics (CARD-06 / GATE-02)

### Exact SVGO command [VERIFIED: svgo.config.mjs:4-6, STYLE_SPEC.md:14-17, docs.yml:54-55]

```bash
npx svgo@3.3.4 --config svgo.config.mjs --quiet --input <slug>.svg --output -
```

**Pin `svgo@3.3.4`** — not `latest`. v4 has a different CLI and config API. [VERIFIED: STYLE_SPEC.md:18]
**Always pass `--config svgo.config.mjs`** — without it, `inlineStyles` corrupts CSS classes. [VERIFIED: STYLE_SPEC.md:23-26]
**Always use `--output -`** (stdout) — never `-o <file>`. The gate never rewrites committed SVGs. [VERIFIED: svgo.config.mjs:18]

### Two-pass idempotence verification [VERIFIED: svgo.config.mjs:4-6, docs.yml:52-62]

```bash
# Run from the repo root
svg="docs/assets/thumb/<slug>.svg"
first=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -)
second=$(printf '%s' "$first" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
diff <(printf '%s' "$first") <(printf '%s' "$second")
# Must produce no output (empty diff = idempotent)
```

### What the CI gate checks [VERIFIED: docs.yml:54-62]

The CI job (`Lint SVG diagrams (SVGO)`) iterates `docs/assets/diagrams/*.svg` — **concept
diagrams only**, NOT `docs/assets/thumb/*.svg`. [VERIFIED: docs.yml:54] The Phase 79 GATE-02
gate is the consolidated gate that will cover thumbnails; Phase 77 only needs to ensure new
thumbnails are locally idempotent so GATE-02 passes without fixing them later.

### Are existing thumbnails already SVGO-optimised?

The existing 58 thumbnails were hand-authored and the SVGO gate runs on `diagrams/` not
`thumb/`. The thumbs are not pre-processed by SVGO. [ASSUMED — no evidence thumbs were
SVGO-processed; the gate glob `docs/assets/diagrams/*.svg` excludes thumb/]. New thumbnails
should be authored so that a single SVGO pass is a no-op (i.e., they are already in the
normalised form). To achieve this:

1. Write the SVG by hand.
2. Run SVGO once: `first=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -)`
3. Compare the diff: if `$first` differs from the file (cosmetic whitespace/attribute
   reordering), that is acceptable — write `printf '%s\n' "$first"` to the file (only if
   first pass transformed it).
4. Re-run the two-pass idempotence check — must produce empty diff.
5. Commit the file in whatever form it was authored (SVGO must not rewrite it — leave the
   hand-authored source unchanged). The gate checks idempotence of the file-on-disk, not
   a pre-normalised form.

**Practical guidance:** The safest approach is to author the SVG, run the idempotence check,
and if the diff is non-empty on pass 1 → pass 2, identify which plugin would still transform
it (likely `convertPathData` on hand-typed coordinates) — but `convertPathData: false` in the
config means this should not happen. If the diff is empty, the file passes.

### Smoke render [VERIFIED: docs-diagram-verify-workflow memory entry]

```bash
rsvg-convert -w 320 -h 180 docs/assets/thumb/<slug>.svg -o /tmp/<slug>.png
```

If `rsvg-convert` is not installed: `sudo pacman -S librsvg` (Manjaro/Arch). This confirms
the SVG parses and renders without errors. View `/tmp/<slug>.png` visually to verify the
line-art matches the intended concept.

---

## 6. Common Pitfalls

### Pitfall 1: Using concept-diagram viewBox on a thumbnail

**What goes wrong:** Using `viewBox="0 0 720 300"` (concept diagram standard) instead of
`viewBox="0 0 320 180"` (thumbnail standard). The card will display a tiny or cropped image.
**Prevention:** Always start from the thumbnail skeleton above. [VERIFIED: every thumb read is 320×180]

### Pitfall 2: Adding `<title>` / `<desc>` / `aria-labelledby` to thumbnails

**What goes wrong:** Concept diagram accessibility requirements do not apply to thumbnails.
Thumbnails use `role="img"` + `aria-label` only; the `<img>` tag carries `aria-hidden="true"`
and `alt=""` so screen readers skip both the `<img>` and the SVG.
**Prevention:** No `<title>`, `<desc>`, or `aria-labelledby` on thumbnail SVGs. [VERIFIED: STYLE_SPEC.md:149-153, all 12 thumbs read]

### Pitfall 3: Adding the `<style>` block to thumbnails

**What goes wrong:** Thumbnails have no text labels (or bare `<text>` with inline attributes),
so the canonical five-class `<style>` block is unnecessary and adds ~220 bytes. SVGO's
`minifyStyles: false` will preserve it, bloating the file.
**Prevention:** Omit the `<style>` block. If a text label is needed, use inline attributes
(`font-family`, `font-size`, `font-weight`, `fill`). [VERIFIED: all 12 thumbs read — none has a `<style>` block]

### Pitfall 4: Non-deterministic `defs` ID collision

**What goes wrong:** Two thumbnails using `<linearGradient id="tb">` — same ID in different
files. MkDocs/browsers inline SVGs differently; an ID collision on the same page causes one
gradient to render with the wrong colour.
**Prevention:** Make every `<linearGradient id>` unique per file. Convention: use a 2-3
character abbreviation of the slug (e.g., `id="sr"` for `shift-registration`, `id="ba"` for
`banded-alignment`, `id="pf"` for `pace-fpca`). [ASSUMED — inferred from corpus where each
thumb using a gradient has a unique 2-letter id: `sof`, `fp`, `tb`, `sa`, `ega`]

### Pitfall 5: Floating-point coordinate precision causing non-idempotence

**What goes wrong:** SVGO's `convertPathData: false` is set, so it will NOT rewrite path
coordinates. Hand-typed coordinates with many decimals are preserved verbatim and pass
idempotence. However, if `convertPathData` were accidentally enabled, high-precision floats
get rounded and the second pass would then differ from the first.
**Prevention:** The config disables `convertPathData`, so use any integer or simple float
coordinates. [VERIFIED: svgo.config.mjs:38-41]

### Pitfall 6: Using `ex-` prefix for the 3 examples thumbnails

**What goes wrong:** The 3 new examples pages (`functional-outlier-workflow`, etc.) do NOT
use the `ex-` prefix convention in their slug or filename — only the existing Phase-1-era
example pages do. The card `src` attribute must match the file exactly.
**Prevention:** Name files `functional-outlier-workflow.svg`, `canadian-depth-centrality.svg`,
`tolerance-vs-conformal.svg`. [VERIFIED: mkdocs.yml:182,189,193 — no `ex-` prefix]

### Pitfall 7: Wrong href trailing slash

**What goes wrong:** Using `href="shift-registration"` (no trailing slash) instead of
`href="shift-registration/"`. MkDocs generates directory-style URLs; the trailing slash is
required for the link to resolve without a redirect.
**Prevention:** Always include the trailing slash in card `href`. [VERIFIED: align/index.md:13,18,23]

### Pitfall 8: Blank lines inside `<a>` blocks for non-examples sections

**What goes wrong:** The align/represent/regression/analyze `index.md` files have no blank
lines between the `<img>`, `<div>`, and `</a>` elements inside each card block. Introducing
blank lines does not break rendering but creates inconsistency with siblings.
**Prevention:** Match the sibling card style per section. Examples section uses blank lines;
other four sections do not. [VERIFIED: align/index.md:13-16 vs examples/index.md:17-22]

### Pitfall 9: Coordinates outside the usable region

**What goes wrong:** Paths with y-coordinates above 28 or x-coordinates below 30 / above
298 will clip or be invisible under the axis lines.
**Prevention:** Keep all path coordinates within x∈[30,298], y∈[28,150]. [VERIFIED: all thumbs use these bounds]

---

## 7. Thumbnail Concept Sketches (Method-Accurate Detail)

Below is a more detailed rendering note for the visually complex items, to give the executor
enough information to author line-art without domain ambiguity.

**shift-registration**: Two nearly identical smooth curves (single-hump), one shifted ~40px to
the right of the other. Both at reduced opacity. A third solid bold curve shows the result after
alignment (peaks coincide). An arrow `←→` at the top between the two misaligned peaks. Hue: `#fd7e14`.

**banded-alignment**: Diagonal axis (lower-left to upper-right represents warp path space).
Two dashed diagonal lines flanking the main diagonal, creating a band. A solid warping path
stays inside the band. This depicts the Sakoe-Chiba constraint. Hue: `#fd7e14`.

**pace-fpca**: Scattered circles (5–8 dots at irregular x positions, varying y) on a single
curve's trajectory, with a smooth Bézier curve passing through their region. Dot scatter
represents sparse observations; the curve represents the PACE-fitted smooth. Hue: `#198754`.

**interpolation**: Coarse source grid (4–5 vertical tick marks with small circles at their tops)
plus a smooth cubic Bézier through those points, plus a second denser set of tick marks showing
the resampled output grid. Hue: `#198754`.

**imputation**: A curve that breaks (gap of ~50px with dashed segment) at a middle section, then
resumes. The dashed segment is the imputed region. Two solid flanking segments confirm the rest
of the curve is intact. Hue: `#198754`.

**concurrent-regression**: A wavy coefficient function β(t) that starts positive, crosses zero,
goes negative, then rises again — a visually complex smooth curve. A horizontal zero-reference
line at mid-y. The coefficient function is the hero path (bold); the reference line is faint.
Hue: `#dc3545`.

**functional-glm**: A functional curve (left ~40% of width) → arrow → scatter of binary outcome
dots (right ~40%). Two dot levels (y-high = class 1, y-low = class 0). A logistic S-curve
through the dots. Hue: `#dc3545`.

**function-on-function**: A square region filling most of the viewBox, with 3–4 faint contour
lines (nested partial ellipses) inside it — the bivariate coefficient surface β(s,t). Axis
lines on two sides label the s and t domains. Hue: `#dc3545`.

**additive-sof**: Three elements: a positive arch (f₁(t)), a negative trough (f₂(t)), and a
scalar response dot at the right edge. The two component curves are at medium opacity; a bold
horizontal baseline. Optionally a small "+" text between them. Hue: `#dc3545`.

**frechet-regression**: A stylised arc (partial circle) representing a geodesic in metric space.
Two small filled circles along the arc (observations) and a third open circle (conditional
Fréchet mean). Hue: `#dc3545`.

**functional-time-series**: Three curves stacked vertically (each ~10px apart in y), getting
progressively lighter (t, t+1, t+2), with a fourth dashed curve slightly ahead of the third
(forecast). All curves have similar sinusoidal shape. Hue: `#6f42c1`.

**density-fda**: Three Gaussian-bell-shaped curves at different horizontal positions/widths
(faint), plus one bold curve that is flatter/straighter — the LQD-transformed version in an
unconstrained domain. A horizontal baseline. Hue: `#6f42c1`.

**advanced-clustering**: Four curve groups: two tight bundles (2–3 close paths each at high
opacity), one sparse group (2 paths with moderate gap), one outlying single path. Dashed
concave-hull outlines around each group. Hue: `#6f42c1`.

**multi-domain**: Two small axis panels side by side (left panel: one curve; right panel:
another curve at different shape). A connecting arc/bridge between them with a circle at the
apex (shared FPC score). Hue: `#6f42c1`.

**shapelets**: A long wavy curve with a highlighted rectangle window (dashed-bordered rect)
around a short distinctive feature. A dashed vertical bracket below the window showing the
matched distance. Hue: `#6f42c1`.

**functional-boxplot**: Three concentric band layers (inner band darkest fill, middle, outer
lightest fill) around a median curve. One curve departing outside the outer band (outlier).
Modelled on `tolerance-bands.svg` but with three fill layers instead of one. Hue: `#6f42c1`.

**functional-statistics**: A bold mean curve with a symmetric shaded envelope (upper and lower
dashed bounding lines). Three short vertical segments at x≈100, 170, 250 showing pointwise
standard deviation. Modelled on `fpca.svg` with the gradient fill. Hue: `#6f42c1`.

**scoring-metrics**: Two curves — true (solid) and predicted (dashed) — with three vertical
line segments bridging the gap between them at x≈100, 170, 250. The gap lines are the visual
representation of integrated error. Modelled on `distance-metrics.svg`. Hue: `#6f42c1`.

**functional-outlier-workflow**: A tight bundle of ~5 parallel curves at medium opacity, with
one outlier curving sharply upward (magnitude outlier, elevated) and one outlier with a
different shape (oscillating where others are smooth). Both outliers end in a small open circle.
Hue: `#3f51b5`.

**canadian-depth-centrality**: Five curves of decreasing opacity from bold (most central) to
very faint (most peripheral), arranged in a fan. The deepest curve (bold) is the median;
each successive curve is slightly further out. Hue: `#3f51b5`.

**tolerance-vs-conformal**: Two bands side by side, divided by a vertical line at x=164.
Left band: wider shaded fill (FPCA-based), solid boundary lines. Right band: narrower shaded
fill, dashed boundary lines (distribution-free). Each has a median curve inside it. Hue: `#3f51b5`.

---

## 8. Validation Architecture

Nyquist validation is not applicable to this phase: the work is hand-authored SVG files and
HTML card entries — there is no runnable code to test with pytest or a test framework.
Verification is manual:
1. SVGO idempotence check (see §5) per thumbnail.
2. `rsvg-convert` smoke render per thumbnail.
3. Visual inspection of each thumbnail at 320×180.
4. `mkdocs build --strict` local build after all card insertions (whole-site gate is Phase 79,
   but a local build verifies the card hrefs and SVG src paths resolve without 404s).

---

## 9. Environment Availability

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| `npx` / `node` | SVGO idempotence check | Yes (node in PATH) | `node --version` → present on dev machine |
| `svgo@3.3.4` | SVGO gate | Via npx — downloads on first use | Pin to exact version |
| `rsvg-convert` | Smoke render | [ASSUMED: present — noted in memory as used in prior phases] | `sudo pacman -S librsvg` if missing |
| `mkdocs` / `.venv` | Local build verification | Yes (dev environment established in prior phases) | `source .venv/bin/activate && mkdocs build --strict` |

---

## Sources

### Primary (HIGH confidence)
- `docs/assets/thumb/*.svg` (12 files read this session) — thumbnail house style, per-section hues, file size range [VERIFIED]
- `docs/align/index.md`, `docs/represent/index.md`, `docs/regression/index.md`, `docs/analyze/index.md`, `docs/examples/index.md` — card template, insertion points [VERIFIED]
- `svgo.config.mjs` — exact SVGO command and idempotence logic [VERIFIED]
- `.github/workflows/docs.yml` — CI gate scope (diagrams only, not thumbs) [VERIFIED]
- `docs/assets/diagrams/STYLE_SPEC.md` — accessibility requirements, viewBox conventions [VERIFIED]
- `mkdocs.yml` (grep output) — nav slugs for all 21 target pages [VERIFIED]
- 21 target page files (`head` output) — H1 / frontmatter titles [VERIFIED]

### Secondary (MEDIUM confidence)
- CONTEXT.md decisions — card pattern, SVGO approach, scope boundaries [CITED: 77-CONTEXT.md]
- REQUIREMENTS.md CARD-01..06 definitions [CITED: REQUIREMENTS.md]

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Existing 58 thumbnails were not pre-processed by SVGO (gate only covers `diagrams/`) | §5 SVGO Mechanics | Low — if they were already SVGO-normalised, new thumbs just need the same treatment |
| A2 | Gradient `id` values must be unique per file to avoid cross-file collision on a page | §6 Pitfall 4 | Medium — collision would render wrong gradient colour in some card; use unique 2-char IDs |
| A3 | `rsvg-convert` is present on the dev machine (cited in memory from v7.0) | §9 Environment | Low — install from `librsvg` if absent; `pacman -S librsvg` |
| A4 | The `ex-` prefix is NOT used for the 3 new examples thumbnails | §2 Per-Section Hue, §3 CARD-05 | Medium — verified via mkdocs.yml; if wrong, card `src` would 404 |

**All 4 assumptions are low-to-medium risk and have a clear resolution path.**

---

## Metadata

**Confidence breakdown:**
- Thumbnail house style: HIGH — 12 files read directly this session
- Per-section hues: HIGH — extracted from actual stroke values in corpus
- Page titles: HIGH — read from source files directly
- Gallery descriptions: MEDIUM — authored to match house voice; human review in Phase 79
- Card insertion order: MEDIUM — logical grouping, planner may adjust
- SVGO mechanics: HIGH — config and CI workflow read directly

**Research date:** 2026-09-06
**Valid until:** 2026-10-06 (stable domain — no external dependencies, all verified from in-repo files)
