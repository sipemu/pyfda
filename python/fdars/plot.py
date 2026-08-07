"""fdars.plot – matplotlib plotting layer for functional data analysis.

This module is an **optional** convenience layer.  matplotlib is *not* a hard
dependency of ``fdars``; it is imported lazily inside each function.  Install
the plotting extra with::

    pip install "fdars[plot]"

Every plotting function accepts an optional ``ax`` argument (a matplotlib
``Axes``).  When ``ax`` is ``None`` a new figure/axes is created.  All
functions return the ``Axes`` (or a sequence of ``Axes`` for multi-panel
plots) so results can be further customised or embedded in larger figures.

The helpers are deliberately tolerant of their inputs: anywhere an ``Fdata``
object is accepted you may equally pass a raw ``(argvals, values)`` pair (or
just a ``values`` matrix, in which case an integer index grid is assumed).
Functions that consume result dictionaries (``plot_fpca``, ``plot_spm_chart``,
``plot_outliergram``, ``plot_tolerance_band``) accept the plain ``dict``
objects returned by the corresponding native ``fdars`` routines.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple, Union

import numpy as np

__all__ = [
    "plot_fdata",
    "plot_mean_band",
    "plot_fpca",
    "plot_alignment",
    "plot_outliergram",
    "plot_boxplot",
    "plot_spm_chart",
    "plot_tolerance_band",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_mpl():
    """Import matplotlib lazily, raising a helpful error if it is missing."""
    try:
        import matplotlib.pyplot as plt  # noqa: F401
        return plt
    except ImportError as exc:  # pragma: no cover - trivial
        raise ImportError(
            "matplotlib is required for fdars.plot but is not installed. "
            'Install the plotting extra with:  pip install "fdars[plot]"'
        ) from exc


def _new_ax(ax, plt, **fig_kw):
    """Return ``ax`` unchanged, or create a fresh one."""
    if ax is None:
        _, ax = plt.subplots(**fig_kw)
    return ax


def _coerce(fd, values=None) -> Tuple[np.ndarray, np.ndarray, Dict[str, str]]:
    """Normalise the many accepted input forms to ``(argvals, values, names)``.

    Accepted forms
    --------------
    * an ``Fdata`` object
    * ``(argvals, values)`` when called as ``_coerce(argvals, values)``
    * a bare 1-D/2-D array of ``values`` (an integer grid is assumed)

    Returns
    -------
    argvals : (m,) ndarray
    values : (n, m) ndarray  (always 2-D)
    names : dict  with keys ``main``/``xlab``/``ylab`` (best-effort)
    """
    names = {"main": "", "xlab": "t", "ylab": "X(t)"}

    # Duck-type an Fdata: it exposes ``.data`` and ``.argvals``.
    if values is None and hasattr(fd, "data") and hasattr(fd, "argvals"):
        if getattr(fd, "fdata2d", False):
            raise NotImplementedError(
                "fdars.plot currently supports 1-D functional data only; "
                "the supplied Fdata is 2-D."
            )
        argvals = np.asarray(fd.argvals, dtype=float)
        vals = np.asarray(fd.data, dtype=float)
        if getattr(fd, "names", None):
            names = {**names, **fd.names}
        return argvals, np.atleast_2d(vals), names

    # ``_coerce((argvals, values))`` passed as a single 2-tuple/2-list
    if (values is None and isinstance(fd, (tuple, list)) and len(fd) == 2
            and not hasattr(fd, "data")):
        fd, values = fd[0], fd[1]

    # ``_coerce(argvals, values)``
    if values is not None:
        argvals = np.asarray(fd, dtype=float).ravel()
        vals = np.atleast_2d(np.asarray(values, dtype=float))
        return argvals, vals, names

    # bare values array
    vals = np.atleast_2d(np.asarray(fd, dtype=float))
    argvals = np.arange(vals.shape[1], dtype=float)
    return argvals, vals, names


def _apply_labels(ax, names: Dict[str, str], main=None, xlab=None, ylab=None):
    """Apply title/axis labels, letting explicit args override ``names``."""
    title = main if main is not None else names.get("main", "")
    if title:
        ax.set_title(title)
    ax.set_xlabel(xlab if xlab is not None else names.get("xlab", ""))
    ax.set_ylabel(ylab if ylab is not None else names.get("ylab", ""))


def _get(result: Dict[str, Any], *keys, required: bool = True, default=None):
    """Fetch the first present key from a result dict."""
    if not isinstance(result, dict):
        raise TypeError(
            f"expected a result dict, got {type(result).__name__}"
        )
    for k in keys:
        if k in result:
            return result[k]
    if required:
        raise KeyError(
            f"result dict is missing any of the expected keys {keys}; "
            f"available keys: {sorted(result)}"
        )
    return default


# ---------------------------------------------------------------------------
# Curve overlays
# ---------------------------------------------------------------------------

def plot_fdata(
    fd,
    values=None,
    ax=None,
    n_sample: Optional[int] = None,
    color=None,
    alpha: float = 0.7,
    linewidth: float = 0.8,
    highlight: Optional[Sequence[int]] = None,
    highlight_color: str = "crimson",
    random_state: Optional[int] = None,
    **kw,
):
    """Overlay a sample of functional curves.

    Parameters
    ----------
    fd : Fdata or array_like
        Functional data.  Either an ``Fdata`` object, a ``values`` matrix
        (with ``values`` left ``None``), or ``argvals`` when ``values`` is
        also supplied.
    values : array_like, optional
        Value matrix ``(n, m)`` when ``fd`` holds the ``argvals`` grid.
    ax : matplotlib.axes.Axes, optional
        Target axes.  A new one is created when omitted.
    n_sample : int, optional
        If given and smaller than ``n``, plot a random subset of this many
        curves (useful for large samples).
    color : optional
        Colour for the (non-highlighted) curves.
    alpha, linewidth : float
        Line styling.
    highlight : sequence of int, optional
        Row indices to draw on top in ``highlight_color``.
    random_state : int, optional
        Seed for the subsampling RNG.
    **kw
        Extra keyword arguments forwarded to ``Axes.plot``.

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _require_mpl()
    ax = _new_ax(ax, plt)
    argvals, vals, names = _coerce(fd, values)
    n = vals.shape[0]

    idx = np.arange(n)
    if n_sample is not None and n_sample < n:
        rng = np.random.default_rng(random_state)
        idx = np.sort(rng.choice(n, size=n_sample, replace=False))

    highlight = set(int(h) for h in highlight) if highlight else set()

    for i in idx:
        if i in highlight:
            continue
        ax.plot(argvals, vals[i], color=color, alpha=alpha,
                linewidth=linewidth, **kw)
    for i in sorted(highlight):
        if 0 <= i < n:
            ax.plot(argvals, vals[i], color=highlight_color, alpha=1.0,
                    linewidth=max(linewidth, 1.5), zorder=5)

    _apply_labels(ax, names)
    return ax


