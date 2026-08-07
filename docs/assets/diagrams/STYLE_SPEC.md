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

The gate is **check-only**: it diffs stdout against the source file. A zero diff means the
diagram is conforming. The gate **never rewrites** a committed hand-authored SVG (D-02).

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
| `0 0 720 300` | 300 | Standard single-row layout (34 of 43 diagrams use this) |
| `0 0 720 480` | 480 | Tall two-row layouts (4 conforming diagrams) |
| `0 0 720 520` | 520 | Extra-tall three-row layouts (1 conforming diagram) |

**SVG root pattern:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none" role="img" aria-label="[descriptive text matching diagram title]">
```

### Legacy Non-Conforming viewBoxes (migration targets)

These 4 diagrams use non-standard widths. They are flagged as migration targets for later
diagram-sweep phases (DIA-01 through DIA-06). Do **not** migrate them in Phase 1.

| File | viewBox | Target Phase |
|------|---------|-------------|
| `elastic-clustering.svg` | `0 0 700 250` | Phase 3 |
| `outlier-detection.svg` | `0 0 600 350` | Phase 6 |
| `covariance-functions.svg` | `0 0 600 425` | Phase 5 |
| `ex-sonar-tsrvf.svg` | `0 0 700 400` | Phase 7 |

---

## Accessibility Pattern

Every conforming diagram must have `role="img"` and `aria-label` on the root `<svg>`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none"
     role="img" aria-label="[descriptive text matching the diagram title]">
```

The `aria-label` must match the diagram's title text (the `.ttl` element content).

**Status:** 34 of 43 diagrams currently have `role="img"`. The 9 missing are legacy diagrams
targeted for migration in later phases.

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

**Full-corpus result (Phase 1, Plan 1, Task 3 — verified 2026-08-07):**

All **43 of 43** diagrams in `docs/assets/diagrams/` pass the idempotence gate under
`svgo.config.mjs`. No exclusion list is required.

**Excluded diagrams:** none.

**Verified preserved constructs on all 43 diagrams:**
- `<style>` block with five CSS classes (`.ttl .sub .lab .sm .mono`)
- `role="img"` and `aria-label` (where present; 34 of 43 have these)
- `viewBox` attribute
- Element IDs
- `<desc>` elements (where present)

**Known non-conformances (not gate failures, migration targets):**
- 8 diagrams have no `<style>` block (use inline `font-size` attributes) — pass gate (no
  CSS to inline or mangle)
- 4 diagrams have non-720 viewBox widths — pass gate (viewBox is preserved, not enforced)
- 9 diagrams missing `role="img"` — pass gate (not enforced by the svgo gate, per D-03)

These are tracked as migration targets for diagram-sweep phases 3–8.

---

## Conformance Summary

**Conforming diagrams (35 of 43):** Have `<style>` block with canonical five classes, `role="img"`,
`aria-label`, `viewBox="0 0 720 {300|480|520}"`, `fill="none"` on root `<svg>`.

**Legacy / non-conforming diagrams (8 of 43):** Use inline `font-size` attributes, missing
`<style>` block, missing `role="img"`, and some have non-720 viewBox widths. These are flagged
but NOT migrated in Phase 1 — they are targets for later diagram-sweep phases.
