# fdars SVG Diagram Style Specification

**Version:** 1.0 (Phase 1 Foundation)
**Status:** Canonical — all new and migrated diagrams must conform.

This specification formalizes the existing 35-diagram baseline into a written contract.
It is the authoring reference for diagram-sweep phases 3–8. Do not invent a new look —
formalize the existing baseline.

---

## SVGO Invocation (mandatory)

The SVGO lint gate checks diagram conformance. **Always invoke with the config flag and the
exact pinned version:**

```bash
npx svgo@3.3.4 --config svgo.config.mjs --quiet --input <file.svg> --output -
```

**Pin `svgo@3.3.4`** — not `latest`. svgo v4 has a different CLI and config API (Pitfall 6).

**Always pass `--config svgo.config.mjs`** — without it, svgo's default `inlineStyles` plugin
converts `.ttl`/`.sub`/`.lab`/`.sm`/`.mono` CSS classes into inline `style=` attributes,
corrupting the canonical class-based structure (Pitfall 1).

The gate is **check-only** and uses an **idempotence check**, not a direct diff against the
source: svgo's XML serialiser always normalises whitespace and attribute ordering, so a direct
diff against a hand-formatted SVG always shows cosmetic differences. The gate instead confirms
`svgo(svgo(svg)) == svgo(svg)` — a zero diff on the second pass means the diagram is conforming
(no further semantic transformation is applied). The gate **never rewrites** a committed
hand-authored SVG (D-02). See "SVGO Gate Coverage" below for details.

---

## Canonical `<style>` Block

Copy this block verbatim into every conforming SVG, immediately after the `<svg>` opening tag:

```xml
<style>
  .ttl{font:700 17px system-ui,-apple-system,sans-serif;fill:#1a1a2e}
  .sub{font:400 12px system-ui,sans-serif;fill:#6c757d}
  .lab{font:700 13px system-ui,sans-serif}
  .sm{font:400 11px system-ui,sans-serif;fill:#495057}
  .mono{font:600 12px ui-monospace,monospace}
</style>
```

### Typography Classes

| Class | Weight | Size | Fill | Semantic Role |
|-------|--------|------|------|---------------|
| `.ttl` | 700 | 17px | `#1a1a2e` (near-black) | Diagram title — centered at y≈26 |
| `.sub` | 400 | 12px | `#6c757d` (muted grey) | Subtitle/caption — centered at y≈46 |
| `.lab` | 700 | 13px | (set per element) | Panel/section label — color set per element |
| `.sm`  | 400 | 11px | `#495057` (mid-grey) | Small annotation text |
| `.mono`| 600 | 12px | (set per element) | Monospace code labels (e.g., function names) |

Font stack: `system-ui, -apple-system, sans-serif` (body); `ui-monospace, monospace` (mono).

---

## Colour Palette

### Structural Colours

| Hex | Role | Usage |
|-----|------|-------|
| `#1a1a2e` | Near-black | Title text only (`.ttl` fill) |
| `#6c757d` | Muted grey | Subtitle text, secondary annotations (`.sub` fill) |
| `#495057` | Mid-grey | `.sm` text, structural lines, annotations |
| `#ced4da` | Light grey | Panel borders (`stroke`), axis lines (`stroke-width 1.2–1.5`) |
| `#f8f9fa` | Near-white | Panel fill / background (`fill` on neutral panels) |
| `#fd7e14` | Orange accent | Method/process panel stroke; also `#fff4ea` fill on those panels |
| `#f8d7b8` | Pale orange | Inner element borders within orange accent panels |

### Data-Curve Palette (FDARS_COLORS — from `scripts/docs_fig.py`)

Used for plotted functional data curves in order:

| Hex | Name |
|-----|------|
| `#3f51b5` | Indigo |
| `#e8710a` | Orange |
| `#198754` | Green |
| `#dc3545` | Red |
| `#6f42c1` | Purple |
| `#0dcaf0` | Cyan |
| `#6c757d` | Grey |

---

## Stroke Weights

| Element | `stroke-width` |
|---------|---------------|
| Panel border (outer rect edge) | `1.5` |
| Axis / reference lines | `1.2` |
| Data curves (primary) | `2.0` – `2.8` |
| Data curves (secondary / faded) | `1.4` – `1.6` |
| Arrows | `2.0` |

---

## viewBox Conventions

**Fixed width: always 720.** Height is one of three allowed values:

