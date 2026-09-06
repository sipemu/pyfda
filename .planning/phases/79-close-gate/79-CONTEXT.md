# Phase 79: Close Gate — Strict Build, SVGO/Determinism, Human Review & Release - Context

**Gathered:** 2026-09-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove the whole v12.0 milestone correct and shippable in one consolidated close,
then prepare (not execute) the release handoff:

- **GATE-01 + DEPTH-03:** whole-site `mkdocs build --strict` green OFFLINE; every
  worked example across the milestone emits `FDARS_FENCE_OK` (this is the single
  offline/method-accuracy sweep for the DEPTH pages).
- **GATE-02:** SVGO idempotence + build-determinism gate green across all
  new/changed SVGs (the 21 Phase-77 thumbnails; no new concept diagrams this
  milestone).
- **GATE-03:** a BLOCKING human diagram/method-accuracy review of the new
  thumbnails (+ the two forwarded visual notes) — approved before close.
- **GATE-04:** advisor/MCP tests incl. guard-sync green after the SKILL-04 tool —
  grounding invariant + MCP LLM-free boundary preserved.
- **Release handoff:** commit the package-version tick to `0.11.0`; the
  irreversible publish (tag push / PyPI) stays HUMAN-GATED — prepared and handed
  off, never executed autonomously.

**In scope:** running the consolidated gates, fixing anything they surface, the
version bump commit, and preparing the release-handoff notes.

**Out of scope:** pushing any git tag, publishing to PyPI, or `git push` to
origin — all human-gated. No `fdars-core` bump beyond the version-string tick.

</domain>

<decisions>
## Implementation Decisions (user-accepted)

### Version tick → 0.11.0 (user-selected)
- Bump the package version to `0.11.0` in ALL three places: `python/fdars/__init__.py`
  (`__version__`, currently STALE at `0.4.0` — a real bug), `pyproject.toml`
  (currently `0.10.0`), and `Cargo.toml` (currently `0.10.0`). Rationale: v12
  shipped importable code (the `fdars_list_capabilities` MCP tool, the
  `fdars-capabilities` skill, the capability generator), and `v0.10.0` is already
  a released tag — a fresh release version is correct.
- The `fdars_list_capabilities` MCP tool reads `fdars.__version__` dynamically
  (fixed in Phase 78), so after the bump it reports `0.11.0`. Re-run the
  capability accuracy + guard-sync tests after the bump to confirm still green
  (the map itself carries no version, so no map drift is expected).

### Publish stays human-gated (non-negotiable, success criterion 5)
- Commit the version tick. Do NOT push any tag, do NOT publish to PyPI, do NOT
  `git push`. Prepare a release-handoff note listing exactly what the user must
  run: push `main` (HEAD is ~79 commits ahead of origin), push the semver publish
  tag `v0.11.0` (fires PyPI), and the milestone marker tag `v12.0`
  (non-publishing). Per [[pyfda-release-versioning]]: PyPI publish fires only on
  `vX.Y.Z` semver tags; milestone `vX.Y` tags are markers.

### GATE-03 blocking human review flow
- Run the AUTOMATED gates first (GATE-01 strict build, GATE-02 SVGO, GATE-04
  guard-sync) and fix anything they surface. THEN pause for the blocking human
  diagram/method-accuracy review: present the 21 new Phase-77 thumbnails plus the
  two forwarded visual-accuracy notes for the reviewer to judge on the built site:
  - **IN-02** (`docs/analyze/functional-time-series.md` thumbnail via Phase-77
    review, actually `functional-time-series.svg`): the dashed forecast segment
    diverges only ~4px from the solid tail — may be indistinct at thumbnail size.
  - **IN-03** (`density-fda.svg`): the LQD-transformed bold curve reads as a
    broader bell rather than a clearly non-bell unconstrained-domain object.
  This is a hard human gate (standing v6.0 hypograph/epigraph lesson); the phase
  cannot close without explicit approval.

### Build discipline
- The whole-site `--strict` build is ~22–35 min with executed fences; run it
  ONCE here (per [[docs-diagram-verify-workflow]]: venv + PYTHONPATH=scripts +
  DOCS_FAST, offline). Keep it offline — no network. If any fence fails, fix the
  page and re-run.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets / Patterns
- **Docs build recipe** ([[docs-diagram-verify-workflow]]): activate `.venv`,
  `PYTHONPATH=scripts DOCS_FAST=1`, `mkdocs build --strict` (the CI command in
  `.github/workflows/docs.yml:86`). rsvg-convert available for SVG smoke-render.
- **SVGO determinism gate** (`.github/workflows/docs.yml`): two-pass transform
  stability (`svgo@3.3.4 pass2 == pass1`) over `docs/assets/diagrams/*.svg`; the
  21 Phase-77 thumbnails already pre-verified idempotent (0/21 unstable) — GATE-02
  re-confirms across all new/changed SVGs.
- **Guard-sync / LLM-free tests** (GATE-04): `tests/test_guard_sync_version_independent.py`
  (extended in Phase 78), `tests/test_mcp_server.py`, `tests/test_advisor_grounding.py`,
  `tests/test_capability_accuracy.py`, `tests/test_mcp_import_smoke.py` — all green after 78.
- **Version files:** `python/fdars/__init__.py:35`, `pyproject.toml:7`, `Cargo.toml:3`.

### Established Patterns
- Milestone close = audit → complete → cleanup (the autonomous lifecycle runs after Phase 79).
- Sequential on `main`, `use_worktrees: false`.

### Integration Points
- Version bump touches 3 files. The whole-site build touches nothing (read-only
  verification) but must pass `--strict`. Handoff note is a new planning artifact.

</code_context>

<specifics>
## Specific Ideas

- GATE-01 is the highest-risk item — it executes EVERY fence across all v12 pages
  (Phases 74–78: 5 regression + 5 analyze pages, 3 flagship examples, the docs
  pages) at once. Any single stale fence fails the build. Budget ~25+ min.
- The 21 thumbnails are already idempotent (pre-verified) — GATE-02 should pass;
  re-confirm across the whole changed-SVG set.
- Forward IN-02/IN-03 explicitly into the GATE-03 human-review packet.
- After Phase 79 completes, the autonomous lifecycle (audit → complete → cleanup)
  runs — but the tag push / PyPI publish remain the user's to execute.

</specifics>

<deferred>
## Deferred Ideas

- Actual `git push`, tag push (`v0.11.0`, `v12.0`), and PyPI publish — HUMAN-GATED
  handoff, never executed autonomously.
- CARD-FUT-01 (Advisor/sklearn galleries), DEPTH-FUT-01 (older thin pages),
  DIAG-FUT-* (dark-mode/theming) — future milestones.

</deferred>
