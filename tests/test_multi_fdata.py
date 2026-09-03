"""Tests for fdars.multi_fdata — PyMultiFunData handle, builder, and guards.

MULTI-01: Opaque handle constructible from component curves; n_obs / n_components
accessors return correct values; construction-time validation raises ValueError
for bad inputs.
"""

import numpy as np
import pytest

import fdars.multi_fdata as mf

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(42)

# Non-square components per research section 8: n_obs=20, var1 (20,30), var2 (20,25)
N_OBS = 20
VAR1 = RNG.standard_normal((N_OBS, 30))   # 20 obs × 30 evaluation points
VAR2 = RNG.standard_normal((N_OBS, 25))   # 20 obs × 25 evaluation points (different domain)
AV1 = np.linspace(0, 1, 30)              # 30-point grid on [0, 1]
AV2 = np.linspace(0, 2, 25)              # 25-point grid on [0, 2]


# ---------------------------------------------------------------------------
# Happy-path: build handle and check accessors
# ---------------------------------------------------------------------------

def test_build_and_accessors():
    """Two non-square components build a handle; accessors return correct values."""
    h = mf.multi_fdata_from_components([VAR1, VAR2], [AV1, AV2])
    assert h.n_obs == N_OBS
    assert h.n_components == 2


# ---------------------------------------------------------------------------
# Guard failures — each must raise ValueError before core panics
# ---------------------------------------------------------------------------

def test_reject_length_mismatch():
    """data_list length != argvals_list length → ValueError."""
    with pytest.raises(ValueError):
        # 2 data arrays but only 1 argvals array
        mf.multi_fdata_from_components([VAR1, VAR2], [AV1])


def test_reject_1d_data():
    """A 1-D array passed as a component → ValueError (must be 2-D)."""
    flat = np.linspace(0, 1, 30)  # shape (30,) — 1-D
    with pytest.raises(ValueError):
        mf.multi_fdata_from_components([flat, VAR2], [AV1, AV2])


def test_reject_nrows_mismatch():
    """Components with different n_obs → ValueError (surfaced from MultiFunData::new)."""
    wrong_nrows = RNG.standard_normal((15, 25))  # 15 obs, not 20
    av_wrong = np.linspace(0, 2, 25)
    with pytest.raises(ValueError):
        mf.multi_fdata_from_components([VAR1, wrong_nrows], [AV1, av_wrong])
