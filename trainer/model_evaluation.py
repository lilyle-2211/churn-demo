"""
Model evaluation and metrics calculation.
"""
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def precision_at_k(y_true, y_score, k=0.05):
    """
    Calculate precision at top k% of predictions.

    Args:
        y_true: True labels
        y_score: Predicted scores
        k: Fraction of top predictions to consider

    Returns:
        Precision at top k%
    """
    n = max(1, int(np.floor(k * len(y_true))))
    top_idx = np.argsort(y_score)[-n:]
    return (y_true[top_idx] == 1).mean()


def evaluate_model(model, dval, dtest, y_val, y_test):
    """
    Evaluate model performance on validation and test sets.

    Args:
        model: Trained XGBoost model
        dval: Validation DMatrix
        dtest: Test DMatrix
        y_val: Validation labels
        y_test: Test labels

    Returns:
        Dictionary of evaluation metrics
    """
    best_it = getattr(model, "best_iteration", None)

    if best_it:
        proba_val = model.predict(dval, iteration_range=(0, best_it + 1))
        proba_test = model.predict(dtest, iteration_range=(0, best_it + 1))
    else:
        proba_val = model.predict(dval)
        proba_test = model.predict(dtest)

    pr_auc_val = average_precision_score(y_val, proba_val)
    roc_auc_val = roc_auc_score(y_val, proba_val)
    pr_auc_test = average_precision_score(y_test, proba_test)
    roc_auc_test = roc_auc_score(y_test, proba_test)

    metrics = {
        "pr_auc_val": pr_auc_val,
        "roc_auc_val": roc_auc_val,
        "pr_auc_test": pr_auc_test,
        "roc_auc_test": roc_auc_test,
        "precision_at_5_val": precision_at_k(y_val, proba_val, k=0.05),
        "precision_at_5_test": precision_at_k(y_test, proba_test, k=0.05),
        "precision_at_10_val": precision_at_k(y_val, proba_val, k=0.10),
        "precision_at_10_test": precision_at_k(y_test, proba_test, k=0.10),
    }

    return metrics
