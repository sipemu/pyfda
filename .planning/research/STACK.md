# Stack Research

**Domain:** Scientific-provenance + cross-language-implementations reference data for a Python/Rust FDA library  
**Researched:** 2026-09-07  
**Confidence:** HIGH (packaging/importlib patterns verified against shipped v12.0 code; format decision derived from existing JSON shapes; stdlib tooling verified against Python docs)

---

## 1. Reference Data Format

### Recommendation: Bespoke minimal JSON, NOT CSL-JSON or BibTeX

**Use two committed JSON files mirroring the `_capability_map.json` + `_capability_curation.json` split:**

```
python/fdars/_references_map.json     # paper registry + callable index + cross-language pointers
python/fdars/_references_curation.json  # (optional) hand override layer, same pattern as _capability_curation.json
```

**Rationale — why NOT CSL-JSON:**

CSL-JSON is a rich bibliographic interchange format originally designed for the citeproc-js citation processor. It carries significant complexity: `author` is an array of objects with `family`/`given` keys, `issued` is a nested `{"date-parts": [[year, month, day]]}` object, type discriminators (`"article-journal"`, `"book"`, etc.) are required for processor dispatch, and field names like `container-title` are citeproc-specific. For a hand-authored provenance store read by Python code and LLMs, this is unnecessary weight. The format is designed for rendering bibliography outputs, not for machine-readable method lookups.

**Rationale — why NOT BibTeX:**

BibTeX is a string format, not JSON. Parsing it requires a third-party library (bibtexparser, pybtex) — adding a runtime dependency. It is also not natively readable by LLMs or directly ingestable by the MCP tool without a parse step. The v12.0 pattern is committed JSON read with `json.loads()` and zero dependencies.

**Rationale — why bespoke minimal JSON:**

The `_capability_map.json` shape (`module -> callable -> {purpose, sig}`) is already the project's data-at-rest convention. The references map extends that same pattern. It stays flat, human-editable, stdlib-readable, and consistent with everything the existing MCP tool and guard-sync tests already know how to handle.

### Recommended schema

Two top-level sections in one file, kept small enough to load in full at every tool call:

```json
{
  "papers": {
    "<paper-key>": {
      "title": "Depth measures for multivariate functional data",
      "authors": ["Ieva, F.", "Paganoni, A.M."],
      "year": 2013,
      "doi": "10.1080/02331888.2012.719672",
      "url": "https://doi.org/10.1080/02331888.2012.719672",
      "venue": "Statistics",
      "notes": ""
    }
  },
  "callables": {
    "depth.fraiman_muniz_1d": {
      "paper_keys": ["fraiman_muniz_2001"],
      "cross_language": [
        {
          "language": "R",
          "package": "fda.usc",
          "function": "fdata.comp",
          "url": "https://cran.r-project.org/package=fda.usc"
        },
        {
          "language": "Python",
          "package": "scikit-fda",
          "function": "MeanDepth",
          "url": "https://fda.readthedocs.io/en/stable/modules/representation/index.html"
        }
      ]
    }
  }
}
```

**Key design decisions in this schema:**

- `papers` is a flat dict keyed by a short human-authored slug (e.g. `"fraiman_muniz_2001"`, `"ramsay_silverman_2005"`) — not by DOI — so callable entries reference readable keys, not opaque DOI strings.
- `authors` is a flat list of `"Family, Given"` strings — not CSL-JSON's nested objects. Sufficient for display and LLM consumption; avoids nested parse complexity.
- `doi` and `url` are both present. `doi` is the bare identifier (`10.XXXX/...`); `url` is the resolvable link. Both are optional for older works without DOIs (e.g. Ramsay & Silverman 2005 book).
- `year` is an integer, not a CSL-JSON nested date-parts object.
- `callables` maps `"module.callable"` keys (matching the `_capability_map.json` + `_capability_curation.json` structure) to `{paper_keys, cross_language}`. Callable keys not present in the callable index have no curated entry — the MCP tool returns an explicit `{"curated": false}` signal for the tail (as specified in PROJECT.md).
- `cross_language` is a list to allow multiple implementations per language; `language` is one of `"R"`, `"Python"`, `"Matlab"`.
- `notes` on `papers` is an optional free-text field for disambiguation or caveats.
- `venue` on `papers` is optional (journal name, conference, or "book") — useful for display on the docs References page.

