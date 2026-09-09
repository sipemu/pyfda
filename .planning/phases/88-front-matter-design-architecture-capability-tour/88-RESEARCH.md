# Phase 88: Front Matter, Design/Architecture & Capability Tour - Research

**Researched:** 2026-09-09
**Domain:** Reproducible-snippet LaTeX pipeline (executed-script → `.tex` fragment) + fdars 0.12.0 public API inventory per method family
**Confidence:** HIGH (every snippet below was RUN against fdars 0.12.0 in `.venv` this session; architecture facts read from source; counts machine-derived from committed maps)

---

## Summary

Phase 88 writes the experiment-free prose of the arXiv paper (intro/statement of need, FDA background, design/architecture, data representation, capability tour, advisor+provenance contribution, availability, conclusion) plus the machinery that makes the capability tour provably current: an **executed-snippet harness** under `paper/code/` that runs real fdars code and emits LaTeX fragments (source + captured output) into `paper/snippets/*.tex`, which the manuscript `\input`s. This mirrors the Phase 86 macro pattern (generate → `--check` drift gate → CI) already proven for `coverage_counts.tex` and `refs.bib`.

The two make-or-break research outputs are delivered here: **(a)** a concrete harness design using LaTeX `listings` (no `-shell-escape`/pygments dependency, so tectonic CI stays simple), with a `--check` drift mode identical in shape to `assert_coverage.py --check`; and **(b)** a **validated minimal snippet per method family** — every snippet in the "Validated Snippets" section was executed this session and its captured output recorded. Two family calls have API-shape gotchas that the planner MUST heed (documented inline): module-level `depth.fraiman_muniz_1d` requires **contiguous float64** arrays and classification labels must be **int64** ndarrays (not lists, not uint32); `spm_monitor` takes **unpacked** phase-1 components, not the result dict; `ftsm_forecast` takes **raw data + argvals**, not a fitted model.

**Primary recommendation:** Build one `paper/code/gen_snippets.py` harness module exposing a `snippet(name, source_code, *, seed=None)` runner that `exec`s the source in a fresh namespace, captures stdout, and writes a deterministic `paper/snippets/<name>.tex` `lstlisting` fragment (source block + a commented output block). Author one runnable tour script per family (or a single `tour.py` with one function per family) that calls the runner. Wire `gen_snippets.py` into `make paper` and `gen_snippets.py --check` into `make paper-check` + `paper.yml`. Add a `maturin develop` step to `paper.yml` (mirroring `ci.yml`) so the snippet check runs against the compiled `fdars`.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Snippet-Sourcing Mechanism (MANU-06 — the critical constraint):**
- Every capability-tour snippet MUST come from an EXECUTED `paper/code/` script — never hand-copied.
- Author runnable Python scripts under `paper/code/` (e.g. `snippets/` or `tour_*.py`) that emit LaTeX `lstlisting`/`verbatim` fragments capturing BOTH source snippet and real captured output into generated `.tex` files under `paper/` (e.g. `paper/snippets/*.tex`), which the manuscript `\input`s.
- Small stdlib+fdars snippet harness in `paper/code/` (reuse `paper_utils` conventions); runs a snippet, captures stdout/result, writes fragment deterministically (seeded; no timestamps).
- Wire snippet generation into `make paper` and a `--check` drift gate into `make paper-check` + `paper.yml`.
- `paper.yml` now needs `fdars` installed (maturin develop / pip install) — Phase 86 deferred this; Phase 88 adds the maturin step.
- Snippets show INPUT and, where illustrative, captured OUTPUT (repr/print). Keep each minimal — breadth over depth.
- Use LaTeX `listings` (or `minted` only if CI toolchain supports it — **prefer `listings`** to avoid a `-shell-escape`/pygments CI dependency).

**Capability Tour Coverage (MANU-06):**
- Walk method FAMILIES (mirroring Phase 87 comparison dimensions), one minimal snippet per family: represent/basis/smoothing, alignment, depth/outliers, FPCA (+ sparse PACE), clustering, classification, regression (SoF/FoF), functional time series, SPM, conformal/tolerance, density/Fréchet/metric, plus the advisor (grounded parameter guidance) and provenance. One representative per family, breadth-first. Cite the comparison table (Phase 87) and coverage macros (Phase 86) for the honest breadth claim.
- Prefer datasets already in `docs/data/` via `paper_utils.data_path()`; keep snippets fast and deterministic.

**Front Matter & Statement of Need (MANU-02, MANU-03):**
- Abstract: concise; positions fdars as broad, method-accurate, Rust-accelerated, sklearn-compatible Python FDA library with grounded advisor + provenance layer. No benchmark claims.
- Introduction/statement of need: frame the Python FDA gap (scikit-fda strong but narrower; R ecosystem fragmented; no single Python library spanning the surface with provenance + advisor) — grounded in Phase 87 evidence, honest, no over-claim.
- FDA-background: brief; cite canonical references (Ramsay & Silverman etc. from refs.bib).

**Design/Architecture & Advisor-Provenance sections (MANU-04):**
- Qualitative architecture (NO benchmarks per milestone lock): Rust `fdars-core` + PyO3 zero-copy boundary, row-major↔column-major conversion, module map, `Fdata` container, sklearn-estimator layer (28 estimators passing check_estimator — cite honestly).
- SEPARATE contribution section presents the grounded AI advisor + scientific-provenance layer (references map, MCP tool) as a differentiator absent from peer FDA packages.

**Data Representation section (MANU-05):**
- Explain `Fdata`, argvals/grids, rangeval, and irregular/sparse representation (`IrregFdata` if present — verify during research). Small executed snippet.

**Availability & Conclusion (MANU-07):**
- PyPI install, `plot` extra, Python 3.9–3.14, license; short Conclusion (breadth + provenance + roadmap-agnostic; JOSS/JSS venues are deferred VENUE items — do not promise them).

### Claude's Discretion
Section ordering within manuscript, exact prose wording/length, snippet selection per family, and listings styling — provided: every snippet is executed-script-sourced, all numbers are macro-derived (no hardcoded integers), prose does not over-claim (peer-review-safe, grounded in evidence/comparison artifacts).

### Deferred Ideas (OUT OF SCOPE)
- Case studies + figures → Phase 89.
- Citable release, arXiv ID, CI human-approval → Phase 90.
- JOSS/JSS venue drafts → VENUE-01/02 (future).
- No benchmarks (milestone lock: breadth + correctness, not performance numbers).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MANU-02 | Front matter — Abstract, Introduction & statement of need (Python FDA gap), brief FDA-background | Statement-of-need framing from Phase 87 evidence (§Statement-of-Need Facts); canonical refs available in `refs.bib` / `_references_map.json` |
| MANU-03 | Software design & architecture — Rust core + PyO3 zero-copy, module map, `Fdata` container, sklearn estimator layer (qualitative) | §Architecture Facts (convert.rs read; 27 native `_mod.rs`; 30 public submodules; 28 sklearn estimators PASS) |
| MANU-04 | Data-representation model — `Fdata`, argvals/grids, irregular/sparse (`IrregFdata`) | §Data Model Facts (`Fdata` verified; irregular = `pace_fpca.PyIrregFdata` + `irreg_fdata_from_lists`; NO top-level `IrregFdata`) |
| MANU-05 | Capability tour by method family, minimal runnable snippets each sourced from an executed `paper/code/` script | §Validated Snippets (13 families, each RUN this session) + §Harness Design |
| MANU-06 | Dedicated section: grounded AI advisor + scientific-provenance layer as novel contribution absent from peers | §Advisor + Provenance Facts (public surface: `fdars.advisor.advise/auto_tune/build_diagnostics`; `_references_map.json` 57 papers / 243 callable_index / 6 curated; MCP tool `fdars_method_references`) |
| MANU-07 | Availability & installation (PyPI, extras, Python 3.9–3.14) + Conclusion | §Availability Facts (CLAUDE.md + ci.yml: Python 3.9–3.14, `plot` extra, PyPI wheels) |

