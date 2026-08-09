---
phase: 01-foundation
plan: 04
subsystem: docs-tooling
tags: [pytest-markdown-docs, conftest, ci, doc-tests, pymdownx-snippets, FND-05]
status: complete
requires:
  - "docs/requirements.txt (docs build deps)"
  - "pymdownx.snippets + docs/includes/ (plan 01-03, FND-04)"
  - ".github/workflows/docs.yml Gate A / SVGO lint (plan 01-01)"
provides:
  - "conftest.py globals hook: np/plt/fdars injected into example fences (FND-05, D-06)"
  - "conftest.py snippet-expansion hook: pytest-markdown-docs runs fences that use --8<-- includes (D-04)"
  - "pytest-markdown-docs==0.9.2 pinned in docs/requirements.txt"
  - "CI Gate B: doc-test smoke on docs/examples/canadian-weather.md only (D-11)"
affects:
  - "Phase 9 example-fixing: gated page set grows page-by-page from canadian-weather.md"
tech-stack:
  added:
    - "pytest-markdown-docs==0.9.2 (Modal Labs; dev/test pytest plugin; docs/requirements.txt only)"
  patterns:
    - "pytest_markdown_docs_globals() returns {np, plt, fdars}"
    - "pytest_markdown_docs_markdown_it() core-rule expands pymdownx --8<-- includes"
    - "matplotlib.use('Agg') before pyplot import (mirrors scripts/docs_fig.py)"
key-files:
  created:
    - "conftest.py"
  modified:
    - "docs/requirements.txt"
    - ".github/workflows/docs.yml"
decisions:
  - "D-04 verdict: pytest-markdown-docs LOCKED IN as THE harness — cross-fence-state risk did not materialise (7/8 canadian-weather.md fences self-contained)"
  - "D-04 fallback NOT needed for cross-fence state; the one real failure was FND-04 snippets (--8<--) reaching Python raw, fixed by teaching the harness to expand includes via the markdown_it hook rather than editing example .md (Phase 9's domain)"
  - "Gate B gates the single smoke-test page only (D-11); grows page-by-page in Phase 9"
metrics:
  duration: 5min
  completed: 2026-08-07
actuals:
  tokens: 1381
  tasks: 4
  commits: 3
---

# Phase 1 Plan 4: Doc-Test Harness (pytest-markdown-docs) Summary

Stood up the `pytest-markdown-docs` doc-test harness end-to-end: a repo-root
`conftest.py` globals hook exposing `np`/`plt`/`fdars` with the Agg backend
forced, the pinned dependency, a passing smoke-test on `canadian-weather.md`,
and CI Gate B scoped to that one page (D-11). The D-04 smoke-test settled the
harness question — `pytest-markdown-docs` is locked in.

## What Was Built

| Task | Deliverable | Commit |
|------|-------------|--------|
| 1 | Package-legitimacy checkpoint (blocking-human) — pytest-markdown-docs@0.9.2 cleared | (checkpoint, no commit) |
| 2 | `conftest.py` globals hook: `pytest_markdown_docs_globals()` → `{np, plt, fdars}`, `matplotlib.use("Agg")` before pyplot (FND-05, D-06) | `5375660` |
| 3 | `pytest-markdown-docs==0.9.2` pinned in `docs/requirements.txt`; smoke-test passes 8/8 on `canadian-weather.md`; D-04 resolved | `79ad31b` |
| 4 | CI Gate B "Doc-test smoke (canadian-weather.md)" in `docs.yml`, one page only (D-11), SVGO Gate A untouched | `517d0f1` |

## D-04 Verdict (recorded)

**`pytest-markdown-docs` is LOCKED IN as THE doc-test harness.** No fallback
harness was needed.

The RESEARCH-flagged cross-fence-state risk **did not materialise**: 7 of the 8
`canadian-weather.md` fences are self-contained (each re-imports and re-declares
its data), so they execute correctly in isolation with the injected globals —
exactly as RESEARCH predicted.

