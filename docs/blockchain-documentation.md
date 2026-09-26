# Blockchain Documentation

See also `blockchain/README.md` for setup commands.

## Why blockchain here

MongoDB is fast and flexible but mutable -- anyone with database access
could silently edit a stored risk assessment after the fact. Registering
a hash of the record on an immutable ledger gives a way to *detect* such
tampering after the fact, without needing to trust the database operator.

## What's on-chain vs off-chain

**On-chain (LoanRecordRegistry.sol):**
- `applicationId` (string)
- `recordHash` (bytes32, SHA-256 of the canonical record)
- `riskCategory` (string)
- `timestamp` (uint256, block time)
- `registrar` (address)

**Off-chain (MongoDB only):**
- All applicant financial details, loan features, prediction
  probabilities, status, audit trail.

The contract intentionally never receives applicant income, credit score,
loan amount, or any other sensitive field -- only their hash.

## Hashing

See `backend/app/services/hashing_service.py`. The canonical record
includes: `application_id, applicant_reference, input_features,
prediction, default_probability, non_default_probability, risk_category,
model_name, model_version, status`. Floats are rounded to 6 decimal places
before serialization (stable JSON, sorted keys) so that harmless floating
point representation differences never change the hash, while any real
change to a canonical field does.

## Smart contract functions

- `registerRecord(applicationId, recordHash, riskCategory)` -- reverts if
  already registered (`"Record already registered"`).
- `getRecord(applicationId)` -- returns the full stored tuple.
- `recordExists(applicationId)` -- boolean existence check.
- `verifyRecord(applicationId, currentHash)` -- returns whether the given
  hash matches what's stored.
- `getRecordTimestamp(applicationId)` -- registration timestamp only.

Event: `LoanRecordRegistered(applicationId, applicationId, recordHash,
riskCategory, timestamp, registrar)`.

## Verified test results (from actual development runs)

- `npx hardhat test`: **8/8 passing** -- registration, event emission,
  correct storage, existence checks, duplicate-prevention, hash
  verification (both matching and tampered), reverts on missing records,
  timestamp sanity, and multi-registrar behavior.
- A local Hardhat node was started, the contract deployed to it, and a
  record registered + read back + verified via `scripts/verify-local.ts`
  -- result: `VERIFIED`.
- The FastAPI backend's `tests/test_blockchain.py` performs the same
  flow through the actual API (register, duplicate-rejection with 409,
  verify-matching returns `verified: true`, verify-after-tampering
  returns `verified: false`) against a live local chain.

## Local network details

- RPC: `http://127.0.0.1:8545`
- Chain ID: `31337`
- Uses Hardhat's built-in, publicly-documented development accounts.
  These private keys are never secret and must never be used on a real
  network with real funds.
