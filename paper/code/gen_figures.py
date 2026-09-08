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

from paper_utils import fig, save_figure

# Output directory — relative to this file so the script is location-independent.
_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def _smoke() -> None:
    """Smoke-test figure — seeded random walk proving the determinism gate.

    Seeds the RNG before any stochastic draw; writes a deterministic PDF to
    paper/figures/smoke.pdf (per PIPE-02).
    """
    np.random.seed(20260908)
    y = np.random.randn(50).cumsum()
    x = np.arange(len(y))

    f, ax = fig()
    ax.plot(x, y)
    ax.set_title("Smoke test — deterministic random walk")
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative value")

    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    save_figure(f, _FIGURES_DIR / "smoke.pdf")


def main() -> None:
    """Regenerate all paper figures."""
    _smoke()
    # Phases 88/89 append additional figure calls here.


if __name__ == "__main__":
    main()
