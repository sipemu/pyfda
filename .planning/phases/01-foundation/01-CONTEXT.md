# Phase 1: Foundation - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up the tooling and guardrails that every subsequent diagram/example sweep depends on — nothing user-visible on the site changes yet. Deliverables (locked by ROADMAP success criteria FND-01..FND-06):

1. **STYLE_SPEC.md** at `docs/assets/diagrams/STYLE_SPEC.md` — palette, the five CSS classes (`.ttl .sub .lab .sm .mono`), stroke weights, fixed viewBox width 720, allowed heights, copy-paste `<style>` block.
2. **SVGO config** (`svgo.config.mjs`) — losslessly lints diagrams while preserving `<style>`, IDs, `<desc>`, `viewBox`, `role`/`aria-label`.
3. **Deterministic figures** — `docs_fig.py` sets `svg.hashsalt`, stochastic blocks seed RNG, so two consecutive full builds produce byte-identical SVG.
4. **Snippets** — enable `pymdownx.snippets`, factor shared dataset-loading preambles into `docs/includes/`.
5. **Doc-test harness** — `pytest-markdown-docs` discovers example fences; `conftest.py` globals hook exposes `np`, `plt`, `fdars`.
6. **DOCS_FAST gate** — lowers expensive iteration counts for fast local verification.

Clarifying HOW to implement the above; the WHAT is fixed by the roadmap. New capabilities belong in other phases.

</domain>

<decisions>
## Implementation Decisions

### SVGO Toolchain (FND-02)
- **D-01:** Install via **zero-install `npx svgo@<pinned>`** — no `package.json`, no `node_modules`, no committed Node toolchain in this Rust/Python repo. Pin the svgo version for reproducibility. — **Reversibility:** reversible (swap to a committed `package.json` later if a Node footprint becomes warranted).
- **D-02:** SVGO runs as a **check-only lint gate** — it verifies a diagram is optimized/conforming but **never rewrites** the committed hand-authored SVGs. Hand-authored markup is the source of truth.
- **D-03:** Gate scope is **optimization-safety only** — preserve `<style>`, IDs, `<desc>`, `viewBox`, `role`/`aria-label` (exactly FND-02). STYLE_SPEC conformance (viewBox width 720, allowed heights, correct class names, required accessibility attrs) stays a **human review-gate** concern, not machine-enforced this phase.

### Test Harness (FND-05)
- **D-04:** **Smoke-test `pytest-markdown-docs` before locking it in.** STATE.md flags a risk that variable state may not carry across separate code fences (var defined in one fence, used in the next). Run it on one real page first; if cross-fence state works → lock it in as THE harness; if not → fall back.
- **D-05:** Smoke-test target = a page with **genuine cross-fence state dependency** (data loaded in an early fence, reused in later fences), chosen by the planner — not merely the page with the most fences. Candidates exist among the 8–9-fence example pages (e.g. `canadian-weather.md`, `canadian-seasonal.md`).
- **D-06:** `conftest.py` globals hook exposes `np`, `plt`, `fdars` to fence execution (FND-05).

### DOCS_FAST (FND-06)
- **D-07:** DOCS_FAST is **speed-only**. Figures MAY look different/rougher in fast mode; it is explicitly NOT for producing publishable/committed figures. The **full build (DOCS_FAST unset) is the source of truth** and is the only place the FND-03 byte-identical determinism guarantee must hold. Determinism is NOT required in fast mode.
- **D-08:** Wire DOCS_FAST via a **central helper in `docs_fig.py`** that reads the env var once (e.g. `fast(full, fast_value)`); exec blocks call the helper instead of hardcoding or inlining per-block `os.environ` checks. Keeps it DRY and easy for later phases to adopt as they author figures. — **Reversibility:** reversible.

### Enforcement & Verification
- **D-09:** **Wire the guardrails into CI now** (extend the existing docs CI workflow), not just create-and-verify-manually. Enforcement from day one.
- **D-10:** **SVGO lint gate blocks on all diagrams immediately.**
- **D-11:** **Doc-test gate grows with coverage.** `pytest-markdown-docs` blocks CI only on the smoke-test page now; the passing/gated set expands **page-by-page as Phase 9 fixes each example** against the current API. This keeps CI green through Phases 1–8 and avoids pulling Phase 9's example-fixing work forward. Do NOT make doc-tests blocking on all example pages now.

