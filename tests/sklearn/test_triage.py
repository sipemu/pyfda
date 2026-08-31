"""Compliance triage harness for Phase 55.

Run the full triage for FPCATransformer with::

    pytest tests/sklearn/test_triage.py -v --tb=short 2>&1 | tee triage_results.txt

Then review triage_results.txt to assign PASS / PASS-WITH-FIXES / EXCLUDE
verdicts and populate ``_coverage.TRIAGE_VERDICTS`` accordingly.

Verdict assignment rule
-----------------------
All checks PASS
    -> PASS

Checks fail only due to fixable guards (1-sample message, float cast, etc.)
    -> PASS-WITH-FIXES: list the specific fixes required

Checks fail due to structural incompatibility (algorithm requirements, wrong
output shape, requires IrregFdata input, etc.)
    -> EXCLUDE: record in EXCLUDED_METHODS with failing_check name

Plan scope
----------
This file (Plan 01) seeds the harness with ONLY ``FPCATransformer(n_components=1)``.
Plan 02 expands ``_ALL_SKELETONS`` to all ~30 candidate classes once the
foundational tracer is confirmed PASS.
"""

from __future__ import annotations

import pytest
from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import FPCATransformer


# ---------------------------------------------------------------------------
# Estimator list — Plan 01: FPCATransformer tracer only
# ---------------------------------------------------------------------------
# Plan 02 extends this list with the remaining ~30 candidates.
_ALL_SKELETONS = [
    FPCATransformer(n_components=1),
]


# ---------------------------------------------------------------------------
# Triage harness
# ---------------------------------------------------------------------------

@parametrize_with_checks(_ALL_SKELETONS)
def test_sklearn_triage(estimator, check):
    """Run each parametrize_with_checks case as an independent test.

    A PASS confirms the estimator is fully sklearn-compliant for that check.
    A FAIL is informative: record the failing check name in TRIAGE_VERDICTS
    and classify as PASS-WITH-FIXES (if fixable) or EXCLUDE (structural).

    This harness surfaces ALL failing checks independently so no single
    failure masks others -- contrast with check_estimator() which aborts at
    the first failure.
    """
    check(estimator)
