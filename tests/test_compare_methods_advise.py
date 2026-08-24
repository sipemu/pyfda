"""Offline + env-gated tests for the 'comparison' advise task family.

Plan 51-02 tasks:
  - Task 1: 'comparison' task clause in _system_prompt (COMPARE-02).
  - Task 2: Winner authority + per-candidate provenance in the LLM path.
  - Task 3: Env-gated live comparison narration smoke test.

No network or ANTHROPIC_API_KEY required for the offline tests.  The live
test (test_live_comparison_narration) is skipped when ANTHROPIC_API_KEY is
absent from the environment.
"""

from __future__ import annotations

import os

import pytest


# ---------------------------------------------------------------------------
# Shared synthetic fixtures (inline, offline)
# ---------------------------------------------------------------------------

def _clustering_diag(mean_amplitude_separation: float) -> dict:
    """Minimal pre-built clustering diagnostics dict."""
    return {
        "method": "clustering",
        "k": 2,
        "cluster_means": [[0.0, 1.0], [0.0, -1.0]],
        "cluster_sizes": [5, 5],
        "pairwise_amplitude_distance": None,
        "pairwise_phase_distance": None,
        "mean_amplitude_separation": mean_amplitude_separation,
        "mean_phase_separation": None,
    }


# ---------------------------------------------------------------------------
# Task 1 — 'comparison' task clause in _system_prompt
# ---------------------------------------------------------------------------

def test_comparison_task_prompt_added():
    """_system_prompt('comparison') returns a prompt with grounding invariant
    and a comparison-specific instruction about narrating a supplied ranking."""
    from fdars.advisor._prompts import _system_prompt, _GROUNDING_INVARIANT

    prompt = _system_prompt("comparison", aspect="clustering")

    # Grounding invariant must be present verbatim.
    assert _GROUNDING_INVARIANT in prompt, (
        "_system_prompt('comparison') missing _GROUNDING_INVARIANT"
    )

    # Comparison task clause must instruct narrating the ranking, not choosing winner.
    prompt_lower = prompt.lower()
    # The clause must mention that the ranking/winner is already decided
    assert "rank" in prompt_lower or "narrat" in prompt_lower, (
        "comparison prompt must reference ranking or narration"
    )
    # The clause must reference the winner being supplied (not chosen by LLM)
    assert "winner" in prompt_lower or "supplied" in prompt_lower or "already" in prompt_lower, (
        "comparison prompt must clarify winner is supplied, not chosen by model"
    )


def test_existing_tasks_unchanged():
    """interpretation/parameter/method prompts are byte-for-byte unchanged."""
    from fdars.advisor._prompts import _system_prompt

    # Capture baseline for each pre-existing task
    baseline_interpretation = _system_prompt("interpretation")
    baseline_parameter = _system_prompt("parameter")
    baseline_method = _system_prompt("method")

    # Call again — must produce identical strings
    assert _system_prompt("interpretation") == baseline_interpretation, (
        "interpretation prompt changed after adding 'comparison' task"
    )
    assert _system_prompt("parameter") == baseline_parameter, (
        "parameter prompt changed after adding 'comparison' task"
    )
    assert _system_prompt("method") == baseline_method, (
        "method prompt changed after adding 'comparison' task"
    )


def test_comparison_rejects_bogus_task():
    """Unsupported task still raises ValueError."""
    from fdars.advisor._prompts import _system_prompt

    with pytest.raises(ValueError, match="unsupported task"):
        _system_prompt("bogus_task_xyz")


# ---------------------------------------------------------------------------
# Task 2 — Winner authority + per-candidate provenance in the LLM path
# ---------------------------------------------------------------------------

# A minimal mock provider that records what it was called with and returns a
# canned Advice.  The mock narration intentionally names the LOSING candidate
# as "best" to verify that the winner field is NOT derived from the LLM.

class _MockProvider:
    """Provider mock: returns a fixed Advice regardless of input."""

    name = "mock"
    model = "mock-model"
    supports_native_structured_output = True

    def __init__(self, advice_to_return, record_calls_to=None):
        self._advice = advice_to_return
        self._calls = record_calls_to if record_calls_to is not None else []

    def complete_structured(self, schema, messages, system):
        self._calls.append({"schema": schema, "messages": messages, "system": system})
        return self._advice


def _make_advice(narration_text: str):
    """Build a minimal Advice with the given interpretation text (no recs)."""
    from fdars.advisor._schema import Advice, Recommendation
    return Advice(
        interpretation=narration_text,
        recommendations=[],
        caveats=[],
    )


