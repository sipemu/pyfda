---
phase: 73-documentation-release
plan: "01"
subsystem: docs
tags: [mkdocs, svg, fdars-fts, markdown-exec, functional-time-series, docs-authoring]

# Dependency graph
requires:
  - phase: 67-functional-time-series-fts
    provides: fdars.fts bindings (ftsm, ftsm_forecast, stationarity_test, dpca, etc.)
provides:
  - docs/analyze/functional-time-series.md with offline FDARS_FENCE_OK fence
  - docs/assets/diagrams/functional-time-series.svg STYLE_SPEC-conformant diagram
  - mkdocs.yml Analyze nav entry for the fts page
  - Proof-of-concept: page+fence+diagram+nav loop works end-to-end
affects: [73-02, 73-03, 73-04, 73-05, 73-06, 73-07]

# Actuals (#2632)
actuals:
  tokens: 14000
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FTS page skeleton: markdown-exec exec='1' source='above' fence + ../assets/diagrams/{slug}.svg ref pattern"
    - "SVG idempotence protocol: npx svgo@3.3.4 --config svgo.config.mjs two-pass diff"
    - "Non-square fixture: n=20 m=30 n_perm=19 seed=42 for stationarity fence"

key-files:
  created:
    - docs/analyze/functional-time-series.md
    - docs/assets/diagrams/functional-time-series.svg
  modified:
    - mkdocs.yml

key-decisions:
  - "FTS diagram viewBox 720x480 (two-row layout: observed/decompose/forecast panels + key functions strip)"
  - "Fence uses exec='1' source='above' (no html='1') — text output only, no matplotlib figure"
  - "Diagram bottom strip lists all key fdars.fts functions for API discoverability"

patterns-established:
  - "Page+fence+diagram+nav loop: confirmed working end-to-end for the tracer plan"
  - "SVGO idempotence: two-pass diff approach confirmed valid for hand-authored SVGs with defs/markers"

requirements-completed: [DOCS-01, DOCS-02]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "docs/analyze/functional-time-series.md page with offline exec fence printing FDARS_FENCE_OK"
    requirement: DOCS-01
    verification:
      - kind: other
        ref: "direct python: .venv/bin/python -c 'from fdars.fts import ftsm, ftsm_forecast, stationarity_test; ... print FDARS_FENCE_OK' → PASS"
        status: pass
      - kind: other
        ref: "DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build — nav wired, no traceback in build output"
        status: pass
    human_judgment: false
  - id: D2
    description: "functional-time-series.svg STYLE_SPEC-conformant and SVGO-idempotent"
    requirement: DOCS-02
    verification:
      - kind: other
        ref: "npx svgo@3.3.4 two-pass idempotence: diff output empty (IDEMPOTENT_OK)"
        status: pass
      - kind: other
        ref: "grep role='img' aria-label aria-labelledby title desc style viewBox 720x480: all present"
        status: pass
    human_judgment: false
  - id: D3
    description: "Analyze nav section in mkdocs.yml includes analyze/functional-time-series.md"
    requirement: DOCS-01
    verification:
      - kind: other
        ref: "grep -q 'functional-time-series.md' mkdocs.yml && echo NAV_WIRED_OK → PASS"
        status: pass
      - kind: other
        ref: "DOCS_FAST build: page absent from 'not in nav' warning list → PASS"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min (includes ~15min waiting for full docs build)
completed: 2026-09-04
status: complete
---

# Phase 73 Plan 01: Functional Time Series Summary

**FTS page + FDARS_FENCE_OK fence + STYLE_SPEC-conformant 720x480 SVG diagram + Analyze nav wiring, proving the end-to-end docs authoring loop for the remaining 6 families**

## Performance

- **Duration:** ~45 min (including ~15 min waiting for the docs build; implementation was ~25 min)
- **Started:** 2026-09-04T13:28:16Z
- **Completed:** 2026-09-04T19:13:40Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created `docs/analyze/functional-time-series.md` with a method-accurate intro, diagram
  reference, FTSM core concept section (math + description), one offline `exec="1"` fence
  importing ftsm/ftsm_forecast/stationarity_test with n=20 m=30 non-square fixture, and a
  complete API Reference section with parameter and key tables for the main dict-returning
  functions
- Authored `docs/assets/diagrams/functional-time-series.svg` — a 720x480 three-panel diagram
  depicting: observed functional curves (indigo, time-indexed) → FTSM decomposition panel
  (orange accent: mean + basis components) → forecast horizon panel (dashed extrapolated
  curves); bottom strip lists key fdars.fts functions; SVGO-idempotent
- Wired the page into mkdocs.yml Analyze nav section; page no longer appears in the
  "not in nav" warning in DOCS_FAST builds

## Task Commits

1. **Task 1: Author functional-time-series.md** - `e6b0709` (feat)
2. **Task 2: Author functional-time-series.svg** - `d5b0c73` (feat)
3. **Task 3: Wire Analyze nav entry** - `6efe67a` (feat)

## Files Created/Modified

- `docs/analyze/functional-time-series.md` — New FTS method page (156 lines): intro, diagram ref, FTSM concept math, exec fence, API reference, references
- `docs/assets/diagrams/functional-time-series.svg` — New concept diagram (129 lines): 720x480, three panels + key functions strip
- `mkdocs.yml` — Added `Functional Time Series: analyze/functional-time-series.md` to Analyze nav section

## Decisions Made

- **viewBox 720x480 (not 300):** Three-row layout needed to fit: observed curves panel, FTSM decomposition panel with mean+basis, forecast panel with extrapolation, AND key-functions strip for API discoverability
- **exec="1" source="above" without html="1":** FTS fence produces text output only (ncomp, forecast shape, p-value), no matplotlib figure — simpler and faster fence
- **Bottom strip in SVG:** Lists all key fdars.fts functions (ftsm, ftsm_forecast, stationarity_test, dpca) for quick discoverability; keeps the diagram self-contained

## Deviations from Plan

None — plan executed exactly as written.

- All three tasks executed in order per plan
- Fence uses exact verbatim template from RESEARCH Section 2 Family A
- SVG mirrors clustering.svg structure with STYLE_SPEC-conformant elements
- Nav entry inserted at top of Analyze section as specified

## Tracer Gate Result

Tracer gate (Task 1 type="tracer") passed:
- HUMAN_VERIFY_MODE=end-of-phase, verify is automated-only (no human-check block)
- Direct Python execution: fence runs cleanly, prints `FDARS_FENCE_OK`
- DOCS_FAST build: page recognized as "in nav" (wired correctly), no fence traceback
- Logged: "Tracer verified end-to-end — expanding" and continued to Tasks 2+3

## Issues Encountered

- The DOCS_FAST build takes 15-25 minutes due to the many advisor/example fences; the
  fence was verified by direct Python execution (`.venv/bin/python`) while the build ran.
  Both direct execution and the full build verified the same result: `FDARS_FENCE_OK` emitted
  with no traceback.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Tracer plan 73-01 complete: page+fence+diagram+nav loop proven end-to-end
- Templates and workflow established for the remaining 6 families (73-02 through 73-07)
- No blockers for expansion plans

---
*Phase: 73-documentation-release*
*Completed: 2026-09-04*
