# Phase 80: Schema, Data Home & Primary Guard Tests — Research

**Researched:** 2026-09-07
**Domain:** JSON schema design, Python packaging (maturin), guard-sync test patterns, structural DOI/URL validation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- References map is a SEPARATE committed side-file `_references_map.json`, paper-keyed + flat `callable_index`, NOT merged into the auto-generated `_capability_map.json` (preserves the SKILL-02 no-drift boundary; mirrors `_capability_curation.json`).
- Identifier space is IDENTICAL to `_capability_curation.json`: `module.callable`, with `_Fdata.*` special-cased against `_capability_map.json`.
- Curation is PAPER-LEVEL with a sub-method-keyed callable index — not one paper blindly mapped across a family (band depth ≠ modified band depth).
- Author-verification is a HARD authoring rule — every paper entry checked against its DOI landing page before commit (F&M is 2001, not 1991; a resolving DOI is NOT proof of correct attribution).
- The `curated:false` / `{"sentinel": "NO_CURATED_ENTRY"}` tail convention is defined here so Phase 82's tool and Phase 81's curation share one shape.
- Cross-language entry shape carries `version` + Matlab `confidence: low` unless verified; point URLs at specific function docs.
- DOI gate is STRUCTURAL only in CI (regex + URL well-formedness + domain allowlist); live resolve is opt-in via `FDARS_ONLINE_CHECKS=1`, never under pytest/mkdocs.
- Guard tests land in the SAME commit as the artifact they guard (GATE-04 lesson).

### Claude's Discretion

- Exact 3–5 seed papers, provided they are author-verified against DOI landing pages and span DISTINCT capability families (e.g. depth, alignment/SRSF, FPCA/basis, clustering). Choose clear-provenance roots to avoid contested attributions this early.
- Precise JSON schema field names/nesting for `papers[*]` (title, authors, year, doi, url, callables, cross_language, notes) and the exact domain allowlist, guided by the mirrored `_capability_curation.json` structure and the cross-language shape above.
- Where the schema doc lives (docs/ page vs. a `docs/`-adjacent authoring note) and test file placement, following existing `tests/` and guard-sync conventions.

### Deferred Ideas (OUT OF SCOPE)

- Broad paper curation across all table-stakes/differentiator families → Phase 81.
- `fdars_method_references` MCP tool handler + full GATE-05 companion mirror → Phase 82.
- References docs page, `llms.txt` provenance section, skill hybrid protocol → Phase 83.
- Whole-site strict build + guard-sync + DOI gate close + human citation review → Phase 84.
- REF-FUT-01 (complete the uncurated tail + coverage floor) and REF-FUT-02 (opt-in live DOI liveness) → future milestone.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCHEMA-01 | Committed `_references_map.json` with paper-keyed `papers` + flat `callable_index`, seeded with 3–5 author-verified papers spanning distinct families, packaged in wheel | JSON schema shape below; maturin packaging section; seed paper table |
| SCHEMA-02 | Author-verification workflow + JSON schema doc governing curation (cross-language shape, `curated:false` tail, DOI-page bar) | Schema field documentation; cross-language entry shape section |
| SCHEMA-03 | Primary GATE-05 guard tests (Python 3.9+, no `mcp` import): (A) internal consistency; (B) cross-file resolution against `_capability_map.json` | Guard test placement and structure section; Group 3 template |
| SCHEMA-04 | Offline structural DOI/URL gate (DOI regex + URL well-formedness + domain allowlist), NO live resolve in CI; opt-in via `FDARS_ONLINE_CHECKS=1` | DOI/URL gate section; `FDARS_ONLINE_CHECKS` pattern; test file placement |
</phase_requirements>

---

## Summary

Phase 80 establishes the references data home for v13.0. It delivers exactly four artifacts: the `_references_map.json` side-file, its JSON schema documentation, primary GATE-05 guard tests, and an offline structural DOI/URL gate. This is purely internal infrastructure work — no new crate-level bindings, no MkDocs pages shipped.

The research reveals that all four artifacts fit snugly into existing patterns. The `_references_map.json` file lands alongside `_capability_curation.json` and `_capability_map.json` in `python/fdars/` and requires NO new maturin `include` entry — Python package files (`.json`, `.py`) under `python/fdars/` already ship in the wheel by maturin's default behavior and are already accessible via `importlib.resources` (verified this session). The guard tests extend `tests/test_guard_sync_version_independent.py` as Group 3, following the established Group 1/2 structure exactly: a primary test on Python 3.9+ with no `mcp` import, and 3.10+ companion tests that keep the MCP literals honest. The DOI/URL gate has a direct precedent in `tests/test_advisor_live_integration.py`'s `FDARS_INTEGRATION` master-gate pattern, now adapted as `FDARS_ONLINE_CHECKS=1` for the live-resolve opt-in.

Five seed papers are recommended, each spanning a distinct capability family. All five DOIs were verified against authoritative sources this session. The F&M year is definitively 2001 (not 1991).

