# Upgrade plan: AI + blockchain lending platform

## Scope and approach
This plan is based on inspection of the current repository before changes. The request describes a broad regulated-fintech product, while the checked-in system is an academic/demo application. Changes will be incremental and will not imply production readiness or fabricate integrations. First prioritize reliable ML artifacts, explainable/traceable risk results, safer API behavior, real local EVM lifecycle support where practical, and truthful architecture/testing documentation.

## Implemented in this upgrade increment
- Expanded model reports with PR-AUC, Brier score, sensitivity/specificity and false-positive/negative rates; recorded model SHA-256 and feature schema metadata; retrained and refreshed the checked-in synthetic-data model/reports.
- Prediction API reports model hash/schema, a probability-derived demonstrative score, explicit global-importance scope, and expected-loss arithmetic using configurable `LOSS_GIVEN_DEFAULT` (default 0.45; an unvalidated assumption).
- Prediction requests write private MongoDB inference events. Added a monitoring API and dashboard for windowed prediction-distribution PSI; the endpoint explicitly reports feature monitoring unavailable and label performance pending.
- Generic server errors no longer disclose raw exception details. Frontend API requests use same-origin `/api` with Vite proxy configuration.
- Added PSI unit/API tests. A subsequent increment added SHAP contributions for the selected logistic estimator, train/validation/test separation with validation-only model selection and sigmoid calibration, plus a 0–1000 calibrated-PD-derived research index with strict synthetic-data caveats.
- Added `LoanLifecycle.sol` for submitted→risk-assessed→approved→funded→active→partial/repaid/defaulted/rejected/cancelled transitions, wallet agreement acknowledgement, native-currency transfer/repayment, operator controls/pause, and deterministic contract-derived reputation.
- Added injected-wallet UI, local deployment script, confirmed transaction receipt/event verification, MongoDB lifecycle event snapshots, chain event discovery, and MATCHED/MISMATCHED/PENDING/FAILED reconciliation. No fiat token, auth/RBAC, external model validation, production-safe lending, or regulated credit score is implemented.

## Current architecture and functionality
- **Frontend:** React 18, Vite, TypeScript and Tailwind; routed dashboards for applications, prediction, analytics, model information, blockchain records and verification. Typed API modules and reusable charts/forms/components are present.
- **API:** FastAPI with route modules for health, model, predictions, applications, dashboard, analytics, blockchain and exports. MongoDB access, repositories/services, input schemas, audit and hashing helpers are present.
- **ML:** A checked-in synthetic CSV and joblib pipeline. Training compares Logistic Regression, Decision Tree, Random Forest and Gradient Boosting on a stratified holdout and selects by ROC-AUC. Numeric imputation/scaling and categorical imputation/encoding are in the pipeline. Prediction is persistent per API process. Existing “risk factors” are global feature importance, not local explanations.
- **Blockchain:** One Solidity `LoanRecordRegistry` records an immutable hash and risk category by application ID. Hardhat deployment, local verification, and tests exist. This is a tamper-evident assessment registry, not a loan lifecycle contract.
- **Persistence and tests:** MongoDB-backed application, prediction, audit and blockchain flows with backend tests; Hardhat tests and frontend TypeScript build. Docker Compose currently starts MongoDB only.
- **Auth/RBAC:** No complete authentication or role-based authorization layer was identified. This must not be represented as implemented.
- **Documentation:** Existing README and docs document the academic system and synthetic-data limitation, but do not yet comprehensively describe governance, threat model, lifecycle boundaries, drift, or deployment limitations.

