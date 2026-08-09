"""HandleRegistry — in-process by-reference data store for fdars MCP tools.

Tools exchange opaque string IDs across the MCP boundary instead of
serialising large NumPy arrays into JSON.  The registry lives in-process
alongside the stdio server, so client and server share the same dict.

This module has **no dependency on the** ``mcp`` **package** and can be
imported safely without the ``[mcp]`` extra (though the rest of the
``fdars.mcp`` subpackage still requires Python >=3.10).
"""

from __future__ import annotations

import uuid
from typing import Any

import numpy as np


class HandleRegistry:
    """In-process store mapping opaque handle IDs to datasets and result dicts.

    Parameters
    ----------
    None

    Attributes
    ----------
    _datasets : dict
        Maps ``ds-<hex>`` handle IDs to ``(data, argvals)`` tuples.
    _results : dict
        Maps ``r-<hex>`` handle IDs to result dicts.

    Notes
    -----
    The registry is a singleton (``registry = HandleRegistry()`` at module
    level).  Callers store a dataset before invoking any MCP tool, then pass
    the returned ``dataset_id`` as a tool argument.  Tests call
    ``registry.clear()`` in a teardown fixture to prevent state leakage
    between test cases (Pitfall 3).
    """

    def __init__(self) -> None:
        self._datasets: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        self._results: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Dataset handles
    # ------------------------------------------------------------------

    def store_dataset(self, data: np.ndarray, argvals: np.ndarray) -> str:
        """Store a dataset (data matrix + evaluation grid) and return its handle ID.

        Parameters
        ----------
        data : np.ndarray
            Observation matrix, shape ``(n_obs, n_points)``.
        argvals : np.ndarray
            Shared evaluation grid, shape ``(n_points,)``.

        Returns
        -------
        str
            Opaque handle ID of the form ``ds-<8-hex-chars>``.
        """
        ds_id = f"ds-{uuid.uuid4().hex[:8]}"
        self._datasets[ds_id] = (data, argvals)
        return ds_id

    def get_dataset(self, ds_id: str) -> tuple[np.ndarray, np.ndarray]:
        """Retrieve a stored dataset by its handle ID.

        Parameters
        ----------
        ds_id : str
            Handle ID returned by :meth:`store_dataset`.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            ``(data, argvals)`` as passed to :meth:`store_dataset`.

        Raises
        ------
        KeyError
            If ``ds_id`` is not in the registry (unknown or already cleared).
        """
        if ds_id not in self._datasets:
            raise KeyError(f"Unknown dataset_id: {ds_id!r}")
        return self._datasets[ds_id]

    # ------------------------------------------------------------------
    # Result handles
    # ------------------------------------------------------------------

    def store_result(self, result: dict[str, Any]) -> str:
        """Store a result dict and return its handle ID.

        Parameters
        ----------
        result : dict
            JSON-serialisable result dict (e.g. from ``fdars.clustering.kmeans_fd``
            or from ``advisor.build_diagnostics``).

        Returns
        -------
        str
            Opaque handle ID of the form ``r-<8-hex-chars>``.
        """
        r_id = f"r-{uuid.uuid4().hex[:8]}"
        self._results[r_id] = result
        return r_id

    def get_result(self, r_id: str) -> dict[str, Any]:
        """Retrieve a stored result dict by its handle ID.

        Parameters
        ----------
        r_id : str
            Handle ID returned by :meth:`store_result`.

        Returns
        -------
        dict
            Result dict as passed to :meth:`store_result`.

        Raises
        ------
        KeyError
            If ``r_id`` is not in the registry (unknown or already cleared).
        """
        if r_id not in self._results:
            raise KeyError(f"Unknown result_id: {r_id!r}")
        return self._results[r_id]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear all stored datasets and results.

        Call this in pytest teardown fixtures to prevent state leakage
        between test cases.
        """
        self._datasets.clear()
        self._results.clear()


# Module-level singleton shared by all MCP tool handlers and tests.
registry = HandleRegistry()