**Consistency with `_capability_map.json`:**

The `callables` keys use the same `"module.callable"` dot-notation as `_capability_curation.json`. The MCP tool can join the two files at call time: look up the callable in `_references_map.json` -> resolve `paper_keys` to entries in `papers` -> attach `cross_language`. No cross-file index needed; both files live under `importlib.resources.files("fdars")`.

---

## 2. DOI / URL Validity Checking

### Strict separation: offline structural gate (CI) vs online resolve (opt-in only)

**OFFLINE structural check — suitable for CI and the default test path:**

Use Python stdlib `re` and `urllib.parse`. No network, no new dependencies.

```python
import re
from urllib.parse import urlparse

_DOI_RE = re.compile(r'^10\.\d{4,9}/\S+$')

def _is_valid_doi(doi: str) -> bool:
    """Structural DOI check: matches 10.NNNN/suffix pattern (CrossRef/MEDRA syntax)."""
    return bool(_DOI_RE.match(doi.strip()))

def _is_valid_url(url: str) -> bool:
    """Structural URL check: scheme is http/https, netloc is non-empty."""
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False
```

The DOI regex `^10\.\d{4,9}/\S+$` is the CrossRef/MEDRA structural definition: registrant prefix starts with `10.`, followed by 4-9 digits, a `/`, and a non-whitespace suffix of any length. This catches malformed DOIs (wrong prefix, missing slash, whitespace) without requiring a network call.

`urllib.parse.urlparse` is a Python stdlib parser (no install needed) that decomposes a URL into `scheme`, `netloc`, `path`, etc. Checking `scheme in ("http", "https")` and `bool(netloc)` is a reliable structural well-formedness gate — it will not reject valid URLs and will catch obviously broken ones (no scheme, no host). Note: `urlparse` does not validate that a URL is reachable; it is a syntax-only check, which is exactly what is needed for CI.

**This check runs in pytest CI on every push** as part of the schema validation test group (see Section 4).

**OPTIONAL online resolve — must NOT run in default test/build path:**

To actually resolve a DOI to its landing page, use `urllib.request.urlopen` with a HEAD request to `https://doi.org/{doi}`. This MUST be gated behind an environment variable (e.g. `FDARS_ONLINE_CHECKS=1`) and excluded from the default `pytest` run and the docs build.

```python
import os
import urllib.request

def _resolve_doi_online(doi: str) -> bool:
    """Optional online DOI resolution — do NOT call from CI default path."""
    if not os.environ.get("FDARS_ONLINE_CHECKS"):
        return True  # skip silently when env var absent
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status < 400
    except Exception:
        return False
```

**Decision: never make the online check part of `pytest` or `mkdocs build`.** The v12.0 pattern and the project constraints are explicit that CI is network-free. A separate `make check-links` target or a GitHub Actions job with `FDARS_ONLINE_CHECKS=1` can run the optional online resolve on demand before committing a curated data update.

---

## 3. Packaging

### How the JSON ships and is read

**The reference map ships as package data inside `python/fdars/`, the same directory as `_capability_map.json`.** Maturin's `python-source = "python"` setting in `pyproject.toml` means the Python package root is `python/fdars/`. All files in that directory — including non-`.py` files — are included in the wheel when maturin copies the package source tree. The existing `_capability_map.json` is not in the `[tool.maturin] include` list and ships correctly because it sits directly in the package source tree.

**To be safe and explicit, add the new file to the `include` glob pattern in `pyproject.toml`:**

```toml
[tool.maturin]
features = ["pyo3/extension-module"]
python-source = "python"
module-name = "fdars._native"
include = [
  "python/fdars/data/*.csv",
  "python/fdars/_capability_map.json",
  "python/fdars/_references_map.json",
]
```

