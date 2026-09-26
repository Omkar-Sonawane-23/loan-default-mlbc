# ML Documentation

See also `ml/README.md` for setup commands.

## Problem framing

Binary classification: predict `loan_default` (0 = no default, 1 = default)
from 14 applicant/loan features, and report a calibrated default
probability rather than just a class label.

## Dataset

- 6,000 synthetic records, generated with `numpy`'s `default_rng(42)`
  for full reproducibility.
- The target is generated from a logistic latent-risk formula combining
  credit score, debt-to-income ratio, prior defaults, employment type,
  income, loan amount, dependents, and savings, plus Gaussian noise --
  then thresholded probabilistically (not a hard rule), so the resulting
  dataset has realistic, non-trivial decision boundaries rather than a
  hand-codeable rule.
- Resulting default rate: ~21.5%.
- **This dataset is entirely synthetic and for academic demonstration
  only** -- it does not describe real people or real financial
  institutions.

## Preprocessing

`sklearn.compose.ColumnTransformer`:
- Numeric features: median imputation + standard scaling.
- Categorical features (`employment_type`, `requested_loan_purpose`):
  most-frequent imputation + one-hot encoding.

All wrapped in a single `sklearn.pipeline.Pipeline` together with the
classifier, so the exact same preprocessing is applied at inference time
(loaded from the one `.joblib` file -- no separate preprocessing code
path to get out of sync).

## Models trained and compared

1. Logistic Regression
2. Decision Tree (max_depth=8)
3. Random Forest (300 trees, max_depth=10)
4. Gradient Boosting

All trained on the same stratified 80/20 train/test split (seed=42).
Metrics: accuracy, precision, recall, F1, ROC-AUC, confusion matrix.

The model with the **highest ROC-AUC on the held-out test set** is
selected automatically -- in the reference run, Logistic Regression won
with ROC-AUC 0.8626 (see `ml/README.md` for the full comparison table).

## Explainability

- For Logistic Regression (or any linear model), feature importance is
  the absolute value of the model's coefficients (in the transformed
  feature space).
- For tree-based models, `feature_importances_` (impurity-based) is used
  instead.
- Both are computed from the actual fitted model -- nothing here is a
  hardcoded or illustrative list.
- The top 5 factors are surfaced in every prediction response as
  `risk_factors`, and the top 12 are plotted to
  `ml/reports/feature_importance.png`.

## Risk thresholds

Demonstration-only, not financially validated:
- LOW: probability < 30%
- MEDIUM: 30% <= probability < 70%
- HIGH: probability >= 70%

## Reproducing results

```bash
cd ml
python scripts/generate_demo_data.py
python scripts/train_model.py
python scripts/evaluate_model.py   # independently re-confirms the same metrics
```
