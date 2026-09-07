---
phase: 80-schema-data-home-primary-guard-tests
verified: 2026-09-07T13:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 80: Schema, Data Home & Primary Guard Tests — Verification Report

**Phase Goal:** The references data home exists with a locked, validated schema and a small verified stub, so all downstream curation/tool/docs work is validated from day one — the schema is never authored free-form.
**Verified:** 2026-09-07T13:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `_references_map.json` loads via importlib.resources from the installed fdars package (SCHEMA-01) | VERIFIED | `.venv/bin/python -c "import importlib.resources as r, json; d=json.loads(r.files('fdars').joinpath('_references_map.json').read_text()); print(sorted(d.keys()), len(d['papers']), 'papers')"` — prints `['callable_index', 'papers'] 5 papers`; no maturin include added (`pyproject.toml` `include` only covers `python/fdars/data/*.csv`) |
| 2 | GATE-05 A passes: callable_index keys == union of papers[*].callables (SCHEMA-03) | VERIFIED | `pytest tests/test_guard_sync_version_independent.py::test_references_map_internal_consistency` — PASSED; frozenset equality confirmed programmatically with 10 keys on each side |
| 3 | GATE-05 B passes: every callable_index key resolves to a real callable in `_capability_map.json`, `_Fdata` special-cased (SCHEMA-03) | VERIFIED | `pytest tests/test_guard_sync_version_independent.py::test_references_map_cross_file_resolution` — PASSED; manual Python check confirms all 10 keys resolve: depth.fraiman_muniz_1d, depth.fraiman_muniz_2d, _Fdata.depth, depth.band_1d, depth.modified_band_1d, alignment.karcher_mean, alignment.elastic_align_pair, alignment.srsf_transform, _Fdata.to_pc, basis.basis_nbasis_cv |
| 4 | Structural DOI/URL gate (GATE-05 C) runs offline in CI with NO live resolve; `FDARS_ONLINE_CHECKS=1` skips it (SCHEMA-04) | VERIFIED | `pytest tests/test_guard_sync_version_independent.py::test_references_map_doi_url_structural_gate` — PASSED; `FDARS_ONLINE_CHECKS=1 pytest ...::test_references_map_doi_url_structural_gate` — 1 skipped; no `urlopen`/`requests`/`socket` in test body confirmed by grep |
| 5 | The stub seeds 3–5 author-verified papers spanning distinct capability families (SCHEMA-01) | VERIFIED | 5 papers: fraiman_muniz_2001 (depth + _Fdata), lopez_pintado_romo_2009 (depth), srivastava_et_al_2011 (alignment), ramsay_dalzell_1991 (_Fdata), eilers_marx_1996 (basis); 4 distinct module families; all `curated: true` |
| 6 | Authoring guide governs curation: paper-level unit, sub-method-keyed callable claims, cross-language shape, curated:false tail convention, DOI-landing-page verification bar (SCHEMA-02) | VERIFIED | `docs/authoring/references-schema.md` exists (449 lines), no exec fences (grep count = 0), contains: `FDARS_ONLINE_CHECKS` (2 hits), `frozenset(callable_index.keys())` (2 hits), `curated` (17 hits), `cross_language` (6 hits), `confidence` (4 hits), F&M-2001-not-1991 example (2 hits), DOI regex `^10\.\d{4,9}/\S+$`, `tests/test_guard_sync_version_independent.py` (4 hits) |

