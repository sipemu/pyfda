"""Cross-implementation agreement table: fdars vs independent R implementations.

Recomputes six fdars methods live and compares them with frozen reference
outputs produced by established R packages (``paper/code/crossimpl_ref.R`` ->
``paper/code/crossimpl_ref/*.csv``; R is not needed here or in CI).  Writes
``paper/sections/crossimpl_table.tex``.

Numbers are rounded to a few significant figures so the table is stable across
platforms; a numerical change in fdars large enough to matter changes the table
and trips the ``--check`` drift gate.

Usage::

    python paper/code/crossimpl.py          # write the table
    python paper/code/crossimpl.py --check  # exit 1 if the committed table is stale
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from fdars import Fdata, alignment, depth, metric, pace_fpca

_HERE = Path(__file__).resolve().parent
_REF = _HERE / "crossimpl_ref"
_REPO = _HERE.parent.parent
_OUT = _HERE.parent / "sections" / "crossimpl_table.tex"


def _ver(pkg: str) -> str:
    v = pd.read_csv(_REF / "versions.csv")
    return str(v.loc[v["package"] == pkg, "version"].iloc[0])


def _sci(x: float) -> str:
    """Two-significant-figure scientific notation for LaTeX, with a floor."""
    if x < 1e-12:
        return r"$<10^{-12}$"
    m, e = f"{x:.1e}".split("e")
    return rf"${m}\times10^{{{int(e)}}}$"


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(abs(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _trapz_weights(t: np.ndarray) -> np.ndarray:
    w = np.zeros_like(t)
    d = np.diff(t)
    w[:-1] += d / 2
    w[1:] += d / 2
    return w


def _rows() -> list[tuple[str, str, str, str]]:
    g = pd.read_csv(_REPO / "docs" / "data" / "growth.csv")
    t = g["age"].to_numpy(dtype=np.float64)
    X = g.iloc[:, 1:].to_numpy(dtype=np.float64).T              # (93, 31)
    rows = []

    # 1. Fraiman-Muniz depth vs fda.usc::depth.FM.
    fm_r = pd.read_csv(_REF / "fm_depth.csv")["fm"].to_numpy()
    fm = np.asarray(depth.fraiman_muniz_1d(X, X, scale=True))
    rows.append((
        r"Fraiman--Muniz depth (growth, $n=93$)",
        rf"\texttt{{depth.fraiman\_muniz\_1d}} vs fda.usc~{_ver('fda.usc')} \texttt{{depth.FM}}",
        rf"max $|\Delta|$ {_sci(np.abs(fm - fm_r).max())}; $\rho={spearmanr(fm, fm_r)[0]:.3f}$",
        r"exact; fdars \texttt{scale=True} $\equiv$ fda.usc \texttt{scale=FALSE}",
    ))

    # 2. Modified band depth vs roahd::MBD.
    mbd_r = pd.read_csv(_REF / "mbd.csv")["mbd"].to_numpy()
    mbd = np.asarray(depth.modified_band_1d(X, X))
    rows.append((
        r"Modified band depth (growth)",
        rf"\texttt{{depth.modified\_band\_1d}} vs roahd~{_ver('roahd')} \texttt{{MBD}}",
        rf"$\rho={spearmanr(mbd, mbd_r)[0]:.3f}$; max $|\Delta|={np.abs(mbd - mbd_r).max():.3f}$",
        r"same ranking; small value differences",
    ))

    # 3. Dense FPCA vs fda.usc::fdata2pc.
    d_r = pd.read_csv(_REF / "fpca_d.csv")["d"].to_numpy()
    rot_r = pd.read_csv(_REF / "fpca_rotation.csv").to_numpy()
    pc = Fdata(X, argvals=t).to_pc(n_comp=4)
    rot = np.asarray(pc["rotation"])
    w = np.asarray(pc["weights"])
    sv_all = np.linalg.svd((X - X.mean(axis=0)) * np.sqrt(w), compute_uv=False)
    share_f = sv_all[0] ** 2 / np.sum(sv_all ** 2)
    share_r = d_r[0] ** 2 / np.sum(d_r ** 2)
    cosines = [_cos(rot[:, k], rot_r[:, k]) for k in range(4)]
    rows.append((
        r"Dense FPCA, 4 components (growth)",
        rf"\texttt{{Fdata.to\_pc}} vs fda.usc~{_ver('fda.usc')} \texttt{{fdata2pc}}",
        rf"eigenfunction $|\cos|$ {min(cosines):.3f}--{max(cosines):.3f}; "
        rf"PC1 share {100 * share_f:.1f}\% vs {100 * share_r:.1f}\%",
        r"quadrature weighting differs on the non-uniform grid",
    ))

    # 4. L2 distance matrix vs fda.usc::metric.lp, plus the explanation:
    #    fda.usc integrates with the trapezoid rule (reproduced exactly here).
    D_r = pd.read_csv(_REF / "l2_dist.csv").to_numpy()
    D = np.asarray(metric.lp_self_1d(X, t, p=2.0))
    off = ~np.eye(D.shape[0], dtype=bool)
    diff = X[:, None, :] - X[None, :, :]
    D_trap = np.sqrt(np.einsum("ijk,k->ij", diff ** 2, _trapz_weights(t)))
    rows.append((
        r"$L^2$ distance matrix (growth)",
        rf"\texttt{{metric.lp\_self\_1d}} vs fda.usc~{_ver('fda.usc')} \texttt{{metric.lp}}",
        rf"max rel.\ diff.\ {100 * np.max(np.abs(D - D_r)[off] / D_r[off]):.1f}\%",
        rf"reference $=$ trapezoid rule (reproduced to "
        rf"{_sci(np.max(np.abs(D_trap - D_r)[off] / D_r[off]))}); fdars' rule is "
        r"exact for quadratics on this grid",
    ))

    # 5. Elastic Karcher mean vs fdasrvf::time_warping (synthetic bumps).
    B = pd.read_csv(_REF / "karcher_input.csv").to_numpy()
    km_r = pd.read_csv(_REF / "karcher_mean.csv")
    tt = km_r["t"].to_numpy()
    fmean_r = km_r["fmean"].to_numpy()
    fmean = np.asarray(alignment.karcher_mean(B, tt, max_iter=20)["mean"])
    rel = np.sqrt(np.trapezoid((fmean - fmean_r) ** 2, tt)
                  / np.trapezoid(fmean_r ** 2, tt))
    rows.append((
        r"Elastic Karcher mean (20 phase-shifted bumps)",
        rf"\texttt{{alignment.karcher\_mean}} vs fdasrvf~{_ver('fdasrvf')} \texttt{{time\_warping}}",
        rf"rel.\ $L^2$ diff.\ {100 * rel:.1f}\%; peak {fmean.max():.3f} vs {fmean_r.max():.3f}",
        rf"cross-sectional mean peak is {B.mean(axis=0).max():.3f}",
    ))

    # 6. PACE sparse FPCA vs fdapace::FPCA (synthetic sparse trajectories).
    L = pd.read_csv(_REF / "pace_input.csv")
    fit = pd.read_csv(_REF / "pace_fit.csv")
    lam_r = pd.read_csv(_REF / "pace_lambda.csv")["lambda"].to_numpy()
    grid = fit["t"].to_numpy()
    ids = sorted(L["id"].unique())
    irr = pace_fpca.irreg_fdata_from_lists(
        [L.loc[L["id"] == i, "t"].to_numpy() for i in ids],
        [L.loc[L["id"] == i, "y"].to_numpy() for i in ids])
    res = pace_fpca.pace_fpca(irr, ncomp=2, bandwidth=0.1, work_grid=grid)
    ef = np.asarray(res["eigenfunctions"])
    lam = np.asarray(res["eigenvalues"])
    pc_cos = [_cos(ef[:, k], fit[f"phi{k + 1}"].to_numpy()) for k in range(2)]
    rows.append((
        r"PACE sparse FPCA (120 curves, 4--8 obs.\ each)",
        rf"\texttt{{pace\_fpca.pace\_fpca}} vs fdapace~{_ver('fdapace')} \texttt{{FPCA}}",
        rf"eigenfunction $|\cos|$ {pc_cos[0]:.3f}, {pc_cos[1]:.3f}; "
        rf"$\hat\lambda=({lam[0]:.2f}, {lam[1]:.2f})$ vs $({lam_r[0]:.2f}, {lam_r[1]:.2f})$",
        r"true $\lambda=(4, 1)$; same Gaussian kernel and bandwidth, but fdars "
        r"smooths local-constant, fdapace local-linear",
    ))
    return rows


def _render(rows: list[tuple[str, str, str, str]]) -> str:
    body = "\n".join(
        rf"{m} & {c} & {a} & {n} \\" + ("\n\\addlinespace" if i < len(rows) - 1 else "")
        for i, (m, c, a, n) in enumerate(rows))
    return (
        "% Auto-generated by paper/code/crossimpl.py -- do not edit.\n"
        "% References: paper/code/crossimpl_ref/ (produced by crossimpl_ref.R).\n"
        "\\begin{table}[htbp]\n\\centering\n\\footnotesize\n"
        "\\caption{Numerical agreement between \\texttt{fdars} and independent R "
        "implementations. fdars is recomputed on every CI run against frozen "
        "reference outputs; $\\rho$ is Spearman rank correlation.}\n"
        "\\label{tab:crossimpl}\n"
        "\\begin{tabular}{*{4}{>{\\raggedright\\arraybackslash}p{0.22\\linewidth}}}\n"
        "\\toprule\n\\textbf{Method (data)} & \\textbf{fdars vs reference} & "
        "\\textbf{Agreement} & \\textbf{Remark} \\\\\n\\midrule\n"
        f"{body}\n\\bottomrule\n\\end{{tabular}}\n\\end{{table}}\n")


def main() -> None:
    content = _render(_rows())
    if "--check" in sys.argv:
        if not _OUT.exists() or _OUT.read_text() != content:
            print(f"DRIFT: {_OUT} is stale -- re-run crossimpl.py and commit.",
                  file=sys.stderr)
            sys.exit(1)
        print("crossimpl: OK (no drift)")
        return
    _OUT.write_text(content)
    print(f"Written {_OUT}")


if __name__ == "__main__":
    main()
