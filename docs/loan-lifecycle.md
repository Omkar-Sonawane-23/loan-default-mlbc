# LoanLifecycle contract and wallet demo

`blockchain/contracts/LoanLifecycle.sol` is an ETH/native-currency test-chain demo; it is not a rupee/stablecoin payment rail. It stores an opaque `bytes32` application ID, risk-assessment hash, agreement hash, wallet addresses, wei amounts, due timestamp and state. PII and model features stay off-chain.

## State machine
`NONE → SUBMITTED → RISK_ASSESSED → APPROVED → FUNDED → ACTIVE → PARTIALLY_REPAID → REPAID`; terminal alternatives are `REJECTED`, `DEFAULTED`, `CANCELLED`. Operator-only methods submit, assess, approve/reject, cancel and mark a past-due loan default. The borrower acknowledges the exact agreement hash in a wallet transaction before funding. A lender funds exactly the principal; contract transfers native currency to the borrower. Borrower repayments must be positive and not exceed outstanding total due; funds transfer to lender, state and balances update, and logs are emitted. All monetary values are `uint256` wei. Payments are not scheduled installments, oracle-fed interest, fiat settlement or automated penalty collection.

`owner` controls operators and pause. Operators are privileged demo keys; production must use audited role governance, multisig/key custody, limits and legal review. The contract uses checks-effects-interactions and a reentrancy guard on transfers. The paused emergency state also pauses repayments, a known operational tradeoff. It has no upgrade mechanism.

## Reputation
The contract updates `completedLoans`, `defaults`, on-time/late final completion counts, borrowed/repaid totals and streak from funding/repayment/default calls. `reputationScore` is a deterministic demo formula: new wallet = 500; otherwise 600 × completed/(completed+defaults) + 400 × onTimeCompletions/completed (integer division). This is public-chain behavior-derived reputation, not the ML PD and not a validated credit score.

## Deploy and use
```bash
cd blockchain
npm ci
npx hardhat node --hostname 0.0.0.0
# second terminal
npm run deploy:lifecycle:local
```
Deployment writes ignored `loan-lifecycle-address.json` (address, chain, deployment block). Configure `VITE_LOAN_LIFECYCLE_ADDRESS`, `VITE_CHAIN_ID`, and optionally backend `LOAN_LIFECYCLE_CONTRACT_ADDRESS` / `BLOCKCHAIN_START_BLOCK`. Add the local chain (31337) to an injected wallet and use only well-known Hardhat test accounts. Account keys printed by Hardhat are public test keys and must never be used on a real network. MetaMask/network connectivity is not simulated. UI route `/loans` calls the contract through the wallet; before assessment, it queries `/api/blockchain/record/{application_id}` and rejects a bytes32 hash that does not match the registered legacy risk record. This requires MongoDB and the assessment registry to be reachable. The app does not invent a risk hash.

Every confirmed UI transaction is offered to `/api/loans/chain-sync`. The API verifies contract address, successful receipt and matching lifecycle event before indexing current contract state in MongoDB. `/api/loans/reconciliation` discovers `LoanSubmitted` IDs from the configured deployment block, marks unindexed chain entries `PENDING`, compares Mongo snapshots to chain current state (`MATCHED`/`MISMATCHED`), and reports read failures. This demonstration route has no authentication/RBAC and must not be exposed as an institutional operational control.
