# LoanDefault MLBC - Blockchain Layer

Solidity smart contracts + Hardhat project: immutable assessment-hash registry and a separate ETH-denominated demo loan lifecycle with wallet-driven funding/repayment and contract-derived reputation.

## What's here

- `contracts/LoanRecordRegistry.sol` - immutable assessment record hash registry
- `contracts/LoanLifecycle.sol` - loan state machine, native-currency funding/repayment and reputation
- `test/LoanRecordRegistry.ts` and `test/LoanLifecycle.ts` - Hardhat/Mocha/Chai tests
- `scripts/deploy.ts` - deploys the contract and writes `deployed-address.json`
- `scripts/verify-local.ts` - sanity-checks a live deployment by registering
  and verifying a test record

## Setup

```bash
cd blockchain
npm install
```

## Compile

```bash
npm run compile
```

## Test

```bash
npm run test
```

Expected output: 8 passing tests covering registration, duplicate
prevention, hash verification (matching and tampered), record retrieval,
and access to timestamps.

## Run a local blockchain

In one terminal:

```bash
npx hardhat node
```

This starts a local Ethereum JSON-RPC node at `http://127.0.0.1:8545`
with chain ID `31337` and 20 pre-funded development accounts. These
private keys are publicly known test keys -- never send real funds to them.

## Deploy

In a second terminal:

```bash
npm run deploy:local
```

This deploys `LoanRecordRegistry` and writes the deployed address to
`deployed-address.json`, which the FastAPI backend reads (or you can copy
the address into `backend/.env` as `BLOCKCHAIN_CONTRACT_ADDRESS`).

## Sanity-check the deployment

```bash
npm run verify:local
```

Registers a test record and verifies it can be read back and validated.

## Loan lifecycle

```bash
npm run deploy:lifecycle:local
```

This deploys `LoanLifecycle` and writes ignored `loan-lifecycle-address.json`, including deployment block for event discovery. The contract uses wei/native chain currency, not fiat or stablecoins. See `docs/loan-lifecycle.md` for flow, access roles, setup and limitations. On the frontend configure `VITE_LOAN_LIFECYCLE_ADDRESS` and `VITE_CHAIN_ID` and connect an injected wallet. Run `npm test` for lifecycle and hash-registry contract suites.

## What the record registry stores

Only: `applicationId`, a SHA-256 `recordHash`, `riskCategory`, a
`timestamp`, and the `registrar` address. It never stores applicant
names, income, government IDs, bank details, or any other sensitive
personal information -- see the root README's Security section.
