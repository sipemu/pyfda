---
phase: 80-schema-data-home-primary-guard-tests
plan: 02
subsystem: docs-authoring
tags: [markdown, schema, curation, doi, references, authoring-guide]

requires:
  - phase: 80-01
    provides: python/fdars/_references_map.json — the shipped file this doc describes

provides:
  - docs/authoring/references-schema.md — locked schema spec + author-verification workflow governing all Phase 81 curation

affects: [phase-81-curation, phase-82-mcp-tool, phase-83-docs]

actuals:
  tokens: 7500
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "docs/authoring/ subdirectory for authoring-internal reference pages (not yet in mkdocs nav — wired in Phase 83)"
    - "Pure markdown schema spec: no exec fences, no live code; stable across mkdocs builds"

key-files:
  created:
    - docs/authoring/references-schema.md

key-decisions:
  - "Documented the ACTUAL shipped shape verbatim (5-paper seed, 11 callable_index entries) rather than an idealized shape — curators author against what is live"
  - "srivastava_et_al_2011 has no doi field (arXiv preprint, type=preprint) — documented this as the canonical preprint case in the doi field rules"
  - "curated:false tail convention documented with a _uncurated_batch_YYYY-MM key pattern, ready for Phase 81 use"
  - "docs/authoring/ not added to mkdocs nav this phase (Phase 83 wires the references docs surface per plan spec)"

requirements-completed: [SCHEMA-02]

coverage:
  - id: D4
    description: "docs/authoring/references-schema.md committed: documents locked schema, author-verification bar (personal DOI-landing-page check), curated:false tail, sub-method-keyed attribution, cross_language shape with Matlab confidence:low, and GATE-05 A/B/C enforcement"
    requirement: SCHEMA-02
    verification:
      - kind: manual
        ref: "docs/authoring/references-schema.md"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-09-07
status: complete
---

# Phase 80 Plan 02: Schema, Data Home & Primary Guard Tests Summary

**`docs/authoring/references-schema.md` committed — locked schema spec + author-verification workflow governing Phase 81 curation (SCHEMA-02)**

## Performance

- **Duration:** 2 min
- **Started:** 2026-09-07T09:58:22Z
- **Completed:** 2026-09-07T10:01:13Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `docs/authoring/` subdirectory and wrote `docs/authoring/references-schema.md` (449 lines, pure markdown, no exec fences)
- Schema spec documents the real shipped `_references_map.json` shape verbatim: top-level `papers`/`callable_index` keys, `papers[*]` field table (title/authors/year/doi/url/type/callables/cross_language/notes/curated), `cross_language[*]` sub-shape (package/function/version/url/confidence)
- Author-verification hard bar stated: `curated: true` requires personally opening the DOI landing page and confirming author list, year, and title — a resolving DOI is NOT proof of correct attribution
- Canonical worked example: F&M depth is 2001 (TEST journal, DOI `10.1007/BF02595706`), not 1991 (Ramsay-Dalzell is 1991, DOI `10.1111/j.2517-6161.1991.tb01844.x`)
- SRSF-vs-SRV pitfall documented: use arXiv:1103.3817 for functional-data SRSF alignment, not the TPAMI SRV/shape paper
- `curated:false` tail convention documented with `_uncurated_batch_YYYY-MM` key pattern for Phase 81 use
- GATE-05 A/B/C enforcement documented with run command `pytest tests/test_guard_sync_version_independent.py -v`
- `FDARS_ONLINE_CHECKS=1` skip behaviour described: structural gate runs always; live resolve skips the gate
- 6 common pitfalls documented (F&M year, maturin include, atomic commit rule, SRSF/SRV, callable_index drift, LP&R same-paper BD/MBD)

## Task Commits

1. **Task 1:** `f037062` — docs(80-02): add references-schema.md — schema spec + author-verification workflow (SCHEMA-02)

## Files Created/Modified

- `docs/authoring/references-schema.md` (created) — schema spec for `_references_map.json`; pure markdown authoring guide for Phase 81 curators; not yet wired into mkdocs nav (Phase 83 does that)

## Decisions Made

- Documented the ACTUAL shipped Phase 80 seed (5 papers, 11 callable_index entries) verbatim, not an idealized shape — curators must author against what is live, not a hypothetical
- `srivastava_et_al_2011` used as the canonical preprint example (no `doi` field, `type: "preprint"`) — makes the `doi` field conditionality concrete
- `curated:false` tail convention uses `_uncurated_batch_YYYY-MM` as the key pattern suggestion (flexible, date-stamped for Phase 81 tracking)
- `docs/authoring/` not added to mkdocs.yml nav — per plan spec, Phase 83 wires the references docs surface

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes at trust boundaries. The file is a pure markdown authoring guide — no executable code, no data processing. No threat flags.

## Self-Check: PASSED

- `docs/authoring/references-schema.md` exists: FOUND
- `grep -c "callable_index"` = 15: FOUND
- DOI regex `^10\.\d{4,9}/\S+$` present: FOUND (3 occurrences)
- `frozenset(callable_index.keys())` invariant: FOUND (2 occurrences)
- `curated` present: FOUND (17 occurrences)
- `cross_language` present: FOUND (6 occurrences)
- `confidence` present: FOUND (4 occurrences)
- `FDARS_ONLINE_CHECKS` present: FOUND (2 occurrences)
- F&M-2001-not-1991 example: FOUND (2 occurrences)
- `tests/test_guard_sync_version_independent.py` referenced: FOUND (4 occurrences)
- No exec fences: CONFIRMED (grep count = 0)
- Commit `f037062` exists: FOUND

---
*Phase: 80-schema-data-home-primary-guard-tests*
*Completed: 2026-09-07*
