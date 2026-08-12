---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-08-12T13:12:38.725Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 22 | deviation | python/fdars/mcp/server.py |  | No deviations from plan 22-02 | open |  | 2026-08-12T13:12:38.725Z |  |

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
  }
]
````
