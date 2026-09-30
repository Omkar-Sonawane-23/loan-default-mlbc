# Explainability and risk index

## Local SHAP
Prediction inference loads the registered scikit-learn artifact once, prepares an interventional SHAP `LinearExplainer` from up to 100 synthetic reference rows, transforms the current row with the model's stored preprocessing pipeline, and groups one-hot contributions back to original feature names. The API response's `local_explanation` includes method/status, baseline, signed contributors and target scale. For this selected sigmoid-calibrated logistic model, the explanation is for the first cross-validation base estimator's pre-calibration output (log-odds), **not calibrated PD points**. `risk_factors` remains model-global coefficient importance and is labelled separately. If the model type or SHAP explainer is unavailable, inference returns `UNAVAILABLE` rather than fabricated attribution.

## Calibration and evaluation
Training reserves stratified train, validation and test partitions. Candidate selection uses `0.6 × ROC-AUC + 0.4 × PR-AUC` on validation data. The selected estimator is sigmoid calibrated using three folds of train+validation only. ROC-AUC, PR-AUC, Brier score, sensitivity, specificity and false-positive/negative rates for the calibrated artifact are measured on the untouched test split. This is a deterministic evaluation on generated synthetic rows, not independent or prospective validation, fairness review, or a guarantee of calibration in any population.

## 0–1000 index
`credit_score = round((1 - calibrated_PD) × 1000)`. This is a monotonic display transformation of the model's calibrated synthetic-data PD, not a validated consumer score, lender policy, bureau score, or creditworthiness assertion. Keep the human-review disclaimer. Risk categories remain demo bands and are not regulatory decision rules.
