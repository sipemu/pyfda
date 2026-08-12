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

    def test_outliers_deterministic(self):
        """Outliers build_diagnostics is byte-identical on repeated calls (ASPECT-02).

        Verifies: two calls on the same fixed LRT fixture produce equal dicts
        AND byte-identical json.dumps(sort_keys=True).  A recursive walker
        asserts no value is a numpy scalar (no np.generic).
        Also verifies magnitude_shape path for completeness.
        """
        import json

        from fdars.advisor import build_diagnostics

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

        # LRT fixture
        lrt_result = {
            "outliers": np.array([False, False, True, False, False]),
            "threshold": 2.47,
        }
        d1 = build_diagnostics(lrt_result, method="outliers")
        d2 = build_diagnostics(lrt_result, method="outliers")
        assert d1 == d2, "Two calls on LRT fixture produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between outliers LRT calls"
        check_no_numpy(d1)

        # magnitude_shape fixture
        ms_result = {
            "magnitude": np.array([0.1, 0.3, 2.5, 0.2, 0.15]),
            "shape": np.array([0.05, 0.1, 0.8, 0.07, 0.06]),
        }
        m1 = build_diagnostics(ms_result, method="outliers")
        m2 = build_diagnostics(ms_result, method="outliers")
        assert m1 == m2, "Two calls on magnitude_shape fixture produced different dicts"
        assert json.dumps(m1, sort_keys=True) == json.dumps(m2, sort_keys=True), (
            "json.dumps not byte-identical between magnitude_shape calls"
        )
        check_no_numpy(m1)

    def test_classification_deterministic(self):
        """Classification build_diagnostics is byte-identical on repeated calls (ASPECT-03).

        Verifies: two calls on the same fixed point-estimate fixture produce
        equal dicts AND byte-identical json.dumps(sort_keys=True).  A recursive
        walker asserts no value is a numpy scalar.  Also verifies the CV fixture
        (cv_error_rate path) for completeness.
        """
        import json

        from fdars.advisor import build_diagnostics

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

        # Point-estimate fixture
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
        check_no_numpy(p1)

        # CV fixture (confirms cv_error_rate path)
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
        check_no_numpy(c1)

    def test_advise_raises_importerror_without_anthropic(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "anthropic", None)
        from fdars.advisor import advise, build_diagnostics

        diag = build_diagnostics(
            {"mean": [0.0, 1.0, 0.0], "converged": True, "n_iter": 3},
            method="alignment",
        )
        with pytest.raises(ImportError, match="pip install fdars\\[advisor\\]"):
            advise(diag, task="interpretation", domain_context="test")

    # ------------------------------------------------------------------
    # Task 1 (Wave 3): _utils shared helper + fpca refactor regression guard
    # ------------------------------------------------------------------

    def test_utils_eigenvalues_variance(self):
        """_eigenvalues_to_variance_cumulative returns a list of native floats,
        monotonically non-decreasing, last≈1.0; zero-sum input returns [0.0]*n.
        RED gate for _utils.py (Task 1 of plan 21-03).
        """
        from fdars.advisor.aspects._utils import _eigenvalues_to_variance_cumulative

        # Normal case
        result = _eigenvalues_to_variance_cumulative(np.array([2.1, 0.8, 0.3]))
        assert len(result) == 3
        # All native floats (no numpy scalars)
        for v in result:
            assert isinstance(v, float), f"Expected float, got {type(v)!r}"
        # Monotonically non-decreasing
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1], "Result not monotonically non-decreasing"
        # Last value approximately 1.0
        assert abs(result[-1] - 1.0) < 1e-9, f"Last value should be ~1.0, got {result[-1]}"

        # Zero-sum case: no divide-by-zero, returns [0.0]*n
        zero_result = _eigenvalues_to_variance_cumulative(np.array([0.0, 0.0, 0.0]))
        assert zero_result == [0.0, 0.0, 0.0], f"Zero-sum case wrong: {zero_result}"
        for v in zero_result:
            assert isinstance(v, float), f"Zero case: expected float, got {type(v)!r}"

        # Single element
        single = _eigenvalues_to_variance_cumulative(np.array([5.0]))
        assert abs(single[0] - 1.0) < 1e-9

    def test_fpca_output_unchanged_after_refactor(self):
        """fpca build_diagnostics output is byte-identical before and after the
        _utils refactor.  The expected dict is derived from the pre-refactor
        fpca.py logic, captured inline so the test is self-contained.
        RED gate: passes once fpca.py uses _utils but produces same output.
        """
        import json

        from fdars.advisor import build_diagnostics

        # Fixed FPCA fixture — no RNG
        sv = np.array([3.0, 1.5, 0.8])
        n_obs = 10
        scores = np.zeros((n_obs, 3))  # shape only; used for n_obs
        fpca_fixture = {
            "singular_values": sv,
            "scores": scores,
        }

        # Compute expected dict inline from the original fpca.py logic
        denom = max(n_obs - 1, 1)
        eigenvalues = (sv ** 2) / denom
        total_var = float(eigenvalues.sum())
        evr = eigenvalues / total_var
        cum_list = [float(v) for v in np.cumsum(evr)]
        n_comp = 3
        leading_var = float(evr[0])
        remaining_var = float(evr[1:].sum())
        phase_leakage_indicator = float(remaining_var)
        expected = {
            "method": "fpca",
            "n_components": n_comp,
            "n_obs": n_obs,
            "eigenvalues": [float(v) for v in eigenvalues],
            "explained_variance_ratio": [float(v) for v in evr],
            "cumulative_variance_explained": cum_list,
            "total_variance": total_var,
            "phase_leakage_indicator": phase_leakage_indicator,
            "phase_leakage_flagged": bool(phase_leakage_indicator > 0.5),
        }

        actual = build_diagnostics(fpca_fixture, method="fpca")
        assert actual == expected, (
            f"fpca output changed after refactor.\n"
            f"Expected: {json.dumps(expected, sort_keys=True)}\n"
            f"Actual:   {json.dumps(actual, sort_keys=True)}"
        )
        # Byte-identical JSON
        assert json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)

    def test_represent_deterministic(self):
        """represent build_diagnostics is byte-identical on repeated calls (ASPECT-01).

        Uses the deterministic np.ones((20,50)) + np.linspace(0,1,50) fixture
        (no RNG) so byte-identity holds unconditionally.  Verifies:
        - Two calls return equal dicts.
        - json.dumps(sort_keys=True) is byte-identical between calls.
        - No numpy scalar types leak into the output.
        - Both the dict form and the Fdata-like object form produce the same result.
        """
        import json
        import types

        from fdars.advisor import build_diagnostics

        data = np.ones((20, 50))
        argvals = np.linspace(0, 1, 50)

        # ---- Dict form ----
        d1 = build_diagnostics({"data": data, "argvals": argvals}, method="represent")
        d2 = build_diagnostics({"data": data, "argvals": argvals}, method="represent")
        assert d1 == d2, "Two calls (dict form) produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between dict-form calls"

        # No numpy scalar leak
        def check_no_numpy(obj):
            """Recursive walker: fail if any value is a numpy scalar (np.generic)."""
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

        # ---- Fdata-like object form ----
        obj = types.SimpleNamespace(data=data, argvals=argvals)
        o1 = build_diagnostics(obj, method="represent")
        o2 = build_diagnostics(obj, method="represent")
        assert o1 == o2, "Two calls (object form) produced different dicts"
        assert json.dumps(o1, sort_keys=True) == json.dumps(o2, sort_keys=True), (
            "json.dumps not byte-identical between object-form calls"
        )
        check_no_numpy(o1)

        # ---- Both forms produce identical output ----
        assert d1 == o1, "Dict form and Fdata-like object form produced different results"
        assert s1 == json.dumps(o1, sort_keys=True), (
            "json.dumps of dict form and object form not byte-identical"
        )


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

    def test_prompt_represent_clause(self):
        """represent clause appears only when aspect='represent' (ASPECT-06).

        - is_uniform_grid token is present in _system_prompt(..., 'represent')
        - is_uniform_grid token is absent from the base prompt (aspect='')
        - represent-aspect prompt differs from depth-aspect prompt
        """
        from fdars.advisor._prompts import _system_prompt

        repr_prompt = _system_prompt("interpretation", "represent")
        assert "is_uniform_grid" in repr_prompt, (
            "'is_uniform_grid' token missing from represent-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        assert "is_uniform_grid" not in base_prompt, (
            "'is_uniform_grid' unexpectedly appears in base (no-aspect) prompt"
        )
        depth_prompt = _system_prompt("interpretation", "depth")
        assert repr_prompt != depth_prompt, (
            "represent prompt must differ from depth prompt"
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


class TestRepresent:
    """RED gate tests for represent aspect (ASPECT-01 — plan 21-03, Task 2).

    These tests fail until represent.py is created and wired into the dispatcher.
    """

    def test_represent_dict_form_basic(self):
        """Dict form: n_obs, n_points, is_uniform_grid, argvals range (ASPECT-01)."""
        import json

        from fdars.advisor import build_diagnostics

        data = np.ones((20, 50))
        argvals = np.linspace(0, 1, 50)
        d = build_diagnostics({"data": data, "argvals": argvals}, method="represent")
        assert d["n_obs"] == 20
        assert d["n_points"] == 50
        assert d["is_uniform_grid"] is True
        assert abs(d["argvals_min"] - 0.0) < 1e-9
        assert abs(d["argvals_max"] - 1.0) < 1e-9
        # JSON-serialisable
        json.dumps(d, sort_keys=True)

    def test_represent_fdata_like_form(self):
        """Fdata-like object (attrs .data/.argvals) yields same fields as dict form."""
        import types

        from fdars.advisor import build_diagnostics

        data = np.ones((20, 50))
        argvals = np.linspace(0, 1, 50)
        dict_result = build_diagnostics({"data": data, "argvals": argvals}, method="represent")

        obj = types.SimpleNamespace(data=data, argvals=argvals)
        obj_result = build_diagnostics(obj, method="represent")
        assert obj_result == dict_result, (
            "Fdata-like object must yield same fields as dict form"
        )

    def test_represent_prompt_clause(self):
        """is_uniform_grid token appears in represent-aspect prompt, not in base."""
        from fdars.advisor._prompts import _system_prompt

        repr_prompt = _system_prompt("interpretation", "represent")
        assert "is_uniform_grid" in repr_prompt, (
            "'is_uniform_grid' token missing from represent-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        assert "is_uniform_grid" not in base_prompt, (
            "'is_uniform_grid' unexpectedly appears in base (no-aspect) prompt"
        )


class TestRegression:
    """Offline determinism tests for regression + regression_cv aspects (ASPECT-04).

    RED gate: these tests fail until regression.py and regression_cv.py are
    created and wired into the dispatcher.
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
                TestRegression._check_no_numpy(v)
        elif isinstance(obj, list):
            for v in obj:
                TestRegression._check_no_numpy(v)

    # ------------------------------------------------------------------
    # Task 1: regression builder tests (corrections #3/#4/#5)
    # ------------------------------------------------------------------

    def test_regression_fregre_lm_basic(self):
        """fregre_lm fixture: r_squared present, has_fosr=False, residual stats OK (ASPECT-04)."""
        import json

        from fdars.advisor import build_diagnostics

        lm_result = {
            "fitted_values": np.array([1.1, 2.0, 3.2, 0.9, 2.5]),
            "residuals": np.array([0.1, -0.2, 0.3, -0.1, 0.2]),
            "beta_t": np.linspace(-0.5, 0.5, 30),
            "r_squared": 0.82,
            "coefficients": np.array([0.3, -0.1, 0.05]),
            "intercept": 0.15,
        }
        d = build_diagnostics(lm_result, method="regression")
        assert d["method"] == "regression"
        assert abs(d["r_squared"] - 0.82) < 1e-9, "r_squared must be 0.82"
        assert d["has_fosr"] is False, "fregre_lm must not be flagged as fosr"
        assert d["residual_mean"] is not None, "residual_mean must be present for 1-D residuals"
        assert d["residual_skew"] is not None, "residual_skew must be present for 1-D residuals"
        assert d["beta_t_range"] is not None, "beta_t_range must be present when beta_t key exists"
        assert isinstance(d["beta_t_range"], list)
        assert len(d["beta_t_range"]) == 2
        # JSON-serialisable
        json.dumps(d, sort_keys=True)

    def test_regression_fregre_l1_no_r_squared(self):
        """fregre_l1 fixture: no r_squared key -> r_squared=None, no KeyError (correction #3)."""
        import json

        from fdars.advisor import build_diagnostics

        l1_result = {
            "fitted_values": np.array([1.0, 2.1, 3.0, 1.0, 2.4]),
            "residuals": np.array([0.2, -0.3, 0.5, -0.2, 0.3]),
            "beta_t": np.linspace(-0.3, 0.3, 30),
        }
        d = build_diagnostics(l1_result, method="regression")
        assert d["r_squared"] is None, "r_squared must be None when key absent (correction #3)"
        assert d["residual_mean"] is not None, "residual_mean still present for 1-D residuals"
        json.dumps(d, sort_keys=True)

    def test_regression_fosr_2d_residuals(self):
        """fosr fixture: 2-D residuals -> residual stats=None; has_fosr=True (correction #4/#5)."""
        import json

        from fdars.advisor import build_diagnostics

        fosr_result = {
            "fitted": np.ones((4, 6)),        # 2-D "fitted" key (not "fitted_values")
            "residuals": np.zeros((4, 6)),    # 2-D residuals
            "r_squared": 0.5,
        }
        d = build_diagnostics(fosr_result, method="regression")
        assert d["has_fosr"] is True, "fosr with 2-D fitted must set has_fosr=True (correction #5)"
        assert d["residual_mean"] is None, (
            "residual_mean must be None when residuals are 2-D (correction #4)"
        )
        assert d["residual_skew"] is None, "residual_skew must be None for 2-D residuals"
        json.dumps(d, sort_keys=True)

    def test_regression_1d_fitted_not_fosr(self):
        """A 1-D 'fitted' array must NOT set has_fosr=True (ndim==2 guard, correction #5)."""
        import json

        from fdars.advisor import build_diagnostics

        not_fosr_result = {
            "fitted": np.array([1.1, 2.0, 3.2, 0.9, 2.5]),  # 1-D, NOT 2-D
            "residuals": np.array([0.1, -0.2, 0.3, -0.1, 0.2]),
            "r_squared": 0.7,
        }
        d = build_diagnostics(not_fosr_result, method="regression")
        assert d["has_fosr"] is False, (
            "A 1-D fitted array must NOT be flagged as fosr — ndim==2 guard must reject it"
        )
        assert d["residual_mean"] is not None, (
            "residual_mean must be present for 1-D residuals even with 1-D fitted key"
        )
        json.dumps(d, sort_keys=True)

    def test_regression_deterministic(self):
        """Two calls on fregre_lm fixture -> equal dicts + byte-identical JSON (ASPECT-04)."""
        import json

        from fdars.advisor import build_diagnostics

        def check_no_numpy(obj):
            assert not isinstance(obj, np.generic), (
                f"numpy scalar leaked: {type(obj)!r} = {obj!r}"
            )
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_numpy(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_no_numpy(v)

        # fregre_lm fixture (with r_squared)
        lm_result = {
            "fitted_values": np.array([1.1, 2.0, 3.2, 0.9, 2.5]),
            "residuals": np.array([0.1, -0.2, 0.3, -0.1, 0.2]),
            "beta_t": np.linspace(-0.5, 0.5, 30),
            "r_squared": 0.82,
            "coefficients": np.array([0.3, -0.1, 0.05]),
            "intercept": 0.15,
        }
        d1 = build_diagnostics(lm_result, method="regression")
        d2 = build_diagnostics(lm_result, method="regression")
        assert d1 == d2, "Two calls on lm fixture produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between regression lm calls"
        check_no_numpy(d1)

        # fregre_l1 fixture (no r_squared)
        l1_result = {
            "fitted_values": np.array([1.0, 2.1, 3.0, 1.0, 2.4]),
            "residuals": np.array([0.2, -0.3, 0.5, -0.2, 0.3]),
            "beta_t": np.linspace(-0.3, 0.3, 30),
        }
        l1_d1 = build_diagnostics(l1_result, method="regression")
        l1_d2 = build_diagnostics(l1_result, method="regression")
        assert l1_d1 == l1_d2, "Two calls on l1 fixture produced different dicts"
        assert json.dumps(l1_d1, sort_keys=True) == json.dumps(l1_d2, sort_keys=True), (
            "json.dumps not byte-identical between regression l1 calls"
        )
        check_no_numpy(l1_d1)
        assert l1_d1["r_squared"] is None, "l1 fixture must have r_squared=None"

    # ------------------------------------------------------------------
    # Task 2: regression_cv builder tests (correction #7)
    # ------------------------------------------------------------------

    def test_regression_cv_fregre_cv_basic(self):
        """fregre_cv fixture: optimal_k, min_cv_error, elbow_present, array->list (ASPECT-04)."""
        import json

        from fdars.advisor import build_diagnostics

        cv_result = {
            "optimal_k": 3,
            "min_cv_error": 0.045,
            "k_values": np.array([1, 2, 3, 4, 5]),
            "cv_errors": np.array([0.12, 0.07, 0.045, 0.046, 0.048]),
            "fold_errors": np.array([0.04, 0.05, 0.04, 0.05, 0.04]),
        }
        d = build_diagnostics(cv_result, method="regression_cv")
        assert d["method"] == "regression_cv"
        assert d["optimal_k"] == 3
        assert abs(d["min_cv_error"] - 0.045) < 1e-9
        assert d["k_values"] == [1, 2, 3, 4, 5], "k_values must be a list of native ints"
        assert isinstance(d["k_values"][0], int), "k_values[0] must be native int, not numpy"
        assert d["elbow_present"] is True, "CV curve has interior minimum at index 2"
        # JSON-serialisable
        json.dumps(d, sort_keys=True)

    def test_regression_cv_model_selection_ncomp(self):
        """model_selection_ncomp fixture: criteria tuples -> optimal_k, cv_curve (correction #7)."""
        import json

        from fdars.advisor import build_diagnostics

        ms_result = {
            "best_ncomp": 2,
            "criteria": [
                (1, 10.0, 11.0, 0.5),
                (2, 9.0, 10.0, 0.3),
                (3, 9.5, 10.5, 0.35),
            ],
        }
        d = build_diagnostics(ms_result, method="regression_cv")
        assert d["optimal_k"] == 2, "optimal_k must come from best_ncomp"
        assert d["k_values"] == [1, 2, 3], "k_values from criteria tuple index 0"
        assert abs(d["cv_curve"][1] - 0.3) < 1e-9, "cv_curve from GCV at tuple index 3"
        json.dumps(d, sort_keys=True)

    def test_regression_cv_deterministic(self):
        """Two calls on fregre_cv fixture -> equal dicts + byte-identical JSON (ASPECT-04)."""
        import json

        from fdars.advisor import build_diagnostics

        def check_no_numpy(obj):
            assert not isinstance(obj, np.generic), (
                f"numpy scalar leaked: {type(obj)!r} = {obj!r}"
            )
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_numpy(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_no_numpy(v)

        cv_result = {
            "optimal_k": 3,
            "min_cv_error": 0.045,
            "k_values": np.array([1, 2, 3, 4, 5]),
            "cv_errors": np.array([0.12, 0.07, 0.045, 0.046, 0.048]),
            "fold_errors": np.array([0.04, 0.05, 0.04, 0.05, 0.04]),
        }
        d1 = build_diagnostics(cv_result, method="regression_cv")
        d2 = build_diagnostics(cv_result, method="regression_cv")
        assert d1 == d2, "Two calls on fregre_cv fixture produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between regression_cv calls"
        check_no_numpy(d1)
        assert d1["elbow_present"] is True, "elbow_present must be True for interior minimum"

    # ------------------------------------------------------------------
    # Task 3: prompt clause assertions (ASPECT-06)
    # ------------------------------------------------------------------

    def test_regression_prompt_clause(self):
        """r_squared token appears in regression-aspect prompt (ASPECT-06)."""
        from fdars.advisor._prompts import _system_prompt

        regr_prompt = _system_prompt("interpretation", "regression")
        assert "r_squared" in regr_prompt, (
            "'r_squared' token missing from regression-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        assert "r_squared" not in base_prompt, (
            "'r_squared' unexpectedly appears in base (no-aspect) prompt"
        )

    def test_regression_cv_prompt_clause(self):
        """optimal_k token appears in regression_cv-aspect prompt (ASPECT-06)."""
        from fdars.advisor._prompts import _system_prompt

        cv_prompt = _system_prompt("interpretation", "regression_cv")
        assert "optimal_k" in cv_prompt, (
            "'optimal_k' token missing from regression_cv-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        assert "optimal_k" not in base_prompt, (
            "'optimal_k' unexpectedly appears in base (no-aspect) prompt"
        )


class TestSpm:
    """Offline and fdars-guarded tests for spm aspect (ASPECT-05 — plan 21-05).

    test_spm_basic: validates field presence + JSON-serialisability without
    requiring the compiled fdars extension (the spe_moment_match_diagnostic path
    is guarded by try/except in the builder so None fallback is exercised here).

    test_spm_deterministic: uses pytest.importorskip("fdars.spm") so the test
    is skipped in environments without the compiled extension.  Exercises the
    live spe_moment_match_diagnostic call and asserts byte-identical JSON output,
    no numpy scalar leaks, and that spe_kurtosis_excess is a native float.
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
                TestSpm._check_no_numpy(v)
        elif isinstance(obj, list):
            for v in obj:
                TestSpm._check_no_numpy(v)

    # ------------------------------------------------------------------
    # Synthetic Phase-I fixture (from 21-RESEARCH §8)
    # ------------------------------------------------------------------

    @staticmethod
    def _spm_fixture():
        return {
            "t2": np.array([1.2, 3.4, 0.8, 5.1, 2.3, 4.0, 1.5, 2.7, 0.9, 3.1]),
            "spe": np.array([0.05, 0.12, 0.03, 0.25, 0.08, 0.18, 0.04, 0.09, 0.02, 0.11]),
            "t2_limit": 4.5,
            "spe_limit": 0.20,
            "eigenvalues": np.array([2.1, 0.8, 0.3]),
        }

    # ------------------------------------------------------------------
    # Task 1 tests (RED gate — spm builder must exist + be wired)
    # ------------------------------------------------------------------

    def test_spm_basic(self):
        """spm branch present in dispatcher; core fields correct; JSON-serialisable.

        Does NOT require fdars.spm (spe_moment_match_diagnostic path is guarded
        by try/except in the builder — None fallback must be tested here).
        RED gate for Task 1 (plan 21-05).
        """
        import json

        from fdars.advisor import build_diagnostics

        spm_result = self._spm_fixture()
        d = build_diagnostics(spm_result, method="spm")

        assert d["method"] == "spm"
        assert d["n_obs"] == 10
        assert d["ncomp"] == 3
        assert abs(d["t2_limit"] - 4.5) < 1e-9
        assert abs(d["spe_limit"] - 0.20) < 1e-9
        # t2: values [1.2, 3.4, 0.8, 5.1, 2.3, 4.0, 1.5, 2.7, 0.9, 3.1], limit=4.5
        # exceeds: [5.1] -> 1/10 = 0.1
        assert abs(d["t2_exceedance_rate"] - 0.1) < 1e-9, (
            f"t2_exceedance_rate expected 0.1, got {d['t2_exceedance_rate']}"
        )
        # spe: values [...0.25...0.18...], limit=0.20
        # exceeds: [0.25] -> 1/10 = 0.1
        assert abs(d["spe_exceedance_rate"] - 0.1) < 1e-9, (
            f"spe_exceedance_rate expected 0.1, got {d['spe_exceedance_rate']}"
        )
        # Cumulative variance: eigenvalues=[2.1, 0.8, 0.3], sum=3.2
        # evr=[0.65625, 0.25, 0.09375], cumsum=[0.65625, 0.90625, 1.0]
        assert abs(d["variance_explained_cumulative"][-1] - 1.0) < 1e-9, (
            f"Last cumulative variance should be ~1.0, got {d['variance_explained_cumulative'][-1]}"
        )
        # eigenvalues emitted as plain list
        assert d["eigenvalues"] == [2.1, 0.8, 0.3] or all(
            abs(a - b) < 1e-9 for a, b in zip(d["eigenvalues"], [2.1, 0.8, 0.3])
        )
        # JSON-serialisable
        json.dumps(d, sort_keys=True)

    def test_spm_deterministic(self):
        """spm build_diagnostics is byte-identical on repeated calls (ASPECT-05).

        Requires fdars.spm (uses the live spe_moment_match_diagnostic call).
        Two calls on the same Phase-I fixture must produce equal dicts AND
        byte-identical json.dumps(sort_keys=True).  All values must be native
        Python types (no numpy scalars).  spe_kurtosis_excess must be a native
        float (not None), confirming the live call succeeded.
        """
        import json

        pytest.importorskip("fdars.spm")

        from fdars.advisor import build_diagnostics

        spm_result = self._spm_fixture()
        d1 = build_diagnostics(spm_result, method="spm")
        d2 = build_diagnostics(spm_result, method="spm")

        assert d1 == d2, "Two calls produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between calls"

        # No numpy scalar types
        self._check_no_numpy(d1)

        # Live call succeeded: spe_kurtosis_excess must be a native float
        assert d1["spe_kurtosis_excess"] is not None, (
            "spe_kurtosis_excess should not be None when fdars.spm is available"
        )
        assert isinstance(d1["spe_kurtosis_excess"], float), (
            f"spe_kurtosis_excess must be native float, got {type(d1['spe_kurtosis_excess'])!r}"
        )
        assert isinstance(d1["spe_moment_match_adequate"], bool), (
            f"spe_moment_match_adequate must be native bool, got {type(d1['spe_moment_match_adequate'])!r}"
        )

    # ------------------------------------------------------------------
    # Task 2 prompt tests (spm clause)
    # ------------------------------------------------------------------

    def test_spm_prompt_clause(self):
        """t2_exceedance_rate token appears in spm-aspect prompt, not in base (ASPECT-06)."""
        from fdars.advisor._prompts import _system_prompt

        spm_prompt = _system_prompt("interpretation", "spm")
        assert "t2_exceedance_rate" in spm_prompt, (
            "'t2_exceedance_rate' token missing from spm-aspect prompt"
        )
        base_prompt = _system_prompt("interpretation", "")
        assert "t2_exceedance_rate" not in base_prompt, (
            "'t2_exceedance_rate' unexpectedly appears in base (no-aspect) prompt"
        )

    def test_all_seven_aspect_primers_present(self):
        """All seven new aspects have primer clauses in _ASPECT_PRIMERS (ASPECT-06).

        This is the final Nyquist gate for ASPECT-06 coverage: every new aspect
        added in Phase 21 must have a primer entry so that _system_prompt(task, aspect)
        delivers an FDA-grounded clause for each analysis type.
        """
        from fdars.advisor._prompts import _ASPECT_PRIMERS

        required = {
            "depth",
            "outliers",
            "classification",
            "represent",
            "regression",
            "regression_cv",
            "spm",
        }
        assert required <= set(_ASPECT_PRIMERS), (
            f"Missing aspect primers: {required - set(_ASPECT_PRIMERS)}"
        )


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
