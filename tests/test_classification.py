"""Tests for fdars.classification.elastic_multinomial (CLASS-01).

Task 4: elastic_multinomial binding — CR-01 negative/non-contiguous-label guard,
(n,K) proba transposition guard, class_models omitted.
Task 5: import-path coverage (TestClassificationImportPaths).
"""

import numpy as np
import pytest

from fdars import classification as cls


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

def _make_multiclass_data(n=30, m=32, K=3, seed=42):
    """Return (data, labels, argvals) for K-class synthetic functional data."""
    rng = np.random.default_rng(seed)
    data = rng.standard_normal((n, m))
    labels = np.array([i % K for i in range(n)], dtype=np.int64)
    argvals = np.linspace(0.0, 1.0, m)
    return data, labels, argvals


# ---------------------------------------------------------------------------
# Task 4: elastic_multinomial binding
# ---------------------------------------------------------------------------

class TestElasticMultinomial:
    """Tests for fdars.classification.elastic_multinomial (CLASS-01)."""

    @pytest.fixture(scope="class")
    def result(self):
        data, labels, argvals = _make_multiclass_data(n=30, m=32, K=3)
        return cls.elastic_multinomial(
            data, labels, argvals, ncomp_beta=5, lambda_=0.1, max_iter=30, tol=1e-3
        )

    def test_multinomial_smoke(self, result):
        """Result dict must have exactly 5 keys and NOT contain class_models."""
        expected_keys = {
            "n_classes", "classes", "train_probabilities",
            "predicted_classes", "train_accuracy",
        }
        assert set(result.keys()) == expected_keys, (
            f"Key mismatch: got {set(result.keys())}"
        )
        assert "class_models" not in result, "class_models must NOT be exposed (CLASS-01)"
        assert result["n_classes"] == 3, f"n_classes: expected 3, got {result['n_classes']}"

    def test_multinomial_proba_shape(self, result):
        """train_probabilities must be shape (n, K) with K=3 != n=30 (transposition guard)."""
        n, K = 30, 3
        proba = result["train_probabilities"]
        assert proba.shape == (n, K), (
            f"train_probabilities shape: expected ({n}, {K}), got {proba.shape}"
        )
        # K != n so a transpose cannot silently pass
        assert K != n, "Fixture must have K != n for transposition guard"
        # Each row must sum to 1.0 (probability simplex)
        row_sums = proba.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6), (
            f"train_probabilities rows do not sum to 1.0: {row_sums[:5]}"
        )

    def test_multinomial_accuracy_range(self, result):
        """train_accuracy must be in [0, 1]."""
        acc = result["train_accuracy"]
        assert 0.0 <= acc <= 1.0, f"train_accuracy out of range: {acc}"

    def test_negative_label_guard(self):
        """Labels containing -1 must raise ValueError (CR-01 guard before i64->usize cast)."""
        data, _, argvals = _make_multiclass_data(n=30, m=32, K=3)
        n = 30
        bad_labels = np.array([-1, 0, 1] * (n // 3), dtype=np.int64)
        with pytest.raises(ValueError, match="non-negative"):
            cls.elastic_multinomial(
                data, bad_labels, argvals, ncomp_beta=5, lambda_=0.1,
                max_iter=5, tol=1e-3
            )

    def test_noncontiguous_label_guard(self):
        """Non-contiguous labels [0,2,...] must raise ValueError (core rejects via to_pyresult)."""
        data, _, argvals = _make_multiclass_data(n=30, m=32, K=3)
        n = 30
        # Labels skip 1: [0, 2, 0, 2, ...] — core rejects non-contiguous range
        bad_labels = np.array([0, 2] * (n // 2), dtype=np.int64)
        with pytest.raises(ValueError, match="contiguous"):
            cls.elastic_multinomial(
                data, bad_labels, argvals, ncomp_beta=5, lambda_=0.1,
                max_iter=5, tol=1e-3
            )


# ---------------------------------------------------------------------------
# Task 5: Import-path coverage
# ---------------------------------------------------------------------------

class TestClassificationImportPaths:
    """Both import path patterns must resolve for elastic_multinomial."""

    def test_submodule_attribute_access(self):
        """Attribute access via fdars.classification resolves to a callable."""
        import fdars
        assert callable(fdars.classification.elastic_multinomial), (
            "fdars.classification.elastic_multinomial must be callable"
        )

    def test_from_import(self):
        """from fdars.classification import elastic_multinomial resolves to callable."""
        from fdars.classification import elastic_multinomial  # noqa: F401
        assert callable(elastic_multinomial)
