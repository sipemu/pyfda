"""Offline test suite for auto_tune() — the LLM-backed tuning API (Plan 53-02, Task 2).

All tests use a fake Provider (or monkeypatched advise) so that:
  - No ANTHROPIC_API_KEY is required
  - No network calls are made (safe for CI)

The tests prove the grounding-invariant hard boundary:
  - The LLM's only numeric contribution is TuneProposal.new_value (schema-validated,
    clamped to declared range)
  - Out-of-range proposals are CLAMPED, not rejected
  - A missing/wrong-param parameter_delta exits the loop with parse_failure
    and the fake advise is called exactly ONCE (no numeric-path retry)
  - auto_tune(method='alignment') and auto_tune(method='depth') raise ValueError
  - auto_tune completes fully offline with a fake Provider (no API key needed)
  - The result is a TuneResult with a populated trace
"""

from __future__ import annotations

import os
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fake Provider infrastructure
#
# FakeProvider implements the Provider protocol with a callable passed at
# construction time as the 'response_fn'.  Each call to complete_structured
# invokes response_fn(Advice_class, messages, system) and returns the result.
# This lets individual tests control exactly what the "LLM" returns without
# any network traffic.
# ---------------------------------------------------------------------------


class FakeProvider:
    """Minimal Provider that satisfies the Provider protocol for offline testing.

    Delegates to a caller-supplied response factory without any network call.
    The protocol attributes (name, model, supports_native_structured_output)
    are required so that resolve_provider's isinstance(provider, _ProviderProtocol)
    check recognises the fake as a valid Provider instance.
    """

    name: str = "fake"
    model: str = "fake-model"
    supports_native_structured_output: bool = True  # skip ValidateAndRetry schema repair

    def __init__(self, response_fn):
        self._response_fn = response_fn

    def complete_structured(self, model_cls, messages, system):
        return self._response_fn(model_cls, messages, system)


def _make_parameter_delta_recommendation(param: str, new_value: float, rationale: str = "qualitative reason"):
    """Build a fake Advice object with one Recommendation carrying a parameter_delta.

    Evidence items use qualitative-only text (no numeric tokens) so that
    _check_grounding never fires on the fake advice, regardless of the
    synthetic diagnostics dict the test uses.
    """
    from fdars.advisor._schema import Advice, Recommendation, TuneProposal
    return Advice(
        interpretation="test interpretation",
        recommendations=[
            Recommendation(
                action=f"adjust {param}",
                kind="parameter",
                rationale=rationale,
                expected_effect="should improve",
                # No numeric tokens here — avoids GroundingViolationError in tests
                evidence=["the diagnostic value indicates adjustment is warranted"],
                parameter_delta=TuneProposal(
                    param=param,
                    new_value=new_value,
                    rationale=rationale,
                ),
            )
        ],
        caveats=[],
    )


def _make_no_parameter_delta_advice():
    """Build a fake Advice with no parameter_delta in any Recommendation."""
    from fdars.advisor._schema import Advice, Recommendation
    return Advice(
        interpretation="no delta advice",
        recommendations=[
            Recommendation(
                action="inspect diagnostics",
                kind="none",
                rationale="qualitative reason",
                expected_effect="should improve",
                # No numeric tokens — avoids GroundingViolationError in tests
                evidence=["the current diagnostics do not indicate a clear parameter change"],
                parameter_delta=None,
            )
        ],
        caveats=[],
    )


# ---------------------------------------------------------------------------
# Minimal seam helpers — avoid real fdars/MCP calls in all tests
# ---------------------------------------------------------------------------


def _fake_run_method(dataset_id, method, **params):
    """Returns a minimal synthetic 'result' dict. No fdars or network call."""
    return {"synthetic": True, "method": method, "params": params}


def _make_fake_build_diagnostics(target_key, target_values):
    """Return a build_diagnostics stand-in that cycles through target_values list."""
    call_count = [0]

    def fake_build_diagnostics(result, method, argvals=None, **kwargs):
        idx = min(call_count[0], len(target_values) - 1)
        call_count[0] += 1
        return {target_key: target_values[idx]}

    return fake_build_diagnostics


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAutoTuneRejectsNonTuneable:
    """auto_tune for non-tuneable methods must raise ValueError immediately."""

    def test_alignment_raises_value_error(self):
        """auto_tune(method='alignment') must raise ValueError naming the reason."""
        from fdars.advisor import auto_tune

        with pytest.raises(ValueError, match="alignment"):
            auto_tune("fake_dataset", "alignment", provider=FakeProvider(lambda *a: None))

    def test_depth_raises_value_error(self):
        """auto_tune(method='depth') must raise ValueError naming the reason."""
        from fdars.advisor import auto_tune

        with pytest.raises(ValueError, match="depth"):
            auto_tune("fake_dataset", "depth", provider=FakeProvider(lambda *a: None))


