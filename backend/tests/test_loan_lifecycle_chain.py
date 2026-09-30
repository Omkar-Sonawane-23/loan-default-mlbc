"""Real local-EVM + FastAPI/Mongo mock integration; skips if a local chain is absent."""
import time
import uuid
import pytest
from web3 import Web3
from app.config import settings
from app.services.lifecycle_chain_service import LifecycleChain
from app.dependencies import get_database

OWNER_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
BORROWER_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
LENDER_KEY = "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"


def _send(chain, key, function, value=0):
    account = chain.w3.eth.account.from_key(key)
    tx = function.build_transaction({
        "from": account.address,
        "nonce": chain.w3.eth.get_transaction_count(account.address, "pending"),
        "chainId": settings.BLOCKCHAIN_CHAIN_ID,
        "gas": 900_000,
        "gasPrice": chain.w3.eth.gas_price,
        "value": value,
    })
    signed = chain.w3.eth.account.sign_transaction(tx, key)
    tx_hash = chain.w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = chain.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)
    assert receipt.status == 1
    return Web3.to_hex(receipt.transactionHash)


def test_real_local_loan_flow_indexes_and_reconciles(client):
    chain = LifecycleChain()
    try:
        chain._require()
    except Exception:
        pytest.skip("Deploy LoanLifecycle and run local Hardhat node for the EVM integration test")

    owner = chain.w3.eth.account.from_key(OWNER_KEY)
    borrower = chain.w3.eth.account.from_key(BORROWER_KEY)
    lender = chain.w3.eth.account.from_key(LENDER_KEY)
    loan_id = Web3.to_hex(Web3.keccak(text=f"test-loan-{uuid.uuid4()}"))
    principal, total_due = 10**15, 11 * 10**14
    agreement = Web3.keccak(text=f"agreement-{loan_id}")
    risk_hash = Web3.keccak(text=f"assessment-{loan_id}")
    due_at = int(time.time()) + 3600
    c = chain.contract

    _send(chain, OWNER_KEY, c.functions.submitLoan(bytes.fromhex(loan_id[2:]), borrower.address, principal, total_due, due_at, agreement))
    _send(chain, OWNER_KEY, c.functions.assessRisk(bytes.fromhex(loan_id[2:]), risk_hash))
    _send(chain, OWNER_KEY, c.functions.decide(bytes.fromhex(loan_id[2:]), True))
    _send(chain, BORROWER_KEY, c.functions.acceptAgreement(bytes.fromhex(loan_id[2:]), agreement))
    _send(chain, LENDER_KEY, c.functions.fundLoan(bytes.fromhex(loan_id[2:])), principal)
    _send(chain, BORROWER_KEY, c.functions.repay(bytes.fromhex(loan_id[2:])), principal)
    final_tx = _send(chain, BORROWER_KEY, c.functions.repay(bytes.fromhex(loan_id[2:])), total_due - principal)

    pending = client.get("/api/loans/reconciliation")
    assert pending.status_code == 200
    assert pending.json()["counts"]["PENDING"] >= 1
    assert next(item for item in pending.json()["records"] if item["loan_id"] == loan_id.lower())["status"] == "PENDING"
    response = client.post("/api/loans/chain-sync", json={"loan_id": loan_id, "transaction_hash": final_tx})
    assert response.status_code == 200, response.text
    assert response.json()["contract_state"] == "REPAID"
    again = client.post("/api/loans/chain-sync", json={"loan_id": loan_id, "transaction_hash": final_tx})
    assert again.status_code == 200
    assert again.json()["sync_status"] == "ALREADY_INDEXED"
    record = client.get("/api/loans/reconciliation")
    assert record.status_code == 200
    assert record.json()["counts"]["MATCHED"] == 1
    assert next(item for item in record.json()["records"] if item["loan_id"] == loan_id.lower())["blockchain_state"] == "REPAID"
    db = client.app.dependency_overrides[get_database]()
    db.loan_lifecycle.update_one({"loan_id": loan_id.lower()}, {"$set": {"contract_state": "DEFAULTED"}})
    mismatch = client.get("/api/loans/reconciliation").json()
    assert mismatch["counts"]["MISMATCHED"] == 1
