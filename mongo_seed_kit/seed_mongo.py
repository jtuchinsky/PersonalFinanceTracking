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
    "required": ["id", "email", "name", "password", "account_status", "created_at", "updated_at"],
    "properties": {
        "id": {"bsonType": "string"},
        "email": {"bsonType": "string"},
        "name": {"bsonType": "string"},
        "password": {"bsonType": "string"},
        "account_status": {"enum": ["active", "locked", "deleted"]},
        "last_login": {"bsonType": ["date", "null"]},
        "created_at": {"bsonType": "date"},
        "updated_at": {"bsonType": "date"}
    }
}

ADMIN_SCHEMA = {
    "bsonType": "object",
    "required": ["id", "email", "name", "password", "role", "account_status", "created_at", "updated_at"],
    "properties": {
        "id": {"bsonType": "string"},
        "email": {"bsonType": "string"},
        "name": {"bsonType": "string"},
        "password": {"bsonType": "string"},
        "role": {"enum": ["admin", "super_admin"]},
        "permissions": {"bsonType": "array"},
        "account_status": {"enum": ["active", "locked", "deleted"]},
        "last_login": {"bsonType": ["date", "null"]},
        "created_by": {"bsonType": ["string", "null"]},
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
    # User indexes
    db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_user_email")
    db.users.create_index([("id", ASCENDING)], unique=True, name="uniq_user_id")

    # Admin indexes
    db.admins.create_index([("email", ASCENDING)], unique=True, name="uniq_admin_email")
    db.admins.create_index([("id", ASCENDING)], unique=True, name="uniq_admin_id")

    # Activity indexes
    db.user_activities.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)], name="user_activity_time")
    db.admin_activities.create_index([("admin_id", ASCENDING), ("timestamp", DESCENDING)], name="admin_activity_time")

    # Account and transaction indexes
    db.accounts.create_index([("user_id", ASCENDING)], name="user_accounts")
    db.transactions.create_index([("user_id", ASCENDING), ("date", DESCENDING)], name="user_transactions")
    db.transactions.create_index([("account_id", ASCENDING)], name="account_transactions")

    # Category and credentials indexes
    db.categories.create_index([("name", ASCENDING)], name="category_name")
    db.account_credentials.create_index([("account_id", ASCENDING)], unique=True, name="uniq_account_cred")

import uuid

def upsert_user(db, email, name, password):
    now = datetime.datetime.now(datetime.timezone.utc)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())

    doc = {
        "id": user_id,
        "email": email.lower(),
        "name": name,
        "password": hashed,
        "account_status": "active",
        "last_login": None,
        "created_at": now,
        "updated_at": now
    }
    existing = db.users.find_one({"email": doc["email"]})
    if existing:
        db.users.update_one({"id": existing["id"]}, {"$set": doc})
        return existing["id"]
    db.users.insert_one(doc)
    return user_id

def upsert_admin(db, email, name, password, role="admin"):
    now = datetime.datetime.now(datetime.timezone.utc)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    admin_id = str(uuid.uuid4())

    doc = {
        "id": admin_id,
        "email": email.lower(),
        "name": name,
        "password": hashed,
        "role": role,
        "permissions": ["user_management", "system_stats", "view_activities"],
        "account_status": "active",
        "last_login": None,
        "created_by": None,
        "created_at": now,
        "updated_at": now
    }
    existing = db.admins.find_one({"email": doc["email"]})
    if existing:
        db.admins.update_one({"id": existing["id"]}, {"$set": doc})
        return existing["id"]
    db.admins.insert_one(doc)
    return admin_id

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

def seed_categories(db):
    """Seed default expense categories"""
    categories = [
        {"id": str(uuid.uuid4()), "name": "Food & Dining", "color": "#FF6B6B", "icon": "utensils"},
        {"id": str(uuid.uuid4()), "name": "Transportation", "color": "#4ECDC4", "icon": "car"},
        {"id": str(uuid.uuid4()), "name": "Shopping", "color": "#45B7D1", "icon": "shopping-bag"},
        {"id": str(uuid.uuid4()), "name": "Entertainment", "color": "#96CEB4", "icon": "music"},
        {"id": str(uuid.uuid4()), "name": "Bills & Utilities", "color": "#FFEAA7", "icon": "zap"},
        {"id": str(uuid.uuid4()), "name": "Healthcare", "color": "#DDA0DD", "icon": "heart"},
        {"id": str(uuid.uuid4()), "name": "Travel", "color": "#98D8C8", "icon": "plane"},
        {"id": str(uuid.uuid4()), "name": "Education", "color": "#F7DC6F", "icon": "book"},
        {"id": str(uuid.uuid4()), "name": "Investments", "color": "#BB8FCE", "icon": "trending-up"},
        {"id": str(uuid.uuid4()), "name": "Other", "color": "#AEB6BF", "icon": "more-horizontal"}
    ]

    for category in categories:
        existing = db.categories.find_one({"name": category["name"]})
        if not existing:
            db.categories.insert_one(category)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="finance_tracker")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    client = get_client()
    db = client[args.db]

    # Create collections with new schema
    ensure_coll(db, "users", USER_SCHEMA, force=args.force)
    ensure_coll(db, "admins", ADMIN_SCHEMA, force=args.force)

    # Activity collections
    user_activity_schema = {"bsonType": "object", "required": ["id", "user_id", "action", "timestamp"]}
    admin_activity_schema = {"bsonType": "object", "required": ["id", "admin_id", "action", "timestamp"]}
    ensure_coll(db, "user_activities", user_activity_schema, force=args.force)
    ensure_coll(db, "admin_activities", admin_activity_schema, force=args.force)

    # Financial collections
    account_schema = {"bsonType": "object", "required": ["id", "user_id", "name", "account_type"]}
    transaction_schema = {"bsonType": "object", "required": ["id", "user_id", "account_id", "amount"]}
    category_schema = {"bsonType": "object", "required": ["id", "name", "color", "icon"]}
    credentials_schema = {"bsonType": "object", "required": ["id", "account_id"]}

    ensure_coll(db, "accounts", account_schema, force=args.force)
    ensure_coll(db, "transactions", transaction_schema, force=args.force)
    ensure_coll(db, "categories", category_schema, force=args.force)
    ensure_coll(db, "account_credentials", credentials_schema, force=args.force)

    ensure_indexes(db)

    # Create sample admin and user
    admin_id = upsert_admin(db, "admin@example.com", "System Administrator", "Admin#12345", "super_admin")
    user_id = upsert_user(db, "user@example.com", "John Doe", "User#12345")

    # Seed categories
    seed_categories(db)

    print(f"✅ Seed complete!")
    print(f"   Admin created: admin@example.com / Admin#12345")
    print(f"   User created: user@example.com / User#12345")
    print(f"   Database: {args.db}")

if __name__ == "__main__":
    main()
