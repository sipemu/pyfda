"""Shared helpers for the paper figure pipeline.

Reuses scripts/docs_fig.py for figure style and docs/data/ for datasets.
This module must be importable with PYTHONPATH=scripts:paper/code.

Design decisions (PIPE-01, PIPE-02):
- ``fig`` and ``FDARS_COLORS`` are re-exported from ``docs_fig``; importing
  that module also runs its module-top ``matplotlib.use("Agg")`` and
  ``plt.rcParams.update`` block — do NOT repeat them here.
- ``data_path`` resolves against ``docs/data/`` in the repo root; no dataset
  is ever copied into the paper tree.
- ``save_figure`` writes a deterministic PDF with the ``CreationDate`` key set
  to ``None`` so that re-runs leave ``git diff paper/figures/`` empty.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Make scripts/ importable when running under PYTHONPATH=scripts:paper/code
# or directly via `python paper/code/gen_figures.py` from the repo root.
# paper/code/ is three levels below the repo root, so .parent × 3 reaches it.
# ---------------------------------------------------------------------------
_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Re-export the established docs_fig surface.
# Importing docs_fig runs its module-top matplotlib.use("Agg") and rcParams
# block — Agg backend and all style rcParams are active after this import.
from docs_fig import fig, FDARS_COLORS  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

__all__ = ["fig", "FDARS_COLORS", "data_path", "save_figure"]


def data_path(name: str) -> Path:
    """Return an absolute path to a dataset file in docs/data/.

    Parameters
    ----------
    name : str
        Filename relative to ``docs/data/`` (e.g. ``"growth.csv"``).
        Must not contain ``..`` or be an absolute path.

    Returns
    -------
    Path
        Absolute path to the dataset file.

    Raises
    ------
    ValueError
        If ``name`` contains ``..`` or is an absolute path (path traversal
        rejected per T-85-01).
    FileNotFoundError
        If the resolved path does not exist.

    Notes
    -----
    No dataset is copied — the paper pipeline resolves against the canonical
    ``docs/data/`` directory in the repository (per PIPE-01, D-14.0
    data-reuse lock).  This keeps a single authoritative copy and avoids
    size-doubling committed data in ``paper/``.
    """
    root = Path(__file__).resolve().parent.parent.parent
    data_dir = (root / "docs" / "data").resolve()
    resolved = (data_dir / name).resolve()
    if not resolved.is_relative_to(data_dir):
        raise ValueError(
            f"data_path: name must be a plain filename, got {name!r}. "
            "Traversal and absolute paths are not permitted."
        )
    if not resolved.exists():
        raise FileNotFoundError(f"dataset not found: {resolved}")
    return resolved


def save_figure(figure, path: str | Path) -> None:
    """Save *figure* as a deterministic PDF to *path*, then close it.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        The figure to save.
    path : str or Path
        Destination path (created by the caller's ``mkdir``).

    Notes
    -----
    Passes ``metadata={"CreationDate": None}`` to suppress the default
    wall-clock stamp embedded in PDF output so that consecutive pipeline runs
    produce byte-identical files and ``git diff paper/figures/`` stays empty
    (per PIPE-02, T-85-02).
    """
    figure.savefig(
        path,
        format="pdf",
        bbox_inches="tight",
        metadata={"CreationDate": None},
    )
    plt.close(figure)
