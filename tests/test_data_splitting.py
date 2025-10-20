"""Tests for data splitting logic."""
import numpy as np
import pandas as pd
import pytest

from trainer.data_preprocessing import compute_scale_pos_weight, time_ordered_split


@pytest.fixture
def sample_data():
    """Create sample payment data for testing."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    data = {
        "user_id": np.repeat(range(20), 5),
        "payment_date": np.tile(dates[:5], 20),
    }
    # Add a random is_churn column (binary target)
    data["is_churn"] = np.random.randint(0, 2, size=100)
    return pd.DataFrame(data)


def test_time_ordered_split(sample_data):
    """Test time-ordered splitting returns correct shapes."""
    feature_cols = ["payment_date"]
    X_train, y_train, X_val, y_val, X_test, y_test = time_ordered_split(
        sample_data, test_frac=0.2, val_frac=0.1, feature_cols=feature_cols
    )

    # Check shapes
    total_rows = len(sample_data)
    assert X_train.shape[0] + X_val.shape[0] + X_test.shape[0] == total_rows
    assert y_train.shape[0] + y_val.shape[0] + y_test.shape[0] == total_rows

    # Check that all y values are present
    assert set(y_train) | set(y_val) | set(y_test) <= {0, 1}


def test_time_ordered_split_fractions(sample_data):
    """Test split fractions are approximately correct."""
    feature_cols = ["payment_date"]
    X_train, y_train, X_val, y_val, X_test, y_test = time_ordered_split(
        sample_data, test_frac=0.2, val_frac=0.1, feature_cols=feature_cols
    )

    total = len(sample_data)
    # Check split fractions (approximate due to user grouping and rounding)
    assert X_train.shape[0] / total > 0.65  # ~70%
    assert X_val.shape[0] / total < 0.15  # ~10%
    assert X_test.shape[0] / total < 0.25  # ~20%


def test_compute_scale_pos_weight():
    """Test scale_pos_weight calculation."""
    y = np.array([0, 0, 0, 0, 1])  # 20% positive class
    weight = compute_scale_pos_weight(y)
    assert weight == 4.0  # 4 negatives / 1 positive

    y_balanced = np.array([0, 0, 1, 1])  # 50% positive
    weight_balanced = compute_scale_pos_weight(y_balanced)
    assert weight_balanced == 1.0


def test_compute_scale_pos_weight_edge_case():
    """Test scale_pos_weight with no positive samples."""
    y = np.array([0, 0, 0, 0])
    weight = compute_scale_pos_weight(y)
    assert weight == 1.0  # Default when no positives
