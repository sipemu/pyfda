# Phase 1: Foundation - Research

**Researched:** 2026-08-07
**Domain:** Docs tooling — SVG linting, matplotlib determinism, MkDocs snippets, pytest-markdown-docs, CI integration
**Confidence:** HIGH (all claims grounded in files read this session or authoritative source + registry verification)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**SVGO Toolchain (FND-02)**
- D-01: Zero-install `npx svgo@<pinned>` — no package.json, no node_modules. Pin version for reproducibility. Reversible.
- D-02: SVGO runs as check-only lint gate — verifies conformance but NEVER rewrites hand-authored SVGs.
- D-03: Gate scope is optimization-safety only — preserve `<style>`, IDs, `<desc>`, `viewBox`, `role`/`aria-label`. STYLE_SPEC conformance (width 720, correct classes, required attrs) stays a human review-gate concern this phase.

**Test Harness (FND-05)**
- D-04: Smoke-test `pytest-markdown-docs` before locking it in. If cross-fence state works → lock in; if not → fall back per Claude's discretion.
- D-05: Smoke-test on a page with genuine cross-fence state dependency, chosen by planner.
- D-06: `conftest.py` globals hook exposes `np`, `plt`, `fdars`.

**DOCS_FAST (FND-06)**
- D-07: DOCS_FAST is speed-only. Full build (DOCS_FAST unset) is the source of truth. Determinism NOT required in fast mode.
- D-08: Central helper in `docs_fig.py`: `fast(full, fast_value)` reads env var once. DRY pattern.

**Enforcement & Verification**
- D-09: Wire guardrails into CI now (extend existing docs CI workflow), not just manually.
- D-10: SVGO lint gate blocks on ALL diagrams immediately.
- D-11: Doc-test gate grows with coverage — blocks CI only on smoke-test page now; expands page-by-page in Phase 9.

### Claude's Discretion
- Test-harness fallback if cross-fence state fails: (a) custom conftest.py fence-exec harness with shared namespace, or (b) consolidate-fences authoring convention. Pick based on how pytest-markdown-docs fails.
- Smoke-test page selection.
- DOCS_FAST semantics and wiring (decided as D-07/D-08 above).
- `pymdownx.snippets` / `docs/includes/` organization.
- Pre-commit hooks: optional.
- Determinism mechanics (svg.hashsalt, RNG seeding): standard implementation.

### Deferred Ideas (OUT OF SCOPE)
- A11Y-01: Long-form `<title>`/`<desc>` + `aria-labelledby` for complex diagrams — v2.
- EX2-01: Editorial consolidation of overlapping example pages — v2.
- Fixing example pages to run against the current API — Phase 9.
- Method-semantic research flags (regression/, monitoring/) — Phases 7-8.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FND-01 | SVG style spec at `docs/assets/diagrams/STYLE_SPEC.md` codifying palette, five CSS classes, stroke weights, viewBox 720, allowed heights, copy-paste `<style>` block | Existing SVG baseline read; canonical `<style>` block extracted verbatim from conforming diagrams |
| FND-02 | SVGO config (`svgo.config.mjs`) losslessly lints diagrams while preserving `<style>`, IDs, `<desc>`, `viewBox`, `role`/`aria-label` | Tested svgo@3.3.4 stdout on real diagram; exact plugins-to-disable identified |
| FND-03 | Deterministic figures — `docs_fig.py` sets `svg.hashsalt`; stochastic blocks seed RNG | `svg.hashsalt` rcParam confirmed present; default is `None` (non-deterministic); seam confirmed |
| FND-04 | `pymdownx.snippets` enabled; shared dataset-loading preambles factored into `docs/includes/` | `pymdownx.snippets` confirmed absent from `mkdocs.yml`; `docs/includes/` does not exist yet; 114 `docs_data` imports across examples quantified |
| FND-05 | Example fences runnable as tests via `pytest-markdown-docs`; `conftest.py` globals hook | pytest-markdown-docs 0.9.2 on PyPI; execution model documented; cross-fence state finding documented |
| FND-06 | DOCS_FAST lowers expensive iteration counts for local builds | `DOCS_FAST` env var confirmed absent from codebase; expensive params identified (`n_perm`, `max_iter`, `nb`, `oversampling`) |
</phase_requirements>

---

## Summary

Phase 1 establishes six tooling guardrails that protect every subsequent phase's work. All six are net-new additions — nothing in the repo conflicts with them, but several implementation details require care.

The most consequential finding is about the smoke-test page selection for FND-05. After reading all example pages, every code fence across `canadian-weather.md` and `canadian-seasonal.md` is **self-contained**: each fence re-imports `load_canadian_weather`, re-declares `rng`, and rebuilds `long`/`fd` from scratch. There is no cross-fence state dependency in the current examples. This means the D-04 smoke-test will likely pass trivially (each fence executes in isolation with the injected globals), and `pytest-markdown-docs` will work without the continuation feature. The planner should select the page with the most expensive imports (e.g., `docs/examples/canadian-weather.md` with 8 fences importing `fdars.regression`) as the smoke-test.

For FND-02, testing `npx svgo@3.3.4` against `elastic-alignment.svg` (the canonical conforming diagram) revealed exactly which default plugins must be disabled: `inlineStyles`, `minifyStyles`, `removeUnknownsAndDefaults`, `cleanupIds`, and `removeDesc` are the dangerous ones. The check-only gate pattern uses `svgo --output -` (stdout mode) and then `diff` against the source; a zero-diff means the diagram is already optimally structured under the safe config.

