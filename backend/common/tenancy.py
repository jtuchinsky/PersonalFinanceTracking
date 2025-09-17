from typing import Dict, Any
TENANT_CLAIM = "tenantId"
def tenant_filter(tenant_id: str, base: Dict[str, Any] | None = None) -> Dict[str, Any]:
    q = dict(base or {})
    q[TENANT_CLAIM] = tenant_id
    return q
def require_tenant_id(claims: Dict[str, Any]) -> str:
    tid = claims.get(TENANT_CLAIM)
    if not tid:
        raise ValueError("Missing tenantId in token/claims")
    return tid
