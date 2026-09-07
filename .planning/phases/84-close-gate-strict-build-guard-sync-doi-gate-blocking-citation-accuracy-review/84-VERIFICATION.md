---
phase: 84-close-gate-strict-build-guard-sync-doi-gate-blocking-citation-accuracy-review
verified: 2026-09-07
status: human_needed
score: 3/4 gates automated-green; GATE-03 requires human sign-off (by design)
requirements: [GATE-01, GATE-02, GATE-03, GATE-04]
---

# Phase 84 Verification — Close Gate

**Status: `human_needed`** — all automated gates are green; the milestone stops here for the BLOCKING HUMAN citation-accuracy review (GATE-03) and the irreversible publish handoff (GATE-04), exactly as the standing decision requires ("autonomous execution stops at this gate").

## Automated gates — GREEN

### GATE-01 — whole-site strict build ✓
- `PYTHONPATH=scripts mkdocs build --strict` → **exit 0**, built in 1392.88 s (~23 min), OFFLINE.
- `docs/references.md` rendered: `site/references/index.html` (200 KB).
- Fence-error gate `scripts/check_docs_figures.py site` → **"OK: no failed figure blocks in site"** (executed fences emit `FDARS_FENCE_OK`).
- `maturin develop` refreshed the compiled extension against current source before the build.

### GATE-02 — GATE-05 groups + DOI gate + coverage ✓
- `pytest tests/test_guard_sync_version_independent.py -q` → **12 passed**: primary A/B (Py3.9+), companion C/D (Py3.10+), coverage-fraction, anti-feature-absence, and the offline structural DOI/URL gate.
- Coverage reported: **28/437** callables curated (437 = 409 public-module callables + 28 `_Fdata` class methods; derived from `_capability_map.json`, never hardcoded).

### GATE-04 (automated half) — grounding + LLM-free boundary ✓
- `pytest -k "guard_sync or references or mcp or grounding or llm_free or capabilit"` → **168 passed, 0 failed**.
- MCP LLM-free boundary intact: `fdars_method_references` returns no `provider`/`model` keys, imports no advisor/provider module (AST-guarded); `NO_CURATED_ENTRY` sentinel for absent keys.
- Grounding invariant intact (advisor grounding guard + references guards green).

## Human gate — REQUIRED before close (autonomous STOPS here)

### GATE-03 — BLOCKING human citation-accuracy review
A human (NOT an LLM) must verify a sample of curated entries against their DOI landing pages: authors/year/title match, sub-method attribution correct, cross-language pointers resolve.

**Primary review target — the 6 `curated:true` papers (these ship AUTHORITATIVELY via the MCP tool / references page / llms.txt):**
1. `fraiman_muniz_2001` — Fraiman & Muniz, "Trimmed means for functional data" (2001), doi:10.1007/BF02595706 → `depth.fraiman_muniz_1d/2d`, `_Fdata.depth`. (Confirm 2001, NOT 1991.)
2. `lopez_pintado_romo_2009` — López-Pintado & Romo, "On the concept of depth for functional data" (2009), doi:10.1198/jasa.2009.0108 → `depth.band_1d`, `depth.modified_band_1d`. (Confirm band vs modified-band both trace here.)
3. `srivastava_et_al_2011` — Srivastava, Wu, Kurtek, Klassen, Marron, "Registration of functional data using Fisher-Rao metric" (2011), arXiv:1103.3817 (no DOI) → 10 alignment/SRSF callables. (Confirm this arXiv paper, NOT the TPAMI SRV/shape paper.)
4. `ramsay_dalzell_1991` — Ramsay & Dalzell, "Some tools for functional data analysis" (1991), doi:10.1111/j.2517-6161.1991.tb01844.x → `_Fdata.to_pc`, FLM regression callables.
5. `eilers_marx_1996` — Eilers & Marx, "Flexible smoothing with B-splines and penalties" (1996), doi:10.1214/ss/1038425655 → 7 basis/smoothing callables. (Confirm `smoothing.gcv_smoother` is NOT here — it was correctly removed in Phase 80 review.)
6. `cuturi_blondel_2017` — Cuturi & Blondel, "Soft-DTW: a differentiable loss function for time-series" (2017), PMLR (no DOI) → `metric.soft_dtw_self_1d/cross_1d` (the plain loss only; the *divergence* is correctly attributed to Blondel et al. 2021).

**Secondary — the human MAY promote `curated:false` candidates to `curated:true` after opening their DOI landing pages** (this is the only sanctioned promotion point; ~48 named papers currently `curated:false` pending human verification because an autonomous agent cannot personally open a landing page). High-value candidates include: `arribas_gil_romo_2014` (outliergram, doi:10.1093/biostatistics/kxu006 — the Phase-81-review corrected attribution), `sun_genton_2011` (functional boxplot), `narisetty_nair_2016`, `cuevas_febrero_fraiman_2007`, `ramsay_silverman_2005`, `dai_genton_2019`, `febrero_galeano_gonzalez_2008`.

### GATE-04 (publish half) — version tick + irreversible publish handoff
- Package is dual-pinned at **0.11.0** (`pyproject.toml` + `Cargo.toml`); v12.0 shipped as pkg 0.11.0 / tag v0.11.0.
- A REVERSIBLE version tick (e.g. 0.11.0 → 0.12.0) MAY be committed at the human's discretion; the IRREVERSIBLE publish (git tag `vX.Y.Z` → PyPI, and the milestone tag `v13.0`) is NOT executed autonomously and is handed off.

## Editorial reconciliation for the human to accept
- The PROJECT/REQUIREMENTS/ROADMAP text says "N/409"; the honest shipped denominator is **437** (= 409 public + 28 `_Fdata`). The emitter/tool/docs all derive 437; the requirement text should be reconciled to state `N/437 total (409 public + 28 Fdata methods)`.

## Resume after human approval
Once GATE-03 is signed off (and any promotions/version tick committed): run `/gsd-audit-milestone` → `/gsd-complete-milestone v13.0` → `/gsd-cleanup`, then push the release tag if publishing.
