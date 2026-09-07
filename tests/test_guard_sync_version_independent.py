"""Version-independent guard-sync assertions for fdars MCP server constants.

This module provides guard-sync tests that run on ALL supported Python
versions including 3.9.  It does NOT import ``mcp`` and does NOT import
``fdars.mcp.server`` at module level (importing that module pulls in ``mcp``,
which is unavailable on Python 3.9).

Guard Group 1 — _DIAGNOSTICS_METHODS (COMPAT-03):

Primary test (runs on Python 3.9+):
    Recovers the advisor's supported-method set by calling
    ``build_diagnostics({}, "__sentinel__")`` and parsing the ``ValueError``
    message — pure ``fdars.advisor`` import, no mcp dependency.  Asserts the
    recovered set equals a hard-coded expected frozenset that mirrors
    ``fdars.mcp.server._DIAGNOSTICS_METHODS``.

Companion test (guarded internally to Python 3.10+):
    Imports ``fdars.mcp.server._DIAGNOSTICS_METHODS`` and asserts it equals the
    same hard-coded frozenset, keeping the literal honest on 3.10+.

Guard Group 2 — _CAPABILITY_MODULES / fdars_list_capabilities (GATE-04):

Primary test (runs on Python 3.9+, no mcp import):
    Loads ``_capability_map.json`` via importlib.resources and asserts its
    submodule key set equals the hard-coded ``_EXPECTED_CAPABILITY_MODULES``.

Companion tests (guarded internally to Python 3.10+):
    (a) Calls ``fdars_list_capabilities(None)`` and asserts no provider/model
        keys in the return value (LLM-free boundary, T-78-09).
    (b) Imports ``server._CAPABILITY_MODULES`` and asserts it equals
        ``_EXPECTED_CAPABILITY_MODULES`` (three-way literal mirror, T-78-10).
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
import urllib.parse
from importlib import resources

import pytest

# ---------------------------------------------------------------------------
# Expected diagnostics method set — hard-coded mirror of
# fdars.mcp.server._DIAGNOSTICS_METHODS.
#
# MAINTENANCE NOTE: this frozenset MUST equal fdars.mcp.server._DIAGNOSTICS_METHODS
# AND build_diagnostics._supported.  Update all three in one atomic commit when
# adding a new aspect (guard-sync invariant T-22-07 / COMPAT-03).
# ---------------------------------------------------------------------------

_EXPECTED_DIAGNOSTICS_METHODS: frozenset[str] = frozenset(
    {
        # Runnable aspects (also in _RUNNABLE_METHODS)
        "alignment",
        "fpca",
        "basis",
        "smoothing",
        "clustering",
        "depth",
        # Diagnostics-only aspects
        "outliers",
        "classification",
        "represent",
        "regression",
        "regression_cv",
        "spm",
        "scoring",
        "inference",
        "fts",     # ADV-01 Phase 72
        "frechet", # ADV-01 Phase 72
    }
)


# ---------------------------------------------------------------------------
# PRIMARY TEST — runs on Python 3.9+ (no mcp import)
# ---------------------------------------------------------------------------


def test_guard_sync_version_independent():
    """Guard-sync: advisor._supported equals _EXPECTED_DIAGNOSTICS_METHODS (Python 3.9+).

    Recovers the advisor's canonical supported-method set without importing mcp:
    1. Calls ``build_diagnostics({}, "__sentinel_not_a_method__")`` to provoke a
       ``ValueError`` whose message embeds the full sorted supported list.
    2. Parses the bracketed list via ``ast.literal_eval``.
    3. Asserts the parsed set equals ``_EXPECTED_DIAGNOSTICS_METHODS`` (the
       hard-coded mirror of ``fdars.mcp.server._DIAGNOSTICS_METHODS``).

    Fails if:
    - A new aspect is added to ``build_diagnostics`` but not to
      ``_EXPECTED_DIAGNOSTICS_METHODS`` (stale literal — update it in sync with
      _DIAGNOSTICS_METHODS and the advisor _supported set).
    - An entry in ``_EXPECTED_DIAGNOSTICS_METHODS`` no longer exists in
      ``build_diagnostics._supported`` (phantom entry).

    Reference: COMPAT-03 — no ``pytestmark`` skip; this test MUST run on Python 3.9.
    """
    from fdars.advisor import build_diagnostics  # noqa: PLC0415

    _sentinel = "__sentinel_not_a_method_compat03__"
    try:
        build_diagnostics({}, _sentinel)
    except ValueError as exc:
        advisor_error_msg = str(exc)
    else:
        pytest.fail(
            f"build_diagnostics did not raise ValueError for sentinel {_sentinel!r}. "
            "The advisor may no longer validate the method name — check "
            "build_diagnostics implementation."
        )

    # Verify the error message contains the expected prefix so substring parsing
    # is meaningful.
    assert "Supported:" in advisor_error_msg, (
        f"Unexpected advisor error message format (no 'Supported:' prefix): "
        f"{advisor_error_msg!r}"
    )

    # Parse the sorted list embedded in the error message.
    # Format: "build_diagnostics: unsupported method '...'. Supported: ['a', 'b', ...]."
    list_start = advisor_error_msg.index("[")
    list_end = advisor_error_msg.rindex("]") + 1
    advisor_supported = frozenset(
        ast.literal_eval(advisor_error_msg[list_start:list_end])
    )

    assert advisor_supported == _EXPECTED_DIAGNOSTICS_METHODS, (
        f"advisor._supported != _EXPECTED_DIAGNOSTICS_METHODS (COMPAT-03 drift).\n"
        f"  In advisor only:   {advisor_supported - _EXPECTED_DIAGNOSTICS_METHODS}\n"
        f"  In expected only:  {_EXPECTED_DIAGNOSTICS_METHODS - advisor_supported}\n"
        "Update _EXPECTED_DIAGNOSTICS_METHODS to match advisor._supported and "
        "fdars.mcp.server._DIAGNOSTICS_METHODS in one atomic commit."
    )


# ---------------------------------------------------------------------------
# COMPANION TEST — internally guarded to Python 3.10+ (keeps the literal honest)
# ---------------------------------------------------------------------------


def test_guard_sync_mcp_server_matches_expected():
    """Guard-sync companion: fdars.mcp.server._DIAGNOSTICS_METHODS equals hard-coded set.

    Internally guarded to Python 3.10+ via ``pytest.importorskip("mcp")``.
    On Python 3.9 this test is skipped (the mcp package is absent), but the
    primary test above still runs and catches advisor drift.

    On Python 3.10+ this test imports ``fdars.mcp.server._DIAGNOSTICS_METHODS``
    and asserts it equals ``_EXPECTED_DIAGNOSTICS_METHODS``, keeping the
    hard-coded literal in sync with the actual server constant.

    Reference: COMPAT-03.
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    mcp = pytest.importorskip("mcp")  # noqa: F841  # skip if mcp not installed

    from fdars.mcp.server import _DIAGNOSTICS_METHODS  # noqa: PLC0415

    assert _DIAGNOSTICS_METHODS == _EXPECTED_DIAGNOSTICS_METHODS, (
        f"fdars.mcp.server._DIAGNOSTICS_METHODS != _EXPECTED_DIAGNOSTICS_METHODS "
        f"(COMPAT-03 drift — update the hard-coded literal in this test file to "
        f"match _DIAGNOSTICS_METHODS).\n"
        f"  In _DIAGNOSTICS_METHODS only: {_DIAGNOSTICS_METHODS - _EXPECTED_DIAGNOSTICS_METHODS}\n"
        f"  In _EXPECTED only:            {_EXPECTED_DIAGNOSTICS_METHODS - _DIAGNOSTICS_METHODS}"
    )