> **Note on the MANU numbering discrepancy:** REQUIREMENTS.md maps MANU-02..MANU-07 to Phase 88, but the requirement *text* for MANU-04/05/06 is offset by one from the CONTEXT.md prose descriptions (REQUIREMENTS MANU-04 = data representation; CONTEXT lists MANU-05 = data representation). The planner should treat the CONTEXT.md section descriptions as authoritative for what to write and the REQUIREMENTS.md IDs (MANU-02 through MANU-07) as the set to satisfy. All six requirements are covered by the sections below regardless of the exact ID↔section pairing.
</phase_requirements>

---

## Architectural Responsibility Map

This phase produces documentation artifacts (LaTeX prose + generated `.tex` snippet fragments) plus one new Python harness script and a CI-workflow edit. No runtime-code tier assignment risk.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Snippet harness (`gen_snippets.py`) | `paper/code/` Python pipeline | reuses `paper_utils.data_path` | Runs fdars, captures output, writes `.tex` — same tier as `gen_figures.py`/`assert_coverage.py` |
| Generated snippet fragments | `paper/snippets/*.tex` (generated artifacts) | `\input`-ed by `sections/capabilities.tex` | Machine-generated; committed; drift-gated |
| Prose sections | `paper/sections/*.tex` | `paper.tex` (`\input`) | Hand-authored; stubs already exist from Phase 85 |
| fdars API grounding | `python/fdars/` (read-only) + `.venv` runtime | `_capability_map.json`, `_references_map.json` | Ground-truth; no new bindings (milestone lock) |
| `paper.yml` maturin step | `.github/workflows/paper.yml` | mirrors `ci.yml` build | Compiled `fdars` needed for snippet `--check` |

---

## Harness Design (the make-or-break mechanism)

### Decision: `listings`, not `minted`

Use LaTeX **`listings`** for the code fragments.

- `listings` is pure-TeX (no external tool), so tectonic compiles it with **no `-shell-escape`** and **no Python/pygments dependency** in CI. `minted` requires `-shell-escape` + a `pygmentize` binary — a CI toolchain risk the CONTEXT.md explicitly wants to avoid.
- `listings` ships in every TeX distribution (TeX Live base). tectonic fetches it from its bundle on first build automatically — same mechanism that will pull `booktabs`/`adjustbox` already used by Phase 87. `[CITED: listings is a core CTAN/TeX Live package]`
- Add `\usepackage{listings}` to `paper/paper.tex` preamble (currently absent — see Pitfall 1).

**Confidence:** HIGH that `listings` avoids the pygments/`-shell-escape` dependency. MEDIUM that tectonic bundles `listings` by default — it bundles a very large TeX Live subset and `listings` is a base package, but the planner should include a CI smoke check (a one-listing dummy build) the first time `paper.yml` compiles a snippet, exactly as Phase 87 recommended for `adjustbox`.

### Fragment shape (source + captured output in one `.tex`)

Each generated `paper/snippets/<name>.tex` contains a source `lstlisting` and, when illustrative, a captured-output `lstlisting`. Example generated fragment:

```latex
% AUTO-GENERATED by paper/code/gen_snippets.py — do not edit.
\begin{lstlisting}[language=Python,style=fdarsinput]
import numpy as np, pandas as pd
from fdars import Fdata
growth = pd.read_csv("docs/data/growth.csv", index_col=0)
fd = Fdata(growth.values.T, argvals=growth.index.values.astype(float))
print(repr(fd))
\end{lstlisting}
\begin{lstlisting}[style=fdarsoutput]
Fdata (1D)  –  93 obs × 31 points  –  range [1.0, 18.0]
\end{lstlisting}
```

The `lstdefinestyle` blocks (`fdarsinput`, `fdarsoutput`) live once in `paper.tex` preamble (input = boxed monospace with Python keywords; output = plain monospace, `basicstyle=\ttfamily\small`, no highlighting). `capabilities.tex` then does `\input{snippets/represent}` etc.

### Determinism rules (no drift on re-run)

1. **No timestamps** anywhere in the generated `.tex` (the auto-generated banner is static text, no date — same as `coverage_counts.tex`).
2. **Seed every stochastic call.** Any snippet whose fdars call takes a `seed=` param passes a fixed seed (most default to `seed=42`); any snippet using `np.random` seeds `np.random.seed(<fixed>)` before the draw. (Mirrors `gen_figures.py` per-figure seeding.)
3. **Stable float formatting.** Captured `repr`/`print` output can vary in trailing digits across platforms. The harness should format captured floats through a fixed formatter (e.g. round-to-`n` via `np.round` in the snippet itself, or a `np.set_printoptions(precision=4, suppress=True)` set at snippet-namespace top). **Prefer printing rounded values or shapes/keys rather than raw float arrays** — the validated snippets below print shapes, dict keys, counts, and single rounded scalars precisely to keep output byte-stable. This is the residual determinism risk (same class as FreeType font variance for figures); the CI determinism gate (empty `git diff paper/snippets/`) catches it.
4. **Fixed dict/array ordering.** Python dict insertion order is stable; fdars result dicts return in a fixed key order (verified in snippets below). Print `list(result.keys())` deterministically.
5. **Line endings / trailing newline.** Write with a single trailing `\n`, `utf-8`, LF — same as `assert_coverage.py:_render`.

### `--check` drift mode (mirror `assert_coverage.py`)

`gen_snippets.py` supports two modes, identical in shape to the proven `assert_coverage.py`:

- **Generate mode** (default): run each snippet, write `paper/snippets/<name>.tex`.
- **`--check` mode**: regenerate each fragment into memory, compare byte-for-byte against the committed file; if any differs or is missing, print `DRIFT: <path> is stale — re-run gen_snippets.py and commit.` to stderr and `sys.exit(1)`. On success print `gen_snippets: OK (no drift)`.

This is the hard local gate that makes stale API snippets impossible: if fdars 0.12.0's API changes, the regenerated output diverges from the committed `.tex` and CI fails. Re-verified at Phase 90 GATE-02.

### Reference implementation sketch

```python
# paper/code/gen_snippets.py
"""Generate or check paper/snippets/*.tex from executed fdars snippets.

Each snippet runs REAL fdars code against a docs/data/ dataset, captures its
stdout, and emits a deterministic lstlisting fragment (source + output).

Usage:
    python paper/code/gen_snippets.py           # generate
    python paper/code/gen_snippets.py --check    # drift gate (exit 1 on stale)

Requires a compiled fdars (maturin develop) on PYTHONPATH.
"""
from __future__ import annotations

import io
import sys
import textwrap
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

_SNIPPETS_DIR = Path(__file__).resolve().parent.parent / "snippets"
_BANNER = "% AUTO-GENERATED by paper/code/gen_snippets.py — do not edit."


def _run(source: str) -> str:
    """Exec *source* in a fresh namespace, return captured stdout verbatim."""
    ns: dict = {}
    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(compile(textwrap.dedent(source), "<snippet>", "exec"), ns)  # noqa: S102
    return buf.getvalue()


def _render(source: str, output: str) -> str:
    src = textwrap.dedent(source).strip("\n")
    lines = [
        _BANNER,
        r"\begin{lstlisting}[language=Python,style=fdarsinput]",
        src,
        r"\end{lstlisting}",
    ]
    if output.strip():
        lines += [
            r"\begin{lstlisting}[style=fdarsoutput]",
            output.rstrip("\n"),
            r"\end{lstlisting}",
        ]
    return "\n".join(lines) + "\n"


# Each entry: (name, source-code-string). The source string is what the reader
# sees AND what actually runs — single source of truth. Keep imports inside so
# each fragment is self-contained and copy-pasteable by a reader.
SNIPPETS: list[tuple[str, str]] = [
    ("represent", '''
        import numpy as np, pandas as pd
        from fdars import Fdata
        growth = pd.read_csv("docs/data/growth.csv", index_col=0)
        fd = Fdata(growth.values.T, argvals=growth.index.values.astype(float))
        print(repr(fd))
    '''),
    # ... one entry per family (see §Validated Snippets for the exact bodies)
]


def main() -> None:
    check = "--check" in sys.argv
    _SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, source in SNIPPETS:
        out = _run(source)
        content = _render(source, out)
        target = _SNIPPETS_DIR / f"{name}.tex"
        if check:
            if not target.exists() or target.read_text() != content:
                stale.append(str(target))
        else:
            target.write_text(content)
    if check:
        if stale:
            print("DRIFT: stale/missing snippets — re-run gen_snippets.py and commit:",
                  file=sys.stderr)
            for s in stale:
                print(f"  {s}", file=sys.stderr)
            sys.exit(1)
        print("gen_snippets: OK (no drift)")
    else:
        print(f"Wrote {len(SNIPPETS)} snippet fragments to {_SNIPPETS_DIR}")


if __name__ == "__main__":
    main()
```

