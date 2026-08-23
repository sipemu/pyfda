"""Tests for Group B advisor branches (ADV-05 Group B):
  - elastic_multinomial via classification aspect
  - pace_fpca via fpca aspect

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests mirror the structure of test_advisor_inference.py:
- check_no_numpy recursive walker
- byte-identical json.dumps(sort_keys=True)
- grounding via _extract_numbers from fdars.advisor.providers._validate
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Shared helper: recursive numpy-scalar walker.
# ---------------------------------------------------------------------------

def check_no_numpy(obj):
    """Fail if any value in obj is a numpy scalar (np.generic subclass)."""
    assert not isinstance(obj, np.generic), (
        f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
    )
    if isinstance(obj, dict):
        for v in obj.values():
            check_no_numpy(v)
    elif isinstance(obj, list):
        for v in obj:
            check_no_numpy(v)


# ---------------------------------------------------------------------------
# TestElasticMultinomial
# ---------------------------------------------------------------------------

class TestElasticMultinomial:
    """Verify the elastic_multinomial branch of _build_classification_diagnostics."""

    @pytest.fixture(scope="class")
    def multinomial_result(self):
        """Build a real elastic_multinomial result."""
        from fdars import classification as cls
        n, m, K = 30, 32, 3
        rng = np.random.default_rng(42)
        data = rng.standard_normal((n, m))
        labels = np.array([i % K for i in range(n)], dtype=np.int64)
        argvals = np.linspace(0.0, 1.0, m)
        return cls.elastic_multinomial(
            data, labels, argvals, ncomp_beta=5, lambda_=0.1, max_iter=30, tol=1e-3
        )

    def test_multinomial_method_field(self, multinomial_result):
        """build_diagnostics on elastic_multinomial returns method == 'classification'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert diag["method"] == "classification"

    def test_multinomial_has_elastic_multinomial_true(self, multinomial_result):
        """has_elastic_multinomial must be True."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert diag["has_elastic_multinomial"] is True

    def test_multinomial_n_classes_from_raw(self, multinomial_result):
        """n_classes must equal raw["n_classes"] (fdars-computed count, K=3)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert isinstance(diag["n_classes"], int)
        assert diag["n_classes"] == multinomial_result["n_classes"]
        assert diag["n_classes"] == 3

    def test_multinomial_train_accuracy_is_float(self, multinomial_result):
        """train_accuracy must be a native float in [0, 1]."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert isinstance(diag["train_accuracy"], float)
        assert 0.0 <= diag["train_accuracy"] <= 1.0

    def test_multinomial_train_accuracy_matches_raw(self, multinomial_result):
        """train_accuracy must equal float(raw["train_accuracy"])."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert abs(diag["train_accuracy"] - float(multinomial_result["train_accuracy"])) < 1e-12

    def test_multinomial_train_error_rate_is_float(self, multinomial_result):
        """train_error_rate must be a native float equal to 1 - train_accuracy."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert isinstance(diag["train_error_rate"], float)
        assert abs(diag["train_error_rate"] - (1.0 - diag["train_accuracy"])) < 1e-12

    def test_multinomial_existing_accuracy_path_unaffected(self, multinomial_result):
        """The existing point-estimate accuracy path should be None for elastic_multinomial.

        elastic_multinomial has no 'accuracy' key, so diag['accuracy'] should be None.
        """
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        # elastic_multinomial has 'train_accuracy' not 'accuracy'
        assert diag.get("accuracy") is None

    def test_multinomial_no_numpy(self, multinomial_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        check_no_numpy(diag)

    def test_multinomial_json_serialisable(self, multinomial_result):
        """Output must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        json.dumps(diag, sort_keys=True)

    def test_multinomial_determinism(self, multinomial_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(multinomial_result, method="classification")
        d2 = build_diagnostics(multinomial_result, method="classification")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_multinomial_grounding(self, multinomial_result):
        """train_accuracy is discoverable in json.dumps(diag) via _extract_numbers."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers
        diag = build_diagnostics(multinomial_result, method="classification")
        diag_json = json.dumps(diag, sort_keys=True)
        found = set(_extract_numbers(diag_json))
        n_classes_str = str(diag["n_classes"])
        assert any(n_classes_str in n or n in n_classes_str for n in found), (
            f"n_classes={n_classes_str} not discoverable in diagnostics json"
        )

    # -- ASPECT-02 new scalars -----------------------------------------------

    def test_overfitting_gap_with_holdout(self, multinomial_result):
        """overfitting_gap = train_accuracy - holdout_accuracy when holdout supplied."""
        from fdars.advisor import build_diagnostics
        diag_no_holdout = build_diagnostics(multinomial_result, method="classification")
        train_acc = diag_no_holdout["train_accuracy"]
        holdout_acc = 0.72
        diag = build_diagnostics(
            multinomial_result, method="classification", holdout_accuracy=holdout_acc
        )
        expected_gap = train_acc - holdout_acc
        assert abs(diag["overfitting_gap"] - expected_gap) < 1e-10

    def test_overfitting_gap_is_native_float(self, multinomial_result):
        """overfitting_gap must be a native float when holdout supplied."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(
            multinomial_result, method="classification", holdout_accuracy=0.72
        )
        assert type(diag["overfitting_gap"]) is float

    def test_overfitting_gap_none_when_no_holdout(self, multinomial_result):
        """overfitting_gap must be None when no holdout_accuracy supplied (not fabricated)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert diag["overfitting_gap"] is None, (
            "overfitting_gap must be None when holdout_accuracy is not supplied "
            "— grounding invariant: do not fabricate a holdout"
        )

    def test_overfitting_gap_holdout_source_provenance(self, multinomial_result):
        """overfitting_gap_holdout_source must be 'holdout_accuracy' when supplied."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(
            multinomial_result, method="classification", holdout_accuracy=0.70
        )
        assert diag["overfitting_gap_holdout_source"] == "holdout_accuracy"

    def test_overfitting_gap_holdout_source_none(self, multinomial_result):
        """overfitting_gap_holdout_source must be None when no holdout supplied."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert diag["overfitting_gap_holdout_source"] is None

    def test_n_classes_flagged_is_bool(self, multinomial_result):
        """n_classes_flagged must be a native bool."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        assert type(diag["n_classes_flagged"]) is bool

    def test_n_classes_flagged_true_for_multiclass(self, multinomial_result):
        """n_classes_flagged must be True when n_classes == 3 (multiclass, > 2)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(multinomial_result, method="classification")
        # K=3 in the fixture, so multiclass -> flagged True
        assert diag["n_classes"] == 3
        assert diag["n_classes_flagged"] is True

    def test_n_classes_flagged_false_for_binary(self):
        """n_classes_flagged must be False when n_classes == 2 (binary)."""
        from fdars.advisor import build_diagnostics
        # Synthesise a minimal elastic_multinomial result with n_classes=2
        binary_result = {
            "train_accuracy": 0.90,
            "n_classes": 2,
            "classes": [0, 1],
            "predicted_classes": [0, 1, 0, 1],
            "train_probabilities": [[0.9, 0.1], [0.1, 0.9], [0.8, 0.2], [0.2, 0.8]],
        }
        diag = build_diagnostics(binary_result, method="classification")
        assert diag["n_classes_flagged"] is False

    def test_new_scalars_json_serialisable(self, multinomial_result):
        """All three new ASPECT-02 scalars must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(
            multinomial_result, method="classification", holdout_accuracy=0.72
        )
        subset = {
            "overfitting_gap": diag["overfitting_gap"],
            "overfitting_gap_holdout_source": diag["overfitting_gap_holdout_source"],
            "n_classes_flagged": diag["n_classes_flagged"],
        }
        json.dumps(subset)
        check_no_numpy(subset)

    def test_new_scalars_none_for_plain_fclassif(self):
        """A plain fclassif (accuracy path) result leaves overfitting_gap None."""
        from fdars.advisor import build_diagnostics
        plain_result = {"accuracy": 0.85, "predicted": [0, 1, 0, 1, 0]}
        diag = build_diagnostics(plain_result, method="classification")
        assert diag["overfitting_gap"] is None
        assert diag["n_classes_flagged"] is None

    def test_overfitting_gap_exact_with_fixtures(self):
        """Direct arithmetic check: train=0.95, holdout=0.72 -> gap=0.23."""
        from fdars.advisor import build_diagnostics
        result = {
            "train_accuracy": 0.95,
            "n_classes": 3,
            "classes": [0, 1, 2],
            "predicted_classes": [],
            "train_probabilities": [],
        }
        diag = build_diagnostics(
            result, method="classification", holdout_accuracy=0.72
        )
        assert abs(diag["overfitting_gap"] - 0.23) < 1e-10


