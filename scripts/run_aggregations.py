import os, subprocess
tenant = os.getenv("TENANT_ID", "demo-tenant")
mongo_uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGO_DB_NAME","personal_finance")
if not mongo_uri: raise SystemExit("Set MONGODB_URI")
def run_js(path):
    with open(path, "r") as f: js = f.read().replace("__TENANT_ID__", tenant)
    subprocess.run(["mongosh", f"{mongo_uri}/{db_name}", "--eval", js], check=True)
run_js("mongo/aggregations/subscriptions_pipeline.js")
run_js("mongo/aggregations/rollups_category_month.js")
print("Aggregation pipelines executed.")
