"""Tests for the outlier advisor diagnostics — v6.0 detector branches (ADV-04).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests mirror the structure of test_advisor_inference.py:
- check_no_numpy recursive walker
- byte-identical json.dumps(sort_keys=True)
- grounding via _extract_numbers from fdars.advisor.providers._validate
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Shared helper: recursive numpy-scalar walker (canonical pattern from
# test_advisor_inference.py:247-255).
# ---------------------------------------------------------------------------

def check_no_numpy(obj):
    """Fail if any value in obj is a numpy scalar (np.generic subclass)."""
    assert not isinstance(obj, np.generic), (
        f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
    )
    if isinstance(obj, dict):
        for v in obj.values():
            check_no_numpy(v)
    elif isinstance(obj, list):
        for v in obj:
            check_no_numpy(v)


# ---------------------------------------------------------------------------
# Task 1: TestTvdmss — build_diagnostics on a REAL tvdmss result
# ---------------------------------------------------------------------------

class TestTvdmss:
    """Verify the tvdmss branch of _build_outliers_diagnostics (ADV-04)."""

    @pytest.fixture(scope="class")
    def tvdmss_result(self):
        """Build a real tvdmss result using a deterministic small array."""
        from fdars import outliers as outl
        rng = np.random.default_rng(0)
        data = rng.standard_normal((12, 25))
        # plant a clear magnitude outlier so we get at least one index in the lists
        data[0, :] += 10
        return outl.tvdmss(data)

    def test_tvdmss_method_field(self, tvdmss_result):
        """build_diagnostics on tvdmss result returns method == 'outliers'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert diag["method"] == "outliers"

    def test_tvdmss_has_tvdmss_true(self, tvdmss_result):
        """has_tvdmss must be True for a tvdmss result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert diag["has_tvdmss"] is True

    def test_tvdmss_n_obs(self, tvdmss_result):
        """n_obs must equal len(tvd) == 12 for the fixture."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert diag["n_obs"] == 12
        assert isinstance(diag["n_obs"], int)

    def test_tvdmss_counts_are_int(self, tvdmss_result):
        """n_magnitude_outliers and n_shape_outliers must be native int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert isinstance(diag["n_magnitude_outliers"], int)
        assert isinstance(diag["n_shape_outliers"], int)

    def test_tvdmss_counts_match_raw(self, tvdmss_result):
        """Counts must equal len of the index lists in the raw result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert diag["n_magnitude_outliers"] == len(tvdmss_result["magnitude_outliers"])
        assert diag["n_shape_outliers"] == len(tvdmss_result["shape_outliers"])

    def test_tvdmss_fractions_are_float(self, tvdmss_result):
        """Outlier fractions must be native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert isinstance(diag["magnitude_outlier_fraction"], float)
        assert isinstance(diag["shape_outlier_fraction"], float)

    def test_tvdmss_fraction_values(self, tvdmss_result):
        """Fractions must equal count / n_obs."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        n_obs = diag["n_obs"]
        assert abs(diag["magnitude_outlier_fraction"] - diag["n_magnitude_outliers"] / n_obs) < 1e-12
        assert abs(diag["shape_outlier_fraction"] - diag["n_shape_outliers"] / n_obs) < 1e-12

    def test_tvdmss_ranges_are_list_of_float(self, tvdmss_result):
        """tvd_range and mss_range must be list of exactly 2 native floats."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        for key in ("tvd_range", "mss_range"):
            val = diag[key]
            assert isinstance(val, list), f"{key} must be list, got {type(val)}"
            assert len(val) == 2, f"{key} must have 2 elements"
            assert isinstance(val[0], float), f"{key}[0] must be float"
            assert isinstance(val[1], float), f"{key}[1] must be float"
            assert val[0] <= val[1], f"{key}[0] must be <= {key}[1]"

    def test_tvdmss_existing_flags_false(self, tvdmss_result):
        """has_outliergram and has_magnitude_shape must be False for a tvdmss input."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        assert diag["has_outliergram"] is False
        assert diag["has_magnitude_shape"] is False

    def test_tvdmss_no_numpy(self, tvdmss_result):
        """Output must contain no numpy scalars (check_no_numpy passes)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        check_no_numpy(diag)

    def test_tvdmss_json_serialisable(self, tvdmss_result):
        """Output must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(tvdmss_result, method="outliers")
        json.dumps(diag, sort_keys=True)

    def test_tvdmss_determinism(self, tvdmss_result):
        """Two calls on the same result produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(tvdmss_result, method="outliers")
        d2 = build_diagnostics(tvdmss_result, method="outliers")
        assert d1 == d2, "Two calls produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between calls"

    def test_tvdmss_grounding(self, tvdmss_result):
        """n_magnitude_outliers is discoverable in json.dumps(diag) via _extract_numbers."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers
        diag = build_diagnostics(tvdmss_result, method="outliers")
        diag_json = json.dumps(diag, sort_keys=True)
        found = set(_extract_numbers(diag_json))
        # n_obs = 12 must be discoverable
        n_obs_str = str(diag["n_obs"])
        assert any(n_obs_str in n or n in n_obs_str for n in found), (
            f"n_obs={diag['n_obs']} not discoverable in diagnostics json; found={found!r}"
        )