# ===========================================================================
# Guard Group 2 — _CAPABILITY_MODULES / fdars_list_capabilities (GATE-04)
# ===========================================================================

# ---------------------------------------------------------------------------
# Expected capability modules — hard-coded mirror of _CAPABILITY_MODULES in
# fdars.mcp.server AND the submodule keys of python/fdars/_capability_map.json
# (i.e. all top-level JSON keys except '_Fdata').
#
# MAINTENANCE NOTE: update _EXPECTED_CAPABILITY_MODULES here,
# _CAPABILITY_MODULES in fdars.mcp.server, and regenerate _capability_map.json
# — all in one atomic commit — when adding a new submodule to fdars/__init__.py.
# ---------------------------------------------------------------------------

_EXPECTED_CAPABILITY_MODULES: frozenset[str] = frozenset({
    "alignment", "basis", "classification", "clustering", "conformal",
    "covariance", "datasets", "density_fda", "depth", "explain", "famm",
    "fdata", "frechet", "fts", "inference", "metric", "metrics", "multi_fdata",
    "outliers", "pace_fpca", "regression", "represent", "scalar_on_function",
    "scoring", "seasonal", "shapelet", "simulation", "smoothing", "spm",
    "tolerance",
})


# ---------------------------------------------------------------------------
# PRIMARY TEST — runs on Python 3.9+ (no mcp import, no fdars.mcp.server import)
# ---------------------------------------------------------------------------


