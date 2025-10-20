"""Tests for model evaluation metrics."""
import numpy as np

from trainer.model_evaluation import precision_at_k


def test_precision_at_k_perfect():
    """Test precision@k with perfect predictions."""
    y_true = np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
    y_score = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])

    precision = precision_at_k(y_true, y_score, k=0.3)  # Top 30% = 3 predictions
    assert precision == 1.0  # All 3 top predictions are correct


def test_precision_at_k_zero():
    """Test precision@k with worst predictions."""
    y_true = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
    y_score = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])

    precision = precision_at_k(y_true, y_score, k=0.3)  # Top 30%
    assert precision == 0.0  # None of the top predictions are correct


def test_precision_at_k_small_k():
    """Test precision@k with very small k."""
    y_true = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    y_score = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])

    precision = precision_at_k(y_true, y_score, k=0.1)  # Top 10% = 1 prediction
    assert precision == 1.0


def test_precision_at_k_bounds():
    """Test precision@k output is between 0 and 1."""
    y_true = np.random.randint(0, 2, size=100)
    y_score = np.random.rand(100)

    precision = precision_at_k(y_true, y_score, k=0.05)
    assert 0.0 <= precision <= 1.0
