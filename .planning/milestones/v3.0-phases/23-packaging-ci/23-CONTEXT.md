# Phase 23: Packaging & CI - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous smart-discuss — extras already added in Phase 20; offline+live tests already exist from Phases 20–21; this phase codifies the matrix + smoke + coverage)

<domain>
## Phase Boundary

The full aspect × provider contract is proven network-free and deterministically, the extras/version matrix is correct across Python 3.9–3.14, and the core provably imports with no provider extra installed.

In scope (REQ-IDs): QUAL-01, QUAL-02, QUAL-03, QUAL-04.

Out of scope: the actual PyPI release / version bump (that's a ship-time action, not a phase); docs-site pages (Phase 24). This phase touches `.github/workflows/ci.yml`, possibly `pyproject.toml` (only if an extra needs a fix), and test scaffolding/CI scripts.
</domain>

<decisions>
## Implementation Decisions

### Grounded in current state

- **QUAL-03 — CI matrix (the main new work).** `.github/workflows/ci.yml`'s `test-python` job currently runs only Python `3.10, 3.12, 3.13` and installs only `maturin numpy pandas pytest` (no provider extras). Expand the matrix to **3.9, 3.10, 3.11, 3.12, 3.13, 3.14** and add correct extra/version gating:
  - On **3.9**: `[gemini]` and `[mcp]` are NOT installable (both require 3.10+); `openai>=1.40,<2.0` IS fine on 3.9. So 3.9 installs the base + `[advisor]` + `[openai]` + `[ollama]` (NOT gemini/mcp) — or relies on the offline mocks. The suite must stay green on 3.9 with mcp/gemini tests skipping cleanly (they already guard on version / importorskip).
  - On **3.10+**: the full `[all-providers]` + `[mcp]` set is installable.
  - Keep the existing Rust job + rustfmt/clippy gates intact.
  - **Reality note:** the live CI matrix only actually runs on GitHub Actions (push/PR). Locally we can validate YAML correctness, the gating logic, and that the offline suite passes under the current interpreter; the true multi-Python run is verified by the CI run itself — call this out rather than claiming local proof.
- **QUAL-04 — bare-venv smoke test.** Add a CI step/job (and a local-runnable script) that creates a FRESH venv, installs ONLY the base package (`maturin develop` / built wheel, NO provider extras, NO `[advisor]`/`[mcp]`), then asserts: `import fdars` works, `from fdars import advisor` works, and an offline `build_diagnostics(...)` call runs — proving the core is importable and functional with zero provider deps. A missing provider extra must raise the actionable ImportError only when a provider is actually requested.
- **QUAL-01 — two-layer offline coverage (mostly already exists).** Phases 20–21 delivered per-adapter fixture tests (`test_advisor_openai/ollama/gemini*.py`, `sys.modules` fakes) and per-aspect determinism tests. This phase CONFIRMS the aspect × provider contract is covered network-free + deterministic (add any missing determinism/cross-coverage assertion; optionally a small test-strategy doc/marker). Do not duplicate what exists.
- **QUAL-02 — env-gated live tests (mostly already exists).** `tests/test_advisor_live_integration.py` has one env-gated live test per provider that skips cleanly. Confirm these skip cleanly with no keys/server and are one-per-provider; extend only if a provider is missing.

### Claude's Discretion

Exact matrix shape (single job with conditional extra install vs a matrix dimension for extra-sets), whether the bare-venv smoke is a separate CI job vs a step, and whether to add a lightweight `tests/test_bare_venv_smoke` marker or a shell script under CI — at Claude's discretion. Keep the existing CI structure/style.
</decisions>

<code_context>
## Existing Code Insights

- `.github/workflows/ci.yml` — `test-rust` (matrix toolchains) + `test-python` (matrix 3.10/3.12/3.13; venv + `pip install maturin numpy pandas pytest` + `maturin develop --release` + `pytest tests/ -v`). Also has rustfmt/clippy gates (see full file).
- `pyproject.toml` extras (Phase 20): `plot`, `dev`, `advisor` (anthropic+pydantic), `mcp` (mcp>=2.0, 3.10+), `openai` (openai>=1.40,<2.0 + pydantic), `gemini` (google-genai>=1.0,<3.0 + pydantic, 3.10+), `ollama` (ollama>=0.6.2 + pydantic), `all-providers` (meta).
- Tests: full suite currently 233 passed, 4 skipped (offline; live + py3.9-guarded skips). Provider adapter tests use `sys.modules` fakes (SDKs not installed in dev venv). `tests/test_advisor_live_integration.py` = 3 env-gated live tests.
- Dev venv is Python 3.14; editable install (`maturin develop`).
- `.publish.yml` (separate workflow) handles PyPI on `vX.Y.Z` tags (fixed earlier this milestone).

## Note on branch
Work has been accumulating on the `release/0.3.0` branch (75+ commits ahead of origin/main). Merge/rename is a ship-time concern, not this phase.
</code_context>

<specifics>
## Specific Ideas

- 3.9 gating: ensure `[gemini]`/`[mcp]` are conditionally skipped in install on 3.9 (e.g. `pip install ... ${{ matrix.python-version != '3.9' && 'fdars[gemini,mcp]' || '' }}` or a conditional step). The test suite already guards gemini/mcp at runtime, so 3.9 should stay green.
- Bare-venv smoke: a distinct job that does NOT install any `[...]` extra, only the built package + numpy/pandas, then runs a 3-line import+build_diagnostics assertion.
- Keep all offline tests network-free; do not add any step that requires an API key or a running Ollama server (live tests stay skip-by-default in CI).
- Validate `ci.yml` YAML parses (e.g. `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"`).

## Reality check (Nyquist)
The multi-Python matrix and extra-gating are only truly exercised by the GitHub Actions run. Verify locally: YAML validity, gating expressions, bare-venv smoke script runs on the local interpreter, and the offline suite is green. Flag the CI-run-dependent parts as verified-on-push, not claimed-locally.
</specifics>

<deferred>
## Deferred Ideas

- The actual PyPI release carrying the provider extras (version bump + tag) → ship-time, after the milestone (the publish workflow is already fixed).
- Docs-site provider setup guide + per-aspect pages → Phase 24.
</deferred>
