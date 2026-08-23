"""Version-independent guard-sync assertion: _DIAGNOSTICS_METHODS mirrors build_diagnostics._supported.

This module provides a guard-sync test that runs on ALL supported Python
versions including 3.9.  It does NOT import ``mcp`` and does NOT import
``fdars.mcp.server`` at module level (importing that module pulls in ``mcp``,
which is unavailable on Python 3.9).

Primary test (runs on Python 3.9+):
    Recovers the advisor's supported-method set by calling
    ``build_diagnostics({}, "__sentinel__")`` and parsing the ``ValueError``
    message — pure ``fdars.advisor`` import, no mcp dependency.  Asserts the
    recovered set equals a hard-coded expected frozenset that mirrors
    ``fdars.mcp.server._DIAGNOSTICS_METHODS``.

Companion test (guarded internally to Python 3.10+):
    Imports ``fdars.mcp.server._DIAGNOSTICS_METHODS`` and asserts it equals the
    same hard-coded frozenset, keeping the literal honest on 3.10+.

Reference: COMPAT-03.
"""

from __future__ import annotations

import ast
import sys

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
