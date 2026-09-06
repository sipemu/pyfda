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

    python scripts/generate_capability_dataset.py

Output: ``python/fdars/_capability_map.json``

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

import fdars

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
    renamed or removed method still fails the accuracy test.
    """
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


if __name__ == "__main__":
    dataset = generate_capability_dataset()
    output_path = Path(__file__).parent.parent / "python" / "fdars" / "_capability_map.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, sort_keys=True, ensure_ascii=False)
    n_modules = len(dataset)
    n_callables = sum(len(v) for v in dataset.values())
    print(
        f"Written {n_modules} modules ({n_callables} callables) to {output_path}"
    )
