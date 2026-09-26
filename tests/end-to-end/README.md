# End-to-End Testing

This project was verified end-to-end during development with the
following actual sequence (not simulated):

1. `python ml/scripts/generate_demo_data.py` -- generated 6,000 synthetic
   rows, default rate 21.55%.
2. `python ml/scripts/train_model.py` -- trained & compared 4 models;
   Logistic Regression selected (ROC-AUC 0.8626); confusion matrix and
   feature importance plots saved.
3. `python ml/scripts/evaluate_model.py` -- independently reloaded the
   persisted model and reproduced identical metrics.
4. `python ml/scripts/seed_demo_applications.py` -- generated 40 demo
   applications via real inference through the trained model.
5. `cd blockchain && npx hardhat compile` -- compiled `LoanRecordRegistry.sol`
   with solc 0.8.24.
6. `npx hardhat test` -- **8/8 tests passing** against Hardhat's in-memory
   EVM (registration, duplicate-prevention, hash verification, tamper
   detection, timestamps, multi-registrar).
7. `npx hardhat node` + `npm run deploy:local` -- deployed the contract to
   a live local chain (chain id 31337); confirmed via
   `npm run verify:local` that a record could be registered, read back,
   and verified (result: `VERIFIED`).
8. `cd backend && pytest` -- **31/31 tests passing**, including:
   - `test_health.py`, `test_hashing.py` (deterministic SHA-256,
     tamper-sensitivity), `test_prediction.py` (real inference, input
     validation, risk ordering), `test_applications.py` (full CRUD,
     search, filter, audit logging), `test_analytics.py` (dashboard
     stats reflect real data), and `test_blockchain.py` -- run against
     the SAME live local chain from step 7, performing REAL on-chain
     registration, duplicate-rejection (409), hash verification
     (`verified: true`), and tamper detection (`verified: false`) through
     the actual FastAPI endpoints.
9. A full manual smoke test was run through `TestClient` against the live
   chain: health check -> real prediction -> application creation ->
   on-chain registration (with real transaction hash and block number) ->
   verification (`VERIFIED`) -> dashboard stats -> CSV export -> PDF
   export -> audit log -- all confirmed working end-to-end.
10. `cd frontend && npm install && npm run build` -- TypeScript compiled
    with zero errors (`tsc -b`) and Vite produced a working production
    bundle.

## Running it yourself

See the root `README.md` "Complete Run Instructions" section, or use
`scripts/setup.sh` followed by `scripts/start-dev.sh`.

Note: because a local Hardhat node is an ephemeral, in-memory blockchain
by default, its state (and any registered records) resets each time the
node process restarts unless you run `npx hardhat node` and keep it
running for the duration of your session -- this is expected local-network
behavior, not a bug.