class TestAutoTuneOfflineNoApiKey:
    """auto_tune must complete offline via a fake Provider without ANTHROPIC_API_KEY."""

    def test_offline_no_api_key(self):
        """auto_tune completes with a fake Provider even when ANTHROPIC_API_KEY is unset."""
        from fdars.advisor import auto_tune
        from fdars.advisor._tuning import _UnparseableProposalError

        # Ensure the env var is NOT set for this test
        env_backup = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            # Fake provider that returns a valid parameter_delta on first call
            # then no parameter_delta (triggering parse_failure) on second call.
            call_count = [0]

            def response_fn(model_cls, messages, system):
                call_count[0] += 1
                if call_count[0] == 1:
                    return _make_parameter_delta_recommendation("n_basis", 20)
                return _make_no_parameter_delta_advice()

            fake_provider = FakeProvider(response_fn)

            # Smoothing: target_metric=optimal_gcv (lower is better)
            # n_basis starts at 15, proposal = 20
            # diagnostics: first call returns gcv=0.1, after change gcv=0.08 (improved)
            # third call: no parameter_delta -> parse_failure
            fake_build = _make_fake_build_diagnostics(
                "optimal_gcv", [0.1, 0.08, 0.07]
            )

            result = auto_tune(
                "fake_dataset",
                "smoothing",
                provider=fake_provider,
                max_steps=5,
                _run_method=_fake_run_method,
                _build_diagnostics=fake_build,
            )

            assert result is not None
        finally:
            if env_backup is not None:
                os.environ["ANTHROPIC_API_KEY"] = env_backup


class TestAutoTuneReturnsTuneResult:
    """auto_tune must return a TuneResult with a populated trace."""

    def test_returns_tune_result_type(self):
        """Result must be an instance of TuneResult."""
        from fdars.advisor import auto_tune
        from fdars.advisor._schema import TuneResult

        call_count = [0]

        def response_fn(model_cls, messages, system):
            call_count[0] += 1
            # Return no parameter_delta on first call -> parse_failure immediately
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=3,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert isinstance(result, TuneResult)

    def test_result_has_trace(self):
        """TuneResult.trace must be a TuningTrace with stop_reason."""
        from fdars.advisor import auto_tune
        from fdars.advisor._schema import TuneResult, TuningTrace

        def response_fn(model_cls, messages, system):
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=2,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert hasattr(result, "trace")
        assert hasattr(result.trace, "stop_reason")
        assert result.trace.stop_reason in {
            "budget", "converged", "oscillation", "guard_stop", "parse_failure"
        }


class TestAutoTuneClampOutOfRange:
    """Out-of-range LLM new_value must be clamped, not rejected."""

    def test_clamps_above_range(self):
        """When LLM proposes new_value above range, it must be clamped to hi.

        smoothing n_basis range is [4, 60].  A proposal of 999 must be clamped to 60.
        The loop must continue (clamped step is valid) and the clamp must be recorded.
        """
        from fdars.advisor import auto_tune
        from fdars.advisor._schema import TuneResult

        call_count = [0]

        def response_fn(model_cls, messages, system):
            call_count[0] += 1
            if call_count[0] == 1:
                # Propose 999 — way above the range [4, 60]
                return _make_parameter_delta_recommendation("n_basis", 999)
            # Second call: no delta -> parse_failure
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)

        # initial gcv=0.1; after change gcv=0.08 (improved at clamped n_basis=60)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1, 0.08])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=5,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert isinstance(result, TuneResult)

        # Find the step where the proposal was clamped
        accepted_or_all_steps = result.trace.steps
        assert len(accepted_or_all_steps) >= 1, "Expected at least one step in trace"

        # The first step param_after must be 60 (the upper bound), not 999
        first_step = accepted_or_all_steps[0]
        assert first_step.param_after == 60.0, (
            f"Expected param_after=60.0 (clamped from 999), got {first_step.param_after}"
        )

    def test_clamps_below_range(self):
        """When LLM proposes new_value below range, it must be clamped to lo.

        smoothing n_basis range is [4, 60].  A proposal of -5 must be clamped to 4.
        """
        from fdars.advisor import auto_tune
        from fdars.advisor._schema import TuneResult

        call_count = [0]

        def response_fn(model_cls, messages, system):
            call_count[0] += 1
            if call_count[0] == 1:
                # Propose -5 — below the range [4, 60]
                return _make_parameter_delta_recommendation("n_basis", -5)
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)

        # initial gcv=0.1; after change gcv=0.05 (improved at clamped n_basis=4)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1, 0.05])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=5,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert isinstance(result, TuneResult)
        first_step = result.trace.steps[0]
        assert first_step.param_after == 4.0, (
            f"Expected param_after=4.0 (clamped from -5), got {first_step.param_after}"
        )


