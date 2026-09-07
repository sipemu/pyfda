"""Generate the fdars capability dataset: python/fdars/_capability_map.json.

This script introspects the LIVE ``fdars`` package and emits a single
canonical JSON file that feeds three non-duplicating surfaces:

* The capability-discovery skill ``SKILL.md`` (78-02)
* The ``docs/llms.txt`` LLM-oriented digest (78-03)
* The ``fdars_list_capabilities`` MCP tool (78-04)

Generating all three surfaces from one source makes them impossible to drift
apart.  The SKILL-02 accuracy test (``tests/test_capability_accuracy.py``)
regenerates the dataset and asserts byte-identity with the committed copy, so
drift is caught on every CI run.

MAINTENANCE RULE
----------------
Re-run this script whenever ``_submodule_names`` in
``python/fdars/__init__.py`` changes, and commit the regenerated JSON together
with any updates to ``_CAPABILITY_MODULES`` in ``python/fdars/mcp/server.py``
and ``_EXPECTED_CAPABILITY_MODULES`` in
``tests/test_guard_sync_version_independent.py`` in **one atomic commit**.

Usage
-----
::

    # Re-generate the capability JSON (requires live fdars install):
    python scripts/generate_capability_dataset.py

    # Emit docs/llms.txt and docs/ai-capability-map.md from the committed map:
    python scripts/generate_capability_dataset.py --llmstxt

    # Emit docs/references.md and docs/llms.txt (with provenance section):
    python scripts/generate_capability_dataset.py --references

Output (default):     ``python/fdars/_capability_map.json``
Output (--llmstxt):   ``docs/llms.txt`` + ``docs/ai-capability-map.md``
Output (--references): ``docs/references.md`` + ``docs/llms.txt`` (extended)

NOTE: ``--references`` re-emits BOTH ``docs/references.md`` AND the full
``docs/llms.txt`` (with the provenance section appended) so the two surfaces
stay in sync.  Run ``--references`` after any provenance data update in
``python/fdars/_references_map.json``.

EXCLUDED modules (intentional non-duplication boundary)
--------------------------------------------------------
* ``fdars.advisor``  — the LLM/diagnostics layer; covered by the
  ``fdars-advisor`` skill — including it would blur the non-duplication
  boundary with that skill.
* ``fdars.plot``     — optional matplotlib dependency; plotting helpers are
  not part of the analytical capability surface.
* ``fdars.results``  — internal result-wrapper types; not user-facing
  callables in the capability sense.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

# ``fdars`` is imported lazily in generate_capability_dataset() so that the
# --llmstxt docs-emit path can run without a live fdars install.

# ---------------------------------------------------------------------------
# Authoritative ordered list of submodules to enumerate.
# MUST match the ``_submodule_names`` tuple in python/fdars/__init__.py plus
# the three pure-Python modules datasets, metrics, covariance.
# DO NOT add advisor, plot, or results (see module docstring).
# ---------------------------------------------------------------------------
_SUBMODULE_NAMES: list[str] = [
    # Native submodules (from __init__._submodule_names)
    "fdata",
    "depth",
    "metric",
    "basis",
    "smoothing",
    "clustering",
    "regression",
    "alignment",
    "outliers",
    "seasonal",
    "spm",
    "classification",
    "tolerance",
    "conformal",
    "simulation",
    "explain",
    "represent",
    "scoring",
    "inference",
    "pace_fpca",
    "fts",
    "scalar_on_function",
    "frechet",
    "density_fda",
    "multi_fdata",
    "famm",
    "shapelet",
    # Pure-Python convenience modules
    "datasets",
    "metrics",
    "covariance",
]


def get_signature_str(obj: object, name: str = "") -> str:
    """Extract a portable signature string.

    Tries ``inspect.signature`` first (works on all PyO3 0.28 callables in
    this codebase — VERIFIED).  Falls back to ``__text_signature__`` then the
    literal placeholder ``'(...)'``.
    """
    try:
        return str(inspect.signature(obj))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        ts = getattr(obj, "__text_signature__", None)
        if ts:
            return ts
        return "(...)"


def get_purpose(obj: object) -> str:
    """Return the first non-blank docstring line, capped at 120 characters."""
    doc = getattr(obj, "__doc__", None) or ""
    lines = [line.strip() for line in doc.splitlines() if line.strip()]
    return lines[0][:120] if lines else ""


def _build_fdata_entry() -> dict:
    """Introspect ``fdars.Fdata`` public methods and return a map entry dict.

    The ``_Fdata`` entry uses the same ``{"purpose": str, "sig": str}`` shape
    as module entries, but the keys are the public method names on the class.
    Constructor signature is captured under the key ``__init__``.
    """
    import fdars  # noqa: PLC0415 — lazy import; not needed for --llmstxt path
    cls = fdars.Fdata
    entry: dict = {}

    # Constructor
    try:
        init_sig = str(inspect.signature(cls.__init__))
    except (ValueError, TypeError):
        init_sig = "(...)"
    init_doc = getattr(cls.__init__, "__doc__", None) or getattr(cls, "__doc__", None) or ""
    init_lines = [l.strip() for l in init_doc.splitlines() if l.strip()]
    entry["__init__"] = {
        "purpose": init_lines[0][:120] if init_lines else "Fdata functional data container constructor.",
        "sig": init_sig,
    }

    # Public instance methods (non-underscore callables)
    method_names = sorted(
        name
        for name in dir(cls)
        if not name.startswith("_") and callable(getattr(cls, name, None))
    )
    for method_name in method_names:
        obj = getattr(cls, method_name, None)
        if obj is None:
            continue
        entry[method_name] = {
            "purpose": get_purpose(obj),
            "sig": get_signature_str(obj, method_name),
        }

    return entry


def generate_capability_dataset() -> dict:
    """Enumerate the live fdars public surface and return a stable sorted dict.

    Iterates ``_SUBMODULE_NAMES`` in order, reading each module's ``__all__``
    as the authoritative public filter.  Skips private names (leading
    underscore) and non-callables.  Adds an ``_Fdata`` entry for the
    ``fdars.Fdata`` top-level OOP class.

    Curated ``when``-to-use guidance is merged in from
    ``python/fdars/_capability_curation.json`` if present: for each
    ``"module.callable"`` key found in the curation file, the corresponding
    map entry gains a ``"when"`` field.  Introspected ``purpose`` and ``sig``
    are always sourced from live code (never overwritten by curation) so a
    renamed or removed *introspected* method still fails the drift/import
    accuracy tests.  A curation key whose callable was renamed/removed is
    silently skipped here (it finds no map entry to annotate); that staleness
    is caught separately by ``test_capability_curation_keys_resolve`` in
    ``tests/test_capability_accuracy.py``.
    """
    import fdars  # noqa: PLC0415 — lazy import; not needed for --llmstxt path

    dataset: dict = {}

    for mod_name in _SUBMODULE_NAMES:
        mod = getattr(fdars, mod_name, None)
        if mod is None:
            print(f"WARNING: fdars.{mod_name} not found — skipping", file=sys.stderr)
            continue

        # __all__ is the authoritative public-API filter for all modules.
        # Using dir() without __all__ would expose stdlib re-exports (Any, Dict,
        # List, etc.) in pure-Python modules like fdars.datasets.
        all_ = getattr(mod, "__all__", None)
        if all_:
            names = sorted(n for n in all_ if not n.startswith("_"))
        else:
            # Fallback: should not be reached for any current fdars module.
            names = sorted(
                n
                for n in dir(mod)
                if not n.startswith("_") and callable(getattr(mod, n, None))
            )

        callables: dict = {}
        for fn_name in names:
            obj = getattr(mod, fn_name, None)
            if obj is None or not callable(obj):
                continue
            callables[fn_name] = {
                "purpose": get_purpose(obj),
                "sig": get_signature_str(obj, fn_name),
            }

        if callables:
            dataset[mod_name] = callables

    # Add the _Fdata top-level OOP class entry.
    dataset["_Fdata"] = _build_fdata_entry()

    # Merge curated when-to-use guidance (if curation file present).
    curation_path = Path(__file__).parent.parent / "python" / "fdars" / "_capability_curation.json"
    if curation_path.exists():
        with open(curation_path, encoding="utf-8") as f:
            curation: dict = json.load(f)
        for key, when_text in curation.items():
            if "." not in key:
                continue
            mod_name, fn_name = key.split(".", 1)
            if mod_name in dataset and fn_name in dataset[mod_name]:
                dataset[mod_name][fn_name]["when"] = when_text

    return dataset


# ---------------------------------------------------------------------------
# Docs-emit helpers (--llmstxt path)
#
# These functions read the COMMITTED ``python/fdars/_capability_map.json``
# and emit two docs files offline.  They do NOT import fdars so they work
# in CI docs environments where the compiled extension may not be present.
# ---------------------------------------------------------------------------

# Map module names to their reference-docs page (relative to docs/).
# Modules without a dedicated page fall back to the reference index.
_MODULE_REF_PAGES: dict[str, str] = {
    "alignment": "reference/alignment.md",
    "basis": "reference/basis.md",
    "classification": "reference/classification.md",
    "clustering": "reference/clustering.md",
    "conformal": "reference/conformal.md",
    "depth": "reference/depth.md",
    "explain": "reference/explain.md",
    "fdata": "reference/fdata.md",
    "metric": "reference/metric.md",
    "outliers": "reference/outliers.md",
    "regression": "reference/regression.md",
    "seasonal": "reference/seasonal.md",
    "simulation": "reference/simulation.md",
    "smoothing": "reference/smoothing.md",
    "spm": "reference/spm.md",
    "tolerance": "reference/tolerance.md",
}

_SITE_BASE = "https://sipemu.github.io/pyfda"

# One-line module summaries for the Core Modules bullet list.
_MODULE_SUMMARIES: dict[str, str] = {
    "alignment": "Elastic alignment, SRSF registration, Karcher mean, elastic FPCA",
    "basis": "Basis representations — B-spline, Fourier, functional PCA",
    "classification": "Functional classifiers — k-nearest neighbours, SVM, centroid-based",
    "clustering": "Functional k-means, fuzzy, GMM, and elastic clustering",
    "conformal": "Conformal prediction and classification bands",
    "covariance": "Kernel covariance functions for Gaussian processes over functions",
    "datasets": "Built-in datasets — Canadian weather, Tecator, phoneme, growth, and more",
    "density_fda": "Density-based functional data analysis and Wasserstein distances",
    "depth": "Functional depth measures — Fraiman-Muniz, band, modal, random-projection",
    "explain": "Functional explainability — SHAP, FCI, GRAD-CAM, and attribution maps",
    "famm": "Functional additive mixed models (FAMM) for longitudinal data",
    "fdata": "Core functional data operations — mean, deriv, norm, integrate, reconstruct",
    "frechet": "Fréchet regression for metric-space responses",
    "fts": "Functional time series — forecasting, correlation, spectral analysis",
    "inference": "Functional inference — two-sample tests, interval-wise testing",
    "metric": "Functional distance and similarity metrics — L2, L1, Mahalanobis, DTW",
    "metrics": "Regression and classification scoring metrics for functional outputs",
    "multi_fdata": "Multi-domain functional data — paired domains, joint analysis",
    "outliers": "Functional outlier detection — depth-based, magnitude, shape outliers",
    "pace_fpca": "PACE: Principal Analysis by Conditional Expectation for sparse data",
    "regression": "Functional regression — scalar-on-function, function-on-scalar, GLM",
    "represent": "Dimensionality reduction and functional representation tools",
    "scalar_on_function": "Scalar-on-function regression with regularisation",
    "scoring": "Functional scoring — penalised, tolerance-band, and integrated scores",
    "seasonal": "Seasonal functional decomposition and periodic pattern analysis",
    "shapelet": "Functional shapelets — pattern-based classification and feature learning",
    "simulation": "Simulation of functional data — GPs, Brownian motion, Ornstein-Uhlenbeck",
    "smoothing": "Functional smoothing — kernel, basis, and roughness-penalised methods",
    "spm": "Statistical process monitoring — T2, SPE, control charts",
    "tolerance": "Functional tolerance bands — simultaneous and pointwise coverage",
}


def _module_url(mod_name: str) -> str:
    """Return the canonical docs URL for a module."""
    page = _MODULE_REF_PAGES.get(mod_name, "reference/index.md")
    # strip the .md extension for HTML nav URL
    page_path = page.replace(".md", "/").rstrip("/")
    return f"{_SITE_BASE}/{page_path}/"


def _emit_llmstxt(
    data: dict,
    repo_root: Path,
    ref_data: "dict | None" = None,
    cap_data: "dict | None" = None,
) -> Path:
    """Emit ``docs/llms.txt`` from the capability map.

    Follows the llms.txt convention:
    - Line 1: H1 title
    - Blockquote: one-paragraph library summary
    - ``## Core Modules``: bullet list of module name + summary + link
    - ``## Full API Reference``: per-module subsections with
      ``module.fn(sig) — purpose`` lines (curated ``when`` appended if present)
    - ``## Scientific Provenance & Cross-Language Implementations`` section
      (appended only when both ``ref_data`` and ``cap_data`` are provided)

    Output is deterministic: modules are emitted in sorted order.

    The ``ref_data`` / ``cap_data`` parameters are optional.  When both are
    provided (the ``--references`` path), the provenance section is appended.
    When absent (the ``--llmstxt`` path from ``emit_docs()``), the output is
    byte-for-byte identical to the previous behaviour.
    """
    out_path = repo_root / "docs" / "llms.txt"

    public_modules = sorted(k for k in data if not k.startswith("_"))
    n_callables = sum(len(data[m]) for m in public_modules)

    lines: list[str] = []

    # H1 title
    lines.append("# fdars — Functional Data Analysis for Python")
    lines.append("")

    # Blockquote summary
    lines.append(
        "> High-performance functional data analysis toolkit powered by Rust via PyO3. "
        "Provides depth measures, basis representations, smoothing, clustering, elastic "
        "alignment, regression (scalar-on-function, function-on-scalar, Fréchet), outlier "
        "detection, functional time series, seasonal decomposition, SPM control charts, "
        "conformal prediction, density FDA, and more. "
        f"{len(public_modules)} public submodules, {n_callables} public callables."
    )
    lines.append("")

    # Optional: links to key docs
    lines.append(f"[Documentation]({_SITE_BASE}/)")
    lines.append(f"[Reference]({_SITE_BASE}/reference/)")
    lines.append(f"[GitHub](https://github.com/sipemu/pyfda)")
    lines.append("")

    # Core Modules section
    lines.append("## Core Modules")
    lines.append("")
    for mod_name in public_modules:
        url = _module_url(mod_name)
        summary = _MODULE_SUMMARIES.get(mod_name, f"fdars.{mod_name} functions")
        lines.append(f"- [fdars.{mod_name}]({url}): {summary}")
    lines.append("")

    # Full API Reference section
    lines.append("## Full API Reference")
    lines.append("")
    lines.append(
        "Each entry: `module.function(signature)` — one-line purpose. "
        "Where available, a `When:` note gives guidance on which task this function suits best."
    )
    lines.append("")

    for mod_name in public_modules:
        mod_entries = data[mod_name]
        fn_names = sorted(mod_entries.keys())
        n = len(fn_names)
        lines.append(f"### fdars.{mod_name} ({n} functions)")
        lines.append("")
        for fn_name in fn_names:
            entry = mod_entries[fn_name]
            sig = entry.get("sig", "(...)")
            purpose = entry.get("purpose", "")
            when = entry.get("when", "")
            line = f"- `{mod_name}.{fn_name}{sig}` — {purpose}"
            if when:
                line += f" When: {when}"
            lines.append(line)
        lines.append("")

    # Provenance section — appended only when ref_data/cap_data are provided
    if ref_data is not None and cap_data is not None:
        lines.extend(_provenance_section_lines(ref_data, cap_data))

    content = "\n".join(lines)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def _emit_ai_capability_map(data: dict, repo_root: Path) -> Path:
    """Emit ``docs/ai-capability-map.md`` from the capability map.

    Produces a human-readable MkDocs page with:
    - Front-matter title
    - Intro paragraph
    - Per-module sections with a summary table (function, signature, purpose)

    Output is deterministic: modules emitted in sorted order; functions in sorted
    order within each module.
    """
    out_path = repo_root / "docs" / "ai-capability-map.md"

    public_modules = sorted(k for k in data if not k.startswith("_"))
    n_callables = sum(len(data[m]) for m in public_modules)

    lines: list[str] = []

    # MkDocs page title
    lines.append("# fdars AI Capability Map")
    lines.append("")
    lines.append(
        "This page is the human-readable companion to the machine-readable "
        f"[`llms.txt`]({_SITE_BASE}/llms.txt) digest. "
        "It lists every public callable in the `fdars` library, grouped by submodule."
    )
    lines.append("")
    lines.append(
        f"**{len(public_modules)} submodules &middot; {n_callables} public callables** "
        "— all generated offline from the committed capability map. "
        "AI agents: use `fdars_list_capabilities()` (MCP tool) or "
        f"[llms.txt]({_SITE_BASE}/llms.txt) for the machine-readable form."
    )
    lines.append("")

    # Quick-nav table
    lines.append("## Module Index")
    lines.append("")
    lines.append("| Module | Purpose | Functions |")
    lines.append("|--------|---------|-----------|")
    for mod_name in public_modules:
        url = _module_url(mod_name)
        summary = _MODULE_SUMMARIES.get(mod_name, f"fdars.{mod_name}")
        n = len(data[mod_name])
        lines.append(f"| [`fdars.{mod_name}`](#{mod_name}) | {summary} | {n} |")
    lines.append("")

    # Per-module sections
    lines.append("## Module Details")
    lines.append("")

    for mod_name in public_modules:
        mod_entries = data[mod_name]
        fn_names = sorted(mod_entries.keys())
        url = _module_url(mod_name)
        summary = _MODULE_SUMMARIES.get(mod_name, "")

        lines.append(f"### `fdars.{mod_name}` {{#{mod_name}}}")
        lines.append("")
        if summary:
            lines.append(f"{summary}.")
            lines.append("")
        lines.append(f"[Reference docs]({url})")
        lines.append("")
        lines.append("| Function | Signature | Purpose |")
        lines.append("|----------|-----------|---------|")
        for fn_name in fn_names:
            entry = mod_entries[fn_name]
            sig = entry.get("sig", "(...)")
            purpose = entry.get("purpose", "")
            # Escape pipe chars in sig/purpose for table cell safety
            sig_cell = sig.replace("|", "&#124;")
            purpose_cell = purpose.replace("|", "&#124;")
            lines.append(f"| `{fn_name}` | `{sig_cell}` | {purpose_cell} |")
        lines.append("")

    content = "\n".join(lines)
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# References-emit helpers (--references path)
#
# These functions read the COMMITTED ``python/fdars/_references_map.json``
# and ``python/fdars/_capability_map.json`` to emit two docs surfaces offline.
# They do NOT import fdars — they work in docs-build environments where the
# compiled extension may not be present.
# ---------------------------------------------------------------------------


def _coverage_counts(ref_data: dict, cap_data: dict) -> "tuple[int, int]":
    """Derive coverage numerator and denominator from the committed JSON data.

    Mirrors the derivation in ``python/fdars/mcp/server.py`` exactly.
    NEVER returns hardcoded values — all numbers are derived from live JSON.

    Returns:
        (numerator, denominator) where
        - denominator = total callables in _capability_map.json
        - numerator   = callables backed by at least one curated:true paper
    """
    denominator = sum(len(v) for v in cap_data.values())
    papers_map = ref_data.get("papers", {})
    callable_index = ref_data.get("callable_index", {})
    curated_paper_keys = frozenset(
        pk for pk, p in papers_map.items() if p.get("curated", False) is True
    )
    numerator = sum(
        1 for _, pks in callable_index.items()
        if any(pk in curated_paper_keys for pk in pks)
    )
    return (numerator, denominator)


def _callable_purpose(callable_key: str, cap_data: dict) -> str:
    """Look up purpose for a callable key from the capability map.

    Handles the ``_Fdata`` module prefix (OOP container methods live under
    ``cap_data["_Fdata"]``).
    """
    if "." not in callable_key:
        return ""
    module, fn = callable_key.split(".", 1)
    mod_data = cap_data.get(module, {})
    entry = mod_data.get(fn, {})
    return entry.get("purpose", "")


def _emit_references_page(ref_data: dict, cap_data: dict, repo_root: Path) -> Path:
    """Write ``docs/references.md`` — family-grouped scientific references page.

    Structure:
    - H1 title + intro blockquote with derived coverage fraction
    - ## Coverage section (derived, never hardcoded)
    - ## Methods by Module — one H3 per module family (alphabetical)
      - H4 per paper (Authors Year — Title)
      - Metadata table (Authors / Year / DOI / URL / Type / Status)
      - Callables list (with purpose from capability map)
      - Cross-language table (only when non-empty)
    - Sentinel papers (_uncurated* keys) are completely skipped

    Only uses plain Markdown — no {#anchor} attr_list syntax, no HTML blocks.
    Internal doc links restricted to ai-capability-map.md (confirmed present).
    """
    out_path = repo_root / "docs" / "references.md"
    papers_map = ref_data.get("papers", {})

    numerator, denominator = _coverage_counts(ref_data, cap_data)
    coverage_str = f"{numerator}/{denominator}"

    curated_paper_keys = frozenset(
        pk for pk, p in papers_map.items() if p.get("curated", False) is True
    )

    # Group papers by primary module (first callable's module prefix).
    # Skip sentinel papers (_uncurated* keys).
    # A multi-module paper appears once under its primary module.
    module_papers: dict[str, list[tuple[str, dict]]] = {}
    for paper_key in sorted(papers_map.keys()):
        if paper_key.startswith("_uncurated"):
            continue
        paper = papers_map[paper_key]
        callables = paper.get("callables", [])
        if not callables:
            continue
        primary_module = callables[0].split(".")[0]
        module_papers.setdefault(primary_module, []).append((paper_key, paper))

    lines: list[str] = []

    # H1 + intro blockquote
    lines.append("# fdars Scientific References")
    lines.append("")
    lines.append(
        f"> Curated primary paper references for fdars functional data analysis methods.  "
    )
    lines.append(
        f"> Generated offline from `python/fdars/_references_map.json`.  "
    )
    lines.append(
        f"> **{numerator}/{denominator} callables** have curated entries (authoring: {coverage_str}).  "
    )
    lines.append(
        f"> Uncurated callables are absent; see the [AI Capability Map](ai-capability-map.md) "
        f"for the full callable surface."
    )
    lines.append("")

    # Coverage section
    lines.append("## Coverage")
    lines.append("")
    lines.append(
        f"**{numerator} of {denominator} public callables** have at least one curated "
        f"primary-paper entry."
    )
    lines.append(
        "Remaining callables have contested attribution, no single primary paper, "
        "or are pending Phase-84 human DOI-landing-page verification."
    )
    lines.append(
        f"See [AI Capability Map](ai-capability-map.md) for all {denominator} callables."
    )
    lines.append("")

    # Methods by Module
    lines.append("## Methods by Module")
    lines.append("")

    for module_key in sorted(module_papers.keys()):
        papers_in_module = module_papers[module_key]

        # Section heading
        if module_key == "_Fdata":
            lines.append("### Fdata Class Methods")
        else:
            summary = _MODULE_SUMMARIES.get(module_key, "")
            if summary:
                lines.append(f"### fdars.{module_key} — {summary}")
            else:
                lines.append(f"### fdars.{module_key}")
        lines.append("")

        for paper_key, paper in papers_in_module:
            authors_list = paper.get("authors", [])
            year = paper.get("year", "")
            title = paper.get("title", "")
            doi = paper.get("doi", "")
            url = paper.get("url", "")
            pub_type = paper.get("type", "")
            is_curated = paper.get("curated", False) is True
            callables = paper.get("callables", [])
            cross_language = paper.get("cross_language", {})

            # H4: Authors (Year) — Title
            authors_str = ", ".join(authors_list) if authors_list else "Unknown"
            year_str = str(year) if year else "n.d."
            title_str = title if title else "(title pending verification)"
            lines.append(f"#### {authors_str} ({year_str}) — {title_str}")
            lines.append("")

            # Metadata table
            lines.append("| Field | Value |")
            lines.append("|-------|-------|")
            lines.append(f"| Authors | {authors_str} |")
            lines.append(f"| Year | {year_str} |")
            if doi:
                lines.append(f"| DOI | `doi:{doi}` |")
            if url:
                # Shorten URL for display — use the full URL as link text clipped
                display_url = url if len(url) <= 60 else url[:57] + "..."
                lines.append(f"| URL | [{display_url}]({url}) |")
            lines.append(f"| Type | {pub_type} |")
            status = "Curated" if is_curated else "Pending DOI verification"
            lines.append(f"| Status | {status} |")
            lines.append("")

            # Callables
            if callables:
                lines.append("**Callables implementing this method:**")
                lines.append("")
                for callable_key in callables:
                    purpose = _callable_purpose(callable_key, cap_data)
                    if purpose:
                        lines.append(f"- `{callable_key}` — {purpose}")
                    else:
                        lines.append(f"- `{callable_key}`")
                lines.append("")

            # Cross-language table (omit entirely when empty — honest gap)
            if cross_language:
                lines.append("**Cross-language implementations:**")
                lines.append("")
                lines.append("| Language | Package | Function | Confidence |")
                lines.append("|----------|---------|----------|------------|")
                for lang, impl in sorted(cross_language.items()):
                    pkg = impl.get("package", "")
                    fn = impl.get("function", "")
                    confidence = impl.get("confidence", "")
                    lines.append(f"| {lang} | `{pkg}` | `{fn}` | {confidence} |")
                lines.append("")

            lines.append("---")
            lines.append("")

    content = "\n".join(lines)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def _provenance_section_lines(ref_data: dict, cap_data: dict) -> "list[str]":
    """Build the '## Scientific Provenance & Cross-Language Implementations' block.

    Returns a list of lines to be appended to docs/llms.txt.  Emits ONLY
    callables whose backing paper has curated:true on at least one paper.
    Sentinel papers (_uncurated* keys) never appear in this section.

    Per-entry line format:
        - `module.callable` — Authors (Year) doi:DOI ; R: pkg::fn / Python: pkg.fn
    The doi segment is omitted when doi is empty.
    The cross-language segment is omitted when cross_language is empty.
    """
    papers_map = ref_data.get("papers", {})
    callable_index = ref_data.get("callable_index", {})

    numerator, denominator = _coverage_counts(ref_data, cap_data)
    uncurated_count = denominator - numerator

    curated_paper_keys = frozenset(
        pk for pk, p in papers_map.items() if p.get("curated", False) is True
    )

    # Group curated callables by module for the per-module subsections.
    # A callable appears only once in callable_index, under its canonical key.
    # Skip any callable whose every backing paper is uncurated.
    module_callable_entries: dict[str, list[tuple[str, str, dict]]] = {}
    for callable_key in sorted(callable_index.keys()):
        paper_keys = callable_index[callable_key]
        # Only callables with at least one curated:true backing paper
        curated_pks = [pk for pk in paper_keys if pk in curated_paper_keys]
        if not curated_pks:
            continue
        module = callable_key.split(".")[0] if "." in callable_key else callable_key
        for pk in curated_pks:
            paper = papers_map[pk]
            module_callable_entries.setdefault(module, []).append(
                (callable_key, pk, paper)
            )

    lines: list[str] = []
    lines.append("")
    lines.append("## Scientific Provenance & Cross-Language Implementations")
    lines.append("")
    lines.append(
        f"Coverage: {numerator} of {denominator} public callables have curated "
        f"primary-paper entries."
    )
    lines.append(
        "Uncurated callables are absent from this section. A consumer MAY synthesize"
    )
    lines.append(
        "provenance for uncurated callables but MUST flag each synthesized citation as"
    )
    lines.append(
        'ungrounded (grounded: false) — never present synthesized provenance as curated.'
    )
    lines.append("")

    for module_key in sorted(module_callable_entries.keys()):
        entries = module_callable_entries[module_key]
        if module_key == "_Fdata":
            lines.append("### Fdata Class Methods")
        else:
            lines.append(f"### fdars.{module_key}")
        lines.append("")

        for callable_key, paper_key, paper in entries:
            authors_list = paper.get("authors", [])
            year = paper.get("year", "")
            doi = paper.get("doi", "")
            cross_language = paper.get("cross_language", {})

            authors_str = ", ".join(authors_list) if authors_list else "Unknown"
            year_str = str(year) if year else "n.d."

            # Build entry line
            entry_line = f"- `{callable_key}` — {authors_str} ({year_str})"
            if doi:
                entry_line += f" doi:{doi}"
            if cross_language:
                lang_parts = []
                for lang in sorted(cross_language.keys()):
                    impl = cross_language[lang]
                    pkg = impl.get("package", "")
                    fn = impl.get("function", "")
                    if lang == "R":
                        lang_parts.append(f"R: {pkg}::{fn}")
                    elif lang == "Python":
                        lang_parts.append(f"Python: {pkg}.{fn}")
                    elif lang == "Matlab":
                        lang_parts.append(f"Matlab: {pkg}.{fn}")
                    else:
                        lang_parts.append(f"{lang}: {pkg}.{fn}")
                if lang_parts:
                    entry_line += " ; " + " / ".join(lang_parts)

            lines.append(entry_line)

        lines.append("")

    # Closing uncurated note (verbatim per spec)
    lines.append(
        f"> Uncurated callables ({uncurated_count} of {denominator}) are absent "
        f"from this section."
    )
    lines.append(
        "> A consumer MAY synthesize provenance for these callables but MUST structurally"
    )
    lines.append(
        '> flag each synthesized citation as ungrounded: { "grounded": false } per citation.'
    )
    lines.append(
        "> Never present synthesized provenance as curated data from this file."
    )
    lines.append("")

    return lines


def emit_references(repo_root: Path) -> None:
    """Read the committed JSON artifacts and emit docs/references.md + docs/llms.txt.

    This is the --references offline path.  It does NOT import fdars — it reads
    the committed JSON artifacts so it works in docs-build environments where the
    compiled extension may not be present.

    Emits BOTH docs/references.md AND the full docs/llms.txt (with the
    '## Scientific Provenance & Cross-Language Implementations' section appended)
    so the two surfaces stay in sync.  Run --references whenever provenance data
    in python/fdars/_references_map.json changes.
    """
    ref_path = repo_root / "python" / "fdars" / "_references_map.json"
    cap_path = repo_root / "python" / "fdars" / "_capability_map.json"

    if not ref_path.exists():
        print(f"ERROR: references map not found at {ref_path}", file=sys.stderr)
        sys.exit(1)
    if not cap_path.exists():
        print(f"ERROR: capability map not found at {cap_path}", file=sys.stderr)
        print(
            "Run: python scripts/generate_capability_dataset.py first",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(ref_path, encoding="utf-8") as f:
        ref_data: dict = json.load(f)
    with open(cap_path, encoding="utf-8") as f:
        cap_data: dict = json.load(f)

    refs_path = _emit_references_page(ref_data, cap_data, repo_root)
    llmstxt_path = _emit_llmstxt(cap_data, repo_root, ref_data=ref_data, cap_data=cap_data)

    print(f"Written {refs_path}")
    print(f"Written {llmstxt_path} (extended with provenance section)")


def emit_docs(repo_root: Path) -> None:
    """Read the committed capability map and emit docs/llms.txt + docs/ai-capability-map.md.

    This is the --llmstxt path.  It does NOT import fdars — it reads the
    committed JSON artifact so it works in docs-build environments where the
    compiled extension may not be present.
    """
    map_path = repo_root / "python" / "fdars" / "_capability_map.json"
    if not map_path.exists():
        print(f"ERROR: capability map not found at {map_path}", file=sys.stderr)
        print("Run: python scripts/generate_capability_dataset.py first", file=sys.stderr)
        sys.exit(1)

    with open(map_path, encoding="utf-8") as f:
        data: dict = json.load(f)

    llmstxt_path = _emit_llmstxt(data, repo_root)
    capmap_path = _emit_ai_capability_map(data, repo_root)

    public_modules = [k for k in data if not k.startswith("_")]
    n_callables = sum(len(data[m]) for m in public_modules)
    print(
        f"Written {llmstxt_path} "
        f"({len(public_modules)} modules, {n_callables} callables)"
    )
    print(f"Written {capmap_path}")


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    if "--llmstxt" in sys.argv:
        emit_docs(repo_root)
    elif "--references" in sys.argv:
        emit_references(repo_root)
    else:
        dataset = generate_capability_dataset()
        output_path = repo_root / "python" / "fdars" / "_capability_map.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, sort_keys=True, ensure_ascii=False)
        n_modules = len(dataset)
        n_callables = sum(len(v) for v in dataset.values())
        print(
            f"Written {n_modules} modules ({n_callables} callables) to {output_path}"
        )
