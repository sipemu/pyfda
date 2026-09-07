---
phase: 80-schema-data-home-primary-guard-tests
plan: 01
subsystem: testing
tags: [json, guard-tests, references, doi, importlib, pytest, fdars]

requires:
  - phase: 79-docs-depth-card-coverage
    provides: existing guard-sync test infrastructure (test_guard_sync_version_independent.py groups 1/2)

provides:
  - python/fdars/_references_map.json — paper-keyed references data home with 5 author-verified seed papers and callable_index
  - GATE-05 A/B/C guard tests in test_guard_sync_version_independent.py (Group 3)
  - Structural DOI/URL gate with FDARS_ONLINE_CHECKS=1 skip pattern

affects: [80-02, phase-81-curation, phase-82-mcp-tool, phase-83-docs, phase-84-site-gate]

actuals:
  tokens: 3252
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Paper-keyed JSON side-file with flat callable_index: papers[key].callables union == callable_index keys (GATE-05 A invariant)"
    - "GATE-04 atomic commit: artifact and guard tests land in the same commit"
    - "FDARS_ONLINE_CHECKS=1 inverts the FDARS_INTEGRATION pattern: structural gate runs always; opt-in live-resolve skips it"

key-files:
  created:
    - python/fdars/_references_map.json
  modified:
    - tests/test_guard_sync_version_independent.py

key-decisions:
  - "All 3 tasks collapsed into ONE atomic commit per GATE-04 lesson — artifact + guard tests cannot be split across CI runs"
  - "depth.fraiman_muniz_2d included: it resolves in _capability_map.json (verified before commit)"
  - "srivastava_et_al_2011 has no doi field (arXiv preprint only); type=preprint; no doi key at all"
  - "eilers_marx_1996 callables limited to smoothing.gcv_smoother + basis.basis_nbasis_cv per task action (pspline_fit_1d not listed despite resolving)"
  - "rss.onlinelibrary.wiley.com added to _ALLOWED_DOMAINS to cover Ramsay-Dalzell URL; rdrr.io covers the F&M cross_language R URL"

patterns-established:
  - "Pattern: _references_map.json ships in wheel without maturin include — python/fdars/ package root ships automatically"
  - "Pattern: GATE-05 primary tests (3.9+, no mcp import) run unconditionally in CI; companion tests (3.10+) deferred to Phase 82"

requirements-completed: [SCHEMA-01, SCHEMA-03, SCHEMA-04]

coverage:
  - id: D1
    description: "_references_map.json committed with 5 author-verified papers (depth/alignment/FPCA/smoothing families), loads via importlib.resources, 11 callable_index entries all cross-file-resolved"
    requirement: SCHEMA-01
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_map_internal_consistency"
        status: pass
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_map_cross_file_resolution"
        status: pass
    human_judgment: false
  - id: D2
    description: "GATE-05 A (internal consistency) and B (cross-file resolution) guard tests appended to test_guard_sync_version_independent.py as Group 3, run on Python 3.9+ with no mcp import"
    requirement: SCHEMA-03
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_map_internal_consistency"
        status: pass
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_map_cross_file_resolution"
        status: pass
    human_judgment: false
  - id: D3
    description: "Structural DOI/URL gate (GATE-05 C): DOI regex + domain allowlist, no live resolve; FDARS_ONLINE_CHECKS=1 skips cleanly"
    requirement: SCHEMA-04
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py::test_references_map_doi_url_structural_gate"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-09-07
status: complete
---

# Phase 80 Plan 01: Schema, Data Home & Primary Guard Tests Summary

**Paper-keyed `_references_map.json` seeded with 5 author-verified papers + GATE-05 A/B/C guard tests in one atomic commit, full suite green (5681 passed)**

## Performance

- **Duration:** 5 min
- **Started:** 2026-09-07T09:50:15Z
- **Completed:** 2026-09-07T09:55:40Z
- **Tasks:** 3 (all collapsed into one atomic commit per GATE-04)
- **Files modified:** 2

## Accomplishments

- Created `python/fdars/_references_map.json` with 5 author-verified seed papers spanning depth (F&M 2001, LP&R 2009), elastic alignment/SRSF (Srivastava et al. 2011 arXiv:1103.3817), FPCA (Ramsay-Dalzell 1991), and B-spline smoothing (Eilers-Marx 1996); 11 callable_index entries all resolving in `_capability_map.json`; one cross_language R entry for F&M depth
- Appended Group 3 (A/B/C) to `tests/test_guard_sync_version_independent.py`: internal consistency (GATE-05 A), cross-file resolution (GATE-05 B), structural DOI/URL gate (GATE-05 C); added `os`, `re`, `urllib.parse` to module imports
- Structural gate runs unconditionally in CI (no network I/O); `FDARS_ONLINE_CHECKS=1` inverts to `pytest.skip` (1 skipped confirmed); full suite: 5681 passed, 10 skipped

## Task Commits

All three tasks landed in a single atomic commit per GATE-04 lesson:

1. **Tasks 1+2+3 (atomic):** `e7814db` — feat(80-01): seed _references_map.json + GATE-05 A/B/C guard tests (SCHEMA-01/03/04)

## Files Created/Modified

- `python/fdars/_references_map.json` (created) — paper-keyed references data home: `papers` (5 entries) + flat `callable_index` (11 entries); ships in wheel without maturin include
- `tests/test_guard_sync_version_independent.py` (modified) — Group 3 A/B/C tests appended; `os`, `re`, `urllib.parse` added to stdlib imports

## Decisions Made

- Collapsed all 3 plan tasks into one atomic git commit (GATE-04 lesson: artifact + guard tests cannot be split; CI would fail between commits if the JSON existed without tests or vice versa)
- `depth.fraiman_muniz_2d` included in F&M callables — resolves in `_capability_map.json` (verified before write)
- `srivastava_et_al_2011` has no `doi` field by design (arXiv preprint; no journal DOI available); type is `"preprint"`
- `eilers_marx_1996` callables: `smoothing.gcv_smoother` + `basis.basis_nbasis_cv` only (per task action spec; `basis.pspline_fit_1d` was verified to resolve but not listed)
- `_ALLOWED_DOMAINS` includes `rss.onlinelibrary.wiley.com` (Ramsay-Dalzell URL) and `rdrr.io` (F&M cross_language R URL) — both were in the research allowlist

## Deviations from Plan

None — plan executed exactly as written. The GATE-04 atomic-commit constraint was honored by design (all 3 tasks committed together).

## Issues Encountered

None.

## Next Phase Readiness

- `_references_map.json` is live and loadable via importlib.resources; all GATE-05 guards are green
- Phase 80-02 (schema documentation `docs/authoring/references-schema.md`) is unblocked
- Phase 81 (broad curation) can begin adding papers; the `callable_index` consistency invariant is enforced by GATE-05 A from day one
- Phase 82 (MCP tool handler) can load `_references_map.json` using the same `resources.files("fdars") / "_references_map.json"` pattern documented in 80-RESEARCH.md

## Self-Check: PASSED

- `python/fdars/_references_map.json` exists: FOUND
- `tests/test_guard_sync_version_independent.py` updated: FOUND (3 new test functions)
- Commit `e7814db` exists: FOUND
- Full suite: 5681 passed, 10 skipped, 0 failures

---
*Phase: 80-schema-data-home-primary-guard-tests*
*Completed: 2026-09-07*
