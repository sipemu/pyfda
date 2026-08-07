# Architecture Research

**Domain:** Documentation design system — hand-authored SVG diagrams + build-time reproducible figure pipeline (fdars / pyfda MkDocs site)
**Researched:** 2026-08-07
**Confidence:** HIGH (derived from direct codebase analysis; confirmed against web sources)

---

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AUTHORING LAYER                                  │
│                                                                         │
│  ┌──────────────────────────┐   ┌─────────────────────────────────┐    │
│  │  SVG Design System       │   │  Figure Pipeline                │    │
│  │  (hand-authored)         │   │  (build-time execution)         │    │
│  │                          │   │                                 │    │
│  │  style-spec.md           │   │  scripts/docs_fig.py  ←─ rcP   │    │
│  │      ↓ (copy block)      │   │  scripts/docs_data.py ←─ CSV   │    │
│  │  diagrams/*.svg          │   │      ↑ imported via PYTHONPATH  │    │
│  │  (43 files, inline SVG)  │   │  docs/**/*.md (exec blocks)     │    │
│  └──────────────────────────┘   └─────────────────────────────────┘    │
└───────────────────┬─────────────────────────────┬───────────────────────┘
                    │                             │
                    ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BUILD LAYER                                      │
│                                                                         │
│  MkDocs Material (mkdocs build --strict)                                │
│    ├── markdown-exec plugin  →  exec blocks  →  inline SVG figures      │
│    ├── docs/hooks.py         →  PYTHONPATH fallback for mkdocs serve    │
│    └── docs/**/*.md          →  SVG <img> references (../assets/...)   │
│                                                                         │
│  Post-build gate:                                                       │
│    scripts/check_docs_figures.py site/   →  exits 1 if any traceback   │
└───────────────────┬─────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                                     │
│                                                                         │
│  site/  (HTML, inline SVGs, embedded matplotlib SVG figures)            │
│    Deployed: GitHub Pages (https://sipemu.github.io/pyfda/)             │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Lives In | Changes By |
|-----------|---------------|----------|------------|
| Style spec | Single source of truth for palette, typography, spacing, viewBox | `.planning/research/style-spec.md` (or `docs/assets/diagrams/STYLE.md`) | Edited once; applied globally |
| Canonical `<style>` block | The verbatim CSS class definitions to paste into every SVG | Part of style spec | Updated spec triggers sweep of all diagrams |
| Individual SVG diagrams | Concept visualisation of one FDA method; hand-authored | `docs/assets/diagrams/*.svg` | Per-diagram authoring sweeps (section-by-section) |
| Card / thumb SVGs | Section index hero images (not method diagrams) | `docs/assets/cards/*.svg`, `docs/assets/thumb/*.svg` | Treated separately; lower accuracy requirement |
| `docs_fig.py` | Matplotlib style, `fig()` factory, `render()` → inline SVG string | `scripts/docs_fig.py` | Only when style or render behavior changes |
| `docs_data.py` | Canonical dataset loaders (`load_*` functions) for build-time use | `scripts/docs_data.py` | Only when adding new datasets |
| Example pages | Narrative + exec blocks that call `docs_fig` / `docs_data` | `docs/examples/*.md`, `docs/**/*.md` | Section-by-section example sweep |
| Build gate | Detects silent exec-block tracebacks after `mkdocs build` | `scripts/check_docs_figures.py` | Maintained alongside pipeline |
| Scorecard | Mechanical A+ criteria check per page | `scripts/a_plus_scorecard.py` | Maintained alongside quality bar |

---

## Diagram Design System

### The De-Facto Baseline (what already exists)

35 of 43 diagrams already share a consistent pattern:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none"
     role="img" aria-label="[description]">
  <style>
    .ttl{font:700 17px system-ui,-apple-system,sans-serif;fill:#1a1a2e}
    .sub{font:400 12px system-ui,sans-serif;fill:#6c757d}
    .lab{font:700 13px system-ui,sans-serif}
    .sm{font:400 11px system-ui,sans-serif;fill:#495057}
    .mono{font:600 12px ui-monospace,monospace}
  </style>
  <!-- Title + subtitle -->
  <text class="ttl" x="360" y="26" text-anchor="middle">...</text>
  <text class="sub" x="360" y="46" text-anchor="middle">...</text>
  <!-- Three-panel layout: input | method box | output -->
  ...
</svg>
```

The 8–9 outlier diagrams use `font-family='Segoe UI, system-ui, sans-serif'` as an SVG attribute instead of the `<style>` block, have non-standard viewBox sizes (480, 520, 400, 250 height), and use ad-hoc fill colors rather than the Bootstrap-ish palette. These are the diagrams that need the most work.

### Design Tokens — Canonical Spec

The style spec formalizes what is already implicitly the standard.

**viewBox Convention**
- Standard: `viewBox="0 0 720 300"` — wide landscape, fits content column
- Tall variant (for multi-row content): `viewBox="0 0 720 420"` — use sparingly; prefer 300
- Never use pixel `width`/`height` attributes alongside `viewBox` (breaks responsive scaling)

**Typography Classes (canonical `<style>` block)**

| Class | Role | Spec |
|-------|------|------|
| `.ttl` | Diagram title | `font:700 17px system-ui,-apple-system,sans-serif; fill:#1a1a2e` |
| `.sub` | Subtitle / caption | `font:400 12px system-ui,sans-serif; fill:#6c757d` |
| `.lab` | Panel header label | `font:700 13px system-ui,sans-serif` (fill varies by panel accent) |
| `.sm`  | Small annotation | `font:400 11px system-ui,sans-serif; fill:#495057` |
| `.mono` | API function name | `font:600 12px ui-monospace,monospace` (fill matches accent) |

**Palette — Structural Colours** (used for backgrounds, borders, axes, arrows)

| Token | Hex | Role |
|-------|-----|------|
| `text-dark` | `#1a1a2e` | Title text |
| `text-body` | `#495057` | Body annotations |
| `text-muted` | `#6c757d` | Subtitles, secondary labels |
| `border-muted` | `#ced4da` | Panel borders (neutral panels) |
| `stroke-axis` | `#adb5bd` | Axis lines, arrows, grid |
| `bg-neutral` | `#f8f9fa` | Input/raw-data panel background |
| `bg-white` | `#ffffff` | Inner item cards |

**Palette — Semantic Accent Colours** (used for method/output panels and curve strokes)

| Token | Hex | Role | Usage example |
|-------|-----|------|---------------|
| `accent-blue` | `#0d6efd` | Primary method accent | Fdata, smoothing, basis |
| `accent-blue-tint` | `#eaf1ff` | Tinted panel background | Blue-accent panel bg |
| `accent-blue-border` | `#b6d0ff` | Inner card border | Inside blue panels |
| `accent-green` | `#198754` | Basis, reconstruction | Basis representation |
| `accent-green-tint` | `#eafaf1` | Green panel bg | Basis panel |
| `accent-orange` | `#fd7e14` | Alignment, warping | Elastic alignment, SRSF |
| `accent-orange-tint` | `#fff4ea` | Orange panel bg | Alignment panels |
| `accent-red` | `#dc3545` | Outliers, anomalies | Outlier detection |
| `accent-purple` | `#6f42c1` | Classification, FPCA | FPCA components |
| `accent-indigo` | `#3f51b5` | Primary curve color | Same as docs_fig primary |

**Stroke Weights**

| Context | Weight |
|---------|--------|
| Panel border | `1.5` |
| Axis line | `1.2` |
| Secondary / background curves | `1.6–1.8` |
| Primary / highlighted curve | `2.4–2.8` |
| Mean / reference line | `2.4–2.6` |
| Arrow shaft | `2.0` |

**Standard Three-Panel Layout** (the dominant pattern)

```
x=24   x=220  x=272  x=448  x=500  x=696
  [  Input panel  ] → [  Method box  ] → [  Output panel  ]
  y=70                                              y=258
```
- Panels: `rx="12"` rounded corners
- Arrow: simple `<path d="M... h34"> + arrowhead polygon` at neutral stroke `#adb5bd`
- Title at `y=26` (`.ttl`), subtitle at `y=46` (`.sub`)
- Panel header at `y=94` (`.lab`), sub-caption at `y=112` (`.sm`)

### Reusable SVG Snippet Patterns

These four shapes repeat across diagrams. Authoring consistency means copying these exactly rather than redrawing.

**1. Horizontal arrow (between panels)**
```xml
<path d="M228 164 h34" stroke="#adb5bd" stroke-width="2"/>
<path d="M262 164 l-9 -5 v10 z" fill="#adb5bd"/>
```

**2. Neutral input panel shell**
```xml
<rect x="24" y="70" width="196" height="188" rx="12" fill="#f8f9fa" stroke="#ced4da" stroke-width="1.5"/>
<text class="lab" x="122" y="94" text-anchor="middle" fill="#495057">Panel Title</text>
<text class="sm"  x="122" y="112" text-anchor="middle">Short description</text>
```

**3. Blue accent method/output panel shell**
```xml
<rect x="272" y="70" width="176" height="188" rx="12" fill="#eaf1ff" stroke="#0d6efd" stroke-width="1.5"/>
<text class="mono" x="360" y="98" text-anchor="middle" fill="#0d6efd">function_name()</text>
<text class="sm"   x="360" y="118" text-anchor="middle">sub-description</text>
```

**4. Axis pair (mini plot background)**
```xml
<line x1="0" y1="120" x2="156" y2="120" stroke="#adb5bd" stroke-width="1.2"/>
<line x1="0" y1="0"   x2="0"   y2="120" stroke="#adb5bd" stroke-width="1.2"/>
```

### File Naming Convention

| Pattern | When to use |
|---------|-------------|
| `{topic}.svg` | Single-concept diagrams (`smoothing.svg`, `fpca.svg`) |
| `{qualifier}-{topic}.svg` | Method variants (`elastic-alignment.svg`, `advanced-spm.svg`) |
| `{topic1}-{topic2}.svg` | Comparison/compound diagrams (`alignment-comparison.svg`) |
| `ex-{dataset}-{topic}.svg` | Example-specific diagrams (`ex-sonar-tsrvf.svg`) |

All names: kebab-case, no version suffixes. File corresponds 1-to-1 with the doc page that references it.

### Method-Accuracy Review Protocol

Each diagram must be reviewed against the method it depicts — not just for style. The review gate per section asks:

1. Does the input panel show what the method actually takes? (data type, structure)
2. Does the middle panel name the actual fdars API function and its key parameters?
3. Does the output panel show what the method actually produces? (output type, key property)
4. Are any mathematical symbols or arrow directions correct?
5. Does the diagram show the typical/default case rather than an edge case?

Review is done on the built site (rendered HTML), not the raw SVG, because viewBox scaling and font rendering differ in the browser.

---

## Figure / Example Pipeline

### Build-Time Execution Architecture

```
Makefile: export PYTHONPATH := scripts
           mkdocs build --strict
               │
               ▼
        markdown-exec plugin
        (per-page, per-block)
               │
   ┌───────────┴────────────┐
   │  ```python exec="1"    │
   │  html="1"              │
   │  source="above"        │
   │  ...                   │
   │  print(render(f))      │
   │  ```                   │
   └───────────┬────────────┘
               │ captured stdout
               ▼
      inline SVG <div class="fdars-figure">
      embedded in page HTML
               │
               ▼
        site/*.html
               │
               ▼
  scripts/check_docs_figures.py site/
  → exits 1 if Traceback / ModuleNotFoundError / exec-error in HTML
```

### The `scripts/` Layer

Two scripts provide everything exec blocks need:

**`docs_fig.py`** — Style and render
- Sets `plt.rcParams` at module import time (runs once per build, module cached by Python)
- `fig(nrows, ncols, **kwargs)` → thin `plt.subplots` wrapper using the themed defaults
- `render(figure)` → strips XML preamble, returns `<div class="fdars-figure"><svg ...></svg></div>`
- The FDARS_COLORS list matches the indigo-primary MkDocs Material theme and the SVG diagram accent palette

**`docs_data.py`** — Deterministic datasets
- All loaders: `(argvals, X, meta)` tuple — consistent contract for all datasets
- Paths resolved relative to the script file (`../docs/data/`), works at build time and interactively
- `load_penicillin()` is the only synthetic dataset; it is seeded (`default_rng(20260805)`) — deterministic
- Real datasets (growth, canadian_weather, tecator, phoneme, wine, sonar) ship in `python/fdars/data/` (bundled with wheel) AND `docs/data/` (for docs build)

### Determinism Requirements for Exec Blocks

Every exec block must be deterministic so the built site does not change across runs without a code change:

| Source of randomness | Mitigation |
|---------------------|-----------|
| Simulated data | Use `np.random.default_rng(<fixed_seed>)` |
| Stochastic algorithms | Seed via `rng=` parameter or `np.random.seed()` |
| Real datasets | Inherently deterministic; always use `docs_data.load_*()` |
| Floating-point path ordering | Stable sort, fixed numpy seed |

The A+ scorecard checks for this: `seeded = real or (not uses_rng) or seed_pattern_present`.

### Matplotlib Style: What Is Established

The `docs_fig.py` rcParams block is already the canonical style. Key decisions already made:

- `figure.figsize = (7.5, 4.0)` — fits the content column width
- `savefig.transparent = True` — SVG figures have transparent background; page bg shows through
- `axes.spines.top/right = False` — clean minimal frame
- `axes.grid = True, grid.alpha = 0.22` — subtle grid
- `font.size = 11, axes.titlesize = 12.5, axes.titleweight = "600"` — legible, matches site typography
- `legend.frameon = False` — inline style matches diagram aesthetic

What is NOT yet established (gaps that matter for the example sweep):
- No `axes.labelsize` / `xtick.labelsize` / `ytick.labelsize` set explicitly — they inherit `font.size=11` which is fine but should be confirmed consistent
- No `figure.titlesize` — suptitle has no explicit size token
- Multi-panel (`nrows>1`) figures are not demonstrated in `docs_fig.py` — the `fig()` wrapper passes `**kwargs` to `plt.subplots`, so it works, but `figsize` needs to be overridden per-call for tall figures

---

## Data / Asset Flow

```
docs/data/*.csv          ─────────────────────────────────────────────►
python/fdars/data/*.csv  ──── docs_data.load_*() ──► exec blocks ──► figures ──► site/*.html

docs/assets/diagrams/*.svg ──(img reference in .md)──► site/*.html

scripts/docs_fig.py  ──► rcParams at import  ──► fig()/render() ──► exec blocks
scripts/docs_data.py ──► load_*() ──────────────────► exec blocks

Style spec (doc) ──► (author copies <style> block) ──► diagrams/*.svg
```

Key constraint: datasets live in BOTH `docs/data/` (for build-time) and `python/fdars/data/` (bundled in wheel). When a new dataset is added it goes in both places. `docs_data.py` loads from `docs/data/` via relative path.

---

## Recommended Project Structure (Documentation System)

```
docs/
├── assets/
│   ├── diagrams/         # Hand-authored concept SVGs (one per page)
│   │   ├── STYLE.md      # ← NEW: canonical style spec / token reference
│   │   └── *.svg         # 43 existing diagrams
│   ├── cards/            # Section hero SVGs (8 files, lower accuracy req)
│   └── thumb/            # Thumbnail variants
├── stylesheets/
│   └── extra.css         # .fdars-diagram and .fdars-figure CSS rules

scripts/
├── docs_fig.py           # matplotlib theme + render(); NEVER import-side-effects outside rcParams
├── docs_data.py          # dataset loaders; all return (argvals, X, meta)
├── check_docs_figures.py # post-build gate: catches silent exec tracebacks
└── a_plus_scorecard.py   # per-page A+ quality gate

.planning/research/
└── STYLE_SPEC.md         # ← alternative location for style spec (pre-authoring artifact)
```

The single most important new file is `docs/assets/diagrams/STYLE.md` (or equivalent). It is the style spec that every diagram author (including AI-assisted authoring) copies from. It must contain the verbatim canonical `<style>` block, the palette table, the viewBox convention, and the panel layout measurements.

---

## Architectural Patterns

### Pattern 1: Style Spec First, Then Sweep

**What:** Write the style spec document before touching any diagram. The spec is the authority; each diagram is a client of the spec.

**When to use:** At the start of the milestone, before any section sweep begins.

**Trade-offs:** Adds one upfront step but prevents the "gradual divergence" problem where fixing diagrams introduces new inconsistency. Without the spec, fixing 10 diagrams in a sweep still leaves them inconsistent with each other.

**Concrete form for this project:** The spec should be a markdown file that contains:
1. The verbatim `<style>` block to copy-paste into every SVG
2. Palette table (token name → hex → role)
3. Stroke weight table
4. viewBox convention + layout measurements
5. The four reusable snippet patterns (arrow, neutral panel, accent panel, axis pair)
6. The naming convention rules

### Pattern 2: Three-Panel Structure as the Default

**What:** Every concept diagram defaults to `[input] → [method] → [output]`. Deviate only when the concept genuinely requires it.

**When to use:** For all method-explanation diagrams. For comparison diagrams, use a 2-row or 2-column grid.

**Trade-offs:** Forces consistency and makes diagrams scannable as a set. The cost is slight visual monotony, which is outweighed by the clarity benefit for technical documentation.

**Application here:** When correcting diagrams that currently use idiosyncratic layouts (covariance-functions, clustering, depth-functions), bring them to the three-panel structure unless there is a strong reason not to.

### Pattern 3: exec Block Self-Containment with Shared Imports

**What:** Each exec block imports `from docs_fig import fig, render` and `from docs_data import load_*` at the top of the block. The block is otherwise fully self-contained and runnable as a script.

**When to use:** In every exec block in the example sweep.

**Trade-offs:** Slight repetition of imports, but makes each block independently runnable/debuggable without MkDocs context. Never use page-level shared state between exec blocks (markdown-exec does not guarantee ordering).

**Key example:**
```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_growth

age, X, meta = load_growth()
f, ax = fig()
ax.plot(age, X.T, alpha=0.2, color="#3f51b5", lw=1)
ax.set(title="Growth curves", xlabel="age (years)", ylabel="height (cm)")
print(render(f))
```

### Pattern 4: Section-by-Section Gate

**What:** Complete a section's diagrams, review on the built site, get human sign-off, then move to the next section.

**When to use:** Throughout the milestone, for both diagram sweeps and example sweeps.

**Trade-offs:** Slower throughput than doing all diagrams then all reviews, but avoids compounding errors across sections and ensures method accuracy is validated before moving forward.

**Build order implication:** Establish the style spec (and build it into the first diagrams) before starting the first section, so the review of the first section also validates the spec itself.

---

## Anti-Patterns

### Anti-Pattern 1: Fixing Diagrams Without the Style Spec

**What people do:** Open a diagram that looks wrong, fix the specific accuracy issue, move on.

**Why it's wrong:** The diagram may be method-accurate after the fix but still inconsistent in font, palette, or viewBox with the 35 diagrams that use the `<style>` block pattern. Each individual fix adds inconsistency because there is no single standard to fix to.

**Do this instead:** Write the spec first. Fix diagrams against the spec. Every touched diagram gets the canonical `<style>` block, correct viewBox, and standard layout.

### Anti-Pattern 2: exec Blocks that Import fdars Without Checking the API

**What people do:** Copy a code pattern from an old example, update it to use the "current" API from memory.

**Why it's wrong:** The fdars API has evolved (the lambda_ default fix, the recon fix are recent examples). Examples silently produce wrong output or raise errors that ship as tracebacks via markdown-exec's silent failure mode.

**Do this instead:** Before writing an exec block for a method, check the reference page and the actual Python module (`python/fdars/*.py`, `src/*_mod.rs`) for the current signature. Run the block interactively (`PYTHONPATH=scripts python -c "..."`) before adding it to the docs.

### Anti-Pattern 3: Committing Figures as PNG/Static Images

**What people do:** Generate a figure once, screenshot it, commit the PNG.

**Why it's wrong:** The figure becomes stale the moment the API or dataset changes. The whole point of markdown-exec is that figures are always in sync with the code.

**Do this instead:** All data-driven figures must go through the exec block / `render()` pipeline. The only committed visual assets are hand-authored SVG diagrams.

### Anti-Pattern 4: Diagrams That Depict Aspirational Rather Than Actual Behavior

**What people do:** Draw a diagram showing three clearly separated clusters with perfect centroids, or a smooth FPCA decomposition with orthogonal components that look ideal.

**Why it's wrong:** Users run the actual method on real data and the output does not match the diagram, eroding trust.

**Do this instead:** Diagrams should show the *concept* but use realistic-looking curves (slightly irregular, overlapping) and caption them with method names, not idealized results. The worked examples show actual output; the diagrams show the idea.

### Anti-Pattern 5: Non-Deterministic exec Blocks

**What people do:** Use `np.random.randn()` without a seed, trusting that the result will be "representative."

**Why it's wrong:** Every build produces different output. The figure caption may reference specific numbers that change. CI comparison is impossible.

**Do this instead:** All random data uses `rng = np.random.default_rng(<fixed_seed>)`. All real data goes through `docs_data.load_*()`. The A+ scorecard checks this mechanically.

---

## Build Order for the Milestone

The ordering constraint is: style spec must precede all diagram work; `docs_fig` / `docs_data` must be stable before example sweeps begin. Section sweeps can then proceed serially with human review gates between them.

```
Phase 1: FOUNDATION
  ├── Write docs/assets/diagrams/STYLE.md (style spec + token table + snippet patterns)
  ├── Audit which 8-9 diagrams deviate from the standard (viewBox, font-family, palette)
  └── No diagram edits yet — just spec + audit list

Phase 2: learn/ SECTION
  ├── Apply spec to all learn/ diagrams (6 pages × ~1 diagram each)
  ├── Correct any method accuracy issues
  ├── Verify example exec blocks run against current API
  └── Review gate: mkdocs build --strict → human site review

Phase 3: represent/ SECTION
  ├── Apply spec to represent/ diagrams (7 pages)
  ├── depth-functions.svg and streaming-depth.svg are likely complexity cases
  └── Review gate

Phase 4: align/ SECTION
  ├── Apply spec to align/ diagrams (6 pages)
  ├── elastic-alignment, advanced-alignment, tsrvf are method-accuracy-critical
  └── Review gate

Phase 5: analyze/ SECTION
  ├── Apply spec to analyze/ diagrams (8 pages)
  ├── clustering.svg, gmm-clustering.svg, depth-functions adjacent diagrams need format migration
  └── Review gate

Phase 6: regression/ SECTION
  ├── Apply spec to regression/ diagrams (12 pages — largest section)
  ├── Most likely to need deeper research: elastic-regression, conformal-prediction
  └── Review gate

Phase 7: monitoring/ SECTION
  ├── Apply spec to monitoring/ diagrams (3 pages)
  ├── spm.svg uses non-standard viewBox 720×480 — needs migration
  └── Review gate

Phase 8: examples/ SWEEP
  ├── Verify all 17 example pages run against current fdars API
  ├── Richer narrative pass (why/interpretation)
  ├── Improved figure styling (consistent use of docs_fig, consistent colors)
  ├── Add new examples for under-documented capabilities
  └── Review gate: scorecard must pass (a_plus_scorecard.py --gate)
```

**Foundation must exist before Phase 2 begins.** All section phases can be reviewed one at a time. The examples sweep is last because it depends on the API being verified correct (example blocks may expose binding issues), and because the diagrams serve as concept anchors that the examples reference.

---

## Integration Points

### SVG Diagrams ↔ Markdown Pages

Diagrams are referenced as:
```markdown
![Description — concept diagram](../assets/diagrams/name.svg){ .fdars-diagram }
```
The `.fdars-diagram` CSS class (in `docs/stylesheets/extra.css`) controls max-width, display, and margin. The alt text is the primary accessibility text — it should match the SVG `aria-label`.

### exec Blocks ↔ Build Pipeline

exec blocks run in the process that executes `mkdocs build`. `PYTHONPATH=scripts` is set by the Makefile. `docs/hooks.py` provides a fallback for `mkdocs serve`. There is no caching of exec block results across builds — full rebuild re-executes all blocks. For the current ~50-page scope this is acceptable (typical build: 60–120s with all figures).

### docs_data.py ↔ docs/data/ vs python/fdars/data/

`docs_data.py` loads from `docs/data/` (path relative to the script). The same CSVs also ship in the wheel from `python/fdars/data/`. If a new dataset is added for an example, it goes in `docs/data/` (for the docs build) and optionally in `python/fdars/data/` (if it should ship with the wheel). The `load_penicillin()` synthetic generator does not need a CSV file.

---

## Scaling Considerations

The documentation system does not scale to "users" — it scales to the number of pages and diagrams being maintained. At the current scope (~50 diagrams, ~50 exec-block pages):

| Concern | Current (50 pages) | If 150 pages |
|---------|-------------------|--------------|
| Full build time | 60–120s (acceptable) | 3–6 min (painful for iteration) |
| Diagram consistency | Style spec + manual copy | Same — spec still works |
| exec block maintenance | Per-page API check | Consider a centralized smoke-test that imports all example modules |
| Dataset coverage | 7 loaders sufficient | May need additional loaders in docs_data.py |

No architectural change is needed within this milestone's scope. The check_docs_figures.py post-build gate and the a_plus_scorecard.py are the correct quality mechanisms at this scale.

---

## Sources

- Direct codebase analysis: `scripts/docs_fig.py`, `scripts/docs_data.py`, `scripts/check_docs_figures.py`, `scripts/a_plus_scorecard.py`, `Makefile`, `mkdocs.yml`, `docs/hooks.py` (HIGH confidence — primary source)
- Direct inspection of all 43 SVG files in `docs/assets/diagrams/` (HIGH confidence)
- [Customizing Matplotlib with style sheets and rcParams](https://matplotlib.org/stable/users/explain/customizing.html) — rcParams documentation (MEDIUM confidence)
- [Markdown Exec usage and gallery](https://pawamoy.github.io/markdown-exec/usage/) — exec block mechanics (MEDIUM confidence)
- [Reproducible Reports with MkDocs](https://timvink.nl/reproducible-reports-with-mkdocs/) — build-time execution patterns (LOW confidence)
- [CSS custom properties / design tokens](https://penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables/) — SVG styling patterns (LOW confidence)

---

*Architecture research for: fdars documentation design system (SVG diagrams + figure pipeline)*
*Researched: 2026-08-07*
