import os, json
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGO_DB_NAME", "personal_finance")
if not uri: raise SystemExit("Set MONGODB_URI")
client = MongoClient(uri); db = client[db_name]
def apply_validator(coll, path):
    with open(path, "r") as f: validator = json.load(f)
    try: db.command({"collMod": coll, "validator": validator})
    except Exception: db.create_collection(coll, validator=validator)
apply_validator("transactions", "mongo/validators/transactions.validator.json")
apply_validator("subscriptions", "mongo/validators/subscriptions.validator.json")
db.transactions.create_index([("tenantId",1),("accountId",1),("dedupeHash",1)], unique=True, name="uniq_tenant_account_dedupe")
db.transactions.create_index([("tenantId",1),("accountId",1),("postedAt",1)])
db.transactions.create_index([("tenantId",1),("categoryId",1),("postedAt",1)])
db.subscriptions.create_index([("tenantId",1),("merchantNormalized",1)], unique=True)
db.rollups_category_month.create_index([("tenantId",1),("month",1),("categoryId",1)], unique=True)
db.rules.create_index([("tenantId",1),("priority",1)])
db.accounts.create_index([("tenantId",1)])
db.budgets.create_index([("tenantId",1),("month",1)], unique=True)
print("Validators and indexes applied to", db_name)
