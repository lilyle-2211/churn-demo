"""
Data preprocessing and feature engineering for churn prediction.
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def prepare_data(df, categorical_features=None):
    """
    Prepare data: convert datetime and categorical features.
    """
    df["payment_date"] = pd.to_datetime(df["payment_date"], utc=True)

    # Combine category conversion and encoding
    if categorical_features is not None:
        for col in categorical_features:
            df[col] = df[col].astype("category").cat.codes
    return df.values


def time_ordered_split(df, test_frac, val_frac, feature_cols, label_col="is_churn"):
    """
    Split data into train/val/test sets based on user signup date.

    Args:
        df: DataFrame with user_id and payment_date columns
        test_frac: Fraction of users for test set
        val_frac: Fraction of users for validation set

    Returns:
        Tuple of (train_df, val_df, test_df) boolean arrays
    """
    logger.info("Time-ordered split by user signup date")

    # Time-ordered split (simple version)
    user_signup = df.groupby("user_id")["payment_date"].min().sort_values()
    n_users = len(user_signup)
    test_start = int((1.0 - test_frac) * n_users)
    val_start = int((1.0 - (test_frac + val_frac)) * n_users)

    train_users = set(user_signup.iloc[:val_start].index)
    val_users = set(user_signup.iloc[val_start:test_start].index)
    test_users = set(user_signup.iloc[test_start:].index)

    X_train = df[df["user_id"].isin(train_users)][feature_cols].values
    y_train = df[df["user_id"].isin(train_users)][label_col].values
    X_val = df[df["user_id"].isin(val_users)][feature_cols].values
    y_val = df[df["user_id"].isin(val_users)][label_col].values
    X_test = df[df["user_id"].isin(test_users)][feature_cols].values
    y_test = df[df["user_id"].isin(test_users)][label_col].values

    logger.info(
        f"Users: total={n_users}, train={len(train_users)}, val={len(val_users)}, test={len(test_users)}"
    )
    logger.info(
        f"Rows: total={len(df)}, train={len(X_train)}, val={len(X_val)}, test={len(X_test)}"
    )
    logger.info(
        f"Train period: {user_signup.iloc[0]['signup_date']} to {user_signup.iloc[val_start-1]['signup_date']}"
    )
    logger.info(
        f"Val period:   {user_signup.iloc[val_start]['signup_date']} to {user_signup.iloc[test_start-1]['signup_date']}"
    )
    logger.info(
        f"Test period:  {user_signup.iloc[test_start]['signup_date']} to {user_signup.iloc[-1]['signup_date']}"
    )

    return X_train, y_train, X_val, y_val, X_test, y_test


def compute_scale_pos_weight(y_train):
    """
    Compute scale_pos_weight for handling class imbalance.

    Args:
        y_train: Training labels

    Returns:
        Scale weight for positive class
    """
    pos = int((y_train == 1).sum())
    neg = int((y_train == 0).sum())
    scale_pos_weight = (neg / pos) if pos > 0 else 1.0
    logger.info(f"Train pos/neg: {pos}/{neg}, scale_pos_weight: {scale_pos_weight:.4f}")
    return scale_pos_weight
