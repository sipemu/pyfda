---
name: fdars-advisor
description: >
  Run the fdars functional data analysis advisor workflow: interpret a
  computed result, get grounded parameter recommendations, re-run with
  suggested parameters, and compare before/after diagnostics. Use when
  working with fdars clustering, smoothing, FPCA, alignment, or basis
  results and needing parameter guidance or a before/after comparison.
  Trigger: whenever the user asks for fdars parameter tuning, smoothing
  basis selection, cluster k guidance, FPCA component count, alignment
  lambda, or wants a grounded before/after diagnostics comparison.
compatibility: >
  Requires Python 3.10+ and pip access to install fdars and mcp>=2.0.0.
  Install: pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0
  anthropic>=0.72.0 pydantic>=2.0 (git-URL install required until fdars 0.3.0
  ships the [mcp,advisor] extras to PyPI). Optional: ANTHROPIC_API_KEY for
  grounded LLM advice step. Designed for Claude Code and Managed Agents
  environments with allow_package_managers enabled.
allowed-tools: Bash Read
---

## Setup

Install dependencies (run once in the agent's execution environment):

```bash
# Current workaround — fdars[mcp] and fdars[advisor] extras are not yet
# published on PyPI 0.2.0; install from git + extras separately:
pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0
```

Once fdars 0.3.0+ is published to PyPI with the `[mcp,advisor]` extras:

```bash
# Future one-liner (available when fdars 0.3.0 ships):
pip install "fdars[mcp,advisor]"
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

## Tools Referenced

This skill orchestrates the Phase 12 MCP tools built in `python/fdars/mcp/`:

- `fdars_run_method` — run a supported fdars method (smoothing, clustering,
  FPCA, alignment, basis) and store the result handle.
- `fdars_compare_run` — re-run with changed parameters and compute the
  before/after delta; all numbers are fdars-computed.

The Phase 11 advisor (`python/fdars/advisor.py`) provides `build_diagnostics`
and `advise()`: the grounding source for all LLM recommendations.

## Grounding Invariant

Every recommendation cites a diagnostics value computed by fdars (via
`build_diagnostics`). The LLM (`advise()`) never fabricates numbers; it
only interprets and reasons over the diagnostics dict. This invariant is
enforced by the Pydantic `Recommendation.evidence` schema (non-empty list
required) and the system prompt's explicit no-fabrication constraint.
