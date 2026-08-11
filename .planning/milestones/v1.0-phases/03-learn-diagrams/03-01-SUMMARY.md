---
phase: 03-learn-diagrams
plan: "01"
subsystem: docs/assets/diagrams
tags: [svg, diagrams, smoothing, DIA-01, GAP-0001, tracer]
dependency_graph:
  requires: []
  provides: [smoothing.svg-corrected, svgo-gate-proven, build-loop-proven]
  affects: [docs/learn/smoothing.md, site/learn/smoothing/]
tech_stack:
  added: []
  patterns: [hand-authored-svg-edit, svgo-idempotence-gate, mkdocs-docs-fast-build]
key_files:
  created: []
  modified:
    - docs/assets/diagrams/smoothing.svg
decisions:
  - "GAP-0001: Ghost underlay redrawn (not removed) — preserves pedagogical before/after contrast; a genuine noisy-path ghost is required so the reader can compare the input noise to the smooth output"
  - "New Panel 3 ghost coordinate string: M0 96 L8 78 L16 106 L24 74 L32 98 L40 66 L48 88 L56 56 L64 82 L72 52 L80 76 L88 50 L96 72 L104 44 L112 66 L120 46 L128 64 L136 48 L144 56 L152 52 L156 64"
  - "SVGO gate confirmed idempotent on smoothing.svg under svgo@3.3.4 + svgo.config.mjs"
  - "mkdocs build invoked as PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build (bare mkdocs not on PATH; venv+PYTHONPATH required)"
metrics:
  duration: "20 minutes"
  completed: "2026-08-08"
  tasks_completed: 3
  commits: 1
estimate:
  tokens: 42000
actuals:
  tokens: 4200
  tasks: 3
  commits: 1
status: complete
requirements: [DIA-01]
---

# Phase 03 Plan 01: Smoothing Diagram Fix (DIA-01) Summary

**One-liner:** Redrawn Panel 3 ghost underlay with genuinely-distinct noisy coordinates, verified with SVGO idempotence gate and mkdocs build.

## What Was Built

The single confirmed accuracy bug in the learn/ section (GAP-0001) was fixed. `smoothing.svg` Panel 3 ("Smooth Curve") previously drew its faint ghost "before" reference by reusing Panel 1's noisy polyline coordinates verbatim from `L8` onward — meaning both the noisy-input panel and the smoothed-output panel showed the exact same wiggle, defeating the before/after contrast.

