"""fdars AI advisor — end-to-end recipe.

Demonstrates the complete advisor workflow against the Canadian Weather dataset:

  1. Load a real dataset (35 Canadian weather stations, daily temperature curves).
  2. Cluster the temperature curves into 4 groups with ``kmeans_fd``.
  3. Build offline diagnostics with ``build_diagnostics`` — deterministic, no network.
  4. Optionally get a grounded LLM interpretation (requires ``ANTHROPIC_API_KEY``).

Run (offline — no API key required):

    pip install fdars
    python examples/advisor_recipe.py

Run with LLM interpretation (requires Anthropic API key):

    pip install fdars[advisor]
    ANTHROPIC_API_KEY=sk-ant-... python examples/advisor_recipe.py

The script exits 0 in both cases. When the key is absent the LLM step is
skipped and the offline diagnostics are printed instead.
"""

from __future__ import annotations

import os

import numpy as np

import fdars
from fdars import clustering, datasets
from fdars.advisor import build_diagnostics, describe_cluster_differences

# ---------------------------------------------------------------------------
# Step 1: Load the Canadian Weather dataset
# ---------------------------------------------------------------------------

print("Loading Canadian Weather dataset...")
ds = datasets.load_canadian_weather()

# ds.data is an Fdata object (35 stations × 365 daily observations)
X = np.asarray(ds.data.data, dtype=float)   # shape (35, 365)
day = np.asarray(ds.argvals, dtype=float)    # shape (365,) — day-of-year grid

print(f"  {X.shape[0]} weather stations, {X.shape[1]} daily temperature points")

# ---------------------------------------------------------------------------
# Step 2: Cluster — 4 climate-region groups via functional k-means
# ---------------------------------------------------------------------------

print("\nClustering into 4 groups with kmeans_fd (seed=42)...")
result = clustering.kmeans_fd(X, day, k=4, seed=42)

print(f"  Cluster assignments: {result['cluster'].tolist()}")
print(f"  Converged: {result.get('converged', 'n/a')}")

# ---------------------------------------------------------------------------
# Step 3: Build offline diagnostics — deterministic, no API key needed
# ---------------------------------------------------------------------------

print("\nBuilding cluster diagnostics (offline)...")
diag = build_diagnostics(result, method="clustering", argvals=day)

print(f"  k (clusters): {diag['k']}")
print(f"  Cluster sizes: {diag['cluster_sizes']}")
print(f"  Mean amplitude separation: {diag['mean_amplitude_separation']:.4f}")
print(f"  Mean phase separation:     {diag['mean_phase_separation']:.4f}")

# ---------------------------------------------------------------------------
# Step 4: Optional LLM interpretation — guarded by ANTHROPIC_API_KEY
# ---------------------------------------------------------------------------

if os.environ.get("ANTHROPIC_API_KEY"):
    print("\nANTHROPIC_API_KEY found — requesting grounded LLM interpretation...")
    advice = describe_cluster_differences(
        result,
        argvals=day,
        domain_context=(
            "35 Canadian weather stations clustered by daily temperature curve. "
            "4 climate regions expected: Arctic, Atlantic, Continental, Pacific."
        ),
        run_llm=True,
    )
    print("\n--- Advisor interpretation ---")
    print(advice.interpretation)
    print("\n--- Recommendations ---")
    for rec in advice.recommendations:
        print(f"[{rec.kind}] {rec.action}")
        if rec.evidence:
            for ev in rec.evidence:
                print(f"       evidence: {ev}")
else:
    print(
        "\nANTHROPIC_API_KEY is not set — LLM interpretation step skipped."
        "\nOffline diagnostics are available in the `diag` dict printed above."
        "\nTo get grounded LLM advice, set the key and re-run:"
        "\n    ANTHROPIC_API_KEY=sk-ant-... python examples/advisor_recipe.py"
    )
