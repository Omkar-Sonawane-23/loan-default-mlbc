"""
train_model.py

Trains and compares 4 real supervised classification models on the
synthetic loan default dataset:

  1. Logistic Regression
  2. Decision Tree
  3. Random Forest
  4. Gradient Boosting

Candidate selection uses a stratified validation split and a documented ROC-AUC/PR-AUC composite; an untouched stratified test split is reserved for final calibrated evaluation. All reported metrics are computed from actual model predictions.
"""
import json
import os
import sys
import time
import datetime
import hashlib

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, ConfusionMatrixDisplay,
)

sys.path.insert(0, os.path.dirname(__file__) + "/../src")
from config import (
    DATA_PATH, MODEL_PATH, METADATA_PATH, METRICS_PATH, COMPARISON_PATH,
    CONFUSION_MATRIX_PATH, FEATURE_IMPORTANCE_PATH, TARGET_COLUMN,
    FEATURE_COLUMNS, RANDOM_SEED, TEST_SIZE, MODEL_VERSION_PREFIX,
)
from preprocessing import build_preprocessor, get_feature_names


CANDIDATE_MODELS = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
    "Decision Tree": DecisionTreeClassifier(max_depth=8, random_state=RANDOM_SEED),
    "Random Forest": RandomForestClassifier(
        n_estimators=300, max_depth=10, random_state=RANDOM_SEED, n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_SEED),
}


