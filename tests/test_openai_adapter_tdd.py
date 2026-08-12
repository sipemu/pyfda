"""TDD RED phase for OpenAIProvider adapter.

These tests drive the implementation of python/fdars/advisor/providers/openai.py.
Run: pytest tests/test_openai_adapter_tdd.py -q

All tests are offline (no openai SDK installed; fake module via sys.modules).
"""
from __future__ import annotations

import sys
import types
import importlib

import pytest


def _make_fake_openai():
    """Return a fake openai module with a MagicMock OpenAI class."""
    from unittest.mock import MagicMock
    fake = types.ModuleType("openai")
    fake.OpenAI = MagicMock()
    fake.__version__ = "1.40.0"
    return fake


@pytest.fixture()
def fake_openai(monkeypatch):
    """Install a fake openai module for the duration of a test."""
    fake = _make_fake_openai()
    monkeypatch.setitem(sys.modules, "openai", fake)
    yield fake


def test_openai_provider_importable_without_sdk():
    """OpenAIProvider must be importable even when openai SDK is absent (deferred import)."""
    from fdars.advisor.providers.openai import OpenAIProvider  # noqa: PLC0415
    assert OpenAIProvider.name == "openai"
    assert OpenAIProvider.supports_native_structured_output is True


def test_openai_schema_helper_strips_title(fake_openai, monkeypatch):
    """_openai_schema must return schema without a top-level 'title' key."""
    if "fdars.advisor.providers.openai" in sys.modules:
        del sys.modules["fdars.advisor.providers.openai"]
    from fdars.advisor.providers.openai import _openai_schema
    from fdars.advisor._schema import Advice
    s = _openai_schema(Advice)
    assert "title" not in s
    assert s["type"] == "object"
