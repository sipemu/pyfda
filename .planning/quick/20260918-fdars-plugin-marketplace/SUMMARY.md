---
type: quick
slug: fdars-plugin-marketplace
status: complete
created: 2026-09-18
completed: 2026-09-18
---

# Summary: fdars Claude Code plugin marketplace

Added an in-repo Claude Code plugin marketplace exposing the two existing fdars Agent
Skills, with zero duplication and no test/doc breakage.

- **`.claude-plugin/marketplace.json`** — marketplace `pyfda`, one plugin `fdars`,
  `source: "./.claude"`, top-level + plugin descriptions, version 0.13.0.
- **`.claude/.claude-plugin/plugin.json`** — plugin `fdars`, `skills: "./skills"` (scopes
  loading to the existing `.claude/skills/fdars-advisor` + `fdars-capabilities`).
- **README.md** — new "Claude Code plugin (Agent Skills)" section with install commands.
- Validated: `claude plugin validate .` → passed (added marketplace `description` to clear
  the only warning). Existing skills unchanged; tests/docs paths intact.

Install: `/plugin marketplace add sipemu/pyfda` → `/plugin install fdars@pyfda`
→ `/fdars:fdars-capabilities`, `/fdars:fdars-advisor`.

Committed and pushed to origin/main.
