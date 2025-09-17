from typing import Tuple
import re
COMMON_MERCHANTS = {
    r"(?i)trader\\s*joe": "groceries",
    r"(?i)whole\\s*foods": "groceries",
    r"(?i)costco": "groceries",
    r"(?i)netflix": "subscriptions",
    r"(?i)spotify": "subscriptions",
    r"(?i)uber\\s*eats": "dining",
    r"(?i)mcdonald": "dining",
    r"(?i)starbucks": "coffee"
}
def normalize_merchant(desc: str | None) -> str | None:
    if not desc: return None
    m = re.sub(r"[^a-zA-Z0-9\\s]", "", desc)
    m = re.sub(r"\\s+", " ", m).strip().upper()
    return m
def heuristic_category(merchant_norm: str | None, description_raw: str | None) -> Tuple[str | None, float]:
    cand = description_raw or ""
    for rx, cat in COMMON_MERCHANTS.items():
        if re.search(rx, cand): return (cat, 0.7)
    return (None, 0.0)