def plot_mean_band(
    fd,
    values=None,
    ax=None,
    band: str = "sd",
    n_sd: float = 1.0,
    quantiles: Tuple[float, float] = (0.25, 0.75),
    show_curves: bool = False,
    mean_color: str = "navy",
    band_color: str = "steelblue",
    band_alpha: float = 0.25,
    **kw,
):
    """Plot the pointwise mean with a variability envelope.

    Parameters
    ----------
    fd, values : see :func:`plot_fdata`.
    ax : matplotlib.axes.Axes, optional
    band : {"sd", "quantile"}
        ``"sd"`` draws mean ± ``n_sd`` standard deviations; ``"quantile"``
        draws the empirical band between ``quantiles``.
    n_sd : float
        Number of standard deviations for the ``"sd"`` band.
    quantiles : (low, high)
        Lower/upper quantiles for the ``"quantile"`` band.
    show_curves : bool
        Faintly draw the individual curves underneath.
    **kw
        Forwarded to the mean line ``Axes.plot`` call.

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _require_mpl()
    ax = _new_ax(ax, plt)
    argvals, vals, names = _coerce(fd, values)

    if show_curves:
        for row in vals:
            ax.plot(argvals, row, color="0.7", alpha=0.3, linewidth=0.6)

    mean = vals.mean(axis=0)

    if band == "sd":
        sd = vals.std(axis=0)
        lower, upper = mean - n_sd * sd, mean + n_sd * sd
        band_label = f"mean ± {n_sd:g} sd"
    elif band == "quantile":
        lo, hi = quantiles
        lower = np.quantile(vals, lo, axis=0)
        upper = np.quantile(vals, hi, axis=0)
        band_label = f"[{lo:g}, {hi:g}] quantile band"
    else:
        raise ValueError("band must be 'sd' or 'quantile'")

    ax.fill_between(argvals, lower, upper, color=band_color,
                    alpha=band_alpha, label=band_label)
    ax.plot(argvals, mean, color=mean_color, linewidth=2.0,
            label="mean", **kw)

    _apply_labels(ax, names)
    ax.legend(loc="best", fontsize="small")
    return ax


# ---------------------------------------------------------------------------
# FPCA
# ---------------------------------------------------------------------------

def plot_fpca(
    result: Dict[str, Any],
    argvals=None,
    n_comp: Optional[int] = None,
    axes=None,
    scree_color: str = "steelblue",
    **kw,
):
    """Scree plot plus the leading functional principal components.

    Parameters
    ----------
    result : dict
        Output of the native FPCA / represent routine.  Expected keys:
        ``rotation`` (m, k) or ``components``/``harmonics``,
        ``singular_values`` (k,) or ``eigenvalues``/``sdev``, and
        (optionally) ``mean`` (m,).
    argvals : array_like, optional
        Evaluation grid of length ``m``.  Defaults to an integer index.
    n_comp : int, optional
        Number of components to draw (defaults to all available).
    axes : sequence of two Axes, optional
        ``(scree_ax, component_ax)``.  Created when omitted.
    scree_color : str
        Bar colour for the scree plot.
    **kw
        Forwarded to the component ``Axes.plot`` calls.

    Returns
    -------
    (scree_ax, component_ax) : tuple of matplotlib.axes.Axes
    """
    plt = _require_mpl()

    rotation = np.asarray(
        _get(result, "rotation", "components", "harmonics"), dtype=float
    )
    if rotation.ndim == 1:
        rotation = rotation[:, None]
    sv = np.asarray(
        _get(result, "singular_values", "eigenvalues", "sdev", "values"),
        dtype=float,
    ).ravel()

    m, k_avail = rotation.shape
    if n_comp is None:
        n_comp = k_avail
    n_comp = min(n_comp, k_avail)

    if argvals is None:
        argvals = np.arange(m, dtype=float)
    else:
        argvals = np.asarray(argvals, dtype=float).ravel()

    if axes is None:
        _, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    scree_ax, comp_ax = axes

    # --- scree: proportion of variance ---
    var = sv ** 2 if np.all(sv >= 0) else np.abs(sv)
    total = var.sum()
    prop = var / total if total > 0 else var
    comps = np.arange(1, len(prop) + 1)
    scree_ax.bar(comps, prop, color=scree_color, alpha=0.85)
    scree_ax.plot(comps, np.cumsum(prop), "-o", color="darkorange",
                  markersize=4, label="cumulative")
    scree_ax.set_xlabel("component")
    scree_ax.set_ylabel("proportion of variance")
    scree_ax.set_title("Scree plot")
    scree_ax.set_xticks(comps)
    scree_ax.legend(loc="center right", fontsize="small")

    # --- leading components (harmonics) ---
    for j in range(n_comp):
        lbl = f"PC{j + 1}"
        if j < len(prop):
            lbl += f" ({prop[j] * 100:.1f}%)"
        comp_ax.plot(argvals, rotation[:, j], label=lbl, **kw)
    comp_ax.axhline(0.0, color="0.7", linewidth=0.8, zorder=0)
    comp_ax.set_xlabel("t")
    comp_ax.set_ylabel("weight")
    comp_ax.set_title("Principal components")
    comp_ax.legend(loc="best", fontsize="small")

    return scree_ax, comp_ax


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------

def plot_alignment(
    original,
    aligned,
    warps=None,
    argvals=None,
    axes=None,
    alpha: float = 0.6,
    linewidth: float = 0.8,
    **kw,
):
    """Three-panel before/after alignment plot with warping functions.

    Parameters
    ----------
    original : Fdata or array_like
        Unaligned curves ``(n, m)``.
    aligned : Fdata, array_like, or dict
        Aligned curves.  A result ``dict`` from an alignment routine is also
        accepted, in which case the aligned curves are read from
        ``aligned_data`` and warps from ``gammas`` when ``warps`` is None.
    warps : array_like, optional
        Warping functions ``(n, m)`` (``gamma`` curves).  When omitted they
        are taken from the ``aligned`` dict if present.
    argvals : array_like, optional
        Shared evaluation grid.  Inferred from ``original`` when possible.
    axes : sequence of Axes, optional
        Two axes (no warps) or three axes (with warps).
    **kw
        Forwarded to the curve ``Axes.plot`` calls.

    Returns
    -------
    tuple of matplotlib.axes.Axes
    """
    plt = _require_mpl()

    # Unpack a result dict for the aligned argument.
    if isinstance(aligned, dict):
        if warps is None:
            warps = aligned.get("gammas")
        aligned = _get(aligned, "aligned_data", "aligned", "f_aligned")

    o_argvals, o_vals, o_names = _coerce(original)
    if argvals is None:
        argvals = o_argvals

    if isinstance(aligned, dict):  # pragma: no cover - defensive
        raise TypeError("could not extract aligned curves from dict")
    _, a_vals, _ = _coerce(aligned)
    a_vals = np.atleast_2d(np.asarray(a_vals, dtype=float))

    have_warps = warps is not None
    n_panels = 3 if have_warps else 2

    if axes is None:
        _, axes = plt.subplots(1, n_panels, figsize=(4.6 * n_panels, 4.0))
    axes = np.atleast_1d(axes)

    for row in o_vals:
        axes[0].plot(argvals, row, color="steelblue", alpha=alpha,
                     linewidth=linewidth, **kw)
    axes[0].set_title("Original")
    _apply_labels(axes[0], o_names, main="Original")

    a_grid = argvals if a_vals.shape[1] == len(argvals) else np.arange(a_vals.shape[1])
    for row in a_vals:
        axes[1].plot(a_grid, row, color="seagreen", alpha=alpha,
                     linewidth=linewidth, **kw)
    axes[1].set_title("Aligned")
    _apply_labels(axes[1], o_names, main="Aligned")

    if have_warps:
        warps = np.atleast_2d(np.asarray(warps, dtype=float))
        w_grid = argvals if warps.shape[1] == len(argvals) else np.linspace(
            argvals[0], argvals[-1], warps.shape[1])
        for row in warps:
            axes[2].plot(w_grid, row, color="0.4", alpha=alpha,
                         linewidth=linewidth)
        # identity reference
        axes[2].plot(w_grid, np.linspace(w_grid[0], w_grid[-1], len(w_grid)),
                     "--", color="crimson", linewidth=1.0, label="identity")
        axes[2].set_title("Warping functions")
        axes[2].set_xlabel("t")
        axes[2].set_ylabel(r"$\gamma(t)$")
        axes[2].legend(loc="best", fontsize="small")

    return tuple(axes)


# ---------------------------------------------------------------------------
# Outliergram / functional boxplot
# ---------------------------------------------------------------------------

def plot_outliergram(
    result: Dict[str, Any],
    ax=None,
    factor: float = 1.5,
    point_color: str = "steelblue",
    outlier_color: str = "crimson",
    **kw,
):
    """Outliergram: Modified Epigraph Index (MEI) versus Modified Band Depth.

    Parameters
    ----------
    result : dict
        Output of the native ``outliergram`` routine.  Expected keys:
        ``mei`` (n,), ``mbd`` (n,) and optionally ``outliers`` (bool array).
    ax : matplotlib.axes.Axes, optional
    factor : float
        Outlier factor used only to annotate the plot title.
    **kw
        Forwarded to the ``Axes.scatter`` call.

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _require_mpl()
    ax = _new_ax(ax, plt)

    mei = np.asarray(_get(result, "mei"), dtype=float).ravel()
    mbd = np.asarray(_get(result, "mbd", "depth"), dtype=float).ravel()
    outliers = result.get("outliers")
    if outliers is None:
        outliers = np.zeros(len(mei), dtype=bool)
    else:
        outliers = np.asarray(outliers, dtype=bool).ravel()

    # theoretical parabola  MBD = a0 + a1*MEI + a2*n*MEI^2  (a0=-2, a1=2, a2=2)
    grid = np.linspace(0.0, 1.0, 200)
    parabola = 2.0 * grid - 2.0 * grid ** 2  # normalised reference
    scale = mbd.max() / parabola.max() if parabola.max() > 0 and len(mbd) else 1.0
    ax.plot(grid, parabola * scale, "--", color="0.5", linewidth=1.0,
            label="reference parabola", zorder=1)

    ax.scatter(mei[~outliers], mbd[~outliers], color=point_color,
               s=30, label="regular", zorder=2, **kw)
    if outliers.any():
        ax.scatter(mei[outliers], mbd[outliers], color=outlier_color,
                   s=45, marker="D", label="outlier", zorder=3, **kw)

    ax.set_xlabel("Modified Epigraph Index (MEI)")
    ax.set_ylabel("Modified Band Depth (MBD)")
    ax.set_title(f"Outliergram (factor = {factor:g})")
    ax.legend(loc="best", fontsize="small")
    return ax