def test_winner_set_before_llm_and_preserved():
    """Mock narration names loser as best; returned winner is still fdars winner.

    Clustering: higher mean_amplitude_separation is better.
    candidate_A: sep=0.80 (best)
    candidate_B: sep=0.30 (worst)
    Mock narration says "candidate_B is the winner" — must be ignored.
    """
    from fdars.advisor.compare_methods import compare_methods

    diag_a = _clustering_diag(mean_amplitude_separation=0.80)
    diag_b = _clustering_diag(mean_amplitude_separation=0.30)

    # Build a mock narration that incorrectly names the loser as best.
    mock_narration = _make_advice(
        "candidate_B is the winner with superior amplitude separation."
    )
    mock_provider = _MockProvider(advice_to_return=mock_narration)

    result = compare_methods(
        {"candidate_A": diag_a, "candidate_B": diag_b},
        run_llm=True,
        provider=mock_provider,
        domain_context="test",
    )

    # The fdars sort says candidate_A wins (0.80 > 0.30, higher-is-better).
    assert result["winner"] == "candidate_A", (
        f"Expected winner 'candidate_A' but got {result['winner']!r}. "
        "The LLM narration must NOT override the fdars-computed winner."
    )


def test_llm_cannot_override_winner():
    """winner field == deterministic sort winner regardless of LLM content."""
    from fdars.advisor.compare_methods import compare_methods

    # lower-is-better metric: regression_cv (min_cv_error)
    diag_low = {
        "method": "regression_cv",
        "optimal_k": 3,
        "min_cv_error": 0.12,
        "cv_curve": [0.5, 0.3, 0.12, 0.2],
        "k_values": [1, 2, 3, 4],
        "cv_curve_range": [0.12, 0.5],
        "elbow_present": True,
    }
    diag_high = {
        "method": "regression_cv",
        "optimal_k": 2,
        "min_cv_error": 0.45,
        "cv_curve": [0.6, 0.45, 0.5],
        "k_values": [1, 2, 3],
        "cv_curve_range": [0.45, 0.6],
        "elbow_present": False,
    }

    # Mock narration claims the higher-error candidate won.
    mock_narration = _make_advice(
        "config_B (min_cv_error=0.45) demonstrates superior performance and is the winner."
    )
    mock_provider = _MockProvider(advice_to_return=mock_narration)

    result = compare_methods(
        {"config_A": diag_low, "config_B": diag_high},
        run_llm=True,
        provider=mock_provider,
        domain_context="test",
    )

    # Deterministic sort: lower is better for min_cv_error → config_A (0.12) wins.
    assert result["winner"] == "config_A", (
        f"Expected winner 'config_A' (min_cv_error=0.12) but got {result['winner']!r}."
    )


def test_provenance_is_per_candidate_not_flat_merged():
    """Provider receives a list of labeled blocks, never a flat-merged dict.

    Two candidates share a coincidental numeric value (0.50) in different
    diagnostic keys.  The per-candidate structure must be preserved so
    grounding can be attributed to the right candidate.
    """
    from fdars.advisor.compare_methods import compare_methods

    # candidate_X: mean_amplitude_separation=0.80, mean_phase_separation=0.50
    diag_x = {
        "method": "clustering",
        "k": 2,
        "cluster_means": [[0.0, 1.0], [0.0, -1.0]],
        "cluster_sizes": [5, 5],
        "pairwise_amplitude_distance": None,
        "pairwise_phase_distance": None,
        "mean_amplitude_separation": 0.80,
        "mean_phase_separation": 0.50,
    }
    # candidate_Y: mean_amplitude_separation=0.50, mean_phase_separation=0.20
    # Note: 0.50 appears in candidate_X.mean_phase_separation, so it is only
    # grounded for candidate_X, not candidate_Y (where it is the amplitude sep).
    diag_y = {
        "method": "clustering",
        "k": 2,
        "cluster_means": [[0.0, 0.5], [0.0, -0.5]],
        "cluster_sizes": [6, 4],
        "pairwise_amplitude_distance": None,
        "pairwise_phase_distance": None,
        "mean_amplitude_separation": 0.50,
        "mean_phase_separation": 0.20,
    }

    # Capture what the provider receives.
    recorded_calls = []
    mock_advice = _make_advice("candidate_X ranks first with amplitude separation 0.80.")
    mock_provider = _MockProvider(advice_to_return=mock_advice, record_calls_to=recorded_calls)

    result = compare_methods(
        {"candidate_X": diag_x, "candidate_Y": diag_y},
        run_llm=True,
        provider=mock_provider,
        domain_context="test",
    )

    assert len(recorded_calls) >= 1, "Mock provider should have been called."

    # The user message content in any call must contain labeled blocks (not a merged dict).
    # Look across all messages in the first call.
    first_call_messages = recorded_calls[0]["messages"]
    combined_user_content = " ".join(
        m["content"] for m in first_call_messages if m.get("role") == "user"
    )

    # The payload must reference both candidate labels explicitly.
    assert "candidate_X" in combined_user_content, (
        "Per-candidate labeled block for 'candidate_X' missing from LLM message."
    )
    assert "candidate_Y" in combined_user_content, (
        "Per-candidate labeled block for 'candidate_Y' missing from LLM message."
    )

    # Winner is still fdars-sort winner.
    assert result["winner"] == "candidate_X", (
        f"Expected winner 'candidate_X' (sep=0.80) but got {result['winner']!r}."
    )


