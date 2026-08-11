# Phase 1: Foundation - Pattern Map

**Mapped:** 2026-08-07
**Files analyzed:** 8 (3 net-new, 4 modified, 1 net-new directory tree)
**Analogs found:** 7 / 8

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/assets/diagrams/STYLE_SPEC.md` | spec/doc | — | `docs/assets/diagrams/elastic-alignment.svg` (baseline source) | exact (spec documents this file's structure) |
| `svgo.config.mjs` | config | — | none (no JS config files in repo) | no-analog |
| `scripts/docs_fig.py` (edit) | utility | transform | `scripts/docs_fig.py` itself | self (two additions to existing file) |
| `docs/includes/load-*.md` | snippet/fragment | — | `docs/examples/canadian-weather.md` (preamble pattern) | partial (source of deduplication target) |
| `mkdocs.yml` (edit) | config | — | `mkdocs.yml` itself | self (one block addition) |
| `conftest.py` | test-config | — | `tests/test_basic.py` (test structure) | partial (same pytest ecosystem) |
| `.github/workflows/docs.yml` (edit) | CI workflow | — | `.github/workflows/docs.yml` itself | self (two step additions to existing job) |

---

## Pattern Assignments

### `docs/assets/diagrams/STYLE_SPEC.md` (spec document)

**Analog:** `docs/assets/diagrams/elastic-alignment.svg` (lines 1–8) — the canonical conforming SVG that the spec formalizes.

**SVG root + accessibility pattern** (line 1):
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none" role="img" aria-label="[descriptive text matching diagram title]">
```

**Canonical `<style>` block to copy verbatim** (lines 2–8):
```xml
<style>
  .ttl{font:700 17px system-ui,-apple-system,sans-serif;fill:#1a1a2e}
  .sub{font:400 12px system-ui,sans-serif;fill:#6c757d}
  .lab{font:700 13px system-ui,sans-serif}
  .sm{font:400 11px system-ui,sans-serif;fill:#495057}
  .mono{font:600 12px ui-monospace,monospace}
</style>
```

**Panel fill/border pattern** (lines 13, 29 of elastic-alignment.svg):
```xml
<!-- Neutral panel -->
<rect x="24" y="70" width="196" height="188" rx="12" fill="#f8f9fa" stroke="#ced4da" stroke-width="1.5"/>
<!-- Method/process panel (orange accent) -->
<rect x="272" y="70" width="176" height="188" rx="12" fill="#fff4ea" stroke="#fd7e14" stroke-width="1.5"/>
```

**Palette (from `scripts/docs_fig.py` lines 29–37 and SVG baseline):**
```
#1a1a2e  — near-black (title text only)
#6c757d  — muted grey (subtitle text)
#495057  — mid-grey (.sm text, structural lines)
#ced4da  — light grey (panel borders, axis lines; stroke-width 1.2–1.5)
#f8f9fa  — near-white (panel fill)
#fd7e14  — orange accent (method panels: stroke #fd7e14, fill #fff4ea)
#f8d7b8  — pale orange (inner element borders within orange panels)
Data curve colors (from FDARS_COLORS): #3f51b5 #e8710a #198754 #dc3545 #6f42c1 #0dcaf0 #6c757d
```

**viewBox conventions (from grep tally across 43 diagrams):**
- Standard: `viewBox="0 0 720 300"` — 34 diagrams
- Tall: `viewBox="0 0 720 480"` — 4 diagrams
- Extra-tall: `viewBox="0 0 720 520"` — 1 diagram
- Non-conforming legacy (migration targets, NOT the spec): 700×250, 700×400, 600×350, 600×425 — 4 diagrams

**Stroke weights:**
- Panel border outer: `stroke-width="1.5"`
- Axis/reference lines: `stroke-width="1.2"`
- Data curves primary: `stroke-width="2"` to `stroke-width="2.8"`
- Data curves secondary/faded: `stroke-width="1.4"` to `stroke-width="1.6"`
- Arrows: `stroke-width="2"`

---

### `svgo.config.mjs` (config, no analog — use RESEARCH.md pattern)

**No analog:** No JavaScript config files exist in the repo.

