# Phase 83: Docs, llms.txt & Skill Extension — Research

**Researched:** 2026-09-07
**Domain:** Offline docs-emit (Python), mkdocs nav, MCP skill extension
**Confidence:** HIGH (all findings sourced directly from codebase reads this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Docs + `llms.txt` emit OFFLINE from the committed JSON — the `--references` path, like the existing `--llmstxt` path, reads `_references_map.json` directly and does NOT import `fdars` (so it works without a compiled install and under CI/build).
- The skill's hybrid curated/ungrounded fallback lives ONLY in the skill (the MCP tool stays LLM-free per Phase 82); the `grounded: bool` flag is machine-readable per citation, never presenting synthesized provenance as curated. Do NOT duplicate the `fdars-advisor` boundary.
- Coverage is partial-but-honest; uncurated methods are absent from curated output; the "synthesize but flag ungrounded" note is explicit.
- The Coverage line in `docs/references.md` and the `llms.txt` provenance section MUST use the DERIVED real denominator (**N/437**, computed from the live `_capability_map.json`), NOT the stale "409" that appears verbatim in the DOCS-01/DOCS-02 requirement text. Authoring-time value is 28/437. Do NOT hardcode.
- The WHOLE-SITE `mkdocs build --strict` (~25 min, executed fences) is the Phase-84 close gate. This phase must ensure `docs/references.md` is nav-wired and renders cleanly (a targeted/offline strict check of the page + nav validity is sufficient here).

### Claude's Discretion

- The exact family-grouping and visual layout of `docs/references.md` (headings per family, the per-method paper + cross-language table/list shape), guided by the existing `ai-capability-map.md` style and the `_references_map.json` structure.
- The precise `llms.txt` provenance line format (within the DOCS-02 template) and the skill walkthrough's concrete example callables (pick one curated hit e.g. `depth.fraiman_muniz_1d`, and one uncurated/all-false or sentinel e.g. `clustering.align_cluster_fd` or `explain.shap_values`).
- How skill "tests" are expressed (matching the existing `fdars-capabilities` skill's test convention).

### Deferred Ideas (OUT OF SCOPE)

- Whole-site `mkdocs build --strict` (~25 min) + guard-sync + DOI gate close + BLOCKING human citation-accuracy review — Phase 84.
- Completing the uncurated N/437 tail + a coverage floor — REF-FUT-01.
</user_constraints>

---

## Summary

Phase 83 makes the Phase-81 provenance surface public and consumable via three coordinated deliverables: a new `--references` offline emitter in `scripts/generate_capability_dataset.py`, an extension to the existing `_emit_llmstxt` helper with a provenance section, and a `## Scientific Provenance Protocol` section added to `.claude/skills/fdars-capabilities/SKILL.md`.

The data source is `python/fdars/_references_map.json` (57 papers, 243 `callable_index` entries, 28/437 callables with a `curated:true` backing paper — all numbers verified by reading the live JSON this session). The denominator 437 comes from `_capability_map.json` (the same JSON the MCP tool counts; verified this session). The stale "409" figure that appears in the DOCS-01/DOCS-02 requirement text in the ROADMAP is incorrect and must NOT be used anywhere.

The family grouping for `docs/references.md` is by module: the `callable_index` already indexes every entry as `module.callable`, and the `papers` map stores a `callables` list that gives the natural module grouping. Using the module key as the section heading is consistent with `ai-capability-map.md` and requires no additional lookup table. Sentinel papers (keys starting with `_uncurated`) are excluded from the emitted page — they exist only in the JSON for internal tracking. The `llms.txt` provenance section appends to the existing `_emit_llmstxt` output and stays offline (no `fdars` import; reads only the committed JSON files).

**Primary recommendation:** Mirror the `--llmstxt` dispatch pattern exactly: add `elif "--references" in sys.argv: emit_references(repo_root)` at the `__main__` block, implement `emit_references()` analogously to `emit_docs()`, and call two new helpers `_emit_references_page` and `_extend_llmstxt_provenance`. Wire the single nav entry between `AI Capability Map` and `scikit-learn API` in `mkdocs.yml`.

---

## Source-of-Truth File Inventory (all read this session)

| File | Key Facts Verified |
|------|--------------------|
| `scripts/generate_capability_dataset.py` | `--llmstxt` dispatch at line 502; `emit_docs()` at line 472; `_emit_llmstxt` lines 311-388; `_emit_ai_capability_map` lines 391-469; NO `fdars` import in emit path |
| `python/fdars/_references_map.json` | 57 papers, 243 `callable_index` entries; `curated:true` on exactly 6 paper keys; 28 callables backed by a `curated:true` paper |
| `python/fdars/_capability_map.json` | 437 total callables (sum over all module entries including `_Fdata`) |
| `mkdocs.yml` lines 82-221 | Nav: `AI Capability Map: ai-capability-map.md` at line 169; immediately followed by `scikit-learn API:` at line 170; the AI Advisor section ends at line 168 |
| `.claude/skills/fdars-capabilities/SKILL.md` | 97 lines; existing sections: Capability Map, Module Overview, How to Find a Method, Skill Boundary, Optional Extras; no existing Scientific Provenance section |
| `python/fdars/mcp/server.py` lines 838-1044 | `fdars_method_references` return contract: hit with `curated:True`, hit with `curated:False`, `NO_CURATED_ENTRY` sentinel, `AMBIGUOUS_CALLABLE` sentinel |
| `tests/test_capability_accuracy.py` | Test structure: `test_capability_map_no_drift`, `test_capability_map_all_importable`; uses plain pytest, no mcp import at module level |
| `tests/test_guard_sync_version_independent.py` | `test_references_tool_llm_free_boundary` at line 719 exercises `fdars_method_references("depth.fraiman_muniz_1d")` (curated hit) and `fdars_method_references("explain.shap_values")` (NO_CURATED_ENTRY sentinel) |
| `docs/ai-capability-map.md` | Style: H1 title, intro paragraph with callout counts, Module Index table, Module Details H3 per module |

---

## Design 1: `--references` Emitter

### 1.1 Dispatch Addition

In `scripts/generate_capability_dataset.py`, the `__main__` block (lines 500-513) currently has:

```python
if "--llmstxt" in sys.argv:
    emit_docs(repo_root)
else:
    dataset = generate_capability_dataset()
    ...
```

Change to a chain of `if`/`elif`/`else`:

```python
if "--llmstxt" in sys.argv:
    emit_docs(repo_root)
elif "--references" in sys.argv:
    emit_references(repo_root)
else:
    dataset = generate_capability_dataset()
    ...
```

[VERIFIED: scripts/generate_capability_dataset.py:500-513]

### 1.2 `emit_references(repo_root)` Sketch

Mirrors `emit_docs()` exactly in structure. Reads `_references_map.json` AND `_capability_map.json` (for the denominator). No `fdars` import.

```python
def emit_references(repo_root: Path) -> None:
    """Read committed JSON artifacts and emit docs/references.md.

    Offline path: does NOT import fdars.  Mirrors emit_docs() structure.
    """
    ref_path = repo_root / "python" / "fdars" / "_references_map.json"
    cap_path = repo_root / "python" / "fdars" / "_capability_map.json"
    if not ref_path.exists():
        print(f"ERROR: references map not found at {ref_path}", file=sys.stderr)
        sys.exit(1)
    if not cap_path.exists():
        print(f"ERROR: capability map not found at {cap_path}", file=sys.stderr)
        sys.exit(1)

    with open(ref_path, encoding="utf-8") as f:
        ref_data: dict = json.load(f)
    with open(cap_path, encoding="utf-8") as f:
        cap_data: dict = json.load(f)

    refs_path = _emit_references_page(ref_data, cap_data, repo_root)
    llmstxt_path = _extend_llmstxt_provenance(ref_data, cap_data, repo_root)

    print(f"Written {refs_path}")
    print(f"Extended {llmstxt_path} with provenance section")
```

### 1.3 Coverage Derivation (MUST NOT be hardcoded)

Exactly mirrors the MCP tool's derivation (verified in `server.py` lines 1032-1040):

```python
# Denominator: total callables in _capability_map.json
denominator = sum(len(v) for v in cap_data.values())

# Numerator: callable_index entries backed by at least one curated:true paper
papers_map = ref_data.get("papers", {})
callable_index = ref_data.get("callable_index", {})
curated_paper_keys = frozenset(
    pk for pk, p in papers_map.items() if p.get("curated", False) is True
)
numerator = sum(
    1 for _, pks in callable_index.items()
    if any(pk in curated_paper_keys for pk in pks)
)
coverage_str = f"{numerator}/{denominator}"  # e.g. "28/437"
```

[VERIFIED: python/fdars/mcp/server.py:1032-1040]

### 1.4 Family Grouping Strategy

Use the **module name** (first component of `callable_index` keys) as the family/section heading. This requires no auxiliary lookup table — the index already encodes it.

Algorithm:

1. Iterate `papers_map` in sorted key order.
2. Skip any paper key starting with `_uncurated` (these are internal sentinel placeholders; they have empty `title`/`authors` and `curated:false`).
3. For each non-sentinel paper, derive its primary module from `paper["callables"][0].split(".")[0]`.
4. Group papers by primary module, maintaining paper key sort order within each group.
5. Sort groups by module name alphabetically (consistent with `ai-capability-map.md` style).

**Result at authoring time (2026-09-07):** 19 module families with at least one non-sentinel paper:
`_Fdata`, `alignment`, `basis`, `classification`, `clustering`, `density_fda`, `depth`, `famm`, `fdata`, `frechet`, `fts`, `inference`, `metric`, `outliers`, `pace_fpca`, `regression`, `shapelet`, `smoothing`, `spm`

[VERIFIED: by running the grouping logic against the live JSON this session]

### 1.5 `_emit_references_page` Output Structure

```
docs/references.md
```

Page layout:

```markdown
# fdars Scientific References

> Curated primary paper references for fdars functional data analysis methods.
> Generated offline from `python/fdars/_references_map.json`.
> **{N}/{T} callables** have curated entries (authoring: {coverage_str}).
> Uncurated callables are absent; see the [AI Capability Map](ai-capability-map.md)
> for the full callable surface.

## Coverage

**{N} of {T} public callables** have at least one curated primary-paper entry.
Remaining callables have contested attribution, no single primary paper,
or are pending Phase-84 human DOI-landing-page verification.
See [AI Capability Map](ai-capability-map.md) for all {T} callables.

## Methods by Module

### `fdars.{module}` — {module_summary}

#### {Paper: Authors (Year) — Title}

| Field | Value |
|-------|-------|
| Authors | {joined author list} |
| Year | {year} |
| DOI | `{doi}` |
| URL | [{shortened-url}]({url}) |
| Type | {journal/book/preprint/conference} |
| Status | Curated / Pending DOI verification |

**Callables implementing this method:**
- `{module.callable}` — {purpose from capability_map}

**Cross-language implementations:**
| Language | Package | Function | Confidence |
|----------|---------|----------|------------|
| R | `{package}` | `{package::function}` | {confidence} |
| Python | `{package}` | `{package.function}` | {confidence} |
| Matlab | `{package}` | `{function}` | {confidence} |

---
```

**Notes on layout choices (Claude's Discretion):**
- Each paper gets its own H4 under the module H3, not a flat table — this matches the citation-heavy nature of the content and avoids a table row that would need to hold multi-line author lists.
- The purpose for each callable is looked up from `cap_data[module][callable_name]["purpose"]` — this requires a defensive `get()` since `_Fdata` callables use `cap_data["_Fdata"]` as the key (note the underscore prefix matches the map structure).
- Cross-language implementations are omitted entirely when the paper has an empty `cross_language` dict — honest gap, not a placeholder row.
- The Coverage section is computed at emit time, never hardcoded.
- `_Fdata` papers (e.g., `ramsay_dalzell_1991` which covers `_Fdata.to_pc`) appear under a `## Fdata Class Methods` section (not a module heading, since `_Fdata` is the OOP container, not a submodule).

### 1.6 Callable Purpose Lookup

When rendering `Callables implementing this method`, look up purpose from `cap_data`:

```python
def _callable_purpose(callable_key: str, cap_data: dict) -> str:
    """Look up purpose for a callable key from capability map."""
    if "." not in callable_key:
        return ""
    module, fn = callable_key.split(".", 1)
    # _Fdata methods live under cap_data["_Fdata"]
    mod_data = cap_data.get(module, {})
    entry = mod_data.get(fn, {})
    return entry.get("purpose", "")
```

---

## Design 2: `llms.txt` Provenance Section

### 2.1 Where It Appends

The existing `_emit_llmstxt` function (lines 311-388) writes a complete file ending with a blank line after the last module section. The new `_extend_llmstxt_provenance` helper is called from `emit_references()` and APPENDS to the existing `docs/llms.txt` file — it does NOT regenerate the whole file. Alternatively (cleaner), `_emit_llmstxt` can be extended to accept the optional `ref_data` and `cap_data` arguments and include the section inline, with the caller defaulting to `None` for the existing `emit_docs()` path. The inline approach is preferred to avoid two-pass writes.

**Recommended:** Add an optional `ref_data` / `cap_data` parameter pair to `_emit_llmstxt`. When both are present, append the provenance section. When absent (the `--llmstxt` path from `emit_docs()`), omit it — keeping backward compatibility.

```python
def _emit_llmstxt(
    data: dict,
    repo_root: Path,
    ref_data: dict | None = None,
    cap_data: dict | None = None,
) -> Path:
    ...
    # existing section logic unchanged ...

    # Provenance section — only when ref_data/cap_data provided
    if ref_data is not None and cap_data is not None:
        lines.extend(_provenance_section_lines(ref_data, cap_data))

    content = "\n".join(lines)
    out_path.write_text(content, encoding="utf-8")
    return out_path
```

### 2.2 Provenance Section Template

Section heading and per-entry format for the `## Scientific Provenance & Cross-Language Implementations` block:

```
## Scientific Provenance & Cross-Language Implementations

Coverage: {N} of {T} public callables have curated primary-paper entries.
Uncurated callables are absent from this section. A consumer MAY synthesize
provenance for uncurated callables but MUST flag each synthesized citation as
ungrounded (grounded: false) — never present synthesized provenance as curated.

### {fdars.module}

- `{module.callable}` — {Authors} ({Year}) doi:{doi} ; R: {pkg}::{fn} / Python: {pkg}.{fn}
```

**Per-entry line format (exact):**

```
- `depth.fraiman_muniz_1d` — Fraiman, R., Muniz, G. (2001) doi:10.1007/BF02595706 ; R: fda.usc::depth.FM / Python: scikit-fda.fraiman_muniz_depth
```

Rules:
- If a callable has multiple papers, emit one line per paper, each starting with the callable name.
- If `doi` is empty, omit `doi:` entirely — do not emit `doi:`.
- Cross-language implementations: emit only languages present in `cross_language`; use ` / ` separator between languages. If no cross-language entries exist, omit the ` ;` part entirely.
- Emit only callables in `callable_index` whose backing paper has `curated:true` on at least one paper — this is the same predicate used for the coverage numerator.
- Sentinel papers (`_uncurated*` keys) never appear in this section.

**Uncurated note (verbatim, end of section):**

```
> Uncurated callables ({T - N} of {T}) are absent from this section.
> A consumer MAY synthesize provenance for these callables but MUST structurally
> flag each synthesized citation as ungrounded: { "grounded": false } per citation.
> Never present synthesized provenance as curated data from this file.
```

### 2.3 Offline Guarantee

`_emit_llmstxt` and `_provenance_section_lines` must NOT contain any `import fdars` call. They read only `data` (capability map dict) and optionally `ref_data`/`cap_data` (references map dict) — both passed in as already-loaded dicts from the caller who opened the JSON files. This mirrors the existing pattern precisely.

[VERIFIED: scripts/generate_capability_dataset.py:311-388 — `_emit_llmstxt` has no `import fdars` statement anywhere in its body]

---

## Design 3: mkdocs.yml Nav Wiring

### 3.1 Exact Edit

Insert one nav entry between `AI Capability Map: ai-capability-map.md` (line 169) and `scikit-learn API:` (line 170):

**Before (lines 169-170):**
```yaml
  - AI Capability Map: ai-capability-map.md
  - scikit-learn API:
```

**After:**
```yaml
  - AI Capability Map: ai-capability-map.md
  - Scientific References: references.md
  - scikit-learn API:
```

[VERIFIED: mkdocs.yml:169-170]

**Indentation:** Two-space indent, matching `  - AI Capability Map: ai-capability-map.md` exactly. The nav is a flat top-level list at this point (not a sub-list), so no additional nesting is needed.

### 3.2 mkdocs Strict Gotchas to Avoid

1. **Broken nav entry:** The nav entry `Scientific References: references.md` will cause `mkdocs build --strict` to fail with `Config value 'nav': The following pages exist in the docs directory, but are not included in the nav: ...` if the file does not exist at `docs/references.md`, OR with `The following pages exist in the nav, but not in the docs directory: ...` if the nav entry exists before the file is written. Both tasks (write file, add nav entry) must be in the same wave.

2. **Broken internal links in the page:** Any `[text](relative-link.md)` in `docs/references.md` that points to a non-existent file will fail `--strict`. The recommended `[AI Capability Map](ai-capability-map.md)` link is safe (that file exists). The recommended `[Reference](reference/index.md)` is safe. Do NOT add links to module reference pages that do not exist in the nav/docs directory.

3. **MkDocs `md_in_html` extension:** The generated page uses only standard Markdown (headers, tables, bullet lists). No HTML blocks. No risk of `md_in_html` issues.

4. **Anchor conflicts:** The `{#anchor}` syntax (used in `ai-capability-map.md` for Module Details) is from the `attr_list` extension. If the References page uses it, verify `attr_list` is in `mkdocs.yml`'s `markdown_extensions`. Recommendation: avoid `{#anchor}` anchors in `references.md` to sidestep any extension dependency — use plain H3 headings (MkDocs auto-generates anchors from heading text).

### 3.3 Lightweight Local Validation (Phase 83 scope)

Do NOT run the full `mkdocs build --strict` (25-min, executed fences) — that is Phase 84's gate.

Sufficient checks for Phase 83:

```bash
# 1. Confirm the page parses as valid Markdown (no syntax errors)
python3 -c "
import pathlib, re
text = pathlib.Path('docs/references.md').read_text()
# Minimal: check no unclosed code fences
fences = re.findall(r'^```', text, re.M)
print(f'Code fence markers: {len(fences)} (should be even)')
assert len(fences) % 2 == 0, 'Unclosed code fence detected'
print('Markdown fence check: OK')
"

# 2. Confirm the nav entry resolves to an existing file
python3 -c "
import pathlib
assert pathlib.Path('docs/references.md').exists(), 'docs/references.md not found'
print('docs/references.md exists: OK')
"

# 3. Targeted offline strict check (fast — no fence execution)
# This validates nav + file existence + internal links without running code fences
DOCS_FAST=1 mkdocs build --strict --no-directory-urls -d /tmp/mkdocs-phase83-check 2>&1 | grep -E 'ERROR|WARNING|references' | head -20
```

The `DOCS_FAST=1` env var (already used in the project's docs build workflow, per `docs-diagram-verify-workflow.md` memory) suppresses `markdown-exec` code fence execution, making the build fast. This is sufficient to catch nav/link errors without the 25-min fence runtime.

---

## Design 4: Skill Extension — Scientific Provenance Protocol

### 4.1 Where to Insert

Append a new `## Scientific Provenance Protocol` section to `.claude/skills/fdars-capabilities/SKILL.md` after the existing `## Skill Boundary` section (line 82-89) and before `## Optional Extras` (line 91). This preserves the existing structure and keeps provenance logically adjacent to the boundary section.

[VERIFIED: .claude/skills/fdars-capabilities/SKILL.md:82-97]

### 4.2 Decision Tree (Hybrid Protocol)

```markdown
## Scientific Provenance Protocol

When asked about the paper origins, citations, or cross-language implementations
of an fdars method, use this protocol:

### Step 1: Look up via `fdars_method_references`

```bash
# MCP tool (Python 3.10+, fdars[mcp] installed):
# fdars_method_references("depth.fraiman_muniz_1d")
#
# Offline (any Python 3.9+):
# python -c "
# import json, importlib.resources as r
# ref = json.loads(r.files('fdars').joinpath('_references_map.json').read_text())
# idx = ref['callable_index'].get('depth.fraiman_muniz_1d', [])
# print(idx)
# "
#
# Docs page: https://sipemu.github.io/pyfda/references/
# llms.txt provenance section: https://sipemu.github.io/pyfda/llms.txt
```

### Step 2: Route by return value

**Path A — `curated: True` hit:**
The return includes `"curated": True` and at least one paper with `"curated": True`.
- Use the paper data verbatim: authors, year, DOI, cross-language implementations.
- Present as: "According to fdars curated provenance: [Authors] ([Year]), [Title]. doi:[DOI]"
- Do NOT paraphrase, embellish, or add citations not in the return payload.

**Path B — `curated: False` hit (all backing papers have `curated: False`):**
The callable is indexed but all papers pending DOI verification.
- State the candidate paper(s) from the return payload WITH the caveat that they are
  pending Phase-84 human DOI-landing-page verification.
- Present as: "Candidate reference (pending verification): [Authors] ([Year]), [Title]."
- Attach `grounded: false` to each citation in any structured output you produce.
- Do NOT present as confirmed curated provenance.

**Path C — `NO_CURATED_ENTRY` sentinel:**
The callable exists in fdars but has no entry in `callable_index`.
- You MAY synthesize a candidate reference from your training knowledge.
- You MUST flag every synthesized citation structurally:
  `{ "grounded": false, "source": "synthesis", "review_required": true }`
- State explicitly: "No curated entry exists for [callable]. The following is synthesized
  and ungrounded — treat as a starting point for manual verification only."
- Never omit the `grounded: false` flag in structured output.
- Never present synthesized provenance as matching the curated surface.

**Non-duplication with `fdars-advisor`:**
This provenance protocol covers citation lookup and cross-language implementation pointers.
For parameter tuning, method selection diagnostics, and before/after comparisons,
use the `fdars-advisor` skill — do not route those queries here.
```

### 4.3 Both-Path Walkthrough

**Walkthrough A — Curated Hit: `depth.fraiman_muniz_1d`**

```
User: What paper is depth.fraiman_muniz_1d based on?

Step 1: call fdars_method_references("depth.fraiman_muniz_1d")

Return:
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
        "R": {"package": "fda.usc", "function": "depth.FM", "confidence": "high"},
        "Python": {"package": "scikit-fda", "function": "fraiman_muniz_depth", "confidence": "high"}
      },
      "curated": True
    }
  ],
  "coverage": "28/437",
  "version": "..."
}

Step 2: curated: True → Path A
Response: "According to fdars curated provenance: Fraiman, R. and Muniz, G. (2001),
'Trimmed means for functional data'. doi:10.1007/BF02595706.
Cross-language: R fda.usc::depth.FM (high confidence), Python scikit-fda.fraiman_muniz_depth (high confidence)."
```

**Walkthrough B — NO_CURATED_ENTRY Sentinel: `explain.shap_values`**

(Confirmed by `test_references_tool_llm_free_boundary` in `tests/test_guard_sync_version_independent.py` line 765, which uses `explain.shap_values` as the miss example.)

```
User: What paper is explain.shap_values based on?

Step 1: call fdars_method_references("explain.shap_values")

Return:
{
  "method": "explain.shap_values",
  "curated": False,
  "sentinel": "NO_CURATED_ENTRY",
  "message": "No curated reference entry for 'explain.shap_values'. ...",
  "version": "..."
}

Step 2: NO_CURATED_ENTRY sentinel → Path C
Response: "No curated entry exists for explain.shap_values in the fdars provenance
surface. The following is synthesized from training knowledge and ungrounded:
{ 'grounded': false, 'source': 'synthesis', 'review_required': true,
  'candidate': 'Lundberg & Lee (2017), A Unified Approach to Interpreting Model Predictions' }
Treat this as a starting point for manual verification only — it has NOT been
confirmed against fdars-core source code or DOI landing pages."
```

**Walkthrough C — `curated: False` hit (all papers pending): `clustering.align_cluster_fd`**

The `_uncurated_align_cluster_fd_2026-09` paper entry has `curated: false`. The callable_index entry is `"clustering.align_cluster_fd": ["_uncurated_align_cluster_fd_2026-09"]`.

```
User: What paper backs clustering.align_cluster_fd?

Step 1: call fdars_method_references("clustering.align_cluster_fd")

Return:
{
  "method": "clustering.align_cluster_fd",
  "curated": False,
  "papers": [
    {
      "paper_key": "_uncurated_align_cluster_fd_2026-09",
      "title": "",
      "authors": [],
      "year": null,
      "curated": False,
      ...
    }
  ],
  "coverage": "28/437",
  "version": "..."
}

Step 2: curated: False (all papers curated:false) → Path B
Response: "clustering.align_cluster_fd has a candidate attribution (contested — no single
curated primary paper confirmed): the SRSF/Karcher-mean elastic clustering framework
(Srivastava et al. 2011) is a primary candidate, but attribution is contested and pending
Phase-84 human verification. { 'grounded': false } — do not treat as confirmed curated provenance."
```

### 4.4 Skill Test Convention

The existing `fdars-capabilities` skill has no formal test file. The existing guard tests in `tests/test_guard_sync_version_independent.py` test the MCP tool directly. For SKILL-02, follow the same pattern as `test_capability_accuracy.py`:

Add a new test file `tests/test_references_skill_boundary.py` with two tests:

1. **`test_references_curated_hit_returns_curated_true`** (Python 3.10+ guard): calls `fdars_method_references("depth.fraiman_muniz_1d")` and asserts `result["curated"] is True` and `result["papers"][0]["curated"] is True`. This exercises Path A.

2. **`test_references_sentinel_returns_no_curated_entry`** (Python 3.10+ guard): calls `fdars_method_references("explain.shap_values")` and asserts `result["curated"] is False` and `result["sentinel"] == "NO_CURATED_ENTRY"`. This exercises Path C.

Both tests use the same `pytest.importorskip("mcp")` guard pattern as existing MCP tests (avoids failing on Python 3.9 where `mcp` is unavailable).

```python
# tests/test_references_skill_boundary.py
import pytest

@pytest.mark.skipif(
    condition=False,  # replaced by importorskip below
    reason="placeholder"
)
def test_placeholder(): pass  # not used

def test_references_curated_hit_returns_curated_true():
    """SKILL-02 Path A: curated hit returns curated:True."""
    mcp_mod = pytest.importorskip("mcp", reason="mcp not installed (Python 3.9)")
    from fdars.mcp.server import fdars_method_references
    result = fdars_method_references("depth.fraiman_muniz_1d")
    assert result["curated"] is True, "Expected curated:True for fraiman_muniz_1d"
    assert len(result["papers"]) >= 1
    assert any(p["curated"] for p in result["papers"])

def test_references_sentinel_returns_no_curated_entry():
    """SKILL-02 Path C: NO_CURATED_ENTRY sentinel for uncatalogued callable."""
    pytest.importorskip("mcp", reason="mcp not installed (Python 3.9)")
    from fdars.mcp.server import fdars_method_references
    result = fdars_method_references("explain.shap_values")
    assert result["curated"] is False
    assert result.get("sentinel") == "NO_CURATED_ENTRY"
```

[VERIFIED: test pattern mirrors `tests/test_guard_sync_version_independent.py:741-766` which uses the same pair of callables]

---

## Architecture Patterns

### Script Dispatch Pattern (existing, confirmed)

```
scripts/generate_capability_dataset.py
  __main__
    if "--llmstxt" in sys.argv  → emit_docs(repo_root)
    elif "--references" in sys.argv  → emit_references(repo_root)   ← NEW
    else  → generate_capability_dataset() + write JSON
```

### Offline Emit Pattern (existing, confirmed)

```
emit_references(repo_root)
  ├── open _references_map.json   (NO fdars import)
  ├── open _capability_map.json   (NO fdars import)
  ├── _emit_references_page(ref_data, cap_data, repo_root) → docs/references.md
  └── _emit_llmstxt(cap_data, repo_root, ref_data, cap_data) → docs/llms.txt (extended)
```

Both helpers receive pre-loaded dicts — no file I/O inside them beyond the final `out_path.write_text(...)`.

---

## Common Pitfalls

### Pitfall 1: Stale "409" Denominator

**What goes wrong:** Using the hardcoded string "409" from the DOCS-01/DOCS-02 requirement text anywhere in the emitted docs. The capability map now has 437 callables.
**Why it happens:** The requirement text was written when the count was 409; it was not updated as new modules were added.
**How to avoid:** NEVER hardcode 437 either. Always derive: `sum(len(v) for v in cap_data.values())`.
**Warning signs:** Any `"409"` or `"437"` literal in the Python source of `generate_capability_dataset.py`.

[VERIFIED: current cap map sum = 437, verified by Python computation this session]

### Pitfall 2: Accidentally Importing `fdars` in the Emitter

**What goes wrong:** CI docs build fails with `ImportError` or `ModuleNotFoundError` because the compiled Rust extension (`fdars._native`) is not present in the docs build environment.
**Why it happens:** Adding a bare `import fdars` at module level or inside a helper function that is called from the offline emit path.
**How to avoid:** The existing lazy-import pattern in `generate_capability_dataset.py` (see module docstring lines 53-55) makes `import fdars` appear only inside `generate_capability_dataset()` and `_build_fdata_entry()` — both guarded by the `else:` branch. Helpers in the `--llmstxt`/`--references` branch must never call these functions.
**Warning signs:** `import fdars` not inside a function that is exclusively reachable via the `else:` (live-introspection) branch.

[VERIFIED: scripts/generate_capability_dataset.py:53-55 — the `_emit_llmstxt` function has zero `fdars` references; all fdars imports are inside `generate_capability_dataset()` and `_build_fdata_entry()` only]

### Pitfall 3: mkdocs Strict Link/Nav Breakage

**What goes wrong:** `mkdocs build --strict` fails with `ERROR - Config value 'nav': The page 'references.md' is listed in the nav, but does not exist in the docs directory.`
**Why it happens:** Nav entry added before the file is generated, or the file is generated to the wrong path.
**How to avoid:** Tasks that add the nav entry and generate the file must be in the same wave (or the file-generation task runs first). The output path MUST be `docs/references.md` (relative to repo root), not `docs/reference/references.md` or any subdirectory.
**Warning signs:** Nav entry and file-write in separate waves with no dependency enforcement.

### Pitfall 4: Skill Presenting Synthesized Provenance as Curated

**What goes wrong:** An agent following the skill returns a synthesized citation for an uncurated callable without the `grounded: false` flag, making the consumer believe it is curated fdars data.
**Why it happens:** The skill's Path C fallback omits the explicit `grounded: false` structured flag, or uses prose-only hedging ("I think this is based on...") that a downstream system cannot parse.
**How to avoid:** Path C MUST include `{ "grounded": false, "source": "synthesis", "review_required": true }` as a machine-readable structure in the response. Prose hedging is in addition to, not instead of, this flag.
**Warning signs:** A synthesized citation appearing in structured JSON output without a `grounded` key.

### Pitfall 5: Family Grouping Inconsistent with References Map Structure

**What goes wrong:** The emitter groups papers by a computed "family" that diverges from the `callable_index` module prefix — e.g., grouping `spm.mfpca` under `multi_fdata` because `happ_greven_2018` also covers `multi_fdata.PyMultiFunData`.
**Why it happens:** The `callables` list in a paper spans multiple modules (cross-module papers). Using the first callable's module as the primary module, and using the paper's `callables` list to list all callables under that section, cleanly handles this: `happ_greven_2018` is listed under `spm` (first callable is `spm.mfpca`), and the callables list `["spm.mfpca", "multi_fdata.PyMultiFunData", "multi_fdata.multi_fdata_from_components"]` shows all three.
**How to avoid:** Do NOT attempt to split a multi-module paper into multiple sections. List it once under its primary module (first callable's module) and enumerate all callables in the paper's `callables` list.
**Warning signs:** The same paper key appearing in two different module sections.

### Pitfall 6: Sentinel Papers Appearing in Emitted Output

**What goes wrong:** Papers with keys starting `_uncurated*` appear in `docs/references.md` or the `llms.txt` provenance section, displaying empty titles and null years.
**Why it happens:** The emitter iterates `papers_map` without filtering out sentinel keys.
**How to avoid:** In all emit loops: `if paper_key.startswith("_uncurated"): continue`.
**Warning signs:** Any section in the emitted page with an empty heading or null year.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Coverage fraction | Custom counter | Mirror `server.py:1032-1040` exactly — same derivation as MCP tool |
| Family grouping | External lookup table | Module prefix from `callable_index` keys — already encoded |
| Nav integration | Manual HTML | Single `mkdocs.yml` nav entry — mkdocs handles the rest |
| Provenance lookup | Regex over docstrings | `fdars_method_references` MCP tool — it's already LLM-free and does exactly this |

---

## Data Summary (Verified This Session)

| Metric | Value | Source |
|--------|-------|--------|
| Total callables (denominator) | 437 | `_capability_map.json` sum, computed this session |
| Callable index entries | 243 | `_references_map.json` `callable_index` count |
| Papers in papers map | 57 | `_references_map.json` `papers` count |
| `curated:true` paper keys | 6 | `fraiman_muniz_2001`, `lopez_pintado_romo_2009`, `srivastava_et_al_2011`, `ramsay_dalzell_1991`, `eilers_marx_1996`, `cuturi_blondel_2017` |
| Callables with curated:true backing | 28 | Computed this session against live JSON |
| Coverage string | `28/437` | Derived (NOT hardcoded) |
| Module families with non-sentinel papers | 19 | Computed this session |
| Skill existing section count | 5 | Read SKILL.md this session (97 lines) |
| `explain.shap_values` in callable_index | NO | Confirmed — sentinel path for walkthrough |
| `depth.fraiman_muniz_1d` curated | YES | `curated:true` on `fraiman_muniz_2001` |
| `clustering.align_cluster_fd` curated | NO | Only backing paper is `_uncurated_align_cluster_fd_2026-09` with `curated:false` |

[VERIFIED: python/fdars/_references_map.json:1190-1434 — callable_index read this session]
[VERIFIED: python/fdars/_capability_map.json:1-50 (sample) — full sum computed via Python this session]
[VERIFIED: python/fdars/mcp/server.py:1032-1040 — coverage derivation formula]

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `DOCS_FAST=1` suppresses `markdown-exec` fence execution in this project | Design 3.3 | Lightweight check takes 25 min instead of seconds; fallback: use `--no-strict` for the Phase-83 page-render check |
| A2 | `explain.shap_values` is not in `callable_index` (NO_CURATED_ENTRY path) | Design 4.3 | Walkthrough B demonstrates wrong path; test `test_references_sentinel_returns_no_curated_entry` catches this if wrong |

All other claims in this document are verified by reading the source files this session.

---

## Open Questions

1. **`_emit_llmstxt` extension vs. `_extend_llmstxt_provenance` separate function**
   - What we know: `emit_docs()` currently calls `_emit_llmstxt(data, repo_root)` with no provenance args; the new `emit_references()` also needs llms.txt provenance.
   - What's unclear: Should `--references` also re-emit the full `llms.txt` (with provenance) or only append? Re-emitting the full file is simpler and avoids read-then-modify logic.
   - Recommendation: Make `emit_references()` call `_emit_llmstxt(cap_data, repo_root, ref_data=ref_data, cap_data=cap_data)` — this re-emits the full llms.txt with provenance appended. The planner should document that `--references` must be run after `--llmstxt` if the two are invoked independently (or `--references` always re-emits both).

2. **`_Fdata` section heading in references page**
   - What we know: `_Fdata` papers (e.g., `ramsay_dalzell_1991` covering `_Fdata.to_pc`) would appear under a `_Fdata` module section.
   - What's unclear: Whether `## _Fdata` or `## Fdata Class Methods` is the right heading.
   - Recommendation: Use `## Fdata Class Methods` for readability; use `## fdars.{module}` for all other 18 module families. The emitter checks `if module == "_Fdata"` and uses the human-readable heading.

---

## Sources

### Primary (HIGH confidence — read this session)
- `scripts/generate_capability_dataset.py` — full file read; dispatch, emit helpers, offline pattern confirmed
- `python/fdars/_references_map.json` — full file read (1435 lines); all counts computed
- `python/fdars/_capability_map.json` — sampled + computed total via Python; 437 callables confirmed
- `python/fdars/mcp/server.py:838-1044` — `fdars_method_references` return contract read in full
- `.claude/skills/fdars-capabilities/SKILL.md` — full 97-line file read
- `mkdocs.yml:82-221` — nav structure including AI section at lines 159-169 read
- `docs/ai-capability-map.md:1-80` — style/format reference read
- `docs/llms.txt:1-60` — existing format confirmed
- `tests/test_capability_accuracy.py:1-80` — test structure confirmed
- `tests/test_guard_sync_version_independent.py` — grep confirmed `explain.shap_values` and `depth.fraiman_muniz_1d` as the miss/hit pair in existing tests

---

## RESEARCH COMPLETE
