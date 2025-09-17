from typing import List, Dict, Any
import csv, io
from pymongo import UpdateOne
from .hashutil import txn_dedupe_hash
from .categorize import normalize_merchant, heuristic_category
def parse_csv_and_build_docs(file_bytes: bytes, tenant_id: str, account_id: str, currency: str = "USD") -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    out = []
    for row in reader:
        posted_at = row.get("Date") or row.get("Posted") or row.get("posted_at")
        amount = float(row.get("Amount") or row.get("amount") or 0.0)
        desc = row.get("Description") or row.get("Payee") or row.get("Memo") or ""
        merchant_norm = normalize_merchant(desc)
        dedupe = txn_dedupe_hash(account_id, posted_at, amount, merchant_norm, desc)
        cat_guess, conf = heuristic_category(merchant_norm, desc)
        doc = {
            "tenantId": tenant_id,
            "accountId": account_id,
            "postedAt": posted_at,
            "amount": amount,
            "currency": currency,
            "merchant": merchant_norm,
            "descriptionRaw": desc,
            "categoryId": cat_guess,
            "categoryConfidence": conf,
            "isPending": False,
            "dedupeHash": dedupe
        }
        out.append(doc)
    return out
def bulk_upsert_transactions(col, docs: List[Dict[str, Any]]):
    ops = []
    for d in docs:
        ops.append(UpdateOne(
            {"tenantId": d["tenantId"], "accountId": d["accountId"], "dedupeHash": d["dedupeHash"]},
            {"$setOnInsert": d},
            upsert=True
        ))
    if ops:
        res = col.bulk_write(ops, ordered=False)
        return {"upserts": res.upserted_count, "matched": res.matched_count, "modified": res.modified_count}
    return {"upserts": 0, "matched": 0, "modified": 0}
