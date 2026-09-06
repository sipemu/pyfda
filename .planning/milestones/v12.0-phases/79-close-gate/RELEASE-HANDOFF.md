# v12.0 Release Handoff — HUMAN-GATED

**Prepared:** 2026-09-06 by the autonomous close gate (Phase 79). These are the
**irreversible, one-way** steps the autonomous run did NOT execute. Run them
yourself when ready.

## State at handoff

- Package version bumped to **0.11.0** in all three files (`python/fdars/__init__.py`,
  `pyproject.toml`, `Cargo.toml`) — committed.
- All close gates green: GATE-01 (whole-site `--strict` offline, 135 pages, 0 fence
  failures), GATE-02 (122/122 SVGs SVGO-idempotent), GATE-03 (human diagram review
  approved), GATE-04 (76 advisor/MCP/guard-sync tests green; MCP LLM-free boundary
  intact; tool now reports `0.11.0`).
- `main` is **~80+ commits ahead of `origin/main`** — all v12.0 work is unpushed.
- Nothing has been pushed, tagged, or published.

## Steps to publish (run in order)

```bash
# 1. Push the branch — fires the docs CI (path filter: docs/**, python/**, src/**, scripts/**)
git push origin main

# 2. Semver PUBLISH tag — matches vX.Y.Z in publish.yml → builds + publishes wheels to PyPI
git tag v0.11.0
git push origin v0.11.0

# 3. Milestone MARKER tag — vX.Y does NOT match the publish pattern (non-publishing marker only)
git tag v12.0
git push origin v12.0
```

## Notes

- **`v0.11.0` (semver) triggers the PyPI wheel publish**; **`v12.0` is a
  milestone marker only** (per project convention / [[pyfda-release-versioning]]:
  publish fires only on `vX.Y.Z` tags).
- Confirm CI is green after `git push origin main` before pushing the `v0.11.0`
  tag, so the wheel build runs against a passing tree.
- If a `CHANGELOG` is desired for the release, add it before tagging (none exists
  in-repo today).
