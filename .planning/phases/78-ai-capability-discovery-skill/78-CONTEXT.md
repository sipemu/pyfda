# Phase 78: AI Capability-Discovery Skill - Context

**Gathered:** 2026-09-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Give AI agents a way to discover the whole `fdars` capability surface, across
three non-duplicating surfaces, all fed from ONE generated source of truth:

- **SKILL-01** — a new standalone capability-discovery Agent Skill
  (`.claude/skills/fdars-capabilities/`) with a spec-valid `SKILL.md` mapping
  every public fdars submodule: what each method does, when to reach for it, and
  how to call it (signature + minimal usage).
- **SKILL-02** — an automated test/harness verifying the capability map against
  the live package (every documented method exists + is importable; no
  stale/renamed entries).
- **SKILL-03** — an LLM-oriented docs page (llms.txt-style whole-library API
  digest) authored/generated and wired into the site.
- **SKILL-04** — an MCP capability tool (`fdars_list_capabilities`) added to the
  existing server, returning the capability surface, provably LLM-free, with the
  guard/tests updated to cover it (feeds GATE-04 at Phase 79).

**In scope:** the capability generator, the new skill dir + SKILL.md, the
llms.txt page + nav wiring, the new MCP tool, and the tests (SKILL-02 accuracy
harness + extended guard-sync).

**Out of scope:** any change to the existing `fdars-advisor` skill's advisor
loop or its MCP tools' behavior; new `fdars-core` bindings; the consolidated
close gate (Phase 79 runs GATE-04 guard-sync-green + the whole-site build). No
`fdars-core` bump.

</domain>

<decisions>
## Implementation Decisions (user-accepted "Accept all")

### Single generator = one source of truth
- A generator script introspects the LIVE `fdars` package (public submodules +
  their public callables, signatures via `inspect.signature`, one-line purpose
  from docstrings) and emits ONE capability dataset. That dataset feeds all
  three surfaces: the skill `SKILL.md` capability map, the `docs/llms.txt` page,
  and the MCP `fdars_list_capabilities` tool. This makes the surfaces impossible
  to drift apart and makes SKILL-02 trivial (regenerate → assert no diff +
  everything importable).
- Where a curated one-liner ("what it does / when to use") is needed beyond what
  docstrings give, keep that curation in a data file the generator merges in —
  so re-generation never clobbers hand-written guidance, and the accuracy test
  still catches a method that was renamed/removed.

### New, distinct skill
- Ship a NEW standalone skill `fdars-capabilities` (name TBD by research/planner
  — must be spec-valid and not collide with `fdars-advisor`). Its trigger is
  **capability discovery** ("what can fdars do?", "which method for X?", "how do
  I call Y?") — explicitly disjoint from `fdars-advisor`'s tune/diagnose/compare
  loop. The SKILL.md description must make the boundary clear so an agent picks
  the right skill (non-duplication is a hard constraint / GATE-04 concern).

### llms.txt page
- Generate `docs/llms.txt` (the standard agent-readable root path) as the
  whole-library API digest, AND wire an in-nav digest page so humans and
  site-search reach it too. Follow the llms.txt convention (concise,
  machine-friendly, links into the method docs).

### MCP tool (LLM-free)
- Add ONE `@mcp.tool()` `fdars_list_capabilities` to `python/fdars/mcp/server.py`
  returning the static generated capability surface (optional `module` filter
  arg). It is provably LLM-free: it returns pre-generated/introspected static
  data — NO model call, no new LLM logic in the compute boundary.
- Extend the guard-sync test(s) (`tests/test_guard_sync_version_independent.py`
  pattern) so the new tool's surface stays literal-synced with the generator,
  keeping the grounding-invariant / LLM-free boundary provable (GATE-04). Follow
  the existing "hard-coded frozenset mirror + regenerate-to-check" discipline;
  respect the Python 3.9 constraint (guard test must not import `mcp` at module
  level).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets / Patterns to follow
- **Existing skill** (do NOT modify its loop): `.claude/skills/fdars-advisor/SKILL.md`
  — the spec-valid SKILL.md format (frontmatter: name, description, compatibility)
  to mirror for the new skill.
- **MCP server:** `python/fdars/mcp/server.py` registers tools via `@mcp.tool()`
  (existing: `fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`,
  `fdars_compare_methods`, `fdars_build_pipeline_report`, `fdars_auto_tune`).
  Add the new tool here alongside them. Supporting modules in `python/fdars/mcp/`
  (`_registry.py`, `_runner.py`, etc.).
- **Guard-sync test:** `tests/test_guard_sync_version_independent.py` — the
  hard-coded-frozenset-mirror + version-independent pattern (COMPAT-03; must run
  on Py3.9 without importing `mcp`). Related: `tests/test_mcp_server.py`,
  `tests/test_mcp_import_smoke.py`, `tests/test_advisor_grounding.py`.
- **Package surface:** `python/fdars/__init__.py` dynamically registers native
  submodules; `fdars.<module>.<fn>` is the call form. The generator introspects
  this live surface.

### Established Patterns
- Pytest under `tests/`; Python 3.9–3.14 compatibility (guard tests must not hard-depend on `mcp`).
- Docs pages live under `docs/` and are wired via `mkdocs.yml` nav.

### Integration Points
- New skill dir: `.claude/skills/fdars-capabilities/`.
- New MCP tool: `python/fdars/mcp/server.py`.
- llms.txt: `docs/llms.txt` + a nav page in `mkdocs.yml`.
- Generator: a script (likely under `scripts/` or `python/fdars/`) + its output
  artifacts. Runs on `main`, `use_worktrees: false` (standing v12.0).

</code_context>

<specifics>
## Specific Ideas

- The generator is the tracer: prove introspect → emit dataset → SKILL.md +
  llms.txt + MCP tool all consume it → SKILL-02 accuracy test green, on ONE
  slice first, then expand to the whole surface.
- SKILL-04's guard-sync extension is the highest-risk item (GATE-04) — get the
  LLM-free boundary + Py3.9 guard discipline right.
- If a docs fence or the llms.txt digest embeds runnable examples, they must
  still emit `FDARS_FENCE_OK` and pass the Phase 79 whole-site build.

</specifics>

<deferred>
## Deferred Ideas

- Any change to the advisor loop / advisor MCP tool behavior (out of scope).
- New `fdars-core` bindings / crate bump (out of scope this milestone).
- The consolidated close gate — whole-site `--strict`, SVGO/determinism,
  human diagram review, GATE-04 guard-sync-green confirmation → Phase 79.

</deferred>
