---
phase: 82-mcp-tool-fdars-method-references-gate-05-companion
verified: 2026-09-07T18:58:03Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 82: fdars_method_references MCP Tool + GATE-05 Verification Report

**Phase Goal:** The LLM-free `fdars_method_references()` MCP tool ships alongside `fdars_list_capabilities`, returning curated provenance or an explicit uncurated sentinel, with the full GATE-05 three-way mirror enforced in the same commit — the provable LLM-free boundary is closed.

**Verified:** 2026-09-07T18:58:03Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `fdars_method_references('depth.fraiman_muniz_1d')` returns curated:true with papers list, coverage '28/437', and version — no provider/model key (MCP-01, MCP-02, MCP-03) | VERIFIED | Live smoke-check: `HIT OK`; `curated:true`, `coverage:'28/437'`, `provider` and `model` absent; `papers` non-empty with cross_language. Coverage derived live from cap_data at server.py:1032–1040, never hardcoded. |
| 2 | `fdars_method_references('explain.shap_values')` returns curated:false + sentinel 'NO_CURATED_ENTRY' + message + version — never {} and never raises (MCP-02) | VERIFIED | Live smoke-check: `MISS OK`; sentinel `'NO_CURATED_ENTRY'`, `curated:False`, `doi` absent, `message` non-empty, `version` present. |
| 3 | `fdars_method_references('clustering.align_cluster_fd')` (present in callable_index, all papers curated:false) returns curated:false WITH papers and NO sentinel key (MCP-02) | VERIFIED | Live smoke-check: `ALL-CURATED-FALSE HIT OK`; `curated:False`, `sentinel` key absent, `papers` list non-empty. |
| 4 | A bare callable 'fraiman_muniz_1d' suffix-resolves to depth.fraiman_muniz_1d; an unknown 'module.callable' whose module is not in _REFERENCES_MODULES raises ValueError before any JSON load (MCP-01, MCP-03) | VERIFIED | Live smoke-check: bare resolve `b['method'] == 'depth.fraiman_muniz_1d'`; `VALUEERROR OK` with message naming tool (`fdars_method_references`) and bad module (`zzz`). `_Fdata.depth` passes gate without ValueError. |
| 5 | Guard Group 3 companion tests (C)/(D) pass on Python 3.10+ and the full test_guard_sync_version_independent.py suite is green; the tool + guards land in the SAME commit (MCP-04) | VERIFIED | `pytest tests/test_guard_sync_version_independent.py -q`: **12 passed in 1.61s**; both named tests pass individually. Commit `3610b45` contains both `python/fdars/mcp/server.py` and `tests/test_guard_sync_version_independent.py` atomically. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/mcp/server.py` | Contains `fdars_method_references` `@mcp.tool()` + `_REFERENCES_MODULES` alias + updated docstring | VERIFIED | Function at line 843, alias at line 766, docstring bullet at line 27. Handler is ~160 lines, substantive. |
| `tests/test_guard_sync_version_independent.py` | Contains `_EXPECTED_REFERENCES_MODULES`, `test_references_tool_llm_free_boundary`, `test_references_mcp_server_frozenset_matches` | VERIFIED | `_EXPECTED_REFERENCES_MODULES` at line 228, (C) test at line 719, (D) test at line 809. |
| `python/fdars/_references_map.json` | Loaded via importlib.resources by the handler | VERIFIED | File exists (73 KB), 57 papers, 243 callable_index entries. |
| `python/fdars/_capability_map.json` | Loaded to derive coverage denominator | VERIFIED | File exists (77 KB), 437 total callables across all modules. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `fdars_method_references` handler | `_REFERENCES_MODULES` | `if module not in _REFERENCES_MODULES` frozenset gate at server.py:933 — before any JSON load | WIRED | Gate fires on unknown module, raises ValueError with tool name and bad module in message. |
| `_REFERENCES_MODULES` | `_CAPABILITY_MODULES` | `_REFERENCES_MODULES: frozenset[str] = _CAPABILITY_MODULES` alias at server.py:766 | WIRED | Alias (identity), not independent frozenset. Confirmed by `_REFERENCES_MODULES is _CAPABILITY_MODULES` live check. |
| `test_references_mcp_server_frozenset_matches` | `_REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES == _CAPABILITY_MODULES` | Three-way assert at test lines 831–843 | WIRED | Both equality assertions present with symmetric-difference diagnostics in messages. |
| `test_references_tool_llm_free_boundary` | AST-walk of `inspect.getsource(fdars_method_references)` | `ast.walk(tree)` checking `ImportFrom` and `Import` nodes against `forbidden_modules` + `forbidden_fdars_names` | WIRED | WR-01 fix (commit b958fcd) added `from fdars import advisor` catch via `forbidden_fdars_names = {"advisor"}` + `node.module == "fdars"` branch. |
| coverage denominator | `_capability_map.json` at call time | `sum(len(v) for v in cap_data.values())` at server.py:1032 | WIRED | Derives 437 live; docstring example "28/437" is documentation only, not the runtime value. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `fdars_method_references` | `ref_data` | `importlib.resources.files("fdars") / "_references_map.json"` read at call time | Yes — 57 papers, 243 callable_index entries | FLOWING |
| `fdars_method_references` | `cap_data` | `importlib.resources.files("fdars") / "_capability_map.json"` read at call time | Yes — 437 callables across 30 modules | FLOWING |
| `fdars_method_references` | `coverage_str` | Derived: `numerator/denominator` from both JSON files | Yes — emits `"28/437"` | FLOWING |
| `fdars_method_references` | `projected_papers` | Paper projection from `papers_map` filtered by `callable_index` keys | Yes — fields: paper_key, title, authors, year, doi, url, type, cross_language, curated | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Curated hit: `depth.fraiman_muniz_1d` | PYTHONPATH=python .venv/bin/python -c "...HIT OK..." | `HIT OK` — curated:true, coverage:'28/437', provider/model absent, papers non-empty | PASS |
| Sentinel miss: `explain.shap_values` | PYTHONPATH=python .venv/bin/python -c "...MISS OK..." | `MISS OK` — curated:false, sentinel:'NO_CURATED_ENTRY', doi absent, message+version present | PASS |
| All-curated:false hit: `clustering.align_cluster_fd` | PYTHONPATH=python .venv/bin/python -c "...ALL BRANCHES OK" | `ALL-CURATED-FALSE HIT OK` — curated:false, sentinel absent, papers non-empty | PASS |
| Bare callable: `fraiman_muniz_1d` | Same compound check | Resolves to `depth.fraiman_muniz_1d`, curated:true | PASS |
| Unknown module ValueError: `zzz.nope` | Same compound check | Raises ValueError naming tool and module, before JSON load | PASS |
| `_Fdata` special-case: `_Fdata.depth` | Same compound check | Returns dict with version key — no ValueError from frozenset gate | PASS |
| Full guard suite | PYTHONPATH=python .venv/bin/python -m pytest tests/test_guard_sync_version_independent.py -q | 12 passed in 1.61s | PASS |
| Named companion tests | pytest ...::test_references_tool_llm_free_boundary ...::test_references_mcp_server_frozenset_matches -v | 2 passed in 1.39s | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| MCP-01 | 82-01-PLAN.md | `fdars_method_references(method)` synchronous `@mcp.tool()` after `fdars_list_capabilities`; loads JSON via `importlib.resources`; accepts `"module.callable"` or bare callable; no model/provider call | SATISFIED | Decorator at server.py:842; function immediately follows `fdars_list_capabilities` close at server.py:835; lazy imports: `json`, `importlib.resources`, `fdars.__version__` only — no advisor/provider. |
| MCP-02 | 82-01-PLAN.md | Hit returns `{"method","curated","papers","coverage","version"}`; miss returns `{"method","curated":false,"sentinel":"NO_CURATED_ENTRY","message","version"}`; never `{}`; never raises except unknown-module ValueError | SATISFIED | All six return branches verified live. All-curated:false path returns papers with no sentinel (honesty rule: present-but-unverified differs from absent). Coverage emits `28/437` (REQUIREMENTS.md says `N/409` — stale; tool correctly derives 437; Phase 84 to reconcile the text). |
| MCP-03 | 82-01-PLAN.md | `_REFERENCES_MODULES` DERIVED from `_CAPABILITY_MODULES` (alias), frozenset-gated before any JSON load | SATISFIED | `_REFERENCES_MODULES: frozenset[str] = _CAPABILITY_MODULES` at server.py:766; gate at server.py:933 fires before `ref_file.read_text()` at server.py:950. |
| MCP-04 | 82-01-PLAN.md | GATE-05 companion tests (C)/(D) in `tests/test_guard_sync_version_independent.py` in the SAME commit; (C) AST no-import + result-key boundary; (D) three-way frozenset mirror | SATISFIED | Both test functions exist and pass. WR-01 fix (b958fcd) extended (C) to catch `from fdars import advisor` form. Atomic commit `3610b45` contains both files. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| server.py | 874 | `"28/437"` in docstring example | Info | Documentation example only — runtime value is derived at lines 1032–1040. Not a hardcoded stub. |
| server.py | 963–985 | Sentinel responses (`NO_CURATED_ENTRY`, `AMBIGUOUS_CALLABLE`) omit `coverage` field | Info (IN-01, acknowledged by reviewer) | Minor API inconsistency; callers can guard with `.get("coverage")`. Deferred to future cleanup per 82-REVIEW-FIX.md. Explicitly out-of-scope for phase 82. |

No TBD / FIXME / XXX debt markers found in either modified file.

### Gaps Summary

No gaps. All five must-haves verified, all four MCP requirements satisfied, all guards green.

**Coverage denominator note (not a gap):** REQUIREMENTS.md MCP-02 text says `N/409`; the derived denominator from the live `_capability_map.json` is 437. The tool correctly derives 437 at call time. Phase 84 is the designated phase to reconcile the requirement text. This is a known, explicitly-deferred discrepancy noted in SUMMARY.md and confirmed by Phase 81's CURATE-05 guard.

---

_Verified: 2026-09-07T18:58:03Z_
_Verifier: Claude (gsd-verifier)_
