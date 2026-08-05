"""Loaders for the vendored FDA datasets used in the docs Examples gallery.

Each loader resolves paths relative to the repository (``docs/data/``) so it
works both interactively and at ``mkdocs`` build time, and returns a tuple::

    argvals, X, meta

where ``argvals`` is a 1-D ``np.ndarray`` of the shared evaluation grid,
``X`` is an ``(n_obs, n_points)`` ``np.ndarray`` of curves (the functional
observations, one per row), and ``meta`` is a ``pandas.DataFrame`` of
per-observation labels/covariates aligned to the rows of ``X``.

Datasets (see ``docs/data/README.md`` for sources, licenses and shapes):

- ``load_growth``          -- Berkeley Growth Study heights vs age.
- ``load_canadian_weather``-- Canadian daily mean temperature by station.
- ``load_tecator``         -- Tecator NIR absorbance spectra + fat content.
- ``load_phoneme``         -- Phoneme log-periodograms by phoneme class.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ``docs/data`` relative to this file (scripts/docs_data.py -> ../docs/data).
_DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"


def _path(name: str) -> Path:
    p = _DATA_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"vendored dataset not found: {p}")
    return p


def load_growth():
    """Berkeley Growth Study: heights (cm) of 39 boys and 54 girls at 31 ages.

    Returns
    -------
    age : np.ndarray, shape (31,)
        Ages in years (unequally spaced: yearly to age 8, then biannual).
    X : np.ndarray, shape (93, 31)
        Height curves, one child per row (boys first, then girls).
    meta : pandas.DataFrame
        Columns ``id`` (e.g. ``M01``) and ``sex`` (``"male"``/``"female"``).
    """
    df = pd.read_csv(_path("growth.csv"))
    age = df["age"].to_numpy(dtype=float)
    ids = [c for c in df.columns if c != "age"]
    X = df[ids].to_numpy(dtype=float).T  # rows = children, cols = ages
    sex = ["male" if c.startswith("M") else "female" for c in ids]
    meta = pd.DataFrame({"id": ids, "sex": sex})
    return age, X, meta


def load_canadian_weather(variable: str = "temperature"):
    """Canadian Weather: daily curves for 35 weather stations over a year.

    Parameters
    ----------
    variable : {"temperature", "precipitation"}
        Which daily curve to load (mean temperature in Celsius, or
        precipitation in mm).

    Returns
    -------
    day : np.ndarray, shape (365,)
        Day of year, 1..365.
    X : np.ndarray, shape (35, 365)
        Daily curves, one station per row.
    meta : pandas.DataFrame
        Columns ``station``, ``province``, ``region``, ``lat``, ``lon``.
    """
    fname = {
        "temperature": "canadian_weather.csv",
        "precipitation": "canadian_weather_precip.csv",
    }[variable]
    df = pd.read_csv(_path(fname))
    day = df["day"].to_numpy(dtype=float)
    stations = [c for c in df.columns if c != "day"]
    X = df[stations].to_numpy(dtype=float).T
    meta = pd.read_csv(_path("canadian_weather_meta.csv"))
    # Align meta to the column order of the wide table.
    meta = meta.set_index("station").loc[stations].reset_index()
    return day, X, meta


def load_tecator():
    """Tecator: 100-channel NIR absorbance spectra of 240 meat samples.

    Returns
    -------
    wavelength : np.ndarray, shape (100,)
        Wavelengths in nm, evenly spaced over 850..1050 nm.
    X : np.ndarray, shape (240, 100)
        Absorbance spectra, one sample per row.
    meta : pandas.DataFrame
        Columns ``sample``, ``moisture``, ``fat``, ``protein`` (percent).
    """
    df = pd.read_csv(_path("tecator.csv"))
    ch = [c for c in df.columns if c.startswith("ch")]
    X = df[ch].to_numpy(dtype=float)
    wavelength = np.linspace(850.0, 1050.0, len(ch))
    meta = df[["sample", "moisture", "fat", "protein"]].copy()
    return wavelength, X, meta


def load_phoneme():
    """Phoneme: log-periodograms (256 freqs) for 5 phoneme classes.

    A balanced, seeded subset of the ElemStatLearn phoneme data: 80 curves
    from each of the classes ``aa``, ``ao``, ``iy``, ``sh``, ``dcl``.

    Returns
    -------
    freq : np.ndarray, shape (256,)
        Frequency index, 1..256.
    X : np.ndarray, shape (400, 256)
        Log-periodogram curves, one utterance per row.
    meta : pandas.DataFrame
        Column ``phoneme`` (class label).
    """
    df = pd.read_csv(_path("phoneme.csv"))
    feat = [c for c in df.columns if c.startswith("f")]
    X = df[feat].to_numpy(dtype=float)
    freq = np.arange(1, len(feat) + 1, dtype=float)
    meta = df[["phoneme"]].copy()
    return freq, X, meta


__all__ = [
    "load_growth",
    "load_canadian_weather",
    "load_tecator",
    "load_phoneme",
]
