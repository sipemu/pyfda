"""fdars.advisor.aspects._utils — Shared helpers for advisor aspect builders.

Contains ``_eigenvalues_to_variance_cumulative``, the canonical helper for
converting a sequence of already-scaled eigenvalues into a cumulative explained
variance list.  Used by ``fpca.py`` and ``spm.py`` (Wave 5); avoids duplicating
the three-line NumPy pattern across multiple aspect files.

All helpers in this module:
- Accept and return plain Python types or NumPy arrays as documented.
- Never call any fdars function (pure NumPy only).
- Are deterministic: identical input always produces identical output.
"""

from __future__ import annotations

import numpy as np


def _eigenvalues_to_variance_cumulative(eigenvalues) -> list:
    """Compute cumulative explained variance from a sequence of eigenvalues.

    The eigenvalues must be **already scaled** (e.g. ``sv**2 / (n-1)`` for
    FPCA, or the raw eigenvalues returned directly by ``spm_phase1``).  This
    function does NOT apply any ``/ (n-1)`` scaling step.

    Parameters
    ----------
    eigenvalues : array_like
        1-D sequence of eigenvalues, shape ``(k,)``.  All values should be
        non-negative; negative values are not rejected but will produce a
        non-monotone cumulative sequence.

    Returns
    -------
    list of float
        Cumulative explained variance ratios, length ``len(eigenvalues)``.
        Each element is a native Python ``float`` (no NumPy scalars).
        The last element is approximately ``1.0`` when the total is positive.
        Returns ``[0.0] * len(eigenvalues)`` when the sum of eigenvalues is
        ``<= 0`` (guards against divide-by-zero).

    Examples
    --------
    >>> _eigenvalues_to_variance_cumulative([2.1, 0.8, 0.3])
    [0.65625, 0.90625, 1.0]
    >>> _eigenvalues_to_variance_cumulative([0.0, 0.0])
    [0.0, 0.0]
    """
    ev = np.asarray(eigenvalues, dtype=float)
    total = float(ev.sum())
    if total <= 0.0:
        return [0.0] * len(ev)
    evr = ev / total
    return [float(v) for v in np.cumsum(evr)]
