"""Paper figure generation pipeline.

Run this script to regenerate all paper figures deterministically::

    PYTHONPATH=scripts:paper/code python paper/code/gen_figures.py

Or via the Makefile::

    make paper-figures

Each figure function seeds the RNG with a fixed integer before any stochastic
draw so that consecutive runs produce byte-identical PDF output.  Additional
figure functions added in Phases 88/89 append to ``main()`` here.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from paper_utils import fig, save_figure, style_setup, clean_ax, brand_legend
import casestudy1
import gen_tour_figures

# Output directory — relative to this file so the script is location-independent.
_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def _smoke() -> None:
    """Smoke-test figure — seeded random walk proving the determinism gate.

    Seeds the RNG before any stochastic draw; writes a deterministic PDF to
    paper/figures/smoke.pdf (per PIPE-02).
    """
    rng = np.random.default_rng(20260908)
    y = rng.standard_normal(50).cumsum()
    x = np.arange(len(y))

    f, ax = fig()
    ax.plot(x, y, label="Random walk")
    ax.set_title("Smoke test — deterministic random walk")
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative value")
    clean_ax(ax, frame=True)
    brand_legend(ax)

    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    save_figure(f, _FIGURES_DIR / "smoke.pdf")


def main() -> None:
    """Regenerate all paper figures."""
    style_setup()
    _smoke()
    casestudy1.main()
    # Studies 2-4: imported directly so any ImportError or runtime failure
    # surfaces as a hard error (no silent swallow — WR-02).
    import casestudy2
    casestudy2.main()
    import casestudy3
    casestudy3.main()
    import casestudy4
    casestudy4.main()
    # Capability-tour figures (Section 4): one per method family. Imported at
    # module top so any ImportError/runtime failure is a hard error (WR-02).
    gen_tour_figures.main()


if __name__ == "__main__":
    main()
