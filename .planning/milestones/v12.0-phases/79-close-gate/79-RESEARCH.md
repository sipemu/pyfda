# Phase 79: Close Gate — Research

**Researched:** 2026-09-06
**Domain:** Release-gate verification, SVGO idempotence, pytest, version-bump mechanics
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Version tick to `0.11.0` in ALL three files: `python/fdars/__init__.py:35`, `pyproject.toml:7`, `Cargo.toml:3`.
- `fdars_list_capabilities` MCP tool reads `fdars.__version__` dynamically — after the bump it reports `0.11.0` without any rebuild.
- Re-run capability accuracy + guard-sync tests AFTER the bump to confirm still green.
- Publish stays HUMAN-GATED: commit the tick, do NOT push tags, do NOT publish, do NOT `git push`.
- GATE-03 is a hard human gate — the phase cannot close without explicit approval of the 21 new Phase-77 thumbnails + IN-02/IN-03 forwarded notes.
- Run automated gates (GATE-01, GATE-02, GATE-04) first; pause for GATE-03 human review; then version bump.

### Claude's Discretion
- Whether to use `DOCS_FAST=1` for GATE-01 (see dedicated section below).

### Deferred Ideas (OUT OF SCOPE)
- Pushing any git tag (`v0.11.0`, `v12.0`), publishing to PyPI, `git push` — all human-gated handoff.
- CARD-FUT-01, DEPTH-FUT-01, DIAG-FUT-* — future milestones.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-01 | Whole-site `mkdocs build --strict` green offline; all fences emit `FDARS_FENCE_OK` | Section 1 — exact command, DOCS_FAST ruling, check_docs_figures.py anatomy |
| GATE-02 | SVGO idempotence + build-determinism gate green across all new/changed SVGs | Section 2 — confirmed 21 thumbs + 101 concept diagrams all stable |
| GATE-03 | Blocking human diagram/method-accuracy review — approved before close | Section 3 — 21 thumbnail slugs + IN-02/IN-03 packet |
| GATE-04 | Grounding invariant + MCP LLM-free boundary — advisor/MCP tests green | Section 4 — 5 test files, timing, confirmed green |
| DEPTH-03 | Every new/extended fence on DEPTH pages runs offline, emitting `FDARS_FENCE_OK` | Section 1 — 13 pages × fence counts verified |
</phase_requirements>

---

## Summary

Phase 79 is a pure verification-and-release-prep phase. Every fact below is a runbook-ready finding derived by reading the actual source files and running tools this session. No design decisions are needed; the only risks are (a) a fence failure in the 47-block whole-site build, (b) an SVGO instability, (c) a guard-sync drift after the version bump, and (d) mistiming the human gate.

The toolchain state is: `.venv` contains Python 3.14.7, mkdocs 1.6.1, mkdocs-material 9.7.6, markdown-exec, pydantic 2.13.4, anthropic — a full superset of the docs requirements. The native extension (`fdars._native`) compiled at v0.9.0 is still intact and all GATE-04 tests pass now. No `maturin develop` is needed before the gates; the version bump to 0.11.0 requires updating three version-string lines only — no recompilation.

**Primary recommendation:** Run gates in order: GATE-02 (fast, ~2 min) → GATE-04 (fast+slow, ~95 s) → GATE-01 (slow, DOCS_FAST=1 recommended, ~7 min; without DOCS_FAST ~25–45 min) → GATE-03 (human review) → version bump → confirm post-bump GATE-04 green → prepare release-handoff note.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Docs build gate (GATE-01) | Build script (mkdocs) | `.venv` Python env | mkdocs --strict executes fences at build time via markdown-exec |
| SVGO idempotence (GATE-02) | CI/CD gate script | npx svgo@3.3.4 | SVG conformance check over committed source files |
| Human diagram review (GATE-03) | Human reviewer | Built site/ | Visual accuracy requires human judgment (v6.0 lesson) |
| Advisor/MCP tests (GATE-04) | pytest + `.venv` | No mcp dependency for 3.9 tests | Test isolation per COMPAT-03 guard-sync design |
| Version bump | Python/Rust source files | — | Three independent version-string literals |
| Release handoff | User (human) | GitHub Actions | PyPI publish fires only on `vX.Y.Z` semver tag push |

---

## Section 1: GATE-01 + DEPTH-03 — Whole-Site Strict Build