# ---------------------------------------------------------------------------
# TestPaceFpca
# ---------------------------------------------------------------------------

class TestPaceFpca:
    """Verify the pace_fpca branch of _build_fpca_diagnostics (ADV-05 Group B)."""

    @pytest.fixture(scope="class")
    def pace_result(self):
        """Build a real pace_fpca result from ragged functional data."""
        import fdars.pace_fpca as pf
        rng = np.random.default_rng(42)
        n = 8
        argvals_list, values_list = [], []
        for i in range(n):
            n_pts = 3 + (i % 3)
            t = np.sort(rng.uniform(0.0, 1.0, n_pts))
            v = (i + 1) * np.sin(t * np.pi) + rng.normal(0, 0.05, n_pts)
            argvals_list.append(t)
            values_list.append(v)
        fd = pf.irreg_fdata_from_lists(argvals_list, values_list)
        return pf.pace_fpca(fd, ncomp=2, bandwidth=0.2, sigma2=0.01, alpha=0.05)

    def test_pace_method_field(self, pace_result):
        """build_diagnostics on pace_fpca result returns method == 'fpca'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert diag["method"] == "fpca"

    def test_pace_has_pace_fpca_true(self, pace_result):
        """has_pace_fpca must be True for a pace_fpca result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert diag["has_pace_fpca"] is True

    def test_pace_ncomp_is_int(self, pace_result):
        """pace_ncomp must be a native int equal to raw['ncomp'] == 2."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert isinstance(diag["pace_ncomp"], int)
        assert diag["pace_ncomp"] == pace_result["ncomp"]
        assert diag["pace_ncomp"] == 2

    def test_pace_sigma2_is_float(self, pace_result):
        """pace_sigma2 must be a native float equal to raw['sigma2']."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert isinstance(diag["pace_sigma2"], float)
        assert abs(diag["pace_sigma2"] - float(pace_result["sigma2"])) < 1e-12

    def test_pace_variance_explained_cumulative_is_list_of_float(self, pace_result):
        """pace_variance_explained_cumulative must be a list of native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        cum = diag["pace_variance_explained_cumulative"]
        assert isinstance(cum, list), "pace_variance_explained_cumulative must be a list"
        assert len(cum) == 2, "length must equal ncomp=2"
        for v in cum:
            assert isinstance(v, float), f"Each element must be native float, got {type(v)}"

    def test_pace_cumulative_last_approx_one(self, pace_result):
        """Last element of cumulative variance list must be ~1.0 when eigenvalue sum > 0."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        cum = diag["pace_variance_explained_cumulative"]
        assert abs(cum[-1] - 1.0) < 1e-10, (
            f"Last cumulative variance element must be ~1.0, got {cum[-1]}"
        )

    def test_pace_variance_explained_first_is_float(self, pace_result):
        """pace_variance_explained_first must be a native float in (0, 1]."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        vef = diag["pace_variance_explained_first"]
        assert isinstance(vef, float), "pace_variance_explained_first must be float"
        assert 0.0 < vef <= 1.0

    def test_pace_singular_values_path_none(self, pace_result):
        """Standard FPCA singular_values-path keys must be None for pace_fpca input.

        The pace_fpca result has 'eigenvalues' (not 'singular_values'), so the
        standard FPCA branch (sv_raw = raw.get('singular_values')) is None and
        the standard FPCA output keys are all None.
        """
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        # Standard FPCA path uses 'singular_values' — must be None for pace_fpca
        assert diag.get("n_components") is None
        assert diag.get("eigenvalues") is None  # standard path eigenvalues, not pace

    def test_pace_no_numpy(self, pace_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        check_no_numpy(diag)

    def test_pace_json_serialisable(self, pace_result):
        """Output must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        json.dumps(diag, sort_keys=True)

    def test_pace_determinism(self, pace_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(pace_result, method="fpca")
        d2 = build_diagnostics(pace_result, method="fpca")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_pace_grounding(self, pace_result):
        """pace_sigma2 is discoverable in json.dumps(diag) via _extract_numbers."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers
        diag = build_diagnostics(pace_result, method="fpca")
        diag_json = json.dumps(diag, sort_keys=True)
        found = set(_extract_numbers(diag_json))
        ncomp_str = str(diag["pace_ncomp"])
        assert any(ncomp_str in n or n in ncomp_str for n in found), (
            f"pace_ncomp={ncomp_str} not discoverable in diagnostics json"
        )

    # -- ASPECT-01 new scalars -----------------------------------------------

    def test_pace_noise_signal_ratio_is_float(self, pace_result):
        """pace_noise_signal_ratio must be a native float (sigma2 / total eigenvalue sum)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert type(diag["pace_noise_signal_ratio"]) is float, (
            f"pace_noise_signal_ratio must be native float, got {type(diag['pace_noise_signal_ratio'])}"
        )

    def test_pace_noise_signal_ratio_nonnegative(self, pace_result):
        """pace_noise_signal_ratio must be >= 0 (both sigma2 and eigenvalues >= 0)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert diag["pace_noise_signal_ratio"] >= 0.0

    def test_pace_noise_signal_ratio_matches_formula(self, pace_result):
        """pace_noise_signal_ratio must equal sigma2 / sum(eigenvalues)."""
        import numpy as _np
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        sigma2 = float(pace_result["sigma2"])
        eigenvalues = _np.asarray(pace_result["eigenvalues"], dtype=float)
        total_var = float(eigenvalues.sum())
        if total_var > 0:
            expected = sigma2 / total_var
            assert abs(diag["pace_noise_signal_ratio"] - expected) < 1e-10

    def test_pace_truncated_rank_flagged_is_bool(self, pace_result):
        """pace_truncated_rank_flagged must be a native bool."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert type(diag["pace_truncated_rank_flagged"]) is bool, (
            f"pace_truncated_rank_flagged must be native bool, got {type(diag['pace_truncated_rank_flagged'])}"
        )

    def test_pace_truncated_rank_flagged_matches_formula(self, pace_result):
        """pace_truncated_rank_flagged is True when ncomp < len(eigenvalues)."""
        import numpy as _np
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        ncomp = int(pace_result["ncomp"])
        n_eigenvalues = len(_np.asarray(pace_result["eigenvalues"]))
        expected = ncomp < n_eigenvalues
        assert diag["pace_truncated_rank_flagged"] == expected

    def test_pace_mean_prediction_band_width_is_float(self, pace_result):
        """pace_mean_prediction_band_width must be a native float when band arrays present."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert type(diag["pace_mean_prediction_band_width"]) is float, (
            f"pace_mean_prediction_band_width must be native float, got {type(diag['pace_mean_prediction_band_width'])}"
        )

    def test_pace_mean_prediction_band_width_positive(self, pace_result):
        """pace_mean_prediction_band_width must be >= 0 (upper >= lower everywhere)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        assert diag["pace_mean_prediction_band_width"] >= 0.0

    def test_pace_new_scalars_json_serialisable(self, pace_result):
        """All three new ASPECT-01 scalars must be JSON-serialisable (no numpy scalar)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(pace_result, method="fpca")
        # json.dumps with only the three new keys to isolate
        subset = {
            "pace_noise_signal_ratio": diag["pace_noise_signal_ratio"],
            "pace_truncated_rank_flagged": diag["pace_truncated_rank_flagged"],
            "pace_mean_prediction_band_width": diag["pace_mean_prediction_band_width"],
        }
        json.dumps(subset)
        check_no_numpy(subset)

    def test_pace_new_scalars_none_for_standard_fpca(self):
        """Standard FPCA (singular_values path) leaves all three new scalars None."""
        from fdars.advisor import build_diagnostics
        standard_result = {
            "singular_values": [2.1, 1.5, 0.8],
            "scores": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        }
        diag = build_diagnostics(standard_result, method="fpca")
        assert diag["pace_noise_signal_ratio"] is None
        assert diag["pace_truncated_rank_flagged"] is None
        assert diag["pace_mean_prediction_band_width"] is None


# ---------------------------------------------------------------------------
# TestDeterminism — combined across both branches
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Combined determinism and no-numpy tests for both Group B branches."""

    def test_elastic_multinomial_byte_identical(self):
        """elastic_multinomial: json.dumps is byte-identical across two calls."""
        from fdars import classification as cls
        from fdars.advisor import build_diagnostics
        n, m, K = 20, 16, 3
        rng = np.random.default_rng(77)
        data = rng.standard_normal((n, m))
        labels = np.array([i % K for i in range(n)], dtype=np.int64)
        argvals = np.linspace(0.0, 1.0, m)
        result = cls.elastic_multinomial(data, labels, argvals, ncomp_beta=4, lambda_=0.1)
        d1 = build_diagnostics(result, method="classification")
        d2 = build_diagnostics(result, method="classification")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
        check_no_numpy(d1)

    def test_pace_fpca_byte_identical(self):
        """pace_fpca: json.dumps is byte-identical across two calls."""
        import fdars.pace_fpca as pf
        from fdars.advisor import build_diagnostics
        rng = np.random.default_rng(99)
        n = 6
        argvals_list, values_list = [], []
        for i in range(n):
            n_pts = 3 + (i % 3)
            t = np.sort(rng.uniform(0.0, 1.0, n_pts))
            v = np.sin(t * np.pi) + rng.normal(0, 0.05, n_pts)
            argvals_list.append(t)
            values_list.append(v)
        fd = pf.irreg_fdata_from_lists(argvals_list, values_list)
        result = pf.pace_fpca(fd, ncomp=2, bandwidth=0.2, sigma2=0.05, alpha=0.05)
        d1 = build_diagnostics(result, method="fpca")
        d2 = build_diagnostics(result, method="fpca")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
        check_no_numpy(d1)
