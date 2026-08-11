---
phase: 13-agent-skill-surface
plan: "02"
subsystem: agent-skill
tags: [skill, mcp, fdars-advisor, expansion, tdd]
status: complete

dependency_graph:
  requires:
    - 13-01-SUMMARY.md  # tracer wave — all artifacts already built
  provides:
    - .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py  # env-gated advise() step
    - .claude/skills/fdars-advisor/SKILL.md  # full body: Grounded Advice + Grounding Invariant
    - tests/test_skill.py  # 3 expansion tests: name==dir, compatibility, py39 exit-0
  affects:
    - tests/  # no new files; existing test module now fully exercised

tech_stack:
  added: []
  patterns:
    - All Plan 02 work pre-built in Plan 01 scaffold (Wave 1 proactive inclusion)
    - Env-gated advise() block: os.environ.get("ANTHROPIC_API_KEY") gate
    - Structural test for version-guard ordering (guard index < fdars.mcp import index)
    - SKILL.md progressive-disclosure body (Setup / Offline Walkthrough / Grounded Advice / Grounding Invariant)

key_files:
  created: []
  modified:
    - .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py  # already extended in Plan 01
    - .claude/skills/fdars-advisor/SKILL.md  # already completed in Plan 01
    - tests/test_skill.py  # already extended in Plan 01

decisions:
  - "Plan 01 pre-built all Plan 02 deliverables: env-gated advise() step in walkthrough, SKILL.md Grounded Advice + Grounding Invariant sections, and all 3 expansion tests — verified green on first run"
  - "No new commits required for Plan 02 — all work already committed under Plan 01 commits (00d18d5, e91bffe, 3202d58, b811422)"
  - "test_walkthrough_py39_exit0 uses structural assertion (guard index < mcp import index) with re.MULTILINE to avoid false match on comments"
  - "SKILL.md stays under 100 lines (87 lines actual) — detail is in the script, not the body (progressive disclosure)"

metrics:
  duration: "2 minutes"
  completed: "2026-08-10"
  tasks_completed: 3
  commits: 0

estimate:
  tokens: 58000
actuals:
  tokens: 2100
  tasks: 3
  commits: 0
---

# Phase 13 Plan 02: Full Skill Surface Expansion Summary

**One-liner:** All three Plan 02 expansion deliverables (env-gated advise() walkthrough step, complete SKILL.md body with Grounded Advice + Grounding Invariant, and three edge tests) were pre-built in Plan 01 and verified green in 6/6 tests at wave-2 start.

## Tasks Completed

| # | Name | Type | Commit | Files |
|---|------|------|--------|-------|
| 1 | Env-gated advise() grounded-advice step in walkthrough | auto (pre-built P01) | e91bffe | .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py |
| 2 | Complete SKILL.md body — Grounded Advice + Grounding Invariant | auto (pre-built P01) | 3202d58 | .claude/skills/fdars-advisor/SKILL.md |
| 3 | Edge tests — name==dir, compatibility, Python-3.9 exit-0 | auto (pre-built P01) | 00d18d5 / 3202d58 | tests/test_skill.py |

## Verification Results

All plan verifications ran clean at wave-2 start:

- `env -u ANTHROPIC_API_KEY .venv/bin/python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py | grep -F "[offline]"` — matched `Step 4: [offline] ANTHROPIC_API_KEY not set — skipping advise()`
- `pytest tests/test_skill.py::test_walkthrough_script_offline tests/test_skill.py::test_walkthrough_delta_nonempty -x -q` — 2 passed
- SKILL.md body check: `## Grounded Advice`, `## Grounding Invariant`, `fdars_compare_run`, `ANTHROPIC_API_KEY` all present; 87 lines (< 500 limit)
- `pytest tests/test_skill.py -x -q` — **6 passed in 1.96s** (full suite green)

## Task 1 Acceptance Criteria

- [x] Offline run (no key) prints an `[offline]` notice, still prints the delta, and exits 0
- [x] The script calls `build_diagnostics(before_result, "smoothing")` before the advise branch
- [x] The advise() call uses `task="parameter"` and a `domain_context` string
- [x] No file-based key read and no key value printed anywhere in the script
- [x] test_walkthrough_script_offline and test_walkthrough_delta_nonempty still pass

## Task 2 Acceptance Criteria

- [x] Body contains `## Grounded Advice` and `## Grounding Invariant` sections
- [x] Body names `fdars_compare_run` (Phase 12 tool reference) and mentions ANTHROPIC_API_KEY
- [x] Body is under 500 lines (actual: 87 lines)
- [x] Frontmatter still parses with name == fdars-advisor (unchanged from Plan 01)

## Task 3 Acceptance Criteria

- [x] test_skill_md_name_matches_dir, test_skill_md_compatibility, test_walkthrough_py39_exit0 all pass
- [x] test_skill_md_compatibility asserts `3.10` and an install/pip token appear in the compatibility field
- [x] test_walkthrough_py39_exit0 asserts the version-guard index precedes the first `from fdars.mcp` import index
- [x] Full `pytest tests/test_skill.py -x -q` is green (6 tests pass)

## Success Criteria Verification

- [x] The full interpret->recommend->re-run->compare loop is packaged and runnable (SKILL-01, Success Criterion 1)
- [x] The execution environment is documented and the skill runs end-to-end (SKILL-02, Success Criterion 2)
- [x] A dry-run walkthrough produces grounded advice + a before/after comparison against Canadian Weather (Success Criterion 3, offline portion)
- [ ] Manual: With ANTHROPIC_API_KEY set, confirm interpretation/recommendations cite diagnostics values (Success Criterion 3, LLM half — requires human review)

## Deviations from Plan

None — all Plan 02 deliverables were pre-built in Plan 01 as documented in 13-01-SUMMARY.md decisions. The Plan 01 scaffold included the full expansion code rather than stubs, per the Decision: "Plan 02 tests (test_skill_md_name_matches_dir, test_skill_md_compatibility, test_walkthrough_py39_exit0) included in test_skill.py during Plan 01 scaffold so all 6 tests collect from the start."

## Known Stubs

None — the compute path is fully wired. The advise() LLM step is env-gated (not stubbed) with a clear offline notice.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes beyond what the threat model anticipated.

- T-13-02 (Information Disclosure — ANTHROPIC_API_KEY): Mitigated. Key read only via `os.environ.get`; never hardcoded, never printed, never written to a file.
- T-13-04 (LLM fabrication): Mitigated by Phase 11 Pydantic schema (non-empty `evidence` required) + system prompt. Offline delta makes fdars-computed values visible alongside any advice.

## Self-Check: PASSED

- [x] tests/test_skill.py exists and collects 6 tests (all pass)
- [x] .claude/skills/fdars-advisor/SKILL.md exists with `## Grounded Advice` and `## Grounding Invariant` sections and `fdars_compare_run` reference
- [x] .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py exits 0 offline, prints `[offline]` notice and 4-key delta
- [x] SKILL.md line count: 87 (< 500 limit)
- [x] Commits 00d18d5, e91bffe, 3202d58, b811422 all present in git log
