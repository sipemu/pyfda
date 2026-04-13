"""Fdata – functional data container mirroring the R fdata class.

Bundles observation data, evaluation grid, identifiers, and metadata into a
single object so users do not have to pass separate arrays to every function.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False

from fdars import _native

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_ids(n: int) -> List[str]:
    return [f"obs_{i + 1}" for i in range(n)]


def _to_dataframe(metadata, n: int, ids: List[str]):
    """Convert metadata to a pandas DataFrame and validate."""
    if metadata is None:
        return None
    if not _HAS_PANDAS:
        raise ImportError(
            "pandas is required for metadata support. "
            "Install it with: pip install pandas"
        )
    if isinstance(metadata, pd.DataFrame):
        df = metadata.reset_index(drop=True)
    elif isinstance(metadata, dict):
        df = pd.DataFrame(metadata)
    else:
        raise TypeError("metadata must be a pandas DataFrame or dict")
    if len(df) != n:
        raise ValueError(
            f"metadata must have {n} rows (one per observation), got {len(df)}"
        )
    if "id" in df.columns:
        meta_ids = list(df["id"].astype(str))
        if meta_ids != ids:
            raise ValueError("IDs in metadata do not match fdata identifiers")
    return df


# ---------------------------------------------------------------------------
# Fdata class
# ---------------------------------------------------------------------------

class Fdata:
    """Functional data object for 1-D curves or 2-D surfaces.

    Parameters
    ----------
    data : array_like
        Observation matrix.

        * 1-D: shape ``(n_obs, n_points)``
        * 2-D: shape ``(n_obs, m1, m2)`` **or** ``(n_obs, m1*m2)``
          (the latter requires *argvals* to be a tuple of two arrays).
    argvals : array_like or tuple of array_like, optional
        Evaluation grid.  For 1-D data a single 1-D array of length
        ``n_points``; for 2-D data a tuple ``(s, t)`` of two 1-D arrays.
        Defaults to ``np.arange(n_points)`` (1-D) or inferred from the
        array shape (2-D).
    rangeval : tuple, optional
        Domain range.  Defaults to ``(argvals[0], argvals[-1])`` for 1-D, or
        a tuple of two such ranges for 2-D.
    names : dict, optional
        Plot labels.  Keys: ``main``, ``xlab``, ``ylab`` (and ``zlab`` for
        2-D).
    id : sequence of str, optional
        Observation identifiers.  Defaults to ``["obs_1", "obs_2", …]``.
    metadata : pandas.DataFrame or dict, optional
        Per-observation covariates.  Must have one row per observation.
        Dicts are automatically converted to ``pandas.DataFrame``.

    Examples
    --------
    >>> import numpy as np
    >>> from fdars import Fdata
    >>> t = np.linspace(0, 1, 100)
    >>> X = np.array([np.sin(2 * np.pi * t + p) for p in np.linspace(0, np.pi, 20)])
    >>> fd = Fdata(X, argvals=t)
    >>> fd
    Fdata (1D)  –  20 obs × 100 points  –  range [0.0, 1.0]

    >>> fd_sub = fd[0:5]          # first 5 curves, metadata preserved
    >>> fd_centered = fd.center()  # subtract pointwise mean
    """

    # ---- construction -------------------------------------------------------

    def __init__(
        self,
        data,
        argvals=None,
        rangeval=None,
        names: Optional[Dict[str, str]] = None,
        id: Optional[Sequence[str]] = None,
        metadata=None,
    ):
        data = np.asarray(data, dtype=np.float64)

        # Detect 2-D from input shape or argvals type
        is_2d = False
        dims: Optional[Tuple[int, int]] = None

        if data.ndim == 3:
            is_2d = True
            n, m1, m2 = data.shape
            dims = (m1, m2)
            data = data.reshape(n, m1 * m2)
        elif isinstance(argvals, (tuple, list)) and len(argvals) == 2:
            is_2d = True

        if data.ndim == 1:
            data = data.reshape(1, -1)

        if data.ndim != 2:
            raise ValueError("data must be a 2-D matrix or 3-D array (for surfaces)")

        n, m = data.shape

        # ---- argvals --------------------------------------------------------
        if is_2d:
            if argvals is None:
                if dims is None:
                    raise ValueError(
                        "argvals must be provided as (s, t) for 2-D data from a matrix"
                    )
                argvals = (np.arange(dims[0], dtype=np.float64),
                           np.arange(dims[1], dtype=np.float64))
            s = np.asarray(argvals[0], dtype=np.float64)
            t = np.asarray(argvals[1], dtype=np.float64)
            if dims is None:
                dims = (len(s), len(t))
            if len(s) * len(t) != m:
                raise ValueError(
                    f"argvals grid ({len(s)}×{len(t)}) does not match "
                    f"data columns ({m})"
                )
            argvals = (s, t)
        else:
            if argvals is None:
                argvals = np.arange(m, dtype=np.float64)
            argvals = np.asarray(argvals, dtype=np.float64)
            if len(argvals) != m:
                raise ValueError(
                    f"Length of argvals ({len(argvals)}) must equal number "
                    f"of columns ({m})"
                )

        # ---- rangeval -------------------------------------------------------
        if rangeval is None:
            if is_2d:
                rangeval = (
                    (float(argvals[0][0]), float(argvals[0][-1])),
                    (float(argvals[1][0]), float(argvals[1][-1])),
                )
            else:
                rangeval = (float(argvals[0]), float(argvals[-1]))

        # ---- names ----------------------------------------------------------
        if names is None:
            if is_2d:
                names = {"main": "", "xlab": "s", "ylab": "t", "zlab": "X(s,t)"}
            else:
                names = {"main": "", "xlab": "t", "ylab": "X(t)"}

        # ---- id -------------------------------------------------------------
        if id is None:
            id = _default_ids(n)
        else:
            id = [str(i) for i in id]
            if len(id) != n:
                raise ValueError(f"id must have length {n}, got {len(id)}")

        # ---- metadata -------------------------------------------------------
        metadata = _to_dataframe(metadata, n, id)

        # ---- store ----------------------------------------------------------
        self.data: np.ndarray = data
        self.argvals: Union[np.ndarray, Tuple[np.ndarray, np.ndarray]] = argvals
        self.rangeval = rangeval
        self.names: Dict[str, str] = names
        self.fdata2d: bool = is_2d
        self.dims: Optional[Tuple[int, int]] = dims
        self.id: List[str] = list(id)
        self.metadata: Optional["pd.DataFrame"] = metadata

    # ---- properties ---------------------------------------------------------

    @property
    def n_obs(self) -> int:
        """Number of observations (curves or surfaces)."""
        return self.data.shape[0]

    @property
    def n_points(self) -> int:
        """Number of evaluation points (total for 2-D)."""
        return self.data.shape[1]

    @property
    def shape(self) -> Tuple[int, ...]:
        """Shape of the data matrix."""
        return self.data.shape

    # ---- repr / print -------------------------------------------------------

    def __repr__(self) -> str:
        kind = "2D" if self.fdata2d else "1D"
        if self.fdata2d:
            grid = f"{self.dims[0]}×{self.dims[1]} grid"
            rng = (
                f"range s [{self.rangeval[0][0]}, {self.rangeval[0][1]}], "
                f"t [{self.rangeval[1][0]}, {self.rangeval[1][1]}]"
            )
        else:
            grid = f"{self.n_points} points"
            rng = f"range [{self.rangeval[0]}, {self.rangeval[1]}]"
        meta = ""
        if self.metadata is not None:
            cols = ", ".join(self.metadata.columns)
            meta = f"  –  metadata: {cols}"
        return f"Fdata ({kind})  –  {self.n_obs} obs × {grid}  –  {rng}{meta}"

    def summary(self) -> None:
        """Print a detailed summary (mirrors R's ``summary.fdata``)."""
        print("Functional data summary")
        print("=======================")
        print(f"Type: {'2D (surface)' if self.fdata2d else '1D (curve)'}")
        print(f"Number of observations: {self.n_obs}")

        if self.fdata2d:
            print(f"Grid dimensions: {self.dims[0]} × {self.dims[1]}")
            print(f"Total evaluation points: {self.n_points}")
        else:
            print(f"Number of evaluation points: {self.n_points}")

        print(f"\nData range:")
        print(f"  Min: {self.data.min():.6g}")
        print(f"  Max: {self.data.max():.6g}")
        print(f"  Mean: {self.data.mean():.6g}")
        print(f"  SD: {self.data.std():.6g}")

        if self.metadata is not None:
            print(f"\nMetadata:")
            for col in self.metadata.columns:
                vals = self.metadata[col]
                if np.issubdtype(vals.dtype, np.number):
                    print(f"  {col}: numeric, range [{vals.min()}, {vals.max()}]")
                else:
                    nuniq = vals.nunique()
                    print(f"  {col}: {vals.dtype}, {nuniq} unique values")

    # ---- indexing / subsetting ----------------------------------------------

    def __getitem__(self, key) -> "Fdata":
        """Subset observations (and optionally evaluation points for 1-D).

        Usage::

            fd[0:5]           # first 5 observations
            fd[[0, 3, 7]]     # observations by index list
            fd[0:5, 10:50]    # first 5 observations, points 10-50 (1-D only)
        """
        if isinstance(key, tuple):
            i, j = key
        else:
            i = key
            j = None

        if isinstance(i, int):
            i = [i]

        new_data = self.data[i]

        if self.fdata2d:
            if j is not None:
                raise IndexError(
                    "Column subsetting is not supported for 2-D fdata. "
                    "Use row indexing to select surfaces."
                )
            new_argvals = self.argvals
            new_rangeval = self.rangeval
            new_dims = self.dims
        else:
            if j is not None:
                new_data = new_data[:, j]
                new_argvals = self.argvals[j]
                new_rangeval = (float(new_argvals[0]), float(new_argvals[-1]))
            else:
                new_argvals = self.argvals
                new_rangeval = self.rangeval
            new_dims = None

        new_id = [self.id[k] for k in (range(*i.indices(self.n_obs)) if isinstance(i, slice) else i)]
        new_meta = None
        if self.metadata is not None:
            new_meta = self.metadata.iloc[i].reset_index(drop=True)

        return Fdata(
            data=new_data,
            argvals=new_argvals,
            rangeval=new_rangeval,
            names=self.names.copy(),
            id=new_id,
            metadata=new_meta,
        )

    def __len__(self) -> int:
        return self.n_obs

    # ---- arithmetic (element-wise, mirrors R Ops.fdata) ---------------------

    def _arith(self, other, op):
        if isinstance(other, Fdata):
            if self.data.shape != other.data.shape:
                raise ValueError("data dimensions must match")
            new_data = op(self.data, other.data)
        else:
            new_data = op(self.data, other)
        return Fdata(
            data=new_data,
            argvals=self.argvals,
            rangeval=self.rangeval,
            names=self.names.copy(),
            id=self.id.copy(),
            metadata=self.metadata,
        )

    def __add__(self, other):
        return self._arith(other, np.add)

    def __radd__(self, other):
        return self._arith(other, lambda a, b: np.add(b, a))

    def __sub__(self, other):
        return self._arith(other, np.subtract)

    def __rsub__(self, other):
        return self._arith(other, lambda a, b: np.subtract(b, a))

    def __mul__(self, other):
        return self._arith(other, np.multiply)

    def __rmul__(self, other):
        return self._arith(other, lambda a, b: np.multiply(b, a))

    def __truediv__(self, other):
        return self._arith(other, np.true_divide)

    def __rtruediv__(self, other):
        return self._arith(other, lambda a, b: np.true_divide(b, a))

    # ---- functional data operations (delegate to Rust) ----------------------

    def mean(self) -> np.ndarray:
        """Pointwise mean across observations.

        Returns
        -------
        numpy.ndarray
            1-D array of mean values.
        """
        if self.fdata2d:
            return _native.fdata.mean_2d(self.data)
        return _native.fdata.mean_1d(self.data)

    def center(self) -> "Fdata":
        """Subtract the pointwise mean (centering).

        Returns
        -------
        Fdata
            Centered functional data object.
        """
        centered = _native.fdata.center_1d(self.data)
        return Fdata(
            data=centered,
            argvals=self.argvals,
            rangeval=self.rangeval,
            names=self.names.copy(),
            id=self.id.copy(),
            metadata=self.metadata,
        )

    def deriv(self, nderiv: int = 1):
        """Compute numerical derivatives.

        Parameters
        ----------
        nderiv : int
            Order of differentiation (default 1).

        Returns
        -------
        Fdata or tuple of Fdata
            For 1-D: a single Fdata with derivative values.
            For 2-D: tuple ``(ds, dt, dsdt)`` of partial derivatives.
        """
        if self.fdata2d:
            ds, dt, dsdt = _native.fdata.deriv_2d(
                self.data, self.argvals[0], self.argvals[1]
            )
            make = lambda d, name: Fdata(
                data=d, argvals=self.argvals, rangeval=self.rangeval,
                names={**self.names, "main": name}, id=self.id.copy(),
                metadata=self.metadata,
            )
            return make(ds, "dX/ds"), make(dt, "dX/dt"), make(dsdt, "d²X/dsdt")
        result = _native.fdata.deriv_1d(self.data, self.argvals, nderiv)
        return Fdata(
            data=result,
            argvals=self.argvals,
            rangeval=self.rangeval,
            names={**self.names, "main": f"Derivative (order {nderiv})"},
            id=self.id.copy(),
            metadata=self.metadata,
        )

    def norm(self, p: float = 2.0) -> np.ndarray:
        """Compute Lp norms.

        Parameters
        ----------
        p : float
            Order of the norm (default 2.0 for L2).

        Returns
        -------
        numpy.ndarray
            1-D array of norms, one per observation.
        """
        if self.fdata2d:
            raise NotImplementedError("norm not yet implemented for 2-D fdata")
        return _native.fdata.norm_lp_1d(self.data, self.argvals, p)

    def normalize(self, method: str = "center") -> "Fdata":
        """Normalize functional data.

        Parameters
        ----------
        method : str
            One of ``"center"``, ``"autoscale"``, ``"pareto"``, ``"range"``,
            ``"curve_center"``, ``"curve_standardize"``, ``"curve_range"``.

        Returns
        -------
        Fdata
            Normalized functional data object.
        """
        result = _native.fdata.normalize(self.data, method)
        return Fdata(
            data=result,
            argvals=self.argvals,
            rangeval=self.rangeval,
            names=self.names.copy(),
            id=self.id.copy(),
            metadata=self.metadata,
        )

    def geometric_median(self, max_iter: int = 100, tol: float = 1e-8) -> np.ndarray:
        """Compute the geometric (L1) median curve or surface.

        Returns
        -------
        numpy.ndarray
            1-D array of median values.
        """
        if self.fdata2d:
            return _native.fdata.geometric_median_2d(
                self.data, self.argvals[0], self.argvals[1], max_iter, tol
            )
        return _native.fdata.geometric_median_1d(
            self.data, self.argvals, max_iter, tol
        )

    # ---- depth convenience --------------------------------------------------

    def depth(self, method: str = "fraiman_muniz", ref: Optional["Fdata"] = None,
              **kwargs) -> np.ndarray:
        """Compute depth values for each observation.

        Parameters
        ----------
        method : str
            Depth method name (e.g. ``"fraiman_muniz"``, ``"modal"``,
            ``"band"``, ``"random_projection"``, ``"random_tukey"``).
        ref : Fdata, optional
            Reference data.  Defaults to ``self``.
        **kwargs
            Extra parameters forwarded to the depth function.

        Returns
        -------
        numpy.ndarray
            1-D array of depth values.
        """
        suffix = "_2d" if self.fdata2d else "_1d"
        fn = getattr(_native.depth, method + suffix)
        ref_data = ref.data if ref is not None else self.data
        return fn(self.data, ref_data, **kwargs)

    # ---- metric convenience -------------------------------------------------

    def distance(self, other: Optional["Fdata"] = None, method: str = "lp",
                 **kwargs) -> np.ndarray:
        """Compute a distance matrix.

        Parameters
        ----------
        other : Fdata, optional
            Second set of observations.  If ``None`` computes self-distances.
        method : str
            Distance method (e.g. ``"lp"``, ``"hausdorff"``, ``"dtw"``).
        **kwargs
            Extra parameters forwarded to the metric function.

        Returns
        -------
        numpy.ndarray
            2-D distance matrix.
        """
        suffix = "_2d" if self.fdata2d else "_1d"
        if other is None:
            fn = getattr(_native.metric, method + "_self" + suffix)
            return fn(self.data, self.argvals, **kwargs)
        fn = getattr(_native.metric, method + "_cross" + suffix)
        return fn(self.data, other.data, self.argvals, **kwargs)

    # ---- copy ---------------------------------------------------------------

    def copy(self) -> "Fdata":
        """Return a deep copy."""
        meta = self.metadata.copy() if self.metadata is not None else None
        av = (self.argvals[0].copy(), self.argvals[1].copy()) if self.fdata2d else self.argvals.copy()
        return Fdata(
            data=self.data.copy(),
            argvals=av,
            rangeval=self.rangeval,
            names=self.names.copy(),
            id=self.id.copy(),
            metadata=meta,
        )