The fix replaces the Panel 3 ghost path with a genuinely-distinct hand-authored jagged polyline that:
- Spans the same x-range 0–156 with the same 8px x-step
- Has y-values that differ from Panel 1's sequence at every vertex
- Reads as noisy data with ±10–25px vertical jitter around the smooth curve's downward trend
- Preserves all existing faded styling (stroke #0d6efd, stroke-opacity .2, stroke-width 1)

This plan also proves the full author → SVGO gate → mkdocs build verification loop that Plan 02 will use for the remaining five learn/ diagrams.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (tracer) | Redraw Panel 3 ghost underlay (DIA-01) | 7d1ea5d | docs/assets/diagrams/smoothing.svg |
| 2 | SVGO gate + mkdocs build | (gate-only, no file changes) | — |
| 3 | Built-site review (checkpoint:human-verify) | recorded for batched review | — |

## Design Decisions

### GAP-0001: Ghost redrawn, not removed

The audit recommendation (02-AUDIT.md) flagged Panel 3's ghost as a coordinate-reuse bug. The fix redraws it as a genuinely-distinct faded noisy path rather than removing it. Reason: the ghost underlay is the pedagogical "before" reference — without it, Panel 3 would show only the smooth output with no visual contrast to the input noise. The before/after comparison is the diagram's core teaching point.

**New Panel 3 ghost path (line 48):**
```
M0 96 L8 78 L16 106 L24 74 L32 98 L40 66 L48 88 L56 56 L64 82 L72 52 L80 76 L88 50 L96 72 L104 44 L112 66 L120 46 L128 64 L136 48 L144 56 L152 52 L156 64
```

This path roughly follows the smooth curve's downward trend (y≈96 at x=0 to y≈64 at x=156) with ±10–25px jitter that reads as measurement noise — distinct from Panel 1's pattern (which roughly oscillates around a higher-y centre).

### SVGO gate result

Gate confirmed idempotent: `svgo(svgo(smoothing.svg)) == svgo(smoothing.svg)` under `svgo@3.3.4 --config svgo.config.mjs`. The committed file was not reserialised (gate run stdout-only with `--output -`).

### mkdocs build invocation

Per environment notes: bare `mkdocs` is not on PATH; the correct invocation is:
```
PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build
```
This is an expected environment adaptation (venv + PYTHONPATH), not a plan deviation. The plan's illustrative `DOCS_FAST=1 mkdocs build` was substituted accordingly.

## Acceptance Criteria Verification

- [x] `grep -c 'L8 70 L16 100 L24 62 L32 84 L40 54' docs/assets/diagrams/smoothing.svg` returns `1` (Panel 1 signature appears exactly once — not duplicated in Panel 3) **PASS**
- [x] Panel 3 ghost path begins at `M0 ` and reaches x `156` (full panel width) **PASS**
- [x] `grep -c 'viewBox="0 0 720 300"'` returns `1` **PASS**
- [x] `grep -c 'role="img"'` returns `1` **PASS**
- [x] Style block with five CSS classes present **PASS**
- [x] Smooth Bezier curve (stroke-width 3) unchanged **PASS**
- [x] SVGO idempotence gate: SVGO_OK **PASS**
- [x] `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build` exits 0, no ERROR/Traceback **PASS**
- [x] Committed smoothing.svg unchanged by gate run (gate stdout-only) **PASS**

## Human Verification Needed (end-of-phase)

**Task 3** is `type="checkpoint:human-verify"` with `gate="blocking"`. Per `human_verify_mode: "end-of-phase"`, the details are recorded here for batched review at phase end.

**What was built:** The corrected smoothing.svg — Panel 3's faded "before" ghost is now a genuinely-distinct noisy path (no longer a copy of Panel 1's coordinates), and the diagram passes the SVGO gate and builds.

**How to verify:**
Run `DOCS_FAST=1 .venv/bin/mkdocs serve` and open http://127.0.0.1:8000/learn/smoothing/ (or open the built `site/learn/smoothing/index.html`). On the smoothing concept diagram at the top of the page:
1. Confirm the smoothed (right) panel's faint blue "before" reference is visibly a DIFFERENT jagged shape from the noisy (left) panel — not the same wiggle shifted down.
2. Confirm the bold smooth blue curve still passes cleanly through the noise as a legible before/after contrast.
3. Confirm nothing else changed (title, subtitle, method panel, arrows, labels all intact).

**Resume signal:** Type "approved" if the smoothed panel's ghost is genuinely distinct and the diagram reads correctly, or describe what looks wrong.

## Deviations from Plan

### Environment Adaptations (not plan deviations)

**1. [Env] mkdocs invocation via venv + PYTHONPATH**
- **Found during:** Task 2
- **Issue:** `mkdocs` is not on system PATH; plan shows illustrative `DOCS_FAST=1 mkdocs build`
- **Fix:** Used `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build` as specified in critical environment notes
- **Impact:** None — same build result, expected adaptation

**2. [Env] Task 2 has no file commit**
- **Found during:** Task 2
- **Issue:** Task 2 is a pure verification/gate task; no files are modified. The smoothing.svg was committed in Task 1. `site/` is gitignored.
- **Fix:** No commit for Task 2; Task 1's commit carries the only file change. Gate results documented here.
- **Impact:** None — one commit for one file change is correct

## Known Stubs

None. The corrected SVG is complete and all diagram elements are correctly authored.

## Threat Surface Scan

No new security-relevant surface. This plan edited only a single static SVG asset. The SVGO gate ran in stdout-only mode — no network access, no runtime input, no credentials. Threat T-03-01 mitigated: `git diff --stat HEAD~1 HEAD` confirms only the coordinate edit in smoothing.svg (1 insertion, 1 deletion), no SVGO reserialisation.

## Self-Check: PASSED

- smoothing.svg exists: FOUND
- 03-01-SUMMARY.md exists: FOUND
- Task 1 commit 7d1ea5d: FOUND
- Panel 1 signature count == 1: PASS
- viewBox="0 0 720 300" intact: PASS
- role="img" intact: PASS
- SVGO idempotence gate: PASS
