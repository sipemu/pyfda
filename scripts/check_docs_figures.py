#!/usr/bin/env python3
"""Fail if any build-time figure block errored during the docs build.

markdown-exec renders a Python traceback *in place* when an exec block raises,
without failing `mkdocs build` — so a broken figure (e.g. a missing dependency)
ships silently. This scans the built site for those tracebacks and exits non-zero,
listing the offending pages, so CI blocks the deploy instead of shipping broken
figures.

Usage:  python scripts/check_docs_figures.py <built-site-dir>
"""
from __future__ import annotations
import glob, os, re, sys

MARKERS = (
    "Traceback (most recent call last)",
    "ModuleNotFoundError",
    'class="exec-error"',
)


def main(site_dir: str) -> int:
    bad = []
    for html in glob.glob(os.path.join(site_dir, "**", "index.html"), recursive=True):
        txt = open(html, encoding="utf-8", errors="replace").read()
        hits = [m for m in MARKERS if m in txt]
        if hits:
            rel = os.path.relpath(os.path.dirname(html), site_dir)
            bad.append((rel, hits))
    if bad:
        print("FAILED: build-time figure error(s) detected:", file=sys.stderr)
        for rel, hits in bad:
            print(f"  {rel}  ({', '.join(hits)})", file=sys.stderr)
        return 1
    print(f"OK: no failed figure blocks in {site_dir}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
