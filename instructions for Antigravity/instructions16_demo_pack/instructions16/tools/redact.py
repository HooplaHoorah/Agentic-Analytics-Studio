import hashlib

def fp(v: str) -> str:
    return hashlib.sha256(v.encode("utf-8")).hexdigest()[:10]

def redact(k: str, v: str) -> str:
    if not v:
        return "MISSING"
    if any(s in k.upper() for s in ["TOKEN", "SECRET", "KEY", "PASSWORD"]):
        return f"SET len={len(v)} sha256[:10]={fp(v)}"
    return f"SET len={len(v)}"
