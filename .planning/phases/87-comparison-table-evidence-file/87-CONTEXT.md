# Phase 87: Comparison Table + Evidence File - Context

**Gathered:** 2026-09-08
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous — grey areas proposed and auto-accepted with sensible defaults)

<domain>
## Phase Boundary

The highest peer-review-rejection-risk artifact — the comparison-with-related-software table — exists and is defensible, with every competitor cell backed by a version-stamped source, so the capability tour that cites it (Phase 88) can be written with confidence.

Delivers:
- `paper/comparison_evidence.md` — for each peer package (scikit-fda, FDApy, R fda / fda.usc / refund, funData / tidyfun, Matlab fdaM / PACE), a version-stamped source (package, version, URL, access date) for every claim; ≥1 peer package spot-checked against its live registry (PyPI/CRAN/arXiv).
- An `\input`-ed LaTeX comparison table (capability-dimension rows × peer-package columns) rendering in the manuscript; fdars column grounded from `python/fdars/_capability_map.json`; coverage stated honestly (✓ / partial / —).
- Every non-fdars cell traces to a claim in `comparison_evidence.md`.

Requirements: COMP-01, COMP-02.

</domain>

<decisions>
## Implementation Decisions

### Comparison Dimensions (table rows)
- Rows are capability *dimensions* grouped from the fdars submodule surface, chosen so each row is a recognizable FDA task a reviewer can check across packages (not one row per fdars submodule — that would be unfair granularity). Proposed dimension set:
  1. Representation / basis smoothing (basis, represent, smoothing)
  2. Registration / alignment (alignment)
  3. Depth & outlier detection (depth, outliers)
  4. FPCA / covariance / PACE sparse FPCA (pace_fpca, covariance)
  5. Clustering (clustering)
  6. Classification (classification, shapelet)
  7. Functional regression — scalar-on-function & function-on-function (regression, scalar_on_function, famm)
  8. Functional time series (fts)
  9. Statistical process monitoring / SPM (spm)
  10. Inference / hypothesis testing (inference)
  11. Conformal prediction & tolerance (conformal, tolerance)
  12. Density / Fréchet / metric-space methods (density_fda, frechet, metric)
  13. Simulation & datasets (simulation, datasets)
  14. Grounded parameter advisor + scientific provenance (explain / advisor + references map) — the fdars differentiator
- The planner/researcher may merge/split a row if evidence shows a fairer mapping, but must keep the advisor/provenance differentiator row.

### Peer-Package Columns
- Columns exactly as the roadmap lists: fdars, scikit-fda, FDApy, R {fda, fda.usc, refund}, funData/tidyfun, Matlab {fdaM, PACE}. Group the R and Matlab families sensibly (e.g. one "R (fda/fda.usc/refund)" column or a small cluster) — decided by the planner to keep the table readable, but every named package must appear in `comparison_evidence.md`.

### Coverage Rubric
- Three honest states per cell: `✓` (first-class documented support), `partial` (possible but limited / indirect / requires user glue), `—` (no support found). Ambiguity resolves DOWN (prefer `partial` over `✓`, `—` over `partial`) — under-claiming for fdars and not over-claiming against peers is the peer-review-safe bias.
- The fdars column is derived from `_capability_map.json` (a dimension is `✓` only if a public callable exists for it), never asserted.

### Evidence Standard
- Every non-fdars cell → a claim line in `comparison_evidence.md` with: package, version, source URL, access date (2026-09-08), and a one-line justification. No cell may be filled from memory.
- Spot-check ≥1 peer package against its live registry: minimum scikit-fda on PyPI AND R fda.usc on CRAN (two spot-checks for safety). Record the checked version + date.
- Where a capability is genuinely uncertain for a peer package, mark `partial` or `—` with an explicit "not found in <source>" note rather than guessing.

### Claude's Discretion
Exact table column grouping, row ordering, and LaTeX table environment (e.g. `tabular`/`booktabs`) are at the planner's discretion, provided the table `\input`s cleanly into `paper.tex` and traces every cell to evidence.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/_capability_map.json` — 31 top-level keys (30 public submodules + `_Fdata`) = the ground truth for the fdars column.
- `python/fdars/_references_map.json` — the provenance backing the advisor/provenance differentiator row.
- Phase 86 machinery (`coverage_counts.tex`, `refs.bib`, `make paper`, `paper.yml`) — the comparison table `\input`s alongside these; if the table cites counts, use the coverage macros, not literals.

### Established Patterns
- Machine-derived numbers via macros; honest coverage marking; no hardcoded integers in `.tex`.

### Integration Points
- The comparison table file is `\input`-ed by `paper/paper.tex` (into `sections/comparison.tex`, stubbed in Phase 85).
- Phase 88's capability tour cites this table; Phase 90 human review spot-checks the peer cells (reviewer-rejection gate).

</code_context>

<specifics>
## Specific Ideas

Milestone risk note (STATE): "inaccurate peer-comparison rows — reviewer-rejection risk: ground every competitor cell in comparison_evidence.md (URL + version + date); ≥1 peer package spot-checked; blocking human review at Phase 90." Honor this exactly: the evidence file is the defensibility artifact.

</specifics>

<deferred>
## Deferred Ideas

None — stays within the comparison-table scope. (Benchmark/performance comparisons are explicitly OUT — the milestone is breadth+correctness, not benchmarks.)

</deferred>
