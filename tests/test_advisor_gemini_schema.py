"""Offline tests for the _gemini_schema translation helper.

All tests are network-free, SDK-free.  The helper depends only on pydantic
(which IS installed in the venv).  No google-genai import is required or
performed.

Requirements covered:
    PROV-05  Gemini schema translation strips disallowed keys and resolves refs
    T-20-08  Over-permissive schema translation must not loosen constraints
"""
from __future__ import annotations

import json

import pytest

from fdars.advisor._schema import Advice


# ---------------------------------------------------------------------------
# Test 1: additionalProperties stripped from output
# ---------------------------------------------------------------------------


def test_additional_properties_stripped():
    """_gemini_schema output contains no 'additionalProperties' substring."""
    from fdars.advisor.providers.gemini import _gemini_schema

    result = _gemini_schema(Advice)
    serialised = json.dumps(result)
    assert "additionalProperties" not in serialised, (
        "additionalProperties must be stripped from the Gemini schema "
        f"(found in: {serialised!r})"
    )


# ---------------------------------------------------------------------------
# Test 2: $ref and $defs resolved (inlined)
# ---------------------------------------------------------------------------


def test_ref_and_defs_absent():
    """_gemini_schema output contains no '$ref' or '$defs' (resolved inline)."""
    from fdars.advisor.providers.gemini import _gemini_schema

    result = _gemini_schema(Advice)
    serialised = json.dumps(result)
    assert "$ref" not in serialised, (
        f"'$ref' must be resolved inline for Gemini; found in: {serialised!r}"
    )
    assert "$defs" not in serialised, (
        f"'$defs' must be absent from the Gemini schema; found in: {serialised!r}"
    )


# ---------------------------------------------------------------------------
# Test 3: kind enum preserved at the nested Recommendation path
# ---------------------------------------------------------------------------


def test_kind_enum_preserved():
    """The kind Literal enum is preserved at the nested Recommendation path."""
    from fdars.advisor.providers.gemini import _gemini_schema

    result = _gemini_schema(Advice)

    # Navigate: properties -> recommendations -> items -> properties -> kind -> enum
    try:
        kind_schema = (
            result["properties"]["recommendations"]["items"]["properties"]["kind"]
        )
    except (KeyError, TypeError) as exc:
        pytest.fail(
            f"Expected nested path properties.recommendations.items.properties.kind "
            f"to exist in the translated schema; got {exc!r}. "
            f"Full schema: {json.dumps(result, indent=2)}"
        )

    assert "enum" in kind_schema, (
        f"kind field must have an 'enum' key in the Gemini schema; "
        f"got {kind_schema!r}"
    )
    assert kind_schema["enum"] == ["parameter", "method", "none"], (
        f"kind enum values must be preserved as ['parameter', 'method', 'none']; "
        f"got {kind_schema['enum']!r}"
    )


# ---------------------------------------------------------------------------
# Test 4: required arrays preserved on root and inlined Recommendation
# ---------------------------------------------------------------------------


def test_required_arrays_preserved():
    """required fields are preserved on both root (Advice) and inlined Recommendation."""
    from fdars.advisor.providers.gemini import _gemini_schema

    result = _gemini_schema(Advice)

    # Root Advice required fields
    assert "required" in result, (
        f"Root schema must have a 'required' array; got keys: {list(result.keys())!r}"
    )
    root_required = set(result["required"])
    assert "interpretation" in root_required, (
        f"'interpretation' must be in root required; got {root_required!r}"
    )
    assert "recommendations" in root_required, (
        f"'recommendations' must be in root required; got {root_required!r}"
    )
    assert "caveats" in root_required, (
        f"'caveats' must be in root required; got {root_required!r}"
    )

    # Inlined Recommendation required fields
    try:
        rec_schema = result["properties"]["recommendations"]["items"]
    except (KeyError, TypeError) as exc:
        pytest.fail(
            f"Expected properties.recommendations.items to exist; got {exc!r}. "
            f"Full schema: {json.dumps(result, indent=2)}"
        )

    assert "required" in rec_schema, (
        f"Inlined Recommendation schema must have a 'required' array; "
        f"got keys: {list(rec_schema.keys())!r}"
    )
    rec_required = set(rec_schema["required"])
    for field in ("action", "kind", "rationale", "expected_effect", "evidence"):
        assert field in rec_required, (
            f"'{field}' must be in Recommendation required; got {rec_required!r}"
        )


# ---------------------------------------------------------------------------
# Test 5: title stripped (lean payload)
# ---------------------------------------------------------------------------


def test_title_stripped():
    """_gemini_schema output contains no 'title' key (lean payload)."""
    from fdars.advisor.providers.gemini import _gemini_schema

    result = _gemini_schema(Advice)
    serialised = json.dumps(result)
    # We check the JSON since nested 'title' keys are the main concern
    assert '"title"' not in serialised, (
        f"'title' keys must be stripped from the Gemini schema; "
        f"found in serialised output: {serialised!r}"
    )


# ---------------------------------------------------------------------------
# Test 6: original schema is not mutated
# ---------------------------------------------------------------------------


def test_original_schema_not_mutated():
    """_gemini_schema must not mutate the Pydantic schema (operates on a deepcopy)."""
    from fdars.advisor.providers.gemini import _gemini_schema

    original = Advice.model_json_schema()
    original_serialised = json.dumps(original, sort_keys=True)

    _gemini_schema(Advice)

    after = Advice.model_json_schema()
    after_serialised = json.dumps(after, sort_keys=True)

    assert original_serialised == after_serialised, (
        "_gemini_schema must not mutate the Pydantic model's schema. "
        f"Schema changed from {original_serialised!r} to {after_serialised!r}"
    )
