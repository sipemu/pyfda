"""Tests for the 'parameter_proposal' system-prompt clause (Plan 53-02, Task 1).

TDD RED tests — all tests verify that:
  - _system_prompt('parameter_proposal') returns a non-empty prompt (does not raise)
  - the prompt mentions parameter_delta
  - the prompt contains an explicit no-numeric-prediction prohibition
  - all five prior task families still build without error

No API key required.  No network.
"""

from __future__ import annotations

import pytest

from fdars.advisor._prompts import _system_prompt


# ---------------------------------------------------------------------------
# parameter_proposal clause tests
# ---------------------------------------------------------------------------


def test_parameter_proposal_returns_prompt():
    """_system_prompt('parameter_proposal') must return a non-empty string."""
    p = _system_prompt("parameter_proposal")
    assert isinstance(p, str)
    assert len(p) > 100


def test_parameter_proposal_mentions_parameter_delta():
    """The clause must instruct the model to populate parameter_delta."""
    p = _system_prompt("parameter_proposal")
    assert "parameter_delta" in p


def test_parameter_proposal_no_numeric_prediction_prohibition():
    """The clause must forbid predicting the numeric value of the target metric."""
    p = _system_prompt("parameter_proposal")
    # The prohibition must use qualitative direction language
    # (should-decrease / should-increase / likely-to-improve or equivalent)
    prohibition_terms = [
        "qualitative",
        "do not predict",
        "must not predict",
        "no numeric",
        "should decrease",
        "should increase",
        "likely to improve",
    ]
    lower_p = p.lower()
    assert any(term in lower_p for term in prohibition_terms), (
        f"No no-numeric-prediction prohibition found in parameter_proposal clause. "
        f"Expected one of: {prohibition_terms}"
    )


def test_parameter_proposal_grounding_invariant_present():
    """The grounding invariant must be present in the parameter_proposal prompt."""
    from fdars.advisor._prompts import _GROUNDING_INVARIANT
    p = _system_prompt("parameter_proposal")
    assert _GROUNDING_INVARIANT in p


def test_parameter_proposal_case_insensitive():
    """_system_prompt should accept 'PARAMETER_PROPOSAL' and 'Parameter_Proposal'."""
    for variant in ("PARAMETER_PROPOSAL", "Parameter_Proposal", "parameter_proposal"):
        p = _system_prompt(variant)
        assert "parameter_delta" in p


# ---------------------------------------------------------------------------
# Regression: five prior task families unchanged
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("task", ["interpretation", "parameter", "method", "comparison", "pipeline"])
def test_prior_task_families_unchanged(task):
    """All five prior task families must still build without error."""
    p = _system_prompt(task)
    assert isinstance(p, str)
    assert len(p) > 50
