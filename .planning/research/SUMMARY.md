# Project Research Summary

**Project:** pyfda — v14.0 fdars Software Paper (arXiv Preprint)
**Domain:** Academic software-description paper + reproducible figure/table artifact
**Researched:** 2026-09-08
**Confidence:** HIGH

## Executive Summary

v14.0 delivers an FDApy-style arXiv software paper introducing the `fdars` package, foregrounding **breadth** (437 callables across 31 modules) and **method-accuracy/correctness** — explicitly no performance benchmarks. The Python FDA gap is real and citable: only scikit-fda (largely one-dimensional; no FTS/Fréchet/SPM/conformal) and FDApy (FPCA + dimension reduction only) exist, while fdars covers ≥18 capability families with no Python equivalent, plus a scikit-learn estimator layer (28 estimators) and a unique grounded AI-advisor + scientific-provenance layer. The paper is backed by a fully reproducible pipeline (a Python figure/table generator + CI `tectonic` PDF compile) fed from two committed single-source-of-truth JSON files (`_capability_map.json` for coverage, `_references_map.json` for the bibliography), so numeric claims cannot silently drift.

Experts build these papers as a plain `article`-class LaTeX manuscript whose every code snippet flows from executed scripts (never copy-pasted) and whose every number is a machine-derived macro. The recommended approach mirrors the project's proven v12/v13 patterns: derive denominators, don't hardcode; default coverage claims to honest/partial; and gate correctness with a blocking human read-through (the same shape that caught 9 citation bugs in v13).

**Primary risk:** stale API snippets and hardcoded coverage counts drifting from the live JSON after the manuscript is written — mitigated by deriving all numeric claims at build time (`\input{counts.tex}` macros) and executing every snippet through a hard pipeline gate before LaTeX compiles. **Secondary risk:** inaccurate peer-package comparison rows inviting reviewer rejection — mitigated by grounding the comparison table in a version-stamped `comparison_evidence.md`, human-reviewed at close.

## Key Findings

### Recommended Stack

Plain `\documentclass[12pt]{article}` (no custom `.sty`) matching the FDApy reference exactly — venue-agnostic, reshapeable to JOSS/JSS later. Bibliography via **natbib + BibTeX, not biblatex + biber**: tectonic has documented, unfixed biber version-mismatch failures in CI (silently produces `[?]` citations). arXiv's Nov-2025 rule change accepts raw `.bib` directly (no pre-compiled `.bbl`), but natbib+bibtex avoids all ambiguity. PDF compiles **only in CI** (no local TeX) via `wtfjoke/setup-tectonic@v4` (tectonic 0.17.x), in a standalone `paper.yml` workflow path-filtered to `paper/**`.

**Core technologies:**
- **LaTeX `article` class + natbib + BibTeX** — manuscript — venue-agnostic, tectonic-compatible, no biber failure mode
- **tectonic 0.17.x via `wtfjoke/setup-tectonic@v4`** — CI PDF compile — single-binary, no local TeX needed, caches packages
- **Python + matplotlib (`Agg`) + Makefile** — reproducible figure/table pipeline — no Snakemake/DVC (20+ deps for zero benefit on a linear pipeline); determinism via `use("Agg")`, module-top rcParams, per-figure `np.random.seed(42)`, PDF output with suppressed `CreationDate` metadata
- **stdlib Python generators** — `gen_refs_bib.py` (bib from `_references_map.json`), `assert_coverage.py`/`gen_counts.py` (coverage macros from `_capability_map.json`) — no new deps
- **CITATION.cff 1.2.0** — citable-release metadata — validate with `cffconvert --validate`

### Expected Features

Section skeleton grounded in FDApy (arXiv:2101.11003) and scikit-fda (JSS 2024): Intro → FDA background → Data representation → Software design/architecture → Capability tour by family → Comparison with related software → Case studies → Availability → Conclusion → References.

**Must have (table stakes):**
- Statement of need / the Python FDA gap, with peer-package comparison
- Data-representation model (`Fdata`, argvals/grids, irregular/sparse)
- Capability tour by family with minimal runnable examples
- ≥3 real-dataset case studies with figures
- Honest, machine-derived coverage numbers

**Should have (competitive differentiators):**
- Formal comparison table (≈23 capability rows × ~8 package columns: scikit-fda, FDApy, R fda/fda.usc/refund, funData/tidyfun, Matlab fdaM/PACE)
- The unique fdars story: PACE/sparse FPCA, sklearn compatibility (28 estimators, full `check_estimator`), grounded AI advisor + provenance layer, Rust/zero-copy design (qualitative)

**Defer / exclude:**
- Performance benchmarks — explicitly out of scope per user
- JOSS short-form draft — arXiv preprint is primary; can reshape later

