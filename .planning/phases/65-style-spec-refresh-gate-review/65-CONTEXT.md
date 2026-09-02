# Phase 65: STYLE_SPEC Refresh, Whole-Site Gate & Human Review - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Final gate phase (executed inline by orchestrator due to session-quota constraint)

<domain>
## Phase Boundary
Close the milestone: refresh STYLE_SPEC.md to current reality (SPEC-02), run the SVGO idempotence + determinism gate across all diagrams (GATE-01), get the whole-site `mkdocs build --strict` green offline (GATE-02), and run the blocking human diagram review (GATE-03). No new diagram content beyond STYLE_SPEC.md edits.
</domain>

<decisions>
## Implementation Decisions

### SPEC-02 — STYLE_SPEC.md refresh
- Update stale status/counts written in the 43-diagram era to current reality: 90 concept diagrams in `docs/assets/diagrams/` (156 SVGs total incl. 8 cards + 58 thumbs). Specifically the lines referencing "34 of 43".
- Finalize the accessibility pattern to reflect what the milestone made universal: every concept diagram now carries `role="img"` + `aria-label` (matching the visible title) AND a long-form `<title>` + `<desc>` wired via `aria-labelledby`. Update the "Accessibility Pattern" section accordingly and note gallery thumbs are decorative (`alt=""` + `aria-hidden="true"`).

### GATE-01 — SVGO idempotence + determinism
- Run `npx svgo@3.3.4 --config svgo.config.mjs` idempotence check across all diagrams (svgo(svgo(x)) == svgo(x)). No non-idempotent diagrams.

### GATE-02 — whole-site build
- `DOCS_FAST=1 .venv/bin/mkdocs build --strict` must exit 0 offline (the standing recipe; DOCS_FAST avoids the heavy executed-fence path — this milestone changed only SVGs/pages, no fence code).

### GATE-03 — blocking human diagram review (THE designed pause)
- Present the consolidated human-review checklist (PHASE-65-HUMAN-REVIEW-CARRYFORWARD.md) to the user for visual method-accuracy/design sign-off before the milestone closes. This gate CANNOT be self-approved.

### Constraints
- Docs-only. STYLE_SPEC.md IS edited this phase (the one phase allowed to). No re-edit of the 90 concept diagrams / derivative assets unless the gate surfaces a concrete failure.
</decisions>

<code_context>
## Existing Code Insights
- `.venv/bin/mkdocs` present; recipe `DOCS_FAST=1 .venv/bin/mkdocs build --strict`.
- `svgo.config.mjs` present; svgo via npx (svgo@3.3.4).
- STYLE_SPEC stale lines: ~112, ~146, ~184, ~186 ("34 of 43").
- `.github/workflows/docs.yml` is the CI docs build.
</code_context>

<specifics>
## Specific Ideas
- GATE-03 is a hard stop for human input — the autonomous run terminates here until the user signs off; then milestone audit → complete → cleanup.
</specifics>

<deferred>
## Deferred Ideas
None.
</deferred>
