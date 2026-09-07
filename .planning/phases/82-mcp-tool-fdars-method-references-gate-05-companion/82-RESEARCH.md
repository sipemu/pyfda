# Phase 82: MCP Tool `fdars_method_references` + GATE-05 Companion — Research

**Researched:** 2026-09-07
**Domain:** Python MCP server extension + guard-sync test authoring
**Confidence:** HIGH (codebase-internal; all claims verified by reading source files this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- The tool is PROVABLY LLM-free: static `importlib.resources` load, `_REFERENCES_MODULES`
  DERIVED from `_CAPABILITY_MODULES`, no `provider`/`model` keys in response, explicit
  `{"curated": false, "sentinel": "NO_CURATED_ENTRY"}` for the tail. The hybrid
  curated/ungrounded fallback lives ONLY in the skill (Phase 83), never here.
- Guard tests land in the SAME commit as the tool handler (GATE-04 lesson).
- Guard Group 3 companion tests are Py3.10+ (they import `mcp`), matching the existing split.
- `_Fdata` callables are special-cased consistently with `fdars_list_capabilities` and the
  Phase-80 cross-file resolution.
- Coverage string MUST use the DERIVED real denominator (N/437, from `_capability_map.json`),
  NOT the stale "409" in the MCP-02 requirement text.

### Claude's Discretion

- Exact `papers[...]` projection shape returned on a hit (which fields to surface).
- Exact `message` wording on a miss.
- Suffix-resolution algorithm for a bare `"callable"`.
- Whether `coverage` is computed at call time from both JSON files or read from a
  pre-computed field — provided it is honest and matches the guard-emitted fraction.

### Deferred Ideas (OUT OF SCOPE)

- The skill's hybrid curated/ungrounded fallback (Phase 83).
- References docs page + llms.txt provenance section (Phase 83).
- Whole-site strict build + guard-sync close + human citation review (Phase 84).
- HTTP/SSE MCP transport (future; stdio only).
</user_constraints>

---

## Summary

Phase 82 is a pure codebase-internal implementation phase. No external packages are needed.
The implementation mirrors `fdars_list_capabilities` (lines 761–826 of `server.py`) very
closely: same `@mcp.tool()` pattern, same lazy-import discipline, same `importlib.resources`
load idiom. The only new complexity is the two-format input (`"module.callable"` vs bare
`"callable"`), the curated-paper projection, and the three-way sentinel/hit/curated-false
classification.

The two JSON data files have been read and their schemas are fully understood. The
`callable_index` has 243 entries across 21 modules. Six curated-true papers cover 28
callables. The denominator is 437 (verified from `_capability_map.json`). There are currently
zero genuinely ambiguous bare-callable lookups (no suffix appears under two different module
prefixes in the current index), but the suffix-resolution algorithm must handle the ambiguous
case correctly for future-proofing.

The guard tests mirror the Guard Group 2 pattern (primary Py3.9+ no-mcp, companion Py3.10+
imports-mcp). The (C) test uses AST inspection of the handler source to assert no
`fdars.advisor` or provider imports live inside the function body — this is stronger than
checking result keys alone. The (D) test mirrors `test_capability_mcp_server_frozenset_matches`.

**Primary recommendation:** implement `fdars_method_references` immediately after
`fdars_list_capabilities` in `server.py`, add companion (C)/(D) tests in
`test_guard_sync_version_independent.py`, commit both in the same atomic commit.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| References lookup (method→papers) | MCP server layer (`server.py`) | — | Static JSON lookup; no computation; consistent with `fdars_list_capabilities` pattern |
| Input validation (frozenset gate) | MCP server layer, BEFORE JSON load | — | Established T-78-08 discipline: validate before any I/O |
| Data store (`_references_map.json`) | Python package data (importlib.resources) | — | Committed artifact; loaded at call time, not imported |
| Guard tests | `tests/test_guard_sync_version_independent.py` | — | Guard Group 3 home; established in Phase 80 |
| Version string | `fdars.__version__` (package-level constant) | — | Single source of truth, matches `fdars_list_capabilities` pattern |

---

## Standard Stack

No new packages. All implementation uses existing dependencies:

| Component | Source | Notes |
|-----------|--------|-------|
| `mcp.server.MCPServer` | `mcp` optional extra (Py 3.10+) | Already in server.py |
| `importlib.resources` | stdlib | Used in `fdars_list_capabilities`; same pattern here |
| `json` | stdlib | Lazy-imported inside handler body |
| `fdars.__version__` | package constant | Line 35 of `python/fdars/__init__.py`: `__version__ = "0.11.0"` |
| `_references_map.json` | `python/fdars/_references_map.json` | 57 papers, 243 callable_index entries |
| `_capability_map.json` | `python/fdars/_capability_map.json` | 437 total callables; used for denominator |

[VERIFIED: python/fdars/__init__.py:35] `__version__ = "0.11.0"`

---

## Data Shape Reference

All claims below are verified by reading the actual files this session.

### `_references_map.json` top-level structure

[VERIFIED: python/fdars/_references_map.json:1-1435]

```json
{
  "papers": {
    "<paper_key>": {
      "title": "str",
      "authors": ["str", ...],
      "year": int_or_null,
      "doi": "str (may be empty for PMLR/arXiv entries)",
      "url": "str (may be empty for curated:false)",
      "type": "journal|book|book_chapter|conference|preprint",
      "callables": ["module.callable", ...],
      "cross_language": {
        "R": {"package": "str", "function": "str", "url": "str", "confidence": "high|low"},
        "Python": {"package": "str", "function": "str", "url": "str", "confidence": "high|low"},
        "Matlab": {"package": "str", "function": "str", "url": "str", "confidence": "high|low"}
      },
      "notes": "str",
      "curated": true_or_false
    }
  },
  "callable_index": {
    "module.callable": ["paper_key", ...],
    "_Fdata.method": ["paper_key", ...]
  }
}
```

Key facts [VERIFIED: python/fdars/_references_map.json]:
- Total papers: 57
- Total callable_index keys: 243
- Curated-true papers (6): `cuturi_blondel_2017`, `eilers_marx_1996`, `fraiman_muniz_2001`,
  `lopez_pintado_romo_2009`, `ramsay_dalzell_1991`, `srivastava_et_al_2011`
- Callables backed by at least one curated-true paper: 28
- Current coverage: **28/437** (verified by running the same formula as the coverage test)
- Zero genuinely ambiguous bare callables (no suffix appears under two different module prefixes)

### `_capability_map.json` denominator

[VERIFIED: python/fdars/_capability_map.json:1] and confirmed by running:
`sum(len(v) for v in cap_data.values()) == 437`

The denominator includes `_Fdata` class methods in the count (consistent with the coverage
test at `tests/test_guard_sync_version_independent.py:558`).

### `_CAPABILITY_MODULES` frozenset (the derivation source)

[VERIFIED: python/fdars/mcp/server.py:751-758]

```python
_CAPABILITY_MODULES: frozenset[str] = frozenset({
    "alignment", "basis", "classification", "clustering", "conformal",
    "covariance", "datasets", "density_fda", "depth", "explain", "famm",
    "fdata", "frechet", "fts", "inference", "metric", "metrics", "multi_fdata",
    "outliers", "pace_fpca", "regression", "represent", "scalar_on_function",
    "scoring", "seasonal", "shapelet", "simulation", "smoothing", "spm",
    "tolerance",
})
```

30 members. `_REFERENCES_MODULES` is this same set (derived, not independently declared).

---

## Handler Design

### Placement

Add immediately after `fdars_list_capabilities` (which ends at line 826 of `server.py`),
before the `# stdio entry point` comment block. The module-level docstring list of tools
(lines 18–27) must also be updated to include `fdars_method_references`.

### `_REFERENCES_MODULES` Declaration

```python
# _REFERENCES_MODULES is intentionally an alias for _CAPABILITY_MODULES — single
# source of truth. The (D) guard in test_guard_sync_version_independent.py asserts
# _REFERENCES_MODULES == _CAPABILITY_MODULES == _EXPECTED_REFERENCES_MODULES.
_REFERENCES_MODULES: frozenset[str] = _CAPABILITY_MODULES
```

Place this immediately after `_CAPABILITY_MODULES` (after line 758), before the
`@mcp.tool()` decorator for `fdars_list_capabilities`. The maintenance comment on
`_CAPABILITY_MODULES` (lines 747–750) should be updated to mention that
`_REFERENCES_MODULES` is derived from it.

### Handler Signature and Body Sketch

```python
@mcp.tool()
def fdars_method_references(method: str) -> dict:
    """Return curated paper references for an fdars callable.  LLM-free.

    Loads ``python/fdars/_references_map.json`` (committed at curation time)
    via ``importlib.resources`` and returns the paper(s) backing the requested
    callable, or an explicit sentinel when no curated entry exists.
    **No network call; no model invoked; no ANTHROPIC_API_KEY required.**

    Parameters
    ----------
    method : str
        The callable to look up.  Two formats accepted:

        - ``"module.callable"`` (preferred): e.g. ``"depth.fraiman_muniz_1d"``,
          ``"_Fdata.depth"``.  The module prefix is validated against
          ``_REFERENCES_MODULES`` before any JSON load.
        - bare ``"callable"`` (no dot): e.g. ``"fraiman_muniz_1d"``.  Resolved
          by suffix-matching all ``callable_index`` keys ending in
          ``".<callable>"``.  If exactly one match, auto-resolved.  If multiple
          matches, all are returned (ambiguous result).  If zero matches,
          sentinel is returned.

    Returns
    -------
    dict
        **Hit** (callable found in ``callable_index``)::

            {
                "method": "module.callable",
                "curated": True,          # or False if all backing papers are curated:false
                "papers": [...],          # projected paper entries (see below)
                "coverage": "28/437",     # N/T derived from live JSON files
                "version": "0.11.0",
            }

        **Miss** (callable absent from ``callable_index``)::

            {
                "method": "module.callable",
                "curated": False,
                "sentinel": "NO_CURATED_ENTRY",
                "message": "No curated reference entry for 'module.callable'. ...",
                "version": "0.11.0",
            }

        **Ambiguous bare callable** (multiple module matches)::

            {
                "method": "<bare>",
                "curated": False,
                "sentinel": "AMBIGUOUS_CALLABLE",
                "matches": ["module1.callable", "module2.callable"],
                "message": "Bare callable '<bare>' matches multiple entries. ...",
                "version": "0.11.0",
            }

    Raises
    ------
    ValueError
        If ``method`` is ``"module.callable"`` format and the module is not in
        ``_REFERENCES_MODULES``.  Message format mirrors ``fdars_list_capabilities``:
        ``"fdars_method_references: unknown module '<x>'. Known: [...]."``
    """
    import json  # noqa: PLC0415
    from importlib import resources  # noqa: PLC0415

    from fdars import __version__ as _fdars_version  # noqa: PLC0415

    # ------------------------------------------------------------------
    # Input classification
    # ------------------------------------------------------------------
    has_dot = "." in method

    if has_dot:
        # "module.callable" or "_Fdata.method" format
        module, _callable = method.split(".", 1)
        # V5 frozenset gate: validate module BEFORE any JSON load
        # Note: _Fdata is NOT in _REFERENCES_MODULES (it is the class entry,
        # not a submodule). Special-case it consistently with fdars_list_capabilities.
        if module != "_Fdata" and module not in _REFERENCES_MODULES:
            raise ValueError(
                f"fdars_method_references: unknown module {module!r}. "
                f"Known: {sorted(_REFERENCES_MODULES)!r}."
            )
        resolved_key = method  # use as-is for callable_index lookup

    else:
        # Bare callable — defer resolution until after JSON load
        resolved_key = None  # signals suffix-resolve path

    # ------------------------------------------------------------------
    # JSON load
    # ------------------------------------------------------------------
    ref_file = resources.files("fdars") / "_references_map.json"
    cap_file = resources.files("fdars") / "_capability_map.json"

    ref_data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
    cap_data: dict = json.loads(cap_file.read_text(encoding="utf-8"))

    papers_map = ref_data.get("papers", {})
    callable_index = ref_data.get("callable_index", {})

    # ------------------------------------------------------------------
    # Suffix resolution (bare callable path)
    # ------------------------------------------------------------------
    if resolved_key is None:
        suffix = "." + method
        matches = [k for k in callable_index if k.endswith(suffix)]
        if len(matches) == 0:
            return {
                "method": method,
                "curated": False,
                "sentinel": "NO_CURATED_ENTRY",
                "message": (
                    f"No curated reference entry for bare callable {method!r}. "
                    "Use 'module.callable' format (e.g. 'depth.fraiman_muniz_1d') "
                    "or check fdars_list_capabilities for available callables."
                ),
                "version": _fdars_version,
            }
        if len(matches) > 1:
            return {
                "method": method,
                "curated": False,
                "sentinel": "AMBIGUOUS_CALLABLE",
                "matches": sorted(matches),
                "message": (
                    f"Bare callable {method!r} matches {len(matches)} entries: "
                    f"{sorted(matches)}. Use 'module.callable' format to disambiguate."
                ),
                "version": _fdars_version,
            }
        # Exactly one match — auto-resolve
        resolved_key = matches[0]

    # ------------------------------------------------------------------
    # Callable index lookup
    # ------------------------------------------------------------------
    if resolved_key not in callable_index:
        return {
            "method": resolved_key,
            "curated": False,
            "sentinel": "NO_CURATED_ENTRY",
            "message": (
                f"No curated reference entry for {resolved_key!r}. "
                "This callable exists in fdars but has not yet been mapped to a "
                "primary paper. Use fdars_list_capabilities to confirm the callable "
                "exists, and check back after Phase 84 human citation review."
            ),
            "version": _fdars_version,
        }

    # ------------------------------------------------------------------
    # Paper projection
    # ------------------------------------------------------------------
    paper_keys: list[str] = callable_index[resolved_key]

    projected_papers = []
    any_curated = False
    for pk in paper_keys:
        paper = papers_map.get(pk, {})
        if paper.get("curated", False):
            any_curated = True
        projected_papers.append({
            "paper_key": pk,
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "doi": paper.get("doi", ""),
            "url": paper.get("url", ""),
            "type": paper.get("type", ""),
            "cross_language": paper.get("cross_language", {}),
            "curated": paper.get("curated", False),
        })

    # ------------------------------------------------------------------
    # Coverage (derived at call time from live JSON)
    # ------------------------------------------------------------------
    denominator = sum(len(v) for v in cap_data.values())
    curated_paper_keys = frozenset(
        pk for pk, p in papers_map.items() if p.get("curated", False) is True
    )
    numerator = sum(
        1 for _, pks in callable_index.items()
        if any(pk in curated_paper_keys for pk in pks)
    )
    coverage_str = f"{numerator}/{denominator}"

    return {
        "method": resolved_key,
        "curated": any_curated,
        "papers": projected_papers,
        "coverage": coverage_str,
        "version": _fdars_version,
    }
```

### Key Design Decisions Embedded in the Sketch

**1. `_REFERENCES_MODULES` as an alias, not a copy**

```python
_REFERENCES_MODULES: frozenset[str] = _CAPABILITY_MODULES
```

This is the "DERIVED" relationship. The (D) guard asserts `_REFERENCES_MODULES == _CAPABILITY_MODULES == _EXPECTED_REFERENCES_MODULES`. An alias (`=`) satisfies this by identity; a `frozenset(...)` copy also works but the alias is cleaner. Either works for the three-way assert.

**2. `_Fdata` special-casing**

`_Fdata` is not in `_REFERENCES_MODULES` (which equals `_CAPABILITY_MODULES`, and `_Fdata` is excluded from `_CAPABILITY_MODULES` per the maintenance comment at server.py:796–798). The handler must accept `_Fdata.depth` and similar — check `module != "_Fdata"` before the frozenset gate, exactly as `fdars_list_capabilities` handles it (the full map returned by `fdars_list_capabilities(None)` includes `_Fdata`, but filtered requests are restricted to `_CAPABILITY_MODULES` submodule names).

[VERIFIED: python/fdars/mcp/server.py:796-798] The docstring says: "The `_Fdata` entry present in `_capability_map.json` ... is intentionally NOT included in `_CAPABILITY_MODULES`."

**3. The curated:false-papers-vs-sentinel edge case**

When a callable IS in `callable_index` but ALL its backing papers are `curated:false`, the tool returns a **hit** with `"curated": false` (not the sentinel). Rationale:

- The sentinel `NO_CURATED_ENTRY` means "no callable_index entry at all" — the callable is completely untracked. That is the anti-feature-family case.
- A callable present in `callable_index` (even if all papers are `curated:false`) is a different state: it IS tracked, the attribution is contested or pending verification. Returning the papers (with their `curated:false` flags) is more honest than returning a sentinel that implies no information exists.
- The (C) guard test: "a known-ABSENT callable returns `curated:false` with no `doi`". This tests the sentinel path (absent from `callable_index`). The guard does NOT test the "present but curated:false papers" path. The two states are distinguished by `sentinel` key presence:
  - `callable_index` miss → `curated:false` + `sentinel: "NO_CURATED_ENTRY"` + `message`
  - `callable_index` hit, all papers curated:false → `curated:false` + `papers: [...]` (no sentinel)
- This aligns with the LLM-free honesty rule: return what you know, flag what is unverified.

**4. Coverage computed at call time**

The `coverage` field is computed fresh on each call from both JSON files (same formula as `test_references_map_coverage_fraction`). This avoids a stale cache and costs two small JSON reads (already happening for the references lookup). The denominator is 437 at authoring time but will drift correctly when the capability map grows — the live derivation keeps it honest.

**5. `version` field source**

`from fdars import __version__ as _fdars_version` — identical to `fdars_list_capabilities`. [VERIFIED: python/fdars/mcp/server.py:811] This is a lazy import inside the handler body (consistent with the `# noqa: PLC0415` pattern throughout the file).

**6. Paper projection fields**

Project: `paper_key`, `title`, `authors`, `year`, `doi`, `url`, `type`, `cross_language`, `curated`. Omit: `callables` (redundant — the caller already knows which callable they asked for) and `notes` (internal curation notes not for MCP consumers). This matches the spirit of `fdars_list_capabilities` returning only the fields needed by the consumer.

---

## Return Shape Reference

### Hit (callable found, at least one curated-true paper)

Example: `method="depth.fraiman_muniz_1d"`

```python
{
    "method": "depth.fraiman_muniz_1d",
    "curated": True,
    "papers": [
        {
            "paper_key": "fraiman_muniz_2001",
            "title": "Trimmed means for functional data",
            "authors": ["Fraiman, R.", "Muniz, G."],
            "year": 2001,
            "doi": "10.1007/BF02595706",
            "url": "https://link.springer.com/article/10.1007/BF02595706",
            "type": "journal",
            "cross_language": {
                "R": {"package": "fda.usc", "function": "depth.FM",
                      "url": "...", "confidence": "high"},
                "Python": {"package": "scikit-fda", "function": "fraiman_muniz_depth",
                           "url": "...", "confidence": "high"}
            },
            "curated": True,
        }
    ],
    "coverage": "28/437",
    "version": "0.11.0",
}
```

### Hit (callable found, all papers curated:false)

Example: `method="clustering.align_cluster_fd"`

```python
{
    "method": "clustering.align_cluster_fd",
    "curated": False,          # no sentinel key
    "papers": [
        {
            "paper_key": "_uncurated_align_cluster_fd_2026-09",
            "title": "",
            "authors": [],
            "year": None,
            "doi": "",
            "url": "",
            "type": "preprint",
            "cross_language": {},
            "curated": False,
        }
    ],
    "coverage": "28/437",
    "version": "0.11.0",
}
```

### Miss (callable absent from callable_index)

Example: `method="explain.shap_values"` or any anti-feature callable

```python
{
    "method": "explain.shap_values",
    "curated": False,
    "sentinel": "NO_CURATED_ENTRY",
    "message": "No curated reference entry for 'explain.shap_values'. ...",
    "version": "0.11.0",
}
```

### Ambiguous bare callable (future-proof; currently no cases exist)

```python
{
    "method": "some_bare_name",
    "curated": False,
    "sentinel": "AMBIGUOUS_CALLABLE",
    "matches": ["module_a.some_bare_name", "module_b.some_bare_name"],
    "message": "Bare callable 'some_bare_name' matches 2 entries: [...]. ...",
    "version": "0.11.0",
}
```

---

## Guard Group 3 Companion Tests (C) and (D)

Add to `tests/test_guard_sync_version_independent.py` in a new section after the existing
Guard Group 3 tests (after line 673).

### Module-level addition

Add `_EXPECTED_REFERENCES_MODULES` immediately after `_EXPECTED_CAPABILITY_MODULES`
(after line 196):

```python
# ---------------------------------------------------------------------------
# Expected references modules — hard-coded mirror of _REFERENCES_MODULES in
# fdars.mcp.server (which is DERIVED from _CAPABILITY_MODULES — an alias).
#
# MAINTENANCE NOTE: _REFERENCES_MODULES == _CAPABILITY_MODULES by design.
# Update _EXPECTED_REFERENCES_MODULES here in the same atomic commit that
# updates _EXPECTED_CAPABILITY_MODULES and regenerates _capability_map.json.
# ---------------------------------------------------------------------------

_EXPECTED_REFERENCES_MODULES: frozenset[str] = frozenset({
    "alignment", "basis", "classification", "clustering", "conformal",
    "covariance", "datasets", "density_fda", "depth", "explain", "famm",
    "fdata", "frechet", "fts", "inference", "metric", "metrics", "multi_fdata",
    "outliers", "pace_fpca", "regression", "represent", "scalar_on_function",
    "scoring", "seasonal", "shapelet", "simulation", "smoothing", "spm",
    "tolerance",
})
```

[VERIFIED: python/fdars/mcp/server.py:751-758] This frozenset is byte-identical to
`_CAPABILITY_MODULES` — that identity is the invariant.

### Section header in the test file

```python
# ===========================================================================
# Guard Group 3 — fdars_method_references companion tests (GATE-05 C/D)
# ===========================================================================
```

Place this after the existing anti-feature-absence guard (after line 673).

### Test (C): LLM-free boundary

```python
def test_references_tool_llm_free_boundary():
    """GATE-05 C: fdars_method_references is LLM-free (Python 3.10+).

    Internally guarded to Python 3.10+ (mcp requires 3.10+).  Asserts:

    1. A known curated callable returns a hit with ``'curated'`` key, no
       ``'provider'`` or ``'model'`` key (LLM-free boundary).
    2. A callable absent from ``callable_index`` returns ``curated:False``
       with ``sentinel: 'NO_CURATED_ENTRY'`` and no ``'doi'`` key.
    3. The handler function body contains no import of ``fdars.advisor`` or
       any provider/model module (AST-level no-import assertion).

    Reference: GATE-05 C — companion test (Python 3.10+).
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    pytest.importorskip("mcp")

    import ast  # noqa: PLC0415
    import inspect  # noqa: PLC0415

    from fdars.mcp.server import fdars_method_references  # noqa: PLC0415

    # --- Assertion 1: known curated callable hit is LLM-free ---
    result_hit = fdars_method_references("depth.fraiman_muniz_1d")

    assert "curated" in result_hit, (
        "fdars_method_references hit must return 'curated' key"
    )
    assert result_hit["curated"] is True, (
        "depth.fraiman_muniz_1d is backed by fraiman_muniz_2001 (curated:true)"
    )
    assert "provider" not in result_hit, (
        "fdars_method_references must NOT expose 'provider' key (LLM-free boundary)"
    )
    assert "model" not in result_hit, (
        "fdars_method_references must NOT expose 'model' key (LLM-free boundary)"
    )
    assert "papers" in result_hit and isinstance(result_hit["papers"], list)
    assert "coverage" in result_hit
    assert "version" in result_hit

    # --- Assertion 2: known-absent callable returns sentinel with no doi ---
    # explain.shap_values: module 'explain' IS in _REFERENCES_MODULES (passes gate)
    # but 'explain.shap_values' is absent from callable_index -> sentinel
    result_miss = fdars_method_references("explain.shap_values")

    assert result_miss.get("curated") is False, (
        "A callable absent from callable_index must return curated:False"
    )
    assert result_miss.get("sentinel") == "NO_CURATED_ENTRY", (
        "A callable absent from callable_index must return sentinel='NO_CURATED_ENTRY'"
    )
    assert "doi" not in result_miss, (
        "The sentinel response must NOT expose a 'doi' key (no paper data to project)"
    )

    # --- Assertion 3: AST-level no-import boundary ---
    src = inspect.getsource(fdars_method_references)
    tree = ast.parse(src)
    forbidden_modules = {"fdars.advisor", "fdars.mcp._runner", "fdars.mcp._compare",
                         "fdars.mcp._tuning", "anthropic", "openai"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module not in forbidden_modules, (
                f"fdars_method_references imports from {node.module!r} — "
                "LLM-free boundary violated: this handler must not import "
                "advisor or provider modules."
            )
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_modules, (
                    f"fdars_method_references imports {alias.name!r} — "
                    "LLM-free boundary violated."
                )
```

### Test (D): frozenset literal mirror

```python
def test_references_mcp_server_frozenset_matches():
    """GATE-05 D: server._REFERENCES_MODULES == expected frozenset (Python 3.10+).

    Internally guarded to Python 3.10+.  Asserts the three-way literal mirror:

        server._REFERENCES_MODULES
            == _EXPECTED_REFERENCES_MODULES
            == server._CAPABILITY_MODULES

    ``_REFERENCES_MODULES`` is DERIVED from ``_CAPABILITY_MODULES`` (alias) so
    the three-way equality holds by construction.  This guard catches any future
    edit that accidentally makes them diverge.

    Reference: GATE-05 D — companion test (Python 3.10+).
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    pytest.importorskip("mcp")

    from fdars.mcp.server import _CAPABILITY_MODULES, _REFERENCES_MODULES  # noqa: PLC0415

    assert _REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES, (
        f"server._REFERENCES_MODULES != _EXPECTED_REFERENCES_MODULES.\n"
        f"  In server only:   {_REFERENCES_MODULES - _EXPECTED_REFERENCES_MODULES}\n"
        f"  In expected only: {_EXPECTED_REFERENCES_MODULES - _REFERENCES_MODULES}\n"
        "Update _REFERENCES_MODULES in server.py and _EXPECTED_REFERENCES_MODULES here "
        "in one atomic commit."
    )
    assert _REFERENCES_MODULES == _CAPABILITY_MODULES, (
        f"server._REFERENCES_MODULES != server._CAPABILITY_MODULES — "
        "they must remain equal (DERIVED relationship).\n"
        f"  In _REFERENCES only:  {_REFERENCES_MODULES - _CAPABILITY_MODULES}\n"
        f"  In _CAPABILITY only:  {_CAPABILITY_MODULES - _REFERENCES_MODULES}"
    )
```

---

## Common Pitfalls

### Pitfall 1: Hardcoding the 409 denominator from MCP-02 requirement text

**What goes wrong:** Using `coverage = f"{numerator}/409"` because 409 appears in the roadmap requirement text.
**Why it happens:** The MCP-02 requirement predates Phase 81's honest callable count audit. 409 was a pre-audit estimate.
**How to avoid:** Derive the denominator at call time: `sum(len(v) for v in cap_data.values())` from the live `_capability_map.json`. This is 437 and will update correctly if the capability map grows.
**Warning signs:** The `test_references_map_coverage_fraction` guard asserts `denominator == 437` as a tripwire — if the tool hardcodes 409, the strings will disagree and any integration test comparing them will catch it.

### Pitfall 2: Forgetting the `_Fdata` special-case in the module gate

**What goes wrong:** `"_Fdata" not in _REFERENCES_MODULES` triggers a `ValueError` for inputs like `"_Fdata.depth"`.
**Why it happens:** `_Fdata` is excluded from `_CAPABILITY_MODULES` (and thus `_REFERENCES_MODULES`) intentionally — it is the class surface, not a submodule.
**How to avoid:** Guard with `if module != "_Fdata" and module not in _REFERENCES_MODULES: raise ValueError(...)`. Mirror the established handling in `fdars_list_capabilities`.
[VERIFIED: python/fdars/mcp/server.py:796-798] "_Fdata entry ... is intentionally NOT included in _CAPABILITY_MODULES."

### Pitfall 3: Using `sentinel` for the curated:false-papers-present case

**What goes wrong:** Returning `{"sentinel": "NO_CURATED_ENTRY", ...}` for a callable that IS in `callable_index` but has only `curated:false` papers.
**Why it happens:** Conflating "no curated paper" with "no callable_index entry".
**How to avoid:** Reserve `sentinel: "NO_CURATED_ENTRY"` ONLY for the case where `resolved_key not in callable_index`. When the callable is present in the index with curated:false papers, return `{"curated": false, "papers": [...]}` (no sentinel key). The (C) guard test specifically targets a callable ABSENT from `callable_index` for the sentinel assertion, not a callable with curated:false papers.

### Pitfall 4: Splitting on the first dot only for `_Fdata.to_pc`

**What goes wrong:** `"_Fdata.to_pc".split(".", 1)` gives `["_Fdata", "to_pc"]` which is correct. But a naive `split(".")` without maxsplit would split `_Fdata` on its underscore prefix incorrectly if someone wrote `"_Fdata.to_pc.extra"`. 
**How to avoid:** Always use `method.split(".", 1)` (maxsplit=1). The CONTEXT keys use `"module.callable"` format; no callable contains a dot in its own name.

### Pitfall 5: Companion tests not gated to Python 3.10+

**What goes wrong:** Test (C) and (D) import `fdars.mcp.server`, which imports `mcp` at module top. On Python 3.9, `mcp` is absent, causing the entire test file to fail collection.
**How to avoid:** Gate both tests with `if sys.version_info < (3, 10): pytest.skip(...)` AND `pytest.importorskip("mcp")` — matching the exact pattern at lines 251–254 of the test file. Primary tests A/B (already present) must continue to pass on Python 3.9.
[VERIFIED: python/fdars/tests/test_guard_sync_version_independent.py:251-254] Established pattern.

### Pitfall 6: Missing the module-level docstring update in server.py

**What goes wrong:** The Tools-exposed list at server.py lines 18–27 is not updated to include `fdars_method_references`, leaving the docstring stale.
**How to avoid:** Update the docstring comment line, e.g. add `- ``fdars_method_references`` — LLM-free static reference lookup by callable (MCP-01..04)`.

### Pitfall 7: Coverage computed with `callable_index` entries only, not `cap_data`

**What goes wrong:** Using `len(callable_index) == 243` as the denominator instead of `sum(len(v) for v in cap_data.values()) == 437`.
**Why it happens:** The 243 is the callable_index size (how many callables have any tracking entry), not the total fdars callable surface.
**How to avoid:** Load `_capability_map.json` and sum all callable counts — exactly as the coverage test does. The denominator is "total fdars callables", not "callables with any reference entry".

### Pitfall 8: The `inspect.getsource` approach in test (C) requires the handler to be importable

**What goes wrong:** If `fdars.mcp.server` is not importable in the test environment (e.g., `mcp` not installed), `inspect.getsource` will fail before the skip guard activates.
**How to avoid:** The `pytest.importorskip("mcp")` at the top of the test ensures the import is skipped if mcp is absent. The `from fdars.mcp.server import fdars_method_references` import is inside the test function body, after the skip guard. This is the established pattern for all companion tests.

---

## Architecture Patterns

### Placement in server.py

```
server.py structure (relevant excerpt):
├── _RUNNABLE_METHODS (line 53)
├── _SUPPORTED_METHODS (line 59)
├── _DIAGNOSTICS_METHODS (line 67)
├── @mcp.tool() fdars_build_diagnostics (line 97)
├── @mcp.tool() fdars_run_method (line 168)
├── @mcp.tool() fdars_compare_run
├── @mcp.tool() fdars_compare_methods
├── @mcp.tool() fdars_build_pipeline_report
├── @mcp.tool() fdars_auto_tune
├── _CAPABILITY_MODULES (line 751)      ← add _REFERENCES_MODULES alias here
├── @mcp.tool() fdars_list_capabilities (line 762)
├── @mcp.tool() fdars_method_references  ← NEW (immediately after)
└── run_stdio() (line 834)
```

### Lazy-import discipline

All imports inside handler bodies use `# noqa: PLC0415` comments. The pattern:
```python
import json  # noqa: PLC0415
from importlib import resources  # noqa: PLC0415
from fdars import __version__ as _fdars_version  # noqa: PLC0415
```
[VERIFIED: python/fdars/mcp/server.py:808-811]

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `pytest tests/test_guard_sync_version_independent.py -x -q` |
| Full suite command | `pytest tests/ -x -q` |

### Phase Requirements → Test Map

| ID | Behavior | Test Type | Automated Command | File Exists? |
|----|----------|-----------|-------------------|-------------|
| MCP-01 | `fdars_method_references` returns hit with `curated:True` for known callable | unit (companion C) | `pytest tests/test_guard_sync_version_independent.py::test_references_tool_llm_free_boundary -x` | New — Wave 0 |
| MCP-02 | Sentinel returned for callable absent from index | unit (companion C) | Same test | New — Wave 0 |
| MCP-03 | No `provider`/`model` keys in any response | unit (companion C) | Same test | New — Wave 0 |
| MCP-04 | `_REFERENCES_MODULES == _CAPABILITY_MODULES == _EXPECTED_REFERENCES_MODULES` | unit (companion D) | `pytest tests/test_guard_sync_version_independent.py::test_references_mcp_server_frozenset_matches -x` | New — Wave 0 |
| GATE-05 | Existing primary A/B tests continue to pass on Python 3.9+ | guard | `pytest tests/test_guard_sync_version_independent.py -x -q` | Existing |

### Wave 0 Gaps

- [ ] Two new test functions (C and D) in `tests/test_guard_sync_version_independent.py`
- [ ] `_EXPECTED_REFERENCES_MODULES` frozenset literal in `tests/test_guard_sync_version_independent.py`
- [ ] `fdars_method_references` handler in `python/fdars/mcp/server.py`
- [ ] `_REFERENCES_MODULES` alias in `python/fdars/mcp/server.py`
- [ ] Module docstring update in `python/fdars/mcp/server.py`

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Paper data storage | Custom database or cache | `_references_map.json` via `importlib.resources` | Already committed; zero-dependency; consistent with `fdars_list_capabilities` |
| Version string | Hard-coded version in tool | `from fdars import __version__` | [VERIFIED: server.py:811] single source of truth, no drift |
| Denominator computation | Hardcoded 437 (or stale 409) | `sum(len(v) for v in cap_data.values())` | Stays correct across crate bumps |
| No-import boundary test | Ad-hoc string search on source | `ast.parse` + `ast.walk` on `inspect.getsource` | Structured, not fooled by comments; established in Python ecosystem |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | — | — | — |

**All claims in this research were verified by reading source files this session. No `[ASSUMED]` tags were required.**

---

## Sources

### Primary (HIGH confidence — read directly this session)

- `python/fdars/mcp/server.py:740-857` — `fdars_list_capabilities` implementation, `_CAPABILITY_MODULES` frozenset, lazy-import pattern, `__version__` load
- `python/fdars/_references_map.json:1-1435` — complete JSON schema: 57 papers, 243 callable_index entries, curated/uncurated structure
- `python/fdars/_capability_map.json:1-30` — capability map structure, denominator computation
- `tests/test_guard_sync_version_independent.py:1-673` — Guard Group 1/2/3 primary tests, companion-test pattern, `_EXPECTED_CAPABILITY_MODULES`, Py3.10+ skip pattern
- `python/fdars/__init__.py:35` — `__version__ = "0.11.0"`

### Verification runs (this session)

- `sum(len(v) for v in cap_data.values()) == 437` — confirmed denominator
- `numerator == 28` — confirmed curated coverage count
- `sorted(curated_paper_keys)` — confirmed 6 curated-true papers
- Suffix-resolution check confirmed zero ambiguous bare callables in current index
- `ast.walk` on `fdars_list_capabilities` confirmed the lazy-import pattern

---

## RESEARCH COMPLETE