### Architecture Approach

`paper/` sits at repo root, peer to `docs/`/`examples/` (it is not a docs page). The figure pipeline **reuses** `scripts/docs_fig.py` via import (adds `scripts/` to `sys.path`, reuses `fig()`/`FDARS_COLORS`, adds a PNG/PDF `save_fig()` helper) and reuses `docs/data/` via a `data_path()` resolver — no copy, no symlink. Single-source-of-truth wiring: `assert_coverage.py` re-derives (public, total) counts from `_capability_map.json` and writes `coverage_counts.tex` macros, exiting non-zero on drift; `gen_refs_bib.py` emits `refs.bib` from `_references_map.json`. A standalone `paper.yml` CI job (path-filtered to `paper/**` + both JSON files + `docs/data/**`) runs the pipeline as the hard gate, then compiles with tectonic.

**Major components:**
1. **`paper/` LaTeX manuscript** (`paper.tex`, `refs.bib`, `figures/`, `sections/`) — the deliverable
2. **`paper/code/` reproducible pipeline** (`build_figures.py`/`generate_all.py`, `paper_utils.py`, `assert_coverage.py`, `gen_refs_bib.py`, Makefile targets) — regenerates every figure + table + numeric macro
3. **`.github/workflows/paper.yml`** — offline pipeline gate + tectonic PDF compile
4. **`CITATION.cff` + `comparison_evidence.md`** — citable metadata + version-stamped peer-coverage evidence

### Critical Pitfalls

1. **Stale code snippets** (highest risk) — every `.tex` snippet must flow from executed `paper/code/` scripts via `\verbatiminput` / `\input`, never copy-pasted; the pipeline runner is the hard local gate.
2. **Hardcoded coverage counts drifting from JSON** — derive all numbers as `\input{counts.tex}` macros; `assert_coverage.py` exits non-zero on drift; wired into CI before figures are committed.
3. **Inaccurate peer-comparison rows** (reviewer-rejection risk) — ground every competitor cell in `comparison_evidence.md` (URL + version + date); blocking human review at close.
4. **Non-deterministic matplotlib output** — `Agg` backend, fixed rcParams, per-figure seed, PDF with suppressed `CreationDate`; determinism check = empty `git diff paper/figures/` on re-run (FreeType/font variance across platforms is the residual risk — generate/verify in CI).
5. **tectonic + biblatex silent bib failure** — use natbib + BibTeX; decided before the first `paper.tex` commit.
6. **arXiv self-containment** — arXiv recompiles source server-side; close-gate must test a clean-dir `pdflatex + bibtex` build with all figures committed to `paper/figures/`.

## Implications for Roadmap

Based on research, suggested phase structure (continues numbering from v13.0 → **starts at Phase 85**):

### Phase 85: Manuscript Scaffold + Pipeline Infrastructure
**Rationale:** Strict prerequisite — locks the tooling decisions (natbib+BibTeX, plain `article`, no `\today`, macro-driven counts) that every later phase depends on; getting these wrong propagates everywhere.
**Delivers:** `paper/` tree, `paper.tex` skeleton + section stubs, `CITATION.cff`, `paper/code/` framework, `paper_utils.py`/`data_path()`, Makefile targets, a compiling minimal PDF.
**Avoids:** Pitfalls 5 (biblatex), 2 (hardcoded counts scaffolding).

### Phase 86: Single-Source-of-Truth Wiring + CI Gate
**Rationale:** Make drift tripwires functional before any prose cites numbers, so every authoring phase is protected from day one.
**Delivers:** `assert_coverage.py` (counts from `_capability_map.json` → `coverage_counts.tex`, non-zero on drift), `gen_refs_bib.py` (`refs.bib` from `_references_map.json`), `.github/workflows/paper.yml` (offline pipeline gate + tectonic compile).
**Uses:** stdlib generators, tectonic CI. **Implements:** components 2–3. **Avoids:** Pitfalls 1, 2.

### Phase 87: Comparison Table + Evidence File
**Rationale:** Highest peer-review-rejection risk; must precede the capability tour that references it. Requires a peer-package spot-check gate.
**Delivers:** `comparison_evidence.md` (version-stamped sources), the ~23×8 comparison table (`\input`-ed), fdars column grounded from `_capability_map.json`.
**Avoids:** Pitfall 3 (inaccurate comparison).

### Phase 88: Front Matter + Design/Architecture + Capability Tour
**Rationale:** Prose sections that need no experiments; unblock writing immediately once infrastructure exists.
**Delivers:** Abstract, Intro/statement-of-need, FDA background, data-representation, software design (Rust+PyO3, module map, `Fdata`, sklearn, advisor), capability tour by family with minimal runnable snippets.

