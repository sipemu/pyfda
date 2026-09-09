---
schema_version: 1
open_count: 16
waived_count: 0
fixed_count: 0
total_count: 16
last_updated: 2026-09-09T06:04:49.508Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 22 | deviation | python/fdars/mcp/server.py |  | No deviations from plan 22-02 | open |  | 2026-08-12T13:12:38.725Z |  |
| 2 | 76 | stub | docs/examples/frechet-density-regression.md |  | No stubs present — all fences produce live outputs | open |  | 2026-09-05T21:47:16.350Z |  |
| 3 | 77 | deviation | docs/analyze/index.md |  | Gallery card visual order + thumbnail display requires human review in Phase 79 | open |  | 2026-09-05T23:03:31.725Z |  |
| 4 | 83 | deviation | scripts/generate_capability_dataset.py |  | Task 3 verify command grep scope broader than intent — align_cluster_fd legitimately in Full API Reference; provenance section correctly clean (section-scoped check confirms) | open |  | 2026-09-07T19:26:35.119Z |  |
| 5 | 85 | stub | paper/paper.tex |  | Abstract placeholder — expanded in Phase 88 | open |  | 2026-09-08T20:49:43.659Z |  |
| 6 | 85 | stub | paper/refs.bib |  | Stub placeholder entry — gen_refs_bib.py regenerates in Phase 86 | open |  | 2026-09-08T20:49:43.791Z |  |
| 7 | 85 | stub | paper/sections/intro.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:44.006Z |  |
| 8 | 85 | stub | paper/sections/design.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:44.288Z |  |
| 9 | 85 | stub | paper/sections/represent.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:44.544Z |  |
| 10 | 85 | stub | paper/sections/capabilities.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:44.800Z |  |
| 11 | 85 | stub | paper/sections/comparison.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:44.967Z |  |
| 12 | 85 | stub | paper/sections/casestudies.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:45.106Z |  |
| 13 | 85 | stub | paper/sections/availability.tex |  | Placeholder section — expanded in later phases | open |  | 2026-09-08T20:49:45.297Z |  |
| 14 | 88 | stub | paper/sections/abstract.tex |  | Abstract stub — one-sentence placeholder; expanded in Phase 88 Plan 03 | open |  | 2026-09-09T06:04:44.850Z |  |
| 15 | 88 | stub | paper/sections/advisor.tex |  | Advisor section stub — title + one sentence; expanded in Phase 88 Plan 04 | open |  | 2026-09-09T06:04:49.388Z |  |
| 16 | 88 | stub | paper/sections/conclusion.tex |  | Conclusion section stub — title + one sentence; expanded in Phase 88 Plan 05 | open |  | 2026-09-09T06:04:49.508Z |  |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "22",
    "file": "python/fdars/mcp/server.py",
    "line": null,
    "description": "No deviations from plan 22-02",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-12T13:12:38.725Z",
    "resolved_at": null
  },
  {
    "id": 2,
    "kind": "stub",
    "phase": "76",
    "file": "docs/examples/frechet-density-regression.md",
    "line": null,
    "description": "No stubs present — all fences produce live outputs",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-05T21:47:16.350Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "deviation",
    "phase": "77",
    "file": "docs/analyze/index.md",
    "line": null,
    "description": "Gallery card visual order + thumbnail display requires human review in Phase 79",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-05T23:03:31.725Z",
    "resolved_at": null
  },
  {
    "id": 4,
    "kind": "deviation",
    "phase": "83",
    "file": "scripts/generate_capability_dataset.py",
    "line": null,
    "description": "Task 3 verify command grep scope broader than intent — align_cluster_fd legitimately in Full API Reference; provenance section correctly clean (section-scoped check confirms)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-07T19:26:35.119Z",
    "resolved_at": null
  },
  {
    "id": 5,
    "kind": "stub",
    "phase": "85",
    "file": "paper/paper.tex",
    "line": null,
    "description": "Abstract placeholder — expanded in Phase 88",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:43.659Z",
    "resolved_at": null
  },
  {
    "id": 6,
    "kind": "stub",
    "phase": "85",
    "file": "paper/refs.bib",
    "line": null,
    "description": "Stub placeholder entry — gen_refs_bib.py regenerates in Phase 86",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:43.791Z",
    "resolved_at": null
  },
  {
    "id": 7,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/intro.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:44.006Z",
    "resolved_at": null
  },
  {
    "id": 8,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/design.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:44.288Z",
    "resolved_at": null
  },
  {
    "id": 9,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/represent.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:44.544Z",
    "resolved_at": null
  },
  {
    "id": 10,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/capabilities.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:44.800Z",
    "resolved_at": null
  },
  {
    "id": 11,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/comparison.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:44.967Z",
    "resolved_at": null
  },
  {
    "id": 12,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/casestudies.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:45.106Z",
    "resolved_at": null
  },
  {
    "id": 13,
    "kind": "stub",
    "phase": "85",
    "file": "paper/sections/availability.tex",
    "line": null,
    "description": "Placeholder section — expanded in later phases",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-08T20:49:45.297Z",
    "resolved_at": null
  },
  {
    "id": 14,
    "kind": "stub",
    "phase": "88",
    "file": "paper/sections/abstract.tex",
    "line": null,
    "description": "Abstract stub — one-sentence placeholder; expanded in Phase 88 Plan 03",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-09T06:04:44.850Z",
    "resolved_at": null
  },
  {
    "id": 15,
    "kind": "stub",
    "phase": "88",
    "file": "paper/sections/advisor.tex",
    "line": null,
    "description": "Advisor section stub — title + one sentence; expanded in Phase 88 Plan 04",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-09T06:04:49.388Z",
    "resolved_at": null
  },
  {
    "id": 16,
    "kind": "stub",
    "phase": "88",
    "file": "paper/sections/conclusion.tex",
    "line": null,
    "description": "Conclusion section stub — title + one sentence; expanded in Phase 88 Plan 05",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-09T06:04:49.508Z",
    "resolved_at": null
  }
]
````