def test_capability_map_modules_match_expected():
    """Guard-sync: JSON submodule keys == _EXPECTED_CAPABILITY_MODULES (Python 3.9+).

    Loads the committed ``_capability_map.json`` directly via
    ``importlib.resources`` (no mcp dependency; Py 3.9-safe) and asserts its
    top-level keys — excluding the special ``'_Fdata'`` class entry — equal
    the hard-coded expected frozenset.

    Fails if:
    - A new module was added to fdars but the JSON was not regenerated.
    - ``_EXPECTED_CAPABILITY_MODULES`` is stale (update it, regenerate JSON,
      update ``_CAPABILITY_MODULES`` in server.py — all in one atomic commit).

    Reference: GATE-04 — no skip; this test MUST run on Python 3.9.
    """
    cap_file = resources.files("fdars") / "_capability_map.json"
    data: dict = json.loads(cap_file.read_text(encoding="utf-8"))
    # Exclude the special _Fdata class entry; compare submodule keys only.
    actual = frozenset(data.keys()) - {"_Fdata"}

    assert actual == _EXPECTED_CAPABILITY_MODULES, (
        f"_capability_map.json submodule keys != _EXPECTED_CAPABILITY_MODULES.\n"
        f"  In JSON only:     {actual - _EXPECTED_CAPABILITY_MODULES}\n"
        f"  In expected only: {_EXPECTED_CAPABILITY_MODULES - actual}\n"
        "Regenerate: python scripts/generate_capability_dataset.py\n"
        "Then update _EXPECTED_CAPABILITY_MODULES here and _CAPABILITY_MODULES "
        "in fdars.mcp.server in one atomic commit."
    )


# ---------------------------------------------------------------------------
# COMPANION TESTS — internally guarded to Python 3.10+ (keeps MCP literals honest)
# ---------------------------------------------------------------------------


def test_capability_tool_llm_free_boundary():
    """Guard-sync companion: fdars_list_capabilities returns LLM-free result.

    Internally guarded to Python 3.10+ (mcp requires 3.10+).  Asserts:
    - The tool is callable.
    - Result has a ``'modules'`` key.
    - Result has NO ``'provider'`` or ``'model'`` key (LLM-free boundary, T-78-09).
    - Returned module set equals ``_EXPECTED_CAPABILITY_MODULES`` (excluding
      ``'_Fdata'`` which is present in the underlying JSON but not a submodule).

    Reference: GATE-04.
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    pytest.importorskip("mcp")  # skip if mcp not installed

    from fdars.mcp.server import fdars_list_capabilities  # noqa: PLC0415

    result = fdars_list_capabilities(module=None)

    # Shape assertions
    assert "modules" in result, "fdars_list_capabilities must return 'modules' key"
    assert isinstance(result["modules"], dict)

    # LLM-free boundary: no model/provider keys (T-78-09)
    assert "provider" not in result, (
        "fdars_list_capabilities must NOT expose 'provider' key (LLM-free boundary)"
    )
    assert "model" not in result, (
        "fdars_list_capabilities must NOT expose 'model' key (LLM-free boundary)"
    )

    # Module set consistency (full return includes _Fdata from the JSON; exclude it)
    returned_modules = frozenset(result["modules"].keys()) - {"_Fdata"}
    assert returned_modules == _EXPECTED_CAPABILITY_MODULES, (
        f"fdars_list_capabilities returned modules != _EXPECTED_CAPABILITY_MODULES.\n"
        f"  Returned only:    {returned_modules - _EXPECTED_CAPABILITY_MODULES}\n"
        f"  Expected only:    {_EXPECTED_CAPABILITY_MODULES - returned_modules}"
    )


def test_capability_mcp_server_frozenset_matches():
    """Guard-sync companion: server._CAPABILITY_MODULES == expected frozenset.

    Internally guarded to Python 3.10+ via pytest.importorskip.  Asserts the
    hard-coded literal ``_CAPABILITY_MODULES`` in ``fdars.mcp.server`` equals
    ``_EXPECTED_CAPABILITY_MODULES``, keeping the three-way mirror honest
    (server == JSON keys == test expected; T-78-10).

    Reference: GATE-04.
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    pytest.importorskip("mcp")

    from fdars.mcp.server import _CAPABILITY_MODULES  # noqa: PLC0415

    assert _CAPABILITY_MODULES == _EXPECTED_CAPABILITY_MODULES, (
        f"server._CAPABILITY_MODULES != _EXPECTED_CAPABILITY_MODULES.\n"
        f"  In server only:   {_CAPABILITY_MODULES - _EXPECTED_CAPABILITY_MODULES}\n"
        f"  In expected only: {_EXPECTED_CAPABILITY_MODULES - _CAPABILITY_MODULES}\n"
        "Update _CAPABILITY_MODULES in server.py to match."
    )