The single initial failure was a **different, real interaction** between two
Phase-1 guardrails, not cross-fence state:

- Fence #1 begins with `--8<-- "includes/load-canadian-weather.md"` — a
  `pymdownx.snippets` include directive introduced by plan 01-03 (FND-04).
- `pytest-markdown-docs` reads the **raw** markdown and does not run MkDocs'
  build-time snippets preprocessor, so the `--8<--` line reached Python verbatim
  and raised `TypeError: bad operand type for unary -: 'str'`.

The two CONTEXT/D-04 fallbacks (custom fence-exec harness / consolidate-fences)
both target cross-fence state and do not apply. Instead the harness was taught
to expand snippet includes via the plugin's documented
`pytest_markdown_docs_markdown_it()` hook: a `markdown_it` core rule rewrites
fence-token content, expanding `--8<-- "path"` against `docs/` (mirroring
mkdocs.yml's `snippets: base_path: [docs]`). This keeps `pytest-markdown-docs`
as the harness and leaves every example `.md` untouched — page rewrites are
Phase 9's domain (D-11). After the fix: **8/8 fences pass**.

## Verification Evidence

- `conftest.pytest_markdown_docs_globals()` returns exactly `{np, plt, fdars}`;
  `matplotlib.get_backend() == 'Agg'` after import → `CONFTEST_OK`.
- `pytest --co -q --markdown-docs --markdown-docs-syntax=superfences
  docs/examples/canadian-weather.md` collects **8 fences** (non-empty →
  the superfences flag recognises `exec="1"` fences; RESEARCH Pitfall 5).
- Full run: **8 passed** on `canadian-weather.md`.
- **Raise-vs-print backstop (RESEARCH Open Q2/A1) confirmed** on a probe page:
  a fence that only `print()`s HTML **passes**; a fence that `raise`s **fails**.
  The gate fails only on exceptions, not on printed output.
- `docs.yml` parses as valid YAML; contains the "Doc-test smoke" step; gates the
  single page only (`docs/examples/` appears ≤ 2 times); SVGO Gate A still present.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking issue] Snippet `--8<--` include broke fence execution under pytest**
- **Found during:** Task 3 (smoke-test run)
- **Issue:** The plan's `<action>` anticipated a possible *cross-fence-state*
  failure. The actual failure was a snippet-preprocessor mismatch: plan 01-03's
  `--8<--` include (FND-04) is not expanded by `pytest-markdown-docs`, so the
  raw directive reached Python and raised `TypeError`.
- **Fix:** Added `pytest_markdown_docs_markdown_it()` to `conftest.py` — a
  `markdown_it` core rule that expands `--8<--` includes in fence content
  (base_path `docs/`, matching mkdocs.yml). This is within the plan's explicit
  D-04 "choose the fallback at execution time" mandate; the chosen resolution is
  narrower than either listed fallback and touches no example markdown.
- **Files modified:** `conftest.py`
- **Commit:** `79ad31b`

## Auth Gates

Task 1 was a **blocking-human package-legitimacy checkpoint** (not an auth gate).
`pytest-markdown-docs@0.9.2` was flagged SUS in RESEARCH (low PyPI download
visibility). The gate was cleared by the orchestrator holding delegated approval
authority, with independent PyPI confirmation (name `pytest-markdown-docs`
0.9.2, author "Modal Labs, Elias Freider", repo
`github.com/modal-labs/pytest-markdown-docs`, a pytest dev/test plugin). Pinned
`==0.9.2` and placed in `docs/requirements.txt` only (not a runtime dependency
of the shipped fdars wheel).

## Known Stubs

None. All deliverables are wired and verified against compiled fdars (0.2.0 in
`.venv`).

## Self-Check: PASSED
- FOUND: conftest.py
- FOUND: docs/requirements.txt (contains `pytest-markdown-docs==0.9.2`)
- FOUND: .github/workflows/docs.yml (contains "Doc-test smoke")
- FOUND commit: 5375660
- FOUND commit: 79ad31b
- FOUND commit: 517d0f1
