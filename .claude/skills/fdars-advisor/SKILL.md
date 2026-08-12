---
name: fdars-advisor
description: >
  Run the fdars functional data analysis advisor workflow: interpret a
  computed result, get grounded parameter recommendations, re-run with
  suggested parameters, and compare before/after diagnostics. Use when
  working with fdars results from any analysis aspect — clustering,
  smoothing, FPCA, alignment, basis/represent, depth, outliers,
  classification, regression, regression CV, or monitoring/SPM — and
  needing grounded diagnostics, parameter guidance, method guidance, or
  a before/after comparison.
  Trigger: whenever the user asks for fdars parameter tuning, smoothing
  basis selection, cluster k guidance, FPCA component count, alignment
  lambda, depth ranking, outlier detection thresholds, classification
  method selection, regression diagnostics, regression CV, or SPM
  monitoring, or wants a grounded before/after diagnostics comparison.
compatibility: >
  Requires Python 3.10+ and pip access. Core install (git-URL until fdars
  3.0 ships extras to PyPI): pip install "fdars @
  git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0
  pydantic>=2.0. For other providers: openai>=1.40.0 (OpenAI/vLLM),
  ollama>=0.6.2 (local/key-free), or google-genai>=1.0 (Gemini). Provider
  extras ([openai], [ollama], [gemini]) publish with fdars 3.0; install
  provider packages manually until then. ANTHROPIC_API_KEY required for
  Anthropic; Ollama runs key-free. Designed for Claude Code and Managed
  Agents environments with allow_package_managers enabled.
allowed-tools: Bash Read
---

## Setup

Install dependencies (run once in the agent's execution environment):

```bash
# Git-URL install (required until fdars 3.0 ships provider extras to PyPI):
pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0
```

For providers other than Anthropic, install the provider package manually:

```bash
# OpenAI or OpenAI-compatible endpoint (vLLM, LM Studio, LocalAI):
pip install openai>=1.40.0

# Local / key-free Ollama:
pip install ollama>=0.6.2

# Gemini:
pip install google-genai>=1.0
```

Once fdars 3.0 is published to PyPI with provider extras:

```bash
# Future one-liner (available when fdars 3.0 ships):
pip install "fdars[mcp,advisor,openai]"   # or [ollama] / [gemini]
```

## Offline Walkthrough (no API key needed)

Run the full interpret->re-run->compare loop against the Canadian Weather
dataset. No network connection is required (dataset is bundled with fdars).

```bash
python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py
```

Expected output: a 4-key deterministic delta block:

```
  Delta (after - before) [4 scalar keys]:
    gcv_aic_approx: -2181.912236
    gcv_bic_approx: -2108.448571
    optimal_gcv: -0.068405
    optimal_edf: +9.853957
```

These numbers are fdars-computed (pspline_fit_gcv, n_basis 15 vs 25).

## Grounded Advice (requires ANTHROPIC_API_KEY)

```bash
ANTHROPIC_API_KEY=sk-... python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py
```

Expected output: interpretation + recommendations with cited diagnostics
evidence + before/after delta block.

## Provider Selection

`advise()` routes through a `Provider` protocol. `advise(provider=, model=)` is
the only entry point for provider selection — the MCP tools are compute-only and
do not call `advise()`.

**Explicit parameters:**

```python
from fdars.advisor import advise
advice = advise(diagnostics, task="interpretation",
                domain_context="...",
                provider="openai",    # "anthropic" | "openai" | "ollama" | "gemini"
                model="gpt-4o")
```

**Environment variables (override defaults when no explicit arg):**

| Variable | Purpose | Example |
|---|---|---|
| `FDARS_ADVISOR_PROVIDER` | Provider name | `anthropic`, `openai`, `ollama`, `gemini` |
| `FDARS_ADVISOR_MODEL` | Model identifier | `claude-opus-4-8`, `gpt-4o`, `llama3.2` |
| `FDARS_ADVISOR_BASE_URL` | Custom API endpoint | `http://localhost:11434` |

**Local / offline path (no API key required):**

```bash
# Start Ollama daemon first: https://ollama.com
ollama pull llama3.2
FDARS_ADVISOR_PROVIDER=ollama FDARS_ADVISOR_MODEL=llama3.2 python my_analysis.py
```

**OpenAI-compatible endpoint (vLLM, LM Studio, LocalAI):**

```bash
FDARS_ADVISOR_PROVIDER=openai \
FDARS_ADVISOR_MODEL=meta-llama/Llama-3-8B-Instruct \
FDARS_ADVISOR_BASE_URL=http://localhost:8000/v1 \
python my_analysis.py
```

## Tools Referenced

This skill orchestrates three MCP tools in `python/fdars/mcp/`:

- `fdars_run_method` — run a supported fdars method (smoothing, clustering,
  FPCA, alignment, basis, depth) and store the result handle.
- `fdars_build_diagnostics` — build offline diagnostics from a stored result
  handle; accepts all 12 analysis aspects (clustering, smoothing, FPCA,
  alignment, basis, represent, depth, outliers, classification, regression,
  regression_cv, spm).
- `fdars_compare_run` — re-run with changed parameters and compute the
  before/after delta; all numbers are fdars-computed.

`python/fdars/advisor/` provides `build_diagnostics` (offline, no LLM) and
`advise()` (LLM interpretation) — the grounding source for all recommendations.

## Grounding Invariant

Every recommendation cites a diagnostics value computed by fdars (via
`build_diagnostics`). The LLM (`advise()`) never fabricates numbers; it
only interprets and reasons over the diagnostics dict. This invariant is
enforced by the Pydantic `Recommendation.evidence` schema (non-empty list
required) and the system prompt's explicit no-fabrication constraint.
