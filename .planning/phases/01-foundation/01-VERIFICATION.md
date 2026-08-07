---
phase: 01-foundation
verified: 2026-08-07T16:00:00Z
status: human_needed
score: 10/12 must-haves verified
behavior_unverified: 2
overrides_applied: 0
behavior_unverified_items:
  - truth: "Two consecutive full mkdocs builds produce byte-identical SVG output from docs_fig.py exec blocks (FND-03, ROADMAP SC #3)"
    test: "Run mkdocs build twice consecutively (with DOCS_FAST unset) and diff the SVG outputs"
    expected: "No byte-level difference between build 1 and build 2 SVG outputs"
    why_human: "Requires the compiled fdars wheel and a full mkdocs build in a controlled env; the hashsalt code seam is verified present, but end-to-end determinism across two real builds is a runtime invariant that cannot be confirmed from the source alone"
  - truth: "Setting DOCS_FAST=1 causes the docs build to complete materially faster than the full build by lowering expensive iteration counts (FND-06, ROADMAP SC #6)"
    test: "Time a full mkdocs build (DOCS_FAST unset) vs DOCS_FAST=1 mkdocs build on a page with expensive params wrapped in fast()"
    expected: "DOCS_FAST=1 build completes materially faster"
    why_human: "Requires a full mkdocs build with compiled fdars; the fast() helper logic is verified working (returns fast_value when set), but the end-to-end speedup is a runtime property not observable from code alone"
human_verification:
  - test: "Run two consecutive full mkdocs builds and diff SVG outputs for byte-identity (FND-03 runtime proof)"
    expected: "diff between build 1 and build 2 produces no output (zero diff)"
    why_human: "Requires compiled fdars + mkdocs build environment; svg.hashsalt seam verified in source but two-build byte-identity is a runtime invariant"
  - test: "Run DOCS_FAST=1 mkdocs build and compare wall-clock time to full build (FND-06 runtime proof)"
    expected: "DOCS_FAST=1 build completes materially faster on any page using fast() for expensive params"
    why_human: "Requires compiled fdars + mkdocs build environment; the fast() helper is functionally verified but end-to-end timing is a runtime property"
  - test: "Run the CI workflow on a branch (or observe the most recent docs.yml run) to confirm both Gate A (SVGO) and Gate B (doc-test smoke) pass and block before mkdocs build"
    expected: "Gate A passes for all 43 diagrams; Gate B 8/8 fences pass on canadian-weather.md; mkdocs build --strict exits 0"
    why_human: "CI run confirmation requires actual GitHub Actions execution; cannot be observed from the local working tree"
---

# Phase 1: Foundation Verification Report

