# Requirements: pyfda — v7.0 Documentation Quality Pass

**Defined:** 2026-08-22
**Core Value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

## v7.0 Requirements

Documentation-only quality milestone. No `fdars-core` bump, no new bindings. Requirements map to roadmap phases (continue numbering from Phase 41 → start at Phase 42).

### Audit

- [ ] **AUDIT-01**: A diagram audit report inventories all 68 concept diagrams in `docs/assets/diagrams/` (cards/ and thumb/ excluded), each scored on the four fix axes — visual/layout quality, STYLE_SPEC conformance, XML source formatting, method-accuracy — producing a ranked, per-section fix list that gates the fix phases. Report also confirms the per-page diagram-coverage gap (which `examples/` and advisor pages lack a concept SVG) and the thin-page extension list.

### SVG Fix

- [ ] **SVGFIX-01**: Every concept diagram flagged for visual/layout issues is corrected — no overlapping labels, consistent spacing, alignment, and sizing — verified on the built site (rendered PNG check).
- [ ] **SVGFIX-02**: Every concept diagram conforms to `docs/assets/diagrams/STYLE_SPEC.md` — palette, system-ui fonts, `viewBox`, the `.ttl/.sub/.lab/.sm/.mono` CSS classes, and `role="img"` + `aria-label`.
- [ ] **SVGFIX-03**: Every concept diagram's XML source is clean and hand-editable and passes the SVGO idempotence + build-determinism CI gate (byte-identical rebuilds for deterministic content).
- [ ] **SVGFIX-04**: Every concept diagram is method-accurate against the shipped `fdars` bindings — no diagram misdepicts what its method does (per the v6.0 hypograph/epigraph lesson).

### Diagram Coverage

- [ ] **DIACOV-01**: Each of the ~21 `docs/examples/*.md` worked-example pages carries a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG, wired into the page.
- [ ] **DIACOV-02**: Each of the 5 advisor surface pages (`python-api`, `mcp`, `providers`, `agent-skill`, `aspects`) carries a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG.

### Page Depth

- [ ] **DEPTH-01**: The thin v6.0 method pages (`regression/concurrent-regression`, `regression/functional-glm`, `represent/pace-fpca`, `inference/interval-inference`) are extended to mature-page structure — intro, method explanation, worked example, parameters, caveats/interpretation.
- [ ] **DEPTH-02**: The thin v4/v5 method pages (`represent/interpolation`, `represent/imputation`, `analyze/scoring-metrics`, `analyze/functional-statistics`, and any other sub-~200-line method page surfaced by AUDIT-01) are extended to mature-page structure.
- [ ] **DEPTH-03**: Extended pages gain new worked examples and/or cross-links where they add value; every worked example runs offline against the current `fdars` API and emits `FDARS_FENCE_OK`, with fence data kept small (synthetic `n ≤ 20`; subsampled datasets).

### Site Gate

- [ ] **GATE-01**: Whole-site `mkdocs build --strict` is green offline after all changes.
- [ ] **GATE-02**: Per-section review is held on the built site, and a blocking human diagram method-accuracy review passes before milestone close.

## Future Requirements

Deferred, tracked but not in the current roadmap.

### Diagrams

- **DIAG-FUT-01**: Long-form `<title>`/`<desc>` + `aria-labelledby` accessibility pass for complex diagrams (carried over: A11Y-01).
- **DIAG-FUT-02**: Regenerate `thumb/` and `cards/` SVGs to mirror any concept diagram whose composition changed materially during the audit (only if a thumb visibly diverges).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Programmatic / tool-generated diagrams | Diagrams stay hand-authored inline SVG — standing project decision |
| `cards/` and `thumb/` SVG audit | Audit targets the 68 concept diagrams; cards/thumbs are decorative, revisited only if a fixed diagram's thumb visibly diverges (→ DIAG-FUT-02) |
| Dark-mode / theming rework of SVGs | Not part of this milestone's intent — standing exclusion |
| `fdars-core` bump / new bindings / advisor logic changes | Docs-only quality milestone; no code-behavior change |
| Reference-API pages (`docs/reference/*`) content | Auto-derived stubs; not concept pages — out of the depth/diagram scope |
| New method pages for unbound capabilities | No new bindings this milestone; nothing new to document |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUDIT-01 | Phase 42 | Pending |
| SVGFIX-01 | Phases 43, 44, 45 | Pending |
| SVGFIX-02 | Phases 43, 44, 45 | Pending |
| SVGFIX-03 | Phases 43, 44, 45 | Pending |
| SVGFIX-04 | Phases 43, 44, 45 | Pending |
| DIACOV-01 | Phase 46 | Pending |
| DIACOV-02 | Phase 47 | Pending |
| DEPTH-01 | Phase 48 | Pending |
| DEPTH-02 | Phase 48 | Pending |
| DEPTH-03 | Phase 48 | Pending |
| GATE-01 | Phase 49 | Pending |
| GATE-02 | Phase 49 | Pending |

**Coverage:**
- v7.0 requirements: 12 total
- Mapped to phases: 12 ✓
- Unmapped: 0

**Note on SVGFIX-01..04:** These four quality axes are applied per diagram across the three section-batched fix phases (43 learn/represent/align, 44 analyze/monitoring/advisor, 45 regression/inference). Each fix phase delivers all four axes for its batch; the requirements are jointly completed once all three batches pass. No diagram is fixed in more than one phase (each diagram belongs to exactly one section batch).

---
*Requirements defined: 2026-08-22*
*Last updated: 2026-08-22 — traceability populated during v7.0 roadmap creation (12/12 mapped)*