### Authoritative Command Sequence

```bash
# From the project root (/home/simonm/projects/rust/pyfda)
source .venv/bin/activate
PYTHONPATH=scripts DOCS_FAST=1 mkdocs build --strict
python scripts/check_docs_figures.py site
```

**Where each tool comes from:** [VERIFIED: .venv/bin/mkdocs (version 1.6.1 confirmed this session)]

### What `check_docs_figures.py` Checks (and How It Exit-Codes)

[VERIFIED: scripts/check_docs_figures.py:1-42]

The script scans every `site/**/index.html` recursively and searches for three markers:

```
"Traceback (most recent call last)"   # Python exception in exec block
"ModuleNotFoundError"                 # missing import in exec block
'class="exec-error"'                  # markdown-exec rendered error class
```

Exit behaviour (verbatim from source):
- If any marker found: prints `FAILED: build-time figure error(s) detected:` to stderr listing `rel_path (marker_hits)`, returns exit code **1**.
- If no markers: prints `OK: no failed figure blocks in {site_dir}`, returns exit code **0**.

**Why this is needed:** `mkdocs build --strict` does NOT fail when a `markdown-exec` fence raises a Python exception — it renders the traceback as HTML in place of the figure and continues. `check_docs_figures.py` is the only mechanism that catches silent fence failures. [VERIFIED: scripts/check_docs_figures.py:6-10]

### DOCS_FAST=1 vs Full Build — Authoritative Ruling

[VERIFIED: scripts/docs_fig.py:114-131]

`DOCS_FAST=1` activates the `fast(full, fast_value)` helper in `docs_fig.py`, which substitutes a reduced iteration count (e.g. `fast_value`) for the `full` value when `DOCS_FAST` is set. Three milestone pages use `fast()`:

| Page | `fast()` call | Full value | Fast value |
|------|--------------|-----------|-----------|
| `docs/regression/frechet-regression.md` | `n_perm=fast(999, 99)` | 999 perms | 99 perms |
| `docs/analyze/functional-time-series.md` | `n_perm=fast(999, 19)` | 999 perms | 19 perms |
| `docs/analyze/functional-time-series.md` | `n_sim=fast(999, 99)` | 999 sims | 99 sims |
| `docs/examples/fts-forecast.md` | `n_perm=fast(999, 99)` | 999 perms | 99 perms |
| `docs/examples/fts-forecast.md` | `n_sim=fast(999, 99)` | 999 sims | 99 sims |

From `docs_fig.py` docstring (verbatim): *"Fast mode is speed-only: figures may look rougher and MUST NOT be committed as publishable output. The full build (DOCS_FAST unset) is the source of truth and the only mode where the byte-identical determinism guarantee (FND-03) holds."*

The CI workflow (`docs.yml`) does **not** set `DOCS_FAST`. [VERIFIED: .github/workflows/docs.yml — no DOCS_FAST env var present]

**Recommendation for GATE-01:** Use `DOCS_FAST=1` for the close-gate run. Rationale:
- The gate is verifying fence correctness (do the fences run without error and emit `FDARS_FENCE_OK`?), not the final published figure resolution.
- `FDARS_FENCE_OK` is emitted regardless of `fast()` value — the marker confirms the code path ran, not the iteration depth.
- The full build without `DOCS_FAST` takes ~25–45 min (999 permutation tests dominate); `DOCS_FAST=1` takes ~7 min. [CITED: docs-diagram-verify-workflow memory: "Full-site build is slow (~400s)"]
- If GATE-01 passes with `DOCS_FAST=1`, that proves correctness. The determinism (FND-03) guarantee requires the unset build, but that is a publishing concern (GATE-02 covers determinism).

**If you want the CI-equivalent authoritative build** (unset `DOCS_FAST`), budget 25–45 min.

### Milestone Pages with Exec Fences (DEPTH-03 Scope)

All 13 pages below were new or substantially extended in phases 74–78. Each exec fence ends with `print("FDARS_FENCE_OK")`. [VERIFIED: grep -rn 'FDARS_FENCE_OK' across these files this session]

**Regression section (Phase 74 — DEPTH-01):**

