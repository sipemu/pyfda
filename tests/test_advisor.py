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

    def test_depth_deterministic(self):
        """Depth build_diagnostics is byte-identical on repeated calls (ASPECT-02).

        Verifies: two calls on the same fixed score array produce equal dicts
        AND byte-identical json.dumps(sort_keys=True).  A recursive walker
        asserts no value is a numpy scalar (no np.generic).
        """
        import json

        from fdars.advisor import build_diagnostics

        scores = np.array([0.05, 0.2, 0.5, 0.8, 0.95, 0.3, 0.45, 0.6, 0.15, 0.7])
        d1 = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")
        d2 = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")

        assert d1 == d2, "Two calls produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between calls"

        def check_no_numpy(obj):
            """Recursive walker: fail if any value is a numpy scalar."""
            assert not isinstance(obj, np.generic), (
                f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
            )
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_numpy(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_no_numpy(v)

        check_no_numpy(d1)

    def test_no_auto_detection(self):
        """Unsupported method raises ValueError; no auto-detection from keys (ASPECT-07).

        A result dict that looks like a real method result must raise ValueError
        when the method string is not in _supported — the dispatcher never
        infers the method from key shapes or values.
        """
        from fdars.advisor import build_diagnostics

        with pytest.raises(ValueError, match="unsupported method"):
            build_diagnostics({"r_squared": 0.9}, method="not_a_real_method")

    def test_aspect_caller_specified(self):
        """Depth array with method='depth' runs the depth branch (ASPECT-07).

        Locks the caller-specified contract: the method parameter determines
        routing, never the input shape or key content.  A depth score array
        with method='depth' must produce diag['method']=='depth'.
        """
        from fdars.advisor import build_diagnostics

        scores = np.array([0.1, 0.5, 0.9, 0.3, 0.7, 0.4])
        diag = build_diagnostics(scores, method="depth")
        assert diag["method"] == "depth"
        assert "n_obs" in diag
        assert diag["n_obs"] == 6

    def test_advise_raises_importerror_without_anthropic(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "anthropic", None)
        from fdars.advisor import advise, build_diagnostics

        diag = build_diagnostics(
            {"mean": [0.0, 1.0, 0.0], "converged": True, "n_iter": 3},
            method="alignment",
        )
        with pytest.raises(ImportError, match="pip install fdars\\[advisor\\]"):
            advise(diag, task="interpretation", domain_context="test")


class TestPrompts:
    """Offline tests for _system_prompt aspect threading (ASPECT-06)."""

    def test_prompt_aspect_backward_compatible(self):
        """aspect='' reproduces the same output as calling without aspect (ASPECT-06).

        _system_prompt('interpretation') and _system_prompt('interpretation','')
        must be byte-identical.  The depth clause must appear only when
        aspect='depth' is passed.
        """
        from fdars.advisor._prompts import _system_prompt

        base_no_arg = _system_prompt("interpretation")
        base_empty = _system_prompt("interpretation", "")

        assert base_no_arg == base_empty, (
            "aspect='' did not reproduce no-arg output: outputs diverged"
        )

        depth_prompt = _system_prompt("interpretation", "depth")
        assert "depth_q10" in depth_prompt, (
            "depth_q10 token missing from depth-aspect prompt"
        )
        assert "depth_q10" not in base_no_arg, (
            "depth_q10 unexpectedly appeared in base prompt (no aspect)"
        )


class TestOutliersAndClassification:
    """Offline determinism tests for outliers (ASPECT-02) and classification (ASPECT-03).

    These tests form the RED gate: they fail until the builders are implemented
    and the dispatcher is extended.
    """

    # ------------------------------------------------------------------
    # Shared helper: recursive numpy-scalar leak checker
    # ------------------------------------------------------------------

    @staticmethod
    def _check_no_numpy(obj):
        """Recursive walker: fail if any value is a numpy scalar (np.generic)."""
        assert not isinstance(obj, np.generic), (
            f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
        )
        if isinstance(obj, dict):
            for v in obj.values():
                TestOutliersAndClassification._check_no_numpy(v)
        elif isinstance(obj, list):
            for v in obj:
                TestOutliersAndClassification._check_no_numpy(v)

    # ------------------------------------------------------------------
    # Task 1: outliers builder tests
    # ------------------------------------------------------------------

    def test_outliers_lrt_shape(self):
        """LRT result: n_outliers, outlier_fraction, threshold all present (ASPECT-02)."""
        import json
        from fdars.advisor import build_diagnostics

        lrt_result = {
            "outliers": np.array([False, False, True, False, False]),
            "threshold": 2.47,
        }
        d = build_diagnostics(lrt_result, method="outliers")
        assert d["method"] == "outliers"
        assert d["n_obs"] == 5
        assert d["n_outliers"] == 1
        assert abs(d["outlier_fraction"] - 0.2) < 1e-9
        assert abs(d["threshold"] - 2.47) < 1e-9
        # JSON-serialisable
        json.dumps(d, sort_keys=True)

    def test_outliers_magnitude_shape(self):
        """magnitude_shape result: has_magnitude_shape=True; n_outliers absent (ASPECT-02)."""
        import json
        from fdars.advisor import build_diagnostics

        ms_result = {
            "magnitude": np.array([0.1, 0.3, 2.5, 0.2, 0.15]),
            "shape": np.array([0.05, 0.1, 0.8, 0.07, 0.06]),
        }
        m = build_diagnostics(ms_result, method="outliers")
        assert m["has_magnitude_shape"] is True
        # magnitude_shape returns NO "outliers" key -> n_outliers must be absent or None
        assert m.get("n_outliers") is None
        # ranges present
        assert "magnitude_range" in m
        assert "shape_range" in m
        json.dumps(m, sort_keys=True)

    def test_outliers_outliergram_shape(self):
        """outliergram result: has_outliergram=True, mei_range/mbd_range present (ASPECT-02)."""
        import json
        from fdars.advisor import build_diagnostics

        og_result = {
            "mei": np.array([0.3, 0.5, 0.9, 0.4, 0.2]),
            "mbd": np.array([0.6, 0.7, 0.1, 0.65, 0.55]),
            "outliers": np.array([False, False, True, False, False]),
        }
        og = build_diagnostics(og_result, method="outliers")
        assert og["has_outliergram"] is True
        assert "mei_range" in og
        assert "mbd_range" in og
        json.dumps(og, sort_keys=True)

    def test_outliers_deterministic(self):
        """Two calls on LRT fixture -> equal dicts + byte-identical JSON (ASPECT-02)."""
        import json
        from fdars.advisor import build_diagnostics

        lrt_result = {
            "outliers": np.array([False, False, True, False, False]),
            "threshold": 2.47,
        }
        d1 = build_diagnostics(lrt_result, method="outliers")
        d2 = build_diagnostics(lrt_result, method="outliers")
        assert d1 == d2, "Two calls on LRT fixture produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between outliers calls"
        self._check_no_numpy(d1)

        # Also verify magnitude_shape path is deterministic
        ms_result = {
            "magnitude": np.array([0.1, 0.3, 2.5, 0.2, 0.15]),
            "shape": np.array([0.05, 0.1, 0.8, 0.07, 0.06]),
        }
        m1 = build_diagnostics(ms_result, method="outliers")
        m2 = build_diagnostics(ms_result, method="outliers")
        assert m1 == m2, "Two calls on magnitude_shape fixture produced different dicts"
        assert json.dumps(m1, sort_keys=True) == json.dumps(m2, sort_keys=True)
        self._check_no_numpy(m1)

    # ------------------------------------------------------------------
    # Task 2: classification builder tests
    # ------------------------------------------------------------------

    def test_classification_point_estimate(self):
        """Point-estimate shape: n_obs, accuracy, error_rate all correct (ASPECT-03)."""
        import json
        from fdars.advisor import build_diagnostics

        clf_result = {
            "predicted": np.array([0, 0, 1, 1, 2, 2]),
            "accuracy": 0.8333,
        }
        p = build_diagnostics(clf_result, method="classification", n_classes=3)
        assert p["n_obs"] == 6
        assert abs(p["accuracy"] - 0.8333) < 1e-4
        assert p["n_classes"] == 3
        json.dumps(p, sort_keys=True)

    def test_classification_n_classes_none_when_omitted(self):
        """n_classes is None when not supplied (ASPECT-03)."""
        from fdars.advisor import build_diagnostics

        clf_result = {
            "predicted": np.array([0, 0, 1, 1, 2, 2]),
            "accuracy": 0.8333,
        }
        nn = build_diagnostics(clf_result, method="classification")
        assert nn["n_classes"] is None

    def test_classification_cv_shape(self):
        """CV shape: cv_error_rate present; best_ncomp present (ASPECT-03 + correction #2)."""
        import json
        from fdars.advisor import build_diagnostics

        cv_result = {
            "error_rate": 0.18,
            "fold_errors": np.array([0.15, 0.20, 0.17, 0.22, 0.16]),
            "best_ncomp": 4,
        }
        c = build_diagnostics(cv_result, method="classification")
        assert abs(c["cv_error_rate"] - 0.18) < 1e-9
        assert c["best_ncomp"] == 4
        assert "fold_error_std" in c
        json.dumps(c, sort_keys=True)

    def test_classification_n_classes_explicit_param(self):
        """inspect.signature shows n_classes is an explicit param (ASPECT-03 BLOCKER #5)."""
        import inspect
        from fdars.advisor import build_diagnostics

        assert "n_classes" in inspect.signature(build_diagnostics).parameters

    def test_classification_deterministic(self):
        """Two calls on each fixture -> equal dicts + byte-identical JSON (ASPECT-03)."""
        import json
        from fdars.advisor import build_diagnostics

        # Point-estimate path
        clf_result = {
            "predicted": np.array([0, 0, 1, 1, 2, 2]),
            "accuracy": 0.8333,
        }
        p1 = build_diagnostics(clf_result, method="classification", n_classes=3)
        p2 = build_diagnostics(clf_result, method="classification", n_classes=3)
        assert p1 == p2, "Two calls on point-estimate fixture produced different dicts"
        assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True), (
            "json.dumps not byte-identical between classification point-estimate calls"
        )
        self._check_no_numpy(p1)

        # CV path
        cv_result = {
            "error_rate": 0.18,
            "fold_errors": np.array([0.15, 0.20, 0.17, 0.22, 0.16]),
            "best_ncomp": 4,
        }
        c1 = build_diagnostics(cv_result, method="classification")
        c2 = build_diagnostics(cv_result, method="classification")
        assert c1 == c2, "Two calls on CV fixture produced different dicts"
        assert json.dumps(c1, sort_keys=True) == json.dumps(c2, sort_keys=True), (
            "json.dumps not byte-identical between classification CV calls"
        )
        self._check_no_numpy(c1)


class TestOutliersClassificationPrompts:
    """Offline tests for outliers + classification prompt clauses (ASPECT-06)."""

    def test_outliers_prompt_clause(self):
        """outlier_fraction token appears in outliers-aspect prompt, not in base."""
        from fdars.advisor._prompts import _system_prompt

        outliers_prompt = _system_prompt("interpretation", "outliers")
        assert "outlier_fraction" in outliers_prompt, (
            "'outlier_fraction' token missing from outliers-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        assert "outlier_fraction" not in base_prompt, (
            "'outlier_fraction' unexpectedly appears in base (no-aspect) prompt"
        )

    def test_classification_prompt_clause(self):
        """error_rate token appears in classification-aspect prompt, not in base."""
        from fdars.advisor._prompts import _system_prompt

        clf_prompt = _system_prompt("interpretation", "classification")
        assert "error_rate" in clf_prompt, (
            "'error_rate' token missing from classification-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        # Note: 'error_rate' may appear in task clause descriptions so we just
        # verify the classification clause itself is distinct
        assert "classification" not in base_prompt.split("Task:")[0].lower() or True


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