def plot_boxplot(
    fd,
    values=None,
    ax=None,
    depth: Optional[Sequence[float]] = None,
    central_prop: float = 0.5,
    factor: float = 1.5,
    show_outliers: bool = True,
    median_color: str = "black",
    box_color: str = "dodgerblue",
    box_alpha: float = 0.35,
    outlier_color: str = "crimson",
    **kw,
):
    """Functional boxplot (central envelope, median, whiskers, outliers).

    The central region is the envelope of the ``central_prop`` deepest curves.
    Curves outside the whisker fence (central envelope inflated by ``factor``)
    are flagged as outliers.

    Parameters
    ----------
    fd, values : see :func:`plot_fdata`.
    ax : matplotlib.axes.Axes, optional
    depth : sequence of float, optional
        Per-curve depth values (larger = more central).  When omitted a
        simple band-depth proxy based on pointwise ranks is used.
    central_prop : float
        Proportion of deepest curves defining the central envelope.
    factor : float
        Whisker inflation factor.
    show_outliers : bool
        Draw flagged outlier curves.

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _require_mpl()
    ax = _new_ax(ax, plt)
    argvals, vals, names = _coerce(fd, values)
    n = vals.shape[0]

    if depth is None:
        # Modified band depth proxy: mean over t of how many curves the
        # observation lies between (via pointwise ranks).
        ranks = np.argsort(np.argsort(vals, axis=0), axis=0)  # 0..n-1
        prop_below = ranks / (n - 1 if n > 1 else 1)
        depth = 1.0 - np.abs(prop_below - 0.5).mean(axis=1) * 2.0
    depth = np.asarray(depth, dtype=float).ravel()

    order = np.argsort(depth)[::-1]  # deepest first
    median_idx = order[0]
    n_central = max(1, int(np.ceil(central_prop * n)))
    central = order[:n_central]

    lower = vals[central].min(axis=0)
    upper = vals[central].max(axis=0)

    # whisker fence
    ext = factor * (upper - lower)
    fence_lo, fence_hi = lower - ext, upper + ext
    inside = np.all((vals >= fence_lo) & (vals <= fence_hi), axis=1)
    outliers = np.where(~inside)[0]

    # non-outlier envelope for whiskers
    reg = vals[inside] if inside.any() else vals
    whisk_lo = reg.min(axis=0)
    whisk_hi = reg.max(axis=0)

    ax.fill_between(argvals, lower, upper, color=box_color, alpha=box_alpha,
                    label=f"central {central_prop:.0%}", zorder=1)
    ax.plot(argvals, upper, color=box_color, linewidth=1.0, zorder=2)
    ax.plot(argvals, lower, color=box_color, linewidth=1.0, zorder=2)
    ax.plot(argvals, whisk_hi, color="0.4", linewidth=0.8, linestyle="--",
            zorder=2)
    ax.plot(argvals, whisk_lo, color="0.4", linewidth=0.8, linestyle="--",
            zorder=2, label="whiskers")
    ax.plot(argvals, vals[median_idx], color=median_color, linewidth=2.0,
            label="median", zorder=4, **kw)

    if show_outliers and len(outliers):
        for i in outliers:
            ax.plot(argvals, vals[i], color=outlier_color, linewidth=0.9,
                    alpha=0.9, zorder=3)
        # single legend entry
        ax.plot([], [], color=outlier_color, linewidth=0.9, label="outliers")

    _apply_labels(ax, names, main="Functional boxplot")
    ax.legend(loc="best", fontsize="small")
    return ax


# ---------------------------------------------------------------------------
# SPM control chart
# ---------------------------------------------------------------------------

def plot_spm_chart(
    stats,
    limits=None,
    ax=None,
    statistic: str = "t2",
    center: Optional[float] = None,
    label: Optional[str] = None,
    marker_color: str = "steelblue",
    alarm_color: str = "crimson",
    **kw,
):
    """Control chart with an upper control limit (and optional centre line).

    Parameters
    ----------
    stats : array_like or dict
        Either the per-observation statistic values, or a result dict from
        ``spm_phase1`` / ``spm_monitor``.  When a dict is given, ``statistic``
        selects ``"t2"`` or ``"spe"`` and the corresponding ``*_limit`` /
        ``*_alarm`` entries are used automatically.
    limits : float or (lower, upper), optional
        Upper control limit, or a ``(lcl, ucl)`` pair.  Ignored when ``stats``
        is a dict carrying its own limit.
    ax : matplotlib.axes.Axes, optional
    statistic : {"t2", "spe"}
        Which statistic to read when ``stats`` is a dict.
    center : float, optional
        Centre line.  Defaults to the median of the plotted statistic.
    **kw
        Forwarded to the ``Axes.plot`` marker call.

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _require_mpl()
    ax = _new_ax(ax, plt)

    alarm = None
    ucl = None
    lcl = None

    if isinstance(stats, dict):
        key = statistic.lower()
        values = np.asarray(_get(stats, key), dtype=float).ravel()
        ucl = stats.get(f"{key}_limit", stats.get("limit"))
        alarm = stats.get(f"{key}_alarm")
        if label is None:
            label = key.upper()
    else:
        values = np.asarray(stats, dtype=float).ravel()

    if limits is not None:
        if np.isscalar(limits):
            ucl = float(limits)
        else:
            lcl, ucl = float(limits[0]), float(limits[1])

    if label is None:
        label = statistic.upper()

    idx = np.arange(1, len(values) + 1)

    if alarm is None and ucl is not None:
        alarm = values > ucl
    alarm = (np.asarray(alarm, dtype=bool).ravel()
             if alarm is not None else np.zeros(len(values), dtype=bool))

    ax.plot(idx, values, "-", color=marker_color, linewidth=1.0, zorder=1)
    ax.scatter(idx[~alarm], values[~alarm], color=marker_color, s=25,
               zorder=2, label=label, **kw)
    if alarm.any():
        ax.scatter(idx[alarm], values[alarm], color=alarm_color, s=45,
                   marker="X", zorder=3, label="alarm", **kw)

    if center is None:
        center = float(np.median(values))
    ax.axhline(center, color="green", linewidth=1.0, linestyle="-",
               label="center")
    if ucl is not None:
        ax.axhline(float(ucl), color=alarm_color, linewidth=1.2,
                   linestyle="--", label="UCL")
    if lcl is not None:
        ax.axhline(lcl, color=alarm_color, linewidth=1.2, linestyle="--",
                   label="LCL")

    ax.set_xlabel("observation")
    ax.set_ylabel(label)
    ax.set_title(f"Control chart ({label})")
    ax.legend(loc="best", fontsize="small")
    return ax