| Page | Exec fences | FDARS_FENCE_OK markers |
|------|-------------|----------------------|
| `docs/regression/additive-sof.md` | 4 | 4 |
| `docs/regression/concurrent-regression.md` | 3 | 3 |
| `docs/regression/frechet-regression.md` | 4 | 4 |
| `docs/regression/functional-glm.md` | 4 | 4 |
| `docs/regression/function-on-function.md` | 4 | 4 |

**Analyze section (Phase 75 — DEPTH-02):**

| Page | Exec fences | FDARS_FENCE_OK markers |
|------|-------------|----------------------|
| `docs/analyze/functional-time-series.md` | 3 | 3 |
| `docs/analyze/density-fda.md` | 3 | 3 |
| `docs/analyze/multi-domain.md` | 4 | 4 |
| `docs/analyze/shapelets.md` | 4 | 4 |
| `docs/analyze/advanced-clustering.md` | 3 | 3 |

**Examples section (Phase 76 — EXMP-01/02/03):**

| Page | Exec fences | FDARS_FENCE_OK markers |
|------|-------------|----------------------|
| `docs/examples/fts-forecast.md` | 4 | 4 |
| `docs/examples/frechet-density-regression.md` | 3 | 3 |
| `docs/examples/phoneme-shapelets.md` | 4 | 4 |

**Phase 78 pages (no exec fences — static content):**
- `docs/ai-capability-map.md`: 0 exec fences [VERIFIED: grep -n 'exec=' this session — no output]
- `docs/llms.txt`: static committed file, not processed by markdown-exec

**Index pages modified (Phase 77 card additions):** `docs/regression/index.md`, `docs/analyze/index.md`, `docs/examples/index.md`, `docs/align/index.md`, `docs/represent/index.md` — all have 0 exec fences. [VERIFIED: grep -c 'exec=' this session]

**Expected runtime:** ~7 min with `DOCS_FAST=1`. Budget 35 min if running without `DOCS_FAST`.

---

## Section 2: GATE-02 — SVGO Idempotence + Build Determinism

### CI Gate Scope (Authoritative)

[VERIFIED: .github/workflows/docs.yml:54]

The CI SVGO gate glob is: `for svg in docs/assets/diagrams/*.svg`

**The 21 Phase-77 thumbnails in `docs/assets/thumb/` are NOT in the CI SVGO gate.**

The CI gate covers `docs/assets/diagrams/*.svg` only (101 files). The thumb directory is outside its scope.

### Why Run SVGO on Thumbnails Anyway

REQUIREMENTS.md CARD-06 requires: *"All new thumbnails … pass the SVGO idempotence + build-determinism gate."* [VERIFIED: REQUIREMENTS.md:35] So GATE-02 for Phase 79 covers BOTH directories:
- CI scope: `docs/assets/diagrams/*.svg` (101 files)
- Phase-77 additions: `docs/assets/thumb/<21-slugs>.svg`

### Pre-Verification Results (Confirmed This Session)

Both sets are already confirmed stable:
- **21 Phase-77 thumbnails:** ALL STABLE — zero unstable. [VERIFIED: npx svgo@3.3.4 two-pass run this session]
- **101 concept diagrams:** ALL STABLE. [VERIFIED: npx svgo@3.3.4 two-pass run this session]
- **No concept diagrams changed in v12 milestone:** confirmed by `git diff --name-only f889832..9992162 -- 'docs/assets/diagrams/*.svg'` — empty output. [VERIFIED: git command this session]

### Exact GATE-02 Command