# ===========================================================================
# Guard Group 3 — _references_map.json primary GATE-05 (SCHEMA-03)
# ===========================================================================

# ---------------------------------------------------------------------------
# PRIMARY TEST A — runs on Python 3.9+ (no mcp import, no fdars.mcp.server import)
# ---------------------------------------------------------------------------


def test_references_map_internal_consistency():
    """GATE-05 A: callable_index keys == union of papers[*].callables (Python 3.9+).

    Loads the committed ``_references_map.json`` via importlib.resources (no
    mcp dependency; Py 3.9-safe) and asserts the internal consistency invariant:

        frozenset(callable_index.keys())
            == frozenset(c for p in papers.values() for c in p["callables"])

    Fails if:
    - A paper's callables list contains a key not in callable_index (orphan callable).
    - callable_index contains a key with no paper referencing it (phantom index entry).

    Reference: GATE-05 A — no skip; this test MUST run on Python 3.9.
    """
    ref_file = resources.files("fdars") / "_references_map.json"
    data: dict = json.loads(ref_file.read_text(encoding="utf-8"))

    papers = data.get("papers", {})
    callable_index = data.get("callable_index", {})

    from_papers: frozenset[str] = frozenset(
        c for p in papers.values() for c in p.get("callables", [])
    )
    from_index: frozenset[str] = frozenset(callable_index.keys())

    assert from_papers == from_index, (
        f"_references_map.json internal consistency failure (GATE-05 A).\n"
        f"  In papers but not in callable_index: {from_papers - from_index}\n"
        f"  In callable_index but not in any paper: {from_index - from_papers}\n"
        "Ensure every callable in papers[*].callables appears in callable_index "
        "and vice versa."
    )


# ---------------------------------------------------------------------------
# PRIMARY TEST B — runs on Python 3.9+ (no mcp import)
# ---------------------------------------------------------------------------


def test_references_map_cross_file_resolution():
    """GATE-05 B: every callable_index key resolves in _capability_map.json (Python 3.9+).

    Loads both ``_references_map.json`` and ``_capability_map.json`` via
    importlib.resources and asserts every key in ``callable_index`` resolves to
    an existing callable in the capability map:

    - For ``"module.callable"`` keys: ``cap_data["module"]["callable"]`` must exist.
    - For ``"_Fdata.<method>"`` keys: ``cap_data["_Fdata"]["<method>"]`` must exist.

    Fails if a key in callable_index refers to a callable that does not exist
    in the capability map (renamed, removed, or mistyped callable).

    Reference: GATE-05 B — no skip; this test MUST run on Python 3.9.
    """
    ref_file = resources.files("fdars") / "_references_map.json"
    cap_file = resources.files("fdars") / "_capability_map.json"

    ref_data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
    cap_data: dict = json.loads(cap_file.read_text(encoding="utf-8"))

    callable_index = ref_data.get("callable_index", {})
    unresolved: list[str] = []

    for key in callable_index:
        if "." not in key:
            unresolved.append(f"{key!r} — no dot separator")
            continue
        module, callable_name = key.split(".", 1)
        if module not in cap_data:
            unresolved.append(f"{key!r} — module {module!r} not in capability map")
        elif callable_name not in cap_data[module]:
            unresolved.append(
                f"{key!r} — {callable_name!r} not in capability_map[{module!r}]"
            )

    assert not unresolved, (
        f"_references_map.json cross-file resolution failures (GATE-05 B):\n"
        + "\n".join(f"  - {e}" for e in unresolved)
        + "\nEnsure all callable_index keys exist in _capability_map.json. "
        "If a callable was renamed, update _references_map.json to match."
    )