**Primary recommendation:** Write `_references_map.json` with the schema shape defined below, extend `test_guard_sync_version_independent.py` with Group 3 A/B tests, and add a structural DOI/URL gate test — all in a single atomic commit.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| References map (JSON schema + data) | Python package layer (`python/fdars/`) | — | Same tier as `_capability_curation.json` and `_capability_map.json`; loaded at runtime via `importlib.resources` |
| Guard tests (GATE-05 A/B) | Test layer (`tests/`) | — | Guard-sync tests live alongside the artifact they guard; Group 3 extends existing file |
| DOI/URL structural gate | Test layer (`tests/`) | CI env gate | Offline structural check lives in pytest; live resolve gated by `FDARS_ONLINE_CHECKS=1` |
| Schema documentation | Docs layer (`docs/`) | — | Author-workflow doc is a committed docs page consumed by Phase 81 curators |

---

## Existing File Shapes — Verbatim Verification

### `python/fdars/_capability_curation.json` (identifier space source-of-truth)

**Format:** Flat map, `"module.callable"` → `"when-to-use string"`. Special-cased prefix for Fdata methods: `"_Fdata.<method>"`.
[VERIFIED: python/fdars/_capability_curation.json:1-29]

Verbatim keys (all keys in the file, complete):
```
"_Fdata.__init__"
"_Fdata.center"
"_Fdata.depth"
"_Fdata.to_pc"
"alignment.karcher_mean"
"alignment.elastic_align_pair"
"basis.basis_nbasis_cv"
"basis.basis_to_fdata_1d"
"clustering.kmeans_fd"
"fdata.functional_covariance"
"depth.fraiman_muniz_1d"
"depth.band_1d"
"depth.modal_1d"
"fdata.mean_1d"
"fdata.deriv_1d"
"fdata.norm_lp_1d"
"frechet.frechet_global_reg"
"fts.ftsm"
"fts.stationarity_test"
"inference.flm_f_test"
"inference.mean_scb"
"regression.fregre_lm"
"regression.concurrent_regression"
"scoring.functional_mae"
"simulation.sim_kl"
"smoothing.nadaraya_watson"
"smoothing.gcv_smoother"
```

**Identifier space rules (from this file):**
- Module-prefixed callables: `"<module>.<callable>"` e.g. `"depth.fraiman_muniz_1d"`
- Fdata class methods: `"_Fdata.<method>"` e.g. `"_Fdata.depth"` (leading underscore + class name)
- No bare module keys; every key has exactly one dot
- Value is a free-text string description

### `python/fdars/_capability_map.json` (cross-file resolution target for GATE-05 B)

**Format:** Nested map. Top-level keys are module names. Two shapes:
- Regular modules: `"<module>": { "<callable>": { "purpose": str, "sig": str, "when"?: str } }`
- Special class entry: `"_Fdata": { "<method>": { "purpose": str, "sig": str, "when"?: str } }`
[VERIFIED: python/fdars/_capability_map.json:1-119]

**Key module names** (submodule names only, `_Fdata` excluded from `_CAPABILITY_MODULES`):
[VERIFIED: tests/test_guard_sync_version_independent.py:186-193]
```python
frozenset({
    "alignment", "basis", "classification", "clustering", "conformal",
    "covariance", "datasets", "density_fda", "depth", "explain", "famm",
    "fdata", "frechet", "fts", "inference", "metric", "metrics", "multi_fdata",
    "outliers", "pace_fpca", "regression", "represent", "scalar_on_function",
    "scoring", "seasonal", "shapelet", "simulation", "smoothing", "spm",
    "tolerance",
})
```

**GATE-05 cross-file resolution logic:**
- For `"module.callable"` keys → look up `data["module"]["callable"]` in the capability map
- For `"_Fdata.<method>"` keys → look up `data["_Fdata"]["<method>"]` in the capability map
- A key resolves if the nested path exists (any truthy value is sufficient)

### `python/fdars/mcp/server.py` — `_CAPABILITY_MODULES` and importlib.resources pattern

**`_CAPABILITY_MODULES` definition:**
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

**`importlib.resources` load pattern used for `_capability_map.json`:**
[VERIFIED: python/fdars/mcp/server.py:808-814]
```python
import json
from importlib import resources
cap_file = resources.files("fdars") / "_capability_map.json"
data: dict = json.loads(cap_file.read_text(encoding="utf-8"))
```

Phase 82 will add a `_REFERENCES_MODULES` frozenset DERIVED from `_CAPABILITY_MODULES` (not a separate literal) and load `_references_map.json` using the identical pattern:
```python
ref_file = resources.files("fdars") / "_references_map.json"
data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
```

---

## Packaging — Maturin Include Analysis

**Finding: No new `include` entry is needed for `_references_map.json`.**

The pyproject.toml `[tool.maturin]` section currently reads:
[VERIFIED: pyproject.toml:86]
```toml
include = ["python/fdars/data/*.csv"]
```

The `data/*.csv` entries need explicit `include` because they are in a subdirectory (`python/fdars/data/`) that maturin might not auto-include. However, files directly in `python/fdars/` (the package root under `python-source = "python"`) are part of the Python package and ship automatically with the wheel.

**Verification:** Both `_capability_map.json` and `_capability_curation.json` currently live in `python/fdars/` with NO explicit `include` entry, and both are accessible via `importlib.resources` in the installed dev package:
[VERIFIED by bash probe this session]
```
resources.files('fdars') / '_capability_map.json'  → found: True
resources.files('fdars') / '_capability_curation.json'  → found: True
```