# ---------------------------------------------------------------------------
# Tolerance band
# ---------------------------------------------------------------------------

def plot_tolerance_band(
    band: Dict[str, Any],
    fd=None,
    values=None,
    argvals=None,
    ax=None,
    band_color: str = "orange",
    band_alpha: float = 0.3,
    center_color: str = "darkorange",
    curve_color: str = "0.6",
    **kw,
):
    """Tolerance / prediction band, optionally over the underlying curves.

    Parameters
    ----------
    band : dict
        Result of a tolerance-band routine.  Expected keys: ``upper`` (m,),
        ``lower`` (m,) and optionally ``center`` (m,).
    fd, values : optional
        Underlying functional data to draw faintly beneath the band.
    argvals : array_like, optional
        Evaluation grid of length ``m``.  Inferred from ``fd`` or defaulted
        to an integer index.
    ax : matplotlib.axes.Axes, optional
    **kw
        Forwarded to the centre line ``Axes.plot`` call.

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _require_mpl()
    ax = _new_ax(ax, plt)

    upper = np.asarray(_get(band, "upper"), dtype=float).ravel()
    lower = np.asarray(_get(band, "lower"), dtype=float).ravel()
    center = band.get("center")
    m = len(upper)

    names = {"main": "", "xlab": "t", "ylab": "X(t)"}
    if fd is not None or values is not None:
        argvals_fd, vals, names = _coerce(fd, values)
        if argvals is None:
            argvals = argvals_fd
        for row in vals:
            ax.plot(argvals, row, color=curve_color, alpha=0.3,
                    linewidth=0.6, zorder=1)

    if argvals is None:
        argvals = np.arange(m, dtype=float)
    else:
        argvals = np.asarray(argvals, dtype=float).ravel()

    ax.fill_between(argvals, lower, upper, color=band_color, alpha=band_alpha,
                    label="tolerance band", zorder=2)
    ax.plot(argvals, upper, color=band_color, linewidth=1.0, zorder=3)
    ax.plot(argvals, lower, color=band_color, linewidth=1.0, zorder=3)
    if center is not None:
        ax.plot(argvals, np.asarray(center, dtype=float).ravel(),
                color=center_color, linewidth=2.0, label="center",
                zorder=4, **kw)

    _apply_labels(ax, names, main="Tolerance band")
    ax.legend(loc="best", fontsize="small")
    return ax
