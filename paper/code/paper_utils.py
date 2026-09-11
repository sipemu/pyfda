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
import seaborn as sns  # noqa: E402

__all__ = [
    "fig",
    "FDARS_COLORS",
    "data_path",
    "save_figure",
    "style_setup",
    "clean_ax",
    "panel_frame",
    "brand_legend",
    "metric_box",
    "DIMGREY",
    "LIGHTGREY",
]

# ---------------------------------------------------------------------------
# matplotlib-skill aesthetic (tvhahn/matplotlib-skill), applied with the fdars
# brand palette.  We adopt the skill's LAYOUT invariants — seaborn whitegrid +
# DejaVu Sans, full despine, dimgrey text/ticks, subtle panel frames, framed
# white legends, metric boxes — but keep FDARS_COLORS as the data palette so the
# paper stays visually consistent with the docs site.  Determinism is preserved:
# seaborn's theme is deterministic, fonts are fixed (DejaVu Sans), and
# ``save_figure`` still strips the PDF CreationDate (byte-stable re-runs).
# ---------------------------------------------------------------------------
DIMGREY = "dimgrey"
LIGHTGREY = "lightgrey"


def style_setup() -> None:
    """Install the skill's theme with the brand palette (call before plotting).

    Idempotent and deterministic — safe to call once per figure script.  Applies
    ``sns.set_theme`` (whitegrid, DejaVu Sans), then overrides the colour cycle
    with ``FDARS_COLORS`` and softens text/ticks to ``dimgrey`` per the skill's
    invariants.
    """
    sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
    plt.rcParams.update(
        {
            "figure.figsize": (7.5, 4.0),
            "figure.dpi": 150,
            "savefig.transparent": True,
            "axes.prop_cycle": plt.cycler(color=FDARS_COLORS),
            "axes.titlecolor": DIMGREY,
            "axes.titleweight": "600",
            "axes.labelcolor": DIMGREY,
            "text.color": DIMGREY,
            "xtick.color": DIMGREY,
            "ytick.color": DIMGREY,
            "xtick.labelcolor": DIMGREY,
            "ytick.labelcolor": DIMGREY,
            "axes.edgecolor": LIGHTGREY,
            "legend.frameon": False,
            "font.size": 11,
            "axes.titlesize": 12.5,
            # FND-03 parity: deterministic element IDs (no effect on PDF bytes,
            # kept for consistency with the docs pipeline).
            "svg.hashsalt": "fdars-docs",
        }
    )


def clean_ax(ax, *, grid: bool = True, grid_axis: str = "both",
             frame: bool = False) -> None:
    """Apply the skill's per-axes cleanup: despine, soften ticks, keep a grid.

    We adopt the skill's despine + dimgrey + panel-frame conventions but retain
    a subtle reference grid (the skill's "degrid" default was dropped by request
    — grid lines aid reading values off functional curves).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to clean.
    grid : bool, optional
        Draw a light reference grid.  Default True.  Pass ``False`` only where a
        grid is genuinely unwanted (e.g. heatmaps).
    grid_axis : str, optional
        Which axis the grid applies to (``"x"``/``"y"``/``"both"``).  Default
        ``"both"``; bar-like charts pass ``"y"``.
    frame : bool, optional
        Draw a subtle panel frame (lightgrey) around the axes patch — used for
        curves/scatter clouds that float in the coordinate space.
    """
    sns.despine(ax=ax, left=True, bottom=True)
    if grid:
        ax.grid(True, alpha=0.4, linewidth=0.6, axis=grid_axis)
    else:
        ax.grid(False)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", which="both", length=0, labelcolor=DIMGREY)
    if frame:
        panel_frame(ax)


def panel_frame(ax) -> None:
    """Draw the skill's subtle lightgrey panel frame via the axes patch."""
    ax.patch.set_edgecolor(LIGHTGREY)
    ax.patch.set_linewidth(0.8)


def brand_legend(ax, **kwargs):
    """``ax.legend`` with the skill's framed white-box defaults."""
    kwargs.setdefault("frameon", True)
    kwargs.setdefault("facecolor", "white")
    kwargs.setdefault("framealpha", 0.8)
    kwargs.setdefault("edgecolor", LIGHTGREY)
    kwargs.setdefault("labelcolor", DIMGREY)
    return ax.legend(**kwargs)


def metric_box(ax, text: str, *, loc: str = "upper left",
               fontsize: float = 9.5) -> None:
    """Place a skill-style metric annotation (e.g. ``$R^2$``) inside *ax*.

    Positioned just inside a corner using axis-fraction coordinates; text is
    ``dimgrey`` with no visible box (the skill's transparent metric box).
    """
    corners = {
        "upper left": (0.03, 0.97, "top", "left"),
        "upper right": (0.97, 0.97, "top", "right"),
        "lower left": (0.03, 0.03, "bottom", "left"),
        "lower right": (0.97, 0.03, "bottom", "right"),
    }
    x, y, va, ha = corners[loc]
    ax.text(
        x, y, text, transform=ax.transAxes, color=DIMGREY, fontsize=fontsize,
        va=va, ha=ha, fontweight="medium",
        bbox={"facecolor": "white", "alpha": 0.0, "pad": 4},
    )


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
