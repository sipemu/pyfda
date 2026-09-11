"""mkdocs build hooks.

Adds ``scripts/`` to ``sys.path`` so build-time ``markdown-exec`` code blocks
can ``from docs_fig import fig, render`` for consistent inline SVG figures.
"""
from __future__ import annotations

import os
import sys

_SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
# NOTE: some mkdocs/markdown-exec setups execute code blocks with a sys.path
# that does not retain this insert, so the canonical mechanism is the
# `PYTHONPATH=scripts` env var (see the Makefile and docs.yml workflow). This
# hook is a best-effort fallback for `mkdocs serve` / local runs.