For FND-03, `svg.hashsalt` rcParam is confirmed present in matplotlib 3.10.8 (installed in the project venv) and defaults to `None`. Setting it to any non-empty string (e.g., `"fdars-docs"`) makes element IDs deterministic. The `scripts/docs_fig.py` file currently has no hashsalt setting and no DOCS_FAST logic.

**Primary recommendation:** Implement in the order: STYLE_SPEC.md → svgo.config.mjs + gate test → docs_fig.py changes (hashsalt + DOCS_FAST) → mkdocs.yml snippets + docs/includes/ → conftest.py + smoke-test → CI extension. This is the tracer-bullet sequence; the svgo gate (FND-02) is the end-to-end CI proof.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| SVG style specification | Authoring/documentation | — | Defines the hand-authored SVG contract; no runtime component |
| SVGO lint gate | CI/workflow | Local npx invocation | Verification is CI's job; local invocation is a dev convenience |
| Matplotlib SVG determinism | Build-time (mkdocs build) | scripts/docs_fig.py | rcParam must be set before any figure is rendered; docs_fig.py is the central render entrypoint |
| DOCS_FAST gate | Build-time (docs_fig.py helper) | Individual exec blocks | Helper reads env var once; blocks call it — prevents scattered os.environ checks |
| pymdownx.snippets | MkDocs plugin config | docs/includes/ snippets | Extension is configured in mkdocs.yml; includes live in docs/includes/ |
| Doc-test harness | pytest + CI | conftest.py globals | pytest-markdown-docs runs under pytest; CI gates on a specific page list |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| svgo | 3.3.4 [VERIFIED: npm registry] | SVG lint/optimization via CLI | The canonical Node.js SVG optimizer; 36M weekly downloads; stable v3 API |
| pytest-markdown-docs | 0.9.2 [VERIFIED: pip index versions] | Runs Python code fences as pytest tests | Maintained by Modal Labs; integrates with standard pytest ecosystem |
| pymdownx.snippets | bundled with pymdown-extensions [VERIFIED: mkdocs.yml] | Include shared file fragments in Markdown | Already part of the installed MkDocs Material stack; zero new dependency |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| matplotlib | 3.10.8 (installed) [VERIFIED: .venv] | Figure rendering via `svg.hashsalt` | Already the project figure engine; hashsalt just requires a rcParam set |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| npx svgo@3.3.4 (zero-install) | committed node_modules | node_modules would add ~10 MB to repo and create Node.js maintenance surface in a Rust/Python project; decision locked as D-01 |
| pytest-markdown-docs | pytest-codeblocks | pytest-codeblocks has a similar approach but less active maintenance; D-04 locks pytest-markdown-docs unless smoke-test fails |

**Installation (docs CI and local):**
```bash
# Python packages (add to docs/requirements.txt)
pip install pytest-markdown-docs

# SVGO (zero-install, no npm install needed)
npx svgo@3.3.4 --version   # verifies cache/download
```

---

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| svgo@3.3.4 | npm | ~12 yrs (2012) [VERIFIED: npm registry] | 36M/wk [VERIFIED: npm registry] | github.com/svg/svgo [VERIFIED: npm registry] | SUS (seam flagged v4.0.2 as "too-new"; v3.3.4 is the stable v3 dist-tag) | Approved — use pinned `svgo@3.3.4`, not `latest` |
| pytest-markdown-docs@0.9.2 | PyPI | Active, 0.9.2 released 2026-03-23 [VERIFIED: PyPI] | Unknown [SUS: unknown-downloads] | github.com/modal-labs/pytest-markdown-docs [VERIFIED: PyPI] | SUS (unknown-downloads) | Approved — backed by Modal Labs; confirmed on PyPI; planner must add checkpoint:human-verify before install |

**Packages removed due to SLOP verdict:** none

**Packages flagged as suspicious [SUS]:**
- `svgo@3.3.4` — seam flagged because it checked latest (v4, published 2026-07-11). Pin to `svgo@3.3.4` which is the long-established v3 dist-tag. Planner adds `checkpoint:human-verify` before CI step.
- `pytest-markdown-docs@0.9.2` — low download count visibility on PyPI. Planner adds `checkpoint:human-verify` before adding to docs/requirements.txt.

*Both packages have confirmed source repositories and are installed/invocable in the current environment.*

---

## Architecture Patterns

### System Architecture Diagram

```
[Hand-authored .svg files in docs/assets/diagrams/]
          |
          v
[CI: npx svgo@3.3.4 --config svgo.config.mjs -i file.svg -o - | diff - file.svg]
          |  (gate: diff must be empty — diagram already conforms)
          |
[mkdocs build]
  |                    |
  v                    v
[markdown-exec        [pymdownx.snippets]
 exec blocks]          reads docs/includes/*.md
  |                    for --8<-- include syntax
  v
[docs_fig.py: fig() / render()]
  svg.hashsalt="fdars-docs"  (determinism)
  DOCS_FAST → fast(full, fast_val)  (speed gate)
          |
          v
[built site/: byte-identical SVG on repeated builds]
          |
          v
[pytest --markdown-docs docs/examples/smoke-page.md]
  conftest.py: pytest_markdown_docs_globals() → {np, plt, fdars}
  (CI: blocks on smoke-test page only — D-11)
```

