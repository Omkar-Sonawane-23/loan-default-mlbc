"""
test_blockchain.py

These tests perform REAL transactions against a local Hardhat blockchain
via web3.py -- nothing here is mocked. They require:

  1. `npx hardhat node` running at http://127.0.0.1:8545 (chain id 31337)
  2. The contract deployed (`npm run deploy:local` inside blockchain/),
     with BLOCKCHAIN_CONTRACT_ADDRESS pointing at it (or
     blockchain/deployed-address.json present, which is auto-detected).

If neither is available, these tests are skipped with a clear reason
rather than failing the whole suite -- this keeps `pytest` runnable in
environments without a live chain, while still providing real coverage
whenever one is present (see docs/blockchain-documentation.md for how
this was verified during development).
"""
import time
import pytest
from tests.conftest import SAMPLE_FEATURES

from app.services.blockchain_service import get_blockchain_service


def _blockchain_ready() -> bool:
    try:
        return get_blockchain_service().is_available()
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _blockchain_ready(),
    reason="No local Hardhat node + deployed contract detected at BLOCKCHAIN_RPC_URL",
)


@pytest.fixture(autouse=True)
def _unique_application_id_seq(mock_db):
    """
    The on-chain contract persists state across this whole pytest session
    (it's a real blockchain), while each test gets a FRESH in-memory
    MongoDB. Without this, every test's first application would be
    assigned "LN-000001" again and collide with an already-registered
    on-chain record from an earlier test. Seeding a unique, high starting
    sequence per test avoids that collision -- it's a test-isolation
    detail, not a product behavior.
    """
    unique_seq = int(time.time() * 1000) % 1_000_000
    mock_db.applications.insert_one({"_seq": unique_seq, "_seed_marker": True})
    yield


def _create_and_predict(client):
    resp = client.post("/api/applications", json={"input_features": SAMPLE_FEATURES})
    assert resp.status_code == 201
    return resp.json()


def test_register_application_on_blockchain(client):
    application = _create_and_predict(client)
    app_id = application["application_id"]

    response = client.post(f"/api/blockchain/register/{app_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_hash"].startswith("0x")
    assert data["block_number"] > 0
    assert data["contract_address"]
    assert data["chain_id"] == 31337


def test_duplicate_registration_is_rejected(client):
    application = _create_and_predict(client)
    app_id = application["application_id"]

    client.post(f"/api/blockchain/register/{app_id}")
    second_attempt = client.post(f"/api/blockchain/register/{app_id}")
    assert second_attempt.status_code == 409


def test_verify_matching_record_returns_verified_true(client):
    application = _create_and_predict(client)
    app_id = application["application_id"]
    client.post(f"/api/blockchain/register/{app_id}")

    response = client.get(f"/api/blockchain/verify/{app_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["current_database_hash"] == data["blockchain_hash"]


def test_verify_tampered_record_returns_verified_false(client):
    application = _create_and_predict(client)
    app_id = application["application_id"]
    client.post(f"/api/blockchain/register/{app_id}")

    # Tamper with the record directly via the update endpoint
    client.patch(f"/api/applications/{app_id}/status", json={"status": "UNDER_REVIEW"})
    # status is not part of canonical hash by design in this schema... use input feature change instead
    tampered_features = dict(SAMPLE_FEATURES)
    tampered_features["loan_amount"] = SAMPLE_FEATURES["loan_amount"] + 999999
    client.put(f"/api/applications/{app_id}", json={"input_features": tampered_features})

    response = client.get(f"/api/blockchain/verify/{app_id}")
    data = response.json()
    assert data["verified"] is False
    assert data["current_database_hash"] != data["blockchain_hash"]


def test_verify_unregistered_application_reports_not_registered(client):
    application = _create_and_predict(client)
    app_id = application["application_id"]

    response = client.get(f"/api/blockchain/verify/{app_id}")
    data = response.json()
    assert data["verified"] is False
    assert "not been registered" in data["message"]
