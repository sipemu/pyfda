"""Shared helpers for build-time figure generation in the docs.

Executed by ``markdown-exec`` code blocks (``python exec="1" html="1"``).
Renders matplotlib figures to inline SVG so they embed directly in the
generated HTML -- no committed image assets, always in sync with the API.

Usage inside a docs code block::

    ```python exec="1" html="1" source="above"
    import numpy as np
    from docs_fig import fig, render
    from fdars.simulation import simulate

    f, ax = fig()
    ...
    print(render(f))
    ```

Use ``fast(full, fast_value)`` to lower expensive iteration counts in local
builds without touching the published/committed output::

    res  = fanova(X, grp, n_perm=fast(500, 50))
    out  = karcher_mean(data, t, max_iter=fast(20, 5))
    band = fpca_tolerance_band(ref, nb=fast(800, 100))

Set the environment variable ``DOCS_FAST=1`` (or any non-empty value) before
running ``mkdocs build`` to activate fast mode.  Fast mode is **speed-only**:
figures may look rougher and MUST NOT be committed as publishable output.
The full build (``DOCS_FAST`` unset) is the source of truth and the only mode
where the byte-identical determinism guarantee (FND-03) holds.
"""
from __future__ import annotations

import os as _os
from io import StringIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# ---- Brand palette (matches the mkdocs-material indigo/blue theme) ----------
FDARS_COLORS = [
    "#3f51b5",  # indigo (primary)
    "#e8710a",  # orange
    "#198754",  # green
    "#dc3545",  # red
    "#6f42c1",  # purple
    "#0dcaf0",  # cyan
    "#6c757d",  # grey
]

plt.rcParams.update(
    {
        "figure.figsize": (7.5, 4.0),
        "figure.dpi": 110,
        "savefig.transparent": True,
        "axes.prop_cycle": plt.cycler(color=FDARS_COLORS),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.7,
        "font.size": 11,
        "axes.titlesize": 12.5,
        "axes.titleweight": "600",
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "figure.autolayout": True,
        # FND-03: deterministic SVG element IDs across builds.
        # Without this, matplotlib uses uuid4() → IDs differ every run →
        # byte-for-byte comparison of two consecutive builds always fails.
        # Note: hashsalt fixes IDs only; stochastic exec blocks must also
        # seed their own RNG (rng = np.random.default_rng(42)). Per-block
        # seed auditing is a phases-3–8 concern (RESEARCH Pitfall 3).
        "svg.hashsalt": "fdars-docs",
    }
)


def fig(nrows: int = 1, ncols: int = 1, **kwargs):
    """Create a themed figure/axes pair (thin wrapper over ``plt.subplots``)."""
    return plt.subplots(nrows, ncols, **kwargs)


def render(figure=None) -> str:
    """Return ``figure`` (or the current figure) as an inline-SVG ``<div>``.

    Use inside a ``markdown-exec`` block as ``print(render(f))`` -- the block's
    ``print`` is captured by markdown-exec (with ``html="1"``) and embedded
    verbatim, dropping a crisp, scalable figure into the page. ``render`` must
    *return* rather than print, because a ``print`` executed here (in the
    ``docs_fig`` module namespace) would bypass markdown-exec's per-block
    ``print`` override and leak to real stdout.
    """
    figure = figure or plt.gcf()
    buf = StringIO()
    figure.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(figure)
    svg = buf.getvalue()
    # Strip the XML/doctype preamble so the <svg> embeds cleanly as HTML.
    start = svg.find("<svg")
    if start != -1:
        svg = svg[start:]
    return f'<div class="fdars-figure">{svg}</div>'


def fast(full, fast_value):
    """Return ``fast_value`` if ``DOCS_FAST`` is set, else ``full``.

    Central helper for lowering expensive iteration counts in local builds
    without scattering ``os.environ`` checks across individual exec blocks
    (FND-06, D-08).  Call it at any parameter that is expensive to compute::

        res  = fanova(X, grp, n_perm=fast(500, 50))
        out  = karcher_mean(data, t, max_iter=fast(20, 5))
        band = fpca_tolerance_band(ref, nb=fast(800, 100))
        ls   = lomb_scargle_fdata(fd, oversampling=fast(4, 2))

    Fast mode is **speed-only** (D-07): figures may look rougher and MUST NOT
    be committed as publishable output.  The full build (``DOCS_FAST`` unset)
    is the only source of truth and the only mode where the byte-identical
    determinism guarantee (FND-03) holds.
    """
    return fast_value if _os.environ.get("DOCS_FAST") else full