**Note on `data_path` vs literal path:** the sketch prints `"docs/data/growth.csv"` as a literal in the reader-facing source for clarity, but the harness runs from repo root under `PYTHONPATH=scripts:paper/code`. If the snippet is exec'd with cwd = repo root, the literal relative path works. Safer: the harness can inject `data_path` into the exec namespace and the reader-facing snippet uses `data_path("growth.csv")` (matches `paper_utils` convention). **Planner decides** — the CONTEXT prefers `paper_utils.data_path()`. Recommendation: inject `from paper_utils import data_path` availability and write snippets using `data_path("growth.csv")` so they are robust to cwd and consistent with the figure pipeline; the reader still sees a clean, honest call.

---

## Data Model Facts (MANU-05)

All verified by importing fdars 0.12.0 in `.venv` this session.

- **`Fdata` constructor** `[VERIFIED: fdars 0.12.0 runtime + _capability_map.json:5]`:
  `Fdata(data, argvals=None, rangeval=None, names: Optional[Dict[str,str]]=None, id: Optional[Sequence[str]]=None, metadata=None)`
- **Row convention:** `data` is `(n_obs, n_points)` — observations are rows. Verified: growth `(93 obs, 31 points)` built from `growth.values.T` (CSV is timepoints×subjects, so transpose). `[VERIFIED: runtime — repr "93 obs × 31 points"]`
- **Key properties** `[VERIFIED: runtime]`: `n_obs`, `n_points`, `rangeval` (tuple, e.g. `(1.0, 18.0)`), plus `data`, `argvals`, `id`, `metadata` (per CLAUDE.md). Methods incl. `mean()`, `center()`, `depth()`, `to_pc()`, `to_basis()`, `distance()`, `norm()`, `deriv()`, `cov()`, `std()`, `var()`, `median()`, `geometric_median()`, `impute()`, `interpolate()`, `resample()`, `downsample()`, `upsample()`, `shift_register()`, `concat()`, `stack()` `[VERIFIED: _capability_map.json:1-118]`
- **`repr`:** `Fdata (1D)  –  93 obs × 31 points  –  range [1.0, 18.0]` (and appends `– metadata: id, sex` when metadata present). Note the repr uses en-dashes `–` and `×` — the harness must handle UTF-8 (paper.tex already loads `inputenc utf8`; `listings` prints it fine as `\ttfamily`).

### IrregFdata / sparse representation — the MANU-05 answer

- **There is NO top-level `fdars.IrregFdata`** and no `fdata.IrregFdata`. `[VERIFIED: runtime — hasattr checks all False]`
- **The irregular/sparse representation is `fdars.pace_fpca.PyIrregFdata`**, constructed via `fdars.pace_fpca.irreg_fdata_from_lists(argvals_list, values_list)` — a list of per-observation grids and a list of per-observation values (ragged). `[VERIFIED: runtime — sig (argvals_list, values_list); returns builtins.PyIrregFdata]`
- This feeds **`fdars.pace_fpca.pace_fpca(data, ncomp=3, bandwidth=0.1, sigma2=0.01, work_grid=None, alpha=0.05)`** — the sparse/longitudinal FPCA (PACE) that the comparison table row 4 grounds. `[VERIFIED: runtime]`

**MANU-05 prose guidance:** Describe the dense representation as `Fdata` (regular grid, `(n_obs, n_points)` matrix + shared `argvals`). Describe the irregular/sparse case honestly as the **`PyIrregFdata` container fed to PACE FPCA** (per-curve grids of differing length) — do NOT call it `IrregFdata` in prose; the public name is `PyIrregFdata` and the constructor is `irreg_fdata_from_lists`. This is a genuine differentiator vs scikit-fda (dense FPCA only).

---

## Architecture Facts (MANU-03/MANU-04, qualitative — NO benchmarks)

All read from source or machine-derived this session.

- **Rust core + PyO3 zero-copy boundary.** `src/convert.rs` read directly `[VERIFIED: src/convert.rs:26-58]`:
  - `numpy2d_to_fdmatrix` (lines 30-43): NumPy `(n_obs, n_points)` in **C order (row-major)** → `FdMatrix` **column-major** (`nrows=n_obs, ncols=n_points`); explicit transpose loop `col_major[i + j*nrows] = arr_ref[[i,j]]`.
  - `fdmatrix_to_numpy2d` (lines 45-58): reverse, `mat.to_row_major()` → numpy `(n_obs, n_points)`.
  - This is the row-major↔column-major conversion the paper describes. Quote the exact doc-comment: *"Convert a numpy 2D array (row-major) to FdMatrix (column-major). NumPy shape: (n_obs, n_points) in C order (row-major). FdMatrix: column-major with nrows=n_obs, ncols=n_points."* `[VERIFIED: src/convert.rs:26-29]`
  - **Honest nuance:** the boundary is not literally zero-copy for 2D matrices (there is an explicit element-by-element layout conversion). It IS zero-GIL-contention / read-only via `PyReadonlyArray` wrappers (per CLAUDE.md "PyReadonly wrappers avoid GIL contention"). **Prose should say "read-only NumPy views (`PyReadonlyArray`) with a row-major↔column-major layout conversion at the boundary"** rather than claiming byte-for-byte zero-copy for the matrix path. CLAUDE.md itself lists "NumPy Layout Conversion Overhead" as a known anti-pattern — the paper should be accurate here to survive review.
- **Native module map:** **27** Rust binding files `src/*_mod.rs` `[VERIFIED: filesystem — ls src/*_mod.rs | wc -l = 27]`: alignment, basis, classification, clustering, conformal, density_fda, depth, explain, famm, fdata, frechet, fts, inference, metric, multi_fdata, outliers, pace_fpca, regression, represent, scalar_on_function, scoring, seasonal, shapelet, simulation, smoothing, spm, tolerance.
- **Public Python submodules:** **30** `[VERIFIED: coverage_counts.tex \nsubmodules=30 + runtime import]` (native modules + pure-Python layers like `metrics`, `covariance`, `datasets`, `plot`, `advisor`, `sklearn`, `results`, `multi_fdata`). Full runtime `dir(fdars)` non-underscore: Fdata, advisor, alignment, basis, classification, clustering, conformal, covariance, datasets, density_fda, depth, explain, famm, fdata, fdata_class, frechet, fts, inference, metric, metrics, multi_fdata, outliers, pace_fpca, plot, regression, represent, results, scalar_on_function, scoring, seasonal, shapelet, simulation, smoothing, spm, tolerance.
- **Machine-derived counts (use the macros, DO NOT hardcode)** `[VERIFIED: paper/coverage_counts.tex]`:
  - `\nsubmodules` = 30, `\npubliccallables` = 409, `\ncallables` = 437, `\nfdata` = 27, `\ncoverage` = 28, `\ndocpapers` = 47.
  - Prose must reference these via `\input{coverage_counts}` macros (already `\input`-ed in `paper.tex`), never literal integers.
