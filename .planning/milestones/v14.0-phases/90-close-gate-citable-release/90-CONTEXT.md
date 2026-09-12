# Phase 90: Close Gate + Citable Release - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning
**Mode:** Smart discuss + user decisions (autonomous run; user answered the 3 gating questions)

<domain>
## Phase Boundary

The manuscript is provably correct, self-contained for arXiv, human-approved, and shipped as a citable release — the milestone's core-value gates all pass and the paired 0.13.0 package tag is prepared. Final phase of milestone v14.0.

Requirements: GATE-02 (correctness gate), GATE-03 (arXiv self-containment PDF compile), GATE-04 (blocking human read-through), REL-01 (citable 0.13.0 release).

</domain>

<decisions>
## Implementation Decisions (user-confirmed 2026-09-09)

### PDF gate (GATE-03) → **Push to trigger CI**
- No local TeX toolchain exists. Validate the arXiv-equivalent PDF compile via the `paper.yml` GitHub Actions workflow (tectonic). Push the milestone work so CI runs, then fetch the compiled PDF/artifact for the GATE-04 read-through.

### Push target → **Push to main**
- Push the (currently ~111 unpushed) commits directly to `origin/main` (project default branch), matching how prior milestones shipped. `gh`/`git` available.

### Release scope (REL-01) → **Prepare, you publish**
- I bump 0.12.0 → 0.13.0 (`Cargo.toml`, `pyproject.toml`, `python/fdars/__init__.py` `__version__`), rebuild fdars at 0.13.0 (`maturin develop --release`), regenerate all paper artifacts so any version-bearing output (snippets, `\FdarsVersion`, coverage macros) reflects 0.13.0, finalize `CITATION.cff` (version 0.13.0; arXiv/Zenodo DOI stays a marked placeholder until the arXiv ID is assigned at submission), and PREPARE the `v0.13.0` tag.
- The USER performs the actual PyPI publish + tag push (PyPI publish fires on the semver `vX.Y.Z` tag push). I do NOT push the tag or publish.

### Gate ordering (load-bearing)
1. Release prep (version bump + rebuild + regenerate) locally; GATE-02 correctness gate MUST stay green at 0.13.0.
2. Push to origin/main → `paper.yml` CI compiles the PDF (GATE-03).
3. Fetch the CI PDF → present for the BLOCKING human read-through (GATE-04). This gate blocks close — do not tag/release until the user approves prose accuracy, comparison table, and citations.
4. On approval: prepare `v0.13.0` tag + hand the user the publish/tag-push commands (REL-01).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- GATE-02 local gates already GREEN this session: `assert_coverage.py --check`, `gen_refs_bib.py --check`, `gen_snippets.py --check`, `check_comparison.py`, figure determinism (`git diff paper/figures/` empty), 0 dangling citations (23 keys).
- `make paper` / `make paper-check` / `make paper-verify` pipeline (Phases 85–89).
- `.github/workflows/paper.yml` — builds fdars via maturin, runs all `--check` gates offline, then compiles the PDF via `wtfjoke/setup-tectonic` (pinned SHA). This is the GATE-03 executor once pushed.
- Toolchain: maturin 1.13.1, cargo 1.97.0, gh 2.97.0 available.

### Version references to bump (0.12.0 → 0.13.0)
- `Cargo.toml:3`, `pyproject.toml:7`, `python/fdars/__init__.py:35` (`__version__`).
- `paper/sections/comparison_table.tex:1` `\newcommand{\FdarsVersion}{0.12.0}` (has a TODO(REL-01) to bump).
- `paper/snippets/represent.tex` (and any snippet capturing the installed fdars version) — regenerated after the rebuild.
- `CITATION.cff:5` `version: "0.12.0"`; `CITATION.cff:36-37` arXiv URL placeholder (keep placeholder until arXiv ID assigned).

### Integration Points
- After the version bump, MUST rebuild fdars (maturin develop) so `import fdars; fdars.__version__` reports 0.13.0, then regenerate snippets/figures so the paper's captured version strings and the drift gates stay consistent (assert_coverage/gen_snippets --check must pass at 0.13.0).

</code_context>

<specifics>
## Specific Ideas

- Milestone gates (STATE): GATE-02 correctness (snippets execute + assert_coverage clean + determinism), GATE-03 self-containment (clean pdflatex/bibtex-equivalent compile — done via tectonic CI here), GATE-04 blocking human read-through. All three are the milestone core-value gates that must pass before close.
- `pyfda-release-versioning` memory: package 0.x is decoupled from the milestone vX.Y; PyPI publish fires only on semver `vX.Y.Z` tags; the v14.0 milestone ships as package 0.13.0.
- Deferred future items (VENUE-01/02 JOSS/JSS, REF-FUT-01 uncurated tail) stay OUT of scope.

</specifics>

<deferred>
## Deferred Ideas

- Actual arXiv submission + real arXiv ID / Zenodo DOI substitution (placeholder now; finalized at upload).
- PyPI publish + tag push — the USER performs these (I prepare only).
- JOSS/JSS venue drafts (VENUE-01/02), uncurated-reference tail (REF-FUT-01) — future milestones.

</deferred>