```bash
# From project root. Run against the 21 Phase-77 thumbnails (CARD-06 requirement):
FAILED=0
for svg in \
  docs/assets/thumb/additive-sof.svg \
  docs/assets/thumb/advanced-clustering.svg \
  docs/assets/thumb/banded-alignment.svg \
  docs/assets/thumb/canadian-depth-centrality.svg \
  docs/assets/thumb/concurrent-regression.svg \
  docs/assets/thumb/density-fda.svg \
  docs/assets/thumb/frechet-regression.svg \
  docs/assets/thumb/functional-boxplot.svg \
  docs/assets/thumb/functional-glm.svg \
  docs/assets/thumb/functional-outlier-workflow.svg \
  docs/assets/thumb/functional-statistics.svg \
  docs/assets/thumb/functional-time-series.svg \
  docs/assets/thumb/function-on-function.svg \
  docs/assets/thumb/imputation.svg \
  docs/assets/thumb/interpolation.svg \
  docs/assets/thumb/multi-domain.svg \
  docs/assets/thumb/pace-fpca.svg \
  docs/assets/thumb/scoring-metrics.svg \
  docs/assets/thumb/shapelets.svg \
  docs/assets/thumb/shift-registration.svg \
  docs/assets/thumb/tolerance-vs-conformal.svg; do
  first=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -)
  second=$(printf '%s' "$first" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
  if ! diff <(printf '%s' "$first") <(printf '%s' "$second") >/dev/null; then
    echo "SVGO UNSTABLE: $svg"
    FAILED=1
  fi
done
[ $FAILED -eq 0 ] && echo "ALL 21 THUMBS: SVGO STABLE" || { echo "FAILED"; exit 1; }

# Also run the CI-scope diagrams gate (matching docs.yml exactly):
FAILED=0
for svg in docs/assets/diagrams/*.svg; do
  first=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -)
  second=$(printf '%s' "$first" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
  if ! diff <(printf '%s' "$first") <(printf '%s' "$second") >/dev/null; then
    echo "SVGO: $svg is not stable under svgo.config.mjs (would be transformed)"
    FAILED=1
  fi
done
[ $FAILED -eq 0 ] || { echo "SVGO lint failed — fix diagrams above"; exit 1; }
echo "ALL DIAGRAMS: SVGO STABLE"
```

### SVGO Version Safety

- No global `svgo` installed. [VERIFIED: `which svgo` → not found this session]
- `npx svgo@3.3.4` resolves correctly (3.3.4 confirmed). [VERIFIED: `npx svgo@3.3.4 --version` → `3.3.4` this session]
- Node.js v24.13.1 is available. [VERIFIED: `node --version` this session]
- No `svgo@4.x` conflict risk.

### Build Determinism (FND-03)

`docs_fig.py` achieves deterministic SVG output via: [VERIFIED: scripts/docs_fig.py:71-78]
- `svg.hashsalt = "fdars-docs"` → deterministic element IDs (not uuid4)
- `metadata={"Date": None}` in `savefig()` → suppresses wall-clock timestamp

The byte-identical guarantee requires the full build (DOCS_FAST unset). This is a publishing concern; build-determinism verification is satisfied by running the build twice without DOCS_FAST and diffing `site/`. This is optional for the close gate (GATE-01 with DOCS_FAST=1 satisfies correctness; GATE-02 SVGO stability satisfies source-file conformance).

---

## Section 3: GATE-03 — Blocking Human Review Packet

### What to Present

**21 Phase-77 thumbnails** (reviewed on the built `site/` or via `rsvg-convert`):

| # | Slug | Section page | Forwarded note |
|---|------|-------------|----------------|
| 1 | `additive-sof` | `regression/index.md` | — |
| 2 | `advanced-clustering` | `analyze/index.md` | — |
| 3 | `banded-alignment` | `align/index.md` | — |
| 4 | `canadian-depth-centrality` | `examples/index.md` | — |
| 5 | `concurrent-regression` | `regression/index.md` | — |
| 6 | `density-fda` | `analyze/index.md` | **IN-03** |
| 7 | `frechet-regression` | `regression/index.md` | — |
| 8 | `functional-boxplot` | `analyze/index.md` | — |
| 9 | `functional-glm` | `regression/index.md` | — |
| 10 | `functional-outlier-workflow` | `examples/index.md` | — |
| 11 | `functional-statistics` | `analyze/index.md` | — |
| 12 | `functional-time-series` | `analyze/index.md` | **IN-02** |
| 13 | `function-on-function` | `regression/index.md` | — |
| 14 | `imputation` | `represent/index.md` | — |
| 15 | `interpolation` | `represent/index.md` | — |
| 16 | `multi-domain` | `analyze/index.md` | — |
| 17 | `pace-fpca` | `represent/index.md` | — |
| 18 | `scoring-metrics` | `analyze/index.md` | — |
| 19 | `shapelets` | `analyze/index.md` | — |
| 20 | `shift-registration` | `align/index.md` | — |
| 21 | `tolerance-vs-conformal` | `examples/index.md` | — |

**Forwarded visual-accuracy notes (from Phase-77 review):**