- **`Fdata` container** — see §Data Model Facts.
- **sklearn estimator layer:** **28 estimators, ALL verdict `PASS`** (i.e. pass `check_estimator`) `[VERIFIED: fdars.sklearn.TRIAGE_VERDICTS — 28 entries all "PASS"]`. The 28: FPCATransformer, BSplineSmoother, LocalPolynomialSmoother, BasisRepresentation, Imputer, SplineInterpolator, DepthTransformer, NormTransformer, FPCRegressor, PLSRegressor, RobustFPCRegressor, GLMRegressor, NonparametricRegressor, FPCLDAClassifier, FPCQDAClassifier, FPCKNNClassifier, DDClassifier, LogisticFPCClassifier, ElasticMultinomialClassifier, FunctionalKMeans, FuzzyFunctionalCMeans, FunctionalGMM, LRTOutlierDetector, OutliergramDetector, MagnitudeShapeDetector, TVDMSSDetector, MUODDetector, DepthgramDetector.
  - **28 == `\ncoverage`** — the coverage-count macro (`\ncoverage`=28) equals the sklearn PASS count. Confirm which the paper means: `\ncoverage` in `assert_coverage.py` is "callables backed by ≥1 curated paper", NOT sklearn estimators — a **coincidental collision at 28**. Do NOT conflate them in prose. The sklearn "28 estimators pass check_estimator" is a separate fact; if the paper wants a machine-derived sklearn count it needs a NEW macro (e.g. `\nsklearnestimators` from `len(TRIAGE_VERDICTS)` where verdict=="PASS"). **Recommendation:** planner adds a `\nsklearnestimators` macro to `assert_coverage.py` derived from `fdars.sklearn.TRIAGE_VERDICTS`, so the sklearn count is also machine-derived and not a hardcoded `28` that silently drifts.
  - **13 methods EXCLUDED** from the sklearn layer (`fdars.sklearn.EXCLUDED_METHODS`, len 13) — e.g. `alignment.elastic_align_pair`, `alignment.karcher_mean`, `pace_fpca.pace_fpca`, `regression.functional_glm_binomial` — because they don't fit the stateless fit/transform contract. Mention honestly if the paper discusses coverage.
  - Estimator classes live in `fdars.sklearn._skeletons` (importable: `from fdars.sklearn._skeletons import FPCATransformer, FPCRegressor, ...`). They are NOT re-exported at `fdars.sklearn` top level in 0.12.0 — the public `__all__` is `['_BaseFdarsEstimator', 'EXCLUDED_METHODS', 'TRIAGE_VERDICTS']`. The sklearn Pipeline snippet below imports from `fdars.sklearn._skeletons`. `[VERIFIED: runtime]`

---

## Advisor + Provenance Facts (MANU-04 contribution section)

- **`fdars.advisor` is a module** (not a callable) `[VERIFIED: runtime — type(fdars.advisor) == module]`. Public surface `[VERIFIED: runtime dir()]`: `advise`, `auto_tune`, `build_diagnostics`, `build_pipeline_report`, `compare_methods`, `describe_cluster_differences`, `pipeline_report`, plus dataclasses `Advice`, `Recommendation`, `PipelineReport`, and version-floor constants `ADVISOR_ANTHROPIC_MIN_VERSION`, `ADVISOR_OPENAI_MIN_VERSION`, `ADVISOR_OLLAMA_MIN_VERSION`.
  - **`advise(diagnostics, *, task, domain_context, model='claude-opus-4-8', provider=None, aspect='') -> Advice`** — the grounded-parameter-advisor entry point. It takes a **diagnostics dict** (not raw data) and calls an LLM provider. `[VERIFIED: runtime signature]`
  - **`build_diagnostics(result, method, *, argvals=None, n_classes=None, holdout_accuracy=None, **kwargs) -> dict`** — the **LLM-free** grounding step: turns a method result dict into a structured diagnostics dict. Supported methods `[VERIFIED: runtime error message]`: `alignment, basis, classification, clustering, depth, fpca, frechet, fts, inference, outliers, regression, regression_cv, represent, scoring, smoothing, spm`. **This is the snippet to show for the advisor** (see Validated Snippets) — it runs offline, deterministically, no API key.
  - `auto_tune(dataset_id, method, *, target_metric=None, max_steps=10, ..., guard=True, ...)` — closed-loop parameter search with a grounding guard (the "advisor grounding guard" from MEMORY.md). Document its signature; do not run it in a snippet (needs LLM + guard).
- **Scientific provenance = `_references_map.json`** `[VERIFIED: python/fdars/_references_map.json read this session]`:
  - Top-level keys: `papers`, `callable_index`.
  - **57 papers** total (`len(refs["papers"])`); **6 curated** (`curated is True`); `callable_index` has **243 entries** (callable → paper-key list). `[VERIFIED: runtime json load]`
  - Macros already available: `\ndocpapers`=47 (non-`_uncurated` papers eligible for refs.bib), `\ncoverage`=28 (callables backed by ≥1 curated paper). Use these, not the raw 57/6/243.
  - Each paper entry has: title, authors (list), year, doi/url, type, `callables` (list), `cross_language` (R/Python/Matlab equivalents with confidence), `notes`, `curated` (bool). Example: `fraiman_muniz_2001` maps to `depth.fraiman_muniz_1d/2d`, `_Fdata.depth`, with R `fda.usc::depth.FM` and Python `scikit-fda fraiman_muniz_depth` cross-refs.
- **MCP tool `fdars_method_references`** — the LLM-free provenance query tool (from v13.0 milestone, MEMORY.md). Cite as the provenance-serving surface; it reads `_references_map.json`. `[CITED: MEMORY.md v13.0 state; docs/llms.txt]`
- **The differentiator claim (peer-review-safe):** No peer FDA package (scikit-fda, FDApy, R fda/fda.usc/refund, funData/tidyfun, Matlab fdaM/PACE) provides a grounded parameter advisor OR a machine-readable scientific-provenance layer — confirmed in Phase 87 evidence dossiers (row 14 = ✓ only for fdars). Frame the advisor + provenance as the novel contribution absent from all peers. Ground the "absent from peers" claim in `paper/comparison_evidence.md` (already written, Phase 87), NOT from memory.

---

## Statement-of-Need Facts (MANU-02) — grounded in Phase 87 evidence

Reuse Phase 87 RESEARCH.md / `comparison_evidence.md` (do NOT re-assert from memory):

- **scikit-fda** (Python peer, v0.10.1, arXiv:2211.02566): strong on representation/basis/smoothing, registration, depth, dense FPCA, clustering, classification, scalar-on-function regression, datasets; **lacks** FTS, SPM, conformal, density/Fréchet, sparse PACE (partial FPCA), advisor/provenance. The nearest Python peer but narrower.
- **FDApy** (v1.0.3): representation + (M)FPCA + simulation only; narrow.
- **R ecosystem fragmented:** fda (representation/FPCA/registration), fda.usc (depth/classification/SoF regression), refund (SoF/FoF/FPCA), funData/tidyfun (infrastructure) — no single R package spans the surface.
- **Matlab fdaM/PACE:** partially maintained (fdaM ~2014), narrower.
- **fdars position:** the only Python library spanning all 14 comparison dimensions (Phase 87 table) WITH sklearn compatibility AND a grounded advisor + scientific provenance. State breadth honestly via `\nsubmodules`/`\npubliccallables` macros; cite `Table~\ref{tab:comparison}` (Phase 87). NO benchmark claims (milestone lock).
- **FDA background:** cite canonical Ramsay & Silverman (2005) *Functional Data Analysis* + method-family papers already in `_references_map.json`/`refs.bib`. Keep brief.

---

## Validated Snippets (one per capability-tour family)

**Every snippet below was executed against fdars 0.12.0 in `.venv` this session and its output captured.** These are the ground-truth call shapes for `gen_snippets.py`. Datasets from `docs/data/`. Confidence HIGH unless noted. `[VERIFIED: fdars 0.12.0 runtime]` applies to all unless marked otherwise.

**Shared setup convention** (each generated snippet re-imports for self-containment):
```python
import numpy as np, pandas as pd
from fdars import Fdata
import fdars
growth = pd.read_csv("docs/data/growth.csv", index_col=0)
ARG = growth.index.values.astype(float)              # ages 1.0 .. 18.0, len 31
X   = growth.values.T.astype(np.float64)             # (93 obs, 31 points) — MUST be float64 & contiguous
```

