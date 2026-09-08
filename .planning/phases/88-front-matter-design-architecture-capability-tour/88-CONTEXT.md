# Phase 88: Front Matter, Design/Architecture & Capability Tour - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous — grey areas proposed and auto-accepted with sensible defaults)

<domain>
## Phase Boundary

The experiment-free prose of the paper is complete — a reader can understand the Python FDA gap, the data model, the Rust/PyO3 + sklearn + advisor architecture, and can see the breadth of the library through minimal runnable, executed-script-sourced snippets. (Case studies with figures are Phase 89; the citable release + CI human-approval gate is Phase 90.)

Delivers prose + snippets for the section stubs authored in Phase 85: `intro.tex`, `design.tex`, `represent.tex`, `capabilities.tex`, `availability.tex` (+ a Conclusion and the advisor/provenance contribution section). Requirements MANU-02..MANU-07.

</domain>

<decisions>
## Implementation Decisions

### Snippet-Sourcing Mechanism (the critical constraint — MANU-06)
- Every code snippet in the capability tour MUST come from an EXECUTED `paper/code/` script — never hand-copied. Mechanism (analogous to the Phase 86 macro pattern): author runnable Python scripts under `paper/code/` (e.g. `snippets/` or `tour_*.py`) that, when run, emit LaTeX `lstlisting`/`verbatim` fragments capturing BOTH the source snippet and its real captured output into generated `.tex` files under `paper/` (e.g. `paper/snippets/*.tex`), which the manuscript `\input`s.
- Add a small stdlib+fdars snippet harness in `paper/code/` (reuse `paper_utils` conventions) that runs a snippet, captures stdout/result, and writes the fragment deterministically (seeded; no timestamps). Wire snippet generation into `make paper` and a `--check` drift gate into `make paper-check` + `paper.yml`.
- This means `paper.yml` now needs `fdars` installed (maturin develop / pip install) — Phase 86 deferred this; Phase 88 (or 89) adds the maturin step to the workflow. fdars 0.12.0 is confirmed importable locally.
- Snippets show INPUT and, where illustrative, captured OUTPUT (repr/print). Keep each snippet minimal (a few lines) — breadth over depth.
- Use LaTeX `listings` (or `minted` only if the CI toolchain supports it — prefer `listings` to avoid a `-shell-escape`/pygments CI dependency).

### Capability Tour Coverage (MANU-06)
- Walk method FAMILIES (mirroring the Phase 87 comparison dimensions), one minimal snippet per family, so the tour visibly spans the breadth: represent/basis/smoothing, alignment, depth/outliers, FPCA (+ sparse PACE), clustering, classification, regression (SoF/FoF), functional time series, SPM, conformal/tolerance, density/Fréchet/metric, plus the advisor (grounded parameter guidance) and provenance. Not every one of 30 submodules — one representative per family, breadth-first. Cite the comparison table (Phase 87) and coverage macros (Phase 86) for the honest breadth claim.
- Prefer datasets already in `docs/data/` via `paper_utils.data_path()`; keep snippets fast and deterministic.

### Front Matter & Statement of Need (MANU-02, MANU-03)
- Abstract: concise, positions fdars as a broad, method-accurate, Rust-accelerated, sklearn-compatible Python FDA library with a grounded advisor + provenance layer. No benchmark claims.
- Introduction & statement of need: frame the Python FDA gap (scikit-fda strong but narrower; R ecosystem fragmented across packages; no single Python library spanning the surface with provenance + advisor) — grounded in the Phase 87 evidence, honest, no over-claim.
- FDA-background section: brief, cite canonical references (Ramsay & Silverman etc. from refs.bib).

### Design / Architecture & Advisor-Provenance sections (MANU-04)
- Qualitative architecture (NO benchmarks per milestone lock): Rust `fdars-core` + PyO3 zero-copy boundary, row-major↔column-major conversion, module map, the `Fdata` container, and the sklearn-estimator layer (28 estimators passing check_estimator — cite honestly).
- A SEPARATE contribution section presents the grounded AI advisor + scientific-provenance layer (references map, MCP tool) as a differentiator absent from peer FDA packages — the milestone's dedicated advisor/provenance section.

### Data Representation section (MANU-05)
- Explain `Fdata`, argvals/grids, rangeval, and irregular/sparse representation (`IrregFdata` if present in the API — verify during research). Small executed snippet.

### Availability & Conclusion (MANU-07)
- PyPI install, `plot` extra, Python 3.9–3.14, license; a short Conclusion (breadth + provenance + roadmap-agnostic framing; JOSS/JSS venues are deferred VENUE items — do not promise them).

### Claude's Discretion
Section ordering within the manuscript, exact prose wording/length, snippet selection per family, and the listings styling are at the planner/executor's discretion, provided: every snippet is executed-script-sourced, all numbers are macro-derived (no hardcoded integers), and prose does not over-claim (peer-review-safe, grounded in the evidence/comparison artifacts).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Section stubs (Phase 85): intro/design/represent/capabilities/availability + casestudies (Phase 89) + comparison (Phase 87, done).
- `paper/code/paper_utils.py` (`fig`, `data_path`, `save_figure`) — reuse for snippet harness dataset access.
- Coverage macros (`coverage_counts.tex`) + `refs.bib` (Phase 86), comparison table (Phase 87) — cite these; never hardcode counts.
- `fdars` 0.12.0 importable in `.venv` — 30 public submodules + advisor + Fdata; sklearn estimator layer; the `fdars-capabilities` / `fdars-advisor` skills document the surface.
- `python/fdars/_capability_map.json` (purpose/sig/when per callable) and `_references_map.json` — authoritative for accurate method descriptions + citations.

### Established Patterns
- Machine-derived numbers via macros; deterministic seeded output; CI-only tectonic; honest/under-claiming prose.
- markdown-exec live-execution pattern exists in the docs build — but the PAPER uses the executed-script→generated-.tex harness (not markdown-exec), matching the reproducible-pipeline model.

### Integration Points
- Generated snippet `.tex` files `\input`-ed by capabilities.tex (and others). Snippet generation joins `make paper`; drift check joins `make paper-check` + `paper.yml`.
- paper.yml gains a maturin/fdars install step (deferred from Phase 86).

</code_context>

<specifics>
## Specific Ideas

Milestone HIGHEST-RISK note (STATE): "stale API snippets — every .tex snippet must flow from an executed paper/code/ script (never copy-pasted); the pipeline runner is the hard local gate, re-verified at Phase 90 (GATE-02)." Honor exactly: the snippet harness + drift gate is the mechanism that makes snippets provably current against fdars 0.12.0.

</specifics>

<deferred>
## Deferred Ideas

- Case studies + figures → Phase 89.
- Citable release, arXiv ID, CI human-approval → Phase 90.
- JOSS/JSS venue drafts → VENUE-01/02 (future).
- No benchmarks (milestone lock: breadth + correctness, not performance numbers).

</deferred>
