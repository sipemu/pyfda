# Phase 17: Agent Skill Page - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss grey areas auto-answered with recommended defaults per the autonomous-run instruction; grounded in `.claude/skills/fdars-advisor/`).

<domain>
## Phase Boundary

Author a new `docs/advisor/agent-skill.md` page documenting the `fdars-advisor` Anthropic Agent Skill: git-URL install, the full interpret→recommend→re-run→compare walkthrough, and the skill's execution-environment / compatibility requirements. Covers SKILLDOC-01, SKILLDOC-02. `mkdocs.yml` nav wiring is Phase 18.

</domain>

<decisions>
## Implementation Decisions

### Page & Content
- Page path: `docs/advisor/agent-skill.md` (the exact target the earlier pages forward-link to as `agent-skill.md`).
- ILLUSTRATIVE (non-executed) fences only — the skill requires Python 3.10+, the git-URL/`[mcp]`+`[advisor]` install, and (for grounded advice) `ANTHROPIC_API_KEY`; the docs build must NOT depend on any of that. Do NOT add an executed `exec="1"` fence.
- Document git-URL install verbatim from `SKILL.md`: `pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0` (git-URL required until fdars 0.3.0), and the future one-liner `pip install "fdars[mcp,advisor]"`.
- Walk the interpret→recommend→re-run→compare loop mirroring `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py`: load Canadian Weather → store in registry → run `smoothing` (`pspline_fit_gcv`, n_basis=15) "before" → build offline diagnostics → optional API-key-gated `advise()` → compare (re-run n_basis=25 via `compare_run`) → print the observable delta.
- Document execution-environment / compatibility (SKILLDOC-02): Python 3.10+, package-manager access to install fdars + extras, offline walkthrough needs no key, the grounded-advice step needs `ANTHROPIC_API_KEY`. Reflect SKILL.md's `compatibility:` field.
- Mirror the SKILL.md section structure where sensible: Setup, Offline Walkthrough, Grounded Advice (requires ANTHROPIC_API_KEY), Tools Referenced, Grounding Invariant.

### Cross-links & Nav
- Cross-link back to the overview (`index.md`), Python API (`python-api.md`), and MCP server (`mcp.md`) pages. This is the last content page of the advisor section.
- `mkdocs.yml` nav wiring deferred to Phase 18 (NAVDOC-01).

### Claude's Discretion
- Exact prose, section order, and how much of the walkthrough to inline vs. summarize — subject to method-accuracy against SKILL.md + the walkthrough script.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.claude/skills/fdars-advisor/SKILL.md` — manifest with `name: fdars-advisor`, `description`, `compatibility` (Python 3.10+, git-URL install until fdars 0.3.0), and sections Setup / Offline Walkthrough / Grounded Advice / Tools Referenced / Grounding Invariant.
- `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py` — the offline interpret→recommend→re-run→compare walkthrough (Canadian Weather, smoothing pspline_fit_gcv n_basis 15→25) to mirror.
- `docs/advisor/index.md`, `python-api.md`, `mcp.md` — the sibling pages to cross-link and match in tone/structure.

### Established Patterns
- Grounding invariant applies: the walkthrough computes real diagnostics offline; the `advise()` grounded step is API-key-gated and not run in the docs build.
- Install extras: `[advisor]` (anthropic>=0.72.0, pydantic>=2.0), `[mcp]` (mcp>=2.0.0, Python 3.10+).

### Integration Points
- New file `docs/advisor/agent-skill.md`.
- `mkdocs.yml` nav deferred to Phase 18.

</code_context>

<specifics>
## Specific Ideas

- Install commands, compatibility text, and the walkthrough steps MUST match `.claude/skills/fdars-advisor/SKILL.md` and `scripts/fdars_advisor_walkthrough.py` — do not invent install flags or steps.
- The docs build must NOT require Python 3.10+, the `[mcp]`/`[advisor]` extras, or an API key — all fences illustrative.

</specifics>

<deferred>
## Deferred Ideas

- `mkdocs.yml` nav wiring + full-build gate (Phase 18).
- HTTP/SSE transport — out of scope.

</deferred>
