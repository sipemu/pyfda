"""Provider protocol for fdars.advisor.

Defines the Provider structural interface that all LLM adapters must satisfy.
Uses typing.Protocol (runtime_checkable) so duck-typed fakes pass isinstance
checks without inheriting from this class.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    """Structural interface for LLM backend adapters.

    Attributes
    ----------
    name : str
        Provider identifier, e.g. ``"anthropic"``.
    model : str
        Model identifier, e.g. ``"claude-opus-4-8"``.
    supports_native_structured_output : bool
        True if the backend enforces schema natively (e.g. Anthropic
        ``messages.parse``); False if JSON must be parsed and validated
        by ``ValidateAndRetry``.
    """

    name: str
    model: str
    supports_native_structured_output: bool

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        """Return a validated schema instance.

        Parameters
        ----------
        schema : type
            Pydantic model class to validate against (e.g. ``Advice``).
        messages : list[dict]
            Conversation messages, e.g. ``[{"role": "user", "content": "..."}]``.
        system : str
            System prompt (contains the grounding invariant).

        Returns
        -------
        object
            A validated schema instance (e.g. ``Advice``).

        Raises
        ------
        ValueError
            On provider refusal, empty response, or unrecoverable failure.
        """
        ...
