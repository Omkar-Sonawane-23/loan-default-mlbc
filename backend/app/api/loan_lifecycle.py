"""Wallet transaction indexing and database/on-chain reconciliation for the demo contract."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.dependencies import get_database
from app.services.lifecycle_chain_service import LifecycleChain

router = APIRouter(prefix="/loans", tags=["loan lifecycle"])


class ConfirmedChainTransaction(BaseModel):
    loan_id: str = Field(pattern=r"^0x[0-9a-fA-F]{64}$")
    transaction_hash: str = Field(pattern=r"^0x[0-9a-fA-F]{64}$")
    application_reference: str = Field(default="", max_length=64, pattern=r"^[A-Za-z0-9._-]*$")


@router.post("/chain-sync")
def sync_confirmed_transaction(payload: ConfirmedChainTransaction, db=Depends(get_database)):
    """Index a transaction only after receipt/event verification against the configured contract."""
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable")
    chain = LifecycleChain()
    try:
        receipt = chain.verify_transaction(payload.transaction_hash, payload.loan_id)
        current = chain.loan(payload.loan_id)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not verify lifecycle transaction: {type(exc).__name__}")
    duplicate = db.loan_lifecycle.find_one({"loan_id": current["loan_id"], "transaction_hashes": receipt["transaction_hash"]})
    if duplicate:
        return {"sync_status": "ALREADY_INDEXED", **current, "transaction": receipt}
    now = datetime.now(timezone.utc)
    record = {**current, "application_reference": payload.application_reference, "last_confirmed_transaction": receipt, "updated_at": now}
    db.loan_lifecycle.update_one(
        {"loan_id": current["loan_id"]},
        {"$set": record, "$addToSet": {"transaction_hashes": receipt["transaction_hash"]}, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )
    db.audit_logs.insert_one({
        "application_id": current["loan_id"], "event": "BLOCKCHAIN_LIFECYCLE_SYNCED",
        "details": {"transaction_hash": receipt["transaction_hash"], "contract_state": current["contract_state"]},
        "timestamp": now,
    })
    return {"sync_status": "CONFIRMED_AND_INDEXED", **current, "transaction": receipt}


@router.get("/reconciliation")
def reconcile_lifecycle(db=Depends(get_database)):
    """Compare indexed Mongo state with the deployed contract's current state."""
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable")
    try:
        chain = LifecycleChain()
        rows = list(db.loan_lifecycle.find({}, {"_id": 0}).sort("updated_at", -1))
        on_chain_ids = chain.submitted_loan_ids()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Reconciliation unavailable: {type(exc).__name__}")
    by_id = {row.get("loan_id", "").lower(): row for row in rows}
    results = []
    counts = {"MATCHED": 0, "MISMATCHED": 0, "PENDING": 0, "FAILED": 0}
    all_ids = sorted(on_chain_ids | set(by_id))
    for loan_id in all_ids:
        row = by_id.get(loan_id)
        if row is None:
            try:
                on_chain = chain.loan(loan_id)
                outcome = "PENDING"
                item = {"loan_id": loan_id, "database_state": None, "blockchain_state": on_chain["contract_state"], "status": outcome, "last_transaction_hash": None}
            except Exception as exc:
                outcome = "FAILED"
                item = {"loan_id": loan_id, "database_state": None, "blockchain_state": None, "status": outcome, "error": type(exc).__name__}
        else:
            try:
                on_chain = chain.loan(loan_id)
                db_state = row.get("contract_state")
                outcome = "MATCHED" if db_state == on_chain["contract_state"] else "MISMATCHED"
                item = {"loan_id": loan_id, "database_state": db_state, "blockchain_state": on_chain["contract_state"], "status": outcome, "last_transaction_hash": (row.get("last_confirmed_transaction") or {}).get("transaction_hash")}
            except Exception as exc:
                outcome = "FAILED"
                item = {"loan_id": loan_id, "database_state": row.get("contract_state"), "blockchain_state": None, "status": outcome, "error": type(exc).__name__}
        counts[outcome] += 1
        results.append(item)
    return {"contract_address": chain.address or None, "checked_at": datetime.now(timezone.utc), "counts": counts, "records": results, "notice": "On-chain submissions are discovered from LoanSubmitted events beginning at configured deployment block. Unindexed chain records are PENDING. This demo endpoint is not authenticated."}
