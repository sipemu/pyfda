"""Behavior tests for convert::extract_ragged_vecs via its public consumer
fdars.pace_fpca.irreg_fdata_from_lists (FRE-03).

Tests exercise the relocated helper indirectly through irreg_fdata_from_lists
because extract_ragged_vecs is a Rust pub fn, not a Python-exposed symbol.
"""

import numpy as np
import pytest

import fdars.pace_fpca as pf


# ---------------------------------------------------------------------------
# Ragged (non-uniform-length) input is accepted
# ---------------------------------------------------------------------------


class TestRaggedVecsAcceptsNonUniform:
    """extract_ragged_vecs must accept non-uniform (ragged) per-curve lengths."""

    def test_ragged_numpy_arrays_accepted(self):
        """Two numpy arrays of different lengths must be accepted without error."""
        av_list = [np.array([0.0, 0.5, 1.0]), np.array([0.0, 0.25, 0.5, 0.75, 1.0])]
        vl_list = [np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.5, 2.0, 2.5, 3.0])]
        # Should return without raising — ragged lengths are permitted
        fd = pf.irreg_fdata_from_lists(av_list, vl_list)
        assert isinstance(fd, pf.PyIrregFdata)

    def test_mixed_element_types_accepted(self):
        """Elements may be plain Python lists or tuples as well as numpy arrays."""
        # Curve 0: plain Python list of floats
        # Curve 1: Python tuple of floats
        # Curve 2: 1-D numpy array
        av_list = [
            [0.0, 0.3, 0.6, 0.9],
            (0.1, 0.5, 0.9),
            np.array([0.0, 0.5, 1.0]),
        ]
        vl_list = [
            [0.0, 1.0, 0.0, -1.0],
            (1.0, 0.0, 1.0),
            np.array([0.0, 1.0, 0.0]),
        ]
        fd = pf.irreg_fdata_from_lists(av_list, vl_list)
        assert isinstance(fd, pf.PyIrregFdata)


# ---------------------------------------------------------------------------
# Negative case: unsupported element type raises ValueError with caller_name
# ---------------------------------------------------------------------------


class TestRaggedVecsUnsupportedType:
    """An unsupported element type must raise ValueError mentioning the caller_name."""

    def test_string_element_raises_value_error(self):
        """A string element is not a valid curve; caller_name must appear in the message."""
        av_bad = ["not an array", np.array([0.0, 0.5, 1.0])]
        vl_bad = ["not an array", np.array([1.0, 2.0, 3.0])]
        with pytest.raises(ValueError, match="irreg_fdata_from_lists"):
            pf.irreg_fdata_from_lists(av_bad, vl_bad)

    def test_int_element_raises_value_error(self):
        """A bare integer element is not a valid curve; caller_name must appear in the message."""
        av_bad = [42, np.array([0.0, 0.5, 1.0])]
        vl_bad = [42, np.array([1.0, 2.0, 3.0])]
        with pytest.raises(ValueError, match="irreg_fdata_from_lists"):
            pf.irreg_fdata_from_lists(av_bad, vl_bad)
