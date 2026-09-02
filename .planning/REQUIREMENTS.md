# Requirements: pyfda — v10.0 Diagram Quality & Accessibility Pass

**Defined:** 2026-09-02
**Core Value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

## Milestone v10.0 Requirements

Docs-only diagram quality pass over all 156 hand-authored inline SVGs (90 concept in `docs/assets/diagrams/`, 8 section cards in `docs/assets/cards/`, 58 gallery thumbnails in `docs/assets/thumb/`). No `fdars-core` bump, no bindings, no advisor/MCP changes, no package version bump. Diagrams stay hand-authored inline SVG. Scope: consistency + defect-fix (no palette/typography change); dark-mode out of scope; audit covers all 156.

### Audit & Inventory

- [x] **AUDIT-01**: A scored inventory of all 156 SVGs is produced as the milestone-gating artifact, scoring each on design/geometry quality, STYLE_SPEC conformance, accessibility, and thumb/card sync
- [x] **AUDIT-02**: The inventory flags each diagram with defect severity and identifies coverage gaps (pages/methods that lack a diagram), driving the DEFECT/COVER scope

### Design-Quality Defects

- [ ] **DEFECT-01**: Every diagram flagged with geometry/line defects (mismatched lines, misaligned endpoints, overlapping or misplaced elements) is corrected
- [ ] **DEFECT-02**: Every diagram flagged with layout defects (spacing, alignment, label overlap, panel sizing) is corrected
- [ ] **DEFECT-03**: Every defect fix preserves method-accuracy — a correction never makes the diagram misdepict the method

### Accessibility (A11Y-01)

- [ ] **A11Y-01**: Every concept diagram has `role="img"` and an `aria-label` matching its title text (closes the basic gaps left stale in STYLE_SPEC)
- [ ] **A11Y-02**: Complex/multi-panel diagrams carry a long-form `<title>` + `<desc>` wired via `aria-labelledby` so screen readers convey what the diagram depicts
- [ ] **A11Y-03**: Decorative gallery thumbnails use correct non-announcing semantics (empty `alt` / `aria-hidden`) consistently

### Cards / Thumbs Sync (DIAG-FUT-02)

- [ ] **SYNC-01**: All 58 gallery thumbnails reflect their current concept diagrams — redrawn/regenerated where they have drifted
- [ ] **SYNC-02**: All 8 section cards are reviewed and brought to the same quality and consistency bar as the concept diagrams

### New Coverage

- [ ] **COVER-01**: Diagrams are added for the audit-identified pages/methods that lack one, each method-accurate and STYLE_SPEC-conformant

### STYLE_SPEC Conformance

- [ ] **SPEC-01**: All 156 SVGs conform to the current STYLE_SPEC (viewBox conventions, canonical `<style>` block, colour palette, stroke weights, panel patterns)
- [ ] **SPEC-02**: STYLE_SPEC.md is updated — stale status/counts refreshed and the accessibility pattern finalized to match the shipped diagram set

### Gate

- [ ] **GATE-01**: SVGO idempotence + build-determinism gate green across all diagrams (no drift on re-run)
- [ ] **GATE-02**: Whole-site `mkdocs build --strict` green offline
- [ ] **GATE-03**: Blocking human diagram review approved before milestone close

## Future Requirements

Deferred to a later milestone. Tracked but not in this roadmap.

### Diagrams

- **DIAG-FUT-01b**: Full dark-mode / theming adaptation of the diagram set (CSS-var / media-query styling)
- **DIAG-FUT-03**: Palette / typography re-theme (a "full re-theme" refresh, beyond consistency + defect-fix)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Dark-mode / theming rework of SVGs | User chose consistency + defect-fix depth only; matches standing decision (deferred as DIAG-FUT-01b) |
| Palette / typography re-theme | User chose consistency + defect-fix; keep the current STYLE_SPEC palette/type (deferred as DIAG-FUT-03) |
| Programmatic / tool-generated diagrams | Locked constraint — diagrams stay hand-authored inline SVG |
| `fdars-core` bump / new bindings / advisor / MCP changes | Docs-only milestone; no code or compute changes |
| Package version bump | Docs-only milestone produces no shippable package change (v7.0 precedent) |
| Rewriting example-page prose or worked examples | This milestone is diagrams-only; page-depth/examples were v7.0 scope |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUDIT-01 | Phase 60 | Complete |
| AUDIT-02 | Phase 60 | Complete |
| DEFECT-01 | Phases 61, 62, 63 | Pending |
| DEFECT-02 | Phases 61, 62, 63 | Pending |
| DEFECT-03 | Phases 61, 62, 63 | Pending |
| A11Y-01 | Phases 61, 62, 63 | Pending |
| A11Y-02 | Phases 61, 62, 63 | Pending |
| A11Y-03 | Phase 64 | Pending |
| SYNC-01 | Phase 64 | Pending |
| SYNC-02 | Phase 64 | Pending |
| COVER-01 | Phase 64 | Pending |
| SPEC-01 | Phases 61, 62, 63 | Pending |
| SPEC-02 | Phase 65 | Pending |
| GATE-01 | Phase 65 | Pending |
| GATE-02 | Phase 65 | Pending |
| GATE-03 | Phase 65 | Pending |

**Note on batched requirements:** DEFECT-01/02/03, A11Y-01/02, and SPEC-01 are cross-cutting correction requirements delivered incrementally across the three section-batched correction phases (61 learn/represent/align, 62 analyze/monitoring/advisor, 63 regression/inference/examples). Each requirement is fully satisfied only once all three batches are complete (verified at the Phase 63 completion criterion + the Phase 65 whole-site gate). This is the same section-batching pattern used for SVGFIX-* across v7.0 Phases 43–45.

**Coverage:**

- v10.0 requirements: 16 total
- Mapped to phases: 16 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-02*
*Last updated: 2026-09-02 after roadmap creation (Phases 60–65 mapped; 16/16 covered)*
