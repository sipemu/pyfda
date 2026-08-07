"""pytest-markdown-docs globals for fdars documentation fences.

Injects ``np``, ``plt``, and ``fdars`` into every markdown code fence executed
by ``pytest-markdown-docs`` (FND-05, D-06). The example exec blocks still
perform their own imports explicitly (self-documenting build-time figures);
these globals are a fallback so isolated fences don't fail on a bare ``np``.

``matplotlib.use("Agg")`` MUST precede ``import matplotlib.pyplot as plt`` --
CI has no display, so the non-interactive backend must be selected before
pyplot binds a backend. Same ordering as ``scripts/docs_fig.py`` (lines 37-40).

Note: ``docs_fig`` / ``docs_data`` are NOT injected here. Those resolve via
``PYTHONPATH=scripts`` (set by the CI Gate B step and by local smoke-test runs).
"""
import matplotlib

matplotlib.use("Agg")  # non-interactive backend; must precede the pyplot import
import matplotlib.pyplot as plt  # noqa: E402

import numpy as np  # noqa: E402
import fdars  # noqa: E402


def pytest_markdown_docs_globals():
    """Return globals injected into every markdown code fence during testing."""
    return {"np": np, "plt": plt, "fdars": fdars}
