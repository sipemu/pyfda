"""Generate or check paper/coverage_counts.tex from the committed JSON maps.

Derives seven LaTeX ``\\newcommand`` macros from
``python/fdars/_capability_map.json``, ``python/fdars/_references_map.json``,
and ``fdars.sklearn.TRIAGE_VERDICTS`` (requires a compiled fdars in the env).

Usage
-----
Generate mode (writes paper/coverage_counts.tex)::

    python paper/code/assert_coverage.py

Check mode (exits 1 if the committed file differs from a fresh derivation)::

    python paper/code/assert_coverage.py --check

Macro set emitted
-----------------
``\\ncallables``         — total callable entries across all map keys
``\\ncoverage``          — callables backed by at least one curated paper
``\\ndocpapers``         — non-``_uncurated`` papers in _references_map.json
``\\nexcludedmethods``   — methods in ``fdars.sklearn.EXCLUDED_METHODS`` (interface
                           constraints that prevent sklearn estimator wrapping)
``\\nfdata``             — public (non-underscore-prefixed) methods in the ``_Fdata`` key
``\\npubliccallables``   — callable entries in non-underscore module keys
``\\nsklearnestimators`` — sklearn estimator classes with verdict "PASS" in TRIAGE_VERDICTS
                           (machine-derived; DISTINCT from \\ncoverage which counts
                           callables backed by curated papers — coincidental collision at 28,
                           see RESEARCH.md §Architecture Facts Pitfall 6)
``\\nsubmodules``        — number of public (non-underscore) module keys
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_CAP_MAP = _REPO / "python" / "fdars" / "_capability_map.json"
_REF_MAP = _REPO / "python" / "fdars" / "_references_map.json"
_OUT = _REPO / "paper" / "coverage_counts.tex"


def _derive_counts() -> dict[str, int]:
    """Derive the seven coverage macro values from the committed JSON maps.

    Returns
    -------
    dict[str, int]
        Mapping of macro name (without backslash) to integer value.

    Notes
    -----
    Counting semantics mirror ``scripts/generate_capability_dataset.py:_coverage_counts()``
    exactly.  The ``_Fdata`` key IS included in the ``ncallables`` denominator
    (``sum(len(v) for v in cap.values())`` includes all keys, underscore-prefixed
    or not).  Do NOT subtract ``__init__`` from the total.

    The ``nsklearnestimators`` macro is machine-derived from
    ``fdars.sklearn.TRIAGE_VERDICTS`` — the count of estimator classes whose
    Phase 55-58 verdict is ``"PASS"`` after all reclassifications.  It is
    DISTINCT from ``ncoverage`` (callables backed by curated papers): the two
    happen to coincide at 28 as of fdars 0.12.0 but measure different surfaces.
    A compiled ``fdars`` must be importable in the active environment.
    """
    cap = json.loads(_CAP_MAP.read_text())
    refs = json.loads(_REF_MAP.read_text())
    papers = refs["papers"]
    callable_index = refs.get("callable_index", {})

    # Public modules: non-underscore top-level keys (excludes "_Fdata")
    public_modules = [k for k in cap if not k.startswith("_")]

    # Public Fdata methods: non-underscore-prefixed entries in the "_Fdata" key
    # (excludes all private/dunder methods; counts the public API surface)
    fdata_public = [m for m in cap.get("_Fdata", {}) if not m.startswith("_")]

    # Curated paper keys (curated is True, not just truthy)
    curated_keys = frozenset(pk for pk, p in papers.items() if p.get("curated") is True)

    # Callables backed by at least one curated paper
    n_coverage = sum(
        1 for _, pks in callable_index.items()
        if any(pk in curated_keys for pk in pks)
    )

    # Non-uncurated papers (eligible for refs.bib emission)
    n_docpapers = sum(1 for k in papers if not k.startswith("_uncurated"))

    # sklearn estimators with verdict "PASS" after Phase 55-58 reclassification.
    # Machine-derived from TRIAGE_VERDICTS — do NOT hardcode the integer.
    # DISTINCT from ncoverage (curated-paper-backed callables): see module docstring.
    try:
        from fdars.sklearn import TRIAGE_VERDICTS, EXCLUDED_METHODS  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "assert_coverage.py: cannot import fdars.sklearn.TRIAGE_VERDICTS — "
            "run under a compiled fdars venv (maturin develop)."
        ) from exc
    n_sklearn_estimators = sum(1 for v in TRIAGE_VERDICTS.values() if v == "PASS")
    # Methods excluded from the sklearn estimator layer (interface constraints).
    # Machine-derived from EXCLUDED_METHODS — do NOT hardcode the integer in prose.
    n_excluded_methods = len(EXCLUDED_METHODS)

    return {
        "ncallables": sum(len(v) for v in cap.values()),
        "ncoverage": n_coverage,
        "ndocpapers": n_docpapers,
        "nexcludedmethods": n_excluded_methods,
        "nfdata": len(fdata_public),
        "npubliccallables": sum(len(cap[k]) for k in public_modules),
        "nsklearnestimators": n_sklearn_estimators,
        "nsubmodules": len(public_modules),
    }


def _render(counts: dict[str, int]) -> str:
    """Render macro dict to LaTeX ``\\newcommand`` source text.

    Parameters
    ----------
    counts : dict[str, int]
        Mapping of macro name to integer value.

    Returns
    -------
    str
        Full file content ending with a single trailing newline.  Macros are
        emitted in sorted key order so re-runs are byte-identical.
    """
    lines = [
        "% Auto-generated by paper/code/assert_coverage.py — do not edit.",
        "% Source: python/fdars/_capability_map.json + _references_map.json",
    ]
    for macro, value in sorted(counts.items()):
        lines.append(f"\\newcommand{{\\{macro}}}{{{value}}}")
    return "\n".join(lines) + "\n"


def main() -> None:
    """Entry point: generate or check coverage_counts.tex."""
    check_mode = "--check" in sys.argv
    counts = _derive_counts()
    content = _render(counts)

    if check_mode:
        if not _OUT.exists():
            print(
                f"DRIFT: {_OUT} does not exist — run without --check to generate.",
                file=sys.stderr,
            )
            sys.exit(1)
        committed = _OUT.read_text(encoding="utf-8")
        if committed != content:
            print(
                f"DRIFT: {_OUT} is stale — re-run assert_coverage.py and commit.",
                file=sys.stderr,
            )
            sys.exit(1)
        print("assert_coverage: OK (no drift)")
    else:
        _OUT.write_text(content, encoding="utf-8")
        print(f"Written {_OUT}")


if __name__ == "__main__":
    main()
