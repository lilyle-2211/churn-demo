"""Tests for data splitting logic."""
import numpy as np
import pandas as pd
import pytest

from trainer.data_splitting import compute_scale_pos_weight, time_ordered_split


@pytest.fixture
def sample_data():
    """Create sample payment data for testing."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    data = {
        "user_id": np.repeat(range(20), 5),
        "payment_date": np.tile(dates[:5], 20),
    }
    return pd.DataFrame(data)


def test_time_ordered_split(sample_data):
    """Test time-ordered splitting returns correct shapes."""
    train_mask, val_mask, test_mask, train_users, val_users, test_users = time_ordered_split(
        sample_data, test_frac=0.2, val_frac=0.1
    )

    # Check masks are boolean arrays
    assert train_mask.dtype == bool
    assert val_mask.dtype == bool
    assert test_mask.dtype == bool

    # Check all rows are assigned to exactly one set
    assert (train_mask | val_mask | test_mask).all()
    assert not (train_mask & val_mask).any()
    assert not (train_mask & test_mask).any()
    assert not (val_mask & test_mask).any()

    # Check user sets are disjoint
    assert len(train_users & val_users) == 0
    assert len(train_users & test_users) == 0
    assert len(val_users & test_users) == 0


def test_time_ordered_split_fractions(sample_data):
    """Test split fractions are approximately correct."""
    train_mask, val_mask, test_mask, train_users, val_users, test_users = time_ordered_split(
        sample_data, test_frac=0.2, val_frac=0.1
    )

    total_users = len(train_users) + len(val_users) + len(test_users)

    # Check user counts (approximate due to rounding)
    assert len(train_users) / total_users > 0.65  # ~70%
    assert len(val_users) / total_users < 0.15  # ~10%
    assert len(test_users) / total_users < 0.25  # ~20%


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