**Copy from RESEARCH.md Pattern 1 exactly:**
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
          // Preserve <desc> elements (accessibility)
          removeDesc: false,
          // Preserve role="img" and aria-label (accessibility attributes)
          removeUnknownsAndDefaults: false,
          // Preserve viewBox
          removeViewBox: false,
        },
      },
    },
  ],
};
```

---

### `scripts/docs_fig.py` — additions only (utility, transform)

**Analog:** `scripts/docs_fig.py` itself — two additions to the existing file.

**Current rcParams block to extend** (lines 39–58 — ADD `"svg.hashsalt"` key):
```python
plt.rcParams.update(
    {
        "figure.figsize": (7.5, 4.0),
        "figure.dpi": 110,
        "savefig.transparent": True,
        "axes.prop_cycle": plt.cycler(color=FDARS_COLORS),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.7,
        "font.size": 11,
        "axes.titlesize": 12.5,
        "axes.titleweight": "600",
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "figure.autolayout": True,
        # FND-03: deterministic SVG element IDs across builds.
        # Without this, matplotlib uses uuid4() → IDs differ every run.
        "svg.hashsalt": "fdars-docs",
    }
)
```

**New `fast()` helper to add after the `render()` function** (after line 85):
```python
import os as _os


def fast(full, fast_value):
    """Return fast_value if DOCS_FAST is set, else full.

    Usage in exec blocks::

        res = fanova(X, grp, n_perm=fast(500, 50))
        out = karcher_mean(data, t, max_iter=fast(20, 5))
        band = fpca_tolerance_band(ref, nb=fast(800, 100))
    """
    return fast_value if _os.environ.get("DOCS_FAST") else full
```

**Module docstring style** (lines 1–18): preserve the existing `"""..."""` module docstring; add `fast` to the Usage example list in the docstring.

**Import style** (lines 19–26): `from __future__ import annotations` first, then stdlib imports, then third-party. The new `import os as _os` follows the same leading-underscore-alias pattern to keep it out of `help(docs_fig)` output.

---

### `docs/includes/load-*.md` (snippet fragments)

**Analog:** `docs/examples/canadian-weather.md` — the preamble repeated in every fence is the extraction target.

**Target preamble pattern to extract** (repeated in example fences across 17 pages):
```python
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("temperature")
```

**Include file format:** Plain Python lines only — no fence delimiters, no `exec` attributes. The consuming fence provides those:
```markdown
```python exec="1" html="1" source="above"
--8<-- "includes/load-canadian-weather.md"
# page-specific code here...
print(render(f))
```
```

**Four include files to create** (one per dataset loader):
- `docs/includes/load-canadian-weather.md` — `load_canadian_weather("temperature")`
- `docs/includes/load-canadian-weather-precip.md` — `load_canadian_weather("precipitation")`
- `docs/includes/load-tecator.md` — `load_tecator()`
- `docs/includes/load-growth.md` — `load_growth()`
- `docs/includes/load-phoneme.md` — `load_phoneme()`

---

### `mkdocs.yml` — one block addition (config)

**Analog:** `mkdocs.yml` itself — the existing `markdown_extensions:` block (lines 49–67).

**Existing block to extend** (lines 49–67, add `pymdownx.snippets` entry):
```yaml
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.arithmatex:
      generic: true
  - admonition
  - pymdownx.details
  - attr_list
  - md_in_html
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - tables
  - toc:
      permalink: true
  # FND-04: shared dataset-loading preambles in docs/includes/
  - pymdownx.snippets:
      base_path:
        - docs
```

**Insertion point:** After the `toc:` block, before the closing of `markdown_extensions`. The `base_path: ["docs"]` makes `--8<-- "includes/load-canadian-weather.md"` resolve to `docs/includes/load-canadian-weather.md`.

---

### `conftest.py` (test-config, repo root)

**Analog:** `tests/test_basic.py` (lines 1–11) — establishes the pytest import conventions and structure used in the project.

**Existing test import pattern** (lines 1–10 of `tests/test_basic.py`):
```python
"""Basic tests for fdars package."""