### 1. Represent (data model)
```python
fd = Fdata(X, argvals=ARG, names={"x": "Age (years)", "y": "Height (cm)"})
print(repr(fd))
print("mean shape:", fd.mean().shape)
```
Output: `Fdata (1D)  –  93 obs × 31 points  –  range [1.0, 18.0]` / `mean shape: (31,)`

### 2. Basis / smoothing
```python
res = fdars.basis.fdata_to_basis_1d(X[:5], ARG, n_basis=8, basis_type="bspline")
coefs, nbasis = res            # returns a (coefs, nbasis) TUPLE, not a dict
print("coefficients shape:", coefs.shape, "| n_basis:", nbasis)
sm = fdars.basis.smooth_basis_gcv(X[:5], ARG, n_basis=8, basis_type="bspline")
print("smoothing keys:", list(sm.keys()))
print("fitted shape:", sm["fitted"].shape)
```
Output: `coefficients shape: (5, 8) | n_basis: 8` / `smoothing keys: ['fitted', 'coefficients', 'edf', 'gcv', 'aic', 'bic', 'nbasis']` / `fitted shape: (5, 31)`
**GOTCHA:** `fdata_to_basis_1d` returns a `(ndarray, int)` **tuple**; `smooth_basis_gcv` returns a **dict**. Signature: `fdata_to_basis_1d(data, argvals, n_basis, basis_type='bspline')`; `smooth_basis_gcv(data, argvals, n_basis, basis_type='bspline', lfd_order=2, log_lambda_min=..., log_lambda_max=4.0, n_grid=25)`.

### 3. Depth & outliers
```python
fd = Fdata(X, argvals=ARG)
depths = fd.depth(method="fraiman_muniz")         # via Fdata method — robust
print("depths shape:", depths.shape, "| most central obs:", int(np.argmax(depths)))
out = fdars.outliers.muod(X)                       # muod(data, factor=1.5) — NO argvals
print("shape outliers:", out["shape_outliers"], "| amplitude:", out["amplitude_outliers"])
```
Output: `depths shape: (93,) | most central obs: 43` / `shape outliers: [41, 55, 70] | amplitude: [0, 28]`
**GOTCHA:** module-level `fdars.depth.fraiman_muniz_1d(data, ref_data, scale=True)` requires **both args as contiguous float64 ndarrays** — passing a non-float64 or non-contiguous array raises `'ndarray' object is not an instance of 'ndarray'` (a PyO3 dtype error). Prefer `Fdata.depth(method="fraiman_muniz")` in the snippet — cleaner and it handles the dtype. `muod(data, factor=1.5)` takes **no argvals**; keys: `shape_outliers, magnitude_outliers, amplitude_outliers, shape_index, magnitude_index, amplitude_index`.

### 4. FPCA (dense) + sparse PACE
```python
fd = Fdata(X, argvals=ARG)
pc = fd.to_pc(n_comp=3)
print("FPCA scores shape:", pc["scores"].shape, "| singular values:", np.round(pc["singular_values"], 2))

# sparse / irregular PACE FPCA
np.random.seed(42)
argvals_list = [np.sort(np.random.uniform(1, 18, np.random.randint(5, 15))).tolist() for _ in range(30)]
values_list  = [np.sin(av).tolist() for av in argvals_list]
irreg = fdars.pace_fpca.irreg_fdata_from_lists(argvals_list, values_list)
pace  = fdars.pace_fpca.pace_fpca(irreg, ncomp=2)
print("PACE scores shape:", pace["scores"].shape, "| ncomp:", pace["ncomp"])
```
Output: `FPCA scores shape: (93, 3) | singular values: [...]` (round for determinism) / `PACE scores shape: (30, 2) | ncomp: 2`
`to_pc` keys: `scores (93,3), rotation (31,3), singular_values (3,), mean (31,), centered (93,31), weights (31,)`. `pace_fpca` keys: `mean, eigenvalues, eigenfunctions, scores, fitted, fitted_lower, fitted_upper, argvals, sigma2, ncomp`. **This is the MANU-05 irregular-representation snippet too.**

### 5. Clustering
```python
km = fdars.clustering.kmeans_fd(X, ARG, k=3, seed=42)   # sig (data, argvals, k, max_iter=100, tol=1e-6, seed=42)
print("cluster sizes:", np.bincount(km["cluster"]).tolist(), "| converged:", km["converged"])
```
Output: `cluster sizes: [...] | converged: True` (keys: `cluster (93,), centers (3,31), tot_withinss, iter, converged`). Seed makes it deterministic. **Print `iter`/`converged`, not the float `tot_withinss`** (float determinism).

### 6. Classification
```python
ph = pd.read_csv("docs/data/phoneme.csv", index_col=0)
Xp = ph.values.astype(np.float64)                        # (400, 256)
labels_str = ph.index.tolist()
uniq = list(dict.fromkeys(labels_str)); lut = {l: i for i, l in enumerate(uniq)}
y = np.array([lut[l] for l in labels_str], dtype=np.int64)   # MUST be int64 ndarray
res = fdars.classification.fclassif_knn(Xp[:100], y[:100], ncomp=3, k=5)  # sig (data, labels, ncomp=3, k=5)
print("accuracy:", res["accuracy"])
```
Output: `accuracy: 0.9`
**GOTCHA:** `fclassif_knn(data, labels, ncomp=3, k=5)` takes **NO argvals**; `labels` MUST be an **int64 ndarray** — a Python list raises `'list' object is not an instance of 'ndarray'`, and **uint32 also fails** (`'ndarray' object is not an instance of 'ndarray'`). Keys: `predicted, accuracy`. phoneme dataset: 400 rows × 256 freq points, 5 classes (`sh, aa, iy, dcl, ao`) in the row index.

### 7. Functional regression — scalar-on-function (+ FoF signature)
```python
tec = pd.read_csv("docs/data/tecator.csv", index_col=0)   # (240, 103): 100 channels + moisture/fat/protein
Xt = tec.iloc[:, :100].values.astype(np.float64)
yfat = tec["fat"].values.astype(np.float64)
sof = fdars.regression.fregre_lm(Xt, yfat, n_comp=5)       # sig (data, response, n_comp=3)
print("R^2:", round(sof["r_squared"], 4))
```
Output: `R^2: 0.9287`
Keys: `fitted_values (240,), residuals (240,), beta_t (100,), r_squared, coefficients (6,), intercept`. **Function-on-function** call: `fdars.regression.fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3)` (signature verified; run a FoF snippet in the harness if the tour wants FoF — tecator has no natural functional response, so either simulate or use SoF as the tour representative and mention FoF availability in prose).

### 8. Functional time series
```python
cw = pd.read_csv("docs/data/canadian_weather.csv", index_col=0)   # (365 days, 35 stations)
Xfts = cw.T.values.astype(np.float64)                              # (35 series, 365 points)
ARGd = np.arange(365, dtype=np.float64) + 1.0
model = fdars.fts.ftsm(Xfts, ARGd, ncomp=3)                        # keys incl. scores, ar_models
fc = fdars.fts.ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)             # NOTE: raw data+argvals, not the model
print("forecast shape:", fc["forecast"].shape, "| h:", fc["h"])
```
Output: `forecast shape: (3, 365) | h: 3`
**GOTCHA:** `ftsm_forecast(data, argvals, h=1, ncomp=3)` takes **raw data + argvals**, NOT a fitted `ftsm` model dict. `ftsm` keys: `mean, rotation, scores, fitted, weights, ncomp, ar_models`. Treating 35 stations as the FTS time index over 365-point daily curves works for the tour; the CASE-03 forecast study (Phase 89) uses `canadian_weather_precip.csv` multi-year slicing — a Phase 89 concern, flagged in STATE.