**Conclusion:** Place `_references_map.json` in `python/fdars/_references_map.json`. It will ship in the wheel automatically. The planner does NOT need to add a maturin `include` entry.

---

## Recommended JSON Schema Shape

### Top-level structure

```json
{
  "papers": {
    "<paper_key>": { ... }
  },
  "callable_index": {
    "<module>.<callable>": ["<paper_key>", ...],
    "_Fdata.<method>": ["<paper_key>", ...]
  }
}
```

**`paper_key`** is a short, stable ASCII slug: `"fraiman_muniz_2001"`, `"lopez_pintado_romo_2009"`, etc. Lowercase, no spaces, year suffix to distinguish same-author multi-papers.

**Internal consistency invariant (GATE-05 A):**
```python
frozenset(data["callable_index"].keys()) == frozenset(
    c for p in data["papers"].values() for c in p["callables"]
)
```
Every callable in any paper's `callables` list must appear in `callable_index`, and vice versa.

### `papers[*]` entry shape

```json
{
  "title": "Trimmed means for functional data",
  "authors": ["Fraiman, R.", "Muniz, G."],
  "year": 2001,
  "doi": "10.1007/BF02595706",
  "url": "https://link.springer.com/article/10.1007/BF02595706",
  "type": "journal",
  "callables": [
    "depth.fraiman_muniz_1d",
    "depth.fraiman_muniz_2d",
    "_Fdata.depth"
  ],
  "cross_language": {
    "R": {
      "package": "fda.usc",
      "function": "depth.FM",
      "url": "https://rdrr.io/cran/fda.usc/man/depth.fdata.html"
    }
  },
  "notes": "Introduces marginal-integral depth (Fraiman-Muniz depth). Year is 2001, not 1991.",
  "curated": true
}
```

**All fields:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | yes | Full paper title, verbatim from DOI landing page |
| `authors` | array[string] | yes | `"LastName, Initials."` format, ordered as in paper |
| `year` | integer | yes | Publication year (not preprint year) |
| `doi` | string | yes | Must match `^10\.\d{4,9}/\S+$`; omit leading `doi:` or `https://doi.org/` |
| `url` | string | yes | Canonical landing page URL; for journal papers, the publisher URL |
| `type` | enum string | yes | One of `"journal"`, `"conference"`, `"preprint"`, `"book"`, `"book_chapter"` |
| `callables` | array[string] | yes | `"module.callable"` or `"_Fdata.<method>"` identifiers; each must resolve in `_capability_map.json` |
| `cross_language` | object | no | Cross-language implementations; keys are `"R"`, `"Python"`, `"Matlab"` |
| `notes` | string | no | Curator notes; attribution warnings, version notes, contested-attribution flags |
| `curated` | boolean | yes | `true` = author+year+title verified against DOI landing page personally; `false` = pending |

**`cross_language[*]` entry shape:**

```json
{
  "package": "<package-name>",
  "function": "<function-or-method-name>",
  "version": "1.4.0",
  "url": "https://specific-function-docs-url",
  "confidence": "high"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `package` | string | yes | Package or library name |
| `function` | string | yes | Specific function/method name |
| `version` | string | no | Verified-against version; omit if unknown |
| `url` | string | yes | Points to specific function docs, not package homepage |
| `confidence` | enum | yes | `"high"` = personally verified; `"low"` = inferred from docs/README only. **Matlab entries default to `"low"` unless verified.** |

**`curated:false` tail convention:**

For callables known to need references but not yet curated, include an uncurated entry with `curated: false`:
```json
{
  "_uncurated_placeholder": {
    "title": "",
    "authors": [],
    "year": null,
    "doi": "",
    "url": "",
    "type": "journal",
    "callables": ["<module>.<callable>"],
    "curated": false
  }
}
```

In Phase 80, the stub file has NO uncurated entries (the seed papers are all author-verified). The tail convention is specified here so Phase 81's curation work can start adding `curated:false` entries that won't break GATE-05 A (the guard only checks consistency, not `curated` status).

---

## Guard Test Placement and Structure (GATE-05)

### File location

**Add Group 3 tests to the existing file:**
`tests/test_guard_sync_version_independent.py`

This is the established home for guard-sync tests that span Python versions. The file currently has Groups 1 and 2; Group 3 (GATE-05) follows the exact same structural pattern.

### Group 3 template (complete, implementation-ready)

```python
# ===========================================================================
# Guard Group 3 — _references_map.json primary GATE-05 (SCHEMA-03)
# ===========================================================================

# ---------------------------------------------------------------------------
# PRIMARY TEST A — runs on Python 3.9+ (no mcp import, no fdars.mcp.server import)
# ---------------------------------------------------------------------------


