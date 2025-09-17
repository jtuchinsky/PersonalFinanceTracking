import os
from fastapi import FastAPI, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.common.db import get_db
from backend.common.tenancy import require_tenant_id
from backend.services.import_csv import parse_csv_and_build_docs, bulk_upsert_transactions
from backend.services.rules import pick_rule

app = FastAPI(title="Money Autopilot MVP API")

def get_claims():
    return {"tenantId": "demo-tenant"}

class RuleDoc(BaseModel):
    name: str
    priority: int = 100
    enabled: bool = True
    conditions: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []

@app.post("/imports/csv")
async def import_csv(account_id: str, file: UploadFile = File(...), claims: Dict[str, Any] = Depends(get_claims)):
    db = get_db()
    tenant_id = require_tenant_id(claims)
    data = await file.read()
    docs = parse_csv_and_build_docs(data, tenant_id=tenant_id, account_id=account_id)
    stats = bulk_upsert_transactions(db.transactions, docs)
    return {"status": "ok", "stats": stats}

@app.post("/rules/test")
async def rules_test(sample_txn: Dict[str, Any], rules: List[RuleDoc]):
    r = pick_rule([r.model_dump() for r in rules], sample_txn)
    return {"matchedRule": r}

@app.get("/subscriptions")
async def list_subscriptions(claims: Dict[str, Any] = Depends(get_claims)):
    db = get_db()
    tenant_id = require_tenant_id(claims)
    cur = db.subscriptions.find({"tenantId": tenant_id}).limit(200)
    return [s for s in cur]

@app.get("/insights/{yyyy_mm}")
async def insights(yyyy_mm: str, claims: Dict[str, Any] = Depends(get_claims)):
    db = get_db()
    tenant_id = require_tenant_id(claims)
    out = {
        "month": yyyy_mm,
        "categoryDeltas": list(db.rollups_category_month.find({"tenantId": tenant_id, "month": yyyy_mm})),
    }
    return out

@app.post("/exports/full")
async def export_full(claims: Dict[str, Any] = Depends(get_claims)):
    import json, zipfile, datetime
    db = get_db()
    tenant_id = require_tenant_id(claims)
    export_dir = os.getenv("EXPORT_DIR", "exports")
    os.makedirs(export_dir, exist_ok=True)
    datasets = {
        "accounts": list(db.accounts.find({"tenantId": tenant_id})),
        "transactions": list(db.transactions.find({"tenantId": tenant_id})),
        "rules": list(db.rules.find({"tenantId": tenant_id})),
        "subscriptions": list(db.subscriptions.find({"tenantId": tenant_id})),
        "budgets": list(db.budgets.find({"tenantId": tenant_id})),
        "insights": list(db.insights.find({"tenantId": tenant_id})),
        "auditLog": list(db.audit_log.find({"tenantId": tenant_id})),
    }
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    zip_path = os.path.join(export_dir, f"export_{tenant_id}_{ts}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        manifest = []
        for name, rows in datasets.items():
            fn = f"{name}.json"
            z.writestr(fn, json.dumps(rows, default=str, ensure_ascii=False, indent=2))
            manifest.append({"name": name, "count": len(rows)})
        z.writestr("manifest.json", json.dumps({"tenantId": tenant_id, "datasets": manifest}, indent=2))
    return {"status": "ok", "file": zip_path}
