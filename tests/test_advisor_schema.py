"""Tests for fdars.advisor._schema — schema types + backward compat (Plan 53-01, Task 1).

Covers:
  - TuneProposal, TuningStep, TuningTrace, TuneResult importable from _schema
  - Recommendation.parameter_delta defaults to None; existing five-field construction unchanged
  - All four new types JSON-serialisable via their field dicts under both pydantic and fallback

No API key required.  No network.
"""

from __future__ import annotations

import json


# ---------------------------------------------------------------------------
# Importability guard (runs at collection time under both pydantic and fallback)
# ---------------------------------------------------------------------------

from fdars.advisor._schema import (
    Advice,
    Recommendation,
    TuneProposal,
    TuneResult,
    TuningStep,
    TuningTrace,
)


# ---------------------------------------------------------------------------
# Test: Recommendation.parameter_delta defaults to None (backward compat)
# ---------------------------------------------------------------------------


def test_recommendation_parameter_delta_optional():
    """Constructing Recommendation with original five fields leaves parameter_delta as None."""
    rec = Recommendation(
        action="increase n_basis",
        kind="parameter",
        rationale="GCV is high",
        expected_effect="should decrease",
        evidence=["optimal_gcv=0.042"],
    )
    assert rec.parameter_delta is None
    assert rec.action == "increase n_basis"
    assert rec.kind == "parameter"


def test_recommendation_parameter_delta_can_be_set():
    """parameter_delta can be set to a TuneProposal on Recommendation."""
    proposal = TuneProposal(
        param="n_basis",
        new_value=20.0,
        rationale="GCV suggests over-smoothing",
    )
    rec = Recommendation(
        action="increase n_basis to 20",
        kind="parameter",
        rationale="GCV is high",
        expected_effect="should decrease",
        evidence=["optimal_gcv=0.042"],
        parameter_delta=proposal,
    )
    assert rec.parameter_delta is not None
    assert rec.parameter_delta.new_value == 20.0
    assert rec.parameter_delta.param == "n_basis"


# ---------------------------------------------------------------------------
# Test: TuneProposal fields
# ---------------------------------------------------------------------------


def test_tune_proposal_fields():
    """TuneProposal has the required fields with correct values."""
    proposal = TuneProposal(
        param="n_basis",
        new_value=20.0,
        rationale="GCV suggests over-smoothing",
    )
    assert proposal.param == "n_basis"
    assert proposal.new_value == 20.0
    assert proposal.rationale == "GCV suggests over-smoothing"


# ---------------------------------------------------------------------------
# Test: TuningStep fields
# ---------------------------------------------------------------------------


def test_tuning_step_fields():
    """TuningStep has all required fields with correct defaults."""
    step = TuningStep(
        step=0,
        param_before=15.0,
        param_after=20.0,
        target_before=0.05,
        target_after=0.03,
        accepted=True,
        stop_reason=None,
        guard_violations=[],
        proposal_source="mock",
    )
    assert step.step == 0
    assert step.param_before == 15.0
    assert step.param_after == 20.0
    assert step.target_before == 0.05
    assert step.target_after == 0.03
    assert step.accepted is True
    assert step.stop_reason is None
    assert step.guard_violations == []
    assert step.proposal_source == "mock"


# ---------------------------------------------------------------------------
# Test: TuningTrace JSON-serialisable with nested TuningStep
# ---------------------------------------------------------------------------


def test_tune_schema_json_serialisable():
    """A TuningTrace containing one TuningStep is JSON-serialisable."""
    step = TuningStep(
        step=0,
        param_before=15.0,
        param_after=20.0,
        target_before=0.05,
        target_after=0.03,
        accepted=True,
        stop_reason=None,
        guard_violations=[],
        proposal_source="mock",
    )
    trace = TuningTrace(
        method="smoothing",
        param="n_basis",
        target_metric="optimal_gcv",
        target_direction="lower",
        steps=[step],
        final_params={"n_basis": 20},
        final_diagnostics={"optimal_gcv": 0.03},
        converged=False,
        stop_reason="budget",
        n_steps=1,
        steps_used=1,
        budget_remaining=9,
    )
    # Build the field dict for JSON serialisation
    try:
        from pydantic import BaseModel as _PydanticBaseModel
        if isinstance(trace, _PydanticBaseModel):
            d = trace.model_dump()
        else:
            raise TypeError("not pydantic")
    except (ImportError, TypeError):
        # Fallback: build the dict manually from the stand-in
        d = {
            "method": trace.method,
            "param": trace.param,
            "target_metric": trace.target_metric,
            "target_direction": trace.target_direction,
            "steps": [
                {
                    "step": s.step,
                    "param_before": s.param_before,
                    "param_after": s.param_after,
                    "target_before": s.target_before,
                    "target_after": s.target_after,
                    "accepted": s.accepted,
                    "stop_reason": s.stop_reason,
                    "guard_violations": s.guard_violations,
                    "proposal_source": s.proposal_source,
                }
                for s in trace.steps
            ],
            "final_params": trace.final_params,
            "final_diagnostics": trace.final_diagnostics,
            "converged": trace.converged,
            "stop_reason": trace.stop_reason,
            "n_steps": trace.n_steps,
            "steps_used": trace.steps_used,
            "budget_remaining": trace.budget_remaining,
        }
    encoded = json.dumps(d)
    assert isinstance(encoded, str)
    decoded = json.loads(encoded)
    assert decoded["method"] == "smoothing"
    assert decoded["n_steps"] == 1
    assert len(decoded["steps"]) == 1


# ---------------------------------------------------------------------------
# Test: TuneResult fields
# ---------------------------------------------------------------------------


def test_tune_result_fields():
    """TuneResult has required fields."""
    step = TuningStep(
        step=0,
        param_before=15.0,
        param_after=20.0,
        target_before=0.05,
        target_after=0.03,
        accepted=True,
        stop_reason="budget",
        guard_violations=[],
        proposal_source="mock",
    )
    trace = TuningTrace(
        method="smoothing",
        param="n_basis",
        target_metric="optimal_gcv",
        target_direction="lower",
        steps=[step],
        final_params={"n_basis": 20},
        final_diagnostics={"optimal_gcv": 0.03},
        converged=False,
        stop_reason="budget",
        n_steps=1,
        steps_used=1,
        budget_remaining=9,
    )
    result = TuneResult(
        trace=trace,
        improved=True,
        initial_target_value=0.05,
        final_target_value=0.03,
        improvement_pct=40.0,
    )
    assert result.improved is True
    assert result.initial_target_value == 0.05
    assert result.final_target_value == 0.03
    assert result.improvement_pct == 40.0


# ---------------------------------------------------------------------------
# Test: Existing Advice + Recommendation construction is unchanged
# ---------------------------------------------------------------------------


def test_advice_construction_unchanged():
    """Existing Advice/Recommendation five-field construction still works."""
    rec = Recommendation(
        action="try higher k",
        kind="parameter",
        rationale="low separation",
        expected_effect="should improve",
        evidence=["mean_amplitude_separation=0.31"],
    )
    advice = Advice(
        interpretation="Clustering appears under-separated.",
        recommendations=[rec],
        caveats=["Dataset is small."],
    )
    assert len(advice.recommendations) == 1
    assert advice.recommendations[0].parameter_delta is None