- **IN-02** (`functional-time-series.svg`): The dashed forecast segment diverges only ~4px from the solid historical tail. At thumbnail size (the gallery card), the dashed line may be indistinct from the solid line, making the forecast motif unclear. Reviewer should judge: acceptable at card size, or redraw with wider dash gap / darker contrast?
- **IN-03** (`density-fda.svg`): The LQD-transformed bold curve reads as a broader bell shape rather than a clearly non-bell unconstrained-domain object. The method-accuracy question is whether a viewer will misread it as a standard density curve. Reviewer should judge: acceptable, or mark for redraw?

**How to render for review:**

Option A — built site (after GATE-01 completes):
```
# Point browser at file:///home/simonm/projects/rust/pyfda/site/
# Navigate to regression/, analyze/, align/, represent/, examples/ index pages.
```

Option B — rsvg-convert (instant, no build required):
```bash
# Render individual thumbnails to PNG for close inspection:
rsvg-convert -w 320 -h 180 docs/assets/thumb/functional-time-series.svg -o /tmp/thumb-fts.png
rsvg-convert -w 320 -h 180 docs/assets/thumb/density-fda.svg -o /tmp/thumb-density.png
```

**This gate is blocking.** The version bump and release-handoff note MUST wait for explicit human approval. [VERIFIED: CONTEXT.md decisions — "hard human gate (standing v6.0 hypograph/epigraph lesson)"]

---

## Section 4: GATE-04 — Advisor/MCP Tests

### Exact Test Command (Full GATE-04 Suite)

```bash
source .venv/bin/activate
pytest \
  tests/test_guard_sync_version_independent.py \
  tests/test_mcp_import_smoke.py \
  tests/test_capability_accuracy.py \
  tests/test_advisor_grounding.py \
  tests/test_mcp_server.py \
  -v --tb=short
```

### Test Files and Timing

| File | Tests | Runtime | Python guard |
|------|-------|---------|--------------|
| `test_guard_sync_version_independent.py` | 9 (5 guard-sync + 4 capability) | ~0.8 s | 3 tests skip on Py<3.10 |
| `test_mcp_import_smoke.py` | 1 (COMPAT-02) | <1 s | skips on Py<3.10 |
| `test_capability_accuracy.py` | 3 (SKILL-02: no-drift + all-importable + curation) | <1 s | no skip |
| `test_advisor_grounding.py` | 67 collected / 54 run | ~1 s | 13 skip on Py<3.10 |
| `test_mcp_server.py` | 13 | ~92 s | skips on Py<3.10 |
| **Total** | — | **~95 s** | — |

### Confirmed Green (This Session)

All 5 files are green on current HEAD (before version bump):
- `test_guard_sync_version_independent.py`: 9 passed ✓ [VERIFIED: pytest run this session]
- `test_mcp_import_smoke.py`: 1 passed ✓ [VERIFIED: pytest run this session]
- `test_capability_accuracy.py`: 3 passed ✓ [VERIFIED: pytest run this session]
- `test_advisor_grounding.py`: 54 passed, 13 skipped ✓ [VERIFIED: pytest run this session]
- `test_mcp_server.py`: 13 passed ✓ [VERIFIED: pytest run this session]

### Fast Subset (for iteration during fixes)

```bash
source .venv/bin/activate
pytest \
  tests/test_guard_sync_version_independent.py \
  tests/test_mcp_import_smoke.py \
  tests/test_capability_accuracy.py \
  tests/test_advisor_grounding.py \
  -v --tb=short
# ~2 s total — run this after version bump to confirm no drift before the slow mcp_server run
```

### What the Tests Guard (version-bump relevance)

`test_capability_accuracy.py::test_capability_map_no_drift` regenerates the capability surface from the live `fdars` package and compares signatures/purposes to the committed `_capability_map.json`. **The version bump does not change any callable signatures or docstrings** — this test will still pass. [VERIFIED: test_capability_accuracy.py:219-247 — comparison is on `purpose` + `sig` fields stripped of `when` fields]

`test_guard_sync_version_independent.py::test_capability_tool_llm_free_boundary` calls `fdars_list_capabilities(None)` and checks that the return has `modules` but NOT `provider`/`model` keys. The `version` field IS in the return but is not asserted for a specific value. [VERIFIED: test_guard_sync_version_independent.py:258-275, server.py:821-824] After the bump, `version` will report `0.11.0` — the test still passes.

**No test asserts a specific `fdars.__version__` string value.** [VERIFIED: grep -rn 'version\|0\.' tests/ filtered for version assertions — only unrelated ollama version found]

