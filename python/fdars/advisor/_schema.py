"""fdars.advisor._schema — Pydantic schema for Advice / Recommendation.

Contains the Pydantic models (with graceful fallback when pydantic is absent)
for :class:`Advice` and :class:`Recommendation`.  Importing this module never
touches the anthropic SDK, never opens a network connection, and never imports
any other fdars.advisor submodule (no circular import risk — see RESEARCH.md
Risk 2).

When ``pydantic`` is not installed the classes still exist as plain
dataclass-style stand-ins so that importing ``fdars.advisor`` and calling
``build_diagnostics`` both succeed without any optional dependency installed.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

# ---------------------------------------------------------------------------
# Pydantic models (with graceful fallback when pydantic is absent)
# ---------------------------------------------------------------------------

# We attempt to import from pydantic.  When pydantic is not installed we
# synthesise equivalent plain-Python classes so that the module is importable
# offline without the [advisor] extra.  The Pydantic-backed classes are
# required for advise() because anthropic.messages.parse uses them as the
# output_format; that code path also needs the anthropic package, which is
# also absent without the extra — so both missing-dependency paths converge at
# the same _require_anthropic() guard inside advise().

try:
    from pydantic import BaseModel as _PydanticBaseModel

    # -----------------------------------------------------------------------
    # Tuning schema types (TUNE-06) — pydantic branch
    # -----------------------------------------------------------------------

    class TuneProposal(_PydanticBaseModel):
        """Structured parameter proposal from the proposer (LLM or heuristic).

        The proposer (LLM or heuristic) populates this schema; the loop core
        clamps and validates new_value before it enters the numeric path.

        Attributes
        ----------
        param : str
            Exact param name from _PARAM_REGISTRY (e.g. ``"n_basis"``).
        new_value : float
            Proposed new value; the loop clamps to the declared range.
        rationale : str
            Qualitative justification — must NOT cite predicted future values.
        """

        param: str
        new_value: float
        rationale: str

    class TuningStep(_PydanticBaseModel):
        """One iteration of the tuning loop — recorded whether accepted or not.

        Attributes
        ----------
        step : int
            Zero-based step index.
        param_before : float
            Scalar param value entering this step.
        param_after : float
            Scalar param value proposed this step (may equal param_before if
            the proposal was clamped to the same value).
        target_before : float
            Target metric value before re-run.
        target_after : float or None
            Target metric value after re-run; None when the step was rejected
            before the fdars call (e.g. budget exceeded, parse_failure).
        accepted : bool
            True iff target improved AND guards were satisfied.
        stop_reason : str or None
            Non-None only for the final step that triggered termination.
            One of ``"budget"``, ``"converged"``, ``"oscillation"``,
            ``"guard_stop"``, ``"parse_failure"``.
        guard_violations : list[str]
            Human-readable guard violation descriptions; empty when guards ok.
        proposal_source : str
            Identifier for the proposer: ``"llm"``, ``"heuristic"``, or
            ``"mock"``.
        """

        step: int
        param_before: float
        param_after: float
        target_before: float
        target_after: Optional[float] = None
        accepted: bool
        stop_reason: Optional[str] = None
        guard_violations: List[str] = []
        proposal_source: str

    class TuningTrace(_PydanticBaseModel):
        """Complete record of a run_tuning_loop() call.

        Attributes
        ----------
        method : str
            The fdars method being tuned (e.g. ``"smoothing"``).
        param : str
            The scalar parameter being tuned (e.g. ``"n_basis"``).
        target_metric : str
            The diagnostic metric used as the optimisation target.
        target_direction : str
            ``"higher"`` or ``"lower"`` (from ``_METRIC_REGISTRY``).
        steps : list[TuningStep]
            All steps recorded during the loop (accepted and rejected).
        final_params : dict
            The param dict at loop termination.
        final_diagnostics : dict
            The diagnostics dict at loop termination.
        converged : bool
            True when stop_reason is ``"converged"``.
        stop_reason : str
            Reason for termination; one of ``"budget"``, ``"converged"``,
            ``"oscillation"``, ``"guard_stop"``, ``"parse_failure"``.
        n_steps : int
            Number of iterations actually executed.
        steps_used : int
            Alias for n_steps; included for MCP return dict consistency.
        budget_remaining : int
            ``max_steps - n_steps``.
        """

        method: str
        param: str
        target_metric: str
        target_direction: str
        steps: List[TuningStep]
        final_params: Dict[str, Any]
        final_diagnostics: Dict[str, Any]
        converged: bool
        stop_reason: str
        n_steps: int
        steps_used: int
        budget_remaining: int

    class TuneResult(_PydanticBaseModel):
        """Returned by auto_tune() and fdars_auto_tune.

        Attributes
        ----------
        trace : TuningTrace
            Full trace of the tuning loop.
        improved : bool
            True iff the final target value is better than the initial value.
        initial_target_value : float
            Target metric value before any tuning.
        final_target_value : float
            Target metric value at loop termination.
        improvement_pct : float or None
            ``(final - initial) / abs(initial) * 100``; None when initial is 0.
        """

        trace: TuningTrace
        improved: bool
        initial_target_value: float
        final_target_value: float
        improvement_pct: Optional[float] = None

    class Recommendation(_PydanticBaseModel):
        """A single actionable recommendation grounded in fdars diagnostics.

        Attributes
        ----------
        action : str
            Concrete step (e.g. ``"increase n_basis to ~15"``).
        kind : {"parameter", "method", "none"}
            Category of the recommendation.
        rationale : str
            Why this action is warranted, tied to a diagnostic.
        expected_effect : str
            What should change in subsequent runs if the action is applied.
        evidence : list[str]
            Each entry cites a specific diagnostic value present in the input.
        parameter_delta : TuneProposal or None
            Optional structured parameter proposal; populated only for the
            ``"parameter_proposal"`` task.  Defaults to ``None`` so that all
            existing five-field constructions remain valid.
        """

        action: str
        kind: Literal["parameter", "method", "none"]
        rationale: str
        expected_effect: str
        evidence: List[str]
        parameter_delta: Optional[TuneProposal] = None

    class Advice(_PydanticBaseModel):
        """Schema-validated advice returned by :func:`advise`.

        Attributes
        ----------
        interpretation : str
            Plain-language interpretation of the result in domain terms.
        recommendations : list[Recommendation]
            Concrete next actions ordered by priority.
        caveats : list[str]
            Limitations, assumptions, or conditions that qualify the advice.
        """

        interpretation: str
        recommendations: List[Recommendation]
        caveats: List[str]

    class PipelineReport(_PydanticBaseModel):
        """Schema-validated pipeline diagnostic report returned by :func:`pipeline_report`.

        Contains a per-stage narrative summary, an overall narrative, and the
        DETERMINISTIC cross-stage caveats computed by Python (not the LLM).
        The LLM narrates the report but never generates the caveats.

        Attributes
        ----------
        stages : list
            Per-stage narrative sections.  Each element is a short string
            summarising one pipeline stage's diagnostic findings in narrative
            form.  The order matches the caller-declared stage order.
        narrative : str
            Overall pipeline narrative integrating all stages into a coherent
            summary of the functional data analysis pipeline.
        caveats : list
            Structured cross-stage caveats computed by Python (PIPE-03).
            Each element is a dict with keys ``stage``, ``aspect``, ``rule``,
            ``value``, and ``message`` — exactly as produced by
            ``_compute_cross_stage_caveats``.  This field is authoritative;
            the LLM narrates caveats but never generates them.
        """

        stages: List[str]
        narrative: str
        caveats: List[Any]

except ImportError:
    # pydantic is absent — define minimal stand-ins so importing advisor and
    # calling build_diagnostics work fully offline.

    # -----------------------------------------------------------------------
    # Tuning schema stand-ins (TUNE-06) — fallback branch
    # -----------------------------------------------------------------------

    class TuneProposal:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic TuneProposal model."""

        def __init__(self, param: str, new_value: float, rationale: str):
            self.param = param
            self.new_value = new_value
            self.rationale = rationale

        def __repr__(self) -> str:
            return f"TuneProposal(param={self.param!r}, new_value={self.new_value!r})"

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, TuneProposal):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class TuningStep:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic TuningStep model."""

        def __init__(
            self,
            step: int,
            param_before: float,
            param_after: float,
            target_before: float,
            target_after=None,
            accepted: bool = False,
            stop_reason=None,
            guard_violations=None,
            proposal_source: str = "mock",
        ):
            self.step = step
            self.param_before = param_before
            self.param_after = param_after
            self.target_before = target_before
            self.target_after = target_after
            self.accepted = accepted
            self.stop_reason = stop_reason
            self.guard_violations = guard_violations if guard_violations is not None else []
            self.proposal_source = proposal_source

        def __repr__(self) -> str:
            return (
                f"TuningStep(step={self.step!r}, accepted={self.accepted!r}, "
                f"stop_reason={self.stop_reason!r})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, TuningStep):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class TuningTrace:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic TuningTrace model."""

        def __init__(
            self,
            method: str,
            param: str,
            target_metric: str,
            target_direction: str,
            steps=None,
            final_params=None,
            final_diagnostics=None,
            converged: bool = False,
            stop_reason: str = "budget",
            n_steps: int = 0,
            steps_used: int = 0,
            budget_remaining: int = 0,
        ):
            self.method = method
            self.param = param
            self.target_metric = target_metric
            self.target_direction = target_direction
            self.steps = steps if steps is not None else []
            self.final_params = final_params if final_params is not None else {}
            self.final_diagnostics = final_diagnostics if final_diagnostics is not None else {}
            self.converged = converged
            self.stop_reason = stop_reason
            self.n_steps = n_steps
            self.steps_used = steps_used
            self.budget_remaining = budget_remaining

        def __repr__(self) -> str:
            return (
                f"TuningTrace(method={self.method!r}, n_steps={self.n_steps!r}, "
                f"stop_reason={self.stop_reason!r})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, TuningTrace):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class TuneResult:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic TuneResult model."""

        def __init__(
            self,
            trace,
            improved: bool,
            initial_target_value: float,
            final_target_value: float,
            improvement_pct=None,
        ):
            self.trace = trace
            self.improved = improved
            self.initial_target_value = initial_target_value
            self.final_target_value = final_target_value
            self.improvement_pct = improvement_pct

        def __repr__(self) -> str:
            return (
                f"TuneResult(improved={self.improved!r}, "
                f"improvement_pct={self.improvement_pct!r})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, TuneResult):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class Recommendation:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic Recommendation model.

        Has the same fields; not schema-validated.  advise() requires pydantic
        and will fail with a clear error before this class is used in that path.
        """

        def __init__(
            self,
            action: str,
            kind: str,
            rationale: str,
            expected_effect: str,
            evidence: List[str],
            parameter_delta=None,
        ):
            self.action = action
            self.kind = kind
            self.rationale = rationale
            self.expected_effect = expected_effect
            self.evidence = evidence
            self.parameter_delta = parameter_delta

        def __repr__(self) -> str:
            return (
                f"Recommendation(action={self.action!r}, kind={self.kind!r})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Recommendation):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class Advice:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic Advice model.

        Has the same fields; not schema-validated.  advise() requires pydantic
        and will fail with a clear error before this class is used in that path.
        """

        def __init__(
            self,
            interpretation: str,
            recommendations: List[Recommendation],
            caveats: List[str],
        ):
            self.interpretation = interpretation
            self.recommendations = recommendations
            self.caveats = caveats

        def __repr__(self) -> str:
            n = len(self.recommendations)
            return (
                f"Advice(interpretation=..., recommendations={n}, "
                f"caveats={len(self.caveats)})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Advice):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class PipelineReport:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic PipelineReport model.

        Has the same fields; not schema-validated.  pipeline_report() requires
        pydantic and will fail with a clear error before this class is used
        in that path.
        """

        def __init__(
            self,
            stages: List,
            narrative: str,
            caveats: List,
        ):
            self.stages = stages
            self.narrative = narrative
            self.caveats = caveats

        def __repr__(self) -> str:
            return (
                f"PipelineReport(stages={len(self.stages)}, "
                f"narrative=..., caveats={len(self.caveats)})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, PipelineReport):
                return NotImplemented
            return self.__dict__ == other.__dict__
