"""Aspect × provider offline cross-coverage matrix tests (QUAL-01, QUAL-02).

QUAL-01: Each supported aspect's diagnostics flow through both a native fake
provider AND a fallback fake provider, producing a grounded Advice — proving
the aspect × provider CONTRACT is exercised network-free and deterministically.

QUAL-02: Introspection confirmation that tests/test_advisor_live_integration.py
holds exactly one env-gated live test per provider (openai, gemini, ollama)
and that all gates are falsy in a clean environment.

This file DOES NOT duplicate:
  - Per-aspect determinism tests (already in tests/test_advisor.py)
  - Per-adapter machinery tests (already in tests/test_advisor_providers.py)
  - Per-adapter stub/fixture tests (tests/test_advisor_openai/ollama/gemini.py)
  - Live provider integration tests (tests/test_advisor_live_integration.py)

It only adds the CROSS-PRODUCT: aspect diagnostics × provider machinery.

Requirements covered:
    QUAL-01  Aspect × {native, fallback} offline cross-coverage
    QUAL-02  Live-integration contract: one gated test per provider, clean skip
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

pydantic = pytest.importorskip("pydantic")


# ---------------------------------------------------------------------------
# Local fake providers (same pattern as tests/test_advisor_providers.py,
# kept local so this file is self-contained per plan instructions)
# ---------------------------------------------------------------------------


class _FakeNativeProvider:
    """Simulates a native-structured-output provider.

    supports_native_structured_output=True tells ValidateAndRetry to skip the
    repair loop and return the provider result directly via schema.model_validate.
    """

    name = "fake-native"
    model = "fake-model"
    supports_native_structured_output = True

    def __init__(self, response: dict) -> None:
        self._response = response

    def complete_structured(self, schema: type, messages: list, system: str) -> object:
        return schema.model_validate(self._response)


class _FakeFallbackProvider:
    """Simulates a non-native provider that returns a raw dict.

    supports_native_structured_output=False tells ValidateAndRetry to run the
    validate-and-retry loop on the returned raw dict.
    """

    name = "fake-fallback"
    model = "fake-model"
    supports_native_structured_output = False

    def __init__(self, response: dict) -> None:
        self._response = response

    def complete_structured(self, schema: type, messages: list, system: str) -> object:
        return self._response


# ---------------------------------------------------------------------------
# Aspect fixtures — tiny, deterministic, no RNG, no wall-clock, no network.
# Each entry:  (aspect, result_dict, build_kwargs, evidence_key)
#   evidence_key: the key in the built diagnostics whose value is used to
#   build the evidence string so grounding passes.
# ---------------------------------------------------------------------------

# Clustering — from test_advisor.py#test_clustering_offline_with_synthetic
_CLUSTERING_RESULT = {
    "centers": [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]],
    "cluster": [0, 0, 1, 1],
    "k": 2,
}

# Depth — from test_advisor.py#test_depth_build_diagnostics_basic
_DEPTH_SCORES = np.array([0.05, 0.2, 0.5, 0.8, 0.95, 0.3, 0.45, 0.6, 0.15, 0.7])

# Outliers — from test_advisor.py#test_outliers_lrt_shape
_OUTLIERS_RESULT = {
    "outliers": np.array([False, False, True, False, False]),
    "threshold": 2.47,
}

# Classification — from test_advisor.py#test_classification_point_estimate
_CLASSIFICATION_RESULT = {
    "predicted": np.array([0, 0, 1, 1, 2, 2]),
    "accuracy": 0.8333,
}

# Represent — from test_advisor.py#test_represent_dict_form_basic
_REPRESENT_RESULT = {
    "data": np.ones((20, 50)),
    "argvals": np.linspace(0, 1, 50),
}

# Regression — from test_advisor.py#test_regression_fregre_lm_basic
_REGRESSION_RESULT = {
    "fitted_values": np.array([1.1, 2.0, 3.2, 0.9, 2.5]),
    "residuals": np.array([0.1, -0.2, 0.3, -0.1, 0.2]),
    "beta_t": np.linspace(-0.5, 0.5, 30),
    "r_squared": 0.82,
    "coefficients": np.array([0.3, -0.1, 0.05]),
    "intercept": 0.15,
}

# Regression CV — from test_advisor.py#test_regression_cv_fregre_cv_basic
_REGRESSION_CV_RESULT = {
    "optimal_k": 3,
    "min_cv_error": 0.045,
    "k_values": np.array([1, 2, 3, 4, 5]),
    "cv_errors": np.array([0.12, 0.07, 0.045, 0.046, 0.048]),
    "fold_errors": np.array([0.04, 0.05, 0.04, 0.05, 0.04]),
}

# SPM — from test_advisor.py#TestSpm._spm_fixture
_SPM_RESULT = {
    "t2": np.array([1.2, 3.4, 0.8, 5.1, 2.3, 4.0, 1.5, 2.7, 0.9, 3.1]),
    "spe": np.array([0.05, 0.12, 0.03, 0.25, 0.08, 0.18, 0.04, 0.09, 0.02, 0.11]),
    "t2_limit": 4.5,
    "spe_limit": 0.20,
    "eigenvalues": np.array([2.1, 0.8, 0.3]),
}

# Alignment — from advisor/__init__.py#_selfcheck_alignment_diagnostics
_ALIGNMENT_RESULT = {
    "mean": [0.0, 1.0, 2.0, 1.0, 0.0],
    "aligned_data": [
        [0.0, 1.0, 2.0, 1.0, 0.0],
        [0.1, 1.1, 2.0, 0.9, 0.0],
    ],
    "converged": True,
    "n_iter": 3,
}
_ALIGNMENT_ARGVALS = [0.0, 0.25, 0.5, 0.75, 1.0]

# FPCA — from test_advisor.py#test_fpca_output_unchanged_after_refactor
_FPCA_RESULT = {
    "singular_values": np.array([3.0, 1.5, 0.8]),
    "scores": np.zeros((10, 3)),
}

# Basis — from test_advisor.py#test_build_diagnostics_deterministic
_BASIS_RESULT = {
    "n_basis_values": [5, 8, 10],
    "gcv": [0.5, 0.3, 0.4],
    "edf": [3.0, 5.0, 7.0],
}

# Smoothing — simple GCV curve fixture
_SMOOTHING_RESULT = {
    "lambda_values": np.array([0.001, 0.01, 0.1, 1.0]),
    "gcv": np.array([0.5, 0.3, 0.4, 0.8]),
    "edf": np.array([10.0, 8.0, 5.0, 3.0]),
}

# ---------------------------------------------------------------------------
# NEW: ASPECT-05 fixtures — PACE-FPCA, elastic-multinomial, ITP
# All synthetic, offline, no RNG, no network.
# ---------------------------------------------------------------------------

# PACE-FPCA (aspect_id="fpca_pace", method="fpca")
# Trigger in fpca.py: "eigenvalues" in raw (unambiguous — standard FPCA uses "singular_values").
# ncomp=2 < len(eigenvalues)=3 → pace_truncated_rank_flagged=True.
# sigma2=0.05, total_signal=5.0 → pace_noise_signal_ratio=0.01.
# fitted_lower/upper are (2,3) 2-D lists → pace_mean_prediction_band_width is a real float.
_PACE_FPCA_RESULT = {
    "eigenvalues": [3.0, 1.5, 0.5],
    "ncomp": 2,
    "sigma2": 0.05,
    "fitted_lower": [[0.1, 0.2, 0.15], [0.05, 0.1, 0.08]],
    "fitted_upper": [[0.5, 0.6, 0.55], [0.45, 0.5, 0.48]],
}

# elastic-multinomial (aspect_id="classification_elastic", method="classification")
# Trigger in classification.py: "train_accuracy" in raw.
# n_classes=3 → n_classes_flagged=True; holdout_accuracy=0.72 supplied → overfitting_gap=0.23.
_ELASTIC_RESULT = {
    "train_accuracy": 0.95,
    "n_classes": 3,
}

# ITP (aspect_id="inference_itp", method="inference")
# Trigger in inference.py: "adjusted_pvalues" in raw.
# adjusted_pvalues: first element 0.02 < 0.05 → itp_detected_at_0.05=True, itp_min=0.02.
# 1 of 5 significant → itp_n_significant_0.05=1, itp_fraction=0.2.
_ITP_RESULT = {
    "adjusted_pvalues": [0.02, 0.8, 0.9, 0.85, 0.6],
    "raw_pvalues": [0.01, 0.6, 0.7, 0.65, 0.4],
    "n_basis": 5,
    "n_perm": 99,
}


# ---------------------------------------------------------------------------
# Build the evidence_value from real diagnostics for each aspect so that the
# grounding check in advise() passes.  The helper also returns the key used.
# ---------------------------------------------------------------------------


def _build_grounded_advice_dict(diag: dict) -> dict:
    """Construct an Advice-shaped dict whose evidence cites a real value from diag.

    Scans the diagnostics for the first numeric (int/float) value at a top-level
    key and uses it to build an evidence string.  If no numeric value is found
    (all None), falls back to qualitative evidence — the grounding check passes
    for strings with no numeric tokens.
    """
    evidence_str = None
    for k, v in diag.items():
        if isinstance(v, (int, float)) and v is not None and k != "method":
            evidence_str = f"{k}={v}"
            break

    if evidence_str is None:
        # Qualitative fallback — no numbers to cite, so grounding accepts it
        evidence_str = "Analysis completed with available diagnostics."

    return {
        "interpretation": f"Diagnostic analysis for {diag.get('method', 'unknown')} completed.",
        "recommendations": [
            {
                "action": "Review the diagnostics carefully.",
                "kind": "parameter",
                "rationale": "The diagnostics show the results of the analysis.",
                "expected_effect": "Better understanding of the results.",
                "evidence": [evidence_str],
            }
        ],
        "caveats": ["Based on synthetic diagnostics."],
    }


# ---------------------------------------------------------------------------
# Parametrized aspect × provider matrix (QUAL-01)
# ---------------------------------------------------------------------------

# Each tuple: (aspect_id, result, build_kwargs)
# build_kwargs is passed as **kwargs to build_diagnostics alongside method=aspect_id
_ASPECT_FIXTURES = [
    ("clustering", _CLUSTERING_RESULT, {}),
    ("depth", _DEPTH_SCORES, {"method_name": "fraiman_muniz"}),
    ("outliers", _OUTLIERS_RESULT, {}),
    ("classification", _CLASSIFICATION_RESULT, {"n_classes": 3}),
    ("represent", _REPRESENT_RESULT, {}),
    ("regression", _REGRESSION_RESULT, {}),
    ("regression_cv", _REGRESSION_CV_RESULT, {}),
    ("spm", _SPM_RESULT, {}),
    ("alignment", _ALIGNMENT_RESULT, {"argvals": _ALIGNMENT_ARGVALS}),
    ("fpca", _FPCA_RESULT, {}),
    ("basis", _BASIS_RESULT, {}),
    ("smoothing", _SMOOTHING_RESULT, {}),
    # ASPECT-05: three new aspects — PACE-FPCA, elastic-multinomial, ITP.
    # aspect_id is a unique label distinct from the method name (which is the same
    # base method but a different result shape / diagnostic branch).
    ("fpca_pace", _PACE_FPCA_RESULT, {}),
    ("classification_elastic", _ELASTIC_RESULT, {"holdout_accuracy": 0.72}),
    ("inference_itp", _ITP_RESULT, {}),
]

_ASPECT_IDS = [t[0] for t in _ASPECT_FIXTURES]
_PROVIDER_KINDS = ["native", "fallback"]


def _make_provider(kind: str, advice_dict: dict):
    """Return a fake provider of the given kind pre-loaded with advice_dict."""
    if kind == "native":
        return _FakeNativeProvider(advice_dict)
    else:
        return _FakeFallbackProvider(advice_dict)


@pytest.mark.parametrize(
    "aspect, result, build_kwargs",
    _ASPECT_FIXTURES,
    ids=_ASPECT_IDS,
)
@pytest.mark.parametrize("provider_kind", _PROVIDER_KINDS)
def test_aspect_provider_matrix(aspect, result, build_kwargs, provider_kind):
    """QUAL-01: Each aspect × {native, fallback} provider yields a grounded Advice.

    Contract under test:
      build_diagnostics(result, method=aspect, **build_kwargs)
        → deterministic offline diagnostics dict
        → fake provider returns evidence citing a REAL diagnostics value
        → advise(diag, provider=fake) runs _check_grounding
        → returns a validated Advice instance

    Network-free, key-free, provider-SDK-free.
    """
    from fdars.advisor import Advice, advise, build_diagnostics

    # Mapping from aspect_id to the method string accepted by build_diagnostics.
    # For the original 12 aspects, aspect_id == method.  For the three new
    # ASPECT-05 fixtures, the id is more specific (e.g. "fpca_pace") but the
    # underlying method dispatch key is the base method name.
    _ASPECT_ID_TO_METHOD = {
        "fpca_pace": "fpca",
        "classification_elastic": "classification",
        "inference_itp": "inference",
    }
    method = _ASPECT_ID_TO_METHOD.get(aspect, aspect)

    # Step 1: build diagnostics offline (no network, no RNG)
    if aspect == "alignment":
        # alignment uses argvals as a positional-ish named arg
        argvals = build_kwargs.get("argvals")
        diag = build_diagnostics(result, method=method, argvals=argvals)
    elif aspect in ("classification", "classification_elastic"):
        # classification_elastic: forward holdout_accuracy so overfitting_gap is populated
        n_classes = build_kwargs.get("n_classes")
        holdout_accuracy = build_kwargs.get("holdout_accuracy")
        diag = build_diagnostics(
            result, method=method,
            n_classes=n_classes,
            holdout_accuracy=holdout_accuracy,
        )
    else:
        diag = build_diagnostics(result, method=method)

    assert isinstance(diag, dict), f"build_diagnostics({aspect!r}) must return a dict"
    assert diag.get("method") == method, (
        f"diag['method'] must be {method!r} (aspect_id={aspect!r}), "
        f"got {diag.get('method')!r}"
    )

    # Step 2: build a grounded advice_dict using a REAL value from diag
    advice_dict = _build_grounded_advice_dict(diag)

    # Step 3: construct the fake provider
    provider = _make_provider(provider_kind, advice_dict)

    # Step 4: call advise() — this exercises the full aspect × provider path
    # including _check_grounding (GROUND-03) centralized in advise()
    result_advice = advise(
        diag,
        task="interpretation",
        domain_context=f"matrix-test: {aspect}/{provider_kind}",
        provider=provider,
    )

    # Step 5: assert the result is a valid Advice instance
    assert isinstance(result_advice, Advice), (
        f"advise({aspect!r}, provider={provider_kind!r}) must return Advice, "
        f"got {type(result_advice).__name__!r}"
    )
    assert result_advice.interpretation, (
        f"Advice.interpretation must be non-empty for {aspect!r}/{provider_kind!r}"
    )
    assert isinstance(result_advice.recommendations, list), (
        f"Advice.recommendations must be a list for {aspect!r}/{provider_kind!r}"
    )


def test_matrix_no_provider_sdk_imported():
    """QUAL-01 guardrail: running the matrix imports no provider SDK at collection time.

    The parametrized tests above must exercise the provider machinery WITHOUT
    importing anthropic, openai, google.genai, or ollama.  This test asserts
    that after all matrix tests have run, those modules are absent from sys.modules.
    """
    forbidden = ("anthropic", "openai", "google.genai", "ollama")
    leaked = [mod for mod in forbidden if mod in sys.modules]
    assert not leaked, (
        f"Provider SDK(s) leaked into sys.modules during matrix tests: {leaked!r}. "
        "Fake providers must not import any real SDK."
    )


# ---------------------------------------------------------------------------
# QUAL-02: Live-integration contract confirmation
# ---------------------------------------------------------------------------


def test_live_integration_contract(monkeypatch):
    """QUAL-02: Introspect test_advisor_live_integration.py without running it.

    Asserts the env-gated live-test contract holds:
    1. Exactly three live tests exist — one each for openai, gemini, ollama.
    2. Module-level gate booleans are all False when env vars are absent.
    3. Importing the module pulls in no provider SDK.

    No live provider call is made; this only confirms the existing file's shape.
    """
    import importlib
    import importlib.util
    import pathlib

    # Clear all provider SDK entries from sys.modules before importing the
    # live-integration module so the post-import check is reliable.
    sdk_keys_before = {k for k in sys.modules if k in (
        "anthropic", "openai", "google", "google.genai", "ollama"
    )}

    # Ensure a clean env for the gate check — monkeypatch wipes integration flags
    monkeypatch.delenv("FDARS_INTEGRATION", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    # Reload the module under the clean env so its module-level gate expressions
    # are re-evaluated with empty env.  We use importlib to avoid any import cache
    # issues when the module was already imported in this process.
    live_module_path = (
        pathlib.Path(__file__).parent / "test_advisor_live_integration.py"
    )
    assert live_module_path.exists(), (
        f"test_advisor_live_integration.py not found at {live_module_path}"
    )

    spec = importlib.util.spec_from_file_location(
        "test_advisor_live_integration_fresh", live_module_path
    )
    live_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(live_mod)

    # -----------------------------------------------------------------------
    # Assert 1: Exactly one live test per provider (openai, gemini, ollama)
    # -----------------------------------------------------------------------
    live_test_names = [
        name for name in dir(live_mod)
        if name.startswith("test_live")
    ]
    assert len(live_test_names) == 3, (
        f"Expected exactly 3 live tests (one per provider), "
        f"found {len(live_test_names)}: {live_test_names!r}"
    )

    # Each provider must have exactly one test
    providers_covered = {"openai", "gemini", "ollama"}
    for provider in providers_covered:
        matching = [n for n in live_test_names if provider in n]
        assert len(matching) == 1, (
            f"Expected exactly 1 live test for {provider!r}, "
            f"found {len(matching)}: {matching!r}"
        )

    # -----------------------------------------------------------------------
    # Assert 2: All gate booleans are False in a clean environment
    # -----------------------------------------------------------------------
    # The live module defines _OPENAI_GATE, _GEMINI_GATE, _OLLAMA_GATE at
    # module level.  With no env vars set they must all be falsy.
    assert hasattr(live_mod, "_OPENAI_GATE"), (
        "test_advisor_live_integration must define _OPENAI_GATE at module level"
    )
    assert hasattr(live_mod, "_GEMINI_GATE"), (
        "test_advisor_live_integration must define _GEMINI_GATE at module level"
    )
    assert hasattr(live_mod, "_OLLAMA_GATE"), (
        "test_advisor_live_integration must define _OLLAMA_GATE at module level"
    )

    assert not live_mod._OPENAI_GATE, (
        f"_OPENAI_GATE must be False in a clean env (no FDARS_INTEGRATION / OPENAI_API_KEY), "
        f"got {live_mod._OPENAI_GATE!r}"
    )
    assert not live_mod._GEMINI_GATE, (
        f"_GEMINI_GATE must be False in a clean env (no FDARS_INTEGRATION / GEMINI_API_KEY), "
        f"got {live_mod._GEMINI_GATE!r}"
    )
    # _OLLAMA_GATE depends on a TCP connection — in CI with no Ollama daemon it
    # must also be False.  We assert it is falsy, not that it is exactly False,
    # since it could be False due to either the master gate or the TCP check.
    assert not live_mod._OLLAMA_GATE, (
        f"_OLLAMA_GATE must be False when FDARS_INTEGRATION is unset, "
        f"got {live_mod._OLLAMA_GATE!r}"
    )

    # -----------------------------------------------------------------------
    # Assert 3: Importing the module does not import any provider SDK
    # -----------------------------------------------------------------------
    sdk_keys_after = {k for k in sys.modules if k in (
        "anthropic", "openai", "google", "google.genai", "ollama"
    )}
    newly_imported_sdks = sdk_keys_after - sdk_keys_before
    assert not newly_imported_sdks, (
        f"Importing test_advisor_live_integration pulled in provider SDK(s): "
        f"{newly_imported_sdks!r}. SDK imports must stay inside test bodies only."
    )
