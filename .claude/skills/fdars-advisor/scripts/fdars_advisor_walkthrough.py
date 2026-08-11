"""fdars advisor skill — interpret->recommend->re-run->compare walkthrough.

Demonstrates the full advisor workflow against the Canadian Weather dataset
using the ``fdars.mcp`` helpers directly (no live MCP transport required).

Steps:

  1. Load the Canadian Weather dataset (35 stations × 365 daily observations)
     and store it in the handle registry.
  2. Run the ``smoothing`` method (``pspline_fit_gcv``) with n_basis=15 to
     obtain a "before" result handle.
  3. Build deterministic diagnostics (offline, no API key).
  4. (Optional, API-key-gated) Call ``advise()`` for grounded LLM recommendations.
  5. Compare: re-run smoothing with n_basis=25 via ``compare_run`` and print
     the observable delta — every scalar key where after − before is finite.

Run offline (no API key; requires Python >=3.10):

    python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py

Run with LLM advice (requires ANTHROPIC_API_KEY):

    ANTHROPIC_API_KEY=sk-... python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py

The script exits 0 on Python >=3.10 and prints a skip notice + exits 0 on
Python 3.9 (import-safe; the ``[mcp]`` extra requires >=3.10).
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Python version guard — mcp requires >=3.10; exit 0 gracefully on 3.9
# (MUST precede any 'from fdars.mcp import ...' line — Pitfall 4)
# ---------------------------------------------------------------------------

if sys.version_info < (3, 10):
    print(
        "Python 3.10+ required for fdars[mcp] (mcp>=2.0.0 does not support 3.9).\n"
        "This script will be skipped. "
        "Upgrade to Python 3.10+ and re-run:\n"
        "    pip install 'fdars @ git+https://github.com/sipemu/pyfda' mcp>=2.0.0\n"
        "    python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py"
    )
    sys.exit(0)

import numpy as np

from fdars import datasets
from fdars.advisor import build_diagnostics
from fdars.mcp._compare import compare_run
from fdars.mcp._registry import registry
from fdars.mcp._runner import run_method


def main() -> None:
    """Run the fdars advisor walkthrough end-to-end.

    Loads Canadian Weather, runs smoothing (n_basis=15), builds diagnostics,
    optionally calls advise() when ANTHROPIC_API_KEY is set, then compares
    against n_basis=25 and prints the before/after delta block.
    """
    # Pitfall 7: clear the singleton registry so repeated in-process runs
    # do not accumulate stale handles from prior invocations.
    registry.clear()

    # ---------------------------------------------------------------------------
    # Step 1: Load Canadian Weather and register in the handle registry
    # ---------------------------------------------------------------------------

    print("Step 1: Loading Canadian Weather dataset...")
    ds = datasets.load_canadian_weather()

    # ds.data is an Fdata object (35 stations × 365 daily observations)
    X = np.asarray(ds.data.data, dtype=float)    # shape (35, 365)
    day = np.asarray(ds.argvals, dtype=float)    # shape (365,) — day-of-year grid

    print(f"  {X.shape[0]} weather stations, {X.shape[1]} daily temperature points")

    dataset_id = registry.store_dataset(X, day)
    print(f"  Registered dataset: {dataset_id}")

    # ---------------------------------------------------------------------------
    # Step 2: Run smoothing (n_basis=15) to get the "before" result handle
    # ---------------------------------------------------------------------------

    print("\nStep 2: Running smoothing (pspline_fit_gcv, n_basis=15)...")
    before_result = run_method(dataset_id, "smoothing", n_basis=15)
    before_result_id = registry.store_result(before_result)
    print(f"  Before result handle: {before_result_id}")
    print(f"  GCV (before): {before_result.get('gcv', 'n/a'):.6f}")
    print(f"  EDF (before): {before_result.get('edf', 'n/a'):.4f}")

    # ---------------------------------------------------------------------------
    # Step 3: Build deterministic diagnostics (offline, no API key needed)
    # ---------------------------------------------------------------------------

    print("\nStep 3: Building diagnostics...")
    diagnostics = build_diagnostics(before_result, "smoothing")
    print(f"  Diagnostics keys: {list(diagnostics.keys())}")

    # ---------------------------------------------------------------------------
    # Step 4: (Optional) Grounded LLM advice — gated on ANTHROPIC_API_KEY
    # ---------------------------------------------------------------------------

    if os.environ.get("ANTHROPIC_API_KEY"):
        from fdars.advisor import advise

        print("\nStep 4: Calling advise() for grounded parameter recommendations...")
        advice = advise(
            diagnostics,
            task="parameter",
            domain_context="35 Canadian weather stations, daily temperature curves",
        )
        print(f"  Interpretation: {advice.interpretation}")
        print(f"  Recommendations ({len(advice.recommendations)}):")
        for rec in advice.recommendations:
            print(f"    - [{rec.kind}] {rec.action}")
            for ev in rec.evidence:
                print(f"        evidence: {ev}")
        if advice.caveats:
            print(f"  Caveats: {advice.caveats}")
    else:
        print("\nStep 4: [offline] ANTHROPIC_API_KEY not set — skipping advise()")

    # ---------------------------------------------------------------------------
    # Step 5: Compare — re-run with n_basis=25 and print the delta
    # (always runs; deterministic; no API key required)
    # ---------------------------------------------------------------------------

    print("\nStep 5: Comparing with n_basis=25 (more basis functions)...")
    compare_result = compare_run(
        dataset_id,
        "smoothing",
        before_result_id,
        {"n_basis": 25},
    )

    after_result_id = compare_result["after_result_id"]
    print(f"  After result handle: {after_result_id}")

    delta = compare_result["delta"]
    print(f"\n  Delta (after - before) [{len(delta)} scalar keys]:")
    if delta:
        for k, v in delta.items():
            sign = "+" if v >= 0 else ""
            print(f"    {k}: {sign}{v:.6f}")
    else:
        print("    (no scalar finite keys in common)")

    print("\nWalkthrough complete — all numbers computed deterministically by fdars.")
    print("No fabrication: every delta value is fdars-computed.")


if __name__ == "__main__":
    main()
