"""Example datasets shipped with :mod:`fdars`.

Each loader returns a small :class:`Dataset` bundle whose ``.data`` attribute is
a ready-to-use :class:`fdars.Fdata` object (unless ``return_fdata=False``, in
which case the raw ``(argvals, X, meta)`` tuple is returned instead).

The CSV assets live in the package under ``fdars/data/`` and are read through
:mod:`importlib.resources`, so the loaders work identically from a source
checkout and from an installed wheel.

Datasets (see ``docs/data/README.md`` for sources, licenses and shapes):

- :func:`load_growth`            -- Berkeley Growth Study heights vs age.
- :func:`load_canadian_weather`  -- Canadian daily temperature / precipitation.
- :func:`load_tecator`           -- Tecator NIR absorbance spectra + fat content.
- :func:`load_phoneme`           -- Phoneme log-periodograms by phoneme class.
- :func:`load_wine`              -- UCI Wine chemical measurements (feature table).
- :func:`load_sonar`             -- UCI Sonar return energies (Mine/Rock).

Every loader with a real vendored CSV is exported; the synthetic
``load_penicillin`` demo lives in ``scripts/docs_data.py`` and is not shipped.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from importlib.resources import files
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:  # pragma: no cover - pandas is a hard dependency
    _HAS_PANDAS = False

from fdars.fdata_class import Fdata

__all__ = [
    "Dataset",
    "load_growth",
    "load_canadian_weather",
    "load_tecator",
    "load_phoneme",
    "load_wine",
    "load_sonar",
]


# ---------------------------------------------------------------------------
# Bundle returned by the loaders
# ---------------------------------------------------------------------------

@dataclass
class Dataset:
    """Container for a loaded example dataset.

    Attributes
    ----------
    data : fdars.Fdata
        The functional-data object (curves as rows), with metadata attached.
    argvals : numpy.ndarray or list[str]
        The shared evaluation grid (e.g. ages, days, wavelengths) or, for the
        tabular ``wine`` dataset, the list of feature names.
    y : numpy.ndarray or None
        Primary label / target aligned to the rows of the data, when the
        dataset has an obvious one (e.g. ``sex``, ``fat``, ``phoneme`` class);
        ``None`` otherwise.
    meta : pandas.DataFrame
        Per-observation labels / covariates aligned to the rows of the data.
    name : str
        Short dataset name.
    description : str
        One-line human-readable description.
    """

    data: Fdata
    argvals: Any
    y: Optional[np.ndarray]
    meta: Any
    name: str = ""
    description: str = ""
    _extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    # convenience aliases
    @property
    def target(self) -> Optional[np.ndarray]:
        return self.y

    @property
    def labels(self) -> Optional[np.ndarray]:
        return self.y

    def __getitem__(self, key: str) -> Any:
        return self._extras[key]

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Dataset(name={self.name!r}, data={self.data!r})"


# ---------------------------------------------------------------------------
# CSV reading (numpy-only, no pandas required for parsing)
# ---------------------------------------------------------------------------

def _read_csv_text(fname: str) -> str:
    """Return the text of a vendored CSV shipped under ``fdars/data/``."""
    resource = files("fdars").joinpath("data", fname)
    return resource.read_text(encoding="utf-8")


def _read_table(fname: str) -> Tuple[List[str], List[List[str]]]:
    """Parse a CSV into ``(header, rows)`` of *string* cells."""
    text = _read_csv_text(fname)
    reader = csv.reader(io.StringIO(text))
    rows = [r for r in reader if r]  # drop blank lines
    if not rows:
        raise ValueError(f"empty dataset file: {fname}")
    header = rows[0]
    # Some vendored files have a trailing empty header cell from a dangling
    # comma; drop columns whose header is empty.
    keep = [i for i, h in enumerate(header) if h.strip() != ""]
    header = [header[i] for i in keep]
    body = [[r[i] if i < len(r) else "" for i in keep] for r in rows[1:]]
    return header, body


def _column(header: List[str], body: List[List[str]], name: str) -> List[str]:
    j = header.index(name)
    return [row[j] for row in body]


def _float_matrix(body: List[List[str]], cols: List[int]) -> np.ndarray:
    return np.array(
        [[float(row[j]) for j in cols] for row in body], dtype=np.float64
    )


def _make_meta(columns: Dict[str, Any]):
    """Build metadata as a pandas DataFrame if available, else a dict."""
    if _HAS_PANDAS:
        return pd.DataFrame(columns)
    return {k: np.asarray(v) for k, v in columns.items()}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_growth(return_fdata: bool = True):
    """Berkeley Growth Study: heights (cm) of 39 boys & 54 girls at 31 ages.

    Parameters
    ----------
    return_fdata : bool, default True
        If ``True`` return a :class:`Dataset` whose ``.data`` is an
        :class:`~fdars.Fdata`; otherwise return the raw ``(age, X, meta)``.

    Returns
    -------
    Dataset or (numpy.ndarray, numpy.ndarray, meta)
        ``argvals``/age has shape ``(31,)``; the data matrix is ``(93, 31)``
        (boys first, then girls); ``meta`` has columns ``id`` and ``sex``.
    """
    header, body = _read_table("growth.csv")
    age = np.array(_column(header, body, "age"), dtype=np.float64)
    id_cols = [c for c in header if c != "age"]
    col_idx = [header.index(c) for c in id_cols]
    # rows = children, cols = ages
    X = _float_matrix(body, col_idx).T
    ids = list(id_cols)
    sex = np.array(
        ["male" if c.startswith("M") else "female" for c in ids]
    )
    meta = _make_meta({"id": ids, "sex": sex})

    if not return_fdata:
        return age, X, meta

    fd = Fdata(
        X,
        argvals=age,
        names={"main": "Berkeley Growth Study", "xlab": "age (years)",
               "ylab": "height (cm)"},
        id=ids,
        metadata=meta,
    )
    return Dataset(
        data=fd, argvals=age, y=sex, meta=meta, name="growth",
        description="Berkeley Growth Study heights (93 children x 31 ages).",
    )


def load_canadian_weather(variable: str = "temperature",
                          return_fdata: bool = True):
    """Canadian Weather: daily curves for 35 stations over a 365-day year.

    Parameters
    ----------
    variable : {"temperature", "precipitation"}, default "temperature"
        Mean daily temperature (Celsius) or precipitation (mm).
    return_fdata : bool, default True
        See :func:`load_growth`.

    Returns
    -------
    Dataset or (numpy.ndarray, numpy.ndarray, meta)
        ``argvals``/day has shape ``(365,)``; the data matrix is ``(35, 365)``;
        ``meta`` has columns ``station``, ``province``, ``region``, ``lat``,
        ``lon`` aligned to the data rows.
    """
    fname = {
        "temperature": "canadian_weather.csv",
        "precipitation": "canadian_weather_precip.csv",
    }
    if variable not in fname:
        raise ValueError(
            f"variable must be one of {sorted(fname)}, got {variable!r}"
        )

    header, body = _read_table(fname[variable])
    day = np.array(_column(header, body, "day"), dtype=np.float64)
    stations = [c for c in header if c != "day"]
    col_idx = [header.index(c) for c in stations]
    X = _float_matrix(body, col_idx).T  # one station per row

    # station metadata, aligned to the column order of the wide table
    m_header, m_body = _read_table("canadian_weather_meta.csv")
    m_station = _column(m_header, m_body, "station")
    order = {s: k for k, s in enumerate(m_station)}
    idx = [order[s] for s in stations]
    meta_cols: Dict[str, Any] = {}
    for col in m_header:
        vals = _column(m_header, m_body, col)
        vals = [vals[k] for k in idx]
        if col in ("lat", "lon"):
            vals = np.array(vals, dtype=np.float64)
        else:
            vals = np.array(vals)
        meta_cols[col] = vals
    meta = _make_meta(meta_cols)

    if not return_fdata:
        return day, X, meta

    unit = "temperature (C)" if variable == "temperature" else "precipitation (mm)"
    fd = Fdata(
        X,
        argvals=day,
        names={"main": f"Canadian Weather ({variable})",
               "xlab": "day of year", "ylab": unit},
        id=list(stations),
        metadata=meta,
    )
    return Dataset(
        data=fd, argvals=day, y=np.array(meta_cols["region"]), meta=meta,
        name="canadian_weather",
        description=f"Canadian daily {variable} for 35 stations over 365 days.",
    )


def load_tecator(return_fdata: bool = True):
    """Tecator: 100-channel NIR absorbance spectra of 240 meat samples.

    Parameters
    ----------
    return_fdata : bool, default True
        See :func:`load_growth`.

    Returns
    -------
    Dataset or (numpy.ndarray, numpy.ndarray, meta)
        ``argvals``/wavelength has shape ``(100,)`` (850..1050 nm); the data
        matrix is ``(240, 100)``; ``meta`` has columns ``sample``,
        ``moisture``, ``fat``, ``protein``. ``.y`` is the fat content.
    """
    header, body = _read_table("tecator.csv")
    ch = [c for c in header if c.startswith("ch")]
    col_idx = [header.index(c) for c in ch]
    X = _float_matrix(body, col_idx)
    wavelength = np.linspace(850.0, 1050.0, len(ch))

    sample = np.array(_column(header, body, "sample"))
    moisture = np.array(_column(header, body, "moisture"), dtype=np.float64)
    fat = np.array(_column(header, body, "fat"), dtype=np.float64)
    protein = np.array(_column(header, body, "protein"), dtype=np.float64)
    meta = _make_meta({
        "sample": sample, "moisture": moisture, "fat": fat, "protein": protein,
    })

    if not return_fdata:
        return wavelength, X, meta

    fd = Fdata(
        X,
        argvals=wavelength,
        names={"main": "Tecator NIR spectra", "xlab": "wavelength (nm)",
               "ylab": "absorbance"},
        id=[str(s) for s in sample],
        metadata=meta,
    )
    return Dataset(
        data=fd, argvals=wavelength, y=fat, meta=meta, name="tecator",
        description="Tecator NIR absorbance spectra (240 x 100) + fat content.",
    )


def load_phoneme(return_fdata: bool = True):
    """Phoneme: log-periodograms (256 freqs) for 5 phoneme classes.

    A balanced subset of the ElemStatLearn phoneme data: 80 curves from each of
    the classes ``aa``, ``ao``, ``iy``, ``sh``, ``dcl`` (400 rows).

    Parameters
    ----------
    return_fdata : bool, default True
        See :func:`load_growth`.

    Returns
    -------
    Dataset or (numpy.ndarray, numpy.ndarray, meta)
        ``argvals``/freq has shape ``(256,)``; the data matrix is
        ``(400, 256)``; ``meta`` has column ``phoneme``. ``.y`` is the class.
    """
    header, body = _read_table("phoneme.csv")
    feat = [c for c in header if c.startswith("f")]
    col_idx = [header.index(c) for c in feat]
    X = _float_matrix(body, col_idx)
    freq = np.arange(1, len(feat) + 1, dtype=np.float64)
    phoneme = np.array(_column(header, body, "phoneme"))
    meta = _make_meta({"phoneme": phoneme})

    if not return_fdata:
        return freq, X, meta

    fd = Fdata(
        X,
        argvals=freq,
        names={"main": "Phoneme log-periodograms", "xlab": "frequency index",
               "ylab": "log-periodogram"},
        metadata=meta,
    )
    return Dataset(
        data=fd, argvals=freq, y=phoneme, meta=meta, name="phoneme",
        description="Phoneme log-periodograms (400 x 256), 5 classes.",
    )


def load_wine(return_fdata: bool = True):
    """Wine (UCI): 13 chemical measurements for 178 wines of 3 cultivars.

    This is a multivariate *table* (feature vectors), commonly used as the
    input to an Andrews transformation. ``argvals`` is therefore the list of
    feature names rather than a numeric grid.

    Parameters
    ----------
    return_fdata : bool, default True
        See :func:`load_growth`. The ``Fdata`` is built over an integer
        feature-index grid ``0..12`` since the columns are heterogeneous.

    Returns
    -------
    Dataset or (list[str], numpy.ndarray, meta)
        ``argvals``/feature_names has length 13; the data matrix is
        ``(178, 13)`` (raw, unstandardized); ``meta`` has column ``cultivar``.
        ``.y`` is the cultivar (1/2/3).
    """
    header, body = _read_table("wine.csv")
    feature_names = [c for c in header if c != "class"]
    col_idx = [header.index(c) for c in feature_names]
    X = _float_matrix(body, col_idx)
    cultivar = np.array(_column(header, body, "class"), dtype=np.int64)
    meta = _make_meta({"cultivar": cultivar})

    if not return_fdata:
        return feature_names, X, meta

    grid = np.arange(len(feature_names), dtype=np.float64)
    fd = Fdata(
        X,
        argvals=grid,
        names={"main": "Wine (UCI)", "xlab": "feature index", "ylab": "value"},
        metadata=meta,
    )
    return Dataset(
        data=fd, argvals=feature_names, y=cultivar, meta=meta, name="wine",
        description="UCI Wine: 178 wines x 13 features, 3 cultivars.",
        _extras={"feature_names": feature_names},
    )


def load_sonar(return_fdata: bool = True):
    """Sonar (UCI): 60-band sonar return energies for 208 objects.

    The 60 energy values across frequency bands form a natural spectral curve.

    Parameters
    ----------
    return_fdata : bool, default True
        See :func:`load_growth`.

    Returns
    -------
    Dataset or (numpy.ndarray, numpy.ndarray, meta)
        ``argvals``/band has shape ``(60,)``; the data matrix is ``(208, 60)``
        (values in ``[0, 1]``); ``meta`` has column ``label``
        (``"Mine"``/``"Rock"``). ``.y`` is the label.
    """
    header, body = _read_table("sonar.csv")
    bands = [c for c in header if c != "label"]
    col_idx = [header.index(c) for c in bands]
    X = _float_matrix(body, col_idx)
    band = np.arange(1, len(bands) + 1, dtype=np.float64)
    label = np.array(_column(header, body, "label"))
    meta = _make_meta({"label": label})

    if not return_fdata:
        return band, X, meta

    fd = Fdata(
        X,
        argvals=band,
        names={"main": "Sonar (Mines vs Rocks)", "xlab": "frequency band",
               "ylab": "energy"},
        metadata=meta,
    )
    return Dataset(
        data=fd, argvals=band, y=label, meta=meta, name="sonar",
        description="UCI Sonar: 208 objects x 60 bands (Mine/Rock).",
    )