## Problems and risks identified
1. Current training metrics are a single holdout comparison and include accuracy, precision, recall, F1 and ROC-AUC only; no PR-AUC, calibration, Brier score or CV reporting.
2. Feature importance is model-global and presented as prediction contributors in the API; this can mislead users as a local explanation.
3. Score/risk cutoffs are hard-coded demo thresholds and lack explicit configuration rationale.
4. Model metadata does not hash the model artifact and model/prediction registry is not comprehensive.
5. Exception handler returns exception text, which can leak internals. CORS defaults are local-development oriented; auth/rate limiting are absent.
6. On-chain registry has no role controls or loan state machine; it must be described honestly as a demo registry, not lending infrastructure.
7. Compose does not start app services, and the requested production-grade flow is much larger than existing tested scope.
8. Synthetic dataset limits external validity, subgroup fairness and calibration claims.

## Proposed architecture
Retain React/Vite → FastAPI → MongoDB and the separate scikit-learn artifact pipeline. Keep blockchain transaction submission as an explicitly configured EVM integration and distinguish unavailable, simulated/demo and confirmed status. Adopt small, testable improvements rather than introducing unsupported services. Future production architecture requires a reviewed identity provider, authorization policy, secrets management, monitoring, key custody and legal/compliance assessment.

## Database changes
Preserve existing application/audit structures and add indexed `model_predictions` (off-chain features and model output) and `loan_lifecycle` snapshots (opaque loan ID, wallet/public chain fields, current on-chain state and verified transaction reference). `loan_lifecycle` is written only after receipt/event validation. Financial features and SHAP details remain off-chain. Reconciliation compares snapshots with current contract state and discovers pending on-chain submissions.

## ML changes
Expand evaluation with PR-AUC, specificity/sensitivity, confusion-derived rates and Brier score; retain preprocessing in the estimator pipeline, select using a validation-only 0.6 ROC-AUC + 0.4 PR-AUC composite, calibrate with sigmoid cross-validation on train+validation, and reserve test data for final evaluation. Record artifact SHA-256, feature schema and dataset provenance. Local SHAP explains base estimator output in encoded space (grouped for display); calibration and drift claims remain limited to synthetic data and observed unlabeled predictions.

## Blockchain changes
Keep the existing immutable hash registry and add a separate EVM loan lifecycle contract with operator roles, explicit states, agreement hash acknowledgement, wei funding/repayment, reentrancy protection, pause control and contract-derived reputation. Wallet UI submits direct signed transactions. Backend indexing verifies receipt status, target address and matching event; reconciliation scans LoanSubmitted logs and compares indexed snapshots. Native currency is test/demo only. Never store sensitive applicant features on-chain or substitute fabricated hashes/receipts.

## API changes
Harden error responses, add readiness/model-status reporting, document actual capabilities, and ensure request/prediction metadata can include model version and artifact hash. Defer JWT/RBAC until a complete identity/authorization design can be implemented and tested; current routes must not be advertised as protected.

## Frontend changes
Preserve existing dashboard and add truthful status/context for model provenance and explanation scope. Keep simulation/demo labeling explicit. Avoid fake wallet, status, metrics or repayment UX.

## Security improvements
Do not return raw exception details. Keep secrets environment-only; maintain restrictive configurable CORS. Document missing auth/RBAC/rate limiting as a release blocker, protect MongoDB and wallet keys operationally, validate inputs, and ensure raw PII never reaches chain or logs.

## Testing strategy
Validated in this increment: backend pytest suite including actual local Hardhat loan create→assess→approve→agreement-acknowledge→fund→partial/full repay→sync→reconcile and deliberate DB mismatch using mongomock; Hardhat suite for access, state transitions, repayments, default, pause and reputation; frontend TypeScript/build; deterministic synthetic-data training. Production MongoDB and MetaMask end-to-end browser session were unavailable here and are not claimed.

## Deployment and migration
Local development remains component-based unless Compose is expanded and validated. Existing MongoDB records and registry deployments are not migrated automatically; contract upgrades require a new deployment and explicit address configuration. Synthetic data/model artifacts are demo-only. Production deployment requires private network/database, secret rotation, TLS, auth/RBAC, monitoring, audited contracts and regulatory review.
