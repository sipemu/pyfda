---
phase: 13
slug: agent-skill-surface
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-10
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (already in `.venv`) |
| **Config file** | `pyproject.toml` (no pytest section; defaults) |
| **Quick run command** | `pytest tests/test_skill.py -x -q` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds (skill tests <10s; walkthrough offline <5s) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_skill.py -x -q`
- **After every plan wave:** Run `pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

> Task IDs are provisional (planner assigns final IDs). This maps each success criterion / requirement to an observable, automated check derived from RESEARCH.md §Validation Architecture.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-00 | 01 | 0 | SKILL-01/02 | — | N/A | scaffold | `pytest tests/test_skill.py -q` (stubs collect) | ❌ W0 | ⬜ pending |
| 13-01-01 | 01 | 1 | SKILL-01 | — | SKILL.md parses; frontmatter has required `name` + `description` | unit | `pytest tests/test_skill.py::test_skill_md_frontmatter -x` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | SKILL-01 | — | `name:` frontmatter equals skill directory name (`fdars-advisor`) | unit | `pytest tests/test_skill.py::test_skill_md_name_matches_dir -x` | ❌ W0 | ⬜ pending |
| 13-01-03 | 01 | 1 | SKILL-01 | T-13 (V5) | Walkthrough script exits 0 offline (no API key, Python ≥3.10) | smoke | `pytest tests/test_skill.py::test_walkthrough_script_offline -x` | ❌ W0 | ⬜ pending |
| 13-01-04 | 01 | 1 | SKILL-01 | — | Script prints a non-empty delta with ≥1 finite numeric key (grounded before/after) | smoke | `pytest tests/test_skill.py::test_walkthrough_delta_nonempty -x` | ❌ W0 | ⬜ pending |
| 13-01-05 | 01 | 1 | SKILL-02 | — | SKILL.md `compatibility` documents Python ≥3.10 + install (git-URL until PyPI extras ship) | unit | `pytest tests/test_skill.py::test_skill_md_compatibility -x` | ❌ W0 | ⬜ pending |
| 13-01-06 | 01 | 1 | SKILL-02 | — | Script exits 0 on Python 3.9 with informative message (not error) — version guard | unit | `pytest tests/test_skill.py::test_walkthrough_py39_exit0 -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_skill.py` — new test module: SKILL.md parse + frontmatter validation (`name`, `description`, `compatibility`), `name`↔dir match, offline script run (exit 0 + non-empty delta), Python 3.9 exit-0 check.
- [ ] Frontmatter parsing in tests via stdlib-friendly `yaml.safe_load` (PyYAML) — confirm/add as a test dep if not already present; otherwise hand-parse the `---` block.
- [ ] No new test framework install needed — pytest already present.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Recorded/dry-run walkthrough transcript shows grounded advice + before/after comparison against a real dataset (Success Criterion 3) | SKILL-01 | The grounded-advice (`advise()`) step needs `ANTHROPIC_API_KEY` and is non-deterministic (LLM output varies) — the offline delta is auto-verified, but the *advice* portion of the transcript is reviewed by hand | Set `ANTHROPIC_API_KEY`, run `python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py`; confirm the printed interpretation/recommendations cite diagnostics values and the before/after delta block is present. Capture transcript into the phase walkthrough artifact. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