### 9. SPM (statistical process monitoring)
```python
fd = Fdata(X, argvals=ARG)
p1 = fdars.spm.spm_phase1(X[:46], ARG, ncomp=3, alpha=0.05)
mon = fdars.spm.spm_monitor(p1["mean"], p1["loadings"], p1["weights"],
                            p1["eigenvalues"], p1["t2_limit"], p1["spe_limit"], X[46:], ARG)
print("T2 alarms:", int(mon["t2_alarm"].sum()), "| SPE alarms:", int(mon["spe_alarm"].sum()))
```
Output: `T2 alarms: <int> | SPE alarms: <int>`
**GOTCHA:** `spm_monitor(mean, loadings, weights, eigenvalues, t2_limit, spe_limit, new_data, argvals)` takes the phase-1 components **unpacked as positional args**, NOT the `spm_phase1` result dict. `spm_phase1(data, argvals, ncomp=3, alpha=0.05)` keys: `t2, spe, t2_limit, spe_limit, mean, loadings, weights, eigenvalues`. `spm_monitor` keys: `t2, spe, t2_alarm, spe_alarm`. Print alarm counts (ints), not float T2 values.

### 10. Conformal & tolerance
```python
tol = fdars.tolerance.fpca_tolerance_band(X, ncomp=3, nb=200, coverage=0.95, seed=42)
print("tolerance keys:", list(tol.keys()), "| band width shape:", tol["half_width"].shape)
```
Output: `tolerance keys: ['upper', 'lower', 'center', 'half_width'] | band width shape: (31,)`
**GOTCHA:** `fpca_tolerance_band(data, ncomp=3, nb=1000, coverage=0.95, seed=42)` takes **NO argvals** and has **no `alpha` kwarg** (use `coverage`). Seeded → deterministic. For conformal specifically, `fdars.conformal` has `conformal_fregre_lm` etc.; tolerance-band is the cleaner tour representative.

### 11. Density / Fréchet / metric
```python
D = fdars.metric.lp_self_1d(X, ARG, p=2.0)       # (93,93) L2 distance matrix
print("L2 distance matrix shape:", D.shape)
Ddtw = fdars.metric.dtw_self_1d(X[:10])          # dtw_self_1d(data, p=2.0, w=0) — no argvals
print("DTW[0,1]:", round(float(Ddtw[0, 1]), 2))
```
Output: `L2 distance matrix shape: (93, 93)` / `DTW[0,1]: 1813.09`
**GOTCHA:** `fdars.frechet.wasserstein_barycenter` does **NOT exist** — that name is in `fdars.density_fda.wasserstein_barycenter(density_matrix, argvals, weights=None)`. `fdars.frechet` provides `frechet_mean(objects, space, d, weights=None)` (objects must be a **list**, not ndarray), `frechet_anova`, `frechet_global_reg`, `frechet_local_reg`. For the metric/Fréchet family the **safest tour snippet is `metric.lp_self_1d` or `metric.dtw_self_1d`** (clean, no list/space plumbing). If the tour wants density: `density_fda.lqd_fpca`, `density_fda.wasserstein_barycenter` require density curves as input (more setup).

### 12. Clustering-adjacent / alignment (elastic)
```python
km_res = fdars.alignment.karcher_mean(X[:10], ARG)   # elastic Karcher/Fréchet mean under SRSF
print("karcher keys:", list(km_res.keys()), "| converged:", km_res["converged"])
print("aligned shape:", km_res["aligned_data"].shape)
```
Output: `karcher keys: ['mean', 'mean_srsf', 'aligned_data', 'gammas', 'n_iter', 'converged'] | converged: <bool>` / `aligned shape: (10, 31)`
`karcher_mean(data, argvals, lambda_=0.0, max_iter=20, tol=1e-4)`. Use a 10-obs subset for speed (elastic alignment is iterative). This is the **alignment** family representative.

### 13. Advisor (LLM-free diagnostics) + provenance
```python
fd = Fdata(X, argvals=ARG)
pc = fd.to_pc(n_comp=3)
diag = fdars.advisor.build_diagnostics(pc, "fpca", argvals=ARG)   # LLM-free grounding
print("cumulative variance explained:", np.round(diag["cumulative_variance_explained"], 3).tolist())
```
Output: `cumulative variance explained: [0.831, 0.969, 1.0]`
`build_diagnostics(result, method, *, argvals=None, ...)` — supported methods: alignment, basis, classification, clustering, depth, fpca, frechet, fts, inference, outliers, regression, regression_cv, represent, scoring, smoothing, spm. Diagnostics keys for fpca incl.: `method, n_components, n_obs, eigenvalues, explained_variance_ratio, cumulative_variance_explained, total_variance, phase_leakage_indicator, has_pace_fpca, ...`. This is **LLM-free and deterministic** — ideal for the advisor snippet. The full `advise(diagnostics, task=..., domain_context=...)` call needs an LLM provider; show its signature in prose but do NOT run it in a generated snippet (non-deterministic, needs API key). Provenance: cite `_references_map.json` (57 papers / \ndocpapers=47 curated-eligible / \ncoverage=28 callables backed) + the `fdars_method_references` MCP tool.

### 14. sklearn estimator layer (Pipeline)
```python
from fdars.sklearn._skeletons import FPCATransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_score
tec = pd.read_csv("docs/data/tecator.csv", index_col=0)
Xt = tec.iloc[:, :100].values.astype(np.float64); yfat = tec["fat"].values.astype(np.float64)
pipe = Pipeline([("fpca", FPCATransformer(n_components=5)), ("ridge", RidgeCV())])
scores = cross_val_score(pipe, Xt, yfat, cv=5, scoring="r2")
print("mean R^2 (5-fold):", round(float(scores.mean()), 3))
```
Output: `mean R^2 (5-fold): 0.784`
**GOTCHA:** `FPCATransformer(argvals=None, n_components=3)` — the param is **`n_components`**, NOT `n_comp`. Estimators import from `fdars.sklearn._skeletons` (not re-exported at `fdars.sklearn`). This showcases the sklearn-compatibility differentiator. Deterministic (cross_val_score with default KFold is deterministic for these estimators). **Round the mean** for float stability.

> **Snippets I could NOT get to a clean one-liner (flagged for planner):** `frechet.frechet_mean` (needs a `list` of objects + a `space` string + a precomputed `d` — plumbing-heavy; use `metric.lp_self_1d` for the metric family instead). `density_fda.wasserstein_barycenter` (needs density curves as input — more setup than a breadth snippet warrants). Neither blocks the tour: the metric family is covered by `lp_self_1d`/`dtw_self_1d` (validated), and density can be mentioned in prose citing the comparison table. Confidence on these two: MEDIUM (signatures verified, but no minimal runnable snippet produced).

---

## Dataset Suitability (docs/data/)

All present `[VERIFIED: ls docs/data/]`. Shapes verified this session.

| Dataset | Shape (CSV) | fdars orientation | Best-fit families |
|---------|-------------|-------------------|-------------------|
| `growth.csv` | 31 ages × 93 subjects (index=age) | `.values.T` → (93 obs, 31 pts), argvals=ages 1–18 | represent, basis/smoothing, depth/outliers, FPCA, clustering, SPM, tolerance, alignment, advisor — **the workhorse** |
| `canadian_weather.csv` | 365 days × 35 stations | `.T` → (35, 365), argvals=day 1–365 | FTS (`ftsm`/`ftsm_forecast`), represent |
| `canadian_weather_precip.csv` | 365 × 35 | same | FTS (CASE-03, Phase 89 — multi-year slicing flagged) |
| `canadian_weather_meta.csv` | station metadata | — | metadata demo for `Fdata(metadata=...)` if desired |
| `phoneme.csv` | 400 rows × 256 freq (index=phoneme label) | `.values` → (400, 256), 5 classes | classification (`fclassif_knn`), metric |
| `tecator.csv` | 240 × 103 (100 channels + moisture/fat/protein) | `.iloc[:,:100]` = spectra, `["fat"]` = scalar y | scalar-on-function regression, sklearn Pipeline (fat prediction) |
| `wine.csv` | (available) | — | sklearn classification (CASE-04, Phase 89) |
| `sonar.csv` | (available) | — | sklearn classification (CASE-04, Phase 89) |