### Phase 89: Case Studies + Reproducible Figures
**Rationale:** Experiment-dependent; depends on `fdars` install in the paper env + verified dataset structures.
**Delivers:** 3 case studies on `docs/data/` (phoneme/growth → smooth+FPCA+classify; tecator/canadian_weather → registration+regression; canadian_weather_precip → FTS forecast), figure scripts, committed `paper/figures/`.

### Phase 90: Close Gate — Correctness, arXiv Compile, Human Review
**Rationale:** Final integration; depends on all sections + figures.
**Delivers:** every-snippet-runs verification, `assert_coverage` re-run (catch late binding additions), determinism check (byte-identical figures on re-run), clean-dir arXiv `pdflatex+bibtex` compile test, blocking human manuscript read-through, `CITATION.cff`/metadata finalization, package-tick decision.

### Phase Ordering Rationale
- Infrastructure (85–86) strictly precedes authoring — no parallel work without the scaffold + drift gates.
- The comparison table (87) precedes the capability tour that cites it and carries the highest external-review risk, so it's isolated with its own evidence gate.
- Prose (88) and experiment-driven case studies (89) are largely independent once infrastructure is ready and could overlap.
- Close (90) is pure integration + the correctness gates the milestone's core value demands.

### Research Flags
Phases likely needing deeper research during planning:
- **Phase 86:** tectonic caching + path-filter behavior (verify cache hit/miss when library changes but `paper/` doesn't) before deploying `paper.yml`.
- **Phase 87:** peer-package coverage facts (scikit-fda 0.10.x `check_estimator` status, FDApy v1.x, R refund) need a spot-check against CRAN/PyPI/arXiv before the table is finalized.
- **Phase 89:** `canadian_weather_precip.csv` structure — confirm it supports multi-year slicing for the FTS case study before the figure script is written.

Phases with standard patterns (skip research-phase):
- **Phase 85:** arXiv/LaTeX requirements well-documented; structure mirrors FDApy/scikit-fda.
- **Phase 88:** routine academic prose; snippet-testing + deterministic matplotlib are proven `docs.yml` patterns.
- **Phase 90:** human review + arXiv submission rules are documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | arXiv reqs + tectonic biber issues + matplotlib Agg determinism verified against official docs / issue trackers |
| Features | MEDIUM-HIGH | Section skeleton grounded in FDApy + scikit-fda JSS; differentiators verified vs `_capability_map.json`; comparison rows MEDIUM pending Phase-87 spot-check |
| Architecture | HIGH | Layered onto the existing repo; single-source-of-truth + drift tripwire proven in v12–v13; CI mirrors `docs.yml` |
| Pitfalls | HIGH | Derived from arXiv docs, tectonic issues, matplotlib docs, and shipped v6–v13 gate patterns |

**Overall confidence:** HIGH

### Gaps to Address
- **`journal` field missing in `_references_map.json`** — `gen_refs_bib.py` needs a strategy: add `journal`/venue to `@article` entries during a curation pass, or emit `@misc` for venue-less papers. Resolve in Phase 86.
- **FTS dataset structure** — verify `canadian_weather_precip.csv` slicing supports the forecast case study. Resolve in Phase 89.
- **Peer-package coverage verification** — spot-check ≥1 peer package against CRAN/PyPI/arXiv before finalizing the table. Resolve in Phase 87.
- **matplotlib font portability** — confirm byte-identical PDF figures across macOS + Ubuntu CI (FreeType differences). Handle in Phase 86/89 determinism gate.

## Sources

### Primary (HIGH confidence)
- info.arxiv.org/help/submit_tex.html — arXiv TeX submission requirements (Nov-2025 raw-`.bib` rule)
- tectonic GitHub issues #35, #53, #866, #930; setup-tectonic #194 — biber/biblatex failure modes
- matplotlib official docs — `Agg` backend, rcParams, PDF metadata / `svg.hashsalt` determinism
- CITATION.cff 1.2.0 schema; `cffconvert`

### Secondary (MEDIUM confidence)
- arXiv:2101.11003 (FDApy) — section anatomy, case-study conventions, style target
- scikit-fda JSS 2024 (v109i02) — fuller FDA-paper section structure
- JOSS paper format + review criteria — "state of the field" expectations
- CRAN Task View: Functional Data Analysis; PACE description — peer-package coverage (needs spot-check)

### Tertiary (LOW confidence)
- Abstract-level analysis of peer-package feature coverage — comparison-table cells pending Phase-87 verification

---
*Research completed: 2026-09-08*
*Ready for roadmap: yes*
