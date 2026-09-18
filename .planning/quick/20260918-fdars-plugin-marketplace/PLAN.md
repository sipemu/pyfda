---
type: quick
slug: fdars-plugin-marketplace
created: 2026-09-18
---

# Quick: fdars Claude Code plugin marketplace (in-repo)

Package the two existing fdars Agent Skills (`fdars-advisor`, `fdars-capabilities`)
as a Claude Code plugin marketplace hosted in this repo, so users can
`/plugin marketplace add sipemu/pyfda` → `/plugin install fdars@pyfda`.

Constraint: do NOT move/copy/edit the skills at `.claude/skills/` — they are hardcoded
in `tests/test_skill.py`, `tests/test_references_skill_boundary.py`,
`docs/advisor/agent-skill.md`, and the walkthrough script. Reuse in place via a plugin
whose root is `.claude/` (`source: "./.claude"`, skills → `.claude/skills/`).

Files: `.claude-plugin/marketplace.json`, `.claude/.claude-plugin/plugin.json`, README note.
