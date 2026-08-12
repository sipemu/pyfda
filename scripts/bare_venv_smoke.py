"""Bare-venv smoke test for fdars (QUAL-04).

Proves that the base package (no provider extras) can:
  1. import fdars
  2. from fdars import advisor
  3. run an offline build_diagnostics call (represent aspect) and json.dumps the result
  4. raise an actionable ImportError (naming "pip install fdars[") when a provider
     whose extra is absent is requested

Runnable locally AND wired as the scripts/bare_venv_smoke.py step in the
``smoke-bare-venv`` CI job.  Exit code 0 = all checks passed; exit code 1 = a
check failed (message explains which).
"""

from __future__ import annotations

import json
import sys

import numpy as np


def main() -> int:
    # ------------------------------------------------------------------
    # Check 1: import fdars
    # ------------------------------------------------------------------
    try:
        import fdars  # noqa: F401
    except ImportError as exc:
        print(f"FAIL [check 1]: import fdars raised ImportError: {exc}")
        return 1

    # ------------------------------------------------------------------
    # Check 2: from fdars import advisor (importable with no provider SDK)
    # ------------------------------------------------------------------
    try:
        from fdars import advisor
    except ImportError as exc:
        print(f"FAIL [check 2]: from fdars import advisor raised ImportError: {exc}")
        return 1

    # ------------------------------------------------------------------
    # Check 3: offline build_diagnostics (represent) + json.dumps
    # ------------------------------------------------------------------
    data = np.ones((20, 50))
    argvals = np.linspace(0, 1, 50)
    try:
        result = advisor.build_diagnostics(
            {"data": data, "argvals": argvals}, method="represent"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL [check 3]: build_diagnostics raised {type(exc).__name__}: {exc}")
        return 1

    if not isinstance(result, dict):
        print(f"FAIL [check 3]: build_diagnostics returned {type(result)}, expected dict")
        return 1

    try:
        json.dumps(result, sort_keys=True)
    except (TypeError, ValueError) as exc:
        print(f"FAIL [check 3]: json.dumps(result) raised {type(exc).__name__}: {exc}")
        return 1

    # ------------------------------------------------------------------
    # Check 4: missing-provider raises ImportError naming "pip install fdars["
    # ------------------------------------------------------------------
    try:
        advisor.advise(result, task="interpretation", domain_context="smoke", provider="openai")
        print("FAIL [check 4]: expected ImportError from missing openai extra, but no exception raised")
        return 1
    except ImportError as exc:
        msg = str(exc)
        if "pip install fdars[" not in msg:
            print(
                f"FAIL [check 4]: ImportError raised but message does not contain "
                f"'pip install fdars[': {msg!r}"
            )
            return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL [check 4]: expected ImportError, got {type(exc).__name__}: {exc}")
        return 1

    print("PASS: fdars base-package smoke (import, advisor, build_diagnostics, missing-provider ImportError)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
