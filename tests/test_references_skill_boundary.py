"""SKILL-02: Skill-boundary tests for the Scientific Provenance Protocol.

Exercises both routing branches defined in the fdars-capabilities skill's
``## Scientific Provenance Protocol`` section:

- Path A (curated hit): ``fdars_method_references`` returns ``curated: True``
  when the callable has at least one curated backing paper.
- Path C (NO_CURATED_ENTRY sentinel): ``fdars_method_references`` returns
  ``curated: False`` and ``sentinel == "NO_CURATED_ENTRY"`` when the callable
  is absent from ``callable_index``.

Both tests skip cleanly on Python 3.9 (where ``mcp`` is unavailable) via
``pytest.importorskip("mcp")``.  On Python 3.10+ with ``fdars[mcp]`` installed
they run against the live MCP handler.

References
----------
- .claude/skills/fdars-capabilities/SKILL.md — Scientific Provenance Protocol
- tests/test_guard_sync_version_independent.py — existing GATE-05 C guard
  (same hit/miss pair used as canonical examples)
"""

import pytest


def test_references_curated_hit_returns_curated_true():
    """SKILL-02 Path A: fdars_method_references curated hit returns curated:True.

    ``depth.fraiman_muniz_1d`` is backed by ``fraiman_muniz_2001`` (curated:true
    in ``_references_map.json``).  Per the skill's Path A rule, the response
    must have ``curated: True`` and at least one paper with ``curated: True``.
    """
    pytest.importorskip("mcp", reason="mcp not installed (Python 3.9 or fdars[mcp] absent)")
    from fdars.mcp.server import fdars_method_references  # noqa: PLC0415

    result = fdars_method_references("depth.fraiman_muniz_1d")

    assert result["curated"] is True, (
        "Expected curated:True for depth.fraiman_muniz_1d "
        "(backed by fraiman_muniz_2001, curated:true)"
    )
    assert "papers" in result and len(result["papers"]) >= 1, (
        "Hit response must include at least one paper"
    )
    assert any(p["curated"] for p in result["papers"]), (
        "At least one paper in the response must have curated:True (Path A)"
    )


def test_references_sentinel_returns_no_curated_entry():
    """SKILL-02 Path C: fdars_method_references returns NO_CURATED_ENTRY sentinel.

    ``explain.shap_values`` is absent from ``callable_index`` in
    ``_references_map.json``.  Per the skill's Path C rule, the response must
    have ``curated: False`` and ``sentinel == "NO_CURATED_ENTRY"``.
    """
    pytest.importorskip("mcp", reason="mcp not installed (Python 3.9 or fdars[mcp] absent)")
    from fdars.mcp.server import fdars_method_references  # noqa: PLC0415

    result = fdars_method_references("explain.shap_values")

    assert result["curated"] is False, (
        "Expected curated:False for explain.shap_values (absent from callable_index)"
    )
    assert result.get("sentinel") == "NO_CURATED_ENTRY", (
        "Expected sentinel='NO_CURATED_ENTRY' for a callable absent from callable_index"
    )
