"""Tests for the fdars MCP fdars_build_pipeline_report tool (Plan 52-03).

Plan 52-03 tasks:
  - Task 1: MCP re-run helper (_pipeline.build_pipeline_report_mcp) delegating
    to the deterministic offline core (build_pipeline_report run_llm=False).
  - Task 2: fdars_build_pipeline_report @mcp.tool wrapper + guard-sync no-op.
  - Task 3: Prove the MCP tool stays LLM-free; guard-sync stays a no-op.

All tests are skipped on Python <3.10 via the module-level pytestmark.
No ANTHROPIC_API_KEY and no network are required.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Module-level skip guard: Python 3.9 CI runners skip cleanly (mirrors server.py)
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="mcp requires Python 3.10+",
)

# ---------------------------------------------------------------------------
# Autouse fixture: clear the registry after each test (Pitfall 3)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_registry():
    """Reset the handle registry after every test to prevent state leakage."""
    yield
    from fdars.mcp._registry import registry
    registry.clear()


# ---------------------------------------------------------------------------
# Dataset fixture: small synthetic dataset with two well-separated clusters
# ---------------------------------------------------------------------------


@pytest.fixture()
def dataset_id():
    """Register a small synthetic dataset and return its opaque dataset_id.

    Two well-separated clusters (10 obs each), 30 grid points.
    Small enough for fast offline tests; large enough for clustering/fpca to run.
    """
    from fdars.mcp._registry import registry

    rng = np.random.default_rng(42)
    X_cluster0 = rng.standard_normal((10, 30)) + 3.0
    X_cluster1 = rng.standard_normal((10, 30)) - 3.0
    X = np.vstack([X_cluster0, X_cluster1])
    argvals = np.linspace(0, 1, 30)
    return registry.store_dataset(X, argvals)


# ---------------------------------------------------------------------------
# Task 1 tests: build_pipeline_report_mcp helper
# ---------------------------------------------------------------------------


def test_helper_returns_by_reference_dict(dataset_id):
    """Happy path: helper returns report_id + per-stage result_id handles.

    Runs two stages (smoothing then fpca) via build_pipeline_report_mcp and
    asserts the return is JSON-serialisable and carries only handles (no arrays).
    """
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = build_pipeline_report_mcp(dataset_id, stages)

    # Must be JSON-serialisable (no NumPy arrays)
    serialised = json.dumps(result)
    assert serialised, "json.dumps returned empty string"

    # Top-level keys
    assert "report_id" in result, f"'report_id' missing from {list(result.keys())}"
    assert "stages" in result, f"'stages' missing from {list(result.keys())}"

    # Per-stage entries: stage, aspect, result_id — NO arrays
    assert len(result["stages"]) == 2, (
        f"Expected 2 stage entries, got {len(result['stages'])}"
    )
    for entry in result["stages"]:
        assert "stage" in entry, f"stage entry missing 'stage': {list(entry.keys())}"
        assert "aspect" in entry, f"stage entry missing 'aspect': {list(entry.keys())}"
        assert "result_id" in entry, f"stage entry missing 'result_id': {list(entry.keys())}"
        assert isinstance(entry["result_id"], str), (
            f"result_id should be a str handle, got {type(entry['result_id'])}"
        )
        # No array values may appear in the return
        for k, v in entry.items():
            assert not isinstance(v, np.ndarray), (
                f"Array found under key '{k}' — by-reference invariant violated (T-52-10)"
            )


def test_helper_report_id_is_string_handle(dataset_id):
    """report_id must be an opaque string handle, not an array or dict."""
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = build_pipeline_report_mcp(dataset_id, stages)

    assert isinstance(result["report_id"], str), (
        f"report_id should be a str handle, got {type(result['report_id'])}"
    )


def test_helper_rejects_unknown_param_key(dataset_id):
    """Unknown per-stage param key raises ValueError BEFORE any run.

    Passes a stage with 'bogus_param' — a key outside the allowlist
    {'lambda_', 'n_basis', 'n_comp', 'k', 'seed'}.  Expects ValueError
    naming the unknown key before any fdars call is attempted.
    """
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {"bogus_param": 99}},
    ]
    with pytest.raises(ValueError, match="bogus_param"):
        build_pipeline_report_mcp(dataset_id, stages)


def test_helper_rejects_non_runnable_aspect(dataset_id):
    """A stage aspect outside _RUNNABLE_METHODS raises ValueError naming the set.

    'regression' is a diagnostics-only aspect — not in _RUNNABLE_METHODS.
    The helper must reject it with a clear message before any run.
    """
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "fit", "aspect": "regression", "params": {}},
    ]
    with pytest.raises(ValueError, match="regression"):
        build_pipeline_report_mcp(dataset_id, stages)


def test_helper_rejects_completely_unknown_aspect(dataset_id):
    """A stage aspect not in _DIAGNOSTICS_METHODS at all raises ValueError."""
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "mystery", "aspect": "totally_unknown", "params": {}},
    ]
    with pytest.raises(ValueError):
        build_pipeline_report_mcp(dataset_id, stages)


def test_helper_stage_order_preserved(dataset_id):
    """Stage entries in return must preserve caller-declared order."""
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "A_smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "B_decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = build_pipeline_report_mcp(dataset_id, stages)

    returned_stages = [e["stage"] for e in result["stages"]]
    assert returned_stages == ["A_smooth", "B_decompose"], (
        f"Stage order not preserved: got {returned_stages}"
    )


def test_helper_aggregates_via_offline_core(dataset_id):
    """build_pipeline_report_mcp must delegate to build_pipeline_report(run_llm=False).

    Checks that the full aggregate is stored in the registry under report_id
    and that it has the expected keys from the offline core return format.
    """
    from fdars.mcp._pipeline import build_pipeline_report_mcp
    from fdars.mcp._registry import registry

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = build_pipeline_report_mcp(dataset_id, stages)

    # The full aggregate report must be retrievable from the registry
    full_report = registry.get_result(result["report_id"])
    assert isinstance(full_report, dict), (
        f"Expected dict stored under report_id, got {type(full_report)}"
    )
    # The offline core returns {"stages": [...]} — verify the key
    assert "stages" in full_report, (
        f"Offline core result missing 'stages' key: {list(full_report.keys())}"
    )
    # Each offline stage block must have stage/aspect/diagnostics
    for block in full_report["stages"]:
        assert "stage" in block, f"stage block missing 'stage': {list(block.keys())}"
        assert "aspect" in block, f"stage block missing 'aspect': {list(block.keys())}"
        assert "diagnostics" in block, f"stage block missing 'diagnostics': {list(block.keys())}"


def test_helper_stores_per_stage_results(dataset_id):
    """Each stage result must be retrievable from the registry by its result_id."""
    from fdars.mcp._pipeline import build_pipeline_report_mcp
    from fdars.mcp._registry import registry

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = build_pipeline_report_mcp(dataset_id, stages)

    for entry in result["stages"]:
        result_id = entry["result_id"]
        stored = registry.get_result(result_id)
        # Stored result is the raw fdars result (has arrays) — but it IS retrievable
        assert stored is not None, f"result_id {result_id!r} not found in registry"


def test_helper_validates_all_stages_before_running(dataset_id):
    """All stage params must be validated BEFORE any run is attempted.

    If stage[0] is valid but stage[1] has a bad param, the ValueError must
    be raised before stage[0] is run (fail-closed allowlist, T-52-09).
    """
    from fdars.mcp._pipeline import build_pipeline_report_mcp

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "bad", "aspect": "fpca", "params": {"evil_param": 1}},
    ]
    with pytest.raises(ValueError, match="evil_param"):
        build_pipeline_report_mcp(dataset_id, stages)


# ---------------------------------------------------------------------------
# Task 2 tests: fdars_build_pipeline_report thin MCP tool handler
# ---------------------------------------------------------------------------


def test_tool_handler_returns_report_dict(dataset_id):
    """Happy path: fdars_build_pipeline_report returns a by-reference report dict.

    Calls the tool handler directly (no async MCP client needed for the
    synchronous handler).  Asserts the return shape.
    """
    from fdars.mcp.server import fdars_build_pipeline_report

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = fdars_build_pipeline_report(dataset_id=dataset_id, stages=stages)

    assert "report_id" in result, f"'report_id' missing from {list(result.keys())}"
    assert "stages" in result, f"'stages' missing from {list(result.keys())}"
    assert len(result["stages"]) == 2, (
        f"Expected 2 stage entries, got {len(result['stages'])}"
    )
    # Must be JSON-serialisable
    json.dumps(result)


def test_tool_handler_rejects_non_runnable_aspect(dataset_id):
    """fdars_build_pipeline_report must reject a stage with a non-runnable aspect.

    'regression' is diagnostics-only — not in _RUNNABLE_METHODS.
    The tool must raise ValueError naming the supported set.
    """
    from fdars.mcp.server import fdars_build_pipeline_report

    stages = [
        {"stage_name": "fit", "aspect": "regression", "params": {}},
    ]
    with pytest.raises(ValueError, match="regression"):
        fdars_build_pipeline_report(dataset_id=dataset_id, stages=stages)


def test_tool_handler_rejects_unknown_param_key(dataset_id):
    """fdars_build_pipeline_report must reject unknown per-stage param keys."""
    from fdars.mcp.server import fdars_build_pipeline_report

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {"bad_key": 1}},
    ]
    with pytest.raises(ValueError, match="bad_key"):
        fdars_build_pipeline_report(dataset_id=dataset_id, stages=stages)


def test_tool_no_provider_model_argument():
    """fdars_build_pipeline_report must not accept a provider or model argument.

    Checks the tool handler's signature directly — no provider/model param
    means the MCP layer is provably LLM-free (Anti-Pattern 3 / PIPE-04).
    """
    import inspect
    from fdars.mcp.server import fdars_build_pipeline_report

    sig = inspect.signature(fdars_build_pipeline_report)
    param_names = list(sig.parameters.keys())
    assert "provider" not in param_names, (
        f"fdars_build_pipeline_report exposes 'provider' param — LLM-free boundary "
        f"violated (T-52-08). Params: {param_names}"
    )
    assert "model" not in param_names, (
        f"fdars_build_pipeline_report exposes 'model' param — LLM-free boundary "
        f"violated (T-52-08). Params: {param_names}"
    )


def test_tool_is_registered_as_mcp_tool():
    """fdars_build_pipeline_report must be registered in the MCP server tool list.

    Uses the internal _tool_manager._tools dict for synchronous inspection
    (mcp.list_tools() is an async coroutine; async client usage is tested in
    test_mcp_server.py via pytest-asyncio for the full async path).
    """
    from fdars.mcp.server import mcp

    tool_names = list(mcp._tool_manager._tools.keys())
    assert "fdars_build_pipeline_report" in tool_names, (
        f"fdars_build_pipeline_report not in tool list: {tool_names}"
    )


# ---------------------------------------------------------------------------
# Task 3 tests: LLM-free invariant + guard-sync no-op assertion
# ---------------------------------------------------------------------------


def test_tool_never_imports_advise():
    """_pipeline.py must not reference the advise entrypoint.

    File-scan invariant (mirrors test_tool_never_imports_advise in
    test_mcp_compare_methods.py): the pipeline MCP helper must stay LLM-free.
    Token constructed at runtime to avoid this test file self-flagging.
    """
    import pathlib

    # Build the search token at runtime to avoid this file self-flagging.
    _token = "adv" + "ise"

    target = (
        pathlib.Path(__file__).resolve().parents[1]
        / "python"
        / "fdars"
        / "mcp"
        / "_pipeline.py"
    )
    assert target.exists(), f"mcp/_pipeline.py not found at {target}"
    content = target.read_text()
    assert _token not in content, (
        f"mcp/_pipeline.py references '{_token}' (LLM-free invariant "
        f"violation — PIPE-04): file must never import advise"
    )


def test_importing_pipeline_module_does_not_import_advise():
    """Importing mcp/_pipeline.py must not pull in the advise module.

    Verifies the deferred-import pattern keeps the module LLM-free at load
    time by running a subprocess with a fresh interpreter — this guarantees
    isolation from prior test imports (T-52-08 mitigated).
    """
    import subprocess
    import sys as _sys

    # Subprocess check: a fresh Python process imports mcp/_pipeline.py and
    # asserts that fdars.advisor.providers was NOT pulled in as a side effect.
    code = (
        "import sys; "
        "import fdars.mcp._pipeline; "
        "assert 'fdars.advisor.providers' not in sys.modules, "
        "'providers imported at module load — LLM-free invariant violated'"
    )
    result = subprocess.run(
        [_sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Importing mcp/_pipeline.py pulled in 'fdars.advisor.providers' (T-52-08):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_guard_sync_still_no_op():
    """_DIAGNOSTICS_METHODS (14) and _RUNNABLE_METHODS (6) unchanged by this phase.

    Asserts that adding fdars_build_pipeline_report added no new entry to
    either set (guard-sync no-op — PIPE-04 / T-52-11).
    """
    from fdars.mcp.server import _DIAGNOSTICS_METHODS, _RUNNABLE_METHODS

    assert len(_RUNNABLE_METHODS) == 6, (
        f"_RUNNABLE_METHODS has {len(_RUNNABLE_METHODS)} entries (expected 6): "
        f"{sorted(_RUNNABLE_METHODS)}"
    )
    assert len(_DIAGNOSTICS_METHODS) == 14, (
        f"_DIAGNOSTICS_METHODS has {len(_DIAGNOSTICS_METHODS)} entries (expected 14): "
        f"{sorted(_DIAGNOSTICS_METHODS)}"
    )


def test_offline_no_api_key_required(dataset_id, monkeypatch):
    """Tool must run without ANTHROPIC_API_KEY (fully offline).

    Unsets the key then calls the tool — must succeed without network.
    """
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from fdars.mcp.server import fdars_build_pipeline_report

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    # Should complete offline with no key required
    result = fdars_build_pipeline_report(dataset_id=dataset_id, stages=stages)
    assert "report_id" in result, (
        f"Tool failed without ANTHROPIC_API_KEY: {result}"
    )


def test_return_carries_handles_not_arrays(dataset_id):
    """The tool return dict must be free of NumPy array values (by-reference).

    Recursively inspects all values in the return dict and asserts none are
    numpy ndarrays (Anti-Pattern 4 / T-52-10).
    """
    from fdars.mcp.server import fdars_build_pipeline_report

    stages = [
        {"stage_name": "smooth", "aspect": "smoothing", "params": {}},
        {"stage_name": "decompose", "aspect": "fpca", "params": {"n_comp": 2}},
    ]
    result = fdars_build_pipeline_report(dataset_id=dataset_id, stages=stages)

    def _check_no_arrays(obj, path="root"):
        if isinstance(obj, np.ndarray):
            pytest.fail(
                f"Array found at {path!r} — by-reference invariant violated (T-52-10)"
            )
        elif isinstance(obj, dict):
            for k, v in obj.items():
                _check_no_arrays(v, f"{path}.{k}")
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                _check_no_arrays(v, f"{path}[{i}]")

    _check_no_arrays(result)