### Recommended Project Structure (new files only)

```
docs/assets/diagrams/
└── STYLE_SPEC.md          # FND-01: palette, classes, viewBox spec, <style> block

svgo.config.mjs            # FND-02: lint config (repo root, zero-install via npx)

scripts/docs_fig.py        # FND-03, FND-06: add svg.hashsalt + fast() helper

docs/includes/             # FND-04: shared snippet fragments
└── load-canadian-weather.py.md
└── load-tecator.py.md
└── load-growth.py.md
└── load-phoneme.py.md

mkdocs.yml                 # FND-04: add pymdownx.snippets extension

conftest.py                # FND-05: pytest_markdown_docs_globals hook (repo root)

.github/workflows/docs.yml # FND-02, FND-05: add svgo gate + doc-test gate
```

---

## Pattern 1: SVGO Check-Only Gate

**What:** Run svgo in stdout mode (`-o -`), diff the output against the source file. Zero diff = diagram already conforms to the safe svgo config. Nonzero diff = the diagram would change under the optimizer = structural nonconformance.

**When to use:** CI step after checkout, before mkdocs build. Also usable locally for a quick lint of a single diagram.

**Critical insight from live test:** Running `npx svgo@3.3.4` with default settings on `docs/assets/diagrams/elastic-alignment.svg` produced a modified file that:
- Inlined the `.ttl` and `.sub` CSS classes into `style=` attributes (via `inlineStyles`)
- Removed `role="img"` (via `removeUnknownsAndDefaults`)
- Removed all comments
- Removed `<desc>` (via `removeDesc` — not present in this SVG, but relevant for others)

The diff would be nonzero for this conforming diagram under default settings. Therefore the config MUST disable these plugins.

**Example `svgo.config.mjs`:**
```js
// svgo.config.mjs — check-only config for hand-authored fdars diagrams.
// Run via: npx svgo@3.3.4 --config svgo.config.mjs -i <file.svg> -o -
// Gate: diff the output against the source — zero diff means conforming.
export default {
  plugins: [
    {
      name: "preset-default",
      params: {
        overrides: {
          // Preserve the CSS <style> block with class definitions (.ttl .sub .lab .sm .mono)
          inlineStyles: false,
          minifyStyles: false,
          // Preserve element IDs (used for <g id="...">, gradients, defs cross-references)
          cleanupIds: false,
          // Preserve <desc> elements (accessibility; may be added to diagrams)
          removeDesc: false,
          // Preserve role="img" and aria-label (accessibility attributes)
          // removeUnknownsAndDefaults strips role/aria-* that are not in SVG spec's known set
          removeUnknownsAndDefaults: false,
          // Preserve viewBox (never remove viewBox from hand-authored diagrams)
          removeViewBox: false,
        },
      },
    },
  ],
};
```

**CI shell gate (for docs.yml):**
```bash
# Lint all diagrams: fail if any would be modified by the safe svgo config.
FAILED=0
for svg in docs/assets/diagrams/*.svg; do
  diff <(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -) "$svg" \
    || { echo "SVGO: $svg would be modified"; FAILED=1; }
done
[ $FAILED -eq 0 ] || { echo "SVGO lint failed — fix diagrams above"; exit 1; }
```

