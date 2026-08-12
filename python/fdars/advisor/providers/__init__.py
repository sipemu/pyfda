"""fdars.advisor.providers — LLM provider protocol and adapters.

Public exports:

- ``Provider`` — structural protocol (runtime_checkable)
- ``AnthropicProvider`` — Anthropic SDK adapter
- ``ValidateAndRetry`` — validation/repair wrapper for non-native providers
- ``resolve_provider`` — factory: params + env → ValidateAndRetry-wrapped adapter
- ``_check_grounding`` — centralized grounding validator (called by advise())
- ``GroundingViolationError`` — raised when evidence cites absent diagnostics values

Lazy-import policy
------------------
Importing this package does NOT load the ``anthropic`` SDK.  The SDK import is
deferred to ``AnthropicProvider.__init__`` (via ``_require_anthropic()``), which
is only called when a provider instance is constructed.  Constructing an
``AnthropicProvider`` (or calling ``resolve_provider()``) is the point where
the SDK must be present.
"""
from __future__ import annotations

from fdars.advisor.providers._protocol import Provider
from fdars.advisor.providers._validate import (
    ValidateAndRetry,
    _check_grounding,
    GroundingViolationError,
)
from fdars.advisor.providers._factory import resolve_provider
from fdars.advisor.providers.anthropic import AnthropicProvider

__all__ = [
    "Provider",
    "AnthropicProvider",
    "ValidateAndRetry",
    "resolve_provider",
    "_check_grounding",
    "GroundingViolationError",
]
