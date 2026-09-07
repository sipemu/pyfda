---
phase: 83-docs-llms-txt-skill-extension
reviewed: 2026-09-07T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - scripts/generate_capability_dataset.py
  - docs/references.md
  - docs/llms.txt
  - .claude/skills/fdars-capabilities/SKILL.md
  - tests/test_references_skill_boundary.py
  - scripts/check_references_render.py
  - mkdocs.yml
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 83: Code Review Report (Re-review — Iteration 2)

**Reviewed:** 2026-09-07T00:00:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** clean

## Summary

Re-review of Phase 83 following application of all three WR fixes (WR-01, WR-02, WR-03)
documented in `83-REVIEW-FIX.md` (iteration 1). All prior findings are resolved. No new
issues found.

### Verification evidence

**WR-01 — Coverage wording (no conflation of 409 vs 437):** Confirmed resolved.

- `docs/llms.txt` header line 3: "30 public submodules, 409 public callables" — counts
  public module callables only (`_Fdata` excluded from `public_modules`), correctly labelled.
- `docs/llms.txt` provenance section line 548: "Coverage: 28 of 437 callables
  (including 28 Fdata class methods) have curated primary-paper entries." — denominator
  is 437 with its composition explicitly stated; no ambiguity with the 409 figure.
- Closing blockquote: "409 of 437 total callables are not yet curated and are absent from
  this section." — the "of 437 total" phrase anchors the uncurated fraction unambiguously.
- `docs/references.md`: "**28/437 callables**" and "**28 of 437 public callables**" — consistent.
- No hardcoded 437 or 409 literals appear in `scripts/generate_capability_dataset.py`
  (`grep -n "437\|409" ...` produces no output). Both figures are derived at runtime:
  `n_callables` from `sum(len(data[m]) for m in public_modules)`, denominator from
  `_coverage_counts()` which sums all values including `_Fdata`.
- Regeneration is deterministic: `PYTHONPATH= .venv/bin/python scripts/generate_capability_dataset.py --references`
  then `git diff --stat` shows only `.planning/state.json` changed — zero doc drift.
- `SKILL.md` line 78 comment reconciled to "409 public module callables + 28 Fdata class methods = 437 total".

**WR-02 — Path B test exists and is substantive:** Confirmed resolved.

- `tests/test_references_skill_boundary.py` contains
  `test_references_curated_false_hit_returns_path_b` (lines 53-75).
- Assertions: `curated is False`, `sentinel != "NO_CURATED_ENTRY"`, `"papers" in result`.
  These are three independent, non-tautological assertions covering exactly the Path B contract.
- Module docstring at lines 1-24 accurately lists all three paths (A/B/C).
- Test is gated with `pytest.importorskip("mcp")` consistent with the other two tests.
- Live run: `pytest tests/test_references_skill_boundary.py -v` — **3/3 passed** in 1.31s
  (Python 3.14.7, mcp available).

**WR-03 — `check_references_render.py` asserts `_uncurated` absence:** Confirmed resolved.

- `check_no_sentinel_leakage()` (lines 148-171) reads both `docs/references.md` and
  `docs/llms.txt`, counts occurrences of `"_uncurated"` in each, and calls `sys.exit(1)`
  with a descriptive error if any are found. The assertion is real and non-vacuous.
- `main()` calls it as check [5] after the existing four checks (lines 180-184).
- Live run: `scripts/check_references_render.py` — **RENDER_VALIDITY_OK** (5/5 checks pass).
- `grep -c "_uncurated" docs/references.md docs/llms.txt` — `0` / `0`.

**Milestone-gating honesty properties verified intact:**

- Offline operation: `emit_references()` reads committed JSON, no live fdars import.
- Derived denominator: no hardcoded 437/409 in emitter; both computed from JSON at emit time.
- Sentinel filtering: `_uncurated*` keys skipped in `_emit_references_page` (line 576) and
  `_provenance_section_lines` (curated_paper_keys frozenset excludes them).
- Skill never presents synthesized as curated: Path B and Path C walkthroughs in SKILL.md
  both include explicit `grounded: false` structural flags with correct prose guidance.

All reviewed files meet quality standards. No issues found.

---

_Reviewed: 2026-09-07T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
_Iteration: 2 (re-review after WR-01/WR-02/WR-03 fixes)_
