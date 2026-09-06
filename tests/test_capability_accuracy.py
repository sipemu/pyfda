"""SKILL-02 accuracy harness: capability map no-drift + all-importable.

Two tests:

``test_capability_map_no_drift``
    Regenerate the capability dataset from the live ``fdars`` package and
    assert that the byte-sorted JSON matches the committed
    ``python/fdars/_capability_map.json``.  Any drift means the generator
    must be re-run and the new map committed.

``test_capability_map_all_importable``
    For every ``module.callable`` entry in the committed map, assert
    ``getattr(fdars.<module>, <callable>)`` resolves.  For the special
    ``_Fdata`` entry, assert each method resolves on ``fdars.Fdata``.
    A renamed or removed method fails here.

Python version constraint
-------------------------
This module imports ONLY stdlib (``json``, ``sys``, ``inspect``,
``importlib.resources``) plus ``pytest`` and ``fdars``.  It does NOT import
``mcp`` at module level — ``mcp`` is absent on Python 3.9 and importing it
at module level would break the entire test collection on 3.9 (COMPAT-03).

Reference: SKILL-02, COMPAT-03.
"""

from __future__ import annotations

import inspect
import json
import sys
from importlib import resources
from pathlib import Path

import pytest

import fdars

# ---------------------------------------------------------------------------
# The same ordered submodule list as the generator.
# MAINTENANCE NOTE: keep in sync with _SUBMODULE_NAMES in
# scripts/generate_capability_dataset.py and _submodule_names in
# python/fdars/__init__.py.  Update all three in one atomic commit.
# ---------------------------------------------------------------------------
_SUBMODULE_NAMES: list[str] = [
    # Native submodules
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


# ---------------------------------------------------------------------------
# Helpers — mirror generate_capability_dataset.py exactly
# ---------------------------------------------------------------------------


def _get_signature_str(obj: object, name: str = "") -> str:
    """Portable signature extractor matching the generator exactly."""
    try:
        return str(inspect.signature(obj))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        ts = getattr(obj, "__text_signature__", None)
        if ts:
            return ts
        return "(...)"


def _get_purpose(obj: object) -> str:
    """First non-blank docstring line, max 120 chars — mirrors generator."""
    doc = getattr(obj, "__doc__", None) or ""
    lines = [line.strip() for line in doc.splitlines() if line.strip()]
    return lines[0][:120] if lines else ""


def _build_fdata_entry() -> dict:
    """Reconstruct the _Fdata entry from the live Fdata class."""
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
            "purpose": _get_purpose(obj),
            "sig": _get_signature_str(obj, method_name),
        }

    return entry


def _generate_live() -> dict:
    """Regenerate the capability dataset from live fdars.

    Mirrors ``generate_capability_dataset()`` in
    ``scripts/generate_capability_dataset.py`` exactly — same submodule list,
    same ``__all__`` filter, same purpose/sig extraction, same ``_Fdata``
    handling, same curation-merge.  The no-drift test will fail if this
    function diverges from the generator.

    NOTE: the curation merge is intentionally NOT replicated here.  The
    no-drift test compares the live *introspected* surface (purpose + sig)
    against the committed map's introspected fields.  The ``when`` fields are
    hand-authored and will always be present in the committed map but absent
    from the live re-generation.  The comparison strips ``when`` fields from
    both sides so curation additions do not cause spurious drift failures.
    """
    dataset: dict = {}

    for mod_name in _SUBMODULE_NAMES:
        mod = getattr(fdars, mod_name, None)
        if mod is None:
            continue

        all_ = getattr(mod, "__all__", None)
        if all_:
            names = sorted(n for n in all_ if not n.startswith("_"))
        else:
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
                "purpose": _get_purpose(obj),
                "sig": _get_signature_str(obj, fn_name),
            }

        if callables:
            dataset[mod_name] = callables

    dataset["_Fdata"] = _build_fdata_entry()

    return dataset


def _load_committed() -> dict:
    """Load the committed _capability_map.json via importlib.resources (Py 3.9+).

    Uses ``importlib.resources.files('fdars') / '_capability_map.json'`` which
    survives wheel installation (no hard-coded file paths).
    """
    cap_file = resources.files("fdars") / "_capability_map.json"
    return json.loads(cap_file.read_text(encoding="utf-8"))


def _strip_when(dataset: dict) -> dict:
    """Return a copy of dataset with 'when' fields removed.

    Used to compare the introspected surface independently of hand-authored
    curation guidance, so adding a 'when' entry to _capability_curation.json
    does not cause a spurious no-drift failure.
    """
    stripped: dict = {}
    for mod_name, entries in dataset.items():
        stripped[mod_name] = {}
        for fn_name, entry in entries.items():
            stripped[mod_name][fn_name] = {
                k: v for k, v in entry.items() if k != "when"
            }
    return stripped


# ---------------------------------------------------------------------------
# SKILL-02 tests
# ---------------------------------------------------------------------------


def test_capability_map_no_drift() -> None:
    """SKILL-02 (a): regenerate matches committed introspected surface — no drift.

    Compares purpose + sig fields only (strips ``when`` curation fields from
    both sides so curation additions do not trigger this test).  Any change
    to a callable's signature or docstring will still cause a failure.

    Remediation: run ``python scripts/generate_capability_dataset.py`` and
    commit the updated ``python/fdars/_capability_map.json``.
    """
    committed = _load_committed()
    live = _generate_live()

    committed_stripped = _strip_when(committed)
    live_stripped = _strip_when(live)

    committed_json = json.dumps(committed_stripped, sort_keys=True, indent=2)
    live_json = json.dumps(live_stripped, sort_keys=True, indent=2)

    assert committed_json == live_json, (
        "Capability map introspected surface has drifted from the live fdars package.\n"
        "Run: python scripts/generate_capability_dataset.py\n"
        "Then commit python/fdars/_capability_map.json.\n\n"
        "Modules in committed only: "
        + str(set(committed_stripped) - set(live_stripped))
        + "\n"
        "Modules in live only: "
        + str(set(live_stripped) - set(committed_stripped))
    )


def test_capability_map_all_importable() -> None:
    """SKILL-02 (b): every documented callable is importable via fdars.<module>.<fn>.

    For the special ``_Fdata`` entry, methods are resolved on ``fdars.Fdata``
    (the top-level OOP class) rather than a submodule.

    Fails if a callable was renamed or removed after the map was committed.
    Remediation: re-run the generator, commit the updated map.
    """
    committed = _load_committed()
    missing: list[str] = []

    for mod_name, entries in committed.items():
        if mod_name == "_Fdata":
            # _Fdata entries are methods on the top-level Fdata class
            for fn_name in entries:
                if fn_name == "__init__":
                    # The constructor is always importable via the class itself
                    if not callable(fdars.Fdata):
                        missing.append("fdars.Fdata (class not callable)")
                elif getattr(fdars.Fdata, fn_name, None) is None:
                    missing.append(f"fdars.Fdata.{fn_name}")
            continue

        mod = getattr(fdars, mod_name, None)
        if mod is None:
            missing.append(f"fdars.{mod_name} (module not found)")
            continue

        for fn_name in entries:
            if getattr(mod, fn_name, None) is None:
                missing.append(f"fdars.{mod_name}.{fn_name}")

    assert not missing, (
        f"SKILL-02: {len(missing)} documented callables are not importable:\n"
        + "\n".join(f"  {m}" for m in missing[:20])
        + ("\n  ..." if len(missing) > 20 else "")
    )