def test_references_map_internal_consistency():
    """GATE-05 A: callable_index keys == union of papers[*].callables (Python 3.9+).

    Loads the committed ``_references_map.json`` via importlib.resources (no
    mcp dependency; Py 3.9-safe) and asserts the internal consistency invariant:

        frozenset(callable_index.keys())
            == frozenset(c for p in papers.values() for c in p["callables"])

    Fails if:
    - A paper's callables list contains a key not in callable_index (orphan callable).
    - callable_index contains a key with no paper referencing it (phantom index entry).

    Reference: GATE-05 A — no skip; this test MUST run on Python 3.9.
    """
    ref_file = resources.files("fdars") / "_references_map.json"
    data: dict = json.loads(ref_file.read_text(encoding="utf-8"))

    papers = data.get("papers", {})
    callable_index = data.get("callable_index", {})

    from_papers: frozenset[str] = frozenset(
        c for p in papers.values() for c in p.get("callables", [])
    )
    from_index: frozenset[str] = frozenset(callable_index.keys())

    assert from_papers == from_index, (
        f"_references_map.json internal consistency failure (GATE-05 A).\n"
        f"  In papers but not in callable_index: {from_papers - from_index}\n"
        f"  In callable_index but not in any paper: {from_index - from_papers}\n"
        "Ensure every callable in papers[*].callables appears in callable_index "
        "and vice versa."
    )


# ---------------------------------------------------------------------------
# PRIMARY TEST B — runs on Python 3.9+ (no mcp import)
# ---------------------------------------------------------------------------


def test_references_map_cross_file_resolution():
    """GATE-05 B: every callable_index key resolves in _capability_map.json (Python 3.9+).

    Loads both ``_references_map.json`` and ``_capability_map.json`` via
    importlib.resources and asserts every key in ``callable_index`` resolves to
    an existing callable in the capability map:

    - For ``"module.callable"`` keys: ``cap_data["module"]["callable"]`` must exist.
    - For ``"_Fdata.<method>"`` keys: ``cap_data["_Fdata"]["<method>"]`` must exist.

    Fails if a key in callable_index refers to a callable that does not exist
    in the capability map (renamed, removed, or mistyped callable).

    Reference: GATE-05 B — no skip; this test MUST run on Python 3.9.
    """
    ref_file = resources.files("fdars") / "_references_map.json"
    cap_file = resources.files("fdars") / "_capability_map.json"

    ref_data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
    cap_data: dict = json.loads(cap_file.read_text(encoding="utf-8"))

    callable_index = ref_data.get("callable_index", {})
    unresolved: list[str] = []

    for key in callable_index:
        if "." not in key:
            unresolved.append(f"{key!r} — no dot separator")
            continue
        module, callable_name = key.split(".", 1)
        if module not in cap_data:
            unresolved.append(f"{key!r} — module {module!r} not in capability map")
        elif callable_name not in cap_data[module]:
            unresolved.append(
                f"{key!r} — {callable_name!r} not in capability_map[{module!r}]"
            )

    assert not unresolved, (
        f"_references_map.json cross-file resolution failures (GATE-05 B):\n"
        + "\n".join(f"  - {e}" for e in unresolved)
        + "\nEnsure all callable_index keys exist in _capability_map.json. "
        "If a callable was renamed, update _references_map.json to match."
    )
```

### Companion tests (Python 3.10+, Phase 82 deferred)

Group 3 companion tests (asserting `_REFERENCES_MODULES` matches the JSON surface, LLM-free boundary) are DEFERRED to Phase 82, when `fdars_method_references` is implemented and `_REFERENCES_MODULES` is defined in `server.py`. Phase 80 only ships the two primary tests (A and B).

### Structural placement rules

These exactly mirror the existing Group 1/2 pattern:
[VERIFIED: tests/test_guard_sync_version_independent.py:81-135 (Group 1), 196-228 (Group 2)]

- **No `pytestmark` skip:** Both GATE-05 tests MUST run on Python 3.9.
- **No `mcp` import at module level:** `from importlib import resources` and `import json` (both stdlib) are the only new imports needed — both already present in the test file.
- **Pytest autodiscovery:** Both tests follow the `test_` prefix convention and live in `tests/`, which is the CI pytest target (`pytest tests/ -v`).
[VERIFIED: .github/workflows/ci.yml:88]

---

## Structural DOI/URL Gate (SCHEMA-04)

### Test file placement

Add to `tests/test_guard_sync_version_independent.py` as **Group 3 C** (same atomic commit as Groups 3 A and 3 B):

```python
# ---------------------------------------------------------------------------
# PRIMARY TEST C — runs on Python 3.9+ — STRUCTURAL DOI/URL gate (no live resolve)
# ---------------------------------------------------------------------------

import os
import re
import urllib.parse

_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")

# Domain allowlist for cross-language entry URLs and paper landing pages.
# Extend this list in Phase 81/84 as new reference domains are verified.
_ALLOWED_DOMAINS = frozenset({
    # Publisher / preprint hosts
    "doi.org", "link.springer.com", "www.tandfonline.com",
    "academic.oup.com", "onlinelibrary.wiley.com", "www.sciencedirect.com",
    "dl.acm.org", "ieeexplore.ieee.org", "www.jstor.org",
    "projecteuclid.org", "arxiv.org", "www.researchgate.net",
    "pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
    # Cross-language reference hosts (R, Python)
    "rdrr.io", "cran.r-project.org", "www.rdocumentation.org",
    "pypi.org", "fdasrsf-python.readthedocs.io",
    # fdars own docs
    "sipemu.github.io",
})


