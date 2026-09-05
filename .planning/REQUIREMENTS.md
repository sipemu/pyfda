# Requirements: pyfda — v12.0 Docs Depth, Card Coverage & AI Capability Skill

**Defined:** 2026-09-05
**Core Value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

**Milestone shape:** Docs + skill only. No `fdars-core` bump, no new PyO3 bindings (v7.0/v10.0 precedent). Package version may tick for the release.

## v12.0 Requirements

### Documentation Depth (DEPTH)

Bring the thin v11.0-era method pages (currently 20–35% of the mature-page baseline) up to parity. "Parity" = a "When to use" decision section, a "See also" cross-reference block, parameter-selection + result-interpretation guidance, ≥3 caution/tip/note admonition boxes, and ≥3 runnable inline `FDARS_FENCE_OK` worked examples per page.

- [x] **DEPTH-01**: The regression-family thin pages — `frechet-regression`, `function-on-function`, `additive-sof`, `concurrent-regression`, `functional-glm` — each reach the parity bar above.
- [x] **DEPTH-02**: The analyze-family thin pages — `functional-time-series`, `density-fda`, `multi-domain`, `shapelets`, `advanced-clustering` — each reach the parity bar above.
- [ ] **DEPTH-03**: Every new/extended fence on the DEPTH pages runs offline against the current `fdars` API and existing `docs/data/` datasets, emitting `FDARS_FENCE_OK`; method claims are accurate against the shipped bindings.

### Worked Examples (EXMP)

2–3 flagship end-to-end example pages for marquee new methods, matching the mature `examples/` standard (narrative + real dataset + runnable offline fences), wired into nav and the examples gallery.

- [x] **EXMP-01**: A flagship Functional Time Series example page (e.g. forecast + evaluation) against a `docs/data/` dataset, runnable offline (`FDARS_FENCE_OK`).
- [x] **EXMP-02**: A flagship Fréchet-regression example page (metric-space response walkthrough), runnable offline (`FDARS_FENCE_OK`).
- [x] **EXMP-03**: A third flagship example page for another marquee new method (e.g. shapelet classification or density FDA) **if a strong dataset fit exists**; otherwise this scope is satisfied by EXMP-01/02 (the "2–3" range).

### Card Coverage (CARD)

Complete section-landing card coverage across the focus sections. Each missing card needs a hand-authored inline SVG thumbnail at `docs/assets/thumb/<page-slug>.svg` plus a `fdars-gallery` card entry in the section `index.md`.

- [x] **CARD-01**: Align landing page reaches 100% — thumbnails + cards for `shift-registration`, `banded-alignment`.
- [x] **CARD-02**: Represent landing page reaches 100% — thumbnails + cards for `pace-fpca`, `interpolation`, `imputation`.
- [ ] **CARD-03**: Regression landing page reaches 100% — thumbnails + cards for `concurrent-regression`, `functional-glm`, `function-on-function`, `additive-sof`, `frechet-regression`.
- [ ] **CARD-04**: Analyze landing page reaches 100% — thumbnails + cards for `functional-time-series`, `density-fda`, `advanced-clustering`, `multi-domain`, `shapelets`, `functional-boxplot`, `functional-statistics`, `scoring-metrics`.
- [ ] **CARD-05**: Examples landing page gains cards for the 3 uncarded pages — `functional-outlier-workflow`, `canadian-depth-centrality`, `tolerance-vs-conformal`.
- [x] **CARD-06**: All new thumbnails are hand-authored inline SVG, STYLE_SPEC-conformant, decorative-accessible (matching the existing `aria-hidden` card pattern), and pass the SVGO idempotence + build-determinism gate.

### AI Capability Skill (SKILL)

Give AI agents a way to discover the full fdars capability surface, across all three surfaces the user selected. Distinct from — and non-duplicating — the existing narrow `fdars-advisor` skill/MCP.

- [ ] **SKILL-01**: A standalone capability-discovery Agent Skill with a spec-valid `SKILL.md` mapping the whole fdars surface — every public submodule, what each method does, when to reach for it, and how to call it (signature + minimal usage).
- [ ] **SKILL-02**: The skill's capability map is verified accurate against the live package by an automated test/harness (documented methods exist and are importable; no stale/renamed entries).
- [ ] **SKILL-03**: An LLM-oriented docs page (llms.txt-style API digest of the whole library) authored/generated and wired into the site for agents to read.
- [ ] **SKILL-04**: An MCP capability tool (e.g. `fdars_list_capabilities` / describe) added to the existing server, returning the capability surface; the MCP compute boundary stays provably LLM-free and the guard/tests are updated to cover it.

### Close Gate (GATE)

- [ ] **GATE-01**: Whole-site `mkdocs build --strict` green offline; all worked examples across the milestone emit `FDARS_FENCE_OK`.
- [ ] **GATE-02**: SVGO idempotence + build-determinism gate green across all new/changed SVGs.
- [ ] **GATE-03**: Blocking human diagram/method-accuracy review of the new thumbnails (and any new concept diagrams) — approved before close.
- [ ] **GATE-04**: Grounding invariant + MCP LLM-free boundary preserved — advisor/MCP tests (incl. guard-sync) green after the SKILL-04 tool lands.

## Future Requirements

Deferred; tracked but not in this roadmap.

### Documentation

- **CARD-FUT-01**: Add a gallery/card grid to the Advisor (7 pages) and sklearn (5 pages) landing pages — they currently use a deliberate no-gallery text pattern; converting them is a separate design decision.
- **DEPTH-FUT-01**: Depth sweep of any older thin pages beyond the v11.0-era set surfaced during work.

## Out of Scope

| Feature | Reason |
|---------|--------|
| `fdars-core` version bump / new PyO3 bindings | This is a docs + skill milestone; no upstream capability work (user decision) |
| Advisor/sklearn landing-page galleries | Deliberate no-gallery pattern today; conversion is a separate design call (→ CARD-FUT-01) |
| Programmatic/tool-generated concept diagrams | Diagrams stay hand-authored inline SVG (standing project decision) |
| Dark-mode / theming rework of SVGs | Out of this milestone's intent (standing) |
| New LLM logic in the MCP capability tool | MCP boundary must stay provably LLM-free; the tool only describes the static surface |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEPTH-01 | Phase 74 | Complete |
| DEPTH-02 | Phase 75 | Complete |
| DEPTH-03 | Phase 79 | Pending |
| EXMP-01 | Phase 76 | Complete |
| EXMP-02 | Phase 76 | Complete |
| EXMP-03 | Phase 76 | Complete |
| CARD-01 | Phase 77 | Complete |
| CARD-02 | Phase 77 | Complete |
| CARD-03 | Phase 77 | Pending |
| CARD-04 | Phase 77 | Pending |
| CARD-05 | Phase 77 | Pending |
| CARD-06 | Phase 77 | Complete |
| SKILL-01 | Phase 78 | Pending |
| SKILL-02 | Phase 78 | Pending |
| SKILL-03 | Phase 78 | Pending |
| SKILL-04 | Phase 78 | Pending |
| GATE-01 | Phase 79 | Pending |
| GATE-02 | Phase 79 | Pending |
| GATE-03 | Phase 79 | Pending |
| GATE-04 | Phase 79 | Pending |

**Coverage:**

- v12.0 requirements: 20 total
- Mapped to phases: 20 ✓
- Unmapped: 0

---
*Requirements defined: 2026-09-05*
*Last updated: 2026-09-05 after roadmap creation (traceability mapped to Phases 74–79)*
