"""
train_model.py

Trains and compares 4 real supervised classification models on the
synthetic loan default dataset:

  1. Logistic Regression
  2. Decision Tree
  3. Random Forest
  4. Gradient Boosting

The best model is selected automatically based on ROC-AUC on a held-out
stratified test split. All metrics reported are computed from actual
model predictions -- nothing is fabricated.
"""
import json
import os
import sys
import time
import datetime

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
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, ConfusionMatrixDisplay,
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
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, y_proba), 4),
    }


def main():
    print(f"Loading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows | "
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

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        metrics = evaluate(y_test, y_pred, y_proba)
        metrics["training_time_seconds"] = round(elapsed, 3)
        comparison[name] = metrics
        fitted_pipelines[name] = pipeline

        print(f"  {name}: {metrics}")

    # ---- Select best model by ROC-AUC ----
    best_model_name = max(comparison, key=lambda k: comparison[k]["roc_auc"])
    best_pipeline = fitted_pipelines[best_model_name]
    best_metrics = comparison[best_model_name]

    print(f"\nSelected best model: {best_model_name} (ROC-AUC={best_metrics['roc_auc']})")

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
    preprocessor = best_pipeline.named_steps["preprocessor"]
    feature_names = get_feature_names(preprocessor)
    classifier = best_pipeline.named_steps["classifier"]

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

    model_version = f"{MODEL_VERSION_PREFIX}-{best_model_name.lower().replace(' ', '-')}"

    metadata = {
        "model_name": best_model_name,
        "model_version": model_version,
        "trained_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dataset_path": os.path.basename(DATA_PATH),
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "random_seed": RANDOM_SEED,
        "metrics": best_metrics,
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