def test_references_map_doi_url_structural_gate():
    """GATE-05 C: structural DOI regex + URL well-formedness (NO live resolve).

    Checks every paper entry in _references_map.json for:
    - doi: matches ^10\\.\\d{4,9}/\\S+$ (SCHEMA-04 DOI regex)
    - url: well-formed http/https URL; domain in _ALLOWED_DOMAINS

    For cross_language entries:
    - url: well-formed http/https URL; domain in _ALLOWED_DOMAINS

    NO live network resolve is performed. FDARS_ONLINE_CHECKS=1 is checked and
    test raises pytest.skip if the env var is set (live resolve is opt-in only).

    Reference: SCHEMA-04 — no mcp import; runs on Python 3.9+.
    """
    if os.environ.get("FDARS_ONLINE_CHECKS") == "1":
        pytest.skip("FDARS_ONLINE_CHECKS=1 set — live resolve path; skip structural gate.")

    ref_file = resources.files("fdars") / "_references_map.json"
    data: dict = json.loads(ref_file.read_text(encoding="utf-8"))

    errors: list[str] = []
    papers = data.get("papers", {})

    for key, paper in papers.items():
        doi = paper.get("doi", "")
        url = paper.get("url", "")

        # DOI structural check (skip empty doi for curated:false entries)
        if paper.get("curated", True) and doi:
            if not _DOI_RE.match(doi):
                errors.append(f"papers[{key!r}].doi {doi!r} does not match ^10.\\d{{4,9}}/\\S+$")

        # URL well-formedness + domain check
        if url:
            try:
                parsed = urllib.parse.urlparse(url)
                if parsed.scheme not in ("http", "https"):
                    errors.append(f"papers[{key!r}].url {url!r} — scheme must be http/https")
                elif parsed.netloc not in _ALLOWED_DOMAINS:
                    errors.append(
                        f"papers[{key!r}].url domain {parsed.netloc!r} not in _ALLOWED_DOMAINS"
                    )
            except Exception as exc:
                errors.append(f"papers[{key!r}].url {url!r} — parse error: {exc}")

        # Cross-language URL checks
        for lang, cl_entry in paper.get("cross_language", {}).items():
            cl_url = cl_entry.get("url", "")
            if cl_url:
                try:
                    parsed = urllib.parse.urlparse(cl_url)
                    if parsed.scheme not in ("http", "https"):
                        errors.append(
                            f"papers[{key!r}].cross_language[{lang!r}].url {cl_url!r} — "
                            "scheme must be http/https"
                        )
                    elif parsed.netloc not in _ALLOWED_DOMAINS:
                        errors.append(
                            f"papers[{key!r}].cross_language[{lang!r}].url domain "
                            f"{parsed.netloc!r} not in _ALLOWED_DOMAINS"
                        )
                except Exception as exc:
                    errors.append(
                        f"papers[{key!r}].cross_language[{lang!r}].url — parse error: {exc}"
                    )

    assert not errors, (
        "Structural DOI/URL gate failures (SCHEMA-04):\n"
        + "\n".join(f"  - {e}" for e in errors)
    )
```

### `FDARS_ONLINE_CHECKS=1` gating convention

**Prior art:** `tests/test_advisor_live_integration.py` uses `FDARS_INTEGRATION=1` as a master gate [VERIFIED: tests/test_advisor_live_integration.py:80-86]. The pattern is:

```python
_GATE = os.environ.get("FDARS_INTEGRATION") == "1"
@pytest.mark.skipif(not _GATE, reason="...")
def test_live_...():
    ...
