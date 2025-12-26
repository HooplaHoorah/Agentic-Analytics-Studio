import hashlib
from pathlib import Path
from typing import Dict

def short_fp(v: str) -> str:
    return hashlib.sha256(v.encode("utf-8")).hexdigest()[:10]

def redact(k: str, v: str) -> str:
    if not v:
        return "MISSING"
    if "TOKEN" in k or "SECRET" in k:
        return f"SET len={len(v)} sha256[:10]={short_fp(v)}"
    return f"SET len={len(v)}"

def parse_env(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    out: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out
