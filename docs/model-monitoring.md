# Model monitoring (implemented subset)

`GET /api/model-monitoring/summary?window_days=30` reports counts and mean predicted PD in the current and preceding windows, plus population stability index (PSI) between those prediction distributions. Prediction events are stored in MongoDB's `model_predictions` collection with off-chain input features, model version, inference output, UTC timestamp, and `data_source=user_provided`.

PSI bins are based on reference-window quantiles; zero-frequency bins are clipped for numerical stability. Bands use conventional screening values (`<0.10` low, `<0.25` moderate, otherwise high). These are heuristics, not calibrated alert thresholds. If either interval has insufficient observations, status reflects that. The API explicitly reports feature drift unavailable and label performance pending: no production feature baseline or outcome-label feed is configured. Do not infer model quality, fairness, or default-rate trends from prediction drift alone.

Predictions can contain sensitive financial features. The collection must be treated as private financial data: restrict database access, configure retention/deletion policy, and do not expose this endpoint to unauthenticated public users in a real deployment. Authentication/RBAC is not implemented in this academic application.
