---
phase: 83-docs-llms-txt-skill-extension
plan: "02"
subsystem: docs
tags: [mkdocs, nav, references, validator, stdlib, offline]

requires:
  - phase: 83-01
    provides: docs/references.md produced by the --references emitter

provides:
  - mkdocs.yml nav entry wiring docs/references.md under the AI/capability section
  - scripts/check_references_render.py fast offline validity checker (stdlib-only)

affects: [phase-84-close-gate, mkdocs-build-strict]

actuals:
  tokens: 1553
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Fast offline validity check script (stdlib-only: pathlib, re, sys) as a Phase-N gate before the full 25-min strict build"

key-files:
  created:
    - scripts/check_references_render.py
  modified:
    - mkdocs.yml

key-decisions:
  - "Nav entry inserted at two-space indent (flat top-level list entry) directly after AI Capability Map: ai-capability-map.md, matching surrounding indentation exactly (DOCS-03)"
  - "Fast checker is stdlib-only — no fdars import, no mkdocs dependency — so it runs in any Python 3.9+ env without a compiled extension"
  - "Full mkdocs build --strict (~25 min) explicitly deferred to Phase 84 per standing decision; Phase 83 gate is the targeted 4-check script only"
  - "Checker validates 4 invariants: file exists, code fences balanced, nav placement correct, internal .md links resolve under docs/"

patterns-established:
  - "Targeted fast validity checker pattern: create a stdlib-only script for each generated docs page to confirm correctness before the costly full strict build"

requirements-completed: [DOCS-03]

coverage:
  - id: D1
    description: "mkdocs.yml nav entry 'Scientific References: references.md' directly after AI Capability Map entry"
    requirement: DOCS-03
    verification:
      - kind: other
        ref: "grep -A1 'AI Capability Map: ai-capability-map.md' mkdocs.yml | grep 'Scientific References: references.md'"
        status: pass
    human_judgment: false
  - id: D2
    description: "scripts/check_references_render.py prints RENDER_VALIDITY_OK (4 checks pass)"
    requirement: DOCS-03
    verification:
      - kind: other
        ref: "python scripts/check_references_render.py => RENDER_VALIDITY_OK"
        status: pass
    human_judgment: false

duration: 3min
completed: "2026-09-07"
status: complete
---

# Phase 83 Plan 02: Docs, llms.txt & Skill Extension — Nav Wiring Summary

**mkdocs.yml nav-wired `references.md` under AI/capability section and a stdlib-only 4-check fast validator confirms nav placement, balanced fences, and internal link resolution without the 25-min full strict build**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-09-07T19:32:35Z
- **Completed:** 2026-09-07T19:35:30Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Inserted `- Scientific References: references.md` in `mkdocs.yml` nav directly after `- AI Capability Map: ai-capability-map.md` (line 169→170), two-space flat-list indentation matching the surrounding entries (DOCS-03)
- Created `scripts/check_references_render.py` — a stdlib-only fast validator (pathlib, re, sys; no fdars import) that checks: (1) `docs/references.md` exists, (2) code fences balanced, (3) nav placement correct in `mkdocs.yml`, (4) all relative `.md` links under `docs/` resolve — exits 0 with `RENDER_VALIDITY_OK`

## Task Commits

1. **Task 1: Insert the Scientific References nav entry in mkdocs.yml** - `2569a2c` (chore)
2. **Task 2: Add scripts/check_references_render.py and run the fast validity check** - `cbfd1f2` (feat)

## Files Created/Modified

- `mkdocs.yml` — +1 line: `  - Scientific References: references.md` between AI Capability Map and scikit-learn API entries
- `scripts/check_references_render.py` — new stdlib-only 4-check fast validity script (159 lines)

## Decisions Made

- Nav entry placed at two-space indent (flat top-level list entry) to match surrounding entries exactly — not nested under a sub-section.
- Fast checker is stdlib-only (`pathlib`, `re`, `sys`) with no `fdars` import so it runs in any Python 3.9+ environment without a compiled extension (mirrors the offline emit pattern).
- The full `mkdocs build --strict` (~25 min with executed fences) remains deferred to Phase 84 per standing decision. The 4-check fast script is the sufficient Phase-83 gate.
- Checker validates the nav sequence by searching for `AI Capability Map: ai-capability-map.md` and asserting the immediately-following line contains `Scientific References: references.md` — robust to surrounding nav changes.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. `docs/references.md` existed as expected (produced by Plan 83-01). All 4 validity checks passed on first run.

## Known Stubs

None. The nav entry resolves to a real file (`docs/references.md`) that was fully produced by Plan 83-01.

## Threat Surface Scan

No new network endpoints, auth paths, or trust boundary changes. The nav edit is a read-only mkdocs configuration change; the checker script is a read-only local file validator. T-83-04 (broken nav/link entry) is now mitigated by both the nav edit (Task 1 precondition checked) and the checker (Task 2 asserts the file exists and links resolve).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- DOCS-03 satisfied: `docs/references.md` is nav-wired and the fast checker confirms valid nav + internal links.
- Phase 84 can now run the full `mkdocs build --strict` as its close gate (the nav entry and page are both present and valid).
- The `scripts/check_references_render.py` script is reusable for regression checks after any future nav edits.

---

## Self-Check: PASSED

- `mkdocs.yml` nav entry present: FOUND
- `docs/references.md` file: FOUND
- `scripts/check_references_render.py`: FOUND
- Commit `2569a2c`: FOUND (`chore(83-02): wire Scientific References nav entry in mkdocs.yml`)
- Commit `cbfd1f2`: FOUND (`feat(83-02): add fast render/nav-validity checker for references.md`)
- `RENDER_VALIDITY_OK` confirmed on final run

---
*Phase: 83-docs-llms-txt-skill-extension*
*Completed: 2026-09-07*
