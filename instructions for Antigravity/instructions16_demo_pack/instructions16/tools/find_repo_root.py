#!/usr/bin/env python3
import sys
from pathlib import Path

def is_root(p: Path) -> bool:
    return (p / "aas" / "api.py").exists() and (p / "requirements.txt").exists()

start = Path(__file__).resolve()
for p in [start] + list(start.parents):
    if is_root(p):
        print(str(p))
        sys.exit(0)

cwd = Path.cwd().resolve()
for p in [cwd] + list(cwd.parents):
    if is_root(p):
        print(str(p))
        sys.exit(0)

print("ERROR: could not locate repo root (expected 'aas/api.py' and 'requirements.txt')", file=sys.stderr)
sys.exit(2)