Explicit inclusion makes the packaging contract visible and guards against any future maturin version change that might alter default non-Python file behavior.

**How the MCP tool reads the file — mirror `fdars_list_capabilities` exactly:**

```python
import json
from importlib import resources

ref_file = resources.files("fdars") / "_references_map.json"
data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
```

`importlib.resources.files()` was added in Python 3.9 (the project's minimum supported version) and returns a `Traversable` object. The `/` operator is syntactic sugar for `.joinpath()`. `.read_text(encoding="utf-8")` reads the file as a string without requiring an actual filesystem path — it works correctly inside a zip-packaged wheel or an editable install. This is the exact pattern already used in `fdars_list_capabilities` at `server.py` line 813.

**No new Python dependencies are introduced.** `json` and `importlib.resources` are both stdlib. The references file is read at tool-call time, not at import time, consistent with the `fdars_list_capabilities` lazy-load pattern.

**Docs build reads the same committed file offline:**

The MkDocs build uses `markdown-exec` to run Python fences. Any References page that renders the data should read the file via `importlib.resources.files("fdars") / "_references_map.json"` if `fdars` is installed in the docs venv (it is — the docs build requires `fdars` installed). This is network-free and offline, consistent with the `--strict` build constraint and the 22-35 min build time noted in memory. Do NOT read the file by raw filesystem path in docs fences — use the same `importlib.resources` path as the tool for consistency.

---

## 4. Testing

### Test structure mirrors GATE-04 (three-way guard-sync)

All tests use stdlib only (`json`, `re`, `urllib.parse`, `importlib.resources`, `sys`) plus `pytest`. No `jsonschema` library. No network in the default path. New file: `tests/test_references_map.py`.

**Group A — Schema validity (runs on Python 3.9+, no mcp import):**

```python
def test_references_map_schema():
    """Every paper entry has required fields; every callable entry has valid keys."""
    from importlib import resources
    import json, re
    from urllib.parse import urlparse

    data = json.loads(
        (resources.files("fdars") / "_references_map.json").read_text(encoding="utf-8")
    )
    papers = data["papers"]
    callables = data["callables"]

    _DOI_RE = re.compile(r'^10\.\d{4,9}/\S+$')

    for key, p in papers.items():
        assert "title" in p and p["title"], f"paper {key!r} missing title"
        assert "authors" in p and isinstance(p["authors"], list), \
            f"paper {key!r} authors must be list"
        assert "year" in p and isinstance(p["year"], int), \
            f"paper {key!r} year must be int"
        # doi OR url required (older books may lack DOI)
        has_doi = bool(p.get("doi", "").strip())
        has_url = bool(p.get("url", "").strip())
        assert has_doi or has_url, f"paper {key!r} needs doi or url"
        if has_doi:
            assert _DOI_RE.match(p["doi"].strip()), \
                f"paper {key!r} DOI malformed: {p['doi']!r}"
        if has_url:
            u = urlparse(p["url"])
            assert u.scheme in ("http", "https") and u.netloc, \
                f"paper {key!r} URL malformed: {p['url']!r}"

    for key, c in callables.items():
        assert "." in key, f"callable key {key!r} must be 'module.function'"
        assert "paper_keys" in c and isinstance(c["paper_keys"], list), \
            f"{key!r} paper_keys must be list"
        for pk in c["paper_keys"]:
            assert pk in papers, \
                f"{key!r} references unknown paper_key {pk!r}"
        for impl in c.get("cross_language", []):
            assert impl.get("language") in ("R", "Python", "Matlab"), \
                f"{key!r} impl language must be R/Python/Matlab"
            assert "package" in impl and "function" in impl, \
                f"{key!r} impl missing package or function"
```

**Group B — Callable index completeness vs capability map:**

```python
def test_callable_index_subset_of_capability_map():
    """Every key in callables[] matches a known callable in _capability_map.json."""
    from importlib import resources
    import json

    cap = json.loads(
        (resources.files("fdars") / "_capability_map.json").read_text(encoding="utf-8")
    )
    ref = json.loads(
        (resources.files("fdars") / "_references_map.json").read_text(encoding="utf-8")
    )

    # Build flat set of known callables from capability map
    known = set()
    for module, fns in cap.items():
        for fn in fns:
            known.add(f"{module}.{fn}")

    for key in ref["callables"]:
        assert key in known, (
            f"references callable {key!r} not found in _capability_map.json. "
            "Update the key or regenerate the capability map."
        )
```

**Group C — LLM-free boundary test for `fdars_method_references` (mirrors GATE-04, Python 3.10+ only):**

```python
def test_method_references_tool_llm_free_boundary():
    """fdars_method_references returns no model/provider keys (LLM-free boundary)."""
    import sys
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")
    pytest.importorskip("mcp")

    from fdars.mcp.server import fdars_method_references

    result = fdars_method_references("depth.fraiman_muniz_1d")

    assert "provider" not in result, \
        "must not expose 'provider' key (LLM-free boundary)"
    assert "model" not in result, \
        "must not expose 'model' key (LLM-free boundary)"
    assert "curated" in result, \
        "must return 'curated' key indicating lookup outcome"

    # Unknown callable must return explicit ungrounded signal, not raise
    result_unknown = fdars_method_references("__unknown_callable__")
    assert result_unknown.get("curated") is False, (
        "unknown callable must return curated=False (ungrounded-synthesis-permitted signal)"
    )
```

**Group D — Paper count guard-sync (Python 3.9+, lightweight drift detector):**

```python
# Hard-coded mirror of len(data["papers"]) — update in same atomic commit as JSON.
# Prevents silent paper deletions. Intentionally a count, not a full key set
# (the schema test in Group A already checks all key constraints).
_EXPECTED_PAPER_COUNT = 0  # set to actual count after initial curation

def test_references_paper_count_guard():
    """Guard-sync: paper count equals hard-coded expected value."""
    from importlib import resources
    import json

    data = json.loads(
        (resources.files("fdars") / "_references_map.json").read_text(encoding="utf-8")
    )
    actual = len(data["papers"])
    assert actual == _EXPECTED_PAPER_COUNT, (
        f"_references_map.json has {actual} papers but expected {_EXPECTED_PAPER_COUNT}. "
        "Update _EXPECTED_PAPER_COUNT in this file to match the new count."
    )
```

---

## Core Technologies (Summary)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `json` (stdlib) | Python 3.9+ | Load and parse `_references_map.json` | Already used in `fdars_list_capabilities`; zero new deps |
| `importlib.resources.files()` (stdlib) | Python 3.9+ | Read committed JSON from inside the installed wheel | Exact pattern from v12.0; works in zip wheels and editable installs |
| `re` (stdlib) | Python 3.9+ | DOI structural validation (`10.\d{4,9}/...`) | Offline, zero-dep, CI-safe |
| `urllib.parse.urlparse` (stdlib) | Python 3.9+ | URL structural well-formedness check | Offline, zero-dep, CI-safe |
| `urllib.request` (stdlib) | Python 3.9+ | Optional online DOI/URL resolve (env-gated) | Stdlib; never runs in default CI path |
| Bespoke minimal JSON | n/a | References data format | Consistent with `_capability_map.json`; no parser library needed; hand-authorable |
| `pytest` | already in `[dev]` extra | Schema validity, completeness, LLM-free boundary tests | Already in the test suite; no new dev dep |

---

## Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `importlib.resources` (stdlib) | Python 3.9+ | Package data access | Always — `resources.files("fdars") / "_references_map.json"` |
| `json` (stdlib) | Python 3.9+ | JSON decode | Always — `json.loads(file.read_text(encoding="utf-8"))` |
| `re` (stdlib) | Python 3.9+ | DOI regex structural check | In CI schema-validity test |
| `urllib.parse` (stdlib) | Python 3.9+ | URL structural check | In CI schema-validity test |

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `jsonschema` (PyPI) | New runtime/dev dependency; stdlib dict checks are sufficient for this flat schema | Manual assertions in pytest (Group A above) |
| `bibtexparser` / `pybtex` | New dependency; BibTeX is a string format requiring a parser | Bespoke JSON readable with `json.loads()` |
| `citeproc-py` or CSL-JSON tooling | Heavy dependency; CSL-JSON is for citation rendering, not machine lookup | Bespoke minimal JSON schema |
| `requests` / `httpx` | New network dependency | `urllib.request` stdlib for the optional online check |
| Network calls in `pytest` or `mkdocs build` | Violates the project's offline constraint | `os.environ.get("FDARS_ONLINE_CHECKS")` gate; default is offline |
| Separate `_references_papers.json` + `_references_callables.json` | Two-file split adds indirection with no benefit at this data size (~409 callables, ~100 papers) | Single `_references_map.json` with `papers` and `callables` top-level keys |

---

## Packaging Details

**No new `pyproject.toml` extras.** The references JSON is core package data, not optional. It ships in the base `fdars` wheel alongside `_capability_map.json`. The `fdars_method_references` MCP tool is added to `server.py` under the same `[mcp]` extra gating as today — but the JSON file itself is always installed.

**Wheel inclusion:** Add to `[tool.maturin] include` in `pyproject.toml` explicitly alongside the existing CSV glob. Glob path is relative to the project root (where `pyproject.toml` lives), matching the existing `"python/fdars/data/*.csv"` pattern.

**`importlib.resources` path invariant:** Always use `resources.files("fdars") / "_references_map.json"` — never construct a raw filesystem path. This ensures the read works identically in a wheel, an editable install (`maturin develop`), and the docs build environment.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Bespoke minimal JSON | CSL-JSON | Only if you need a citeproc renderer to produce formatted citations — not this project's use case |
| Bespoke minimal JSON | BibTeX | Only if you need LaTeX integration — requires a parser library |
| Single `_references_map.json` | Split papers/callables files | Only if the combined file grows beyond ~500KB — unlikely at this scale |
| `re` + `urllib.parse` offline | `rfc3986` (PyPI) | Only if strict RFC 3986 conformance is needed for untrusted external input — overkill for hand-authored data |
| Pytest manual assertions | `jsonschema` (PyPI) | Only if the schema becomes complex enough to justify a JSON Schema — current schema is flat enough for manual checks |

---

## Sources

- `/home/simonm/projects/rust/pyfda/python/fdars/mcp/server.py` lines 747-826 — `fdars_list_capabilities` pattern (verified: `resources.files("fdars") / "_capability_map.json"`, `json.loads(cap_file.read_text(encoding="utf-8"))`) — HIGH confidence (direct code read)
- `/home/simonm/projects/rust/pyfda/python/fdars/_capability_map.json` — existing data shape (module -> callable -> {purpose, sig}) — HIGH confidence
- `/home/simonm/projects/rust/pyfda/python/fdars/_capability_curation.json` — existing override layer shape ("module.callable" -> when-string) — HIGH confidence
- `/home/simonm/projects/rust/pyfda/tests/test_guard_sync_version_independent.py` — GATE-04 test pattern (three-way guard-sync, 3.9-safe primary + 3.10-guarded companion) — HIGH confidence
- `/home/simonm/projects/rust/pyfda/tests/test_capability_accuracy.py` — schema validation pattern (no jsonschema, stdlib only) — HIGH confidence
- `/home/simonm/projects/rust/pyfda/pyproject.toml` lines 79-87 — `[tool.maturin]` include syntax — HIGH confidence
- Python 3.9 docs (`docs.python.org/3.9`) — `importlib.resources.files()` added in 3.9; `Traversable` API — MEDIUM confidence (web fetch)
- CrossRef DOI syntax — registrant prefix `10.NNNN/suffix`, 4-9 digit prefix — MEDIUM confidence (websearch)
- Maturin docs (`maturin.rs/config.html`) — `python-source` + `include` field behavior — MEDIUM confidence (web fetch)

---

*Stack research for: fdars v13.0 Scientific Provenance & Cross-Language Implementations*  
*Researched: 2026-09-07*
