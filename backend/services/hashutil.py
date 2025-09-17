import hashlib
def txn_dedupe_hash(account_id: str, posted_at: str, amount: float, merchant: str | None, description_raw: str | None) -> str:
    key = f"{account_id}|{posted_at}|{amount:.2f}|{merchant or ''}|{description_raw or ''}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()
