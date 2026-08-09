"""Offline and integration tests for fdars.advisor.

Offline tests (TestBuildDiagnosticsOffline) require no network, no anthropic
package, and no ANTHROPIC_API_KEY. They exercise build_diagnostics and the
offline escape hatches of describe_cluster_differences.

Integration tests (TestAdvisorIntegration) require ANTHROPIC_API_KEY to be
set and the anthropic+pydantic packages installed. They are skipped in CI.
"""

import os

import numpy as np
import pytest


class TestBuildDiagnosticsOffline:
    """Offline tests — no LLM, no network, no anthropic required."""

    def test_clustering_offline_with_synthetic(self):
        from fdars.advisor import build_diagnostics

        result = {
            "centers": [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]],
            "cluster": [0, 0, 1, 1],
            "k": 2,
        }
        diag = build_diagnostics(result, method="clustering")
        assert diag["method"] == "clustering"
        assert diag["k"] == 2
        assert diag["cluster_sizes"] == [2, 2]