**Important:** The 8 diagrams without `<style>` blocks (`clustering.svg`, `depth-functions.svg`, `spm.svg`, `seasonal-analysis.svg`, `outlier-detection.svg`, `elastic-clustering.svg`, `gmm-clustering.svg`, `covariance-functions.svg`) use inline `font-size` attributes and non-conforming `viewBox` widths (600 or 700). The SVGO gate (D-03) does NOT enforce viewBox width 720 or class names — that is human review. SVGO only checks that it would not rewrite the file (i.e., it's already optimized/structured under the safe config). These 8 diagrams will likely PASS the gate as long as they have no constructs that the safe-config plugins would touch. Verify during the smoke-test wave.

---

## Pattern 2: STYLE_SPEC Canonical `<style>` Block

**What:** The verbatim `<style>` block from the 35 conforming diagrams (those that already have `<style>` blocks). This IS the spec — read directly from source.

**Canonical block (verbatim from `docs/assets/diagrams/elastic-alignment.svg:2-8` and confirmed identical in `docs/assets/diagrams/conformal-prediction.svg:2-8`):** [VERIFIED: docs/assets/diagrams/elastic-alignment.svg:2-8]

```xml
<style>
  .ttl{font:700 17px system-ui,-apple-system,sans-serif;fill:#1a1a2e}
  .sub{font:400 12px system-ui,sans-serif;fill:#6c757d}
  .lab{font:700 13px system-ui,sans-serif}
  .sm{font:400 11px system-ui,sans-serif;fill:#495057}
  .mono{font:600 12px ui-monospace,monospace}
</style>
```

**Class semantics:**
- `.ttl` — diagram title (700 weight, 17px, dark `#1a1a2e`; centered at y≈26)
- `.sub` — subtitle/caption (400 weight, 12px, muted `#6c757d`; centered at y≈46)
- `.lab` — panel/section label (700 weight, 13px; no default fill — color set per element)
- `.sm` — small annotation text (400 weight, 11px, `#495057`)
- `.mono` — monospace code labels (600 weight, 12px, ui-monospace; e.g., function names)

**ViewBox conventions** [VERIFIED: bash grep tally on docs/assets/diagrams/*.svg]:
- Standard: `viewBox="0 0 720 300"` — 34 of 43 diagrams
- Tall (two-row layouts): `viewBox="0 0 720 480"` — 4 diagrams
- Extra-tall: `viewBox="0 0 720 520"` — 1 diagram
- Non-conforming (legacy): 700×400, 700×250, 600×425, 600×350 — 4 diagrams (will be migrated in later phases)
- **Fixed width: always 720.** Height is one of {300, 480, 520} for new/conforming diagrams.

**Palette** [VERIFIED: docs/assets/diagrams/elastic-alignment.svg; cross-referenced with scripts/docs_fig.py:29-37]:
```
#1a1a2e  — near-black (title text only)
#6c757d  — muted grey (subtitle text, secondary annotations)
#495057  — mid-grey (.sm text, structural lines)
#ced4da  — light grey (panel borders, axis lines: stroke-width 1.2–1.5)
#f8f9fa  — near-white (panel fill / background)
#fd7e14  — orange accent (method/process panels: stroke #fd7e14, fill #fff4ea)
#f8d7b8  — pale orange (inner element borders within orange panels)
```
Plus brand colors from `docs_fig.py` FDARS_COLORS for data curves:
`#3f51b5` (indigo), `#e8710a` (orange), `#198754` (green), `#dc3545` (red), `#6f42c1` (purple), `#0dcaf0` (cyan), `#6c757d` (grey).

**Stroke weights** (from 3-file sample of conforming diagrams):
- Panel borders: `stroke-width="1.5"` (outer rect edges)
- Axis/reference lines: `stroke-width="1.2"`
- Data curves (primary): `stroke-width="2"` to `stroke-width="2.8"`
- Data curves (secondary/faded): `stroke-width="1.4"` to `stroke-width="1.6"`
- Arrows: `stroke-width="2"`

**Accessibility pattern** (conforming diagrams):
```xml
<svg ... role="img" aria-label="[descriptive text matching diagram title]">
```
9 of 43 diagrams are missing `role="img"` — these are legacy diagrams to fix in later phases.

---

## Pattern 3: docs_fig.py Additions (FND-03 + FND-06)

**Current state** [VERIFIED: scripts/docs_fig.py:1-86]: `docs_fig.py` has `fig()` and `render()` helpers, brand palette, and matplotlib rcParams — but **no `svg.hashsalt` setting and no DOCS_FAST logic**.

**FND-03 addition — deterministic SVG:**
```python
# Add to plt.rcParams.update({...}) in docs_fig.py — after the existing rcParams dict
# svg.hashsalt: set any fixed string → element IDs become deterministic across builds.
# Without this, matplotlib uses uuid4() → SVG IDs differ every run → byte-for-byte
# comparison of two builds always fails.
plt.rcParams.update({
    # ... existing keys ...
    "svg.hashsalt": "fdars-docs",
})
```

**FND-06 addition — DOCS_FAST helper:**
```python
import os as _os

def fast(full, fast_value):
    """Return fast_value if DOCS_FAST is set, else full.

    Usage in exec blocks:
        res = fanova(X, grp, n_perm=fast(500, 50))
        out = karcher_mean(data, t, max_iter=fast(20, 5))
        band = fpca_tolerance_band(ref, nb=fast(800, 100))
    """
    return fast_value if _os.environ.get("DOCS_FAST") else full
```

**Confirmed expensive parameters to accelerate** [VERIFIED: grep on docs/examples/*.md]:
- `n_perm` (fanova): 500 or 999 → fast: 50
- `max_iter` (karcher_mean, tsrvf_transform, alignment_quality): 15–20 → fast: 5
- `nb` (fpca_tolerance_band): 800 → fast: 100
- `oversampling` (lomb_scargle_fdata): 4 → fast: 2

---

## Pattern 4: pymdownx.snippets Wiring (FND-04)

**mkdocs.yml change** — add `pymdownx.snippets` to `markdown_extensions:` with `base_path: ["docs"]`:

```yaml
markdown_extensions:
  # ... existing extensions ...
  - pymdownx.snippets:
      base_path:
        - docs
```

With `base_path: ["docs"]`, include paths resolve relative to the `docs/` directory, so `--8<-- "includes/load-canadian-weather.md"` finds `docs/includes/load-canadian-weather.md`.

**Include file structure** — each `docs/includes/` snippet is a plain Python block (no exec attributes — those belong on the consuming fence):
```markdown
<!-- docs/includes/load-canadian-weather.md -->
```python
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("temperature")
```
```

**Usage in an example page fence:**
```markdown
```python exec="1" html="1" source="above"
--8<-- "includes/load-canadian-weather.md"
# ... page-specific code using day, X, meta ...
print(render(f))
```
```

**Scope:** 114 `from docs_data import` occurrences across 17 example pages. The four loaders (`load_canadian_weather`, `load_tecator`, `load_growth`, `load_phoneme`) map to 4 include files. A 5th include for `load_canadian_weather("precipitation")` may be warranted if used in 3+ fences.

**Important caveat:** `pymdownx.snippets` runs at the Markdown pre-processing stage, before `markdown-exec`. The include content is textually substituted into the fence. This is safe for `exec="1"` fences — the combined (preamble + page-specific) code is what gets executed.

---

## Pattern 5: pytest-markdown-docs Harness (FND-05)

**Execution model** [CITED: pypi.org/project/pytest-markdown-docs + github.com/modal-labs/pytest-markdown-docs]:
- By default, each code fence runs in its **own isolated namespace**. Variables defined in fence 1 are NOT visible in fence 2.
- `continuation` info string enables cross-fence state: ` ```python continuation ` — the continuation fence shares the namespace of the immediately preceding fence.
- `pytest_markdown_docs_globals()` hook in `conftest.py` injects globals available in ALL fences on ALL pages.

**Critical finding — current example pages are already self-contained:**
Every fence in `canadian-weather.md` and `canadian-seasonal.md` re-imports `load_canadian_weather`, re-declares `rng`, and rebuilds all variables from scratch [VERIFIED: grep scan of docs/examples/canadian-weather.md and docs/examples/canadian-seasonal.md]. There is NO genuine cross-fence state dependency in the current pages.

**Implication for D-04 smoke-test:** The smoke-test will almost certainly pass without needing the `continuation` feature. The D-04 concern was a precaution; the actual code already follows the per-fence self-contained pattern.

**Smoke-test page recommendation:** `docs/examples/canadian-weather.md` — 8 fences, imports `fdars.regression.fanova` and `fdars.regression.fosr`, actually calls compute-heavy functions. This is the most meaningful "does the harness work with real fdars imports?" test.

**`conftest.py` (repo root):**
```python
# conftest.py
"""pytest-markdown-docs globals for fdars documentation fences.

Injects np, plt, and fdars so individual fences don't need to import them.
The exec blocks still perform their own imports explicitly (self-documenting),
but the globals are available as a fallback and for any fences that rely on them.
"""
import matplotlib
matplotlib.use("Agg")  # non-interactive backend required for CI

import matplotlib.pyplot as plt
import numpy as np
import fdars


def pytest_markdown_docs_globals():
    """Return globals injected into every markdown code fence during testing."""
    return {"np": np, "plt": plt, "fdars": fdars}
```

**pytest invocation:**
```bash
# Smoke-test only (D-11: CI gates on one page now)
PYTHONPATH=scripts pytest --markdown-docs docs/examples/canadian-weather.md -v

# Full example sweep (Phase 9, not Phase 1)
PYTHONPATH=scripts pytest --markdown-docs docs/examples/ -v
```

**Why `PYTHONPATH=scripts`:** `conftest.py` globals don't include `docs_fig` or `docs_data`. The exec blocks import these explicitly, and they resolve via `PYTHONPATH=scripts` (same as mkdocs build). [VERIFIED: scripts/docs_fig.py:1, docs/hooks.py:10-13]

**`--markdown-docs-syntax=superfences` flag:** The MkDocs Material theme uses PyMdown's superfences, which uses ` ```python exec="1" ` info strings. pytest-markdown-docs supports this via `--markdown-docs-syntax=superfences`. Without this flag, the fences with `exec="1"` attributes may be skipped (treated as non-Python fences). This flag is required.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SVG linting/optimization | Custom Python SVG parser | `npx svgo@3.3.4` | svgo handles all SVG edge cases, has a plugin ecosystem, is battle-tested at 36M/wk |
| Markdown code fence execution as tests | Custom exec harness | `pytest-markdown-docs` | Already handles namespace isolation, pytest integration, CI reporting |
| SVG determinism | Custom ID renaming | `plt.rcParams["svg.hashsalt"]` | matplotlib built-in; handles all internal ID types including clipPath IDs |
| Snippet includes | Custom template system | `pymdownx.snippets` | Already in the installed MkDocs Material stack; zero new dependency |

**Key insight:** All four problems have existing solutions in the current stack. The phase installs/configures them; it does not build anything custom.

---

## Runtime State Inventory

Step 2.5 SKIPPED — Phase 1 is greenfield tooling additions, not a rename/refactor/migration. No stored data, live service config, OS-registered state, secrets, or build artifacts are being renamed or migrated.

---

## Common Pitfalls

### Pitfall 1: svgo default plugins strip CSS classes

**What goes wrong:** Running `npx svgo` without the config (or with a config that doesn't disable `inlineStyles`) converts `.ttl`/`.sub`/`.lab`/`.sm`/`.mono` class-based styling into inline `style=` attributes. The CSS `<style>` block is then empty or partially emptied by `minifyStyles`. The diff gate would catch this, but if someone runs svgo manually without the config they'll corrupt diagrams.

**Why it happens:** `inlineStyles` is on by default in `preset-default`; it considers CSS class rules that only match one element as candidates for inlining. In the 35 conforming diagrams, `.ttl` and `.sub` each appear once per diagram — they get inlined.

**How to avoid:** Always invoke with `--config svgo.config.mjs`. Document this clearly in STYLE_SPEC.md. The CI gate uses `--config` explicitly.

**Warning signs:** `<style>` block in the output file is shorter than the original, or elements show `style="font:700 17px..."` instead of `class="ttl"`.

**Live evidence:** Confirmed during this research session by running `npx svgo@3.3.4` on `elastic-alignment.svg` — `.ttl` and `.sub` were inlined; `role="img"` was stripped by `removeUnknownsAndDefaults`.

### Pitfall 2: removeUnknownsAndDefaults strips role and aria-label

**What goes wrong:** `removeUnknownsAndDefaults` removes SVG attributes not in the SVG specification's known attribute set. `role` is an ARIA attribute (not native SVG), and some versions of svgo treat it as unknown. `aria-label` may be similarly affected.

**Why it happens:** svgo's SVG spec model doesn't always include ARIA attributes in its known-attributes list.

**How to avoid:** Disable `removeUnknownsAndDefaults` in the config (done in the config above). The conforming diagrams already use both `role="img"` and `aria-label`.

### Pitfall 3: svg.hashsalt does not eliminate ALL matplotlib nondeterminism

**What goes wrong:** Even with `svg.hashsalt` set, stochastic figures (using `np.random`, `rng = np.random.default_rng()`) still produce different output on each build because the random numbers differ.

**Why it happens:** `svg.hashsalt` only fixes SVG element IDs (clip paths, etc.). It does not seed Python random number generators.

**How to avoid:** Each exec block that uses randomness must set its own seed before the random call. Convention: `rng = np.random.default_rng(42)` at the top of the block. This is already done in `canadian-seasonal.md:30` [VERIFIED: docs/examples/canadian-seasonal.md:30].

**Note:** FND-03 says "stochastic example blocks seed their RNG." Phase 1 only establishes the convention in `STYLE_SPEC.md` (or equivalent doc) and sets `svg.hashsalt`. The actual seed-auditing of all exec blocks is a Phase 3–8 concern as each section is swept.

### Pitfall 4: pymdownx.snippets + markdown-exec ordering

**What goes wrong:** A snippet that contains ` ```python ` fences within an include file triggers its own markdown processing. If the snippet itself has an `exec="1"` attribute, the code runs at include-time, not at the outer fence's execution time.

**Why it happens:** The snippets extension substitutes content literally before the Markdown parser sees it. If the included content contains a full fence with `exec="1"`, the outer fence's exec context may not apply correctly.

**How to avoid:** The `docs/includes/` snippets should contain only raw Python code lines (no fence delimiters, no `exec` attributes). The consuming fence provides the ` ```python exec="1" html="1" ` delimiters and the `--8<-- "includes/..."` is just one of the lines inside that fence.

### Pitfall 5: pytest --markdown-docs misses fences with info string attributes

**What goes wrong:** Fences like ` ```python exec="1" html="1" source="above" ` are not recognized as Python fences by pytest-markdown-docs in default mode, because the info string is `python exec="1" html="1" source="above"`, not just `python`.

**Why it happens:** The default `--markdown-docs-syntax` mode expects bare ` ```python ` info strings.

**How to avoid:** Always pass `--markdown-docs-syntax=superfences` flag. This tells pytest-markdown-docs to use PyMdown's superfences parsing, which correctly strips the extra attributes and identifies the language from the first token.

### Pitfall 6: svgo@4 vs svgo@3 API differences

**What goes wrong:** Pinning to `svgo@3.3.4` (stable v3 dist-tag) is correct for this phase. If someone uses `npx svgo` without a version pin, they get svgo 4.0.2 (latest dist-tag), which has a different CLI and config API.

**How to avoid:** Always pin: `npx svgo@3.3.4`. Document the pin in STYLE_SPEC.md and in the CI workflow comment.

---

## CI Extension (FND-02 + FND-05, D-09–D-11)

**Existing workflow:** `.github/workflows/docs.yml` [VERIFIED: .github/workflows/docs.yml:1-56]

Current steps:
1. checkout + python + rust toolchain + rust-cache
2. `pip install -r docs/requirements.txt maturin`
3. `maturin develop --release`
4. `mkdocs build --strict` + `python scripts/check_docs_figures.py site`
5. deploy via `ghp-import`

**Two gates to add:**

**Gate A — SVGO lint (before mkdocs build):**
```yaml
- name: Lint SVG diagrams (SVGO)
  run: |
    FAILED=0
    for svg in docs/assets/diagrams/*.svg; do
      diff <(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -) "$svg" \
        || { echo "SVGO: $svg would be modified"; FAILED=1; }
    done
    [ $FAILED -eq 0 ] || { echo "SVGO lint failed"; exit 1; }
```

**Gate B — Doc-test smoke (after maturin develop, before or after mkdocs build):**
```yaml
- name: Doc-test smoke (canadian-weather.md)
  env:
    PYTHONPATH: scripts
  run: |
    source .venv/bin/activate
    pytest --markdown-docs --markdown-docs-syntax=superfences \
      docs/examples/canadian-weather.md -v
```

**Placement:** Gate A runs before `mkdocs build`. Gate B runs after `maturin develop` (needs compiled fdars). Both must pass before the deploy step.

**D-11 implementation:** Gate B is hardcoded to one page now. When Phase 9 fixes each example page, the gate is expanded by adding pages to the pytest invocation (or a file list). CI stays green through Phases 2–8 because only the one verified page is gated.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already used in `tests/`) |
| Config file | none yet (no pytest.ini or pyproject.toml `[tool.pytest]` section) |
| Quick run command | `PYTHONPATH=scripts pytest --markdown-docs --markdown-docs-syntax=superfences docs/examples/canadian-weather.md -v` |
| Full suite command | `PYTHONPATH=scripts pytest --markdown-docs --markdown-docs-syntax=superfences docs/examples/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FND-01 | STYLE_SPEC.md exists at correct path | smoke | `test -f docs/assets/diagrams/STYLE_SPEC.md` | ❌ Wave 0 |
| FND-02 | svgo diff gate produces zero diff on all diagrams | automated shell | See CI Gate A above | ❌ Wave 0 |
| FND-03 | Two consecutive builds produce byte-identical SVG | automated shell | `mkdocs build && cp -r site site1 && mkdocs build && diff -r site1 site` (select *.svg files) | ❌ Wave 0 |
| FND-04 | `pymdownx.snippets` in mkdocs.yml; `docs/includes/` files exist; `--8<--` syntax in at least one example fence | build smoke | `mkdocs build --strict` + manual check | ❌ Wave 0 |
| FND-05 | pytest --markdown-docs passes on smoke-test page | automated pytest | `PYTHONPATH=scripts pytest --markdown-docs --markdown-docs-syntax=superfences docs/examples/canadian-weather.md -v` | ❌ Wave 0 |
| FND-06 | DOCS_FAST=1 build completes in materially less time than full build | timing smoke | `time DOCS_FAST=1 mkdocs build` vs `time mkdocs build` | ❌ Wave 0 |

### Wave 0 Gaps

- [ ] `conftest.py` (repo root) — covers FND-05 globals hook
- [ ] `docs/assets/diagrams/STYLE_SPEC.md` — covers FND-01
- [ ] `svgo.config.mjs` (repo root) — covers FND-02
- [ ] `docs/includes/` directory + snippet files — covers FND-04
- [ ] No gaps in framework — pytest already installed; no new test files needed beyond conftest.py

---

## Security Domain

`security_enforcement: true` (from .planning/config.json), `security_asvs_level: 1`.

This phase has no networked service, no user input handling, no authentication, and no cryptography. The tooling additions (svgo, pytest-markdown-docs, pymdownx.snippets) are all build-time/dev-time tools.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | n/a (docs build tooling) |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | minimal | SVG files are hand-authored; no user input path |
| V6 Cryptography | no | n/a |

### Known Threat Patterns for this Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious postinstall in npx package | Tampering | Pin exact version (`svgo@3.3.4`); confirmed `postinstall: null` [VERIFIED: npm registry via legitimacy seam] |
| svgo config escape (path traversal in --input) | Tampering | Input paths are hardcoded glob patterns in CI (not user-supplied); not a practical threat |
| Markdown exec code injection via snippets | Tampering | `docs/includes/` is committed to git; no runtime user content; only authors edit includes |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js / npx | FND-02 SVGO gate | ✓ [VERIFIED: bash] | v24.13.1 (npx 11.8.0) | None — npx required for zero-install svgo |
| Python 3.12 | FND-05 pytest | ✓ (CI: python 3.12) [VERIFIED: docs.yml] | 3.12 in CI | — |
| matplotlib (svg.hashsalt) | FND-03 | ✓ [VERIFIED: .venv] | 3.10.8 | — |
| pymdown-extensions | FND-04 snippets | ✓ (bundled with mkdocs-material) [VERIFIED: mkdocs.yml use of other pymdownx.* extensions] | — | — |
| pytest-markdown-docs | FND-05 | Not yet installed [VERIFIED: pip show] | 0.9.2 latest on PyPI | If smoke-test fails: custom conftest harness (Claude's discretion) |

**Missing dependencies with no fallback:** None (npx is already available in CI and locally).

**Missing dependencies with fallback:** `pytest-markdown-docs` (add to docs/requirements.txt; fallback to custom harness per D-04 if smoke-test reveals fundamental incompatibility).

---

## SVG Baseline Summary (for STYLE_SPEC.md)

**Conforming diagrams (35 of 43):** Have `<style>` block with canonical five classes, `role="img"`, `aria-label`, `viewBox="0 0 720 {300|480|520}"`, `fill="none"` on root `<svg>`.

**Legacy/nonconforming diagrams (8 of 43):** Use inline `font-size` attributes, missing `<style>` block, missing `role="img"`, and some have non-720 viewBox widths. These are flagged but NOT migrated in Phase 1 — they are targets for later diagram sweep phases (DIA-01 through DIA-06).

The 4 non-conforming-viewBox diagrams: [VERIFIED: bash grep on docs/assets/diagrams/*.svg]
- `elastic-clustering.svg` — `viewBox="0 0 700 250"`
- `outlier-detection.svg` — `viewBox="0 0 600 350"`
- `covariance-functions.svg` — `viewBox="0 0 600 425"`
- `ex-sonar-tsrvf.svg` — `viewBox="0 0 700 400"`

STYLE_SPEC.md formalizes the 35-diagram baseline as the standard. The nonconforming 8 are documented as migration targets.

---

## Open Questions

1. **Does svgo diff gate produce zero diff on ALL 43 current diagrams under the proposed config?**
   - What we know: The 35 conforming diagrams have `<style>` blocks and the right structure; with `inlineStyles`/`minifyStyles`/`cleanupIds`/`removeDesc`/`removeUnknownsAndDefaults`/`removeViewBox` disabled, svgo should not touch CSS classes, IDs, or accessibility attrs.
   - What's unclear: The 8 legacy diagrams (using inline `font-size`, different viewBox) — whether svgo would attempt to modify any other attribute under the remaining default plugins (e.g., `convertPathData`, `sortAttrs`). `sortAttrs` reorders attributes but does not change values; `convertPathData` optimizes path coordinates (changes values but not structure).
   - Recommendation: The first task in the plan should run the diff gate against all 43 diagrams with the proposed config. If any legacy diagram fails, add additional plugin disables or restrict the gate to the conforming 35 until Phase 3–8 migrate them.

2. **Does `--markdown-docs-syntax=superfences` correctly handle `exec="1" html="1" source="above"` fences?**
   - What we know: The flag exists and is designed for PyMdown superfences compatibility [CITED: pypi.org/project/pytest-markdown-docs].
   - What's unclear: Whether `html="1"` output (the rendered SVG `<div>`) causes a test failure when pytest evaluates the fence (the print(render(f)) call produces HTML output, not a Python value). pytest-markdown-docs typically treats print output as acceptable; a fence fails only if it raises an exception.
   - Recommendation: The smoke-test (D-04/D-05) will settle this. The exec blocks call `print(render(f))` which prints an SVG string — this should not raise. But figure rendering requires `matplotlib.use("Agg")`, which the `conftest.py` sets before importing plt.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `--markdown-docs-syntax=superfences` correctly parses `exec="1" html="1" source="above"` info strings | Pattern 5 | If wrong: fences are silently skipped (not tested). Mitigation: smoke-test verifies at least one fence runs. |
| A2 | The 8 legacy diagrams (non-conforming viewBox, inline fonts) pass the svgo diff gate under the proposed config | Pattern 1 / Open Questions | If wrong: gate fails on legacy diagrams; add those SVGs to an exclusion list or add additional plugin disables. |
| A3 | `pymdownx.snippets` include substitution happens before `markdown-exec` fence execution, making the combined content available to exec | Pattern 4 | If wrong: exec block sees only the `--8<-- "..."` literal text, not the expanded content. Low risk: this is the documented behavior of snippets + exec ordering. |
| A4 | Setting `svg.hashsalt` is sufficient for byte-identical SVG output from `render()` in `docs_fig.py` (assuming all exec blocks also seed their RNG) | Pattern 3 | If wrong: other sources of nondeterminism exist (e.g., font metric differences by OS). Mitigation: FND-03 verification runs two consecutive builds and diffs. |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed. (Table is not empty — A1–A4 require verification via execution.)

---

## Sources

### Primary (HIGH confidence)

- [VERIFIED: docs/assets/diagrams/elastic-alignment.svg:1-8] — canonical `<style>` block and SVG root attributes; read this session
- [VERIFIED: docs/assets/diagrams/conformal-prediction.svg:1-8] — confirmed identical `<style>` block; read this session
- [VERIFIED: scripts/docs_fig.py:1-86] — complete file read; no hashsalt, no DOCS_FAST; read this session
- [VERIFIED: mkdocs.yml:1-170] — complete file read; no `pymdownx.snippets`; read this session
- [VERIFIED: docs/hooks.py:1-14] — complete file read; PYTHONPATH=scripts pattern confirmed; read this session
- [VERIFIED: .github/workflows/docs.yml:1-56] — complete file read; existing CI steps confirmed; read this session
- [VERIFIED: bash grep on docs/assets/diagrams/*.svg] — viewBox tally (34×720×300, 4×720×480, 1×720×520, 4 non-conforming); style block count (35 with, 8 without); role="img" count (34 with, 9 without)
- [VERIFIED: npm registry] — `svgo@3.3.4` exists, 36M weekly downloads, source repo confirmed, no postinstall script
- [VERIFIED: pip index versions] — `pytest-markdown-docs 0.9.2` exists on PyPI
- [VERIFIED: bash] — `npx svgo@3.3.4` executable (v24.13.1 node, 11.8.0 npx); live test run on elastic-alignment.svg

### Secondary (MEDIUM confidence)

- [CITED: pypi.org/project/pytest-markdown-docs] — execution model (per-fence isolation by default; `continuation` feature; globals hook signature)
- [CITED: github.com/modal-labs/pytest-markdown-docs] — confirmed `--markdown-docs-syntax=superfences` flag; globals hook takes no params, returns dict

### Tertiary (LOW confidence)

- [WebSearch] — svgo preset-default plugin list (inlineStyles, minifyStyles, cleanupIds, removeDesc, removeUnknownsAndDefaults, removeViewBox confirmed as relevant); pattern for `overrides` in svgo.config.mjs
- [WebSearch] — `svg.hashsalt` rcParam behavior: setting to non-None string makes element IDs deterministic; `None` default uses uuid4

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified on registries this session; live tool invocation confirmed
- Architecture: HIGH — all architectural claims grounded in files read this session
- Pitfalls: HIGH — Pitfall 1 and 2 confirmed by live svgo run on actual diagram; Pitfalls 3–6 cited from tool documentation
- CSS class spec: HIGH — verbatim from source files read this session
- Snippet/snippets config: MEDIUM — documented pattern from pymdownx; actual mkdocs.yml edit unverified until executed

**Research date:** 2026-08-07
**Valid until:** 2026-09-07 (stable tooling — svgo v3, pytest-markdown-docs, pymdownx.snippets are all stable APIs)
