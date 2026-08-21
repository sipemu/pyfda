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


# ---------------------------------------------------------------------------
# Task 2: TestMuod — build_diagnostics on a REAL muod result
# ---------------------------------------------------------------------------

class TestMuod:
    """Verify the muod branch of _build_outliers_diagnostics (ADV-04)."""

    @pytest.fixture(scope="class")
    def muod_result(self):
        """Build a real muod result using a deterministic small array."""
        from fdars import outliers as outl
        rng = np.random.default_rng(2)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10  # plant an outlier
        return outl.muod(data)

    def test_muod_has_muod_true(self, muod_result):
        """has_muod must be True for a muod result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        assert diag["has_muod"] is True

    def test_muod_method_field(self, muod_result):
        """build_diagnostics on muod result returns method == 'outliers'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        assert diag["method"] == "outliers"

    def test_muod_counts_are_int(self, muod_result):
        """All three outlier counts must be native int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        assert isinstance(diag["n_muod_magnitude_outliers"], int)
        assert isinstance(diag["n_muod_shape_outliers"], int)
        assert isinstance(diag["n_amplitude_outliers"], int)

    def test_muod_counts_match_raw(self, muod_result):
        """Counts must equal len of the index lists in the raw result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        assert diag["n_muod_magnitude_outliers"] == len(muod_result["magnitude_outliers"])
        assert diag["n_muod_shape_outliers"] == len(muod_result["shape_outliers"])
        assert diag["n_amplitude_outliers"] == len(muod_result["amplitude_outliers"])

    def test_muod_fractions_are_float(self, muod_result):
        """All three outlier fractions must be native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        for key in ("muod_magnitude_outlier_fraction", "muod_shape_outlier_fraction",
                    "amplitude_outlier_fraction"):
            assert isinstance(diag[key], float), f"{key} must be float"

    def test_muod_index_ranges_are_list_of_float(self, muod_result):
        """All three *_index_range fields must be list of 2 native floats."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        for key in ("shape_index_range", "magnitude_index_range", "amplitude_index_range"):
            val = diag[key]
            assert isinstance(val, list), f"{key} must be list"
            assert len(val) == 2, f"{key} must have 2 elements"
            assert isinstance(val[0], float), f"{key}[0] must be float"
            assert isinstance(val[1], float), f"{key}[1] must be float"

    def test_muod_has_tvdmss_false(self, muod_result):
        """has_tvdmss must be False for a muod result (no tvd/mss keys)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        assert diag["has_tvdmss"] is False

    def test_muod_no_numpy(self, muod_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(muod_result, method="outliers")
        check_no_numpy(diag)

    def test_muod_determinism(self, muod_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(muod_result, method="outliers")
        d2 = build_diagnostics(muod_result, method="outliers")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_muod_grounding(self, muod_result):
        """n_amplitude_outliers is discoverable in json.dumps(diag)."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers
        diag = build_diagnostics(muod_result, method="outliers")
        diag_json = json.dumps(diag, sort_keys=True)
        found = set(_extract_numbers(diag_json))
        n_amp = str(diag["n_amplitude_outliers"])
        assert any(n_amp in n or n in n_amp for n in found), (
            f"n_amplitude_outliers={n_amp} not discoverable; found={found!r}"
        )


# ---------------------------------------------------------------------------
# Task 2: TestSeqTransform — build_diagnostics on a REAL sequential_transform_outliers result
# ---------------------------------------------------------------------------