**Loaders exist:** `fdars.datasets.load_growth()`, `load_canadian_weather(variable='temperature')`, `load_phoneme()`, `load_tecator()`, `load_wine()`, `load_sonar()` — each returns a `Dataset` dataclass (`.data` = Fdata, `.argvals`, `.y`, `.meta`, `.name`). `[VERIFIED: runtime]` These are cleaner than manual CSV reads and could be the tour's data-access idiom — BUT the CONTEXT.md prefers `paper_utils.data_path()` for the reproducible pipeline (no data duplication, resolves docs/data/). **Recommendation:** for the paper snippets use `pd.read_csv(data_path("growth.csv"), ...)` for full transparency of the data→Fdata construction (pedagogically clearer for a software paper), OR `fdars.datasets.load_growth()` for brevity. Planner's discretion; both validated.

---

## paper.yml maturin/fdars install step (deferred from Phase 86)

`paper.yml` currently installs only `matplotlib numpy` (stdlib-plus scripts) and has **no fdars**. The snippet `--check` gate needs a compiled `fdars`. Mirror `ci.yml`'s build approach (`maturin develop`).

**Add to `.github/workflows/paper.yml`** (before the snippet-check step, after checkout):

```yaml
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Create venv and build fdars (maturin develop)
        run: |
          python -m venv .venv
          . .venv/bin/activate
          pip install maturin numpy pandas scipy scikit-learn matplotlib
          maturin develop --release

      - name: Assert snippets not stale (MANU-06 / GATE-02 drift gate)
        run: |
          . .venv/bin/activate
          PYTHONPATH=scripts:paper/code python paper/code/gen_snippets.py --check
```