**Phase Goal:** The tooling and guardrails that every subsequent diagram sweep depends on are in place and verified working.
**Verified:** 2026-08-07
**Status:** human_needed (10/12 truths verified; 2 behavior-dependent truths require full mkdocs build to confirm)
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `docs/assets/diagrams/STYLE_SPEC.md` exists and documents palette, five CSS classes, stroke weights, viewBox width 720, allowed heights {300,480,520}, and copy-paste `<style>` block (FND-01) | VERIFIED | File exists; all five class selectors confirmed (`grep .ttl/.sub/.lab/.sm/.mono`); all seven hex values confirmed; viewBox 720 and heights 300/480/520 confirmed; stroke weights section present; aria-label and svgo@3.3.4 pin confirmed |
| 2 | `svgo.config.mjs` (repo root) exists and disables inlineStyles, minifyStyles, cleanupIds, removeDesc, removeUnknownsAndDefaults, removeViewBox (FND-02, D-03) | VERIFIED | File exists; all six required plugins confirmed false; additionally disables convertPathData, mergePaths, collapseGroups (deviation documented in SUMMARY — needed for idempotence across all 43 diagrams) |
| 3 | The SVGO gate is check-only: it NEVER rewrites committed hand-authored SVGs, only diffs stdout against source (D-02) | VERIFIED | CI step uses `--output -` (stdout) only, no `-o <file>`; idempotence-check approach confirmed in docs.yml (pass 1 vs pass 2); STYLE_SPEC.md documents the check-only contract; deviation from source-diff to idempotence-check preserves D-02 intent exactly |
| 4 | `.github/workflows/docs.yml` runs the SVGO lint gate on all diagrams before mkdocs build, blocking on any diff (D-09, D-10) | VERIFIED | "Lint SVG diagrams (SVGO)" step confirmed at line 40; runs before "Build and gate on figure errors" (line 78); loops over `docs/assets/diagrams/*.svg`; exits 1 on any non-idempotent diagram; YAML parses clean (yaml.safe_load exits 0) |
| 5 | `scripts/docs_fig.py` sets `plt.rcParams['svg.hashsalt'] = 'fdars-docs'` so matplotlib SVG element IDs are deterministic across builds (FND-03) | VERIFIED | `"svg.hashsalt": "fdars-docs"` confirmed in rcParams.update dict at line 77; behavioral check passes: `plt.rcParams['svg.hashsalt'] == 'fdars-docs'` after import (HASHSALT_OK) |
| 6 | Two consecutive full mkdocs builds produce byte-identical SVG output from docs_fig.py exec blocks (FND-03, ROADMAP SC #3) | PRESENT_BEHAVIOR_UNVERIFIED | Code seam (hashsalt) is present and verified; end-to-end two-build byte-identity is a runtime invariant requiring a full mkdocs build with compiled fdars — cannot be confirmed from source alone |
| 7 | `scripts/docs_fig.py` exposes a `fast(full, fast_value)` helper that reads `DOCS_FAST` once and returns `fast_value` when set, else `full` (FND-06, D-08) | VERIFIED | `def fast(full, fast_value)` exists at line 109; `_os.environ.get("DOCS_FAST")` is the single env check; behavioral spot-check confirmed: returns 500 unset, returns 50 with `DOCS_FAST=1`; module docstring states fast mode is speed-only (D-07) |
| 8 | Setting `DOCS_FAST=1` causes the docs build to complete materially faster than the full build (FND-06, ROADMAP SC #6) | PRESENT_BEHAVIOR_UNVERIFIED | fast() helper is verified working; end-to-end timing speedup is a runtime property requiring a real mkdocs build — cannot be confirmed from source alone |
| 9 | `pymdownx.snippets` is enabled in mkdocs.yml with `base_path: [docs]` so `--8<-- "includes/..."` resolves under `docs/` (FND-04) | VERIFIED | `pymdownx.snippets` confirmed in mkdocs.yml markdown_extensions block with `base_path: [docs]`; mkdocs.yml is structurally valid (uses mkdocs-material Python YAML tags, expected behavior) |
| 10 | `docs/includes/` contains one snippet fragment per dataset loader (canadian-weather, canadian-weather-precip, tecator, growth, phoneme), each holding only plain Python preamble lines with no fence delimiters and no exec attributes (FND-04) | VERIFIED | All five files exist; none contain backtick fence delimiters or exec= attributes; content confirmed: plain import + loader lines only; loader variable names verified (day/X/meta, wl/X/meta, age/X/meta, freq/X/meta) |
| 11 | At least one example page fence uses the `--8<--` include instead of inline preamble, and mkdocs build --strict still succeeds (FND-04, ROADMAP SC #4) | VERIFIED | `docs/examples/canadian-weather.md` line 20 confirmed: `--8<-- "includes/load-canadian-weather.md"` inside an `exec="1" html="1"` fence; SUMMARY records mkdocs build --strict exit 0 (312s) |
| 12 | `conftest.py` (repo root) defines `pytest_markdown_docs_globals()` returning `{np, plt, fdars}`, and sets `matplotlib.use('Agg')` before importing pyplot (FND-05, D-06) | VERIFIED | File exists; `pytest_markdown_docs_globals()` confirmed; behavioral check: returns exactly `{np, plt, fdars}`; `matplotlib.get_backend() == 'Agg'` confirmed; Agg set before pyplot import at lines 35-38; snippet expansion hook `pytest_markdown_docs_markdown_it()` also present (documented D-04 fix) |
| 13 | `pytest --co -q` discovers example code fences via pytest-markdown-docs with `--markdown-docs-syntax=superfences` (FND-05, ROADMAP SC #5) | VERIFIED | Collection run confirmed: 8 fences collected from `docs/examples/canadian-weather.md` with the superfences flag (non-empty collection proves the syntax flag recognizes exec="1" fences) |
| 14 | The doc-test CI gate (Gate B) blocks on the smoke-test page ONLY, not on all example pages (D-11) | VERIFIED | "Doc-test smoke (canadian-weather.md)" step confirmed in docs.yml line 63; gates only `docs/examples/canadian-weather.md`; comment in CI step explicitly says gated set grows in Phase 9; `docs/examples/` appears exactly 2 times in docs.yml (the comment and the path) |
| 15 | `pytest-markdown-docs` is added to `docs/requirements.txt` (FND-05) | VERIFIED | `pytest-markdown-docs==0.9.2` confirmed in docs/requirements.txt at line 16 with explanatory comment |

**Score:** 10/12 truths verified (2 present, behavior-unverified — require full mkdocs build)

Note: Truths 1–5, 7, 9–15 were fully verified. Truths 6 and 8 are backstop/runtime invariants with code seams verified but runtime confirmation deferred.

---

### Deferred Items

None. All phase deliverables target this phase; backstop truths 6 and 8 require human CI verification, not later-phase work.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/assets/diagrams/STYLE_SPEC.md` | SVG authoring contract | VERIFIED | Full FND-01 checklist satisfied |
| `svgo.config.mjs` | Check-only SVGO lint config | VERIFIED | 9 plugins disabled (6 required + 3 for idempotence) |
| `.github/workflows/docs.yml` | CI gates A and B | VERIFIED | Gate A (SVGO, line 40) and Gate B (doc-test, line 63) both present and ordered correctly |
| `scripts/docs_fig.py` | svg.hashsalt + fast() helper | VERIFIED | Both additions confirmed in existing file |
| `mkdocs.yml` | pymdownx.snippets with base_path | VERIFIED | Extension present with `base_path: [docs]` |
| `docs/includes/load-canadian-weather.md` | Snippet fragment (no fence) | VERIFIED | Plain Python preamble, no fence delimiters |
| `docs/includes/load-canadian-weather-precip.md` | Snippet fragment (no fence) | VERIFIED | Plain Python preamble |
| `docs/includes/load-tecator.md` | Snippet fragment (no fence) | VERIFIED | Plain Python preamble |
| `docs/includes/load-growth.md` | Snippet fragment (no fence) | VERIFIED | Plain Python preamble |
| `docs/includes/load-phoneme.md` | Snippet fragment (no fence) | VERIFIED | Plain Python preamble |
| `conftest.py` | pytest globals hook + snippet expand | VERIFIED | globals hook + markdown_it hook present |
| `docs/requirements.txt` | pytest-markdown-docs pinned | VERIFIED | ==0.9.2 confirmed |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `svgo.config.mjs` plugin overrides | `<style>`, IDs, `<desc>`, viewBox, role/aria-label | 9 `false` overrides in preset-default | VERIFIED | All five preserved constructs confirmed in config |
| CI Gate A diff loop | `docs/assets/diagrams/*.svg` | Idempotence check (pass2==pass1) | VERIFIED | Loop runs before mkdocs build (line 40 < line 78) |
| `npx svgo@3.3.4` | reproducible gate output | exact version pin in CI step | VERIFIED | `svgo@3.3.4` pinned in docs.yml line 55-56 |
| `plt.rcParams['svg.hashsalt']` | deterministic IDs at build time | set at module-import in rcParams.update | VERIFIED | Set at line 77, inside the dict that runs at module load |
| `fast()` helper | `os.environ['DOCS_FAST']` | `_os.environ.get("DOCS_FAST")` in body | VERIFIED | Single env check, DRY per D-08; behavioral check passes |
| `mkdocs.yml pymdownx.snippets base_path` | `--8<-- "includes/NAME.md"` resolves to `docs/includes/NAME.md` | `base_path: [docs]` | VERIFIED | Config present; one fence in canadian-weather.md uses the include |
| `conftest.py matplotlib.use('Agg')` | must precede import matplotlib.pyplot | set before pyplot import | VERIFIED | Lines 35-38: `matplotlib.use("Agg")` then `import matplotlib.pyplot as plt` |
| `PYTHONPATH=scripts` | fences resolve docs_fig/docs_data imports | CI Gate B env block | VERIFIED | `env: PYTHONPATH: scripts` confirmed in Gate B step |
| Gate B smoke-test page list | `docs/examples/canadian-weather.md` only | hardcoded single path in CI | VERIFIED | Only one path (`canadian-weather.md`) appears in pytest invocation |

---

### Data-Flow Trace (Level 4)

Not applicable. This is a documentation-tooling phase. No dynamic-data-rendering components.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `plt.rcParams['svg.hashsalt'] == 'fdars-docs'` after import | `.venv/bin/python -c "import docs_fig, matplotlib.pyplot as plt; assert plt.rcParams['svg.hashsalt']=='fdars-docs'"` | HASHSALT_OK | PASS |
| `fast(500, 50)` returns 500 when DOCS_FAST unset | `.venv/bin/python -c "import docs_fig; ... assert docs_fig.fast(500,50)==500"` | Returns 500 | PASS |
| `fast(500, 50)` returns 50 when DOCS_FAST=1 | `.venv/bin/python -c "import os,docs_fig; os.environ['DOCS_FAST']='1'; assert docs_fig.fast(500,50)==50"` | Returns 50 | PASS |
| conftest globals returns exactly {np, plt, fdars} | `.venv/bin/python -c "import conftest; assert set(conftest.pytest_markdown_docs_globals())=={'np','plt','fdars'}"` | CONFTEST_OK | PASS |
| conftest forces Agg backend | `.venv/bin/python -c "import conftest, matplotlib; assert matplotlib.get_backend().lower()=='agg'"` | backend: Agg | PASS |
| pytest --co discovers 8 fences in canadian-weather.md | `.venv/bin/python -m pytest --co -q --markdown-docs --markdown-docs-syntax=superfences docs/examples/canadian-weather.md` | 8 tests collected | PASS |
| Two-build byte-identical SVG output (FND-03 runtime) | Requires full mkdocs build with compiled fdars | (not run — needs real build env) | SKIP (route to human) |
| DOCS_FAST=1 materially faster (FND-06 runtime) | Requires full mkdocs build timing | (not run — needs real build env) | SKIP (route to human) |

---

### Probe Execution

No explicit probe scripts declared in PLAN files. Step 7c: N/A for this phase.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| FND-01 | Plan 01-01 | SVG style spec at docs/assets/diagrams/STYLE_SPEC.md | SATISFIED | Full FND-01 checklist: palette, five classes, stroke weights, viewBox 720 + heights, `<style>` block, accessibility, svgo pin |
| FND-02 | Plan 01-01 | SVGO config preserves style/IDs/desc/viewBox/aria; check-only gate in CI | SATISFIED | svgo.config.mjs with 9 disabled plugins; idempotence gate in CI blocking before build; prohibition on rewrites verified |
| FND-03 | Plan 01-02 | Deterministic SVG output: svg.hashsalt set in docs_fig.py | PARTIALLY SATISFIED | Code seam verified (hashsalt at rcParams line 77); runtime two-build byte-identity requires human CI verification |
| FND-04 | Plan 01-03 | pymdownx.snippets enabled; docs/includes/ preamble fragments; one fence converted | SATISFIED | snippets in mkdocs.yml; 5 include files confirmed clean; include wired in canadian-weather.md |
| FND-05 | Plan 01-04 | pytest-markdown-docs harness; conftest.py globals; CI Gate B on one page | SATISFIED | conftest.py, docs/requirements.txt pin, CI Gate B all verified; 8 fences collected |
| FND-06 | Plan 01-02 | fast() DOCS_FAST helper as single env check | PARTIALLY SATISFIED | Helper verified working behaviorally; end-to-end timing speedup requires human CI verification |

**REQUIREMENTS.md Traceability:** All six FND-01 through FND-06 requirements are marked Complete in REQUIREMENTS.md Phase 1 row. Plans 01-01 through 01-04 collectively claim exactly these six IDs; no orphaned or unmapped requirement IDs found for Phase 1.

---

### Anti-Patterns Found

| File | Pattern | Severity | Notes |
|------|---------|----------|-------|
| None | — | — | No TBD, FIXME, XXX, or placeholder patterns found in any phase-modified file |

Debt-marker scan across all phase-modified files (`STYLE_SPEC.md`, `svgo.config.mjs`, `scripts/docs_fig.py`, `conftest.py`, `docs/requirements.txt`, `.github/workflows/docs.yml`, `mkdocs.yml`) produced no matches.

---

### Prohibition Verification

| Prohibition | Status | Evidence |
|-------------|--------|---------|
| SVGO gate MUST NOT rewrite committed hand-authored SVGs (D-02) | VERIFIED NOT VIOLATED | CI step uses `--output -` (stdout only), never `-o <file>`; idempotence check does not touch source files |
| STYLE_SPEC conformance MUST NOT be machine-enforced by the svgo gate this phase (D-03) | VERIFIED NOT VIOLATED | Gate checks structural idempotence only; no viewBox width, class names, or role/aria-label enforcement in the gate loop |
| DOCS_FAST MUST NOT use scattered os.environ checks (D-08) | VERIFIED NOT VIOLATED | Single `_os.environ.get("DOCS_FAST")` call in `fast()` body only; line 126 is the only occurrence in docs_fig.py |
| Snippet files MUST NOT contain fence delimiters or exec= attributes (FND-04) | VERIFIED NOT VIOLATED | All five include files confirmed fence-free and exec-attribute-free |
| Doc-test CI gate MUST NOT block on all example pages (D-11) | VERIFIED NOT VIOLATED | Gate B hardcodes `docs/examples/canadian-weather.md` only; `docs/examples/` appears exactly twice in docs.yml (comment + path) |

---

### Documented Deviations (from PLAN intent)

Two auto-fixed deviations are documented in SUMMARYs and confirmed correct in the codebase:

1. **Gate design changed from source-diff to idempotence check (Plan 01-01):** The planned `diff <(svgo stdout) source` gate was replaced with `diff <(svgo(svgo(x))) <(svgo(x))` because svgo@3.3.4's XML serialiser unconditionally normalises whitespace and attribute ordering. The new gate preserves D-02 (never rewrites source) while being mechanically correct. Three additional plugins (mergePaths, convertPathData, collapseGroups) were disabled to achieve idempotence across all 43 diagrams. All 43 pass with no exclusion list.

2. **Snippet include expansion hook added to conftest.py (Plan 01-04):** The planned D-04 fallback was for cross-fence state; the actual failure was the `--8<--` snippet directive reaching Python raw under pytest. Fixed by adding `pytest_markdown_docs_markdown_it()` core rule to conftest.py. This is within the plan's "choose fallback at execution time" mandate and leaves example .md files untouched.

Both deviations are mechanical improvements that preserve the plan intent. No scope was added or removed.

---

### Human Verification Required

#### 1. Two-Build Byte-Identical SVG Output (FND-03 runtime proof)

**Test:** Run `mkdocs build` twice consecutively (with `DOCS_FAST` unset and compiled fdars installed) and diff the SVG output files between the two builds.
**Expected:** Zero byte-level difference between build 1 and build 2 SVG outputs across all rendered figures.
**Why human:** The `svg.hashsalt = "fdars-docs"` code seam is present and verified. The two-build byte-identity guarantee is a runtime invariant that depends on the full build pipeline (mkdocs + markdown-exec + compiled fdars + matplotlib SVG backend). Cannot be confirmed from source inspection alone.

#### 2. DOCS_FAST=1 Material Speedup (FND-06 runtime proof)

**Test:** Time a full `mkdocs build` (DOCS_FAST unset) vs `DOCS_FAST=1 mkdocs build` on any page with expensive params wrapped in `fast()`.
**Expected:** The DOCS_FAST=1 build completes materially faster.
**Why human:** The `fast()` helper is verified working (returns fast_value when DOCS_FAST is set). Whether the speedup is "material" depends on which pages use `fast()` at which call sites. Currently no example pages other than canadian-weather.md call `fast()`, so this may only become testable when later phases add expensive-param blocks. The helper is correctly in place for those phases.

#### 3. Full CI Run Confirmation

**Test:** Trigger a GitHub Actions run on the docs workflow (or review the most recent run) and confirm both Gate A (SVGO) and Gate B (doc-test smoke) pass, and mkdocs build --strict exits 0.
**Expected:** All 43 diagrams pass the idempotence gate; 8/8 fences pass on canadian-weather.md; strict build exits 0; no regression on existing CI steps.
**Why human:** Cannot observe actual CI run results from the local working tree.

---

### Gaps Summary

No gaps. All required artifacts exist and are substantive and wired. Both prohibitions verified not violated. No debt markers.

The two human-verification items are runtime invariants (FND-03 two-build byte-identity and FND-06 timing speedup) for which the code seams are correctly in place but end-to-end confirmation requires a full mkdocs build with compiled fdars.

---

_Verified: 2026-08-07_
_Verifier: Claude (gsd-verifier)_
