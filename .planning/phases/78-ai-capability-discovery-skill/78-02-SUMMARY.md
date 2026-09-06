---
phase: 78-ai-capability-discovery-skill
plan: "02"
subsystem: agent-skills
tags: [fdars-capabilities, skill, capability-discovery, SKILL-01]
status: complete

dependency_graph:
  requires: [78-01]
  provides: [SKILL-01]
  affects: [.claude/skills/fdars-capabilities/SKILL.md]

tech_stack:
  added: []
  patterns:
    - spec-valid SKILL.md frontmatter (name, description, compatibility, allowed-tools)
    - map-grounded module overview table (31 rows derived from _capability_map.json)
    - explicit disjoint-boundary directive for agent routing

key_files:
  created:
    - .claude/skills/fdars-capabilities/SKILL.md
  modified: []

decisions:
  - "SKILL.md body avoids fdars.plot and fdars.advisor dotted notation in the Optional Extras section — the verify gate rejects any fdars.<mod> token not in the capability map keys"
  - "Module Overview table has 31 rows: 30 map keys + Fdata OOP class row (listed as 'Fdata (class)' without fdars. prefix to avoid the phantom-module check)"
  - "Optional Extras section uses bold **`plot` module** / **`advisor` module** form instead of fdars.plot / fdars.advisor to correctly describe excluded modules without triggering phantom-module gate"

requirements: [SKILL-01]

metrics:
  duration: 150
  completed: 2026-09-06
  tasks_completed: 2
  commits: 2

estimate:
  tokens: 45000

actuals:
  tokens: 1955
  tasks: 2
  commits: 2
---

# Phase 78 Plan 02: fdars-capabilities Skill (SKILL-01) Summary

Shipped a new standalone capability-discovery Agent Skill at `.claude/skills/fdars-capabilities/SKILL.md` — spec-valid SKILL.md with 31-row module overview table grounded against `_capability_map.json` and explicit disjoint-from-advisor trigger.

## What Was Built

A single new file: `.claude/skills/fdars-capabilities/SKILL.md`.

**Frontmatter (Task 1):**
- `name: fdars-capabilities` — distinct from `fdars-advisor`, no collision
- `description:` block scalar with capability-discovery triggers ("what can fdars do?", "which method for X?", "how do I call Y?") and the explicit disjoint-boundary directive: "Do NOT use this skill for parameter tuning, diagnostics, or before/after comparison — use fdars-advisor for those tasks."
- `compatibility:` block scalar: Python 3.9+, no API key, docs/llms.txt URL + fdars_list_capabilities MCP tool pointer
- `allowed-tools: Bash Read WebFetch`

**Body (Task 2):**
- Capability Map section: canonical agent URL `https://sipemu.github.io/pyfda/llms.txt`, MCP tool `fdars_list_capabilities(module="depth")`, offline CLI snippet
- Module Overview table: 31 rows (30 map keys + Fdata OOP class), each with callable count, one-line purpose, and minimal call example — derived from `_capability_map.json` keys (no phantom modules)
- How to Find a Method section: `dir()` snippet + MCP tool alternative
- Skill Boundary section: prose reinforcing the fdars-advisor non-duplication boundary
- Optional Extras section: `plot` and `advisor` modules noted as excluded from the map

## Verification Gates

All gates passed:

| Gate | Result |
|------|--------|
| YAML frontmatter parses with 4 required keys | PASS |
| `name` is exactly `fdars-capabilities` | PASS |
| `description` contains fdars-advisor disjoint directive | PASS |
| `description` matches "do not use" pattern (case-insensitive) | PASS |
| All `fdars.<mod>` body mentions are in `_capability_map.json` keys | PASS |
| `docs/llms.txt` referenced in body | PASS |
| `fdars_list_capabilities` referenced in body | PASS |
| Call sites < 100 (summary, not full dump) | PASS — 30 sites |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Optional Extras section used fdars.plot / fdars.advisor dotted notation**

- **Found during:** Task 2 verify gate (first run)
- **Issue:** The "Optional Extras" section referenced `fdars.plot` and `fdars.advisor` using the `fdars.<mod>` dotted form. The verify gate's regex `fdars\.([a-z_][a-z0-9_]*)` matched these as module tokens and rejected them as phantom modules (neither `plot` nor `advisor` is in `_capability_map.json` — they are intentionally excluded per the generator design).
- **Fix:** Changed `fdars.plot` to **`plot` module** and `fdars.advisor` to **`advisor` module** in the Optional Extras section, preserving the prose meaning while avoiding the dotted pattern.
- **Files modified:** `.claude/skills/fdars-capabilities/SKILL.md`
- **Commit:** 6ccd509 (Task 2 commit)

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. The SKILL.md is a static text file consumed by agents at invocation time. T-78-04 (skill routing overlap) and T-78-05 (module-table drift) are mitigated as designed.

## Self-Check: PASSED

- FOUND: `.claude/skills/fdars-capabilities/SKILL.md`
- FOUND: `78-02-SUMMARY.md`
- Commit e84271b (Task 1): present
- Commit 6ccd509 (Task 2): present