import numpy as np
import pytest
```

**New conftest.py** — copy structure, extend for globals hook:
```python
# conftest.py
"""pytest-markdown-docs globals for fdars documentation fences.

Injects np, plt, and fdars so individual fences don't need to import them.
The exec blocks still perform their own imports explicitly (self-documenting),
but the globals are available as a fallback.
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

**Key constraint:** `matplotlib.use("Agg")` must appear before `import matplotlib.pyplot as plt` — same pattern already used in `scripts/docs_fig.py` lines 23–26.

---

### `.github/workflows/docs.yml` — two step additions (CI workflow)

**Analog:** `.github/workflows/docs.yml` itself — the existing job step structure (lines 17–55).

**Existing step pattern to copy** (lines 36–49 — note `source .venv/bin/activate` required before every command):
```yaml
      - name: Install docs dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r docs/requirements.txt maturin
      - name: Build and install fdars (needed for build-time figures)
        run: |
          source .venv/bin/activate
          maturin develop --release
      - name: Build and gate on figure errors
        env:
          PYTHONPATH: scripts
        run: |
          source .venv/bin/activate
          mkdocs build --strict
          python scripts/check_docs_figures.py site
```

**Gate A — SVGO lint (insert BEFORE the "Build and gate on figure errors" step):**
```yaml
      - name: Lint SVG diagrams (SVGO)
        # FND-02: check-only gate. Pinned to svgo@3.3.4 (not latest — v4 has different API).
        # diff exit code nonzero = svgo would rewrite the diagram = structural nonconformance.
        run: |
          FAILED=0
          for svg in docs/assets/diagrams/*.svg; do
            diff <(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -) "$svg" \
              || { echo "SVGO: $svg would be modified"; FAILED=1; }
          done
          [ $FAILED -eq 0 ] || { echo "SVGO lint failed — fix diagrams above"; exit 1; }
```

**Gate B — Doc-test smoke (insert AFTER "Build and install fdars", BEFORE "Build and gate on figure errors"):**
```yaml
      - name: Doc-test smoke (canadian-weather.md)
        # FND-05/D-11: CI gates on one page now; expands page-by-page in Phase 9.
        env:
          PYTHONPATH: scripts
        run: |
          source .venv/bin/activate
          pytest --markdown-docs --markdown-docs-syntax=superfences \
            docs/examples/canadian-weather.md -v
```

**Step ordering in final job:**
1. checkout + python + rust toolchain + rust-cache
2. Install docs dependencies (pip install)
3. Build and install fdars (maturin develop)
4. **[NEW] Gate A — Lint SVG diagrams (SVGO)**
5. **[NEW] Gate B — Doc-test smoke (canadian-weather.md)**
6. Build and gate on figure errors (mkdocs build --strict)
7. Deploy (ghp-import)

---

## Shared Patterns

### venv activation
**Source:** `.github/workflows/docs.yml` lines 34–38, 39–41
**Apply to:** All new CI steps
```yaml
run: |
  source .venv/bin/activate
  <command>
```
Every command that uses Python (pip, maturin, mkdocs, pytest) must activate the venv first. This is the project's established CI pattern — there is no `actions/setup-python` `cache: pip` shortcut in use.

### `matplotlib.use("Agg")` before pyplot import
**Source:** `scripts/docs_fig.py` lines 23–26
**Apply to:** `conftest.py`
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
```
Must appear before the pyplot import or matplotlib will default to an interactive backend that fails in CI.

### Module docstring + `from __future__ import annotations`
**Source:** `scripts/docs_fig.py` lines 1–19
**Apply to:** `conftest.py` (docstring only; conftest doesn't need `from __future__ import annotations`)
```python
"""One-line purpose. Longer explanation if needed."""
from __future__ import annotations
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `svgo.config.mjs` | config | — | No JavaScript or Node.js config files exist in this Rust/Python repo. Use RESEARCH.md Pattern 1 verbatim. |

---

## Metadata

**Analog search scope:** `scripts/`, `.github/workflows/`, `tests/`, `docs/assets/diagrams/`, `mkdocs.yml`, `docs/examples/`
**Files read:** 7 (docs_fig.py, docs.yml, mkdocs.yml, elastic-alignment.svg, test_basic.py, 01-CONTEXT.md, 01-RESEARCH.md)
**Pattern extraction date:** 2026-08-07