Notes:
- `ci.yml` uses `python -m venv .venv; source .venv/bin/activate; pip install maturin numpy pandas scipy pytest ...; maturin develop --release`. Mirror it. `[VERIFIED: .github/workflows/ci.yml:64-72]`
- **Add `scikit-learn`** to the pip install — the sklearn Pipeline snippet (#14) imports `sklearn.pipeline`, `sklearn.linear_model`, `sklearn.model_selection`. Also `pandas` (all snippets read CSVs).
- Python 3.12 is fine (paper.yml already uses 3.12; fdars is abi3-py39 so any 3.9+ works).
- **Step order (load-bearing, per Phase 86 pattern):** offline drift gates (figures → assert_coverage --check → gen_refs_bib → check_comparison → **gen_snippets --check**) BEFORE `Setup tectonic` + PDF compile, so drift fails fast before the expensive PDF step.
- **Path filter:** `paper.yml` triggers on `paper/**`, `_capability_map.json`, `_references_map.json`, `docs/data/**`. The snippet check ALSO depends on the compiled `fdars` (Rust `src/` + `python/fdars/`). **A pure Rust/Python API change that does NOT touch `paper/**` would NOT trigger paper.yml**, so a snippet could silently go stale. **Flag for planner:** either (a) add `src/**` and `python/fdars/**` to paper.yml path filter, OR (b) accept that GATE-02 (Phase 90) is the backstop re-run. Recommendation: add `python/fdars/**` and `src/**` to the path filter so an API change re-runs the snippet gate. This is the single most important CI decision for the "no stale snippets" milestone risk.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Code highlighting in LaTeX | Custom verbatim macros | `listings` (`\usepackage{listings}` + `lstdefinestyle`) | Standard, no shell-escape, tectonic-friendly |
| Snippet drift detection | Ad-hoc diff scripts | Copy `assert_coverage.py --check` shape | Proven pattern; byte-compare + exit 1 |
| Capturing stdout | Manual print-to-file | `contextlib.redirect_stdout(io.StringIO())` | Clean, stdlib, deterministic |
| Dataset access | Copy CSVs into paper/ | `paper_utils.data_path("growth.csv")` | No data duplication (PIPE-01 lock) |
| Coverage/ref counts in prose | Hardcode `30`, `409`, `28` | `\input{coverage_counts}` macros | Machine-derived; drift-gated (no hardcoded ints — milestone lock) |
| fdars build in CI | pip install fdars from PyPI | `maturin develop --release` (mirror ci.yml) | Tests the local tree, not a published wheel |

**Key insight:** The snippet harness is a near-clone of the already-proven Phase 86 macro pipeline (generate → `--check` → CI). Do not invent a new mechanism; reuse the `_render`/`--check`/`sys.exit(1)` structure of `assert_coverage.py` verbatim in shape.

---

## Common Pitfalls

### Pitfall 1: `listings` not in paper.tex preamble
**What goes wrong:** `\begin{lstlisting}` → "Undefined control sequence" in tectonic CI.
**Why:** `paper.tex` currently loads natbib, fontenc, inputenc, hyperref, url, graphicx, amsmath, booktabs, adjustbox — **no `listings`**. `[VERIFIED: paper/paper.tex]`
**How to avoid:** Plan a task to add `\usepackage{listings}` + the `lstdefinestyle{fdarsinput}`/`{fdarsoutput}` blocks to `paper.tex`. Include a one-listing CI smoke check on first build (as Phase 87 did for adjustbox).

### Pitfall 2: Non-float64 / non-contiguous arrays into native calls
**What goes wrong:** `TypeError: argument 'X': 'ndarray' object is not an instance of 'ndarray'` — a PyO3 dtype/layout mismatch that reads like nonsense.
**Why:** PyO3 `PyReadonlyArray` bindings require exact `f64` (or exact `int64` for labels) and C-contiguity. A `float32`, `uint32`, or a transposed non-contiguous view fails.
**How to avoid:** Every snippet does `.astype(np.float64)` (and `np.int64` for labels); avoid passing raw `.T` views to native funcs without `np.ascontiguousarray` if needed (the validated snippets pass `.values.T.astype(np.float64)` which materializes a contiguous copy — confirmed working). Prefer `Fdata` methods where possible (they handle dtype).

### Pitfall 3: Assuming result-dict / signature shapes from memory
**What goes wrong:** `spm_monitor(phase1_dict)`, `ftsm_forecast(model)`, `fclassif_knn(..., argvals, labels)`, `fpca_tolerance_band(..., alpha=...)`, `FPCATransformer(n_comp=...)` — all WRONG, all raise. Documented above.
**Why:** These signatures are non-obvious and differ across families.
**How to avoid:** The harness RUNS the snippet — a wrong signature fails `gen_snippets.py` immediately, which is exactly the point. But the planner should seed the harness with the VERIFIED call shapes from §Validated Snippets to avoid churn.

### Pitfall 4: Float output drift across platforms
**What goes wrong:** CI `git diff paper/snippets/` non-empty because a captured float printed `0.9287153594311788` locally but `0.9287153594311789` in CI.
**Why:** Raw float repr is not portable.
**How to avoid:** Snippets print shapes, dict keys, counts, `.tolist()` of `np.round(..., n)`, or single `round(float(x), n)` scalars — never raw float arrays. Enforced in the validated snippets above.

### Pitfall 5: paper.yml path filter misses API changes
**What goes wrong:** A change to `python/fdars/` or `src/` alters an API; no `paper/**` file changed; paper.yml doesn't run; a snippet silently goes stale until Phase 90.
**How to avoid:** Add `python/fdars/**` and `src/**` to paper.yml's `paths:` filter (both push and pull_request). See §paper.yml step.

### Pitfall 6: Conflating the `28`s
**What goes wrong:** Prose says "28 estimators pass check_estimator" and cites `\ncoverage` (=28) — but `\ncoverage` is "callables backed by curated papers", a different 28.
**How to avoid:** Add a distinct `\nsklearnestimators` macro (from `TRIAGE_VERDICTS` PASS count) so the sklearn claim is machine-derived and independent. Do not reuse `\ncoverage`.

### Pitfall 7: Calling the advisor `advise()` in a generated snippet
**What goes wrong:** `advise(...)` hits an LLM provider → non-deterministic, needs API key, fails in offline CI.
**How to avoid:** The advisor snippet uses `build_diagnostics(...)` (LLM-free, deterministic). Show `advise()` signature in prose only.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| fdars (compiled) | All snippets | ✓ (.venv) | 0.12.0 | maturin develop in CI |
| numpy | All snippets | ✓ | (in .venv) | — |
| pandas | CSV reads | ✓ | (in .venv) | — |
| scikit-learn | Pipeline snippet (#14) | ✓ | (in .venv) | add to paper.yml pip install |
| matplotlib | figure pipeline (not snippets) | ✓ | (paper.yml) | — |
| listings (LaTeX) | snippet rendering | ✗ (not in paper.tex yet) | TeX Live base | add `\usepackage{listings}`; tectonic fetches |
| tectonic (PDF) | CI compile | ✓ (paper.yml) | wtfjoke/setup-tectonic@v4 | — |
| maturin (Rust build) | paper.yml fdars build | ✗ (not in paper.yml yet) | 1.x | add step mirroring ci.yml |

**Missing with no fallback:** none. **Missing needing action:** `\usepackage{listings}` in paper.tex; maturin/fdars build + scikit-learn in paper.yml (both planned above).

---

## Validation Architecture

`workflow.nyquist_validation` not explicitly false; but this phase's deliverables are prose + generated `.tex` + one harness script. The harness IS the validation for snippets (it runs real code). Test map:

| Behavior | Test Type | Automated Command |
|----------|-----------|-------------------|
| Every snippet runs against fdars 0.12.0 | integration | `PYTHONPATH=scripts:paper/code python paper/code/gen_snippets.py` (fails if any snippet errors) |
| No snippet drift | drift gate | `python paper/code/gen_snippets.py --check` (exit 1 on stale) |
| Coverage macros current | drift gate | `python paper/code/assert_coverage.py --check` (existing) |
| PDF compiles with listings | smoke | tectonic build in paper.yml (CI-only) |
| Prose accuracy / no over-claim | human | Phase 90 GATE-04 blocking read-through |

**Wave 0 gaps:** `paper/code/gen_snippets.py` (new), `paper/snippets/` dir (new), `\usepackage{listings}` + `lstdefinestyle` in paper.tex, `make paper`/`make paper-check`/`paper.yml` wiring, maturin step in paper.yml. No pytest framework needed for this phase — the harness self-validates.

---

## Security Domain

Not applicable — documentation + a local pipeline script. The harness `exec`s snippet source that the authors write (not user input); no network, no secrets (the advisor snippet uses LLM-free `build_diagnostics`). No ASVS categories apply.

---

## Package Legitimacy Audit

No new external packages installed. fdars is the project's own compiled package (maturin develop). scikit-learn, pandas, numpy, matplotlib are already project deps (CLAUDE.md dependency list + ci.yml). LaTeX `listings` is a base TeX Live package fetched by tectonic. No SLOP/SUS risk.

| Package | Registry | Verdict | Note |
|---------|----------|---------|------|
| fdars 0.12.0 | local (maturin) | OK | project's own package, importable in .venv |
| scikit-learn | PyPI | OK | existing project dep (docs examples, sklearn layer) |
| listings (LaTeX) | CTAN/TeX Live | OK | base package; tectonic bundles it |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | tectonic bundles `listings` by default | Harness Design | LOW — base TeX Live package; CI smoke check on first build catches it; fallback: it's fetchable from CTAN |
| A2 | Float output determinism holds if snippets print shapes/keys/rounded scalars | Determinism rules | LOW — validated snippets avoid raw float arrays; determinism gate catches residual |
| A3 | `frechet.frechet_mean` / `density_fda.wasserstein_barycenter` are usable but plumbing-heavy | Snippet #11 | LOW — signatures verified; metric family covered by validated `lp_self_1d`; only affects which snippet represents the family |
| A4 | The two "28"s (sklearn PASS vs \ncoverage curated) are a coincidental collision | Architecture Facts | MEDIUM — verified `\ncoverage`=28 (assert_coverage semantics) AND sklearn PASS=28 independently; if planner reuses `\ncoverage` for the sklearn claim it would be wrong |
| A5 | FoF regression has no natural docs/data/ functional response for a minimal snippet | Snippet #7 | LOW — SoF is the tour representative; FoF signature verified, mentioned in prose |
| A6 | MANU ID↔section pairing offset (REQUIREMENTS vs CONTEXT) | phase_requirements note | LOW — all six requirements covered regardless; planner uses CONTEXT section descriptions as authoritative |

---

## Open Questions

1. **paper.yml path filter scope** — should `python/fdars/**` + `src/**` be added so API changes re-trigger the snippet gate?
   - Recommendation: YES (add them). This is the strongest guarantee against the milestone's HIGHEST-RISK "stale API snippets" concern. Alternative: rely on Phase 90 GATE-02 backstop.
2. **`\nsklearnestimators` macro** — add a machine-derived sklearn PASS count to `assert_coverage.py`?
   - Recommendation: YES — otherwise "28 estimators" is either a hardcoded int (violates milestone lock) or wrongly reuses `\ncoverage`.
3. **Snippet data idiom** — `paper_utils.data_path()` + `pd.read_csv` (transparent) vs `fdars.datasets.load_growth()` (brief)?
   - Recommendation: `data_path()` + `read_csv` for pedagogical clarity in a software paper; both validated. Planner's discretion.
4. **FoF and density snippets** — include as tour families or mention in prose only?
   - Recommendation: metric family = `lp_self_1d` (validated); regression family = SoF (validated) with FoF mentioned; density mentioned in prose citing comparison table. Keeps the tour breadth-first without plumbing-heavy snippets.

---

## Sources

### Primary (HIGH confidence)
- fdars 0.12.0 imported in `.venv` this session — every snippet in §Validated Snippets RUN, output captured; all signatures via `inspect.signature`.
- `python/fdars/_capability_map.json` — read this session (Fdata methods, module signatures).
- `python/fdars/_references_map.json` — read this session (57 papers, 6 curated, 243 callable_index).
- `python/fdars/sklearn/_skeletons.py` + `TRIAGE_VERDICTS`/`EXCLUDED_METHODS` — 28 PASS estimators, 13 excluded, via runtime.
- `src/convert.rs:1-59` — row-major↔column-major conversion, read directly.
- `paper/coverage_counts.tex` — machine-derived macros (30/409/437/27/28/47).
- `paper/code/assert_coverage.py`, `gen_figures.py`, `check_comparison.py`, `paper_utils.py` — harness pattern to mirror, read directly.
- `.github/workflows/ci.yml:64-72`, `paper.yml` — maturin build pattern + current paper CI, read directly.
- `docs/data/*.csv` — shapes verified this session.

### Secondary (MEDIUM confidence)
- Phase 87 RESEARCH.md + `paper/comparison_evidence.md` — peer-package positioning for statement-of-need (transcribe, don't re-assert).
- MEMORY.md v13.0/v9.0 — MCP tool `fdars_method_references`, advisor grounding guard, 28-estimators check_estimator history.

### Tertiary (LOW confidence)
- tectonic `listings` bundle availability — inferred from TeX Live base-package status; verify via CI smoke build.

---

## Metadata

**Confidence breakdown:**
- Validated snippets (13 families + sklearn): HIGH — each RUN this session, output captured, gotchas documented.
- Harness design: HIGH on `listings`/`--check`/determinism approach (mirrors proven Phase 86); MEDIUM on tectonic bundling `listings` (CI smoke check recommended).
- Data model (Fdata + PyIrregFdata): HIGH — runtime-verified; the MANU-05 `IrregFdata` question answered (it's `pace_fpca.PyIrregFdata`).
- Architecture facts: HIGH — convert.rs read, counts machine-derived, sklearn 28-PASS verified; the "zero-copy" nuance flagged for accurate prose.
- Advisor/provenance: HIGH — public surface + LLM-free `build_diagnostics` snippet verified; MCP tool cited from MEMORY.
- paper.yml step: HIGH — mirrors ci.yml; path-filter gap flagged as key decision.

**Research date:** 2026-09-09
**Valid until:** 2026-12-09 (3 months; re-check if fdars bumps past 0.12.0 before Phase 90 — REL-01 bumps to 0.13.0, which should be re-validated at GATE-02).