| viewBox | Height | When to use |
|---------|--------|-------------|
| `0 0 720 300` | 300 | Standard single-row layout (64 of 93 concept diagrams use this) |
| `0 0 720 480` | 480 | Tall two-row layouts (28 concept diagrams) |
| `0 0 720 520` | 520 | Extra-tall three-row layouts (1 concept diagram) |

**SVG root pattern:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none" role="img" aria-label="[descriptive text matching diagram title]">
```

### Legacy Non-Conforming viewBoxes — RESOLVED

The 4 diagrams formerly flagged as non-standard-width migration targets
(`elastic-clustering.svg`, `outlier-detection.svg`, `covariance-functions.svg`,
`ex-sonar-tsrvf.svg`) were all migrated to the canonical `720`-width grid during the
v7.0 diagram-quality pass and the v10.0 corrections. **All 93 concept diagrams now use a
`720`-width viewBox** (`720×300`, `720×480`, or `720×520`). No non-conforming viewBoxes remain.

---

## Accessibility Pattern

Every concept diagram must carry the full accessibility markup on the root `<svg>`:
`role="img"`, an `aria-label`, and a long-form `<title>` + `<desc>` wired via
`aria-labelledby`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none"
     role="img" aria-label="[text matching the diagram title]"
     aria-labelledby="NAME-title NAME-desc">
  <title id="NAME-title">[concise diagram name]</title>
  <desc id="NAME-desc">[1–2 sentences: what the diagram depicts and the method it illustrates]</desc>
```

The `aria-label` and `<title>` must match the diagram's visible title text (the `.ttl`
element content). The `<desc>` gives screen-reader users the method-level meaning that the
visual conveys. `aria-labelledby` references the in-document `<title>` and `<desc>` ids.

**Decorative gallery thumbnails** (`docs/assets/thumb/*.svg`, embedded via
`<img class="fdars-gallery-thumb">` on section index pages) are decorative duplicates of
their linked titles: they use empty `alt=""` **and** `aria-hidden="true"` so screen readers
do not double-announce them.

**Status:** All **93 of 93** concept diagrams have `role="img"`, a title-matching
`aria-label`, and long-form `<title>`/`<desc>`/`aria-labelledby` (universal as of the v10.0
Diagram Quality & Accessibility Pass). All 58 gallery thumbnails carry `aria-hidden="true"`.

---

## Panel Patterns

### Neutral Panel

```xml
<rect x="24" y="70" width="196" height="188" rx="12"
      fill="#f8f9fa" stroke="#ced4da" stroke-width="1.5"/>
```

### Method/Process Panel (orange accent)

```xml
<rect x="272" y="70" width="176" height="188" rx="12"
      fill="#fff4ea" stroke="#fd7e14" stroke-width="1.5"/>
```

---

## SVGO Gate Coverage

**Gate approach:** Idempotence check — not a direct diff against the hand-authored source.
svgo's XML serialiser always normalises whitespace and attribute ordering regardless of plugin
settings; a direct diff against the formatted source always shows cosmetic differences.
The idempotence check (svgo(svgo(svg)) == svgo(svg)) proves no further semantic transformation
is applied after the first pass.

**Full-corpus result (refreshed in the v10.0 Diagram Quality & Accessibility Pass, 2026-09-02):**

All **93 of 93** concept diagrams in `docs/assets/diagrams/` pass the idempotence gate under
`svgo.config.mjs`. No exclusion list is required.

**Excluded diagrams:** none.

**Verified preserved constructs on all 93 diagrams:**
- `<style>` block with five CSS classes (`.ttl .sub .lab .sm .mono`) — present on all 93
- `role="img"`, title-matching `aria-label`, and `<title>`/`<desc>`/`aria-labelledby` — present on all 93
- `viewBox` attribute (all `720`-width)
- Element IDs
- `<desc>` elements

**Known non-conformances:** none. The v1.0-era gaps (8 diagrams without a `<style>` block,
4 non-720 viewBoxes, 9 missing `role="img"`) were all resolved across the v7.0 and v10.0
diagram passes — every concept diagram is now fully conformant and fully accessible.

---

## Conformance Summary

**Conforming diagrams (35 of 43):** Have `<style>` block with canonical five classes, `role="img"`,
`aria-label`, `viewBox="0 0 720 {300|480|520}"`, `fill="none"` on root `<svg>`.

**Legacy / non-conforming diagrams (8 of 43):** Use inline `font-size` attributes, missing
`<style>` block, missing `role="img"`, and some have non-720 viewBox widths. These are flagged
but NOT migrated in Phase 1 — they are targets for later diagram-sweep phases.