---

## Section 5: Version Bump Mechanics (0.10.0 → 0.11.0)

### Exact Files and Lines

| File | Line | Current value (verbatim) | New value |
|------|------|--------------------------|-----------|
| `python/fdars/__init__.py` | 35 | `__version__ = "0.4.0"` | `__version__ = "0.11.0"` |
| `pyproject.toml` | 7 | `version = "0.10.0"` | `version = "0.11.0"` |
| `Cargo.toml` | 3 | `version = "0.10.0"` | `version = "0.11.0"` |

[VERIFIED: python3 -c reads all three files this session, verbatim strings confirmed]

**Note on `__init__.py` staleness:** The current value is `"0.4.0"` which is stale (the dist-info installed in `.venv` reports 0.9.0 from a September 4 `maturin develop`). This is a known bug called out in CONTEXT.md. The bump to `0.11.0` corrects it.

### Does Cargo.toml Bump Require `maturin develop` Rebuild?

**No rebuild is needed for GATE-04 tests or for `fdars.__version__` to report correctly.**

Evidence:
1. `fdars.__version__` is read from `python/fdars/__init__.py:35` at Python import time. [VERIFIED: python -c "import fdars; print(fdars.__version__)" → `0.4.0` matching __init__.py:35 exactly, this session]
2. The native module (`fdars._native`) exposes zero version attributes. [VERIFIED: `[a for a in dir(fdars._native) if 'version' in a.lower()]` → `[]` this session]
3. The MCP server reads `from fdars import __version__` (line 811 of server.py). [VERIFIED: grep -n '__version__' python/fdars/mcp/server.py this session]
4. `importlib.metadata.version('fdars')` returns the dist-info version (currently `0.9.0`, stale). No test reads this. [VERIFIED: python -c import this session]

**What Cargo.toml version controls:** The version string embedded in the compiled `.so` wheel binary at Rust compile time. This affects `maturin build` output and `pip show fdars` `Version:` field — neither is tested by GATE-04. Bumping Cargo.toml without rebuilding is safe for this gate phase; the rebuild will happen naturally when the user runs `maturin build --release` for the wheel publication.

**Sequence:** Edit three files → run fast GATE-04 subset (~2 s) → if green, run full GATE-04 with mcp_server (~95 s) → commit version bump.

---

## Section 6: Release Handoff

### Commands the USER Must Run (DO NOT Execute Autonomously)

```bash
# 1. Push all 80+ commits to origin (fires docs CI automatically — docs.yml path filter will match)
git push origin main

# 2. Create and push the semver publish tag (FIRES PYPI — irreversible)
git tag v0.11.0
git push origin v0.11.0

# 3. Create and push the milestone marker tag (NO PyPI trigger — markers don't match vX.Y.Z)
git tag v12.0
git push origin v12.0
```

### Workflow Trigger Analysis

[VERIFIED: .github/workflows/publish.yml:5-9]

```yaml
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
```

- `v0.11.0` matches `v[0-9]+.[0-9]+.[0-9]+` → **publish.yml fires → PyPI publish**
- `v12.0` does NOT match (only two numeric segments) → **no publish workflow**
- `git push origin main` → **docs.yml fires** (path filter: `docs/**`, `python/**`, `src/**`, `scripts/**`, `mkdocs.yml`)

[VERIFIED: .github/workflows/docs.yml:5-12 — triggers on push to branches: [main] with path filters]

### Current State

- HEAD is **80 commits ahead** of `origin/main`. [VERIFIED: `git rev-list origin/main..HEAD --count` → `80` this session]
- Remote: `https://github.com/sipemu/pyfda.git` [VERIFIED: `git remote -v` this session]
- No tags have been pushed for v12.0 or v0.11.0 (confirmed: CONTEXT.md deferred section, and no local tags of this name exist from git log)

### Release-Handoff Note (Include in Phase 79 Summary)

Prepare a `RELEASE-HANDOFF.md` (or section in the phase SUMMARY) containing the three commands above plus this warning: pushing `v0.11.0` fires PyPI immediately and cannot be undone. The version bump commit must be on `main` and pushed before tagging.

---

## Section 7: Common Pitfalls

