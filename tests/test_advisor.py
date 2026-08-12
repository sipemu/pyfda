"""Offline and integration tests for fdars.advisor.

Offline tests (TestBuildDiagnosticsOffline) require no network, no anthropic
package, and no ANTHROPIC_API_KEY. They exercise build_diagnostics and the
offline escape hatches of describe_cluster_differences.

Integration tests (TestAdvisorIntegration) require ANTHROPIC_API_KEY to be
set and the anthropic+pydantic packages installed. They are skipped in CI.
"""

import os
import sys

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

    def test_clustering_with_real_dataset(self):
        from fdars import clustering, datasets
        from fdars.advisor import build_diagnostics

        ds = datasets.load_canadian_weather()
        X = np.asarray(ds.data.data, dtype=float)
        day = np.asarray(ds.argvals, dtype=float)
        result = clustering.kmeans_fd(X, day, k=4, seed=42)
        diag = build_diagnostics(result, method="clustering", argvals=day)
        assert diag["method"] == "clustering"
        assert diag["k"] == 4
        assert len(diag["cluster_sizes"]) == 4
        assert diag["pairwise_amplitude_distance"] is not None

    def test_build_diagnostics_deterministic(self):
        from fdars.advisor import build_diagnostics

        result = {
            "n_basis_values": [5, 8, 10],
            "gcv": [0.5, 0.3, 0.4],
            "edf": [3.0, 5.0, 7.0],
        }
        d1 = build_diagnostics(result, method="basis")
        d2 = build_diagnostics(result, method="basis")
        assert d1 == d2

    def test_depth_build_diagnostics_basic(self):
        """RED gate: depth branch must exist in build_diagnostics (Task 1)."""
        import json

        from fdars.advisor import build_diagnostics

        scores = np.array([0.05, 0.2, 0.5, 0.8, 0.95, 0.3, 0.45, 0.6, 0.15, 0.7])
        diag = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")
        assert diag["method"] == "depth"
        assert diag["n_obs"] == 10
        assert diag["method_name"] == "fraiman_muniz"
        assert abs(diag["depth_min"] - 0.05) < 1e-9
        assert sum(diag["depth_histogram"]) == 10
        # JSON-serialisable
        json.dumps(diag, sort_keys=True)

    def test_advise_raises_importerror_without_anthropic(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "anthropic", None)
        from fdars.advisor import advise, build_diagnostics

        diag = build_diagnostics(
            {"mean": [0.0, 1.0, 0.0], "converged": True, "n_iter": 3},
            method="alignment",
        )
        with pytest.raises(ImportError, match="pip install fdars\\[advisor\\]"):
            advise(diag, task="interpretation", domain_context="test")


class TestAdvisorIntegration:
    """LLM integration tests — skipped in CI without ANTHROPIC_API_KEY."""

    pytestmark = pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set — skipping LLM integration test",
    )

    def test_advise_returns_advice_schema(self):
        pytest.importorskip("anthropic")
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice, advise, build_diagnostics

        result = {"n_basis_values": [5, 8, 10], "gcv": [0.5, 0.3, 0.4]}
        diag = build_diagnostics(result, method="basis")
        advice = advise(diag, task="parameter", domain_context="NIR spectroscopy")
        assert isinstance(advice, Advice)
        assert isinstance(advice.interpretation, str)
        assert isinstance(advice.recommendations, list)
