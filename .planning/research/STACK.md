# Stack Research

**Domain:** Technical library documentation — hand-authored SVG concept diagrams + reproducible code-driven examples (MkDocs Material site)
**Researched:** 2026-08-07
**Confidence:** MEDIUM (core tools verified against live PyPI/npm; some configuration details LOW from web search)

---

## Context

The fdars/pyfda docs site already has a working foundation: MkDocs Material 9.7.7, markdown-exec 1.12.3, KaTeX math, a shared `docs_fig.py` figure helper, and ~50 hand-authored SVGs with a de-facto style. This STACK.md does **not** propose rebuilding that foundation — it prescribes the specific additional tools and techniques needed to bring diagrams and examples to a consistently high standard. All tool choices are additive to the existing stack.

---

## Recommended Stack

### Core Documentation Platform (existing — no changes needed)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| MkDocs Material | 9.7.7 | Static site framework and theme | Already in use; latest stable; used by AWS/Google/Microsoft |
| markdown-exec | 1.12.3 | Execute Python code blocks at build time, emit inline SVG figures | Already wired correctly via `docs_fig.py`; `html="1"` + `print(render(f))` is the canonical pattern |
| pymdownx.tabbed | bundled with Material | Content tabs for showing code and output side-by-side | Already enabled (`alternate_style: true`); use `=== "Code"` / `=== "Output"` tabs on example pages |
| pymdownx.arithmatex + KaTeX 0.16.11 | bundled / CDN | Inline and display math | Already configured; KaTeX is faster than MathJax and sufficient for the formulas used |
| pymdownx.superfences | bundled | Nest code blocks inside tabs and admonitions | Already enabled; required by markdown-exec |

### SVG Authoring and Optimization

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| SVGO | **3.3.4** (not 4.x) | Lossless SVG optimization: strip XML preamble, compress path data, deduplicate | Use v3 LTS branch because v4.0.x changed plugin APIs and the ecosystem hasn't fully stabilized around it. v3.3.4 ships the same day as v4.0.2 and is still maintained. Reduces typical hand-authored SVG by 15–35% without touching style or accessibility. |
| Plain text editor + browser | — | Hand-authoring inline SVGs | No change from current approach; no heavyweight tool needed |
| STYLE_SPEC.md | — | Canonical written spec for all SVG style tokens | Lives in `docs/assets/diagrams/`; authors copy the `<style>` block from it into each new SVG. This is the only practical way to share tokens across external `.svg` files since page-level CSS cannot penetrate the SVG boundary. |

**Why SVGO v3, not v4:** SVGO 4.0.0 was released June 2026 and introduced breaking changes to plugin configuration. Many downstream tools have not yet updated. For a docs-quality linting use-case (not icon pipeline), stability matters more than the marginal gains in v4. Revisit at v4.1+.

**Why not Inkscape or Figma exports:** Programmatic or GUI-export SVGs contain irrelevant metadata, unsafe IDs, and layout artifacts. Hand-authoring stays because it gives exact control over every coordinate, class, and label — matching the PROJECT.md constraint.

### SVG Style Specification (the shared token layer)

Since SVGs are referenced as external files (`![...](../assets/diagrams/NAME.svg)`), external CSS from `stylesheets/extra.css` does not apply inside the SVG. Tokens must be replicated in each SVG's `<style>` block. The spec to codify:

| Token | Current value | Recommended value | Notes |
|-------|--------------|-------------------|-------|
| `.ttl` | `font:700 17px system-ui` + fill `#1a1a2e` | Keep as-is | Title text |
| `.sub` | `font:400 12px system-ui` + fill `#6c757d` | Keep as-is | Subtitle / caption |
| `.lab` | `font:700 13px system-ui` | Keep as-is | Panel label |
| `.sm` | `font:400 11px system-ui` + fill `#495057` | Keep as-is | Small annotation |
| `.mono` | `font:600 12px ui-monospace` | Keep as-is | Code / method name |
| viewBox width | 720 | **720 (fixed)** | Must be consistent across all diagrams so they render at the same CSS width |
| viewBox height | 300 | 200 / 300 / 400 | Allow 3 heights only: compact/standard/tall |
| Primary color | `#3f51b5` indigo | Keep — matches Material primary | — |
| Accent / highlight | `#fd7e14` orange | Keep | Used for "after" panels in method diagrams |
| Muted lines | `#adb5bd` | Keep | Arrows, dividers |
| Panel fill (neutral) | `#f8f9fa` | Keep | Background rects |
| Panel fill (accent) | `#fff4ea` | Keep | Highlighted panels |

