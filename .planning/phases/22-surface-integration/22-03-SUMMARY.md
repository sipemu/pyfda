---
phase: 22-surface-integration
plan: "03"
subsystem: docs
tags: [skill-md, agent-skill, provider-selection, ollama, mcp, fdars-advisor, testing]

requires:
  - phase: 21-advisor-aspects
    provides: "full 12-aspect advisor coverage (depth, outliers, classification, regression, regression_cv, spm)"

provides:
  - "SKILL.md description updated with full 12-aspect advisor coverage"
  - "SKILL.md ## Provider Selection section documenting advise(provider=, model=) + env vars + local Ollama + OpenAI-compatible base_url"
  - "SKILL.md install/compatibility note corrected — no overclaim on PyPI extras today; provider extras noted as fdars 3.0 future release"
  - "SKILL.md ## Tools Referenced refreshed with all 3 MCP tools and python/fdars/advisor/ package reference"
  - "test_skill_md_full_aspect_coverage — asserts depth/outliers/classification/regression/spm appear in SKILL.md"
  - "test_skill_md_provider_selection_section — asserts Provider Selection heading + Ollama + FDARS_ADVISOR_PROVIDER"

affects: [22-surface-integration, skill-documentation, provider-selection]

actuals:
  tokens: 2222
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "YAML block-scalar frontmatter with 2-space continuation indent (Pitfall 5 from research)"
    - "File-scan tests (no network, no credentials) as lightweight doc-compliance locks"

key-files:
  created: []
  modified:
    - .claude/skills/fdars-advisor/SKILL.md
    - tests/test_skill.py

key-decisions:
  - "Four surgical edits only — no rewrite; all existing sections and frontmatter keys preserved"
  - "Provider selection documented in SKILL.md body only; MCP tools stay compute-only (advise() not referenced in any MCP handler)"
  - "Install note references git-URL path and lists provider packages for manual install; PyPI extras noted as fdars 3.0 (not today)"
  - "Walkthrough script left unchanged — multi-aspect demo is Phase 24 docs concern"

patterns-established:
  - "SKILL.md description: enumerate full aspect set so LLM agents know full coverage scope"
  - "Provider Selection section: params table + env-var table + local Ollama example + OpenAI-compatible example"

requirements-completed: [SURF-03, SURF-02]

coverage:
  - id: D1
    description: "SKILL.md description enumerates the full 12-aspect advisor coverage (not just stale 5-aspect list)"
    requirement: SURF-03
    verification:
      - kind: unit
        ref: "tests/test_skill.py::test_skill_md_full_aspect_coverage"
        status: pass
    human_judgment: false
  - id: D2
    description: "SKILL.md ## Provider Selection section documents advise(provider=, model=), env vars, local Ollama path"
    requirement: SURF-03
    verification:
      - kind: unit
        ref: "tests/test_skill.py::test_skill_md_provider_selection_section"
        status: pass
    human_judgment: false
  - id: D3
    description: "SKILL.md install/compatibility note corrected — provider extras ([openai]/[ollama]/[gemini]) noted as fdars 3.0 future, not current PyPI"
    requirement: SURF-03
    verification:
      - kind: unit
        ref: "tests/test_skill.py::test_skill_md_compatibility"
        status: pass
    human_judgment: false
  - id: D4
    description: "SKILL.md ## Tools Referenced refreshed with all 3 MCP tools and python/fdars/advisor/ package"
    requirement: SURF-03
    verification:
      - kind: unit
        ref: "tests/test_skill.py::test_skill_md_full_aspect_coverage"
        status: pass
    human_judgment: false
  - id: D5
    description: "SKILL.md YAML frontmatter stays spec-valid (yaml.safe_load passes; name==fdars-advisor; allowed-tools intact)"
    requirement: SURF-03
    verification:
      - kind: unit
        ref: "tests/test_skill.py::test_skill_md_frontmatter"
        status: pass
      - kind: unit
        ref: "tests/test_skill.py::test_skill_md_name_matches_dir"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-08-12
status: complete
---

# Phase 22 Plan 03: SKILL.md Provider + Full-Coverage Documentation Summary

