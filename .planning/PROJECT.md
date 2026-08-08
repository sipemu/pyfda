# pyfda — Documentation Overhaul

## What This Is

pyfda is the PyO3 binding layer that exposes the Rust `fdars-core` functional-data-analysis library to Python as the `fdars` package (represent, smooth, align, analyze, regress, monitor). This milestone is a **documentation overhaul**: reworking the MkDocs site's hand-authored SVG diagrams and its worked example pages to a consistently high, method-accurate standard.

## Core Value

The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

## Requirements

### Validated

<!-- Existing capabilities inferred from the codebase map — the product being documented. -->

- ✓ PyO3 binding layer exposing `fdars-core` compute to Python (`fdars` package) — existing
- ✓ MkDocs (Material) documentation site with sections: learn, represent, smooth, align, analyze, regression, monitoring, reference, examples — existing
- ✓ ~50 hand-authored inline SVG concept diagrams in `docs/assets/diagrams/` (plus cards/ and thumb/) — existing
- ✓ Build-time inline figures via `markdown-exec` + `scripts/docs_fig.py` (`PYTHONPATH=scripts`) — existing
- ✓ 17 narrative example pages in `docs/examples/*.md` backed by datasets in `docs/data/` — existing
- ✓ Released at v0.2.0 with R-parity phase 1 complete — existing
- ✓ Documentation tooling foundation — `STYLE_SPEC.md`, SVGO check-only lint gate in CI (idempotence, all 43 diagrams), build determinism (`svg.hashsalt` + `<dc:date>` suppression — verified byte-identical across builds for deterministic content), `pymdownx.snippets` dataset includes, `pytest-markdown-docs` doc-test harness (one-page CI gate), and the `DOCS_FAST` helper — Phase 1
- ✓ Nav + reference-API audit — `02-AUDIT.md` maps all 42 method-section pages on style/accuracy axes (D-02 rollup), a full R-era grep report (4 leftovers, all in `spm.svg`), and a ranked GAP-0001..0011 / EX-0001..0008 list with a user Selection column gating Phase 3 — Phase 2

### Active

<!-- The documentation overhaul. Hypotheses until shipped and validated. -->

**SVG diagrams (priority):**
- [ ] Establish a shared SVG style spec (palette, typography, spacing, viewBox conventions) and apply it for visual consistency across all diagrams
- [ ] Correct diagrams so each faithfully depicts what the underlying method actually does (accuracy to the method)
- [ ] Close diagram coverage gaps — every page that warrants a diagram has an accurate, non-generic one
- [ ] All diagrams remain hand-authored inline SVG (no move to programmatic generation)

**Example pages (secondary):**
- [ ] Every `docs/examples/*.md` runs correctly against the current `fdars` API and produces the shown output
- [ ] Richer narrative — explain the why/interpretation, not just code
- [ ] Improved output figures (clarity, styling, captions)
- [ ] Add new worked examples covering under-documented capabilities

**Foundation:**
- [x] Nav + reference-API audit that proposes the concrete list of diagram coverage gaps and new-example candidates — validated in Phase 2 (`02-AUDIT.md`)

### Out of Scope

- Programmatic/tool-generated diagrams — user chose to keep diagrams hand-authored inline SVG
- Dark-mode / theming rework of SVGs — not part of this milestone's intent
- Library/runtime code changes to `fdars` or `fdars-core` — this is a documentation milestone; code fixes only if an example exposes a genuine binding bug
- R-parity feature work — tracked separately (see `PARITY_PLAN.md`)

## Context

- **Site build:** MkDocs Material (`mkdocs.yml`); diagrams referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`. Inline figures use `markdown-exec` importing `docs_fig` from `scripts/` (canonical mechanism is `PYTHONPATH=scripts`; `docs/hooks.py` is a fallback). A `site/` build output and a docs CI workflow already exist.
- **Diagram style today:** `viewBox="0 0 720 300"`, inline `<style>` classes (`.ttl/.sub/.lab/.sm/.mono`), system-ui fonts, muted Bootstrap-ish palette, `role="img"` + `aria-label`. This is the de-facto baseline the shared style spec will formalize.
- **Datasets:** `docs/data/` (canadian weather, growth, phoneme, tecator, sonar, wine) drive the narrative examples; standalone scripts also live in top-level `examples/`.
- **Codebase map:** see `.planning/codebase/` (ARCHITECTURE, STRUCTURE, STACK, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS).

## Constraints

- **Authoring**: Diagrams stay hand-authored inline SVG — max conceptual control, edited by hand against a shared style spec.
- **Accuracy**: Diagrams and example outputs must be method-accurate; correctness is validated by section review on the built site, not assumed.
- **Compatibility**: Examples must run against the *current* `fdars` API and existing datasets in `docs/data/`.
- **Process**: Work proceeds section-by-section (learn/, align/, analyze/, regression/, monitoring/, represent/, examples/) with a review gate per section before moving on.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep diagrams as hand-authored inline SVG | Max control over the conceptual look; matches existing baseline | — Pending |
| Formalize a shared SVG style spec before rollout | Consistency across ~50 diagrams needs one standard | — Pending |
| Full sweep of all diagrams + all example pages | User wants the whole doc set brought to one bar | — Pending |
| Review per doc section via the built site | User validates accuracy/style in batches before rollout continues | — Pending |
| Derive coverage/new-example list from nav + reference-API audit | Systematic gap detection over guesswork | ✓ Done — `02-AUDIT.md` (Phase 2): ranked GAP/EX list + Selection gate |
| Diagrams prioritized over examples | User's stated priority order | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-07 after Phase 2*
