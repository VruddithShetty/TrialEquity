#!/usr/bin/env python3
"""Reset the default admin password in the local MongoDB database."""

import sys
from pathlib import Path

from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth import get_password_hash


MONGODB_URL = "mongodb://mongodb:27017"
DATABASE_NAME = "clinical_trials"
ADMIN_EMAIL = "user@example.com"
DEFAULT_PASSWORD = "password123"


def main() -> None:
    client = MongoClient(MONGODB_URL)
    users = client[DATABASE_NAME]["users"]

    result = users.update_one(
        {"email": ADMIN_EMAIL},
        {"$set": {"hashed_password": get_password_hash(DEFAULT_PASSWORD)}},
    )

    if result.matched_count == 0:
        raise SystemExit(f"No admin user found for {ADMIN_EMAIL}")

    user = users.find_one(
        {"email": ADMIN_EMAIL},
        {"email": 1, "username": 1, "role": 1, "_id": 0},
    )
    print(user)


if __name__ == "__main__":
    main()