def evaluate(y_true, y_pred, y_proba) -> dict:
    """Report ranking, minority-class and probability-calibration metrics."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "sensitivity": round(tp / (tp + fn), 4) if tp + fn else 0.0,
        "specificity": round(tn / (tn + fp), 4) if tn + fp else 0.0,
        "false_positive_rate": round(fp / (fp + tn), 4) if fp + tn else 0.0,
        "false_negative_rate": round(fn / (fn + tp), 4) if fn + tp else 0.0,
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, y_proba), 4),
        "pr_auc": round(average_precision_score(y_true, y_proba), 4),
        "brier_score": round(brier_score_loss(y_true, y_proba), 4),
    }


def main():
    print(f"Loading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_trainval, y_trainval, test_size=0.25, random_state=RANDOM_SEED, stratify=y_trainval
    )
    print(f"Train: {len(X_train)} | Validation: {len(X_validation)} | Test: {len(X_test)} rows | "
          f"Test default rate: {y_test.mean():.3%}")

    comparison = {}
    fitted_pipelines = {}

    for name, estimator in CANDIDATE_MODELS.items():
        print(f"\nTraining {name} ...")
        start = time.time()
        pipeline = Pipeline(steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", estimator),
        ])
        pipeline.fit(X_train, y_train)
        elapsed = time.time() - start

        y_pred = pipeline.predict(X_validation)
        y_proba = pipeline.predict_proba(X_validation)[:, 1]

        metrics = evaluate(y_validation, y_pred, y_proba)
        metrics["selection_score"] = round(0.6 * metrics["roc_auc"] + 0.4 * metrics["pr_auc"], 4)
        metrics["training_time_seconds"] = round(elapsed, 3)
        comparison[name] = metrics
        fitted_pipelines[name] = pipeline

        print(f"  {name}: {metrics}")

    # Select using validation only, balancing ROC-AUC and minority-class PR-AUC.
    best_model_name = max(comparison, key=lambda k: comparison[k]["selection_score"])
    # Refit/calibrate inside train+validation folds; test remains untouched until final evaluation.
    base_pipeline = Pipeline(steps=[
        ("preprocessor", build_preprocessor()),
        ("classifier", CANDIDATE_MODELS[best_model_name]),
    ])
    calibrated = CalibratedClassifierCV(estimator=base_pipeline, method="sigmoid", cv=3)
    calibrated.fit(X_trainval, y_trainval)
    base_pipeline = calibrated.calibrated_classifiers_[0].estimator
    best_pipeline = calibrated
    calibrated_proba = best_pipeline.predict_proba(X_test)[:, 1]
    calibrated_pred = (calibrated_proba >= 0.5).astype(int)
    best_metrics = evaluate(y_test, calibrated_pred, calibrated_proba)
    best_metrics["calibration_method"] = "sigmoid/Platt scaling (3-fold CV on train+validation)"
    best_metrics["evaluation_population"] = "untouched synthetic test split; not external validation"

    print(f"\nSelected and calibrated model: {best_model_name} (holdout ROC-AUC={best_metrics['roc_auc']})")

    # ---- Save model comparison ----
    os.makedirs(os.path.dirname(COMPARISON_PATH), exist_ok=True)
    with open(COMPARISON_PATH, "w") as f:
        json.dump(comparison, f, indent=2)

    # ---- Save best model metrics ----
    with open(METRICS_PATH, "w") as f:
        json.dump({"selected_model": best_model_name, **best_metrics}, f, indent=2)

    # ---- Confusion matrix plot ----
    y_pred_best = best_pipeline.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Default", "Default"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(f"Confusion Matrix - {best_model_name}")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=150)
    plt.close(fig)

    # ---- Feature importance plot ----
    explanation_pipeline = base_pipeline
    preprocessor = explanation_pipeline.named_steps["preprocessor"]
    feature_names = get_feature_names(preprocessor)
    classifier = explanation_pipeline.named_steps["classifier"]

    importance_method = None
    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_
        importance_method = "impurity-based feature_importances_"
    elif hasattr(classifier, "coef_"):
        importances = np.abs(classifier.coef_[0])
        importance_method = "absolute value of logistic regression coefficients"
    else:
        importances = None

    feature_importance_list = []
    if importances is not None:
        idx_sorted = np.argsort(importances)[::-1][:12]
        top_features = [feature_names[i] for i in idx_sorted]
        top_values = [float(importances[i]) for i in idx_sorted]
        feature_importance_list = [
            {"feature": f, "importance": round(v, 5)} for f, v in zip(top_features, top_values)
        ]

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(top_features[::-1], top_values[::-1], color="#2563eb")
        ax.set_xlabel("Importance")
        ax.set_title(f"Feature Importance - {best_model_name}\n({importance_method})")
        plt.tight_layout()
        plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=150)
        plt.close(fig)

    # ---- Save model ----
    os.makedirs(MODEL_DIR := os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)
    with open(MODEL_PATH, "rb") as artifact:
        artifact_sha256 = hashlib.sha256(artifact.read()).hexdigest()

    model_version = f"{MODEL_VERSION_PREFIX}-{best_model_name.lower().replace(' ', '-')}"

    metadata = {
        "model_name": best_model_name,
        "model_version": model_version,
        "artifact_sha256": artifact_sha256,
        "feature_schema_version": "v1.0",
        "trained_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dataset_path": os.path.basename(DATA_PATH),
        "dataset_size": len(df),
        "train_size": len(X_trainval),
        "candidate_fit_size": len(X_train),
        "validation_size": len(X_validation),
        "train_plus_validation_size": len(X_trainval),
        "test_size": len(X_test),
        "model_selection_metric": "0.6 × ROC-AUC + 0.4 × PR-AUC on validation split",
        "selected_model_validation_metrics": comparison[best_model_name],
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "random_seed": RANDOM_SEED,
        "metrics": best_metrics,
        "calibration": {
            "method": "sigmoid",
            "folds": 3,
            "evaluation_split": "untouched stratified test split",
            "evidence": "synthetic dataset only; not independently validated",
        },
        "feature_importance": feature_importance_list,
        "feature_importance_method": importance_method,
        "candidate_models_compared": list(CANDIDATE_MODELS.keys()),
        "notice": (
            "This model is trained on a SYNTHETIC dataset generated for academic "
            "demonstration only. It is not validated for real financial decisions."
        ),
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved model -> {MODEL_PATH}")
    print(f"Saved metadata -> {METADATA_PATH}")
    print(f"Saved comparison -> {COMPARISON_PATH}")
    print(f"Saved metrics -> {METRICS_PATH}")
    print(f"Saved confusion matrix -> {CONFUSION_MATRIX_PATH}")
    if importances is not None:
        print(f"Saved feature importance -> {FEATURE_IMPORTANCE_PATH}")


if __name__ == "__main__":
    main()
