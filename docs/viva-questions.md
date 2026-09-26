# Viva / Presentation Questions

## Machine Learning

**Q: Why did you generate a synthetic dataset instead of using a real
one?**
A: Real loan/credit datasets contain sensitive personal and financial
information and are typically restricted or require institutional
approval. A synthetic dataset, generated with a documented, reproducible
process (fixed random seed, described latent-risk formula), lets the
project demonstrate a complete, real ML pipeline end-to-end without any
privacy or licensing concerns, while remaining honest that it's not
validated for real-world use.

**Q: Why 4 models, and how did you pick the winner?**
A: To demonstrate model comparison as a core ML skill: a simple linear
baseline (Logistic Regression), a single tree (Decision Tree), and two
ensemble methods (Random Forest, Gradient Boosting). The winner is
selected automatically by the highest ROC-AUC on a held-out, stratified
test split -- not manually chosen.

**Q: Why did Logistic Regression outperform the ensemble methods here?**
A: The synthetic dataset's latent risk score was generated from a linear
combination of features passed through a logistic (sigmoid) function --
which is exactly the functional form Logistic Regression fits, so it has
a natural advantage on this particular synthetic data. On real-world data
with more complex non-linear interactions, tree-based ensembles often
outperform linear models; this is a useful, honest observation about
synthetic benchmarks in general.

**Q: How do you explain a prediction to a non-technical user?**
A: The API returns the top 5 features by (global) model importance as
`risk_factors` in every prediction response, and the UI displays them as
a ranked bar list alongside the probability. This is a global explanation
(what the model generally weighs most) rather than a per-instance
explanation like SHAP, which is documented explicitly in the metadata's
`feature_importance_method` field.

## Blockchain

**Q: Why blockchain at all -- why not just an audit log in MongoDB?**
A: An audit log inside the same database that stores the data can be
edited or deleted by anyone with database access, along with the record
it's supposed to be auditing. A hash registered on an independent,
append-only ledger can't be altered after the fact, so it gives a way to
*detect* tampering that doesn't depend on trusting the database operator.

**Q: What exactly goes on-chain, and why not the whole record?**
A: Only `applicationId`, a SHA-256 hash of the canonical record,
`riskCategory`, a timestamp, and the registrar's address. Putting
sensitive applicant data (income, credit score) on a public/shared ledger
would be both unnecessary and a privacy risk -- the hash alone is
sufficient to prove integrity without revealing content.

**Q: What happens if someone edits a MongoDB record after it's
registered?**
A: The application's `blockchain.registered` flag and stored hash don't
change automatically. When `/api/blockchain/verify/{id}` is called, the
backend recomputes the hash from the CURRENT MongoDB state and compares
it against the immutable on-chain hash -- since the record changed, the
recomputed hash differs, and the endpoint returns `verified: false` /
"VERIFICATION FAILED", with both hashes shown so the mismatch is visible.

**Q: What if the application is deleted from MongoDB?**
A: The on-chain record is untouched -- blockchains here are
append-only/immutable by design. The API's delete response explicitly
notes this when the deleted application had been registered.

**Q: Why Hardhat and not a public testnet?**
A: A local Hardhat node gives a free, instant, fully controllable
Ethereum-compatible environment ideal for development and a live
demonstration, without needing testnet ETH, waiting for confirmations, or
any external dependency during a presentation.

## System Design

**Q: Why FastAPI + MongoDB + web3.py specifically?**
A: FastAPI gives strong typing (via Pydantic) and automatic interactive
API docs, which is valuable both for development and for demonstrating
the API surface. MongoDB's document model maps naturally onto the
variable-shaped loan application records. web3.py is the standard Python
library for talking to Ethereum-compatible nodes, letting the same
Python backend own both the ML and blockchain integration without a
separate service.

**Q: How would this scale / what would you change for production?**
A: Add authentication/authorization, use a public or consortium testnet
with proper key management (e.g. a KMS, not an in-code dev key), add
model monitoring and retraining pipelines, validate the ML model against
real historical outcome data with fairness/bias audits, and add rate
limiting and input sanitization hardening to the API.
