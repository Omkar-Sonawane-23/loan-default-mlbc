"""
seed_mongodb.py

Loads ml/data/processed/seed_applications.json into MongoDB's `applications`
collection, giving the demo a realistic mix of LOW/MEDIUM/HIGH risk
applications, different statuses, and some pre-flagged for blockchain
registration.

Usage (from backend/ with a virtualenv active and MongoDB running):

    python scripts/seed_mongodb.py

Optional: also register the applications flagged `should_register_demo`
on the blockchain (requires a running local Hardhat node + deployed
contract):

    python scripts/seed_mongodb.py --register-on-chain
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import database
from app.services.blockchain_business_service import BlockchainBusinessService

SEED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "data", "processed", "seed_applications.json"
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--register-on-chain", action="store_true",
                         help="Also register flagged applications on the blockchain")
    args = parser.parse_args()

    with open(SEED_PATH) as f:
        applications = json.load(f)

    db = database.connect()
    database.ensure_indexes()

    collection = db.applications
    inserted = 0
    for i, app in enumerate(applications, start=1):
        app = dict(app)
        should_register = app.pop("should_register_demo", False)
        app["_seq"] = i
        existing = collection.find_one({"application_id": app["application_id"]})
        if existing:
            continue
        collection.insert_one(app)
        inserted += 1

        if args.register_on_chain and should_register:
            try:
                service = BlockchainBusinessService(db)
                service.register(app["application_id"])
                print(f"  registered {app['application_id']} on-chain")
            except Exception as e:
                print(f"  could not register {app['application_id']}: {e}")

    print(f"Seeded {inserted} new applications into MongoDB ({len(applications) - inserted} already existed).")


if __name__ == "__main__":
    main()
