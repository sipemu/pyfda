"""fdars MCP advisor — end-to-end compare recipe.

Demonstrates the full MCP tool workflow (register → run → compare) against
the Canadian Weather dataset, using the ``fdars.mcp`` helpers directly
(no live MCP transport required for the script — transport is only needed
when driving the tools from a language model via stdio).

Steps:

  1. Load the Canadian Weather dataset (35 stations × 365 daily temperature
     curves) and store it in the handle registry.
  2. Run the ``smoothing`` method (``pspline_fit_gcv``) with n_basis=15 to
     get a before result handle.
  3. Compare: re-run smoothing with n_basis=25 via ``compare_run``.
  4. Print the observable ``delta`` — every scalar key where after − before
     is finite; fdars computes every number.

Run (offline — no API key; requires Python >=3.10):

    pip install "fdars[mcp]"
    python examples/mcp_recipe.py

The script exits 0 on Python >=3.10 and prints a skip notice + exits 0 on
Python 3.9 (import-safe everywhere; the ``[mcp]`` extra is 3.10+ only).

No ``ANTHROPIC_API_KEY`` is required.  No network connection is made.
"""

from __future__ import annotations

import sys

# ---------------------------------------------------------------------------
# Python version guard — mcp requires >=3.10; exit 0 gracefully on 3.9
# ---------------------------------------------------------------------------

if sys.version_info < (3, 10):
    print(
        "Python 3.10+ required for fdars[mcp] (mcp>=2.0.0 does not support 3.9).\n"
        "This script will be skipped. "
        "Upgrade to Python 3.10+ and re-run:\n"
        "    pip install 'fdars[mcp]' && python examples/mcp_recipe.py"
    )
    sys.exit(0)

import numpy as np

from fdars import datasets
from fdars.mcp._registry import registry
from fdars.mcp._runner import run_method
from fdars.mcp._compare import compare_run

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
# Step 2: Run smoothing (n_basis=15) to get a before result handle
# ---------------------------------------------------------------------------

print("\nStep 2: Running smoothing (pspline_fit_gcv, n_basis=15)...")
before_result = run_method(dataset_id, "smoothing", n_basis=15)
before_result_id = registry.store_result(before_result)
print(f"  Before result handle: {before_result_id}")
print(f"  GCV (before): {before_result.get('gcv', 'n/a'):.6f}")
print(f"  EDF (before): {before_result.get('edf', 'n/a'):.4f}")

# ---------------------------------------------------------------------------
# Step 3: Compare — re-run with n_basis=25 and compute the delta
# ---------------------------------------------------------------------------

print("\nStep 3: Comparing with n_basis=25 (more basis functions)...")
compare_result = compare_run(
    dataset_id,
    "smoothing",
    before_result_id,
    {"n_basis": 25},
)

after_result_id = compare_result["after_result_id"]
print(f"  After result handle: {after_result_id}")

# ---------------------------------------------------------------------------
# Step 4: Print the observable delta — fdars-computed, no LLM required
# ---------------------------------------------------------------------------

print("\nStep 4: Observable before/after/delta\n")
print("  Before diagnostics (n_basis=15):")
for k, v in compare_result["before"].items():
    if v is not None and not isinstance(v, list):
        print(f"    {k}: {v}")

print("\n  After diagnostics (n_basis=25):")
for k, v in compare_result["after"].items():
    if v is not None and not isinstance(v, list):
        print(f"    {k}: {v}")

delta = compare_result["delta"]
print(f"\n  Delta (after - before) [{len(delta)} scalar keys]:")
if delta:
    for k, v in delta.items():
        sign = "+" if v >= 0 else ""
        print(f"    {k}: {sign}{v:.6f}")
else:
    print("    (no scalar finite keys in common)")

print("\nRecipe complete — all numbers computed deterministically by fdars.")
print("No ANTHROPIC_API_KEY was required.  No network connection was made.")