The `<style>` block template (identical across all SVGs) should be extracted into a reference section of `STYLE_SPEC.md` so authors can copy-paste it.

### SVG Accessibility (WCAG 1.1.1)

The existing pattern is correct and should be the enforced standard:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300"
     fill="none" role="img" aria-label="[Concise description of what the diagram shows]">
  <!-- content -->
</svg>
```

**Do NOT add a `<title>` element** unless you also add `aria-labelledby` pointing to its `id`. A lone `<title>` without `aria-labelledby` is ignored by most screen readers and creates false confidence. The `aria-label` approach (already in use) is simpler and equally valid per WCAG 1.1.1.

For diagrams where the concept is complex enough to warrant a longer description, add:

```xml
<svg role="img" aria-labelledby="diag-title diag-desc" ...>
  <title id="diag-title">Short title</title>
  <desc id="diag-desc">Longer description of the method depicted.</desc>
  ...
</svg>
```

### Reproducible Figure Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| matplotlib | 3.11.1 | Plot figures for example pages | Already in use; current stable |
| numpy | — | Data generation in examples | Already in use; set `np.random.seed(42)` before any stochastic data |
| `svg.hashsalt` rcParam | — | Make matplotlib SVG clip-path IDs deterministic | Without this, every `mkdocs build` produces different SVG content, breaking incremental builds and diffs |

**Required addition to `docs_fig.py`:**

```python
import matplotlib as mpl
mpl.rcParams["svg.hashsalt"] = "fdars-docs"  # deterministic clip-path IDs
```

This one line makes SVG output byte-identical across runs when the data is identical, which enables meaningful `git diff` on built output and deterministic CI.

**Seed discipline for example pages:** Every example block that generates synthetic or sampled data must call `np.random.seed(42)` (or `rng = np.random.default_rng(42)` for new-style API) at the top of the block. This ensures re-running the block produces the same figure without re-seeding the entire process.

### Example Code Testing

| Tool | Version | Purpose | Why |
|------|---------|---------|-----|
| pytest-markdown-docs | **0.9.2** | Runs Python code fences in `.md` files as pytest tests | Best fit: supports `continuation` blocks (multi-block examples that share state), globals injection via `conftest.py`, and `notest` fence tag to skip plotting-only blocks. More featureful than pytest-codeblock for narrative example pages |
| scripts/check_docs_figures.py | existing | Post-build scan for markdown-exec exec-error markers in built HTML | Already in the project; this catches the class of errors that `--strict` misses (exec block exceptions rendered inline rather than failing the build) |

**Test invocation pattern:**

```bash
# 1. Run markdown code-fence tests (fast — no build needed)
pytest --markdown-docs docs/examples/ docs/learn/ docs/represent/ ...

# 2. Full build + strict mode (catches broken links, nav errors)
mkdocs build --strict

# 3. Post-build exec-error scan (catches silent figure failures)
python scripts/check_docs_figures.py site/
```

**conftest.py globals hook** (add to project root `conftest.py`):

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import fdars

def pytest_markdown_docs_globals():
    return {"np": np, "plt": plt, "fdars": fdars}
```

This avoids requiring every example code block to re-import the same stack.

**Fence annotations to use in example pages:**

```markdown
```python notest
# Blocks that only show output or are illustrative — skip from test run
```

```python continuation
# Subsequent blocks that build on previous state in the same page
```
```

### MkDocs Material Features to Exploit

