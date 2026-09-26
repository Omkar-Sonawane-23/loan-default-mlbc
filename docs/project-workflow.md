# Project Workflow (Presentation Flow)

1. **Dashboard** -- show the portfolio overview: total applications, risk
   mix, blockchain registration rate.
2. **Risk Prediction** -- fill in a loan application, click "Predict Risk"
   -> real-time ML inference (not hardcoded) shows default probability,
   risk category, and the top contributing factors from the trained
   model's own feature importance.
3. **Save Application** -- persists to MongoDB with the prediction
   attached; an audit event is logged.
4. **Register on Blockchain** -- computes a SHA-256 hash of the canonical
   record and sends a real transaction to the local Hardhat blockchain.
   Show the returned transaction hash and block number.
5. **Application Details** -- show the full record: ML assessment,
   feature importance, blockchain info (hash, tx hash, block number), and
   the audit timeline built from real logged events.
6. **Verify Record** -- enter the application ID, click "Verify Record".
   The backend recomputes the hash from the CURRENT database record and
   compares it to what's on-chain -> **VERIFIED**.
7. **Tamper demo** -- edit the application's loan amount via the API or
   Applications page, then verify again -> **VERIFICATION FAILED**, with
   both hashes shown side-by-side to make the mismatch visible.
8. **Analytics / Model Analytics** -- show the model comparison table,
   confusion matrix, and portfolio-wide charts.
9. **Blockchain page** -- show the deployed contract address, chain ID,
   and the list of recent on-chain transactions.
10. **Export** -- download a CSV of all applications, or a PDF report for
    one specific application (both generated live from MongoDB, not
    pre-baked files).
