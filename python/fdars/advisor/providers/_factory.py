"""Provider factory for fdars.advisor.

``resolve_provider()`` implements the selection/precedence logic (PROV-06):
explicit arguments > environment variables > Anthropic default.
"""
from __future__ import annotations

import os


def resolve_provider(
    provider: "str | object | None" = None,
    model: "str | None" = None,
    api_key: "str | None" = None,
    base_url: "str | None" = None,
    **kw: object,
) -> object:
    """Return a ``ValidateAndRetry``-wrapped ``Provider`` adapter.

    Precedence (highest to lowest):

    1. Explicit ``provider=`` argument (string name or Provider instance).
    2. ``FDARS_ADVISOR_PROVIDER`` environment variable.
    3. Default: ``"anthropic"`` (backward compatible with today's behavior).

    Model precedence (highest to lowest):

    1. Explicit ``model=`` argument.
    2. ``FDARS_ADVISOR_MODEL`` environment variable.
    3. Provider default (``"claude-opus-4-8"`` for Anthropic).

    Parameters
    ----------
    provider : str or Provider or None
        Provider name (``"anthropic"``) or an existing ``Provider`` instance.
        When ``None``, uses ``FDARS_ADVISOR_PROVIDER`` env or Anthropic default.
    model : str or None
        Model identifier.  When ``None``, uses ``FDARS_ADVISOR_MODEL`` env or
        the provider's built-in default.
    api_key : str or None
        Explicit API key.  When ``None``, uses the per-provider key env var
        (e.g. ``ANTHROPIC_API_KEY``).
    base_url : str or None
        Custom base URL for the provider API.  When ``None``, uses
        ``FDARS_ADVISOR_BASE_URL`` env var.  Currently only consumed by the
        Anthropic adapter constructor if the SDK supports it (reserved for
        Phase 20 providers).
    **kw
        Ignored; reserved for future providers.

    Returns
    -------
    ValidateAndRetry
        A ``ValidateAndRetry``-wrapped adapter.

    Raises
    ------
    ValueError
        When ``provider`` is an unknown string name.  Only ``"anthropic"`` is
        supported in Phase 19; additional providers are added in Phase 20.
    """
    from fdars.advisor.providers._validate import ValidateAndRetry  # noqa: PLC0415
    from fdars.advisor.providers._protocol import Provider as _ProviderProtocol  # noqa: PLC0415

    # If the caller passed an existing Provider instance, wrap and return.
    if isinstance(provider, _ProviderProtocol):
        return ValidateAndRetry(provider)

    provider_name: str = (
        provider  # type: ignore[assignment]
        or os.environ.get("FDARS_ADVISOR_PROVIDER")
        or "anthropic"
    )
    resolved_model: str = (
        model
        or os.environ.get("FDARS_ADVISOR_MODEL")
        or _DEFAULT_MODELS.get(provider_name, "")
    )
    resolved_key: "str | None" = api_key or os.environ.get(
        _KEY_ENV.get(provider_name, ""), None
    )
    # base_url: reserved for Phase 20 adapters; resolve and pass through
    resolved_base_url: "str | None" = base_url or os.environ.get(
        "FDARS_ADVISOR_BASE_URL"
    )
    _ = resolved_base_url  # consumed by Phase 20 adapters

    if provider_name == "anthropic":
        from fdars.advisor.providers.anthropic import AnthropicProvider  # noqa: PLC0415

        adapter = AnthropicProvider(model=resolved_model, api_key=resolved_key)
    else:
        raise ValueError(
            f"resolve_provider: unknown provider {provider_name!r}. "
            f"Supported in Phase 19: 'anthropic'. "
            f"Additional providers (openai, gemini, ollama) are added in Phase 20."
        )

    return ValidateAndRetry(adapter)


_DEFAULT_MODELS: dict = {
    "anthropic": "claude-opus-4-8",
    # Phase 20: "openai": "gpt-4o", "gemini": "gemini-2.0-flash", "ollama": "llama3.2"
}

_KEY_ENV: dict = {
    "anthropic": "ANTHROPIC_API_KEY",
    # Phase 20: "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"
}