**Four targeted edits to `.claude/skills/fdars-advisor/SKILL.md` expanding the aspect list from 5 to 12, adding a Provider Selection section with local Ollama + env vars, fixing the PyPI-overclaiming install note, and refreshing the Tools Referenced section; locked by two new file-scan tests.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-08-12T13:02:18Z
- **Completed:** 2026-08-12T13:05:06Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- SKILL.md `description` and `Trigger:` line updated from stale "clustering, smoothing, FPCA, alignment, or basis" to full 12-aspect set including depth, outliers, classification, regression, regression CV, and monitoring/SPM
- New `## Provider Selection` section added documenting `advise(provider=, model=)` as the sole selection entry point, the `FDARS_ADVISOR_PROVIDER`/`FDARS_ADVISOR_MODEL`/`FDARS_ADVISOR_BASE_URL` env vars (verified verbatim against `_factory.py`), a local/key-free Ollama path, and an OpenAI-compatible `base_url` path
- `compatibility` field and `## Setup` block corrected to document the git-URL install path; provider packages listed for manual install; `[openai]`/`[ollama]`/`[gemini]` extras explicitly noted as publishing with fdars 3.0, not available on PyPI today
- `## Tools Referenced` refreshed: lists all 3 MCP tools (`fdars_run_method` with depth, `fdars_build_diagnostics` accepting 12 aspects, `fdars_compare_run`); points to `python/fdars/advisor/` package (not stale `advisor.py` single-file reference)
- Two new tests in `tests/test_skill.py`: `test_skill_md_full_aspect_coverage` and `test_skill_md_provider_selection_section`; all 8 tests pass (6 pre-existing + 2 new)

## Task Commits

1. **Task 1: Four targeted edits to SKILL.md** — `728a441` (docs)
2. **Task 2: Add full-aspect coverage + provider-selection tests** — `22a8ece` (test)

## Files Created/Modified

- `.claude/skills/fdars-advisor/SKILL.md` — four targeted edits (aspect list, provider section, install note, Tools Referenced); YAML frontmatter preserved and spec-valid
- `tests/test_skill.py` — added `test_skill_md_full_aspect_coverage` and `test_skill_md_provider_selection_section`

## Decisions Made

- Four surgical edits rather than a rewrite: all existing sections, `name: fdars-advisor`, `allowed-tools: Bash Read`, and the `## Grounding Invariant` section preserved intact
- SKILL.md documents provider selection in its body; MCP tools remain compute-only with no reference to `advise()` — SURF-02 architectural separation confirmed and locked by 22-02's `test_mcp_does_not_import_advise`
- Walkthrough script (`fdars_advisor_walkthrough.py`) left unchanged per plan instruction — multi-aspect examples are a Phase 24 docs concern
- YAML block-scalar indentation maintained at 2-space continuation (Pitfall 5 from research) to keep `yaml.safe_load` passing

## Deviations from Plan

None — plan executed exactly as written. All four edits made as specified; two tests added matching the spec from research section 5.

## Issues Encountered

None. The YAML frontmatter `description: >` and `compatibility: >` block scalars parsed correctly on the first attempt. All 8 tests passed immediately after changes.

## Threat Mitigations Applied

- **T-22-09 (Information disclosure):** Install note documents key-free Ollama path; `ANTHROPIC_API_KEY` noted as Anthropic-only; no credentials leaked
- **T-22-10 (Repudiation — overclaiming PyPI):** Corrected note states provider extras publish with fdars 3.0, preventing a broken `pip install fdars[openai]` on today's PyPI

## Next Phase Readiness

- SURF-03 fully satisfied: SKILL.md documents full aspect coverage and provider selection
- SURF-02 touchpoint addressed: SKILL.md correctly states `advise(provider=, model=)` is the sole entry point; MCP tools are compute-only
- Phase 22 is now complete across all three plans (22-01 MCP tracer, 22-02 MCP expansion, 22-03 SKILL.md)

## Self-Check: PASSED

- `.claude/skills/fdars-advisor/SKILL.md` exists and was modified: confirmed
- `tests/test_skill.py` exists and was modified: confirmed
- Commit `728a441` exists: confirmed
- Commit `22a8ece` exists: confirmed
- All 8 tests in `tests/test_skill.py` pass: confirmed (8 passed in 2.20s)

---
*Phase: 22-surface-integration*
*Completed: 2026-08-12*