# ---------------------------------------------------------------------------
# PRIMARY TEST C — runs on Python 3.9+ — STRUCTURAL DOI/URL gate (no live resolve)
# ---------------------------------------------------------------------------

_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")

# Domain allowlist for cross-language entry URLs and paper landing pages.
# Extend this list in Phase 81/84 as new reference domains are verified.
_ALLOWED_DOMAINS = frozenset({
    # Publisher / preprint hosts
    "doi.org", "link.springer.com", "www.tandfonline.com",
    "academic.oup.com", "onlinelibrary.wiley.com", "rss.onlinelibrary.wiley.com",
    "www.sciencedirect.com", "dl.acm.org", "ieeexplore.ieee.org",
    "www.jstor.org", "projecteuclid.org", "arxiv.org", "www.researchgate.net",
    "pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
    # Cross-language reference hosts (R, Python)
    "rdrr.io", "cran.r-project.org", "www.rdocumentation.org",
    "pypi.org", "fdasrsf-python.readthedocs.io",
    # fdars own docs
    "sipemu.github.io",
    # Phase 81 additions — publisher hosts
    "www3.stat.sinica.edu.tw",   # Statistica Sinica (Degras 2011, Shen & Faraway 2004)
    "proceedings.mlr.press",      # PMLR (Cuturi & Blondel 2017 soft-DTW)
    "journals.sagepub.com",       # SAGE Journals (Volkmann et al. 2023 multiFAMM)
    # Phase 81 additions — cross-language package docs (Python)
    "tslearn.readthedocs.io",     # tslearn (DTW, GAK, soft-DTW cross-language)
    "fda.readthedocs.io",         # scikit-fda (functional data cross-language)
    "www.sktime.net",             # sktime (shapelet cross-language)
    # Phase 81 additions — conditionally needed (later batches)
    "epubs.siam.org",             # SIAM (Agueh & Carlier 2011 Wasserstein)
    "icml.cc",                    # ICML (alternative Cuturi 2011 landing page)
    "www.stat.ucdavis.edu",       # UC Davis PACE Matlab tool
})


def test_references_map_doi_url_structural_gate():
    """GATE-05 C: structural DOI regex + URL well-formedness (NO live resolve).

    Checks every paper entry in _references_map.json for:
    - doi: matches ^10\\.\\d{4,9}/\\S+$ (SCHEMA-04 DOI regex)
    - url: well-formed http/https URL; domain in _ALLOWED_DOMAINS

    For cross_language entries:
    - url: well-formed http/https URL; domain in _ALLOWED_DOMAINS

    NO live network resolve is performed. FDARS_ONLINE_CHECKS=1 is checked and
    test raises pytest.skip if the env var is set (live resolve is opt-in only).

    Reference: SCHEMA-04 — no mcp import; runs on Python 3.9+.
    """
    if os.environ.get("FDARS_ONLINE_CHECKS") == "1":
        pytest.skip("FDARS_ONLINE_CHECKS=1 set — live resolve path; structural gate skipped.")

    ref_file = resources.files("fdars") / "_references_map.json"
    data: dict = json.loads(ref_file.read_text(encoding="utf-8"))

    errors: list[str] = []
    papers = data.get("papers", {})

    for key, paper in papers.items():
        doi = paper.get("doi", "")
        url = paper.get("url", "")

        # DOI structural check (skip empty doi for curated:false entries)
        if paper.get("curated", True) and doi:
            if not _DOI_RE.match(doi):
                errors.append(
                    f"papers[{key!r}].doi {doi!r} does not match ^10.\\d{{4,9}}/\\S+$"
                )

        # URL presence check for curated entries (url is required per schema)
        if paper.get("curated", True) and not url:
            errors.append(
                f"papers[{key!r}] is curated:true but has no url (url is required)"
            )

        # URL well-formedness + domain check
        if url:
            try:
                parsed = urllib.parse.urlparse(url)
                if parsed.scheme not in ("http", "https"):
                    errors.append(f"papers[{key!r}].url {url!r} — scheme must be http/https")
                elif parsed.netloc not in _ALLOWED_DOMAINS:
                    errors.append(
                        f"papers[{key!r}].url domain {parsed.netloc!r} not in _ALLOWED_DOMAINS"
                    )
            except Exception as exc:
                errors.append(f"papers[{key!r}].url {url!r} — parse error: {exc}")

        # Cross-language required-field presence checks (package, function, url, confidence)
        for lang, cl_entry in paper.get("cross_language", {}).items():
            for required_field in ("package", "function", "url", "confidence"):
                if required_field not in cl_entry:
                    errors.append(
                        f"papers[{key!r}].cross_language[{lang!r}] missing required "
                        f"field {required_field!r}"
                    )
            cl_url = cl_entry.get("url", "")
            if cl_url:
                try:
                    parsed = urllib.parse.urlparse(cl_url)
                    if parsed.scheme not in ("http", "https"):
                        errors.append(
                            f"papers[{key!r}].cross_language[{lang!r}].url {cl_url!r} — "
                            "scheme must be http/https"
                        )
                    elif parsed.netloc not in _ALLOWED_DOMAINS:
                        errors.append(
                            f"papers[{key!r}].cross_language[{lang!r}].url domain "
                            f"{parsed.netloc!r} not in _ALLOWED_DOMAINS"
                        )
                except Exception as exc:
                    errors.append(
                        f"papers[{key!r}].cross_language[{lang!r}].url — parse error: {exc}"
                    )

    assert not errors, (
        "Structural DOI/URL gate failures (SCHEMA-04):\n"
        + "\n".join(f"  - {e}" for e in errors)
    )


