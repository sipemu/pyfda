# Phase 49: Whole-Site Gate & Human Review - Context

**Gathered:** 2026-08-22
**Status:** Ready (final gate phase — orchestrator-driven, not subagent-delegated because the ~20-min build must be backgrounded + polled)

<domain>
## Phase Boundary

The milestone's final gate (GATE-01 + GATE-02):
- **GATE-01:** whole-site `mkdocs build --strict` is green OFFLINE after all v7.0 changes (all executed fences emit `FDARS_FENCE_OK`); SVGO idempotence + build-determinism gate green across every changed/added diagram.
- **GATE-02:** per-section review on the built site + a **BLOCKING human diagram method-accuracy review** before milestone close.

No new features; this phase runs the gate + a small set of carried-forward method-accuracy cleanups, then pauses for the human diagram review.
</domain>

<decisions>
## Implementation Decisions

### Carried-forward method-accuracy cleanups (small, surfaced during v7.0)
- `docs/advisor/mcp.md` "five supported fdars methods" → "six" (server.py `_RUNNABLE_METHODS` = 6; the advisor-mcp diagram already shows 6). FIXED this phase.
- `docs/advisor/aspects.md` — checked: intro states no wrong count; diagram alt-text already "14 aspects". No fix needed.
- `docs/represent/pace-fpca.md` — optional brief note that PACE eigenvalue magnitudes can differ from standard FPCA at small n (Phase 48 flag). Optional — human's call.

### Build discipline (orchestrator-run, per project lessons)
- Run `.venv/bin/mkdocs build --strict` with `PYTHONPATH=scripts` OFFLINE (no `DOCS_FAST` — the real strict build executes all fences full-size). Background it to a log + poll (detaches past the 2-min tool timeout). One build at a time; reap orphaned `mkdocs` between attempts. Worktrees OFF (build uses the main-tree `.venv`).
- Confirm exit 0 + grep the build log/site for `FDARS_FENCE_OK` on the executed pages.

### SVGO idempotence / determinism gate
- Run the pinned `svgo@3.3.4 --config svgo.config.mjs` idempotence check (2nd pass byte-identical) across all `docs/assets/diagrams/*.svg` — especially the ~26 added (20 example + 5 advisor + 1 migrated) and the ~7 fixed this milestone.

### GATE-02 — blocking human diagram review (the pause)
- Present the diagrams + the accumulated judgment-call items to the user; the milestone does NOT close until the human approves. Autonomous mode pauses here (human_needed).
</decisions>

<code_context>
## Existing Code Insights

### Build recipe (memory: docs-diagram-verify-workflow, v6-autonomous-run-state)
- `.venv/bin/mkdocs`, `PYTHONPATH=scripts`, offline. Full strict build ~19–25 min (executed fences run real compute).
- Background + poll; reap orphaned mkdocs; finish all edits before the verifying build (MkDocs snapshots content at build start).

### Accumulated judgment-call items for the human diagram review (GATE-02)
- Phase 43: `elastic-alignment.svg` γ(t) warp inset — is the 56×56px inset prominent enough for amplitude/phase decomposition, or does Panel 3 need a redesign?
- Phase 46 (examples): `ex-canadian-weather.svg` (precipitation as a bottom strip vs its own panel row); `ex-canadian-seasonal.svg` (secondary peak-timing analyses not in main panels); `ex-andrews-wine-clustering.svg` (bootstrap CI section omitted — pure numpy, not fdars); `ex-andrews-wine-qc.svg` (trimmed-mean robustness section omitted). (The layout-fix pass resolved all 12 rendering defects separately.)
- Phase 47: advisor diagrams clean; mcp/aspects follow the shipped code.
- Phase 48: `pace-fpca` PACE-vs-FPCA eigenvalue magnitude difference note (prose, optional).

### Milestone diagram footprint
- 61 audited concept diagrams (all fixed/confirmed in 43–45), 20 new example diagrams (46), 5 new advisor diagrams (47) = 86 concept diagrams total; all method-accurate to the shipped bindings per the per-phase verifications.
</code_context>

<specifics>
## Specific Ideas

- The human review is the last v7.0 lesson from v6.0: automated verify + orchestrator visual review caught a great deal (incl. 12 example-diagram layout defects + banded-alignment overlap), but final method-accuracy sign-off is the human's.
</specifics>

<deferred>
## Deferred Ideas

- Accessibility long-form `<title>`/`<desc>` + `aria-labelledby` (DIAG-FUT-01 / A11Y-01) — future.
- `thumb/` regeneration for any concept diagram whose composition changed materially (DIAG-FUT-02) — future, only if a thumb visibly diverges.
</deferred>