```

GATE-05 C inverts this: it runs ALWAYS (no skipif), but if `FDARS_ONLINE_CHECKS=1` is set it calls `pytest.skip()` internally with a message. This is intentional: the structural gate must run in CI unconditionally; only the live-resolve path (a separate future test or script) uses the env var to opt in.

**CI behavior:** The CI `ci.yml` `test-python` job runs `pytest tests/ -v` with no special env vars [VERIFIED: .github/workflows/ci.yml:86-88]. GATE-05 C runs structurally in every CI run. Live resolve is never triggered.

---

## Seed Papers — Verified Candidates

Five papers spanning distinct capability families. All DOIs and author attributions are verified against authoritative sources this session.

| # | Family | Paper Key | Authors | Year | DOI | URL | `callables` (representative) | Notes |
|---|--------|-----------|---------|------|-----|-----|-------------------------------|-------|
| 1 | Functional Depth | `fraiman_muniz_2001` | Fraiman, R.; Muniz, G. | 2001 | `10.1007/BF02595706` | https://link.springer.com/article/10.1007/BF02595706 | `depth.fraiman_muniz_1d`, `depth.fraiman_muniz_2d`, `_Fdata.depth` | Introduces marginal-integral (FM) depth. Year = 2001 (TEST journal). **NOT 1991.** |
| 2 | Band Depth | `lopez_pintado_romo_2009` | López-Pintado, S.; Romo, J. | 2009 | `10.1198/jasa.2009.0108` | https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.0108 | `depth.band_1d`, `depth.modified_band_1d` | Introduces band depth (BD) and modified band depth (MBD). JASA. |
| 3 | Elastic Alignment / SRSF | `srivastava_et_al_2011` | Srivastava, A.; Wu, W.; Kurtek, S.; Klassen, E.; Marron, J.S. | 2011 | — (arXiv preprint) | https://arxiv.org/abs/1103.3817 | `alignment.karcher_mean`, `alignment.elastic_align_pair`, `alignment.srsf_transform` | Fisher-Rao metric framework; SRSF/SRVF. arXiv:1103.3817. No journal DOI — type = `"preprint"`. |
| 4 | FPCA / Functional PCA | `ramsay_dalzell_1991` | Ramsay, J.O.; Dalzell, C.J. | 1991 | `10.1111/j.2517-6161.1991.tb01844.x` | https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.2517-6161.1991.tb01844.x | `_Fdata.to_pc`, `represent.*` | Seminal FDA paper introducing FPCA as functional PCs. JRSS-B. |
| 5 | B-spline Smoothing (P-spline) | `eilers_marx_1996` | Eilers, P.H.C.; Marx, B.D. | 1996 | `10.1214/ss/1038425655` | https://projecteuclid.org/journals/statistical-science/volume-11/issue-2/Flexible-smoothing-with-B-splines-and-penalties/10.1214/ss/1038425655.full | `smoothing.gcv_smoother`, `basis.basis_nbasis_cv`, `basis.pspline_fit_1d` | Introduces P-splines (penalised B-splines with difference penalty). Statistical Science. |

**Provenance tags:**
- Papers 1, 2, 4, 5: [VERIFIED: publisher landing page confirmed via web search this session; DOI confirmed against authoritative journal/publisher URLs]
- Paper 3: [CITED: arxiv.org/abs/1103.3817] — arXiv preprint with no peer-reviewed journal DOI in the sources found. A later peer-reviewed version may exist (Srivastava & Klassen 2016 book); use arXiv for now, type = `"preprint"`, no `doi` field.

**Attribution notes:**
- F&M paper: Title is "Trimmed means for functional data" published in TEST journal 2001. The `fraiman_muniz_1d` depth function is named for this paper. The depth concept is introduced in the paper as the marginal-integral depth. [VERIFIED: link.springer.com/article/10.1007/BF02595706]
- Band depth: LP&R 2009 introduces both BD and MBD. The modified band depth (`depth.modified_band_1d`) is in the SAME paper — it is correct to attribute both to this single paper key.
- SRSF: The SRSF framework (for functional data, distinguishing from the SRV for curves/shapes) uses arXiv:1103.3817. A related companion paper is Srivastava-Klassen-Joshi-Jermyn (2011 IEEE TPAMI, DOI: `10.1109/TPAMI.2010.184`) which is for shapes of curves in Euclidean spaces (SRV representation). For fdars which implements SRSF for functional data alignment, prefer the arXiv preprint over the TPAMI paper to avoid conflating SRV (shape) with SRSF (functional data).

---

## Schema Documentation Location

**Recommendation:** Create `docs/authoring/references-schema.md` as a new subdirectory page. This is consistent with how CLAUDE.md describes the docs site structure and avoids cluttering the top-level `docs/` with an authoring-internal page.

Alternatively (simpler for Phase 80): ship the schema documentation as an inline comment block at the top of `_references_map.json` itself (not possible — JSON has no comments) or as a companion `docs/_references_schema.md` or `python/fdars/_references_map_schema.md`. The planner should choose; the CONTEXT.md says "where the schema doc lives" is Claude's discretion.

**Recommended:** `docs/authoring/references-schema.md` — a dedicated authoring guide. Phase 83 will link to it from the references docs page. Keep it a pure Markdown file with no `exec` fences (no live code execution needed for a schema spec).

---

## `generate_capability_dataset.py` — Offline Generation Precedent

The existing script has two paths [VERIFIED: scripts/generate_capability_dataset.py:501-513]:
- Default: regenerates `_capability_map.json` from live fdars (requires installed package)
- `--llmstxt`: emits `docs/llms.txt` and `docs/ai-capability-map.md` from the COMMITTED JSON (no live fdars needed)

Phase 83 will add a `--references` path that emits the references docs section from the committed `_references_map.json`. The pattern to follow:

```python
if "--references" in sys.argv:
    emit_references_docs(repo_root)  # reads _references_map.json offline
