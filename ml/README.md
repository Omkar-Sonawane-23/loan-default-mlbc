# LoanDefault MLBC - Machine Learning

**Academic demonstration only.** The dataset here is entirely synthetic
(generated with a fixed random seed) and the model is not validated for
real credit decisions.

## Pipeline

```bash
cd ml
pip install -r ../backend/requirements.txt   # or install scikit-learn, pandas, numpy, joblib, matplotlib directly

python scripts/generate_demo_data.py     # generates data/demo_loan_data.csv (6,000 synthetic rows)
python scripts/train_model.py            # trains & compares 4 models, saves the best one
python scripts/evaluate_model.py         # re-evaluates the persisted model independently
python scripts/seed_demo_applications.py # generates realistic demo applications via real inference
```

## Results (from an actual run)

Trained and compared 4 real models on a held-out, stratified 20% test
split (1,200 rows) of the 6,000-row synthetic dataset:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **Logistic Regression (selected)** | 86.58% | 82.24% | 48.26% | 60.83% | **86.26%** |
| Gradient Boosting | 86.33% | 79.87% | 49.03% | 60.77% | 85.47% |
| Random Forest | 83.92% | 77.97% | 35.52% | 48.81% | 84.30% |
| Decision Tree | 82.17% | 63.98% | 39.77% | 49.05% | 76.83% |

(These exact numbers are from `reports/model_comparison.json`, generated
by an actual training run during development of this project. Re-running
`train_model.py` will reproduce the same numbers since the dataset
generation and train/test split both use a fixed random seed.)

Logistic Regression was automatically selected as the best model by
ROC-AUC. Feature importance is derived from the model's own coefficients
(documented in `models/model_metadata.json` as
`"feature_importance_method"`).

## Structure

```
ml/
  data/demo_loan_data.csv          synthetic dataset (generated)
  data/processed/seed_applications.json   realistic demo applications (generated)
  models/loan_default_model.joblib  trained pipeline (preprocessing + classifier)
  models/model_metadata.json        model info, metrics, feature importance
  reports/model_metrics.json        best model's metrics
  reports/model_comparison.json     all 4 models' metrics
  reports/confusion_matrix.png      confusion matrix plot
  reports/feature_importance.png    feature importance plot
  scripts/                          the 4 pipeline scripts above
  src/                              shared config, preprocessing, and inference code
```

## Features used

`age, annual_income, employment_years, employment_type, credit_score,
loan_amount, loan_term_months, existing_debt, debt_to_income_ratio,
number_of_previous_loans, previous_default, dependents, savings_amount,
requested_loan_purpose`

## Risk thresholds (demonstration only, not financially validated)

- **LOW**: default probability < 30%
- **MEDIUM**: 30% to < 70%
- **HIGH**: 70% and above
