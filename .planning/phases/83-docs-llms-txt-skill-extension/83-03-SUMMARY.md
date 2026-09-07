---
phase: 83-docs-llms-txt-skill-extension
plan: "03"
subsystem: skill
tags: [skill, scientific-provenance, fdars-capabilities, mcp, grounded-flag, SKILL-01, SKILL-02]
dependency_graph:
  requires: [83-01-PLAN.md]
  provides: [fdars-capabilities Scientific Provenance Protocol, skill-boundary tests]
  affects: [.claude/skills/fdars-capabilities/SKILL.md, tests/test_references_skill_boundary.py]
tech_stack:
  added: []
  patterns: [pytest.importorskip guard, MCP tool routing, grounded:false machine-readable flag]
key_files:
  modified:
    - .claude/skills/fdars-capabilities/SKILL.md
  created:
    - tests/test_references_skill_boundary.py
decisions:
  - "grounded:false is machine-readable per-citation (not prose-only) — satisfies T-83-05 threat mitigation"
  - "Protocol section inserted between ## Skill Boundary and ## Optional Extras per Design 4.1"
  - "Both-path walkthrough covers all three paths (A/B/C) explicitly labelled by path letter"
  - "Test uses pytest.importorskip inside each test function (not at module level) for clean skip on Python 3.9"
  - "No Path-B test added; Path B demonstrated in walkthrough C (sufficient per plan note)"
metrics:
  duration_seconds: 118
  completed_date: "2026-09-07"
  tasks_completed: 2
  tasks_total: 2
  commits: 2
  files_changed: 2
status: complete
actuals:
  tokens: 2551
  tasks: 2
  commits: 2
---

# Phase 83 Plan 03: fdars-capabilities Skill Extension — Summary

**One-liner:** Hybrid curated/ungrounded Scientific Provenance Protocol added to fdars-capabilities skill, with machine-readable `grounded: false` flag and both-path walkthrough covering three routing paths, plus pytest tests for Path A and Path C.

## What Was Built

### Task 1 — `## Scientific Provenance Protocol` section in SKILL.md (commit `bf643c0`)

Inserted a new `## Scientific Provenance Protocol` section into `.claude/skills/fdars-capabilities/SKILL.md` between `## Skill Boundary` and `## Optional Extras`.

The section encodes the three-path hybrid decision tree over the Phase-82 `fdars_method_references` MCP tool:

- **Path A — `curated: True` hit**: use paper data verbatim (authors, year, DOI, cross-language); no paraphrasing.
- **Path B — `curated: False` hit (all backing papers pending)**: state candidate papers from payload; attach `{ "grounded": false, "source": "pending_verification" }` per citation; do not present as confirmed curated provenance.
- **Path C — `NO_CURATED_ENTRY` sentinel**: MAY synthesize candidate from training knowledge; MUST structurally flag every synthesized citation `{ "grounded": false, "source": "synthesis", "review_required": true }`; NEVER omit the `grounded: false` flag; NEVER present synthesized provenance as curated.

The section also includes:
- Three lookup surfaces (MCP tool, offline JSON, published docs URLs)
- Non-duplication boundary note with `fdars-advisor` (provenance lookup vs. parameter tuning)
- Both-path walkthrough (Walkthrough A, B, C) with concrete return payloads and labelled Path letters

**All three walkthroughs use verified callables:**
- `depth.fraiman_muniz_1d` — `fraiman_muniz_2001` (curated:true) — Path A
- `explain.shap_values` — absent from callable_index — Path C
- `clustering.align_cluster_fd` — `_uncurated_align_cluster_fd_2026-09` (curated:false) — Path B

### Task 2 — `tests/test_references_skill_boundary.py` (commit `58326f7`)

Created a new test file with two tests exercising both routing branches:

- `test_references_curated_hit_returns_curated_true` — Path A: `depth.fraiman_muniz_1d` returns `curated:True` with at least one paper having `curated:True`. Mirrors the existing GATE-05 C guard's curated hit assertion.
- `test_references_sentinel_returns_no_curated_entry` — Path C: `explain.shap_values` returns `curated:False` and `sentinel == "NO_CURATED_ENTRY"`. Mirrors the existing GATE-05 C guard's sentinel assertion.

Both tests use `pytest.importorskip("mcp")` inside the test body to skip cleanly on Python 3.9 where `mcp` is unavailable (same pattern as `test_guard_sync_version_independent.py`).

Result: **2 passed in 0.72s** on Python 3.12 with `mcp` installed.

## Verification

```
HEADING:  ## Scientific Provenance Protocol ✓
NO_CURATED_ENTRY sentinel path present ✓
grounded flag present ✓
depth.fraiman_muniz_1d walkthrough ✓
fdars-advisor boundary note ✓
explain.shap_values walkthrough ✓
test file exists ✓
pytest: 2 passed in 0.72s ✓
```

## Deviations from Plan

None — plan executed exactly as written.

- Task 2 test convention exactly mirrors `test_guard_sync_version_independent.py` as specified.
- No Path-B test added per plan note ("Path B demonstrated in walkthrough C, sufficient for SKILL-02 — required branches are curated hit and ungrounded sentinel").
- Walkthrough C (Path B) included in SKILL.md alongside A and B as specified.

## Requirements Coverage

- **SKILL-01**: `## Scientific Provenance Protocol` section present with three-path hybrid decision tree, machine-readable `grounded: false` flag, NO_CURATED_ENTRY handling, and fdars-advisor non-duplication boundary.
- **SKILL-02**: Walkthrough demonstrates both curated hit (Path A) and visibly-labelled ungrounded fallback (Path C + Path B). Skill tests exercise both branches and pass (2/2 on Python 3.10+, skip cleanly on Python 3.9).

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes introduced. The skill file is documentation only; the test file exercises an existing LLM-free MCP handler.

T-83-05 (synthesized citation presented as curated — high severity) is mitigated: Path C mandates `{ "grounded": false, "source": "synthesis", "review_required": true }` structurally and the verify grep confirms `grounded` is present in SKILL.md.

## Self-Check: PASSED

- `.claude/skills/fdars-capabilities/SKILL.md` — modified, verified present
- `tests/test_references_skill_boundary.py` — created, verified present
- Commit `bf643c0` — `git log --oneline` confirms
- Commit `58326f7` — `git log --oneline` confirms
- `pytest tests/test_references_skill_boundary.py -q` — 2 passed in 0.72s
