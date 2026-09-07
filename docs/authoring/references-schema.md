# References Map Schema & Author-Verification Workflow

This page documents the locked schema for `python/fdars/_references_map.json` and the
mandatory author-verification workflow that governs all curation of that file. Read this
before adding any paper entry.

**Hard rule:** `_references_map.json` is never authored free-form. Every entry is
validated from day one by the GATE-05 guard tests. Authoring an entry that violates the
schema causes an immediate CI failure.

---

## Purpose & Scope

`_references_map.json` is the paper-level provenance side-file for fdars callables. It
maps primary literature (journal articles, conference papers, preprints, books) to the
specific fdars functions they introduced or justify. The file is:

- Authored entirely by hand — no auto-generation.
- Validated continuously by GATE-05 guard tests (Groups 3 A, B, C in
  `tests/test_guard_sync_version_independent.py`).
- Loaded at runtime via `importlib.resources` (no I/O at import time; loaded on demand
  by the MCP tool handler in Phase 82).
- The single source of truth for citation provenance in the fdars capability surface.

---

## File Location & Packaging

**Location:** `python/fdars/_references_map.json`

**Packaging:** Files directly under `python/fdars/` (the Python package root configured
via `python-source = "python"` in `pyproject.toml`) ship in the wheel automatically.
No maturin `include` entry is needed — verified against the analogous files
`_capability_map.json` and `_capability_curation.json`, which already ship without an
explicit `include` entry.

**Loading pattern** (same as `_capability_map.json`):

```python
import json
from importlib import resources

ref_file = resources.files("fdars") / "_references_map.json"
data: dict = json.loads(ref_file.read_text(encoding="utf-8"))
```

---

## Identifier Space