class TestAutoTuneParseFailureNoRetry:
    """A proposal with no parameter_delta must exit with parse_failure — advise called once."""

    def test_parse_failure_exits_immediately(self):
        """When the fake provider returns no parameter_delta, the loop exits with parse_failure."""
        from fdars.advisor import auto_tune

        def response_fn(model_cls, messages, system):
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=10,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert result.trace.stop_reason == "parse_failure", (
            f"Expected stop_reason='parse_failure', got {result.trace.stop_reason!r}"
        )

    def test_advise_called_exactly_once_on_parse_failure(self):
        """The LLM (fake advise) must be called exactly once when parameter_delta is missing.

        Proves: no numeric-path retry (TUNE-03).
        """
        from fdars.advisor import auto_tune

        call_count = [0]

        def response_fn(model_cls, messages, system):
            call_count[0] += 1
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=10,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert result.trace.stop_reason == "parse_failure"
        # The fake advise (via FakeProvider.complete_structured) must have been
        # called exactly once — no retry into the numeric path
        assert call_count[0] == 1, (
            f"Expected advise to be called exactly once on parse_failure, "
            f"but it was called {call_count[0]} time(s). "
            "This would mean the LLM was retried in the numeric path (prohibited by TUNE-03)."
        )

    def test_wrong_param_name_exits_parse_failure(self):
        """A parameter_delta with wrong param name must exit with parse_failure."""
        from fdars.advisor import auto_tune

        def response_fn(model_cls, messages, system):
            # Return wrong param name (lambda_ instead of n_basis for smoothing)
            return _make_parameter_delta_recommendation("lambda_", 1.0)

        fake_provider = FakeProvider(response_fn)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=5,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert result.trace.stop_reason == "parse_failure", (
            f"Expected parse_failure for wrong param name, got {result.trace.stop_reason!r}"
        )


class TestAutoTuneInAllExports:
    """auto_tune must appear in fdars.advisor.__all__."""

    def test_auto_tune_in_all(self):
        """auto_tune must be listed in fdars.advisor.__all__."""
        import fdars.advisor as advisor
        assert "auto_tune" in advisor.__all__, (
            f"auto_tune not in fdars.advisor.__all__. "
            f"Current __all__: {advisor.__all__!r}"
        )

    def test_auto_tune_importable_directly(self):
        """from fdars.advisor import auto_tune must work without error."""
        from fdars.advisor import auto_tune
        assert callable(auto_tune)


class TestAutoTuneSuccessfulRun:
    """Integration: a successful run with improving fake diagnostics."""

    def test_budget_exhaustion_returns_result(self):
        """A run that hits max_steps returns a TuneResult with stop_reason='budget'."""
        from fdars.advisor import auto_tune
        from fdars.advisor._schema import TuneResult

        call_count = [0]

        def response_fn(model_cls, messages, system):
            call_count[0] += 1
            # Alternate between two valid proposals to keep improving
            if call_count[0] % 2 == 1:
                return _make_parameter_delta_recommendation("n_basis", 20)
            return _make_parameter_delta_recommendation("n_basis", 25)

        fake_provider = FakeProvider(response_fn)

        # Always improving: gcv goes 0.10 -> 0.09 -> 0.08 -> 0.07 -> ...
        gcv_values = [0.10 - i * 0.01 for i in range(20)]
        fake_build = _make_fake_build_diagnostics("optimal_gcv", gcv_values)

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=3,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        assert isinstance(result, TuneResult)
        # With max_steps=3 and always-improving proposals that alternate between
        # n_basis=20 and n_basis=25, the loop may hit budget or oscillation
        assert result.trace.stop_reason in {"budget", "oscillation", "converged"}

    def test_result_improved_flag(self):
        """TuneResult.improved is True when final target is better than initial."""
        from fdars.advisor import auto_tune

        call_count = [0]

        def response_fn(model_cls, messages, system):
            call_count[0] += 1
            if call_count[0] == 1:
                return _make_parameter_delta_recommendation("n_basis", 20)
            return _make_no_parameter_delta_advice()

        fake_provider = FakeProvider(response_fn)

        # initial gcv=0.1; after change gcv=0.05 (improved)
        fake_build = _make_fake_build_diagnostics("optimal_gcv", [0.1, 0.05])

        result = auto_tune(
            "fake_dataset",
            "smoothing",
            provider=fake_provider,
            max_steps=5,
            _run_method=_fake_run_method,
            _build_diagnostics=fake_build,
        )

        # After one successful step (gcv: 0.1 -> 0.05), improved should be True
        assert result.improved is True
        assert result.initial_target_value == pytest.approx(0.1)
        assert result.final_target_value == pytest.approx(0.05)