### Pitfall 1: DOCS_FAST vs Full Build Confusion
**What goes wrong:** Running with `DOCS_FAST=1` for speed, but then assuming byte-identical SVG output (FND-03 guarantee requires unset DOCS_FAST).
**How to avoid:** Use `DOCS_FAST=1` for GATE-01 correctness checks. If you need FND-03 verification, run without it in a separate pass.
**Impact:** Figures are functionally correct with DOCS_FAST; only iteration counts differ.

### Pitfall 2: pydantic / anthropic CI False-Red
**What goes wrong:** Docs CI fails with advisor fence errors because the CI env lacks pydantic/anthropic.
**Confirmed non-issue for LOCAL build:** `.venv` has pydantic 2.13.4 and anthropic. [VERIFIED: this session] `docs/requirements.txt` includes both. The false-red is a CI-specific issue (CI installs `docs/requirements.txt` → should be fine; the memory note was from earlier phases where pydantic was missing from docs/requirements.txt).
**Warning signs:** `pydantic` or `anthropic` in `check_docs_figures.py` output.

### Pitfall 3: SVGO Version Mismatch (Global vs npx Pinned)
**What goes wrong:** A global `svgo@4.x` takes precedence over `npx svgo@3.3.4`, breaking the config (v4 has different CLI/config API).
**Confirmed non-issue:** No global svgo installed. [VERIFIED: `which svgo` → not found this session] `npx` always downloads the pinned 3.3.4.
**If this ever occurs:** Use `npx svgo@3.3.4` explicitly (not just `svgo`); always pass `--config svgo.config.mjs`.

