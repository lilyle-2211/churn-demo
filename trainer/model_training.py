"""
Model training and hyperparameter tuning with Optuna.
"""
import logging

import optuna
import xgboost as xgb
from sklearn.metrics import average_precision_score
from validation import load_config

logger = logging.getLogger(__name__)


def create_dmatrix(
    X, y, feature_cols, numeric_features, categorical_features, enable_categorical=True
):
    """
    Create XGBoost DMatrix with categorical feature support.

    Args:
        X: Feature matrix
        y: Labels
        feature_cols: List of all feature column names
        numeric_features: List of numeric feature names
        categorical_features: List of categorical feature names
        enable_categorical: Whether to enable categorical support

    Returns:
        XGBoost DMatrix
    """
    dmatrix = xgb.DMatrix(
        X, label=y, feature_names=feature_cols, enable_categorical=enable_categorical
    )
    # Mark categorical features: 'q' for quantitative (numeric), 'c' for categorical
    dmatrix.set_info(
        feature_types=["q"] * len(numeric_features) + ["c"] * len(categorical_features)
    )
    return dmatrix


def tune_hyperparameters(dtrain, dval, y_val, scale_pos_weight, n_trials=None):
    """
    Tune hyperparameters using Optuna.

    Args:
        dtrain: Training DMatrix
        dval: Validation DMatrix
        y_val: Validation labels
        scale_pos_weight: Scale weight for positive class
        n_trials: Number of Optuna trials (if None, uses config value)

    Returns:
        Best hyperparameters dictionary
    """
    config = load_config()
    if n_trials is None:
        n_trials = config.model.n_trials

    logger.info("Starting Optuna hyperparameter tuning")

    def objective(trial):
        # Start with fixed params
        param = {
            **config.model.fixed_params,
            "seed": config.data.random_state,
            "scale_pos_weight": scale_pos_weight,
        }

        # Add tunable hyperparameters dynamically
        for hp_name, hp_range in config.model.hyperparameter_ranges.items():
            if hp_range.type == "int":
                param[hp_name] = trial.suggest_int(hp_name, int(hp_range.min), int(hp_range.max))
            else:  # float
                param[hp_name] = trial.suggest_float(
                    hp_name, hp_range.min, hp_range.max, log=hp_range.log
                )

        bst_trial = xgb.train(
            param,
            dtrain,
            num_boost_round=config.model.num_boost_round,
            evals=[(dval, "val")],
            early_stopping_rounds=config.model.early_stopping_rounds,
            verbose_eval=False,
        )
        preds = bst_trial.predict(dval)

        return average_precision_score(y_val, preds)

    study = optuna.create_study(
        direction="maximize", sampler=optuna.samplers.TPESampler(seed=config.data.random_state)
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

    logger.info("Optuna tuning complete")
    logger.info(f"Best trial PR-AUC: {study.best_trial.value}")
    logger.info(f"Best hyperparameters: {study.best_params}")

    return study.best_params


def train_final_model(dtrain, dval, best_params, scale_pos_weight):
    """
    Train the final model with best hyperparameters.

    Args:
        dtrain: Training DMatrix
        dval: Validation DMatrix
        best_params: Best hyperparameters from tuning
        scale_pos_weight: Scale weight for positive class

    Returns:
        Trained XGBoost model
    """
    config = load_config()
    final_params = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "verbosity": 1,
        "seed": config.data.random_state,
        "scale_pos_weight": scale_pos_weight,
        "tree_method": "hist",
        "max_cat_to_onehot": 4,
        **best_params,
    }

    logger.info("Training final model")
    bst = xgb.train(
        final_params,
        dtrain,
        num_boost_round=config.model.num_boost_round,
        evals=[(dtrain, "train"), (dval, "val")],
        early_stopping_rounds=config.model.early_stopping_rounds,
        verbose_eval=20,
    )

    return bst


def log_feature_importance(model, feature_cols, categorical_features):
    """
    Print feature importance sorted by gain.

    Args:
        model: Trained XGBoost model
        feature_cols: List of feature column names
        categorical_features: List of categorical feature names
    """
    logger.info("Feature importance:")
    importance = sorted(
        model.get_score(importance_type="gain").items(), key=lambda x: x[1], reverse=True
    )
    for feat, score in importance:
        # Map feature index to actual name
        if feat.startswith("f") and feat[1:].isdigit():
            feat_idx = int(feat[1:])
            feat_name = feature_cols[feat_idx]
        else:
            feat_name = feat

        feat_type = "categorical" if feat_name in categorical_features else "numeric"
        logger.info(f"  {feat} ({feat_name} - {feat_type}): {score:.2f}")
