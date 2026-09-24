"""Drift gate for the machine-generated case-study number macros.

Recomputes every number quoted in the four case studies (running each
``casestudyN.main(check=True)``, which skips figure output) and fails if any
committed ``paper/sections/generated/csN_numbers.tex`` differs.

Usage::

    PYTHONPATH=scripts:paper/code python paper/code/check_cs_numbers.py
"""
from __future__ import annotations

import sys

import casestudy1
import casestudy2
import casestudy3
import casestudy4


def main() -> int:
    status = 0
    for mod in (casestudy1, casestudy2, casestudy3, casestudy4):
        status |= int(mod.main(check=True) or 0)
    if status:
        print("check_cs_numbers: FAILED (stale case-study numbers)",
              file=sys.stderr)
    else:
        print("check_cs_numbers: OK (no drift)")
    return status


if __name__ == "__main__":
    sys.exit(main())