Keys in `callable_index` (and in each paper's `callables` array) must use the SAME
identifier space as `_capability_curation.json`:

- Regular callables: `"module.callable"` — exactly one dot, e.g. `"depth.fraiman_muniz_1d"`
- Fdata class methods: `"_Fdata.<method>"` — leading underscore + class name + dot, e.g. `"_Fdata.depth"`
- No bare module keys; no nested dots; no top-level names without a dot

Every identifier claimed in `_references_map.json` MUST resolve in `_capability_map.json`
(GATE-05 B enforces this). If a callable is renamed or removed from the capability map,
update `_references_map.json` in the same commit.

---

## Top-Level Shape

The file has exactly two top-level keys:

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

**`paper_key`** is a short, stable ASCII slug: lowercase, no spaces, year suffix to
distinguish same-author multi-papers. Examples: `"fraiman_muniz_2001"`,
`"lopez_pintado_romo_2009"`. Once a paper key is committed, do not rename it —
downstream phases (Phase 82 MCP tool, Phase 83 docs) reference these keys by name.

**Internal consistency invariant (GATE-05 A):**

```python
frozenset(callable_index.keys()) == frozenset(
    c for p in papers.values() for c in p["callables"]
)
```

Every callable in any paper's `callables` list must appear in `callable_index`, and vice
versa. Both sections must be edited together — never update one without updating the other.
GATE-05 A catches any mismatch immediately (see Pitfall 5 below).

### Shipped example (Phase 80 seed)

The 5-paper seed committed in Phase 80 and the 10 `callable_index` entries:

```json
{
  "papers": {
    "fraiman_muniz_2001": {
      "callables": ["depth.fraiman_muniz_1d", "depth.fraiman_muniz_2d", "_Fdata.depth"]
    },
    "lopez_pintado_romo_2009": {
      "callables": ["depth.band_1d", "depth.modified_band_1d"]
    },
    "srivastava_et_al_2011": {
      "callables": ["alignment.karcher_mean", "alignment.elastic_align_pair", "alignment.srsf_transform"]
    },
    "ramsay_dalzell_1991": {
      "callables": ["_Fdata.to_pc"]
    },
    "eilers_marx_1996": {
      "callables": ["basis.basis_nbasis_cv"]
    }
  },
  "callable_index": {
    "depth.fraiman_muniz_1d": ["fraiman_muniz_2001"],
    "depth.fraiman_muniz_2d": ["fraiman_muniz_2001"],
    "_Fdata.depth": ["fraiman_muniz_2001"],
    "depth.band_1d": ["lopez_pintado_romo_2009"],
    "depth.modified_band_1d": ["lopez_pintado_romo_2009"],
    "alignment.karcher_mean": ["srivastava_et_al_2011"],
    "alignment.elastic_align_pair": ["srivastava_et_al_2011"],
    "alignment.srsf_transform": ["srivastava_et_al_2011"],
    "_Fdata.to_pc": ["ramsay_dalzell_1991"],
    "basis.basis_nbasis_cv": ["eilers_marx_1996"]
  }
}
```

---

## `papers[*]` Field Reference

Every paper entry must follow this shape:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | yes | Full paper title, verbatim from the DOI landing page |
| `authors` | array of strings | yes | `"LastName, Initials."` format, ordered as in the paper |
| `year` | integer | yes | Publication year (journal pub date, not preprint submission date) |
| `doi` | string | conditional | Must match `^10\.\d{4,9}/\S+$`; omit the leading `doi:` or `https://doi.org/` prefix; omit entirely for preprints with no journal DOI |
| `url` | string | yes | Canonical landing page — for journal articles, the publisher URL |
| `type` | string enum | yes | One of: `"journal"`, `"conference"`, `"preprint"`, `"book"`, `"book_chapter"` |
| `callables` | array of strings | yes | `"module.callable"` or `"_Fdata.<method>"` identifiers; each must resolve in `_capability_map.json` |
| `cross_language` | object | no | Cross-language implementations; see `cross_language[*]` shape below |
| `notes` | string | no | Curator notes: attribution warnings, version constraints, contested-attribution flags |
| `curated` | boolean | yes | `true` = author + year + title personally verified against the DOI landing page; `false` = pending |

**`doi` field rule:** The DOI regex is `^10\.\d{4,9}/\S+$`. Write only the bare DOI
identifier, for example `"10.1007/BF02595706"`. Do not include `"doi:"`, `"https://doi.org/"`,
or any other prefix. GATE-05 C validates this regex for every entry where `doi` is present
and `curated` is `true`.

**`type` rule:** Use `"preprint"` when no peer-reviewed journal DOI is available. Omit
the `doi` field entirely for preprints (do not set it to `null` or `""`).

**Verbatim example — `fraiman_muniz_2001`:**

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
      "url": "https://rdrr.io/cran/fda.usc/man/depth.fdata.html",
      "confidence": "high"
    }
  },
  "notes": "Introduces marginal-integral depth (Fraiman-Muniz depth). Year is 2001, not 1991.",
  "curated": true
}
```

---

## `cross_language[*]` Shape

The optional `cross_language` object documents equivalent implementations in other
languages. Keys are `"R"`, `"Python"`, or `"Matlab"`. Each entry:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `package` | string | yes | Package or library name |
| `function` | string | yes | Specific function or method name |
| `version` | string | no | Version against which the mapping was verified; omit if unknown |
| `url` | string | yes | URL pointing to the SPECIFIC function docs, not to the package homepage |
| `confidence` | string enum | yes | `"high"` = personally verified; `"low"` = inferred from docs or README only |

**Locked rule:** Matlab entries default to `confidence: "low"` unless personally
verified. The `"low"` confidence value signals to downstream consumers that the mapping
should not be asserted programmatically.

**Honest gaps:** If a method has no known implementation in a given language, simply
omit that language key from `cross_language`. Do not create placeholder entries with
empty strings.

**URL rule:** The `url` must point to specific function documentation — not to a
package homepage or a repository root. GATE-05 C validates the domain against an
allowlist.

---

## The `curated:false` Tail Convention

For callables known to need a reference but not yet curated, add an entry with
`curated: false`. Empty or null bibliographic fields are acceptable in this state:

```json
{
  "_uncurated_batch_YYYY-MM": {
    "title": "",
    "authors": [],
    "year": null,
    "url": "",
    "type": "journal",
    "callables": [
      "module.some_callable",
      "module.another_callable"
    ],
    "notes": "Pending curation — attribution not yet verified.",
    "curated": false
  }
}
```

**Why this works:** GATE-05 A checks `callable_index` ↔ `papers[*].callables`
consistency regardless of `curated` status. A `curated: false` entry participates in
the consistency check the same as a fully curated entry. The guards do NOT block on
`curated: false` — they only block on internal inconsistency or unresolvable callable
identifiers.

**DOI gate behaviour for `curated: false`:** GATE-05 C skips the DOI regex check for
entries where `curated` is `false`. An empty `doi` field in an uncurated entry does not
cause a test failure.

**Phase 80 note:** The Phase 80 seed contains NO `curated: false` entries — all 5
seed papers were author-verified before commit. This convention is defined here for
Phase 81 onward, where curation of the broader callable surface will use the
`curated: false` sentinel for anti-feature families or callables with contested
attributions, rather than force-citing an unverified paper.

---

## Sub-Method-Keyed Attribution Rule

Attribution is **per sub-method**, not per method family. Do not map one paper key
across an entire family of related callables unless the paper genuinely introduces
all of them.

**Correct:** `depth.band_1d` and `depth.modified_band_1d` both trace to
`lopez_pintado_romo_2009` because López-Pintado & Romo (2009) introduces BOTH band
depth and modified band depth in the same JASA paper. One paper key, two callables.

**Incorrect:** Attributing every depth variant to the same paper because they belong
to the "depth" module family. Band depth ≠ Fraiman-Muniz depth ≠ modal depth.

**Contested or multi-primary attributions:** List co-primary papers in the
`callable_index` value array (a callable may cite more than one paper key). Use `notes`
to explain contested history. Do not force-pick a single paper when the evidence is
genuinely split — flag it in notes and defer a definitive call to Phase 84 human review.

---

## Author-Verification Workflow

An entry may set `curated: true` ONLY after the curator has **personally opened the
DOI landing page** and confirmed:

1. **Author list** — every author name in the `authors` array matches the paper's
   author list, in order, verbatim as printed.
2. **Year** — `year` matches the journal publication date (not a preprint submission
   or online-first date).
3. **Title** — `title` matches the paper's title exactly as printed.

**A resolving DOI is NOT proof of correct attribution.** DOIs can resolve even when
the metadata in `_references_map.json` is wrong (wrong year, wrong author order, wrong
title). Verification means reading the landing page, not checking that the URL loads.

### Canonical worked example: F&M 2001 vs 1991

Fraiman-Muniz depth is frequently mis-cited as 1991 in secondary sources. The correct
attribution is:

- **Correct:** Fraiman, R.; Muniz, G. (2001). "Trimmed means for functional data."
  TEST 10(2), 419–440. DOI: `10.1007/BF02595706`.
- **Wrong:** 1991 is the year of the **Ramsay-Dalzell** paper ("Some tools for
  functional data analysis", JRSS-B, DOI: `10.1111/j.2517-6161.1991.tb01844.x`),
  which introduces FPCA — a completely different method.

Both are landmark FDA papers published one decade apart. The years are confused because
they appear together in review articles and textbooks. The DOI landing pages are
unambiguous. Always verify year against the DOI landing page, not a secondary citation.

### SRSF vs SRV paper pitfall

For elastic alignment and SRSF-based callables (`alignment.karcher_mean`,
`alignment.elastic_align_pair`, `alignment.srsf_transform`), use:

- **Correct:** Srivastava, A.; Wu, W.; Kurtek, S.; Klassen, E.; Marron, J.S. (2011).
  "Registration of functional data using Fisher-Rao metric." arXiv:1103.3817.

- **Wrong:** Srivastava-Klassen-Joshi-Jermyn (2011 IEEE TPAMI, DOI:
  `10.1109/TPAMI.2010.184`). That paper is for the square-root velocity (SRV)
  representation of *curve shapes in Euclidean spaces* — not the SRSF framework for
  *functional data alignment*. The two papers share overlapping authors and both use
  "square root" transforms, but they address different problems.

---

## What the Guards Enforce (GATE-05)

Run the guards with:

```
pytest tests/test_guard_sync_version_independent.py -v
```

All three GATE-05 tests (Group 3) live in `tests/test_guard_sync_version_independent.py`
and run unconditionally on Python 3.9+ (no `mcp` import, no network I/O in CI).

### GATE-05 A — Internal Consistency

**Test:** `test_references_map_internal_consistency`

Asserts the invariant:

```python
frozenset(callable_index.keys()) == frozenset(
    c for p in papers.values() for c in p["callables"]
)
```

Fails if:

- A paper's `callables` list contains a key not present in `callable_index`
  (orphan callable — the paper claims it but the index does not list it).
- `callable_index` contains a key that no paper references
  (phantom index entry — the index lists it but no paper claims it).

**Fix:** Edit both `papers[*].callables` and `callable_index` together in the same
commit. Never update one without the other.

### GATE-05 B — Cross-File Resolution

**Test:** `test_references_map_cross_file_resolution`

Loads both `_references_map.json` and `_capability_map.json` and asserts every key in
`callable_index` resolves to an existing callable in the capability map:

- For `"module.callable"` keys: `cap_data["module"]["callable"]` must exist.
- For `"_Fdata.<method>"` keys: `cap_data["_Fdata"]["<method>"]` must exist.

Fails if a callable in `_references_map.json` was renamed or removed from
`_capability_map.json`. When that happens, update `_references_map.json` to match the
new callable name (or remove the entry if the callable was deleted).

### GATE-05 C — Structural DOI/URL Gate

**Test:** `test_references_map_doi_url_structural_gate`

Runs structural checks with NO live network resolve:

- **DOI regex:** every `doi` field must match `^10\.\d{4,9}/\S+$` (for curated entries
  that carry a DOI).
- **URL well-formedness:** `url` and `cross_language[*].url` must be valid `http`/`https`
  URLs.
- **Domain allowlist:** the URL domain must appear in `_ALLOWED_DOMAINS` (a
  frozenset defined in the test file). Add new legitimate domains to that frozenset
  when curating entries from new publishers.

**`FDARS_ONLINE_CHECKS=1`:** If this environment variable is set to `"1"`, GATE-05 C
calls `pytest.skip()` and exits cleanly. The structural gate is designed to run always
in CI; live DOI resolution is an opt-in offline path that skips the structural gate to
avoid double-running. Do not set `FDARS_ONLINE_CHECKS=1` in CI or during `mkdocs build`.

---

## Common Pitfalls

### Pitfall 1: F&M Year (1991 vs 2001)

The Fraiman-Muniz paper is 2001, not 1991. 1991 is Ramsay-Dalzell. Both are in the
seed file. The years are one decade apart. Always verify against the DOI landing page.

### Pitfall 2: Believing JSON in `python/fdars/` Needs a Maturin Include

Files directly under `python/fdars/` ship in the wheel automatically. Only files in
subdirectories outside the package namespace (e.g. `python/fdars/data/*.csv`) need an
explicit `include` entry in `pyproject.toml`. Do not add `"python/fdars/*.json"` to
`include` — it is already covered.

### Pitfall 3: Splitting Artifact and Guard Tests Across Commits

GATE-04 rule: the JSON file and its guard tests must land in the **same commit**. If
you commit the JSON first and the tests second, CI may run between commits and fail on
a file the tests do not yet know about (or vice versa). Always commit `_references_map.json`
changes and related test changes atomically.

### Pitfall 4: SRSF vs SRV Paper Confusion

Use arXiv:1103.3817 (Srivastava et al. 2011) for SRSF functional-data alignment.
The IEEE TPAMI 2010/2011 paper (same first author) is for curve shapes, not functional
data. See the author-verification section above for the full distinction.

### Pitfall 5: `callable_index` Drift from `papers[*].callables`

The `callable_index` and `papers[*].callables` are intentionally redundant — one
provides the paper-to-callables direction, the other provides the callable-to-papers
direction. Editing only one breaks GATE-05 A. Edit both in every commit that changes
callable assignments.

### Pitfall 6: Same-Paper Entries for BD and MBD

Band depth (`depth.band_1d`) and modified band depth (`depth.modified_band_1d`) are
BOTH introduced in López-Pintado & Romo (2009). Use a single paper key
(`lopez_pintado_romo_2009`) with both callables in the `callables` array. Do not create
two separate paper entries for the same paper.

---

## See Also

- `python/fdars/_references_map.json` — the live file governed by this spec
- `python/fdars/_capability_curation.json` — the identifier space source of truth
  (same `module.callable` / `_Fdata.<method>` key format)
- `python/fdars/_capability_map.json` — the cross-file resolution target for GATE-05 B
- `tests/test_guard_sync_version_independent.py` — Group 3 guard tests (GATE-05 A/B/C)
- Phase 81 — broad curation across all fdars callable families
- Phase 82 — `fdars_method_references` MCP tool handler that loads this file
- Phase 83 — references docs page wired into mkdocs nav
- Phase 84 — whole-site gate + human citation review close
