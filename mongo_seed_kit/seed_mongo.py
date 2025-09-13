#!/usr/bin/env python3
"""
Seed MongoDB Atlas with initial data for PersonalFinanceTracking.

Usage:
  export MONGODB_URI="your mongodb+srv://..."
  python seed_mongo.py --db finance_app --force
"""
import os, sys, argparse, datetime, secrets
from pymongo import MongoClient, ASCENDING, DESCENDING
import bcrypt

def get_client():
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        print("ERROR: Set MONGODB_URI env var", file=sys.stderr)
        sys.exit(1)
    return MongoClient(uri, tz_aware=True, appname="PFT-Seeder")

# JSON Schema validators
USER_SCHEMA = {
    "bsonType": "object",
    "required": ["email", "hashed_password", "status", "is_admin", "created_at", "updated_at"],
    "properties": {
        "email": {"bsonType": "string"},
        "hashed_password": {"bsonType": "string"},
        "status": {"enum": ["active", "paused", "removed"]},
        "is_admin": {"bsonType": "bool"},
        "created_at": {"bsonType": "date"},
        "updated_at": {"bsonType": "date"}
    }
}

AUDIT_SCHEMA = {
    "bsonType": "object",
    "required": ["action", "created_at"],
    "properties": {
        "action": {"bsonType": "string"},
        "created_at": {"bsonType": "date"}
    }
}

ITEM_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "item_id", "access_token_ref", "created_at"],
    "properties": {
        "item_id": {"bsonType": "string"},
        "access_token_ref": {"bsonType": "string"},
        "created_at": {"bsonType": "date"}
    }
}

TXN_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "item_id", "amount", "date", "name"],
    "properties": {
        "amount": {"bsonType": ["double", "int"]},
        "date": {"bsonType": "date"},
        "name": {"bsonType": "string"}
    }
}

SESSION_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "created_at", "expires_at"],
    "properties": {
        "created_at": {"bsonType": "date"},
        "expires_at": {"bsonType": "date"}
    }
}

def ensure_coll(db, name, schema, force=False):
    if name in db.list_collection_names():
        if force:
            db.command("collMod", name, validator={"$jsonSchema": schema}, validationLevel="moderate")
        return db[name]
    return db.create_collection(name, validator={"$jsonSchema": schema}, validationLevel="moderate")

def ensure_indexes(db):
    db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    db.audit_logs.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_time")
    db.plaid_items.create_index([("item_id", ASCENDING)], unique=True, name="uniq_item")
    db.transactions.create_index([("user_id", ASCENDING), ("date", DESCENDING)], name="user_date")
    db.sessions.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_expires")

def upsert_user(db, email, password, is_admin=False):
    now = datetime.datetime.utcnow()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    doc = {
        "email": email.lower(),
        "hashed_password": hashed,
        "is_admin": is_admin,
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    existing = db.users.find_one({"email": doc["email"]})
    if existing:
        db.users.update_one({"_id": existing["_id"]}, {"$set": doc})
        return existing["_id"]
    return db.users.insert_one(doc).inserted_id

def insert_sample(db, user_id):
    now = datetime.datetime.utcnow()
    item_id = f"item_{secrets.token_hex(6)}"
    ref = f"ref_{secrets.token_hex(12)}"
    db.plaid_items.insert_one({
        "user_id": user_id,
        "item_id": item_id,
        "access_token_ref": ref,
        "institution_name": "Sandbox Bank",
        "created_at": now
    })
    db.transactions.insert_many([
        {"user_id": user_id, "item_id": item_id, "amount": 12.34, "date": now, "name": "Coffee"},
        {"user_id": user_id, "item_id": item_id, "amount": 110.0, "date": now, "name": "Groceries"},
    ])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="finance_app")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    client = get_client()
    db = client[args.db]

    ensure_coll(db, "users", USER_SCHEMA, force=args.force)
    ensure_coll(db, "audit_logs", AUDIT_SCHEMA, force=args.force)
    ensure_coll(db, "plaid_items", ITEM_SCHEMA, force=args.force)
    ensure_coll(db, "transactions", TXN_SCHEMA, force=args.force)
    ensure_coll(db, "sessions", SESSION_SCHEMA, force=args.force)
    ensure_indexes(db)

    admin_id = upsert_user(db, "admin@example.com", "Admin#12345", True)
    user_id = upsert_user(db, "user@example.com", "User#12345", False)
    insert_sample(db, user_id)

    print("✅ Seed complete.")

if __name__ == "__main__":
    main()
