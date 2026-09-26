"""
evaluate_model.py

Reloads the persisted pipeline and the held-out test split (recreated with
the same random seed) and reprints evaluation metrics. Useful for verifying
that the saved model on disk matches the reported metrics, independent of
train_model.py.
"""
import os
import sys
import json

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
)

sys.path.insert(0, os.path.dirname(__file__) + "/../src")
from config import DATA_PATH, MODEL_PATH, TARGET_COLUMN, FEATURE_COLUMNS, RANDOM_SEED, TEST_SIZE


def main():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )

    pipeline = joblib.load(MODEL_PATH)
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
    }
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("Re-evaluation of persisted model on held-out test split:")
    print(json.dumps(metrics, indent=2))
    print("\nConfusion Matrix [[TN, FP], [FN, TP]]:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Default", "Default"]))


if __name__ == "__main__":
    main()
