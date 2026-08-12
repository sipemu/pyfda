"""Gemini LLM adapter for fdars.advisor.

Wraps the ``google-genai`` SDK's ``Client.models.generate_content`` API into
the ``Provider`` protocol interface.  The Gemini backend uses native structured
output via ``response_json_schema`` in ``GenerateContentConfig``, so
``ValidateAndRetry`` returns the result directly without a repair loop.

Schema translation
------------------
Pydantic's ``model_json_schema()`` produces a schema that includes
``additionalProperties: false`` and uses ``$defs``/``$ref`` for nested models.
The ``google-genai`` SDK **rejects** schemas containing ``additionalProperties``
at the client-side validation layer (before the API call), and Gemini's API
does not support JSON Schema ``$ref``.  The ``_gemini_schema`` helper resolves
these incompatibilities.

Python version requirement
--------------------------
``google-genai>=1.0`` requires Python >=3.10.  ``GeminiProvider.__init__``
checks ``sys.version_info`` and raises a clear ``ImportError`` on older
interpreters before importing the SDK.

Deferred imports
----------------
Only ``from __future__ import annotations`` appears at module level.  All SDK
imports are deferred to ``__init__`` and ``complete_structured`` so that
``import fdars`` and ``build_diagnostics()`` both work with no provider SDK
installed (bare-venv compatibility — Pitfall 4).

Security note (T-20-07, T-20-08)
---------------------------------
``_gemini_schema`` only **strips** keys that the SDK/API rejects
(``additionalProperties``, ``$ref``/``$defs``, ``title``); it never loosens
constraints or removes ``required`` arrays or ``enum`` values.  Correctness
and constraint preservation are tested in ``tests/test_advisor_gemini_schema.py``.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Schema translation helpers (module-level functions, no SDK import required)
# ---------------------------------------------------------------------------


def _resolve_refs(obj: object, defs: dict) -> object:
    """Recursively resolve ``$ref`` pointers using the ``$defs`` map.

    When a dict contains a ``$ref`` key (e.g. ``{"$ref": "#/$defs/Recommendation"}``),
    it is replaced inline with a deepcopy of the matching ``$defs`` entry.
    The resolved value is recursed into to resolve any further ``$ref`` pointers.

    Parameters
    ----------
    obj : object
        The schema object to process (dict, list, or scalar).
    defs : dict
        The ``$defs`` map extracted from the top-level schema.

    Returns
    -------
    object
        The input with all ``$ref`` pointers replaced by their resolved values.
    """
    import copy as _copy  # noqa: PLC0415

    if isinstance(obj, dict):
        if "$ref" in obj:
            # e.g. "#/$defs/Recommendation" → "Recommendation"
            ref_name = obj["$ref"].split("/")[-1]
            resolved = _copy.deepcopy(defs.get(ref_name, obj))
            return _resolve_refs(resolved, defs)
        return {k: _resolve_refs(v, defs) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_refs(item, defs) for item in obj]
    return obj


def _strip_key(obj: object, key: str) -> None:
    """Recursively remove all occurrences of ``key`` from a nested dict in-place.

    Mutates the input dict (and its nested dicts/lists).  Should be called on
    a deepcopy of the original schema to avoid mutating Pydantic's cached schema.

    Parameters
    ----------
    obj : object
        The schema object to process (dict, list, or scalar).
    key : str
        The key to remove wherever it appears.
    """
    if isinstance(obj, dict):
        obj.pop(key, None)
        for v in obj.values():
            _strip_key(v, key)
    elif isinstance(obj, list):
        for item in obj:
            _strip_key(item, key)


def _gemini_schema(model_cls: type) -> dict:
    """Convert a Pydantic model to a Gemini ``response_json_schema``-compatible dict.

    The ``google-genai`` SDK's client validator rejects schemas containing
    ``additionalProperties``, even though the underlying API now supports it.
    Gemini's API also does not support JSON Schema ``$ref`` — nested definitions
    must be inlined.

    Transformation steps (applied to a deep copy; original schema never mutated):

    1. ``_resolve_refs``: inline every ``$ref`` from the ``$defs`` map.
    2. ``_strip_key("additionalProperties")``: remove client-rejected keys.
    3. ``_strip_key("title")``: keep the wire payload lean.

    The ``Literal["parameter", "method", "none"]`` field serialises to
    ``{"enum": [...], "type": "string"}`` which Gemini accepts unchanged —
    no special handling needed for enums.  ``required`` arrays are preserved
    on every object including the inlined ``Recommendation``.

    Parameters
    ----------
    model_cls : type
        Pydantic ``BaseModel`` subclass (e.g. ``Advice``).

    Returns
    -------
    dict
        JSON Schema dict safe to pass as ``response_json_schema`` to
        ``types.GenerateContentConfig``.

    Notes
    -----
    Security (T-20-08): this helper only strips keys that the SDK/API rejects;
    it never removes ``required`` arrays, ``enum`` values, or type constraints.
    The schema after transformation is strictly *less* verbose but equally
    constrained.
    """
    import copy as _copy  # noqa: PLC0415

    schema = _copy.deepcopy(model_cls.model_json_schema())

    # Step 1: Resolve $defs / $ref — Gemini does not support JSON Schema $ref.
    defs = schema.pop("$defs", {})
    schema = _resolve_refs(schema, defs)

    # Step 2: Strip additionalProperties recursively — SDK rejects this key.
    _strip_key(schema, "additionalProperties")

    # Step 3: Strip title keys — keeps the wire payload lean.
    _strip_key(schema, "title")

    return schema


# ---------------------------------------------------------------------------
# GeminiProvider adapter
# ---------------------------------------------------------------------------


class GeminiProvider:
    """Adapter that delegates to ``google-genai`` ``Client.models.generate_content``.

    Uses Gemini's native structured output via ``response_json_schema`` in
    ``GenerateContentConfig``.  The Pydantic→Gemini schema translation
    (``_gemini_schema``) strips ``additionalProperties`` and inlines ``$ref``
    pointers before the schema is sent to the API.

    Requires Python >=3.10 (``google-genai`` SDK requirement).

    Parameters
    ----------
    model : str
        Gemini model identifier.  Default ``"gemini-2.0-flash"``.
    api_key : str or None
        Explicit API key.  When ``None``, the SDK reads ``GEMINI_API_KEY``
        from the environment.

    Raises
    ------
    ImportError
        On Python <3.10 — ``google-genai`` requires Python >=3.10.  The error
        message suggests using ``fdars[openai]`` or ``fdars[ollama]`` on Python
        3.9.
    ImportError
        When ``google-genai`` is not installed.  The error message names
        ``pip install fdars[gemini]``.
    """

    name = "gemini"
    supports_native_structured_output = True

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: "str | None" = None,
    ) -> None:
        # Python version check — deferred sys import so the module is importable
        # on any Python without triggering the check at import time.
        import sys  # noqa: PLC0415

        if sys.version_info < (3, 10):
            raise ImportError(
                "The fdars[gemini] extra requires Python >=3.10 "
                "(google-genai SDK requirement). "
                "Use fdars[openai] or fdars[ollama] on Python 3.9."
            )

        # Deferred import guards — only triggered from resolve_provider(), never
        # at module load.  Keeps bare-venv import of fdars working without SDK.
        from fdars.advisor import _require_gemini, _require_pydantic  # noqa: PLC0415

        genai = _require_gemini()
        _require_pydantic()

        self.model = model
        self._api_key = api_key
        # Cache the client on self._client — constructed once in __init__.
        self._client = genai.Client(api_key=self._api_key)

    def complete_structured(
        self,
        schema: type,
        messages: list,
        system: str,
    ) -> object:
        """Call ``client.models.generate_content`` with translated schema + system prompt.

        Parameters
        ----------
        schema : type
            Pydantic model class used as ``response_json_schema``
            (after translation by ``_gemini_schema``).
        messages : list[dict]
            Conversation messages.  User-role content is joined into a single
            string (Gemini uses ``contents=`` not ``messages=``).
        system : str
            System prompt (contains the grounding invariant), passed as
            ``system_instruction`` in ``GenerateContentConfig``.

        Returns
        -------
        object
            Validated Pydantic instance (e.g. ``Advice``).

        Raises
        ------
        ValueError
            When ``response.text`` is falsy (empty / None response from the
            model — GROUND-04 parity).  The error message names
            ``GEMINI_API_KEY`` and model checks to guide debugging.
        """
        from google.genai import types as _types  # noqa: PLC0415

        # Build Gemini-safe schema (strips additionalProperties, resolves $ref).
        gemini_schema = _gemini_schema(schema)

        # Gemini uses contents= (not messages=) — join user-role message content
        # into a single string.
        user_content = " ".join(
            str(m.get("content", ""))
            for m in messages
            if m.get("role") == "user"
        )

        response = self._client.models.generate_content(
            model=self.model,
            contents=user_content,
            config=_types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_json_schema=gemini_schema,
            ),
        )

        raw_json = response.text
        if not raw_json:
            raise ValueError(
                "GeminiProvider: model returned an empty response. "
                "Check that GEMINI_API_KEY is set correctly and that the "
                f"model {self.model!r} is available in your Gemini project."
            )

        # Parse and validate — returns a native Pydantic instance.
        # ValidateAndRetry sees supports_native_structured_output=True and
        # returns this instance directly without a repair retry.
        return schema.model_validate_json(raw_json)
