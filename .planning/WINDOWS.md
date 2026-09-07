---
schema_version: 1
open_count: 4
waived_count: 0
fixed_count: 0
total_count: 4
last_updated: 2026-09-07T19:26:35.119Z
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
  }
]
````