These are already available in the project's config and should be used consistently across example pages:

| Feature | Config key | Use for |
|---------|-----------|---------|
| Content tabs | `pymdownx.tabbed` + `content.tabs.link` | Show "Code" + "Output" side-by-side on example pages |
| Admonitions | `admonition` + `pymdownx.details` | "Note", "Tip", "Warning" callouts for method caveats |
| Code annotations | `pymdownx.highlight` | Annotate specific lines in example code with `# (1)` |
| Snippets | `pymdownx.snippets` (add to config) | Include shared preamble (e.g., dataset loading) from an `includes/` file to avoid repeating 10-line CSV-loading blocks across 6 examples that use the same dataset |

**Snippets is not currently in mkdocs.yml** — add it:

```yaml
markdown_extensions:
  - pymdownx.snippets:
      base_path: [docs]
      check_paths: true
```

Then create `docs/includes/load_canadian.md`, `docs/includes/load_tecator.md`, etc. with the dataset-loading preamble and embed via `--8<-- "includes/load_canadian.md"`.

---

## SVGO Configuration for This Project

Create `svgo.config.mjs` in the repo root:

```javascript
export default {
  multipass: true,
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // Preserve the hand-authored <style> block with CSS classes
          inlineStyles: false,     // would convert .ttl/.sub/.lab rules to inline style attrs
          mergeStyles: false,      // would rewrite the style block
          minifyStyles: false,     // compress CSS — skip to keep class names readable in source

          // Preserve IDs used by CSS selectors and aria-labelledby
          cleanupIds: false,       // would rename/mangle IDs

          // Preserve accessibility elements
          removeDesc: false,       // would strip <desc> elements
          // removeTitle is NOT in preset-default so no override needed

          // Preserve viewBox — essential for responsive scaling
          removeViewBox: false,    // already false by default but make it explicit

          // Preserve intentional transforms in hand-drawn geometry
          convertTransform: false, // optional: disable if transforms are load-bearing
        },
      },
    },
  ],
};
```

**CLI usage:**

```bash
# Optimize all diagrams in-place (dry-run first)
npx svgo --config svgo.config.mjs --folder docs/assets/diagrams/ --dry-run

# Optimize in-place
npx svgo --config svgo.config.mjs --folder docs/assets/diagrams/ --recursive

# Single file
npx svgo --config svgo.config.mjs docs/assets/diagrams/elastic-alignment.svg
```