### Claude's Discretion
- **Test-harness fallback** (if smoke-test shows cross-fence state fails): user said "you decide at the time." Candidate space = (a) a **custom `conftest.py` fence-exec harness** that execs all fences of a page in one shared namespace, or (b) a **consolidate-fences authoring convention** (each page's runnable code self-contained). Pick based on exactly how `pytest-markdown-docs` fails during the smoke-test.
- **Smoke-test page selection:** planner's choice among genuinely state-dependent pages.
- **DOCS_FAST semantics & wiring** (D-07, D-08): decided by Claude on "you decide"; recorded above as locked.
- **`pymdownx.snippets` / `docs/includes/` organization** (FND-04): not discussed — standard approach (one include per dataset preamble, referenced via snippets) at planner discretion.
- **Pre-commit hooks:** optional; CI is the agreed gate. Add pre-commit only if it's cheap.
- **Determinism mechanics** (FND-03: `svg.hashsalt`, RNG seeding): standard implementation, not a gray area.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase spec & scope
- `.planning/ROADMAP.md` §"Phase 1: Foundation" — the six success criteria that define done.
- `.planning/REQUIREMENTS.md` §Foundation — FND-01..FND-06 requirement text.
- `.planning/PROJECT.md` — milestone intent, constraints, Out-of-Scope, Key Decisions table.

### Existing docs tooling (to extend, not replace)
- `mkdocs.yml` — current `plugins:` (`markdown-exec`), `hooks:` (`docs/hooks.py`), and `markdown_extensions:` (`pymdownx.*`); `pymdownx.snippets` must be ADDED here (FND-04).
- `scripts/docs_fig.py` — the build-time figure helper (`fig()`, `render()`, brand palette, matplotlib rcParams); DOCS_FAST helper (D-08) and `svg.hashsalt` (FND-03) go here. Canonical exec mechanism is `PYTHONPATH=scripts`.
- `docs/hooks.py` — fallback figure mechanism.
- `docs/assets/diagrams/` — the 43 existing hand-authored `.svg` diagrams SVGO must lint; de-facto baseline for STYLE_SPEC (`viewBox="0 0 720 300"`, `.ttl/.sub/.lab/.sm/.mono`, system-ui, muted palette, `role="img"` + `aria-label`).
- `docs/examples/*.md` — 17 example pages (smoke-test target lives here).

### Codebase maps
- `.planning/codebase/` — ARCHITECTURE, STRUCTURE, STACK, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS.

### CI
- `.github/workflows/` — existing docs CI workflow to extend with the SVGO lint + doc-test gates (D-09).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/docs_fig.py`: already centralizes figure rendering, the brand palette, and matplotlib rcParams — the natural home for the DOCS_FAST helper and `svg.hashsalt` determinism setting.
- 43 conforming-ish SVGs in `docs/assets/diagrams/` provide the concrete baseline the STYLE_SPEC formalizes; SVGO config should pass cleanly against them.
- 17 example pages in `docs/examples/` with 7–9 python fences each — repeated CSV-loading preambles are the deduplication target for `docs/includes/`.

### Established Patterns
- Build-time inline SVG figures via `markdown-exec` code blocks (`python exec="1" html="1"`) importing `docs_fig` with `PYTHONPATH=scripts` (canonical) / `docs/hooks.py` (fallback).
- Diagrams referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`.
- No existing Node toolchain, no `package.json`, no project-level `conftest.py`, no `docs/includes/` yet — all net-new this phase.

### Integration Points
- `mkdocs.yml` gains `pymdownx.snippets`; `docs/includes/` becomes the snippets base.
- `docs_fig.py` gains DOCS_FAST helper + `svg.hashsalt`.
- New root/test `conftest.py` for the pytest-markdown-docs globals hook.
- New `svgo.config.mjs` at repo root; invoked via pinned `npx`.
- Existing `.github/workflows/` docs CI extended with the two gates.

</code_context>

<specifics>
## Specific Ideas

- STYLE_SPEC must formalize the EXISTING baseline, not invent a new look: `viewBox="0 0 720 300"` width-720 convention, the five classes `.ttl/.sub/.lab/.sm/.mono`, system-ui fonts, the muted Bootstrap-ish palette, `role="img"` + `aria-label`.
- svgo invocation pinned to a specific version string for reproducibility (zero-install `npx`).
- Full build is the determinism/publish source of truth; DOCS_FAST is a throwaway local accelerator.

</specifics>

<deferred>
## Deferred Ideas

- **A11Y-01** (from STATE.md): long-form `<title>`/`<desc>` + `aria-labelledby` for complex diagrams — v2.
- **EX2-01** (from STATE.md): editorial consolidation of overlapping example pages (sonar-tsrvf vs phoneme-shape; Andrews-wine series) — v2.
- **Method-semantic research flags** (from STATE.md, land in later phases): regression/ and monitoring/ diagram accuracy needs verification against `fdars-core` behavior — β(t), conformal functional bands, SPM Phase I/II — Phases 7–8.
- Fixing example pages to run against the current API is **Phase 9**, not Phase 1 — the doc-test gate is deliberately scoped narrow now (D-11) to avoid pulling it forward.

</deferred>

---

*Phase: 1-Foundation*
*Context gathered: 2026-08-07*