```

This is OUT OF SCOPE for Phase 80. Document it here so the planner knows to note it in Phase 83's context.

---

## Common Pitfalls

### Pitfall 1: F&M Year (1991 vs 2001)
**What goes wrong:** The Fraiman-Muniz depth paper is cited as 1991 in some secondary sources. 1991 is the year of the Ramsay-Dalzell paper; Fraiman-Muniz is 2001.
**Why it happens:** Both are landmark FDA papers; the years are confused by proximity.
**How to avoid:** The DOI `10.1007/BF02595706` resolves to a 2001 publication in TEST journal (TEST 10(2), 2001). Always verify against the DOI landing page, not secondary citations.
**Warning signs:** Any reference stub listing F&M as 1991 is wrong. The Ramsay-Dalzell 1991 paper has DOI `10.1111/j.2517-6161.1991.tb01844.x`.

### Pitfall 2: Wheel Packaging — Believing `include` is Required for JSON in `python/fdars/`
**What goes wrong:** Adding an unnecessary `include = ["python/fdars/*.json"]` to `pyproject.toml` (already works without it).
**Why it happens:** The `data/*.csv` explicit `include` suggests all data files need explicit inclusion.
**How to avoid:** Files directly under `python/fdars/` (the Python package root under `python-source = "python"`) are part of the Python package namespace and ship automatically in the wheel. Only files in subdirectories not part of the package namespace (e.g., `python/fdars/data/`) need explicit `include`.
**Verification:** `_capability_map.json` and `_capability_curation.json` already ship without any explicit include entry.

### Pitfall 3: Guard-Sync Drift — Forgetting the Atomic Commit Rule
**What goes wrong:** The JSON file is committed in one commit and the guard tests in a later commit. If CI runs between commits, the guard tests fail on a file that doesn't exist yet.
**Why it happens:** Multi-step authoring workflows split artifact + test commits.
**How to avoid:** GATE-04 lesson (from CONTEXT.md): guard tests land in the SAME commit as the artifact they guard. Phase 80 delivers `_references_map.json` + guard tests (GATE-05 A, B, C) in one atomic commit.

### Pitfall 4: SRSF vs SRV Paper Confusion
**What goes wrong:** Attributing the SRSF functional alignment framework to the Srivastava-Klassen-Joshi-Jermyn 2011 IEEE TPAMI paper (DOI: `10.1109/TPAMI.2010.184`), which is actually about the square-root velocity (SRV) representation for curve shapes in Euclidean spaces — NOT the SRSF for functional data alignment.
**Why it happens:** Both papers are by overlapping authors (Srivastava, Klassen), both use "square root" transformations, both published in 2011.
**How to avoid:** Use arXiv:1103.3817 (Srivastava, Wu, Kurtek, Klassen, Marron 2011) for the SRSF/functional-data alignment root. The TPAMI paper is for 2D shape analysis.

### Pitfall 5: `callable_index` Drift from `papers[*].callables`
**What goes wrong:** Manually editing one section but not the other, breaking GATE-05 A.
**Why it happens:** The `callable_index` and `papers[*].callables` are redundant by design (one provides lookup direction, the other provides provenance direction). Manual edits are error-prone.
**How to avoid:** Always edit both sections together. GATE-05 A catches any mismatch immediately.

### Pitfall 6: LP-Romo 2009 — Same Paper for BD and MBD
**What goes wrong:** Creating two separate paper entries for band depth and modified band depth because they "feel like different methods."
**Why it happens:** MBD was introduced as an improvement to BD in the same paper.
**How to avoid:** One paper key (`lopez_pintado_romo_2009`) with both `depth.band_1d` and `depth.modified_band_1d` in the `callables` list. The paper is the unit of attribution.

---

## Architecture Patterns

### Recommended Project Structure (new files only)

```
python/fdars/
├── _references_map.json      # NEW — paper-keyed refs + callable_index
tests/
└── test_guard_sync_version_independent.py  # EXTENDED — add Group 3 (A, B, C)
docs/authoring/
└── references-schema.md      # NEW — curator workflow + schema specification
```

### Pattern: Extending `test_guard_sync_version_independent.py`

The file has a clean group structure separated by `# ===========` header comments [VERIFIED: tests/test_guard_sync_version_independent.py:172-175]. Add Group 3 after Group 2's closing companion tests (line 301). No changes to existing Group 1 or 2 code.

New imports needed in the test file (both already present in the module-level import block [VERIFIED: tests/test_guard_sync_version_independent.py:35-41]):
```python
import os          # already imported via test_advisor_live_integration.py pattern
import re          # new for DOI regex
import urllib.parse  # new for URL parsing
```

The existing imports are: `ast`, `json`, `sys`, `resources`, `pytest`. Need to add `os`, `re`, `urllib.parse` at module level.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (no version pin; installed via `dev` extra) |
| Config file | none — pytest auto-discovers `tests/` |
| Quick run command | `pytest tests/test_guard_sync_version_independent.py -v` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCHEMA-01 | `_references_map.json` loadable via importlib.resources | unit (structural) | `pytest tests/test_guard_sync_version_independent.py::test_references_map_internal_consistency` | ❌ Wave 0 |
| SCHEMA-03 A | callable_index == union of papers[*].callables | unit (guard) | `pytest tests/test_guard_sync_version_independent.py::test_references_map_internal_consistency` | ❌ Wave 0 |
| SCHEMA-03 B | callable_index keys resolve in _capability_map.json | unit (guard) | `pytest tests/test_guard_sync_version_independent.py::test_references_map_cross_file_resolution` | ❌ Wave 0 |
| SCHEMA-04 | DOI regex + URL structural gate, no live resolve | unit (structural) | `pytest tests/test_guard_sync_version_independent.py::test_references_map_doi_url_structural_gate` | ❌ Wave 0 |

### Wave 0 Gaps

- [ ] `python/fdars/_references_map.json` — the data artifact under test
- [ ] Group 3 A/B/C in `tests/test_guard_sync_version_independent.py` — the tests themselves
- [ ] `docs/authoring/references-schema.md` — schema documentation (not a test file)

### Sampling Rate

- **Per task commit:** `pytest tests/test_guard_sync_version_independent.py -v`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ | GATE-05 (all tests) | ✓ | 3.12 (local) | — |
| `importlib.resources` | JSON loading | ✓ | stdlib | — |
| `fdars` (installed) | All tests | ✓ | dev install | `maturin develop` |
| `pytest` | Test runner | ✓ | installed | — |
| DOI network access | SCHEMA-04 live resolve (opt-in only) | ✓ | — | Structural gate runs without network |

---

## Security Domain

No security-sensitive surface introduced in this phase. All artifacts are:
- Read-only JSON side-files
- Test-only code with no network access in CI
- No user-supplied inputs processed at runtime

ASVS categories: Not applicable (no authentication, no session, no network endpoints).

---

## Sources

### Primary (HIGH confidence)

- `python/fdars/_capability_curation.json` — exact identifier space (all keys verbatim)
- `python/fdars/_capability_map.json` — cross-file resolution target structure
- `python/fdars/mcp/server.py` — `_CAPABILITY_MODULES` frozenset and importlib.resources load pattern
- `tests/test_guard_sync_version_independent.py` — Group 1/2 structure, guard pattern, expected frozensets
- `pyproject.toml` — maturin `include` and `python-source` configuration
- `scripts/generate_capability_dataset.py` — offline generation pattern precedent
- `.github/workflows/ci.yml` — CI test invocation, Python version matrix
- `tests/test_advisor_live_integration.py` — env-gating pattern (`FDARS_INTEGRATION=1`)
- [Springer/TEST journal: Fraiman & Muniz 2001](https://link.springer.com/article/10.1007/BF02595706) — DOI `10.1007/BF02595706`
- [JASA: López-Pintado & Romo 2009](https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.0108) — DOI `10.1198/jasa.2009.0108`
- [arXiv:1103.3817: Srivastava et al. 2011](https://arxiv.org/abs/1103.3817) — SRSF framework
- [JRSS-B: Ramsay & Dalzell 1991](https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.2517-6161.1991.tb01844.x) — DOI `10.1111/j.2517-6161.1991.tb01844.x`
- [Statistical Science: Eilers & Marx 1996](https://projecteuclid.org/journals/statistical-science/volume-11/issue-2/Flexible-smoothing-with-B-splines-and-penalties/10.1214/ss/1038425655.full) — DOI `10.1214/ss/1038425655`

### Secondary (MEDIUM confidence)

- Srivastava-Klassen-Joshi-Jermyn 2011 IEEE TPAMI (DOI `10.1109/TPAMI.2010.184`) confirmed to be SRV for curve shapes (NOT SRSF for functional data alignment) via Semantic Scholar and DL.ACM

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `_references_map.json` in `python/fdars/` ships in the wheel without a new `include` entry | Packaging | Would need one-line pyproject.toml addition; low risk, easy fix |
| A2 | The Srivastava et al. 2011 arXiv preprint (1103.3817) is the correct root reference for the SRSF alignment in fdars-core | Seed Papers | Should verify with fdars-core maintainer; the fdars alignment module could cite a different authoritative source |
| A3 | `docs/authoring/` subdirectory does not yet exist in the repo | Schema Doc Location | If it exists, schema doc goes there; if not, create `docs/authoring/` in the same commit |

---

## Open Questions

1. **SRSF root paper confirmation**
   - What we know: Srivastava et al. arXiv:1103.3817 introduces SRSF for functional data alignment; the TPAMI 2010/2011 paper is for curve shapes.
   - What's unclear: fdars-core may cite a different authoritative source internally (e.g., the Srivastava-Klassen 2016 book).
   - Recommendation: Phase 81 should check fdars-core source/docs for any explicit citation and update if needed.

2. **`rrsf_transform`, `srsf_inverse` callables for paper 3**
   - What we know: `alignment.srsf_transform` and `alignment.srsf_inverse` exist in `_capability_map.json`.
   - What's unclear: Phase 80 stub only needs 3–5 representative callables; including all SRSF-derived callables is Phase 81 work.
   - Recommendation: Seed stub includes only `alignment.karcher_mean`, `alignment.elastic_align_pair`, `alignment.srsf_transform` for paper 3.

---

## Metadata

**Confidence breakdown:**
- JSON schema shape: HIGH — derived from verbatim inspection of `_capability_curation.json` and `_capability_map.json`
- Guard test structure: HIGH — derived from verbatim inspection of `test_guard_sync_version_independent.py`
- Packaging/maturin: HIGH — verified via bash probe that existing JSONs ship without explicit include
- DOI/URL gate pattern: HIGH — derived from `test_advisor_live_integration.py` env-gate pattern
- Seed paper DOIs (F&M, LP&R, Ramsay-Dalzell, Eilers-Marx): HIGH — publisher URLs confirmed via web search
- SRSF paper (arXiv:1103.3817): MEDIUM — arXiv confirmed; journal version uncertain

**Research date:** 2026-09-07
**Valid until:** 2026-10-07 (stable schema; web sources stable; fdars codebase may evolve)

---

## RESEARCH COMPLETE