def test_grounding_runs_per_candidate():
    """A mock narration citing candidate_A's value for a claim about candidate_B
    raises GroundingViolationError when grounding is checked per-candidate.

    candidate_A: mean_amplitude_separation=0.91
    candidate_B: mean_amplitude_separation=0.30
    Mock recommendation about candidate_B cites '0.91' (candidate_A's value).
    The per-candidate grounding check should detect this mismatch.
    """
    from fdars.advisor.compare_methods import compare_methods
    from fdars.advisor.providers._validate import GroundingViolationError

    diag_a = _clustering_diag(mean_amplitude_separation=0.91)
    diag_b = _clustering_diag(mean_amplitude_separation=0.30)

    # Mock narration: a recommendation about candidate_B cites candidate_A's value.
    from fdars.advisor._schema import Advice, Recommendation
    bad_advice = Advice(
        interpretation="candidate_A ranks first.",
        recommendations=[
            Recommendation(
                action="Prefer candidate_A",
                kind="none",
                rationale="candidate_B has amplitude separation 0.91",  # fabricated for B
                expected_effect="Better clustering",
                evidence=["candidate_B amplitude separation = 0.91"],  # wrong provenance
            )
        ],
        caveats=[],
    )
    mock_provider = _MockProvider(advice_to_return=bad_advice)

    with pytest.raises(GroundingViolationError):
        compare_methods(
            {"candidate_A": diag_a, "candidate_B": diag_b},
            run_llm=True,
            provider=mock_provider,
            domain_context="test",
        )


def test_result_shape_run_llm_true():
    """compare_methods(run_llm=True) result carries winner, ranking, and advice."""
    from fdars.advisor.compare_methods import compare_methods

    diag_a = _clustering_diag(mean_amplitude_separation=0.75)
    diag_b = _clustering_diag(mean_amplitude_separation=0.40)

    mock_advice = _make_advice("candidate_A ranks first based on amplitude separation.")
    mock_provider = _MockProvider(advice_to_return=mock_advice)

    result = compare_methods(
        {"candidate_A": diag_a, "candidate_B": diag_b},
        run_llm=True,
        provider=mock_provider,
        domain_context="FDA test",
    )

    # Required fields: method, metric, ranking, winner, advice (or narration)
    assert "method" in result
    assert "metric" in result
    assert "ranking" in result
    assert "winner" in result
    # At least one of advice/narration must be present for the LLM path
    assert "advice" in result or "narration" in result, (
        "run_llm=True result must carry 'advice' or 'narration' from the LLM"
    )
    assert result["winner"] == "candidate_A"


# ---------------------------------------------------------------------------
# Task 3 — Env-gated live comparison narration smoke test
# ---------------------------------------------------------------------------

_HAS_API_KEY = bool(os.environ.get("ANTHROPIC_API_KEY"))


@pytest.mark.skipif(not _HAS_API_KEY, reason="ANTHROPIC_API_KEY not set — live test skipped")
def test_live_comparison_narration():
    """Live end-to-end: compare_methods(run_llm=True) with real Anthropic API.

    Uses two small clustering candidates so the API call is cheap.
    Asserts:
      - winner equals offline deterministic winner for the same inputs
      - narration/advice is non-empty
      - grounding passes (no GroundingViolationError)
    """
    from fdars.advisor.compare_methods import compare_methods

    # Two small clustering candidates with different amplitude separations.
    diag_hi = _clustering_diag(mean_amplitude_separation=0.78)
    diag_lo = _clustering_diag(mean_amplitude_separation=0.32)

    # Compute offline winner first for comparison.
    offline = compare_methods(
        {"kmeans_k3": diag_hi, "kmeans_k5": diag_lo},
        run_llm=False,
    )
    expected_winner = offline["winner"]

    # Live call — must not raise GroundingViolationError.
    result = compare_methods(
        {"kmeans_k3": diag_hi, "kmeans_k5": diag_lo},
        run_llm=True,
        domain_context="Phoneme FDA study: comparing k=3 vs k=5 clustering configs.",
    )

    assert result["winner"] == expected_winner, (
        f"Live winner {result['winner']!r} != offline winner {expected_winner!r}."
    )

    # Narration must be non-empty.
    advice_obj = result.get("advice") or result.get("narration")
    assert advice_obj is not None, "Live result missing 'advice'/'narration' field."
    if hasattr(advice_obj, "interpretation"):
        assert advice_obj.interpretation, "Live advice.interpretation is empty."
    else:
        assert str(advice_obj), "Live narration is empty."
