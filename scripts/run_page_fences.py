#!/usr/bin/env python
"""Per-page offline fence verifier for the docs depth phases.

Extracts every ```python fence with exec="..." from the given markdown page,
runs each fence body under the current interpreter with PYTHONPATH=scripts and
DOCS_FAST=1, and asserts each prints the FDARS_FENCE_OK sentinel.

Usage (from repo root, under .venv):
    PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py <page.md>

Exit 0 iff at least one exec fence ran and every exec fence emitted the sentinel.
This is the phase-local, fence-level accuracy gate. The whole-site
`mkdocs build --strict` sweep is deferred to the milestone close gate (Phase 79).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SENTINEL = "FDARS_FENCE_OK"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: run_page_fences.py <page.md>", file=sys.stderr)
        return 2
    page = Path(argv[1])
    src = page.read_text()
    fences = re.findall(r"```python([^\n]*)\n(.*?)```", src, re.S)
    run = [body for info, body in fences if "exec=" in info]
    if not run:
        print(f"NO EXEC FENCES in {page}", file=sys.stderr)
        return 1
    env = dict(os.environ)
    env.setdefault("PYTHONPATH", "scripts")
    env.setdefault("DOCS_FAST", "1")
    env.setdefault("MPLBACKEND", "Agg")
    ok = 0
    for i, body in enumerate(run):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write(body)
            path = fh.name
        proc = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, env=env
        )
        os.unlink(path)
        if proc.returncode != 0 or SENTINEL not in proc.stdout:
            print(f"FENCE {i} FAILED in {page} (rc={proc.returncode})", file=sys.stderr)
            print(proc.stderr[-1800:], file=sys.stderr)
            return 1
        ok += 1
    print(f"ALL {ok} EXEC FENCES EMITTED {SENTINEL} in {page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
