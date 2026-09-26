"""
Shared pytest fixtures.

MongoDB: tests use mongomock (an in-memory MongoDB-compatible engine) so
the full application/repository/service stack can be exercised without
requiring a running mongod instance in CI/sandbox environments. Application
code always talks to `db` through the same PyMongo API, so mongomock is a
faithful stand-in for these tests.

ML model: tests load the REAL trained pipeline from ml/models/ (no mocking)
-- if it isn't present, ML-dependent tests are skipped with a clear reason.

Blockchain: blockchain-dependent tests are skipped unless a local Hardhat
node + deployed contract are reachable at BLOCKCHAIN_RPC_URL (see
tests/test_blockchain.py for how to run them for real).
"""
import os
import sys

import mongomock
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import database
from app.main import app
from app.dependencies import get_database


@pytest.fixture()
def mock_db():
    client = mongomock.MongoClient()
    db = client["loan_default_mlbc_test"]
    yield db


@pytest.fixture()
def client(mock_db, monkeypatch):
    # Avoid the app's lifespan trying to reach a real (absent) MongoDB
    # instance during tests -- the mongomock db is injected via the
    # dependency override below instead.
    monkeypatch.setattr(database, "connect", lambda: None)
    monkeypatch.setattr(database, "ensure_indexes", lambda: None)
    monkeypatch.setattr(database, "close", lambda: None)

    app.dependency_overrides[get_database] = lambda: mock_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def ml_model_available():
    model_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models", "loan_default_model.joblib")
    )
    return os.path.exists(model_path)


SAMPLE_FEATURES = {
    "age": 34,
    "annual_income": 720000,
    "employment_years": 6,
    "employment_type": "Salaried",
    "credit_score": 710,
    "loan_amount": 500000,
    "loan_term_months": 60,
    "existing_debt": 120000,
    "debt_to_income_ratio": 0.35,
    "number_of_previous_loans": 1,
    "previous_default": 0,
    "dependents": 1,
    "savings_amount": 200000,
    "requested_loan_purpose": "Home",
}
