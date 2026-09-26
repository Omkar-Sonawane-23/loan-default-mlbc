# LoanDefault MLBC - Blockchain Layer

Solidity smart contract + Hardhat project providing tamper-evident,
on-chain verification hashes for loan risk assessment records.

## What's here

- `contracts/LoanRecordRegistry.sol` - the smart contract (Solidity 0.8.24)
- `test/LoanRecordRegistry.ts` - Hardhat/Mocha/Chai test suite (8 tests, all passing)
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

## What the contract stores

Only: `applicationId`, a SHA-256 `recordHash`, `riskCategory`, a
`timestamp`, and the `registrar` address. It never stores applicant
names, income, government IDs, bank details, or any other sensitive
personal information -- see the root README's Security section.
