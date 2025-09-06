#!/usr/bin/env python3
import re
import sys
from pathlib import Path

import yaml

p = Path("config/mcp/allowlist.yaml")
data = yaml.safe_load(p.read_text(encoding="utf-8"))

# Minimal schema
assert isinstance(data, dict) and "allow" in data, (
    "allowlist.yaml missing 'allow' key"
)
assert isinstance(data["allow"], list), "'allow' must be a list"

# Tool name hygiene: lowercase, dot-separated
bad = [
    t
    for t in data["allow"]
    if not re.fullmatch(r"[a-z0-9]+(\.[a-z0-9]+)+", str(t))
]
if bad:
    print(f"Invalid tool names: {bad}", file=sys.stderr)
    sys.exit(1)
print("OK: allowlist.yaml validated")