**Score:** 6/6 truths verified (all 5 plan must-haves + SCHEMA-02 from Plan 02 truth)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/_references_map.json` | Paper-keyed `papers` map + flat `callable_index`; 5 curated seed papers | VERIFIED | Exists; 5 papers (fraiman_muniz_2001, lopez_pintado_romo_2009, srivastava_et_al_2011, ramsay_dalzell_1991, eilers_marx_1996); 10 callable_index entries; valid JSON; ships in wheel without maturin include |
| `tests/test_guard_sync_version_independent.py` | Group 3 A/B/C appended; os/re/urllib.parse imports added | VERIFIED | 506 lines total; 3 new test functions at lines 315, 355, 422; imports `os` (line 38), `re` (line 39), `urllib.parse` (line 41); no mcp import at module level; Group 3 header comment at line 307 |
| `docs/authoring/references-schema.md` | Schema spec + author-verification workflow; pure markdown | VERIFIED | Exists; 449 lines; zero exec fences; all 10 mandatory content strings present |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `callable_index` keys | `papers[*].callables` (internal) | frozenset equality — GATE-05 A | WIRED | 10 keys each side; test passes |
| `callable_index` keys | `_capability_map.json` nested paths (cross-file) | module split + dict lookup — GATE-05 B | WIRED | All 10 keys resolve; `_Fdata` top-level key used correctly |
| `_references_map.json` | wheel packaging | `python/fdars/` ships automatically via `python-source = "python"` in pyproject.toml | WIRED | `importlib.resources` load confirmed; no spurious maturin `include` added (only `python/fdars/data/*.csv` is explicitly included) |
| `docs/authoring/references-schema.md` | `python/fdars/_references_map.json` shipped shape | Doc describes actual 5-paper seed, 10 callable_index entries; post-fix matches live JSON | WIRED | Schema doc example shows same 10 keys; `smoothing.gcv_smoother` absent from both |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `_references_map.json` loads via importlib.resources | `.venv/bin/python -c "import importlib.resources as r, json; d=json.loads(r.files('fdars').joinpath('_references_map.json').read_text()); print(sorted(d.keys()), len(d['papers']), 'papers')"` | `['callable_index', 'papers'] 5 papers` | PASS |
| GATE-05 A internal consistency | `pytest tests/test_guard_sync_version_independent.py::test_references_map_internal_consistency -v` | PASSED | PASS |
| GATE-05 B cross-file resolution | `pytest tests/test_guard_sync_version_independent.py::test_references_map_cross_file_resolution -v` | PASSED | PASS |
| GATE-05 C structural DOI/URL gate (offline) | `pytest tests/test_guard_sync_version_independent.py::test_references_map_doi_url_structural_gate -v` | PASSED | PASS |
| FDARS_ONLINE_CHECKS=1 skip | `FDARS_ONLINE_CHECKS=1 pytest tests/test_guard_sync_version_independent.py::test_references_map_doi_url_structural_gate -v` | 1 skipped | PASS |
| Full guard suite (all 8 tests) | `pytest tests/test_guard_sync_version_independent.py -v` | 8 passed in 0.81s | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| SCHEMA-01 | 80-01-PLAN.md | `_references_map.json` committed, paper-keyed, ships via importlib.resources, seeded with 3–5 author-verified papers spanning distinct families | SATISFIED | File exists, loads via importlib.resources, 5 papers, 4 distinct module families, all `curated: true`, correct structure |
| SCHEMA-02 | 80-02-PLAN.md | Documented author-verification workflow + JSON schema doc governing curation | SATISFIED | `docs/authoring/references-schema.md` exists, 449 lines, all mandatory sections confirmed |
| SCHEMA-03 | 80-01-PLAN.md | Primary GATE-05 guard tests (Python 3.9+, no mcp import) pass — A (internal consistency) and B (cross-file resolution) | SATISFIED | Both tests exist, no mcp import at module level, both PASS in pytest run |
| SCHEMA-04 | 80-01-PLAN.md | Offline structural DOI/URL gate runs in CI with no live network resolve; opt-in via `FDARS_ONLINE_CHECKS=1` | SATISFIED | Test passes offline; `FDARS_ONLINE_CHECKS=1` produces 1 skipped; no urlopen/requests/socket in test body |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | — |

No anti-patterns found. No TBD/FIXME/XXX markers. No stub implementations. No hardcoded empty data in production paths.

---

### Additional Verification: F&M Attribution, DOI Integrity, Code Review

**F&M year is 2001, not 1991:** Confirmed. `_references_map.json` has `"year": 2001` for `fraiman_muniz_2001`; the notes field explicitly states "Year is 2001, not 1991." The schema doc reproduces this worked example. `ramsay_dalzell_1991` correctly carries year 1991.

**No fabricated DOIs:** All 4 DOIs present in the file pass the `^10\.\d{4,9}/\S+$` regex. `srivastava_et_al_2011` correctly has NO doi field (arXiv preprint, type = "preprint"). GATE-05 C validates this structurally on every CI run.

**`smoothing.gcv_smoother` correctly absent:** Code review (CR-01) caught an incorrect attribution of `smoothing.gcv_smoother` to the Eilers-Marx P-splines paper; it was removed in commit 6829967. The schema doc example was also updated (3a46732) to show 10 entries (not 11). Both the live JSON and the schema doc example are consistent.

**Code review:** `80-REVIEW.md` reports status `clean` after 3 iterations (0 critical, 0 warning, 0 info findings). The `80-REVIEW-FIX.md` documents 4 findings resolved: CR-01 (wrong gcv_smoother attribution), WR-01 (GATE-05 C url presence check), WR-02 (cross_language required-field validation), WR-01 iter 2 (stale docs example). All fixed before final review.

**GATE-04 atomic commit honored:** Artifact + guard tests landed in a single commit `e7814db` as required. CI cannot observe a state where the JSON exists without tests or vice versa.

**Pyproject.toml:** Only existing `python/fdars/data/*.csv` is explicitly included. No spurious `_references_map.json` maturin include was added — files under `python/fdars/` ship automatically.

---

### Human Verification Required

None. All must-haves are verifiable programmatically. The blocking human citation-accuracy review (GATE-03) is a Phase 84 gate, not a Phase 80 requirement.

---

_Verified: 2026-09-07T13:00:00Z_
_Verifier: Claude (gsd-verifier)_