# ---------------------------------------------------------------------------
# COVERAGE TEST — runs on Python 3.9+ — honest N/437 fraction emission
# ---------------------------------------------------------------------------
# NOTE: 409 was the stale roadmap-time estimate of the callable count.
# The real denominator is derived at test-time from _capability_map.json
# (437 at authoring time, 2026-09-07). A hardcoded denominator would desync
# whenever a new crate version adds or removes callables; recomputing from the
# live file keeps this test honest across crate bumps.


def test_references_map_coverage_fraction():
    """GATE-05 coverage emission: print N/437 fraction derived from _capability_map.json.

    Loads _references_map.json and _capability_map.json via importlib.resources.
    Computes:
      denominator = sum(len(v) for v in cap_data.values()) — from the live file,
                    NOT hardcoded, so a future crate-bump cannot silently desync it.
      numerator   = count of DISTINCT callable_index keys where at least one
                    referenced paper has curated:true.

    Prints "COVERAGE: {numerator}/{denominator} callables curated ..." for
    surfacing under pytest -s.

    Asserts:
      - denominator == 437 as a drift tripwire (update this constant if the
        capability map legitimately grows — it exists to catch accidental
        capability-map changes, not to block intentional growth).
      - 0 <= numerator <= denominator (sanity bound).

    No hard coverage floor — a floor is deferred to REF-FUT-01 per CONTEXT.md.
    """
    ref_file = resources.files("fdars") / "_references_map.json"
    cap_file = resources.files("fdars") / "_capability_map.json"
    ref_data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
    cap_data: dict = json.loads(cap_file.read_text(encoding="utf-8"))

    # Denominator: recomputed from the live capability map (never hardcoded)
    denominator = sum(len(v) for v in cap_data.values())

    papers = ref_data.get("papers", {})
    callable_index = ref_data.get("callable_index", {})

    # Build set of paper_keys that have curated:true
    curated_paper_keys = frozenset(
        pk for pk, paper in papers.items() if paper.get("curated", False) is True
    )

    # Numerator: distinct callable_index keys backed by at least one curated paper
    numerator = sum(
        1
        for callable_key, paper_keys in callable_index.items()
        if any(pk in curated_paper_keys for pk in paper_keys)
    )

    print(
        f"COVERAGE: {numerator}/{denominator} callables curated "
        f"({100 * numerator / denominator:.1f}% of fdars callable surface)"
    )

    # Drift tripwire: update the expected count if capability map legitimately grew
    assert denominator == 437, (
        f"_capability_map.json callable count changed: expected 437, got {denominator}. "
        "If a crate bump added/removed callables intentionally, update this constant "
        "in test_references_map_coverage_fraction. If unexpected, investigate."
    )
    assert 0 <= numerator <= denominator, (
        f"Numerator {numerator} out of bounds [0, {denominator}]"
    )
