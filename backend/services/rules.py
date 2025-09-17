from typing import Any, Dict, List
import re
class Rule:
    def __init__(self, rule_doc: Dict[str, Any]):
        self.rule = rule_doc
        self.priority = rule_doc.get("priority", 1000)
        self.enabled = rule_doc.get("enabled", True)
        self.conditions = rule_doc.get("conditions", [])
        self.actions = rule_doc.get("actions", [])
    def matches(self, txn: Dict[str, Any]) -> bool:
        for cond in self.conditions:
            field = cond.get("field"); op = cond.get("op"); val = cond.get("value")
            tv = (txn.get(field) or "")
            if op == "regex":
                if re.search(val, str(tv)) is None: return False
            elif op == "contains":
                if str(val).lower() not in str(tv).lower(): return False
            elif op == "gte":
                if float(tv) < float(val): return False
            elif op == "lte":
                if float(tv) > float(val): return False
            else:
                return False
        return True
    def apply(self, txn: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(txn)
        for act in self.actions:
            t = act.get("type")
            if t == "set_category": out["categoryId"] = act.get("category_id")
            elif t == "rename_merchant": out["merchant"] = act.get("to")
            elif t == "add_tag":
                tags = set(out.get("tags") or []); tags.add(act.get("tag")); out["tags"] = list(tags)
        return out
def pick_rule(rules: List[Dict[str, Any]], txn: Dict[str, Any]) -> Dict[str, Any] | None:
    compiled = [Rule(r) for r in rules if r.get("enabled", True)]
    compiled.sort(key=lambda r: r.priority)
    for r in compiled:
        if r.matches(txn): return r.rule
    return None