class TestSeqTransform:
    """Verify the sequential_transform_outliers branch (ADV-04)."""

    @pytest.fixture(scope="class")
    def seq_result(self):
        """Build a real sequential_transform_outliers result."""
        from fdars import outliers as outl
        rng = np.random.default_rng(3)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10
        return outl.sequential_transform_outliers(data, transforms=["t0", "t1", "d1"])

    def test_seq_has_sequential_transform_true(self, seq_result):
        """has_sequential_transform must be True."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(seq_result, method="outliers")
        assert diag["has_sequential_transform"] is True

    def test_seq_n_union_outliers_is_int(self, seq_result):
        """n_union_outliers must be a native int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(seq_result, method="outliers")
        assert isinstance(diag["n_union_outliers"], int)
        assert diag["n_union_outliers"] == len(seq_result["union_outliers"])

    def test_seq_n_transforms_is_int(self, seq_result):
        """n_transforms must be a native int equal to 3 (t0, t1, d1)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(seq_result, method="outliers")
        assert isinstance(diag["n_transforms"], int)
        assert diag["n_transforms"] == 3

    def test_seq_no_fabricated_fraction(self, seq_result):
        """No outlier_fraction key must be added (n_obs unrecoverable)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(seq_result, method="outliers")
        # Existing 'outlier_fraction' from LRT path should be None (no "outliers" key)
        assert diag.get("outlier_fraction") is None
        # Specifically: no key like "union_outlier_fraction" must exist
        fraction_keys = [k for k in diag if "fraction" in k and diag[k] is not None]
        assert not fraction_keys, (
            f"Fabricated fraction keys found: {fraction_keys}"
        )

    def test_seq_no_numpy(self, seq_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(seq_result, method="outliers")
        check_no_numpy(diag)

    def test_seq_determinism(self, seq_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(seq_result, method="outliers")
        d2 = build_diagnostics(seq_result, method="outliers")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


# ---------------------------------------------------------------------------
# Task 2: TestDepthgram — build_diagnostics on a REAL depthgram result
# ---------------------------------------------------------------------------

class TestDepthgram:
    """Verify the depthgram branch of _build_outliers_diagnostics (ADV-04)."""

    @pytest.fixture(scope="class")
    def depthgram_result(self):
        """Build a real depthgram result."""
        from fdars import outliers as outl
        rng = np.random.default_rng(4)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10
        return outl.depthgram(data)

    def test_depthgram_has_depthgram_true(self, depthgram_result):
        """has_depthgram must be True."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(depthgram_result, method="outliers")
        assert diag["has_depthgram"] is True

    def test_depthgram_counts_are_int(self, depthgram_result):
        """n_depthgram_shape_outliers and n_depthgram_magnitude_outliers must be int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(depthgram_result, method="outliers")
        assert isinstance(diag["n_depthgram_shape_outliers"], int)
        assert isinstance(diag["n_depthgram_magnitude_outliers"], int)

    def test_depthgram_counts_match_raw(self, depthgram_result):
        """Counts must equal len of raw index lists."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(depthgram_result, method="outliers")
        assert diag["n_depthgram_shape_outliers"] == len(depthgram_result["shape_outliers"])
        assert diag["n_depthgram_magnitude_outliers"] == len(depthgram_result["magnitude_outliers"])

    def test_depthgram_ranges_are_list_of_float(self, depthgram_result):
        """depthgram_mbd_range and depthgram_mei_range must be list of 2 floats."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(depthgram_result, method="outliers")
        for key in ("depthgram_mbd_range", "depthgram_mei_range"):
            val = diag[key]
            assert isinstance(val, list), f"{key} must be list"
            assert len(val) == 2
            assert isinstance(val[0], float) and isinstance(val[1], float)

    def test_depthgram_no_numpy(self, depthgram_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(depthgram_result, method="outliers")
        check_no_numpy(diag)

    def test_depthgram_determinism(self, depthgram_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(depthgram_result, method="outliers")
        d2 = build_diagnostics(depthgram_result, method="outliers")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


# ---------------------------------------------------------------------------
# Task 2: TestOrdering — depthgram is NOT misrouted into outliergram
# ---------------------------------------------------------------------------

class TestOrdering:
    """Verify depthgram is detected before outliergram (ADV-04 ordering guard)."""

    @pytest.fixture(scope="class")
    def depthgram_result(self):
        """Build a real depthgram result for ordering test."""
        from fdars import outliers as outl
        rng = np.random.default_rng(5)
        data = rng.standard_normal((12, 25))
        data[0, :] += 10
        return outl.depthgram(data)

    def test_depthgram_has_depthgram_not_outliergram(self, depthgram_result):
        """A depthgram result must yield has_depthgram=True and has_outliergram=False."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(depthgram_result, method="outliers")
        assert diag["has_depthgram"] is True, "has_depthgram must be True for depthgram input"
        assert diag["has_outliergram"] is False, (
            "has_outliergram must be False for depthgram input "
            "(depthgram was misrouted into the outliergram branch)"
        )

    def test_outliergram_still_works(self):
        """A real outliergram result must still yield has_outliergram=True."""
        from fdars import outliers as outl
        from fdars.advisor import build_diagnostics
        rng = np.random.default_rng(6)
        data = rng.standard_normal((12, 25))
        data[0, :] += 10
        result = outl.outliergram(data)
        diag = build_diagnostics(result, method="outliers")
        assert diag["has_outliergram"] is True
        assert diag["has_depthgram"] is False
