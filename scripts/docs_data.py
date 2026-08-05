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


def load_wine():
    """Wine (UCI): 13 chemical measurements for 178 wines of 3 cultivars.

    This is a multivariate *table*, not functional data -- it is the input to
    the Andrews transformation (feature vector -> curve). Accordingly the first
    return value is the list of feature names rather than an ``argvals`` grid.

    Returns
    -------
    feature_names : list[str], length 13
        The chemical feature names, in column order of ``X``.
    X : np.ndarray, shape (178, 13)
        Feature matrix, one wine per row (raw, unstandardized).
    meta : pandas.DataFrame
        Column ``cultivar`` (1, 2 or 3).
    """
    df = pd.read_csv(_path("wine.csv"))
    feature_names = [c for c in df.columns if c != "class"]
    X = df[feature_names].to_numpy(dtype=float)
    meta = pd.DataFrame({"cultivar": df["class"].to_numpy(dtype=int)})
    return feature_names, X, meta


def load_sonar():
    """Sonar (UCI): 60-band sonar return energies for 208 objects.

    The 60 energy values across frequency bands form a natural spectral curve.

    Returns
    -------
    band : np.ndarray, shape (60,)
        Frequency-band index, 1..60.
    X : np.ndarray, shape (208, 60)
        Energy curves, one object per row (values in [0, 1]).
    meta : pandas.DataFrame
        Column ``label`` ("Mine" or "Rock").
    """
    df = pd.read_csv(_path("sonar.csv"))
    bands = [c for c in df.columns if c != "label"]
    X = df[bands].to_numpy(dtype=float)
    band = np.arange(1, len(bands) + 1, dtype=float)
    meta = df[["label"]].copy()
    return band, X, meta


def load_penicillin(n_normal: int = 40, n_faulty: int = 6, n_points: int = 200):
    """SYNTHETIC penicillin-fermentation batch profiles for monitoring demos.

    This dataset is *simulated* (deterministic, seeded) -- it is a stylised
    stand-in for an industrial penicillin batch trajectory, not measured data.
    Each curve is a batch's penicillin concentration over the fermentation, with
    a lag, exponential growth and a stationary phase; a handful of ``faulty``
    batches have a depressed/late trajectory to exercise process monitoring.

    Returns
    -------
    time : np.ndarray, shape (n_points,)
        Fermentation time in hours, 0..400.
    X : np.ndarray, shape (n_normal + n_faulty, n_points)
        Concentration curves, normal batches first then faulty.
    meta : pandas.DataFrame
        Columns ``batch`` and ``status`` ("normal"/"faulty").
    """
    rng = np.random.default_rng(20260805)
    time = np.linspace(0.0, 400.0, n_points)

    def _batch(k_max, t_lag, rate, noise):
        # logistic growth after a lag, plus small multiplicative variation
        g = k_max / (1.0 + np.exp(-rate * (time - t_lag)))
        g *= 1.0 + noise * rng.standard_normal(n_points).cumsum() / n_points
        return np.clip(g, 0.0, None)

    rows, status = [], []
    for _ in range(n_normal):
        rows.append(_batch(k_max=rng.uniform(1.35, 1.55),
                           t_lag=rng.uniform(90, 110),
                           rate=rng.uniform(0.045, 0.055), noise=0.04))
        status.append("normal")
    for _ in range(n_faulty):
        rows.append(_batch(k_max=rng.uniform(0.85, 1.05),      # depressed yield
                           t_lag=rng.uniform(140, 175),        # late onset
                           rate=rng.uniform(0.030, 0.042), noise=0.06))
        status.append("faulty")
    X = np.vstack(rows)
    meta = pd.DataFrame({"batch": [f"B{i:02d}" for i in range(len(status))],
                         "status": status})
    return time, X, meta


__all__ = [
    "load_growth",
    "load_canadian_weather",
    "load_tecator",
    "load_phoneme",
    "load_wine",
    "load_sonar",
    "load_penicillin",
]