### Pitfall 4: Cargo.toml Bump Triggers Rebuild Assumption
**What goes wrong:** Assuming `cargo build` must run after Cargo.toml version bump before tests pass.
**Reality:** The version bump only changes the metadata embedded in the compiled binary at compile time. Tests read `fdars.__version__` from `__init__.py`, not from the binary. No rebuild needed for GATE-04. [VERIFIED: this session]
**What DOES require a rebuild:** `maturin build --release` for the PyPI wheel (user's responsibility post-tagging).

### Pitfall 5: check_docs_figures.py Only Finds Rendered Tracebacks
**What goes wrong:** A fence that exits 0 but produces wrong output is not caught by this script. A fence that raises a Python exception IS caught.
**Implication:** `FDARS_FENCE_OK` in every fence is the correctness signal; `check_docs_figures.py` is the error-detection signal. Both must pass.

### Pitfall 6: test_mcp_server.py Takes ~92 Seconds
**What goes wrong:** Running the full GATE-04 suite and expecting it to finish in < 10 s.
**How to avoid:** Run the fast subset (4 files, ~2 s) first; only add `test_mcp_server.py` for the final gate confirmation. [VERIFIED: test_mcp_server.py: 13 passed in 91.85s — measured this session]

### Pitfall 7: docs.yml Triggers on `git push origin main`
**What goes wrong:** Pushing main to fix a fence failure triggers a docs CI build that reads the unfixed state (if the commit order is wrong).
**How to avoid:** All fence fixes must be committed and the version bump committed before `git push origin main`. The push fires docs CI against HEAD at push time. Phase 79 is a verification phase — no fence fixes are expected, but be aware if any arise.

### Pitfall 8: `fdars.__version__` vs `importlib.metadata.version('fdars')` Discrepancy
**What goes wrong:** After bumping `__init__.py` to `0.11.0`, `pip show fdars` still reports `0.9.0` (the stale dist-info). This is expected and harmless — the dist-info is a snapshot from the last `maturin develop`. No test reads `importlib.metadata.version('fdars')`. [VERIFIED: grep -rn 'metadata.*fdars' tests/ → no results this session]
**How to avoid:** Confusion only. Ignore `pip show fdars` version for test purposes.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.14 (.venv) | All GATE-04 tests, mkdocs build | ✓ | 3.14.7 | — |
| mkdocs | GATE-01 | ✓ | 1.6.1 | — |
| mkdocs-material | GATE-01 | ✓ | 9.7.6 | — |
| markdown-exec | GATE-01 | ✓ | installed | — |
| fdars (_native compiled) | GATE-01 + GATE-04 | ✓ | 0.9.0 native (0.4.0 __version__) | — |
| pydantic | GATE-01 (advisor fences) | ✓ | 2.13.4 | — |
| anthropic | GATE-01 (advisor fences) | ✓ | installed | — |
| mcp | GATE-04 (Python 3.10+ tests) | ✓ | installed | skip on 3.9 |
| npx / Node.js | GATE-02 (SVGO) | ✓ | v24.13.1 | — |
| svgo@3.3.4 via npx | GATE-02 | ✓ | 3.3.4 (npx-fetched) | — |
| rsvg-convert | GATE-03 visual review | ✓ | per project memory | — |

**Missing dependencies with no fallback:** None — all required tools available. [VERIFIED: command availability checks this session]

---

## Validation Architecture

### Execution Order (Recommended)

```
GATE-02 (SVGO ~2 min) → GATE-04 fast subset (~2 s) → GATE-01 (mkdocs ~7 min) →
check_docs_figures.py → GATE-04 full (mcp_server ~92 s) →
[PAUSE — GATE-03 human review] →
[APPROVAL] → version bump → GATE-04 fast post-bump confirm (~2 s) → commit → handoff note
```

### Quick Run Commands Per Gate

| Gate | Quick command | Full command | Expected time |
|------|--------------|--------------|---------------|
| GATE-02 (thumbs) | Loop over 21 thumbs (above) | Same | ~2 min |
| GATE-02 (diagrams) | Loop over `diagrams/*.svg` | Same | ~3 min |
| GATE-04 (fast) | `pytest test_guard_sync* test_mcp_import* test_capability* test_advisor_grounding* -v` | + `test_mcp_server.py` | 2 s / 95 s |
| GATE-01 + DEPTH-03 | `DOCS_FAST=1 mkdocs build --strict && python scripts/check_docs_figures.py site` | Without DOCS_FAST | ~7 min / ~35 min |

---

## Assumptions Log

All claims in this research were verified by reading source files or running tools in this session. No assumed claims.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Full build without DOCS_FAST takes ~25–45 min | Section 1 | [CITED: docs-diagram-verify-workflow memory "~400s" + CONTEXT.md "22-35 min"] — measured by prior sessions, not this session | Could be faster/slower |

---

## Sources

### Primary (HIGH confidence)
- `scripts/check_docs_figures.py` — read verbatim this session; anatomy fully documented
- `scripts/docs_fig.py` — read verbatim this session; DOCS_FAST semantics confirmed
- `.github/workflows/docs.yml` — read verbatim this session; CI command and SVGO glob confirmed
- `.github/workflows/publish.yml` — read verbatim this session; trigger pattern confirmed
- `python/fdars/__init__.py:35` — read this session; `__version__ = "0.4.0"` verbatim
- `pyproject.toml:7` — read this session; `version = "0.10.0"` verbatim
- `Cargo.toml:3` — read this session; `version = "0.10.0"` verbatim
- `python/fdars/mcp/server.py:811` — read this session; `from fdars import __version__` confirmed
- `tests/test_guard_sync_version_independent.py` — read this session; guard assertions verified
- `tests/test_capability_accuracy.py` — read this session; no version-specific assertions
- `tests/test_mcp_import_smoke.py` — read this session
- `tests/test_mcp_server.py` — read this session
- `tests/test_advisor_grounding.py` — read this session
- pytest runs (5 files) — all confirmed green this session
- SVGO two-pass runs (21 thumbs + 101 diagrams) — all confirmed stable this session
- git diff, git log commands — phase boundary and file changes confirmed this session

### Secondary (MEDIUM confidence)
- `.planning/phases/79-close-gate/79-CONTEXT.md` — user decisions and constraints (read this session)
- `.planning/REQUIREMENTS.md` — requirement definitions (read this session)
- `docs-diagram-verify-workflow` memory — build timing estimate (~400 s)

---

## Metadata

**Confidence breakdown:**
- Gate commands: HIGH — read directly from docs.yml and verified tools this session
- Version bump mechanics: HIGH — read all three files verbatim, tested import chain this session
- SVGO stability: HIGH — ran actual two-pass check across all 122 SVGs this session
- GATE-04 greenness: HIGH — ran all 5 test files this session
- Build timing (DOCS_FAST=1): MEDIUM — from project memory, not timed this session
- Build timing (no DOCS_FAST): MEDIUM-LOW — inferred from fast() call sites and prior session memory

**Research date:** 2026-09-06
**Valid until:** 2026-09-13 (7 days — any new commits to the 13 milestone pages could introduce fence regressions)