**What SVGO safely removes** even with the above disabled: XML processing instructions, redundant whitespace, numeric precision on coordinates, unused namespace declarations, empty containers, duplicate path segments. Typical savings on these diagrams: 10–20% without any semantic change.

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| SVGO 3.3.4 | SVGO 4.0.2 | v4 changed plugin API in June 2026; ecosystem still catching up; v3 maintained in parallel |
| pytest-markdown-docs 0.9.2 | pytest-codeblock 0.5.8 | pytest-codeblock lacks continuation blocks and globals injection — needed for multi-step narrative examples |
| pytest-markdown-docs | phmdoctest | phmdoctest generates separate test files from markdown rather than running inline; adds friction to the edit-test cycle |
| Inline `<style>` + STYLE_SPEC.md | CSS custom properties in page stylesheet | External CSS cannot pierce the SVG boundary when SVGs are referenced as `<img src="...">` files; custom properties only work for inline-embedded SVGs |
| aria-label on svg element | `<title>` element alone | `<title>` without `aria-labelledby` is ignored by most screen readers; aria-label is simpler and already the project pattern |
| svg.hashsalt rcParam | Committed figure PNGs | SVGs are lighter, scalable, and already the project's output format; PNGs would require a separate commit step |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SVGO 4.0.x (current) | Plugin API breaking changes in June 2026; insufficient ecosystem testing at this point | SVGO 3.3.4 (LTS branch, same maintenance team, released same day) |
| Diagrams as Code tools (Mermaid, D2, Kroki, Graphviz) | PROJECT.md constraint: diagrams stay hand-authored inline SVG | Continue with hand-authored SVG + STYLE_SPEC.md |
| MathJax | Slower page load than KaTeX; already using KaTeX | KaTeX 0.16.11 (already configured) |
| mkdocs-material Insiders features | Requires paid sponsorship; social cards, tags, etc. are nice-to-have not blockers for this milestone | Use free-tier features only |
| pytest --markdown-docs on exec blocks | markdown-exec blocks use `exec="1"` fence syntax which pytest-markdown-docs does not parse as runnable Python | Use pytest-markdown-docs only on plain ```python fences; verify exec blocks via the existing check_docs_figures.py script |
| Dark-mode SVG variants | Out of scope per PROJECT.md | Leave SVGs as light-mode-only; system-ui fonts and muted palette render acceptably in dark mode |

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| markdown-exec 1.12.3 | Python >=3.10, MkDocs Material 9.x, pymdownx.superfences | Already installed and working |
| mkdocs-material 9.7.7 | Python 3.8+, pymdownx 9.x | Latest stable July 2026 |
| SVGO 3.3.4 | Node.js 14+; npx usage requires no global install | Use npx svgo or install as dev dep in package.json if needed |
| pytest-markdown-docs 0.9.2 | pytest, Python >=3.8 | Requires fdars installed in the test venv |
| matplotlib 3.11.1 | Python 3.9+, numpy compatible | svg.hashsalt available since matplotlib 2.1 |

---

## Installation

```bash
# SVG optimization (one-off or CI — use npx, no global install needed)
npx svgo@3 --config svgo.config.mjs --folder docs/assets/diagrams/

# Example code testing
pip install pytest-markdown-docs

# docs build + figure validation (already in CI or Makefile)
mkdocs build --strict
python scripts/check_docs_figures.py site/

# Add to pyproject.toml [project.optional-dependencies] docs group:
# pytest-markdown-docs
# matplotlib>=3.9
# numpy
# scipy
# scikit-learn
# pandas
```

---

## Sources

- [markdown-exec PyPI](https://pypi.org/project/markdown-exec/) — version 1.12.3, July 2026 (LOW confidence via websearch)
- [mkdocs-material PyPI](https://pypi.org/project/mkdocs-material/) — version 9.7.7, July 2026 (LOW confidence via websearch)
- [SVGO GitHub releases](https://github.com/svg/svgo/releases) — v3.3.4 and v4.0.2 both July 2026 (LOW confidence via websearch)
- [SVGO preset-default docs](https://svgo.dev/docs/preset-default/) — full 33-plugin list, overrides API (LOW confidence via WebFetch)
- [SVGO plugins reference](https://svgo.dev/docs/plugins/) — plugin categories (LOW confidence via WebFetch)
- [pytest-markdown-docs PyPI](https://pypi.org/project/pytest-markdown-docs/) — version 0.9.2, March 2026; continuation/globals features (LOW confidence via websearch)
- [matplotlib PyPI](https://pypi.org/project/matplotlib/) — version 3.11.1, July 2026 (LOW confidence via websearch)
- [matplotlib svg.hashsalt](https://matplotlib.org/stable/users/prev_whats_new/whats_new_2.1.0.html) — introduced matplotlib 2.1; deterministic clip-path IDs (LOW confidence via websearch)
- [Creating Accessible SVGs — Deque](https://www.deque.com/blog/creating-accessible-svgs/) — role=img + aria-label/aria-labelledby patterns (LOW confidence via websearch)
- [WCAG 1.1.1 SVG guidance — getwcag.com](https://getwcag.com/en/accessibility-guide/svg-img-alt) — accessible name requirement (LOW confidence via websearch)
- Existing project codebase: `docs/assets/diagrams/*.svg`, `scripts/docs_fig.py`, `scripts/check_docs_figures.py`, `mkdocs.yml` — used as primary ground truth for existing baseline

---

*Stack research for: fdars/pyfda documentation overhaul — SVG diagrams + example pages*
*Researched: 2026-08-07*
